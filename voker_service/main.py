from typing import Any, Dict, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel
from wildcard_core.events.types import OAuthCompletionData, WebhookOAuthCompletion, WebhookRequest, WildcardEvent
from wildcard_core.models.Action import Action
from wildcard_core.tool_registry.tools.rest_api.types.auth_types import AuthType, OAuth2AuthConfig
from wildcard_core.tool_search.utils.api_service import APIService
from wildcard_openai import ToolClient
import sys
import os
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from wildcard_openai import Prompt
from voker_service.auth.routes import router as auth_router
from voker_service.wildcard_node import init_tool_node, run_tool_node

app = FastAPI()
base_url = "https://wildcard-voker.onrender.com"
frontend_url = "https://wildcard-voker.vercel.app"

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://wildcard-voker.vercel.app",
        "http://localhost:5173",  # For local development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers with their prefixes
app.include_router(auth_router, prefix="/auth")

# Initialize the OAuth credentials store
app.state.oauth_credentials = {}

class Message(BaseModel):
    role: str
    content: str

class RunRequest(BaseModel):
    user_id: str
    messages: List[Message]
    tool_name: str

@app.get('/health')
async def health():
    return {"status": "healthy"}


def patch_gmail_scopes(scopes: List[str]) -> List[str]:
    # GMAIL Metadata scopes conflict with other scopes in production (gmail side issue)
    return scopes + ["https://www.googleapis.com/auth/gmail.addons.current.message.metadata", "https://www.googleapis.com/auth/gmail.metadata"]

@app.post('/run_with_tool')
def run_with_tool(request: RunRequest):
    
    print(f"Request: {request.model_dump()}")
    voker_system_prompt = "Perform the action specified by the user."
    
    async def run_with_tool_async():
        api_service = APIService.GMAIL
        webhook_url = f"{base_url}/auth_webhook/{request.user_id}"
        
        user_credentials = get_credentials_for_user(request.user_id, api_service)        
        auth_config = OAuth2AuthConfig(
            type= AuthType.OAUTH2,
            token = user_credentials["access_token"],
            token_type = user_credentials["token_type"],
            refresh_token = user_credentials["refresh_token"],
            expires_at=user_credentials["expires_at"],
            scopes = patch_gmail_scopes(user_credentials["scope"]),    
        )
        tool_client, openai_client = await init_tool_node(request.tool_name, auth_config, webhook_url)
        messages = [
            Prompt.fixed_tool_prompt(tool_client.get_tools(format="openai")),
            {"role": "system", "content": f"{voker_system_prompt}"},
        ]
        messages.extend(request.messages)
        
        print(f"SENDING MESSAGES: {messages}")
        tool_response = await run_tool_node(tool_client, openai_client, messages)
        return tool_response
    
    tool_response = asyncio.run(run_with_tool_async())
    return {"status": "success", "data": tool_response}

@app.post("/auth_webhook/{user_id}")
def agent_webhook(request: WebhookRequest[Any], user_id: str):
    """
    Handle webhook callbacks from the auth_service.
    """
    print("RECEIVED WEBHOOK: ", request.model_dump())
    if request.event == WildcardEvent.END_OAUTH_FLOW or request.event == WildcardEvent.END_REFRESH_TOKEN:
        save_credentials_for_user(user_id, request.data["api_service"], request.data)
        
        return JSONResponse({"status": "success", "message": "Credentials saved successfully", "redirect_url": f"{base_url}/success"})
    else:
        return JSONResponse({"status": "error", "message": "Unsupported event", "error": f"Unsupported event: {request.event}"})

def save_credentials_for_user(user_id: str, api_service: str, credentials: Dict[str, Any]):
    if user_id not in app.state.oauth_credentials:
        app.state.oauth_credentials[user_id] = {}
    app.state.oauth_credentials[user_id][api_service] = credentials
    
def get_credentials_for_user(user_id: str, api_service: str) -> Dict[str, Any]:
    if user_id not in app.state.oauth_credentials:
        raise KeyError(f"No credentials found for user {user_id}")
    if api_service not in app.state.oauth_credentials[user_id]:
        raise KeyError(f"No credentials found for service {api_service} for user {user_id}")
    return app.state.oauth_credentials[user_id][api_service]




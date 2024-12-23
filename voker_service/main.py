from typing import Any, Dict, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from wildcard_core.events.types import OAuthCompletionData, WebhookOAuthCompletion, WebhookRequest, WildcardEvent
from wildcard_core.models.Action import Action
from wildcard_core.tool_registry.tools.rest_api.types.auth_types import AuthType, OAuth2AuthConfig
from wildcard_openai import ToolClient
from auth import auth_router
from chain import chain_router
from .wildcard_node import init_tool_node, run_tool_node

app = FastAPI()
base_url = "https://wildcard-voker.onrender.com"
frontend_url = "https://wildcard-voker.vercel.app"

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Update allow origins to be base_url for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with their prefixes
app.include_router(auth_router, prefix="/auth")
app.include_router(chain_router, prefix="/chain")

# Initialize the OAuth credentials store
app.state.oauth_credentials = {}

class RunRequest(BaseModel):
    user_id: str
    messages: List[str]
    tool: Action


@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/run_with_tool")
async def run_with_tool(request: RunRequest):
    api_service = Action.get_api_service(request.tool)
    webhook_url = f"{base_url}/auth_webhook/{request.user_id}"
    tool_client, openai_client = await init_tool_node(api_service, get_credentials_for_user(request.user_id, api_service), webhook_url)
    return await run_tool_node(tool_client, openai_client, request.messages)

@app.post("/auth_webhook/{user_id}")
async def agent_webhook(request: WebhookRequest[Any], user_id: str):
    """
    Handle webhook callbacks from the auth_service.
    """
    if request.event == WildcardEvent.END_OAUTH_FLOW or request.event == WildcardEvent.END_REFRESH_TOKEN:
        save_credentials_for_user(user_id, request.data["api_service"], request.data)
        
        return RedirectResponse(url=f"{base_url}/success", status_code=303)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported event: {request.event}")

def save_credentials_for_user(user_id: str, api_service: str, credentials: Dict[str, Any]):
    if user_id not in app.state.oauth_credentials:
        app.state.oauth_credentials[user_id] = {}
    app.state.oauth_credentials[user_id][api_service] = credentials
    
def get_credentials_for_user(user_id: str, api_service: str) -> OAuth2AuthConfig:
    return app.state.oauth_credentials[user_id][api_service]




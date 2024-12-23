import os
from wildcard_core.events.types import WebhookOAuthCompletion, OAuthCompletionData, WildcardEvent
from wildcard_core.tool_search.utils.api_service import APIService
from wildcard_core.tool_registry.tools.rest_api.types import OAuth2Flows, AuthorizationCodeFlow, ImplicitFlow, PasswordFlow, ClientCredentialsFlow
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, Union
from requests_oauthlib import OAuth2Session
from .utils import join_url_parts
from fastapi import APIRouter

from .utils import construct_oauth2_authorization_url
from .auth_config import settings

import uuid

import json
import requests

base_url = "https://wildcard-voker.onrender.com"

router = APIRouter()

@router.get("/health")
async def health():
    return JSONResponse({"message": "AgentAuth service is healthy."})

@router.post("/refresh_token/{api_service}")
async def refresh_token(request: Request, api_service: str):
    """
    Refreshes the token for a given API service using the stored refresh token.
    Expects JSON payload with:
    - webhook_url: URL to send the refreshed token to
    """
    if api_service not in [s.value for s in APIService]:
        raise HTTPException(status_code=400, detail="Unsupported API service.")
        
    data = await request.json()
    webhook_url = data.get("webhook_url")
    
    if not webhook_url:
        raise HTTPException(status_code=400, detail="webhook_url is required.")
    
    # Get stored token
    stored_token = get_token(api_service)
    if not stored_token or not stored_token.get('refresh_token'):
        raise HTTPException(status_code=404, detail="No refresh token found for this service.")
    
    # Create OAuth client
    oauth_client = OAuth2Session(
        client_id=settings.oauth_config[api_service]['client_id'],
        client_secret=settings.oauth_config[api_service]['client_secret'],
        access_token_url=settings.oauth_config[api_service]['token_url'],
        refresh_token=stored_token['refresh_token']
    )
    
    try:
        # Refresh the token
        new_token = oauth_client.refresh_token(
            token_url=settings.oauth_config[api_service]['token_url'],
            refresh_token=stored_token['refresh_token'],
            client_id=settings.oauth_config[api_service]['client_id'],
            client_secret=settings.oauth_config[api_service]['client_secret']
        )
        
        # Store the new token
        store_token(api_service, new_token)
        
        # Send the new token to the webhook URL
        payload = WebhookOAuthCompletion(
            event=WildcardEvent.END_REFRESH_TOKEN,
            data=OAuthCompletionData(
                api_service=api_service,
                token_type=new_token.get("token_type", "Bearer"),
                access_token=new_token.get("access_token"),
                expires_at=int(new_token.get("expires_at")) if new_token.get("expires_at") else None,
                refresh_token=new_token.get("refresh_token", stored_token['refresh_token']),  # Use old refresh token if new one not provided
                scope=parse_scope(new_token)
            )
        )
        
        response = requests.post(webhook_url, json=payload.model_dump())
        response.raise_for_status()
        
        return JSONResponse({"message": "Token refreshed successfully."})
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to refresh token: {str(e)}")


# Initialize Authlib OAuth
@router.post("/oauth_flow/{api_service}")
async def start_oauth_flow(request: Request, api_service: str):
    """
    Starts the OAuth flow based on the provided payload.
    Expects JSON payload with:
    - flow (OAuth2Flows as dict): The highest priority OAuth flow to use from OpenAPI Security Schemes
    - webhook_url (str)
    - required_scopes (list)
    """
    
    data = await request.json()
    
    print(f"DATA: {data}")
    api_service = data.get("api_service")
    webhook_url = data.get("webhook_url")
    required_scopes = data.get("required_scopes")
    flow = data.get("flow")
    
    print(f"FLOW: {flow}")
    flow = OAuth2Flows(**flow)
    
    # Register OAuth service
    
    def find_target_flow_from_oauth2flows(flow: OAuth2Flows) -> Union[AuthorizationCodeFlow, ImplicitFlow, PasswordFlow, ClientCredentialsFlow]:
        if flow.authorizationCode:
            return flow.authorizationCode
        else:
            raise HTTPException(status_code=400, detail="Only authorization code flow is supported at this time.")
    
    target_flow = find_target_flow_from_oauth2flows(flow)
    if settings.oauth_config.get(api_service, None) is None:
        raise HTTPException(status_code=400, detail=f"OAuth configuration not found for the service {api_service}.")

    if not api_service or not required_scopes or not flow:
        raise HTTPException(status_code=400, detail="api_service, required_scopes, and flow are required.")

    if api_service not in [s.value for s in APIService]:
        raise HTTPException(status_code=400, detail="Unsupported API service.")
    
    callback_url = construct_callback_url(api_service)
    
    # Construct Authorization URL
    authorization_url, state = construct_oauth2_authorization_url(api_service, target_flow, callback_url, required_scopes)    
    print(f"AUTHORIZATION URL: {authorization_url}")
    
    # Generate state and store it along with webhook_url
    store_state(state, api_service)
    store_target_flow(state, target_flow)
    store_callback_url(state, callback_url)
    store_webhook_url(state, webhook_url)
    
    print("router.STATE:", router.state)

    return JSONResponse({"authorization_url": authorization_url})

@router.get("/callback/{api_service}")
async def auth_service_callback(request: Request, api_service: str):
    """
    Handles the OAuth 2.0 callback from the provider, exchanging the authorization code for tokens,
    and sends the tokens to the client's webhook URL.
    """
    if api_service not in [s.value for s in APIService]:
        raise HTTPException(status_code=400, detail="Unsupported API service.")

    # Verify state parameter to prevent CSRF
    state = request.query_params.get('state')
    if not verify_state(state, api_service):
        raise HTTPException(status_code=400, detail="Invalid state parameter.")

    callback_url = get_callback_url(state)
    target_flow = get_target_flow(state)
    
    if not target_flow or not callback_url:
        raise HTTPException(status_code=400, detail="Target flow or callback URL not found for the service.")
    
    oauth_client = OAuth2Session(
        client_id=settings.oauth_config[api_service]['client_id'],
        redirect_uri=callback_url,
        state=state
    )
    
    print("REQUEST QUERY PARAMS: ", request.query_params)
    
    # TODO: Handle other flows, assume authorization code for now
    token = oauth_client.fetch_token(
        token_url=target_flow.tokenUrl,
        client_id=settings.oauth_config[api_service]['client_id'],
        client_secret=settings.oauth_config[api_service]['client_secret'],
        code=request.query_params.get('code')
    )

    print("TOKEN: ", token)
    # Optionally, retrieve user information if needed
    # user = await oauth_client.parse_id_token(request, token)

    # Store tokens securely (e.g., in a database)
    store_token(api_service, token)

    # Retrieve client's webhook URL from stored state or another method
    # For this example, we'll assume the redirect_url was provided and stored during initiation
    # You might need to enhance the state_store to keep track of redirect URLs per api_service
    # Here, we'll assume the webhook_url is stored alongside the state
    webhook_url = get_webhook_url(state)  # Implement this function

    print(f"WEBHOOK URL: {webhook_url}")
    if not webhook_url:
        raise HTTPException(status_code=400, detail="Webhook URL not found for the service.")

    # Send the token to the client's webhook URL
    payload: WebhookOAuthCompletion = WebhookOAuthCompletion(
        event=WildcardEvent.END_OAUTH_FLOW,
        data=OAuthCompletionData(
            api_service=api_service,
            token_type=token.get("token_type", "Bearer"),
            access_token=token.get("access_token"),
            expires_at=int(token.get("expires_at")) if token.get("expires_at") else None,
            refresh_token=token.get("refresh_token", None),
            scope=parse_scope(token)
        )
    )

    response = requests.post(webhook_url, json=payload.model_dump())
    response.raise_for_status()
    return response

# TODO: This is unsafe without a Wildcard API key
# @router.get("/auth/{api_service}/token")
# async def get_api_token(api_service: str):
#     """
#     Retrieves the stored access token for a given API service.
#     """
#     token = get_token(api_service)
#     if not token:
#         raise HTTPException(status_code=404, detail="Token not found.")
#     return JSONResponse(content=token)

# Utility functions to manage state and token storage
# TODO: Manage state and token storage in a database securely

def store_state(state: str, api_service: str):
    """
    Stores the state parameter associated with the API service.
    """
    if not hasattr(router.state, 'state_store'):
        router.state.state_store = {}
    router.state.state_store[state] = {"api_service": api_service}  # Initialize webhook_url as None

def get_webhook_url(state: str) -> Optional[str]:
    """
    Retrieves the webhook URL associated with the given state and API service.
    """
    if not hasattr(router.state, 'webhook_url_store'):
        return None
    state_entry = router.state.webhook_url_store.get(state)
    if state_entry:
        return state_entry.get("webhook_url", None)
    return None

def store_webhook_url(state: str, webhook_url: str):
    """
    Stores the webhook URL for a given state.
    """
    if not hasattr(router.state, 'webhook_url_store'):
        router.state.webhook_url_store = {}
    if not state in router.state.webhook_url_store:
        router.state.webhook_url_store[state] = {}
    router.state.webhook_url_store[state]['webhook_url'] = webhook_url

def verify_state(state: str, api_service: str) -> bool:
    """
    Verifies the state parameter.
    """
    if not hasattr(router.state, 'state_store'):
        return False
    state_entry = router.state.state_store.pop(state, None)
    if state_entry and state_entry["api_service"] == api_service:
        return True
    return False

def store_token(api_service: str, token: Dict[str, Any]):
    """
    Stores the OAuth tokens securely.
    """
    if not hasattr(router.state, 'token_store'):
        router.state.token_store = {}
    router.state.token_store[api_service] = token

    # Optionally, persist tokens to a database
    os.makedirs("tokens", exist_ok=True)
    with open(f"tokens/{api_service}.json", "w") as f:
        json.dump(token, f)

def get_token(api_service: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves the stored access token for a given API service.
    """
    return router.state.token_store.get(api_service, None)

def store_target_flow(state: str, target_flow: Union[AuthorizationCodeFlow, ImplicitFlow, PasswordFlow, ClientCredentialsFlow]):
    """
    Stores the target flow for a given state.
    """
    if not hasattr(router.state, 'target_flow_store'):
        router.state.target_flow_store = {}
    router.state.target_flow_store[state] = target_flow
    
def store_callback_url(state: str, callback_url: str):
    """
    Stores the callback URL for a given state.
    """
    if not hasattr(router.state, 'callback_url_store'):
        router.state.callback_url_store = {}
    router.state.callback_url_store[state] = callback_url
    
def get_callback_url(state: str) -> Optional[str]:
    """
    Retrieves the callback URL for a given state.
    """
    return router.state.callback_url_store.get(state, None)

def get_target_flow(state: str) -> Optional[Union[AuthorizationCodeFlow, ImplicitFlow, PasswordFlow, ClientCredentialsFlow]]:
    """
    Retrieves the target flow for a given state.
    """
    return router.state.target_flow_store.get(state, None)

def construct_callback_url(api_service: str) -> str:
    """
    Constructs the callback URL for a given API service.
    """
    relative_callback_url = router.url_path_for("auth_service_callback", api_service=api_service)
    out_url = join_url_parts(base_url, relative_callback_url)
    print(f"OUT URL: {out_url}")
    return out_url

def parse_scope(token: dict) -> Union[list[str], None]:
    
    scope_list = []
    def handle_value(value: Union[list[str], str]) -> list[str]:
        if isinstance(value, list):
            for v in value:
                handle_value(v)
        elif isinstance(value, str):
            if "," in value:
                scope_list.extend([s.strip() for s in value.split(",")])
            else:
                scope_list.extend(value.split())
    
    value = token.get("scope", token.get("scopes", None))
    if value is None:
        print("WARNING - SCOPE IS EMPTY")
        return []
    handle_value(value)
    return scope_list
from wildcard_core.tool_registry.tools.rest_api.types.auth_types import AuthType, OAuth2AuthConfig
from datetime import datetime, timezone
from typing import List
def patch_gmail_scopes(scopes: List[str]) -> List[str]:
    # GMAIL Metadata scopes conflict with other scopes in production (gmail issue)
    return scopes + ["https://www.googleapis.com/auth/gmail.addons.current.message.metadata", "https://www.googleapis.com/auth/gmail.metadata"]

data = {} # Fill in from https://wildcard-auth-service.vercel.app

gmail_auth_config = OAuth2AuthConfig(
        type= AuthType.OAUTH2,
        token = data["access_token"],
        token_type = data["token_type"],
        refresh_token = "",
        expires_at=data["expires_at"],
        scopes = patch_gmail_scopes(data["scope"])
    )
from wildcard_core.tool_registry.tools.rest_api.types.auth_types import AuthType, OAuth2AuthConfig
from datetime import datetime, timezone
from typing import List
import json

def patch_gmail_scopes(scopes: List[str]) -> List[str]:
    # GMAIL Metadata scopes conflict with other scopes in production (gmail issue)
    return scopes + ["https://www.googleapis.com/auth/gmail.addons.current.message.metadata", "https://www.googleapis.com/auth/gmail.metadata"]

OUTPUT = """<PASTE AUTH OUTPUT HERE>""" # Fill in with response from https://wildcard-voker.vercel.app
DATA = json.loads(OUTPUT)["data"]

class AuthConfig:
    def __init__(self, data: dict = DATA):
        self.data = data

    def get_gmail_auth_config(self):
        return OAuth2AuthConfig(
            type= AuthType.OAUTH2,
            token = self.data["access_token"],
            token_type = self.data["token_type"],
            refresh_token = "",
            expires_at=self.data["expires_at"],
            scopes = patch_gmail_scopes(self.data["scope"])
        )
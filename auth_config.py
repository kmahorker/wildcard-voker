from wildcard_core.tool_registry.tools.rest_api.types.auth_types import AuthType, OAuth2AuthConfig
from datetime import datetime, timezone
from typing import List
import json

def patch_gmail_scopes(scopes: List[str]) -> List[str]:
    # GMAIL Metadata scopes conflict with other scopes in production (gmail issue)
    return scopes + ["https://www.googleapis.com/auth/gmail.addons.current.message.metadata", "https://www.googleapis.com/auth/gmail.metadata"]

OUTPUT = """{"message":"Token received successfully.","data":{"api_service":"gmail","token_type":"Bearer","access_token":"ya29.a0ARW5m76hyRB25rV-GQy62NedeTAvGFMhOPkYRmyNSD6kUbqhLDfvzRyWobBRLzd2XcC45_fDTNttJARBvFR2KQ_D0bulPqMVSfy-2Xu2isze6_10bfPQk_fPn94cuL35-NbQ7AHwUVwL38P_ODVMHNJpkbR-1xqClBCQiHcUSYk5QBSJyGSmofi8qd-q6g1f3JuUaCgYKAeoSARISFQHGX2Mi3wO7EKrXiE6pJk0n0xMQ0A0203","scope":["https://www.googleapis.com/auth/gmail.modify","https://www.googleapis.com/auth/gmail.addons.current.message.readonly","https://www.googleapis.com/auth/gmail.readonly","https://mail.google.com/","https://www.googleapis.com/auth/gmail.settings.sharing","https://www.googleapis.com/auth/gmail.labels","https://www.googleapis.com/auth/gmail.insert","https://www.googleapis.com/auth/gmail.addons.current.action.compose","https://www.googleapis.com/auth/gmail.compose","https://www.googleapis.com/auth/gmail.send","https://www.googleapis.com/auth/gmail.settings.basic","https://www.googleapis.com/auth/gmail.addons.current.message.action"],"expires_at":1735271627,"refresh_token":null}}""" # Fill in with response from https://wildcard-voker.vercel.app
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
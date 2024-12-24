from wildcard_core.auth.oauth_helper import OAuthCredentialsRequiredException
from wildcard_core.tool_registry.tools.rest_api.types.auth_types import AuthType, OAuth2AuthConfig
from wildcard_core.tool_search.utils.api_service import APIService
from wildcard_openai import ToolClient, Action, Prompt
from openai import OpenAI
import os
from typing import List, Dict, Any
import asyncio
import json

async def init_tool_node(tool: Action, auth_config: OAuth2AuthConfig, webhook_url: str):
    tool_client = ToolClient(api_key="voker-api-key", index_name="newid1", webhook_url="")
    await tool_client.add(tool)
    
    # Register Authentication Credentials
    tool_client.register_api_auth(APIService.GMAIL, auth_config)
    
    # Could use an instance of the Voker class here
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    return tool_client, openai_client

async def run_tool_node(tool_client: ToolClient, openai_client: OpenAI, messages: List[Dict[str, Any]]):

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tool_client.get_tools(format="openai"),
        tool_choice="auto",
        temperature=0,
    )
    
    tool_response = await tool_client.run_tools(response)
    return response + [{"role": "tool", "content": json.dumps(tool_response)}]
    

def main():
    # In production, auth configs would be fetched from the database
    auth_config = OAuth2AuthConfig(
        type= AuthType.OAUTH2,
        token = "",
        token_type = "",
        refresh_token = "",
        expires_at=0,
        scopes = {},    
    )
    tool_client, openai_client = asyncio.run(init_tool_node(Action.Gmail.SEND_EMAIL, auth_config))
    
    # TODO: Implement the wildcard tool prompt in core package
    wildcard_tool_prompt = "You are a wildcard tool that can perform actions on behalf of the user."
    voker_system_prompt = "Perform the action specified by the user."
    voker_content = "Send an email to logan.mdchainsolutions@gmail.com that says 'Hello!'"
        
    messages = [
        Prompt.fixed_tool_prompt(tool_client.get_tools(format="openai")),
        {"role": "system", "content": f"{voker_system_prompt}"},
        {"role": "user", "content": voker_content}
    ]

    response = asyncio.run(run_tool_node(tool_client, openai_client, messages))
    print(response)
    
if __name__ == "__main__":
    main()
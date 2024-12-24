from wildcard_core.auth.oauth_helper import OAuthCredentialsRequiredException
from wildcard_core.tool_registry.tools.rest_api.types.auth_types import AuthType, OAuth2AuthConfig
from wildcard_core.tool_search.utils.api_service import APIService
from wildcard_openai import ToolClient, Action, Prompt
from openai import OpenAI
import os
from typing import List, Dict, Any, Optional
import asyncio
import json
from openai.types.chat.chat_completion import ChatCompletion
async def init_tool_node(tool: Action, auth_config: OAuth2AuthConfig, webhook_url: str):
    tool_client = ToolClient(api_key="voker-api-key", index_name="newid1", webhook_url="")
    await tool_client.add(tool)
    
    # Register Authentication Credentials
    tool_client.register_api_auth(APIService.GMAIL, auth_config)
    
    # Could use an instance of the Voker class here
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    return tool_client, openai_client

async def run_tool_node(tool_client: ToolClient, openai_client: OpenAI, messages: List[Dict[str, Any]]):
    def run_openai_completion(messages: List[Dict[str, Any]]):
        return openai_client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tool_client.get_tools(format="openai"),
            tool_choice="auto",
            temperature=0,
        )
        
    def process_response(response: ChatCompletion, messages: List[Dict[str, Any]], tool_response: Optional[Any] = None):
        # Gives the updated full list of messages for the next iteration
        assistant_message = response.choices[0].message.model_dump()
        
        messages += [
            assistant_message
        ]
        
        if tool_response is not None:
            tool_call_id = response.choices[0].message.tool_calls[0].id
            messages += [
                {"role": "tool", "tool_call_id": tool_call_id, "content": json.dumps(tool_response)}
            ]
        
        return messages
    
    # Run the first LLM completion
    response = run_openai_completion(messages)
    tool_response = await tool_client.run_tools(response)
    messages = process_response(response, messages, tool_response)
    
    # Send the Tool Response back to the LLM to get a final response
    final_response = run_openai_completion(messages)

    return process_response(final_response, messages)

def main():
    # In production, auth configs would be fetched from the database
    auth_config = OAuth2AuthConfig(
        type= AuthType.OAUTH2,
        token = "ya29.a0ARW5m74jmMIiVYJpbwKkWAT4Mq_rHBp1QuiTa_yPFCXbGszUl1aAxLcM5O76tqZiI-GMcY5WTpJlzO2k19MW0xVhr2ZrtLBgHbIaLp5jQYO-l4yGJqBJLf6svekP8TKv9A9jridOFmEkdIj31PBx4Nk2BIqe5deKkW74DM8maCgYKAUISARISFQHGX2MidStqBSSfgOnlgI-juZXumQ0175",
        token_type = "Bearer",
        refresh_token = "1//04XPug3IVTSEWCgYIARAAGAQSNwF-L9Ir0JqVcr2HippZG1bnliZfsPTHtYsk7INTcrLcMON400lphFUbQ609Z0Ui3blMLoJGcKE",
        expires_at=1735027735,
        scopes = set("https://www.googleapis.com/auth/gmail.addons.current.message.action https://www.googleapis.com/auth/gmail.insert https://www.googleapis.com/auth/gmail.labels https://www.googleapis.com/auth/gmail.settings.basic https://www.googleapis.com/auth/gmail.settings.sharing https://www.googleapis.com/auth/gmail.send https://www.googleapis.com/auth/gmail.compose https://www.googleapis.com/auth/gmail.modify https://www.googleapis.com/auth/gmail.addons.current.action.compose https://www.googleapis.com/auth/gmail.addons.current.message.readonly https://www.googleapis.com/auth/gmail.readonly https://mail.google.com/".split(" "))  
    )
    tool_client, openai_client = asyncio.run(init_tool_node(Action.Gmail.MESSAGES_SEND, auth_config, ""))
    
    # TODO: Implement the wildcard tool prompt in core package
    wildcard_tool_prompt = "You are a wildcard tool that can perform actions on behalf of the user."
    voker_system_prompt = "Perform the action specified by the user."
    voker_content = "Send an email to logan.midchainsolutions@gmail.com that says 'Hello!'"
        
    messages = [
        Prompt.fixed_tool_prompt(tool_client.get_tools(format="openai")),
        {"role": "system", "content": f"{voker_system_prompt}"},
        {"role": "user", "content": voker_content}
    ]

    response = asyncio.run(run_tool_node(tool_client, openai_client, messages))
    print(response)
    
if __name__ == "__main__":
    main()
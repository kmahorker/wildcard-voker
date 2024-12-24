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
            tool_choice="required",
            parallel_tool_calls=False,
            temperature=0,
        )
        
    def process_response(response: ChatCompletion, messages: List[Dict[str, Any]], tool_response: Optional[Any] = None):
        # Gives the updated full list of messages for the next iteration
        assistant_message = response.choices[0].message.model_dump(exclude_none=True, exclude_unset=True)
        if "content" not in assistant_message:
            assistant_message["content"] = ""
        
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
    print("Running Voker Stage")
    response = run_openai_completion(messages)
    tool_response = None
    if response.choices[0].message.tool_calls is not None:
        tool_response = await tool_client.run_tools(response)
        print("======tool response========", tool_response)
    
    messages = process_response(response, messages, tool_response)
        
    return messages

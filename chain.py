
# Call /run_with_tool for each stage
from wildcard_core.models import Action
import requests
import asyncio
import json
from voker_service.wildcard_node import init_tool_node, run_tool_node

from wildcard_core.tool_registry.tools.rest_api.types.auth_types import AuthType, OAuth2AuthConfig

from wildcard_openai import Prompt

base_url = "https://wildcard-voker.onrender.com"
user_id = "2b31e59c-37d6-4f4d-8271-d76d7269253b"
voker_1 = {
    "user_id": user_id,
    "message": "Search for the messages in my inbox that are about the order number 832493284 and are from the vendors that have sent me proposals.",
    "tool_name": Action.Gmail.MESSAGES_LIST,
}
# voker2s = []
voker_2 = {
    "user_id": user_id,
    "message": "For each of the emails get and analyze the content. Call this function to get the message multiple time. Call it for every message that there is. Understand the proposal and the vendor's price.",
    "tool_name": Action.Gmail.MESSAGES_GET,
}

voker_3 = {
    "user_id": user_id,
    "message": """Create a draft email with an attachment called proposal.txt of the following info:
    proposal.txt attachment:
        Hello,
        I am interested in your proposal. Please provide me with more information about your company and your proposal.
        Thank you,
        Logan
    """,
    "tool_name": Action.Gmail.DRAFTS_CREATE,
}

voker_list = [voker_1, voker_2, voker_3]


# Run Voker Chain

async def run_single_voker(voker, previous_messages):
    auth_config = OAuth2AuthConfig(
        type= AuthType.OAUTH2,
        token = "ya29.a0ARW5m75QQodDFkZ6fHtDUH-YQ7jp2GPkoZJ8lJCpK1oKaXAMeyMxwNl7wlx2nbfc5OlsN33XZKuU0wb9m_BGt8xAgmrouYPzNyTcrp1ArgS3lfSGShJtfaRlRX3dzx_erlB3Dd0nksNxTAiohsoXVcI7GyvkxArUtw72agMcaCgYKAeMSARISFQHGX2MiiLB5yo-6vBuBhupfT3B7Eg0175",
        token_type = "Bearer",
        refresh_token = "1//04XPug3IVTSEWCgYIARAAGAQSNwF-L9Ir0JqVcr2HippZG1bnliZfsPTHtYsk7INTcrLcMON400lphFUbQ609Z0Ui3blMLoJGcKE",
        expires_at=1735084178,
        scopes = set("https://www.googleapis.com/auth/gmail.addons.current.action.compose https://www.googleapis.com/auth/gmail.compose https://www.googleapis.com/auth/gmail.send https://www.googleapis.com/auth/gmail.settings.basic https://www.googleapis.com/auth/gmail.settings.sharing https://www.googleapis.com/auth/gmail.insert https://mail.google.com/ https://www.googleapis.com/auth/gmail.addons.current.message.readonly https://www.googleapis.com/auth/gmail.labels https://www.googleapis.com/auth/gmail.addons.current.message.action https://www.googleapis.com/auth/gmail.modify https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.metadata https://www.googleapis.com/auth/gmail.addons.current.message.metadata https://mail.google.com/ https://www.googleapis.com/auth/gmail.addons.current.message.action https://www.googleapis.com/auth/gmail.modify https://www.googleapis.com/auth/gmail.addons.current.message.readonly https://www.googleapis.com/auth/gmail.metadata https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.send  https://mail.google.com/  https://www.googleapis.com/auth/gmail.compose  https://www.googleapis.com/auth/gmail.addons.current.action.compose  https://www.googleapis.com/auth/gmail.modify".split(" "))
    )
    tool_client, openai_client = await init_tool_node(voker["tool_name"], auth_config, "")
    
    # TODO: Implement the wildcard tool prompt in core package
    wildcard_tool_prompt = "You are a wildcard tool that can perform actions on behalf of the user."
    voker_system_prompt = """
    The users name is Logan. His email is logan.midchainsolutions@gmail.com.
    Perform the action specified by the user.
    """
    voker_content = "Send an email to logan.midchainsolutions@gmail.com that says 'Hello!'"
        
    # if len(previous_messages) > 2:
    #     # Prune the system messages
    #     previous_messages = previous_messages[2:]
    
    messages = [
        Prompt.fixed_tool_prompt(tool_client.get_tools(format="openai")),
        {"role": "system", "content": f"{voker_system_prompt}"}
    ] + previous_messages

    response = await run_tool_node(tool_client, openai_client, messages)
    
    return response

async def run_voker_chain():
    messages = []
    for voker in voker_list:
        messages.append({"role": "user", "content": voker["message"]})
        messages = await run_single_voker(voker, messages)        
        
        
        # response = requests.post(f"{base_url}/run_with_tool", json={
        #     "user_id": user_id, 
        #     "messages": messages, 
        #     "tool_name": voker["tool_name"]
        # })
        
        
        # print(f"Status code: {response.status_code}")
        # print(f"Response text: {response.text}")
        # if response.ok:
        #     response_json = response.json()
        #     if "error" not in response_json:
        #         messages = response_json["data"]
        #     else:
        #         print(f"Error: {response_json['error']}")
        #         break
            
        # print(f"Messages: {messages}")

if __name__ == "__main__":
    asyncio.run(run_voker_chain())
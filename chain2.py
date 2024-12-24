
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
    "message": """Search for the messages in:inbox that are about the order number 832493284. 
    I should have received a few emails.
    You should only return the message ids.
    """,
    "tool_name": Action.Gmail.MESSAGES_LIST,
}
voker_2 = {
    "user_id": user_id,
    "message": """You have been given a set of message ids. 
    Get one of the emails and understand the proposal and the vendor's price.""",
    "tool_name": Action.Gmail.MESSAGES_GET,
}

voker_3 = {
    "user_id": user_id,
    "message": """You have been given a set of message ids. 
    Get one of the emails and understand the proposal and the vendor's price.""",
    "tool_name": Action.Gmail.MESSAGES_ATTACHMENTS_GET,
}

voker_list = [voker_1, voker_2, voker_3]


# Run Voker Chain

async def run_single_voker(voker, previous_messages):
    auth_config = OAuth2AuthConfig(
        type= AuthType.OAUTH2,
        token = "ya29.a0ARW5m76EroQt07e6gh8VTIJLJapo8VNnqNZ0yrjdmkshX2_hXlC4fwJGNe9ffKegadeY6NsADoXpv7W3SHz5T9ReQuTigsbemmHv0uYhOXpWX5NID7QX37j4kfsUqEdrsG40Gt9mWbHPLB_seUCAzIJduceqM0h5L1IrCAMuaCgYKAa8SARISFQHGX2Mid_-5rMsjcwYrWuYZDPYcMQ0175",
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

    print("\n\n=====WRITING CHAIN RESULT TO FILE =====\n\n")

    # Gmail api returns the attachment content in base64url format 
    # where the '+' and '/' characters of standard Base64 are respectively replaced by '-' and '_'.
    # This function converts the base64url format to standard Base64.
    def patch_gmail_base64(content):
        return content.replace('-', '+').replace('_', '/')

    with open('chain_result.txt', 'w') as f:
        if isinstance(messages[-1], dict) and 'content' in messages[-1]:
            tool_response = json.loads(messages[-1]['content'])
            if 'data' in tool_response:
                f.write(patch_gmail_base64(tool_response['data']))
        else:
            f.write(str(messages[-1]))


if __name__ == "__main__":
    asyncio.run(run_voker_chain())
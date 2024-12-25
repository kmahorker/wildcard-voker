
# Call /run_with_tool for each stage
from wildcard_core.models import Action
import requests
import asyncio
import json
from voker_service.wildcard_node import init_tool_node, run_tool_node

from wildcard_core.tool_registry.tools.rest_api.types.auth_types import AuthType, OAuth2AuthConfig

from wildcard_openai import Prompt
import auth_config

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
    tool_client, openai_client = await init_tool_node(voker["tool_name"], auth_config.gmail_auth_config, "")
    
    voker_system_prompt = """
    The users name is Logan. His email is logan.midchainsolutions@gmail.com.
    Perform the action specified by the user.
    """
    voker_content = "Send an email to logan.midchainsolutions@gmail.com that says 'Hello!'"
    
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
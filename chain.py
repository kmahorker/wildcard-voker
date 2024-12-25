
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
    "tool_name": Action.Gmail.THREADS_LIST,
}
voker_2 = {
    "user_id": user_id,
    "message": """You have been given a set of message ids. 
    Get one of the emails and understand the proposal and the vendor's price.""",
    "tool_name": Action.Gmail.THREADS_GET,
}

voker_3 = {
    "user_id": user_id,
    "message": """You have been given a set of thread ids. 
    Get one of the emails and understand the proposal and the vendor's price.""",
    "tool_name": Action.Gmail.MESSAGES_GET,
}

voker_4 = {
    "user_id": user_id,
    "message": """Analyze the email that you have received.
    Create a draft that is a reply to the corresponding email. Include the threadId when you are creating the draft. 
    In the draft, negotiate the price, delivery time, and unit size of the proposal from the vendor.
    """,
    "tool_name": Action.Gmail.DRAFTS_CREATE,
}


voker_list = [voker_1, voker_2, voker_3, voker_4]


# Run Voker Chain
async def run_single_voker(voker, previous_messages):
    tool_client, openai_client = await init_tool_node(voker["tool_name"], auth_config.gmail_auth_config, "")
    
    # TODO: Implement the wildcard tool prompt in core package
    voker_system_prompt = """
    The users name is Logan. His email is logan.midchainsolutions@gmail.com.
    Perform the action specified by the user.
    """
    
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

if __name__ == "__main__":
    asyncio.run(run_voker_chain())
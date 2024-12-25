
# Call /run_with_tool for each stage
from wildcard_core.models import Action
import requests
import asyncio
import argparse
import json
from voker_service.wildcard_node import init_tool_node, run_tool_node

from wildcard_core.tool_registry.tools.rest_api.types.auth_types import AuthType, OAuth2AuthConfig

from wildcard_openai import Prompt

base_url = "https://wildcard-voker.onrender.com"

voker_1 = {
    "message": """
    The users name is Logan. His email is logan.midchainsolutions@gmail.com.
    Search for the messages in inbox that are about the order number 832493284.
    You should only return the message ids.
    """,
    "tool_name": Action.Gmail.THREADS_LIST,
}
voker_2 = {
    "message": """You have been given a set of message ids. 
    Get one of the emails and understand the proposal and the vendor's price.
    """,
    "tool_name": Action.Gmail.THREADS_GET,
}

voker_3 = {
    "message": """You have been given a set of thread ids. 
    Get one of the emails and understand the proposal and the vendor's price.""",
    "tool_name": Action.Gmail.MESSAGES_GET,
}

voker_4 = {
    "message": """Analyze the email that you have received.
    Create a draft that is a reply to the corresponding email. Include the threadId when you are creating the draft. 
    In the draft, negotiate the price, delivery time, and unit size of the proposal from the vendor.
    """,
    "tool_name": Action.Gmail.DRAFTS_CREATE,
}


voker_list = [voker_1, voker_2, voker_3, voker_4]


# Run Voker Chain
async def run_voker_chain(user_id: str):
    voker_system_prompt = """
    Perform the action specified by the user. 
    Do not ask or expect for any further information than what the user has already provided.
    """
    messages = []
    
    for voker in voker_list:
        messages.append({"role": "user", "content": voker["message"]})
                
        response = requests.post(f"{base_url}/run_with_tool", json={
            "user_id": user_id, 
            "messages": messages, 
            "tool_name": voker["tool_name"],
            "voker_system_prompt": voker_system_prompt
        })

        if response.ok:
            response_json = response.json()
            if "error" not in response_json:
                messages = response_json["data"]
            else:
                print(f"Error: {response_json['error']}")
                break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Chain script.')
    parser.add_argument('--user_id', required=True, help='User ID')
    args = parser.parse_args()

    asyncio.run(run_voker_chain(args.user_id))
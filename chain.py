
# Call /run_with_tool for each stage
from wildcard_core.models import Action
import requests
import asyncio
import json
# base_url = "https://wildcard-voker.onrender.com"
base_url = "https://wildcard-voker.onrender.com"
user_id = "ff863eb8-c921-4f6d-9637-80c2f40ef713"
voker_1 = {
    "user_id": user_id,
    "message": "Get the RFP proposal emails related to the order number 832493284",
    "tool_name": Action.Gmail.MESSAGES_LIST,
}

voker_2 = {
    "user_id": user_id,
    "message": "Get each of the emails and summarize the content",
    "tool_name": Action.Gmail.MESSAGES_GET,
}

voker_3 = {
    "user_id": user_id,
    "message": "Create a draft email in response to the email that analyzes the RFP proposal and negotiates a price reduction",
    "tool_name": Action.Gmail.DRAFTS_CREATE,
}

voker_list = [voker_1, voker_2, voker_3]


# Run Voker Chain

async def run_voker_chain():
    messages = []
    for voker in voker_list:
        messages.append({"role": "user", "content": voker["message"]})
        response = requests.post(f"{base_url}/run_with_tool", json={
            "user_id": user_id, 
            "messages": messages, 
            "tool_name": voker["tool_name"]
        })
        
        print(f"Status code: {response.status_code}")
        print(f"Response text: {response.text}")
        if response.ok:
            response_json = response.json()
            if "error" not in response_json:
                messages.extend(response_json["data"])
            else:
                print(f"Error: {response_json['error']}")
                break

if __name__ == "__main__":
    asyncio.run(run_voker_chain())
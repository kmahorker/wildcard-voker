
# Call /run_with_tool for each stage
from wildcard_core.models import Action
import requests
import asyncio

# base_url = "https://wildcard-voker.onrender.com"
base_url = "https://wildcard-voker.onrender.com"
user_id = "cdee7474-b45f-43c5-bf93-a4ef916db370"
voker_1 = {
    "user_id": user_id,
    "message": "Get the RFP proposal emails related to the order number 832493284",
    "tool_name": Action.Gmail.MESSAGES_LIST,
}

voker_2 = {
    "user_id": user_id,
    "message": "Create a draft email in response to the email that analyzes the RFP proposal and negotiates a price reduction",
    "tool_name": Action.Gmail.DRAFTS_CREATE,
}

# voker_3 = {
#     "user_id": user_id,
#     "message": "",
#     "tool": Action.Gmail.SEND_EMAIL,
# }

voker_list = [voker_1, voker_2]


# Run Voker Chain

async def run_voker_chain():
    messages = []
    for voker in voker_list:
        messages.append(voker["message"])
        response = requests.post(f"{base_url}/run_with_tool", json={
            "user_id": user_id, 
            "messages": messages, 
            "tool_name": voker["tool_name"]
        })
        
        print(f"Status code: {response.status_code}")
        print(f"Response text: {response.text}")
        if response.ok:
            print(f"Response JSON: {response.json()}")

if __name__ == "__main__":
    asyncio.run(run_voker_chain())
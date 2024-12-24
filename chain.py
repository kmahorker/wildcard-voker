
# Call /run_with_tool for each stage
from wildcard_core.models import Action
import requests
import asyncio

# base_url = "https://wildcard-voker.onrender.com"
base_url = "https://wildcard-voker.onrender.com"
user_id = "56243666-a186-4d17-bc98-54323e0923e3"
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
        messages.append({"role": "user", "content": voker["message"]})
        response = requests.post(f"{base_url}/run_with_tool", json={
            "user_id": user_id, 
            "messages": messages, 
            "tool_name": voker["tool_name"]
        })
        
        print(f"Status code: {response.status_code}")
        print(f"Response text: {response.text}")
        if response.ok:
            print(f"Response JSON: {response.json()}")
            
            messages.append({"role": "assistant", "content": response.json()["content"]})

if __name__ == "__main__":
    asyncio.run(run_voker_chain())
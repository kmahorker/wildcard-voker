
# Call /run_with_tool for each stage
from wildcard_core.models import Action
import requests
import asyncio
import json
# base_url = "https://wildcard-voker.onrender.com"
base_url = "https://wildcard-voker.onrender.com"
user_id = "d6dae831-b518-42d4-b5fd-79eec0ad4cf0"
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
            response_json = response.json()
            print(f"Response JSON: {response_json}")
            if "error" in response_json["data"]:
                print(f"Error: {response_json['data']['error']}")
                break
            
            if "messages" in response_json["data"]:
                messages.append({"role": "assistant", "content": json.dumps(response_json["data"]["messages"][-1])})
                
            print(f"Messages: {messages}")

if __name__ == "__main__":
    asyncio.run(run_voker_chain())
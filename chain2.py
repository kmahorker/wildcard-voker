
from wildcard_core.models import Action
import asyncio
import json
from voker_service.wildcard_node import run_single_voker
import auth_config

voker_1 = {
    "message": """Search for the messages in:inbox that are about the order number 832493284. 
    I should have received a few emails.
    You should only return the message ids.
    """,
    "tool_name": Action.Gmail.MESSAGES_LIST,
}
voker_2 = {
    "message": """You have been given a set of message ids. 
    Get one of the emails and understand the proposal and the vendor's price.""",
    "tool_name": Action.Gmail.MESSAGES_GET,
}

voker_3 = {
    "message": """You have been given a set of message ids. 
    Get one of the emails and understand the proposal and the vendor's price.""",
    "tool_name": Action.Gmail.MESSAGES_ATTACHMENTS_GET,
}

voker_list = [voker_1, voker_2, voker_3]

async def run_voker_chain():
    voker_system_prompt = """
    The users name is Logan. His email is logan.midchainsolutions@gmail.com.
    Perform the action specified by the user.
    """
    
    auth = auth_config.AuthConfig()
    
    messages = []
    for voker in voker_list:
        messages.append({"role": "user", "content": voker["message"]})
        messages = await run_single_voker(voker, voker_system_prompt, auth.get_gmail_auth_config(), messages)        

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
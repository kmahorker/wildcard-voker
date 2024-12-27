
# Call /run_with_tool for each stage
from wildcard_core.models import Action
import asyncio
from voker_service.wildcard_node import run_single_voker
import auth_config

voker_inputs = {
    "email_address": "logan.midchainsolutions@gmail.com",
    "name": "Logan",
    "order_number": "832493284"
}   

voker_1 = {
    "message": """Search for the messages in:inbox that are about the order number @order_number. 
    I should have received a few emails.
    You should only return the message ids.
    """,
    "tool_name": Action.Gmail.THREADS_LIST,
}
voker_2 = {
    "message": """You have been given a set of message ids. 
    Get one of the emails and understand the proposal and the vendor's price.""",
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
async def run_voker_chain():
    voker_system_prompt = """
    The users name is @name. His email is @email_address.
    Perform the action specified by the user.
    """
    
    auth = auth_config.AuthConfig()
    messages = []
    for voker in voker_list:
        messages.append({"role": "user", "content": voker["message"]})
        messages = await run_single_voker(voker, voker_system_prompt, auth.get_gmail_auth_config(), messages, voker_inputs)

if __name__ == "__main__":
    asyncio.run(run_voker_chain())
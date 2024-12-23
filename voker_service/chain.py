
# Call /run_with_tool for each stage

user_id = "123"
voker_1 = {
    "user_id": user_id,
    "message": "Send an email to logan.mdchainsolutions@gmail.com that says 'Hello!'",
    "tool": Action.Gmail.SEND_EMAIL,
}

voker_2 = {
    "user_id": user_id,
    "message": "Send an email to logan.mdchainsolutions@gmail.com that says 'Hello!'",
    "tool": Action.Gmail.SEND_EMAIL,
}

voker_3 = {
    "user_id": user_id,
    "message": "Send an email to logan.mdchainsolutions@gmail.com that says 'Hello!'",
    "tool": Action.Gmail.SEND_EMAIL,
}

voker_list = [voker_1, voker_2, voker_3]


# Run Voker Chain
last_response = None
for voker in voker_list:
    if last_response:
        voker["message"] =f"\Previous response: {last_response} \n{voker['message']}"
    response = requests.post(f"{base_url}/run_with_tool", json=voker)
    last_response = response.json()
    
    
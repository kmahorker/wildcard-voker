# Wildcard <> Voker Implementation

This repository contains the rails for Voker to use the Wildcard API.

## Setup

### Dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install -r voker_service/requirements.txt
pip install -i https://test.pypi.org/simple/ wildcard-openai==0.0.22 --extra-index-url https://pypi.org/simple/
export PYTHONPATH=$PYTHONPATH:..
```

### OpenAI Key

We've provisioned and sent via email an OpenAI key for you to use. Please add it as an environment variable.
```bash
export OPENAI_API_KEY=<your_openai_key>
```

### Auth

We've hosted an Auth server frontend at https://wildcard-voker.vercel.app. Please use this to authenticate with Gmail.

1. Go to https://wildcard-voker.vercel.app
2. Authenticate with the demo Google account
    - email: logan.midchain@gmail.com
    - password: DemoPassword1!!
3. Copy the value(the whole object) of "data" from the response page
4. Paste the value into the auth_config.py file.
5. Replace the null value in the data object with 'None'

### Running tool chains
Specify the tool actions and the prompts for each voker in the chain.

[chain.py](./chain.py) contains a tool chain reading a thread from the inbox and creating a draft reply to the first email in the thread.
- Voker 1 searches for the threads in the inbox that are about the order number 832493284.
- Voker 2 picks one of the threads and gets the emails in the thread.
- Voker 3 gets and understands one of the proposals and the vendor's price.
- Voker 4 creates a draft that is a reply to the corresponding email, negotiating the price, delivery time, and unit size of the proposal from the vendor.
```bash
python3 chain.py
```
Once the chain is run, you can check the Gmail UI to see the draft it created.


[chain2.py](./chain2.py) contains a tool chain reading messages about a specific order number from the inbox and reading an attachment from one of the emails.
- Voker 1 searches for the messages in the inbox that are about the order number 832493284.
- Voker 2 picks one of the messages and gets the email.
- Voker 3 reads the attachment from the email.
```bash
python3 chain2.py
```
The chain output in the file [chain_result.txt](./chain_result.txt) contains the encoded PDF attachment. Decoding the base64 string will give you the PDF.

You can edit these chains to test different workflows.

## Supported Actions
The Action class imported in both [chain.py](./chain.py) and [chain2.py](./chain2.py) contains gmail tool actions that you can pick from. You can read more about the supported actions [here](https://docs.wild-card.ai/docs/gmail-actions#/).
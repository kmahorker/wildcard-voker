# Wildcard <> Voker Implementation

This repository contains the rails for Voker to use the Wildcard API.

## Setup

```bash
virtualenv .venv
source .venv/bin/activate

pip install -r voker_service/requirements.txt
pip install -i https://test.pypi.org/simple/ wildcard-openai==0.0.22 --extra-index-url https://pypi.org/simple/
export PYTHONPATH=$PYTHONPATH:..
```

## Quickstart

### Auth

We've hosted an Auth server frontend at https://wildcard-voker.vercel.app. Please use this to authenticate with Gmail.

1. Go to https://wildcard-voker.vercel.app
2. Authenticate with your Google account
3. Copy the `user_id` from the next page

### Running tool chains
Specify the tool actions and the prompts for each voker in the chain.

chain.py contains a tool chain reading a thread from the inbox and creating a draft reply to the first email in the thread.
```bash
python3 chain.py --user_id <user_id>
```

chain2.py contains a tool chain reading messages about a specific order number from the inbox and reading an attachment from one of the emails.
```bash
python3 chain2.py --user_id <user_id>
```

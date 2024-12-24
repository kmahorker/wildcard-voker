# Wildcard <> Voker Implementation

This repository contains the rails for Voker to use the Wildcard API.

## Setup

```bash
virtualenv .venv
source .venv/bin/activate

pip install -r voker_service/requirements.txt
pip install -i https://test.pypi.org/simple/ wildcard-openai==0.0.21 --extra-index-url https://pypi.org/simple/
pip install -i https://test.pypi.org/simple/ wildcard-core==0.0.60 --extra-index-url https://pypi.org/simple/
export PYTHONPATH=$PYTHONPATH:..
```

Start the server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Run tool chains

Specify the tool actions and the prompts for each voker in the chain.

chain.py contains a tool chain reading a thread from the inbox and creating a draft reply to the first email in the thread.
```bash
python3 chain.py
```

chain2.py contains a tool chain reading messages about a specific order number from the inbox and reading an attachment from one of the emails.
```bash
python3 chain2.py
```

# Wildcard <> Voker Implementation

This repositoty contains the rails for Voker to use the Wildcard API.

## How to run

```bash

cd voker_service

pip install -r requirements.txt && pip install -i https://test.pypi.org/simple/ wildcard-openai==0.0.9 --extra-index-url https://pypi.org/simple/ && export PYTHONPATH=$PYTHONPATH:..
```


## How to test

```bash
python3 voker_service/wildcard_node.py
```

```bash
python3 chain.py
```



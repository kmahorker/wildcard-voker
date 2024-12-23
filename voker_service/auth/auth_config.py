from pydantic_settings import BaseSettings
from typing import Dict, Any, List
import yaml
import os

class Settings(BaseSettings):
    oauth_config: Dict[str, Dict[str, Any]]
    redirect_uri_base: str
    database_url: str = "sqlite:///./oauth.db"
    wildcard_api_key: str
    allow_origins: List[str]

    class Config:
        env_file = ".env"

def load_yaml_config(path: str = os.path.join(os.path.dirname(__file__), 'auth_config.yml')) -> Settings:
    with open(path, 'r') as file:
        yaml_config = yaml.safe_load(file)
        return Settings(**yaml_config)

settings = load_yaml_config()
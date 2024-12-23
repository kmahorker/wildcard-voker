import uuid
from urllib.parse import urlencode
from requests_oauthlib import OAuth2Session
from .auth_config import settings
from urllib.parse import urljoin


def construct_oauth2_authorization_url(api_service, target_flow, redirect_uri, required_scopes):
    # Extract OAuth configuration for the specified API service
    oauth_conf = settings.oauth_config.get(api_service)
    if not oauth_conf:
        raise ValueError(f"No OAuth configuration found for service '{api_service}'.")

    client_id = oauth_conf.get('client_id')
    client_secret = oauth_conf.get('client_secret')
    if not client_id or not client_secret:
        raise ValueError("Both 'client_id' and 'client_secret' must be provided in the OAuth configuration.")

    authorize_url = target_flow.authorizationUrl
    scopes = required_scopes

    # Generate a unique state string if not provided
    state = uuid.uuid4().hex
    
    # Create an OAuth2 session
    oauth = OAuth2Session(
        client_id=client_id,
        redirect_uri=redirect_uri,
        scope=' '.join(scopes),
    )

    # Generate the authorization URL
    authorization_url, generated_state = oauth.authorization_url(authorize_url, state=state)

    return authorization_url, generated_state

def join_url_parts(base_url: str, *parts: str) -> str:
    """
    Joins a base URL with multiple path parts using urljoin.        
    Example:
        >>> join_url_parts("https://api.example.com", "/api", "/v1/", "/users")
        'https://api.example.com/api/v1/users'
    """
    # Ensure base_url ends with slash for proper urljoin behavior
    url = base_url if base_url.endswith('/') else f"{base_url}/"
    
    # Join all parts, ensuring each part is properly stripped
    for part in parts:
        if part:
            # Remove leading/trailing slashes for consistency
            cleaned_part = part.strip('/')
            if cleaned_part:
                url = urljoin(url, cleaned_part + '/')
    
    return url.rstrip('/')  # Remove trailing slash from final URL
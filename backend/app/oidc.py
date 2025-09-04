from authlib.integrations.starlette_client import OAuth
from fastapi import Request
import os
import logging

logger = logging.getLogger(__name__)

# Debug: Print environment variables
client_id = os.getenv("OIDC_CLIENT_ID")
client_secret = os.getenv("OIDC_CLIENT_SECRET") 
issuer = os.getenv("OIDC_ISSUER")

logger.info(f"OIDC_CLIENT_ID: {client_id}")
logger.info(f"OIDC_CLIENT_SECRET: {'***' if client_secret else None}")
logger.info(f"OIDC_ISSUER: {issuer}")

# Validate required environment variables
if not all([client_id, client_secret, issuer]):
    raise ValueError("Missing required OIDC environment variables: OIDC_CLIENT_ID, OIDC_CLIENT_SECRET, OIDC_ISSUER")

if not issuer.startswith(('http://', 'https://')):
    raise ValueError(f"OIDC_ISSUER must start with http:// or https://. Got: {issuer}")

oauth = OAuth()
oauth.register(
    name="oidc",
    client_id=client_id,
    client_secret=client_secret,
    server_metadata_url=f"{issuer}/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

async def get_current_user(request: Request):
    user = request.session.get("user")
    if user:
        return user
    return None
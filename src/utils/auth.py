"""JWT validation helper for Amazon Cognito tokens."""

import json
import os
from urllib.request import urlopen

from aws_lambda_powertools import Logger
from jose import JWTError, jwk, jwt

logger = Logger(child=True)

# Cache JWKS in memory to avoid fetching on every request
_JWKS_CACHE: dict = {}


class AuthError(Exception):
    """Raised when JWT validation fails."""

    def __init__(self, message: str, code: str = "UNAUTHORIZED") -> None:
        super().__init__(message)
        self.code = code


def _get_jwks(user_pool_id: str, region: str) -> dict:
    """Fetch and cache the Cognito JWKS for the given user pool."""
    from urllib.error import URLError

    cache_key = f"{region}/{user_pool_id}"
    if cache_key in _JWKS_CACHE:
        return _JWKS_CACHE[cache_key]

    url = f"https://cognito-idp.{region}.amazonaws.com/" f"{user_pool_id}/.well-known/jwks.json"
    try:
        with urlopen(url, timeout=5) as resp:  # noqa: S310
            jwks = json.loads(resp.read())
    except URLError as exc:
        raise AuthError(f"Failed to fetch JWKS: {exc}", "SERVER_ERROR") from exc

    _JWKS_CACHE[cache_key] = jwks
    return jwks


def validate_token(token: str) -> dict:
    """
    Validate a Cognito JWT and return its decoded claims.

    Raises AuthError on any validation failure.
    """
    user_pool_id = os.environ.get("COGNITO_USER_POOL_ID", "")
    region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
    app_client_id = os.environ.get("COGNITO_APP_CLIENT_ID", "")

    if not user_pool_id:
        raise AuthError("COGNITO_USER_POOL_ID not configured", "SERVER_ERROR")

    try:
        # Decode header to find the key ID (kid)
        headers = jwt.get_unverified_headers(token)
        kid = headers.get("kid")
        if not kid:
            raise AuthError("Token missing kid header")

        jwks = _get_jwks(user_pool_id, region)
        key_data = next((k for k in jwks["keys"] if k["kid"] == kid), None)
        if not key_data:
            raise AuthError("Public key not found for this token")

        public_key = jwk.construct(key_data)
        claims = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=app_client_id or None,
        )
        return claims

    except JWTError as exc:
        raise AuthError(f"Invalid token: {exc}") from exc


def extract_token_from_header(authorization_header: str | None) -> str:
    """
    Extract the Bearer token from an Authorization header value.

    Raises AuthError if the header is missing or malformed.
    """
    if not authorization_header:
        raise AuthError("Missing Authorization header")

    parts = authorization_header.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthError("Authorization header must be 'Bearer <token>'")

    return parts[1]


def get_current_user_id(authorization_header: str | None) -> str:
    """Convenience helper: extract and validate JWT, return the Cognito 'sub'."""
    token = extract_token_from_header(authorization_header)
    claims = validate_token(token)
    sub = claims.get("sub")
    if not sub:
        raise AuthError("Token missing sub claim")
    return sub

"""
AWS Cognito JWT verification utilities.
"""

import requests
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from jose.exceptions import JWTClaimsError, ExpiredSignatureError
from app.core.config import get_settings

settings = get_settings()


class CognitoJWTVerifier:
    """AWS Cognito JWT token verifier."""
    
    def __init__(self):
        self.user_pool_id = settings.COGNITO_USER_POOL_ID
        self.app_client_id = settings.COGNITO_APP_CLIENT_ID
        self.region = settings.AWS_REGION
        self.jwks_url = f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}/.well-known/jwks.json"
        self._jwks_cache = None
        self._jwks_cache_time = None
    
    def _get_jwks(self) -> Dict[str, Any]:
        """Get JWKS (JSON Web Key Set) from Cognito."""
        import time
        
        # Cache JWKS for 1 hour to avoid frequent requests
        current_time = time.time()
        if (self._jwks_cache is None or 
            self._jwks_cache_time is None or 
            current_time - self._jwks_cache_time > 3600):
            
            try:
                response = requests.get(self.jwks_url, timeout=10)
                response.raise_for_status()
                self._jwks_cache = response.json()
                self._jwks_cache_time = current_time
            except requests.RequestException as e:
                raise Exception(f"Failed to fetch JWKS: {str(e)}")
        
        return self._jwks_cache
    
    def _get_signing_key(self, token: str) -> Optional[str]:
        """Get the signing key for the token."""
        try:
            # Decode token header without verification
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get('kid')
            
            if not kid:
                return None
            
            # Get JWKS
            jwks = self._get_jwks()
            
            # Find the key with matching kid
            for key in jwks.get('keys', []):
                if key.get('kid') == kid:
                    return key
            
            return None
            
        except JWTError:
            return None
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify Cognito JWT token and return payload if valid.
        
        Args:
            token: JWT token to verify
            
        Returns:
            Token payload if valid, None if invalid
        """
        try:
            # Get signing key
            signing_key = self._get_signing_key(token)
            if not signing_key:
                return None
            
            # Verify token
            payload = jwt.decode(
                token,
                signing_key,
                algorithms=['RS256'],
                audience=self.app_client_id,
                issuer=f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}"
            )
            
            # Additional validation
            if payload.get('token_use') != 'access':
                return None
            
            return payload
            
        except (JWTError, JWTClaimsError, ExpiredSignatureError):
            return None
        except Exception as e:
            # Log error for debugging
            print(f"Token verification error: {str(e)}")
            return None
    
    def get_user_info_from_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Extract user information from verified token.
        
        Args:
            token: JWT token
            
        Returns:
            User information dict if token is valid, None otherwise
        """
        payload = self.verify_token(token)
        if not payload:
            return None
        
        return {
            'username': payload.get('username'),
            'sub': payload.get('sub'),  # User ID
            'email': payload.get('email'),
            'email_verified': payload.get('email_verified', False),
            'cognito_groups': payload.get('cognito:groups', []),
            'token_use': payload.get('token_use'),
            'exp': payload.get('exp'),
            'iat': payload.get('iat')
        }


# Global verifier instance
cognito_verifier = CognitoJWTVerifier()


def verify_cognito_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify Cognito JWT token.
    
    Args:
        token: JWT token to verify
        
    Returns:
        User information if token is valid, None otherwise
    """
    return cognito_verifier.get_user_info_from_token(token)


def get_current_user_from_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Get current user information from token.
    
    Args:
        token: JWT token
        
    Returns:
        User information dict if token is valid, None otherwise
    """
    return verify_cognito_token(token)

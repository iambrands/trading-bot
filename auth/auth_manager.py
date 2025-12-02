"""JWT Authentication Manager for Crypto Scalping Trading Bot."""

import jwt
import bcrypt
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict
import logging
from config import get_config

logger = logging.getLogger(__name__)

# Generate a secret key if not set (for production, this should be in .env)
SECRET_KEY = secrets.token_urlsafe(32)


class AuthManager:
    """Handles JWT authentication and password hashing."""
    
    def __init__(self, config=None):
        self.config = config or get_config()
        # In production, this should come from environment variable
        self.secret_key = getattr(self.config, 'JWT_SECRET_KEY', SECRET_KEY)
        self.algorithm = 'HS256'
        self.token_expiry_hours = 24  # Tokens expire after 24 hours
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against a hash."""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    def generate_token(self, user_id: int, email: str) -> str:
        """Generate a JWT token for a user."""
        payload = {
            'user_id': user_id,
            'email': email,
            'exp': datetime.utcnow() + timedelta(hours=self.token_expiry_hours),
            'iat': datetime.utcnow()
        }
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
    
    def extract_token_from_header(self, auth_header: Optional[str]) -> Optional[str]:
        """Extract token from Authorization header (Bearer <token>)."""
        if not auth_header:
            return None
        
        parts = auth_header.split(' ')
        if len(parts) == 2 and parts[0].lower() == 'bearer':
            return parts[1]
        return None


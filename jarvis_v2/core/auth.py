#!/usr/bin/env python3
"""
JARVIS Authentication System
JWT-based authentication for WebSocket connections
"""

import jwt
import time
from typing import Optional, Dict
from datetime import datetime, timedelta

# Secret key - Production'da environment variable'dan alınmalı
SECRET_KEY = "jarvis-secret-key-change-in-production"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 saat

class AuthService:
    """JWT Authentication Service"""
    
    def __init__(self):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
    
    def create_token(self, user_id: str, username: str = "user") -> str:
        """Create JWT token"""
        payload = {
            "user_id": user_id,
            "username": username,
            "exp": datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES),
            "iat": datetime.utcnow()
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            print("❌ Token expired")
            return None
        except jwt.InvalidTokenError:
            print("❌ Invalid token")
            return None
    
    def create_default_token(self) -> str:
        """Create default token for local development"""
        return self.create_token(user_id="local-user", username="JARVIS User")

# Singleton instance
_auth_service = None

def get_auth_service() -> AuthService:
    """Get singleton auth service"""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service

if __name__ == "__main__":
    # Test
    auth = get_auth_service()
    token = auth.create_default_token()
    print(f"Token: {token}")
    
    verified = auth.verify_token(token)
    print(f"Verified: {verified}")

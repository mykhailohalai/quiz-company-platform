from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from app.core import settings

class JWTHelper():
    @staticmethod
    def create_access_token(user_id: UUID, username: str):
        payload_data = {
            "username": username,
            "user_id": str(user_id),
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=settings.jwt_expire_minutes),
        }
        secret_key = settings.jwt_secret_key
        
        token = jwt.encode(
            payload=payload_data,
            key=secret_key,
            algorithm=settings.jwt_algorithm
        )

        return token


import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from decouple import config
from bson import ObjectId
from api.db import users_collection


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith("Bearer "):
            return None  # Means DRF will continue to other authenticators if any

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, config("ACCESS_TOKEN_SECRET"), algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token expired")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token")

        user_id = payload.get("id")  # or "user_id" depending on what you encoded
        if not user_id:
            raise AuthenticationFailed("Invalid payload: missing user_id")

        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise AuthenticationFailed("User not found")

        # DRF requires returning (user, auth_token)
        # You can return the full user dict (or a custom wrapper)
        return (user, token)

def get_user_from_request(request):
    auth = request.headers.get("Authorization", None)
    if not auth or not auth.startswith("Bearer "):
        return None

    token = auth.split(" ")[1]

    payload = jwt.decode(token, config("ACCESS_TOKEN_SECRET"), algorithms=["HS256"])
    return {
        "_id": payload["user_id"]
    }

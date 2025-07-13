
import jwt
from decouple import config
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from bson import ObjectId
from api.db import users_collection


from api.utils.mongo_user import MongoUser  # Import your wrapper

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, config("ACCESS_TOKEN_SECRET"), algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token expired")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token")

        user_id = payload.get("id")
        if not user_id:
            raise AuthenticationFailed("Invalid payload")

        user_dict = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user_dict:
            raise AuthenticationFailed("User not found")

        return (MongoUser(user_dict), token)  #  Wrap dict in MongoUser class
def get_user_from_request(request):
    auth = request.headers.get("Authorization", None)
    if not auth or not auth.startswith("Bearer "):
        return None

    token = auth.split(" ")[1]

    payload = jwt.decode(token, config("ACCESS_TOKEN_SECRET"), algorithms=["HS256"])
    return {
        "_id": payload["user_id"]
    }


import jwt
from rest_framework import permissions
from decouple import config
from api.db import users_collection
from bson import ObjectId

class IsAuthenticatedWithJWT(permissions.BasePermission):
    def has_permission(self, request, view):
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith("Bearer "):
            return False

        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, config("ACCESS_TOKEN_SECRET"), algorithms=["HS256"])
            user_id = payload.get("user_id")
            user = users_collection.find_one({"_id": ObjectId(user_id)})

            if not user:
                return False

            request.user = user  # Attach user to request
            return True

        except (jwt.ExpiredSignatureError, jwt.DecodeError):
            return False

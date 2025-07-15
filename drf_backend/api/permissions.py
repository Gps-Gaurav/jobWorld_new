
import jwt
from rest_framework import permissions
from rest_framework.permissions import BasePermission
from decouple import config
from api.db import users_collection
from bson import ObjectId
from api.utils.jwt_auth import get_user_from_request

class IsAuthenticatedWithJWT(BasePermission):
    def has_permission(self, request, view):
        auth_header = request.headers.get('Authorization')
        print("🔐 Auth Header:", auth_header)

        if not auth_header or not auth_header.startswith("Bearer "):
            print("❌ No valid token")
            return False

        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, config("ACCESS_TOKEN_SECRET"), algorithms=["HS256"])
            print("🧾 Payload:", payload)

            # ✅ Fix: use "id" key instead of "user_id"
            user_id = payload.get("user_id") or payload.get("id")
            if not user_id:
                print("❌ No user_id or id in token")
                return False

            user = users_collection.find_one({"_id": ObjectId(user_id)})
            if not user:
                print("❌ User not found in DB")
                return False

            request.user = user
            print("✅ Authenticated user:", user)
            return True

        except Exception as e:
            print("❌ JWT error:", str(e))
            return False



class IsAdminOrRecruiter(BasePermission):
    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        print("🧑 User in role check:", user)

        if user and user.get("role") in ["admin", "recruiter"]:
            print("✅ Role allowed:", user.get("role"))
            return True

        print("❌ Role not allowed or user missing")
        return False
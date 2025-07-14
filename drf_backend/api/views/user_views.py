
import bcrypt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import permission_classes

from api.db import users_collection
import jwt
from decouple import config
from bson import ObjectId
from api.utils.jwt_tokens import create_access_token, create_refresh_token
from api.utils import jwt_tokens
from api.utils.jwt_auth import get_user_from_request
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from datetime import datetime
from cloudinary.uploader import upload as upload_to_cloudinary 
from rest_framework.permissions import AllowAny, IsAuthenticated


@permission_classes([AllowAny])
class RegisterView(APIView):
    def post(self, request):
        data = request.data
        required = ['fullName', 'email', 'password', 'phoneNumber', 'role']

        for field in required:
            if field not in data:
                return Response({'error': f"{field} is required"}, status=400)

        # Check if user already exists
        if users_collection.find_one({'$or': [{'email': data['email']}, {'phoneNumber': data['phoneNumber']}] }):
            return Response({'error': 'User already exists'}, status=400)

        # Hash the password
        hashed_pw = bcrypt.hashpw(data['password'].encode(), bcrypt.gensalt()).decode()

        # Upload avatar (optional)
        avatar_url = ""
        if 'avatar' in request.FILES:
            cloud_result = upload_to_cloudinary(request.FILES['avatar'])
            avatar_url = cloud_result.get('secure_url', '')

        # Final user object
        user = {
            "fullName": data['fullName'],
            "email": data['email'].lower(),
            "phoneNumber": data['phoneNumber'],
            "password": hashed_pw,
            "role": data['role'],
            "profile": {
                "bio": "",
                "avatar": avatar_url,
                "coverImage": None,
                "skills": [],
                "resume": "",
                "location": {},
                "education": [],
                "experience": [],
                "languages": [],
                "certifications": [],
                "socialLinks": {},
                "interests": [],
                "preferredJobTypes": [],
                "expectedSalary": {}
            },
            "refreshToken": "",
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "__v": 0
        }

        inserted = users_collection.insert_one(user)
        user['_id'] = str(inserted.inserted_id)

        return Response({"message": "User registered", "user": user}, status=201)

@permission_classes([AllowAny])
class LoginView(APIView):
    def post(self, request):
        identifier = request.data.get('identifier')
        password = request.data.get('password')
        role = request.data.get('role')

        if not identifier or not password or not role:
            return Response({'success': False, 'message': 'Email, password, and role are required'}, status=400)

        if role not in ['student', 'recruiter']:
            return Response({'success': False, 'message': 'Invalid role'}, status=400)

        #  First get user
        user = users_collection.find_one({
            "$and": [
                {"$or": [{"email": identifier}, {"phoneNumber": identifier}]},
                {"role": role}
            ]
        })

        if not user or not bcrypt.checkpw(password.encode(), user['password'].encode()):
            return Response({'success': False, 'message': 'Invalid credentials'}, status=401)

        #  Create payload and tokens
        payload = {
            'id': str(user['_id']),
            'email': user['email'],
            'role': user['role']
        }

        access = create_access_token(payload)
        refresh = create_refresh_token(payload)

        #  Then update refresh token
        users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"refreshToken": refresh}}
        )

        return Response({
            'success': True,
            'message': 'Login successful',
            'data': {
                'accessToken': access,
                'refreshToken': refresh,
                'user': {
                    'id': str(user['_id']),
                    'email': user['email'],
                    'role': user['role'],
                    'fullName': user.get('fullName'),
                    'phoneNumber': user.get('phoneNumber'),
                    'profile': user.get('profile', {})
                }
            }
        }, status=200)
       
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            user_id = request.user.get("id") if isinstance(request.user, dict) else request.user.id

            # Clear token from DB
            users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$unset": {"refreshToken": "", "accessToken": ""}}  # optional
            )

            return Response({
                "success": True,
                "message": "Logged out successfully"
            }, status=200)

        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=500)
    permission_classes = [IsAuthenticated]


class RefreshTokenView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response({"error": "Refresh token required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payload = jwt.decode(
                refresh_token,
                config("REFRESH_TOKEN_SECRET"),
                algorithms=["HS256"]
            )
            user_id = payload.get("user_id")

            # Generate new access token
            access_token = create_access_token(user_id)

            return Response({"access": access_token}, status=status.HTTP_200_OK)

        except jwt.ExpiredSignatureError:
            return Response({"error": "Refresh token expired."}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({"error": "Invalid refresh token."}, status=status.HTTP_401_UNAUTHORIZED)
        

class ChangePasswordView(APIView):
    def post(self, request):
        user = jwt_tokens.get_user_from_request(request)
        user_id = user["_id"]
        data = request.data

        old_password = data.get("oldPassword")
        new_password = data.get("newPassword")

        if not old_password or not new_password:
            return Response({"error": "Old and new passwords are required"}, status=400)

        user_doc = users_collection.find_one({"_id": ObjectId(user_id)})

        if not user_doc or not bcrypt.checkpw(old_password.encode(), user_doc["password"].encode()):
            return Response({"error": "Invalid old password"}, status=401)

        hashed_new_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
        users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"password": hashed_new_password}}
        )

        return Response({"message": "Password changed successfully"}, status=200)
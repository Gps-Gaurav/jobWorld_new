# api/views/auth_views.py
import bcrypt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.db import users_collection
import jwt
from decouple import config
from bson import ObjectId
from api.utils.jwt_tokens import create_access_token, create_refresh_token
from api.utils import jwt_tokens


class RegisterView(APIView):
    def post(self, request):
        data = request.data
        full_name = data.get("fullName")
        email = data.get("email")
        phone = data.get("phoneNumber")
        password = data.get("password")

        if users_collection.find_one({"email": email}):
            return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        user = {
            "fullName": full_name,
            "email": email,
            "phoneNumber": phone,
            "password": hashed_password.decode('utf-8')
        }

        users_collection.insert_one(user)
        return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)



class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Email and password required'}, status=400)

        user = users_collection.find_one({'email': email})
        if not user or not bcrypt.checkpw(password.encode(), user['password'].encode()):
            return Response({'error': 'Invalid credentials'}, status=401)

        payload = {'id': str(user['_id']), 'email': user['email']}
        access = create_access_token(payload)
        refresh = create_refresh_token(payload)

        return Response({
            'access': access,
            'refresh': refresh,
            'user': {'id': str(user['_id']), 'email': user['email']}
        })

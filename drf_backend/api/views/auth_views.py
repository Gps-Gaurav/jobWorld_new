
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
import cloudinary.uploader
from django.views.decorators.csrf import csrf_exempt
from bson import ObjectId
from api.db import users_collection  # your pymongo connection
from django.contrib.auth.hashers import make_password

class RegisterView(APIView):
    def post(self, request):
        data = request.data

        # Get fields
        name = data.get("name")
        email = data.get("email")
        password = make_password(data.get("password"))  # hashed password
        role = data.get("role", "student")  # default: student
        photo_file = data.get("photo")

        # Cloudinary upload if photo provided
        photo_url = ""
        if photo_file:
            upload_result = cloudinary.uploader.upload(photo_file)
            photo_url = upload_result["secure_url"]

        # Check if user exists
        if users_collection.find_one({"email": email}):
            return Response({"error": "Email already registered"}, status=400)

        # Insert into Mongo
        user_data = {
            "name": name,
            "email": email,
            "password": password,
            "role": role,
            "photo": photo_url,
        }
        users_collection.insert_one(user_data)

        return Response({"msg": "User registered successfully!"}, status=201)

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

        # Include role and photo if available
        user_data = {
            'id': str(user['_id']),
            'email': user['email'],
            'role': user.get('role', 'student'),  # default fallback
            'photo': user.get('photo', '')        # fallback if no photo
        }

        return Response({
            'access': access,
            'refresh': refresh,
            'user': user_data
        })

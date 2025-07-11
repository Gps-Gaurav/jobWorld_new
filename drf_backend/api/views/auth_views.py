
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
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from datetime import datetime
from cloudinary.uploader import upload as upload_to_cloudinary  # Assuming you're using cloudinary SDK

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

        # ADD THIS BLOCK TO UPDATE refreshToken IN DB
        users_collection.update_one(
            {'_id': user['_id']},
            {
                '$set': {
                    'refreshToken': refresh,
                    'updatedAt': datetime.utcnow()
                }
            }
        )

        return Response({
            'access': access,
            'refresh': refresh,
            'user': {
                'id': str(user['_id']),
                'email': user['email'],
                'role': user['role'],
                'fullName': user['fullName'],
                'profile': user.get('profile', {})
            }
        })

# api/utils/auth_utils.py
import bcrypt
import jwt
from datetime import datetime, timedelta
from decouple import config

ACCESS_SECRET = config("ACCESS_TOKEN_SECRET")
REFRESH_SECRET = config("REFRESH_TOKEN_SECRET")

def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def generate_access_token(user_data: dict) -> str:
    payload = {
        "_id": str(user_data["_id"]),
        "email": user_data["email"],
        "fullname": user_data["fullName"],
        "exp": datetime.utcnow() + timedelta(minutes=int(config("ACCESS_TOKEN_EXPIRY_MINUTES", default=60)))
    }
    return jwt.encode(payload, ACCESS_SECRET, algorithm="HS256")

def generate_refresh_token(user_data: dict) -> str:
    payload = {
        "_id": str(user_data["_id"]),
        "exp": datetime.utcnow() + timedelta(days=int(config("REFRESH_TOKEN_EXPIRY_DAYS", default=7)))
    }
    return jwt.encode(payload, REFRESH_SECRET, algorithm="HS256")

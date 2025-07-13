# api/utils/jwt_auth.py
import jwt
from decouple import config

def get_user_from_request(request):
    auth = request.headers.get("Authorization", None)
    if not auth or not auth.startswith("Bearer "):
        return None

    token = auth.split(" ")[1]

    payload = jwt.decode(token, config("ACCESS_TOKEN_SECRET"), algorithms=["HS256"])
    return {
        "_id": payload["user_id"]
    }

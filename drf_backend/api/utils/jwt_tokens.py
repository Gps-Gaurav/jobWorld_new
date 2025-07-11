import drf_backend.api.utils.jwt_tokens as jwt_tokens
from datetime import datetime, timedelta
from decouple import config

ACCESS_TOKEN_SECRET = config('ACCESS_TOKEN_SECRET')
REFRESH_TOKEN_SECRET = config('REFRESH_TOKEN_SECRET')
ACCESS_TOKEN_EXPIRY = config('ACCESS_TOKEN_EXPIRY', default='1d')
REFRESH_TOKEN_EXPIRY = config('REFRESH_TOKEN_EXPIRY', default='7d')


def get_expiry_time(duration: str):
    """
    Converts expiry like '1d' or '15m' to timedelta.
    """
    unit = duration[-1]
    val = int(duration[:-1])

    if unit == 'd':
        return timedelta(days=val)
    elif unit == 'h':
        return timedelta(hours=val)
    elif unit == 'm':
        return timedelta(minutes=val)
    else:
        return timedelta(minutes=15)  # default


def create_access_token(payload: dict):
    expiry = datetime.utcnow() + get_expiry_time(ACCESS_TOKEN_EXPIRY)
    payload.update({"exp": expiry})
    token = jwt_tokens.encode(payload, ACCESS_TOKEN_SECRET, algorithm="HS256")
    return token


def create_refresh_token(payload: dict):
    expiry = datetime.utcnow() + get_expiry_time(REFRESH_TOKEN_EXPIRY)
    payload.update({"exp": expiry})
    token = jwt_tokens.encode(payload, REFRESH_TOKEN_SECRET, algorithm="HS256")
    return token


def verify_access_token(token: str):
    try:
        payload = jwt_tokens.decode(token, ACCESS_TOKEN_SECRET, algorithms=["HS256"])
        return payload
    except jwt_tokens.ExpiredSignatureError:
        return None
    except jwt_tokens.InvalidTokenError:
        return None

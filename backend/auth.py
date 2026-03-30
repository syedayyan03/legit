import hashlib
import jwt
import datetime
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET_KEY = "LEGIT_SECRET_KEY" # In a real app, use environment variables
ALGORITHM = "HS256"

security = HTTPBearer()

def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed_password: str):
    return hash_password(password) == hashed_password

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_token if decoded_token["exp"] >= datetime.datetime.utcnow().timestamp() else None
    except:
        return None

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload

optional_security = HTTPBearer(auto_error=False)

def get_optional_current_user(credentials: HTTPAuthorizationCredentials = Security(optional_security)):
    if not credentials:
        return None
    token = credentials.credentials
    return decode_access_token(token)

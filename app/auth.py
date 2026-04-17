from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from app.models import UserInDB, TokenData, Role

# Security configuration
SECRET_KEY = "mediserve-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")

# Fake user database - in production this would be a real database
FAKE_USERS_DB = {
    "dr_smith": {
        "username": "dr_smith",
        "email": "dr.smith@mediserve.com",
        "role": Role.DOCTOR,
        "hashed_password": pwd_context.hash("doctor123"),
        "disabled": False
    },
    "admin_jane": {
        "username": "admin_jane",
        "email": "jane@mediserve.com",
        "role": Role.ADMIN,
        "hashed_password": pwd_context.hash("admin123"),
        "disabled": False
    },
    "insurance_acme": {
        "username": "insurance_acme",
        "email": "acme@insurance.com",
        "role": Role.INSURANCE,
        "hashed_password": pwd_context.hash("insurance123"),
        "disabled": False
    }
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_user(username: str) -> Optional[UserInDB]:
    if username in FAKE_USERS_DB:
        user_data = FAKE_USERS_DB[username]
        return UserInDB(**user_data)
    return None


def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[TokenData]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None:
            return None
        return TokenData(username=username, role=role)
    except JWTError:
        return None
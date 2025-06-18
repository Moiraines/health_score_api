from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from datetime import datetime, timedelta
from app.core.security import get_current_user
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from app.core.config import settings
import secrets
import os
# from dotenv import load_dotenv
#
# load_dotenv()

app = FastAPI(
    title="Health Score API",
    description="API for managing user health scores and fitness activities",
    version="1.0.0",
)

# Security settings
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

# Dummy database (replace with actual database)
dummy_db = {
    "testuser": {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": pwd_context.hash("testpassword"),
        "full_name": "Test User",
        "disabled": False,
    }
}

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/token", response_model=Token)
async def login_for_access_token(username: str, password: str):
    user = authenticate_user(dummy_db, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username}, expires_delta=refresh_token_expires
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@app.post("/token/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        user = get_user(dummy_db, username)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(
            data={"sub": user.username}, expires_delta=refresh_token_expires
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# Health Score endpoints
@app.post("/health-scores")
async def create_health_score(current_user: User = Depends(get_current_user)):
    # Implement health score creation logic
    pass

@app.get("/health-scores/{score_id}")
async def get_health_score(score_id: str, current_user: User = Depends(get_current_user)):
    # Implement health score retrieval logic
    pass

# Import routers for different API modules
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.health_score import router as health_score_router
from app.api.v1.activities import router as activities_router

# Include API routers with version prefix
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(health_score_router, prefix="/api")
app.include_router(activities_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to the Health Score API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

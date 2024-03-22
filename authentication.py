from fastapi import HTTPException
from grpc import Status
from passlib.context import CryptContext
from models import User
from config import config_credential

import jwt

from datetime import datetime, timedelta

# pwd -> password
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# Função para comparar a senha digitada com a senha criptografada
def get_hashed_password(password):
    return pwd_context.hash(password)

async def very_token(token : str):
    try:
        payload = jwt.decode(token, config_credential['SECRET'], algorithms=["HS256"])
        user = await User.get(id=payload.get('id'))
    except:
        raise HTTPException(
            status_code = Status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    return user

async def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

async def autheticate_user(username, password):
    user = await User.get(username=username)
    
    if user and verify_password(password, user.password):
        return user
    return "Invalid user"


async def token_generator(username : str, password : str):
    user = await autheticate_user(username, password)
    if not user:
        raise HTTPException(
            status_code = Status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"}
        ) 
        
    token_data = {
        "id": user.id,
        "username": user.username,
        "exp": datetime.utcnow() + timedelta(hours=1) # token expira em 1 hora
    }
    
    token = jwt.encode(token_data, config_credential['SECRET'], algorithm="HS256")
    
    return token

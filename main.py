from fastapi import FastAPI, Depends, requests, HTTPException, status
from starlette.requests import Request
from starlette.responses import HTMLResponse
from tortoise import models
from tortoise.contrib.fastapi import register_tortoise
from models import User, Business, Product
from models import user_pydantic, user_pydanticIn, business_pydantic

# autenticação
from authentication import token_generator, get_hashed_password, config_credential
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# template
from fastapi.templating import Jinja2Templates
from jwt import PyJWTError
import jwt
from config import config_credential

# Importando o sinal de tortoise
from tortoise.signals import post_save
from typing import List, Optional, Type
from tortoise import BaseDBAsyncClient

# response class
from fastapi.responses import HTMLResponse



# Criando a instância do FastAPI
app = FastAPI()

# Criando a instância do OAuth2
oath2_scheme = OAuth2PasswordBearer(tokenUrl="token")



@app.post('/token')
async def generate_token(request_form: OAuth2PasswordRequestForm = Depends()):
    token = await token_generator(request_form.username, request_form.password)    
    return {'acess_token': token, "token_type": "bearer"}


async def get_current_user(token: str = Depends(oath2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, config_credential['SECRET'], algorithms=["HS256"])
        user_id: str = payload.get("id")
        
        if user_id is None:
            raise credentials_exception
        
    except PyJWTError:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    user = await User.get(id=user_id)
    return user



@app.post('/user/me')
async def user_login(user: user_pydanticIn = Depends(get_current_user)):
    business = await Business.get(owner=user)
    return {
        'status': 'ok',
        'data': {
            'username': user.username,
            'email' : user.email,
            'verify': user.is_verify,
            'joined_date': user.joined_date.strftime('%b-%d-%Y'),
        } 
    }


# criar um negócio para cada usuário registrado
@post_save(User)
async def create_business(
    # sender -> Tipo de objeto que está sendo enviado
    sender: "Type[User]",
    # instance -> Instância do objeto que está sendo enviada
    instance: User,
    # created -> Se o objeto foi criado ou não
    created: bool,
    # using_db -> Banco de dados que está sendo usado
    using_db: "Optional[BaseDBAsyncClient]",
    # update_fields -> Campos que foram atualizados
    update_fileds: List[str]
) -> None: # None -> Não retorna nada
    
    # Se o usuário foi criado, criar um negócio para ele
    if created:
        business_obj = await Business.create(
            business_name = instance.username, owner = instance
        )
        # transformar o objeto tortoise em um objeto pydantic
        await business_pydantic.from_tortoise_orm(business_obj)
        # enviar email
        

# Rota de registro de usuário
@app.post("/registration")
async def user_registration(user: user_pydanticIn): # type: ignore
    # Verificar se o usuário já existe
    user_info = user.dict(exclude_unset=True)
    # senha -> senha criptografada
    user_info['password'] = get_hashed_password(user_info['password'])
    # Criar um novo usuário
    user_obj = await User.create(**user_info)
    # Transformar o objeto tortoise em um objeto pydantic
    new_user = await user_pydantic.from_tortoise_orm(user_obj)
    # retorna a resposta
    return {
        "status: ":  "ok",
        "data: " : f"Hello {new_user.username}, obrigada por escolher nosso serviço! Por favor, verifique o seu email e clique no link para confirmar o registro."
    }

# Rota de teste
@app.get("/")
def index():
    return {"Mensagem": "Hello World!"}


# Registrando o Tortoise ORM com FastAPI
register_tortoise(
    app,
    db_url="sqlite://database.sqlite3",
    modules={"models" : ['models']},
    generate_schemas=True,
    add_exception_handlers=True
)
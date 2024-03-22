from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from models import *
from authentication import (get_hashed_password)

# Importando o sinal de tortoise
from tortoise.signals import post_save
from typing import List, Optional, Type
from tortoise import BaseDBAsyncClient

# Criando a instância do FastAPI
app = FastAPI()


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
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from models import User, Business, Product

# Criando a instância do FastAPI
app = FastAPI()

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
from passlib.context import CryptContext

# pwd -> password
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# Função para comparar a senha digitada com a senha criptografada
def get_hashed_password(password):
    return pwd_context.hash(password)




import os
from sqlalchemy import create_engine, Column, Integer, String, Float, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import bcrypt

load_dotenv()

def get_custo(codigo):
    session = Session()
    custo = session.query(Custos).filter_by(codigo=codigo).first()
    session.close()
    return custo
Base = declarative_base()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("❌ ERRO: A variável DATABASE_URL não está definida!")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Classes
class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
    nivel = Column(String)  # 'admin', 'engenharia', ou 'vendedor'

class Custos(Base):  
    __tablename__ = 'custos'
    codigo = Column(String(4), primary_key=True)
    descricao = Column(String(50), nullable=False)
    unidade = Column(String(10), nullable=False)
    valor = Column(Float, nullable=False)

class Parametros(Base):
    __tablename__ = 'parametros'
    id = Column(Integer, primary_key=True)
    parametro = Column(String, nullable=False)
    valor = Column(Float, nullable=False)

# Funçoes para iniciar e atualizar banco de dados

def init_db():
    inspector = inspect(engine)
    
    # Cria a tabela de usuários se não existir
    if not inspector.has_table('usuarios'):
        Base.metadata.create_all(engine, tables=[Usuario.__table__])
    
    # Cria a tabela de custos se não existir
    if not inspector.has_table('custos'):
        Base.metadata.create_all(engine, tables=[Custos.__table__])
    
    # Cria a tabela de parâmetros se não existir
    if not inspector.has_table('parametros'):
        Base.metadata.create_all(engine, tables=[Parametros.__table__])
    
    add_admin_if_not_exists()

def recreate_users_table():
    Base.metadata.drop_all(engine, tables=[Usuario.__table__])
    Base.metadata.create_all(engine, tables=[Usuario.__table__])
    print("Tabela 'usuarios' recriada.")

def add_admin_if_not_exists():
    with Session() as session:
        admin = session.query(Usuario).filter_by(username='admin').first()
        if not admin:
            hashed_password = hash_password('fuza123')
            novo_admin = Usuario(username='admin', password=hashed_password, nivel='admin')
            session.add(novo_admin)
            session.commit()
            print("Usuário admin criado.")
        elif not admin.nivel:
            admin.nivel = 'admin'
            session.commit()
            print("Nível do usuário admin atualizado.")

# Funcoes de busca
def get_user(username):
    session = Session()
    user = session.query(Usuario).filter_by(username=username).first()
    session.close()
    return user

def get_custo(codigo):
    session = Session()
    custo = session.query(Custos).filter_by(codigo=codigo).first()
    session.close()
    return custo

def get_parametro(parametro_id):
    session = Session()
    custo = session.query(Parametros).filter_by(id=parametro_id).first()
    session.close()
    return custo

# Funcoes internas

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

# -- Funções CRUD de usuarios --

def get_all_users():
    session = Session()
    usuarios = session.query(Usuario).all()
    session.close()
    return usuarios

def add_user(username, password, nivel):
    session = Session()
    hashed_password = hash_password(password)
    novo_usuario = Usuario(
        username=username,
        password=hashed_password,
        nivel=nivel
    )
    session.add(novo_usuario)
    session.commit()
    session.close()

def update_user(old_username, new_username, new_password, nivel):
    session = Session()
    user = session.query(Usuario).filter_by(username=old_username).first()
    if not user:
        session.close()
        return False

    if new_username.strip():
        user.username = new_username.strip()
    if new_password.strip():
        user.password = hash_password(new_password.strip())
    user.nivel = nivel
    session.commit()
    session.close()
    return True

def remove_user(username):
    """
    Remove um usuário do BD.
    """
    session = Session()
    user = session.query(Usuario).filter_by(username=username).first()
    if user:
        session.delete(user)
        session.commit()
    session.close()

# -- Funções CRUD de custos --

def get_all_custos():
    session = Session()
    custos = session.query(Custos).order_by(Custos.codigo).all()
    session.close()
    return custos

def add_custo(codigo, descricao, unidade, valor):
    session = Session()
    novo_custo = Custos(codigo=codigo, descricao=descricao, unidade=unidade, valor=valor)
    session.add(novo_custo)
    session.commit()
    session.close()

def update_custo(codigo, descricao, unidade, valor):
    session = Session()
    custo = session.query(Custos).filter_by(codigo=codigo).first()
    if custo:
        custo.descricao = descricao
        custo.unidade = unidade
        custo.valor = valor
        session.commit()
    session.close()

def remove_custo(codigo):
    session = Session()
    custo = session.query(Custos).filter_by(codigo=codigo).first()
    if custo:
        session.delete(custo)
        session.commit()
    session.close()

# -- Funções CRUD de parametros --

def get_all_parametros():
    session = Session()
    custos = session.query(Parametros).all()
    session.close()
    return custos

def add_parametro(parametro, valor):
    session = Session()
    novo_parametro = Parametros(parametro=parametro, valor=valor)
    session.add(novo_parametro)
    session.commit()
    session.close()

def update_parametro(parametro_id, novo_parametro, novo_valor):
    session = Session()
    parametro = session.query(Parametros).filter_by(id=parametro_id).first()
    if parametro:
        parametro.parametro = novo_parametro
        parametro.valor = novo_valor
        session.commit()
    session.close()

def remove_parametro(parametro_id):
    session = Session()
    parametro = session.query(Parametros).filter_by(id=parametro_id).first()
    if parametro:
        session.delete(parametro)
        session.commit()
    session.close()
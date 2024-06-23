from sqlalchemy import create_engine, Column, String, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Imovel(Base):
    __tablename__ = 'imoveis'
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, unique=True, nullable=False)
    titulo = Column(String)
    data_primeiro_leilao = Column(String)
    valor_primeiro_leilao = Column(String)
    data_segundo_leilao = Column(String)
    valor_segundo_leilao = Column(String)
    descricao = Column(String)
    imagem = Column(String)
    cidade = Column(String)
    estado = Column(String)
    disponivel = Column(Boolean, default=True)
    local = Column(String)  # Novo campo

# Configuração do banco de dados
engine = create_engine('sqlite:///imoveis.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

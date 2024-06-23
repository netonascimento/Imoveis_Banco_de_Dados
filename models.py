from sqlalchemy import create_engine, Column, String, Integer, Boolean, Float
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
    local = Column(String)
    area = Column(Float)  # Novo campo para a área do imóvel
    custo_por_m2_primeiro_leilao = Column(Float)  # Custo por m² no primeiro leilão
    custo_por_m2_segundo_leilao = Column(Float)  # Custo por m² no segundo leilão
    localizacao = Column(String)  # Novo campo para a localização do bem

# Configuração do banco de dados
engine = create_engine('sqlite:///imoveis.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

import pandas as pd
from models import Session, Imovel

def export_to_csv():
    session = Session()
    imoveis = session.query(Imovel).all()
    session.close()

    data = []
    for imovel in imoveis:
        data.append({
            'URL': imovel.url,
            'Título': imovel.titulo,
            'Data do Primeiro Leilão': imovel.data_primeiro_leilao,
            'Valor do Primeiro Leilão': imovel.valor_primeiro_leilao,
            'Data do Segundo Leilão': imovel.data_segundo_leilao,
            'Valor do Segundo Leilão': imovel.valor_segundo_leilao,
            'Descrição': imovel.descricao,
            'Imagem': imovel.imagem,
            'Cidade': imovel.cidade,
            'Estado': imovel.estado,
            'Disponível': imovel.disponivel,
            'Local': imovel.local
        })

    df = pd.DataFrame(data)
    print(df)
    csv_path = 'imoveis.csv'
    df.to_csv(csv_path, index=False, sep=';')
    return csv_path

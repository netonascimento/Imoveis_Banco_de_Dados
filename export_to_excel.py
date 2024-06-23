import pandas as pd
from models import Session, Imovel

def export_to_xlsx():
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
            'Disponível': 'Sim' if imovel.disponivel else 'Não',
            'Local': imovel.local
        })

    df = pd.DataFrame(data)
    xlsx_path = 'imoveis.xlsx'
    df.to_excel(xlsx_path, index=False, engine='openpyxl')
    return xlsx_path

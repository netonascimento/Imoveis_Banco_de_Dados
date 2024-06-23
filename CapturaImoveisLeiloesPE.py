import time
from bs4 import BeautifulSoup
import requests
import pandas as pd
from models import Session, Imovel
from sqlalchemy.exc import IntegrityError

def get_page_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    response = requests.get(url, headers=headers)
    time.sleep(0.001)  # Tempo de espera entre as requisições
    return response.content

def get_total_pages(content):
    soup = BeautifulSoup(content, 'html.parser')
    pagination = soup.find_all('li', class_='page-item')
    if pagination:
        last_page_link = pagination[-1].find('a', class_='page-link')
        total_pages = int(last_page_link.text.strip()) if last_page_link else 1
    else:
        total_pages = 1
    return total_pages

def extract_property_links(content):
    soup = BeautifulSoup(content, 'html.parser')
    property_links = []
    property_items = soup.find_all('a', class_='btn btn-block btn-dark')
    for item in property_items:
        link = item['href']
        property_links.append(link)
    return property_links

def extract_property_details(content):
    soup = BeautifulSoup(content, 'html.parser')
    property_info = {}

    # Extraindo título e descrição
    titulo_tag = soup.find('h1')
    property_info['titulo'] = titulo_tag.text.strip() if titulo_tag else 'N/A'

    descricao_tag = soup.find('div', class_='mb-3 p-2 border rounded text-justify')
    descricao_completa = descricao_tag.text.strip() if descricao_tag else 'N/A'
    
    # Encontrar "Descrição do bem" na descrição
    index_descricao = descricao_completa.find('Descrição do bem:')
    if index_descricao != -1:
        descricao_resumida = descricao_completa[index_descricao:]
    else:
        descricao_resumida = descricao_completa

    property_info['descricao_completa'] = descricao_completa
    property_info['descricao_resumida'] = descricao_resumida

    # Extraindo a localização do bem
    localizacao = ''
    lines = descricao_completa.split('\n')
    for line in lines:
        if 'Localização do bem:' in line:
            localizacao = line.replace('Localização do bem:', '').strip()
    
    property_info['localizacao'] = localizacao if localizacao else 'N/A'

    # Extraindo dados de leilão
    detalhes = soup.find_all('h6', class_='text-center border-top p-2 m-0')
    for detalhe in detalhes:
        if 'Data 1º Leilão' in detalhe.text:
            property_info['data_primeiro_leilao'] = detalhe.text.replace('Data 1º Leilão:', '').strip()
        elif 'Lance Inicial' in detalhe.text and 'data_primeiro_leilao' in property_info:
            property_info['valor_primeiro_leilao'] = detalhe.text.replace('Lance Inicial:', '').strip()
        elif 'Data 2º Leilão' in detalhe.text:
            property_info['data_segundo_leilao'] = detalhe.text.replace('Data 2º Leilão:', '').strip()
        elif 'Lance Inicial' in detalhe.text and 'data_segundo_leilao' in property_info:
            property_info['valor_segundo_leilao'] = detalhe.text.replace('Lance Inicial:', '').strip()
            print(property_info['valor_segundo_leilao'])

    # Extraindo cidade e estado
    cidade_estado = ''
    for line in lines:
        if 'Cidade:' in line:
            cidade_estado = line.replace('Cidade:', '').strip()
            break

    if '/' in cidade_estado:
        cidade, estado = cidade_estado.split('/')
        property_info['cidade'] = cidade.strip()
        property_info['estado'] = estado.strip()
    else:
        property_info['cidade'] = cidade_estado
        property_info['estado'] = 'N/A'
    
    # Extraindo link da imagem
    imagem_tag = soup.find('div', class_='img-cover')
    if imagem_tag and 'style' in imagem_tag.attrs:
        style = imagem_tag['style']
        start = style.find("url('") + len("url('")
        end = style.find("')", start)
        image_url = style[start:end]
        property_info['imagem'] = image_url
    else:
        property_info['imagem'] = 'N/A'

    return property_info

def save_to_csv(session):
    imoveis = session.query(Imovel).all()
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
            'Local': imovel.local,
            'Localização': imovel.localizacao
        })

    df = pd.DataFrame(data)
    csv_path = 'imoveis.csv'
    df.to_csv(csv_path, index=False, sep=';', encoding='utf-8')
    return csv_path

def main():
    session = Session()
    base_url = 'https://www.leilaopernambuco.com.br/lotes/imovel?tipo=imovel&page=1'
    
    # Obtendo o conteúdo da primeira página para determinar o número total de páginas
    first_page_content = get_page_content(base_url)
    total_pages = get_total_pages(first_page_content)
    print(f'Total de páginas encontradas: {total_pages}')

    all_property_links = []
    for page_num in range(1, total_pages + 1):
        page_url = f'https://www.leilaopernambuco.com.br/lotes/imovel?tipo=imovel&page={page_num}'
        print(f'Extraindo imóveis da página: {page_url}')
        page_content = get_page_content(page_url)
        property_links = extract_property_links(page_content)
        print(f'Links de imóveis extraídos: {len(property_links)}')
        all_property_links.extend(property_links)

    # Coletando detalhes de todos os imóveis
    for property_link in all_property_links:
        print(f'Extraindo detalhes do imóvel: {property_link}')
        property_content = get_page_content(property_link)
        property_details = extract_property_details(property_content)
        if property_details:
            try:
                # Salvando os detalhes no banco de dados
                existing_imovel = session.query(Imovel).filter_by(url=property_link).first()
                if existing_imovel:
                    print(f"Atualizando imóvel existente: {property_link}")
                    existing_imovel.titulo = property_details.get('titulo', 'N/A')
                    existing_imovel.data_primeiro_leilao = property_details.get('data_primeiro_leilao', 'N/A')
                    existing_imovel.valor_primeiro_leilao = property_details.get('valor_primeiro_leilao', 'N/A')
                    existing_imovel.data_segundo_leilao = property_details.get('data_segundo_leilao', 'N/A')
                    existing_imovel.valor_segundo_leilao = property_details.get('valor_segundo_leilao', 'N/A')
                    existing_imovel.descricao = property_details.get('descricao_resumida', 'N/A')
                    existing_imovel.cidade = property_details.get('cidade', 'N/A')
                    existing_imovel.estado = property_details.get('estado', 'N/A')
                    existing_imovel.disponivel = True
                    existing_imovel.local = 'leilaopernambuco'
                    existing_imovel.localizacao = property_details.get('localizacao', 'N/A')
                    existing_imovel.imagem = property_details.get('imagem', 'N/A')
                else:
                    print(f"Inserindo novo imóvel: {property_link}")
                    imovel = Imovel(
                        url=property_link,
                        titulo=property_details.get('titulo', 'N/A'),
                        data_primeiro_leilao=property_details.get('data_primeiro_leilao', 'N/A'),
                        valor_primeiro_leilao=property_details.get('valor_primeiro_leilao', 'N/A'),
                        data_segundo_leilao=property_details.get('data_segundo_leilao', 'N/A'),
                        valor_segundo_leilao=property_details.get('valor_segundo_leilao', 'N/A'),
                        descricao=property_details.get('descricao_resumida', 'N/A'),
                        cidade=property_details.get('cidade', 'N/A'),
                        estado=property_details.get('estado', 'N/A'),
                        disponivel=True,
                        local='leilaopernambuco',
                        localizacao=property_details.get('localizacao', 'N/A'),
                        imagem=property_details.get('imagem', 'N/A')
                    )
                    session.add(imovel)
                session.commit()
            except IntegrityError:
                session.rollback()
                print(f"Erro ao inserir o imóvel com URL: {property_link}")

    csv_path = save_to_csv(session)
    print(f'Dados salvos em {csv_path}')
    
    session.close()

if __name__ == '__main__':
    main()

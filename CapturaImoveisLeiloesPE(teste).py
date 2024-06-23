import requests
from bs4 import BeautifulSoup
import time
import brotli
from models import Session, Imovel  # Importando as configurações do banco de dados e o modelo

# Configurações para os headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}

# Função para obter o conteúdo de uma página específica
def get_page_content(url):
    response = requests.get(url, headers=headers)
    # print(f'Status Code for {url}: {response.status_code}')
    # if response.status_code == 410:
    #     print(f'The resource at {url} has been permanently removed.')
    #     return None
    # elif response.status_code != 200:
    #     print(f'Error {response.status_code} accessing {url}')
    #     return None
    
    # # Descomprimir conteúdo se necessário
    # try:
    #     if response.headers.get('Content-Encoding') == 'gzip':
    #         content = gzip.decompress(response.content)
    #     elif response.headers.get('Content-Encoding') == 'deflate':
    #         content = response.content.decode('deflate')
    #     elif response.headers.get('Content-Encoding') == 'br':
    #         content = brotli.decompress(response.content)
    #     else:
    #         content = response.content
        
    #     # Tentar decodificar o conteúdo para utf-8
    #     content = content.decode('utf-8')
    # except (brotli.error, UnicodeDecodeError) as e:
    #     print(f"Erro ao descomprimir ou decodificar o conteúdo: {e}")
    #     return None
    
    return response.content

# Função para extrair o número total de páginas
def get_total_pages(content):
    if content is None:
        return 0
    print("Capturando o total de páginas...")
    soup = BeautifulSoup(content, 'html.parser')
    pagination = soup.find_all('li', class_='page-item')
    last_page_link = pagination[-1].find('a', class_='page-link') if pagination else None
    total_pages = int(last_page_link.text.strip()) if last_page_link else 1
    print(f"Total de páginas: {total_pages}")
    return total_pages

# Função para extrair os links dos imóveis de uma página
def extract_property_links(content):
    if content is None:
        return []
    soup = BeautifulSoup(content, 'html.parser')
    property_links = []
    property_items = soup.find_all('a', class_='btn btn-block btn-dark')
    for item in property_items:
        link = item['href']
        property_links.append(link)
    return property_links

# Função para extrair os detalhes de um imóvel
def extract_property_details(content):
    if content is None:
        return {}
    soup = BeautifulSoup(content, 'html.parser')
    property_info = {}

    titulo_tag = soup.find('h1')
    property_info['Título'] = titulo_tag.text.strip() if titulo_tag else 'N/A'

    detalhes = soup.find_all('h6', class_='text-center border-top p-2 m-0')

    property_info['Data do Primeiro Leilão'] = 'N/A'
    property_info['Valor do Primeiro Leilão'] = 'N/A'
    property_info['Data do Segundo Leilão'] = 'N/A'
    property_info['Valor do Segundo Leilão'] = 'N/A'

    for detalhe in detalhes:
        if 'Data 1º Leilão' in detalhe.text:
            property_info['Data do Primeiro Leilão'] = detalhe.text.replace('Data 1º Leilão:', '').strip()
        elif 'Lance Inicial' in detalhe.text and property_info['Valor do Primeiro Leilão'] == 'N/A':
            property_info['Valor do Primeiro Leilão'] = detalhe.text.replace('Lance Inicial:', '').strip()
        elif 'Data 2º Leilão' in detalhe.text:
            property_info['Data do Segundo Leilão'] = detalhe.text.replace('Data 2º Leilão:', '').strip()
        elif 'Lance Inicial' in detalhe.text and property_info['Valor do Primeiro Leilão'] != 'N/A':
            property_info['Valor do Segundo Leilão'] = detalhe.text.replace('Lance Inicial:', '').strip()

    descricao_tag = soup.find('div', class_='mb-3 p-2 border rounded text-justify')
    property_info['Descrição'] = descricao_tag.text.strip() if descricao_tag else 'N/A'

    url_tag = soup.find('meta', property='og:url')
    property_info['URL'] = url_tag['content'] if url_tag else 'N/A'

    imagem_tag = soup.find('meta', property='og:image')
    property_info['Imagem'] = imagem_tag['content'] if imagem_tag else 'N/A'

    # Extraindo cidade e estado
    descricao_texto = descricao_tag.get_text() if descricao_tag else ''
    cidade_estado = ''
    for line in descricao_texto.split('\n'):
        if 'Cidade:' in line:
            cidade_estado = line.replace('Cidade:', '').strip()
            break

    if '/' in cidade_estado:
        cidade, estado = cidade_estado.split('/')
        property_info['Cidade'] = cidade.strip()
        property_info['Estado'] = estado.strip()
    else:
        property_info['Cidade'] = cidade_estado
        property_info['Estado'] = 'N/A'

    return property_info

# Função para salvar ou atualizar imóveis no banco de dados
def save_or_update_imovel(imovel_data, local):
    session = Session()  # Cria uma nova instância de sessão
    imovel = session.query(Imovel).filter_by(url=imovel_data['URL']).first()
    if imovel:
        imovel.titulo = imovel_data['Título']
        imovel.data_primeiro_leilao = imovel_data['Data do Primeiro Leilão']
        imovel.valor_primeiro_leilao = imovel_data['Valor do Primeiro Leilão']
        imovel.data_segundo_leilao = imovel_data['Data do Segundo Leilão']
        imovel.valor_segundo_leilao = imovel_data['Valor do Segundo Leilão']
        imovel.descricao = imovel_data['Descrição']
        imovel.imagem = imovel_data['Imagem']
        imovel.cidade = imovel_data['Cidade']
        imovel.estado = imovel_data['Estado']
        imovel.disponivel = True
        imovel.local = local
    else:
        imovel = Imovel(
            url=imovel_data['URL'],
            titulo=imovel_data['Título'],
            data_primeiro_leilao=imovel_data['Data do Primeiro Leilão'],
            valor_primeiro_leilao=imovel_data['Valor do Primeiro Leilão'],
            data_segundo_leilao=imovel_data['Data do Segundo Leilão'],
            valor_segundo_leilao=imovel_data['Valor do Segundo Leilão'],
            descricao=imovel_data['Descrição'],
            imagem=imovel_data['Imagem'],
            cidade=imovel_data['Cidade'],
            estado=imovel_data['Estado'],
            disponivel=True,
            local=local
        )
        session.add(imovel)
    session.commit()
    session.close()

# URL da primeira página
page_url = 'https://www.leilaopernambuco.com.br/lotes/imovel?tipo=imovel&page=1'
local = 'leilaopernambuco'  # Adiciona o local de onde os imóveis estão sendo extraídos

# Cria uma nova instância de sessão
session = Session()

# Coletar links de imóveis da primeira página
print(f'Extraindo imóveis da página: {page_url}')
page_content = get_page_content(page_url)
property_links = extract_property_links(page_content)
print(f'Links de imóveis extraídos: {len(property_links)}')

# Obtendo o número total de páginas
total_pages = get_total_pages(page_content)

# Coletando links de imóveis de todas as páginas
for page_num in range(2, total_pages + 1):
    page_url = f'https://www.leilaopernambuco.com.br/lotes/imovel?tipo=imovel&page={page_num}'
    print(f'Extraindo imóveis da página: {page_url}')
    page_content = get_page_content(page_url)
    property_links.extend(extract_property_links(page_content))
    time.sleep(0.01)  # Adicionando delay entre as requisições

print(f'Total de links de imóveis extraídos: {len(property_links)}')

# Atualizando a disponibilidade de todos os imóveis para False antes de iniciar a nova coleta
session.query(Imovel).update({Imovel.disponivel: False})
session.commit()

# Coletando detalhes de todos os imóveis
all_properties = []
for property_link in property_links:
    print(f'Extraindo detalhes do imóvel: {property_link}')
    property_content = get_page_content(property_link)
    if property_content is None:
        continue  # Pula a iteração se o conteúdo for None
    property_details = extract_property_details(property_content)
    if not property_details:
        continue  # Pula a iteração se não conseguiu extrair detalhes
    save_or_update_imovel(property_details, local)
    all_properties.append(property_details)
    time.sleep(0.01)  # Adicionando delay entre as requisições

# Listando imóveis não encontrados para marcar como não disponíveis
for imovel in session.query(Imovel).filter(Imovel.url.notin_([imovel['URL'] for imovel in all_properties])).all():
    imovel.disponivel = False
session.commit()

session.close()

print(f'Total de imóveis extraídos: {len(all_properties)}')

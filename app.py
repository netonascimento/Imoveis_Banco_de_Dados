from flask import Flask, render_template, jsonify, redirect, url_for, send_file
from models import Session, Imovel
from CapturaImoveisLeiloesPE import save_to_csv
import os

app = Flask(__name__)

@app.route('/')
def index():
    session = Session()
    default_estado = 'PE'  # Define o estado padrão
    estados = sorted(set(imovel.estado for imovel in session.query(Imovel).all() if imovel.estado))
    session.close()
    return render_template('index.html', estados=estados, default_estado=default_estado)

@app.route('/api/imoveis')
def api_imoveis():
    session = Session()
    imoveis = session.query(Imovel).all()
    session.close()

    imoveis_data = [{
        'url': imovel.url,
        'titulo': imovel.titulo,
        'data_primeiro_leilao': imovel.data_primeiro_leilao,
        'valor_primeiro_leilao': imovel.valor_primeiro_leilao,
        'data_segundo_leilao': imovel.data_segundo_leilao,
        'valor_segundo_leilao': imovel.valor_segundo_leilao,
        'descricao_completa': imovel.descricao,
        'descricao_resumida': imovel.descricao[:50] + '...' if len(imovel.descricao) > 50 else imovel.descricao,
        'imagem': imovel.imagem,
        'cidade': imovel.cidade,
        'estado': imovel.estado,
        'disponivel': imovel.disponivel,
        'local': imovel.local,
        'localizacao': imovel.localizacao
    } for imovel in imoveis]

    return jsonify(imoveis_data)

@app.route('/atualizar')
def atualizar():
    os.system('python scraper.py')
    return redirect(url_for('index'))

@app.route('/exportar')
def exportar():
    csv_path = save_to_csv(Session())
    return send_file(csv_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

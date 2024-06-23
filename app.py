from flask import Flask, render_template, jsonify, redirect, url_for, send_file
from models import Session, Imovel
from  export_to_excel import export_to_xlsx
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
        'descricao': imovel.descricao,
        'imagem': imovel.imagem,
        'cidade': imovel.cidade,
        'estado': imovel.estado,
        'disponivel': imovel.disponivel,
        'local': imovel.local
    } for imovel in imoveis]

    return jsonify(imoveis_data)

@app.route('/atualizar')
def atualizar():
    os.system('python scraper.py')
    return redirect(url_for('index'))

@app.route('/exportar')
def exportar():
    xlsx_path = export_to_xlsx()
    return send_file(xlsx_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

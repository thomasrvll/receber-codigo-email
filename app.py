# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re

# Inicializa o aplicativo Flask
app = Flask(__name__)
# Habilita o CORS para permitir que o front-end acesse esta API
CORS(app)

def obter_codigo_do_email(mailbox=""):
    """
    Esta função busca o email e retorna um dicionário com o resultado.
    """
    try:
        headers = {
            "x-rapidapi-key": "078fdc91bcmsh987d0980e53f51ep12d907jsn5d09ebb75145",
            "x-rapidapi-host": "temp-mail-maildrop1.p.rapidapi.com"
        }

        # PASSO 1: Listar e-mails para obter o ID
        url_lista = f"https://temp-mail-maildrop1.p.rapidapi.com/mailbox/{mailbox}"
        response_lista = requests.get(url_lista, headers=headers)

        if response_lista.status_code != 200:
            return {"sucesso": False, "erro": f"Erro ao buscar a lista de e-mails: {response_lista.text}"}
        
        inbox_data = response_lista.json()
        if not inbox_data.get("success") or not inbox_data.get("data"):
            return {"sucesso": False, "erro": "Caixa de e-mails vazia ou não encontrada."}

        email_mais_recente = inbox_data["data"][0]
        email_id = email_mais_recente["id"]

        # PASSO 2: Usar o ID e o NOME DA CAIXA para buscar o conteúdo
        url_conteudo = f"https://temp-mail-maildrop1.p.rapidapi.com/mailbox/{mailbox}/message/{email_id}"
        response_conteudo = requests.get(url_conteudo, headers=headers)

        if response_conteudo.status_code != 200:
            return {"sucesso": False, "erro": f"Erro ao buscar o conteúdo do e-mail: {response_conteudo.text}"}
            
        conteudo_data = response_conteudo.json()
        corpo_html = conteudo_data.get("data", {}).get("html", "")

        if not corpo_html:
             return {"sucesso": False, "erro": "O corpo do e-mail (html) veio vazio."}

        # PASSO 3: Extrair o código de verificação
        match = re.search(r'\b\d{4,8}\b', corpo_html)
        if match:
            codigo = match.group(0)
            return {"sucesso": True, "codigo": codigo}
        else:
            return {"sucesso": False, "erro": "Código de verificação não encontrado no corpo do e-mail."}

    except requests.exceptions.RequestException as e:
        return {"sucesso": False, "erro": f"Erro de conexão com a API: {e}"}
    except Exception as e:
        return {"sucesso": False, "erro": f"Ocorreu um erro inesperado: {e}"}

# Define a rota da API
@app.route('/get-code', methods=['POST'])
def get_code_route():
    data = request.get_json()
    if not data or 'email' not in data:
        return jsonify({"sucesso": False, "erro": "O campo 'email' é obrigatório."}), 400

    email = data['email']
    resultado = obter_codigo_do_email(mailbox=email)
    
    # Retorna o resultado como JSON
    if resultado['sucesso']:
        return jsonify(resultado), 200
    else:
        return jsonify(resultado), 500

# Executa o servidor quando o script é chamado
if __name__ == '__main__':
    app.run(debug=True)
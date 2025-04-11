import traceback
import subprocess
import sys
import webview
import threading
import requests
from flask import Flask, request, jsonify
import os
import json
from flask import send_from_directory
import re
import yaml
# --- Funções de execução ---

def obter_dados_arquivo(caminho):
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)

def escolher_modelo(caminho):
    return {"modelo": os.path.basename(caminho)}

def abrir_empresa(DadosEmpresa, ModeloDocumento):
    return {"empresa_criada": True, "documento_gerado": f"{ModeloDocumento['modelo']} para {DadosEmpresa.get('nome', 'empresa')}"}

funcoes_disponiveis = {
    "obter_dados_arquivo": obter_dados_arquivo,
    "escolher_modelo": escolher_modelo,
    "abrir_empresa": abrir_empresa,
}

# --- Utilitários ---

def gerar_estrutura_arquivos(root_path):
    estrutura = []

    def listar(caminho, indent=""):
        itens = sorted(os.listdir(caminho))
        for i, item in enumerate(itens):
            item_path = os.path.join(caminho, item)
            is_last = (i == len(itens) - 1)
            branch = "└── " if is_last else "├── "
            estrutura.append(f"{indent}{branch}{item}")
            if os.path.isdir(item_path):
                extender = "    " if is_last else "│   "
                listar(item_path, indent + extender)

    estrutura.append(os.path.basename(root_path.strip("/")) + "/")
    listar(root_path, "")
    return "\n".join(estrutura)

def construir_prompt(mensagem, estrutura_arquivos):
    return {
        "messages": [
            {
                "role": "system",
                "content": "Dado o contexto abaixo, gere uma intenção, uma pipeline e seus parâmetros de execução, usando formato ebnf com campos: mensagens, files_tree, status, intencao e pipeline."
            },
            {
                "role": "user",
                "content": f"""```ebnf
contexto:
  mensagens:
    - "{mensagem}"

  files_tree: \"\"\"
{estrutura_arquivos.strip()}
\"\"\"
```"""
            }
        ],
        "temperature": 0.2,
        "top_p": 1.0,
        "max_tokens": 1024,
        "stream": False
    }

def enviar_para_llama(prompt):
    response = requests.post(
        "http://localhost:8080/v1/chat/completions",
        headers={"Content-Type": "application/json"},
        data=json.dumps(prompt)
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def extrair_contexto_ebnf(resposta):
    match = re.search(r"```ebnf\n(.*?)```", resposta, re.DOTALL)
    if not match:
        raise Exception("Bloco EBNF não encontrado.")
    return yaml.safe_load(match.group(1))

def executar_pipeline(contexto):
    pipeline = contexto["pipeline"]
    memoria = {}

    for etapa in pipeline:
        funcao = etapa["função"]
        parametros = etapa["parâmetros"]

        for chave, valor in parametros.items():
            if isinstance(valor, dict) and not valor:
                if chave == "DadosEmpresa":
                    parametros[chave] = memoria.get("obter_dados_arquivo", {})
                elif chave == "ModeloDocumento":
                    parametros[chave] = memoria.get("escolher_modelo", {})

        func = funcoes_disponiveis.get(funcao)
        if not func:
            raise Exception(f"Função '{funcao}' não implementada.")
        resultado = func(**parametros)
        etapa["resultado"] = resultado
        memoria[funcao] = resultado

    return contexto

def start_llama_server():
    """Start the Llama server in a new console window."""
    try:
        subprocess.Popen(
            ['./llama/llama-server.exe', '-m', './models/gemma-3-4b-it-Q4_K_M.gguf'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("Llama server started successfully.")
    except Exception as e:
        print(f"Error starting Llama server: {e}")
        sys.exit(1)



app = Flask(__name__)




@app.route("/")
def servir_index():
    return send_from_directory("dist", "index.html")




@app.route('/v1/chat/completions', methods=['POST'])
def handle_chat():
    
    payload = request.json
    print("📥 Payload recebido:", payload)

    try:
        data = request.get_json()
        messages = data.get("messages", [])
        mensagem_usuario = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        root_path = data.get("root_path", "ambiente fictício\clientes")  # Caminho padrão opcional

        estrutura = gerar_estrutura_arquivos(root_path)
        prompt = construir_prompt(mensagem_usuario, estrutura)
        resposta_modelo = enviar_para_llama(prompt)
        contexto = extrair_contexto_ebnf(resposta_modelo)
        resultado = executar_pipeline(contexto)

        return jsonify({
            "contexto": contexto,
            "resultado": resultado
        })

    except Exception as e:
           
        traceback_str = traceback.format_exc()
        print("🚨 Erro no processamento:\n", traceback_str)
        return jsonify({"erro": str(e), "trace": traceback_str}), 500

def start_flask_server(): 
    thread = threading.Thread(target=lambda: app.run(port=5002, debug=False))
    thread.daemon = True
    thread.start()

if __name__ == '__main__':
    start_llama_server()

    start_flask_server()
    webview.create_window('dPacioli Junior', 'http://localhost:5002/', width=800, height=700, frameless=True)
    
    webview.start()

    input("Press Enter to continue...")  # Keeps the script running to maintain the processes.

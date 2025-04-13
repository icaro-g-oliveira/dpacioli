import traceback
import subprocess
import sys
import webview
import threading
import requests
import os
import json
from flask import send_from_directory, Flask, Response, request, jsonify
import time
import openai
import time
import yaml

LLAMA_SERVER_CONFIG = {
    "PORT": "8080",
    "MODEL_PATH" : "./models/gemma-3-1b-it-Q4_K_M.gguf"
}
FLASK_SERVER_CONFIG = {
    "PORT": 5002,
    "HOST": "127.0.0.1"
}

ROOT_PATH = "ambiente fictício/clientes"


def iniciar_llama_server():
    subprocess.Popen(
        ["./llama/llama-server.exe", "--port", LLAMA_SERVER_CONFIG.get("PORT"), "-m", LLAMA_SERVER_CONFIG.get("MODEL_PATH"), "--n-gpu-layers", "26"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

def esperar_disponibilidade(url, timeout=30):
    import requests
    for _ in range(timeout):
        try:
            if requests.get(url + "/v1/models").status_code == 200:
                return True
        except:
            pass
        time.sleep(1)
    raise TimeoutError("Servidor llama-server não respondeu a tempo.")

# Inicia o servidor em thread
llama_thread = threading.Thread(target=iniciar_llama_server)
llama_thread.daemon = True
llama_thread.start()

# Espera o server responder
esperar_disponibilidade(f"http://127.0.0.1:{LLAMA_SERVER_CONFIG.get('PORT')}")

# Configura o cliente OpenAI local
openai.api_key = "llama"  # dummy key
openai.base_url = f"http://127.0.0.1:{LLAMA_SERVER_CONFIG.get('PORT')}/v1"

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

def executar_pipeline(contexto):
    print("🧠 Contexto recebido para execução:\n", json.dumps(contexto, indent=2, ensure_ascii=False))

    pipeline = contexto.get("pipeline", [])
    status = contexto.setdefault("status", {})
    status["em_execucao"] = True
    status["realizado"] = False

    memoria = {}

    for etapa in pipeline:
        funcao = etapa.get("função")
        lista_parametros = etapa.get("parâmetros", [])

        parametros = {}
        for par in lista_parametros:
            if not isinstance(par, dict):
                raise ValueError(f"Parâmetro inválido na etapa '{funcao}': {par}")
            for chave, valor in par.items():
                if valor == {} or valor == []:
                    parametros[chave] = memoria.get(chave) or memoria.get(funcao) or {}
                else:
                    parametros[chave] = valor

        func = funcoes_disponiveis.get(funcao)
        if not func:
            raise Exception(f"Função '{funcao}' não implementada.")

        resultado = func(**parametros)
        etapa["resultado"] = [resultado]
        memoria[funcao] = resultado

    status["realizado"] = True
    status["em_execucao"] = False
    return contexto

def formatar_prompt_openai_like(mensagem_usuario: str) -> dict:
    return {
        "messages": [
            {"role": "user", "content": mensagem_usuario}
        ],
        "temperature": 0.2,
        "top_p": 1.0,
        "max_tokens": 1024
    }

def enviar_para_llama(mensagens):
    url = f"http://127.0.0.1:{LLAMA_SERVER_CONFIG.get('PORT')}/v1/chat/completions"
    payload = {
        "model": os.path.basename(LLAMA_SERVER_CONFIG["MODEL_PATH"]).replace(".gguf", ""),
        "messages": mensagens,
        "temperature": 0.2,
        "top_p": 1.0,
        "max_tokens": 1024
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print("❌ Erro ao consultar llama-server:", e)
        traceback.print_exc()
        return f"Erro ao consultar llama-server: {e}"

app = Flask(__name__)

@app.route("/")
def servir_index():
    return send_from_directory("dist", "index.html")

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    data = request.get_json()
    nova_mensagem = data["messages"][-1]["content"]
    CONTEXT_SESSION["messages"].append({"role": "user", "content": nova_mensagem})

    # 🔁 Envia mensagem para o modelo (com contexto atual)
    contexto_obj = {
        "contexto": {
            "mensagens": [msg["content"] for msg in CONTEXT_SESSION["messages"] if msg["role"] == "user"],
            "files_tree": CONTEXT_SESSION.get("files_tree", ""),
            "intencao": CONTEXT_SESSION.get("intencao", ""),
            "status": CONTEXT_SESSION.get("status", {"em_execucao": True, "realizado": False}),
            "pipeline": CONTEXT_SESSION.get("pipeline", [])
        }
    }

    resposta = enviar_para_llama([
            {"role": "system", "content": CONTEXT_SESSION["messages"][0]["content"]},
            {"role": "user", "content": json.dumps(contexto_obj, indent=2, ensure_ascii=False)}
        ])

    print(resposta)
    CONTEXT_SESSION["messages"].append({"role": "assistant", "content": resposta})
    print(jsonify(CONTEXT_SESSION))
    # 🔄 Parseia o retorno e executa etapa da pipeline se aplicável
    try:
        
        return jsonify({
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": ""
                }
            }]
        })

    except Exception as e:
        return jsonify({
            "error": {
                "message": f"Erro ao processar resposta do modelo: {str(e)}"
            }
        }), 500

def start_llama_server():
    llama_thread = threading.Thread(target=lambda:
        subprocess.Popen(
            ["./llama/llama-server.exe", "--port", LLAMA_SERVER_CONFIG.get("PORT"), "-m", "./models/gemma-3-4b-it-Q4_K_M.gguf"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    )
    llama_thread.daemon = True
    llama_thread.start()

def start_flask_server():
    print("🚀 Iniciando Flask em:", FLASK_SERVER_CONFIG)
    thread = threading.Thread(target=lambda: app.run(host=FLASK_SERVER_CONFIG.get("HOST"), port=FLASK_SERVER_CONFIG.get("PORT"), debug=False))
    thread.daemon = True
    thread.start()

def start_vite_dev_server():
    try:
        print("🌱 Starting npm run preview...")
        subprocess.Popen(
            ['./node/node.exe', './node_modules/vite/bin/vite.js', 'preview', '--', '--port', str(FLASK_SERVER_CONFIG.get("PORT"))],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except Exception as e:
        print(f"❌ Erro ao iniciar Vite: {e}")
        sys.exit(1)
        
CONTEXT_SESSION = {
    "messages": []  # lista com role: system, user, assistant
}

def inicializar_contexto(markdown_path: str):
    try:
        with open(markdown_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()

        CONTEXT_SESSION["messages"] = [
            {"role": "system", "content": system_prompt},
        ]

        print("🧠 Enviando system prompt ao modelo...")
        response = enviar_para_llama(CONTEXT_SESSION["messages"])
        print("✅ Modelo respondeu:", response)

    except Exception as e:
        print("❌ Erro ao inicializar contexto:", e)
        traceback.print_exc()
        
        
def esperar_modelo_estar_pronto(timeout=60, intervalo=2):
    inicio = time.time()
    while True:
        try:
            response = requests.post(
                f"http://127.0.0.1:{LLAMA_SERVER_CONFIG.get('PORT')}/v1/chat/completions",
                headers={"Content-Type": "application/json"},
                data=json.dumps({
                    "messages": [{"role": "user", "content": "status"}],
                    "temperature": 0.1,
                    "max_tokens": 5
                })
            )
            if response.status_code == 200:
                print("✅ Modelo carregado e pronto!")
                return True
        except Exception:
            pass

        if time.time() - inicio > timeout:
            print("⏰ Tempo esgotado aguardando o modelo.")
            return False

        print("⏳ Aguardando modelo carregar...")
        time.sleep(intervalo)
        
        
CONTEXT_SESSION["files_tree"] = gerar_estrutura_arquivos(ROOT_PATH)

if __name__ == '__main__':
    start_llama_server()
    start_flask_server()
    if esperar_modelo_estar_pronto():
        inicializar_contexto("./systemPrompt_simplificado.md")
    # start_vite_dev_server()  # Descomente se quiser rodar em modo preview de dev
    webview.create_window('dPacioli Junior', f"http://localhost:{FLASK_SERVER_CONFIG.get('PORT')}/", width=800, height=700, frameless=True)
    webview.start()
    input("Pressione Enter para finalizar...")

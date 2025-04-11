import subprocess
import sys
import webview
import threading
import requests
from flask import Flask, request, jsonify

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

""" TODO: decorar com @app.route("/") """
def start_npm_preview():
    """ TODO: 
            Substituir o corpo pelo serviço de dist/index.html
    """
    """Run 'npm run preview' to start the preview server."""
    try:
        print("Starting npm run preview...")
        subprocess.Popen(
            ['./node/node.exe', './node_modules/vite/bin/vite.js', 'preview'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("npm preview server started.")
    except Exception as e:
        print(f"Error starting npm preview: {e}")
        sys.exit(1)

def start_http_server_non_blocking():
    """Start the npm preview server in a non-blocking way."""
    npm_thread = threading.Thread(target=start_npm_preview)
    npm_thread.daemon = True  # Ensure the thread terminates when the main program ends
    npm_thread.start()
    print("npm preview server is running in the background.")

app = Flask(__name__)

@app.route('/v1/chat/completions', methods=['POST'])
def handle_chat():
    
    payload = request.json
    print("📥 Payload recebido:", payload)

    url = "http://localhost:8080/v1/chat/completions"
    
    """ 
        TODO: 
            Parse nesse payload em:
                ```ebnf
                contexto:
                    mensagens: [ ... ]
                ```
    """

    try:
        """ Dar request para o endereço da execução llama-server em start_llama_server: localhost:8080/v1/chat/completions"""
        resposta = requests.post(url, headers=headers, json=proxy_payload)
        resposta.raise_for_status()
        return jsonify(resposta.json())
    except requests.RequestException as e:
        print("❌ Erro na requisição ao llama-server:", e)
        return jsonify({"error": "Erro ao processar requisição no llama-server"}), 500

def start_flask_server(): 
    thread = threading.Thread(target=lambda: app.run(port=5002, debug=False))
    thread.daemon = True
    thread.start()

if __name__ == '__main__':
    start_llama_server()
    start_http_server_non_blocking()


    """ TODO: direcionar o webview para a porta 5002 do flask server"""
    start_flask_server()
    webview.create_window('dPacioli Junior', 'http://localhost:4173/', width=800, height=700, frameless=True)
    
    
    webview.start()

    input("Press Enter to continue...")  # Keeps the script running to maintain the processes.

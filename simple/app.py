from flask import Flask, request, jsonify
from modelo import inferir_funcao
import funcoes
import traceback

app = Flask(__name__)

@app.route("/v1/chat/completions", methods=["POST"])
def processar_mensagem():
    dados = request.json
    messages = dados.get("messages", [])
    
    if not messages:
        return jsonify({"error": "Campo 'messages' está vazio ou ausente."}), 400

    try:
        # Última mensagem do usuário como entrada principal
        ultima_mensagem = messages[-1]["content"]
        
        # Inferência de função e argumentos
        nome_funcao, argumentos = inferir_funcao(ultima_mensagem)
        
        # Executa a função dinamicamente
        funcao = getattr(funcoes, nome_funcao)
        resultado = funcao(**argumentos)

        # Resposta no formato OpenAI-style
        return jsonify({
            "id": "chatcmpl-local-001",
            "object": "chat.completion",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": "toolcall-001",
                                "type": "function",
                                "function": {
                                    "name": nome_funcao,
                                    "arguments": str(argumentos)
                                }
                            }
                        ]
                    },
                    "finish_reason": "tool_calls"
                }
            ],
            "executed_tool_result": resultado
        })

    except Exception as e:
        return jsonify({
            "error": str(e),
            "trace": traceback.format_exc()
        }), 500


if __name__ == "__main__":
    app.run(debug=True, port=8080)

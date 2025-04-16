from flask import Flask, request, jsonify
from lark import Lark
from core.ExecClasses import ExecTreeTransformer, executor_dag
from core.gramatica_dinamica import gerar_gramatica_mecanica
from modelo import inferir_, interpretar_para_gramatica
import funcoes
import traceback

def executar_(chamadas: list[tuple[str, dict]]) -> tuple[list[dict], list]:
    """
    Executa uma lista de chamadas de função do módulo 'funcoes'.

    Parameters:
        chamadas (list): Lista de tuplas (nome_funcao, argumentos).

    Returns:
        tuple: (tool_calls, resultados)
            - tool_calls: lista de dicionários estilo OpenAI
            - resultados: lista de resultados de execução
    """
    tool_calls = []
    resultados = []

    for i, (nome_funcao, argumentos) in enumerate(chamadas):
        funcao = getattr(funcoes, nome_funcao, None)
        if funcao is None:
            raise ValueError(f"Função '{nome_funcao}' não encontrada.")

        resultado = funcao(**argumentos)
        resultados.append(resultado)

        tool_calls.append({
            "id": f"toolcall-{i:03}",
            "type": "function",
            "function": {
                "name": nome_funcao,
                "arguments": str(argumentos)
            }
        })

    return tool_calls, resultados


app = Flask(__name__)

@app.route("/v1/chat/completions", methods=["POST"])
def processar_mensagem():
    dados = request.json
    messages = dados.get("messages", [])

    if not messages:
        return jsonify({"error": "Campo 'messages' está vazio ou ausente."}), 400

    try:
        ultima_mensagem = messages[-1]["content"]
        chamadas = processar_entrada_usuario(ultima_mensagem)
        tool_calls, resultados = executar_(chamadas)

        return jsonify({
            "id": "chatcmpl-local-001",
            "object": "chat.completion",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": tool_calls
                    },
                    "finish_reason": "tool_calls"
                }
            ],
            "executed_tool_result": resultados
        })

    except Exception as e:
        return jsonify({
            "error": str(e),
            "trace": traceback.format_exc()
        }), 500


gramatica = gerar_gramatica_mecanica()

print(gramatica)


def processar_entrada_usuario(mensagem_usuario: str):
    # 1. Gerar gramática com base nas funções disponíveis
    global gramatica

    # 2. Pedir ao modelo para estruturar a entrada natural segundo a gramática
    entrada_estruturada = interpretar_para_gramatica(mensagem_usuario, gramatica)

    print(f"🧠 Entrada estruturada: {entrada_estruturada}")

    # 3. Parsear com Lark
    parser = Lark(gramatica, start="start", parser="lalr")
    arvore = parser.parse(entrada_estruturada)

    # 4. Transformar em DAG de ExecNode
    transformer = ExecTreeTransformer()
    exec_nodes = transformer.transform(arvore)

    # 5. Executar encadeadamente
    executor_dag(exec_nodes, executor_basico)
    
    return [(node.funcao, node.argumentos) for node in exec_nodes]

def executor_basico(nome: str, args: dict):
    funcao = getattr(funcoes, nome)
    return funcao(**args)

if __name__ == "__main__":
    app.run(debug=True, port=8080)
    
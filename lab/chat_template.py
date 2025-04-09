from flask import Flask, request, jsonify
from flask_cors import CORS
from uuid import uuid4
import json
import inspect
from llama_cpp import Llama

app = Flask(__name__)
CORS(app)

# === Inicializar o modelo ===
llm = Llama(
    model_path="./models/Hermes-2-Pro-Llama-3-8B-Q4_K_M.gguf",
    chat_format="chatml-function-calling",
    n_ctx=8192,
    n_gpu_layers=-1,
    verbose=False
)

# === System prompt técnico ===
TECHNICAL_SYSTEM_PROMPT = ("""
Você é um modelo com capacidade de function calling.

Você pode usar ferramentas externas chamadas de funções sempre que necessário para responder com maior precisão.

Quando for apropriado, você deve chamar uma dessas funções diretamente utilizando o formato interno esperado.

Não inclua a resposta da função na sua mensagem.  
Apenas chame a função necessária com o nome correto e os argumentos apropriados.

Não invente funções nem parâmetros que não foram declarados.

Se nenhuma função for necessária, responda normalmente com texto.
""")

# === Registry dinâmico de ferramentas ===
tool_registry = {}

def _python_type_to_json(annotation):
    if annotation == int:
        return "integer"
    elif annotation == float:
        return "number"
    elif annotation == bool:
        return "boolean"
    elif annotation == list:
        return "array"
    elif annotation == dict:
        return "object"
    else:
        return "string"

def tool(description: str = ""):
    def decorator(func):
        sig = inspect.signature(func)
        props = {}
        required = []

        for name, param in sig.parameters.items():
            param_type = str(param.annotation.__name__) if param.annotation != inspect._empty else "string"
            props[name] = {
                "type": _python_type_to_json(param.annotation),
                "description": f"Parâmetro '{name}'"
            }
            if param.default == inspect.Parameter.empty:
                required.append(name)

        tool_schema = {
            "type": "function",
            "function": {
                "name": func.__name__,
                "description": description or func.__doc__ or f"Executa a função {func.__name__}",
                "parameters": {
                    "type": "object",
                    "properties": props,
                    "required": required
                }
            }
        }

        tool_registry[func.__name__] = {
            "func": func,
            "schema": tool_schema
        }

        return func
    return decorator

# === Exemplo de função registrada ===
@tool(description="Retorna a previsão do tempo para uma cidade específica.")
def obter_previsao_tempo(cidade: str):
    return f"Hoje em {cidade} está ensolarado com 25°C."

def executar_tool_call(tool_call):
    nome = tool_call["name"]
    args = tool_call["arguments"]
    entry = tool_registry.get(nome)
    if not entry:
        return f"Função '{nome}' não registrada."
    try:
        return entry["func"](**args)
    except Exception as e:
        return f"Erro ao executar '{nome}': {str(e)}"

# === Sessões de chat ===
chat_sessions = {}

@app.route("/v1/chat/completions", methods=["POST"])
def chat_completions():
    data = request.json
    session_id = data.get("session_id", "default")

    messages = data.get("messages", [])
    temperature = data.get("temperature", 0.7)
    top_p = data.get("top_p", 0.95)
    top_k = data.get("top_k", 40)
    max_tokens = data.get("max_tokens", 512)
    tool_choice = "auto"
    tools = [entry["schema"] for entry in tool_registry.values()]

    # Insere system prompt se necessário
    if not any(m["role"] == "system" for m in messages):
        messages.insert(0, {
            "role": "system",
            "content": TECHNICAL_SYSTEM_PROMPT
        })

    if session_id not in chat_sessions:
        chat_sessions[session_id] = []

    chat_sessions[session_id].extend(messages)

    print(chat_sessions)

    resposta = llm.create_chat_completion(
        messages=chat_sessions[session_id],
        tools=tools,
        tool_choice=tool_choice,
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
        max_tokens=max_tokens
    )

    resposta_msg = resposta["choices"][0]["message"]
    tool_calls = resposta_msg.get("tool_calls")

    if tool_calls:
        tool_call = tool_calls[0]
        tool_id = tool_call.get("id") or f"toolu_{uuid4().hex[:8]}"
        nome = tool_call["function"]["name"]
        args = json.loads(tool_call["function"]["arguments"])
        resultado = executar_tool_call({
            "name": nome,
            "arguments": args
        })

        chat_sessions[session_id].append({
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "id": tool_id,
                    "type": "function",
                    "function": {
                        "name": nome,
                        "arguments": json.dumps(args)
                    }
                }
            ]
        })

        chat_sessions[session_id].append({
            "role": "tool",
            "tool_call_id": tool_id,
            "content": resultado
        })

        resposta_final = llm.create_chat_completion(
            messages=chat_sessions[session_id],
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            max_tokens=max_tokens
        )

        return jsonify({
            "id": resposta_final["id"],
            "object": resposta_final["object"],
            "created": resposta_final["created"],
            "model": "Hermes-2-Pro",
            "choices": resposta_final["choices"],
            "usage": resposta_final.get("usage", {})
        })

    return jsonify({
        "id": resposta["id"],
        "object": resposta["object"],
        "created": resposta["created"],
        "model": "Hermes-2-Pro",
        "choices": resposta["choices"],
        "usage": resposta.get("usage", {})
    })

if __name__ == "__main__":
    app.run(port=8080)

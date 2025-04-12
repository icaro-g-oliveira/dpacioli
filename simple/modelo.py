from llama_cpp import Llama
from ferramentas import tools
import os
import json
from funcoes import mapear, caminho_relativo

BASE_DIR = os.getcwd()

# 🚀 Carrega o system_prompt base só uma vez
with open("system_prompt.md", "r", encoding="utf-8") as f:
    system_instrucoes = f.read()

llm = Llama(
    model_path="../models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
    chat_format="chatml-function-calling",
    n_ctx=4096,
    n_threads=8,
    n_gpu_layers=0,
    use_mlock=True,
    use_mmap=True
)


def gerar_arvore_de_arquivos(caminho: str) -> str:
    estrutura = []
    for raiz, pastas, arquivos in os.walk(caminho):
        if "__pycache__" in raiz:
            continue
        nivel = raiz.replace(caminho, '').count(os.sep)
        indent = '  ' * nivel
        estrutura.append(f"{indent}- {os.path.basename(raiz)}/")
        subindent = '  ' * (nivel + 1)
        for f in arquivos:
            if not f.endswith(".pyc"):
                estrutura.append(f"{subindent}- {f}")
    return "\n".join(estrutura)

def corrigir_args_alucinados(nome_funcao: str, args: dict) -> tuple[str, dict]:
    caminho = args.get("caminho", "")
    if "*" in caminho:
        caminho_base = caminho.split("*")[0].rstrip("/\\")
        caminho_abs = caminho_relativo(caminho_base)
        if not os.path.isdir(caminho_abs):
            raise FileNotFoundError(f"Pasta não encontrada: {caminho_base}")
        arquivos = [
            f for f in os.listdir(caminho_abs)
            if os.path.isfile(os.path.join(caminho_abs, f))
        ]
        lista = [{"caminho": os.path.join(caminho_base, f)} for f in arquivos]
        return "mapear", {
            "funcao": nome_funcao,
            "lista_de_argumentos": lista
        }
    return nome_funcao, args

def inferir_funcao(mensagem: str):
    # 🌳 Gera apenas a árvore no momento da chamada
    arvore = gerar_arvore_de_arquivos(BASE_DIR)

    # 🔧 Usa o system_prompt pré-carregado + árvore atual
    system_prompt = f"""
    Você interpreta comandos do usuário e gera chamadas de função.
    Quando o usuário mencionar ações sobre múltiplos arquivos, como 'todos os arquivos da pasta X',
    você deve utilizar a função `mapear`, mas apenas gerar:
    - o nome da função desejada\n
    - uma lista de pasta / arquivo.extensao
    \n\n📂 Estrutura de arquivos:\n\n{arvore}
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": mensagem}
    ]
    
    output = llm.create_chat_completion(
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    tool_calls = output["choices"][0]["message"]["tool_calls"]
    
    funcoes_corrigidas = []
    for call in tool_calls:
        nome = call["function"]["name"]
        args = json.loads(call["function"]["arguments"])
        nome_corrigido, args_corrigidos = corrigir_args_alucinados(nome, args)
        funcoes_corrigidas.append((nome_corrigido, args_corrigidos))

    return funcoes_corrigidas
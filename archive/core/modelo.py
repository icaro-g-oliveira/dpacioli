from llama_cpp import Llama
from open_ai_ferramentas import tools
import os
import json
from funcoes import caminho_relativo

BASE_DIR = os.getcwd()
EXECUTE_PROMPT_PATH = "executePrompt.md"

# 🚀 Carrega o system_prompt base só uma vez
with open(EXECUTE_PROMPT_PATH, "r", encoding="utf-8") as f:
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


def gerar_arvore_de_arquivos(caminho_base: str) -> str:
    estrutura = {}
    for raiz, _, arquivos in os.walk(caminho_base):
        if "__pycache__" in raiz:
            continue
        rel_path = os.path.relpath(raiz, caminho_base)
        estrutura[rel_path] = [f for f in arquivos if not f.endswith(".pyc")]

    linhas = []
    for pasta, arquivos in estrutura.items():
        if arquivos:
            linhas.append(f"📁 {pasta}/")
            linhas.append(f"- {', '.join(arquivos)}")
    return "\n".join(linhas)


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

def inferir_(mensagem: str):
    # 🌳 Gera apenas a árvore no momento da chamada
    arvore = gerar_arvore_de_arquivos(BASE_DIR)

    # 🔧 Usa o system_prompt pré-carregado + árvore atual
    system_prompt = system_prompt = f"""
        {system_instrucoes}
        📁 Estrutura de arquivos:
        {arvore}
        """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": mensagem}
    ]
    
    print(messages)
    
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



def interpretar_para_gramatica(mensagem: str, gramatica: str) -> str:
    prompt = f"""
    Você está interpretando comandos naturais do usuário e convertendo-os para a seguinte gramática formal:

    {gramatica}

    📎 Exemplo:
    Entrada: "quero apagar o arquivo contrato.txt"
    Saída: deletar(caminho="contrato.txt")

    Agora, interprete e converta:
    Entrada: "{mensagem}"
    Saída:
    """.strip()

    resposta = llm.create_chat_completion([
        {"role": "system", "content": prompt},
        {"role": "user", "content": mensagem}
    ])

    return resposta["choices"][0]["message"]["content"].strip()

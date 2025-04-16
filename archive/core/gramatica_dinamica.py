from lark import Lark, Transformer
from pathlib import Path
from modelo import llm
import inspect
import ast
import funcoes

def gerar_gramatica_via_llm_com_argumentos(caminho_funcoes: str = "funcoes.py") -> str:
    from pathlib import Path

    try:
        conteudo_funcoes = Path(caminho_funcoes).read_text(encoding="utf-8")
    except Exception as e:
        raise RuntimeError(f"Erro ao ler {caminho_funcoes}: {e}")

    prompt = f"""
    Você está criando uma gramática formal em EBNF para um interpretador de comandos de linguagem natural.

    Baseado nas funções Python listadas abaixo, extraia para cada função:
    1. O verbo de ação (primeira parte do nome da função, como 'copiar', 'adicionar', etc.)
    2. Os parâmetros (ex: origem, destino)

    Gere a gramática no estilo Lark para cada função assim:

    comando: "verbo" "(" param1=ESCAPED_STRING [, param2=ESCAPED_STRING, ...] ")"

    No final, liste todos os verbos únicos ordenados para a regra `acao`.

    ⚠️ Somente inclua funções definidas no arquivo, ignore auxiliares como `mapear`.

    Conteúdo do arquivo `funcoes.py`:

    ```python
    {conteudo_funcoes}
    ```
    """

    response = llm.create_chat_completion([
        {"role": "system", "content": prompt}
    ])
    
    print(response)

    return response["choices"][0]["message"]["content"].strip()


def gerar_gramatica_mecanica(funcoes_modulo=funcoes) -> str:
    import inspect

    acoes = set()

    for nome, func in inspect.getmembers(funcoes_modulo, inspect.isfunction):
        if nome.startswith("_") or nome == "mapear":
            continue
        verbo = nome.split("_")[0]
        acoes.add(verbo)

    acao_regra = "acao: " + " | ".join(f'"{a}"' for a in sorted(acoes))

    gramatica = f"""
start: comando ("e" comando)*

comando: acao "(" argumentos ")"
{acao_regra}

argumentos: ESCAPED_STRING ("," ESCAPED_STRING)*

%import common.ESCAPED_STRING
%import common.WS
%ignore WS
""".strip()

    return gramatica

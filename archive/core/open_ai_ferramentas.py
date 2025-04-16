import inspect
import funcoes

def gerar_tools_a_partir_de_modulo(modulo):
    tools = []

    for nome, func in inspect.getmembers(modulo, inspect.isfunction):
        sig = inspect.signature(func)
        doc = inspect.getdoc(func) or ""
        lines = doc.splitlines()

        descricao = lines[0].strip() if lines else ""

        parametros = {}
        for param in sig.parameters.values():
            tipo_python = param.annotation.__name__ if param.annotation != inspect.Parameter.empty else "str"

            # Mapeamento manual para JSON Schema
            TIPO_MAPA = {
                "str": "string",
                "int": "integer",
                "float": "number",
                "bool": "boolean",
                "list": "array",
                "dict": "object",
            }

            tipo = TIPO_MAPA.get(tipo_python, "string")
            parametros[param.name] = {
                "type": tipo.lower(),
                "description": _extrair_descricao_parametro(param.name, lines)
            }

        tools.append({
            "type": "function",
            "function": {
                "name": nome,
                "description": descricao,
                "parameters": {
                    "type": "object",
                    "properties": parametros,
                    "required": list(sig.parameters)
                }
            }
        })

    return tools

def _extrair_descricao_parametro(nome_param, linhas_doc):
    """
    Tenta extrair a descrição de um parâmetro com base na docstring estruturada.
    """
    for linha in linhas_doc:
        if nome_param in linha:
            return linha.split(":", 1)[-1].strip()
    return f"Parâmetro {nome_param}"



tools = gerar_tools_a_partir_de_modulo(funcoes)
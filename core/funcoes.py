import os
import shutil

BASE_DIR = os.getcwd()

def caminho_relativo(caminho: str) -> str:
    """
    Converte um caminho para um caminho absoluto relativo ao diretório atual.
    """
    return os.path.join(BASE_DIR, caminho.lstrip("/\\"))


def listar_arquivos(caminho: str) -> list[str]:
    """
    Lista os nomes de arquivos e pastas no caminho especificado.

    Parameters:
        caminho (str): Caminho relativo da pasta.

    Returns:
        list[str]: Lista dos nomes dos arquivos e pastas contidos na pasta.
    """
    caminho_absoluto = caminho_relativo(caminho)
    if not os.path.isdir(caminho_absoluto):
        raise FileNotFoundError(f"O caminho '{caminho}' não é uma pasta válida.")
    return os.listdir(caminho_absoluto)


def ler_arquivo(caminho: str) -> str:
    """
    Lê e retorna o conteúdo de um arquivo.

    Parameters:
        caminho (str): Caminho relativo do arquivo.

    Returns:
        str: Conteúdo do arquivo.
    """
    caminho_absoluto = caminho_relativo(caminho)
    if not os.path.isfile(caminho_absoluto):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")
    with open(caminho_absoluto, "r", encoding="utf-8") as f:
        return f.read()


def copiar_arquivo(origem: str, destino: str) -> str:
    """
    Copia um arquivo de origem para destino.

    Parameters:
        origem (str): Caminho do arquivo de origem.
        destino (str): Caminho do destino final.

    Returns:
        str: Confirmação da cópia.
    """
    origem_abs = caminho_relativo(origem)
    destino_abs = caminho_relativo(destino)
    if not os.path.isfile(origem_abs):
        raise FileNotFoundError(f"Arquivo de origem não encontrado: {origem}")
    os.makedirs(os.path.dirname(destino_abs), exist_ok=True)
    shutil.copy2(origem_abs, destino_abs)
    return f"Arquivo copiado de '{origem}' para '{destino}'."


def mover_arquivo(origem: str, destino: str) -> str:
    """
    Move um arquivo de um local para outro.

    Parameters:
        origem (str): Caminho atual do arquivo.
        destino (str): Caminho de destino.

    Returns:
        str: Confirmação da movimentação.
    """
    origem_abs = caminho_relativo(origem)
    destino_abs = caminho_relativo(destino)
    if not os.path.isfile(origem_abs):
        raise FileNotFoundError(f"Arquivo de origem não encontrado: {origem}")
    os.makedirs(os.path.dirname(destino_abs), exist_ok=True)
    shutil.move(origem_abs, destino_abs)
    return f"Arquivo movido de '{origem}' para '{destino}'."


def deletar_arquivo(caminho: str) -> str:
    """
    Remove um arquivo.

    Parameters:
        caminho (str): Caminho relativo do arquivo a ser deletado.

    Returns:
        str: Confirmação da exclusão.
    """
    caminho_absoluto = caminho_relativo(caminho)
    if not os.path.isfile(caminho_absoluto):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")
    os.remove(caminho_absoluto)
    return f"Arquivo '{caminho}' deletado com sucesso."

def criar_arquivo(caminho: str, conteudo: str = "") -> str:
    """
    Cria um arquivo com conteúdo opcional.

    Parameters:
        caminho (str): Caminho relativo do novo arquivo.
        conteudo (str): Conteúdo inicial do arquivo (opcional).

    Returns:
        str: Confirmação da criação.
    """
    caminho_abs = caminho_relativo(caminho)
    os.makedirs(os.path.dirname(caminho_abs), exist_ok=True)

    with open(caminho_abs, "w", encoding="utf-8") as f:
        f.write(conteudo)

    return f"Arquivo criado em '{caminho}' com {len(conteudo)} caracteres."

def escrever_arquivo(caminho: str, conteudo: str) -> str:
    """
    Escreve conteúdo em um arquivo, substituindo o conteúdo anterior.

    Parameters:
        caminho (str): Caminho relativo do arquivo a ser escrito.
        conteudo (str): Conteúdo a ser inserido no arquivo.

    Returns:
        str: Confirmação da escrita.
    """
    caminho_abs = caminho_relativo(caminho)
    os.makedirs(os.path.dirname(caminho_abs), exist_ok=True)

    with open(caminho_abs, "w", encoding="utf-8") as f:
        f.write(conteudo)

    return f"Arquivo '{caminho}' atualizado com sucesso."

def preencher_template(modelo: str, destino: str, dados: dict) -> str:
    """
    Gera um novo documento com base em um arquivo modelo, substituindo variáveis por dados fornecidos.

    Parameters:
        modelo (str): Caminho do arquivo modelo (com placeholders no formato {{variavel}}).
        destino (str): Caminho do novo arquivo a ser gerado.
        dados (dict): Dicionário de substituições {variavel: valor}.

    Returns:
        str: Caminho do novo arquivo gerado.
    """
    caminho_modelo = caminho_relativo(modelo)
    caminho_destino = caminho_relativo(destino)

    if not os.path.isfile(caminho_modelo):
        raise FileNotFoundError(f"Modelo não encontrado: {modelo}")

    with open(caminho_modelo, "r", encoding="utf-8") as f:
        conteudo = f.read()

    for chave, valor in dados.items():
        conteudo = conteudo.replace(f"{{{{{chave}}}}}", valor)

    os.makedirs(os.path.dirname(caminho_destino), exist_ok=True)
    with open(caminho_destino, "w", encoding="utf-8") as f:
        f.write(conteudo)

    return f"Documento gerado em '{destino}'."

def substituir_texto_arquivo(caminho: str, antigo: str, novo: str) -> str:
    """
    Substitui todas as ocorrências de um texto por outro em um arquivo.

    Parameters:
        caminho (str): Caminho relativo do arquivo.
        antigo (str): Texto a ser substituído.
        novo (str): Texto que substituirá o original.

    Returns:
        str: Confirmação da substituição.
    """
    caminho_abs = caminho_relativo(caminho)

    if not os.path.isfile(caminho_abs):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    with open(caminho_abs, "r", encoding="utf-8") as f:
        conteudo = f.read()

    conteudo_atualizado = conteudo.replace(antigo, novo)

    with open(caminho_abs, "w", encoding="utf-8") as f:
        f.write(conteudo_atualizado)

    return f"Texto '{antigo}' substituído por '{novo}' em '{caminho}'."

def adicionar_texto_arquivo(caminho: str, conteudo: str) -> str:
    """
    Adiciona conteúdo ao final de um arquivo existente.

    Parameters:
        caminho (str): Caminho relativo do arquivo.
        conteudo (str): Texto a ser adicionado.

    Returns:
        str: Confirmação da adição.
    """
    caminho_abs = caminho_relativo(caminho)

    os.makedirs(os.path.dirname(caminho_abs), exist_ok=True)
    with open(caminho_abs, "a", encoding="utf-8") as f:
        f.write("\n"+conteudo)

    return f"Texto adicionado ao final do arquivo '{caminho}'."

def remover_texto_arquivo(caminho: str, texto: str) -> str:
    """
    Remove todas as ocorrências de um texto de um arquivo.

    Parameters:
        caminho (str): Caminho relativo do arquivo.
        texto (str): Texto a ser removido.

    Returns:
        str: Confirmação da remoção.
    """
    caminho_abs = caminho_relativo(caminho)

    if not os.path.isfile(caminho_abs):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    with open(caminho_abs, "r", encoding="utf-8") as f:
        conteudo = f.read()

    conteudo_modificado = conteudo.replace(texto, "")

    with open(caminho_abs, "w", encoding="utf-8") as f:
        f.write(conteudo_modificado)

    return f"Texto '{texto}' removido de '{caminho}'."


def mapear(funcao, lista_de_argumentos: list[dict]) -> list:
    """
    Aplica uma função a cada conjunto de argumentos da lista.

    Parameters:
        funcao (function): Função que será aplicada.
        lista_de_argumentos (list[dict]): Lista de dicionários com argumentos.

    Returns:
        list: Lista de resultados da execução.
    """
    return [funcao(**args) for args in lista_de_argumentos]


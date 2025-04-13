from lark import Transformer, Tree, Token
from dataclasses import dataclass, field

@dataclass
class ExecNode:
    funcao: str
    argumentos: dict
    prioridade: int
    depende_de: list["ExecNode"] = field(default_factory=list)

    def __hash__(self):
        # para poder usar como chave em sets/grafos
        return hash((self.funcao, frozenset(self.argumentos.items()), self.prioridade))

class ExecTreeTransformer(Transformer): #DAG
    def __init__(self):
        self.nodes = []
        self.contador = 0

    def start(self, comandos):
        # encadeia cada comando como dependente do anterior
        for i in range(1, len(self.nodes)):
            self.nodes[i].depende_de.append(self.nodes[i-1])
        return self.nodes

    def comando(self, items):
        nome_funcao = items[0].value
        args = {}

        for token in items[1:]:
            if isinstance(token, Tree) and token.data == "argumento":
                k, v = token.children
                args[str(k)] = str(v).strip('"')

        node = ExecNode(
            funcao=nome_funcao,
            argumentos=args,
            prioridade=self.contador
        )
        self.contador += 1
        self.nodes.append(node)
        return node

    def argumento(self, items):
        return Tree("argumento", items)

    def ESCAPED_STRING(self, token):
        return token

    def acao(self, items):
        return items[0]

def executor_dag(nodes: list[ExecNode], executor: callable):
    executados = set()

    def executar_recursivo(no: ExecNode):
        for dep in no.depende_de:
            if dep not in executados:
                executar_recursivo(dep)
        resultado = executor(no.funcao, no.argumentos)
        print(f"[✔] Executado: {no.funcao} {no.argumentos}")
        executados.add(no)

    for no in nodes:
        if no not in executados:
            executar_recursivo(no)

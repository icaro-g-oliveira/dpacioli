import unittest
from lark import Lark
from gramatica_dinamica import gerar_gramatica_mecanica
from ExecClasses import ExecTreeTransformer
from modelo import interpretar_para_gramatica
import funcoes

from dataclasses import dataclass
from typing import List

@dataclass
class ExecNode:
    funcao: str
    argumentos: dict
    prioridade: int
    depende_de: List["ExecNode"]

class TestPipelineDeExecucao(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gramatica = gerar_gramatica_mecanica()
        cls.parser = Lark(cls.gramatica, start="start", parser="lalr")
        cls.transformador = ExecTreeTransformer()

    def test_pipeline_simples(self):
        entrada_usuario = 'quero criar um arquivo chamado exemplo.txt com "teste" dentro'

        entrada_estruturada = interpretar_para_gramatica(entrada_usuario, self.gramatica)
        arvore = self.parser.parse(entrada_estruturada)
        nodes = self.transformador.transform(arvore)

        self.assertGreater(len(nodes), 0)
        self.assertEqual(nodes[0].funcao, "criar_arquivo")
        self.assertIn("caminho", nodes[0].argumentos)

    def test_pipeline_encadeada(self):
        entrada_usuario = 'quero criar exemplo.txt com "abc" e depois ler o arquivo'

        entrada_estruturada = interpretar_para_gramatica(entrada_usuario, self.gramatica)
        arvore = self.parser.parse(entrada_estruturada)
        nodes = self.transformador.transform(arvore)

        self.assertEqual(len(nodes), 2)
        self.assertEqual(nodes[0].funcao, "criar_arquivo")
        self.assertEqual(nodes[1].funcao, "ler_arquivo")
        self.assertIn(nodes[0], nodes[1].depende_de)

    def test_execucao_fisica(self):
        entrada_usuario = 'criar arquivo de teste.txt com "isso é um teste" e depois ler'

        entrada_estruturada = interpretar_para_gramatica(entrada_usuario, self.gramatica)
        arvore = self.parser.parse(entrada_estruturada)
        nodes = self.transformador.transform(arvore)

        resultados = []
        for node in nodes:
            func = getattr(funcoes, node.funcao)
            resultado = func(**node.argumentos)
            resultados.append(resultado)

        self.assertTrue(any("teste" in r for r in resultados))

if __name__ == "__main__":
    unittest.main()

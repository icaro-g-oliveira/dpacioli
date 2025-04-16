import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../MIAgents/fundation")))

from sistema import Fluxo
from efeitos_e_retornos import FolhaProcessada, FolhaProtocolada

class Fluxo(Fluxo):
    δ_5: FolhaProcessada
    δ_6: FolhaProtocolada

import json
# Dados de entrada
entrada = {
    "α": 3,
    "β": 1,
    "γ": 0,
    "δ": "cliente enviou os documentos hoje e o prazo encerra amanhã",
    "δ_4": "gerar_folha",
    "δ_5": {
        "data_processamento": "2025-04-16T10:00:00",
        "observacoes": "Encargos calculados com base nos dados atuais"
    },
    "δ_6": {
        "sistema": "Sistema RH Central",
        "protocolo_id": "PRT-20250416-001",
        "data_protocolo": "2025-04-16T10:15:00",
        "responsavel": "Joana Silva"
    },
    "ζ": "libera a emissão das guias do INSS e FGTS"
}

# Criando instância do modelo
fluxo = Fluxo(**entrada)


# Print formatado e compatível com Pydantic v2 + JSON
print(json.dumps(fluxo.model_dump(), indent=2, ensure_ascii=False, default=str))

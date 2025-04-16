from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# Modelos customizados
class FolhaProcessada(BaseModel):
    evento: str = "folha processada"
    encargos_calculados: bool = True
    data_processamento: Optional[datetime] = None
    observacoes: Optional[str] = None


class FolhaProtocolada(BaseModel):
    evento: str = "folha protocolada"
    sistema: str
    protocolo_id: str
    data_protocolo: datetime
    responsavel: Optional[str] = None


# Modelo geral
class Fluxo(BaseModel):
    α: int
    β: int
    γ: int
    δ: str #A fazer expansão
    δ_4: str
    δ_5: FolhaProcessada
    δ_6: FolhaProtocolada
    ζ: str#A fazer expansão
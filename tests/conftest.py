import json
from types import SimpleNamespace

import pytest

from leitor_contratos.config import Config

CHAVE_FALSA = "sk-ant-teste-nao-e-uma-chave-real"

CONTRATO = (
    "CLÁUSULA 1. Em caso de cancelamento será cobrada multa de R$ 500,00.\n"
    "CLÁUSULA 2. O contrato será renovado automaticamente por 12 meses."
)


@pytest.fixture
def config() -> Config:
    return Config(api_key=CHAVE_FALSA, modelo="claude-haiku-5-5", max_tokens=1000, timeout=5, max_caracteres=10_000)


def analise_json(**alteracoes) -> str:
    dados = {
        "eh_contrato": True,
        "resumo": "Contrato de serviço.",
        "pontos_de_atencao": [
            {
                "risco": "alto",
                "titulo": "Multa",
                "trecho": "Em caso de cancelamento será cobrada multa de R$ 500,00.",
                "explicacao": "Sair custa R$ 500.",
            }
        ],
        "tentativas_de_manipulacao": [],
        "perguntas": ["A multa é proporcional?"],
    }
    dados.update(alteracoes)
    return json.dumps(dados, ensure_ascii=False)


def mensagem(texto: str = "", stop_reason: str = "end_turn") -> SimpleNamespace:
    blocos = [SimpleNamespace(type="thinking", thinking="")]
    if texto:
        blocos.append(SimpleNamespace(type="text", text=texto))
    return SimpleNamespace(stop_reason=stop_reason, content=blocos)


class ClienteSimulado:
    def __init__(self, resposta=None, erro: Exception | None = None):
        self.chamadas: list[dict] = []
        self._resposta = resposta
        self._erro = erro
        self.messages = self

    def create(self, **parametros):
        self.chamadas.append(parametros)
        if self._erro:
            raise self._erro
        return self._resposta

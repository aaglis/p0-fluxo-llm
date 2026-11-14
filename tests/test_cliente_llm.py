import anthropic
import httpx2
import pytest

from leitor_contratos import erros
from leitor_contratos.apresentacao import formatar_erro
from leitor_contratos.cliente_llm import solicitar_analise
from leitor_contratos.prompt import montar_solicitacao
from tests.conftest import CHAVE_FALSA, ClienteSimulado, mensagem

REQUISICAO = httpx2.Request("POST", "https://api.anthropic.com/v1/messages")


def erro_http(classe, status):
    resposta = httpx2.Response(status, request=REQUISICAO)
    return classe(f"erro {status} chave={CHAVE_FALSA}", response=resposta, body=None)


CASOS = [
    (erro_http(anthropic.AuthenticationError, 401), erros.CredencialInvalida),
    (erro_http(anthropic.PermissionDeniedError, 403), erros.CredencialInvalida),
    (erro_http(anthropic.NotFoundError, 404), erros.ConfiguracaoInvalida),
    (erro_http(anthropic.RateLimitError, 429), erros.ServicoIndisponivel),
    (erro_http(anthropic.InternalServerError, 500), erros.ServicoIndisponivel),
    (erro_http(anthropic.InternalServerError, 529), erros.ServicoIndisponivel),
    (anthropic.APITimeoutError(request=REQUISICAO), erros.TempoEsgotado),
    (anthropic.APIConnectionError(request=REQUISICAO), erros.FalhaComunicacao),
]


@pytest.mark.parametrize("erro_api,erro_esperado", CASOS)
def test_traduz_erros_da_api(config, erro_api, erro_esperado):
    cliente = ClienteSimulado(erro=erro_api)
    with pytest.raises(erro_esperado) as capturado:
        solicitar_analise(cliente, config, montar_solicitacao("contrato"))
    assert CHAVE_FALSA not in formatar_erro(capturado.value)


def test_envia_parametros_da_configuracao(config):
    cliente = ClienteSimulado(resposta=mensagem("{}"))
    solicitar_analise(cliente, config, montar_solicitacao("contrato"))
    chamada = cliente.chamadas[0]
    assert chamada["model"] == config.modelo
    assert chamada["max_tokens"] == config.max_tokens
    assert "output_config" in chamada

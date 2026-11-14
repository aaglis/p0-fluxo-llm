import pytest

from leitor_contratos.erros import RespostaInvalida
from leitor_contratos.resposta import extrair_analise, trecho_existe, verificar
from tests.conftest import CONTRATO, analise_json, mensagem


def test_resposta_valida():
    analise = extrair_analise(mensagem(analise_json()))
    assert analise.pontos_de_atencao[0].risco == "alto"


@pytest.mark.parametrize(
    "resposta",
    [
        mensagem(""),
        mensagem("isto não é json"),
        mensagem('{"resumo": "faltam campos"}'),
        mensagem(analise_json(), stop_reason="max_tokens"),
        mensagem(analise_json(), stop_reason="refusal"),
    ],
    ids=["vazia", "nao_json", "campos_faltando", "cortada", "recusa"],
)
def test_respostas_invalidas(resposta):
    with pytest.raises(RespostaInvalida):
        extrair_analise(resposta)


def test_trecho_tolera_espacos_aspas_e_maiusculas():
    assert trecho_existe("“EM CASO de cancelamento   será cobrada”", CONTRATO)


def test_trecho_inventado_e_sinalizado():
    analise = extrair_analise(mensagem(analise_json(pontos_de_atencao=[
        {"risco": "alto", "titulo": "Inventado", "trecho": "multa de R$ 9.999,00", "explicacao": "x"}
    ])))
    resultado = verificar(analise, CONTRATO)
    assert resultado.trechos_nao_encontrados == 1


def test_manipulacao_so_e_confirmada_se_existir_no_texto():
    analise = extrair_analise(mensagem(analise_json(
        tentativas_de_manipulacao=["renovado automaticamente", "frase que não existe"]
    )))
    assert verificar(analise, CONTRATO).manipulacoes_confirmadas == ["renovado automaticamente"]

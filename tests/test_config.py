import pytest

from leitor_contratos.config import MODELO_PADRAO, carregar_config
from leitor_contratos.erros import ConfiguracaoInvalida, CredencialAusente
from tests.conftest import CHAVE_FALSA


def test_credencial_ausente():
    with pytest.raises(CredencialAusente):
        carregar_config({})


def test_credencial_com_valor_de_exemplo_conta_como_ausente():
    with pytest.raises(CredencialAusente):
        carregar_config({"ANTHROPIC_API_KEY": "coloque-sua-chave-aqui"})


def test_valores_padrao():
    config = carregar_config({"ANTHROPIC_API_KEY": CHAVE_FALSA})
    assert config.modelo == MODELO_PADRAO
    assert config.max_tokens > 0


@pytest.mark.parametrize("nome,valor", [
        ("MAX_TOKENS", "abc"),
        ("MAX_TOKENS", "0"),
        ("TIMEOUT_SEGUNDOS", "-1"),
        ("TIMEOUT_SEGUNDOS", "0"),
        ("MAX_TENTATIVAS", "-1"),
        ("ESFORCO", "altissimo"),
        ("LOG_NIVEL", "barulhento"),
    ])
def test_configuracao_invalida(nome, valor):
    with pytest.raises(ConfiguracaoInvalida):
        carregar_config({"ANTHROPIC_API_KEY": CHAVE_FALSA, nome: valor})


def test_chave_nao_aparece_na_representacao():
    assert CHAVE_FALSA not in repr(carregar_config({"ANTHROPIC_API_KEY": CHAVE_FALSA}))


def test_parametros_lidos_do_ambiente():
    config = carregar_config({
        "ANTHROPIC_API_KEY": CHAVE_FALSA,
        "ANTHROPIC_MODEL": "claude-sonnet-5-5",
        "MAX_TOKENS": "2000",
        "TIMEOUT_SEGUNDOS": "30.5",
        "MAX_TENTATIVAS": "0",
        "ESFORCO": "HIGH",
        "LOG_NIVEL": "debug",
        "LOG_ARQUIVO": "",
    })
    assert (config.modelo, config.max_tokens, config.timeout) == ("claude-sonnet-5-5", 2000, 30.5)
    assert (config.max_tentativas, config.esforco, config.nivel_log, config.arquivo_log) == (0, "high", "DEBUG", "")

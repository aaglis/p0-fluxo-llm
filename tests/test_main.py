import anthropic
import httpx2

import main
from tests.conftest import CHAVE_FALSA, ClienteSimulado, analise_json, mensagem


def executar_com(monkeypatch, capsys, tmp_path, cliente=None, chave=CHAVE_FALSA):
    contrato = tmp_path / "contrato.txt"
    contrato.write_text("Em caso de cancelamento será cobrada multa de R$ 500,00.", encoding="utf-8")
    monkeypatch.setenv("ANTHROPIC_API_KEY", chave)
    if cliente:
        monkeypatch.setattr(main, "criar_cliente", lambda config: cliente)
    codigo = main.executar([str(contrato)])
    return codigo, capsys.readouterr()


def test_fluxo_completo_simulado(monkeypatch, capsys, tmp_path):
    codigo, saida = executar_com(monkeypatch, capsys, tmp_path, ClienteSimulado(resposta=mensagem(analise_json())))
    assert codigo == 0
    assert "[ALTO] Multa" in saida.out


def test_credencial_ausente(monkeypatch, capsys, tmp_path):
    codigo, saida = executar_com(monkeypatch, capsys, tmp_path, chave="")
    assert codigo == 1
    assert "chave de acesso ao Claude não foi configurada" in saida.err
    assert "Traceback" not in saida.err


def test_credencial_invalida_sem_expor_a_chave(monkeypatch, capsys, tmp_path):
    requisicao = httpx2.Request("POST", "https://api.anthropic.com/v1/messages")
    erro = anthropic.AuthenticationError(
        f"invalid x-api-key {CHAVE_FALSA}", response=httpx2.Response(401, request=requisicao), body=None
    )
    codigo, saida = executar_com(monkeypatch, capsys, tmp_path, ClienteSimulado(erro=erro))
    assert codigo == 1
    assert "recusada" in saida.err
    assert CHAVE_FALSA not in saida.err + saida.out

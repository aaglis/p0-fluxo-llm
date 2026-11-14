import os
import subprocess
import sys
from pathlib import Path

import anthropic
import httpx2

import main
from tests.conftest import CHAVE_FALSA, ClienteSimulado, analise_json, mensagem


TEXTO_CONTRATO = "Em caso de cancelamento será cobrada multa de R$ 500,00."


def executar_com(monkeypatch, capsys, tmp_path, cliente=None, chave=CHAVE_FALSA):
    contrato = tmp_path / "contrato.txt"
    contrato.write_text(TEXTO_CONTRATO, encoding="utf-8")
    monkeypatch.setenv("ANTHROPIC_API_KEY", chave)
    monkeypatch.setenv("LOG_ARQUIVO", str(tmp_path / "execucao.log"))
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


def test_registro_nao_guarda_chave_nem_conteudo(monkeypatch, capsys, tmp_path):
    codigo, _ = executar_com(monkeypatch, capsys, tmp_path, ClienteSimulado(resposta=mensagem(analise_json())))
    registro = (tmp_path / "execucao.log").read_text(encoding="utf-8")
    assert codigo == 0
    assert "Execução concluída com sucesso" in registro
    assert CHAVE_FALSA not in registro
    assert TEXTO_CONTRATO not in registro
    assert "multa" not in registro.lower()


def test_registro_de_erro_nao_guarda_chave(monkeypatch, capsys, tmp_path):
    requisicao = httpx2.Request("POST", "https://api.anthropic.com/v1/messages")
    erro = anthropic.AuthenticationError(
        f"invalid x-api-key {CHAVE_FALSA}", response=httpx2.Response(401, request=requisicao), body=None
    )
    executar_com(monkeypatch, capsys, tmp_path, ClienteSimulado(erro=erro))
    registro = (tmp_path / "execucao.log").read_text(encoding="utf-8")
    assert "AuthenticationError status=401" in registro
    assert CHAVE_FALSA not in registro


def test_modo_verboso_mostra_registros_no_terminal(monkeypatch, capsys, tmp_path):
    contrato = tmp_path / "contrato.txt"
    contrato.write_text(TEXTO_CONTRATO, encoding="utf-8")
    monkeypatch.setenv("ANTHROPIC_API_KEY", CHAVE_FALSA)
    monkeypatch.setenv("LOG_ARQUIVO", "")
    monkeypatch.setattr(main, "criar_cliente", lambda config: ClienteSimulado(resposta=mensagem(analise_json())))
    assert main.executar(["--verbose", str(contrato)]) == 0
    assert "Enviando solicitação" in capsys.readouterr().err


def test_terminal_sem_chave_mostra_apenas_a_mensagem(tmp_path):
    raiz = Path(__file__).resolve().parent.parent
    ambiente = {**os.environ, "ANTHROPIC_API_KEY": "", "LOG_ARQUIVO": ""}
    processo = subprocess.run(
        [sys.executable, str(raiz / "main.py"), "contrato.txt"],
        cwd=tmp_path, env=ambiente, capture_output=True, text=True, timeout=60,
    )
    assert processo.returncode == 1
    assert processo.stderr.strip().splitlines()[0] == "Erro: A chave de acesso ao Claude não foi configurada."
    assert "Execução encerrada" not in processo.stderr

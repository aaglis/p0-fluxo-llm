from leitor_contratos.apresentacao import formatar_relatorio, sanitizar
from leitor_contratos.resposta import extrair_analise, verificar
from tests.conftest import CONTRATO, analise_json, mensagem


def resultado(**alteracoes):
    return verificar(extrair_analise(mensagem(analise_json(**alteracoes))), CONTRATO)


def test_remove_sequencias_de_controle_do_terminal():
    assert sanitizar("\x1b[2Jtexto\x07‮") == "[2Jtexto"


def test_relatorio_confirma_trechos_conferidos():
    assert "Todos os trechos citados foram conferidos" in formatar_relatorio(resultado())


def test_relatorio_avisa_trecho_nao_encontrado():
    pontos = [{"risco": "baixo", "titulo": "X", "trecho": "não existe", "explicacao": "y"}]
    assert "NÃO encontrado" in formatar_relatorio(resultado(pontos_de_atencao=pontos))


def test_relatorio_ordena_por_risco():
    pontos = [
        {"risco": "baixo", "titulo": "B", "trecho": "renovado", "explicacao": "y"},
        {"risco": "alto", "titulo": "A", "trecho": "multa", "explicacao": "y"},
    ]
    texto = formatar_relatorio(resultado(pontos_de_atencao=pontos))
    assert texto.index("[ALTO] A") < texto.index("[BAIXO] B")


def test_texto_que_nao_e_contrato():
    texto = formatar_relatorio(resultado(eh_contrato=False, pontos_de_atencao=[], perguntas=[]))
    assert "PONTOS DE ATENÇÃO" not in texto

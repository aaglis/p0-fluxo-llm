import pytest

from leitor_contratos.entrada import ler_texto, preparar_texto
from leitor_contratos.erros import EntradaInvalida


@pytest.mark.parametrize("texto", ["", "   \n\t  ", "​​"])
def test_entrada_vazia_e_bloqueada(texto):
    with pytest.raises(EntradaInvalida):
        preparar_texto(texto, 1000)


def test_entrada_acima_do_limite():
    with pytest.raises(EntradaInvalida):
        preparar_texto("a" * 11, 10)


def test_remove_caracteres_ocultos():
    preparado = preparar_texto("mul​ta‮ de R$ 500\x1b", 1000)
    assert preparado.texto == "multa de R$ 500"
    assert preparado.caracteres_ocultos_removidos == 3


def test_arquivo_inexistente(tmp_path):
    with pytest.raises(EntradaInvalida):
        ler_texto([str(tmp_path / "nao_existe.txt")])


def test_arquivo_nao_utf8(tmp_path):
    arquivo = tmp_path / "contrato.txt"
    arquivo.write_bytes(b"\xff\xfe\x00multa")
    with pytest.raises(EntradaInvalida):
        ler_texto([str(arquivo)])

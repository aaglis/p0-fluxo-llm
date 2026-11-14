import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO

from .erros import EntradaInvalida

PERMITIDOS = {"\n", "\t"}


@dataclass(frozen=True)
class TextoPreparado:
    texto: str
    caracteres_ocultos_removidos: int


def ler_texto(argumentos: list[str], stdin: TextIO = sys.stdin) -> str:
    if argumentos:
        return _ler_arquivo(Path(argumentos[0]))

    if stdin.isatty():
        print(
            "Cole o texto do contrato e pressione Ctrl+D (Ctrl+Z e Enter no Windows) para finalizar:\n",
            file=sys.stderr,
        )
    return stdin.read()


def _ler_arquivo(caminho: Path) -> str:
    if not caminho.exists():
        raise EntradaInvalida(f"O arquivo '{caminho}' não foi encontrado.", dica="Confira o caminho informado.")
    if not caminho.is_file():
        raise EntradaInvalida(f"'{caminho}' não é um arquivo.")
    try:
        return caminho.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raise EntradaInvalida(
            f"Não foi possível ler '{caminho}' como texto UTF-8.",
            dica="Converta o contrato para .txt (UTF-8) antes de analisar.",
        )
    except OSError as erro:
        raise EntradaInvalida(f"Não foi possível abrir '{caminho}': {erro.strerror}.")


def _eh_oculto(caractere: str) -> bool:
    if caractere in PERMITIDOS:
        return False
    return unicodedata.category(caractere) in {"Cf", "Cc"}


def preparar_texto(bruto: str, max_caracteres: int) -> TextoPreparado:
    texto = bruto.replace("\r\n", "\n").replace("\r", "\n")
    limpo = "".join(c for c in texto if not _eh_oculto(c))
    removidos = len(texto) - len(limpo)
    limpo = limpo.strip()

    if not limpo:
        raise EntradaInvalida(
            "Nenhum texto foi recebido.",
            dica="Informe o caminho de um arquivo ou cole o contrato no terminal.",
        )
    if len(limpo) > max_caracteres:
        raise EntradaInvalida(
            f"O texto tem {len(limpo)} caracteres e o limite configurado é {max_caracteres}.",
            dica="Analise o contrato em partes ou ajuste MAX_CARACTERES no .env.",
        )
    return TextoPreparado(texto=limpo, caracteres_ocultos_removidos=removidos)

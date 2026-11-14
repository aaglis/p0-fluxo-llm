import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from analisador import analisar_contrato


def ler_entrada(argumentos: list[str]) -> str:
    if argumentos:
        return Path(argumentos[0]).read_text(encoding="utf-8")

    if sys.stdin.isatty():
        print("Cole o texto do contrato e pressione Ctrl+D (Ctrl+Z e Enter no Windows) para finalizar:\n")
    return sys.stdin.read()


def main() -> int:
    load_dotenv()

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY não encontrada. Copie .env.example para .env e informe sua chave.", file=sys.stderr)
        return 1

    texto = ler_entrada(sys.argv[1:]).strip()
    if not texto:
        print("Nenhum texto recebido. Informe um arquivo ou cole o contrato.", file=sys.stderr)
        return 1

    print("\nAnalisando o contrato, aguarde...\n", file=sys.stderr)
    relatorio = analisar_contrato(texto)
    print(relatorio)
    return 0


if __name__ == "__main__":
    sys.exit(main())

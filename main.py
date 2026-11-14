import argparse
import logging
import sys

from dotenv import load_dotenv

from leitor_contratos.apresentacao import formatar_erro, formatar_relatorio
from leitor_contratos.cliente_llm import criar_cliente, solicitar_analise
from leitor_contratos.config import carregar_config
from leitor_contratos.entrada import ler_texto, preparar_texto
from leitor_contratos.erros import ErroAplicacao
from leitor_contratos.prompt import montar_solicitacao
from leitor_contratos.registro import configurar_registro
from leitor_contratos.resposta import extrair_analise, verificar

logger = logging.getLogger("leitor_contratos.main")


def ler_argumentos(argumentos: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="Aponta as cláusulas de risco de um contrato, em português simples.",
    )
    parser.add_argument("arquivo", nargs="?", help="arquivo .txt com o contrato (sem ele, o texto é lido do terminal)")
    parser.add_argument("-v", "--verbose", action="store_true", help="mostra os registros da execução no terminal")
    return parser.parse_args(argumentos)


def executar(argumentos: list[str]) -> int:
    opcoes = ler_argumentos(argumentos)
    try:
        config = carregar_config()
        configurar_registro(config, opcoes.verbose)
        logger.info("Execução iniciada")

        preparado = preparar_texto(ler_texto([opcoes.arquivo] if opcoes.arquivo else []), config.max_caracteres)
        solicitacao = montar_solicitacao(preparado.texto)

        print("Analisando o contrato, aguarde...\n", file=sys.stderr)
        resposta = solicitar_analise(criar_cliente(config), config, solicitacao)

        resultado = verificar(extrair_analise(resposta), solicitacao.texto_enviado)
        print(formatar_relatorio(resultado, preparado.caracteres_ocultos_removidos))
        logger.info("Execução concluída com sucesso")
        return 0
    except ErroAplicacao as erro:
        logger.warning("Execução encerrada com erro: %s", type(erro).__name__)
        print(formatar_erro(erro), file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        logger.info("Execução cancelada pelo usuário")
        print("\nOperação cancelada.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    load_dotenv()
    sys.exit(executar(sys.argv[1:]))

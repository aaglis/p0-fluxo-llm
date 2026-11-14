import sys

from dotenv import load_dotenv

from leitor_contratos.apresentacao import formatar_erro, formatar_relatorio
from leitor_contratos.cliente_llm import criar_cliente, solicitar_analise
from leitor_contratos.config import carregar_config
from leitor_contratos.entrada import ler_texto, preparar_texto
from leitor_contratos.erros import ErroAplicacao
from leitor_contratos.prompt import montar_solicitacao
from leitor_contratos.resposta import extrair_analise, verificar


def executar(argumentos: list[str]) -> int:
    try:
        config = carregar_config()
        preparado = preparar_texto(ler_texto(argumentos), config.max_caracteres)
        solicitacao = montar_solicitacao(preparado.texto)

        print("Analisando o contrato, aguarde...\n", file=sys.stderr)
        resposta = solicitar_analise(criar_cliente(config), config, solicitacao)

        resultado = verificar(extrair_analise(resposta), solicitacao.texto_enviado)
        print(formatar_relatorio(resultado, preparado.caracteres_ocultos_removidos))
        return 0
    except ErroAplicacao as erro:
        print(formatar_erro(erro), file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nOperação cancelada.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    load_dotenv()
    sys.exit(executar(sys.argv[1:]))

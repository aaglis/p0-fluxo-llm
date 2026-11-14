import textwrap
import unicodedata

from .erros import ErroAplicacao
from .resposta import Resultado

ROTULOS = {"alto": "ALTO", "medio": "MÉDIO", "baixo": "BAIXO"}
LARGURA = 90
AVISO_FINAL = "Este relatório não substitui a orientação de um advogado."


def sanitizar(texto: str) -> str:
    return "".join(c for c in texto if c == "\n" or unicodedata.category(c) not in {"Cc", "Cf"})


def _paragrafo(texto: str, recuo: str = "") -> str:
    return textwrap.fill(sanitizar(texto), width=LARGURA, initial_indent=recuo, subsequent_indent=recuo)


def formatar_relatorio(resultado: Resultado, caracteres_ocultos: int = 0) -> str:
    analise = resultado.analise
    linhas: list[str] = []

    if caracteres_ocultos:
        linhas += [
            f"[!] Foram removidos {caracteres_ocultos} caracteres invisíveis do texto. "
            "Eles podem esconder conteúdo; confira o documento original.",
            "",
        ]

    linhas += ["RESUMO", _paragrafo(analise.resumo), ""]

    if not analise.eh_contrato:
        return "\n".join(linhas + [AVISO_FINAL])

    if resultado.manipulacoes_confirmadas:
        linhas.append("[!] ALERTA: o contrato contém texto que tenta manipular a análise automática:")
        linhas += [_paragrafo(f'"{t}"', "    ") for t in resultado.manipulacoes_confirmadas]
        linhas.append("")

    linhas.append(f"PONTOS DE ATENÇÃO ({len(resultado.pontos)})")
    for item in resultado.pontos:
        ponto = item.ponto
        linhas.append("")
        linhas.append(f"[{ROTULOS[ponto.risco]}] {sanitizar(ponto.titulo)}")
        rotulo = "Trecho" if item.trecho_encontrado else "Trecho (NÃO encontrado no contrato, confira)"
        linhas.append(_paragrafo(f'{rotulo}: "{ponto.trecho}"', "    "))
        linhas.append(_paragrafo(f"O que significa: {ponto.explicacao}", "    "))

    if analise.perguntas:
        linhas += ["", "PERGUNTE ANTES DE ASSINAR"]
        linhas += [_paragrafo(f"{i}. {p}", "  ") for i, p in enumerate(analise.perguntas, start=1)]

    linhas.append("")
    if resultado.trechos_nao_encontrados:
        linhas.append(
            f"[!] {resultado.trechos_nao_encontrados} trecho(s) citado(s) não foram encontrados literalmente "
            "no contrato. Confira-os no documento original."
        )
    else:
        linhas.append("Todos os trechos citados foram conferidos no texto do contrato.")
    linhas.append(AVISO_FINAL)
    return "\n".join(linhas)


def formatar_erro(erro: ErroAplicacao) -> str:
    mensagem = f"Erro: {erro.mensagem}"
    return f"{mensagem}\n{erro.dica}" if erro.dica else mensagem

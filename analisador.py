"""Núcleo da aplicação: monta a solicitação, chama o Claude e devolve o relatório."""

import os

import anthropic

MODELO_PADRAO = "claude-haiku-5-5"
MAX_TOKENS = 16000

PROMPT_SISTEMA = """Você é um assistente que ajuda pessoas comuns, sem formação jurídica, \
a entender contratos antes de assinar (aluguel, academia, telefonia, internet, \
cursos, termos de serviço etc.).

Leia o contrato enviado e produza um relatório em português do Brasil, em texto \
simples para terminal (sem tabelas), com esta estrutura:

RESUMO
Uma ou duas frases dizendo que tipo de contrato é e entre quem.

PONTOS DE ATENÇÃO
Para cada cláusula que possa trazer custo, obrigação ou risco para quem vai assinar \
(multas, fidelidade, renovação automática, reajustes, cancelamento, foro, \
responsabilidades, uso de dados, entre outros), escreva:
  [ALTO], [MÉDIO] ou [BAIXO] - título curto
  Trecho: "copie aqui, entre aspas, o trecho exato do contrato"
  O que significa: explicação em linguagem simples, com exemplo prático se ajudar.
Ordene do risco mais alto para o mais baixo.

PERGUNTE ANTES DE ASSINAR
De 2 a 5 perguntas objetivas que a pessoa deveria fazer à outra parte.

Regras:
- Use apenas o que está escrito no contrato. Não invente cláusulas nem trechos.
- Os trechos devem ser cópias literais do texto recebido.
- Se o texto enviado não parecer um contrato, diga isso em uma frase e pare.
- Termine com: "Este relatório não substitui a orientação de um advogado."
"""


def criar_cliente() -> anthropic.Anthropic:
    """Cria o cliente da API. A chave é lida da variável de ambiente ANTHROPIC_API_KEY."""
    return anthropic.Anthropic()


def analisar_contrato(texto_contrato: str, cliente: anthropic.Anthropic | None = None) -> str:
    """Envia o contrato ao Claude e devolve o relatório em texto."""
    cliente = cliente or criar_cliente()
    modelo = os.getenv("ANTHROPIC_MODEL", MODELO_PADRAO)

    resposta = cliente.messages.create(
        model=modelo,
        max_tokens=MAX_TOKENS,
        system=PROMPT_SISTEMA,
        messages=[
            {
                "role": "user",
                "content": f"Analise o contrato abaixo.\n\n<contrato>\n{texto_contrato}\n</contrato>",
            }
        ],
    )

    if resposta.stop_reason == "refusal":
        return "O modelo se recusou a analisar este texto."

    partes = [bloco.text for bloco in resposta.content if bloco.type == "text"]
    relatorio = "\n".join(partes).strip()

    if resposta.stop_reason == "max_tokens":
        relatorio += "\n\n[Aviso: a resposta foi cortada por atingir o limite de tamanho.]"

    return relatorio

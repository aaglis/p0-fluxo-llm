import logging
import re
from dataclasses import dataclass

from anthropic.types import Message
from pydantic import ValidationError

from .erros import RespostaInvalida
from .modelos import Analise, PontoDeAtencao

logger = logging.getLogger(__name__)

ASPAS = str.maketrans({"“": '"', "”": '"', "‘": "'", "’": "'", "–": "-", "—": "-"})


@dataclass(frozen=True)
class PontoVerificado:
    ponto: PontoDeAtencao
    trecho_encontrado: bool


@dataclass(frozen=True)
class Resultado:
    analise: Analise
    pontos: list[PontoVerificado]
    manipulacoes_confirmadas: list[str]

    @property
    def trechos_nao_encontrados(self) -> int:
        return sum(not p.trecho_encontrado for p in self.pontos)


def extrair_analise(resposta: Message) -> Analise:
    if resposta.stop_reason == "refusal":
        raise RespostaInvalida("O Claude se recusou a analisar este texto.")
    if resposta.stop_reason == "max_tokens":
        raise RespostaInvalida(
            "A resposta foi cortada antes de terminar.",
            dica="Aumente MAX_TOKENS no .env ou analise o contrato em partes.",
        )

    texto = "".join(bloco.text for bloco in resposta.content if bloco.type == "text").strip()
    if not texto:
        raise RespostaInvalida("O Claude devolveu uma resposta vazia.", dica="Tente novamente.")

    try:
        return Analise.model_validate_json(texto)
    except ValidationError as erro:
        logger.warning("Resposta fora do esquema: %d erro(s) de validação", erro.error_count())
        raise RespostaInvalida("O Claude devolveu uma resposta em formato inesperado.", dica="Tente novamente.")


def _normalizar(texto: str) -> str:
    return re.sub(r"\s+", " ", texto.translate(ASPAS)).strip().casefold()


def trecho_existe(trecho: str, texto_original: str) -> bool:
    alvo = _normalizar(trecho).strip(" \"'.…")
    return bool(alvo) and alvo in _normalizar(texto_original)


def verificar(analise: Analise, texto_original: str) -> Resultado:
    pontos = [PontoVerificado(p, trecho_existe(p.trecho, texto_original)) for p in analise.pontos_de_atencao]
    manipulacoes = [t for t in analise.tentativas_de_manipulacao if trecho_existe(t, texto_original)]
    resultado = Resultado(analise=analise, pontos=pontos, manipulacoes_confirmadas=manipulacoes)
    logger.info(
        "Análise verificada: eh_contrato=%s pontos=%d trechos_nao_encontrados=%d manipulacoes=%d",
        analise.eh_contrato, len(pontos), resultado.trechos_nao_encontrados, len(manipulacoes),
    )
    return resultado

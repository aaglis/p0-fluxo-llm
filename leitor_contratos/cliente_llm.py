import logging
import time

import anthropic
from anthropic.types import Message

from .config import Config
from .erros import (
    ConfiguracaoInvalida,
    CredencialInvalida,
    ErroAplicacao,
    FalhaComunicacao,
    RespostaInvalida,
    ServicoIndisponivel,
    TempoEsgotado,
)
from .prompt import Solicitacao

logger = logging.getLogger(__name__)


def criar_cliente(config: Config) -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=config.api_key, timeout=config.timeout, max_retries=config.max_tentativas)


def solicitar_analise(cliente: anthropic.Anthropic, config: Config, solicitacao: Solicitacao) -> Message:
    logger.info(
        "Enviando solicitação: modelo=%s max_tokens=%d esforco=%s timeout=%gs tentativas=%d",
        config.modelo, config.max_tokens, config.esforco, config.timeout, config.max_tentativas,
    )
    inicio = time.monotonic()
    try:
        resposta = cliente.messages.create(
            model=config.modelo,
            max_tokens=config.max_tokens,
            system=solicitacao.system,
            messages=solicitacao.messages,
            output_config={**solicitacao.output_config, "effort": config.esforco},
        )
    except anthropic.APIError as erro:
        logger.warning(
            "Falha na chamada após %.1fs: %s status=%s request_id=%s",
            time.monotonic() - inicio, type(erro).__name__,
            getattr(erro, "status_code", "-"), getattr(erro, "request_id", None) or "-",
        )
        raise traduzir_erro(erro, config) from None

    uso = getattr(resposta, "usage", None)
    logger.info(
        "Resposta recebida em %.1fs: stop_reason=%s tokens_entrada=%s tokens_saida=%s request_id=%s",
        time.monotonic() - inicio, resposta.stop_reason,
        getattr(uso, "input_tokens", "-"), getattr(uso, "output_tokens", "-"),
        getattr(resposta, "_request_id", None) or "-",
    )
    return resposta


def traduzir_erro(erro: anthropic.APIError, config: Config) -> ErroAplicacao:
    if isinstance(erro, anthropic.AuthenticationError):
        return CredencialInvalida(
            "A chave de acesso foi recusada pelo Claude.",
            dica="Confira ANTHROPIC_API_KEY no .env ou gere uma nova chave no console da Anthropic.",
        )
    if isinstance(erro, anthropic.PermissionDeniedError):
        return CredencialInvalida(
            "A chave informada não tem permissão para usar este serviço.",
            dica="Verifique as permissões e os créditos da conta no console da Anthropic.",
        )
    if isinstance(erro, anthropic.NotFoundError):
        return ConfiguracaoInvalida(f"O modelo '{config.modelo}' não foi encontrado.", dica="Confira ANTHROPIC_MODEL no .env.")
    if isinstance(erro, anthropic.RateLimitError):
        return ServicoIndisponivel("O limite de requisições da conta foi atingido.", dica="Aguarde alguns instantes e tente novamente.")
    if isinstance(erro, anthropic.BadRequestError):
        return RespostaInvalida(
            "O Claude recusou a solicitação por considerá-la inválida.",
            dica="O texto pode ser grande demais, ou algum parâmetro do .env não é aceito por este modelo.",
        )
    if isinstance(erro, anthropic.InternalServerError):
        return ServicoIndisponivel(
            "O serviço do Claude está indisponível ou sobrecarregado no momento.", dica="Tente novamente em alguns minutos."
        )
    if isinstance(erro, anthropic.APIStatusError):
        return ServicoIndisponivel(f"O Claude respondeu com um erro inesperado (código {erro.status_code}).")
    if isinstance(erro, anthropic.APITimeoutError):
        return TempoEsgotado(
            f"O Claude não respondeu em {config.timeout:g} segundos.",
            dica="Tente novamente ou aumente TIMEOUT_SEGUNDOS no .env.",
        )
    if isinstance(erro, anthropic.APIConnectionError):
        return FalhaComunicacao("Não foi possível conectar ao Claude.", dica="Verifique sua conexão com a internet.")
    return FalhaComunicacao("Ocorreu uma falha inesperada na comunicação com o Claude.")

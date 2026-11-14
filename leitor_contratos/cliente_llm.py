import anthropic
from anthropic.types import Message

from .config import Config
from .erros import (
    ConfiguracaoInvalida,
    CredencialInvalida,
    FalhaComunicacao,
    RespostaInvalida,
    ServicoIndisponivel,
    TempoEsgotado,
)
from .prompt import Solicitacao


def criar_cliente(config: Config) -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=config.api_key, timeout=config.timeout, max_retries=config.max_tentativas)


def solicitar_analise(cliente: anthropic.Anthropic, config: Config, solicitacao: Solicitacao) -> Message:
    try:
        return cliente.messages.create(
            model=config.modelo,
            max_tokens=config.max_tokens,
            system=solicitacao.system,
            messages=solicitacao.messages,
            output_config={**solicitacao.output_config, "effort": config.esforco},
        )
    except anthropic.AuthenticationError:
        raise CredencialInvalida(
            "A chave de acesso foi recusada pelo Claude.",
            dica="Confira ANTHROPIC_API_KEY no .env ou gere uma nova chave no console da Anthropic.",
        )
    except anthropic.PermissionDeniedError:
        raise CredencialInvalida(
            "A chave informada não tem permissão para usar este serviço.",
            dica="Verifique as permissões e os créditos da conta no console da Anthropic.",
        )
    except anthropic.NotFoundError:
        raise ConfiguracaoInvalida(
            f"O modelo '{config.modelo}' não foi encontrado.",
            dica="Confira ANTHROPIC_MODEL no .env.",
        )
    except anthropic.RateLimitError:
        raise ServicoIndisponivel(
            "O limite de requisições da conta foi atingido.",
            dica="Aguarde alguns instantes e tente novamente.",
        )
    except anthropic.BadRequestError:
        raise RespostaInvalida(
            "O Claude recusou a solicitação por considerá-la inválida.",
            dica="O texto pode ser grande demais. Reduza o contrato ou confira MAX_TOKENS no .env.",
        )
    except anthropic.InternalServerError:
        raise ServicoIndisponivel(
            "O serviço do Claude está indisponível ou sobrecarregado no momento.",
            dica="Tente novamente em alguns minutos.",
        )
    except anthropic.APIStatusError as erro:
        raise ServicoIndisponivel(f"O Claude respondeu com um erro inesperado (código {erro.status_code}).")
    except anthropic.APITimeoutError:
        raise TempoEsgotado(
            f"O Claude não respondeu em {config.timeout:g} segundos.",
            dica="Tente novamente ou aumente TIMEOUT_SEGUNDOS no .env.",
        )
    except anthropic.APIConnectionError:
        raise FalhaComunicacao(
            "Não foi possível conectar ao Claude.",
            dica="Verifique sua conexão com a internet.",
        )

import os
from collections.abc import Mapping
from dataclasses import dataclass, field

from .erros import ConfiguracaoInvalida, CredencialAusente

MODELO_PADRAO = "claude-haiku-5-5"
MAX_TOKENS_PADRAO = 16000
TIMEOUT_PADRAO = 120.0
MAX_CARACTERES_PADRAO = 100_000
MAX_TENTATIVAS_PADRAO = 2
ESFORCO_PADRAO = "medium"
ESFORCOS_VALIDOS = ("low", "medium", "high", "xhigh", "max")
NIVEL_LOG_PADRAO = "INFO"
NIVEIS_LOG_VALIDOS = ("DEBUG", "INFO", "WARNING", "ERROR")
ARQUIVO_LOG_PADRAO = "logs/leitor_contratos.log"

VALOR_DE_EXEMPLO = "coloque-sua-chave-aqui"


@dataclass(frozen=True)
class Config:
    api_key: str = field(repr=False)
    modelo: str = MODELO_PADRAO
    max_tokens: int = MAX_TOKENS_PADRAO
    timeout: float = TIMEOUT_PADRAO
    max_caracteres: int = MAX_CARACTERES_PADRAO
    max_tentativas: int = MAX_TENTATIVAS_PADRAO
    esforco: str = ESFORCO_PADRAO
    nivel_log: str = NIVEL_LOG_PADRAO
    arquivo_log: str = ARQUIVO_LOG_PADRAO


def _ler_numero(env: Mapping[str, str], nome: str, padrao, tipo, minimo):
    bruto = env.get(nome, "").strip()
    if not bruto:
        return padrao
    try:
        valor = tipo(bruto)
    except ValueError:
        raise ConfiguracaoInvalida(f"{nome} deve ser um número (valor atual: {bruto!r}).")
    if valor < minimo:
        raise ConfiguracaoInvalida(f"{nome} deve ser no mínimo {minimo} (valor atual: {bruto}).")
    if tipo is float and valor == 0:
        raise ConfiguracaoInvalida(f"{nome} deve ser maior que zero.")
    return valor


def _ler_opcao(env: Mapping[str, str], nome: str, padrao: str, opcoes: tuple[str, ...], maiusculas=False) -> str:
    bruto = env.get(nome, "").strip()
    if not bruto:
        return padrao
    valor = bruto.upper() if maiusculas else bruto.lower()
    if valor not in opcoes:
        raise ConfiguracaoInvalida(f"{nome} deve ser um destes valores: {', '.join(opcoes)} (valor atual: {bruto!r}).")
    return valor


def carregar_config(env: Mapping[str, str] | None = None) -> Config:
    env = os.environ if env is None else env

    api_key = env.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key or api_key == VALOR_DE_EXEMPLO:
        raise CredencialAusente(
            "A chave de acesso ao Claude não foi configurada.",
            dica="Copie .env.example para .env e preencha ANTHROPIC_API_KEY com a sua chave.",
        )

    return Config(
        api_key=api_key,
        modelo=env.get("ANTHROPIC_MODEL", "").strip() or MODELO_PADRAO,
        max_tokens=_ler_numero(env, "MAX_TOKENS", MAX_TOKENS_PADRAO, int, 1),
        timeout=_ler_numero(env, "TIMEOUT_SEGUNDOS", TIMEOUT_PADRAO, float, 0),
        max_caracteres=_ler_numero(env, "MAX_CARACTERES", MAX_CARACTERES_PADRAO, int, 1),
        max_tentativas=_ler_numero(env, "MAX_TENTATIVAS", MAX_TENTATIVAS_PADRAO, int, 0),
        esforco=_ler_opcao(env, "ESFORCO", ESFORCO_PADRAO, ESFORCOS_VALIDOS),
        nivel_log=_ler_opcao(env, "LOG_NIVEL", NIVEL_LOG_PADRAO, NIVEIS_LOG_VALIDOS, maiusculas=True),
        arquivo_log=env.get("LOG_ARQUIVO", ARQUIVO_LOG_PADRAO).strip(),
    )

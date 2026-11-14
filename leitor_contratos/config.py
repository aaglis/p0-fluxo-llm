import os
from collections.abc import Mapping
from dataclasses import dataclass, field

from .erros import ConfiguracaoInvalida, CredencialAusente

MODELO_PADRAO = "claude-haiku-5-5"
MAX_TOKENS_PADRAO = 16000
TIMEOUT_PADRAO = 120.0
MAX_CARACTERES_PADRAO = 100_000

VALOR_DE_EXEMPLO = "coloque-sua-chave-aqui"


@dataclass(frozen=True)
class Config:
    api_key: str = field(repr=False)
    modelo: str
    max_tokens: int
    timeout: float
    max_caracteres: int


def _ler_inteiro(env: Mapping[str, str], nome: str, padrao: int) -> int:
    bruto = env.get(nome, "").strip()
    if not bruto:
        return padrao
    try:
        valor = int(bruto)
    except ValueError:
        raise ConfiguracaoInvalida(f"{nome} deve ser um número inteiro (valor atual: {bruto!r}).")
    if valor <= 0:
        raise ConfiguracaoInvalida(f"{nome} deve ser maior que zero (valor atual: {valor}).")
    return valor


def _ler_decimal(env: Mapping[str, str], nome: str, padrao: float) -> float:
    bruto = env.get(nome, "").strip()
    if not bruto:
        return padrao
    try:
        valor = float(bruto)
    except ValueError:
        raise ConfiguracaoInvalida(f"{nome} deve ser um número (valor atual: {bruto!r}).")
    if valor <= 0:
        raise ConfiguracaoInvalida(f"{nome} deve ser maior que zero (valor atual: {valor}).")
    return valor


def carregar_config(env: Mapping[str, str] | None = None) -> Config:
    env = os.environ if env is None else env

    api_key = env.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key or api_key == VALOR_DE_EXEMPLO:
        raise CredencialAusente(
            "A chave de acesso ao Claude não foi configurada.",
            dica="Copie .env.example para .env e preencha ANTHROPIC_API_KEY com a sua chave.",
        )

    modelo = env.get("ANTHROPIC_MODEL", "").strip() or MODELO_PADRAO

    return Config(
        api_key=api_key,
        modelo=modelo,
        max_tokens=_ler_inteiro(env, "MAX_TOKENS", MAX_TOKENS_PADRAO),
        timeout=_ler_decimal(env, "TIMEOUT_SEGUNDOS", TIMEOUT_PADRAO),
        max_caracteres=_ler_inteiro(env, "MAX_CARACTERES", MAX_CARACTERES_PADRAO),
    )

import logging
import sys
from pathlib import Path

from .config import Config

FORMATO = "%(asctime)s %(levelname)s %(name)s: %(message)s"


def configurar_registro(config: Config, verboso: bool = False) -> logging.Logger:
    logger = logging.getLogger("leitor_contratos")
    logger.setLevel(config.nivel_log)
    logger.propagate = False
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()

    formatador = logging.Formatter(FORMATO)

    if config.arquivo_log:
        caminho = Path(config.arquivo_log)
        caminho.parent.mkdir(parents=True, exist_ok=True)
        arquivo = logging.FileHandler(caminho, encoding="utf-8")
        arquivo.setFormatter(formatador)
        logger.addHandler(arquivo)

    if verboso:
        console = logging.StreamHandler(sys.stderr)
        console.setFormatter(formatador)
        logger.addHandler(console)

    if not logger.handlers:
        logger.addHandler(logging.NullHandler())
    return logger

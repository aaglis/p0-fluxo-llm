class ErroAplicacao(Exception):
    def __init__(self, mensagem: str, dica: str = ""):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.dica = dica


class EntradaInvalida(ErroAplicacao):
    pass


class ConfiguracaoInvalida(ErroAplicacao):
    pass


class CredencialAusente(ErroAplicacao):
    pass


class CredencialInvalida(ErroAplicacao):
    pass


class ServicoIndisponivel(ErroAplicacao):
    pass


class FalhaComunicacao(ErroAplicacao):
    pass


class TempoEsgotado(ErroAplicacao):
    pass


class RespostaInvalida(ErroAplicacao):
    pass

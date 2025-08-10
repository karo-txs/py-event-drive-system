class DomainError(Exception):
    """Erro base do domínio."""
    pass


class InvalidStatus(DomainError):
    """Status inválido para entidade."""
    pass

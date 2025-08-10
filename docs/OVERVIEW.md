# Arquitetura e Decisões

- **Hexagonal/Clean Architecture**: Separação clara entre domínio, aplicação, infraestrutura e interfaces.
- **Entradas**: Lambda handler (`app/interfaces/lambda/handler.py`) e FastAPI (`app/interfaces/http/main.py`).
- **Mensageria**: Porta MessageBus, adapters para SQS e RabbitMQ.
- **Persistência**: Porta Repository, adapter Postgres (SQLAlchemy async).
- **Configuração**: `.env` e 12-factor.
- **Observabilidade**: structlog, OpenTelemetry (flag).
- **Testes**: pytest, fixtures, cobertura.
- **Scripts**: automação local cross-platform.
- **Docker**: Compose para Postgres, RabbitMQ, LocalStack (opcional).

Veja `/docs/prompts/` para prompts de evolução.

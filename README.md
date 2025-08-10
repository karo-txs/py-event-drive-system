# dev-event-driven-system

Microserviço Python 3.12, arquitetura hexagonal, orientado a eventos, pronto para AWS Lambda e FastAPI.

## Como rodar local

```sh
make venv
cp .env.example .env
```

## Subir dependências e app com Docker Compose

```sh
make compose-up
```

Acesse o app em http://localhost:8000


## Parar containers

```sh
make compose:-down
```

## Testar endpoints

### Health check
```sh
curl http://localhost:8000/health
```

### Process event
```sh
curl -X POST http://localhost:8000/process -H "Content-Type: application/json" -d '{"id": "abc", "name": "Test"}'
```

## Outras instruções
- Para rodar testes: `make tests`
- Para logs: veja saída do container ou terminal
- Para acessar RabbitMQ: http://localhost:15672 (guest/guest)
- Para acessar Postgres: localhost:5432 (user/password)

Mais detalhes em `/docs/OVERVIEW.md`.
# Prompt: Checklist de saúde

**Quando usar:**
- Antes de PR, release ou deploy.

**O que fornecer:**
- Nada (rodar checklist).

**Passos para o Copilot:**
1. Rodar lint, testes, coverage.
2. Subir compose.
3. Testar endpoints /health e /process.
4. Simular evento (SQS, RabbitMQ).
5. Conferir logs estruturados.

**Saídas esperadas:**
- Relatório de saúde do projeto.

**Critérios de aceite:**
- Lint, testes e coverage ok.
- Endpoints respondem.
- Logs no padrão JSON.

**Exemplo de comando:**
```
make lint
make tests
make coverage
make compose-up
curl http://localhost:8000/health
```

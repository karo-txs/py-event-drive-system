# Prompt: Conectar entidade ao banco

**Quando usar:**
- Para persistir entidade no banco relacional.

**O que fornecer:**
- Schema da tabela, índices, chaves, constraints.

**Passos para o Copilot:**
1. Gerar/atualizar model SQLAlchemy em `/app/infrastructure/persistence/models.py`.
2. Gerar/atualizar repository.
3. Gerar migration (ou instrução manual).
4. Gerar teste de integração CRUD.

**Saídas esperadas:**
- Model, repository, migration (ou instrução SQL), teste integração.

**Critérios de aceite:**
- CRUD funciona.
- Teste integração passa.

**Exemplo de comando:**
```
make tests
```

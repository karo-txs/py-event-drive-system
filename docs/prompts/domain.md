# Prompt: Gerar/alterar entidades e regras

**Quando usar:**
- Para criar ou modificar entidades de domínio, value objects ou regras de negócio.

**O que fornecer:**
- Descrição das novas entidades, atributos, relacionamentos e invariantes.

**Passos para o Copilot:**
1. Gerar/alterar arquivos em `/app/domain` (entities, value objects, regras).
2. Atualizar/exibir testes unitários em `/tests/unit`.

**Saídas esperadas:**
- Arquivos Python em `/app/domain`.
- Testes unitários cobrindo as regras.

**Critérios de aceite:**
- Código roda sem erros.
- Testes unitários cobrem cenários principais.

**Exemplo de comando:**
```
make tests
```

# Prompt: Consumir/produzir evento

**Quando usar:**
- Para consumir ou publicar eventos em fila/mensageria.

**O que fornecer:**
- Payload do evento, regras de roteamento, idempotência.

**Passos para o Copilot:**
1. Gerar/atualizar handler ou publisher.
2. Atualizar MessageBus/adapters.
3. Gerar/exibir testes (unitário/integrado).

**Saídas esperadas:**
- Handler/publisher, testes.

**Critérios de aceite:**
- Evento processado corretamente.
- Teste cobre consumo/publicação.

**Exemplo de comando:**
```
make tests
```

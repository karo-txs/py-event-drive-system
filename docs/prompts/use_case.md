# Prompt: Adicionar um novo caso de uso

**Quando usar:**
- Para criar um novo caso de uso de negócio (service/application layer).

**O que fornecer:**
- Nome do use case, inputs/outputs esperados, eventos publicados.

**Passos para o Copilot:**
1. Criar classe em `/app/application/use_cases/`.
2. Gerar/atualizar DTOs em `/app/application/dtos.py`.
3. Gerar/exibir testes unitários para o use case.

**Saídas esperadas:**
- Novo arquivo de use case.
- DTOs atualizados.
- Testes unitários.

**Critérios de aceite:**
- Testes passam.
- Lógica cobre cenários informados.

**Exemplo de comando:**
```
make tests
```

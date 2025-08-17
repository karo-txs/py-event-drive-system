# PROMPT — Implementar/Expandir Domínio (Hexagonal, imutável onde fizer sentido)

> **Contexto fixo do projeto**
>
> * Linguagem: Python 3.12
> * Arquitetura: Clean/Hexagonal (Domain puro, sem dependências de infraestrutura)
> * Template existente (NÃO MUDE caminhos nem nomes-base sem instrução):
>
>   * `app/domain/entities.py` (já contém `Status` e `Item`)
>   * `app/domain/errors.py` (já contém `DomainError`, `InvalidStatus`)
> * Estilo: `dataclasses` imutáveis (`frozen=True`) para Entidades/Value Objects quando fizer sentido; sem import de ORM, HTTP ou libs de infra.
> * Idioma dos nomes de código: **inglês** (ex.: `Order`, `Customer`, `Status`). Docstrings em **português**.
> * **Objetivo** desta tarefa: adicionar/editar entidades, value objects, regras/invariantes e erros de domínio **conforme o problema do usuário**, mantendo o domínio **puro, testável e autocontido**.

---

## 1) Campos a preencher pelo usuário (cole abaixo do título ao acionar o Copilot)

Preencha **TUDO** entre `{{ }}`. Se algo não existir, use `null` ou remova com justificativa.

```
# DOMAIN_SPEC

## Contexto do Negócio
- Domínio/resumo: {{ex.: “processamento de pedidos e pagamentos”}}
- Termos onipresentes (ubiquitous language): {{ex.: Order, Payment, Invoice, Customer}}

## Entidades (com atributos, tipos e se são obrigatórios)
- {{EntityName}}:
  - atributos:
    - {{field_name}}: {{type}} {{required? true/false}} {{observations/invariantes}}
    - ...
  - identidade: {{ex.: order_id (str/UUID)}}
  - relacionamentos: {{ex.: Order has many OrderItem}}
- {{OutraEntidade}}:
  - ...

## Value Objects
- {{VOName}}: {{campos e regras (ex.: Money com currency, amount>=0)}}
- {{OutroVO}}: ...

## Invariantes/Políticas (SEM falar de banco, fila ou API)
- {{ex.: “Order só pode mudar para PAID se total > 0 e payment_confirmed=true”}}
- {{ex.: “SKU é sempre upper-case; quantidade mínima 1; desconto ≤ 30%”}}

## Eventos de Domínio (se existirem)
- {{EventName}}: {{quando dispara, payload mínimo (apenas IDs/VOs)}}

## Regras de Estado (máquinas de estado)
- {{ex.: Status: created → confirmed → paid → fulfilled → closed; transições proibidas: ...}}

## Erros de Domínio (nomes e mensagens)
- {{ex.: InvalidOrderState, NegativeQuantity, CurrencyMismatch}}

## Compatibilidade com o template atual
- Manter `Item` e `Status`? {{keep/remove/rename}} (se remover/renomear, explicar por quê)
```

---

## 2) Escopo e restrições que o Copilot deve seguir

* **NÃO** adicione dependências externas no domínio.
* **NÃO** acople domínio a SQLAlchemy, httpx, boto, etc.
* **NÃO** mova nem renomeie `app/domain/errors.py` e `app/domain/entities.py` sem instrução explícita do campo “Compatibilidade”.
* Se “Compatibilidade”=”keep”, preserve `Item`/`Status` existentes e **adicione** novas entidades/VOs lado a lado.
* Use `@dataclass(frozen=True)` para Entidades/VOs sempre que possível.
* **Validações** em `__post_init__` ou construtores de VO.
* Erros específicos devem **herdar** de `DomainError`.
* **Sem I/O** (arquivos, rede) no domínio.
* **Cobertura** de testes do domínio ≥ **90%** para novos artefatos.

---

## 3) Saídas esperadas (arquivos e mudanças)

Crie/edite **somente** estes caminhos:

* `app/domain/entities.py`

  * Adicionar novas **Entidades** e **Value Objects** conforme `DOMAIN_SPEC`.
  * Se especificado, estender `Status` ou criar novo state machine como VO (ex.: `OrderStatus`).
  * Implementar **invariantes** no `__post_init__` e/ou métodos puros que retornem **novas instâncias** (estilo funcional) para mudanças de estado.

* `app/domain/errors.py`

  * Adicionar **novas exceções** específicas solicitadas (ex.: `InvalidOrderState(DomainError)`).
  * Mensagens claras e curtas.

* `tests/unit/domain/test_entities.py` (criar/editar)

  * Testes de construção feliz (happy path) e de falhas (erros).
  * Testes de invariantes, máquinas de estado e value objects.
  * Testes **parametrizados** quando fizer sentido.

> **Formato da resposta do Copilot:**
>
> 1. *Resumo das decisões* (bullet points)
> 2. **Diffs unificados** para `entities.py` e `errors.py` (se editados)
> 3. **Conteúdo completo** do novo arquivo de teste `tests/unit/domain/test_entities.py`
> 4. *Checklist de verificação* (comandos para rodar os testes)

---

## 4) Passo a passo que o Copilot deve executar

1. **Ler** o bloco `DOMAIN_SPEC` e montar um **modelo conceitual**: entidades, VOs, relacionamentos, estados e invariantes.
2. **Projetar** as entidades como `@dataclass(frozen=True)` com **tipagem forte** (`from __future__ import annotations` se usar tipos recursivos).
3. Para **Value Objects**, fornecer **validações** (ex.: normalizar `Currency` para ISO, validar `Email`, `Money.amount >= 0`).
4. Implementar **regras de negócio** como métodos **puros** que retornam **novas instâncias** (ex.: `with_status(new_status)`), **nunca** mutando estado.
5. Transições de **máquina de estado**: encapsule numa classe VO (ex.: `OrderStatus`) com conjunto de transições válidas e método `transition(to)`.
6. **Erros**: criar subclasses de `DomainError` para cada política violada com mensagens sucintas.
7. Escrever **testes** cobrindo: construção válida/ inválida; invariantes; transições válidas/ inválidas; igualdade/ordenação (se aplicável) de VOs.
8. Rodar mentalmente os testes para evitar dependência de infraestrutura. Se precisar de dados fake, crie **helpers** dentro do teste.

---

## 5) Regras de codificação (domínio)

* `dataclasses` + `frozen=True`.
* Tipos: `str`, `int`, `Decimal`, `UUID`, `datetime`, VOs próprios (evite `Any`).
* **Sem** print/log no domínio.
* Métodos devem ser **determinísticos** e **Idempotentes** quando apropriado.
* Implementar `__eq__`/`__hash__` **apenas** se necessário; `dataclass(frozen=True)` já ajuda.
* Documentar em docstrings **o porquê** da regra, não o óbvio.
* Mensagens de erro direcionadas ao **desenvolvedor**, não ao usuário final.

---

## 6) Exemplo de saída (mini‑modelo ilustrativo)

> **Atenção:** este é **exemplo ilustrativo**. A versão real deve seguir o seu `DOMAIN_SPEC`.

**Patch — `app/domain/entities.py` (trecho):**

```diff
*** a/app/domain/entities.py
--- b/app/domain/entities.py
@@
 from dataclasses import dataclass
-from typing import Any
+from typing import Any, Optional
+from decimal import Decimal
+from uuid import UUID, uuid4
 
 
 class Status:
@@
 class Item:
@@
         if not isinstance(self.status, Status):
             raise ValueError("status must be a Status instance")
+
+# ===== New Domain Below (example) =====
+@dataclass(frozen=True)
+class Money:
+    """Value object monetário (amount >= 0; currency ISO-4217)."""
+    amount: Decimal
+    currency: str
+    def __post_init__(self):
+        if self.amount < 0:
+            raise ValueError("amount must be >= 0")
+        if len(self.currency) != 3 or not self.currency.isupper():
+            raise ValueError("currency must be 3-letter upper-case code")
+
+class OrderStatus:
+    """Máquina de estado de Order."""
+    VALID = {"created", "confirmed", "paid", "fulfilled", "closed", "canceled"}
+    TRANSITIONS = {
+        "created": {"confirmed", "canceled"},
+        "confirmed": {"paid", "canceled"},
+        "paid": {"fulfilled"},
+        "fulfilled": {"closed"},
+        "closed": set(),
+        "canceled": set(),
+    }
+    def __init__(self, value: str):
+        if value not in self.VALID:
+            raise ValueError(f"Invalid order status: {value}")
+        self.value = value
+    def can_transition_to(self, to: str) -> bool:
+        return to in self.TRANSITIONS[self.value]
+    def transition(self, to: str) -> "OrderStatus":
+        if not self.can_transition_to(to):
+            raise ValueError(f"Invalid transition: {self.value} -> {to}")
+        return OrderStatus(to)
+    def __str__(self) -> str:
+        return self.value
+
+@dataclass(frozen=True)
+class Order:
+    """Entidade de domínio: Order."""
+    order_id: UUID
+    customer_id: UUID
+    total: Money
+    status: OrderStatus
+    note: Optional[str] = None
+    def __post_init__(self):
+        if self.total.amount == 0 and str(self.status) == "paid":
+            from app.domain.errors import InvalidOrderState
+            raise InvalidOrderState("Pedido não pode estar 'paid' com total 0")
+    def confirm(self) -> "Order":
+        new_status = self.status.transition("confirmed")
+        return Order(self.order_id, self.customer_id, self.total, new_status, self.note)
+    def pay(self) -> "Order":
+        if self.total.amount <= 0:
+            from app.domain.errors import InvalidOrderState
+            raise InvalidOrderState("Total deve ser > 0 para pagar")
+        new_status = self.status.transition("paid")
+        return Order(self.order_id, self.customer_id, self.total, new_status, self.note)
```

**Patch — `app/domain/errors.py` (trecho):**

```diff
*** a/app/domain/errors.py
--- b/app/domain/errors.py
@@
 class InvalidStatus(DomainError):
     """Status inválido para entidade."""
     pass
+
+class InvalidOrderState(DomainError):
+    """Transição de estado inválida ou estado inconsistente de Order."""
+    pass
```

**Arquivo novo — `tests/unit/domain/test_entities.py`:**

```python
import pytest
from decimal import Decimal
from uuid import uuid4
from app.domain.entities import Money, Order, OrderStatus

def test_money_valid():
    m = Money(Decimal("10.00"), "USD")
    assert m.amount == Decimal("10.00")
    assert m.currency == "USD"

@pytest.mark.parametrize("amount", [Decimal("-1"), Decimal("-0.01")])
def test_money_negative(amount):
    with pytest.raises(ValueError):
        Money(amount, "USD")

def test_order_happy_path_confirm_pay():
    o = Order(order_id=uuid4(), customer_id=uuid4(),
              total=Money(Decimal("100.00"), "USD"),
              status=OrderStatus("created"))
    o2 = o.confirm()
    assert str(o2.status) == "confirmed"
    o3 = o2.pay()
    assert str(o3.status) == "paid"

def test_order_cannot_pay_with_zero_total():
    from app.domain.errors import InvalidOrderState
    o = Order(order_id=uuid4(), customer_id=uuid4(),
              total=Money(Decimal("0.00"), "USD"),
              status=OrderStatus("created"))
    with pytest.raises(InvalidOrderState):
        _ = o.pay()
```

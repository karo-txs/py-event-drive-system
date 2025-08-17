# PROMPT — Implementar Use Case(s) na camada **Application**

> **Contexto fixo do projeto**
>
> * Arquitetura: Clean/Hexagonal.
> * Domínio já implementado (puro).
> * **Template existente (NÃO ALTERAR caminhos/assinaturas sem instrução explícita):**
>
>   * `app/application/dtos.py`
>   * `app/application/errors.py`
>   * `app/application/ports.py`
>   * `app/application/use_cases/process_event.py` (exemplo existente; pode coexistir com novos casos)
> * **Ports estáveis** (não renomear métodos): `Repository[T]`, `MessageBus`, `ExternalApiClient`.

---

## 1) Campos a preencher pelo usuário (APP\_SPEC)

Preencha **todos** os `{{ }}`. Se algo não se aplica, use `null`.

```
# APP_SPEC

use_case_name: EditClinic

domain_entities:
  - Clinic

input_fields:
  - name: clinic_id
    type: UUID | str
    required: true
    validation: must exist
  - name: name
    type: str | None
    required: false
    validation: if provided, non-empty
  - name: address
    type: str | None
    required: false
    validation: none
  - name: phone
    type: str | None
    required: false
    validation: E.164 when provided
  - name: email
    type: str | None
    required: false
    validation: RFC 5322 basic when provided

output_fields:
  - name: success
    type: bool
  - name: message
    type: str

flow:
  - step: Load Clinic by clinic_id (Repository.get)
  - step: If not found -> ApplicationError("clinic_not_found")
  - step: Build new Clinic instance with updated fields (immutability)
  - step: Repository.save(updated_clinic)
  - step: Publish ClinicContactUpdated if contact/address/name changed
  - step: Return success

rules:
  - Validate phone/email when provided
  - No other domain side-effects

repository:
  entity: Clinic
  methods_required: [get, save]
  id_field: clinic_id

events_to_publish:
  - type: ClinicContactUpdated
    payload: { clinic_id: <uuid>, changed_fields: <list[str]> }

external_api: []

idempotency:
  key_from_input: clinic_id
  strategy: if no changes, still return success message "no_changes"

error_mapping:
  - from: InvalidEmail
    to: ApplicationError
    message: invalid email
  - from: InvalidPhone
    to: ApplicationError
    message: invalid phone

```

---

## 2) O que o Copilot deve gerar/editar

**Arquivos permitidos para mudança:**

* `app/application/dtos.py`

  * Criar **novos DTOs** (Input/Output) para o `use_case_name` **sem** remover os existentes (`ProcessEventInput/Output`).
* `app/application/use_cases/{{snake_case(use_case_name)}}.py`

  * Novo arquivo de caso de uso com classe `{{PascalCase(use_case_name)}}`.
  * Método assíncrono `execute(input_dto) -> output_dto`.
  * Usar **apenas** as portas: `Repository`, `MessageBus`, `ExternalApiClient`.
* `app/application/errors.py`

  * Se necessário, adicionar subclasses de `ApplicationError` (p.ex. `ValidationAppError`, `ConflictAppError`).
* `tests/unit/application/test_{{snake_case(use_case_name)}}.py`

  * Testes unitários assíncronos com **mocks** das portas.

> **Não alterar** assinaturas dos ports em `ports.py`.
> **Não acoplar** Application a ORM, boto, httpx etc. (isso é papel de Infrastructure/adapters).
> **Logging**: use `app.infrastructure.logging.logger.configure_logger` já existente.

---

## 3) Estrutura base de código (modelo)

> Copilot, use este esqueleto e preencha conforme `APP_SPEC`.

**Novo DTO em `app/application/dtos.py`:**

```python
# --- ADD BELOW (keep existing DTOs) ---
from dataclasses import dataclass
from typing import Optional

@dataclass
class {{PascalCase(use_case_name)}}Input:
    {{ for f in input_fields -}}
    {{ f.name }}: {{ f.type }}
    {{ endfor }}

@dataclass
class {{PascalCase(use_case_name)}}Output:
    {{ for f in output_fields -}}
    {{ f.name }}: {{ f.type }}
    {{ endfor }}
```

**Novo Use Case em `app/application/use_cases/{{snake_case(use_case_name)}}.py`:**

```python
from app.application.dtos import {{PascalCase(use_case_name)}}Input, {{PascalCase(use_case_name)}}Output
from app.application.ports import Repository, MessageBus, ExternalApiClient
from app.infrastructure.logging.logger import configure_logger
from app.application.errors import ApplicationError
from app.config.settings import Settings

# importe entidades/VOs/erros do domínio necessários
# ex.: from app.domain.entities import Clinic, ClinicHours, DayOfWeek, TimeRange
# ex.: from app.domain.errors import InvalidDayOfWeek, OverlappingClinicHours

settings = Settings()
logger = configure_logger(settings.LOG_LEVEL)

class {{PascalCase(use_case_name)}}:
    """Caso de uso: {{use_case_name}}."""

    def __init__(self,
                 repo: Repository[{{repository.entity}}],
                 bus: MessageBus,
                 api: ExternalApiClient):
        self.repo = repo
        self.bus = bus
        self.api = api

    async def execute(self, dto: {{PascalCase(use_case_name)}}Input) -> {{PascalCase(use_case_name)}}Output:
        try:
            # 1) Validar/preparar entrada conforme APP_SPEC.rules
            # 2) Carregar entidades necessárias via repo.get
            # 3) Construir/alterar entidades/VOs do domínio (imutáveis)
            # 4) Persistir via repo.save
            # 5) Chamar API externa (se definido em APP_SPEC.external_api) com retries simples, se aplicável
            # 6) Publicar evento(s) conforme APP_SPEC.events_to_publish
            # 7) Montar e retornar Output

            {{# exemplo de sketch – substitua pelos steps de flow }}
            # entity = await self.repo.get(dto.{{repository.id_field}})
            # if not entity: raise ApplicationError("...")

            # Chamada API externa (opcional)
            # await self.api.post("{{ external_api[0].path if external_api else '/noop' }}", {...})

            # Publicação de evento (opcional)
            # await self.bus.send({"type": "{{ events_to_publish[0].type if events_to_publish else 'Noop' }}", ...})

            return {{PascalCase(use_case_name)}}Output(
                {{ for f in output_fields -}}
                {{ f.name }}={{ "True" if f.name == "success" else "None" }},
                {{ endfor }}
            )
        except Exception as e:
            # Mapeamento de erros de domínio -> ApplicationError conforme APP_SPEC.error_mapping
            logger.error("Use case error", use_case="{{use_case_name}}", error=str(e))
            raise ApplicationError(str(e))
```

---

## 4) Testes unitários (modelo)

**`tests/unit/application/test_{{snake_case(use_case_name)}}.py`**

```python
import pytest
from types import SimpleNamespace
from app.application.use_cases.{{snake_case(use_case_name)}} import {{PascalCase(use_case_name)}}
from app.application.dtos import {{PascalCase(use_case_name)}}Input

class RepoMock:
    def __init__(self):
        self.saved = []
        self.by_id = {}
    async def get(self, id: str):
        return self.by_id.get(id)
    async def save(self, obj):
        self.saved.append(obj)

class BusMock:
    def __init__(self):
        self.events = []
    async def send(self, event: dict): self.events.append(event)
    async def receive(self) -> dict: return {}
    async def ack(self, message_id: str): ...
    async def nack(self, message_id: str): ...

class ApiMock:
    async def get(self, path: str, params: dict | None = None): return {"ok": True}
    async def post(self, path: str, data: dict): return {"ok": True}

@pytest.mark.asyncio
async def test_{{snake_case(use_case_name)}}_happy_path():
    repo, bus, api = RepoMock(), BusMock(), ApiMock()
    uc = {{PascalCase(use_case_name)}}(repo=repo, bus=bus, api=api)

    dto = {{PascalCase(use_case_name)}}Input(
        {{ for f in input_fields -}}
        {{ f.name }}={{ "True" if f.type == "bool" else "'x'" }},
        {{ endfor }}
    )
    out = await uc.execute(dto)
    assert hasattr(out, "success")
    assert out.success is True
```

---

## 5) Regras e limites

* **Não** alterar `ports.py` nem suas assinaturas.
* **Não** acoplar Application a bibliotecas de infraestrutura.
* **Não** remover `ProcessEvent` existente; novos casos devem viver em arquivos próprios.
* **Nomeação**: arquivo `snake_case(use_case_name).py`; classe `PascalCase(use_case_name)`.
* **Logging**: apenas via `configure_logger`.
* **Tratamento de erros**: converta erros de domínio → `ApplicationError` (ou subclasses que você criar).
* **Idempotência**: se definido em `APP_SPEC.idempotency`, implemente checagem simples (ex.: “se já salvo, retornar sucesso”).

---

## 6) Critérios de aceite

* Compila e roda testes **sem depender de banco/fila/HTTP reais** (mocks).
* Novo caso de uso **somente** usa os **ports**.
* Entrada/saída condizem com o `APP_SPEC`.
* Publicação de eventos e chamadas externas seguem o `APP_SPEC`.
* Mensagens de erro claras (via `ApplicationError`).

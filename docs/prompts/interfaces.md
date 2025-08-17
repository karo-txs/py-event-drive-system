# PROMPT — Implementar Interfaces (HTTP + Lambda + Worker)

> **Contexto fixo do projeto**
>
> * Arquitetura: Hexagonal. Application já tem **use cases** e **DTOs**. Infra já tem **providers** (`provide_repository`, `provide_message_bus`, `provide_external_api`) e **logger**.
> * **Template existente (não alterar estrutura/caminhos sem instrução explícita):**
>
>   * `app/interfaces/http/routers.py`, `app/interfaces/http/main.py`
>   * `app/interfaces/lambda/handler.py`
>   * `app/interfaces/worker/main.py`
> * Objetivo: expor **rotas HTTP** por use case, **rotear eventos no Lambda** por `command`/origem, e **processar mensagens no Worker** por `type`/`command`, tudo com validação Pydantic e mapeamento de erros consistente.

---

## 1) Preencha o **INTERFACES\_SPEC**

> Use nomes exatos dos seus use cases/DTOs já criados.

```
# INTERFACES_SPEC

http:
  base_path: "/api/v1"
  tags:
    - name: "clinic"
      description: "Endpoints de clínica"
  routes:
    - path: "/clinic"
      method: "POST"
      tag: "clinic"
      use_case: "RegisterClinic"
      input_dto: "RegisterClinicInput"
      output_dto: "RegisterClinicOutput"
      request_model_name: "RegisterClinicRequest"
      response_model_name: "RegisterClinicResponse"
    - path: "/clinic/{clinic_id}"
      method: "PATCH"
      tag: "clinic"
      use_case: "EditClinic"
      input_dto: "EditClinicInput"
      output_dto: "EditClinicOutput"
      request_model_name: "EditClinicRequest"
      response_model_name: "EditClinicResponse"
    - path: "/clinic/{clinic_id}"
      method: "DELETE"
      tag: "clinic"
      use_case: "RemoveClinic"
      input_dto: "RemoveClinicInput"
      output_dto: "RemoveClinicOutput"
      request_model_name: "RemoveClinicRequest"
      response_model_name: "RemoveClinicResponse"
    - path: "/clinics"
      method: "GET"
      tag: "clinic"
      use_case: "ListClinics"
      input_dto: "ListClinicsInput"
      output_dto: "ListClinicsOutput"
      request_model_name: null
      response_model_name: "ListClinicsResponse"
    - path: "/clinic/search"
      method: "GET"
      tag: "clinic"
      use_case: "GetClinic"
      input_dto: "GetClinicInput"
      output_dto: "GetClinicOutput"
      request_model_name: null
      response_model_name: "GetClinicResponse"

lambda:
  # Estratégia de roteamento: por "command" no body ou por origem (SQS/APIGW)
  command_field: "command"
  commands:
    - command: "register_clinic"
      use_case: "RegisterClinic"
      input_dto: "RegisterClinicInput"
    - command: "edit_clinic"
      use_case: "EditClinic"
      input_dto: "EditClinicInput"
    - command: "remove_clinic"
      use_case: "RemoveClinic"
      input_dto: "RemoveClinicInput"
    - command: "list_clinics"
      use_case: "ListClinics"
      input_dto: "ListClinicsInput"
    - command: "get_clinic"
      use_case: "GetClinic"
      input_dto: "GetClinicInput"

worker:
  # Estratégia de roteamento: por "type" do evento na fila
  type_field: "type"
  handlers:
    - type: "ClinicRegistered"
      use_case: "GetClinic"       # exemplo: pós-processamento
      input_builder: "lambda e: {'clinic_id': e['clinic_id']}"
    - type: "ClinicHoursDefined"
      use_case: "GetClinic"
      input_builder: "lambda e: {'clinic_id': e['clinic_id']}"
  idle_sleep_seconds: 1

errors:
  map:
    - from: "ApplicationError"
      http_status: 400
    - from: "InvalidEmail"
      http_status: 422
    - from: "OverlappingClinicHours"
      http_status: 409
    - from: "not_found"
      http_status: 404
```

---

## 2) O que você (Copilot) deve fazer

1. **Ler o `INTERFACES_SPEC`** e **inspecionar** `app/application/use_cases/*.py` e `app/application/dtos.py` para confirmar nomes/classes dos use cases e DTOs.
2. **HTTP (FastAPI)**:

   * Em `app/interfaces/http/routers.py`, adicionar rotas para cada item de `http.routes`.
   * Criar **Pydantic request models** (quando `request_model_name` != null) refletindo os campos do **Input DTO**. Para métodos GET, use **query params**.
   * Converter request → **Input DTO**, invocar o **use case**, devolver **Output DTO** (FastAPI pode serializar dataclasses).
   * Usar `Settings` + `providers` para injeção de `repo`, `bus`, `api`.
   * Adicionar **tratamento de erros** com mapeamento `errors.map`.
   * Colocar as rotas no `router` com **tags** conforme `http.tags`.
3. **Lambda** (`app/interfaces/lambda/handler.py`):

   * Roteamento por fonte: **SQS** (`Records`) e **API Gateway** (`body`).
   * Para APIGW, se houver `command` no body (`lambda.command_field`), selecionar use case; se não, manter compatibilidade do endpoint `/process` existente.
   * Para SQS, iterar mensagens; se houver `type` ou `command`, **rotear** para o use case correspondente; **ack/nack** via `MessageBus` se o seu adapter suportar.
   * Converter payload para **Input DTO** correto e retornar um dict serializável.
4. **Worker** (`app/interfaces/worker/main.py`):

   * Loop assíncrono infinito, `bus.receive()`; pegar `type` (conforme `worker.type_field`), montar input pelo `input_builder` (string Python a ser `eval`/implementada como função inline) e chamar o use case.
   * Logar sucesso/erro e `await asyncio.sleep(idle_sleep_seconds)`.
5. **Não remover** rotas/handler/worker existentes; **estender** mantendo compat.

---

## 3) Esqueletos de código a produzir/editar

### 3.1 HTTP — `app/interfaces/http/routers.py`

```python
from fastapi import APIRouter, Query, Path, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from app.config.settings import Settings
from app.infrastructure.providers import (
    provide_repository,
    provide_message_bus,
    provide_external_api,
)
from app.infrastructure.logging.logger import configure_logger

# DTOs e Use Cases descobertos pelo Copilot:
# from app.application.dtos import ...
# from app.application.use_cases.register_clinic import RegisterClinic
# ...

settings = Settings()
logger = configure_logger(settings.LOG_LEVEL)
router = APIRouter()

# Health existente
@router.get("/health", status_code=200, tags=["health"])
async def health():
    return {"status": "ok"}

# === Para cada rota em INTERFACES_SPEC.http.routes, gerar um bloco como abaixo ===

# Exemplo para POST /clinic -> RegisterClinic
class {{request_model_name or "Noop"}}(BaseModel):
    # Preencher com campos do {{input_dto}} (Copilot lê dos dataclasses)
    # Ex.: clinic_id: Optional[str] = None
    #     name: Optional[str] = None
    #     address: Optional[str] = None
    #     phone: Optional[str] = None
    #     email: Optional[str] = None
    #     hours: Optional[list[dict]] = None
    ...

@router.post("{{http.base_path}}{{path}}", response_model={{output_dto}}, tags=["{{tag}}"])
async def {{use_case|lower}}_endpoint(
    {{ "clinic_id: str" if "{clinic_id}" in path else "" }},
    payload: {{request_model_name}} = None
):
    try:
        repo = provide_repository(settings)
        bus = provide_message_bus(settings)
        api = provide_external_api(settings)

        # Import dinâmico do use case
        from app.application.use_cases.{{ use_case|snake }} import {{use_case}}
        from app.application.dtos import {{input_dto}}, {{output_dto}}

        # Montar DTO de input a partir de path/query/payload
        # Exemplo base:
        data = {}
        if payload: data.update(payload.model_dump(exclude_none=True))
        if "{{ 'clinic_id' if '{clinic_id}' in path else '' }}":
            data["clinic_id"] = clinic_id

        dto = {{input_dto}}(**data)

        uc = {{use_case}}(repo=repo, bus=bus, api=api)
        result: {{output_dto}} = await uc.execute(dto)
        return result
    except Exception as exc:
        # Mapeamento de erros HTTP
        status = _map_http_status(exc)
        logger.error("HTTP handler error", route="{{path}}", error=str(exc))
        raise HTTPException(status_code=status, detail=str(exc))

def _map_http_status(exc: Exception) -> int:
    name = exc.__class__.__name__
    msg = str(exc).lower()
    # Preencher com INTERFACES_SPEC.errors.map
    if name == "ApplicationError": return 400
    if "invalid email" in msg: return 422
    if "overlap" in msg: return 409
    if "not_found" in msg: return 404
    return 500
```

> **Observação:** Para rotas **GET** (List/Get), o Copilot deve gerar assinaturas com **query params** (ex.: `page: int = Query(1, ge=1)`, `email: Optional[str] = Query(None)`), construir o **Input DTO** a partir desses params e não usar `payload`.

---

### 3.2 FastAPI App — `app/interfaces/http/main.py`

```python
from fastapi import FastAPI
from app.infrastructure.persistence.db import init_db
from app.interfaces.http.routers import router
from app.config.settings import Settings

def create_app() -> FastAPI:
    settings = Settings()
    app = FastAPI(
        title="dev-event-driven-system",
        version="0.1.0",
        description="Microserviço hexagonal orientado a eventos",
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    app.include_router(router, prefix="")  # rotas já incluem base_path

    @app.on_event("startup")
    async def on_startup():
        await init_db()

    return app

def get_app():
    return create_app()
```

---

### 3.3 Lambda — `app/interfaces/lambda/handler.py`

```python
import json, asyncio
from app.infrastructure.providers import provide_repository, provide_message_bus, provide_external_api
from app.infrastructure.logging.logger import configure_logger
from app.application.errors import ApplicationError
from app.config.settings import Settings

settings = Settings()
logger = configure_logger(settings.LOG_LEVEL)

COMMAND_FIELD = "{{ lambda.command_field }}"
COMMAND_MAP = {
{% for c in lambda.commands -%}
    "{{ c.command }}": ("{{ c.use_case|snake }}", "{{ c.use_case }}", "{{ c.input_dto }}"),
{% endfor -%}
}

def handler(event, context):
    try:
        # SQS batch
        if "Records" in event:
            for r in event["Records"]:
                payload = _parse_record(r)
                asyncio.run(_dispatch(payload))
            return {"statusCode": 200, "body": "Processed SQS batch"}

        # API Gateway HTTP
        if "body" in event:
            body = json.loads(event["body"] or "{}")
            res = asyncio.run(_dispatch(body))
            return {"statusCode": 200, "body": json.dumps(res)}

        logger.error("Evento não reconhecido", event=event)
        return {"statusCode": 400, "body": "Bad event"}
    except Exception as e:
        logger.error("Erro no handler", error=str(e))
        return {"statusCode": 500, "body": str(e)}

def _parse_record(record):
    try:
        return json.loads(record.get("body") or "{}")
    except Exception:
        return {}

async def _dispatch(body: dict):
    repo = provide_repository(settings)
    bus  = provide_message_bus(settings)
    api  = provide_external_api(settings)

    command = body.get(COMMAND_FIELD)
    if command and command in COMMAND_MAP:
        module_name, class_name, input_dto = COMMAND_MAP[command]
        uc = _import_uc(module_name, class_name)
        dto_cls = _import_dto(input_dto)
        dto = dto_cls(**body)
        result = await uc(repo=repo, bus=bus, api=api).execute(dto)
        return _to_plain(result)

    # Fallback para compat /process antigo (ProcessEvent)
    try:
        from app.application.use_cases.process_event import ProcessEvent
        from app.application.dtos import ProcessEventInput
        dto = ProcessEventInput(payload=body)
        result = await ProcessEvent(repo, bus, api).execute(dto)
        return _to_plain(result)
    except Exception as e:
        raise e

def _import_uc(module_name: str, class_name: str):
    mod = __import__(f"app.application.use_cases.{module_name}", fromlist=[class_name])
    return getattr(mod, class_name)

def _import_dto(class_name: str):
    mod = __import__("app.application.dtos", fromlist=[class_name])
    return getattr(mod, class_name)

def _to_plain(obj):
    # dataclass → dict
    try:
        from dataclasses import asdict, is_dataclass
        return asdict(obj) if is_dataclass(obj) else obj
    except Exception:
        return obj
```

---

### 3.4 Worker — `app/interfaces/worker/main.py`

```python
import asyncio
from typing import Callable, Any, Dict
from app.infrastructure.providers import provide_repository, provide_message_bus
from app.infrastructure.logging.logger import configure_logger
from app.config.settings import Settings

settings = Settings()
logger = configure_logger(settings.LOG_LEVEL)

TYPE_FIELD = "{{ worker.type_field }}"
IDLE_SLEEP = {{ worker.idle_sleep_seconds }}

# Construir o mapa de handlers a partir de INTERFACES_SPEC.worker.handlers
HANDLERS = {
{% for h in worker.handlers -%}
    "{{ h.type }}": ("{{ h.use_case|snake }}", "{{ h.use_case }}", {{ h.input_builder }}),
{% endfor -%}
}

async def worker_loop():
    repo = provide_repository(settings)
    bus  = provide_message_bus(settings)
    logger.info("Worker iniciado, aguardando mensagens...")

    while True:
        msg = await bus.receive()
        try:
            event_type = msg.get(TYPE_FIELD) or msg.get("type")
            body = msg.get("body") if "body" in msg else msg
            if not event_type or event_type not in HANDLERS:
                logger.info("Evento ignorado", event=event_type)
                await asyncio.sleep(IDLE_SLEEP); continue

            module_name, class_name, builder = HANDLERS[event_type]
            uc = _import_uc(module_name, class_name)
            dto_input = builder(body) if callable(builder) else {}
            dto_cls = _infer_input_dto(class_name)  # opcional: criar heurística por nome
            dto = dto_cls(**dto_input)

            result = await uc(repo=repo, bus=bus, api=None).execute(dto)
            logger.info("Evento processado", type=event_type, result=_safe(result))
        except Exception as exc:
            logger.error("Erro ao processar evento", error=str(exc))
        await asyncio.sleep(IDLE_SLEEP)

def _import_uc(module_name: str, class_name: str):
    mod = __import__(f"app.application.use_cases.{module_name}", fromlist=[class_name])
    return getattr(mod, class_name)

def _infer_input_dto(class_name: str):
    # Convencional: <UseCaseName>Input
    dto_name = f"{class_name}Input"
    mod = __import__("app.application.dtos", fromlist=[dto_name])
    return getattr(mod, dto_name)

def _safe(obj: Any) -> Dict[str, Any]:
    try:
        from dataclasses import asdict, is_dataclass
        return asdict(obj) if is_dataclass(obj) else obj
    except Exception:
        return {"ok": True}
```

---

## 4) Regras e limites

* **Não** alterar `providers` nem ports.
* **Não** acoplar HTTP/Lambda/Worker a detalhes de ORM/mensageria; só use **use cases** e **DTOs**.
* **Validação**: entrada via **Pydantic**; saída via **DTOs** (dataclasses) — FastAPI serializa.
* **Erros**: mapear para HTTP status conforme `INTERFACES_SPEC.errors.map`; no Lambda/Worker, apenas logar e devolver mensagem com `success=false` (se aplicável).
* **Logs**: sempre `configure_logger`.
* **Compatibilidade**: manter endpoints/handler originais e apenas **estender** (ex.: `/process`).

---

## 5) Formato da resposta do Copilot

1. **Resumo**: rotas geradas, comandos do Lambda e tipos do Worker.
2. **Diffs** aplicados em `routers.py`, `main.py`, `lambda/handler.py`, `worker/main.py`.
3. **Exemplos de chamadas**:

   * HTTP: `curl -X POST {{base_path}}/clinic -H "Content-Type: application/json" -d '{...}'`
   * Lambda: body `{"command": "register_clinic", ...}`
   * Worker: mensagem `{"type":"ClinicRegistered","clinic_id":"..."}`
4. **Checklist**:

   * `uv run uvicorn app.interfaces.http.main:get_app --factory` → `/docs` ok
   * Simular Lambda local com payloads de exemplo
   * Rodar worker local e enviar mensagens no broker

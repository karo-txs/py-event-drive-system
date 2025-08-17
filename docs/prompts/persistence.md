# PROMPT — Persistência (SQLAlchemy Async): **models + repositories**

> **Contexto fixo**
>
> * Arquitetura hexagonal: Repositories implementam **ports** da camada Application, sem lógica de domínio.
> * ORM: **SQLAlchemy Async** (`AsyncSession`), mapeamentos simples e conversão **to\_entity/from\_entity**.
> * Banco/Tabelas: **já criadas por outro projeto** — vamos **reutilizar** os modelos SQLAlchemy fornecidos pelo usuário.
> * **Não** alterar `app/application/ports.py` (assinaturas).
> * **Transações**: preferir `async with session.begin():` quando fizer sentido.

---

## 1) **PERSIST\_SPEC**

```
# PERSIST_SPEC

## Entidades do domínio alvo (nome exato do módulo de domínio)
domain_entities:
  - {{ "Clinic" }}
  - {{ "ClinicHours" }}

## Modelos SQLAlchemy já prontos (cole aqui o CÓDIGO Python completo)
sqlalchemy_models_code: |
  {{ cole aqui seus modelos SQLAlchemy existentes, por ex. ClinicModel, ClinicHoursModel,
     incluindo Base/declarative_base (ou indique que deve reutilizar Base do template) }}

## Tabela/esquema
schema: {{ ex.: "public" | "agendia" }}
conventions:
  use_uuid: {{ true | false }}
  time_types: {{ "Time" | "String(HH:MM:SS)" }}
  timezone_aware: {{ true | false }}

## Mapeamento domínio <-> modelo
mappings:
  Clinic:
    model: {{ "ClinicModel" }}
    id_field: {{ "id" | "clinic_id" }}
    fields:
      name: {{ "nome" | "name" }}
      address: {{ "endereco" | "address" }}
      phone: {{ "telefone" | "phone" }}
      email: {{ "email" }}
      created_at: {{ "created_at" }}
  ClinicHours:
    model: {{ "ClinicHoursModel" }}
    id_field: {{ "id" | "clinic_hours_id" }}
    fields:
      clinic_id: {{ "clinic_id" }}
      day_of_week: {{ "day_of_week" }}
      open_time: {{ "open_time" }}
      close_time: {{ "close_time" }}
      valid_from: {{ "valid_from" }}
      valid_to: {{ "valid_to" }}

## Consultas necessárias (além de get/save do Port)
queries:
  - name: get_by_email
    target: Clinic
    where: email = :email
    returns: one_or_none
  - name: find_by_name
    target: Clinic
    where: name ILIKE :name
    returns: list
  - name: list_all_with_pagination
    target: Clinic
    params: [page, page_size]
    returns: list_and_total
  - name: list_hours_by_clinic
    target: ClinicHours
    where: clinic_id = :clinic_id
    returns: list
  - name: delete_clinic_and_hours
    target: Clinic
    where: clinic_id = :clinic_id
    returns: affected_counts

## Política de gravação
write_policy:
  clinic:
    mode: {{ "upsert" | "insert_then_update_on_conflict" | "replace" }}
  clinichours:
    mode: {{ "upsert" | "replace" }}

## Conversões especiais (opcional)
conversions:
  time_as_str: {{ true | false }}  # se ORM usa Time, mas domínio usa str, converter "HH:MM[:SS]"
  uuid_as_str: {{ true | false }}  # se domínio usa str e DB usa UUID
```

---

## 2) O que o Copilot deve gerar/editar

**Arquivos alvo (NÃO tocar nos ports):**

* `app/infrastructure/persistence/models.py`

  * Incluir/organizar os **modelos SQLAlchemy colados** em `sqlalchemy_models_code`.
  * Reutilizar `Base = declarative_base()` do template (ou o fornecido).
  * Implementar `to_entity()` e `from_entity()` para **Clinic** e **ClinicHours** baseados em `mappings` e `conversions`.

* `app/infrastructure/persistence/repositories.py`

  * Criar `ClinicRepository(Repository[Clinic])` e `ClinicHoursRepository(Repository[ClinicHours])`.
  * Métodos obrigatórios do Port: `get(id: str) -> T | None`, `save(obj: T) -> None`.
  * Implementar **métodos extras** de `queries` (e.g., `get_by_email`, `find_by_name`, `list_all_with_pagination`, `list_hours_by_clinic`, `delete_clinic_and_hours`).
  * **Transações**: usar `async with self.session.begin():` para writes compostos; `commit()` quando apropriado.

> Se seu repositório estiver com o caminho `infraesctructure/…`, aplicar as mesmas mudanças lá **ou** corrigir para `infrastructure/…` e ajustar imports.

---

## 3) Regras de implementação

* **Async** sempre que acessar banco.
* **Sem** importar erros de Application; lidar com `IntegrityError`/`NoResultFound` localmente e propagar exceções do SQLAlchemy como-is (ou encapsular em exceções de infra, se desejar).
* **to\_entity/from\_entity** devem respeitar o domínio (imutável).
* `list_all_with_pagination`: retornar `(items, total)`; paginação 1‑based; `LIMIT/OFFSET`.
* `delete_clinic_and_hours`: efetuar remoções em **transação única** (ou marcar como inativo se optar por soft delete; documente).
* **Conversões**:

  * `UUID <-> str`: usar `str(uuid)` ao sair e `UUID(s)` ao entrar se domínio exigir.
  * `Time <-> str`: normalizar para `HH:MM[:SS]`.
  * `timezone-aware datetime`: garantir `.tzinfo` ao construir entidade.
* **Índices e FKs**: **não** criar/migrar — assumimos DB pronto.
* **Performance**: nas consultas de lista, usar `selectinload` (se necessário) ou consultas separadas batched.

---

## 4) Esqueletos que o Copilot deve produzir

**`models.py` (trechos — manter `ItemModel` existente):**

```python
# --- PRESERVE o que já existe ---
from sqlalchemy.orm import Mapped, mapped_column, declarative_base
from sqlalchemy import String, DateTime, Time, Text, Integer, ForeignKey
from typing import Optional
from datetime import time, date, datetime
from uuid import UUID

Base = declarative_base()

# == Cole aqui os modelos do PERSIST_SPEC.sqlalchemy_models_code ==
# e, se necessário, ajuste para reutilizar 'Base' acima.

# Exemplo ilustrativo (substitua pelos seus):
class ClinicModel(Base):
    __tablename__ = "clinic"
    __table_args__ = {"schema": "{{schema}}", "comment": "Clínica"}
    id: Mapped[str] = mapped_column(String, primary_key=True)  # ou UUID, conforme seu modelo
    nome: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    endereco: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    telefone: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone={{timezone_aware}}), nullable=True)

    # ---- mapeamento domínio <-> modelo ----
    def to_entity(self) -> "Clinic":
        from app.domain.entities import Clinic
        # aplicar conversions (uuid_as_str, time_as_str...) se necessário
        return Clinic(
            clinic_id=self.id,
            name=self.nome,
            address=self.endereco,
            phone=self.telefone,
            email=self.email,
            created_at=self.created_at,
        )

    @staticmethod
    def from_entity(entity: "Clinic") -> "ClinicModel":
        return ClinicModel(
            id=str(entity.clinic_id),
            nome=entity.name,
            endereco=entity.address,
            telefone=entity.phone,
            email=entity.email,
            created_at=entity.created_at,
        )

class ClinicHoursModel(Base):
    __tablename__ = "clinic_hours"
    __table_args__ = {"schema": "{{schema}}", "comment": "Horário_Clínica"}
    id: Mapped[str] = mapped_column(String, primary_key=True)  # ou UUID
    clinic_id: Mapped[str] = mapped_column(ForeignKey(f"{{schema}}.clinic.id"), nullable=False)
    day_of_week: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    open_time: Mapped[Optional[Time]] = mapped_column(Time, nullable=True)
    close_time: Mapped[Optional[Time]] = mapped_column(Time, nullable=True)
    valid_from: Mapped[Optional[date]] = mapped_column(nullable=True)
    valid_to: Mapped[Optional[date]] = mapped_column(nullable=True)

    def to_entity(self) -> "ClinicHours":
        from app.domain.entities import ClinicHours
        return ClinicHours(
            clinic_hours_id=self.id,
            clinic_id=self.clinic_id,
            day_of_week=self.day_of_week,
            open_time=self.open_time.isoformat() if self.open_time else None,
            close_time=self.close_time.isoformat() if self.close_time else None,
            valid_from=self.valid_from,
            valid_to=self.valid_to,
        )

    @staticmethod
    def from_entity(entity: "ClinicHours") -> "ClinicHoursModel":
        from datetime import time
        def _parse_t(s: str | None) -> Optional[time]:
            if not s: return None
            parts = [int(p) for p in s.split(":")]
            return time(parts[0], parts[1], parts[2] if len(parts) > 2 else 0)

        return ClinicHoursModel(
            id=str(entity.clinic_hours_id),
            clinic_id=str(entity.clinic_id),
            day_of_week=entity.day_of_week,
            open_time=_parse_t(entity.open_time),
            close_time=_parse_t(entity.close_time),
            valid_from=entity.valid_from,
            valid_to=entity.valid_to,
        )
```

**`repositories.py` (novos repositórios + métodos extras):**

```python
from typing import Optional, Iterable, Tuple, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from sqlalchemy.orm import selectinload

from app.application.ports import Repository
from .models import ClinicModel, ClinicHoursModel

# ---- ClinicRepository ----
class ClinicRepository(Repository["Clinic"]):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, id: str) -> Optional["Clinic"]:
        res = await self.session.execute(select(ClinicModel).where(ClinicModel.id == id))
        row = res.scalar_one_or_none()
        return row.to_entity() if row else None

    async def save(self, obj: "Clinic") -> None:
        model = ClinicModel.from_entity(obj)
        async with self.session.begin():
            await self.session.merge(model)

    # Extras (conforme PERSIST_SPEC.queries)
    async def get_by_email(self, email: str) -> Optional["Clinic"]:
        res = await self.session.execute(select(ClinicModel).where(ClinicModel.email == email))
        row = res.scalar_one_or_none()
        return row.to_entity() if row else None


# ---- ClinicHoursRepository ----
class ClinicHoursRepository(Repository["ClinicHours"]):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, id: str) -> Optional["ClinicHours"]:
        res = await self.session.execute(select(ClinicHoursModel).where(ClinicHoursModel.id == id))
        row = res.scalar_one_or_none()
        return row.to_entity() if row else None

    async def save(self, obj: "ClinicHours") -> None:
        model = ClinicHoursModel.from_entity(obj)
        async with self.session.begin():
            await self.session.merge(model)

    async def list_hours_by_clinic(self, clinic_id: str) -> List["ClinicHours"]:
        res = await self.session.execute(select(ClinicHoursModel).where(ClinicHoursModel.clinic_id == clinic_id))
        rows = res.scalars().all()
        return [r.to_entity() for r in rows]

    async def delete_clinic_and_hours(self, clinic_id: str) -> tuple[int, int]:
        """Remove horários e a clínica numa única transação. Retorna (hours_deleted, clinic_deleted)."""
        async with self.session.begin():
            hrs_res = await self.session.execute(
                delete(ClinicHoursModel).where(ClinicHoursModel.clinic_id == clinic_id).returning(ClinicHoursModel.id)
            )
            hours_deleted = len(hrs_res.scalars().all())
            cl_res = await self.session.execute(
                delete(ClinicModel).where(ClinicModel.id == clinic_id).returning(ClinicModel.id)
            )
            clinic_deleted = len(cl_res.scalars().all())
        return hours_deleted, clinic_deleted
```

---

## 5) Testes (mínimos)

* `tests/integration/persistence/test_clinic_repo.py`

  * Subir `AsyncSession` (SQLite em memória ou Postgres de teste).
  * Inserir `ClinicModel` e ler via repo.get.
  * Testar `save` (merge/upsert).
  * Testar `find_by_name`, `get_by_email`, `list_all_with_pagination`.

* `tests/integration/persistence/test_clinic_hours_repo.py`

  * Criar clinic + vários hours e validar `list_hours_by_clinic`.
  * Validar `delete_clinic_and_hours` retorna contagens corretas.

> Se usar SQLite para testes, ajuste tipos de tempo/uuid conforme necessário.


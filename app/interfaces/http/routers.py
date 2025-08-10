from app.infrastructure.providers import (
    provide_repository,
    provide_message_bus,
    provide_external_api,
)
from app.application.dtos import ProcessEventInput, ProcessEventOutput
from app.application.use_cases.process_event import ProcessEvent
from app.config.settings import Settings
from pydantic import BaseModel
from fastapi import APIRouter


router = APIRouter()


class ProcessPayload(BaseModel):
    id: str | None = None
    name: str


@router.get("/health", status_code=200)
async def health():
    return {"status": "ok"}


@router.post("/process", response_model=ProcessEventOutput)
async def process(payload: ProcessPayload):
    settings = Settings()
    repo = provide_repository(settings)
    bus = provide_message_bus(settings)
    api = provide_external_api(settings)
    use_case = ProcessEvent(repo, bus, api)
    dto = ProcessEventInput(payload.model_dump())
    # try:
    result = await use_case.execute(dto)
    return result
    # except Exception as exc:
    #     return JSONResponse(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         content={"error": f"Erro ao processar evento: {exc}"},
    #     )

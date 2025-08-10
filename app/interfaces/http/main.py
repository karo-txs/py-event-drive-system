from app.infrastructure.persistence.db import init_db
from app.interfaces.http.routers import router
from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI(
        title="dev-event-driven-system",
        version="0.1.0",
        description="Microserviço hexagonal orientado a eventos",
    )
    app.include_router(router)

    @app.on_event("startup")
    async def on_startup():
        await init_db()

    return app


def get_app():
    return create_app()

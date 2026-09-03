from fastapi import FastAPI

from personal_finance.api.routers.health import router as health_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Personal Finance API",
        version="0.2.0",
    )

    app.include_router(health_router)

    return app

"""Localhost application."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from task_manager.web.api import router as api_router
from task_manager.web.pages import router as page_router
from task_manager.workspace import Workspace


def create_app(workspace: Workspace) -> FastAPI:
    app = FastAPI(title="AI Engineering Task Manager")
    app.state.workspace = workspace
    app.include_router(api_router)
    app.include_router(page_router)

    @app.exception_handler(RequestValidationError)
    async def validation_error(_request: Request, _exc: RequestValidationError):
        return JSONResponse(
            status_code=400,
            content={
                "refused": True,
                "message": "The request is missing a required field or has the wrong shape.",
            },
        )

    return app

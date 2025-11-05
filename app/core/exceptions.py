from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from app.core.logger import logger

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException):
        logger.error(f"HTTPException {exc.status_code}: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.status_code, "detail": exc.detail}},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception):
        logger.exception(f"Unhandled Exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={"error": {"code": 500, "detail": f"Internal server error: {str(exc)}"}},
        )

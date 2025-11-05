from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers_analyze import router as analyze_router
from app.core.exceptions import register_exception_handlers
from app.core.logger import logger
from dotenv import load_dotenv

load_dotenv()  # Load .env file

app = FastAPI(
    title="Vendor Voice VLLM",
    version="1.2.0",
    description="Converts multiple file uploads to PDF on the fly and converts to text.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
app.include_router(analyze_router, prefix="/v1")

@app.get("/health")
async def health():
    logger.info("Health check requested")
    return {"status": "ok", "version": app.version}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

import os
from fastapi.security.api_key import APIKeyHeader
from fastapi import HTTPException, Security, status
from dotenv import load_dotenv
load_dotenv()

SUPPORTED_IMAGE_MIMES = {
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/gif",
    "image/webp",
}

SUPPORTED_PDF_MIME = "application/pdf"
SUPPORTED_ALL = SUPPORTED_IMAGE_MIMES | {"application/vnd.openxmlformats-officedocument.wordprocessingml.document", SUPPORTED_PDF_MIME}

MAX_FILE_BYTES = 50 * 1024 * 1024  # 50 MB
MAX_FILES = 10

DEFAULT_MODEL = "gpt-5-mini"
TEMPERATURE = 0.1

FASTAPI_SECRET_KEY = os.getenv("FASTAPI_SECRET_KEY")

# Security
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    """Check if provided API key matches env secret."""
    if not api_key or api_key != FASTAPI_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
        )
    return True
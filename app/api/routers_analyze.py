import uuid
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from app.models.schemas import AnalyzeResponse
from app.services.openai_client import process_files
from app.core.config import verify_api_key
from app.core.logger import logger

router = APIRouter(tags=["File Analysis"])

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    files: list[UploadFile] = File(..., description="Upload multiple image/PDF/DOCX files."),
    prompt: str = Form(default="Give me relevant info that I will pass to voice agent to help fix customer issue."),
    _: bool = Depends(verify_api_key),
):
    # Generate a short unique ID for traceability
    request_id = str(uuid.uuid4())[:8]
    logger.info(f"[{request_id}] Received request with {len(files)} files for analysis.")

    try:
        result = await process_files(files, prompt, request_id)
        logger.info(f"[{request_id}] Request completed successfully.")
        return result

    except HTTPException as e:
        logger.error(f"[{request_id}] HTTP error: {e.detail}")
        raise

    except Exception as e:
        logger.exception(f"[{request_id}] Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"[{request_id}] {str(e)}")

import io
import asyncio
from fastapi import UploadFile, HTTPException
from openai import OpenAI
from app.models.schemas import FileResult, AnalyzeResponse
from app.services.file_converter import convert_to_pdf_bytes
from app.core.config import SUPPORTED_ALL, MAX_FILES, MAX_FILE_BYTES, DEFAULT_MODEL, TEMPERATURE
from app.core.logger import logger

async def _read_upload(upload: UploadFile) -> bytes:
    data = await upload.read()
    if not data:
        raise HTTPException(status_code=400, detail=f"Empty file: {upload.filename}")
    if len(data) > MAX_FILE_BYTES:
        raise HTTPException(status_code=413, detail=f"File too large (> {MAX_FILE_BYTES} bytes): {upload.filename}")
    return data

async def _upload_pdf_to_openai(client: OpenAI, pdf_name: str, pdf_bytes: bytes) -> str:
    try:
        file_res = client.files.create(
            file=(pdf_name, io.BytesIO(pdf_bytes), "application/pdf"),
            purpose="user_data",
        )
        logger.info(f"Uploaded file to OpenAI: {pdf_name}")
        return file_res.id
    except Exception as e:
        logger.error(f"OpenAI upload failed: {e}")
        raise HTTPException(status_code=502, detail=f"OpenAI file upload failed: {e}")

async def _convert_and_upload(client: OpenAI, upload: UploadFile) -> FileResult:
    if upload.content_type not in SUPPORTED_ALL:
        raise HTTPException(status_code=415, detail=f"Unsupported file type: {upload.filename}")

    data = await _read_upload(upload)
    pdf_name, pdf_bytes = convert_to_pdf_bytes(data, upload.filename, upload.content_type)
    file_id = await _upload_pdf_to_openai(client, pdf_name, pdf_bytes)

    return FileResult(
        original_filename=upload.filename,
        original_mime=upload.content_type,
        converted_filename=pdf_name,
        converted_bytes=len(pdf_bytes),
        openai_file_id=file_id,
    )

def _build_input_parts(prompt: str, file_ids: list[str]) -> list[dict]:
    parts = [{"type": "input_text", "text": prompt}]
    for fid in file_ids:
        parts.append({"type": "input_file", "file_id": fid})
    return [{"role": "user", "content": parts}]

async def process_files(files: list[UploadFile], prompt: str, request_id: str) -> AnalyzeResponse:
    if not files:
        raise HTTPException(status_code=400, detail="No files provided.")
    if len(files) > MAX_FILES:
        raise HTTPException(status_code=400, detail=f"Too many files. Max allowed: {MAX_FILES}.")
        
        
    client = OpenAI()

    tasks = [_convert_and_upload(client, f) for f in files]
    results = await asyncio.gather(*tasks)
    file_ids = [r.openai_file_id for r in results]

    try:
        response = client.responses.create(
            model=DEFAULT_MODEL,
            instructions=(
                "You are an assistant that extracts meaningful information from ticket attachments "
                "to help a voice agent understand and speak to the customer to solve his ticket issue since it cant read attachments at all. "
                "Read the uploaded files carefully (screenshots, PDFs, or documents) "
                "and identify any relevant issue descriptions, details, "
                "dates, or identifiers related to the support ticket. If there are multiple files, write each one separately."
                "You would say something like 'In the first attachment, I found...'. In the second one, I found...'. "
                "Do not try to solve the issue and do not mention information that is not in the images, just extract relevant information. "
                "Return the extracted text in clear, concise, and short using simple basic English."
            ),
            # temperature=TEMPERATURE,
            input=_build_input_parts(prompt, file_ids),
        )
        output_raw = getattr(response, "output_text", None) or str(response)
        output_text = f"Extracted information from the attachment: {output_raw}"
        logger.info("OpenAI response generated successfully.")

    except Exception as e:
        logger.error(f"OpenAI response failed: {e}")
        raise HTTPException(status_code=502, detail=f"OpenAI analysis failed: {e}")

    return AnalyzeResponse(
        model=DEFAULT_MODEL,
        prompt_used=prompt,
        output_text=output_text,
        files=results,
        request_id=request_id
    )

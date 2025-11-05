from pydantic import BaseModel, Field
from typing import List

class FileResult(BaseModel):
    original_filename: str
    original_mime: str
    converted_filename: str
    converted_bytes: int
    openai_file_id: str

class AnalyzeResponse(BaseModel):
    model: str
    prompt_used: str
    output_text: str
    files: List[FileResult] = Field(default_factory=list)
    request_id: str

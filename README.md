# Vendor Attachment Analysis

FastAPI service that accepts multiple user uploads, converts them to PDF when necessary, and forwards them to OpenAI's Responses API for analysis.

## Features
- Upload multiple files with a single request.
- Automatic conversion of supported images and plain text files to PDF before analysis.
- Temporary file handling so nothing persists once a request finishes.
- Centralised error handling with clear HTTP status codes for common failure cases.

## Requirements
- Python 3.11+
- An OpenAI API key with access to a multimodal model that supports PDF inputs (for example `gpt-5`).

## Installation
```bash
python -m venv .venv
.venv\\Scripts\\activate  # Windows
pip install -r requirements.txt
```

## Configuration
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=sk-...
FASTAPI_SECRET_KEY=MO-VLLM-sdhUIDM19402KLOSN
```

## Running the API
Start the FastAPI app with Uvicorn:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
The service will be available at `http://localhost:8000`.

## API Endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Basic readiness probe. |
| POST | `/api/v1/documents/analyze` | Convert uploads to PDF and request an OpenAI analysis. |

### POST `/api/v1/analyze`
### Required Headers

When sending requests (via Postman, curl, or another client), make sure to include the following headers:

| Key | Value |
|------|--------|
| `x-api-key` | `MO-VLLM-sdhUIDM19402KLOSN` |
| `accept` | `application/json` |

These headers authenticate your request and specify that responses will be in JSON format.

#### In Postman
1. Go to the **Headers** tab.  
2. Add a key named `x-api-key` and paste the value above.  
3. Add another key named `accept` with the value `application/json`.
- **Content type:** `multipart/form-data`
- **Body fields:**
  - `prompt` (text): instruction for the model. (Use the default)
  - `files` (file, repeatable): one or more files. Accepts PDFs, PNG/JPEG/WebP/TIFF/BMP images.
- **Response:**
```json
{
    "model": "gpt-5-mini",
    "prompt_used": "Give me relevant info that I will pass to voice agent to help fix customer issue.",
    "output_text": "Extracted information from the attachment: In the first attachment, I found:\n- A modal titled \"Default Shipping Configuration.\"\n- Message: there are no warehouses configured for shipping. It says you can create warehouses on the Warehouses page under Inventory Management, or save the product as a draft and then continue editing after creating warehouses.\n- The shipping setup UI is visible (shipper, from/to city, estimated days, policy fields).\n\nIn the second attachment, I found:\n- A validation popup: \"Please fill the missing fields and/or correct the listed entries in order to submit your product for approval.\"\n- Specific error: \"There is an issue with your shipping configuration: quantities from 1000 to 9999 are not covered. (in default shipping config)\"\n\nIn the third attachment, I found:\n- Two red error banners: \"The item_shipping field is required.\" and \"The tax_shipping field is required.\"\n- The Add Product form with Product Name shown as \"PRIOR Wall Light Sandy Dark Grey Aluminum.\"\n- The page includes product info fields (brand, tags) and a \"Preview Product\" button at top.\n\nUse these exact issues and product name when speaking to the customer.",
    "files": [
        {
            "original_filename": "Shipping config.png",
            "original_mime": "image/png",
            "converted_filename": "Shipping config.pdf",
            "converted_bytes": 116314,
            "openai_file_id": "file-KfYQBMbKzV5AMtUxbY6Zfe"
        },
        {
            "original_filename": "9999.jpg",
            "original_mime": "image/jpeg",
            "converted_filename": "9999.pdf",
            "converted_bytes": 39952,
            "openai_file_id": "file-ULqgfpaY3eigCv1g76REVq"
        },
        {
            "original_filename": "bulk upload.png",
            "original_mime": "image/png",
            "converted_filename": "bulk upload.pdf",
            "converted_bytes": 63564,
            "openai_file_id": "file-FAMYV7S6zco2f1WDFcgyha"
        }
    ],
    "request_id": "3471a77d"
}
```

### Error status codes
- `400` � Invalid request or custom application error.
- `413` � File exceeds the configured size limit.
- `415` � Unsupported file type.
- `422` � Validation error (e.g., missing prompt).
- `502` � Upstream OpenAI failure.

## Supported Conversions
- PDFs are passed through unchanged.
- Images (`png`, `jpg/jpeg`, `webp`, `tiff`, `bmp`) are flattened to PDF.


## Postman Usage
1. Open Postman and create a new `POST` request to `http://localhost:8000/api/v1/analyze` or to `http://staging.caestro.com:8005/v1/analyze` to test in staging.
2. Under the **Body** tab, select **form-data**.
3. Add a key `prompt` (type `Text`) with your instruction.
4. Add one or more keys named `attachments` (type `File`) and choose local files to upload. Postman will automatically send all with the same key.
5. Ensure no additional headers are required; Postman sets multipart boundaries automatically.
6. Send the request and inspect the JSON response for the analysis and token usage.

## Development Notes
- Temporary files are stored in the operating system's temp directory and are deleted after each request.
- The service cleans up uploaded files from OpenAI once the analysis completes.

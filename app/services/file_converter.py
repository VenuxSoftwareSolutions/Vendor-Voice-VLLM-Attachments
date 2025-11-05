import io
import os
import tempfile
import subprocess
from fastapi import HTTPException, status
from PIL import Image, UnidentifiedImageError
from app.core.logger import logger

def _docx2pdf_available() -> bool:
    try:
        import docx2pdf  # noqa
        return True
    except ImportError:
        return False

def _soffice_available() -> bool:
    from shutil import which
    return which("soffice") is not None

def convert_docx_to_pdf_bytes(data: bytes, filename: str) -> bytes:
    logger.info(f"Converting DOCX file: {filename}")
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp_docx:
        tmp_docx.write(data)
        tmp_docx.flush()
        tmp_docx_path = tmp_docx.name

    tmp_outdir = tempfile.mkdtemp()
    pdf_path = os.path.join(tmp_outdir, os.path.basename(tmp_docx_path).replace(".docx", ".pdf"))

    try:
        if _docx2pdf_available() and os.name in ("nt", "mac"):
            from docx2pdf import convert
            convert(tmp_docx_path, pdf_path)
        elif _soffice_available():
            cmd = ["soffice", "--headless", "--convert-to", "pdf", "--outdir", tmp_outdir, tmp_docx_path]
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            raise HTTPException(status_code=501, detail="No DOCX converter found. Install LibreOffice or docx2pdf.")

        with open(pdf_path, "rb") as f:
            pdf_data = f.read()
        logger.info(f"DOCX converted successfully: {filename}")
        return pdf_data

    except Exception as e:
        logger.error(f"DOCX conversion failed for {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"DOCX→PDF conversion failed for {filename}: {e}")
    finally:
        try:
            os.remove(tmp_docx_path)
        except Exception:
            pass

def convert_to_pdf_bytes(data: bytes, filename: str, mime: str) -> tuple[str, bytes]:
    if mime == "application/pdf" or filename.lower().endswith(".pdf"):
        return filename, data

    if mime.startswith("image/"):
        try:
            with Image.open(io.BytesIO(data)) as im:
                if im.mode in ("RGBA", "LA", "P"):
                    bg = Image.new("RGB", im.size, (255, 255, 255))
                    bg.paste(im.convert("RGBA"), mask=im.convert("RGBA").split()[-1] if im.mode in ("RGBA", "LA") else None)
                    frame = bg
                else:
                    frame = im.convert("RGB")

                buf = io.BytesIO()
                frame.save(buf, format="PDF", resolution=300.0)
                pdf_bytes = buf.getvalue()
            logger.info(f"Image converted to PDF: {filename}")
            return f"{filename.rsplit('.', 1)[0]}.pdf", pdf_bytes
        except UnidentifiedImageError:
            raise HTTPException(status_code=400, detail=f"Invalid image file: {filename}")
        except Exception as e:
            logger.error(f"Image→PDF failed for {filename}: {e}")
            raise HTTPException(status_code=500, detail=f"Image→PDF failed for {filename}: {e}")

    if filename.lower().endswith(".docx"):
        pdf_bytes = convert_docx_to_pdf_bytes(data, filename)
        return f"{filename.rsplit('.', 1)[0]}.pdf", pdf_bytes

    raise HTTPException(status_code=415, detail=f"Unsupported file format: {filename}")

import os
import tempfile
import traceback
import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.speech import transcribe_file

log = logging.getLogger("medigraph.speech")
router = APIRouter(prefix="/speech", tags=["speech"])

ALLOWED = {
    "audio/webm", "audio/ogg", "audio/wav", "audio/x-wav",
    "audio/mp4", "audio/mpeg", "audio/m4a", "video/webm",
}

@router.post("/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    language: str | None = Form(None),
):
    log.info("incoming file: name=%r content_type=%r language=%r",
             file.filename, file.content_type, language)

    if file.content_type and file.content_type not in ALLOWED:
        raise HTTPException(415, f"unsupported content-type: {file.content_type}")

    lang = None
    if language in ("en", "hi"):
        lang = language

    raw = await file.read()
    log.info("received %d bytes", len(raw))
    if len(raw) < 1000:
        raise HTTPException(400, f"audio too small ({len(raw)} bytes)")

    suffix = ".webm"
    if file.filename and "." in file.filename:
        suffix = "." + file.filename.rsplit(".", 1)[-1]

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(raw)
            tmp_path = tmp.name
        log.info("wrote temp file %s (%d bytes)", tmp_path, len(raw))
        result = transcribe_file(tmp_path, language=lang)
        log.info("transcribed: %r confidence=%.3f lang=%s",
                 result.get("text"), result.get("confidence", 0.0), result.get("language"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        log.error("transcription failed: %s", e)
        log.error(traceback.format_exc())
        raise HTTPException(500, f"transcription failed: {type(e).__name__}: {e}")
    finally:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
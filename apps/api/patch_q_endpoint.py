from pathlib import Path

tsx = r'''
from fastapi import APIRouter, HTTPException, Query
from app.data.questionnaire_gm import REGISTRY

router = APIRouter(prefix="/questionnaires", tags=["questionnaires"])


@router.get("/{questionnaire_id}")
def get_questionnaire(
    questionnaire_id: str,
    lang: str = Query("en", pattern="^(en|hi)$"),
    mode: str = Query("full", pattern="^(full|brief|returning)$"),
):
    """Return a questionnaire.

    - id `gm_v1` with mode `full`   -> everything
    - id `gm_v1` with mode `brief`  -> 10 questions (first-time)
    - id `gm_v1` with mode `returning` -> 5 questions (follow-up)
    """
    if questionnaire_id == "gm_v1":
        key = {
            "full": "gm_v1",
            "brief": "gm_v1_brief",
            "returning": "gm_v1_returning",
        }[mode]
    else:
        key = questionnaire_id

    q = REGISTRY.get(key)
    if not q:
        raise HTTPException(404, "questionnaire not found")
    return {
        "id": q["id"],
        "name": q[f"name_{lang}"],
        "language": lang,
        "mode": mode,
        "sections": q["sections"],
    }
'''

out = Path("app/api/v1/questionnaires.py")
out.write_text(tsx.lstrip(), encoding="utf-8")
print("WROTE", out)
print("bytes:", out.stat().st_size)

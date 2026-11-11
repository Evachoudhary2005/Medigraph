"""Document intelligence: OpenCV preprocessing, PaddleOCR, type classification.

PaddleOCR is initialized lazily per-language and cached for the process lifetime.
Handles both PaddleOCR 2.x (ocr()) and 3.x (predict()) result shapes.
"""
from __future__ import annotations

import logging
from typing import Optional

import cv2
import numpy as np

log = logging.getLogger("medigraph.document")

_ocr_instances: dict = {}


def _get_ocr(lang: str = "en"):
    if lang not in _ocr_instances:
        from paddleocr import PaddleOCR
        # PaddleOCR 3.x constructor
        try:
            ocr = PaddleOCR(
                lang=lang,
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
            )
        except TypeError:
            # Older 2.x API fallback
            ocr = PaddleOCR(lang=lang, use_angle_cls=True, show_log=False)
        _ocr_instances[lang] = ocr
    return _ocr_instances[lang]


def preprocess(image_path: str) -> np.ndarray:
    """Grayscale, denoise, adaptive threshold. Returns the processed image."""
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Cannot read image: {image_path}")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, h=10)
    thresh = cv2.adaptiveThreshold(
        denoised, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 31, 2,
    )
    return thresh


def _poly_to_list(poly) -> list:
    try:
        arr = np.asarray(poly).tolist()
        return [[float(x), float(y)] for x, y in arr]
    except Exception:
        return []


def _normalize_result(result) -> list:
    """Normalize both 2.x and 3.x PaddleOCR outputs to [{text, confidence, bbox}]."""
    items: list = []
    if result is None:
        return items

    # PaddleOCR 3.x: list of OCRResult (dict-like) with rec_texts/rec_scores/rec_polys
    if isinstance(result, list) and result and hasattr(result[0], "get"):
        for page in result:
            texts = page.get("rec_texts") or []
            scores = page.get("rec_scores") or []
            polys = page.get("rec_polys") or page.get("dt_polys") or []
            for i, txt in enumerate(texts):
                items.append({
                    "text": str(txt),
                    "confidence": float(scores[i]) if i < len(scores) else 0.0,
                    "bbox": _poly_to_list(polys[i]) if i < len(polys) else [],
                })
        return items

    # PaddleOCR 2.x: [[[bbox, (text, conf)], ...], ...]
    if isinstance(result, list):
        for page in result:
            if not page:
                continue
            for line in page:
                try:
                    bbox, (text, conf) = line[0], line[1]
                    items.append({
                        "text": str(text),
                        "confidence": float(conf),
                        "bbox": bbox,
                    })
                except Exception:
                    continue
    return items


def run_ocr(image_path: str, lang: str = "en") -> list:
    ocr = _get_ocr(lang)
    if hasattr(ocr, "predict"):
        try:
            result = ocr.predict(image_path)
        except Exception as e:
            log.warning("predict() failed (%s); falling back to ocr()", e)
            result = ocr.ocr(image_path)
    else:
        result = ocr.ocr(image_path)
    return _normalize_result(result)


_CLASSIFIER_KEYWORDS = {
    "prescription": [
        "prescription", "rx", "tab.", "tab ", "-t ", "cap.", "cap ", "-c ",
        "inj.", "syp.", "syrup", "dose", "dosage", "once daily", "twice daily",
        "bd", "tds", "od", "hs", "mg", "mcg", "before food", "after food",
        "prescribed", "complaint",
    ],
    "lab_report": [
        "hb", "hemoglobin", "wbc", "rbc", "platelet", "esr",
        "mg/dl", "mmol/l", "g/dl", "cells/cumm", "reference range",
        "normal range", "lab report", "test name", "creatinine",
        "urea", "sgot", "sgpt", "fasting", "post prandial",
    ],
    "discharge_summary": [
        "discharge", "admitted", "admission", "diagnosis", "advised",
        "follow up", "follow-up", "discharged on", "course in hospital",
        "condition at discharge",
    ],
}


def classify(text: str) -> str:
    t = (text or "").lower()
    scores = {k: 0 for k in _CLASSIFIER_KEYWORDS}
    for label, kws in _CLASSIFIER_KEYWORDS.items():
        for kw in kws:
            if kw in t:
                scores[label] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "other"

def _render_pdf_pages(pdf_path: str, scale: float = 2.5):
    """Render each PDF page to a numpy BGR array using pypdfium2."""
    import numpy as _np
    import pypdfium2 as _pdfium

    pdf = _pdfium.PdfDocument(pdf_path)
    try:
        for page in pdf:
            pil_image = page.render(scale=scale).to_pil().convert("RGB")
            arr = _np.array(pil_image)
            bgr = arr[:, :, ::-1].copy()
            yield bgr
    finally:
        pdf.close()


def ocr_pdf(pdf_path: str, lang: str = "en") -> list:
    """OCR every page of a PDF using pypdfium2 + PaddleOCR."""
    import cv2 as _cv2
    import os as _os

    all_regions: list = []
    for idx, img in enumerate(_render_pdf_pages(pdf_path), start=1):
        tmp_path = pdf_path + f".page{idx}.png"
        _cv2.imwrite(tmp_path, img)
        try:
            regions = run_ocr(tmp_path, lang=lang)
            for r in regions:
                r["page"] = idx
            all_regions.extend(regions)
        finally:
            try:
                _os.unlink(tmp_path)
            except OSError:
                pass
    return all_regions


def _render_pdf_pages(pdf_path: str, scale: float = 2.5):
    """Render each PDF page to a numpy BGR array using pypdfium2."""
    import numpy as _np
    import pypdfium2 as _pdfium

    pdf = _pdfium.PdfDocument(pdf_path)
    try:
        for page in pdf:
            pil_image = page.render(scale=scale).to_pil().convert("RGB")
            arr = _np.array(pil_image)
            bgr = arr[:, :, ::-1].copy()
            yield bgr
    finally:
        pdf.close()


def ocr_pdf(pdf_path: str, lang: str = "en") -> list:
    """OCR every page of a PDF using pypdfium2 + PaddleOCR."""
    import cv2 as _cv2
    import os as _os

    all_regions: list = []
    for idx, img in enumerate(_render_pdf_pages(pdf_path), start=1):
        tmp_path = pdf_path + f".page{idx}.png"
        _cv2.imwrite(tmp_path, img)
        try:
            regions = run_ocr(tmp_path, lang=lang)
            for r in regions:
                r["page"] = idx
            all_regions.extend(regions)
        finally:
            try:
                _os.unlink(tmp_path)
            except OSError:
                pass
    return all_regions

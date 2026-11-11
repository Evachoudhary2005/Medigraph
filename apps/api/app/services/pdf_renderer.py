"""Render a clinical summary to PDF using reportlab.

Input: a sections list from the summary builder + patient metadata.
Output: bytes of a PDF file.
"""
from __future__ import annotations

import io
from datetime import datetime
from typing import Any

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)


def _escape(text: str) -> str:
    """Escape HTML-ish chars so reportlab's Paragraph parser doesn't choke."""
    if text is None:
        return ""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def build_summary_pdf(
    patient_id: str,
    patient_label: str,
    sections: list[dict],
    alerts: list[dict] | None = None,
    generated_by: str = "clinician",
) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
        title="Clinical Summary",
        author="MediGraph",
    )

    styles = getSampleStyleSheet()
    title = ParagraphStyle("TitleX", parent=styles["Title"], fontSize=20,
                           spaceAfter=4, textColor=colors.HexColor("#0f172a"))
    sub = ParagraphStyle("SubX", parent=styles["Normal"], fontSize=9,
                         textColor=colors.HexColor("#475569"), spaceAfter=14)
    h2 = ParagraphStyle("H2X", parent=styles["Heading2"], fontSize=12,
                        textColor=colors.HexColor("#0f172a"),
                        spaceBefore=14, spaceAfter=6)
    body = ParagraphStyle("BodyX", parent=styles["Normal"], fontSize=10,
                          leading=14, spaceAfter=4)
    meta = ParagraphStyle("MetaX", parent=styles["Normal"], fontSize=8,
                          textColor=colors.HexColor("#64748b"), spaceAfter=2)
    warn = ParagraphStyle("WarnX", parent=styles["Normal"], fontSize=8,
                          textColor=colors.HexColor("#b45309"), spaceAfter=2)

    story: list[Any] = []

    # Header
    story.append(Paragraph("Clinical Summary Draft", title))
    story.append(Paragraph(
        f"Patient: <b>{_escape(patient_label)}</b> &nbsp;|&nbsp; "
        f"ID: <font face='Courier'>{_escape(patient_id)}</font> &nbsp;|&nbsp; "
        f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')} "
        f"by {_escape(generated_by)}",
        sub,
    ))

    # Urgent alerts banner
    urgent = [a for a in (alerts or []) if a.get("severity") == "urgent"]
    if urgent:
        for a in urgent:
            story.append(Paragraph(
                f"<b><font color='#991b1b'>URGENT: {_escape(a.get('name', ''))}</font></b>",
                h2,
            ))
            story.append(Paragraph(_escape(a.get("description", "")), body))
            story.append(Paragraph(
                _escape(a.get("source_hint", "")), meta,
            ))
            for ev in a.get("evidence", []):
                story.append(Paragraph(
                    f"  - {_escape(str(ev.get('label', '')))}: "
                    f"{_escape(str(ev.get('value', '')))}",
                    meta,
                ))

    # Sections
    for sec in sections:
        items = sec.get("items", [])
        if not items:
            continue
        story.append(Paragraph(_escape(sec.get("title", "")), h2))

        table_data: list[list[Any]] = [["Statement", "Source", "Confidence", "Status"]]
        for it in items:
            text = _escape(it.get("text", ""))
            src = _escape(it.get("source", "")).upper()
            conf = it.get("confidence", 0.0)
            status = it.get("verification_status", "pending")
            table_data.append([
                Paragraph(text, body),
                Paragraph(src, meta),
                Paragraph(f"{conf:.2f}", meta),
                Paragraph(_escape(status), meta),
            ])

        t = Table(table_data, colWidths=[10 * cm, 2 * cm, 2.2 * cm, 2.5 * cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#334155")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.HexColor("#e2e8f0")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(t)

    # Warnings
    warnings: list[str] = []
    for sec in sections:
        for it in sec.get("items", []):
            for w in it.get("warnings", []) or []:
                warnings.append(f"{it.get('text', '')} - {w}")
    if warnings:
        story.append(Paragraph("Warnings", h2))
        for w in warnings:
            story.append(Paragraph("- " + _escape(w), warn))

    # Footer
    story.append(Spacer(1, 20))
    story.append(Paragraph(
        "Generated by MediGraph. Local-only AI. "
        "All facts require clinician verification before clinical use.",
        meta,
    ))

    doc.build(story)
    return buf.getvalue()
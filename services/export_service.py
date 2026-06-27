"""
services/export_service.py — Generate Excel and PDF attendance reports.
"""

import os
import io
from datetime import date, datetime
import pandas as pd
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import cm
from flask import current_app
from models import Attendance, Student, Subject, Teacher


def _build_dataframe(records):
    """Convert a list of Attendance ORM objects into a pandas DataFrame."""
    rows = []
    for r in records:
        rows.append({
            "Date": r.date.strftime("%Y-%m-%d"),
            "Time": r.time.strftime("%H:%M:%S"),
            "Student ID": r.student.student_id,
            "Student Name": r.student.name,
            "Class": r.student.class_name,
            "Roll No": r.student.roll_no,
            "Subject": r.subject.subject_name,
            "Subject Code": r.subject.subject_code,
            "Status": r.status.capitalize(),
            "Method": r.method.replace("_", " ").title(),
            "Teacher": r.teacher.name if r.teacher else "—",
        })
    return pd.DataFrame(rows)


def export_excel(records, filename_prefix="attendance") -> str:
    """Write an XLSX file to EXPORTS_DIR and return its path."""
    export_dir = current_app.config["EXPORTS_DIR"]
    os.makedirs(export_dir, exist_ok=True)

    df = _build_dataframe(records)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(export_dir, f"{filename_prefix}_{timestamp}.xlsx")

    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Attendance")
        ws = writer.sheets["Attendance"]
        # Auto-size columns
        for col in ws.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            ws.column_dimensions[col[0].column_letter].width = max_len + 4

    return path


def export_pdf(records, title="Attendance Report", filename_prefix="attendance") -> str:
    """Write a PDF report to EXPORTS_DIR and return its path."""
    export_dir = current_app.config["EXPORTS_DIR"]
    os.makedirs(export_dir, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(export_dir, f"{filename_prefix}_{timestamp}.pdf")

    doc = SimpleDocTemplate(
        path,
        pagesize=landscape(A4),
        rightMargin=1 * cm,
        leftMargin=1 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1 * cm,
    )

    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph(title, styles["Title"]))
    story.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%d %B %Y, %H:%M UTC')}", styles["Normal"]))
    story.append(Spacer(1, 0.5 * cm))

    # Table data
    df = _build_dataframe(records)
    headers = list(df.columns)
    data = [headers] + df.values.tolist()

    tbl = Table(data, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4f8")]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(tbl)

    doc.build(story)
    return path

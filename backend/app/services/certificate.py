from __future__ import annotations

import secrets
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas

# Root directory for generated certificate PDFs
CERT_ROOT = Path("media/certificates")


def _format_completion_date(completion_date: Optional[datetime | str]) -> str:
    if completion_date is None:
        return datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")

    if isinstance(completion_date, datetime):
        return completion_date.astimezone(timezone.utc).strftime("%Y-%m-%d")

    normalized = str(completion_date).strip()
    if not normalized:
        return datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    return normalized


def is_valid_pdf_file(path: Path) -> bool:
    """Return True when *path* looks like a valid PDF file."""
    if not path.exists() or not path.is_file():
        return False

    try:
        raw = path.read_bytes()
    except OSError:
        return False

    if len(raw) < 32:
        return False

    # Minimal structure checks: header marker and EOF marker.
    return raw.startswith(b"%PDF-") and b"%%EOF" in raw[-2048:]


def generate_verification_code(length: int = 12) -> str:
    """Return a cryptographically random uppercase alphanumeric code.

    Example output: ``"A3FG9XKL2QPT"``
    """
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_certificate_pdf(
    student_name: str,
    workshop_title: str,
    verification_code: str,
    completion_date: Optional[datetime | str] = None,
    certificate_id: Optional[str] = None,
) -> str:
    """Generate a real PDF certificate and return the relative file path.

    Args:
        student_name: Full name of the student.
        workshop_title: Title of the completed workshop.
        verification_code: Short code printed on the certificate.
        completion_date: Completion date to print on certificate.
        certificate_id: Optional UUID to use as filename; generated if omitted.

    Returns:
        Relative path to the (mock) PDF file, e.g.
        ``"media/certificates/<id>.pdf"``.
    """
    CERT_ROOT.mkdir(parents=True, exist_ok=True)

    cert_id = certificate_id or str(uuid.uuid4())
    dest_path = CERT_ROOT / f"{cert_id}.pdf"

    display_date = _format_completion_date(completion_date)

    cert_canvas = canvas.Canvas(str(dest_path), pagesize=landscape(A4))
    width, height = landscape(A4)

    cert_canvas.setTitle("Certificate of Completion")
    cert_canvas.setAuthor("EduFlow")
    cert_canvas.setSubject("Course Completion Certificate")

    cert_canvas.setLineWidth(3)
    cert_canvas.rect(30, 30, width - 60, height - 60)

    cert_canvas.setFont("Helvetica-Bold", 30)
    cert_canvas.drawCentredString(width / 2, height - 130, "Certificate of Completion")

    cert_canvas.setFont("Helvetica", 16)
    cert_canvas.drawCentredString(width / 2, height - 175, "This certifies that")

    cert_canvas.setFont("Helvetica-Bold", 26)
    cert_canvas.drawCentredString(width / 2, height - 225, student_name)

    cert_canvas.setFont("Helvetica", 16)
    cert_canvas.drawCentredString(width / 2, height - 265, "has successfully completed")

    cert_canvas.setFont("Helvetica-Bold", 22)
    cert_canvas.drawCentredString(width / 2, height - 305, workshop_title)

    cert_canvas.setFont("Helvetica", 14)
    cert_canvas.drawCentredString(width / 2, height - 350, f"Completion Date: {display_date}")
    cert_canvas.drawCentredString(width / 2, height - 375, f"Verification Code: {verification_code}")

    cert_canvas.setFont("Helvetica-Oblique", 11)
    cert_canvas.drawCentredString(width / 2, 55, "Issued by EduFlow")

    cert_canvas.showPage()
    cert_canvas.save()

    return str(dest_path).replace("\\", "/")

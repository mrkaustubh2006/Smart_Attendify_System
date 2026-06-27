"""
services/qr_service.py — Generates and stores static QR codes for students.
The QR payload is ONLY the opaque qr_token — never PII.
"""

import os
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from PIL import Image, ImageDraw, ImageFont
from flask import current_app


def generate_student_qr(student) -> str:
    """
    Generate a PNG QR code for the given student and save it to disk.
    Returns the relative path (relative to app root) so it can be stored in DB.
    """
    qr_dir = current_app.config["QR_CODES_DIR"]
    os.makedirs(qr_dir, exist_ok=True)

    filename = f"qr_{student.student_id}.png"
    filepath = os.path.join(qr_dir, filename)

    # Build QR image — payload is ONLY the secure token
    qr = qrcode.QRCode(
        version=3,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=12,
        border=4,
    )
    qr.add_data(student.qr_token)
    qr.make(fit=True)

    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        fill_color="#1e3a5f",
        back_color="white",
    )
    img = img.convert("RGB")

    # Add a small label below the QR
    label_height = 40
    final = Image.new("RGB", (img.width, img.height + label_height), "white")
    final.paste(img, (0, 0))

    draw = ImageDraw.Draw(final)
    label = f"{student.name}  |  {student.student_id}"
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    except OSError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), label, font=font)
    text_w = bbox[2] - bbox[0]
    x = (final.width - text_w) // 2
    draw.text((x, img.height + 8), label, fill="#1e3a5f", font=font)

    final.save(filepath, "PNG", quality=95)
    return os.path.join("qr_codes", filename)   # Relative path for DB storage

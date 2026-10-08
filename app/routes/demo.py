"""Synthetic-data-only demo routes. These never read or write patient data."""

import io

import qrcode
from flask import Blueprint, current_app, make_response, render_template, request, send_file

demo_bp = Blueprint("demo", __name__, url_prefix="/demo")

# Explicitly fabricated values: no real patient identity, contact details, or
# treatment instructions. Keep the route independent of the patient database.
DEMO_RECORD = {
    "display_name": "Synthetic patient profile",
    "allergies": "Synthetic example: penicillin allergy",
    "medications": [
        "Synthetic example: anticoagulant use",
        "Synthetic example: insulin use",
    ],
    "emergency_contact": "Demo contact — no real phone number",
    "provenance": "Fabricated for demonstration; not verified",
    "freshness": "Demo fixture; not a real patient update date",
}


def _no_store(response):
    """Avoid browser/proxy caching of the demo record page."""
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["X-Robots-Tag"] = "noindex, nofollow, noarchive"
    return response


@demo_bp.get("/")
def home():
    response = make_response(render_template("demo/landing.html"))
    return _no_store(response)


@demo_bp.get("/qr.png")
def qr_image():
    base_url = current_app.config.get("BASE_URL", "").rstrip("/")
    site_root = base_url or request.host_url.rstrip("/")
    record_url = f"{site_root}{current_app.config.get('APPLICATION_ROOT', '').rstrip('/')}/demo/record"

    image = qrcode.make(record_url)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    response = make_response(send_file(buffer, mimetype="image/png", max_age=0))
    return _no_store(response)


@demo_bp.get("/record")
def record():
    response = make_response(render_template("demo/record.html", record=DEMO_RECORD))
    return _no_store(response)

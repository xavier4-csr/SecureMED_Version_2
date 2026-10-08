"""
patient.py — Patient-facing Flask routes.

Endpoints:
  GET  /register        -> render registration form
  POST /register        -> full crypto pipeline, save to DB, redirect to dashboard
  GET  /qr/<qr_id>      -> serve QR code as PNG image
  GET  /dashboard       -> patient's QR code + recent access log
  GET  /logout          -> clear session
"""

import uuid
import json
import io

import bcrypt
import qrcode
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, send_file, flash, current_app
)

from app.utils.crypto   import generate_salt, derive_key, encrypt
from app.utils.hashing  import hash_record
from app.utils.otp      import generate_totp_secret
from app.utils.db       import insert_patient, get_patient, get_access_logs

patient_bp = Blueprint("patient", __name__)


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

@patient_bp.route("/register", methods=["GET"])
def register_form():
    return render_template("patient/register.html")


@patient_bp.route("/register", methods=["POST"])
def register_submit():
    # --- 1. Collect fields ---
    full_name       = request.form.get("full_name",       "").strip()
    blood_type      = request.form.get("blood_type",      "").strip()
    allergies       = request.form.get("allergies",       "").strip()
    conditions      = request.form.get("conditions",      "").strip()
    medications     = request.form.get("medications",     "").strip()
    emergency_name  = request.form.get("emergency_name",  "").strip()
    emergency_phone = request.form.get("emergency_phone", "").strip()
    password        = request.form.get("password",        "")
    confirm         = request.form.get("confirm_password","")

    # --- Validation ---
    errors = []
    if not full_name:        errors.append("Full name is required.")
    if not blood_type:       errors.append("Blood type is required.")
    if not emergency_name:   errors.append("Emergency contact name is required.")
    if not emergency_phone:  errors.append("Emergency contact phone is required.")
    if len(password) < 8:    errors.append("Password must be at least 8 characters.")
    if password != confirm:  errors.append("Passwords do not match.")

    if errors:
        for e in errors:
            flash(e, "error")
        return render_template("patient/register.html"), 400

    # --- 2. Hash password ---
    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(rounds=12)
    ).decode("utf-8")

    # --- 3. Assemble medical record ---
    record = {
        "full_name":       full_name,
        "blood_type":      blood_type,
        "allergies":       allergies,
        "conditions":      conditions,
        "medications":     medications,
        "emergency_name":  emergency_name,
        "emergency_phone": emergency_phone,
    }
    plaintext = json.dumps(record, ensure_ascii=False)

    # --- 4. Hash the plaintext record ---
    data_hash = hash_record(plaintext)

    # --- 5. Derive encryption key ---
    qr_id = str(uuid.uuid4())
    salt  = generate_salt()
    key   = derive_key(qr_id, salt)

    # --- 6. Encrypt ---
    encrypted = encrypt(plaintext, key)

    # --- 7. TOTP secret ---
    totp_secret = generate_totp_secret()

    # --- 8. Save to DB ---
    try:
        insert_patient(
            qr_id          = qr_id,
            encrypted_data = encrypted["ciphertext"],
            iv             = encrypted["iv"],
            gcm_tag        = encrypted["gcm_tag"],
            data_hash      = data_hash,
            salt           = salt,
            totp_secret    = totp_secret,
            password_hash  = password_hash,
        )
    except Exception as e:
        flash("Registration failed. Please try again.", "error")
        return render_template("patient/register.html"), 500

    # --- 9. Session + redirect ---
    session.clear()
    session["qr_id"]     = qr_id
    session["full_name"] = full_name
    session["role"]      = "patient"

    flash("Registration successful! Here is your QR code.", "success")
    return redirect(url_for("patient.dashboard"))


# ---------------------------------------------------------------------------
# QR Code image — uses BASE_URL config for LAN / mobile access
# ---------------------------------------------------------------------------

@patient_bp.route("/qr/<qr_id>")
def qr_image(qr_id):
    """
    Generate and serve a QR code PNG.
    Encodes the full /scan/<qr_id> URL.
    Uses BASE_URL from app config (settable via .env) if available,
    so QR codes work when scanned from a phone on the same Wi-Fi.
    """
    base_url = current_app.config.get("BASE_URL", "")
    if base_url:
        scan_url = f"{base_url}/scan/{qr_id}"
    else:
        scan_url = f"{request.host_url.rstrip('/')}/scan/{qr_id}"

    img = qrcode.make(scan_url)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    return send_file(buf, mimetype="image/png")


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@patient_bp.route("/dashboard")
def dashboard():
    if session.get("role") != "patient":
        flash("Please register to view your dashboard.", "error")
        return redirect(url_for("patient.register_form"))

    qr_id     = session["qr_id"]
    full_name = session.get("full_name", "")
    logs      = get_access_logs(qr_id, limit=10)

    return render_template(
        "patient/dashboard.html",
        qr_id     = qr_id,
        full_name = full_name,
        logs      = logs,
    )


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------

@patient_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("patient.register_form"))

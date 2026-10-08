"""
responder.py — Emergency access routes for first responders.

Endpoints:
  GET  /scan/<qr_id>    -> look up patient, generate OTP, display it
  POST /verify/<qr_id>  -> validate OTP, decrypt, verify hash, open session
  GET  /view/<qr_id>    -> show decrypted critical info (session-gated)
"""

import json
from datetime import datetime, timedelta

from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, flash
)
from cryptography.exceptions import InvalidTag

from app import limiter
from app.utils.crypto   import derive_key, decrypt
from app.utils.hashing  import verify_hash
from app.utils.otp      import generate_otp, verify_otp
from app.utils.db       import get_patient, log_access

responder_bp = Blueprint("responder", __name__)

SESSION_DURATION = 10  # minutes


def _get_responder_ip():
    return request.headers.get("X-Forwarded-For", request.remote_addr)


# ---------------------------------------------------------------------------
# Step 1 — Scan QR -> show OTP
# ---------------------------------------------------------------------------

@responder_bp.route("/scan/<qr_id>")
@limiter.limit("20 per minute")
def scan(qr_id):
    patient = get_patient(qr_id)

    if not patient:
        flash("QR code not recognised. This profile may not exist.", "error")
        return render_template("responder/scan.html", found=False), 404

    otp_code = generate_otp(patient["totp_secret"])

    log_access(
        patient_qr_id  = qr_id,
        responder_ip   = _get_responder_ip(),
        success        = False,
        failure_reason = "otp_pending"
    )

    return render_template(
        "responder/scan.html",
        found    = True,
        qr_id    = qr_id,
        otp_code = otp_code,
    )


# ---------------------------------------------------------------------------
# Step 2 — Submit OTP -> decrypt and verify
# ---------------------------------------------------------------------------

@responder_bp.route("/verify/<qr_id>", methods=["POST"])
@limiter.limit("5 per minute")
def verify(qr_id):
    ip        = _get_responder_ip()
    submitted = request.form.get("otp_code", "").strip()
    patient   = get_patient(qr_id)

    if not patient:
        flash("Invalid QR code.", "error")
        return redirect(url_for("responder.scan", qr_id=qr_id))

    # --- Validate OTP ---
    if not verify_otp(patient["totp_secret"], submitted):
        log_access(qr_id, ip, success=False, failure_reason="invalid_otp")
        flash("Incorrect or expired code. Please try again.", "error")
        return redirect(url_for("responder.scan", qr_id=qr_id))

    # --- Derive AES key ---
    try:
        key = derive_key(qr_id, bytes(patient["salt"]))
    except Exception:
        log_access(qr_id, ip, success=False, failure_reason="key_derivation_error")
        flash("Internal security error. Access denied.", "error")
        return redirect(url_for("responder.scan", qr_id=qr_id))
    # --- Decrypt record ---
    try:
        plaintext = decrypt(
            iv         = bytes(patient["iv"]),
            ciphertext = bytes(patient["encrypted_data"]),
            gcm_tag    = bytes(patient["gcm_tag"]),
            key        = key,
        )
    except InvalidTag:
        log_access(qr_id, ip, success=False, failure_reason="decryption_failed")
        flash("Data integrity check failed. Record may be compromised.", "error")
        return redirect(url_for("responder.scan", qr_id=qr_id))

    # --- Verify SHA-256 hash ---
    if not verify_hash(plaintext, patient["data_hash"]):
        log_access(qr_id, ip, success=False, failure_reason="hash_mismatch")
        flash("Record integrity check failed. Do not trust this data.", "error")
        return redirect(url_for("responder.scan", qr_id=qr_id))

    # --- All checks passed — open session ---
    record  = json.loads(plaintext)
    expires = datetime.utcnow() + timedelta(minutes=SESSION_DURATION)

    session["responder_verified"] = True
    session["responder_qr_id"]    = qr_id
    session["responder_record"]   = record
    session["responder_expires"]  = expires.isoformat()

    log_access(qr_id, ip, success=True)

    return redirect(url_for("responder.view", qr_id=qr_id))


# ---------------------------------------------------------------------------
# Step 3 — View decrypted emergency info
# ---------------------------------------------------------------------------

@responder_bp.route("/view/<qr_id>")
def view(qr_id):
    if not session.get("responder_verified"):
        flash("Access denied. Please scan the QR code first.", "error")
        return redirect(url_for("responder.scan", qr_id=qr_id))

    if session.get("responder_qr_id") != qr_id:
        flash("Session mismatch. Please re-scan.", "error")
        return redirect(url_for("responder.scan", qr_id=qr_id))

    # --- Expiry check ---
    expires_str = session.get("responder_expires")
    if expires_str:
        expires = datetime.fromisoformat(expires_str)
        if datetime.utcnow() > expires:
            session.clear()
            flash("Session expired. Please re-scan and re-enter the code.", "error")
            return redirect(url_for("responder.scan", qr_id=qr_id))

    record = session.get("responder_record", {})

    return render_template(
        "responder/view.html",
        record          = record,
        qr_id           = qr_id,
        session_expires = expires_str,
    )

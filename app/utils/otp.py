"""
otp.py — TOTP one-time password generation and verification.

Uses RFC 6238 TOTP (same standard as Google Authenticator).
Each code is valid for 30 seconds. A window of ±1 step is allowed
to account for clock drift between server and device (~90 sec total).

Flow:
  1. At registration:  generate_totp_secret() -> store in totp_secret column
  2. At emergency scan: generate_otp(secret)  -> send this code to the responder
  3. On OTP submission: verify_otp(secret, code) -> True/False
"""

import pyotp


def generate_totp_secret() -> str:
    """
    Generate a cryptographically random base32 TOTP secret.
    Call once at patient registration and store in the totp_secret column.

    Returns:
        A 32-character base32 string (160 bits of entropy).
    """
    return pyotp.random_base32()


def generate_otp(secret: str) -> str:
    """
    Generate the current 6-digit TOTP code for a given secret.
    This is the code shown to or sent to the first responder.
    It changes every 30 seconds automatically.

    Args:
        secret: The base32 TOTP secret from the patients table.

    Returns:
        A 6-digit string e.g. '482910'
    """
    totp = pyotp.TOTP(secret)
    return totp.now()


def verify_otp(secret: str, code: str) -> bool:
    """
    Verify a 6-digit TOTP code against the patient's secret.
    valid_window=1 allows ±1 time step (±30 sec) to handle clock drift.

    Args:
        secret: The base32 TOTP secret from the patients table.
        code:   The 6-digit string entered by the first responder.

    Returns:
        True  — code is valid, proceed with decryption.
        False — code is wrong or expired, reject and log.
    """
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)


def get_otp_uri(secret: str, qr_id: str) -> str:
    """
    Generate an otpauth:// URI for use with authenticator apps.
    Optional — useful if you want to let responders use Google Authenticator
    instead of receiving the code via the system.

    Args:
        secret: The base32 TOTP secret.
        qr_id:  The patient's QR ID (used as the account label).

    Returns:
        An otpauth:// URI string.
    """
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(
        name=qr_id,
        issuer_name="SecureMed QR"
    )
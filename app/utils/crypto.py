"""
crypto.py — AES-256-GCM encryption and PBKDF2 key derivation.

Flow:
  1. derive_key(qr_id, salt)  -> 32-byte AES key via PBKDF2-HMAC-SHA256
  2. encrypt(plaintext, key)  -> dict with iv, ciphertext, gcm_tag (all bytes)
  3. decrypt(iv, ciphertext, gcm_tag, key) -> original plaintext string
"""

import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


# ---------------------------------------------------------------------------
# Key derivation
# ---------------------------------------------------------------------------

def derive_key(qr_id: str, salt: bytes) -> bytes:
    """
    Derive a 32-byte AES-256 key from the patient's QR ID + salt.
    Uses PBKDF2-HMAC-SHA256 with 600,000 iterations (NIST 2023 minimum).
    The key is NEVER stored — it is re-derived on every encrypt/decrypt call.

    Args:
        qr_id:  The patient's unique public QR identifier (string).
        salt:   A 32-byte random salt stored in the patients table.

    Returns:
        32 bytes suitable for use as an AES-256 key.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600_000,
    )
    return kdf.derive(qr_id.encode("utf-8"))


# ---------------------------------------------------------------------------
# Encryption
# ---------------------------------------------------------------------------

def encrypt(plaintext: str, key: bytes) -> dict:
    """
    Encrypt plaintext using AES-256-GCM.
    A fresh random 16-byte IV is generated for every call, meaning two
    encryptions of the same plaintext will always produce different ciphertext.

    Args:
        plaintext:  The patient's medical record as a JSON string.
        key:        32-byte AES key from derive_key().

    Returns:
        A dict with three bytes values:
          {
            'iv':         16 bytes  — initialisation vector
            'ciphertext': n  bytes  — encrypted data
            'gcm_tag':    16 bytes  — GCM authentication tag
          }
        Store all three as separate columns in the DB.
    """
    iv = os.urandom(16)
    aesgcm = AESGCM(key)

    # AESGCM.encrypt() returns ciphertext + 16-byte tag appended
    combined = aesgcm.encrypt(iv, plaintext.encode("utf-8"), None)

    # Split off the last 16 bytes as the GCM tag
    ciphertext = combined[:-16]
    gcm_tag    = combined[-16:]

    return {
        "iv":         iv,
        "ciphertext": ciphertext,
        "gcm_tag":    gcm_tag,
    }


# ---------------------------------------------------------------------------
# Decryption
# ---------------------------------------------------------------------------

def decrypt(iv: bytes, ciphertext: bytes, gcm_tag: bytes, key: bytes) -> str:
    """
    Decrypt an AES-256-GCM encrypted record.
    GCM authentication is built-in — if the ciphertext or tag has been
    tampered with, this will raise an InvalidTag exception before returning
    any data.

    Args:
        iv:         16-byte IV stored in the patients table.
        ciphertext: Encrypted data stored in the patients table.
        gcm_tag:    16-byte GCM tag stored in the patients table.
        key:        32-byte AES key from derive_key().

    Returns:
        Original plaintext string (the patient's medical record as JSON).

    Raises:
        cryptography.exceptions.InvalidTag — if decryption fails (tampered data
        or wrong key). Always catch this in your route and return 403.
    """
    aesgcm = AESGCM(key)

    # Re-combine ciphertext + tag before passing to decrypt
    combined = ciphertext + gcm_tag
    plaintext_bytes = aesgcm.decrypt(iv, combined, None)

    return plaintext_bytes.decode("utf-8")


# ---------------------------------------------------------------------------
# Salt generation (called once at registration)
# ---------------------------------------------------------------------------

def generate_salt() -> bytes:
    """Generate a cryptographically random 32-byte salt."""
    return os.urandom(32)
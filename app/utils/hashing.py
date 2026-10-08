"""
hashing.py — SHA-256 record integrity fingerprinting.

Flow:
  1. At registration:  hash_record(plaintext)  -> store the hex digest in DB
  2. After decryption: verify_hash(plaintext, stored_hash) -> must return True
                       If False, the record was tampered with — reject and alert.
"""

import hashlib
import hmac


def hash_record(plaintext: str) -> str:
    """
    Produce a SHA-256 hex digest of the patient's plaintext medical record.
    Call this BEFORE encrypting, and store the result in data_hash column.

    Args:
        plaintext: The patient's medical record as a JSON string.

    Returns:
        64-character lowercase hex string (SHA-256 digest).
    """
    return hashlib.sha256(plaintext.encode("utf-8")).hexdigest()


def verify_hash(plaintext: str, stored_hash: str) -> bool:
    """
    Recompute the SHA-256 hash of decrypted plaintext and compare it
    against the stored hash in constant time (prevents timing attacks).

    Call this AFTER decrypting. If it returns False:
      - Do NOT show the data to the responder
      - Log the anomaly
      - Return a 500/integrity error response

    Args:
        plaintext:   The decrypted medical record string.
        stored_hash: The hex digest stored in the data_hash DB column.

    Returns:
        True  — record is intact, safe to display.
        False — record has been tampered with, reject immediately.
    """
    recomputed = hashlib.sha256(plaintext.encode("utf-8")).hexdigest()

    # Use compare_digest to prevent timing-based attacks
    return hmac.compare_digest(recomputed, stored_hash)
import pytest
from app.utils.crypto import derive_key, encrypt, decrypt, generate_salt
from cryptography.exceptions import InvalidTag

def test_encrypt_decrypt_roundtrip():
    salt = generate_salt()
    key = derive_key("test-qr-id", salt)
    plaintext = '{"blood_type": "O+", "allergies": ["penicillin"]}'
    result = encrypt(plaintext, key)
    recovered = decrypt(result["iv"], result["ciphertext"], result["gcm_tag"], key)
    assert recovered == plaintext

def test_different_iv_each_encryption():
    salt = generate_salt()
    key = derive_key("test-qr-id", salt)
    plaintext = "same data"
    r1 = encrypt(plaintext, key)
    r2 = encrypt(plaintext, key)
    assert r1["iv"] != r2["iv"]
    assert r1["ciphertext"] != r2["ciphertext"]

def test_wrong_key_raises_error():
    salt = generate_salt()
    key = derive_key("correct-id", salt)
    wrong_key = derive_key("wrong-id", salt)
    plaintext = "sensitive data"
    result = encrypt(plaintext, key)
    with pytest.raises(Exception):
        decrypt(result["iv"], result["ciphertext"], result["gcm_tag"], wrong_key)

def test_same_inputs_same_key():
    salt = generate_salt()
    key1 = derive_key("patient-abc", salt)
    key2 = derive_key("patient-abc", salt)
    assert key1 == key2

def test_tampered_ciphertext_raises_error():
    salt = generate_salt()
    key = derive_key("test-qr-id", salt)
    result = encrypt("real data", key)
    tampered = bytes([result["ciphertext"][0] ^ 0xFF]) + result["ciphertext"][1:]
    with pytest.raises(Exception):
        decrypt(result["iv"], tampered, result["gcm_tag"], key)
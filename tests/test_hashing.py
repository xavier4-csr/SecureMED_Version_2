from app.utils.hashing import hash_record, verify_hash

def test_hash_returns_64_char_hex():
    h = hash_record("some medical data")
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)

def test_verify_hash_correct_data():
    plaintext = '{"blood_type": "A-", "allergies": []}'
    h = hash_record(plaintext)
    assert verify_hash(plaintext, h) is True

def test_verify_hash_tampered_data():
    plaintext = '{"blood_type": "A-", "allergies": []}'
    h = hash_record(plaintext)
    tampered = '{"blood_type": "B+", "allergies": []}'
    assert verify_hash(tampered, h) is False

def test_same_input_same_hash():
    data = "consistent record"
    assert hash_record(data) == hash_record(data)
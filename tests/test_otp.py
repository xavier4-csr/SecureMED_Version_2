from app.utils.otp import generate_totp_secret, generate_otp, verify_otp

def test_secret_is_base32():
    secret = generate_totp_secret()
    assert isinstance(secret, str)
    assert len(secret) == 32
    valid_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ234567")
    assert all(c in valid_chars for c in secret)

def test_otp_is_six_digits():
    secret = generate_totp_secret()
    code = generate_otp(secret)
    assert isinstance(code, str)
    assert len(code) == 6
    assert code.isdigit()

def test_verify_current_otp():
    secret = generate_totp_secret()
    code = generate_otp(secret)
    assert verify_otp(secret, code) is True

def test_verify_wrong_otp():
    secret = generate_totp_secret()
    assert verify_otp(secret, "000000") is False

def test_verify_wrong_secret():
    secret1 = generate_totp_secret()
    secret2 = generate_totp_secret()
    code = generate_otp(secret1)
    assert verify_otp(secret2, code) is False
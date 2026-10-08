"""
test_routes.py — End-to-end route tests for SecureMed QR.
Run: pytest tests/test_routes.py -v

These legacy-flow regression tests use Flask's test client and mocked
database/security helpers. They do not require a live patient database.
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"]   = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as client:
        yield client


# ---------------------------------------------------------------------------
# Patient routes
# ---------------------------------------------------------------------------

def test_register_page_loads(client):
    """GET /register returns 200."""
    r = client.get("/register")
    assert r.status_code == 200
    assert b"medical profile" in r.data.lower() or b"register" in r.data.lower()


def test_register_missing_fields(client):
    """POST /register with empty form returns 400."""
    r = client.post("/register", data={})
    assert r.status_code == 400


def test_register_password_mismatch(client):
    """POST /register with mismatched passwords returns 400."""
    r = client.post("/register", data={
        "full_name":       "Test Patient",
        "blood_type":      "O+",
        "allergies":       "",
        "conditions":      "",
        "medications":     "",
        "emergency_name":  "Jane Doe",
        "emergency_phone": "+254700000000",
        "password":        "password123",
        "confirm_password":"different456",
    })
    assert r.status_code == 400


def test_dashboard_requires_session(client):
    """GET /dashboard without session redirects."""
    r = client.get("/dashboard")
    assert r.status_code == 302
    assert "/register" in r.headers["Location"]


def test_qr_image_requires_valid_id(client):
    """GET /qr/<bad-id> returns 404 or valid PNG — just not a 500."""
    with patch("app.routes.patient.get_patient", return_value=None):
        r = client.get("/qr/nonexistent-id")
        # Should serve a QR regardless — it's just a URL, not a DB lookup
        assert r.status_code in (200, 404)
        assert r.status_code != 500


# ---------------------------------------------------------------------------
# Responder routes
# ---------------------------------------------------------------------------

def test_scan_unknown_qr(client):
    """GET /scan/<unknown> returns 404."""
    with patch("app.routes.responder.get_patient", return_value=None):
        r = client.get("/scan/unknown-qr-id")
        assert r.status_code == 404


def test_view_without_session_redirects(client):
    """GET /view/<id> without verified session redirects to scan."""
    r = client.get("/view/some-qr-id")
    assert r.status_code == 302
    assert "scan" in r.headers["Location"]


def test_verify_wrong_otp(client):
    """POST /verify/<id> with wrong OTP redirects back to scan."""
    mock_patient = {
        "totp_secret":    "JBSWY3DPEHPK3PXP",
        "salt":           b"\x00" * 32,
        "iv":             b"\x00" * 16,
        "encrypted_data": b"\x00" * 32,
        "gcm_tag":        b"\x00" * 16,
        "data_hash":      "a" * 64,
    }
    with patch("app.routes.responder.get_patient", return_value=mock_patient):
        with patch("app.routes.responder.verify_otp", return_value=False):
            with patch("app.routes.responder.log_access"):
                r = client.post("/verify/test-qr-id", data={"otp_code": "000000"})
                assert r.status_code == 302
                assert "scan" in r.headers["Location"]


def test_verify_correct_otp_flow(client):
    """POST /verify/<id> with correct OTP redirects to view."""
    mock_patient = {
        "totp_secret":    "JBSWY3DPEHPK3PXP",
        "salt":           b"\x00" * 32,
        "iv":             b"\x00" * 16,
        "encrypted_data": b"\x00" * 32,
        "gcm_tag":        b"\x00" * 16,
        "data_hash":      "abc123",
    }
    mock_record = json.dumps({
        "full_name": "Test Patient", "blood_type": "O+",
        "allergies": "None", "conditions": "None",
        "medications": "None", "emergency_name": "Jane",
        "emergency_phone": "0700000000"
    })
    with patch("app.routes.responder.get_patient", return_value=mock_patient):
        with patch("app.routes.responder.verify_otp",  return_value=True):
            with patch("app.routes.responder.derive_key", return_value=b"\x00" * 32):
                with patch("app.routes.responder.decrypt",  return_value=mock_record):
                    with patch("app.routes.responder.verify_hash", return_value=True):
                        with patch("app.routes.responder.log_access"):
                            r = client.post("/verify/test-qr-id", data={"otp_code": "123456"})
                            assert r.status_code == 302
                            assert "view" in r.headers["Location"]

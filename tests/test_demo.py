from app import create_app


def make_client():
    app = create_app()
    app.config.update(TESTING=True, SECRET_KEY="test-only-secret")
    return app.test_client()


def test_health_endpoint_is_minimal():
    response = make_client().get("/healthz")
    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == {"status": "ok"}


def test_home_redirects_to_demo():
    client = make_client()
    response = client.get("/")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/demo/")


def test_demo_landing_is_clearly_synthetic():
    response = make_client().get("/demo/")
    assert response.status_code == 200
    assert b"Synthetic-data prototype" in response.data
    assert b"does not verify who scans it" in response.data
    assert b"not a clinical service" in response.data
    assert response.headers["Cache-Control"].startswith("no-store")


def test_demo_qr_is_png_and_not_cached():
    response = make_client().get("/demo/qr.png")
    assert response.status_code == 200
    assert response.mimetype == "image/png"
    assert response.headers["Cache-Control"].startswith("no-store")


def test_record_prioritizes_allergy_and_meds_with_contact_secondary():
    response = make_client().get("/demo/record")
    body = response.data.decode("utf-8")
    assert response.status_code == 200
    assert "SYNTHETIC DEMO — NOT FOR MEDICAL CARE" in body
    assert "Synthetic example: penicillin allergy" in body
    assert "Synthetic example: anticoagulant use" in body
    assert "Synthetic example: insulin use" in body
    assert "Secondary — emergency contact" in body
    assert body.index("Key medication information") < body.index("Secondary — emergency contact")
    assert "blood type" not in body.lower()
    assert "no cached medical details" in body.lower()
    assert response.headers["Cache-Control"].startswith("no-store")
    assert response.headers["X-Robots-Tag"] == "noindex, nofollow, noarchive"


def test_legacy_patient_and_responder_routes_are_hidden_outside_tests():
    app = create_app()
    # App factory must leave testing disabled for this production-mode check.
    assert not app.testing
    client = app.test_client()
    assert client.get("/register").status_code == 404
    assert client.get("/scan/demo").status_code == 404
    assert client.get("/dashboard").status_code == 404

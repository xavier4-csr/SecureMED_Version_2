# SecureMed QR — V2 Presentation Demo

> **Status: synthetic-data demo only.** This prototype illustrates a QR-linked emergency-profile concept. It is not a clinical service, does not authenticate responders, and must not be used for care or with real patient information.

## Current experience

- `/` redirects to the demo landing page.
- `/demo/` introduces the synthetic scenario and displays a QR code.
- `/demo/record` presents fabricated allergy and medication examples, with emergency-contact context secondary.
- `/demo/qr.png` serves the QR image.
- `/healthz` returns a minimal liveness status for hosting health checks.
- Legacy database-backed patient and responder routes return 404 outside tests.

The demo is static: it does not initialize or connect to a patient database, and it does not require Neon, Redis, or user accounts. The profile is hard-coded synthetic content. The QR is a public locator, not proof of responder identity. If the service is unavailable, do not infer that the person has no allergies or medications; follow established emergency procedures.

## Run locally

Requires Python 3.11 or newer.

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python run.py
```

Open <http://localhost:5000/>. The local command uses Flask's development server; do not expose it as a public deployment. For a temporary phone test on the same network, set `BASE_URL` to a reachable address before generating the QR. Do not put real patient details or credentials in the demo.

## Tests

```bash
pytest -q
```

The test suite covers the demo landing/record/QR, the minimal health endpoint, no-cache response headers, and legacy-route blocking. It does not establish clinical safety or production readiness.

## Render demo deployment

The repository includes `render.yaml` for a low-cost synthetic demo web service:

1. Create a Render Web Service from this repository and use the Blueprint settings.
2. Keep `DEMO_MODE` enabled; the app currently sets it to `True`.
3. Let Render generate `SECRET_KEY`; set the canonical public origin as `BASE_URL` if needed.
4. Do not attach or configure a patient database or Redis for the current demo.
5. After deployment, test `/healthz`, `/demo/`, `/demo/record`, `/demo/qr.png`, and verify `/register` and `/scan/demo` return 404.

No Render deployment is currently implied by this repository. Verify the QR points to the intended HTTPS host before presenting it.

## Safety boundary

- Use fabricated values only; never upload, type, or demonstrate real patient or emergency-contact details.
- QR possession does not authenticate a paramedic or authorize access to real records.
- The demo gives no treatment recommendations and makes no legal, clinical, privacy-compliance, or availability claims.
- “Emergency doctrine applies” is an unverified project assumption, not a conclusion about Kenyan law or clinical policy.
- Any real-data pilot is a separate project gate requiring clinical, privacy/legal, security, identity, authorization, key-management, and operational review.

## Project map

```text
app/
  routes/        Flask routes: demo plus legacy routes blocked in demo mode
  templates/     landing, synthetic record, and historical prototype views
  utils/         legacy crypto/database/hash/OTP helpers (not used by demo routes)
docs/
  product-brief.md
  user-flows.md
  threat-model.md
  FAST_TRACK_PRESENTATION_ROADMAP.md
scripts/          local setup helper
 tests/           pytest suite
config.py         app configuration (demo mode remains on)
render.yaml       Render web-service blueprint; no database required
run.py            local entry point and Render external-host detection
```

## Working documents

- [Threat model](docs/threat-model.md)
- [Fast-track presentation roadmap](docs/FAST_TRACK_PRESENTATION_ROADMAP.md)
- [Product brief](docs/product-brief.md)
- [User flows](docs/user-flows.md)

The longer [production redesign roadmap](PRODUCTION_REDESIGN_ROADMAP.md) describes additional gates. Finishing a presentation demo does not make the system production-ready.

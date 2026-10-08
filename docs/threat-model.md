# SecureMed QR — Threat Model

**Status:** Initial engineering draft for the public synthetic-data demo

**Reviewed:** 2026-10-08

**Repository:** `xavier4-csr/SecureMED_Version_2`

**Scope:** Current Flask/Jinja demo on `main`, plus explicit gates for any future patient-data service.

> This is an engineering risk assessment, not a clinical, legal, privacy, or independent security review. The demo must use fabricated data only. It is not suitable for real patient information or emergency care.

## 1. Executive summary

The current demo serves a hard-coded synthetic record and QR image. It does not initialize or connect to the patient database in demo mode, does not accept patient-profile input in the demo flow, and does not authenticate QR viewers. The QR is a public locator for fabricated content—not proof of responder identity.

This sharply limits the impact of a direct patient-record breach **while the demo remains static and synthetic**. The most relevant current risks are:

1. A viewer mistakes the fabricated emergency example for real or clinically authoritative information.
2. Configuration changes or a route-guard regression expose legacy patient/responder routes.
3. QR generation uses an untrusted request host if no canonical `BASE_URL` is configured.
4. A public endpoint is abused, or configuration/secrets are mishandled during deployment.
5. A future developer reuses the QR-only flow with real data without first adding independent identity, authorization, key management, and governance.

No Render deployment has been confirmed. Deployment-specific controls below are therefore required checks, not claims that those controls have already been verified in production.

## 2. Scope, assets, and trust boundaries

### In scope

- `/demo/`, `/demo/record`, and `/demo/qr.png`.
- The Flask application, templates, configuration, dependencies, GitHub repository, and a future public web host.
- The disabled legacy patient/responder blueprints, because they remain in the source tree and must stay unreachable in the public demo.

### Explicitly out of scope

- Real-patient data, real emergency contacts, clinical decision support, treatment recommendations, EHR/EMS integration, and any production or supervised clinical use.
- Assurance that the app meets Kenyan or other health, privacy, or medical-device law or policy.

### Assets to protect

| Asset | Current sensitivity / importance |
|---|---|
| Synthetic demo content and its labels | Low confidentiality; **high integrity** because misleading presentation could create unsafe expectations. |
| Application source, GitHub access, and deployment settings | Important to preserve integrity and prevent unauthorized code/config changes. |
| `SECRET_KEY` and any future provider credentials | Secret, even though the current demo has no patient database. |
| Availability and correct demo routing | Useful for a presentation, but no uptime guarantee is made. |
| Any future real patient records | Highly sensitive; **not present or permitted in this demo**. They require a separate design and approval gate. |

### Current data flow

```text
Visitor or phone camera
    → public HTTPS host (future deployment; sandbox preview is temporary)
    → Flask demo route
    → hard-coded DEMO_RECORD rendered into HTML

Landing page
    → QR image route
    → QR contains a link to /demo/record
```

The demo record route does not query the database. QR generation uses configured `BASE_URL` when available, otherwise it constructs the origin from the request host. That fallback is a configuration/security point to verify before deployment.

## 3. Controls confirmed in the current source

These are source-code observations, not a substitute for testing the deployed service:

- `DEMO_MODE` is set to `True` in `config.py`.
- Demo routes use a fixed `DEMO_RECORD` explicitly marked as fabricated; the contact field contains no real phone number.
- The demo record says the QR does not verify the viewer’s identity and provides no treatment advice.
- `app/__init__.py` skips database initialization and filesystem-backed application sessions in demo mode.
- Patient and responder blueprints are registered but a request guard returns 404 for those blueprints in demo mode outside tests.
- Demo HTML and QR responses set `Cache-Control: no-store, no-cache, must-revalidate, max-age=0`, `Pragma: no-cache`, and `X-Robots-Tag: noindex, nofollow, noarchive`.
- The record page listens for the browser `offline` event and hides the record content in favor of an unavailable notice. It does not implement an offline record cache or service worker.
- `render.yaml` specifies Gunicorn and asks Render to generate `SECRET_KEY`; the database URL is optional. The current demo does not need it.
- Automated tests passed locally (28 tests) when this draft was prepared. Re-run them after code changes and verify behavior on the deployed host.

## 4. Risk ranking

**Priority meaning:** P0 = resolve or explicitly accept before public presentation/deployment; P1 = address before sustained public exposure; P2 = mandatory before any real-data pilot. The ratings assume fabricated data stays in use.

| ID | Threat and likely impact | Current controls / evidence | Priority and remaining work |
|---|---|---|---|
| T1 | **Demo mistaken for a real or authoritative medical record.** A presenter or viewer could infer that a medication/allergy example is verified or could guide treatment. | Synthetic-data badges, fabricated provenance, no-treatment-advice wording, and a limitations section appear in the current demo. | **P0.** Keep the warning visible on every record view and in presentation material; never present the values as clinical guidance. Test with a first-time viewer that they understand the page is fabricated. |
| T2 | **QR copied, photographed, or shared.** Anyone with the URL can open the demo record; QR possession does not establish responder identity. | The page states that QR does not verify identity; the exposed content is synthetic. | **P0 for the demo boundary; P2 blocker for real data.** Do not add patient data to this QR flow. Any later real-data product needs independent responder identity and server-side authorization; a hidden or harder-to-guess QR is not a substitute. |
| T3 | **Legacy patient/responder routes become reachable after a configuration or code change.** This could expose registration, verification, database access, or decrypted data if someone re-enables the old flow. | `DEMO_MODE=True`; request guard blocks the legacy blueprints outside tests; regression tests expect 404s. | **P0.** Keep demo mode fail-closed; retain route-denial tests in CI. Do not set demo mode false on a public deployment. Before a real-data pilot, replace the legacy flow rather than merely removing the guard. |
| T4 | **Host-header or origin manipulation poisons the generated QR destination.** If the fallback origin is derived from an attacker-controlled `Host` header, a QR could point a scanner at an unintended site. | `run.py` uses Render’s `RENDER_EXTERNAL_HOSTNAME` when present; demo QR generation prefers `BASE_URL` when configured. | **P0 before hosting the QR publicly.** Set `BASE_URL` to the exact canonical HTTPS origin in deployment configuration; add an allowlist/validation; test that forged `Host` and forwarded-host headers cannot change the QR destination. |
| T5 | **Browser, proxy, or history caching leaves a previously rendered record visible during an outage.** | No-store headers and an offline event handler are present; no service worker is included. | **P1 for the synthetic demo; P2 for any real record.** Verify headers on the actual host and test offline transitions, reload, back/forward navigation, and common mobile browsers. Never use offline caching as a medical-record fallback. |
| T6 | **Secret/configuration exposure or weak signing key.** A weak Flask key can undermine signed session/CSRF state; provider credentials could be leaked through configuration or Git. | New repository snapshot excludes `.env`; `.env.example` uses placeholders; Render blueprint requests a generated key. `config.py` still has a development fallback. | **P0 before hosting.** Confirm the host has generated a unique secret and debug mode is off. Do not copy local secrets. The earlier source repository’s history was not rewritten; rotate any credential that was real or reused. Keep secret scanning enabled. |
| T7 | **Public endpoint abuse or denial of service.** Repeated requests can degrade a small free demo or consume hosting resources. | Flask-Limiter is initialized; without Redis, the configured storage is process-local memory. The demo is read-only and static. | **P1.** Treat the in-process limiter as best-effort, not a distributed defense. Set host-side usage limits/alerts where available; review logs and rate limits before a public presentation. No availability commitment is made. |
| T8 | **Dependency or repository supply-chain compromise.** A compromised package, maintainer token, or unreviewed change could alter the demo or expose future settings. | Dependencies are declared in `requirements.txt`; the repository is public, but public visibility alone does not protect branch integrity. | **P1.** Add CI for tests, dependency/security scanning, and secret scanning; protect `main` and enable strong account authentication. Review dependency updates before merging. |
| T9 | **Visitor privacy leakage through logs or analytics.** IP addresses and request paths may be present in host/access logs even though the demo accepts no patient data. | The demo has no patient profile form, analytics integration, or database write in the current flow. | **P1.** Check hosting-provider log retention and access. Do not place personal or medical information in URLs, query strings, issue reports, or support logs. Document only the minimum operational logging required. |
| T10 | **Future real-data feature is added on top of demo assumptions.** The static QR, old OTP design, local session behavior, or database helpers may be mistaken for production security. | README marks the former prototype documentation as historical; roadmap lists identity, authorization, KMS, lifecycle, and audit work as gates. | **P2 hard stop.** Do not accept real patient records until the production blockers in section 6 are designed, implemented, tested, and independently reviewed. |

## 5. Required checks before a public demo deployment

1. Set `BASE_URL` to the chosen canonical HTTPS host and verify the generated QR uses exactly that origin. Reject or ignore untrusted host overrides.
2. Verify the deployed start command uses Gunicorn, debug mode is off, and the host generated a unique `SECRET_KEY`.
3. Confirm no database is attached or required for the synthetic demo; keep demo mode enabled.
4. Run `pytest -q`; specifically retain tests that check demo labels, no-store headers, QR output, and 404 responses for legacy routes.
5. Inspect deployed response headers for the demo page and QR. Review whether additional headers (for example CSP, `X-Content-Type-Options`, `Referrer-Policy`, and clickjacking protection) are appropriate and implemented.
6. Exercise the demo on a phone: normal scan, QR unavailable, network lost while viewing, page reload while offline, and back/forward navigation.
7. Correct the README’s remaining historical setup and security sections so a new visitor does not mistake the older MySQL/OTP description for current behavior.
8. Confirm repository secret scanning and dependency checks are enabled; do not commit `.env`, local databases, logs, or session files.

## 6. Hard blockers before any real-patient data

The current demo is **not** a starting authorization to pilot with real records. At minimum, a separate reviewed design must provide:

- Independently authenticated and appropriately verified responders; QR is a locator, never a bearer authorization credential.
- Central server-side authorization, minimum field disclosure, expiring access grants, and a reviewed emergency/break-glass process.
- Patient identity, profile correction, revocation, recovery, retention, and deletion workflows.
- Reviewed encryption and managed key handling (for example envelope encryption with a KMS); fail closed if key services fail.
- Data minimization, provenance/freshness semantics, tamper-resistant audit events, and safe error states.
- Versioned schema migrations, backup/restore drills, monitoring, incident response, and an accountable operating organization.
- Qualified Kenyan clinical, privacy/legal, and security review for the intended workflow and jurisdiction. This document does not determine what law or doctrine applies.
- Independent security testing and explicit approval by the accountable organization before any pilot.

## 7. Review and change triggers

Revisit this threat model whenever the app adds user input, patient records, authentication, a database, new QR semantics, offline behavior, analytics, a new host/domain, or a different deployment configuration. Record the change, the owner, evidence of the test/review, residual risk, and approval before expanding the data scope.

**Current decision:** synthetic data only; public QR access is intentionally unauthenticated for demonstration; no real-patient use, clinical reliance, or production-readiness claim.

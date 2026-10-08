# SecureMed QR — One-Month Redesign Roadmap

**Purpose:** move SecureMed QR from a working prototype toward a security-reviewed, presentation-ready emergency-profile demo, while laying out the work required before any real-patient pilot.

**Important scope boundary:** completing this 20-workday plan does **not** by itself make the product clinically validated, legally compliant, or safe for production medical data. Use synthetic records throughout this month. A real-data pilot is a separate launch gate requiring relevant clinical, privacy/legal, and independent security approval.

**Planning assumption:** four weeks / 20 working days, one primary developer, and timely access to a product/clinical stakeholder plus a security reviewer. If those people are unavailable, keep the technical tasks but do not treat the final week as a launch approval.

---

## 1. Current-state findings this plan addresses

The repository already has a Flask/Jinja web app, PostgreSQL persistence, patient registration, QR generation, encryption helpers, a responder view, CSRF protection, rate limiting, and basic access logs. The following issues make this a prototype rather than a production-ready medical service:

- `/scan/<qr_id>` generates and displays the OTP to the same visitor who is asked to submit it. It does not authenticate a responder.
- The encryption key is derived from the public QR ID plus a salt stored in the database. The TOTP secret is also stored in the database. These choices do not provide meaningful protection against a database compromise.
- Patient passwords are saved but there is no login, account recovery, profile-edit, QR-revocation, or deletion flow. The database has an update helper, but it is not connected to a user-facing workflow.
- Decrypted medical details are put into the Flask session. The redesigned app should keep sensitive record data out of session state, browser storage, URLs, and logs.
- `.env`, Python bytecode, runtime logs/session files, and other generated files are tracked; the ignore rules are in `gitignore.txt`, not a functioning `.gitignore`.
- The README describes MySQL, while the current application uses PostgreSQL. The automated “successful OTP” route test mocks the OTP, crypto, and integrity-check functions rather than proving an integrated flow.
- The landing page claims data is encrypted before leaving the browser, but the current implementation encrypts submitted form data on the server.

Treat these as design and repository issues, not merely hosting problems.

---

## 2. Decisions and prerequisites — complete before coding

Record these in a short product/security decision log. Items marked **blocker** must be settled before implementing the associated feature.

1. **Purpose and launch scope (blocker):** Is the one-month target a classroom/demo website, a supervised usability study, or an actual clinical pilot? This roadmap targets a demo and pilot-readiness work only.
2. **Jurisdiction and accountable organization (blocker for real data):** Identify the country/region, data controller/owner, clinical sponsor, and the applicable privacy/health-data requirements. Get qualified legal/privacy advice; do not infer compliance from hosting-provider marketing.
3. **Users and trust model (blocker):** Define patient, emergency contact, responder, organization administrator, and support roles. Decide how responders prove identity and what organization verifies their status.
4. **Emergency access policy (blocker):** Define the normal responder flow and an audited “break-glass” route for a patient who cannot consent. Decide required purpose/reason, duration, notifications, and review process. Do not use the current same-page OTP flow.
5. **Minimum emergency dataset:** Agree field-by-field what is necessary, what is optional, how “unknown” differs from “none,” who supplies each value, and how `last_updated` and provenance are displayed.
6. **Identity and key-management providers (blocker for deployable security):** Select an identity provider that supports the intended responder authentication/MFA and a key-management service appropriate to the deployment. Confirm service terms, region, access controls, cost, and any required contractual assurances. A free demo database or a random environment variable is not a production key-management plan.
7. **Operational ownership:** Name who will respond to incidents, rotate compromised credentials, restore backups, review emergency accesses, and take down the service if needed.
8. **Budget and hosting boundary:** Decide what can be zero-cost for a synthetic-data demo and what requires paid/stable hosting before a real pilot. Set an explicit no-billing/usage limit where available.
9. **Credential hygiene:** Immediately rotate any real credentials that have ever been committed in `.env`; remove secrets from the working tree and plan a history cleanup. Do not print or paste secrets into tickets or chat.
10. **People and access:** Arrange at least one short review with a responder/clinical user, one patient/privacy perspective, and a security reviewer. If no reviewers are available, label the output as an engineering demo only.

### Day-0 completion gate

Before implementation begins, the team has: (a) written the demo/pilot boundary, (b) made decisions 1, 3, 4, and 5, (c) recorded provider choices or explicitly marked them as demo-only, (d) rotated any exposed credentials, and (e) agreed that only synthetic data will be used.

---

## 3. Proposed target design for the month

Keep the existing Flask/Jinja application as a **single web app** for now; splitting the frontend and backend adds deployment complexity without solving the current risks. Organize business logic into services so routes do not perform security decisions themselves.

Suggested modules (names can change, responsibilities should not):

```text
app/
  routes/                 # thin HTTP handlers and templates
  services/
    identity.py           # patient/responder identity adapter
    access_policy.py      # authorization and access-grant decisions
    records.py            # validate, read, update, revoke/deactivate profiles
    encryption.py         # encrypt/decrypt with envelope-key operations
    audit.py              # append-only security/audit events
    qr_tokens.py          # issue, validate, revoke QR identifiers/tokens
  repositories/           # parameterized persistence operations
  models/                  # domain/data-transfer schemas
  utils/                   # narrowly scoped helpers only
migrations/                # versioned schema changes
```

For a pilot-capable design, the QR must be treated as a **locator**, not proof of responder authorization. Authenticate responders independently (for example via an approved organizational identity provider and MFA); authorize the requested fields and purpose on the server. A QR may contain an opaque, revocable identifier, but should not contain medical data or a reusable authorization secret.

For record encryption, use a random data-encryption key and envelope encryption: a managed KMS protects/wraps the data key; the application stores ciphertext and the wrapped key, not the plaintext key. Use an authenticated cipher such as AES-GCM with context bound as associated data. The exact KMS/provider design is a prerequisite decision and requires review. A local development key may exist only for local synthetic-data development and must fail closed in a production environment.

Keep only user/session identifiers, access-grant IDs, and expiry metadata in session state. Load the minimum authorized record after checking the grant. Never cache emergency medical data in local storage or a service worker. For loss of network, show a clear unavailable state and document an approved real-world fallback; do not silently serve stale data.

---

## 4. One-month execution plan (20 working days)

Each day should end with a small reviewable commit or pull request, updated tests, and a short note in the decision log. Merge security-sensitive work only after review.

### Week 1 — Scope, threat model, and repository foundation

| Day | Work and execution | Code / functions / artifacts | Done when |
|---|---|---|---|
| 1 | Kickoff. Confirm demo versus pilot scope, stakeholder roles, success scenario, data fields, and explicit non-goals. Write the primary emergency-use story from QR scan through authorized access. | `docs/product-brief.md`, `docs/decisions.md`; user stories and acceptance criteria. | Team can explain who uses the product, for what emergency, and what data is in/out. Synthetic-data-only boundary is recorded. |
| 2 | Review the current patient and responder journey with at least one intended user. Map normal, consent-capable, unconscious-patient, lost-network, incorrect/old profile, and suspected QR-copy scenarios. | `docs/user-flows.md`; UX wireframes for registration, profile, scan, denied access, and outage. | Stakeholder feedback is recorded; “what if no internet?” has a safe, explicit answer. |
| 3 | Run a threat-model workshop: QR theft/copying, database theft, compromised responder account, insider misuse, session theft, brute force, stale/wrong records, service outage, and leaked credentials. Rank risks by likelihood/impact. | `docs/threat-model.md`, abuse-case list, data-flow diagram, initial risk register. | Every sensitive data flow has a trust boundary, mitigation owner, and unresolved-risk entry. |
| 4 | Agree target architecture and security decisions: responder identity/MFA, break-glass process, key management, account recovery, minimal disclosure, retention, audit review, and provider constraints. | Architecture diagram; decision records; identity/KMS adapter interfaces. | No implementation depends on an unresolved security assumption. If provider choice is pending, related integration remains a stub and demo-only. |
| 5 | Clean repository and CI foundation. Rotate real credentials if any were committed, add a proper `.gitignore`, remove generated files, clean Git history with coordinated force-push if needed, add secret scanning and dependency checks. | `.gitignore`, CI workflow, secret-scan/dependency-scan config, updated README and `.env.example`. | No secret or generated runtime artifact is tracked; secret scanner is clean; deployed credentials have been rotated. History rewrite is coordinated with repo collaborators. |

### Week 2 — Data model, identity, and authorization

| Day | Work and execution | Code / functions / artifacts | Done when |
|---|---|---|---|
| 6 | Design normalized, versioned database schema and migration process. Add timestamps, provenance, status, and revocation fields; avoid storing unnecessary personal data. | PostgreSQL migrations (Alembic or equivalent); repositories for patients, profiles, responders/orgs, access grants, and audit events. | A fresh test database can migrate from zero; no startup-time ad hoc table mutation is needed. |
| 7 | Implement patient account lifecycle for the agreed scope: registration, authenticated sign-in/out, profile read/update, validation, recovery design, deactivate/delete request, and QR rotation. Use a maintained password/auth solution rather than bespoke credential logic where possible. | Thin patient routes; `records.validate_profile()`, `records.update_profile()`, `records.deactivate_profile()`, `qr_tokens.issue()` / `qr_tokens.revoke()`; templates and form validation. | Patient actions require an authenticated owner; edits show when the profile was last updated; revoked QR no longer resolves to an active profile. |
| 8 | Integrate responder identity using the chosen provider in a staging environment. Enforce MFA/strong authentication according to the agreed risk model; map external identity to a verified responder and organization. | `services/identity.py`: `authenticate_responder()`, `get_verified_principal()`, `require_role()`; OIDC callback/logout routes as provider requires. | An unauthenticated or unverified user cannot enter the responder access flow; test identities are non-production. |
| 9 | Implement access policy as a central service. Define normal access rules, authorized data scopes, grant expiry, denied access behavior, and break-glass reason capture. | `access_policy.authorize()`, `access_policy.create_grant()`, `access_policy.expire_grant()`; policy tests. | Routes call one authorization service; no route directly trusts a QR scan, form field, or client-side role. |
| 10 | Replace current OTP page with the responder-authenticated access flow. Add per-user and per-target throttling, abuse handling, safe error messages, and server-side grant checks. | Replace `/scan` + `/verify` flow; target endpoints such as `GET /scan/<token>`, `POST /access/request`, `GET /access/<grant_id>`; tests. | There is no OTP displayed by the server to the scanner. A copied QR alone cannot reveal a record. Authorization is enforced server-side and denied attempts are audited. |

### Week 3 — Key management, emergency experience, and data lifecycle

| Day | Work and execution | Code / functions / artifacts | Done when |
|---|---|---|---|
| 11 | Implement the reviewed encryption/key-management design behind an interface. Generate a random per-record or per-profile data key; wrap/unwrap it through the selected KMS; bind patient/profile/version context as authenticated associated data. | `encryption.encrypt_record()`, `encryption.decrypt_record()`, `wrap_data_key()`, `unwrap_data_key()`; development and staging adapters. | KMS failure fails closed; ciphertext tampering and wrong context fail; key material is not persisted in DB, logs, browser, or app sessions. |
| 12 | Migrate the existing emergency record format. Plan/test a versioned re-encryption migration; do not attempt to “upgrade” old records without knowing the old key material and data integrity. Since this is a demo, prefer re-registering synthetic data after schema changes. | `record_version`, migration/backfill script for synthetic data, migration rollback/backup notes. | Test migration is repeatable and does not silently drop or mislabel patient data. Production data migration remains blocked until reviewed and backed up. |
| 13 | Implement least-privilege emergency display and audit trail. Decide exactly which fields are shown, when break-glass is permitted, how long access lasts, and who gets notified/reviews it. | `audit.log_event()` with actor, subject, purpose, timestamp, outcome, grant ID, and minimal metadata; `records.get_emergency_view()`; patient access-history view. | No full record, OTP, password, access token, or secret appears in logs. Every grant, view, denial, revocation, and break-glass event has an auditable event. |
| 14 | Add profile freshness, source/provenance, patient editing, revocation, and deletion/retention workflows. Ensure empty/unknown values are not rendered as “none.” | Fields such as `updated_at`, `source`, `verified_at`; `records.update_profile()`, `records.revoke_qr()`, `records.request_deletion()`; UI states. | Stale records are visibly flagged; profile owner can correct details and invalidate lost/copied QR; “unknown” is distinct from “no known allergies.” |
| 15 | Harden session and HTTP behavior. Stop putting record contents into Flask session; add production config validation, secure cookies, TLS/proxy configuration, security headers, CSRF on state changes, and secret handling. | Session stores principal/grant IDs only; `config.validate_production_config()`; no-debug production startup; CSP/HSTS and related headers; log redaction. | App refuses production startup with placeholder secrets or demo-only key adapters; no sensitive record data appears in cookie/session payload, URL, or application log. |

### Week 4 — Verification, staging, and presentation

| Day | Work and execution | Code / functions / artifacts | Done when |
|---|---|---|---|
| 16 | Complete the responder/patient UI and accessibility pass. Add clear states for no match, expired QR, denied access, stale profile, service/database outage, and limited network. Explain what to do if the service is unavailable. | Templates/CSS, accessible labels/focus/error handling, outage page, safe fallback instructions. | A first-time tester can complete the synthetic scenario; critical information and denial/outage reasons are unambiguous. No emergency record is cached offline. |
| 17 | Build integrated automated tests, not only mocked route tests. Cover identity, permissions, key management adapter, encryption round trips/tamper detection, revocation, expiry, rate limits, CSRF, audit coverage, and database migrations. | Unit + integration + browser/route tests; CI test database; fixtures using synthetic records only. | CI exercises the full test path with real crypto and a test database. Tests prove unauthorized/expired/revoked access is denied. |
| 18 | Deploy an isolated staging demo and operational controls. Configure TLS, domain, environment secrets, database/KMS credentials, logs/metrics, usage/spend alerts, backups, and a tested restore procedure. Keep seed data synthetic. | Staging deployment, health/readiness endpoint, backup/restore runbook, incident/contact runbook, deploy checklist. | A fresh deployment works from the documented steps; restore is demonstrated; secrets are not in the repository; monitoring shows health without exposing PHI. |
| 19 | Run a tabletop and usability test with stakeholders. Test the normal and break-glass flow, unavailable internet, copied QR, wrong responder, stale data, revoked QR, database outage, and incident response. Fix issues found. | Test script, findings log, remediation PRs, updated risk register. | Critical issues have fixes or explicit blockers; the emergency fallback is understood; reviewers sign off on the demo scope. |
| 20 | Security review and presentation rehearsal. Demonstrate the threat model, architecture, working synthetic-data scenario, limitations, and next gate. Decide whether to continue as a demo, schedule a supervised study, or stop pending risk remediation. | Final demo script, architecture/threat-model slides or notes, release checklist, residual-risk register, next-phase backlog. | Demo is clearly labeled “not for real patient data”; no unresolved critical security defect is presented as solved; pilot is not enabled by default. |

---

## 5. Core code and behavior that must exist before a real-patient pilot

These are **gates**, not optional polish:

- **Independent responder identity:** `get_verified_principal()` must return an authenticated, appropriately verified responder. A QR scan by itself never authorizes access.
- **Central authorization:** `authorize(principal, patient, purpose, requested_fields)` denies by default and returns a narrow, expiring grant only when policy permits.
- **Emergency exception:** `create_break_glass_grant()` requires the agreed reason and captures required context; event is immutable/auditable, reviewed, and triggers the agreed notification. Do not assume patient consent is possible in every emergency.
- **Reviewed key management:** `encrypt_record()` and `decrypt_record()` use random data keys protected by managed KMS/envelope encryption. KMS outages fail closed; key rotation and recovery are tested.
- **Revocable locator:** `issue_qr_token()` returns a random opaque reference; `revoke_qr_token()` invalidates it; token does not encode PHI or act as a bearer credential.
- **Patient control:** authenticated `update_profile()`, QR rotation/revocation, account recovery, and deletion/retention workflows are tested end to end.
- **Minimal emergency response:** `get_emergency_view()` returns only agreed fields; sensitive data is not placed in URLs, browser local storage, logs, analytics, or general session state.
- **Tamper-evident audit:** `log_event()` records required access/security events, blocks ordinary updates/deletes to audit entries, and has a retention/export policy.
- **Safe failure and operations:** health checks, meaningful alerts, TLS, backups, tested restore, deploy rollback, incident response, and named operational ownership exist.
- **Independent verification:** a qualified security reviewer tests the deployed system; clinical/privacy/legal reviewers approve the workflow and data scope for the intended jurisdiction.

---

## 6. Testing and acceptance checklist

### Security and access

- QR is copied and scanned by an unauthenticated person → no profile data is revealed.
- Authenticated responder from the wrong organization or without sufficient scope → denied and audited.
- Break-glass access → requires reason, expires, is visible in review, and triggers the agreed alert.
- Expired/revoked QR or access grant → denied, even if a stale browser tab is used.
- Repeated attempts → throttled without leaking whether a profile exists unnecessarily.
- Session contains identifiers only; logout/revocation ends access; CSRF is rejected on state-changing requests.
- No passwords, OTPs, access tokens, KMS keys, plaintext records, or avoidable patient identifiers appear in logs.

### Data correctness and reliability

- Tampered ciphertext, wrong key, wrong associated context, or corrupt record → no partial plaintext is displayed.
- “Unknown,” “not entered,” “none reported,” and confirmed absence are distinct states.
- Profile shows last-updated/source details; edits produce a new timestamp and audit event.
- Database/KMS/network outage → safe error and documented fallback, never a fabricated “no conditions” result.
- Backup restore and schema migration are exercised in staging.

### User experience

- Responder can reach the agreed minimum emergency view on a phone with gloves/limited time (validate with real users).
- Access denial, stale profile, lost network, and unknown QR states explain the next safe action.
- Keyboard/screen-reader basics, readable contrast, mobile layout, and form validation are tested.

---

## 7. What should wait until after this month

Do not force these into the first month unless an accountable sponsor and reviewer are available: real-patient onboarding, multi-hospital federation, integrations with EHR/EMS systems, offline storage of medical data, large-scale analytics, claims of regulatory compliance, and automated high-availability/24×7 guarantees. Each expands risk and needs requirements, contractual review, and dedicated testing.

A suitable next phase is a **supervised pilot plan**: named clinical sponsor, approved cohort, formal consent and data-retention plan, security assessment, incident drills, defined uptime/support expectations, and measurable usability/safety outcomes. Until those are approved, keep the public demo synthetic-data-only.

---

## 8. Repository-specific immediate actions

1. Check whether any real secret was committed in `.env`; rotate it with its provider immediately if so. Do not copy the old value into a new file.
2. Add `.gitignore` (not `gitignore.txt`) and exclude `.env`, virtual environments, `__pycache__/`, `*.pyc`, session data, logs, database dumps, and local uploads.
3. Remove committed generated artifacts and, if secrets were ever present, coordinate a Git history rewrite and require collaborators to re-clone. Rewriting history alone does not replace credential rotation.
4. Correct the README’s MySQL/PostgreSQL mismatch and remove the inaccurate “encrypted before it leaves your browser” statement unless browser-side encryption is actually built and independently reviewed.
5. Replace the current OTP flow before any public demonstration that implies it authenticates responders. Until then, label it clearly as a simulated access flow and use synthetic data.
6. Keep the existing test suite, but add integrated tests that do not mock away the crypto and authorization behavior under test.

# SecureMed QR V2 — Fast-Track Presentation Roadmap

**Goal:** prepare a credible, working synthetic-data demonstration for an organization in the shortest practical time. This plan is for a presentation prototype—not a clinical pilot or production medical-record system.

**Schedule assumption:** one developer, focused work, and prompt access to the Render account and presentation contact. The technical critical path is about **three focused build days**. Calendar time may be longer if hosting access, organizational feedback, or review is delayed. If the organization has given a specific presentation date or acceptance criteria, update this plan against that date before expanding scope.

## Non-negotiable boundary

- Fabricated data only; no real patient names, phone numbers, or medical details.
- No claim that QR possession verifies responder identity.
- No treatment advice, clinical decision support, or claim of legal/privacy compliance.
- No database is required for the current demo. Do not connect Neon or enable legacy patient/responder routes for this presentation.
- “Emergency doctrine applies” remains an unverified assumption supplied by the project owner; it is not a legal or clinical determination.

## Current baseline

| Item | Status |
|---|---|
| Synthetic demo routes and record | Implemented |
| Prominent synthetic-data and QR limitation messaging | Implemented |
| No-store headers and unavailable/offline notice | Implemented; verify on mobile browsers and deployed host |
| Legacy patient/responder routes blocked outside tests | Implemented; regression tests exist |
| Threat model | Drafted in `docs/threat-model.md` |
| Public GitHub repository | Created at `xavier4-csr/SecureMED_Version_2` |
| Automated test suite | 28 tests previously passing; rerun after each change |
| Render deployment | Not done |
| Current README accuracy | Completed in Step 1; rewritten for the current synthetic demo |

## Fast critical path

### Step 1 — Make the demo deployable and understandable (completed 2026-10-08)

**Work**
- Replace historical README instructions with the current synthetic-demo setup and safety boundary.
- Add a minimal `/healthz` response that reveals no configuration or user data.
- Configure Render’s health check to use `/healthz`.
- Add a regression test proving the health response is minimal.

**Done when** `pytest -q` passes; README matches the live code; `/healthz` returns only `{"status":"ok"}`; the Render blueprint points to that route.

### Step 2 — Close presentation-critical configuration and UX gaps

**Work**
- Pin QR generation to the canonical HTTPS `BASE_URL`; test that a forged `Host` header cannot redirect the QR.
- Verify no-store and indexing headers on the landing, record, and QR responses.
- Add/verify appropriate security headers (CSP, content-type sniffing, referrer, and framing controls) without breaking the page.
- Test the offline/unavailable state, lost connectivity, reload, browser back/forward behavior, readable mobile layout, keyboard navigation, and screen-reader labels.
- Confirm `/register`, `/scan/demo`, `/dashboard`, and other legacy flows remain unavailable in non-test mode.

**Done when** the tests cover these assertions and the demo has been checked on a phone-sized viewport. Do not use offline caching for medical content.

### Step 3 — Deploy the synthetic demo to Render

**Work**
- Connect the new GitHub repository to a Render Web Service using `render.yaml`.
- Keep `DEMO_MODE=True`, use the generated `SECRET_KEY`, set/verify the canonical public origin, and do not configure a patient database or Redis.
- Deploy with Gunicorn, verify HTTPS, health check, logs, and the host’s free-tier limits.
- Smoke-test every route, including QR decoding to the expected HTTPS record URL and 404s for legacy routes.

**Done when** a fresh deployment is reachable on the intended public URL, `/healthz` is healthy, the QR opens the same demo record, no real data is present, and the known limitations are visible.

### Step 4 — Prepare the organizational presentation

**Work**
- Create a 5–8 minute walkthrough: problem hypothesis → QR scan → synthetic record → outage/unknown state → safety limitations → questions for the organization.
- Rehearse with the actual presentation device/network; bring a screenshot or static backup of the landing and record pages, clearly labelled as a backup—not offline medical access.
- Prepare a one-page feedback log: workflow fit, fields/order, trust/freshness, connectivity, QR placement, and what the organization would require before any pilot.
- Ask for feedback and permission before attributing or publishing any participant comments.

**Done when** the presenter can demonstrate the flow and explain what is—and is not—implemented without implying clinical readiness.

## Suggested 3-day execution cadence

| Day | Focus | Exit gate |
|---|---|---|
| Day 1 | Complete Step 1; implement QR-origin validation and security-header tests from Step 2. | Test suite passes; README and configuration are accurate; no unsafe demo-mode path is introduced. |
| Day 2 | Finish mobile/offline/accessibility smoke tests; connect the repository to Render and deploy with no database. | Public HTTPS demo works, health check is green, QR target is correct, legacy routes return 404. |
| Day 3 | Rehearse the presentation, verify the backup/demo device, and record organizational questions. | Demo is clearly synthetic; presenter can describe risks and next gates; no real-data pilot is implied. |

The schedule is a target, not a promise. Do not skip the QR-origin check, route guard, synthetic-data boundary, or successful smoke tests to save time.

## Stop conditions and post-presentation paths

Stop and keep the demo synthetic if the organization asks to upload real patient data, use real emergency contacts, rely on offline records, or treat QR access as responder authentication. Record the request, but do not implement it as a quick demo enhancement.

After the presentation, choose one path:

1. **Presentation demo only:** incorporate low-risk usability feedback and keep fixed synthetic data.
2. **Supervised usability research:** agree participant consent, data handling, oversight, and study plan before collecting research data.
3. **Real-data pilot request:** pause feature development and begin a separate clinical/privacy/legal/security and operational discovery phase. The month-long production roadmap remains the minimum planning reference; the three-day demo plan does not replace it.

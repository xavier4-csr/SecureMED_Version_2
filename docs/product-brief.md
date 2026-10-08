# SecureMed QR — Product Scope Brief (Draft)

**Status:** Demo scope approved by the project owner; informed by one real practitioner interview structured with Claude. Validate with additional intended users before any broader claims.

**Purpose:** define the first-month target for the redesign.

**Target:** presentation-ready demo using synthetic data only. This is not approval to collect, store, or process real patient information.

## Agreed scope

| Topic | Agreed choice |
|---|---|
| First-month outcome | Demo with synthetic data |
| Intended presentation context | Kenya |
| Primary user | Paramedic / first responder |
| Emergency scenario | Patient is unconscious after a road traffic accident |
| Initial information shown | Allergies and key medications prominent; emergency contact secondary |
| Access preference for demo | No responder login; scan a QR code |
| Network failure preference | Show an unavailable/offline notice; no cached medical record |
| Consent assumption | Owner’s statement: “Emergency doctrine applies” |

## Problem statement

In a road traffic accident, an unconscious patient may be unable to share relevant health information. The demo explores whether a QR-linked profile can make **synthetic allergy and key-medication information** easy to find after immediate scene assessment or during handover, with an emergency contact available as secondary context. It must make clear what the system can and cannot do.

## Demo user journey

1. A demo patient profile is created using invented data.
2. The demo displays a QR code linked to that profile.
3. A paramedic scans the QR code on a phone.
4. The demo shows synthetic allergy and key-medication fields prominently, with emergency contact secondary. It shows each field's source/status and last-updated information, and clearly labels the flow as a demonstration.
5. If the network or service is unavailable, show “Cannot load profile. Treat information as unknown and follow your established emergency process.” Do not show cached medical details or imply that data is available offline.

## Access and safety constraints

- The requested **no-login QR flow applies only to the synthetic-data demo**. Anyone who obtains or photographs a QR could otherwise access the linked record; QR possession is not proof that someone is a paramedic. Do not use real patient records or describe this flow as responder authentication.
- The current repository’s OTP is displayed to the same visitor who is asked to enter it. It does not add an independent authentication factor and must not be presented as one.
- The “emergency doctrine applies” statement is recorded as a **policy hypothesis supplied by the project owner**, not as a verified statement of Kenyan law or clinical policy. Before any real-data use, confirm the applicable consent/emergency-access rules with qualified Kenyan legal/privacy and clinical reviewers and the responsible organization.
- Display allergies and key medications prominently, with emergency contact secondary. Distinguish “unknown/not provided” from “none reported.” Show source/status and last-updated information, and identify every record as synthetic demo data.
- Do not store sensitive record data in a browser cache, local storage, service worker, URL, analytics event, or log. For this demo, offline means showing a status notice—not showing a cached medical record.
- Use invented names, contact details, and medical details only. Avoid real phone numbers and identifiers.

## In scope for the first-month demo

- A simple synthetic patient profile and QR code.
- Mobile-friendly scan/view screens.
- Prominent allergy and key-medication display, secondary emergency-contact context, field freshness/source, and demo labeling.
- No-login QR access **only to fabricated demo records**.
- Clear unknown, invalid QR, stale data, and unavailable/offline states.
- A presentation script that explains the access limitation and does not claim production readiness.

## Out of scope for this demo

- Real patient information or real emergency contacts.
- Claiming that QR possession verifies responder identity.
- Clinical decision support, treatment recommendations, or EHR/EMS integration.
- Serving records offline or caching sensitive data on a device.
- Claims of compliance with Kenyan or other health/privacy laws.
- A real-world pilot or public service launch.

## Demo success criteria

- A first-time tester can scan the demo QR on a phone and locate allergy and key-medication information, plus secondary emergency-contact context, in the handover-oriented scenario.
- Every displayed record is clearly synthetic and shows an update/status indicator.
- A missing network/service produces an unmistakable offline/unavailable notice without presenting stale or invented clinical information as current.
- A presenter can explain that QR-only access is a deliberate prototype trade-off and is not suitable for real patient data.

## Open validation items before proceeding beyond demo

1. Confirm the workflow with a Kenyan paramedic or relevant emergency-care representative.
2. Confirm exact field meaning and presentation (including allergy unknown vs. none reported).
3. Validate Kenyan consent, emergency-access, privacy, and health-record obligations with qualified reviewers and the accountable organization.
4. Define an independently authenticated responder model and a reviewed emergency/break-glass process before any real-data pilot.
5. Define data ownership, correction, revocation, deletion, retention, incident response, and operational support.

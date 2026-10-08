# SecureMed QR — Task 2: Demo Journey and User-Validation Guide

**Status:** Draft updated after one real emergency-care practitioner interview (responses organized with Claude). Use further review to validate generalizability. This is a product-design aid, not clinical or legal guidance.

**Scope:** Synthetic-data demo only. Do not test with real patient details.

## 1. Scenario to validate

A paramedic arrives at a road traffic accident. The patient is unconscious and cannot provide information. After immediate scene priorities, the paramedic or receiving team may use a phone to scan a SecureMed QR marker during transport/handover. The synthetic demo shows allergy and key-medication information prominently, with emergency contact secondary. The target point in the workflow remains a hypothesis to validate with more responders and receiving-facility staff.

## 2. Draft happy-path journey

1. **Demo setup:** Presenter selects a pre-created synthetic patient profile. The QR is visibly labeled as a demo artifact.
2. **Scan:** Paramedic scans the QR with the phone camera. No app installation is required for the demo.
3. **Demo landing state:** Page clearly says “Synthetic demo record—not real patient information.” It does not imply that the QR verifies the scanner's identity.
4. **Emergency view:** Show allergy status and key medications prominently; place emergency contact in a secondary section. Show per-field source/status and last-updated information. Distinguish “not provided/unknown” from “none reported.”
5. **Next action:** The screen does not make treatment recommendations. Any contact control in the demo is clearly marked as a simulation and does not place a call or message anyone.
6. **Exit:** Close the page; the demo should not save the medical view into local storage or a service worker.

## 3. Failure and edge-state behavior

| Situation | Draft demo behavior | Validate with responder |
|---|---|---|
| No mobile data / service unavailable | Show “Cannot load profile. Treat information as unknown and follow your established emergency process.” Do not show cached medical details. | What fallback is actually usable in this setting? What wording avoids confusion? |
| QR not recognized | Say the code cannot be matched; do not imply that no allergy or condition exists. | What would the paramedic do next? |
| Allergy field not supplied | Display “Not provided” or “Unknown,” not “No known allergies.” | Which phrasing is operationally clear? |
| Profile old or not recently confirmed | Show a prominent “Last updated…” marker and an unverified/stale label if the owner has not confirmed it. | What date/status is needed to judge freshness? |
| QR is damaged or copied | For this demo, do not claim that the scan authenticates a responder. Record QR-only access as a prototype limitation. | What identity assurance and organizational process would a real service require? |
| Emergency contact is absent/unreachable | State that the contact is unavailable; do not imply that the app has verified the person or number. | What alternative should the interface indicate? |
| User has gloves, poor light, or limited time | Use large, high-contrast text and avoid multi-step forms in the demo. | Can the essential fields be found quickly on their actual device? |

**Safety rule:** an outage or missing record must never render as “no known allergies” or another reassuring clinical statement. The demo must not offer cached clinical data as an offline fallback.

## 4. 20–30 minute stakeholder interview

### Opening (read aloud)

> We are exploring a synthetic-data demo of a QR-linked emergency profile for an unconscious road-traffic-accident patient. It is not a clinical service, and we are not asking for real patient information. I want to learn how this workflow fits—or does not fit—your actual practice. There are no preferred answers.

### Questions

1. At which point is an emergency profile useful: roadside, transport/handover, or receiving-facility triage?
2. Does the proposed order—allergies and key medications prominent, emergency contact secondary—fit your work? What should change?
3. At the scene, what phone/device and network conditions should we realistically test? How often is data connectivity unavailable or unreliable?
4. Would a QR marker on a card, wristband, or another object be noticeable and practical? What could prevent a scan?
5. If anyone who photographs the QR can open a synthetic record without logging in, what does that demonstrate well—and what does it risk teaching the audience incorrectly?
6. When a patient cannot consent, who or what organizational policy should guide access? Who should review or be notified about access afterward? (Capture as a question for qualified policy/legal review, not as a conclusion.)
7. If the app cannot connect, what is the safe and realistic next action? What exact message would help rather than distract?
8. What would make the profile untrustworthy—for example, stale data, unclear source, a typo, or an unreachable contact?
9. What would you want to see in a demonstration before judging the concept useful?
10. What part of this concept should we stop, change, or investigate before showing it more widely?

### Closing

Ask the participant to rank the top three changes and whether they are willing to review a revised flow. Do not record identifiable patient stories or sensitive operational information without an approved process.

## 5. Observation checklist

During a synthetic-record walkthrough, record observations rather than coaching the participant:

- Can they identify that the page is a demo and contains synthetic data?
- Can they locate allergy status and emergency-contact status?
- Do they understand “unknown,” “not provided,” and “none reported” as different?
- Do they notice the last-updated/stale indicator?
- Do they understand that QR-only access does not verify that they are a responder?
- Do they correctly understand what happens when the network is unavailable?
- Which step causes hesitation, extra taps, or misinterpretation?

Do not set a usability pass threshold in advance; establish it after learning the real task and observing more than one representative user.

## 6. Decisions to record after the interview

Update `docs/product-brief.md` and `docs/decisions.md` with:

- Confirmed, changed, or removed fields and their exact labels.
- Whether a QR is usable in the target context and how it should be placed/presented.
- Required freshness/source indicators.
- Exact safe outage wording and the responder's established fallback.
- The difference between the synthetic demo's QR-only shortcut and any future responder identity/access policy.
- Unresolved clinical, privacy/legal, operational, or security questions with an owner and next action.

This draft reflects one real interview, not a representative study. Further feedback can refine the demo; implementation remains synthetic-data-only. A paramedic's workflow feedback does not replace qualified security, clinical-governance, privacy, or legal review for any real-data pilot.

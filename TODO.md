# Frontend Overhaul — Task Tracker

## Steps
- [x] 1. `app/static/css/main.css` — append v3 CSS (hero parallax, tilt-card, glass-panel, reveal, orbs, qrid-box, btn-sm, preserve-3d, otp radius, reduced-motion)
- [x] 2. `app/templates/base.html` — add interaction <script> (3D tilt + scroll reveal) before </body>
- [x] 3. `app/templates/index.html` — orbs in hero; tilt-card+reveal on step-cards & sec-cards; reveal on record-preview & stats-bar
- [x] 4. `app/templates/patient/dashboard.html` — reveal on cards; tilt-card QR; qrid-box + copyQrId(); stagger delays
- [x] 5. `app/templates/patient/register.html` — add reveal to outer .card
- [x] 6. `app/templates/responder/scan.html` — reveal on found .card; tilt-card OTP box
- [x] 7. `app/templates/responder/view.html` — add reveal to main .card
- [x] 8. Verify templates render / Jinja syntax review

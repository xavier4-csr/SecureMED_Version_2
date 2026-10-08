# SecureMed QR

> **Current status: synthetic-data demonstration only.** The running app redirects `/` to `/demo/` and serves a fabricated profile at `/demo/record`. It does not authenticate responders and must not be used with real patient data. The former database-backed registration/responder routes are blocked outside tests. The demo does not initialize or connect to the patient database. No clinical, security-compliance, or availability guarantee is made.

## Run the current demo

Install dependencies with `pip install -r requirements.txt`, then run `python run.py` and open `http://localhost:5000/`. To test QR scanning on a phone, set `BASE_URL` to a reachable HTTPS address before generating the QR. The demo uses fixed synthetic values and does not need a patient database.

Current demo routes: `/demo/`, `/demo/qr.png`, and `/demo/record`. Run checks with `pytest -q`.

> **Historical prototype documentation follows.** The descriptions below refer to the earlier database-backed OTP/encryption prototype; that flow is intentionally not exposed by the current demo and should not be relied on for a security or production claim.

A Flask-based emergency medical profile system with three layers of security:
**AES-256-GCM encryption**, **TOTP one-time passwords**, and **SHA-256 record hashing**.

Patients register once and carry a QR wristband or card. First responders scan
the QR code, enter a time-limited OTP, and instantly see the critical medical
info they need — blood type, allergies, conditions, emergency contacts.

---

## How it works

```
Patient registers
  → bcrypt password hash
  → SHA-256 record fingerprint
  → AES-256-GCM encryption (key derived via PBKDF2, never stored)
  → TOTP secret generated
  → QR code issued

Responder scans QR
  → OTP displayed (rotates every 30 sec)
  → Responder enters OTP → verified server-side
  → AES key re-derived → record decrypted
  → SHA-256 hash verified (tamper detection)
  → Critical info displayed for 10 minutes
  → Every attempt logged to access_logs
```

---

## Security design

| Layer | Technology | Purpose |
|---|---|---|
| Encryption | AES-256-GCM | Protects data at rest — ciphertext is useless without the key |
| Key derivation | PBKDF2-HMAC-SHA256 (600k iterations) | Key never stored — re-derived from qr_id + salt on demand |
| Access gate | TOTP (RFC 6238) | Time-limited 6-digit code, expires every 30 seconds |
| Tamper detection | SHA-256 | Hash stored at registration, verified after every decryption |
| Password storage | bcrypt (cost 12) | Patient account passwords hashed and salted |
| Audit trail | MySQL access_logs | Every scan attempt logged with IP, timestamp, success/fail |

**What is never stored:** plaintext records, plaintext passwords, AES keys, OTP codes.

---

## Project structure

```
SecureMed-QR/
├── run.py                        # Start the Flask dev server
├── config.py                     # App configuration
├── .env                          # Secret credentials (never commit)
├── requirements.txt              # Pinned dependencies
│
├── app/
│   ├── __init__.py               # App factory: init DB, register blueprints
│   ├── routes/
│   │   ├── patient.py            # /register, /qr/<id>, /dashboard
│   │   └── responder.py          # /scan/<id>, /verify/<id>, /view/<id>
│   ├── utils/
│   │   ├── crypto.py             # AES-256-GCM encrypt/decrypt, PBKDF2
│   │   ├── hashing.py            # SHA-256 hash and verify
│   │   ├── otp.py                # TOTP generate and verify
│   │   └── db.py                 # MySQL connection pool and helpers
│   ├── templates/
│   │   ├── base.html
│   │   ├── patient/
│   │   │   ├── register.html
│   │   │   └── dashboard.html
│   │   └── responder/
│   │       ├── scan.html
│   │       └── view.html
│   └── static/
│       └── css/main.css
│
└── tests/
    ├── test_crypto.py
    ├── test_hashing.py
    ├── test_otp.py
    └── test_routes.py
```

---

## Setup

### Prerequisites
- Python 3.11+
- MySQL 8.0+ running locally

### Install

#### Windows (recommended)

Use the provided script:

```bat
scripts\setup_and_run_windows.bat
```

#### Manual (Windows)

```bat
git clone <repo-url>
cd SecureMed-QR

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
```


### Configure

```bash
cp .env.example .env
```

Edit `.env`:

```env
SECRET_KEY=replace-with-a-long-random-string-at-least-32-chars
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=securemed
```

### Run

```bash
python run.py
```

Open `http://localhost:5000/register`

The database and tables are created automatically on first run.

---

## Running tests

```bash
pytest tests/test_crypto.py tests/test_hashing.py tests/test_otp.py -v
```

---

## API endpoints

| Method | Route | Description |
|---|---|---|
| GET | `/register` | Patient registration form |
| POST | `/register` | Submit registration — runs full crypto pipeline |
| GET | `/qr/<qr_id>` | Serve QR code as PNG image |
| GET | `/dashboard` | Patient dashboard with QR and access log |
| GET | `/logout` | Clear session |
| GET | `/scan/<qr_id>` | Responder scans QR — shows OTP |
| POST | `/verify/<qr_id>` | Responder submits OTP — decrypt and open session |
| GET | `/view/<qr_id>` | Display decrypted medical record (session-gated) |

---

## Dependencies

```
flask                  Web framework
mysql-connector-python MySQL driver
cryptography           AES-256-GCM, PBKDF2
bcrypt                 Password hashing
pyotp                  TOTP one-time passwords
qrcode + pillow        QR code generation
python-dotenv          Environment variable loading
pytest                 Testing
```

---

## Important notes

- `instance/` and `.env` are in `.gitignore` — never commit them
- The AES encryption key is derived at runtime and never persisted anywhere
- Every access attempt (success or failure) is written to `access_logs`
- OTP sessions expire after 10 minutes automatically
- For production: use HTTPS, set a strong `SECRET_KEY`, and restrict DB user permissions

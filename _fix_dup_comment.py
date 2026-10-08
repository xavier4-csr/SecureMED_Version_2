"""Remove the stray duplicate '# --- Validate OTP ---' comment at column 0."""
path = "app/routes/responder.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace the duplicate block (stray col-0 comment + correct indented comment)
old = (
    "\n# --- Validate OTP ---\n"
    "    # --- Validate OTP ---\n"
    "    if not verify_otp(patient[\"totp_secret\"], submitted):\n"
) new = (
    "\n    # --- Validate OTP ---\n"
    "    if not verify_otp(patient[\"totp_secret\"], submitted):\n"
)

if old in content:
    content = content.replace(old, new)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("DEDUPED")
else:
    print("PATTERN NOT FOUND")

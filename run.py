import os
import socket
from app import create_app

app = create_app()

# -- On Render auto-detect BASE_URL from the RENDER_EXTERNAL_HOSTNAME env var --
#    RENDER_EXTERNAL_HOSTNAME is set by Render automatically in production.
#    Do NOT override if the user has explicitly set BASE_URL in .env / env vars.
render_hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "")
if render_hostname and not app.config.get("BASE_URL"):
    app.config["BASE_URL"] = f"https://{render_hostname}"

# -- LOCAL DEV ONLY: Auto-detect LAN IP for phone/mobile testing --
#    This block only runs when started via `python run.py` (__main__),
#    NOT when gunicorn imports the app in production.
if __name__ == "__main__":
    # Detect LAN IP for local network testing
    LAN_IP = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.1)
        s.connect(("8.8.8.8", 80))
        LAN_IP = s.getsockname()[0]
        s.close()
    except Exception:
        LAN_IP = "127.0.0.1"

    # Fall back to LAN IP for BASE_URL if still not set (local dev without .env)
    if not app.config.get("BASE_URL"):
        app.config["BASE_URL"] = f"http://{LAN_IP}:5000"

    print(f"\n[NET] Your LAN IP is: {LAN_IP}")
    print(f"[NET] BASE_URL = {app.config['BASE_URL']}")
    print(f"[NET] On your phone, visit {app.config['BASE_URL']}")
    print(f"[NET] QR codes will encode: {app.config['BASE_URL']}/scan/<qr_id>\n")

    # 0.0.0.0 makes Flask accessible from other devices on your network
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)

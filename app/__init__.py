from flask import Flask, abort, render_template, request
from werkzeug.middleware.proxy_fix import ProxyFix
from config import Config
from flask_session import Session
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.utils.db import init_db, close_db

csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Render sits behind a reverse proxy - trust its X-Forwarded-* headers
    # so request.host_url, url_for(_external=True), and client IPs
    # (used by rate limiting and access_logs) are correct.
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    # The synthetic demo stores no application session state. Avoid writing
    # server-side session files; legacy non-demo configurations use Flask-Session.
    if not app.config.get("DEMO_MODE", True):
        Session(app)

    # Initialise CSRF protection
    csrf.init_app(app)

    # Initialise rate limiter (uses Redis storage from config)
    limiter.init_app(app)

    # The public prototype is intentionally synthetic-data-only. Do not
    # connect to or initialize a patient database in demo mode.
    if not app.config.get("DEMO_MODE", True):
        with app.app_context():
            init_db()
        app.teardown_appcontext(close_db)

    # Register routes and blueprints
    from app.routes.patient   import patient_bp
    from app.routes.responder import responder_bp
    from app.routes.main      import main_bp
    from app.routes.demo      import demo_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(demo_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(responder_bp)

    @app.before_request
    def block_legacy_patient_routes_in_demo():
        """Keep the old database-backed prototype routes unreachable in demo."""
        if app.config.get("DEMO_MODE", True) and not app.testing:
            if request.blueprint in {"patient", "responder"}:
                abort(404)

    # --- Custom error handlers ---
    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        """Return a friendly page when rate-limited instead of raw 429."""
        return render_template("demo/landing.html"), 429

    return app

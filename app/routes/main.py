"""
main.py — Landing page and general routes.
"""
from flask import Blueprint, redirect, url_for

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    return redirect(url_for("demo.home"))

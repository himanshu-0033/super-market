"""
RetailPOS — Flask Point of Sale Application
=============================================
Main entry point for the application.
"""

from backend import create_app
from backend.models import db

app = create_app()

@app.route("/")
def index():
    from flask import redirect, url_for
    from flask_login import current_user
    
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for("dashboard.dashboard"))
        return redirect(url_for("pos.pos"))
    return redirect(url_for("auth.login"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("[OK] Database tables created.")
    app.run(debug=True)

import os
from datetime import datetime

from flask import (
    Flask, render_template, request,
    redirect, url_for, flash
)
from flask_sqlalchemy import SQLAlchemy
from cryptography.fernet import Fernet
import smtplib
from email.mime.text import MIMEText

# ---------------------------------------------------
# Flask & DB Config
# ---------------------------------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-this-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///time_capsule.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------------------------------------------
# Encryption Setup (Sprint 2)
# ---------------------------------------------------
ENCRYPTION_KEY = os.environ.get("TIME_CAPSULE_KEY")
if not ENCRYPTION_KEY:
    # For demo only – in real deployment, set TIME_CAPSULE_KEY env var
    ENCRYPTION_KEY = Fernet.generate_key()
    print("TEMP DEV ENCRYPTION KEY (save this if you want to keep data):")
    print(ENCRYPTION_KEY.decode())

fernet = Fernet(ENCRYPTION_KEY)

# ---------------------------------------------------
# Email Config (Optional: real sending in Sprint 2)
# ---------------------------------------------------
# Set these as environment variables if you want real email sending
EMAIL_HOST = os.environ.get("EMAIL_HOST")          # e.g. "smtp.gmail.com"
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True


def send_email(to_email: str, subject: str, body: str, from_email: str):
    """
    Simple SMTP email sender.
    If EMAIL_HOST_USER/PASSWORD not configured, just print to console.
    """
    if not (EMAIL_HOST and EMAIL_HOST_USER and EMAIL_HOST_PASSWORD):
        print("=== SIMULATED EMAIL (no SMTP config) ===")
        print(f"To: {to_email}")
        print(f"From: {from_email}")
        print(f"Subject: {subject}")
        print(body)
        print("=== END EMAIL ===")
        return

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = EMAIL_HOST_USER
    msg["To"] = to_email

    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        if EMAIL_USE_TLS:
            server.starttls()
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        server.send_message(msg)
        print(f"Email sent to {to_email}")


# ---------------------------------------------------
# DB Model – Sprint 1 + encryption hooks (Sprint 2)
# ---------------------------------------------------
class Capsule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_name = db.Column(db.String(100), nullable=False)
    sender_email = db.Column(db.String(120), nullable=False)
    recipient_email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)

    encrypted_content = db.Column(db.LargeBinary, nullable=False)

    delivery_datetime = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default="pending", nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ----- Helper methods for encryption -----
    def set_content(self, plain_text: str):
        self.encrypted_content = fernet.encrypt(plain_text.encode("utf-8"))

    def get_content(self) -> str:
        try:
            return fernet.decrypt(self.encrypted_content).decode("utf-8")
        except Exception:
            return "[Unable to decrypt content]"


# ---------------------------------------------------
# Ensure DB Tables Exist (fixes your 'no such table: capsule' error)
# ---------------------------------------------------
with app.app_context():
    db.create_all()


# ---------------------------------------------------
# Routes – Sprint 1
# ---------------------------------------------------
@app.route("/")
def index():
    capsules = Capsule.query.order_by(Capsule.created_at.desc()).all()
    return render_template("index.html", capsules=capsules)


@app.route("/capsule/new", methods=["GET", "POST"])
def create_capsule():
    if request.method == "POST":
        sender_name = request.form.get("sender_name")
        sender_email = request.form.get("sender_email")
        recipient_email = request.form.get("recipient_email")
        subject = request.form.get("subject")
        message = request.form.get("message")
        delivery_str = request.form.get("delivery_datetime")

        if not all([sender_name, sender_email, recipient_email, subject, message, delivery_str]):
            flash("All fields are required.", "danger")
            return redirect(url_for("create_capsule"))

        try:
            delivery_datetime = datetime.fromisoformat(delivery_str)
        except ValueError:
            flash("Invalid date/time format.", "danger")
            return redirect(url_for("create_capsule"))

        capsule = Capsule(
            sender_name=sender_name,
            sender_email=sender_email,
            recipient_email=recipient_email,
            subject=subject,
            delivery_datetime=delivery_datetime,
        )
        capsule.set_content(message)

        db.session.add(capsule)
        db.session.commit()
        flash("Time capsule created successfully!", "success")
        return redirect(url_for("index"))

    return render_template("create_capsule.html")


@app.route("/capsule/<int:capsule_id>")
def view_capsule(capsule_id):
    capsule = Capsule.query.get_or_404(capsule_id)
    content = capsule.get_content()
    return render_template("view_capsule.html", capsule=capsule, content=content)


# ---------------------------------------------------
# Scheduler – Sprint 2 (time-based delivery)
# ---------------------------------------------------
@app.route("/scheduler/run")
def run_scheduler():
    """
    Simulates the background job that TimeCapsulator does
    with Celery.

    In production, hit this endpoint periodically using cron:
      */5 * * * * curl http://127.0.0.1:5000/scheduler/run
    """
    now = datetime.utcnow()
    due_capsules = Capsule.query.filter(
        Capsule.status == "pending",
        Capsule.delivery_datetime <= now
    ).all()

    if not due_capsules:
        return "No capsules due.", 200

    for cap in due_capsules:
        message_body = cap.get_content()

        # Send email (or simulate)
        send_email(
            to_email=cap.recipient_email,
            subject=cap.subject,
            body=f"From: {cap.sender_name} <{cap.sender_email}>\n\n{message_body}",
            from_email=cap.sender_email,
        )

        cap.status = "sent"

    db.session.commit()
    return f"Processed {len(due_capsules)} capsule(s).", 200


if __name__ == "__main__":
    app.run(debug=True)

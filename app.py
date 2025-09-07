from flask import Flask, request, jsonify, render_template
import os
import smtplib
from email.message import EmailMessage
import random

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "super-secret")

# Load .env credentials
SMTP_HOST = os.environ.get("SMTP_HOST")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
MAIL_USER = os.environ.get("MAIL_USER")
MAIL_PASS = os.environ.get("MAIL_PASS")
MAIL_FROM = os.environ.get("MAIL_FROM")

# OTP storage (for testing)
otp_store = {}

# Function to send OTP email
def send_otp(to_email, otp_code):
    msg = EmailMessage()
    msg["Subject"] = "Your OTP Code"
    msg["From"] = MAIL_FROM
    msg["To"] = to_email
    msg.set_content(f"Your OTP is: {otp_code}")

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(MAIL_USER, MAIL_PASS)
        server.send_message(msg)

# ✅ Route to serve frontend
@app.route("/")
def index():
    return render_template("otp.html")

# ✅ Route to send OTP
@app.route("/send-otp", methods=["POST"])
def send_otp_route():
    data = request.get_json()
    email = data.get("email")
    otp = str(random.randint(100000, 999999))  # Random 6-digit OTP
    otp_store[email] = otp  # Store OTP for testing
    send_otp(email, otp)
    return jsonify({"status": "success", "otp": otp})

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, request, jsonify
import os, smtplib, random
from email.message import EmailMessage
from dotenv import load_dotenv
from flask_cors import CORS

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# SMTP config from .env
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
MAIL_USER = os.getenv("MAIL_USER")
MAIL_PASS = os.getenv("MAIL_PASS")
MAIL_FROM = os.getenv("MAIL_FROM")

# Simple memory-based OTP store
otp_store = {}

def send_otp(to_email, otp_code):
    msg = EmailMessage()
    msg["Subject"] = "Your OTP Code - Smart AI Security"
    msg["From"] = MAIL_FROM
    msg["To"] = to_email
    msg.set_content(f"Your OTP is: {otp_code}. It expires in 5 minutes.")

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(MAIL_USER, MAIL_PASS)
        server.send_message(msg)

@app.route("/send-otp", methods=["POST"])
def send_otp_route():
    data = request.get_json()
    email = data.get("email")
    if not email:
        return jsonify({"ok": False, "error": "Email required"}), 400

    otp = str(random.randint(100000, 999999))
    otp_store[email] = otp
    try:
        send_otp(email, otp)
        return jsonify({"ok": True, "message": "OTP sent"})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/verify-otp", methods=["POST"])
def verify_otp_route():
    data = request.get_json()
    email = data.get("email")
    otp = data.get("otp")
    if not email or not otp:
        return jsonify({"ok": False, "error": "Missing fields"}), 400

    if email not in otp_store:
        return jsonify({"ok": False, "error": "No OTP found"}), 404

    if otp_store[email] != otp:
        return jsonify({"ok": False, "error": "Invalid OTP"}), 400

    del otp_store[email]  # success → remove OTP
    return jsonify({"ok": True, "message": "OTP verified!"})

if __name__ == "__main__":
    app.run(debug=True)

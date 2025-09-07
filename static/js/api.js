const API_BASE = "http://127.0.0.1:5000";

document.addEventListener("DOMContentLoaded", () => {
  // Login → Send OTP
  const loginForm = document.getElementById("loginForm");
  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const email = document.getElementById("email").value.trim();
      localStorage.setItem("email", email);

      const res = await fetch(`${API_BASE}/send-otp`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email })
      });
      const data = await res.json();
      if (data.ok) {
        alert("OTP sent to your email!");
        window.location.href = "otp.html";
      } else {
        alert("Error: " + data.error);
      }
    });
  }

  // OTP → Verify
  const otpForm = document.getElementById("otpForm");
  if (otpForm) {
    otpForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const otp = document.getElementById("otp").value.trim();
      const email = localStorage.getItem("email");

      const res = await fetch(`${API_BASE}/verify-otp`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, otp })
      });
      const data = await res.json();
      if (data.ok) {
        alert("OTP verified! Redirecting to dashboard...");
        window.location.href = "dashboard.html"; // create later
      } else {
        alert("Error: " + data.error);
      }
    });
  }
});

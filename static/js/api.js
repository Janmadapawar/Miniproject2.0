document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("otp-form");
    const emailInput = document.getElementById("email");
    const messageDiv = document.getElementById("message");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const email = emailInput.value;

        try {
            const response = await fetch("http://127.0.0.1:5000/send-otp", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ email })
            });

            const data = await response.json();

            if (data.status === "success") {
                messageDiv.innerText = `OTP sent to ${email}: ${data.otp}`;
            } else {
                messageDiv.innerText = "Failed to send OTP. Try again.";
            }

        } catch (err) {
            messageDiv.innerText = "Error connecting to backend.";
            console.error(err);
        }
    });
});

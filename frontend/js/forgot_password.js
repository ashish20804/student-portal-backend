const BASE_URL = "http://127.0.0.1:5000";

// Handle Step 1: Sending the OTP
document.getElementById("requestOtpForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("resetEmail").value;
    const sendBtn = document.getElementById("sendOtpBtn");

    sendBtn.innerText = "Sending...";
    sendBtn.disabled = true;

    try {
        const res = await fetch(`${BASE_URL}/forgot-password`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email })
        });

        const data = await res.json();

        if (res.ok) {
            // Switch views
            document.getElementById("requestOtpForm").style.display = "none";
            document.getElementById("resetPasswordForm").style.display = "block";
            document.getElementById("forgotTitle").innerText = "Verify OTP";
            document.getElementById("forgotSubtitle").innerText = `We sent a code to ${email}`;
        } else {
            alert(data.error);
            sendBtn.innerText = "Send OTP";
            sendBtn.disabled = false;
        }
    } catch (err) {
        alert("Connection error. Is the backend running?");
        sendBtn.disabled = false;
    }
});

// Handle Step 2: Verifying OTP and Resetting Password
document.getElementById("resetPasswordForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("resetEmail").value;
    const otp = document.getElementById("otpCode").value;
    const new_password = document.getElementById("newPassword").value;

    const res = await fetch(`${BASE_URL}/reset-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, otp, new_password })
    });

    const data = await res.json();

    if (res.ok) {
        alert("Password updated successfully! Please login.");
        window.location.href = "login.html";
    } else {
        alert(data.error);
    }
});
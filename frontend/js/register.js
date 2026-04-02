const BASE_URL = "http://127.0.0.1:5000";

document.getElementById("registerForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const submitBtn = e.target.querySelector('button[type="submit"]');
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirmPassword").value;

    // 1. Basic Match Check
    if (password !== confirmPassword) {
        alert("⚠️ Passwords do not match");
        return;
    }

    try {
        // --- DISABLE BUTTON IMMEDIATELY ---
        // This stops the delay caused by clicking twice
        submitBtn.disabled = true;
        submitBtn.innerText = "Processing...";

        const res = await fetch(`${BASE_URL}/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });

        const data = await res.json();

        if (res.ok) {
            // This alert will now trigger as soon as the database saves the user
            alert("✨ Registration successful!");
            window.location.href = "login.html";
        } else {
            // If the email already exists, it shows this instead
            alert("⚠️ " + (data.error || "Registration failed"));
            
            // Re-enable the button so the user can fix the email
            submitBtn.disabled = false;
            submitBtn.innerText = "Create Account";
        }
    } catch (err) {
        alert("📡 Server connection failed. Is your Flask backend running?");
        submitBtn.disabled = false;
        submitBtn.innerText = "Create Account";
    }
});
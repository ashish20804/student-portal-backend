document.getElementById("registerForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const submitBtn     = e.target.querySelector('button[type="submit"]');
    const email         = document.getElementById("email").value;
    const password      = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirmPassword").value;

    if (password !== confirmPassword) {
        alert("Passwords do not match");
        return;
    }

    try {
        submitBtn.disabled  = true;
        submitBtn.innerText = "Processing...";

        const res = await fetch(`${CONFIG.API_BASE_URL}/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });

        const data = await res.json();

        if (res.ok) {
            alert("Registration successful!");
            window.location.href = "login.html";
        } else {
            alert(data.error || "Registration failed");
            submitBtn.disabled  = false;
            submitBtn.innerText = "Create Account";
        }
    } catch {
        alert("Server connection failed. Please try again.");
        submitBtn.disabled  = false;
        submitBtn.innerText = "Create Account";
    }
});

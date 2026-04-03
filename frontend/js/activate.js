const token = new URLSearchParams(window.location.search).get("token");

if (!token) {
    showError("Invalid activation link. Please contact your administrator.");
    document.getElementById("activateForm").style.display = "none";
}

document.getElementById("activateForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const password = document.getElementById("password").value;
    const confirm  = document.getElementById("confirmPassword").value;

    if (password.length < 8) { showError("Password must be at least 8 characters."); return; }
    if (password !== confirm) { showError("Passwords do not match."); return; }

    const btn = document.getElementById("activateBtn");
    btn.disabled    = true;
    btn.textContent = "Activating...";

    try {
        const res = await fetch(`${CONFIG.API_BASE_URL}/activate`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ token, password })
        });
        const data = await res.json();
        if (res.ok) {
            document.getElementById("activateForm").style.display = "none";
            showSuccess(data.message + " Redirecting to login...");
            setTimeout(() => window.location.href = "login.html", 2500);
        } else {
            showError(data.error || "Activation failed. The link may have expired.");
            btn.disabled    = false;
            btn.textContent = "Activate & Set Password";
        }
    } catch {
        showError("Could not connect to server.");
        btn.disabled    = false;
        btn.textContent = "Activate & Set Password";
    }
});

function showError(msg) {
    const el = document.getElementById("errorAlert");
    el.textContent = msg;
    el.classList.remove("d-none");
    document.getElementById("successAlert").classList.add("d-none");
}

function showSuccess(msg) {
    const el = document.getElementById("successAlert");
    el.textContent = msg;
    el.classList.remove("d-none");
    document.getElementById("errorAlert").classList.add("d-none");
}

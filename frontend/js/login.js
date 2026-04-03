document.getElementById("loginForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const email    = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const res = await fetch(`${CONFIG.API_BASE_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ email, password })
    });

    const data = await res.json();
    if (res.ok) {
        if (data.role === "admin")        window.location.href = "admin_dashboard.html";
        else if (data.role === "faculty") window.location.href = "faculty_dashboard.html";
        else                              window.location.href = "dashboard.html";
    } else {
        alert(data.error);
    }
});

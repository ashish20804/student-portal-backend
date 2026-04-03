const BASE_URL         = CONFIG.API_BASE_URL;
const ROOT_URL         = CONFIG.API_BASE_URL;
const IMAGE_DISPLAY_URL = `${CONFIG.API_BASE_URL}/student/display-photo`;

window.onload = async () => { await loadDashboard(); };

async function loadDashboard() {
    try {
        const res = await fetch(`${BASE_URL}/student/dashboard`, { method: "GET", credentials: "include" });
        if (res.status === 401 || res.status === 403) { window.location.href = "login.html"; return; }

        const data = await res.json();

        document.getElementById("welcomeHeading").innerText = `Welcome Back, ${data.name || 'Student'}`;
        document.getElementById("userNameDisplay").innerText = data.name || 'Student';
        document.getElementById("userRollDisplay").innerText = data.rollNumber || "---";

        const dept = data.department || 'Not Assigned';
        const sem  = data.semester ? `${data.semester} semester` : 'Semester not set';
        document.getElementById("subHeader").innerText = `${dept}, ${sem}`;

        document.getElementById("sgpa").innerText       = data.sgpa ? parseFloat(data.sgpa).toFixed(1) : "0.0";
        document.getElementById("cgpa").innerText       = data.cgpa ? parseFloat(data.cgpa).toFixed(1) : "0.0";
        document.getElementById("attendance").innerText = (data.attendance_percentage || 0) + "%";

        const initialCircle = document.getElementById("userInitialCircle");
        if (data.profile_image) {
            initialCircle.innerHTML = `<img src="${IMAGE_DISPLAY_URL}/${data.profile_image}?t=${Date.now()}" style="width:100%;height:100%;object-fit:cover;">`;
            initialCircle.classList.remove('bg-primary');
        } else if (data.name) {
            initialCircle.innerHTML = data.name.trim().charAt(0).toUpperCase();
            initialCircle.classList.add('bg-primary');
        }

        if (data.userId) initNotifications(data.userId);
        await loadAnnouncements();

    } catch (err) { console.error("Fetch error:", err); }
}

async function logout() {
    if (!confirm("Are you sure you want to logout?")) return;
    try { await fetch(`${BASE_URL}/logout`, { method: "POST", credentials: "include" }); } catch {}
    window.location.href = "login.html";
}

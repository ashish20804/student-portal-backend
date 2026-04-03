const BASE_URL = `${CONFIG.API_BASE_URL}/admin`;
const AUTH_URL = CONFIG.API_BASE_URL;
const ROOT_URL = CONFIG.API_BASE_URL;

window.onload = async () => {
    await fetchDashboardData();
    await loadAnnouncements();
    try {
        const res = await fetch(`${ROOT_URL}/student/profile`, { credentials: 'include' });
        if (res.ok) {
            const data = await res.json();
            const el = document.getElementById("adminName");
            const av = document.getElementById("adminAvatar");
            if (el) el.innerText = data.name || "Admin User";
            if (av) av.innerText = (data.name || "A").charAt(0).toUpperCase();
            if (data.userId) initNotifications(data.userId);
        }
    } catch { /* silent */ }
};

async function fetchDashboardData() {
    try {
        const res = await fetch(`${BASE_URL}/dashboard`, { method: "GET", credentials: "include" });
        if (res.status === 401 || res.status === 403) { window.location.href = "login.html"; return; }
        if (!res.ok) throw new Error("Server Error");
        const data = await res.json();
        updateElementText("statStudents",   data.total_students);
        updateElementText("statPlaced",     data.placed_students);
        updateElementText("statFaculty",    data.total_faculty);
        updateElementText("statActivities", data.total_activities);
        renderNotifications(data.notifications);
        renderPlacements(data.recent_placements);
    } catch (err) { console.error("Dashboard Sync Error:", err); showErrorState(); }
}

function updateElementText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value !== undefined ? value : 0;
}

function renderNotifications(notifications) {
    const container = document.getElementById("notificationList");
    if (!container) return;
    container.innerHTML = notifications && notifications.length
        ? notifications.map(n => `
            <div class="alert alert-${n.type || 'info'} small py-2 border-0 mb-2 shadow-sm d-flex align-items-center">
                <i class="bi bi-info-circle-fill me-2"></i><div>${n.text}</div>
            </div>`).join('')
        : `<p class="text-muted small p-2">No new notifications.</p>`;
}

function renderPlacements(placements) {
    const container = document.getElementById("placementList");
    if (!container) return;
    container.innerHTML = placements && placements.length
        ? placements.map(p => `
            <div class="d-flex justify-content-between align-items-center mb-3 p-3 bg-white rounded border shadow-sm">
                <div><div class="fw-bold text-dark">${p.name}</div><small class="text-muted">${p.company}</small></div>
                <span class="badge bg-success rounded-pill">${p.package}</span>
            </div>`).join('')
        : `<p class="text-muted small p-2">No recent placements found.</p>`;
}

function showErrorState() {
    ["statStudents","statPlaced","statFaculty","statActivities"].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.textContent = "!";
    });
}

function showAnnouncementModal() { new bootstrap.Modal(document.getElementById('announceModal')).show(); }
function backupDB() { alert('Database backup feature coming soon.'); }

async function sendAnnouncement() {
    const textarea = document.getElementById("announceText");
    const content  = (textarea.value || '').trim();
    if (!content) { alert("Please enter a message."); return; }
    try {
        const res  = await fetch(`${ROOT_URL}/announcements`, {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ content }), credentials: "include"
        });
        const data = await res.json();
        if (res.ok) {
            textarea.value = "";
            bootstrap.Modal.getInstance(document.getElementById('announceModal')).hide();
            await loadAnnouncements();
        } else { alert(data.message || "Failed to post announcement."); }
    } catch { alert("Connection error. Please try again."); }
}

async function logout() {
    if (!confirm("Are you sure you want to logout?")) return;
    try { await fetch(`${AUTH_URL}/logout`, { method: "POST", credentials: "include" }); } catch {}
    localStorage.removeItem("userName");
    localStorage.removeItem("userRole");
    window.location.href = "login.html";
}

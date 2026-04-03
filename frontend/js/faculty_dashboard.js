const BASE_URL         = `${CONFIG.API_BASE_URL}/faculty`;
const ROOT_URL         = CONFIG.API_BASE_URL;
const IMAGE_DISPLAY_URL = `${CONFIG.API_BASE_URL}/student/display-photo`;

window.onload = async function () { await loadFacultyDashboard(); };

async function loadFacultyDashboard() {
    try {
        const response = await fetch(`${BASE_URL}/dashboard`, { credentials: 'include' });
        if (response.status === 401 || response.status === 403) { window.location.href = "login.html"; return; }

        const data = await response.json();
        const name = data.faculty_name || "Faculty Member";

        document.getElementById("navFacultyName").innerText = name;
        document.getElementById("welcomeName").innerText    = name;

        const avatar = document.getElementById("facultyAvatar");
        if (data.profile_image) {
            avatar.innerHTML = `<img src="${IMAGE_DISPLAY_URL}/${data.profile_image}?t=${Date.now()}" style="width:100%;height:100%;object-fit:cover;border-radius:50%;">`;
        } else {
            avatar.innerText = name.charAt(0).toUpperCase();
        }

        document.getElementById("statPlaced").innerText          = data.placed_students || 0;
        document.getElementById("statHigherStudies").innerText   = data.higher_studies_count || 0;
        document.getElementById("statExtracurricular").innerText = data.extracurricular_count || 0;
        document.getElementById("statActivities").innerText      = data.total_activities || 0;

        const perms = data.permissions || [];
        if (perms.includes("view_placement"))      { document.getElementById("stat-card-placement")?.classList.remove("d-none"); document.getElementById("action-placement-details")?.classList.remove("d-none"); }
        if (perms.includes("view_higher_studies")) { document.getElementById("stat-card-higher-studies")?.classList.remove("d-none"); document.getElementById("action-higher-studies")?.classList.remove("d-none"); }
        if (perms.includes("view_activities"))     { document.getElementById("stat-card-activities")?.classList.remove("d-none"); document.getElementById("stat-card-organised")?.classList.remove("d-none"); document.getElementById("action-activity-list")?.classList.remove("d-none"); }
        if (perms.includes("post_announcement"))   { document.getElementById("action-announcement")?.classList.remove("d-none"); }

        if (data.userId) initNotifications(data.userId);
        await loadAnnouncements();

    } catch (error) { console.error("Dashboard Load Error:", error); }
}

async function logout() {
    try { await fetch(`${ROOT_URL}/logout`, { method: "POST", credentials: 'include' }); } catch {}
    window.location.href = "login.html";
}

const ROOT_URL = CONFIG.API_BASE_URL;
let allActivities = [];

window.onload = loadActivityData;

async function loadActivityData() {
    try {
        const res = await fetch(`${ROOT_URL}/faculty/all-activities`, { credentials: "include" });
        if (res.status === 401 || res.status === 403) { window.location.href = "login.html"; return; }
        if (!res.ok) throw new Error();
        allActivities = await res.json();
        populateCategoryDropdown();
        applyFilters();
    } catch {
        document.getElementById("activityTable").innerHTML =
            `<tr><td colspan="7" class="text-center py-4 text-danger">Error loading activities.</td></tr>`;
    }

    ["searchInput", "filterCategory", "filterLevel"].forEach(id =>
        document.getElementById(id).addEventListener("input", applyFilters)
    );
}

function populateCategoryDropdown() {
    const sel = document.getElementById("filterCategory");
    const cats = [...new Set(allActivities.map(a => a.category).filter(Boolean))].sort();
    cats.forEach(cat => {
        const opt = document.createElement("option");
        opt.value = cat; opt.textContent = cat;
        sel.appendChild(opt);
    });
}

function applyFilters() {
    const q    = document.getElementById("searchInput").value.trim().toLowerCase();
    const cat  = document.getElementById("filterCategory").value;
    const lvl  = document.getElementById("filterLevel").value;

    const filtered = allActivities.filter(a => {
        const name   = (a.student_name || "").toLowerCase();
        const rollNo = (a.roll_no || "").toLowerCase();
        return (!q   || name.includes(q) || rollNo.includes(q))
            && (!cat || a.category === cat)
            && (!lvl || a.level === lvl);
    });

    renderTable(filtered);
}

function clearFilters() {
    document.getElementById("searchInput").value = "";
    document.getElementById("filterCategory").value = "";
    document.getElementById("filterLevel").value = "";
    applyFilters();
}

function renderTable(data) {
    document.getElementById("recordCount").textContent = data.length;
    const tbody = document.getElementById("activityTable");

    if (!data.length) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-muted">No records match your filters.</td></tr>`;
        return;
    }

    tbody.innerHTML = data.map(act => `
        <tr>
            <td>${act.student_name}</td>
            <td class="text-muted">${act.roll_no || "—"}</td>
            <td>${act.activityName}</td>
            <td><span class="badge bg-light text-dark border">${act.category}</span></td>
            <td>${act.level}</td>
            <td>${act.achievement || "—"}</td>
            <td>
                ${act.doc_path
                    ? `<a href="${ROOT_URL}/faculty/view-proof/${act.doc_path}" target="_blank" class="btn btn-sm btn-outline-success">
                        <i class="bi bi-patch-check me-1"></i>Certificate</a>`
                    : `<span class="text-muted small">Not Uploaded</span>`}
            </td>
        </tr>`).join("");
}

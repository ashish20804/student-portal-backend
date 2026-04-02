const ROOT_URL = "http://127.0.0.1:5000";
let allPlacements = [];

window.onload = loadPlacementData;

async function loadPlacementData() {
    try {
        const res = await fetch(`${ROOT_URL}/faculty/all-placements`, { credentials: "include" });
        if (res.status === 401 || res.status === 403) { window.location.href = "login.html"; return; }
        if (!res.ok) throw new Error();
        allPlacements = await res.json();
        applyFilters();
    } catch {
        document.getElementById("placementTable").innerHTML =
            `<tr><td colspan="6" class="text-center py-4 text-danger">Could not fetch placement records.</td></tr>`;
    }

    ["searchInput", "filterCompany", "filterRole"].forEach(id =>
        document.getElementById(id).addEventListener("input", applyFilters)
    );
}

function applyFilters() {
    const q      = document.getElementById("searchInput").value.trim().toLowerCase();
    const comp   = document.getElementById("filterCompany").value.trim().toLowerCase();
    const role   = document.getElementById("filterRole").value.trim().toLowerCase();

    const filtered = allPlacements.filter(p => {
        const name    = (p.student_name || "").toLowerCase();
        const rollNo  = (p.roll_no || "").toLowerCase();
        const company = (p.companyName || "").toLowerCase();
        const jobRole = (p.jobRole || "").toLowerCase();
        return (!q    || name.includes(q) || rollNo.includes(q))
            && (!comp || company.includes(comp))
            && (!role || jobRole.includes(role));
    });

    renderTable(filtered);
}

function clearFilters() {
    ["searchInput", "filterCompany", "filterRole"].forEach(id =>
        document.getElementById(id).value = ""
    );
    applyFilters();
}

function renderTable(data) {
    document.getElementById("recordCount").textContent = data.length;
    const tbody = document.getElementById("placementTable");

    if (!data.length) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center py-4 text-muted">No records match your filters.</td></tr>`;
        return;
    }

    tbody.innerHTML = data.map(p => `
        <tr>
            <td>${p.student_name}</td>
            <td class="text-muted">${p.roll_no || "—"}</td>
            <td>${p.companyName}</td>
            <td>${p.jobRole}</td>
            <td class="text-success fw-semibold">${p.package ? p.package + " LPA" : "N/A"}</td>
            <td>
                ${p.doc_path
                    ? `<a href="${ROOT_URL}/faculty/view-proof/${p.doc_path}" target="_blank" class="btn btn-sm btn-outline-primary">
                        <i class="bi bi-file-earmark-arrow-down me-1"></i>Offer Letter</a>`
                    : `<span class="badge bg-warning-subtle text-warning border border-warning-subtle">Not Uploaded</span>`}
            </td>
        </tr>`).join("");
}

const ROOT_URL = CONFIG.API_BASE_URL;
let allRecords = [];

window.onload = loadHigherStudiesData;

async function loadHigherStudiesData() {
    try {
        const res = await fetch(`${ROOT_URL}/faculty/all-higher-studies`, { credentials: "include" });
        if (res.status === 401 || res.status === 403) { window.location.href = "login.html"; return; }
        if (!res.ok) throw new Error();
        allRecords = await res.json();
        applyFilters();
    } catch {
        document.getElementById("higherStudiesTable").innerHTML =
            `<tr><td colspan="7" class="text-center py-4 text-danger">Failed to connect to server.</td></tr>`;
    }

    ["searchInput", "filterUniversity", "filterStatus"].forEach(id =>
        document.getElementById(id).addEventListener("input", applyFilters)
    );
}

function applyFilters() {
    const q      = document.getElementById("searchInput").value.trim().toLowerCase();
    const uni    = document.getElementById("filterUniversity").value.trim().toLowerCase();
    const status = document.getElementById("filterStatus").value;

    const filtered = allRecords.filter(r => {
        const name   = (r.student_name || "").toLowerCase();
        const rollNo = (r.roll_no || "").toLowerCase();
        const univ   = (r.university || "").toLowerCase();
        return (!q      || name.includes(q) || rollNo.includes(q))
            && (!uni    || univ.includes(uni))
            && (!status || r.admissionStatus === status);
    });

    renderTable(filtered);
}

function clearFilters() {
    document.getElementById("searchInput").value = "";
    document.getElementById("filterUniversity").value = "";
    document.getElementById("filterStatus").value = "";
    applyFilters();
}

function renderTable(data) {
    document.getElementById("recordCount").textContent = data.length;
    const tbody = document.getElementById("higherStudiesTable");

    if (!data.length) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-muted">No records match your filters.</td></tr>`;
        return;
    }

    const statusClass = {
        "Selected": "bg-success-subtle text-success border-success-subtle",
        "Applied":  "bg-primary-subtle text-primary border-primary-subtle",
        "Pending":  "bg-warning-subtle text-warning border-warning-subtle",
    };

    tbody.innerHTML = data.map(r => `
        <tr>
            <td>${r.student_name}</td>
            <td class="text-muted">${r.roll_no || "—"}</td>
            <td>${r.university}</td>
            <td>${r.courseName}</td>
            <td>${r.country}</td>
            <td>
                <span class="badge border ${statusClass[r.admissionStatus] || "bg-secondary-subtle text-secondary"}">
                    ${r.admissionStatus}
                </span>
            </td>
            <td>
                ${r.doc_path
                    ? `<a href="${ROOT_URL}/faculty/view-proof/${r.doc_path}" target="_blank" class="btn btn-sm btn-outline-danger">
                        <i class="bi bi-file-earmark-pdf me-1"></i>View Proof</a>`
                    : `<span class="badge bg-light text-muted border"><i class="bi bi-x-circle me-1"></i>No Doc</span>`}
            </td>
        </tr>`).join("");
}

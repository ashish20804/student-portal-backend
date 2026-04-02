const API_URL = "http://127.0.0.1:5000/placement";
const MAX_SIZE_BYTES = 1024 * 1024; // 1MB for testing (Change to 20 * 1024 * 1024 later)

window.onload = loadPlacementData;

async function loadPlacementData() {
    try {
        const res = await fetch(`${API_URL}/`, { credentials: "include" });
        if (!res.ok) return;
        const data = await res.json();
        
        const badge = document.getElementById('currentStatusBadge');
        const icon = document.getElementById('statusIcon');

        const isPlaced = data.some(p => p.status === 'Selected');

        if (isPlaced) {
            badge.className = "badge bg-success text-white px-3 py-2";
            badge.innerText = "Placed";
            icon.className = "bi bi-check-circle-fill text-success fs-4 me-3";
        } else {
            badge.className = "badge badge-not-placed px-3 py-2";
            badge.innerText = "Not Placed";
            icon.className = "bi bi-x-circle text-danger fs-4 me-3";
        }

        renderHistory(data);
    } catch (err) {
        console.error("Error loading placement data:", err);
    }
}

function toggleForm() {
    const section = document.getElementById('placementFormSection');
    section.classList.toggle('d-none');
}

// SUBMIT FORM WITH FILE SIZE VALIDATION (Matching Higher Studies logic)
document.getElementById("placementForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const fileInput = document.getElementById("proof_file");

    // 1. Validate if file exists and check size during submission
    if (fileInput.files.length > 0) {
        const selectedFile = fileInput.files[0];
        if (selectedFile.size > MAX_SIZE_BYTES) {
            alert(`❌ File Too Large: "${selectedFile.name}" is over 20MB. Please compress the PDF or choose a smaller file.`);
            fileInput.value = ""; // Clear the input for the user
            return; // Stop the submission
        }
    } else {
        alert("⚠️ Please upload the Offer Letter (PDF) to proceed.");
        return;
    }

    // 2. Prepare FormData for the API
    const formData = new FormData();
    formData.append("companyName", document.getElementById("companyName").value);
    formData.append("jobRole", document.getElementById("jobRole").value);
    formData.append("package", document.getElementById("package").value);
    formData.append("placementYear", document.getElementById("placementYear").value);
    formData.append("status", document.getElementById("status").value);
    formData.append("proof_file", fileInput.files[0]);

    try {
        const res = await fetch(`${API_URL}/`, {
            method: "POST",
            credentials: "include",
            body: formData 
        });

        if (res.ok) {
            alert("✨ Placement record and offer letter saved!");
            document.getElementById("placementForm").reset();
            toggleForm();
            loadPlacementData();
        } else {
            const result = await res.json();
            // This catches the 413 error from your Flask errorhandler
            alert("Upload Error: " + (result.error || "Could not save record."));
        }
    } catch (err) {
        alert("Server connection failed. The file might be too large for your network connection.");
    }
});

function renderHistory(list) {
    const container = document.getElementById("placementHistory");
    if (!list || list.length === 0) {
        container.innerHTML = `<p class="text-center text-muted">No history found</p>`;
        return;
    }

    container.innerHTML = list.map(p => {
        let statusBadgeClass = "bg-warning-subtle"; 
        if (p.status === 'Selected') statusBadgeClass = "bg-success-subtle";
        if (p.status === 'Rejected') statusBadgeClass = "bg-danger-subtle";

        return `
        <div class="history-card p-3 mb-3 bg-white shadow-sm">
            <div class="d-flex justify-content-between align-items-start">
                <div>
                    <h6 class="fw-bold mb-1"><i class="bi bi-building me-2"></i>${p.companyName}</h6>
                    <p class="small text-muted mb-2">${p.jobRole}</p>
                    <span class="badge ${statusBadgeClass} px-3 mb-2">
                        ${p.status === 'Rejected' ? 'Not Selected' : p.status}
                    </span>
                    ${p.hasProof ? 
                        `<div class="mt-2">
                            <a href="${API_URL}/view-proof/${p.id}" target="_blank" class="small text-decoration-none">
                                <i class="bi bi-file-earmark-pdf text-danger me-1"></i>View Offer Letter
                            </a>
                        </div>` : ''
                    }
                </div>
                <div class="text-end">
                    <span class="badge bg-success-subtle mb-2 text-dark">${p.package || 'N/A'}</span>
                    <div class="small text-muted">
                        <i class="bi bi-calendar-event me-1"></i>${p.placementYear || ''}
                    </div>
                </div>
            </div>
        </div>
    `}).join('');
}
const API_URL = `${CONFIG.API_BASE_URL}/higherstudies`;

window.onload = loadPageData;

async function loadPageData() {
    const container = document.getElementById("applicationsContainer");
    try {
        const res = await fetch(`${API_URL}/`, { credentials: "include" });
        if (!res.ok) throw new Error("Session expired");
        
        const data = await res.json();
        updatePlanningUI(data.isPlanning);
        renderApplications(data.applications);
    } catch (err) {
        console.error("Load Error:", err);
    }
}

async function setPlanningStatus(status) {
    try {
        const res = await fetch(`${API_URL}/toggle-planning`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({ status: status })
        });
        if (res.ok) {
            updatePlanningUI(status);
            if(!status) document.getElementById('formSection').classList.add('d-none');
        }
    } catch (err) { alert("Error updating status"); }
}

function updatePlanningUI(isPlanning) {
    const yesBtn = document.getElementById('planYes');
    const noBtn = document.getElementById('planNo');
    const addBtn = document.getElementById('addAppBtn');
    if (isPlanning) {
        yesBtn.className = "btn btn-primary w-50 py-1";
        noBtn.className = "btn btn-outline-secondary w-50 py-1";
        addBtn.classList.remove('d-none');
    } else {
        noBtn.className = "btn btn-secondary w-50 py-1";
        yesBtn.className = "btn btn-outline-primary w-50 py-1";
        addBtn.classList.add('d-none');
    }
}

function toggleForm() {
    document.getElementById('formSection').classList.toggle('d-none');
}

// SUBMIT FORM WITH FILE SIZE VALIDATION
document.getElementById("higherStudiesForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const fileInput = document.getElementById("proof_file");
    const maxSizeInBytes =  1024 * 1024; // 20MB

    // 1. Validate if file exists and check size before uploading
    if (fileInput.files.length > 0) {
        const selectedFile = fileInput.files[0];
        if (selectedFile.size > maxSizeInBytes) {
            alert(`❌ File Too Large: "${selectedFile.name}" is over 20MB. Please compress the PDF or choose a smaller file.`);
            fileInput.value = ""; // Clear the input for the user
            return; // Stop the submission
        }
    } else {
        alert("⚠️ Please upload a PDF proof (Admission Letter/Application) to proceed.");
        return;
    }

    // 2. Prepare FormData for the API
    const formData = new FormData();
    formData.append("university", document.getElementById("university").value);
    formData.append("courseName", document.getElementById("courseName").value);
    formData.append("country", document.getElementById("country").value);
    formData.append("admissionStatus", document.getElementById("admissionStatus").value);
    formData.append("applicationDate", document.getElementById("applicationDate").value);
    formData.append("proof_file", fileInput.files[0]);

    try {
        // Optional: You could add a 'Uploading...' state to the button here
        const res = await fetch(`${API_URL}/`, {
            method: "POST",
            credentials: "include", 
            body: formData
        });

        if (res.ok) {
            alert("✨ Application and Proof saved successfully!"); 
            e.target.reset();
            toggleForm();
            loadPageData();
        } else {
            const result = await res.json();
            // This catches the 413 error from Flask if the backend rejects it
            alert("Upload Error: " + (result.error || "Could not save application."));
        }
    } catch (err) {
        alert("Server connection failed. The file might be too large for your network connection.");
    }
});

function renderApplications(apps) {
    const container = document.getElementById("applicationsContainer");
    if (!apps || apps.length === 0) {
        container.innerHTML = `<p class="text-muted text-center py-3">No applications found.</p>`;
        return;
    }

    container.innerHTML = apps.map(app => `
        <div class="border rounded-3 p-3 mb-3 d-flex justify-content-between align-items-center bg-white shadow-sm">
            <div>
                <h6 class="fw-bold mb-1"><i class="bi bi-bank me-2 text-primary"></i>${app.university}</h6>
                <p class="small text-muted mb-0">${app.courseName} | ${app.country}</p>
                ${app.hasProof ? 
                    `<a href="${API_URL}/view-proof/${app.id}" target="_blank" class="btn btn-sm btn-link p-0 mt-2 text-decoration-none">
                        <i class="bi bi-file-earmark-pdf text-danger"></i> View Admission Letter
                    </a>` : 
                    `<span class="small text-warning mt-2 d-block"><i class="bi bi-exclamation-circle"></i> No proof uploaded</span>`
                }
            </div>
            <div class="text-end">
                <span class="badge bg-primary-subtle text-primary mb-2">${app.admissionStatus}</span>
                <div class="small text-muted">${app.applicationDate || ''}</div>
            </div>
        </div>
    `).join('');
}
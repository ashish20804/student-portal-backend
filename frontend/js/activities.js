const ACT_URL = `${CONFIG.API_BASE_URL}/activity`;
const COM_URL = `${CONFIG.API_BASE_URL}/committee`;

const MAX_SIZE_BYTES = 1024 * 1024; 

window.onload = () => {
    loadActivities();
    loadCommittees();
};

function toggleForm(type) {
    const modal = document.getElementById(`${type}Modal`);
    modal.classList.toggle('d-none');
}

// ------------------- ACTIVITIES -------------------
async function loadActivities() {
    try {
        const res = await fetch(`${ACT_URL}/my`, { credentials: "include" });
        const data = await res.json();
        const container = document.getElementById("activityList");

        if (!data || data.length === 0) {
            container.innerHTML = `<p class="text-muted text-center py-3">No activities added yet.</p>`;
            return;
        }

        container.innerHTML = data.map(act => `
            <div class="card p-3 mb-3 border-start border-4 shadow-sm" style="border-color: var(--purple-brand) !important;">
                <h6 class="fw-bold mb-1">${act.activityName}</h6>
                <p class="small text-muted mb-2">${act.category || 'General'}</p>
                <div class="d-flex justify-content-between align-items-center">
                    <span class="small text-secondary">
                        <i class="bi bi-trophy me-1"></i>${act.achievement || 'Participant'}
                    </span>
                    ${act.hasCertificate ? 
                        `<a href="${ACT_URL}/view-cert/${act.activityId}" target="_blank" class="small text-decoration-none fw-bold" style="color: var(--purple-brand)">
                            <i class="bi bi-file-earmark-check me-1"></i>View Certificate
                        </a>` : 
                        `<span class="small text-muted italic">No certificate</span>`
                    }
                </div>
            </div>
        `).join('');
    } catch (err) { console.error("Load failed", err); }
}

document.getElementById("activityForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    
    const fileInput = document.getElementById("certFile");
    const formData = new FormData();
    
    // 1. Validate file size during submission
    if (fileInput && fileInput.files.length > 0) {
        const selectedFile = fileInput.files[0];
        if (selectedFile.size > MAX_SIZE_BYTES) {
            alert(`❌ File Too Large: "${selectedFile.name}" is over the 1MB limit. Please upload a smaller certificate.`);
            fileInput.value = ""; // Clear the input
            return; // Stop submission
        }
        formData.append("certificate", selectedFile);
    }

    // 2. Prepare remaining data
    formData.append("activityName", document.getElementById("actName").value);
    formData.append("category", document.getElementById("actCat").value);
    formData.append("achievement", document.getElementById("actAch").value);
    
    try {
        const res = await fetch(`${ACT_URL}/`, {
            method: "POST",
            credentials: "include",
            body: formData
        });

        if (res.ok) {
            alert("✨ Activity saved successfully!");
            e.target.reset();
            toggleForm('activity');
            loadActivities();
        } else {
            const errData = await res.json();
            alert("Upload Error: " + (errData.error || "Failed to save activity"));
        }
    } catch (err) {
        alert("Server connection failed. The file might be too large for your network.");
    }
});

// ------------------- COMMITTEES -------------------
async function loadCommittees() {
    try {
        const res = await fetch(`${COM_URL}/my`, { credentials: "include" });
        const data = await res.json();
        const container = document.getElementById("committeeList");

        if (!data || data.length === 0) {
            container.innerHTML = `<p class="text-muted text-center py-3">No committees joined.</p>`;
            return;
        }

        container.innerHTML = data.map(com => `
            <div class="card p-3 mb-3 d-flex flex-row align-items-start shadow-sm">
                <div class="committee-icon me-3"><i class="bi bi-people-fill"></i></div>
                <div>
                    <h6 class="fw-bold mb-0">${com.committeeName}</h6>
                    <p class="small text-primary mb-1">${com.role || 'Member'}</p>
                    <p class="extra-small text-muted" style="font-size: 0.7rem;">
                        <i class="bi bi-calendar-check me-1"></i>Joined: ${new Date(com.joinDate).toLocaleDateString()}
                    </p>
                </div>
            </div>
        `).join('');
    } catch (err) { console.error("Load failed", err); }
}

document.getElementById("committeeForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {
        committeeName: document.getElementById("comName").value,
        type: document.getElementById("comType").value
    };

    try {
        const res = await fetch(`${COM_URL}/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify(payload)
        });

        if (res.ok) {
            alert("🤝 Successfully joined the committee!");
            e.target.reset();
            toggleForm('committee');
            loadCommittees();
        } else {
            alert("Failed to join committee.");
        }
    } catch (err) {
        alert("Server connection error.");
    }
});
const BASE_URL = `${CONFIG.API_BASE_URL}/faculty`;
let selectedStudent = null;
let userPermissions = [];

// ─── FETCH STUDENT LIST ───────────────────────────────────────────────────────

async function fetchStudents() {
    const tableBody = document.getElementById('studentTableBody');
    tableBody.innerHTML = '<tr><td colspan="6" class="text-center py-4"><div class="spinner-border text-primary spinner-border-sm me-2"></div>Loading...</td></tr>';

    const params = new URLSearchParams({
        search:     document.getElementById('searchInput').value,
        semester:   document.getElementById('semesterFilter').value,
        department: document.getElementById('deptFilter').value
    });

    try {
        const res = await fetch(`${BASE_URL}/students?${params}`, { credentials: 'include' });

        if (res.status === 401) { window.location.href = "login.html"; return; }
        if (res.status === 403) {
            tableBody.innerHTML = `<tr><td colspan="6" class="text-center text-danger py-4">
                Access Denied. <a href="login.html" class="btn btn-sm btn-outline-danger ms-2">Login</a>
            </td></tr>`;
            return;
        }

        const students = await res.json();

        if (!students.length) {
            tableBody.innerHTML = '<tr><td colspan="6" class="text-center py-4 text-muted">No students found.</td></tr>';
            return;
        }

        tableBody.innerHTML = students.map(s => `
            <tr>
                <td class="ps-4 fw-bold text-primary">${s.rollNumber || 'N/A'}</td>
                <td>${s.name}</td>
                <td class="text-muted small">${s.email}</td>
                <td><span class="badge bg-primary-subtle text-primary px-3">${s.department || 'N/A'}</span></td>
                <td>Semester ${s.semester || 'N/A'}</td>
                <td class="text-end pe-4">
                    <button onclick="messageStudent(${s.userId}, '${s.name}')"
                            class="btn btn-sm btn-outline-primary me-1" title="Message">
                        <i class="bi bi-chat-dots"></i>
                    </button>
                    <button onclick="openProfile(${s.userId})" class="btn btn-sm btn-primary">
                        <i class="bi bi-eye"></i> View Details
                    </button>
                </td>
            </tr>`).join('');

    } catch (e) {
        tableBody.innerHTML = '<tr><td colspan="6" class="text-center text-danger py-4">Error connecting to server.</td></tr>';
    }
}

// ─── OPEN STUDENT PROFILE ─────────────────────────────────────────────────────

async function openProfile(userId) {
    document.getElementById('listView').classList.add('d-none');
    document.getElementById('profileView').classList.remove('d-none');
    document.getElementById('headerTitle').innerText = "Student Details";
    document.getElementById('tabContent').innerHTML = '<div class="text-center py-5"><div class="spinner-border text-primary"></div></div>';

    try {
        const res = await fetch(`${BASE_URL}/student/${userId}`, { credentials: 'include' });
        const data = await res.json();

        if (!res.ok) {
            document.getElementById('tabContent').innerHTML = `<div class="alert alert-danger">${data.message || 'Failed to load.'}</div>`;
            return;
        }

        selectedStudent = data;
        userPermissions = data.permissions || [];

        const info = data.basic_info;
        document.getElementById('profName').innerText    = info.name;
        document.getElementById('profRoll').innerText    = info.rollNumber || 'N/A';
        document.getElementById('profEmail').innerText   = info.email;
        document.getElementById('profDept').innerText    = info.department || 'N/A';
        document.getElementById('profSem').innerText     = `Semester ${info.semester || 'N/A'}`;
        document.getElementById('profInit').innerText    = info.name.charAt(0).toUpperCase();
        document.getElementById('profPhone').innerText   = info.phone || 'N/A';
        document.getElementById('profAddress').innerText = info.address || 'N/A';

        buildTabs();

    } catch (e) {
        console.error("Profile load error:", e);
        document.getElementById('tabContent').innerHTML = `<div class="alert alert-danger">Error loading profile.</div>`;
    }
}

// ─── BUILD TABS BASED ON PERMISSIONS ─────────────────────────────────────────

function buildTabs() {
    const nav = document.getElementById('permissionTabsNav');

    // permission → tab ids it controls
    const permToTabs = {
        'view_placement':      ['placement'],
        'view_higher_studies': ['higher'],
        'view_activities':     ['curricular', 'extra']
    };

    // Hide all tabs first
    ['placement', 'higher', 'curricular', 'extra'].forEach(id => {
        document.getElementById(`tab-${id}`).classList.add('d-none');
    });

    let firstVisibleTab = null;

    Object.entries(permToTabs).forEach(([perm, tabIds]) => {
        if (userPermissions.includes(perm)) {
            tabIds.forEach(id => {
                document.getElementById(`tab-${id}`).classList.remove('d-none');
                if (!firstVisibleTab) firstVisibleTab = id;
            });
        }
    });

    if (!firstVisibleTab) {
        nav.classList.add('d-none');
        document.getElementById('tabContent').innerHTML = `
            <div class="alert alert-warning">
                <i class="bi bi-lock me-2"></i>You do not have permission to view student details.
                Contact admin to grant access.
            </div>`;
        return;
    }

    nav.classList.remove('d-none');
    showTab(firstVisibleTab);
}

// ─── RENDER TAB CONTENT ───────────────────────────────────────────────────────

function showTab(type) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active-tab'));
    const activeBtn = document.getElementById(`tab-${type}`);
    if (activeBtn) activeBtn.classList.add('active-tab');

    const content = document.getElementById('tabContent');
    const student = selectedStudent;

    if (type === 'placement') {
        const p = student.placement;
        const isPlaced = p && p.status === 'Selected';
        content.innerHTML = `
            <div class="card border-0 shadow-sm p-4">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h5 class="fw-bold mb-0">Placement Information</h5>
                    <span class="status-pill ${isPlaced ? '' : 'bg-danger-subtle text-danger border border-danger-subtle'}">
                        ${isPlaced ? 'Placed' : 'Not Placed'}
                    </span>
                </div>
                ${p ? `
                <div class="row g-3">
                    <div class="col-md-6"><div class="info-card"><small class="text-muted">Company</small><br><strong>${p.companyName || 'N/A'}</strong></div></div>
                    <div class="col-md-6"><div class="info-card"><small class="text-muted">Job Role</small><br><strong>${p.jobRole || 'N/A'}</strong></div></div>
                    <div class="col-md-6"><div class="info-card"><small class="text-muted">Package</small><br><strong>${p.package ? p.package + ' LPA' : 'N/A'}</strong></div></div>
                    <div class="col-md-6"><div class="info-card"><small class="text-muted">Year</small><br><strong>${p.placementYear || 'N/A'}</strong></div></div>
                </div>` : '<p class="text-muted">No placement record found.</p>'}
            </div>`;

    } else if (type === 'higher') {
        const list = student.higher_studies || [];
        content.innerHTML = `
            <div class="card border-0 shadow-sm p-4">
                <h5 class="fw-bold mb-4">Higher Studies</h5>
                ${list.length ? list.map(h => `
                    <div class="info-card mb-3">
                        <strong>${h.university || 'N/A'}</strong>
                        <br><small class="text-muted">${h.course || 'N/A'} &bull; ${h.country || 'N/A'}</small>
                        <br><span class="badge bg-info-subtle text-info mt-1">${h.status || 'N/A'}</span>
                    </div>`).join('') : '<p class="text-muted">No higher studies records found.</p>'}
            </div>`;

    } else if (type === 'curricular' || type === 'extra') {
        const CURRICULAR_CATS = ['Academic', 'Research', 'Technical', 'Curricular'];
        const EXTRA_CATS      = ['Sports', 'Cultural', 'Social', 'Extracurricular', 'Other'];

        const all  = student.activities || [];
        const acts = all.filter(a =>
            type === 'curricular'
                ? CURRICULAR_CATS.includes(a.category)
                : EXTRA_CATS.includes(a.category)
        );

        content.innerHTML = `
            <div class="card border-0 shadow-sm p-4">
                <h5 class="fw-bold mb-4">${type === 'curricular' ? 'Curricular' : 'Extracurricular'} Activities</h5>
                ${acts.length ? acts.map(a => `
                    <div class="info-card mb-3">
                        <strong>${a.activityName}</strong>
                        <br><small class="text-muted">${a.category || 'N/A'} &bull; Level: ${a.level || 'N/A'}</small>
                        ${a.achievement ? `<br><span class="badge bg-success-subtle text-success mt-1">${a.achievement}</span>` : ''}
                    </div>`).join('') : `<p class="text-muted">No ${type === 'curricular' ? 'curricular' : 'extracurricular'} activities found.</p>`}
            </div>`;
    }
}

// ─── NAVIGATION ───────────────────────────────────────────────────────────────

function messageStudent(userId, name) {
    window.location.href = `messages.html?userId=${userId}&name=${encodeURIComponent(name)}`;
}

function handleBackNavigation() {
    if (!document.getElementById('profileView').classList.contains('d-none')) {
        document.getElementById('profileView').classList.add('d-none');
        document.getElementById('listView').classList.remove('d-none');
        document.getElementById('headerTitle').innerText = "Student List";
        selectedStudent = null;
        userPermissions = [];
    } else {
        window.location.href = "faculty_dashboard.html";
    }
}

window.onload = fetchStudents;

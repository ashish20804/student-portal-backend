const BASE_URL = `${CONFIG.API_BASE_URL}/admin`;
let selectedUserId = null;

console.log("✅ user_management.js loaded successfully");

// Initial load
window.onload = fetchUsers;

/**
 * Fetches all users from the backend with optional search and department filters.
 */
async function fetchUsers() {
    const search = document.getElementById("userSearch").value;
    const role = document.getElementById("roleFilter").value;
    const dept = document.getElementById("deptFilter").value;

    const params = new URLSearchParams();
    if (search) params.append("search", search);
    if (dept) params.append("department", dept);

    try {
        const res = await fetch(`${BASE_URL}/users?${params.toString()}`, { 
            method: "GET",
            credentials: "include" 
        });

        if (!res.ok) {
            if (res.status === 403) alert("Access Denied: Admin role required.");
            throw new Error("Failed to fetch users");
        }

        const users = await res.json();
        const tbody = document.getElementById("userTableBody");
        
        const filteredUsers = users.filter(u => !role || u.role === role);

        if (filteredUsers.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="text-center py-4 text-muted">No users found matching your criteria.</td></tr>`;
            return;
        }

        tbody.innerHTML = filteredUsers.map(user => `
            <tr>
                <td class="ps-4 fw-bold text-muted">${user.userId}</td>
                <td><div class="fw-bold">${user.name}</div></td>
                <td class="small text-muted">${user.email}</td>
                <td><span class="badge ${getRoleBadge(user.role)}">${user.role.toUpperCase()}</span></td>
                <td>${user.department || 'N/A'}</td>
                <td class="text-end pe-4">
                    <div class="dropdown">
                        <button class="btn btn-light btn-sm rounded-circle" data-bs-toggle="dropdown">
                            <i class="bi bi-three-dots-vertical"></i>
                        </button>
                        <ul class="dropdown-menu dropdown-menu-end shadow border-0">
                            <li>
                                <button class="dropdown-item" onclick='prepareAndOpenModal(${JSON.stringify(user)})'>
                                    <i class="bi bi-shield-lock me-2"></i> Edit Access
                                </button>
                            </li>
                            ${user.role === 'student' ? `
                            <li>
                                <button class="dropdown-item" onclick='openAcademicModal(${JSON.stringify(user)})'>
                                    <i class="bi bi-mortarboard me-2"></i> Update Academic Details
                                </button>
                            </li>
                            ` : ''}
                            <li><hr class="dropdown-divider"></li>
                            <li>
                                <button class="dropdown-item text-danger" onclick="deleteUser(${user.userId}, '${user.name}')">
                                    <i class="bi bi-trash me-2"></i> Remove User
                                </button>
                            </li>
                        </ul>
                    </div>
                </td>
            </tr>
        `).join('');
    } catch (err) {
        console.error("Fetch Error:", err);
    }
}

/**
 * --- NEW: ADD USER MODAL LOGIC ---
 */

// Updates UI based on Role selection
function updateAddButtonText() {
    console.log("🔵 updateAddButtonText() called");
    const role = document.getElementById("addRole").value;
    const btn = document.getElementById("btnNextAction");
    
    btn.innerText = `Create ${role.charAt(0).toUpperCase() + role.slice(1)} Account`;
    console.log("Button text updated to:", btn.innerText);
}

// Resets modal state when closed
function resetAddUserModal() {
    document.getElementById("addName").value = "";
    document.getElementById("addEmail").value = "";
    document.getElementById("addRole").value = "faculty";
    document.getElementById("addDept").value = "CSE";
    updateAddButtonText();
}

// Decides whether to submit immediately or go to Step 2
async function handleUserCreationFlow() {
    console.log("🔵 handleUserCreationFlow() called");
    const role = document.getElementById("addRole").value;
    await submitUserData({
        name: document.getElementById("addName").value,
        email: document.getElementById("addEmail").value,
        role: role,
        department: document.getElementById("addDept").value
    });
}

// Core POST request for adding users
async function submitUserData(payload) {
    if (!payload.name || !payload.email) {
        alert("Please fill in all required fields: Name and Email.");
        return;
    }

    console.log("📤 Submitting user data:", payload);

    try {
        const res = await fetch(`${BASE_URL}/users/add`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
            credentials: "include"
        });

        const result = await res.json();
        console.log("📥 Server response:", result);

        if (res.ok) {
            alert(result.message || "User created successfully! Credentials sent via email.");
            bootstrap.Modal.getInstance(document.getElementById('addUserModal')).hide();
            resetAddUserModal();
            fetchUsers();
        } else {
            alert(`Error: ${result.message || result.error || "Failed to create user"}`);
        }
    } catch (err) {
        console.error("❌ Add User Error:", err);
        alert("Server connection failed. Please check if the backend is running.");
    }
}

/**
 * --- EXISTING: EDIT ACCESS & DELETE LOGIC ---
 */

function getRoleBadge(role) {
    switch(role.toLowerCase()) {
        case 'admin': return 'bg-danger-subtle text-danger border border-danger-subtle';
        case 'faculty': return 'bg-success-subtle text-success border border-success-subtle';
        default: return 'bg-primary-subtle text-primary border border-primary-subtle';
    }
}

function prepareAndOpenModal(user) {
    selectedUserId = user.userId;
    document.getElementById("modalUserName").innerText = user.name;
    document.getElementById("editRole").value = user.role;
    
    const checkboxes = document.querySelectorAll('input[name="perm"]');
    checkboxes.forEach(cb => cb.checked = false);
    
    if (user.permissions && Array.isArray(user.permissions)) {
        user.permissions.forEach(permissionValue => {
            const cb = document.querySelector(`input[name="perm"][value="${permissionValue}"]`);
            if (cb) cb.checked = true;
        });
    }

    const modalElement = document.getElementById('accessModal');
    const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
    modal.show();
}

async function saveAccessChanges() {
    const newRole = document.getElementById("editRole").value;
    const selectedPerms = Array.from(document.querySelectorAll('input[name="perm"]:checked')).map(cb => cb.value);

    try {
        const res = await fetch(`${BASE_URL}/users/${selectedUserId}/update-access`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ role: newRole, permissions: selectedPerms }),
            credentials: "include"
        });

        if (res.ok) {
            alert("Access levels successfully updated!");
            location.reload();
        } else {
            const errorData = await res.json();
            alert(`Failed: ${errorData.message || 'Unknown error'}`);
        }
    } catch (err) {
        console.error("Save Error:", err);
    }
}

async function deleteUser(id, name) {
    if (!confirm(`Permanently remove ${name}?`)) return;

    try {
        const res = await fetch(`${BASE_URL}/users/${id}`, {
            method: "DELETE",
            credentials: "include"
        });

        if (res.ok) {
            alert("User removed.");
            fetchUsers();
        }
    } catch (err) {
        console.error("Delete Error:", err);
    }
}

// Academic Details Modal Functions
let selectedStudentId = null;

function openAcademicModal(user) {
    console.log("🔵 openAcademicModal() called for:", user);
    selectedStudentId = user.userId;
    document.getElementById("academicStudentName").innerText = user.name;
    
    // Fetch current student data
    fetchStudentAcademicData(user.userId);
    
    const modalElement = document.getElementById('academicModal');
    const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
    modal.show();
}

async function fetchStudentAcademicData(userId) {
    try {
        const res = await fetch(`${BASE_URL}/students/${userId}/academic`, {
            method: "GET",
            credentials: "include"
        });

        if (res.ok) {
            const data = await res.json();
            document.getElementById("editRollNo").value = data.rollNumber || "";
            document.getElementById("editProgram").value = data.program || "B.Tech";
            document.getElementById("editSemester").value = data.semester || 1;
            document.getElementById("editSgpa").value = data.sgpa || 0;
            document.getElementById("editCgpa").value = data.cgpa || 0;
            document.getElementById("editAttendance").value = data.attendance_percentage || 0;
            document.getElementById("editDepartment").value = data.department || "CSE";
        }
    } catch (err) {
        console.error("Fetch Academic Data Error:", err);
    }
}

async function saveAcademicDetails() {
    console.log("🔵 saveAcademicDetails() called");
    
    const data = {
        rollNumber: document.getElementById("editRollNo").value,
        program: document.getElementById("editProgram").value,
        semester: parseInt(document.getElementById("editSemester").value),
        sgpa: parseFloat(document.getElementById("editSgpa").value),
        cgpa: parseFloat(document.getElementById("editCgpa").value),
        attendance_percentage: parseFloat(document.getElementById("editAttendance").value),
        department: document.getElementById("editDepartment").value
    };

    console.log("📤 Updating academic data:", data);

    try {
        const res = await fetch(`${BASE_URL}/students/${selectedStudentId}/academic`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
            credentials: "include"
        });

        const result = await res.json();
        console.log("📥 Server response:", result);

        if (res.ok) {
            alert(result.message || "Academic details updated successfully!");
            bootstrap.Modal.getInstance(document.getElementById('academicModal')).hide();
            fetchUsers();
        } else {
            alert(`Error: ${result.message || result.error || "Failed to update"}`);
        }
    } catch (err) {
        console.error("❌ Update Academic Error:", err);
        alert("Server connection failed.");
    }
}
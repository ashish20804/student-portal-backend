const BASE_URL   = 'http://127.0.0.1:5000';
const TESTI_URL  = `${BASE_URL}/testimonials`;
const PROFILE_URL = `${BASE_URL}/student/profile`;
const IMG_URL    = `${BASE_URL}/student/display-photo`;

let allTestimonials = [];
let currentUserId  = null;
let currentFilter  = 'all';
let deleteTargetId = null;

const AVATAR_COLORS = ['#0d6efd','#6610f2','#198754','#dc3545','#fd7e14','#0dcaf0','#6f42c1'];
function colorFor(str) {
    let h = 0;
    for (let i = 0; i < str.length; i++) h = str.charCodeAt(i) + ((h << 5) - h);
    return AVATAR_COLORS[Math.abs(h) % AVATAR_COLORS.length];
}

window.onload = async () => {
    await loadCurrentUser();
    await fetchTestimonials();
    setupDeleteModal();
};

async function loadCurrentUser() {
    try {
        const res = await fetch(PROFILE_URL, { credentials: 'include' });
        if (!res.ok) { window.location.href = 'login.html'; return; }
        const data = await res.json();
        currentUserId = data.userId;

        document.getElementById('navUserName').textContent = data.name;
        const nav = document.getElementById('navAvatar');
        if (data.profile_image) {
            nav.innerHTML = `<img src="${IMG_URL}/${data.profile_image}">`;
            nav.style.background = 'transparent';
        } else {
            nav.textContent = data.name.charAt(0).toUpperCase();
            nav.style.background = colorFor(data.name);
        }
    } catch { window.location.href = 'login.html'; }
}

async function fetchTestimonials() {
    try {
        const res = await fetch(TESTI_URL, { credentials: 'include' });
        if (!res.ok) throw new Error();
        allTestimonials = await res.json();
        renderTestimonials(allTestimonials);
    } catch {
        document.getElementById('testimonialGrid').innerHTML =
            `<div class="col-12 text-center text-danger py-5"><i class="bi bi-exclamation-circle fs-3 d-block mb-2"></i>Unable to load testimonials.</div>`;
    }
}

function applyFilter(filter, btn) {
    currentFilter = filter;
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const filtered = filter === 'featured'
        ? allTestimonials.filter(t => t.is_featured)
        : allTestimonials;
    renderTestimonials(filtered);
}

function renderTestimonials(list) {
    const grid = document.getElementById('testimonialGrid');
    document.getElementById('countLabel').textContent = `${list.length} testimonial${list.length !== 1 ? 's' : ''}`;

    if (!list.length) {
        grid.innerHTML = `<div class="col-12 text-center text-muted py-5">
            <i class="bi bi-chat-dots fs-2 d-block mb-2 opacity-50"></i>
            No testimonials here yet. Be the first to share!
        </div>`;
        return;
    }

    grid.innerHTML = list.map(t => {
        const isOwn = t.userId === currentUserId;
        const avatarHtml = t.profile_image
            ? `<img src="${IMG_URL}/${t.profile_image}">`
            : `<span>${t.user_name.charAt(0).toUpperCase()}</span>`;
        const avatarBg = t.profile_image ? 'transparent' : colorFor(t.user_name);

        return `
        <div class="col-md-4 col-sm-6">
            <div class="card testimonial-card shadow-sm h-100 p-4 ${t.is_featured ? 'featured' : ''}">
                <div class="big-quote">"</div>
                ${t.is_featured ? '<span class="featured-badge"><i class="bi bi-star-fill me-1"></i>Featured</span>' : ''}

                ${isOwn ? `
                <div class="own-actions position-absolute" style="top:12px;left:14px;">
                    <button class="btn btn-sm btn-light border rounded-pill px-2 py-0 me-1" title="Edit" onclick="openEdit(${t.id}, \`${escapeJs(t.content)}\`)">
                        <i class="bi bi-pencil small"></i>
                    </button>
                    <button class="btn btn-sm btn-light border rounded-pill px-2 py-0 text-danger" title="Delete" onclick="openDelete(${t.id})">
                        <i class="bi bi-trash small"></i>
                    </button>
                </div>` : ''}

                <p class="content-text mt-2 flex-grow-1">"${escapeHtml(t.content)}"</p>

                <hr class="opacity-10 my-3">
                <div class="d-flex align-items-center justify-content-between">
                    <div class="d-flex align-items-center gap-2">
                        <div class="avatar-circle" style="background:${avatarBg};">${avatarHtml}</div>
                        <div>
                            <div class="fw-bold small">${escapeHtml(t.user_name)} ${isOwn ? '<span class="badge bg-primary-subtle text-primary ms-1" style="font-size:0.6rem;">You</span>' : ''}</div>
                            <div class="text-muted" style="font-size:0.72rem;">${t.department || 'Student'}${t.roll_no ? ' · ' + t.roll_no : ''}</div>
                        </div>
                    </div>
                    <span class="text-muted" style="font-size:0.7rem;">${t.date_added}</span>
                </div>
            </div>
        </div>`;
    }).join('');
}

// --- Modal helpers ---
function openEdit(id, content) {
    document.getElementById('editingId').value = id;
    document.getElementById('testiContent').value = content;
    document.getElementById('modalTitle').textContent = 'Edit Your Story';
    document.getElementById('submitBtn').innerHTML = '<i class="bi bi-check2 me-1"></i> Update';
    updateCharCount(document.getElementById('testiContent'));
    new bootstrap.Modal(document.getElementById('testiModal')).show();
}

function openDelete(id) {
    deleteTargetId = id;
    new bootstrap.Modal(document.getElementById('deleteModal')).show();
}

function setupDeleteModal() {
    document.getElementById('confirmDeleteBtn').onclick = async () => {
        if (!deleteTargetId) return;
        try {
            const res = await fetch(`${TESTI_URL}/${deleteTargetId}`, {
                method: 'DELETE', credentials: 'include'
            });
            if (res.ok) {
                bootstrap.Modal.getInstance(document.getElementById('deleteModal')).hide();
                await fetchTestimonials();
            } else {
                const d = await res.json();
                alert(d.message || 'Delete failed.');
            }
        } catch { alert('Server error.'); }
    };
}

// Reset modal on close
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('testiModal').addEventListener('hidden.bs.modal', () => {
        document.getElementById('editingId').value = '';
        document.getElementById('testiContent').value = '';
        document.getElementById('modalTitle').textContent = 'Share Your Story';
        document.getElementById('submitBtn').innerHTML = '<i class="bi bi-send me-1"></i> Post';
        updateCharCount(document.getElementById('testiContent'));
    });
});

async function submitTestimonial() {
    const content   = document.getElementById('testiContent').value.trim();
    const editingId = document.getElementById('editingId').value;
    const btn       = document.getElementById('submitBtn');

    if (!content) {
        document.getElementById('testiContent').classList.add('is-invalid');
        return;
    }
    document.getElementById('testiContent').classList.remove('is-invalid');

    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Saving...';

    try {
        const url    = editingId ? `${TESTI_URL}/${editingId}` : TESTI_URL;
        const method = editingId ? 'PUT' : 'POST';

        const res = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content }),
            credentials: 'include'
        });
        const data = await res.json();

        if (res.ok) {
            bootstrap.Modal.getInstance(document.getElementById('testiModal')).hide();
            await fetchTestimonials();
        } else {
            alert(data.message || 'Something went wrong.');
        }
    } catch { alert('Server connection failed.'); }
    finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-send me-1"></i> Post';
    }
}

function updateCharCount(el) {
    const len = el.value.length;
    const counter = document.getElementById('charCount');
    counter.textContent = `${len} / 1000`;
    counter.className = len > 900 ? 'text-danger' : len > 700 ? 'text-warning' : 'text-muted';
}

function escapeHtml(str) {
    return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function escapeJs(str) {
    return String(str).replace(/\\/g,'\\\\').replace(/`/g,'\\`').replace(/\$/g,'\\$');
}

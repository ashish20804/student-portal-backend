const ANNOUNCE_URL = `${CONFIG.API_BASE_URL}/announcements`;

const ROLE_COLORS = {
    admin:   { bg: '#dc3545', label: 'Admin' },
    faculty: { bg: '#0d6efd', label: 'Faculty' },
    student: { bg: '#198754', label: 'Student' }
};

async function loadAnnouncements() {
    const container = document.getElementById('announcementList');
    if (!container) return;

    try {
        const res = await fetch(ANNOUNCE_URL, { credentials: 'include' });
        if (!res.ok) throw new Error('Failed to load');
        const data = await res.json();

        if (!data.length) {
            container.innerHTML = '<p class="text-muted small">No announcements yet.</p>';
            return;
        }

        container.innerHTML = data.map(a => {
            const rc = ROLE_COLORS[a.role] || { bg: '#6c757d', label: a.role };
            return `
            <div class="card border-0 shadow-sm mb-3 p-3">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="d-flex align-items-center gap-2 mb-2">
                        <div class="rounded-circle text-white d-flex align-items-center justify-content-center fw-bold"
                             style="width:36px;height:36px;background:${rc.bg};font-size:14px;flex-shrink:0;">
                            ${a.posted_by.charAt(0).toUpperCase()}
                        </div>
                        <div>
                            <div class="fw-bold small">${a.posted_by}
                                <span class="badge ms-1 rounded-pill" style="background:${rc.bg};font-size:10px;">${rc.label}</span>
                            </div>
                            <div class="text-muted" style="font-size:11px;">${a.created_at}</div>
                        </div>
                    </div>
                </div>
                <p class="mb-0 small" style="white-space:pre-wrap;">${escapeHtml(a.content)}</p>
            </div>`;
        }).join('');
    } catch {
        container.innerHTML = '<p class="text-muted small">Could not load announcements.</p>';
    }
}

function escapeHtml(str) {
    return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function showAnnouncementModal() {
    new bootstrap.Modal(document.getElementById('announceModal')).show();
}

async function sendAnnouncement() {
    const textarea = document.getElementById('announceText');
    const content  = (textarea.value || '').trim();
    if (!content) { alert('Please enter announcement text.'); return; }

    try {
        const res = await fetch(ANNOUNCE_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ content })
        });
        const data = await res.json();
        if (res.ok) {
            textarea.value = '';
            bootstrap.Modal.getInstance(document.getElementById('announceModal')).hide();
            await loadAnnouncements();
        } else {
            alert(data.message || 'Failed to post announcement.');
        }
    } catch {
        alert('Connection error. Please try again.');
    }
}

// notif.js — shared notification bell logic for student / faculty / admin dashboards
// Include AFTER setting ROOT_URL in the parent script.

function _notifReadKey(myUserId, senderId) {
    return `notif_read_${myUserId}_${senderId}`;
}

let _myUserId = null;   // set after profile load

async function initNotifications(myUserId) {
    _myUserId = myUserId;
    await pollNotifications();
    setInterval(pollNotifications, 20000);
    document.addEventListener('click', e => {
        if (!document.getElementById('notifBellWrap')?.contains(e.target))
            document.getElementById('notifDropdown')?.classList.remove('show');
    });
}

function toggleNotifDropdown() {
    document.getElementById('notifDropdown').classList.toggle('show');
}

function markNotifRead(senderId, ts) {
    if (!_myUserId) return;
    localStorage.setItem(_notifReadKey(_myUserId, senderId), ts);
    // Re-render immediately without waiting for next poll
    pollNotifications();
}

async function pollNotifications() {
    try {
        const res = await fetch(`${ROOT_URL}/message/unread-count`, { credentials: 'include' });
        if (!res.ok) return;
        const data = await res.json();

        // Filter out senders the user already clicked/read
        const unread = data.senders.filter(s => {
            if (!_myUserId) return true;
            const readTs = localStorage.getItem(_notifReadKey(_myUserId, s.userId));
            if (!readTs) return true;
            return new Date(s.ts) > new Date(readTs);
        });

        const badge = document.getElementById('notifBadge');
        const list  = document.getElementById('notifList');
        const bell  = document.getElementById('notifBellIcon');
        if (!badge || !list || !bell) return;

        if (unread.length > 0) {
            badge.textContent = unread.length > 9 ? '9+' : unread.length;
            badge.classList.remove('d-none');
            bell.className = 'bi bi-bell-fill fs-5 text-danger';

            list.innerHTML = unread.map(s => {
                const color = _strToColor(s.name);
                return `<a href="messages.html?userId=${s.userId}&name=${encodeURIComponent(s.name)}"
                           class="notif-item"
                           onclick="markNotifRead(${s.userId}, '${s.ts}'); event.stopPropagation();">
                    <div class="notif-avatar" style="background:${color}">${s.name.charAt(0).toUpperCase()}</div>
                    <div class="flex-grow-1 overflow-hidden">
                        <div class="fw-bold small text-truncate">${s.name}</div>
                        <div class="text-muted" style="font-size:0.72rem;">${s.identifier} &middot; ${s.time}</div>
                    </div>
                    <i class="bi bi-chat-dots text-primary flex-shrink-0"></i>
                </a>`;
            }).join('');
        } else {
            badge.classList.add('d-none');
            bell.className = 'bi bi-bell fs-5 text-muted';
            list.innerHTML = '<div class="notif-empty"><i class="bi bi-check2-all d-block mb-1 fs-5 text-success"></i>All caught up!</div>';
        }
    } catch { /* silent */ }
}

function _strToColor(str) {
    let h = 0;
    for (let i = 0; i < str.length; i++) h = str.charCodeAt(i) + ((h << 5) - h);
    return `hsl(${Math.abs(h) % 360},65%,45%)`;
}

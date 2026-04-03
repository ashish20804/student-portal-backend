const MSG_URL     = `${CONFIG.API_BASE_URL}/message`;
const PROFILE_URL = `${CONFIG.API_BASE_URL}/student/profile`; 

let activeChatId = null;
let pollInterval = null;

window.onload = async () => {
    const ok = await loadLoggedInUser();
    if (!ok) return; // redirected to login
    await loadRecentChats();
    autoOpenFromURL();
    setupSearch();
};

// --- Auto-open conversation if redirected from student_list ---
async function autoOpenFromURL() {
    const params = new URLSearchParams(window.location.search);
    const userId = params.get('userId');
    const name   = params.get('name');
    if (!userId || !name) return;

    const decodedName = decodeURIComponent(name);
    const uid = parseInt(userId);

    try {
        const res = await fetch(`${MSG_URL}/search?q=${encodeURIComponent(decodedName)}`, { credentials: 'include' });
        const users = await res.json();
        const match = users.find(u => u.userId == uid);
        const profileImage = match ? (match.profile_image || '') : '';

        // If user not in sidebar yet, inject them
        if (!document.querySelector(`.chat-item[data-uid="${uid}"]`)) {
            const container = document.getElementById('chatList');
            const avatarContent = profileImage
                ? `<img src="${profileImage}" class="w-100 h-100 object-fit-cover">`
                : decodedName.charAt(0).toUpperCase();
            const bgColor = profileImage ? 'transparent' : stringToColor(decodedName);
            const div = document.createElement('div');
            div.className = 'chat-item d-flex align-items-center p-3 border-bottom cursor-pointer';
            div.dataset.uid = uid;
            div.onclick = () => openConversation(uid, decodedName, profileImage);
            div.innerHTML = `
                <div class="avatar me-3 overflow-hidden d-flex align-items-center justify-content-center fw-bold text-white shadow-sm"
                     style="background-color:${bgColor};width:45px;height:45px;border-radius:50%;flex-shrink:0;">${avatarContent}</div>
                <div class="flex-grow-1">
                    <h6 class="mb-0 fw-bold text-truncate">${decodedName}</h6>
                    <p class="mb-0 text-muted extra-small">student</p>
                </div>`;
            container.prepend(div);
        }

        openConversation(uid, decodedName, profileImage);
    } catch {
        openConversation(uid, decodedName, '');
    }
}

// --- 1. Load Logged-In User Profile (Handles Student & Faculty) ---
async function loadLoggedInUser() {
    try {
        const res = await fetch(PROFILE_URL, { credentials: "include" });

        if (res.status === 401) {
            window.location.href = 'login.html';
            return false;
        }

        const data = await res.json();

        if (res.ok) {
            document.getElementById("userNameDisplay").innerText = data.name;

            const subText = (data.role === 'faculty') ? "Faculty" : (data.rollNumber || "");
            document.getElementById("userRollDisplay").innerText = subText;

            const avatarDiv = document.getElementById("loggedInUserAvatar");
            if (data.profile_image) {
                avatarDiv.innerHTML = `<img src="${data.profile_image}" class="w-100 h-100 object-fit-cover">`;
                avatarDiv.style.backgroundColor = "transparent";
            } else {
                avatarDiv.innerText = data.name.charAt(0).toUpperCase();
                avatarDiv.style.backgroundColor = stringToColor(data.name);
            }

            const backBtn = document.getElementById("backBtn");
            backBtn.href = (data.role === 'faculty') ? "faculty_dashboard.html" : "dashboard.html";
            return true;
        }
        window.location.href = 'login.html';
        return false;
    } catch (err) {
        console.error("Profile load failed:", err);
        window.location.href = 'login.html';
        return false;
    }
}

// --- 2. Encryption/Decryption Helpers ---
function encryptMessage(text) {
    // Encodes string to Base64 to "hide" content in the database
    return btoa(unescape(encodeURIComponent(text)));
}

function decryptMessage(encodedText) {
    try {
        // Decodes Base64 back to readable text
        return decodeURIComponent(escape(atob(encodedText)));
    } catch (e) {
        return encodedText; // Return original if not encoded
    }
}

// --- 3. Sidebar & Search ---
function setupSearch() {
    const searchInput = document.getElementById("userSearchInput");
    searchInput.addEventListener('input', async (e) => {
        const query = e.target.value.trim();
        if (query.length < 2) { loadRecentChats(); return; }
        try {
            const res = await fetch(`${MSG_URL}/search?q=${query}`, { credentials: "include" });
            const users = await res.json();
            renderChatList(users);
        } catch (err) { console.error(err); }
    });
}

async function loadRecentChats() {
    try {
        const res = await fetch(`${MSG_URL}/chats`, { credentials: "include" });
        if (res.status === 401) { window.location.href = 'login.html'; return; }
        const chats = await res.json();
        renderChatList(chats);
    } catch (err) { console.error(err); }
}

function renderChatList(users) {
    const container = document.getElementById("chatList");
    if (users.length === 0) {
        container.innerHTML = '<div class="text-center text-muted p-3">No users found</div>';
        return;
    }

    container.innerHTML = users.map(user => {
        const avatarContent = user.profile_image 
            ? `<img src="${user.profile_image}" class="w-100 h-100 object-fit-cover">`
            : user.username.charAt(0).toUpperCase();
        const bgColor = user.profile_image ? 'transparent' : stringToColor(user.username);

        return `
            <div class="chat-item d-flex align-items-center p-3 border-bottom cursor-pointer" 
                 data-uid="${user.userId}"
                 onclick="openConversation(${user.userId}, '${user.username}', '${user.profile_image || ''}')">
                <div class="avatar me-3 overflow-hidden d-flex align-items-center justify-content-center fw-bold text-white shadow-sm" 
                     style="background-color: ${bgColor}; width: 45px; height: 45px; border-radius: 50%; flex-shrink: 0;">
                    ${avatarContent}
                </div>
                <div class="flex-grow-1">
                    <div class="d-flex justify-content-between align-items-center">
                        <h6 class="mb-0 fw-bold text-truncate">${user.username}</h6>
                        <span class="extra-small text-muted" style="font-size: 0.65rem;">${user.rollNumber || ''}</span>
                    </div>
                    <p class="mb-0 text-muted extra-small">${user.role}</p>
                </div>
            </div>
        `;
    }).join('');
}

// --- 4. Chat Logic ---
async function openConversation(userId, username, profileImage) {
    activeChatId = userId;
    // Highlight active chat in sidebar
    document.querySelectorAll('.chat-item').forEach(el => el.classList.remove('active'));
    const activeItem = document.querySelector(`.chat-item[data-uid="${userId}"]`);
    if (activeItem) { activeItem.classList.add('active'); activeItem.scrollIntoView({ block: 'nearest' }); }
    document.getElementById("chatHeader").classList.remove("d-none");
    document.getElementById("activeChatName").innerText = username;
    
    const headerAvatar = document.getElementById("activeAvatar");
    headerAvatar.classList.add("overflow-hidden");
    if (profileImage && profileImage !== 'null' && profileImage !== '') {
        headerAvatar.innerHTML = `<img src="${profileImage}" class="w-100 h-100 object-fit-cover">`;
        headerAvatar.style.backgroundColor = "transparent";
    } else {
        headerAvatar.innerText = username.charAt(0).toUpperCase();
        headerAvatar.style.backgroundColor = stringToColor(username);
        headerAvatar.innerHTML = username.charAt(0).toUpperCase();
    }
    
    document.getElementById("msgInput").disabled = false;
    document.getElementById("sendBtn").disabled = false;
    
    fetchMessages(); 
    if (pollInterval) clearInterval(pollInterval);
    pollInterval = setInterval(fetchMessages, 3000);
}

async function fetchMessages() {
    if (!activeChatId) return;
    try {
        const res = await fetch(`${MSG_URL}/conversation/${activeChatId}`, { credentials: "include" });
        const messages = await res.json();
        const display = document.getElementById("messageDisplay");
        
        display.innerHTML = messages.map(m => {
            const isSent = m.senderId != activeChatId;
            const content = decryptMessage(m.content); // Decrypt for viewing
            return `
                <div class="msg-row ${isSent ? 'sent' : 'received'}">
                    <div class="bubble">${content}<span class="time">${m.timestamp}</span></div>
                </div>
            `;
        }).join('');
        display.scrollTop = display.scrollHeight;
    } catch (err) { console.error(err); }
}

document.getElementById("sendForm").onsubmit = async (e) => {
    e.preventDefault();
    const input = document.getElementById("msgInput");
    const content = input.value.trim();
    if (!content) return;

    const encryptedContent = encryptMessage(content); // Encrypt for database

    try {
        const res = await fetch(`${MSG_URL}/send`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ receiverId: activeChatId, content: encryptedContent }),
            credentials: "include"
        });
        if (res.ok) { input.value = ""; fetchMessages(); }
    } catch (err) { console.error(err); }
};

function stringToColor(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) hash = str.charCodeAt(i) + ((hash << 5) - hash);
    return `hsl(${Math.abs(hash) % 360}, 65%, 45%)`;
}

// --- 5. Logout ---
async function logout() {
    if (confirm("Are you sure you want to logout?")) {
        await fetch(`${CONFIG.API_BASE_URL}/logout`, { method: 'POST', credentials: 'include' });
        window.location.href = "login.html";
    }
}
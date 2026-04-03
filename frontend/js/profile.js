const BASE_URL          = `${CONFIG.API_BASE_URL}/student`;
const IMAGE_DISPLAY_URL = `${CONFIG.API_BASE_URL}/student/display-photo`;

window.onload = loadProfile;

document.getElementById("imageUpload").addEventListener("change", function () {
    const file = this.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = e => document.getElementById("profilePreview").src = e.target.result;
        reader.readAsDataURL(file);
    }
});

async function loadProfile() {
    try {
        const res = await fetch(`${BASE_URL}/profile`, { method: "GET", credentials: "include" });
        if (!res.ok) throw new Error("Failed to fetch profile");
        const data = await res.json();

        const previewImg = document.getElementById("profilePreview");
        if (data.profile_image) {
            previewImg.src = `${IMAGE_DISPLAY_URL}/${data.profile_image}?t=${Date.now()}`;
        } else {
            previewImg.src = `https://ui-avatars.com/api/?name=${data.name}&background=random&size=128`;
        }

        document.getElementById("rollNumber").value  = data.rollNumber  || "N/A";
        document.getElementById("email").value       = data.email       || "";
        document.getElementById("fullName").value    = data.name        || "";
        document.getElementById("phoneNumber").value = data.phoneNumber || "";
        document.getElementById("address").value     = data.address     || "";
        document.getElementById("program").value     = data.program     || "";
        document.getElementById("semester").value    = data.semester    || "";
        document.getElementById("department").value  = data.department  || "";
    } catch (err) {
        console.error("Load Error:", err);
        alert("Error loading profile data");
    }
}

document.getElementById("profileForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const saveBtn = document.getElementById("saveBtn");
    saveBtn.disabled  = true;
    saveBtn.innerText = "Saving...";

    const formData = new FormData();
    formData.append("name",        document.getElementById("fullName").value);
    formData.append("phoneNumber", document.getElementById("phoneNumber").value);
    formData.append("address",     document.getElementById("address").value);
    formData.append("program",     document.getElementById("program").value);
    formData.append("semester",    document.getElementById("semester").value);
    formData.append("department",  document.getElementById("department").value);

    const imageFile = document.getElementById("imageUpload").files[0];
    if (imageFile) formData.append("profile_image", imageFile);

    try {
        const res    = await fetch(`${BASE_URL}/profile`, { method: "PUT", credentials: "include", body: formData });
        const result = await res.json();
        if (res.ok) { alert("Profile updated successfully!"); window.location.href = "dashboard.html"; }
        else        { alert(result.error || "Failed to update profile."); }
    } catch (err) {
        console.error("Update error:", err);
        alert("An error occurred while saving.");
    } finally {
        saveBtn.disabled  = false;
        saveBtn.innerText = "Save Changes";
    }
});

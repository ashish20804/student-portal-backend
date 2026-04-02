const BASE_URL = "http://127.0.0.1:5000/student";
// UPDATED: Points to your Flask display route instead of a static folder
const IMAGE_DISPLAY_URL = "http://127.0.0.1:5000/student/display-photo";

window.onload = loadProfile;

// 1. Handle Image Preview when a file is selected (Immediate visual feedback)
document.getElementById("imageUpload").addEventListener("change", function() {
    const file = this.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById("profilePreview").src = e.target.result;
        };
        reader.readAsDataURL(file);
    }
});

// 2. Load Profile Data
async function loadProfile() {
    try {
        const res = await fetch(`${BASE_URL}/profile`, {
            method: "GET",
            credentials: "include"
        });

        if (!res.ok) throw new Error("Failed to fetch profile");

        const data = await res.json();

        // Handle Profile Image Display
        const previewImg = document.getElementById("profilePreview");
        if (data.profile_image) {
            // Added a timestamp (?t=...) to bypass browser cache so new uploads show up immediately
            const timestamp = new Date().getTime();
            previewImg.src = `${IMAGE_DISPLAY_URL}/${data.profile_image}?t=${timestamp}`;
        } else {
            // Fallback to letter avatar if no image exists in DB
            previewImg.src = `https://ui-avatars.com/api/?name=${data.name}&background=random&size=128`;
        }

        // Fill Read-Only fields
        document.getElementById("rollNumber").value = data.rollNumber || "N/A";
        document.getElementById("email").value = data.email || "";

        // Fill Editable fields
        document.getElementById("fullName").value = data.name || "";
        document.getElementById("phoneNumber").value = data.phoneNumber || "";
        document.getElementById("address").value = data.address || "";
        document.getElementById("program").value = data.program || "";
        document.getElementById("semester").value = data.semester || "";
        document.getElementById("department").value = data.department || "";

    } catch (err) {
        console.error("Load Error:", err);
        alert("Error loading profile data");
    }
}

// 3. Update Profile (Using FormData for Image Support)
document.getElementById("profileForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    
    const saveBtn = document.getElementById("saveBtn");
    saveBtn.disabled = true;
    saveBtn.innerText = "Saving...";

    // Use FormData to handle both text and file uploads
    const formData = new FormData();
    formData.append("name", document.getElementById("fullName").value);
    formData.append("phoneNumber", document.getElementById("phoneNumber").value);
    formData.append("address", document.getElementById("address").value);
    formData.append("program", document.getElementById("program").value);
    formData.append("semester", document.getElementById("semester").value);
    formData.append("department", document.getElementById("department").value);

    // Check if a new image file was selected via the input
    const imageFile = document.getElementById("imageUpload").files[0];
    if (imageFile) {
        formData.append("profile_image", imageFile);
    }

    try {
        const res = await fetch(`${BASE_URL}/profile`, {
            method: "PUT",
            credentials: "include",
            // NOTE: Content-Type header is NOT set here. Browser handles it for FormData.
            body: formData
        });

        const result = await res.json();

        if (res.ok) {
            alert("Profile updated successfully!");
            window.location.href = "dashboard.html";
        } else {
            alert(result.error || "Failed to update profile.");
        }
    } catch (err) {
        console.error("Update error:", err);
        alert("An error occurred while saving.");
    } finally {
        saveBtn.disabled = false;
        saveBtn.innerText = "Save Changes";
    }
});
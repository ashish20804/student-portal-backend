const BASE_URL = 'http://127.0.0.1:5000/student';
const IMAGE_DISPLAY_URL = 'http://127.0.0.1:5000/student/display-photo';

window.onload = loadFacultyProfile;

document.getElementById('imageUpload').addEventListener('change', function () {
    const file = this.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = e => document.getElementById('profilePreview').src = e.target.result;
        reader.readAsDataURL(file);
    }
});

async function loadFacultyProfile() {
    try {
        const res = await fetch(`${BASE_URL}/profile`, { credentials: 'include' });
        if (res.status === 401 || res.status === 403) {
            window.location.href = 'login.html';
            return;
        }
        if (!res.ok) throw new Error('Failed to load profile');

        const data = await res.json();

        const preview = document.getElementById('profilePreview');
        if (data.profile_image) {
            preview.src = `${IMAGE_DISPLAY_URL}/${data.profile_image}?t=${Date.now()}`;
        } else {
            preview.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(data.name || 'Faculty')}&background=random&size=128`;
        }

        document.getElementById('email').value       = data.email        || '';
        document.getElementById('fullName').value    = data.name         || '';
        document.getElementById('phoneNumber').value = data.phoneNumber  || '';
        document.getElementById('address').value     = data.address      || '';
        document.getElementById('designation').value = data.rollNumber   || '';  // backend sends designation as rollNumber
        document.getElementById('department').value  = data.department   || '';

    } catch (err) {
        console.error('Load error:', err);
        alert('Error loading profile data.');
    }
}

document.getElementById('profileForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const saveBtn = document.getElementById('saveBtn');
    saveBtn.disabled = true;
    saveBtn.innerText = 'Saving...';

    const formData = new FormData();
    formData.append('name',        document.getElementById('fullName').value);
    formData.append('phoneNumber', document.getElementById('phoneNumber').value);
    formData.append('address',     document.getElementById('address').value);
    formData.append('designation', document.getElementById('designation').value);
    formData.append('department',  document.getElementById('department').value);

    const imageFile = document.getElementById('imageUpload').files[0];
    if (imageFile) formData.append('profile_image', imageFile);

    try {
        const res = await fetch(`${BASE_URL}/profile`, {
            method: 'PUT',
            credentials: 'include',
            body: formData
        });
        const result = await res.json();
        if (res.ok) {
            alert('Profile updated successfully!');
            window.location.href = 'faculty_dashboard.html';
        } else {
            alert(result.error || 'Failed to update profile.');
        }
    } catch (err) {
        console.error('Save error:', err);
        alert('An error occurred while saving.');
    } finally {
        saveBtn.disabled = false;
        saveBtn.innerText = 'Save Changes';
    }
});

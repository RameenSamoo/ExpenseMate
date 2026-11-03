/* ==========================================================================
   EXPENSEMATE - Settings Controller
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  loadUserSettings();
});

async function loadUserSettings() {
  try {
    const res = await apiFetch('/api/settings');
    if (res.success) {
      document.getElementById('set-fullname').value = res.user.full_name;
      document.getElementById('set-email').value = res.user.email;
      if (res.user.currency) {
        document.getElementById('set-currency').value = res.user.currency;
      }
    }
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

async function saveUserProfile(e) {
  e.preventDefault();
  const fullName = document.getElementById('set-fullname').value;
  const email = document.getElementById('set-email').value;
  const currency = document.getElementById('set-currency').value;
  const currPass = document.getElementById('set-curr-pass').value;
  const newPass = document.getElementById('set-new-pass').value;

  const payload = {
    full_name: fullName,
    email: email,
    currency: currency
  };

  if (newPass) {
    payload.current_password = currPass;
    payload.new_password = newPass;
  }

  try {
    const res = await apiFetch('/api/settings', {
      method: 'PUT',
      body: JSON.stringify(payload)
    });

    showToast('Profile and settings updated successfully!', 'success');
    document.getElementById('set-curr-pass').value = '';
    document.getElementById('set-new-pass').value = '';
    
    document.getElementById('user-name-display').textContent = fullName;
    document.getElementById('user-avatar-initial').textContent = fullName[0].toUpperCase();
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

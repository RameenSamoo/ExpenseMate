/* ==========================================================================
   EXPENSEMATE - Authentication Controller (Login & Registration)
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.getElementById('login-email').value;
      const password = document.getElementById('login-password').value;

      try {
        const response = await apiFetch('/api/auth/login', {
          method: 'POST',
          body: JSON.stringify({ email, password })
        });
        showToast('Login successful! Redirecting...', 'success');
        setTimeout(() => { window.location.href = '/dashboard'; }, 800);
      } catch (err) {
        showToast(err.message, 'danger');
      }
    });
  }

  const registerForm = document.getElementById('register-form');
  if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const fullName = document.getElementById('reg-fullname').value;
      const email = document.getElementById('reg-email').value;
      const password = document.getElementById('reg-password').value;
      const confirmPassword = document.getElementById('reg-confirm').value;

      if (password !== confirmPassword) {
        showToast('Passwords do not match.', 'danger');
        return;
      }

      try {
        const response = await apiFetch('/api/auth/register', {
          method: 'POST',
          body: JSON.stringify({
            full_name: fullName,
            email,
            password,
            confirm_password: confirmPassword
          })
        });
        showToast('Account created successfully!', 'success');
        setTimeout(() => { window.location.href = '/dashboard'; }, 800);
      } catch (err) {
        showToast(err.message, 'danger');
      }
    });
  }
});

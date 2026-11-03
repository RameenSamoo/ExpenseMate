/* ==========================================================================
   EXPENSEMATE - Global API Fetch Wrapper & UI Utility System
   ========================================================================== */

/**
 * Universal fetch wrapper for API communication.
 */
async function apiFetch(url, options = {}) {
  const defaultHeaders = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  };

  const config = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers
    }
  };

  try {
    const response = await fetch(url, config);
    
    // Check unauthenticated redirect
    if (response.status === 401 && !url.includes('/api/auth/login')) {
      showToast('Session expired. Please log in again.', 'warning');
      setTimeout(() => { window.location.href = '/login'; }, 1200);
      throw new Error('Unauthorized');
    }

    const data = await response.json();

    if (!response.ok) {
      const errorMsg = data.message || 'An error occurred while processing your request.';
      throw new Error(errorMsg);
    }

    return data;
  } catch (error) {
    console.error(`API Error [${url}]:`, error);
    throw error;
  }
}

/**
 * Global Toast Notification Manager
 */
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  
  let icon = 'ℹ';
  if (type === 'success') icon = '✓';
  if (type === 'warning') icon = '⚠';
  if (type === 'danger') icon = '✕';

  toast.innerHTML = `
    <span style="font-weight:700; font-size:1.1rem;">${icon}</span>
    <span>${message}</span>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

/**
 * Formats currency values as Rs. 25,000 (PKR standard)
 */
function formatCurrency(amount, currencySymbol = 'Rs.') {
  const val = parseFloat(amount || 0);
  const formatted = val.toLocaleString('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2
  });
  return `${currencySymbol} ${formatted}`;
}

/**
 * Global Confirmation Modal Dialog
 */
let pendingConfirmAction = null;

function confirmAction(title, message, onConfirmCallback) {
  const modal = document.getElementById('confirm-modal');
  const titleEl = document.getElementById('confirm-modal-title');
  const msgEl = document.getElementById('confirm-modal-message');
  const actionBtn = document.getElementById('confirm-modal-action-btn');

  if (!modal) {
    if (confirm(message)) onConfirmCallback();
    return;
  }

  titleEl.textContent = title || 'Confirm Action';
  msgEl.textContent = message;
  pendingConfirmAction = onConfirmCallback;

  actionBtn.onclick = () => {
    if (pendingConfirmAction) pendingConfirmAction();
    closeConfirmModal();
  };

  modal.classList.add('active');
}

function closeConfirmModal() {
  const modal = document.getElementById('confirm-modal');
  if (modal) modal.classList.remove('active');
  pendingConfirmAction = null;
}

// Sidebar Drawer Toggle for Responsive Screens
document.addEventListener('DOMContentLoaded', () => {
  const toggleBtn = document.getElementById('menu-toggle');
  const sidebar = document.getElementById('app-sidebar');

  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', () => {
      sidebar.classList.toggle('open');
    });
  }
});

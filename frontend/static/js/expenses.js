/* ==========================================================================
   EXPENSEMATE - Expenses Page Controller
   ========================================================================== */

let expenseTrendChart = null;
let expenseCategoryChart = null;

document.addEventListener('DOMContentLoaded', () => {
  // Set year filter to current year
  const yearFilter = document.getElementById('exp-year-filter');
  if (yearFilter) yearFilter.value = String(new Date().getFullYear());

  loadCategories();
  loadExpenseData();

  const expDate = document.getElementById('exp-date');
  if (expDate) expDate.value = new Date().toISOString().split('T')[0];
});

async function loadCategories() {
  try {
    const res = await apiFetch('/api/categories?type=expense');
    const select = document.getElementById('exp-category');
    const filterSelect = document.getElementById('exp-category-filter');

    select.innerHTML = '';
    filterSelect.innerHTML = '<option value="">All Categories</option>';

    res.data.forEach(c => {
      select.innerHTML += `<option value="${c.id}">${c.name}</option>`;
      filterSelect.innerHTML += `<option value="${c.id}">${c.name}</option>`;
    });
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

async function loadExpenseData() {
  const search = document.getElementById('exp-search').value;
  const categoryId = document.getElementById('exp-category-filter').value;
  const year = document.getElementById('exp-year-filter').value;

  try {
    const res = await apiFetch(`/api/expenses?year=${year}&category_id=${categoryId}&search=${encodeURIComponent(search)}`);
    if (res.success) {
      renderExpenseMetrics(res.analytics);
      renderExpenseTrendChart(res.analytics);
      renderExpenseCategoryChart(res.analytics.category_breakdown);
      renderExpenseHistory(res.data.items);
    }
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

function renderExpenseMetrics(analytics) {
  document.getElementById('exp-metric-total').textContent = formatCurrency(analytics.total_expense);
  document.getElementById('exp-metric-daily').textContent = formatCurrency(analytics.daily_avg);
  document.getElementById('exp-metric-top').textContent = analytics.top_category;
}

function renderExpenseTrendChart(analytics) {
  const ctx = document.getElementById('chart-expense-trend').getContext('2d');
  if (expenseTrendChart) expenseTrendChart.destroy();

  expenseTrendChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: analytics.months,
      datasets: [{
        label: 'Expenses (Rs.)',
        data: analytics.trend,
        borderColor: '#E53E3E',
        backgroundColor: 'rgba(229, 62, 62, 0.1)',
        fill: true,
        tension: 0.3,
        borderWidth: 2.5
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { beginAtZero: true, grid: { color: '#F0EAE1' } },
        x: { grid: { display: false } }
      }
    }
  });
}

function renderExpenseCategoryChart(breakdown) {
  const ctx = document.getElementById('chart-expense-category').getContext('2d');
  if (expenseCategoryChart) expenseCategoryChart.destroy();

  if (!breakdown || breakdown.length === 0) {
    breakdown = [{ category_name: 'None', total: 1 }];
  }

  const labels = breakdown.map(b => b.category_name);
  const data = breakdown.map(b => b.total);
  const palette = ['#E8B4A8', '#8FA3C0', '#F6AD55', '#68D391', '#63B3ED', '#B794F4', '#FC8181'];

  expenseCategoryChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: palette.slice(0, labels.length)
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'right', labels: { boxWidth: 12 } }
      }
    }
  });
}

function renderExpenseHistory(items) {
  const tbody = document.getElementById('table-expense-body');
  tbody.innerHTML = '';

  if (!items || items.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5" class="empty-state">No expense records found.</td></tr>';
    return;
  }

  items.forEach(item => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${item.transaction_date}</td>
      <td style="font-weight: 600;">${item.category_name}</td>
      <td>${item.description || '-'}</td>
      <td style="text-align: right;" class="amount-expense">- ${formatCurrency(item.amount)}</td>
      <td style="text-align: right;">
        <div class="action-buttons" style="justify-content: flex-end;">
          <button class="btn-icon" onclick="openEditExpenseModal(${item.id})">Edit</button>
          <button class="btn-icon delete" onclick="deleteExpenseRecord(${item.id})">Delete</button>
        </div>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function openExpenseModal() {
  document.getElementById('exp-id').value = '';
  document.getElementById('expense-modal-title').textContent = 'Add Expense Record';
  document.getElementById('expense-form').reset();
  document.getElementById('exp-date').value = new Date().toISOString().split('T')[0];
  document.getElementById('expense-modal').classList.add('active');
}

function closeExpenseModal() {
  document.getElementById('expense-modal').classList.remove('active');
}

async function openEditExpenseModal(id) {
  try {
    const res = await apiFetch(`/api/transactions/${id}`);
    const item = res.data;

    document.getElementById('exp-id').value = item.id;
    document.getElementById('exp-category').value = item.category_id;
    document.getElementById('exp-amount').value = item.amount;
    document.getElementById('exp-date').value = item.transaction_date;
    document.getElementById('exp-desc').value = item.description || '';
    
    document.getElementById('expense-modal-title').textContent = 'Edit Expense Record';
    document.getElementById('expense-modal').classList.add('active');
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

async function saveExpenseRecord(e) {
  e.preventDefault();
  const id = document.getElementById('exp-id').value;
  const categoryId = document.getElementById('exp-category').value;
  const amount = document.getElementById('exp-amount').value;
  const date = document.getElementById('exp-date').value;
  const desc = document.getElementById('exp-desc').value;

  const url = id ? `/api/expenses/${id}` : '/api/expenses';
  const method = id ? 'PUT' : 'POST';

  try {
    await apiFetch(url, {
      method: method,
      body: JSON.stringify({
        category_id: categoryId,
        amount: amount,
        transaction_date: date,
        description: desc
      })
    });

    showToast(`Expense ${id ? 'updated' : 'added'} successfully!`, 'success');
    closeExpenseModal();
    loadExpenseData();
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

function deleteExpenseRecord(id) {
  confirmAction('Delete Expense', 'Are you sure you want to delete this expense record?', async () => {
    try {
      await apiFetch(`/api/expenses/${id}`, { method: 'DELETE' });
      showToast('Expense record deleted.', 'success');
      loadExpenseData();
    } catch (err) {
      showToast(err.message, 'danger');
    }
  });
}

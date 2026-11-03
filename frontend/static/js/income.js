/* ==========================================================================
   EXPENSEMATE - Income Page Controller
   ========================================================================== */

let incomeTrendChart = null;

document.addEventListener('DOMContentLoaded', () => {
  // Set year filter to current year
  const yearFilter = document.getElementById('inc-year-filter');
  if (yearFilter) yearFilter.value = String(new Date().getFullYear());

  loadCategories();
  loadIncomeData();

  const incDate = document.getElementById('inc-date');
  if (incDate) incDate.value = new Date().toISOString().split('T')[0];
});

async function loadCategories() {
  try {
    const res = await apiFetch('/api/categories?type=income');
    const select = document.getElementById('inc-category');
    const filterSelect = document.getElementById('inc-category-filter');

    select.innerHTML = '';
    filterSelect.innerHTML = '<option value="">All Income Sources</option>';

    res.data.forEach(c => {
      select.innerHTML += `<option value="${c.id}">${c.name}</option>`;
      filterSelect.innerHTML += `<option value="${c.id}">${c.name}</option>`;
    });
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

async function loadIncomeData() {
  const search = document.getElementById('inc-search').value;
  const categoryId = document.getElementById('inc-category-filter').value;
  const year = document.getElementById('inc-year-filter').value;

  try {
    const res = await apiFetch(`/api/income?year=${year}&category_id=${categoryId}&search=${encodeURIComponent(search)}`);
    if (res.success) {
      renderIncomeMetrics(res.analytics);
      renderIncomeTrendChart(res.analytics);
      renderIncomeHistory(res.data.items);
    }
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

function renderIncomeMetrics(analytics) {
  document.getElementById('inc-metric-total').textContent = formatCurrency(analytics.total_income);
  document.getElementById('inc-metric-avg').textContent = formatCurrency(analytics.avg_monthly_income);
  document.getElementById('inc-metric-top').textContent = analytics.top_source;
}

function renderIncomeTrendChart(analytics) {
  const ctx = document.getElementById('chart-income-trend').getContext('2d');
  if (incomeTrendChart) incomeTrendChart.destroy();

  incomeTrendChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: analytics.months,
      datasets: [{
        label: 'Income (Rs.)',
        data: analytics.trend,
        backgroundColor: '#48BB78',
        borderRadius: 6
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

function renderIncomeHistory(items) {
  const tbody = document.getElementById('table-income-body');
  tbody.innerHTML = '';

  if (!items || items.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5" class="empty-state">No income records found.</td></tr>';
    return;
  }

  items.forEach(item => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${item.transaction_date}</td>
      <td style="font-weight: 600;">${item.category_name}</td>
      <td>${item.description || '-'}</td>
      <td style="text-align: right;" class="amount-income">+ ${formatCurrency(item.amount)}</td>
      <td style="text-align: right;">
        <div class="action-buttons" style="justify-content: flex-end;">
          <button class="btn-icon" onclick="openEditIncomeModal(${item.id})">Edit</button>
          <button class="btn-icon delete" onclick="deleteIncomeRecord(${item.id})">Delete</button>
        </div>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function openIncomeModal() {
  document.getElementById('inc-id').value = '';
  document.getElementById('income-modal-title').textContent = 'Add Income Record';
  document.getElementById('income-form').reset();
  document.getElementById('inc-date').value = new Date().toISOString().split('T')[0];
  document.getElementById('income-modal').classList.add('active');
}

function closeIncomeModal() {
  document.getElementById('income-modal').classList.remove('active');
}

async function openEditIncomeModal(id) {
  try {
    const res = await apiFetch(`/api/transactions/${id}`);
    const item = res.data;

    document.getElementById('inc-id').value = item.id;
    document.getElementById('inc-category').value = item.category_id;
    document.getElementById('inc-amount').value = item.amount;
    document.getElementById('inc-date').value = item.transaction_date;
    document.getElementById('inc-desc').value = item.description || '';
    
    document.getElementById('income-modal-title').textContent = 'Edit Income Record';
    document.getElementById('income-modal').classList.add('active');
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

async function saveIncomeRecord(e) {
  e.preventDefault();
  const id = document.getElementById('inc-id').value;
  const categoryId = document.getElementById('inc-category').value;
  const amount = document.getElementById('inc-amount').value;
  const date = document.getElementById('inc-date').value;
  const desc = document.getElementById('inc-desc').value;

  const url = id ? `/api/income/${id}` : '/api/income';
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

    showToast(`Income ${id ? 'updated' : 'added'} successfully!`, 'success');
    closeIncomeModal();
    loadIncomeData();
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

function deleteIncomeRecord(id) {
  confirmAction('Delete Income', 'Are you sure you want to delete this income record?', async () => {
    try {
      await apiFetch(`/api/income/${id}`, { method: 'DELETE' });
      showToast('Income record deleted.', 'success');
      loadIncomeData();
    } catch (err) {
      showToast(err.message, 'danger');
    }
  });
}

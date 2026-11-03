/* ==========================================================================
   EXPENSEMATE - Budgets Page Controller
   ========================================================================== */

let budgetUtilizationChart = null;

document.addEventListener('DOMContentLoaded', () => {
  loadExpenseCategoriesDropdown();
  loadBudgetsData();
});

async function loadExpenseCategoriesDropdown() {
  try {
    const res = await apiFetch('/api/categories?type=expense');
    const select = document.getElementById('b-category-id');
    select.innerHTML = '';
    res.data.forEach(c => {
      select.innerHTML += `<option value="${c.id}">${c.name}</option>`;
    });
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

async function loadBudgetsData() {
  const month = document.getElementById('budget-month-select').value;
  const year = document.getElementById('budget-year-select').value;

  try {
    const res = await apiFetch(`/api/budgets?month=${month}&year=${year}`);
    if (res.success) {
      renderBudgetsView(res.data);
    }
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

function renderBudgetsView(data) {
  const ov = data.overall;
  document.getElementById('b-metric-total').textContent = formatCurrency(ov.amount);
  document.getElementById('b-metric-spent').textContent = formatCurrency(ov.spent);
  document.getElementById('b-metric-pct').textContent = `${ov.percentage}% Used`;
  document.getElementById('b-metric-rem').textContent = formatCurrency(ov.remaining);

  renderBudgetUtilizationChart(ov.amount, ov.spent, ov.remaining, ov.percentage);
  renderCategoryBudgetsList(data.categories);
}

function renderBudgetUtilizationChart(budget, spent, remaining, usedPct) {
  const ctx = document.getElementById('chart-budget-utilization').getContext('2d');
  if (budgetUtilizationChart) budgetUtilizationChart.destroy();

  budgetUtilizationChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Spent', 'Remaining'],
      datasets: [{
        data: [Math.max(0, spent), Math.max(0, remaining)],
        backgroundColor: [
          usedPct >= 100 ? '#E53E3E' : (usedPct >= 80 ? '#DD6B20' : '#E8B4A8'),
          '#8FA3C0'
        ]
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '70%',
      plugins: {
        legend: { position: 'bottom' }
      }
    }
  });
}

function renderCategoryBudgetsList(categories) {
  const container = document.getElementById('budget-category-list');
  container.innerHTML = '';

  if (!categories || categories.length === 0) {
    container.innerHTML = '<div class="empty-state">No category budget limits set for this month.</div>';
    return;
  }

  categories.forEach(cat => {
    const statusClass = cat.status === 'Exceeded' ? 'exceeded' : (cat.status === 'Warning' ? 'warning' : 'normal');

    const item = document.createElement('div');
    item.className = 'card-panel';
    item.style.marginBottom = '12px';
    item.style.padding = '16px';

    item.innerHTML = `
      <div class="progress-meta" style="margin-bottom: 8px;">
        <span style="font-size: 1.05rem; font-weight: 700; color: var(--primary-dark);">${cat.category_name}</span>
        <span>${formatCurrency(cat.spent)} / ${formatCurrency(cat.amount)}</span>
      </div>
      <div class="progress-track" style="height: 12px;">
        <div class="progress-fill ${statusClass}" style="width: ${Math.min(cat.percentage, 100)}%;"></div>
      </div>
      <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px;">
        <span style="font-size: 0.82rem; color: var(--text-muted);">${cat.percentage}% Used • Remaining: ${formatCurrency(cat.remaining)}</span>
        <div style="display: flex; gap: 8px; align-items: center;">
          <span class="status-pill ${statusClass}">${cat.status}</span>
          <button class="btn-icon delete" onclick="deleteBudgetRecord(${cat.id})">Delete</button>
        </div>
      </div>
    `;
    container.appendChild(item);
  });
}

function toggleCategorySelect() {
  const type = document.getElementById('b-target-type').value;
  const group = document.getElementById('b-cat-group');
  group.style.display = type === 'category' ? 'block' : 'none';
}

function openBudgetModal() {
  document.getElementById('budget-form').reset();
  toggleCategorySelect();
  document.getElementById('budget-modal').classList.add('active');
}

function closeBudgetModal() {
  document.getElementById('budget-modal').classList.remove('active');
}

async function saveBudgetRecord(e) {
  e.preventDefault();
  const month = document.getElementById('budget-month-select').value;
  const year = document.getElementById('budget-year-select').value;
  const scope = document.getElementById('b-target-type').value;
  const categoryId = scope === 'category' ? document.getElementById('b-category-id').value : null;
  const amount = document.getElementById('b-amount').value;

  try {
    await apiFetch('/api/budgets', {
      method: 'POST',
      body: JSON.stringify({
        month: month,
        year: year,
        amount: amount,
        category_id: categoryId
      })
    });

    showToast('Budget saved successfully!', 'success');
    closeBudgetModal();
    loadBudgetsData();
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

function deleteBudgetRecord(id) {
  confirmAction('Delete Budget', 'Are you sure you want to delete this budget limit?', async () => {
    try {
      await apiFetch(`/api/budgets/${id}`, { method: 'DELETE' });
      showToast('Budget deleted.', 'success');
      loadBudgetsData();
    } catch (err) {
      showToast(err.message, 'danger');
    }
  });
}

let yearlyBudgetChart = null;
let currentBudgetTab = 'monthly';

function switchBudgetTab(tab) {
  currentBudgetTab = tab;
  const mSec = document.getElementById('monthly-budget-section');
  const ySec = document.getElementById('yearly-budget-section');
  const btnM = document.getElementById('tab-btn-monthly');
  const btnY = document.getElementById('tab-btn-yearly');

  if (tab === 'monthly') {
    mSec.style.display = 'block';
    ySec.style.display = 'none';
    btnM.className = 'btn btn-primary';
    btnY.className = 'btn btn-secondary';
    loadBudgetsData();
  } else {
    mSec.style.display = 'none';
    ySec.style.display = 'block';
    btnM.className = 'btn btn-secondary';
    btnY.className = 'btn btn-primary';
    loadYearlyBudgetData();
  }
}

async function loadYearlyBudgetData() {
  const yearSelect = document.getElementById('yearly-budget-year-select');
  const year = yearSelect ? yearSelect.value : new Date().getFullYear();

  try {
    const res = await apiFetch(`/api/budgets/yearly?year=${year}`);
    if (res.success) {
      renderYearlyBudgetView(res.data);
    }
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

function renderYearlyBudgetView(data) {
  const ov = data.overall;
  document.getElementById('yb-metric-total').textContent = formatCurrency(ov.annual_budget);
  document.getElementById('yb-metric-spent').textContent = formatCurrency(ov.annual_spent);
  document.getElementById('yb-metric-pct').textContent = `${ov.percentage}% Used`;
  document.getElementById('yb-metric-rem').textContent = formatCurrency(ov.annual_remaining);

  const statusEl = document.getElementById('yb-metric-status');
  statusEl.textContent = ov.status;
  statusEl.style.color = ov.status === 'Exceeded' ? '#E53E3E' : (ov.status === 'Warning' ? '#DD6B20' : '#2F855A');

  renderYearlyBudgetTrendChart(data.months, data.budget_trend, data.spent_trend);
  renderYearlyCategoryTable(data.categories);
}

function renderYearlyBudgetTrendChart(months, budgetTrend, spentTrend) {
  const ctx = document.getElementById('chart-yearly-budget-trend').getContext('2d');
  if (yearlyBudgetChart) yearlyBudgetChart.destroy();

  yearlyBudgetChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: months,
      datasets: [
        {
          label: 'Budget Allocated',
          data: budgetTrend,
          backgroundColor: '#3182CE'
        },
        {
          label: 'Actual Spent',
          data: spentTrend,
          backgroundColor: '#E53E3E'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom' }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: value => 'Rs. ' + value.toLocaleString()
          }
        }
      }
    }
  });
}

function renderYearlyCategoryTable(categories) {
  const tbody = document.getElementById('table-yearly-budget-body');
  tbody.innerHTML = '';

  if (!categories || categories.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" class="empty-state">No category budget limits or transactions recorded for this year.</td></tr>';
    return;
  }

  categories.forEach(cat => {
    const statusClass = cat.status === 'Exceeded' ? 'exceeded' : (cat.status === 'Warning' ? 'warning' : 'normal');

    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td style="font-weight: 600;">${cat.category_name}</td>
      <td style="text-align: right;">${formatCurrency(cat.annual_budget)}</td>
      <td style="text-align: right; font-weight: 700;">${formatCurrency(cat.annual_spent)}</td>
      <td style="text-align: right; color: ${cat.remaining < 0 ? '#E53E3E' : 'inherit'};">${formatCurrency(cat.remaining)}</td>
      <td style="text-align: right;">${cat.percentage}%</td>
      <td style="text-align: center;"><span class="status-pill ${statusClass}">${cat.status}</span></td>
    `;
    tbody.appendChild(tr);
  });
}

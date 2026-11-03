/* ==========================================================================
   EXPENSEMATE - Dashboard Controller & Chart.js Visual System
   ========================================================================== */

let spendGaugeChart = null;
let cashFlowChart = null;
let expenseAllocationChart = null;

document.addEventListener('DOMContentLoaded', () => {
  loadDashboardData();
  
  // Set default date input in modal to today
  const txDateInput = document.getElementById('tx-date');
  if (txDateInput) {
    txDateInput.value = new Date().toISOString().split('T')[0];
  }
});

async function loadDashboardData() {
  const month = document.getElementById('dash-month-select').value;
  const year = document.getElementById('dash-year-select').value;

  try {
    const res = await apiFetch(`/api/dashboard?month=${month}&year=${year}`);
    if (res.success) {
      renderDashboard(res.data);
    }
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

function renderDashboard(data) {
  const m = data.metrics;

  // Update Period Display
  const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  const periodStr = `${monthNames[data.month - 1]} ${data.year}`;
  document.getElementById('global-period-display').textContent = periodStr;

  // Update Metric Cards
  document.getElementById('val-balance').textContent = formatCurrency(m.total_balance);
  document.getElementById('val-income').textContent = formatCurrency(m.total_income);
  document.getElementById('val-expenses').textContent = formatCurrency(m.total_expenses);
  document.getElementById('val-savings').textContent = formatCurrency(m.savings);
  document.getElementById('sub-savings-rate').textContent = `Savings Rate: ${m.savings_rate}%`;

  document.getElementById('val-budget').textContent = formatCurrency(m.monthly_budget);
  document.getElementById('val-budget-rem').textContent = formatCurrency(m.budget_remaining);
  document.getElementById('sub-budget-pct').textContent = `${m.budget_used_percentage}% Used`;

  // Render Alerts
  renderAlerts(data.alerts);

  // Render Donut Gauge: Amount Left to Spend
  renderSpendGauge(m.monthly_budget, m.total_expenses, m.budget_remaining, m.budget_used_percentage);

  // Render Cash Flow Summary Bar Chart
  renderCashFlowChart(m.total_income, m.total_expenses, m.savings);

  // Render Expense Allocation Donut Chart
  renderExpenseAllocationChart(data.expense_allocation);

  // Render Category Budget Status Progress Bars
  renderBudgetCategoryProgress(data.budget_categories);

  // Render Income & Expense Summary Tables
  renderSummaryTable('table-income-summary', data.income_summary);
  renderSummaryTable('table-expense-summary', data.expense_allocation);

  // Render Recent Transactions
  renderRecentTransactions(data.recent_transactions);
}

function renderAlerts(alerts) {
  const container = document.getElementById('dashboard-alerts-container');
  container.innerHTML = '';
  if (!alerts || alerts.length === 0) return;

  alerts.forEach(al => {
    const card = document.createElement('div');
    const alertClass = al.type === 'danger' ? 'status-pill exceeded' : (al.type === 'warning' ? 'status-pill warning' : 'status-pill normal');
    card.style.cssText = 'background: #FFFFFF; border: 1px solid var(--border-light); border-left: 5px solid ' + (al.type === 'danger' ? '#E53E3E' : (al.type === 'warning' ? '#DD6B20' : '#38A169')) + '; border-radius: var(--radius-md); padding: 14px 18px; box-shadow: var(--shadow-sm); display: flex; align-items: center; justify-content: space-between;';
    card.innerHTML = `
      <div>
        <strong style="color: var(--primary-dark); font-size: 0.95rem;">${al.title}</strong>
        <p style="font-size: 0.85rem; color: var(--text-muted); margin-top: 2px;">${al.message}</p>
      </div>
      <span class="${alertClass}">${al.type.toUpperCase()}</span>
    `;
    container.appendChild(card);
  });
}

function renderSpendGauge(budget, spent, remaining, usedPct) {
  const ctx = document.getElementById('chart-spend-gauge').getContext('2d');
  
  document.getElementById('gauge-center-amt').textContent = formatCurrency(remaining);
  document.getElementById('gauge-center-lbl').textContent = `${usedPct}% USED`;

  if (spendGaugeChart) spendGaugeChart.destroy();

  const spentVal = Math.max(0, spent);
  const remVal = Math.max(0, remaining);

  spendGaugeChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Spent', 'Remaining'],
      datasets: [{
        data: [spentVal, remVal],
        backgroundColor: [
          usedPct >= 100 ? '#E53E3E' : (usedPct >= 80 ? '#DD6B20' : '#E8B4A8'),
          '#8FA3C0'
        ],
        borderWidth: 0,
        hoverOffset: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '76%',
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: function(context) {
              return ` ${context.label}: ${formatCurrency(context.raw)}`;
            }
          }
        }
      }
    }
  });
}

function renderCashFlowChart(income, expenses, savings) {
  const ctx = document.getElementById('chart-cash-flow').getContext('2d');
  if (cashFlowChart) cashFlowChart.destroy();

  cashFlowChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Income', 'Expenses', 'Savings'],
      datasets: [{
        data: [income, expenses, savings],
        backgroundColor: ['#48BB78', '#E53E3E', '#8FA3C0'],
        borderRadius: 8,
        barThickness: 36
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: { color: '#F0EAE1' },
          ticks: {
            callback: function(value) { return 'Rs.' + (value / 1000) + 'k'; }
          }
        },
        x: { grid: { display: false } }
      }
    }
  });
}

function renderExpenseAllocationChart(allocationData) {
  const ctx = document.getElementById('chart-expense-allocation').getContext('2d');
  if (expenseAllocationChart) expenseAllocationChart.destroy();

  if (!allocationData || allocationData.length === 0) {
    allocationData = [{ category_name: 'No Expenses', total: 1 }];
  }

  const labels = allocationData.map(d => d.category_name);
  const dataVals = allocationData.map(d => d.total);
  const palette = ['#8FA3C0', '#E8B4A8', '#F6AD55', '#68D391', '#63B3ED', '#B794F4', '#FC8181', '#CBD5E0'];

  expenseAllocationChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: dataVals,
        backgroundColor: palette.slice(0, labels.length),
        borderWidth: 2,
        borderColor: '#FFFFFF'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'right', labels: { boxWidth: 12, font: { family: 'Outfit', size: 12 } } }
      }
    }
  });
}

function renderBudgetCategoryProgress(categories) {
  const container = document.getElementById('dashboard-budget-list');
  container.innerHTML = '';

  if (!categories || categories.length === 0) {
    container.innerHTML = '<div class="empty-state">No category budgets set for this month.</div>';
    return;
  }

  categories.forEach(cat => {
    const statusClass = cat.status === 'Exceeded' ? 'exceeded' : (cat.status === 'Warning' ? 'warning' : 'normal');
    
    const item = document.createElement('div');
    item.className = 'progress-item';
    item.innerHTML = `
      <div class="progress-meta">
        <span>${cat.category_name}</span>
        <span>${formatCurrency(cat.spent)} / ${formatCurrency(cat.amount)}</span>
      </div>
      <div class="progress-track">
        <div class="progress-fill ${statusClass}" style="width: ${Math.min(cat.percentage, 100)}%;"></div>
      </div>
      <div style="display:flex; justify-content:space-between; align-items:center; margin-top:2px;">
        <span style="font-size:0.75rem; color:var(--text-muted);">${cat.percentage}% Used</span>
        <span class="status-pill ${statusClass}">${cat.status}</span>
      </div>
    `;
    container.appendChild(item);
  });
}

function renderSummaryTable(tableId, dataList) {
  const tbody = document.getElementById(tableId);
  tbody.innerHTML = '';

  if (!dataList || dataList.length === 0) {
    tbody.innerHTML = '<tr><td colspan="2" class="empty-state" style="padding:16px;">No data recorded.</td></tr>';
    return;
  }

  dataList.forEach(item => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td style="font-weight: 600;">${item.category_name}</td>
      <td style="text-align: right; font-weight: 700;">${formatCurrency(item.total)}</td>
    `;
    tbody.appendChild(tr);
  });
}

function renderRecentTransactions(transactions) {
  const tbody = document.getElementById('table-recent-transactions');
  tbody.innerHTML = '';

  if (!transactions || transactions.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5" class="empty-state">No recent transactions recorded.</td></tr>';
    return;
  }

  transactions.forEach(tx => {
    const tr = document.createElement('tr');
    const isInc = tx.transaction_type === 'income';
    const sign = isInc ? '+' : '-';
    const amountClass = isInc ? 'amount-income' : 'amount-expense';

    tr.innerHTML = `
      <td>${tx.transaction_date}</td>
      <td><span class="status-pill ${isInc ? 'normal' : 'exceeded'}">${tx.transaction_type}</span></td>
      <td style="font-weight: 600;">${tx.category_name}</td>
      <td>${tx.description || '-'}</td>
      <td style="text-align: right;" class="${amountClass}">${sign} ${formatCurrency(tx.amount)}</td>
    `;
    tbody.appendChild(tr);
  });
}

// Modal handling for Quick Add Expense/Income
async function openAddTransactionModal(type) {
  document.getElementById('tx-type').value = type;
  document.getElementById('tx-modal-title').textContent = type === 'income' ? 'Add Income Record' : 'Add Expense Record';
  
  // Load categories
  try {
    const res = await apiFetch(`/api/categories?type=${type}`);
    const select = document.getElementById('tx-category');
    select.innerHTML = '';
    res.data.forEach(c => {
      select.innerHTML += `<option value="${c.id}">${c.name}</option>`;
    });
    document.getElementById('tx-modal').classList.add('active');
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

function closeTxModal() {
  document.getElementById('tx-modal').classList.remove('active');
}

async function saveDashboardTransaction(e) {
  e.preventDefault();
  const type = document.getElementById('tx-type').value;
  const categoryId = document.getElementById('tx-category').value;
  const amount = document.getElementById('tx-amount').value;
  const date = document.getElementById('tx-date').value;
  const desc = document.getElementById('tx-desc').value;

  const endpoint = type === 'income' ? '/api/income' : '/api/expenses';

  try {
    await apiFetch(endpoint, {
      method: 'POST',
      body: JSON.stringify({
        category_id: categoryId,
        amount: amount,
        transaction_date: date,
        description: desc
      })
    });

    showToast(`${type.toUpperCase()} added successfully!`, 'success');
    closeTxModal();
    loadDashboardData();
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

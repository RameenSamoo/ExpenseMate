/* ==========================================================================
   EXPENSEMATE - Analytics & Comparison Controller
   ========================================================================== */

let anDistributionChart = null;
let anIncVsExpChart = null;
let anSpendingTrendChart = null;

document.addEventListener('DOMContentLoaded', () => {
  loadAnalyticsData();
  loadComparisonData();
});

async function loadAnalyticsData() {
  const month = document.getElementById('an-month-select').value;
  const year = document.getElementById('an-year-select').value;

  try {
    const res = await apiFetch(`/api/analytics?month=${month}&year=${year}`);
    if (res.success) {
      renderAnalyticsMetrics(res.data.metrics);
      renderAnalyticsCharts(res.data);
    }
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

function renderAnalyticsMetrics(m) {
  document.getElementById('an-savings-rate').textContent = `${m.savings_rate}%`;
  document.getElementById('an-highest-cat').textContent = m.highest_spending_category;
  document.getElementById('an-lowest-cat').textContent = m.lowest_spending_category;
  document.getElementById('an-net-savings').textContent = formatCurrency(m.savings);
  document.getElementById('an-tx-count').textContent = m.transaction_count;

  if (m.most_expensive_transaction) {
    document.getElementById('an-max-tx').textContent = formatCurrency(m.most_expensive_transaction.amount);
    document.getElementById('an-max-tx-name').textContent = `${m.most_expensive_transaction.category_name} (${m.most_expensive_transaction.transaction_date})`;
  } else {
    document.getElementById('an-max-tx').textContent = 'Rs. 0';
    document.getElementById('an-max-tx-name').textContent = 'No transactions';
  }
}

function renderAnalyticsCharts(data) {
  const distCtx = document.getElementById('chart-an-distribution').getContext('2d');
  const incExpCtx = document.getElementById('chart-an-inc-vs-exp').getContext('2d');
  const trendCtx = document.getElementById('chart-an-spending-trend').getContext('2d');

  if (anDistributionChart) anDistributionChart.destroy();
  if (anIncVsExpChart) anIncVsExpChart.destroy();
  if (anSpendingTrendChart) anSpendingTrendChart.destroy();

  // 1. Distribution Donut
  const expCats = data.expense_categories || [];
  anDistributionChart = new Chart(distCtx, {
    type: 'doughnut',
    data: {
      labels: expCats.map(c => c.category_name),
      datasets: [{
        data: expCats.map(c => c.total),
        backgroundColor: ['#8FA3C0', '#E8B4A8', '#F6AD55', '#68D391', '#63B3ED', '#B794F4']
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: 'right' } }
    }
  });

  // 2. Income vs Expense Bar
  const m = data.metrics;
  anIncVsExpChart = new Chart(incExpCtx, {
    type: 'bar',
    data: {
      labels: ['Income', 'Expense'],
      datasets: [{
        data: [m.total_income, m.total_expenses],
        backgroundColor: ['#48BB78', '#E53E3E'],
        borderRadius: 8,
        barThickness: 40
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, grid: { color: '#F0EAE1' } },
        x: { grid: { display: false } }
      }
    }
  });

  // 3. Monthly Spending Trend Line Chart
  const cashFlow = data.cash_flow_trend || [];
  const monthLabels = Array.from(new Set(cashFlow.map(c => c.month_str)));
  const incMap = {};
  const expMap = {};

  cashFlow.forEach(row => {
    if (row.transaction_type === 'income') incMap[row.month_str] = row.total;
    if (row.transaction_type === 'expense') expMap[row.month_str] = row.total;
  });

  anSpendingTrendChart = new Chart(trendCtx, {
    type: 'line',
    data: {
      labels: monthLabels,
      datasets: [
        {
          label: 'Income',
          data: monthLabels.map(l => incMap[l] || 0),
          borderColor: '#48BB78',
          backgroundColor: 'rgba(72, 187, 120, 0.1)',
          fill: true,
          tension: 0.3
        },
        {
          label: 'Expenses',
          data: monthLabels.map(l => expMap[l] || 0),
          borderColor: '#E53E3E',
          backgroundColor: 'rgba(229, 62, 62, 0.1)',
          fill: true,
          tension: 0.3
        }
      ]
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

async function loadComparisonData() {
  const m1 = document.getElementById('comp-m1').value;
  const y1 = document.getElementById('comp-y1').value;
  const m2 = document.getElementById('comp-m2').value;
  const y2 = document.getElementById('comp-y2').value;

  const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  document.getElementById('comp-th-m1').textContent = `${monthNames[parseInt(m1)-1]} ${y1}`;
  document.getElementById('comp-th-m2').textContent = `${monthNames[parseInt(m2)-1]} ${y2}`;

  try {
    const res = await apiFetch(`/api/analytics/comparison?m1=${m1}&y1=${y1}&m2=${m2}&y2=${y2}`);
    if (res.success) {
      renderComparisonTable(res.data.categories);
    }
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

function renderComparisonTable(categories) {
  const tbody = document.getElementById('table-comparison-body');
  tbody.innerHTML = '';

  if (!categories || categories.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5" class="empty-state">No category spending comparison available.</td></tr>';
    return;
  }

  categories.forEach(item => {
    const isInc = item.difference > 0;
    const arrow = isInc ? '▲' : (item.difference < 0 ? '▼' : '•');
    const colorStyle = isInc ? 'color: #C53030; font-weight:700;' : (item.difference < 0 ? 'color: #2F855A; font-weight:700;' : 'color: var(--text-muted);');

    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td style="font-weight: 600;">${item.category_name}</td>
      <td style="text-align: right;">${formatCurrency(item.month1_amount)}</td>
      <td style="text-align: right;">${formatCurrency(item.month2_amount)}</td>
      <td style="text-align: right; ${colorStyle}">${isInc ? '+' : ''}${formatCurrency(item.difference)}</td>
      <td style="text-align: right; ${colorStyle}">${arrow} ${item.percentage_change}%</td>
    `;
    tbody.appendChild(tr);
  });
}

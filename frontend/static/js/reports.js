/* ==========================================================================
   EXPENSEMATE - Reports Controller
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  loadReportData();
});

async function loadReportData() {
  const month = document.getElementById('report-month-select').value;
  const year = document.getElementById('report-year-select').value;

  try {
    const res = await apiFetch(`/api/reports?month=${month}&year=${year}`);
    if (res.success) {
      renderReportDocument(res.data);
    }
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

function renderReportDocument(d) {
  const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  document.getElementById('report-date-str').textContent = `Period: ${monthNames[d.month - 1]} ${d.year}`;
  document.getElementById('report-user-name').textContent = d.user_name || 'User';

  const m = d.metrics;
  document.getElementById('rep-inc').textContent = formatCurrency(m.total_income);
  document.getElementById('rep-exp').textContent = formatCurrency(m.total_expenses);
  document.getElementById('rep-sav').textContent = formatCurrency(m.savings);
  document.getElementById('rep-rate').textContent = `${m.savings_rate}%`;

  document.getElementById('rep-budget').textContent = formatCurrency(m.monthly_budget);
  document.getElementById('rep-budget-used').textContent = `${m.budget_used_percentage}%`;
  document.getElementById('rep-top-cat').textContent = d.top_spending_category;

  // Expense Allocation Table
  const expTbody = document.getElementById('table-report-exp-body');
  expTbody.innerHTML = '';
  if (!d.expense_allocation || d.expense_allocation.length === 0) {
    expTbody.innerHTML = '<tr><td colspan="2" class="empty-state">No expenses recorded for this period.</td></tr>';
  } else {
    d.expense_allocation.forEach(row => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td style="font-weight: 600;">${row.category_name}</td>
        <td style="text-align: right; font-weight: 700;">${formatCurrency(row.total)}</td>
      `;
      expTbody.appendChild(tr);
    });
  }

  // Goals Table
  const goalsTbody = document.getElementById('table-report-goals-body');
  goalsTbody.innerHTML = '';
  if (!d.goals_list || d.goals_list.length === 0) {
    goalsTbody.innerHTML = '<tr><td colspan="6" class="empty-state">No financial goals set.</td></tr>';
  } else {
    d.goals_list.forEach(g => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td style="font-weight: 600;">${g.goal_name}</td>
        <td>${g.target_date}</td>
        <td style="text-align: right;">${formatCurrency(g.target_amount)}</td>
        <td style="text-align: right; color: #2F855A; font-weight: 700;">${formatCurrency(g.current_amount)}</td>
        <td>${g.progress_percentage}%</td>
        <td><span class="status-pill normal">${g.status}</span></td>
      `;
      goalsTbody.appendChild(tr);
    });
  }
}

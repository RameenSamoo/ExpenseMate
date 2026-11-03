/* ==========================================================================
   EXPENSEMATE - Savings Goal Tracker Controller
   ========================================================================== */

let goalsDistributionChart = null;
let goalsMonthlyChart = null;

document.addEventListener('DOMContentLoaded', () => {
  loadGoalsData();

  const gStartDate = document.getElementById('goal-start-date');
  const gTargetDate = document.getElementById('goal-target-date');
  const cDate = document.getElementById('contrib-date');

  const today = new Date().toISOString().split('T')[0];
  if (gStartDate) gStartDate.value = today;
  if (cDate) cDate.value = today;
  
  // Set default target date 1 year from now
  const nextYear = new Date();
  nextYear.setFullYear(nextYear.getFullYear() + 1);
  if (gTargetDate) gTargetDate.value = nextYear.toISOString().split('T')[0];
});

async function loadGoalsData() {
  try {
    const res = await apiFetch('/api/goals');
    if (res.success) {
      renderGoalMetrics(res.data.summary);
      renderGoalsCharts(res.data.goals);
      renderGoalsTable(res.data.goals);
    }
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

function renderGoalMetrics(summary) {
  document.getElementById('g-metric-target').textContent = formatCurrency(summary.total_goal_amount);
  document.getElementById('g-metric-saved').textContent = formatCurrency(summary.total_saved_amount);
  document.getElementById('g-metric-active').textContent = summary.active_goals_count;
  document.getElementById('g-metric-progress').textContent = `${summary.overall_progress_percentage}%`;
}

function renderGoalsCharts(goals) {
  const distCtx = document.getElementById('chart-goals-distribution').getContext('2d');
  const monthlyCtx = document.getElementById('chart-goals-monthly').getContext('2d');

  if (goalsDistributionChart) goalsDistributionChart.destroy();
  if (goalsMonthlyChart) goalsMonthlyChart.destroy();

  if (!goals || goals.length === 0) return;

  const names = goals.map(g => g.goal_name);
  const savedVals = goals.map(g => g.current_amount);
  const monthlyTargets = goals.map(g => g.required_monthly);

  const palette = ['#8FA3C0', '#E8B4A8', '#F6AD55', '#68D391', '#63B3ED', '#B794F4'];

  // Distribution Donut
  goalsDistributionChart = new Chart(distCtx, {
    type: 'doughnut',
    data: {
      labels: names,
      datasets: [{
        data: savedVals,
        backgroundColor: palette.slice(0, names.length)
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: 'right' } }
    }
  });

  // Monthly Contribution Target Bar Chart
  goalsMonthlyChart = new Chart(monthlyCtx, {
    type: 'bar',
    data: {
      labels: names,
      datasets: [{
        label: 'Monthly Target (Rs.)',
        data: monthlyTargets,
        backgroundColor: '#8FA3C0',
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

function renderGoalsTable(goals) {
  const tbody = document.getElementById('table-goals-body');
  tbody.innerHTML = '';

  if (!goals || goals.length === 0) {
    tbody.innerHTML = '<tr><td colspan="9" class="empty-state">No financial goals set. Click "+ Create Goal" to begin!</td></tr>';
    return;
  }

  goals.forEach(g => {
    let statusClass = 'normal';
    if (g.status === 'Completed') statusClass = 'normal';
    if (g.status === 'On Track') statusClass = 'normal';
    if (g.status === 'In Progress') statusClass = 'normal';
    if (g.status === 'Deadline Approaching') statusClass = 'warning';
    if (g.status === 'Behind Schedule') statusClass = 'exceeded';

    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td style="font-weight: 700; color: var(--primary-dark);">${g.goal_name}</td>
      <td>${g.start_date}</td>
      <td>${g.target_date}</td>
      <td style="text-align: right; font-weight: 600;">${formatCurrency(g.target_amount)}</td>
      <td style="text-align: right; font-weight: 700; color: #2F855A;">${formatCurrency(g.current_amount)}</td>
      <td style="text-align: right;">${formatCurrency(g.required_monthly)}</td>
      <td>
        <div class="progress-track" style="height: 8px;">
          <div class="progress-fill ${statusClass}" style="width: ${g.progress_percentage}%;"></div>
        </div>
        <span style="font-size: 0.75rem; color: var(--text-muted);">${g.progress_percentage}%</span>
      </td>
      <td><span class="status-pill ${statusClass}">${g.status}</span></td>
      <td style="text-align: right;">
        <div class="action-buttons" style="justify-content: flex-end;">
          <button class="btn-icon" style="background: var(--status-normal-bg); color: var(--status-normal-text);" onclick="openAddContribModal(${g.id}, '${g.goal_name}')">+ Save</button>
          <button class="btn-icon" onclick="openEditGoalModal(${g.id})">Edit</button>
          <button class="btn-icon delete" onclick="deleteGoalRecord(${g.id})">Delete</button>
        </div>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function openGoalModal() {
  document.getElementById('goal-id').value = '';
  document.getElementById('goal-modal-title').textContent = 'Create Financial Goal';
  document.getElementById('goal-form').reset();
  
  const today = new Date().toISOString().split('T')[0];
  document.getElementById('goal-start-date').value = today;
  document.getElementById('goal-modal').classList.add('active');
}

function closeGoalModal() {
  document.getElementById('goal-modal').classList.remove('active');
}

async function openEditGoalModal(id) {
  try {
    const res = await apiFetch(`/api/goals/${id}`);
    const g = res.data;

    document.getElementById('goal-id').value = g.id;
    document.getElementById('goal-name').value = g.goal_name;
    document.getElementById('goal-start-date').value = g.start_date;
    document.getElementById('goal-target-date').value = g.target_date;
    document.getElementById('goal-target-amt').value = g.target_amount;
    document.getElementById('goal-starting-amt').value = g.starting_amount;
    document.getElementById('goal-monthly-target').value = g.monthly_target;
    document.getElementById('goal-priority').value = g.priority;
    document.getElementById('goal-notes').value = g.notes || '';

    document.getElementById('goal-modal-title').textContent = 'Edit Goal Details';
    document.getElementById('goal-modal').classList.add('active');
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

async function saveGoalRecord(e) {
  e.preventDefault();
  const id = document.getElementById('goal-id').value;
  const goalName = document.getElementById('goal-name').value;
  const startDate = document.getElementById('goal-start-date').value;
  const targetDate = document.getElementById('goal-target-date').value;
  const targetAmt = document.getElementById('goal-target-amt').value;
  const startingAmt = document.getElementById('goal-starting-amt').value;
  const monthlyTarget = document.getElementById('goal-monthly-target').value;
  const priority = document.getElementById('goal-priority').value;
  const notes = document.getElementById('goal-notes').value;

  const url = id ? `/api/goals/${id}` : '/api/goals';
  const method = id ? 'PUT' : 'POST';

  try {
    await apiFetch(url, {
      method: method,
      body: JSON.stringify({
        goal_name: goalName,
        start_date: startDate,
        target_date: targetDate,
        target_amount: targetAmt,
        starting_amount: startingAmt,
        monthly_target: monthlyTarget,
        priority: priority,
        notes: notes
      })
    });

    showToast(`Goal ${id ? 'updated' : 'created'} successfully!`, 'success');
    closeGoalModal();
    loadGoalsData();
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

function openAddContribModal(goalId, goalName) {
  document.getElementById('contrib-goal-id').value = goalId;
  document.getElementById('contrib-modal-title').textContent = `Add Savings Deposit: ${goalName}`;
  document.getElementById('contrib-form').reset();
  document.getElementById('contrib-date').value = new Date().toISOString().split('T')[0];
  document.getElementById('contrib-modal').classList.add('active');
}

function closeContribModal() {
  document.getElementById('contrib-modal').classList.remove('active');
}

async function saveGoalContribution(e) {
  e.preventDefault();
  const goalId = document.getElementById('contrib-goal-id').value;
  const amount = document.getElementById('contrib-amount').value;
  const date = document.getElementById('contrib-date').value;
  const desc = document.getElementById('contrib-desc').value;

  try {
    await apiFetch(`/api/goals/${goalId}/contributions`, {
      method: 'POST',
      body: JSON.stringify({
        amount: amount,
        contribution_date: date,
        description: desc
      })
    });

    showToast('Contribution added to savings goal!', 'success');
    closeContribModal();
    loadGoalsData();
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

function deleteGoalRecord(id) {
  confirmAction('Delete Goal', 'Are you sure you want to delete this financial goal and all contribution history?', async () => {
    try {
      await apiFetch(`/api/goals/${id}`, { method: 'DELETE' });
      showToast('Goal deleted.', 'success');
      loadGoalsData();
    } catch (err) {
      showToast(err.message, 'danger');
    }
  });
}

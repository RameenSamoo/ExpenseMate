/* ==========================================================================
   EXPENSEMATE - Transactions Page & CSV Controller
   ========================================================================== */

let currentPage = 1;

document.addEventListener('DOMContentLoaded', () => {
  loadCategoriesFilter();
  loadTransactionsData(1);
});

async function loadCategoriesFilter() {
  try {
    const res = await apiFetch('/api/categories');
    const select = document.getElementById('tx-cat-filter');
    select.innerHTML = '<option value="">All Categories</option>';
    res.data.forEach(c => {
      select.innerHTML += `<option value="${c.id}">${c.name} (${c.type})</option>`;
    });
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

async function loadTransactionsData(page = 1) {
  currentPage = page;
  const search = document.getElementById('tx-search-input').value;
  const type = document.getElementById('tx-type-filter').value;
  const categoryId = document.getElementById('tx-cat-filter').value;
  const month = document.getElementById('tx-month-filter').value;
  const year = document.getElementById('tx-year-filter').value;

  const queryParams = new URLSearchParams({
    page: page,
    limit: 15,
    type: type,
    category_id: categoryId,
    month: month,
    year: year,
    search: search
  });

  try {
    const res = await apiFetch(`/api/transactions?${queryParams.toString()}`);
    if (res.success) {
      renderTransactionsTable(res.data.items);
      renderPagination(res.data);
    }
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

function renderTransactionsTable(items) {
  const tbody = document.getElementById('table-transactions-body');
  tbody.innerHTML = '';

  if (!items || items.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" class="empty-state">No matching transactions found.</td></tr>';
    return;
  }

  items.forEach(tx => {
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
      <td style="text-align: right;">
        <div class="action-buttons" style="justify-content: flex-end;">
          <button class="btn-icon delete" onclick="deleteTransactionRecord(${tx.id}, '${tx.transaction_type}')">Delete</button>
        </div>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function renderPagination(data) {
  const info = document.getElementById('pagination-info-text');
  const container = document.getElementById('pagination-buttons');
  
  info.textContent = `Page ${data.page} of ${data.total_pages} (${data.total} total records)`;
  container.innerHTML = '';

  const prevBtn = document.createElement('button');
  prevBtn.className = 'btn-page';
  prevBtn.textContent = '« Prev';
  prevBtn.disabled = data.page <= 1;
  prevBtn.onclick = () => loadTransactionsData(data.page - 1);
  container.appendChild(prevBtn);

  for (let p = 1; p <= data.total_pages; p++) {
    const pageBtn = document.createElement('button');
    pageBtn.className = `btn-page ${p === data.page ? 'active' : ''}`;
    pageBtn.textContent = p;
    pageBtn.onclick = () => loadTransactionsData(p);
    container.appendChild(pageBtn);
  }

  const nextBtn = document.createElement('button');
  nextBtn.className = 'btn-page';
  nextBtn.textContent = 'Next »';
  nextBtn.disabled = data.page >= data.total_pages;
  nextBtn.onclick = () => loadTransactionsData(data.page + 1);
  container.appendChild(nextBtn);
}

function exportTransactionsCSV() {
  const type = document.getElementById('tx-type-filter').value;
  const categoryId = document.getElementById('tx-cat-filter').value;
  const month = document.getElementById('tx-month-filter').value;
  const year = document.getElementById('tx-year-filter').value;

  const queryParams = new URLSearchParams({
    type: type,
    category_id: categoryId,
    month: month,
    year: year
  });

  window.location.href = `/api/export?${queryParams.toString()}`;
}

function openImportModal() {
  document.getElementById('import-form').reset();
  document.getElementById('import-summary-result').style.display = 'none';
  document.getElementById('import-modal').classList.add('active');
}

function closeImportModal() {
  document.getElementById('import-modal').classList.remove('active');
}

async function uploadCSVFile(e) {
  e.preventDefault();
  const fileInput = document.getElementById('csv-file-input');
  if (!fileInput.files || fileInput.files.length === 0) {
    showToast('Please select a CSV file first.', 'warning');
    return;
  }

  const file = fileInput.files[0];
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch('/api/import', {
      method: 'POST',
      body: formData
    });
    const res = await response.json();

    if (!res.success) {
      throw new Error(res.message);
    }

    const summaryBox = document.getElementById('import-summary-result');
    summaryBox.style.display = 'block';
    summaryBox.className = 'demo-box';
    summaryBox.innerHTML = `
      <strong>Import Results:</strong><br>
      ✓ Imported: <strong>${res.summary.imported}</strong> rows<br>
      ✕ Rejected: <strong>${res.summary.rejected}</strong> rows
      ${res.summary.errors.length > 0 ? `<br><small style="color:#C53030;">Errors: ${res.summary.errors.join(', ')}</small>` : ''}
    `;

    showToast(res.message, 'success');
    loadTransactionsData(1);
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

function deleteTransactionRecord(id, type) {
  confirmAction('Delete Transaction', 'Are you sure you want to delete this transaction?', async () => {
    try {
      const endpoint = type === 'income' ? `/api/income/${id}` : `/api/expenses/${id}`;
      await apiFetch(endpoint, { method: 'DELETE' });
      showToast('Transaction deleted.', 'success');
      loadTransactionsData(currentPage);
    } catch (err) {
      showToast(err.message, 'danger');
    }
  });
}

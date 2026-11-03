/* ==========================================================================
   EXPENSEMATE - Category Manager Controller
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  loadCategoriesData();
});

async function loadCategoriesData() {
  try {
    const res = await apiFetch('/api/categories');
    if (res.success) {
      const expCats = res.data.filter(c => c.type === 'expense');
      const incCats = res.data.filter(c => c.type === 'income');

      renderCategoryTable('table-expense-cats-body', expCats);
      renderCategoryTable('table-income-cats-body', incCats);
    }
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

function renderCategoryTable(tableId, categories) {
  const tbody = document.getElementById(tableId);
  tbody.innerHTML = '';

  if (!categories || categories.length === 0) {
    tbody.innerHTML = '<tr><td colspan="2" class="empty-state">No categories configured.</td></tr>';
    return;
  }

  categories.forEach(cat => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td style="font-weight: 600;">${cat.name}</td>
      <td style="text-align: right;">
        <div class="action-buttons" style="justify-content: flex-end;">
          <button class="btn-icon" onclick="openRenameCategoryModal(${cat.id}, '${cat.name}', '${cat.type}')">Rename</button>
          <button class="btn-icon delete" onclick="deleteCategoryRecord(${cat.id}, '${cat.name}')">Delete</button>
        </div>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function openCategoryModal(type) {
  document.getElementById('cat-id').value = '';
  document.getElementById('cat-type').value = type;
  document.getElementById('cat-modal-title').textContent = `Add ${type.toUpperCase()} Category`;
  document.getElementById('category-form').reset();
  document.getElementById('category-modal').classList.add('active');
}

function closeCategoryModal() {
  document.getElementById('category-modal').classList.remove('active');
}

function openRenameCategoryModal(id, currentName, type) {
  document.getElementById('cat-id').value = id;
  document.getElementById('cat-type').value = type;
  document.getElementById('cat-name').value = currentName;
  document.getElementById('cat-modal-title').textContent = `Rename Category`;
  document.getElementById('category-modal').classList.add('active');
}

async function saveCategoryRecord(e) {
  e.preventDefault();
  const id = document.getElementById('cat-id').value;
  const name = document.getElementById('cat-name').value;
  const type = document.getElementById('cat-type').value;

  const url = id ? `/api/categories/${id}` : '/api/categories';
  const method = id ? 'PUT' : 'POST';

  try {
    await apiFetch(url, {
      method: method,
      body: JSON.stringify({ name, type })
    });

    showToast(`Category ${id ? 'renamed' : 'added'} successfully!`, 'success');
    closeCategoryModal();
    loadCategoriesData();
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

function deleteCategoryRecord(id, name) {
  confirmAction('Delete Category', `Are you sure you want to delete category '${name}'?`, async () => {
    try {
      await apiFetch(`/api/categories/${id}`, { method: 'DELETE' });
      showToast(`Category '${name}' deleted successfully.`, 'success');
      loadCategoriesData();
    } catch (err) {
      showToast(err.message, 'danger');
    }
  });
}

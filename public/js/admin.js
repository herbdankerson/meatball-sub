const API_BASE = '/api';

const token = localStorage.getItem('token');
if (!token) window.location.href = 'index.html';

document.getElementById('logoutBtn').addEventListener('click', () => {
  localStorage.clear();
  window.location.href = 'index.html';
});

async function fetchProducts() {
  const res = await fetch(`${API_BASE}/products`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  if (!res.ok) return [];
  return res.json();
}

function renderProducts(products) {
  const tbody = document.querySelector('#productsTable tbody');
  tbody.innerHTML = '';
  products.forEach(p => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><input value="${p.name}" data-id="${p.id}" data-field="name"></td>
      <td><input value="${p.description}" data-id="${p.id}" data-field="description"></td>
      <td><input type="number" value="${p.price}" data-id="${p.id}" data-field="price"></td>
      <td><input type="checkbox" ${p.visible ? 'checked' : ''} data-id="${p.id}" data-field="visible"></td>
      <td><button data-id="${p.id}" class="saveBtn">Save</button></td>`;
    tbody.appendChild(tr);
  });
}

async function load() {
  const products = await fetchProducts();
  renderProducts(products);
}

load();

document.querySelector('#productsTable').addEventListener('click', async (e) => {
  if (e.target.classList.contains('saveBtn')) {
    const id = e.target.getAttribute('data-id');
    const row = e.target.parentElement.parentElement;
    const inputs = row.querySelectorAll('input');
    const updated = {};
    inputs.forEach(i => {
      if (i.type === 'checkbox') {
        updated[i.dataset.field] = i.checked;
      } else {
        updated[i.dataset.field] = i.value;
      }
    });
    await fetch(`${API_BASE}/products?id=eq.${id}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify(updated)
    });
    load();
  }
});

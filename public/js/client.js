const API_BASE = '/api';
const token = localStorage.getItem('token');
if (!token) window.location.href = 'index.html';

document.getElementById('logoutBtn').addEventListener('click', () => {
  localStorage.clear();
  window.location.href = 'index.html';
});

const productList = document.getElementById('productList');
const cartItems = document.getElementById('cartItems');
let cart = [];

async function fetchProducts() {
  const res = await fetch(`${API_BASE}/client_products`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  if (!res.ok) return [];
  return res.json();
}

function renderProducts(products) {
  productList.innerHTML = '';
  products.forEach(p => {
    const div = document.createElement('div');
    div.className = 'product';
    div.innerHTML = `
      <img src="${p.image_url}" alt="${p.name}">
      <h3>${p.name}</h3>
      <p>${p.description}</p>
      <p>Price: $${p.price}</p>
      <button data-id="${p.id}">Add to Cart</button>`;
    productList.appendChild(div);
  });
}

function renderCart() {
  cartItems.innerHTML = '';
  cart.forEach(item => {
    const li = document.createElement('li');
    li.textContent = `${item.name} x${item.qty}`;
    cartItems.appendChild(li);
  });
}

productList.addEventListener('click', (e) => {
  if (e.target.tagName === 'BUTTON') {
    const id = e.target.getAttribute('data-id');
    const prod = cart.find(i => i.id == id);
    if (prod) {
      prod.qty++;
    } else {
      const name = e.target.parentElement.querySelector('h3').textContent;
      cart.push({id, name, qty: 1});
    }
    renderCart();
  }
});

document.getElementById('placeOrderBtn').addEventListener('click', async () => {
  if (!cart.length) return;
  await fetch(`${API_BASE}/orders`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({items: cart})
  });
  cart = [];
  renderCart();
  alert('Order placed!');
});

async function load() {
  const products = await fetchProducts();
  renderProducts(products);
}

load();

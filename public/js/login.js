const API_BASE = '/api';

const form = document.getElementById('loginForm');
const errorDiv = document.getElementById('loginError');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;
  try {
    const res = await fetch(`${API_BASE}/login`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({username, password})
    });
    if (!res.ok) throw new Error('Login failed');
    const data = await res.json();
    localStorage.setItem('token', data.token);
    localStorage.setItem('role', data.role);
    if (data.role === 'admin') {
      window.location.href = 'admin.html';
    } else {
      window.location.href = 'client.html';
    }
  } catch (err) {
    errorDiv.textContent = err.message;
  }
});

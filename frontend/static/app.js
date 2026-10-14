const API = "";

function getToken() {
  try {
    return localStorage.getItem("sharelist_token");
  } catch {
    return null;
  }
}

function setToken(token) {
  try {
    localStorage.setItem("sharelist_token", token);
  } catch {
    // ignore storage errors (e.g. private browsing)
  }
}

function clearToken() {
  try {
    localStorage.removeItem("sharelist_token");
  } catch {
    // ignore
  }
}

async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(API + path, { ...options, headers });
  let body = null;
  try {
    body = await res.json();
  } catch {
    body = null;
  }
  if (!res.ok) {
    const detail = body && body.detail ? body.detail : `Request failed (${res.status})`;
    const err = new Error(detail);
    err.status = res.status;
    throw err;
  }
  return body;
}

function showError(el, message) {
  if (el) el.textContent = message;
}

function requireAuthOrRedirect() {
  if (!getToken()) {
    window.location.href = "index.html";
  }
}

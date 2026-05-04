const chatContainer = document.getElementById('chat-container');
const orderInput    = document.getElementById('order-input');
const sendBtn       = document.getElementById('send-button');

const sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);

// Check authentication on page load
function initAuth() {
  const token = localStorage.getItem('token');
  const user = localStorage.getItem('user');
  const userInfoBar = document.getElementById('user-info-bar');
  
  if (token && user) {
    try {
      const userData = JSON.parse(user);
      document.getElementById('user-name').textContent = userData.name.split(' ')[0];
      if (userInfoBar) {
        userInfoBar.classList.remove('hidden');
      }
    } catch (e) {
      console.error('Error parsing user data:', e);
      redirectToLogin();
    }
  } else {
    // Redirect to login if not authenticated
    if (window.location.pathname === '/') {
      redirectToLogin();
    }
  }
}

function redirectToLogin() {
  window.location.href = '/login';
}

function handleLogout() {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  redirectToLogin();
}

// Auto-grow textarea
if (orderInput) {
  orderInput.addEventListener('input', function () {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 120) + 'px';
  });

  // Keyboard send
  orderInput.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  });
}

if (sendBtn) {
  sendBtn.addEventListener('click', sendMessage);
}

// Quick buttons — chips + action grid
document.querySelectorAll('[data-quick]').forEach(btn => {
  btn.addEventListener('click', function () {
    const msg = this.dataset.quick;
    appendMessage(msg, 'user');
    processMessage(msg);
    if (this.closest('.menu-strip')) {
      document.querySelectorAll('.menu-chip').forEach(c => c.classList.remove('active'));
      this.classList.add('active');
    }
  });
});

function sendMessage() {
  const text = orderInput.value.trim();
  if (!text) return;
  appendMessage(text, 'user');
  orderInput.value = '';
  orderInput.style.height = 'auto';
  processMessage(text);
}

function appendMessage(text, sender) {
  const wrap   = document.createElement('div');
  wrap.className = `message ${sender}-message`;

  const inner  = document.createElement('div');
  inner.className = 'msg-wrap';

  const label  = document.createElement('span');
  label.className = 'msg-label';
  label.textContent = sender === 'user' ? 'You' : 'James';

  const bubble = document.createElement('div');
  bubble.className = 'message-bubble';
  bubble.innerHTML = text.replace(/\n/g, '<br>');

  inner.appendChild(label);
  inner.appendChild(bubble);
  wrap.appendChild(inner);
  chatContainer.appendChild(wrap);
  scrollBottom();
  return wrap;
}

function showTyping() {
  const wrap = document.createElement('div');
  wrap.className = 'message bot-message';
  wrap.id = 'typing-indicator';

  const inner = document.createElement('div');
  inner.className = 'msg-wrap';

  const label = document.createElement('span');
  label.className = 'msg-label';
  label.textContent = 'James';

  const bubble = document.createElement('div');
  bubble.className = 'typing-bubble';
  bubble.innerHTML = `
    <div class="dot-anim"><span></span><span></span><span></span></div>
    <span class="typing-text">Preparing your response…</span>
  `;

  inner.appendChild(label);
  inner.appendChild(bubble);
  wrap.appendChild(inner);
  chatContainer.appendChild(wrap);
  scrollBottom();
}

function removeTyping() {
  const el = document.getElementById('typing-indicator');
  if (el) el.remove();
}

async function processMessage(message) {
  showTyping();
  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: message, session_id: sessionId })
    });
    const data = await res.json();
    removeTyping();
    appendMessage(data.message || 'I apologise — something went wrong.', 'bot');
    if (data.order_completed) {
      setTimeout(() => {
        appendMessage('✅ Your order has been placed. Our kitchen will begin shortly. Bon appétit!', 'bot');
        showToast('🎉 Order confirmed — estimated 20 min');
      }, 700);
    }
  } catch (err) {
    removeTyping();
    appendMessage('I sincerely apologise — there was a connection error. Please try again.', 'bot');
  }
}

function scrollBottom() {
  chatContainer.scrollTo({ top: chatContainer.scrollHeight, behavior: 'smooth' });
}

function clearChat() {
  chatContainer.innerHTML = '';
  appendMessage('The conversation has been cleared. How may I assist you this evening?', 'bot');
}

function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 3500);
}

// Initialize authentication
initAuth();

if (orderInput) {
  orderInput.focus();
}
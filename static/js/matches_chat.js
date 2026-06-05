/**
 * DateMe — matches_chat.js
 * Real-time polling: new messages, read receipts, typing indicator, reactions.
 * Global notification polling (new matches + unread counts) runs even outside chat.
 */

/* ── Report modal (always needed) ─────────────────────────────────────── */
document.addEventListener("DOMContentLoaded", function () {
  const modal       = document.getElementById("reportModal");
  const submitBtn   = document.getElementById("submitReport");
  const reasonInput = document.getElementById("reasonInput");

  window.openReport = function () { if (modal) modal.classList.add("show"); };
  window.closeReport = function () { if (modal) modal.classList.remove("show"); };
  window.selectReason = function (btn, val) {
    document.querySelectorAll(".reason-btn").forEach(b => b.classList.remove("selected"));
    btn.classList.add("selected");
    if (reasonInput) reasonInput.value = val;
    if (submitBtn)   submitBtn.disabled = false;
  };
  if (modal) modal.addEventListener("click", e => { if (e.target === modal) window.closeReport(); });
});

/* ── Chat initialiser (called only when a chat is open) ─────────────── */
function initChat() {
  const chatBody     = document.getElementById("chatBody");
  const typingBubble = document.getElementById("typingBubble");
  const msgInput     = document.getElementById("msgInput");
  const emojiPopup   = document.getElementById("emojiPickerPopup");

  let lastMsgId      = getLastMsgId();
  let typingTimer    = null;
  let activeMsgId    = null;   // msg currently showing emoji picker for

  // Initial scroll
  if (chatBody) chatBody.scrollTop = chatBody.scrollHeight;

  /* ── Message polling (every 2 s) ─── */
  setInterval(async () => {
    try {
      const res  = await fetch(`${POLL_URL}?after=${lastMsgId}`);
      const data = await res.json();
      if (data.messages && data.messages.length > 0) {
        data.messages.forEach(msg => {
          appendOrUpdateMessage(msg);
          if (msg.id > lastMsgId) lastMsgId = msg.id;
        });
        chatBody.scrollTop = chatBody.scrollHeight;
        // Update read receipts for my own messages
        updateReadReceipts(data.messages);
      }
    } catch (e) { /* network blip, ignore */ }
  }, 2000);

  /* ── Typing indicator polling (every 2 s) ─── */
  setInterval(async () => {
    try {
      const res  = await fetch(TYPING_STAT_URL);
      const data = await res.json();
      if (typingBubble) {
        typingBubble.style.display = data.typing ? 'flex' : 'none';
        if (data.typing) chatBody.scrollTop = chatBody.scrollHeight;
      }
    } catch (e) {}
  }, 2000);

  /* ── Typing ping on keypress ─── */
  if (msgInput) {
    msgInput.addEventListener('input', () => {
      clearTimeout(typingTimer);
      sendTypingPing();
      // Stop pinging after 4 s of silence
      typingTimer = setTimeout(() => {}, 4000);
    });
  }

  /* ── Emoji picker ─── */
  window.showEmojiPicker = function (msgId, btn) {
    if (activeMsgId === msgId && emojiPopup.style.display !== 'none') {
      emojiPopup.style.display = 'none';
      activeMsgId = null;
      return;
    }
    activeMsgId = msgId;
    const rect = btn.getBoundingClientRect();
    const panelRect = document.querySelector('.chat-panel').getBoundingClientRect();
    emojiPopup.style.display = 'flex';
    emojiPopup.style.top  = (rect.top  - panelRect.top  - emojiPopup.offsetHeight - 8) + 'px';
    emojiPopup.style.left = (rect.left - panelRect.left - 20) + 'px';
  };

  window.sendReaction = async function (emoji) {
    if (!activeMsgId) return;
    emojiPopup.style.display = 'none';
    try {
      const res  = await fetch(`${REACT_BASE_URL}${activeMsgId}/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CSRF_TOKEN },
        body: JSON.stringify({ emoji })
      });
      const data = await res.json();
      if (data.reactions !== undefined) {
        renderReactions(activeMsgId, data.reactions);
      }
    } catch (e) {}
    activeMsgId = null;
  };

  // Close emoji picker on outside click
  document.addEventListener('click', e => {
    if (emojiPopup && !emojiPopup.contains(e.target) && !e.target.classList.contains('react-trigger')) {
      emojiPopup.style.display = 'none';
      activeMsgId = null;
    }
  });
}

/* ── Helpers ──────────────────────────────────────────────────────────── */

function getLastMsgId() {
  const msgs = document.querySelectorAll('[data-msg-id]');
  let max = 0;
  msgs.forEach(el => {
    const id = parseInt(el.dataset.msgId, 10);
    if (id > max) max = id;
  });
  return max;
}

function appendOrUpdateMessage(msg) {
  const existing = document.getElementById(`msg-${msg.id}`);
  if (existing) {
    // Update read receipt only
    const receipt = existing.querySelector('.read-receipt');
    if (receipt && msg.sender === ME_ID) {
      receipt.textContent = msg.is_read ? '✓✓' : '✓';
      if (msg.is_read) receipt.classList.add('seen');
    }
    renderReactions(msg.id, msg.reactions || []);
    return;
  }

  const chatBody = document.getElementById('chatBody');
  const typingBubble = document.getElementById('typingBubble');
  const isMine = msg.sender === ME_ID;

  const div = document.createElement('div');
  div.className = `msg ${isMine ? 'msg-mine' : 'msg-theirs'}`;
  div.id = `msg-${msg.id}`;
  div.dataset.msgId = msg.id;
  div.innerHTML = `
    <div class="msg-body-text">${escHtml(msg.body)}</div>
    <div class="msg-footer">
      <span class="msg-time">${msg.time}</span>
      ${isMine ? `<span class="read-receipt" id="receipt-${msg.id}">${msg.is_read ? '✓✓' : '✓'}</span>` : ''}
    </div>
    <div class="msg-reactions" id="reactions-${msg.id}"></div>
    <button class="react-trigger" onclick="showEmojiPicker(${msg.id}, this)" title="React">＋</button>
  `;
  chatBody.insertBefore(div, typingBubble || null);
  if (msg.reactions && msg.reactions.length) renderReactions(msg.id, msg.reactions);
}

function updateReadReceipts(messages) {
  messages.forEach(msg => {
    if (msg.sender === ME_ID && msg.is_read) {
      const el = document.getElementById(`receipt-${msg.id}`);
      if (el) { el.textContent = '✓✓'; el.classList.add('seen'); }
    }
  });
}

function renderReactions(msgId, reactions) {
  const container = document.getElementById(`reactions-${msgId}`);
  if (!container) return;
  // Group by emoji
  const counts = {};
  reactions.forEach(r => {
    counts[r.emoji] = counts[r.emoji] || { count: 0, mine: false };
    counts[r.emoji].count++;
    if (r.user_id === ME_ID) counts[r.emoji].mine = true;
  });
  container.innerHTML = Object.entries(counts).map(([emoji, info]) =>
    `<span class="reaction-pill${info.mine ? ' mine' : ''}" data-emoji="${emoji}">${emoji}${info.count > 1 ? ` ${info.count}` : ''}</span>`
  ).join('');
}

async function sendTypingPing() {
  try {
    await fetch(TYPING_PING_URL, {
      method: 'POST',
      headers: { 'X-CSRFToken': CSRF_TOKEN }
    });
  } catch (e) {}
}

function escHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

/* ── Global notification polling (injected from base template) ─────────
   Runs on every page. Shows browser notifications + updates unread badges.  */
window.initNotificationPoll = function (pollUrl, csrfToken) {
  // Request browser notification permission once
  if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission();
  }

  setInterval(async () => {
    try {
      const res  = await fetch(pollUrl);
      const data = await res.json();

      // Update page title with unread count
      const base = 'DateMe';
      document.title = data.unread > 0 ? `(${data.unread}) ${base}` : base;

      // New match browser notifications
      if (data.new_matches && data.new_matches.length > 0) {
        data.new_matches.forEach(m => {
          showToast(`💕 New match with ${m.username}!`, `/match/matches/${m.user_id}/`);
          if (Notification.permission === 'granted') {
            new Notification('New match on DateMe!', {
              body: `You matched with ${m.username} 💕`,
              icon: '/static/favicon.ico',
              tag: `match-${m.user_id}`,
            });
          }
        });
      }

      // Unread badge in nav (if element exists)
      const navBadge = document.getElementById('navUnreadBadge');
      if (navBadge) {
        navBadge.textContent = data.unread || '';
        navBadge.style.display = data.unread > 0 ? 'inline' : 'none';
      }
    } catch (e) {}
  }, 5000);
};

function showToast(text, link) {
  const toast = document.createElement('div');
  toast.className = 'dateme-toast';
  toast.innerHTML = `<a href="${link}" style="color:inherit;text-decoration:none">${text}</a>
    <button onclick="this.parentElement.remove()" class="toast-close">×</button>`;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 6000);
}

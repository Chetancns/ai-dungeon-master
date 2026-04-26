const API_BASE  = 'http://localhost:8000';
const gameId   = localStorage.getItem('game_id');
const playerId = localStorage.getItem('player_id');

if (!gameId || !playerId) {
  window.location.href = 'index.html';
}

let knownLogLength = 0;
let pollInterval   = null;
let isSubmitting   = false;

const classEmoji = { Warrior:'⚔️', Mage:'🔮', Rogue:'🗡️', Ranger:'🏹', Cleric:'✨' };

// ── Toast notification ─────────────────────────────────────
function showToast(message, type = 'error') {
  let toast = document.getElementById('game-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'game-toast';
    toast.style.cssText = `
      position:fixed;bottom:24px;left:50%;transform:translateX(-50%);
      z-index:1000;padding:12px 20px;border-radius:8px;font-size:0.9rem;
      max-width:90vw;text-align:center;pointer-events:none;
    `;
    document.body.appendChild(toast);
  }
  toast.className = `alert alert-${type}`;
  toast.textContent = message;
  toast.style.display = 'block';
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => { toast.style.display = 'none'; }, 4000);
}


const storyParchment = document.getElementById('story-parchment');
const storyPanel     = document.getElementById('story-log-panel');
const actionInput    = document.getElementById('action-input');
const actionBtn      = document.getElementById('action-btn');

// ── Ctrl+Enter shortcut ────────────────────────────────────
actionInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
    e.preventDefault();
    if (!actionBtn.disabled) submitAction();
  }
});

// ── Render a single story event ────────────────────────────
function renderEvent(event) {
  const div = document.createElement('div');
  div.className = `story-event ${event.role}`;

  const header = event.role === 'dm'
    ? '🎲 Dungeon Master'
    : `🧙 ${event.player_name}`;

  const ts = new Date(event.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  div.innerHTML = `
    <div class="story-event-header">${header} <span class="text-muted" style="font-weight:300;font-size:0.75rem;">${ts}</span></div>
    <div class="story-event-content">${escapeHtml(event.content).replace(/\n/g, '<br>')}</div>
  `;
  return div;
}

function escapeHtml(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function scrollToBottom() {
  storyPanel.scrollTop = storyPanel.scrollHeight;
}

// ── Sidebar ────────────────────────────────────────────────
function renderSidebar(players) {
  const container = document.getElementById('sidebar-players');
  container.innerHTML = players.map(p => `
    <div class="sidebar-player">
      <strong>${classEmoji[p.character_class] || '🎲'} ${p.character_name}</strong>
      <small>${p.player_name} · ${p.character_class}</small>
    </div>
  `).join('');
}

// ── Thinking indicator ─────────────────────────────────────
function showThinking() {
  const div = document.createElement('div');
  div.id = 'thinking-indicator';
  div.className = 'thinking-msg';
  div.innerHTML = '<span class="spinner"></span> 🎲 The DM is thinking…';
  storyParchment.appendChild(div);
  scrollToBottom();
}

function hideThinking() {
  const el = document.getElementById('thinking-indicator');
  if (el) el.remove();
}

// ── Main poll ──────────────────────────────────────────────
async function poll() {
  try {
    const res  = await fetch(`${API_BASE}/api/game/${gameId}`);
    const data = await res.json();
    if (!res.ok) return;

    // Update top bar
    document.getElementById('tb-style').textContent  = data.game_style;
    document.getElementById('tb-game-id').textContent = data.game_id;
    renderSidebar(data.players);

    // Append only NEW story events
    if (data.story_log.length > knownLogLength) {
      // Remove placeholder on first event
      const placeholder = document.getElementById('story-placeholder');
      if (placeholder) placeholder.remove();

      hideThinking();

      const newEvents = data.story_log.slice(knownLogLength);
      newEvents.forEach(ev => {
        storyParchment.appendChild(renderEvent(ev));
      });
      knownLogLength = data.story_log.length;
      scrollToBottom();

      // Re-enable input after DM responds (last event must be dm)
      const lastEvent = data.story_log[data.story_log.length - 1];
      if (lastEvent && lastEvent.role === 'dm' && isSubmitting) {
        setInputEnabled(true);
        isSubmitting = false;
      }
    }

    // Enable input on first load (game in_progress, DM has spoken at least once)
    if (!isSubmitting && data.status === 'in_progress' && data.story_log.length > 0) {
      const lastEvent = data.story_log[data.story_log.length - 1];
      if (lastEvent.role === 'dm') {
        setInputEnabled(true);
      }
    }

  } catch (err) {
    console.error('Poll error:', err);
  }
}

function setInputEnabled(enabled) {
  actionInput.disabled = !enabled;
  actionBtn.disabled   = !enabled;
  if (enabled) actionInput.focus();
}

// ── Submit Action ──────────────────────────────────────────
async function submitAction() {
  const action = actionInput.value.trim();
  if (!action) return;

  isSubmitting = true;
  setInputEnabled(false);
  actionInput.value = '';
  showThinking();

  try {
    const res  = await fetch(`${API_BASE}/api/action/${gameId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_id: playerId, action }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Action failed');

    hideThinking();

    // Render any new events returned directly (avoids waiting for next poll)
    const newEvents = data.story_log.slice(knownLogLength);
    const placeholder = document.getElementById('story-placeholder');
    if (placeholder) placeholder.remove();

    newEvents.forEach(ev => storyParchment.appendChild(renderEvent(ev)));
    knownLogLength = data.story_log.length;
    scrollToBottom();

    isSubmitting = false;
    setInputEnabled(true);

  } catch (err) {
    hideThinking();
    isSubmitting = false;
    setInputEnabled(true);
    showToast('Error: ' + err.message);
  }
}

// ── Leave Game ─────────────────────────────────────────────
async function leaveGame() {
  if (!confirm('Leave the game?')) return;
  try {
    await fetch(`${API_BASE}/api/game/${gameId}/leave`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_id: playerId }),
    });
  } catch (_) {}
  localStorage.removeItem('game_id');
  localStorage.removeItem('player_id');
  localStorage.removeItem('player_name');
  window.location.href = 'index.html';
}

// ── Bootstrap ──────────────────────────────────────────────
poll();
pollInterval = setInterval(poll, 2000);

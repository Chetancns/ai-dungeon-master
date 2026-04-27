const API_BASE   = 'http://localhost:8000';
const gameId    = localStorage.getItem('game_id');
const playerId  = localStorage.getItem('player_id_' + gameId);

if (!gameId || !playerId) {
  window.location.href = 'index.html';
}

let pollInterval = null;
let lastPlayerCount = 0;

document.getElementById('game-id-display').textContent = gameId;

function showAlert(message, type = 'error') {
  document.getElementById('lobby-alert').innerHTML =
    `<div class="alert alert-${type}">${message}</div>`;
}

function copyGameId() {
  navigator.clipboard.writeText(gameId).then(() => {
    const btn = document.getElementById('copy-btn');
    btn.textContent = '✅ Copied!';
    setTimeout(() => { btn.textContent = '📋 Copy ID'; }, 2000);
  });
}

function renderPlayers(players) {
  const container = document.getElementById('player-list');
  const classEmoji = { Warrior:'⚔️', Mage:'🔮', Rogue:'🗡️', Ranger:'🏹', Cleric:'✨' };
  container.innerHTML = players.map((p, i) => `
    <div class="player-list-item">
      <div class="player-avatar">${classEmoji[p.character_class] || '🎲'}</div>
      <div class="player-info">
        <strong>${p.character_name}</strong> ${i === 0 ? '<span class="badge" style="font-size:0.65rem;">Creator</span>' : ''}
        <small>${p.player_name} · ${p.character_class}</small>
      </div>
    </div>
  `).join('');
}

async function poll() {
  try {
    const res  = await fetch(`${API_BASE}/api/game/${gameId}`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Error fetching game');

    // If game started, move to game screen
    if (data.status === 'in_progress') {
      clearInterval(pollInterval);
      window.location.href = 'game.html';
      return;
    }

    // Update info
    document.getElementById('style-badge').textContent      = data.game_style;
    document.getElementById('player-count-info').textContent = `${data.players.length} / ${data.max_players} players`;

    renderPlayers(data.players);

    // Waiting message
    const waitMsg = document.getElementById('waiting-msg');
    waitMsg.style.display = data.players.length < data.max_players ? 'block' : 'none';

    // Start button — only creator can click
    const startBtn  = document.getElementById('start-btn');
    const startHint = document.getElementById('start-hint');
    const isCreator = data.players.length > 0 && data.players[0].player_id === playerId;

    if (isCreator) {
      startBtn.disabled = false;
      startHint.textContent = 'You are the creator — start when ready!';
    } else {
      startBtn.disabled = true;
      const creatorName = data.players[0]?.player_name || 'the creator';
      startHint.textContent = `Waiting for ${creatorName} to start the game…`;
    }

  } catch (err) {
    showAlert(err.message);
  }
}

async function startGame() {
  const btn = document.getElementById('start-btn');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Starting…';

  try {
    const res  = await fetch(`${API_BASE}/api/game/${gameId}/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_id: playerId }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Failed to start game');

    clearInterval(pollInterval);
    window.location.href = 'game.html';
  } catch (err) {
    showAlert(err.message);
    btn.disabled = false;
    btn.textContent = '⚔️ Start Adventure';
  }
}

// Initial poll + polling every 2 s
poll();
pollInterval = setInterval(poll, 2000);

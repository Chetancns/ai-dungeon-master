const API_BASE = 'http://localhost:8000';

function showAlert(containerId, message, type = 'error') {
  const el = document.getElementById(containerId);
  el.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
}

// ── Create Game ────────────────────────────────────────────
document.getElementById('create-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const btn = e.target.querySelector('button[type="submit"]');
  btn.disabled = true;
  btn.textContent = 'Creating…';

  const body = {
    creator_name:    document.getElementById('c-player-name').value.trim(),
    character_name:  document.getElementById('c-char-name').value.trim(),
    character_class: document.getElementById('c-char-class').value,
    game_style:      document.getElementById('c-game-style').value,
    max_players:     parseInt(document.getElementById('c-max-players').value),
  };

  try {
    const res = await fetch(`${API_BASE}/api/game/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Failed to create game');

    localStorage.setItem('game_id',   data.game_id);
    localStorage.setItem('player_id', data.player_id);
    localStorage.setItem('player_name', body.creator_name);
    window.location.href = 'lobby.html';
  } catch (err) {
    showAlert('create-alert', err.message);
    btn.disabled = false;
    btn.textContent = 'Create Game';
  }
});

// ── Join Game ──────────────────────────────────────────────
document.getElementById('join-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const btn = e.target.querySelector('button[type="submit"]');
  btn.disabled = true;
  btn.textContent = 'Joining…';

  const gameId = document.getElementById('j-game-id').value.trim().toUpperCase();
  const body = {
    player_name:     document.getElementById('j-player-name').value.trim(),
    character_name:  document.getElementById('j-char-name').value.trim(),
    character_class: document.getElementById('j-char-class').value,
  };

  try {
    const res = await fetch(`${API_BASE}/api/game/join/${gameId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Failed to join game');

    localStorage.setItem('game_id',   gameId);
    localStorage.setItem('player_id', data.player_id);
    localStorage.setItem('player_name', body.player_name);
    window.location.href = 'lobby.html';
  } catch (err) {
    showAlert('join-alert', err.message);
    btn.disabled = false;
    btn.textContent = 'Join Game';
  }
});

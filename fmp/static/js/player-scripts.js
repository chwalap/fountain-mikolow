function updateDetails(playlistId) {
  selectedItemId = playlistId;

  hideDetails();

  if (!validIdRange(selectedItemId)) {
    createNotification('warning', 'Najpierw wybierz playlistę.');
    return;
  }

  showDetails(selectedItemId);
}

function hideDetails() {
  document.getElementById('playlist-title').classList.add('hidden');
  document.getElementById('playlist').innerHTML = '';
}

function showDetails(playlistId) {
  document.getElementById('playlist-title').classList.remove('hidden');
  document.getElementById('playlist-title').textContent = `${selectable_list_entries[playlistId].name}`;

  if (selectable_list_entries[playlistId].tracks.length > 0) {
    document.getElementById('no-tracks-message').classList.add('hidden');
  } else {
    document.getElementById('no-tracks-message').classList.remove('hidden');
  }

  const playlistDiv = document.getElementById('playlist');
  selectable_list_entries[playlistId].tracks.forEach(s => {
    const li = document.createElement('li');
    li.innerHTML = `
      <div class="track-container" id="${s.id}">
        <div class="track-name">${s.name}</div>
        <div class="track-duration">${format_time(s.duration)}</div>
      </div>
    `;
    playlistDiv.appendChild(li);
  });
}

document.addEventListener('DOMContentLoaded', () => {
  selectCallback = updateDetails;
});

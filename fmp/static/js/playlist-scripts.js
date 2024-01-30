/*
todo:
- refactor code
- does it even make sense to have a save button? any change should be saved asap
- add possibility to change the playlist's name
- ask to save on tab change
*/

function askToSave(playlistId) {
  if (isSaveRequired(playlistId)) {
    showMessage(
      `Czy chcesz zapisać zmiany w playliście ${selectable_list_entries[playlistId].name}?`,
      ["Tak", "Nie"],
      () => savePlaylist(playlistId),
      () => requireSaving(playlistId, false)
    );
  }
}

function updateDetails(playlistId) {
  if (selectedItemId != playlistId) {
    askToSave(selectedItemId);
  }

  selectedItemId = playlistId;

  hideDetails();

  if (!validIdRange(selectedItemId)) {
    createNotification('warning', 'Najpierw wybierz playlistę.');
    return;
  }

  showDetails(selectedItemId);

  hiddenTracks = selectable_list_entries[selectedItemId].tracks;
  filter_tracks();
}

function hideDetails() {
  document.getElementById('delete-playlist').classList.add('hidden');
  document.getElementById('save-playlist').classList.add('hidden');
  document.getElementById('playlist-details').innerHTML = '';
  document.getElementById('playlist-name').textContent = '';
}

function showDetails(playlistId) {
  document.getElementById('playlist-name').textContent = `${selectable_list_entries[playlistId].name}`;
  document.getElementById('delete-playlist').classList.remove('hidden');
  document.getElementById('save-playlist').classList.remove('hidden');

  const playlistDetailsDiv = document.getElementById('playlist-details');
  selectable_list_entries[playlistId].tracks.forEach(s => {
    const li = document.createElement('li');
    li.innerHTML = `
      <div class="track-item" onClick="removeFromPlaylist(${s.id})">
        <span class="track-name">${s.name}</span>
        <span class="track-arrow left-arrow">
          <i class="fas fa-arrow-left"></i>
        </span>
      </div>
    `;
    playlistDetailsDiv.appendChild(li);
  });
}

function savePlaylist(playlistId) {
  if (!isSaveRequired(playlistId)) {
    createNotification('info', 'Brak zmian do zapisania.');
    return;
  }

  if (!validIdRange(playlistId)) {
    createNotification('warning', 'Najpierw wybierz playlistę.');
    return;
  }

  const playlistData = {
    id: selectable_list_entries[playlistId].id,
    name: selectedItemId >= 0 ? selectable_list_entries[playlistId].name : '',
    tracks: selectedItemId >= 0 ? selectable_list_entries[playlistId].tracks.map(track => track.id) : []
  };

  fetch('/playlist/update', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(playlistData)
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Błąd serwera!');
    }
    return response.json();
  })
  .then(data => {
    if (data.status === 'success') {

      if (playlistData.id === -1) {
        const newPlaylistId = data.playlist_id;
        selectable_list_entries[playlistId].id = newPlaylistId;
      }

      playlistName = selectable_list_entries[playlistId].name;

      requireSaving(playlistId, false);
      callSelectCallback(playlistId);
      createNotification('success', `Playlista ${playlistName} została zapisana.`);
    } else {
      createNotification('error', 'Błąd podczas zapisywania playlisty!');
    }
  })
  .catch(error => {
    createNotification('error', `Błąd podczas zapisywania playlisty: ${error}!`);
  });
}

function removePlaylist() {
  if (!validIdRange(selectedItemId)) {
    createNotification('warning', 'Najpierw wybierz playlistę.');
    return;
  }

  const playlistToDelete = selectable_list_entries[selectedItemId];
  if (playlistToDelete.id === -1) {
    createNotification('warning', 'Playlista nie została zapisana.');
    return;
  }

  showMessage(
    `Czy na pewno chcesz usunąć playlistę ${playlistToDelete.name}?`,
    ["Tak", "Nie"],
    () => {
      fetch('/playlist/remove', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ id: playlistToDelete.id })
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('Błąd serwera!');
        }
        return response.json();
      })
      .then(data => {
        if (data.status === 'success') {
          playlistName = selectable_list_entries[selectedItemId].name;

          selectable_list_entries.splice(selectedItemId, 1);

          if (selectable_list_entries.length == 0) {
            selectedItemId = -1;
            showNoEntriesMessage(true);
          } else if (selectedItemId >= selectable_list_entries.length) {
            selectedItemId -= 1;
          }

          selectedPlaylist = document.querySelector('.selected-list-item');
          if (selectedPlaylist) {
            selectedPlaylist.remove();
          }

          hiddenTracks = [];
          filter_tracks();

          callSelectCallback(selectedItemId);
          createNotification('removed', `Playlista ${playlistName} została usunięta.`);
        } else {
          createNotification('error', 'Błąd podczas usuwania playlisty!');
        }
      })
      .catch(error => {
        createNotification('error', `Błąd podczas usuwania playlisty: ${error}!`);
      });
    },
    () => {
      callSelectCallback(selectedItemId);
    }
  );
}

function removeFromPlaylist(trackId) {
  if (!validIdRange(selectedItemId)) {
    createNotification('warning', 'Najpierw wybierz playlistę.');
    return;
  }

  if (!selectable_list_entries[selectedItemId].tracks.some(s => s.id === trackId)) {
    createNotification('warning', 'Ta piosenka nie jest częścią tej playlisty.');
    return;
  }

  selectable_list_entries[selectedItemId].tracks = selectable_list_entries[selectedItemId].tracks.filter(s => s.id !== trackId);
  requireSaving(selectedItemId, true);
  callSelectCallback(selectedItemId);
}

function addToPlaylist(trackId) {
  if (!validIdRange(selectedItemId)) {
    createNotification('warning', 'Najpierw wybierz playlistę.');
    return;
  }

  if (selectable_list_entries[selectedItemId].tracks.some(s => s.id === trackId)) {
    createNotification('warning', 'Ta piosenka już jest częścią tej playlisty.');
    return;
  }

  trackName = tracks.find(s => s.id === trackId).name;
  selectable_list_entries[selectedItemId].tracks.push({ id: trackId, name: trackName });

  requireSaving(selectedItemId, true);
  callSelectCallback(selectedItemId);
}

function createNewItem(name) {
  return { id: -1, name: name, tracks: [], requireSaving: true};
}

document.addEventListener('DOMContentLoaded', () => {
  createNewItemCallback = createNewItem;
  selectCallback = updateDetails;
  saveCallback = savePlaylist;

  addClickHandlersToTracks("addToPlaylist");
});

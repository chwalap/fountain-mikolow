/*
todo:
 - set date to '' when time changed to daily
*/

function askToSave(scheduleId) {
  if (isSaveRequired(scheduleId)) {
    showMessage(
      `Czy chcesz zapisać zmiany w harmonogramie ${selectable_list_entries[scheduleId].name}?`,
      ["Tak", "Nie"],
      () => saveSchedule(scheduleId),
      () => requireSaving(scheduleId, false)
    );
  }
}

function updateDetails(scheduleId) {
  if (selectedItemId != scheduleId) {
    askToSave(selectedItemId);
  }

  selectedItemId = scheduleId;

  hideDetails();

  if (!validIdRange(selectedItemId)) {
    createNotification('warning', 'Najpierw wybierz harmonogram.');
    return;
  }

  showDetails(selectedItemId);

  hiddenTracks = [{id: selectable_list_entries[selectedItemId].track_id}];
  filter_tracks();
}

function hideDetails() {
  document.getElementById('schedule-name').textContent = '';
  document.getElementById('delete-schedule').classList.add('hidden');
  document.getElementById('save-schedule').classList.add('hidden');

  var inputs = document.querySelectorAll('.input-group');
  for (var i = 0; i < inputs.length; ++i) {
    inputs[i].style.display = '';
  }
}

function showDetails(scheduleId) {
  const scheduleNameDiv = document.getElementById('schedule-name');
  const removeScheduleButton = document.getElementById('delete-schedule');
  const saveScheduleButton = document.getElementById('save-schedule');
  const scheduleTypeInput = document.getElementById('schedule-type');
  const scheduleTimeInput = document.getElementById('schedule-time');
  const scheduleDateInput = document.getElementById('schedule-date');
  const trackNameInput = document.getElementById('track-name');

  scheduleNameDiv.textContent = `${selectable_list_entries[scheduleId].name}`;
  removeScheduleButton.classList.remove('hidden');
  saveScheduleButton.classList.remove('hidden');

  var inputs = document.querySelectorAll('.input-group');
  for (var i = 0; i < inputs.length; ++i) {
    inputs[i].style.display = 'grid';
  }

  scheduleDateInput.parentNode.parentNode.style.display = selectable_list_entries[selectedItemId].type === 'yearly' ? 'grid' : 'none';

  scheduleTypeInput.value = `${selectable_list_entries[scheduleId].type}`;
  scheduleTimeInput.value = `${selectable_list_entries[scheduleId].time}`;
  scheduleDateInput.value = `${selectable_list_entries[scheduleId].date}`;
  let trackId = selectable_list_entries[selectedItemId].track_id;
  trackNameInput.value = trackId != -1 ? `${tracks.find(s => s.id === trackId).name}` : '';
}

function saveSchedule(scheduleId) {
  if (!isSaveRequired(scheduleId)) {
    createNotification('info', 'Brak zmian do zapisania.');
    return;
  }

  if (!validIdRange(scheduleId)) {
    createNotification('warning', 'Najpierw wybierz harmonogram.');
    return;
  }

  const scheduleData = {
    id: selectable_list_entries[scheduleId].id,
    name: selectedItemId >= 0 ? selectable_list_entries[scheduleId].name : '',
    type: selectedItemId >= 0 ? selectable_list_entries[scheduleId].type : '',
    time: selectedItemId >= 0 ? selectable_list_entries[scheduleId].time : '',
    date: selectedItemId >= 0 ? selectable_list_entries[scheduleId].date : '',
    track_id: selectedItemId >= 0 ? selectable_list_entries[scheduleId].track_id : -1
  };

  console.log(scheduleData);

  fetch('/schedule/update', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(scheduleData)
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Błąd serwera!');
    }
    return response.json();
  })
  .then(data => {
    if (data.status === 'success') {

      if (scheduleData.id === -1) {
        const newScheduleId = data.schedule_id;
        selectable_list_entries[scheduleId].id = newScheduleId;
      }

      scheduleName = selectable_list_entries[scheduleId].name;

      requireSaving(scheduleId, false);
      callSelectCallback(scheduleId);
      createNotification('success', `Harmonogram ${scheduleName} został zapisany.`);
    } else {
      createNotification('error', 'Błąd podczas zapisywania harmonogramu!');
    }
  })
  .catch(error => {
    createNotification('error', `Błąd podczas zapisywania harmonogramu: ${error}!`);
  });
}

function removeSchedule(scheduleId) {
  if (!validIdRange(selectedItemId)) {
    createNotification('warning', 'Najpierw wybierz playlistę.');
    return;
  }

  const scheduleToDelete = selectable_list_entries[selectedItemId];
  if (scheduleToDelete.id === -1) {
    createNotification('warning', 'Harmonogram nie został zapisany.');
    return;
  }

  showMessage(
    `Czy na pewno chcesz usunąć harmonogram ${scheduleToDelete.name}?`,
    ["Tak", "Nie"],
    () => {
      fetch('/schedule/remove', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ id: scheduleToDelete.id })
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('Błąd serwera!');
        }
        return response.json();
      })
      .then(data => {
        if (data.status === 'success') {
          scheduleName = selectable_list_entries[selectedItemId].name;

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
          createNotification('removed', `Harmonogram ${scheduleName} został usunięty.`);
        } else {
          createNotification('error', 'Błąd podczas usuwania harmonogramu!');
        }
      })
      .catch(error => {
        createNotification('error', `Błąd podczas usuwania harmonogramu: ${error}!`);
      });
    },
    () => {
      callSelectCallback(selectedItemId);
    }
  );
}

function assignToSchedule(trackId) {
  if (!validIdRange(selectedItemId)) {
    createNotification('warning', 'Najpierw wybierz harmonogram.');
    return;
  }

  if (selectable_list_entries[selectedItemId].track_id && selectable_list_entries[selectedItemId].track_id == trackId) {
    createNotification('warning', 'Ta piosenka jest już przypisana do tego harmonogramu.');
    return;
  }

  selectable_list_entries[selectedItemId].track_id = trackId;

  requireSaving(selectedItemId, true);
  callSelectCallback(selectedItemId);
}

function createNewItem(name) {
  return {
    id: -1,
    name: name,
    type: 'daily',
    time: '',
    date: '',
    track_id: -1,
    requireSaving: true
  };
}

function toggleScheduleInputs() {
  var scheduleType = document.getElementById('schedule-type').value;
  var scheduleDateGroup = document.querySelector('.input-group #schedule-date').parentNode.parentNode;

  if (scheduleType === 'yearly') {
    scheduleDateGroup.style.display = 'grid';
  } else {
    scheduleDateGroup.style.display = '';
  }

  selectable_list_entries[selectedItemId].type = scheduleType;
  requireSaving(selectedItemId, true);
}

function updateScheduleTime() {
  selectable_list_entries[selectedItemId].time = document.getElementById('schedule-time').value;
  requireSaving(selectedItemId, true);
}


function updateScheduleDate() {
  selectable_list_entries[selectedItemId].date = document.getElementById('schedule-date').value;
  requireSaving(selectedItemId, true);
}

document.addEventListener('DOMContentLoaded', () => {
  createNewItemCallback = createNewItem;
  selectCallback = updateDetails;
  saveCallback = saveSchedule;

  document.getElementById('schedule-type').addEventListener('change', toggleScheduleInputs);
  document.getElementById('schedule-time').addEventListener('change', updateScheduleTime);
  document.getElementById('schedule-date').addEventListener('change', updateScheduleDate);

  addClickHandlersToTracks("assignToSchedule");
});

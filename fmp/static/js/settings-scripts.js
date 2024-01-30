function saveSettings() {

  const audioOutput = document.getElementById('audio-output');
  const playerAlwaysOnTop = document.getElementById('player-always-on-top');
  const fromTime = document.getElementById('from-time');
  const toTime = document.getElementById('to-time');

  var settings_data = {
    'audio_output': audioOutput.value,
    'player_always_on_top': playerAlwaysOnTop.checked ? 'on' : 'off',
    'working_from': fromTime.value,
    'working_to': toTime.value
  };

  fetch('/settings/save', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(settings_data)
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Błąd serwera!');
    }
    return response.json();
  })
  .then(data => {
    if (data.status === 'success') {
      createNotification('info', 'Ustawienia zapisane.');
    } else {
      createNotification('error', 'Błąd podczas zapisywania ustawień!');
    }
  })
  .catch(error => {
    createNotification('error', `Błąd podczas zapisywania ustawień: ${error}!`);
  });

  const footer = document.getElementById('footer-controls');
  if (playerAlwaysOnTop.checked) {
    footer.classList.remove('hidden');
    // setTimeout(() => { footer.style.display = 'none'; }, 1000);
  } else {
    footer.classList.add('hidden');
    // footer.style.display = 'flex';
    // setTimeout(() => { footer.classList.remove('hidden'); }, 1000);
  }
}

function savePassword() {
  const newPassword = document.getElementById('new-password').value;
  if (newPassword.value == "") {
    createNotification('error', 'Hasło nie może być puste!');
    return;
  }

  showMessage(
    `Jesteś pewny że chcesz zmienić hasło?`,
    ["Tak", "Nie"],
    () => {
      fetch('/settings/change-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({'new_password': newPassword})
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('Błąd serwera!');
        }
        return response.json();
      })
      .then(data => {
        if (data.status === 'success') {
          createNotification('info', 'Hasło zostało zmienione.');
        } else {
          createNotification('error', 'Błąd podczas zmiany hasła!');
        }
      })
      .catch(error => {
        createNotification('error', `Błąd podczas zmiany hasła: ${error}!`);
      });
    },
    () => createNotification('removed', 'Hasło nie zostało zmienione.')
  );
}

function refreshTracks() {
  fetch('/settings/refresh-track-list', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: ''
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Błąd serwera!');
    }
    return response.json();
  })
  .then(data => {
    if (data.status === 'success') {
      createNotification('info', 'Lista utworów została odświeżona.');
    } else {
      createNotification('error', 'Błąd podczas odświeżania listy utworów!');
    }
  })
  .catch(error => {
    createNotification('error', `Błąd podczas odświeżania listy utworów: ${error}!`);
  });
}

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('audio-output').addEventListener('change', saveSettings);
  document.getElementById('player-always-on-top').addEventListener('change', saveSettings);
  document.getElementById('from-time').addEventListener('change', saveSettings);
  document.getElementById('to-time').addEventListener('change', saveSettings);
  document.getElementById('reload-tracks').addEventListener('click', refreshTracks);
  document.getElementById('save-password').addEventListener('click', savePassword);
});

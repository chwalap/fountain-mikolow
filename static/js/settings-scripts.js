function saveSettings() {
  const audioOutput = document.getElementById('audio-output');
  const alwaysShowPlayer = document.getElementById('always-show-player');
  const fromTime = document.getElementById('from-time');
  const toTime = document.getElementById('to-time');

  var settings_data = {
    'audio_output': audioOutput.value,
    'player_always_on_top': alwaysShowPlayer.value,
    'working_from': fromTime.value,
    'working_to': toTime.value
  };

  fetch('/save-settings', {
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
}


document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('audio-output').addEventListener('change', saveSettings);
  document.getElementById('always-show-player').addEventListener('change', saveSettings);
  document.getElementById('from-time').addEventListener('change', saveSettings);
  document.getElementById('to-time').addEventListener('change', saveSettings);
});

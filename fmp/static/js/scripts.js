let secondAccumulator = 0;
let lastUpdateTime = 0;
let updateId = 0;

let yesCallback = null;
let noCallback = null;

function format_time(secs) {
  let hours = Math.floor(secs / 3600);
  let minutes = Math.floor((secs % 3600) / 60);
  let seconds = secs % 60;

  let formattedTime = hours > 0
    ? `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
    : `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;

  return formattedTime;
}

function updateProgressBar(percentage) {
  const progressBar = document.getElementById('progress-bar');
  progressBar.style.width = `${percentage}%`;
}

function updateProgressTime(progress, duration) {
  const progressTime = document.getElementById('progress-time');
  progressTime.dataset.progress = progress;
  progressTime.innerText = `${format_time(progress)} / ${format_time(duration)}`
}

function updateTrackProgress() {
  const progressTime = document.getElementById('progress-time');
  let trackProgress = parseInt(progressTime.dataset.progress);
  let trackDuration = parseInt(progressTime.dataset.duration);

  let tm = Date.now();
  let dt = tm - lastUpdateTime;
  lastUpdateTime = tm;

  secondAccumulator += dt;
  const percentage = (((trackProgress * 1000) + secondAccumulator) / (trackDuration * 1000)) * 100;
  updateProgressBar(percentage);

  while (secondAccumulator >= 1000) {
    trackProgress += 1;
    secondAccumulator -= 1000;
  }

  updateProgressTime(trackProgress, trackDuration);
  updateId = setTimeout(updateTrackProgress, 100);
}

function showMessage(message, buttons = ['yes', 'no'], yesAction, noAction) {
  document.getElementById('messageText').innerText = message;
  const yesButton = document.getElementById('yesButton');
  const noButton = document.getElementById('noButton');

  yesButton.innerText = buttons[0];
  noButton.innerText = buttons[1];

  yesCallback = yesAction;
  noCallback = noAction;

  let messageBox = document.getElementById('messageBox');
  messageBox.style.display = 'flex';

  let messageBoxKeyHandler = (event) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      buttonClicked('yes');
      messageBox.removeEventListener('keydown', messageBoxKeyHandler);
    } else if (event.key === 'Escape') {
      event.preventDefault();
      buttonClicked('no');
      messageBox.removeEventListener('keydown', messageBoxKeyHandler);
    }
  };

  messageBox.focus();

  messageBox.addEventListener('keydown', messageBoxKeyHandler);
}

function buttonClicked(buttonValue) {
  document.getElementById('messageBox').style.display = 'none';

  if (buttonValue === 'yes' && typeof yesCallback === 'function') {
    yesCallback();
  } else if (buttonValue === 'no' && typeof noCallback === 'function') {
    noCallback();
  }
}

function createNotification(type, message, duration = 10000) {
  const notification = document.createElement('div');
  notification.classList.add('notification', type);
  notification.innerText = message;

  const container = document.getElementById('notification-container');
  container.appendChild(notification);

  notification.addEventListener('click', () => {
    notification.remove();
  });

  setTimeout(() => {
      if (notification.parentNode === container) {
          container.removeChild(notification);
      }
  }, duration);
}

function updateCurrentTrack(current_track) {
  document.getElementById('current-track-name').innerText = current_track['name'];
  updateProgressTime(0, current_track['duration']);
  updateProgressBar(0);
}

document.addEventListener("DOMContentLoaded", function() {
  var menuToggle = document.querySelector('.top-menu .menu-toggle');
  var menuList = document.querySelector('.top-menu ul');

  function toggleMenu() {
    menuList.classList.toggle('active');
  }

  menuToggle.addEventListener('click', function(event) {
    toggleMenu();
    event.stopPropagation();
  });

  document.addEventListener('click', function(event) {
    var isClickInsideMenu = menuList.contains(event.target) || menuToggle.contains(event.target);

    if (!isClickInsideMenu && menuList.classList.contains('active')) {
      toggleMenu();
    }
  });

  document.getElementById('prev-track').addEventListener('click', e => {
    fetch('/player/prev-track')
    .then(response => response.json())
    .then(data => {
      if (data.status === 'success') {
        updateCurrentTrack(data.current_track);
      } else {
        createNotification('error', 'Nie udało się zmienić utworu na poprzedni!')
      }
    });
  });

  document.getElementById('next-track').addEventListener('click', e => {
    fetch('/player/next-track')
    .then(response => response.json())
    .then(data => {
      if (data.status === 'success') {
        updateCurrentTrack(data.current_track);
      } else {
        createNotification('error', 'Nie udało się zmienić utworu na następny!')
      }
    });
  });

  document.getElementById('play-pause').addEventListener('click', e => {
    fetch('/player/toogle-play')
    .then(response => response.json())
    .then(data => {
      if (data.status === 'success') {
        if (data.is_music_playing) {
          lastUpdateTime = Date.now();
          updateTrackProgress();
          createNotification('info', 'Muzyka została wznowiona.');
        } else {
          clearTimeout(updateId);
          createNotification('info', 'Muzyka została zatrzymana.');
        }
      }
    });
  });

  document.getElementById('volumeSlider').addEventListener('change', e => {
    fetch('/player/change-volume', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({'volume': document.getElementById('volumeSlider').value})
    })
    .then(response => response.json())
    .then(data => {
      if (data.status !== 'success') {
        createNotification('error', data.message);
      }
    });
  })

  lastUpdateTime = Date.now();
  updateTrackProgress();
});

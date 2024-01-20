const trackDuration = 180;
let currentTime = 0;
const updateInterval = 100;

function updateProgressBar() {
  const progressBar = document.getElementById('progress-bar');
  currentTime += updateInterval;

  const percentage = (currentTime / (trackDuration * 1000)) * 100;
  progressBar.style.width = `${percentage}%`;

  if (currentTime < trackDuration * 1000) {
    setTimeout(updateProgressBar, updateInterval);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  updateProgressBar();
});

let yesCallback = null;
let noCallback = null;

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
});

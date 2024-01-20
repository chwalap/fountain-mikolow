let hiddenTracks = [];

function filter_tracks()
{
  const searchInput = document.getElementById('track-search');
  const query = searchInput.value.toLowerCase();
  const trackItems = document.querySelectorAll('#track-list .track-list-item');

  trackItems.forEach(item => {
    const trackName = item.querySelector('.track-name').textContent.toLowerCase();
    const trackId = item.id.split('-')[1];
    const hidden = !trackName.includes(query) || hiddenTracks.find(t => t.id == trackId);
    item.style.display = hidden ? 'none' : '';
  });
}

function addClickHandlersToTracks(handler) {
  const trackListItems = document.querySelectorAll('.track-list-item');

  trackListItems.forEach(item => {
      const trackId = item.id.split('-')[1];
      item.setAttribute('onclick', `${handler}(${trackId})`);
  });
}

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('track-search').addEventListener('input', () => {
    filter_tracks();
  });
});

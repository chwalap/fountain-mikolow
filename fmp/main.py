import time
import sounddevice as sd
import numpy as np

from pydub import AudioSegment

from fmp.audio import get_output_audio_devices
from fmp.tracks import update_tracks_database
from fmp.playlist import get_all_playlists_with_tracks
from fmp.settings import read_settings

# todo: add synchronisation
# todo: find better library for a music player

global playlists, current_track_id, current_track, current_playlist, is_music_playing, current_track_start_time, volume, is_track_paused, current_track_paused_at, current_track_changed
playlists = None
current_track_id = 0
current_track = None
current_playlist = None
is_music_playing = True
is_track_paused = False
current_track_changed = False
current_track_paused_at = 0
current_track_start_time = 0
volume = 50

def get_player_state():
  global playlists, current_track, current_track_start_time, volume
  track_name = ''
  track_length = 0
  track_progress = 0
  track_percentage = 0

  if current_track:
    track_name = current_track['name']
    track_length = current_track['duration']
    track_progress = int(time.time()) - current_track_start_time
    track_percentage = track_progress / track_length * 100

  return dict(
    current_track_name = track_name,
    current_track_length = track_length,
    current_track_progress = track_progress,
    current_track_percentage = track_percentage,
    volume = volume
  )

# todo: consider streaming instead of doing all this
def audio_file_to_np_array(file_name):
  asg = AudioSegment.from_file(file_name)
  dtype = getattr(np, "int{:d}".format(asg.sample_width * 8))
  arr = np.ndarray((int(asg.frame_count()), asg.channels), buffer=asg.raw_data, dtype=dtype)
  return arr, asg.frame_rate


def toogle_play():
  global is_music_playing, is_track_paused, current_track_start_time, current_track_paused_at
  if is_music_playing:
    is_music_playing = False
    is_track_paused = True
    current_track_paused_at = int(time.time()) - current_track_start_time
    sd.stop()
  else:
    is_music_playing = True
  return is_music_playing


def next_track():
  global current_playlist, current_track_id, current_track, current_track_changed, is_track_paused, is_music_playing
  if len(current_playlist['tracks']) == 0:
    current_track_id = 0
    current_track = None
    # todo: stop music and clear flags
  else:
    current_track_id += 1
    if current_track_id >= len(current_playlist['tracks']):
      current_track_id = 0
    current_track = current_playlist['tracks'][current_track_id]
    current_track_changed = True
    is_track_paused = False
    is_music_playing = True
    print('track has changed! next track...')
    sd.stop()
  return current_track


def prev_track():
  global current_playlist, current_track_id, current_track, current_track_changed, is_track_paused
  if len(current_playlist['tracks']) == 0:
    current_track_id = 0
    current_track = None
    # todo: stop music and clear flags
  else:
    current_track_id -= 1
    if current_track_id < 0:
      current_track_id = len(current_playlist['tracks']) - 1

    current_track = current_playlist['tracks'][current_track_id]
    current_track_changed = True
    is_track_paused = False
    is_music_playing = True
    print('track has changed! previous track...')
    sd.stop()
  return current_track


def resume_track(audio, fr):
  global is_track_paused, current_track_paused_at, current_track_start_time
  print('track was paused! resuming....')
  is_track_paused = False
  audio = audio[current_track_paused_at * fr:]
  current_track_start_time = int(time.time()) - current_track_paused_at
  return audio


def change_volume(v):
  global volume
  volume = v


def main_loop(app):
  global playlists, current_track_id, current_track, current_playlist, is_music_playing, current_track_start_time, volume, is_track_paused, current_track_paused_at, current_track_changed

  print('Starting...')

  with app.app_context():
    # setup output device
    settings = read_settings()
    if settings['audio_output'] in get_output_audio_devices():
      sd.default.device = settings['audio_output']

    # update tracks list on startup
    update_tracks_database()

    # load all playlists and select the first one
    if not playlists:
      playlists = get_all_playlists_with_tracks()
      if len(playlists) > 0:
        current_playlist = playlists[0]

    sd.stop()

  # main loop
  while True:
    if not is_music_playing:
      time.sleep(0.3) # todo: adjust the timeout
      continue

    if not current_playlist:
      # todo: handle this on UI
      print('No playlist is selected')
      time.sleep(0.3)
      continue

    if len(current_playlist['tracks']) == 0:
      print(f"No tracks in the {current_playlist['name']} playlist")
      time.sleep(0.3)
      continue

    print(f"Playing playlist {current_playlist['name']} [{len(current_playlist['tracks'])}]")

    while is_music_playing:
      if not current_track:
        print('No track selected')
        current_track_id = 0
        current_track = current_playlist['tracks'][current_track_id]

      sd.stop()

      print(f"Playing {current_track['name']} track")
      audio, fr = audio_file_to_np_array(current_track['file_path'])

      if is_track_paused:
        audio = resume_track(audio, fr)
      else:
        current_track_start_time = int(time.time())

      sd.play(audio, samplerate=fr)
      sd.wait()

      if not current_track_changed:
        next_track()
        current_track_changed = False

      print(f"{current_track['name']} finished!")

    print(f"Music has been stopped")


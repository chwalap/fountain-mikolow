import threading
from pydub import AudioSegment, playback

import sounddevice as sd

def get_output_audio_devices():
  return [d['name'] for d in sd.query_devices() if d['max_output_channels'] > 0]


def add_track_duration(playlists):
  for playlist in playlists.values():
    for track in playlist['tracks']:
      audio = AudioSegment.from_file(track['file_path'])
      duration = len(audio)
      track['duration'] = duration


def play_playlist(playlists, playlist_id):
  def play_tracks():
    if playlist_id in playlists:
      for track in playlists[playlist_id]['tracks']:
        audio = AudioSegment.from_file(track['file_path'])
        playback.play(audio)

  player_thread = threading.Thread(target=play_tracks)
  player_thread.start()


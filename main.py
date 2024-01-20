import datetime
import random
import time
import json
import tracks
import os
import db
from log import log
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import timedelta
import pyaudio

# todo: use npm and create a bundle of css and js


app = Flask(__name__)
app.secret_key = b'\x9d\x1aS\xac#K\xd8\x89d\xb3\xce\xda\x14IB\x9c\x1a_\xe9\xef$/&l'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=360)


def get_audio_devices():
  p = pyaudio.PyAudio()
  info = p.get_host_api_info_by_index(0)
  numdevices = info.get('deviceCount')
  devices = []

  for i in range(0, numdevices):
    if p.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels') > 0:
      devices.append(p.get_device_info_by_host_api_device_index(0, i).get('name'))

  p.terminate()
  return devices


# def get_datetime_from_hour(time_str):
#   hour, minute = map(int, time_str.split(':'))
#   today = datetime.date.today()
#   return datetime.datetime(year=today.year, month=today.month, day=today.day, hour=hour, minute=minute)


# def get_datetime_from_date(date_str):
#   day, month = map(int, date_str.split('.'))
#   today = datetime.date.today()
#   return datetime.datetime(year=today.year, month=month, day=day)


# def get_tomorrow_start():
#   now = datetime.datetime.now()
#   tomorrow = now.date() + datetime.timedelta(days=1)
#   return datetime.datetime.combine(tomorrow, datetime.time.min)


# def wait_until(tm):
#   while datetime.datetime.now() < tm:
#     time.sleep(1)


# def get_next_scheduled_track(s):
#   if len(s) <= 0:
#       return None, None
#   track = s[0]['filename'], s[0]['time']
#   del(s[0])
#   return track


# def get_next_track(playlist):
#   global current_track_id
#   if len(playlist) == 0:
#       return None
#   current_track = playlist[current_track_id]
#   current_track_id += 1
#   if current_track_id == len(playlist):
#       random.shuffle(playlist)  # reshuffle
#       current_track_id = 0
#   return current_track


# def main_loop(playlist, scheduled_tracks, start_time, end_time):
#   log(f'Waiting for the day to start at {start_time}')
#   wait_until(start_time)

#   next_scheduled_track, next_scheduled_time = get_next_scheduled_track(scheduled_tracks)
#   current_track = get_next_track(playlist)

#   log(f'Music started playing at {datetime.datetime.now()}')

#   while True:
#       # Check end of the day
#       if datetime.datetime.now() >= end_time:
#           break

#       # Check if next scheduled task should be played now
#       if next_scheduled_time is not None and datetime.datetime.now() > next_scheduled_time:
#           log(f'Playing scheduled track {next_scheduled_track}')
#           play_file(next_scheduled_track)
#           next_scheduled_track, next_scheduled_time = get_next_scheduled_track(scheduled_tracks)
#           continue

#       # Wait for next scheduled track or end_time when nothing to play
#       if current_track is None:
#           log('No tracks to play for now')
#           wait_until(min(end_time, end_time if next_scheduled_time is None else next_scheduled_track))
#           continue

#       # Play random track from playlist
#       log(f'Playing random track {current_track}')
#       play_file(current_track)
#       current_track = get_next_track(playlist)

#   log(f'No more music for today')

#   # Wait for tomorrow
#   log(f'Waiting for midnight')
#   wait_until(get_tomorrow_start())


# def main(config_file):
#   while True:
#     config = read_config_file(config_file)
#     start_time = get_datetime_from_hour(config['Work']['start_time'])
#     end_time = get_datetime_from_hour(config['Work']['end_time'])
#     random_playlist, scheduled_tracks = tracks.get_todays_tracks(config)
#     main_loop(random_playlist, scheduled_tracks, start_time, end_time)


# if __name__ == "__main__":
#     try:
#         main('./config.ini')
#     except KeyboardInterrupt:
#         log("Interrupted by user")


settings = {}


@app.route('/')
def home():
  if 'username' not in session:
    return render_template('login.html')

  return redirect(url_for('player'))


@app.route('/player')
def player():
  if 'username' not in session:
    return render_template('login.html')

  settings = db.read_settings()
  db.update_tracks_database(settings['audio_path'])

  playlists = db.get_all_playlists_with_tracks()
  playlists_json = json.dumps(playlists)

  return render_template('player.html',
    selectable_list_title='Playlisty',
    selectable_list_entries_json=playlists_json,
    selectable_list_entries=playlists,
  )


@app.route('/playlist')
def playlist():
  if 'username' not in session:
    return render_template('login.html')

  settings = db.read_settings()
  db.update_tracks_database(settings['audio_path'])

  playlists = db.get_all_playlists_with_tracks()
  playlists_json = json.dumps(playlists)

  tracks = db.get_all_tracks()
  tracks_json = json.dumps(tracks)

  return render_template(
    'playlist.html',
    selectable_list_title='Playlisty',
    selectable_list_entries_json=playlists_json,
    selectable_list_entries=playlists,
    show_create_new_item_button=True,
    tracks_json=tracks_json,
    tracks=tracks
  )


@app.route('/update-playlist', methods=['POST'])
def update_playlist():
  if 'username' not in session:
    return render_template('login.html')

  data = request.json
  playlist_id = data['id']
  # todo: pass data to update_playlist
  playlist_name = data['name']
  track_ids = data['tracks']

  playlist_id = db.update_playlist(playlist_id, playlist_name, track_ids)
  # todo: add handling "no playlist exists"
  return jsonify({'status': 'success', 'playlist_id': playlist_id})


@app.route('/remove-playlist', methods=['POST'])
def remove_playlist():
  if 'username' not in session:
    return render_template('login.html')

  data = request.json
  playlist_id = data['id']

  if db.delete_playlist(playlist_id):
    return jsonify({'status': 'success'})
  else:
    return jsonify({'status': 'failure'}), 400


@app.route('/schedule')
def schedule():
  if 'username' not in session:
    return render_template('login.html')

  schedules = db.get_all_schedules()
  schedules_json = json.dumps(schedules)

  # todo: consider making this aprt of get_all_tracks
  settings = db.read_settings()
  db.update_tracks_database(settings['audio_path'])

  tracks = db.get_all_tracks()
  tracks_json = json.dumps(tracks)

  return render_template(
    'schedule.html',
    selectable_list_title='Harmonogram',
    selectable_list_entries_json=schedules_json,
    selectable_list_entries=schedules,
    show_create_new_item_button=True,
    tracks_json=tracks_json,
    tracks=tracks
  )


@app.route('/update-schedule', methods=['POST'])
def update_schedule():
  if 'username' not in session:
    return render_template('login.html')

  data = request.json
  schedule_id = data['id']
  # todo: pass data to update_schedule
  schedule_name = data['name']
  schedule_type = data['type']
  schedule_time = data['time']
  schedule_date = data['date']
  schedule_track_id = data['track_id']

  # todo: add validation fo incoming data parameters

  schedule_id = db.update_schedule(schedule_id, schedule_name, schedule_type, schedule_time, schedule_date, schedule_track_id)

  # todo: add handling "no schedule exists"
  return jsonify({'status': 'success', 'schedule_id': schedule_id})


@app.route('/remove-schedule', methods=['POST'])
def remove_schedule():
  if 'username' not in session:
    return render_template('login.html')

  data = request.json
  schedule_id = data['id']

  if db.delete_schedule(schedule_id):
    return jsonify({'status': 'success'})
  else:
    return jsonify({'status': 'failure'}), 400


@app.route('/settings')
def settings():
  if 'username' not in session:
    return render_template('login.html')

  settings = db.read_settings()
  audio_devices = get_audio_devices()

  return render_template('settings.html', settings=settings, audio_devices=audio_devices)


@app.route('/save-settings', methods=['POST'])
def save_settings():
  if 'username' not in session:
    return render_template('login.html')

  if db.save_settings(request.json):
    return jsonify({'status': 'success'})
  else:
    return jsonify({'status': 'failure'}), 400


@app.route('/logout')
def logout():
  session.pop('username', None)
  return redirect(url_for('home'))


@app.route('/login', methods=['POST'])
def login():
  username = request.form['username']
  password = request.form['password']

  if not db.check_user_credentials(username, password):
    return "Invalid username or password", 401

  session['username'] = username

  return redirect(url_for('player'))


if __name__ == '__main__':
  db.create_tables()
  settings = db.read_settings()
  app.run('0.0.0.0', 1234, debug=True)

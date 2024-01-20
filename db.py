import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash


def db_connect():
  _conn = sqlite3.connect('player.db')
  return _conn


def create_tables():
  conn = db_connect()
  cursor = conn.cursor()

  cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                      id INTEGER PRIMARY KEY,
                      username TEXT NOT NULL,
                      password TEXT NOT NULL
                    )''')

  cursor.execute('''CREATE TABLE IF NOT EXISTS schedule (
                      id INTEGER PRIMARY KEY,
                      name TEXT NOT NULL,
                      type TEXT NOT NULL,
                      time TEXT NOT NULL,
                      date TEXT NOT NULL,
                      track_id INTEGER,
                      FOREIGN KEY (track_id) REFERENCES tracks (id)
                    )''')

  cursor.execute('''CREATE TABLE IF NOT EXISTS playlists (
                      id INTEGER PRIMARY KEY,
                      name TEXT NOT NULL
                    )''')

  cursor.execute('''CREATE TABLE IF NOT EXISTS tracks (
                      id INTEGER PRIMARY KEY,
                      name TEXT NOT NULL,
                      file_path TEXT NOT NULL
                    )''')

  cursor.execute('''CREATE TABLE IF NOT EXISTS playlist_tracks (
                    playlist_id INTEGER,
                    track_id INTEGER,
                    FOREIGN KEY (playlist_id) REFERENCES playlists (id),
                    FOREIGN KEY (track_id) REFERENCES tracks (id)
                  )''')

  cursor.execute('''CREATE TABLE IF NOT EXISTS settings (
                      key TEXT PRIMARY KEY,
                      value TEXT
                    )''')

  conn.commit()
  conn.close()

  add_setting('audio_output', '')
  add_setting('player_always_on_top', 'True')
  add_setting('working_from', '08:00')
  add_setting('working_to', '22:00')

  add_user('admin', 'dupa123kotki666')


def read_settings():
  conn = db_connect()
  cursor = conn.cursor()
  cursor.execute("SELECT key, value FROM settings")
  results = {key: value for key, value in cursor.fetchall()}
  results['player_always_on_top'] = True if results['player_always_on_top'] == 'True' else False
  conn.close()
  return results


def save_settings(settings):
  conn = db_connect()
  cursor = conn.cursor()
  cursor.execute('UPDATE settings SET value = ? WHERE key = ?', (settings['audio_output'], 'audio_output'))
  cursor.execute('UPDATE settings SET value = ? WHERE key = ?', ('True' if settings['player_always_on_top'] == 'on' else 'False', 'player_always_on_top'))
  cursor.execute('UPDATE settings SET value = ? WHERE key = ?', (settings['working_from'], 'working_from'))
  cursor.execute('UPDATE settings SET value = ? WHERE key = ?', (settings['working_to'], 'working_to'))
  conn.commit()
  conn.close()

  return True


def add_setting(key, value):
  conn = db_connect()
  cursor = conn.cursor()
  cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, value))
  conn.commit()
  conn.close()


def add_user(username, password):
  conn = db_connect()
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
  if cursor.fetchone():
    return None

  sql = ''' INSERT INTO users(username, password)
            VALUES(?, ?) '''
  cursor.execute(sql, (username, generate_password_hash(password)))
  conn.commit()
  conn.close()
  return cursor.lastrowid


def check_user_credentials(username, password):
  conn = db_connect()
  cursor = conn.cursor()
  cursor.execute(f"SELECT id, password FROM users WHERE username = '{username}'")
  user = cursor.fetchone()
  conn.close()
  if user:
    return check_password_hash(user[1], password)
  return False


def update_tracks_database(directory):
  conn = db_connect()
  cursor = conn.cursor()
  cursor.execute("SELECT id, name FROM tracks")

  existing_tracks = {name: id for id, name in cursor.fetchall()}
  current_tracks = set(os.listdir(directory))

  for track in current_tracks:
    if track not in existing_tracks:
      cursor.execute("INSERT INTO tracks (name, file_path) VALUES (?, ?)", (track, os.path.join(directory, track)))

  for track, id in existing_tracks.items():
    if track not in current_tracks:
      cursor.execute("DELETE FROM tracks WHERE id = ?", (id,))

  conn.commit()
  conn.close()


def add_track_to_playlist(track_id, playlist_id):
  conn = db_connect()
  cursor = conn.cursor()
  cursor.execute("INSERT INTO playlist_tracks (playlist_id, track_id) VALUES (?, ?)", (playlist_id, track_id))
  conn.commit()
  conn.close()


def remove_track_from_playlist(track_id, playlist_id):
  conn = db_connect()
  cursor = conn.cursor()
  cursor.execute("DELETE FROM playlist_tracks WHERE playlist_id = ? AND track_id = ?", (playlist_id, track_id))
  conn.commit()
  conn.close()


def get_all_playlists():
  query = "SELECT p.id, p.name FROM playlists p ORDER BY p.id"
  conn = db_connect()
  cursor = conn.cursor()
  cursor.execute(query)
  results = cursor.fetchall()
  conn.close()
  return results


def get_all_playlists_with_tracks():
  ps = get_all_playlists()

  conn = db_connect()
  cursor = conn.cursor()
  playlists = []

  for playlist_id, playlist_name in ps:
    query = f'''
    SELECT s.id, s.name, s.file_path
    FROM playlists p
    JOIN playlist_tracks ps ON p.id = ps.playlist_id
    JOIN tracks s ON ps.track_id = s.id
    WHERE p.id = {playlist_id}
    ORDER BY s.name
    '''
    cursor.execute(query)
    tracks = cursor.fetchall()

    playlist = {'id': playlist_id, 'name': playlist_name, 'tracks': []}
    for track_id, track_name, track_file_path in tracks:
      playlist['tracks'].append({'id': track_id, 'name': track_name, 'file_path': track_file_path})

    playlists.append(playlist)

  conn.close()
  return playlists


def get_all_tracks():
  query = "SELECT s.id, s.name, s.file_path FROM tracks s ORDER BY s.id"
  conn = db_connect()
  cursor = conn.cursor()
  cursor.execute(query)
  results = cursor.fetchall()
  tracks = []
  for track_id, track_name, file_path in results:
    tracks.append({'id': track_id, 'name' : track_name, 'file_path': file_path})
  return tracks


def update_playlist(playlist_id, playlist_name, track_ids):
  conn = db_connect()
  cursor = conn.cursor()

  if playlist_id == -1:
    cursor.execute('INSERT INTO playlists (name) VALUES (?)', (playlist_name,))
    playlist_id = cursor.lastrowid
  else:
    cursor.execute('UPDATE playlists SET name = ? WHERE id = ?', (playlist_name, playlist_id))

  # Update tracks in the playlist
  cursor.execute('DELETE FROM playlist_tracks WHERE playlist_id = ?', (playlist_id,))
  for track_id in track_ids:
    cursor.execute('INSERT INTO playlist_tracks (playlist_id, track_id) VALUES (?, ?)', (playlist_id, track_id))

  conn.commit()
  conn.close()
  return playlist_id


def delete_playlist(playlist_id):
  query = "DELETE FROM playlists WHERE id = ?"
  conn = db_connect()
  cursor = conn.cursor()

  try:
    cursor.execute(query, (playlist_id,))
    conn.commit()
    success = cursor.rowcount > 0
  except Exception as e:
    print(f"An error occurred: {e}")
    success = False
  finally:
    conn.close()

  return success


def get_all_schedules():
  query = "SELECT s.id, s.name, s.type, s.time, s.date, s.track_id FROM schedule s ORDER BY s.id"
  conn = db_connect()
  cursor = conn.cursor()
  cursor.execute(query)
  results = cursor.fetchall()
  schedules = []
  for schedule_id, schedule_name, schedule_type, scheduled_time, scheduled_date, track_id in results:
    schedules.append({'id': schedule_id, 'name' : schedule_name, 'type': schedule_type, 'time': scheduled_time, 'date' : scheduled_date, 'track_id' : track_id})
  return schedules


def update_schedule(schedule_id, schedule_name, schedule_type, schedule_time, schedule_date, schedule_track_id):
  conn = db_connect()
  cursor = conn.cursor()

  if schedule_id == -1:
    cursor.execute('INSERT INTO schedule (name, type, time, date, track_id) VALUES (?, ?, ?, ?, ?)', (schedule_name, schedule_type, schedule_time, schedule_date, schedule_track_id))
    schedule_id = cursor.lastrowid
  else:
    cursor.execute('UPDATE schedule SET name = ?, type = ?, time = ?, date = ?, track_id = ? WHERE id = ?', (schedule_name, schedule_type, schedule_time, schedule_date, schedule_track_id, schedule_id))

  conn.commit()
  conn.close()
  return schedule_id


def delete_schedule(schedule_id):
  query = "DELETE FROM schedule WHERE id = ?"
  conn = db_connect()
  cursor = conn.cursor()

  try:
    cursor.execute(query, (schedule_id,))
    conn.commit()
    success = cursor.rowcount > 0
  except Exception as e:
    print(f"An error occurred: {e}")
    success = False
  finally:
    conn.close()

  return success

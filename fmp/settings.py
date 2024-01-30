import sounddevice as sd

from flask import (
  Blueprint, render_template, request, jsonify, session
)

from fmp.db import get_db
from fmp.auth import login_required
from fmp.audio import get_output_audio_devices
from fmp.tracks import update_tracks_database

from werkzeug.security import generate_password_hash


bp = Blueprint('settings', __name__, url_prefix='/settings')


@bp.route('/')
@login_required
def settings():
  return render_template('settings.html', audio_devices=get_output_audio_devices())


@bp.route('/save', methods=['POST'])
@login_required
def save_settings():
  if request.json['audio_output'] in get_output_audio_devices():
    sd.default.device = request.json['audio_output']
  else:
    return jsonify({'status': 'failure'})

  try:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('UPDATE settings SET value = ? WHERE key = ?', (request.json['audio_output'], 'audio_output'))
    cursor.execute('UPDATE settings SET value = ? WHERE key = ?', ('True' if request.json['player_always_on_top'] == 'on' else 'False', 'player_always_on_top'))
    cursor.execute('UPDATE settings SET value = ? WHERE key = ?', (request.json['working_from'], 'working_from'))
    cursor.execute('UPDATE settings SET value = ? WHERE key = ?', (request.json['working_to'], 'working_to'))
    db.commit()
  except Exception as e:
    print(f"An error occurred: {e}")
    return jsonify({'status': 'failure'}), 400

  return jsonify({'status': 'success'})


@bp.route('/refresh-track-list', methods=['POST'])
@login_required
def refresh_track_list():
  if update_tracks_database():
    return jsonify({'status': 'success'})
  else:
    return jsonify({'status': 'failure'}), 400


@bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
  username = session['username']
  new_password = request.json['new_password']

  if new_password == '':
    return jsonify({'status': 'failure'}), 400

  try:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('UPDATE users SET password = ? WHERE username = ?', (generate_password_hash(new_password), username))
    db.commit()
  except Exception as e:
    print(f'An error occurred: {e}')
    return jsonify({'status': 'failure'}), 400

  return jsonify({'status': 'success'})


def read_settings():
  results = {}
  try:
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT key, value FROM settings")
    results = {key: value for key, value in cursor.fetchall()}
    results['player_always_on_top'] = True if results['player_always_on_top'] == 'True' else False
  except Exception as e:
    print(f'An error occured: {e}')
    print(e.with_traceback())

  return results


def add_setting(key, value):
  try:
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, value))
    db.commit()
  except Exception as e:
    print(f'An error occured: {e}')


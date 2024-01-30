import json

from flask import (
  Blueprint, render_template, request, jsonify
)

from fmp.db import get_db
from fmp.auth import login_required
from fmp.tracks import get_all_tracks

bp = Blueprint('schedule', __name__, url_prefix='/schedule')


@bp.route('/')
@login_required
def schedule():
  schedules = get_all_schedules()
  schedules_json = json.dumps(schedules)

  tracks = get_all_tracks()
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


@bp.route('/update', methods=['POST'])
@login_required
def update_schedule():
  # todo: add validation for incoming data parameters
  try:
    db = get_db()
    cursor = db.cursor()
    data = request.json
    schedule_id = data['id']
    schedule_name = data['name']
    schedule_type = data['type']
    schedule_time = data['time']
    schedule_date = data['date']
    schedule_track_id = data['track_id']

    if schedule_id == -1:
      cursor.execute('INSERT INTO schedule (name, type, time, date, track_id) VALUES (?, ?, ?, ?, ?)', (schedule_name, schedule_type, schedule_time, schedule_date, schedule_track_id))
      schedule_id = cursor.lastrowid
    else:
      cursor.execute('UPDATE schedule SET name = ?, type = ?, time = ?, date = ?, track_id = ? WHERE id = ?', (schedule_name, schedule_type, schedule_time, schedule_date, schedule_track_id, schedule_id))

    db.commit()
  except Exception as e:
    print(f"An error occurred: {e}")
    return jsonify({'status': 'failure'}), 400

  return jsonify({'status': 'success', 'schedule_id': schedule_id})


@bp.route('/remove', methods=['POST'])
@login_required
def remove_schedule():
  try:
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM schedule WHERE id = ?", (request.json['id'],))
    db.commit()
  except Exception as e:
    print(f"An error occurred: {e}")
    return jsonify({'status': 'failure'}), 400

  return jsonify({'status': 'success'})


def get_all_schedules():
  schedules = []
  try:
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT s.id, s.name, s.type, s.time, s.date, s.track_id FROM schedule s ORDER BY s.id")
    results = cursor.fetchall()
    for r in results:
      schedules.append({'id': r['id'], 'name' : r['name'], 'type': r['type'], 'time': r['time'], 'date' : r['date'], 'track_id' : r['track_id']})
  except Exception as e:
    print(f"An error occurred: {e}")

  return schedules


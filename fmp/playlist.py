import json

from flask import (
  Blueprint, render_template, request, jsonify
)

from fmp.db import get_db
from fmp.auth import login_required
from fmp.tracks import get_all_tracks

bp = Blueprint('playlist', __name__, url_prefix='/playlist')

@bp.route('/')
@login_required
def playlist():
  playlists = get_all_playlists_with_tracks()
  playlists_json = json.dumps(playlists)

  tracks = get_all_tracks()
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


@bp.route('/update', methods=['POST'])
@login_required
def update_playlist():
  try:
    db = get_db()
    cursor = db.cursor()
    data = request.json
    playlist_id = data['id']
    playlist_name = data['name']
    track_ids = data['tracks']

    if playlist_id == -1:
      cursor.execute('INSERT INTO playlists (name) VALUES (?)', (playlist_name,))
      playlist_id = cursor.lastrowid
    else:
      cursor.execute('UPDATE playlists SET name = ? WHERE id = ?', (playlist_name, playlist_id))

    # Update tracks in the playlist
    cursor.execute('DELETE FROM playlist_tracks WHERE playlist_id = ?', (playlist_id,))
    for track_id in track_ids:
      cursor.execute('INSERT INTO playlist_tracks (playlist_id, track_id) VALUES (?, ?)', (playlist_id, track_id))

    db.commit()
  except Exception as e:
    print(f"An error occurred: {e}")
    return jsonify({'status': 'failure'}), 400

  return jsonify({'status': 'success', 'playlist_id': playlist_id})


@bp.route('/remove', methods=['POST'])
@login_required
def remove_playlist():
  try:
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM playlists WHERE id = ?", (request.json['id'],))
    db.commit()
  except Exception as e:
    print(f"An error occurred: {e}")
    return jsonify({'status': 'failure'}), 400

  return jsonify({'status': 'success'})


def get_all_playlists():
  try:
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT p.id, p.name FROM playlists p ORDER BY p.id")
    return cursor.fetchall()
  except Exception as e:
    print(f"An error occurred: {e}")


def get_all_playlists_with_tracks():
  playlists = []
  try:
    db = get_db()
    cursor = db.cursor()

    for p in get_all_playlists():
      tracks = cursor.execute(f'''
        SELECT s.id, s.name, s.file_path, s.duration
        FROM playlists p
        JOIN playlist_tracks ps ON p.id = ps.playlist_id
        JOIN tracks s ON ps.track_id = s.id
        WHERE p.id = {p['id']}
        ORDER BY s.name
      ''').fetchall()

      playlist = {'id': p['id'], 'name': p['name'], 'tracks': []}
      for t in tracks:
        playlist['tracks'].append({'id': t['id'], 'name': t['name'], 'file_path': t['file_path'], 'duration': t['duration']})

      playlists.append(playlist)
  except Exception as e:
    print(f"An error occurred: {e}")

  return playlists


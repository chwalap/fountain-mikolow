import json
import sounddevice as sd

from flask import (
  Blueprint, render_template, jsonify, g, request
)

import fmp.main
from fmp.auth import login_required
from fmp.playlist import get_all_playlists_with_tracks

bp = Blueprint('player', __name__, url_prefix='/player')


@bp.route('/')
@login_required
def player():
  playlists = get_all_playlists_with_tracks()
  playlists_json = json.dumps(playlists)

  # todo: add current_playlist, current_track

  return render_template('player.html',
    selectable_list_title='Playlisty',
    selectable_list_entries_json=playlists_json,
    selectable_list_entries=playlists,
  )


@bp.route("/toogle-play")
@login_required
def toogle_play():
  is_music_playing = fmp.main.toogle_play()
  return jsonify({'status': 'success', 'is_music_playing': is_music_playing})


@bp.route("/next-track")
@login_required
def next_track():
  # todo: handle when no playlist is selected
  current_track = fmp.main.next_track()
  return jsonify({'status': 'success', 'current_track': current_track})


@bp.route("/prev-track")
@login_required
def prev_track():
  current_track = fmp.main.prev_track()
  return jsonify({'status': 'success', 'current_track': current_track})


@bp.route('/change-volume', methods=["POST"])
@login_required
def change_volume():
  try:
    volume = int(request.json['volume'])
    if volume < 0 or volume > 100:
      raise 'Incorrect value of volume!'
    fmp.main.change_volume(volume)
  except Exception as e:
    return jsonify({'status': 'failure', 'message': 'Nieprawidłowy poziom głośności!'})

  return jsonify({'status': 'success'})


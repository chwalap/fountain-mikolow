import os
import threading

from flask import Flask, redirect, url_for
from datetime import timedelta

from fmp.settings import read_settings
from fmp.main import main_loop, get_player_state

is_main_loop_running = False


def create_app(test_config=None):
  app = Flask(__name__, instance_relative_config=True)

  app.secret_key = b'\x9d\x1aS\xac#K\xd8\x89d\xb3\xce\xda\x14IB\x9c\x1a_\xe9\xef$/&l'
  app.config['SESSION_PERMANENT'] = True
  app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=360)
  app.config['DATABASE'] = os.path.join(app.instance_path, 'player.db')

  if test_config is None:
    app.config.from_pyfile('config.py', silent=True)
  else:
    app.config.from_mapping(test_config)

  try:
    os.makedirs(app.instance_path)
  except OSError:
    pass

  # import and register all blueprints
  from . import db
  db.init_app(app)

  from . import auth
  app.register_blueprint(auth.bp)

  from . import player
  app.register_blueprint(player.bp)

  from . import playlist
  app.register_blueprint(playlist.bp)

  from . import schedule
  app.register_blueprint(schedule.bp)

  from . import settings
  app.register_blueprint(settings.bp)

  # index endpoint
  @app.route('/')
  @auth.login_required
  def index():
    return redirect(url_for('player.player'))

  # settings ctx processor
  @app.context_processor
  def settings_processor():
    return dict(settings=read_settings())

  # current track ctx processor
  @app.context_processor
  def player_state_processor():
    return get_player_state()


  @app.template_filter('format_time')
  def format_time(secs):
    hours = secs // 3600
    minutes = (secs % 3600) // 60
    seconds = secs % 60

    if hours > 0:
      return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
      return f"{minutes:02d}:{seconds:02d}"


  global is_main_loop_running
  if not is_main_loop_running:
    is_main_loop_running = True
    threading.Thread(target=main_loop, args=(app,), daemon=True).start()

  return app


import functools

from flask import (
  Blueprint, redirect, render_template, request, session, url_for, flash, g
)
from werkzeug.security import check_password_hash, generate_password_hash

from fmp.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/logout')
def logout():
  session.pop('username', None)
  return redirect(url_for('index'))


@bp.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    error = None

    try:
      db = get_db()
      cursor = db.cursor()
      user = cursor.execute(f"SELECT id, password FROM users WHERE username = '{username}'").fetchone()
      print(user['password'])

      if user is None:
        error = f'Użytkownik {username} nie istnieje!'
      elif not check_password_hash(user['password'], password):
        error = 'Niepoprawne hasło!'

    except Exception as e:
      error = f'Błąd serwera: {e}'

    if error is None:
      session['username'] = username
      return redirect(url_for('index'))

    flash(error)

  return render_template('login.html')


def login_required(view):
  @functools.wraps(view)
  def wrapped_view(**kwargs):
    if 'username' not in session:
      return redirect(url_for('auth.login'))

    return view(**kwargs)

  return wrapped_view


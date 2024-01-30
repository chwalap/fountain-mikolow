import os
from pydub import AudioSegment

from fmp.db import get_db


def get_all_tracks():
  tracks = []

  try:
    db = get_db()
    cursor = db.cursor()
    cursor.execute( "SELECT id, name, file_path, duration FROM tracks ORDER BY id")
    results = cursor.fetchall()
    for r in results:
      tracks.append({'id': r['id'], 'name' : r['name'], 'file_path': r['file_path'], 'duration': r['duration']})
  except Exception as e:
    print(f"An error occurred: {e}")

  return tracks


def update_tracks_database():
  directory = './fmp/audio/' # maybe make it part of config?

  try:
    db = get_db()
    cursor = db.cursor()

    db_tracks = cursor.execute("SELECT id, name FROM tracks").fetchall()
    db_track_names = {t['name'] for t in db_tracks}
    fs_tracks = set(os.listdir(directory))

    for track_name in fs_tracks:
      if track_name not in db_track_names:
        track_path = os.path.join(directory, track_name)
        track_duration = AudioSegment.from_file(track_path).duration_seconds
        cursor.execute("INSERT INTO tracks (name, file_path, duration) VALUES (?, ?, ?)", (track_name, track_path, int(track_duration),))
        print(f'New track added into database: {track_path}: {track_duration}')

    for track_id, track_name in db_tracks:
      if track_name not in fs_tracks:
        cursor.execute("DELETE FROM tracks WHERE id = ?", (track_id,))
        cursor.execute("DELETE FROM playlist_tracks WHERE track_id = ?", (track_id,))
        print(f'Track {track_name} removed from database')

    db.commit()
    return True
  except Exception as e:
    print(f"An error occurred: {e}")
    return False






# import datetime
# import os
# import pandas as pd
# import random
# from log import log


# def is_christmas_period(start, end):
#     now = datetime.datetime.now()
#     start_date = datetime.datetime.strptime(start, "%d.%m").replace(year=now.year)
#     end_date = datetime.datetime.strptime(end, "%d.%m").replace(year=now.year)

#     if end_date < start_date:
#         end_date = end_date.replace(year=end_date.year + 1)

#     return start_date <= now <= end_date


# def get_files_in_directory(path):
#     return [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.mp3')]


# def create_playlist(config):
#     random_path = config['Audio']['audio_random_path']
#     christmas_path = config['Audio']['audio_christmas_path']
#     christmas_start = config['Christmas']['christmas_start']
#     christmas_end = config['Christmas']['christmas_end']

#     if is_christmas_period(christmas_start, christmas_end):
#         log("It's Christmas time!\n")
#         return get_files_in_directory(christmas_path)
#     else:
#         return get_files_in_directory(random_path)


# def read_schedules(yearly_schedule_file, daily_schedule_file, schedule_path):
#     if not os.path.exists(yearly_schedule_file):
#         log(f'{yearly_schedule_file} does not exists')
#         exit(1)

#     if not os.path.exists(daily_schedule_file):
#         log(f'{daily_schedule_file} does not exists')
#         exit(1)

#     now = datetime.datetime.now()
#     date_format = '%H:%M:%S'

#     yearly_schedule = pd.read_csv(yearly_schedule_file, dtype={'time': 'object'})
#     yearly_schedule['filename'] = yearly_schedule['filename'].apply(lambda x: os.path.join(schedule_path, x))
#     yearly_schedule['time'] = pd.to_datetime(yearly_schedule['time'], format='%d.%m.%Y %H:%M:%S')
#     yearly_schedule = yearly_schedule[yearly_schedule['time'].dt.date == now.date()]
#     yearly_tracks = yearly_schedule.to_dict('records')

#     daily_schedule = pd.read_csv(daily_schedule_file, dtype={'time': 'object'})
#     daily_schedule['filename'] = daily_schedule['filename'].apply(lambda x: os.path.join(schedule_path, x))
#     daily_schedule['time'] = pd.to_datetime(daily_schedule['time'], format=date_format)
#     daily_schedule['time'] = daily_schedule['time'].apply(lambda x: datetime.datetime(now.year, now.month, now.day, x.hour, x.minute, x.second))
#     daily_tracks = daily_schedule.to_dict('records')

#     combined_tracks = yearly_tracks + daily_tracks
#     combined_tracks.sort(key=lambda x: x['time'])

#     # Remove tracks that do not exist or are expired
#     valid_tracks = [track for track in combined_tracks if os.path.exists(track['filename']) and track['time'] >= now]

#     return valid_tracks


# def get_todays_tracks(config):
#     random_playlist = create_playlist(config)
#     random.shuffle(random_playlist)
#     log("Random playlist:")
#     [log(f"\t{f}") for f in random_playlist]
#     log()

#     scheduled_tracks = read_schedules(
#         config['Schedules']['yearly_schedule'],
#         config['Schedules']['daily_schedule'],
#         config['Audio']['audio_schedule_path']
#     )
#     log("Scheduled tracks for today:")
#     [log(f"\t{t['filename']} at {t['time']}") for t in scheduled_tracks]
#     log()

#     return random_playlist, scheduled_tracks




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



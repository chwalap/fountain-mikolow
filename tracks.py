import datetime
import os
import pandas as pd
import random
from log import log


def is_christmas_period(start, end):
    now = datetime.datetime.now()
    start_date = datetime.datetime.strptime(start, "%d.%m").replace(year=now.year)
    end_date = datetime.datetime.strptime(end, "%d.%m").replace(year=now.year)

    if end_date < start_date:
        end_date = end_date.replace(year=end_date.year + 1)

    return start_date <= now <= end_date


def get_files_in_directory(path):
    return [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.mp3')]


def create_playlist(config):
    random_path = config['Audio']['audio_random_path']
    christmas_path = config['Audio']['audio_christmas_path']
    christmas_start = config['Christmas']['christmas_start']
    christmas_end = config['Christmas']['christmas_end']

    if is_christmas_period(christmas_start, christmas_end):
        log("It's Christmas time!\n")
        return get_files_in_directory(christmas_path)
    else:
        return get_files_in_directory(random_path)


def read_schedules(yearly_schedule_file, daily_schedule_file, schedule_path):
    if not os.path.exists(yearly_schedule_file):
        log(f'{yearly_schedule_file} does not exists')
        exit(1)

    if not os.path.exists(daily_schedule_file):
        log(f'{daily_schedule_file} does not exists')
        exit(1)

    now = datetime.datetime.now()
    date_format = '%H:%M:%S'

    yearly_schedule = pd.read_csv(yearly_schedule_file, dtype={'time': 'object'})
    yearly_schedule['filename'] = yearly_schedule['filename'].apply(lambda x: os.path.join(schedule_path, x))
    yearly_schedule['time'] = pd.to_datetime(yearly_schedule['time'], format='%d.%m.%Y %H:%M:%S')
    yearly_schedule = yearly_schedule[yearly_schedule['time'].dt.date == now.date()]
    yearly_tracks = yearly_schedule.to_dict('records')

    daily_schedule = pd.read_csv(daily_schedule_file, dtype={'time': 'object'})
    daily_schedule['filename'] = daily_schedule['filename'].apply(lambda x: os.path.join(schedule_path, x))
    daily_schedule['time'] = pd.to_datetime(daily_schedule['time'], format=date_format)
    daily_schedule['time'] = daily_schedule['time'].apply(lambda x: datetime.datetime(now.year, now.month, now.day, x.hour, x.minute, x.second))
    daily_tracks = daily_schedule.to_dict('records')

    combined_tracks = yearly_tracks + daily_tracks
    combined_tracks.sort(key=lambda x: x['time'])

    # Remove tracks that do not exist or are expired
    valid_tracks = [track for track in combined_tracks if os.path.exists(track['filename']) and track['time'] >= now]

    return valid_tracks


def get_todays_tracks(config):
    random_playlist = create_playlist(config)
    random.shuffle(random_playlist)
    log("Random playlist:")
    [log(f"\t{f}") for f in random_playlist]
    log()

    scheduled_tracks = read_schedules(
        config['Schedules']['yearly_schedule'],
        config['Schedules']['daily_schedule'],
        config['Audio']['audio_schedule_path']
    )
    log("Scheduled tracks for today:")
    [log(f"\t{t['filename']} at {t['time']}") for t in scheduled_tracks]
    log()

    return random_playlist, scheduled_tracks

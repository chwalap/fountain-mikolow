import os
import configparser
import datetime
import random
import time
import tracks
from log import log

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame

pygame.mixer.init()
current_track_id = 0


def read_config_file(filepath):
    c = configparser.ConfigParser()
    c.read(filepath)
    if get_datetime_from_hour(c['Work']['start_time']) > get_datetime_from_hour(c['Work']['end_time']):
        log('start_time is after end_time')
        exit(1)
    return c


def play_file(filename):
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(1)


def get_datetime_from_hour(time_str):
    hour, minute = map(int, time_str.split(':'))
    today = datetime.date.today()
    return datetime.datetime(year=today.year, month=today.month, day=today.day, hour=hour, minute=minute)


def get_datetime_from_date(date_str):
    day, month = map(int, date_str.split('.'))
    today = datetime.date.today()
    return datetime.datetime(year=today.year, month=month, day=day)


def get_tomorrow_start():
    now = datetime.datetime.now()
    tomorrow = now.date() + datetime.timedelta(days=1)
    return datetime.datetime.combine(tomorrow, datetime.time.min)


def wait_until(tm):
    while datetime.datetime.now() < tm:
        time.sleep(1)


def get_next_scheduled_track(s):
    if len(s) <= 0:
        return None, None
    track = s[0]['filename'], s[0]['time']
    del(s[0])
    return track


def get_next_track(playlist):
    global current_track_id
    if len(playlist) == 0:
        return None
    current_track = playlist[current_track_id]
    current_track_id += 1
    if current_track_id == len(playlist):
        random.shuffle(playlist)  # reshuffle
        current_track_id = 0
    return current_track


def main_loop(playlist, scheduled_tracks, start_time, end_time):
    log(f'Waiting for the day to start at {start_time}')
    wait_until(start_time)

    next_scheduled_track, next_scheduled_time = get_next_scheduled_track(scheduled_tracks)
    current_track = get_next_track(playlist)

    log(f'Music started playing at {datetime.datetime.now()}')

    while True:
        # Check end of the day
        if datetime.datetime.now() >= end_time:
            break

        # Check if next scheduled task should be played now
        if next_scheduled_time is not None and datetime.datetime.now() > next_scheduled_time:
            log(f'Playing scheduled track {next_scheduled_track}')
            play_file(next_scheduled_track)
            next_scheduled_track, next_scheduled_time = get_next_scheduled_track(scheduled_tracks)
            continue

        # Wait for next scheduled track or end_time when nothing to play
        if current_track is None:
            log('No tracks to play for now')
            wait_until(min(end_time, end_time if next_scheduled_time is None else next_scheduled_track))
            continue

        # Play random track from playlist
        log(f'Playing random track {current_track}')
        play_file(current_track)
        current_track = get_next_track(playlist)

    log(f'No more music for today')

    # Wait for tomorrow
    log(f'Waiting for midnight')
    wait_until(get_tomorrow_start())


def main(config_file):
    while True:
        config = read_config_file(config_file)
        start_time = get_datetime_from_hour(config['Work']['start_time'])
        end_time = get_datetime_from_hour(config['Work']['end_time'])
        random_playlist, scheduled_tracks = tracks.get_todays_tracks(config)
        main_loop(random_playlist, scheduled_tracks, start_time, end_time)


if __name__ == "__main__":
    try:
        main('./config.ini')
    except KeyboardInterrupt:
        log("Interrupted by user")

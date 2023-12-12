import datetime


def log(message=None):
    if message is None:
        log_to_stdout_and_file('')
    else:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_to_stdout_and_file(f"{timestamp} - {message}")


def log_to_stdout_and_file(message):
    print(message)
    with open('player.log', 'a') as file:
        file.write(f'{message}\n')

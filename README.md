# Running MP3 Player

This guide provides instructions on how to set up and run the MP3 Player project, designed specifically for Raspberry Pi. This Python-based player allows for the scheduling and random playing of audio tracks.

## Prerequisites

- A Raspberry Pi with Raspbian OS installed.
- Basic familiarity with the command line interface.

## Installation Steps

1. **Clone the Repository**: Clone the project repository to your Raspberry Pi.

    ```bash
    git clone https://github.com/chwalap/fountain-mikolow.git
    cd fountain-mikolow
    ```

2. **Create a Python Environment**:
   
    It's recommended to use a virtual environment for this project.

    ```bash
    sudo apt-get install python3-venv
    python3 -m venv mp3player_env
    source mp3player_env/bin/activate
    ```

3. **Install Dependencies**:

    Install the required Python packages.

    ```bash
    pip install -r requirements.txt
    ```

## Configuration

Before running the application, ensure to configure the following:

- **Audio Directories**: Set the paths for audio files in the configuration file. The directories are:
  - `./audio/random`: For random audio tracks.
  - `./audio/christmas`: For Christmas audio tracks.
  - `./audio/schedule`: For scheduled audio tracks.

- **Schedules**:
  - `yearly_schedule.csv` and `daily_schedule.csv` for scheduling tracks.

    Format for `daily_schedule.csv`:
    ```
    filename, time
    Hejnal_mariacki.mp3, 15:50:00
    ...
    ```

    Format for `yearly_schedule.csv`:
    ```
    filename, time
    Ludovico_Einaudi_-_Nuvole_Bianche.mp3, 4.12.2023 16:24:00
    ...
    ```

- **Work Hours Configuration**: Define the start and end times for music playback.

- **Christmas Period Configuration**: Set the start and end dates for the Christmas period.

## Running the Application

To run the MP3 Player, use the following command:

```bash
python3 main.py
```

This will start the MP3 Player according to the configurations set in your files.

## Additional Notes

- Ensure that your audio files are correctly placed in the respective directories.
- Verify that the CSV schedule files are formatted correctly.
- Adjust the configurations as needed to suit your specific use case.

---

## Running the MP3 Player as a Service on Raspberry Pi

To ensure the MP3 Player runs continuously in the background and starts automatically at boot, it's advisable to set it up as a systemd service. Follow these steps to achieve this:

### Creating the Service File

1. **Create a New Service File**:

    Open a new service file in the systemd directory.

    ```bash
    sudo nano /etc/systemd/system/mp3player.service
    ```

2. **Add Service Configuration**:

    In the opened file, add the following configuration:

    ```ini
    [Unit]
    Description=MP3 Player Service
    After=network.target

    [Service]
    Type=simple
    User=pi
    WorkingDirectory=/path/to/your/project
    ExecStart=/path/to/your/mp3player_env/bin/python /path/to/your/project/main.py
    Restart=on-failure

    [Install]
    WantedBy=multi-user.target
    ```

    Replace `/path/to/your/project` with the actual path to your MP3 Player project directory and `/path/to/your/mp3player_env` with the path to your Python virtual environment.

3. **Reload Systemd**:

    After saving and closing the file, reload systemd to apply the new service.

    ```bash
    sudo systemctl daemon-reload
    ```

### Enabling and Starting the Service

1. **Enable the Service**:

    Enable the service to start on boot.

    ```bash
    sudo systemctl enable mp3player.service
    ```

2. **Start the Service**:

    Start the service immediately.

    ```bash
    sudo systemctl start mp3player.service
    ```

### Managing the Service

- **Check Status**:
  To check the status of the service, use:
  ```bash
  sudo systemctl status mp3player.service
  ```

- **Stop Service**:
  To stop the service:
  ```bash
  sudo systemctl stop mp3player.service
  ```

- **Restart Service**:
  To restart the service after making changes:
  ```bash
  sudo systemctl restart mp3player.service
  ```

### Troubleshooting

If you encounter issues, checking the service status and logs can be helpful:

```bash
journalctl -u mp3player.service
```

This will display the logs for the MP3 Player service and can provide insights into any problems.

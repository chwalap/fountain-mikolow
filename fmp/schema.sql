DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS schedule;
DROP TABLE IF EXISTS playlists;
DROP TABLE IF EXISTS tracks;
DROP TABLE IF EXISTS playlist_tracks;
DROP TABLE IF EXISTS settings;


CREATE TABLE  users (
  id INTEGER PRIMARY KEY,
  username TEXT NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE schedule (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  type TEXT NOT NULL,
  time TEXT NOT NULL,
  date TEXT NOT NULL,
  track_id INTEGER,
  FOREIGN KEY (track_id) REFERENCES tracks (id)
);

CREATE TABLE playlists (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE tracks (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  file_path TEXT NOT NULL,
  duration INT NOT NULL
);

CREATE TABLE playlist_tracks (
  playlist_id INTEGER,
  track_id INTEGER,
  FOREIGN KEY (playlist_id) REFERENCES playlists (id),
  FOREIGN KEY (track_id) REFERENCES tracks (id)
);

CREATE TABLE settings (
  key TEXT PRIMARY KEY,
  value TEXT
);

INSERT INTO settings (key, value) VALUES ('audio_output', '');
INSERT INTO settings (key, value) VALUES ('player_always_on_top', 'True');
INSERT INTO settings (key, value) VALUES ('working_from', '08:00');
INSERT INTO settings (key, value) VALUES ('working_to', '22:00');

/* todo: test if this works */
INSERT INTO users(username, password) VALUES ('admin', 'scrypt:32768:8:1$TX2xdiZ9hq4yrVlE$1fe6800a32dbd368d57b51e012abc7da679b581be170b412a7249a4aad431b051ee15872bbb908c4e49ed4d236031751097e6fc07f973be79f7f7c3fff2ccde1')

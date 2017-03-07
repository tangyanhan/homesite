DELETE FROM video_video;
DELETE FROM sqlite_sequence WHERE name='video_video';
DELETE FROM video_keywordcount;
DELETE FROM sqlite_sequence WHERE name='video_keywordcount';
DELETE FROM video_keywordpathhash;
DELETE FROM sqlite_sequence WHERE name='video_keywordpathhash';
VACUUM;


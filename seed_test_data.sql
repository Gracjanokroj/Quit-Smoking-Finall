
SET FOREIGN_KEY_CHECKS = 0;


INSERT IGNORE INTO quit_smoking_webapp_cravinglevel (id, name) VALUES
  (1, 'Low'),
  (2, 'Medium'),
  (3, 'High');


INSERT IGNORE INTO quit_smoking_webapp_emotion (id, name) VALUES
  (1, 'Stress'),
  (2, 'Boredom'),
  (3, 'Anxiety'),
  (4, 'Happiness'),
  (5, 'Frustration'),
  (6, 'Sadness');


INSERT IGNORE INTO quit_smoking_webapp_situation (id, name) VALUES
  (1, 'Work'),
  (2, 'After meal'),
  (3, 'Coffee'),
  (4, 'Driving'),
  (5, 'Party'),
  (6, 'Watching TV');

-- ── Users ───────────────────────────────────────────────────
-- Passwords (plain):
--   user_1 → User1@Test99!
--   user_2 → User2@Test99!
--   user_3 → User3@Test99!
--   user_4 → User4@Test99!
--   user_5 → User5@Test99!

DELETE FROM auth_user WHERE username IN (
  'user_1','user_2','user_3','user_4','user_5'
);

INSERT INTO auth_user
  (id, password, last_login, is_superuser, username, first_name, last_name,
   email, is_staff, is_active, date_joined)
VALUES
  (101,
   'pbkdf2_sha256$600000$9ceoFPp6Jr0Qc3yPBbUoss$lGU9Nwy/h6MPgT+WFSgyscVD5bhoU2yjStHbPITNZts=',
   NULL, 0, 'user_1', '', '', 'user1@test.com',
   0, 1, '2026-03-15 10:00:00'),
  (102,
   'pbkdf2_sha256$600000$ej6hNJJHFImcQqTyRlwTeo$TB9wvn74qS/q6mrbWkzxCK8Jv4owL/f7pfhBCIgRMIU=',
   NULL, 0, 'user_2', '', '', 'user2@test.com',
   0, 1, '2026-03-15 10:00:00'),
  (103,
   'pbkdf2_sha256$600000$bfmIKOioyLrJynLeX3vBR3$yiTrBRnQdPiSK/NDt+IjCaMh4n+OYWfNNcw2K70vGlE=',
   NULL, 0, 'user_3', '', '', 'user3@test.com',
   0, 1, '2026-03-15 10:00:00'),
  (104,
   'pbkdf2_sha256$600000$5pywVtmnSwhDjijzsS58qp$wZfnodXz6tu77wENydveZug6nDnHo0DVHhdJ247MAbE=',
   NULL, 0, 'user_4', '', '', 'user4@test.com',
   0, 1, '2026-03-15 10:00:00'),
  (105,
   'pbkdf2_sha256$600000$XXv8BcivqqcT14t32pZy2c$Bafa6pl6WPdSijC/hLJTsT7jDEZiiYVJ2497/+Mg1eg=',
   NULL, 0, 'user_5', '', '', 'user5@test.com',
   0, 1, '2026-03-15 10:00:00');


DELETE FROM quit_smoking_webapp_userprofile WHERE user_id IN (101,102,103,104,105);

INSERT INTO quit_smoking_webapp_userprofile
  (user_id, cigarettes_per_day, pack_price, reason_to_quit, ranking_consent, updated_date)
VALUES
  (101, 10, 18.00, 'I want to improve my health and run without getting tired', 1, NULL),
  (102, 25, 15.00, 'Too expensive and my doctor told me to stop', 1, NULL),
  (103,  5, 20.00, 'For my children and to feel better every day', 1, NULL),
  (104, 15, 16.00, 'My family is asking me to quit for years', 1, NULL),
  (105, 12, 18.00, 'Save money for a holiday trip', 0, NULL);


DELETE FROM quit_smoking_webapp_dailylog WHERE user_id IN (101,102,103,104,105);


INSERT INTO quit_smoking_webapp_dailylog
  (user_id, cigarettes_smoked, smoke_free_day, first_cigarette_time, craving_level_id, created_at)
VALUES
  (101,8,0,'08:30:00',2,'2026-03-22 12:00:00'),
  (101,7,0,'08:45:00',2,'2026-03-23 12:00:00'),
  (101,0,1,NULL,1,'2026-03-24 12:00:00'),
  (101,6,0,'09:00:00',2,'2026-03-25 12:00:00'),
  (101,5,0,'09:15:00',1,'2026-03-26 12:00:00'),
  (101,0,1,NULL,1,'2026-03-27 12:00:00'),
  (101,0,1,NULL,1,'2026-03-28 12:00:00'),
  (101,4,0,'09:30:00',1,'2026-03-29 12:00:00'),
  (101,5,0,'09:00:00',2,'2026-03-30 12:00:00'),
  (101,0,1,NULL,1,'2026-03-31 12:00:00'),
  (101,3,0,'10:00:00',1,'2026-04-01 12:00:00'),
  (101,4,0,'09:45:00',1,'2026-04-02 12:00:00'),
  (101,0,1,NULL,1,'2026-04-03 12:00:00'),
  (101,0,1,NULL,1,'2026-04-04 12:00:00'),
  (101,0,1,NULL,1,'2026-04-05 12:00:00'),
  (101,3,0,'10:15:00',1,'2026-04-06 12:00:00'),
  (101,2,0,'10:30:00',1,'2026-04-07 12:00:00'),
  (101,0,1,NULL,1,'2026-04-08 12:00:00'),
  (101,0,1,NULL,1,'2026-04-09 12:00:00'),
  (101,2,0,'11:00:00',1,'2026-04-10 12:00:00'),
  (101,0,1,NULL,1,'2026-04-11 12:00:00'),
  (101,0,1,NULL,1,'2026-04-12 12:00:00'),
  (101,0,1,NULL,1,'2026-04-13 12:00:00'),
  (101,0,1,NULL,1,'2026-04-14 12:00:00'),
  (101,1,0,'11:30:00',1,'2026-04-15 12:00:00'),
  (101,0,1,NULL,1,'2026-04-16 12:00:00'),
  (101,0,1,NULL,1,'2026-04-17 12:00:00'),
  (101,0,1,NULL,1,'2026-04-18 12:00:00'),
  (101,0,1,NULL,1,'2026-04-19 12:00:00'),
  (101,0,1,NULL,1,'2026-04-20 12:00:00');


INSERT INTO quit_smoking_webapp_dailylog
  (user_id, cigarettes_smoked, smoke_free_day, first_cigarette_time, craving_level_id, created_at)
VALUES
  (102,22,0,'07:00:00',3,'2026-03-22 12:00:00'),
  (102,20,0,'07:10:00',3,'2026-03-23 12:00:00'),
  (102,25,0,'06:50:00',3,'2026-03-24 12:00:00'),
  (102,18,0,'07:30:00',2,'2026-03-25 12:00:00'),
  (102,0,1,NULL,2,'2026-03-26 12:00:00'),
  (102,15,0,'08:00:00',2,'2026-03-27 12:00:00'),
  (102,20,0,'07:00:00',3,'2026-03-28 12:00:00'),
  (102,22,0,'07:15:00',3,'2026-03-29 12:00:00'),
  (102,19,0,'07:30:00',3,'2026-03-30 12:00:00'),
  (102,17,0,'08:00:00',2,'2026-03-31 12:00:00'),
  (102,0,1,NULL,2,'2026-04-01 12:00:00'),
  (102,0,1,NULL,2,'2026-04-02 12:00:00'),
  (102,14,0,'08:30:00',2,'2026-04-03 12:00:00'),
  (102,18,0,'07:45:00',3,'2026-04-04 12:00:00'),
  (102,20,0,'07:00:00',3,'2026-04-05 12:00:00'),
  (102,16,0,'08:00:00',2,'2026-04-06 12:00:00'),
  (102,0,1,NULL,2,'2026-04-07 12:00:00'),
  (102,12,0,'09:00:00',2,'2026-04-08 12:00:00'),
  (102,15,0,'08:30:00',2,'2026-04-09 12:00:00'),
  (102,18,0,'07:45:00',3,'2026-04-10 12:00:00'),
  (102,14,0,'08:15:00',2,'2026-04-11 12:00:00'),
  (102,0,1,NULL,2,'2026-04-12 12:00:00'),
  (102,10,0,'09:30:00',2,'2026-04-13 12:00:00'),
  (102,12,0,'09:00:00',2,'2026-04-14 12:00:00'),
  (102,14,0,'08:45:00',2,'2026-04-15 12:00:00'),
  (102,0,1,NULL,1,'2026-04-16 12:00:00'),
  (102,8,0,'10:00:00',1,'2026-04-17 12:00:00'),
  (102,10,0,'09:30:00',2,'2026-04-18 12:00:00'),
  (102,12,0,'09:00:00',2,'2026-04-19 12:00:00'),
  (102,8,0,'10:15:00',1,'2026-04-20 12:00:00');


INSERT INTO quit_smoking_webapp_dailylog
  (user_id, cigarettes_smoked, smoke_free_day, first_cigarette_time, craving_level_id, created_at)
VALUES
  (103,0,1,NULL,1,'2026-03-22 12:00:00'),
  (103,0,1,NULL,1,'2026-03-23 12:00:00'),
  (103,2,0,'14:00:00',1,'2026-03-24 12:00:00'),
  (103,0,1,NULL,1,'2026-03-25 12:00:00'),
  (103,0,1,NULL,1,'2026-03-26 12:00:00'),
  (103,0,1,NULL,1,'2026-03-27 12:00:00'),
  (103,0,1,NULL,1,'2026-03-28 12:00:00'),
  (103,1,0,'18:00:00',1,'2026-03-29 12:00:00'),
  (103,0,1,NULL,1,'2026-03-30 12:00:00'),
  (103,0,1,NULL,1,'2026-03-31 12:00:00'),
  (103,0,1,NULL,1,'2026-04-01 12:00:00'),
  (103,0,1,NULL,1,'2026-04-02 12:00:00'),
  (103,0,1,NULL,1,'2026-04-03 12:00:00'),
  (103,0,1,NULL,1,'2026-04-04 12:00:00'),
  (103,0,1,NULL,1,'2026-04-05 12:00:00'),
  (103,1,0,'19:00:00',1,'2026-04-06 12:00:00'),
  (103,0,1,NULL,1,'2026-04-07 12:00:00'),
  (103,0,1,NULL,1,'2026-04-08 12:00:00'),
  (103,0,1,NULL,1,'2026-04-09 12:00:00'),
  (103,0,1,NULL,1,'2026-04-10 12:00:00'),
  (103,0,1,NULL,1,'2026-04-11 12:00:00'),
  (103,0,1,NULL,1,'2026-04-12 12:00:00'),
  (103,0,1,NULL,1,'2026-04-13 12:00:00'),
  (103,0,1,NULL,1,'2026-04-14 12:00:00'),
  (103,0,1,NULL,1,'2026-04-15 12:00:00'),
  (103,0,1,NULL,1,'2026-04-16 12:00:00'),
  (103,0,1,NULL,1,'2026-04-17 12:00:00'),
  (103,0,1,NULL,1,'2026-04-18 12:00:00'),
  (103,0,1,NULL,1,'2026-04-19 12:00:00'),
  (103,0,1,NULL,1,'2026-04-20 12:00:00');

INSERT INTO quit_smoking_webapp_dailylog
  (user_id, cigarettes_smoked, smoke_free_day, first_cigarette_time, craving_level_id, created_at)
VALUES
  (104,12,0,'08:00:00',2,'2026-03-22 12:00:00'),
  (104,0,1,NULL,1,'2026-03-23 12:00:00'),
  (104,18,0,'07:00:00',3,'2026-03-24 12:00:00'),
  (104,5,0,'10:00:00',1,'2026-03-25 12:00:00'),
  (104,0,1,NULL,1,'2026-03-26 12:00:00'),
  (104,0,1,NULL,1,'2026-03-27 12:00:00'),
  (104,15,0,'07:30:00',3,'2026-03-28 12:00:00'),
  (104,10,0,'08:30:00',2,'2026-03-29 12:00:00'),
  (104,0,1,NULL,1,'2026-03-30 12:00:00'),
  (104,20,0,'07:00:00',3,'2026-03-31 12:00:00'),
  (104,8,0,'09:00:00',2,'2026-04-01 12:00:00'),
  (104,0,1,NULL,1,'2026-04-02 12:00:00'),
  (104,0,1,NULL,1,'2026-04-03 12:00:00'),
  (104,12,0,'08:15:00',2,'2026-04-04 12:00:00'),
  (104,0,1,NULL,1,'2026-04-05 12:00:00'),
  (104,6,0,'09:30:00',2,'2026-04-06 12:00:00'),
  (104,0,1,NULL,1,'2026-04-07 12:00:00'),
  (104,0,1,NULL,1,'2026-04-08 12:00:00'),
  (104,14,0,'07:45:00',3,'2026-04-09 12:00:00'),
  (104,0,1,NULL,1,'2026-04-10 12:00:00'),
  (104,5,0,'10:30:00',1,'2026-04-11 12:00:00'),
  (104,0,1,NULL,1,'2026-04-12 12:00:00'),
  (104,0,1,NULL,1,'2026-04-13 12:00:00'),
  (104,8,0,'09:00:00',2,'2026-04-14 12:00:00'),
  (104,0,1,NULL,1,'2026-04-15 12:00:00'),
  (104,0,1,NULL,1,'2026-04-16 12:00:00'),
  (104,3,0,'11:00:00',1,'2026-04-17 12:00:00'),
  (104,0,1,NULL,1,'2026-04-18 12:00:00'),
  (104,0,1,NULL,1,'2026-04-19 12:00:00'),
  (104,4,0,'10:45:00',1,'2026-04-20 12:00:00');

INSERT INTO quit_smoking_webapp_dailylog
  (user_id, cigarettes_smoked, smoke_free_day, first_cigarette_time, craving_level_id, created_at)
VALUES
  (105,10,0,'09:00:00',2,'2026-03-22 12:00:00'),
  (105,9,0,'09:10:00',2,'2026-03-23 12:00:00'),
  (105,11,0,'08:50:00',2,'2026-03-24 12:00:00'),
  (105,8,0,'09:20:00',2,'2026-03-25 12:00:00'),
  (105,0,1,NULL,1,'2026-03-26 12:00:00'),
  (105,7,0,'09:30:00',1,'2026-03-27 12:00:00'),
  (105,8,0,'09:15:00',2,'2026-03-28 12:00:00'),
  (105,0,1,NULL,1,'2026-03-29 12:00:00'),
  (105,6,0,'09:45:00',1,'2026-03-30 12:00:00'),
  (105,7,0,'09:30:00',1,'2026-03-31 12:00:00'),
  (105,5,0,'10:00:00',1,'2026-04-01 12:00:00'),
  (105,0,1,NULL,1,'2026-04-02 12:00:00'),
  (105,0,1,NULL,1,'2026-04-03 12:00:00'),
  (105,6,0,'09:50:00',1,'2026-04-04 12:00:00'),
  (105,4,0,'10:15:00',1,'2026-04-05 12:00:00'),
  (105,0,1,NULL,1,'2026-04-06 12:00:00'),
  (105,5,0,'10:00:00',1,'2026-04-07 12:00:00'),
  (105,3,0,'10:30:00',1,'2026-04-08 12:00:00'),
  (105,0,1,NULL,1,'2026-04-09 12:00:00'),
  (105,4,0,'10:45:00',1,'2026-04-10 12:00:00'),
  (105,0,1,NULL,1,'2026-04-11 12:00:00'),
  (105,0,1,NULL,1,'2026-04-12 12:00:00'),
  (105,3,0,'11:00:00',1,'2026-04-13 12:00:00'),
  (105,2,0,'11:30:00',1,'2026-04-14 12:00:00'),
  (105,0,1,NULL,1,'2026-04-15 12:00:00'),
  (105,0,1,NULL,1,'2026-04-16 12:00:00'),
  (105,2,0,'11:45:00',1,'2026-04-17 12:00:00'),
  (105,0,1,NULL,1,'2026-04-18 12:00:00'),
  (105,1,0,'12:00:00',1,'2026-04-19 12:00:00'),
  (105,0,1,NULL,1,'2026-04-20 12:00:00');




INSERT INTO quit_smoking_webapp_dailylogemotion (daily_log_id, emotion_id, custom_emotion)
SELECT dl.id, 1, '' FROM quit_smoking_webapp_dailylog dl
WHERE dl.user_id = 101 AND dl.smoke_free_day = 0;

INSERT INTO quit_smoking_webapp_dailylogemotion (daily_log_id, emotion_id, custom_emotion)
SELECT dl.id, 2, '' FROM quit_smoking_webapp_dailylog dl
WHERE dl.user_id = 101 AND dl.smoke_free_day = 0;


INSERT INTO quit_smoking_webapp_dailylogemotion (daily_log_id, emotion_id, custom_emotion)
SELECT dl.id, 1, '' FROM quit_smoking_webapp_dailylog dl
WHERE dl.user_id = 102 AND dl.smoke_free_day = 0;

INSERT INTO quit_smoking_webapp_dailylogemotion (daily_log_id, emotion_id, custom_emotion)
SELECT dl.id, 5, '' FROM quit_smoking_webapp_dailylog dl
WHERE dl.user_id = 102 AND dl.smoke_free_day = 0;

INSERT INTO quit_smoking_webapp_dailylogemotion (daily_log_id, emotion_id, custom_emotion)
SELECT dl.id, 3, '' FROM quit_smoking_webapp_dailylog dl
WHERE dl.user_id = 103 AND dl.smoke_free_day = 0;

INSERT INTO quit_smoking_webapp_dailylogemotion (daily_log_id, emotion_id, custom_emotion)
SELECT dl.id, 2, '' FROM quit_smoking_webapp_dailylog dl
WHERE dl.user_id = 104 AND dl.smoke_free_day = 0;

INSERT INTO quit_smoking_webapp_dailylogemotion (daily_log_id, emotion_id, custom_emotion)
SELECT dl.id, 6, '' FROM quit_smoking_webapp_dailylog dl
WHERE dl.user_id = 104 AND dl.smoke_free_day = 0;


INSERT INTO quit_smoking_webapp_dailylogemotion (daily_log_id, emotion_id, custom_emotion)
SELECT dl.id, 1, '' FROM quit_smoking_webapp_dailylog dl
WHERE dl.user_id = 105 AND dl.smoke_free_day = 0;

INSERT INTO quit_smoking_webapp_dailylogemotion (daily_log_id, emotion_id, custom_emotion)
SELECT dl.id, 3, '' FROM quit_smoking_webapp_dailylog dl
WHERE dl.user_id = 105 AND dl.smoke_free_day = 0;


INSERT INTO quit_smoking_webapp_dailylogsituation (daily_log_id, situation_id, custom_situation)
SELECT dl.id, 1, '' FROM quit_smoking_webapp_dailylog dl
WHERE dl.user_id = 101 AND dl.smoke_free_day = 0;

INSERT INTO quit_smoking_webapp_dailylogsituation (daily_log_id, situation_id, custom_situation)
SELECT dl.id, 3, '' FROM quit_smoking_webapp_dailylog dl
WHERE dl.user_id = 101 AND dl.smoke_free_day = 0;

INSERT INTO quit_smoking_webapp_dailylogsituation (daily_log_id, situation_id, custom_situation)
SELECT dl.id, 1, '' FROM quit_smoking_webapp_dailylog dl
WHERE dl.user_id = 102 AND dl.smoke_free_day = 0;

INSERT INTO quit_smoking_webapp_dailylogsituation (daily_log_id, situation_id, custom_situation)
SELECT dl.id, 2, '' FROM quit_smoking_webapp_dailylog dl
WHERE dl.user_id = 102 AND dl.smoke_free_day = 0;

INSERT INTO quit_smoking_webapp_dailylogsituation (daily_log_id, situation_id, custom_situation)
SELECT dl.id, 5, '' FROM quit_smoking_webapp_dailylog dl
WHERE dl.user_id = 103 AND dl.smoke_free_day = 0;


INSERT INTO quit_smoking_webapp_dailylogsituation (daily_log_id, situation_id, custom_situation)
SELECT dl.id, 4, '' FROM quit_smoking_webapp_dailylog dl
WHERE dl.user_id = 104 AND dl.smoke_free_day = 0;

INSERT INTO quit_smoking_webapp_dailylogsituation (daily_log_id, situation_id, custom_situation)
SELECT dl.id, 6, '' FROM quit_smoking_webapp_dailylog dl
WHERE dl.user_id = 104 AND dl.smoke_free_day = 0;

INSERT INTO quit_smoking_webapp_dailylogsituation (daily_log_id, situation_id, custom_situation)
SELECT dl.id, 3, '' FROM quit_smoking_webapp_dailylog dl
WHERE dl.user_id = 105 AND dl.smoke_free_day = 0;

INSERT INTO quit_smoking_webapp_dailylogsituation (daily_log_id, situation_id, custom_situation)
SELECT dl.id, 2, '' FROM quit_smoking_webapp_dailylog dl
WHERE dl.user_id = 105 AND dl.smoke_free_day = 0;

SET FOREIGN_KEY_CHECKS = 1;


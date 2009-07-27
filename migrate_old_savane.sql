-- USE savane;

-- Import all users except for the 'None' user (#100)
INSERT INTO auth_user
    (id, username, first_name, last_name, email,
     password, last_login, date_joined, is_active,
     is_superuser, is_staff)
  SELECT user_id, user_name, realname, '', email,
      CONCAT('md5$$', user_pw), now(), FROM_UNIXTIME(add_date), status='A',
      0, 0
    FROM savane_old.user
    WHERE user_id != 100;

-- Import all extended information except for the 'None' user (#100)
INSERT INTO my_extendeduser
    (user_ptr_id, status, spamscore, authorized_keys,
     authorized_keys_count, people_view_skills, people_resume,
     timezone, theme, email_hide, gpg_key, gpg_key_count)
  SELECT user_id, status, spamscore, authorized_keys,
      authorized_keys_count, people_view_skills,
      people_resume, timezone, theme,
      email_hide, gpg_key, gpg_key_count
    FROM savane_old.user
    WHERE user_id != 100;

-- Some clean-up is done on the savane_old database.  It may sound
-- better to leave savane_old read-only, but at the same time this
-- means we can experiment the clean-ups on live "old savane" installs
-- before the migration.


-- Import all users except for the 'None' user (#100)
-- Get rid of duplicates (old mysql/php/savane bug?)
USE savane_old;
DELETE FROM user
  WHERE user_id IN (
    SELECT user_id FROM (
      SELECT B.user_id FROM user A, user B
        WHERE A.user_id < B.user_id AND A.user_name = B.user_name
      ) AS temp
    );
USE savane;
-- Actual import
-- Using a heuristic to split realname in firstname/lastname; we can't
-- place all in firstname because it's 30 chars long, while realname
-- is 32 chars long :/
TRUNCATE auth_user;
INSERT INTO auth_user
    (id, username, first_name, last_name, email,
     password, last_login, date_joined, is_active,
     is_superuser, is_staff)
  SELECT user_id, user_name,
      SUBSTRING_INDEX(realname, ' ', 1),
      TRIM(REPLACE(realname, SUBSTRING_INDEX(realname, ' ', 1), '')),
      email,
      CONCAT('md5$$', user_pw), now(), FROM_UNIXTIME(add_date), status='A',
      0, 0
    FROM savane_old.user
    WHERE savane_old.user.user_id != 100;

-- Import all extended information except for the 'None' user (#100)
TRUNCATE svmain_extendeduser;
INSERT INTO svmain_extendeduser
    (user_ptr_id, status, spamscore, authorized_keys,
     authorized_keys_count, people_view_skills, people_resume,
     timezone, theme, email_hide, gpg_key, gpg_key_count)
  SELECT user_id, status, spamscore, IFNULL(authorized_keys, ''),
      authorized_keys_count, people_view_skills,
      people_resume, IFNULL(timezone, ''), IFNULL(theme, ''),
      IFNULl(email_hide, 0), IFNULL(gpg_key, ''), gpg_key_count
    FROM savane_old.user
    WHERE savane_old.user.user_id != 100;

-- Import group configurations
-- type_id -> id
TRUNCATE svmain_groupconfiguration;
INSERT INTO svmain_groupconfiguration
    (id, name, description, base_host,
     mailing_list_address, mailing_list_virtual_host, mailing_list_format,
     can_use_homepage, can_use_download, can_use_cvs, can_use_arch, can_use_svn, can_use_git, can_use_hg,
     can_use_bzr, can_use_license, can_use_devel_status, can_use_mailing_list,
     can_use_patch, can_use_task, can_use_news, can_use_support, can_use_bug,
     is_menu_configurable_homepage,
     is_menu_configurable_download,
     is_menu_configurable_support,
     is_menu_configurable_mail,
     is_menu_configurable_cvs,
     is_menu_configurable_cvs_viewcvs,
     is_menu_configurable_cvs_viewcvs_homepage,
     is_menu_configurable_arch,
     is_menu_configurable_arch_viewcvs,
     is_menu_configurable_svn,
     is_menu_configurable_svn_viewcvs,
     is_menu_configurable_git,
     is_menu_configurable_git_viewcvs,
     is_menu_configurable_hg,
     is_menu_configurable_hg_viewcvs,
     is_menu_configurable_bzr,
     is_menu_configurable_bzr_viewcvs,
     is_menu_configurable_bugs,
     is_menu_configurable_task,
     is_menu_configurable_patch,
     is_menu_configurable_extralink_documentation,
     is_configurable_download_dir,
     homepage_scm,
     dir_type_cvs,
     dir_type_arch,
     dir_type_svn,
     dir_type_git,
     dir_type_hg,
     dir_type_bzr,
     dir_type_homepage,
     dir_type_download,
     dir_homepage,
     dir_cvs,
     dir_arch,
     dir_svn,
     dir_git,
     dir_hg,
     dir_bzr,
     dir_download,
     url_homepage,
     url_cvs_viewcvs_homepage,
     url_cvs_viewcvs,
     url_arch_viewcvs,
     url_svn_viewcvs,
     url_git_viewcvs,
     url_hg_viewcvs,
     url_bzr_viewcvs,
     url_download,
     url_mailing_list_listinfo,
     url_mailing_list_subscribe,
     url_mailing_list_unsubscribe,
     url_mailing_list_archives,
     url_mailing_list_archives_private,
     url_mailing_list_admin,
     url_extralink_documentation)
  SELECT type_id, name, description, base_host,
      mailing_list_address, mailing_list_virtual_host, mailing_list_format,
      can_use_homepage, can_use_download, can_use_cvs, can_use_arch, can_use_svn, can_use_git, can_use_hg,
      can_use_bzr, can_use_license, can_use_devel_status, can_use_mailing_list,
      can_use_patch, can_use_task, can_use_news, can_use_support, can_use_bug,
      is_menu_configurable_homepage,
      is_menu_configurable_download,
      is_menu_configurable_support,
      is_menu_configurable_mail,
      is_menu_configurable_cvs,
      is_menu_configurable_cvs_viewcvs,
      is_menu_configurable_cvs_viewcvs_homepage,
      is_menu_configurable_arch,
      is_menu_configurable_arch_viewcvs,
      is_menu_configurable_svn,
      is_menu_configurable_svn_viewcvs,
      is_menu_configurable_git,
      is_menu_configurable_git_viewcvs,
      is_menu_configurable_hg,
      is_menu_configurable_hg_viewcvs,
      is_menu_configurable_bzr,
      is_menu_configurable_bzr_viewcvs,
      is_menu_configurable_bugs,
      is_menu_configurable_task,
      is_menu_configurable_patch,
      is_menu_configurable_extralink_documentation,
      is_configurable_download_dir,
      homepage_scm,
      dir_type_cvs,
      dir_type_arch,
      dir_type_svn,
      dir_type_git,
      dir_type_hg,
      dir_type_bzr,
      dir_type_homepage,
      dir_type_download,
      dir_homepage,
      dir_cvs,
      dir_arch,
      dir_svn,
      dir_git,
      dir_hg,
      dir_bzr,
      dir_download,
      url_homepage,
      url_cvs_viewcvs_homepage,
      url_cvs_viewcvs,
      url_arch_viewcvs,
      url_svn_viewcvs,
      url_git_viewcvs,
      url_hg_viewcvs,
      url_bzr_viewcvs,
      url_download,
      url_mailing_list_listinfo,
      url_mailing_list_subscribe,
      url_mailing_list_unsubscribe,
      url_mailing_list_archives,
      url_mailing_list_archives_private,
      url_mailing_list_admin,
      url_extralink_documentation
    FROM savane_old.group_type;


-- Import groups
-- id <- group_id
-- name <- unix_group_name
TRUNCATE auth_group;
INSERT INTO auth_group
    (id, name)
  SELECT group_id, unix_group_name
    FROM savane_old.groups
    WHERE savane_old.groups.group_id != 100;

-- Import license/devel_status
-- ./manage.py loaddata savane/svmain/fixtures/license.yaml
-- ./manage.py loaddata savane/svmain/fixtures/developmentstatus.yaml

-- Import groups
-- group_ptr_id <- group_id
-- full_name <- group_name
-- license_id <- license+1 (django counts from 1, not from 0)
-- devel_status_id <- devel_status+1 (django counts from 1, not from 0)
-- type_id <- type
-- register_time <- FROM_UNIXTIME(register_time)
--
-- Using LEFT JOIN so that if the license isn't known, the project is
-- not ignored (with license_id=NULL).
-- Using X+0 to convert empty string to 0 without warning
TRUNCATE svmain_extendedgroup;
INSERT INTO svmain_extendedgroup
    (group_ptr_id, full_name, license_id, devel_status_id, type_id,
     register_time,
     is_public,
     status,
     short_description,
     long_description,
     license_other,
     register_purpose,
     required_software,
     other_comments,
     registered_gpg_keys,
     use_homepage,
     use_mail,
     use_patch,
     use_task,
     use_cvs,
     use_arch,
     use_svn,
     use_git,
     use_hg,
     use_bzr,
     use_news,
     use_support,
     use_download,
     use_bugs,
     use_extralink_documentation,
     url_homepage,
     url_download,
     url_support,
     url_mail,
     url_cvs,
     url_cvs_viewcvs,
     url_cvs_viewcvs_homepage,
     url_arch,
     url_arch_viewcvs,
     url_svn,
     url_svn_viewcvs,
     url_git,
     url_git_viewcvs,
     url_hg,
     url_hg_viewcvs,
     url_bzr,
     url_bzr_viewcvs,
     url_bugs,
     url_task,
     url_patch,
     url_extralink_documentation)
  SELECT group_id, group_name, svmain_license.id, IFNULL(devel_status+1, 8), type,
      FROM_UNIXTIME(register_time),
      is_public,
      status,
      IFNULL(short_description, ''),
      IFNULL(long_description, ''),
      IFNULL(license_other, ''),
      IFNULL(register_purpose, ''),
      IFNULL(required_software, ''),
      IFNULL(other_comments, ''),
      IFNULL(registered_gpg_keys, ''),
      IFNULL(use_homepage+0, 0),
      IFNULL(use_mail+0, 0),
      IFNULL(use_patch+0, 0),
      IFNULL(use_task+0, 0),
      IFNULL(use_cvs+0, 0),
      IFNULL(use_arch+0, 0),
      IFNULL(use_svn+0, 0),
      IFNULL(use_git+0, 0),
      IFNULL(use_hg+0, 0),
      IFNULL(use_bzr+0, 0),
      IFNULL(use_news+0, 0),
      IFNULL(use_support+0, 0),
      IFNULL(use_download+0, 0),
      IFNULL(use_bugs+0, 0),
      IFNULL(use_extralink_documentation+0, 0),
      IFNULL(url_homepage, ''),
      IFNULL(url_download, ''),
      IFNULL(url_support, ''),
      IFNULL(url_mail, ''),
      IFNULL(url_cvs, ''),
      IFNULL(url_cvs_viewcvs, ''),
      IFNULL(url_cvs_viewcvs_homepage, ''),
      IFNULL(url_arch, ''),
      IFNULL(url_arch_viewcvs, ''),
      IFNULL(url_svn, ''),
      IFNULL(url_svn_viewcvs, ''),
      IFNULL(url_git, ''),
      IFNULL(url_git_viewcvs, ''),
      IFNULL(url_hg, ''),
      IFNULL(url_hg_viewcvs, ''),
      IFNULL(url_bzr, ''),
      IFNULL(url_bzr_viewcvs, ''),
      IFNULL(url_bugs, ''),
      IFNULL(url_task, ''),
      IFNULL(url_patch, ''),
      IFNULL(url_extralink_documentation, '')
    FROM savane_old.groups LEFT JOIN savane.svmain_license ON savane_old.groups.license = savane.svmain_license.slug
    WHERE savane_old.groups.group_id != 100;

-- Import users<->groups relationships
-- Get rid of duplicates
USE savane_old;
-- Give priority to non-pending memberships
DELETE FROM user_group
  WHERE user_group_id IN (
    SELECT user_group_id FROM (
      SELECT B.user_group_id FROM user_group A, user_group B
        WHERE A.admin_flags <> 'P' AND B.admin_flags = 'P'
          AND A.user_id = B.user_id AND A.group_id = B.group_id
      ) AS temp
    );
-- Delete other duplicates, give priority to the first one
DELETE FROM user_group
  WHERE user_group_id IN (
    SELECT user_group_id FROM (
      SELECT B.user_group_id FROM user_group A, user_group B
        WHERE A.user_group_id < B.user_group_id
          AND A.user_id = B.user_id AND A.group_id = B.group_id
      ) AS temp
    );
-- Get rid of ghost relationships (deleted group)
DELETE FROM user_group
  WHERE group_id IN (
    SELECT group_id FROM (
      SELECT user_group.group_id
        FROM user_group
          LEFT JOIN groups ON user_group.group_id = groups.group_id
        WHERE groups.group_id IS NULL
      ) AS temp
    );
-- Get rid of ghost relationships (deleted user)
DELETE FROM user_group WHERE user_id IN (
  SELECT user_id FROM (
    SELECT user_group.user_id
      FROM user_group
        LEFT JOIN user ON user_group.user_id = user.user_id
      WHERE user.user_id IS NULL
    ) AS temp
  );
USE savane;
-- Actual import
TRUNCATE auth_user_groups;
INSERT INTO auth_user_groups
    (user_id, group_id)
  SELECT user_id, group_id
    FROM savane_old.user_group;
TRUNCATE svmain_membership;
INSERT INTO svmain_membership
    (user_id, group_id, admin_flags, onduty)
  SELECT user_id, group_id, admin_flags, onduty
    FROM savane_old.user_group;
-- Set members of 'administration' as superusers
-- TODO: get the supergroup name from the old Savane configuration
UPDATE auth_user SET is_staff=1, is_superuser=1
  WHERE id IN (
    SELECT user_id
    FROM auth_user_groups JOIN auth_group ON auth_user_groups.group_id = auth_group.id
    WHERE auth_group.name='administration'
  );

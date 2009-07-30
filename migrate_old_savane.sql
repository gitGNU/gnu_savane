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
TRUNCATE auth_user;
INSERT INTO auth_user
    (id, username, first_name, last_name, email,
     password, last_login, date_joined, is_active,
     is_superuser, is_staff)
  SELECT user_id, user_name, realname, '', email,
      CONCAT('md5$$', user_pw), now(), FROM_UNIXTIME(add_date), status='A',
      0, 0
    FROM savane_old.user
    WHERE savane_old.user.user_id != 100;

-- Import all extended information except for the 'None' user (#100)
-- (X or 0) means 'if V==NULL then 0 else V'
TRUNCATE svmain_extendeduser;
INSERT INTO svmain_extendeduser
    (user_ptr_id, status, spamscore, authorized_keys,
     authorized_keys_count, people_view_skills, people_resume,
     timezone, theme, email_hide, gpg_key, gpg_key_count)
  SELECT user_id, status, spamscore, authorized_keys,
      authorized_keys_count, people_view_skills,
      people_resume, timezone, theme,
      (email_hide or 0), gpg_key, gpg_key_count
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
  SELECT group_id, group_name, svmain_license.id, devel_status+1, type,
      FROM_UNIXTIME(register_time),
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
      url_extralink_documentation
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

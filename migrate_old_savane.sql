-- Convert old Savane data to the new version
-- 
-- Copyright (C) 2009, 2010  Sylvain Beucler
-- Copyright (C) 2009  Jonathan Gonzalez V.
--
-- This file is part of Savane.
-- 
-- Savane is free software: you can redistribute it and/or modify it
-- under the terms of the GNU Affero General Public License as
-- published by the Free Software Foundation, either version 3 of the
-- License, or (at your option) any later version.
-- 
-- Savane is distributed in the hope that it will be useful, but
-- WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
-- Affero General Public License for more details.
-- 
-- You should have received a copy of the GNU Affero General Public
-- License along with this program.  If not, see
-- <http://www.gnu.org/licenses/>.

-- This script works on the database from 'savane-cleanup' version
-- with the LATEST DATABASE UPGRADES (check updates/clean-up/).

-- Some clean-up is done on the savane_old database.  It may sound
-- better to leave savane_old read-only, but at the same time this
-- means we can experiment the clean-ups on live "old savane" installs
-- before the migration.

-- Handle dates correctly: FROM_UNIXTIME is mistakenly _timezone-
-- dependent_, so currently the migration script produces valid dates
-- only if it's run in the UTC timezone...
SET time_zone = '+00:00';


----
-- USERS
----

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
TRUNCATE svmain_svuserinfo;
INSERT INTO svmain_svuserinfo
    (user_id, status, spamscore,
     timezone, email_hide, gpg_key, gpg_key_count)
  SELECT user_id, status, spamscore,
      IFNULL(timezone, ''), IFNULL(email_hide, 0), IFNULL(gpg_key, ''), gpg_key_count
    FROM savane_old.user
    WHERE savane_old.user.user_id != 100;

-- view_skills <- people_view_skills
-- resume <- people_resume
TRUNCATE svpeople_userinfo;
INSERT INTO svpeople_userinfo
    (user_id, view_skills, resume)
  SELECT user_id, people_view_skills, people_resume
    FROM savane_old.user
    WHERE savane_old.user.user_id != 100;

-- Import the ssh into the new model, the python code should care about make
-- the proper migration after a login or with a python code
TRUNCATE svmain_sshkey;
INSERT INTO svmain_sshkey
        (user_id, ssh_key)
  SELECT user_id, authorized_keys
  FROM savane_old.user
  WHERE authorized_keys != ''
  and savane_old.user.user_id != 100;


----
-- GROUPS
----

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
--      url_mailing_list_subscribe,
--      url_mailing_list_unsubscribe,
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
--       url_mailing_list_subscribe,
--       url_mailing_list_unsubscribe,
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
-- full_name <- group_name
-- license_id <- license+1 (django counts from 1, not from 0)
-- devel_status_id <- devel_status+1 (django counts from 1, not from 0)
-- type_id <- type
-- register_time <- FROM_UNIXTIME(register_time)
--
-- Using LEFT JOIN so that if the license isn't known, the project is
-- not ignored (with license_id=NULL).
-- Using X+0 to convert empty string to 0 without warning
TRUNCATE svmain_svgroupinfo;
INSERT INTO svmain_svgroupinfo
    (group_id, full_name, license_id, devel_status_id, type_id,
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
  SELECT group_id, group_name, svmain_license.id, IFNULL(IF(devel_status=0,9,devel_status), 7), type,
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
    FROM savane_old.user_group
    WHERE admin_flags <> 'P';
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


----
-- JOBS
----

TRUNCATE svpeople_job;
-- id <- job_id
-- created_by_id <- created_by
-- status <- status_id
INSERT INTO svpeople_job
    (id, group_id, created_by_id, title, description, date, status, category_id)
  SELECT job_id, group_id, created_by, title, description, FROM_UNIXTIME(date), status_id, category_id
    FROM savane_old.people_job;

TRUNCATE svpeople_category;
-- id <- category_id
-- label <- name
-- active <- '1'
INSERT INTO svpeople_category
    (id, label, active)
  SELECT category_id, name, '1'
    FROM savane_old.people_job_category;
# Decapitalize, used in translations
UPDATE svpeople_category SET label='Project manager' WHERE label='Project Manager';
UPDATE svpeople_category SET label='Unix admin' WHERE label='Unix Admin';
UPDATE svpeople_category SET label='Doc writer' WHERE label='Doc Writer';
UPDATE svpeople_category SET label='Support manager' WHERE label='Support Manager';
UPDATE svpeople_category SET label='Graphic/other designer' WHERE label='Graphic/Other Designer';

TRUNCATE svpeople_skill;
-- id <- skill_id
-- label <- name
-- active <- '1'
INSERT INTO svpeople_skill
    (id, label, active)
  SELECT skill_id, name, '1'
    FROM savane_old.people_skill;
TRUNCATE svpeople_skilllevel;
-- id <- skill_level_id
-- label <- name
-- active <- '1'
INSERT INTO svpeople_skilllevel
    (id, label, active)
  SELECT skill_level_id, name, '1'
    FROM savane_old.people_skill_level;
TRUNCATE svpeople_skillyear;
-- id <- skill_year_id
-- label <- name
-- active <- '1'
INSERT INTO svpeople_skillyear
    (id, label, active)
  SELECT skill_year_id, name, '1'
    FROM savane_old.people_skill_year;

TRUNCATE svpeople_jobinventory;
-- id <- job_inventory_id
INSERT INTO svpeople_jobinventory
    (id, job_id, skill_id, skill_level_id, skill_year_id)
  SELECT job_inventory_id, job_id, skill_id, skill_level_id, skill_year_id
    FROM savane_old.people_job_inventory;
TRUNCATE svpeople_skillinventory;
-- id <- skill_inventory_id
INSERT INTO svpeople_skillinventory
    (id, user_id, skill_id, skill_level_id, skill_year_id)
  SELECT skill_inventory_id, user_id, skill_id, skill_level_id, skill_year_id
    FROM savane_old.people_skill_inventory;


----
-- TRACKERS
----

INSERT INTO tracker_tracker (`name`) VALUES ('bugs');
INSERT INTO tracker_tracker (`name`) VALUES ('patch');
INSERT INTO tracker_tracker (`name`) VALUES ('support');
INSERT INTO tracker_tracker (`name`) VALUES ('task');

TRUNCATE tracker_item;
INSERT INTO tracker_item
    (tracker_id, public_bugs_id, group_id, status_id, severity, privacy,
    discussion_lock,
    vote, spamscore, ip, category_id, submitted_by_id, assigned_to,
    date, summary, details, close_date, bug_group_id, resolution_id,
    category_version_id, platform_version_id, reproducibility_id,
    size_id, fix_release_id, plan_release_id, hours, component_version,
    fix_release, plan_release, priority,
    planned_starting_date, planned_close_date,
    percent_complete, keywords, release_id, `release`,
    originator_name, originator_email, originator_phone,
    custom_tf1, custom_tf2, custom_tf3, custom_tf4, custom_tf5,
    custom_tf6, custom_tf7, custom_tf8, custom_tf9, custom_tf10,
    custom_ta1, custom_ta2, custom_ta3, custom_ta4, custom_ta5,
    custom_ta6, custom_ta7, custom_ta8, custom_ta9, custom_ta10,
    custom_sb1, custom_sb2, custom_sb3, custom_sb4, custom_sb5,
    custom_sb6, custom_sb7, custom_sb8, custom_sb9, custom_sb10,
    custom_df1, custom_df2, custom_df3, custom_df4, custom_df5)
  SELECT
    'bugs', bug_id, group_id, status_id, severity, privacy, discussion_lock,
    vote, spamscore, ip, category_id, submitted_by, assigned_to,
    FROM_UNIXTIME(date), IFNULL(summary, ''), IFNULL(details, ''), FROM_UNIXTIME(close_date), bug_group_id, resolution_id,
    category_version_id, platform_version_id, reproducibility_id,
    size_id, fix_release_id, plan_release_id, hours, component_version,
    fix_release, plan_release, priority,
    FROM_UNIXTIME(planned_starting_date),
    FROM_UNIXTIME(planned_close_date),
    percent_complete, keywords, release_id, `release`,
    originator_name, originator_email, originator_phone,
    custom_tf1, custom_tf2, custom_tf3, custom_tf4, custom_tf5,
    custom_tf6, custom_tf7, custom_tf8, custom_tf9, custom_tf10,
    custom_ta1, custom_ta2, custom_ta3, custom_ta4, custom_ta5,
    custom_ta6, custom_ta7, custom_ta8, custom_ta9, custom_ta10,
    custom_sb1, custom_sb2, custom_sb3, custom_sb4, custom_sb5,
    custom_sb6, custom_sb7, custom_sb8, custom_sb9, custom_sb10,
    FROM_UNIXTIME(IF(custom_df1<0,0,custom_df1)),
    FROM_UNIXTIME(IF(custom_df2<0,0,custom_df2)),
    FROM_UNIXTIME(IF(custom_df3<0,0,custom_df3)),
    FROM_UNIXTIME(IF(custom_df4<0,0,custom_df4)),
    FROM_UNIXTIME(IF(custom_df5<0,0,custom_df5))
    FROM savane_old.bugs;

-- We're merging all the *_field tables, so we need to assign new ids
CREATE TEMPORARY TABLE conv_field_ids (
  new INT auto_increment PRIMARY KEY,
  tracker_id VARCHAR(7), old INT,
  INDEX(tracker_id), INDEX(old));
INSERT INTO conv_field_ids (tracker_id, old)
        SELECT 'bugs',    bug_field_id FROM savane_old.bugs_field
  UNION SELECT 'patch',   bug_field_id FROM savane_old.patch_field
  UNION SELECT 'support', bug_field_id FROM savane_old.patch_field
  UNION SELECT 'task',    bug_field_id FROM savane_old.patch_field;

-- id <- conv_field_ids.new  (duplicates in savane_old.*_field tables)
-- name <- field_name
-- tracker_id <- 'bugs'
TRUNCATE tracker_field;
INSERT INTO tracker_field
    (id, tracker_id, name, display_type, display_size, label,
     description, scope, required, empty_ok, keep_history, special, custom)
  SELECT
      conv_field_ids.new, 'bugs', field_name, display_type, display_size, label,
      description, scope, required, empty_ok, keep_history, special, custom
    FROM savane_old.bugs_field JOIN conv_field_ids
      ON (bug_field_id = old AND tracker_id = 'bugs');
INSERT INTO tracker_field
    (id, tracker_id, name, display_type, display_size, label,
     description, scope, required, empty_ok, keep_history, special, custom)
  SELECT
      conv_field_ids.new, 'patch', field_name, display_type, display_size, label,
      description, scope, required, empty_ok, keep_history, special, custom
    FROM savane_old.patch_field JOIN conv_field_ids
      ON (bug_field_id = old AND tracker_id = 'patch');

-- Get rid of duplicates (old mysql/php/savane bug?)
-- It only affected group_id=100, maybe the installation was done
-- twice or something.
-- Give priority to the last one.
-- Need to create a real table - a temporary one has issues with being "reopened" in joins
CREATE TABLE temp_bugs_field_usage AS SELECT * FROM savane_old.bugs_field_usage;
ALTER TABLE temp_bugs_field_usage ADD (id INT auto_increment PRIMARY KEY);
DELETE FROM temp_bugs_field_usage
  WHERE id IN (
    SELECT id FROM (
      SELECT B.id FROM temp_bugs_field_usage A, temp_bugs_field_usage B
        WHERE A.id > B.id
          AND A.bug_field_id = B.bug_field_id AND A.group_id = B.group_id
      ) AS temp
    );
-- id <- <auto>
-- field_id <- bug_field_id
TRUNCATE tracker_fieldusage;
INSERT INTO tracker_fieldusage
    (field_id, group_id, use_it, show_on_add, show_on_add_members, place,
     custom_label, custom_description, custom_display_size, custom_empty_ok,
     custom_keep_history, transition_default_auth)
  SELECT
      conv_field_ids.new, group_id, use_it, show_on_add, show_on_add_members, place,
      custom_label, custom_description, custom_display_size, custom_empty_ok,
      IFNULL(custom_keep_history, 0), transition_default_auth
   FROM temp_bugs_field_usage JOIN conv_field_ids
      ON (bug_field_id = old AND tracker_id = 'bugs');
DROP TABLE temp_bugs_field_usage;

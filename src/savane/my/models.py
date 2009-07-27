# User extra attributes
# Copyright (C) 2009  Sylvain Beucler
# Copyright (C) 2009  Jonathan Gonzalez V.
#
# This file is part of Savane.
# 
# Savane is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# Savane is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django.db import models
from django.contrib.auth import models as auth_models

# TODO: these models probably don't belong to the 'my' application

class ExtendedUser(auth_models.User):
    """Django base User class + extra Savane fields"""

    # Migrated to 'firstname' in auth.User
    #realname = models.CharField(max_length=96)

    # Old Savane can be Active/Deleted/Pending/Suspended/SQuaD
    status_CHOICES = (
        ('A', 'Active'),
        ('D', 'Deleted'),
        ('P', 'Pending'),
        ('S', 'Suspended'),
        #('SQD', 'Squad'), # TODO: implement squads more cleanly
        )
    status = models.CharField(max_length=3)

    # Used by trackers only but it could be used more widely
    spamscore = models.IntegerField(null=True, blank=True)
    # Previously used for e-mail changes and password recovery, Django
    # does it different with a auth.tokens
    #confirm_hash = models.CharField(max_length=96, blank=True, null=True)

    # Keys
    authorized_keys = models.TextField(blank=True, null=True)
    authorized_keys_count = models.IntegerField(null=True, blank=True)
    gpg_key = models.TextField(blank=True, null=True)
    gpg_key_count = models.IntegerField(null=True, blank=True)

    # Personal info
    people_resume = models.TextField()

    # Preferences - /!\ some are also in the user_preferences table
    people_view_skills = models.IntegerField(null=True)
    timezone = models.CharField(max_length=192, blank=True, null=True)
    theme = models.CharField(max_length=45, blank=True, null=True)
    email_hide = models.CharField(max_length=9, blank=True, null=True)


    # Inherit specialized models.Manager with convenience functions
    objects = auth_models.UserManager()

class License(models.Model):
    """
    Main license used by a project

    TODO: support several licenses per project (mixed-licensed code,
    documentation, ...)
    """
    slug = models.CharField(max_length=32)
    name = models.CharField(max_length=255)
    url = models.CharField(max_length=255)

class DevelopmentStatus(models.Model):
    """Describe the development status of a project"""
    name = models.CharField(max_length=255)

class GroupConfiguration(models.Model):
    """Group configuration and main category (previously group_type)"""
    name = models.CharField(max_length=255)
    # Text added to each project page
    description = models.TextField(blank=True)

    #admin_email_adress = models.CharField(max_length=128, null=True) # unused

    # Redirect to this host when visiting project page
    base_host = models.CharField(max_length=128, null=True)
    # Mailing lists are hosted there
    mailing_list_host = models.CharField(max_length=255, null=True)

    # Permissions
    can_use_homepage     = models.BooleanField(default=True)
    can_use_download     = models.BooleanField(default=True)
    can_use_cvs          = models.BooleanField(default=True)
    can_use_arch         = models.BooleanField(default=False)
    can_use_svn          = models.BooleanField(default=False)
    can_use_git          = models.BooleanField(default=False)
    can_use_hg           = models.BooleanField(default=False)
    can_use_bzr          = models.BooleanField(default=False)
    can_use_license      = models.BooleanField(default=True)
    can_use_devel_status = models.BooleanField(default=True)
    can_use_forum        = models.BooleanField(default=False)
    can_use_mailing_list = models.BooleanField(default=True)
    can_use_patch        = models.BooleanField(default=False)
    can_use_task         = models.BooleanField(default=True)
    can_use_news         = models.BooleanField(default=True)
    can_use_support      = models.BooleanField(default=True)
    can_use_bug          = models.BooleanField(default=True)
    is_menu_configurable_homepage                = models.BooleanField(default=False)
    is_menu_configurable_download                = models.BooleanField(default=False)
    is_menu_configurable_forum                   = models.BooleanField(default=False)
    is_menu_configurable_support                 = models.BooleanField(default=False)
    is_menu_configurable_mail                    = models.BooleanField(default=False)
    is_menu_configurable_cvs                     = models.BooleanField(default=False)
    is_menu_configurable_cvs_viewcvs             = models.BooleanField(default=False)
    is_menu_configurable_cvs_viewcvs_homepage    = models.BooleanField(default=False)
    is_menu_configurable_arch                    = models.BooleanField(default=False)
    is_menu_configurable_arch_viewcvs            = models.BooleanField(default=False)
    is_menu_configurable_svn                     = models.BooleanField(default=False)
    is_menu_configurable_svn_viewcvs             = models.BooleanField(default=False)
    is_menu_configurable_git                     = models.BooleanField(default=False)
    is_menu_configurable_git_viewcvs             = models.BooleanField(default=False)
    is_menu_configurable_hg                      = models.BooleanField(default=False)
    is_menu_configurable_hg_viewcvs              = models.BooleanField(default=False)
    is_menu_configurable_bzr                     = models.BooleanField(default=False)
    is_menu_configurable_bzr_viewcvs             = models.BooleanField(default=False)
    is_menu_configurable_bugs                    = models.BooleanField(default=False)
    is_menu_configurable_task                    = models.BooleanField(default=False)
    is_menu_configurable_patch                   = models.BooleanField(default=False)
    is_menu_configurable_extralink_documentation = models.BooleanField(default=False)
    is_configurable_download_dir                 = models.BooleanField(default=False)

    # Directory creation config
    SCM_CHOICES = (
        ('cvs', 'CVS'),
        ('svn' , 'Subversion'),
        ('arch' , 'GNU Arch'),
        ('git' , 'Git'),
        ('hg' , 'Mercurial'),
        ('bzr' , 'Bazaar'),
        )
    homepage_scm = models.CharField(max_length=4, choices=SCM_CHOICES, default='cvs')
    DIR_TYPE_CHOICES = (
        ('basicdirectory', 'Basic directory'),
        ('basiccvs', 'Basic CVS directory'),
        ('basicsvn', 'Basic Subversion directory'),
        ('basicgit', 'Basic Git directory'),
        ('basichg', 'Basic Mercurial directory'),
        ('basicbzr', 'Basic Bazaar directory'),
        ('cvsattic', 'CVS Attic/Gna!'),
        ('svnattic', 'Subversion Attic/Gna!'),
        ('svnatticwebsite', 'Subversion Subdirectory Attic/Gna!'),
        ('savannah-gnu', 'CVS Savannah GNU'),
        ('savannah-nongnu', 'CVS Savannah non-GNU'),
        )
    dir_type_cvs      = models.CharField(max_length=15, choices=DIR_TYPE_CHOICES, default='basiccvs')
    dir_type_arch     = models.CharField(max_length=15, choices=DIR_TYPE_CHOICES, default='basicdirectory')
    dir_type_svn      = models.CharField(max_length=15, choices=DIR_TYPE_CHOICES, default='basicsvn')
    dir_type_git      = models.CharField(max_length=15, choices=DIR_TYPE_CHOICES, default='basicgit')
    dir_type_hg       = models.CharField(max_length=15, choices=DIR_TYPE_CHOICES, default='basichg')
    dir_type_bzr      = models.CharField(max_length=15, choices=DIR_TYPE_CHOICES, default='basicbzr')
    dir_type_homepage = models.CharField(max_length=15, choices=DIR_TYPE_CHOICES, default='basicdirectory')
    dir_type_download = models.CharField(max_length=15, choices=DIR_TYPE_CHOICES, default='basicdirectory')
    dir_homepage = models.CharField(max_length=255, default='/'),
    dir_cvs      = models.CharField(max_length=255, default='/')
    dir_arch     = models.CharField(max_length=255, default='/')
    dir_svn      = models.CharField(max_length=255, default='/')
    dir_git      = models.CharField(max_length=255, default='/')
    dir_hg       = models.CharField(max_length=255, default='/')
    dir_bzr      = models.CharField(max_length=255, default='/')
    dir_download = models.CharField(max_length=255, default='/')

    # Default URLs
    url_homepage             = models.CharField(max_length=255, default='http://'),
    url_download             = models.CharField(max_length=255, default='http://')
    url_cvs_viewcvs          = models.CharField(max_length=255, default='http://')
    url_arch_viewcvs         = models.CharField(max_length=255, default='http://') 
    url_svn_viewcvs          = models.CharField(max_length=255, default='http://')
    url_git_viewcvs          = models.CharField(max_length=255, default='http://')
    url_hg_viewcvs           = models.CharField(max_length=255, default='http://')
    url_bzr_viewcvs          = models.CharField(max_length=255, default='http://')
    url_cvs_viewcvs_homepage = models.CharField(max_length=255, default='http://')
    url_mailing_list_listinfo         = models.CharField(max_length=255, default='http://'),
    url_mailing_list_subscribe        = models.CharField(max_length=255, default='http://')
    url_mailing_list_unsubscribe      = models.CharField(max_length=255, default='http://')
    url_mailing_list_archives         = models.CharField(max_length=255, default='http://')
    url_mailing_list_archives_private = models.CharField(max_length=255, default='http://')
    url_mailing_list_admin            = models.CharField(max_length=255, default='http://')
    url_extralink_documentation = models.CharField(max_length=255, blank=True)

    # Unused
    #license_array = models.TextField()

    devel_status_array = models.ForeignKey(DevelopmentStatus),

    mailing_list_address = models.CharField(max_length=255, default='@'),
    mailing_list_virtual_host = models.CharField(max_length=255, default=''),
    mailing_list_format = models.CharField(max_length=255, default='%NAME'),

    # TODO: split forum and news config
    #forum_flags     = IntegerField(default='2')
    #news_flags      = IntegerField(default='3')
    #forum_rflags    = IntegerField(default='2')
    #news_rflags     = IntegerField(default='2')

    # TODO: split tracker config
    #bugs_flags      = IntegerField(default='2')
    #task_flags      = IntegerField(default='2')
    #patch_flags     = IntegerField(default='2')
    #cookbook_flags  = IntegerField(default='2')
    #support_flags   = IntegerField(default='2')
    #bugs_rflags     = IntegerField(default='2')
    #task_rflags     = IntegerField(default='5')
    #patch_rflags    = IntegerField(default='2')
    #cookbook_rflags = IntegerField(default='5')
    #support_rflags  = IntegerField(default='2')


class ExtendedGroup(auth_models.Group):
    """Django base Group class + extra Savane fields"""
    
    type = models.ForeignKey(GroupConfiguration)
    name = models.CharField(max_length=30, blank=True)
    is_public = models.BooleanField(default=False)
    status_CHOICES = (
        ('A', 'Active'),
        ('P', 'Pending'),
        ('D', 'Deleted'),
        ('M', 'Maintenance (accessible only to superuser)'),
        ('I', 'Incomplete (failure during registration)'),
        )
    status = models.CharField(max_length=1, default='A')
    short_description = models.CharField(max_length=255, blank=True)
    long_description = models.TextField()
    license = models.ForeignKey(License, null=True)
    license_other = models.TextField()

    devel_status = models.ForeignKey(DevelopmentStatus),

    # Registration-specific
    register_purpose = models.TextField()
    required_software = models.TextField()
    other_comments = models.TextField()

    register_time = models.DateTimeField()
    #rand_hash text,
    
    registered_gpg_keys = models.TextField()

    # Project "Features"
    use_homepage                = models.BooleanField(default=False)
    use_mail                    = models.BooleanField(default=False)
    use_patch                   = models.BooleanField(default=False)
    use_task                    = models.BooleanField(default=False)
    use_forum                   = models.BooleanField(default=False)
    use_cvs                     = models.BooleanField(default=False)
    use_arch                    = models.BooleanField(default=False)
    use_svn                     = models.BooleanField(default=False)
    use_git                     = models.BooleanField(default=False)
    use_hg                      = models.BooleanField(default=False)
    use_bzr                     = models.BooleanField(default=False)
    use_news                    = models.BooleanField(default=False)
    use_support                 = models.BooleanField(default=False)
    use_download                = models.BooleanField(default=False)
    use_bugs                    = models.BooleanField(default=False)
    use_extralink_documentation = models.BooleanField(default=False)

    # 'null' means 'use default'
    url_homepage                = models.CharField(max_length=255, null=True)
    url_download                = models.CharField(max_length=255, null=True)
    url_forum                   = models.CharField(max_length=255, null=True)
    url_support                 = models.CharField(max_length=255, null=True)
    url_mail                    = models.CharField(max_length=255, null=True)
    url_cvs                     = models.CharField(max_length=255, null=True)
    url_cvs_viewcvs             = models.CharField(max_length=255, null=True)
    url_cvs_viewcvs_homepage    = models.CharField(max_length=255, null=True)
    url_arch                    = models.CharField(max_length=255, null=True)
    url_arch_viewcvs            = models.CharField(max_length=255, null=True)
    url_svn                     = models.CharField(max_length=255, null=True)
    url_svn_viewcvs             = models.CharField(max_length=255, null=True)
    url_git                     = models.CharField(max_length=255, null=True)
    url_git_viewcvs             = models.CharField(max_length=255, null=True)
    url_hg                      = models.CharField(max_length=255, null=True)
    url_hg_viewcvs              = models.CharField(max_length=255, null=True)
    url_bzr                     = models.CharField(max_length=255, null=True)
    url_bzr_viewcvs             = models.CharField(max_length=255, null=True)
    url_bugs                    = models.CharField(max_length=255, null=True)
    url_task                    = models.CharField(max_length=255, null=True)
    url_patch                   = models.CharField(max_length=255, null=True)
    url_extralink_documentation = models.CharField(max_length=255, null=True)

    # Admin override (unused)
    #dir_cvs = models.CharField(max_length=255, null=True)
    #dir_arch = models.CharField(max_length=255, null=True)
    #dir_svn = models.CharField(max_length=255, null=True)
    #dir_git = models.CharField(max_length=255, null=True)
    #dir_hg = models.CharField(max_length=255, null=True)
    #dir_bzr = models.CharField(max_length=255, null=True)
    #dir_homepage = models.CharField(max_length=255, null=True)
    #dir_download = models.CharField(max_length=255, null=True)

    # TODO: split trackers configuration
    #bugs_preamble = models.TextField()
    #task_preamble = models.TextField()
    #patch_preamble = models.TextField()
    #support_preamble = models.TextField()
    #cookbook_preamble = models.TextField()

    #new_bugs_address text NOT NULL
    #new_patch_address text NOT NULL
    #new_support_address text NOT NULL
    #new_task_address text NOT NULL
    #new_news_address text NOT NULL
    #new_cookbook_address text NOT NULL

    #bugs_glnotif int(11) NOT NULL default '1'
    #support_glnotif int(11) NOT NULL default '1'
    #task_glnotif int(11) NOT NULL default '1'
    #patch_glnotif int(11) NOT NULL default '1'
    #cookbook_glnotif int(11) NOT NULL default '1'
    #send_all_bugs int(11) NOT NULL default '0'
    #send_all_patch int(11) NOT NULL default '0'
    #send_all_support int(11) NOT NULL default '0'
    #send_all_task int(11) NOT NULL default '0'
    #send_all_cookbook int(11) NOT NULL default '0'
    #bugs_private_exclude_address text
    #task_private_exclude_address text
    #support_private_exclude_address text
    #patch_private_exclude_address text
    #cookbook_private_exclude_address text
# User/group extra attributes
# Copyright (C) 2002-2006 Mathieu Roy <yeupou--gnu.org>
# Copyright (C) 2007, 2008, 2009  Sylvain Beucler
# Copyright (C) 2008  Aleix Conchillo Flaque
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

"""
User/group extra attributes

This may look like reinventing the User.get_profile() that comes with
Django;
http://www.b-list.org/weblog/2006/jun/06/django-tips-extending-user-model/
http://mirobetm.blogspot.com/2007/04/en-django-extending-user_2281.html

However profiles were mainly useful in Django < 1.0 where you couldn't
subclass User.

Profiles also have a few drawbacks, namely they are site-specific,
which means you cannot have multiple applications have different
profiles in the same website, while with subclassing you only need to
user different class names (to avoid parent->child fieldname clash).

Moreover splitting the information in two different models can be
cumbersome when using ModelForms.

Subclassing drawback: there's apparently a technique to use a
vhost-based profile class (with django.contrib.site and multiples
settings.py). But it's not useful for Savane IMHO.

In addition, it seems impossible to convert an existing User to a
derived class from Python (this can be done through DB but that's
ugly). This apparently prevents auto-creating our derived class when a
new User is directly created (and sends a post_save signal).

Profiles vs. inheritance is also described at
http://scottbarnham.com/blog/2008/08/21/extending-the-django-user-model-with-inheritance/

Note that Scott's authentication backend has the same issue than
profiles: only one profile class can be used on a single website, so
we don't use it.

The current solution is to use AutoOneToOneField: OneToOneField is
similar to extending a model class (at the SQL tables level), and
AutoOneToOneField is a trick from django-annoying to automatically
create the extended data on first access.
"""

from django.db import models
from django.contrib.auth import models as auth_models


class SshKey(models.Model):
    user = models.ForeignKey(auth_models.User)
    # Could a CharField with max_length=3000 or something similar, as
    # it's a single line of text, but it sounds safer to use a
    # TextField for such a long text.  Too bad for the admin/ area.
    ssh_key = models.TextField(blank=False)

from annoying.fields import AutoOneToOneField
class SvUserInfo(models.Model):
    """
    Django base User class + extra Savane fields

    Since it adds a field to Django's User objects, we prefix it by
    'sv' to avoid clashes with other packages, C-style (ahem).

    Using AutoOneToOneField to automatically create this extra data
    for new users as soon as the field is accessed.
    """

    class Meta:
        ordering = ['user__username']

    user = AutoOneToOneField(auth_models.User, primary_key=True)

    # Migrated to 'first_name' and 'last_name' in auth.User
    #realname = models.CharField(max_length=96)

    # Old Savane can be Active/Deleted/Pending/Suspended/SQuaD
    status_CHOICES = (
        ('A', 'Active'),
        ('D', 'Deleted'),
        ('P', 'Pending'),
        ('S', 'Suspended'),
        #('SQD', 'Squad'), # TODO: implement squads more cleanly
        )
    status = models.CharField(max_length=3, choices=status_CHOICES, default='A')

    # Unix mapping, used when populating a LDAP directory
    uidNumber = models.IntegerField(default=0)
    gidNumber = models.IntegerField(default=0)

    # Used by trackers only but it could be used more widely
    spamscore = models.IntegerField(null=True, blank=True)
    # Previously used for e-mail changes and password recovery, Django
    # does it different with a auth.tokens
    #confirm_hash = models.CharField(max_length=96, blank=True, null=True)

    # Keys
    gpg_key = models.TextField(blank=True)
    gpg_key_count = models.IntegerField(null=True, blank=True)
    # SSH keys: cf. SshKey above

    # Personal info
    people_resume = models.TextField()

    # Preferences - /!\ some are also in the user_preferences table
    people_view_skills = models.BooleanField(default=False)
    email_hide = models.BooleanField(default=False)
    timezone = models.CharField(max_length=192, blank=True)
    theme = models.CharField(max_length=45, blank=True)

    # Inherit specialized models.Manager with convenience functions
    objects = auth_models.UserManager()

    @staticmethod
    def query_active_users_raw(conn, fields):
        """
        Return efficient query with all the users; used by LDIF export
        """
        return conn.query("SELECT "
                          + ",".join(fields)
                          + " FROM auth_user JOIN svmain_extendeduser"
                          + " ON auth_user.id = svmain_extendeduser.user_ptr_id"
                          + " WHERE status = 'A'"
                          )


class License(models.Model):
    """
    Main license used by a project

    TODO: support several licenses per project (mixed-licensed code,
    documentation, ...)
    """
    slug = models.SlugField(max_length=32)
    name = models.CharField(max_length=255)
    url = models.CharField(max_length=255, blank=True)

    def get_group_names(self):
        """
        Return a list of groups with only the 'name' attribute
        retrieved for efficiency (retrieving all informations, namely
        long_description, is quite long).  Used by the license template.
        """
        return self.svgroupinfo_set.values_list('group__name', flat=True)

    def __unicode__(self):
        return self.slug + ": " + self.name

    @models.permalink
    def get_absolute_url(self):
        return ('savane.svmain.license_detail', [self.slug])

    class Meta:
        ordering = ['slug']

class DevelopmentStatus(models.Model):
    """Describe the development status of a project"""
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name_plural='Development statuses'

class GroupConfiguration(models.Model):
    """Group configuration and main category (previously group_type)"""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True,
      help_text='Will be added on each project main page')

    #admin_email_adress = models.CharField(max_length=128, null=True) # unused

    # Redirect to this host when visiting project page
    base_host = models.CharField(max_length=128, blank=True)

    # Mailing lists
    mailing_list_address = models.CharField(max_length=255, default='@',
      help_text='would be %LIST@gnu.org for GNU projects at sv.gnu.org')
    mailing_list_virtual_host = models.CharField(max_length=255, blank=True,
      help_text='would be lists.gnu.org or lists.nongnu.org at sv.gnu.org [BACKEND SPECIFIC]')
    mailing_list_format = models.CharField(max_length=255, default='%NAME',
      help_text='With this, you can force projects to follow a specific policy'
        + ' for the name of the %LIST. Here you should use the special wildcard'
        + ' %NAME, which is the part the of the mailing list name that the'
        + ' project admin can define (would be %PROJECT-%NAME for non-GNU'
        + ' projects at sv.gnu.org). Do no add any @hostname here!'
        + ' You can specify multiple formats separated by a "," comma.')
    #mailing_list_host = models.CharField(max_length=255, help_text='DEPRECATED')

    # Permissions
    can_use_homepage     = models.BooleanField(default=True)
    can_use_download     = models.BooleanField(default=True,
      help_text='This is useful if you provide directly download areas (created'
        + ' by the backend) or if you want to allow projects to configure the'
        + ' related menu entry (see below).')
    can_use_cvs          = models.BooleanField(default=False)
    can_use_arch         = models.BooleanField(default=False)
    can_use_svn          = models.BooleanField(default=False)
    can_use_git          = models.BooleanField(default=False)
    can_use_hg           = models.BooleanField(default=False)
    can_use_bzr          = models.BooleanField(default=False)
    can_use_license      = models.BooleanField(default=True,
      help_text='This is useful if you want project to select a license'
        + ' on submission.')
    can_use_devel_status = models.BooleanField(default=True,
      help_text='This is useful if you want project to be able to defines their'
        + ' development status that will be shown on their main page. This is'
        + ' purely a matter of cosmetics. This option is mainly here just to'
        + ' remove this content in case it is useless (it does not makes sense'
        + ' for organizational projects).')
    can_use_mailing_list = models.BooleanField(default=True,
      help_text='This is one of the main issue tracker of Savane.'
        + ' Projects are supposed to use it as primary interface with end user.')
    can_use_support      = models.BooleanField(default=True)
    can_use_bug          = models.BooleanField(default=True)
    can_use_task         = models.BooleanField(default=True)
    can_use_patch        = models.BooleanField(default=False)
    can_use_news         = models.BooleanField(default=True)
    is_menu_configurable_homepage                = models.BooleanField(default=False,
      help_text='the homepage link can be modified')
    is_menu_configurable_download                = models.BooleanField(default=False)
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
    is_configurable_download_dir = models.BooleanField(default=False,
      help_text="the download _directory_ can be modified -- beware, if the"
        + " backend is running and creating download dir, it can be used"
        + " maliciously. don't activate this feature unless you truly know"
        + "what you're doing")

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
    dir_homepage = models.CharField(max_length=255, default='/')
    dir_cvs      = models.CharField(max_length=255, default='/')
    dir_arch     = models.CharField(max_length=255, default='/')
    dir_svn      = models.CharField(max_length=255, default='/')
    dir_git      = models.CharField(max_length=255, default='/')
    dir_hg       = models.CharField(max_length=255, default='/')
    dir_bzr      = models.CharField(max_length=255, default='/')
    dir_download = models.CharField(max_length=255, default='/')

    # Default URLs
    url_homepage             = models.CharField(max_length=255, default='http://')
    url_cvs_viewcvs_homepage = models.CharField(max_length=255, default='http://')
    url_cvs_viewcvs          = models.CharField(max_length=255, default='http://')
    url_arch_viewcvs         = models.CharField(max_length=255, default='http://')
    url_svn_viewcvs          = models.CharField(max_length=255, default='http://')
    url_git_viewcvs          = models.CharField(max_length=255, default='http://')
    url_hg_viewcvs           = models.CharField(max_length=255, default='http://')
    url_bzr_viewcvs          = models.CharField(max_length=255, default='http://')
    url_download             = models.CharField(max_length=255, default='http://')
    url_mailing_list_listinfo         = models.CharField(max_length=255, default='http://')
    url_mailing_list_subscribe        = models.CharField(max_length=255, default='http://')
    url_mailing_list_unsubscribe      = models.CharField(max_length=255, default='http://')
    url_mailing_list_archives         = models.CharField(max_length=255, default='http://')
    url_mailing_list_archives_private = models.CharField(max_length=255, default='http://')
    url_mailing_list_admin            = models.CharField(max_length=255, default='http://')
    url_extralink_documentation = models.CharField(max_length=255, blank=True)

    # Deprecated
    # "Forum is a deprecated feature of Savane. We do not recommend
    #  using it and we do not maintain this code any longer."
    #can_use_forum = models.BooleanField(default=False)
    #is_menu_configurable_forum = models.BooleanField(default=False)
    #forum_flags = IntegerField(default='2')
    #forum_rflags = IntegerField(default='2')

    # Unused
    #license_array = models.TextField()
    #devel_status_array = models.TextField()

    # TODO: split forum and news config
    #news_flags      = IntegerField(default='3')
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

    def __unicode__(self):
        return self.name


class SvGroupInfo(models.Model):
    """
    Django base Group class + extra Savane fields

    Cf. SvUserInfo for concepts.
    """

    class Meta:
        ordering = ['group__name']

    group = AutoOneToOneField(auth_models.Group, primary_key=True)

    type = models.ForeignKey(GroupConfiguration)
    full_name = models.CharField(max_length=255, blank=True,
      help_text="Full project name (not Unix system name)")
    is_public = models.BooleanField(default=False)
    status_CHOICES = (
        ('A', 'Active'),
        ('P', 'Pending'),
        ('D', 'Deleted'),
        ('M', 'Maintenance (accessible only to superuser)'),
        ('I', 'Incomplete (failure during registration)'),
        )
    status = models.CharField(max_length=1, choices=status_CHOICES, default='A')
    gidNumber = models.IntegerField(default=0)

    short_description = models.CharField(max_length=255, blank=True)
    long_description = models.TextField(blank=True)
    license = models.ForeignKey(License, blank=True, null=True)
    license_other = models.TextField(blank=True)

    devel_status = models.ForeignKey(DevelopmentStatus)

    # Registration-specific
    register_purpose = models.TextField(blank=True)
    required_software = models.TextField(blank=True)
    other_comments = models.TextField(blank=True)

    register_time = models.DateTimeField()
    #rand_hash text,

    registered_gpg_keys = models.TextField(blank=True)

    # Project "Features"
    use_homepage                = models.BooleanField(default=False)
    use_mail                    = models.BooleanField(default=False)
    use_patch                   = models.BooleanField(default=False)
    use_task                    = models.BooleanField(default=False)
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

    # blank means 'use default'
    url_homepage                = models.CharField(max_length=255, blank=True)
    url_download                = models.CharField(max_length=255, blank=True)
    url_support                 = models.CharField(max_length=255, blank=True)
    url_mail                    = models.CharField(max_length=255, blank=True)
    url_cvs                     = models.CharField(max_length=255, blank=True)
    url_cvs_viewcvs             = models.CharField(max_length=255, blank=True)
    url_cvs_viewcvs_homepage    = models.CharField(max_length=255, blank=True)
    url_arch                    = models.CharField(max_length=255, blank=True)
    url_arch_viewcvs            = models.CharField(max_length=255, blank=True)
    url_svn                     = models.CharField(max_length=255, blank=True)
    url_svn_viewcvs             = models.CharField(max_length=255, blank=True)
    url_git                     = models.CharField(max_length=255, blank=True)
    url_git_viewcvs             = models.CharField(max_length=255, blank=True)
    url_hg                      = models.CharField(max_length=255, blank=True)
    url_hg_viewcvs              = models.CharField(max_length=255, blank=True)
    url_bzr                     = models.CharField(max_length=255, blank=True)
    url_bzr_viewcvs             = models.CharField(max_length=255, blank=True)
    url_bugs                    = models.CharField(max_length=255, blank=True)
    url_task                    = models.CharField(max_length=255, blank=True)
    url_patch                   = models.CharField(max_length=255, blank=True)
    url_extralink_documentation = models.CharField(max_length=255, blank=True)

    # Admin override (unused)
    #dir_cvs = models.CharField(max_length=255)
    #dir_arch = models.CharField(max_length=255)
    #dir_svn = models.CharField(max_length=255)
    #dir_git = models.CharField(max_length=255)
    #dir_hg = models.CharField(max_length=255)
    #dir_bzr = models.CharField(max_length=255)
    #dir_homepage = models.CharField(max_length=255)
    #dir_download = models.CharField(max_length=255)

    # Deprecated
    #url_forum = models.CharField(max_length=255, blank=True)
    #use_forum = models.BooleanField(default=False)

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

    def full_name_display(self):
        if self.full_name != "":
            return self.full_name
        else:
            return self.group.name

    @staticmethod
    def query_active_groups_raw(conn, fields):
        """
        Return efficient query with all the users; used by LDIF export
        """
        return conn.query("SELECT "
                          + ",".join(fields)
                          + " FROM auth_group JOIN svmain_svgroupinfo"
                          + " ON auth_group.id = svmain_svgroupinfo.group_id"
                          + " WHERE status = 'A'"
                          )

    def __unicode__(self):
        return "%s (%s)" % (self.group.name, self.status)


class Membership(models.Model):
    """
    Extra attributes about a User<->Group relationship
    (e.g. "is the user an admin?")

    Consider this as metadata about an existing
    django.contrib.auth.User.groups relationship; or a potential
    relationship (e.g. pending membership waiting for admin approval).

    The group membership is defined by the underlying User.groups
    relationship, not this one.
    """

    class Meta:
        unique_together = (('user', 'group'),)
        ordering = ('group', 'user', )

    user = models.ForeignKey(auth_models.User)
    group = models.ForeignKey(auth_models.Group)

    admin_flags_CHOICES = (
        ('A', 'Admin'),
        # IMHO we need to put 'P' in a separate table, like 'pending
        # membership', otherwise it's too easy to make mistakes
        ('P', 'Pending moderation'),
        ('SQD', 'Squad'), # FIXME: I dislike squad=user
        )
    admin_flags = models.CharField(max_length=3, choices=admin_flags_CHOICES,
      blank=True, help_text="membership properties")
    onduty = models.BooleanField(default=True,
      help_text="Untick to hide emeritous members from the project page")
    since = models.DateField(blank=True, null=True)

    # TODO: split news params
    #news_flags int(11) default NULL

    # Trackers-related
    #privacy_flags = models.BooleanField(default=True)
    #bugs_flags int(11) default NULL
    #task_flags int(11) default NULL
    #patch_flags int(11) default NULL
    #support_flags int(11) default NULL
    #cookbook_flags int(11) default NULL

    # Deprecated
    #forum_flags int(11) default NULL

    def save(self, force_insert=False, force_update=False):
        """
        Update the matching User<->Group relationship
        """
        if self.admin_flags != 'P':
            self.group.user_set.add(self.user)
        if self.admin_flags == 'P':
            self.group.user_set.remove(self.user)
        super(self.__class__, self).save(force_insert, force_update)
    def delete(self, using=None):
        self.group.user_set.remove(self.user)
        super(self.__class__, self).delete(using)

    @staticmethod
    def is_member(user, group):
        return group.user_set.filter(pk=user.pk).count() > 0

    @staticmethod
    def is_admin(user, group):
        return (Membership.is_member(user, group)
                and Membership.objects
                .filter(user=user, group=group, admin_flags='A').count() > 0)

    @staticmethod
    def query_active_memberships_raw(conn, fields):
        """
        Return efficient query with all the users; used by LDIF export
        """
        return conn.query("SELECT "
                          + ",".join(fields)
                          + " FROM svmain_membership JOIN auth_user"
                          + " ON user_id = auth_user.id"
                          + " WHERE admin_flags<>'P'"
                          )

    def __unicode__(self):
        return "[%s is a member of %s]" % (self.user.username, self.group.name)

# User/group admin interface
# Copyright (C) 2009, 2010  Sylvain Beucler
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

from django.contrib import admin
from django.utils.translation import ugettext, ugettext_lazy as _
import models as svmain_models

class LicenseAdmin(admin.ModelAdmin):
    list_display  = ['slug', 'pk', 'name', 'url']
    search_fields = ['name']

class DevelopmentStatusAdmin(admin.ModelAdmin):
    list_display  = ['name', 'pk']
    search_fields = ['name']

class SshKeyInline(admin.TabularInline):
    model = svmain_models.SshKey
    extra = 2  # to add several keys in the ExtendedUser page

class SvUserInfoAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('user',)}),
        ('Savane',
         {'fields': ('status', 'spamscore',
                     'gpg_key', 'gpg_key_count',
                     'email_hide', 'timezone', 'theme',)}),
        )
    list_display = ('user', 'status')
    list_filter = ('status',)
    search_fields = ('user',)
    ordering = ('user__username',)
    #filter_horizontal = ('m2m',)
    #inlines = [SshKeyInline]

class GroupConfigurationAdmin(admin.ModelAdmin):
    fieldsets = (
        (_('General Settings'), {'fields': ('name', 'base_host', 'description')}),
        (_('Project WWW Homepage'),
         {'fields': ('can_use_homepage', 'homepage_scm', 'dir_type_homepage',
                     'dir_homepage', 'url_homepage', 'url_cvs_viewcvs_homepage')}),
        (_('Source Code Manager: CVS'),
         {'fields': ('can_use_cvs', 'dir_type_cvs',
                     'dir_cvs', 'url_cvs_viewcvs')}),
        (_('Source Code Manager: GNU Arch'),
         {'fields': ('can_use_arch', 'dir_type_arch',
                     'dir_arch', 'url_arch_viewcvs')}),
        (_('Source Code Manager: Subversion'),
         {'fields': ('can_use_svn', 'dir_type_svn',
                     'dir_svn', 'url_svn_viewcvs')}),
        (_('Source Code Manager: Git'),
         {'fields': ('can_use_git', 'dir_type_git',
                     'dir_git', 'url_git_viewcvs')}),
        (_('Source Code Manager: Mercurial'),
         {'fields': ('can_use_hg', 'dir_type_hg',
                     'dir_hg', 'url_hg_viewcvs')}),
        (_('Source Code Manager: Bazaar'),
         {'fields': ('can_use_bzr', 'dir_type_bzr',
                     'dir_bzr', 'url_bzr_viewcvs')}),
        (_('Download area'),
         {'fields': ('can_use_download', 'dir_type_download',
                     'dir_download', 'url_download')}),
        (_('Licenses'), {'fields': ('can_use_license',)}),
        (_('Development Status'), {'fields': ('can_use_devel_status',)}),
        (_('Mailing List'),
         {'fields': ('can_use_mailing_list', 'mailing_list_virtual_host',
                     'mailing_list_address', 'mailing_list_format',
                     'url_mailing_list_listinfo', 'url_mailing_list_archives',
                     'url_mailing_list_archives_private', 'url_mailing_list_admin')}),
        # TODO: finish
        (_('News Manager'), {'fields': ('can_use_news',)}),
        (_('Project Menu Settings'),
         {'fields': ('is_menu_configurable_homepage',
                     'is_menu_configurable_extralink_documentation',
                     'is_menu_configurable_download',
                     'is_configurable_download_dir',
                     'is_menu_configurable_support',
                     # ...
                     )}),
        
        )

class SvGroupInfoAdmin(admin.ModelAdmin):
    # Copy/pasted from django.contrib.auth.admin; inheritance fails
    # when you attempt to display extended fields..
    search_fields = ('name',)
    ordering = ('group__name',)
    #filter_horizontal = ('permissions',)
    list_display  = ('pk', 'full_name', 'type', 'license',)
    list_filter = ('type', 'license', 'devel_status',)
    date_hierarchy = 'register_time'

class MailingListAdmin(admin.ModelAdmin):
    search_fields = ('list_name',)
    ordering = ('list_name',)
    list_display  = ('pk', 'list_name', 'status', 'is_public', 'description',)
    list_filter = ('status', 'is_public', )

admin.site.register(svmain_models.SvUserInfo, SvUserInfoAdmin)
admin.site.register(svmain_models.SvGroupInfo, SvGroupInfoAdmin)
admin.site.register(svmain_models.GroupConfiguration, GroupConfigurationAdmin)
admin.site.register(svmain_models.License, LicenseAdmin)
admin.site.register(svmain_models.DevelopmentStatus, DevelopmentStatusAdmin)
admin.site.register(svmain_models.MailingList, MailingListAdmin)

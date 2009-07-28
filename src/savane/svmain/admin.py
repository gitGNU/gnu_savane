from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.utils.translation import ugettext, ugettext_lazy as _
import models as svmain_models

class LicenseAdmin(admin.ModelAdmin):
    list_display  = ['slug', 'pk', 'name', 'url']
    search_fields = ['name']

class DevelopmentStatusAdmin(admin.ModelAdmin):
    list_display  = ['name', 'pk']
    search_fields = ['name']

class ExtendedUserAdmin(admin.ModelAdmin):
    # Copy/pasted from django.contrib.auth.admin; inheritance fails
    # when you attempt to display extended fields..
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_staff', 'is_active', 'is_superuser', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Groups'), {'fields': ('groups',)}),
        (_('Savane'),
         {'fields': ('status', 'spamscore',
                     'authorized_keys', 'authorized_keys_count',
                     'gpg_key', 'gpg_key_count',
                     'people_view_skills', 'email_hide', 'timezone', 'theme',)}),
        )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    filter_horizontal = ('user_permissions',)

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
                     'url_mailing_list_listinfo', 'url_mailing_list_subscribe',
                     'url_mailing_list_unsubscribe', 'url_mailing_list_archives',
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

class ExtendedGroupAdmin(admin.ModelAdmin):
    # Copy/pasted from django.contrib.auth.admin; inheritance fails
    # when you attempt to display extended fields..
    search_fields = ('name',)
    ordering = ('name',)
    filter_horizontal = ('permissions',)
    list_display  = ('name', 'pk', 'full_name', 'type', 'license',)
    list_filter = ('type', 'license', 'devel_status',)

admin.site.register(svmain_models.ExtendedUser, ExtendedUserAdmin)
admin.site.register(svmain_models.ExtendedGroup, ExtendedGroupAdmin)
admin.site.register(svmain_models.GroupConfiguration, GroupConfigurationAdmin)
admin.site.register(svmain_models.License, LicenseAdmin)
admin.site.register(svmain_models.DevelopmentStatus, DevelopmentStatusAdmin)

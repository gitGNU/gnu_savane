# URL dispatching for presentation pages
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

from django.conf.urls.defaults import *
from django.views.generic.list_detail import object_list, object_detail
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext, ugettext_lazy as _

import savane.svmain.models as svmain_models
import django.contrib.auth.models as auth_models
import views
from savane.filters import search
from savane.perms import only_project_admin
from savane.django_utils import decorated_patterns

urlpatterns = patterns ('',)

urlpatterns += patterns ('',
  url(r'^$', 'django.views.generic.simple.direct_to_template',
      { 'template' : 'index.html',
        'extra_context' : { 'has_left_menu': False } },
      name='homepage'),
  # TODO: add a web interface to edit some static content (using Django template notation?)
  url(r'^contact/$', 'django.views.generic.simple.direct_to_template',
      { 'template' : 'svmain/text.html',
        'extra_context' : { 'title' : 'Contact', }, },
      name='contact'),
)

# TODO: not sure about the views naming convention - all this
# "models in 'svmain', views in 'my'" is getting messy, probably a
# mistake from me (Beuc) :P
from django.contrib.auth.admin import UserAdmin
urlpatterns += patterns ('',
  url(r'^u/$',
      search(object_list),
      { 'queryset': auth_models.User.objects.all(),
        'paginate_by': 20,
        'model_admin': UserAdmin,
        'extra_context' : { 'title' : _("Users") },
        'template_name' : 'svmain/user_list.html' },
      name='user_list'),
  url(r'^u/(?P<slug>[-\w]+)/$', object_detail,
      { 'queryset' : auth_models.User.objects.all(),
        'slug_field' : 'username',
        'extra_context' : { 'title' : _("User detail") },
        'template_name' : 'svmain/user_detail.html', },
      name='user_detail'),
  url(r'^us/(?P<slug>[-\w]+)/$', views.user_redir),
  url(r'^users/(?P<slug>[-\w]+)/?$', views.user_redir),
)

from django.contrib.auth.admin import GroupAdmin
urlpatterns += patterns ('',
  url(r'^p/$',
      search(object_list),
      { 'queryset': auth_models.Group.objects.all(),
        'paginate_by': 20,
        'model_admin': GroupAdmin,
        'extra_context' : { 'title' : _("Projects") },
        'template_name' : 'svmain/group_list.html' },
      name='group_list'),
  url(r'^p/(?P<slug>[-\w]+)/$', object_detail,
      { 'queryset' : auth_models.Group.objects.all(),
        'slug_field' : 'name',
        'template_name' : 'svmain/group_detail.html',
        'template_object_name' : 'group', },
      name='group_detail'),
  url(r'^pr/(?P<slug>[-\w]+)/$', views.group_redir),
  url(r'^projects/(?P<slug>[-\w]+)/$', views.group_redir),
  url(r'^p/(?P<slug>[-\w]+)/memberlist/$', object_detail,
      { 'queryset' : auth_models.Group.objects.all(),
        'slug_field' : 'name',
        'extra_context' : { 'title' : _("Project memberlist") },
        'template_name' : 'svmain/group_memberlist.html',
        'template_object_name' : 'group', },
      name='group_memberlist'),
  url(r'^p/(?P<slug>[-\w]+)/gpgkeyring/$', views.group_gpgkeyring,
      { 'extra_context' : { 'title' : ("Project members GPG keyring") }, },
      name='group_gpgkeyring'),
  url(r'^p/(?P<slug>[-\w]+)/gpgkeyring/download/$', views.group_gpgkeyring_download,
      name='group_gpgkeyring_download'),
  url(r'^p/(?P<slug>[-\w]+)/mailinglist/$', views.group_mailinglist,
      { 'extra_context' : { 'title' : ("Mailing lists") }, },
      name='group_mailinglist'),
  # VCS
  url(r'^p/(?P<slug>[-\w]+)/vcs/cvs/$', object_detail,
      { 'queryset' : auth_models.Group.objects.all(),
        'slug_field' : 'name',
        'extra_context' : { 'title' : ("CVS Repositories") },
        'template_name' : 'svmain/group_vcs_cvs.html',
        'template_object_name' : 'group', },
      name='group_vcs_cvs'),
  url(r'^p/(?P<slug>[-\w]+)/svn/cvs/$', object_detail,
      { 'queryset' : auth_models.Group.objects.all(),
        'slug_field' : 'name',
        'extra_context' : { 'title' : ("Subversion Repositories") },
        'template_name' : 'svmain/group_vcs_svn.html',
        'template_object_name' : 'group', },
      name='group_vcs_svn'),
  url(r'^p/(?P<slug>[-\w]+)/arch/cvs/$', object_detail,
      { 'queryset' : auth_models.Group.objects.all(),
        'slug_field' : 'name',
        'extra_context' : { 'title' : ("GNU Arch Repositories") },
        'template_name' : 'svmain/group_vcs_arch.html',
        'template_object_name' : 'group', },
      name='group_vcs_arch'),
  url(r'^p/(?P<slug>[-\w]+)/git/cvs/$', object_detail,
      { 'queryset' : auth_models.Group.objects.all(),
        'slug_field' : 'name',
        'extra_context' : { 'title' : ("Git Repositories") },
        'template_name' : 'svmain/group_vcs_git.html',
        'template_object_name' : 'group', },
      name='group_vcs_git'),
  url(r'^p/(?P<slug>[-\w]+)/hg/cvs/$', object_detail,
      { 'queryset' : auth_models.Group.objects.all(),
        'slug_field' : 'name',
        'extra_context' : { 'title' : ("Mercurial Repositories") },
        'template_name' : 'svmain/group_vcs_hg.html',
        'template_object_name' : 'group', },
      name='group_vcs_hg'),
  url(r'^p/(?P<slug>[-\w]+)/bzr/cvs/$', object_detail,
      { 'queryset' : auth_models.Group.objects.all(),
        'slug_field' : 'name',
        'extra_context' : { 'title' : ("Bazaar Repositories") },
        'template_name' : 'svmain/group_vcs_bzr.html',
        'template_object_name' : 'group', },
      name='group_vcs_bzr'),

)
urlpatterns += decorated_patterns ('', login_required,
  url(r'^p/(?P<slug>[-\w]+)/join/$', views.group_join),
)
urlpatterns += decorated_patterns ('', only_project_admin,
  url(r'^p/(?P<slug>[-\w]+)/admin/$', views.group_admin,
      name='group_admin'),
  url(r'^p/(?P<slug>[-\w]+)/admin/info/$', views.group_admin_info,
      { 'post_save_redirect' : '../../',  # back to project page to see the changes
        'extra_context' : { 'title' : _("Editing public info") }, },
      name='group_admin_info'),
  url(r'^p/(?P<slug>[-\w]+)/admin/features/$', views.group_admin_features,
      { 'extra_context' : { 'title' : _("Select features") },
        'post_save_redirect': ''},
      name='group_admin_features'),
  url(r'^p/(?P<slug>[-\w]+)/admin/members/$', views.group_admin_members,
      { 'extra_context' : { 'title' : _("Manage members") }, },
      name='group_admin_members'),
  url(r'^p/(?P<slug>[-\w]+)/admin/members/add/$', views.group_admin_members_add,
      { 'extra_context' : { 'title' : _("Manage members") }, },
      name='group_admin_members_add'),
)

urlpatterns += patterns ('',
  url(r'^license/$', 'django.views.generic.list_detail.object_list',
      { 'queryset' : svmain_models.License.objects.all(),
        'extra_context' : { 'title' : _("License list") }, },
      name='license_list'),
  url(r'^license/(?P<slug>[-\w]+)$', object_detail,
      { 'queryset' : svmain_models.License.objects.all(),
        'extra_context' : { 'title' : _("License detail") }, },
      name='license_detail'),
)

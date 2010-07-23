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

import savane.svmain.models as svmain_models
import django.contrib.auth.models as auth_models
import views
from savane.filters import search

urlpatterns = patterns ('',)

urlpatterns += patterns ('',
  url(r'^$', 'django.views.generic.simple.direct_to_template',
      { 'template' : 'index.html',
        'extra_context' : { 'has_left_menu': False } },
      name='homepage'),
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
        'extra_context' : { 'title' : 'Users' },
        'template_name' : 'svmain/user_list.html' },
      name='savane.svmain.user_list'),
  url(r'^u/(?P<slug>[-\w]+)$', object_detail,
      { 'queryset' : auth_models.User.objects.all(),
        'slug_field' : 'username',
        'extra_context' : { 'title' : 'User detail' },
        'template_name' : 'svmain/user_detail.html', },
      name='savane.svmain.user_detail'),
  url(r'^us/(?P<slug>[-\w]+)$', views.user_redir),
  url(r'^users/(?P<slug>[-\w]+)/?$', views.user_redir),
)

from django.contrib.auth.admin import GroupAdmin
urlpatterns += patterns ('',
  url(r'^p/$',
      search(object_list),
      { 'queryset': auth_models.Group.objects.all(),
        'paginate_by': 20,
        'model_admin': GroupAdmin,
        'extra_context' : { 'title' : 'Projects' },
        'template_name' : 'svmain/group_list.html' },
      name='savane.svmain.group_list'),
  url(r'^p/(?P<slug>[-\w]+)$', object_detail,
      { 'queryset' : auth_models.Group.objects.all(),
        'slug_field' : 'name',
        'extra_context' : { 'title' : 'Project summary' },
        'template_name' : 'svmain/group_detail.html', },
      name='savane.svmain.group_detail'),
  url(r'^pr/(?P<slug>[-\w]+)$', views.group_redir),
  url(r'^projects/(?P<slug>[-\w]+)$', views.group_redir),

  url(r'^license/$', 'django.views.generic.list_detail.object_list',
      { 'queryset' : svmain_models.License.objects.all(),
        'extra_context' : { 'title' : 'License list' }, },
      name='savane.svmain.license_list'),
  url(r'^license/(?P<slug>[-\w]+)$', object_detail,
      { 'queryset' : svmain_models.License.objects.all(),
        'extra_context' : { 'title' : 'License detail' }, },
      name='savane.svmain.license_detail'),
)

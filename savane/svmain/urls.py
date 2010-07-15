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

from savane.svmain import models as svmain_models
import views

urlpatterns = patterns ('',
  url(r'^$', 'django.views.generic.simple.direct_to_template',
      { 'template' : 'index.html',
        'extra_context' : { 'has_left_menu': False } },
      name='homepage'),
  url(r'^contact$', 'django.views.generic.simple.direct_to_template',
      { 'template' : 'contact.html' },
      name='contact'),

  # TODO: not sure about the views naming convention - all this
  # "models in 'svmain', views in 'my'" is getting messy, probably a
  # mistake from me (Beuc) :P
  url(r'^p/(?P<slug>[-\w]+)$', 'django.views.generic.list_detail.object_detail',
      { 'queryset' : svmain_models.ExtendedGroup.objects.all(),
        'slug_field' : 'name' },
      name='savane.svmain.group_detail'),
  url(r'^pr/(?P<slug>[-\w]+)$', views.group_redir),
  url(r'^projects/(?P<slug>[-\w]+)$', views.group_redir),

  url(r'^u/(?P<slug>[-\w]+)$', 'django.views.generic.list_detail.object_detail',
      { 'queryset' : svmain_models.ExtendedUser.objects.all(),
        'slug_field' : 'username' },
      name='savane.svmain.user_detail'),
  url(r'^us/(?P<slug>[-\w]+)$', views.user_redir),
  url(r'^users/(?P<slug>[-\w]+)/?$', views.user_redir),

  url(r'^license/$', 'django.views.generic.list_detail.object_list',
      { 'queryset' : svmain_models.License.objects.all(), },
      name='savane.svmain.license_list'),
  url(r'^license/(?P<slug>[-\w]+)$', 'django.views.generic.list_detail.object_detail',
      { 'queryset' : svmain_models.License.objects.all(), },
      name='savane.svmain.license_detail'),
)

# News URLs
# Copyright (C) 2010  Sylvain Beucler
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

from django.conf import settings
from django.conf.urls.defaults import *
from django.utils.translation import ugettext, ugettext_lazy as _
from django.views.generic.list_detail import object_detail, object_list
from django.views.generic.create_update import create_object, update_object
from django.contrib.auth.decorators import login_required
import models as svnews_models
import views
#import forms as svnews_forms
from savane.perms import only_project_admin
from savane.django_utils import decorated_patterns

urlpatterns = patterns ('',)

urlpatterns += patterns ('',
  url(r'^$', views.redirect_to_admin_group,
      {},
      name='news_list_admin_group'),
  url(r'^(?P<object_id>\d+)/$', object_detail,
      { 'queryset' : svnews_models.News.objects.filter(is_approved__in=(0,1,2,)) },
      name='news_detail'),
  url(r'^(?P<slug>[-\w]+)/$', views.news_list_by_group,
      { 'queryset' : svnews_models.News.objects.filter(is_approved__in=(0,1,2,)).order_by('-date') },
      name='news_list_by_group'),
)
urlpatterns += decorated_patterns ('', only_project_admin,
  url(r'^(?P<slug>[-\w]+)/manage/$', object_list,
      { 'extra_context' : { 'title' : _("Manage"), }, },
      name='news_manage_by_group'),
  url(r'^(?P<slug>[-\w]+)/(?P<object_id>\d+)/edit/$', update_object,
      { 'model' : svnews_models.News,
        'extra_context' : { 'title' : _("Manage"), }, },
      name='news_edit'),
)

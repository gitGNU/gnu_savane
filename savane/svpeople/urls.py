# Jobs URLs
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

from django.conf.urls.defaults import *
import views
from django.utils.translation import ugettext, ugettext_lazy as _
from django.views.generic.list_detail import object_detail
from savane.utils import get_site_name
import models as svpeople_models

urlpatterns = patterns ('',)

urlpatterns += patterns ('',
  url(r'^$', views.index,
      { 'extra_context' : { 'title' : _("Projects needing help"), }, },
      name='index'),
  url(r'^category/(?P<category_id>\d+)/$', views.job_list_by_category,
      {},
      name='job_list_by_category'),
  url(r'^type/(?P<type_id>\d+)/$', views.job_list_by_type,
      { 'extra_context' : { 'title' : _("Project help wanted"), }, },
      name='job_list_by_type'),
  url(r'^job/(?P<object_id>\d+)/$', object_detail,
      { 'queryset' : svpeople_models.Job.objects.all(),
        'extra_context' : { 'title' : _("View a job"), }, },
      name='job_detail'),
)

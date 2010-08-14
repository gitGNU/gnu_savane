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
from django.views.generic.create_update import create_object, update_object
from django.contrib.auth.decorators import login_required
from savane.utils import get_site_name
import models as svpeople_models
import forms as svpeople_forms
from savane.perms import only_project_admin
from savane.django_utils import decorated_patterns

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
  url(r'^group/(?P<slug>[-\w]+)/$', views.job_list_by_group,
      { 'extra_context' : { 'title' : _("Looking for a job to edit"), }, },
      name='job_list_by_group'),
  url(r'^job/(?P<object_id>\d+)/$', object_detail,
      { 'queryset' : svpeople_models.Job.objects.all(),
        'extra_context' : { 'title' : _("View a job"), }, },
      name='job_detail'),
  # access restriction done in job_update():
  url(r'^job/(?P<object_id>\d+)/edit/$', views.job_update,
      { 'extra_context' : { 'title' : _("Edit a job for your project"),
                            'action' : _("Update") }, },
      name='job_edit'),
)
urlpatterns += decorated_patterns ('', only_project_admin,
  url(r'^group/(?P<slug>[-\w]+)/add/$', views.job_add,
      { 'extra_context' : { 'title' : _("Create a job for your project"),
                            'add' : True,
                            'action' : _("Continue >>") }, },
      name='job_add'),
)
urlpatterns += decorated_patterns ('', login_required,
  url(r'^my_info/$', views.userinfo_update,
      { 'extra_context' : { 'title' : _("Edit your resume & skills"), }, },
      name='userinfo_update'),
)

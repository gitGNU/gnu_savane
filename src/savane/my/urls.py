# Accounts URLs
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
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template
from django.views.generic.list_detail import object_list
import views
import savane.svmain.models as svmain_models
from decorator import decorator

@decorator
def only_mine(f, *args, **kwargs):
    """Filter a generic query_set to only display objets related to
    the current user"""
    request = args[0]
    user = request.user
    print kwargs
    kwargs['queryset'] = kwargs['queryset'].filter(user=user.id)
    return f(*args, **kwargs)

@only_mine
def object_list__only_mine(*args, **kwargs):
    return object_list(*args, **kwargs)

@login_required
def direct_to_template__login_required(*args, **kwargs):
    return direct_to_template(*args, **kwargs)

urlpatterns = patterns ('',
  url(r'^$', direct_to_template__login_required,
      { 'template' : 'my/index.html' },
      name='savane.my.views.index'),
  url('^conf/$', views.sv_conf),
  url('^conf/resume_skill$', views.sv_resume_skill),
  url('^conf/ssh_gpg$', views.sv_ssh_gpg),
  url('^conf/ssh_gpg$', views.sv_ssh_gpg),
  url(r'^groups/$', object_list__only_mine,
      { 'queryset' : svmain_models.ExtendedGroup.objects.all() },
      name='savane.my.generic.group_list'),
)

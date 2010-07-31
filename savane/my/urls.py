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
import django.contrib.auth.models as auth_models
from savane.my.filters import *
from savane.django_utils import decorated_patterns
from django.utils.translation import ugettext, ugettext_lazy as _

urlpatterns = patterns ('',)

urlpatterns += decorated_patterns ('', login_required,
  url(r'^$', direct_to_template,
      { 'template' : 'my/index.html',
        'extra_context' : { 'title' : _("My account configuration"), }, },
      name='index'),
  url('^contact/$', views.contact,
      { 'extra_context' : {'title' : _("Contact info"), }, },
      name='conf'),
  url('^conf/resume_skills/$', views.resume_skills,
      { 'extra_context' : {'title' : _("Edit your resume & skills"), } },
      name='resume_skills'),
  url('^conf/ssh/$', views.ssh,
      { 'extra_context' : {'title' : _("Change authorized keys"), } },
      name='ssh'),
  url('^conf/ssh/delete/$', views.ssh_delete,
      name='ssh_delete'),
  url('^i18n/$', direct_to_template,
      { 'template' : 'my/i18n.html',
        'extra_context' : {'title' : _("Language"), } },
      name='i18n'),
  # TODO: set_lang only lasts for the user's session
  url('^i18n/', include('django.conf.urls.i18n')),
  url(r'^groups/$', only_mine(object_list),
      { 'queryset' : auth_models.Group.objects.all(),
        'extra_context' : { 'title' : _("My groups"), },
        'template_name' : 'svmain/group_list.html', },
      name='group_list'),
  url(r'^memberships/$', only_mine(object_list),
      { 'queryset' : svmain_models.Membership.objects.all(),
        'extra_context' : { 'title' : _("My memberships"), },
        },
      name='membership_list'),
)

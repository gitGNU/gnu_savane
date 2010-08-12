# Accounts URLs
# Copyright (C) 2009, 2010  Sylvain Beucler
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
  url(r'^$', views.index,
      { 'extra_context' : { 'title' : _("My account configuration"), }, },
      name='index'),
  url('^contact/$', views.contact,
      { 'extra_context' : {'title' : _("Contact info"), }, },
      name='contact'),
  url('^email_confirm/(?P<confirm_hex>\w+)/$', views.email_confirm,
      name='email_confirm'),
  url('^email_cancel/(?P<cancel_hex>\w+)/$', views.email_cancel,
      name='email_cancel'),
  url('^resume_skills/$', views.resume_skills,
      { 'extra_context' : {'title' : _("Edit your resume & skills"), } },
      name='resume_skills'),
  url('^ssh/$', views.ssh,
      { 'extra_context' : {'title' : _("Change authorized keys"), } },
      name='ssh'),
  url('^ssh/delete/$', views.ssh_delete,
      name='ssh_delete'),
)
# language can be set for anonymous users too
import django.views.i18n
urlpatterns += patterns ('',
  url('^i18n/$', views.i18n,
      { 'extra_context' : {'title' : _("Language"), } },
      name='i18n'),
  url('^i18n/setlang/', views.i18n_persistent(django.views.i18n.set_language),
      name='set_language'),
)

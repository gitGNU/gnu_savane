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

def only_mine(f):
    """Filter a generic query_set to only display objets related to
    the current user"""
    def _dec(request, queryset, *args, **kwargs):
        user = request.user
        queryset = queryset.filter(user=user.id)
        return f(request, queryset, *args, **kwargs)
    return _dec

# Batch-decorator for urlpatterns
# http://www.djangosnippets.org/snippets/532/
from django.core.urlresolvers import RegexURLPattern
class DecoratedURLPattern(RegexURLPattern):
    def resolve(self, *args, **kwargs):
        result = RegexURLPattern.resolve(self, *args, **kwargs)
        if result:
            result = list(result)
            result[0] = self._decorate_with(result[0])
        return result
def decorated_patterns(prefix, func, *args):
    result = patterns(prefix, *args)
    if func:
        for p in result:
            if isinstance(p, RegexURLPattern):
                p.__class__ = DecoratedURLPattern
                p._decorate_with = func
    return result

urlpatterns = decorated_patterns ('', login_required,
  url(r'^$', direct_to_template,
      { 'template' : 'my/index.html' },
      name='savane.my.views.index'),
  url('^conf/$', views.sv_conf),
  url('^conf/resume_skill$', views.sv_resume_skill),
  url('^conf/ssh_gpg$', views.sv_ssh_gpg),
  url(r'^groups/$', only_mine(object_list),
      { 'queryset' : svmain_models.ExtendedGroup.objects.all() },
      name='savane.my.group_list'),
)

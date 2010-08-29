# News
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
from django.shortcuts import get_object_or_404
from django.views.generic.simple import redirect_to
from django.views.generic.list_detail import object_list, object_detail
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _, ungettext
import django.contrib.auth.models as auth_models
import models as svnews_models

def redirect_to_admin_group(*args, **kwargs):
    group = get_object_or_404(auth_models.Group, name=settings.SV_ADMIN_GROUP)
    kwargs['url']=reverse('savane:svnews:news_list_by_group', args=[group.name])
    return redirect_to(*args, **kwargs)

def news_list_by_group(request, slug, *args, **kwargs):
    group = get_object_or_404(auth_models.Group, name=slug)
    kwargs['queryset'] = kwargs['queryset'].filter(group=group)
    kwargs['extra_context'] = kwargs.get('extra_context', {})
    kwargs['extra_context']['group'] = group
    return object_list(request, *args, **kwargs)

def news_detail(request, *args, **kwargs):
    news = get_object_or_404(svnews_models.News, pk=kwargs['object_id'])
    group = news.group
    kwargs['extra_context'] = kwargs.get('extra_context', {})
    kwargs['extra_context']['group'] = group
    kwargs['extra_context']['group_news'] = svnews_models.News \
        .approved_objects.filter(group=group) \
        .select_related()
    return object_detail(request, *args, **kwargs)

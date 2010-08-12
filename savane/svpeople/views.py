# Jobs
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

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import ugettext as _, ungettext
from django.db import models
from annoying.decorators import render_to
from savane.middleware.exception import HttpAppException
import savane.svmain.models as svmain_models
import models as svpeople_models

@render_to('svpeople/index.html', mimetype=None)
def index(request, extra_context={}):
    category_list = svpeople_models.Category.objects.all()
    type_list = svmain_models.GroupConfiguration.objects.all()
    type_and_count = [ {'type' : t,
                        'count' : svpeople_models.Job.open_objects \
                            .filter(group__svgroupinfo__type=t).count() }
                       for t in type_list ]
    context = { 'category_list' : category_list,
                'type_and_count' : type_and_count,
                }
    context.update(extra_context)
    return context

@render_to('svpeople/job_list_by_category.html', mimetype=None)
def job_list_by_category(request, category_id, extra_context={}):
    category = get_object_or_404(svpeople_models.Category, pk=category_id)
    object_list = svpeople_models.Job.open_objects \
        .filter(category=category).order_by('-date') \
        .select_related('category', 'group__svgroupinfo__type')
        # select_related() gets all fields, it doesn't work at the field level (e.g. category__name)
        # only() does not work on related objects as of 1.2 :/
        #.only('title', 'category__label', 'date', 'group__svgroupinfo__full_name', 'group__svgroupinfo__type__name')
    context = {
        'category' : category,
        'object_list' : object_list,
        }
    context.update(extra_context)
    return context

@render_to('svpeople/job_list_by_type.html', mimetype=None)
def job_list_by_type(request, type_id, extra_context={}):
    type = get_object_or_404(svmain_models.GroupConfiguration, pk=type_id)
    object_list = svpeople_models.Job.open_objects \
        .filter(group__svgroupinfo__type=type).order_by('category', 'group__name') \
        .select_related('category', 'group__svgroupinfo__type')
    context = {
        'type' : type,
        'object_list' : object_list,
        }
    context.update(extra_context)
    return context

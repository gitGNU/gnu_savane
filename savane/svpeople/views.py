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
from annoying.decorators import render_to
from savane.middleware.exception import HttpAppException
import savane.svmain.models as svmain_models
import models as svpeople_models

@render_to('svpeople/index.html', mimetype=None)
def index(request, extra_context={}):
    category_list = svpeople_models.Category.objects.all()
    type_list = svmain_models.GroupConfiguration.objects.all()
    context = { 'category_list' : category_list,
                'type_list' : type_list,
                }
    context.update(extra_context)
    return context

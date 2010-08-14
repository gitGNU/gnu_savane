# Trackers
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

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _, ungettext
import django.contrib.auth.models as auth_models
import savane.tracker.models as tracker_models
from annoying.decorators import render_to
from savane.middleware.exception import HttpAppException

@render_to('tracker/item_form.html', mimetype=None)
def item_detail(request, tracker, object_id, extra_context={}):
    if tracker not in [k for (k,v) in tracker_models.Tracker.NAME_CHOICES]:
        raise HttpAppException("Invalid tracker")

    kwargs = {'public_%s' % tracker : object_id}
    item = get_object_or_404(tracker_models.Item, **kwargs)

    context = {
        'object' : item,
        }
    context.update(extra_context)
    return context

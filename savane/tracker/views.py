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
from django.views.generic.list_detail import object_detail, object_list
import savane.tracker.models as tracker_models
from annoying.decorators import render_to
from savane.middleware.exception import HttpAppException

def item_list(request, tracker, extra_context={}, paginate_by=None):
    queryset = tracker_models.Item.objects.filter(tracker=tracker).order_by('-public_%s' % tracker)
    return object_list(request, queryset=queryset, extra_context=extra_context,
                       paginate_by=paginate_by)

@render_to('tracker/item_form.html', mimetype=None)
def item_detail(request, tracker, object_id, extra_context={}):
    tracker = get_object_or_404(tracker_models.Tracker, name=tracker)

    kwargs = {tracker.get_public_id_item_field() : object_id}
    item = get_object_or_404(tracker_models.Item, **kwargs)

    if item.privacy == 0:  # reverse meaning...
        # Allowed: members with 'private items' privs
        if not request.user.is_superuser:
            raise HttpAppException(_("Access denied") + _(": ") + _("private item"))

    context = {
        'object' : item,
        }
    context.update(extra_context)
    return context

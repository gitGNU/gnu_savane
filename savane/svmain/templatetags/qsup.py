# Top-level menu
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

from django import template
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.translation import ugettext as _
import savane.svmain.models as svmain_models

register = template.Library()

@register.inclusion_tag('svmain/identity.html', takes_context=True)
def qsup(context, param_name, param_value):
    """
    Query_String UPdate
    Write a querystring taking into account the current arguments

    Requires access to 'reuuest' in 'context'
    (cf. 'django.core.context_processors.request')

    Written as in inclusion_tag with a 'passthrough' template because
    it's simpler and more maintainable than reimplementing a template
    tag parser.
    """

    params = context['request'].GET.copy()
    # Update query_string
    params[param_name] = param_value
    return { 'text': params.urlencode() }

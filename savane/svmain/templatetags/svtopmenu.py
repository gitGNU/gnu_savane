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
import savane.svmain.models as svmain_models
from django.conf import settings

register = template.Library()

@register.inclusion_tag('svmain/svtopmenu.html', takes_context=True)
def svtopmenu(context, menu_name):
    """
    Return info to build the top menu, including menu structure and
    page icon.

    TODO: use context['request'].PATH_INFO to determine if a link is
    the current URL, and mark it so we can apply a different CSS style
    on it.
    """
    icon = 'main'
    entries = []

    if menu_name == 'group':
        entry_home = { 'text' : 'Home',
                   'href' : reverse('savane.svmain.group_detail', args=[context['group'].name]),
                   'title': "Project Main Page at %s" % 'this website'}
        entry_home['children'] = []
        entry_home['children'].append({'text' : 1.1, 'href' : 1.1, 'title': 1.1 })
        if (context['user'].groups.filter(name=context['group']).count()):
            entry_home['children'].append({'separator' : True })
            entry_home['children'].append({'text' : "I'm a member", 'href' : 1.2, 'title': 1.2 })
        if (svmain_models.Membership.objects.filter(user=context['user'], group=context['group'], admin_flags='A').count()):
            entry_home['children'].append({'separator' : True })
            entry_home['children'].append({'text' : "I'm an admin",
                                           'href' : reverse('savane.svmain.group_admin', args=[context['group'].name]) })

        entry_test = {
                    'text' : 2, 'href' : 2, 'title': 2, 'children':
                    [
                        {'text' : 2.1, 'href' : 2.1, 'title': 2.1 },
                    ]
                }

        entries.append(entry_home)
        entries.append(entry_test)
    elif menu_name == 'my':
        pass

    context = {
        'menu_name' : menu_name,
        'entries' : entries,
        }
    return context

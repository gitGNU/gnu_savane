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
    group = context['group']

    if menu_name == 'group':
        entry_home = { 'text' : 'Main',
                   'href' : reverse('savane:svmain:group_detail', args=[group.name]),
                   'title': "Project Main Page at %s" % 'this website'}
        entry_home['children'] = []
        entry_home['children'].append({'text' : _("Main"),
                                       'href' : reverse('savane:svmain:group_detail', args=[group.name]) })
        entry_home['children'].append({'text' : _("View members"),
                                       'href' : reverse('savane:svmain:group_memberlist', args=[group.name]) })
        entry_home['children'].append({'text' : _("GPG keyring"),
                                       'href' : reverse('savane:svmain:group_gpgkeyring', args=[group.name]) })
        if (svmain_models.Membership.is_admin(context['user'], group)):
            entry_home['children'].append({'separator' : True })
            entry_home['children'].append({'text' : _("Administer:"), 'strong': True,
                                           'href' : reverse('savane:svmain:group_admin', args=[group.name]) })
            entry_home['children'].append({'text' : _("Edit public info"),
                                           'href' : reverse('savane:svmain:group_admin_info', args=[group.name]) })
            entry_home['children'].append({'text' : _("Select features"),
                                           'href' : reverse('savane:svmain:group_admin_features', args=[group.name]) })
            entry_home['children'].append({'text' : _("Manage members"),
                                           'href' : reverse('savane:svmain:group_admin_members', args=[group.name]) })

        entry_homepage = {'text' : _("Homepage"),
                          'href' : group.svgroupinfo.get_url_homepage(),
                          'title': _("Browse project homepage (outside of Savane)")}

        entry_download = {'text' : _("Download"),
                          'href' : group.svgroupinfo.get_url_download(),
                          'title': _("Download area: files released")}

        entry_mailinglists = {'text' : _("Mailing lists") + " (TODO)",
                              'href' : '',
                              'title': _("List existing mailing lists")}
        entry_mailinglists['children'] = []
        entry_mailinglists['children'].append({'text' : _("Browse") + " (TODO)",
                                                   'href' : '' })
        if (svmain_models.Membership.is_admin(context['user'], group)):
            entry_mailinglists['children'].append({'separator' : True })
            entry_mailinglists['children'].append({'text' : _("Configure:") + " (TODO)", 'strong': True,
                                                   'href' : '' })
 
        entry_sourcecode = {'text' : _("Source code") + " (TODO)",
                           'href' : '',
                           'title': _("Source Code Management")}
        entry_sourcecode['children'] = []
        entry_sourcecode['children'].append({'text' : _("Use X") + " (TODO)",
                                               'href' : '' })
 

        entries.append(entry_home)
        entries.append(entry_homepage)
        entries.append(entry_download)
        entries.append(entry_mailinglists)
        entries.append(entry_sourcecode)
    elif menu_name == 'my':
        pass

    context = {
        'menu_name' : menu_name,
        'entries' : entries,
        }
    return context

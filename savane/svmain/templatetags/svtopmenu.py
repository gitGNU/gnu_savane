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
        # Main
        entry_home = { 'text' : _("Main"),
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

        # Homepage
        entry_homepage = {'text' : _("Homepage"),
                          'href' : group.svgroupinfo.get_url_homepage(),
                          'title': _("Browse project homepage (outside of Savane)")}

        # Homepage
        entry_download = {'text' : _("Download"),
                          'href' : group.svgroupinfo.get_url_download(),
                          'title': _("Download area: files released")}

        # Mailing lists
        entry_mailinglist = {'text' : _("Mailing lists"),
                              'href' : reverse('savane:svmain:group_mailinglist', args=[group.name]),
                              'title': _("List existing mailing lists")}
        entry_mailinglist['children'] = []
        entry_mailinglist['children'].append({'text' : _("Browse"),
                                               'href' : reverse('savane:svmain:group_mailinglist', args=[group.name]) })
        if (svmain_models.Membership.is_admin(context['user'], group)):
            entry_mailinglist['children'].append({'separator' : True })
            entry_mailinglist['children'].append({'text' : _("Configure:") + " (TODO)", 'strong': True,
                                                   'href' : '' })

        # Source code
        entry_sourcecode = {'text' : _("Source code"),
                           'href' : '',
                           'title': _("Source Code Management")}
        entry_sourcecode['children'] = []
        entry_sourcecode['children'].append({'text' : _("Use CVS"),
                                             'href' :  reverse('savane:svmain:group_scm_cvs', args=[group.name]) })

        # Add 'em all!
        entries.append(entry_home)
        entries.append(entry_homepage)
        entries.append(entry_download)
        entries.append(entry_mailinglist)
        if len(entry_sourcecode['children']) > 0:
            entries.append(entry_sourcecode)
    elif menu_name == 'my':
        # Not sure if we should make it, the current interface works
        # without it
        pass

    context = {
        'menu_name' : menu_name,
        'entries' : entries,
        }
    return context

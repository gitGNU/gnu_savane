# Webmail for Django's locmem mail backend
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

from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext as _, ungettext
from annoying.decorators import render_to
from django.core import mail

@render_to('webmail_locmem/mail_list.html')
def index(request, extra_context={}):
    if not hasattr(mail, 'outbox'):
        object_list = []
    else:
        object_list = mail.outbox

    # Attributes: ['attach', 'attach_file', 'attachments', 'bcc',
    # 'body', 'connection', 'content_subtype', 'encoding',
    # 'extra_headers', 'from_email', 'get_connection', 'message',
    # 'mixed_subtype', 'recipients', 'send', 'subject', 'to']

    empty = True
    for i in object_list:
        if i:
            empty = False

    context = { 'object_list' : object_list,
                'empty' : empty
                }
    context.update(extra_context)
    return context

@render_to('webmail_locmem/mail_detail.html')
def mail_detail(request, object_id, extra_context={}):
    object_id = int(object_id)
    if not hasattr(mail, 'outbox'):
        object_list = []
    else:
        object_list = mail.outbox

    object = None
    if object_id <= len(object_list):
        object = mail.outbox[object_id-1]
    if object is None:
        raise Http404(_("No such message"))

    context = { 'object' : object,
                'object_id' : object_id,
                'title' : _("Message #%d") % object_id }
    context.update(extra_context)
    return context

@render_to('webmail_locmem/mail_delete.html')
def mail_delete(request, object_id, extra_context={}):
    object_id = int(object_id)
    try:
        object_list = mail.outbox
        object = mail.outbox[object_id-1]
    except AttributeError, IndexError:
        raise Http404(_("No such message"))

    if request.method == 'POST':
        print mail.outbox
        mail.outbox[object_id-1] = None
        print mail.outbox
        messages.success(request, "Message #%d deleted" % object_id)
        return HttpResponseRedirect(reverse('mail_list'))

    context = { 'object' : object,
                'title' : _("Delete message #%d?") % int(object_id) }
    context.update(extra_context)
    return context

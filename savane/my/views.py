# Manage user attributes
# Copyright (C) 2009  Sylvain Beucler
# Copyright (C) 2009  Jonathan Gonzalez V.
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

from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import ugettext as _, ungettext
from django.core import mail
from django.conf import settings
import savane.svmain.models as svmain_models
from savane.my.forms import *
from annoying.decorators import render_to
from savane.utils import get_site_name
from savane.middleware.exception import HttpAppException
import random
import smtplib

@login_required()
@render_to('my/index.html', mimetype=None)
def index(request, extra_context={}):
    svmain_models.Membership.tidy(user=request.user)
    membership_list = svmain_models.Membership.objects.filter(user=request.user)

    context = { 'object_list' : membership_list, }
    context.update(extra_context)
    return context

@login_required()
@render_to('my/contact.html', mimetype=None)
def contact(request, extra_context={}):
    form_mail = MailForm(initial={'email' : request.user.email})
    form_identity = IdentityForm(initial={'first_name' : request.user.first_name,
                                          'last_name' : request.user.last_name,
                                          'gpg_key' : request.user.svuserinfo.gpg_key, })
    form = None

    if request.method == 'POST':
        if 'update_mail' in request.POST:
            form_mail = MailForm(request.POST)
            form = form_mail
        elif 'update_identity' in request.POST:
            form_identity = IdentityForm(request.POST)
            form = form_identity

        if form is not None and form.is_valid():
            if 'update_mail' in request.POST:
                request.user.svuserinfo  # ugly work-around
                request.user.svuserinfo.email_new = request.POST['email']
                request.user.svuserinfo.email_hash_confirm = random.getrandbits(64-1)
                request.user.svuserinfo.email_hash_cancel = random.getrandbits(64-1)
                request.user.svuserinfo.save()

                hex_confirm = hex(request.user.svuserinfo.email_hash_confirm)[2:-1]
                hex_cancel = hex(request.user.svuserinfo.email_hash_cancel)[2:-1]
                try:
                    # TODO: we might use templates instead of plain string concatenation
                    url = 'http://' + Site.objects.get_current().domain + reverse('savane:my:email_confirm', args=[hex_confirm])
                    subject = get_site_name() + ' ' + _("verification")
                    message = (_("You have requested a change of email address on %s.\n"
                                 + "Please visit the following URL to complete the email change:") % get_site_name()
                               + "\n\n"
                               + url
                               + "\n\n"
                               + _("-- the %s team.") % get_site_name()
                               + "\n")
                    to = [request.user.svuserinfo.email_new]
                    mail.send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, to)
		  
                    url = 'http://' + Site.objects.get_current().domain + reverse('savane:my:email_cancel', args=[hex_cancel])
                    subject = get_site_name() + ' ' + _("verification")
                    message = (_("Someone, presumably you, has requested a change of email address on %s.\n"
                                 + "If it wasn't you, maybe someone is trying to steal your account..."
                                 + "\n\n"
                                 + "Your current address is %s, the supposedly new address is %s."
                                 + "\n\n") % (get_site_name(), request.user.email, request.user.svuserinfo.email_new)
                               + _("If you did not request that change, please visit the following URL to discard\n"
                                   + "the email change and report the problem to us:")
                               + "\n\n"
                               + url
                               + "\n\n"
                               + _("-- the %s team.") % get_site_name()
                               + "\n")
                    to = [request.user.email]
                    if request.user.email != '':
                        mail.send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, to)
                except smtplib.SMTPException:
		      messages.error(request, _("The system reported a failure when trying to send the confirmation mail."
                                                + " Please retry and report that problem to administrators."))
                messages.success(request, _("Confirmation mailed to %s.") % request.user.svuserinfo.email_new
                                 + ' ' + _("Follow the instructions in the email to complete the email change."))
                
                
                return HttpResponseRedirect("")  # reload
            elif 'update_identity' in request.POST:
                request.user.first_name = request.POST['first_name']
                request.user.last_name = request.POST['last_name']
                request.user.save()
                request.user.svuserinfo
                request.user.svuserinfo.gpg_key = request.POST['gpg_key']
                request.user.svuserinfo.save()
                messages.success(request, _("Personal information changed."))
                return HttpResponseRedirect("")  # reload

    context = { 'form_mail' : form_mail,
                'form_identity' : form_identity,
                }
    context.update(extra_context)
    return context

@login_required()
@render_to('svmain/generic_confirm.html', mimetype=None)
def email_confirm(request, confirm_hex):
    if request.user.svuserinfo.email_hash_confirm == int(confirm_hex, 16):
        if request.method == 'POST':
            request.user.email = request.user.svuserinfo.email_new
            request.user.save()
            request.user.svuserinfo.email_hash_confirm = None
            request.user.svuserinfo.email_hash_cancel = None
            request.user.svuserinfo.email_new = ''
            request.user.svuserinfo.save()
            messages.success(request, _("Email address updated."))
            return HttpResponseRedirect(reverse('savane:my:contact'))
        return {'title': _("Confirm Email change"),
                'text': _('Confirm your e-mail change to %s?') % request.user.svuserinfo.email_new }
    else:
        raise HttpAppException(_("Invalid confirmation hash"))

@login_required()
@render_to('svmain/generic_confirm.html', mimetype=None)
def email_cancel (request, cancel_hex):
    if request.user.svuserinfo.email_hash_cancel == int(cancel_hex, 16):
        if request.method == 'POST':
            request.user.svuserinfo.email_hash_confirm = None
            request.user.svuserinfo.email_hash_cancel = None
            request.user.svuserinfo.email_new = ''
            request.user.svuserinfo.save()
            messages.success(request, _("Address change process discarded."))
            return HttpResponseRedirect(reverse('savane:my:contact'))
        return {'title': _("Cancel Email change"),
                'text': _('Cancel your e-mail change to %s?') % request.user.svuserinfo.email_new}
    else:
        raise HttpAppException(_("Invalid confirmation hash"))

@login_required()
def resume_skills(request, extra_context={}):
    return render_to_response('my/resume_skill.html',
                              extra_context,
                              context_instance=RequestContext(request))

@login_required()
def ssh(request, extra_context={}):
    info = request.user.svuserinfo

    error_msg = None
    success_msg = None

    form = SSHForm()
    ssh_keys = None

    if request.method == 'POST':
        form = None
        form = SSHForm(request.POST, request.FILES)

        if form is not None and form.is_valid():
            keys_saved = 0

            if 'key' in request.POST:
                key = request.POST['key'].strip()
                if len(key) > 0:
                    ssh_key = svmain_models.SshKey(ssh_key=key)
                    request.user.sshkey_set.add(ssh_key)
                    keys_saved += 1

            if 'key_file' in request.FILES:
                ssh_key_file = request.FILES['key_file']
                if ssh_key_file is not None:
                    key = ''
                    for chunk in ssh_key_file.chunks():
                        key = key + chunk
                        if len(key) > 0:
                            ssh_key = svmain_models.SshKey(ssh_key=key)
                            request.user.sshkey_set.add(ssh_key)
                            keys_saved += 1

            if keys_saved > 0:
                messages.success(request, ungettext('Key registered', '%(count)d keys registered', keys_saved) % {
                        'count': keys_saved})
                return HttpResponseRedirect("")  # reload
            else:
                error_msg = _("Error while registering keys")
    else:
        form_ssh = SSHForm()

    keys = request.user.sshkey_set.all()
    if keys is not None:
        ssh_keys = dict()
        for key in keys:
            ssh_keys[key.pk] = ssh_key_fingerprint(key.ssh_key)

    context = { 'form' : form,
                'ssh_keys' : ssh_keys,
                'error_msg' : error_msg,
                'success_msg' : success_msg,
                }
    context.update(extra_context)
    return render_to_response('my/ssh.html',
                              context,
                              context_instance=RequestContext(request))

@login_required()
@render_to('svmain/generic_confirm.html', mimetype=None)
def ssh_delete(request):
    if request.method == 'POST':
        try:
            ssh_key = request.user.sshkey_set.get(pk=request.POST.get('key_pk', 0))
            ssh_key.delete()
        except svmain_models.SshKey.DoesNotExist:
            messages.error(request, _("Cannot remove the selected key"))
        return HttpResponseRedirect("../")
    else:
        return {}

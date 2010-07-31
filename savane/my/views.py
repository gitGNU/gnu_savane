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
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import ugettext as _, ungettext
from savane.svmain.models import SvUserInfo, SshKey
from savane.my.forms import *
from annoying.decorators import render_to

@login_required()
def conf(request, extra_context={}):
    form_mail = MailForm(initial={'email' : request.user.email})
    form_identity = IdentityForm(initial={'first_name' : request.user.first_name,
                                          'last_name' : request.user.last_name})
    form = None

    if request.method == 'POST':
        action = request.POST['action']
        if action == 'update_mail':
            form_mail = MailForm(request.POST)
            form = form_mail
        elif action == 'update_identity':
            form_identity = IdentityForm(request.POST)
            form = form_identity

        if form is not None and form.is_valid():
            if action == 'update_mail':
                new_email = request.POST['email']
                request.user.email = new_email
                request.user.save()
                messages.success(request, _("The e-mail address was successfully updated. New e-mail address is <%s>") % new_email)
                return HttpResponseRedirect("")  # reload
            elif action == 'update_identity':
                request.user.first_name = request.POST['first_name']
                request.user.last_name = request.POST['last_name']
                request.user.save()
                messages.success(request, _("Personal information changed."))
                return HttpResponseRedirect("")  # reload

    context = { 'form_mail' : form_mail,
                'form_identity' : form_identity,
                }
    context.update(extra_context)
    return render_to_response('my/conf.html',
                              context,
                              context_instance=RequestContext(request))

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
                    ssh_key = SshKey(ssh_key=key)
                    request.user.sshkey_set.add(ssh_key)
                    keys_saved += 1

            if 'key_file' in request.FILES:
                ssh_key_file = request.FILES['key_file']
                if ssh_key_file is not None:
                    key = ''
                    for chunk in ssh_key_file.chunks():
                        key = key + chunk
                        if len(key) > 0:
                            ssh_key = SshKey(ssh_key=key)
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
        except SshKey.DoesNotExist:
            messages.error(request, _("Cannot remove the selected key"))
        return HttpResponseRedirect("../")
    else:
        return {}

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
from django import forms
from django.contrib import messages
from savane.svmain.models import SvUserInfo, SshKey
from savane.utils import *
from annoying.decorators import render_to

@login_required()
def sv_conf(request, extra_context={}):
    form_mail = MailForm(initial={'email' : request.user.email})
    form_identity = IdentityForm(initial={'name' : request.user.first_name,
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
                messages.success(request, u"The E-Mail address was succesfully updated. New E-Mail address is <%s>" % new_email)
            elif action == 'update_identity':
                request.user.first_name = request.POST['name']
                request.user.last_name = request.POST['last_name']
                request.user.save()
                messages.success(request, u"Personal information changed.")

    context = { 'form_mail' : form_mail,
                'form_identity' : form_identity,
                }
    context.update(extra_context)
    return render_to_response('my/conf.html',
                              context,
                              context_instance=RequestContext(request))

@login_required()
def sv_resume_skill(request, extra_context={}):
    return render_to_response('my/resume_skill.html',
                              extra_context,
                              context_instance=RequestContext(request))

@login_required()
def sv_ssh_gpg(request, extra_context={}):
    info = request.user.svuserinfo

    error_msg = None
    success_msg = None

    form_ssh = SSHForm()
    form_gpg = GPGForm()
    ssh_keys = None

    if request.method == 'GET' and 'action' in request.GET:
        action = request.GET['action']
        if action == 'delete_key':
            key_pk = request.GET['key_pk']
            try:
                ssh_key = request.user.sshkey_set.get(pk=key_pk)
                ssh_key.delete()
            except:
                error_msg = 'Cannot remove the selected key'

    if request.method == 'POST':
        form = None
        action = request.POST['action']
        if action == 'add_ssh':
            form_ssh = SSHForm( request.POST, request.FILES )
            form = form_ssh
        elif action == 'update_gpg':
            form_gpg = GPGForm( request.POST )

        if form is not None and form.is_valid():
            if action == 'add_ssh':
                if 'key' in request.POST:
                    key = request.POST['key'].strip()
                    if len(key) > 0:
                        ssh_key = SshKey(ssh_key=key)
                        request.user.sshkey_set.add(ssh_key)
                        success_msg = 'Authorized keys stored.'

                if 'key_file' in request.FILES:
                    ssh_key_file = request.FILES['key_file']
                    if ssh_key_file is not None:
                        key = ''
                        for chunk in ssh_key_file.chunks():
                            key = key + chunk

                            if len(key) > 0:
                                ssh_key = SshKey(ssh_key=key)
                                request.user.sshkey_set.add(ssh_key)
                                success_msg = 'Authorized keys stored.'

                form_ssh = SSHForm()

                if len( success_msg ) == 0:
                    error_msg = 'Cannot added the public key'

            elif action == 'update_gpg':
                if 'gpg_key' in request.POST:
                    gpg_key = request.POST['gpg_key']
                    info.gpg_key = gpg_key
                    success_msg = 'GPG Key stored.'

    if info.gpg_key != '':
        gpg_data = dict({'action':'update_gpg', 'gpg_key':info.gpg_key})
        form_gpg = GPGForm( gpg_data )
    else:
        form_gpg = GPGForm()

    keys =  request.user.sshkey_set.all()
    if keys is not None:
        ssh_keys = dict()
        for key in keys:
            ssh_keys[key.pk] =  ssh_key_fingerprint( key.ssh_key )


    context = { 'form_gpg' : form_gpg,
                'form_ssh' : form_ssh,
                'ssh_keys' : ssh_keys,
                'error_msg' : error_msg,
                'success_msg' : success_msg,
                }
    context.update(extra_context)
    return render_to_response('my/ssh_gpg.html',
                              context,
                              context_instance=RequestContext(request))

@login_required()
@render_to('svmain/generic_confirm.html', mimetype=None)
def sv_ssh_delete(request):
    if request.method == 'POST':
        try:
            ssh_key = request.user.sshkey_set.get(pk=request.POST.get('key_pk', 0))
            ssh_key.delete()
        except SshKey.DoesNotExist:
            messages.error(request, u"Cannot remove the selected key")
        return HttpResponseRedirect("../")
    else:
        return {}


class MailForm( forms.Form ):
    email = forms.EmailField(required=True)
    action = forms.CharField( widget=forms.HiddenInput, required=True, initial='update_mail' )

class IdentityForm( forms.Form ):
    name = forms.CharField( required = True )
    last_name = forms.CharField( required = False )
    action = forms.CharField( widget=forms.HiddenInput, required=True, initial='update_identity' )

class GPGForm( forms.Form ):
    gpg_key = forms.CharField( widget=forms.Textarea( attrs={'cols':'70','rows':'15'} ), required=False )
    action = forms.CharField( widget=forms.HiddenInput, required=True, initial='update_gpg' )

class SSHForm( forms.Form ):
    key_file = forms.FileField(required=False, help_text="Be sure to upload the file ending with .pub")
    key = forms.CharField(widget=forms.TextInput(attrs={'size':'60'}), required=False)

    action = forms.CharField(widget=forms.HiddenInput, required=True, initial='add_ssh')

    def clean_key( self ):
        ssh_key = self.cleaned_data['key']

        try:
            ssh_key_fingerprint(ssh_key)
        except:
            raise forms.ValidationError("The uploaded string is not a public key file")

        return ssh_key

    def clean_key_file( self ):
        ssh_key_file = self.cleaned_data['key_file']

        if ssh_key_file is None:
            return ssh_key_file

        ssh_key = str()
        for chunk in ssh_key_file.chunks():
            ssh_key = ssh_key + chunk

        try:
            ssh_key_fingerprint(ssh_key)
        except:
            raise forms.ValidationError("The uploaded file is not a public key file")

        return ssh_key_file

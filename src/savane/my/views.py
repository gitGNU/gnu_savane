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
from savane.svmain.models import ExtendedUser, SshKey

import random
import time
import os
import re
from subprocess import Popen, PIPE

@login_required()
def sv_conf( request ):

    error_msg = ''
    success_msg = ''

    form_pass = PasswordForm ()
    form_mail = MailForm ()
    form_identity = IdentityForm ()
    form = None

    if request.method == 'POST':
        action = request.POST['action']
        if action == 'update_password':
            form_pass = PasswordForm( request.POST )
            form = form_pass
        elif action == 'update_mail':
            form_mail = MailForm( request.POST )
            form = form_mail
        elif action == 'update_identity':
            form_identity = IdentityForm( request.POST )
            form = form_identity

        if form is not None and form.is_valid():
            if action == 'update_password':
                if request.user.check_password( request.POST['old_password'] ):
                    request.user.set_password( request.POST['new_password'] );
                    request.user.save()
                    success_msg = "Password was successfully changed."
                    form_pass = PasswordForm()
                else:
                    error_msg = "Old password didn't match."
            elif action == 'update_mail':
                new_email = request.POST['email']
                request.user.email = new_email
                request.user.save()
                form_mail = MailForm()
                success_msg = 'The E-Mail address was succesfully updated. New E-Mail address is <'+new_email+'>'
            elif action == 'update_identity':
                request.user.first_name = request.POST['name']
                request.user.last_name = request.POST['last_name']
                request.user.save()
                success_msg = 'Personal information changed.'
                form_identity = IdentityForm()

    return render_to_response('my/conf.html',
                              { 'form_pass' : form_pass,
                                'form_mail' : form_mail,
                                'form_identity' : form_identity,
                                'error_msg' : error_msg,
                                'success_msg' : success_msg,
                                },
                              context_instance=RequestContext(request))

@login_required()
def sv_resume_skill( request ):
    return render_to_response('my/resume_skill.html',
                               context_instance=RequestContext(request))
@login_required()
def sv_ssh_gpg( request ):
    eu = get_object_or_404(ExtendedUser, pk=request.user.pk)

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
                ssh_key = eu.sshkey_set.get(pk=key_pk)
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
                        eu.sshkey_set.add(ssh_key)
                        success_msg = 'Authorized keys stored.'

                if 'key_file' in request.FILES:
                    ssh_key_file = request.FILES['key_file']
                    if ssh_key_file is not None:
                        key = ''
                        for chunk in ssh_key_file.chunks():
                            key = key + chunk

                            if len(key) > 0:
                                ssh_key = SshKey(ssh_key=key)
                                eu.sshkey_set.add(ssh_key)
                                success_msg = 'Authorized keys stored.'

                form_ssh = SSHForm()

                if len( success_msg ) == 0:
                    error_msg = 'Cannot added the public key'

            elif action == 'update_gpg':
                pass
    else:
       if eu.gpg_key != '':
           gpg_data = dict({'action':'update_gpg', 'gpg_key':eu.gpg_key})
           form_gpg = GPGForm( gpg_data )
       else:
           form_gpg = GPGForm()

    keys =  eu.sshkey_set.all()
    if keys is not None:
        ssh_keys = dict()
        for key in keys:
            key_len = len(key.ssh_key)
            head_key = key.ssh_key[0:20]
            tail_key = key.ssh_key[key_len-20:key_len]
            ssh_keys[key.pk] = head_key+'[...stripped..]'+tail_key



    return render_to_response('my/ssh_gpg.html',
                              { 'form_gpg' : form_gpg,
                                'form_ssh' : form_ssh,
                                'ssh_keys' : ssh_keys,
                                'error_msg' : error_msg,
                                'success_msg' : success_msg,
                                },
                              context_instance=RequestContext(request))

class MailForm( forms.Form ):
    email = forms.EmailField(required=True)
    action = forms.CharField( widget=forms.HiddenInput, required=True, initial='update_mail' )

class PasswordForm( forms.Form ):
    old_password = forms.CharField(widget=forms.PasswordInput,required=True)
    new_password = forms.CharField(widget=forms.PasswordInput,required=True)
    repated_password = forms.CharField(widget=forms.PasswordInput,required=True)
    action = forms.CharField( widget=forms.HiddenInput, required=True, initial='update_password' )

    def clean( self ):
        cleaned_data = self.cleaned_data
        new_password = cleaned_data.get('new_password')
        old_password = cleaned_data.get('old_password')

class IdentityForm( forms.Form ):
    name = forms.CharField( required = True )
    last_name = forms.CharField( required = False )
    action = forms.CharField( widget=forms.HiddenInput, required=True, initial='update_identity' )

class GPGForm( forms.Form ):
    gpg_key = forms.CharField( widget=forms.Textarea( attrs={'cols':'70','rows':'15'} ), required=False )
    action = forms.CharField( widget=forms.HiddenInput, required=True, initial='update_gpg' )

class SSHForm( forms.Form ):
    key_file = forms.FileField( required=False )
    key = forms.CharField( widget=forms.TextInput( attrs={'size':'60'} ), required=False )

    action = forms.CharField( widget=forms.HiddenInput, required=True, initial='add_ssh' )

    def clean_key( self ):
        ssh_key = self.cleaned_data['key']

        if ssh_key is None or len(ssh_key) == 0:
            return ssh_key

        file_name = '/tmp/%d' % random.randint(0, int(time.time()))

        tmp_file = open( file_name, 'wb+' )
        tmp_file.write( ssh_key )
        tmp_file.close()

        cmd = 'ssh-keygen -l -f %s' % file_name
        pipe = Popen( cmd, shell=True, stdout=PIPE).stdout
        res = re.search("not a public key file", pipe.readline())
        if res is not None:
            raise forms.ValidationError( "The uploaded string is not a public key file" )

        return ssh_key

    def clean_key_file( self ):
        ssh_key_file = self.cleaned_data['key_file']

        if ssh_key_file is None:
            return ssh_key_file

        file_name = '/tmp/%d' % random.randint(0, int(time.time()))

        tmp_file = open( file_name, 'wb+' )
        for chunk in ssh_key_file.chunks():
            tmp_file.write(chunk)
        tmp_file.close()

        cmd = 'ssh-keygen -l -f %s' % file_name
        pipe = Popen( cmd, shell=True, stdout=PIPE).stdout
        res = re.search("not a public key file", pipe.readline())

        if res is not None:
            raise forms.ValidationError( "The uploaded file is not a public key file" )

        return ssh_key_file

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
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django import forms
from models import ExtendedUser

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
                    success_msg = "Password was successfully changed."
                    form_pass = PasswordForm()
                else:
                    error_msg = "Old password didn't match."
            elif action == 'update_mail':
                new_email = request.POST['email']
                request.user.email = new_email
                request.user.save()
                form_mail = MilForm()
                success_msg = 'The E-Mail address was succesfully updated. New E-Mail address is <'+new_email+'>'
            elif action == 'update_identity':
                request.user.first_name = request.POST['name']
                request.user.last_name = request.POST['last_name']
                request.user.save()
                success_msg = 'Personal information changed.'
                form_identity = IdentityForm()

    return render_to_response('savane/my/conf.html',
                              { 'form_pass' : form_pass,
                                'form_mail' : form_mail,
                                'form_identity' : form_identity,
                                'error_msg' : error_msg,
                                'success_msg' : success_msg,
                                },
                              context_instance=RequestContext(request))

@login_required()
def sv_resume_skill( request ):
    return render_to_response('savane/my/resume_skill.html',
                               context_instance=RequestContext(request))
@login_required()
def sv_ssh_gpg( request ):
    eu = ExtendedUser.objects.get(pk=request.user.pk)

    error_msg = None
    success_msg = None

    form_ssh = SSHForm()
    form_gpg = GPGForm()

    if request.method == 'POST':
        form = None
        action = request.POST['action']
        if action == 'update_ssh':
            form_ssh = SSHForm( request.POST )
            form = form_ssh
        elif action == 'update_gpg':
            form_gpg = GPGForm( request.POST )

        if form is not None and form.is_valid():
            if action == 'update_ssh':
                keys = list()
                for i in range( 1, 6 ):
                    key_str = 'key_'+str(i)
                    key = request.POST[ key_str ]
                    if key != '':
                        keys.append( key )
                keys_str = str('###').join( keys )

                eu.authorized_keys = keys_str
                eu.save()
                success_msg = 'Authorized keys stored.'
            elif action == 'update_gpg':
                pass
    else:
        if eu.authorized_keys != '':
            keys_data = dict({'action':'update_ssh'})
            keys = (eu.authorized_keys or '').split('###')
            i = 1
            for key in keys:
                key_str = 'key_'+str(i)
                keys_data[ key_str ] = key
                i += 1
                form_ssh = SSHForm( keys_data )
        else:
            form_ssh = SSHForm()

        if eu.gpg_key != '':
            gpg_data = dict({'action':'update_gpg', 'gpg_key':eu.gpg_key})
            form_gpg = GPGForm( gpg_data )
        else:
            form_gpg = GPGForm()


    return render_to_response('savane/my/ssh_gpg.html',
                              { 'form_gpg' : form_gpg,
                                'form_ssh' : form_ssh,
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
    widget = forms.TextInput( attrs={'size':'60'} )
    key_1 = forms.CharField( widget=widget, required=False )
    key_2 = forms.CharField( widget=widget, required=False )
    key_3 = forms.CharField( widget=widget, required=False )
    key_4 = forms.CharField( widget=widget, required=False )
    key_5 = forms.CharField( widget=widget, required=False )
    action = forms.CharField( widget=forms.HiddenInput, required=True, initial='update_ssh' )

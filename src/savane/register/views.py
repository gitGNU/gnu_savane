# Copyright (C) 2009 Jonathan Gonzalez V.
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
from django import forms

from savane.svmain.models import ExtendedUser, SshKey


def register( request ):
    error_msg = ''
    success_msg = ''

    form = RegisterForm()

    return render_to_response('register/register.html',
                              { 'error_msg' : error_msg,
                                'form' : form,
                                'success_msg' : success_msg,
                                },
                              context_instance=RequestContext(request))



class RegisterForm( forms.Form ):
    username = forms.CharField( required=True )
    password = forms.CharField( widget=forms.PasswordInput,required=True )
    repeat_password = forms.CharField( widget=forms.PasswordInput,required=True )
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField( required=True )

    action = forms.CharField( widget=forms.HiddenInput, required=True, initial='register' )

    def clean_login( self ):
        username = lsef.cleaned_data['username']

        try:
            user = ExtendedUser.objects.get( username=username)
        except:
            return username

        raise forms.ValidationError( 'The username already exists.' )

    def clean( self ):
        password = self.cleaned_data.get( 'password' )
        repeat_password = self.cleaned_data.get( 'repeat_password' )

        if password != repeat_password:
            raise forms.ValidationError( 'Password do not match.' )

        return self.cleaned_data

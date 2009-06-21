from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django import forms

def index( request ):
    return render_to_response( 'savane_user/index.html',
                               RequestContext( request,
                                               ) )
def sv_login( request ):
    username = request.POST['username']
    password = request.POST['password']

    user = authenticate( username=username, password=password )

    if user is not None:
        login( request, user )
    else:
        login_error = u"User or password didn't match"
        return render_to_response( 'error.html',
                                   {'error' : login_error
                                    } )

    return HttpResponseRedirect ( '/' )

def sv_logout( request ):
    logout( request )

    return HttpResponseRedirect( '/' )


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
                else:
                    error_msg = "Old password didn't match."
            elif action == 'update_mail':
                new_email = request.POST['email']
                request.user.email = new_email
                request.user.save()
                success_msg = 'The E-Mail address was succesfully updated. New E-Mail address is <'+new_email+'>'
            elif action == 'update_identity':
                request.user.first_name = request.POST['name']
                request.user.last_name = request.POST['last_name']
                request.user.save()
                success_msg = 'Personal information changed.'

    return render_to_response( 'savane_user/conf.html',
                               RequestContext( request,
                                               { 'form_pass' : form_pass,
                                                 'form_mail' : form_mail,
                                                 'form_identity' : form_identity,
                                                 'error_msg' : error_msg,
                                                 'success_msg' : success_msg,
                                                 }
                                               ) )

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

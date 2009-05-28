from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django import forms

def index( request ):
    return render_to_response( 'savane_user/index.djhtml',
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
        return render_to_response( 'error.djhtml',
                                   {'error' : login_error
                                    } )

    return HttpResponseRedirect ( '/' )

def sv_logout( request ):
    logout( request )

    return HttpResponseRedirect( '/' )


def sv_conf( request ):
    return render_to_response( 'savane_user/conf.djhtml',
                               RequestContext( request,
                                               ) )
def sv_identity( request ):

    if 'action' in request.POST and request.user.is_authenticated():
        request.user.first_name = request.POST['new_name']
        request.user.last_name = request.POST['new_last_name']
        request.user.save()

    return render_to_response( 'savane_user/identity.djhtml',
                               RequestContext( request,
                                               ) )
def sv_authentication( request ):
    if request.user.is_authenticated() is False:
        return HttpResponseRedirect( '/' )
    error = ''
    if request.method == 'POST':
        form = PasswordForm( request.POST )

        if form.is_valid():
            success = u"Valid Form"
            form = PasswordForm( )
            return render_to_response( 'savane_user/authentication.djhtml',
                                       RequestContext( request,
                                                       { 'form' : form,
                                                         'success_message' : success,}
                                                       ) )
        else:
            error = u"Isn't valid"
    else:
        form = PasswordForm()

    return render_to_response( 'savane_user/authentication.djhtml',
                               RequestContext( request,
                                               {'form' : form,
                                                'error_message' : error,}
                                               ) )

class PasswordForm( forms.Form ):
    old_password = forms.CharField(widget=forms.PasswordInput,required=True)
    new_password = forms.CharField(widget=forms.PasswordInput,required=True)
    repated_password = forms.CharField(widget=forms.PasswordInput,required=True)
    accion = forms.CharField( widget=forms.HiddenInput, required=True, initial='update' )

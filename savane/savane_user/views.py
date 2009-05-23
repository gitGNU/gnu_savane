from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout

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
    return render_to_response( 'savane_user/identity.djhtml',
                               RequestContext( request,
                                               ) )

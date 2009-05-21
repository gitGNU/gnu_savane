from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse

def index(request):
    authenticated = request.user.is_authenticated()

    return render_to_response( 'index.djhtml', RequestContext( request, {'authenticated': authenticated},
                                                               ) )

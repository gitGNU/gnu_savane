from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse

def index(request):
    return render_to_response( 'index.html',
                               RequestContext( request, {'has_left_menu': False},
                                               ) )

def contact( request ):
    return render_to_response( 'contact.html',
                               RequestContext( request,
                                               ))

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse

from django.contrib.auth.models import check_password

def index(request):
    return render_to_response( 'savane_user/index.djhtml',
                               RequestContext(request,
                                              ) )

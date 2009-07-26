from django.conf.urls.defaults import *
from main import views


urlpatterns = patterns ('',
                        url('^$',
                            views.index,
                            ),
                        url('^contact$',
                            views.contact,
                            ),
                        )

from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
                       (r'^$', "main.views.index"),
                       (r'^css/(?P<path>.*)$', 'django.views.static.serve',
                        {'document_root' : settings.SAVANE_ROOT + 'media/css/'}),
                       (r'^images/(?P<path>.*)$', 'django.views.static.serve',
                        {'document_root' : settings.SAVANE_ROOT + 'media/images/'}),

                       (r'^user/', include('savane_user.urls')),

                       # Uncomment the next line to enable the admin:
                       # (r'^admin/(.*)', admin.site.root),
                       )

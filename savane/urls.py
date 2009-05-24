from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
                       (r'^$', "main.views.index"),

                       (r'^user/', include('savane_user.urls')),

                       # Uncomment the next line to enable the admin:
                       # (r'^admin/(.*)', admin.site.root),
                       )

# Static content
if settings.DEBUG:
    urlpatterns += patterns('django.views.static',
        (r'^css/(?P<path>.*)$', 'serve',
         {'document_root' : settings.STATIC_ROOT + 'css/', 'show_indexes' : True}),
        (r'^images/(?P<path>.*)$', 'serve',
         {'document_root' : settings.STATIC_ROOT + 'images/', 'show_indexes' : True}),
    )

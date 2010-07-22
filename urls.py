# URL dispatching
# Copyright (C) 2009  Sylvain Beucler
# Copyright (C) 2009  Jonathan Gonzalez V.
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

from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',)

# Home/presentation pages
urlpatterns += patterns('',
  (r'', include('savane.svmain.urls')),
)

# User account
urlpatterns += patterns('',
  (r'^my/', include('savane.my.urls')),
  # Generic login/logout/change_pass/etc.
  (r'^accounts/logout/$', 'django.contrib.auth.views.logout',
    {'next_page' : '/'}),  # redirect to '/' instead of login page
  # django-registration
  (r'^accounts/', include('registration.backends.default.urls')),
  (r'^accounts/', include('django.contrib.auth.urls')),
)

# Enable the auto-admin:
from django.contrib import admin
import django
admin.autodiscover()

urlpatterns += patterns('',
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)


# Static content
if settings.DEBUG:
    urlpatterns += patterns('django.views.static',
        (r'^' + settings.STATIC_MEDIA_URL[1:] + '(?P<path>.*)$', 'serve',
         {'document_root' : settings.STATIC_MEDIA_ROOT, 'show_indexes' : True}),
    )

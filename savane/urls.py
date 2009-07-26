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

# Home/presentation pages
urlpatterns = patterns('',
  (r'', include('main.urls')),
)

# User account
urlpatterns += patterns('',
  (r'^my/', include('my.urls')),
  # Generic login/logout/change_pass/etc.
  (r'^accounts/logout/$', 'django.contrib.auth.views.logout',
    {'next_page' : '/'}),  # redirect to '/' instead of login page
  (r'^accounts/', include('django.contrib.auth.urls')),
)

# Static content
if settings.DEBUG:
    urlpatterns += patterns('django.views.static',
        (r'^css/(?P<path>.*)$', 'serve',
         {'document_root' : settings.STATIC_ROOT + 'css/', 'show_indexes' : True}),
        (r'^images/(?P<path>.*)$', 'serve',
         {'document_root' : settings.STATIC_ROOT + 'images/', 'show_indexes' : True}),
    )

# Uncomment the next lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()
# urlpatterns += patterns(
#   (r'^admin/(.*)', admin.site.root),
# )

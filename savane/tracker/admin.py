# Trackers admin interface
# Copyright (C) 2010  Sylvain Beucler
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

from django.contrib import admin
from django.utils.translation import ugettext, ugettext_lazy as _
from models import *

# It's not sensible to edit this, it's only a PK
#class TrackerAdmin(admin.ModelAdmin):
#    list_display  = ('name',)

class FieldAdmin(admin.ModelAdmin):
    search_fields = ('name', 'label', 'description', )
    ordering = ('tracker', 'name', )
    list_display  = ('id', 'tracker', 'scope', 'name', 'label', 'display_type', 'display_size',
                     'required', 'empty_ok', 'keep_history', 'special', 'custom', )
    list_display_links = ('id', 'name', 'label')
    list_filter = ('tracker', 'display_type', 'scope',
                   'required', 'empty_ok', 'keep_history', 'special', 'custom', )
    #inlines = ( FieldUsage??, )

admin.site.register(Field, FieldAdmin)

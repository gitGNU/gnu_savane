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

class FieldUsageInline(admin.TabularInline):
    model = FieldUsage
    raw_id_fields = ('group',)
class FieldAdmin(admin.ModelAdmin):
    search_fields = ('name', 'label', 'description', )
    ordering = ('tracker', 'name', )
    list_display  = ('id', 'tracker', 'scope', 'name', 'label', 'display_type', 'display_size',
                     'required', 'empty_ok', 'keep_history', 'special', 'custom', )
    list_display_links = ('id', 'name', 'label')
    list_filter = ('tracker', 'display_type', 'scope',
                   'required', 'empty_ok', 'keep_history', 'special', 'custom', )
    inlines = ( FieldUsageInline, )

class FieldUsageAdmin(admin.ModelAdmin):
    search_fields = ('group', 'custom_label', 'custom_description', )
    ordering = ('group', 'field',)
    list_display  = ('id', 'group', 'field', 'use_it', 'place', )
    list_display_links = ('id',)
    list_filter = ('use_it', 'show_on_add', 'show_on_add_members', 'custom_empty_ok', 'custom_keep_history',)
    raw_id_fields = ('group',)

admin.site.register(Field, FieldAdmin)
admin.site.register(FieldUsage, FieldUsageAdmin)

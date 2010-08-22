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

class TrackerAdmin(admin.ModelAdmin):
    list_display  = ('name',)

# class FieldOverlayInline(admin.TabularInline):
#     model = FieldOverlay
#     raw_id_fields = ('group',)
# class FieldAdmin(admin.ModelAdmin):
#     search_fields = ('name', 'label', 'description', )
#     ordering = ('name', )
#     list_display  = ('name', 'scope', 'required', 'special', 'custom', )
#     list_display_links = ('name', )
#     list_filter = ('display_type', 'scope', 'required', 'special', 'custom', )
#     inlines = ( FieldOverlayInline, )
#admin.site.register(Field, FieldAdmin)

class FieldOverlayAdmin(admin.ModelAdmin):
    search_fields = ('group', 'label', 'description', )
    ordering = ('group', 'field',)
    list_display  = ('id', 'tracker', 'group', 'field', 'use_it', 'rank', )
    list_display_links = ('id',)
    list_filter = ('use_it', 'show_on_add_anonymous', 'show_on_add_connected', 'show_on_add_members',
                   'empty_ok', 'keep_history',)
    raw_id_fields = ('group',)

class FieldChoiceAdmin(admin.ModelAdmin):
    search_fields = ('group', 'value_id', 'value', 'description', )
    ordering = ('group', 'field', 'tracker', 'rank')
    list_display  = ('id', 'tracker', 'group', 'field', 'value_id', 'value', 'status', 'rank')
    list_display_links = ('id',)
    list_filter = ('status',)
    raw_id_fields = ('group',)

 
admin.site.register(FieldOverlay, FieldOverlayAdmin)
admin.site.register(FieldChoice, FieldChoiceAdmin)

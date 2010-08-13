# User/group admin interface
# Copyright (C) 2009, 2010  Sylvain Beucler
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

class JobInventoryInline(admin.TabularInline):
    model = JobInventory
class JobAdmin(admin.ModelAdmin):
    search_fields = ('title',)
    ordering = ('date',)
    list_display  = ('id', 'title', 'category', 'status', 'group', 'created_by',)
    list_display_links = ('id', 'title',)
    list_filter = ('status', 'category',)
    date_hierarchy = 'date'
    raw_id_fields = ('group', 'created_by', )
    inlines = ( JobInventoryInline, )

class LabelAdmin(admin.ModelAdmin):
    ordering = ('id'),
    list_display = ['id', 'label', 'active']
    list_display_links = ['id']
    list_editable = ['label', 'active']
    list_filter = ['active']
    search_fields = ['libelle']


admin.site.register(Job, JobAdmin)
admin.site.register(Skill, LabelAdmin)
admin.site.register(SkillYear, LabelAdmin)
admin.site.register(SkillLevel, LabelAdmin)
admin.site.register(Category, LabelAdmin)

# TODO: JobInventory and SkillInventory

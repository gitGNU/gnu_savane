# Trackers definition
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

"""
The Field definition cannot be changed, so it's been made static
instead of stored in the database.

Here's the previous model definition.  See also FieldOverlay, which is
still used for non-default (i.e. override) values.

class Field(models.Model):
    class Meta:
        verbose_name = _("field")
        verbose_name_plural = _("fields")

    DISPLAY_TYPE_CHOICES = (('DF', _('date field')),
                            ('SB', _('select box')),
                            ('TA', _('text area')),
                            ('TF', _('text field')),)
    SCOPE_CHOICES = (('S', _('system')), # user cannot modify related FieldChoice's (TF)
                     ('P', _('project')),)  # user can modify related FieldChoice's (TF)

    name = models.CharField(max_length=32, db_index=True, primary_key=True)

    # Data type
    display_type = models.CharField(max_length=255, choices=DISPLAY_TYPE_CHOICES)

    # Field values can be added (if SB)
    scope = models.CharField(max_length=1, choices=SCOPE_CHOICES)
    # Field cannot be hidden (but can be made optional) (except if special: might be hidden and managed by code)
    required = models.BooleanField(help_text=_("field cannot be disabled in group configuration"))

    # Field cannot be made optional (displayed unless 'bug_id' and 'group_id')
    # Also, field are not displayed (filled by the system) - except for 'summary', 'comment_type' and 'details'
    # (consequently, they cannot be customized in any way, except for 'summary' and 'details' where you can only customize the display size)
    special = models.BooleanField()
    # Field may change label and description
    custom = models.BooleanField(help_text=_("let the user change the label and description"))

    def __unicode__(self):
        "For admin interface"
        return self.name
"""

from django.utils.translation import ugettext, ugettext_lazy as _
from copy import deepcopy

field_defs = {
    'bug_id' : {
        'name': 'bug_id',
        'display_type': 'TF',
        'scope': 'S',
        'required': 1,
        'special': 1,
        'custom': 0,
    },
    'group_id' : {
        'name': 'group_id',
        'display_type': 'TF',
        'scope': 'S',
        'required': 1,
        'special': 1,
        'custom': 0,
    },
    'submitted_by' : {
        'name': 'submitted_by',
        'display_type': 'SB',
        'scope': 'S',
        'required': 1,
        'special': 1,
        'custom': 0,
    },
    'date' : {
        'name': 'date',
        'display_type': 'DF',
        'scope': 'S',
        'required': 1,
        'special': 1,
        'custom': 0,
    },
    'close_date' : {
        'name': 'close_date',
        'display_type': 'DF',
        'scope': 'S',
        'required': 1,
        'special': 1,
        'custom': 0,
    },
    'status_id' : {
        'name': 'status_id',
        'display_type': 'SB',
        'scope': 'S',
        'required': 1,
        'special': 0,
        'custom': 0,
    },
    'severity' : {
        'name': 'severity',
        'display_type': 'SB',
        'scope': 'S',
        'required': 0,
        'special': 0,
        'custom': 0,
    },
    'category_id' : {
        'name': 'category_id',
        'display_type': 'SB',
        'scope': 'P',
        'required': 0,
        'special': 0,
        'custom': 0,
    },
    'assigned_to' : {
        'name': 'assigned_to',
        'display_type': 'SB',
        'scope': 'S',
        'required': 1,
        'special': 0,
        'custom': 0,
    },
    'summary' : {
        'name': 'summary',
        'display_type': 'TF',
        'scope': 'S',
        'required': 1,
        'special': 1,
        'custom': 0,
    },
    'details' : {
        'name': 'details',
        'display_type': 'TA',
        'scope': 'S',
        'required': 1,
        'special': 1,
        'custom': 0,
    },
    'bug_group_id' : {
        'name': 'bug_group_id',
        'display_type': 'SB',
        'scope': 'P',
        'required': 0,
        'special': 0,
        'custom': 0,
    },
    'resolution_id' : {
        'name': 'resolution_id',
        'display_type': 'SB',
        'scope': 'P',
        'required': 0,
        'special': 0,
        'custom': 0,
    },
    'privacy' : {
        'name': 'privacy',
        'display_type': 'SB',
        'scope': 'S',
        'required': 0,
        'special': 0,
        'custom': 0,
    },
    'vote' : {
        'name': 'vote',
        'display_type': 'TF',
        'scope': 'S',
        'required': 0,
        'special': 1,
        'custom': 0,
    },
    'category_version_id' : {
        'name': 'category_version_id',
        'display_type': 'SB',
        'scope': 'P',
        'required': 0,
        'special': 0,
        'custom': 0,
    },
    'platform_version_id' : {
        'name': 'platform_version_id',
        'display_type': 'SB',
        'scope': 'P',
        'required': 0,
        'special': 0,
        'custom': 0,
    },
    'reproducibility_id' : {
        'name': 'reproducibility_id',
        'display_type': 'SB',
        'scope': 'S',
        'required': 0,
        'special': 0,
        'custom': 0,
    },
    'size_id' : {
        'name': 'size_id',
        'display_type': 'SB',
        'scope': 'S',
        'required': 0,
        'special': 0,
        'custom': 0,
    },
    'fix_release_id' : {
        'name': 'fix_release_id',
        'display_type': 'SB',
        'scope': 'P',
        'required': 0,
        'special': 0,
        'custom': 0,
    },
    'comment_type_id' : {
        'name': 'comment_type_id',
        'display_type': 'SB',
        'scope': 'P',
        'required': 1,
        'special': 1,
        'custom': 0,
    },
    'hours' : {
        'name': 'hours',
        'display_type': 'TF',
        'scope': 'S',
        'required': 0,
        'special': 0,
        'custom': 0,
    },
    'plan_release_id' : {
        'name': 'plan_release_id',
        'display_type': 'SB',
        'scope': 'P',
        'required': 0,
        'special': 0,
        'custom': 0,
    },
    'component_version' : {
        'name': 'component_version',
        'display_type': 'TF',
        'scope': 'S',
        'required': 0,
        'special': 0,
        'custom': 0,
    },
    'fix_release' : {
        'name': 'fix_release',
        'display_type': 'TF',
        'scope': 'S',
        'required': 0,
        'special': 0,
        'custom': 0,
    },
    'plan_release' : {
        'name': 'plan_release',
        'display_type': 'TF',
        'scope': 'S',
        'required': 0,
        'special': 0,
        'custom': 0,
    },
    'priority' : {
        'name': 'priority',
        'display_type': 'SB',
        'scope': 'S',
        'required': 0,
        'special': 0,
        'custom': 0,
    },
    'keywords' : {
        'name': 'keywords',
        'display_type': 'TF',
        'scope': 'S',
        'required': 0,
        'special': 0,
        'custom': 0,
    },
    'release_id' : {
        'name': 'release_id',
        'display_type': 'SB',
        'scope': 'P',
        'required': 0,
        'special': 0,
        'custom': 0,
    },
    'release' : {
        'name': 'release',
        'display_type': 'TF',
        'scope': 'S',
        'required': 0,
        'special': 0,
        'custom': 0,
    },
    'originator_name' : {
        'name': 'originator_name',
        'display_type': 'TF',
        'scope': 'S',
        'required': 0,
        'special': 0,
        'custom': 0,
    },
    'originator_email' : {
        'name': 'originator_email',
        'display_type': 'TF',
        'scope': 'S',
        'required': 0,
        'special': 0,
        'custom': 0,
    },
    'originator_phone' : {
        'name': 'originator_phone',
        'display_type': 'TF',
        'scope': 'S',
        'required': 0,
        'special': 0,
        'custom': 0,
    },
    'percent_complete' : {
        'name': 'percent_complete',
        'display_type': 'SB',
        'scope': 'S',
        'required': 0,
        'special': 0,
        'custom': 0,
    },
    'custom_tf1' : {
        'name': 'custom_tf1',
        'display_type': 'TF',
        'scope': 'P',
        'required': 0,
        'special': 0,
        'custom': 1,
    },
    'custom_tf2' : {
        'name': 'custom_tf2',
        'display_type': 'TF',
        'scope': 'P',
        'required': 0,
        'special': 0,
        'custom': 1,
    },
    'custom_tf3' : {
        'name': 'custom_tf3',
        'display_type': 'TF',
        'scope': 'P',
        'required': 0,
        'special': 0,
        'custom': 1,
    },
    'custom_tf4' : {
        'name': 'custom_tf4',
        'display_type': 'TF',
        'scope': 'P',
        'required': 0,
        'special': 0,
        'custom': 1,
    },
    'custom_tf5' : {
        'name': 'custom_tf5',
        'display_type': 'TF',
        'scope': 'P',
        'required': 0,
        'special': 0,
        'custom': 1,
    },
    'custom_tf6' : {
        'name': 'custom_tf6',
        'display_type': 'TF',
        'scope': 'P',
        'required': 0,
        'special': 0,
        'custom': 1,
    },
    'custom_tf7' : {
        'name': 'custom_tf7',
        'display_type': 'TF',
        'scope': 'P',
        'required': 0,
        'special': 0,
        'custom': 1,
    },
    'custom_tf8' : {
        'name': 'custom_tf8',
        'display_type': 'TF',
        'scope': 'P',
        'required': 0,
        'special': 0,
        'custom': 1,
    },
    'custom_tf9' : {
        'name': 'custom_tf9',
        'display_type': 'TF',
        'scope': 'P',
        'required': 0,
        'special': 0,
        'custom': 1,
    },
    'custom_tf10' : {
        'name': 'custom_tf10',
        'display_type': 'TF',
        'scope': 'P',
        'required': 0,
        'special': 0,
        'custom': 1,
    },
    'custom_ta1' : {
        'name': 'custom_ta1',
        'display_type': 'TA',
        'scope': 'P',
        'required': 0,
        'special': 0,
        'custom': 1,
    },
    'custom_ta2' : {
        'name': 'custom_ta2',
        'display_type': 'TA',
        'scope': 'P',
        'required': 0,
        'special': 0,
        'custom': 1,
    },
    'custom_ta3' : {
        'name': 'custom_ta3',
        'display_type': 'TA',
        'scope': 'P',
        'required': 0,
        'special': 0,
        'custom': 1,
    },
    'custom_ta4' : {
        'name': 'custom_ta4',
        'display_type': 'TA',
        'scope': 'P',
        'required': 0,
        'special': 0,
        'custom': 1,
    },
    'custom_ta5' : {
        'name': 'custom_ta5',
        'display_type': 'TA',
        'scope': 'P',
        'required': 0,
        'special': 0,
        'custom': 1,
    },
    'custom_ta6' : {
        'name': 'custom_ta6',
        'display_type': 'TA',
        'scope': 'P',
        'required': 0,
        'special': 0,
        'custom': 1,
    },
    'custom_ta7' : {
        'name': 'custom_ta7',
        'display_type': 'TA',
        'scope': 'P',
        'required': 0,
        'special': 0,
        'custom': 1,
    },
    'custom_ta8' : {
        'name': 'custom_ta8',
        'display_type': 'TA',
        'scope': 'P',
        'required': 0,
        'special': 0,
        'custom': 1,
    },
    'custom_ta9' : {
        'name': 'custom_ta9',
        'display_type': 'TA',
        'scope': 'P',
        'required': 0,
        'special': 0,
        'custom': 1,
    },
    'custom_ta10' : {
        'name': 'custom_ta10',
        'display_type': 'TA',
        'scope': 'P',
        'required': 0,
        'special': 0,
        'custom': 1,
    },
    'custom_sb1' : {
        'name': 'custom_sb1',
        'display_type': 'SB',
        'scope': 'P',
        'required': 0,
        'special': 0,
        'custom': 1,
    },
    'custom_sb2' : {
        'name': 'custom_sb2',
        'display_type': 'SB',
        'scope': 'P',
        'required': 0,
        'special': 0,
        'custom': 1,
    },
    'custom_sb3' : {
        'name': 'custom_sb3',
        'display_type': 'SB',
        'scope': 'P',
        'required': 0,
        'special': 0,
        'custom': 1,
    },
    'custom_sb4' : {
        'name': 'custom_sb4',
        'display_type': 'SB',
        'scope': 'P',
        'required': 0,
        'special': 0,
        'custom': 1,
    },
    'custom_sb5' : {
        'name': 'custom_sb5',
        'display_type': 'SB',
        'scope': 'P',
        'required': 0,
        'special': 0,
        'custom': 1,
    },
    'custom_sb6' : {
        'name': 'custom_sb6',
        'display_type': 'SB',
        'scope': 'P',
        'required': 0,
        'special': 0,
        'custom': 1,
    },
    'custom_sb7' : {
        'name': 'custom_sb7',
        'display_type': 'SB',
        'scope': 'P',
        'required': 0,
        'special': 0,
        'custom': 1,
    },
    'custom_sb8' : {
        'name': 'custom_sb8',
        'display_type': 'SB',
        'scope': 'P',
        'required': 0,
        'special': 0,
        'custom': 1,
    },
    'custom_sb9' : {
        'name': 'custom_sb9',
        'display_type': 'SB',
        'scope': 'P',
        'required': 0,
        'special': 0,
        'custom': 1,
    },
    'custom_sb10' : {
        'name': 'custom_sb10',
        'display_type': 'SB',
        'scope': 'P',
        'required': 0,
        'special': 0,
        'custom': 1,
    },
    'custom_df1' : {
        'name': 'custom_df1',
        'display_type': 'DF',
        'scope': 'P',
        'required': 0,
        'special': 0,
        'custom': 1,
    },
    'custom_df2' : {
        'name': 'custom_df2',
        'display_type': 'DF',
        'scope': 'P',
        'required': 0,
        'special': 0,
        'custom': 1,
    },
    'custom_df3' : {
        'name': 'custom_df3',
        'display_type': 'DF',
        'scope': 'P',
        'required': 0,
        'special': 0,
        'custom': 1,
    },
    'custom_df4' : {
        'name': 'custom_df4',
        'display_type': 'DF',
        'scope': 'P',
        'required': 0,
        'special': 0,
        'custom': 1,
    },
    'custom_df5' : {
        'name': 'custom_df5',
        'display_type': 'DF',
        'scope': 'P',
        'required': 0,
        'special': 0,
        'custom': 1,
    },
    'discussion_lock' : {
        'name': 'discussion_lock',
        'display_type': 'SB',
        'scope': 'S',
        'required': 1,
        'special': 0,
        'custom': 0,
    },
    'planned_close_date' : {
        'name': 'planned_close_date',
        'display_type': 'DF',
        'scope': 'S',
        'required': 0,
        'special': 0,
        'custom': 0,
    },
    'planned_starting_date' : {
        'name': 'planned_starting_date',
        'display_type': 'DF',
        'scope': 'S',
        'required': 0,
        'special': 0,
        'custom': 0,
    },
}


# The following is now stored in the DB
## A couple changes per-tracker in the default configuration
##submitted_by     92 -> (use_it=0)(patch,support) | (use_it=1)(bugs,task)
#default_fields['patch']['submitted_by']['use_it'] = default_fields['support']['submitted_by']['use_it'] = 0
##severity    102 -> (use_it,show_on_add,show_on_add_members=0)(patch,task) | (use_it,show_on_add,show_on_add_members=1)(bugs,support)
#default_fields['patch']['severity']['use_it'] = default_fields['task']['severity']['use_it'] = 0
#default_fields['patch']['severity']['show_on_add'] = default_fields['task']['severity']['show_on_add'] = 0
#default_fields['patch']['severity']['show_on_add_members'] = default_fields['task']['severity']['show_on_add_members'] = 0
##bug_group_id    107 -> (show_on_add,show_on_add_members=0)(patch,support) | (show_on_add,show_on_add_members=1)(bugs,task) [but use_it=0]
##default_fields['patch']['bug_group_id']['show_on_add'] = default_fields['support']['bug_group_id']['show_on_add'] = 0
##default_fields['patch']['bug_group_id']['show_on_add_members'] = default_fields['support']['bug_group_id']['show_on_add_members'] = 0
##platform_version_id    201 -> (use_it,show_on_add,show_on_add_members=0)(bugs,patch,task) | (use_it,show_on_add,show_on_add_members=1)(support)
#default_fields['support']['platform_version_id']['use_it'] = 1
#default_fields['support']['platform_version_id']['show_on_add'] = 1
#default_fields['support']['platform_version_id']['show_on_add_members'] = 1
##hours    201 -> (use_it,show_on_add,show_on_add_members=0)(bugs,patch,support) | (use_it,show_on_add,show_on_add_members=1)(task)
#default_fields['task']['hours']['use_it'] = 1
#default_fields['task']['hours']['show_on_add'] = 1
#default_fields['task']['hours']['show_on_add_members'] = 1
##priority    211 -> (show_on_add,show_on_add_members,place)
##           bugs: 0,1,200
##           patch: 1,1,150
#default_fields['patch']['priority']['show_on_add'] = 1
#default_fields['patch']['priority']['show_on_add_members'] = 1
#default_fields['patch']['priority']['place'] = 150
##           support: 0,0,150
#default_fields['support']['priority']['show_on_add'] = 0
#default_fields['support']['priority']['show_on_add_members'] = 0
#default_fields['support']['priority']['place'] = 150
##           task: 1,1,200
#default_fields['task']['priority']['show_on_add'] = 1
#default_fields['task']['priority']['show_on_add_members'] = 1
#default_fields['task']['priority']['place'] = 200
##originator_email    216 -> (use_it,show_on_add=0)(task) | (use_it=1,show_on_add=2)(bugs,patch,support)
#default_fields['task']['originator_email']['use_it'] = 0
#default_fields['task']['originator_email']['show_on_add'] = 0
##percent_complete    220 -> (use_it,show_on_add_members=0)(bugs,patch,support) | (use_it,show_on_add_members=1)(task)
#default_fields['task']['originator_email']['use_it'] = 1
#default_fields['task']['originator_email']['show_on_add_members'] = 1
#
## 'planned_starting_date' was initially specific to 'task'
#default_fields['bugs']   ['planned_starting_date']['use_it'] = 0
#default_fields['patch']  ['planned_starting_date']['use_it'] = 0
#default_fields['support']['planned_starting_date']['use_it'] = 0
## 'same for planned_close_date'
#default_fields['bugs']   ['planned_close_date']['use_it'] = 0
#default_fields['patch']  ['planned_close_date']['use_it'] = 0
#default_fields['support']['planned_close_date']['use_it'] = 0

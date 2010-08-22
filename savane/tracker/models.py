# Trackers data structure
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

from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext, ugettext_lazy as _
import django.contrib.auth.models as auth_models
from django.utils.safestring import mark_safe
import datetime
import locale
from copy import deepcopy
from savane.utils import htmlentitydecode, unescape
from defs import *

##
# Trackers definition
##



# TODO: default '100' (aka 'nobody' or 'None', depending on
# fields) -> change to NULL?

# Date fields: use default=... rather than auto_now_add=...; indeed,
# auto_now_add cannot be overriden, hence it would mess data imports.
# EDIT: actually I think only forms fields cannot be overriden, it
# still can be done programmatically

DISPLAY_TYPE_CHOICES = (('', _('not editable')),
                        ('DF', _('date field')),
                        ('SB', _('select box')),
                        ('TA', _('text area')),
                        ('TF', _('text field')),)
SCOPE_CHOICES = (('S', _('system')), # user cannot modify related FieldChoice's (TF)
                 ('P', _('project')),)  # user can modify related FieldChoice's (TF)

RESTRICTION_CHOICES = (('2', _('anonymous')),
                       ('3', _('logged-in user')),
                       ('5', _('project member')),)
PERMISSION_CHOICES = (('', _('group type default')),
                      ('9', _('none')),
                      ('1', _('technician')),
                      ('3', _('manager')),
                      ('2', _('technician & manager')),)
NEW_ITEM_POSTING_RESTRICTION_CHOICES = PERMISSION_CHOICES + (('', _('group type default')),)
COMMENT_POSTING_RESTRICTION_CHOICES = PERMISSION_CHOICES + (('', _('same as new item')),)


NOTIFICATION_ROLES = (
    {'id': 1, 'label': 'SUBMITTER', 'short': _('Submitter'), 'description': _('The person who submitted the item')},
    {'id': 2, 'label': 'ASSIGNEE',  'short': _('Assignee' ), 'description': _('The person to whom the item was assigned')},
    {'id': 3, 'label': 'CC',        'short': _('CC'       ), 'description': _('The person who is in the CC list')},
    {'id': 4, 'label': 'SUBMITTER', 'short': _('Submitter'), 'description': _('A person who once posted a follow-up comment')},
)

NOTIFICATION_EVENTS = (
    {'id': 1, 'label': 'ROLE_CHANGE'     , 'short': _('Role has changed'),
     'description': _("I'm added to or removed from this role")},
    {'id': 2, 'label': 'NEW_COMMENT'     , 'short': _('New comment'),
     'description': _('A new followup comment is added')},
    {'id': 3, 'label': 'NEW_FILE'        , 'short': _('New attachment'),
     'description': _('A new file attachment is added')},
    {'id': 4, 'label': 'CC_CHANGE'       , 'short': _('CC Change'),
     'description': _('A new CC address is added/removed')},
    {'id': 5, 'label': 'CLOSED'          , 'short': _('Item closed'),
     'description': _('The item is closed')},
    {'id': 6, 'label': 'PSS_CHANGE'      , 'short': _('PSS change'),
     'description': _('Priority,Status,Severity changes')},
    {'id': 7, 'label': 'ANY_OTHER_CHANGE', 'short': _('Any other change'),
     'description': _('Any change not mentioned above')},
    {'id': 8, 'label': 'I_MADE_IT'       , 'short': _('I did it'),
     'description': _('I am the author of the change')},
    {'id': 9, 'label': 'NEW_ITEM'        , 'short': _('New Item'),
     'description': _('A new item has been submitted')},
)


class Tracker(models.Model):
    """
    Historically 4 trackers are hard-coded.

    The current implementation reduces the duplication to the
    Item.bugs_id / Item.patch_id / Item.support_id / Item.task_id
    (previous PHP implementation duplicated all tables).
    """
    NAME_CHOICES = (('bugs', _('Bugs')),
                    ('patch', _('Patches')),
                    ('support', _('Support')),
                    ('task', _('Tasks')),
                    )
    name = models.CharField(max_length=7, choices=NAME_CHOICES, primary_key=True)

    def get_public_id_item_field(self):
        return 'public_' + str(self.name)  # don't transform to unicode

    def __unicode__(self):
        "Used in the admin interface fields list"
        return self.name

class GroupTypeConfiguration(models.Model):
    """
    Previously in table "groups_type"
    TODO: keep?
    """
    tracker = models.ForeignKey('Tracker')
    group_type = models.IntegerField()  # TODO: ForeignKey
    new_item_posting_restriction = models.CharField(max_length=1,
                                                    choices=NEW_ITEM_POSTING_RESTRICTION_CHOICES,
                                                    blank=True)
    comment_posting_restriction = models.CharField(max_length=1,
                                                   choices=COMMENT_POSTING_RESTRICTION_CHOICES,
                                                   blank=True)
    default_member_permission = models.CharField(max_length=1, choices=PERMISSION_CHOICES, blank=True)

class GroupConfiguration(models.Model):
    """
    Previously in table "groups_default_permissions"
    """
    tracker = models.ForeignKey('Tracker')
    group = models.ForeignKey(auth_models.Group)
    new_item_restriction = models.CharField(max_length=1,
                                            choices=NEW_ITEM_POSTING_RESTRICTION_CHOICES,
                                            blank=True)
    comment_restriction = models.CharField(max_length=1,
                                           choices=COMMENT_POSTING_RESTRICTION_CHOICES,
                                           blank=True)
    default_member_permission = models.CharField(max_length=1, choices=PERMISSION_CHOICES, blank=True)

class MemberPermission(models.Model):
    """
    Previously in table "user_group"
    """
    tracker = models.ForeignKey('Tracker')
    group = models.ForeignKey(auth_models.Group)
    user = models.ForeignKey(auth_models.User)
    permission = models.CharField(max_length=1, choices=PERMISSION_CHOICES, blank=True)

#class SquadPermission(models.Model): pass


class FieldOverlay(models.Model):
    """
    Per-group tracker field definition override
    (or site-wide field default if group==NULL)
    """
    class Meta:
        unique_together = (('tracker', 'group', 'field'),)
        verbose_name = _("field overlay")
        verbose_name_plural = _("field overlays")

    EMPTY_OK_CHOICES = (('0', _('mandatory only if it was presented to the original submitter')),
                        ('1', _('optional (empty values are accepted)')),
                        ('3', _('mandatory')),)
    TRANSITION_DEFAULT_AUTH_CHOICES = (('', _('undefined')),
                                       ('A', _('allowed')),
                                       ('F', _('forbidden')),)
    tracker = models.ForeignKey(Tracker)
    group = models.ForeignKey(auth_models.Group, blank=True, null=True,
                              help_text=_("NULL == default for all groups"))
    field = models.CharField(max_length=32)

    # If Field.custom
    label = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    # If not Field.required:
    use_it = models.BooleanField(_("used"))
    # When posting a new item:
    show_on_add_anonymous = models.NullBooleanField(_("show to anonymous users"), blank=True, null=True)
    show_on_add_connected = models.NullBooleanField(_("show to connected users"), blank=True, null=True)
    show_on_add_members   = models.NullBooleanField(_("show to project members"), blank=True, null=True)

    # Can always be changed (expect for special 'summary' and 'details')
    empty_ok = models.CharField(max_length=1, choices=EMPTY_OK_CHOICES,
                                default='0', blank=True, null=True)

    # Can always be changed
    rank = models.IntegerField(help_text=_("display rank"))

    # Specific to SB
    # Can always be changed
    transition_default_auth = models.CharField(max_length=1, choices=TRANSITION_DEFAULT_AUTH_CHOICES, default='A')

    # Specific to TA and TF
    # Works for both custom and non-custom fields
    display_size = models.CharField(max_length=255, blank=True, null=True)
      # The default value is in Field.display_size
      #   rather than FieldUsage(group_id=100).custom_display_size

    # If !Field.special
    keep_history = models.BooleanField(_("keep field value changes in history"))

    def apply_on(self, field_definition):
        """
        Modify a default field definition with FieldOverlay's override
        values.  Only apply sensible overlays.
        """
        if not field_definition['required']:
            field_definition['use_it'] = self.use_it
            field_definition['show_on_add_anonymous'] = self.show_on_add_anonymous
            field_definition['show_on_add_connected'] = self.show_on_add_connected
            field_definition['show_on_add_members'] = self.show_on_add_members
        field_definition['empty_ok'] = self.empty_ok
        field_definition['rank'] = self.rank
        if field_definition['display_type'] == 'SB':
            field_definition['transition_default_auth'] = self.transition_default_auth
        elif field_definition['display_type'] in ('TA', 'TF'):
            field_definition['display_size'] = self.display_size
            # Make it easier to access the field from templates:
            if field_definition['display_size'] is not None:  # some old data may have weird values
                if field_definition['display_type'] == 'TF':
                    field_definition['input_size'] = field_definition['display_size'].split("/")[0]
                    field_definition['input_maxlength'] = field_definition['display_size'].split("/")[1]
                else:
                    field_definition['textarea_cols'] = field_definition['display_size'].split("/")[0]
                    field_definition['textarea_rows'] = field_definition['display_size'].split("/")[1]
        if self.group_id is None or field_definition['special'] != 1:
            field_definition['keep_history'] = self.keep_history
        if self.group_id is None or field_definition['custom'] == 1:
            field_definition['label'] = self.label
            field_definition['description'] = self.description

class FieldChoice(models.Model):
    """
    Per-group tracker select box values override
    (or site-wide field default if group==NULL)
    """
    class Meta:
        unique_together = (('tracker', 'group', 'field', 'value_id'),)

    STATUS_CHOICES = (('A', _('active')),
                      ('H', _('hidden')), # mask previously-active or system fields
                      ('P', _('permanent')),) # status cannot be modified, always visible
    tracker = models.ForeignKey(Tracker, blank=True, null=True)
    group = models.ForeignKey(auth_models.Group, blank=True, null=True,
                              help_text=_("NULL == default for all groups"))
    field = models.CharField(max_length=32)
    value_id = models.IntegerField(db_index=True) # group_specific value identifier
      # It's not a duplicate of 'id', as it's the value referenced by
      # Item fields, and the configuration of that value can be
      # customized per-project.
    value = models.CharField(max_length=255) # label
    description = models.TextField()
    rank = models.IntegerField()
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A', db_index=True)

    # Field category: specific (bad!) field for e-mail notifications
    email_ad = models.TextField(blank=True, null=True,
                                help_text=_("comma-separated list of e-mail addresses to notify when an item is created or modified in this category"))
    send_all_flag = models.BooleanField(_("send on all updates"), default=True)

    def __unicode__(self):
        #return "%s.%s: %s (%d)" % (self.tracker_id, self.field, self.value, self.value_id)
        group_name = '<default>'
        if self.group_id is not None:
            group_name = self.group.name
        return "%s.%s: %s (%d)" % (group_name, self.field, self.value, self.value_id)

##
# Field
##

def field_get_values(tracker_id, group, field_def, cur_item_value_id=None):
    """
    Return all possible values for this select box field
    """
    name = field_def['name']
    if name == 'submitted_by':
        # Not editable
        return []
    if name == 'assigned_to':
        # Hard-coded processing: it's a list of project members
        values = [{'value_id' : -1, 'value' : _("None")}]
        pks = list(group.user_set.order_by('username').values_list('pk', flat=True))
        # Add the current value if the user was previously part of the
        # project and assigned this time
        if cur_item_value_id not in pks:
            pks.insert(0, cur_item_value_id)
        for user in auth_models.User.objects.filter(pk__in=pks):
            values.append({'value_id' : user.pk, 'value' : user.username})
    else:
        values = list(FieldChoice.objects \
            .filter(tracker=tracker_id, group=None, field=name) \
            .filter(~Q(status='H')|Q(value_id=cur_item_value_id)) \
            .values('value_id', 'value', 'rank'))
        # value overlays
        overlay_values = list(FieldChoice.objects \
            .filter(tracker=tracker_id, group=group, field=name) \
            .values('value_id', 'value', 'rank', 'status'))
        for o in overlay_values:
            found = False
            i = 0
            for v in values:
                if v['value_id'] == o['value_id']:
                    found = True
                    if o['status'] == 'H':
                        del values[i]
                        i -= 1
                    else:
                        v['value'] = o['value']
                        v['rank'] = o['rank']
                    break
                i += 1
            if not found and o['status'] != 'H' and field_def['scope'] != 'S':
                values.append(o)
        values.sort(key=lambda x: x['rank'])

    # Try to apply a translation:
    for v in values:
        v['value'] = ugettext(v['value'])

    return values

# Auto_increment counters
# We could make this more generic, but we'd have to implement
# per-tracker atomic ID increment manually.
class BugsPublicId   (models.Model): pass
class PatchPublicId  (models.Model): pass
class SupportPublicId(models.Model): pass
class TaskPublicId   (models.Model): pass

class Item(models.Model):
    """
    One tracker item: a bug report, a support request...
    """

    class Meta:
        unique_together = (('tracker', 'public_bugs'),
                           ('tracker', 'public_patch'),
                           ('tracker', 'public_support'),
                           ('tracker', 'public_task'),)

    # Rename 'id' to avoid confusion with public ids below
    internal_id = models.AutoField(primary_key=True)
    tracker = models.ForeignKey('Tracker')

    # Per-tracker public item identifier.  Reason is historical:
    # trackers were stored in different tables, each with its own
    # auto_increment field:
    public_bugs    = models.OneToOneField(BugsPublicId,    blank=True, null=True)
    public_task    = models.OneToOneField(TaskPublicId,    blank=True, null=True)
    public_support = models.OneToOneField(SupportPublicId, blank=True, null=True)
    public_patch   = models.OneToOneField(PatchPublicId,   blank=True, null=True)

    # Non-fields values
    group = models.ForeignKey(auth_models.Group)
    spamscore = models.IntegerField(default=0)
    ip = models.IPAddressField(blank=True, null=True)
    submitted_by = models.ForeignKey(auth_models.User, blank=True, null=True, related_name='items_submitted')
    date = models.DateTimeField(default=datetime.date.today)
    close_date = models.DateTimeField(blank=True, null=True)

    # Forward dependencies
    dependencies = models.ManyToManyField('self', symmetrical=False,
                                          related_name='reverse_dependencies')

    ##
    # Field values
    ##
    # Note: For select boxes, FK should be limited to same group, and
    # to a specific field each e.g.:
    # severity = models.ForeignKey('FieldChoice', to_field='value_id', default=5)
    #            + constraint(same group or 100) + constraint(field='severity')
    # To avoid unnecessary burden, let's drop the above incomplete ForeignKey

    # More generally one can wonder if this should be moved to a M2M
    # item<->field_value table; but after we're done with the
    # migration from the previous database :) Plus it might just be
    # cumbersome, given there's already several hardcoded fields
    # behavior.

    # - fields with hard-coded processing
    summary = models.TextField()
    details = models.TextField()
    privacy = models.IntegerField(default=1)
    discussion_lock = models.IntegerField(default=0)
    vote = models.IntegerField(default=0)
    category_id = models.IntegerField(default=100)
    assigned_to = models.ForeignKey(auth_models.User, related_name='items_assigned', blank=True, null=True)

    # - other fields
    status_id = models.IntegerField(default=100, verbose_name=_("open/closed"))
    resolution_id = models.IntegerField(default=100)
    severity = models.IntegerField(default=5)
    planned_starting_date = models.DateTimeField(blank=True, null=True)
    planned_close_date = models.DateTimeField(blank=True, null=True)
    percent_complete = models.IntegerField(default=1) # SB
    reproducibility_id = models.IntegerField(default=100)
    bug_group_id = models.IntegerField(default=100, verbose_name=_("item group"))
    keywords = models.CharField(max_length=255)
    hours = models.FloatField(default=0.0)
    priority = models.IntegerField(default=5)
    size_id = models.IntegerField(default=100)
    platform_version_id = models.IntegerField(default=100)
    fix_release = models.CharField(max_length=255)
    fix_release_id = models.IntegerField(default=100)
    plan_release = models.CharField(max_length=255)
    plan_release_id = models.IntegerField(default=100)
    release = models.CharField(max_length=255)
    release_id = models.IntegerField(default=100)
    category_version_id = models.IntegerField(default=100)
    component_version = models.CharField(max_length=255)
    originator_name = models.CharField(max_length=255)
    originator_email = models.EmailField(max_length=255)
    originator_phone = models.CharField(max_length=255)

    # - fields dedicated to user customization
    custom_tf1  = models.CharField(max_length=255)
    custom_tf2  = models.CharField(max_length=255)
    custom_tf3  = models.CharField(max_length=255)
    custom_tf4  = models.CharField(max_length=255)
    custom_tf5  = models.CharField(max_length=255)
    custom_tf5  = models.CharField(max_length=255)
    custom_tf6  = models.CharField(max_length=255)
    custom_tf7  = models.CharField(max_length=255)
    custom_tf8  = models.CharField(max_length=255)
    custom_tf9  = models.CharField(max_length=255)
    custom_tf10 = models.CharField(max_length=255)

    custom_ta1  = models.TextField()
    custom_ta2  = models.TextField()
    custom_ta3  = models.TextField()
    custom_ta4  = models.TextField()
    custom_ta5  = models.TextField()
    custom_ta6  = models.TextField()
    custom_ta7  = models.TextField()
    custom_ta8  = models.TextField()
    custom_ta9  = models.TextField()
    custom_ta10 = models.TextField()

    custom_sb1  = models.IntegerField(default=100)
    custom_sb2  = models.IntegerField(default=100)
    custom_sb3  = models.IntegerField(default=100)
    custom_sb4  = models.IntegerField(default=100)
    custom_sb5  = models.IntegerField(default=100)
    custom_sb6  = models.IntegerField(default=100)
    custom_sb7  = models.IntegerField(default=100)
    custom_sb8  = models.IntegerField(default=100)
    custom_sb9  = models.IntegerField(default=100)
    custom_sb10 = models.IntegerField(default=100)

    custom_df1  = models.DateTimeField()
    custom_df2  = models.DateTimeField()
    custom_df3  = models.DateTimeField()
    custom_df4  = models.DateTimeField()
    custom_df5  = models.DateTimeField()

    def get_public_id(self):
        if self.tracker_id == 'bugs':
            return self.public_bugs_id
        elif self.tracker_id == 'patch':
            return self.public_patch_id
        elif self.tracker_id == 'support':
            return self.public_support_id
        elif self.tracker_id == 'task':
            return self.public_task_id

    def get_shortcut(self):
        if self.tracker_id == 'bugs':
            return "bug #%d" % self.public_bugs_id
        elif self.tracker_id == 'patch':
            return "patch #%d" % self.public_bugs_id
        elif self.tracker_id == 'support':
            return "sr #%d" % self.public_bugs_id
        elif self.tracker_id == 'task':
            return "task #%d" % self.public_bugs_id

    def get_tracker_name(self):
        for (k,v) in Tracker.NAME_CHOICES:
            if k == self.tracker_id:
                return v

    def get_summary(self):
        # Unapply HTML entities
        # TODO: convert field to plain text
        return unescape(self.summary)

    def get_priority_css_class(self):
        from string import ascii_letters
        return "prior" + ascii_letters[self.priority-1]

    def get_icon_name(self):
        if self.tracker_id == 'bugs':
            return "bug"
        elif self.tracker_id == 'patch':
            return "patch"
        elif self.tracker_id == 'support':
            return "help"
        elif self.tracker_id == 'task':
            return "task"

    def get_field_defs(self):
        """
        Return fields definition for this group tracker (default
        values + group-specific overlay).  Only apply sensible
        overlay values (cf. FieldOverlay model definition).
        """
        fields = deepcopy(field_defs)
        for overlays in (FieldOverlay.objects.filter(tracker=self.tracker_id, group=None),
                         FieldOverlay.objects.filter(tracker=self.tracker_id, group=self.group)):
            for overlay in overlays:
                name = overlay.field
                overlay.apply_on(fields[name])
        for name in fields:
            if fields[name]['display_type'] == 'SB':
                fields[name]['choices'] = field_get_values(self.tracker_id, self.group,
                                                          fields[name], self.get_value(name))
        return fields

    def get_form_fields(self, user=None):
        """
        Return displayable fields, ordered by rank
        """
        fields = self.get_field_defs()
        ret = []
        for name in fields.keys():
            if (not (fields[name]['required'] or fields[name]['use_it'])
                or fields[name]['special']):
                continue
            ret.append((name,fields[name]))
        ret.sort(key=lambda x: x[1]['rank'])
        return ret

    def get_value(self, key):
        if key == 'comment_type_id':
            # not stored in the item, but in the history
            # TODO: it actually has nothing do in fields definitions
            # (not part of the generic form, not a stored value); move
            # it out!
            return None
        elif key in ('submitted_by', 'assigned_to'):
            return getattr(self, key+'_id')
        else:
            return getattr(self, key)

    def get_form(self, user=None):
        # TODO: privacy
        # TODO: privileges
        form_fields = self.get_form_fields()
        html = '';
        for field_no, (name,field) in enumerate(form_fields):
            value = self.get_value(name)

            if field_no % 2 == 0:
                html += '<tr>'

            html += u'<th><span class="help" title="%s">%s</span></th>\n' % (field['description'], field['label']+ugettext(": "))

            html += '<td>'
            if field['display_type'] == 'DF':
                html += u'<select name="%s_dayfd" value="TODO">\n' % (name)
                for i in range(1,31+1):
                    html += '<option value="%d">%d</option>\n' % (i, i)
                html += '</select>\n'
                html += u'<select name="%s_monthfd" value="TODO">\n' % (name)
                for i,langinfo_constant in enumerate( \
                    (locale.MON_1, locale.MON_2, locale.MON_3, locale.MON_4,
                     locale.MON_4, locale.MON_6, locale.MON_7, locale.MON_8,
                     locale.MON_9, locale.MON_10, locale.MON_11, locale.MON_12)):
                    html += '<option value="%d">%s</option>\n' % (i, locale.nl_langinfo(langinfo_constant))
                html += '</select>\n'
                html += u'<input type="text" size="4" maxlength="4" name="%s_yearfd" value="TODO">' % (name)
            elif field['display_type'] == 'SB':
                html += u'<select name="%s">\n' % name
                for option in field['choices']:
                    selected = ''
                    if option['value_id'] == value:
                        selected = ' selected="selected"'
                    html += u'<option value="%d"%s>%s</option>\n' % (option['value_id'], selected, option['value'])
                html += '</select>'
            elif field['display_type'] == 'TA':
                # TODO: display_size
                html += u'<textarea name="%s">%s</textarea>' % (name, value)
            elif field['display_type'] == 'TF':
                # TODO: display_size
                html += u'<input type="text" name="%s" value="%s" />' % (name, value)
            html += '</td>\n'

            if field_no % 2 == 1:
                html += '</tr>\n'
        if field_no % 2 == 0:  # close if odd number of fields
            html += '</tr>\n'

        #return mark_safe(''.join(['%s (%d)<br />' % (f, v['rank']) for f,v in form_fields]))
        return mark_safe(html)

    @models.permalink
    def get_absolute_url(self):
        return ('savane:tracker:item_detail', [self.tracker_id, self.get_public_id()])

    def __unicode__(self):
        return "%s #%d" % (self.tracker_id, self.get_public_id())

class ItemMsgId(models.Model):
    """
    Identifier for 'Message-Id' and 'References' e-mail fields, used
    to group messages by conversation
    """
    item = models.ForeignKey('Item')
    msg_id = models.CharField(max_length=255)


class ItemHistory(models.Model):
    """
    This stores 2 kinds of values:
    - item comments (field='details')
    - value changes, for fields that have history tracking enabled
    """
    item = models.ForeignKey('Item')
    field = models.CharField(max_length=32)
       # Should be: field = models.ForeignKey('Field', to_field='name')
       #            + constraint (item.tracker=field.tracker)
       # or simply: field = models.ForeignKey('Field')
       # But as it's a history field, adding constraints might be just bad.
    old_value= models.TextField(blank=True, null=True)
    new_value= models.TextField()
    mod_by = models.ForeignKey(auth_models.User)
    date = models.DateTimeField(default=datetime.date.today)
    ip = models.IPAddressField(blank=True, null=True)

    # Specific (bad!) field for 'details'
    # I guess 'details' could be stored separately.
    type = models.IntegerField(_("comment type"), blank=True, null=True)
      # Should be:
      # type = models.ForeignKey('FieldChoice', to_field='value_id')
      #        + constraint(same group or 100) + constraint(field='comment_type_id')
      # The purpose is to add <strong>[$comment_type]</strong> when
      # displaying an item comment.
    spamscore = models.IntegerField(_("total spamscore for this comment"))

class ItemCc(models.Model):
    """
    Item carbon copies for mail notifications
    """
    item = models.ForeignKey('Item')
    email = models.EmailField(max_length=255)
    added_by = models.ForeignKey(auth_models.User)
    comment = models.TextField()
    date = models.DateTimeField(default=datetime.date.today)

#class ItemDependencies:
# => cf. Item.dependencies

class ItemFile(models.Model):
    """
    One file attached to an item.
    """
    item = models.ForeignKey('Item')
    submitted_by = models.ForeignKey(auth_models.User)
    date = models.DateTimeField(default=datetime.date.today)
    description = models.TextField()
    filename = models.TextField()
    filesize = models.IntegerField(default=0)
    filetype = models.TextField()
    # /!\ `file` longblob NOT NULL - if not savane-cleanup

class ItemSpamScore(models.Model):
    """
    Spam reports

    Score is summed in ItemHistory.spamscore.
    """
    score = models.IntegerField(default=1)
    affected_user = models.ForeignKey(auth_models.User, related_name='itemspamscore_affected_set')
    reporter_user = models.ForeignKey(auth_models.User, related_name='itemspamscore_reported_set')
    item = models.ForeignKey('Item')
    comment_id = models.ForeignKey('ItemHistory', null=True)


# TODO:
# - trackers_notification  # yes/no configuration depending on the events and roles
# - groups  # per-group notification settings
# - bugs_canned_responses

# Re-implement?  Not much used:
# - user_squad
# - trackers_field_transition
# - trackers_field_transition_other_field_update
# - trackers_watcher
# - trackers_export  # to implement differently
# - trackers_spamban  # spamassassin gateway
# - trackers_spamcheck_queue
# - trackers_spamcheck_queue_notification
# - user_votes

# Depends if we display in a compatible manner:
# - user_preferences # per-tracker browse configuration
# - bugs_report
# - bugs_report_field

# Feature disabled in 2004 by yeupou, empty tables:
# http://svn.gna.org/viewcvs/savane?view=rev&rev=3094
# http://svn.gna.org/viewcvs/savane/savane/trunk/frontend/php/include/trackers_run/index.php?rev=3094&view=diff&r1=3094&r2=3093&p1=savane/trunk/frontend/php/include/trackers_run/index.php&p2=/savane/trunk/frontend/php/include/trackers_run/index.php
# - bugs_filter

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
from django.utils.translation import ugettext, ugettext_lazy as _
import django.contrib.auth.models as auth_models
import datetime
from savane.utils import htmlentitydecode, unescape

# TODO: default '100' (aka 'nobody' or 'None', depending on
# fields) -> change to NULL?

# Date fields: use default=... rather than auto_now_add=...; indeed,
# auto_now_add cannot be overriden, hence it would mess data imports.

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


class Field(models.Model):
    """
    Site-wide field definitions for the 4 trackers: 70 fields each, +
    2 more for 'task' ('planned_starting_date', 'planned_close_date'),
    1 more for 'patch' ('revision tag').

    Most fields cannot be redefined (such as display_type or
    scope). Usually fields that can be redefined are in FieldUsage,
    where an entry with special group_id=100 contains the default
    value.

    However some of the fields in this class ('display_size',
    'empty_ok', and 'keep_history') can be redefined through similar
    fields in FieldUsage - in which case it's not clear whether the
    default value is:

    - in Field(tracker_id, field_name)

    - or FieldUsage(tracker_id, group_id=100, field_name)

    At first glance it's defined here, all related values in
    FieldUsage are set to NULL.

    Field definition is almost identical for all trackers (59 fields /
    73 have the same configuration).  They could be regrouped.

    SELECT COUNT(*) FROM (
            SELECT field_name FROM bugs_field
      UNION SELECT field_name FROM patch_field
      UNION SELECT field_name FROM support_field
      UNION SELECT field_name FROM task_field
    ) subquery;
    => 73

    SELECT COUNT(*), field_name FROM (
            SELECT * FROM bugs_field
      UNION SELECT * FROM patch_field
      UNION SELECT * FROM support_field
      UNION SELECT * FROM task_field
    ) subquery
    GROUP BY field_name HAVING COUNT(*) > 1;
    +----------+---------------------+
    | COUNT(*) | field_name          |
    +----------+---------------------+
    |        2 | assigned_to         |
    |        2 | category_version_id |
    |        2 | close_date          |
    |        3 | comment_type_id     |
    |        2 | date                |
    |        3 | fix_release         |
    |        3 | fix_release_id      |
    |        3 | hours               |
    |        2 | keywords            |
    |        4 | plan_release        |
    |        3 | plan_release_id     |
    |        4 | priority            |
    |        2 | resolution_id       |
    |        2 | size_id             |
    +----------+---------------------+
    14 rows in set (0.00 sec)
    """
    class Meta:
        unique_together = (('tracker', 'name'),)
        verbose_name = _("field")
        verbose_name_plural = _("fields")

    DISPLAY_TYPE_CHOICES = (('DF', _('date field')),
                            ('SB', _('select box')),
                            ('TA', _('text area')),
                            ('TF', _('text field')),)
    SCOPE_CHOICES = (('S', _('system')), # user cannot modify related FieldValue's (TF)
                     ('P', _('project')),)  # user can modify related FieldValue's (TF)

    tracker = models.ForeignKey('Tracker')
    name = models.CharField(max_length=255, db_index=True)
    display_type = models.CharField(max_length=255, choices=DISPLAY_TYPE_CHOICES)
    display_size = models.CharField(max_length=255)
      # DF: unused
      # SB: unused
      # TA: cols/rows
      # TF: visible_length/max_length
    label  = models.CharField(max_length=255)
    description = models.TextField()

    # Field values can be changed (if TF)
    scope = models.CharField(max_length=1, choices=SCOPE_CHOICES)
    # Field cannot be hidden (but can be made optional)
    required = models.BooleanField(help_text=_("field cannot be disabled in configuration"))
    # Default value (fields can always override this except for 'summary' and 'details', cf. 'special')
    empty_ok = models.BooleanField()
    # Default value + Field may store history changes
    keep_history = models.BooleanField()
    # Field cannot be made optional (displayed unless 'bug_id' and 'group_id')
    # Also, field are not displayed (filled by the system) - except for 'summary', 'comment_type' and 'details'
    # (consequently, they cannot be customized in any way, except for 'summary' and 'details' where you can only customize the display size)
    special = models.BooleanField()
    # Field may change label and description
    custom = models.BooleanField(help_text=_("let the user change the label and description"))

    def __unicode__(self):
        return "%s.%s" % (self.tracker_id, self.name)

class FieldUsage(models.Model):
    """
    Field configuration overlay for each group
    group == NULL means default
    """
    class Meta:
        unique_together = (('field', 'group'),)
        verbose_name = _("field usage")
        verbose_name_plural = _("field usages")

    TRANSITION_DEFAULT_AUTH_CHOICES = (('', _('undefined')),
                                       ('A', _('allowed')),
                                       ('F', _('forbidden')),)
    SHOW_ON_ADD_CHOICES = (('0', _('no')),
                           ('1', _('show to logged in users')),
                           ('2', _('show to anonymous users')),
                           ('3', _('show to both logged in and anonymous users')),)
    CUSTOM_EMPTY_OK_CHOICES = (('0', _('mandatory only if it was presented to the original submitter')),
                               ('1', _('optional (empty values are accepted)')),
                               ('3', _('mandatory')),)
    field = models.ForeignKey('Field')
    group = models.ForeignKey(auth_models.Group, blank=True, null=True, help_text=_("NULL == default"))

    # If not Field.required:
    use_it = models.BooleanField(_("used"))
    show_on_add = models.CharField(max_length=1, choices=SHOW_ON_ADD_CHOICES,
                                   default='0', blank=True, null=True)
      # new:
      # show_on_add_logged_in = models.BooleanField("show to logged in users")
      # show_on_add_anonymous = models.BooleanField("show to anonymous users")
    show_on_add_members = models.BooleanField(_("show to project members"))

    # Can always be changed (expect for special 'summary' and 'details')
    custom_empty_ok = models.CharField(max_length=1, choices=CUSTOM_EMPTY_OK_CHOICES,
                                       default='0', blank=True, null=True)

    # Can always be changed
    place = models.IntegerField(help_text=_("display rank")) # new:rank

    # ???
    # Specific to SB
    transition_default_auth = models.CharField(max_length=1, choices=TRANSITION_DEFAULT_AUTH_CHOICES, default='A')

    # Specific to TA and TF
    # Works for both custom and non-custom fields
    custom_display_size = models.CharField(max_length=255, blank=True, null=True)
      # The default value is in Field.display_size
      #   rather than FieldUsage(group_id=100).custom_display_size
    custom_keep_history = models.BooleanField(_("keep field value changes in history"))

    # If Field.custom
    # Specific (bad!) fields for custom fields (if Field.custom is True):
    custom_label = models.CharField(max_length=255, blank=True, null=True)
    custom_description = models.CharField(max_length=255, blank=True, null=True)

class FieldValue(models.Model):
    """
    Choice for a select-box (SB) field of a specific group
    """
    class Meta:
        unique_together = (('bug_field', 'group', 'value_id'),)

    STATUS_CHOICES = (('A', _('active')),
                      ('H', _('hidden')), # mask previously-active or system fields
                      ('P', _('permanent')),) # status cannot be modified, always visible
    bug_field = models.ForeignKey('Field')
    group = models.ForeignKey(auth_models.Group) # =100 for system-wide values
    value_id = models.IntegerField(db_index=True) # group_specific value identifier
      # It's not a duplicate of 'id', as it's the value referenced by
      # Item fields, and the configuration of that value can be
      # customized per-project.
    value = models.CharField(max_length=255) # label
    description = models.TextField()
    order_id = models.IntegerField() # new:rank
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A', db_index=True)

    # Field category: specific (bad!) field for e-mail notifications
    email_ad = models.TextField(help_text=_("comma-separated list of e-mail addresses to notify when an item is created or modified in this category"))
    send_all_flag = models.BooleanField(_("send on all updates"), default=True)

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
    submitted_by = models.ForeignKey(auth_models.User, default=100)
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
    # severity = models.ForeignKey('FieldValue', to_field='value_id', default=5)
    #            + constraint(same group or 100) + constraint(field_name='severity')
    # To avoid unnecessary burden, let's drop the above incomplete ForeignKey

    # More generally one can wonder if this should be moved to a M2M
    # bug<->field table; but after we're done with the migration from
    # the previous database :)

    # - fields with hard-coded processing
    summary = models.TextField()
    details = models.TextField()
    privacy = models.IntegerField(default=5)
    discussion_lock = models.IntegerField(default=0)
    vote = models.IntegerField(default=0)
    category_id = models.IntegerField(default=100)
    assigned_to = models.IntegerField(default=100)

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

    def get_form(self, user):
        
        pass

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
    - item comments (field_name='details')
    - value changes, for fields that have history tracking enabled
    """
    item = models.ForeignKey('Item')
    field_name = models.CharField(max_length=255)
       # Should be: field_name = models.ForeignKey('Field', to_field='name')
       #            + constraint (item.tracker=field.tracker)
       # or simply: field_name = models.ForeignKey('Field')
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
      # type = models.ForeignKey('FieldValue', to_field='value_id')
      #        + constraint(same group or 100) + constraint(field_name='comment_type_id')
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

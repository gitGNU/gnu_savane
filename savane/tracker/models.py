from django.db import models

# Create your models here.
class Tracker(models.Model):
    NAME_CHOICES = (('bugs', 'bugs'),
                    ('patches', 'patches'),
                    ('support', 'support'),
                    ('tasks', 'tasks'),
                    )
    name = models.CharField(max_length=7, choices=NAME_CHOICES)

class Field(models.Model):
    DISPLAY_TYPE_CHOICES = (('DF', 'date field'),
                            ('SB', 'select box'),
                            ('TA', 'text area'),
                            ('TF', 'text field'),)
    SCOPE_CHOICES = (('S', 'system'),
                     ('P', 'project'),)

    tracker = models.ForeignKey("Tracker")
    name = models.CharField(max_length=255, db_index=True)
    display_type = models.CharField(max_length=255, choices=DISPLAY_TYPE_CHOICES)
    display_size = models.CharField(max_length=255)
      # new:
      # display_size_min = models.IntegerField(blank=True, null=True)
      # display_size_max = models.IntegerField(blank=True, null=True)
    label  = models.CharField(max_length=255)
    description = models.TextField()
    scope = models.CharField(max_length=1, choices=SCOPE_CHOICES)
    required = models.BooleanField()
    empty_ok = models.BooleanField()
    keep_history = models.BooleanField()
    special = models.BooleanField(help_text="field is not entered by the user but by the system")
    custom = models.BooleanField(help_text="let the user change the label and description")

class FieldUsage(models.Model):
    TRANSITION_DEFAULT_AUTH_CHOICES = (('', 'undefined'),
                                       ('A', 'allowed'),
                                       ('F', 'forbidden'),)
    SHOW_ON_ADD_CHOICES = (('0', 'no'),
                           ('1', 'show to logged in users'),
                           ('2', 'show to anonymous users'),
                           ('3', 'show to both logged in and anonymous users'),)
    CUSTOM_EMPTY_OK_CHOICES = (('0', 'mandatory only if it was presented to the original submitter'),
                               ('1', 'optional (empty values are accepted)'),
                               ('3', 'mandatory'),)
    group = models.ForeignKey('auth.Group')
    use_it = models.BooleanField("used")
    show_on_add = models.CharField(max_length=1, choices=SHOW_ON_ADD_CHOICES,
                                   default='0', blank=True, null=True)
      # new:
      # show_on_add_logged_in = models.BooleanField("show to logged in users")
      # show_on_add_anonymous = models.BooleanField("show to anonymous users")
    show_on_add_members = models.BooleanField("show to project members")
    place = models.IntegerField() # new:rank
    transition_default_auth = models.CharField(max_lenth=1, choices=TRANSITION_DEFAULT_AUTH, default='A')
    
    # Specific (bad!) fields for custom fields:
    custom_label = models.CharField(max_length=255, blank=True, null=True)
    custom_description = models.CharField(max_length=255, blank=True, null=True)
    custom_display_size = models.CharField(max_length=255, blank=True, null=True)
      # new:
      # custom_display_size_min = models.IntegerField(blank=True, null=True)
      # custom_display_size_max = models.IntegerField(blank=True, null=True)
    custom_empty_ok = models.CharField(max_length=1, choices=CUSTOM_EMPTY_OK_CHOICES,
                                       default='0', blank=True, null=True)
    custom_keep_history = models.BooleanField("keep field value changes in history")

class FieldValue(models.Model):
    """
    Choice for a select-box (SB) field
    """
    class Meta:
        unique_together = (('bug_field', 'group', 'value_id'),)

    STATUS_CHOICES = (('A', 'active'),
                      ('H', 'hidden'), # mask previously-active or system fields
                      ('P', 'permanent'),) # status cannot be modified, always visible
    bug_field = models.ForeignKey('Field')
    group = models.ForeignKey('auth.Group')
    value_id = models.IntegerField(db_index=True) # group_specific value identifier
      # somehow duplicate of 'id', but might be useful when moving a bug to another group
    value = models.CharField(max_length=255) # label
    description = models.TextField()
    order_id = models.IntegerField() # new:rank
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A', db_index=True)

    # Field category: specific (bad!) field for e-mail notifications
    email_ad = models.TextField(help_text="comma-separated list of e-mail addresses"
                                + " to notify when an item is created or modified"
                                + " in this category")
    send_all_flag = models.BooleanField("send on all updates", default=True)


class Item(models.Model):
    # TODO: default '100' (aka 'nobody' or 'None', depending on
    # fields) -> change to NULL?

    group = models.ForeignKey('auth.Group')
    spamscore = models.IntegerField(default=0)
    ip = IPAddressField(blank=True, null=True)
    submitted_by = models.ForeignKey('auth.User', default=100)
    date = models.DateTimeField()
    close_date = models.DateTimeField(blank=True, null=True)

    ##
    # Field values
    ##
    # Note: For select boxes, FK should be limited to same group, and
    # to a specific field each e.g.:
    # severity = models.ForeignKey('FieldValue', to_field='value_id', default=5)
    #            + constraint(same group) + constraint(field_name='severity')
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
    status_id = models.IntegerField(default=100, verbose_name="open/closed")
    resolution_id = models.IntegerField(default=100)
    severity = models.IntegerField(default=5)
    planned_starting_date = models.DateTimeField(blank=True, null=True)
    planned_close_date = models.DateTimeField(blank=True, null=True)
    percent_complete = models.IntegerField(default=1) # SB
    reproducibility_id = models.IntegerField(default=100)
    bug_group_id = models.IntegerField(default=100, verbose_name="item group")
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
    originator_email = models.CharField(max_length=255)
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

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
    label  = models.CharField(max_length=255)
    description = models.TextField()
    scope = models.CharField(max_length=1, choices=SCOPE_CHOICES)
    required = models.BooleanField()
    empty_ok = models.BooleanField()
    keep_history = models.BooleanField()
    special = models.BooleanField() # TODO: ???
    custom = models.BooleanField() # TODO: ???

class FieldValue(models.Model):
    """
    Values for select-box (SB) fields
    """
    STATUS_CHOICES = (('A', 'active'),
                      ('H', 'hidden'), # mask previously-active or system fields
                      ('P', 'permanent'),) # status cannot be modified, always visible
    bug_field = models.ForeignKey('Field')
    group = models.ForeignKey(auth.Group, null=True)
      # => NULL if value is system-wide;
      # but not a duplicate of status='P': 114 group_id's for status=H at SV
    value_id = models.IntegerField(db_index=True) # TODO: ???
    value = models.CharField(max_length=255)
    description = models.TextField()
    rank = models.IntegerField() # old:order_id
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A', db_index=True)

    # Field category: specific (bad!) field for e-mail notifications
    email_ad = models.TextField(help_text="comma-separated list of e-mail addresses")
    send_all_flag = models.BooleanField(default=True)

class FieldUsage(models.Model):
    group = models.ForeignKey(auth.Group)
  #`use_it` int(11) NOT NULL default '0',
  #`show_on_add` int(11) NOT NULL default '0',
  #`show_on_add_members` int(11) NOT NULL default '0',
  #`place` int(11) NOT NULL default '0',
  #`custom_label` varchar(255) default NULL,
  #`custom_description` varchar(255) default NULL,
  #`custom_display_size` varchar(255) default NULL,
  #`custom_empty_ok` int(11) default NULL,
  #`custom_keep_history` int(11) default NULL,
  #`transition_default_auth` char(1) NOT NULL default 'A',



class Item(models.Model):
    pass
  #group = models.ForeignKey(auth.Group)
  #`status_id` int(11) NOT NULL default '100',
  #`severity` int(11) NOT NULL default '5',
  #`privacy` int(2) NOT NULL default '1',
  #`discussion_lock` int(1) default '0',
  #`vote` int(11) NOT NULL default '0',
  #`spamscore` int(2) default '0',
  #`ip` varchar(15) default NULL,
  #`category_id` int(11) NOT NULL default '100',
  #`submitted_by` int(11) NOT NULL default '100',
  #`assigned_to` int(11) NOT NULL default '100',
  #`date` int(11) NOT NULL default '0',
  #`summary` text,
  #`details` text,
  #`close_date` int(11) default NULL,
  #`bug_group_id` int(11) NOT NULL default '100',
  #`resolution_id` int(11) NOT NULL default '100',
  #`category_version_id` int(11) NOT NULL default '100',
  #`platform_version_id` int(11) NOT NULL default '100',
  #`reproducibility_id` int(11) NOT NULL default '100',
  #`size_id` int(11) NOT NULL default '100',
  #`fix_release_id` int(11) NOT NULL default '100',
  #`plan_release_id` int(11) NOT NULL default '100',
  #`hours` float(10,2) NOT NULL default '0.00',
  #`component_version` varchar(255) NOT NULL default '',
  #`fix_release` varchar(255) NOT NULL default '',
  #`plan_release` varchar(255) NOT NULL default '',
  #`priority` int(11) NOT NULL default '5',
  #`planned_starting_date` int(11) default NULL,
  #`planned_close_date` int(11) default NULL,
  #`percent_complete` int(11) NOT NULL default '1',
  #`keywords` varchar(255) NOT NULL default '',
  #`release_id` int(11) NOT NULL default '100',
  #`release` varchar(255) NOT NULL default '',
  #`originator_name` varchar(255) NOT NULL default '',
  #`originator_email` varchar(255) NOT NULL default '',
  #`originator_phone` varchar(255) NOT NULL default '',
  #`custom_tf1` varchar(255) NOT NULL default '',
  #`custom_tf2` varchar(255) NOT NULL default '',
  #`custom_tf3` varchar(255) NOT NULL default '',
  #`custom_tf4` varchar(255) NOT NULL default '',
  #`custom_tf5` varchar(255) NOT NULL default '',
  #`custom_tf6` varchar(255) NOT NULL default '',
  #`custom_tf7` varchar(255) NOT NULL default '',
  #`custom_tf8` varchar(255) NOT NULL default '',
  #`custom_tf9` varchar(255) NOT NULL default '',
  #`custom_tf10` varchar(255) NOT NULL default '',
  #`custom_ta1` text NOT NULL,
  #`custom_ta2` text NOT NULL,
  #`custom_ta3` text NOT NULL,
  #`custom_ta4` text NOT NULL,
  #`custom_ta5` text NOT NULL,
  #`custom_ta6` text NOT NULL,
  #`custom_ta7` text NOT NULL,
  #`custom_ta8` text NOT NULL,
  #`custom_ta9` text NOT NULL,
  #`custom_ta10` text NOT NULL,
  #`custom_sb1` int(11) NOT NULL default '100',
  #`custom_sb2` int(11) NOT NULL default '100',
  #`custom_sb3` int(11) NOT NULL default '100',
  #`custom_sb4` int(11) NOT NULL default '100',
  #`custom_sb5` int(11) NOT NULL default '100',
  #`custom_sb6` int(11) NOT NULL default '100',
  #`custom_sb7` int(11) NOT NULL default '100',
  #`custom_sb8` int(11) NOT NULL default '100',
  #`custom_sb9` int(11) NOT NULL default '100',
  #`custom_sb10` int(11) NOT NULL default '100',
  #`custom_df1` int(11) NOT NULL default '0',
  #`custom_df2` int(11) NOT NULL default '0',
  #`custom_df3` int(11) NOT NULL default '0',
  #`custom_df4` int(11) NOT NULL default '0',
  #`custom_df5` int(11) NOT NULL default '0',

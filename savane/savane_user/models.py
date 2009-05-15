from django.db import models

class User(models.Model):
    user_id = models.IntegerField(primary_key=True)
    user_name = models.TextField()
    email = models.TextField()
    user_pw = models.CharField(max_length=96)
    realname = models.CharField(max_length=96)
    status = models.CharField(max_length=48)
    spamscore = models.IntegerField(null=True, blank=True)
    add_date = models.IntegerField()
    confirm_hash = models.CharField(max_length=96, blank=True)
    authorized_keys = models.TextField(blank=True)
    authorized_keys_count = models.IntegerField(null=True, blank=True)
    email_new = models.TextField(blank=True)
    people_view_skills = models.IntegerField()
    people_resume = models.TextField()
    timezone = models.CharField(max_length=192, blank=True)
    theme = models.CharField(max_length=45, blank=True)
    email_hide = models.CharField(max_length=9, blank=True)
    gpg_key = models.TextField(blank=True)
    gpg_key_count = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'user'

from django.db import models
#from django.db.models import Manager
from django.contrib.auth.models import User, UserManager
#from django.contrib.auth.models import User

class User(User):
    realname = models.CharField(max_length=96)
    status = models.CharField(max_length=48)
    spamscore = models.IntegerField(null=True, blank=True)
    confirm_hash = models.CharField(max_length=96, blank=True, null=True)
    authorized_keys = models.TextField(blank=True, null=True)
    authorized_keys_count = models.IntegerField(null=True, blank=True)
    people_view_skills = models.IntegerField(null=True)
    people_resume = models.TextField()
    timezone = models.CharField(max_length=192, blank=True, null=True)
    theme = models.CharField(max_length=45, blank=True, null=True)
    email_hide = models.CharField(max_length=9, blank=True, null=True)
    gpg_key = models.TextField(blank=True, null=True)
    gpg_key_count = models.IntegerField(null=True, blank=True)
    objects = UserManager()

    class Meta():
        db_table = u'user'



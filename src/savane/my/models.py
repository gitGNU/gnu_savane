# User extra attributes
# Copyright (C) 2009  Sylvain Beucler
# Copyright (C) 2009  Jonathan Gonzalez V.
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
from django.contrib.auth.models import User, UserManager

class ExtendedUser(User):
    # Migrated to 'firstname' in auth.User
    #realname = models.CharField(max_length=96)

    # Old Savane can be Active/Deleted/Pending/Suspended/SQuaD
    status = models.CharField(max_length=48)

    # Used by trackers only but it could be used more widely
    spamscore = models.IntegerField(null=True, blank=True)
    # Previously used for e-mail changes and password recovery, Django
    # does it different with a auth.tokens
    #confirm_hash = models.CharField(max_length=96, blank=True, null=True)

    # Keys
    authorized_keys = models.TextField(blank=True, null=True)
    authorized_keys_count = models.IntegerField(null=True, blank=True)
    gpg_key = models.TextField(blank=True, null=True)
    gpg_key_count = models.IntegerField(null=True, blank=True)

    # Personal info
    people_resume = models.TextField()

    # Preferences - /!\ some are also in the user_preferences table
    people_view_skills = models.IntegerField(null=True)
    timezone = models.CharField(max_length=192, blank=True, null=True)
    theme = models.CharField(max_length=45, blank=True, null=True)
    email_hide = models.CharField(max_length=9, blank=True, null=True)


    # Inherit specialized models.Manager with convenience functions
    objects = UserManager()

# Jobs models
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
from django.contrib.auth import models as auth_models
from django.utils.translation import ugettext, ugettext_lazy as _
import datetime

class Job(models.Model):
    status_CHOICES = (
        ('1', _('Open')),
        ('2', _('Filled')),
        ('3', _('Deleted')),
        )

    group = models.ForeignKey(auth_models.Group)
    created_by =  models.ForeignKey(auth_models.User)
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1, choices=status_CHOICES)
    category = models.ForeignKey("Category")


class Label(models.Model):
    class Meta:
        abstract = True
    active = models.BooleanField(default=True)
    label = models.CharField(max_length=255)

class Category(Label):
    pass

class Skill(Label):
    pass
class SkillLevel(Label):
    pass
class SkillYear(Label):
    pass

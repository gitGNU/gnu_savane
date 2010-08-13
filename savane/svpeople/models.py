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

class OpenJobManager(models.Manager):
    def get_query_set(self):
        return super(self.__class__, self).get_query_set().filter(status=1)

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

    objects = models.Manager() # default manager
    open_objects = OpenJobManager()

    def __unicode__(self):
        return "%s" % (self.title)

class Label(models.Model):
    class Meta:
        abstract = True
    active = models.BooleanField(default=True)
    label = models.CharField(max_length=255)

    def __unicode__(self):
        return "%s" % (self.label)

class Category(Label):
    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")
    def open_job_set(self):
        return self.job_set.filter(status=1)

class Skill(Label):
    pass
class SkillLevel(Label):
    pass
class SkillYear(Label):
    pass

# Cf. fixtures/*.yaml
default_categories_marked_for_translation = (
    _("Developer"),
    _("Project manager"),
    _("Unix admin"),
    _("Doc writer"),
    _("Tester"),
    _("Support manager"),
    _("Graphic/other designer"),
    _("Translator"),
)
default_skill_levels_marked_for_translation = (
    _("Base knowledge"),
    _("Good knowledge"),
    _("Master"),
    _("Master apprentice"),
    _("Expert"),
)
default_skill_years_marked_for_translation = (
    _("(< 6 months)"),
    _("6 Mo - 2 yr"),
    _("2 yr - 5 yr"),
    _("5 yr - 10 yr"),
    _("> 10 years"),
)

class JobInventory(models.Model):
    job = models.ForeignKey(Job)
    skill = models.ForeignKey(Skill)
    skill_level = models.ForeignKey(SkillLevel)
    skill_year = models.ForeignKey(SkillYear)

class SkillInventory(models.Model):
    user = models.ForeignKey(auth_models.User)
    skill = models.ForeignKey(Skill)
    skill_level = models.ForeignKey(SkillLevel)
    skill_year = models.ForeignKey(SkillYear)

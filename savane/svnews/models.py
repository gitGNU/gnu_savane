# News and comments structure
# Copyright (C) 2004, 2005  Mathieu Roy
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
import django.contrib.auth.models as auth_models
from savane.utils import markup
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _, ungettext

# - news_byte
class ApprovedNewsManager(models.Manager):
    def get_query_set(self):
        return super(self.__class__, self).get_query_set().filter(is_approved__in=(0,1,2))
class News(models.Model):
    """
    One piece of news
    """
    class Meta:
        ordering = ('-date',)

    IS_APPROVED_CHOICES = (
        ('0', 'approved for project page'),
        ('1', 'approved for site frontpage news'),
        ('2', 'refused for site frontpage news'),
        ('4', 'removed'),
        ('5', 'proposed'),
        )
    group = models.ForeignKey(auth_models.Group)
    submitted_by = models.ForeignKey(auth_models.User)
    is_approved = models.CharField(max_length=1, choices=IS_APPROVED_CHOICES, db_index=True)
    date = models.DateTimeField(auto_now_add=True, db_index=True)
    date_last_edit = models.DateTimeField(auto_now=True, db_index=True)
    summary = models.CharField(max_length=255)
    details = models.TextField()
    # Savane3's 'forum_id', the most visible id, is now 'id'.
    # Savane3's 'id', only used in administration screens, is dropped.

    objects = models.Manager() # default manager
    approved_objects = ApprovedNewsManager()

    def get_details_short(self):
        # if the news item is large (>500 characters),
        # only show about 250 characters of the story
        story = self.details
        strlen_story = len(story);
        if strlen_story > 500:
            # if there is a linebreak close to the 250 character
            # mark, we use it to truncate the news item, so that
            # the markup will not be confused.
            # We accept the range from 240 to 350 characters, else
            # the news item will be split on whitespace.
            # See bug #7634
            linebreak = self.details.find("\n", min(strlen_story, 240))
            if linebreak >= 0 and linebreak < 350:
                truncate = linebreak
            else:
                truncate = story[:250].rfind(' ')
                if truncate == False:
                    truncate = 250
            summ_txt = story[:truncate]
            summ_txt += " ..."
            summ_txt = markup.full(summ_txt)
            summ_txt += '<br />'
            summ_txt += '<a href="%s">' % reverse('savane:svnews:news_detail', args=[self.pk])
            summ_txt += _("[Read more]")
            summ_txt += '</a>'
        else:
            # this is a short news item. just display it.
            summ_txt = markup.full(story)
        return summ_txt

class Comment(models.Model):
    """
    A comment on the news item
    """
    news = models.ForeignKey(News)  # savane_old: uses forum_id through forum_group_list
    posted_by = models.ForeignKey(auth_models.User, related_name='svnews_comment_set')
    subject = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True, db_index=True)
    is_followup_to = models.ForeignKey("Comment")
    thread = models.ForeignKey("Thread")
    #has_followups = models.BooleanField()

class Notification(models.Model):
    """
    Notify this User when comments are posted to this item
    """
    news = models.ForeignKey(News)  # savane_old: uses forum_id through forum_group_list
    user = models.ForeignKey(auth_models.User)

class LastVisit(models.Model):
    """
    Mark the last visit date from a user, so that comments posted
    since then are highlighted
    """
    news = models.ForeignKey(News)  # savane_old: uses forum_id through forum_group_list
    user = models.ForeignKey(auth_models.User)
    date = models.DateTimeField(auto_now=True)

class Thread(models.Model):
    """
    Counter for top-level discussions ("threads")

    Threads are currently used to get all messages in a thread without
    using expensive recursive querying.

    TODO: there are better SQL solutions based on tree structures
    """
    pass

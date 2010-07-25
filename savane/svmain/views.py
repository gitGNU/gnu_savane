# Manage user attributes
# Copyright (C) 2009  Sylvain Beucler
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

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
import django.contrib.auth.models as auth_models
from django.contrib import messages
import models as svmain_models
from annoying.decorators import render_to

def user_redir(request, slug):
    u = get_object_or_404(auth_models.User, username=slug)
    return HttpResponseRedirect(reverse('savane.svmain.user_detail', args=(slug,)))

def group_redir(request, slug):
    g = get_object_or_404(auth_models.Group, name=slug)
    return HttpResponseRedirect(reverse('savane.svmain.group_detail', args=(slug,)))

def group_join(request, slug):
    g = get_object_or_404(auth_models.Group, name=slug)
    if svmain_models.Membership.objects.filter(user=request.user, group=g).count():
        messages.error(request, u"Request for inclusion already registered")
    else:
        svmain_models.Membership(user=request.user, group=g, admin_flags='P').save()
        # TODO: send e-mail notification to group admins
        messages.success(request, u"Request for inclusion sent to project administrators")
    return HttpResponseRedirect('../')

@render_to('svmain/group_admin.html', mimetype=None)
def group_admin(request, slug, extra_context={}):
    group = get_object_or_404(auth_models.Group, name=slug)

    context = {
        'group' : group,
        }
    context.update(extra_context)
    return context

@render_to('svmain/group_admin_members.html', mimetype=None)
def group_admin_members(request, slug, extra_context={}):
    group = get_object_or_404(auth_models.Group, name=slug)
    members = group.user_set.all()

    context = {
        'group' : group,
        'members' : members,
        }
    context.update(extra_context)
    return context

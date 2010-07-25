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

    # If using a non-Savane groups base, prepare membership metadata
    user_pks = svmain_models.Membership.objects.filter(group=group).values_list('user__pk', flat=True)
    missing_members = group.user_set.exclude(pk__in=user_pks)
    for member in missing_members:
        svmain_models.Membership(user=member, group=group, admin_flags='A').save()

    # If a membership does not have a matching User<->Group relationship, remove it
    user_pks = group.user_set.values_list('pk', flat=True)
    invalid_memberships = svmain_models.Membership.objects.exclude(user__in=user_pks).exclude(admin_flags='P')
    invalid_memberships.delete()


    memberships = svmain_models.Membership.objects.filter(group=group).exclude(admin_flags='P')
    pending_memberships = svmain_models.Membership.objects.filter(group=group, admin_flags='P')


    if request.method == 'POST':
        for membership in memberships:
            if request.user != membership.user: # don't unadmin or remove myself
                # admin / unadmin 
                if request.POST.get('admin_%d' % membership.pk, None):
                    if membership.admin_flags != 'A':
                        membership.admin_flags = 'A'
                        membership.save()
                        messages.success(request, "permissions of %s updated." % membership.user)
                else:
                    if membership.admin_flags != '':
                        membership.admin_flags = ''
                        membership.save()
                        messages.success(request, "permissions of %s updated." % membership.user)
                # remove members
                if request.POST.get('remove_%d' % membership.pk, None):
                    group.user_set.remove(membership.user)
                    membership.delete()
                    messages.success(request, "User %s deleted from the project." % membership.user)
        # approve pending membership
        for membership in pending_memberships:
            if request.POST.get('approve_%d' % membership.pk, None):
                group.user_set.add(membership.user)
                membership.admin_flags = ''
                membership.save()
                messages.success(request, "User %s added to the project." % membership.user)
        return HttpResponseRedirect('')  # reload


    context = {
        'group' : group,
        'memberships' : memberships,
        'pending_memberships' : pending_memberships,
        }
    context.update(extra_context)
    return context

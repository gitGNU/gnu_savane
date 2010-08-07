# View and manage users and groups
# Copyright (C) 2009, 2010  Sylvain Beucler
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

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
import django.contrib.auth.models as auth_models
from django.contrib import messages
from django.utils.text import capfirst
from django.utils.translation import ugettext as _, ungettext
import models as svmain_models
import forms as svmain_forms
from annoying.decorators import render_to

def user_redir(request, slug):
    u = get_object_or_404(auth_models.User, username=slug)
    return HttpResponseRedirect(reverse('savane.svmain.user_detail', args=(slug,)))

def group_redir(request, slug):
    g = get_object_or_404(auth_models.Group, name=slug)
    return HttpResponseRedirect(reverse('savane.svmain.group_detail', args=(slug,)))

##
# Main
##

def group_join(request, slug):
    g = get_object_or_404(auth_models.Group, name=slug)
    if svmain_models.Membership.objects.filter(user=request.user, group=g).count():
        messages.error(request, _("Request for inclusion already registered"))
    else:
        svmain_models.Membership(user=request.user, group=g, admin_flags='P').save()
        # TODO: send e-mail notification to group admins
        messages.success(request, _("Request for inclusion sent to project administrators"))
    return HttpResponseRedirect('../')

@render_to('svmain/group_gpgkeyring.html')
def group_gpgkeyring(request, slug, extra_context={}):
    """
    Generate temporary keyring and display it
    """
    group = get_object_or_404(auth_models.Group, name=slug)

    import os, sys, tempfile, shutil, glob
    from pyme import core, constants
    # Don't be fooled by the library-like look of pyme - internaly it
    # just invokes command-line 'gpg'.  There's no "gpg library".
    tdir = tempfile.mkdtemp()
    core.set_engine_info(constants.PROTOCOL_OpenPGP, None, tdir)
    c = core.Context()

    for user in group.user_set.all():
        status = c.op_import(core.Data(str(user.svuserinfo.gpg_key)))
        result = c.op_import_result()

    # Page display:
    # gpg --homedir /tmp/t --batch --quiet --no-tty --no-options \
    #   --no-default-keyring --list-keys  --display-charset=utf-8 \
    #   --keyring `pwd`/out
    import subprocess
    args = ['gpg', '--homedir', tdir,
            '--batch', '--quiet', '--no-tty', '--no-options',
            '--no-default-keyring', '--list-keys', '--display-charset=utf-8']
    out_err = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    out = out_err[0]
    # Remove filename (first 2 lines):
    gpgkeyring = "\n".join(out.split("\n")[2:])

    shutil.rmtree(tdir)


    context = {
        'gpgkeyring': gpgkeyring,
        'group' : group,
        }
    context.update(extra_context)
    return context

def group_gpgkeyring_download(request, slug):
    """
    Generate a GPG binary keyring
    """
    group = get_object_or_404(auth_models.Group, name=slug)

    import os, sys, tempfile, shutil, glob
    from pyme import core, constants
    # Don't be fooled by the library-like look of pyme - internaly it
    # just invokes command-line 'gpg'.  There's no "gpg library".
    tdir = tempfile.mkdtemp()
    core.set_engine_info(constants.PROTOCOL_OpenPGP, None, tdir)
    c = core.Context()

    for user in group.user_set.all():
        status = c.op_import(core.Data(str(user.svuserinfo.gpg_key)))
        result = c.op_import_result()

    data_export = core.Data()
    c.op_export(None, 0, data_export)
    data_export.seek(0, os.SEEK_SET)
    keyring_txt = data_export.read()

    response = HttpResponse()
    response = HttpResponse(mimetype='application/pgp-keys')
    response['Content-Disposition'] = 'attachment; filename=%s-keyring.gpg' % group.name
    response['Content-Description'] = _("GPG Keyring of the project %s") % group.name

    response.write(keyring_txt)

    shutil.rmtree(tdir)

    return response

@render_to('svmain/group_admin.html', mimetype=None)
def group_admin(request, slug, extra_context={}):
    group = get_object_or_404(auth_models.Group, name=slug)

    context = {
        'group' : group,
        }
    context.update(extra_context)
    return context

@render_to("svmain/group_admin_info.html", mimetype=None)
def group_admin_info(request, slug, extra_context={}, post_save_redirect=None):
    group = get_object_or_404(auth_models.Group, name=slug)
    object = group.svgroupinfo

    form_class = svmain_forms.GroupInfoForm

    if request.method == 'POST': # If the form has been submitted...
        form = form_class(request.POST, instance=object) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data
            object = form.save()
            messages.success(request, _("%s saved.") % capfirst(object._meta.verbose_name))
            if post_save_redirect is None:
                post_save_redirect = object.get_absolute_url()
            return HttpResponseRedirect(post_save_redirect) # Redirect after POST
    else:
        form = form_class(instance=object) # An unbound form

    context = {
        'group' : group,
        'form' : form,
        }
    context.update(extra_context)
    return context

@render_to("svmain/group_admin_features.html", mimetype=None)
def group_admin_features(request, slug, extra_context={}, post_save_redirect=None):
    group = get_object_or_404(auth_models.Group, name=slug)
    object = group.svgroupinfo

    form_class = svmain_forms.GroupFeaturesForm

    if request.method == 'POST': # If the form has been submitted...
        form = form_class(request.POST, instance=object) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data
            object = form.save()
            messages.success(request, _("%s saved.") % capfirst(object._meta.verbose_name))
            if post_save_redirect is None:
                post_save_redirect = object.get_absolute_url()
            return HttpResponseRedirect(post_save_redirect) # Redirect after POST
    else:
        form = form_class(instance=object) # An unbound form

    context = {
        'group' : group,
        'form' : form,
        }
    context.update(extra_context)
    return context
    

@render_to('svmain/group_admin_members.html', mimetype=None)
def group_admin_members(request, slug, extra_context={}):
    group = get_object_or_404(auth_models.Group, name=slug)
    svmain_models.Membership.tidy(group=group)

    memberships = svmain_models.Membership.objects.filter(group=group).exclude(admin_flags='P')
    pending_memberships = svmain_models.Membership.objects.filter(group=group, admin_flags='P')


    if request.method == 'POST':
        for membership in memberships:
            # Note: Membership's save() and delete() update the
            # matching User<->Group relationship.
            if request.user != membership.user: # don't unadmin or remove myself
                # admin / unadmin 
                if request.POST.get('admin_%d' % membership.pk, None):
                    if membership.admin_flags != 'A':
                        membership.admin_flags = 'A'
                        membership.save()
                        messages.success(request, _("Permissions of %s updated.") % membership.user.username)
                else:
                    if membership.admin_flags != '':
                        membership.admin_flags = ''
                        membership.save()
                        messages.success(request, _("Permissions of %s updated.") % membership.user.username)
                # remove members
                if request.POST.get('remove_%d' % membership.pk, None):
                    membership.delete()
                    messages.success(request, _("User %s deleted from the project.") % membership.user.username)
        # approve pending membership
        for membership in pending_memberships:
            if request.POST.get('approve_%d' % membership.pk, None):
                membership.admin_flags = ''
                membership.save()
                messages.success(request, _("User %s added to the project.") % membership.user.username)
            if request.POST.get('reject_%d' % membership.pk, None):
                membership.delete()
                messages.success(request, _("User %s deleted from the project.") % membership.user.username)
        return HttpResponseRedirect('')  # reload


    context = {
        'group' : group,
        'memberships' : memberships,
        'pending_memberships' : pending_memberships,
        }
    context.update(extra_context)
    return context

def group_admin_members_add(request, slug, extra_context={}):
    group = get_object_or_404(auth_models.Group, name=slug)

    if request.method == "POST":
        user = get_object_or_404(auth_models.User, pk=int(request.POST['user_id']))
        svmain_models.Membership(user=user, group=group, admin_flags='').save()
        messages.success(request, _("User %s added to the project.") % user.username)
        return HttpResponseRedirect('../')

    from django.views.generic.list_detail import object_list
    from savane.filters import search
    from django.contrib.auth.admin import UserAdmin
    context = {}
    context.update(extra_context)
    context.update({'group' : group})
    queryset = auth_models.User.objects.filter(is_active=True).exclude(pk__in=group.user_set.all())
    return search(object_list)(request,
                               queryset=queryset,
                               paginate_by=20,
                               model_admin=UserAdmin,
                               extra_context=context,
                               template_name='svmain/group_admin_members_add.html')

##
# Mailing lists
##

def group_mailinglist(request, slug, extra_context={}):
    group = get_object_or_404(auth_models.Group, name=slug)

    from django.views.generic.list_detail import object_list
    context = {}
    context.update(extra_context)
    context.update({'group' : group})
    queryset = svmain_models.MailingList.objects.filter(group=group).exclude(status=0)
    return object_list(request,
                       queryset=queryset,
                       extra_context=context,
                       template_name='svmain/group_mailinglist.html')

# Jobs
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

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import capfirst
from django.utils.translation import ugettext as _, ungettext
from django.db import models
import django.contrib.auth.models as auth_models
from annoying.decorators import render_to
from savane.middleware.exception import HttpAppException
import savane.svmain.models as svmain_models
import models as svpeople_models
import forms as svpeople_forms

@render_to('svpeople/index.html', mimetype=None)
def index(request, extra_context={}):
    category_list = svpeople_models.Category.objects.all()
    type_list = svmain_models.GroupConfiguration.objects.all()
    type_and_count = [ {'type' : t,
                        'count' : svpeople_models.Job.open_objects \
                            .filter(group__svgroupinfo__type=t).count() }
                       for t in type_list ]
    context = { 'category_list' : category_list,
                'type_and_count' : type_and_count,
                }
    context.update(extra_context)
    return context

@render_to('svpeople/job_list_by_category.html', mimetype=None)
def job_list_by_category(request, category_id, extra_context={}):
    category = get_object_or_404(svpeople_models.Category, pk=category_id)
    object_list = svpeople_models.Job.open_objects \
        .filter(category=category).order_by('-date') \
        .select_related('category', 'group__svgroupinfo__type')
        # select_related() gets all fields, it doesn't work at the field level (e.g. category__name)
        # only() does not work on related objects as of 1.2 :/
        #.only('title', 'category__label', 'date', 'group__svgroupinfo__full_name', 'group__svgroupinfo__type__name')
    context = {
        'category' : category,
        'object_list' : object_list,
        }
    context.update(extra_context)
    return context

@render_to('svpeople/job_list_by_type.html', mimetype=None)
def job_list_by_type(request, type_id, extra_context={}):
    type = get_object_or_404(svmain_models.GroupConfiguration, pk=type_id)
    object_list = svpeople_models.Job.open_objects \
        .filter(group__svgroupinfo__type=type).order_by('category', 'group__name') \
        .select_related('category', 'group__svgroupinfo__type')
    context = {
        'type' : type,
        'object_list' : object_list,
        }
    context.update(extra_context)
    return context

@render_to('svpeople/job_list_by_group.html', mimetype=None)
def job_list_by_group(request, slug, extra_context={}):
    group = get_object_or_404(auth_models.Group, name=slug)
    object_list = svpeople_models.Job.open_objects \
        .filter(group=group).order_by('-date') \
        .select_related('category', 'group__svgroupinfo__type')
    context = {
        'type' : type,
        'object_list' : object_list,
        }
    context.update(extra_context)
    return context

@render_to('svpeople/job_form.html', mimetype=None)
def job_add(request, slug, extra_context={}, post_save_redirect=None):
    group = get_object_or_404(auth_models.Group, name=slug)

    form_class = svpeople_forms.JobForm

    if request.method == 'POST': # If the form has been submitted...
        form = form_class(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data
            object = form.save(commit=False)
            # Force 'created_by' and 'group'
            object.created_by = request.user
            object.group = group
            object.save()
            messages.success(request, _("%s saved.") % capfirst(object._meta.verbose_name))
            if post_save_redirect is None:
                #post_save_redirect = object.get_absolute_url()
                post_save_redirect = reverse('savane:svpeople:job_edit', args=(object.pk,))
            return HttpResponseRedirect(post_save_redirect) # Redirect after POST
    else:
        form = form_class()

    context = {
        'form' : form,
        }
    context.update(extra_context)
    return context

@render_to('svpeople/job_form.html', mimetype=None)
def job_update(request, object_id, extra_context={}, form_class=svpeople_forms.JobForm, post_save_redirect=None):
    object = get_object_or_404(svpeople_models.Job, id=object_id)
    group = object.group

    if request.user.is_anonymous() or not svmain_models.Membership.is_admin(request.user, group):
        raise HttpAppException(_("Permission denied"))

    #form_class = svpeople_forms.JobForm
    form_valid = False
    formset_valid = False

    if request.method == 'POST': # If the form has been submitted...
        form = form_class(request.POST, instance=object) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data
            object = form.save()
            messages.success(request, _("%s saved.") % capfirst(object._meta.verbose_name))
            form_valid = True
    else:
        form = form_class(instance=object) # An unbound form

    # Skills
    # TODO: translate skill_year and skill_level
    from django.forms.models import inlineformset_factory
    JobInventoryFormSet = inlineformset_factory(svpeople_models.Job, svpeople_models.JobInventory)
    if request.method == "POST":
        formset = JobInventoryFormSet(request.POST, request.FILES, instance=object)
        if formset.is_valid():
            formset.save()
            formset_valid = True
    else:
        formset = JobInventoryFormSet(instance=object)

    if form_valid and formset_valid:
        if post_save_redirect is None:
            post_save_redirect = object.get_absolute_url()
        return HttpResponseRedirect(post_save_redirect) # Redirect after POST

    context = {
        'form' : form,
        'formset' : formset,
        }
    context.update(extra_context)
    return context

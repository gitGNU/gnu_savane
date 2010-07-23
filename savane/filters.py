# -*- coding: utf-8 -*-
# 
# Copyright (C) 2010  Sylvain Beucler
# Copyright ??? Django team
#
# This file is part of Savane.
# 
# Savane is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# Savane is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django.db import models
import operator
from django.http import HttpResponse

# Copy/paste these:
#from django.contrib.admin.views.main import
#ALL_VAR, ORDER_VAR, ORDER_TYPE_VAR, PAGE_VAR,
#SEARCH_VAR, TO_FIELD_VAR, IS_POPUP_VAR, ERROR_FLAG
ALL_VAR = 'all'
ORDER_VAR = 'o'
ORDER_TYPE_VAR = 'ot'
PAGE_VAR = 'p'
SEARCH_VAR = 'q'
TO_FIELD_VAR = 't'
IS_POPUP_VAR = 'pop'
ERROR_FLAG = 'e'

class ChangeList:
    """
    Object to pass views configuration to (e.g.: search string, ordering...)
    -Draft-
    """
    def __init__(model_admin, request):
        self.query = request.GET.get(SEARCH_VAR, '')
        self.list_display = model_admin.list_display

def search(f):
    """
    Inspired by Django's admin interface, filter queryset based on GET
    parameters (contrib.admin.views.main.*_VAR):

    - o=N: order by ModelAdmin.display_fields[N]
    - ot=xxx: order type: 'asc' or 'desc'
    - q=xxx: plain text search on ModelAdmin.search_fields (^ -> istartswith, = -> iexact, @ -> search, each word ANDed)
    - everything else: name of a Q filter

    exceptions:
    - p=N: current page
    - all=: disable pagination
    - pop: popup
    - e: error
    - to: ? (related to making JS-friendly PK values?)

    additional exclusions:
    - page: used by django.views.generic.list_detail

    We could also try and deduce filters from the Model, or avoid
    using some declared parameters as Q filters, or find a better
    idea.
    """
    def _decorator(request, *args, **kwargs):
        qs = kwargs['queryset']
        model_admin = kwargs['model_admin']

        lookup_params = request.GET.copy()
        for i in (ALL_VAR, ORDER_VAR, ORDER_TYPE_VAR, SEARCH_VAR, IS_POPUP_VAR, 'page'):
            if lookup_params.has_key(i):
                del lookup_params[i]

        try:
            qs = qs.filter(**lookup_params)
        # Naked except! Because we don't have any other way of validating "params".
        # They might be invalid if the keyword arguments are incorrect, or if the
        # values are not in the correct type, so we might get FieldError, ValueError,
        # ValicationError, or ? from a custom field that raises yet something else 
        # when handed impossible data.
        except:
            return HttpResponse("Erreur: paramètres de recherche invalides.")
            #raise IncorrectLookupParameters

        # TODO: order - but maybe in another, separate filter?

        ##
        # Search string
        ##
        def construct_search(field_name):
            if field_name.startswith('^'):
                return "%s__istartswith" % field_name[1:]
            elif field_name.startswith('='):
                return "%s__iexact" % field_name[1:]
            elif field_name.startswith('@'):
                return "%s__search" % field_name[1:]
            else:
                return "%s__icontains" % field_name

        query = request.GET.get(SEARCH_VAR, '')
        search_fields = model_admin.search_fields
        if search_fields and query:
            for bit in query.split():
                or_queries = [models.Q(**{construct_search(str(field_name)): bit}) for field_name in search_fields]
                qs = qs.filter(reduce(operator.or_, or_queries))
            for field_name in search_fields:
                if '__' in field_name:
                    qs = qs.distinct()
                    break

        kwargs['queryset'] = qs

        # TODO: pass order params
        if not kwargs.has_key('extra_context'):
            kwargs['extra_context'] = {}
        kwargs['extra_context']['q'] = query

        # TODO: move in a clean-up decorator
        del kwargs['model_admin']
        return f(request, *args, **kwargs)
    return _decorator

# Permission restrictions to use as view decorators
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

import django.contrib.auth.models as auth_models
from django.shortcuts import get_object_or_404
from savane.middleware.exception import HttpAppException
import savane.svmain.models as svmain_models

def is_member(user, group):
    return group.user_set.filter(pk=user.pk).count() > 0

def is_admin(user, group):
    return (is_member(user, group)
            and svmain_models.Membership.objects
            .filter(user=user, group=group, admin_flags='A'))

def only_project_admin(f, error_msg="Permission Denied"):
    """
    Decorator to keep non-members out of project administration
    screens.  Identifies the current group using the 'slug' keyword
    parameter.
    """
    def _f(request, *args, **kwargs):
        group = get_object_or_404(auth_models.Group, name=kwargs['slug'])
        if request.user.is_anonymous() or not is_admin(request.user, group):
            raise HttpAppException(error_msg)
        return f(request, *args, **kwargs)
    return _f

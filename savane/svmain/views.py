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
import models as svmain_models

def group_redir(request, slug):
    eg = get_object_or_404(svmain_models.ExtendedGroup, name=slug)
    return HttpResponseRedirect(eg.get_absolute_url())

def user_redir(request, slug):
    ug = get_object_or_404(svmain_models.ExtendedUser, username=slug)
    return HttpResponseRedirect(ug.get_absolute_url())

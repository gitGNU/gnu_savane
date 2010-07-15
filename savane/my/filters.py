# Only select information related to the current user
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

def only_mine(f):
    """Filter a generic query_set to only display objets related to
    the current user"""
    def _fd(request, queryset, *args, **kwargs):
        user = request.user
        queryset = queryset.filter(user=user.id)
        return f(request, queryset, *args, **kwargs)
    return _fd

#def only_my_groups(f):
#    """
#    Filter groups that the current user is member of
#    """
#    def _fd(request, queryset, *args, **kwargs):
#        user = request.user
#        queryset = queryset.filter(extendeduser=user.id)
#        return f(request, queryset, *args, **kwargs)
#    return _fd

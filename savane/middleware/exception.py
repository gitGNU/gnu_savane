# Catch app-specific exception and display it to the user
# Copyright (C) 2009, 2010  Sylvain Beucler
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

from django.shortcuts import render_to_response
from django.template import RequestContext

class HttpAppException(Exception):
    pass

class HttpCatchAppExceptionMiddleware(object):
    def process_exception(self, request, exception):
        """
        Only catch our HttpAppException (and derivate classes)
        """
        if isinstance(exception, HttpAppException):
            return render_to_response('error.html',
                                      { 'error' : exception.message },
                                      context_instance=RequestContext(request))
        return None

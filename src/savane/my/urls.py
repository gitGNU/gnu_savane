# Accounts URLs
# Copyright (C) 2009  Sylvain Beucler
# Copyright (C) 2009  Jonathan Gonzalez V.
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

from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template
import views

@login_required
def direct_to_template__login_required(*args, **kwargs):
    return direct_to_template(*args, **kwargs)


urlpatterns = patterns ('',
  url(r'^$', direct_to_template__login_required,
      { 'template' : 'savane/my/index.html' },
      name='my.views.index'),
  url('^conf/$',
      views.sv_conf,
      ),
  url('^conf/resume_skill$',
      views.sv_resume_skill,
      ),
  url('^conf/ssh_gpg$',
      views.sv_ssh_gpg,
      ),
)

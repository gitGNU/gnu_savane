# Forms for users and groups
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


from django import forms
import models as svmain_models

class GroupInfoForm(forms.ModelForm):
    class Meta:
        model = svmain_models.SvGroupInfo
        fields = ('full_name', 'short_description', 'long_description', 'devel_status',)

class GroupFeaturesForm(forms.ModelForm):
    class Meta:
        model = svmain_models.SvGroupInfo
        fields = ('use_homepage', 'use_mail', 'use_news', 'use_download', 
                  'use_extralink_documentation',
                  'use_cvs', 'use_arch', 'use_svn', 'use_git', 'use_hg', 'use_bzr',
                  'use_bugs', 'use_support', 'use_patch', 'use_task',
                  
                  'url_homepage', 'url_mail', 'url_download', 'url_extralink_documentation',
                  'url_cvs', 'url_cvs_viewcvs', 'url_cvs_viewcvs_homepage',
                  'url_arch', 'url_arch_viewcvs',
                  'url_svn', 'url_svn_viewcvs',
                  'url_git', 'url_git_viewcvs',
                  'url_hg', 'url_hg_viewcvs',
                  'url_bzr', 'url_bzr_viewcvs',
                  'url_bugs', 'url_support', 'url_patch', 'url_task')

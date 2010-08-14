# Forms for jobs
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
import models as svpeople_models
from django.utils.translation import ugettext

class JobForm(forms.ModelForm):
    class Meta:
        model = svpeople_models.Job
        fields = ('category', 'status', 'title', 'description', )
    description = forms.CharField(widget=forms.Textarea(attrs={'cols':'70','rows':'15'}))

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        # Translate categories from database
        self.fields['category'].choices = \
            [ (k,ugettext(v)) for k,v in self.fields['category'].choices ]

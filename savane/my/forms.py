# Manage user attributes
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

from django import forms
from django.utils.translation import ugettext, ugettext_lazy as _
from savane.utils import *

class MailForm(forms.Form):
    email = forms.EmailField(required=True)

class IdentityForm(forms.Form):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    gpg_key = forms.CharField(widget=forms.Textarea(attrs={'cols':'70','rows':'15'}), required=False,
                              help_text=_("You can write down here your (ASCII) public key (gpg --export --armor keyid)"))

class SSHForm(forms.Form):
    key_file = forms.FileField(required=False, help_text=_("Be sure to upload the file ending with .pub"))
    key = forms.CharField(widget=forms.TextInput(attrs={'size':'60'}), required=False)

    def clean_key(self):
        ssh_key = self.cleaned_data['key']

        # String is not mandatory
        if len(ssh_key) == 0:
            return None

        try:
            ssh_key_fingerprint(ssh_key)
        except Exception as e:
            raise forms.ValidationError(_("The uploaded string is not a public key file: %s") % e)
        return ssh_key

    def clean_key_file(self):
        ssh_key_file = self.cleaned_data['key_file']

        # File is not mandatory
        if ssh_key_file is None:
            return None

        # Avoid large file attacks
        if ssh_key_file.size > 100*1024:
            return None

        ssh_key = ssh_key_file.read()
        try:
            ssh_key_fingerprint(ssh_key)
        except Exception as e:
            raise forms.ValidationError(_("The uploaded file is not a public key file: %s") % e)

        return ssh_key_file

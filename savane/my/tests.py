# Tests
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

from django.core import mail
from django.test import TestCase
from django.core.urlresolvers import reverse
import django.contrib.auth.models as auth_models
import re

class SimpleTest(TestCase):
    #fixtures = [
    #    'license.yaml',
    #    'developmentstatus.yaml',
    #    ]

    def test_010_conf_edit(self):
        """
        Sample form test
        """

        auth_models.User.objects.create_user(username='test', email='test@test.tld', password='test')
        self.assertTrue(self.client.login(username='test', password='test'))

        response = self.client.get(reverse('savane:my:conf'))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('savane:my:conf'),
                                    {'action': 'update_identity', 'name': 'Lambda', 'last_name': 'Visitor'})
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('savane:my:conf'),
                                    {'action': 'update_identity', 'name': '', 'last_name': 'Visitor'})
        self.assertFormError(response, 'form_identity', 'name', u'This field is required.')

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
import tempfile
from savane.utils import ssh_key_fingerprint

__test__ = {"doctest": """
>>> ssh_key_fingerprint("ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDbYV67YG54OX3/c7GNIG7zS1sSF3ddhCwhodEGpcbkQs4QOi7gcZHopyjBqvhyJB5fu76odOqI9KngW5IfpPX4lK/3kZZ8QISiF6nekB8wbi49hlB9K8j7NZ7rBTIsKApVNFqd4vriE9m7842soBOc6/sYSEemHxjA7+d+qbkV8j5wuo1QH0ynA5jPMI8RHhTtUBEZIJK2AFUB42bx2XFakhSh5K2DAfZyZ2dKeRkKRRbFzr0eAvbyCPKT93seWAFypETiomKbjMBRvMJyfpTcx4legzs9oGfeLHIb3V0oyM3ysXdqkwoOwO43qCcG/lDFvonzBGlDKh/T07kVXdLh")
'2048 6e:57:73:c6:92:16:62:b8:cc:ed:01:3f:17:95:24:51 (RSA)\n'
"""}

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

        # Contact info
        response = self.client.get(reverse('savane:my:conf'))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('savane:my:conf'),
                                    {'action': 'update_identity', 'first_name': 'Lambda', 'last_name': 'Visitor'})
        self.assertEqual(response.status_code, 302)

        response = self.client.post(reverse('savane:my:conf'),
                                    {'action': 'update_identity', 'first_name': '', 'last_name': 'Visitor'})
        self.assertFormError(response, 'form_identity', 'first_name', u'This field is required.')

        # SSH keys
        # - string
        response = self.client.get(reverse('savane:my:ssh'))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('savane:my:ssh'),
                                    {'key': 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDbYV67YG54OX3/c7GNIG7zS1sSF3ddhCwhodEGpcbkQs4QOi7gcZHopyjBqvhyJB5fu76odOqI9KngW5IfpPX4lK/3kZZ8QISiF6nekB8wbi49hlB9K8j7NZ7rBTIsKApVNFqd4vriE9m7842soBOc6/sYSEemHxjA7+d+qbkV8j5wuo1QH0ynA5jPMI8RHhTtUBEZIJK2AFUB42bx2XFakhSh5K2DAfZyZ2dKeRkKRRbFzr0eAvbyCPKT93seWAFypETiomKbjMBRvMJyfpTcx4legzs9oGfeLHIb3V0oyM3ysXdqkwoOwO43qCcG/lDFvonzBGlDKh/T07kVXdLh'})
        self.assertEqual(response.status_code, 302)
        response = self.client.post(reverse('savane:my:ssh'), {'key': 'ssh-rsa AAAABBM= me@myhost'})
        self.assertFormError(response, 'form', 'key', u'The uploaded string is not a public key file: '
                             + 'SSH error: is not a public key file.\n')

        # - file upload
        f = tempfile.TemporaryFile()
        f.write('ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDbYV67YG54OX3/c7GNIG7zS1sSF3ddhCwhodEGpcbkQs4QOi7gcZHopyjBqvhyJB5fu76odOqI9KngW5IfpPX4lK/3kZZ8QISiF6nekB8wbi49hlB9K8j7NZ7rBTIsKApVNFqd4vriE9m7842soBOc6/sYSEemHxjA7+d+qbkV8j5wuo1QH0ynA5jPMI8RHhTtUBEZIJK2AFUB42bx2XFakhSh5K2DAfZyZ2dKeRkKRRbFzr0eAvbyCPKT93seWAFypETiomKbjMBRvMJyfpTcx4legzs9oGfeLHIb3V0oyM3ysXdqkwoOwO43qCcG/lDFvonzBGlDKh/T07kVXdLh')
        f.flush()
        f.seek(0)
        response = self.client.post(reverse('savane:my:ssh'), {'key_file': f})
        self.assertEqual(response.status_code, 302)

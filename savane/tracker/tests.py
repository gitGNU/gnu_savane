"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from django.core.urlresolvers import reverse

class SimpleTest(TestCase):
    fixtures = [
        'tracker.yaml',
        'demo/item.yaml',
        ]

    def test_010_view_item(self):
        """
        Consult a tracker item
        """
        response = self.client.get(reverse('savane:tracker:item_detail', args=('bugs', 1)))
        self.assertEqual(response.status_code, 200)
        print response.content

# Utility functions for savane
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

import os, tempfile
import random
import time
import re
import subprocess
from django.utils.translation import ugettext as _

def ssh_key_fingerprint(ssh_key):
    """
    Check if the public key is valid using command-line 'ssh-keygen'
    """
    tmp_file = tempfile.NamedTemporaryFile()  # auto-removed
    tmp_file.write(ssh_key)
    tmp_file.flush()

    args = ['ssh-keygen', '-l', '-f', tmp_file.name]
    try:
        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError:
        # Error running ssh-keygen, probably not installed
        return 'Failed to run ssh-keygen, contact the site administrator'
    out_err = process.communicate()
    out = out_err[0]

    if process.returncode != 0:
        raise Exception(_("SSH error: %s") % out.replace(tmp_file.name+' ', ''))

    return out.replace(tmp_file.name+' ', '')

from django.contrib.sites.models import Site, RequestSite
def get_site_name():
    """
    Return the site name, used in various templates
    """
    if Site._meta.installed:
        site_name = Site.objects.get_current().name
    else:
        site_name = 'Savane'
    return site_name

# http://wiki.python.org/moin/EscapingHtml
import re
from htmlentitydefs import name2codepoint
# doesn't handle stuff like '&#039;'
def htmlentitydecode(s):
    return re.sub('&(%s);' % '|'.join(name2codepoint),
            lambda m: unichr(name2codepoint[m.group(1)]), s)
import htmllib
def unescape(s):
    p = htmllib.HTMLParser(None)
    p.save_bgn()
    p.feed(s)
    return p.save_end()

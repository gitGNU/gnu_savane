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

import os
from subprocess import Popen, PIPE

def ssh_key_fingerprint( ssh_key ):
    if ssh_key is None or len(ssh_key) == 0:
        return None

    file_name = '/tmp/%d' % random.randint(0, int(time.time()))

    tmp_file = open( file_name, 'wb+' )
    tmp_file.write( ssh_key )
    tmp_file.close()

    cmd = 'ssh-keygen -l -f %s' % file_name
    pipe = Popen( cmd, shell=True, stdout=PIPE).stdout
    res = re.search("not a public key file", pipe.readline())
    if res is not None:
        raise forms.ValidationError( "The uploaded string is not a public key file" )

    return ssh_key


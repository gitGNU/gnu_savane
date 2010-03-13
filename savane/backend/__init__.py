# Run a subcommand specified on the command line
# Copyright (C) 2009  Sylvain Beucler
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

import os, sys
import imp

def wrapper():
    """
    Load python savane.backend submodule specified on the first
    argument of the command line
    """
    if len(sys.argv) == 1:
        print "Usage: %s command" % sys.argv[0]
        sys.exit(1)
    command_name = sys.argv[1]
    (f, path, descr) = imp.find_module(command_name, __path__)
    imp.load_module(command_name, f, path, descr)

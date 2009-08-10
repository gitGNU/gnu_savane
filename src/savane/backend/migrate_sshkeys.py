# Migrate users' SSH keys from old Savane to new Savane
# Copyright (C) 2009  Jonathan Gonzalez
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

# Moves the keys stored at users.authorized_keys to a new table user.sshkeys


from savane.svmain.models import ExtendedUser, SshKey

sv_users = ExtendedUser.objects.all().exclude(authorized_keys='')
for sv_user in sv_users:
    keys = (sv_user.authorized_keys or '').split('###')
    sv_user.sshkey_set.all().delete()
    remove = False
    for key in keys:
        if len(key) > 0:
            try:
                ssh_key = SshKey(ssh_key=key)
                sv_user.sshkey_set.add(ssh_key)
                remove = True
            except:
                print "User: %s Failed" % sv_user.username

    if remove:
        sv_user.authorized_keys = ''
        sv_user.save()



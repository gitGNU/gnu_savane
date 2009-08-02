# Replicate users and groups to an OpenLDAP directory
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

# Recommended indexes:
# index		uid,sn,uidNumber,gidNumber,memberUid,shadowExpire eq

# TODO: most settings are hard-coded and need to be made configurable
# - base: dc=savannah,dc=gnu,dc=org
# - users ou: "users"
# - groups ou: "groups"
# - create 'organization' and 'organizationalUnit' objects?
# - min uid: 1000
# - min gid: 1000
# - default group: cn=svusers / gid=1000

import sys
import codecs
import base64, binascii
import savane.svmain.models as svmain_models

# Convert stdout to UTF-8 - if the stdout is redirected to a file
# sys.stdout.encoding is autodetected as 'None' and you get the
# obnoxious UnicodeEncodeError python error.
sys.stdout = codecs.getwriter('UTF-8')(sys.stdout)

print """dn: dc=savannah,dc=gnu,dc=org
objectClass: top
objectClass: dcObject
objectClass: organization
o: GNU
dc: savannah
structuralObjectClass: organization

dn: ou=users,dc=savannah,dc=gnu,dc=org
ou: users
objectClass: organizationalUnit
objectClass: top
structuralObjectClass: organizationalUnit

dn: ou=groups,dc=savannah,dc=gnu,dc=org
ou: groups
objectClass: organizationalUnit
objectClass: top
structuralObjectClass: organizationalUnit
"""

# Add user admin/admin
# (REMOVE WHEN TESTING IS DONE!)
print """
dn: cn=admin,dc=savannah,dc=gnu,dc=org
objectClass: simpleSecurityObject
objectClass: organizationalRole
cn: admin
description: LDAP administrator
userPassword:: e2NyeXB0fWt0YVZ1TFNDaEg0Wi4=
structuralObjectClass: organizationalRole
"""

#count = svmain_models.ExtendedUser.objects.count()
#print str(count) + " users in the database."

uidNumber=1000
for user in svmain_models.ExtendedUser.objects.only('username', 'first_name', 'last_name', 'email',
                                                    'password', 'uidNumber', 'gidNumber'):
    uidNumber=uidNumber+1
    ##if uidNumber == 0: # either non-assigned, or mistakenly assigned to root
    #if uidNumber < 1000: # either non-assigned, or mistakenly assigned to privileged user
    #    uidn = UidNumber()
    #    uidn.save()
    #    user.uidNumber = uidn
    #    user.save()

    cleanup = [user.first_name, user.last_name, user.email]
    for i in range(0, len(cleanup)):
        cleanup[i] = cleanup[i].replace('\n', ' ')
        cleanup[i] = cleanup[i].replace('\r', ' ')
        cleanup[i] = cleanup[i].strip()
    (first_name, last_name, email) = cleanup

    ldap_password = '{CRYPT}!'  # default = unusable password
    if user.password.startswith('sha1$'):
        # Django-specific algorithm: it sums 5-char-salt+pass instead
        # of SSHA's pass+4-bytes-salt, so we can't store it in LDAP -
        # /me curses django devs
        pass
    elif user.password.startswith('md5$$'):
        # MD5 without salt
        algo, empty, hash_hex = user.password.split('$')
        if (len(hash_hex) == 32): # filter out empty or disabled passwords
            ldap_password = "{MD5}" + base64.b64encode(binascii.a2b_hex(hash_hex))
    elif user.password.startswith('md5$'):
        # md5$salt$ vs. {SMD5} is similar to sha1$salt$ vs. {SSHA} -
        # cf. above
        pass
    elif user.password.startswith('crypt$'):
        # glibc crypt has improved algorithms, but where salt contains
        # three '$'s, which Django doesn't support (since '$' is
        # already the salt field separator). So this is only weak,
        # passwd-style (not shadow-style) crypt.
        algo, salt_hex, hash_hex = user.password.split('$')
        # salt_hex is 2-chars long and already prepended to hash_hex
        ldap_password = "{CRYPT}" + base64.b64encode(binascii.a2b_hex(hash_hex))
    elif '$' not in user.password:
        # MD5 without salt, alternate Django syntax
        hash_hex = user.password
        if (len(hash_hex) == 32): # filter out empty or disabled passwords
            ldap_password = "{MD5}" + base64.b64encode(binascii.a2b_hex(hash_hex))

    # Object classes:
    # - posixAccount: base class for libnss-ldap/pam-ldap support
    # - shadowAccount: for shadowExpire
    # - inetOrgPerson: for mail and givenName, and structural class
    print u"""
dn: uidNumber=%(uidNumber)d,ou=users,dc=savannah,dc=gnu,dc=org
uid: %(username)s
cn:: %(full_name)s
sn:: %(last_name)s
mail: %(email)s
userPassword: %(ldap_password)s
uidNumber: %(uidNumber)d
gidNumber: %(gidNumber)d
homeDirectory: %(homedir)s
objectClass: shadowAccount
objectClass: posixAccount
objectClass: inetOrgPerson
objectClass: top
structuralObjectClass: inetOrgPerson""" % {
        'username' : user.username,
        'full_name' : base64.b64encode((first_name + u' ' + last_name).encode('UTF-8')),
        'last_name' : base64.b64encode((last_name or u'-').encode('UTF-8')),
        'email' : email,
        'ldap_password' : ldap_password,
        'uidNumber' : uidNumber,
        'gidNumber' : 1000,
        'homedir' : u'/home/' + user.username[:1] + u'/' + user.username[:2] + u'/' + user.username,
        }
    # non-mandatory fields - slapadd doesn't accept empty fields apparently
    if len(first_name) > 0:
        print "givenName::" + base64.b64encode(first_name.encode('UTF-8'))
    # disallow login for users that are not part of any group
    #if user.extendedgroup_set.count() == 0:
    #    print "shadowExpire: 10" # timestamp - avoid 0 as it may be
    #                             # interpreted at 'no expiration'

print u"""
dn: cn=svusers,ou=groups,dc=savannah,dc=gnu,dc=org
cn: svusers
gidNumber: 1000
objectClass: posixGroup
objectClass: top
structuralObjectClass: posixGroup"""
i=1000
for group in svmain_models.ExtendedGroup.objects.only('name'):
    i=i+1
    print u"""
dn: cn=%(name)s,ou=groups,dc=savannah,dc=gnu,dc=org
cn: %(name)s
gidNumber: %(gidNumber)s
objectClass: posixGroup
objectClass: top
structuralObjectClass: posixGroup""" % {
     'name' : group.name,
     'gidNumber' : i,
     }
    for user in group.extendeduser_set.only('username'):
        print "memberUid: " + user.username

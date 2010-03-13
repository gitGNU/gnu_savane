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
# index		uid,uidNumber,gidNumber,memberUid,shadowExpire eq

# TODO: most settings are hard-coded and need to be made configurable
# - base: dc=savannah,dc=gnu,dc=org
# - users ou: "users"
# - groups ou: "groups"
# - create 'organization' and 'organizationalUnit' objects?
# - min uid: 1000
# - min gid: 1000
# - default group: cn=svusers / gid=1000
# - loginShell: /usr/local/bin/sv_membersh
# - homedir: 2-level /home/u/us/username

import sys
import codecs
import base64, binascii
from django.db import connection, models
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

import MySQLdb, settings
MySQLdb.charset = 'UTF-8'
conn = MySQLdb.connect(user=settings.DATABASE_USER,
                       passwd=settings.DATABASE_PASSWORD,
                       db=settings.DATABASE_NAME,
                       use_unicode=True)

# Alternatively:
#from django.db import connection
#connection.cursor() # establish connection - well looks like it does
#conn = connection.connection # MySQL-specific connection - now using mysqldb


##
# Users
##

max_uid = svmain_models.ExtendedUser.objects.all().aggregate(models.Max('uidNumber'))['uidNumber__max']
if max_uid < 1000: max_uid = 1000

users_with_group = {}
group_users = {}
svmain_models.Membership.query_active_memberships_raw(conn, ('group_id', 'username'))
res = conn.store_result()
for row in res.fetch_row(maxrows=0, how=1):
    users_with_group[row['username']] = 1
    if group_users.has_key(row['group_id']):
        group_users[row['group_id']].append(row['username'])
    else:
        group_users[row['group_id']] = [row['username'],]

user_saves = []
svmain_models.ExtendedUser.query_active_users_raw(conn, ('username', 'first_name', 'last_name', 'email',
                                                         'password', 'uidNumber', 'gidNumber'))
res = conn.store_result()
for row in res.fetch_row(maxrows=0):
    (username, first_name, last_name, email, password, uidNumber, gidNumber) = row

    #if uidNumber == 0: # either non-assigned, or mistakenly assigned to root
    if uidNumber < 1000: # either non-assigned, or mistakenly assigned to privileged user
        max_uid = max_uid + 1
        user_saves.append((username, max_uid))
        uidNumber = max_uid

    cleanup = [first_name, last_name, email]
    for i in range(0, len(cleanup)):
        cleanup[i] = cleanup[i].replace('\n', ' ')
        cleanup[i] = cleanup[i].replace('\r', ' ')
        cleanup[i] = cleanup[i].strip()
    (first_name, last_name, email) = cleanup

    ldap_password = '{CRYPT}!'  # default = unusable password
    if users_with_group.has_key(username):
        if password.startswith('sha1$'):
            # Django-specific algorithm: it sums 5-char-salt+pass instead
            # of SSHA's pass+4-bytes-salt, so we can't store it in LDAP -
            # /me curses django devs
            pass
        elif password.startswith('md5$$'):
            # MD5 without salt
            algo, empty, hash_hex = password.split('$')
            if (len(hash_hex) == 32): # filter out empty or disabled passwords
                ldap_password = "{MD5}" + base64.b64encode(binascii.a2b_hex(hash_hex))
        elif password.startswith('md5$'):
            # md5$salt$ vs. {SMD5} is similar to sha1$salt$ vs. {SSHA} -
            # cf. above
            pass
        elif password.startswith('crypt$'):
            # glibc crypt has improved algorithms, but where salt contains
            # three '$'s, which Django doesn't support (since '$' is
            # already the salt field separator). So this is only weak,
            # passwd-style (not shadow-style) crypt.
            algo, salt_hex, hash_hex = password.split('$')
            # salt_hex is 2-chars long and already prepended to hash_hex
            ldap_password = "{CRYPT}" + base64.b64encode(binascii.a2b_hex(hash_hex))
        elif '$' not in password:
            # MD5 without salt, alternate Django syntax
            hash_hex = password
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
loginShell: /usr/local/bin/sv_membersh
objectClass: shadowAccount
objectClass: posixAccount
objectClass: inetOrgPerson
objectClass: top
structuralObjectClass: inetOrgPerson""" % {
        'username' : username,
        'full_name' : base64.b64encode((first_name + ' ' + last_name).encode('UTF-8')),
        'last_name' : base64.b64encode((last_name or '-').encode('UTF-8')),
        'email' : email,
        'ldap_password' : ldap_password,
        'uidNumber' : uidNumber,
        'gidNumber' : 1000,
        'homedir' : '/home/' + username[:1] + '/' + username[:2] + '/' + username,
        }
    # non-mandatory fields - slapadd doesn't accept empty fields apparently
    if len(first_name) > 0:
        print "givenName::" + base64.b64encode(first_name.encode('UTF-8'))
    # disallow login for users that are not part of any group
    if not users_with_group.has_key(username):
        # shadowExpire is a timestamp - avoid 0 as it may be
        # interpreted as 'no expiration'
        print "shadowExpire: 10"

##
# Groups
##

max_gid = svmain_models.ExtendedGroup.objects.all().aggregate(models.Max('gidNumber'))['gidNumber__max']
if max_gid < 1000: max_gid = 1000

# Create base 'svusers' group
print u"""
dn: cn=svusers,ou=groups,dc=savannah,dc=gnu,dc=org
cn: svusers
gidNumber: 1000
objectClass: posixGroup
objectClass: top
structuralObjectClass: posixGroup"""

# Dump groups
group_saves = []
svmain_models.ExtendedGroup.query_active_groups_raw(conn, ('group_ptr_id', 'name', 'gidNumber'))
res = conn.store_result()
#for group in svmain_models.ExtendedGroup.objects.only('name'):
for row in res.fetch_row(maxrows=0):
    (group_id, name, gidNumber) = row

    if gidNumber < 1000: # either non-assigned, or mistakenly assigned to privileged user
        max_gid = max_gid + 1
        group_saves.append((group_id, max_gid))
        gidNumber = max_gid

    print u"""
dn: cn=%(name)s,ou=groups,dc=savannah,dc=gnu,dc=org
cn: %(name)s
gidNumber: %(gidNumber)s
objectClass: posixGroup
objectClass: top
structuralObjectClass: posixGroup""" % {
     'name' : name,
     'gidNumber' : gidNumber,
     }
    if group_users.has_key(group_id):
        for username in group_users[group_id]:
            print "memberUid: " + username

# TODO
# - user_saves
# - group_saves
# with multi-line UPDATEs

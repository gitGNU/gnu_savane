#!/usr/bin/env python
import sys, os

# For security, do not place this file in the directory that contains
# your settings.py: it would allow an attacker to get it.
 
# Add a custom Python path.
#sys.path.insert(0, "/var/www/myproject")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Switch to the directory of your project. (Optional.)
# os.chdir("/home/user/myproject")

# Set the DJANGO_SETTINGS_MODULE environment variable.
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
 
from django.core.servers.fastcgi import runfastcgi
runfastcgi(method="threaded", daemonize="false")

# Apparently the service needs to be installed at '/'

# Your .fcgi needs to reside in suexec-docroot (compile-time
# constant), which is '/var/www' for Debian GNU/Linux

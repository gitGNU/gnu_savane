import sys

# The problem:

# Django (./manage.py) is confused if the code is in a directory
# called 'savane', because it adds that directory (e.g. '..') to the
# path, and our code also contains a 'savane' subdirectory:

# savane/
# savane/.git
# savane/settings_default.py
# savane/settings.py
# savane/...
# savane/savane/  <-- we're here
# savane/savane/svmain/

# Solutions:

# We either need the user to rename the directory that contains the
# code, or rename our own 'savane' subdirectory, or place it somewhere
# else.

# It doesn't make sense to rename our subdirectory because it's meant
# to be added to the Python path and hence it needs to be named after
# our project (or, maybe we could rename it to 'savane4').

# We could put everything in a subdirectory (such as 'src') and add it
# to the Python path in (the top-level) settings.py, but it's less
# convenient to work with.

# For now we'll just display instructions for the first solution to
# the user.

print """
Your working directory is called 'savane', which confuses the Django framework.
Please rename your working directory to 'savane-forge' for example.
"""
sys.exit(1)

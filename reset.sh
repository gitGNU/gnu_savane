#!/bin/bash
mysql -e 'DROP DATABASE savane';
mysql -e 'CREATE DATABASE savane DEFAULT CHARSET utf8';
./manage.py syncdb --noinput
./manage.py loaddata savane/*/fixtures/*.yaml
./manage.py loaddata savane/svmain/fixtures/demo/*.yaml

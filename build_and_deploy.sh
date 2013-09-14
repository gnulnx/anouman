#!/usr/bin/env bash

source buildenv/bin/activate
rm -rf buildenv/lib/python2.7/site-packages/Dnginx-0.1-py2.7.egg-info/
rm -rf dist

rm -rf B/anouman-admin.py  A/Dnginx-0.1-py2.7.egg-info/  dist

python setup.py sdist
pip install dist/anouman-0.1.tar.gz

ls /Users/jfurr/blank/lib/python2.7/site-packages/anouman/templates/

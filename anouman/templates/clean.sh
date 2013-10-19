#!/usr/bin/env bash

# This file cleans up a server for a fresh anouman install
# Set the domain name of the project here
DOMAINNAME={{DOMAINNAME}}

# Echo Clean up NGINX sites enabled
# TODO  Shouldn't we store these locally in our package directory and then just create the symbolic
# link back to the sites-enabled for nginx?  If you are worried about conforming then just create a
# symlink in sites-available to.
sudo rm -rf /etc/nginx/sites-enabled/nginx.$DOMAINNAME.conf  /etc/nginx/sites-available/nginx.$DOMAINNAME.conf

# Remove anouman
/usr/bin/yes | sudo pip uninstall anouman

# Remove all traces of virtualenv
sudo rm -rf /home/anouman/*
sudo rm -rf /home/anouman/.virtualenvs/

# Remove the .bash_profile
# Make sure this test never runs on the clients machine!
rm -rf /home/anouman/.bash_profile


# Remove the site upstart command
sudo rm -rf /etc/init/site1.com.conf

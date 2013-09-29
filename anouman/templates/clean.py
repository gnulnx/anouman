#!/usr/bin/env python
import os
from django.template import Template, Context
from django.conf import settings

## When you initially did this you were only using django templates
## and this was not a full django project.  You can only call this
## once so you put in a few files to make sure it was called...
try: settings.configure()
except: pass

"""
    Render the clean.sh file used to clean VM between vagrant runs
"""

context = {
    'DOMAINNAME':'site1.com',
}

templ="""#!/usr/bin/env bash

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
sudo rm -rf /etc/init/site1.com.conf"""

def render(c={}):
    """
        Pass in a context our the defaults above will be used
    """
    context.update(c)

    t = Template( templ )
    c = Context( context )
    return t.render( c )

def save(path="./clean.sh", **kwargs):
    c = kwargs.get('context', context)
    with open(path, 'w') as f:
        f.write(render(c))


if __name__ == '__main__':
    pass

#!/usr/bin/env python
import os
from django.template import Template, Context
from django.conf import settings

## When you initially did this you were only using django templates
## and this was not a full django project.  You can only call this
## once so you put it in a few files to make sure it was called...
try: settings.configure()
except: pass

"""
    Render the basic bootstrap.sh file for use with Vagrant
"""

context = {
    'NGINX':True,
    'MYSQL':False,
}

templ="""#!/usr/bin/env bash
# Setup anouman user
sudo useradd --shell /bin/bash --home /home/anouman anouman
echo -e "anouman\\nanouman\\n" | sudo passwd anouman
sudo usermod --groups admin anouman

sudo apt-get update                         # Update apt-get
sudo apt-get install -yf vim                # VIM because VI isn't as cool
sudo apt-get install -yf git                # install git

### PYTHON STUFF
sudo apt-get install -yf python-setuptools
sudo apt-get install -yf python-virtualenv
sudo apt-get install -yf python-dev
sudo apt-get install -yf build-essential

{% if NGINX %}
sudo apt-get install -yf nginx              # install nginx
{% endif %}

{% if MYSQL %}
sudo apt-get install -yf mysql-client       # only install mysql command line client
sudo apt-get install -yf libmysqlclient-dev # needed for django mysql integration
{% endif %}
"""

def render(c={}):
    """
        Pass in a context our the defaults above will be used
    """
    context.update(c)

    t = Template( templ )
    c = Context( context )
    return t.render( c )

def save(path="./bootstrap.sh", **kwargs):
    c = kwargs.get('context', context)
    with open(path, 'w') as f:
        f.write(render(c))


if __name__ == '__main__':
    pass

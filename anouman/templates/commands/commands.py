#!/usr/bin/env python
from django.template import Template, Context
import os

commands = """
#This section defined commands specified by Anouman

NGINX=/etc/init.d/nginx
DOMAINNAME={{DOMAINNAME}}

function site {
        if [ $1 == 'status' ];
        then
                sudo $NGINX status
                sudo status $DOMAINNAME
        fi

        if [ $1 == 'stop' ];
        then
                sudo $NGINX stop
                sudo stop $DOMAINNAME
        fi

        if [ $1 == 'start' ];
        then
                sudo $NGINX start
                sudo start $DOMAINNAME
        fi

        if [ $1 == 'reload' ];
        then
                sudo nginx -s reload
        fi
}"""

context = {
    'DOMAINNAME':'',
}


def get_commands(context=context):
    t = Template( commands )
    c = Context( context )
    return t.render(c)




#!/usr/bin/env python

shell_commands_expected="""
#This section defines commands specified by Anouman

NGINX=/etc/init.d/nginx
DOMAINNAME=example.com

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

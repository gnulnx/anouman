#!/usr/bin/env python
import os 
import argparse

from anouman.project_setup.setup import (
    package_django_project,
    deploy_django_project,
    build_vm,
) 

descr="""
    anouman is a django 1.4+ deployment simplifier.

    You provide anouman a django project and anouman provides
    you a fully deployable anouman package (aka tarball)
    
    NOTE:  anouman
    Currently we can deploy project based on django 1.4 and up.
"""

def get_args():
    parser = argparse.ArgumentParser(
        description=descr
    )
    
    parser.add_argument('--vm',
        help='Create a virtual machine.  Pass it the VM name',
        dest='vm',
        default="",
    )

    parser.add_argument('--domainname',
        help='Enter the domain name of your website',
        dest='domainname',
        default="www.example.com",
    )

    parser.add_argument('--startproject',
        help='Start a new django project with default option nginx/gunicorn',
        dest='project_name',
        default=False,
    )

    parser.add_argument('--django-version',
        help='Set the django version.  Default to latest version pip repo.  (ex:  ==1.5.1) note the ==',
        dest='django_version',
        default='>=1.5, <=1.6',
    )
    
    parser.add_argument('--django-project',
        help='Create deployment for django project.  (Assumes one settings file and one wsgi file)',
        dest='django_project',
        default=False,
    )
    
    parser.add_argument('--settings',
        help='Specify path to settings.py',
        dest='settings',
        default=False,
    )

    parser.add_argument('--wsgi',
        help='Specify path to wsgi.py',
        dest='wsgi',
        default=False,
    )

    parser.add_argument('--manage',
        help='Specify the path to your projects manage.py scrpt',
        dest='manage',
        default=False,
    )

    parser.add_argument('--virtualenv',
        help='Set the virtualev directory.',
        dest='virtualenv',
        default='virtualenv',
    )
    
    parser.add_argument('--bind',
        help='Set the virtualev directory.',
        dest='bind',
        default=False, #ex:  10.0.1.13:8001
    )
    
    parser.add_argument('--gunicorn',
        help='use gunicorn as the django server',
        dest='gunicorn',
        action='store_true',
        default=True,
    )

    parser.add_argument('--deploy',
        help='deploy the project',
        dest='deploy',
        default=False,
    )
    
    parser.add_argument('--setup',
        help='setup anouman',
        dest='setup',
        action='store_true',
        default=False,
    )

    parser.add_argument('--mysql',
        help='setup for mysql backed database',
        dest='mysql',
        action='store_true',
        default=True,
    )

    args = parser.parse_args()

    if args.django_project:
        args.django_project = os.path.abspath(args.django_project)

    """ By default (neither --socket nor --bind is explicitly passed in) 
        we bind to --socket=unix:/var/run/your_project.sock
        If the --bind={10.0.1.13:8000} option is used
        the --socket default is overridden...Even if you pass 
        --socket yourself.  If
    """
    if args.bind:
        args.socket=False

    return args



if __name__ == '__main__':
    print "anouman"
    args = get_args()
    
    if args.vm:
       build_vm(args) 

    # Project Packaging
    if args.django_project:
        package_django_project(args)
    
    # Project Deploying
    if args.deploy:
        deploy_django_project(args)

    # This is for creating a brand new django project
    # TODO do we still want to go this route???
    if args.project_name:
        setup.new_project( args )


    

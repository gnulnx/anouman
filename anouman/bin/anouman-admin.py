#!/usr/bin/env python
import os 
import argparse
import subprocess

from os.path import expanduser

import anouman.project_setup.setup as setup

descr="""
    anouman is a django 1.4+ deployment simplifier.

    You provide anouman a django project and anouman provides
    you a fully deployable pip installable package.
    
    PLUS you also get the option of running it on a virtual machine 
    first.

    NOTE:  anouman
    Currently we can deploy project based on django 1.4 and up.
"""

def get_args():
    parser = argparse.ArgumentParser(
        description=descr
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
        help='Create deployment for settings',
        dest='settings',
        default=False,
    )

    parser.add_argument('--wsgi',
        help='Create deployment for wsgi',
        dest='wsgi',
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
    #parser.add_argument('--socket',
    #    help='Set the unix socket we should bind to',
    #    dest='socket',
    #    default='unix:/var/run/your_project.sock',
    #)
    
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
    args = get_args()

    # Client Side
    # Package a current django project as an anouman tar ball
    if args.django_project:
        setup.package_django_project(args)
    
    # Server Side
    # deploy a anouman tarball
    if args.deploy:
        setup.deploy_django_project(args)

    # This is for creating a brand new django project
    # TODO do we still want to go this route???
    if args.project_name:
        setup.new_project( args )


    # TODO Is this code path still used?
    if args.setup:
        print "YEP YOU ARE IN args.setup section"
        sys.exit(0)
        # Change to the users home diretory
        os.chdir( expanduser("~") )


        print "Running initial setup"
        subprocess.call(["pip", "install", "virtualenv"])      
        
        print "Creating the master .anouman virtualenv"
        subprocess.call(["virtualenv", ".anouman"])

        # Source the activate command
        print "source .anouman/bin/activate"
        os.system("source .anouman/bin/activate")
        #subprocess.call(["source", ".anouman/bin/activate"])
     
        print "pip install virtualenvwrapper"
        subprocess.call(["pip", "install", "virtualenvwrapper"])

        print "installing django for anouman"
        subprocess.call(["pip", "install", "django"])

        # Now lets convert our virtualenv to a wrapped virtualenv
        print "mkvirtualenv .anouman"
        subprocess.call(["mkvirtualenv", ".anouman"])

        print "echo source .anouman/bin/virtualenvwrapper >> .bash_profil"        
        os.system("source .anouman/bin/virtualenvwrapper")
        
        print "Also add it to the users .bash_profile"
        subprocess.call(["echo", "source .anouman/bin/virtualenvwrapper >> .bash_profile"])



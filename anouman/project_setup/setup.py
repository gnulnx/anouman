import os, sys, stat
import getpass
import fnmatch
import subprocess
from anouman.templates.gunicorn_start import  (
    gunicorn_start,
    gunicorn_context, 
)

from anouman.templates.gunicorn_start import (
    gunicorn_start,
    gunicorn_context,
)

from anouman.exceptions import (
    MultipleSettingError,
    NoSettingsError,
    MultipleWSGIError,
    NoWSGIError,
)

def find_file(root_dir, pattern):
    matches = []
    for root, dirnames, filenames in os.walk(root_dir):
        for filename in fnmatch.filter(filenames, pattern):
            matches.append(os.path.join(root, filename))
    return matches

def get_settings(args):
    """
        This function checks for the existence of the settings file.

        If the --settings options is specified then we simply
        check to see if the file exists and if so return the name of the
        file.

        If no --settings option was given then we look for settings.py
        recursivly in the directory defined by --django-project.
          -- If multiple settings.py are found we throw an exception.
          -- If not settings.py is found we throw an exception.
          -- If one settings.py is found we return it's path.
    """
    settings_path=''
    if not args.settings:
        matches = find_file(args.django_project, 'settings.py')
        if len(matches) > 1:
            raise MultipleSettingError(matches)
        elif len(matches) == 0:
            raise NoSettingsError()
        settings_path= matches[0]
    elif not os.path.isfile(args.settings):
        raise NoSettingsError() 
    else:
        settings_path = args.settings
    
    # We now have the path to the wsgi.py modules, but we need
    # to convert it to python module format:  website.wsgi
    tmp = settings_path.split( os.path.abspath(args.django_project) )
    if len(tmp) == 2:
        return tmp[1][1:].replace("/", ".").replace(".py", "")
    else:
        raise NoSettingsError( str(tmp) )
    
def get_wsgi(args):
    """
        This function checks for the existence of the wsgi file.

        If the --wsgi options is specified then we simply
        check to see if the file exists and if so return the name of the
        file.

        If no --wsgi option was given then we look for settings.py
        recursivly in the directory defined by --django-project.
          -- If multiple wsgi.py are found we throw an exception.
          -- If not wsgi.py is found we throw an exception.
          -- If one wsgi.py is found we return it's path.
    """
    wsgi_path = ''
    if not args.wsgi:
        matches = find_file(args.django_project, 'wsgi.py')
        if len(matches) > 1:
            raise MultipleWSGIError(matches)
        if len(matches) == 0:
            raise NoWSGIError()
        wsgi_path=os.path.abspath( matches[0] )
    elif not os.path.isfile(args.wsgi):
        raise NoWSGIError() 
    else:
        wsgi_path = os.path.abspath( args.wsgi )

    # We now have the path to the wsgi.py modules, but we need
    # to convert it to python module format:  website.wsgi
    tmp = wsgi_path.split( os.path.abspath(args.django_project) )
    if len(tmp) == 2:
        return tmp[1][1:].replace("/", ".").replace(".py", "")
    else:
        raise NoWSGIError( str(tmp) )



def django_project(args):
    """
        Builds the gunicorn_start.py file based on:

        1)  A django settings.py file
        2)  A django project which is recursivly grepped for settings.py
    """
    SETTINGS = get_settings(args)
    WSGI = get_wsgi(args)
       
    BIN=os.path.abspath("%s/bin"%(args.virtualenv))
    PIP="%s/pip"%(BIN)
    DJANGO_VERSION="django%s"%(args.django_version)
    GUNICORN_START="%s/gunicorn_start"%(BIN)

    """
        Install the base modules into the virtualenv
    """
    subprocess.call(["virtualenv", args.virtualenv])
    subprocess.call([PIP, 'install', DJANGO_VERSION])
    if args.gunicorn:
        subprocess.call([PIP, "install", "gunicorn"])

    """
        Now we build up a context to apply to gunicorn_start.template.
        The gunicorn_context is found in: anouman/templates/gunicorn_start/__init__.py

        We the update gunicorn_context with out context and save the file
        to {{virtualenv}}/bin/gunicorn.py
    """
    NAME=os.path.basename(args.django_project)
    context = {
        'NAME':NAME,
        'USER':getpass.getuser(),   
        'GROUP':getpass.getuser(),
        'GUNICORN':"%s/gunicorn"%(BIN),
        'DJANGODIR':os.path.abspath(args.django_project),
        'DJANGO_SETTINGS_MODULE':SETTINGS,
        'DJANGO_WSGI_MODULE':WSGI,
    }   
    if args.bind:
        context['BIND'] = args.bind
    elif args.socket:
        context['SOCKFILE'] = args.socket
    else:
        raise Exception("You must have either --bind or --socket")

    gunicorn_context.update(context) 

    with open(GUNICORN_START, 'w') as f:
        f.write( 
            gunicorn_start( 
                gunicorn_context
            ) 
        )
    # Set Permissions on the GUNICORN file    
    os.chmod(GUNICORN_START, stat.S_IRWXU|stat.S_IRWXG|stat.S_IXOTH)
    print gunicorn_start( gunicorn_context )

    """
        Now we create the gunicorn upstart scripts
    """
    

def new_project(args):
    BIN="%s/bin"%(args.virtualenv)
    PIP="%s/pip"%(BIN)
    GUNICORN="%s/gunicorn"%(BIN)
    GUNICORN_START="%s/gunicorn_start.py"%(BIN)
    DJANGO_VERSION="django%s"%(args.django_version)
    ADMIN='%s/django-admin.py'%(BIN)
    # Our very first step will be to create a brand new virtual environment
    subprocess.call(["virtualenv", args.virtualenv])
    subprocess.call([PIP, 'install', DJANGO_VERSION])
    # This section setups up the django server
    if args.gunicorn:
        subprocess.call([PIP, "install", "gunicorn"])

    
    # Next we need to install packaged.txt.  This will include things like django
    subprocess.call([ADMIN, 'startproject', args.project_name])

    print "Your project is ready for development"
    print "run source %s/activate" %(BIN)

    with open(GUNICORN_START, 'w') as f:
        f.write( gunicorn_start() )

    # Set Permissions on the GUNICORN file    
    os.chmod(GUNICORN_START, stat.S_IRWXU|stat.S_IRWXG|stat.S_IXOTH)


if __name__ == '__main__':
    setup("TestENV")

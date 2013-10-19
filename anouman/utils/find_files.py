import os, sys, re
import fnmatch

from anouman.exceptions import (
    MultipleSettingError,
    NoSettingsError,
    MultipleWSGIError,
    NoWSGIError,
    MultipleMANAGEError,
    NoMANAGEError,
)

def find_file(root_dir, pattern):
    """
        This is a generic recursive grep function
    """
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
            print "args.django_project: ", args.django_project
            print "search path: %s"%(os.path.abspath(args.django_project))
            raise NoSettingsError()
        settings_path= matches[0]
    elif not os.path.isfile(args.settings):
        raise NoSettingsError() 
    else:
        settings_path = args.settings
   
    # We now have the path to the settings.py modules, but we need
    # to convert it to python module format:  settings.wsgi
    tmp = settings_path.split(args.django_project)
    if len(tmp) == 2:
        return [
            os.path.abspath(settings_path), 
            tmp[1][1:].replace("/", ".").replace(".py", "")
        ]
    else:
        raise NoSettingsError( str(tmp) )
    
def get_wsgi(args):
    """
        This function checks for the existence of the wsgi.py file.

        If the --wsgi options is specified then we simply
        check to see if the file exists and if so return the name of the
        file.

        If no --wsgi option was given then we look for wsgi.py
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

def get_manage(args):
    """
        This function checks for the existence of the manage.py file.

        If the --manage options is specified then we simply
        check to see if the file exists and if so return the name of the
        file.

        If no --manage option was given then we look for manage.py
        recursivly in the directory defined by --django-project.
          -- If multiple manage.py are found we throw an exception.
          -- If not manage.py is found we throw an exception.
          -- If one manage.py is found we return it's path.
    """
    manage_path = ''
    if not args.manage:
        matches = find_file(args.django_project, 'manage.py')
        if len(matches) > 1:
            raise MultipleMANAGEError(matches)
        if len(matches) == 0:
            raise NoMANAGEError()
        manage_path = matches[0]
    elif not os.path.isfile(args.manage):
        raise NoMANAGEError()
    else:
        manage_path = os.path.abspath( args.manage )

    return os.path.abspath( manage_path )

def change_settings(settings_file, pattern, value):
    with  open(settings_file, 'r') as f:
        contents = f.readlines()

    match_count = 0
    for line in contents:
        if pattern in line and "#" not in line:
            match_count = match_count + 1

    
    if match_count > 1:
        print "WARNING:  More than one %s line in settings file." %(pattern)
        print "Anouman would prefer to have you set this value yourself or remove duplicate %s settings" %(pattern)
        return False

    new_contents = []
    for line in contents:
        if pattern in line and "#" not in line:
            line = "#"+line
            new_contents.append(line)
            new_contents.append('%s="%s"'%(pattern, value) )
        else:
            new_contents.append(line)

    with open(settings_file, 'w') as f:
        f.writelines(new_contents)

    # Flush the stdout buffer and force write to disk
    sys.stdout.flush()

    return True

def set_static_roots(args):
    """
        We need to change the STATIC_ROOT and MEDIA_ROOT variables
    """
    [settings_path, SETTINGS] = get_settings(args)
    sys.path.append(os.path.dirname(settings_path))
    import settings
    
    change_settings(settings_path, r'MEDIA_ROOT', "%s/"%(os.path.abspath("%s/media/" %(args.domainname))) )
    change_settings(settings_path, r'STATIC_ROOT', "%s/"%(os.path.abspath("%s/static/" %(args.domainname))) )

    reload(settings)

    return [settings.STATIC_ROOT, settings.MEDIA_ROOT]

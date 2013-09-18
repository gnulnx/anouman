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
    #tmp = settings_path.split( os.path.abspath(args.django_project) )
    tmp = settings_path.split(args.django_project)
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

def deploy_django_project(args):
    print "deploy_django_project 1"
    """
        The Very First thing we want to do is unpack the project
    """
    print "unzipping: ", args.deploy
    subprocess.call(["tar", "xvfz", args.deploy])
    
    # Set both args.domainname  AND args.django_project to the deploy basename
    args.domainname = args.deploy.split(".tar.gz")[0]
    args.django_project=args.domainname+"/src"

    # Ideally I'd like to call mkvirtualenv from virtualenv wrapper
    # But since it's derived from a soruced file it's not accessible
    # so instead we just call virtualenv ourselves and save in the
    # default ~/.virtualenvs/  directory
    VIRTUALENV = ".virtualenvs/%s"%(args.domainname)
    subprocess.call(["virtualenv", VIRTUALENV])

    SETTINGS = get_settings(args)
    WSGI = get_wsgi(args)


    print "SETTINGS: ", SETTINGS
    print "WSGI: ", WSGI

    BIN=os.path.abspath("%s/bin"%(VIRTUALENV))
    PIP="%s/pip"%(BIN)
    DJANGO_VERSION="django%s"%(args.django_version)
    GUNICORN_START="%s/gunicorn_start"%(BIN)

    print "deploy_django_project 2"

    pkg_success = []
    pgk_fails = []
    with open("%s/pip_packages.txt"%(args.domainname)) as f:
        PACKAGES = f.readlines()
        PACKAGES.append("gunicorn")
        for package in PACKAGES:
            try:
                subprocess.call([PIP, "install", package])
                pkg_success.append(package)
            except:
                pgk_fails.append(package)
    
    subprocess.call([PIP, "install", "-r", "%s/pip_packages.txt"%(args.domainname)])
    print "Package Installation Results"
    print "SUCCESS: %s" %(len(pkg_success))
    print "FAIL:    %s" %(len(pgk_fails))
    for f in pgk_fails:
        print "\t*\t%s"%(f)


    """
        Now we build up a context to apply to gunicorn_start.template.
        default context located: anouman/templates/gunicorn_start/__init__.py

        We the update gunicorn_context with our context and save the file
        to {{domainname}}/bin/gunicorn_start
    """
    NAME=os.path.basename(args.django_project)
    DJANGODIR=os.path.abspath(args.domainname + "/" + NAME)

    context = {
        'NAME':args.domainname,
        'USER':getpass.getuser(),
        'GROUP':getpass.getuser(),
        'GUNICORN':"%s/gunicorn"%(BIN),
        'DJANGODIR':DJANGODIR,
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
    os.chmod(
        GUNICORN_START,
        stat.S_IRWXU|stat.S_IRWXG|stat.S_IXOTH
     )
    """
        Now we create the gunicorn upstart scripts
    """

def package_django_project(args):
    SETTINGS = get_settings(args)
    WSGI = get_wsgi(args)
    
    BIN=os.path.abspath("%s/bin"%(args.domainname))
    PIP="%s/pip"%(BIN)
    DJANGO_VERSION="django%s"%(args.django_version)
    GUNICORN_START="%s/gunicorn_start"%(BIN)
        
    os.makedirs(args.domainname)
    
    """
        Install packages from project environment into the new virtualenv.
        Also store the status for success/fail as we install them
    """
    pip = subprocess.check_output(['which', 'pip'])
    print "pip: ", pip
    print "Saving pacakges to: ", "%s/pip_packages.txt"%(args.domainname)
    os.system("pip freeze > %s/pip_packages.txt"%(args.domainname))

    #freeze = subprocess.check_output([pip, 'freeze'])
    #print "freeze: ", freeze
    #with open("%s/pip_packages.txt"%(args.domainname), 'w') as f:
    #    pkg_success = []
    #    pgk_fails = []
    #    for package in subprocess.check_output([pip, 'freeze']).split("\n"):
    #        f.write(package+"\n")
    
    """
        Now we copy your django project into the virtual env
    """
    print "Copying your source tree into the virtual env"
    print "args.django_project: ", args.django_project
    print "args.domainname: ", args.domainname
    subprocess.call(['cp', '-r', args.django_project, args.domainname+"/src"]) 
    subprocess.call(['tar', '-cf', args.domainname+".tar", args.domainname])
    subprocess.call(['gzip', args.domainname+".tar"])
    subprocess.call(["rm", "-rf", args.domainname])

"""
def django_project(args):
    if args.deploy:
        deploy_django_project(args)
    else:
        package_django_project(args)
"""
 
def new_project(args):
    BIN="%s/bin"%(args.domainname)
    PIP="%s/pip"%(BIN)
    GUNICORN="%s/gunicorn"%(BIN)
    GUNICORN_START="%s/gunicorn_start.py"%(BIN)
    DJANGO_VERSION="django%s"%(args.django_version)
    ADMIN='%s/django-admin.py'%(BIN)
    # Our very first step will be to create a brand new virtual environment
    subprocess.call(["virtualenv", args.domainname])
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

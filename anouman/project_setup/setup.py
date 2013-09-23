import os, sys, stat
from os.path import expanduser
import getpass
import subprocess

# TODO refactor this template
from anouman.templates.gunicorn_start import (
    gunicorn_start,
    gunicorn_context,
)

# TODO Refactor this template
from anouman.templates.nginx import (
    nginx_upstart,
    nginx_context,
)

from anouman.templates.init_script import gunicorn_upstart
from anouman.templates.commands import commands

from anouman.utils.find_files import (
    get_settings,
    get_wsgi,
    get_manage
)

def deploy_django_project(args):
    """
        The Very First thing we want to do is unpack the project
    """
    # subproces, tar returns zero on success...
    if subprocess.call(["tar", "xvfz", args.deploy]):
        raise Exception( "Call to subprocess failed" )
    
    # Set both args.domainname  AND args.django_project to the deploy basename
    args.domainname = args.deploy.split(".tar.gz")[0]
    args.django_project=args.domainname+"/src"

    # Ideally I'd like to call mkvirtualenv from virtualenv wrapper
    # But since it's derived from a soruced file it's not accessible
    # so instead we just call virtualenv ourselves and save in the
    # default ~/.virtualenvs/  directory
    home = expanduser("~")
    VIRTUALENV = home+"/.virtualenvs/%s"%(args.domainname)
    subprocess.call(["virtualenv", VIRTUALENV])

    #settings is the full path
    #SETTINGS is the django project path:  ex finance.settings
    [settings, SETTINGS] = get_settings(args)
    WSGI = get_wsgi(args)       # get module path to wsgi.py
    MANAGE = get_manage(args) #get abspath of manage.py

    BIN=os.path.abspath("%s/bin"%(VIRTUALENV))
    PIP="%s/pip"%(BIN)
    PYTHON="%s/python"%(BIN)
    ACTIVATE="%s/activate"%(BIN)
    DJANGO_VERSION="django%s"%(args.django_version)
    GUNICORN_START="%s/gunicorn_start"%(BIN)
    
    ## Now add a few shell commands to the activate script that will be
    ## unique to each deployed website
    # TODO You can potentially use virtualenv hooks.
    commands.context['DOMAINNAME'] = args.domainname
    cmd_str = commands.get_commands(commands.context)
    with open(ACTIVATE, 'a') as f:   
        f.write(cmd_str)


    # Now we loop over the list of packages we stored during the packaging phase
    # and try to install them with pip
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


    # Now we run the collectstatic command
    subprocess.call([PYTHON, MANAGE, "collectstatic"])


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

        # Default bind is unix:/var/run/domainname.com.sock
        # Override with --bind=ip:port 
        'BIND':args.bind if args.bind else 'unix:/var/run/%s.sock' %(args.domainname),
    }

    gunicorn_context.update(context)

    with open(GUNICORN_START, 'w') as f:
        f.write( gunicorn_start( gunicorn_context ) )

    # Set Permissions on the GUNICORN file
    os.chmod(GUNICORN_START, stat.S_IRWXU|stat.S_IRWXG|stat.S_IXOTH)


    """
        Now we create the gunicorn upstart scripts
    """
    NAME=args.domainname+".conf"
    gunicorn_upstart.context.update({
        'GUNICORN_START':GUNICORN_START,
        'DOMAINNAME':args.domainname,
    })
    with open(NAME, 'w') as f:
        f.write(
            gunicorn_upstart.build_init(
                gunicorn_upstart.context
            )
        )

    print "We need to copy the website startup scripts to /etc/init/"
    print "This will require you to enter your sudo password now."
    os.system("sudo mv %s /etc/init/%s"%(NAME, NAME) )


    """
        nginx script for the site.
        place in:   /etc/nginx/sites-available
        link to:    /etc/nginx/sites-enabled 

        templ_file: anouman/templates/nginx/ngix_site.template
         
    """
    ## Import the users django settings file and grab the STATIC_ROOT and MEDIA_ROOT vars
    sys.path.append(os.path.dirname(settings))
    import settings
    if settings.STATIC_ROOT[-1] is not '/':
        settings.STATIC_ROOT = settings.STATIC_ROOT = "/"

    # Create the log directory, defaults to domain/logs
    # TODO add --logs option to allow user to specify log directory
    PROJECT_ROOT = "/".join( settings.STATIC_ROOT.split("/")[:-2] )
    LOG_DIR = os.getcwd() +"/%s/logs/"%(args.domainname)
    os.makedirs(LOG_DIR)

    nginx_context.update({
        'UNIXBIND':'unix:/var/run/%s.sock' %(args.domainname),
        'DOMAINNAME':args.domainname,
        'DJANGO_STATIC':settings.STATIC_ROOT,
        'DJANGO_MEDIA':settings.MEDIA_ROOT,
        'ACCESS_LOG':"%s/access.log"%(LOG_DIR),
        'ERROR_LOG':"%s/error.log"%(LOG_DIR),
        
    })

    NGINX_CONF='nginx.%s.conf'%(args.domainname)
    with open(NGINX_CONF, 'w') as f:
        f.write( nginx_upstart(nginx_context) )

    print "We need to copy the nginx.domainname.conf file to /etc/nginx/sites-available/"
    print "This will require sudo"
    os.system("sudo mv %s /etc/nginx/sites-available/%s" % (NGINX_CONF, NGINX_CONF) )
    os.system("sudo ln -s /etc/nginx/sites-available/%s /etc/nginx/sites-enabled/"% (NGINX_CONF))

    print "\n\n----------------------------------------------"
    print "Please add the following line(s) to your .bash_profile"
    print "source /usr/local/bin/virtualenvwrapper.sh;"
    print "workon %s"%(args.domainname)
    print "\nThen call source on .bash_profile"
    print "\n$source ~/.bash_profile"

def package_django_project(args):
    # settings is the full path
    # SETTINGS is the django projec path, exL  finance.settings
    [settings, SETTINGS] = get_settings(args)
    
    DJANGO_VERSION="django%s"%(args.django_version)
        
    os.makedirs(args.domainname)
    
    """
        Install packages from project environment into the new virtualenv.
        Also store the status for success/fail as we install them
    """
    pip = subprocess.check_output(['which', 'pip'])
    print "pip: ", pip
    print "Saving pacakges to: ", "%s/pip_packages.txt"%(args.domainname)
    os.system("pip freeze > %s/pip_packages.txt"%(args.domainname))


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
    print "This does nothing"
    pass

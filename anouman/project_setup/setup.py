import os, sys, stat
from os.path import expanduser
import getpass
import subprocess


from anouman.templates import (
    gunicorn_start,
    site_upstart,
    commands,
    nginx,
    vagrant,
    vagrant_bootstrap,
    clean
)

from anouman.utils.find_files import (
    get_settings,
    get_wsgi,
    get_manage
)

def build_vm(args):
    if not args.vm:
        raise Exception("build_vm must be callsed with args.mv=name")

    os.mkdir(args.vm)
    os.chdir(args.vm)
    # Write the Vagrantfile
    vagrant.save("Vagrantfile", context={
            'NAME':args.vm,
            'PUBLIC':True
    })

    # Write teh bootstrap file
    vagrant_bootstrap.save(path="./bootstrap.sh", context={
        'NGINX':True,
        'MYSQL':True,
    })

    # Write the clean file
    clean.save(path="./clean.sh", context={
        'DOMAINNAME':'site3.com'
    })
    
    subprocess.call(['vagrant', 'up'])

def deploy_django_project(args):
    """
        The very first thing we want to do is unpack the project
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

    # A few useful constant are set.
    BIN=os.path.abspath("%s/bin"%(VIRTUALENV))
    PIP="%s/pip"%(BIN)
    PYTHON="%s/python"%(BIN)
    ACTIVATE="%s/activate"%(BIN)
    DJANGO_VERSION="django%s"%(args.django_version)
    GUNICORN_START="%s/gunicorn_start"%(BIN)
    
    ## Now add a few shell commands to the activate script that will be
    ## unique to each deployed website
    # TODO You can potentially use virtualenv hooks.
    with open(ACTIVATE, 'a') as f:   
        f.write(
            commands.render(
                {'DOMAINNAME':args.domainname}
            )
        )


    """
        Now we build up a context to apply to gunicorn_start.template.
        default context located: anouman/templates/gunicorn_start/__init__.py

        We the update gunicorn_context with our context and save the file
        to {{domainname}}/bin/gunicorn_start
    """
    NAME=os.path.basename(args.django_project)
    DJANGODIR=os.path.abspath(args.domainname + "/" + NAME)

    gunicorn_start.save(GUNICORN_START, context={
        'NAME':args.domainname,
        'USER':getpass.getuser(),
        'GROUP':getpass.getuser(),
        'GUNICORN':"%s/gunicorn"%(BIN),
        'DJANGODIR':DJANGODIR,
        'DJANGO_SETTINGS_MODULE':SETTINGS,
        'DJANGO_WSGI_MODULE':WSGI,
        'BIND':args.bind if args.bind else 'unix:/var/run/%s.sock' %(args.domainname),
    })

    # Set Permissions on the GUNICORN file
    os.chmod(GUNICORN_START, stat.S_IRWXU|stat.S_IRWXG|stat.S_IXOTH)


    """
        Now we create the gunicorn upstart scripts
    """
    NAME=args.domainname+".conf"
    site_upstart.save(NAME, context={
        'GUNICORN_START':GUNICORN_START,
        'DOMAINNAME':args.domainname,
    })

    os.system("sudo mv %s /etc/init/%s"%(NAME, NAME) )


    ## Import the users django settings file and grab the STATIC_ROOT and MEDIA_ROOT vars
    sys.path.append(os.path.dirname(settings))
    from settings import STATIC_ROOT, MEDIA_ROOT
    if MEDIA_ROOT:
        if MEDIA_ROOT[-1] is not '/':
            MEDIA_ROOT = MEDIA_ROOT + "/"
    else:
        MEDIA_ROOT = "/"

    if STATIC_ROOT:
        if STATIC_ROOT[-1] is not '/': #here
            STATIC_ROOT = STATIC_ROOT + "/"
    else:
        STATIC_ROOT = "/"

    # Create the log directory, defaults to domain/logs
    # TODO add --logs option to allow user to specify log directory
    PROJECT_ROOT = "/".join( STATIC_ROOT.split("/")[:-2] )
    LOG_DIR = os.getcwd() +"/%s/logs/"%(args.domainname)
    os.makedirs(LOG_DIR)

    """
        nginx script for the site.
        place in:   domainname/etc/nginx/sites-available
        and in:   /etc/nginx/sites-available
        link to:    /etc/nginx/sites-enabled 

        Anouman should eventually be able to bring your sites on       
        and off line simple by removing the symlink
         
    """
    NGINX_CONF='nginx.%s.conf'%(args.domainname)
    nginx.save(NGINX_CONF, context={
        'UNIXBIND':'unix:/var/run/%s.sock' %(args.domainname),
        'DOMAINNAME':args.domainname,
        'DJANGO_STATIC':STATIC_ROOT,
        'DJANGO_MEDIA':MEDIA_ROOT,
        'ACCESS_LOG':"%s/access.log"%(LOG_DIR),
        'ERROR_LOG':"%s/error.log"%(LOG_DIR),
    })

    # First we make sure we have an /etc/ directory in our project directory.
    # We will use this directory to store ubuntu settings files that we generate 
    # vi anouman
    os.makedirs("%s/etc/nginx/sites-available/"%(args.domainname) )
    os.system("sudo cp %s %s/etc/nginx/sites-available/%s" % (NGINX_CONF, args.domainname, NGINX_CONF) )

    # TODO??    Do you really need to copy to /etc/nginx/sites-available/?
    #           Can't you just symlink from domain/etc/nginx/sites-available/
    os.system("sudo mv %s /etc/nginx/sites-available/%s" % (NGINX_CONF, NGINX_CONF) )
    os.system("sudo ln -s /etc/nginx/sites-available/%s /etc/nginx/sites-enabled/"% (NGINX_CONF))


    """
        This section installs the users python packages into their site virtualenv
    """
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
        Really?  This was the first idea you had for a setup complete message?  lol
    """
    print "#######################################################################"
    print "                                                                       "    
    print "                        SETUP COMPLETE                                 "    
    print "                                                                       "    
    print "         Please add the following line(s) to your .bash_profile        "
    print "                                                                       "    
    print "         source /usr/local/bin/virtualenvwrapper.sh                    "
    print "         workon %s                                                     "%(args.domainname)
    print "                                                                       "    
    print "         Then call source on .bash_profile                             "
    print "         $source ~/.bash_profile                                       "
    print "                                                                       "    
    print "#######################################################################"

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

import os, sys, stat
from os.path import expanduser
import getpass
import subprocess


from anouman.templates import (
    GunicornTemplate,
    UpstateTemplate,
    NginxTemplate,
    ShellCommandTemplate,
)

from anouman.utils.find_files import (
    get_settings,
    get_wsgi,
    get_manage,
    get_static_roots
)

def package_django_project(args):
    BIN=os.path.abspath("%s/bin"%(args.domainname))
    
    # settings is the full path
    # SETTINGS is the django projec path, exL  finance.settings
    [settings, SETTINGS] = get_settings(args)
    WSGI = get_wsgi(args) 
        
    os.makedirs(args.domainname)
    os.makedirs("%s/bin"%(args.domainname))
    os.makedirs("%s/etc/nginx/sites-available"%(args.domainname))
    os.makedirs("%s/etc/init"%(args.domainname))

    LOG_DIR = "%s/logs"%(args.domainname)
    os.makedirs(LOG_DIR)

    [STATIC_ROOT, MEDIA_ROOT] =get_static_roots(args) 

    NGINX_CONF='%s/etc/nginx/sites-available/%s.conf'%(args.domainname, args.domainname)
    NginxTemplate.save(NGINX_CONF, context={
        'UNIXBIND':'unix:/var/run/%s.sock' %(args.domainname),
        'DOMAINNAME':args.domainname,
        'DJANGO_STATIC':STATIC_ROOT,
        'DJANGO_MEDIA':MEDIA_ROOT,
        'ACCESS_LOG':"%s/nginx-access.log"%(LOG_DIR),
        'ERROR_LOG':"%s/nginx-error.log"%(LOG_DIR),
    })
   

    """
        Now we build up a context to apply to gunicorn_start.template.
        default context located: anouman/templates/gunicorn_start/__init__.py

        We the update gunicorn_context with our context and save the file
        to {{domainname}}/bin/gunicorn_start
    """
    NAME=os.path.basename(args.django_project)
    DJANGODIR=os.path.abspath(args.domainname + "/" + NAME)

    #/home/anouman/.virtualenvs/johnfurr.com/bin/gunicorn_start
    GUNICORN_START="%s/bin/gunicorn_start.sh"%(args.domainname)
    BIND = args.bind if args.bind else 'unix:/var/run/%s.sock' %(args.domainname)
    GunicornTemplate.save(GUNICORN_START, context={
        'NAME':args.domainname,
        'USER':getpass.getuser(),
        'GROUP':getpass.getuser(),
        'GUNICORN':"%s/gunicorn"%(BIN),
        'DJANGODIR':DJANGODIR,
        'DJANGO_SETTINGS_MODULE':SETTINGS,
        'DJANGO_WSGI_MODULE':WSGI,
        'ACCESS_LOG':"%s/gunicorn-access.log"%(LOG_DIR),
        'ERROR_LOG':"%s/gunicorn-error.log"%(LOG_DIR),
        'BIND':BIND,
        'SOCKFILE': False if 'unix' not in BIND else BIND.split('unix:')[1],
    }) 
    
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


if __name__ == '__main__':
    print "This does nothing"
    pass

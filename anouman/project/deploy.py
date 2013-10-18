import os, sys, stat
from os.path import expanduser
import getpass
import subprocess


from anouman.templates import (
    VagrantTemplate,
    VagrantBootstrapTemplate,
    CleanTemplate,
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


class Deploy():
    """
        The following modules level variables are used throughout the deployment process
    """

    def __init__(self, args):
        # Next we unpack the project
        # subproces, tar returns zero on success...
        if subprocess.call(["tar", "xvfz", args.deploy]):
            raise Exception( "Call to subprocess failed on tar unpack" )
        
        # Set both args.domainname  AND args.django_project to the deploy basename
        args.domainname = args.deploy.split(".tar.gz")[0]
        args.django_project=args.domainname+"/src"
   
        home = expanduser("~")
        # absolute path to the virtualenv
        self.VIRTUALENV = home+"/.virtualenvs/%s"%(args.domainname)

        # absoluate path to virtualenv/bin/
        self.VIRTBIN=os.path.abspath("%s/bin"%(self.VIRTUALENV))

        # absolute path to the virtualenv pip
        self.PIP="%s/pip"%(self.VIRTBIN)

        # absolute path the virtualenv python interpretor
        self.PYTHON="%s/python"%(self.VIRTBIN)

        # absolute path the vitualenv activate script
        self.ACTIVATE="%s/activate"%(self.VIRTBIN)

        # absolute path to the project LOGDIR
        self.LOG_DIR = os.getcwd() +"/%s/logs"%(args.domainname)

        # absolute path to the gunicorn_start.sh script
        self.GUNICORN_START="%s/gunicorn_start"%(self.VIRTBIN)

        # SETTINGS project path:  ex  project.settings
        # settings absolute path to the settings.py
        [self.settings, self.SETTINGS] = get_settings(args)    

        # absolute path to the project wsgi.py
        self.WSGI = get_wsgi(args) 

        # absolute path to manage.py
        self.MANAGE = get_manage(args) #get abspath of manage.py

        # Create log directory if it doesn't exist
        if not os.path.isdir(self.LOG_DIR):
            os.makedirs(self.LOG_DIR)

        
        self.deploy_django_project(args)

    
    def deploy_django_project(self, args):
        """
            This is the primary deploy method
        """

        # Create a virtualenv
        subprocess.call(["virtualenv", self.VIRTUALENV])

        # Append anouman shell command to activate script
        ShellCommandTemplate.save(self.ACTIVATE, context={'DOMAINNAME':args.domainname})

        # Create the gunicorn_start.sh file
        self.Setup_Gunicorn_Start(args)

        # Create the upstart files in /etc/init
        self.SetupUpstart(args)

        # Create the NGINX files
        self.SetupNGINX(args)

        # Install the python packages
        self.install_python_packages(args)

        # Run collectstatic command
        subprocess.call([self.PYTHON, self.MANAGE, "collectstatic"])

        """
            Print output message
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



    def SetupNGINX(self, args):
        """
            nginx script for the site.
            place in:   domainname/etc/nginx/sites-available
            and in:   /etc/nginx/sites-available
            link to:    /etc/nginx/sites-enabled 

            Anouman should eventually be able to bring your sites on       
            and off line simple by removing the symlink

            Must pass an args with minimally:
            args.domainname
            args.django_project OR args.settings
        """

        # retrieve STATIC_ROOT and MEDIA_ROOT from settings.py
        [self.STATIC_ROOT, self.MEDIA_ROOT] = get_static_roots(args)

        print self.STATIC_ROOT
        print self.MEDIA_ROOT
        raw_input()

        NGINX_CONF='nginx.%s.conf'%(args.domainname)
        NginxTemplate.save(NGINX_CONF, context={
            'UNIXBIND':'unix:/var/run/%s.sock' %(args.domainname),
            'DOMAINNAME':args.domainname,
            'DJANGO_STATIC':self.STATIC_ROOT,
            'DJANGO_MEDIA':self.MEDIA_ROOT,
            'ACCESS_LOG':"%s/nginx-access.log"%(self.LOG_DIR),
            'ERROR_LOG':"%s/nginx-error.log"%(self.LOG_DIR),
        })

        # First we make sure we have an /etc/ directory in our project directory.
        # We will use this directory to store ubuntu settings files that we generate 
        # vi anouman
        os.system( "rm -rf %s/etc/nginx/sites-available/"%(args.domainname) )
        os.system( "rm -rf %s/etc/nginx/sites-enabled/"%(args.domainname) )
        os.makedirs("%s/etc/nginx/sites-available/"%(args.domainname) )
        os.system("sudo cp %s %s/etc/nginx/sites-available/%s" % (NGINX_CONF, args.domainname, NGINX_CONF) )

        # TODO??    Do you really need to copy to /etc/nginx/sites-available/?
        #           Can't you just symlink from domain/etc/nginx/sites-available/
        os.system("sudo mv %s /etc/nginx/sites-available/%s" % (NGINX_CONF, NGINX_CONF) )
        os.system("sudo ln -s /etc/nginx/sites-available/%s /etc/nginx/sites-enabled/"% (NGINX_CONF))


    def SetupUpstart(self, args):
        """
            Now we create the gunicorn upstart scripts
        """
        NAME=args.domainname+".conf"

        UpstateTemplate.save(NAME, context={
            'GUNICORN_START':self.GUNICORN_START,
            'DOMAINNAME':args.domainname,
        })

        os.system("sudo mv %s /etc/init/%s"%(NAME, NAME) )


    def Setup_Gunicorn_Start(self, args):
        """
            Now we build up a context to apply to gunicorn_start.template.
            default context located: anouman/templates/gunicorn_start/__init__.py

            We the update gunicorn_context with our context and save the file
            to {{domainname}}/bin/gunicorn_start
        """
 
        NAME=os.path.basename(args.django_project)
        DJANGODIR=os.path.abspath(args.domainname + "/" + NAME)
        GunicornTemplate.save(self.GUNICORN_START, context={
            'NAME':args.domainname,
            'USER':getpass.getuser(),
            'GROUP':getpass.getuser(),
            'GUNICORN':"%s/gunicorn"%(self.VIRTBIN),
            'DJANGODIR':DJANGODIR,
            'DJANGO_SETTINGS_MODULE':self.SETTINGS,
            'DJANGO_WSGI_MODULE':self.WSGI,
            'ACCESS_LOG':"%s/gunicorn-access.log"%(self.LOG_DIR),
            'ERROR_LOG':"%s/gunicorn-error.log"%(self.LOG_DIR),
            'BIND':args.bind if args.bind else 'unix:/var/run/%s.sock' %(args.domainname),
        })

        # Set Permissions on the GUNICORN file
        os.chmod(self.GUNICORN_START, stat.S_IRWXU|stat.S_IRWXG|stat.S_IXOTH)

        return self.GUNICORN_START

    def install_python_packages(self, args):
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
                    subprocess.call([self.PIP, "install", package])
                    pkg_success.append(package)
                except:
                    pgk_fails.append(package)
    
        subprocess.call([self.PIP, "install", "-r", "%s/pip_packages.txt"%(args.domainname)])
        print "Package Installation Results"
        print "SUCCESS: %s" %(len(pkg_success))
        print "FAIL:    %s" %(len(pgk_fails))
        for f in pgk_fails:
            print "\t*\t%s"%(f)



if __name__ == '__main__':
    print "This does nothing"
    pass

import os, sys, stat, shutil
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
    change_settings,
)


class Deploy():
    """
        To Deploy a site simply call Deploy(args)
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

        # settings absolute path to the settings.py
        # SETTINGS project path:  ex  project.settings
        [self.settings, self.SETTINGS] = get_settings(args)    

        # absolute path to the project wsgi.py
        self.WSGI = get_wsgi(args) 

        # absolute path to manage.py
        self.MANAGE = get_manage(args) #get abspath of manage.py

        # Create log directory if it doesn't exist
        if not os.path.isdir(self.LOG_DIR):
            os.makedirs(self.LOG_DIR)

        # Copy the users settings file to anouman_settings.py
        self.create_anouman_settings(args)

        # Update Settings File
        self.update_settings_file(args)
       
        # Now deploy the django project 
        self.deploy_django_project(args)


    def create_anouman_settings(self, args):
        """
            A copy of the settings file is made so anouman can make modifications to it without
            having to change the users source code.

            Assigns the path to anouman_settings.py to the self.anouman_settings
        """
        self.anouman_settings = "%s/anouman_settings.py" % ( os.path.dirname(self.settings) )
        shutil.copyfile(self.settings, self.anouman_settings)

        self.ANOUMAN_SETTINGS = SETTINGS.split(".")[:-1] + "anouman_settings.py"

    def update_settings_file(self, args):
        """
            We need to change the STATIC_ROOT and MEDIA_ROOT variables to default anouman locations.
            TODO: Eventually this should allow users to make modifications to these files in the
            Anouman bundle and not have --deploy overwrite them.
        
            We also need to change DEBUG to False for production use

            You should call create_anouman_settings() before calling this function
        """

        # First import the settings file
        #[settings_path, SETTINGS] = get_settings(args)
        #sys.path.append(os.path.dirname(settings_path))
        #import settings

        sys.path.append(os.path.dirname( self.anouman_settings )
        import anouman_settings

        # Then modify settings
        change_settings(self.anouman_settings, r'MEDIA_ROOT', "%s/"%(os.path.abspath("%s/media/" %(args.domainname))) )
        change_settings(self.anouman_settings, r'STATIC_ROOT', "%s/"%(os.path.abspath("%s/static/" %(args.domainname))) )

        # Set Debug to False and update ALLOWED_HOSTS to match domain name
        change_settings(self.anouman_settings, r'DEBUG', False )
        change_settings(self.anouman_settings, r'ALLOWED_HOSTS', ["%s"%(args.domainname)] )

        # Now reload the settings file
        reload(anouman_settings)

        # And set some class variables
        self.STATIC_ROOT = anouman_settings.STATIC_ROOT
        self.MEDIA_ROOT = anouman_settings.MEDIA_ROOT

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
        # TODO Figure out why you weren't able to do this with subprocess.call([])
        os.system( '''/bin/echo "yes" | %s %s collectstatic'''%(self.PYTHON, self.MANAGE) )


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
            and in:     /etc/nginx/sites-available
            link to:    /etc/nginx/sites-enabled 

            Anouman should eventually be able to bring your sites on       
            and off line simple by removing the symlink

            Must pass an args with minimally:
            args.domainname
            args.django_project OR args.settings
        """

        
        # Create the project etc/nginx/sites_available directory
        if not os.path.exists( "%s/etc/nginx/sites-available/"%(args.domainname) ):
            os.makedirs("%s/etc/nginx/sites-available/"%(args.domainname) )

        # Save nginx config ot project/etc/nginx/sites-available
        NGINX_CONF="%s/etc/nginx/sites-available/%s"%(args.domainname, args.domainname)
        NginxTemplate.save(NGINX_CONF, context={
            'UNIXBIND':'unix:/var/run/%s.sock' %(args.domainname),
            'DOMAINNAME':args.domainname,
            'DJANGO_STATIC':self.STATIC_ROOT,
            'DJANGO_MEDIA':self.MEDIA_ROOT,
            'ACCESS_LOG':"%s/nginx-access.log"%(self.LOG_DIR),
            'ERROR_LOG':"%s/nginx-error.log"%(self.LOG_DIR),
        })

        # Remove any prior installs
        os.system("rm -f /etc/nginx/sites-available/%(dn)s /etc/nginx/sites-enabled/%(dn)s"% {'dn':args.domainname} )

        # Copy the /etc/nginx files to /etc/nginx
        os.system("sudo cp -r %s/etc/nginx/* /etc/nginx/" %(args.domainname))
       
        # Symlink sites-available to sites enabled 
        os.system("sudo ln -s /etc/nginx/sites-available/%(dn)s /etc/nginx/sites-enabled/%(dn)s"% {'dn':args.domainname} )


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
            Setup and install gunicorn_start.sh on the server
            
            default context located: anouman/templates/gunicorn_start.sh
            install location  {virtenv}/bin/gunicorn_start.sh
        """

        # set DJANGODIR env variable to abspath of project root.
        NAME=os.path.basename(args.django_project)
        DJANGODIR=os.path.abspath(args.domainname + "/" + NAME)

        GunicornTemplate.save(self.GUNICORN_START, context={
            'NAME':args.domainname,
            'USER':getpass.getuser(),
            'GROUP':getpass.getuser(),
            'GUNICORN':"%s/gunicorn"%(self.VIRTBIN),
            'DJANGODIR':DJANGODIR,
            #'DJANGO_SETTINGS_MODULE':self.SETTINGS,
            'DJANGO_SETTINGS_MODULE':self.ANOUMAN_SETTINGS,
            'DJANGO_WSGI_MODULE':self.WSGI,
            'ACCESS_LOG':"%s/gunicorn-access.log"%(self.LOG_DIR),
            'ERROR_LOG':"%s/gunicorn-error.log"%(self.LOG_DIR),
            'LOG_LEVEL':args.gunicorn_log_level,
            'BIND':args.bind if args.bind else 'unix:/var/run/%s.sock' %(args.domainname),
        })

        # Set Permissions on the GUNICORN file
        os.chmod(self.GUNICORN_START, stat.S_IRWXU|stat.S_IRWXG|stat.S_IXOTH)

        return self.GUNICORN_START

    def install_python_packages(self, args):
        """
            This section installs the users python packages into their site virtualenv
            TODO:  This should have better reporting for failing packages
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

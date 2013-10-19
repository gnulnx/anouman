import os
import subprocess


from anouman.utils.find_files import (
    get_settings,
    get_wsgi,
)

def package_django_project(args):
    # settings is the full path
    # SETTINGS is the django projec path, exL  finance.settings
    [settings, SETTINGS] = get_settings(args)
    
    # TODO Should this all be done in deploy?    
    os.makedirs(args.domainname)
    os.makedirs("%s/bin"%(args.domainname))
    os.makedirs("%s/etc/nginx/sites-available"%(args.domainname))
    os.makedirs("%s/etc/init"%(args.domainname))

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

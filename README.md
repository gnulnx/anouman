Anouman Overview
================

Anouman is a django site deployment tool that is designed to greatly simplify the process of deploying [Django](https://www.djangoproject.com/) projects behind [gunicorn](http://gunicorn.org/)/[nginx](http://nginx.com/).  In the spirit of reusing great open source software Anouman makes use of [virtualenv](https://pypi.python.org/pypi/virtualenv),[virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/), and of course [django](https://www.djangoproject.com/) to help manage the process of deploying your django instances.  

The easiest way to become familiar with Anouman is to dive in and use it by following along with the tutorial below.  However, before you begin you will first need to install [vagrant](http://www.vagrantup.com/) and [virtualbox](https://www.virtualbox.org/).  You will be using these tools to build a fresh Ubuntu VM to test your django deployment on.

**Disclaimer:** *Anouman is still very much alpha stage software.  As such it has only been tested on Ubuntu 12.04 using the BASH shell.  I'd love to hear from others if they get this working in other OS/SHELL combinations.*  

Install Anouman
--------------

    pip install anouman

Virtual Machine Creation and Provisioning
-----------------------------------------

**Step 1:** VM Creation
    
    anouman --vm test1

This command uses vagrant to create and spin up a virtual machine in a directory called test1.
As part of the process it created a user *anouman* with sudo privileges and password *anouman*.  To login use:

    ssh anouman@192.168.100.100  # Password *anouman*

**Step 2:** Final provisioning

If you are using MySQL or Postgres you will need to install them now.  For mysql

    sudo apt-get install mysql-server

You will then need to login to the mysql server and create the appropriate database for your django project.

If you are using [Postgres](http://www.postgresql.org/download/linux/ubuntu/) you will need to follow a similar [protocal](http://www.postgresql.org/download/linux/ubuntu/) to setup your Postgres database.


Assuming this worked then you are ready to walk through the anouman tutorial and deploy your django project on a fresh virtual machine.



Anouman Setup and Deployment Tutorial
-----------------------------

### Section 1:  Packaging

This section will assume you have a django project called *example*.   Most likely your project is not named *example*
so to follow along with your project simple replace *example* with your project's name.

Before you begin make sure to open a new Terminal window.

**Step 1:** Switch to the python virtualenv you use for development.
        You are using [virtualenv](http://www.virtualenv.org/en/latest/) for python development right?  
        If not Anouman should still work with your python system packages.

        source /path/to/your/virtualenv/activate
        pip install anouman

**Step 2:** Update your django settings file to reflect the Virtual Machine you are about to deploy it on.

If you are using sqlite as your backend database you can ignore this section.

If you are using MySQL or Postgres with your project you will likely need to update your DATABASE settings in your settings.py file.
Look for the DATABASE Section and update change the HOST line to:
    
    'HOST': '192.168.100.100'
    
STATIC_ROOT and MEDIA_ROOT will be automatically set during deployment to reflect a default installion.  
Don't worry your original settings.py file on your local machine will remain untouched.

**Step 3:** Next you will create an anouman package that will be deployable on an anouman loaded
        server.  Start by navigating to the directory containing your django project.
        This is the directory you originally ran *django-admin.py startproject* from.
        For instance if you ran *django-admin startprojet example* from your home directory then you 
        want to be in your home directory when you issue the folowing command:

        anouman --django-project=example --domainname=example.com

Behind the scenes your django project was copied into a directory named
example.com/src. Inside this directory is another file which contains a listing of python packages you
are using for your django projects.  This was determiend from the output of "pip freeze" 

### Section2:  Deploying

**Step 4:** Scp your project to the virtual machine we created above and then log in.

        scp example.com.tar.gz  anouman@192.168.100.100:/home/anouman
        
Return to the terminal where you are logged into your vm or relogin with:

        ssh anouman@192.168.100.100

**Step 5:** Install anouman into the servers system python repository.

        sudo pip install anouman

**Step 6:** Setup  anouman and deploy your new project.   The first time you run anouman, with or without arguments, it will install itself and in the process create a wrapped '*anouman*' virtualenv as well as a wrapped '*example.com*' virtualenv.  For the sake of this tutorial we will do both setup and deployment with one command.

        anouman --deploy example.com.tar.gz

Follow the intructions when this command finished to update you .bash_profile
    
**Step 8:**  Assuming you update and sourced .bash_profile at the end of the deployment step you will now have a few shell commands that were appended to the end of your sites virtualenv activate script. For instance to check the status of gunicorn/nginx type:

    site status
    
Now let's bring it up..

    site start
    
Likewise you can stop your site with:

    site stop
    
Go ahead and bring the site back up:

    site start
    
You can force nginx to do a reload with:

    site reload

These site management commands are specific to the site curently being worked on.  If you install another django project anouman will gladly set it up for you and ensure that nginx properly directs traffic to the appropriate django back end and it's all managed with virtualenv and virtualenvwrapper.  To switch between sites deployed with anouman is as simple as switching wrapped virtualenv's.  For ex:  workon example.com, workon site2.com, etc.

**Step 9:**  Adjust client /etc/hosts file to simulate DNS for your web site.  First make sure your site is running (see step 8).  Next, add the following line to your /etc/hosts

    192.168.100.100   www.example.com   example.com

**Step 10:** Now point your browser to example.com and you should see your django website.  Enjoy. 

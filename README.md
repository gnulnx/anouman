Anouman Overview
================

Anouman is a django site deployment tool that is designed to greatly simplify the process of deploying [Django](https://www.djangoproject.com/) projects behind [gunicorn](http://gunicorn.org/)/[nginx](http://nginx.com/).  In the spirit of reusing great open source software Anouman makes use of [virtualenv](https://pypi.python.org/pypi/virtualenv), [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/), and of course [django](https://www.djangoproject.com/) to help manage the process of deploying your django projects.  

The easiest way to become familiar with Anouman is to dive in and use it by following along with the tutorial below.  However, before you begin you will first need to install [vagrant](http://www.vagrantup.com/) and [virtualbox](https://www.virtualbox.org/).  You will be using these tools to build a fresh Ubuntu VM to test your django deployment on.

**Disclaimer:** *Anouman is still very much alpha stage software.  As such it has only been tested on Ubuntu 12.04 using the BASH shell.  I'd love to hear from others if they get this working in other OS/SHELL combinations.*  

Install Anouman
--------------

Switch to the python virtualenv you use for development.  You are using [virtualenv](http://www.virtualenv.org/en/latest/) for python development right?  If not Anouman should still work with your python system packages.

    source /path/to/your/virtualenv/activate
    pip install anouman

Virtual Machine Creation and Provisioning
-----------------------------------------

**Step 1:** VM Creation
    
    anouman --vm test1

This command uses vagrant to create and spin up a virtual machine in a directory called test1.
As part of this process anouman created an account with sudo privileges.  Go ahead and login with user/password=*anouman/anouman*:

    ssh anouman@192.168.100.100  # Password *anouman*

**Step 2:** Final provisioning

If you are using sqlite as your database you may skip this step.

If you are using MySQL or Postgres you will need to install them now.  For MySQL:

    sudo apt-get install mysql-server

You will then need to login to the mysql server and create/setup the appropriate database for your django project.

If you are using [Postgres](http://www.postgresql.org/download/linux/ubuntu/) you will need to follow a similar [protocal](http://www.postgresql.org/download/linux/ubuntu/) to setup your Postgres database.


Assuming this worked then you are ready to walk through the Anouman tutorial and deploy your django project on a fresh virtual machine.



Anouman Setup and Deployment Tutorial
-----------------------------

### Section 1:  Packaging

This section will assume you have a django project called *example*.   Most likely your project is not named *example*
so follow along with your own project by simply replacing *example* with your project's name.

Before you begin make sure to open a new Terminal window.

**Step 1:** Create Anouman Package

In this step you will use Anouman to create a deployable package from your django project.  Start by navigating to the directory containing your django project. This is the directory you originally ran *django-admin.py startproject* from. For instance if you ran *django-admin start-project example* from your home directory then you want to be in your home directory when you issue the following command:

        anouman --django-project=example --domainname=example.com

Behind the scenes your django project was copied into a directory named example.com/src. Inside this directory is another file which contains a listing of python packages you are using for your django projects.  This was determiend from the output of "pip freeze".  Lastly this directory was tarred and gzipped. AKA an anouman package/bundle.

### Section2:  Deploying

**Step 1:** Copy files to server

Scp your Anouman bundle to the virtual machine we created above and then log in.

        scp example.com.tar.gz  anouman@192.168.100.100:/home/anouman
        
If you are using sqlite and it is not contained in your project directory then you will now need to copy it to the VM as well. *A future version will take care of copying your database to a default location and updating your setting file*

Return to the terminal where you are logged into your vm or relogin with:

        ssh anouman@192.168.100.100

**Step 2:** Install Anouman into the servers system python repository.  

        sudo pip install anouman

**Step 3:** Setup Anouman and deploy your new project.

*Anouman requires all projects to be installed as a non root user.*

The first time you run Anouman it will install itself and in the process create a wrapped '*anouman*' virtualenv as well as a wrapped '*example.com*' virtualenv.  

        anouman --deploy example.com.tar.gz

Follow the intructions when this command finishes to update/source your .bash_profile.  You should now have your web site deployed behind nginx/gunicorn.  Your projects system packages are now located in the default virtualenv wrapper location */home/anouman/.virtualenvs/example.com*.  If you are unfamiliar with the  [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/) I highly recommend taking a little time to become familiar with it.

Anouman has also modified your STATIC_ROOT and MEDIA_ROOT variables in settings.py to point to *example.com/static* and *example.com/media* respectively.  The goal here is to have each site completely contained in a single directory with nginx logs, gunicorn logs, static files, and your source code.  *This makes it trivial to move your site to a new server using anouman.*         

Your site should now be running behind nginx/gunicon with static files properly being servered, however you still have a few steps remaining before everything will work correctly.
    
**STep 4:** Ensure your database settings are correct.

Your site should now be deployed into a directory called */home/anouman/example.com*.  Your original django project can be found in *example.com/src*.  Please update the DATABASE section of settings.py so that it points to your database. If it was a MySQL or Postgres DB running on localhost then you may only need to populate the database.  If it was MySQL or Postgres on a remotely accessible database then you likely have nothing to do.

If you are using an sqlite database then I recommend you create example.com/DB and copy your sqlite database into this directory.  If you are following along with the tutorial then you would change the DATABASE NAME section in your settings.py file to  /home/anouman/example.com/DB/{name_of_your_db}
    
**Step 5**  Explore Anouman Shell Commands

Assuming you updated and sourced .bash_profile at the end of the deployment step you will now have a few shell commands that were appended to the end of your sites virtualenv activate script which is locate in .  For instance to check the status of gunicorn/nginx type:

    site status
    
Now let's bring it up..

    site start
    
Likewise you can stop your site with:

    site stop
    
Go ahead and bring the site back up:

    site start
    
You can force nginx to do a reload with:

    site reload

These site management commands are specific to the site curently being worked on.  If you install another django project Anouman will gladly set it up for you and ensure that nginx properly directs traffic to the appropriate django back end and it's all managed with virtualenv and virtualenvwrapper.  To switch between sites deployed with Anouman is as simple as switching wrapped virtualenv's.  For ex:  workon example.com, workon site2.com, etc.

**Step 6:**  Adjust client */etc/hosts* file to simulate DNS for your web site.  

First make sure your site is running (see step 5).  Next, add the following line to your */etc/hosts*.

    192.168.100.100   www.example.com   example.com
    
If you setup another site, say site2.com, on the same server then you would add another line to /etc/hsots

    192.168.100.100 www.site2.com   site1.com
    
NGINX will now properly direct traffic based on the URL to the correct gunicorn/django backend as well as server the correct static files for the given project. 

**Step 7:** Now point your browser to example.com and you should see your django website.  Enjoy. 

Anouman Overview
================

Anouman is a django site deployment tool that is designed to greatly
simplify the process of deploying
`Django <https://www.djangoproject.com/>`__ projects behind
`gunicorn <http://gunicorn.org/>`__/`nginx <http://nginx.com/>`__. In
the spirit of reusing great open source software Anouman makes use of
`virtualenv <https://pypi.python.org/pypi/virtualenv>`__,\ `virtualenvwrapper <http://virtualenvwrapper.readthedocs.org/en/latest/>`__,
and of course `django <https://www.djangoproject.com/>`__ to help manage
the process of deploying your django instances.

The easiest way to become familiar with Anouman is to dive in and use it
by following along with the tutorial below. However, before you begin
you will first need to install `vagrant <http://www.vagrantup.com/>`__
and `virtualbox <https://www.virtualbox.org/>`__. You will be using
these tools to build a fresh Ubuntu VM to test your django deployment
on.

**Disclaimer:** *Anouman is still very much alpha stage software. As
such it has only been tested on Ubuntu 12.04 using the BASH shell. I'd
love to hear from others if they get this working in other OS/SHELL
combinations.*

Install Anouman
---------------

::

    pip install anouman

Virtual Machine Creation and Provisioning
-----------------------------------------

**Step 1:** VM Creation

::

    anouman --vm test1

This command uses vagrant to create and spin up a virtual machine in a
directory called test1. As part of the process it created a user
*anouman* with sudo privileges and password *anouman*. To login use:

::

    ssh anouman@192.168.100.100  # Password *anouman*

**Step 2:** Final provisioning

If you are using mysql or
`Postgres <http://www.postgresql.org/download/linux/ubuntu/>`__ you will
need to install them now. For mysql

::

    sudo apt-get install mysql-server

You will then need to login to the mysql server and create the
appropriate database for your django project

If you are using Postgres you will need to follow a similar protocal to
setup your Postgres database

Assuming this worked then you are ready to walk through the anouman
tutorial and deploy your django project on a fresh virtual machine.

Anouman Setup and Deployment Tutorial
-------------------------------------

Section 1: Packaging
~~~~~~~~~~~~~~~~~~~~

**Step 1:** Switch to the python virtualenv you use for development. You
are using `virtualenv <http://www.virtualenv.org/en/latest/>`__ for
python development right? If not Anouman should still work with your
python system packages.

::

        source /path/to/your/virtualenv/activate
        pip install anouman

**Step 2:** Update your django settings file to reflect the Virtual
Machine you are about to deploy it on.

First set your database HOST to match the ip address of the virtual
machine you created above. In you django settings.py file make sure the
HOST portion of your DATABASE section has the following:

::

    'HOST': '192.168.100.100'

Next we need to ensure that STATIC\_ROOT and MEDIA\_ROOT are set
correctly in your settings.py file. I recommend installing into the
anouman package location... For example if your domain name is
*site1.com* and your deployment user is *anouman* then I reccomend
updating your settings.py file with the following:

::

        STATIC_ROOT=/home/anouman/site1.com/static_root
        MEDIA_ROOT=/home/anouman/site1.com/media_root
        

Now when you run *manage.py collectstatic* your site will stay bundled
up in one nice neat directory, which turns out to be incredibly useful
if you want to deploy and manage more than one site...

**Step 3:** Next you will create an anouman package that will be
deployable on an anouman loaded server. Start by navigating to the
directory containing your django project. This is the directory you
originally ran "django-admin.py startproject" from and type the
following.

::

        anouman --django-project={path to your change project} --domainname=example.com

Behind the scenes your django project was copied into a directory named
site1.com/src. Inside this directory is another file which contains a
listing of python packages you are using for your django projects. This
was determiend from the output of "pip freeze"

Section2: Deploying
~~~~~~~~~~~~~~~~~~~

**Step 4:** Scp your project to the virtual machine we created above and
then log in.

::

        scp site1.com.tar.gz  anouman@192.168.100.100:/home/anouman
        
        ssh anouman@192.168.100.100

**Step 5:** Install anouman into the servers system python repository.

::

        sudo pip install anouman

**Step 6:** Setup anouman and deploy your new project. The first time
you run anouman, with or without arguments, it will install itself. For
the sake of this tutorial we will do both setup and deployment with one
command.

::

        anouman --deploy site1.com.tar.gz

The first time you call anouman it will download and install
virtualenv/virtualenvwrapper and create a wrapped 'anouman' virtualenv
and a wrapped 'example.com' virtualenv.

**Step 7:** We now want to update your .bash\_profile so the bash
environment for your site is loaded on login. To do this add the
following lines to the end of your .bash\_profile. If you don't have a
.bash\_profile in your home directory create one.

::

    source /usr/local/bin/virtualenvwrapper.sh
    workon site1.com

Now load the new environment:

::

    source ~/.bash_profile

**Step 8:** You now have a few shell commands that were appended to the
end of your sites virtualenv activate script. For instance to check the
status of gunicorn/nginx type:

::

    site status

Now let's bring it up..

::

    site start

Likewise you can stop your site with:

::

    site stop

and you can force nginx to do a reload with:

::

    site reload

These site management commands are specific to the site curently being
worked on. If you install another django project anouman will gladly set
it up for you and ensure that nginx properly directs traffic to the
appropriate django back end and it's all managed with virtualenv and
virtualenvwrapper. To switch between sites deployed with anouman is as
simple as switching wrapped virtualenv's. For ex: workon example.com,
workon site2.com, etc.

**Step 9:** Adjust client /etc/hosts file to simulate DNS for your web
site. First make sure your site is running (see step 8). Next, add the
following line to your /etc/hosts

::

    192.168.100.100   www.site1.com   site1.com

**Step 10:** Now point your browser to site1.com and you should see your
django website. Enjoy.

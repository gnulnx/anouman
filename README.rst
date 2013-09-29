Anouman Overview
================

Anouman is a django site deployment tool that is designed to greatly
simplify the process of deploying
`Django <https://www.djangoproject.com/>`__ projects behind
`gunicorn <http://gunicorn.org/>`__/`nginx <http://nginx.com/>`__. In
the spirit of reusing great open source software Anouman makes use of
`virtualenv <https://pypi.python.org/pypi/virtualenv>`__/`virtualenvwrapper <http://virtualenvwrapper.readthedocs.org/en/latest/>`__
to help manage the process of deploying your django instances.

The easiest way to become familiar with Anouman is to dive in and use it
by following along with the tutorial below. However, before you begin
you will first need to install `vagrant <http://www.vagrantup.com/>`__
and `virtualbox <https://www.virtualbox.org/>`__. We will be using these
tools to build a fresh Ubuntu VM to test your django deployment on.

**Disclaimer:** *Anouman is still very much alpha stage software. As
such it has only been tested on Ubuntu 12.04 using the BASH shell. I'd
love to hear from others if they get this working in other OS/SHELL
combinations.*

Virtual Machine Creation and Provisioning
-----------------------------------------

**Step 1:** VM creation. Hopefully by now you have vagrant and virtual
box both installed. Next you should create a directory called 'site1'
and place the following vagrant settings into a file named
*'Vagrantfile'*

::

    # -*- mode: ruby -*-
    # vi: set ft=ruby :

    # Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
    VAGRANTFILE_API_VERSION = "2"

    Vagrant.configure(VAGRANTFILE_API_VERSION) do |config| 
      # Every Vagrant virtual environment requires a box to build off of. 
      config.vm.box = "site1" 

      # The url from where the 'config.vm.box' box will be fetched if it 
      # doesn't already exist on the user's system. 
      config.vm.box_url = "http://files.vagrantup.com/precise64.box" 

      # Run bootstrap.sh provisioning script 
      config.vm.provision :shell, :path => "bootstrap.sh" 

      # Create a private network, which allows host-only access to the machine 
      # using a specific IP. 
      # config.vm.network :private_network, ip: "192.168.33.10"  

      # Create a public network, which will make the machine appear as another 
      #physical device on your network. 
      config.vm.network :public_network 

      #config.vm.provider :virtualbox do |vb| 
      # # Don't boot with headless mode 
      #  vb.gui = true 
      # 
      #  # Use VBoxManage to customize the VM. For example to change memory: 
      #  vb.customize ["modifyvm", :id, "--memory", "1024"] 
      #end 
    end

**Step 2:** Next you will create a simple bootstrap provision file to
use with vagrant VM. Copy the following into a file called
*'bootstrap.sh'* in the same directory as your Vagrantfile.

::

    #!/usr/bin/env bash
    sudo apt-get update                         # Update apt-get
    sudo apt-get install -yf vim                # VIM because VI isn't as cool
    sudo apt-get install -yf git                # install git
    sudo apt-get install -yf nginx              # install nginx
    sudo apt-get install -yf mysql-client       # only install mysql command line client
    sudo apt-get install -yf libmysqlclient-dev # needed for django mysql integration

    ### PYTHON STUFF
    sudo apt-get install -yf python-setuptools
    sudo apt-get install -yf python-virtualenv
    sudo apt-get install -yf python-dev
    sudo apt-get install -yf build-essential

**Step 3:** Power on your virtual machine and finish setting it up:

::

    vagrant up

When vagrant finishes powering up, log into your VM with:

::

    vagrant ssh

Next you should create a new user for deplying your django project. If
you want to follow along closely with this tutorial then create a user
name *'anouman'*.

::

    sudo adduser anouman

Next you will want to give your new user sudo privileges, by editing
/etc/sudoers and adding the following line:

::

    anouman ALL=(ALL:ALL) ALL  

directly below the line that says:

::

    root    ALL=(ALL:ALL) ALL

Next you need to make sure your server has the appropriate database
software installed. This tutorial will assume you are using MySQL since
the provision script above already installed mysql-client you only need
to install mysql-server.

::

    sudo apt-get install mysql-server

Now we will use ifconfig to determine the public ip address of your new
server.

::

    ifconfig

Remember this information because you know want to logout and log back
in as your new user.

::

    exit
    ssh anouman@your.vm.ip.address

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

First set your database host to match the ip address of the virtual
machine you created above. For example if your virtual machine ip is
10.0.1.15 then make sure you have the following in the DATABASES section
of your settings file:

::

    'HOST': '10.0.1.15'

Next we need to ensure that STATIC\_ROOT and MEDIA\_ROOT are set
correctly in your settings.py file. I recommend installing into the
anouman package location... For example if your domain name is
*example.com* and your deployment user is *anouman* then I reccomend
updating your settings.py file with the following:

::

        STATIC_ROOT=/home/anouman/example.com/static_root
        MEDIA_ROOT=/home/anouman/example.com/media_root
        

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
example.com/src. Inside this directory is another file which contains a
listing of python packages you are using for your django projects. This
was determiend from the output of "pip freeze"

Section2: Deploying
~~~~~~~~~~~~~~~~~~~

**Step 4:** Scp your project to the virtual machine we created above.

::

        scp example.com.tar.gz  anouman@your.vm.ip.address:/home/anouman

**Step 5:** Install anouman into the servers system python repository.

::

        sudo pip install anouman

**Step 6:** Setup anouman and deploy your new project. The first time
you run anouman, with or without arguments, it will install itself. For
the sake of this tutorial we will do both setup and deployment with one
command.

::

        anouman --deploy example.com.tar.gz

The first time you call anouman it will download and install
virtualenv/virtualenvwrapper and create a wrapped 'anouman' virtualenv
and a wrapped 'example.com' virtualenv.

**Step 7:** We now want to update your .bash\_profile so the bash
environment for your site is loaded on login. To do this add the
following lines to the end of your .bash\_profile. If you don't have a
.bash\_profile in your home directory create one.

::

    source /usr/local/bin/virtualenvwrapper.sh
    workon example.com

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

    your.site.ip.address   www.example.com   example.com

**Step 10:** Now point your browser to example.com and you should see
your django website. Enjoy.

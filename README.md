Anouman Overview
================

Anouman is a django site deployment tool that is designed to greatly simplify the process of deploying django projects behind gunicorn/nginx.  In the spirit of reusing great open source software Anouman makes use of virtualenv/virtualenvwrapper to help manage the process of deploying your django instances.  

The easiest way to become familiar with Anouman is to dive in and use it by following along with the tutorial below.  Before you begin you will first need to install [vagrant](http://www.vagrantup.com/) and [virtualbox](https://www.virtualbox.org/).  We will be using these tools to build a fresh Ubuntu VM to test your django deployment on.

*Anouman is still very much alpha stage software.  As such it has only been tested on Ubuntu 12.04 using the BASH shell.  I'd love to hear from others if they get this working in other OS/SHELL combinations.* 


Virtual Machine Creation and Provisioning
-----------------------------------------


**Step 1:** VM creation.  Hopefully by now you have vagrant and virtual box both installed.  What you should do next is create a directory called 'site1' and then place the following contents into a file named 'Vagrantfile'

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

**Step 2:** Copy the following information into a file called 'bootstrap.sh' in the same directory as your Vagrantfile.   This will give us basic provisioning of our new system.  

    #!/usr/bin/env bash
    sudo apt-get update                         # Update apt-get
    sudo apt-get install -yf vim                #VIM because VI isn't cool
    sudo apt-get install -yf git                # install git
    sudo apt-get install -yf nginx              # install nginx
    sudo apt-get install -yf mysql-client       #only install mysql command line client
    sudo apt-get install -yf libmysqlclient-dev # needed for django mysql integration

    ### PYTHON STUFF
    sudo apt-get install -yf python-setuptools
    sudo apt-get install -yf python-virtualenv
    sudo apt-get install -yf python-dev
    sudo apt-get install -yf build-essential


**Step 3:** Power on your virtual machine and finish setting it up:

    vagrant up
    
When vagrant finishes powering up, log into your VM with:

    vagrant ssh
    
Now we want to add a user that we will use to deploy our django projects.

    sudo adduser anouman
    
Next we want to go ahead and give our new user sudo privileges, by editing /etc/sudoers and adding the following line:
    
    anouman ALL=(ALL:ALL) ALL  
    
directly below the line that say's:

    root    ALL=(ALL:ALL) ALL

Now we will use ifconfig to determine the public ip address of our new server.

    ifconfig
    
Remember this information because we now want to log out and then log back in as the user anouman:

    exit
    ssh anouman@your.ip.address
    
Assuming this worked then you are ready to walk through the anouman tutorial and in the process deploy your django project on a fresh virtual machine.



Setup and Deployment Tutorial
-----------------------------

### Section 1:  Packaging

**Step 1:** Switch to the python virtualenv you use for development.
        You are using virtualenv for python development right?  If not Anouman should still work
        with your python system packages.

        source /path/to/your/virtualenv/activate
        pip install anouman

**Step 2:** Create an anouman package that will be deployable on an anouman loaded
        server.  Start by navigating to the directory containing your django project.
        This is the directory you originall ran "django-admin.py startproject".
        

        anouman --django-project={path to your change project} --domainname=example.com

        What just happened behind the scenes was your django project was copied into a directory named
        example.com. Inside this directory is another file which contains a listing of your django projects 
        python packages generated from the output of:  pip --freeze 

### Section2:  Deploying

**Step 3:** Scp your project to virtual machine we created above.

        scp www.example.com.tar.gz  anouman@www.example.com:/home/anouman

**Step 4:** Install anouman into the servers system python repository.

        sudo pip install anouman

**Step 5:** Setup  anouman and deploy your new project.   The first time you run anouman, with or without arguments, it will install itself.  For the sake of this tutorial we will do both setup and deployment with on command.

        anouman --depoly=example.com.tar.gz

The first time you call anouman it will download and install virtualenv/virtualenvwrapper and create a wrapped 'anouman' virtualenv and a wrapped 'example.com' virtualenv.

**Step 6:** Restart your server to bring everything online.  If you are using vagrant to follow along you may need to give the server a minute or two after calling 'vagrant up' returns before your website comes on line.  There seems to be either a bug in virtualbox or vagrant with host networking at times...

    exit  
    vagrant halt
    vagrant up
    
              
**Step 7**  modify your /etc/hosts file to reflect the domainname/ip address of your server.  For example if your ipaddress is 10.0.1.12 and your domainname is *example.com*  then add the following line to your /etc/hosts file.

    10.0.1.12   www.example.com   example.com


If everything works as expected you should be able to point your browser to the ip address of your virtual machine

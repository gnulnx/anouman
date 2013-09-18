anouman
======

A django wrapper designed to setup django project so they are easily deployable with nginx/gunicorn


Step 1: Switch to the python environment you use for development.
        Many people use virtualenv to contain all of their django related
        python packages in one place.  If you do so then first change to your virtual env.
        Now install anouman.

        pip install anouman

Step 2: Create an anouman package that will be deployable on an anouman loaded
        server.

        anouman --django-project={path to your change project} --domainname=www.example.com

        What just happened behind the scense was your project was copied into a directory named
        www.example.com. Inside this directory is another file which contains a listing of your 
        projects python packages generated from the output of:  pip --freeze 

Step 3: Scp your project to the server

        scp www.example.com.tar.gz  username@www.example.com:/home/username

Step 4: Install anouman into the system python repository.

        sudo pip install anouman

Step 5: Setup your anouman and deploy your new project

        anouman --depoly=www.domain.example.com.tar.gz


              

Anouman Overview
======

Anouman is a django site deployment tool that is designed to greatly simplify the process of deploying django projects behind gunicorn/nginx.  The following tutorial assumes you have a fresh ubuntu server at your disposal and to achieve this we recomment setting up vagrant with virtualbox




**Step 1:** Switch to the python virtualenv you use for development.
        You are using virtualenv for python developmen right?  If not anouman should still work
        with your python system packages.

        source /path/to/your/virtualenv/activate
        pip install anouman

**Step 2:** Create an anouman package that will be deployable on an anouman loaded
        server.  Start by navigating to the directory containing your django project.
        This is the directory you originall ran django-admin.y --startproject.
        

        anouman --django-project={path to your change project} --domainname=example.com

        What just happened behind the scenes was your project was copied into a directory named
        example.com. Inside this directory is another file which contains a listing of your 
        projects python packages generated from the output of:  pip --freeze 

**Step 3:** Scp your project to the server

        scp www.example.com.tar.gz  username@www.example.com:/home/username

**Step 4:** Install anouman into the system python repository.

        sudo pip install anouman

**Step 5:** Setup your anouman and deploy your new project

        anouman --depoly=www.domain.example.com.tar.gz

**Step 6:** Restart your server to bring everything online
              

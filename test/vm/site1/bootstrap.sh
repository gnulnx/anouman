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

#!/usr/bin/env bash
# Setup anouman user
sudo useradd --shell /bin/bash --home /home/anouman anouman
echo -e "anouman\\nanouman\\n" | sudo passwd anouman
sudo usermod --groups admin anouman
sudo mkdir /home/anouman
sudo chown -R anouman:anouman /home/anouman

sudo apt-get update                         # Update apt-get
sudo apt-get install -yf vim                # VIM because VI isn't as cool
sudo apt-get install -yf git                # install git

### PYTHON STUFF
sudo apt-get install -yf python-setuptools
sudo apt-get install -yf python-virtualenv
sudo apt-get install -yf python-dev
sudo apt-get install -yf build-essential

{% if NGINX %}
sudo apt-get install -yf nginx              # install nginx
{% endif %}

{% if MYSQL %}
sudo apt-get install -yf mysql-client       # only install mysql command line client
sudo apt-get install -yf libmysqlclient-dev # needed for django mysql integration
{% endif %}

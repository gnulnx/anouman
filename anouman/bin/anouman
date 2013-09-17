#!/usr/bin/env bash

USER=`whoami`
if [ $USER == 'root' ];
then
    echo "You need to run this as a normal mode user"
    exit
fi

function setup {
    cd ~/

    sudo pip install virtualenvwrapper

    source /usr/local/bin/virtualenvwrapper.sh;
    echo "source /usr/local/bin/virtualenvwrapper.sh;" >> .bash_profile
    echo "source /usr/local/bin/anouman-setup.sh" >> .bash_profile
    echo "workon anouman" >> .bash_profile

    mkvirtualenv anouman;
    workon anouman;

    pip install django

    lssitepackages
}

if [ ! -d ".virtualenvs/anouman" ]; then
    setup
fi

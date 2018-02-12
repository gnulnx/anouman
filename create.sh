#!/usr/bin/env bash

# Create multipel droplets simulatneously by calling like:
#
#./create.sh test1 test2 test 3
#
# NOTE: The jobs are all backgrounded to the system.
#
# You can monitor the job with ./list.sh

# Help
if [ "$1" == "--help" ] 
then
    ./manage.py create_droplet --help
    exit 1
fi

# Create Droplets
for var in "$@"
do
    echo "Spinning up: $var"
    ./manage.py create_droplet --name $var --monitoring --private --settings=anouman.local &
done

#!/usr/bin/env bash
for var in "$@"
do
    echo "Spinning up: $var"
    ./manage.py create_droplet --name $var --monitoring --private --settings=anouman.local &
done

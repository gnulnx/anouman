#!/usr/bin/env bash

./manage.py create_droplet --name $1 --monitoring --private --settings=anouman.local

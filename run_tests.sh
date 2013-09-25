#!/usr/bin/env bash

workon anouman

/usr/bin/yes | python -m unittest discover -v > /dev/null

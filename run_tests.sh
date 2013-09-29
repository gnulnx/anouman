#!/usr/bin/env bash

#############################################
#                                           #
#   Simple Test Driver                      #
#                                           # 
#   ./run_tests  -q (queit)  -f (failfast)  #
#############################################

#QUEIT=""
#if [[ "$@" == *-q* ]]; then
#    QUEIT=" > /dev/null"
#fi
#
#FAILFAST=""
#if [[ "$@" == *-f* ]]; then
#    FAILFAST=" --failfast "
#fi
#
#VERBOSE=""
#if [[ "$@" == *-v* ]]; then
#    VERBOSE=" -v "
#fi
#
#echo "/usr/bin/yes | python -m unittest discover $VERBOSE $FAILFAST  $QUEIT"
#exec /usr/bin/yes | python -m unittest discover $VERBOSE $FAILFAST $QUEIT



if [[ "$@" == *-q* ]];
then
    if [[ "$@" == *-f* ]];
    then
        /usr/bin/yes | python -m unittest discover -v --failfast  > /dev/null
    else
        /usr/bin/yes | python -m unittest discover -v > /dev/null
    fi
else
    if [[ "$@" == *-f* ]];
    then
        /usr/bin/yes | python -m unittest discover -v --failfast
    else
        /usr/bin/yes | python -m unittest discover -v 
    fi
fi

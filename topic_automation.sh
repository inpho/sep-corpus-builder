#!/bin/bash
SEASONYEAR=$1
SEASON=${SEASONYEAR::-4}
YEAR=${SEASONYEAR#$SEASON}

case $SEASON in
  'win') SEASONDESC='Winter';;
  'spr') SEASONDESC='Spring';;
  'sum') SEASONDESC='Summer';;
  'fall') SEASONDESC='Fall';;
esac

DESC="Stanford Encyclopedia of Philosophy ($SEASONDESC $YEAR)"
INI="sep.$SEASONYEAR.ini"

set -x    # enable command trace
set -e    # exit on first error

# python build.py $SEASONYEAR -o /tmp/sep.$SEASONYEAR
# topicexplorer init --name $DESC data_$SEASONYEAR $INI
# topicexplorer prep $INI --high .25 --low .1 --lang en -q
# topicexplorer train $INI -k 20 40 60 80 100 120 --iter 1000 -p 8 -q
# topicexplorer export -o /tmp/sep.$SEASONYEAR.tez $INI
# aws s3 cp /tmp/sep.$SEASONYEAR.tez s3://hypershelf/sep.$SEASONYEAR.tez --acl bucket-owner-full-control

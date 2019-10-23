#!/bin/bash
if [[ -z $1 || -z $2 ]]
then
  echo "usage: start.sh spiderName url1,url2"
else
  scrapy crawl $1 -a start_url=$2 
fi
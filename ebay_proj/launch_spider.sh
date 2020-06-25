#!/bin/bash

cd ~/ebay_proj
filename=$1'_'$(date +'%y%m%d')'.json'
# echo $filename
filename=${filename// /_}
rm -f './scraped_json/'$filename

scrapy crawl ebay -o './scraped_json/'$filename -a product="$1"

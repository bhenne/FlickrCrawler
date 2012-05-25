#!/bin/bash

#file1=flickr_data/FlickrDataset.txt #DS1
file1=flickr_data/FlickrDataset2.txt #DS1 with Make
file2=flickr_data/FlickrDataset_mobile.txt #DS2

columns=`head -n 1 $file1`
c=`echo $columns | sed 's/;/ VARCHAR(255), /g;' | sed 's/#//;' | sed 's/\./_/g;' | sed 's/\./_/g;'`

tail -n 20834 $file1 | head -n 20000 >/tmp/Flickrdatamysql1
tail -n 3258 $file2 | head -n 3000 >/tmp/Flickrdatamysql2

#tail -n 20834 $file1 >/tmp/Flickrdatamysql1
#tail -n 3258 $file2 >/tmp/Flickrdatamysql2


echo "DROP DATABASE IF EXISTS FlickrDataset; CREATE DATABASE FlickrDataset DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci; USE FlickrDataset; CREATE TABLE DS1 ( $c VARCHAR(255) ); LOAD DATA LOCAL INFILE '/tmp/Flickrdatamysql1' INTO TABLE DS1 FIELDS TERMINATED BY ';'; CREATE TABLE DS2 ( $c VARCHAR(255) ); LOAD DATA LOCAL INFILE '/tmp/Flickrdatamysql2' INTO TABLE DS2 FIELDS TERMINATED BY ';';" | mysql -u root -p

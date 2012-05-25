#!/bin/bash

file1=flickr_data/Flickr_manPplcount_20k.csv #DS1
file2=flickr_data/Flickr_manPplcount_3k.csv #DS2

c="filename VARCHAR(255), pplcount VARCHAR(3)"

cp $file1 /tmp/flickr_count_foo1
cp $file2 /tmp/flickr_count_foo2


echo "USE FlickrDataset; DROP TABLE IF EXISTS DS1pplcount; CREATE TABLE DS1pplcount ( $c ); LOAD DATA LOCAL INFILE '/tmp/flickr_count_foo1' INTO TABLE DS1pplcount FIELDS TERMINATED BY ';'; DROP TABLE IF EXISTS DS2pplcount; CREATE TABLE DS2pplcount ( $c ); LOAD DATA LOCAL INFILE '/tmp/flickr_count_foo2' INTO TABLE DS2pplcount FIELDS TERMINATED BY ';';" | mysql -u root -p

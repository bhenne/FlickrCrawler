#!/bin/bash

file1=flickr_data/Flickr_users_unicode.txt #DS1 users
file2=flickr_data/Flickr_exif_denied_list.txt #DS1 exif denied
file3=flickr_photos/DS1_photo_owners.csv #DS1 photo owners

c="username VARCHAR(255), ispro VARCHAR(25), realname VARCHAR(255), path_alias VARCHAR(255), id VARCHAR(255), nsid VARCHAR(255), location VARCHAR(255), p_count VARCHAR(255), p_firstdate VARCHAR(255), p_firstdatetaken VARCHAR(255)"
c2="nsid VARCHAR(255), exifaccess VARCHAR(255), msg VARCHAR(255)"

c3="nsid VARCHAR(255), photo_id VARCHAR(255), photo_secret VARCHAR(255), photo_farm VARCHAR(255), photo_server VARCHAR(255), photo_title VARCHAR(255)"

cp $file1 /tmp/flickr_db_foo
cp $file2 /tmp/flickr_exif_foo
cp $file3 /tmp/flickr_owner_foo


echo "USE FlickrDataset; DROP TABLE IF EXISTS DS1users; CREATE TABLE DS1users ( $c ); LOAD DATA LOCAL INFILE '/tmp/flickr_db_foo' INTO TABLE DS1users FIELDS TERMINATED BY ';'; DROP TABLE IF EXISTS DS1exifaccess; CREATE TABLE DS1exifaccess ( $c2 ); LOAD DATA LOCAL INFILE '/tmp/flickr_exif_foo' INTO TABLE DS1exifaccess FIELDS TERMINATED BY ';'; DROP TABLE IF EXISTS DS1owners; CREATE TABLE DS1owners ( $c3 ); LOAD DATA LOCAL INFILE '/tmp/flickr_owner_foo' INTO TABLE DS1owners FIELDS TERMINATED BY ';';" | mysql -u root -p

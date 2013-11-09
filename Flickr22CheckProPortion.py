import os
import csv

import Flickr20CheckDataset
import Flickr21CheckUser_1to1

userlistpath = '/Users/henne/research_data/LocrFlickr_datasets1/flickr-files'
userlistfiles = [ 'Flickr_users_unicode.txt', 'Flickr_users_mobile_unicode.txt', 'Flickr_users_mobile_unicode.txt.FULL' ] 

pros = {}
for userfile in userlistfiles:
    csvReader = csv.reader(open(os.path.join(userlistpath,userfile), 'rt'), delimiter=';')
    for row in csvReader:
        if len(row) < 6:
            continue
        elif len(row) > 10:
            #row = (";".join(row)).replace(",",";").split(";")  #: for testing broken lines for location
            row2 = row[0:-3]
            first_ad = -1
            second_ad = -1
            last_ad = -1
            for i in range(len(row2)-1, 0, -1):
                if row2[i].find('@') > 0:
                    if last_ad == -1:
                        last_ad = i
            melted_loco = ";".join(row2[last_ad+1:])
            remainder = row2[:last_ad+1]
            boolpos = -1
            for i in range(len(remainder)-1, 0, -1):
                if remainder[i] == 'True' or remainder[i] == 'False':
                    boolpos = i
            pos0 = [";".join(remainder[:boolpos])]
            pos1 = [remainder[boolpos]]
            pos2 = [";".join(remainder[boolpos+1:-3])]
            secondlast = remainder[-3:]
            last = row[-3:]

            newrow = pos0 + pos1 + pos2 + secondlast + last
            row = newrow

        id = row[4]
        nsid = row[5]
        if row[1] == 'True':
            ispro = True
        elif row[1] == 'False':
            ispro = False
        else: # if there is one ; in the user name...
            if row[2] == 'True':
                ispro = True
            elif row[2] == 'False':
                ispro = False
            else:
                raise ValueError('%s is no boolean value' % row[1])
        if nsid not in pros:
            pros[nsid] = ispro 

users = Flickr21CheckUser_1to1.owners.keys()
print 'user:', len(users)
print 'account data:', len(pros)

pro = 0
nopro = 0
err = 0
notex = 0
for u in users:
    if u in pros:
        if pros[u] == True:
            pro += 1
        elif pros[u] == False:
            nopro += 1
        else:
            err += 1
    else:
        notex += 1

print 'pro: %s (%s), no pro: %s (%s), err: %s, not found: %s' % (pro, round(100.0/len(users)*pro, 1), nopro, round(100.0/len(users)*nopro, 1), err, notex)

orig = 0
other = 0
for f in os.listdir(Flickr20CheckDataset.imagepath):
    if f.lower().endswith('.jpg') or f.lower().endswith('.jpeg'):
        pre = f.rpartition('.')[0]
        if pre.endswith('_o'):
            orig += 1
        else:
            other += 1

print 'original files: %s (%s), other: %s (%s)' % (orig, round(100.0/(orig+other)*orig, 1), other, round(100.0/(orig+other)*other, 1))


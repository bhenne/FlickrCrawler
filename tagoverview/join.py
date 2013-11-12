"""Joins all files linked at http://www.exiv2.org/metadata.html
to a single big file with all tags supported by exiv2"""

import os

allcontent = """<html>
<head>
 <title>All Exiv2 0.23 tags</title>
 <link type="text/css" rel="stylesheet" href="http://www.exiv2.org/include/default.css">
 <link type="text/css" rel="stylesheet" href="http://www.exiv2.org/include/sortabletable.css">
</head>
<body>
<h1>All Exiv2 0.23 tags</h1>
"""

filelist = sorted(os.listdir("."))
filelist.remove('tags.html')
filelist.insert(0, 'tags.html')

for fname in filelist:
   if fname == 'Exiv2-tags.html' or fname.endswith('.html') == False:
       continue
   f = open(fname, 'rt')
   print "reading %s" % fname
   content = False
   for line in f:
       if content == True:
           if line.find('</table>') > -1:
               line = line.replace('<script type="text/javascript">', '')
           allcontent += '%s' % line
       if line.find('<h1>Image metadata library') > -1:
           content = True
       elif line.startswith('<p>Click on a column header to sort'):
           content = True
       elif line.find('</table>') > -1:
           content = False
   f.close()

allcontent += """</body>
</html>
"""

f = open('Exiv2-tags.html', 'wt')
f.write(allcontent)
f.close()

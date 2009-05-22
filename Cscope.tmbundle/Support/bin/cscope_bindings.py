#encoding: utf-8
#!/usr/bin/python

import os
from popen2 import popen2

TM_BUNDLE_PATH = os.environ['TM_BUNDLE_SUPPORT']
CSCOPE_BIN = '"' + TM_BUNDLE_PATH + '/bin/cscope"'
CSCOPE_COMMAND = os.environ['CSCOPE_COMMAND']

def build():
	os.chdir(os.environ['TM_PROJECT_DIRECTORY'])
	find_cmd = "find . -name \\*\.c -o -name \\*\.h -o -name \\*\.m -o -name \\*\.java -o -name \\*\.py > tm_cscope.files;"
	os.system(find_cmd + CSCOPE_BIN + " -b;")
	print 'Cscope DB built'

if int(CSCOPE_COMMAND) == -1:
  build()
  exit(0)

command_names = ["Find C Symbol", "Find global definition", "Functions called by", "Functions calling", "", "", "", "", "Find files including"]

print """
<html>
  <head>
    <title>CSCOPE Output</title>
    <style>
      tr, td { font-size: 100%; padding: .25em; }
    </style>
  </head>
  <body>
"""

if int(CSCOPE_COMMAND) in range(0,8):
	try:
		search = os.environ['TM_CURRENT_WORD']
	except:
		print 'MOVE THE CURSOR OVER A WORD TO USE THIS FUNCTIONALITY'
		exit(0)
else:
	search = os.environ['TM_FILENAME']

print '<h2>CSCOPE - ', command_names[int(CSCOPE_COMMAND)], search, '</h2>'


CSCOPE_DIR = os.environ.get('TM_CSCOPE_DIR') or os.environ['TM_PROJECT_DIRECTORY']
os.chdir(CSCOPE_DIR)

cmd = CSCOPE_BIN + ' -d -L -' + CSCOPE_COMMAND + '"' + search + '"'
# print cmd
cscope_out, cscope_in = popen2(cmd)

# TODO: João add the javascript
print '<table><tr><th>File</th><th>Function</th></tr>'
for i in cscope_out.readlines():
	f, func, line, rest = i.split(' ', 3)
	if func != 'NULL':
		func = func.replace('<', '&lt;')
		func = func.replace('>', '&gt;')
	else:
		func = '---'
	link = '<a href="txmt://open?url=file://' + CSCOPE_DIR + '/' + f + '&line=' + line + '">'
	print '<tr><td>', link, f + ':' + line, '</a></td><td>', func, '</td></tr>'
print '</table>'

print '</body></html>'

#ps

#print [i for i in os.environ if i[0:2] == 'TM']
#print os.environ['TM_FILENAME']

#print CSCOPE_BIN
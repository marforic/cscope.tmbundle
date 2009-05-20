#!/usr/bin/python

import os
from popen2 import popen2

TM_BUNDLE_PATH = os.environ['TM_BUNDLE_SUPPORT']
CSCOPE_BIN = '"' + TM_BUNDLE_PATH + '/bin/cscope"'
CSCOPE_COMMAND = os.environ['CSCOPE_COMMAND']

if int(CSCOPE_COMMAND) == -1:
	os.chdir(os.environ['TM_PROJECT_DIRECTORY'])
	os.system("find . -name \\*\.c -o -name \\*\.h -o -name \\*\.m -o -name \\*\.java > cscope.files;" + 
				CSCOPE_BIN + " -b;" + "echo \"Cscope DB built\"")
	exit(0)


command_names = ["Find C Symbol", "Find global definition", "Functions called by", "Functions calling this", "", "", "", "", "Find files including"]

print '<html><head><title>CSCOPE Output</title></head><body>'

if int(CSCOPE_COMMAND) in range(0,8):
	try:
		search = os.environ['TM_CURRENT_WORD']
	except:
		print 'MOVE THE CURSOR OVER A WORD TO USE THIS FUNCTIONALITY'
		exit(0)
else:
	search = os.environ['TM_FILENAME']

print '<h1>CSCOPE - ', command_names[int(CSCOPE_COMMAND)], search, '</h1>'

os.chdir(os.environ['TM_PROJECT_DIRECTORY'])
cscope_out, cscope_in = popen2(CSCOPE_BIN + ' -L -' + CSCOPE_COMMAND + '"' + search + '"')

# TODO: João add the javascript
print '<table><tr><th>File</th><th>Function</th><th>Line #</th><th>Line</th></tr>'
for i in cscope_out.readlines():
	f, func, line, rest = i.split(' ', 3)
	if func != 'NULL':
		func = func.replace('<', '&lt;')
		func = func.replace('>', '&gt;')
	else:
		func = '---'
	link = '<a href="txmt://open?url=file://' + os.environ['TM_PROJECT_DIRECTORY'] + '/' + f + '&line=' + line + '">'
	print '<tr><td>', link, f, '</a></td><td>', func, '</td><td>', line, '</td><td>', rest, '</td></tr>'
print '</table>'

print '</body></html>'

#ps

#print [i for i in os.environ if i[0:2] == 'TM']
#print os.environ['TM_FILENAME']

#print CSCOPE_BIN
#encoding: utf-8
#!/usr/bin/python

import os
from popen2 import popen2

def build():
	os.chdir(os.environ['TM_PROJECT_DIRECTORY'])
	# TODO cleanup
	find_cmd = "find . -name \\*\.c -o -name \\*\.h -o -name \\*\.m -o -name \\*\.java -o -name \\*\.py > tm_cscope.files;"
	os.system(find_cmd + CSCOPE_BIN + " -b;")
	print 'Cscope DB built'


def get(search):
	os.chdir(CSCOPE_DIR)
	# TODO cleanup
	cmd = CSCOPE_BIN + ' -d -L -' + CSCOPE_COMMAND + '"' + search + '"'
	cscope_out, cscope_in = popen2(cmd)
	return cscope_out


# TODO replace HTML rendering with something else
def render(search, cscope_out):
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

	print '<h2>', command_names[int(CSCOPE_COMMAND)], search, '</h2>'

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


if __name__ == '__main__':
	
	CSCOPE_BIN = '"' + os.environ['TM_BUNDLE_SUPPORT'] + '/bin/cscope"'
	CSCOPE_COMMAND = os.environ['CSCOPE_COMMAND']
	CSCOPE_DIR = os.environ.get('TM_CSCOPE_DIR') or os.environ['TM_PROJECT_DIRECTORY']
	
	assert int(CSCOPE_COMMAND) in range(-1,8)
	
	if int(CSCOPE_COMMAND) == -1:
		build()
		exit(0)
		
	try:
		search = os.environ.get('TM_SELECTED_TEXT') or os.environ['TM_CURRENT_WORD']
	except:
		print 'No word selected.'
		exit(0)

	# TODO: handle filenames
	# search = os.environ['TM_FILENAME']
	
	cscope_out = get(search)
	render(search, cscope_out)
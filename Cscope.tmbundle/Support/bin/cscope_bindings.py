#encoding: utf-8
#!/usr/bin/python

import os, sys
# TODO use subprocess instead
from popen2 import popen2

def build():
    os.chdir(os.environ['TM_PROJECT_DIRECTORY'])
    # TODO cleanup
    # has to be cscope.files for cscope to use it, or the -i flag should be used: i.e. cscope -i tm_cscope.files
    find_cmd = "find . -name \\*\.c -o -name \\*\.h -o -name \\*\.m -o -name \\*\.java -o -name \\*\.py > tm_cscope.files;"
    # TODO return value
    os.system(find_cmd + CSCOPE_BIN + " -i tm_cscope.files -b;")
    print 'Cscope DB built'

def tm_open(path, line):
    cmd = 'mate -a ' + CSCOPE_DIR + '/' + path + ' --line=' + line
    cscope_out, cscope_in = popen2(cmd)
    return cscope_out

def get(search):
    os.chdir(CSCOPE_DIR)
    # TODO cleanup
    cmd = CSCOPE_BIN + ' -d -L -' + CSCOPE_COMMAND + '"' + search + '"'
    cscope_out, cscope_in = popen2(cmd)
    return cscope_out

# TODO replace HTML rendering with something else
def render_html(search, cscope_out):
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
        # TODO what happens if a file has a space in the name?
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

def choice(cscope_out):

    # TODO why isn't this in TM_SUPPORT_PATH??
    # sys.path.append(os.environ['TM_SUPPORT_PATH'])
    sys.path.append('/Applications/TextMate.app/Contents/SharedSupport/Support/lib')
    import dialog

    paths = []
    for i in cscope_out.readlines():    
        path, func, line, rest = i.split(' ', 3)
    
        # filter out current file
        if path in os.environ['TM_FILEPATH'] and line == os.environ['TM_LINE_NUMBER']:
            continue    
    
        full = (path, line)
        paths.append((path + ':' + line, full))
      
    if not paths:
        raise LookupError
  
    # TODO sort global def to top, local appearances
    paths.sort(key=lambda x: x[0])
  
    choice = dialog.menu(paths)
  
    if not choice:
        raise TypeError
  
    return choice

if __name__ == '__main__':
    
    sys.path.append('/Applications/TextMate.app/Contents/SharedSupport/Support/lib')
    import dialog

    CSCOPE_BIN = '"' + os.environ['TM_BUNDLE_SUPPORT'] + '/bin/cscope"'
    CSCOPE_COMMAND = os.environ['CSCOPE_COMMAND']
    CSCOPE_DIR = os.environ.get('TM_CSCOPE_DIR') or os.environ['TM_PROJECT_DIRECTORY']
  
    assert int(CSCOPE_COMMAND) in range(-1,9)
  
    if int(CSCOPE_COMMAND) == -1:
        build()
        exit(0)

    # up to now the only command for which we want to use the filenames is the find #includes
    # TODO: beautify the elif, maybe using an helper function?
    try:
        if (int(CSCOPE_COMMAND) == 8):
            search = os.environ['TM_FILENAME']
        elif (int(CSCOPE_COMMAND) == 0):
            search = dialog.get_string(title="Find C Symbol", prompt="Symbol:")
        elif (int(CSCOPE_COMMAND) == 4):
            search = dialog.get_string(title="Find this string text", prompt="Text:")
        elif (int(CSCOPE_COMMAND) == 6):
            search = dialog.get_string(title="Find this egrep expression", prompt="Regexp:")
        elif (int(CSCOPE_COMMAND) == 7):
            search = dialog.get_string(title="Find this file", prompt="Filename:")
        else:
            search = os.environ.get('TM_SELECTED_TEXT') or os.environ['TM_CURRENT_WORD']
    except:
        print 'No word selected'
        exit(1)
  
    if not search:
        exit(1)

    cscope_out = get(search)

    # TODO optionally configure HTML output??
     # render_html(search, cscope_out)
  
    try:
        path, line = choice(cscope_out)
    except LookupError:
        print 'Can\'t find "%s"' % search
        exit(1)
    except TypeError:
        # With the output as ToolTip we don't want to print this in case the user presses ESC
        #print 'No file selected'
        exit(1)

    tm_open(path, line)
      
    # TODO doctests
  

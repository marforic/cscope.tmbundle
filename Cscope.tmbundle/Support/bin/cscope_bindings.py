#encoding: utf-8
#!/usr/bin/python

import os, sys

try:
    import subprocess
except ImportError:
    subprocess = None
    from popen2 import popen2

# Add TextMate's support library to path and import the dialog module
# which we use to communicate back to TextMate
sys.path.append(os.path.join(os.environ['TM_SUPPORT_PATH'], "lib"))
import dialog

CSCOPE_FILE_LIST    = "tm_cscope.files"
CSCOPE_BIN          = os.path.join(os.environ['TM_BUNDLE_SUPPORT'], "bin", "cscope")
CSCOPE_COMMAND      = os.environ['CSCOPE_COMMAND']
CSCOPE_DIR          = os.environ.get('TM_CSCOPE_DIR') or os.environ['TM_PROJECT_DIRECTORY']

TEXTMATE_CMD        = ["mate", "-a"]
FILE_LIST_CMD       = ["find", ".", "-name", "*.c", "-o", "-name", "*.h",
                    "-o", "-name", "*.m", "-o", "-name", "*.java", "-o", "-name", "*.py"]
CSCOPE_BUILD_CMD    = [CSCOPE_BIN, "-i", CSCOPE_FILE_LIST, "-b"]
CSCOPE_RUN_CMD      = [CSCOPE_BIN, '-d', '-L']


def run_cmd(cmd):
    """
    Run command and return a stdout iterable.
    """
    if not subprocess:
        return run_cmd_popen2(cmd)

    output = []
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, cwd=CSCOPE_DIR)
    for line in p.stdout:
        output.append(line)

    return p.wait(), output

def run_cmd_popen2(cmd):
    """
    Run command using popen2 and return a dummy exit code an stdout iterable

    This is only here to support Python version without the subprocess module
    """
    os.chdir(CSCOPE_DIR)
    output = []
    stdout, stdin = popen2(prepare_popen2_cmd(cmd))

    for line in stdout:
        output.append(line)
    return 0, output

def prepare_popen2_cmd(cmd):
    """
    When using subprocess we want out command line and arguments to be
    specified as a list or tuple, but that doesn't quite work with
    popen2 or os.system. This function is by no means safe as we only
    join the arguments with a space and escape space/star.
    """
    cmd = [x.replace(" ", "\\ ") for x in cmd]
    cmd = [x.replace("*", "\\*") for x in cmd]
    return " ".join(cmd)

def build():
    """
    Build/rebuild the Cscope database
    """
    
    # First, we build a list of files for cscope to use. In a perfect world
    # we'd just use subprocess and pipe the stdout straight to a file, rather
    # than buffering everything up and then writing to file. But oh, well.
    exit_code, output = run_cmd(FILE_LIST_CMD)
    if exit_code:
        # TODO: Add some detail to the error message, such as what the user
        # could do about it.
        raise RuntimeError("Could not generate list of files for Cscope (%s: %s)" % (exit_code, output))

    file_list = file(os.path.join(CSCOPE_DIR, CSCOPE_FILE_LIST), "w")
    file_list.write("".join(output))
    file_list.close()

    # Then, we build the actual database
    exit_code, output = run_cmd(CSCOPE_BUILD_CMD)
    if exit_code:
        raise RuntimeError("Could not generate Cscope database (%s: %s)" % (exit_code, output))

    print 'Cscope DB built'

def tm_open(filename, line):
    """
    Open the file in TextMate at the specified line
    """
    cmd = TEXTMATE_CMD + [os.path.join(CSCOPE_DIR, filename), "--line=%s" % line]
    run_cmd(cmd)

def run_cscope(search):
    """
    Run the requested Cscope command and return the command output
    """
    cmd = CSCOPE_RUN_CMD + ['-%s' % CSCOPE_COMMAND, search]
    exit_code, output = run_cmd(cmd)
    if exit_code:
        raise RuntimeError("Could not run Cscope (exit code: %s)" % exit_code)
    return output


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

def choice_menu(cscope_out):
    """
    Display a dialog menu in TextMate with Cscope's output and wait for the
    user to choose a file to open.
    """
    paths = []
    for line in cscope_out:
        # TODO: What if the file has a space in its name? Switch to regexp?
        path, func, line, rest = line.split(' ', 3)
    
        # Filter out current file
        if path in os.environ['TM_FILEPATH'] and line == os.environ['TM_LINE_NUMBER']:
            continue    
    
        full = (path, line)
        paths.append((path + ':' + line, full))
      
    if not paths:
        raise LookupError
  
    # TODO sort global def to top, local appearances
    paths.sort(key=lambda x: x[0])
  
    # Display menu dialog in TextMate and wait for a choice
    choice = dialog.menu(paths)
  
    if not choice:
        raise TypeError
  
    return choice

if __name__ == '__main__':
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

    cscope_out = run_cscope(search)

    # TODO optionally configure HTML output??
     # render_html(search, cscope_out)
  
    try:
        path, line = choice_menu(cscope_out)
    except LookupError:
        print 'Can\'t find "%s"' % search
        exit(1)
    except TypeError:
        # With the output as ToolTip we don't want to print this in case the user presses ESC
        #print 'No file selected'
        exit(1)

    tm_open(path, line)
      
    # TODO doctests

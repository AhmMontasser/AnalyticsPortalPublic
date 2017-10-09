#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import datetime
import shutil
os.environ['TCL_LIBRARY'] = r'D:\Anaconda\pkgs\python-3.6.1-2\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'D:\Anaconda\pkgs\python-3.6.1-2\tcl\tk8.6'
from cx_Freeze import setup, Executable
#shutil.rmtree("build", ignore_errors=True)
#shutil.rmtree("Example", ignore_errors=True)
# This is ugly. I don't even know why I wrote it this way.
def files_under_dir(dir_name):
    file_list = []
    for root, dirs, files in os.walk(dir_name):
        for name in files:
            file_list.append(os.path.join(root, name))
    return file_list


includefiles = []
for directory in ('static', 'templates', 'data'):
    includefiles.extend(files_under_dir(directory))

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

dt = datetime.datetime.now()

main_executable = Executable("Main.py", base=base)
setup(name="D:\python_projects\DataAnalysisWebSite\Example",
      version="0.3." + dt.strftime('%m%d.%H%m'),
      description="Example Web Server",
      options={
          'build_exe': {
              'packages': [
                      'asyncio',
                      'packaging',
                      'numpy',
                      'appdirs',
                      'flask','jinja2', 'jinja2.ext',
                            'plotly',
                            'pandas',
                            'datetime',
                            'Package',
                            'sys',
                            'DataComposition',
                            'indexReader',
                           'os'],
              'include_files': includefiles,
              'include_msvcr': True}},
      executables=[main_executable], requires=['flask', 'wtforms'])
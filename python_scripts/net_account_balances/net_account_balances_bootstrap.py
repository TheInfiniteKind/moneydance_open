#!/usr/bin/env python
# -*- coding: UTF-8 -*-

########################################################################################################################
## bootstrap.py: Execute a compiled script if possible (faster load times) #############################################
########################################################################################################################
# Author: Stuart Beesley Feb 2023 - StuWareSoftSystems
# Purpose: a) load compiled version for faster launch time, b) avoid "method too large" RuntimeException (.pyc helper)
#
# NOTES: There are various ways to load/run/execute a script.... Some as follows:
# execfile() - executes a py script file on disk
# exec() - can execute org.python.core.PyCode object.
# org.python.util.PythonInterpreter.execfile() - can execute a py script on disk, or from an InputStream
# imp.load_module() - can import (which means runs/executes) a script, or InputStream, and either .py or $py.class file
# >> The "problem" with Import / load_module() is that the code will end up within its own module's namespace...
#
# Normally running just the original .py file will be fine.
#
# For large files, executing a $py.class compiled code file will be faster to load: To compile, use command below:
# java -cp jython.jar org.python.util.jython -c "import compileall; compileall.compile_file(yourscript.py')"
# For some large files, you may get a "method too large" RuntimeException. One resolution to this is to provide a
# CPython byte code .pyc file - this "helps" both the running of .py files, and/or the compilation of $py.class files
# to create a CPython byte code .pyc file, use this command: python -m py_compile yourscript.py
# ... or add -Dpython.cpython2=python to the java compile command when compiling.
# If the .pyc file is present when running a script, or compiling, then the "method too large" problem will be avoided
#
# Given Moneydance extensions will be running from within their own mxt file (ZIP) then you need a way to reference the
# zip's resources. Use the moneydance_extension_loader (ClassLoader) variable and then use .getResourceAsStream().
# I.E. you cannot just import / execute a file/directory/package that you created... You have to access the mxt's stream
########################################################################################################################

###############################################################################
# MIT License
#
# Copyright (c) 2021-2023 Stuart Beesley - StuWareSoftSystems
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
###############################################################################

import imp
import datetime
import __builtin__ as builtins

from java.lang import System, RuntimeException                                                                          # noqa

global moneydance, moneydance_ui, moneydance_extension_parameter, moneydance_extension_loader

_THIS_IS_ = u"net_account_balances"

def _specialPrint(_what):
    dt = datetime.datetime.now().strftime(u"%Y/%m/%d-%H:%M:%S")
    print(_what)
    System.err.write(_THIS_IS_ + u":" + dt + u": ")
    System.err.write(_what)
    System.err.write(u"\n")


if u"__file__" in globals(): raise Exception(u"ERROR: This script should only be run as part of an extension!")

# Little trick as imported module will have it's own globals
builtins.moneydance = moneydance
builtins.moneydance_ui = moneydance_ui

MDEL = u"moneydance_extension_loader"
if MDEL in globals(): builtins.moneydance_extension_loader = moneydance_extension_loader

MDEP = u"moneydance_extension_parameter"
if MDEP in globals(): builtins.moneydance_extension_parameter = moneydance_extension_parameter

MD_EXTENSION_LOADER = moneydance_extension_loader

_normalExtn = u".py"
_compiledExtn = u"$py.class"

# Method to run/execute compiled code in current name space.
# import os
# from org.python.core import BytecodeLoader
# from org.python.apache.commons.compress.utils import IOUtils
# _launchedFile = _THIS_IS_ + _compiledExtn
# scriptStream = MD_EXTENSION_LOADER.getResourceAsStream(u"/%s" %(_launchedFile))
# code = BytecodeLoader.makeCode(os.path.splitext(_launchedFile)[0], IOUtils.toByteArray(scriptStream), (_THIS_IS_ + _normalExtn))
# scriptStream.close()
# exec(code)

# Method to run/execute py script in current name space.
# try:
#     _launchedFile = _THIS_IS_ + _normalExtn;
#     scriptStream = MD_EXTENSION_LOADER.getResourceAsStream(u"/%s" %(_launchedFile));
#     py = moneydance.getPythonInterpreter()
#     py.getSystemState().setClassLoader(MD_EXTENSION_LOADER)
#     py.set("moneydance_extension_loader", MD_EXTENSION_LOADER)
#     py.execfile(scriptStream)
#     scriptStream.close()
#     moneydance.resetPythonInterpreter(py)
# except RuntimeException as e:
#     if u"method too large" in e.toString().lower():
#         raise Exception(u"@@ Sorry - script is too large for normal execution. Needs compiling first! @@".upper())
#     else: raise

# Method(s) to run/execute script via import. Loads into it's own module namespace
# ... Tries the compiled $py.class file first, then the original .py file
_launchedFile = _THIS_IS_ + _compiledExtn
scriptStream = MD_EXTENSION_LOADER.getResourceAsStream(u"/%s" %(_launchedFile))
if scriptStream is None:
    _specialPrint(u"@@ Will run normal (non)compiled script ('%s') @@" %(_launchedFile))
    _launchedFile = _THIS_IS_ + _normalExtn
    scriptStream = MD_EXTENSION_LOADER.getResourceAsStream(u"/%s" %(_launchedFile))
    _suffixIdx = 0
else:
    _specialPrint(u"@@ Will run pre-compiled script for best launch speed ('%s') @@" %(_launchedFile))
    _suffixIdx = 1

if scriptStream is None: raise Exception(u"ERROR: Could not get the script (%s) from within the mxt" %(_launchedFile))

_startTimeMs = System.currentTimeMillis()
bootstrapped_extension = imp.load_module(_THIS_IS_,
                                         scriptStream,
                                         (u"bootstrapped_" + _launchedFile),
                                         imp.get_suffixes()[_suffixIdx])
_specialPrint(u"BOOTSTRAP launched script in %s seconds..." %((System.currentTimeMillis() - _startTimeMs) / 1000.0))
scriptStream.close()

# if the extension is using an extension class, then pass pass back to Moneydance
try: moneydance_extension = bootstrapped_extension.moneydance_extension
except AttributeError: pass

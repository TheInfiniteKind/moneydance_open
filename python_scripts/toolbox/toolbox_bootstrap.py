#!/usr/bin/env python
# -*- coding: UTF-8 -*-

########################################################################################################################
## bootstrap.py: Execute a compiled script if possible (faster load times) #############################################
########################################################################################################################
# Author: Stuart Beesley Aug 2023 - StuWareSoftSystems
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

global sys, imp, builtins
global System, Runtime, RuntimeException, Long, Runnable, Thread, InterruptedException
global Platform, Common, AppEventManager
global moneydance, moneydance_ui, moneydance_extension_parameter, moneydance_extension_loader
global _THIS_IS_, _QuickAbortThisScriptException, _specialPrint, _decodeCommand, _HANDLE_EVENT_ENABLED_IF_REQUESTED
global _getExtensionPreferences, _saveExtensionPreferences
global debug

if "__file__" in globals(): raise Exception("ERROR: This script should only be run as part of an extension!")
if "debug" not in globals(): debug = False

# Little trick as imported module will have it's own globals
builtins.moneydance = moneydance
builtins.moneydance_ui = moneydance_ui

MDEL = "moneydance_extension_loader"
if MDEL in globals(): builtins.moneydance_extension_loader = moneydance_extension_loader

MDEP = "moneydance_extension_parameter"
if MDEP in globals(): builtins.moneydance_extension_parameter = moneydance_extension_parameter

MD_EXTENSION_LOADER = moneydance_extension_loader

_normalExtn = ".py"
_compiledExtn = "$py.class"

# Method to run/execute compiled code in current name space.
_startTimeMs = System.currentTimeMillis()
import os
from org.python.core import BytecodeLoader
from org.python.apache.commons.compress.utils import IOUtils as PythonIOUtils
_launchedFile = _THIS_IS_ + _compiledExtn
scriptStream = MD_EXTENSION_LOADER.getResourceAsStream("/%s" %(_launchedFile))
code = BytecodeLoader.makeCode(os.path.splitext(_launchedFile)[0], PythonIOUtils.toByteArray(scriptStream), (_THIS_IS_ + _normalExtn))
scriptStream.close()
exec(code)
_specialPrint("BOOTSTRAP launched script in %s seconds..." %((System.currentTimeMillis() - _startTimeMs) / 1000.0))
del PythonIOUtils, BytecodeLoader

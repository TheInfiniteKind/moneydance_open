#!/usr/bin/env python
# -*- coding: UTF-8 -*-

########################################################################################################################
## extension_bootstrap.py: Execute a compiled script if possible (faster load times) ###################################
########################################################################################################################
# Author: Stuart Beesley 2025 - StuWareSoftSystems
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
# NOTE: moneydance_this_fm appeared in 2024.2(5142), when moneydance_extension_loader was nuked
# NOTE: Security concerns with these methods are addressed by ensuring you only ever install/run IK signed mxt versions.
########################################################################################################################

###############################################################################
# MIT License
#
# Copyright (c) 2020-2025 Stuart Beesley - StuWareSoftSystems
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

########################################################################################################################
# common definitions / declarations
if "__file__" in globals(): raise Exception("ERROR: This script should only be run as part of an extension!")

global MD_REF, MD_REF_UI
global sys, imp, builtins
global System, Runtime, RuntimeException, Long, Boolean, Integer, Runnable, Thread, InterruptedException
global Platform, Common, AppEventManager
global moneydance_extension_parameter, moneydance_extension_loader, moneydance_this_fm
global _THIS_IS_, _QuickAbortThisScriptException, _specialPrint, _decodeCommand, _HANDLE_EVENT_ENABLED_IF_REQUESTED
global _getExtensionDatasetSettings, _saveExtensionDatasetSettings
global _getExtensionGlobalPreferences, _saveExtensionGlobalPreferences
global _getFieldByReflection

global debug

try:
    # Set moneydance_extension_parameter when using bootstrap and you want to detect different menus within main code...
    moneydance_extension_parameter = "show_sg2020"                                                                      # noqa

    if "moneydance_this_fm" in globals():
        MD_EXTENSION_LOADER = moneydance_this_fm
    else:
        MD_EXTENSION_LOADER = moneydance_extension_loader

    _normalExtn = ".py"
    _compiledExtn = "$py.class"

    # Method to run/execute compiled code in current name space.
    _startTimeMs = System.currentTimeMillis()
    _launchedFile = _THIS_IS_ + _compiledExtn

    _scriptStream = MD_EXTENSION_LOADER.getResourceAsStream("/%s" %(_launchedFile))
    if _scriptStream is None:
        _launchedFile = _THIS_IS_ + _normalExtn
        _scriptStream = MD_EXTENSION_LOADER.getResourceAsStream("/%s" %(_launchedFile))
        if _scriptStream is not None:
            _specialPrint("@@ BOOTSTRAP - will run normal (non)compiled script ('%s') @@" %(_launchedFile))
            _pyi = _getFieldByReflection(MD_REF.getModuleForID(_THIS_IS_), "python")
            _pyi.execfile(_scriptStream, _launchedFile)
            _scriptStream.close()
            del _pyi
    else:
        _specialPrint("@@ BOOTSTRAP - will run pre-compiled script for best launch speed ('%s') @@" %(_launchedFile))
        import os
        from org.python.core import BytecodeLoader
        from org.python.apache.commons.compress.utils import IOUtils as PythonIOUtils
        _pyCode = BytecodeLoader.makeCode(os.path.splitext(_launchedFile)[0], PythonIOUtils.toByteArray(_scriptStream), (_THIS_IS_ + _normalExtn))
        _scriptStream.close()
        del PythonIOUtils, BytecodeLoader
        exec(_pyCode)
        del _pyCode
    if _scriptStream is None: raise Exception("ERROR: Could not get the script (%s) from within the mxt" %(_launchedFile))

    _specialPrint("BOOTSTRAP - launched script in %s seconds..." %((System.currentTimeMillis() - _startTimeMs) / 1000.0))
    del _scriptStream, _normalExtn, _compiledExtn, _launchedFile, _startTimeMs
except _QuickAbortThisScriptException: pass

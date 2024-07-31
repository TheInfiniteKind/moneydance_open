#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# This script handles invoke and handle_event method calls, and can sometimes include a bootstrap.
# You would only use/need this script if using script_info {"type" = "method", "method" = "invoke", "script_file" = "invoke.py"}
# This gets called when moneydance.showURL() is called. It might get called when clicking on the menu item, depending on the combination of options used.
# If you are using the ExtensionClass() method and an initializer, then you do not need this file...
# Or this script can get triggered on MD events... (depends on script_info.dict)

###############################################################################
# MIT License
#
# Copyright (c) 2020-2024 Stuart Beesley - StuWareSoftSystems
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
if "moneydance_extension_parameter" not in globals(): raise Exception("ERROR: 'moneydance_extension_parameter' not found in globals()!")

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

########################################################################################################################
# definitions unique to this script

try:
    if not isinstance(moneydance_extension_parameter, basestring): moneydance_extension_parameter = ""
    cmd, cmdParam = _decodeCommand(moneydance_extension_parameter)

    if not _HANDLE_EVENT_ENABLED_IF_REQUESTED and not cmd.endswith("_events"):
        _specialPrint("EVENT HANDLING IS DISABLED >> WILL IGNORE THIS EVENT..... (was passed '%s', Command: '%s', Parameter: '%s')" %(moneydance_extension_parameter, cmd, cmdParam))
        raise _QuickAbortThisScriptException

    respondToMDEvents = [AppEventManager.FILE_CLOSING]

    lInvoke = lQuitAfter = lHandleEvent = False
    if moneydance_extension_parameter.startswith("md:"):
        if debug: _specialPrint("HANDLE_EVENT was passed '%s', Command: '%s', Parameter: '%s'" %(moneydance_extension_parameter, cmd, cmdParam))
        if moneydance_extension_parameter not in respondToMDEvents:
            if debug: _specialPrint("... ignoring: '%s'" %(moneydance_extension_parameter))
            raise _QuickAbortThisScriptException
        else:
            _EXTN_PREF_KEY_AUTO_EXTRACT_WHEN_FILE_CLOSING = "auto_extract_when_file_closing"
            if not _getExtensionDatasetSettings().getBoolean(_EXTN_PREF_KEY_AUTO_EXTRACT_WHEN_FILE_CLOSING, False):
                if debug: _specialPrint("handle_event() - Event: '%s' - 'auto_extract_when_file_closing' NOT SET - So Ignoring...." %(moneydance_extension_parameter))
                raise _QuickAbortThisScriptException
            else:
                lHandleEvent = True
                _specialPrint("handle_event() - Event: '%s' Book: '%s', 'auto_extract_when_file_closing' is set >> EXECUTING" %(moneydance_extension_parameter, MD_REF.getCurrentAccountBook()))

    else:
        lInvoke = True
        _specialPrint("INVOKE was passed '%s', Command: '%s', Parameter: '%s'" %(moneydance_extension_parameter, cmd, cmdParam))

        if cmd.lower() == "disable_events":
            _HANDLE_EVENT_ENABLED_IF_REQUESTED = False
            _specialPrint("DISABLE_EVENTS detected >> DISABLED event handling....")
            raise _QuickAbortThisScriptException
        elif cmd.lower() == "enable_events":
            _HANDLE_EVENT_ENABLED_IF_REQUESTED = True
            _specialPrint("ENABLE_EVENTS detected >> (RE)ENABLING event handling....")
            raise _QuickAbortThisScriptException

        if cmd.lower() != "autoextract":
            _specialPrint("Invoke IGNORED... Only accepted command = 'autoextract:noquit' or 'autoextract:quit'")
            raise _QuickAbortThisScriptException

        if cmdParam.lower() == "quit":
            lQuitAfter = True
            _specialPrint("... Moneydance will QUIT after auto extract completes...")
        else:
            _specialPrint("... Moneydance will remain running after auto extract completes...")


    ################################
    # Copied from bootstrap code....

    # Set moneydance_extension_parameter when using bootstrap and you want to detect different menus within main code...
    # moneydance_extension_parameter = ""                                                                               # noqa
    # Don't set ^^^^^^^^^ as .invoke() command will be setting this.....!

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

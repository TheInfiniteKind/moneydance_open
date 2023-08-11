#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# This script combines bootstrap, invoke and handle_event method calls...

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

if "__file__" in globals(): raise Exception("ERROR: This script should only be run as part of an extension!")
if "moneydance_extension_parameter" not in globals(): raise Exception("ERROR: 'moneydance_extension_parameter' not found in globals()!")

global System, RuntimeException, imp, builtins, AppEventManager
global moneydance, moneydance_ui, moneydance_extension_parameter, moneydance_extension_loader
global _THIS_IS_, _QuickAbortThisScriptException, _specialPrint, _decodeCommand, _HANDLE_EVENT_ENABLED_IF_REQUESTED
global _getExtensionPreferences, _saveExtensionPreferences
global debug

try:
    if "debug" not in globals(): debug = False

    if not isinstance(moneydance_extension_parameter, basestring): moneydance_extension_parameter = ""
    cmd, cmdParam = _decodeCommand(moneydance_extension_parameter)

    if not _HANDLE_EVENT_ENABLED_IF_REQUESTED and not cmd.endswith("_events"):
        _specialPrint("EVENT HANDLING IS DISABLED >> WILL IGNORE THIS EVENT..... (was passed '%s', Command: '%s', Parameter: '%s')" %(moneydance_extension_parameter, cmd, cmdParam))
        raise _QuickAbortThisScriptException

    respondToMDEvents = [AppEventManager.FILE_CLOSING]
    # allMDEvents = ["md:file:closing",
    #                "md:file:closed",
    #                "md:file:opening",
    #                "md:file:opened",
    #                "md:file:presave",
    #                "md:file:postsave",
    #                "md:app:exiting",
    #                "md:account:select",
    #                "md:account:root",
    #                "md:graphreport",
    #                "md:viewbudget",
    #                "md:viewreminders",
    #                "md:licenseupdated"]

    lInvoke = lQuitAfter = lHandleEvent = False
    if moneydance_extension_parameter.startswith("md:"):
        if debug: _specialPrint("HANDLE_EVENT was passed '%s', Command: '%s', Parameter: '%s'" %(moneydance_extension_parameter, cmd, cmdParam))
        if moneydance_extension_parameter not in respondToMDEvents:
            if debug: _specialPrint("... ignoring: '%s'" %(moneydance_extension_parameter))
            raise _QuickAbortThisScriptException
        else:
            _EXTN_PREF_KEY_AUTO_EXTRACT_WHEN_FILE_CLOSING = "auto_extract_when_file_closing"
            if not _getExtensionPreferences().getBoolean(_EXTN_PREF_KEY_AUTO_EXTRACT_WHEN_FILE_CLOSING, False):
                if debug: _specialPrint("handle_event() - Event: '%s' - 'auto_extract_when_file_closing' NOT SET - So Ignoring...." %(moneydance_extension_parameter))
                raise _QuickAbortThisScriptException
            else:
                lHandleEvent = True
                _specialPrint("handle_event() - Event: '%s' Book: '%s', 'auto_extract_when_file_closing' is set >> EXECUTING" %(moneydance_extension_parameter, moneydance.getCurrentAccountBook()))

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
    # import os
    # from org.python.core import BytecodeLoader
    # from org.python.apache.commons.compress.utils import IOUtils
    # _launchedFile = _THIS_IS_ + _compiledExtn
    # scriptStream = MD_EXTENSION_LOADER.getResourceAsStream("/%s" %(_launchedFile))
    # code = BytecodeLoader.makeCode(os.path.splitext(_launchedFile)[0], IOUtils.toByteArray(scriptStream), (_THIS_IS_ + _normalExtn))
    # scriptStream.close()
    # exec(code)

    # Method to run/execute py script in current name space.
    # try:
    #     _launchedFile = _THIS_IS_ + _normalExtn;
    #     scriptStream = MD_EXTENSION_LOADER.getResourceAsStream("/%s" %(_launchedFile));
    #     py = moneydance.getPythonInterpreter()
    #     py.getSystemState().setClassLoader(MD_EXTENSION_LOADER)
    #     py.set("moneydance_extension_loader", MD_EXTENSION_LOADER)
    #     py.execfile(scriptStream)
    #     scriptStream.close()
    #     moneydance.resetPythonInterpreter(py)
    # except RuntimeException as e:
    #     if "method too large" in e.toString().lower():
    #         raise Exception("@@ Sorry - script is too large for normal execution. Needs compiling first! @@".upper())
    #     else: raise

    # Method(s) to run/execute script via import. Loads into it's own module namespace
    # ... Tries the compiled $py.class file first, then the original .py file

    _launchedFile = _THIS_IS_ + _compiledExtn
    scriptStream = MD_EXTENSION_LOADER.getResourceAsStream("/%s" %(_launchedFile))
    if scriptStream is None:
        _specialPrint("@@ Will run normal (non)compiled script ('%s') @@" %(_launchedFile))
        _launchedFile = _THIS_IS_ + _normalExtn
        scriptStream = MD_EXTENSION_LOADER.getResourceAsStream("/%s" %(_launchedFile))
        _suffixIdx = 0
    else:
        _specialPrint("@@ Will run pre-compiled script for best launch speed ('%s') @@" %(_launchedFile))
        _suffixIdx = 1

    if scriptStream is None: raise Exception("ERROR: Could not get the script (%s) from within the mxt" %(_launchedFile))

    _startTimeMs = System.currentTimeMillis()
    bootstrapped_extension = imp.load_module(_THIS_IS_,
                                             scriptStream,
                                             ("bootstrapped_" + _launchedFile),
                                             imp.get_suffixes()[_suffixIdx])
    _specialPrint("BOOTSTRAP launched script in %s seconds..." %((System.currentTimeMillis() - _startTimeMs) / 1000.0))
    scriptStream.close()

    # if the extension is using an extension class, then pass pass back to Moneydance
    try: moneydance_extension = bootstrapped_extension.moneydance_extension
    except AttributeError: pass

except _QuickAbortThisScriptException: pass

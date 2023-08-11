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

global sys, imp, builtins
global System, Runtime, RuntimeException, Long, Runnable, Thread, InterruptedException
global Platform, Common, AppEventManager
global moneydance, moneydance_ui, moneydance_extension_parameter, moneydance_extension_loader
global _THIS_IS_, _QuickAbortThisScriptException, _specialPrint, _decodeCommand, _HANDLE_EVENT_ENABLED_IF_REQUESTED
global _getExtensionPreferences, _saveExtensionPreferences
global debug

global _ALL_OBSERVED_BOOKS, _observeMoneydanceObjects

global moneydance_invoke_called     # pulled in from main toolbox code (only executes if toolbox loaded/running)

try:
    if "debug" not in globals(): debug = False

    if not isinstance(moneydance_extension_parameter, basestring): moneydance_extension_parameter = ""
    cmd, cmdParam = _decodeCommand(moneydance_extension_parameter)

    if not _HANDLE_EVENT_ENABLED_IF_REQUESTED and not cmd.endswith("_events"):
        _specialPrint("EVENT HANDLING IS DISABLED >> WILL IGNORE THIS EVENT..... (was passed '%s', Command: '%s', Parameter: '%s')" %(moneydance_extension_parameter, cmd, cmdParam))
        raise _QuickAbortThisScriptException

    respondToMDEvents = [AppEventManager.FILE_OPENED, AppEventManager.FILE_CLOSING]

    lInvoke = lQuitAfter = lHandleEvent = False
    if moneydance_extension_parameter.startswith("md:"):
        if debug: _specialPrint("HANDLE_EVENT was passed '%s', Command: '%s', Parameter: '%s'" %(moneydance_extension_parameter, cmd, cmdParam))
        if moneydance_extension_parameter not in respondToMDEvents:
            if debug: _specialPrint("... ignoring: '%s'" %(moneydance_extension_parameter))
            raise _QuickAbortThisScriptException
        else:
            lHandleEvent = True

            _observeMoneydanceObjects(_ALL_OBSERVED_BOOKS)
            raise _QuickAbortThisScriptException

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


    try: moneydance_invoke_called(moneydance_extension_parameter)
    except: pass


except _QuickAbortThisScriptException: pass

#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# unload script for extension - this will only run from build 3056 onwards - otherwise ignored

global sys, imp, builtins
global System, Runtime, RuntimeException, Long, Runnable, Thread, InterruptedException
global Platform, Common, AppEventManager
global moneydance, moneydance_ui, moneydance_extension_parameter, moneydance_extension_loader
global _THIS_IS_, _QuickAbortThisScriptException, _specialPrint, _decodeCommand, _HANDLE_EVENT_ENABLED_IF_REQUESTED
global _getExtensionPreferences, _saveExtensionPreferences
global debug

global destroyOldFrames, myPrint        # Pull these in from main toolbox code (will only exist if toolbox was launched)
try:
    myPrint("DB", "attempting .unload() script")
    destroyOldFrames(_THIS_IS_)
    myPrint("B", ".unload() script (non-bootstrapped) successful!")
except:
    _specialPrint("%s .unload() script running....\n"
                  "BUT key objects NOT detected in my namespace (or extension is not running) - exiting..\n" %(_THIS_IS_))
del _THIS_IS_, _specialPrint, _QuickAbortThisScriptException, _decodeCommand, _HANDLE_EVENT_ENABLED_IF_REQUESTED
del _getExtensionPreferences, _saveExtensionPreferences

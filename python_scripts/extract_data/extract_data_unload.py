#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# unload script for extension - this will only run from build 3056 onwards - otherwise ignored

global _THIS_IS_, _QuickAbortThisScriptException, _specialPrint, _decodeCommand, _HANDLE_EVENT_ENABLED_IF_REQUESTED
global _getExtensionPreferences, _saveExtensionPreferences
global destroyOldFrames, bootstrapped_extension
global debug

try:
    _specialPrint("attempting .unload() script")
    destroyOldFrames(_THIS_IS_)
    _specialPrint(".unload() script (non-bootstrapped) successful!")
except:
    try:
        _specialPrint("... first attempt calling .unload() script failed... Will attempt bootstrapped .unload()")
        bootstrapped_extension.destroyOldFrames(_THIS_IS_)
        _specialPrint("... bootstrapped .unload() script called successfully")
    except:
        _specialPrint("%s .unload() script running....\n"
                      "BUT key objects NOT detected in my namespace (or extension is not running) - exiting..\n" %(_THIS_IS_))

del _THIS_IS_, _specialPrint, _QuickAbortThisScriptException, _decodeCommand, _HANDLE_EVENT_ENABLED_IF_REQUESTED
del _getExtensionPreferences, _saveExtensionPreferences

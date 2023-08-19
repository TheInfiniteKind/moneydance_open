#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# unload script for extension - this will only run from build 3056 onwards - otherwise ignored

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

########################################################################################################################
# common definitions / declarations
if "__file__" in globals(): raise Exception("ERROR: This script should only be run as part of an extension!")
global MD_REF, MD_REF_UI
global sys, imp, builtins
global System, Runtime, RuntimeException, Long, Boolean, Integer, Runnable, Thread, InterruptedException
global Platform, Common, AppEventManager
global moneydance_extension_parameter, moneydance_extension_loader
global _THIS_IS_, _QuickAbortThisScriptException, _specialPrint, _decodeCommand, _HANDLE_EVENT_ENABLED_IF_REQUESTED
global _getExtensionDatasetSettings, _saveExtensionDatasetSettings
global _getExtensionGlobalPreferences, _saveExtensionGlobalPreferences
global _getFieldByReflection

global debug

########################################################################################################################
# definitions unique to this script
# none

########################################################################################################################
# common code
global destroyOldFrames, myPrint        # Pull these in from main toolbox code (will only exist if toolbox was launched)
try:
    myPrint("DB", "attempting .unload() script")
    destroyOldFrames(_THIS_IS_)
    myPrint("B", ".unload() script (non-bootstrapped) successful!")
except:
    _specialPrint("%s .unload() script running....\n"
                  "BUT key objects NOT detected in my namespace (or extension is not running) - exiting..\n" %(_THIS_IS_))
del _THIS_IS_, _specialPrint, _QuickAbortThisScriptException, _decodeCommand, _HANDLE_EVENT_ENABLED_IF_REQUESTED
del _getExtensionDatasetSettings, _saveExtensionDatasetSettings
del _getExtensionGlobalPreferences, _saveExtensionGlobalPreferences
del _getFieldByReflection

########################################################################################################################
# code unique to this script
# none

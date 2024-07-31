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
global moneydance_invoke_called

try: moneydance_invoke_called(moneydance_extension_parameter)
except:
    if debug: _specialPrint("@@ ERROR calling .invoke(%s)" %(moneydance_extension_parameter))

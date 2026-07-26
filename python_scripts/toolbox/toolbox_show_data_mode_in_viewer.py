#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# toolbox_show_data_mode_in_viewer.py script for extension - this will only run from build 5500 onwards - otherwise ignored

###############################################################################
# MIT License
#
# Copyright (c) 2020-2026 Stuart Beesley - StuWareSoftSystems
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
global MD_REF
global _THIS_IS_, _QuickAbortThisScriptException, _specialPrint, _decodeCommand, _HANDLE_EVENT_ENABLED_IF_REQUESTED

global debug

########################################################################################################################
# definitions unique to this script

try:
    if float(MD_REF.getBuild()) >= 5500:    # Data export reporting capability (also AppDebug class present etc)
        from com.infinitekind.util import AppDebug                                                                      # noqa
        from javax.swing import SwingUtilities
        logger = AppDebug.logger("report-data").allowTogglingInUI(True).friendlyName("Show 'Data Mode' Reports in the Report Viewer")
        status = logger.isEnabled()
        logger.setEnabled(not status)
        SwingUtilities.invokeLater(lambda: MD_REF.getPreferences().firePreferencesUpdated())
        _specialPrint("Toggled AppDebug::report-data flag (show 'Data Mode' Reports in the Report Viewer) - now: %s" %(status))
    else:
        _specialPrint("AppDebug::report-data flag cannot be toggled - feature not available in this version")
        MD_REF.getUI().showErrorMessage("Feature not available in this version")
except:
    msg = "ERROR - could not enable AppDebug::report-data flag"
    _specialPrint(msg)
    MD_REF.getUI().showErrorMessage(msg)

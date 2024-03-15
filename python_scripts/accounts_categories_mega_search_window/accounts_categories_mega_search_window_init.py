#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Initializer script for extension - this will only run from build 3056 onwards - otherwise ignored

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
global moneydance, moneydance_ui
MD_REF = moneydance             # Make my own copy of reference as MD removes it once main thread ends.. Don't use/hold on to _data variable
MD_REF_UI = moneydance_ui       # Necessary as calls to .getUI() will try to load UI if None - we don't want this....

# Nuke unwanted (direct/indirect) reference(s) to AccountBook etc....
if "moneydance_data" in globals():
    moneydance_data = None
    del moneydance_data

if "moneybot" in globals():
    moneybot = None
    del moneybot

import sys
reload(sys)                     # Dirty hack to eliminate UTF-8 coding errors
sys.setdefaultencoding('utf8')  # Without this str() fails on unicode strings... NOTE: Builds MD2022(4040+) already do this...

import imp                                                                                                              # noqa
import __builtin__ as builtins                                                                                          # noqa
import datetime                                                                                                         # noqa
from java.lang import System, Runtime, RuntimeException, Long, Integer, Boolean, Runnable, Thread, InterruptedException # noqa
from com.moneydance.util import Platform                                                                                # noqa
from com.moneydance.apps.md.controller import Common                                                                    # noqa
from com.moneydance.apps.md.controller import AppEventManager                                                           # noqa

############ SET _THIS_IS_ and debug (default) BELOW ###
global debug
if "debug" not in globals():
    # if Moneydance is launched with -d, or this property is set, or extension is being (re)installed with Console open.
    debug = (False or MD_REF.DEBUG or Boolean.getBoolean("moneydance.debug"))

_THIS_IS_ = "accounts_categories_mega_search_window"
_HANDLE_EVENT_ENABLED_IF_REQUESTED = False
############ SET _THIS_IS_, _HANDLE_EVENT_ENABLED_IF_REQUESTED, and debug (default) ABOVE ###

class _QuickAbortThisScriptException(Exception): pass

def _specialPrint(_what):
    dt = datetime.datetime.now().strftime("%Y/%m/%d-%H:%M:%S")
    # print(_what)
    System.err.write(_THIS_IS_ + ":" + dt + ": ")
    System.err.write(_what)
    System.err.write("\n")


if debug: _specialPrint("** DEBUG IS ON **")

def _decodeCommand(passedEvent):
    param = ""
    uri = passedEvent
    command = uri
    theIdx = uri.find('?')
    if(theIdx>=0):
        command = uri[:theIdx]
        param = uri[theIdx+1:]
    else:
        theIdx = uri.find(':')
        if(theIdx>=0):
            command = uri[:theIdx]
            param = uri[theIdx+1:]
    return command, param

from java.lang import NoSuchFieldException, NoSuchMethodException                                                       # noqa
from java.lang.reflect import Modifier                                                                                  # noqa

def _getFieldByReflection(theObj, fieldName, isInt=False):
    try: theClass = theObj.getClass()
    except TypeError: theClass = theObj     # This catches where the object is already the Class
    reflectField = None
    while theClass is not None:
        try:
            reflectField = theClass.getDeclaredField(fieldName)
            break
        except NoSuchFieldException:
            theClass = theClass.getSuperclass()
    if reflectField is None: raise Exception("ERROR: could not find field: %s in class hierarchy" %(fieldName))
    if Modifier.isPrivate(reflectField.getModifiers()): reflectField.setAccessible(True)
    elif Modifier.isProtected(reflectField.getModifiers()): reflectField.setAccessible(True)
    isStatic = Modifier.isStatic(reflectField.getModifiers())
    if isInt: return reflectField.getInt(theObj if not isStatic else None)
    return reflectField.get(theObj if not isStatic else None)


from com.infinitekind.util import StreamTable
from com.infinitekind.tiksync import SyncRecord
_EXTN_PREF_KEY = "stuwaresoftsystems" + "." + _THIS_IS_
_MD_KOTLIN_COMPILED_BUILD = 5000

class _StreamTableFixed(StreamTable):
    """Replicates StreamTable. Provide a source to merge. Method .getBoolean() is 'fixed' to be backwards compatible with builds prior to Kotlin (Y/N vs 0/1)"""
    def __init__(self, _streamTableToCopy):
        # type: (StreamTable) -> None
        if not isinstance(_streamTableToCopy, StreamTable): raise Exception("LOGIC ERROR: Must pass a StreamTable! (Passed: %s)" %(type(_streamTableToCopy)))
        self.merge(_streamTableToCopy)

    def getBoolean(self, key, defaultVal):
        # type: (basestring, bool) -> bool
        if MD_REF.getBuild() >= _MD_KOTLIN_COMPILED_BUILD:      # MD2023.0 First Kotlin release - changed the code from detecting only Y/N to Y/N/T/F/0/1
            return super(self.__class__, self).getBoolean(key, defaultVal)
        _value = self.get(key, None)
        if _value in ["1", "Y", "y", "T", "t", "true", True]: return True
        if _value in ["0", "N", "n", "F", "f", "false", False]: return False
        return defaultVal

def _getExtensionDatasetSettings():
    # type: () -> SyncRecord
    _extnSettings =  MD_REF.getCurrentAccountBook().getLocalStorage().getSubset(_EXTN_PREF_KEY)
    if debug: _specialPrint("Retrieved Extension Dataset Settings from LocalStorage: %s" %(_extnSettings))
    return _extnSettings

def _saveExtensionDatasetSettings(newExtnSettings):
    # type: (SyncRecord) -> None
    if not isinstance(newExtnSettings, SyncRecord):
        raise Exception("ERROR: 'newExtnSettings' is not a SyncRecord (given: '%s')" %(type(newExtnSettings)))
    _localStorage = MD_REF.getCurrentAccountBook().getLocalStorage()
    _localStorage.put(_EXTN_PREF_KEY, newExtnSettings)
    if debug: _specialPrint("Stored Extension Dataset Settings into LocalStorage: %s" %(newExtnSettings))

def _getExtensionGlobalPreferences(enhancedBooleanCheck=True):
    # type: (bool) -> StreamTable
    _extnPrefs =  MD_REF.getPreferences().getTableSetting(_EXTN_PREF_KEY, StreamTable())
    if MD_REF.getBuild() < _MD_KOTLIN_COMPILED_BUILD:
        if enhancedBooleanCheck:
            _extnPrefs = _StreamTableFixed(_extnPrefs)
            if debug: _specialPrint("... copied retrieved Extension Global Preferences into enhanced StreamTable for backwards .getBoolean() capability...")
    if debug: _specialPrint("Retrieved Extension Global Preferences: %s" %(_extnPrefs))
    return _extnPrefs

def _saveExtensionGlobalPreferences(newExtnPrefs):
    # type: (StreamTable) -> None
    if not isinstance(newExtnPrefs, StreamTable):
        raise Exception("ERROR: 'newExtnPrefs' is not a StreamTable (given: '%s')" %(type(newExtnPrefs)))
    MD_REF.getPreferences().setSetting(_EXTN_PREF_KEY, newExtnPrefs)
    if debug: _specialPrint("Stored Extension Global Preferences: %s" %(newExtnPrefs))

########################################################################################################################
# definitions unique to this script

# none for this script...


msg = "\n#####################################################################\n"\
      "%s: %s_init.py initializer script running - doing nothing - will exit....\n"\
      "#####################################################################\n" %(_THIS_IS_,_THIS_IS_)

_specialPrint(msg)

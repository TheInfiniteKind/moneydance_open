#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Initializer file for extension - this will only run from build 3056 onwards - otherwise ignored

global moneydance
import imp, datetime                                                                                                    # noqa
import __builtin__ as builtins                                                                                          # noqa
from java.lang import System, RuntimeException                                                                          # noqa
from com.moneydance.apps.md.controller import AppEventManager                                                           # noqa
global debug

_THIS_IS_ = "extract_data"

_HANDLE_EVENT_ENABLED_IF_REQUESTED = True

class _QuickAbortThisScriptException(Exception): pass

def _specialPrint(_what):
    dt = datetime.datetime.now().strftime("%Y/%m/%d-%H:%M:%S")
    print(_what)
    System.err.write(_THIS_IS_ + ":" + dt + ": ")
    System.err.write(_what)
    System.err.write("\n")

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


from com.infinitekind.tiksync import SyncRecord
_EXTN_PREF_KEY = "stuwaresoftsystems" + "." + _THIS_IS_

def _getExtensionPreferences():
    # type: () -> SyncRecord
    _extnPrefs =  moneydance.getCurrentAccountBook().getLocalStorage().getSubset(_EXTN_PREF_KEY)
    _specialPrint("Retrieved Extn Preferences from LocalStorage: %s" %(_extnPrefs))
    return _extnPrefs

def _saveExtensionPreferences(newExtnPrefs):
    # type: (SyncRecord) -> None
    if not isinstance(newExtnPrefs, SyncRecord):
        raise Exception("ERROR: 'newExtnPrefs' is not a SyncRecord (given: '%s')" %(type(newExtnPrefs)))
    _localStorage = moneydance.getCurrentAccountBook().getLocalStorage()
    _localStorage.put(_EXTN_PREF_KEY, newExtnPrefs)
    _specialPrint("Stored Extn Preferences into LocalStorage: %s"  %(newExtnPrefs))



msg = "\n#############################################################################################\n"\
      "%s: %s_init.py initializer script - setting up extension then will exit....\n"\
      "###############################################################################################\n" %(_THIS_IS_,_THIS_IS_)

_specialPrint(msg)

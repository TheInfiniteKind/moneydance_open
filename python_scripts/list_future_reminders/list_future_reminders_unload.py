#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# unload script for extension - this will only run from build 3056 onwards - otherwise ignored

from java.lang import System
import datetime

_THIS_IS_ = u"list_future_reminders"

def _specialPrint(_what):
    dt = datetime.datetime.now().strftime(u"%Y/%m/%d-%H:%M:%S")
    print(_what)
    System.err.write(_THIS_IS_ + u":" + dt + u": ")
    System.err.write(_what)
    System.err.write("\n")


global destroyOldFrames, bootstrapped_extension, myPrint
try:
    myPrint("DB", "attempting .unload() script")
    destroyOldFrames(_THIS_IS_)
    myPrint("B", ".unload() script (non-bootstrapped) successful!")
except:
    try:
        bootstrapped_extension.myPrint("DB", "... first attempt calling .unload() script failed... Will attempt bootstrapped .unload()")
        bootstrapped_extension.destroyOldFrames(_THIS_IS_)
        bootstrapped_extension.myPrint("B", "... bootstrapped .unload() script called successfully")
    except:
        _specialPrint("%s .unload() script running....\n"
                      "BUT key objects NOT detected in my namespace (or extension is not running) - exiting..\n" %(_THIS_IS_))
del _THIS_IS_, _specialPrint

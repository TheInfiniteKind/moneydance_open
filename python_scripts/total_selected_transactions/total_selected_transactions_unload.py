#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# unload script for extension - this will only run from build 3056 onwards - otherwise ignored

from java.lang import System

_THIS_IS_ = u"total_selected_transactions"

global debug, myPrint, myModuleID, destroyOldFrames
if ("debug" not in globals()
        or "myPrint" not in globals()
        or "myModuleID" not in globals()
        or "destroyOldFrames" not in globals()):
    msg = "%s .unload() script running....\nBUT key objects NOT detected in my namespace (or extension is not running) - exiting..\n" %(_THIS_IS_)
    print(msg)
    System.err.write(msg)
else:
    myPrint("DB", ".unload() script operational ;->\n")
    destroyOldFrames(myModuleID)
    myPrint("DB","... Completed unload routines...")

del _THIS_IS_

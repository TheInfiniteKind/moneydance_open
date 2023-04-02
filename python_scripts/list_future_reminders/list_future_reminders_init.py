#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Initializer file for extension - this will only run from build 3056 onwards - otherwise ignored

import datetime
from java.lang import System

_THIS_IS_ = u"list_future_reminders"

def _specialPrint(_what):
    dt = datetime.datetime.now().strftime(u"%Y/%m/%d-%H:%M:%S")
    print(_what)
    System.err.write(_THIS_IS_ + u":" + dt + u": ")
    System.err.write(_what)
    System.err.write(u"\n")


msg = u"\n#####################################################################\n"\
      u"%s: %s_init.py initializer script running - doing nothing - will exit....\n"\
      u"#####################################################################\n" %(_THIS_IS_,_THIS_IS_)

_specialPrint(msg)
del _THIS_IS_, _specialPrint

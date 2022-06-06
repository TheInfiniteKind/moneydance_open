#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Initializer file for extension - this will only run from build 3056 onwards - otherwise ignored

global moneydance

from java.lang import System

def _specialPrint(_what):
    print(_what)
    System.err.write(_what)


_THIS_IS_ = u"toolbox"

_TOOLBOX_PREFERENCES_ZAPPER = u"toolbox_preferences_zapper"

keysToZap = moneydance.getPreferences().getVectorSetting(_TOOLBOX_PREFERENCES_ZAPPER, None)
if keysToZap is None:
    msg = u"\n#####################################################################\n"\
          u"%s: %s_init.py initializer script running - doing nothing - will exit....\n"\
          u"#####################################################################\n\n" %(_THIS_IS_,_THIS_IS_)
    _specialPrint(msg)
else:
    msg = u"\n##########################################################################\n"\
          u"%s: %s_init.py initializer script running - EXECUTING PREFERENCES ZAPPER....\n"\
          u"############################################################################\n\n" %(_THIS_IS_,_THIS_IS_)
    _specialPrint(msg)

    for zapKey in keysToZap:
        _specialPrint(u".. Zapping: '%s'\n" %(zapKey))
        moneydance.getPreferences().setSetting(zapKey, None)
    moneydance.getPreferences().setSetting(_TOOLBOX_PREFERENCES_ZAPPER, None)
    _specialPrint(u"############# FINISHED ZAPPING ########################\n")

del _THIS_IS_, _TOOLBOX_PREFERENCES_ZAPPER, _specialPrint

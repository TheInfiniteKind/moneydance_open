#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Initializer file for extension - this will only run from build 3056 onwards - otherwise ignored

global moneydance

from java.lang import System, Runtime, Long

def _specialPrint(_what):
    print(_what)
    System.err.write(_what)


_THIS_IS_ = u"toolbox"

_TOOLBOX_PREFERENCES_ZAPPER = u"toolbox_preferences_zapper"

try:
    def convertBytesGBs(_size): return round((_size/(1000.0*1000.0*1000)),1)
    from com.moneydance.apps.md.controller import Common
    msg = u"\n"
    msg += u"-----------------------------------------------------\n"
    msg += (u"%s - quick information:\n" %(_THIS_IS_.capitalize()))
    msg += (u"MD CONSOLE FILE LOCATION:       '%s'\n" %(moneydance.getLogFile().getCanonicalPath()))
    msg += (u"MD CONFIG/PREFERENCES LOCATION: '%s'\n" %(Common.getPreferencesFile().getCanonicalPath()))
    msg += (u"MD EXECUTION MODE:               %s (%s)\n" %(moneydance.getExecutionMode(), (u"AppletMode" if (moneydance.getExecutionMode() == moneydance.EXEC_MODE_APPLET) else u"Normal")))
    # msg += (u"OS PLATFORM:                     %s (%s)\n" %(System.getProperty(u"os.name"), System.getProperty(u"os.version")))
    # msg += (u"ARCHITECTURE:                    %s\n" %(System.getProperty(u"os.arch")))

    runTime = Runtime.getRuntime()
    maxMemory = Runtime.getRuntime().maxMemory()
    msg += (u"JVM - Available processor cores: %s\n" %(runTime.availableProcessors()))
    msg += (u"JVM - Maximum memory possible:   %s\n" %(u"{}".format(u"no limit") if (Long(maxMemory) == Long.MAX_VALUE) else u"{:,} GB".format(convertBytesGBs(maxMemory))))
    msg += (u"JVM - Total memory allocated:    {:,} GB (used {:,} GB / free {:,} GB)\n".format(convertBytesGBs(runTime.totalMemory()),
                                                                                               convertBytesGBs(runTime.totalMemory() - runTime.freeMemory()),
                                                                                               convertBytesGBs(runTime.freeMemory())))
    msg += u"-----------------------------------------------------\n"
    msg += u"\n"
    _specialPrint(msg)
except:
    _specialPrint(u"ERROR: %s quick information failed...." %(_THIS_IS_.capitalize()))

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

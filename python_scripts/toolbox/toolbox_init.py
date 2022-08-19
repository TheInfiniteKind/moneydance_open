#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Initializer file for extension - this will only run from build 3056 onwards - otherwise ignored

global moneydance

from java.lang import System, Runtime, Long, Runnable, Thread
from com.moneydance.util import Platform

def _specialPrint(_what):
    print(_what)
    System.err.write(_what)


_THIS_IS_ = u"toolbox"

_TOOLBOX_PREFERENCES_ZAPPER = u"toolbox_preferences_zapper"

keysToZap = moneydance.getPreferences().getVectorSetting(_TOOLBOX_PREFERENCES_ZAPPER, None)
if keysToZap is None:
    msgx = u"\n#####################################################################\n"\
           u"%s: %s_init.py initializer script running - doing nothing - will exit....\n"\
           u"#####################################################################\n\n" %(_THIS_IS_,_THIS_IS_)
    _specialPrint(msgx)
else:
    msgx = u"\n##########################################################################\n"\
           u"%s: %s_init.py initializer script running - EXECUTING PREFERENCES ZAPPER....\n"\
           u"############################################################################\n\n" %(_THIS_IS_,_THIS_IS_)
    _specialPrint(msgx)

    for zapKey in keysToZap:
        _specialPrint(u".. Zapping: '%s'\n" %(zapKey))
        moneydance.getPreferences().setSetting(zapKey, None)
    moneydance.getPreferences().setSetting(_TOOLBOX_PREFERENCES_ZAPPER, None)
    _specialPrint(u"############# FINISHED ZAPPING ########################\n")

class QuickDiag(Runnable):
    def __init__(self, mdRef, _thisis):
        self.mdRef = mdRef
        self.thisis = _thisis

    def run(self):
        try:
            Thread.sleep(10 * 1000)     # Sleep to allow JVM Memory to settle down.....
            def convertBytesGBs(_size): return round((_size/(1000.0*1000.0*1000)),1)
            from com.moneydance.apps.md.controller import Common
            msg = u"\n"
            msg += u"-----------------------------------------------------\n"
            msg += (u"%s - quick information:\n" %(self.thisis.capitalize()))
            msg += u"-----\n"

            msg += (u"MD CONSOLE FILE LOCATION:       '%s'\n" %(self.mdRef.getLogFile().getCanonicalPath()))
            msg += (u"MD CONFIG/PREFERENCES LOCATION: '%s'\n" %(Common.getPreferencesFile().getCanonicalPath()))

            msg += u"-----\n"
            from com.moneydance.apps.md.controller.io import FileUtils
            destroyBackupChoices = self.mdRef.getPreferences().getSetting(u"backup.destroy_number", u"5")
            returnedBackupType = self.mdRef.getPreferences().getSetting(u"backup.backup_type", u"every_x_days")
            if returnedBackupType == u"every_time":
                dailyBackupCheckbox = True
                destroyBackupChoices = 1
            elif returnedBackupType == u"every_x_days":
                dailyBackupCheckbox = True
            else:
                dailyBackupCheckbox = False

            msg += (u"BACKUPS - Save Daily:            %s\n" %(dailyBackupCheckbox))
            msg += (u"BACKUPS - Keep no more than:     %s backups\n" %(destroyBackupChoices))
            msg += (u"BACKUPS - Separate Backup Foldr: %s\n" %(self.mdRef.getPreferences().getBoolSetting(u"backup.location_selected", True)))
            msg += (u"BACKUPS - Backup Folder:        '%s'\n" %(FileUtils.getBackupDir(self.mdRef.getPreferences()).getCanonicalPath()))

            msg += (u"..key - 'backup.location':      '%s'\n" %(self.mdRef.getPreferences().getSetting(u"backup.location", u"<not set>")))
            msg += (u"..key - 'backup.last_browsed':  '%s'\n" %(self.mdRef.getPreferences().getSetting(u"backup.last_browsed", u"<not set>")))
            msg += (u"..key - 'backup.last_saved':    '%s'\n" %(self.mdRef.getPreferences().getSetting(u"backup.last_saved", u"<not set>")))
            msg += (u"..key - '_default_backup_dir':  '%s'\n" %(self.mdRef.getPreferences().getSetting(u"_default_backup_dir", u"<not set>")))

            msg += u"-----\n"

            from java.util import Locale, TimeZone, Date
            sysLoc = Locale.getDefault()
            msg += (u"System Default Locale Cty/Lang: '%s' / '%s'\n" %(sysLoc.getCountry(), sysLoc.getLanguage()))

            MDLoc = self.mdRef.getPreferences().getLocale()
            msg += (u"MD Preference Locale Ctry/Lang: '%s' / '%s'\n" %(self.mdRef.getPreferences().getSetting(u"locale.country", u""), self.mdRef.getPreferences().getSetting(u"locale.language", u"")))
            msg += (u"MD Locale Cty/Lang:             '%s' / '%s'\n" %(MDLoc.getCountry(), MDLoc.getLanguage()))
            msg += (u"Moneydance decimal point:       '%s'\n" %(self.mdRef.getPreferences().getSetting(u"decimal_character", u".")))

            # defaultTZ = TimeZone.getDefault()
            # msg += (u"Default TimeZone (UTC offset)   '%s(%s) %s'\n" %(defaultTZ.getDisplayName(), defaultTZ.getRawOffset(), "** SummerTime+1" if defaultTZ.inDaylightTime(Date()) else ""))
            # msg += (u"MD TimeZone                     '%s'\n" %(defaultTZ.getDisplayName(MDLoc)))
            msg += u"-----\n"

            msg += (u"MD EXECUTION MODE:               %s (%s)\n" %(self.mdRef.getExecutionMode(), (u"AppletMode" if (self.mdRef.getExecutionMode() == self.mdRef.EXEC_MODE_APPLET) else u"Normal")))
            # msg += (u"OS PLATFORM:                     %s (%s)\n" %(System.getProperty(u"os.name"), System.getProperty(u"os.version")))
            # msg += (u"ARCHITECTURE:                    %s\n" %(System.getProperty(u"os.arch")))

            for i in range(3):
                runTime = Runtime.getRuntime()
                maxMemory = Runtime.getRuntime().maxMemory()
                if i < 1: msg += (u"JVM - Available processor cores: %s\n" %(runTime.availableProcessors()))
                msg += (u"JVM - Maximum memory possible:   %s\n" %(u"{}".format(u"no limit") if (Long(maxMemory) == Long.MAX_VALUE) else u"{:,} GB".format(convertBytesGBs(maxMemory))))
                msg += (u"JVM - Total memory allocated:    {:,} GB (used {:,} GB / free {:,} GB)\n".format(convertBytesGBs(runTime.totalMemory()),
                                                                                                           convertBytesGBs(runTime.totalMemory() - runTime.freeMemory()),
                                                                                                           convertBytesGBs(runTime.freeMemory())))
                usage = ((runTime.totalMemory() - runTime.freeMemory()) / float(maxMemory))
                if  usage > 0.75:
                    msg += (u"** MD memory usage is %s of max allocated to JVM%s **\n"
                            %(u"{:.0%}".format(usage),
                              u", consider editing .vmoptions file to increase '-Xmx' memory setting" if not Platform.isOSX() else u""))
                msg += u"-----------------------------------------------------\n"
                msg += u"\n"
                _specialPrint(msg)
                msg = u"-----------------------------------------------------\n"

                Thread.sleep(60 * 1000)     # Sleep and repeat.....

        except:
            _specialPrint(u"ERROR: %s quick information failed...." %(self.thisis.capitalize()))


t = Thread(QuickDiag(moneydance, _THIS_IS_), u"%s_init_quickdiag" %(_THIS_IS_))
t.setDaemon(True)
t.start()

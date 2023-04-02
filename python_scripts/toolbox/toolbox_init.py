#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Initializer file for extension - this will only run from build 3056 onwards - otherwise ignored

global moneydance

import sys
import datetime
from java.lang import System, Runtime, Long, Runnable, Thread, InterruptedException
from com.moneydance.util import Platform
from com.moneydance.apps.md.controller import Common
from java.io import File

_THIS_IS_ = u"toolbox"

def _specialPrint(_what):
    dt = datetime.datetime.now().strftime(u"%Y/%m/%d-%H:%M:%S")
    print(_what)
    System.err.write(_THIS_IS_ + u":" + dt + u": ")
    System.err.write(_what)
    System.err.write("\n")

def returnPathStrings(fileReference, arePathsIdentical=False):
    _pathStr = u""
    if fileReference is not None and isinstance(fileReference, File):
        _pathStr = u"'%s'" %(fileReference.getAbsolutePath())
        if fileReference.getAbsolutePath() != fileReference.getCanonicalPath():
            _pathStr += u" (alias to: '%s')" %(fileReference.getCanonicalPath())

    if arePathsIdentical: return (fileReference.getAbsolutePath() == fileReference.getCanonicalPath())
    return _pathStr


_TOOLBOX_PREFERENCES_ZAPPER = u"toolbox_preferences_zapper"

keysToZap = moneydance.getPreferences().getVectorSetting(_TOOLBOX_PREFERENCES_ZAPPER, None)
if keysToZap is None:
    msgx = u"\n#############################################################################################################################\n"\
           u"%s: %s_init.py initializer script running - performing some quick checks, logging diagnostics, then will exit....\n"\
           u"#############################################################################################################################\n" %(_THIS_IS_,_THIS_IS_)
    _specialPrint(msgx)
else:
    msgx = u"\n########################################################################################\n"\
           u"%s: %s_init.py initializer script running - EXECUTING PREFERENCES ZAPPER....\n"\
           u"########################################################################################\n" %(_THIS_IS_,_THIS_IS_)
    _specialPrint(msgx)

    for zapKey in keysToZap:
        _specialPrint(u".. Zapping: '%s'" %(zapKey))
        moneydance.getPreferences().setSetting(zapKey, None)
    moneydance.getPreferences().setSetting(_TOOLBOX_PREFERENCES_ZAPPER, None)
    _specialPrint(u"############# FINISHED ZAPPING ########################")

def showMacAliasPath():
    fRawPath = Common.getRootDirectory()
    rawPath = fRawPath.getCanonicalPath()
    checkForStr = u"/com.infinitekind.MoneydanceOSX/"
    replaceWithStr = u"/Moneydance/"
    if (Platform.isOSX() and fRawPath.exists() and fRawPath.isDirectory() and isinstance(rawPath, basestring) and checkForStr in rawPath):
        return rawPath.replace(checkForStr, replaceWithStr)
    return None

class QuickDiag(Runnable):
    def __init__(self, mdRef, _thisis):
        self.mdRef = mdRef
        self.thisis = _thisis

    def run(self):
        msg = u"\n"
        try:
            Thread.sleep(10 * 1000)     # Sleep to allow JVM Memory to settle down.....
            def convertBytesGBs(_size): return round((_size/(1000.0*1000.0*1000)),1)
            from com.moneydance.apps.md.controller import Common
            msg += u"-----------------------------------------------------\n"
            msg += (u"%s - quick information:\n" %(self.thisis.capitalize()))
            msg += u"-----\n"

            msg += (u"MD CONSOLE FILE LOCATION:       %s\n" %(returnPathStrings(self.mdRef.getLogFile())))
            msg += (u"MD CONFIG/PREFERENCES LOCATION: %s\n" %(returnPathStrings(Common.getPreferencesFile())))

            if showMacAliasPath():
                msg += (u"... Mac Finder path for above:  '%s'\n" %(showMacAliasPath()))

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

            MD_CONFIGDICT_BACKUP_TYPE = u"backup.backup_type"
            backupFolder = FileUtils.getBackupDir(self.mdRef.getPreferences())
            backupType = self.mdRef.getPreferences().getSetting(MD_CONFIGDICT_BACKUP_TYPE, u"every_x_days")
            autoBackup = (backupType != u"no_backup")
            if not autoBackup:
                backupFileTxt = u"** WARNING: AUTO BACKUPS ARE DISABLED **"
            elif backupFolder is None:
                backupFileTxt = u"** ERROR: NO AUTO-BACKUP LOCATION DETECTED **"
            elif not isinstance(backupFolder, File) or not backupFolder.exists():
                backupFileTxt = u"** ERROR: INVALID AUTO-BACKUP LOCATION DETECTED **"
            else:
                backupFileTxt = u"(backup location exists)"

            msg += (u"BACKUPS - Backup Folder:        %s %s\n" %(returnPathStrings(backupFolder), backupFileTxt))

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
                if  usage > 0.60:
                    msg += (u"** MD memory usage is %s of max allocated to JVM%s **\n"
                            %(u"{:.0%}".format(usage),
                              u", consider editing .vmoptions file to increase '-Xmx' memory setting" if not Platform.isOSX() else u""))
                msg += u"-----------------------------------------------------\n"
                msg += u"\n"
                _specialPrint(msg)
                msg = u"\n-----------------------------------------------------\n"
                Thread.sleep(60 * 1000)     # Sleep and repeat.....

        except InterruptedException: pass

        except:
            if msg is not None and isinstance(msg, basestring):
                msg += u"\n"
                _specialPrint(msg)

            _specialPrint(u"*** ERROR: %s quick information failed.... (%s, %s, line: %s)"
                          %(self.thisis.capitalize(), unicode(sys.exc_info()[0]), unicode(sys.exc_info()[1]), unicode(sys.exc_info()[2].tb_lineno)))


try:
    for t in Thread.getAllStackTraces().keySet():
        for checkName in [u"toolbox_DownloadExtensionVersionData", u"%s_init_quickdiag" %(_THIS_IS_)]:
            if checkName.lower() in t.getName().lower() and t.isAlive():
                _specialPrint(u"Interrupting old Thread '%s'(id: %s) which seems to still be alive" %(t, t.getId()))
                t.interrupt()
except: _specialPrint(u"%s - error interrupting old Thread... (continuing)" %(_THIS_IS_))

t = Thread(QuickDiag(moneydance, _THIS_IS_), u"%s_init_quickdiag" %(_THIS_IS_))
t.setDaemon(True)
t.start()

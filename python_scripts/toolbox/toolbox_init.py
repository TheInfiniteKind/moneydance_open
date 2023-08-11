#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Initializer file for extension - this will only run from build 3056 onwards - otherwise ignored

global moneydance

import sys                                                                                                              # noqa
import imp                                                                                                              # noqa
import __builtin__ as builtins                                                                                          # noqa
import datetime                                                                                                         # noqa
from java.lang import System, Runtime, RuntimeException, Long, Runnable, Thread, InterruptedException                   # noqa
from com.moneydance.util import Platform                                                                                # noqa
from com.moneydance.apps.md.controller import Common                                                                    # noqa
from com.moneydance.apps.md.controller import AppEventManager                                                           # noqa
from java.io import File

global debug
if "debug" not in globals(): debug = False

_THIS_IS_ = "toolbox"

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


from java.lang.ref import WeakReference
_ALL_OBSERVED_BOOKS = []
def _observeMoneydanceObjects(_observedBooksRef):
    _syncer = None
    _book = moneydance.getCurrentAccountBook()
    if _book is not None:
        lFoundRef = False
        for _ref in _observedBooksRef:
            if _ref[0].get() is not None and _ref[0].get() is _book:
                lFoundRef = True
                break
        if not lFoundRef:
            _syncer = _book.getSyncer()
            _observedBooksRef.append([WeakReference(_book), WeakReference(_syncer)])
    if debug: _specialPrint("OBSERVED (WeakReference) for book: %s, syncer: %s. (Now contains [%s])" %(_book, _syncer, len(_ALL_OBSERVED_BOOKS)))
    del _book, _syncer


_observeMoneydanceObjects(_ALL_OBSERVED_BOOKS)


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

def returnPathStrings(fileReference, arePathsIdentical=False):
    _pathStr = ""
    if fileReference is not None and isinstance(fileReference, File):
        _pathStr = "'%s'" %(fileReference.getAbsolutePath())
        if fileReference.getAbsolutePath() != fileReference.getCanonicalPath():
            _pathStr += " (alias to: '%s')" %(fileReference.getCanonicalPath())

    if arePathsIdentical: return (fileReference.getAbsolutePath() == fileReference.getCanonicalPath())
    return _pathStr


_TOOLBOX_PREFERENCES_ZAPPER = "toolbox_preferences_zapper"

keysToZap = moneydance.getPreferences().getVectorSetting(_TOOLBOX_PREFERENCES_ZAPPER, None)
if keysToZap is None:
    msgx = "\n#############################################################################################################################\n"\
           "%s: %s_init.py initializer script running - performing some quick checks, logging diagnostics, then will exit....\n"\
           "#############################################################################################################################\n" %(_THIS_IS_,_THIS_IS_)
    _specialPrint(msgx)
else:
    msgx = "\n########################################################################################\n"\
           "%s: %s_init.py initializer script running - EXECUTING PREFERENCES ZAPPER....\n"\
           "########################################################################################\n" %(_THIS_IS_,_THIS_IS_)
    _specialPrint(msgx)

    for zapKey in keysToZap:
        _specialPrint(".. Zapping: '%s'" %(zapKey))
        moneydance.getPreferences().setSetting(zapKey, None)
    moneydance.getPreferences().setSetting(_TOOLBOX_PREFERENCES_ZAPPER, None)
    _specialPrint("############# FINISHED ZAPPING ########################")

def showMacAliasPath():
    fRawPath = Common.getRootDirectory()
    rawPath = fRawPath.getCanonicalPath()
    checkForStr = "/com.infinitekind.MoneydanceOSX/"
    replaceWithStr = "/Moneydance/"
    if (Platform.isOSX() and fRawPath.exists() and fRawPath.isDirectory() and isinstance(rawPath, basestring) and checkForStr in rawPath):
        return rawPath.replace(checkForStr, replaceWithStr)
    return None

class QuickDiag(Runnable):
    def __init__(self, mdRef, _thisis):
        self.mdRef = mdRef
        self.thisis = _thisis

    def run(self):
        msg = "\n"
        try:
            Thread.sleep(10 * 1000)     # Sleep to allow JVM Memory to settle down.....
            def convertBytesGBs(_size): return round((_size/(1000.0*1000.0*1000)),1)
            from com.moneydance.apps.md.controller import Common
            msg += "-----------------------------------------------------\n"
            msg += ("%s - quick information:\n" %(self.thisis.capitalize()))
            msg += "-----\n"

            msg += ("MD CONSOLE FILE LOCATION:       %s\n" %(returnPathStrings(self.mdRef.getLogFile())))
            msg += ("MD CONFIG/PREFERENCES LOCATION: %s\n" %(returnPathStrings(Common.getPreferencesFile())))

            if showMacAliasPath():
                msg += ("... Mac Finder path for above:  '%s'\n" %(showMacAliasPath()))

            msg += "-----\n"
            from com.moneydance.apps.md.controller.io import FileUtils
            destroyBackupChoices = self.mdRef.getPreferences().getSetting("backup.destroy_number", "5")
            returnedBackupType = self.mdRef.getPreferences().getSetting("backup.backup_type", "every_x_days")
            if returnedBackupType == "every_time":
                dailyBackupCheckbox = True
                destroyBackupChoices = 1
            elif returnedBackupType == "every_x_days":
                dailyBackupCheckbox = True
            else:
                dailyBackupCheckbox = False

            msg += ("BACKUPS - Save Daily:            %s\n" %(dailyBackupCheckbox))
            msg += ("BACKUPS - Keep no more than:     %s backups\n" %(destroyBackupChoices))
            msg += ("BACKUPS - Separate Backup Foldr: %s\n" %(self.mdRef.getPreferences().getBoolSetting("backup.location_selected", True)))

            MD_CONFIGDICT_BACKUP_TYPE = "backup.backup_type"
            backupFolder = FileUtils.getBackupDir(self.mdRef.getPreferences())
            backupType = self.mdRef.getPreferences().getSetting(MD_CONFIGDICT_BACKUP_TYPE, "every_x_days")
            autoBackup = (backupType != "no_backup")
            if not autoBackup:
                backupFileTxt = "** WARNING: AUTO BACKUPS ARE DISABLED **"
            elif backupFolder is None:
                backupFileTxt = "** ERROR: NO AUTO-BACKUP LOCATION DETECTED **"
            elif not isinstance(backupFolder, File) or not backupFolder.exists():
                backupFileTxt = "** ERROR: INVALID AUTO-BACKUP LOCATION DETECTED **"
            else:
                backupFileTxt = "(backup location exists)"

            msg += ("BACKUPS - Backup Folder:        %s %s\n" %(returnPathStrings(backupFolder), backupFileTxt))

            msg += ("..key - 'backup.location':      '%s'\n" %(self.mdRef.getPreferences().getSetting("backup.location", "<not set>")))
            msg += ("..key - 'backup.last_browsed':  '%s'\n" %(self.mdRef.getPreferences().getSetting("backup.last_browsed", "<not set>")))
            msg += ("..key - 'backup.last_saved':    '%s'\n" %(self.mdRef.getPreferences().getSetting("backup.last_saved", "<not set>")))
            msg += ("..key - '_default_backup_dir':  '%s'\n" %(self.mdRef.getPreferences().getSetting("_default_backup_dir", "<not set>")))

            msg += "-----\n"

            from java.util import Locale, TimeZone, Date
            sysLoc = Locale.getDefault()
            msg += ("System Default Locale Cty/Lang: '%s' / '%s'\n" %(sysLoc.getCountry(), sysLoc.getLanguage()))

            MDLoc = self.mdRef.getPreferences().getLocale()
            msg += ("MD Preference Locale Ctry/Lang: '%s' / '%s'\n" %(self.mdRef.getPreferences().getSetting("locale.country", ""), self.mdRef.getPreferences().getSetting("locale.language", "")))
            msg += ("MD Locale Cty/Lang:             '%s' / '%s'\n" %(MDLoc.getCountry(), MDLoc.getLanguage()))
            msg += ("Moneydance decimal point:       '%s'\n" %(self.mdRef.getPreferences().getSetting("decimal_character", ".")))

            # defaultTZ = TimeZone.getDefault()
            # msg += ("Default TimeZone (UTC offset)   '%s(%s) %s'\n" %(defaultTZ.getDisplayName(), defaultTZ.getRawOffset(), "** SummerTime+1" if defaultTZ.inDaylightTime(Date()) else ""))
            # msg += ("MD TimeZone                     '%s'\n" %(defaultTZ.getDisplayName(MDLoc)))
            msg += "-----\n"

            msg += ("MD EXECUTION MODE:               %s (%s)\n" %(self.mdRef.getExecutionMode(), ("AppletMode" if (self.mdRef.getExecutionMode() == self.mdRef.EXEC_MODE_APPLET) else "Normal")))
            # msg += ("OS PLATFORM:                     %s (%s)\n" %(System.getProperty("os.name"), System.getProperty("os.version")))
            # msg += ("ARCHITECTURE:                    %s\n" %(System.getProperty("os.arch")))

            for i in range(3):
                runTime = Runtime.getRuntime()
                maxMemory = Runtime.getRuntime().maxMemory()
                if i < 1: msg += ("JVM - Available processor cores: %s\n" %(runTime.availableProcessors()))
                msg += ("JVM - Maximum memory possible:   %s\n" %("{}".format("no limit") if (Long(maxMemory) == Long.MAX_VALUE) else "{:,} GB".format(convertBytesGBs(maxMemory))))
                msg += ("JVM - Total memory allocated:    {:,} GB (used {:,} GB / free {:,} GB)\n".format(convertBytesGBs(runTime.totalMemory()),
                                                                                                           convertBytesGBs(runTime.totalMemory() - runTime.freeMemory()),
                                                                                                           convertBytesGBs(runTime.freeMemory())))
                usage = ((runTime.totalMemory() - runTime.freeMemory()) / float(maxMemory))
                if  usage > 0.60:
                    msg += ("** MD memory usage is %s of max allocated to JVM%s **\n"
                            %("{:.0%}".format(usage),
                              ", consider editing .vmoptions file to increase '-Xmx' memory setting" if not Platform.isOSX() else ""))
                msg += "-----------------------------------------------------\n"
                msg += "\n"
                _specialPrint(msg)
                msg = "\n-----------------------------------------------------\n"
                Thread.sleep((i + 1) * 60 * 1000)     # Sleep and repeat.....

        except InterruptedException: pass

        except:
            if msg is not None and isinstance(msg, basestring):
                msg += "\n"
                _specialPrint(msg)

            _specialPrint("*** ERROR: %s quick information failed.... (%s, %s, line: %s)"
                          %(self.thisis.capitalize(), unicode(sys.exc_info()[0]), unicode(sys.exc_info()[1]), unicode(sys.exc_info()[2].tb_lineno)))


try:
    for t in Thread.getAllStackTraces().keySet():
        for checkName in ["toolbox_DownloadExtensionVersionData", "%s_init_quickdiag" %(_THIS_IS_)]:
            if checkName.lower() in t.getName().lower() and t.isAlive():
                _specialPrint("Interrupting old Thread '%s'(id: %s) which seems to still be alive" %(t, t.getId()))
                t.interrupt()
except: _specialPrint("%s - error interrupting old Thread... (continuing)" %(_THIS_IS_))

t = Thread(QuickDiag(moneydance, _THIS_IS_), "%s_init_quickdiag" %(_THIS_IS_))
t.setDaemon(True)
t.start()

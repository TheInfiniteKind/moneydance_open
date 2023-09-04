#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Initializer script for extension - this will only run from build 3056 onwards - otherwise ignored

###############################################################################
# MIT License
#
# Copyright (c) 2021-2023 Stuart Beesley - StuWareSoftSystems
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

_THIS_IS_ = "toolbox"
_HANDLE_EVENT_ENABLED_IF_REQUESTED = True
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


def _returnPathStrings(fileReference, arePathsIdentical=False):
    _pathStr = ""
    if fileReference is not None and isinstance(fileReference, File):
        _pathStr = "'%s'" %(fileReference.getAbsolutePath())
        if fileReference.getAbsolutePath() != fileReference.getCanonicalPath():
            _pathStr += " (alias to: '%s')" %(fileReference.getCanonicalPath())

    if arePathsIdentical: return (fileReference.getAbsolutePath() == fileReference.getCanonicalPath())
    return _pathStr


from java.lang.ref import WeakReference
_ALL_OBSERVED_BOOKS = []    # type: [[WeakReference, WeakReference, WeakReference, [WeakReference]]]

def _observeMoneydanceObjects(_observedBooksRef, _init=False):
    # type: ([[WeakReference, WeakReference, WeakReference, [WeakReference]]], bool) -> None
    _EXTN_PREF_KEY_ENABLE_OBSERVER = "enable_observer"
    if not _getExtensionGlobalPreferences().getBoolean(_EXTN_PREF_KEY_ENABLE_OBSERVER, False):
        if debug: _specialPrint("_observeMoneydanceObjects() - doing nothing as '%s' not set..." %(_EXTN_PREF_KEY_ENABLE_OBSERVER))
        return

    if _init: _specialPrint("@@ OBSERVER MODE HAS BEEN ENABLED - Will weakly watch retained references to key objects as they are created (use Toolbox CMD-/ to view) @@")

    _WRAPPERIDX = 0; _BOOKIDX = 1; _SYNCERIDX = 2; _SYNCTASKSIDX = 3
    _wrapper = MD_REF.getCurrentAccounts()
    _book = MD_REF.getCurrentAccountBook()       # This will always actually be _wrapper's .currentBook reference...
    _syncer = None
    wr_syncerThreads = []

    if _wrapper is None and _book is None:
        if debug: _specialPrint("OBSERVED - Wrapper and Book are None - ignoring...")
    elif _wrapper is None or _book is None:
        if debug: _specialPrint("@@ OBSERVED - LOGIC ERROR - Somehow Wrapper(%s) or Book(%s) are None - ignoring @@" %("None" if _wrapper is None else "not none", _book))
    else:
        lFoundRef = False
        iFoundObserved = -1
        _foundRefObjects = None
        for iFoundObserved in range(0, len(_observedBooksRef)):
            _foundRefObjects = _observedBooksRef[iFoundObserved]
            if _foundRefObjects[_WRAPPERIDX] is None: raise Exception("LOGIC ERROR: _foundRefObjects[%s] is None?!" %(_WRAPPERIDX))
            if _foundRefObjects[_BOOKIDX] is None: raise Exception("LOGIC ERROR: _foundRefObjects[%s] is None?!" %(_BOOKIDX))
            if _foundRefObjects[_BOOKIDX].get() is not None and _foundRefObjects[_BOOKIDX].get() is _book:
                lFoundRef = True
                break

        _syncer = _book.getSyncer()
        if _syncer is not None:
            try:
                sThread = _getFieldByReflection(_syncer, "syncThread")                                              # up to MD2023.2(5007)
                if sThread is not None:
                    wr_syncerThreads.append(WeakReference(sThread))
                del sThread
            except:
                sTasks = _getFieldByReflection(_syncer, "syncTasks")                                                # MD2023.2(5008 onwards)
                if sTasks is not None and len(sTasks) > 0:
                    for sTask in sTasks:
                        wr_syncerThreads.append(WeakReference(sTask))
                        del sTask
                del sTasks

        if lFoundRef:
            # Wrapper and Book will never change (other than going to None). If found, check Syncer as that can change in session (by user)
            if debug: _specialPrint("OBSERVED wrapper: (@%s) book: '%s'(@%s) - already found in WeakReference list..."
                                    %(Integer.toHexString(System.identityHashCode(_wrapper)), _book, Integer.toHexString(System.identityHashCode(_book))))
            if _syncer is not None and _foundRefObjects[_SYNCERIDX].get() is None:
                if debug: _specialPrint("... OBSERVED wrapper: (@%s) book: '%s'(@%s) - updating observed Syncer ref with: %s"
                                        %(Integer.toHexString(System.identityHashCode(_wrapper)), _book, Integer.toHexString(System.identityHashCode(_book)), _syncer))
                _observedBooksRef[iFoundObserved][_SYNCERIDX] = WeakReference(_syncer)

            if (len([_st.get() for _st in wr_syncerThreads if _st.get() is not None])
                    > len([_st.get() for _st in _foundRefObjects[_SYNCTASKSIDX] if _st.get() is not None])):
                if debug: _specialPrint("... OBSERVED wrapper: (@%s) book: '%s'(@%s) - updating observed Syncer Thread(s) ref(s) with: %s"
                                        %(Integer.toHexString(System.identityHashCode(_wrapper)), _book, Integer.toHexString(System.identityHashCode(_book)), wr_syncerThreads))
                _observedBooksRef[iFoundObserved][_SYNCTASKSIDX] = wr_syncerThreads
        else:
            _refsToAppend = [WeakReference(_wrapper), WeakReference(_book), WeakReference(_syncer), wr_syncerThreads]
            _observedBooksRef.append(_refsToAppend)
            if debug:
                _specialPrint("OBSERVED NEW (WeakReference) for wrapper: (@%s) book: '%s'(@%s), syncer: %s. syncerThread(s): %s"
                              %(Integer.toHexString(System.identityHashCode(_refsToAppend[_WRAPPERIDX].get())),
                                _refsToAppend[_BOOKIDX].get(),
                                Integer.toHexString(System.identityHashCode(_refsToAppend[_BOOKIDX].get())),
                                _refsToAppend[_SYNCERIDX].get(),
                                [_st.get() for _st in _refsToAppend[_SYNCTASKSIDX]]))

            del _refsToAppend

        del _foundRefObjects

    if debug:
        _specialPrint("OBSERVED - Observer now contains %s entries)" %(len(_ALL_OBSERVED_BOOKS)))
        for _foundRefObjects in _ALL_OBSERVED_BOOKS:
            _specialPrint("...OBSERVED ENTRY: wrapper: (@%s) book: '%s'(@%s), syncer: %s. syncerThreads: %s"
                          %(Integer.toHexString(System.identityHashCode(_foundRefObjects[_WRAPPERIDX].get())),
                            _foundRefObjects[_BOOKIDX].get(),
                            Integer.toHexString(System.identityHashCode(_foundRefObjects[_BOOKIDX].get())),
                            _foundRefObjects[_SYNCERIDX].get(),
                            [_st.get() for _st in _foundRefObjects[_SYNCTASKSIDX]]))
            del _foundRefObjects

    del _wrapper, _book, _syncer, wr_syncerThreads


_observeMoneydanceObjects(_ALL_OBSERVED_BOOKS, _init=True)


_TOOLBOX_PREFERENCES_ZAPPER = "toolbox_preferences_zapper"

keysToZap = MD_REF.getPreferences().getVectorSetting(_TOOLBOX_PREFERENCES_ZAPPER, None)
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
        MD_REF.getPreferences().setSetting(zapKey, None)
    MD_REF.getPreferences().setSetting(_TOOLBOX_PREFERENCES_ZAPPER, None)
    _specialPrint("############# FINISHED ZAPPING ########################")

def _showMacAliasPath():
    fRawPath = Common.getRootDirectory()
    rawPath = fRawPath.getCanonicalPath()
    checkForStr = "/com.infinitekind.MoneydanceOSX/"
    replaceWithStr = "/Moneydance/"
    if (Platform.isOSX() and fRawPath.exists() and fRawPath.isDirectory() and isinstance(rawPath, basestring) and checkForStr in rawPath):
        return rawPath.replace(checkForStr, replaceWithStr)
    return None

def _setFieldByReflection(theObj, fieldName, newValue):
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
    return reflectField.set(theObj if not isStatic else None, newValue)

def _invokeMethodByReflection(theObj, methodName, params, *args):
    try: theClass = theObj.getClass()
    except TypeError: theClass = theObj     # This catches where the object is already the Class
    reflectMethod = None
    while theClass is not None:
        try:
            if params is None:
                reflectMethod = theClass.getDeclaredMethod(methodName)
                break
            else:
                reflectMethod = theClass.getDeclaredMethod(methodName, params)
                break
        except NoSuchMethodException:
            theClass = theClass.getSuperclass()
    if reflectMethod is None: raise Exception("ERROR: could not find method: %s in class hierarchy" %(methodName))
    reflectMethod.setAccessible(True)
    return reflectMethod.invoke(theObj, *args)


from javax.swing import SwingUtilities
def _genericSwingEDTRunner(ifOffEDTThenRunNowAndWait, ifOnEDTThenRunNowAndWait, codeblock, *args):
    isOnEDT = SwingUtilities.isEventDispatchThread()

    class GenericSwingEDTRunner(Runnable):

        def __init__(self, _codeblock, arguments):
            self.codeBlock = _codeblock
            self.params = arguments

        def run(self):
            if debug: _specialPrint(">>> _genericSwingEDTRunner() >> Executed codebock on the EDT <<<")
            self.codeBlock(*self.params)

    _gser = GenericSwingEDTRunner(codeblock, args)

    if ((isOnEDT and not ifOnEDTThenRunNowAndWait) or (not isOnEDT and not ifOffEDTThenRunNowAndWait)):
        SwingUtilities.invokeLater(_gser)
    elif not isOnEDT:
        SwingUtilities.invokeAndWait(_gser)
    else:
        _gser.run()


########################################################################################################################
def _disableMoneyForesight():
    _EXTN_PREF_KEY_DISABLE_FORESIGHT = "disable_moneyforesight"
    if not _getExtensionGlobalPreferences().getBoolean(_EXTN_PREF_KEY_DISABLE_FORESIGHT, False):
        if debug: _specialPrint("@@@ config.dict '%s' setting not set... skipping any disable MoneyForesight action....." %(_EXTN_PREF_KEY_DISABLE_FORESIGHT))
        return
    elif float(MD_REF.getBuild()) < 3095:    # First bundled in MD2021.2(3095)
        if debug: _specialPrint("@@@ Build too old for MoneyForesight to exist - skipping any disable action.....")
        return
    else:
        _mfsKey = "moneyforesight"
        _mfs = MD_REF.getModuleForID(_mfsKey)
        if _mfs is None:
            _specialPrint("@@@ MoneyForesight extension not detected / loaded to disable / unload @@@")
        else:
            try:
                # Cleanup and unload module...
                from com.moneydance.apps.md.controller import FeatureModule
                if MD_REF.getCurrentAccountBook() is not None: _mfs.cleanup()
                for _mfsFieldStr in ["favouritesRepository", "accountSetModelRepository", "foresightUserPreferences", "accountHelper", "reminderReviewHomePage"]:
                    _setFieldByReflection(_mfs, _mfsFieldStr, None)
                _invokeMethodByReflection(MD_REF, "unloadModule", [FeatureModule], [_mfs])

                del FeatureModule, _mfsFieldStr
                _specialPrint("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
                _specialPrint("@@@ MoneyForesight disabled / unloaded! @@@")
                _specialPrint("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
            except:
                _specialPrint("*** ERROR: %s - MoneyForesight disable actions FAILED....: (%s, %s, line: %s)"
                              %(_THIS_IS_.capitalize(), unicode(sys.exc_info()[0]), unicode(sys.exc_info()[1]), unicode(sys.exc_info()[2].tb_lineno)))

        # Now clean up summary / home screen...
        from com.infinitekind.util import StreamVector
        _prefs = MD_REF.getPreferences()
        _lefties = _prefs.getVectorSetting(_prefs.GUI_VIEW_LEFT, StreamVector())
        _righties = _prefs.getVectorSetting(_prefs.GUI_VIEW_RIGHT, StreamVector())
        _unused = _prefs.getVectorSetting(_prefs.GUI_VIEW_UNUSED, StreamVector())
        _anyLeftRightChanges = False
        for _left_right in [_lefties, _righties]:
            _removeList = []
            for _widgetID in _left_right:
                if _mfsKey in _widgetID: _removeList.append(_widgetID)
            for _widgetID in _removeList:
                _left_right.remove(_widgetID)
                if _widgetID not in _unused:
                    _unused.add(_widgetID)
                _anyLeftRightChanges = True
                if debug: _specialPrint("@@ Removed '%s' from %s (and added to unused)" %(_widgetID, type(_left_right)))
            del _left_right
        if _anyLeftRightChanges:
            _prefs.setSetting(_prefs.GUI_VIEW_LEFT, _lefties)
            _prefs.setSetting(_prefs.GUI_VIEW_RIGHT, _righties)
            _prefs.setSetting(_prefs.GUI_VIEW_UNUSED, _unused)
            _specialPrint("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
            _specialPrint("@@@ Saved updated lefties/righties etc. @@@")
            _specialPrint("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

        # Now refresh the home screen...
        if _mfs is not None or _anyLeftRightChanges:
            if MD_REF.getCurrentAccountBook() is not None:
                _genericSwingEDTRunner(False, False, MD_REF.getPreferences().firePreferencesUpdated)

        del _mfs, _mfsKey, _prefs, _anyLeftRightChanges
########################################################################################################################


_disableMoneyForesight()


from java.io import File

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

            msg += ("MD CONSOLE FILE LOCATION:       %s\n" %(_returnPathStrings(self.mdRef.getLogFile())))
            msg += ("MD CONFIG/PREFERENCES LOCATION: %s\n" %(_returnPathStrings(Common.getPreferencesFile())))

            if _showMacAliasPath():
                msg += ("... Mac Finder path for above:  '%s'\n" %(_showMacAliasPath()))

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

            msg += ("BACKUPS - Backup Folder:        %s %s\n" %(_returnPathStrings(backupFolder), backupFileTxt))

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
del t

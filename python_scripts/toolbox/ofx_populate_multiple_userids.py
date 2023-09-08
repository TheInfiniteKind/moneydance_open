#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# ofx_populate_multiple_userids.py (build 13) - Author - Stuart Beesley - StuWareSoftSystems 2021-2023

# This script allows you to add multiple UserIDs to a working OFX profile

# DISCLAIMER >> PLEASE ALWAYS BACKUP YOUR DATA BEFORE MAKING CHANGES (Menu>Export Backup will achieve this)
#               You use this at your own risk. I take no responsibility for its usage..!

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
# Use in Moneydance Menu Window->Show Moneybot Console >> Open Script >> RUN

# build: 1 - Initial preview release..... Based upon ofx_create_new_usaa_bank_profile.py (now deprecated)
# build: 2 - Enhanced to run within Toolbox
# build: 3 - Enhanced further to run within Toolbox
# build: 4 - Tweaks - allow when downgraded from MD2022; manually update mapping table if on MD2021 or lower....
# build: 5 - Common code tweaks
# build: 6 - Common code tweaks
# build: 7 - Common code - eliminating globals
# build: 8 - Tweaks
# build: 9 - FileDialog() (refer: java.desktop/sun/lwawt/macosx/CFileDialog.java) seems to no longer use "com.apple.macos.use-file-dialog-packages" in favor of "apple.awt.use-file-dialog-packages" since Monterrey...
# build: 10 - MD2023 fixes to common code...
# build: 11 - Common code tweaks
# build: 12 - Common code tweaks
# build: 13 - Tweaks

# CUSTOMIZE AND COPY THIS ##############################################################################################
# CUSTOMIZE AND COPY THIS ##############################################################################################
# CUSTOMIZE AND COPY THIS ##############################################################################################

# SET THESE LINES
myModuleID = u"ofx_populate_multiple_userids"
version_build = "13"
MIN_BUILD_REQD = 1904                                               # Check for builds less than 1904 / version < 2019.4
_I_CAN_RUN_AS_MONEYBOT_SCRIPT = True

global moneydance, moneydance_ui, moneydance_extension_loader, moneydance_extension_parameter

global MD_REF, MD_REF_UI
if "moneydance" in globals(): MD_REF = moneydance           # Make my own copy of reference as MD removes it once main thread ends.. Don't use/hold on to _data variable
if "moneydance_ui" in globals(): MD_REF_UI = moneydance_ui  # Necessary as calls to .getUI() will try to load UI if None - we don't want this....
if "MD_REF" not in globals(): raise Exception("ERROR: 'moneydance' / 'MD_REF' NOT set!?")
if "MD_REF_UI" not in globals(): raise Exception("ERROR: 'moneydance_ui' / 'MD_REF_UI' NOT set!?")

# Nuke unwanted (direct/indirect) reference(s) to AccountBook etc....
if "moneydance_data" in globals():
    moneydance_data = None
    del moneydance_data

if "moneybot" in globals():
    moneybot = None
    del moneybot

from java.lang import Boolean
global debug
if "debug" not in globals():
    # if Moneydance is launched with -d, or this property is set, or extension is being (re)installed with Console open.
    debug = (False or MD_REF.DEBUG or Boolean.getBoolean("moneydance.debug"))

global ofx_populate_multiple_userids_frame_
# SET LINES ABOVE ^^^^

# COPY >> START
import __builtin__ as builtins

def checkObjectInNameSpace(objectName):
    """Checks globals() and builtins for the existence of the object name (used for StuWareSoftSystems' bootstrap)"""
    if objectName is None or not isinstance(objectName, basestring) or objectName == u"": return False
    if objectName in globals(): return True
    return objectName in dir(builtins)


if MD_REF is None: raise Exception(u"CRITICAL ERROR - moneydance object/variable is None?")
if checkObjectInNameSpace(u"moneydance_extension_loader"):
    MD_EXTENSION_LOADER = moneydance_extension_loader
else:
    MD_EXTENSION_LOADER = None

if (u"__file__" in globals() and __file__.startswith(u"bootstrapped_")): del __file__       # Prevent bootstrapped loader setting this....

from java.lang import System, Runnable
from javax.swing import JFrame, SwingUtilities, SwingWorker
from java.awt.event import WindowEvent

class QuickAbortThisScriptException(Exception): pass

class MyJFrame(JFrame):

    def __init__(self, frameTitle=None):
        super(JFrame, self).__init__(frameTitle)
        self.disposing = False
        self.myJFrameVersion = 4
        self.isActiveInMoneydance = False
        self.isRunTimeExtension = False
        self.MoneydanceAppListener = None
        self.HomePageViewObj = None

    def dispose(self):
        # This removes all content as Java/Swing (often) retains the JFrame reference in memory...
        if self.disposing: return
        try:
            self.disposing = True
            self.getContentPane().removeAll()
            if self.getJMenuBar() is not None: self.setJMenuBar(None)
            super(self.__class__, self).dispose()
        except:
            _msg = "%s: ERROR DISPOSING OF FRAME: %s\n" %(myModuleID, self)
            print(_msg); System.err.write(_msg)
        finally:
            self.disposing = False

class GenericWindowClosingRunnable(Runnable):

    def __init__(self, theFrame):
        self.theFrame = theFrame

    def run(self):
        self.theFrame.setVisible(False)
        self.theFrame.dispatchEvent(WindowEvent(self.theFrame, WindowEvent.WINDOW_CLOSING))

class GenericDisposeRunnable(Runnable):
    def __init__(self, theFrame):
        self.theFrame = theFrame

    def run(self):
        self.theFrame.setVisible(False)
        self.theFrame.dispose()

class GenericVisibleRunnable(Runnable):
    def __init__(self, theFrame, lVisible=True, lToFront=False):
        self.theFrame = theFrame
        self.lVisible = lVisible
        self.lToFront = lToFront

    def run(self):
        self.theFrame.setVisible(self.lVisible)
        if self.lVisible and self.lToFront:
            if self.theFrame.getExtendedState() == JFrame.ICONIFIED:
                self.theFrame.setExtendedState(JFrame.NORMAL)
            self.theFrame.toFront()

def getMyJFrame(moduleName):
    try:
        frames = JFrame.getFrames()
        for fr in frames:
            if (fr.getName().lower().startswith(u"%s_main" %moduleName)
                    and (type(fr).__name__ == MyJFrame.__name__ or type(fr).__name__ == u"MyCOAWindow")  # isinstance() won't work across namespaces
                    and fr.isActiveInMoneydance):
                _msg = "%s: Found live frame: %s (MyJFrame() version: %s)\n" %(myModuleID,fr.getName(),fr.myJFrameVersion)
                print(_msg); System.err.write(_msg)
                if fr.isRunTimeExtension:
                    _msg = "%s: ... and this is a run-time self-installed extension too...\n" %(myModuleID)
                    print(_msg); System.err.write(_msg)
                return fr
    except:
        _msg = "%s: Critical error in getMyJFrame(); caught and ignoring...!\n" %(myModuleID)
        print(_msg); System.err.write(_msg)
    return None


frameToResurrect = None
try:
    # So we check own namespace first for same frame variable...
    if (u"%s_frame_"%myModuleID in globals()
            and (isinstance(ofx_populate_multiple_userids_frame_, MyJFrame)                 # EDIT THIS
                 or type(ofx_populate_multiple_userids_frame_).__name__ == u"MyCOAWindow")  # EDIT THIS
            and ofx_populate_multiple_userids_frame_.isActiveInMoneydance):                 # EDIT THIS
        frameToResurrect = ofx_populate_multiple_userids_frame_                             # EDIT THIS
    else:
        # Now check all frames in the JVM...
        getFr = getMyJFrame( myModuleID )
        if getFr is not None:
            frameToResurrect = getFr
        del getFr
except:
    msg = "%s: Critical error checking frameToResurrect(1); caught and ignoring...!\n" %(myModuleID)
    print(msg); System.err.write(msg)

# ############################
# Trap startup conditions here.... The 'if's pass through to oblivion (and thus a clean exit)... The final 'else' actually runs the script
if int(MD_REF.getBuild()) < MIN_BUILD_REQD:     # Check for builds less than 1904 (version 2019.4) or build 3056 accordingly
    msg = "SORRY YOUR MONEYDANCE VERSION IS TOO OLD FOR THIS SCRIPT/EXTENSION (min build %s required)" %(MIN_BUILD_REQD)
    print(msg); System.err.write(msg)
    try:    MD_REF_UI.showInfoMessage(msg)
    except: raise Exception(msg)

elif frameToResurrect and frameToResurrect.isRunTimeExtension:
    msg = "%s: Sorry - runtime extension already running. Please uninstall/reinstall properly. Must be on build: %s onwards. Now exiting script!\n" %(myModuleID, MIN_BUILD_REQD)
    print(msg); System.err.write(msg)
    try: MD_REF_UI.showInfoMessage(msg)
    except: raise Exception(msg)

elif not _I_CAN_RUN_AS_MONEYBOT_SCRIPT and u"__file__" in globals():
    msg = "%s: Sorry - this script cannot be run in Moneybot console. Please install mxt and run extension properly. Must be on build: %s onwards. Now exiting script!\n" %(myModuleID, MIN_BUILD_REQD)
    print(msg); System.err.write(msg)
    try: MD_REF_UI.showInfoMessage(msg)
    except: raise Exception(msg)

elif not _I_CAN_RUN_AS_MONEYBOT_SCRIPT and not checkObjectInNameSpace(u"moneydance_extension_loader"):
    msg = "%s: Error - moneydance_extension_loader seems to be missing? Must be on build: %s onwards. Now exiting script!\n" %(myModuleID, MIN_BUILD_REQD)
    print(msg); System.err.write(msg)
    try: MD_REF_UI.showInfoMessage(msg)
    except: raise Exception(msg)

elif frameToResurrect:  # and it's active too...
    try:
        msg = "%s: Detected that %s is already running..... Attempting to resurrect..\n" %(myModuleID, myModuleID)
        print(msg); System.err.write(msg)
        SwingUtilities.invokeLater(GenericVisibleRunnable(frameToResurrect, True, True))
    except:
        msg  = "%s: Failed to resurrect main Frame.. This duplicate Script/extension is now terminating.....\n" %(myModuleID)
        print(msg); System.err.write(msg)
        raise Exception(msg)

else:
    del frameToResurrect
    msg = "%s: Startup conditions passed (and no other instances of this program detected). Now executing....\n" %(myModuleID)
    print(msg); System.err.write(msg)

    # COMMON IMPORTS #######################################################################################################
    # COMMON IMPORTS #######################################################################################################
    # COMMON IMPORTS #######################################################################################################

    global sys
    if "sys" not in globals():
        # NOTE: As of MD2022(4040), python.getSystemState().setdefaultencoding("utf8") is called on the python interpreter at script launch...
        import sys
        reload(sys)                     # Dirty hack to eliminate UTF-8 coding errors
        sys.setdefaultencoding('utf8')  # Without this str() fails on unicode strings...

    import os
    import os.path
    import codecs
    import inspect
    import pickle
    import platform
    import csv
    import datetime
    import traceback
    import subprocess

    from org.python.core.util import FileUtil

    from com.moneydance.util import Platform
    from com.moneydance.awt import JTextPanel, GridC, JDateField
    from com.moneydance.apps.md.view.gui import MDImages

    from com.infinitekind.util import DateUtil, CustomDateFormat, StringUtils

    from com.infinitekind.moneydance.model import *
    from com.infinitekind.moneydance.model import AccountUtil, AcctFilter, CurrencyType, CurrencyUtil
    from com.infinitekind.moneydance.model import Account, Reminder, ParentTxn, SplitTxn, TxnSearch, InvestUtil, TxnUtil

    from com.moneydance.apps.md.controller import AccountBookWrapper, AppEventManager                                   # noqa
    from com.infinitekind.moneydance.model import AccountBook
    from com.infinitekind.tiksync import SyncRecord                                                                     # noqa
    from com.infinitekind.util import StreamTable                                                                       # noqa

    from javax.swing import JButton, JScrollPane, WindowConstants, JLabel, JPanel, JComponent, KeyStroke, JDialog, JComboBox
    from javax.swing import JOptionPane, JTextArea, JMenuBar, JMenu, JMenuItem, AbstractAction, JCheckBoxMenuItem, JFileChooser
    from javax.swing import JTextField, JPasswordField, Box, UIManager, JTable, JCheckBox, JRadioButton, ButtonGroup
    from javax.swing.text import PlainDocument
    from javax.swing.border import EmptyBorder
    from javax.swing.filechooser import FileFilter

    exec("from javax.print import attribute")       # IntelliJ doesnt like the use of 'print' (as it's a keyword). Messy, but hey!
    exec("from java.awt.print import PrinterJob")   # IntelliJ doesnt like the use of 'print' (as it's a keyword). Messy, but hey!
    global attribute, PrinterJob

    from java.awt.datatransfer import StringSelection
    from javax.swing.text import DefaultHighlighter
    from javax.swing.event import AncestorListener

    from java.awt import Color, Dimension, FileDialog, FlowLayout, Toolkit, Font, GridBagLayout, GridLayout
    from java.awt import BorderLayout, Dialog, Insets, Point
    from java.awt.event import KeyEvent, WindowAdapter, InputEvent
    from java.util import Date, Locale

    from java.text import DecimalFormat, SimpleDateFormat, MessageFormat
    from java.util import Calendar, ArrayList
    from java.lang import Thread, IllegalArgumentException, String, Integer, Long
    from java.lang import Double, Math, Character, NoSuchFieldException, NoSuchMethodException, Boolean
    from java.lang.reflect import Modifier
    from java.io import FileNotFoundException, FilenameFilter, File, FileInputStream, FileOutputStream, IOException, StringReader
    from java.io import BufferedReader, InputStreamReader
    from java.nio.charset import Charset

    if int(MD_REF.getBuild()) >= 3067:
        from com.moneydance.apps.md.view.gui.theme import ThemeInfo                                                     # noqa
    else:
        from com.moneydance.apps.md.view.gui.theme import Theme as ThemeInfo                                            # noqa

    if isinstance(None, (JDateField,CurrencyUtil,Reminder,ParentTxn,SplitTxn,TxnSearch, JComboBox, JCheckBox,
                         AccountBook, AccountBookWrapper, Long, Integer, Boolean,
                         JTextArea, JMenuBar, JMenu, JMenuItem, JCheckBoxMenuItem, JFileChooser, JDialog,
                         JButton, FlowLayout, InputEvent, ArrayList, File, IOException, StringReader, BufferedReader,
                         InputStreamReader, Dialog, JTable, BorderLayout, Double, InvestUtil, JRadioButton, ButtonGroup,
                         AccountUtil, AcctFilter, CurrencyType, Account, TxnUtil, JScrollPane, WindowConstants, JFrame,
                         JComponent, KeyStroke, AbstractAction, UIManager, Color, Dimension, Toolkit, KeyEvent, GridLayout,
                         WindowAdapter, CustomDateFormat, SimpleDateFormat, Insets, FileDialog, Thread, SwingWorker)): pass
    if codecs.BOM_UTF8 is not None: pass
    if csv.QUOTE_ALL is not None: pass
    if datetime.MINYEAR is not None: pass
    if Math.max(1,1): pass
    # END COMMON IMPORTS ###################################################################################################

    # COMMON GLOBALS #######################################################################################################
    # All common globals have now been eliminated :->
    # END COMMON GLOBALS ###################################################################################################
    # COPY >> END

    # SET THESE VARIABLES FOR ALL SCRIPTS ##################################################################################
    if "GlobalVars" in globals():   # Prevent wiping if 'buddy' extension - like Toolbox - is running too...
        global GlobalVars
    else:
        class GlobalVars:        # Started using this method for storing global variables from August 2021
            CONTEXT = MD_REF
            defaultPrintService = None
            defaultPrinterAttributes = None
            defaultPrintFontSize = None
            defaultPrintLandscape = None
            defaultDPI = 72     # NOTE: 72dpi is Java2D default for everything; just go with it. No easy way to change
            STATUS_LABEL = None
            DARK_GREEN = Color(0, 192, 0)
            resetPickleParameters = False
            decimalCharSep = "."
            lGlobalErrorDetected = False
            MYPYTHON_DOWNLOAD_URL = "https://yogi1967.github.io/MoneydancePythonScripts/"
            i_am_an_extension_so_run_headless = None
            parametersLoadedFromFile = {}
            thisScriptName = None
            MD_MDPLUS_BUILD = 4040                          # 2022.0
            MD_ALERTCONTROLLER_BUILD = 4077                 # 2022.3
            def __init__(self): pass    # Leave empty

            class Strings:
                def __init__(self): pass    # Leave empty

    GlobalVars.MD_PREFERENCE_KEY_CURRENT_THEME = "gui.current_theme"
    GlobalVars.thisScriptName = u"%s.py(Extension)" %(myModuleID)

    # END SET THESE VARIABLES FOR ALL SCRIPTS ##############################################################################

    # >>> THIS SCRIPT'S IMPORTS ############################################################################################
    from com.infinitekind.moneydance.model import OnlineService
    from com.moneydance.apps.md.view.gui import MDAccountProxy
    from java.net import URLEncoder
    from com.infinitekind.moneydance.model import OnlineTxnList
    from com.infinitekind.tiksync import SyncableItem
    from java.util import UUID
    from com.infinitekind.util import StringUtils

    from javax.swing import JList, ListSelectionModel
    from com.moneydance.awt import GridC
    from javax.swing import DefaultListCellRenderer
    from javax.swing import BorderFactory
    from javax.swing import DefaultListSelectionModel
    from com.infinitekind.moneydance.model import OnlineAccountInfo
    from java.lang import String
    # >>> END THIS SCRIPT'S IMPORTS ########################################################################################

    # >>> THIS SCRIPT'S GLOBALS ########################################################################################
    GlobalVars.Strings.OFX_LAST_TXN_UPDATE = "ofx_last_txn_update"
    GlobalVars.MD_MULTI_OFX_TXN_DNLD_DATES_BUILD = 4074
    # >>> END THIS SCRIPT'S GLOBALS ####################################################################################

    # COPY >> START
    # COMMON CODE ######################################################################################################
    # COMMON CODE ################# VERSION 108 ########################################################################
    # COMMON CODE ######################################################################################################
    GlobalVars.i_am_an_extension_so_run_headless = False
    try:
        GlobalVars.thisScriptName = os.path.basename(__file__)
    except:
        GlobalVars.i_am_an_extension_so_run_headless = True

    scriptExit = """
----------------------------------------------------------------------------------------------------------------------
Thank you for using %s!
The author has other useful Extensions / Moneybot Python scripts available...:

Extension (.mxt) format only:
Toolbox: View Moneydance settings, diagnostics, fix issues, change settings and much more
         + Extension menus: Total selected txns; Move Investment Txns; Zap md+/ofx/qif (default) memo fields;

Custom Balances (net_account_balances): Summary Page (HomePage) widget. Display the total of selected Account Balances

Extension (.mxt) and Script (.py) Versions available:
Extract Data: Extract various data to screen /or csv.. (also auto-extract mode): Includes:
    - StockGlance2020: Securities/stocks, total by security across investment accounts;
    - Reminders; Account register transaction (attachments optional);
    - Investment transactions (attachments optional); Security Balances; Currency price history;
    - Decrypt / extract raw 'Trunk' file; Extract raw data as JSON file; All attachments;

List Future Reminders:                  View future reminders on screen. Allows you to set the days to look forward
Security Performance Graph:             Graphs selected securities, calculating relative price performance as percentage
Accounts Categories Mega Search Window: Combines MD Menu> Tools>Accounts/Categories and adds Quick Search box/capability

A collection of useful ad-hoc scripts (zip file)
useful_scripts:                         Just unzip and select the script you want for the task at hand...

Visit: %s (Author's site)
----------------------------------------------------------------------------------------------------------------------
""" %(GlobalVars.thisScriptName, GlobalVars.MYPYTHON_DOWNLOAD_URL)

    def cleanup_references():
        global MD_REF, MD_REF_UI, MD_EXTENSION_LOADER
        # myPrint("DB","About to delete reference to MD_REF, MD_REF_UI and MD_EXTENSION_LOADER....!")
        # del MD_REF, MD_REF_UI, MD_EXTENSION_LOADER

    def load_text_from_stream_file(theStream):
        myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()")

        cs = Charset.forName("UTF-8")

        istream = theStream

        if not istream:
            myPrint("B","... Error - the input stream is None")
            return "<NONE>"

        fileContents = ""
        istr = bufr = None
        try:
            istr = InputStreamReader(istream, cs)
            bufr = BufferedReader(istr)
            while True:
                line = bufr.readLine()
                if line is not None:
                    line += "\n"                   # not very efficient - should convert this to "\n".join() to contents
                    fileContents+=line
                    continue
                break
            fileContents+="\n<END>"
        except:
            myPrint("B", "ERROR reading from input stream... ")
            dump_sys_error_to_md_console_and_errorlog()

        try: bufr.close()
        except: pass

        try: istr.close()
        except: pass

        try: istream.close()
        except: pass

        myPrint("DB", "Exiting ", inspect.currentframe().f_code.co_name, "()")

        return fileContents

    # P=Display on Python Console, J=Display on MD (Java) Console Error Log, B=Both, D=If Debug Only print, DB=print both
    def myPrint(where, *args):
        if where[0] == "D" and not debug: return

        try:
            printString = ""
            for what in args:
                printString += "%s " %what
            printString = printString.rstrip(" ")

            if where == "P" or where == "B" or where[0] == "D":
                if not GlobalVars.i_am_an_extension_so_run_headless:
                    try:
                        print(printString)
                    except:
                        print("Error writing to screen...")
                        dump_sys_error_to_md_console_and_errorlog()

            if where == "J" or where == "B" or where == "DB":
                dt = datetime.datetime.now().strftime("%Y/%m/%d-%H:%M:%S")
                try:
                    System.err.write(GlobalVars.thisScriptName + ":" + dt + ": ")
                    System.err.write(printString)
                    System.err.write("\n")
                except:
                    System.err.write(GlobalVars.thisScriptName + ":" + dt + ": " + "Error writing to console")
                    dump_sys_error_to_md_console_and_errorlog()

        except IllegalArgumentException:
            myPrint("B","ERROR - Probably on a multi-byte character..... Will ignore as code should just continue (PLEASE REPORT TO DEVELOPER).....")
            dump_sys_error_to_md_console_and_errorlog()

        return


    if debug: myPrint("B", "** DEBUG IS ON **")

    def dump_sys_error_to_md_console_and_errorlog(lReturnText=False):

        tb = traceback.format_exc()
        trace = traceback.format_stack()
        theText =  ".\n" \
                   "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n" \
                   "@@@@@ Unexpected error caught!\n".upper()
        theText += tb
        for trace_line in trace: theText += trace_line
        theText += "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
        myPrint("B", theText)
        if lReturnText: return theText
        return

    def safeStr(_theText): return ("%s" %(_theText))

    def pad(theText, theLength, padChar=u" "):
        if not isinstance(theText, (unicode, str)): theText = safeStr(theText)
        theText = theText[:theLength].ljust(theLength, padChar)
        return theText

    def rpad(theText, theLength, padChar=u" "):
        if not isinstance(theText, (unicode, str)): theText = safeStr(theText)
        theText = theText[:theLength].rjust(theLength, padChar)
        return theText

    def cpad(theText, theLength, padChar=u" "):
        if not isinstance(theText, (unicode, str)): theText = safeStr(theText)
        if len(theText) >= theLength: return theText[:theLength]
        padLength = int((theLength - len(theText)) / 2)
        theText = theText[:theLength]
        theText = ((padChar * padLength)+theText+(padChar * padLength))[:theLength]
        return theText

    myPrint("B", GlobalVars.thisScriptName, ": Python Script Initialising.......", "Build:", version_build)

    def getMonoFont():
        try:
            theFont = MD_REF.getUI().getFonts().code
            # if debug: myPrint("B","Success setting Font set to Moneydance code: %s" %theFont)
        except:
            theFont = Font("monospaced", Font.PLAIN, 15)
            if debug: myPrint("B","Failed to Font set to Moneydance code - So using: %s" %theFont)

        return theFont

    def isOSXVersionAtLeast(compareVersion):
        # type: (basestring) -> bool
        """Pass a string in the format 'x.x.x'. Will check that this MacOSX version is at least that version. The 3rd micro number is optional"""

        try:
            if not Platform.isOSX(): return False

            def convertVersion(convertString):
                _os_major = _os_minor = _os_micro = 0
                _versionNumbers = []

                for versionPart in StringUtils.splitIntoList(convertString, '.'):
                    strippedPart = StringUtils.stripNonNumbers(versionPart, '.')
                    if (StringUtils.isInteger(strippedPart)):
                        _versionNumbers.append(Integer.valueOf(Integer.parseInt(strippedPart)))
                    else:
                        _versionNumbers.append(0)

                if len(_versionNumbers) >= 1: _os_major = max(0, _versionNumbers[0])
                if len(_versionNumbers) >= 2: _os_minor = max(0, _versionNumbers[1])
                if len(_versionNumbers) >= 3: _os_micro = max(0, _versionNumbers[2])

                return _os_major, _os_minor, _os_micro


            os_major, os_minor, os_micro = convertVersion(System.getProperty("os.version", "0.0.0"))
            myPrint("DB", "MacOS Version number(s): %s.%s.%s" %(os_major, os_minor, os_micro))

            if not isinstance(compareVersion, basestring) or len(compareVersion) < 1:
                myPrint("B", "ERROR: Invalid compareVersion of '%s' passed - returning False" %(compareVersion))
                return False

            chk_os_major, chk_os_minor, chk_os_micro = convertVersion(compareVersion)
            myPrint("DB", "Comparing against Version(s): %s.%s.%s" %(chk_os_major, chk_os_minor, chk_os_micro))


            if os_major < chk_os_major: return False
            if os_major > chk_os_major: return True

            if os_minor < chk_os_minor: return False
            if os_minor > chk_os_minor: return True

            if os_micro < chk_os_micro: return False
            return True

        except:
            myPrint("B", "ERROR: isOSXVersionAtLeast() failed - returning False")
            dump_sys_error_to_md_console_and_errorlog()
            return False

    def isOSXVersionCheetahOrLater():       return isOSXVersionAtLeast("10.0")
    def isOSXVersionPumaOrLater():          return isOSXVersionAtLeast("10.1")
    def isOSXVersionJaguarOrLater():        return isOSXVersionAtLeast("10.2")
    def isOSXVersionPantherOrLater():       return isOSXVersionAtLeast("10.3")
    def isOSXVersionTigerOrLater():         return isOSXVersionAtLeast("10.4")
    def isOSXVersionLeopardOrLater():       return isOSXVersionAtLeast("10.5")
    def isOSXVersionSnowLeopardOrLater():   return isOSXVersionAtLeast("10.6")
    def isOSXVersionLionOrLater():          return isOSXVersionAtLeast("10.7")
    def isOSXVersionMountainLionOrLater():  return isOSXVersionAtLeast("10.8")
    def isOSXVersionMavericksOrLater():     return isOSXVersionAtLeast("10.9")
    def isOSXVersionYosemiteOrLater():      return isOSXVersionAtLeast("10.10")
    def isOSXVersionElCapitanOrLater():     return isOSXVersionAtLeast("10.11")
    def isOSXVersionSierraOrLater():        return isOSXVersionAtLeast("10.12")
    def isOSXVersionHighSierraOrLater():    return isOSXVersionAtLeast("10.13")
    def isOSXVersionMojaveOrLater():        return isOSXVersionAtLeast("10.14")
    def isOSXVersionCatalinaOrLater():      return isOSXVersionAtLeast("10.15")
    def isOSXVersionBigSurOrLater():        return isOSXVersionAtLeast("10.16")  # BigSur is officially 11.0, but started at 10.16
    def isOSXVersionMontereyOrLater():      return isOSXVersionAtLeast("12.0")
    def isOSXVersionVenturaOrLater():       return isOSXVersionAtLeast("13.0")

    def get_home_dir():
        homeDir = None

        # noinspection PyBroadException
        try:
            if Platform.isOSX():
                homeDir = System.getProperty(u"UserHome")  # On a Mac in a Java VM, the homedir is hidden
            else:
                # homeDir = System.getProperty("user.home")
                homeDir = os.path.expanduser(u"~")  # Should work on Unix and Windows
                if homeDir is None or homeDir == u"":
                    homeDir = System.getProperty(u"user.home")
                if homeDir is None or homeDir == u"":
                    homeDir = os.environ.get(u"HOMEPATH")
        except:
            pass

        if homeDir is None or homeDir == u"":
            homeDir = MD_REF.getCurrentAccountBook().getRootFolder().getParent()  # Better than nothing!

        if homeDir is None or homeDir == u"":
            homeDir = u""

        myPrint("DB", "Home Directory detected...:", homeDir)
        return homeDir

    def getDecimalPoint():
        decimalFormat = DecimalFormat.getInstance()
        # noinspection PyUnresolvedReferences
        decimalSymbols = decimalFormat.getDecimalFormatSymbols()

        try:
            _decimalCharSep = decimalSymbols.getDecimalSeparator()
            myPrint(u"D",u"Decimal Point Character: %s" %(_decimalCharSep))
            return _decimalCharSep
        except:
            myPrint(u"B",u"Error in getDecimalPoint() routine....?")
            dump_sys_error_to_md_console_and_errorlog()
        return u"error"


    GlobalVars.decimalCharSep = getDecimalPoint()


    def isMacDarkModeDetected():
        darkResponse = "LIGHT"
        if Platform.isOSX():
            try:
                darkResponse = subprocess.check_output("defaults read -g AppleInterfaceStyle", shell=True)
                darkResponse = darkResponse.strip().lower()
            except: pass
        return ("dark" in darkResponse)

    def isMDThemeDark():
        try:
            currentTheme = MD_REF.getUI().getCurrentTheme()
            try:
                if currentTheme.isSystemDark(): return True     # NOTE: Only VAQua has isSystemDark()
            except: pass
            if "dark" in currentTheme.getThemeID().lower(): return True
            if isMDThemeFlatDark(): return True
            if isMDThemeDarcula(): return True
        except: pass
        return False

    def isMDThemeDarcula():
        try:
            currentTheme = MD_REF.getUI().getCurrentTheme()
            if isMDThemeFlatDark(): return False                    # Flat Dark pretends to be Darcula!
            if "darcula" in currentTheme.getThemeID(): return True
        except: pass
        return False

    def isMDThemeCustomizable():
        try:
            currentTheme = MD_REF.getUI().getCurrentTheme()
            if currentTheme.isCustomizable(): return True
        except: pass
        return False

    def isMDThemeHighContrast():
        try:
            currentTheme = MD_REF.getUI().getCurrentTheme()
            if "high_contrast" in currentTheme.getThemeID(): return True
        except: pass
        return False

    def isMDThemeDefault():
        try:
            currentTheme = MD_REF.getUI().getCurrentTheme()
            if "default" in currentTheme.getThemeID(): return True
        except: pass
        return False

    def isMDThemeClassic():
        try:
            currentTheme = MD_REF.getUI().getCurrentTheme()
            if "classic" in currentTheme.getThemeID(): return True
        except: pass
        return False

    def isMDThemeSolarizedLight():
        try:
            currentTheme = MD_REF.getUI().getCurrentTheme()
            if "solarized_light" in currentTheme.getThemeID(): return True
        except: pass
        return False

    def isMDThemeSolarizedDark():
        try:
            currentTheme = MD_REF.getUI().getCurrentTheme()
            if "solarized_dark" in currentTheme.getThemeID(): return True
        except: pass
        return False

    def isMDThemeFlatDark():
        try:
            currentTheme = MD_REF.getUI().getCurrentTheme()
            if "flat dark" in currentTheme.toString().lower(): return True
        except: pass
        return False

    def isMDThemeVAQua():
        if Platform.isOSX():
            try:
                # currentTheme = MD_REF.getUI().getCurrentTheme()       # Not reset when changed in-session as it's a final variable!
                # if ".vaqua" in safeStr(currentTheme.getClass()).lower(): return True
                currentTheme = ThemeInfo.themeForID(MD_REF.getUI(), MD_REF.getPreferences().getSetting(GlobalVars.MD_PREFERENCE_KEY_CURRENT_THEME, ThemeInfo.DEFAULT_THEME_ID))
                if ".vaqua" in currentTheme.getClass().getName().lower(): return True                                   # noqa
            except:
                myPrint("B", "@@ Error in isMDThemeVAQua() - Alert author! Error:", sys.exc_info()[1])
        return False

    def isIntelX86_32bit():
        """Detect Intel x86 32bit system"""
        return String(System.getProperty("os.arch", "null").strip()).toLowerCase(Locale.ROOT) == "x86"

    def getMDIcon(startingIcon=None, lAlwaysGetIcon=False):
        if lAlwaysGetIcon or isIntelX86_32bit():
            return MD_REF.getUI().getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png")
        return startingIcon

    # JOptionPane.DEFAULT_OPTION, JOptionPane.YES_NO_OPTION, JOptionPane.YES_NO_CANCEL_OPTION, JOptionPane.OK_CANCEL_OPTION
    # JOptionPane.ERROR_MESSAGE, JOptionPane.INFORMATION_MESSAGE, JOptionPane.WARNING_MESSAGE, JOptionPane.QUESTION_MESSAGE, JOptionPane.PLAIN_MESSAGE

    # Copies MD_REF.getUI().showInfoMessage (but a newer version now exists in MD internal code)
    def myPopupInformationBox(theParent=None, theMessage="What no message?!", theTitle="Info", theMessageType=JOptionPane.INFORMATION_MESSAGE):

        if theParent is None and (theMessageType == JOptionPane.PLAIN_MESSAGE or theMessageType == JOptionPane.INFORMATION_MESSAGE):
            icon = getMDIcon(lAlwaysGetIcon=True)
        else:
            icon = getMDIcon(None)
        JOptionPane.showMessageDialog(theParent, JTextPanel(theMessage), theTitle, theMessageType, icon)

    def wrapLines(message, numChars=40):
        charCount = 0
        result=""
        for ch in message:
            if ch == '\n' or ch == '\r':
                charCount = 0
            elif charCount > numChars and not Character.isWhitespace(ch):
                result+="\n"
                charCount = 0
            else:
                charCount+=1
            result+=ch
        return result

    def myPopupAskBackup(theParent=None, theMessage="What no message?!", lReturnTheTruth=False):

        _options=["STOP", "PROCEED WITHOUT BACKUP", "DO BACKUP NOW"]
        response = JOptionPane.showOptionDialog(theParent,
                                                theMessage,
                                                "PERFORM BACKUP BEFORE UPDATE?",
                                                0,
                                                JOptionPane.WARNING_MESSAGE,
                                                getMDIcon(),
                                                _options,
                                                _options[0])

        if response == 2:
            myPrint("B", "User requested to create a backup before update/fix - calling Moneydance's 'Export Backup' routine...")
            MD_REF.getUI().setStatus("%s is creating a backup...." %(GlobalVars.thisScriptName),-1.0)
            MD_REF.getUI().saveToBackup(None)
            MD_REF.getUI().setStatus("%s create (export) backup process completed...." %(GlobalVars.thisScriptName),0)
            return True

        elif response == 1:
            myPrint("B", "User DECLINED to create a backup before update/fix...!")
            if not lReturnTheTruth:
                return True

        return False

    # Copied MD_REF.getUI().askQuestion
    def myPopupAskQuestion(theParent=None,
                           theTitle="Question",
                           theQuestion="What?",
                           theOptionType=JOptionPane.YES_NO_OPTION,
                           theMessageType=JOptionPane.QUESTION_MESSAGE):

        if theParent is None and (theMessageType == JOptionPane.PLAIN_MESSAGE or theMessageType == JOptionPane.INFORMATION_MESSAGE):
            icon = getMDIcon(lAlwaysGetIcon=True)
        else:
            icon = getMDIcon(None)

        # question = wrapLines(theQuestion)
        question = theQuestion
        result = JOptionPane.showConfirmDialog(theParent,
                                               question,
                                               theTitle,
                                               theOptionType,
                                               theMessageType,
                                               icon)
        return result == 0

    # Copies Moneydance .askForQuestion
    def myPopupAskForInput(theParent,
                           theTitle,
                           theFieldLabel,
                           theFieldDescription="",
                           defaultValue=None,
                           isPassword=False,
                           theMessageType=JOptionPane.INFORMATION_MESSAGE):

        if theParent is None and (theMessageType == JOptionPane.PLAIN_MESSAGE or theMessageType == JOptionPane.INFORMATION_MESSAGE):
            icon = getMDIcon(lAlwaysGetIcon=True)
        else:
            icon = getMDIcon(None)

        p = JPanel(GridBagLayout())
        defaultText = None
        if defaultValue: defaultText = defaultValue
        if isPassword:
            field = JPasswordField(defaultText)
        else:
            field = JTextField(defaultText)
        field.addAncestorListener(RequestFocusListener())

        _x = 0
        if theFieldLabel:
            p.add(JLabel(theFieldLabel), GridC.getc(_x, 0).east())
            _x+=1

        p.add(field, GridC.getc(_x, 0).field())
        p.add(Box.createHorizontalStrut(244), GridC.getc(_x, 0))
        if theFieldDescription:
            p.add(JTextPanel(theFieldDescription), GridC.getc(_x, 1).field().colspan(_x + 1))
        if (JOptionPane.showConfirmDialog(theParent,
                                          p,
                                          theTitle,
                                          JOptionPane.OK_CANCEL_OPTION,
                                          theMessageType,
                                          icon) == 0):
            return field.getText()
        return None

    # APPLICATION_MODAL, DOCUMENT_MODAL, MODELESS, TOOLKIT_MODAL
    class MyPopUpDialogBox():

        def __init__(self,
                     theParent=None,
                     theStatus="",
                     theMessage="",
                     maxSize=Dimension(0,0),
                     theTitle="Info",
                     lModal=True,
                     lCancelButton=False,
                     OKButtonText="OK",
                     lAlertLevel=0):

            self.theParent = theParent
            self.theStatus = theStatus
            self.theMessage = theMessage
            self.maxSize = maxSize
            self.theTitle = theTitle
            self.lModal = lModal
            self.lCancelButton = lCancelButton
            self.OKButtonText = OKButtonText
            self.lAlertLevel = lAlertLevel
            self.fakeJFrame = None
            self._popup_d = None
            self.lResult = [None]
            self.statusLabel = None
            self.messageJText = None
            if not self.theMessage.endswith("\n"): self.theMessage+="\n"
            if self.OKButtonText == "": self.OKButtonText="OK"
            if isMDThemeDark() or isMacDarkModeDetected(): self.lAlertLevel = 0

        def updateMessages(self, newTitle=None, newStatus=None, newMessage=None, lPack=True):
            # We wait when on the EDT as most scripts execute on the EDT.. So this is probably an in execution update message
            # ... if we invokeLater() then the message will (probably) only appear after the EDT script finishes....
            genericSwingEDTRunner(False, True, self._updateMessages, newTitle, newStatus, newMessage, lPack)

        def _updateMessages(self, newTitle=None, newStatus=None, newMessage=None, lPack=True):
            if not newTitle and not newStatus and not newMessage: return
            if newTitle:
                self.theTitle = newTitle
                self._popup_d.setTitle(self.theTitle)
            if newStatus:
                self.theStatus = newStatus
                self.statusLabel.setText(self.theStatus)
            if newMessage:
                self.theMessage = newMessage
                self.messageJText.setText(self.theMessage)
            if lPack: self._popup_d.pack()

        class WindowListener(WindowAdapter):

            def __init__(self, theDialog, theFakeFrame, lResult):
                self.theDialog = theDialog
                self.theFakeFrame = theFakeFrame
                self.lResult = lResult

            def windowClosing(self, WindowEvent):                                                                       # noqa
                myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", WindowEvent)
                myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

                myPrint("DB", "JDialog Frame shutting down....")

                self.lResult[0] = False

                # Note - listeners are already on the EDT
                if self.theFakeFrame is not None:
                    self.theDialog.dispose()
                    self.theFakeFrame.dispose()
                else:
                    self.theDialog.dispose()

                myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
                return

        class OKButtonAction(AbstractAction):

            def __init__(self, theDialog, theFakeFrame, lResult):
                self.theDialog = theDialog
                self.theFakeFrame = theFakeFrame
                self.lResult = lResult

            def actionPerformed(self, event):
                myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event)
                myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

                self.lResult[0] = True

                # Note - listeners are already on the EDT
                if self.theFakeFrame is not None:
                    self.theDialog.dispose()
                    self.theFakeFrame.dispose()
                else:
                    self.theDialog.dispose()

                myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
                return

        class CancelButtonAction(AbstractAction):

            def __init__(self, theDialog, theFakeFrame, lResult):
                self.theDialog = theDialog
                self.theFakeFrame = theFakeFrame
                self.lResult = lResult

            def actionPerformed(self, event):
                myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event)
                myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

                self.lResult[0] = False

                # Note - listeners are already on the EDT
                if self.theFakeFrame is not None:
                    self.theDialog.dispose()
                    self.theFakeFrame.dispose()
                else:
                    self.theDialog.dispose()

                myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
                return

        def kill(self):
            myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()")
            myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

            if not SwingUtilities.isEventDispatchThread():
                SwingUtilities.invokeLater(GenericVisibleRunnable(self._popup_d, False))
                if self.fakeJFrame is not None:
                    SwingUtilities.invokeLater(GenericDisposeRunnable(self._popup_d))
                    SwingUtilities.invokeLater(GenericDisposeRunnable(self.fakeJFrame))
                else:
                    SwingUtilities.invokeLater(GenericDisposeRunnable(self._popup_d))
            else:
                self._popup_d.setVisible(False)
                if self.fakeJFrame is not None:
                    self._popup_d.dispose()
                    self.fakeJFrame.dispose()
                else:
                    self._popup_d.dispose()

            myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

        def result(self): return self.lResult[0]

        def go(self):
            myPrint("DB", "In MyPopUpDialogBox.", inspect.currentframe().f_code.co_name, "()")
            myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

            class MyPopUpDialogBoxRunnable(Runnable):
                def __init__(self, callingClass):
                    self.callingClass = callingClass

                def run(self):                                                                                          # noqa
                    myPrint("DB", "In MyPopUpDialogBoxRunnable.", inspect.currentframe().f_code.co_name, "()")
                    myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

                    # Create a fake JFrame so we can set the Icons...
                    if self.callingClass.theParent is None:
                        self.callingClass.fakeJFrame = MyJFrame()
                        self.callingClass.fakeJFrame.setName(u"%s_fake_dialog" %(myModuleID))
                        self.callingClass.fakeJFrame.setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE)
                        self.callingClass.fakeJFrame.setUndecorated(True)
                        self.callingClass.fakeJFrame.setVisible(False)
                        if not Platform.isOSX():
                            self.callingClass.fakeJFrame.setIconImage(MDImages.getImage(MD_REF.getSourceInformation().getIconResource()))

                    class MyJDialog(JDialog):
                        def __init__(self, maxSize, *args):
                            self.maxSize = maxSize                                                                      # type: Dimension
                            super(self.__class__, self).__init__(*args)

                        # On Windows, the height was exceeding the screen height when default size of Dimension (0,0), so set the max....
                        def getPreferredSize(self):
                            calcPrefSize = super(self.__class__, self).getPreferredSize()
                            newPrefSize = Dimension(min(calcPrefSize.width, self.maxSize.width), min(calcPrefSize.height, self.maxSize.height))
                            return newPrefSize

                    screenSize = Toolkit.getDefaultToolkit().getScreenSize()

                    if isinstance(self.callingClass.maxSize, Dimension)\
                            and self.callingClass.maxSize.height and self.callingClass.maxSize.width:
                        maxDialogWidth = min(screenSize.width-20, self.callingClass.maxSize.width)
                        maxDialogHeight = min(screenSize.height-40, self.callingClass.maxSize.height)
                        maxDimension = Dimension(maxDialogWidth,maxDialogHeight)
                    else:
                        maxDialogWidth = min(screenSize.width-20, max(GetFirstMainFrame.DEFAULT_MAX_WIDTH, int(round(GetFirstMainFrame.getSize().width *.9,0))))
                        maxDialogHeight = min(screenSize.height-40, max(GetFirstMainFrame.DEFAULT_MAX_WIDTH, int(round(GetFirstMainFrame.getSize().height *.9,0))))
                        maxDimension = Dimension(maxDialogWidth,maxDialogHeight)

                    # noinspection PyUnresolvedReferences
                    self.callingClass._popup_d = MyJDialog(maxDimension,
                                                           self.callingClass.theParent, self.callingClass.theTitle,
                                                           Dialog.ModalityType.APPLICATION_MODAL if (self.callingClass.lModal) else Dialog.ModalityType.MODELESS)

                    self.callingClass._popup_d.getContentPane().setLayout(BorderLayout())
                    self.callingClass._popup_d.setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE)

                    shortcut = Toolkit.getDefaultToolkit().getMenuShortcutKeyMaskEx()

                    # Add standard CMD-W keystrokes etc to close window
                    self.callingClass._popup_d.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_W, shortcut), "close-window")
                    self.callingClass._popup_d.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_F4, shortcut), "close-window")
                    self.callingClass._popup_d.getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0), "close-window")
                    self.callingClass._popup_d.getRootPane().getActionMap().put("close-window", self.callingClass.CancelButtonAction(self.callingClass._popup_d, self.callingClass.fakeJFrame,self.callingClass.lResult))
                    self.callingClass._popup_d.addWindowListener(self.callingClass.WindowListener(self.callingClass._popup_d, self.callingClass.fakeJFrame,self.callingClass.lResult))

                    if (not Platform.isMac()):
                        # MD_REF.getUI().getImages()
                        self.callingClass._popup_d.setIconImage(MDImages.getImage(MD_REF.getSourceInformation().getIconResource()))

                    self.callingClass.messageJText = JTextArea(self.callingClass.theMessage)
                    self.callingClass.messageJText.setFont(getMonoFont())
                    self.callingClass.messageJText.setEditable(False)
                    self.callingClass.messageJText.setLineWrap(False)
                    self.callingClass.messageJText.setWrapStyleWord(False)

                    _popupPanel = JPanel(BorderLayout())
                    _popupPanel.setBorder(EmptyBorder(8, 8, 8, 8))

                    if self.callingClass.theStatus:
                        _statusPnl = JPanel(BorderLayout())
                        self.callingClass.statusLabel = JLabel(self.callingClass.theStatus)
                        self.callingClass.statusLabel.setForeground(getColorBlue())
                        self.callingClass.statusLabel.setBorder(EmptyBorder(8, 0, 8, 0))
                        _popupPanel.add(self.callingClass.statusLabel, BorderLayout.NORTH)

                    myScrollPane = JScrollPane(self.callingClass.messageJText, JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED,JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED)
                    myScrollPane.setWheelScrollingEnabled(True)
                    _popupPanel.add(myScrollPane, BorderLayout.CENTER)

                    buttonPanel = JPanel()
                    if self.callingClass.lModal or self.callingClass.lCancelButton:
                        buttonPanel.setLayout(FlowLayout(FlowLayout.CENTER))

                        if self.callingClass.lCancelButton:
                            cancel_button = JButton("CANCEL")
                            cancel_button.setPreferredSize(Dimension(100,40))
                            cancel_button.setBackground(Color.LIGHT_GRAY)
                            cancel_button.setBorderPainted(False)
                            cancel_button.setOpaque(True)
                            cancel_button.setBorder(EmptyBorder(8, 8, 8, 8))

                            cancel_button.addActionListener(self.callingClass.CancelButtonAction(self.callingClass._popup_d, self.callingClass.fakeJFrame,self.callingClass.lResult) )
                            buttonPanel.add(cancel_button)

                        if self.callingClass.lModal:
                            ok_button = JButton(self.callingClass.OKButtonText)
                            if len(self.callingClass.OKButtonText) <= 2:
                                ok_button.setPreferredSize(Dimension(100,40))
                            else:
                                ok_button.setPreferredSize(Dimension(200,40))

                            ok_button.setBackground(Color.LIGHT_GRAY)
                            ok_button.setBorderPainted(False)
                            ok_button.setOpaque(True)
                            ok_button.setBorder(EmptyBorder(8, 8, 8, 8))
                            ok_button.addActionListener( self.callingClass.OKButtonAction(self.callingClass._popup_d, self.callingClass.fakeJFrame, self.callingClass.lResult) )
                            buttonPanel.add(ok_button)

                        _popupPanel.add(buttonPanel, BorderLayout.SOUTH)

                    if self.callingClass.lAlertLevel >= 2:
                        # internalScrollPane.setBackground(Color.RED)
                        self.callingClass.messageJText.setBackground(Color.RED)
                        self.callingClass.messageJText.setForeground(Color.BLACK)
                        self.callingClass.messageJText.setOpaque(True)
                        _popupPanel.setBackground(Color.RED)
                        _popupPanel.setForeground(Color.BLACK)
                        _popupPanel.setOpaque(True)
                        buttonPanel.setBackground(Color.RED)
                        buttonPanel.setOpaque(True)

                    elif self.callingClass.lAlertLevel >= 1:
                        # internalScrollPane.setBackground(Color.YELLOW)
                        self.callingClass.messageJText.setBackground(Color.YELLOW)
                        self.callingClass.messageJText.setForeground(Color.BLACK)
                        self.callingClass.messageJText.setOpaque(True)
                        _popupPanel.setBackground(Color.YELLOW)
                        _popupPanel.setForeground(Color.BLACK)
                        _popupPanel.setOpaque(True)
                        buttonPanel.setBackground(Color.YELLOW)
                        buttonPanel.setOpaque(True)

                    self.callingClass._popup_d.add(_popupPanel, BorderLayout.CENTER)
                    self.callingClass._popup_d.pack()
                    self.callingClass._popup_d.setLocationRelativeTo(self.callingClass.theParent)
                    self.callingClass._popup_d.setVisible(True)

            if not SwingUtilities.isEventDispatchThread():
                if not self.lModal:
                    myPrint("DB",".. Not running on the EDT, but also NOT Modal, so will .invokeLater::MyPopUpDialogBoxRunnable()...")
                    SwingUtilities.invokeLater(MyPopUpDialogBoxRunnable(self))
                else:
                    myPrint("DB",".. Not running on the EDT so calling .invokeAndWait::MyPopUpDialogBoxRunnable()...")
                    SwingUtilities.invokeAndWait(MyPopUpDialogBoxRunnable(self))
            else:
                myPrint("DB",".. Already on the EDT, just executing::MyPopUpDialogBoxRunnable() now...")
                MyPopUpDialogBoxRunnable(self).run()

            myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

            return self.lResult[0]

    def play_the_money_sound():

        # Seems to cause a crash on Virtual Machine with no Audio - so just in case....
        try:
            if MD_REF.getPreferences().getSetting("beep_on_transaction_change", "y") == "y":
                MD_REF.getUI().getSounds().playSound("cash_register.wav")
        except:
            pass

        return

    def get_filename_addition():

        cal = Calendar.getInstance()
        hhmm = str(10000 + cal.get(11) * 100 + cal.get(12))[1:]
        nameAddition = "-" + str(DateUtil.getStrippedDateInt()) + "-"+hhmm

        return nameAddition

    def check_file_writable(fnm):
        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )
        myPrint("DB","Checking path: ", fnm)

        if os.path.exists(fnm):
            myPrint("DB", "path exists..")
            # path exists
            if os.path.isfile(fnm):  # is it a file or a dir?
                myPrint("DB","path is a file..")
                # also works when file is a link and the target is writable
                return os.access(fnm, os.W_OK)
            else:
                myPrint("DB", "path is not a file..")
                return False  # path is a dir, so cannot write as a file
        # target does not exist, check perms on parent dir
        myPrint("DB","path does not exist...")
        pdir = os.path.dirname(fnm)
        if not pdir: pdir = '.'
        # target is creatable if parent dir is writable
        return os.access(pdir, os.W_OK)

    class ExtFilenameFilter(FilenameFilter):
        """File extension filter for FileDialog"""
        def __init__(self, ext): self.ext = "." + ext.upper()                                                           # noqa

        def accept(self, thedir, filename):                                                                             # noqa
            if filename is not None and filename.upper().endswith(self.ext): return True
            return False

    class ExtFileFilterJFC(FileFilter):
        """File extension filter for JFileChooser"""
        def __init__(self, ext): self.ext = "." + ext.upper()

        def getDescription(self): return "*"+self.ext                                                                   # noqa

        def accept(self, _theFile):                                                                                     # noqa
            if _theFile is None: return False
            return _theFile.getName().upper().endswith(self.ext)

    def MDDiag():
        myPrint("D", "Moneydance Build:", MD_REF.getVersion(), "Build:", MD_REF.getBuild())


    MDDiag()

    myPrint("DB","System file encoding is:", sys.getfilesystemencoding() )   # Not used, but interesting. Perhaps useful when switching between Windows/Macs and writing files...

    def checkVersions():
        lError = False
        plat_j = platform.system()
        plat_p = platform.python_implementation()
        python_maj = sys.version_info.major
        python_min = sys.version_info.minor

        myPrint("DB","Platform:", plat_p, plat_j, python_maj, ".", python_min)
        myPrint("DB", sys.version)

        if plat_p != "Jython":
            lError = True
            myPrint("DB", "Error: Script requires Jython")
        if plat_j != "Java":
            lError = True
            myPrint("DB", "Error: Script requires Java  base")
        if (python_maj != 2 or python_min != 7):
            lError = True
            myPrint("DB", "\n\nError: Script was  designed on version 2.7. By all means bypass this test and see what happens.....")

        if lError:
            myPrint("J", "Platform version issue - will terminate script!")
            myPrint("P", "\n@@@ TERMINATING PROGRAM @@@\n")
            raise(Exception("Platform version issue - will terminate script!"))

        return not lError


    checkVersions()

    def setDefaultFonts():
        """Grabs the MD defaultText font, reduces default size down to below 18, sets UIManager defaults (if runtime extension, will probably error, so I catch and skip)"""
        if MD_REF_UI is None: return

        # If a runtime extension, then this may fail, depending on timing... Just ignore and return...
        try:
            myFont = MD_REF.getUI().getFonts().defaultText
        except:
            myPrint("B","ERROR trying to call .getUI().getFonts().defaultText - skipping setDefaultFonts()")
            return

        if myFont is None:
            myPrint("B","WARNING: In setDefaultFonts(): calling .getUI().getFonts().defaultText has returned None (but moneydance_ui was set) - skipping setDefaultFonts()")
            return

        if myFont.getSize()>18:
            try:
                myFont = myFont.deriveFont(16.0)
                myPrint("B", "I have reduced the font size down to point-size 16 - Default Fonts are now set to: %s" %(myFont))
            except:
                myPrint("B","ERROR - failed to override font point size down to 16.... will ignore and continue. Font set to: %s" %(myFont))
        else:
            myPrint("DB", "Attempting to set default font to %s" %myFont)

        try:
            UIManager.getLookAndFeelDefaults().put("defaultFont", myFont )

            # https://thebadprogrammer.com/swing-uimanager-keys/
            UIManager.put("CheckBoxMenuItem.acceleratorFont", myFont)
            UIManager.put("Button.font", myFont)
            UIManager.put("ToggleButton.font", myFont)
            UIManager.put("RadioButton.font", myFont)
            UIManager.put("CheckBox.font", myFont)
            UIManager.put("ColorChooser.font", myFont)
            UIManager.put("ComboBox.font", myFont)
            UIManager.put("Label.font", myFont)
            UIManager.put("List.font", myFont)
            UIManager.put("MenuBar.font", myFont)
            UIManager.put("Menu.acceleratorFont", myFont)
            UIManager.put("RadioButtonMenuItem.acceleratorFont", myFont)
            UIManager.put("MenuItem.acceleratorFont", myFont)
            UIManager.put("MenuItem.font", myFont)
            UIManager.put("RadioButtonMenuItem.font", myFont)
            UIManager.put("CheckBoxMenuItem.font", myFont)
            UIManager.put("OptionPane.buttonFont", myFont)
            UIManager.put("OptionPane.messageFont", myFont)
            UIManager.put("Menu.font", myFont)
            UIManager.put("PopupMenu.font", myFont)
            UIManager.put("OptionPane.font", myFont)
            UIManager.put("Panel.font", myFont)
            UIManager.put("ProgressBar.font", myFont)
            UIManager.put("ScrollPane.font", myFont)
            UIManager.put("Viewport.font", myFont)
            UIManager.put("TabbedPane.font", myFont)
            UIManager.put("Slider.font", myFont)
            UIManager.put("Table.font", myFont)
            UIManager.put("TableHeader.font", myFont)
            UIManager.put("TextField.font", myFont)
            UIManager.put("Spinner.font", myFont)
            UIManager.put("PasswordField.font", myFont)
            UIManager.put("TextArea.font", myFont)
            UIManager.put("TextPane.font", myFont)
            UIManager.put("EditorPane.font", myFont)
            UIManager.put("TabbedPane.smallFont", myFont)
            UIManager.put("TitledBorder.font", myFont)
            UIManager.put("ToolBar.font", myFont)
            UIManager.put("ToolTip.font", myFont)
            UIManager.put("Tree.font", myFont)
            UIManager.put("FormattedTextField.font", myFont)
            UIManager.put("IconButton.font", myFont)
            UIManager.put("InternalFrame.optionDialogTitleFont", myFont)
            UIManager.put("InternalFrame.paletteTitleFont", myFont)
            UIManager.put("InternalFrame.titleFont", myFont)
        except:
            myPrint("B","Failed to set Swing default fonts to use Moneydance defaults... sorry")

        myPrint("DB",".setDefaultFonts() successfully executed...")
        return

    setDefaultFonts()

    def who_am_i():
        try: username = System.getProperty("user.name")
        except: username = "???"
        return username

    def getHomeDir():
        # Yup - this can be all over the place...
        myPrint("D", 'System.getProperty("user.dir")', System.getProperty("user.dir"))
        myPrint("D", 'System.getProperty("UserHome")', System.getProperty("UserHome"))
        myPrint("D", 'System.getProperty("user.home")', System.getProperty("user.home"))
        myPrint("D", 'os.path.expanduser("~")', os.path.expanduser("~"))
        myPrint("D", 'os.environ.get("HOMEPATH")', os.environ.get("HOMEPATH"))
        return

    myPrint("D", "I am user:", who_am_i())
    if debug: getHomeDir()

    # noinspection PyArgumentList
    class JTextFieldLimitYN(PlainDocument):

        limit = 10  # Default
        toUpper = False
        what = ""

        def __init__(self, limit, toUpper, what):

            super(PlainDocument, self).__init__()
            self.limit = limit
            self.toUpper = toUpper
            self.what = what

        def insertString(self, myOffset, myString, myAttr):

            if (myString is None): return
            if self.toUpper: myString = myString.upper()
            if (self.what == "YN" and (myString in "YN")) \
                    or (self.what == "DELIM" and (myString in ";|,")) \
                    or (self.what == "1234" and (myString in "1234")) \
                    or (self.what == "CURR"):
                if ((self.getLength() + len(myString)) <= self.limit):
                    super(JTextFieldLimitYN, self).insertString(myOffset, myString, myAttr)                             # noqa

    def fix_delimiter( theDelimiter ):

        try:
            if sys.version_info.major >= 3: return theDelimiter
            if sys.version_info.major <  2: return str(theDelimiter)

            if sys.version_info.minor >  7: return theDelimiter
            if sys.version_info.minor <  7: return str(theDelimiter)

            if sys.version_info.micro >= 2: return theDelimiter
        except:
            pass

        return str( theDelimiter )

    def get_StuWareSoftSystems_parameters_from_file(myFile="StuWareSoftSystems.dict"):
        global debug    # This global for debug must be here as we set it from loaded parameters

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )

        if GlobalVars.resetPickleParameters:
            myPrint("B", "User has specified to reset parameters... keeping defaults and skipping pickle()")
            GlobalVars.parametersLoadedFromFile = {}
            return

        migratedFilename = os.path.join(MD_REF.getCurrentAccountBook().getRootFolder().getAbsolutePath(), myFile)

        myPrint("DB", "Now checking for parameter file:", migratedFilename)

        if os.path.exists(migratedFilename):
            myPrint("DB", "loading parameters from (non-encrypted) Pickle file:", migratedFilename)
            myPrint("DB", "Parameter file", migratedFilename, "exists..")
            # Open the file
            try:
                # Really we should open() the file in binary mode and read/write as binary, then we wouldn't get platform differences!
                istr = FileInputStream(migratedFilename)
                load_file = FileUtil.wrap(istr)
                if not Platform.isWindows():
                    load_string = load_file.read().replace('\r', '')    # This allows for files migrated from windows (strip the extra CR)
                else:
                    load_string = load_file.read()

                GlobalVars.parametersLoadedFromFile = pickle.loads(load_string)
                load_file.close()
            except FileNotFoundException:
                myPrint("B", "Error: failed to find parameter file...")
                GlobalVars.parametersLoadedFromFile = None
            except EOFError:
                myPrint("B", "Error: reached EOF on parameter file....")
                GlobalVars.parametersLoadedFromFile = None
            except:
                myPrint("B", "Error opening Pickle File Unexpected error:", sys.exc_info()[0], "Error:", sys.exc_info()[1], "Line:", sys.exc_info()[2].tb_lineno)
                myPrint("B", ">> Will ignore saved parameters, and create a new file...")
                GlobalVars.parametersLoadedFromFile = None

            if GlobalVars.parametersLoadedFromFile is None:
                GlobalVars.parametersLoadedFromFile = {}
                myPrint("DB","Parameters did NOT load, will use defaults..")
            else:
                myPrint("DB","Parameters successfully loaded from file...")
        else:
            myPrint("DB", "Parameter Pickle file does NOT exist - will use default and create new file..")
            GlobalVars.parametersLoadedFromFile = {}

        if not GlobalVars.parametersLoadedFromFile: return

        myPrint("DB","GlobalVars.parametersLoadedFromFile read from file contains...:")
        for key in sorted(GlobalVars.parametersLoadedFromFile.keys()):
            myPrint("DB","...variable:", key, GlobalVars.parametersLoadedFromFile[key])

        if GlobalVars.parametersLoadedFromFile.get("debug") is not None: debug = GlobalVars.parametersLoadedFromFile.get("debug")

        myPrint("DB","Parameter file loaded if present and GlobalVars.parametersLoadedFromFile{} dictionary set.....")

        # Now load into memory!
        load_StuWareSoftSystems_parameters_into_memory()

        return

    def save_StuWareSoftSystems_parameters_to_file(myFile="StuWareSoftSystems.dict"):
        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )

        if GlobalVars.parametersLoadedFromFile is None: GlobalVars.parametersLoadedFromFile = {}

        # Don't forget, any parameters loaded earlier will be preserved; just add changed variables....
        GlobalVars.parametersLoadedFromFile["__Author"] = "Stuart Beesley - (c) StuWareSoftSystems"
        GlobalVars.parametersLoadedFromFile["debug"] = debug

        dump_StuWareSoftSystems_parameters_from_memory()

        # Pickle was originally encrypted, no need, migrating to unencrypted
        migratedFilename = os.path.join(MD_REF.getCurrentAccountBook().getRootFolder().getAbsolutePath(),myFile)

        myPrint("DB","Will try to save parameter file:", migratedFilename)

        ostr = FileOutputStream(migratedFilename)

        myPrint("DB", "about to Pickle.dump and save parameters to unencrypted file:", migratedFilename)

        try:
            save_file = FileUtil.wrap(ostr)
            pickle.dump(GlobalVars.parametersLoadedFromFile, save_file, protocol=0)
            save_file.close()

            myPrint("DB","GlobalVars.parametersLoadedFromFile now contains...:")
            for key in sorted(GlobalVars.parametersLoadedFromFile.keys()):
                myPrint("DB","...variable:", key, GlobalVars.parametersLoadedFromFile[key])

        except:
            myPrint("B", "Error - failed to create/write parameter file.. Ignoring and continuing.....")
            dump_sys_error_to_md_console_and_errorlog()

            return

        myPrint("DB","Parameter file written and parameters saved to disk.....")

        return

    def get_time_stamp_as_nice_text(timeStamp, _format=None, lUseHHMMSS=True):

        if _format is None: _format = MD_REF.getPreferences().getShortDateFormat()

        humanReadableDate = ""
        try:
            c = Calendar.getInstance()
            c.setTime(Date(timeStamp))
            longHHMMSSText = " HH:mm:ss(.SSS) Z z zzzz" if (lUseHHMMSS) else ""
            dateFormatter = SimpleDateFormat("%s%s" %(_format, longHHMMSSText))
            humanReadableDate = dateFormatter.format(c.getTime())
        except: pass
        return humanReadableDate

    def currentDateTimeMarker():
        c = Calendar.getInstance()
        dateformat = SimpleDateFormat("_yyyyMMdd_HHmmss")
        _datetime = dateformat.format(c.getTime())
        return _datetime

    def destroyOldFrames(moduleName):
        myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()")
        myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))
        frames = JFrame.getFrames()
        for fr in frames:
            if fr.getName().lower().startswith(moduleName+"_"):
                myPrint("DB","Found old frame %s and active status is: %s" %(fr.getName(),fr.isActiveInMoneydance))
                try:
                    fr.isActiveInMoneydance = False
                    if not SwingUtilities.isEventDispatchThread():
                        SwingUtilities.invokeLater(GenericVisibleRunnable(fr, False, False))
                        SwingUtilities.invokeLater(GenericDisposeRunnable(fr))  # This should call windowClosed() which should remove MD listeners.....
                    else:
                        fr.setVisible(False)
                        fr.dispose()            # This should call windowClosed() which should remove MD listeners.....
                    myPrint("DB","disposed of old frame: %s" %(fr.getName()))
                except:
                    myPrint("B","Failed to dispose old frame: %s" %(fr.getName()))
                    dump_sys_error_to_md_console_and_errorlog()

    def classPrinter(className, theObject):
        try:
            text = "Class: %s %s@{:x}".format(System.identityHashCode(theObject)) %(className, theObject.__class__)
        except:
            text = "Error in classPrinter(): %s: %s" %(className, theObject)
        return text

    def getColorBlue():
        # if not isMDThemeDark() and not isMacDarkModeDetected(): return(MD_REF.getUI().getColors().reportBlueFG)
        # return (MD_REF.getUI().getColors().defaultTextForeground)
        return MD_REF.getUI().getColors().reportBlueFG

    def getColorRed(): return (MD_REF.getUI().getColors().errorMessageForeground)

    def getColorDarkGreen(): return (MD_REF.getUI().getColors().budgetHealthyColor)

    def setDisplayStatus(_theStatus, _theColor=None):
        """Sets the Display / Status label on the main diagnostic display: G=Green, B=Blue, R=Red, DG=Dark Green"""

        if GlobalVars.STATUS_LABEL is None or not isinstance(GlobalVars.STATUS_LABEL, JLabel): return

        class SetDisplayStatusRunnable(Runnable):
            def __init__(self, _status, _color):
                self.status = _status; self.color = _color

            def run(self):
                GlobalVars.STATUS_LABEL.setText((_theStatus))
                if self.color is None or self.color == "": self.color = "X"
                self.color = self.color.upper()
                if self.color == "R":    GlobalVars.STATUS_LABEL.setForeground(getColorRed())
                elif self.color == "B":  GlobalVars.STATUS_LABEL.setForeground(getColorBlue())
                elif self.color == "DG": GlobalVars.STATUS_LABEL.setForeground(getColorDarkGreen())
                else:                    GlobalVars.STATUS_LABEL.setForeground(MD_REF.getUI().getColors().defaultTextForeground)

        if not SwingUtilities.isEventDispatchThread():
            SwingUtilities.invokeLater(SetDisplayStatusRunnable(_theStatus, _theColor))
        else:
            SetDisplayStatusRunnable(_theStatus, _theColor).run()

    def setJFileChooserParameters(_jf, lReportOnly=False, lDefaults=False, lPackagesT=None, lApplicationsT=None, lOptionsButton=None, lNewFolderButton=None):
        """sets up Client Properties for JFileChooser() to behave as required >> Mac only"""

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        if not Platform.isOSX(): return
        if not isinstance(_jf, JFileChooser): return

        _PKG = "JFileChooser.packageIsTraversable"
        _APP = "JFileChooser.appBundleIsTraversable"
        _OPTIONS = "JFileChooser.optionsPanelEnabled"
        _NEWFOLDER = "JFileChooser.canCreateDirectories"

        # JFileChooser defaults: https://violetlib.org/vaqua/filechooser.html
        # "JFileChooser.packageIsTraversable"   default False   >> set "true" to allow Packages to be traversed
        # "JFileChooser.appBundleIsTraversable" default False   >> set "true" to allow App Bundles to be traversed
        # "JFileChooser.optionsPanelEnabled"    default False   >> set "true" to allow Options button
        # "JFileChooser.canCreateDirectories"   default False   >> set "true" to allow New Folder button

        if debug or lReportOnly:
            myPrint("B", "Parameters set: ReportOnly: %s, Defaults:%s, PackagesT: %s, ApplicationsT:%s, OptionButton:%s, NewFolderButton: %s" %(lReportOnly, lDefaults, lPackagesT, lApplicationsT, lOptionsButton, lNewFolderButton))
            txt = ("Before setting" if not lReportOnly else "Reporting only")
            for setting in [_PKG, _APP, _OPTIONS, _NEWFOLDER]: myPrint("DB", "%s: '%s': '%s'" %(pad(txt,14), pad(setting,50), _jf.getClientProperty(setting)))
            if lReportOnly: return

        if lDefaults:
            _jf.putClientProperty(_PKG, None)
            _jf.putClientProperty(_APP, None)
            _jf.putClientProperty(_OPTIONS, None)
            _jf.putClientProperty(_NEWFOLDER, None)
        else:
            if lPackagesT       is not None: _jf.putClientProperty(_PKG, lPackagesT)
            if lApplicationsT   is not None: _jf.putClientProperty(_APP, lApplicationsT)
            if lOptionsButton   is not None: _jf.putClientProperty(_OPTIONS, lOptionsButton)
            if lNewFolderButton is not None: _jf.putClientProperty(_NEWFOLDER, lNewFolderButton)

        for setting in [_PKG, _APP, _OPTIONS, _NEWFOLDER]: myPrint("DB", "%s: '%s': '%s'" %(pad("After setting",14), pad(setting,50), _jf.getClientProperty(setting)))

        return

    def setFileDialogParameters(lReportOnly=False, lDefaults=False, lSelectDirectories=None, lPackagesT=None):
        """sets up System Properties for FileDialog() to behave as required >> Mac only"""

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        if not Platform.isOSX(): return

        _TRUE = "true"
        _FALSE = "false"

        _DIRS_FD = "apple.awt.fileDialogForDirectories"        # When True you can select a Folder (rather than a file)
        _PKGS_FD = "apple.awt.use-file-dialog-packages"        # When True allows you to select a 'bundle' as a file; False means navigate inside the bundle
        # "com.apple.macos.use-file-dialog-packages"           # DEPRECATED since Monterrey - discovered this about MD2022.5(4090) - refer: java.desktop/sun/lwawt/macosx/CFileDialog.java

        # FileDialog defaults
        # "apple.awt.fileDialogForDirectories"       default "false" >> set "true"  to allow Directories to be selected
        # "apple.awt.use-file-dialog-packages"       default "true"  >> set "false" to allow access to Mac 'packages'

        if debug or lReportOnly:
            myPrint("B", "Parameters set: ReportOnly: %s, Defaults:%s, SelectDirectories:%s, PackagesT:%s" % (lReportOnly, lDefaults, lSelectDirectories, lPackagesT))
            txt = ("Before setting" if not lReportOnly else "Reporting only")
            for setting in [_DIRS_FD, _PKGS_FD]: myPrint("DB", "%s: '%s': '%s'" %(pad(txt,14), pad(setting,50), System.getProperty(setting)))
            if lReportOnly: return

        if lDefaults:
            System.setProperty(_DIRS_FD,_FALSE)
            System.setProperty(_PKGS_FD,_TRUE)
        else:
            if lSelectDirectories is not None: System.setProperty(_DIRS_FD, (_TRUE if lSelectDirectories   else _FALSE))
            if lPackagesT         is not None: System.setProperty(_PKGS_FD, (_TRUE if lPackagesT           else _FALSE))

        for setting in [_DIRS_FD, _PKGS_FD]: myPrint("DB", "After setting:  '%s': '%s'" %(pad(setting,50), System.getProperty(setting)))

        return

    def getFileFromFileChooser(fileChooser_parent,                  # The Parent Frame, or None
                               fileChooser_starting_dir,            # The Starting Dir
                               fileChooser_filename,                # Default filename (or None)
                               fileChooser_title,                   # The Title (with FileDialog, only works on SAVE)
                               fileChooser_multiMode,               # Normally False (True has not been coded!)
                               fileChooser_open,                    # True for Open/Load, False for Save
                               fileChooser_selectFiles,             # True for files, False for Directories
                               fileChooser_OK_text,                 # Normally None, unless set - use text
                               fileChooser_fileFilterText=None,     # E.g. "txt" or "qif"
                               lForceJFC=False,
                               lForceFD=False,
                               lAllowTraversePackages=None,
                               lAllowTraverseApplications=None,     # JFileChooser only..
                               lAllowNewFolderButton=True,          # JFileChooser only..
                               lAllowOptionsButton=None):           # JFileChooser only..
        """Launches FileDialog on Mac, or JFileChooser on other platforms... NOTE: Do not use Filter on Macs!"""

        _THIS_METHOD_NAME = "Dynamic File Chooser"

        if fileChooser_multiMode:
            myPrint("B","@@ SORRY Multi File Selection Mode has not been coded! Exiting...")
            return None

        if fileChooser_starting_dir is None or fileChooser_starting_dir == "" or not os.path.exists(fileChooser_starting_dir):
            fileChooser_starting_dir = MD_REF.getPreferences().getSetting("gen.data_dir", None)

        if fileChooser_starting_dir is None or not os.path.exists(fileChooser_starting_dir):
            fileChooser_starting_dir = None
            myPrint("B","ERROR: Starting Path does not exist - will start with no starting path set..")

        else:
            myPrint("DB", "Preparing the Dynamic File Chooser with path: %s" %(fileChooser_starting_dir))
            if Platform.isOSX() and "/Library/Containers/" in fileChooser_starting_dir:
                myPrint("DB", "WARNING: Folder will be restricted by MacOSx...")
                if not lForceJFC:
                    txt = ("FileDialog: MacOSx restricts Java Access to 'special' locations like 'Library\n"
                          "Folder: %s\n"
                          "Please navigate to this location manually in the next popup. This grants permission"
                          %(fileChooser_starting_dir))
                else:
                    txt = ("JFileChooser: MacOSx restricts Java Access to 'special' locations like 'Library\n"
                          "Folder: %s\n"
                          "Your files will probably be hidden.. If so, switch to FileDialog()...(contact author)"
                          %(fileChooser_starting_dir))
                MyPopUpDialogBox(fileChooser_parent,
                                 "NOTE: Mac Security Restriction",
                                 txt,
                                 theTitle=_THIS_METHOD_NAME,
                                 lAlertLevel=1).go()

        if (Platform.isOSX() and not lForceJFC) or lForceFD:

            setFileDialogParameters(lPackagesT=lAllowTraversePackages, lSelectDirectories=(not fileChooser_selectFiles))

            myPrint("DB", "Preparing FileDialog() with path: %s" %(fileChooser_starting_dir))
            if fileChooser_filename is not None: myPrint("DB", "... and filename:                 %s" %(fileChooser_filename))

            fileDialog = FileDialog(fileChooser_parent, fileChooser_title)

            fileDialog.setTitle(fileChooser_title)

            if fileChooser_starting_dir is not None:    fileDialog.setDirectory(fileChooser_starting_dir)
            if fileChooser_filename is not None:        fileDialog.setFile(fileChooser_filename)

            fileDialog.setMultipleMode(fileChooser_multiMode)

            if fileChooser_open:
                fileDialog.setMode(FileDialog.LOAD)
            else:
                fileDialog.setMode(FileDialog.SAVE)

            # if fileChooser_fileFilterText is not None and (not Platform.isOSX() or not Platform.isOSXVersionAtLeast("10.13")):
            if fileChooser_fileFilterText is not None and (not Platform.isOSX() or isOSXVersionMontereyOrLater()):
                myPrint("DB",".. Adding file filter for: %s" %(fileChooser_fileFilterText))
                fileDialog.setFilenameFilter(ExtFilenameFilter(fileChooser_fileFilterText))

            fileDialog.setVisible(True)

            setFileDialogParameters(lDefaults=True)

            myPrint("DB", "FileDialog returned File:      %s" %(fileDialog.getFile()))
            myPrint("DB", "FileDialog returned Directory: %s" %(fileDialog.getDirectory()))

            if fileDialog.getFile() is None or fileDialog.getFile() == "": return None

            _theFile = os.path.join(fileDialog.getDirectory(), fileDialog.getFile())

        else:

            myPrint("DB", "Preparing JFileChooser() with path: %s" %(fileChooser_starting_dir))
            if fileChooser_filename is not None: myPrint("DB", "... and filename:                   %s" %(fileChooser_filename))

            if fileChooser_starting_dir is not None:
                jfc = JFileChooser(fileChooser_starting_dir)
            else:
                jfc = JFileChooser()

            if fileChooser_filename is not None: jfc.setSelectedFile(File(fileChooser_filename))
            setJFileChooserParameters(jfc,
                                      lPackagesT=lAllowTraversePackages,
                                      lApplicationsT=lAllowTraverseApplications,
                                      lNewFolderButton=lAllowNewFolderButton,
                                      lOptionsButton=lAllowOptionsButton)

            jfc.setDialogTitle(fileChooser_title)
            jfc.setMultiSelectionEnabled(fileChooser_multiMode)

            if fileChooser_selectFiles:
                jfc.setFileSelectionMode(JFileChooser.FILES_ONLY)         # FILES_ONLY, DIRECTORIES_ONLY, FILES_AND_DIRECTORIES
            else:
                jfc.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY)   # FILES_ONLY, DIRECTORIES_ONLY, FILES_AND_DIRECTORIES

            # if fileChooser_fileFilterText is not None and (not Platform.isOSX() or not Platform.isOSXVersionAtLeast("10.13")):
            if fileChooser_fileFilterText is not None and (not Platform.isOSX() or isOSXVersionMontereyOrLater()):
                myPrint("DB",".. Adding file filter for: %s" %(fileChooser_fileFilterText))
                jfc.setFileFilter(ExtFileFilterJFC(fileChooser_fileFilterText))

            if fileChooser_OK_text is not None:
                returnValue = jfc.showDialog(fileChooser_parent, fileChooser_OK_text)
            else:
                if fileChooser_open:
                    returnValue = jfc.showOpenDialog(fileChooser_parent)
                else:
                    returnValue = jfc.showSaveDialog(fileChooser_parent)

            if returnValue == JFileChooser.CANCEL_OPTION \
                    or (jfc.getSelectedFile() is None or jfc.getSelectedFile().getName()==""):
                myPrint("DB","JFileChooser was cancelled by user, or no file was selected...")
                return None

            _theFile = jfc.getSelectedFile().getAbsolutePath()
            myPrint("DB","JFileChooser returned File/path..: %s" %(_theFile))

        myPrint("DB","...File/path exists..: %s" %(os.path.exists(_theFile)))
        return _theFile

    class RequestFocusListener(AncestorListener):
        """Add this Listener to a JTextField by using .addAncestorListener(RequestFocusListener()) before calling JOptionPane.showOptionDialog()"""

        def __init__(self, removeListener=True):
            self.removeListener = removeListener

        def ancestorAdded(self, e):
            component = e.getComponent()
            component.requestFocusInWindow()
            component.selectAll()
            if (self.removeListener): component.removeAncestorListener(self)

        def ancestorMoved(self, e): pass
        def ancestorRemoved(self, e): pass

    class SearchAction(AbstractAction):

        def __init__(self, theFrame, searchJText):
            self.theFrame = theFrame
            self.searchJText = searchJText
            self.lastSearch = ""
            self.lastPosn = -1
            self.previousEndPosn = -1
            self.lastDirection = 0

        def actionPerformed(self, event):
            myPrint("D","in SearchAction(), Event: ", event)

            p = JPanel(FlowLayout())
            lbl = JLabel("Enter the search text:")
            tf = JTextField(self.lastSearch,20)
            p.add(lbl)
            p.add(tf)

            tf.addAncestorListener(RequestFocusListener())

            _search_options = [ "Next", "Previous", "Cancel" ]

            defaultDirection = _search_options[self.lastDirection]

            response = JOptionPane.showOptionDialog(self.theFrame,
                                                    p,
                                                    "Search for text",
                                                    JOptionPane.OK_CANCEL_OPTION,
                                                    JOptionPane.QUESTION_MESSAGE,
                                                    getMDIcon(None),
                                                    _search_options,
                                                    defaultDirection)

            lSwitch = False
            if (response == 0 or response == 1):
                if response != self.lastDirection: lSwitch = True
                self.lastDirection = response
                searchWhat = tf.getText()
            else:
                searchWhat = None

            del p, lbl, tf, _search_options

            if not searchWhat or searchWhat == "": return

            theText = self.searchJText.getText().lower()
            highlighter = self.searchJText.getHighlighter()
            highlighter.removeAllHighlights()

            startPos = 0

            if response == 0:
                direction = "[forwards]"
                if searchWhat == self.lastSearch:
                    startPos = self.lastPosn
                    if lSwitch: startPos=startPos+len(searchWhat)+1
                self.lastSearch = searchWhat

                # if startPos+len(searchWhat) >= len(theText):
                #     startPos = 0
                #
                pos = theText.find(searchWhat.lower(),startPos)     # noqa
                myPrint("DB", "Search %s Pos: %s, searchWhat: '%s', startPos: %s, endPos: %s" %(direction, pos, searchWhat,startPos, -1))

            else:
                direction = "[backwards]"
                endPos = len(theText)-1

                if searchWhat == self.lastSearch:
                    if self.previousEndPosn < 0: self.previousEndPosn = len(theText)-1
                    endPos = max(0,self.previousEndPosn)
                    if lSwitch: endPos = max(0,self.lastPosn-1)

                self.lastSearch = searchWhat

                pos = theText.rfind(searchWhat.lower(),startPos,endPos)     # noqa
                myPrint("DB", "Search %s Pos: %s, searchWhat: '%s', startPos: %s, endPos: %s" %(direction, pos, searchWhat,startPos,endPos))

            if pos >= 0:
                self.searchJText.setCaretPosition(pos)
                try:
                    highlighter.addHighlight(pos,min(pos+len(searchWhat),len(theText)),DefaultHighlighter.DefaultPainter)
                except: pass
                if response == 0:
                    self.lastPosn = pos+len(searchWhat)
                    self.previousEndPosn = len(theText)-1
                else:
                    self.lastPosn = pos-len(searchWhat)
                    self.previousEndPosn = pos-1
            else:
                self.lastPosn = 0
                self.previousEndPosn = len(theText)-1
                myPopupInformationBox(self.theFrame,"Searching %s text not found" %direction)

            return

    def saveOutputFile(_theFrame, _theTitle, _fileName, _theText):

        theTitle = "Select location to save the current displayed output... (CANCEL=ABORT)"
        copyToFile = getFileFromFileChooser(_theFrame,          # Parent frame or None
                                            get_home_dir(),     # Starting path
                                            _fileName,          # Default Filename
                                            theTitle,           # Title
                                            False,              # Multi-file selection mode
                                            False,              # True for Open/Load, False for Save
                                            True,               # True = Files, else Dirs
                                            None,               # Load/Save button text, None for defaults
                                            "txt",              # File filter (non Mac only). Example: "txt" or "qif"
                                            lAllowTraversePackages=False,
                                            lForceJFC=False,
                                            lForceFD=True,
                                            lAllowNewFolderButton=True,
                                            lAllowOptionsButton=True)

        if copyToFile is None or copyToFile == "":
            return
        elif not safeStr(copyToFile).endswith(".txt"):
            myPopupInformationBox(_theFrame, "Sorry - please use a .txt file extension when saving output txt")
            return
        elif ".moneydance" in os.path.dirname(copyToFile):
            myPopupInformationBox(_theFrame, "Sorry, please choose a location outside of the Moneydance location")
            return

        if not check_file_writable(copyToFile):
            myPopupInformationBox(_theFrame, "Sorry, that file/location does not appear allowed by the operating system!?")

        toFile = copyToFile
        try:
            with open(toFile, 'w') as f: f.write(_theText)
            myPrint("B", "%s: text output copied to: %s" %(_theTitle, toFile))

            if os.path.exists(toFile):
                play_the_money_sound()
                txt = "%s: Output text saved as requested to: %s" %(_theTitle, toFile)
                setDisplayStatus(txt, "B")
                myPopupInformationBox(_theFrame, txt)
            else:
                txt = "ERROR - failed to write output text to file: %s" %(toFile)
                myPrint("B", txt)
                myPopupInformationBox(_theFrame, txt)
        except:
            txt = "ERROR - failed to write output text to file: %s" %(toFile)
            dump_sys_error_to_md_console_and_errorlog()
            myPopupInformationBox(_theFrame, txt)

        return

    if MD_REF_UI is not None:       # Only action if the UI is loaded - e.g. scripts (not run time extensions)
        try: GlobalVars.defaultPrintFontSize = eval("MD_REF.getUI().getFonts().print.getSize()")   # Do this here as MD_REF disappears after script ends...
        except: GlobalVars.defaultPrintFontSize = 12
    else:
        GlobalVars.defaultPrintFontSize = 12

    ####################################################################################################################
    # PRINTING UTILITIES...: Points to MM, to Inches, to Resolution: Conversion routines etc
    _IN2MM = 25.4; _IN2CM = 2.54; _IN2PT = 72
    def pt2dpi(_pt,_resolution):    return _pt * _resolution / _IN2PT
    def mm2pt(_mm):                 return _mm * _IN2PT / _IN2MM
    def mm2mpt(_mm):                return _mm * 1000 * _IN2PT / _IN2MM
    def pt2mm(_pt):                 return round(_pt * _IN2MM / _IN2PT, 1)
    def mm2in(_mm):                 return _mm / _IN2MM
    def in2mm(_in):                 return _in * _IN2MM
    def in2mpt(_in):                return _in * _IN2PT * 1000
    def in2pt(_in):                 return _in * _IN2PT
    def mpt2in(_mpt):               return _mpt / _IN2PT / 1000
    def mm2px(_mm, _resolution):    return mm2in(_mm) * _resolution
    def mpt2px(_mpt, _resolution):  return mpt2in(_mpt) * _resolution

    def printDeducePrintableWidth(_thePageFormat, _pAttrs):

        _BUFFER_PCT = 0.95

        myPrint("DB", "PageFormat after user dialog: Portrait=%s Landscape=%s W: %sMM(%spts) H: %sMM(%spts) Paper: %s Paper W: %sMM(%spts) H: %sMM(%spts)"
                %(_thePageFormat.getOrientation()==_thePageFormat.PORTRAIT, _thePageFormat.getOrientation()==_thePageFormat.LANDSCAPE,
                  pt2mm(_thePageFormat.getWidth()),_thePageFormat.getWidth(), pt2mm(_thePageFormat.getHeight()),_thePageFormat.getHeight(),
                  _thePageFormat.getPaper(),
                  pt2mm(_thePageFormat.getPaper().getWidth()), _thePageFormat.getPaper().getWidth(), pt2mm(_thePageFormat.getPaper().getHeight()), _thePageFormat.getPaper().getHeight()))

        if _pAttrs.get(attribute.standard.MediaSizeName):
            myPrint("DB", "Requested Media: %s" %(_pAttrs.get(attribute.standard.MediaSizeName)))

        if not _pAttrs.get(attribute.standard.MediaPrintableArea):
            raise Exception("ERROR: MediaPrintableArea not present in pAttrs!?")

        mediaPA = _pAttrs.get(attribute.standard.MediaPrintableArea)
        myPrint("DB", "MediaPrintableArea settings from Printer Attributes..: w%sMM h%sMM MediaPrintableArea: %s, getPrintableArea: %s "
                % (mediaPA.getWidth(attribute.standard.MediaPrintableArea.MM),
                   mediaPA.getHeight(attribute.standard.MediaPrintableArea.MM),
                   mediaPA, mediaPA.getPrintableArea(attribute.standard.MediaPrintableArea.MM)))

        if (_thePageFormat.getOrientation()==_thePageFormat.PORTRAIT):
            deducedWidthMM = mediaPA.getWidth(attribute.standard.MediaPrintableArea.MM)
        elif (_thePageFormat.getOrientation()==_thePageFormat.LANDSCAPE):
            deducedWidthMM = mediaPA.getHeight(attribute.standard.MediaPrintableArea.MM)
        else:
            raise Exception("ERROR: thePageFormat.getOrientation() was not PORTRAIT or LANDSCAPE!?")

        myPrint("DB","Paper Orientation: %s" %("LANDSCAPE" if _thePageFormat.getOrientation()==_thePageFormat.LANDSCAPE else "PORTRAIT"))

        _maxPaperWidthPTS = mm2px(deducedWidthMM, GlobalVars.defaultDPI)
        _maxPaperWidthPTS_buff = _maxPaperWidthPTS * _BUFFER_PCT

        myPrint("DB", "MediaPrintableArea: deduced printable width: %sMM(%sPTS) (using factor of *%s = %sPTS)" %(round(deducedWidthMM,1), round(_maxPaperWidthPTS,1), _BUFFER_PCT, _maxPaperWidthPTS_buff))
        return deducedWidthMM, _maxPaperWidthPTS, _maxPaperWidthPTS_buff

    def loadDefaultPrinterAttributes(_pAttrs=None):

        if _pAttrs is None:
            _pAttrs = attribute.HashPrintRequestAttributeSet()
        else:
            _pAttrs.clear()

        # Refer: https://docs.oracle.com/javase/7/docs/api/javax/print/attribute/standard/package-summary.html
        _pAttrs.add(attribute.standard.DialogTypeSelection.NATIVE)
        if GlobalVars.defaultPrintLandscape:
            _pAttrs.add(attribute.standard.OrientationRequested.LANDSCAPE)
        else:
            _pAttrs.add(attribute.standard.OrientationRequested.PORTRAIT)
        _pAttrs.add(attribute.standard.Chromaticity.MONOCHROME)
        _pAttrs.add(attribute.standard.JobSheets.NONE)
        _pAttrs.add(attribute.standard.Copies(1))
        _pAttrs.add(attribute.standard.PrintQuality.NORMAL)

        return _pAttrs

    def printOutputFile(_callingClass=None, _theTitle=None, _theJText=None, _theString=None):

        # Possible future modification, leverage MDPrinter, and it's classes / methods to save/load preferences and create printers
        try:
            if _theJText is None and _theString is None: return
            if _theJText is not None and len(_theJText.getText()) < 1: return
            if _theString is not None and len(_theString) < 1: return

            # Make a new one for printing
            if _theJText is not None:
                printJTextArea = JTextArea(_theJText.getText())
            else:
                printJTextArea = JTextArea(_theString)

            printJTextArea.setEditable(False)
            printJTextArea.setLineWrap(True)    # As we are reducing the font size so that the width fits the page width, this forces any remainder to wrap
            # if _callingClass is not None: printJTextArea.setLineWrap(_callingClass.lWrapText)  # Mirror the word wrap set by user
            printJTextArea.setWrapStyleWord(False)
            printJTextArea.setOpaque(False); printJTextArea.setBackground(Color(0,0,0,0)); printJTextArea.setForeground(Color.BLACK)
            printJTextArea.setBorder(EmptyBorder(0, 0, 0, 0))

            # IntelliJ doesnt like the use of 'print' (as it's a keyword)
            try:
                if checkObjectInNameSpace("MD_REF"):
                    usePrintFontSize = eval("MD_REF.getUI().getFonts().print.getSize()")
                elif checkObjectInNameSpace("moneydance"):
                    usePrintFontSize = eval("moneydance.getUI().getFonts().print.getSize()")
                else:
                    usePrintFontSize = GlobalVars.defaultPrintFontSize  # Just in case cleanup_references() has tidied up once script ended
            except:
                usePrintFontSize = 12   # Font print did not exist before build 3036

            theFontToUse = getMonoFont()       # Need Monospaced font, but with the font set in MD preferences for print
            theFontToUse = theFontToUse.deriveFont(float(usePrintFontSize))
            printJTextArea.setFont(theFontToUse)

            def computeFontSize(_theComponent, _maxPaperWidth, _dpi):

                # Auto shrink font so that text fits on one line when printing
                # Note: Java seems to operate it's maths at 72DPI (so must factor that into the maths)
                try:
                    _DEFAULT_MIN_WIDTH = mm2px(100, _dpi)   # 100MM
                    _minFontSize = 5                        # Below 5 too small
                    theString = _theComponent.getText()
                    _startingComponentFont = _theComponent.getFont()

                    if not theString or len(theString) < 1: return -1

                    fm = _theComponent.getFontMetrics(_startingComponentFont)
                    _maxFontSize = curFontSize = _startingComponentFont.getSize()   # Max out at the MD default for print font size saved in preferences
                    myPrint("DB","Print - starting font:", _startingComponentFont)
                    myPrint("DB","... calculating.... The starting/max font size is:", curFontSize)

                    maxLineWidthInFile = _DEFAULT_MIN_WIDTH
                    longestLine = ""
                    for line in theString.split("\n"):              # Look for the widest line adjusted for font style
                        _w = pt2dpi(fm.stringWidth(line), _dpi)
                        # myPrint("DB", "Found line (len: %s):" %(len(line)), line)
                        # myPrint("DB", "...calculated length metrics: %s/%sPTS (%sMM)" %(fm.stringWidth(line), _w, pt2mm(_w)))
                        if _w > maxLineWidthInFile:
                            longestLine = line
                            maxLineWidthInFile = _w
                    myPrint("DB","longest line width %s chars; maxLineWidthInFile now: %sPTS (%sMM)" %(len(longestLine),maxLineWidthInFile, pt2mm(maxLineWidthInFile)))

                    # Now shrink the font size to fit.....
                    while (pt2dpi(fm.stringWidth(longestLine) + 5,_dpi) > _maxPaperWidth):
                        myPrint("DB","At font size: %s; (pt2dpi(fm.stringWidth(longestLine) + 5,_dpi):" %(curFontSize), (pt2dpi(fm.stringWidth(longestLine) + 5,_dpi)), pt2mm(pt2dpi(fm.stringWidth(longestLine) + 5,_dpi)), "MM", " >> max width:", _maxPaperWidth)
                        curFontSize -= 1
                        fm = _theComponent.getFontMetrics(Font(_startingComponentFont.getName(), _startingComponentFont.getStyle(), curFontSize))
                        myPrint("DB","... next will be: at font size: %s; (pt2dpi(fm.stringWidth(longestLine) + 5,_dpi):" %(curFontSize), (pt2dpi(fm.stringWidth(longestLine) + 5,_dpi)), pt2mm(pt2dpi(fm.stringWidth(longestLine) + 5,_dpi)), "MM")

                        myPrint("DB","... calculating.... length of line still too long... reducing font size to:", curFontSize)
                        if curFontSize < _minFontSize:
                            myPrint("DB","... calculating... Next font size is too small... exiting the reduction loop...")
                            break

                    if not Platform.isMac():
                        curFontSize -= 1   # For some reason, sometimes on Linux/Windows still too big....
                        myPrint("DB","..knocking 1 off font size for good luck...! Now: %s" %(curFontSize))

                    # Code to increase width....
                    # while (pt2dpi(fm.stringWidth(theString) + 5,_dpi) < _maxPaperWidth):
                    #     curSize += 1
                    #     fm = _theComponent.getFontMetrics(Font(_startingComponentFont.getName(), _startingComponentFont.getStyle(), curSize))

                    curFontSize = max(_minFontSize, curFontSize); curFontSize = min(_maxFontSize, curFontSize)
                    myPrint("DB","... calculating.... Adjusted final font size to:", curFontSize)

                except:
                    myPrint("B", "ERROR: computeFontSize() crashed?"); dump_sys_error_to_md_console_and_errorlog()
                    return -1
                return curFontSize

            myPrint("DB", "Creating new PrinterJob...")
            printer_job = PrinterJob.getPrinterJob()

            if GlobalVars.defaultPrintService is not None:
                printer_job.setPrintService(GlobalVars.defaultPrintService)
                myPrint("DB","Assigned remembered PrintService...: %s" %(printer_job.getPrintService()))

            if GlobalVars.defaultPrinterAttributes is not None:
                pAttrs = attribute.HashPrintRequestAttributeSet(GlobalVars.defaultPrinterAttributes)
            else:
                pAttrs = loadDefaultPrinterAttributes(None)

            pAttrs.remove(attribute.standard.JobName)
            pAttrs.add(attribute.standard.JobName("%s: %s" %(myModuleID.capitalize(), _theTitle), None))

            if GlobalVars.defaultDPI != 72:
                pAttrs.remove(attribute.standard.PrinterResolution)
                pAttrs.add(attribute.standard.PrinterResolution(GlobalVars.defaultDPI, GlobalVars.defaultDPI, attribute.standard.PrinterResolution.DPI))

            for atr in pAttrs.toArray(): myPrint("DB", "Printer attributes before user dialog: %s:%s" %(atr.getName(), atr))

            if not printer_job.printDialog(pAttrs):
                myPrint("DB","User aborted the Print Dialog setup screen, so exiting...")
                return

            selectedPrintService = printer_job.getPrintService()
            myPrint("DB", "User selected print service:", selectedPrintService)

            thePageFormat = printer_job.getPageFormat(pAttrs)

            # .setPrintable() seems to modify pAttrs & adds MediaPrintableArea. Do this before printDeducePrintableWidth()
            header = MessageFormat(_theTitle)
            footer = MessageFormat("- page {0} -")
            printer_job.setPrintable(printJTextArea.getPrintable(header, footer), thePageFormat)    # Yes - we do this twice

            for atr in pAttrs.toArray(): myPrint("DB", "Printer attributes **AFTER** user dialog (and setPrintable): %s:%s" %(atr.getName(), atr))

            deducedWidthMM, maxPaperWidthPTS, maxPaperWidthPTS_buff = printDeducePrintableWidth(thePageFormat, pAttrs)

            if _callingClass is None or not _callingClass.lWrapText:

                newFontSize = computeFontSize(printJTextArea, int(maxPaperWidthPTS), GlobalVars.defaultDPI)

                if newFontSize > 0:
                    theFontToUse = theFontToUse.deriveFont(float(newFontSize))
                    printJTextArea.setFont(theFontToUse)

            # avoiding Intellij errors
            # eval("printJTextArea.print(header, footer, False, selectedPrintService, pAttrs, True)")  # If you do this, then native features like print to PDF will get ignored - so print via PrinterJob

            # Yup - calling .setPrintable() twice - before and after .computeFontSize()
            printer_job.setPrintable(printJTextArea.getPrintable(header, footer), thePageFormat)
            eval("printer_job.print(pAttrs)")

            del printJTextArea

            myPrint("DB", "Saving current print service:", printer_job.getPrintService())
            GlobalVars.defaultPrinterAttributes = attribute.HashPrintRequestAttributeSet(pAttrs)
            GlobalVars.defaultPrintService = printer_job.getPrintService()

        except:
            myPrint("B", "ERROR in printing routines.....:"); dump_sys_error_to_md_console_and_errorlog()
        return

    def pageSetup():

        myPrint("DB","Printer Page setup routines..:")

        myPrint("DB", 'NOTE: A4        210mm x 297mm	8.3" x 11.7"	Points: w595 x h842')
        myPrint("DB", 'NOTE: Letter    216mm x 279mm	8.5" x 11.0"	Points: w612 x h791')

        pj = PrinterJob.getPrinterJob()

        # Note: PrintService is not used/remembered/set by .pageDialog

        if GlobalVars.defaultPrinterAttributes is not None:
            pAttrs = attribute.HashPrintRequestAttributeSet(GlobalVars.defaultPrinterAttributes)
        else:
            pAttrs = loadDefaultPrinterAttributes(None)

        for atr in pAttrs.toArray(): myPrint("DB", "Printer attributes before Page Setup: %s:%s" %(atr.getName(), atr))

        if not pj.pageDialog(pAttrs):
            myPrint("DB", "User cancelled Page Setup - exiting...")
            return

        for atr in pAttrs.toArray(): myPrint("DB", "Printer attributes **AFTER** Page Setup: %s:%s" %(atr.getName(), atr))

        if debug: printDeducePrintableWidth(pj.getPageFormat(pAttrs), pAttrs)

        myPrint("DB", "Printer selected: %s" %(pj.getPrintService()))

        GlobalVars.defaultPrinterAttributes = attribute.HashPrintRequestAttributeSet(pAttrs)
        myPrint("DB", "Printer Attributes saved....")

        return

    class SetupMDColors:

        OPAQUE = None
        FOREGROUND = None
        FOREGROUND_REVERSED = None
        BACKGROUND = None
        BACKGROUND_REVERSED = None

        def __init__(self): raise Exception("ERROR - Should not create instance of this class!")

        @staticmethod
        def updateUI():
            myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()")

            SetupMDColors.OPAQUE = False

            SetupMDColors.FOREGROUND = GlobalVars.CONTEXT.getUI().getColors().defaultTextForeground
            SetupMDColors.FOREGROUND_REVERSED = SetupMDColors.FOREGROUND

            SetupMDColors.BACKGROUND = GlobalVars.CONTEXT.getUI().getColors().defaultBackground
            SetupMDColors.BACKGROUND_REVERSED = SetupMDColors.BACKGROUND

            if ((not isMDThemeVAQua() and not isMDThemeDark() and isMacDarkModeDetected())
                    or (not isMacDarkModeDetected() and isMDThemeDarcula())):
                SetupMDColors.FOREGROUND_REVERSED = GlobalVars.CONTEXT.getUI().colors.defaultBackground
                SetupMDColors.BACKGROUND_REVERSED = GlobalVars.CONTEXT.getUI().colors.defaultTextForeground

    global ManuallyCloseAndReloadDataset            # Declare it for QuickJFrame/IDE, but not present in common code. Other code will ignore it

    class GetFirstMainFrame:

        DEFAULT_MAX_WIDTH = 1024
        DEFAULT_MAX_HEIGHT = 768

        def __init__(self): raise Exception("ERROR: DO NOT CREATE INSTANCE OF GetFirstMainFrame!")

        @staticmethod
        def getSize(defaultWidth=None, defaultHeight=None):
            if defaultWidth is None: defaultWidth = GetFirstMainFrame.DEFAULT_MAX_WIDTH
            if defaultHeight is None: defaultHeight = GetFirstMainFrame.DEFAULT_MAX_HEIGHT
            try:
                firstMainFrame = MD_REF.getUI().firstMainFrame
                return firstMainFrame.getSize()
            except: pass
            return Dimension(defaultWidth, defaultHeight)

        @staticmethod
        def getSelectedAccount():
            try:
                firstMainFrame = MD_REF.getUI().firstMainFrame
                return firstMainFrame.getSelectedAccount()
            except: pass
            return None

    class QuickJFrame():

        def __init__(self,
                     title,
                     output,
                     lAlertLevel=0,
                     copyToClipboard=False,
                     lJumpToEnd=False,
                     lWrapText=True,
                     lQuitMDAfterClose=False,
                     lRestartMDAfterClose=False,
                     screenLocation=None,
                     lAutoSize=False):
            self.title = title
            self.output = output
            self.lAlertLevel = lAlertLevel
            self.returnFrame = None
            self.copyToClipboard = copyToClipboard
            self.lJumpToEnd = lJumpToEnd
            self.lWrapText = lWrapText
            self.lQuitMDAfterClose = lQuitMDAfterClose
            self.lRestartMDAfterClose = lRestartMDAfterClose
            self.screenLocation = screenLocation
            self.lAutoSize = lAutoSize
            # if Platform.isOSX() and int(float(MD_REF.getBuild())) >= 3039: self.lAlertLevel = 0    # Colors don't work on Mac since VAQua
            if isMDThemeDark() or isMacDarkModeDetected(): self.lAlertLevel = 0

        class QJFWindowListener(WindowAdapter):

            def __init__(self, theFrame, lQuitMDAfterClose=False, lRestartMDAfterClose=False):
                self.theFrame = theFrame
                self.lQuitMDAfterClose = lQuitMDAfterClose
                self.lRestartMDAfterClose = lRestartMDAfterClose
                self.saveMD_REF = MD_REF

            def windowClosing(self, WindowEvent):                                                                       # noqa
                myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", WindowEvent)
                myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

                myPrint("DB", "QuickJFrame() Frame shutting down.... Calling .dispose()")
                self.theFrame.dispose()

                myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

            def windowClosed(self, WindowEvent):                                                                       # noqa
                myPrint("DB","In ", inspect.currentframe().f_code.co_name, "()")
                myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

                if self.lQuitMDAfterClose or self.lRestartMDAfterClose:
                    if "ManuallyCloseAndReloadDataset" not in globals():
                        myPrint("DB", "'ManuallyCloseAndReloadDataset' not in globals(), so just exiting MD the easy way...")
                        myPrint("B", "@@ EXITING MONEYDANCE @@")
                        MD_REF.getUI().exit()
                    else:
                        if self.lQuitMDAfterClose:
                            myPrint("B", "Quit MD after Close triggered... Now quitting MD")
                            ManuallyCloseAndReloadDataset.moneydanceExitOrRestart(lRestart=False)
                        elif self.lRestartMDAfterClose:
                            myPrint("B", "Restart MD after Close triggered... Now restarting MD")
                            ManuallyCloseAndReloadDataset.moneydanceExitOrRestart(lRestart=True)
                else:
                    myPrint("DB", "FYI No Quit MD after Close triggered... So doing nothing...")

        class CloseAction(AbstractAction):

            def __init__(self, theFrame):
                self.theFrame = theFrame

            def actionPerformed(self, event):
                myPrint("D","in CloseAction(), Event: ", event)
                myPrint("DB", "QuickJFrame() Frame shutting down....")

                try:
                    if not SwingUtilities.isEventDispatchThread():
                        SwingUtilities.invokeLater(GenericDisposeRunnable(self.theFrame))
                    else:
                        self.theFrame.dispose()
                except:
                    myPrint("B","Error. QuickJFrame dispose failed....?")
                    dump_sys_error_to_md_console_and_errorlog()


        class ToggleWrap(AbstractAction):

            def __init__(self, theCallingClass, theJText):
                self.theCallingClass = theCallingClass
                self.theJText = theJText

            def actionPerformed(self, event):
                myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

                self.theCallingClass.lWrapText = not self.theCallingClass.lWrapText
                self.theJText.setLineWrap(self.theCallingClass.lWrapText)

        class QuickJFrameNavigate(AbstractAction):

            def __init__(self, theJText, lTop=False, lBottom=False):
                self.theJText = theJText
                self.lTop = lTop
                self.lBottom = lBottom

            def actionPerformed(self, event):
                myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

                if self.lBottom: self.theJText.setCaretPosition(self.theJText.getDocument().getLength())
                if self.lTop:    self.theJText.setCaretPosition(0)

        class QuickJFramePrint(AbstractAction):

            def __init__(self, theCallingClass, theJText, theTitle=""):
                self.theCallingClass = theCallingClass
                self.theJText = theJText
                self.theTitle = theTitle

            def actionPerformed(self, event):
                myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )
                printOutputFile(_callingClass=self.theCallingClass, _theTitle=self.theTitle, _theJText=self.theJText)

        class QuickJFramePageSetup(AbstractAction):

            def __init__(self): pass

            def actionPerformed(self, event):
                myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )
                pageSetup()

        class QuickJFrameSaveTextToFile(AbstractAction):

            def __init__(self, theText, callingFrame):
                self.theText = theText
                self.callingFrame = callingFrame

            def actionPerformed(self, event):
                myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )
                saveOutputFile(self.callingFrame, "QUICKJFRAME", "%s_output.txt" %(myModuleID), self.theText)

        def show_the_frame(self):

            class MyQuickJFrameRunnable(Runnable):

                def __init__(self, callingClass):
                    self.callingClass = callingClass

                def run(self):                                                                                          # noqa
                    screenSize = Toolkit.getDefaultToolkit().getScreenSize()
                    frame_width = min(screenSize.width-20, max(GetFirstMainFrame.DEFAULT_MAX_WIDTH, int(round(GetFirstMainFrame.getSize().width *.9,0))))
                    frame_height = min(screenSize.height-20, max(GetFirstMainFrame.DEFAULT_MAX_HEIGHT, int(round(GetFirstMainFrame.getSize().height *.9,0))))

                    # JFrame.setDefaultLookAndFeelDecorated(True)   # Note: Darcula Theme doesn't like this and seems to be OK without this statement...
                    if self.callingClass.lQuitMDAfterClose:
                        extraText =  ">> MD WILL QUIT AFTER VIEWING THIS <<"
                    elif self.callingClass.lRestartMDAfterClose:
                        extraText =  ">> MD WILL RESTART AFTER VIEWING THIS <<"
                    else:
                        extraText = ""

                    jInternalFrame = MyJFrame(self.callingClass.title + " (%s+F to find/search for text)%s" %(MD_REF.getUI().ACCELERATOR_MASK_STR, extraText))
                    jInternalFrame.setName(u"%s_quickjframe" %myModuleID)

                    if not Platform.isOSX(): jInternalFrame.setIconImage(MDImages.getImage(MD_REF.getSourceInformation().getIconResource()))

                    jInternalFrame.setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE)
                    jInternalFrame.setResizable(True)

                    shortcut = Toolkit.getDefaultToolkit().getMenuShortcutKeyMaskEx()
                    jInternalFrame.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_W,  shortcut), "close-window")
                    jInternalFrame.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_F4, shortcut), "close-window")
                    jInternalFrame.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_F,  shortcut), "search-window")
                    jInternalFrame.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_P, shortcut),  "print-me")
                    jInternalFrame.getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0), "close-window")

                    theJText = JTextArea(self.callingClass.output)
                    theJText.setEditable(False)
                    theJText.setLineWrap(self.callingClass.lWrapText)
                    theJText.setWrapStyleWord(False)
                    theJText.setFont(getMonoFont())

                    jInternalFrame.getRootPane().getActionMap().put("close-window", self.callingClass.CloseAction(jInternalFrame))
                    jInternalFrame.getRootPane().getActionMap().put("search-window", SearchAction(jInternalFrame,theJText))
                    jInternalFrame.getRootPane().getActionMap().put("print-me", self.callingClass.QuickJFramePrint(self.callingClass, theJText, self.callingClass.title))
                    jInternalFrame.addWindowListener(self.callingClass.QJFWindowListener(jInternalFrame, self.callingClass.lQuitMDAfterClose, self.callingClass.lRestartMDAfterClose))

                    internalScrollPane = JScrollPane(theJText, JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED,JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED)

                    if self.callingClass.lAlertLevel>=2:
                        # internalScrollPane.setBackground(Color.RED)
                        theJText.setBackground(Color.RED)
                        theJText.setForeground(Color.BLACK)
                        theJText.setOpaque(True)
                    elif self.callingClass.lAlertLevel>=1:
                        # internalScrollPane.setBackground(Color.YELLOW)
                        theJText.setBackground(Color.YELLOW)
                        theJText.setForeground(Color.BLACK)
                        theJText.setOpaque(True)

                    if not self.callingClass.lAutoSize:
                        jInternalFrame.setPreferredSize(Dimension(frame_width, frame_height))

                    SetupMDColors.updateUI()

                    printButton = JButton("Print")
                    printButton.setToolTipText("Prints the output displayed in this window to your printer")
                    printButton.setOpaque(SetupMDColors.OPAQUE)
                    printButton.setBackground(SetupMDColors.BACKGROUND); printButton.setForeground(SetupMDColors.FOREGROUND)
                    printButton.addActionListener(self.callingClass.QuickJFramePrint(self.callingClass, theJText, self.callingClass.title))

                    if GlobalVars.defaultPrinterAttributes is None:
                        printPageSetup = JButton("Page Setup")
                        printPageSetup.setToolTipText("Printer Page Setup")
                        printPageSetup.setOpaque(SetupMDColors.OPAQUE)
                        printPageSetup.setBackground(SetupMDColors.BACKGROUND); printPageSetup.setForeground(SetupMDColors.FOREGROUND)
                        printPageSetup.addActionListener(self.callingClass.QuickJFramePageSetup())

                    saveButton = JButton("Save to file")
                    saveButton.setToolTipText("Saves the output displayed in this window to a file")
                    saveButton.setOpaque(SetupMDColors.OPAQUE)
                    saveButton.setBackground(SetupMDColors.BACKGROUND); saveButton.setForeground(SetupMDColors.FOREGROUND)
                    saveButton.addActionListener(self.callingClass.QuickJFrameSaveTextToFile(self.callingClass.output, jInternalFrame))

                    wrapOption = JCheckBox("Wrap Contents (Screen & Print)", self.callingClass.lWrapText)
                    wrapOption.addActionListener(self.callingClass.ToggleWrap(self.callingClass, theJText))
                    wrapOption.setForeground(SetupMDColors.FOREGROUND_REVERSED); wrapOption.setBackground(SetupMDColors.BACKGROUND_REVERSED)

                    topButton = JButton("Top")
                    topButton.setOpaque(SetupMDColors.OPAQUE)
                    topButton.setBackground(SetupMDColors.BACKGROUND); topButton.setForeground(SetupMDColors.FOREGROUND)
                    topButton.addActionListener(self.callingClass.QuickJFrameNavigate(theJText, lTop=True))

                    botButton = JButton("Bottom")
                    botButton.setOpaque(SetupMDColors.OPAQUE)
                    botButton.setBackground(SetupMDColors.BACKGROUND); botButton.setForeground(SetupMDColors.FOREGROUND)
                    botButton.addActionListener(self.callingClass.QuickJFrameNavigate(theJText, lBottom=True))

                    closeButton = JButton("Close")
                    closeButton.setOpaque(SetupMDColors.OPAQUE)
                    closeButton.setBackground(SetupMDColors.BACKGROUND); closeButton.setForeground(SetupMDColors.FOREGROUND)
                    closeButton.addActionListener(self.callingClass.CloseAction(jInternalFrame))

                    if Platform.isOSX():
                        save_useScreenMenuBar= System.getProperty("apple.laf.useScreenMenuBar")
                        if save_useScreenMenuBar is None or save_useScreenMenuBar == "":
                            save_useScreenMenuBar= System.getProperty("com.apple.macos.useScreenMenuBar")
                        System.setProperty("apple.laf.useScreenMenuBar", "false")
                        System.setProperty("com.apple.macos.useScreenMenuBar", "false")
                    else:
                        save_useScreenMenuBar = "true"

                    mb = JMenuBar()
                    mb.setBorder(EmptyBorder(0, 0, 0, 0))
                    mb.add(Box.createRigidArea(Dimension(10, 0)))
                    mb.add(topButton)
                    mb.add(Box.createRigidArea(Dimension(10, 0)))
                    mb.add(botButton)
                    mb.add(Box.createHorizontalGlue())
                    mb.add(wrapOption)

                    if GlobalVars.defaultPrinterAttributes is None:
                        mb.add(Box.createRigidArea(Dimension(10, 0)))
                        mb.add(printPageSetup)                                                                          # noqa

                    mb.add(Box.createHorizontalGlue())
                    mb.add(printButton)
                    mb.add(Box.createRigidArea(Dimension(10, 0)))
                    mb.add(saveButton)
                    mb.add(Box.createRigidArea(Dimension(10, 0)))
                    mb.add(closeButton)
                    mb.add(Box.createRigidArea(Dimension(30, 0)))

                    jInternalFrame.setJMenuBar(mb)

                    jInternalFrame.add(internalScrollPane)

                    jInternalFrame.pack()
                    if self.callingClass.screenLocation and isinstance(self.callingClass.screenLocation, Point):
                        jInternalFrame.setLocation(self.callingClass.screenLocation)
                    else:
                        jInternalFrame.setLocationRelativeTo(None)

                    jInternalFrame.setVisible(True)

                    if Platform.isOSX():
                        System.setProperty("apple.laf.useScreenMenuBar", save_useScreenMenuBar)
                        System.setProperty("com.apple.macos.useScreenMenuBar", save_useScreenMenuBar)

                    if "errlog.txt" in self.callingClass.title or self.callingClass.lJumpToEnd:
                        theJText.setCaretPosition(theJText.getDocument().getLength())

                    try:
                        if self.callingClass.copyToClipboard:
                            Toolkit.getDefaultToolkit().getSystemClipboard().setContents(StringSelection(self.callingClass.output), None)
                    except:
                        myPrint("J","Error copying contents to Clipboard")
                        dump_sys_error_to_md_console_and_errorlog()

                    self.callingClass.returnFrame = jInternalFrame

            if not SwingUtilities.isEventDispatchThread():
                myPrint("DB",".. Not running within the EDT so calling via MyQuickJFrameRunnable()...")
                SwingUtilities.invokeAndWait(MyQuickJFrameRunnable(self))
            else:
                myPrint("DB",".. Already within the EDT so calling naked...")
                MyQuickJFrameRunnable(self).run()

            return (self.returnFrame)

    class AboutThisScript(AbstractAction, Runnable):

        def __init__(self, theFrame):
            self.theFrame = theFrame
            self.aboutDialog = None

        def actionPerformed(self, event):
            myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()", "Event:", event)
            self.aboutDialog.dispose()  # Listener is already on the Swing EDT...

        def go(self):
            myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()")

            if not SwingUtilities.isEventDispatchThread():
                myPrint("DB",".. Not running within the EDT so calling via MyAboutRunnable()...")
                SwingUtilities.invokeAndWait(self)
            else:
                myPrint("DB",".. Already within the EDT so calling naked...")
                self.run()

        def run(self):                                                                                                  # noqa
            myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()")
            myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

            # noinspection PyUnresolvedReferences
            self.aboutDialog = JDialog(self.theFrame, "About", Dialog.ModalityType.MODELESS)

            shortcut = Toolkit.getDefaultToolkit().getMenuShortcutKeyMaskEx()
            self.aboutDialog.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_W, shortcut), "close-window")
            self.aboutDialog.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_F4, shortcut), "close-window")
            self.aboutDialog.getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0), "close-window")

            self.aboutDialog.getRootPane().getActionMap().put("close-window", self)
            self.aboutDialog.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE)

            if (not Platform.isMac()):
                # MD_REF.getUI().getImages()
                self.aboutDialog.setIconImage(MDImages.getImage(MD_REF.getSourceInformation().getIconResource()))

            aboutPanel = JPanel()
            aboutPanel.setLayout(FlowLayout(FlowLayout.LEFT))
            aboutPanel.setPreferredSize(Dimension(1120, 550))

            _label1 = JLabel(pad("Author: Stuart Beesley", 800))
            _label1.setForeground(getColorBlue())
            aboutPanel.add(_label1)

            _label2 = JLabel(pad("StuWareSoftSystems (2020-2023)", 800))
            _label2.setForeground(getColorBlue())
            aboutPanel.add(_label2)

            _label3 = JLabel(pad("Script/Extension: %s (build: %s)" %(GlobalVars.thisScriptName, version_build), 800))
            _label3.setForeground(getColorBlue())
            aboutPanel.add(_label3)

            displayString = scriptExit
            displayJText = JTextArea(displayString)
            displayJText.setFont(getMonoFont())
            displayJText.setEditable(False)
            displayJText.setLineWrap(False)
            displayJText.setWrapStyleWord(False)
            displayJText.setMargin(Insets(8, 8, 8, 8))

            aboutPanel.add(displayJText)

            self.aboutDialog.add(aboutPanel)

            self.aboutDialog.pack()
            self.aboutDialog.setLocationRelativeTo(None)
            self.aboutDialog.setVisible(True)

            myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

    def isGoodRate(theRate):

        if Double.isNaN(theRate) or Double.isInfinite(theRate) or theRate == 0:
            return False
        return True

    def safeInvertRate(theRate):

        if not isGoodRate(theRate):
            return theRate
        return (1.0 / theRate)

    def convertBytesGBs(_size): return round((_size/(1000.0*1000.0*1000)),1)

    def convertBytesMBs(_size): return round((_size/(1000.0*1000.0)),1)

    def convertBytesKBs(_size): return round((_size/(1000.0)),1)

    def convertMDShortDateFormat_strftimeFormat(lIncludeTime=False, lForceYYMMDDHMS=False):
        """Returns a Python strftime format string in accordance with MD Preferences for Date Format"""
        # https://strftime.org

        _MDFormat = MD_REF.getPreferences().getShortDateFormat()

        rtnFormat = "%Y-%m-%d"

        if lForceYYMMDDHMS:
            lIncludeTime = True
        else:
            if _MDFormat == "MM/dd/yyyy":
                rtnFormat = "%m/%d/%Y"
            elif _MDFormat == "MM.dd.yyyy":
                rtnFormat = "%m.%d.%Y"
            elif _MDFormat == "yyyy/MM/dd":
                rtnFormat = "%Y/%m/%d"
            elif _MDFormat == "yyyy.MM.dd":
                rtnFormat = "%Y.%m.%d"
            elif _MDFormat == "dd/MM/yyyy":
                rtnFormat = "%d/%m/%Y"
            elif _MDFormat == "dd.MM.yyyy":
                rtnFormat = "%d.%m.%Y"

        if lIncludeTime: rtnFormat += " %H:%M:%S"
        return rtnFormat

    def getHumanReadableDateTimeFromTimeStamp(_theTimeStamp, lIncludeTime=False, lForceYYMMDDHMS=False):
        return datetime.datetime.fromtimestamp(_theTimeStamp).strftime(convertMDShortDateFormat_strftimeFormat(lIncludeTime=lIncludeTime, lForceYYMMDDHMS=lForceYYMMDDHMS))

    def getHumanReadableModifiedDateTimeFromFile(_theFile, lIncludeTime=True, lForceYYMMDDHMS=True):
        return getHumanReadableDateTimeFromTimeStamp(os.path.getmtime(_theFile), lIncludeTime=lIncludeTime, lForceYYMMDDHMS=lForceYYMMDDHMS)

    def convertStrippedIntDateFormattedText(strippedDateInt, _format=None):

        # if _format is None: _format = "yyyy/MM/dd"
        if _format is None: _format = MD_REF.getPreferences().getShortDateFormat()

        if strippedDateInt is None or strippedDateInt == 0:
            return "<not set>"

        try:
            c = Calendar.getInstance()
            dateFromInt = DateUtil.convertIntDateToLong(strippedDateInt)
            c.setTime(dateFromInt)
            dateFormatter = SimpleDateFormat(_format)
            convertedDate = dateFormatter.format(c.getTime())
        except:
            return "<error>"

        return convertedDate

    def selectHomeScreen():

        try:
            currentViewAccount = MD_REF.getUI().firstMainFrame.getSelectedAccount()
            if currentViewAccount != MD_REF.getRootAccount():
                myPrint("DB","Switched to Home Page Summary Page (from: %s)" %(currentViewAccount))
                MD_REF.getUI().firstMainFrame.selectAccount(MD_REF.getRootAccount())
        except:
            myPrint("B","@@ Error switching to Summary Page (Home Page)")

    def fireMDPreferencesUpdated():
        """This triggers MD to firePreferencesUpdated().... Hopefully refreshing Home Screen Views too"""
        myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()" )

        class FPSRunnable(Runnable):
            def __init__(self): pass

            def run(self):
                myPrint("DB",".. Inside FPSRunnable() - calling firePreferencesUpdated()...")
                myPrint("B","Triggering an update to the Summary/Home Page View")
                MD_REF.getPreferences().firePreferencesUpdated()

        if not SwingUtilities.isEventDispatchThread():
            myPrint("DB",".. Not running within the EDT so calling via FPSRunnable()...")
            SwingUtilities.invokeLater(FPSRunnable())
        else:
            myPrint("DB",".. Already running within the EDT so calling FPSRunnable() naked...")
            FPSRunnable().run()
        return

    def decodeCommand(passedEvent):
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

    def getFieldByReflection(theObj, fieldName, isInt=False):
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

    def invokeMethodByReflection(theObj, methodName, params, *args):
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

    def setFieldByReflection(theObj, fieldName, newValue):
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

    def find_feature_module(theModule):
        # type: (str) -> bool
        """Searches Moneydance for a specific extension loaded"""
        fms = MD_REF.getLoadedModules()
        for fm in fms:
            if fm.getIDStr().lower() == theModule:
                myPrint("DB", "Found extension: %s" %(theModule))
                return fm
        return None

    GlobalVars.MD_KOTLIN_COMPILED_BUILD = 5000                                                                          # 2023.0
    def isKotlinCompiledBuild(): return (float(MD_REF.getBuild()) >= GlobalVars.MD_KOTLIN_COMPILED_BUILD)                                           # 2023.0(5000)

    def isMDPlusEnabledBuild(): return (float(MD_REF.getBuild()) >= GlobalVars.MD_MDPLUS_BUILD)                         # 2022.0

    def isAlertControllerEnabledBuild(): return (float(MD_REF.getBuild()) >= GlobalVars.MD_ALERTCONTROLLER_BUILD)       # 2022.3

    def genericSwingEDTRunner(ifOffEDTThenRunNowAndWait, ifOnEDTThenRunNowAndWait, codeblock, *args):
        """Will detect and then run the codeblock on the EDT"""

        isOnEDT = SwingUtilities.isEventDispatchThread()
        # myPrint("DB", "** In .genericSwingEDTRunner(), ifOffEDTThenRunNowAndWait: '%s', ifOnEDTThenRunNowAndWait: '%s', codeblock: '%s', args: '%s'" %(ifOffEDTThenRunNowAndWait, ifOnEDTThenRunNowAndWait, codeblock, args))
        myPrint("DB", "** In .genericSwingEDTRunner(), ifOffEDTThenRunNowAndWait: '%s', ifOnEDTThenRunNowAndWait: '%s', codeblock: <codeblock>, args: <args>" %(ifOffEDTThenRunNowAndWait, ifOnEDTThenRunNowAndWait))
        myPrint("DB", "** In .genericSwingEDTRunner(), isOnEDT:", isOnEDT)

        class GenericSwingEDTRunner(Runnable):

            def __init__(self, _codeblock, arguments):
                self.codeBlock = _codeblock
                self.params = arguments

            def run(self):
                myPrint("DB", "** In .genericSwingEDTRunner():: GenericSwingEDTRunner().run()... about to execute codeblock.... isOnEDT:", SwingUtilities.isEventDispatchThread())
                self.codeBlock(*self.params)
                myPrint("DB", "** In .genericSwingEDTRunner():: GenericSwingEDTRunner().run()... finished executing codeblock....")

        _gser = GenericSwingEDTRunner(codeblock, args)

        if ((isOnEDT and not ifOnEDTThenRunNowAndWait) or (not isOnEDT and not ifOffEDTThenRunNowAndWait)):
            myPrint("DB", "... calling codeblock via .invokeLater()...")
            SwingUtilities.invokeLater(_gser)
        elif not isOnEDT:
            myPrint("DB", "... calling codeblock via .invokeAndWait()...")
            SwingUtilities.invokeAndWait(_gser)
        else:
            myPrint("DB", "... calling codeblock.run() naked...")
            _gser.run()

        myPrint("DB", "... finished calling the codeblock via method reported above...")

    def genericThreadRunner(daemon, codeblock, *args):
        """Will run the codeblock on a new Thread"""

        # myPrint("DB", "** In .genericThreadRunner(), codeblock: '%s', args: '%s'" %(codeblock, args))
        myPrint("DB", "** In .genericThreadRunner(), codeblock: <codeblock>, args: <args>")

        class GenericThreadRunner(Runnable):

            def __init__(self, _codeblock, arguments):
                self.codeBlock = _codeblock
                self.params = arguments

            def run(self):
                myPrint("DB", "** In .genericThreadRunner():: GenericThreadRunner().run()... about to execute codeblock....")
                self.codeBlock(*self.params)
                myPrint("DB", "** In .genericThreadRunner():: GenericThreadRunner().run()... finished executing codeblock....")

        _gtr = GenericThreadRunner(codeblock, args)

        _t = Thread(_gtr, "NAB_GenericThreadRunner".lower())
        _t.setDaemon(daemon)
        _t.start()

        myPrint("DB", "... finished calling the codeblock...")

    GlobalVars.EXTN_PREF_KEY = "stuwaresoftsystems" + "." + myModuleID
    GlobalVars.EXTN_PREF_KEY_ENABLE_OBSERVER = "enable_observer"
    GlobalVars.EXTN_PREF_KEY_DISABLE_FORESIGHT = "disable_moneyforesight"

    class StreamTableFixed(StreamTable):
        """Replicates StreamTable. Provide a source to merge. Method .getBoolean() is 'fixed' to be backwards compatible with builds prior to Kotlin (Y/N vs 0/1)"""
        def __init__(self, _streamTableToCopy):
            # type: (StreamTable) -> None
            if not isinstance(_streamTableToCopy, StreamTable): raise Exception("LOGIC ERROR: Must pass a StreamTable! (Passed: %s)" %(type(_streamTableToCopy)))
            self.merge(_streamTableToCopy)

        def getBoolean(self, key, defaultVal):
            # type: (basestring, bool) -> bool
            if isKotlinCompiledBuild():     # MD2023.0 First Kotlin release - changed the code from detecting only Y/N to Y/N/T/F/0/1
                return super(self.__class__, self).getBoolean(key, defaultVal)
            _value = self.get(key, None)
            if _value in ["1", "Y", "y", "T", "t", "true", True]: return True
            if _value in ["0", "N", "n", "F", "f", "false", False]: return False
            return defaultVal

    def getExtensionDatasetSettings():
        # type: () -> SyncRecord
        _extnSettings =  GlobalVars.CONTEXT.getCurrentAccountBook().getLocalStorage().getSubset(GlobalVars.EXTN_PREF_KEY)
        if debug: myPrint("B", "Retrieved Extension Dataset Settings from LocalStorage: %s" %(_extnSettings))
        return _extnSettings

    def saveExtensionDatasetSettings(newExtnSettings):
        # type: (SyncRecord) -> None
        if not isinstance(newExtnSettings, SyncRecord):
            raise Exception("ERROR: 'newExtnSettings' is not a SyncRecord (given: '%s')" %(type(newExtnSettings)))
        _localStorage = GlobalVars.CONTEXT.getCurrentAccountBook().getLocalStorage()
        _localStorage.put(GlobalVars.EXTN_PREF_KEY, newExtnSettings)
        if debug: myPrint("B", "Stored Extension Dataset Settings into LocalStorage: %s" %(newExtnSettings))

    def getExtensionGlobalPreferences(enhancedBooleanCheck=True):
        # type: (bool) -> StreamTable
        _extnPrefs =  GlobalVars.CONTEXT.getPreferences().getTableSetting(GlobalVars.EXTN_PREF_KEY, StreamTable())
        if not isKotlinCompiledBuild():
            if enhancedBooleanCheck:
                _extnPrefs = StreamTableFixed(_extnPrefs)
                myPrint("DB", "... copied retrieved Extension Global Preferences into enhanced StreamTable for backwards .getBoolean() capability...")
        if debug: myPrint("B", "Retrieved Extension Global Preference: %s" %(_extnPrefs))
        return _extnPrefs

    def saveExtensionGlobalPreferences(newExtnPrefs):
        # type: (StreamTable) -> None
        if not isinstance(newExtnPrefs, StreamTable):
            raise Exception("ERROR: 'newExtnPrefs' is not a StreamTable (given: '%s')" %(type(newExtnPrefs)))
        GlobalVars.CONTEXT.getPreferences().setSetting(GlobalVars.EXTN_PREF_KEY, newExtnPrefs)
        if debug: myPrint("B", "Stored Extension Global Preferences: %s" %(newExtnPrefs))

    # END COMMON DEFINITIONS ###############################################################################################
    # END COMMON DEFINITIONS ###############################################################################################
    # END COMMON DEFINITIONS ###############################################################################################
    # COPY >> END

    # >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
    # >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
    # >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
    def load_StuWareSoftSystems_parameters_into_memory():
        pass
        return

    # >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
    def dump_StuWareSoftSystems_parameters_from_memory():
        pass
        return

    # Now just define debug at beginning if Console is open, or -d launch is used...
    # get_StuWareSoftSystems_parameters_from_file()

    # clear up any old left-overs....
    destroyOldFrames(myModuleID)

    myPrint("DB", "DEBUG IS ON..")

    if SwingUtilities.isEventDispatchThread():
        myPrint("DB", "FYI - This script/extension is currently running within the Swing Event Dispatch Thread (EDT)")
    else:
        myPrint("DB", "FYI - This script/extension is NOT currently running within the Swing Event Dispatch Thread (EDT)")

    def cleanup_actions(theFrame=None):
        myPrint("DB", "In", inspect.currentframe().f_code.co_name, "()")
        myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

        if theFrame is not None and not theFrame.isActiveInMoneydance:
            destroyOldFrames(myModuleID)

        try:
            MD_REF.getUI().setStatus(">> StuWareSoftSystems - thanks for using >> %s......." %(GlobalVars.thisScriptName),0)
        except:
            pass  # If this fails, then MD is probably shutting down.......

        if not GlobalVars.i_am_an_extension_so_run_headless: print(scriptExit)

        cleanup_references()

    # .moneydance_invoke_called() is used via the _invoke.py script as defined in script_info.dict. Not used for runtime extensions
    def moneydance_invoke_called(theCommand):
        # ... modify as required to handle .showURL() events sent to this extension/script...
        myPrint("B","INVOKE - Received extension command: '%s'" %(theCommand))

    GlobalVars.defaultPrintLandscape = True
    # END ALL CODE COPY HERE ###############################################################################################
    # END ALL CODE COPY HERE ###############################################################################################
    # END ALL CODE COPY HERE ###############################################################################################

    MD_REF.getUI().setStatus(">> StuWareSoftSystems - %s launching......." %(GlobalVars.thisScriptName),0)

    if isMDPlusEnabledBuild():
        myPrint("B", "MD2022+ build detected.. Enabling new features....")
        from com.infinitekind.moneydance.model import OnlineAccountMapping

    theOutput = ""
    global toolbox_script_runner

    try:
        def doMain():
            global debug, theOutput, ofx_populate_multiple_userids_frame_, toolbox_script_runner

            class MainAppRunnable(Runnable):
                def __init__(self): pass

                def run(self):                                                                                                  # noqa
                    global ofx_populate_multiple_userids_frame_     # global as defined here

                    myPrint("DB", "In MainAppRunnable()", inspect.currentframe().f_code.co_name, "()")
                    myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

                    # Create Application JFrame() so that all popups have correct Moneydance Icons etc
                    # JFrame.setDefaultLookAndFeelDecorated(True)   # Note: Darcula Theme doesn't like this and seems to be OK without this statement...
                    ofx_populate_multiple_userids_frame_ = MyJFrame()
                    ofx_populate_multiple_userids_frame_.setName(u"%s_main" %(myModuleID))
                    if (not Platform.isMac()):
                        MD_REF.getUI().getImages()
                        ofx_populate_multiple_userids_frame_.setIconImage(MDImages.getImage(MD_REF.getSourceInformation().getIconResource()))
                    ofx_populate_multiple_userids_frame_.setVisible(False)
                    ofx_populate_multiple_userids_frame_.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE)

                    myPrint("DB","Main JFrame %s for application created.." %(ofx_populate_multiple_userids_frame_.getName()))

            if not SwingUtilities.isEventDispatchThread():
                myPrint("DB",".. Main App Not running within the EDT so calling via MainAppRunnable()...")
                SwingUtilities.invokeAndWait(MainAppRunnable())
            else:
                myPrint("DB",".. Main App Already within the EDT so calling naked...")
                MainAppRunnable().run()

            def isMulti_OFXLastTxnUpdate_build(): return (float(MD_REF.getBuild()) >= GlobalVars.MD_MULTI_OFX_TXN_DNLD_DATES_BUILD)

            PARAMETER_KEY = "ofx_populate_multiple_userids"

            book = MD_REF.getCurrentAccountBook()

            if not isMDPlusEnabledBuild() and book.getItemForID("online_acct_mapping") is not None:
                if not myPopupAskQuestion(ofx_populate_multiple_userids_frame_,"OFX: POPULATE MULTIPLE USERIDs - WARNING","MD version older than MD2022 detected, but you already have MD2022 format Data (a downgrade?).... Proceed anyway?"):
                    alert = "MD version older than MD2022 detected, but you have an Online Account mapping object.. Have you downgraded? USER DECIDED NOT TO PROCEED!"
                    myPopupInformationBox(ofx_populate_multiple_userids_frame_, alert, theMessageType=JOptionPane.ERROR_MESSAGE)
                    raise QuickAbortThisScriptException(alert)

            def isUserEncryptionPassphraseSet():

                try:
                    keyFile = File(MD_REF.getCurrentAccount().getBook().getRootFolder(), "key")

                    keyInfo = SyncRecord()
                    fin = FileInputStream(keyFile)
                    keyInfo.readSet(fin)
                    fin.close()
                    return keyInfo.getBoolean("userpass", False)
                except:
                    pass
                return False

            def alert_and_exit(_alert):
                myPopupInformationBox(ofx_populate_multiple_userids_frame_, _alert, theMessageType=JOptionPane.ERROR_MESSAGE)
                raise QuickAbortThisScriptException(_alert)

            def my_getAccountKey(acct):      # noqa
                acctNum = acct.getAccountNum()
                if (acctNum <= 0):
                    return acct.getUUID()
                return str(acctNum)

            def my_createNewClientUID():
                _uid = UUID.randomUUID().toString()
                _uid = StringUtils.replaceAll(_uid, "-", "").strip()
                if len(_uid) > 32: _uid = String(_uid).substring(0, 32)
                return _uid

            class MyAcctFilter(AcctFilter):

                def __init__(self, selectType=0):
                    self.selectType = selectType

                def matches(self, acct):         # noqa

                    if self.selectType == 0 or self.selectType == 1: return False

                    if self.selectType == 2:
                        # noinspection PyUnresolvedReferences
                        if not (acct.getAccountType() == Account.AccountType.BANK
                                or acct.getAccountType() == Account.AccountType.CREDIT_CARD
                                or acct.getAccountType() == Account.AccountType.INVESTMENT):
                            return False
                        else:
                            return True

                    if self.selectType == 3:
                        # noinspection PyUnresolvedReferences
                        if not (acct.getAccountType() == Account.AccountType.BANK
                                or acct.getAccountType() == Account.AccountType.CREDIT_CARD
                                or acct.getAccountType() == Account.AccountType.INVESTMENT):
                            return False

                    if self.selectType == 4: return True

                    if (acct.getAccountOrParentIsInactive()): return False
                    if (acct.getHideOnHomePage() and acct.getBalance() == 0): return False

                    return True

            class StoreUserID():
                def __init__(self, _userID, _password="NOT SET"):
                    self.userID = _userID.strip()
                    self.password = _password
                    self.clientUID = None
                    self.accounts = []

                @staticmethod
                def findUserID(findUserID, listOfUserIDs):
                    # type: (str, [StoreUserID]) -> StoreUserID
                    """
                    Static Method to search a [list] of StoreUserID()
                    """
                    for userIDFromList in listOfUserIDs:
                        if findUserID.lower().strip() == userIDFromList.getUserID().lower().strip(): return userIDFromList
                    return None

                def setPassword(self, _password):       self.password = _password
                def setClientUID(self, _clientUID):     self.clientUID = _clientUID
                def setAccounts(self, _accounts):       self.accounts = _accounts

                def getUserID(self):    return self.userID
                def getPassword(self):  return self.password
                def getClientUID(self): return self.clientUID
                def getAccounts(self):  return self.accounts

                def __str__(self): return "UserID: %s Password: <%s>" %(self.getUserID(), ("*"*len(self.getPassword())))
                def __repr__(self): return self.__str__()

            def getPlaidService():
                _serviceList = MD_REF.getCurrentAccountBook().getOnlineInfo().getAllServices()
                for _service in _serviceList:
                    if _service.getTIKServiceID() == "md:plaid": return _service
                return None

            # def getMsgSetTag(messageType):
            #     # com.infinitekind.moneydance.model.OnlineService.getMsgSetTag(int)
            #     if messageType == 1:    return "fiprofile"
            #     elif messageType == 3:  return "signup"
            #     elif messageType == 4:  return "banking"
            #     elif messageType == 5:  return "creditcard"
            #     elif messageType == 6:  return "investment"
            #     elif messageType == 7:  return "interbankxfr"
            #     elif messageType == 8:  return "wirexfr"
            #     elif messageType == 9:  return "billpay"
            #     elif messageType == 10: return "email"
            #     elif messageType == 11:  return "seclist"
            #     elif messageType == 12:  return "billdir"
            #     return "default"

            def getAccountMsgType(_theAccount):
                # type: (Account) -> int

                # noinspection PyUnresolvedReferences
                if _theAccount.getAccountType() == Account.AccountType.BANK:            return 4
                elif _theAccount.getAccountType() == Account.AccountType.CREDIT_CARD:   return 5
                elif _theAccount.getAccountType() == Account.AccountType.INVESTMENT:    return 6
                alert_and_exit("LOGIC ERROR: Found Bank Account Type: %s" %(_theAccount.getAccountType()))

            class StoreAccountList():
                def __init__(self, obj):
                    if isinstance(obj,Account):
                        self.obj = obj                          # type: Account
                    else:
                        self.obj = None
                    self.OFXAccountType = None
                    self.OFXBankID = None
                    self.OFXAccountNumber = None
                    self.OFXAccountMsgType =  None
                    self.OFXBrokerID =  None

                def getAccount(self): return self.obj

                def setOFXAccountType(self, _at):     self.OFXAccountType = _at
                def setOFXBankID(self, _bankID):      self.OFXBankID = _bankID
                def setOFXAccountNumber(self, _an):   self.OFXAccountNumber = _an
                def setOFXAccountMsgType(self, _amt): self.OFXAccountMsgType = _amt
                def setOFXBrokerID(self, _bID):       self.OFXBrokerID = _bID

                def getOFXAccountType(self):    return self.OFXAccountType
                def getOFXBankID(self):         return self.OFXBankID
                def getOFXAccountNumber(self):  return self.OFXAccountNumber
                def getOFXAccountMsgType(self): return self.OFXAccountMsgType
                def getOFXBrokerID(self):       return self.OFXBrokerID

                def __str__(self):
                    if self.obj is None: return "Invalid Acct Obj or None"
                    return "%s : %s" %(self.obj.getAccountType(),self.obj.getFullAccountName())

                def __repr__(self):
                    return self.__str__()

            def getUpdatedAuthenticationKeys():

                _storage = SyncRecord()
                _authenticationCache = SyncRecord()

                try:
                    LS = MD_REF.getCurrentAccount().getBook().getLocalStorage()
                    LS.save()

                    localFile = File(os.path.join(MD_REF.getCurrentAccount().getBook().getRootFolder().getAbsolutePath(),"safe","settings"))
                    if localFile.exists() and localFile.canRead():
                        inx = LS.openFileForReading("settings")
                        _storage.readSet(inx)
                        _authenticationCache = _storage.getSubset("_authentication")
                        inx.close()
                except:
                    myPrint("B","@@@ ERROR Reading authentication cache from settings @@@")
                    dump_sys_error_to_md_console_and_errorlog()

                del _storage
                return _authenticationCache


            class MyJListRenderer(DefaultListCellRenderer):

                def __init__(self):
                    super(DefaultListCellRenderer, self).__init__()                                                             # noqa

                def getListCellRendererComponent(self, thelist, value, index, isSelected, cellHasFocus):
                    lightLightGray = Color(0xDCDCDC)
                    c = super(MyJListRenderer, self).getListCellRendererComponent(thelist, value, index, isSelected, cellHasFocus) # noqa
                    # c.setBackground(self.getBackground() if index % 2 == 0 else lightLightGray)

                    # Create a line separator between accounts
                    c.setBorder(BorderFactory.createMatteBorder(0, 0, 1, 0, lightLightGray))
                    return c

            class MyDefaultListSelectionModel(DefaultListSelectionModel):
                # Change the selector - so not to deselect items when selecting others...
                def __init__(self):
                    super(DefaultListSelectionModel, self).__init__()                                                           # noqa

                def setSelectionInterval(self, start, end):
                    if (start != end):
                        super(MyDefaultListSelectionModel, self).setSelectionInterval(start, end)                               # noqa
                    elif self.isSelectedIndex(start):
                        self.removeSelectionInterval(start, end)
                    else:
                        self.addSelectionInterval(start, end)

            class MyJScrollPaneForJOptionPane(JScrollPane):               # Allows a scrollable menu in JOptionPane
                def __init__(self, _component, _max_w=800, _max_h=600):
                    super(JScrollPane, self).__init__(_component)
                    self.maxWidth = _max_w
                    self.maxHeight = _max_h
                    self.borders = 90
                    self.screenSize = Toolkit.getDefaultToolkit().getScreenSize()

                def getPreferredSize(self):
                    frame_width = int(round((self.screenSize.width - self.borders) *.9,0))
                    frame_height = int(round((self.screenSize.height - self.borders) *.9,0))
                    return Dimension(min(self.maxWidth, frame_width), min(self.maxHeight, frame_height))

            theOutput = "OFX_POPULATE_MULTIPLE_USERIDS.PY Utility Script....:\n" \
                        " ===================================================\n\n"
            theOutput += "Build %s of script\n\n" %(version_build)

            lRunningFromToolbox = False
            if "toolbox_script_runner" in globals():
                global toolbox_script_runner
                myPrint("B","Toolbox script runner detected: %s (build: %s)" %(toolbox_script_runner, version_build))
                theOutput += "\n** Running from within the Toolbox extension **\n\n"
                lRunningFromToolbox = True

            if isMDPlusEnabledBuild() and float(MD_REF.getBuild()) < 4059:
                alert_and_exit("WARNING: You need to upgrade to at least version MD2022.1(4059) for USAA Connections to work properly! - No changes made!")

            if not lRunningFromToolbox:
                ask = MyPopUpDialogBox(ofx_populate_multiple_userids_frame_,
                                       "This script will update an existing (working) OFX profile with multiple User IDs:",
                                       "Get the latest useful_scripts.zip package from: %s \n"
                                       "You have to select a WORKING profile, answer a series of questions, and enter your UserID/Password details\n"
                                       "..A working profile that has been successfully used on all of your accounts will be the best....\n\n"
                                       "NOTE: This script will largely ignore BillPay.. If it's there it will 'gloss over it'....\n\n"
                                       "If your Bank requires a (hidden) machine specific Client UUID, then script generates a new one (per user)\n"
                                       "... This may mean you have to re-approve access for each user (review email / Bank's online security centre)\n"
                                       "You can also generate a new Default Client UUID for all other Profiles that use a default (OPTIONAL)\n"
                                       "NOTE: User1 is always your default UserID too... Enter the total number of Users you need.\n"
                                       "You can review the existing (hidden) OFX data, and edit it if you wish (very carefully) [OPTIONAL]\n"
                                       "You can also enter missing key data... You will need to know your Bank's reference for your Account Number\n"
                                       "Toolbox extension > Online Banking (OFX) Menu > View installed bank / service profiles might help you here...."
                                       %(GlobalVars.MYPYTHON_DOWNLOAD_URL),
                                       theTitle="KNOWLEDGE",
                                       lCancelButton=True,OKButtonText="CONFIRMED", lAlertLevel=1)
            else:
                ask = MyPopUpDialogBox(ofx_populate_multiple_userids_frame_,
                                       "This script will update an existing (working) OFX profile with multiple User IDs:",
                                       "Get the latest Toolbox extension from: %s\n"
                                       "You have to select a WORKING profile, answer a series of questions, and enter your UserID/Password details\n"
                                       "..A working profile that has been successfully used on all of your accounts will be the best....\n\n"
                                       "NOTE: This script will largely ignore BillPay.. If it's there it will 'gloss over it'....\n\n"
                                       "If your Bank requires a (hidden) machine specific Client UUID, then script generates a new one (per user)\n"
                                       "... This may mean you have to re-approve access for each user (review email / Bank's online security centre)\n"
                                       "You can also generate a new Default Client UUID for all other Profiles that use a default (OPTIONAL)\n"
                                       "NOTE: User1 is always your default UserID too... Enter the total number of Users you need.\n"
                                       "You can review the existing (hidden) OFX data, and edit it if you wish (very carefully) [OPTIONAL]\n"
                                       "You can also enter missing key data... You will need to know your Bank's reference for your Account Number\n"
                                       "Toolbox extension > Online Banking (OFX) Menu > View installed bank / service profiles might help you here...."
                                       %(GlobalVars.MYPYTHON_DOWNLOAD_URL),
                                       theTitle="KNOWLEDGE",
                                       lCancelButton=True,OKButtonText="CONFIRMED", lAlertLevel=1)
            if not ask.go():
                alert_and_exit("Knowledge rejected - no changes made")

            if not lRunningFromToolbox:
                if not myPopupAskQuestion(ofx_populate_multiple_userids_frame_, "BACKUP", "ADD USERIDs TO OFX PROFILE >> HAVE YOU DONE A GOOD BACKUP FIRST?", theMessageType=JOptionPane.WARNING_MESSAGE):
                    alert_and_exit("BACKUP FIRST! PLEASE USE FILE>EXPORT BACKUP then come back!! - No changes made.")

                if not myPopupAskQuestion(ofx_populate_multiple_userids_frame_, "DISCLAIMER", "DO YOU ACCEPT YOU RUN THIS AT YOUR OWN RISK?", theMessageType=JOptionPane.WARNING_MESSAGE):
                    alert_and_exit("Disclaimer rejected - no changes made")

            lIgnoreBillPay = True
            if not lIgnoreBillPay:
                if not myPopupAskQuestion(ofx_populate_multiple_userids_frame_, "BILLPAY", "CONFIRM YOU ARE NOT USING BILLPAY ON THIS PROFILE (This will not work for BP)?", theMessageType=JOptionPane.WARNING_MESSAGE):
                    alert_and_exit("Using BillPay so aborting (sorry) - no changes made")

            # if not myPopupAskQuestion(ofx_populate_multiple_userids_frame_, "INVESTMENTS", "CONFIRM YOU ARE NOT USING INVESTMENT ACCOUNTS ON THIS PROFILE (This will NOT work for Investments)?", theMessageType=JOptionPane.WARNING_MESSAGE):
            #     alert_and_exit("Using Investments so aborting (sorry) - no changes made")

            lCachePasswords = (isUserEncryptionPassphraseSet() and MD_REF.getUI().getCurrentAccounts().getBook().getLocalStorage().getBoolean("store_passwords", False))
            if not lCachePasswords:
                if not myPopupAskQuestion(ofx_populate_multiple_userids_frame_,"STORE PASSWORDS","Your system is not set up to save/store passwords. Do you want to continue?",theMessageType=JOptionPane.ERROR_MESSAGE):
                    alert_and_exit("Please set up Master password and select store passwords first - then try again - no changes made")
                theOutput += "\nProceeding even though system is not set up for passwords\n"

            serviceList = MD_REF.getCurrentAccount().getBook().getOnlineInfo().getAllServices()  # type: [OnlineService]
            if getPlaidService() in serviceList: serviceList.remove(getPlaidService())

            selectedService = JOptionPane.showInputDialog(ofx_populate_multiple_userids_frame_,
                                                              "Select the OFX Service Profile to manage UserIDs",
                                                              "Select OFX Service Profile",
                                                              JOptionPane.WARNING_MESSAGE,
                                                              getMDIcon(None),
                                                              serviceList,
                                                              None)         # type: [OnlineService]

            if not selectedService:
                alert_and_exit("ERROR NO OFX SERVICE PROFILE SELECTED")

            if isinstance(selectedService,OnlineService): pass

            ################################################################################################################

            USAA_FI_ID = "67811"
            USAA_FI_ORG = "USAA Federal Savings Bank"
            OLD_TIK_FI_ID = "md:1295"
            NEW_TIK_FI_ID = "md:custom-1295"

            lSelectedUSAA = False

            if (selectedService.getTIKServiceID() == OLD_TIK_FI_ID or selectedService.getTIKServiceID() == NEW_TIK_FI_ID
                    or selectedService.getServiceId() == ":%s:%s" %(USAA_FI_ORG, USAA_FI_ID)
                    or "USAA" in selectedService.getFIOrg()
                    or "USAA" in selectedService.getFIName()):
                lSelectedUSAA = True
                theOutput += "USAA Profile has been selected - will manage special client UUIDs....\n"

            theOutput += "OFX Service Profile selected: %s(%s)\n\n" %(selectedService, selectedService.getTIKServiceID())

            matchingAccts = []
            accounts = AccountUtil.allMatchesForSearch(MD_REF.getCurrentAccount().getBook(), MyAcctFilter(4))
            for acct in accounts:
                if acct.getBillPayFI() == selectedService:
                    if not lIgnoreBillPay:
                        alert_and_exit("ERROR - BILLPAY LINK FOUND ON ACCT: %s - ABORTING" %(acct))
                    else:
                        theOutput += "Ignoring BillPay link found on account: %s\n" %(acct)
                if acct.getBankingFI() == selectedService:
                    # noinspection PyUnresolvedReferences
                    if (acct.getAccountType() == Account.AccountType.BANK
                            or acct.getAccountType() == Account.AccountType.CREDIT_CARD
                            or acct.getAccountType() == Account.AccountType.INVESTMENT):
                        matchingAccts.append(acct)
                    else:
                        alert_and_exit("ERROR: FOUND LINKED ACCT (%s) THAT IS NOT BANK, CREDIT CARD OR INVESTMENT - ABORTING" %(acct))

            if len(matchingAccts) < 1:
                theOutput += "WARNING! No Accounts are already linked to this profile? Are you sure this is a good profile?\n"
                if myPopupAskQuestion(ofx_populate_multiple_userids_frame_,"NO ACCOUNTS LINKED >> FORCE LINK ACCOUNT", "Would you like to try and force link an account to this profile?"):
                    theOutput += "@@@ FORCE LINKING ACCOUNTS INTO THIS PROFILE..!! @@\n"
                else:
                    alert_and_exit("ERROR NO ACCOUNTS LINKED TO THIS OFX SERVICE PROFILE FOUND")

            theOutput += "\n"

            theOutput += "Found %s Accounts linked to this OFX Service Profile\n" %(len(matchingAccts))
            for acct in matchingAccts: theOutput += "... Account: %s\n" %(acct.getFullAccountName())

            theOutput += "\n"

            realms = selectedService.getRealms()
            if len(realms) < 1: alert_and_exit("ERROR NO REALMS WITHIN THIS OFX SERVICE PROFILE FOUND")

            theOutput += "Found %s Realms within this OFX Service Profile\n" %(len(realms))
            for realm in realms: theOutput += "... Realm: %s\n" %(realm)
            theRealm = realms[0]    # Take the first one...

            if len(realms) > 1: alert_and_exit("ERROR MORE THAN 1 REALMS WITHIN THIS OFX SERVICE PROFILE FOUND - LOGIC NOT PROGRAMMED >> SORRY :-<")

            theOutput += "\n"

            lOverrideRootUUID = False
            if selectedService.getClientIDRequired(theRealm):
                if myPopupAskQuestion(ofx_populate_multiple_userids_frame_,"KEEP DATASET's DEFAULT CLIENT UUID [Normal Option]", "Do you want to keep this Dataset's default Client UUID? (YES=KEEP, NO=Reset/Regenerate[optional])?"):
                    theOutput += "User opted to keep this Dataset's / Root's current Master/Default Client UUID.....\n"
                else:
                    lOverrideRootUUID = True
                    theOutput += "User opted to generate a new Root Master/Default Client UUID for this Dataset.....\n"
            else:
                theOutput += "This service profile does not require ClientUUIDs... skipping....\n"

            theOutput += "\n"

            theOutput += "Selecting Accounts to link to profile:\n"
            theOutput += "--------------------------------------\n"

            listOfAccountsForJList = []

            getAccounts = AccountUtil.allMatchesForSearch(MD_REF.getCurrentAccountBook(), MyAcctFilter(2))
            getAccounts = sorted(getAccounts, key=lambda sort_x: (sort_x.getAccountType(), sort_x.getFullAccountName().upper()))
            for acct in getAccounts:
                if not lIgnoreBillPay and acct.getBillPayFI() == selectedService: alert_and_exit("LOGIC ERROR: PARSING getAccounts() - FOUND BILLPAY")
                elif acct.getBankingFI() == selectedService: pass
                elif acct.getBillPayFI() == selectedService: pass
                elif acct.getBankingFI() is not None or acct.getBillPayFI() is not None: continue
                elif acct.getAccountOrParentIsInactive(): continue
                elif acct.getHideOnHomePage() and acct.getBalance() == 0: continue
                listOfAccountsForJList.append(StoreAccountList(acct))
            del getAccounts

            jlst = JList([])
            jlst.setBackground(MD_REF.getUI().getColors().listBackground)
            jlst.setCellRenderer(MyJListRenderer())
            jlst.setFixedCellHeight(jlst.getFixedCellHeight()+30)
            jlst.setSelectionMode(ListSelectionModel.MULTIPLE_INTERVAL_SELECTION)
            jlst.setSelectionModel(MyDefaultListSelectionModel())
            jlst.setListData(listOfAccountsForJList)

            jlstIndex = 0
            preSelectList = []
            for acctObj in listOfAccountsForJList:
                if acctObj.obj in matchingAccts:
                    preSelectList.append(jlstIndex)
                jlstIndex += 1
            jlst.setSelectedIndices(preSelectList)
            if len(matchingAccts) > 0: jlst.ensureIndexIsVisible(preSelectList[0])
            del preSelectList, listOfAccountsForJList

            jsp = MyJScrollPaneForJOptionPane(jlst,750,600)

            options = ["EXIT", "PROCEED"]
            userAction = (JOptionPane.showOptionDialog(ofx_populate_multiple_userids_frame_,
                                                       jsp,
                                                       "OFX MANAGE USERIDs - CAREFULLY SELECT THE ACCOUNTS TO LINK/MANAGE",
                                                       JOptionPane.OK_CANCEL_OPTION,
                                                       JOptionPane.QUESTION_MESSAGE,
                                                       getMDIcon(lAlwaysGetIcon=True),
                                                       options, options[0]))
            if userAction != 1:
                alert_and_exit("OFX ACCOUNT SELECTION ABORTED")
            del jsp, userAction

            selectedAccountsList = []
            for selectedAccount in jlst.getSelectedValuesList():
                theOutput += "...account %s selected...\n" %(selectedAccount.obj)
                selectedAccountsList.append(selectedAccount.obj)
            del jlst

            if len(selectedAccountsList) < 1: alert_and_exit("ERROR NO ACCOUNTS SELECTED")

            theOutput += "\n"

            accountsToManage = []

            delinkAccounts = []
            for acct in matchingAccts:
                if acct not in selectedAccountsList:
                    if myPopupAskQuestion(ofx_populate_multiple_userids_frame_, "ACCT SELECTED FOR DE-LINK",
                                          "Are you sure you want to de-link Account %s from OFX Service Profile?" %(acct)):
                        theOutput += "Will DE-LINK Account: %s from OFX Service Profile\n" %(acct)
                        delinkAccounts.append(acct)
                    else:
                        alert_and_exit("ERROR - USER DOES NOT WANT TO DE-LINK: %s" %(acct))

            linkNewAccounts = []
            for acct in selectedAccountsList:
                if acct in matchingAccts:
                    theOutput += "No action on Account %s as already linked and still selected\n" %(acct)
                else:
                    if myPopupAskQuestion(ofx_populate_multiple_userids_frame_, "ACCT SELECTED FOR NEW LINK",
                                          "Are you sure you want to LINK Account %s to OFX Service Profile?" %(acct)):
                        theOutput += "Will LINK Account: %s to OFX Service Profile\n" %(acct)
                        linkNewAccounts.append(acct)
                    else:
                        alert_and_exit("ERROR - USER DOES NOT WANT TO LINK: %s" %(acct))
                accountsToManage.append(acct)
            del selectedAccountsList, matchingAccts

            theOutput += "\n"

            ####################################################################################################################
            # Validate OFX Setup on Accounts selected for linking

            theOutput += "Account OFX Data Validation / Correction...:\n"
            theOutput += "--------------------------------------------\n"

            OFX_ACCOUNT_TYPES = ["CHECKING", "SAVINGS", "MONEYMRKT", "CREDITLINE"]

            updateAccountOFXDataList = []

            lReviewExistingOFXData = myPopupAskQuestion(ofx_populate_multiple_userids_frame_,"REVIEW EXISTING OFX DATA BY ACCOUNT", "Would you like to review existing OFX data by account (advanced)?")
            lEnterMissingOFXData = myPopupAskQuestion(ofx_populate_multiple_userids_frame_,"VALIDATE OFX DATA BY ACCOUNT", "Would you like to enter missing OFX data by account (advanced)?")

            if lReviewExistingOFXData or lEnterMissingOFXData:
                for acct in accountsToManage:
                    theOutput += "Validating Acct: %s\n" %(acct)

                    accountTypeOFX = routeID = bankID = brokerID = None                                                 # noqa

                    # noinspection PyUnresolvedReferences
                    if acct.getAccountType() == Account.AccountType.BANK:

                        accountTypeOFX = acct.getOFXAccountType()
                        if lReviewExistingOFXData or (lEnterMissingOFXData and accountTypeOFX == ""):
                            theOutput += "Account: %s account type is currently %s\n" %(acct, accountTypeOFX)
                            accountTypeOFX = (OFX_ACCOUNT_TYPES[0] if (acct.getOFXAccountType() == "") else accountTypeOFX)

                            accountTypeOFX = JOptionPane.showInputDialog(ofx_populate_multiple_userids_frame_,
                                                                         "Carefully select the type for this account",
                                                                         "ACCOUNT TYPE FOR ACCOUNT: %s" %(acct),
                                                                         JOptionPane.INFORMATION_MESSAGE,
                                                                         getMDIcon(lAlwaysGetIcon=True),
                                                                         OFX_ACCOUNT_TYPES,
                                                                         accountTypeOFX)
                            if not lEnterMissingOFXData and not accountTypeOFX:
                                accountTypeOFX = None
                            elif not accountTypeOFX:
                                alert_and_exit("ERROR - NO ACCOUNT TYPE SELECTED FOR: %s - Aborting" %(acct))
                            theOutput += "Account %s - selected type: %s\n" %(acct,accountTypeOFX)
                        else:
                            accountTypeOFX = None

                        routeID = acct.getOFXBankID()
                        if lReviewExistingOFXData or (lEnterMissingOFXData and routeID == ""):
                            routeID = myPopupAskForInput(ofx_populate_multiple_userids_frame_, "Routing - Account: %s" % (acct), "Routing:", "Type/Paste your Routing Number - very carefully", routeID)
                            if not lEnterMissingOFXData and (routeID is None or routeID == ""):
                                routeID = None
                            elif routeID is None or routeID == "" or len(routeID) < 6:
                                alert_and_exit("ERROR - invalid Routing supplied for acct: %s - Aborting" %(acct))
                            theOutput += "Account %s - routeID entered: %s\n" %(acct, routeID)
                        else:
                            routeID = None

                    # noinspection PyUnresolvedReferences
                    if acct.getAccountType() == Account.AccountType.INVESTMENT:

                        brokerID = acct.getOFXBrokerID()
                        if lReviewExistingOFXData or (lEnterMissingOFXData and brokerID == ""):
                            brokerID = myPopupAskForInput(ofx_populate_multiple_userids_frame_, "BrokerID - Account: %s" %(acct), "BrokerID:", "Type/Paste your BrokerID - very carefully", brokerID)
                            if not lEnterMissingOFXData and (brokerID is None or brokerID == ""):
                                brokerID = None
                            elif brokerID is None or brokerID == "" or len(brokerID) < 4:
                                alert_and_exit("ERROR - invalid BrokerID supplied for acct: %s - Aborting" %(acct))
                            theOutput += "Account %s - BrokerID entered: %s\n" %(acct, brokerID)
                        else:
                            brokerID = None

                    bankID = acct.getOFXAccountNumber()
                    if lReviewExistingOFXData or (lEnterMissingOFXData and bankID == ""):
                        bankID = myPopupAskForInput(ofx_populate_multiple_userids_frame_, "ACCOUNT: %s" %(acct), "Bank/CC/Investment Acct Number:", "Type/Paste your Account / CC Number - very carefully", bankID)
                        if not lEnterMissingOFXData and (bankID is None or bankID == ""):
                            bankID = None
                        elif bankID is None or bankID == "":
                            alert_and_exit("ERROR - no Account Number supplied for acct: %s - Aborting" %(acct))
                        theOutput += "Account %s - Entered Number: %s\n" %(acct, bankID)
                    else:
                        bankID = None

                    if accountTypeOFX or routeID or bankID or brokerID:
                        storeAcct = StoreAccountList(acct)
                        storeAcct.setOFXAccountType(accountTypeOFX)
                        storeAcct.setOFXBankID(routeID)
                        storeAcct.setOFXAccountNumber(bankID)
                        storeAcct.setOFXBrokerID(brokerID)
                        # noinspection PyUnresolvedReferences
                        storeAcct.setOFXAccountMsgType(getAccountMsgType(acct))
                        updateAccountOFXDataList.append(storeAcct)

                theOutput += "Validation complete.... %s Accounts need to be updated\n" %(len(updateAccountOFXDataList))

            lOFXNumbersFailedValidation = lFoundUpdateOFX = False
            for acct in accountsToManage:
                for storedAcct in updateAccountOFXDataList:
                    if storedAcct.getAccount() == acct:
                        if storedAcct.getOFXAccountNumber() is None or storedAcct.getOFXAccountNumber() == "":
                            lOFXNumbersFailedValidation = True
                        lFoundUpdateOFX = True
                        break
                if not lFoundUpdateOFX:
                    if acct.getOFXAccountNumber() != "":
                        continue
                    lOFXNumbersFailedValidation = True
                if lOFXNumbersFailedValidation:
                    theOutput += "...ERROR - ACCOUNT: %s HAS NO OFX ACCOUNT NUMBER\n" %(acct)
                    break
                lFoundUpdateOFX = False

            if lOFXNumbersFailedValidation: alert_and_exit("ERROR - NOT ALL YOUR ACCOUNTS HAVE AN ASSIGNED OFX NUMBER... CANNOT PROCEED..!")
            del lOFXNumbersFailedValidation, lFoundUpdateOFX

            theOutput += "\n"
            theOutput += "@@ Client ID for Realm: %s required flag: %s\n" %(theRealm, selectedService.getClientIDRequired(theRealm))
            theOutput += "--------------------------------------\n"

            theOutput += "\n"

            theOutput += "Harvesting existing UserID details from root...:\n"
            theOutput += "------------------------------------------------\n"

            authKeyPrefix = "ofx.client_uid"
            specificAuthKeyPrefix = authKeyPrefix+"::" + selectedService.getTIKServiceID() + "::"

            root = MD_REF.getRootAccount()
            rootKeys = list(root.getParameterKeys())

            harvestedUserIDList = []

            for i in range(0,len(rootKeys)):
                rk = rootKeys[i]
                if rk.startswith(specificAuthKeyPrefix):
                    rk_value = root.getParameter(rk)
                    harvestedUID = StoreUserID(rk[len(specificAuthKeyPrefix):])
                    if harvestedUID.getUserID() != "null":
                        theOutput += "... Harvested old authKey %s: ClientUID: %s\n" %(rk,rk_value)
                        harvestedUID.setClientUID(rk_value)
                        harvestedUserIDList.append(harvestedUID)

            if len(harvestedUserIDList) > 0:
                theOutput += "Harvested User and ClientUIDs...:\n"
                for harvested in harvestedUserIDList:
                    theOutput += "Harvested User: %s, ClientUID: %s\n" %(harvested.getUserID(), harvested.getClientUID())

            theOutput += "\n"

            theOutput += "Harvesting existing UserIDs from service profile:...:\n"
            theOutput += "-----------------------------------------------------\n"
            for pKey in selectedService.getParameterKeys():
                if pKey.startswith("so_user_id"):
                    theOutput += "Existing User: %s\n" %(selectedService.getParameter(pKey))

            theOutput += "\n"

            if isUserEncryptionPassphraseSet():
                theOutput += "Harvesting Existing UserIDs/Passwords from authentication cache:...:\n"
                theOutput += "--------------------------------------------------------------------\n"
                authKeys = getUpdatedAuthenticationKeys()
                if len(authKeys) > 0:
                    for theAuthKey in sorted(authKeys.keys()):                                                                  # noqa
                        if (selectedService.getFIOrg() + "--" + selectedService.getFIId() + "--") in theAuthKey:
                            theOutput += "Existing AuthCache Entry: %s\n" %(authKeys.get(theAuthKey))                              # noqa
                del authKeys

                theOutput += "\n"


            howManyUsers = 0
            userResponse = myPopupAskForInput(ofx_populate_multiple_userids_frame_, "OFX USERID MANAGEMENT", "Total number of UserIDs:", "How many UserIDs (in Total, including default) do you want to setup/manage?",defaultValue=howManyUsers)
            if userResponse is None or not StringUtils.isInteger(userResponse) or int(userResponse) < 1 or int(userResponse) > 7:
                alert_and_exit("ERROR: INVALID TOTAL NUMBER OF USERIDs TO MANAGE ENTERED (range 1-7)")
            howManyUsers = int(userResponse)
            theOutput += "Total UserIDs to Manage: %s\n" %(howManyUsers)

            if howManyUsers > len(accountsToManage):
                alert_and_exit("ERROR - YOU HAVE SPECIFIED MORE TOTAL USERIDs THAN ACCOUNTS?!")


            theOutput += "Gathering Default UserID details...:\n"
            theOutput += "------------------------------------\n"

            oldDefaultUserID = selectedService.getUserId(theRealm, None)
            if oldDefaultUserID is None: oldDefaultUserID = ""
            theOutput += "Default UserID: %s\n" %("<NONE>" if (oldDefaultUserID == "") else oldDefaultUserID)

            defaultEntry = oldDefaultUserID
            while True:
                userID = myPopupAskForInput(ofx_populate_multiple_userids_frame_, "DEFAULT UserID", "DEFAULT UserID (User1)", "Edit DEFAULT UserID (carefully) or leave unchanged (Will become User 1 too)", defaultEntry)
                theOutput += "userID entered: %s\n" %userID
                if userID is None:
                    alert_and_exit("ERROR - No DEFAULT userID supplied! Aborting")
                defaultEntry = userID
                if userID is None or userID == "" or userID == "UserID" or len(userID)<4:
                    theOutput += "\n ** ERROR - No valid DEFAULT userID supplied - try again ** \n"
                    continue
                break

            if oldDefaultUserID == userID:
                theOutput += "Default UserID (also User1) (%s) will NOT be changed\n" % (oldDefaultUserID)
            else:
                theOutput += "Default UserID (also User1) (%s) will be changed to: %s\n" % (oldDefaultUserID, userID)
            newDefaultUserID = userID
            del defaultEntry, userID

            theOutput += "\n"

            theOutput += "Gathering new UserID and Passwords...:\n"
            theOutput += "--------------------------------------\n"

            userIDList = []
            for onUser in range(0,howManyUsers):

                if onUser == 0:
                    defaultEntry = userID = newDefaultUserID                                                            # noqa
                else:
                    defaultEntry = "UserID%s" %(onUser+1)

                    while True:
                        userID = myPopupAskForInput(ofx_populate_multiple_userids_frame_, "ENTER UserID", "UserID%s:" %(onUser+1),
                                                    "Enter UserID%s (min length 4) carefully" %(onUser+1), defaultEntry)
                        theOutput += "userID%s entered: %s\n" %(onUser+1, userID)
                        if userID is None: alert_and_exit("ERROR - no userID%s supplied! Aborting" %(onUser+1))
                        defaultEntry = userID
                        for uid in userIDList:
                            if uid.getUserID() == userID:
                                theOutput += "\n ** ERROR - DUPLICATE userID%s supplied - try again ** \n" %(onUser+1)
                                continue
                        if userID is None or userID == "" or userID == ("UserID%s" %(onUser+1)) or len(userID)<4:
                            theOutput += "\n ** ERROR - no valid userID%s supplied - try again ** \n" %(onUser+1)
                            continue
                        break
                userIDList.append(StoreUserID(userID))
                del defaultEntry, userID

            if len(userIDList) != howManyUsers:
                alert_and_exit("LOGIC ERROR: NUMBER OF USERIDs ENTERED (%s) DOES NOT MATCH (%s)" %(len(userIDList), howManyUsers))

            if newDefaultUserID != userIDList[0].getUserID():
                alert_and_exit("LOGIC ERROR: NEW DEFAULT USERID %s DOES NOT MATCH userIDList[0] %s" %(newDefaultUserID, userIDList[0].getUserID()))

            theOutput += "\n"

            if lSelectedUSAA:
                for findStoredUser in userIDList:
                    foundHarvestedStoredUser = StoreUserID.findUserID(findStoredUser.getUserID(),harvestedUserIDList)    # type: StoreUserID
                    if foundHarvestedStoredUser is not None:
                        if foundHarvestedStoredUser.getClientUID() is not None:
                            findStoredUser.setClientUID(foundHarvestedStoredUser.getClientUID())
                        else:
                            alert_and_exit("LOGIC ERROR: Found harvested UserID (%s) with no ClientUID?!" %(findStoredUser))
            else:
                theOutput += "Skipping matching ClientUIDs into new UserID list as not updating a USAA profile...\n"
            del harvestedUserIDList

            for userID in userIDList: theOutput += "UserID entered: %s (Harvested ClientUID: %s)\n" %(userID, userID.getClientUID())

            theOutput += "\n"

            for onUser in range(0,len(userIDList)):
                defaultEntry = "%s:*****" %(onUser+1)
                while True:
                    password = myPopupAskForInput(ofx_populate_multiple_userids_frame_, "ENTER PASSWORD", "USERID%s:%s Password:" %(onUser+1, userIDList[onUser].getUserID()),
                                                  "Type/Paste your Password%s (min length 4) very carefully" %(onUser+1), defaultEntry)
                    theOutput += "User%s: %s : password entered: %s\n" %(onUser+1, userIDList[onUser].getUserID(), password)
                    if password is None:
                        alert_and_exit("ERROR - User: %s - no password %s supplied! Aborting" %(userIDList[onUser].getUserID(), onUser+1))
                    defaultEntry = password
                    if password is None or password == "" or password == ("%s:*****" %(onUser+1)) or len(password) < 4:
                        theOutput += "\n ** ERROR - User: %s - no password %s supplied - try again ** \n" %(userIDList[onUser].getUserID(), onUser+1)
                        continue
                    break
                userIDList[onUser].setPassword(password)
                del defaultEntry, password

            theOutput += "\n"

            if lSelectedUSAA:
                for onUser in range(0,len(userIDList)):
                    if userIDList[onUser].getClientUID() is None:
                        defaultEntry = "nnnnnnnn-nnnn-nnnn-nnnn-nnnnnnnnnnnn"
                    else:
                        defaultEntry = userIDList[onUser].getClientUID()
                    while True:
                        uuid = myPopupAskForInput(ofx_populate_multiple_userids_frame_, "ENTER UUID", "USERID%s:%s ClientUID:" %(onUser+1, userIDList[onUser].getUserID()),
                                                      "Paste the Bank Supplied UUID 36 digits 8-4-4-4-12 very carefully", defaultEntry)
                        theOutput += "User%s: %s : ClientUID entered: %s\n" %(onUser+1, userIDList[onUser].getUserID(), uuid)
                        if uuid is None:
                            alert_and_exit("ERROR - User: %s - no ClientUID %s supplied! Aborting" %(userIDList[onUser].getUserID(), onUser+1))
                        defaultEntry = uuid
                        if (uuid is None or uuid == "" or len(uuid) != 36 or uuid == "nnnnnnnn-nnnn-nnnn-nnnn-nnnnnnnnnnnn" or
                                (str(uuid)[8]+str(uuid)[13]+str(uuid)[18]+str(uuid)[23]) != "----"):
                            theOutput += "\n ** ERROR - no valid ClientUID for User%s (%s) supplied - try again ** \n" %(onUser+1,userIDList[onUser].getUserID())
                            continue
                        break
                    userIDList[onUser].setClientUID(uuid)
                    del defaultEntry, uuid

            theOutput += "\n"

            theOutput += "Final list of resolved UserIDs, Passwords, and ClientUIDs (if required)....\n"
            for userID in userIDList:
                if userID.getPassword() == "NOT SET": alert_and_exit("LOGIC ERROR - PASSWORD NOT SET FOR: %s" %(userID))
                theOutput += "UserID entered: %s (Password: %s) (ClientUID: %s)\n" %(userID.getPassword(),userID.getPassword(),userID.getClientUID())

            theOutput += "\n"

            ####################################################################################################################
            ############################### MATCH USERIDs TO ACCOUNTS
            theOutput += "Matching UserIDs to Accounts...:\n"
            theOutput += "--------------------------------\n"
            listOfAccountsForUserID = []
            for acct in accountsToManage: listOfAccountsForUserID.append(StoreAccountList(acct))

            for onUser in range(0,len(userIDList)):
                theOutput += "Account / UserID%s Match: %s\n" %(onUser+1, userIDList[onUser].getUserID())

                jlst = JList([])
                jlst.setBackground(MD_REF.getUI().getColors().listBackground)
                jlst.setCellRenderer( MyJListRenderer() )
                jlst.setFixedCellHeight(jlst.getFixedCellHeight()+30)
                jlst.setSelectionMode(ListSelectionModel.MULTIPLE_INTERVAL_SELECTION)
                jlst.setSelectionModel(MyDefaultListSelectionModel())
                jlst.setListData(listOfAccountsForUserID)

                jsp = MyJScrollPaneForJOptionPane(jlst,750,600)

                options = ["EXIT", "PROCEED"]
                userAction = (JOptionPane.showOptionDialog(ofx_populate_multiple_userids_frame_,
                                                           jsp,
                                                           "SELECT THE ACCOUNT(S) TO LINK TO USERID%s: %s" %(onUser+1, userIDList[onUser].getUserID()),
                                                           JOptionPane.OK_CANCEL_OPTION,
                                                           JOptionPane.QUESTION_MESSAGE,
                                                           getMDIcon(lAlwaysGetIcon=True),
                                                           options, options[0]))
                if userAction != 1: alert_and_exit("OFX ACCOUNT / USER MATCH SELECTION ABORTED")
                del jsp, userAction

                selectedAccountsList = []
                for selectedAccount in jlst.getSelectedValuesList():
                    theOutput += "...account %s selected for match to UserID: %s\n" %(selectedAccount.obj, userIDList[onUser].getUserID())
                    selectedAccountsList.append(selectedAccount.getAccount())
                    listOfAccountsForUserID.remove(selectedAccount)
                del jlst
                if len(selectedAccountsList) < 1: alert_and_exit("ERROR NO ACCOUNTS SELECTED TO MATCH TO USERID%s: %s" %(onUser+1, userIDList[onUser].getUserID()))
                userIDList[onUser].setAccounts(selectedAccountsList)
                del selectedAccountsList

            del listOfAccountsForUserID
            ####################################################################################################################
            theOutput += "\n"

            theOutput += "Sanity check...:\n"
            theOutput += "----------------\n"

            # Sanity check!
            iCheckAccountNumber = 0
            for onUser in range(0,len(userIDList)): iCheckAccountNumber += len(userIDList[onUser].getAccounts())
            if len(accountsToManage) != iCheckAccountNumber:
                alert_and_exit("LOGIC ERROR: accountsToManage(%s) <> total of UserID.getAccounts() (%s)!? - exiting without changes" %(len(accountsToManage), iCheckAccountNumber))
            del iCheckAccountNumber

            # This is it folks.... Shall we go for it?
            if not myPopupAskQuestion(ofx_populate_multiple_userids_frame_,"PROCEED WITH OFX PROFILE CHANGES", "Proceed with changes?"):
                alert_and_exit("USER DECLINED TO PROCEED WITH OFX PROFILE CHANGES")

            theOutput += "\n\n"

            # ... and WE ARE OFF AND RUNNING......
            theOutput += "PROCEEDING WITH OFX PROFILE UPDATES:\n"

            theOutput += "\n"

            theOutput += "Removing existing profile links from mapping object - will rebuild the table...:\n"
            theOutput += "--------------------------------------------------------------------------------\n"

            lMappingNeedsSync = False
            mappingObject = book.getItemForID("online_acct_mapping")
            if mappingObject is not None:
                mappingKeys = list(mappingObject.getParameterKeys())
                for i in range(0, len(mappingKeys)):
                    pk = mappingKeys[i]
                    if pk.startswith("map.") and (selectedService.getTIKServiceID() in pk):
                        theOutput += "Deleting old Account Mapping %s: %s\n" %(pk, mappingObject.getParameter(pk))
                        mappingObject.setEditingMode()
                        mappingObject.setParameter(pk, None)
                        lMappingNeedsSync = True
                del mappingKeys
                if lMappingNeedsSync: mappingObject.syncItem()
            del mappingObject

            mappingObject = None
            lManualMappingNeedsSync = False

            mappingObjectClass = None
            lMappingNeedsSync = False

            if isMDPlusEnabledBuild():
                theOutput += "Grabbing reference to OnlineAccountMapping() with selected service profile...\n"
                mappingObjectClass =  OnlineAccountMapping(book, selectedService)
            else:
                theOutput += "Grabbing manual reference to MD2022 mapping object (if it exists)...\n"
                mappingObject = book.getItemForID("online_acct_mapping")

            ####################################################################################################################
            theOutput += "\n"
            theOutput += "De-linking accounts, updating OFX data, linking new accounts...:\n"
            theOutput += "----------------------------------------------------------------\n"

            if len(delinkAccounts): myPrint("B","DE-LINKING ACCOUNTS..:")
            for acct in delinkAccounts:
                theOutput += "...De-linking acct: %s\n" %(acct)
                acct.setBankingFI(None)
                if isMDPlusEnabledBuild():
                    acct.setOnlineIDForServiceID(selectedService.getTIKServiceID(), None)
                acct.syncItem()
            del delinkAccounts

            theOutput += "\n"

            if len(updateAccountOFXDataList): theOutput += "UPDATING ACCOUNTS WITH OFX DATA..:\n"
            for acct in updateAccountOFXDataList:
                theOutput += "...Updating acct: %s\n" %(acct.getAccount())
                acct.getAccount().setEditingMode()
                if acct.getOFXBankID():         acct.getAccount().setOFXBankID(acct.getOFXBankID())
                if acct.getOFXAccountNumber():  acct.getAccount().setOFXAccountNumber(acct.getOFXAccountNumber())
                if acct.getOFXAccountType():    acct.getAccount().setOFXAccountType(acct.getOFXAccountType())
                if acct.getOFXAccountMsgType(): acct.getAccount().setOFXAccountMsgType(acct.getOFXAccountMsgType())
                if acct.getOFXBrokerID():       acct.getAccount().setOFXBrokerID(acct.getOFXBrokerID())
                acct.getAccount().setBankingFI(selectedService)
                if isMDPlusEnabledBuild():
                    if acct.getOFXAccountNumber():
                        acct.getAccount().setOnlineIDForServiceID(selectedService.getTIKServiceID(),acct.getOFXAccountNumber())
                acct.getAccount().syncItem()
            del updateAccountOFXDataList

            theOutput += "\n"

            if len(linkNewAccounts): theOutput += "CREATING NEW LINKS FOR ACCOUNTS..:\n"
            for acct in linkNewAccounts:
                theOutput += "...Creating new OFX link for acct: %s\n" %(acct)
                acct.setBankingFI(selectedService)
                if isMDPlusEnabledBuild():
                    acct.setOnlineIDForServiceID(selectedService.getTIKServiceID(),acct.getOFXAccountNumber())
                acct.syncItem()
            del linkNewAccounts

            ####################################################################################################################
            theOutput += "\n"

            theOutput += "Updating root...:\n"
            theOutput += "-----------------\n"

            if selectedService.getClientIDRequired(theRealm) or lOverrideRootUUID:
                theOutput += "ClientUID required.... Setting up root with keys...\n"

                root = MD_REF.getRootAccount()
                rootKeys = list(root.getParameterKeys())                                                                # noqa

                root.setEditingMode()

                # This sets the Dataset Client UUID in Root - the default for all OFX scripts that need it.. (unless specifically set by profile/user)
                theDefaultUUID = root.getParameter(authKeyPrefix, "")
                if lOverrideRootUUID or theDefaultUUID == "":
                    theDefaultUUID = my_createNewClientUID()
                    theOutput += "Overriding Root's default UUID. Was: %s >> changing to >> %s\n" %(root.getParameter(authKeyPrefix, None), theDefaultUUID)
                    root.setParameter(authKeyPrefix, theDefaultUUID)

                if selectedService.getClientIDRequired(theRealm):

                    # Delete all existing root keys for this specific profile
                    rootKeys = list(root.getParameterKeys())
                    for i in range(0,len(rootKeys)):
                        rk = rootKeys[i]
                        if rk.startswith(authKeyPrefix) and (selectedService.getTIKServiceID() in rk):
                            theOutput += "Deleting old authKey %s: %s\n" %(rk,root.getParameter(rk))
                            root.setParameter(rk, None)

                    # Generate a new Client UUID for this profile's default and user1
                    if lSelectedUSAA:
                        theDefaultUUID = userIDList[0].getClientUID()
                    else:
                        theDefaultUUID = my_createNewClientUID()

                    root.setParameter(authKeyPrefix+"_default_user"+"::" + selectedService.getTIKServiceID(), newDefaultUserID)
                    root.setParameter(authKeyPrefix+"::" + selectedService.getTIKServiceID() + "::" + "null",   theDefaultUUID)

                    for onUser in range(0,len(userIDList)):
                        theOutput += "Updating Root >> UserID%s (%s)\n" %(onUser+1, userIDList[onUser].getUserID())

                        if onUser == 0:
                            # User 1 keeps the same Client UUID as this Profile's default....
                            whatClientID = theDefaultUUID
                        else:
                            # New Client UUID for all extra users
                            if lSelectedUSAA: whatClientID = userIDList[onUser].getClientUID()
                            else: whatClientID = my_createNewClientUID()

                        root.setParameter(authKeyPrefix+"::" + selectedService.getTIKServiceID() + "::" + userIDList[onUser].getUserID(), whatClientID)

                root.syncItem()
                theOutput += "Root UserIDs and UUIDs updated...\n"
                del theDefaultUUID
            else:
                theOutput += "ClientUID NOT required.... Skipping Root updates.....\n"
            del lOverrideRootUUID

            ####################################################################################################################

            theOutput += "\n"

            theOutput += "Updating Service Profile with updated UserIDs....:\n"
            theOutput += "--------------------------------------------------\n"

            selectedService.setEditingMode()

            selectedService.setUserId(theRealm, None, newDefaultUserID)
            del oldDefaultUserID, newDefaultUserID

            selectedService.setParameter(PARAMETER_KEY,"python fix script")

            lChangedAvailableAccounts = False
            updatedAccounts = selectedService.getAvailableAccounts()

            validateListOnlineAccounts = []

            for onUser in range(0,len(userIDList)):
                theOutput += "... Adding UserID: %s\n" %(userIDList[onUser].getUserID())
                # actualIDNumber = onUser + 1
                for acct in userIDList[onUser].getAccounts():
                    theOutput += "...... On Account: %s (%s)\n" %(acct, acct.getOFXAccountNumber())

                    selectedService.setParameter("so_user_id_%s::%s" %(theRealm, my_getAccountKey(acct)), userIDList[onUser].getUserID())

                    if acct.getOFXAccountNumber() != "":
                        lFound = False
                        validateListOnlineAccounts.append(acct.getOFXAccountNumber())
                        for onlineAcct in updatedAccounts:
                            if onlineAcct.getAccountNumber() == acct.getOFXAccountNumber():
                                theOutput += "...Found online account: %s in .getAvailableAccounts() - skipping the add...\n" %(acct.getOFXAccountNumber())
                                # if not selectedService.supportsMsgSet(acct.getOFXAccountMsgType()):
                                #     myPrint("B", "...... supportsMsgSet(%s) failed.... forcing this on....." %(selectedService.supportsMsgSet(acct.getOFXAccountMsgType())))
                                #     selectedService.setMsgSetVersion(acct.getOFXAccountMsgType(), 1)
                                lFound = True
                        if not lFound:
                            theOutput += "...Adding account: %s to .getAvailableAccounts()\n" %(acct.getOFXAccountNumber())
                            lChangedAvailableAccounts = True
                            info = OnlineAccountInfo()
                            info.setAccountNumber(acct.getOFXAccountNumber())
                            info.setRoutingNumber(acct.getOFXBillPayBankID())
                            info.setAccountType(acct.getOFXAccountType())
                            info.setAccountMessageType(acct.getOFXAccountMsgType())
                            info.setInvestmentBrokerID(acct.getOFXBrokerID())
                            info.setIsInvestmentAccount(acct.getAccountType()==Account.AccountType.INVESTMENT)                  # noqa
                            info.setIsBankAccount(acct.getAccountType()==Account.AccountType.BANK)                              # noqa
                            info.setIsCCAccount(acct.getAccountType()==Account.AccountType.CREDIT_CARD)                         # noqa
                            # if not selectedService.supportsMsgSet(acct.getOFXAccountMsgType()):
                            #     selectedService.setMsgSetVersion(acct.getOFXAccountMsgType(), 1)
                            updatedAccounts.add(info)
                            del info
                        del lFound

                    if isMDPlusEnabledBuild() and mappingObjectClass is not None and acct.getOFXAccountNumber() != "":
                        theOutput += (".. setting bank account %s into MD2022 map for: %s\n" %(acct.getOFXAccountNumber(), acct))
                        mappingObjectClass.setMapping(acct.getOFXAccountNumber(), acct)
                        lMappingNeedsSync = True

                    elif not isMDPlusEnabledBuild() and mappingObject is not None and acct.getOFXAccountNumber() != "":
                        mapPrefix = "map." + selectedService.getTIKServiceID() + ":::"
                        theOutput += (".. manually setting bank account %s into MD2022 map for: %s\n" %(acct.getOFXAccountNumber(), acct))
                        mappingObject.setAccountParameter(None, mapPrefix + acct.getOFXAccountNumber(), acct)
                        lManualMappingNeedsSync = True

            theOutput += ("\nScanning available accounts, removing orphans......\n")
            for iSearchOnlineAccounts in reversed(range(0, len(updatedAccounts))):
                onlineAcct  = updatedAccounts[iSearchOnlineAccounts]
                if onlineAcct.getAccountNumber() not in validateListOnlineAccounts:
                    theOutput += ("... removed orphan acct: '%s' from available accounts\n" %(onlineAcct.getAccountNumber()))
                    updatedAccounts.remove(iSearchOnlineAccounts)
                    lChangedAvailableAccounts = True
            del validateListOnlineAccounts

            if lChangedAvailableAccounts:
                selectedService.setAvailableAccounts(updatedAccounts)

            theOutput += "... Saving updated OFX Profile...\n"
            selectedService.syncItem()

            if lMappingNeedsSync: mappingObjectClass.syncItem()
            if lManualMappingNeedsSync: mappingObject.syncItem()
            del lMappingNeedsSync, mappingObjectClass, lManualMappingNeedsSync, mappingObject

            ####################################################################################################################

            theOutput += "\n"

            theOutput += "accessing / updating authentication keys...:\n"
            theOutput += "--------------------------------------------\n"

            _ACCOUNT = 0
            _SERVICE = 1
            _ISBILLPAY = 2

            # theOutput += "\n>>REALMs configured:\n"
            # realmsToCheck = selectedService.getRealms()
            # if "DEFAULT" not in realmsToCheck:
            #     realmsToCheck.insert(0,"DEFAULT")

            theOutput += "Clearing authentication cache from %s\n" %(selectedService)
            selectedService.clearAuthenticationCache()

            for onUser in range(0,len(userIDList)):

                theOutput += ">> Setting up cached authentication for user %s\n" %(userIDList[onUser].getUserID())

                newAuthObj = "type=0&userid=%s&pass=%s&extra=" %(URLEncoder.encode(userIDList[onUser].getUserID()),URLEncoder.encode(userIDList[onUser].getPassword()))

                if onUser == 0:
                    authKey = "ofx:" + theRealm
                    authObj = selectedService.getCachedAuthentication(authKey)
                    theOutput += ".. Realm: %s old Cached Authentication: %s\n" %(theRealm, authObj)
                    theOutput += "   >> ** Setting new cached authentication from %s to: %s\n" %(authKey, newAuthObj)
                    selectedService.cacheAuthentication(authKey, newAuthObj)

                listAccountMDProxies = []
                for acct in userIDList[onUser].getAccounts():
                    listAccountMDProxies.append([MDAccountProxy(acct, False),selectedService,False])

                for olacct in listAccountMDProxies:
                    authKey = "ofx:" + (theRealm + "::" + olacct[_ACCOUNT].getAccountKey())
                    authObj = selectedService.getCachedAuthentication(authKey)
                    theOutput += "   ... Realm: %s Account Key: %s old Cached Authentication: %s\n" %(theRealm, olacct[_ACCOUNT].getAccountKey(),authObj)
                    theOutput += "         >> ** Setting new cached authentication from %s to: %s\n" %(authKey, newAuthObj)
                    selectedService.cacheAuthentication(authKey, newAuthObj)

            ####################################################################################################################
            MD_REF.getCurrentAccount().getBook().getLocalStorage().save()  # Flush settings to disk before changes
            ####################################################################################################################

            theOutput += "\n"
            theOutput += "FINISHED UPDATES\n"
            theOutput += "----------------\n"
            theOutput += "\n"

            ####################################################################################################################

            last_date_options = ["NO (FINISHED)", "YES - VIEW LAST TXN DOWNLOAD DATES"]
            theResult = JOptionPane.showOptionDialog(ofx_populate_multiple_userids_frame_,
                                                     "SUCCESS! >> Now would you like to view your last txn download dates?",
                                                     "LAST DOWNLOAD DATES",
                                                     JOptionPane.YES_NO_OPTION,
                                                     JOptionPane.QUESTION_MESSAGE,
                                                     getMDIcon(None),
                                                     last_date_options,
                                                     last_date_options[0])
            if theResult > 0:

                def MyGetDownloadedTxns(theAcct):       # Use my version to prevent creation of default record(s)

                    myID = theAcct.getParameter("id", None)
                    defaultTxnsListID = myID + ".oltxns"

                    if myID is not None and myID != "":
                        defaultTxnList = MD_REF.getCurrentAccount().getBook().getItemForID(defaultTxnsListID)   # type: SyncableItem
                        if defaultTxnList is not None and isinstance(defaultTxnList, OnlineTxnList):
                            return defaultTxnList

                    txnsListID = theAcct.getParameter("ol_txns_list_id", None)
                    if txnsListID is None or txnsListID == "":
                        if myID is not None and myID != "":
                            txnsListID = defaultTxnsListID

                    if txnsListID is not None and txnsListID != "":
                        txnsObj = MD_REF.getCurrentAccount().getBook().getItemForID(txnsListID)              # type: SyncableItem
                        if (txnsObj is not None and isinstance(txnsObj, OnlineTxnList)):
                            return txnsObj

                    return None

                accountsDL = AccountUtil.allMatchesForSearch(MD_REF.getCurrentAccount().getBook(), MyAcctFilter(3))
                accountsDL = sorted(accountsDL, key=lambda sort_x: (sort_x.getAccountType(), sort_x.getFullAccountName().upper()))

                outputDates = "\nBANK OFX: LAST DOWNLOADED TRANSACTION DATE(s)\n"\
                              "--------------------------------------------\n\n"\
                              "** Please check for recent dates. If your account is set to zero - you will likely get up to six months+ of data, maybe even more, or possibly problems (from too many transactions)!\n\n"

                if isMulti_OFXLastTxnUpdate_build():
                    outputDates += "NOTE: Multiple OFXLastTxnUpdate dates (i.e. per OFX/MD+ connection) are possible with this build...\n\n"

                for acct in accountsDL:
                    theOnlineTxnRecord = MyGetDownloadedTxns(acct)     # Use my version to prevent creation of default record(s)
                    if theOnlineTxnRecord is None:
                        humanReadableOFXLastTxnDate = "Never downloaded = 'Download all available dates'"
                        outputDates += "%s %s %s\n" %(pad(repr(acct.getAccountType()),12),
                                                      pad(acct.getFullAccountName(),40),
                                                      humanReadableOFXLastTxnDate)
                    else:
                        #  Since build 4074, .getOFXLastTxnUpdate() can be multi connection... But prior is single (all with same key)
                        for k in theOnlineTxnRecord.getParameterKeys():
                            if not k.startswith(GlobalVars.Strings.OFX_LAST_TXN_UPDATE): continue
                            # theCurrentDate = theOnlineTxnRecord.getOFXLastTxnUpdate()
                            theCurrentDate = theOnlineTxnRecord.getLongParameter(k, 0)

                            if theCurrentDate != 0:
                                humanReadableOFXLastTxnDate = get_time_stamp_as_nice_text(theCurrentDate, lUseHHMMSS=False)
                            else:
                                if isMDPlusEnabledBuild():
                                    humanReadableOFXLastTxnDate = "IS SET TO ZERO (MD will prompt for start date)"
                                else:
                                    humanReadableOFXLastTxnDate = "IS SET TO ZERO = 'Download all available dates'"

                            outputDates += "%s %s %s %s\n" %(pad(repr(acct.getAccountType()),12),
                                                             pad(acct.getFullAccountName(),40),
                                                             humanReadableOFXLastTxnDate,
                                                             k[len(GlobalVars.Strings.OFX_LAST_TXN_UPDATE):])

                outputDates += "\n<END>"
                jif = QuickJFrame("LAST DOWNLOAD DATES", outputDates, copyToClipboard=True, lWrapText=False,lAutoSize=True).show_the_frame()
                myPopupInformationBox(jif, "REVIEW OUTPUT. Use Toolbox first if you need to change any last download txn dates.....", theMessageType=JOptionPane.INFORMATION_MESSAGE)

            theOutput += "SUCCESS!\n"
            theOutput += "\n<END>\n"

            myPrint("B", "@@@ %s: Script successfully completed all updates (review output log on screen) @@@", myModuleID.upper())

            jif2 = QuickJFrame(myModuleID.upper(),theOutput,copyToClipboard=True,lWrapText=False,lJumpToEnd=True).show_the_frame()
            myPopupInformationBox(jif2, "SUCCESS. REVIEW OUTPUT (and console)", theMessageType=JOptionPane.WARNING_MESSAGE)

        doMain()

    except QuickAbortThisScriptException:
        myPrint("DB", "Caught Exception: QuickAbortThisScriptException... Doing nothing...")

    except:
        theOutput += dump_sys_error_to_md_console_and_errorlog(True)
        jif3 = QuickJFrame(myModuleID.upper(), theOutput,copyToClipboard=True, lWrapText=False, lJumpToEnd=True).show_the_frame()
        myPopupInformationBox(jif3, "ERROR. SCRIPT CRASHED - REVIEW OUTPUT (and console)", theMessageType=JOptionPane.ERROR_MESSAGE)
        del theOutput, jif3

    cleanup_actions()

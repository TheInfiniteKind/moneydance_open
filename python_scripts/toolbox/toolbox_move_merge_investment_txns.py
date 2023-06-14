#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# toolbox_move_merge_investment_txns.py build: 1008 - May 2023 - Stuart Beesley StuWareSoftSystems

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
# Called by the Toolbox extension

# build: 1000 - Initial Release.
# build: 1001 - Tweaks
# build: 1002 - Tweaked to cope with Search and Advanced Find windows...
# build: 1003 - FileDialog() (refer: java.desktop/sun/lwawt/macosx/CFileDialog.java) seems to no longer use "com.apple.macos.use-file-dialog-packages" in favor of "apple.awt.use-file-dialog-packages" since Monterrey...
# build: 1003 - Common code
# build: 1004 - Added bootstrap to execute compiled version of extension (faster to load)....
# build: 1005 - Cope with MD2023 new Balance Adjustment and changed meaning of Start Balance (i.e. block when adj != 0)
# build: 1005 - MD2023 fixes to common code...
# build: 1006 - Common code tweaks
# build: 1007 - Fix missing reference to CurrencyTable class
# build: 1008 - Tweak pre-selected txns detection routing for Bank Register 'issue'. Also copy latest detect_non_hier_sec_acct_or_orphan_txns()

# Allows the user to select investment transactions and then move them between accounts:
# Can be called from the Extensions Menu (with/without txns selected); or from Toolbox menu

# CUSTOMIZE AND COPY THIS ##############################################################################################
# CUSTOMIZE AND COPY THIS ##############################################################################################
# CUSTOMIZE AND COPY THIS ##############################################################################################

# SET THESE LINES
myModuleID = u"toolbox_move_merge_investment_txns"
version_build = "1008"
MIN_BUILD_REQD = 1904                                               # Check for builds less than 1904 / version < 2019.4
_I_CAN_RUN_AS_MONEYBOT_SCRIPT = False

if u"debug" in globals():
    global debug
else:
    debug = False
global toolbox_move_merge_investment_txns_frame_
# SET LINES ABOVE ^^^^

# COPY >> START
import __builtin__ as builtins

def checkObjectInNameSpace(objectName):
    """Checks globals() and builtins for the existence of the object name (used for StuWareSoftSystems' bootstrap)"""
    if objectName is None or not isinstance(objectName, basestring) or objectName == u"": return False
    if objectName in globals(): return True
    return objectName in dir(builtins)


global moneydance, moneydance_ui, moneydance_extension_loader, moneydance_extension_parameter
MD_REF = moneydance             # Make my own copy of reference as MD removes it once main thread ends.. Don't use/hold on to _data variable
MD_REF_UI = moneydance_ui       # Necessary as calls to .getUI() will try to load UI if None - we don't want this....
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
        self.myJFrameVersion = 3
        self.isActiveInMoneydance = False
        self.isRunTimeExtension = False
        self.MoneydanceAppListener = None
        self.HomePageViewObj = None

    def dispose(self):
        # This removes all content as VAqua retains the JFrame reference in memory...
        if self.disposing: return
        try:
            self.disposing = True
            self.removeAll()
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
            and (isinstance(toolbox_move_merge_investment_txns_frame_, MyJFrame)                 # EDIT THIS
                 or type(toolbox_move_merge_investment_txns_frame_).__name__ == u"MyCOAWindow")  # EDIT THIS
            and toolbox_move_merge_investment_txns_frame_.isActiveInMoneydance):                 # EDIT THIS
        frameToResurrect = toolbox_move_merge_investment_txns_frame_                             # EDIT THIS
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

    # NOTE: As of MD2022(4040) python.getSystemState().setdefaultencoding("utf8") is called on the python interpreter at launch...
    import sys
    reload(sys)  # Dirty hack to eliminate UTF-8 coding errors
    sys.setdefaultencoding('utf8')  # Dirty hack to eliminate UTF-8 coding errors. Without this str() fails on unicode strings...

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
    from com.infinitekind.moneydance.model import AccountUtil, AcctFilter, CurrencyType, CurrencyUtil, CurrencyTable
    from com.infinitekind.moneydance.model import Account, Reminder, ParentTxn, SplitTxn, TxnSearch, InvestUtil, TxnUtil

    from com.moneydance.apps.md.controller import AccountBookWrapper
    from com.infinitekind.moneydance.model import AccountBook

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

    # END SET THESE VARIABLES FOR ALL SCRIPTS ##########################################################################

    # >>> THIS SCRIPT'S IMPORTS ########################################################################################
    from javax.swing import JSplitPane
    from java.awt import CardLayout
    from com.moneydance.apps.md.view.gui.acctpanels import BankAcctPanel
    from com.moneydance.apps.md.view.gui import MainFrame, AccountDetailPanel, InvestAccountDetailPanel, LoanAccountDetailPanel, LiabilityAccountInfoPanel, TxnSearchWindow
    from com.moneydance.apps.md.view.gui.txnreg import TxnRegister, TxnRegisterList
    from com.infinitekind.moneydance.model import InvestFields, InvestTxnType, TxnSet                                   # noqa
    from javax.swing import DefaultComboBoxModel
    from java.awt.event import ItemListener, ItemEvent, HierarchyListener                                               # noqa
    from java.lang import Long                                                                                          # noqa
    from com.moneydance.awt import JCurrencyField
    # >>> END THIS SCRIPT'S IMPORTS ####################################################################################

    # >>> THIS SCRIPT'S GLOBALS ########################################################################################
    GlobalVars.extn_param_shownHelpFile_MIT = None
    GlobalVars.Strings.EXTENSION_QL_ID = "securityquoteload"
    GlobalVars.Strings.EXTENSION_QER_ID = "yahooqt"

    GlobalVars.Strings.MD_KEY_BALANCE_ADJUSTMENT = "baladj"
    GlobalVars.MD_KOTLIN_COMPILED_BUILD = 5000                                  # 2023.0 - Introduced Balance Adjustment
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
Toolbox:                                View Moneydance settings, diagnostics, fix issues, change settings and much more
                                        + Extension Menus: Total selected transactions & Move Investment Transactions
Custom Balances (net_account_balances): Summary Page (HomePage) widget. Display the total of selected Account Balances

Extension (.mxt) and Script (.py) Versions available:
Extract Data:                           Extract various data to screen and/or csv.. Consolidation of:
- stockglance2020                       View summary of Securities/Stocks on screen, total by Security, export to csv 
- extract_reminders_csv                 View reminders on screen, edit if required, extract all to csv
- extract_currency_history_csv          Extract currency history to csv
- extract_investment_transactions_csv   Extract investment transactions to csv
- extract_account_registers_csv         Extract Account Register(s) to csv along with any attachments

List Future Reminders:                  View future reminders on screen. Allows you to set the days to look forward
Accounts Categories Mega Search Window: Combines MD Menu> Tools>Accounts/Categories and adds Quick Search box/capability
Security Performance Graph:             Graphs selected securities, calculating relative price performance as percentage

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
            printString = printString.strip()

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
                    System.err.write(GlobalVars.thisScriptName + ":" + dt + ": "+"Error writing to console")
                    dump_sys_error_to_md_console_and_errorlog()

        except IllegalArgumentException:
            myPrint("B","ERROR - Probably on a multi-byte character..... Will ignore as code should just continue (PLEASE REPORT TO DEVELOPER).....")
            dump_sys_error_to_md_console_and_errorlog()

        return

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
            # if Platform.isOSX() and int(float(MD_REF.getBuild())) >= 3039: self.lAlertLevel = 0    # Colors don't work on Mac since VAQua
            if isMDThemeDark() or isMacDarkModeDetected(): self.lAlertLevel = 0

        def updateMessages(self, newTitle=None, newStatus=None, newMessage=None, lPack=True):
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
            return

        def result(self):
            return self.lResult[0]

        def go(self):
            myPrint("DB", "In MyPopUpDialogBox.", inspect.currentframe().f_code.co_name, "()")
            myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

            class MyPopUpDialogBoxRunnable(Runnable):
                def __init__(self, callingClass):
                    self.callingClass = callingClass

                def run(self):                                                                                                      # noqa

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
                        # self.callingClass._popup_d.setPreferredSize(Dimension(maxDialogWidth,maxDialogHeight))
                    else:
                        maxDialogWidth = min(screenSize.width-20, max(GetFirstMainFrame.DEFAULT_MAX_WIDTH, int(round(GetFirstMainFrame.getSize().width *.9,0))))
                        maxDialogHeight = min(screenSize.height-40, max(GetFirstMainFrame.DEFAULT_MAX_WIDTH, int(round(GetFirstMainFrame.getSize().height *.9,0))))
                        maxDimension = Dimension(maxDialogWidth,maxDialogHeight)
                        # self.callingClass._popup_d.setPreferredSize(Dimension(maxDialogWidth,maxDialogHeight))

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
                myPrint("DB",".. Not running within the EDT so calling via MyPopUpDialogBoxRunnable()...")
                SwingUtilities.invokeAndWait(MyPopUpDialogBoxRunnable(self))
            else:
                myPrint("DB",".. Already within the EDT so calling naked...")
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

            _label2 = JLabel(pad("StuWareSoftSystems (2020-2022)", 800))
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

    def isMDPlusEnabledBuild(): return (float(MD_REF.getBuild()) >= GlobalVars.MD_MDPLUS_BUILD)                         # 2022.0

    def isAlertControllerEnabledBuild(): return (float(MD_REF.getBuild()) >= GlobalVars.MD_ALERTCONTROLLER_BUILD)       # 2022.3

    # END COMMON DEFINITIONS ###############################################################################################
    # END COMMON DEFINITIONS ###############################################################################################
    # END COMMON DEFINITIONS ###############################################################################################
    # COPY >> END

    # >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
    # >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
    # >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
    def load_StuWareSoftSystems_parameters_into_memory():
        myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()" )
        myPrint("DB", "Loading variables into memory...")

        if GlobalVars.parametersLoadedFromFile is None: GlobalVars.parametersLoadedFromFile = {}

        # >>> THESE ARE THIS SCRIPT's PARAMETERS TO LOAD
        if GlobalVars.parametersLoadedFromFile.get("extn_param_shownHelpFile_MIT") is not None:
            GlobalVars.extn_param_shownHelpFile_MIT = GlobalVars.parametersLoadedFromFile.get("extn_param_shownHelpFile_MIT")

        myPrint("DB","parametersLoadedFromFile{} set into memory (as variables).....:", GlobalVars.parametersLoadedFromFile)
        return

    # >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
    def dump_StuWareSoftSystems_parameters_from_memory():
        # NOTE: Parameters were loaded earlier on... Preserve existing, and update any used ones...
        # (i.e. other StuWareSoftSystems programs might be sharing the same file)

        if GlobalVars.parametersLoadedFromFile is None: GlobalVars.parametersLoadedFromFile = {}

        # >>> THESE ARE THIS SCRIPT's PARAMETERS TO SAVE
        GlobalVars.parametersLoadedFromFile["extn_param_shownHelpFile_MIT"] = GlobalVars.extn_param_shownHelpFile_MIT

        myPrint("DB","variables dumped from memory back into parametersLoadedFromFile{}.....:", GlobalVars.parametersLoadedFromFile)
        return

    get_StuWareSoftSystems_parameters_from_file(myFile="%s_extension.dict" %(myModuleID))

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
            if GlobalVars.countTxnsMoved > 0:
                MD_REF.getUI().setStatus(">> StuWareSoftSystems - %s >> %s Transactions moved..." %(GlobalVars.thisScriptName, GlobalVars.countTxnsMoved),0)
            else:
                MD_REF.getUI().setStatus(">> StuWareSoftSystems - thanks for using >> %s......." %(GlobalVars.thisScriptName),0)
        except:
            pass  # If this fails, then MD is probably shutting down.......

        if not GlobalVars.i_am_an_extension_so_run_headless: print(scriptExit)

        cleanup_references()

    # .moneydance_invoke_called() is used via the _invoke.py script as defined in script_info.dict. Not used for runtime extensions
    def moneydance_invoke_called(theCommand):
        # ... modify as required to handle .showURL() events sent to this extension/script...
        myPrint("B","INVOKE - Received extension command: '%s'" %(theCommand))

    GlobalVars.defaultPrintLandscape = False
    # END ALL CODE COPY HERE ###############################################################################################
    # END ALL CODE COPY HERE ###############################################################################################
    # END ALL CODE COPY HERE ###############################################################################################

    def isKotlinCompiledBuild(): return (float(MD_REF.getBuild()) >= GlobalVars.MD_KOTLIN_COMPILED_BUILD)                                           # 2023.0(5000)

    # moved out of common code - these two methods are now slightly different from Toolbox main code...
    def doesUserAcceptDisclaimer(theParent, theTitle, disclaimerQuestion):
        disclaimer = myPopupAskForInput(theParent,
                                        theTitle,
                                        "DISCLAIMER:",
                                        "%s Type 'IAGREE' to continue.." %(disclaimerQuestion),
                                        "NO",
                                        False,
                                        JOptionPane.ERROR_MESSAGE)
        agreed = (disclaimer == "IAGREE")
        if agreed:
            myPrint("B", "%s: User AGREED to disclaimer question: '%s'" %(theTitle, disclaimerQuestion))
        else:
            myPrint("B", "%s: User DECLINED disclaimer question: '%s' - no action/changes made" %(theTitle, disclaimerQuestion))
        return agreed

    def confirm_backup_confirm_disclaimer(theFrame, theTitleToDisplay, theAction):

        if not myPopupAskQuestion(theFrame,
                                  theTitle=theTitleToDisplay,
                                  theQuestion=theAction,
                                  theOptionType=JOptionPane.YES_NO_OPTION,
                                  theMessageType=JOptionPane.ERROR_MESSAGE):

            txt = "'%s' User did not say yes to '%s' - no changes made" %(theTitleToDisplay, theAction)
            setDisplayStatus(txt, "R")
            myPrint("B", txt)
            myPopupInformationBox(theFrame,"User did not agree to proceed - no changes made...","NO UPDATE",JOptionPane.ERROR_MESSAGE)
            return False

        if not myPopupAskBackup(theFrame, "Would you like to perform a backup before %s" %(theTitleToDisplay)):
            txt = "'%s' - User chose to exit without the fix/update...."%(theTitleToDisplay)
            setDisplayStatus(txt, "R")
            myPrint("B","'%s' User aborted at the backup prompt to '%s' - no changes made" %(theTitleToDisplay, theAction))
            myPopupInformationBox(theFrame,"User aborted at the backup prompt - no changes made...","DISCLAIMER",JOptionPane.ERROR_MESSAGE)
            return False

        if not doesUserAcceptDisclaimer(theFrame, theTitleToDisplay, theAction):
            setDisplayStatus("'%s' - User declined the disclaimer - no changes made...." %(theTitleToDisplay), "R")
            myPrint("B","'%s' User did not say accept Disclaimer to '%s' - no changes made" %(theTitleToDisplay, theAction))
            myPopupInformationBox(theFrame,"User did not accept Disclaimer - no changes made...","DISCLAIMER",JOptionPane.ERROR_MESSAGE)
            return False

        myPrint("B","'%s' - User has been offered opportunity to create a backup and they accepted the DISCLAIMER on Action: %s - PROCEEDING" %(theTitleToDisplay, theAction))
        return True


    MD_REF.getUI().setStatus(">> StuWareSoftSystems - %s launching......." %(GlobalVars.thisScriptName),0)

    def isQER_running(): return find_feature_module(GlobalVars.Strings.EXTENSION_QER_ID)

    def isQuoteLoader_running():
        # type: () -> int
        """Returns None if not detected/loaded, 0=Detected and NOT busy, 1=Detected but needs manual checks, 2=Detected and is BUSY, 3=Detected, but reflection failed"""

        QL_ID_MIN_VER = 3047        # Mike Bray added special variables for Toolbox to check in QL build 3047

        QL_NOTFOUND = None; QL_NOTBUSY = 0; QL_TOOOLD = 1; QL_BUSY = 2; QL_ERROR = 3                                    # noqa

        foundQLfm = find_feature_module(GlobalVars.Strings.EXTENSION_QL_ID)
        if foundQLfm is None:
            myPrint("DB","QL NOT detected...")
            return QL_NOTFOUND

        if foundQLfm.getBuild() < QL_ID_MIN_VER:                                                                                        # noqa
            myPrint("DB","QL(%s) detected... (but too old for agreed reflection checks) User to check manually" %(foundQLfm.getBuild()))  # noqa
            return QL_TOOOLD

        try:
            myPrint("DB","Reflecting... Detecting QuoteLoader.....:")
            ql_isGUIOpen = getFieldByReflection(foundQLfm, "isGUIOpen")
            ql_isUpdating = getFieldByReflection(foundQLfm, "isUpdating")
            ql_isQuotesRunning = getFieldByReflection(foundQLfm, "isQuotesRunning")

            myPrint("DB","...QL isGUIOpen:       %s" %(ql_isGUIOpen))
            myPrint("DB","...QL isUpdating:      %s" %(ql_isUpdating))
            myPrint("DB","...QL isQuotesRunning: %s" %(ql_isQuotesRunning))

            if ql_isGUIOpen or ql_isUpdating or ql_isQuotesRunning:
                myPrint("DB",">> Detected QL appears to be BUSY...")
                return QL_BUSY

            myPrint("DB",">> QL was detected, but appears NOT busy")

        except:
            myPrint("DB","@@ QL detected but reflection check failed! (please contact Toolbox author)")
            dump_sys_error_to_md_console_and_errorlog()
            return QL_ERROR

        return QL_NOTBUSY

    def perform_qer_quote_loader_check(_frame, _txt, lDialogs=True):
        # type: (JFrame, str, bool) -> int
        """Checks for QER or QL extensions running, pops up a message if needed asking user to check. Response of True = SAFE"""

        resultQER = isQER_running()

        QL_NOTFOUND = None; QL_NOTBUSY = 0; QL_TOOOLD = 1; QL_BUSY = 2; QL_ERROR = 3                                    # noqa

        # Returns None if not detected/loaded, 0=Detected and NOT busy, 1=Detected but needs manual checks, 2=Detected and is BUSY, 3=Detected, but reflection failed"""
        resultQL = isQuoteLoader_running()

        lSafeToProceed = True
        if not resultQER and not resultQL:
            txt = "Q&ER / QuoteLoader are not detected/running - proceeding...."
            setDisplayStatus(txt, "B")
            return lSafeToProceed

        lSafeToProceed = False
        if not lDialogs: return lSafeToProceed

        QER_text = "Q&ER detected. " if (resultQER) else ""

        QL_text = "QL detected" if (resultQL) else ""
        if resultQL == QL_BUSY: QL_text += " and appears BUSY. "
        else: QL_text += ". "

        if not resultQER and resultQL == QL_BUSY:
            txt = "Sorry: QL appears busy (try again later)"
            setDisplayStatus(txt, "R")
            myPopupInformationBox(_frame, txt, "Quote Loader detection", theMessageType=JOptionPane.WARNING_MESSAGE)
            return lSafeToProceed

        saveYES = UIManager.get("OptionPane.yesButtonText"); saveNO = UIManager.get("OptionPane.noButtonText")
        UIManager.put("OptionPane.yesButtonText", "OK - CONTINUE"); UIManager.put("OptionPane.noButtonText", "STOP - I NEED TO CHECK")
        ask = myPopupAskQuestion(_frame,"Q&ER / QUOTE LOADER DETECTION","%s%s Confirm that they're not updating before running '%s'?" %(QER_text, QL_text, _txt))
        UIManager.put("OptionPane.yesButtonText", saveYES); UIManager.put("OptionPane.noButtonText", saveNO)

        if not ask:
            txt = "Q&ER / QuoteLoader loaded (or busy). Please verify they're not updating before running '%s' - no changes made" %(_txt)
            setDisplayStatus(txt, "R")
            return lSafeToProceed

        txt = "User verified that Q&ER / QuoteLoader are not running - proceeding...."
        setDisplayStatus(txt, "B")

        lSafeToProceed = True
        return lSafeToProceed

    ####################################################################################################################
    try:

        if not SwingUtilities.isEventDispatchThread():
            myPrint("B","@@@ ERROR: This extension can only be run on the Swing EDT (contact the author)!")
            raise QuickAbortThisScriptException

        lDetectedBuddyRunning = False
        for checkFr in [u"toolbox", u"toolbox_move_merge_investment_txns", u"toolbox_total_selected_transactions", u"toolbox_zap_mdplus_ofx_default_memo_fields"]:
            if getMyJFrame(checkFr) is not None:
                lDetectedBuddyRunning = True

        class MainAppRunnable(Runnable):
            def __init__(self): pass

            def run(self):                                                                                                  # noqa
                global toolbox_move_merge_investment_txns_frame_    # global as defined here

                myPrint("DB", "In MainAppRunnable()", inspect.currentframe().f_code.co_name, "()")
                myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

                toolbox_move_merge_investment_txns_frame_ = MyJFrame()
                toolbox_move_merge_investment_txns_frame_.setName(u"%s_main" %(myModuleID))
                if (not Platform.isMac()):
                    MD_REF.getUI().getImages()
                    toolbox_move_merge_investment_txns_frame_.setIconImage(MDImages.getImage(MD_REF.getSourceInformation().getIconResource()))
                toolbox_move_merge_investment_txns_frame_.setVisible(False)
                toolbox_move_merge_investment_txns_frame_.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE)

                myPrint("DB","Main JFrame %s for application created.." %(toolbox_move_merge_investment_txns_frame_.getName()))

        if not SwingUtilities.isEventDispatchThread():
            myPrint("DB",".. Main App Not running within the EDT so calling via MainAppRunnable()...")
            SwingUtilities.invokeAndWait(MainAppRunnable())
        else:
            myPrint("DB",".. Main App Already within the EDT so calling naked...")
            MainAppRunnable().run()

        lRunningFromToolboxOverride = False

        lRunningFromToolbox = False
        if u"toolbox_script_runner" in globals():
            global toolbox_script_runner
            myPrint("B","Toolbox script runner detected: %s (build: %s)" %(toolbox_script_runner, version_build))
            lRunningFromToolbox = True
        elif lDetectedBuddyRunning:
            # This (hopefully) means it's been called from the extensions menu as a 'buddy' extension to Toolbox. Both running will overwrite common variables
            msg = "Sorry. Only one of the Toolbox Extension menu scripts can run at once.. Shutting all down. Please try again"
            myPopupInformationBox(toolbox_move_merge_investment_txns_frame_, msg, "ALERT: Toolbox is running", JOptionPane.WARNING_MESSAGE)
            myPrint("B", msg)
            destroyOldFrames(u"toolbox")
            raise QuickAbortThisScriptException

        MD_decimal = MD_REF.getPreferences().getDecimalChar()
        MD_comma = "," if (MD_decimal == ".") else "."
        currencyTable = MD_REF.getCurrentAccountBook().getCurrencies()

        def isPreviewBuild():
            if MD_EXTENSION_LOADER is not None:
                try:
                    stream = MD_EXTENSION_LOADER.getResourceAsStream("/_PREVIEW_BUILD_")
                    if stream is not None:
                        myPrint("B", "@@ PREVIEW BUILD (%s) DETECTED @@" %(version_build))
                        stream.close()
                        return True
                except: pass
            return False

        GlobalVars.countTxnsMoved = 0
        GlobalVars.selectedInvestmentTransactionsList = []
        GlobalVars.theMDFrame = None
        GlobalVars.lCopyAllToClipBoard_TB = lRunningFromToolbox
        GlobalVars.helpFileData = None

        if not lRunningFromToolbox:

            def hunt_component(swingComponent, targetComponent):

                result = None
                comps = swingComponent.getComponents()

                for _c in comps:
                    if isinstance(_c,targetComponent):
                        return _c
                    result = hunt_component(_c, targetComponent)
                    if result:
                        return result

                return result

            def huntRegister(startingPoint):

                for panel in startingPoint.getComponents():

                    myPrint("DB", "............", panel)
                    for pnlComp in panel.getComponents():

                        if not isinstance(pnlComp, TxnRegisterList): continue

                        myPrint("DB", "...............", type(pnlComp))

                        p_regObject = getFieldByReflection(pnlComp, "reg")
                        if isinstance(p_regObject, TxnRegister): pass

                        myPrint("DB", "****** ", (p_regObject))

                        if p_regObject.isEditingTxn():
                            myPrint("DB", " Skipping as Txn is being edited....")
                            continue

                        myPrint("DB", "Found %s txns" %(len(p_regObject.getSelectedTxns())))
                        GlobalVars.theMDFrame = SwingUtilities.getWindowAncestor(pnlComp)
                        analyseTxns(p_regObject.getSelectedTxns(), GlobalVars.theMDFrame)

                        del p_regObject

                        break     # Seems to appear twice, so skip the second one.....


            def analyseTxns(listTxns, frame):

                iCountTxns = 0

                try:
                    if frame.getSelectedAccount() is None or frame.getSelectedAccount() == MD_REF.getCurrentAccountBook().getRootAccount():
                        myPrint("B","ALERT: Trying to run within [Advanced] Search window >> IGNORING SELECTED TRANSACTIONS")
                        return
                except:
                    myPrint("B","ERROR: Trying to call .getSelectedAccount() on:", frame)
                    dump_sys_error_to_md_console_and_errorlog()

                if listTxns:

                    account = None
                    _i = 1

                    for txn in listTxns:
                        iCountTxns += 1
                        myPrint("DB","--- Txn: %s ---" %(_i)); _i += 1
                        myPrint("DB", " Account: %s isParent: %s" %(txn.getAccount(), isinstance(txn,ParentTxn)))

                        if not account:
                            account = txn.getAccount()
                        elif account != txn.getAccount():
                            raise Exception("LOGIC ERROR: Found different accounts within Txns?!")

                        # noinspection PyUnresolvedReferences
                        if account.getAccountType() != Account.AccountType.INVESTMENT:
                            myPrint("DB","Found non Investment account, so will just exit")
                            GlobalVars.selectedInvestmentTransactionsList = []
                            return

                        GlobalVars.selectedInvestmentTransactionsList.append(txn)

                return

            myPrint("DB","Scanning for selected register transactions...:")
            myPrint("DB", "Found Main Application Windows: %s" %(MD_REF.getUI().getMainFrameCount()))
            myPrint("DB", "First Application Window:       %s" %(MD_REF.getUI().getFirstMainFrame().getTitle()))
            myPrint("DB", "Most Active Account Panel:      %s" %(MD_REF.getUI().getMostActiveAccountPanel()))

            foundTxnRegister = None
            foundJSplitPane = None

            myPrint("DB", "Searching Secondary Windows....:")

            for secondary_window in MD_REF.getUI().getSecondaryWindows():
                if not isinstance(secondary_window,
                                  (MainFrame,
                                   BankAcctPanel,
                                   AccountDetailPanel,
                                   InvestAccountDetailPanel,
                                   LoanAccountDetailPanel,
                                   LiabilityAccountInfoPanel,
                                   TxnSearchWindow)):

                    continue

                if not secondary_window.isFocused():                                                                            # noqa
                    myPrint("DB", "Skipping Non-Focused Secondary Window: '%s'" %(secondary_window.getTitle()))                 # noqa
                    continue
                else:
                    myPrint("DB", "Secondary Window: '%s' - isFocused: %s, isVisible: %s, hasFocus: %s"
                            %(secondary_window.getTitle(), secondary_window.isFocused(), secondary_window.isVisible(), secondary_window.hasFocus()))    # noqa

                if isinstance(secondary_window, TxnSearchWindow):
                    myPrint("DB","Special handling for TxnSearchWindow....")

                    account_panel_component = None
                    for account_panel_component in secondary_window.getComponents():                                    # noqa
                        myPrint("DB", ".. hunting for TxnRegister (within Search Window)...")
                        foundTxnRegister = hunt_component(account_panel_component, TxnRegister)

                else:
                    try:
                        accountPanel = secondary_window.getAccountPanel()
                        if not accountPanel: continue
                        if isinstance(accountPanel, JPanel): pass
                    except:
                        myPrint("DB", "Error calling .getAccountPanel() on %s" %(secondary_window))
                        continue

                    account_panel_component = None

                    myPrint("DB", ".. hunting for TxnRegister...")

                    if isinstance(accountPanel.getLayout(), CardLayout) and isinstance(accountPanel, InvestAccountDetailPanel):

                        cPnl = getFieldByReflection(accountPanel, "contentPanel")
                        for account_panel_component in cPnl.getComponents():
                            if not isinstance(account_panel_component, JPanel) or not account_panel_component.isVisible(): continue
                            foundTxnRegister = hunt_component(account_panel_component, TxnRegister)
                            break
                    else:
                        for account_panel_component in accountPanel.getComponents():
                            foundTxnRegister = hunt_component(account_panel_component, TxnRegister)
                            if foundTxnRegister:
                                break

                if not foundTxnRegister:
                    myPrint("DB", "Failed to find TxnRegister in '%s'" %(account_panel_component))
                    continue

                myPrint("DB", ".....Found: TxnRegister: '%s'" %(foundTxnRegister))

                myPrint("DB", ".......hunting for JSplitPane...")
                foundJSplitPane = hunt_component(foundTxnRegister, JSplitPane)

                if foundJSplitPane:
                    myPrint("DB", ".........Found: JSplitScreen", foundJSplitPane)
                    huntRegister(foundJSplitPane)
                else:
                    myPrint("DB", "Failed to find JSplitPane in '%s'" %(foundTxnRegister))

            if not GlobalVars.selectedInvestmentTransactionsList:
                # msg = "No investment txns selected and/or no register in focus"
                # myPrint("DB", msg)
                # myPopupInformationBox(toolbox_move_merge_investment_txns_frame_,msg)
                # raise QuickAbortThisScriptException
                lRunningFromToolboxOverride = True
                lRunningFromToolbox = True
            else:
                GlobalVars.selectedInvestmentTransactionsList = sorted(GlobalVars.selectedInvestmentTransactionsList, key=lambda _x: (_x.getDateInt()))

        if lRunningFromToolbox or GlobalVars.selectedInvestmentTransactionsList:

            # Copied from Toolbox main code....
            def detect_non_hier_sec_acct_or_orphan_txns(startupCheck=False):
                if MD_REF.getCurrentAccountBook() is None: return 0
                txnSet = MD_REF.getCurrentAccountBook().getTransactionSet()
                fields = InvestFields()
                count_the_errors = 0
                count_non_investment_account_errors = 0

                # noinspection PyUnresolvedReferences
                ATI = Account.AccountType.INVESTMENT

                startTimeMS = System.currentTimeMillis()

                for txn in txnSet:

                    if not isinstance(txn, ParentTxn): continue   # only work with parent transactions

                    acct = txn.getAccount()
                    acctType = acct.getAccountType()

                    # noinspection PyUnresolvedReferences
                    if acctType == Account.AccountType.SECURITY:
                        myPrint("B", "*** MAJOR ERROR: Txn is a Parent AND its a SECURITY ACCOUNT:")
                        myPrint("B", txn.toMultilineString())
                        count_the_errors += 1
                        continue

                    # Check(s) expanded to include all Account Types (as Security records should only be within Investment Accounts)
                    fields.setFieldStatus(txn)

                    if fields.hasSecurity and not acct.isAncestorOf(fields.security):
                        count_the_errors += 1

                        # noinspection PyUnresolvedReferences
                        if acctType != ATI:
                            count_non_investment_account_errors += 1

                        if debug or not startupCheck:
                            myPrint("B", "ERROR: Txn for Security %s found within '%s' Account %s that is cross linked to another account (or Security is orphaned)!\n"
                                         "txn:\n%s\n" %(fields.security,
                                                        ("Investment" if (acctType == ATI) else "** NON INVESTMENT(%s)" %(acctType)),
                                                        acct,
                                                        txn.toMultilineString()))
                del txnSet

                if count_the_errors:
                    myPrint("B", "ERROR: %s investment txn(s) with cross-linked securities detected" %(count_the_errors))
                    if count_non_investment_account_errors:
                        myPrint("B", ".... *** AND %s investment txn(s) with cross-linked securities detected found in NON INVESTMENT ACCOUNTS! ***" %(count_non_investment_account_errors))
                else:
                    if debug or startupCheck:
                        myPrint("B", "NOTE: No investment txn(s) with cross-linked securities were detected...")

                if debug:
                    myPrint("B", ".... check took: %s seconds..." %((System.currentTimeMillis() - startTimeMS) / 1000.0))


                return count_the_errors

            class StoreAccountSecurity():
                def __init__(self, obj):
                    self.obj = obj                                                                                       # type: Account

                def __str__(self):
                    # noinspection PyUnresolvedReferences
                    if self.obj is None or not isinstance(self.obj, Account) or self.obj.getAccountType() != Account.AccountType.SECURITY:
                        return "Invalid Account/Security Obj or None"
                    return "%s" %(self.obj.getAccountName())

                def getAccount(self):       return self.obj
                def getAccountName(self):   return self.getAccount().getAccountName()

                def __repr__(self):         return self.__str__()
                def toString(self):         return self.__str__()

            class MyAcctFilter(AcctFilter):
                def __init__(self, selectType=0): self.selectType = selectType

                def matches(self, acct):

                    # Security Accounts only
                    if self.selectType == 2:
                        # noinspection PyUnresolvedReferences
                        if acct.getAccountType() == Account.AccountType.SECURITY:
                            return True
                        return False

                    # Investment Accounts only
                    if self.selectType == 23:
                        # noinspection PyUnresolvedReferences
                        if acct.getAccountType() == Account.AccountType.INVESTMENT:
                            return True
                        return False

                    return False

            class MyJScrollPaneForJOptionPane(JScrollPane, HierarchyListener):    # Allows a scrollable/resizeable menu in JOptionPane
                def __init__(self, _component, _max_w=800, _max_h=600):
                    super(JScrollPane, self).__init__(_component)

                    self.maxWidth = _max_w
                    self.maxHeight = _max_h
                    self.borders = 90
                    self.setOpaque(False)
                    self.setViewportBorder(EmptyBorder(5, 5, 5, 5))
                    self.addHierarchyListener(self)

                def getPreferredSize(self):
                    screenSize = Toolkit.getDefaultToolkit().getScreenSize()
                    frame_width = int(round((screenSize.width - self.borders) *.9,0))
                    frame_height = int(round((screenSize.height - self.borders) *.9,0))
                    return Dimension(min(self.maxWidth, frame_width), min(self.maxHeight, frame_height))

                def hierarchyChanged(self, e):
                    if e: pass
                    dialog = SwingUtilities.getWindowAncestor(self)
                    if isinstance(dialog, Dialog):
                        if not dialog.isResizable():
                            dialog.setResizable(True)

            if MD_EXTENSION_LOADER:
                try:
                    GlobalVars.helpFileData = load_text_from_stream_file(MD_EXTENSION_LOADER.getResourceAsStream("/%s_readme.txt" %(myModuleID)))
                    myPrint("DB","Contents loaded from /%s_readme.txt" %(myModuleID))
                except:
                    myPrint("B","@@ Error loading contents from /%s_readme.txt" %(myModuleID))

            def move_merge_investment_txns():

                myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")
                if MD_REF.getCurrentAccount().getBook() is None: return

                _THIS_METHOD_NAME = "Move/Merge Investment Accounts"

                if lRunningFromToolbox and not lRunningFromToolboxOverride:
                    selectHomeScreen()      # Stops the LOT Control box popping up.....

                if not GlobalVars.extn_param_shownHelpFile_MIT:
                    QuickJFrame("%s: Help / guide (FIRST EXECUTION OF EXTENSION)" %(myModuleID), GlobalVars.helpFileData, lWrapText=False, screenLocation=Point(10,10),lAutoSize=True).show_the_frame()
                    GlobalVars.extn_param_shownHelpFile_MIT = True
                    save_StuWareSoftSystems_parameters_to_file(myFile="%s_extension.dict" %(myModuleID))
                    return

                PARAMETER_KEY = "toolbox_txn_merge"
                PARAMETER_KEY_COST_BASIS = "cost_basis"
                PARAMETER_KEY_OLD_COST_BASIS = ".old_cost_basis"

                today = Calendar.getInstance()                                                                          # noqa

                if detect_non_hier_sec_acct_or_orphan_txns() > 0:
                    txt = "%s: ERROR - Cross-linked (or Orphaned) security txns detected.. Review Console. Run Toolbox 'FIX: Non-Hierarchical Security Acct Txns (& detect Orphans)' >> no changes made" %(_THIS_METHOD_NAME)
                    setDisplayStatus(txt, "R")
                    myPopupInformationBox(toolbox_move_merge_investment_txns_frame_, txt, theMessageType=JOptionPane.ERROR_MESSAGE)
                    return

                allInvestmentAccounts = AccountUtil.allMatchesForSearch(MD_REF.getCurrentAccount().getBook(), MyAcctFilter(23))
                toListAccount = list(allInvestmentAccounts)

                if len(allInvestmentAccounts) < 2:
                    txt = "%s: You do not have enough accounts to do this - no changes made" %(_THIS_METHOD_NAME)
                    setDisplayStatus(txt, "R")
                    myPopupInformationBox(toolbox_move_merge_investment_txns_frame_,txt, theMessageType=JOptionPane.WARNING_MESSAGE)
                    return

                if not lRunningFromToolbox:
                    allInvestmentAccounts = [GlobalVars.selectedInvestmentTransactionsList[0].getAccount()]
                    toListAccount.remove(GlobalVars.selectedInvestmentTransactionsList[0].getAccount())

                txt = "%s" %(_THIS_METHOD_NAME)

                if lRunningFromToolbox:
                    if not perform_qer_quote_loader_check(toolbox_move_merge_investment_txns_frame_, txt): return

                # # ########### FILTER OPTIONS ###################################################################################
                if lRunningFromToolbox:
                    labelMsg = JLabel("Without filters all transactions from source account will be moved/merged into target Account")
                else:
                    myPrint("B", ">> Account: '%s' >> %s txn(s) pre-selected for move/merge feature...."
                            %(GlobalVars.selectedInvestmentTransactionsList[0].getAccount(), len(GlobalVars.selectedInvestmentTransactionsList)))
                    labelMsg = JLabel("The %s txn(s) you have selected will be moved to the target account" %(len(GlobalVars.selectedInvestmentTransactionsList)))
                labelMsg.setForeground(getColorBlue())

                user_selectSourceAccount = JComboBox(allInvestmentAccounts)
                user_selectSourceAccount.setToolTipText("This is the original location/source Account for the Transactions to be moved from")
                user_selectSourceAccount.setName("SELECT_SOURCE_ACCOUNT")
                if not lRunningFromToolbox:
                    user_selectSourceAccount.setSelectedItem(GlobalVars.selectedInvestmentTransactionsList[0].getAccount())
                    user_selectSourceAccount.setEnabled(False)
                else:
                    user_selectSourceAccount.setSelectedIndex(-1)

                if not lRunningFromToolbox:
                    user_selectTargetAccount = JComboBox(toListAccount)
                else:
                    user_selectTargetAccount = JComboBox([])
                user_selectTargetAccount.setSelectedIndex(-1)

                user_selectTargetAccount.setToolTipText("This is the target/destination for the transactions to be moved into")

                user_enableSecurityFilter = JCheckBox("Enable Filter by Security?", False)
                user_enableSecurityFilter.setName("ENABLE_SECURITY_FILTER")
                user_enableSecurityFilter.setToolTipText("When enabled, allows you to filter the move for just one security")

                user_filterSecurity = JComboBox([])
                user_filterSecurity.setEnabled(False)
                user_filterSecurity.setToolTipText("Select the single Security to filter and move")

                user_enableDateRangeFilter = JCheckBox("Enable Date Range Filters?", False)
                user_enableDateRangeFilter.setName("ENABLE_DATE_RANGE_FILTER")
                user_enableDateRangeFilter.setToolTipText("When enabled, allows you to filter the transactions to move to a date range")

                user_dateFieldStart = JDateField(MD_REF.getUI())
                user_dateFieldStart.setEnabled(False)                                                                   # noqa

                user_dateFieldEnd = JDateField(MD_REF.getUI())
                user_dateFieldEnd.setEnabled(False)                                                                     # noqa
                user_dateFieldEnd.gotoToday()

                user_ignoreNegativeShareBalances = JCheckBox("Auto IGNORE where the share balance (by security) of selected txns to move is negative?", False)
                user_ignoreNegativeShareBalances.setToolTipText("Forces a move even if the selected txns total to a negative share balance (per security)")

                user_ignoreAccountLoop = JCheckBox("Auto IGNORE any account 'Loops' and Merge anyway?", False)
                user_ignoreAccountLoop.setToolTipText("Forces the move, even if a 'loop' is created (where to/from accounts are the same). FIX MANUALLY AFTERWARDS")

                user_ignoreAvgCstLotFlagDifference = JCheckBox("Auto IGNORE any differences between Avg Cst & LOT Control flags and Merge anyway?", False)
                user_ignoreAvgCstLotFlagDifference.setToolTipText("Force the move even when Lot Control and Average Cost flags are different between Securities (leaves matched lot data untouched")

                user_forceDeleteSeparatedLotRecords = JCheckBox("Auto DELETE any related LOT records on txns moved that separate matched Buy/Sell LOTs?", False)
                user_forceDeleteSeparatedLotRecords.setToolTipText("Delete LOT records where Buys/Sell txns have been matched, and would be separated. MANUALLY REMATCH LOTS AFTERWARDS")

                _WIPE_OPTIONS = ["CHECK/WARN: Validate for where Txns contain matched LOT records when the target uses Average Cost Control",
                                 "IGNORE PROBLEM(s): Copy any existing matched LOT records unchanged when target uses Average Cost Control",
                                 "WIPE: Delete any matched LOT records from txns being moved when target uses Average Cost Control"]
                _WIPE_CHECK = 0
                _WIPE_IGNORE = 1
                _WIPE_WIPE = 2

                # user_forceWipeLotRecordsWhenTargetAverageCost = JCheckBox("Auto force wipe matched LOT data from txns being moved when target using average cost control", False)
                lblWipeLots = JLabel("Select option when target uses 'average cost control' and txns being moved contain matched LOT data:")
                user_forceWipeLotRecordsWhenTargetAverageCost = JComboBox(_WIPE_OPTIONS)
                user_forceWipeLotRecordsWhenTargetAverageCost.setToolTipText("If a txn being moved has matched LOT data, but the target using average cost, then remove the LOT matching data")
                user_forceWipeLotRecordsWhenTargetAverageCost.setSelectedItem(_WIPE_OPTIONS[_WIPE_CHECK])

                user_deleteEmptySourceAccount = JCheckBox("Auto DELETE Empty Source Account (only actions if empty after processing)?", False)
                user_deleteEmptySourceAccount.setToolTipText("Delete the Source account after the move if it's empty")

                user_mergeCashBalances = JCheckBox("Auto MERGE Source Account's initial [cash] balance to Target's? (Specify amount to move below)",
                                                   False if (GlobalVars.selectedInvestmentTransactionsList) else True)
                user_mergeCashBalances.setName("MOVE_CASH_BALANCE")
                user_mergeCashBalances.setToolTipText("Move the specified amount of initial [cash] balance over to the target account")

                srcAcct = user_selectSourceAccount.getSelectedItem()      # type: Account
                if isinstance(srcAcct, Account): pass

                if srcAcct is None:
                    user_cashBalanceToMove = JCurrencyField(14, None, currencyTable, MD_decimal, MD_comma)
                else:
                    user_cashBalanceToMove = JCurrencyField(14, srcAcct.getCurrencyType(), currencyTable, MD_decimal, MD_comma)
                    user_cashBalanceToMove.setValue(srcAcct.getStartBalance())

                user_cashBalanceToMove.setEmptyIfZero(True)
                user_cashBalanceToMove.setToolTipText("Enter the amount of the source acct's initial [cash] balance to move to target account")   # noqa
                user_cashBalanceToMove.setEnabled(user_mergeCashBalances.isSelected())                                                          # noqa
                del srcAcct

                user_forceAllowResultingNegativeCashBalance = JCheckBox("Auto ALLOW Source Account's Cash balance to go negative?", False)
                user_forceAllowResultingNegativeCashBalance.setToolTipText("Allows the source acct's cash balance to go negative as a result of the move")

                user_forceTrunkSave = JCheckBox("Auto SAVE-TRUNK - Immediately flush all changes back to disk (Use when making large changes)?",
                                                False if (GlobalVars.selectedInvestmentTransactionsList) else True)
                user_forceTrunkSave.setToolTipText("A good idea for large moves. Not needed for small moves.")

                filterPanel = JPanel(GridLayout(0, 1))
                filterPanel.add(labelMsg)
                filterPanel.add(JLabel(""))
                filterPanel.add(JLabel("Select the 'from' source Investment Account"))
                filterPanel.add(user_selectSourceAccount)
                filterPanel.add(JLabel("Select the target Investment Account to move/merge txns into"))
                filterPanel.add(user_selectTargetAccount)
                filterPanel.add(JLabel(""))

                if lRunningFromToolbox:
                    filterPanel.add(JLabel("FILTER OPTIONS:"))
                    filterPanel.add(user_enableSecurityFilter)
                    filterPanel.add(JLabel("Select the Security to FILTER:"))
                    filterPanel.add(user_filterSecurity)
                    filterPanel.add(JLabel(""))
                    filterPanel.add(user_enableDateRangeFilter)
                    filterPanel.add(JLabel("FILTER Range Start Date:"))
                    filterPanel.add(user_dateFieldStart)
                    filterPanel.add(JLabel("FILTER Range End Date:"))
                    filterPanel.add(user_dateFieldEnd)
                    filterPanel.add(JLabel(""))

                filterPanel.add(JLabel("PROCESSING OPTIONS: [Leave all as default to validate the move first]"))
                filterPanel.add(user_mergeCashBalances)
                filterPanel.add(user_cashBalanceToMove)
                filterPanel.add(user_forceAllowResultingNegativeCashBalance)
                filterPanel.add(user_ignoreNegativeShareBalances)
                filterPanel.add(user_ignoreAvgCstLotFlagDifference)
                filterPanel.add(user_forceDeleteSeparatedLotRecords)
                filterPanel.add(lblWipeLots)
                filterPanel.add(user_forceWipeLotRecordsWhenTargetAverageCost)
                filterPanel.add(user_ignoreAccountLoop)
                filterPanel.add(user_deleteEmptySourceAccount)
                filterPanel.add(user_forceTrunkSave)

                class MyItemListener(ItemListener):
                    def __init__(self, selectSource, selectTarget, enableSecurityFilter, filterSecurity, enableDateRangeFilter, dateFieldStart, dateFieldEnd, forceTrunkSave, mergeCashBalances, _cashBalanceToMove, forceWipeLotRecordsWhenTargetAverageCost):
                        self.selectSource = selectSource
                        self.selectTarget = selectTarget
                        self.enableSecurityFilter = enableSecurityFilter
                        self.filterSecurity = filterSecurity
                        self.enableDateRangeFilter = enableDateRangeFilter
                        self.dateFieldStart = dateFieldStart
                        self.dateFieldEnd = dateFieldEnd
                        self.forceTrunkSave = forceTrunkSave
                        self.mergeCashBalances = mergeCashBalances
                        self.cashBalanceToMove = _cashBalanceToMove
                        self.forceWipeLotRecordsWhenTargetAverageCost = forceWipeLotRecordsWhenTargetAverageCost

                    def itemStateChanged(self, e):
                        if ((e.getSource().getName() == "SELECT_SOURCE_ACCOUNT" and e.getStateChange() == ItemEvent.SELECTED)
                                or (e.getSource().getName() == "ENABLE_SECURITY_FILTER" and e.getSource().isSelected())):
                            subAccts = []
                            if self.selectSource.getSelectedItem() is not None:
                                for sAcct in self.selectSource.getSelectedItem().getSubAccounts(): subAccts.append(StoreAccountSecurity(sAcct))
                            self.filterSecurity.setModel(DefaultComboBoxModel(subAccts))
                            self.filterSecurity.setSelectedIndex(-1)

                            if e.getSource().getName() == "SELECT_SOURCE_ACCOUNT":
                                self.cashBalanceToMove.setCurrencyType(e.getSource().getSelectedItem().getCurrencyType())
                                self.cashBalanceToMove.setValue(e.getSource().getSelectedItem().getStartBalance())

                                if lRunningFromToolbox:
                                    _toListAccount = AccountUtil.allMatchesForSearch(MD_REF.getCurrentAccount().getBook(), MyAcctFilter(23))
                                    _toListAccount.remove(e.getSource().getSelectedItem())
                                    self.selectTarget.setModel(DefaultComboBoxModel(_toListAccount))
                                    self.selectTarget.setSelectedIndex(-1)


                        if e.getSource().getName() == "ENABLE_SECURITY_FILTER":
                            self.filterSecurity.setEnabled(e.getSource().isSelected())
                            if not e.getSource().isSelected(): self.filterSecurity.setModel(DefaultComboBoxModel([]))
                            self.forceTrunkSave.setSelected(not self.enableSecurityFilter.isSelected() and not self.enableDateRangeFilter.isSelected())
                            self.mergeCashBalances.setSelected(not self.enableSecurityFilter.isSelected() and not self.enableDateRangeFilter.isSelected())

                        if e.getSource().getName() == "ENABLE_DATE_RANGE_FILTER":
                            for dateFilter in [self.dateFieldStart, self.dateFieldEnd]: dateFilter.setEnabled(e.getSource().isSelected())
                            self.forceTrunkSave.setSelected(not self.enableSecurityFilter.isSelected() and not self.enableDateRangeFilter.isSelected())
                            self.mergeCashBalances.setSelected(not self.enableSecurityFilter.isSelected() and not self.enableDateRangeFilter.isSelected())

                        if e.getSource().getName() == "MOVE_CASH_BALANCE":
                            self.cashBalanceToMove.setEnabled(e.getSource().isSelected())


                myItemListener = MyItemListener(user_selectSourceAccount,
                                                user_selectTargetAccount,
                                                user_enableSecurityFilter,
                                                user_filterSecurity,
                                                user_enableDateRangeFilter,
                                                user_dateFieldStart,
                                                user_dateFieldEnd,
                                                user_forceTrunkSave,
                                                user_mergeCashBalances,
                                                user_cashBalanceToMove,
                                                user_forceWipeLotRecordsWhenTargetAverageCost)
                user_selectSourceAccount.addItemListener(myItemListener)
                user_enableSecurityFilter.addItemListener(myItemListener)
                user_enableDateRangeFilter.addItemListener(myItemListener)
                user_mergeCashBalances.addItemListener(myItemListener)

                _options = ["Cancel", "PROCEED"]
                if GlobalVars.helpFileData: _options.append("HELP/GUIDE")

                while True:
                    jsp = MyJScrollPaneForJOptionPane(filterPanel,850, 700 if (lRunningFromToolbox) else 450)
                    userAction = JOptionPane.showOptionDialog(toolbox_move_merge_investment_txns_frame_,
                                                              jsp,
                                                              "%s: Select FILTER Options:" %(_THIS_METHOD_NAME.upper()),
                                                              JOptionPane.OK_CANCEL_OPTION,
                                                              JOptionPane.QUESTION_MESSAGE,
                                                              getMDIcon(None),
                                                              _options,
                                                              _options[0])

                    if userAction < 1:
                        txt = "%s: User did not select Move/Merge options - no changes made" %(_THIS_METHOD_NAME)
                        setDisplayStatus(txt, "B")
                        # myPopupInformationBox(toolbox_move_merge_investment_txns_frame_,txt,theMessageType=JOptionPane.WARNING_MESSAGE)
                        return

                    if userAction > 1:
                        QuickJFrame("%s: Help / guide" %(myModuleID), GlobalVars.helpFileData, lWrapText=False, screenLocation=Point(10,10),lAutoSize=True).show_the_frame()
                        return

                    if user_selectSourceAccount.getSelectedItem() is None or user_selectTargetAccount.getSelectedItem() is None:
                        txt = "%s: ERROR - Please select a source and target account" %(_THIS_METHOD_NAME)
                        myPopupInformationBox(toolbox_move_merge_investment_txns_frame_,txt,theMessageType=JOptionPane.WARNING_MESSAGE)
                        continue

                    if user_selectSourceAccount.getSelectedItem() == user_selectTargetAccount.getSelectedItem():
                        txt = "%s: ERROR - source and target account must be different" %(_THIS_METHOD_NAME)
                        myPopupInformationBox(toolbox_move_merge_investment_txns_frame_,txt,theMessageType=JOptionPane.WARNING_MESSAGE)
                        continue

                    #### New for MD2023 - Balance Adjustment handling (or rather blocking....!)
                    selAcct = user_selectSourceAccount.getSelectedItem()
                    if isinstance(selAcct, Account): pass

                    if isKotlinCompiledBuild():
                        balAdj = selAcct.getBalanceAdjustment()
                        if (balAdj != 0):
                            balAdjTxt = selAcct.getCurrencyType().formatSemiFancy(balAdj, MD_decimal)
                            txt = "%s: ERROR - Remove Source Account's Balance Adjustment (of %s) before proceeding" %(_THIS_METHOD_NAME, balAdjTxt)
                            myPopupInformationBox(toolbox_move_merge_investment_txns_frame_,txt,theMessageType=JOptionPane.WARNING_MESSAGE)
                            continue
                    else:
                        balAdj = selAcct.getLongParameter(GlobalVars.Strings.MD_KEY_BALANCE_ADJUSTMENT, 0)
                        if (balAdj != 0):
                            balAdjTxt = selAcct.getCurrencyType().formatSemiFancy(balAdj, MD_decimal)
                            txt = "%s: ERROR - Source Account has Balance Adjustment (of %s) from MD2023+ REMOVE FIRST!" %(_THIS_METHOD_NAME, balAdjTxt)
                            myPopupInformationBox(toolbox_move_merge_investment_txns_frame_,txt,theMessageType=JOptionPane.WARNING_MESSAGE)
                            continue

                    selAcct = user_selectTargetAccount.getSelectedItem()
                    if isinstance(selAcct, Account): pass

                    if isKotlinCompiledBuild():
                        balAdj = selAcct.getBalanceAdjustment()
                        if (balAdj != 0):
                            balAdjTxt = selAcct.getCurrencyType().formatSemiFancy(balAdj, MD_decimal)
                            txt = "%s: ERROR - Remove Target Account's Balance Adjustment (of %s) before proceeding" %(_THIS_METHOD_NAME, balAdjTxt)
                            myPopupInformationBox(toolbox_move_merge_investment_txns_frame_,txt,theMessageType=JOptionPane.WARNING_MESSAGE)
                            continue
                    else:
                        balAdj = selAcct.getLongParameter(GlobalVars.Strings.MD_KEY_BALANCE_ADJUSTMENT, 0)
                        if (balAdj != 0):
                            balAdjTxt = selAcct.getCurrencyType().formatSemiFancy(balAdj, MD_decimal)
                            txt = "%s: ERROR - Target Account has Balance Adjustment (of %s) from MD2023+ REMOVE FIRST!" %(_THIS_METHOD_NAME, balAdjTxt)
                            myPopupInformationBox(toolbox_move_merge_investment_txns_frame_,txt,theMessageType=JOptionPane.WARNING_MESSAGE)
                            continue
                    del selAcct, balAdj
                    ################################################################################

                    if (MD_REF.getCurrentAccountBook().getTransactionSet().getTransactionsForAccount(user_selectSourceAccount.getSelectedItem()).getSize() < 1
                            and (user_selectSourceAccount.getSelectedItem().getStartBalance() == 0 or not user_mergeCashBalances.isSelected())):    # noqa
                        txt = "%s: ERROR - Source Account has no transactions and no initial [cash] balance to move" %(_THIS_METHOD_NAME)
                        myPopupInformationBox(toolbox_move_merge_investment_txns_frame_,txt,theMessageType=JOptionPane.WARNING_MESSAGE)
                        continue

                    sCurr = user_selectSourceAccount.getSelectedItem().getCurrencyType()                                # noqa
                    tCurr = user_selectTargetAccount.getSelectedItem().getCurrencyType()                                # noqa
                    if sCurr != tCurr:
                        txt = "ERROR: Sorry the source acct's currency %s does not match target's %s" %(sCurr, tCurr)
                        myPopupInformationBox(toolbox_move_merge_investment_txns_frame_,txt,theMessageType=JOptionPane.WARNING_MESSAGE)
                        continue

                    if user_enableDateRangeFilter.isSelected() and user_dateFieldStart.getDateInt() > user_dateFieldEnd.getDateInt():
                        txt = "%s: ERROR - Invalid date range filter" %(_THIS_METHOD_NAME)
                        myPopupInformationBox(toolbox_move_merge_investment_txns_frame_, txt, theMessageType=JOptionPane.WARNING_MESSAGE)
                        continue

                    if user_enableSecurityFilter.isSelected() and user_filterSecurity.getSelectedItem() is None:
                        txt = "%s: ERROR - Security Filter with no Security found/selected" %(_THIS_METHOD_NAME)
                        myPopupInformationBox(toolbox_move_merge_investment_txns_frame_, txt, theMessageType=JOptionPane.WARNING_MESSAGE)
                        continue

                    if user_mergeCashBalances.isSelected():
                        srcAcct = user_selectSourceAccount.getSelectedItem()       # type: Account
                        if isinstance(srcAcct, Account): pass
                        moveCashAmt = user_cashBalanceToMove.getValue()

                        if moveCashAmt < 0 or moveCashAmt > srcAcct.getStartBalance():
                            txt = "%s: ERROR - Amount of initial [cash] balance to move to target is invalid, negative, or greater than amount held!" %(_THIS_METHOD_NAME)
                            myPopupInformationBox(toolbox_move_merge_investment_txns_frame_, txt, theMessageType=JOptionPane.WARNING_MESSAGE)
                            continue
                        del srcAcct, moveCashAmt

                    break

                del _options, filterPanel, toListAccount, allInvestmentAccounts, MyItemListener, sCurr, tCurr

                sourceAccount = user_selectSourceAccount.getSelectedItem()
                targetAccount = user_selectTargetAccount.getSelectedItem()

                if isinstance(sourceAccount, Account): pass
                if isinstance(targetAccount, Account): pass

                # Belt and braces - block if detected somehow.....
                balAdjS = sourceAccount.getLongParameter(GlobalVars.Strings.MD_KEY_BALANCE_ADJUSTMENT, 0)
                if balAdjS != 0:
                    raise Exception("LOGIC ERROR. Source Acct: '%s' cannot have an '%s' parameter set (value: %s)"
                                    %(sourceAccount.getAccountName(), GlobalVars.Strings.MD_KEY_BALANCE_ADJUSTMENT, balAdjS))
                balAdjT = targetAccount.getLongParameter(GlobalVars.Strings.MD_KEY_BALANCE_ADJUSTMENT, 0)
                if balAdjT != 0:
                    raise Exception("LOGIC ERROR. Target Acct: '%s' cannot have an '%s' parameter set (value: %s)"
                                    %(targetAccount.getAccountName(), GlobalVars.Strings.MD_KEY_BALANCE_ADJUSTMENT, balAdjT))
                del balAdjS, balAdjT


                lFilterSecurities = user_enableSecurityFilter.isSelected()
                filterSecurityList = [user_filterSecurity.getSelectedItem().getAccount()] if lFilterSecurities else []  # noqa

                lFilterByDate = user_enableDateRangeFilter.isSelected()
                if lFilterByDate:
                    filterDateFrom = user_dateFieldStart.getDateInt()
                    filterDateTo = user_dateFieldEnd.getDateInt()
                else:
                    filterDateFrom = filterDateTo = 0

                lSelectALLTransactionsToMerge = not GlobalVars.selectedInvestmentTransactionsList and not lFilterSecurities and not lFilterByDate

                if GlobalVars.selectedInvestmentTransactionsList or lFilterByDate:
                    lNeedsLotMatchSeparationTesting = True
                else:
                    lNeedsLotMatchSeparationTesting = False

                lAutoIgnoreNegativeShareBalances = user_ignoreNegativeShareBalances.isSelected()
                lAutoIgnoreAnyAvgCstLotFlagDifference = user_ignoreAvgCstLotFlagDifference.isSelected()
                lAutoForceDeleteSeparatedLotRecords = user_forceDeleteSeparatedLotRecords.isSelected()
                iAutoForceWipeLotRecordsWhenTargetAverageCostOption = user_forceWipeLotRecordsWhenTargetAverageCost.getSelectedIndex()
                lAutoIgnoreAccountLoops = user_ignoreAccountLoop.isSelected()
                lAutoDeleteEmptySourceAccount = user_deleteEmptySourceAccount.isSelected()
                lAutoMergeCashBalances = user_mergeCashBalances.isSelected()

                if not lAutoMergeCashBalances:
                    cashBalanceToMove = 0
                else:
                    cashBalanceToMove = user_cashBalanceToMove.getValue()
                    if cashBalanceToMove == 0: lAutoMergeCashBalances = False

                lAutoForceAllowResultingNegativeCashBalance = user_forceAllowResultingNegativeCashBalance.isSelected()
                lAutoForceSaveTrunkFile = user_forceTrunkSave.isSelected()

                sourceTxns = MD_REF.getCurrentAccountBook().getTransactionSet().getTransactionsForAccount(sourceAccount)

                # # ##############################################################################################################

                myPrint("B", "%s: Analysing Investment accounts %s into %s...." %(_THIS_METHOD_NAME, sourceAccount, targetAccount))

                output = "%s: from one account into another:\n" \
                         " ============================================================\n\n" %(_THIS_METHOD_NAME)

                try:

                    base = MD_REF.getCurrentAccount().getBook().getCurrencies().getBaseType()

                    if not perform_qer_quote_loader_check(toolbox_move_merge_investment_txns_frame_, txt, lDialogs=False):
                        if lRunningFromToolbox:
                            output += "Q&ER/QuoteLoader extension(s) loaded. They're either quiet, or user confirmed they're not auto-updating and OK to proceed....\n\n"
                        else:
                            output += "Q&ER / QuoteLoader extension is loaded. Running script from register using selected txns, assuming OK to proceed....\n\n"

                    if lSelectALLTransactionsToMerge:
                        output += "Default Option of Move/Merge **ALL** txns selected...\n\n"
                    elif GlobalVars.selectedInvestmentTransactionsList:
                        output += "REGISTER SELECTION FILTER ACTIVE: %s txns selected\n\n" %(len(GlobalVars.selectedInvestmentTransactionsList))
                    else:
                        output += "FILTER TRANSACTIONS - OPTIONS selected...\n"
                        if lFilterSecurities:
                            output += "....... FILTER Security:     %s\n" %(user_filterSecurity.getSelectedItem().getAccountName())  # noqa
                            # output += ".......................:     Include where source of funds is Buy/Sell Xfr (from another account): %s\n" %(user_filterSecurityIncludeWhereSourceFundsToo.isSelected())
                        if lFilterByDate:
                            output += "....... FILTER Date Range..: %s to %s\n" %(convertStrippedIntDateFormattedText(filterDateFrom), convertStrippedIntDateFormattedText(filterDateTo))
                        output += "\n"

                    if (lAutoIgnoreNegativeShareBalances
                            or lAutoIgnoreAccountLoops
                            or lAutoIgnoreAnyAvgCstLotFlagDifference
                            or lAutoDeleteEmptySourceAccount
                            or lAutoMergeCashBalances
                            or lAutoForceSaveTrunkFile
                            or lAutoForceDeleteSeparatedLotRecords
                            or lAutoForceAllowResultingNegativeCashBalance
                            or iAutoForceWipeLotRecordsWhenTargetAverageCostOption > 0):
                        output += "\nAUTO-PROCESSING OPTIONS selected...\n"

                    if lAutoIgnoreNegativeShareBalances:
                        output += "....... Selected transactions that total to a negative share balance (by security) will be auto-processed without warnings...\n"

                    if lAutoIgnoreAccountLoops:
                        output += "....... Transactions with circular account 'loops' will be auto-processed without warnings...\n"

                    if lAutoForceDeleteSeparatedLotRecords:
                        output += "....... Where matched Buy/Sell LOTs would be separated, then auto-wipe matched LOT details from txns without warnings...\n"

                    if lAutoIgnoreAnyAvgCstLotFlagDifference:
                        output += "....... Securities where source and target Cost Basis Avg Cost and Lot Control flags differ will be auto-moved without warnings (preserving any LOT data)...\n"

                    if iAutoForceWipeLotRecordsWhenTargetAverageCostOption:
                        output += "....... Check for matched LOT data that exists on moved txns to where target account uses average cost controlled - Option selected: '%s'\n"\
                                  %(_WIPE_OPTIONS[iAutoForceWipeLotRecordsWhenTargetAverageCostOption])

                    if lAutoDeleteEmptySourceAccount:
                        output += "....... Source account will be auto-deleted after a successful merge if it's empty with no outstanding initial [cash] balance...\n"

                    if lAutoMergeCashBalances:
                        output += "....... Specified amount of the initial [cash] balance in Source Account will be auto added to Target Account's initial [cash] balance...\n"
                        output += "....... Will move %s of the cash balance into target...\n" %(sourceAccount.getCurrencyType().formatFancy(cashBalanceToMove,MD_decimal))

                    if lAutoForceAllowResultingNegativeCashBalance:
                        output += "....... Allow source account's cash balance to go negative as a result of the move...\n"

                    if lAutoForceSaveTrunkFile:
                        output += "....... Trunk File will be saved too ...\n"

                    output += "\n"

                    output += "Pre move/merge analysis....\n"
                    output += "Source Account: %s\n" %(sourceAccount.getFullAccountName())
                    output += "Target Account: %s\n\n" %(targetAccount.getFullAccountName())

                    def check_txn_matches_filter(_txn, _lFilterSecurities, _lFilterByDate, _filterSecurityList, _filterDateFrom, _filterDateTo):
                        """Checks a Transaction to see if it matches filters"""

                        if GlobalVars.selectedInvestmentTransactionsList:      return True
                        if not _lFilterSecurities and not _lFilterByDate:      return True

                        if _lFilterByDate:
                            if _txn.getDateInt() < _filterDateFrom or _txn.getDateInt() > _filterDateTo:      return False
                            if not _lFilterSecurities:                                                        return True

                        _secTxn = TxnUtil.getSecurityPart(_txn.getParentTxn())    # getParent on a ParentTxn returns itself...
                        if _secTxn is None:                              return False
                        if _secTxn.getAccount() in _filterSecurityList:  return True
                        return False

                    ####################################################################################################
                    # Identify Security Accounts involved in the filtered date range... (if lFilterSecurities is set then we already know it's only 1 security)
                    if GlobalVars.selectedInvestmentTransactionsList or (lFilterByDate and not lFilterSecurities):
                        tmpTxns = GlobalVars.selectedInvestmentTransactionsList if (GlobalVars.selectedInvestmentTransactionsList) else sourceTxns
                        for filteredTxn in tmpTxns:
                            if check_txn_matches_filter(filteredTxn, lFilterSecurities, lFilterByDate, filterSecurityList, filterDateFrom, filterDateTo):
                                if isinstance(filteredTxn, ParentTxn):  # Splits will be a cash transfer and do not need a target security account
                                    secTxn = TxnUtil.getSecurityPart(filteredTxn)
                                    if secTxn is not None:
                                        if secTxn.getAccount() not in filterSecurityList:
                                            filterSecurityList.append(secTxn.getAccount())

                        del tmpTxns
                        if GlobalVars.selectedInvestmentTransactionsList:
                            output += "Register Selected Txns.. Identified Securities that will need to exist in target account:\n"
                        else:
                            output += "Filter by Date Range.. Identified Securities that will need to exist in target account:\n"
                        for filteredSec in sorted(filterSecurityList):
                            output += "Security: %s\n" %(filteredSec.getAccountName())
                        output += "\n"


                    ####################################################################################################
                    # Gather source/target Security Sub Accounts
                    def getSubSecAccts(fromWhere, lSource):
                        """Gets all Security Sub Accounts from the given Investment Account"""
                        secs = []
                        _output = ""
                        _txtSource = "Source"
                        if not lSource: _txtSource = "Target"
                        for acct in fromWhere.getSubAccounts():
                            # noinspection PyUnresolvedReferences
                            if acct.getAccountType() == Account.AccountType.SECURITY and acct.getStartBalance() == 0:
                                secs.append(acct)
                                _relCurr = acct.getCurrencyType()
                                _output += "..%s: %s contains Security: %s (%s shares)\n" %(_txtSource, fromWhere, acct, _relCurr.formatSemiFancy(acct.getBalance(),MD_decimal))
                            elif acct.getAccountType() == Account.AccountType.SECURITY:
                                _txt = "Error: %s found SECURITY (sub account) %s with starting balance of %s - should always be ZERO? - Aborting" %(_txtSource, acct, acct.getStartBalance())
                                myPrint("DB",_txt)
                                setDisplayStatus(txt, "R")
                                myPopupInformationBox(toolbox_move_merge_investment_txns_frame_,_txt,theMessageType=JOptionPane.ERROR_MESSAGE)
                                return None, None
                            else:
                                _txt = "Error: %s found non SECURITY account %s within %s? - ABORTING" %(_txtSource, acct,fromWhere)
                                myPrint("DB",_txt)
                                setDisplayStatus(txt, "R")
                                myPopupInformationBox(toolbox_move_merge_investment_txns_frame_,_txt,theMessageType=JOptionPane.ERROR_MESSAGE)
                                return None, None
                        return secs, _output

                    response = getSubSecAccts(sourceAccount, lSource=True)
                    if response[0] is None: return
                    sourceSecurities = response[0]
                    output += response[1]
                    output += "\n"

                    response = getSubSecAccts(targetAccount, lSource=False)
                    if response[0] is None: return
                    targetSecurities = response[0]
                    output += response[1]
                    output += "\n"

                    def find_src_sec_in_target(findSecCurr):
                        """Finds the matching Security Sub Account within a Target account, from the given Source Account"""
                        for _trgSec in targetSecurities:
                            if _trgSec.getCurrencyType() == findSecCurr:
                                return _trgSec
                        return None

                    ####################################################################################################
                    # Build list of Securities to create in target account, accounting for all selection/filters in place
                    securities_to_create = []
                    for srcSec in sourceSecurities:

                        if not lSelectALLTransactionsToMerge and srcSec not in filterSecurityList: continue

                        trgSec = find_src_sec_in_target(srcSec.getCurrencyType())
                        if trgSec:
                            if trgSec.getUsesAverageCost() != srcSec.getUsesAverageCost():
                                insertTxt = ("Source Investment/Security %s uses %s, but Target %s is different - uses %s"
                                                %(srcSec,
                                                  ("Average Cost Control" if (srcSec.getUsesAverageCost()) else "Lot Control"),
                                                  trgSec,
                                                  ("Average Cost Control" if (trgSec.getUsesAverageCost()) else "Lot Control")))

                                if lAutoIgnoreAnyAvgCstLotFlagDifference:
                                    output += "WARNING: %s - WILL MERGE ANYWAY - CHECK RESULTS MANUALLY AFTER PROCESSING!\n" %(insertTxt)
                                else:
                                    output += "\nRefer to section '[Auto IGNORE any differences between Avg Cst & LOT Control flags and Merge anyway?] (^^1)' in the Help/Guide\n\n"
                                    output += "\n** NOTE: When making another move attempt, ensure any option you were previously advised to select are reselected...\n\n"
                                    QuickJFrame("%s: Help / guide (FAILED VALIDATION)" %(myModuleID), GlobalVars.helpFileData, lWrapText=False, screenLocation=Point(10,10),lAutoSize=True).show_the_frame()
                                    jif = QuickJFrame(_THIS_METHOD_NAME,output,copyToClipboard=GlobalVars.lCopyAllToClipBoard_TB,lJumpToEnd=True,lWrapText=False).show_the_frame()
                                    txt = "Error: %s - Aborting" %(insertTxt)
                                    myPrint("DB",txt)
                                    setDisplayStatus(txt, "R")
                                    myPopupInformationBox(jif,txt,theMessageType=JOptionPane.ERROR_MESSAGE)
                                    return
                            else:
                                output += "Matched: %s to %s >> UsesAverageCost=%s\n" %(srcSec, trgSec, srcSec.getUsesAverageCost())
                        else:
                            securities_to_create.append(srcSec)
                    del lAutoIgnoreAnyAvgCstLotFlagDifference

                    if sourceAccount.getCurrencyType() != targetAccount.getCurrencyType():
                        txt = "LOGIC ERROR! The source acct's currency %s does not match target's %s" %(sourceAccount.getCurrencyType(), targetAccount.getCurrencyType())
                        myPrint("DB",txt)
                        setDisplayStatus(txt, "R")
                        myPopupInformationBox(toolbox_move_merge_investment_txns_frame_,txt,theMessageType=JOptionPane.ERROR_MESSAGE)
                        return
                    output += "\nConfirmed that source and target accounts use the same currency: %s\n" %(sourceAccount.getCurrencyType())

                    targetTxns = MD_REF.getCurrentAccountBook().getTransactionSet().getTransactionsForAccount(targetAccount)

                    countSourceBefore = sourceTxns.getSize()
                    countTargetBefore = targetTxns.getSize()

                    output += "\n"
                    output += "Source Account contains: {:>10} transactions\n".format(countSourceBefore)
                    output += "Target Account contains: {:>10} transactions\n".format(countTargetBefore)
                    del targetTxns

                    ####################################################################################################
                    # Validate against a 'loop' where the source account contains a txf to/from the target account
                    iCountLoops = 0
                    output += "\nValidating against an account 'loop' where the source contains a txf to/from the target\n"

                    sourceTxns = sorted(sourceTxns, key=lambda _x: (_x.getDateInt()))       # Sort for the log output of txns with loops

                    estimateTransactionsToMove = 0

                    filteredSecTxnsToMove = {}  # Used later when validating security balances involved in the move

                    tmpTxns = GlobalVars.selectedInvestmentTransactionsList if (GlobalVars.selectedInvestmentTransactionsList) else sourceTxns
                    for srcTxn in tmpTxns:

                        if not check_txn_matches_filter(srcTxn, lFilterSecurities, lFilterByDate, filterSecurityList, filterDateFrom, filterDateTo):
                            continue

                        estimateTransactionsToMove += 1

                        if isinstance(srcTxn,SplitTxn):
                            if srcTxn.getParentTxn().getAccount() == targetAccount:
                                pass
                            else:
                                continue

                        elif isinstance(srcTxn,ParentTxn):

                            secTxn = TxnUtil.getSecurityPart(srcTxn)
                            if secTxn is not None:
                                secAcct = secTxn.getAccount()
                                if secAcct not in filteredSecTxnsToMove:
                                    filteredSecTxnsToMove[secAcct] = TxnSet()
                                filteredSecTxnsToMove[secAcct].addTxn(secTxn)

                            xfrTxn = TxnUtil.getXfrPart(srcTxn)
                            feeTxn = TxnUtil.getCommissionPart(srcTxn)
                            incTxn = TxnUtil.getIncomePart(srcTxn)
                            expTxn = TxnUtil.getExpensePart(srcTxn)

                            if ((xfrTxn and xfrTxn.getAccount() == targetAccount)
                                    or (feeTxn and feeTxn.getAccount() == targetAccount)
                                    or (incTxn and incTxn.getAccount() == targetAccount)
                                    or (expTxn and expTxn.getAccount() == targetAccount)):
                                pass
                            else:
                                continue

                        else:
                            # Should never happen!!
                            txt = "Error: found a non-Parent / non-Split Txn - Cannot continue...:\n%s\nDate: %s\n" %(srcTxn.getSyncInfo().toMultilineHumanReadableString(), convertStrippedIntDateFormattedText(srcTxn.getDateInt()))
                            myPrint("B",txt)
                            txt2 = "%s: ERROR: Found a non-Parent / non-Split Txn - Cannot continue..." %(_THIS_METHOD_NAME)
                            setDisplayStatus(txt2, "R")
                            MyPopUpDialogBox(toolbox_move_merge_investment_txns_frame_,txt2,txt,OKButtonText="ABORT",lAlertLevel=2).go()
                            return

                        # OK - we have a loop - list them out for the user to find....
                        pTxn = srcTxn.getParentTxn()
                        iCountLoops += 1

                        output += ".. *** LOOP DETECTED %s %s %s %s ***\n" %(convertStrippedIntDateFormattedText(pTxn.getDateInt()),            # noqa
                                                       pad(pTxn.getInvestTxnType().getIDString(),12),                                           # noqa
                                                       pad(pTxn.getDescription()+pTxn.getMemo(),60),                                            # noqa
                                                       rpad(sourceAccount.getCurrencyType().formatFancy(srcTxn.getValue(),MD_decimal),18))      # noqa

                    del tmpTxns

                    if iCountLoops < 1:
                        output += "... to/from accounts validated... No account 'loops' should be created...\n"

                    elif lAutoIgnoreAccountLoops:
                        output += "\n*** to/from accounts failed validation. The move/merge will create %s txns with account 'loops' that refer to self. PLEASE FIX YOURSELF LATER ***\n" %(iCountLoops)

                    else:
                        output += "\n*** to/from accounts checked... %s account 'loops' could exist if we proceed with move/merge... ABORTING - NO CHANGES MADE\n" %(iCountLoops)
                        output += "\nRefer to section '[Auto IGNORE any account 'Loops' and Merge anyway?]' in the Help/Guide\n\n"
                        output += "\n** NOTE: When making another move attempt, ensure any option you were previously advised to select are reselected...\n\n"
                        QuickJFrame("%s: Help / guide (FAILED VALIDATION)" %(myModuleID), GlobalVars.helpFileData, lWrapText=False, screenLocation=Point(10,10),lAutoSize=True).show_the_frame()
                        jif = QuickJFrame(_THIS_METHOD_NAME,output,copyToClipboard=GlobalVars.lCopyAllToClipBoard_TB,lJumpToEnd=True,lWrapText=False).show_the_frame()
                        txt = "ERROR: %s Txns to move/merge includes the target account - would cause account 'loop(s)' - no changes made" %(iCountLoops)
                        myPrint("B", txt)
                        setDisplayStatus(txt, "R")
                        myPopupInformationBox(jif, txt, theMessageType=JOptionPane.ERROR_MESSAGE)
                        return
                    del lAutoIgnoreAccountLoops

                    ####################################################################################################
                    # Look for where matched BUY/SELL LOTS would be separated by a filtered move....

                    # Based on: com.infinitekind.moneydance.model.TxnUtil.parseCostBasisTag(SplitTxn)
                    # def parseCostBasisTag(_txn):
                    #     """Returns the Cost Basis Lot Matching Tags without validating the UUID data first"""
                    #
                    #     if not isinstance(_txn, SplitTxn): return None
                    #     tags = _txn.getParameter(PARAMETER_KEY_COST_BASIS, None)
                    #     if tags is None or len(tags) < 1: return None
                    #     splitTags = tags.split(";")
                    #
                    #     rtnTagList = {}
                    #     for eachTagString in splitTags:
                    #         if eachTagString is None or len(eachTagString) < 1: continue
                    #         splitLine = eachTagString.split(":")
                    #         uuid = splitLine[0]
                    #         qty = Long.valueOf(Long.parseLong(splitLine[1]))
                    #         rtnTagList[uuid] = qty
                    #     return rtnTagList

                    fromTxnSecSet = TxnSet()
                    toTxnSecSet = TxnSet()

                    securityTxnsToFix = {}
                    lLotErrorsABORT = False
                    lMoveWouldSeparateMatchedLOTs = False
                    if not lNeedsLotMatchSeparationTesting:
                        output += "\nThere is no (filtered date range) matched Buy/Sell LOT Data to consider, skipping buy/sell lot separation validation\n\n"
                    else:
                        output += "\nMatched Buy/Sell LOT Data needs validating for a filtered range (in case of matched lot separation):\n"

                        for txn in sourceTxns:
                            if isinstance(txn, SplitTxn): continue  # Splits are cash xfr in/out - not involved in Lot Matching
                            secTxn = TxnUtil.getSecurityPart(txn)
                            if secTxn is None: continue

                            lMoveThisTxn = False
                            if GlobalVars.selectedInvestmentTransactionsList:
                                if txn in GlobalVars.selectedInvestmentTransactionsList:
                                    lMoveThisTxn = True
                            else:
                                if check_txn_matches_filter(txn, lFilterSecurities, lFilterByDate, filterSecurityList, filterDateFrom, filterDateTo):
                                    lMoveThisTxn = True

                            if lMoveThisTxn:
                                toTxnSecSet.addTxn(secTxn)
                            else:
                                fromTxnSecSet.addTxn(secTxn)

                        output += ("... Security records being checked (total: %s): Records that will remain(From) Txns: %s, Records being moved(To) Txns: %s\n"
                                      %((fromTxnSecSet.getSize() + toTxnSecSet.getSize()),
                                        fromTxnSecSet.getSize(),
                                        toTxnSecSet.getSize()))
                        
                        # Reverse sanity check....
                        if GlobalVars.selectedInvestmentTransactionsList:
                            for txn in GlobalVars.selectedInvestmentTransactionsList:
                                if isinstance(txn, SplitTxn): continue
                                secTxn = TxnUtil.getSecurityPart(txn)
                                if secTxn is not None:
                                    if not TxnUtil.getTxnByID(toTxnSecSet, secTxn.getUUID()):
                                        raise Exception("LOGIC ERROR: Reverse check of matched Buy/Sell lots failed!?")


                        # Sweep from/to list checking for potential matched lot separation...
                        onSweep = 0
                        for checkTxnList in [fromTxnSecSet, toTxnSecSet]:
                            for secTxn in checkTxnList:

                                newTags = {}
                                lAnyTagChanges = False

                                cbTags = TxnUtil.parseCostBasisTag(secTxn)  # The MD Version ignores where the uuid does not exist... (and thus we don't really care)
                                if cbTags is None: continue
                                for txnID in cbTags:
                                    checkIDWithinFrom  = TxnUtil.getTxnByID(fromTxnSecSet, txnID)
                                    checkIDWithinTo    = TxnUtil.getTxnByID(toTxnSecSet, txnID)
                                    checkIDWithinOther = checkIDWithinTo if (onSweep == 0) else checkIDWithinFrom
                                    checkIDWithinSame = checkIDWithinTo if (onSweep != 0) else checkIDWithinFrom
                                    if checkIDWithinFrom is None and checkIDWithinTo is None:
                                        # This might not ever trigger unless using my own parseCostBasisTag() method...
                                        lLotErrorsABORT = True
                                        output += "... ERROR:    '%s' Buy (id: %s) matched to sale (id: %s) dated: %s missing/invalid?\n"\
                                                  %(pad(secTxn.getAccount().getAccountName(),50),txnID,secTxn.getUUID(), convertStrippedIntDateFormattedText(secTxn.getDateInt()))
                                    elif checkIDWithinFrom is not None and checkIDWithinTo is not None:
                                        lLotErrorsABORT = True
                                        output += "... ERROR:    '%s' Buy (id: %s dated: %s) matched to sale (id: %s) dated: %s appears in BOTH to and from txn sets?\n"\
                                                  %(pad(secTxn.getAccount().getAccountName(),50),txnID,convertStrippedIntDateFormattedText(checkIDWithinFrom.getDateInt()),secTxn.getUUID(), convertStrippedIntDateFormattedText(secTxn.getDateInt()))
                                    elif checkIDWithinOther is not None and cbTags[txnID] != 0:                         # noqa
                                        lMoveWouldSeparateMatchedLOTs = True
                                        lAnyTagChanges = True   # Essentially we skipped this tag and didn't add it to the dictionary...
                                        output += "... ERROR:    '%s' Buy (id: %s dated: %s) matched to sale (id: %s) dated: %s would be separated by this move!\n"\
                                                  %(pad(secTxn.getAccount().getAccountName(),50),txnID,convertStrippedIntDateFormattedText(checkIDWithinOther.getDateInt()),secTxn.getUUID(), convertStrippedIntDateFormattedText(secTxn.getDateInt()))
                                    elif checkIDWithinOther is not None and cbTags[txnID] == 0:  # noqa - # Yup - you can get records matched with a ZERO qty... Ignore these
                                        lAnyTagChanges = True   # Silently ignore - Essentially we skipped this tag and didn't add it to the dictionary...
                                        output += "... IGNORING: '%s' Buy (id: %s dated: %s) ZERO matched to sale (id: %s) dated: %s would be separated by this move! Will be ignored/deleted\n"\
                                                  %(pad(secTxn.getAccount().getAccountName(),50),txnID,convertStrippedIntDateFormattedText(checkIDWithinOther.getDateInt()),secTxn.getUUID(), convertStrippedIntDateFormattedText(secTxn.getDateInt()))
                                    else:
                                        newTags[txnID] = cbTags[txnID]                                                  # noqa
                                        if debug:
                                            output += "... VALID:    '%s' Buy (id: %s dated: %s) matched to sale (id: %s) dated: %s is not being separated\n"\
                                                      %(pad(secTxn.getAccount().getAccountName(),50),txnID,convertStrippedIntDateFormattedText(checkIDWithinSame.getDateInt()),secTxn.getUUID(), convertStrippedIntDateFormattedText(secTxn.getDateInt()))

                                if lAnyTagChanges:
                                    securityTxnsToFix[secTxn] = newTags

                            onSweep += 1
                    del lNeedsLotMatchSeparationTesting, fromTxnSecSet, toTxnSecSet

                    if lLotErrorsABORT:
                        output += "\n*** Buy/Sell matched LOTs ERRORS EXIST. Cannot proceed. PLEASE FIX & TRY AGAIN ***\n"
                        output += "\n*** TOOLBOX 'FIX: Detect and fix (wipe) LOT records where matched Buy/Sell records are invalid' can wipe missing/invalid LOT matching records ***\n"
                        output += "\nRefer to section '[Auto DELETE any related LOT records on txns moved that separate matched Buy/Sell LOTs?] (^^2)' in the Help/Guide\n\n"
                        output += "\n** NOTE: When making another move attempt, ensure any option you were previously advised to select are reselected...\n\n"
                        QuickJFrame("%s: Help / guide (FAILED VALIDATION)" %(myModuleID), GlobalVars.helpFileData, lWrapText=False, screenLocation=Point(10,10),lAutoSize=True).show_the_frame()
                        jif = QuickJFrame(_THIS_METHOD_NAME,output,copyToClipboard=GlobalVars.lCopyAllToClipBoard_TB,lJumpToEnd=True,lWrapText=False).show_the_frame()
                        txt = "ERROR: Buy/Sell matched LOTs ERRORS EXIST. Cannot proceed. PLEASE FIX & TRY AGAIN (Toolbox might help) - no changes made"
                        myPrint("B", txt)
                        setDisplayStatus(txt, "R")
                        myPopupInformationBox(jif, txt, theMessageType=JOptionPane.ERROR_MESSAGE)
                        return
                    del lLotErrorsABORT

                    if not lMoveWouldSeparateMatchedLOTs:
                        output += "... Buy/Sell matched LOTs passed validation...\n"

                    elif lAutoForceDeleteSeparatedLotRecords:
                        output += "\n*** Buy/Sell matched LOTs FAILED VALIDATION. The move/merge will auto-wipe LOT matching records where txns are being separated. PLEASE FIX LOT DATA MANUALLY LATER ***\n\n"

                    else:
                        txt = "Buy/Sell matched LOTs FAILED VALIDATION"
                        output += "... %s. Matched txns would be separated...\n" %(txt)
                        output += "\nRefer to section '[Auto DELETE any related LOT records on txns moved that separate matched Buy/Sell LOTs?] (^^2)' in the Help/Guide\n\n"
                        output += "\n** NOTE: When making another move attempt, ensure any option you were previously advised to select are reselected...\n\n"
                        QuickJFrame("%s: Help / guide (FAILED VALIDATION)" %(myModuleID), GlobalVars.helpFileData, lWrapText=False, screenLocation=Point(10,10),lAutoSize=True).show_the_frame()
                        jif = QuickJFrame(_THIS_METHOD_NAME,output,copyToClipboard=GlobalVars.lCopyAllToClipBoard_TB,lJumpToEnd=True,lWrapText=False).show_the_frame()
                        txt = "ERROR: %s (refer logfile for details) - no changes made" %(txt)
                        myPrint("B", txt)
                        setDisplayStatus(txt, "R")
                        myPopupInformationBox(jif, txt, theMessageType=JOptionPane.ERROR_MESSAGE)
                        return

                    del lMoveWouldSeparateMatchedLOTs

                    ####################################################################################################
                    # Look for where the total balance of shares being moved would be negative

                    lMoveWouldCreateNegativeShareBalances = False
                    output += "\nValidating that the total share balance (by security) of txns to move is not negative:\n"

                    # Sweep from/to list checking for potential matched lot separation...
                    for secAcct in sorted(filteredSecTxnsToMove, key=lambda _x: (_x.getAccountName().lower())):

                        secTxns = filteredSecTxnsToMove[secAcct]        # type: TxnSet
                        # secTxns.sortByField(AccountUtil.DATE)           # Returns com.infinitekind.moneydance.model.TxnUtil.DATE_COMPARATOR : Comparator
                        secTxns.setHoldBalances(True)
                        secTxns.recalcBalances(0, False, False)

                        lastPosn = secTxns.getSize()-1
                        shareBalance = secTxns.getBalanceAt(lastPosn)
                        output += "... Security: %s - moving txns with a share balance of %s %s\n" %(secAcct.getAccountName(),
                                                                                                     secAcct.getCurrencyType().formatSemiFancy(shareBalance, MD_decimal),
                                                                                                     "***" if shareBalance < 0 else "")
                        if shareBalance < 0:
                            lMoveWouldCreateNegativeShareBalances = True


                        # Now check the source in case a buy is moving and leaving sells that make the source negative.... <phew>
                        tmpSourceSecTxns = MD_REF.getCurrentAccountBook().getTransactionSet().getTransactionsForAccount(secAcct)
                        for txn in secTxns: tmpSourceSecTxns.removeTxn(txn)
                        if tmpSourceSecTxns.getSize() > 0:
                            tmpSourceSecTxns.setHoldBalances(True)
                            tmpSourceSecTxns.recalcBalances(0, False, False)

                            lastPosn = tmpSourceSecTxns.getSize()-1
                            shareBalance = tmpSourceSecTxns.getBalanceAt(lastPosn)
                            if shareBalance < 0:
                                lMoveWouldCreateNegativeShareBalances = True
                                output += "...... Security: %s - moving txns will leave a negative share balance of %s behind in the source account %s\n" %(secAcct.getAccountName(),
                                                                                                                                                        secAcct.getCurrencyType().formatSemiFancy(shareBalance, MD_decimal),
                                                                                                                                                        "***" if shareBalance < 0 else "")
                        del secTxns, tmpSourceSecTxns

                    if not lMoveWouldCreateNegativeShareBalances:
                        output += "... No negative share balances (by security detected) within the txns to move..\n"

                    elif lAutoIgnoreNegativeShareBalances:
                        output += "\n*** Check for negative share balances FAILED VALIDATION. The move/merge will move shares where the share balance of moved txns is negative ***\n\n"

                    else:
                        txt = "Check for negative share balances FAILED VALIDATION"
                        output += ">> %s. Txns to move contain negative share balances (by security)...\n\n" %(txt)
                        output += "\nRefer to section '[Auto IGNORE where the share balance (by security) of selected txns to move is negative?]' in the Help/Guide\n\n"
                        output += "\n** NOTE: When making another move attempt, ensure any option you were previously advised to select are reselected...\n\n"
                        QuickJFrame("%s: Help / guide (FAILED VALIDATION)" %(myModuleID), GlobalVars.helpFileData, lWrapText=False, screenLocation=Point(10,10),lAutoSize=True).show_the_frame()
                        jif = QuickJFrame(_THIS_METHOD_NAME,output,copyToClipboard=GlobalVars.lCopyAllToClipBoard_TB,lJumpToEnd=True,lWrapText=False).show_the_frame()
                        txt = "ERROR: %s - no changes made" %(txt)
                        myPrint("B", txt)
                        setDisplayStatus(txt, "R")
                        myPopupInformationBox(jif, txt, theMessageType=JOptionPane.ERROR_MESSAGE)
                        return
                    del lAutoIgnoreNegativeShareBalances


                    ####################################################################################################
                    # Look for where the txn to move contains matched LOT data and the target is average cost control...

                    lMoveWouldMoveLOTDataToCostControlSecurity = False
                    output += "\nValidating that transactions to move do not contain matched LOT data (when target security is using 'Average Cost Control'):\n"

                    # Sweep from/to list checking for potential matched lot separation...
                    for secAcct in sorted(filteredSecTxnsToMove, key=lambda _x: (_x.getAccountName().lower())):

                        trgSec = find_src_sec_in_target(secAcct.getCurrencyType())
                        if not (secAcct if (trgSec is None) else trgSec).getUsesAverageCost(): continue

                        secTxns = filteredSecTxnsToMove[secAcct]        # type: TxnSet
                        secTxns.sortByField(AccountUtil.DATE)           # Returns com.infinitekind.moneydance.model.TxnUtil.DATE_COMPARATOR : Comparator

                        for txn in secTxns:
                            cbTags = TxnUtil.parseCostBasisTag(txn)
                            if cbTags is None or len(cbTags) < 1: continue
                            lMoveWouldMoveLOTDataToCostControlSecurity = True
                            output += ("... Security: %s - Sell txn dated: %s contains matched LOT data but target uses Average Cost Control. \n"
                                       %(secAcct.getAccountName(), convertStrippedIntDateFormattedText(txn.getDateInt())))
                        del secTxns

                    if not lMoveWouldMoveLOTDataToCostControlSecurity:
                        output += "... Validation passed OK..\n"
                        iAutoForceWipeLotRecordsWhenTargetAverageCostOption = False

                    elif iAutoForceWipeLotRecordsWhenTargetAverageCostOption == _WIPE_WIPE:
                        output += "\n*** Check for matched LOT data when target uses average cost control FAILED VALIDATION. The move/merge will WIPE/REMOVE matched LOT data from txns being moved where target account uses average cost control ***\n\n"

                    elif iAutoForceWipeLotRecordsWhenTargetAverageCostOption == _WIPE_IGNORE:
                        output += "\n*** Check for matched LOT data when target uses average cost control FAILED VALIDATION. The move/merge will RETAIN the matched LOT data on txns being moved even where target account uses average cost control ***\n\n"

                    else:
                        txt = "Check for matched LOT data when target uses average cost control - FAILED VALIDATION"
                        output += ">> %s. Txns to move contain matched LOT data (select 'IGNORE' or 'WIPE' in the option drop down. Either will do to force this move through)...\n\n" %(txt)
                        output += "\nRefer to section '[Select option when target uses 'average cost control' and txns being moved contain matched LOT data] (^^3)' in the Help/Guide\n\n"
                        output += "\n** NOTE: When making another move attempt, ensure any option you were previously advised to select are reselected...\n\n"
                        QuickJFrame("%s: Help / guide (FAILED VALIDATION)" %(myModuleID), GlobalVars.helpFileData, lWrapText=False, screenLocation=Point(10,10),lAutoSize=True).show_the_frame()
                        jif = QuickJFrame(_THIS_METHOD_NAME,output,copyToClipboard=GlobalVars.lCopyAllToClipBoard_TB,lJumpToEnd=True,lWrapText=False).show_the_frame()
                        txt = "ERROR: %s - no changes made" %(txt)
                        myPrint("B", txt)
                        setDisplayStatus(txt, "R")
                        myPopupInformationBox(jif, txt, theMessageType=JOptionPane.ERROR_MESSAGE)
                        return
                    del filteredSecTxnsToMove, lMoveWouldMoveLOTDataToCostControlSecurity


                    ####################################################################################################
                    # Check initial [cash] balances
                    sourceRCurr = sourceAccount.getCurrencyType()
                    sourceStartBal = sourceAccount.getStartBalance()

                    targetRCurr = targetAccount.getCurrencyType()
                    targetStartBal = targetAccount.getStartBalance()

                    if sourceStartBal == 0 and targetStartBal == 0:
                        output += "\nSource & Target have starting cash balances of zero...\n"
                    else:
                        output += "\nSource starting cash balance: %s\n" %(sourceRCurr.formatSemiFancy(sourceStartBal,MD_decimal))
                        output += "\nTarget starting cash balance: %s\n" %(targetRCurr.formatSemiFancy(targetStartBal,MD_decimal))

                    if cashBalanceToMove != 0:
                        output += "User has requested to move %s of source acct's starting cash balance, and add into target's...\n\n" %(sourceAccount.getCurrencyType().formatFancy(cashBalanceToMove,MD_decimal))
                    else:
                        output += "Source Account's starting cash balance will NOT be moved into target's\n\n"

                    if sourceStartBal != 0 and lAutoDeleteEmptySourceAccount and (sourceStartBal - cashBalanceToMove) != 0:
                        txt = "NOTE: Source account cannot be auto-deleted post merge as it would be left with a cash starting balance (disabling auto-delete Source Account option OFF)..."
                        output += "%s\n\n" %(txt)
                        lAutoDeleteEmptySourceAccount = False

                    ####################################################################################################
                    # Validate for a resultant negative cash balance
                    if not lAutoForceAllowResultingNegativeCashBalance:

                        fromResultantTxnSet = TxnSet()

                        output += "\nValidating against a negative cash balance in the source account as a result of the move/merge:\n"
                        for txn in sourceTxns:
                            lMoveThisTxn = False
                            if GlobalVars.selectedInvestmentTransactionsList:
                                if txn in GlobalVars.selectedInvestmentTransactionsList:
                                    lMoveThisTxn = True
                            else:
                                if check_txn_matches_filter(txn, lFilterSecurities, lFilterByDate, filterSecurityList, filterDateFrom, filterDateTo):
                                    lMoveThisTxn = True

                            if not lMoveThisTxn: fromResultantTxnSet.addTxn(txn)

                        fromResultantTxnSet.setHoldBalances(True)
                        resultantSourceInitialCashBalance = sourceStartBal - cashBalanceToMove
                        fromResultantTxnSet.recalcBalances(resultantSourceInitialCashBalance, False, False)

                        if fromResultantTxnSet.getSize() > 0:
                            lastPosn = fromResultantTxnSet.getSize()-1
                            estimatedNewSourceCashBalance = fromResultantTxnSet.getBalanceAt(lastPosn)
                        else:
                            estimatedNewSourceCashBalance = resultantSourceInitialCashBalance

                        if estimatedNewSourceCashBalance < 0:
                            output += ">> Check for resultant negative cash balance in source account FAILED VALIDATION. Would result in a negative cash balance of: %s\n\n" %(sourceAccount.getCurrencyType().formatFancy(estimatedNewSourceCashBalance, MD_decimal))
                            output += "\nRefer to section '[Auto ALLOW Source Account's Cash balance to go negative?]' and txns being moved contain matched LOT data] (^^3)' in the Help/Guide\n\n"
                            output += "\n** NOTE: When making another move attempt, ensure any option you were previously advised to select are reselected...\n\n"
                            QuickJFrame("%s: Help / guide (FAILED VALIDATION)" %(myModuleID), GlobalVars.helpFileData, lWrapText=False, screenLocation=Point(10,10),lAutoSize=True).show_the_frame()
                            jif = QuickJFrame(_THIS_METHOD_NAME,output,copyToClipboard=GlobalVars.lCopyAllToClipBoard_TB,lJumpToEnd=True,lWrapText=False).show_the_frame()
                            txt = "ERROR: Check for source account negative cash balance (after move) FAILED VALIDATION - no changes made"
                            myPrint("B", txt)
                            setDisplayStatus(txt, "R")
                            myPopupInformationBox(jif, txt, theMessageType=JOptionPane.ERROR_MESSAGE)
                            return

                        output += "... No resultant negative cash balance in source detected...\n\n"
                        del fromResultantTxnSet

                    output += "\n\n>> %s TRANSACTIONS WILL BE MOVED (out of %s in Source Account) <<\n\n" %(estimateTransactionsToMove, countSourceBefore)

                    ask = MyPopUpDialogBox(toolbox_move_merge_investment_txns_frame_,
                                           "%s: %s txns from selected Investment account into another.. REVIEW DIAGNOSTIC BELOW - THEN CLICK PROCEED TO EXECUTE THE MERGE" %(_THIS_METHOD_NAME, estimateTransactionsToMove),
                                           output,
                                           theTitle=_THIS_METHOD_NAME.upper(),
                                           lCancelButton=True,
                                           OKButtonText="PROCEED")
                    if not ask.go():
                        txt = "%s: - User Aborted - No changes made!" %(_THIS_METHOD_NAME)
                        output += "\n\n%s\n" %(txt)
                        myPrint("B",txt)
                        setDisplayStatus(txt, "R")
                        jif = QuickJFrame(_THIS_METHOD_NAME,output,copyToClipboard=GlobalVars.lCopyAllToClipBoard_TB,lWrapText=False).show_the_frame()
                        myPopupInformationBox(jif,txt,theMessageType=JOptionPane.WARNING_MESSAGE)
                        return

                    if not confirm_backup_confirm_disclaimer(toolbox_move_merge_investment_txns_frame_, _THIS_METHOD_NAME.upper(),
                           "EXECUTE MOVE FROM %s to %s?" %(sourceAccount,targetAccount)):
                        txt = "%s: - User Aborted - No changes made!" %(_THIS_METHOD_NAME)
                        output += "\n\n%s\n" %(txt)
                        QuickJFrame(_THIS_METHOD_NAME,output,copyToClipboard=GlobalVars.lCopyAllToClipBoard_TB,lWrapText=False).show_the_frame()
                        return

                    output += "\nUSER ACCEPTED DISCLAIMER AND CONFIRMED TO PROCEED WITH MOVE/MERGE FROM %s to %s.....\n\n" %(sourceAccount, targetAccount)


                    ################
                    # LET'S DO IT! #
                    ################

                    # Prepare before totals...
                    _WHAT = 0
                    _QTY = 1
                    _COSTBASIS = 2
                    _VALUE = 3
                    _CBFLAG = 4

                    sourceValuesBefore = []
                    targetValuesBefore = []

                    lAnyCostBasisErrorsFound = [False]

                    def create_totals(theCount, theAccount, theTable):
                        _acctRelCurr = theAccount.getCurrencyType()
                        theTable.append(["Txn Count",    theCount, "", "", ""])
                        theTable.append(["Account Starting Balance", "","",_acctRelCurr.formatSemiFancy(theAccount.getStartBalance(),MD_decimal), ""])
                        theTable.append(["Cash Balance", "", "", _acctRelCurr.formatSemiFancy(theAccount.getBalance(),MD_decimal), ""])
                        _totals = [0.0, 0.0, _acctRelCurr.getDoubleValue(theAccount.getBalance()), False]
                        lDetectCBError = False
                        for acct in theAccount.getSubAccounts():
                            # noinspection PyUnresolvedReferences
                            if acct.getAccountType() == Account.AccountType.SECURITY:

                                if not InvestUtil.isCostBasisValid(acct):
                                    lDetectCBError = True
                                    lAnyCostBasisErrorsFound[0] = True

                                _subAcctRelCurr = acct.getCurrencyType()
                                subAcctBal = acct.getBalance()
                                subAcctCostBasis = InvestUtil.getCostBasis(acct)
                                # price = (1.0 / _subAcctRelCurr.adjustRateForSplitsInt(DateUtil.convertCalToInt(today), _subAcctRelCurr.getRelativeRate()))                        # noqa
                                price = CurrencyTable.getUserRate(_subAcctRelCurr, _acctRelCurr)

                                _totals[0] += _subAcctRelCurr.getDoubleValue(subAcctBal)
                                _totals[1] += _acctRelCurr.getDoubleValue(subAcctCostBasis)
                                _totals[2] +=  round(_subAcctRelCurr.getDoubleValue(subAcctBal) * price,_acctRelCurr.getDecimalPlaces())
                                if lDetectCBError: _totals[3] = True
                                theTable.append([acct.getAccountName(),
                                                 _subAcctRelCurr.formatSemiFancy(subAcctBal,MD_decimal),
                                                 _acctRelCurr.formatSemiFancy(subAcctCostBasis,MD_decimal),
                                                 _acctRelCurr.formatSemiFancy(_acctRelCurr.getLongValue(round(_subAcctRelCurr.getDoubleValue(subAcctBal) * price,_acctRelCurr.getDecimalPlaces())),MD_decimal),
                                                 lDetectCBError])
                        theTable.append(["**TOTALS:",
                                         _totals[0],
                                         _acctRelCurr.formatSemiFancy(_acctRelCurr.getLongValue(_totals[1]),MD_decimal),
                                         _acctRelCurr.formatSemiFancy(_acctRelCurr.getLongValue(_totals[2]),MD_decimal),
                                        _totals[3]])

                    create_totals(countSourceBefore, sourceAccount, sourceValuesBefore)
                    create_totals(countTargetBefore, targetAccount, targetValuesBefore)

                    if lAnyCostBasisErrorsFound[0]:
                        output += "\n\n** WARNING: Lot Control / Cost Basis errors detected before changes started - review output....\n\n"
                    else:
                        output += "\nLot Control / Cost Basis reports OK before changes....\n"

                    output += "\n"

                except:
                    txt = "MINOR ERROR - Move/merge crashed before any move/merge. Please review output and console".upper()
                    myPrint("B",txt); output += "\n\n\n%s\n\n" %(txt)
                    output += dump_sys_error_to_md_console_and_errorlog(True)
                    setDisplayStatus(txt, "R")
                    jif = QuickJFrame("MINOR ERROR - %s:" %(_THIS_METHOD_NAME.upper()),output,copyToClipboard=GlobalVars.lCopyAllToClipBoard_TB,lWrapText=False).show_the_frame()
                    myPopupInformationBox(jif,txt,theMessageType=JOptionPane.ERROR_MESSAGE)
                    return

                # Catch any crash during the update as this would be bad... :-(
                try:

                    pleaseWait = MyPopUpDialogBox(toolbox_move_merge_investment_txns_frame_,
                                                  "Please wait: executing move/merge right now..",
                                                  theTitle=_THIS_METHOD_NAME.upper(),
                                                  lModal=False,
                                                  OKButtonText="WAIT")
                    pleaseWait.go()

                    myPrint("DB","Flushing dataset pre-move/merge changes in memory to sync... and disabling balance recalculation(s) / display refresh(es)..")
                    MD_REF.saveCurrentAccount()           # Flush any current txns in memory and start a new sync record for the move/merge..
                    MD_REF.getCurrentAccount().getBook().setRecalcBalances(False)
                    MD_REF.getUI().setSuspendRefresh(True)

                    # Start by adding any Account Starting Cash Balances....
                    if cashBalanceToMove != 0:
                        txt = "Moving %s from source starting cash balance of %s (leaving %s) into target's (original = %s) resulting in %s"\
                              %(sourceRCurr.formatFancy(cashBalanceToMove,MD_decimal),
                                sourceRCurr.formatFancy(sourceStartBal,MD_decimal),
                                sourceRCurr.formatFancy((sourceStartBal - cashBalanceToMove),MD_decimal),
                                targetRCurr.formatFancy(targetStartBal,MD_decimal),
                                targetRCurr.formatFancy((targetStartBal + cashBalanceToMove),MD_decimal))

                        myPrint("B", txt); output += "%s\n" %(txt)

                        targetAccount.setEditingMode()
                        targetAccount.setStartBalance(targetStartBal + cashBalanceToMove)
                        targetAccount.setParameter(PARAMETER_KEY,True)
                        targetAccount.syncItem()

                        sourceAccount.setEditingMode()
                        sourceAccount.setStartBalance(sourceStartBal - cashBalanceToMove)
                        sourceAccount.setParameter(PARAMETER_KEY,True)
                        sourceAccount.syncItem()


                    # Now create any missing security sub account(s)...
                    if len(securities_to_create) > 0:
                        txt = "Adding %s missing security(s) to target Investment Account:" %(len(securities_to_create))
                        myPrint("B", txt); output += "%s\n" %(txt)

                        for sec_to_create in securities_to_create:
                            txt = "... Creating: %s" %(sec_to_create.getAccountName())
                            myPrint("B", txt); output += "%s\n" %(txt)

                            newSecurityAcct = Account.makeAccount(MD_REF.getCurrentAccountBook(),
                                                                  Account.AccountType.SECURITY,                         # noqa
                                                                  targetAccount)

                            newSecurityAcct.setEditingMode()
                            newSecurityAcct.getUUID()
                            newSecurityAcct.setAccountName(sec_to_create.getAccountName())
                            newSecurityAcct.setCurrencyType(sec_to_create.getCurrencyType())
                            newSecurityAcct.setStartBalance(0)

                            newSecurityAcct.setUsesAverageCost(sec_to_create.getUsesAverageCost())
                            newSecurityAcct.setBroker(sec_to_create.getBroker())
                            newSecurityAcct.setBrokerPhone(sec_to_create.getBrokerPhone())
                            newSecurityAcct.setAPR(sec_to_create.getAPR())
                            newSecurityAcct.setBondType(sec_to_create.getBondType())
                            newSecurityAcct.setComment(sec_to_create.getComment())
                            newSecurityAcct.setCompounding(sec_to_create.getCompounding())
                            newSecurityAcct.setFaceValue(sec_to_create.getFaceValue())
                            newSecurityAcct.setFaceValue(sec_to_create.getFaceValue())
                            newSecurityAcct.setMaturity(sec_to_create.getMaturity())
                            newSecurityAcct.setMonth(sec_to_create.getMonth())
                            newSecurityAcct.setNumYears(sec_to_create.getNumYears())
                            newSecurityAcct.setPut(sec_to_create.getPut())
                            newSecurityAcct.setOptionPrice(sec_to_create.getOptionPrice())
                            newSecurityAcct.setDividend(sec_to_create.getDividend())
                            newSecurityAcct.setExchange(sec_to_create.getExchange())
                            newSecurityAcct.setSecurityType(sec_to_create.getSecurityType())
                            newSecurityAcct.setSecuritySubType(sec_to_create.getSecuritySubType())
                            newSecurityAcct.setStrikePrice(sec_to_create.getStrikePrice())

                            for param in ["hide","hide_on_hp","ol.haspendingtxns", "ol.new_txn_count"]:
                                newSecurityAcct.setParameter(param, sec_to_create.getParameter(param))

                            newSecurityAcct.setParameter(PARAMETER_KEY,True)
                            newSecurityAcct.syncItem()
                            targetSecurities.append(newSecurityAcct)                                                    # noqa


                    copyTxns = sourceTxns
                    del sourceTxns

                    txt = "Now Moving/Merging transactions...:"
                    myPrint("B", txt); output += "\n\n%s\n" %(txt)

                    # now for the merge/move of the transactions...
                    tmpTxns = GlobalVars.selectedInvestmentTransactionsList if (GlobalVars.selectedInvestmentTransactionsList) else copyTxns
                    for srcTxn in tmpTxns:

                        if not check_txn_matches_filter(srcTxn, lFilterSecurities, lFilterByDate, filterSecurityList, filterDateFrom, filterDateTo):
                            continue

                        GlobalVars.countTxnsMoved += 1

                        if isinstance(srcTxn, SplitTxn):      # This is a cash transfer
                            pTxn = srcTxn.getParentTxn()
                            pTxn.setEditingMode()
                            srcTxn.setAccount(targetAccount)
                            srcTxn.setParameter(PARAMETER_KEY,True)
                            pTxn.syncItem()
                            output += ".. %s %s %s %s\n" %(convertStrippedIntDateFormattedText(pTxn.getDateInt()),                              # noqa
                                                           pad(pTxn.getInvestTxnType().getIDString(),12),                                       # noqa
                                                           pad(pTxn.getDescription()+pTxn.getMemo(),60),                                        # noqa
                                                           rpad(sourceAccount.getCurrencyType().formatFancy(srcTxn.getValue(),MD_decimal),18))  # noqa
                            continue

                        # Thus, we are on a parent...
                        if not isinstance(srcTxn, ParentTxn): raise Exception("Error: found a non-parent: %s" %(srcTxn))
                        srcTxn.setEditingMode()
                        for iSplit in range(0, srcTxn.getSplitCount()):
                            theSplit = srcTxn.getSplit(iSplit)
                            theSrcSplitAcct = theSplit.getAccount()
                            # noinspection PyUnresolvedReferences
                            if theSrcSplitAcct.getAccountType() == Account.AccountType.SECURITY:
                                trgSec = find_src_sec_in_target(theSrcSplitAcct.getCurrencyType())

                                # Wipe option will remove LOT matching data. Thus IGNORE will do nothing and carry the info across
                                if iAutoForceWipeLotRecordsWhenTargetAverageCostOption == _WIPE_WIPE and trgSec.getUsesAverageCost():
                                    if InvestUtil.isSaleTransaction(srcTxn.getParentTxn().getInvestTxnType()):
                                        if (theSplit.getParameter(PARAMETER_KEY_COST_BASIS, None) is not None):
                                            if debug: theSplit.setParameter(PARAMETER_KEY+PARAMETER_KEY_OLD_COST_BASIS,theSplit.getParameter(PARAMETER_KEY_COST_BASIS, None))
                                            theSplit.setParameter(PARAMETER_KEY_COST_BASIS, None)

                                            # If we just wiped the cost basis tags, then just remove them from the list to fix next...
                                            if theSplit in securityTxnsToFix: securityTxnsToFix.pop(theSplit)

                                # Update the account and thus finally move the security
                                theSplit.setAccount(trgSec)

                        srcTxn.setParameter(PARAMETER_KEY,True)
                        srcTxn.setAccount(targetAccount)

                        srcTxn.syncItem()
                        output += ".. %s %s %s %s %s\n" %(convertStrippedIntDateFormattedText(srcTxn.getDateInt()),                             # noqa
                                                          pad(srcTxn.getInvestTxnType().getIDString(),12),                                      # noqa
                                                          pad(srcTxn.getDescription()+srcTxn.getMemo(),60),                                     # noqa
                                                          rpad(sourceAccount.getCurrencyType().formatFancy(srcTxn.getValue(),MD_decimal),18),   # noqa
                                                          "")

                    del copyTxns, tmpTxns

                    if len(securityTxnsToFix) > 0:
                        txt = "Now updating Buy/Sell Lot Matching data on %s separated transactions (removing any separated Lot data)...:" %(len(securityTxnsToFix))
                        myPrint("B", txt); output += "\n\n%s\n" %(txt)

                        for secTxn in securityTxnsToFix:
                            newTag = ""
                            cbTags = securityTxnsToFix[secTxn]
                            for txnID in cbTags:
                                newTag += "{}:{};".format(txnID,cbTags[txnID])

                            pTxn = secTxn.getParentTxn()
                            pTxn.setEditingMode()

                            if debug: secTxn.setParameter(PARAMETER_KEY+PARAMETER_KEY_OLD_COST_BASIS,secTxn.getParameter(PARAMETER_KEY_COST_BASIS, None))
                            secTxn.setParameter(PARAMETER_KEY_COST_BASIS, newTag)
                            pTxn.syncItem()

                        txt = "....  Buy/Sell Lot Matching data on %s separated transactions UPDATED...:" %(len(securityTxnsToFix))
                        myPrint("B", txt); output += "%s\n" %(txt)

                    output += "\n>> Move/merge completed..: %s txns moved to target account\n\n" %(GlobalVars.countTxnsMoved)

                except:

                    txt = ("MAJOR ERROR - %s: crashed. Please review output, console, and RESTORE YOUR DATASET!" %(_THIS_METHOD_NAME)).upper()
                    myPrint("B",txt); output += "\n\n\n%s\n\n" %(txt)
                    output += dump_sys_error_to_md_console_and_errorlog(True)
                    setDisplayStatus(txt, "R")
                    jif = QuickJFrame("MAJOR ERROR - %s:" %(_THIS_METHOD_NAME.upper()),output,copyToClipboard=GlobalVars.lCopyAllToClipBoard_TB,lWrapText=False).show_the_frame()
                    myPopupInformationBox(jif,txt,theMessageType=JOptionPane.ERROR_MESSAGE)
                    return

                finally:

                    myPrint("DB","Saving dataset move/merge changes in memory to sync... and re-enabling balance recalculation(s) and display refresh(es)..")
                    MD_REF.saveCurrentAccount()
                    MD_REF.getCurrentAccount().getBook().setRecalcBalances(True)
                    MD_REF.getUI().setSuspendRefresh(False)		# This does this too: book.notifyAccountModified(root)

                    pleaseWait.kill()                                                                                           # noqa

                try:
                    # Confirm whether there are any txns left in the source account etc...
                    sourceTxns = MD_REF.getCurrentAccountBook().getTransactionSet().getTransactionsForAccount(sourceAccount)
                    targetTxns = MD_REF.getCurrentAccountBook().getTransactionSet().getTransactionsForAccount(targetAccount)
                    countSourceAfter = sourceTxns.getSize()
                    countTargetAfter = targetTxns.getSize()
                    output += "Source Account now contains: {:>10} transactions\n".format(countSourceAfter)
                    output += "Target Account now contains: {:>10} transactions\n".format(countTargetAfter)

                    del sourceTxns, targetTxns

                    if countSourceAfter == 0:
                        output += "\nVerified that source account now contains ZERO txns...\n"
                    elif not lSelectALLTransactionsToMerge:
                        output += "\nSource account %s still contains %s txns - but accepted as filtering was in operation...\n" %(sourceAccount, countSourceAfter)
                    else:
                        txt = "ERROR: source account %s still seems to have %s transactions" %(sourceAccount, countSourceAfter)
                        myPrint("B", txt); output += "\n%s\n" %(txt)
                        jif = QuickJFrame(_THIS_METHOD_NAME.upper(),output,copyToClipboard=GlobalVars.lCopyAllToClipBoard_TB,lWrapText=False).show_the_frame()
                        setDisplayStatus(txt, "R")
                        myPopupInformationBox(jif,txt,theMessageType=JOptionPane.ERROR_MESSAGE)
                        return

                    if lSelectALLTransactionsToMerge and countTargetAfter == (countSourceBefore + countTargetBefore):
                        output += "Verified that ending target txn count of %s is equal to original source %s + target %s\n"\
                                  %(countTargetAfter, countSourceBefore, countTargetBefore)
                    elif not lSelectALLTransactionsToMerge and (countSourceBefore + countTargetBefore ==  countSourceAfter + countTargetAfter):
                        output += "FILTERED: Verified txn counts that ending source: %s + target: %s is equal to original source: %s + original target: %s - Total: %s\n"\
                                  %(countSourceAfter, countTargetAfter, countSourceBefore, countTargetBefore, (countSourceAfter+countTargetAfter))
                    else:
                        txt = "ERROR: txn counts do not tally - ending source: %s + target: %s NOT equal to original source: %s + target: %s - Total: %s\n"\
                              %(countSourceAfter, countTargetAfter, countSourceBefore, countTargetBefore, (countSourceAfter+countTargetAfter))
                        myPrint("B", txt); output += "\n%s\n" %(txt)
                        jif = QuickJFrame(_THIS_METHOD_NAME.upper(),output,copyToClipboard=GlobalVars.lCopyAllToClipBoard_TB,lWrapText=False).show_the_frame()
                        setDisplayStatus(txt, "R")
                        myPopupInformationBox(jif,txt,theMessageType=JOptionPane.ERROR_MESSAGE)
                        return

                    # Total up the Accounts after the merge...
                    sourceValuesAfter = []
                    targetValuesAfter = []

                    lAnyCostBasisErrorsFound[0] = False
                    create_totals(countSourceAfter, sourceAccount, sourceValuesAfter)
                    create_totals(countTargetAfter, targetAccount, targetValuesAfter)

                    # Delete the empty Account(s) if requested...
                    # Don't forget we block this earlier on if source has a starting balance and user did not request to add into target
                    if lAutoDeleteEmptySourceAccount and countSourceAfter == 0:
                        MD_REF.getCurrentAccount().getBook().setRecalcBalances(False)
                        MD_REF.getUI().setSuspendRefresh(True)

                        txt = "Now deleting the empty source account after removing associated Securities..:"
                        myPrint("B", txt); output += "%s\n\n" %(txt)

                        for subAcct in sourceAccount.getSubAccounts():
                            subAcct.deleteItem()
                        sourceAccount.deleteItem()

                        MD_REF.saveCurrentAccount()
                        MD_REF.getCurrentAccount().getBook().setRecalcBalances(True)
                        MD_REF.getUI().setSuspendRefresh(False)		# This does this too: book.notifyAccountModified(root)
                    else:
                        txt = "NOT deleting source account: %s (Auto-Delete rqst: %s, Source Txns Remaining: %s)" %(sourceAccount, lAutoDeleteEmptySourceAccount, countSourceAfter)
                        myPrint("B", txt); output += "\n%s\n" %(txt)

                    # OK - Main update is done....

                    output += "\n\n ***\n\n" \
                              "STATISTICS OF ACCOUNTS BEFORE AND AFTER...\n"\
                             " =========================================\n\n"
                    output += "BEFORE:\n"\
                              "-----------------------------------------------------\n"

                    def output_stats(theText, theAccount, theTable):

                        if theAccount.getCurrencyType() == base or theAccount.getCurrencyType() is None:
                            relText = ""
                        else:
                            relText = " relative to %s" %(theAccount.getCurrencyType().getRelativeCurrency())

                        local_output = "%s: %s (Currency: %s%s)\n" %(theText, theAccount, theAccount.getCurrencyType(), relText)
                        iRow = 1
                        posInc = 0
                        for data in theTable:
                            if iRow == 2:
                                posInc += 14
                                local_output += "   %s %s %s %s\n" %(pad("",60+posInc),rpad("Qty Shares",12), rpad("Cost Basis",15), rpad("Current Value",15))
                                local_output += "   %s %s %s %s\n" %(pad("",60+posInc),rpad("----------",12), rpad("----------",15), rpad("-------------",15))

                            if iRow == 4:
                                local_output += "   %s %s %s %s\n" %(pad("",60+posInc),rpad("",12), rpad("",15), rpad("-------------",15))

                            if data[_WHAT].upper() == "**TOTALS:".upper():
                                local_output += "   %s %s %s %s\n" %(pad("",60+posInc),rpad("----------",12), rpad("----------",15), rpad("-------------",15))

                            cbMsg = ""
                            if data[_CBFLAG]: cbMsg = " * Cost Basis Error detected"
                            local_output += "   %s %s %s %s %s\n" %(pad(data[_WHAT],60+posInc),rpad(data[_QTY],12), rpad(data[_COSTBASIS],15), rpad(data[_VALUE],15),cbMsg)
                            iRow += 1
                        return local_output

                    output += output_stats("Source", sourceAccount, sourceValuesBefore)
                    output += "\n"
                    output += output_stats("Target", targetAccount, targetValuesBefore)

                    output += "\n\n"
                    output += "AFTER:\n" \
                              "-------------------------------------------------------\n"

                    output += output_stats("Source", sourceAccount, sourceValuesAfter)
                    output += "\n"
                    output += output_stats("Target", targetAccount, targetValuesAfter)

                    if lAnyCostBasisErrorsFound[0]:
                        output += "\n\n** WARNING: Lot Control / Cost Basis errors detected after changes completed - review output....\n\n"
                    else:
                        output += "\nLot Control / Cost Basis reports OK after changes....\n"

                    if lAutoForceSaveTrunkFile:    # We are saving Trunk as we want to flush the mass changes to disk. Stops the restart reapplying these again....
                        pleaseWait = MyPopUpDialogBox(toolbox_move_merge_investment_txns_frame_,
                                                      "Please wait: Flushing dataset (and these move/merge txns) back to disk.....",
                                                      theTitle=_THIS_METHOD_NAME.upper(),
                                                      lModal=False,
                                                      OKButtonText="WAIT")
                        pleaseWait.go()

                        txt = "... Saving Trunk to flush all changes back to disk now ...."
                        myPrint("B", txt); output += "\n%s\n" %(txt)
                        MD_REF.getCurrentAccount().getBook().saveTrunkFile()
                        pleaseWait.kill()

                    output += "\n\n%s TRANSACTIONS MOVED TO TARGET ACCOUNT\n\n" %(GlobalVars.countTxnsMoved)
                    del lAutoForceSaveTrunkFile

                    if lAnyCostBasisErrorsFound[0]:
                        txt = "%s: from %s to %s completed. NOTE: You have Lot Control errors >> please review log and check the results..." %(_THIS_METHOD_NAME, sourceAccount, targetAccount)
                        optionColor = "R"
                        optionFlag = JOptionPane.WARNING_MESSAGE
                    else:
                        txt = "%s: from %s to %s successfully completed (%s txns moved) - please review log and check the results..." %(_THIS_METHOD_NAME, sourceAccount, targetAccount, GlobalVars.countTxnsMoved)
                        optionColor = "DG"
                        optionFlag = JOptionPane.INFORMATION_MESSAGE

                    myPrint("B", txt); output += "\n\n%s\n" %(txt)
                    output += "\n\n *** PLEASE CHECK YOUR PORTFOLIO VIEW & REPORTS TO BALANCES ***\n\n"
                    output += "\n<END>"

                except:
                    txt = ("ERROR - %s crashed after the move/merge. Please review output, console, and VERIFY YOUR DATASET!" %(_THIS_METHOD_NAME)).upper()
                    myPrint("B",txt); output += "\n\n\n%s\n\n" %(txt)
                    output += dump_sys_error_to_md_console_and_errorlog(True)
                    setDisplayStatus(txt, "R")
                    jif = QuickJFrame("ERROR - %s:" %(_THIS_METHOD_NAME.upper()),output,copyToClipboard=GlobalVars.lCopyAllToClipBoard_TB,lWrapText=False).show_the_frame()
                    myPopupInformationBox(jif,txt,theMessageType=JOptionPane.ERROR_MESSAGE)
                    return

                jif = QuickJFrame("%s COMPLETED:" %(_THIS_METHOD_NAME.upper()),output,copyToClipboard=GlobalVars.lCopyAllToClipBoard_TB,lWrapText=False).show_the_frame()
                setDisplayStatus(txt, optionColor)
                play_the_money_sound()
                myPopupInformationBox(jif,txt,theMessageType=optionFlag)

                myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
                return

            move_merge_investment_txns()


        myPrint("B","FINISHED....")
        cleanup_actions()

    except QuickAbortThisScriptException:
        myPrint("DB", "Caught Exception: QuickAbortThisScriptException... Doing nothing...")

    except:
        crash_txt = ("ERROR - %s has crashed. Please review MD Menu>Help>Console Window for details" %(myModuleID)).upper()
        myPrint("B",crash_txt)
        crash_output = dump_sys_error_to_md_console_and_errorlog(True)
        jifr = QuickJFrame("ERROR - %s:" %(myModuleID),crash_output).show_the_frame()
        myPopupInformationBox(jifr,crash_txt,theMessageType=JOptionPane.ERROR_MESSAGE)

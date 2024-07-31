#!/usr/bin/env python
#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# toolbox_zap_mdplus_ofx_qif_default_memo_fields.py build: 1006 - July 2024 - Stuart Beesley StuWareSoftSystems

###############################################################################
# MIT License
#
# Copyright (c) 2020-2024 Stuart Beesley - StuWareSoftSystems
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
# build: 1001 - Renamed to toolbox_zap_mdplus_ofx_default_memo_fields.py - now fixes OFX too...
# build: 1002 - Added LocalStorage preferences, popup config, manual download imports, extra Memo options with popup GUI
# build: 1002 - Renamed to toolbox_zap_mdplus_ofx_qif_default_memo_fields.py - now includes QIF too...
# build: 1003 - Fix held references to MD Objects...
# build: 1004 - Common code - FileFilter fix...
# build: 1005 - MyJFrame(v5)
# build: 1006 - MD2024.2(5142) - moneydance_extension_loader was nuked and moneydance_this_fm with getResourceAsStream() was provided.

# Iterates previous x month's md+/ofx/qif transactions across Bank, Credit Card, Investment accounts and zaps the Memo field
# where it matches certain rules...

# CUSTOMIZE AND COPY THIS ##############################################################################################
# CUSTOMIZE AND COPY THIS ##############################################################################################
# CUSTOMIZE AND COPY THIS ##############################################################################################

# SET THESE LINES
myModuleID = u"toolbox_zap_mdplus_ofx_qif_default_memo_fields"
version_build = "1006"
MIN_BUILD_REQD = 4040                 # 2022.2 MD+ builds
_I_CAN_RUN_AS_DEVELOPER_CONSOLE_SCRIPT = False

global moneydance, moneydance_ui, moneydance_extension_loader, moneydance_extension_parameter, moneydance_this_fm

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

global toolbox_zap_mdplus_ofx_qif_default_memo_fields_frame_
# SET LINES ABOVE ^^^^

# COPY >> START
import __builtin__ as builtins

def checkObjectInNameSpace(objectName):
    """Checks globals() and builtins for the existence of the object name (used for StuWareSoftSystems' bootstrap)"""
    if objectName is None or not isinstance(objectName, basestring) or objectName == u"": return False
    if objectName in globals(): return True
    return objectName in dir(builtins)


if MD_REF is None: raise Exception(u"CRITICAL ERROR - moneydance object/variable is None?")

if checkObjectInNameSpace(u"moneydance_this_fm"):
    MD_EXTENSION_LOADER = moneydance_this_fm
else:
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
        self.myJFrameVersion = 5
        self.isActiveInMoneydance = False
        self.isRunTimeExtension = False
        self.MoneydanceAppListener = None
        self.HomePageViewObj = None

    def dispose(self):
        # This removes all content as Java/Swing (often) retains the JFrame reference in memory...
        # The try/exceptions are needed to ensure we actually get a dispose occurring...
        if self.disposing: return
        try:
            self.disposing = True
            try: self.getContentPane().removeAll()
            except: _msg = "%s: ERROR in .removeAll() WHILST DISPOSING FRAME: %s\n" %(myModuleID, self); print(_msg); System.err.write(_msg)
            if self.getJMenuBar() is not None:
                try: self.setJMenuBar(None)
                except: _msg = "%s: ERROR  in .setJMenuBar(None) WHILST DISPOSING FRAME: %s\n" %(myModuleID, self); print(_msg); System.err.write(_msg)
            rootPane = self.getRootPane()
            if rootPane is not None:
                try:
                    rootPane.getInputMap().clear()
                    rootPane.getActionMap().clear()
                except: _msg = "%s: ERROR in .getInputMap().clear() / .getActionMap().clear() WHILST DISPOSING FRAME: %s\n" %(myModuleID, self); print(_msg); System.err.write(_msg)
            super(self.__class__, self).dispose()
            # if True: _msg = "%s: SUCCESSFULLY DISPOSED FRAME: %s\n" %(myModuleID, self); print(_msg); System.err.write(_msg)
        except:
            _msg = "%s: ERROR DISPOSING OF FRAME: %s\n" %(myModuleID, self); print(_msg); System.err.write(_msg)
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
            and (isinstance(toolbox_zap_mdplus_ofx_qif_default_memo_fields_frame_, MyJFrame)                 # EDIT THIS
                 or type(toolbox_zap_mdplus_ofx_qif_default_memo_fields_frame_).__name__ == u"MyCOAWindow")  # EDIT THIS
            and toolbox_zap_mdplus_ofx_qif_default_memo_fields_frame_.isActiveInMoneydance):                 # EDIT THIS
        frameToResurrect = toolbox_zap_mdplus_ofx_qif_default_memo_fields_frame_                             # EDIT THIS
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

elif not _I_CAN_RUN_AS_DEVELOPER_CONSOLE_SCRIPT and u"__file__" in globals():
    msg = "%s: Sorry - this script cannot be run in Developer Console. Please install mxt and run extension properly. Must be on build: %s onwards. Now exiting script!\n" %(myModuleID, MIN_BUILD_REQD)
    print(msg); System.err.write(msg)
    try: MD_REF_UI.showInfoMessage(msg)
    except: raise Exception(msg)

elif not _I_CAN_RUN_AS_DEVELOPER_CONSOLE_SCRIPT and not checkObjectInNameSpace(u"moneydance_extension_loader")\
        and not checkObjectInNameSpace(u"moneydance_this_fm"):
    msg = "%s: Error - moneydance_extension_loader or moneydance_this_fm seems to be missing? Must be on build: %s onwards. Now exiting script!\n" %(myModuleID, MIN_BUILD_REQD)
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
    from com.infinitekind.moneydance.model import AbstractTxn

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

    # END SET THESE VARIABLES FOR ALL SCRIPTS ##########################################################################

    # >>> THIS SCRIPT'S IMPORTS ########################################################################################
    from java.lang import Long, StringBuilder
    from com.moneydance.awt import AwtUtil
    from com.infinitekind.moneydance.online import OnlineTxnMerger
    from com.infinitekind.moneydance.model import DateRange
    from com.moneydance.apps.md.view.gui import MDUndoManager
    from org.apache.commons.lang3 import StringEscapeUtils
    # >>> END THIS SCRIPT'S IMPORTS ####################################################################################

    # >>> THIS SCRIPT'S GLOBALS ########################################################################################
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
The author has other useful Extensions / 'Developer Console' Python scripts available...:

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

        myPrint("DB", "... destroying own reference to frame('toolbox_zap_mdplus_ofx_qif_default_memo_fields_frame_')...")
        global toolbox_zap_mdplus_ofx_qif_default_memo_fields_frame_
        toolbox_zap_mdplus_ofx_qif_default_memo_fields_frame_ = None
        del toolbox_zap_mdplus_ofx_qif_default_memo_fields_frame_


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
            # type: (File, str) -> bool
            if filename is not None and filename.upper().endswith(self.ext): return True
            return False

    class ExtFileFilterJFC(FileFilter):
        """File extension filter for JFileChooser"""
        def __init__(self, ext): self.ext = "." + ext.upper()

        def getDescription(self): return "*"+self.ext                                                                   # noqa

        def accept(self, _theFile):                                                                                     # noqa
            # type: (File) -> bool
            if _theFile is None: return False
            if _theFile.isDirectory(): return True
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

        if not Platform.isOSX() and lForceFD and not fileChooser_selectFiles:
            myPrint("DB", "@@ Overriding lForceFD to False - as it won't work for selecting Folders on Windows/Linux!")
            lForceFD = False

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

            _label2 = JLabel(pad("StuWareSoftSystems (2020-2024)", 800))
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
        myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()" )
        myPrint("DB", "Loading variables into memory...")

        if GlobalVars.parametersLoadedFromFile is None: GlobalVars.parametersLoadedFromFile = {}

        # >>> THESE ARE THIS SCRIPT's PARAMETERS TO LOAD

        myPrint("DB","parametersLoadedFromFile{} set into memory (as variables).....:", GlobalVars.parametersLoadedFromFile)
        return

    # >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
    def dump_StuWareSoftSystems_parameters_from_memory():
        # NOTE: Parameters were loaded earlier on... Preserve existing, and update any used ones...
        # (i.e. other StuWareSoftSystems programs might be sharing the same file)

        if GlobalVars.parametersLoadedFromFile is None: GlobalVars.parametersLoadedFromFile = {}

        # >>> THESE ARE THIS SCRIPT's PARAMETERS TO SAVE

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

        # try:
        #     MD_REF.getUI().setStatus(">> StuWareSoftSystems - finished.." %(GlobalVars.thisScriptName),0)
        # except:
        #     pass  # If this fails, then MD is probably shutting down.......

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


    def padTruncateWithDots(theText, theLength, padChar=u" ", stripSpaces=True, padString=True):
        if not isinstance(theText, basestring): theText = safeStr(theText)
        if theLength < 1: return ""
        if stripSpaces: theText = theText.strip()
        dotChop = min(3, theLength) if (len(theText) > theLength) else 0
        if padString:
            theText = (theText[:theLength-dotChop] + ("." * dotChop)).ljust(theLength, padChar)
        else:
            theText = (theText[:theLength-dotChop] + ("." * dotChop))
        return theText

    class JTextFieldIntDocument(PlainDocument):

        def __init__(self):
            super(self.__class__, self).__init__()

        def insertString(self, theOffset, theStr, theAttr):
            if theStr is not None:
                theStr = theStr.replace(" ", "")
                currentBufferLength = self.getLength()
                currentBufferContent = self.getText(0, currentBufferLength)

                if (currentBufferLength == 0):
                    newString = theStr
                else:
                    newString = StringBuilder(currentBufferContent).insert(theOffset, theStr).toString()

                if newString[:1] == "-": newString = newString[1:]
                if newString == "" or newString.isnumeric():
                    super(self.__class__, self).insertString(theOffset, theStr, theAttr)

    def html_strip_chars(_textToStrip):
        _textToStrip = StringEscapeUtils.escapeHtml4(_textToStrip)
        _textToStrip = _textToStrip.replace("  ","&nbsp;&nbsp;")
        return _textToStrip

    def wrap_HTML_wrapper(wrapperCharacter, _textToWrap, stripChars=True, addHTML=True):
        newText = "<%s>%s</%s>" %(wrapperCharacter, _textToWrap if not stripChars else html_strip_chars(_textToWrap), wrapperCharacter)
        if addHTML: newText = wrap_HTML(newText, stripChars=False)
        return newText

    def wrap_HTML_fontColor(_fontColorHexOrColor, _textToWrap, stripChars=True, addHTML=True):
        wrapperCharacter = "font"
        if isinstance(_fontColorHexOrColor, Color):
            _fontColorHexOrColor = AwtUtil.hexStringForColor(_fontColorHexOrColor)
        elif (isinstance(_fontColorHexOrColor, basestring)
                and (_fontColorHexOrColor.startswith("#") and len(_fontColorHexOrColor) == 7)):
            pass
        else: raise Exception("Invalid hex color specified!", _fontColorHexOrColor)

        newText = "<%s color=#%s>%s</%s>" %(wrapperCharacter, _fontColorHexOrColor, _textToWrap if not stripChars else html_strip_chars(_textToWrap), wrapperCharacter)
        if addHTML: newText = wrap_HTML(newText, stripChars=False)
        return newText

    def wrap_HTML(_textToWrap, stripChars=True):
        return wrap_HTML_wrapper("html", _textToWrap, stripChars, addHTML=False)

    def wrap_HTML_bold(_textToWrap, stripChars=True, addHTML=True):
        return wrap_HTML_wrapper("b", _textToWrap, stripChars, addHTML)

    def wrap_HTML_underline(_textToWrap, stripChars=True, addHTML=True):
        return wrap_HTML_wrapper("u", _textToWrap, stripChars, addHTML)

    def wrap_HTML_small(_textToWrap, stripChars=True, addHTML=True):
        return wrap_HTML_wrapper("small", _textToWrap, stripChars, addHTML)

    def wrap_HTML_italics(_textToWrap, stripChars=True, addHTML=True):
        return wrap_HTML_wrapper("i", _textToWrap, stripChars, addHTML)

    def wrap_HTML_BIG_small(_bigText, _smallText, _smallColor=None, stripBigChars=True, stripSmallChars=True, _bigColor=None, _italics=False, _bold=False, _underline=False, _html=False, _smallItalics=False, _smallBold=False, _smallUnderline=False):
        if _html:
            htmlBigText = _bigText
        else:
            strippedBigText = html_strip_chars(_bigText) if stripBigChars else _bigText
            if _bigColor is not None:
                htmlBigText = wrap_HTML_fontColor(_bigColor, strippedBigText, stripChars=False, addHTML=False)
            else:
                htmlBigText = strippedBigText

            if (_bold): htmlBigText = wrap_HTML_bold(htmlBigText, stripChars=False, addHTML=False)
            if (_italics): htmlBigText = wrap_HTML_italics(htmlBigText, stripChars=False, addHTML=False)
            if (_underline): htmlBigText = wrap_HTML_underline(htmlBigText, stripChars=False, addHTML=False)

        if _smallColor is None: _smallColor = GlobalVars.CONTEXT.getUI().getColors().tertiaryTextFG
        _htmlSmallText = html_strip_chars(_smallText) if stripSmallChars else _smallText
        convertedSmallText = wrap_HTML_fontColor(_smallColor, _htmlSmallText, stripChars=False, addHTML=False)
        convertedSmallText = wrap_HTML_small(convertedSmallText, stripChars=False, addHTML=False)
        if (_smallBold): convertedSmallText = wrap_HTML_bold(convertedSmallText, stripChars=False, addHTML=False)
        if (_smallItalics): convertedSmallText = wrap_HTML_italics(convertedSmallText, stripChars=False, addHTML=False)
        if (_smallUnderline): convertedSmallText = wrap_HTML_underline(convertedSmallText, stripChars=False, addHTML=False)
        return wrap_HTML("%s%s" %(htmlBigText, convertedSmallText), stripChars=False)


    def stripTextOfCRLFTabs(_text):
        _text = _text.replace("\n", "*")
        _text = _text.replace("\t", "*")
        return _text

    GlobalVars.Strings.EXTENSION_QL_ID = "securityquoteload"
    GlobalVars.Strings.EXTENSION_QER_ID = "yahooqt"

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


    MD_REF.getUI().setStatus(">> StuWareSoftSystems - %s launching......." %(GlobalVars.thisScriptName),0)
    ####################################################################################################################
    try:

        if not SwingUtilities.isEventDispatchThread():
            myPrint("B","@@@ ERROR: This extension can only be run on the Swing EDT (contact the author)!")
            raise QuickAbortThisScriptException

        lDetectedBuddyRunning = False
        for checkFr in [u"toolbox", u"toolbox_move_merge_investment_txns", u"toolbox_total_selected_transactions", u"toolbox_zap_mdplus_ofx_qif_default_memo_fields"]:
            if getMyJFrame(checkFr) is not None:
                lDetectedBuddyRunning = True

        toolbox_zap_mdplus_ofx_qif_default_memo_fields_frame_ = MyJFrame()
        toolbox_zap_mdplus_ofx_qif_default_memo_fields_frame_.setName(u"%s_main" %(myModuleID))
        if (not Platform.isMac()):
            MD_REF.getUI().getImages()
            toolbox_zap_mdplus_ofx_qif_default_memo_fields_frame_.setIconImage(MDImages.getImage(MD_REF.getSourceInformation().getIconResource()))
        toolbox_zap_mdplus_ofx_qif_default_memo_fields_frame_.setVisible(False)
        toolbox_zap_mdplus_ofx_qif_default_memo_fields_frame_.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE)
        myPrint("DB","Main JFrame %s for application created.." %(toolbox_zap_mdplus_ofx_qif_default_memo_fields_frame_.getName()))

        lRunningFromToolboxOverride = False

        lRunningFromToolbox = False
        if u"toolbox_script_runner" in globals():
            global toolbox_script_runner
            myPrint("B","Toolbox script runner detected: %s (build: %s)" %(toolbox_script_runner, version_build))
            lRunningFromToolbox = True
        elif lDetectedBuddyRunning:
            # This (hopefully) means it's been called from the extensions menu as a 'buddy' extension to Toolbox. Both running will overwrite common variables
            msg = "Sorry. Only one of the Toolbox Extension menu scripts can run at once.. Shutting all down. Please try again"
            myPopupInformationBox(toolbox_zap_mdplus_ofx_qif_default_memo_fields_frame_, msg, "ALERT: Toolbox is running", JOptionPane.WARNING_MESSAGE)
            myPrint("B", msg)
            destroyOldFrames(u"toolbox")
            raise QuickAbortThisScriptException

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

        def doMain():
            global debug
            global toolbox_zap_mdplus_ofx_qif_default_memo_fields_frame_

            def getOlMemo(_txn): return txn.getParameter(ORIG_MEMO_TAG, "")

            book = MD_REF.getCurrentAccountBook()
            if book is None:
                myPrint("B","@@@ ERROR: There appears to be no dataset open?! @@")
                raise QuickAbortThisScriptException
            if isinstance(book, AccountBook): pass

            # base = book.getCurrencies().getBaseType()
            # ct = book.getCurrencies()

            extnPrefs = getExtensionDatasetSettings()

            __THIS_METHOD_NAME = "Zap (or swap) md+/ofx/qif memo fields:"

            myPrint("B", ">> '%s' feature activated...." %(myModuleID))


            if not perform_qer_quote_loader_check(toolbox_zap_mdplus_ofx_qif_default_memo_fields_frame_, __THIS_METHOD_NAME):
                raise QuickAbortThisScriptException


            # Remove old key....
            OLD_LS_LOOKBACK_KEY = "toolbox_zap_mdplus_ofx_default_memo_fields_lookback_months"
            MD_REF.getCurrentAccountBook().getLocalStorage().put(OLD_LS_LOOKBACK_KEY, None)

            GlobalVars.UNSTICKY_SOME_KEYS_WHEN_ALL_ACCOUNTS = True

            GlobalVars.DEFAULT_LOOKBACK_MONTHS = 36

            GlobalVars.EXTN_PREF_KEY_SELECTED_ACCOUNT = "selected_account"
            GlobalVars.EXTN_PREF_KEY_LOOKBACK_MONTHS = "lookback_months"
            GlobalVars.EXTN_PREF_KEY_INCLUDE_MDP = "include_mdp"
            GlobalVars.EXTN_PREF_KEY_INCLUDE_OFX = "include_ofx"
            GlobalVars.EXTN_PREF_KEY_INCLUDE_IMPORTED_OFX = "include_imported_ofx"
            GlobalVars.EXTN_PREF_KEY_INCLUDE_DOWNLOADED_QIF = "include_downloaded_qif"
            GlobalVars.EXTN_PREF_KEY_INCLUDE_NON_DOWNLOADED_QIF = "include_non_downloaded_qif"
            GlobalVars.EXTN_PREF_KEY_INCLUDE_UNRECONCILED = "include_unreconciled"
            GlobalVars.EXTN_PREF_KEY_INCLUDE_UNCONFIRMED = "include_unconfirmed"
            GlobalVars.EXTN_PREF_KEY_ZAP_MEMO_WHEN_SUBSET_DESC = "zap_memo_when_subset_desc"
            GlobalVars.EXTN_PREF_KEY_SWAP_MEMO_DESC_WHEN_SUBSET = "swap_memo_desc_when_subset"
            GlobalVars.EXTN_PREF_KEY_OFX_QIF_DONT_CHECK_ORIGINAL_MEMO = "ofx_qif_dont_check_original_memo"
            GlobalVars.EXTN_PREF_KEY_OFX_QIF_DONT_COMPARE_WITH_DESC = "ofx_qif_dont_compare_with_desc"
            GlobalVars.EXTN_PREF_KEY_SHOWN_HELPFILE = "shown_helpfile"

            def setExtnParam_selected_account(prefs, selectedAcct):
                # type: (SyncRecord, Account) -> None
                uuid = "all" if (selectedAcct is None or not isinstance(selectedAcct, Account)) else selectedAcct.getUUID()
                prefs.put(GlobalVars.EXTN_PREF_KEY_SELECTED_ACCOUNT, uuid)

            def getExtnParam_selected_account():
                # type: () -> Account
                sAcctUUID = extnPrefs.getStr(GlobalVars.EXTN_PREF_KEY_SELECTED_ACCOUNT, "all")
                return MD_REF.getCurrentAccountBook().getAccountByUUID(sAcctUUID)

            def getExtnParam_selected_account_text():
                # type: () -> str
                sAcct =  getExtnParam_selected_account()
                return "ALL ACCOUNTS SELECTED" if sAcct is None else sAcct.getFullAccountName()

            def getExtnParam_account_key(_acct=None):
                rtnKey = "all"
                if isinstance(_acct, Account):
                    rtnKey = _acct.getUUID()
                return "_" + rtnKey

            def getExtnParam_lookbackMonths(_acct): return extnPrefs.getInt(GlobalVars.EXTN_PREF_KEY_LOOKBACK_MONTHS + getExtnParam_account_key(_acct), GlobalVars.DEFAULT_LOOKBACK_MONTHS)
            def getExtnParam_include_mdp(_acct): return extnPrefs.getBoolean(GlobalVars.EXTN_PREF_KEY_INCLUDE_MDP + getExtnParam_account_key(_acct), False)
            def getExtnParam_include_ofx(_acct): return extnPrefs.getBoolean(GlobalVars.EXTN_PREF_KEY_INCLUDE_OFX + getExtnParam_account_key(_acct), False)
            def getExtnParam_imported_ofx(_acct): return extnPrefs.getBoolean(GlobalVars.EXTN_PREF_KEY_INCLUDE_IMPORTED_OFX + getExtnParam_account_key(_acct), False)
            def getExtnParam_downloaded_qif(_acct): return extnPrefs.getBoolean(GlobalVars.EXTN_PREF_KEY_INCLUDE_DOWNLOADED_QIF + getExtnParam_account_key(_acct), False)
            def getExtnParam_non_downloaded_qif(_acct): return extnPrefs.getBoolean(GlobalVars.EXTN_PREF_KEY_INCLUDE_NON_DOWNLOADED_QIF + getExtnParam_account_key(_acct), False)
            def getExtnParam_include_unreconciled(_acct): return extnPrefs.getBoolean(GlobalVars.EXTN_PREF_KEY_INCLUDE_UNRECONCILED + getExtnParam_account_key(_acct), False)
            def getExtnParam_include_unconfirmed(_acct): return extnPrefs.getBoolean(GlobalVars.EXTN_PREF_KEY_INCLUDE_UNCONFIRMED + getExtnParam_account_key(_acct), False)
            def getExtnParam_zap_memo_when_subset_desc(_acct): return extnPrefs.getBoolean(GlobalVars.EXTN_PREF_KEY_ZAP_MEMO_WHEN_SUBSET_DESC + getExtnParam_account_key(_acct), False)
            def getExtnParam_swap_memo_desc_when_subset(_acct): return extnPrefs.getBoolean(GlobalVars.EXTN_PREF_KEY_SWAP_MEMO_DESC_WHEN_SUBSET + getExtnParam_account_key(_acct), False)
            def getExtnParam_ofx_qif_dont_check_original_memo(_acct): return extnPrefs.getBoolean(GlobalVars.EXTN_PREF_KEY_OFX_QIF_DONT_CHECK_ORIGINAL_MEMO + getExtnParam_account_key(_acct), False)
            def getExtnParam_ofx_qif_dont_compare_with_desc(_acct): return extnPrefs.getBoolean(GlobalVars.EXTN_PREF_KEY_OFX_QIF_DONT_COMPARE_WITH_DESC + getExtnParam_account_key(_acct), False)
            def getExtnParam_shown_helpfile(): return extnPrefs.getBoolean(GlobalVars.EXTN_PREF_KEY_SHOWN_HELPFILE, False)

            ################################################################################################################
            GlobalVars.helpFileData = None
            if MD_EXTENSION_LOADER:
                try:
                    GlobalVars.helpFileData = load_text_from_stream_file(MD_EXTENSION_LOADER.getResourceAsStream("/%s_readme.txt" %(myModuleID)))
                    myPrint("DB","Contents loaded from /%s_readme.txt" %(myModuleID))
                except:
                    myPrint("B","@@ Error loading contents from /%s_readme.txt" %(myModuleID))

            if not getExtnParam_shown_helpfile():
                QuickJFrame("%s: Help / guide (FIRST EXECUTION OF UTILITY)" %(myModuleID), GlobalVars.helpFileData, lWrapText=False, lAutoSize=True).show_the_frame()
                extnPrefs.put(GlobalVars.EXTN_PREF_KEY_SHOWN_HELPFILE, True)
                saveExtensionDatasetSettings(extnPrefs)
                raise QuickAbortThisScriptException
            ################################################################################################################

            _allActiveAccounts = sorted(AccountUtil.allMatchesForSearch(MD_REF.getCurrentAccountBook(), AcctFilter.ACTIVE_ACCOUNTS_FILTER), key=lambda sort_x: (sort_x.getAccountType(), sort_x.getFullAccountName().lower()))
            allActiveAccounts = [acct for acct in _allActiveAccounts if acct.getAccountType() in [Account.AccountType.BANK, Account.AccountType.CREDIT_CARD, Account.AccountType.INVESTMENT]]   # noqa

            if len(allActiveAccounts) < 1:
                myPopupInformationBox(toolbox_zap_mdplus_ofx_qif_default_memo_fields_frame_, "You have no active Bank, Credit Card, Investment accounts!?", theTitle=__THIS_METHOD_NAME.upper(), theMessageType=JOptionPane.WARNING_MESSAGE)
                raise QuickAbortThisScriptException

            class StoreAccount:
                def __init__(self, _acct):
                    if isinstance(_acct, Account): pass
                    self.acct = _acct

                def getAccount(self): return self.acct

                def __str__(self):
                    _acct = self.getAccount()
                    if _acct is None:
                        acctStr = "ALL active bank, credit card, investment accts"
                    else:
                        acctStr = "%s : %s" %(_acct.getAccountType(), _acct.getFullAccountName())
                    return acctStr
                def __repr__(self):         return self.__str__()
                def toString(self):         return self.__str__()

            acctsForSelector = [StoreAccount(acct) for acct in allActiveAccounts]
            acctsForSelector.insert(0, StoreAccount(None))

            # Popup Parameters ###########################################

            def getAccountFromJComboBox(_jcb):
                if not isinstance(_jcb, JComboBox): raise Exception("ERROR: _jcb is NOT a JComboBox!?")
                _selectedObj = _jcb.getSelectedItem()
                if isinstance(_selectedObj, StoreAccount): pass
                return None if _selectedObj is None else _selectedObj.getAccount()

            label_selectAccount = JLabel("Select single account (or all)")
            user_acctSelector = JComboBox(acctsForSelector)
            previousSelectedAccount = getExtnParam_selected_account()
            for storeAccount in acctsForSelector:
                if storeAccount.getAccount() == previousSelectedAccount:
                    user_acctSelector.setSelectedItem(storeAccount)

            label_lookbackMonths = JLabel("How many months to look back")
            user_lookbackMonths = JTextField(6)
            user_lookbackMonths.setDocument(JTextFieldIntDocument())

            label_include_unreconciled = JLabel("Include unreconciled transactions (else only reconciled)")
            user_include_unreconciled = JCheckBox("")

            label_include_unconfirmed = JLabel("Include unconfirmed transactions (only applies where 'downloaded')")
            user_include_unconfirmed = JCheckBox("(check bypassed on 'QIF-')")

            label_include_mdp = JLabel("Include md+ downloaded txns >> ALWAYS zap md+ memo fields")
            user_include_mdp = JCheckBox("'MD+' (Moneydance downloads (via Plaid))")
            user_include_mdp.setForeground(getColorBlue())

            label_include_ofx = JLabel("Include ofx downloaded memo fields")
            user_include_ofx = JCheckBox("'OFX+' (OFX 'Direct Connect' downloads)")
            user_include_ofx.setForeground(getColorBlue())

            label_include_imported_ofx = JLabel("Include file imported ofx memo fields")
            user_include_imported_ofx = JCheckBox("'OFX-' (manual .ofx / .qfx file downloads/imports)")
            user_include_imported_ofx.setForeground(getColorBlue())

            label_include_downloaded_qif = JLabel("Include downloaded / file imported QIF memo fields")
            user_include_downloaded_qif = JCheckBox("'QIF+' (manual .qif file downloads/imports)")
            user_include_downloaded_qif.setForeground(getColorBlue())

            label_include_non_downloaded_qif = JLabel("Include NON downloaded / file imported QIF memo fields")
            user_include_non_downloaded_qif = JCheckBox("'QIF-' (import of manual non-downloaded .qif file)")
            user_include_non_downloaded_qif.setForeground(getColorRed())

            label_zap_memo_when_subset_desc = JLabel("Zap unchanged memo when memo already within (longer) description")
            user_zap_memo_when_subset_desc = JCheckBox("")

            label_getExtnParam_swap_memo_desc_when_subset = JLabel("Swap memo into description when memo same but longer")
            user_getExtnParam_swap_memo_desc_when_subset = JCheckBox("")

            label_ofx_qif_dont_check_original_memo = JLabel("Don't check / compare the original downloaded memo first")
            user_ofx_qif_dont_check_original_memo = JCheckBox("(i.e. include manually edited memos; check bypassed on 'QIF-')")
            user_ofx_qif_dont_check_original_memo.setForeground(getColorRed())

            label_ofx_qif_dont_compare_with_desc = JLabel("Don't compare memo to description (just zap)")
            user_ofx_qif_dont_compare_with_desc = JCheckBox("(i.e. zap any memos that matches all other rules)")
            user_ofx_qif_dont_compare_with_desc.setForeground(getColorRed())

            label_DEBUG = JLabel("Enable DEBUG messages")
            user_DEBUG = JCheckBox("", debug)

            def updateSelectionsFromSavedSettings(_selectedAccount):
                stickySelection = True
                if GlobalVars.UNSTICKY_SOME_KEYS_WHEN_ALL_ACCOUNTS and _selectedAccount is None:
                    stickySelection = False

                user_lookbackMonths.setText(str(getExtnParam_lookbackMonths(_selectedAccount)))
                user_include_unreconciled.setSelected(getExtnParam_include_unreconciled(_selectedAccount))
                user_include_unconfirmed.setSelected(getExtnParam_include_unconfirmed(_selectedAccount))
                user_include_mdp.setSelected(getExtnParam_include_mdp(_selectedAccount))
                user_include_ofx.setSelected(getExtnParam_include_ofx(_selectedAccount))
                user_include_imported_ofx.setSelected(getExtnParam_imported_ofx(_selectedAccount))
                user_include_downloaded_qif.setSelected(getExtnParam_downloaded_qif(_selectedAccount))
                user_include_non_downloaded_qif.setSelected(False if not stickySelection else getExtnParam_non_downloaded_qif(_selectedAccount))
                user_zap_memo_when_subset_desc.setSelected(getExtnParam_zap_memo_when_subset_desc(_selectedAccount))
                user_getExtnParam_swap_memo_desc_when_subset.setSelected(getExtnParam_swap_memo_desc_when_subset(_selectedAccount))
                user_ofx_qif_dont_check_original_memo.setSelected(False if not stickySelection else getExtnParam_ofx_qif_dont_check_original_memo(_selectedAccount))
                user_ofx_qif_dont_compare_with_desc.setSelected(False if not stickySelection else getExtnParam_ofx_qif_dont_compare_with_desc(_selectedAccount))

            updateSelectionsFromSavedSettings(previousSelectedAccount)

            class WarningMessage(AbstractAction):
                def __init__(self, _dialog, _user_ofx_qif_dont_check_original_memo, _user_ofx_qif_dont_compare_with_desc):
                    self.dialog = _dialog
                    self.dont_check_original_memo = _user_ofx_qif_dont_check_original_memo
                    self.dont_compare_with_desc = _user_ofx_qif_dont_compare_with_desc
                    self.enableListener = True

                def setEnableListener(self, _enableListener): self.enableListener = _enableListener
                def isEnableListener(self,): return self.enableListener

                def actionPerformed(self, event):
                    if self.isEnabled():
                        option = event.getSource()
                        if isinstance(option, JCheckBox): pass
                        if option.isSelected():
                            if option is self.dont_check_original_memo:
                                _msg = "Are you sure? This will include Memos that you have changed!"
                            elif option is self.dont_compare_with_desc:
                                _msg = "Are you sure? This will ignore description and just zap the memo(s)!"
                            else: raise Exception("LOGIC ERROR: event unknown: %s; %s" %(option, event))
                            myPopupInformationBox(self.dialog,
                                                  _msg,
                                                  "WARNING",
                                                  JOptionPane.WARNING_MESSAGE)
                    else:
                        myPrint("DB", "@@ WarningMessage:: .actionPerformed() - disabled - doing nothing....")

            class CheckReloadSettings(AbstractAction):
                def __init__(self, _manageListener):
                    self.manageListener = _manageListener

                def actionPerformed(self, event):
                    option = event.getSource()
                    if isinstance(option, JComboBox): pass
                    myPrint("DB", "@@@ CheckReloadSettings:: .actionPerformed()", event, option)
                    if event.getActionCommand().lower() == "comboBoxChanged".lower():
                        self.manageListener.setEnableListener(False)
                        updateSelectionsFromSavedSettings(getAccountFromJComboBox(option))
                        self.manageListener.setEnableListener(True)

            class UpdateDebug(AbstractAction):
                def __init__(self): pass

                def actionPerformed(self, event):
                    global debug
                    debug = not debug
                    event.getSource().setSelected(debug)
                    myPrint("B", "@@ DEBUG now: %s" %("ON" if debug else "OFF"))

            userFilters = JPanel(GridLayout(0, 2))

            userFilters.add(JLabel(wrap_HTML_underline("Common options...:")))
            userFilters.add(JLabel(""))
            userFilters.add(label_selectAccount)
            userFilters.add(user_acctSelector)
            userFilters.add(label_lookbackMonths)
            userFilters.add(user_lookbackMonths)
            userFilters.add(label_include_unreconciled)
            userFilters.add(user_include_unreconciled)
            userFilters.add(label_include_unconfirmed)
            userFilters.add(user_include_unconfirmed)

            userFilters.add(JLabel(""))
            userFilters.add(JLabel(""))

            userFilters.add(JLabel(wrap_HTML_underline("MD+ options...:")))
            userFilters.add(JLabel(""))
            userFilters.add(label_include_mdp)
            userFilters.add(user_include_mdp)

            warnTxt = "NOTE: With md+ txns, this utility only/always zaps unchanged memo field(s)<br>" \
                      "... no other checks or changes (as per below) take place...."
            warnLbl = JLabel(wrap_HTML_italics(wrap_HTML_small(warnTxt, stripChars=False, addHTML=False), stripChars=False, addHTML=True))
            warnLbl.setForeground(getColorRed())
            userFilters.add(warnLbl)
            userFilters.add(JLabel(""))

            userFilters.add(JLabel(""))
            userFilters.add(JLabel(""))

            userFilters.add(JLabel(wrap_HTML_underline("OFX / QIF options...:")))
            userFilters.add(JLabel(""))
            userFilters.add(label_include_ofx)
            userFilters.add(user_include_ofx)
            userFilters.add(label_include_imported_ofx)
            userFilters.add(user_include_imported_ofx)
            userFilters.add(label_include_downloaded_qif)
            userFilters.add(user_include_downloaded_qif)
            userFilters.add(label_include_non_downloaded_qif)
            userFilters.add(user_include_non_downloaded_qif)
            userFilters.add(label_zap_memo_when_subset_desc)
            userFilters.add(user_zap_memo_when_subset_desc)
            userFilters.add(label_getExtnParam_swap_memo_desc_when_subset)
            userFilters.add(user_getExtnParam_swap_memo_desc_when_subset)

            userFilters.add(label_ofx_qif_dont_check_original_memo)
            userFilters.add(user_ofx_qif_dont_check_original_memo)

            warnTxt = "NOTE: On 'QIF-' txns there is no check as to whether the Memo field has been edited!"
            warnLbl = JLabel(wrap_HTML_italics(wrap_HTML_small(warnTxt, stripChars=False, addHTML=False), stripChars=False, addHTML=True))
            warnLbl.setForeground(getColorRed())
            userFilters.add(warnLbl)
            userFilters.add(JLabel(""))

            userFilters.add(label_ofx_qif_dont_compare_with_desc)
            userFilters.add(user_ofx_qif_dont_compare_with_desc)

            userFilters.add(JLabel(""))
            userFilters.add(JLabel(""))

            userFilters.add(JLabel(wrap_HTML_underline("Advanced options:")))
            userFilters.add(JLabel(""))
            userFilters.add(label_DEBUG)
            userFilters.add(user_DEBUG)

            options = ["Abort", "ANALYSE"]
            if GlobalVars.helpFileData: options.append("HELP/GUIDE")

            pane = JOptionPane()
            pane.setIcon(None)
            pane.setMessage(userFilters)
            pane.setMessageType(JOptionPane.QUESTION_MESSAGE)
            pane.setOptionType(JOptionPane.OK_CANCEL_OPTION)
            pane.setOptions(options)
            dlg = pane.createDialog(toolbox_zap_mdplus_ofx_qif_default_memo_fields_frame_, __THIS_METHOD_NAME)

            warnAlert = WarningMessage(dlg, user_ofx_qif_dont_check_original_memo, user_ofx_qif_dont_compare_with_desc)
            user_acctSelector.addActionListener(CheckReloadSettings(warnAlert))
            user_ofx_qif_dont_check_original_memo.addActionListener(warnAlert)
            user_ofx_qif_dont_compare_with_desc.addActionListener(warnAlert)
            user_DEBUG.addActionListener(UpdateDebug())

            dlg.setVisible(True)

            rtnValue = pane.getValue()

            userAction = -1
            for i in range(0, len(options)):
                if options[i] == rtnValue:
                    userAction = i
                    break

            if userAction < 1:
                myPrint("DB", "User exited - no action taken")
                raise QuickAbortThisScriptException

            if userAction > 1:
                QuickJFrame("%s: Help / guide" %(myModuleID), GlobalVars.helpFileData, lWrapText=False, lAutoSize=True).show_the_frame()
                raise QuickAbortThisScriptException

            userSelectedAcct = getAccountFromJComboBox(user_acctSelector)

            setExtnParam_selected_account(extnPrefs, userSelectedAcct)
            myPrint("DB", "Selected Account:", getExtnParam_selected_account_text())

            months = user_lookbackMonths.getText()
            if StringUtils.isEmpty(months): months = "-1"
            if StringUtils.isInteger(months) and int(months) > 0 and int(months) <= 600:
                months = int(months)
                myPrint("DB", "Months to look back set at: %s" %(months))
            else:
                months = GlobalVars.DEFAULT_LOOKBACK_MONTHS
                myPrint("DB", "Look back months invalid (should be 1 to 600 months) - defaulting to %s ...." %(GlobalVars.DEFAULT_LOOKBACK_MONTHS))
            extnPrefs.put(GlobalVars.EXTN_PREF_KEY_LOOKBACK_MONTHS + getExtnParam_account_key(getExtnParam_selected_account()), months)

            extnPrefs.put(GlobalVars.EXTN_PREF_KEY_INCLUDE_UNRECONCILED + getExtnParam_account_key(getExtnParam_selected_account()), user_include_unreconciled.isSelected())
            myPrint("DB", "Include unreconciled transactions (else only reconciled):", getExtnParam_include_unreconciled(getExtnParam_selected_account()))

            extnPrefs.put(GlobalVars.EXTN_PREF_KEY_INCLUDE_UNCONFIRMED + getExtnParam_account_key(getExtnParam_selected_account()), user_include_unconfirmed.isSelected())
            myPrint("DB", "Include unconfirmed transactions (else only confirmed):", getExtnParam_include_unconfirmed(getExtnParam_selected_account()), "(check bypassed on 'QIF-')")

            extnPrefs.put(GlobalVars.EXTN_PREF_KEY_INCLUDE_MDP + getExtnParam_account_key(getExtnParam_selected_account()), user_include_mdp.isSelected())
            myPrint("DB", "Include MD+ downloaded txns (and always zap memo field):", getExtnParam_include_mdp(getExtnParam_selected_account()))

            extnPrefs.put(GlobalVars.EXTN_PREF_KEY_INCLUDE_OFX + getExtnParam_account_key(getExtnParam_selected_account()), user_include_ofx.isSelected())
            myPrint("DB", "Include Downloaded OFX txns:", getExtnParam_include_ofx(getExtnParam_selected_account()))

            extnPrefs.put(GlobalVars.EXTN_PREF_KEY_INCLUDE_IMPORTED_OFX + getExtnParam_account_key(getExtnParam_selected_account()), user_include_imported_ofx.isSelected())
            myPrint("DB", "Include file imported OFX txns:", getExtnParam_imported_ofx(getExtnParam_selected_account()))

            extnPrefs.put(GlobalVars.EXTN_PREF_KEY_INCLUDE_DOWNLOADED_QIF + getExtnParam_account_key(getExtnParam_selected_account()), user_include_downloaded_qif.isSelected())
            myPrint("DB", "Include downloaded / file imported QIF txns:", getExtnParam_downloaded_qif(getExtnParam_selected_account()))

            extnPrefs.put(GlobalVars.EXTN_PREF_KEY_INCLUDE_NON_DOWNLOADED_QIF + getExtnParam_account_key(getExtnParam_selected_account()), user_include_non_downloaded_qif.isSelected())
            myPrint("DB", "Include NON downloaded / file imported QIF txns:", getExtnParam_non_downloaded_qif(getExtnParam_selected_account()))

            extnPrefs.put(GlobalVars.EXTN_PREF_KEY_ZAP_MEMO_WHEN_SUBSET_DESC + getExtnParam_account_key(getExtnParam_selected_account()), user_zap_memo_when_subset_desc.isSelected())
            myPrint("DB", "Zap unchanged memo when memo already within (longer) description:", getExtnParam_zap_memo_when_subset_desc(getExtnParam_selected_account()))

            extnPrefs.put(GlobalVars.EXTN_PREF_KEY_SWAP_MEMO_DESC_WHEN_SUBSET + getExtnParam_account_key(getExtnParam_selected_account()), user_getExtnParam_swap_memo_desc_when_subset.isSelected())
            myPrint("DB", "Swap memo into description when memo same but longer:", getExtnParam_swap_memo_desc_when_subset(getExtnParam_selected_account()))

            extnPrefs.put(GlobalVars.EXTN_PREF_KEY_OFX_QIF_DONT_CHECK_ORIGINAL_MEMO + getExtnParam_account_key(getExtnParam_selected_account()), user_ofx_qif_dont_check_original_memo.isSelected())
            myPrint("DB", "Don't check / compare the original downloaded memo first:", getExtnParam_ofx_qif_dont_check_original_memo(getExtnParam_selected_account()), "(i.e. include manually edited memos; check bypassed on 'QIF-')")

            extnPrefs.put(GlobalVars.EXTN_PREF_KEY_OFX_QIF_DONT_COMPARE_WITH_DESC + getExtnParam_account_key(getExtnParam_selected_account()), user_ofx_qif_dont_compare_with_desc.isSelected())
            myPrint("DB", "Don't compare memo to description (just zap):", getExtnParam_ofx_qif_dont_compare_with_desc(getExtnParam_selected_account()), "(i.e. zap any memos that matches all other rules)")

            debug = user_DEBUG.isSelected()
            myPrint("DB", "@@ DEBUG IS ON @@")
            ############################################


            myPrint("DB", "Saving Extension's parameters...")
            saveExtensionDatasetSettings(extnPrefs)

            if (not getExtnParam_include_mdp(getExtnParam_selected_account()) and not getExtnParam_include_ofx(getExtnParam_selected_account()) and not getExtnParam_imported_ofx(getExtnParam_selected_account())
                    and not getExtnParam_downloaded_qif(getExtnParam_selected_account()) and not getExtnParam_non_downloaded_qif(getExtnParam_selected_account())):
                myPopupInformationBox(toolbox_zap_mdplus_ofx_qif_default_memo_fields_frame_, "NOTHING TO DO!?", theTitle=__THIS_METHOD_NAME.upper(), theMessageType=JOptionPane.INFORMATION_MESSAGE)
                raise QuickAbortThisScriptException

            class StoreTxn:
                def __init__(self, _isMDP, _isOFX, _isImportedOFX, _isDownloadedQIF, _isNonDownloadedQIF, _txn):
                    if not isinstance(_txn, ParentTxn): raise Exception("ERROR: StoreTxn requires a ParentTxn: was passed: '%s'" %(_txn))
                    self.isMDP = _isMDP
                    self.isOFX = _isOFX
                    self.isImportedOFX = _isImportedOFX
                    self.isDownloadedQIF = _isDownloadedQIF
                    self.isNonDownloadedQIF = _isNonDownloadedQIF
                    self.txn = _txn                                                                                         # type: ParentTxn
                    self.newDesc = None
                    self.newMemo = None
                    self.swapMarker = ""
                    self.olTypeText = self.deriveOlTypeTxt()

                def setSwapMarker(self, newMarker): self.swapMarker = newMarker
                def getSwapMarker(self): return self.swapMarker

                def getOlType(self): return self.olTypeText

                def deriveOlTypeTxt(self):
                    if self.isMDP:
                        txt = "MD+"
                    elif self.isOFX:
                        txt = "OFX+"
                    elif self.isImportedOFX:
                        txt = "OFX-"
                    elif self.isDownloadedQIF:
                        txt = "QIF+"
                    elif self.isNonDownloadedQIF:
                        txt = "QIF-"
                    else:
                        txt = "<??>"
                    return txt

                def willZapMemo(self): return self.getNewMemo() is not None
                def willSwapDesc(self): return self.getNewDesc() is not None

                def getTxn(self): return self.txn
                def getNewMemo(self): return self.newMemo
                def getNewDesc(self): return self.newDesc
                def __str__(self):          return self.getTxn().toString()
                def __repr__(self):         return self.__str__()
                def toString(self):         return self.__str__()

            MD_decimal = MD_REF.getPreferences().getDecimalChar()

            _msgPad = 100
            _msgx = pad("Zap (or swap) memo fields:".upper() + " Please wait: processing..", _msgPad, padChar=".")
            pleaseWait = MyPopUpDialogBox(toolbox_zap_mdplus_ofx_qif_default_memo_fields_frame_,
                                          theStatus=_msgx,
                                          theTitle=_msgx.upper(),
                                          lModal=False,
                                          OKButtonText="WAIT")
            pleaseWait.go()

            try:

                lookbackMonths = getExtnParam_lookbackMonths(getExtnParam_selected_account())

                ORIG_MEMO_TAG = OnlineTxnMerger.ORIG_MEMO_TAG
                OL_MATCH_STATUS_TAG = AbstractTxn.TAG_IS_NEW_TXN
                ORIG_TXN_DATA = getFieldByReflection(AbstractTxn, "ORIG_TXN_TAG")
                QIF_NON_DOWNLOADED_IMPORT = "qif.orig-txn"     # txn.getParameter("qif.orig-txn", "")
                OFX_IMPORT_TAG_MARKER = "<STMTTRN>"

                startDate = DateUtil.incrementDate(DateUtil.convertDateToInt(DateUtil.firstDayInMonth(DateUtil.getStrippedDateObj())), 0, -lookbackMonths, 0)
                endDate = DateUtil.getStrippedDateInt()
                dateRange = DateRange(Integer(startDate), Integer(endDate))

                dateTxt = "%s Date range: Start: %s, End: %s (%s months)" %(__THIS_METHOD_NAME,
                                                                            convertStrippedIntDateFormattedText(startDate),
                                                                            convertStrippedIntDateFormattedText(endDate),
                                                                            lookbackMonths)
                myPrint("B", dateTxt)

                txnsWithMemos = []
                accountsInvolved = {}

                outputTxt = "Transactions where md+/ofx/qif txns' memo field matches the rules chosen:\n" \
                            "-------------------------------------------------------------------------\n\n" \
                            "CANDIDATES TO ZAP (OR SWAP) MEMO FIELD:\n\n"

                outputTxt += "%s\n\n" %(dateTxt)

                iCountPotentialDescMemoSwaps = 0
                iCountBlankDescSwapsWarning = 0

                targetAccount = getExtnParam_selected_account()

                for acct in allActiveAccounts:
                    if isinstance(acct, Account): pass

                    if acct.getAccountType() not in [Account.AccountType.BANK, Account.AccountType.CREDIT_CARD, Account.AccountType.INVESTMENT]:    # noqa
                        raise Exception("LOGIC ERROR: Found account type: '%s'" %(acct.getAccountType()))

                    if targetAccount is not None:
                        if acct != targetAccount: continue

                    _msgx = pad("Please wait: Account: '%s'" %(acct), _msgPad, padChar=".")
                    pleaseWait.updateMessages(newTitle=_msgx, newStatus=_msgx)

                    myPrint("DB", "Account: '%s' (%s)" %(acct, acct.getAccountType()))

                    ts = acct.getBook().getTransactionSet()
                    txns = ts.getTransactions(TxnUtil.getSearch(acct, dateRange))

                    myPrint("DB", "Found %s txns.." %(txns.getSize()))

                    for txn in txns:
                        if not isinstance(txn, ParentTxn): continue

                        isMDP = isOFX = isImportedOFX = isDownloadedQIF = isNonDownloadedQIF = False

                        fiid = txn.getFIID()
                        if fiid is None: fiid = ""

                        # if ((not txn.wasDownloaded() and not (fiid is None or fiid == ""))
                        #         or (txn.wasDownloaded() and (fiid is None or fiid == ""))):
                        #     myPrint("B", "@@@@ txn:", txn.getSyncInfo().toMultilineHumanReadableString())
                        #     raise Exception("LOGIC ERROR: illogical txn.wasDownloaded() vs .getFIID()? (REVIEW CONSOLE)")

                        if not txn.wasDownloaded():
                            if fiid == "":
                                isNonDownloadedQIF = txn.getParameter(QIF_NON_DOWNLOADED_IMPORT, "") != ""
                                if getExtnParam_non_downloaded_qif(getExtnParam_selected_account()) and isNonDownloadedQIF:
                                    fiid = "*"
                                else:
                                    continue
                            else:
                                myPrint("B", "@@@@ txn:", txn.getSyncInfo().toMultilineHumanReadableString())
                                raise Exception("LOGIC ERROR: illogical not txn.wasDownloaded() with txn.getFIID()? (REVIEW CONSOLE)")

                        txnMemo = txn.getMemo().strip().lower()                                                             # noqa
                        if txnMemo == "": continue

                        fiid_check = fiid.lower()
                        if "mdplus:" in fiid_check:
                            isMDP = True
                        elif "ofx:" in fiid_check:
                            isOFX = True
                        elif "qif" in fiid_check:
                            isDownloadedQIF = True

                        if not isMDP and not isOFX and not isDownloadedQIF and not isNonDownloadedQIF:
                            isImportedOFX = OFX_IMPORT_TAG_MARKER in txn.getParameter(ORIG_TXN_DATA, "").upper()

                        i = 0
                        for check in [isMDP, isOFX, isImportedOFX, isDownloadedQIF, isNonDownloadedQIF]:
                            i += (1 if (check) else 0)

                        if i > 1:
                            myPrint("B", "@@@@ txn:", txn.getSyncInfo().toMultilineHumanReadableString())
                            raise Exception("LOGIC ERROR: Seem to have detected multiple OL types (%s)? (REVIEW CONSOLE)"
                                            "isMDP: %s, isOFX: %s, isImportedOFX: %s, isDownloadedQIF: %s, isNonDownloadedQIF: %s"
                                            %(i, isMDP, isOFX, isImportedOFX, isDownloadedQIF, isNonDownloadedQIF))
                        elif i < 1:
                            continue

                        if isMDP and not getExtnParam_include_mdp(getExtnParam_selected_account()): continue
                        if isOFX and not getExtnParam_include_ofx(getExtnParam_selected_account()): continue
                        if isImportedOFX and not getExtnParam_imported_ofx(getExtnParam_selected_account()): continue
                        if isDownloadedQIF and not getExtnParam_downloaded_qif(getExtnParam_selected_account()): continue
                        if isNonDownloadedQIF and not getExtnParam_non_downloaded_qif(getExtnParam_selected_account()): continue

                        storeTxn = StoreTxn(isMDP, isOFX, isImportedOFX, isDownloadedQIF, isNonDownloadedQIF, txn)
                        olTypeTxt = storeTxn.getOlType()

                        # Ignore un-reconciled txns...
                        if (not getExtnParam_include_unreconciled(getExtnParam_selected_account())
                                and txn.getClearedStatus() != AbstractTxn.ClearedStatus.CLEARED):                           # noqa
                            continue

                        # Ignore non-cleared txns... (manual QIF files do not have this setting)....
                        if not isNonDownloadedQIF:
                            if (not getExtnParam_include_unconfirmed(getExtnParam_selected_account())
                                    and txn.getBooleanParameter(OL_MATCH_STATUS_TAG, False)):
                                continue

                        # The fix is slightly different for MD+, OFX and QIF. With MD+ the Memo is usually 'junk' / irrelevant
                        # .. but for OFX, only remove Memo if identical to Description... QIF depends if downloaded or manual...

                        olMemo = getOlMemo(txn).strip().lower()                                                             # noqa

                        mustCheckAgainstOlMemo = True
                        if not isMDP:
                            if isNonDownloadedQIF or getExtnParam_ofx_qif_dont_check_original_memo(getExtnParam_selected_account()):
                                mustCheckAgainstOlMemo = False

                        if mustCheckAgainstOlMemo:
                            if olMemo == "":
                                myPrint("DB", "... ignoring %s memo(s) as (mustCheck) olMemo:'%s' is blank (txnMemo: '%s')'..." %(olTypeTxt, olMemo, txnMemo))
                                continue

                            if txnMemo != olMemo:
                                myPrint("DB", "... ignoring %s memo(s) as (mustCheck) olMemo:'%s' != txnMemo:'%s'..." %(olTypeTxt, olMemo, txnMemo))
                                continue

                        zapMemo = False
                        swapMemoDesc = False

                        if isMDP:
                            zapMemo = True
                        else:
                            if getExtnParam_ofx_qif_dont_compare_with_desc(getExtnParam_selected_account()):
                                zapMemo = True

                            txnDesc = txn.getDescription().strip().lower()                                                  # noqa
                            if txnDesc != "" and txnDesc == txnMemo:
                                zapMemo = True
                            elif txnDesc == "" and txnMemo != "":
                                if getExtnParam_swap_memo_desc_when_subset(getExtnParam_selected_account()):
                                    storeTxn.setSwapMarker("^^")
                                else:
                                    storeTxn.setSwapMarker("##")
                                    iCountBlankDescSwapsWarning += 1
                                swapMemoDesc = True
                                zapMemo = True
                            elif txnMemo in txnDesc and len(txnMemo) < len(txnDesc):
                                if getExtnParam_zap_memo_when_subset_desc(getExtnParam_selected_account()):
                                    zapMemo = True
                                    storeTxn.setSwapMarker("~~")
                            elif txnDesc in txnMemo and len(txnDesc) < len(txnMemo):
                                if getExtnParam_swap_memo_desc_when_subset(getExtnParam_selected_account()):
                                    swapMemoDesc = True
                                    zapMemo = True
                                    storeTxn.setSwapMarker("><")

                            if not zapMemo and not swapMemoDesc:
                                myPrint("DB", "... ignoring %s memo(s) - matching rule failed - txnMemo:'%s', txnDesc:'%s'..." %(olTypeTxt, txnMemo, txnDesc))
                                continue

                        if zapMemo: storeTxn.newMemo = ""
                        if swapMemoDesc: storeTxn.newDesc = txn.getMemo()

                        myPrint("DB", "... Found %s txn dated: %s Desc: '%s' amount: %s (with memo rule match: zapMemo: %s, swapDesc: %s) txnMemo: '%s', olMemo: '%s'..., swapMarker: '%s'"
                                %(olTypeTxt,
                                  convertStrippedIntDateFormattedText(txn.getDateInt()),
                                  txn.getDescription(),
                                  txn.getAccount().getCurrencyType().formatFancy(txn.getValue(), MD_decimal),
                                  zapMemo, swapMemoDesc,
                                  txn.getMemo(),
                                  getOlMemo(txn),
                                  storeTxn.getSwapMarker()))

                        txnsWithMemos.append(storeTxn)
                        accountsInvolved[acct] = 1

            except: raise

            finally: pleaseWait.kill()

            if len(txnsWithMemos) < 1:
                popupTxt = "Did not find any md+/ofx/qif txns memo fields (matching rules) to zap/swap... quitting..."
                _txt = "@@ %s: %s @@" %(myModuleID, popupTxt)
                myPrint("B", _txt)
                myPopupInformationBox(toolbox_zap_mdplus_ofx_qif_default_memo_fields_frame_, popupTxt, theTitle=__THIS_METHOD_NAME.upper(), theMessageType=JOptionPane.INFORMATION_MESSAGE)
                MD_REF.getUI().setStatus(_txt, 0)
                raise QuickAbortThisScriptException

            _msgPad = 100
            _msgx = pad("Zap (or swap) memo fields:".upper() + " Please wait: preparing results..", _msgPad, padChar=".")
            pleaseWait = MyPopUpDialogBox(toolbox_zap_mdplus_ofx_qif_default_memo_fields_frame_,
                                          theStatus=_msgx,
                                          theTitle=_msgx.upper(),
                                          lModal=False,
                                          OKButtonText="WAIT")
            pleaseWait.go()

            txnsWithMemos = sorted(txnsWithMemos, key=lambda sort_x: (sort_x.getTxn().getAccount().getAccountType(),
                                                                      sort_x.getTxn().getAccount().getAccountName().lower(),
                                                                      sort_x.getTxn().getDateInt(),
                                                                      sort_x.getTxn().getValue()))

            #####################################################################################
            # Work out minimum field lengths for reporting.... Not elegant, but does the job...
            OUTPUT_DESC_LENGTH = 18
            OUTPUT_MEMO_LENGTH = 18
            OUTPUT_OLMEMO_LENGTH = 22

            for storedTxn in txnsWithMemos:
                txn = storedTxn.getTxn()
                pTxn = txn.getParentTxn()
                OUTPUT_DESC_LENGTH = max(OUTPUT_DESC_LENGTH, len(pTxn.getDescription()))
                OUTPUT_MEMO_LENGTH = max(OUTPUT_MEMO_LENGTH, len(pTxn.getMemo()))
                OUTPUT_OLMEMO_LENGTH = max(OUTPUT_OLMEMO_LENGTH, len(getOlMemo(pTxn)))

            OUTPUT_DESC_LENGTH = min(OUTPUT_DESC_LENGTH, 250)
            OUTPUT_MEMO_LENGTH = min(OUTPUT_MEMO_LENGTH, 250)
            OUTPUT_OLMEMO_LENGTH = min(OUTPUT_OLMEMO_LENGTH, 250)
            #####################################################################################

            outputTxt += "%s %s %s %s %s %s %s%s %s %s\n" \
                         "%s %s %s %s %s %s %s%s %s %s\n" \
                      %(pad("ol:", 4),
                        pad("Account Type:", 13),
                        pad("Account Name:", 26),
                        pad("Curr:", 5),
                        rpad("Txn Value:", 15),
                        pad("Txn Date:", 10),
                        pad("", 3),
                        pad("Txn Description:", OUTPUT_DESC_LENGTH),
                        pad("Txn Memo:", OUTPUT_MEMO_LENGTH),
                        pad("Txn Ol Memo:", OUTPUT_OLMEMO_LENGTH),
                        pad("", 4, padChar="-"),
                        pad("", 13, padChar="-"),
                        pad("", 26, padChar="-"),
                        pad("", 5, padChar="-"),
                        rpad("",15, padChar="-"),
                        pad("", 10, padChar="-"),
                        pad("", 3),
                        pad("", OUTPUT_DESC_LENGTH, padChar="-"),
                        pad("", OUTPUT_MEMO_LENGTH, padChar="-"),
                        pad("", OUTPUT_OLMEMO_LENGTH, padChar="-"))

            for storedTxn in txnsWithMemos:
                txn = storedTxn.getTxn()
                if isinstance(txn, ParentTxn): pass

                pTxn = txn.getParentTxn()
                pAcct = pTxn.getAccount()
                pAcctCurr = pAcct.getCurrencyType()

                if storedTxn.willSwapDesc():
                    iCountPotentialDescMemoSwaps += 1

                _desc = pTxn.getDescription()
                _memo = pTxn.getMemo()
                _olmemo = getOlMemo(pTxn)
                if _olmemo == "":
                    olTxt = "<blank>"
                elif _memo == _olmemo:
                    olTxt = "<same as memo>"
                elif _desc == _olmemo:
                    olTxt = "<same as description>"
                else:
                    olTxt = stripTextOfCRLFTabs(_olmemo)

                outputTxt += "%s %s %s %s %s %s %s%s %s %s\n" \
                          %(pad(storedTxn.getOlType(), 4),
                            pad(pAcct.getAccountType(), 13),
                            padTruncateWithDots(pAcct.getAccountName(), 26),
                            padTruncateWithDots(pAcctCurr.getIDString(), 5),
                            rpad(pAcctCurr.formatFancy(pTxn.getValue(), MD_decimal),15),
                            pad(convertStrippedIntDateFormattedText(pTxn.getDateInt()), 10),
                            pad(storedTxn.getSwapMarker(), 3),
                            padTruncateWithDots(stripTextOfCRLFTabs(_desc), OUTPUT_DESC_LENGTH),
                            padTruncateWithDots(stripTextOfCRLFTabs(_memo), OUTPUT_MEMO_LENGTH),
                            padTruncateWithDots(olTxt, OUTPUT_OLMEMO_LENGTH)
                            )

            msgTxt = "Found %s accounts with %s md+/ofx/qif txns where memo field(s) can be zapped (or swapped)..." %(len(accountsInvolved), len(txnsWithMemos))
            myPrint("B", msgTxt)

            outputTxt += "\n" \
                         "%s\n" %(msgTxt)

            if iCountPotentialDescMemoSwaps > 0:
                outputTxt += "\nFOUND: %s txns where the Memo and Description fields can be swapped first (to retain maximum information)\n" %(iCountPotentialDescMemoSwaps)

            if iCountBlankDescSwapsWarning > 0:
                outputTxt += "\nALERT ** FOUND: %s txns where Memo can be swapped into Desc (as desc was blank) BUT THE SWAP SETTING WAS NOT TICKED... (to retain maximum information) **\n" %(iCountBlankDescSwapsWarning)

            outputTxt += "KEY: 'Ol Memo = the hidden original downloaded/imported memo data\n"
            outputTxt += "     '^^' = Where memo can be swapped into description as description was blank\n"
            if iCountBlankDescSwapsWarning > 0:
                outputTxt += "     '##' = Where memo can be swapped into description as description was blank (SAFETY SWAP >> 'Swap memo into description' setting NOT TICKED)\n"
            outputTxt += "     '><' = Where memo can be swapped into description as description was found inside (longer) memo\n"
            outputTxt += "     '~~' = Where memo can be zapped as memo was found inside (longer) description\n"
            outputTxt += "\n"

            undo = book.getUndoManager()
            if isinstance(undo, MDUndoManager): pass

            if undo:
                outputTxt += "\n*** If you proceed, MD's Edit>UNDO manager will be enabled and available to you ***\n\n"
            else:
                outputTxt += "\n*** If you proceed, MD's Edit>UNDO manager is NOT available (Consider Backup first) ***\n\n"

            outputTxt += "\n\nParameters:\n"
            outputTxt += "  - Selected Account:                                                              %s\n" %(getExtnParam_selected_account_text())
            outputTxt += "  - Include unreconciled transactions (else only reconciled):                      %s\n" %(getExtnParam_include_unreconciled(getExtnParam_selected_account()))
            outputTxt += "  - Include unconfirmed transactions (else only confirmed) (bypassed on 'QIF-'):   %s\n" %(getExtnParam_include_unconfirmed(getExtnParam_selected_account()))
            outputTxt += "  - Include MD+ downloaded txns (and always zap memo field):      (MD+)            %s\n" %(getExtnParam_include_mdp(getExtnParam_selected_account()))
            outputTxt += "  - Include Downloaded OFX txns:                                  (OFX+)           %s\n" %(getExtnParam_include_ofx(getExtnParam_selected_account()))
            outputTxt += "  - Include file imported OFX txns:                               (OFX-)           %s\n" %(getExtnParam_imported_ofx(getExtnParam_selected_account()))
            outputTxt += "  - Include downloaded / file imported QIF txns:                  (QIF+)           %s\n" %(getExtnParam_downloaded_qif(getExtnParam_selected_account()))
            outputTxt += "  - Include NON downloaded / file imported QIF txns:              (QIF-)           %s\n" %(getExtnParam_non_downloaded_qif(getExtnParam_selected_account()))
            outputTxt += "  - Zap unchanged memo when memo already within (longer) description:              %s\n" %(getExtnParam_zap_memo_when_subset_desc(getExtnParam_selected_account()))
            outputTxt += "  - Swap memo into description when memo same but longer:                          %s\n" %(getExtnParam_swap_memo_desc_when_subset(getExtnParam_selected_account()))
            outputTxt += "  - Don't check / compare the original downloaded memo first (bypassed on 'QIF-'): %s\n" %(getExtnParam_ofx_qif_dont_check_original_memo(getExtnParam_selected_account()))
            outputTxt += "  - Don't compare memo to description (just zap) (after matching all other rules): %s\n" %(getExtnParam_ofx_qif_dont_compare_with_desc(getExtnParam_selected_account()))
            outputTxt += "\n"

            outputTxt += "\n<END>"

            pleaseWait.kill()

            _ask = MyPopUpDialogBox(toolbox_zap_mdplus_ofx_qif_default_memo_fields_frame_,
                                   theStatus=msgTxt,
                                   theMessage=outputTxt,
                                   theTitle=__THIS_METHOD_NAME.upper(),
                                   lAlertLevel=1,
                                   lCancelButton=True,
                                   OKButtonText="ZAP/SWAP MEMOs?")
            if not _ask.go():
                _txt = "%s: no changes made" %(__THIS_METHOD_NAME)
                myPrint("B", _txt)
                myPopupInformationBox(toolbox_zap_mdplus_ofx_qif_default_memo_fields_frame_, _txt, __THIS_METHOD_NAME.upper())
                raise QuickAbortThisScriptException

            try:

                myPrint("B", "PROCEEDING TO %s..." %(__THIS_METHOD_NAME))

                _msgPad = 100
                extraLongTimeMsg = "WILL TAKE SOME TIME >> " if len(txnsWithMemos) > 500 else ""

                _msgx = pad("Updating %s memo(s).. %sPLEASE WAIT..." %(len(txnsWithMemos), extraLongTimeMsg), _msgPad, padChar=".")
                pleaseWait = MyPopUpDialogBox(toolbox_zap_mdplus_ofx_qif_default_memo_fields_frame_,
                                              _msgx,
                                              theTitle=_msgx.upper(),
                                              lModal=False,
                                              OKButtonText="WAIT")
                pleaseWait.go()

                # Pause the MD+ poller...
                if isMDPlusEnabledBuild():
                    myPrint("B", "Pausing MD+")
                    plusPoller = MD_REF.getUI().getPlusController()
                    invokeMethodByReflection(plusPoller, "pausePolling", None)

                myPrint("B", "Flushing memory (pre-update) and saving in memory dataset changes to disk (log files)....")
                MD_REF.saveCurrentAccount()

                myPrint("B", "Pausing the MD Syncing engine....")
                MD_REF.getCurrentAccountBook().pauseSyncing()

                txnsToModify = []
                txnsOriginals = []

                myPrint("B", "UNDO Manager %s enabled...." %("is" if undo else "NOT"))


                for storedTxn in txnsWithMemos:
                    txn = storedTxn.getTxn()
                    if undo:
                        newTxn = txn.duplicate()
                        newTxn.setEditingMode()
                        if storedTxn.willSwapDesc():
                            newTxn.setDescription(storedTxn.getNewDesc())
                        if storedTxn.willZapMemo():
                            newTxn.setMemo(storedTxn.getNewMemo())
                        txnsOriginals.append(txn.duplicate())
                        txnsToModify.append(newTxn)
                    else:
                        txn.setEditingMode()
                        if storedTxn.willSwapDesc():
                            txn.setDescription(storedTxn.getNewDesc())
                        if storedTxn.willZapMemo():
                            txn.setMemo(storedTxn.getNewMemo())
                        txnsToModify.append(txn)

                myPrint("B", "En-mass marking the %s changed txns" %(len(txnsToModify)))
                if undo:
                    undo.modifyItems(txnsOriginals, txnsToModify)
                else:
                    book.logModifiedItems(txnsToModify)

                myPrint("B", "Resuming the MD Syncing engine....")
                MD_REF.getCurrentAccountBook().resumeSyncing()

                myPrint("B", "Flushing memory (post update) and saving in memory dataset changes to disk (log files)....")
                MD_REF.saveCurrentAccount()

                if len(txnsWithMemos) > 500:
                    myPrint("B", "Flushing dataset back to trunk file....")
                    MD_REF.getCurrentAccountBook().saveTrunkFile()

                if isMDPlusEnabledBuild():
                    myPrint("B", "Un-pausing MD+")
                    plusPoller = MD_REF.getUI().getPlusController()
                    invokeMethodByReflection(plusPoller, "resumePolling", None)

            except: raise

            finally:
                pleaseWait.kill()

            sMsg = "Zapping (or swapping) memo field(s) COMPLETED"
            mMsg = "%s md+/ofx/qif txns (involving %s accts)\n" \
                   "%s" %(len(txnsWithMemos), len(accountsInvolved), "(undo enabled)" if (undo) else "")
            MyPopUpDialogBox(toolbox_zap_mdplus_ofx_qif_default_memo_fields_frame_, theStatus=sMsg, theMessage=mMsg, theTitle=__THIS_METHOD_NAME.upper()).go()
            popupTxt = "Zapped (or swapped) memo field(s) on %s md+/ofx/qif txns (involving %s accts)%s" %(len(txnsWithMemos), len(accountsInvolved), " (undo enabled)" if (undo) else "")
            _txt = "@@ %s: %s @@" %(myModuleID, popupTxt)
            myPrint("B", _txt)
            MD_REF.getUI().setStatus(_txt, 0)

            myPrint("B","FINISHED....")

            cleanup_actions()

        doMain()

    except QuickAbortThisScriptException:
        myPrint("DB", "Caught Exception: QuickAbortThisScriptException... Doing nothing...")

    except:
        crash_txt = ("ERROR - %s has crashed. Please review MD Menu>Help>Console Window for details" %(myModuleID)).upper()
        myPrint("B",crash_txt)
        crash_output = dump_sys_error_to_md_console_and_errorlog(True)
        jifr = QuickJFrame("ERROR - %s:" %(myModuleID),crash_output).show_the_frame()
        myPopupInformationBox(jifr,crash_txt,theMessageType=JOptionPane.ERROR_MESSAGE)

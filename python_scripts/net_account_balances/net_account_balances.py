#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# net_account_balances.py build: 1002 - March 2021 - Stuart Beesley - StuWareSoftSystems

###############################################################################
# This extension creates a Moneydance Home Page View >> a little widget on the Home / Summary Screen dashboard
# Drag and drop the .mxt file onto the left side bar to install (or use Extensions, Manage Extensions, add from file)
# Once installed, visit Preferences > Summary Page, and then move the new widget to the desired Home screen location

# This widget allows you to select multiple accounts. The balances are totalled to present on the Home screen widget
# My concept was to add balances to target zero. Thus a positive number is 'good', a negative is 'bad'
# The idea is that you net cash and debt to get back to zero every month
# However, you could create a Net Worth Balance for example; you can use it for anything really
#
# You can change the widget name and also the balance type in the config screen (click the widget, or extensions menu)
# Any non base currency accounts are converted back to your base currency
# NOTE: This does not use recursive balance totalling, it simply uses the selected accounts' balance...

###############################################################################
# MIT License
#
# Copyright (c) 2021 Stuart Beesley
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

# Built to operate on Moneydance 2021.1 build 3056 onwards (as this is when the Py Extensions became fully functional)

# Build: 1 - Initial release
# Build: 2 - Screensize tweaks; ability to set widget display name; alter startup behaviour
# Build: 2 - Renamed to net_account_balances (removed _to_zero); common code/startup
# Build: 3 - properly convert fx accounts back to base currency; allow all account types in selection..
# Build: 4 - Tweak to security currency conversion to base...
# Build: 5 - Enhance JList colors and handling of clicks (so as not to unselect all on new click); add clear selection button
# Build: 1000 - Formal release
# Build: 1001 - Enhancements to incorporate VAqua on Mac; Fix JMenuBar() appearing in wrong place after File/Open(switch datasets)
# Build: 1001 - Change startup common code to detect 'wrong' startup conditions. Make build 3056 the minimum for my extensions (as they leverage .unload() etc)
# Build: 1001 - Fix condition when -invoke[_and_quit] was used to prevent refresh erroring when MD actually closing...
# Build: 1002 - Build 3067 of MD renamed com.moneydance.apps.md.view.gui.theme.Theme to com.moneydance.apps.md.view.gui.theme.ThemeInfo

# CUSTOMIZE AND COPY THIS ##############################################################################################
# CUSTOMIZE AND COPY THIS ##############################################################################################
# CUSTOMIZE AND COPY THIS ##############################################################################################

# SET THESE LINES
myModuleID = u"net_account_balances"
version_build = "1002"
MIN_BUILD_REQD = 3056  # 2021.1 Build 3056 is when Python extensions became fully functional (with .unload() method for example)
_I_CAN_RUN_AS_MONEYBOT_SCRIPT = False

if u"debug" in globals():
    global debug
else:
    debug = False
global net_account_balances_frame_
# SET LINES ABOVE ^^^^

# COPY >> START
global moneydance, moneydance_ui, moneydance_extension_loader, moneydance_extension_parameter
MD_REF = moneydance             # Make my own copy of reference as MD removes it once main thread ends.. Don't use/hold on to _data variable
MD_REF_UI = moneydance_ui       # Necessary as calls to .getUI() will try to load UI if None - we don't want this....
if MD_REF is None: raise Exception("CRITICAL ERROR - moneydance object/variable is None?")
if u"moneydance_extension_loader" in globals():
    MD_EXTENSION_LOADER = moneydance_extension_loader
else:
    MD_EXTENSION_LOADER = None

from java.lang import System, Runnable
from javax.swing import JFrame, SwingUtilities, SwingWorker
from java.awt.event import WindowEvent

class MyJFrame(JFrame):

    def __init__(self, frameTitle=None):
        super(JFrame, self).__init__(frameTitle)
        self.myJFrameVersion = 2
        self.isActiveInMoneydance = False
        self.isRunTimeExtension = False
        self.MoneydanceAppListener = None
        self.HomePageViewObj = None

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

def getMyJFrame( moduleName ):
    try:
        frames = JFrame.getFrames()
        for fr in frames:
            if (fr.getName().lower().startswith(u"%s_main" %moduleName)
                    and type(fr).__name__ == MyJFrame.__name__                         # isinstance() won't work across namespaces
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
            and isinstance(net_account_balances_frame_, MyJFrame)        # EDIT THIS
            and net_account_balances_frame_.isActiveInMoneydance):       # EDIT THIS
        frameToResurrect = net_account_balances_frame_                   # EDIT THIS
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

elif not _I_CAN_RUN_AS_MONEYBOT_SCRIPT and u"moneydance_extension_loader" not in globals():
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

    from org.python.core.util import FileUtil

    from java.lang import Thread

    from com.moneydance.util import Platform
    from com.moneydance.awt import JTextPanel, GridC, JDateField
    from com.moneydance.apps.md.view.gui import MDImages

    from com.infinitekind.util import DateUtil, CustomDateFormat
    from com.infinitekind.moneydance.model import *
    from com.infinitekind.moneydance.model import AccountUtil, AcctFilter, CurrencyType, CurrencyUtil
    from com.infinitekind.moneydance.model import Account, Reminder, ParentTxn, SplitTxn, TxnSearch, InvestUtil, TxnUtil

    from javax.swing import JButton, JScrollPane, WindowConstants, JLabel, JPanel, JComponent, KeyStroke, JDialog, JComboBox
    from javax.swing import JOptionPane, JTextArea, JMenuBar, JMenu, JMenuItem, AbstractAction, JCheckBoxMenuItem, JFileChooser
    from javax.swing import JTextField, JPasswordField, Box, UIManager, JTable, JCheckBox, JRadioButton, ButtonGroup
    from javax.swing.text import PlainDocument
    from javax.swing.border import EmptyBorder

    from java.awt.datatransfer import StringSelection
    from javax.swing.text import DefaultHighlighter

    from java.awt import Color, Dimension, FileDialog, FlowLayout, Toolkit, Font, GridBagLayout, GridLayout
    from java.awt import BorderLayout, Dialog, Insets
    from java.awt.event import KeyEvent, WindowAdapter, InputEvent
    from java.util import Date

    from java.text import DecimalFormat, SimpleDateFormat
    from java.util import Calendar, ArrayList
    from java.lang import Double, Math, Character
    from java.io import FileNotFoundException, FilenameFilter, File, FileInputStream, FileOutputStream, IOException, StringReader
    from java.io import BufferedReader, InputStreamReader
    from java.nio.charset import Charset
    if isinstance(None, (JDateField,CurrencyUtil,Reminder,ParentTxn,SplitTxn,TxnSearch, JComboBox, JCheckBox,
                         JTextArea, JMenuBar, JMenu, JMenuItem, JCheckBoxMenuItem, JFileChooser, JDialog,
                         JButton, FlowLayout, InputEvent, ArrayList, File, IOException, StringReader, BufferedReader,
                         InputStreamReader, Dialog, JTable, BorderLayout, Double, InvestUtil, JRadioButton, ButtonGroup,
                         AccountUtil, AcctFilter, CurrencyType, Account, TxnUtil, JScrollPane, WindowConstants, JFrame,
                         JComponent, KeyStroke, AbstractAction, UIManager, Color, Dimension, Toolkit, KeyEvent,
                         WindowAdapter, CustomDateFormat, SimpleDateFormat, Insets, FileDialog, Thread, SwingWorker)): pass
    if codecs.BOM_UTF8 is not None: pass
    if csv.QUOTE_ALL is not None: pass
    if datetime.MINYEAR is not None: pass
    if Math.max(1,1): pass
    # END COMMON IMPORTS ###################################################################################################

    # COMMON GLOBALS #######################################################################################################
    global myParameters, myScriptName, _resetParameters, i_am_an_extension_so_run_headless, moneydanceIcon
    global lPickle_version_warning, decimalCharSep, groupingCharSep, lIamAMac, lGlobalErrorDetected
    global MYPYTHON_DOWNLOAD_URL
    # END COMMON GLOBALS ###################################################################################################
    # COPY >> END

    # SET THESE VARIABLES FOR ALL SCRIPTS ##################################################################################
    myScriptName = u"%s.py(Extension)" %myModuleID                                                                      # noqa
    myParameters = {}                                                                                                   # noqa
    _resetParameters = False                                                                                            # noqa
    lPickle_version_warning = False                                                                                     # noqa
    lIamAMac = False                                                                                                    # noqa
    lGlobalErrorDetected = False																						# noqa
    MYPYTHON_DOWNLOAD_URL = "https://yogi1967.github.io/MoneydancePythonScripts/"                                       # noqa
    # END SET THESE VARIABLES FOR ALL SCRIPTS ##############################################################################

    # >>> THIS SCRIPT'S IMPORTS ############################################################################################
    import threading
    from com.moneydance.apps.md.view import HomePageView
    from com.infinitekind.moneydance.model import AccountListener
    from com.moneydance.apps.md.controller import FeatureModule
    from javax.swing import JList, ListSelectionModel
    from com.moneydance.awt import CollapsibleRefresher
    from com.moneydance.awt import GridC
    from com.moneydance.apps.md.view.gui import MoneydanceLAF
    from javax.swing import DefaultListCellRenderer
    from javax.swing import BorderFactory
    from com.moneydance.awt import JLinkListener, JLinkLabel
    from javax.swing import DefaultListSelectionModel

    # renamed in MD build 3067
    if int(MD_REF.getBuild()) >= 3067:
        from com.moneydance.apps.md.view.gui.theme import ThemeInfo                                                     # noqa
    else:
        from com.moneydance.apps.md.view.gui.theme import Theme as ThemeInfo

    # from com.moneydance.apps.md.controller import URLUtil
    # >>> END THIS SCRIPT'S IMPORTS ########################################################################################

    # >>> THIS SCRIPT'S GLOBALS ############################################################################################
    global __net_account_balances_extension, extn_param_listAccountUUIDs_NAB, extn_param_balanceType_NAB, extn_param_widget_display_name_NAB
    extn_param_listAccountUUIDs_NAB = []                                                                              # noqa
    extn_param_balanceType_NAB = 0                                                                                    # noqa
    extn_param_widget_display_name_NAB = ""                                                                           # noqa
    DEFAULT_WIDGET_NAME = "Net Account Balances:"
    # >>> END THIS SCRIPT'S GLOBALS ############################################################################################

    # COPY >> START
    # COMMON CODE ##########################################################################################################
    # COMMON CODE ##########################################################################################################
    # COMMON CODE ##########################################################################################################
    i_am_an_extension_so_run_headless = False                                                                           # noqa
    try:
        myScriptName = os.path.basename(__file__)
    except:
        i_am_an_extension_so_run_headless = True                                                                        # noqa

    scriptExit = """
----------------------------------------------------------------------------------------------------------------------
Thank you for using %s!
The author has other useful Extensions / Moneybot Python scripts available...:

Extension (.mxt) format only:
toolbox                                 View Moneydance settings, diagnostics, fix issues, change settings and much more
net_account_balances:                   Homepage / summary screen widget. Display the total of selected Account Balances

Extension (.mxt) and Script (.py) Versions available:
extract_data                            Extract various data to screen and/or csv.. Consolidation of:
- stockglance2020                       View summary of Securities/Stocks on screen, total by Security, export to csv 
- extract_reminders_csv                 View reminders on screen, edit if required, extract all to csv
- extract_currency_history_csv          Extract currency history to csv
- extract_investment_transactions_csv   Extract investment transactions to csv
- extract_account_registers_csv         Extract Account Register(s) to csv along with any attachments

list_future_reminders:                  View future reminders on screen. Allows you to set the days to look forward

A collection of useful ad-hoc scripts (zip file)
useful_scripts:                         Just unzip and select the script you want for the task at hand...

Visit: %s (Author's site)
----------------------------------------------------------------------------------------------------------------------
""" %(myScriptName, MYPYTHON_DOWNLOAD_URL)

    def cleanup_references():
        global MD_REF, MD_REF_UI, MD_EXTENSION_LOADER
        myPrint("DB","About to delete reference to MD_REF, MD_REF_UI and MD_EXTENSION_LOADER....!")
        del MD_REF, MD_REF_UI, MD_EXTENSION_LOADER

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
                    line += "\n"
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
        global myScriptName, debug, i_am_an_extension_so_run_headless

        if where[0] == "D" and not debug: return

        printString = ""
        for what in args:
            printString += "%s " %what
        printString = printString.strip()

        if where == "P" or where == "B" or where[0] == "D":
            if not i_am_an_extension_so_run_headless:
                try:
                    print(printString)
                except:
                    print("Error writing to screen...")
                    dump_sys_error_to_md_console_and_errorlog()

        if where == "J" or where == "B" or where == "DB":
            dt = datetime.datetime.now().strftime("%Y/%m/%d-%H:%M:%S")
            try:
                System.err.write(myScriptName + ":" + dt + ": ")
                System.err.write(printString)
                System.err.write("\n")
            except:
                System.err.write(myScriptName + ":" + dt + ": "+"Error writing to console")
                dump_sys_error_to_md_console_and_errorlog()
        return

    def dump_sys_error_to_md_console_and_errorlog( lReturnText=False ):

        theText = ""
        myPrint("B","Unexpected error caught: %s" %(sys.exc_info()[0]))
        myPrint("B","Unexpected error caught: %s" %(sys.exc_info()[1]))
        myPrint("B","Error on Script Line Number: %s" %(sys.exc_info()[2].tb_lineno))

        if lReturnText:
            theText += "\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
            theText += "Unexpected error caught: %s\n" %(sys.exc_info()[0])
            theText += "Unexpected error caught: %s\n" %(sys.exc_info()[1])
            theText += "Error on Script Line Number: %s\n" %(sys.exc_info()[2].tb_lineno)
            theText += "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
            return theText

        return

    def pad(theText, theLength):
        theText = theText[:theLength].ljust(theLength, u" ")
        return theText

    def rpad(theText, theLength):
        if not (isinstance(theText, unicode) or isinstance(theText, str)):
            theText = str(theText)

        theText = theText[:theLength].rjust(theLength, u" ")
        return theText

    def cpad(theText, theLength):
        if not (isinstance(theText, unicode) or isinstance(theText, str)):
            theText = str(theText)

        if len(theText)>=theLength: return theText[:theLength]

        padLength = int((theLength - len(theText)) / 2)
        theText = theText[:theLength]
        theText = ((" "*padLength)+theText+(" "*padLength))[:theLength]

        return theText


    myPrint("B", myScriptName, ": Python Script Initialising.......", "Build:", version_build)

    def getMonoFont():
        global debug

        try:
            theFont = MD_REF.getUI().getFonts().code
            # if debug: myPrint("B","Success setting Font set to Moneydance code: %s" %theFont)
        except:
            theFont = Font("monospaced", Font.PLAIN, 15)
            if debug: myPrint("B","Failed to Font set to Moneydance code - So using: %s" %theFont)

        return theFont

    def getTheSetting(what):
        x = MD_REF.getPreferences().getSetting(what, None)
        if not x or x == u"": return None
        return what + u": %s" %(x)

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

        if not homeDir: homeDir = u"?"
        return homeDir

    def getDecimalPoint(lGetPoint=False, lGetGrouping=False):
        global debug

        decimalFormat = DecimalFormat.getInstance()
        # noinspection PyUnresolvedReferences
        decimalSymbols = decimalFormat.getDecimalFormatSymbols()

        if not lGetGrouping: lGetPoint = True
        if lGetGrouping and lGetPoint: return u"error"

        try:
            if lGetPoint:
                _decimalCharSep = decimalSymbols.getDecimalSeparator()
                myPrint(u"D",u"Decimal Point Character: %s" %(_decimalCharSep))
                return _decimalCharSep

            if lGetGrouping:
                _groupingCharSep = decimalSymbols.getGroupingSeparator()
                if _groupingCharSep is None or _groupingCharSep == u"":
                    myPrint(u"B", u"Caught empty Grouping Separator")
                    return u""
                if ord(_groupingCharSep) >= 128:    # Probably a nbsp (160) = e.g. South Africa for example..!
                    myPrint(u"B", u"Caught special character in Grouping Separator. Ord(%s)" %(ord(_groupingCharSep)))
                    if ord(_groupingCharSep) == 160:
                        return u" (non breaking space character)"
                    return u" (non printable character)"
                myPrint(u"D",u"Grouping Separator Character:", _groupingCharSep)
                return _groupingCharSep
        except:
            myPrint(u"B",u"Error in getDecimalPoint() routine....?")
            dump_sys_error_to_md_console_and_errorlog()

        return u"error"


    decimalCharSep = getDecimalPoint(lGetPoint=True)
    groupingCharSep = getDecimalPoint(lGetGrouping=True)

    # JOptionPane.DEFAULT_OPTION, JOptionPane.YES_NO_OPTION, JOptionPane.YES_NO_CANCEL_OPTION, JOptionPane.OK_CANCEL_OPTION
    # JOptionPane.ERROR_MESSAGE, JOptionPane.INFORMATION_MESSAGE, JOptionPane.WARNING_MESSAGE, JOptionPane.QUESTION_MESSAGE, JOptionPane.PLAIN_MESSAGE

    # Copies MD_REF.getUI().showInfoMessage
    def myPopupInformationBox(theParent=None, theMessage="What no message?!", theTitle="Info", theMessageType=JOptionPane.INFORMATION_MESSAGE):

        if theParent is None:
            if theMessageType == JOptionPane.PLAIN_MESSAGE or theMessageType == JOptionPane.INFORMATION_MESSAGE:
                icon_to_use=MD_REF.getUI().getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png")
                JOptionPane.showMessageDialog(theParent, JTextPanel(theMessage), theTitle, theMessageType, icon_to_use)
                return
        JOptionPane.showMessageDialog(theParent, JTextPanel(theMessage), theTitle, theMessageType)
        return

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
                                                None,
                                                _options,
                                                _options[0])

        if response == 2:
            myPrint("B", "User requested to perform Export Backup before update/fix - calling moneydance export backup routine...")
            MD_REF.getUI().setStatus("%s performing an Export Backup...." %(myScriptName),-1.0)
            MD_REF.getUI().saveToBackup(None)
            MD_REF.getUI().setStatus("%s Export Backup completed...." %(myScriptName),0)
            return True

        elif response == 1:
            myPrint("B", "User DECLINED to perform Export Backup before update/fix...!")
            if not lReturnTheTruth:
                return True

        return False

    # Copied MD_REF.getUI().askQuestion
    def myPopupAskQuestion(theParent=None,
                           theTitle="Question",
                           theQuestion="What?",
                           theOptionType=JOptionPane.YES_NO_OPTION,
                           theMessageType=JOptionPane.QUESTION_MESSAGE):

        icon_to_use = None
        if theParent is None:
            if theMessageType == JOptionPane.PLAIN_MESSAGE or theMessageType == JOptionPane.INFORMATION_MESSAGE:
                icon_to_use=MD_REF.getUI().getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png")

        # question = wrapLines(theQuestion)
        question = theQuestion
        result = JOptionPane.showConfirmDialog(theParent,
                                               question,
                                               theTitle,
                                               theOptionType,
                                               theMessageType,
                                               icon_to_use)  # getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"))

        return result == 0

    # Copies Moneydance .askForQuestion
    def myPopupAskForInput(theParent,
                           theTitle,
                           theFieldLabel,
                           theFieldDescription="",
                           defaultValue=None,
                           isPassword=False,
                           theMessageType=JOptionPane.INFORMATION_MESSAGE):

        icon_to_use = None
        if theParent is None:
            if theMessageType == JOptionPane.PLAIN_MESSAGE or theMessageType == JOptionPane.INFORMATION_MESSAGE:
                icon_to_use=MD_REF.getUI().getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png")

        p = JPanel(GridBagLayout())
        defaultText = None
        if defaultValue: defaultText = defaultValue
        if isPassword:
            field = JPasswordField(defaultText)
        else:
            field = JTextField(defaultText)

        x = 0
        if theFieldLabel:
            p.add(JLabel(theFieldLabel), GridC.getc(x, 0).east())
            x+=1

        p.add(field, GridC.getc(x, 0).field())
        p.add(Box.createHorizontalStrut(244), GridC.getc(x, 0))
        if theFieldDescription:
            p.add(JTextPanel(theFieldDescription), GridC.getc(x, 1).field().colspan(x + 1))
        if (JOptionPane.showConfirmDialog(theParent,
                                          p,
                                          theTitle,
                                          JOptionPane.OK_CANCEL_OPTION,
                                          theMessageType,
                                          icon_to_use) == 0):
            return field.getText()
        return None

    # APPLICATION_MODAL, DOCUMENT_MODAL, MODELESS, TOOLKIT_MODAL
    class MyPopUpDialogBox():

        def __init__(self, theParent=None, theStatus="", theMessage="", theWidth=200, theTitle="Info", lModal=True, lCancelButton=False, OKButtonText="OK", lAlertLevel=0):
            self.theParent = theParent
            self.theStatus = theStatus
            self.theMessage = theMessage
            self.theWidth = max(80,theWidth)
            self.theTitle = theTitle
            self.lModal = lModal
            self.lCancelButton = lCancelButton
            self.OKButtonText = OKButtonText
            self.lAlertLevel = lAlertLevel
            self.fakeJFrame = None
            self._popup_d = None
            self.lResult = [None]
            if not self.theMessage.endswith("\n"): self.theMessage+="\n"
            if self.OKButtonText == "": self.OKButtonText="OK"

        class WindowListener(WindowAdapter):

            def __init__(self, theDialog, theFakeFrame, lResult):
                self.theDialog = theDialog
                self.theFakeFrame = theFakeFrame
                self.lResult = lResult

            def windowClosing(self, WindowEvent):                                                                       # noqa
                global debug
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
            # noinspection PyMethodMayBeStatic

            def __init__(self, theDialog, theFakeFrame, lResult):
                self.theDialog = theDialog
                self.theFakeFrame = theFakeFrame
                self.lResult = lResult

            def actionPerformed(self, event):
                global debug
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
            # noinspection PyMethodMayBeStatic

            def __init__(self, theDialog, theFakeFrame, lResult):
                self.theDialog = theDialog
                self.theFakeFrame = theFakeFrame
                self.lResult = lResult

            def actionPerformed(self, event):
                global debug
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

            global debug
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
            global debug
            return self.lResult[0]

        def go(self):
            global debug

            myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()")
            myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

            class MyPopUpDialogBoxRunnable(Runnable):
                def __init__(self, callingClass):
                    self.callingClass = callingClass

                def run(self):                                                                                                      # noqa

                    myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()")
                    myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

                    # Create a fake JFrame so we can set the Icons...
                    if self.callingClass.theParent is None:
                        self.callingClass.fakeJFrame = MyJFrame()
                        self.callingClass.fakeJFrame.setName(u"%s_fake_dialog" %(myModuleID))
                        self.callingClass.fakeJFrame.setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE)
                        self.callingClass.fakeJFrame.setUndecorated(True)
                        self.callingClass.fakeJFrame.setVisible( False )
                        if not Platform.isOSX():
                            self.callingClass.fakeJFrame.setIconImage(MDImages.getImage(MD_REF.getSourceInformation().getIconResource()))

                    if self.callingClass.lModal:
                        # noinspection PyUnresolvedReferences
                        self.callingClass._popup_d = JDialog(self.callingClass.theParent, self.callingClass.theTitle, Dialog.ModalityType.APPLICATION_MODAL)
                    else:
                        # noinspection PyUnresolvedReferences
                        self.callingClass._popup_d = JDialog(self.callingClass.theParent, self.callingClass.theTitle, Dialog.ModalityType.MODELESS)

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

                    displayJText = JTextArea(self.callingClass.theMessage)
                    displayJText.setFont( getMonoFont() )
                    displayJText.setEditable(False)
                    displayJText.setLineWrap(False)
                    displayJText.setWrapStyleWord(False)

                    _popupPanel=JPanel()

                    # maxHeight = 500
                    _popupPanel.setLayout(GridLayout(0,1))
                    _popupPanel.setBorder(EmptyBorder(8, 8, 8, 8))

                    if self.callingClass.theStatus:
                        _label1 = JLabel(pad(self.callingClass.theStatus,self.callingClass.theWidth-20))
                        _label1.setForeground(Color.BLUE)
                        _popupPanel.add(_label1)

                    myScrollPane = JScrollPane(displayJText, JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED,JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED)
                    if displayJText.getLineCount()>5:
                        myScrollPane.setWheelScrollingEnabled(True)
                        _popupPanel.add(myScrollPane)
                    else:
                        _popupPanel.add(displayJText)

                    buttonPanel = JPanel()
                    if self.callingClass.lModal or self.callingClass.lCancelButton:
                        buttonPanel.setLayout(FlowLayout(FlowLayout.CENTER))

                        if self.callingClass.lCancelButton:
                            cancel_button = JButton("CANCEL")
                            cancel_button.setPreferredSize(Dimension(100,40))
                            cancel_button.setBackground(Color.LIGHT_GRAY)
                            cancel_button.setBorderPainted(False)
                            cancel_button.setOpaque(True)
                            cancel_button.addActionListener( self.callingClass.CancelButtonAction(self.callingClass._popup_d, self.callingClass.fakeJFrame,self.callingClass.lResult) )
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
                            ok_button.addActionListener( self.callingClass.OKButtonAction(self.callingClass._popup_d, self.callingClass.fakeJFrame, self.callingClass.lResult) )
                            buttonPanel.add(ok_button)

                        _popupPanel.add(buttonPanel)

                    if self.callingClass.lAlertLevel>=2:
                        # internalScrollPane.setBackground(Color.RED)
                        # theJText.setBackground(Color.RED)
                        # theJText.setForeground(Color.BLACK)
                        displayJText.setBackground(Color.RED)
                        displayJText.setForeground(Color.BLACK)
                        _popupPanel.setBackground(Color.RED)
                        _popupPanel.setForeground(Color.BLACK)
                        buttonPanel.setBackground(Color.RED)
                        myScrollPane.setBackground(Color.RED)

                    elif self.callingClass.lAlertLevel>=1:
                        # internalScrollPane.setBackground(Color.YELLOW)
                        # theJText.setBackground(Color.YELLOW)
                        # theJText.setForeground(Color.BLACK)
                        displayJText.setBackground(Color.YELLOW)
                        displayJText.setForeground(Color.BLACK)
                        _popupPanel.setBackground(Color.YELLOW)
                        _popupPanel.setForeground(Color.BLACK)
                        buttonPanel.setBackground(Color.YELLOW)
                        myScrollPane.setBackground(Color.RED)

                    self.callingClass._popup_d.add(_popupPanel)
                    self.callingClass._popup_d.pack()
                    self.callingClass._popup_d.setLocationRelativeTo(None)
                    self.callingClass._popup_d.setVisible(True)  # Keeping this modal....

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
        ext = ""

        def __init__(self, ext):
            self.ext = "." + ext.upper()

        def accept(self, thedir, filename):                                                                             # noqa
            if filename is not None and filename.upper().endswith(self.ext):
                return True
            return False

    try:
        moneydanceIcon = MDImages.getImage(MD_REF.getSourceInformation().getIconResource())
    except:
        moneydanceIcon = None

    def MDDiag():
        global debug
        myPrint("D", "Moneydance Build:", MD_REF.getVersion(), "Build:", MD_REF.getBuild())


    MDDiag()

    myPrint("DB","System file encoding is:", sys.getfilesystemencoding() )   # Not used, but interesting. Perhaps useful when switching between Windows/Macs and writing files...

    def checkVersions():
        global debug

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

        myFont = MD_REF.getUI().getFonts().defaultText

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

    if MD_REF_UI is not None:
        setDefaultFonts()

    def who_am_i():
        try:
            username = System.getProperty("user.name")
        except:
            username = "???"

        return username

    def getHomeDir():
        # Yup - this can be all over the place...
        myPrint("D", 'System.getProperty("user.dir")', System.getProperty("user.dir"))
        myPrint("D", 'System.getProperty("UserHome")', System.getProperty("UserHome"))
        myPrint("D", 'System.getProperty("user.home")', System.getProperty("user.home"))
        myPrint("D", 'os.path.expanduser("~")', os.path.expanduser("~"))
        myPrint("D", 'os.environ.get("HOMEPATH")', os.environ.get("HOMEPATH"))
        return

    def amIaMac():
        return Platform.isOSX()

    myPrint("D", "I am user:", who_am_i())
    if debug: getHomeDir()
    lIamAMac = amIaMac()

    def myDir():
        global lIamAMac
        homeDir = None

        try:
            if lIamAMac:
                homeDir = System.getProperty("UserHome")  # On a Mac in a Java VM, the homedir is hidden
            else:
                # homeDir = System.getProperty("user.home")
                homeDir = os.path.expanduser("~")  # Should work on Unix and Windows
                if homeDir is None or homeDir == "":
                    homeDir = System.getProperty("user.home")
                if homeDir is None or homeDir == "":
                    homeDir = os.environ.get("HOMEPATH")
        except:
            pass

        if homeDir is None or homeDir == "":
            homeDir = MD_REF.getCurrentAccountBook().getRootFolder().getParent()  # Better than nothing!

        myPrint("DB", "Home Directory selected...:", homeDir)
        if homeDir is None: return ""
        return homeDir

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
                    super(JTextFieldLimitYN, self).insertString(myOffset, myString, myAttr)                         # noqa

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
        global debug, myParameters, lPickle_version_warning, version_build, _resetParameters                            # noqa

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )

        if _resetParameters:
            myPrint("B", "User has specified to reset parameters... keeping defaults and skipping pickle()")
            myParameters = {}
            return

        old_dict_filename = os.path.join("..", myFile)

        # Pickle was originally encrypted, no need, migrating to unencrypted
        migratedFilename = os.path.join(MD_REF.getCurrentAccountBook().getRootFolder().getAbsolutePath(),myFile)

        myPrint("DB", "Now checking for parameter file:", migratedFilename)

        if os.path.exists( migratedFilename ):

            myPrint("DB", "loading parameters from non-encrypted Pickle file:", migratedFilename)
            myPrint("DB", "Parameter file", migratedFilename, "exists..")
            # Open the file
            try:
                istr = FileInputStream(migratedFilename)
                load_file = FileUtil.wrap(istr)
                # noinspection PyTypeChecker
                myParameters = pickle.load(load_file)
                load_file.close()
            except FileNotFoundException:
                myPrint("B", "Error: failed to find parameter file...")
                myParameters = None
            except EOFError:
                myPrint("B", "Error: reached EOF on parameter file....")
                myParameters = None
            except:
                myPrint("B","Error opening Pickle File (will try encrypted version) - Unexpected error ", sys.exc_info()[0])
                myPrint("B","Error opening Pickle File (will try encrypted version) - Unexpected error ", sys.exc_info()[1])
                myPrint("B","Error opening Pickle File (will try encrypted version) - Line Number: ", sys.exc_info()[2].tb_lineno)

                # OK, so perhaps from older version - encrypted, try to read
                try:
                    local_storage = MD_REF.getCurrentAccountBook().getLocalStorage()
                    istr = local_storage.openFileForReading(old_dict_filename)
                    load_file = FileUtil.wrap(istr)
                    # noinspection PyTypeChecker
                    myParameters = pickle.load(load_file)
                    load_file.close()
                    myPrint("B","Success loading Encrypted Pickle file - will migrate to non encrypted")
                    lPickle_version_warning = True
                except:
                    myPrint("B","Opening Encrypted Pickle File - Unexpected error ", sys.exc_info()[0])
                    myPrint("B","Opening Encrypted Pickle File - Unexpected error ", sys.exc_info()[1])
                    myPrint("B","Error opening Pickle File - Line Number: ", sys.exc_info()[2].tb_lineno)
                    myPrint("B", "Error: Pickle.load() failed.... Is this a restored dataset? Will ignore saved parameters, and create a new file...")
                    myParameters = None

            if myParameters is None:
                myParameters = {}
                myPrint("DB","Parameters did not load, will keep defaults..")
            else:
                myPrint("DB","Parameters successfully loaded from file...")
        else:
            myPrint("J", "Parameter Pickle file does not exist - will use default and create new file..")
            myPrint("D", "Parameter Pickle file does not exist - will use default and create new file..")
            myParameters = {}

        if not myParameters: return

        myPrint("DB","myParameters read from file contains...:")
        for key in sorted(myParameters.keys()):
            myPrint("DB","...variable:", key, myParameters[key])

        if myParameters.get("debug") is not None: debug = myParameters.get("debug")
        if myParameters.get("lUseMacFileChooser") is not None:
            myPrint("B", "Detected old lUseMacFileChooser parameter/variable... Will delete it...")
            myParameters.pop("lUseMacFileChooser", None)  # Old variable - not used - delete from parameter file

        myPrint("DB","Parameter file loaded if present and myParameters{} dictionary set.....")

        # Now load into memory!
        load_StuWareSoftSystems_parameters_into_memory()

        return

    def save_StuWareSoftSystems_parameters_to_file(myFile="StuWareSoftSystems.dict"):
        global debug, myParameters, lPickle_version_warning, version_build

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )

        if myParameters is None: myParameters = {}

        # Don't forget, any parameters loaded earlier will be preserved; just add changed variables....
        myParameters["__Author"] = "Stuart Beesley - (c) StuWareSoftSystems"
        myParameters["debug"] = debug

        dump_StuWareSoftSystems_parameters_from_memory()

        # Pickle was originally encrypted, no need, migrating to unencrypted
        migratedFilename = os.path.join(MD_REF.getCurrentAccountBook().getRootFolder().getAbsolutePath(),myFile)

        myPrint("DB","Will try to save parameter file:", migratedFilename)

        ostr = FileOutputStream(migratedFilename)

        myPrint("DB", "about to Pickle.dump and save parameters to unencrypted file:", migratedFilename)

        try:
            save_file = FileUtil.wrap(ostr)
            # noinspection PyTypeChecker
            pickle.dump(myParameters, save_file)
            save_file.close()

            myPrint("DB","myParameters now contains...:")
            for key in sorted(myParameters.keys()):
                myPrint("DB","...variable:", key, myParameters[key])

        except:
            myPrint("B", "Error - failed to create/write parameter file.. Ignoring and continuing.....")
            dump_sys_error_to_md_console_and_errorlog()

            return

        myPrint("DB","Parameter file written and parameters saved to disk.....")

        return

    def get_time_stamp_as_nice_text( timeStamp ):

        prettyDate = ""
        try:
            c = Calendar.getInstance()
            c.setTime(Date(timeStamp))
            dateFormatter = SimpleDateFormat("yyyy/MM/dd HH:mm:ss(.SSS) Z z zzzz")
            prettyDate = dateFormatter.format(c.getTime())
        except:
            pass

        return prettyDate

    def currentDateTimeMarker():
        c = Calendar.getInstance()
        dateformat = SimpleDateFormat("_yyyyMMdd_HHmmss")
        _datetime = dateformat.format(c.getTime())
        return _datetime

    def destroyOldFrames(moduleName):
        myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", WindowEvent)
        myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))
        frames = JFrame.getFrames()
        for fr in frames:
            if fr.getName().lower().startswith(moduleName):
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

            _search_options = [ "Next", "Previous", "Cancel" ]

            defaultDirection = _search_options[self.lastDirection]

            response = JOptionPane.showOptionDialog(self.theFrame,
                                                    p,
                                                    "Search for text",
                                                    JOptionPane.OK_CANCEL_OPTION,
                                                    JOptionPane.QUESTION_MESSAGE,
                                                    None,
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

    class QuickJFrame():

        def __init__(self, title, output, lAlertLevel=0, copyToClipboard=False):
            self.title = title
            self.output = output
            self.lAlertLevel = lAlertLevel
            self.returnFrame = None
            self.copyToClipboard = copyToClipboard

        class CloseAction(AbstractAction):

            def __init__(self, theFrame):
                self.theFrame = theFrame

            def actionPerformed(self, event):
                global debug
                myPrint("D","in CloseAction(), Event: ", event)
                myPrint("DB", "QuickJFrame() Frame shutting down....")

                # Already within the EDT
                self.theFrame.dispose()
                return

        def show_the_frame(self):
            global debug

            class MyQuickJFrameRunnable(Runnable):

                def __init__(self, callingClass):
                    self.callingClass = callingClass

                def run(self):                                                                                                      # noqa
                    screenSize = Toolkit.getDefaultToolkit().getScreenSize()

                    frame_width = min(screenSize.width-20, max(1024,int(round(MD_REF.getUI().firstMainFrame.getSize().width *.9,0))))
                    frame_height = min(screenSize.height-20, max(768, int(round(MD_REF.getUI().firstMainFrame.getSize().height *.9,0))))

                    JFrame.setDefaultLookAndFeelDecorated(True)

                    jInternalFrame = MyJFrame(self.callingClass.title + " (%s+F to find/search for text)" %(MD_REF.getUI().ACCELERATOR_MASK_STR))
                    jInternalFrame.setName(u"%s_quickjframe" %myModuleID)

                    if not Platform.isOSX():
                        jInternalFrame.setIconImage(MDImages.getImage(MD_REF.getUI().getMain().getSourceInformation().getIconResource()))

                    jInternalFrame.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE)
                    jInternalFrame.setResizable(True)

                    shortcut = Toolkit.getDefaultToolkit().getMenuShortcutKeyMaskEx()
                    jInternalFrame.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_W,  shortcut), "close-window")
                    jInternalFrame.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_F4, shortcut), "close-window")
                    jInternalFrame.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_F,  shortcut), "search-window")
                    jInternalFrame.getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0), "close-window")

                    theJText = JTextArea(self.callingClass.output)
                    theJText.setEditable(False)
                    theJText.setLineWrap(True)
                    theJText.setWrapStyleWord(True)
                    theJText.setFont( getMonoFont() )

                    jInternalFrame.getRootPane().getActionMap().put("close-window", self.callingClass.CloseAction(jInternalFrame))
                    jInternalFrame.getRootPane().getActionMap().put("search-window", SearchAction(jInternalFrame,theJText))

                    internalScrollPane = JScrollPane(theJText, JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED,JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED)

                    if self.callingClass.lAlertLevel>=2:
                        internalScrollPane.setBackground(Color.RED)
                        theJText.setBackground(Color.RED)
                        theJText.setForeground(Color.BLACK)
                    elif self.callingClass.lAlertLevel>=1:
                        internalScrollPane.setBackground(Color.YELLOW)
                        theJText.setBackground(Color.YELLOW)
                        theJText.setForeground(Color.BLACK)

                    jInternalFrame.setPreferredSize(Dimension(frame_width, frame_height))

                    jInternalFrame.add(internalScrollPane)

                    jInternalFrame.pack()
                    jInternalFrame.setLocationRelativeTo(None)
                    jInternalFrame.setVisible(True)

                    if "errlog.txt" in self.callingClass.title:
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

    class AboutThisScript():

        class CloseAboutAction(AbstractAction):

            def __init__(self, theFrame):
                self.theFrame = theFrame

            def actionPerformed(self, event):
                global debug
                myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()", "Event:", event)

                # Listener is already on the Swing EDT...
                self.theFrame.dispose()

        def __init__(self, theFrame):
            global debug, scriptExit
            self.theFrame = theFrame

        def go(self):
            myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()")

            class MyAboutRunnable(Runnable):
                def __init__(self, callingClass):
                    self.callingClass = callingClass

                def run(self):                                                                                                      # noqa

                    myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
                    myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

                    # noinspection PyUnresolvedReferences
                    about_d = JDialog(self.callingClass.theFrame, "About", Dialog.ModalityType.MODELESS)

                    shortcut = Toolkit.getDefaultToolkit().getMenuShortcutKeyMaskEx()
                    about_d.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_W, shortcut), "close-window")
                    about_d.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_F4, shortcut), "close-window")
                    about_d.getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0), "close-window")

                    about_d.getRootPane().getActionMap().put("close-window", self.callingClass.CloseAboutAction(about_d))

                    about_d.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE)  # The CloseAction() and WindowListener() will handle dispose() - else change back to DISPOSE_ON_CLOSE

                    if (not Platform.isMac()):
                        # MD_REF.getUI().getImages()
                        about_d.setIconImage(MDImages.getImage(MD_REF.getUI().getMain().getSourceInformation().getIconResource()))

                    aboutPanel=JPanel()
                    aboutPanel.setLayout(FlowLayout(FlowLayout.LEFT))
                    aboutPanel.setPreferredSize(Dimension(1120, 500))

                    _label1 = JLabel(pad("Author: Stuart Beesley", 800))
                    _label1.setForeground(Color.BLUE)
                    aboutPanel.add(_label1)

                    _label2 = JLabel(pad("StuWareSoftSystems (2020-2021)", 800))
                    _label2.setForeground(Color.BLUE)
                    aboutPanel.add(_label2)

                    displayString=scriptExit
                    displayJText = JTextArea(displayString)
                    displayJText.setFont( getMonoFont() )
                    displayJText.setEditable(False)
                    displayJText.setLineWrap(False)
                    displayJText.setWrapStyleWord(False)
                    displayJText.setMargin(Insets(8, 8, 8, 8))
                    # displayJText.setBackground((mdGUI.getColors()).defaultBackground)
                    # displayJText.setForeground((mdGUI.getColors()).defaultTextForeground)

                    aboutPanel.add(displayJText)

                    about_d.add(aboutPanel)

                    about_d.pack()
                    about_d.setLocationRelativeTo(None)
                    about_d.setVisible(True)

            if not SwingUtilities.isEventDispatchThread():
                myPrint("DB",".. Not running within the EDT so calling via MyAboutRunnable()...")
                SwingUtilities.invokeAndWait(MyAboutRunnable(self))
            else:
                myPrint("DB",".. Already within the EDT so calling naked...")
                MyAboutRunnable(self).run()

            myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

    # END COMMON DEFINITIONS ###############################################################################################
    # END COMMON DEFINITIONS ###############################################################################################
    # END COMMON DEFINITIONS ###############################################################################################
    # COPY >> END

    # >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
    # >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
    # >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
    def load_StuWareSoftSystems_parameters_into_memory():
        global debug, myParameters, lPickle_version_warning, version_build

        # >>> THESE ARE THIS SCRIPT's PARAMETERS TO LOAD
        global __net_account_balances_extension, extn_param_listAccountUUIDs_NAB, extn_param_balanceType_NAB, extn_param_widget_display_name_NAB

        myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()" )
        myPrint("DB", "Loading variables into memory...")

        if myParameters is None: myParameters = {}

        if myParameters.get("__net_account_balances_extension") is not None: __net_account_balances_extension = myParameters.get("__net_account_balances_extension")
        if myParameters.get("extn_param_listAccountUUIDs_NAB") is not None: extn_param_listAccountUUIDs_NAB = myParameters.get("extn_param_listAccountUUIDs_NAB")
        if myParameters.get("extn_param_balanceType_NAB") is not None: extn_param_balanceType_NAB = myParameters.get("extn_param_balanceType_NAB")
        if myParameters.get("extn_param_widget_display_name_NAB") is not None: extn_param_widget_display_name_NAB = myParameters.get("extn_param_widget_display_name_NAB")

        myPrint("DB","myParameters{} set into memory (as variables).....")

        return

    # >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
    def dump_StuWareSoftSystems_parameters_from_memory():
        global debug, myParameters, lPickle_version_warning, version_build

        # >>> THESE ARE THIS SCRIPT's PARAMETERS TO SAVE
        global __net_account_balances_extension, extn_param_listAccountUUIDs_NAB, extn_param_balanceType_NAB, extn_param_widget_display_name_NAB

        myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()" )

        # NOTE: Parameters were loaded earlier on... Preserve existing, and update any used ones...
        # (i.e. other StuWareSoftSystems programs might be sharing the same file)

        if myParameters is None: myParameters = {}

        myParameters["__net_account_balances_extension"] = version_build
        myParameters["extn_param_listAccountUUIDs_NAB"] = extn_param_listAccountUUIDs_NAB
        myParameters["extn_param_balanceType_NAB"] = extn_param_balanceType_NAB
        myParameters["extn_param_widget_display_name_NAB"] = extn_param_widget_display_name_NAB

        myPrint("DB","variables dumped from memory back into myParameters{}.....")

        return

    # clear up any old left-overs....
    destroyOldFrames(myModuleID)

    myPrint("DB", "DEBUG IS ON..")

    if SwingUtilities.isEventDispatchThread():
        myPrint("DB", "FYI - This script/extension is currently running within the Swing Event Dispatch Thread (EDT)")
    else:
        myPrint("DB", "FYI - This script/extension is NOT currently running within the Swing Event Dispatch Thread (EDT)")

    def cleanup_actions(theFrame, md_reference):
        myPrint("DB", "In", inspect.currentframe().f_code.co_name, "()")
        myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

        if theFrame: pass
        # if not theFrame.isActiveInMoneydance:
        #     destroyOldFrames(myModuleID)  # This was killing frames just launched/reinstalled... not needed (I think)
        #
        try:
            md_reference.getUI().setStatus(">> StuWareSoftSystems - thanks for using >> %s......." %(myScriptName),0)
        except:
            pass  # If this fails, then MD is probably shutting down.......

        if not i_am_an_extension_so_run_headless: print(scriptExit)

        cleanup_references()

    # END ALL CODE COPY HERE ###############################################################################################
    # END ALL CODE COPY HERE ###############################################################################################
    # END ALL CODE COPY HERE ###############################################################################################

    class MyAcctFilter(AcctFilter):

        def __init__(self):
            pass

        # noinspection PyMethodMayBeStatic
        def matches(self, acct):

            # # noinspection PyUnresolvedReferences
            # if not (acct.getAccountType() == Account.AccountType.BANK
            #         or acct.getAccountType() == Account.AccountType.CREDIT_CARD):
            #     return False

            # noinspection PyUnresolvedReferences
            if (acct.getAccountType() == Account.AccountType.ROOT
                    or acct.getAccountType() == Account.AccountType.SECURITY):
                return False

            if (acct.getAccountOrParentIsInactive()): return False
            if (acct.getHideOnHomePage() and acct.getBalance() == 0): return False

            return True

    class StoreAccountList():
        def __init__(self, obj):
            if isinstance(obj,Account):
                self.obj = obj                          # type: Account
            else:
                self.obj = None

        def __str__(self):
            if self.obj is None:
                return "Invalid Acct Obj or None"
            return "%s : %s" %(self.obj.getAccountType(),self.obj.getFullAccountName())

        def __repr__(self):
            return self.__str__()

    def sendMessage(extensionID, theMessage):
        myPrint("DB","In ", inspect.currentframe().f_code.co_name, "()")
        # replicating moneydance.showURL("moneydance:fmodule:net_account_balances:myCommand_here?thisIsMyParameter")

        frs = getMyJFrame( extensionID )
        if frs:
            myPrint("DB", "... found frame: %s - requesting .invoke(%s)" %(frs, theMessage))
            return frs.MoneydanceAppListener.invoke("%s:customevent:%s" %(extensionID,theMessage))
        else:
            myPrint("DB",".. Sorry - did not find my application (JFrame) to send message....")
        return

    myPrint("B","HomePageView widget / extension is now running...")

    class NetAccountBalancesExtension(FeatureModule):

        def __init__(self):  # This is the class' own initialise, just to set up variables
            global extn_param_listAccountUUIDs_NAB, extn_param_balanceType_NAB, extn_param_widget_display_name_NAB, debug
            # super(FeatureModule, self).__init__()                                                                       # noqa

            self.myModuleID = myModuleID

            myPrint("B", "\n##########################################################################################")
            myPrint("B", "Extension: %s (HomePageView widget) initialising...." %(self.myModuleID))
            myPrint("B", "##########################################################################################\n")

            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

            self.moneydanceContext = MD_REF
            self.moneydanceExtensionObject = None

            if float(self.moneydanceContext.getBuild()) >= 3051:
                self.moneydanceExtensionLoader = moneydance_extension_loader  # This is the class loader for the whole extension
                myPrint("DB", "... Build is >= 3051 so using moneydance_extension_loader: %s" %(self.moneydanceExtensionLoader))
            else:
                self.moneydanceExtensionLoader = None

            self.lock = threading.Lock()

            self.alreadyClosed = False

            self.parametersLoaded = False
            self.myCounter = 0
            self.theFrame = None
            self.isUIavailable = False
            self.saveMyHomePageView = None
            self.helpFile = "<NONE>"

            self.savedAccountListUUIDs = []
            self.savedBalanceType = 0
            self.savedWidgetName = DEFAULT_WIDGET_NAME

            self.menuItemDEBUG = None
            self.mainMenuBar= None

            self.configPanelOpen = False

            self.jlst = None
            self.balanceType_option = None
            self.widgetNameField = None

            myPrint("DB", "Exiting ", inspect.currentframe().f_code.co_name, "()")
            myPrint("DB", "##########################################################################################")

        def initialize(self, extension_context, extension_object):  # This is called by Moneydance after the run-time extension self installs itself
            myPrint("DB", "##########################################################################################")
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

            # These extension_* variables are set by Moneydance before calling this script via the PY Interpreter
            self.moneydanceContext = extension_context  # This is the same as the moneydance variable and com.moneydance.apps.md.controller.Main
            self.moneydanceExtensionObject = extension_object  # This is com.moneydance.apps.md.controller.PythonExtension

            if debug:
                myPrint("DB","meta_info.dict 'id' = %s" %(self.moneydanceExtensionObject.getIDStr()))
                myPrint("DB","meta_info.dict 'module_build' = %s" %(self.moneydanceExtensionObject.getBuild()))
                myPrint("DB","meta_info.dict 'desc' = %s" %(self.moneydanceExtensionObject.getDescription()))
                myPrint("DB","script path: %s" %(self.moneydanceExtensionObject.getSourceFile()))

            self.moneydanceContext.registerFeature(extension_object, "%s:customevent:showConfig" %(self.myModuleID), None, self.getName().replace("_"," ").title())
            myPrint("DB","@@ Registered self as an Extension onto the Extension Menu @@")

            self.saveMyHomePageView = MyHomePageView(self)

            self.moneydanceContext.registerHomePageView(extension_object, self.saveMyHomePageView)
            myPrint("DB","@@ Registered extension_object as containing a Home Page View (Summary screen / Dashboard object) @@")

            # If the UI is loaded, then probably a re-install... Refresh the UI with a new window....
            if self.getMoneydanceUI():         # Only do this if the UI is loaded and dataset loaded...
                myPrint("B","@@ Assuming an extension reinstall. Loading a new Dashboard to refresh the view....")
                moneydance_ui.selectAccountNewWindow(self.moneydanceContext.getCurrentAccountBook().getRootAccount())

            myPrint("DB", "Exiting ", inspect.currentframe().f_code.co_name, "()")
            myPrint("DB", "##########################################################################################")

        class CloseAction(AbstractAction):

            def __init__(self, theFrame, callingClass):
                self.theFrame = theFrame
                self.callingClass = callingClass

            def actionPerformed(self, event):                                                                           # noqa
                global debug
                myPrint("DB", "In %s.%s() - Event: %s" %(self, inspect.currentframe().f_code.co_name, event))
                myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
                myPrint("DB", ".. main application frame being disposed (will shut down application)....")

                myPrint("DB", "action = %s" %(event.getActionCommand()))

                # Listeners are already on the Swing EDT
                self.theFrame.dispose()  # Should call WindowListener; windowClosed()

        class HideAction(AbstractAction):

            def __init__(self, theFrame, callingClass):
                self.theFrame = theFrame
                self.callingClass = callingClass

            def actionPerformed(self, event):                                                                           # noqa
                global debug
                myPrint("DB", "In %s.%s() - Event: %s" %(self, inspect.currentframe().f_code.co_name, event))
                myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
                myPrint("DB","Setting MyJFrame to invisible....")

                self.callingClass.configPanelOpen = False

                # Listeners are already on the Swing EDT
                self.theFrame.setVisible(False)

        class HelpAction(AbstractAction):

            def __init__(self, theFrame, callingClass):
                self.theFrame = theFrame
                self.callingClass = callingClass

            def actionPerformed(self, event):                                                                           # noqa
                global debug
                myPrint("DB", "In %s.%s() - Event: %s" %(self, inspect.currentframe().f_code.co_name, event))
                myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

                QuickJFrame("%s - Help" %(self.callingClass.myModuleID), self.callingClass.helpFile).show_the_frame()

        class WindowListener(WindowAdapter):

            def __init__(self, theFrame, moduleID, callingClass):
                self.theFrame = theFrame        # type: MyJFrame
                self.myModuleID = moduleID
                self.callingClass = callingClass

            # noinspection PyMethodMayBeStatic
            def windowActivated(self, WindowEvent):                                                                     # noqa
                global debug
                myPrint("DB", "In %s.%s() - Event: %s" %(self, inspect.currentframe().f_code.co_name, WindowEvent))
                myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

                self.callingClass.menuItemDEBUG.setSelected(debug)
                self.callingClass.balanceType_option.setSelectedIndex(self.callingClass.savedBalanceType)
                self.callingClass.widgetNameField.setText(self.callingClass.savedWidgetName)

                # ######################################################################################################
                # On Mac,since VAqua was used builds 3039 onwards, the JMenuBar() would sometimes appear in the wrong place
                # It seems that the useScreenMenuBar=false setting needs to be in play as the JFrame is made visible
                # or perhaps when the JMenuBar() is added.... Hence doing it here. A bit messy I know.....
                # ... probably I should create a new JFrame() with every config call, but then I would have to change the launch checks...
                # ######################################################################################################
                if Platform.isOSX():
                    # self.callingClass.theFrame.setJMenuBar(None)
                    save_useScreenMenuBar = System.getProperty("apple.laf.useScreenMenuBar")
                    if save_useScreenMenuBar is None or save_useScreenMenuBar == "":
                        save_useScreenMenuBar= System.getProperty("com.apple.macos.useScreenMenuBar")
                    System.setProperty("apple.laf.useScreenMenuBar", "false")
                    System.setProperty("com.apple.macos.useScreenMenuBar", "false")

                    myPrint("DB","...setting the JMenuBar() now....: %s" %(self.callingClass.mainMenuBar))
                    self.callingClass.theFrame.setJMenuBar(self.callingClass.mainMenuBar)

                    self.callingClass.mainMenuBar.revalidate()
                    self.callingClass.mainMenuBar.repaint()

                    System.setProperty("apple.laf.useScreenMenuBar", save_useScreenMenuBar)
                    System.setProperty("com.apple.macos.useScreenMenuBar", save_useScreenMenuBar)
                # ##################################################################################################

                if self.callingClass.configPanelOpen:
                    myPrint("DB",".. Application's config panel is already open so will not refresh...")

                else:

                    self.callingClass.configPanelOpen = True
                    listOfAllAccountsForJList = []

                    getAccounts = AccountUtil.allMatchesForSearch(self.callingClass.moneydanceContext.getCurrentAccountBook(), MyAcctFilter())
                    getAccounts = sorted(getAccounts, key=lambda sort_x: (sort_x.getAccountType(), sort_x.getFullAccountName().upper()))
                    for acct in getAccounts:
                        listOfAllAccountsForJList.append(StoreAccountList(acct))
                    del getAccounts

                    self.callingClass.jlst.setListData(listOfAllAccountsForJList)

                    myPrint("DB","...%s accountsToShow stored in JList" %(len(listOfAllAccountsForJList)))
                    myPrint("DB","...savedAccountListUUIDs: %s" %(self.callingClass.savedAccountListUUIDs))
                    myPrint("DB","...savedBalanceType: %s" %(self.callingClass.savedBalanceType))

                    countMatch = 0

                    index = 0
                    itemsToSelect = []

                    for a in listOfAllAccountsForJList:
                        if a.obj.getUUID() in self.callingClass.savedAccountListUUIDs:
                            countMatch+=1
                            myPrint("DB","...selecting %s in JList()" %a)
                            itemsToSelect.append(index)
                        index += 1

                    if len(itemsToSelect):
                        self.callingClass.jlst.setSelectedIndices(itemsToSelect)
                        self.callingClass.jlst.ensureIndexIsVisible(itemsToSelect[0])

                    myPrint("DB","...%s accountsToShow matched UUIDs and selected in JList" %(countMatch))

                myPrint("DB", "Exiting ", inspect.currentframe().f_code.co_name, "()")

            # noinspection PyMethodMayBeStatic
            def windowDeactivated(self, WindowEvent):                                                                   # noqa
                myPrint("DB", "In %s.%s() - Event: %s" %(self, inspect.currentframe().f_code.co_name, WindowEvent))

                if Platform.isOSX():
                    myPrint("DB","...setting JMenuBar() to None")
                    self.callingClass.theFrame.setJMenuBar(None)

            # noinspection PyMethodMayBeStatic
            def windowDeiconified(self, WindowEvent):                                                                   # noqa
                myPrint("DB", "In %s.%s() - Event: %s" %(self, inspect.currentframe().f_code.co_name, WindowEvent))

            # noinspection PyMethodMayBeStatic
            def windowGainedFocus(self, WindowEvent):                                                                   # noqa
                myPrint("DB", "In %s.%s() - Event: %s" %(self, inspect.currentframe().f_code.co_name, WindowEvent))

            # noinspection PyMethodMayBeStatic
            def windowLostFocus(self, WindowEvent):                                                                     # noqa
                myPrint("DB", "In %s.%s() - Event: %s" %(self, inspect.currentframe().f_code.co_name, WindowEvent))

            # noinspection PyMethodMayBeStatic
            def windowIconified(self, WindowEvent):                                                                     # noqa
                myPrint("DB", "In %s.%s() - Event: %s" %(self, inspect.currentframe().f_code.co_name, WindowEvent))

            # noinspection PyMethodMayBeStatic
            def windowOpened(self, WindowEvent):                                                                        # noqa
                myPrint("DB", "In %s.%s() - Event: %s" %(self, inspect.currentframe().f_code.co_name, WindowEvent))

            # noinspection PyMethodMayBeStatic
            def windowStateChanged(self, WindowEvent):                                                                  # noqa
                myPrint("DB", "In %s.%s() - Event: %s" %(self, inspect.currentframe().f_code.co_name, WindowEvent))

            def terminate_script(self):
                myPrint("DB","In ", inspect.currentframe().f_code.co_name, "()")
                myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

                try:
                    # NOTE - .dispose() - The windowClosed event should set .isActiveInMoneydance False and .removeAppEventListener()
                    if not SwingUtilities.isEventDispatchThread():
                        SwingUtilities.invokeLater(GenericDisposeRunnable(self.theFrame))
                    else:
                        GenericDisposeRunnable(self.theFrame).run()
                except:
                    myPrint("B","Error. Final dispose failed....?")
                    dump_sys_error_to_md_console_and_errorlog()


            def windowClosing(self, WindowEvent):                                                                       # noqa
                global debug

                myPrint("DB", "In %s.%s() - Event: %s" %(self, inspect.currentframe().f_code.co_name, WindowEvent))
                myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

                self.callingClass.configPanelOpen = False

                if self.theFrame.isVisible():
                    myPrint("DB", ".. in windowClosing, but isVisible is True, so will just ignore....")
                else:
                    myPrint("DB", ".. in windowClosing, and isVisible is False, so will start termination....")
                    self.terminate_script()

            def windowClosed(self, WindowEvent):                                                                       # noqa

                myPrint("DB", "In %s.%s() - Event: %s" %(self, inspect.currentframe().f_code.co_name, WindowEvent))
                myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

                self.callingClass.configPanelOpen = False
                self.theFrame.isActiveInMoneydance = False

                if self.theFrame.MoneydanceAppListener is not None and not self.theFrame.MoneydanceAppListener.alreadyClosed:

                    try:
                        myPrint("DB","\n@@@ Calling .unload() to deactivate extension and close the HomePageView... \n")
                        self.theFrame.MoneydanceAppListener.unload(True)
                    except:
                        myPrint("B","@@@ FAILED to call .unload() to deactivate extension and close the HomePageView... \n")
                        dump_sys_error_to_md_console_and_errorlog()

                elif self.theFrame.MoneydanceAppListener is not None and self.theFrame.MoneydanceAppListener.alreadyClosed:
                    myPrint("DB","Skipping .unload() as I'm assuming that's where I was called from (alreadyClosed was set)...")
                else:
                    myPrint("DB","MoneydanceAppListener is None so Skipping .unload()..")

                self.theFrame.MoneydanceAppListener.alreadyClosed = True
                self.theFrame.MoneydanceAppListener = None

                cleanup_actions(self.theFrame, self.callingClass.moneydanceContext)

        class MyActionListener(AbstractAction):

            def __init__(self, callingClass):
                self.callingClass = callingClass

            def actionPerformed(self, event):
                global extn_param_listAccountUUIDs_NAB, extn_param_balanceType_NAB, extn_param_widget_display_name_NAB, debug

                myPrint("DB", "In %s.%s() - Event: %s" %(self, inspect.currentframe().f_code.co_name, event))
                myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
                myPrint("DB", "... Action Command", event.getActionCommand())

                # ##########################################################################################################
                if event.getActionCommand() == "About":
                    AboutThisScript(self.callingClass.theFrame).go()

                # ##########################################################################################################
                if event.getActionCommand() == "Help":
                    QuickJFrame("%s - Help" %(self.callingClass.myModuleID), self.callingClass.helpFile).show_the_frame()

                # ######################################################################################################
                if event.getActionCommand().lower().startswith("save"):
                    del self.callingClass.savedAccountListUUIDs[:]
                    myPrint("B","Saving account list for HomePageView widget..")
                    for selectedAccount in self.callingClass.jlst.getSelectedValuesList():
                        myPrint("DB","...saving account %s in saved parameter list..." %(selectedAccount))
                        self.callingClass.savedAccountListUUIDs.append(selectedAccount.obj.getUUID())
                    self.callingClass.savedBalanceType = self.callingClass.balanceType_option.getSelectedIndex()

                    self.callingClass.savedWidgetName = self.callingClass.widgetNameField.getText()
                    if self.callingClass.savedWidgetName.strip() == "":
                        self.callingClass.savedWidgetName =  DEFAULT_WIDGET_NAME

                    extn_param_listAccountUUIDs_NAB = self.callingClass.savedAccountListUUIDs
                    extn_param_balanceType_NAB = self.callingClass.savedBalanceType
                    extn_param_widget_display_name_NAB = self.callingClass.savedWidgetName

                    self.callingClass.configPanelOpen = False
                    self.callingClass.theFrame.setVisible(False)    # Listener, so already on Swing EDT

                    class MyRefreshRunnable(Runnable):

                        def __init__(self, callingClass):
                            self.callingClass = callingClass

                        # noinspection PyMethodMayBeStatic
                        def run(self):
                            global debug

                            myPrint("DB","Inside %s MyRefreshRunnable.... About call HomePageView .refresh()\n" %(self.callingClass.myModuleID))
                            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
                            try:
                                self.callingClass.saveMyHomePageView.refresh()
                                myPrint("DB","Back from calling HomePageView .refresh() on %s...." %(self.callingClass.myModuleID))
                            except:
                                dump_sys_error_to_md_console_and_errorlog()
                                myPrint("B","@@ ERROR calling .refresh() in HomePageView on %s....  :-< " %(self.callingClass.myModuleID))
                            return

                    myPrint("DB", "... About to call HomePageView .refresh() after updating accounts list via SwingUtilities.invokeLater(MyRefreshRunnable())")
                    SwingUtilities.invokeLater(MyRefreshRunnable(self.callingClass))

                # ######################################################################################################
                if event.getActionCommand().lower().startswith("clear"):
                    myPrint("DB","...clearing selection...")
                    self.callingClass.jlst.clearSelection()

                # ######################################################################################################
                if event.getActionCommand().lower().startswith("cancel"):
                    myPrint("DB","...ignoring changes and reverting to previous account list")
                    self.callingClass.configPanelOpen = False
                    self.callingClass.theFrame.setVisible(False)    # Listener, so already on Swing EDT

                # ######################################################################################################
                if event.getActionCommand().lower().startswith("debug"):
                    if debug:
                        myPrint("B", "User has DISABLED debug mode.......")
                    else:
                        myPrint("B", "User has ENABLED debug mode.......")

                    debug = not debug

                # ######################################################################################################
                if event.getActionCommand().lower().startswith("deactivate"):

                    myPrint("DB", "User has clicked deactivate - sending 'close' request via .showURL().......")
                    self.callingClass.moneydanceContext.showURL("moneydance:fmodule:%s:%s:customevent:close" %(self.callingClass.myModuleID,self.callingClass.myModuleID))

                # ######################################################################################################
                if event.getActionCommand().lower().startswith("uninstall"):

                    myPrint("DB", "User has clicked uninstall - sending 'uninstall' request via .showURL().......")
                    self.callingClass.moneydanceContext.showURL("moneydance:fmodule:%s:%s:customevent:uninstall" %(self.callingClass.myModuleID,self.callingClass.myModuleID))

                # ######################################################################################################
                # Save parameters now...
                if (event.getActionCommand().lower().startswith("save")
                        or event.getActionCommand().lower().startswith("debug")):

                    try:
                        save_StuWareSoftSystems_parameters_to_file(myFile="%s_extension.dict" %(self.callingClass.myModuleID))
                    except:
                        myPrint("DB","@@ Error saving parameters back to pickle file....?")
                        dump_sys_error_to_md_console_and_errorlog()

                myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
                return

        class MyJListRenderer(DefaultListCellRenderer):

            def __init__(self):
                super(DefaultListCellRenderer, self).__init__()                                                         # noqa

            def getListCellRendererComponent(self, thelist, value, index, isSelected, cellHasFocus):
                lightLightGray = Color(0xDCDCDC)
                c = super(NetAccountBalancesExtension.MyJListRenderer, self).getListCellRendererComponent(thelist, value, index, isSelected, cellHasFocus) # noqa
                # c.setBackground(self.getBackground() if index % 2 == 0 else lightLightGray)

                # Create a line separator between accounts
                c.setBorder(BorderFactory.createMatteBorder(0, 0, 1, 0, lightLightGray))

                return c

        def load_saved_parameters(self):
            global extn_param_listAccountUUIDs_NAB, extn_param_balanceType_NAB, extn_param_widget_display_name_NAB

            myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()")
            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
            myPrint("DB", "... parametersLoaded: %s .getCurrentAccountBook(): %s" %(self.parametersLoaded, self.moneydanceContext.getCurrentAccountBook()))

            with self.lock:
                if not self.parametersLoaded:
                    if self.moneydanceContext.getCurrentAccountBook() is not None:
                        self.configPanelOpen = False
                        extn_param_listAccountUUIDs_NAB = []                      # Loading will overwrite if file exists.. Otherwise we want []
                        extn_param_balanceType_NAB = 0                            # Loading will overwrite if file exists.. Otherwise we want 0
                        extn_param_widget_display_name_NAB = DEFAULT_WIDGET_NAME  # Loading will overwrite if file exists.. Otherwise we want this default name
                        get_StuWareSoftSystems_parameters_from_file(myFile="%s_extension.dict" %(self.myModuleID))
                        self.parametersLoaded = True
                        self.savedAccountListUUIDs = extn_param_listAccountUUIDs_NAB
                        self.savedBalanceType = extn_param_balanceType_NAB
                        self.savedWidgetName = extn_param_widget_display_name_NAB

        # method getName() must exist as the interface demands it.....
        def getName(self):      # noqa
            return self.myModuleID.capitalize()

        # Not really used, but returns this value if print or repr is used on the class to retrieve its name....
        def __str__(self):
            return u"%s (Extension)" %(self.myModuleID.capitalize())

        def __repr__(self):
            return self.__str__()

        def getMyself(self):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            fm = self.moneydanceContext.getModuleForID(self.myModuleID)
            if fm is None: return None, None
            try:
                pyo = fm.getClass().getDeclaredField("extensionObject")
                pyo.setAccessible(True)
                pyObject = pyo.get(fm)
                pyo.setAccessible(False)
            except:
                myPrint("DB","Error retrieving my own Python extension object..?")
                dump_sys_error_to_md_console_and_errorlog()
                return None, None

            return fm, pyObject

        def unloadMyself(self):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))

            fm, pyObject = self.getMyself()

            if fm is None:
                myPrint("DB","Failed to retrieve myself - exiting")
                return False
            myPrint("DB","Retrieved myself: %s" %(fm))

            try:
                p = self.moneydanceContext.getClass().getDeclaredMethod("unloadModule", [FeatureModule])
                p.setAccessible(True)
                p.invoke(self.moneydanceContext,[fm])
                p.setAccessible(False)
            except:
                myPrint("DB","Error unloading my own extension object..?")
                dump_sys_error_to_md_console_and_errorlog()
                return False

            myPrint("B","@@ Success! Unloaded / deactivated myself..! ;->")
            return True

        def removeMyself(self):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))

            fm, pyObject = self.getMyself()

            if fm is None:
                myPrint("DB","Failed to retrieve myself - exiting")
                return False
            myPrint("DB","Retrieved myself: %s" %(fm))

            try:
                myPrint("DB","... about to ask MD to uninstall myself....")
                self.moneydanceContext.uninstallModule(fm)
            except:
                myPrint("DB","Error uninstalling my own extension object..?")
                dump_sys_error_to_md_console_and_errorlog()
                return False

            myPrint("B","@@ Success! Removed / uninstalled myself..! ;->")
            return True

        def build_main_frame(self):
            global net_account_balances_frame_

            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

            if self.theFrame is not None:
                myPrint("DB",".. main JFrame is already built: %s - so exiting" %(self.theFrame))
                return

            class BuildMainFrameRunnable(Runnable):
                def __init__(self, callingClass):
                    self.callingClass = callingClass

                def run(self):                                                                                                        # noqa
                    global net_account_balances_frame_

                    myPrint("DB", "Creating main JFrame for application...")

                    myPrint("DB","self.callingClass: %s" %(self.callingClass))
                    myPrint("DB","self.callingClass.theFrame: %s" %(self.callingClass.theFrame))


                    # Called from getMoneydanceUI() so assume the Moneydance GUI is loaded...
                    JFrame.setDefaultLookAndFeelDecorated(True)
                    net_account_balances_frame_ = MyJFrame(u"%s (b:%s) Home Page View widget - settings" % (self.callingClass.myModuleID.capitalize(), version_build))
                    self.callingClass.theFrame = net_account_balances_frame_
                    self.callingClass.theFrame.setName(u"%s_main" %(self.callingClass.myModuleID))

                    self.callingClass.theFrame.isActiveInMoneydance = True
                    self.callingClass.theFrame.isRunTimeExtension = True

                    self.callingClass.theFrame.MoneydanceAppListener = self.callingClass
                    self.callingClass.theFrame.HomePageViewObj = self.callingClass.saveMyHomePageView


                    gridbag = GridBagLayout()
                    pnl = JPanel(gridbag)


                    class MyDefaultListSelectionModel(DefaultListSelectionModel):  # build_main_frame() only runs once, so this is fine to do here...
                        # Change the selector - so not to deselect items when selecting others...
                        def __init__(self):
                            super(DefaultListSelectionModel, self).__init__()                                           # noqa

                        def setSelectionInterval(self, start, end):
                            if (start != end):
                                super(MyDefaultListSelectionModel, self).setSelectionInterval(start, end)               # noqa
                            elif self.isSelectedIndex(start):
                                self.removeSelectionInterval(start, end)
                            else:
                                self.addSelectionInterval(start, end)


                    self.callingClass.jlst = JList([])
                    self.callingClass.jlst.setBackground((self.callingClass.moneydanceContext.getUI().getColors()).listBackground)
                    self.callingClass.jlst.setCellRenderer( self.callingClass.MyJListRenderer() )
                    self.callingClass.jlst.setFixedCellHeight(self.callingClass.jlst.getFixedCellHeight()+30)
                    self.callingClass.jlst.setSelectionMode(ListSelectionModel.MULTIPLE_INTERVAL_SELECTION)
                    self.callingClass.jlst.setSelectionModel(MyDefaultListSelectionModel())

                    scrollpane = JScrollPane(self.callingClass.jlst, JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED,JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED)

                    screenSize = Toolkit.getDefaultToolkit().getScreenSize()
                    desired_scrollPane_width = 550
                    desired_frame_height_max = min(650, int(round(screenSize.height * 0.9,0)))
                    scrollPaneTop = scrollpane.getY()
                    calcScrollPaneHeight = (desired_frame_height_max - scrollPaneTop - 70)

                    scrollpane.setPreferredSize(Dimension(desired_scrollPane_width, calcScrollPaneHeight))
                    scrollpane.setMinimumSize(Dimension(desired_scrollPane_width, calcScrollPaneHeight))
                    scrollpane.setMaximumSize(Dimension(int(round(screenSize.width * 0.9,0)), int(round((screenSize.height * 0.9) - scrollPaneTop - 70,0))))

                    saveMyActionListener = self.callingClass.MyActionListener(self.callingClass)

                    if Platform.isOSX():
                        lbl = JLabel("Select multiple accounts - use CMD-Click, or click first, Shift-Click last...")
                    else:
                        lbl = JLabel("Select multiple accounts - use CTRL-Click, or click first, Shift-Click last...")

                    lbl.setForeground(Color.BLUE)
                    pnl.add(lbl, GridC.getc(0, 0).west().colspan(4).leftInset(10).topInset(10).bottomInset(10))

                    self.callingClass.widgetNameField = JTextField(self.callingClass.savedWidgetName)
                    pnl.add(self.callingClass.widgetNameField, GridC.getc(0, 1).west().colspan(4).leftInset(10).topInset(10).bottomInset(10).rightInset(10).fillboth())

                    balanceTypes = ["Balance", "Current Balance", "Cleared Balance"]
                    self.callingClass.balanceType_option = JComboBox(balanceTypes)
                    self.callingClass.balanceType_option.setToolTipText("Select the balance type to total: Balance (i.e. the final balance), Current Balance (as of today), Cleared Balance")
                    self.callingClass.balanceType_option.setSelectedItem(balanceTypes[self.callingClass.savedBalanceType])
                    pnl.add(self.callingClass.balanceType_option, GridC.getc(0, 2).west().leftInset(10).topInset(2))

                    clearList_button = JButton("Clear Selection")
                    clearList_button.setToolTipText("Clears the current selection(s)...")
                    clearList_button.addActionListener(saveMyActionListener)
                    pnl.add(clearList_button, GridC.getc(1, 2).leftInset(13))

                    saveAccountList_button = JButton("Save Changes")
                    saveAccountList_button.setToolTipText("Saves the selected account list")
                    saveAccountList_button.addActionListener(saveMyActionListener)
                    pnl.add(saveAccountList_button, GridC.getc(2, 2).leftInset(13))

                    cancelChanges_button = JButton("Cancel Changes")
                    cancelChanges_button.setToolTipText("Cancels your changes and reverts to the saved account list")
                    cancelChanges_button.addActionListener(saveMyActionListener)
                    pnl.add(cancelChanges_button, GridC.getc(3, 2).east().rightInset(8))

                    pnl.add(scrollpane,GridC.getc(0, 3).wx(1.0).west().colspan(4).leftInset(8).rightInset(8).topInset(8).bottomInset(8).fillboth())
                    self.callingClass.theFrame.add(pnl)

                    self.callingClass.theFrame.setDefaultCloseOperation(WindowConstants.HIDE_ON_CLOSE)

                    shortcut = Toolkit.getDefaultToolkit().getMenuShortcutKeyMaskEx()

                    # Add standard CMD-W keystrokes etc to close window
                    self.callingClass.theFrame.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_W, shortcut), "hide-window")
                    self.callingClass.theFrame.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_F4, shortcut), "hide-window")
                    self.callingClass.theFrame.getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0), "hide-window")
                    self.callingClass.theFrame.getRootPane().getActionMap().put("close-window", self.callingClass.CloseAction(self.callingClass.theFrame, self.callingClass))
                    self.callingClass.theFrame.getRootPane().getActionMap().put("hide-window", self.callingClass.HideAction(self.callingClass.theFrame, self.callingClass))

                    if self.callingClass.moneydanceExtensionLoader:
                        try:
                            self.callingClass.helpFile = load_text_from_stream_file(self.callingClass.moneydanceExtensionLoader.getResourceAsStream("/%s_readme.txt" %(self.callingClass.myModuleID)))
                            myPrint("DB","Contents loaded from /%s_readme.txt" %(self.callingClass.myModuleID))
                        except:
                            myPrint("DB","Error loading contents from /%s_readme.txt" %(self.callingClass.myModuleID))

                    self.callingClass.theFrame.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_I, shortcut), "display-help")
                    self.callingClass.theFrame.getRootPane().getActionMap().put("display-help", self.callingClass.HelpAction(self.callingClass.theFrame, self.callingClass))

                    self.callingClass.theFrame.addWindowListener(self.callingClass.WindowListener(self.callingClass.theFrame, self.callingClass.myModuleID, self.callingClass))

                    # self.theFrame.setPreferredSize(Dimension(600, 800))
                    self.callingClass.theFrame.setExtendedState(JFrame.NORMAL)
                    self.callingClass.theFrame.setResizable(True)

                    self.callingClass.mainMenuBar = JMenuBar()
                    menuO = JMenu("<html><B>Options</b></html>")

                    self.callingClass.menuItemDEBUG = JCheckBoxMenuItem("Debug")
                    self.callingClass.menuItemDEBUG.addActionListener(saveMyActionListener)
                    self.callingClass.menuItemDEBUG.setToolTipText("Enables extension to output debug information (internal technical stuff)")
                    self.callingClass.menuItemDEBUG.setSelected(debug)
                    menuO.add(self.callingClass.menuItemDEBUG)

                    menuItemDeactivate = JMenuItem("Deactivate Extension")
                    menuItemDeactivate.addActionListener(saveMyActionListener)
                    menuItemDeactivate.setToolTipText("Deactivates this extension and also the HomePage 'widget' (will reactivate upon MD restart)")
                    menuItemDeactivate.setSelected(True)
                    menuO.add(menuItemDeactivate)

                    menuItemUninstall = JMenuItem("Uninstall Extension")
                    menuItemUninstall.addActionListener(saveMyActionListener)
                    menuItemUninstall.setToolTipText("Uninstalls and removes this extension (and also the HomePage 'widget'). This is permanent until you reinstall...")
                    menuItemUninstall.setSelected(True)
                    menuO.add(menuItemUninstall)

                    self.callingClass.mainMenuBar.add(menuO)

                    menuA = JMenu("About")

                    menuItemA = JMenuItem("About")
                    menuItemA.setToolTipText("About...")
                    menuItemA.addActionListener(saveMyActionListener)
                    menuItemA.setEnabled(True)
                    menuA.add(menuItemA)

                    menuItemH = JMenuItem("Help")
                    menuItemH.setToolTipText("Help - show the readme.txt file...")
                    menuItemH.addActionListener(saveMyActionListener)
                    menuItemH.setEnabled(True)
                    menuA.add(menuItemH)

                    self.callingClass.mainMenuBar.add(menuA)

                    if not Platform.isOSX():
                        self.callingClass.theFrame.setJMenuBar(self.callingClass.mainMenuBar)

                    self.callingClass.theFrame.pack()
                    self.callingClass.theFrame.setLocationRelativeTo(None)

                    self.callingClass.jlst.requestFocusInWindow()           # Set initial focus on the account selector

                    self.callingClass.theFrame.setVisible(False)

                    if (not Platform.isOSX()):
                        self.callingClass.moneydanceContext.getUI().getImages()
                        self.callingClass.theFrame.setIconImage(MDImages.getImage(self.callingClass.moneydanceContext.getUI().getMain().getSourceInformation().getIconResource()))


            if not SwingUtilities.isEventDispatchThread():
                myPrint("DB",".. build_main_frame() Not running within the EDT so calling via BuildMainFrameRunnable()...")
                SwingUtilities.invokeLater(BuildMainFrameRunnable(self))
            else:
                myPrint("DB",".. build_main_frame() Already within the EDT so calling naked...")
                BuildMainFrameRunnable(self).run()



        def decodeCommand(self, passedEvent):                                                                           # noqa
            param = "(not set)"
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

        # .invoke() is called when this extension is selected on the Extension Menu.
        # the eventString is set to the string set when the class self-installed itself via .registerFeature() - e.g. "showConfig"
        def invoke(self, eventString=""):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
            myPrint("DB","Extension .invoke() received command: %s. Passing onto .handleEvent()" %(eventString))

            result = self.handle_event(eventString, True)

            myPrint("DB", "Exiting ", inspect.currentframe().f_code.co_name, "()")

            return result

        def getMoneydanceUI(self):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

            if not self.isUIavailable:
                myPrint("DB","Checking to see whether the Moneydance UI is loaded yet....")

                # .getUI() actually tries to load the UI. This is the only way to check...
                f_ui = self.moneydanceContext.getClass().getDeclaredField("ui")
                f_ui.setAccessible(True)
                f_ui_result = f_ui.get(self.moneydanceContext)
                f_ui.setAccessible(False)
                if f_ui_result is None or f_ui_result.firstMainFrame is None:
                    myPrint("DB",".. Nope - the Moneydance UI is NOT yet loaded (fully)..... so exiting...")
                    return False

                if self.moneydanceContext.getCurrentAccountBook() is None:
                    myPrint("DB",".. The UI is loaded, but the dataset is not yet loaded... so exiting ...")
                    return False

                try:
                    # I'm calling this on firstMainFrame rather than just .getUI().setStatus() to confirm GUI is properly loaded.....
                    self.moneydanceContext.getUI().firstMainFrame.setStatus(">> StuWareSoftSystems - %s runtime extension installing......." %(self.myModuleID.capitalize()),-1.0)
                except:
                    myPrint("DB","ERROR - failed using the UI..... will just exit for now...")
                    return False

                myPrint("DB","Success - the Moneydance UI is loaded.... Extension can execute properly now...!")

                setDefaultFonts()
                self.build_main_frame()
                self.isUIavailable = True
            else:
                myPrint("DB","..UI is available - returning True....")

            return True


        class UnloadUninstallSwingWorker(SwingWorker):
            def __init__(self, callingClass, unload=False, uninstall=False):
                self.callingClass = callingClass
                self.unload = unload
                self.uninstall = uninstall

            # noinspection PyMethodMayBeStatic
            def doInBackground(self):
                myPrint("DB", "In UnloadUninstallSwingWorker()", inspect.currentframe().f_code.co_name, "()")

                if self.unload:
                    myPrint("DB","... calling .unloadMyself()")
                    self.callingClass.unloadMyself()
                elif self.uninstall:
                    myPrint("DB","... calling .removeMyself()")
                    self.callingClass.removeMyself()

            # noinspection PyMethodMayBeStatic
            def done(self):
                myPrint("DB", "In UnloadUninstallSwingWorker()", inspect.currentframe().f_code.co_name, "()")
                myPrint("DB","++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

        def handle_event(self, appEvent, lPassedFromInvoke=False):

            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))

            if self.alreadyClosed:
                myPrint("DB","....alreadyClosed (deactivated by user) but the listener is still here (MD EVENT %s CALLED).. - Ignoring and returning back to MD.... (restart to clear me out)..." %(appEvent))
                return

            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
            myPrint("DB","Extension .handle_event() received command: %s (from .invoke() flag = %s)" %(appEvent, lPassedFromInvoke))

            if appEvent == "md:file:closing" or appEvent == "md:file:closed":

                if self.saveMyHomePageView.lastBookUsed is not None:
                    myPrint("DB",".. Dataset closing... releasing references to last book used (%s)" %(self.saveMyHomePageView.lastBookUsed))
                    self.saveMyHomePageView.lastBookUsed = None

                self.parametersLoaded = self.configPanelOpen = False
                if self.theFrame is not None and self.theFrame.isVisible():
                    myPrint("DB","Requesting application JFrame to go invisible...")
                    SwingUtilities.invokeLater(GenericVisibleRunnable(self.theFrame, False))

            elif (appEvent == "md:file:opened"):  # This is the key event when a file is opened
                myPrint("DB","%s Checking to see if UI loaded and create application Frame" %(appEvent))
                self.getMoneydanceUI()  # Check to see if the UI & dataset are loaded.... If so, create the JFrame too...

            elif (appEvent == "%s:customevent:showConfig" %self.myModuleID):
                myPrint("DB","%s Config screen requested - I might show it conditions are appropriate" %(appEvent))

                self.getMoneydanceUI()  # Check to see if the UI & dataset are loaded.... If so, create the JFrame too...

                if self.theFrame is not None and self.isUIavailable and self.theFrame.isActiveInMoneydance:
                    myPrint("DB","... launching the config screen...")
                    SwingUtilities.invokeLater(GenericVisibleRunnable(self.theFrame, True, True))
                else:
                    myPrint("DB", "Sorry, conditions are not right to allow console. Ignoring request....")
                    myPrint("DB", "self.theFrame: %s" %(self.theFrame))
                    myPrint("DB", "self.isUIavailable: %s" %(self.isUIavailable))
                    myPrint("DB", "self.theFrame.isActiveInMoneydance: %s" %(self.theFrame.isActiveInMoneydance))       # noqa

            elif (appEvent == "%s:customevent:close" %(self.myModuleID)):
                if debug:
                    myPrint("DB","@@ Custom event %s triggered.... Will call .unloadMyself() to deactivate (via SwingWorker)...." %(appEvent))
                else:
                    myPrint("B","@@ %s triggered - So I will deactivate myself...." %(appEvent))

                sw = self.UnloadUninstallSwingWorker(self,unload=True)
                sw.execute()
                myPrint("DB","Back from calling .unloadMyself() via SwingWorker to deactivate... ;-> ** I'm getting out quick! **")

            elif (appEvent == "%s:customevent:uninstall" %(self.myModuleID)):
                if debug:
                    myPrint("DB","@@ Custom event %s triggered.... Will call .removeMyself() to uninstall (via SwingWorker)...." %(appEvent))
                else:
                    myPrint("B","@@ %s triggered - So I will uninstall/remove myself...." %(appEvent))

                sw = self.UnloadUninstallSwingWorker(self,uninstall=True)
                sw.execute()
                myPrint("DB","Back from calling .removeMyself() via SwingWorker to deactivate... ;-> ** I'm getting out quick! **")

            else:
                myPrint("DB","@@ Ignoring handle_event: %s (from .invoke() = %s) @@" %(appEvent,lPassedFromInvoke))

            if lPassedFromInvoke: return True

            return

        def unload(self, lFromDispose=False):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

            myPrint("B","@@ Extension Unload called, either a uninstall or reinstall (or deactivate request)... Deactivate and unload...")

            self.theFrame.isActiveInMoneydance = False

            self.alreadyClosed = True

            if not lFromDispose:
                if not SwingUtilities.isEventDispatchThread():
                    SwingUtilities.invokeLater(GenericDisposeRunnable(self.theFrame))
                    myPrint("DB", "Pushed dispose() - via SwingUtilities.invokeLater() - Hopefully I will close to allow re-installation...\n")
                else:
                    GenericDisposeRunnable(self.theFrame).run()
                    myPrint("DB", "Called dispose() (direct as already on EDT) - Hopefully I will close to allow re-installation...\n")

            self.saveMyHomePageView.unload()
            myPrint("DB","@@ Called HomePageView.unload()")

            self.moneydanceContext.getUI().setStatus(">> StuWareSoftSystems - thanks for using >> %s....... >> I am now unloaded...." %(myScriptName),0)

            myPrint("DB","... Completed unload routines...")

    class MyHomePageView(HomePageView):

        def __init__(self, extensionClass):

            self.myModuleID = myModuleID

            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

            # super(HomePageView, self).__init__()                                                                        # noqa

            self.thisView = self
            self.view = None

            self.myModuleID = myModuleID
            self.theBook = None
            self.lastBookUsed = None
            self.i_am_active = False
            self.is_unloaded = False
            self.extensionClass = extensionClass

            # my attempt to replicate Java's 'synchronized' statements
            self.lock = threading.Lock()

        # noinspection PyMethodMayBeStatic
        def getID(self): return u"%s (HomePageView)" %(self.myModuleID.capitalize())                                    # noqa

        # noinspection PyMethodMayBeStatic
        def __str__(self): return self.getID()

        # noinspection PyMethodMayBeStatic
        def __repr__(self): return self.__str__()

        # noinspection PyMethodMayBeStatic
        def toString(self): return self.__str__()

        # Called by Moneydance; Must returns a (swing JComponent) GUI component that provides a view for the given data file.
        def getGUIView(self, book):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
            myPrint("DB","HomePageView widget: .getGUIView(%s) (theBook currently: %s, lastBook: %s)" %(book, self.theBook, self.lastBookUsed))

            if self.is_unloaded:
                myPrint("DB","HomePageView is unloaded, so ignoring....")
                return None     # this hides the widget from the home screen

            self.theBook = book

            if self.theBook is not None and self.theBook != self.lastBookUsed:
                myPrint("DB","Book has changed, calling for parameters to be loaded..... (if not already set)....")
                self.extensionClass.load_saved_parameters()
                self.lastBookUsed = self.theBook

            if self.view is not None:
                return self.view

            class CreateViewPanelRunnable(Runnable):

                def __init__(self, callingClass):
                    self.callingClass = callingClass

                # noinspection PyMethodMayBeStatic
                def run(self):
                    global debug
                    myPrint("DB","Inside CreateViewPanelRunnable().... Calling creating ViewPanel..")
                    self.callingClass.view = self.callingClass.ViewPanel(book, self.callingClass)

            with self.lock:
                if not SwingUtilities.isEventDispatchThread():
                    myPrint("DB",".. Not running within the EDT so calling via CreateViewPanelRunnable()...")
                    SwingUtilities.invokeAndWait(CreateViewPanelRunnable(self))
                else:
                    myPrint("DB",".. Already within the EDT so calling CreateViewPanelRunnable() naked...")
                    CreateViewPanelRunnable(self).run()

                return self.view


        class ViewPanel(JPanel, AccountListener, JLinkListener):

            # Account Listener Methods
            def accountModified(self, paramAccount):                                                                        # noqa
                myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
                myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
                myPrint("DB", "...calling refresh()")
                self.refresh()

            def accountBalanceChanged(self, paramAccount):                                                                  # noqa
                myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
                myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
                myPrint("DB", "...calling refresh()")
                self.refresh()

            def accountDeleted(self, paramAccount):                                                                         # noqa
                myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
                myPrint("DB","... ignoring....")

            def accountAdded(self, paramAccount):                                                                           # noqa
                myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
                myPrint("DB","... ignoring....")

            def linkActivated(self, link, event):
                myPrint("DB", "In %s.%s() - Event: %s" %(self, inspect.currentframe().f_code.co_name, event))
                myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
                myPrint("DB", "... link: %s" %(link))

                if isinstance(link, (str, unicode)):
                    if (link.lower() == "showConfig".lower()):
                        myPrint("DB",".. calling .showURL() to call up showConfig panel")
                        self.callingClass.extensionClass.moneydanceContext.showURL("moneydance:fmodule:%s:%s:customevent:showConfig" %(self.callingClass.myModuleID,self.callingClass.myModuleID))

            # The Runnable for CollapsibleRefresher()
            class GUIRunnable(Runnable):

                def __init__(self, callingClass):
                    myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
                    self.callingClass = callingClass

                # noinspection PyMethodMayBeStatic
                def run(self):
                    global debug

                    myPrint("DB","Inside GUIRunnable.... Calling .reallyRefresh()..")
                    self.callingClass.reallyRefresh()

            def getBalancesBuildView(self, dec):
                myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
                myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

                if self.callingClass.is_unloaded:
                    myPrint("DB","HomePageView is unloaded, so ignoring & returning zero....")
                    return 0

                if self.callingClass.theBook is None:
                    myPrint("DB","HomePageView widget: book is None - returning zero...")
                    return 0

                if len(self.callingClass.extensionClass.savedAccountListUUIDs) < 1:
                    myPrint("DB","...savedAccountListUUIDs is empty - returning zero...")
                    return 0

                myPrint("DB","HomePageView widget: (re)calculating balances")

                baseCurr = self.callingClass.theBook.getCurrencies().getBaseType()

                accountsToShow = []
                for accID in self.callingClass.extensionClass.savedAccountListUUIDs:
                    myPrint("DB","...looking for Account with UUID: %s" %accID)
                    acct = AccountUtil.findAccountWithID(self.callingClass.theBook.getRootAccount(), accID)
                    if acct is not None:
                        myPrint("DB","...found and adding account to list: %s" %acct)
                        accountsToShow.append(acct)
                    else:
                        myPrint("DB","...odd - Account with UUID %s not found..? Skipping this one...." %(accID))

                totalBalance = 0
                for acct in accountsToShow:
                    acctCurr = acct.getCurrencyType()
                    # 0 = "Balance", 1 = "Current Balance", 2 = "Cleared Balance"
                    if self.callingClass.extensionClass.savedBalanceType == 0:
                        bal = acct.getBalance()
                        myPrint("DB","HomePageView widget: adding acct: %s Balance: %s" %((acct.getFullAccountName()), rpad(acctCurr.formatSemiFancy(bal, dec),12)))
                    elif self.callingClass.extensionClass.savedBalanceType == 1:
                        bal = acct.getCurrentBalance()
                        myPrint("DB","HomePageView widget: adding acct: %s Current Balance: %s" %((acct.getFullAccountName()), rpad(acctCurr.formatSemiFancy(bal, dec),12)))
                    elif self.callingClass.extensionClass.savedBalanceType == 2:
                        bal = acct.getClearedBalance()
                        myPrint("DB","HomePageView widget: adding acct: %s Cleared Balance: %s" %((acct.getFullAccountName()), rpad(acctCurr.formatSemiFancy(bal, dec),12)))
                    else:
                        bal = 0
                        myPrint("B","@@ HomePageView widget - INVALID BALANCE TYPE: %s?" %(self.callingClass.extensionClass.savedBalanceType))

                    if bal != 0 and acctCurr != baseCurr:
                        balConv = CurrencyUtil.convertValue(bal, acctCurr, baseCurr)
                        myPrint("DB",".. Converted %s to %s (base)" %(acctCurr.formatSemiFancy(bal, dec), baseCurr.formatSemiFancy(balConv, dec)))
                        totalBalance += balConv
                    else:
                        totalBalance += bal

                    # noinspection PyUnresolvedReferences
                    if acct.getAccountType() == Account.AccountType.INVESTMENT:
                        for securityAcct in acct.getSubAccounts():  # There's only one level of security sub accounts
                            securityCurr = securityAcct.getCurrencyType()
                            relCurr = securityCurr.getCurrencyParameter(None, None, "relative_to_currid", acctCurr)
                            myPrint("DB",".. Security curr: %s Relative curr: %s Account curr: %s Base Curr: %s" %(securityCurr, relCurr, acctCurr, baseCurr))

                            if self.callingClass.extensionClass.savedBalanceType == 0:
                                bal = securityAcct.getBalance()
                                myPrint("DB","HomePageView widget: adding security: %s Share Balance: %s" %((securityAcct.getAccountName()), rpad(securityCurr.formatSemiFancy(bal, dec),12)))
                            elif self.callingClass.extensionClass.savedBalanceType == 1:
                                bal = securityAcct.getCurrentBalance()
                                myPrint("DB","HomePageView widget: adding security: %s Current Share Balance: %s" %((securityAcct.getAccountName()), rpad(securityCurr.formatSemiFancy(bal, dec),12)))
                            elif self.callingClass.extensionClass.savedBalanceType == 2:
                                bal = securityAcct.getClearedBalance()
                                myPrint("DB","HomePageView widget: adding security: %s Cleared Share Balance: %s" %((securityAcct.getAccountName()), rpad(securityCurr.formatSemiFancy(bal, dec),12)))
                            else:
                                bal = 0
                                myPrint("B","@@ HomePageView widget - INVALID BALANCE TYPE: %s?" %(self.callingClass.extensionClass.savedBalanceType))

                            if bal != 0:
                                # securityValue = CurrencyUtil.convertValue(bal, securityCurr, relCurr)
                                # myPrint("DB",".. Converted %s to %s (base)" %(securityCurr.formatSemiFancy(bal, dec), relCurr.formatSemiFancy(securityValue, dec)))

                                securityValue = CurrencyUtil.convertValue(bal, securityCurr, baseCurr)
                                myPrint("DB",".. Converted %s to %s (base)" %(securityCurr.formatSemiFancy(bal, dec), baseCurr.formatSemiFancy(securityValue, dec)))

                                totalBalance += securityValue

                del accountsToShow

                myPrint("DB",".. Calculated a total balance of %s" %(totalBalance/100.0))
                return totalBalance

            def __init__(self, book, callingClass):

                self.callingClass = callingClass
                self.refresher = None
                self.book = book

                super(JPanel, self).__init__()                                                                          # noqa

                myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
                myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

                self.refresher = CollapsibleRefresher(self.GUIRunnable(self))

                self.nameBorder = EmptyBorder(3, 14, 3, 0)
                self.amountBorder = EmptyBorder(3, 0, 3, 14)

                gridbag = GridBagLayout()
                self.setLayout(gridbag)

                self.setOpaque(False)
                self.setBorder(MoneydanceLAF.homePageBorder)

                self.listPanel = JPanel(gridbag)
                self.add(self.listPanel, GridC.getc(0, 1).wx(1.0).fillboth())
                self.add(Box.createVerticalStrut(2), GridC.getc(0, 2).wy(1.0))
                self.listPanel.setOpaque(False)

                if self.callingClass.i_am_active:
                    self.activate()

            def activate(self):
                myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
                myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
                myPrint("DB",".. activate().. Adding myself as an (HomePageView) account listener...")

                self.callingClass.extensionClass.moneydanceContext.getCurrentAccountBook().addAccountListener(self)
                myPrint("DB",".. and calling refresh()..")
                self.refresh()

            def deactivate(self):
                myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))

                myPrint("DB",".. deactivate().. Removing myself as an (HomePageView) account listener...")
                myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
                self.callingClass.extensionClass.moneydanceContext.getCurrentAccountBook().removeAccountListener(self)

            def refresh(self):
                myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
                myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
                myPrint("DB", "HomePageView(ViewPanel): .refresh()..")

                if self.callingClass.is_unloaded:
                    myPrint("DB","HomePageView is unloaded, so ignoring....")
                    return None

                if self.callingClass.extensionClass.moneydanceContext.getUI().getSuspendRefreshes():
                    myPrint("DB","... .getUI().getSuspendRefreshes() is True so ignoring...")
                    return

                if self.refresher is not None:
                    myPrint("DB","... calling refresher.enqueueRefresh()")
                    self.refresher.enqueueRefresh()
                else:
                    myPrint("DB","... refresher is None - just returning without refresh...")

            def reallyRefresh(self):

                myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
                myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
                myPrint("DB", "HomePageView widget: .reallyRefresh().. rebuilding the panel and contents...")

                # launch -invoke[_and_quit] can cause progam to fall over as it's shutting down.. Detect None condition
                if self.callingClass.extensionClass.moneydanceContext.getCurrentAccountBook() is None:
                    myPrint("DB", "@@ .reallyRefresh() detected .getCurrentAccountBook() is None... Perhaps -invoke[_and_quit].. Just ignore and exit this refresh..")
                    return

                self.listPanel.removeAll()

                dec = self.callingClass.extensionClass.moneydanceContext.getPreferences().getDecimalChar()
                baseCurr = self.callingClass.extensionClass.moneydanceContext.getCurrentAccountBook().getCurrencies().getBaseType()

                nameLabel = JLinkLabel("%s" %(self.callingClass.extensionClass.savedWidgetName), "showConfig", JLabel.LEFT)

                netAmount = self.getBalancesBuildView(dec)

                netTotalLbl = JLinkLabel(baseCurr.formatFancy(netAmount, dec), "showConfig", JLabel.RIGHT)
                netTotalLbl.setFont((self.callingClass.extensionClass.moneydanceContext.getUI().getFonts()).mono)

                if netAmount < 0:
                    netTotalLbl.setForeground(self.callingClass.extensionClass.moneydanceContext.getUI().getColors().negativeBalFG)
                else:
                    if  "default" == ThemeInfo.themeForID(self.callingClass.extensionClass.moneydanceContext.getUI(), self.callingClass.extensionClass.moneydanceContext.getUI().getPreferences().getSetting("gui.current_theme", ThemeInfo.DEFAULT_THEME_ID)).getThemeID():
                        netTotalLbl.setForeground(self.callingClass.extensionClass.moneydanceContext.getUI().getColors().budgetHealthyColor)
                    else:
                        netTotalLbl.setForeground(self.callingClass.extensionClass.moneydanceContext.getUI().getColors().positiveBalFG)

                nameLabel.setBorder(self.nameBorder)
                netTotalLbl.setBorder(self.amountBorder)

                nameLabel.setDrawUnderline(False)
                netTotalLbl.setDrawUnderline(False)

                self.listPanel.add(nameLabel, GridC.getc().xy(0, 1).wx(1.0).fillboth().pady(2))
                self.listPanel.add(netTotalLbl, GridC.getc().xy(1, 1).fillboth().pady(2))

                nameLabel.addLinkListener(self)
                netTotalLbl.addLinkListener(self)

                myPrint("DB", "... SwingUtilities.isEventDispatchThread() within .reallyRefresh() returns: %s - about to call .setVisible(True)" %(SwingUtilities.isEventDispatchThread()))
                self.setVisible(True)       # I think we are already on the Swing Event Dispatch Thread (EDT) so can just call directly....

                # self.validate()

                self.invalidate()
                parent = self.getParent()
                while parent is not None:
                    parent.repaint()
                    parent.validate()
                    parent = parent.getParent()

            def updateUI(self):
                myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
                super(MyHomePageView.ViewPanel, self).updateUI()                                                        # noqa
                self.refresh()

        # Sets the view as active or inactive. When not active, a view should not have any registered listeners
        # with other parts of the program. This will be called when an view is added to the home page,
        # or the home page is refreshed after not being visible for a while.


        def setActive(self, active):

            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
            myPrint("DB","HomePageView widget: .setActive(%s) (theBook: %s, lastBook: %s)" %(active,self.theBook, self.lastBookUsed))

            if self.is_unloaded:
                myPrint("DB","HomePageView is unloaded, so ignoring....")
                self.i_am_active = False
                return

            self.i_am_active = active

            if (self.view is not None):
                if (active):
                    myPrint("DB","... calling view.activate()")
                    self.view.activate()
                else:
                    myPrint("DB","... calling view.deactivate()")
                    self.view.deactivate()
            else:
                myPrint("DB","...view is None so ignoring any (de)activate command..")

        # Forces a refresh of the information in the view. For example, this is called after the preferences are updated.
        def refresh(self):                                                                                              # noqa
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
            myPrint("DB", "HomePageView widget: .refresh() (theBook: %s, lastBook: %s)" %(self.theBook, self.lastBookUsed))

            if self.is_unloaded:
                myPrint("DB","HomePageView is unloaded, so ignoring....")
                return None

            if (self.view is not None):
                myPrint("DB","...calling view.refresh()")
                self.view.refresh()


        # Called when the view should clean up everything. For example, this is called when a file is closed and the GUI
        #  is reset. The view should disconnect from any resources that are associated with the currently opened data file.


        def reset(self):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
            myPrint("DB", "HomePageView widget: .reset() - releasing resources to book.... (theBook: %s, lastBook: %s)" %(self.theBook, self.lastBookUsed))

            if self.is_unloaded:
                myPrint("DB","HomePageView is unloaded, so ignoring....")
                return None

            with self.lock:
                self.setActive(False)
                self.lastBookUsed = None
                self.theBook = None
                self.view = None
                if self.extensionClass is not None:
                    self.extensionClass.configPanelOpen = False

        def unload(self):   # This is my own method (not overridden from HomePageView)
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
            myPrint("B", "HomePageView widget: .unload() extension called - so I will wipe the panel and deactivate myself....")
            if self.view is not None: self.view.removeAll()  # Hopefully already within the EDT....
            self.reset()
            self.is_unloaded = True
            # self.extensionClass = None

    # Don't worry about the Swing EDT for initialisation... The GUI won't be loaded on MD startup anyway....
    myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

    # Moneydance queries this variable after script exit and uses it to install the extension
    moneydance_extension = NetAccountBalancesExtension()

    myPrint("B", "StuWareSoftSystems - ", myScriptName, " initialisation routines ending......")

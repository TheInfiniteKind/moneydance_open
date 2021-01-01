#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# extract_investment_transactions_csv.py - build: 1006 - November 2020 - Stuart Beesley
###############################################################################
# MIT License
#
# Copyright (c) 2020 Stuart Beesley - StuWareSoftSystems
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

# This script extracts investment transactions (register) to csv file
# Use in Moneydance Menu Window->Show Moneybot Console >> Open Script >> RUN
# NOTE: MiscExp & MiscInc with fees are just wrong... MD handles them incorrectly. I try to replicate MD until it's fixed

# Stuart Beesley Created 2020-11-01 tested on MacOS - MD2021 onwards - StuWareSoftSystems....
# v0.1 beta - Initial release; v0.2 beta - fixes; v0.3 beta - added options for opening balances and splits
# v0.4 beta - changed to getBalance() to include future dated txns; also tweaked to use MD decimal point
# v1 - Public release
# v1a - Fix small data issue on Memo fields with Opening Balances; also added Bal to Amount field (user request).
# v1b - Small tweak to input parameter field (cosmetic only)
# v1b - Add BOM mark to CSV file so Excel opens CSV with double-click (and changed open() to 'w' from 'wb'). Strip ASCII when requested.
# v1c - Cosmetic change to display; catch pickle.load() error (when from restored file)
# v1d - Reverting to open() 'wb' - fix Excel CRLF double line on Windows issue
# v1e - Convert pickle to unencrypted file
# v1f - Slight tweak to myParameters; changed __file__ usage; code cleanup; version change

# Build: 1000 - IntelliJ code cleanup; made Extension ready; refresh bits with common code - no functional changes
# Build: 1000 - no functional changes; Added code fix for extension runtime to set moneydance variables (if not set)
# Build: 1000 - all print functions changed to work headless; added some popup warnings...; streamlined common code
# Build: 1000 - optional parameter whether to write BOM to export file; added date/time to console log
# Build: 1001 - Enhanced MyPrint to catch unicode utf-8 encode/decode errors
# Build: 1002 - fixed raise(Exception) clauses ;->
# Build: 1003 - fixed last column which was getting *s replacing ,s in error; moved save of parameters earlier...
# Build: 1004 - updated common codeset; leverage moneydance fonts
# Build: 1005 - Removed TxnSortOrder from common code
# Build: 1005 - Fix for Jython 2.7.1 where csv.writer expects a 1-byte string delimiter, not unicode....
# Build: 1005 - Write parameters to csv extract; added fake JFrame() for icons; moved parameter save earlier
# Build: 1006 - Renames of Module, REPO, url and Moneydance...

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

from com.moneydance.util import Platform
from com.moneydance.awt import JTextPanel, GridC, JDateField
from com.moneydance.apps.md.view.gui import MDImages

from com.infinitekind.util import DateUtil, CustomDateFormat
from com.infinitekind.moneydance.model import *
from com.infinitekind.moneydance.model import AccountUtil, AcctFilter, CurrencyType, CurrencyUtil
from com.infinitekind.moneydance.model import Account, Reminder, ParentTxn, SplitTxn, TxnSearch, InvestUtil, TxnUtil

from javax.swing import JButton, JScrollPane, WindowConstants, JFrame, JLabel, JPanel, JComponent, KeyStroke, JDialog, JComboBox
from javax.swing import JOptionPane, JTextArea, JMenuBar, JMenu, JMenuItem, AbstractAction, JCheckBoxMenuItem, JFileChooser
from javax.swing import JTextField, JPasswordField, Box, UIManager, JTable
from javax.swing.text import PlainDocument
from javax.swing.border import EmptyBorder

from java.awt import Color, Dimension, FileDialog, FlowLayout, Toolkit, Font, GridBagLayout, GridLayout
from java.awt import BorderLayout, Dialog, Insets
from java.awt.event import KeyEvent, WindowAdapter, InputEvent

from java.text import DecimalFormat, SimpleDateFormat
from java.util import Calendar, ArrayList
from java.lang import System, Double, Math, Character
from java.io import FileNotFoundException, FilenameFilter, File, FileInputStream, FileOutputStream, IOException, StringReader
from java.io import BufferedReader, InputStreamReader
if isinstance(None, (JDateField,CurrencyUtil,Reminder,ParentTxn,SplitTxn,TxnSearch, JComboBox,
                     JTextArea, JMenuBar, JMenu, JMenuItem, JCheckBoxMenuItem, JFileChooser, JDialog,
                     JButton, FlowLayout, InputEvent, ArrayList, File, IOException, StringReader, BufferedReader,
                     InputStreamReader, Dialog, JTable, BorderLayout, Double, InvestUtil,
                     AccountUtil, AcctFilter, CurrencyType, Account, TxnUtil, JScrollPane, WindowConstants, JFrame,
                     JComponent, KeyStroke, AbstractAction, UIManager, Color, Dimension, Toolkit, KeyEvent,
                     WindowAdapter, CustomDateFormat, SimpleDateFormat, Insets)): pass
if codecs.BOM_UTF8 is not None: pass
if csv.QUOTE_ALL is not None: pass
if datetime.MINYEAR is not None: pass
if Math.max(1,1): pass
# END COMMON IMPORTS ###################################################################################################

# COMMON GLOBALS #######################################################################################################
global debug  # Set to True if you want verbose messages, else set to False....
global myParameters, myScriptName, version_build, _resetParameters, i_am_an_extension_so_run_headless, moneydanceIcon
global lPickle_version_warning, decimalCharSep, groupingCharSep, lIamAMac, lGlobalErrorDetected
# END COMMON GLOBALS ###################################################################################################

# SET THESE VARIABLES FOR ALL SCRIPTS ##################################################################################
version_build = "1006"                                                                                              # noqa
myScriptName = "extract_investment_transactions_csv.py(Extension)"                                                  # noqa
debug = False                                                                                                       # noqa
myParameters = {}                                                                                                   # noqa
_resetParameters = False                                                                                            # noqa
lPickle_version_warning = False                                                                                     # noqa
lIamAMac = False                                                                                                    # noqa
lGlobalErrorDetected = False																						# noqa
# END SET THESE VARIABLES FOR ALL SCRIPTS ##############################################################################

# >>> THIS SCRIPT'S IMPORTS ############################################################################################
# NONE...
# >>> END THIS SCRIPT'S IMPORTS ########################################################################################

# >>> THIS SCRIPT'S GLOBALS ############################################################################################

# Saved to parameters file
global __extract_investment_transactions
global hideHiddenSecurities, hideInactiveAccounts, hideHiddenAccounts, lAllCurrency, filterForCurrency, lAllSecurity
global filterForSecurity, lAllAccounts, filterForAccounts, csvDelimiter, lIncludeOpeningBalances, lAdjustForSplits
global lStripASCII, scriptpath, userdateformat
global lWriteBOMToExportFile_SWSS

# Other used by program
global csvfilename, lDisplayOnly
global baseCurrency, sdf
global transactionTable, dataKeys, extract_investment_transactions_fake_frame_
# >>> END THIS SCRIPT'S GLOBALS ############################################################################################

# Set programmatic defaults/parameters for filters HERE.... Saved Parameters will override these now
# NOTE: You  can override in the pop-up screen
hideHiddenSecurities = True                                                                                         # noqa
hideInactiveAccounts = True                                                                                         # noqa
hideHiddenAccounts = True                                                                                           # noqa
lAllCurrency = True                                                                                                 # noqa
filterForCurrency = "ALL"                                                                                           # noqa
lAllSecurity = True                                                                                                 # noqa
filterForSecurity = "ALL"                                                                                           # noqa
lAllAccounts = True                                                                                                 # noqa
filterForAccounts = "ALL"                                                                                           # noqa
lIncludeOpeningBalances = True                                                                                      # noqa
lAdjustForSplits = True                                                                                             # noqa
userdateformat = "%Y/%m/%d"                                                                                         # noqa
                                                                                                                    # noqa
lStripASCII = False                                                                                                 # noqa
csvDelimiter = ","                                                                                                  # noqa
lWriteBOMToExportFile_SWSS = True                                                                                   # noqa

scriptpath = ""                                                                                                     # noqa
extract_investment_transactions_fake_frame_ = None                                                                  # noqa
extract_filename="extract_investment_transactions.csv"
# >>> END THIS SCRIPT'S GLOBALS ############################################################################################

# COMMON CODE ##########################################################################################################
i_am_an_extension_so_run_headless = False                                                                           # noqa
try:
    myScriptName = os.path.basename(__file__)
except:
    i_am_an_extension_so_run_headless = True                                                                        # noqa

scriptExit = """
----------------------------------------------------------------------------------------------------------------------
Thank you for using %s! The author has other useful Extensions / Moneybot Python scripts available...:

Extension (.mxt) format only:
toolbox                                 View Moneydance settings, diagnostics, fix issues, change settings and much more

Extension (.mxt) and Script (.py) Versions available:
stockglance2020                         View summary of Securities/Stocks on screen, total by Security, export to csv 
extract_reminders_csv                   View reminders on screen, edit if required, extract all to csv
extract_currency_history_csv            Extract currency history to csv
extract_investment_transactions_csv     Extract investment transactions to csv
extract_account_registers_csv           Extract Account Register(s) to csv along with any attachments

Visit: https://yogi1967.github.io/MoneydancePythonScripts/ (Author's site)
----------------------------------------------------------------------------------------------------------------------
""" %myScriptName

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


myPrint("B", "StuWareSoftSystems...")
myPrint("B", myScriptName, ": Python Script Initialising.......", "Build:", version_build)

def is_moneydance_loaded_properly():
    global debug

    if debug or moneydance_data is None or moneydance_ui is None:
        for theClass in ["moneydance",moneydance], ["moneydance_ui",moneydance_ui], ["moneydance_data",moneydance_data]:
            myPrint("B","Moneydance Objects now....: Class: %s %s@{:x}".format(System.identityHashCode(theClass[1])) %(pad(theClass[0],20), theClass[1].__class__))
        myPrint("P","")

    if moneydance is not None and moneydance_data is not None and moneydance_ui is not None:                        # noqa
        if debug: myPrint("B","Success - Moneydance variables are already set....")
        return

    # to cope with being run as Extension.... temporary
    if moneydance is not None and moneydance_data is None and moneydance_ui is None:                                # noqa
        myPrint("B", "@@@ Moneydance variables not set (run as extension?) - attempting to manually set @@@")
        exec "global moneydance_ui;" + "moneydance_ui=moneydance.getUI();"
        exec "global moneydance_data;" + "moneydance_data=moneydance.getCurrentAccount().getBook();"

        for theClass in ["moneydance",moneydance], ["moneydance_ui",moneydance_ui], ["moneydance_data",moneydance_data]:
            myPrint("B","Moneydance Objects after manual setting....: Class: %s %s@{:x}".format(System.identityHashCode(theClass[1])) %(pad(theClass[0],20), theClass[1].__class__))
        myPrint("P","")

    return


is_moneydance_loaded_properly()


def getMonoFont():
    global debug

    try:
        theFont = moneydance_ui.getFonts().code
        if debug: myPrint("B","Success setting Font set to Moneydance code: %s" %theFont)
    except:
        theFont = Font("monospaced", Font.PLAIN, 15)
        if debug: myPrint("B","Failed to Font set to Moneydance code - So using: %s" %theFont)

    return theFont

def getTheSetting(what):
    x = moneydance_ui.getPreferences().getSetting(what, None)
    if not x or x == "": return None
    return what + ": " + str(x)

def get_home_dir():
    homeDir = None

    # noinspection PyBroadException
    try:
        if Platform.isOSX():
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

    if not homeDir: homeDir = "?"
    return homeDir

def getDecimalPoint(lGetPoint=False, lGetGrouping=False):
    global debug

    decimalFormat = DecimalFormat.getInstance()
    # noinspection PyUnresolvedReferences
    decimalSymbols = decimalFormat.getDecimalFormatSymbols()

    if not lGetGrouping: lGetPoint = True
    if lGetGrouping and lGetPoint: return "error"

    if lGetPoint:
        _decimalCharSep = decimalSymbols.getDecimalSeparator()
        myPrint("D","Decimal Point Character:", _decimalCharSep)
        return _decimalCharSep

    if lGetGrouping:
        _groupingCharSep = decimalSymbols.getGroupingSeparator()
        myPrint("D","Grouping Separator Character:", _groupingCharSep)
        return _groupingCharSep

    return "error"


decimalCharSep = getDecimalPoint(lGetPoint=True)
groupingCharSep = getDecimalPoint(lGetGrouping=True)

# JOptionPane.DEFAULT_OPTION, JOptionPane.YES_NO_OPTION, JOptionPane.YES_NO_CANCEL_OPTION, JOptionPane.OK_CANCEL_OPTION
# JOptionPane.ERROR_MESSAGE, JOptionPane.INFORMATION_MESSAGE, JOptionPane.WARNING_MESSAGE, JOptionPane.QUESTION_MESSAGE, JOptionPane.PLAIN_MESSAGE

# Copies Moneydance_ui.showInfoMessage
def myPopupInformationBox(theParent=None, theMessage="What no message?!", theTitle="Info", theMessageType=JOptionPane.INFORMATION_MESSAGE):

    if theParent is None:
        if theMessageType == JOptionPane.PLAIN_MESSAGE or theMessageType == JOptionPane.INFORMATION_MESSAGE:
            icon_to_use=moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png")
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

def myPopupAskBackup(theParent=None, theMessage="What no message?!"):

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
        moneydance_ui.saveToBackup(None)
        return True

    elif response == 1:
        return True

    return False

# Copied Moneydance_ui.askQuestion
def myPopupAskQuestion(theParent=None,
                       theTitle="Question",
                       theQuestion="What?",
                       theOptionType=JOptionPane.YES_NO_OPTION,
                       theMessageType=JOptionPane.QUESTION_MESSAGE):

    icon_to_use = None
    if theParent is None:
        if theMessageType == JOptionPane.PLAIN_MESSAGE or theMessageType == JOptionPane.INFORMATION_MESSAGE:
            icon_to_use=moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png")

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
            icon_to_use=moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png")

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

    def __init__(self, theParent=None, theStatus="", theMessage="", theWidth=200, theTitle="Info", lModal=True, lCancelButton=False, OKButtonText="OK"):
        self.theParent = theParent
        self.theStatus = theStatus
        self.theMessage = theMessage
        self.theWidth = max(80,theWidth)
        self.theTitle = theTitle
        self.lModal = lModal
        self.lCancelButton = lCancelButton
        self.OKButtonText = OKButtonText
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
            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", WindowEvent)

            myPrint("DB", "JDialog Frame shutting down....")

            self.lResult[0] = False

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
            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event)

            self.lResult[0] = True

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
            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event)

            self.lResult[0] = False

            if self.theFakeFrame is not None:
                self.theDialog.dispose()
                self.theFakeFrame.dispose()
            else:
                self.theDialog.dispose()

            myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
            return

    def kill(self):

        global debug
        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

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

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        # Create a fake JFrame so we can set the Icons...
        if self.theParent is None:
            self.fakeJFrame = JFrame()
            self.fakeJFrame.setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE)
            self.fakeJFrame.setUndecorated(True)
            self.fakeJFrame.setVisible( False )
            if not Platform.isOSX():
                self.fakeJFrame.setIconImage(MDImages.getImage(moneydance_ui.getMain().getSourceInformation().getIconResource()))

        if self.lModal:
            # noinspection PyUnresolvedReferences
            self._popup_d = JDialog(self.theParent, self.theTitle, Dialog.ModalityType.APPLICATION_MODAL)
        else:
            # noinspection PyUnresolvedReferences
            self._popup_d = JDialog(self.theParent, self.theTitle, Dialog.ModalityType.MODELESS)

        self._popup_d.setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE)

        shortcut = Toolkit.getDefaultToolkit().getMenuShortcutKeyMaskEx()

        # Add standard CMD-W keystrokes etc to close window
        self._popup_d.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_W, shortcut), "close-window")
        self._popup_d.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_F4, shortcut), "close-window")
        self._popup_d.getRootPane().getActionMap().put("close-window", self.CancelButtonAction(self._popup_d, self.fakeJFrame,self.lResult))
        self._popup_d.addWindowListener(self.WindowListener(self._popup_d, self.fakeJFrame,self.lResult))

        if (not Platform.isMac()):
            # moneydance_ui.getImages()
            self._popup_d.setIconImage(MDImages.getImage(moneydance_ui.getMain().getSourceInformation().getIconResource()))

        displayJText = JTextArea(self.theMessage)
        # displayJText.setFont( getMonoFont() )
        displayJText.setEditable(False)
        displayJText.setLineWrap(False)
        displayJText.setWrapStyleWord(False)

        _popupPanel=JPanel()

        # maxHeight = 500
        _popupPanel.setLayout(GridLayout(0,1))
        _popupPanel.setBorder(EmptyBorder(8, 8, 8, 8))
        # _popupPanel.setMinimumSize(Dimension(self.theWidth, 0))
        # _popupPanel.setMaximumSize(Dimension(self.theWidth, maxHeight))

        if self.theStatus:
            _label1 = JLabel(pad(self.theStatus,self.theWidth-20))
            _label1.setForeground(Color.BLUE)
            _popupPanel.add(_label1)

        if displayJText.getLineCount()>5:
            myScrollPane = JScrollPane(displayJText, JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED,JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED)
            # myScrollPane.setMinimumSize(Dimension(self.theWidth-20, 10))
            # myScrollPane.setMaximumSize(Dimension(self.theWidth-20, maxHeight-100))
            myScrollPane.setWheelScrollingEnabled(True)
            _popupPanel.add(myScrollPane)
        else:
            _popupPanel.add(displayJText)

        if self.lModal or self.lCancelButton:
            buttonPanel = JPanel()
            buttonPanel.setLayout(FlowLayout(FlowLayout.CENTER))

            if self.lCancelButton:
                cancel_button = JButton("CANCEL")
                cancel_button.setPreferredSize(Dimension(100,40))
                cancel_button.setBackground(Color.LIGHT_GRAY)
                cancel_button.setBorderPainted(False)
                cancel_button.setOpaque(True)
                cancel_button.addActionListener( self.CancelButtonAction(self._popup_d, self.fakeJFrame,self.lResult) )
                buttonPanel.add(cancel_button)

            if self.lModal:
                ok_button = JButton(self.OKButtonText)
                if len(self.OKButtonText) <= 2:
                    ok_button.setPreferredSize(Dimension(100,40))
                else:
                    ok_button.setPreferredSize(Dimension(200,40))

                ok_button.setBackground(Color.LIGHT_GRAY)
                ok_button.setBorderPainted(False)
                ok_button.setOpaque(True)
                ok_button.addActionListener( self.OKButtonAction(self._popup_d, self.fakeJFrame, self.lResult) )
                buttonPanel.add(ok_button)

            _popupPanel.add(buttonPanel)

        self._popup_d.add(_popupPanel)

        self._popup_d.pack()
        self._popup_d.setLocationRelativeTo(None)
        self._popup_d.setVisible(True)

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

        return self.lResult[0]

def play_the_money_sound():

    # Seems to cause a crash on Virtual Machine with no Audio - so just in case....
    try:
        moneydance_ui.getSounds().playSound("cash_register.wav")
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


moneydanceIcon = MDImages.getImage(moneydance_ui.getMain().getSourceInformation().getIconResource())

def MDDiag():
    global debug
    myPrint("D", "Moneydance Build:", moneydance.getVersion(), "Build:", moneydance.getBuild())


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

    myFont = moneydance_ui.getFonts().defaultText

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

    return


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
    myPlat = System.getProperty("os.name")
    if myPlat is None: return False
    myPrint("DB", "Platform:", myPlat)
    myPrint("DB", "OS Version:", System.getProperty("os.version"))
    return myPlat == "Mac OS X"


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
        homeDir = moneydance_data.getRootFolder().getParent()  # Better than nothing!

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

def get_StuWareSoftSystems_parameters_from_file():
    global debug, myParameters, lPickle_version_warning, version_build, _resetParameters                            # noqa

    myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )

    if _resetParameters:
        myPrint("B", "User has specified to reset parameters... keeping defaults and skipping pickle()")
        myParameters = {}
        return

    myFile = "StuWareSoftSystems.dict"
    old_dict_filename = os.path.join("..", myFile)

    # Pickle was originally encrypted, no need, migrating to unencrypted
    migratedFilename = os.path.join(moneydance_data.getRootFolder().getAbsolutePath(),myFile)

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
                local_storage = moneydance.getCurrentAccountBook().getLocalStorage()
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

def save_StuWareSoftSystems_parameters_to_file():
    global debug, myParameters, lPickle_version_warning, version_build

    myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )

    if myParameters is None: myParameters = {}

    # Don't forget, any parameters loaded earlier will be preserved; just add changed variables....
    myParameters["__Author"] = "Stuart Beesley - (c) StuWareSoftSystems"
    myParameters["debug"] = debug

    dump_StuWareSoftSystems_parameters_from_memory()

    myFile = "StuWareSoftSystems.dict"
    # Pickle was originally encrypted, no need, migrating to unencrypted
    migratedFilename = os.path.join(moneydance_data.getRootFolder().getAbsolutePath(),myFile)

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

# END COMMON DEFINITIONS ###############################################################################################
# END COMMON DEFINITIONS ###############################################################################################
# END COMMON DEFINITIONS ###############################################################################################


# >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
def load_StuWareSoftSystems_parameters_into_memory():
    global debug, myParameters, lPickle_version_warning, version_build

    # >>> THESE ARE THIS SCRIPT's PARAMETERS TO LOAD
    global __extract_investment_transactions
    global hideHiddenSecurities, hideInactiveAccounts, hideHiddenAccounts, lAllCurrency, filterForCurrency
    global lAllSecurity, filterForSecurity, lAllAccounts, filterForAccounts, lStripASCII, csvDelimiter, scriptpath
    global lIncludeOpeningBalances, lAdjustForSplits, userdateformat
    global lWriteBOMToExportFile_SWSS                                                                                  # noqa

    myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )
    myPrint("DB", "Loading variables into memory...")

    if myParameters is None: myParameters = {}

    if myParameters.get("__extract_investment_transactions") is not None: __extract_investment_transactions = myParameters.get("__extract_investment_transactions")
    if myParameters.get("hideHiddenSecurities") is not None: hideHiddenSecurities = myParameters.get("hideHiddenSecurities")
    if myParameters.get("hideInactiveAccounts") is not None: hideInactiveAccounts = myParameters.get("hideInactiveAccounts")
    if myParameters.get("hideHiddenAccounts") is not None: hideHiddenAccounts = myParameters.get("hideHiddenAccounts")
    if myParameters.get("lAllCurrency") is not None: lAllCurrency = myParameters.get("lAllCurrency")
    if myParameters.get("filterForCurrency") is not None: filterForCurrency = myParameters.get("filterForCurrency")
    if myParameters.get("lAllSecurity") is not None: lAllSecurity = myParameters.get("lAllSecurity")
    if myParameters.get("filterForSecurity") is not None: filterForSecurity = myParameters.get("filterForSecurity")
    if myParameters.get("lAllAccounts") is not None: lAllAccounts = myParameters.get("lAllAccounts")
    if myParameters.get("filterForAccounts") is not None: filterForAccounts = myParameters.get("filterForAccounts")
    if myParameters.get("lStripASCII") is not None: lStripASCII = myParameters.get("lStripASCII")
    if myParameters.get("csvDelimiter") is not None: csvDelimiter = myParameters.get("csvDelimiter")
    if myParameters.get("lIncludeOpeningBalances") is not None: lIncludeOpeningBalances = myParameters.get("lIncludeOpeningBalances")
    if myParameters.get("lAdjustForSplits") is not None: lAdjustForSplits = myParameters.get("lAdjustForSplits")
    if myParameters.get("userdateformat") is not None: userdateformat = myParameters.get("userdateformat")
    if myParameters.get("lWriteBOMToExportFile_SWSS") is not None: lWriteBOMToExportFile_SWSS = myParameters.get("lWriteBOMToExportFile_SWSS")                                                                                  # noqa

    if myParameters.get("scriptpath") is not None:
        scriptpath = myParameters.get("scriptpath")
        if not os.path.isdir(scriptpath):
            myPrint("B","Warning: loaded parameter scriptpath does not appear to be a valid directory:", scriptpath, "will ignore")
            scriptpath = ""

    myPrint("DB","myParameters{} set into memory (as variables).....")

    return

# >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
def dump_StuWareSoftSystems_parameters_from_memory():
    global debug, myParameters, lPickle_version_warning, version_build

    # >>> THESE ARE THIS SCRIPT's PARAMETERS TO SAVE
    global __extract_investment_transactions
    global hideHiddenSecurities, hideInactiveAccounts, hideHiddenAccounts, lAllCurrency, filterForCurrency
    global lAllSecurity, filterForSecurity, lAllAccounts, filterForAccounts, lStripASCII, csvDelimiter, scriptpath
    global lDisplayOnly, version_build, myParameters
    global lIncludeOpeningBalances, lAdjustForSplits
    global userdateformat
    global lWriteBOMToExportFile_SWSS                                                                                  # noqa

    myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )

    # NOTE: Parameters were loaded earlier on... Preserve existing, and update any used ones...
    # (i.e. other StuWareSoftSystems programs might be sharing the same file)

    if myParameters is None: myParameters = {}

    myParameters["__extract_investment_transactions"] = version_build
    myParameters["hideHiddenSecurities"] = hideHiddenSecurities
    myParameters["hideInactiveAccounts"] = hideInactiveAccounts
    myParameters["hideHiddenAccounts"] = hideHiddenAccounts
    myParameters["lAllCurrency"] = lAllCurrency
    myParameters["filterForCurrency"] = filterForCurrency
    myParameters["lAllSecurity"] = lAllSecurity
    myParameters["filterForSecurity"] = filterForSecurity
    myParameters["lAllAccounts"] = lAllAccounts
    myParameters["filterForAccounts"] = filterForAccounts
    myParameters["lStripASCII"] = lStripASCII
    myParameters["csvDelimiter"] = csvDelimiter

    myParameters["lIncludeOpeningBalances"] = lIncludeOpeningBalances
    myParameters["lAdjustForSplits"] = lAdjustForSplits
    myParameters["userdateformat"] = userdateformat
    myParameters["lWriteBOMToExportFile_SWSS"] = lWriteBOMToExportFile_SWSS

    if not lDisplayOnly and scriptpath != "" and os.path.isdir(scriptpath):
        myParameters["scriptpath"] = scriptpath

    myPrint("DB","variables dumped from memory back into myParameters{}.....")

    return


get_StuWareSoftSystems_parameters_from_file()
myPrint("DB", "DEBUG IS ON..")
# END ALL CODE COPY HERE ###############################################################################################

# Create fake JFrame() so that all popups have correct Moneydance Icons etc
extract_investment_transactions_fake_frame_ = JFrame()
if (not Platform.isMac()):
    moneydance_ui.getImages()
    extract_investment_transactions_fake_frame_.setIconImage(MDImages.getImage(moneydance_ui.getMain().getSourceInformation().getIconResource()))
extract_investment_transactions_fake_frame_.setUndecorated(True)
extract_investment_transactions_fake_frame_.setVisible(False)
extract_investment_transactions_fake_frame_.setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE)

csvfilename = None

if decimalCharSep != "." and csvDelimiter == ",": csvDelimiter = ";"  # Override for EU countries or where decimal point is actually a comma...
myPrint("DB", "Decimal point:", decimalCharSep, "Grouping Separator", groupingCharSep, "CSV Delimiter set to:", csvDelimiter)

sdf = SimpleDateFormat("dd/MM/yyyy")

label1 = JLabel("Hide Hidden Securities (Y/N)?:")
user_hideHiddenSecurities = JTextField(2)
user_hideHiddenSecurities.setDocument(JTextFieldLimitYN(1, True, "YN"))
if hideHiddenSecurities: user_hideHiddenSecurities.setText("Y")
else:                        user_hideHiddenSecurities.setText("N")

label2 = JLabel("Hide Inactive Accounts (Y/N)?:")
user_hideInactiveAccounts = JTextField(2)
user_hideInactiveAccounts.setDocument(JTextFieldLimitYN(1, True, "YN"))
if hideInactiveAccounts: user_hideInactiveAccounts.setText("Y")
else:                        user_hideInactiveAccounts.setText("N")

label3 = JLabel("Hide Hidden Accounts (Y/N):")
user_hideHiddenAccounts = JTextField(2)
user_hideHiddenAccounts.setDocument(JTextFieldLimitYN(1, True, "YN"))
if hideHiddenAccounts: user_hideHiddenAccounts.setText("Y")
else:                      user_hideHiddenAccounts.setText("N")

label4 = JLabel("Filter for Currency containing text '...' or ALL:")
user_selectCurrency = JTextField(5)
user_selectCurrency.setDocument(JTextFieldLimitYN(5, True, "CURR"))
if lAllCurrency: user_selectCurrency.setText("ALL")
else:            user_selectCurrency.setText(filterForCurrency)

label5 = JLabel("Filter for Security/Ticker containing text '...' or ALL:")
user_selectTicker = JTextField(12)
user_selectTicker.setDocument(JTextFieldLimitYN(12, True, "CURR"))
if lAllSecurity: user_selectTicker.setText("ALL")
else:            user_selectTicker.setText(filterForSecurity)

label6 = JLabel("Filter for Accounts containing text '...' (or ALL):")
user_selectAccounts = JTextField(12)
user_selectAccounts.setDocument(JTextFieldLimitYN(20, True, "CURR"))
if lAllAccounts: user_selectAccounts.setText("ALL")
else:            user_selectAccounts.setText(filterForAccounts)

label7 = JLabel("Include Opening Balances (Y/N):")
user_selectOpeningBalances = JTextField(2)
user_selectOpeningBalances.setDocument(JTextFieldLimitYN(1, True, "YN"))
if lIncludeOpeningBalances: user_selectOpeningBalances.setText("Y")
else:                       user_selectOpeningBalances.setText("N")

label8 = JLabel("Adjust for stock splits (Y/N):")
user_selectAdjustSplits = JTextField(2)
user_selectAdjustSplits.setDocument(JTextFieldLimitYN(1, True, "YN"))
if lAdjustForSplits: user_selectAdjustSplits.setText("Y")
else:                user_selectAdjustSplits.setText("N")

label9 = JLabel("Output Date Format 1=dd/mm/yyyy, 2=mm/dd/yyyy, 3=yyyy/mm/dd, 4=yyyymmdd:")
user_dateformat = JTextField(2)
user_dateformat.setDocument(JTextFieldLimitYN(1, True, "1234"))

if userdateformat == "%d/%m/%Y": user_dateformat.setText("1")
elif userdateformat == "%m/%d/%Y": user_dateformat.setText("2")
elif userdateformat == "%Y/%m/%d": user_dateformat.setText("3")
elif userdateformat == "%Y%m%d": user_dateformat.setText("4")
else: user_dateformat.setText("3")

label10 = JLabel("Strip non ASCII characters from CSV export? (Y/N)")
user_selectStripASCII = JTextField(2)
user_selectStripASCII.setDocument(JTextFieldLimitYN(1, True, "YN"))
if lStripASCII: user_selectStripASCII.setText("Y")
else:               user_selectStripASCII.setText("N")

label11 = JLabel("Change CSV Export Delimiter from default to: ';|,'")
user_selectDELIMITER = JTextField(2)
user_selectDELIMITER.setDocument(JTextFieldLimitYN(1, True, "DELIM"))
user_selectDELIMITER.setText(csvDelimiter)

labelBOM = JLabel("Write BOM (Byte Order Mark) to file (helps Excel open files) (Y/N):")
user_selectBOM = JTextField(2)
user_selectBOM.setDocument(JTextFieldLimitYN(1, True, "YN"))
if lWriteBOMToExportFile_SWSS:  user_selectBOM.setText("Y")
else:                           user_selectBOM.setText("N")

label12 = JLabel("Turn DEBUG Verbose messages on? (Y/N)")
user_selectDEBUG = JTextField(2)
user_selectDEBUG.setDocument(JTextFieldLimitYN(1, True, "YN"))
if debug:  user_selectDEBUG.setText("Y")
else:           user_selectDEBUG.setText("N")

userFilters = JPanel(GridLayout(14, 2))
userFilters.add(label1)
userFilters.add(user_hideHiddenSecurities)
userFilters.add(label2)
userFilters.add(user_hideInactiveAccounts)
userFilters.add(label3)
userFilters.add(user_hideHiddenAccounts)
userFilters.add(label4)
userFilters.add(user_selectCurrency)
userFilters.add(label5)
userFilters.add(user_selectTicker)
userFilters.add(label6)
userFilters.add(user_selectAccounts)
userFilters.add(label7)
userFilters.add(user_selectOpeningBalances)
userFilters.add(label8)
userFilters.add(user_selectAdjustSplits)
userFilters.add(label9)
userFilters.add(user_dateformat)
userFilters.add(label10)
userFilters.add(user_selectStripASCII)
userFilters.add(label11)
userFilters.add(user_selectDELIMITER)
userFilters.add(labelBOM)
userFilters.add(user_selectBOM)
userFilters.add(label12)
userFilters.add(user_selectDEBUG)

lExit = False
lDisplayOnly = False

options = ["ABORT", "CSV Export"]
userAction = (JOptionPane.showOptionDialog(extract_investment_transactions_fake_frame_, userFilters, "%s(build: %s) Set Script Parameters...."%(myScriptName,version_build),
                                     JOptionPane.OK_CANCEL_OPTION,
                                     JOptionPane.QUESTION_MESSAGE,
                                     moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                     options, options[1]))
if userAction == 1:  # Export
    myPrint("DB", "Export chosen")
    lDisplayOnly = False
else:
    myPrint("B", "User Cancelled Parameter selection.. Will exit..")
    myPopupInformationBox(extract_investment_transactions_fake_frame_, "User Cancelled Parameter selection.. Will abort..", "PARAMETERS")
    lDisplayOnly = False
    lExit = True

if not lExit:
    myPrint("DB", "Parameters Captured",
        "Sec: ", user_hideHiddenSecurities.getText(),
        "InActAct:", user_hideInactiveAccounts.getText(),
        "HidAct:", user_hideHiddenAccounts.getText(),
        "Curr:", user_selectCurrency.getText(),
        "Ticker:", user_selectTicker.getText(),
        "Filter Accts:", user_selectAccounts.getText(),
        "Incl Open Bals:", user_selectOpeningBalances.getText(),
        "Adj Splits:", user_selectAdjustSplits.getText(),
        "User Date Format:", user_dateformat.getText(),
        "Strip ASCII:", user_selectStripASCII.getText(),
        "Write BOM to file:", user_selectBOM.getText(),
        "Verbose Debug Messages: ", user_selectDEBUG.getText(),
        "CSV File Delimiter:", user_selectDELIMITER.getText())
    # endif

    hideHiddenSecurities = False
    hideInactiveAccounts = False
    hideHiddenAccounts = False
    if user_hideHiddenSecurities.getText() == "Y":  hideHiddenSecurities = True
    else:                                           hideHiddenSecurities = False
    if user_hideInactiveAccounts.getText() == "Y":  hideInactiveAccounts = True
    else:                                           hideInactiveAccounts = False
    if user_hideHiddenAccounts.getText() == "Y":    hideHiddenAccounts = True
    else:                                           hideHiddenAccounts = False

    if user_selectCurrency.getText() == "ALL" or user_selectCurrency.getText().strip() == "":
        lAllCurrency = True
        filterForCurrency = "ALL"
    else:
        lAllCurrency = False
        filterForCurrency = user_selectCurrency.getText()

    if user_selectTicker.getText() == "ALL" or user_selectTicker.getText().strip() == "":
        lAllSecurity = True
        filterForSecurity = "ALL"
    else:
        lAllSecurity = False
        filterForSecurity = user_selectTicker.getText()

    if user_selectAccounts.getText() == "ALL" or user_selectAccounts.getText().strip() == "":
        lAllAccounts = True
        filterForAccounts = "ALL"
    else:
        lAllAccounts = False
        filterForAccounts = user_selectAccounts.getText()

    if user_selectOpeningBalances.getText() == "Y":     lIncludeOpeningBalances = True
    else:                                               lIncludeOpeningBalances = False

    if user_selectAdjustSplits.getText() == "Y":    lAdjustForSplits = True
    else:                                           lAdjustForSplits = False

    if user_dateformat.getText() == "1": userdateformat = "%d/%m/%Y"
    elif user_dateformat.getText() == "2": userdateformat = "%m/%d/%Y"
    elif user_dateformat.getText() == "3": userdateformat = "%Y/%m/%d"
    elif user_dateformat.getText() == "4": userdateformat = "%Y%m%d"
    else:
        # PROBLEM /  default
        userdateformat = "%Y/%m/%d"

    if user_selectStripASCII.getText() == "Y":      lStripASCII = True
    else:                                           lStripASCII = False

    csvDelimiter = user_selectDELIMITER.getText()
    if csvDelimiter == "" or (not (csvDelimiter in ";|,")):
        myPrint("B", "Invalid Delimiter:", csvDelimiter, "selected. Overriding with:','")
        csvDelimiter = ","
    if decimalCharSep == csvDelimiter:
        myPrint("B", "WARNING: The CSV file delimiter:", csvDelimiter, "cannot be the same as your decimal point character:",
            decimalCharSep, " - Proceeding without file export!!")
        lDisplayOnly = True

    lWriteBOMToExportFile_SWSS = user_selectBOM.getText() == "Y"

    debug = user_selectDEBUG.getText() == "Y"
    myPrint("DB", "DEBUG turned ON")

    myPrint("B","User Parameters...")
    if hideHiddenSecurities:
        myPrint("B", "Hiding Hidden Securities...")
    else:
        myPrint("B", "Including Hidden Securities...")
    if hideInactiveAccounts:
        myPrint("B", "Hiding Inactive Accounts...")
    else:
        myPrint("B", "Including Inactive Accounts...")

    if hideHiddenAccounts:
        myPrint("B", "Hiding Hidden Accounts...")
    else:
        myPrint("B", "Including Hidden Accounts...")

    if lAllCurrency:
        myPrint("B", "Selecting ALL Currencies...")
    else:
        myPrint("B", "Filtering for Currency containing: ", filterForCurrency)

    if lAllSecurity:
        myPrint("B", "Selecting ALL Securities...")
    else:
        myPrint("B", "Filtering for Security/Ticker containing: ", filterForSecurity)

    if lAllAccounts:
        myPrint("B", "Selecting ALL Accounts...")
    else:
        myPrint("B", "Filtering for Accounts containing: ", filterForAccounts)

    if lIncludeOpeningBalances:
        myPrint("B", "Including Opening Balances...")
    else:
        myPrint("B", "Ignoring Opening Balances... ")

    if lAdjustForSplits:
        myPrint("B", "Script will adjust for Stock Splits...")
    else:
        myPrint("B", "Not adjusting for Stock Splits...")

    myPrint("B", "user date format....:", userdateformat)


    # Now get the export filename
    csvfilename = None

    if not lDisplayOnly:  # i.e. we have asked for a file export - so get the filename - Always False in this script1

        if lStripASCII:
            myPrint("B", "Will strip non-ASCII characters - e.g. Currency symbols from output file...", " Using Delimiter:", csvDelimiter)
        else:
            myPrint("B", "Non-ASCII characters will not be stripped from file: ", " Using Delimiter:", csvDelimiter)

        if lWriteBOMToExportFile_SWSS:
            myPrint("B", "Script will add a BOM (Byte Order Mark) to front of the extracted file...")
        else:
            myPrint("B", "No BOM (Byte Order Mark) will be added to the extracted file...")

        def grabTheFile():
            global debug, lDisplayOnly, csvfilename, lIamAMac, scriptpath, myScriptName
            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

            if scriptpath == "" or scriptpath is None:  # No parameter saved / loaded from disk
                scriptpath = myDir()

            myPrint("DB", "Default file export output path is....:", scriptpath)

            csvfilename = ""
            if lIamAMac:
                myPrint("DB", "MacOS X detected: Therefore I will run FileDialog with no extension filters to get filename....")
                # jFileChooser hangs on Mac when using file extension filters, also looks rubbish. So using Mac(ish)GUI

                System.setProperty("com.apple.macos.use-file-dialog-packages","true")  # In theory prevents access to app file structure (but doesnt seem to work)
                System.setProperty("apple.awt.fileDialogForDirectories", "false")

            filename = FileDialog(extract_investment_transactions_fake_frame_, "Select/Create CSV file for extract (CANCEL=NO EXPORT)")
            filename.setMultipleMode(False)
            filename.setMode(FileDialog.SAVE)
            filename.setFile(extract_filename)
            if (scriptpath is not None and scriptpath != ""): filename.setDirectory(scriptpath)

            # Copied from MD code... File filters only work on non Macs (or Macs below certain versions)
            if (not Platform.isOSX() or not Platform.isOSXVersionAtLeast("10.13")):
                extfilter = ExtFilenameFilter("csv")
                filename.setFilenameFilter(extfilter)  # I'm not actually sure this works...?

            filename.setVisible(True)

            csvfilename = filename.getFile()

            if (csvfilename is None) or csvfilename == "":
                lDisplayOnly = True
                csvfilename = None
                myPrint("B", "User chose to cancel or no file selected >>  So no Extract will be performed... ")
                myPopupInformationBox(extract_investment_transactions_fake_frame_, "User chose to cancel or no file selected >>  So no Extract will be performed... ", "FILE EXPORT")
            elif str(csvfilename).endswith(".moneydance"):
                myPrint("B", "User selected file:", csvfilename)
                myPrint("B", "Sorry - User chose to use .moneydance extension - I will not allow it!... So no Extract will be performed...")
                myPopupInformationBox(extract_investment_transactions_fake_frame_, "Sorry - User chose to use .moneydance extension - I will not allow it!... So no Extract will be performed...", "FILE EXPORT")
                lDisplayOnly = True
                csvfilename = None
            elif ".moneydance" in filename.getDirectory():
                myPrint("B", "User selected file:", filename.getDirectory(), csvfilename)
                myPrint("B", "Sorry - FileDialog() User chose to save file in .moneydance location. NOT Good practice so I will not allow it!... So no Extract will be performed...")
                myPopupInformationBox(extract_investment_transactions_fake_frame_, "Sorry - FileDialog() User chose to save file in .moneydance location. NOT Good practice so I will not allow it!... So no Extract will be performed...", "FILE EXPORT")
                lDisplayOnly = True
                csvfilename = None
            else:
                csvfilename = os.path.join(filename.getDirectory(), filename.getFile())
                scriptpath = str(filename.getDirectory())

            if not lDisplayOnly:
                if os.path.exists(csvfilename) and os.path.isfile(csvfilename):
                    myPrint("B", "WARNING: file exists,but assuming user said OK to overwrite..")

            if not lDisplayOnly:
                if check_file_writable(csvfilename):
                    if lStripASCII:
                        myPrint("B", 'Will extract investment transactions to file: ', csvfilename, "(NOTE: Should drop non utf8 characters...)")
                    else:
                        myPrint("B", 'Will extract investment transactions to file: ', csvfilename, "...")
                    scriptpath = os.path.dirname(csvfilename)
                else:
                    myPrint("B", "Sorry - I just checked and you do not have permissions to create this file:", csvfilename)
                    myPopupInformationBox(extract_investment_transactions_fake_frame_, "Sorry - I just checked and you do not have permissions to create this file: %s" %csvfilename, "FILE EXPORT")
                    csvfilename=""
                    lDisplayOnly = True

            return


        # enddef

        if not lDisplayOnly: grabTheFile()
    else:
        pass
    # endif

    if csvfilename is None:
        lDisplayOnly = True
        myPrint("P", "No Export will be performed")

    save_StuWareSoftSystems_parameters_to_file()

    if not lDisplayOnly:

        # noinspection PyArgumentList
        class MyTxnSearchCostBasis(TxnSearch):

            def __init__(self,
                         hideInactiveAccounts=False,                                                        # noqa
                         lAllAccounts=True,                                                                 # noqa
                         filterForAccounts="ALL",                                                           # noqa
                         hideHiddenAccounts=False,                                                          # noqa
                         hideHiddenSecurities=False,                                                        # noqa
                         lAllCurrency=True,                                                                 # noqa
                         filterForCurrency="ALL",                                                           # noqa
                         lAllSecurity=True,                                                                 # noqa
                         filterForSecurity="ALL",                                                           # noqa
                         findUUID=None):                                                                    # noqa
                super(TxnSearch, self).__init__()

                self.hideInactiveAccounts = hideInactiveAccounts
                self.lAllAccounts = lAllAccounts
                self.filterForAccounts = filterForAccounts
                self.hideHiddenAccounts = hideHiddenAccounts
                self.hideHiddenSecurities = hideHiddenSecurities
                self.lAllCurrency = lAllCurrency
                self.filterForCurrency = filterForCurrency
                self.lAllSecurity = lAllSecurity
                self.filterForSecurity = filterForSecurity
                self.findUUID = findUUID

                self.baseCurrency = moneydance.getCurrentAccountBook().getCurrencies().getBaseType()

            # noinspection PyMethodMayBeStatic
            def matchesAll(self):
                return False


            def matches(self, txn):                                                                             # noqa
                # NOTE: If not using the parameter selectAccountType=.SECURITY then the security filters won't work (without
                # special extra coding!)

                txnAcct = txn.getAccount()                                                                      # noqa

                if self.findUUID is not None:  # If UUID supplied, override all other parameters...
                    if txnAcct.getUUID() == self.findUUID:
                        return True
                    else:
                        return False

                # Investment Accounts only
                # noinspection PyUnresolvedReferences
                if txnAcct.getAccountType() != Account.AccountType.INVESTMENT:
                    return False

                if self.hideInactiveAccounts:
                    # This logic replicates Moneydance AcctFilter.ACTIVE_ACCOUNTS_FILTER
                    if txnAcct.getAccountOrParentIsInactive(): return False
                    if txnAcct.getHideOnHomePage() and txnAcct.getBalance() == 0: return False
                    # Don't repeat the above check on the security sub accounts as probably needed for cost basis reporting

                if self.lAllAccounts:
                    pass
                elif (self.filterForAccounts.upper().strip() in txnAcct.getFullAccountName().upper().strip()):
                    pass
                else:
                    return False

                if (not self.hideHiddenAccounts) or (self.hideHiddenAccounts and not txnAcct.getHideOnHomePage()):
                    pass
                else:
                    return False

                # Check that we are on a parent. If we are on a split, in an Investment Account, then it must be a cash txfr only
                lParent = False                                                                                 # noqa
                parent = txn.getParentTxn()                                                                     # noqa
                if txn == parent:
                    lParent = True                                                                              # noqa

                txnCurr = txnAcct.getCurrencyType()


                if lAllSecurity:
                    securityCurr = None                                                                         # noqa
                    securityTxn = None                                                                          # noqa
                    securityAcct = None                                                                         # noqa
                else:

                    if not lParent: return False

                    # If we don't have a security record, then we are not interested!
                    securityTxn = TxnUtil.getSecurityPart(txn)                                                   # noqa
                    if securityTxn is None:
                        return False

                    securityAcct = securityTxn.getAccount()                                                     # noqa
                    securityCurr = securityAcct.getCurrencyType()                                               # noqa

                    if not self.hideHiddenSecurities or (self.hideHiddenSecurities and not securityCurr.getHideInUI()):
                        pass
                    else:
                        return False

                    # noinspection PyUnresolvedReferences
                    if self.lAllSecurity:
                        pass
                    elif self.filterForSecurity.upper().strip() in securityCurr.getTickerSymbol().upper().strip():
                        pass
                    elif self.filterForSecurity.upper().strip() in securityCurr.getName().upper().strip():
                        pass
                    else:
                        return False
                # ENDIF

                if lAllCurrency:
                    pass
                else:
                    if securityCurr:
                        # noinspection PyUnresolvedReferences
                        if txnCurr.getIDString().upper().strip() != securityCurr.getRelativeCurrency().getIDString().upper().strip():
                            myPrint("B", "LOGIC ERROR: I can't see how the Security's currency is different to the Account's currency? ")
                            # noinspection PyUnresolvedReferences
                            myPrint("B", txnCurr.getIDString().upper().strip(), securityCurr.getRelativeCurrency().getIDString().upper().strip())
                            myPrint("B", repr(txn))
                            myPrint("B", repr(txnCurr))
                            myPrint("B", repr(securityCurr))
                            # noinspection PyUnresolvedReferences
                            myPopupInformationBox(extract_investment_transactions_fake_frame_, "LOGIC ERROR: I can't see how the Security's currency is different to the Account's currency? ","LOGIC ERROR")
                            # noinspection PyUnresolvedReferences
                            extract_investment_transactions_fake_frame_.dispose()
                            raise(Exception("LOGIC Error - Security's currency: "
                                    + securityCurr.getRelativeCurrency().getIDString().upper().strip()              # noqa
                                    + " is different to txn currency: "
                                    + txnCurr.getIDString().upper().strip()
                                    + " Aborting"))


                    # All accounts and security records can have currencies
                        # noinspection PyUnresolvedReferences
                        if self.lAllCurrency:
                            pass
                        elif (self.filterForCurrency.upper().strip() in txnCurr.getIDString().upper().strip()) \
                                and (
                                self.filterForCurrency.upper().strip() in securityCurr.getRelativeCurrency().getIDString().upper().strip()):
                            pass
                        elif (self.filterForCurrency.upper().strip() in txnCurr.getName().upper().strip()) \
                                and (
                                self.filterForCurrency.upper().strip() in securityCurr.getRelativeCurrency().getName().upper().strip()):
                            pass
                        else:
                            return False

                    else:
                        # All accounts and security records can have currencies
                        if self.lAllCurrency:
                            pass
                        elif (self.filterForCurrency.upper().strip() in txnCurr.getIDString().upper().strip()):
                            pass
                        elif (self.filterForCurrency.upper().strip() in txnCurr.getName().upper().strip()):
                            pass
                        else:
                            return False

                # Phew! We made it....
                return True
            # enddef


        # endclass

        _COLUMN = 0
        _HEADING = 1
        dataKeys = {
                "_ACCOUNT":         [0, "Account"],
                "_DATE":            [1, "Date"],
                "_TAXDATE":         [2, "TaxDate"],
                "_CURR":            [3, "Currency"],
                "_SECURITY":        [4, "Security"],
                "_TICKER":          [5, "SecurityTicker"],
                "_SECCURR":         [6, "SecurityCurrency"],
                "_AVGCOST":         [7, "AverageCostControl"],
                "_ACTION":          [8, "Action"],
                "_TT":              [9, "ActionType"],
                "_CHEQUE":          [10, "Cheque"],
                "_DESC":            [11, "Description"],
                "_MEMO":            [12, "Memo"],
                "_CLEARED":         [13, "Cleared"],
                "_TRANSFER":        [14, "Transfer"],
                "_CAT":             [15, "Category"],
                "_SHARES":          [16, "Shares"],
                "_PRICE":           [17, "Price"],
                "_AMOUNT":          [18, "Amount"],
                "_FEE":             [19, "Fee"],
                "_FEECAT":          [20, "FeeCategory"],
                "_TXNNETAMOUNT":    [21, "TransactionNetAmount"],
                "_CASHIMPACT":      [22, "CashImpact"],
                "_SHRSAFTERSPLIT":  [23, "CalculateSharesAfterSplit"],
                "_PRICEAFTERSPLIT": [24, "CalculatePriceAfterSplit"],
                "_HASATTACHMENTS":  [25, "HasAttachments"],
                "_LOTS":            [26, "Lot Data"],
                "_ACCTCASHBAL":     [27, "AccountCashBalance"],
                "_SECSHRHOLDING":   [28, "SecurityShareHolding"],
                "_END":             [29, "_END"]
                }

        transactionTable = []

        myPrint("DB", dataKeys)

        rootbook = moneydance.getCurrentAccountBook()
        rootaccount = rootbook.getRootAccount()
        baseCurrency = moneydance.getCurrentAccountBook().getCurrencies().getBaseType()


        txns = rootbook.getTransactionSet().getTransactions(MyTxnSearchCostBasis(hideInactiveAccounts,
                                                                                 lAllAccounts,
                                                                                 filterForAccounts,
                                                                                 hideHiddenAccounts,
                                                                                 hideHiddenSecurities,
                                                                                 lAllCurrency,
                                                                                 filterForCurrency,
                                                                                 lAllSecurity,
                                                                                 filterForSecurity,
                                                                                 None))

        iBal = 0
        accountBalances = {}

        iCount = 0
        for txn in txns:

            txnAcct = txn.getAccount()
            acctCurr = txnAcct.getCurrencyType()  # Currency of the Investment Account

            if lIncludeOpeningBalances:
                if accountBalances.get(txnAcct):
                    pass
                else:
                    accountBalances[txnAcct] = True
                    openBal = acctCurr.getDoubleValue(txnAcct.getStartBalance())
                    if openBal != 0:
                        iBal+=1
                        row = ([None] * dataKeys["_END"][0])  # Create a blank row to be populated below...
                        row[dataKeys["_ACCOUNT"][_COLUMN]] = txnAcct.getFullAccountName()
                        row[dataKeys["_CURR"][_COLUMN]] = acctCurr.getIDString()
                        row[dataKeys["_DESC"][_COLUMN]] = "MANUAL OPENING BALANCE"
                        row[dataKeys["_ACTION"][_COLUMN]] = "OpenBal"
                        row[dataKeys["_TT"][_COLUMN]] = "MANUAL"
                        row[dataKeys["_DATE"][_COLUMN]] = txnAcct.getCreationDateInt()
                        row[dataKeys["_AMOUNT"][_COLUMN]] = openBal
                        row[dataKeys["_CASHIMPACT"][_COLUMN]] = openBal
                        row[dataKeys["_ACCTCASHBAL"][_COLUMN]] = acctCurr.getDoubleValue(txnAcct.getBalance())

                        myPrint("D", row)
                        transactionTable.append(row)

        # Check that we are on a parent. If we are on a split, in an Investment Account, then it must be a cash txfr only
            parent = txn.getParentTxn()
            if txn == parent:
                lParent = True
            else:
                lParent = False

            securityCurr = None
            securityTxn = feeTxn = xfrTxn = incTxn = expTxn = None
            feeAcct = incAcct = expAcct = xfrAcct = securityAcct = None

            cbTags = None
            if lParent:
                securityTxn = TxnUtil.getSecurityPart(txn)
                if securityTxn:
                    securityAcct = securityTxn.getAccount()
                    securityCurr = securityAcct.getCurrencyType()  # the Security master record
                    cbTags = TxnUtil.parseCostBasisTag(securityTxn)

                xfrTxn = TxnUtil.getXfrPart(txn)
                if xfrTxn: xfrAcct = xfrTxn.getAccount()

                feeTxn = TxnUtil.getCommissionPart(txn)
                if feeTxn: feeAcct = feeTxn.getAccount()

                incTxn = TxnUtil.getIncomePart(txn)
                if incTxn: incAcct = incTxn.getAccount()

                expTxn = TxnUtil.getExpensePart(txn)
                if expTxn:expAcct = expTxn.getAccount()

            row = ([None] * dataKeys["_END"][0])  # Create a blank row to be populated below...

            if lParent and str(txn.getTransferType()).lower() == "xfrtp_bank" and str(txn.getInvestTxnType()).lower() == "bank" \
                    and not xfrTxn and feeTxn and not securityTxn:
                # This seems to be an error! It's an XFR (fixing MD data bug)
                xfrTxn = feeTxn
                feeTxn = None
                xfrAcct = feeAcct
                feeAcct = None

            row[dataKeys["_ACCOUNT"][_COLUMN]] = txnAcct.getFullAccountName()
            row[dataKeys["_CURR"][_COLUMN]] = acctCurr.getIDString()

            row[dataKeys["_DATE"][_COLUMN]] = txn.getDateInt()
            if txn.getTaxDateInt() != txn.getDateInt():
                row[dataKeys["_TAXDATE"][_COLUMN]] = txn.getTaxDateInt()


            if securityTxn:
                row[dataKeys["_SECURITY"][_COLUMN]] = str(securityCurr.getName())
                row[dataKeys["_SECCURR"][_COLUMN]] = str(securityCurr.getRelativeCurrency().getIDString())
                row[dataKeys["_TICKER"][_COLUMN]] = str(securityCurr.getTickerSymbol())
                row[dataKeys["_SHARES"][_COLUMN]] = securityCurr.getDoubleValue(securityTxn.getValue())
                row[dataKeys["_PRICE"][_COLUMN]] = acctCurr.getDoubleValue(securityTxn.getAmount())
                row[dataKeys["_AVGCOST"][_COLUMN]] = securityAcct.getUsesAverageCost()
                row[dataKeys["_SECSHRHOLDING"][_COLUMN]] = securityCurr.formatSemiFancy(securityAcct.getBalance(),decimalCharSep)
            else:
                row[dataKeys["_SECURITY"][_COLUMN]] = ""
                row[dataKeys["_SECCURR"][_COLUMN]] = ""
                row[dataKeys["_TICKER"][_COLUMN]] = ""
                row[dataKeys["_SHARES"][_COLUMN]] = 0
                row[dataKeys["_PRICE"][_COLUMN]] = 0
                row[dataKeys["_AVGCOST"][_COLUMN]] = ""
                row[dataKeys["_SECSHRHOLDING"][_COLUMN]] = 0

            if lAdjustForSplits and securityTxn and row[dataKeys["_SHARES"][_COLUMN]] != 0:
                # Here we go.....
                row[dataKeys["_SHRSAFTERSPLIT"][_COLUMN]] = row[dataKeys["_SHARES"][_COLUMN]]
                stockSplits = securityCurr.getSplits()
                if stockSplits and len(stockSplits)>0:
                    # Here we really go....1

                    myPrint("D", securityCurr, " - Found share splits...")
                    myPrint("D", securityTxn)

                    stockSplits = sorted(stockSplits, key=lambda x: x.getDateInt(), reverse=True)   # Sort date newest first...
                    for theSplit in stockSplits:
                        if row[dataKeys["_DATE"][_COLUMN]] >= theSplit.getDateInt():
                            continue
                        myPrint("D", securityCurr, " -  ShareSplits()... Applying ratio.... *", theSplit.getSplitRatio(), "Shares before:",  row[dataKeys["_SHRSAFTERSPLIT"][_COLUMN]])
                        lWasThereASplit=True
                        # noinspection PyUnresolvedReferences
                        row[dataKeys["_SHRSAFTERSPLIT"][_COLUMN]] = row[dataKeys["_SHRSAFTERSPLIT"][_COLUMN]] * theSplit.getSplitRatio()
                        myPrint("D", securityCurr, " - Shares after:",  row[dataKeys["_SHRSAFTERSPLIT"][_COLUMN]])
                        # Keep going if more splits....
                        continue


            row[dataKeys["_DESC"][_COLUMN]] = str(txn.getDescription())
            row[dataKeys["_ACTION"][_COLUMN]] = str(txn.getTransferType())
            if lParent:
                row[dataKeys["_TT"][_COLUMN]] = str(txn.getInvestTxnType())
            else:
                row[dataKeys["_TT"][_COLUMN]] = str(txn.getParentTxn().getInvestTxnType())

            row[dataKeys["_CLEARED"][_COLUMN]] = str(txn.getStatusChar())

            if lParent:
                if xfrTxn:
                    row[dataKeys["_TRANSFER"][_COLUMN]] = xfrAcct.getFullAccountName()
            else:
                row[dataKeys["_TRANSFER"][_COLUMN]] = txn.getParentTxn().getAccount().getFullAccountName()

            if lParent:
                if securityTxn:
                    row[dataKeys["_AMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(securityTxn.getAmount())
                else:
                    row[dataKeys["_AMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(txn.getValue()) * -1
            else:
                row[dataKeys["_AMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(txn.getValue())

            if xfrTxn:  # Override the value set above. Why? It's the amount TXF'd out of the account....
                row[dataKeys["_AMOUNT"][_COLUMN]] = (acctCurr.getDoubleValue(xfrTxn.getAmount())) * -1
            elif incTxn:
                row[dataKeys["_AMOUNT"][_COLUMN]] = (acctCurr.getDoubleValue(incTxn.getAmount())) * -1
            elif expTxn:
                row[dataKeys["_AMOUNT"][_COLUMN]] = (acctCurr.getDoubleValue(expTxn.getAmount())) * -1

            row[dataKeys["_CHEQUE"][_COLUMN]] = str(txn.getCheckNumber())
            if lParent:
                row[dataKeys["_MEMO"][_COLUMN]] = str(txn.getMemo())
            else:
                row[dataKeys["_MEMO"][_COLUMN]] = str(txn.getParentTxn().getMemo())

            if expTxn:
                row[dataKeys["_CAT"][_COLUMN]] = expAcct.getFullAccountName()

            if incTxn:
                row[dataKeys["_CAT"][_COLUMN]] = incAcct.getFullAccountName()

            if feeTxn:
                row[dataKeys["_FEECAT"][_COLUMN]] = feeAcct.getFullAccountName()

            if incTxn:
                if feeTxn:
                    row[dataKeys["_FEE"][_COLUMN]] = acctCurr.getDoubleValue(feeTxn.getAmount())
                    row[dataKeys["_TXNNETAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(incTxn.getAmount()*-1 + feeTxn.getAmount()*-1)

                    # # Match Moneydance bug - until MD is fixed
                    # if lParent and str(txn.getTransferType()) == "xfrtp_miscincexp" and str(txn.getInvestTxnType()) == "MISCINC" \
                    #         and not xfrTxn and feeTxn:
                    #     row[dataKeys["_FEE"][_COLUMN]] = acctCurr.getDoubleValue(feeTxn.getAmount())
                    #     row[dataKeys["_TXNNETAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(txn.getValue() + feeTxn.getAmount()*-1)

                else:
                    row[dataKeys["_TXNNETAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(incTxn.getAmount()*-1)

            elif expTxn:
                if feeTxn:
                    row[dataKeys["_FEE"][_COLUMN]] = acctCurr.getDoubleValue(feeTxn.getAmount())
                    row[dataKeys["_TXNNETAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(expTxn.getAmount()*-1 + feeTxn.getAmount())

                    # Match Moneydance bug - until MD is fixed
                    if lParent and str(txn.getTransferType()) == "xfrtp_miscincexp" and str(txn.getInvestTxnType()) == "MISCEXP" \
                            and not xfrTxn and feeTxn:
                        row[dataKeys["_FEE"][_COLUMN]] = acctCurr.getDoubleValue(feeTxn.getAmount())
                        row[dataKeys["_TXNNETAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(txn.getValue())

                else:
                    row[dataKeys["_TXNNETAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(expTxn.getAmount()*-1)
            elif securityTxn:
                if feeTxn:
                    row[dataKeys["_FEE"][_COLUMN]] = acctCurr.getDoubleValue(feeTxn.getAmount())
                    row[dataKeys["_TXNNETAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(securityTxn.getAmount() + feeTxn.getAmount())
                else:
                    row[dataKeys["_TXNNETAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(securityTxn.getAmount())
            else:
                if feeTxn:
                    row[dataKeys["_FEE"][_COLUMN]] = acctCurr.getDoubleValue(feeTxn.getAmount())
                    row[dataKeys["_TXNNETAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(txn.getValue() + feeTxn.getAmount())
                else:
                    row[dataKeys["_TXNNETAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(txn.getValue())

            if row[dataKeys["_SHARES"][_COLUMN]] != 0:
                roundPrice = securityCurr.getDecimalPlaces()
                # noinspection PyUnresolvedReferences
                price = ((row[dataKeys["_AMOUNT"][_COLUMN]] / (row[dataKeys["_SHARES"][_COLUMN]])))
                row[dataKeys["_PRICE"][_COLUMN]] = price
                price = None

                if lAdjustForSplits:
                    # noinspection PyUnresolvedReferences
                    price = ((row[dataKeys["_AMOUNT"][_COLUMN]] / (row[dataKeys["_SHRSAFTERSPLIT"][_COLUMN]])))
                    row[dataKeys["_PRICEAFTERSPLIT"][_COLUMN]] = price
                    price = None

            if lParent and (str(txn.getInvestTxnType()) == "SELL_XFER" or str(txn.getInvestTxnType()) == "BUY_XFER"
                            or str(txn.getInvestTxnType()) == "DIVIDEND_REINVEST" or str(txn.getInvestTxnType()) == "DIVIDENDXFR"):
                row[dataKeys["_CASHIMPACT"][_COLUMN]] = 0.0
            elif incTxn or expTxn:
                row[dataKeys["_CASHIMPACT"][_COLUMN]] = row[dataKeys["_TXNNETAMOUNT"][_COLUMN]]
            elif securityTxn:
                row[dataKeys["_CASHIMPACT"][_COLUMN]] = row[dataKeys["_TXNNETAMOUNT"][_COLUMN]]*-1
            else:
                row[dataKeys["_CASHIMPACT"][_COLUMN]] = row[dataKeys["_TXNNETAMOUNT"][_COLUMN]]

            row[dataKeys["_HASATTACHMENTS"][_COLUMN]] = txn.hasAttachments()

            row[dataKeys["_ACCTCASHBAL"][_COLUMN]] = acctCurr.getDoubleValue(txnAcct.getBalance())


            # row[dataKeys["_CURRDPC"][_COLUMN]] = acctCurr.getDecimalPlaces()
            # row[dataKeys["_SECDPC"][_COLUMN]] = securityCurr.getDecimalPlaces()

            if securityTxn:
                row[dataKeys["_AVGCOST"][_COLUMN]] = securityAcct.getUsesAverageCost()

            if securityTxn and cbTags:
                lots = []
                for cbKey in cbTags.keys():
                    relatedCBTxn = rootbook.getTransactionSet().getTxnByID(cbKey)
                    if relatedCBTxn is not None:
                        lots.append([cbKey,
                                     relatedCBTxn.getTransferType(),
                                     relatedCBTxn.getOtherTxn(0).getInvestTxnType(),
                                     relatedCBTxn.getDateInt(),
                                     acctCurr.formatSemiFancy(relatedCBTxn.getValue(), decimalCharSep),
                                     acctCurr.getDoubleValue(relatedCBTxn.getAmount()),
                                     ])
                # endfor
                if len(lots) > 0:
                    row[dataKeys["_LOTS"][_COLUMN]] = lots
                # endif
            # endif

            myPrint("D", row)
            transactionTable.append(row)
            iCount += 1

        myPrint("B", "Investment Transaction Records selected:", len(transactionTable) )
        if iBal: myPrint("B", "...and %s Manual Opening Balance entries created too..." %iBal)
        ###########################################################################################################


        # sort the file: Account>Security>Date
        transactionTable = sorted(transactionTable, key=lambda x: (x[dataKeys["_ACCOUNT"][_COLUMN]],
                                                                   x[dataKeys["_DATE"][_COLUMN]]) )

        ###########################################################################################################


        def ExportDataToFile():
            global debug, csvfilename, decimalCharSep, groupingCharSep, csvDelimiter, version_build, myScriptName
            global transactionTable, userdateformat, lGlobalErrorDetected
            global lWriteBOMToExportFile_SWSS

            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

            headings = []
            sortDataFields = sorted(dataKeys.items(), key=lambda x: x[1][_COLUMN])
            for i in sortDataFields:
                headings.append(i[1][_HEADING])
            print

            myPrint("P", "Now pre-processing the file to convert integer dates and strip non-ASCII if requested....")
            for _row in transactionTable:
                dateasdate = datetime.datetime.strptime(str(_row[dataKeys["_DATE"][_COLUMN]]), "%Y%m%d")  # Convert to Date field
                dateoutput = dateasdate.strftime(userdateformat)
                _row[dataKeys["_DATE"][_COLUMN]] = dateoutput

                if _row[dataKeys["_TAXDATE"][_COLUMN]]:
                    dateasdate = datetime.datetime.strptime(str(_row[dataKeys["_TAXDATE"][_COLUMN]]), "%Y%m%d")  # Convert to Date field
                    dateoutput = dateasdate.strftime(userdateformat)
                    _row[dataKeys["_TAXDATE"][_COLUMN]] = dateoutput

                for col in range(0, dataKeys["_SECSHRHOLDING"][_COLUMN]):
                    _row[col] = fixFormatsStr(_row[col])

            # NOTE - You can add sep=; to beginning of file to tell Excel what delimiter you are using

            # Write the csvlines to a file
            myPrint("B", "Opening file and writing ", len(transactionTable), "records")


            try:
                # CSV Writer will take care of special characters / delimiters within fields by wrapping in quotes that Excel will decode
                with open(csvfilename,"wb") as csvfile:  # PY2.7 has no newline parameter so opening in binary; juse "w" and newline='' in PY3.0

                    if lWriteBOMToExportFile_SWSS:
                        csvfile.write(codecs.BOM_UTF8)   # This 'helps' Excel open file with double-click as UTF-8

                    writer = csv.writer(csvfile, dialect='excel', quoting=csv.QUOTE_MINIMAL, delimiter=fix_delimiter(csvDelimiter))

                    if csvDelimiter != ",":
                        writer.writerow(["sep=", ""])  # Tells Excel to open file with the alternative delimiter (it will add the delimiter to this line)

                    writer.writerow(headings)  # Print the header, but not the extra _field headings

                    for i in range(0, len(transactionTable)):
                        writer.writerow(transactionTable[i])

                    today = Calendar.getInstance()
                    writer.writerow([""])
                    writer.writerow(["StuWareSoftSystems - " + myScriptName + "(build: "
                                     + version_build
                                     + ")  Moneydance Python Script - Date of Extract: "
                                     + str(sdf.format(today.getTime()))])

                    writer.writerow([""])
                    writer.writerow(["User Parameters..."])

                    writer.writerow(["Hiding Hidden Securities...: %s" %(hideHiddenSecurities)])
                    writer.writerow(["Hiding Inactive Accounts...: %s" %(hideInactiveAccounts)])
                    writer.writerow(["Hiding Hidden Accounts.....: %s" %(hideHiddenAccounts)])
                    writer.writerow(["Security filter............: %s '%s'" %(lAllSecurity,filterForSecurity)])
                    writer.writerow(["Account filter.............: %s '%s'" %(lAllAccounts,filterForAccounts)])
                    writer.writerow(["Currency filter............: %s '%s'" %(lAllCurrency,filterForCurrency)])
                    writer.writerow(["Include Opening Balances...: %s" %(lIncludeOpeningBalances)])
                    writer.writerow(["Adjust for Splits..........: %s" %(lAdjustForSplits)])
                    writer.writerow(["Split Securities by Account: %s" %(userdateformat)])

                myPrint("B", "CSV file " + csvfilename + " created, records written, and file closed..")

            except IOError, e:
                lGlobalErrorDetected = True
                myPrint("B", "Oh no - File IO Error!", e)
                myPrint("B", "Path:", csvfilename)
                myPrint("B", "!!! ERROR - No file written - sorry! (was file open, permissions etc?)".upper())
                dump_sys_error_to_md_console_and_errorlog()
                myPopupInformationBox(extract_investment_transactions_fake_frame_,"Sorry - error writing to export file!", "FILE EXTRACT")

        # enddef


        def fixFormatsStr(theString, lNumber=False, sFormat=""):

            global lStripASCII

            if isinstance(theString, bool): return theString
            if isinstance(theString, tuple): return theString
            if isinstance(theString, dict): return theString
            if isinstance(theString, list): return theString

            if isinstance(theString, int) or isinstance(theString, float) or isinstance(theString, long):
                lNumber = True

            if lNumber is None: lNumber = False
            if theString is None: theString = ""

            if sFormat == "%" and theString != "":
                theString = "{:.1%}".format(theString)
                return theString

            if lNumber: return str(theString)

            theString = theString.strip()  # remove leading and trailing spaces

            theString = theString.replace("\n", "*")  # remove newlines within fields to keep csv format happy
            theString = theString.replace("\t", "*")  # remove tabs within fields to keep csv format happy
            theString = theString.replace(";", "*")  # remove tabs within fields to keep csv format happy
            theString = theString.replace(",", "*")  # remove tabs within fields to keep csv format happy
            theString = theString.replace("|", "*")  # remove tabs within fields to keep csv format happy

            if lStripASCII:
                all_ASCII = ''.join(char for char in theString if ord(char) < 128)  # Eliminate non ASCII printable Chars too....
            else:
                all_ASCII = theString
            return all_ASCII

        ExportDataToFile()
        if not lGlobalErrorDetected:
            myPopupInformationBox(extract_investment_transactions_fake_frame_,"Your extract has been created as requested",myScriptName)
            try:
                helper = moneydance.getPlatformHelper()
                helper.openDirectory(File(csvfilename))
            except:
                pass

if extract_investment_transactions_fake_frame_ is not None:
    extract_investment_transactions_fake_frame_.dispose()
    del extract_investment_transactions_fake_frame_

myPrint("B", "StuWareSoftSystems - ", myScriptName, " script ending......")

if not i_am_an_extension_so_run_headless: print(scriptExit)

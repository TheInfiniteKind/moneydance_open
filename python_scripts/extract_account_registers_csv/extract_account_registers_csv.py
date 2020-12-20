#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# extract_account_registers_csv.py - build: 4 - December 2020 - Stuart Beesley
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

# This script extracts Account Register transactions to csv file - and also grabs, decrypts, and stores your attachments

# Use in MoneyDance Menu Window->Show Moneybot Console >> Open Script >> RUN
# NOTE: This will not operate on Investment Accounts...

# Stuart Beesley Created 2020-12-11 tested on MacOS - MD2021 onwards - StuWareSoftSystems....
# Build: 1 beta - Initial release
# Build: 2 beta - Only include opening balances if not filtering records; Added Text filter for Memo and Description
# Build: 3 PREVIEW - Added a better status popup, a few tweaks to code...; removed key from csv; preserve original attachment names...
# Build: 3 PREVIEW - added foreign currency support
# Build: 4 PREVIEW - updated common codeset; leverage moneydance fonts

# todo dropdown date selection....

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
from com.infinitekind.moneydance.model import AccountUtil, AcctFilter, CurrencyType, CurrencyUtil, TxnSortOrder
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
if isinstance(None, (JDateField,CurrencyUtil,TxnSortOrder,Reminder,ParentTxn,SplitTxn,TxnSearch, JComboBox,
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
version_build = "4"                                                                                                 # noqa
myScriptName = "extract_account_registers_csv.py(Extension)"                                                        # noqa
debug = False                                                                                                       # noqa
myParameters = {}                                                                                                   # noqa
_resetParameters = False                                                                                            # noqa
lPickle_version_warning = False                                                                                     # noqa
lIamAMac = False                                                                                                    # noqa
lGlobalErrorDetected = False																						# noqa
# END SET THESE VARIABLES FOR ALL SCRIPTS ##############################################################################

# >>> THIS SCRIPT'S IMPORTS ############################################################################################
from copy import deepcopy
# >>> END THIS SCRIPT'S IMPORTS ########################################################################################

# >>> THIS SCRIPT'S GLOBALS ############################################################################################

# Saved to parameters file
global __extract_account_registers
global hideInactiveAccounts, hideHiddenAccounts, lAllCurrency, filterForCurrency
global lAllAccounts, filterForAccounts, lIncludeSubAccounts_EAR
global lIncludeOpeningBalances_EAR, userdateformat
global userdateStart_EAR, userdateEnd_EAR
global lAllTags_EAR, tagFilter_EAR, lExtractAttachments_EAR
global lStripASCII, scriptpath, csvDelimiter
global lWriteBOMToExportFile_SWSS, saveDropDownAccountUUID_EAR, lIncludeInternalTransfers_EAR
global lAllText_EAR, textFilter_EAR

# Other used by program
global csvfilename, lDisplayOnly
global baseCurrency, sdf
global transactionTable, dataKeys, attachmentDir, relativePath, lDidIUseAttachmentDir, extract_account_registers_frame_
# >>> END THIS SCRIPT'S GLOBALS ############################################################################################

# Set programmatic defaults/parameters for filters HERE.... Saved Parameters will override these now
# NOTE: You  can override in the pop-up screen
hideInactiveAccounts = True                                                                                         # noqa
hideHiddenAccounts = True                                                                                           # noqa
lAllCurrency = True                                                                                                 # noqa
filterForCurrency = "ALL"                                                                                           # noqa
lAllAccounts = True                                                                                                 # noqa
filterForAccounts = "ALL"                                                                                           # noqa
lIncludeSubAccounts_EAR = False                                                                                     # noqa
lIncludeOpeningBalances_EAR = True                                                                                  # noqa
userdateformat = "%Y/%m/%d"                                                                                         # noqa
userdateStart_EAR = 19700101                                                                                        # noqa
userdateEnd_EAR = 20201231                                                                                          # noqa
lAllTags_EAR = True                                                                                                 # noqa
tagFilter_EAR = "ALL"                                                                                               # noqa
lAllText_EAR = True                                                                                                 # noqa
textFilter_EAR = "ALL"                                                                                              # noqa
lExtractAttachments_EAR=False                                                                                       # noqa
lStripASCII = False                                                                                                 # noqa
csvDelimiter = ","                                                                                                  # noqa
scriptpath = ""                                                                                                     # noqa
lWriteBOMToExportFile_SWSS = True                                                                                   # noqa
saveDropDownAccountUUID_EAR = ""                                                                                    # noqa
lIncludeInternalTransfers_EAR = True                                                                                # noqa

extract_account_registers_frame_ = None                                                                             # noqa
attachmentDir = ""                                                                                                  # noqa
lDidIUseAttachmentDir = False                                                                                       # noqa
extract_filename="extract_account_registers.csv"
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
Toolbox                                 View Moneydance settings, diagnostics, fix issues, change settings and much more

Extension (.mxt) and Script (.py) Versions available:
StockGlance2020                         View summary of Securities/Stocks on screen, total by Security, export to csv 
extract_reminders_csv                   View reminders on screen, edit if required, extract all to csv
extract_currency_history_csv            Extract currency history to csv
extract_investment_transactions_csv     Extract investment transactions to csv
extract_account_registers_csv           Extract Account Register(s) to csv along with any attachments

Visit: https://yogi1967.github.io/MoneyDancePythonScripts/ (Author's site)
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
        myPrint("DB","Decimal Point Character:", _decimalCharSep)
        return _decimalCharSep

    if lGetGrouping:
        _groupingCharSep = decimalSymbols.getGroupingSeparator()
        myPrint("DB","Grouping Separator Character:", _groupingCharSep)
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
    myPrint("D", "MoneyDance Build:", moneydance.getVersion(), "Build:", moneydance.getBuild())


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
                super(JTextFieldLimitYN, self).insertString(myOffset, myString, myAttr)                         # noqa

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
    global __extract_account_registers
    global hideInactiveAccounts, hideHiddenAccounts, lAllCurrency, filterForCurrency
    global lAllAccounts, filterForAccounts, lIncludeSubAccounts_EAR
    global lIncludeOpeningBalances_EAR, userdateformat
    global userdateStart_EAR, userdateEnd_EAR
    global lAllTags_EAR, tagFilter_EAR, lExtractAttachments_EAR
    global lStripASCII, scriptpath, csvDelimiter
    global lWriteBOMToExportFile_SWSS, saveDropDownAccountUUID_EAR, lIncludeInternalTransfers_EAR
    global lAllText_EAR, textFilter_EAR

    myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )
    myPrint("DB", "Loading variables into memory...")

    if myParameters is None: myParameters = {}

    if myParameters.get("__extract_account_registers") is not None: __extract_account_registers = myParameters.get("__extract_account_registers")
    if myParameters.get("hideInactiveAccounts") is not None: hideInactiveAccounts = myParameters.get("hideInactiveAccounts")
    if myParameters.get("hideHiddenAccounts") is not None: hideHiddenAccounts = myParameters.get("hideHiddenAccounts")
    if myParameters.get("lAllCurrency") is not None: lAllCurrency = myParameters.get("lAllCurrency")
    if myParameters.get("filterForCurrency") is not None: filterForCurrency = myParameters.get("filterForCurrency")
    if myParameters.get("lAllAccounts") is not None: lAllAccounts = myParameters.get("lAllAccounts")
    if myParameters.get("filterForAccounts") is not None: filterForAccounts = myParameters.get("filterForAccounts")
    if myParameters.get("lIncludeSubAccounts_EAR") is not None: lIncludeSubAccounts_EAR = myParameters.get("lIncludeSubAccounts_EAR")
    if myParameters.get("userdateStart_EAR") is not None: userdateStart_EAR = myParameters.get("userdateStart_EAR")
    if myParameters.get("userdateEnd_EAR") is not None: userdateEnd_EAR = myParameters.get("userdateEnd_EAR")
    if myParameters.get("lAllTags_EAR") is not None: lAllTags_EAR = myParameters.get("lAllTags_EAR")
    if myParameters.get("tagFilter_EAR") is not None: tagFilter_EAR = myParameters.get("tagFilter_EAR")
    if myParameters.get("lAllText_EAR") is not None: lAllText_EAR = myParameters.get("lAllText_EAR")
    if myParameters.get("textFilter_EAR") is not None: textFilter_EAR = myParameters.get("textFilter_EAR")
    if myParameters.get("lExtractAttachments_EAR") is not None: lExtractAttachments_EAR = myParameters.get("lExtractAttachments_EAR")
    if myParameters.get("lStripASCII") is not None: lStripASCII = myParameters.get("lStripASCII")
    if myParameters.get("csvDelimiter") is not None: csvDelimiter = myParameters.get("csvDelimiter")
    if myParameters.get("lIncludeOpeningBalances_EAR") is not None: lIncludeOpeningBalances_EAR = myParameters.get("lIncludeOpeningBalances_EAR")
    if myParameters.get("userdateformat") is not None: userdateformat = myParameters.get("userdateformat")
    if myParameters.get("lWriteBOMToExportFile_SWSS") is not None: lWriteBOMToExportFile_SWSS = myParameters.get("lWriteBOMToExportFile_SWSS")                                                                                  # noqa
    if myParameters.get("saveDropDownAccountUUID_EAR") is not None: saveDropDownAccountUUID_EAR = myParameters.get("saveDropDownAccountUUID_EAR")                                                                                  # noqa
    if myParameters.get("lIncludeInternalTransfers_EAR") is not None: lIncludeInternalTransfers_EAR = myParameters.get("lIncludeInternalTransfers_EAR")                                                                                  # noqa

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
    global __extract_account_registers
    global hideInactiveAccounts, hideHiddenAccounts, lAllCurrency, filterForCurrency
    global lAllAccounts, filterForAccounts, lIncludeSubAccounts_EAR
    global lIncludeOpeningBalances_EAR, userdateformat
    global userdateStart_EAR, userdateEnd_EAR
    global lAllTags_EAR, tagFilter_EAR, lExtractAttachments_EAR
    global lAllText_EAR, textFilter_EAR
    global lStripASCII, scriptpath, csvDelimiter
    global lWriteBOMToExportFile_SWSS, saveDropDownAccountUUID_EAR, lIncludeInternalTransfers_EAR

    myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )

    # NOTE: Parameters were loaded earlier on... Preserve existing, and update any used ones...
    # (i.e. other StuWareSoftSystems programs might be sharing the same file)

    if myParameters is None: myParameters = {}

    myParameters["__extract_account_registers"] = version_build
    myParameters["hideInactiveAccounts"] = hideInactiveAccounts
    myParameters["hideHiddenAccounts"] = hideHiddenAccounts
    myParameters["lAllCurrency"] = lAllCurrency
    myParameters["filterForCurrency"] = filterForCurrency
    myParameters["lAllAccounts"] = lAllAccounts
    myParameters["filterForAccounts"] = filterForAccounts
    myParameters["lIncludeSubAccounts_EAR"] = lIncludeSubAccounts_EAR
    myParameters["lIncludeOpeningBalances_EAR"] = lIncludeOpeningBalances_EAR
    myParameters["userdateformat"] = userdateformat
    myParameters["userdateStart_EAR"] = userdateStart_EAR
    myParameters["userdateEnd_EAR"] = userdateEnd_EAR
    myParameters["lAllTags_EAR"] = lAllTags_EAR
    myParameters["tagFilter_EAR"] = tagFilter_EAR
    myParameters["lAllText_EAR"] = lAllText_EAR
    myParameters["textFilter_EAR"] = textFilter_EAR
    myParameters["lExtractAttachments_EAR"] = lExtractAttachments_EAR
    myParameters["lStripASCII"] = lStripASCII
    myParameters["csvDelimiter"] = csvDelimiter
    myParameters["lWriteBOMToExportFile_SWSS"] = lWriteBOMToExportFile_SWSS
    myParameters["lIncludeInternalTransfers_EAR"] = lIncludeInternalTransfers_EAR
    myParameters["saveDropDownAccountUUID_EAR"] = saveDropDownAccountUUID_EAR

    if not lDisplayOnly and scriptpath != "" and os.path.isdir(scriptpath):
        myParameters["scriptpath"] = scriptpath

    myPrint("DB","variables dumped from memory back into myParameters{}.....")

    return


get_StuWareSoftSystems_parameters_from_file()
myPrint("DB", "DEBUG IS ON..")
# END ALL CODE COPY HERE ###############################################################################################


# Create fake JFrame() so that all popups have correct Moneydance Icons etc
extract_account_registers_frame_ = JFrame()
if (not Platform.isMac()):
    moneydance_ui.getImages()
    extract_account_registers_frame_.setIconImage(MDImages.getImage(moneydance_ui.getMain().getSourceInformation().getIconResource()))
extract_account_registers_frame_.setUndecorated(True)
extract_account_registers_frame_.setVisible(False)
extract_account_registers_frame_.setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE)

csvfilename = None

if decimalCharSep != "." and csvDelimiter == ",": csvDelimiter = ";"  # Override for EU countries or where decimal point is actually a comma...
myPrint("DB", "Decimal point:", decimalCharSep, "Grouping Separator", groupingCharSep, "CSV Delimiter set to:", csvDelimiter)

sdf = SimpleDateFormat("dd/MM/yyyy")

saveColor = JLabel("TEST").getForeground()

labelHideInactiveAccounts = JLabel("Hide Inactive Accounts (Y/N)?:")
user_hideInactiveAccounts = JTextField(2)
user_hideInactiveAccounts.setDocument(JTextFieldLimitYN(1, True, "YN"))
if hideInactiveAccounts: user_hideInactiveAccounts.setText("Y")
else:                    user_hideInactiveAccounts.setText("N")

labelHideHiddenAccounts = JLabel("Hide Hidden Accounts (Y/N):")
user_hideHiddenAccounts = JTextField(2)
user_hideHiddenAccounts.setDocument(JTextFieldLimitYN(1, True, "YN"))
if hideHiddenAccounts: user_hideHiddenAccounts.setText("Y")
else:                  user_hideHiddenAccounts.setText("N")

labelFilterCurrency = JLabel("Filter for Currency containing text '...' or ALL:")
user_selectCurrency = JTextField(12)
user_selectCurrency.setDocument(JTextFieldLimitYN(30, True, "CURR"))
if lAllCurrency: user_selectCurrency.setText("ALL")
else:            user_selectCurrency.setText(filterForCurrency)

# noinspection PyArgumentList
class MyAcctFilterForDropdown(AcctFilter):

    def __init__(self):
        super(AcctFilter, self).__init__()

    def matches(self, acct):                                                                                        # noqa

        # noinspection PyUnresolvedReferences
        if not (acct.getAccountType() == Account.AccountType.BANK
                or acct.getAccountType() == Account.AccountType.CREDIT_CARD
                or acct.getAccountType() == Account.AccountType.ASSET):
            return False

        # This logic replicates Moneydance AcctFilter.ACTIVE_ACCOUNTS_FILTER
        if (acct.getAccountOrParentIsInactive()): return False
        if (acct.getHideOnHomePage() and acct.getBalance() == 0): return False

        return True


labelSelectOneAccount = JLabel("Select One Account here....")
acctList = AccountUtil.allMatchesForSearch(moneydance_data,MyAcctFilterForDropdown())
textToUse = "<NONE SELECTED - USE FILTERS BELOW>"
acctList.add(0,textToUse)
accountDropdown = JComboBox(acctList.toArray())

if saveDropDownAccountUUID_EAR != "":
    findAccount = AccountUtil.findAccountWithID(moneydance.getRootAccount(), saveDropDownAccountUUID_EAR)
    if findAccount:
        accountDropdown.setSelectedItem(findAccount)

labelFilterAccounts = JLabel("Filter for Accounts containing text '...' (or ALL):")
user_selectAccounts = JTextField(12)
user_selectAccounts.setDocument(JTextFieldLimitYN(30, True, "CURR"))
if lAllAccounts: user_selectAccounts.setText("ALL")
else:            user_selectAccounts.setText(filterForAccounts)

labelIncludeSubAccounts = JLabel("Include Sub Accounts (Y/N)?:")
user_includeSubAccounts = JTextField(2)
user_includeSubAccounts.setDocument(JTextFieldLimitYN(1, True, "YN"))
if lIncludeSubAccounts_EAR: user_includeSubAccounts.setText("Y")
else:                       user_includeSubAccounts.setText("N")

labelSeparator1 = JLabel("--------------------------------------------------------------------")
labelSeparator2 = JLabel("--<<Select Account above *OR* ACCT filters below - BUT NOT BOTH>>---".upper())
labelSeparator2.setForeground(Color.BLUE)
labelSeparator3 = JLabel("--------------------------------------------------------------------")
labelSeparator4 = JLabel("--------------------------------------------------------------------")
labelSeparator5 = JLabel("--------------------------------------------------------------------")
labelSeparator6 = JLabel("-------------<<Filters below are AND (not OR)>> --------------------")
labelSeparator6.setForeground(Color.BLUE)
labelSeparator7 = JLabel("--------------------------------------------------------------------")
labelSeparator8 = JLabel("--------------------------------------------------------------------")

labelOpeningBalances = JLabel("Include Opening Balances (Y/N):")
user_selectOpeningBalances = JTextField(2)
user_selectOpeningBalances.setDocument(JTextFieldLimitYN(1, True, "YN"))
if lIncludeOpeningBalances_EAR: user_selectOpeningBalances.setText("Y")
else:                           user_selectOpeningBalances.setText("N")

labelIncludeTransfers = JLabel("Include Transfers between Accounts Selected in this Extract (Y/N):")
user_selectIncludeTransfers = JTextField(2)
user_selectIncludeTransfers.setDocument(JTextFieldLimitYN(1, True, "YN"))
if lIncludeInternalTransfers_EAR: user_selectIncludeTransfers.setText("Y")
else:                    user_selectIncludeTransfers.setText("N")

labelDateStart = JLabel("Date range start (enter as yyyy/mm/dd):")
user_selectDateStart = JDateField(CustomDateFormat("ymd"),15)   # Use MD API function (not std Python)
user_selectDateStart.setDateInt(userdateStart_EAR)

labelDateEnd = JLabel("Date range end (enter as yyyy/mm/dd):")
user_selectDateEnd = JDateField(CustomDateFormat("ymd"),15)   # Use MD API function (not std Python)
user_selectDateEnd.setDateInt(userdateEnd_EAR)
# user_selectDateEnd.gotoToday()

labelTags = JLabel("Filter for Tags (separate with commas) or ALL:")
user_selectTags = JTextField(12)
user_selectTags.setDocument(JTextFieldLimitYN(30, True, "CURR"))
if lAllTags_EAR: user_selectTags.setText("ALL")
else:            user_selectTags.setText(tagFilter_EAR)

labelText = JLabel("Filter for Text in Description or Memo fields or ALL:")
user_selectText = JTextField(12)
user_selectText.setDocument(JTextFieldLimitYN(30, True, "CURR"))
if lAllText_EAR: user_selectText.setText("ALL")
else:            user_selectText.setText(textFilter_EAR)

labelAttachments = JLabel("Extract & Download Attachments (Y/N):")
user_selectExtractAttachments = JTextField(2)
user_selectExtractAttachments.setDocument(JTextFieldLimitYN(1, True, "YN"))
if lExtractAttachments_EAR: user_selectExtractAttachments.setText("Y")
else:                       user_selectExtractAttachments.setText("N")

labelDateFomat = JLabel("Output Date Format 1=dd/mm/yyyy, 2=mm/dd/yyyy, 3=yyyy/mm/dd, 4=yyyymmdd:")
user_dateformat = JTextField(2)
user_dateformat.setDocument(JTextFieldLimitYN(1, True, "1234"))

if userdateformat == "%d/%m/%Y": user_dateformat.setText("1")
elif userdateformat == "%m/%d/%Y": user_dateformat.setText("2")
elif userdateformat == "%Y/%m/%d": user_dateformat.setText("3")
elif userdateformat == "%Y%m%d": user_dateformat.setText("4")
else: user_dateformat.setText("3")

labelStripASCII = JLabel("Strip non ASCII characters from CSV export? (Y/N)")
user_selectStripASCII = JTextField(2)
user_selectStripASCII.setDocument(JTextFieldLimitYN(1, True, "YN"))
if lStripASCII: user_selectStripASCII.setText("Y")
else:               user_selectStripASCII.setText("N")

labelDelimiter = JLabel("Change CSV Export Delimiter from default to: ';|,'")
user_selectDELIMITER = JTextField(2)
user_selectDELIMITER.setDocument(JTextFieldLimitYN(1, True, "DELIM"))
user_selectDELIMITER.setText(csvDelimiter)

labelBOM = JLabel("Write BOM (Byte Order Mark) to file (helps Excel open files) (Y/N):")
user_selectBOM = JTextField(2)
user_selectBOM.setDocument(JTextFieldLimitYN(1, True, "YN"))
if lWriteBOMToExportFile_SWSS:  user_selectBOM.setText("Y")
else:                           user_selectBOM.setText("N")

labelDEBUG = JLabel("Turn DEBUG Verbose messages on? (Y/N)")
user_selectDEBUG = JTextField(2)
user_selectDEBUG.setDocument(JTextFieldLimitYN(1, True, "YN"))
if debug:  user_selectDEBUG.setText("Y")
else:           user_selectDEBUG.setText("N")

labelSTATUSbar = JLabel("")

userFilters = JPanel(GridLayout(0, 2))
userFilters.add(labelSelectOneAccount)
userFilters.add(accountDropdown)
userFilters.add(labelIncludeSubAccounts)
userFilters.add(user_includeSubAccounts)
userFilters.add(labelSeparator1)
userFilters.add(labelSeparator2)
userFilters.add(labelHideInactiveAccounts)
userFilters.add(user_hideInactiveAccounts)
userFilters.add(labelHideHiddenAccounts)
userFilters.add(user_hideHiddenAccounts)
userFilters.add(labelFilterAccounts)
userFilters.add(user_selectAccounts)
userFilters.add(labelFilterCurrency)
userFilters.add(user_selectCurrency)
userFilters.add(labelSeparator5)
userFilters.add(labelSeparator6)
userFilters.add(labelDateStart)
userFilters.add(user_selectDateStart)
userFilters.add(labelDateEnd)
userFilters.add(user_selectDateEnd)
userFilters.add(labelTags)
userFilters.add(user_selectTags)
userFilters.add(labelText)
userFilters.add(user_selectText)
userFilters.add(labelSeparator7)
userFilters.add(labelSeparator8)
userFilters.add(labelOpeningBalances)
userFilters.add(user_selectOpeningBalances)
# userFilters.add(labelIncludeTransfers)
# userFilters.add(user_selectIncludeTransfers)
userFilters.add(labelAttachments)
userFilters.add(user_selectExtractAttachments)
userFilters.add(labelDateFomat)
userFilters.add(user_dateformat)
userFilters.add(labelStripASCII)
userFilters.add(user_selectStripASCII)
userFilters.add(labelDelimiter)
userFilters.add(user_selectDELIMITER)
userFilters.add(labelBOM)
userFilters.add(user_selectBOM)
userFilters.add(labelDEBUG)
userFilters.add(user_selectDEBUG)

userFilters.add(labelSTATUSbar)

lExit = False
lDisplayOnly = False

options = ["ABORT", "CSV Export"]

while True:

    userAction = (JOptionPane.showOptionDialog(extract_account_registers_frame_,
                                         userFilters, "%s(build: %s) Set Script Parameters...."%(myScriptName,version_build),
                                         JOptionPane.OK_CANCEL_OPTION,
                                         JOptionPane.QUESTION_MESSAGE,
                                         moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                         options, options[1]))
    if userAction != 1:
        myPrint("B", "User Cancelled Parameter selection.. Will abort..")
        myPopupInformationBox(extract_account_registers_frame_, "User Cancelled Parameter selection.. Will abort..", "PARAMETERS")
        lDisplayOnly = False
        lExit = True
        break

    if not (user_selectDateStart.getDateInt() <= user_selectDateEnd.getDateInt()
            and user_selectDateEnd.getDateInt() >= user_selectDateStart.getDateInt()):
        user_selectDateStart.setForeground(Color.RED)
        user_selectDateEnd.setForeground(Color.RED)
        labelSTATUSbar.setText(">> Error - date range incorrect, please try again... <<".upper())
        labelSTATUSbar.setForeground(Color.RED)
        continue

    if user_selectTags.getText() != "ALL" and user_selectOpeningBalances.getText() == "Y":
        user_selectTags.setForeground(Color.RED)
        user_selectOpeningBalances.setForeground(Color.RED)
        labelSTATUSbar.setText(">> Error - You cannot filter on Tags and Include Opening Balances..... <<".upper())
        labelSTATUSbar.setForeground(Color.RED)
        continue

    if user_selectText.getText() != "ALL" and user_selectOpeningBalances.getText() == "Y":
        user_selectText.setForeground(Color.RED)
        user_selectOpeningBalances.setForeground(Color.RED)
        labelSTATUSbar.setText(">> Error - You cannot filter on Text and Include Opening Balances..... <<".upper())
        labelSTATUSbar.setForeground(Color.RED)
        continue

    user_selectDateStart.setForeground(saveColor)
    user_selectDateEnd.setForeground(saveColor)
    labelSTATUSbar.setText("")

    if isinstance(accountDropdown.getSelectedItem(),(str,unicode)) and accountDropdown.getSelectedItem() == textToUse:
        # So <NONE> Selected in Account dropdown....
        if user_includeSubAccounts.getText() != "N":
            user_includeSubAccounts.setText("N")
            labelSTATUSbar.setText(">> Error - Dropdown Accounts <NONE> and Include Sub Accounts Y... <<".upper())
            labelSTATUSbar.setForeground(Color.RED)
            user_includeSubAccounts.setForeground(Color.RED)
            accountDropdown.setForeground(Color.RED)
            continue
    elif isinstance(accountDropdown.getSelectedItem(),(Account)):

        if (user_selectAccounts.getText() != "ALL" or user_selectCurrency.getText() != "ALL"
                or user_hideInactiveAccounts.getText() != "Y" or user_hideHiddenAccounts.getText() != "Y"):
            user_selectAccounts.setText("ALL")
            user_selectCurrency.setText("ALL")
            user_hideInactiveAccounts.setText("Y")
            user_hideHiddenAccounts.setText("Y")
            labelSTATUSbar.setText(">> Error - Dropdown Accounts Selected. FILTERS RESET TO DEFAULTS <<".upper())
            labelSTATUSbar.setForeground(Color.RED)
            user_selectAccounts.setForeground(Color.RED)
            user_selectCurrency.setForeground(Color.RED)
            user_hideHiddenAccounts.setForeground(Color.RED)
            user_hideInactiveAccounts.setForeground(Color.RED)
            continue
    else:
        myPrint("B", "@@@ LOGIC ERROR IN PARAMETER DROPDOWN - ABORTING")
        raise(Exception("@@@ LOGIC ERROR IN PARAMETER DROPDOWN"))

    accountDropdown.setForeground(saveColor)
    user_includeSubAccounts.setForeground(saveColor)
    user_selectAccounts.setForeground(saveColor)
    user_selectCurrency.setForeground(saveColor)
    user_hideHiddenAccounts.setForeground(saveColor)
    user_hideInactiveAccounts.setForeground(saveColor)

    break   # Loop

if not lExit:
    myPrint("DB", "Parameters Captured",
        "DropdownAccount:", accountDropdown.getSelectedItem(),
        "SubActs:", user_includeSubAccounts.getText(),
        "InActAct:", user_hideInactiveAccounts.getText(),
        "HidAct:", user_hideHiddenAccounts.getText(),
        "Filter Accts:", user_selectAccounts.getText(),
        "Filter Curr:", user_selectCurrency.getText(),
        "Incl Open Bals:", user_selectOpeningBalances.getText(),
        # "Incl Transfers:", user_selectIncludeTransfers.getText(),
        "StartDate:", user_selectDateStart.getText(),
        "EndDate:", user_selectDateEnd.getText(),
        "DwnldAttchments:", user_selectExtractAttachments.getText(),
        "Tags:", user_selectTags.getText(),
        "Text:", user_selectText.getText(),
        "User Date Format:", user_dateformat.getText(),
        "Strip ASCII:", user_selectStripASCII.getText(),
        "Write BOM to file:", user_selectBOM.getText(),
        "Verbose Debug Messages: ", user_selectDEBUG.getText(),
        "CSV File Delimiter:", user_selectDELIMITER.getText())
    # endif

    hideInactiveAccounts = user_hideInactiveAccounts.getText() == "Y"
    hideHiddenAccounts = user_hideHiddenAccounts.getText() == "Y"
    lIncludeSubAccounts_EAR = user_includeSubAccounts.getText() == "Y"
    lIncludeOpeningBalances_EAR = user_selectOpeningBalances.getText() == "Y"
    lIncludeInternalTransfers_EAR = user_selectIncludeTransfers.getText() == "Y"
    lExtractAttachments_EAR = user_selectExtractAttachments.getText() == "Y"
    lWriteBOMToExportFile_SWSS = user_selectBOM.getText() == "Y"
    lStripASCII = user_selectStripASCII.getText() == "Y"
    debug = user_selectDEBUG.getText() == "Y"

    if user_selectTags.getText() == "ALL" or user_selectTags.getText().strip() == "":
        lAllTags_EAR = True
        tagFilter_EAR = "ALL"
    else:
        lAllTags_EAR = False
        tagFilter_EAR = user_selectTags.getText()

    if user_selectText.getText() == "ALL" or user_selectText.getText().strip() == "":
        lAllText_EAR = True
        textFilter_EAR = "ALL"
    else:
        lAllText_EAR = False
        textFilter_EAR = user_selectText.getText()

    userdateStart_EAR = user_selectDateStart.getDateInt()
    userdateEnd_EAR = user_selectDateEnd.getDateInt()

    if user_dateformat.getText() == "1": userdateformat = "%d/%m/%Y"
    elif user_dateformat.getText() == "2": userdateformat = "%m/%d/%Y"
    elif user_dateformat.getText() == "3": userdateformat = "%Y/%m/%d"
    elif user_dateformat.getText() == "4": userdateformat = "%Y%m%d"
    else:
        # PROBLEM /  default
        userdateformat = "%Y/%m/%d"

    csvDelimiter = user_selectDELIMITER.getText()
    if csvDelimiter == "" or (not (csvDelimiter in ";|,")):
        myPrint("B", "Invalid Delimiter:", csvDelimiter, "selected. Overriding with:','")
        csvDelimiter = ","
    if decimalCharSep == csvDelimiter:
        myPrint("B", "WARNING: The CSV file delimiter:", csvDelimiter, "cannot be the same as your decimal point character:",
            decimalCharSep, " - Proceeding without file export!!")
        lDisplayOnly = True

    if isinstance(accountDropdown.getSelectedItem(), Account):
        dropDownAccount_EAR = accountDropdown.getSelectedItem()
        # noinspection PyUnresolvedReferences
        saveDropDownAccountUUID_EAR = dropDownAccount_EAR.getUUID()
        labelIncludeSubAccounts = user_includeSubAccounts.getText() == "Y"
        lAllAccounts = True
        lAllCurrency = True
        filterForAccounts = "ALL"
        filterForCurrency = "ALL"
        hideInactiveAccounts = True
        hideHiddenAccounts = True
    else:
        dropDownAccount_EAR = None
        saveDropDownAccountUUID_EAR = None
        lIncludeSubAccounts_EAR = False
        if user_selectAccounts.getText() == "ALL" or user_selectAccounts.getText().strip() == "":
            lAllAccounts = True
            filterForAccounts = "ALL"
        else:
            lAllAccounts = False
            filterForAccounts = user_selectAccounts.getText()

        if user_selectCurrency.getText() == "ALL" or user_selectCurrency.getText().strip() == "":
            lAllCurrency = True
            filterForCurrency = "ALL"
        else:
            lAllCurrency = False
            filterForCurrency = user_selectCurrency.getText()


    myPrint("DB", "DEBUG still turned ON (from Parameters)")

    myPrint("B","User Parameters...")

    if dropDownAccount_EAR:
        # noinspection PyUnresolvedReferences
        myPrint("B","Dropdown Account selected..: %s" %(dropDownAccount_EAR.getAccountName()))
        myPrint("B","Include Sub Accounts.......: %s" %(lIncludeSubAccounts_EAR))
    else:
        myPrint("B","Hiding Inactive Accounts...: %s" %(hideInactiveAccounts))
        myPrint("B","Hiding Hidden Accounts.....: %s" %(hideHiddenAccounts))
        myPrint("B","Account filter.............: %s '%s'" %(lAllAccounts,filterForAccounts))
        myPrint("B","Currency filter............: %s '%s'" %(lAllCurrency,filterForCurrency))

    myPrint("B","Include Opening Balances...: %s" %(lIncludeOpeningBalances_EAR))
    # myPrint("B","Include Acct Transfers.....: %s" %(lIncludeInternalTransfers_EAR))
    myPrint("B","Tag filter.................: %s '%s'" %(lAllTags_EAR,tagFilter_EAR))
    myPrint("B","Text filter................: %s '%s'" %(lAllText_EAR,textFilter_EAR))
    myPrint("B","Download Attachments.......: %s" %(lExtractAttachments_EAR))
    myPrint("B","Selected Start Date........: %s" %(userdateStart_EAR))
    myPrint("B","Selected End Date..........: %s" %(userdateEnd_EAR))
    myPrint("B", "user date format..........: %s" %(userdateformat))

    # Now get the export filename
    csvfilename = None

    if not lDisplayOnly:  # i.e. we have asked for a file export - so get the filename - Always False in this script1
        myPrint("B","Strip non-ASCII characters.: %s" %(lStripASCII))
        myPrint("B","Add BOM to front of file...: %s" %(lWriteBOMToExportFile_SWSS))
        myPrint("B","CSV Export Delimiter.......: %s" %(csvDelimiter))

        def grabTheFile():
            global debug, lDisplayOnly, csvfilename, lIamAMac, scriptpath, myScriptName

            global attachmentDir, relativePath, lExtractAttachments_EAR

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

            if lExtractAttachments_EAR:
                filename = FileDialog(extract_account_registers_frame_, "Select/Create CSV file for extract - MUST BE A UNIQUE NAME -(CANCEL=NO EXPORT)")
            else:
                filename = FileDialog(extract_account_registers_frame_, "Select/Create CSV file for extract (CANCEL=NO EXPORT)")

            filename.setMultipleMode(False)
            filename.setMode(FileDialog.SAVE)
            if lExtractAttachments_EAR:
                split_the_name = os.path.splitext(extract_filename)
                attachmentDir = split_the_name[0]+get_filename_addition()
                newName = attachmentDir+split_the_name[1]
                filename.setFile(newName)
            else:
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
                myPopupInformationBox(extract_account_registers_frame_, "User chose to cancel or no file selected >>  So no Extract will be performed... ", "FILE EXPORT")
            elif str(csvfilename).endswith(".moneydance"):
                myPrint("B", "User selected file:", csvfilename)
                myPrint("B", "Sorry - User chose to use .moneydance extension - I will not allow it!... So no Extract will be performed...")
                myPopupInformationBox(extract_account_registers_frame_, "Sorry - User chose to use .moneydance extension - I will not allow it!... So no Extract will be performed...", "FILE EXPORT")
                lDisplayOnly = True
                csvfilename = None
            elif ".moneydance" in filename.getDirectory():
                myPrint("B", "User selected file:", filename.getDirectory(), csvfilename)
                myPrint("B", "Sorry - FileDialog() User chose to save file in .moneydance location. NOT Good practice so I will not allow it!... So no Extract will be performed...")
                myPopupInformationBox(extract_account_registers_frame_, "Sorry - FileDialog() User chose to save file in .moneydance location. NOT Good practice so I will not allow it!... So no Extract will be performed...", "FILE EXPORT")
                lDisplayOnly = True
                csvfilename = None
            else:
                if not lDisplayOnly:
                    relativePath = os.path.splitext(csvfilename)[0]

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
                    myPopupInformationBox(extract_account_registers_frame_, "Sorry - I just checked and you do not have permissions to create this file: %s" %csvfilename, "FILE EXPORT")
                    csvfilename=""
                    lDisplayOnly = True
                    return

                attachmentDir = None
                if lExtractAttachments_EAR:
                    attachmentDir = os.path.splitext( csvfilename )[0]
                    if os.path.exists(attachmentDir):
                        myPrint("B", "Sorry - Attachment Directory already exists... I need to create it: %s" %attachmentDir)
                        myPopupInformationBox(extract_account_registers_frame_, "Sorry - Attachment Directory already exists... I need to create it: %s" %attachmentDir, "ATTACHMENT DIRECTORY")
                        csvfilename=""
                        lDisplayOnly = True
                        return

                    try:
                        os.mkdir(attachmentDir)
                        myPrint("B", "Successfully created Attachment Directory: %s" %attachmentDir)
                        MyPopUpDialogBox(extract_account_registers_frame_, theStatus="I have created Attachment Directory:", theMessage=attachmentDir, theWidth=200, theTitle="Info",lModal=True).go()

                    except:
                        myPrint("B", "Sorry - Failed to create Attachment Directory: %s",attachmentDir)
                        myPopupInformationBox(extract_account_registers_frame_, "Sorry - Failed to create Attachment Directory: %s" %attachmentDir, "ATTACHMENT DIRECTORY")
                        csvfilename=""
                        lDisplayOnly = True
                        return

            return

        # enddef

        if not lDisplayOnly: grabTheFile()
    else:
        pass
    # endif

    if csvfilename is None:
        lDisplayOnly = True
        myPrint("P", "No Export will be performed")


    # save here in case script crashes....
    save_StuWareSoftSystems_parameters_to_file()


    if not lDisplayOnly:

        # noinspection PyArgumentList
        class MyAcctFilter(AcctFilter):

            def __init__(self,
                         _hideInactiveAccounts=True,
                         _hideHiddenAccounts=True,
                         _lAllAccounts=True,
                         _filterForAccounts="ALL",
                         _lAllCurrency=True,
                         _filterForCurrency="ALL"):
                super(AcctFilter, self).__init__()

                self._hideHiddenAccounts = _hideHiddenAccounts
                self._hideInactiveAccounts = _hideInactiveAccounts
                self._lAllAccounts = _lAllAccounts
                self._filterForAccounts = _filterForAccounts
                self._lAllCurrency = _lAllCurrency
                self._filterForCurrency = _filterForCurrency

                self.baseCurrency = moneydance.getCurrentAccountBook().getCurrencies().getBaseType()

            def matches(self, acct):

                # noinspection PyUnresolvedReferences
                if not (acct.getAccountType() == Account.AccountType.BANK
                        or acct.getAccountType() == Account.AccountType.CREDIT_CARD
                        or acct.getAccountType() == Account.AccountType.ASSET):
                    return False

                if self._hideInactiveAccounts:

                    # This logic replicates Moneydance AcctFilter.ACTIVE_ACCOUNTS_FILTER
                    if (acct.getAccountOrParentIsInactive()): return False
                    if (acct.getHideOnHomePage() and acct.getBalance() == 0): return False

                if self._lAllAccounts or (self._filterForAccounts.upper().strip() in acct.getFullAccountName().upper().strip()):
                    pass
                else:
                    return False

                curr = acct.getCurrencyType()
                currID = curr.getIDString()
                currName = curr.getName()

                # All accounts and security records can have currencies
                if self._lAllCurrency:
                    pass
                elif (self._filterForCurrency.upper().strip() in currID.upper().strip()):
                    pass
                elif (self._filterForCurrency.upper().strip() in currName.upper().strip()):
                    pass
                else:
                    return False

                # Phew! We made it....
                return True
            # enddef

        if dropDownAccount_EAR:
            if lIncludeSubAccounts_EAR:
                # noinspection PyUnresolvedReferences
                validAccountList = dropDownAccount_EAR.getSubAccounts()
            else:
                validAccountList = ArrayList()
            validAccountList.add(0,dropDownAccount_EAR)
        else:
            validAccountList = AccountUtil.allMatchesForSearch(moneydance_data,MyAcctFilter(_hideInactiveAccounts=hideInactiveAccounts,
                                                                                            _hideHiddenAccounts=hideHiddenAccounts,
                                                                                            _lAllAccounts=lAllAccounts,
                                                                                            _filterForAccounts=filterForAccounts,
                                                                                            _lAllCurrency=lAllCurrency,
                                                                                            _filterForCurrency=filterForCurrency))

        if debug:
            myPrint("DB","%s Accounts selected in filters" %len(validAccountList))
            for element in validAccountList: myPrint("D","...selected acct: %s" %element)

        _msg = MyPopUpDialogBox(extract_account_registers_frame_, "PLEASE WAIT....", "", 100, "Building Database",False)
        _msg.go()

        _COLUMN = 0
        _HEADING = 1
        dataKeys = {
                "_ACCOUNTTYPE":             [0,  "AccountType"],
                "_ACCOUNT":                 [1,  "Account"],
                "_DATE":                    [2,  "Date"],
                "_TAXDATE":                 [3,  "TaxDate"],
                "_CURR":                    [4,  "Currency"],
                "_CHEQUE":                  [5,  "Cheque"],
                "_DESC":                    [6,  "Description"],
                "_MEMO":                    [7,  "Memo"],
                "_CLEARED":                 [8,  "Cleared"],
                "_TOTALAMOUNT":             [9,  "TotalAmount"],
                "_FOREIGNTOTALAMOUNT":      [10, "ForeignTotalAmount"],
                "_PARENTTAGS":              [11, "ParentTags"],
                "_PARENTHASATTACHMENTS":    [12, "ParentHasAttachments"],
                "_SPLITIDX":                [13, "SplitIndex"],
                "_SPLITMEMO":               [14, "SplitMemo"],
                "_SPLITCAT":                [15, "SplitCategory"],
                "_SPLITAMOUNT":             [16, "SplitAmount"],
                "_FOREIGNSPLITAMOUNT":      [17, "ForeignSplitAmount"],
                "_SPLITTAGS":               [18, "SplitTags"],
                "_ISTRANSFERTOACCT":        [19, "isTransferToAnotherAccount"],
                "_ISTRANSFERSELECTED":      [20, "isTransferWithinThisExtract"],
                "_SPLITHASATTACHMENTS":     [21, "SplitHasAttachments"],
                "_ATTACHMENTLINK":          [22, "AttachmentLink"],
                "_ATTACHMENTLINKREL":       [23, "AttachmentLinkRelative"],
                "_KEY":                     [24, "Key"],
                "_END":                     [25, "_END"]
                }

        attachmentsDownloaded = 0
        transactionTable = []

        myPrint("DB", dataKeys)

        rootbook = moneydance.getCurrentAccountBook()
        rootaccount = rootbook.getRootAccount()
        baseCurrency = moneydance.getCurrentAccountBook().getCurrencies().getBaseType()

        # noinspection PyArgumentList
        class MyTxnSearchCostBasis(TxnSearch):

            def __init__(self, _validAccounts):
                super(TxnSearch, self).__init__()
                self._validAccounts = _validAccounts

            # noinspection PyMethodMayBeStatic
            def matchesAll(self):
                return False

            def matches(self, _txn):

                _txnAcct = _txn.getAccount()

                if _txnAcct in self._validAccounts:
                    return True
                else:
                    return False

        txns = rootbook.getTransactionSet().getTransactions(MyTxnSearchCostBasis(validAccountList))

        iBal = 0
        accountBalances = {}

        _local_storage = moneydance.getCurrentAccountBook().getLocalStorage()

        iCount = 0
        iCountAttachmentsDownloaded = 0

        def tag_search( searchForTags, theTagListToSearch ):

            searchTagList = searchForTags.upper().strip().split(",")

            for tag in theTagListToSearch:
                for searchTag in searchTagList:
                    if searchTag in tag.upper().strip():
                        return True

            return False

        def getTotalLocalValue( theTxn ):

            lValue = 0

            for _iSplit in range(0, (theTxn.getOtherTxnCount())):
                lValue += baseCurrency.getDoubleValue(parent_Txn.getOtherTxn(_iSplit).getValue()) * -1

            return lValue

        for txn in txns:

            if not (userdateStart_EAR <= txn.getDateInt() <= userdateEnd_EAR):
                continue

            lParent = isinstance(txn, ParentTxn)

            parent_Txn = txn.getParentTxn()
            txnAcct = txn.getAccount()
            acctCurr = txnAcct.getCurrencyType()  # Currency of the txn

            # Only include opening balances if not filtering records.... (this is caught during parameter selection earlier)
            if lIncludeOpeningBalances_EAR:
                if accountBalances.get(txnAcct):
                    pass
                else:
                    accountBalances[txnAcct] = True
                    openBal = acctCurr.getDoubleValue(txnAcct.getStartBalance())
                    if openBal != 0:
                        iBal+=1
                        row = ([None] * dataKeys["_END"][0])  # Create a blank row to be populated below...
                        row[dataKeys["_KEY"][_COLUMN]] = txnAcct.getUUID()
                        row[dataKeys["_ACCOUNTTYPE"][_COLUMN]] = str(txnAcct.getAccountType())
                        row[dataKeys["_ACCOUNT"][_COLUMN]] = txnAcct.getFullAccountName()
                        row[dataKeys["_CURR"][_COLUMN]] = acctCurr.getIDString()
                        row[dataKeys["_DESC"][_COLUMN]] = "MANUAL OPENING BALANCE"
                        row[dataKeys["_CHEQUE"][_COLUMN]] = "MANUAL"
                        row[dataKeys["_DATE"][_COLUMN]] = txnAcct.getCreationDateInt()
                        row[dataKeys["_SPLITIDX"][_COLUMN]] = 0
                        if acctCurr == baseCurrency:
                            row[dataKeys["_TOTALAMOUNT"][_COLUMN]] = openBal
                            row[dataKeys["_SPLITAMOUNT"][_COLUMN]] = openBal
                        else:
                            row[dataKeys["_TOTALAMOUNT"][_COLUMN]] = round(openBal / acctCurr.getRate(baseCurrency),2)
                            row[dataKeys["_SPLITAMOUNT"][_COLUMN]] = round(openBal / acctCurr.getRate(baseCurrency),2)
                            row[dataKeys["_FOREIGNTOTALAMOUNT"][_COLUMN]] = openBal
                            row[dataKeys["_FOREIGNSPLITAMOUNT"][_COLUMN]] = openBal


                        myPrint("D", row)
                        transactionTable.append(row)

            keyIndex = 0
            row = ([None] * dataKeys["_END"][0])  # Create a blank row to be populated below...

            txnKey = txn.getUUID()
            row[dataKeys["_KEY"][_COLUMN]] = txnKey + "-" + str(keyIndex).zfill(3)

            row[dataKeys["_ACCOUNTTYPE"][_COLUMN]] = str(txnAcct.getAccountType())
            row[dataKeys["_ACCOUNT"][_COLUMN]] = txnAcct.getFullAccountName()
            row[dataKeys["_CURR"][_COLUMN]] = acctCurr.getIDString()
            row[dataKeys["_DATE"][_COLUMN]] = txn.getDateInt()
            if parent_Txn.getTaxDateInt() != txn.getDateInt():
                row[dataKeys["_TAXDATE"][_COLUMN]] = txn.getTaxDateInt()

            row[dataKeys["_CHEQUE"][_COLUMN]] = txn.getCheckNumber()

            row[dataKeys["_DESC"][_COLUMN]] = parent_Txn.getDescription()
            if lParent:
                row[dataKeys["_MEMO"][_COLUMN]] = txn.getMemo()
            else:
                row[dataKeys["_MEMO"][_COLUMN]] = txn.getDescription()
            row[dataKeys["_CLEARED"][_COLUMN]] = txn.getStatusChar()


            if acctCurr == baseCurrency:
                row[dataKeys["_TOTALAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(txn.getValue())
            else:
                if lParent:
                    row[dataKeys["_FOREIGNTOTALAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(txn.getValue())
                    localValue = getTotalLocalValue( txn )
                    row[dataKeys["_TOTALAMOUNT"][_COLUMN]] = localValue
                else:
                    row[dataKeys["_FOREIGNTOTALAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(txn.getValue())
                    row[dataKeys["_TOTALAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(txn.getAmount())

            row[dataKeys["_PARENTHASATTACHMENTS"][_COLUMN]] = parent_Txn.hasAttachments()
            if str(parent_Txn.getKeywords()) != "[]": row[dataKeys["_PARENTTAGS"][_COLUMN]] = str(parent_Txn.getKeywords())

            uniqueFileNumber = 0
            for _ii in range(0, int(parent_Txn.getOtherTxnCount())):        # If a split, then it will always make it here...

                if not lParent and _ii > 0: break

                splitRowCopy = deepcopy(row)

                if lParent:

                    if (not lAllTags_EAR
                            and not tag_search(tagFilter_EAR, txn.getKeywords())
                            and not tag_search(tagFilter_EAR, parent_Txn.getOtherTxn(_ii).getKeywords())):
                        break

                    if (not lAllText_EAR
                            and textFilter_EAR not in (parent_Txn.getDescription().upper().strip()
                                                       +txn.getMemo().upper().strip()
                                                       +parent_Txn.getOtherTxn(_ii).getDescription().upper()).strip()):
                        break

                    splitMemo = parent_Txn.getOtherTxn(_ii).getDescription()
                    splitTags = str(parent_Txn.getOtherTxn(_ii).getKeywords())
                    splitCat = parent_Txn.getOtherTxn(_ii).getAccount().getAccountName()
                    splitHasAttachments = parent_Txn.getOtherTxn(_ii).hasAttachments()

                    splitAmount = acctCurr.getDoubleValue(parent_Txn.getOtherTxn(_ii).getValue()) * -1

                    splitFAmount = None
                    if parent_Txn.getOtherTxn(_ii).getAmount() != parent_Txn.getOtherTxn(_ii).getValue():
                        splitFAmount = acctCurr.getDoubleValue(parent_Txn.getOtherTxn(_ii).getAmount()) * -1

                    transferAcct = parent_Txn.getOtherTxn(_ii).getAccount()
                    transferType = transferAcct.getAccountType()

                    # noinspection PyUnresolvedReferences
                    if transferAcct != txnAcct and not (
                            transferType == Account.AccountType.ROOT
                            or transferType == Account.AccountType.INCOME
                            or transferType == Account.AccountType.EXPENSE):
                        isTransfer = True
                    else:
                        isTransfer = False

                    isTransferWithinExtract = (isTransfer and transferAcct in validAccountList)

                    if splitTags == "[]": splitTags = ""
                else:
                    # We are on a split - which is a standalone transfer in/out
                    if (not lAllTags_EAR
                            and not tag_search(tagFilter_EAR, txn.getKeywords())
                            and not tag_search(tagFilter_EAR, parent_Txn.getKeywords())):
                        break

                    if (not lAllText_EAR
                            and textFilter_EAR not in (txn.getDescription().upper().strip()
                                                       +parent_Txn.getDescription().upper().strip()
                                                       +parent_Txn.getMemo().upper().strip())):
                        break

                    splitMemo = txn.getDescription()
                    splitTags = str(txn.getKeywords())
                    splitCat = parent_Txn.getAccount().getAccountName()
                    splitHasAttachments = txn.hasAttachments()

                    splitAmount = acctCurr.getDoubleValue(txn.getValue())

                    splitFAmount = None
                    if txn.getAmount() != txn.getValue():
                        splitFAmount = acctCurr.getDoubleValue(txn.getAmount())

                    transferAcct = parent_Txn.getAccount()
                    transferType = transferAcct.getAccountType()

                    # noinspection PyUnresolvedReferences
                    if transferAcct != txnAcct and not (
                            transferType == Account.AccountType.ROOT
                            or transferType == Account.AccountType.INCOME
                            or transferType == Account.AccountType.EXPENSE):
                        isTransfer = True
                    else:
                        isTransfer = False

                    isTransferWithinExtract = (isTransfer and transferAcct in validAccountList)

                    if splitTags == "[]": splitTags = ""

                if _ii > 0:
                    splitRowCopy[dataKeys["_TOTALAMOUNT"][_COLUMN]] = None  # Don't repeat this on subsequent rows
                    splitRowCopy[dataKeys["_FOREIGNTOTALAMOUNT"][_COLUMN]] = None  # Don't repeat this on subsequent rows

                splitRowCopy[dataKeys["_KEY"][_COLUMN]] = txnKey + "-" + str(keyIndex).zfill(3)
                splitRowCopy[dataKeys["_SPLITIDX"][_COLUMN]] = _ii
                splitRowCopy[dataKeys["_SPLITMEMO"][_COLUMN]] = splitMemo
                splitRowCopy[dataKeys["_SPLITAMOUNT"][_COLUMN]] = splitAmount
                splitRowCopy[dataKeys["_FOREIGNSPLITAMOUNT"][_COLUMN]] = splitFAmount
                splitRowCopy[dataKeys["_SPLITTAGS"][_COLUMN]] = splitTags
                splitRowCopy[dataKeys["_SPLITCAT"][_COLUMN]] = splitCat
                splitRowCopy[dataKeys["_SPLITHASATTACHMENTS"][_COLUMN]] = splitHasAttachments
                splitRowCopy[dataKeys["_ISTRANSFERTOACCT"][_COLUMN]] = isTransfer
                splitRowCopy[dataKeys["_ISTRANSFERSELECTED"][_COLUMN]] = isTransferWithinExtract

                holdTheKeys = ArrayList()
                holdTheLocations = ArrayList()

                if _ii == 0 and txn.hasAttachments():
                    # noinspection PyUnresolvedReferences
                    holdTheKeys = holdTheKeys + txn.getAttachmentKeys()
                    for _attachKey in txn.getAttachmentKeys():
                        # noinspection PyUnresolvedReferences
                        holdTheLocations.append(txn.getAttachmentTag(_attachKey))

                if lParent and parent_Txn.getOtherTxn(_ii).hasAttachments():
                    holdTheKeys = holdTheKeys + parent_Txn.getOtherTxn(_ii).getAttachmentKeys()
                    for _attachKey in parent_Txn.getOtherTxn(_ii).getAttachmentKeys():
                        # noinspection PyUnresolvedReferences
                        holdTheLocations.append(parent_Txn.getOtherTxn(_ii).getAttachmentTag(_attachKey))

                if not lExtractAttachments_EAR or not holdTheKeys:
                    if holdTheKeys:
                        splitRowCopy[dataKeys["_ATTACHMENTLINK"][_COLUMN]] = str(holdTheKeys)
                    myPrint("D", splitRowCopy)
                    transactionTable.append(splitRowCopy)
                    # abort
                    keyIndex += 1
                    iCount += 1
                    continue

                # ok, we should still be on the first split record here.... and we want to download attachments....
                attachmentFileList=[]
                attachmentKeys = holdTheKeys
                attachmentLocations = holdTheLocations
                uniqueFileString=" "*3
                for attachmentLocation in attachmentLocations:
                    uniqueFileString = str(uniqueFileNumber).strip().zfill(3)
                    # attachmentLocation = txn.getAttachmentTag(attachmentKey)
                    # outputFile = os.path.join(attachmentDir,str(uniqueFileString)+ os.path.splitext(attachmentLocation)[1] )
                    outputFile = os.path.join(attachmentDir,str(uniqueFileString)+"-"+os.path.basename(attachmentLocation) )
                    _ostr = FileOutputStream( File(outputFile) )
                    bytesCopied = _local_storage.readFile(attachmentLocation, _ostr)
                    _ostr.close()
                    myPrint("DB","Attachment %s bytes >> %s copied to %s" %(bytesCopied, attachmentLocation,outputFile))
                    uniqueFileNumber += 1
                    attachmentFileList.append(outputFile)
                    iCountAttachmentsDownloaded += 1
                    lDidIUseAttachmentDir = True


                if len(attachmentFileList) < 1:
                    myPrint("B", "@@Major Error whilst searching attachments! Will just move on to next record and skip attachment")
                    splitRowCopy[dataKeys["_ATTACHMENTLINK"][_COLUMN]] = "*ERROR*"
                    myPrint("B", splitRowCopy)
                    transactionTable.append(splitRowCopy)
                    keyIndex += 1
                    iCount += 1
                    continue
                else:
                    for _i in range(0,len(attachmentFileList)):
                        rowCopy = deepcopy(splitRowCopy)  # Otherwise passes by references and future changes affect the original(s)

                        if _i > 0:  # If not on first record, update the key...
                            rowCopy[dataKeys["_KEY"][_COLUMN]] = txnKey + "-" + str(keyIndex).zfill(3)

                        if _i > 0:
                            rowCopy[dataKeys["_TOTALAMOUNT"][_COLUMN]] = None
                            rowCopy[dataKeys["_FOREIGNTOTALAMOUNT"][_COLUMN]] = None

                        if _i > 0:  # Inefficient, but won't happen very often - nuke the replicated fields on extra rows
                            for _c in range(dataKeys["_PARENTHASATTACHMENTS"][_COLUMN]+1,dataKeys["_ATTACHMENTLINK"][_COLUMN]):
                                rowCopy[_c] = None

                        rowCopy[dataKeys["_SPLITIDX"][_COLUMN]] = _ii
                        # rowCopy[dataKeys["_ATTACHMENTLINK"][_COLUMN]]     = "FILE://" + attachmentFileList[_i]
                        rowCopy[dataKeys["_ATTACHMENTLINK"][_COLUMN]] = '=HYPERLINK("'+attachmentFileList[_i]+'","FILE: '+os.path.basename(attachmentFileList[_i])[len(uniqueFileString)+1:]+'")'
                        rowCopy[dataKeys["_ATTACHMENTLINKREL"][_COLUMN]] = '=HYPERLINK("'+os.path.join(".",relativePath,os.path.basename(attachmentFileList[_i]))+'","FILE: '+os.path.basename(attachmentFileList[_i])[len(uniqueFileString)+1:]+'")'
                        transactionTable.append(rowCopy)
                        keyIndex += 1
                        iCount += 1


        myPrint("B", "Account Register Transaction Records (Parents, Splits, Attachments) selected:", len(transactionTable) )
        if iCountAttachmentsDownloaded:
            myPrint("B", ".. and I downloaded %s attachments for you too" %iCountAttachmentsDownloaded )
        if iBal: myPrint("B", "...and %s Manual Opening Balance entries created too..." %iBal)
        ###########################################################################################################


        myPrint("P","Sorting... please wait....")
        # sort the file:
        transactionTable = sorted(transactionTable, key=lambda x: (x[dataKeys["_ACCOUNTTYPE"][_COLUMN]],
                                                                   x[dataKeys["_ACCOUNT"][_COLUMN]],
                                                                   x[dataKeys["_DATE"][_COLUMN]],
                                                                   x[dataKeys["_KEY"][_COLUMN]],
                                                                   x[dataKeys["_SPLITIDX"][_COLUMN]]) )

        ###########################################################################################################


        def ExportDataToFile():
            global debug, csvfilename, decimalCharSep, groupingCharSep, csvDelimiter, version_build, myScriptName
            global transactionTable, userdateformat, lGlobalErrorDetected
            global lWriteBOMToExportFile_SWSS
            global lAllTags_EAR, tagFilter_EAR
            global lAllText_EAR, textFilter_EAR
            global lExtractAttachments_EAR, relativePath

            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

            headings = []
            sortDataFields = sorted(dataKeys.items(), key=lambda x: x[1][_COLUMN])
            for i in sortDataFields:
                headings.append(i[1][_HEADING])
            print

            myPrint("P", "Now pre-processing the file to convert integer dates and strip non-ASCII if requested....")
            for _row in transactionTable:
                # try:
                dateasdate = datetime.datetime.strptime(str(_row[dataKeys["_DATE"][_COLUMN]]), "%Y%m%d")  # Convert to Date field
                dateoutput = dateasdate.strftime(userdateformat)
                _row[dataKeys["_DATE"][_COLUMN]] = dateoutput
                # except:
                #     myPrint("B","Logic error post-processing _DATE on row: %s" %_row)

                if _row[dataKeys["_TAXDATE"][_COLUMN]]:
                    dateasdate = datetime.datetime.strptime(str(_row[dataKeys["_TAXDATE"][_COLUMN]]), "%Y%m%d")  # Convert to Date field
                    dateoutput = dateasdate.strftime(userdateformat)
                    _row[dataKeys["_TAXDATE"][_COLUMN]] = dateoutput

                for col in range(0, dataKeys["_ATTACHMENTLINK"][_COLUMN]):  # DO NOT MESS WITH ATTACHMENT LINK NAMES!!
                    _row[col] = fixFormatsStr(_row[col])

            # NOTE - You can add sep=; to beginning of file to tell Excel what delimiter you are using

            # Write the csvlines to a file
            myPrint("B", "Opening file and writing ", len(transactionTable), "records")


            try:
                # CSV Writer will take care of special characters / delimiters within fields by wrapping in quotes that Excel will decode
                with open(csvfilename,"wb") as csvfile:  # PY2.7 has no newline parameter so opening in binary; juse "w" and newline='' in PY3.0

                    if lWriteBOMToExportFile_SWSS:
                        csvfile.write(codecs.BOM_UTF8)   # This 'helps' Excel open file with double-click as UTF-8

                    writer = csv.writer(csvfile, dialect='excel', quoting=csv.QUOTE_MINIMAL, delimiter=csvDelimiter)

                    if csvDelimiter != ",":
                        writer.writerow(["sep=", ""])  # Tells Excel to open file with the alternative delimiter (it will add the delimiter to this line)

                    if lExtractAttachments_EAR and Platform.isOSX():
                        writer.writerow([""])
                        writer.writerow(["** On a Mac with Later versions of Excel, Apple 'Sand Boxing' prevents file access..."])
                        writer.writerow(["** Edit this cell below, then press Enter and it will change to a Hyperlink (blue)"])
                        writer.writerow(["** Click it, then Open, and then GRANT access to the folder.... (the links below will then work)"])
                        writer.writerow([""])
                        # writer.writerow(["FILE://" + os.path.join(".",relativePath)])
                        writer.writerow(["FILE://" + scriptpath])
                        writer.writerow([""])

                    if lExtractAttachments_EAR:
                        writer.writerow(headings[:dataKeys["_KEY"][_COLUMN]])  # Print the header, but not the extra _field headings
                    else:
                        writer.writerow(headings[:dataKeys["_ATTACHMENTLINKREL"][_COLUMN]])  # Print the header, but not the extra _field headings

                    for i in range(0, len(transactionTable)):
                        if lExtractAttachments_EAR:
                            writer.writerow(transactionTable[i][:dataKeys["_KEY"][_COLUMN]])
                        else:
                            writer.writerow(transactionTable[i][:dataKeys["_ATTACHMENTLINKREL"][_COLUMN]])

                    today = Calendar.getInstance()
                    writer.writerow([""])
                    writer.writerow(["StuWareSoftSystems - " + myScriptName + "(build: "
                                     + version_build
                                     + ")  MoneyDance Python Script - Date of Extract: "
                                     + str(sdf.format(today.getTime()))])

                    writer.writerow([""])
                    writer.writerow(["User Parameters..."])

                    if dropDownAccount_EAR:
                        # noinspection PyUnresolvedReferences
                        writer.writerow(["Dropdown Account selected..: %s" %(dropDownAccount_EAR.getAccountName())])
                        writer.writerow(["Include Sub Accounts.......: %s" %(lIncludeSubAccounts_EAR)])
                    else:
                        writer.writerow(["Hiding Inactive Accounts...: %s" %(hideInactiveAccounts)])
                        writer.writerow(["Hiding Hidden Accounts.....: %s" %(hideHiddenAccounts)])
                        writer.writerow(["Account filter.............: %s '%s'" %(lAllAccounts,filterForAccounts)])
                        writer.writerow(["Currency filter............: %s '%s'" %(lAllCurrency,filterForCurrency)])

                    writer.writerow(["Include Opening Balances...: %s" %(lIncludeOpeningBalances_EAR)])
                    # writer.writerow(["Include Acct Transfers.....: %s" %(lIncludeInternalTransfers_EAR)])
                    writer.writerow(["Tag filter.................: %s '%s'" %(lAllTags_EAR,tagFilter_EAR)])
                    writer.writerow(["Text filter................: %s '%s'" %(lAllText_EAR,textFilter_EAR)])
                    writer.writerow(["Download Attachments.......: %s" %(lExtractAttachments_EAR)])
                    writer.writerow(["Selected Start Date........: %s" %(userdateStart_EAR)])
                    writer.writerow(["Selected End Date..........: %s" %(userdateEnd_EAR)])
                    writer.writerow(["user date format..........: %s" %(userdateformat)])

                myPrint("B", "CSV file " + csvfilename + " created, records written, and file closed..")

            except IOError, e:
                lGlobalErrorDetected = True
                myPrint("B", "Oh no - File IO Error!", e)
                myPrint("B", "Path:", csvfilename)
                myPrint("B", "!!! ERROR - No file written - sorry! (was file open, permissions etc?)".upper())
                dump_sys_error_to_md_console_and_errorlog()
                myPopupInformationBox(extract_account_registers_frame_,"Sorry - error writing to export file!", "FILE EXTRACT")

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
            # theString = theString.replace(";", "*")  # remove tabs within fields to keep csv format happy
            # theString = theString.replace(",", "*")  # remove tabs within fields to keep csv format happy
            # theString = theString.replace("|", "*")  # remove tabs within fields to keep csv format happy

            if lStripASCII:
                all_ASCII = ''.join(char for char in theString if ord(char) < 128)  # Eliminate non ASCII printable Chars too....
            else:
                all_ASCII = theString
            return all_ASCII

        if iBal+iCount > 0:
            ExportDataToFile()
            _msg.kill()
            if not lGlobalErrorDetected:
                MyPopUpDialogBox(extract_account_registers_frame_,
                                 "Your extract has been created as requested:",
                                 "With %s rows and %s attachments downloaded"%(iBal+iCount,iCountAttachmentsDownloaded),
                                 200,
                                 myScriptName,lModal=True).go()

                try:
                    helper = moneydance.getPlatformHelper()
                    helper.openDirectory(File(csvfilename))
                except:
                    pass
        else:
            _msg.kill()
            myPopupInformationBox(extract_account_registers_frame_,"No records selected and no extract file created....",myScriptName)

        # Clean up...
        if not lDidIUseAttachmentDir:
            try:
                os.rmdir(attachmentDir)
                myPrint("B", "Successfully removed unused/empty Attachment Directory: %s" %attachmentDir)

            except:
                myPrint("B", "Sorry - I failed to remove the unused/empty Attachment Directory: %s",attachmentDir)

        # delete references to large objects
        del transactionTable
        del accountBalances

if extract_account_registers_frame_ is not None:
    extract_account_registers_frame_.dispose()

myPrint("B", "StuWareSoftSystems - ", myScriptName, " script ending......")

if not i_am_an_extension_so_run_headless: print(scriptExit)

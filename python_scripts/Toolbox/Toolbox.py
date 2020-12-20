#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Toolbox.py build: 1003 - November-December 2020 - Stuart Beesley StuWareSoftSystems
# NOTE: I am just a fellow Moneydance User >> I HAVE NO AFFILIATION WITH MONEYDANCE
# NOTE: I have run all these fixes / updates on my own live personal dataset
# Thanks and credit to Derek Kent(23) for his extensive testing and suggestions....
# Credit of course to Moneydance and they retain all copyright over Moneydance internal code
# Designed to show user a number of settings / fixes / updates they may find useful (some normally hidden)
# The Basic / Geek Out Mode(s) are very safe and do not change any data or settings
# If you switch to Advanced / Hacker mode(s) then you have the ability to perform fixes, change data, change config etc
# NOTE: Any change that impacts config.dict, custom_theme.properties, LocalStorage() ./safe/settings...
#       will always backup that single config/settings file (in the directory where it's located).
#       This is not the same as backing up your Dataset that contains your financial data.

# DISCLAIMER >> PLEASE ALWAYS BACKUP YOUR DATA BEFORE MAKING CHANGES (Menu>Export Backup will achieve this)

# Includes previous / standalone scripts (which I have now decommissioned):
# FIX-reset_window_location_data.py 0.2beta
# DIAG-can_i_delete_security.py v2
# DIAG-list_security_currency_decimal_places.py v1
# DIAG-diagnose_currencies.py v2a
# fix_macos_tabbing_mode.py v1b

# reset_relative_currencies.py              (from Moneydance support)
# remove_ofx_account_bindings.py            (from Moneydance support)
# convert_secondary_to_primary_data_set.py  (from Moneydance support)
# remove_one_service.py                     (from Moneydance support)
# delete_invalid_txns.py                    (from Moneydance support)
###############################################################################
# MIT License
#
# Copyright (c) 2020 Stuart Beesley - StuWareSoftSystems & Moneydance
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

# Build: 999 PREVIEW RELEASE
# Build: 999a Added some instructions on how to properly edit Moneydance.vmoptions file; added to help file(s)
# Build: 999a Now finds the application directory for MacOS too....
# Build: 1000 INITIAL PUBLIC RELEASE
# Build: 1001 Enhanced MyPrint to catch unicode utf-8 encode/decode errors
# Build: 1002 - fixed raise(Exception) clauses ;->
# Build: 1002 - Now leveraging the Default font set in Moneydance; added change Fonts Button
# Build: 1003 - Updated common codeset

# NOTE - I Use IntelliJ IDE - you may see # noinspection Pyxxxx or # noqa comments
# These tell the IDE to ignore certain irrelevant/erroneous warnings being reporting:
# Also: These objects: moneydance_ui, moneydance_data, moneydance are set as ignore Unresolved References (as they exist at run time)
# Further options at: https://www.jetbrains.com/help/pycharm/disabling-and-enabling-inspections.html#comments-ref

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

from javax.swing import JButton, JScrollPane, WindowConstants, JFrame, JLabel, JPanel, JComponent, KeyStroke, JDialog
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
if isinstance(None, (JDateField,CurrencyUtil,TxnSortOrder,Reminder,ParentTxn,SplitTxn,TxnSearch,
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
version_build = "1003"                                                                                              # noqa
myScriptName = "Toolbox.py(Extension)"                                                                              # noqa
debug = False                                                                                                       # noqa
myParameters = {}                                                                                                   # noqa
_resetParameters = False                                                                                            # noqa
lPickle_version_warning = False                                                                                     # noqa
lIamAMac = False                                                                                                    # noqa
lGlobalErrorDetected = False																						# noqa
# END SET THESE VARIABLES FOR ALL SCRIPTS ##############################################################################

# >>> THIS SCRIPT'S IMPORTS ############################################################################################
import re
import fnmatch
import subprocess

from com.moneydance.apps.md.view.gui import theme
from com.moneydance.apps.md.view.gui.theme import Theme
from com.moneydance.apps.md.view.gui.sync import SyncFolderUtil
from com.moneydance.apps.md.controller import ModuleMetaData
from com.moneydance.apps.md.controller import LocalStorageCipher
from com.moneydance.apps.md.controller import Common
from com.moneydance.apps.md.controller import BalanceType
from com.moneydance.apps.md.controller.io import FileUtils, AccountBookUtil
from com.moneydance.apps.md.controller import ModuleLoader
from java.awt import GraphicsEnvironment

from com.infinitekind.util import StreamTable, StreamVector, IOUtils, StringUtils, CustomDateFormat
from com.infinitekind.moneydance.model import ReportSpec, AddressBookEntry, OnlineService
from com.infinitekind.tiksync import SyncRecord

from java.awt.datatransfer import StringSelection
from java.net import URL
from java.nio.charset import Charset
# >>> END THIS SCRIPT'S IMPORTS ########################################################################################

# >>> THIS SCRIPT'S GLOBALS ############################################################################################
global __TOOLBOX
global Toolbox_frame_, _AREYOUSURE, fixRCurrencyCheck, DARK_GREEN, lCopyAllToClipBoard_TB, _COLWIDTHS, lGeekOutModeEnabled_TB
global lHackerMode, lIgnoreOutdatedExtensions_TB
_AREYOUSURE = False                                                                                                 # noqa
DARK_GREEN = Color(0, 192, 0)                                                                                       # noqa
lCopyAllToClipBoard_TB = False                                                                                      # noqa
lGeekOutModeEnabled_TB = False                                                                                      # noqa
lIgnoreOutdatedExtensions_TB = False                                                                                # noqa
lHackerMode = False                                                                                                 # noqa
_COLWIDTHS = ["bank", "cc", "invest", "security", "loan", "misc", "split","rec_credits","rec_debits","secdetail"]   # noqa
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
    global __TOOLBOX, lCopyAllToClipBoard_TB, lGeekOutModeEnabled_TB, lIgnoreOutdatedExtensions_TB

    myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )
    myPrint("DB", "Loading variables into memory...")

    if myParameters is None: myParameters = {}

    if myParameters.get("__TOOLBOX") is not None: __TOOLBOX = myParameters.get("__TOOLBOX")
    if myParameters.get("lCopyAllToClipBoard_TB") is not None: lCopyAllToClipBoard_TB = myParameters.get("lCopyAllToClipBoard_TB")
    if myParameters.get("lGeekOutModeEnabled_TB") is not None: lGeekOutModeEnabled_TB = myParameters.get("lGeekOutModeEnabled_TB")
    if myParameters.get("lIgnoreOutdatedExtensions_TB") is not None: lIgnoreOutdatedExtensions_TB = myParameters.get("lIgnoreOutdatedExtensions_TB")

    myPrint("DB","myParameters{} set into memory (as variables).....")

    return

# >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
def dump_StuWareSoftSystems_parameters_from_memory():
    global debug, myParameters, lPickle_version_warning, version_build

    # >>> THESE ARE THIS SCRIPT's PARAMETERS TO SAVE
    global __TOOLBOX, lCopyAllToClipBoard_TB, lGeekOutModeEnabled_TB, lIgnoreOutdatedExtensions_TB

    myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )

    # NOTE: Parameters were loaded earlier on... Preserve existing, and update any used ones...
    # (i.e. other StuWareSoftSystems programs might be sharing the same file)

    if myParameters is None: myParameters = {}

    myParameters["__TOOLBOX"] = version_build
    myParameters["lCopyAllToClipBoard_TB"] = lCopyAllToClipBoard_TB
    myParameters["lGeekOutModeEnabled_TB"] = lGeekOutModeEnabled_TB
    myParameters["lIgnoreOutdatedExtensions_TB"] = lIgnoreOutdatedExtensions_TB

    myPrint("DB","variables dumped from memory back into myParameters{}.....")

    return


get_StuWareSoftSystems_parameters_from_file()
myPrint("DB", "DEBUG IS ON..")
# END ALL CODE COPY HERE ###############################################################################################


class DetectAndChangeMacTabbingMode(AbstractAction):

    def __init__(self,statusLabel,lQuickCheckOnly):
        self.statusLabel = statusLabel
        self.lQuickCheckOnly = lQuickCheckOnly

    def actionPerformed(self, event):
        global Toolbox_frame_, debug

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

        if not Platform.isOSX():
            if self.lQuickCheckOnly: return True
            myPrint("B", "Change Mac Tabbing Mode - This can only be run on a Mac!")
            self.statusLabel.setText("Change Mac Tabbing Mode - This can only be run on a Mac!".ljust(800, " "))
            self.statusLabel.setForeground(Color.RED)
            myPopupInformationBox(Toolbox_frame_,"Change Mac Tabbing Mode - This can only be run on a Mac!", theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        if not Platform.isOSXVersionAtLeast("10.16"):
            if self.lQuickCheckOnly: return True
            myPrint("B", "Change Mac Tabbing Mode - You are not running Big Sur - no changes made!")
            self.statusLabel.setText(("Change Mac Tabbing Mode - You are not running Big Sur - no changes made!").ljust(800, " "))
            self.statusLabel.setForeground(Color.RED)
            myPopupInformationBox(Toolbox_frame_,"Change Mac Tabbing Mode - You are not running Big Sur - no changes made!", theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        if (moneydance.getBuild() > 1929 and moneydance.getBuild() < 2008):                                         # noqa
            myPrint("B", "Change Mac Tabbing Mode - You are running 2021.build %s - This version has problems with DUAL MONITORS\nPlease upgrade to at least 2021. build 2012:\nhttps://infinitekind.com/preview" %moneydance.getBuild())
            self.statusLabel.setText(("You are running 2021.build %s - This version has problems with DUAL MONITORS - Upgrade to at least 2021. build 2012: https://infinitekind.com/preview" %moneydance.getBuild()).ljust(800, " "))
            self.statusLabel.setForeground(Color.RED)
            myPopupInformationBox(None,"Change Mac Tabbing Mode - You are running 2021.build %s - This version has problems with DUAL MONITORS\nPlease upgrade to at least 2021 first! build 2012:\nhttps://infinitekind.com/preview" %moneydance.getBuild(),theMessageType=JOptionPane.ERROR_MESSAGE)
            return

        prefFile = os.path.join(System.getProperty("UserHome"), "Library/Preferences/.GlobalPreferences.plist")
        if not os.path.exists(prefFile):
            if self.lQuickCheckOnly: return True
            myPrint("B", "Change Mac Tabbing Mode - Sorry - For some reason I could not find: %s - no changes made!" %prefFile)
            self.statusLabel.setText(("Change Mac Tabbing Mode - Sorry - For some reason I could not find: %s - no changes made!" %prefFile).ljust(800, " "))
            self.statusLabel.setForeground(Color.RED)
            myPopupInformationBox(Toolbox_frame_,"Change Mac Tabbing Mode - Sorry - For some reason I could not find: %s - no changes made!" %prefFile,theMessageType=JOptionPane.ERROR_MESSAGE)
            return

        try:
            tabbingMode = subprocess.check_output("defaults read -g AppleWindowTabbingMode", shell=True)
        except:
            if self.lQuickCheckOnly: return True
            myPrint("B", "Change Mac Tabbing Mode - Sorry - error getting your Tabbing mode! - no changes made!")
            self.statusLabel.setText(("Change Mac Tabbing Mode - Sorry - error getting your Tabbing mode! - no changes made!").ljust(800, " "))
            self.statusLabel.setForeground(Color.RED)
            myPopupInformationBox(Toolbox_frame_,"Change Mac Tabbing Mode\nSorry - error getting your Tabbing mode!\nno changes made!",theMessageType=JOptionPane.ERROR_MESSAGE)
            dump_sys_error_to_md_console_and_errorlog()
            return

        tabbingMode=tabbingMode.strip().lower()
        if not (tabbingMode == "fullscreen" or tabbingMode == "manual" or tabbingMode == "always"):
            if self.lQuickCheckOnly: return True
            myPrint("B", "Change Mac Tabbing Mode - Sorry - I don't understand your tabbing mode: %s - no changes made!" %tabbingMode)
            self.statusLabel.setText(("Change Mac Tabbing Mode - Sorry - I don't understand your tabbing mode: %s - no changes made!" %tabbingMode).ljust(800, " "))
            self.statusLabel.setForeground(Color.RED)
            myPopupInformationBox(Toolbox_frame_,"Change Mac Tabbing Mode - Sorry - I don't understand your tabbing mode:\n%s - no changes made!" %tabbingMode, theMessageType=JOptionPane.ERROR_MESSAGE)
            return

        if tabbingMode == "fullscreen" or tabbingMode == "manual":
            if self.lQuickCheckOnly:
                myPrint("J","Quick check of MacOS tabbing showed it's OK and set to: %s" %tabbingMode)
                return True
            myPrint("B", "\n@@@ Change Mac Tabbing Mode - NO PROBLEM FOUND - Your tabbing mode is: %s - no changes made!" %tabbingMode)
            self.statusLabel.setText(("Change Mac Tabbing Mode - NO PROBLEM FOUND - Your tabbing mode is: %s - no changes made!" %tabbingMode).ljust(800, " "))
            self.statusLabel.setForeground(Color.BLUE)
            myPopupInformationBox(Toolbox_frame_,"Change Mac Tabbing Mode - NO PROBLEM FOUND - Your tabbing mode is: %s - no changes made!" %tabbingMode)
            return

        if self.lQuickCheckOnly:
            myPrint("J","Quick check of MacOS tabbing showed it's NEEDS CHANGING >> It's set to: %s" %tabbingMode)
            return False

        myPrint("B","More information here: https://support.apple.com/en-gb/guide/mac-help/mchla4695cce/mac")

        myPrint("B", "@@@ PROBLEM - Your Tabbing Mode is set to: %s - NEEDS CHANGING" %tabbingMode)
        myPopupInformationBox(None,"@@@ PROBLEM - Your Tabbing Mode is set to: %s\nTHIS NEEDS CHANGING!" %tabbingMode,theMessageType=JOptionPane.ERROR_MESSAGE)
        myPopupInformationBox(None,"Info:\n<https://support.apple.com/en-gb/guide/mac-help/mchla4695cce/mac>\nPress OK to select new mode...",theMessageType=JOptionPane.ERROR_MESSAGE)

        mode_options = ["fullscreen", "manual"]
        selectedMode = JOptionPane.showInputDialog(Toolbox_frame_,
                                                    "TABBING MODE", "Select the new Tabbing Mode?",
                                                    JOptionPane.WARNING_MESSAGE,
                                                    moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                    mode_options,
                                                    None)
        if selectedMode is None:
            self.statusLabel.setText("Change Mac Tabbing Mode - No new Tabbing Mode was selected - aborting..".ljust(800, " "))
            self.statusLabel.setForeground(Color.RED)
            myPopupInformationBox(Toolbox_frame_,"Change Mac Tabbing Mode - No new Tabbing Mode was selected - aborting..")
            return

        disclaimer = myPopupAskForInput(Toolbox_frame_,
                                        "TABBING MODE",
                                        "DISCLAIMER:",
                                        "Are you really sure you want to change MacOS system setting>>Tabbing Mode? Type 'IAGREE' to continue..",
                                        "NO",
                                        False,
                                        JOptionPane.ERROR_MESSAGE)

        if not disclaimer == 'IAGREE':
            self.statusLabel.setText("Change Mac Tabbing Mode - User declined the disclaimer - no changes made....".ljust(800, " "))
            self.statusLabel.setForeground(Color.RED)
            return

        try:
            tabbingModeChanged = subprocess.check_output('defaults write -g AppleWindowTabbingMode -string "%s"' %selectedMode, shell=True)
            if tabbingModeChanged.strip() != "":
                myPrint("B", "Tabbing mode change output>>>>")
                myPrint("B", tabbingModeChanged)
            myPrint("B","!!! Your tabbing mode has been changed to %s - Please exit and restart Moneydance" %selectedMode)
        except:
            myPrint("B", "Change Mac Tabbing Mode - Sorry - error setting your Tabbing mode! - no changes made!")
            self.statusLabel.setText((")").ljust(800, " "))
            self.statusLabel.setForeground(Color.RED)
            myPopupInformationBox(Toolbox_frame_,"Change Mac Tabbing Mode\nSorry - error getting your Tabbing mode! - no changes made!", theMessageType=JOptionPane.ERROR_MESSAGE)
            dump_sys_error_to_md_console_and_errorlog()
            return

        if tabbingModeChanged.strip() != "":
            myPopupInformationBox(Toolbox_frame_,"Change Mac Tabbing Mode: Response: %s" %tabbingModeChanged, JOptionPane.WARNING_MESSAGE)

        myPopupInformationBox(None,"OK I Made the Change to your Mac Tabbing Mode: Please exit and restart Moneydance...",theMessageType=JOptionPane.WARNING_MESSAGE)
        self.statusLabel.setText(("MacOS Tabbing Mode: OK I Made the Change to your Mac Tabbing Mode: Please exit and restart Moneydance...").ljust(800, " "))
        self.statusLabel.setForeground(Color.RED)

        return

# noinspection PyBroadException
def buildDiagText(lGrabPasswords=False):
    if lGrabPasswords:
        returnString = ""

        MD_enc = moneydance_ui.getCurrentAccounts().getEncryptionKey()
        MD_hnt = moneydance_ui.getCurrentAccounts().getEncryptionHint()
        MD_sync_pwd = moneydance_ui.getCurrentAccounts().getSyncEncryptionPassword()

        if MD_enc is not None and MD_enc != "":
            returnString += "MD Encryption Passphrase: " + MD_enc
            if MD_hnt is not None and MD_hnt != "":
                returnString += "   Encryption Passphrase Hint: " + MD_hnt

        if MD_sync_pwd is not None and MD_sync_pwd != "":
            returnString += "  MD Sync Passphrase: " + MD_sync_pwd

        if returnString.strip() == "":
            returnString = " - NO PASSPHRASE(S) FOUND - "

        return returnString


    textArray = []                                                                                                  # noqa

    textArray.append("MoneyDance Version / Build: " + str(moneydance.getVersion()) + "  Build: " + str(moneydance.getBuild()))
    textArray.append("MoneyDance Config file reports: " + moneydance_ui.getPreferences().getSetting("current_version", ""))
    textArray.append("MoneyDance updater version to track: " + moneydance_ui.getPreferences().getSetting("updater.version_to_track",""))

    currLicense = moneydance_ui.getPreferences().getSetting("gen.lic_key2021",
                                                            moneydance_ui.getPreferences().getSetting("gen.lic_key2019",
                                                                                                      moneydance_ui.getPreferences().getSetting(
                                                                                                          "gen.lic_key2017",
                                                                                                          moneydance_ui.getPreferences().getSetting(
                                                                                                              "gen.lic_key2015",
                                                                                                              moneydance_ui.getPreferences().getSetting(
                                                                                                                  "gen.lic_key2014",
                                                                                                                  moneydance_ui.getPreferences().getSetting(
                                                                                                                      "gen.lic_key2011",
                                                                                                                      moneydance_ui.getPreferences().getSetting(
                                                                                                                          "gen.lic_key2010",
                                                                                                                          moneydance_ui.getPreferences().getSetting(
                                                                                                                              "gen.lic_key2004",
                                                                                                                              moneydance_ui.getPreferences().getSetting(
                                                                                                                                  "gen.lic_key",
                                                                                                                                  "?")))))))))

    license2021 = moneydance_ui.getPreferences().getSetting("gen.lic_key2021", None)                                # noqa
    license2019 = moneydance_ui.getPreferences().getSetting("gen.lic_key2019", None)
    license2017 = moneydance_ui.getPreferences().getSetting("gen.lic_key2017", None)
    license2015 = moneydance_ui.getPreferences().getSetting("gen.lic_key2015", None)
    license2014 = moneydance_ui.getPreferences().getSetting("gen.lic_key2014", None)
    license2011 = moneydance_ui.getPreferences().getSetting("gen.lic_key2011", None)
    license2010 = moneydance_ui.getPreferences().getSetting("gen.lic_key2010", None)
    license2004 = moneydance_ui.getPreferences().getSetting("gen.lic_key2004", None)

    if moneydance_ui.getMain().isRegistered():
        textArray.append("LICENSED: " + currLicense)
    else:
        textArray.append("UNLICENSED!")

    if license2019:      textArray.append(" >old licenses (2019): " + license2019)
    if license2017:      textArray.append(" >old licenses (2017): " + license2017)
    if license2015:      textArray.append(" >old licenses (2015): " + license2015)
    if license2014:      textArray.append(" >old licenses (2014): " + license2014)
    if license2011:      textArray.append(" >old licenses (2011): " + license2011)
    if license2010:      textArray.append(" >old licenses (2010): " + license2010)
    if license2004:      textArray.append(" >old licenses (2004): " + license2004)

    if not moneydance_data: textArray.append("Moneydance datafile is empty")
    x = moneydance_ui.getPreferences().getSetting("current_accountbook", None)
    y = moneydance_ui.getPreferences().getSetting("current_account_file", None)

    theExtn = os.path.splitext(str(moneydance_data.getRootFolder()))

    if x:
        textArray.append("Current Dataset: " + str(x))
    if y:
        textArray.append("Current Dataset: " + str(y))

    textArray.append("Full location of this Dataset: %s" %(moneydance_data.getRootFolder()))

    x = find_the_program_install_dir()
    if x:
        textArray.append("Application Install Directory: %s" %(x))
    else:
        textArray.append("UNABLE TO DETERMINE Application's Install Directory?!")

    textArray.append("\nRUNTIME ENVIRONMENT")

    textArray.append("Java version: " + str(System.getProperty("java.version")))
    textArray.append("Java vendor: " + str(System.getProperty("java.vendor")))

    textArray.append("Platform: " + platform.python_implementation()
                     + " " + platform.system() + " " + str(sys.version_info.major)
                     + "" + "." + str(sys.version_info.minor))

    textArray.append("SandBoxed: " + repr(moneydance.getPlatformHelper().isSandboxed()))
    textArray.append("Restricted: " + repr(moneydance.getPlatformHelper().isConstrainedToSandbox()))

    if moneydance.getExecutionMode() == moneydance.EXEC_MODE_APP:
        textArray.append("MD Execution Mode: " + str(moneydance.getExecutionMode()) + " = APP (Normal App)")
    elif moneydance.getExecutionMode() == moneydance.EXEC_MODE_APPLET:
        textArray.append("MD Execution Mode: " + str(moneydance.getExecutionMode()) + " = APPLET (probably from an AppStore?")
    else:
        textArray.append("MD Execution Mode: " + str(moneydance.getExecutionMode()))

    textArray.append("MD Debug Mode: " + repr(moneydance.DEBUG))
    textArray.append("Beta Features: " + repr(moneydance.BETA_FEATURES))
    textArray.append("Architecture: " + str(System.getProperty("os.arch")))

    if theExtn and theExtn[1].strip() != "":
        textArray.append("File Extension: " + theExtn[1])
    else:
        textArray.append("File Extension: " + str(moneydance.FILE_EXTENSION))

    textArray.append("Operating System file encoding is: " + str(Charset.defaultCharset()))
    textArray.append(
        "Python default character encoding has been set to: " + sys.getfilesystemencoding() + " (the normal default is ASCII)")


    try:
        # New for MD2020.2012
        x = moneydance_ui.getFonts().code
    except:
        myPrint("B","Failed to get Moneydance code font (must be older version), loading older mono")
        x = moneydance_ui.getFonts().mono

    textArray.append("Python default display font: " + x.getFontName() + " size: " + str(x.getSize()))

    textArray.append(
        "\nMaster Node (dataset): " + str(moneydance_data.getLocalStorage().getBoolean("_is_master_node", True)))

    textArray.append("\nENCRYPTION")
    x = moneydance_ui.getCurrentAccounts().getEncryptionKey()
    if x is None or x == "":
        x = "Encryption not set! - This means an internal Moneydance passphrase is being used to encrypt your dataset!"
    else:
        x = "***************"
    textArray.append("Encryption Passphrase: " + x)

    x = moneydance_ui.getCurrentAccounts().getEncryptionHint()
    if x is None or x == "":
        x = "Encryption passphrase hint not set!"
    else:
        x = "***************"
    textArray.append("Encryption passphrase hint: " + x)

    # if moneydance_ui.getCurrentAccounts().getEncryptionLevel(): # Always reports des - is this legacy?
    if moneydance.getRootAccount().getParameter("md.crypto_level", None):
        x = "Encryption level - Moneydance reports: %s (but I believe this is a legacy encryption method??)" %moneydance_ui.getCurrentAccounts().getEncryptionLevel()
        textArray.append(x)
    else:
        x = "My Encryption 'test' of your key/passphrase reports: %s\n"%getMDEncryptionKey()
        x += "I understand the dataset encryption is: AES 128-bit. Passphrase encrypted using PBKDF2WithHmacSHA512 (fixed internal salt, high iteration) and then your (secure/random) key is encrypted and used to encrypt data to disk using AES/CBC/PKCS5Padding with a fixed internal IV"
        textArray.append(x)
    textArray.append("Encryption store online banking (OFX) passwords: " + str(moneydance_ui.getCurrentAccounts().getBook().getLocalStorage().getBoolean("store_passwords", False)))

    textArray.append("\nSYNC DETAILS")
    # SYNC details
    x = moneydance_ui.getCurrentAccounts().getSyncEncryptionPassword()
    if x is None or x == "":
        x = "Sync passphrase not set!"
    else:
        x = "***************"
    textArray.append("Sync Password: " + x)

    syncMethods = SyncFolderUtil.getAvailableFolderConfigurers(moneydance_ui, moneydance_ui.getCurrentAccounts())
    noSyncOption = SyncFolderUtil.configurerForIDFromList("none", syncMethods)
    syncMethod = SyncFolderUtil.getConfigurerForFile(moneydance_ui, moneydance_ui.getCurrentAccounts(), syncMethods)
    if syncMethod is None:
        syncMethod = noSyncOption
    else:
        syncMethod = syncMethod
    textArray.append("Sync Method: " + str(syncMethod.getSyncFolder()))

    textArray.append("\nTHEMES")
    textArray.append("Your selected Theme: " + str(
        moneydance_ui.getPreferences().getSetting("gui.current_theme", Theme.DEFAULT_THEME_ID)))
    # noinspection PyUnresolvedReferences
    x = theme.Theme.customThemeFile
    if not os.path.exists(str(x)):
        x = " custom_theme.properties file DOES NOT EXIST!"
    textArray.append("Custom Theme File: " + str(x))
    # noinspection PyUnresolvedReferences
    textArray.append("Available themes: " + str(theme.Theme.getAllThemes()))

    textArray.append("\nENVIRONMENT")

    try:
        username = System.getProperty("user.name")
    except:
        username = "???"
    textArray.append("Username:" + username)

    textArray.append(
        "OS Platform:" + System.getProperty("os.name") + "OS Version:" + str(System.getProperty("os.version")))

    textArray.append("Home Directory: " + get_home_dir())

    if System.getProperty("user.dir"): textArray.append("  user.dir:" + System.getProperty("user.dir"))
    if System.getProperty("UserHome"): textArray.append("  UserHome:" + System.getProperty("UserHome"))
    if os.path.expanduser("~"): textArray.append("  ~:" + os.path.expanduser("~"))
    if os.environ.get("HOMEPATH"): textArray.append("  HOMEPATH:" + os.environ.get("HOMEPATH"))

    textArray.append("Moneydance decimal point: " + moneydance_ui.getPreferences().getSetting("decimal_character", "."))
    textArray.append(
        "System Locale Decimal Point: " + getDecimalPoint(lGetPoint=True) + " Grouping Char: " + getDecimalPoint(
            lGetGrouping=True))
    if moneydance_ui.getPreferences().getSetting("decimal_character", ".") != getDecimalPoint(lGetPoint=True):
        textArray.append("NOTE - MD Decimal point is DIFFERENT to the Locale decimal point!!!")
    textArray.append("Locale Country: " + str(moneydance_ui.getPreferences().getSetting("locale.country", "")))
    textArray.append("Locale Language: " + str(moneydance_ui.getPreferences().getSetting("locale.language", "")))

    textArray.append("\nFOLDER / FILE LOCATIONS")

    textArray.append("moneydance_data Dataset internal top level (root) Directory: " + str(moneydance_data.getRootFolder().getParent()))
    textArray.append("Auto Backup Folder: " + str(moneydance_ui.getPreferences().getSetting("backup.location",
                                                                                            FileUtils.getDefaultBackupDir().getAbsolutePath())))
    textArray.append(
        "(Last backup location: " + str(moneydance_ui.getPreferences().getSetting("backup.last_saved", "")) + ")")

    internalFiles = AccountBookUtil.getInternalAccountBooks()
    externalFiles = AccountBookUtil.getExternalAccountBooks()

    if internalFiles.size() + externalFiles.size() > 1:
        textArray.append("\nOther MD Datasets I am aware of...:")

    for wrapper in internalFiles:
        if moneydance_ui.getCurrentAccounts() is not None and moneydance_ui.getCurrentAccounts().getBook() == wrapper.getBook():
            pass
        else:
            textArray.append("Internal file: " + str(wrapper.getBook().getRootFolder()))

    for wrapper in externalFiles:
        if (
                moneydance_ui.getCurrentAccounts() is not None and moneydance_ui.getCurrentAccounts().getBook() == wrapper.getBook()):
            pass
        else:
            textArray.append("External file: " + str(wrapper.getBook().getRootFolder()))

    if internalFiles.size() + externalFiles.size() > 1:
        textArray.append("\n")

    textArray.append("MD System Root Directory: " + repr(Common.getRootDirectory()))

    textArray.append("MD Log file: " + repr(moneydance.getLogFile()))
    textArray.append("Preferences File: " + repr(Common.getPreferencesFile()))

    if os.path.exists(str(Common.getArchiveDirectory())):         textArray.append(
        "Archive Directory: " + repr(Common.getArchiveDirectory()))
    if os.path.exists(str(Common.getFeatureModulesDirectory())):  textArray.append(
        "Extensions Directory: " + repr(Common.getFeatureModulesDirectory()))
    if os.path.exists(str(Common.getCertificateDirectory())):     textArray.append(
        "Certificates Directory: " + repr(Common.getCertificateDirectory()))
    if os.path.exists(str(Common.getDocumentsDirectory())):       textArray.append(
        "Documents Directory: " + repr(Common.getDocumentsDirectory()))

    if getTheSetting("gen.report_dir"):
        textArray.append(getTheSetting("gen.report_dir"))
    if getTheSetting("gen.data_dir"):
        textArray.append(getTheSetting("gen.data_dir"))
    if getTheSetting("gen.import_dir"):
        textArray.append(getTheSetting("gen.import_dir"))

    textArray.append("\n")
    if os.path.exists(str(Common.getPythonDirectory())):          textArray.append(
        "Python Directory: " + repr(Common.getPythonDirectory()))
    if getTheSetting("gen.last_ext_file_dir"):
        textArray.append(getTheSetting("gen.last_ext_file_dir"))
    if getTheSetting("gen.python_default_file"):
        textArray.append(getTheSetting("gen.python_default_file"))
    if getTheSetting("gen.python_dir"):
        textArray.append(getTheSetting("gen.python_dir"))
    if getTheSetting("gen.graph_dir"):
        textArray.append(getTheSetting("gen.graph_dir"))
    if getTheSetting("gen.recent_files"):
        textArray.append(getTheSetting("gen.recent_files"))

    textArray.append("System 'python.path': " + System.getProperty("python.path"))
    textArray.append("System 'python.cachedir': " + System.getProperty("python.cachedir"))
    textArray.append("System 'python.cachedir.skip': " + System.getProperty("python.cachedir.skip"))

    try:
        textArray.append("\nEXTENSIONS / EDITORS / VIEWS")

        textArray.append("Extensions enabled: %s" %moneydance_ui.getMain().getSourceInformation().getExtensionsEnabled())

        x = moneydance.getExternalAccountEditors()
        for y in x:
            textArray.append("External Account Editor: " + str(y))
        x = moneydance.getExternalViews()
        for y in x:
            textArray.append("External View(er): " + str(y))
        x = moneydance.getLoadedModules()
        for y in x:
            textArray.append("Extension Loaded: " + str(y.getDisplayName()))
        x = moneydance.getSuppressedExtensionIDs()
        for y in x:
            textArray.append("Internal/suppressed/secret extensions: " + str(y))
        x = moneydance.getOutdatedExtensionIDs()
        for y in x:
            textArray.append("Outdated extensions (not loaded): " + str(y))

        try:
            theUpdateList = get_extension_update_info()

            for key in theUpdateList.keys():
                updateInfo = theUpdateList[key]
                textArray.append("** UPDATABLE EXTENSION: %s to version: %s" %(pad(key,20),str(updateInfo[0].getBuild())) )
        except:
            textArray.append("ERROR: Failed to retrieve / download Extension update list....")
            dump_sys_error_to_md_console_and_errorlog()

    except:
        pass

    orphan_prefs, orphan_files, orphan_confirmed_extn_keys = get_orphaned_extension()

    if len(orphan_prefs)<1 and len(orphan_files)<1 and len(orphan_confirmed_extn_keys)<1:
        textArray.append("\nCONGRATULATIONS - NO ORPHAN EXTENSIONS DETECTED!!\n")
    else:
        textArray.append("\nWARNING: Orphan Extensions detected (%s in config.dict) & (%s in .MXT files)\n" %(len(orphan_prefs)+len(orphan_confirmed_extn_keys),len(orphan_files)))
        myPrint("B", "WARNING: Orphan Extensions detected (%s in config.dict) & (%s in .MXT files)\n" %(len(orphan_prefs)+len(orphan_confirmed_extn_keys),len(orphan_files)))

    textArray.append("\n ======================================================================================")
    textArray.append("USER PREFERENCES")
    textArray.append("-----------------")
    textArray.append(">> GENERAL")
    textArray.append("Show Full Account Paths: " + str(
        moneydance_ui.getPreferences().getBoolSetting("show_full_account_path", True)))
    textArray.append("Register Follows Recorded Txns: " + str(
        moneydance_ui.getPreferences().getBoolSetting("gui.register_follows_txns", True)))
    textArray.append("Use VAT/GST: " + str(moneydance_ui.getPreferences().getBoolSetting("gen.use_vat", False)))
    textArray.append("Case Sensitive Auto-Complete: " + str(
        moneydance_ui.getPreferences().getBoolSetting("gen.case_sensitive_ac", False)))
    textArray.append(
        "Auto Insert Decimal Points: " + str(moneydance_ui.getPreferences().getBoolSetting("gui.quickdecimal", False)))
    textArray.append("Auto Create New Transactions: " + str(
        moneydance_ui.getPreferences().getBoolSetting("gui.new_txn_on_record", True)))
    textArray.append("Separate Tax Date for Transactions: " + str(
        moneydance_ui.getPreferences().getBoolSetting("gen.separate_tax_date", False)))
    textArray.append("Show All Accounts in Popup: " + str(
        moneydance_ui.getPreferences().getBoolSetting("gui.show_all_accts_in_popup", False)))
    textArray.append("Beep when Transactions Change: " + str(
        moneydance_ui.getPreferences().getBoolSetting("beep_on_transaction_change", True)))
    textArray.append(
        "Theme: " + str(moneydance_ui.getPreferences().getSetting("gui.current_theme", Theme.DEFAULT_THEME_ID)))
    textArray.append(
        "Show Selection Details: " + str(moneydance_ui.getPreferences().getSetting("details_view_mode", "inwindow")))
    textArray.append("Side Bar Balance Type: " + str(moneydance_ui.getPreferences().getSideBarBalanceType()))
    textArray.append("Date Format: " + str(moneydance_ui.getPreferences().getSetting("date_format", None)))
    # this.prefs.getShortDateFormat());
    textArray.append("Decimal Character: " + str(moneydance_ui.getPreferences().getSetting("decimal_character", ".")))
    # this.prefs.getDecimalChar()));
    textArray.append("Locale: " + str(moneydance_ui.getPreferences().getLocale()))

    i = moneydance_ui.getPreferences().getIntSetting("gen.fiscal_year_start_mmdd", 101)
    if i == 101: i = "January 1"
    elif i == 201: i = "February 1"
    elif i == 301: i = "March 1"
    elif i == 401: i = "April 1"
    elif i == 406: i = "April 6 (UK Tax Year Start Date)"
    elif i == 501: i = "May 1"
    elif i == 601: i = "June 1"
    elif i == 701: i = "July 1"
    elif i == 801: i = "August 1"
    elif i == 901: i = "September 1"
    elif i == 1001: i = "October 1"
    elif i == 1101: i = "November 1"
    elif i == 1201: i = "December 1"
    else: i = i
    textArray.append("Fiscal Year Start: " + str(i))
    textArray.append("Font Size: +" + str(moneydance_ui.getPreferences().getIntSetting("gui.font_increment", 0)))

    textArray.append("\n>> NETWORK")
    textArray.append("Automatically Download in Background: " + str(
        moneydance_ui.getPreferences().getBoolSetting("net.auto_download", False)))
    textArray.append("Automatically Merge Downloaded Transactions: " + str(
        moneydance_ui.getPreferences().getBoolSetting("gen.preprocess_dwnlds", False)))
    textArray.append("Mark Transactions as Cleared When Confirmed: " + str(
        moneydance_ui.getPreferences().getBoolSetting("net.clear_confirmed_txns", False)))
    textArray.append("Use Bank Dates for Merged Transactions: " + str(
        moneydance_ui.getPreferences().getBoolSetting("olb.prefer_bank_dates", False)))
    textArray.append("Ignore Transaction Types in Favor of Amount Signs: " + str(
        moneydance_ui.getPreferences().getBoolSetting("prefer_amt_sign_to_txn_type", False)))

    dataStorage = moneydance_data.getLocalStorage()
    autocommit = not dataStorage or dataStorage.getBoolean("do_autocommits",moneydance_ui.getCurrentAccounts().isMasterSyncNode())
    textArray.append("Auto-Commit Reminders (applies to current file on this computer): " + str(autocommit))

    textArray.append("Use Proxy: " + str(moneydance_ui.getPreferences().getBoolSetting("net.use_proxy", False)))
    textArray.append(" Proxy Host: " + str(moneydance_ui.getPreferences().getSetting("net.proxy_host", "")))
    textArray.append(" Proxy Port: " + str(moneydance_ui.getPreferences().getIntSetting("net.proxy_port", 80)))
    textArray.append(
        "Proxy Requires Authentication: " + str(moneydance_ui.getPreferences().getBoolSetting("net.auth_proxy", False)))
    textArray.append(" Proxy Username: " + str(moneydance_ui.getPreferences().getSetting("net.proxy_user", "")))
    textArray.append(" Proxy Password: " + str(moneydance_ui.getPreferences().getSetting("net.proxy_pass", "")))
    textArray.append("Observe Online Payment Date Restrictions: " + str(
        moneydance_ui.getPreferences().getBoolSetting("ofx.observe_bp_window", True)))
    i = moneydance_ui.getPreferences().getIntSetting("net.downloaded_txn_date_window", -1)
    if i < 0: i = "Default"
    textArray.append("Only Match downloaded transactions when they are at most " + str(i) + " days apart")

    textArray.append("\n>> CHEQUE PRINTING")
    textArray.append("preferences not listed here...")

    textArray.append("\n>> PRINTING")
    textArray.append("Font: " + str(moneydance_ui.getPreferences().getSetting("print.font_name", "")))
    textArray.append("Font Size: " + str(moneydance_ui.getPreferences().getSetting("print.font_size", "12")))

    textArray.append("\n>> BACKUPS")

    destroyBackupChoices = moneydance_ui.getPreferences().getSetting("backup.destroy_number", "5")
    returnedBackupType = moneydance_ui.getPreferences().getSetting("backup.backup_type", "every_x_days")
    if returnedBackupType == "every_time":
        dailyBackupCheckbox = True
        destroyBackupChoices = 1
    elif returnedBackupType == "every_x_days":
        dailyBackupCheckbox = True
    else:
        dailyBackupCheckbox = False

    textArray.append("Save Backups Daily: " + str(dailyBackupCheckbox))
    textArray.append("Keep no more than " + str(destroyBackupChoices) + " backups")

    textArray.append("separate Backup Folder: " + str(
        moneydance_ui.getPreferences().getBoolSetting("backup.location_selected", True)))
    textArray.append("Backup Folder: " + str(moneydance_ui.getPreferences().getSetting("backup.location",
                                                                                       FileUtils.getDefaultBackupDir().getAbsolutePath())))

    textArray.append("\n>> SUMMARY PAGE")
    textArray.append("preferences not listed here...")
    textArray.append(" ======================================================================================\n")

    textArray.append("\nHOME SCREEN USER SELECTED PREFERENCES")
    textArray.append("----------------------------")
    textArray.append("Home Screen Configured: %s" %moneydance_ui.getPreferences().getSetting("gui.home.configured", "NOT SET"))

    if moneydance_ui.getPreferences().getSetting("sidebar_bal_type", False):
        textArray.append("Side Bar Balance Type: %s" %(BalanceType.fromInt(moneydance_ui.getPreferences().getIntSetting("sidebar_bal_type",0))))

    textArray.append("Dashboard Item Selected: %s" %moneydance_ui.getPreferences().getSetting("gui.dashboard.item", "NOT SET"))

    textArray.append("Quick Graph Selected: %s" %moneydance_ui.getPreferences().getSetting("gui.quick_graph_type", "NOT SET"))

    textArray.append("Budget Bar Date Range Selected: %s" %moneydance_ui.getPreferences().getSetting("budgetbars_date_range", "NOT SET"))


    textArray.append("Reminders View: %s" %moneydance_ui.getPreferences().getSetting("upcoming_setting", "NOT SET"))

    textArray.append("Exchange Rates View - Invert?: %s" %moneydance_ui.getPreferences().getSetting("gui.home.invert_rates", "NOT SET"))

    textArray.append("BANK Accounts Expanded: %s" %moneydance_ui.getPreferences().getSetting("gui.home.bank_expanded", "NOT SET"))
    if moneydance_ui.getPreferences().getSetting("gui.home.bank_bal_type", False):
        textArray.append(">Balance Displayed: %s" %(BalanceType.fromInt(moneydance_ui.getPreferences().getIntSetting("gui.home.bank_bal_type",0))))

    textArray.append("LOAN Accounts Expanded: %s" %moneydance_ui.getPreferences().getSetting("gui.home.loan_expanded", "NOT SET"))
    if moneydance_ui.getPreferences().getSetting("gui.home.loan_bal_type", False):
        textArray.append(">Balance Displayed: %s" %(BalanceType.fromInt(moneydance_ui.getPreferences().getIntSetting("gui.home.loan_bal_type",0))))

    textArray.append("LIABILITY Accounts Expanded: %s" %moneydance_ui.getPreferences().getSetting("gui.home.liability_expanded", "NOT SET"))
    if moneydance_ui.getPreferences().getSetting("gui.home.liability_bal_type", False):
        textArray.append(">Balance Displayed: %s" %(BalanceType.fromInt(moneydance_ui.getPreferences().getIntSetting("gui.home.liability_bal_type",0))))

    textArray.append("INVESTMENT Accounts Expanded: %s" %moneydance_ui.getPreferences().getSetting("gui.home.invst_expanded", "NOT SET"))
    if moneydance_ui.getPreferences().getSetting("gui.home.invst_bal_type", False):
        textArray.append(">Balance Displayed: %s" %(BalanceType.fromInt(moneydance_ui.getPreferences().getIntSetting("gui.home.invst_bal_type",0))))

    textArray.append("CREDIT CARD Accounts Expanded: %s" %moneydance_ui.getPreferences().getSetting("gui.home.cc_expanded", "NOT SET"))
    if moneydance_ui.getPreferences().getSetting("gui.home.cc_bal_type", False):
        textArray.append(">Balance Displayed: %s" %(BalanceType.fromInt(moneydance_ui.getPreferences().getIntSetting("gui.home.cc_bal_type",0))))

    textArray.append("ASSET Accounts Expanded: %s" %moneydance_ui.getPreferences().getSetting("gui.home.asset_expanded", "NOT SET"))
    if moneydance_ui.getPreferences().getSetting("gui.home.asset_bal_type", False):
        textArray.append(">Balance Displayed: %s" %(BalanceType.fromInt(moneydance_ui.getPreferences().getIntSetting("gui.home.asset_bal_type",0))))


    textArray.append(" ======================================================================================\n")

    try:
        textArray.append("\nFONTS")
        textArray.append(">> Swing Manager default: " + str(UIManager.getFont("Label.font")))
        textArray.append(">> Moneydance default: " + str(moneydance_ui.getFonts().defaultSystemFont))
        textArray.append(">> Moneydance mono: " + str(moneydance_ui.getFonts().mono))
        textArray.append(">> Moneydance default text: " + str(moneydance_ui.getFonts().defaultText))
        textArray.append(">> Moneydance default title: " + str(moneydance_ui.getFonts().detailTitle))
        textArray.append(">> Moneydance calendar title: " + str(moneydance_ui.getFonts().calendarTitle))
        textArray.append(">> Moneydance header: " + str(moneydance_ui.getFonts().header))
        textArray.append(">> Moneydance register: " + str(moneydance_ui.getFonts().register))
        textArray.append(">> Moneydance report header: " + str(moneydance_ui.getFonts().reportHeader))
        textArray.append(">> Moneydance report title: " + str(moneydance_ui.getFonts().reportTitle))

        try:
            textArray.append(">> Moneydance code: " + str(moneydance_ui.getFonts().code))
        except:
            pass

    except:
        myPrint("B","Error getting fonts..?")
        dump_sys_error_to_md_console_and_errorlog()

    textArray.append("\n>> OTHER INTERESTING SETTINGS....")

    if getTheSetting("net.default_browser"):
        textArray.append(getTheSetting("net.default_browser"))
    if getTheSetting("gen.import_dt_fmt_idx"):
        textArray.append(getTheSetting("gen.import_dt_fmt_idx"))
    if getTheSetting("txtimport_datefmt"):
        textArray.append(getTheSetting("txtimport_datefmt"))
    if getTheSetting("txtimport_csv_delim"):
        textArray.append(getTheSetting("txtimport_csv_delim"))
    if getTheSetting("txtimport_csv_decpoint"):
        textArray.append(getTheSetting("txtimport_csv_decpoint"))

    textArray.append("")

    if getTheSetting("ofx.app_id"):
        textArray.append(getTheSetting("ofx.app_id"))
    if getTheSetting("ofx.app_version"):
        textArray.append(getTheSetting("ofx.app_version"))
    if getTheSetting("ofx.bp_country"):
        textArray.append(getTheSetting("ofx.bp_country"))
    if getTheSetting("ofx.app_version"):
        textArray.append(getTheSetting("ofx.app_version"))


    textArray.append("")
    textArray.append("System Properties containing references to Moneydance")
    for x in System.getProperties():

        # noinspection PyUnresolvedReferences
        if "moneydance" in System.getProperty(x).lower():
            textArray.append(">> %s:\t%s" %(x, System.getProperty(x)))

    textArray.append("\n\n<END>\n")

    for i in range(0, len(textArray)):
        textArray[i] = textArray[i] + "\n"

    return "".join(textArray)

def get_list_memorised_reports():
    # Build a quick virtual file of Memorized reports and graphs to display
    memz = []

    iCount = 0
    for x in moneydance_data.getMemorizedItems().getMemorizedGraphs():
        iCount+=1
        memz.append("Graph: %s" % (x.getName()))

    for x in moneydance_data.getMemorizedItems().getMemorizedReports():
        iCount+=1
        memz.append("Report: %s" % (x.getName()))

    memz = sorted(memz, key=lambda sort_x: (str(sort_x[0]).upper()))

    memz.insert(0,"YOUR MEMORIZED REPORTS\n ======================\n")

    memz.append("\nYOUR MEMORIZED REPORTS in detail\n ======================\n")

    iGs = 0
    for x in moneydance_data.getMemorizedItems().getMemorizedGraphs():
        if iGs:
            memz.append("\n ---")
        iGs+=1
        memz.append("Graph:           %s" % (x.getName()))
        memz.append(">> SyncItemType: %s" %(x.getSyncItemType()))
        # memz.append(">> Graph ID:     %s" %(x.getReportID()))
        memz.append(">> Graph Genr:   %s" %(x.getReportGenerator()))
        y = x.getReportParameters()
        for yy in y:
            if yy.lower().strip() == "accounts" or yy.lower().strip() == "source_accts":
                memz.append(">> Parameter key: %s: %s" %(yy, "<not displayed - but contains %s accounts>" %(y.get(yy).count(",")+1)))
            else:
                memz.append(">> Parameter key: %s: %s" %(yy, y.get(yy)))

    iRs = 0
    for x in moneydance_data.getMemorizedItems().getMemorizedReports():
        if iRs or iGs:
            memz.append("\n ---")
        iRs+=1
        memz.append("Report           %s" % (x.getName()))
        memz.append(">> SyncItemType: %s" %(x.getSyncItemType()))
        # memz.append(">> Report ID:    %s" %(x.getReportID()))
        memz.append(">> Report Genr:  %s" %(x.getReportGenerator()))
        y = x.getReportParameters()
        for yy in y:
            if yy.lower().strip() == "accounts" or yy.lower().strip() == "source_accts":
                memz.append(">> Parameter key: %s: %s" %(yy, "<not displayed - but contains %s accounts>" %(y.get(yy).count(",")+1)))
            else:
                memz.append(">> Parameter key: %s: %s" %(yy, y.get(yy)))

    memz.append("\n\n\n====== DEFAULT REPORTS SETTINGS/PARAMETERS (from Local Storage) RAW DUMP ======\n")
    LS = moneydance_ui.getCurrentAccounts().getBook().getLocalStorage()

    last = None
    keys=sorted(LS.keys())
    for theKey in keys:
        value = LS.get(theKey)
        if not theKey.lower().startswith("report_params."): continue
        split_key = theKey.split(".",2)
        if split_key[1] != last:
            memz.append("")
            last = split_key[1]

        if theKey.lower().strip().endswith(".accounts") or theKey.lower().strip().endswith(".source_accts"):
            memz.append("Key:%s Value: %s" % (pad(theKey,70), "<not displayed - but contains %s accounts>" %(value.count(",")+1)))
        else:
            memz.append("Key:%s Value: %s" % (pad(theKey,70), value.strip()))

    x=LS.get("grfRepDefaultParams")
    if x:
        memz.append("\n\nDefault Parameters: 'grfRepDefaultParams' (Probably Legacy keys)")
        memz.append("%s" %x)
        memz.append("")

    memz.append("\n<END>")

    for i in range(0, len(memz)):
        memz[i] = memz[i] + "\n"
    memz = "".join(memz)
    return memz

def view_extensions_details():
    theData = []                                                                                                    # noqa

    theData.append("EXTENSION(s) DETAILS")
    theData.append(" =====================\n")

    theData.append("Extensions enabled: %s\n" %moneydance_ui.getMain().getSourceInformation().getExtensionsEnabled())

    theUpdateList = get_extension_update_info()

    # noinspection PyBroadException
    try:
        x = moneydance.getLoadedModules()
        for y in x:
            isUpdatable= "(latest version)"
            updateInfo = theUpdateList.get(y.getIDStr().lower())
            if updateInfo:
                isUpdatable+= "\t******* Updatable to version: %s *******" % str(updateInfo[0].getBuild()).upper()
            theData.append("Extension ID: " + y.getIDStr())
            theData.append("Extension Name: " + y.getName())
            theData.append("Extension Display Name: " + y.getDisplayName())
            theData.append("Extension Description: " + y.getDescription())
            theData.append("Extension Version: " + str(y.getBuild()) + isUpdatable)
            theData.append("Extension Source File: " + str(y.getSourceFile()))
            theData.append("Extension Vendor: " + y.getVendor())
            theData.append("Extension isBundled: " + str(y.isBundled()))
            theData.append("Extension isVerified: " + str(y.isVerified()))
            if moneydance_ui.getPreferences().getSetting("confirmedext."+str(y.getName()).strip(), None):
                theData.append("** User has Confirmed this unsigned Extension can run - version: " + moneydance_ui.getPreferences().getSetting("confirmedext."+str(y.getName()).strip(), None))
            theData.append("\n\n")

        x = moneydance.getSuppressedExtensionIDs()
        for y in x:
            theData.append("Internal/suppressed/secret extensions: " + str(y))

        x = moneydance.getOutdatedExtensionIDs()
        for y in x:
            theData.append("Outdated extensions (not loaded): " + str(y))
    except:
        theData.append("\nERROR READING EXTENSION DATA!!!!\n")
        dump_sys_error_to_md_console_and_errorlog()

    orphan_prefs, orphan_files, orphan_confirmed_extn_keys = get_orphaned_extension()

    if len(orphan_prefs)<1 and len(orphan_files)<1 and len(orphan_confirmed_extn_keys)<1:
        theData.append("\nCONGRATULATIONS - NO ORPHAN EXTENSIONS DETECTED!!\n")

    else:
        theData.append("\nLISTING EXTENSIONS ORPHANED IN CONFIG.DICT OR FILES (*.MXT)\n")

        for x in orphan_prefs.keys():
            theData.append("%s Extension: %s is %s" %(pad("config.dict:",20),pad(x,20),pad(orphan_prefs[x],20)))

        theData.append("")

        for x in orphan_confirmed_extn_keys.keys():
            _theVersion = moneydance_ui.getPreferences().getSetting(orphan_confirmed_extn_keys[x][1],None)
            theData.append("%s Extension: %s Key: %s (build: %s) is %s" %(pad("config.dict:",20),pad(x,20),pad(orphan_confirmed_extn_keys[x][1],40),_theVersion, pad(orphan_confirmed_extn_keys[x][0],20)))

        theData.append("")

        for x in orphan_files.keys():
            theData.append("%s Extension: %s is %s" %(pad("File: "+orphan_files[x][1],40),pad(x,20),pad(orphan_files[x][0],20)))

    theData.append("\n<END>")

    # Build a quick virtual 'file' of Memorized reports and graphs to display
    for i in range(0, len(theData)):
        theData[i] = theData[i] + "\n"
    theData = "".join(theData)
    return theData

# noinspection PyBroadException
def downloadExtensions():
    downloadInfo = StreamTable()
    if moneydance_ui.getMain().getSourceInformation().getExtensionsEnabled():
        inx = None
        try:
            url = URL(System.getProperty("moneydance.extension_list_url", "https://infinitekind.com/app/md/extensions.dct"))
            inx = BufferedReader(InputStreamReader(url.openStream(), "UTF8"))
            downloadInfo.readFrom(inx)
        except:
            myPrint("B", "ERROR downloading from Moneydance extensions list website... ")
            dump_sys_error_to_md_console_and_errorlog()

        finally:
            if inx:
                try:
                    inx.close()
                except:
                    myPrint("B", "Error closing URL stream")
                    dump_sys_error_to_md_console_and_errorlog()
        return downloadInfo
    else:
        myPrint("B", "@@ Extensions not enabled!!?? @@")
    return False

def check_if_key_string_valid(test_str):
    # http://docs.python.org/library/re.html
    # re.search returns None if no position in the string matches the pattern
    # pattern to search for any character other than "._-A-Za-z0-9"
    pattern = r'[^a-zA-Z0-9-_.]'
    if re.search(pattern, test_str):
        myPrint("DB","Invalid: %r" %(test_str))
        return False
    else:
        myPrint("DB","Valid: %r" %(test_str))
        return True

def get_extension_update_info():
    availableExtensionInfo=downloadExtensions()
    moduleList = availableExtensionInfo.get("feature_modules")      # StreamVector

    installed = moneydance_ui.getMain().getLoadedModules()          # FeatureModule[]
    excludedIDs = moneydance.getSuppressedExtensionIDs()            # List<String>
    for installedMod in installed:
        if installedMod.isBundled():
            excludedIDs.add(installedMod.getIDStr().toLowerCase())

    miniUpdateList={}

    try:
        if moduleList:
            for obj in moduleList:
                if not (isinstance(obj, StreamTable)):
                    myPrint("J", "ERROR - Retrieved data is not a StreamTable()", obj)
                    continue

                extInfo = ModuleMetaData(obj)       # ModuleMetaData

                # noinspection PyUnresolvedReferences
                if excludedIDs.contains(extInfo.getModuleID().lower()):     # Probably internal modules like Python/Jython
                    continue
                if not (1928 >= extInfo.getMinimumSupportedBuild() and 1928 <= extInfo.getMaximumSupportedBuild()):  # noqa
                    continue
                if not (extInfo.getMinimumSupportedBuild() >= 1000):
                    continue
                if not(extInfo.isMacSandboxFriendly() or not Platform.isMac() or not moneydance_ui.getMain().getPlatformHelper().isConstrainedToSandbox()):
                    continue
                existingMod = None          # FeatureModule
                for mod in installed:

                    # noinspection PyUnresolvedReferences
                    if mod.getIDStr().lower() == extInfo.getModuleID().lower():
                        existingMod = mod
                        break
                isInstalled = (existingMod is not None)     # boolean
                isUpdatable = (existingMod is not None and existingMod.getBuild() < extInfo.getBuild())
                if existingMod and isInstalled and isUpdatable:

                    # noinspection PyUnresolvedReferences
                    miniUpdateList[extInfo.getModuleID().lower()] = [extInfo, isInstalled, isUpdatable]

        else:
            myPrint("J", "ERROR - Failed to download module list!)")
    except:
        myPrint("B", "ERROR decoding downloaded module list!)")
        dump_sys_error_to_md_console_and_errorlog()

    return miniUpdateList

def get_register_txn_sort_orders():

    # Flush in memory settings to disk
    moneydance.savePreferences()

    theSortData = []                                                                                                # noqa

    theSortData.append("VIEW REGISTER TXN SORT ORDERS (for Accounts - excluding legacy keys)")
    theSortData.append(" ==================================================================\n")

    theSortData.append("DEFAULTS (from config.dict)\n")

    for x in _COLWIDTHS:

        if      x == "bank":        theType = "Bank"
        elif    x == "cc":          theType = "Credit Card"
        elif    x == "invest":      theType = "Investment"
        elif    x == "loan":        theType = "Loan"
        elif    x == "security":    theType = "Security"
        elif    x == "misc":        theType = "Asset/Liability/Expense/Income/Other"
        elif    x == "rec_credits": theType = "Reconciling window - credits"
        elif    x == "rec_debits":  theType = "Reconciling window - debits"
        elif    x == "secdetail":   theType = "Security Detail"
        elif    x == "split":       theType = "Split Window"
        else:                       theType = "????"

        result = loadMDPreferences(None,x)
        if result:
            oneLineMode = result[0]
            splitReg    = result[1]
            splitSz     = result[2]
            sortID      = result[3]
            position    = result[4]
            ascending   = result[5]
            widths      = result[6]
            position2   = result[7]

            theSortData.append("\nType: %s (%s) Register Sort Data:"%(theType,x))
            theSortData.append(">> Sort Order: %s" %sortID)
            theSortData.append(">> Ascending: %s" %ascending)
            theSortData.append(">> One Line View: %s" %oneLineMode)
            theSortData.append(">> Split Register View: %s (%s)" %(splitReg,splitSz))
            theSortData.append(">> Position: %s Widths: %s Position2 %s\n" %(position, widths, position2))


    theSortData.append("\nDATA SAVED INTERNALLY BY (ACTIVE) ACCOUNT")
    theSortData.append("-----------------------------------------\n")

    accounts = AccountUtil.allMatchesForSearch(moneydance_data, MyAcctFilter(1))
    for acct in accounts:

        for x in _COLWIDTHS:

            if      x == "bank":        theType = "Bank"
            elif    x == "cc":          theType = "Credit Card"
            elif    x == "invest":      theType = "Investment"
            elif    x == "loan":        theType = "Loan"
            elif    x == "security":    theType = "Security"
            elif    x == "misc":        theType = "Asset/Liability/Expense/Income/Other"
            elif    x == "rec_credits": theType = "Reconciling window - credits"
            elif    x == "rec_debits":  theType = "Reconciling window - debits"
            elif    x == "secdetail":   theType = "Security Detail"
            elif    x == "split":       theType = "Split Window"
            else:                       theType = "????"

            result = loadMDPreferences(acct,x, False)

            if result:
                oneLineMode = result[0]
                splitReg    = result[1]
                splitSz     = result[2]
                sortID      = result[3]
                position    = result[4]
                ascending   = result[5]
                widths      = result[6]
                position2   = result[7]

                theSortData.append("\nAccount: %s Account Type: %s Key Type: %s (%s) Register Sort Data:"%(acct.getAccountName(), acct.getAccountType(),theType,x))
                theSortData.append(">> Sort Order: %s" %sortID)
                theSortData.append(">> Ascending: %s" %ascending)
                theSortData.append(">> One Line View: %s" %oneLineMode)
                theSortData.append(">> Split Register View: %s (%s)" %(splitReg,splitSz))
                theSortData.append(">> Position: %s Widths: %s Position2 %s\n" %(position, widths, position2))

    theSortData.append("\n<END>")

    for i in range(0, len(theSortData)):
        theSortData[i] = theSortData[i] + "\n"
    theSortData = "".join(theSortData)
    return theSortData

def view_check_num_settings(statusLabel):
    try:
        from com.infinitekind.moneydance.model import CheckNumSettings
    except:
        statusLabel.setText(("Sorry - your version of MD is too early to use this function, must be at least Moneydance 2020.1 (1925)").ljust(800, " "))
        statusLabel.setForeground(Color.RED)
        return

    theData = []                                                                                                    # noqa

    theData.append("CHECK NUMBER SETTINGS")
    theData.append(" =====================\n")

    acct = root = moneydance.getCurrentAccountBook().getRootAccount()
    x = root.getCheckNumSettings(True)  # False means don't return defaults
    theData.append("\nMaster Dataset & defaults (root account): " + moneydance.getCurrentAccountBook().getName())
    if not x:  # Assume old style check numbers
        theData.append(
            " >>Old style Check numbers as default: " + str(moneydance_ui.getResources().getCheckNumberList(acct)))
        theData.append("\n\n")
    else:
        theData.append(" >>Fixed Chq Items: " + str(x.getPopupStrings()))
        theData.append(
            " >>Complete list of all Items in Chq Popup: " + str(moneydance_ui.getResources().getCheckNumberList(acct)))
        y = x.getRecentsOption()

        # noinspection PyUnresolvedReferences
        if y == CheckNumSettings.IncludeRecentsOption.ACCOUNT: y = "Include from Same Account"
        elif y == CheckNumSettings.IncludeRecentsOption.GLOBAL: y = "Include from All Accounts"
        elif y == CheckNumSettings.IncludeRecentsOption.NONE: y = "Don't Include"

        theData.append(" >>Recent Entries: " + str(y))
        theData.append(" >>Max Entries: " + str(x.getMaximumRecents()))
        theData.append(" >>Show Next-Check Number: " + str(x.getIncludeNextCheckNumber()))
        theData.append(" >>Show Print-Check Option: " + str(x.getIncludePrintCheckMarker()))
        theData.append("\n")

    accounts = AccountUtil.allMatchesForSearch(moneydance_data, MyAcctFilter(3))

    for acct in accounts:

        # noinspection PyUnresolvedReferences
        if acct.getAccountType() == Account.AccountType.ROOT: continue

        x = acct.getCheckNumSettings(False)  # False means don't return defaults

        if not x:
            theData.append("Account: " + acct.getFullAccountName() + " (Settings: NONE/Default)")
            theData.append(" >>Complete list of all Items in Chq Popup: " + str(
                moneydance_ui.getResources().getCheckNumberList(acct)))
            theData.append("\n")
        else:
            theData.append("Account: " + pad(acct.getFullAccountName(), 80))
            theData.append(" >>Fixed Chq Items: " + str(x.getPopupStrings()))
            if acct.getAccountType() != Account.AccountType.ROOT:                                               # noqa
                theData.append(" >>Complete list of all Items in Chq Popup: " + str(
                    moneydance_ui.getResources().getCheckNumberList(acct)))

            y = x.getRecentsOption()
            if y == CheckNumSettings.IncludeRecentsOption.ACCOUNT:                                              # noqa
                y = "Include from Same Account"
            elif y == CheckNumSettings.IncludeRecentsOption.GLOBAL:                                             # noqa
                y = "Include from All Accounts"
            elif y == CheckNumSettings.IncludeRecentsOption.NONE:                                               # noqa
                y = "Don't Include"

            theData.append(" >>Recent Entries: " + str(y))
            theData.append(" >>Max Entries: " + str(x.getMaximumRecents()))
            theData.append(" >>Show Next-Check Number: " + str(x.getIncludeNextCheckNumber()))
            theData.append(" >>Show Print-Check Option: " + str(x.getIncludePrintCheckMarker()))
            theData.append("\n")
            # CheckNumSettings.IncludeRecentsOption

    theData.append(("\n<END>"))

    # Build a quick virtual file of Memorized reports and graphs to display
    for i in range(0, len(theData)):
        theData[i] = theData[i] + "\n"
    theData = "".join(theData)
    return theData

def getMDEncryptionKey():

    try:
        keyFile = File(moneydance_data.getRootFolder(), "key")

        keyInfo = SyncRecord()
        fin = FileInputStream(keyFile)
        keyInfo.readSet(fin)
        fin.close()

        # noinspection PyUnresolvedReferences
        cipherLevel = LocalStorageCipher.MDCipherLevel.GOOD

        keyString=keyInfo.getString("key",None)
        test_with_random = "E6520436865636B2C2062616279206F6E65203220312074776F4D6963726F7068306E6520436865636B204D6963723070686F6"
        y=StringUtils.decodeHex(test_with_random[int(len(test_with_random)/2):]+test_with_random[:int(len(test_with_random)/2)])
        z=""
        for x in y: z+=chr(x)
        newPassphrase = z
        encryptedKeyBytes = StringUtils.decodeHex(keyString)
        if keyInfo.getBoolean("userpass", False):
            newPassphrase = moneydance_ui.getCurrentAccounts().getEncryptionKey()
            if not newPassphrase:
                return "Not sure: Error retrieving your Encryption key!"
        try:

            # This next line triggers a message in the console error log file: "loading with 128 bit encryption key"
            myPrint("J","I'm testing your encryption key.... Will trigger a 'loading with 128 bit encryption key' message on next line......")
            key = LocalStorageCipher.encryptionKeyFromBytesAndPassword(encryptedKeyBytes, list(newPassphrase), cipherLevel)
            # cipher = LocalStorageCipher(key, cipherLevel)
        except:
            return "Not sure: could not decrypt from your passphrase!"

        theFormat  = key.getFormat()
        theAlg = key.getAlgorithm()
    except:
        return "Not sure: Error in decryption routine - oh well!!"


    return "%s / %s" % (theFormat, theAlg)

def decode_encrypted_files():
    # Code to decrypt MD files and write unencrypted.... Neat eh!?
    x = get_home_dir()
    y  = File(x,"decoded_local_storage.BIF")
    OStream = FileOutputStream(y)
    myPrint("B","Bytes copied: ")
    myPrint("B",moneydance.getCurrentAccountBook().getLocalStorage().readFile("./settings",OStream) )
    myPrint("B", "File is located at: %s" %y.getAbsolutePath() )
    OStream.close()
    return

def get_ofx_related_data():
    OFX = []

    OFX.append("I NEED SOMEONE WITH ONLINE BANKING TO VOLUNTEER TO TEST - SO I CAN DISPLAY MORE USEFUL DATA!!!?\n\n ")
    for service in moneydance_data.getOnlineInfo().getAllServices():
        OFX.append(pad("Service:",40) + str(service))
        OFX.append(pad(">>OFX Version:",40) + str(service.getOFXVersion()))
        OFX.append(pad(">>Service Id:",40) + str(service.getServiceId()))
        OFX.append(pad(">>Realms:",40) + str(service.getRealms()))
        OFX.append(pad(">>Bootstrap URL:",40) + str(service.getBootstrapURL()))
        OFX.append(pad(">>Bootstrap URL str:",40) + str(service.getBootstrapURLString()))
        OFX.append(pad(">>Accounts:",40) + str(service.getAvailableAccounts()))
        OFX.append("")

    if moneydance.getRootAccount().getParameter("ofx.client_uid", None):
        OFX.append(pad("ofx.client_uid:",40) + moneydance.getRootAccount().getParameter("ofx.client_uid", None))
        OFX.append("")

    accounts = AccountUtil.allMatchesForSearch(moneydance_data, MyAcctFilter(0))
    for acct in accounts:
        if acct.getParameter("ofx_import_acct_num", None):
            OFX.append(pad(str(acct) + " - ofx_import_acct_num (remembered):",75) + acct.getParameter("ofx_import_acct_num", None))

        if acct.getBooleanParameter("ofx_import_remember_acct_num", False):
            OFX.append(pad(str(acct) + " - ofx_import_remember_acct_num (remembered):",75) + str(acct.getBooleanParameter("ofx_import_remember_acct_num", False)))

        if acct.getOFXAccountKey():
            OFX.append(pad(str(acct) + " acct.getOFXAccountKey():",75) + str(acct.getOFXAccountKey()))

        if acct.getOFXAccountNumber():
            OFX.append(pad(str(acct) + " acct.getOFXAccountNumber():",75) + str(acct.getOFXAccountNumber()))

        if acct.getOFXAccountType():
            OFX.append(pad(str(acct) + " acct.getOFXAccountType():",75) + str(acct.getOFXAccountType()))

        if acct.getOFXBankID():
            OFX.append(pad(str(acct) + " acct.getOFXBankID():",75) + str(acct.getOFXBankID()))

    # getBankingFI()
    # getBillPayFI()

    OFX.append("\n<END>")
    for i in range(0, len(OFX)):
        OFX[i] = OFX[i] + "\n"
    OFX = "".join(OFX)
    return OFX

def display_help():
    global debug

    myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )

    help_data = \
        """
Author: Stuart Beesley - StuWareSoftSystems (written November/December 2020 - a lockdown project)
Credit: Derek Kent(23) for his extensive texting

Get more Scripts/Extensions from: https://yogi1967.github.io/MoneyDancePythonScripts/

NOTE: I AM JUST A USER - I HAVE NO AFFILIATION WITH MONEYDANCE!

This is a Python(Jython 2.7) script that runs inside of Moneydance via the Moneybox Python Interpreter
As such it has full access to Moneydance's internals.
However, where possible this script uses the published APIs. In certain circumstances, it calls internal functions.
The script will never change anything without your permission - and it will always ask you for such (several times).

DISCLAIMER: YOU USE THIS SCRIPT AT YOUR OWN RISK AND YOU ACCEPT ANY CONSEQUENCES OF CHANGING YOUR DATA!

PLEASE ALWAYS BACKUP YOUR DATA FIRST! You  can use the Export Backup (green) button top-left in Toolbox to do this.

PURPOSE

To enable the User to self-diagnose problems, or access key diagnostics to enable support to help
- Basic (default) mode is very safe - it contains view options only
- Advanced Mode - Allows user to run fixes - THIS CHANGES DATA
- Geek Mode - Allows user to view technical information/settings in various places (this is readonly)
- Hacker Mode - Allows the user to manually add/change/delete config.dict and LocalStorage() keys/values - ONLY USE IF YOU KNOW WHAT YOU ARE DOING

- The Toolbox offers the option to Backup first  - ALWAYS BACKUP (But this is your choice!)
- The Toolbox will *ALWAYS* make a copy of config.dict, custom theme file, LocalStorage() ./safe/settings before any changes
>> These backup files will have a unique (timestamp-like) number and _$SAVED$ appended to the end of the filename

>> Your dataset backups will be located wherever you choose to save them (USE THE 'EXPORT BACKUP' button (top left in green)
>> Note the normal Moneydance Backup is a complete dataset, but does not include config.dict, custom theme file, extensions etc

- All updates (and other key messages) get written to the Moneydance console error log

# Includes my previous / standalone scripts:
# FIX-reset_window_location_data.py 0.2beta
# DIAG-can_i_delete_security.py v2
# DIAG-list_security_currency_decimal_places.py v1
# DIAG-diagnose_currencies.py v2a
# fix_macos_tabbing_mode.py v1b

# Also includes these MD scripts (enhanced)
# reset_relative_currencies.py              (from Moneydance support)
# remove_ofx_account_bindings.py            (from Moneydance support)
# convert_secondary_to_primary_data_set.py  (from Moneydance support)
# remove_one_service.py                     (from Moneydance support)
# delete_invalid_txns.py                    (from Moneydance support)

Features:
- Main window shows various diagnostic data and MD Preferences

NOTE: Where CMD is specified, this may be CTRL (or ALT) in Windows / Linux

CMD-I - This  Help Instruction Information

CMD-O - Copy all outputs to Clipboard

ALT-B - Basic Mode
- Basic mode: Buttons
    - EXPORT BACKUP (This calls the Moneydance function to backup your dataset)
    - Copy (Diagnostics) to Clipboard
    - Display MD Passwords (encryption and Sync)
    - View MD Config.dict file
    - View MD Custom Theme file  (only appears if it exists)
    - View Console.log
    - Copy Console.log file to wherever you want
    - View your Java .vmoptions file (only appears if it exists)
    - Open MD Folder
      (Preferences, Themes, Console log, Dataset, Extensions, Auto-backup folder, last backup folder[, Install Dir])
    - Find my Dataset (Search for *.moneydance & *.moneydancearchive Datasets)
    - View memorised reports (parameters and default settings)
    - View Register Txn Sort Orders
    - View Check number settings
    - View Extensions details
    - DIAGnostics - Can I delete a Security (tells you whether a security/stock is being used - and where)
    - DIAGnostics - List decimal places (currency and security). Shows you hidden settings etc.
    - DIAGnostics - Diagnose relative currencies. If errors, then go to FIX below
    - DIAGnostics - View Categories with zero balance. You can also inactivate these below.
    - VIEW - OFX Related Data

ALT-M - Advanced Mode
    - FIX - Change Moneydance Fonts
    - FIX - Delete Custom Theme file
    - FIX - Fix relative currencies
    - FIX - Inactivate all Categories with Zero Balance
    - FIX - Forget OFX Banking Import Link (so that it asks you which account when importing ofx files)
    - FIX - Delete OFX Banking Logon Profile / Service (these are logon profiles that allow you to connect to your bank)
    - FIX - Correct the Name of Root to match Dataset
    - FIX - Make me a Primary Dataset (convert from secondary dataset to enable Sync))
    - FIX - Delete One-Sided Txns
    - FIX - Delete Orphaned/Outdated Extensions (from config.dict and .mxt files)
    - FIX - RESET Window Display Settings
            This allows you to tell Moneydance to forget remembered Display settings:
            1. RESET>> Just Window locations (i.e. it leaves the other settings intact).
            2. RESET>> Just Register Transaction Filters.
            3. RESET>> Just Register Transaction Initial Views (e.g. In investments, start on Portfolio or Security View
            4. RESET>> Window locations, Size, Sort Orders, One-line, Split Reg, Offset, Column Widths; Dividers, isOpen,
            isExpanded, isMaximised settings (this does not reset Filters or Initial views)
    - FIX - Check / fix MacOS Tabbing Mode on Big Sur. If set to always it will allow you to change it
            More information here: https://support.apple.com/en-gb/guide/mac-help/mchla4695cce/mac
            
ALT-G - GEEK OUT MODE
    >> Allows you to view raw settings
    - Search for keys or keydata containing filter characters (you specify)
    - ROOT Parameter keys
    - Local Storage - Settings
    - User Preferences
    - All Accounts’ preference keys
    - View single Object's Keys/Data (Account, Category, Currency, Security, Report / Graph, Reminder, Address, OFX Service, by UUID, TXNs)
    - All Sync Settings
    - All Online Banking Settings
    - All Settings related to window sizes/positions/locations etc
    - All Environment Variables
    - All Java Properties

Menu - HACKER MODE
    >> VERY TECHNICAL - DO NOT USE UNLESS YOU KNOW WHAT YOU ARE DOING
    >> Allows User to Add/Change/Delete a key/value in config.dict or LocalStorage() (./safe/settings)

CMD-P - View parameters file (StuWareSoftSystems). Also allows user to Delete all, and/or change/delete single saved parameters

Menu - DEBUG MODE
    >> Turns on script debug messages...
    
<END>
"""

    help_data = "".join(help_data)

    return help_data

# noinspection PyArgumentList
class MyTxnSearchFilter(TxnSearch):

    def __init__(self,dateStart,dateEnd):
        super(TxnSearch, self).__init__()

        self.dateStart = dateStart
        self.dateEnd = dateEnd

    def matchesAll(self):                                                                                           # noqa
        return False

    def matches(self, txn):

        if txn.getDateInt() >= self.dateStart and txn.getDateInt() <= self.dateEnd:                                 # noqa
            return True
        return False

class MyAcctFilter(AcctFilter):
    selectType = 0

    def __init__(self, selectType=0):
        self.selectType = selectType

    def matches(self, acct):
        if self.selectType == 0:
            # noinspection PyUnresolvedReferences
            if not (acct.getAccountType() == Account.AccountType.BANK
                    or acct.getAccountType() == Account.AccountType.CREDIT_CARD
                    or acct.getAccountType() == Account.AccountType.INVESTMENT):
                return False

        if self.selectType == 10:
            # noinspection PyUnresolvedReferences
            if not (acct.getAccountType() == Account.AccountType.BANK
                    or acct.getAccountType() == Account.AccountType.CREDIT_CARD
                    or acct.getAccountType() == Account.AccountType.INVESTMENT):
                return False

            if acct.getParameter("ofx_import_acct_num", None) is not None \
                    or acct.getParameter("ofx_import_remember_acct_num", None) is not None:
                return True
            return False

        if self.selectType == 1:
            # noinspection PyUnresolvedReferences
            if not (acct.getAccountType() == Account.AccountType.BANK
                    or acct.getAccountType() == Account.AccountType.CREDIT_CARD
                    or acct.getAccountType() == Account.AccountType.LOAN
                    or acct.getAccountType() == Account.AccountType.ASSET
                    or acct.getAccountType() == Account.AccountType.ROOT
                    or acct.getAccountType() == Account.AccountType.LIABILITY
                    or acct.getAccountType() == Account.AccountType.INVESTMENT):
                return False

        if self.selectType == 2:
            # noinspection PyUnresolvedReferences
            if acct.getAccountType() == Account.AccountType.SECURITY: return True
            else: return False

        if self.selectType == 3:
            # noinspection PyUnresolvedReferences
            if not (acct.getAccountType() == Account.AccountType.BANK
                    or acct.getAccountType() == Account.AccountType.ROOT):
                return False

        if self.selectType == 4:
            # noinspection PyUnresolvedReferences
            if not (acct.getAccountType() == Account.AccountType.EXPENSE
                    or acct.getAccountType() == Account.AccountType.INCOME):
                return False
            return True

        if self.selectType == 5:
            # noinspection PyUnresolvedReferences
            if not (acct.getAccountType() == Account.AccountType.BANK
                    or acct.getAccountType() == Account.AccountType.CREDIT_CARD
                    or acct.getAccountType() == Account.AccountType.LOAN
                    or acct.getAccountType() == Account.AccountType.ASSET
                    or acct.getAccountType() == Account.AccountType.LIABILITY
                    or acct.getAccountType() == Account.AccountType.INVESTMENT):
                return False
            return True

        if self.selectType == 6:
            # if not (acct.getAccountType() == Account.AccountType.BANK
            #         or acct.getAccountType() == Account.AccountType.CREDIT_CARD
            #         or acct.getAccountType() == Account.AccountType.LOAN
            #         or acct.getAccountType() == Account.AccountType.ASSET
            #         or acct.getAccountType() == Account.AccountType.ROOT
            #         or acct.getAccountType() == Account.AccountType.LIABILITY
            #         or acct.getAccountType() == Account.AccountType.INVESTMENT):
            #     return False
            return True

        if self.selectType == 7:
            # noinspection PyUnresolvedReferences
            if not (acct.getAccountType() == Account.AccountType.BANK
                    or acct.getAccountType() == Account.AccountType.CREDIT_CARD
                    or acct.getAccountType() == Account.AccountType.LOAN
                    or acct.getAccountType() == Account.AccountType.ASSET
                    or acct.getAccountType() == Account.AccountType.LIABILITY
                    or acct.getAccountType() == Account.AccountType.INVESTMENT):
                return False
            return True

        if self.selectType == 8:
            # noinspection PyUnresolvedReferences
            if not (acct.getAccountType() == Account.AccountType.EXPENSE
                    or acct.getAccountType() == Account.AccountType.INCOME):
                return False
            return True

        if self.selectType == 9:
            # noinspection PyUnresolvedReferences
            if not acct.getAccountType() == Account.AccountType.SECURITY:
                return False
            return True

        if (acct.getAccountOrParentIsInactive()): return False
        if (acct.getHideOnHomePage() and acct.getBalance() == 0): return False

        return True

class QuickJFrame():

    def __init__(self, title, output, lAlertLevel=0):
        self.title = title
        self.output = output
        self.lAlertLevel = lAlertLevel

    class CloseAction(AbstractAction):

        def __init__(self, theFrame):
            self.theFrame = theFrame

        def actionPerformed(self, event):
            global debug
            myPrint("D","in CloseAction(), Event: ", event)

            myPrint("DB", "QuickJFrame() Frame shutting down....")

            self.theFrame.dispose()
            return

    def show_the_frame(self):
        global lCopyAllToClipBoard_TB, debug, Toolbox_frame_

        screenSize = Toolkit.getDefaultToolkit().getScreenSize()
        frame_width = screenSize.width - 20
        frame_height = screenSize.height - 20

        JFrame.setDefaultLookAndFeelDecorated(True)

        jInternalFrame = JFrame(self.title)

        if not Platform.isOSX():
            jInternalFrame.setIconImage(MDImages.getImage(moneydance_ui.getMain().getSourceInformation().getIconResource()))

        jInternalFrame.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE)
        jInternalFrame.setResizable(True)

        shortcut = Toolkit.getDefaultToolkit().getMenuShortcutKeyMaskEx()
        jInternalFrame.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_W, shortcut), "close-window")
        jInternalFrame.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_F4, shortcut), "close-window")

        jInternalFrame.getRootPane().getActionMap().put("close-window", self.CloseAction(jInternalFrame))

        theJText = JTextArea(self.output)
        theJText.setEditable(False)
        theJText.setLineWrap(True)
        theJText.setWrapStyleWord(True)
        # theJText.setFont(Font("monospaced", Font.PLAIN, 15))
        theJText.setFont( getMonoFont() )

        internalScrollPane = JScrollPane(theJText, JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED,JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED)

        if self.lAlertLevel>=2:
            internalScrollPane.setBackground(Color.RED)
            theJText.setBackground(Color.RED)
            theJText.setForeground(Color.BLACK)
        elif self.lAlertLevel>=1:
            internalScrollPane.setBackground(Color.YELLOW)
            theJText.setBackground(Color.YELLOW)
            theJText.setForeground(Color.BLACK)

        jInternalFrame.setMinimumSize(Dimension(frame_width - 50, 0))
        jInternalFrame.setMaximumSize(Dimension(frame_width - 50, frame_height - 100))

        if Platform.isWindows():
            if theJText.getLineCount() > 30:
                jInternalFrame.setPreferredSize(Dimension(frame_width - 50, frame_height - 100))

        jInternalFrame.add(internalScrollPane)

        jInternalFrame.pack()
        jInternalFrame.setLocationRelativeTo(Toolbox_frame_)
        jInternalFrame.setVisible(True)

        if "errlog.txt" in self.title:
            theJText.setCaretPosition(theJText.getDocument().getLength())

        try:
            if lCopyAllToClipBoard_TB:
                Toolkit.getDefaultToolkit().getSystemClipboard().setContents(StringSelection(self.output), None)
        except:

            myPrint("J","Error copying contents to Clipboard")
            dump_sys_error_to_md_console_and_errorlog()

        return (jInternalFrame)

def display_pickle():
    global debug, myParameters

    myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )

    if myParameters is None: myParameters = {}

    params = []
    for key in sorted(myParameters.keys()):
        params.append("Key: " + pad(str(key),50) + " Type: " + pad(str(type(myParameters[key])),20) + "Value: " + str(myParameters[key]) + "\n")

    params.append("\n<END>")

    params = "".join(params)

    return params

def can_I_delete_security(statusLabel):
    global Toolbox_frame_, debug
    myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )

    myPrint("B", "Script running to analyse whether you can delete a Security, or show where it's used....")
    myPrint("P", "----------------------------------------------------------------------------------------")

    if moneydance_data is None:
        statusLabel.setText(("No data to scan - aborting..").ljust(800, " "))
        statusLabel.setForeground(Color.RED)
        return

    usageCount = 0
    sumShares = 0

    book = moneydance.getCurrentAccountBook()
    allCurrencies = book.getCurrencies().getAllCurrencies()

    securities = []

    for currency in allCurrencies:
        # noinspection PyUnresolvedReferences
        if currency.getCurrencyType() == CurrencyType.Type.SECURITY:
            securities.append(currency)

    securities = sorted(securities, key=lambda x: (x.getName().upper()))

    selectedSecurity = JOptionPane.showInputDialog(Toolbox_frame_,
                                                   "Select Security", "Select the security to analyse",
                                                   JOptionPane.INFORMATION_MESSAGE,
                                                   moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                   securities,
                                                   None)
    if selectedSecurity is None:
        statusLabel.setText("No security was selected - aborting..".ljust(800, " "))
        statusLabel.setForeground(Color.RED)
        return

    output = "\nYou want me to look for Security: " + str(selectedSecurity) + "\n"

    accountsList = AccountUtil.allMatchesForSearch(book, MyAcctFilter(2))
    output += "Searching through %s security (sub) accounts.." % (len(accountsList)) + "\n"

    for account in accountsList:
        if account.getCurrencyType() == selectedSecurity:
            # noinspection PyUnresolvedReferences
            output += "   >> Security: %s is used in Account: %s - Share holding balance: %s" \
                      % (selectedSecurity, account.getParentAccount().getAccountName(),
                         selectedSecurity.getDoubleValue(account.getBalance())) + "\n"
            # noinspection PyUnresolvedReferences
            sumShares += selectedSecurity.getDoubleValue(account.getBalance())
            usageCount += 1

    if not usageCount:
        output += "   >> Security not found in any accounts.\n"

    output += "\nChecking security for price history...:\n"

    # noinspection PyUnresolvedReferences
    secSnapshots = selectedSecurity.getSnapshots()
    countPriceHistory = secSnapshots.size()
    if countPriceHistory > 0:
        output += "   >> Security has %s historical prices!" % (secSnapshots.size()) + "\n"
    else:
        output += "   >> Security has no historical prices. \n"

    output += "-----------------------------------------------------------------\n"
    if usageCount:
        output += "\nUSAGE FOUND: You are using security: %s in %s accounts!\n... with a share balance of: %s. These would need to be removed before security deletion" \
                  % (selectedSecurity, usageCount, sumShares) + "\n"
        myPrint("J", ">> NO - Security cannot be deleted as it's being used:" + str(selectedSecurity))

    if countPriceHistory:
        output += "\nPRICE HISTORY FOUND: You have %s price records - If you delete Security then these will be lost..." \
                  % countPriceHistory + "\n"

    if not usageCount and not countPriceHistory:
        output += "\nNo usage of security %s found! You should be able to safely delete the Security" % selectedSecurity + "\n"
        statusLabel.setText(("No usage of security %s found! You should be able to safely delete the Security" % selectedSecurity).ljust(800, " "))
    else:
        statusLabel.setText(("Sorry - usage of Security: %s found - refer to script output for details.." % selectedSecurity).ljust(800,
                                                                                                                    " "))

    statusLabel.setForeground(Color.RED)

    output += "\n<END>"
    myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
    return output

def list_security_currency_decimal_places(statusLabel):
    global Toolbox_frame_, debug, DARK_GREEN
    myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )

    myPrint("B", "Script is analysing your Security decimal place settings...........")
    myPrint("P", "-------------------------------------------------------------------")

    if moneydance_data is None:
        statusLabel.setText("No data to scan - aborting..".ljust(800, " "))
        statusLabel.setForeground(Color.RED)
        return

    iWarnings = 0
    myLen = 50

    decimalPoint_MD = moneydance_ui.getPreferences().getSetting("decimal_character", ".")

    currs = moneydance_data.getCurrencies().getAllCurrencies()

    currs = sorted(currs, key=lambda x: str(x.getName()).upper())

    output = ""

    def analyse_curr(theCurr, theType):
        output = ""                                                                                                 # noqa
        iWarn = 0
        for sec_curr in theCurr:
            if str(sec_curr.getCurrencyType()) != theType: continue

            foo = str(round(CurrencyUtil.getUserRate(sec_curr, sec_curr.getRelativeCurrency()), 8))
            priceDecimals = max(sec_curr.getDecimalPlaces(), min(8, len(foo.split(decimalPoint_MD)[-1])))

            output += sec_curr.getName()[:myLen].ljust(myLen, " ") + "\tDPC: " + \
                      str(sec_curr.getDecimalPlaces()) + \
                      "\t" + \
                      "Relative to: " + str(sec_curr.getRelativeCurrency())[:20].ljust(20, " ") + \
                      "\t" + \
                      "Current rate: " + str(foo)[:20].ljust(20, " ") + \
                      "\tRate dpc: " + str(priceDecimals)
            if (sec_curr.getDecimalPlaces() < priceDecimals and theType == "SECURITY") and \
                    not foo.endswith(".0"):
                iWarn += 1
                output += " ***\n"
            else:
                output += "\n"
        return iWarn, output

    output += " ==============\n"
    output += " --- SECURITIES ----\n"
    output += " ==============\n"

    result = analyse_curr(currs, "SECURITY")
    iWarnings += result[0]
    output += result[1]

    output += " ==============\n"
    output += " --- CURRENCIES ----\n"
    output += " ==============\n"
    result = analyse_curr(currs, "CURRENCY")
    iWarnings += result[0]
    output += result[1]

    output += "-----------------------------------------------------------------"
    if iWarnings:
        output += "\nYou have %s Warning(s)..\n" % iWarnings
        output += "These are where your security decimal place settings seem less than 4 or not equal to price history dpc; This might be OK - depends on your setup\n"
        output += "NOTE: It's quite hard to determine the stored dpc, so use this as guidance only, not definitive!\n"
        output += "NOTE: - This setting is fixed. The only resolution is to create a new security and alter your txns to use the new security...\n"
        output += "DISCLAIMER: Always backup your data before changing your data. I can take no responsibility for any changes....\n"
        myPrint("J", "Decimal places: You have %s Warning(s).. Refer diagnostic file...\n" % iWarnings)
        statusLabel.setText(
            ("Decimal places: You have %s Warning(s).. Refer diagnostic file..." % iWarnings).ljust(800, " "))
        statusLabel.setForeground(Color.RED)
    else:
        output += "\nAll good, decimal places look clean! Congratulations!\n"
        myPrint("J", "All good, decimal places look clean! Congratulations!")
        statusLabel.setText("All good, decimal places look clean! Congratulations!".ljust(800, " "))
        statusLabel.setForeground(DARK_GREEN)

    myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

    output += "\n<END>"
    return output

def read_preferences_file(lSaveFirst=False):

    cf = Common.getPreferencesFile()

    if lSaveFirst:
        moneydance.savePreferences()

    try:
        st = StreamTable()
        st.readFromFile(str(cf))
        tk = st.getKeyArray()
        tk = sorted(tk)
    except:
        st, tk = None, None
        dump_sys_error_to_md_console_and_errorlog()

    return st,tk

def check_for_window_display_data( theKey, theValue ):

    if not isinstance(theValue, (str,unicode)):             return False
    if theKey.startswith("gui.current_theme"):              return False
    if theKey.startswith("gui.dashboard.item"):             return False
    if theKey.startswith("gui.font_increment"):             return False
    if theKey.startswith("gui.new_txn_on_record"):          return False
    if theKey.startswith("gui.quickdecimal"):               return False
    if theKey.startswith("gui.register_follows_txns"):      return False
    if theKey.startswith("gui.show_all_accts_in_popup"):    return False
    if theKey.startswith("gui.source_list_visible"):        return False

    # Preferences Home Screen options
    if theKey.startswith("gui.home.lefties"):               return False
    if theKey.startswith("gui.home.righties"):              return False
    if theKey.startswith("gui.home.unused"):                return False

    if not (theKey.startswith("ext_mgmt_win")
            or theKey.startswith("moneybot_py_divider")
            or theKey.startswith("mbot.loc")
            or theKey.startswith("gui.")
            or theKey.endswith("rec_reg.credit")
            or theKey.endswith("rec_reg.debit")
            or "col_widths." in theKey
            or ("sel_" in theKey and theKey.endswith("_filter"))
            or "sel_inv_view" in theKey

    ):
        return False

    if not ("window" in theKey
            or "win_loc" in theKey
            or "width" in theKey
            or "isopen" in theKey
            or "winloc" in theKey
            or "winsize" in theKey
            or "winsz" in theKey
            or "divider" in theKey
            or "location" in theKey
            or "size" in theKey
            or "rec_reg.credit" in theKey
            or "rec_reg.debit" in theKey
            or "mbot.loc" in theKey
            or "_expanded" in theKey
            or "_filter" in theKey
            or "maximized" in theKey
            or "sel_inv_view" in theKey
    ):
        return False

    return True

def check_for_just_locations_window_display_data( theKey, theValue ):

    # Assumes you have called check_for_window_display_data() first!

    # Locations are  number x number - e.g. 10x100
    if "x" not in theValue.lower(): return False

    if not ("win_loc" in theKey
            or "winloc" in theKey
            or "location" in theKey
            or "mbot.loc" in theKey):
        return False

    return True

# noinspection PyUnusedLocal
def check_for_just_register_filters_window_display_data( theKey, theValue ):

    # Assumes you have called check_for_window_display_data() first!

    if  not ("sel_" in theKey and theKey.endswith("_filter") ):
        return False

    return True

# noinspection PyUnusedLocal
def check_for_just_initial_view_filters_window_display_data( theKey, theValue ):

    if  not ("sel_" in theKey and theKey.endswith("_view") ):
        return False

    return True

# copied from Moneydance TxnRegister.class
def loadMDPreferences(dataObject,  preferencesKey, lGetDefaultForObject=True):   # dataObject should always = Account.

    preferencesKey = preferencesKey

    if not preferencesKey:
        dataPrefKey = "col_widths"
    else:
        dataPrefKey = "col_widths." + preferencesKey

    colWidthPrefs = None

    if dataObject:
        colWidthPrefs = dataObject.getPreference(dataPrefKey, None)

    if not lGetDefaultForObject and dataObject and not colWidthPrefs: return None

    if StringUtils.isBlank(colWidthPrefs) and preferencesKey:
        colWidthPrefs = moneydance_ui.getPreferences().getSetting(dataPrefKey, None)

    if not colWidthPrefs or StringUtils.isBlank(colWidthPrefs):
        return None

    if not colWidthPrefs.startswith(":"):
        colWidthPrefs = ":" + colWidthPrefs

    params = SyncRecord()
    try:
        params.readSet(StringReader(colWidthPrefs))
    except IOException:
        myPrint("B", "Error parsing register settings: " + colWidthPrefs + " key=" + preferencesKey)
        return None

    widths = params.getIntArray("cols")                                                     # int[]

    if params.getBoolean("splitreg", False):
        splitReg = True
        splitSz = Dimension(10, Math.max(0, params.getInt("splitsz", 100)))                   # Dimension
    else:
        splitSz = None
        splitReg = False

    ascending = params.getBoolean("ascending", True)
    sortID = TxnSortOrder.fromInt(params.getInt("sort", -1), ascending)                     # TxnSortOrder

    if sortID:
        pass

    oneLineMode = params.getBoolean("oneline", False)                                     # boolean

    position = params.getString("position", params.getString("offset", None))               # String
    if position:
        pass

    position2 = params.getString("position2", params.getString("offset2", None))            # String
    if position2:
        pass

    theUUID = None
    if dataObject: theUUID = dataObject.getUUID()

    if debug:
        myPrint("D","Object: ", dataObject, theUUID)
        myPrint("D","Analysing the key: %s" %preferencesKey)
        myPrint("D",":oneline:", oneLineMode, type(oneLineMode))
        myPrint("D","splitreg:", splitReg, type(splitReg))
        myPrint("D","splitsz:", splitSz, type(splitSz))
        myPrint("D","sort:", sortID, type(sortID))
        myPrint("D","position:", position, type(position))
        myPrint("D","ascending:", ascending, type(ascending))
        myPrint("D","cols:", widths, type(widths))
        myPrint("D","position2:", position2, type(position2))

    return [oneLineMode, splitReg, splitSz, sortID, position, ascending, widths, position2]

def extract_StuWareSoftSystems_version(theVersionToCheck):

    _MAJOR = 0
    _MINOR = 1

    theVersionToCheck = str(theVersionToCheck).strip()

    if len(theVersionToCheck) < 1: return [0,0]

    if len(theVersionToCheck) == 1: return [int(theVersionToCheck),0]

    if "." in theVersionToCheck:
        x = theVersionToCheck.split(".")
        return [int(x[0]),x[1]]

    major = minor = ""

    for char in theVersionToCheck:
        if (not minor) and (char >= "0" and char <= "9"): # noqa
            major += char
            continue
        minor+=char

    if debug:
        myPrint("D","Decoded: %s.%s" %(major,minor))

    try:
        return [int(major),minor]
    except:
        return [0,0]

def check_for_updatable_extensions_on_startup(statusLabel):
    global lIgnoreOutdatedExtensions_TB

    displayData = "\nStuWareSoftSystems: ALERT INFORMATION ABOUT YOUR EXTENSIONS:\n\n"

    try:
        theUpdateList = get_extension_update_info()

        if not theUpdateList or len(theUpdateList)<1:
            return

        for key in theUpdateList.keys():
            updateInfo = theUpdateList[key]
            displayData+="** UPGRADEABLE EXTENSION: %s to version: %s\n" %(pad(key,20),str(updateInfo[0].getBuild()))
            myPrint("B", "** UPGRADEABLE EXTENSION: %s to version: %s" %(pad(key,20),str(updateInfo[0].getBuild())))
    except:
        dump_sys_error_to_md_console_and_errorlog()
        return

    displayData+="\n<END>\n"

    howMany = int(len(theUpdateList))

    if not lIgnoreOutdatedExtensions_TB:
        statusLabel.setText( ("ALERT - YOU HAVE %s EXTENSION(S) THAT CAN BE UPGRADED!..." %howMany ).ljust(800, " "))
        statusLabel.setForeground(Color.BLUE)
        jif = QuickJFrame("StuWareSoftSystems - EXTENSIONS ALERT!", displayData, 1).show_the_frame()
        options=["OK (keep reminding me)","OK - DON'T TELL ME AGAIN ON STARTUP!"]
        response = JOptionPane.showOptionDialog(jif,
                                                "INFO: You have %s older Extensions that can be upgraded" %howMany,
                                                "OUTDATED EXTENSIONS",
                                                0,
                                                JOptionPane.QUESTION_MESSAGE,
                                                None,
                                                options,
                                                options[0])

        if response:
            myPrint("B","User requested to ignore Outdated warning extensions going forward..... I will obey!!")
            lIgnoreOutdatedExtensions_TB = True
    else:
        statusLabel.setText( ("ALERT - YOU HAVE %s EXTENSION(S) THAT CAN BE UPGRADED!...STARTUP POPUP WARNINGS SUPPRESSED (by you)" %howMany ).ljust(800, " "))
        statusLabel.setForeground(Color.BLUE)

    return

def check_for_old_StuWareSoftSystems_scripts(statusLabel):
    global lPickle_version_warning, myParameters

    lVersionWarning = False

    if not myParameters and not lPickle_version_warning:
        return

    displayData = "\nStuWareSoftSystems: ALERT INFORMATION ABOUT SCRIPTS:\n\n"

    if lPickle_version_warning:
        displayData += "I detected an older (encrypted) version of saved parameter file for use with my Python scripts\n"
        displayData += "No problem, I have updated / converted it.\n\n"

    _MAJOR = 0
    _MINOR = 1
    iCountOldScripts = 0

    if myParameters:

        for key in sorted(myParameters.keys()):
            if key.startswith("__") and key != "__Author":
                myPrint("DB","Decoding old script versions for key: %s version_build: %s" %(key,myParameters[key]))
                theVersion = extract_StuWareSoftSystems_version(myParameters[key])
                if key == "__extract_currency_history_csv":
                    if theVersion[_MAJOR] <  1000:
                        pass
                    else: continue
                elif key == "__StockGlance2020":
                    if theVersion[_MAJOR] <  1000:
                        pass
                    else: continue
                elif key == "__extract_reminders_to_csv":     # Old key - renamed... but see if it's around....
                    if theVersion[_MAJOR] <  1000:
                        pass
                    else: continue
                elif key == "__extract_reminders_csv":
                    if theVersion[_MAJOR] <  1000:
                        pass
                    else: continue
                elif key == "__extract_investment_transactions":
                    if theVersion[_MAJOR] <  1000:
                        pass
                    else: continue
                else: continue
                displayData+="ALERT: Script: %s is out of date - you have version_build: %s_%s\n" %(key,theVersion[_MAJOR],theVersion[_MINOR])
                myPrint("DB", "Script %s is out of date - PLEASE UPDATE"%key)
                iCountOldScripts+=1
                lVersionWarning = True


    if lPickle_version_warning or lVersionWarning:
        displayData+="""
\nCURRENT SCRIPT VERSIONS ARE:
StockGlance2020.py:                     1000
extract_currency_history_csv.py:        1000
extract_reminders_csv.py:               1000
extract_investment_transactions_csv.py: 1000
Toolbox.py:                             1000
\nPlease update any that you use to at least these versions listed above....\n
        """

        jif = QuickJFrame("StuWareSoftSystems - Scripts alert!", displayData, 1).show_the_frame()

        statusLabel.setText( ("PLEASE UPDATE OLDER VERSIONS OF STUWARESOFTSYSTEMS SCRIPTS!...").ljust(800, " "))
        statusLabel.setForeground(Color.BLUE)

        myPopupInformationBox(jif, "You have %s older StuWareSoftSystems scripts - please upgrade them!" % iCountOldScripts, "STUWARESOFTSYSTEMS' SCRIPTS", JOptionPane.WARNING_MESSAGE)

    return

def find_the_program_install_dir():

    theDir = ""

    if Platform.isOSX():
        # Derive from these - not great, but OK: java.home, java.library.path, sun.boot.library.path

        test = System.getProperty("java.home").strip()
        _i = test.lower().find(".app/")                                                                             # noqa
        if _i > 0:
            theDir = test[:_i+4]
    else:
        theDir = System.getProperty("install4j.exeDir").strip()

    if not os.path.exists(theDir):
        theDir = ""

    return theDir


def get_orphaned_extension():

    extension_prefs = moneydance_ui.getPreferences().getTableSetting("gen.fmodules",StreamTable())

    # Get all keys in config dict
    st,tk = read_preferences_file(lSaveFirst=True)  # Must flush memory to disk first before we read the file....
    confirmed_extn_keys = {}
    for theKey in tk:
        if not theKey.lower().startswith("confirmedext."):
            continue    # skip
        confirmed_extn_keys[theKey.split('.')[1].lower().strip()]  = theKey

    outdated={}
    x = moneydance.getOutdatedExtensionIDs()
    for y in x: outdated[y.lower().strip()] = True

    ok={}
    x = moneydance.getLoadedModules()
    for y in x: ok[str(y.getIDStr()).lower().strip()] = True
    x = moneydance.getSuppressedExtensionIDs()
    for y in x: ok[str(y).lower().strip()] = True

    orphan_outdated_prefs = {}
    for extn_pref in extension_prefs:
        if not ok.get(extn_pref.lower().strip()) and not outdated.get(extn_pref.lower().strip()):
            orphan_outdated_prefs[extn_pref] = "ORPHAN"
        elif outdated.get(extn_pref.lower().strip()):
            orphan_outdated_prefs[extn_pref] = "OUTDATED"

    orphan_confirmed_extn_keys = {}
    for extn_pref in confirmed_extn_keys:
        if not ok.get(extn_pref.lower().strip()) and not outdated.get(extn_pref.lower().strip()):
            orphan_confirmed_extn_keys[extn_pref] = ["ORPHAN",confirmed_extn_keys.get(extn_pref.lower().strip())]
        elif outdated.get(extn_pref.lower().strip()):
            orphan_confirmed_extn_keys[extn_pref] = ["OUTDATED",confirmed_extn_keys.get(extn_pref.lower().strip())]

    orphan_outdated_files={}
    extn_files_found=[]

    extensionDir = Common.getFeatureModulesDirectory()
    if extensionDir:
        # noinspection PyTypeChecker
        for root, dirs, files in os.walk(extensionDir.getAbsolutePath()):
            for filename in files:
                for extn in ModuleLoader.FEATURE_MODULE_EXTENSIONS:
                    if filename.endswith("."+extn):
                        # got an Extension
                        extn_files_found.append([os.path.splitext(filename)[0].lower().strip(),filename])
                        pass

    for extn_file in extn_files_found:
        if not ok.get(extn_file[0]):
            if outdated.get(extn_file[0]):
                orphan_outdated_files[extn_file[0]] = ["OUTDATED",extn_file[1]]
            else:
                orphan_outdated_files[extn_file[0]] = ["ORPHAN",extn_file[1]]

    myPrint("DB","OK Extensions:", ok)
    myPrint("DB","OUTDATED: Extensions:", outdated)
    myPrint("DB","ORPHAN/OUTDATED Extension Preferences:", orphan_outdated_prefs)
    myPrint("DB","ORPHAN/OUTDATED Extension Files:", orphan_outdated_files)
    return [orphan_outdated_prefs, orphan_outdated_files, orphan_confirmed_extn_keys]

def diagnose_currencies(statusLabel, lFix=False):
    global Toolbox_frame_, debug, fixRCurrencyCheck, DARK_GREEN
    myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )

    if lFix:
        myPrint("B", "Script running to FIX your relative currencies...............")
        myPrint("P", "---------------------------------------------------------")
    else:
        myPrint("B", "Script running to diagnose your relative currencies...............")
        myPrint("P", "---------------------------------------------------------")

    if moneydance_data is None:
        statusLabel.setText(("No data to scan - aborting..").ljust(800, " "))
        statusLabel.setForeground(Color.RED)
        return

    if lFix:
        if not fixRCurrencyCheck:
            statusLabel.setText(("Sorry, you must run 'DIAG: Diagnose Currencies' first!").ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            return
        elif fixRCurrencyCheck == 1:
            statusLabel.setText(
                ("'DIAG: Diagnose Currencies' reported no issues - so I will not run fixes").ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            return
        elif fixRCurrencyCheck == 2:
            if not myPopupAskQuestion(Toolbox_frame_,
                                      "FIX RELATIVE CURRENCIES",
                                      "'DIAG: Diagnose Currencies' reported only warnings; Are you sure you want to FIX Relative Currencies?",
                                      JOptionPane.YES_NO_OPTION,
                                      JOptionPane.WARNING_MESSAGE):

                statusLabel.setText(("'DIAG: Diagnose Currencies' reported only warnings and user declined to proceed - no fixes applied!").ljust(800, " "))
                statusLabel.setForeground(Color.RED)
                return

        elif fixRCurrencyCheck != 3:
            statusLabel.setText(("LOGIC ERROR reviewing 'DIAG: Diagnose Currencies' - so I will not run fixes").ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            return

        if not myPopupAskQuestion(Toolbox_frame_,
                                  "FIX RELATIVE CURRENCIES",
                                  "OK - Are you sure you want to FIX Relative Currencies?",
                                  JOptionPane.YES_NO_OPTION,
                                  JOptionPane.ERROR_MESSAGE):

            statusLabel.setText(("'FIX: Relative Currencies' user declined to proceed - no fixes applied!").ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            return

        if not myPopupAskBackup(Toolbox_frame_, "Would you like to perform a backup before FIXING RELATIVE CURRENCIES?"):
            statusLabel.setText(("'FIX: Relative Currencies' - User chose to exit without the fix/update....").ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            return

        disclaimer = myPopupAskForInput(Toolbox_frame_,
                                        "FIX RELATIVE CURRENCIES",
                                        "DISCLAIMER:",
                                        "Are you really sure you want to FIX Relative Currencies? Type 'IAGREE' to continue..",
                                        "NO",
                                        False,
                                        JOptionPane.ERROR_MESSAGE)

        if not disclaimer == 'IAGREE':
            statusLabel.setText("User declined the disclaimer - no changes made....".ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            return

        # OK - let's do it!
        fixRCurrencyCheck = None

    lNeedFixScript = False
    iWarnings = 0

    currencies = moneydance_data.getCurrencies()
    baseCurr = currencies.getBaseType()

    output = ""
    output += "Analysing the Base currency setup....\n"
    output += "Base currency: %s\n" % baseCurr

    if not baseCurr.getDoubleParameter("rrate", 1.0) == 1.0:
        myPrint("J", "ERROR - base currency has non-identity relative rate (rrate): " + str(
            baseCurr.getParameter("rrate", "null")))
        output += "ERROR - base currency has non-identity relative rate (rrate): " + str(
            baseCurr.getParameter("rrate", "null")) + "\n"
        lNeedFixScript = True
        if lFix:
            baseCurr.setParameter("rrate", 1.0)
            myPrint("J", "@@CURRENCY FIX APPLIED@@")
            output += "\n@@CURRENCY FIX APPLIED@@\n"

    if not baseCurr.getDoubleParameter("rate", 1.0) == 1.0:
        myPrint("J", "ERROR - base currency has non-identity rate: " + str(baseCurr.getParameter("rate", "null")))
        output += "ERROR - base currency has non-identity rate: " + str(baseCurr.getParameter("rate", "null")) + "\n"
        lNeedFixScript = True
        if lFix:
            baseCurr.setParameter("rate", 1.0)
            myPrint("J", "@@CURRENCY FIX APPLIED@@")
            output += "\n@@CURRENCY FIX APPLIED@@\n"

    if lFix and lNeedFixScript:
        baseCurr.syncItem()

    if not lNeedFixScript:
        output += ("Base currency has Rate (rate) of: %s and Relative Rate (rrate): of %s.  This is Correct...\n"
                   % (baseCurr.getParameter("rate", "null"), baseCurr.getParameter("rrate", "null")))

    baseSnapshots = baseCurr.getSnapshots()
    if baseSnapshots.size() > 0:
        lNeedFixScript = True
        myPrint("J",
                "ERROR: base currency has %s historical prices! These need to be deleted!" % (baseSnapshots.size()))
        output += "ERROR: base currency has %s historical prices! These need to be deleted!\n" % (baseSnapshots.size())
        for baseSnapshot in baseSnapshots:
            if lFix:
                output += "  @@DELETING@@: %s\n" % (baseSnapshot)
                baseSnapshot.deleteItem()
            else:
                output += "  snapshot: %s\n" % baseSnapshot
    else:
        output += "Base currency has no historical prices. This is correct\n"

    root = moneydance_data.getRootAccount()
    if root.getCurrencyType() != baseCurr:
        lNeedFixScript = True

        myPrint("J", "Root account's currency: %s, Base currency: %s" % (root.getCurrencyType(), baseCurr))
        output += "Root account's currency: %s, Base currency: %s\n" % (root.getCurrencyType(), baseCurr)

        myPrint("J", "ERROR - The root account's currency is not set to base! This needs correcting!")
        output += "ERROR - The root account's currency is not set to base! This needs correcting!\n"

        if lFix:
            root.setCurrencyType(baseCurr)
            root.syncItem()
            myPrint("J", "@@CURRENCY FIX APPLIED@@")
            output += "\n@@CURRENCY FIX APPLIED@@\n"

    else:
        output += "Good, the root account's currency is set to the base currency! Root: %s, Base: %s\n" % (root.getCurrencyType(), baseCurr)

    currencies = sorted(currencies, key=lambda x: str(x.getName()).upper())

    lWarning = False
    output += "\nAnalysing the currency table...\n"
    for curr in currencies:
        # noinspection PyUnresolvedReferences
        if curr.getCurrencyType() == CurrencyType.Type.SECURITY:
            continue
        output += "\nChecking currency: %s\n" % curr
        getRelative = curr.getParameter("relative_to_currid")
        if getRelative:
            getRelative = str(getRelative)
        else:
            getRelative = str(getRelative)+" (this is OK and means the Base Rate will be used)"
        output += "relative_to_currid: " + getRelative + "\n"
        if curr.getParameter("relative_to_currid") is not None and curr.getParameter(
                "relative_to_currid") != baseCurr.getParameter("currid"):
            lWarning = True
            iWarnings += 1

            myPrint("J", "WARNING: %s relative_to_currid should be set to None or your base currency!" % curr)
            output += "WARNING: %s relative_to_currid should be set to None or your base currency!\n" % curr

            if lFix:
                curr.setParameter("relative_to_currid", None)
                curr.syncItem()
                myPrint("J", "@@CURRENCY FIX APPLIED@@")
                output += "\n@@CURRENCY FIX APPLIED@@\n"

        output += "Rate: %s (inverted: %s)\n" % (curr.getParameter("rate", "null"), 1 / float(curr.getParameter("rate", "null")))

        if curr.getParameter("rrate", None) is not None:
            output += "Relative Rate: %s (inverted: %s)\n" % (curr.getParameter("rrate", None), 1 / float(curr.getParameter("rrate", None)))

        if not lFix:
            output += "  details:\n"
            output += "\t" + "ID: " + str(curr.getID()) + "\n"
            output += "\t" + "Name: " + str(curr.getName()) + "\n"
            output += "\t" + "Ticker: " + str(curr.getTickerSymbol()) + "\n"
            output += "\t" + "Is Base: " + str(curr == baseCurr) + "\n"
            output += "\t" + "Curr_ID: " + str(curr.getIDString()) + "\n"
            output += "\t" + "Decimal Places: " + str(curr.getDecimalPlaces()) + "\n"
            output += "\t" + "Hide in UI: " + str(curr.getHideInUI()) + "\n"
            output += "\t" + "Effective Date: " + str(curr.getEffectiveDateInt()) + "\n"
            output += "\t" + "Prefix: " + str(curr.getPrefix()) + "\n"
            output += "\t" + "Suffix: " + str(curr.getSuffix()) + "\n"

            output += "  pricing history:\n"
            currSnapshots = curr.getSnapshots()
            if currSnapshots.size() > 0:
                i = 0
                for currSnapshot in reversed(currSnapshots):
                    i += 1
                    output += "  snapshot: %s (reversed: %s)\n" % (currSnapshot, currSnapshot.getRate())
                    if i > 5:
                        output += "  stopping after 5 price history records, but more does exist...\n"
                        break
            else:
                if curr != baseCurr:
                    output += "  This currency has no historical prices? Is this correct?\n"
                else:
                    output += "  This currency has no historical prices...\n"

    output += "-----------------------------------------------------------------\n"
    if lFix:
        fixRCurrencyCheck = None
        myPrint("B", ">> Currency errors / warning detected - FIXES APPLIED..")
        output += "\nRELEVANT FIXES APPLIED\n\n"
        output += "\nDISCLAIMER: I take no responsibility for the execution of this currency fix script\n"
        statusLabel.setText(("RELATIVE CURRENCY FIXES APPLIED - Please review diagnostic report for details!").ljust(800, " "))
        statusLabel.setForeground(Color.RED)

    else:
        if lNeedFixScript:
            fixRCurrencyCheck = 3
            myPrint("B", ">> Currency errors detected - Possible use of reset_relative_currencies.py script required..!?")
            output += " >> Currency errors detected - Possible use of reset_relative_currencies.py script required..!?\n"
            output += "\nERROR: You have currency errors..\n"
            output += "Please discuss details with support and potentially run the FIX Relative Currencies option (based on reset_relative_currencies.py from support)\n"
            output += "DISCLAIMER: Always backup your data before running change scripts. I can take no responsibility for the execution of said script\n"
            statusLabel.setText(("ERROR: You have currency errors.. Please review diagnostic report!").ljust(800, " "))
            statusLabel.setForeground(Color.RED)
        elif lWarning:
            fixRCurrencyCheck = 2
            myPrint("B", "You have %s Warning(s).." % iWarnings)
            output += "You have %s Warning(s)..\n" % iWarnings
            output += "These are where your currency records show a relative currency that's not None or the base currency...; I believe this to be a data error!\n"
            output += "If you are seeing currency problems, then discuss with support and potentially run the FIX Relative Currencies option (based on reset_relative_currencies.py from support)\n"
            output += "This would reset your relative currency back to None...\n"
            output += "DISCLAIMER: Always backup your data before running change scripts. I can take no responsibility for the execution of said script\n"
            statusLabel.setText(
                ("ERROR: You have currency warnings.. Please review diagnostic report!").ljust(800, " "))
            statusLabel.setForeground(Color.RED)
        else:
            fixRCurrencyCheck = 1
            myPrint("J", "All good, currencies look clean! Congratulations!")
            output += "\nAll good, currencies look clean! Congratulations!\n"
            statusLabel.setText(("All good, currencies look clean! Congratulations!").ljust(800, " "))
            statusLabel.setForeground(DARK_GREEN)

    output += "\n<END>"

    myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

    return output

class BackupButtonAction(AbstractAction):
    theString = ""

    def __init__(self, statusLabel, theQuestion):
        self.statusLabel = statusLabel
        self.theQuestion = theQuestion

    def actionPerformed(self, event):
        global Toolbox_frame_, debug
        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

        if myPopupAskQuestion(Toolbox_frame_,
                                  "PERFORM BACKUP",
                              self.theQuestion,
                              JOptionPane.YES_NO_OPTION,
                              JOptionPane.WARNING_MESSAGE):


            myPrint("J", "User requested to perform Export Backup")
            moneydance_ui.saveToBackup(None)
            play_the_money_sound()

            self.statusLabel.setText(("Backup created as requested..").ljust(800, " "))
            self.statusLabel.setForeground(Color.RED)
        else:
            self.statusLabel.setText(("User declined to create backup..").ljust(800, " "))
            self.statusLabel.setForeground(Color.RED)

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
        return

def backup_custom_theme_file():

    # noinspection PyUnresolvedReferences
    themeFile = theme.Theme.customThemeFile

    newFileName = os.path.splitext(themeFile.getName())[0]+get_filename_addition()+os.path.splitext(themeFile.getName())[1]+"_$SAVED$"
    newFile = File(themeFile.getParent(), newFileName)

    try:
        IOUtils.copy(themeFile, newFile)
        myPrint("B", "Custom theme file: backup / copied to %s prior to deletion...."%newFileName)
        return True
    except:
        myPrint("B", "Error: Failed to backup/copy custom theme file prior to deletion....")
        dump_sys_error_to_md_console_and_errorlog()

    return False

def backup_local_storage_settings( lSaveFirst=True ):

    if lSaveFirst:
        moneydance_data.getLocalStorage().save()  # Flush settings to disk before changes

    # I would rather have called LocalStorage() to get the filepath, but it doesn't give the path
    # NOTE  - This backup copy will be encrypted, so you can just put it back to ./safe/settings.
    localStorage_file = File(os.path.join(moneydance_data.getRootFolder().getAbsolutePath(),"safe","settings"))
    copy_localStorage_filename = os.path.join(moneydance_data.getRootFolder().getAbsolutePath(),"settings")

    try:
        newFileName = copy_localStorage_filename+get_filename_addition()+"_$SAVED$"
        newFile = File(newFileName)

        IOUtils.copy(localStorage_file, newFile)
        myPrint("B", "LocalStorage() ./safe/settings copied to %s prior to any changes...."%newFileName)
        return True

    except:
        myPrint("B","@@ ERROR - failed to copy LocalStorage() ./safe/settings prior to any changes!?")
        dump_sys_error_to_md_console_and_errorlog()

    return False

def backup_config_dict( lSaveFirst=True ):

    if lSaveFirst:
        moneydance.savePreferences()  # Flush settings to disk before copy

    try:
        configFile = Common.getPreferencesFile()
        newFileName = os.path.splitext(configFile.getName())[0]+get_filename_addition()+os.path.splitext(configFile.getName())[1]+"_$SAVED$"
        newFile = File(configFile.getParent(), newFileName)

        IOUtils.copy(configFile, newFile)
        myPrint("B", "config.dict backup/copy made to %s prior to changes...."%newFileName)
        return True
    except:
        myPrint("B","@@ ERROR - failed to backup/copy config.dict prior to changes!?")
        dump_sys_error_to_md_console_and_errorlog()

    return False


class CloseAction(AbstractAction):

    def __init__(self, theFrame):
        self.theFrame = theFrame

    def actionPerformed(self, event):                                                                           # noqa
        global debug
        myPrint("D","In ", inspect.currentframe().f_code.co_name, "()")

        self.theFrame.dispose()
        return


def about_this_script():
    global Toolbox_frame_, debug, scriptExit

    myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

    # noinspection PyUnresolvedReferences
    about_d = JDialog(Toolbox_frame_, "About", Dialog.ModalityType.MODELESS)

    shortcut = Toolkit.getDefaultToolkit().getMenuShortcutKeyMaskEx()
    about_d.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_W, shortcut), "close-window")
    about_d.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_F4, shortcut), "close-window")
    about_d.getRootPane().getActionMap().put("close-window", CloseAction(about_d))

    about_d.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE)  # The CloseAction() and WindowListener() will handle dispose() - else change back to DISPOSE_ON_CLOSE

    if (not Platform.isMac()):
        # moneydance_ui.getImages()
        about_d.setIconImage(MDImages.getImage(moneydance_ui.getMain().getSourceInformation().getIconResource()))

    aboutPanel=JPanel()
    aboutPanel.setLayout(FlowLayout(FlowLayout.LEFT))
    aboutPanel.setPreferredSize(Dimension(1070, 400))

    _label1 = JLabel(pad("Author: Stuart Beesley", 800))
    _label1.setForeground(Color.BLUE)
    aboutPanel.add(_label1)

    _label2 = JLabel(pad("StuWareSoftSystems (2020)", 800))
    _label2.setForeground(Color.BLUE)
    aboutPanel.add(_label2)

    displayString=scriptExit
    displayJText = JTextArea(displayString)
    displayJText.setFont( getMonoFont() )
    displayJText.setEditable(False)
    # displayJText.setCaretPosition(0)
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
    return


def terminate_script():
    global debug, Toolbox_frame_, lGlobalErrorDetected

    myPrint("D","In ", inspect.currentframe().f_code.co_name, "()")

    try:
        save_StuWareSoftSystems_parameters_to_file()
    except:
        myPrint("B", "Error - failed to save parameters to pickle file...!")
        dump_sys_error_to_md_console_and_errorlog()

    if not i_am_an_extension_so_run_headless: print(scriptExit)

    Toolbox_frame_.dispose()
    return

class DiagnosticDisplay():
    def __init__(self):
        pass

    class WindowListener(WindowAdapter):

        def __init__(self):
            pass

        def windowClosing(self, WindowEvent):                                                                       # noqa
            global debug, Toolbox_frame_

            myPrint("D","In ", inspect.currentframe().f_code.co_name, "()")

            myPrint("DB", "DiagnosticDisplay() Frame shutting down....")

            terminate_script()

    class CloseAction(AbstractAction):

        def __init__(self, theFrame):
            self.theFrame = theFrame

        def actionPerformed(self, event):                                                                           # noqa
            global debug, Toolbox_frame_
            myPrint("D","In ", inspect.currentframe().f_code.co_name, "()")

            myPrint("DB", "DiagnosticDisplay() Frame shutting down....")

            terminate_script()

            return

    class HackerModeButtonAction(AbstractAction):

        def __init__(self, statusLabel):
            self.statusLabel = statusLabel

        def actionPerformed(self, event):
            global Toolbox_frame_, debug, DARK_GREEN, lCopyAllToClipBoard_TB
            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

            if moneydance_data is None:
                self.statusLabel.setText(("No data to Hack with - aborting..").ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            _HACKCONFIGADD          = 0
            _HACKCONFIGCHG          = 1
            _HACKCONFIGDEL          = 2
            _HACKLOCALSTORAGEADD    = 3
            _HACKLOCALSTORAGECHG    = 4
            _HACKLOCALSTORAGEDEL    = 5

            what = [
                "HACK: config.dict ADD setting",
                "HACK: config.dict CHANGE setting",
                "HACK: config.dict DELETE setting",
                "HACK Local Storage Setting ADD setting",
                "HACK Local Storage Setting CHANGE setting",
                "HACK Local Storage Setting DELETE setting"
            ]

            while True:

                lAdd = lChg = lDel = False
                lConfigDict = lLocalStorage = False

                # noinspection PyUnusedLocal
                LS = st = tk = prefs = fileType = None

                selectedWhat = JOptionPane.showInputDialog(Toolbox_frame_, "HACKER",
                                                           "Select the Key data / option for the Hack",
                                                           JOptionPane.WARNING_MESSAGE,
                                                           None,
                                                           what,
                                                           None)

                if not selectedWhat:
                    self.statusLabel.setText(("Thank you for using HACKER MODE!..").ljust(800, " "))
                    self.statusLabel.setForeground(Color.BLUE)
                    return

                if selectedWhat == what[_HACKCONFIGADD]: lAdd = True
                if selectedWhat == what[_HACKCONFIGCHG]: lChg = True
                if selectedWhat == what[_HACKCONFIGDEL]: lDel = True
                if selectedWhat == what[_HACKLOCALSTORAGEADD]: lAdd = True
                if selectedWhat == what[_HACKLOCALSTORAGECHG]: lChg = True
                if selectedWhat == what[_HACKLOCALSTORAGEDEL]: lDel = True

                if selectedWhat == what[_HACKCONFIGADD]: lConfigDict = True
                if selectedWhat == what[_HACKCONFIGCHG]: lConfigDict = True
                if selectedWhat == what[_HACKCONFIGDEL]: lConfigDict = True
                if selectedWhat == what[_HACKLOCALSTORAGEADD]: lLocalStorage = True
                if selectedWhat == what[_HACKLOCALSTORAGECHG]: lLocalStorage = True
                if selectedWhat == what[_HACKLOCALSTORAGEDEL]: lLocalStorage = True

                LS = moneydance_ui.getCurrentAccounts().getBook().getLocalStorage()

                if lConfigDict:
                    fileType = "config.dict"
                    st,tk = read_preferences_file(lSaveFirst=True)  # Must flush memory to disk first before we read the file....
                    prefs=sorted(tk)
                elif lLocalStorage:
                    fileType = "LocalStorage() ./safe/settings"
                    ls_keys = LS.keys()
                    prefs=sorted(ls_keys)
                else:
                    raise(Exception("ERROR - Unknown type!"))

                text = ""
                if lChg: text = "CHANGE"
                if lDel: text = "DELETE"

                if lAdd:
                    addKey = myPopupAskForInput(Toolbox_frame_,
                                                "HACKER: ADD KEY TO %s" % fileType,
                                                "KEY NAME:",
                                                "Carefully enter the name of the key you want to add (cAseMaTTers!) - STRINGS ONLY:",
                                                "",
                                                False,
                                                JOptionPane.WARNING_MESSAGE)

                    if not addKey or len(addKey) < 1: continue
                    addKey = addKey.strip()

                    if not check_if_key_string_valid(addKey):
                        myPopupInformationBox(Toolbox_frame_, "ERROR: Key %s is NOT valid!" % addKey, "HACKER: ADD TO %s" % fileType, JOptionPane.ERROR_MESSAGE)
                        continue    # back to Hacker menu

                    testKeyExists = True
                    if lConfigDict:     testKeyExists = moneydance_ui.getPreferences().getSetting(addKey,None)
                    if lLocalStorage:   testKeyExists = LS.get(addKey)

                    if testKeyExists:
                        myPopupInformationBox(Toolbox_frame_, "ERROR: Key %s already exists - cannot add - aborting..!" % addKey, "HACKER: ADD TO %s" % fileType, JOptionPane.ERROR_MESSAGE)
                        continue    # back to Hacker menu

                    addValue = myPopupAskForInput(Toolbox_frame_,
                                                "HACKER: ADD KEY VALUE TO %s" % fileType,
                                                "KEY VALUE:",
                                                "Carefully enter the key value you want to add (STRINGS ONLY!):",
                                                "",
                                                  False,
                                                  JOptionPane.WARNING_MESSAGE)

                    if not addValue or len(addValue) <1: continue
                    addValue = addValue.strip()

                    if not check_if_key_string_valid(addValue):
                        myPopupInformationBox(Toolbox_frame_, "ERROR: Key value %s is NOT valid!" % addValue, "HACKER: ADD TO %s" % fileType, JOptionPane.ERROR_MESSAGE)
                        continue    # back to Hacker menu

                    disclaimer = myPopupAskForInput(Toolbox_frame_,
                                                    "HACKER: ADD KEY VALUE TO %s" % fileType,
                                                    "DISCLAIMER:",
                                                    "Type 'IAGREE' to add key: %s with value: %s" % (addKey,addValue),
                                                    "NO",
                                                    False,
                                                    JOptionPane.ERROR_MESSAGE)
                    if disclaimer == "IAGREE":
                        if lConfigDict:
                            moneydance_ui.getPreferences().setSetting(addKey,addValue)
                            moneydance.savePreferences()                # Flush all in memory settings to config.dict file on disk
                        if lLocalStorage:
                            LS.put(addKey,addValue)
                            LS.save()    # Flush local storage to safe/settings

                        play_the_money_sound()
                        myPrint("B","@@ HACKERMODE: key: %s value: %s added to %s @@" %(addKey,addValue,fileType))
                        myPopupInformationBox(Toolbox_frame_,
                                              "SUCCESS: Key %s added to %s!" % (addKey,fileType),
                                              "HACKER: ADD TO %s" % fileType,
                                              JOptionPane.WARNING_MESSAGE)
                        continue

                    myPopupInformationBox(Toolbox_frame_, "NO CHANGES MADE!", "HACKER", JOptionPane.INFORMATION_MESSAGE)
                    continue

                # OK, so we are changing or deleting
                if lChg or lDel:
                    selectedKey = JOptionPane.showInputDialog(Toolbox_frame_, "HACKER",
                                                                "Select the %s key/setting you want to %s" % (fileType,text),
                                                              JOptionPane.WARNING_MESSAGE,
                                                              None,
                                                              prefs,
                                                              None)
                    if not selectedKey: continue

                    lOK_to_Change = False
                    value = None
                    if lConfigDict:
                        # value = moneydance_ui.getPreferences().getSetting(selectedKey)
                        value = st.get(selectedKey)   # Have to use the backdoor to maintain the real instance type

                    if lLocalStorage:
                        value = LS.get(selectedKey)
                        valueTest = LS.getString(selectedKey, "")

                        try:
                            # Is it a StreamTable?
                            valueTest_st = StreamTable()
                            valueTest_st.readFrom(valueTest)
                            value = valueTest_st
                        except:
                            # Is it a StreamVector?
                            valueTest_sv = StreamVector()
                            try:
                                valueTest_sv.readFrom(valueTest)
                                value = valueTest_sv
                            except:
                                pass

                    output =  "%s PLEASE REVIEW KEY & VALUE BEFORE MAKING CHANGES\n" %fileType
                    output += "%s------------------------------------------------\n\n" %("-"*len(fileType))

                    if isinstance(value,(StreamTable,StreamVector)) and lChg:
                        output += "\n@@ Sorry: StreamTable & StreamVector keys cannot be changed by this script (only deleted) @@\n"
                    elif not isinstance(value, (str, unicode)) and lChg:
                        output += "\n@@ Sorry: %s keys cannot be changed by this script (only deleted) @@\n" % type(value)
                    else:
                        lOK_to_Change = True
                        output += "\n@@ This '%s' key can be changed/deleted by this script @@\n" % selectedKey

                    output += "\n%s %s\n" %(pad("%s KEY:"%fileType,25),selectedKey)
                    output += "\n%s %s\n" %(pad("Type:",25), type(value))

                    if isinstance(value,(StreamTable,StreamVector)):
                        output += "\n%s\n%s\n" %("Value:", value)
                    else:
                        output += "\n%s %s\n" %(pad("Value:",25), value)

                    output += "\n<END>"
                    jif = QuickJFrame("REVIEW THE KEY BEFORE CHANGES to %s" %fileType, output).show_the_frame()

                    if lChg and not lOK_to_Change:
                        myPopupInformationBox(jif,
                                              "SORRY: I cannot change the key %s in %s" %(selectedKey,fileType),
                                              "HACKER: CHANGE KEY IN %s" %fileType,
                                              JOptionPane.ERROR_MESSAGE)
                        continue

                    chgValue = None

                    if lChg:
                        chgValue = myPopupAskForInput(jif,
                                                      "HACKER: CHANGE KEY VALUE IN %s" %(fileType),
                                                      "KEY VALUE:",
                                                      "Carefully enter the new key value (STRINGS ONLY!):",
                                                      value,
                                                      False,
                                                      JOptionPane.WARNING_MESSAGE)

                        if not chgValue or len(chgValue) <1 or chgValue == value: continue
                        chgValue = chgValue.strip()

                        if not check_if_key_string_valid(chgValue):
                            myPopupInformationBox(jif,"ERROR: Key value %s is NOT valid!" %chgValue,"HACKER: CHANGE IN %s" %fileType,JOptionPane.ERROR_MESSAGE)
                            continue    # back to Hacker menu

                    disclaimer = None
                    if lDel:
                        disclaimer = myPopupAskForInput(jif,
                                                        "HACKER: %s KEY VALUE IN %s" %(text,fileType),
                                                        "DISCLAIMER:",
                                                        "Type 'IAGREE' to %s key: %s (with old value: %s)" %(text,selectedKey,value),
                                                        "NO",
                                                        False,
                                                        JOptionPane.ERROR_MESSAGE)
                    if lChg:
                        disclaimer = myPopupAskForInput(jif,
                                                        "HACKER: %s KEY VALUE IN %s" %(text,fileType),
                                                        "DISCLAIMER:",
                                                        "Type 'IAGREE' to %s key: %s to new value: %s" %(text,selectedKey,chgValue),
                                                        "NO",
                                                        False,
                                                        JOptionPane.ERROR_MESSAGE)

                    if disclaimer == "IAGREE":
                        if lConfigDict:
                            if lDel:
                                moneydance_ui.getPreferences().setSetting(selectedKey,None)
                            if lChg:
                                moneydance_ui.getPreferences().setSetting(selectedKey,chgValue)
                            moneydance.savePreferences()            # Flush all in memory settings to config.dict file on disk
                        if lLocalStorage:
                            if lDel:
                                LS.put(selectedKey,None)
                            if lChg:
                                LS.put(selectedKey,chgValue)
                            LS.save()                               # Flush local storage to safe/settings

                        play_the_money_sound()

                        if lDel:
                            myPrint("B","@@ HACKERMODE: key: %s DELETED from %s (old value: %s) @@" %(selectedKey,fileType,value))
                            myPopupInformationBox(jif,
                                                  "SUCCESS: key: %s DELETED from %s (old value: %s)" %(selectedKey,fileType,value),
                                                  "HACKER: DELETE IN %s" %fileType,
                                                  JOptionPane.WARNING_MESSAGE)
                        if lChg:
                            myPrint("B","@@ HACKERMODE: key: %s CHANGED to %s in %s @@" %(selectedKey,chgValue, fileType))
                            myPopupInformationBox(jif,
                                                  "SUCCESS: key: %s CHANGED to %s in %s" %(selectedKey,chgValue, fileType),
                                                  "HACKER: CHANGE IN %s" %fileType,
                                                  JOptionPane.WARNING_MESSAGE)
                        continue

                    myPopupInformationBox(jif,"NO CHANGES MADE!", "HACKER", JOptionPane.INFORMATION_MESSAGE)
                    continue

            # ENDWHILE

            myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

            return

    class GeekOutModeButtonAction(AbstractAction):

        def __init__(self, statusLabel):
            self.statusLabel = statusLabel

        def actionPerformed(self, event):
            global Toolbox_frame_, debug, DARK_GREEN, lCopyAllToClipBoard_TB, lGeekOutModeEnabled_TB
            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )


            if moneydance_data is None:
                self.statusLabel.setText(("No data to Geek Out On - aborting..").ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            _SEARCH   = 0
            _ROOTKEYS = 1
            _BOOKKEYS = 2
            _PREFKEYS = 3
            _ACCTKEYS = 4
            _OBJKEYS  = 5
            _SYNCKEYS = 6
            _BANKKEYS = 7
            _SIZEKEYS = 8
            _OSPROPS  = 9
            _OSENV    = 10

            what = [
                    "Search for a key/data (in most places  - but not txns)",
                    "Show ROOT Account's Parameter Keys and data",
                    "Show Dataset's Local Storage Keys and data (from ./safe/settings)",
                    "Show All User Preferences loaded into Memory (from config.dict)",
                    "Show Accounts' Parameter's Keys and Data",
                    "Show an Obj's settings/data (Acct, Cat, Curr, Security, Reports, Reminders, Addrs, OFX, by UUID, TXNs)",
                    "Show All Sync Settings",
                    "Show All Online Banking (OFX) Settings",
                    "Show all Settings relating to Window Locations/Sizes/Widths/Sort Order/Filters/Initial Reg View etc..",
                    "Show all Operating 'System' Properties",
                    "Show all Operating System Environment Variables"]

            _OBJACCT        = 0
            _OBJCAT         = 1
            _OBJACCTSEC     = 2
            _OBJCURR        = 3
            _OBJSEC         = 4
            _OBJREMINDERS   = 5
            _REPORT_MEM     = 6
            _GRAPH_MEM      = 7
            _REPORT_DEF     = 8
            _GRAPH_DEF      = 9
            _OBJADDRESSES   = 10
            _OBJOFXONLINE   = 11
            _OBJBYUUID      = 12
            _OBJTRANSACTION = 13

            objWhat = [
                        "Account",
                        "Category",
                        "Security sub-account",
                        "Currency",
                        "Security",
                        "Reminders",
                        "Report (Memorized)",
                        "Graph (Memorized)",
                        "Report (Default)",
                        "Graph (Default)",
                        "Address Book Entry",
                        "Online OFX Services",
                        "Object by UUID",
                        "Object Transactions (by date)"
            ]

            selectedWhat = JOptionPane.showInputDialog(Toolbox_frame_, "GEEK OUT",
                                                         "Select the type of Key data you want to view",
                                                       JOptionPane.INFORMATION_MESSAGE,
                                                       moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                       what,
                                                       None)
            if not selectedWhat:
                self.statusLabel.setText(("No data type was selected to Geek out on..").ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            myPrint("J", "User has requested to view internal Moneydance Settings (Geek Out Mode): %s"%selectedWhat)

            lObject = False
            selectedObject = None                                                                               # noqa
            lReportDefaultsSelected = False

            root = moneydance.getCurrentAccountBook().getRootAccount()

            output = ""

            searchWhat = ""
            lSearch = lKeys = lKeyData = False
            if selectedWhat == what[_SEARCH]:
                lSearch = True

                selectedSearch = JOptionPane.showInputDialog(Toolbox_frame_, "GEEK OUT",
                                                              "SEARCH: Keys or Key Data?",
                                                             JOptionPane.INFORMATION_MESSAGE,
                                                             moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                             ["Keys","Key Data"],
                                                             None)
                if not selectedSearch:
                    self.statusLabel.setText(("No Search type selected (to Geek out on..)").ljust(800, " "))
                    self.statusLabel.setForeground(Color.RED)
                    return

                if selectedSearch == "Keys": lKeys = True
                elif selectedSearch == "Key Data": lKeyData = True
                else:
                    raise(Exception("ERROR: Unknown Geekout Search Key type selected!?"))

                searchWhat = myPopupAskForInput(Toolbox_frame_, "GEEK OUT: SEARCH", "%s:" % selectedSearch, "Enter the (partial) string to search for within %s..." % selectedSearch, "", False)
                if not searchWhat or searchWhat == "":
                    self.statusLabel.setText(("No Search data selected (to Geek out on..)").ljust(800, " "))
                    self.statusLabel.setForeground(Color.RED)
                    return
                searchWhat=searchWhat.strip()

            if selectedWhat == what[_OBJKEYS]:
                lObject = True

                selectedObjType = JOptionPane.showInputDialog(Toolbox_frame_, "GEEK OUT",
                                                              "Select the type of Object you want to view",
                                                              JOptionPane.INFORMATION_MESSAGE,
                                                              moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                              objWhat,
                                                              None)
                if not selectedObjType:
                    self.statusLabel.setText(("No Object type was selected to Geek out on..").ljust(800, " "))
                    self.statusLabel.setForeground(Color.RED)
                    return

                def getCurrTable(cType):

                    cTable=ArrayList()
                    myTable = moneydance.getCurrentAccountBook().getCurrencies()
                    for curr in myTable:
                        if curr.getCurrencyType() == cType:
                            cTable.add(curr)
                    return cTable

                def getReportsTable(memorized_default_or_all, report_or_graph_or_all):

                    theReports = None

                    repTable=ArrayList()
                    if report_or_graph_or_all == "ALL":
                        if memorized_default_or_all == "ALL":
                            return moneydance_data.getMemorizedItems().getAllItems()
                        elif memorized_default_or_all == "MEMORIZED":
                            return  moneydance_data.getMemorizedItems().getAllMemorizedItems()
                        elif memorized_default_or_all == "DEFAULT":
                            theReports = moneydance_data.getMemorizedItems().getAllItems()
                        else:
                            assert("ERROR - Report  type not defined: %s %s" %(memorized_default_or_all,report_or_graph_or_all))
                    elif report_or_graph_or_all == "REPORT":
                        if memorized_default_or_all == "ALL":
                            return moneydance_data.getMemorizedItems().getAllReports()
                        elif memorized_default_or_all == "MEMORIZED":
                            return  moneydance_data.getMemorizedItems().getMemorizedReports()
                        elif memorized_default_or_all == "DEFAULT":
                            theReports = moneydance_data.getMemorizedItems().getAllReports()
                        else:
                            assert("ERROR - Report  type not defined: %s %s" %(memorized_default_or_all,report_or_graph_or_all))
                    elif report_or_graph_or_all == "GRAPH":
                        if memorized_default_or_all == "ALL":
                            return moneydance_data.getMemorizedItems().getAllGraphs()
                        elif memorized_default_or_all == "MEMORIZED":
                            return  moneydance_data.getMemorizedItems().getMemorizedGraphs()
                        elif memorized_default_or_all == "DEFAULT":
                            theReports = moneydance_data.getMemorizedItems().getAllGraphs()
                        else:
                            assert("ERROR - Report  type not defined: %s %s" %(memorized_default_or_all,report_or_graph_or_all))
                    else:
                        assert("ERROR - Report  type not defined: %s %s" %(memorized_default_or_all,report_or_graph_or_all))

                    # For Default return non memorized Items
                    for rep in theReports:
                        if not rep.isMemorized():
                            repTable.add(rep)

                    return repTable

                baseCurr = moneydance_data.getCurrencies().getBaseType()

                objects = None
                try:
                    if objWhat.index(selectedObjType) == _OBJACCT:
                        objects = AccountUtil.allMatchesForSearch(moneydance_data, MyAcctFilter(7)).toArray()
                    elif objWhat.index(selectedObjType) == _OBJCAT:
                        objects = AccountUtil.allMatchesForSearch(moneydance_data, MyAcctFilter(8)).toArray()
                    elif objWhat.index(selectedObjType) == _OBJACCTSEC:
                        objects = AccountUtil.allMatchesForSearch(moneydance_data, MyAcctFilter(9)).toArray()
                    elif objWhat.index(selectedObjType) == _OBJCURR:
                        # noinspection PyUnresolvedReferences
                        objects = getCurrTable(CurrencyType.Type.CURRENCY)
                    elif objWhat.index(selectedObjType) == _OBJSEC:
                        # noinspection PyUnresolvedReferences
                        objects = getCurrTable(CurrencyType.Type.SECURITY)
                    elif objWhat.index(selectedObjType) == _REPORT_MEM:
                        objects = getReportsTable("MEMORIZED", "REPORT")
                        objects = sorted(objects, key=lambda x: (x.isMemorized(), x.getName().upper()))
                    elif objWhat.index(selectedObjType) == _GRAPH_MEM:
                        objects = getReportsTable("MEMORIZED", "GRAPH")
                        objects = sorted(objects, key=lambda x: (x.isMemorized(), x.getName().upper()))
                    elif objWhat.index(selectedObjType) == _REPORT_DEF:
                        lReportDefaultsSelected = True
                        objects = getReportsTable("DEFAULT", "REPORT")
                        objects = sorted(objects, key=lambda x: (x.isMemorized(), x.getName().upper()))
                    elif objWhat.index(selectedObjType) == _GRAPH_DEF:
                        lReportDefaultsSelected = True
                        objects = getReportsTable("DEFAULT", "GRAPH")
                        objects = sorted(objects, key=lambda x: (x.isMemorized(), x.getName().upper()))
                    elif objWhat.index(selectedObjType) == _OBJREMINDERS:
                        root = moneydance.getCurrentAccountBook()
                        objects = root.getReminders().getAllReminders()
                        objects = sorted(objects, key=lambda x: (x.getDescription().upper()))
                    elif objWhat.index(selectedObjType) == _OBJADDRESSES:
                        root = moneydance.getCurrentAccountBook()
                        objects = root.getAddresses().getAllEntries()
                        objects = sorted(objects, key=lambda x: (x.getName().upper()))
                    elif objWhat.index(selectedObjType) == _OBJOFXONLINE:
                        objects = moneydance_data.getOnlineInfo().getAllServices()
                        objects = sorted(objects, key=lambda x: (x.getFIName().upper()))
                    elif objWhat.index(selectedObjType) == _OBJBYUUID:
                        pass
                    elif objWhat.index(selectedObjType) == _OBJTRANSACTION:
                        pass
                    else:
                        self.statusLabel.setText(("Error selecting Object Type!?").ljust(800, " "))
                        self.statusLabel.setForeground(Color.RED)
                        return
                except:
                    dump_sys_error_to_md_console_and_errorlog( True )


                if objWhat.index(selectedObjType) == _OBJTRANSACTION:

                    dateStart = 20201231
                    dateEnd = 20201231

                    labelDateStart = JLabel("Date range start (enter as yyyy/mm/dd):")
                    user_selectDateStart = JDateField(CustomDateFormat("ymd"),15)   # Use MD API function (not std Python)
                    user_selectDateStart.setDateInt(dateStart)

                    labelDateEnd = JLabel("Date range end (enter as yyyy/mm/dd):")
                    user_selectDateEnd = JDateField(CustomDateFormat("ymd"),15)   # Use MD API function (not std Python)
                    user_selectDateEnd.setDateInt(dateEnd)

                    datePanel = JPanel(GridLayout(8, 2))
                    datePanel.add(labelDateStart)
                    datePanel.add(user_selectDateStart)

                    datePanel.add(labelDateEnd)
                    datePanel.add(user_selectDateEnd)

                    options = ["Cancel", "OK"]

                    while True:
                        userAction = JOptionPane.showOptionDialog(Toolbox_frame_,
                                                                  datePanel,
                                                                  "Select Date Range for TXNs (less is better)",
                                                                  JOptionPane.OK_CANCEL_OPTION,
                                                                  JOptionPane.QUESTION_MESSAGE,
                                                                  None,
                                                                  options,
                                                                  options[1])

                        if userAction != 1:
                            self.statusLabel.setText(("User cancelled Date Selection for TXN Search").ljust(800, " "))
                            self.statusLabel.setForeground(Color.RED)
                            return

                        if user_selectDateStart.getDateInt() <= user_selectDateEnd.getDateInt() \
                                and user_selectDateEnd.getDateInt() >= user_selectDateStart.getDateInt():
                            break   # Valid date range

                        user_selectDateStart.setForeground(Color.RED)
                        user_selectDateEnd.setForeground(Color.RED)
                        continue   # Loop

                    txns = moneydance.getCurrentAccountBook().getTransactionSet().getTransactions(
                        MyTxnSearchFilter(user_selectDateStart.getDateInt(),user_selectDateEnd.getDateInt()))

                    if not txns or txns.getSize() <1:
                        self.statusLabel.setText(("No Transactions Found to Geek out on..").ljust(800, " "))
                        self.statusLabel.setForeground(Color.RED)
                        return

                    if txns.getSize() > 20:
                        if not myPopupAskQuestion(Toolbox_frame_, "SEARCH TXNs BY DATE", "YOU HAVE SELECTED %s TXNS.. PROCEED?" % txns.getSize()):
                            self.statusLabel.setText(("GEEK OUT TXN SEARCH FOUND %s TXNs. USER ABORTED...."%txns.getSize()).ljust(800, " "))
                            self.statusLabel.setForeground(Color.RED)
                            return

                    objects = txns

                if objWhat.index(selectedObjType) == _OBJBYUUID:
                    theUUID = myPopupAskForInput(Toolbox_frame_, "GET SINGLE OBJECT BY UUID", "UUID:", "Enter the UUID of the Object to get", "", False)

                    if not theUUID or theUUID == "":
                        self.statusLabel.setText(("No Object UUID was entered to Geek out on..").ljust(800, " "))
                        self.statusLabel.setForeground(Color.RED)
                        return

                    selectedObject = moneydance_data.getItemForID(theUUID.strip())
                    objects  = [selectedObject]
                    if not selectedObject:
                        self.statusLabel.setText(("No Object was found for UUID: %s" %theUUID).ljust(800, " "))
                        self.statusLabel.setForeground(Color.RED)
                        return
                if objWhat.index(selectedObjType) == _OBJTRANSACTION:
                    pass
                else:
                    selectedObject = JOptionPane.showInputDialog(Toolbox_frame_,
                                                                 "Select Specific Object",
                                                                 "Select the specific Object to view",
                                                                 JOptionPane.INFORMATION_MESSAGE,
                                                                 moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                                 objects,
                                                                 None)
                    objects  = [selectedObject]
                    if not selectedObject:
                        self.statusLabel.setText(("No Object was selected to Geek out on..").ljust(800, " "))
                        self.statusLabel.setForeground(Color.RED)
                        return

            lSync = lOFX = lSizes = False
            if selectedWhat == what[_SYNCKEYS]: lSync = True
            if selectedWhat == what[_BANKKEYS]: lOFX = True
            if selectedWhat == what[_SIZEKEYS]: lSizes = True

            try:
                if lObject:  # selected object

                    output += "\n ====== SELECTED OBJECT's RAW PARAMETER KEYS ======\n"

                    for selectedObject in objects:                                                          # noqa
                        # noinspection PyUnresolvedReferences
                        keys=sorted(selectedObject.getParameterKeys())
                        output += "\nObject Type: %s\n" %type(selectedObject)

                        if isinstance(selectedObject, Account):
                            # noinspection PyUnresolvedReferences
                            if selectedObject.getAccountType() == Account.AccountType.ROOT:
                                output += "\n@@OBJECT IS ACCOUNT AND IT IS ROOT\n"
                            else:
                                output += "\nAccount  Type: %s\n" %selectedObject.getAccountType()

                        if isinstance(selectedObject, (ParentTxn,SplitTxn)):
                            output += "Account: %s\n" %selectedObject.getAccount()

                        for theKey in keys:
                            # noinspection PyUnresolvedReferences
                            value = selectedObject.getParameter(theKey)
                            output += pad("Key:%s" %theKey,50)+" Value: %s\n" %(value.strip())

                        if isinstance(selectedObject, Account):
                            try:
                                theCurr = selectedObject.getCurrencyType()
                                output += "\nMD User Representation of Data Held by this Account/Category\n"
                                output += " =============================================================\n"
                                output += "%s %s\n" % (pad("Object's Sync Type:",50),                selectedObject.getSyncItemType()  )
                                output += "%s %s\n" % (pad("Account Name:",50),                      selectedObject.getAccountName()   )
                                output += "%s %s\n" % (pad("Parent Account Name:",50),               selectedObject.getParentAccount().getAccountName() )
                                output += "%s %s\n" % (pad("Full Account Name:",50),                 selectedObject.getFullAccountName()                )
                                output += "%s %s\n" % (pad("Account Type:",50),                      selectedObject.getAccountType()                    )
                                output += "%s %s\n" % (pad("Account Description:",50),               selectedObject.getAccountDescription()             )
                                output += "%s %s\n" % (pad("Account Start Date:",50),                selectedObject.getCreationDateInt()                )
                                output += "%s %s\n" % (pad("Comment:",50),                           selectedObject.getComment()                        )
                                output += "%s %s\n" % (pad("Account Number (Legacy):",50),           selectedObject.getAccountNum()                     )
                                output += "%s %s\n" % (pad("Account Is Inactive:",50),               selectedObject.getAccountIsInactive()              )
                                output += "%s %s\n" % (pad("Account Or Parent Is Inactive:",50),     selectedObject.getAccountOrParentIsInactive()      )
                                output += "%s %s\n" % (pad("Hidden from Home Screen:",50),           selectedObject.getHideOnHomePage()                 )
                                output += "%s %s\n" % (pad("This Accounts Depth (from top):",50),    selectedObject.getDepth()                          )
                                output += "%s %s\n" % (pad("Parent Accounts back to Root:",50),      selectedObject.getAllAccountNames()                )
                                output += "%s %s\n" % (pad("This Acct's sub accounts:",50),          selectedObject.getSubAccounts()                    )
                                output += "%s %s\n" % (pad("Account Currency:",50),                  selectedObject.getCurrencyType()                   )
                                output += "%s %s\n" % (pad("Count of Sub Accounts:",50),             selectedObject.getSubAccountCount()                )
                                output += "%s %s\n" % (pad("Account Number:",50),                    selectedObject.getBankAccountNumber()              )
                                output += "%s %s\n" % (pad("Bank Name:",50),                         selectedObject.getBankName()                       )
                                output += "%s %s\n" % (pad("Default Category:",50),                  selectedObject.getDefaultCategory()                )
                                if selectedObject.getDefaultTransferAccount():
                                    output += "%s %s\n" % (pad("Default Transfer Acct:",50),         selectedObject.getDefaultTransferAccount()         )
                                output += "%s %s\n" % (pad("Tax related:",50),                       selectedObject.isTaxRelated()                      )
                                if selectedObject.isDeductible():
                                    output += "%s %s\n" % (pad("is Deductible:",50),                 selectedObject.isDeductible()                      )
                                if selectedObject.getTaxCategory():
                                    output += "%s %s\n" % (pad("Tax Category:",50),                 selectedObject.getTaxCategory()                     )

                                # noinspection PyUnresolvedReferences
                                if selectedObject.getAccountType() == Account.AccountType.CREDIT_CARD:
                                    output += "%s %s\n" % (pad("Card Number:",50),                  selectedObject.getCardNumber()                 )
                                    output += "%s %s\n" % (pad("Card Expiration Month:",50),        selectedObject.getCardExpirationMonth()        )
                                    output += "%s %s\n" % (pad("Card Expiation Year:",50),          selectedObject.getCardExpirationYear()         )
                                    output += "%s %s\n" % (pad("Credit Limit:",50),                 selectedObject.getCreditLimit()                )
                                    output += "%s %s\n" % (pad("APR %:",50),                        selectedObject.getAPRPercent()                 )

                                output += "%s %s\n" % (pad("Transactions within this Account:",50),  selectedObject.getTxnCount()                  )
                                output += "%s %s\n" % (pad("Unconfirmed Transactions:",50),          selectedObject.getUnconfirmedTxnCount()       )

                                if selectedObject.getReminder():
                                    output += "%s %s\n" % (pad("Reminder:",50),                      selectedObject.getReminder()                  )

                                # noinspection PyUnresolvedReferences
                                if selectedObject.getAccountType() == Account.AccountType.BANK \
                                        or selectedObject.getAccountType() == Account.AccountType.CREDIT_CARD \
                                        or selectedObject.getAccountType() == Account.AccountType.INVESTMENT:
                                    if selectedObject.isOnlineEnabled():
                                        output += "%s %s\n" % (pad("Online Enabled:",50),                selectedObject.isOnlineEnabled()                 )
                                    if selectedObject.isOnlineBankingCandidate():
                                        output += "%s %s\n" % (pad("Online Banking Candidate:",50),      selectedObject.isOnlineBankingCandidate()        )
                                    if selectedObject.isOnlineBillpayCandidate():
                                        output += "%s %s\n" % (pad("Online Bill Pay Candidate:",50),     selectedObject.isOnlineBillpayCandidate()        )
                                    if selectedObject.getBankingFI():
                                        output += "%s %s\n" % (pad("OFX Banking Service:",50),           selectedObject.getBankingFI()                    )
                                    if selectedObject.getBillPayFI():
                                        output += "%s %s\n" % (pad("OFX Bill Pay Service:",50),          selectedObject.getBillPayFI()                    )
                                    if selectedObject.getOFXAccountType():
                                        output += "%s %s\n" % (pad("OFX Account Type:",50),              selectedObject.getOFXAccountType()               )
                                    if selectedObject.getOFXAccountNumber():
                                        output += "%s %s\n" % (pad("OFX Account Number:",50),            selectedObject.getOFXAccountNumber()             )
                                    if selectedObject.getOFXBankID():
                                        output += "%s %s\n" % (pad("OFX Bank ID:",50),                   selectedObject.getOFXBankID()                    )
                                    if selectedObject.getOFXBranchID():
                                        output += "%s %s\n" % (pad("OFX Branch ID:",50),                 selectedObject.getOFXBranchID()                  )
                                    if selectedObject.getOFXBrokerID():
                                        output += "%s %s\n" % (pad("OFX Broker ID:",50),                 selectedObject.getOFXBrokerID()                  )
                                    if selectedObject.getOFXAccountKey():
                                        output += "%s %s\n" % (pad("OFX Account Key:",50),               selectedObject.getOFXAccountKey()                )
                                    if selectedObject.getOFXAccountMsgType():
                                        output += "%s %s\n" % (pad("OFX Acct Message Type:",50),         selectedObject.getOFXAccountMsgType()            )
                                    if selectedObject.getOFXBillPayAccountNumber():
                                        output += "%s %s\n" % (pad("OFX Bill Pay Acct Number:",50),      selectedObject.getOFXBillPayAccountNumber()      )
                                    if selectedObject.getOFXBillPayAccountType():
                                        output += "%s %s\n" % (pad("OFX Bill Pay Acct Type:",50),        selectedObject.getOFXBillPayAccountType()        )
                                    if selectedObject.getOFXBillPayBankID():
                                        output += "%s %s\n" % (pad("OFX Bill Pay Bank ID:",50),          selectedObject.getOFXBillPayBankID()             )

                                output += "%s %s\n" % ( pad("Start Balance:",50),                        theCurr.getDoubleValue(selectedObject.getStartBalance()))
                                output += "%s %s\n" % ( pad("Balance:",50),                              theCurr.getDoubleValue(selectedObject.getBalance()))
                                output += "%s %s\n" % ( pad("Cleared Balance:",50),                      theCurr.getDoubleValue(selectedObject.getClearedBalance()))
                                output += "%s %s\n" % ( pad("Current Balance:",50),                      theCurr.getDoubleValue(selectedObject.getCurrentBalance()))
                                output += "%s %s\n" % ( pad("Confirmed Balance:",50),                    theCurr.getDoubleValue(selectedObject.getConfirmedBalance()))
                                output += "%s %s\n" % ( pad("Reconciling Balance:",50),                  theCurr.getDoubleValue(selectedObject.getReconcilingBalance()))

                                output += "%s %s\n" % ( pad("User Start Balance:",50),                   theCurr.getDoubleValue(selectedObject.getUserStartBalance()))
                                output += "%s %s\n" % ( pad("User Balance:",50),                         theCurr.getDoubleValue(selectedObject.getUserBalance()))
                                output += "%s %s\n" % ( pad("User Cleared Balance:",50),                 theCurr.getDoubleValue(selectedObject.getUserClearedBalance()))
                                output += "%s %s\n" % ( pad("User Confirmed Balance:",50),               theCurr.getDoubleValue(selectedObject.getUserConfirmedBalance()))
                                output += "%s %s\n" % ( pad("User Current Balance:",50),                 theCurr.getDoubleValue(selectedObject.getUserCurrentBalance()))
                                output += "%s %s\n" % ( pad("User Reconciling Balance:",50),             theCurr.getDoubleValue(selectedObject.getUserReconcilingBalance()))

                                output += "%s %s\n" % ( pad("Recursive Start Balance:",50),              theCurr.getDoubleValue(selectedObject.getRecursiveStartBalance()))
                                output += "%s %s\n" % ( pad("Recursive Balance:",50),                    theCurr.getDoubleValue(selectedObject.getRecursiveBalance()))
                                output += "%s %s\n" % ( pad("Recursive Cleared Balance:",50),            theCurr.getDoubleValue(selectedObject.getRecursiveClearedBalance()))
                                output += "%s %s\n" % ( pad("Recursive Current Balance:",50),            theCurr.getDoubleValue(selectedObject.getRecursiveCurrentBalance()))
                                output += "%s %s\n" % ( pad("Recursive Reconciling Balance:",50),        theCurr.getDoubleValue(selectedObject.getRecursiveReconcilingBalance()))

                                output += "%s %s\n" % ( pad("User Recursive Start Balance:",50),         theCurr.getDoubleValue(selectedObject.getRecursiveUserStartBalance()))
                                output += "%s %s\n" % ( pad("User Recursive Balance:",50),               theCurr.getDoubleValue(selectedObject.getRecursiveUserBalance()))
                                output += "%s %s\n" % ( pad("User Recursive Cleared Balance:",50),       theCurr.getDoubleValue(selectedObject.getRecursiveUserClearedBalance()))
                                output += "%s %s\n" % ( pad("User Recursive Current Balance:",50),       theCurr.getDoubleValue(selectedObject.getRecursiveUserCurrentBalance()))
                                output += "%s %s\n" % ( pad("User Recursive Reconciling Balance:",50),   theCurr.getDoubleValue(selectedObject.getRecursiveUserReconcilingBalance()))

                                # noinspection PyUnresolvedReferences
                                if selectedObject.getAccountType() == Account.AccountType.CREDIT_CARD \
                                        or selectedObject.getAccountType() == Account.AccountType.LOAN:

                                    if selectedObject.getInstitutionName():
                                        output += "%s %s\n" % pad("Institution Name:",50),               selectedObject.getInstitutionName()
                                    if selectedObject.getInitialPrincipal():
                                        output += "%s %s\n" % (pad("Initial Principle:",50),             selectedObject.getInitialPrincipal())
                                    if selectedObject.getPermanentAPR():
                                        output += "%s %s\n" % (pad("Permanent APR:",50),                  selectedObject.getPermanentAPR())
                                    if selectedObject.getPoints():
                                        output += "%s %s\n" % (pad("%loan added as fee to Principle.:",50),selectedObject.getPoints())
                                    if selectedObject.getPaymentsPerYear():
                                        output += "%s %s\n" % (pad("Payments per year:",50),              selectedObject.getPaymentsPerYear())
                                    if selectedObject.getInterestAccount():
                                        output += "%s %s\n" % (pad("Interest Account:",50),               selectedObject.getInterestAccount())
                                    if selectedObject.getEscrowAccount():
                                        output += "%s %s\n" % (pad("Escrow Account:",50),                selectedObject.getEscrowAccount())
                                    if selectedObject.getEscrowPayment():
                                        output += "%s %s\n" % (pad("Escrow Payment:",50),                selectedObject.getEscrowPayment())
                                    if selectedObject.getInterestRate():
                                        output += "%s %s\n" % (pad("Interest Rate:",50),                 selectedObject.getInterestRate())
                                    if selectedObject.getFixedMonthlyPaymentAmount():
                                        output += "%s %s\n" % (pad("Fixed Payment Amt:",50),             selectedObject.getFixedMonthlyPaymentAmount())
                                    if selectedObject.getRateChangeDate():
                                        output += "%s %s\n" % (pad("Date Rate  Changed:",50),            selectedObject.getRateChangeDate())
                                    if selectedObject.getDebtPaymentAmount():
                                        output += "%s %s\n" % (pad("Val Pmts made to this CC:",50),      selectedObject.getDebtPaymentAmount())
                                    if selectedObject.getDebtPaymentProportion():
                                        output += "%s %s\n" % (pad("%value Pmts made to this cc:",50),   selectedObject.getDebtPaymentProportion())
                                    if selectedObject.getDebtPaymentSpec():
                                        output += "%s %s\n" % (pad("Pmt  Plan Used:",50),                selectedObject.getDebtPaymentSpec())

                                    if selectedObject.getPaymentSchedule():
                                        output += "%s %s\n" % (pad("Payment Schedule:",50),               selectedObject.getPaymentSchedule())
                                    if selectedObject.hasExpiringRate():
                                        output += "%s %s\n" % (pad("Has Expiring Rate:",50),              selectedObject.hasExpiringRate())
                                    if selectedObject.getCalcPmt():
                                        output += "%s %s\n" % (pad("Calc Payment:",50),                   selectedObject.getCalcPmt())

                                if selectedObject.getInvestAccountNumber():
                                    output += "%s %s\n" % (pad("Investment Account Number:",50),          selectedObject.getInvestAccountNumber())

                                # noinspection PyUnresolvedReferences
                                if selectedObject.getAccountType() == Account.AccountType.SECURITY:
                                    if selectedObject.getBroker():
                                        output += "%s %s\n" % (pad("Broker:",50),                           selectedObject.getBroker())
                                    if selectedObject.getBrokerPhone():
                                        output += "%s %s\n" % (pad("Broker Phone:",50),                     selectedObject.getBrokerPhone())
                                    if selectedObject.getInvstCommissionAcct():
                                        output += "%s %s\n" % (pad("Investment Commission Account",50),     selectedObject.getInvstCommissionAcct())
                                    if selectedObject.getAnnualFee():
                                        output += "%s %s\n" % (pad("Annual Fee:",50),                       selectedObject.getAnnualFee())
                                    if selectedObject.getDividend():
                                        output += "%s %s\n" % (pad("Dividend:",50),                         selectedObject.getDividend())
                                    if selectedObject.getUsesAverageCost():
                                        output += "%s %s\n" % (pad("Uses Average Cost:",50),                selectedObject.getUsesAverageCost())
                                    if selectedObject.getSecurityType():
                                        output += "%s %s\n" % (pad("Security Type:",50),                    selectedObject.getSecurityType())
                                    if selectedObject.getSecuritySubType():
                                        output += "%s %s\n" % (pad("`Security Sub Type`:",50),              selectedObject.getSecuritySubType())
                                    if selectedObject.getBondType():
                                        output += "%s %s\n" % (pad("Bond Type:",50),                        selectedObject.getBondType())
                                    if selectedObject.getMaturity():
                                        output += "%s %s\n" % (pad("Maturity:",50),                         selectedObject.getMaturity())
                                    if selectedObject.getNumYears():
                                        output += "%s %s\n" % (pad("Maturity Year (6=six Mnths):",50),      selectedObject.getNumYears())
                                    if selectedObject.getCompounding():
                                        output += "%s %s\n" % (pad("CD Compounding:",50),                   selectedObject.getCompounding())
                                    if selectedObject.getOptionPrice():
                                        output += "%s %s\n" % (pad("Option Price:",50),                     selectedObject.getOptionPrice())
                                    if selectedObject.getMonth():
                                        output += "%s %s\n" % (pad("Option Exercise Month (0-11 3rd Fri):",50),selectedObject.getMonth())
                                    if selectedObject.getStrikePrice():
                                        output += "%s %s\n" % (pad("Option Strike Price:",50),               selectedObject.getStrikePrice())
                                    if selectedObject.getPut():
                                        output += "%s %s\n" % (pad("Option Put(T), Call(F):",50),           selectedObject.getPut())
                                    if selectedObject.getEscrow():
                                        output += "%s %s\n" % (pad("Escrow?:",50),                          selectedObject.getEscrow())
                                    if selectedObject.getExchange():
                                        output += "%s %s\n" % (pad("Trading Platform:",50),                 selectedObject.getExchange())
                                    if selectedObject.getFaceValue():
                                        output += "%s %s\n" % (pad("Bond face value:",50),                  selectedObject.getFaceValue())

                            except:
                                output += dump_sys_error_to_md_console_and_errorlog( True )

                        elif isinstance(selectedObject, CurrencyType):
                            try:
                                output += "\nMD User Representation of Data Held by this Currency/Security\n"
                                output += " =============================================================-\n"
                                if selectedObject == baseCurr:                                                              # noqa
                                    output += "THIS IS THE BASE RATE!\n"
                                output += "%s %s\n" % (pad("Sync Item Type:",50),       selectedObject.getSyncItemType()  )
                                output += "%s %s\n" % (pad("Currency Type:",50),        selectedObject.getCurrencyType()  )
                                output += "%s %s\n" % (pad("Name:",50),                 selectedObject.getName()  )
                                output += "%s %s\n" % (pad("Hide in UI?:",50),          selectedObject.getHideInUI()  )
                                output += "%s %s\n" % (pad("ID:",50),                   selectedObject.getID()  )
                                output += "%s %s\n" % (pad("ID String:",50),            selectedObject.getIDString()  )
                                output += "%s %s\n" % (pad("Ticker Symbol:",50),        selectedObject.getTickerSymbol()  )
                                output += "%s %s\n" % (pad("Prefix:",50),               selectedObject.getPrefix()  )
                                output += "%s %s\n" % (pad("Suffix:",50),               selectedObject.getSuffix()  )
                                output += "%s %s\n" % (pad("Decimal Places:",50),       selectedObject.getDecimalPlaces()  )
                                output += "%s %s\n" % (pad("Curr Start Date:",50),      selectedObject.getEffectiveDateInt()  )
                                output += "%s %s\n" % (pad("RATE:",50),                 selectedObject.getRate(None)  )
                                output += "%s %s\n" % (pad("RATE Inverted:",50),        1/selectedObject.getRate(None)  )
                                output += "%s %s\n" % (pad("RATE in terms of Base:",50),selectedObject.getBaseRate()  )
                                output += "%s %s\n" % (pad("Relative Currency:",50),    selectedObject.getRelativeCurrency()  )
                                output += "%s %s\n" % (pad("Relative Rate:",50),        selectedObject.getRelativeRate()  )
                                output += "%s %s\n" % (pad("Count Price History:",50),  len(selectedObject.getSnapshots()  ))
                                output += "%s %s\n" % (pad("Count Stock Splits:",50),   len(selectedObject.getSplits()  ))
                                output += "%s %s\n" % (pad("Daily Change:",50),         selectedObject.getDailyChange()  )
                                output += "%s %s\n" % (pad("Daily Volume:",50),         selectedObject.getDailyVolume()  )
                                output += "<END>\n"
                            except:
                                output += dump_sys_error_to_md_console_and_errorlog( True )

                        elif isinstance(selectedObject, ReportSpec):

                            if lReportDefaultsSelected:
                                LS = moneydance_ui.getCurrentAccounts().getBook().getLocalStorage()
                                keys=sorted(LS.keys())

                                found_any = False
                                for theKey in keys:
                                    value = LS.get(theKey)
                                    if not theKey.lower().startswith("report_params."+selectedObject.getReportGenerator().getShortID()): continue
                                    if not found_any:
                                        output += "\nDEFAULT REPORT PARAMETERS (SET BY USER):\n"
                                        found_any = True
                                    output += "Key:%s Value: %s\n" % (pad(theKey,70), value.strip())
                        elif isinstance(selectedObject, Reminder):
                            pass
                        elif isinstance(selectedObject, AddressBookEntry):
                            pass
                        elif isinstance(selectedObject, OnlineService):
                            output += "\nI need a volunteer who uses OFX online banking to help me test finding the OFX data.... please.....\n"
                            pass

                if selectedWhat == what[_PREFKEYS] or lSync or lOFX or lSizes or lSearch:  # User  Preferences

                    output += "\n ====== USER PREFERENCES LOADED INTO MEMORY (May or may not be the same as config.dict) ======\n"

                    # This bit below is really, really cool!!!! But I am not using it as it only gets pre-defined settings from config.dict.
                    # prefs=[]
                    # what_x = moneydance_ui.getPreferences()
                    # members = [attr for attr in dir(what_x) if not callable(getattr(what_x, attr)) and not attr.startswith("__")]
                    # for mem in members:
                    #     if not mem.upper() == mem: continue
                    #     try:
                    #         convertKey = getattr(UserPreferences, mem)
                    #     except:
                    #         continue
                    #     if not convertKey or convertKey=="" : continue
                    #     value = moneydance_ui.getPreferences().getSetting(getattr(UserPreferences, mem))
                    #     if value: prefs.append([convertKey, mem, value])
                    # prefs =sorted(prefs) # Sort the result (as the input is only a reference to a reference)

                    # As all settings in memory actually come from config.dict (or go back to config.dict) then we look there instead to get the keys
                    st,tk = read_preferences_file(lSaveFirst=True)  # Must flush memory to disk first before we read the file....
                    prefs=sorted(tk)

                    for theKey in prefs:
                        value = st.get(theKey)
                        if lSync and not ("sync" in theKey.lower()): continue
                        if lOFX and not ("ofx" in theKey.lower() or "ol." in theKey.lower() or "olb." in theKey.lower()): continue
                        if lSizes and not check_for_window_display_data(theKey,value): continue
                        if lSearch:
                            myTestValue = value
                            if not isinstance(myTestValue,(str,unicode)): myTestValue  = repr(myTestValue)  # Force the StreamTable / StreamVector into a string for search comparison
                            # noinspection PyUnresolvedReferences
                            if lKeys and not (searchWhat.lower() in theKey.lower()): continue
                            elif lKeyData and not (searchWhat.lower() in myTestValue.lower()): continue
                        # noinspection PyUnresolvedReferences
                        output += (pad("Key:%s" % (theKey),35)+ " Value: %s\n" %((value.strip())))


                if selectedWhat == what[_ROOTKEYS] or lSync or lOFX or lSizes or lSearch:  # ROOT

                    keys=sorted(root.getParameterKeys())
                    output += '\n ====== ROOT PARAMETER KEYS (Preferences will mostly be in Local Storage) ======\n'
                    for theKey in keys:

                        value = root.getParameter(theKey)

                        if lSync and ("sync" not in theKey.lower()): continue
                        if lOFX and not ("ofx" in theKey.lower() or "ol." in theKey.lower() or "olb." in theKey.lower()): continue
                        if lSizes and not check_for_window_display_data(theKey,value): continue
                        if lSearch:
                            if lKeys and not (searchWhat.lower() in theKey.lower()): continue
                            elif lKeyData and not (searchWhat.lower() in value.lower()): continue
                        if theKey.lower() == "netsync.synckey": value = "<*****>"
                        output += pad("Key:%s" %theKey,50)+" Value: %s\n" %(value.strip())

                if selectedWhat == what[_BOOKKEYS] or lSync or lOFX or lSizes or lSearch:  # Local Storage

                    output += '\n ====== BOOK>LOCAL STORAGE KEYS ======\n'
                    LS = moneydance_ui.getCurrentAccounts().getBook().getLocalStorage()
                    keys=sorted(LS.keys())

                    last = None
                    for theKey in keys:
                        value = LS.get(theKey)    # NOTE: .get loses the underlying type and thus becomes a string
                        if lSync and "sync" not in theKey.lower(): continue
                        if lOFX and not ("ofx" in theKey.lower() or "ol." in theKey.lower() or "olb." in theKey.lower()): continue
                        if lSizes and not check_for_window_display_data(theKey,value): continue
                        if lSearch:
                            if lKeys and not (searchWhat.lower() in theKey.lower()): continue
                            elif lKeyData and not (searchWhat.lower() in value.lower()): continue

                        if theKey.lower() == "netsync.synckey": value = "<*****>"

                        splitKey = theKey.split('.')
                        if splitKey[0] != last:
                            last = splitKey[0]
                            lookupAcct = moneydance_data.getAccountByUUID(splitKey[0])
                            if lookupAcct:
                                output += ("\n>> Account: %s\n" %(lookupAcct.getFullAccountName()))
                            else:
                                output += "\n"

                        output += pad("Key:%s" %theKey,70)+" Value: %s\n" %(value.strip())




                if selectedWhat == what[_ACCTKEYS] or lSync or lOFX or lSizes or lSearch:  # Accounts (excluding Root)

                    output += "\n ====== ACCOUNTS' PARAMETER KEYS  (Preferences will mostly be in Local Storage) ======\n"
                    accounts = AccountUtil.allMatchesForSearch(moneydance_data, MyAcctFilter(5))
                    lastAcct = None
                    for acct in accounts:
                        keys = sorted(acct.getParameterKeys())
                        for theKey in keys:

                            value = acct.getParameter(theKey)
                            if lSync and not ("sync" in theKey.lower()): continue
                            if lOFX and not ("ofx" in theKey.lower() or "ol." in theKey.lower() or "olb." in theKey.lower()): continue
                            if lSizes and not check_for_window_display_data(theKey,value): continue
                            if lSearch:
                                if lKeys and not (searchWhat.lower() in theKey.lower()): continue
                                elif lKeyData and not (searchWhat.lower() in value.lower()): continue

                            if acct != lastAcct:
                                output += "\n>> Account: %s\n" %acct.getFullAccountName()
                                lastAcct = acct

                            if theKey.lower() == "netsync.synckey": value = "<*****>"
                            if theKey.lower() == "bank_account_number": value = "<*****>"
                            output += pad("Key:%s" %(theKey),50)+" Value: %s\n" %(value.strip())

                if lOFX or lSearch:
                    output += "\n ====== OFX Online Banking Service ' PARAMETER KEYS ======\n"

                    lastService = None
                    services = moneydance_data.getOnlineInfo().getAllServices()
                    for service in services:
                        keys = sorted(service.getParameterKeys())
                        for theKey in keys:

                            value = service.getParameter(theKey)

                            if lSearch:
                                if lKeys and not (searchWhat.lower() in theKey.lower()): continue
                                elif lKeyData and not (searchWhat.lower() in value.lower()): continue

                            if service != lastService:
                                output += "\nOFX SERVICE: %s\n" %service
                                output += "--------------------------------------------\n"
                                lastService = service

                            output += pad("Key:%s" %theKey,50)+ " Value: %s\n" %(value)

                if selectedWhat == what[_OSPROPS]:  # System.Properties

                    output += "\n ====== (Operating) System.Properties.....======\n"

                    props = sorted(System.getProperties())
                    for prop in props:
                        output += pad("Property:%s" %prop,50)+ " Value: %s\n"%(System.getProperty(prop))

                if selectedWhat == what[_OSENV]:    # Environment variables

                    output += "\n ====== Operating System Environment Variables.....======\n"

                    for k, v in os.environ.items():
                        output += pad("Variable: %s" %k,50)+ " Value: %s\n" %(v)

            except:
                output += dump_sys_error_to_md_console_and_errorlog( True )

            output += "<END>\n"

            QuickJFrame("Geek Out on....: %s" % selectedWhat, output).show_the_frame()

            self.statusLabel.setText(("I hope you enjoyed Geeking Out on...: %s" % selectedWhat).ljust(800, " "))
            self.statusLabel.setForeground(DARK_GREEN)

            myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
            return

    class ZeroBalCategoriesButtonAction(AbstractAction):

        def __init__(self, statusLabel, lFix):
            self.statusLabel = statusLabel
            self.lFix = lFix

        def actionPerformed(self, event):
            global Toolbox_frame_, debug, DARK_GREEN, lCopyAllToClipBoard_TB
            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

            if self.lFix:
                myPrint("DB","User requested to Inactivate Zero Balance Categories!")
            else:
                myPrint("D", "User requested to View Zero Balance Categories!")

            if self.lFix:
                myPrint("B", "Script running to Analyse your Active Categories for Zero Balance...............")
                myPrint("P", "---------------------------------------------------------")
            else:
                myPrint("B", "Script running to de-activate your Categories with Zero Balance...............")
                myPrint("P", "---------------------------------------------------------")

            if moneydance_data is None:
                self.statusLabel.setText(("No data to scan - aborting..").ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            output = ""
            output += "Analysing your categories for Zero Balances....\n\n"

            baseCurr = moneydance_data.getCurrencies().getBaseType()


            # ==========================================
            # Search reminders first
            root = moneydance.getCurrentAccountBook()
            rems = root.getReminders().getAllReminders()

            listOfRems={}

            for rem in rems:
                remType = rem.getReminderType()  # NOTE or TRANSACTION

                if str(remType) != 'TRANSACTION': continue

                lastDate = rem.getLastDateInt()
                if not lastDate:
                    pass    # No end date set, so proceed
                else:
                    remDate = rem.getNextOccurance(lastDate)    # Stop at enddate
                    if not remDate: continue    # Expired so skip

                    if not remDate >= DateUtil.getStrippedDateInt(): continue
                    # Right, got one!

                desc = rem.getDescription()

                txnParent = rem.getTransaction()

                for index2 in range(0, int(txnParent.getOtherTxnCount())):
                    splitDesc = txnParent.getOtherTxn(index2).getDescription()
                    acct = txnParent.getAccount()
                    cat = txnParent.getOtherTxn(index2).getAccount()
                    catValue = baseCurr.getDoubleValue(txnParent.getOtherTxn(index2).getValue()) * -1

                    if catValue:
                        theReminder = [acct, cat, catValue, desc, splitDesc]
                        listOfRems[cat]=theReminder

            # ==========================================


            # Now the Categories
            accounts = AccountUtil.allMatchesForSearch(moneydance_data, MyAcctFilter(4))    # This returns active and inactive accounts
            accounts = sorted(accounts, key=lambda x: (x.getAccountType(), str(x.getFullAccountName()).upper()))

            categoriesToInactivate = {}

            output += "LISTING ACTIVE CATEGORIES WITH ZERO BALANCES:\n\n"

            # Run 1 - get the initial list
            for cat in accounts:
                if cat.getAccountOrParentIsInactive(): continue
                if (cat.getBalance() == 0
                        # and cat.getClearedBalance() == 0
                        and cat.getConfirmedBalance() == 0
                        and cat.getCurrentBalance() == 0
                        # and cat.getReconcilingBalance() == 0
                        and cat.getRecursiveBalance() == 0
                        # and cat.getRecursiveClearedBalance() == 0
                        and cat.getRecursiveCurrentBalance() == 0
                        # and cat.getRecursiveReconcilingBalance() == 0
                                                                        ):
                    if listOfRems.get(cat):     # Found a reminder!
                        pass
                    else:
                        categoriesToInactivate[cat]=True

            # Run 2 - filter out parents.... if we are retaining any sub cats
            for cat in accounts:
                if cat.getAccountOrParentIsInactive(): continue
                if not categoriesToInactivate.get(cat):     # Select categories that we are not deactivating

                    # Look for its parents in the list of Cats to deactivate
                    parentCats = cat.getPath()
                    for theParent in parentCats:
                        if categoriesToInactivate.get(theParent):   # Found a parent - so don't deactivate it!
                            categoriesToInactivate[theParent]=False

            last = None
            iCountForInactivation = 0
            sortedCategoriesToInactivate=sorted(list(categoriesToInactivate), key=lambda x: (x.getAccountType(),x.getFullAccountName()) )

            # for cat in categoriesToInactivate.keys():
            for cat in sortedCategoriesToInactivate:
                if categoriesToInactivate.get(cat):
                    iCountForInactivation+=1

                    if not last or last != cat.getAccountType():
                        output += "\nCATEGORY TYPE: %s\n" % cat.getAccountType()
                        last = cat.getAccountType()

                    output += "Category: %s has Zero Balances\n" % pad(cat.getFullAccountName(),100)
                else:
                    output += "Category: %s ** But cannot be deactivated as it's the Parent of an active Category **\n" % pad(cat.getFullAccountName(),100)


            output += "--------------------------------------------------------------------------------------------------\n"
            output += ("You have %s categories with Zero Balances - these can be made Inactive using Advanced Mode......\n" % iCountForInactivation).upper()
            output += "---------------------------------------------------------------------------------------------------\n\n"

            output += "LISTING ACTIVE CATEGORIES WITH ZERO BALANCES - BUT WITH FUTURE REMINDERS PRESENT:\n\n"

            output += pad("Category Name", 78)
            output += " " + pad("Account", 20)
            output += " " + pad("Reminder Description", 35)
            output += " " + rpad("Rem Amount", 12)
            output += " " + pad("Split Desc", 35)
            # output += " " + rpad("RcrsRecBal", 12)
            output += "\n"

            last = None
            for cat in accounts:
                if cat.getAccountOrParentIsInactive(): continue
                if (cat.getBalance() == 0
                        # and cat.getClearedBalance() == 0
                        and cat.getConfirmedBalance() == 0
                        and cat.getCurrentBalance() == 0
                        # and cat.getReconcilingBalance() == 0
                        and cat.getRecursiveBalance() == 0
                        # and cat.getRecursiveClearedBalance() == 0
                        and cat.getRecursiveCurrentBalance() == 0
                        # and cat.getRecursiveReconcilingBalance() == 0
                                                                        ):
                    if not last or last != cat.getAccountType():
                        output += "\nCATEGORY TYPE: %s\n" % cat.getAccountType()
                        last = cat.getAccountType()

                    foundRem = listOfRems.get(cat)
                    if foundRem:    # Found a reminder!
                        output += "Category: %s Reminder Details: " % pad(cat.getFullAccountName(),50)
                        output += pad(foundRem[0].getAccountName(),20)+" "
                        output += pad(foundRem[3],35)+" "
                        output += rpad(foundRem[2],12)+" "
                        output += pad(foundRem[4],35)+"\n"

            output += "-----------------------------------------------------------------------------------------------------------\n"


            output += "\n\nLISTING INACTIVE CATEGORIES WITH ZERO BALANCES:\n\n"

            ii=0
            last = None
            for cat in accounts:
                if not cat.getAccountOrParentIsInactive(): continue
                if (cat.getBalance() == 0
                      # and cat.getClearedBalance() == 0
                      and cat.getConfirmedBalance() == 0
                      and cat.getCurrentBalance() == 0
                      # and cat.getReconcilingBalance() == 0
                      and cat.getRecursiveBalance() == 0
                      # and cat.getRecursiveClearedBalance() == 0
                      and cat.getRecursiveCurrentBalance() == 0 ):  # and cat.getRecursiveReconcilingBalance() == 0


                    if not last or last != cat.getAccountType():
                        output += "\nCATEGORY TYPE: %s\n" % cat.getAccountType()
                        last = cat.getAccountType()

                    output += "Inactive Category: %s has Zero Balances\n" % pad(cat.getFullAccountName(),100)
                    ii+=1

            if not ii:
                output += "<NONE FOUND>\n\n"

            output += "--------------------------------------------------------------------------------------------------\n"

            output += "LISTING ACTIVE CATEGORIES WITH BALANCES:\n\n"

            output += pad("Category Name", 85)
            output += " " + rpad("Balance", 12)
            # output += " " + rpad("ClrdBal", 12)
            # output += " " + rpad("ConfBal", 12)
            output += " " + rpad("CurrBal", 12)
            # output += " " + rpad("RecBal", 12)
            output += " " + rpad("RcrsBal", 12)
            # output += " " + rpad("RcrsClrdBal", 12)
            output += " " + rpad("RcrsCurrBal", 12)
            # output += " " + rpad("RcrsRecBal", 12)
            output += "\n"

            ii = 0
            last = None
            for cat in accounts:
                if cat.getAccountOrParentIsInactive(): continue
                if not (cat.getBalance() == 0
                        # and cat.getClearedBalance() == 0
                        and cat.getConfirmedBalance() == 0
                        and cat.getCurrentBalance() == 0
                        # and cat.getReconcilingBalance() == 0
                        and cat.getRecursiveBalance() == 0
                        # and cat.getRecursiveClearedBalance() == 0
                        and cat.getRecursiveCurrentBalance() == 0):     # and cat.getRecursiveReconcilingBalance() == 0
                    if not last or last != cat.getAccountType():
                        output += "\nCATEGORY TYPE: %s\n" % cat.getAccountType()
                        last = cat.getAccountType()

                    output += "%s" % pad(cat.getFullAccountName(), 85)

                    mult = 1
                    # noinspection PyUnresolvedReferences
                    if cat.getAccountType() == Account.AccountType.EXPENSE: mult = -1

                    output += " " + rpad("%s" % baseCurr.getDoubleValue(cat.getUserBalance()*mult), 12)
                    # output += " " + rpad("%s" % baseCurr.getDoubleValue(cat.getUserClearedBalance()*mult), 12)
                    # output += " " + rpad("%s" % baseCurr.getDoubleValue(cat.getUserConfirmedBalance()*mult), 12)
                    output += " " + rpad("%s" % baseCurr.getDoubleValue(cat.getUserCurrentBalance()*mult), 12)
                    # output += " " + rpad("%s" % baseCurr.getDoubleValue(cat.getUserReconcilingBalance()*mult), 12)
                    output += " " + rpad("%s" % baseCurr.getDoubleValue(cat.getRecursiveUserBalance()*mult), 12)
                    # output += " " + rpad("%s" % baseCurr.getDoubleValue(cat.getRecursiveUserClearedBalance()*mult), 12)
                    output += " " + rpad("%s" % baseCurr.getDoubleValue(cat.getRecursiveUserCurrentBalance()*mult), 12)
                    # output += " " + rpad("%s" % baseCurr.getDoubleValue(cat.getRecursiveUserReconcilingBalance()*-1), 12)
                    output += "\n"
                    ii+=1
            if not ii:
                output += "<NONE FOUND>\n\n"

            output += "----------------------------------------------------------------------------\n\n"

            output += "LISTING INACTIVE CATEGORIES WITH BALANCES:\n\n"

            output += pad("Category Name", 85)
            output += " " + rpad("Balance", 12)
            # output += " " + rpad("ClrdBal", 12)
            # output += " " + rpad("ConfBal", 12)
            output += " " + rpad("CurrBal", 12)
            # output += " " + rpad("RecBal", 12)
            output += " " + rpad("RcrsBal", 12)
            # output += " " + rpad("RcrsClrdBal", 12)
            output += " " + rpad("RcrsCurrBal", 12)
            # output += " " + rpad("RcrsRecBal", 12)
            output += "\n"

            ii=0
            last = None
            for cat in accounts:
                if not cat.getAccountOrParentIsInactive(): continue
                if not (cat.getBalance() == 0
                      # and cat.getClearedBalance() == 0
                      and cat.getConfirmedBalance() == 0
                      and cat.getCurrentBalance() == 0
                      # and cat.getReconcilingBalance() == 0
                      and cat.getRecursiveBalance() == 0
                      # and cat.getRecursiveClearedBalance() == 0
                      and cat.getRecursiveCurrentBalance() == 0):       # and cat.getRecursiveReconcilingBalance() == 0

                    if not last or last != cat.getAccountType():
                        output += "\nCATEGORY TYPE: %s\n" % cat.getAccountType()
                        last = cat.getAccountType()

                    output += "%s" % pad(cat.getFullAccountName(), 85)

                    mult = 1
                    # noinspection PyUnresolvedReferences
                    if cat.getAccountType() == Account.AccountType.EXPENSE: mult = -1

                    output += " " + rpad("%s" % baseCurr.getDoubleValue(cat.getUserBalance()*mult), 12)
                    # output += " " + rpad("%s" % baseCurr.getDoubleValue(cat.getUserClearedBalance()*mult), 12)
                    # output += " " + rpad("%s" % baseCurr.getDoubleValue(cat.getUserConfirmedBalance()*mult), 12)
                    output += " " + rpad("%s" % baseCurr.getDoubleValue(cat.getUserCurrentBalance()*mult), 12)
                    # output += " " + rpad("%s" % baseCurr.getDoubleValue(cat.getUserReconcilingBalance()*mult), 12)
                    output += " " + rpad("%s" % baseCurr.getDoubleValue(cat.getRecursiveUserBalance()*mult), 12)
                    # output += " " + rpad("%s" % baseCurr.getDoubleValue(cat.getRecursiveUserClearedBalance()*mult), 12)
                    output += " " + rpad("%s" % baseCurr.getDoubleValue(cat.getRecursiveUserCurrentBalance()*mult), 12)
                    # output += " " + rpad("%s" % baseCurr.getDoubleValue(cat.getRecursiveUserReconcilingBalance()*mult), 12)
                    output += "\n"
                    ii+=1

            if not ii:
                output += "<NONE FOUND>\n\n"

            output += "----------------------------------------------------------------------------\n\n"

            output += "\nLEGEND:\n"
            output += "** NOTE: The Balances shown on a Parent Category in any section may not be the sum of its Child Categories shown in the same section.\n"
            output += "         The calculation matches the Moneydance Tools>Categories method and will include the balances(s) from all its Child Categories whether active, inactive or otherwise....\n\n"
            output += "Balance = Account Balance\n"
            # output += "ClrdBal = Cleared Balance (Normally Zero on a Category). Balance excluding uncleared or reconciling txns\n"
            # output += "ConfBal = Confirmed Balance (The Balance less any unconfirmed Online / Downloaded Bank txns\n"
            output += "CurrBal = Current Balance\n"
            # output += "RecBal = Reconciling Balance (Normally Zero on a Category)\n"
            output += "RcrsBal = Recursive (through all sub categories) Account Balance (Note: may contain balances from inactive sub-categories as per Moneydance)\n"
            # output += "RcrsClrdBal = Recursive (through all sub categories) Cleared Balance (Normally Zero on a Category)\n"
            output += "RcrsCurrBal = Recursive (through all sub categories) Current Balance (Note: may contain balances from inactive sub-categories as per Moneydance)\n"
            # output += "RcrsRecBal = Recursive (through all sub categories) Reconciling Balance (Normally Zero on a Category)\n"
            output += "----------------------------------------------------------------------------\n\n"
            output += "<END>"

            if self.lFix:
                output += "\nDISCLAIMER: I take no responsibility if you decide to execute the Inactivate Zero Balance Category fix script!\n"

            if not self.lFix:
                jif = QuickJFrame("View your Active Categories with Zero Balances....", output).show_the_frame()
            else:
                jif = QuickJFrame("View your Active Categories with Zero Balances.... CLICK OK WHEN READY TO PROCEED", output).show_the_frame()

            myPrint("J", "There are %s Active Categories with Zero Balances that could be Inactivated!" % iCountForInactivation)

            if not self.lFix:
                self.statusLabel.setText( ("VIEW ZERO BALANCE CATEGORIES: YOU HAVE %s Zero Balance Categories..." % iCountForInactivation).ljust(800, " "))
                self.statusLabel.setForeground(DARK_GREEN)
                myPopupInformationBox(jif, "You have %s Active Categories with Zero Balances" % iCountForInactivation, "ZERO BALANCE CATEGORIES", JOptionPane.INFORMATION_MESSAGE)
                return

            if iCountForInactivation < 1:
                self.statusLabel.setText(("FIX ZERO BALANCE CATEGORIES: You have no Zero Balance Categories to fix - no fixes applied...").ljust(800, " "))
                self.statusLabel.setForeground(DARK_GREEN)
                myPopupInformationBox(jif, "You have no Zero Balance Categories to fix - no fixes will be applied...", "ZERO BALANCE CATEGORIES", JOptionPane.INFORMATION_MESSAGE)
                return

            if not myPopupAskQuestion(jif,
                                      "FIX - INACTIVATE ZERO BALANCE CATEGORIES",
                                      "OK - Are you sure you want Inactivate these %s Zero Balance Categories?" % iCountForInactivation,
                                      JOptionPane.YES_NO_OPTION,
                                      JOptionPane.ERROR_MESSAGE):

                self.statusLabel.setText(("FIX - INACTIVATE %s ZERO BALANCE CATEGORIES - user declined to proceed - no updates applied!" % iCountForInactivation).ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            if not myPopupAskBackup(jif, "Would you like to perform a backup before INACTIVATING %s CATEGORIES?"% iCountForInactivation):
                self.statusLabel.setText(("FIX - INACTIVATE %s ZERO BALANCE CATEGORIES - User chose to exit without the fix/update..." % iCountForInactivation).ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            disclaimer = myPopupAskForInput(jif,"INACTIVATE ZERO BALANCE CATEGORIES",
                                            "DISCLAIMER:", "Are you really sure you want to Inactivate %s Zero Balance Categories? Type 'IAGREE' to continue.." % iCountForInactivation,
                                            "NO",
                                            False,
                                            JOptionPane.ERROR_MESSAGE)

            if not disclaimer == 'IAGREE':
                self.statusLabel.setText(("FIX - INACTIVATE %s ZERO BALANCE CATEGORIES - User declined Disclaimer... No fixes applied" % iCountForInactivation).ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            # OK - so we are fixing...?
            myPrint("B", ">> User selected to Inactivate %s Zero Balance Categories!?" % iCountForInactivation)
            for cat in categoriesToInactivate.keys():
                if categoriesToInactivate.get(cat):
                    myPrint("B", "Cat: " + cat.getFullAccountName() + " with Zero Balances, Set to INACTIVE!")
                    cat.setAccountIsInactive(True)
                    cat.syncItem()
            myPrint("B", "Finished Inactivating %s Categories with Zero Balances..." % iCountForInactivation)

            self.statusLabel.setText(("FIX - I have set %s Categories with Zero Balances to Inactive as requested!" % iCountForInactivation).ljust(800, " "))
            self.statusLabel.setForeground(Color.RED)
            myPopupInformationBox(jif,"OK - I have set %s Active Categories with Zero Balances to INACTIVE!" % iCountForInactivation,"INACTIVATE ZERO BALANCE CATEGORIES",JOptionPane.WARNING_MESSAGE)
            play_the_money_sound()

            myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
            return

    class DeleteThemeFileButtonAction(AbstractAction):

        def __init__(self, statusLabel):
            self.statusLabel = statusLabel

        def actionPerformed(self, event):
            global Toolbox_frame_, debug
            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

            myPrint("DB", "User requested to delete custom theme file!")

            # noinspection PyUnresolvedReferences
            customThemeFile = str(theme.Theme.customThemeFile)
            if not os.path.exists(customThemeFile):
                self.statusLabel.setText("Custom Theme file does not exist to delete!".ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            if not myPopupAskQuestion(Toolbox_frame_,
                                  "DELETE MD custom Theme file?",
                                  "Are you sure you want to delete custom Theme file?",
                                      JOptionPane.YES_NO_OPTION,
                                      JOptionPane.ERROR_MESSAGE):

                self.statusLabel.setText("User declined to delete custom Theme file!".ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            myPrint("DB", "User confirmed to delete custom Theme file...")

            try:
                if not backup_custom_theme_file():
                    self.statusLabel.setText("Error backing up custom theme file prior to deletion - no changes made!".ljust(800, " "))
                    self.statusLabel.setForeground(Color.RED)
                    return

                os.remove(customThemeFile)
                self.statusLabel.setText(("DELETED CUSTOM THEME FILE: " + customThemeFile).ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                myPrint("B", "User requested to delete custom theme file: ", customThemeFile, " - DELETED!")
                myPopupInformationBox(Toolbox_frame_, "DELETED CUSTOM THEME FILE: %s" % customThemeFile, "DELETE CUSTOM THEME FILE", JOptionPane.WARNING_MESSAGE)

            except:
                myPrint("B", "Error deleting custom theme file", "File:", customThemeFile)
                dump_sys_error_to_md_console_and_errorlog()
                self.statusLabel.setText(("ERROR DELETING CUSTOM THEME FILE: " + customThemeFile).ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                myPopupInformationBox(Toolbox_frame_, "ERROR DELETING CUSTOM THEME FILE: %s" % customThemeFile, "DELETE CUSTOM THEME FILE", JOptionPane.ERROR_MESSAGE)

            myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
            return

    class ForceRemoveExtension(AbstractAction):

        def __init__(self, statusLabel):
            self.statusLabel = statusLabel

        def actionPerformed(self, event):
            global Toolbox_frame_, debug
            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

            myPrint("DB", "User requested to delete all references to orphaned/outdated Extensions from config.dict and *.mxt files...")

            orphan_prefs, orphan_files, orphan_confirmed_extn_keys = get_orphaned_extension()

            if len(orphan_prefs)<1 and len(orphan_files)<1 and len(orphan_confirmed_extn_keys)<1:
                self.statusLabel.setText("No orphaned Extension preferences or files detected - nothing to do!".ljust(800, " "))
                self.statusLabel.setForeground(Color.BLUE)
                return

            displayData="\nLISTING EXTENSIONS ORPHANED IN CONFIG.DICT OR FILES (*.MXT)\n\n"

            for x in orphan_prefs.keys():
                displayData+="%s Extension: %s is %s\n" %(pad("config.dict:",20),pad(x,20),pad(orphan_prefs[x],20))

            displayData+="\n"

            for x in orphan_confirmed_extn_keys.keys():
                _theVersion = moneydance_ui.getPreferences().getSetting(orphan_confirmed_extn_keys[x][1],None)
                displayData+="%s Extension: %s Key: %s (build: %s) is %s\n" %(pad("config.dict: ",20),pad(x,20),pad(orphan_confirmed_extn_keys[x][1],40),_theVersion,pad(orphan_confirmed_extn_keys[x][0],20))

            displayData+="\n"

            for x in orphan_files.keys():
                displayData+="%s Extension: %s is %s\n" %(pad("File: "+orphan_files[x][1],40),pad(x,20),pad(orphan_files[x][0],20))

            displayData+="\n<END>"
            jif = QuickJFrame("ORPHANED EXTENSIONS", displayData).show_the_frame()

            if not myPopupAskQuestion(jif,
                                  "DELETE ORPHANED EXTENSIONS",
                                  "Are you sure you want to delete the Extension Orphans?",
                                  JOptionPane.YES_NO_OPTION,
                                  JOptionPane.ERROR_MESSAGE):
                self.statusLabel.setText("No action taken on the Orphaned Extensions displayed....".ljust(800, " "))
                self.statusLabel.setForeground(Color.BLUE)
                return


            if not myPopupAskBackup(jif, "Would you like to perform a backup before DELETING ORPHANED EXTENSION?"):
                self.statusLabel.setText(("DELETE ORPHANED EXTENSIONS - User chose to exit without the fix/update.....").ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            disclaimer = myPopupAskForInput(jif,
                                            "DELETE ORPHANED EXTENSIONS",
                                            "DISCLAIMER:",
                                            "Are you really sure you want to DELETE these Orphaned Extensions? Type 'IAGREE' to continue..",
                                            "NO",
                                            False,
                                            JOptionPane.ERROR_MESSAGE)

            if not disclaimer == 'IAGREE':
                self.statusLabel.setText("DELETE ORPHANED EXTENSIONS - User declined the disclaimer - no changes made....".ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            extensionDir = Common.getFeatureModulesDirectory()
            if not extensionDir:
                self.statusLabel.setText("DELETE ORPHANED EXTENSIONS - Error getting Extensions directory - no changes made....".ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            if not backup_config_dict():
                self.statusLabel.setText("DELETE ORPHANED EXTENSIONS - Error backing up config.dict preferences file - no changes made....".ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            # reload latest preferences
            extension_prefs = moneydance_ui.getPreferences().getTableSetting("gen.fmodules",None)
            if not extension_prefs:
                self.statusLabel.setText("DELETE ORPHANED EXTENSIONS - Error getting gen.fmodules setting - no changes made....".ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            # OK - let's go....!! Delete away!!!
            for x in orphan_prefs.keys():
                extension_prefs.put(x,None)
                myPrint("B","Orphaned extension %s removed from config.dict!" %x)

            moneydance_ui.getPreferences().setSetting("gen.fmodules",extension_prefs)
            myPrint("B","config.dict gen.fmodules setting re-saved....")

            for x in orphan_confirmed_extn_keys:
                moneydance_ui.getPreferences().setSetting(orphan_confirmed_extn_keys[x][1],None)
                myPrint("B","Orphaned extension key %s removed from config.dict!" %orphan_confirmed_extn_keys[x][1])

            moneydance.savePreferences()

            lError=False
            # extensionDir = Common.getFeatureModulesDirectory()
            for x in orphan_files.keys():
                # noinspection PyTypeChecker
                fileToDelete = os.path.join(extensionDir.getAbsolutePath(),orphan_files[x][1])
                if not os.path.exists(fileToDelete):
                    lError=True
                    myPrint("B","ERROR orphaned extension file %s MISSING" %fileToDelete)
                else:
                    try:
                        os.remove(fileToDelete)
                        myPrint("B","Orphaned extension file %s deleted" %fileToDelete)
                    except:
                        lError=True
                        myPrint("B","ERROR deleting orphaned extension file %s deleted" %fileToDelete)
                        dump_sys_error_to_md_console_and_errorlog()

            play_the_money_sound()

            if lError:
                myPopupInformationBox(jif, "YOUR ORPHANED EXTENSIONS HAVE BEEN DELETED (WITH ERRORS) - PLEASE REVIEW MONEYBOT SCREEN AND CONSOLE ERROR LOG!", "DELETE ORPHANED EXTENSIONS", JOptionPane.ERROR_MESSAGE)
                myPrint("B", "Orphaned Extensions have been deleted - WITH ERRORS - from config.dict and the .MXT files from the Extensions folder....")
                self.statusLabel.setText("YOUR ORPHANED EXTENSIONS HAVE BEEN DELETED - WITH ERRORS - PLEASE REVIEW CONSOLE ERROR LOG!".ljust(800, " "))
            else:
                myPopupInformationBox(jif, "SUCCESS YOUR ORPHANED EXTENSIONS HAVE BEEN DELETED - PLEASE RESTART MONEYDANCE", "DELETE ORPHANED EXTENSIONS", JOptionPane.WARNING_MESSAGE)
                myPrint("B", "SUCCESS - Your Orphaned Extensions have been deleted from config.dict and the .MXT files from the Extensions folder....")
                self.statusLabel.setText("SUCCESS - YOUR ORPHANED EXTENSIONS HAVE BEEN DELETED - I SUGGEST YOU RESTART MONEYDANCE!".ljust(800, " "))

            self.statusLabel.setForeground(Color.RED)
            return



    class ResetWindowPositionsButtonAction(AbstractAction):

        def __init__(self, statusLabel):
            self.statusLabel = statusLabel

        def actionPerformed(self, event):
            global Toolbox_frame_, debug
            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

            _RESETWINLOC    = 0
            _RESETREGFILT   = 1
            _RESETREGVIEW   = 2
            _RESETALL       = 3

            what = [
                "RESET - Only Window Locations on their own (Excludes Filters & Views)",
                "RESET - Only Transaction Register Filters",
                "RESET - Only Transaction Register Initial / Current View screen",
                "RESET - Window display settings (Sizes, Locations, Sorts, Widths etc) - Everything EXCEPT Filters & Views"
                ]

            resetWhat = JOptionPane.showInputDialog(Toolbox_frame_, "RESET WINDOW DISPLAY SETTINGS",
                                                       "Select the Window display setting(s) to RESET",
                                                    JOptionPane.WARNING_MESSAGE,
                                                    None,
                                                    what,
                                                    None)
            if not resetWhat:
                self.statusLabel.setText(("No RESET WINDOW DISPLAY SETTINGS TYPE option was chosen - no changes made!").ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            myPrint("DB", "User requested to %s settings from config.dict, LocalStorage() ./safe/settings , and by account!" %resetWhat)

            lAll = lWinLocations = lRegFilters = lRegViews = False

            if resetWhat == what[_RESETALL]:        lAll            = True
            if resetWhat == what[_RESETWINLOC]:     lWinLocations   = True
            if resetWhat == what[_RESETREGFILT]:    lRegFilters     = True
            if resetWhat == what[_RESETREGVIEW]:    lRegViews       = True

            def get_set_config(st, tk, lReset, lResetAll, lResetWinLoc, lResetRegFilters, lResetRegViews ):                                                               # noqa
                # As of 2021.2010   Window locations are only in config.dict.
                #                   Register Filters and Initial Register Views are only in LocalStorage()
                #                   column width, sort orders, etc are everywhere......

                configData = []

                if not lReset:
                    configData.append("\nDATA STORED WITHIN CONFIG.DICT (effectively defaults where not specifically set by Account):")
                    configData.append("--------------------------------------------------------------------------------------------")

                lastKey = None
                for theKey in tk:
                    # Skip config settings we don't want to reset

                    # Main safety filter here
                    value = st.get(theKey)
                    if not check_for_window_display_data(theKey, value): continue

                    if lResetAll:
                        pass
                    elif lResetWinLoc:
                        if not check_for_just_locations_window_display_data(theKey, value): continue
                    elif lResetRegFilters:
                        if not check_for_just_register_filters_window_display_data(theKey, None): continue
                    elif lResetRegViews:
                        if not check_for_just_initial_view_filters_window_display_data(theKey, None): continue
                    else:
                        myPrint("B", "@@@ ERROR in get_set_config(): unexpected parameter!?")
                        raise(Exception("@@@ ERROR in get_set_config(): unexpected parameter!?"))

                    test = "col_widths."
                    if theKey.startswith(test):
                        if lReset:
                            moneydance.getPreferences().setSetting(theKey, None)
                        else:
                            if theKey[:len(test)] != lastKey:
                                lastKey = theKey[:len(test)]
                                configData.append("COLUMN WIDTHS:")

                            configData.append(pad(theKey+":",30) + moneydance.getPreferences().getSetting(theKey, None).strip())
                        continue

                    test = "ext_mgmt_win"
                    if theKey.startswith(test):
                        if lReset:
                            moneydance.getPreferences().setSetting(theKey, None)
                        else:
                            if theKey[:len(test)] != lastKey:
                                lastKey = theKey[:len(test)]
                                configData.append("\nEXTENSIONS WINDOW:")
                            configData.append(pad(theKey+":",30) + moneydance.getPreferences().getSetting(theKey, None).strip())
                        continue

                    test = "moneybot_py_divider"
                    if theKey.startswith(test):
                        if lReset:
                            moneydance.getPreferences().setSetting(theKey, None)
                        else:
                            if theKey[:len(test)] != lastKey:
                                lastKey = theKey[:len(test)]
                                configData.append("\nMONEYBOT:")
                            configData.append(pad(theKey+":",30) + moneydance.getPreferences().getSetting(theKey, None).strip())
                        continue

                    test = "mbot."
                    if theKey.startswith(test):
                        if lReset:
                            moneydance.getPreferences().setSetting(theKey, None)
                        else:
                            if theKey[:len(test)] != lastKey:
                                lastKey = theKey[:len(test)]
                                configData.append("\nMONEYBOT:")
                            configData.append(pad(theKey+":",30) + moneydance.getPreferences().getSetting(theKey, None).strip())
                        continue

                    test = "gui."
                    if theKey.startswith(test):
                        if lReset:
                            moneydance.getPreferences().setSetting(theKey, None)
                        else:
                            if theKey[:len(test)] != lastKey:
                                lastKey = theKey[:len(test)]
                                configData.append("\nGUI.:")
                            configData.append(pad(theKey+":",30) + moneydance.getPreferences().getSetting(theKey, None).strip())
                        continue

                    myPrint("B","@@ RESET WINDOW DATA - ERROR >> What is this key: %s ? @@" %theKey)
                    raise(Exception("ERROR - caught an un-coded key: " + str(theKey)))

                # END OF config.dict search
                ########################################################################################################

                if lResetAll or lResetRegFilters or lResetRegViews:
                    # Now get the same data for each account
                    accounts = AccountUtil.allMatchesForSearch(moneydance_data, MyAcctFilter(6))

                    if not lReset:
                        configData.append("\nDATA STORED INTERNALLY BY ACCOUNT (not config.dict):")
                        configData.append("-----------------------------------------------------")

                    dataPrefKey = "col_widths."
                    dataPrefKeys_legacy = [  "gui.col_widths",
                                             "rec_reg.credit",
                                             "rec_reg.debit" ]

                    keyIterator=[]
                    if lResetRegFilters:    keyIterator.append("sel_reg_filter")
                    if lResetRegFilters:    keyIterator.append("sel_invreg_filter")
                    if lResetRegViews:      keyIterator.append("sel_inv_view")

                    for acct in accounts:

                        last = None

                        if lResetAll:
                            for x in _COLWIDTHS:
                                xx = acct.getPreference(dataPrefKey+x, None)

                                if xx:
                                    if lReset:
                                        # NOTE: This really sets the preference in LocalStorage() with the acct's UUII+"." prepended as the key!!!! (Sneaky eh!!??)
                                        acct.setPreference(dataPrefKey+x, None)
                                        # acct.syncItem() # Not entirely sure about this.... If Preference goes to LocalStorage() then Acct shouldn't be affected..
                                    else:
                                        if last != acct:
                                            last = acct
                                            configData.append("\n>>Account: %s" %(acct.getAccountName()))

                                        configData.append("Key: %s Value: %s" %(pad(dataPrefKey+x+":",30),str(xx).strip()))

                        if lResetRegFilters or lResetRegViews:
                            for x in keyIterator:
                                xx = acct.getPreference(x, None)

                                if xx:
                                    if lReset:
                                        # NOTE: This really sets the preference in LocalStorage() with the acct's UUII+"." prepended as the key!!!! (Sneaky eh!!??)
                                        acct.setPreference(x, None)
                                        # acct.syncItem() # Not entirely sure about this.... If Preference goes to LocalStorage() then Acct shouldn't be affected..
                                    else:
                                        if last != acct:
                                            last = acct
                                            configData.append("\n>>Account: %s" %(acct.getAccountName()))

                                        configData.append("Key: %s Value: %s" %(pad(x+":",30),str(xx).strip()))

                        lNeedsSync = False

                        if lResetAll:
                            for theLegacyKey in dataPrefKeys_legacy:

                                # Look for legacy keys actually on the account..!
                                yy = acct.getParameter(theLegacyKey, None)

                                if yy:  # Should be a legacy setting
                                    if lReset:
                                        acct.setParameter(theLegacyKey, None)
                                        lNeedsSync = True
                                    else:
                                        if last != acct:
                                            last = acct
                                            configData.append("\n>>Account: %s" %(acct.getAccountName()))

                                        configData.append("Legacy Key: %s Value: %s" %(pad(theLegacyKey+":",30-7),str(yy).strip()))

                        if lResetRegFilters or lResetRegViews:
                            for theLegacyKey in keyIterator:

                                # Look for legacy keys actually on the account..!
                                yy = acct.getParameter(theLegacyKey, None)

                                if yy:  # Should be a legacy setting
                                    if lReset:
                                        acct.setParameter(theLegacyKey, None)
                                        lNeedsSync = True
                                    else:
                                        if last != acct:
                                            last = acct
                                            configData.append("\n>>Account: %s" %(acct.getAccountName()))

                                        configData.append("Legacy Key: %s Value: %s" %(pad(theLegacyKey+":",30-7),str(yy).strip()))

                        if lReset and lNeedsSync:
                            acct.syncItem()

                    # END OF Accounts search
                    ########################################################################################################

                    if not lReset:
                        configData.append("\nDATA STORED INTERNALLY WITHIN LOCAL STORAGE (not config.dict):")
                        configData.append("----------------------------------------------------------------")

                    LS = moneydance_ui.getCurrentAccounts().getBook().getLocalStorage()
                    keys=sorted(LS.keys())

                    if lResetAll:

                        last = None

                        for theKey in keys:
                            value = LS.get(theKey)

                            for theTypeToCheck in dataPrefKeys_legacy:

                                if theKey.endswith("."+theTypeToCheck):

                                    if lReset:
                                        LS.put(theKey, None)
                                    else:
                                        splitKey = theKey.split('.')
                                        if splitKey[0] != last:
                                            last = splitKey[0]
                                            lookupAcct = moneydance_data.getAccountByUUID(splitKey[0])
                                            if lookupAcct:
                                                configData.append("\n>>Account: %s" %(lookupAcct.getAccountName()))
                                            else:
                                                configData.append("\n>>Account: <NOT FOUND> ???")

                                        configData.append("LS Key: %s Value: %s" %(pad(theKey+":",55),str(value).strip()))

                            # Now look for keys not linked to Accounts... Perhaps deleted ones?
                            for theTypeToCheck in _COLWIDTHS:

                                if theKey.endswith(".col_widths."+theTypeToCheck):

                                    splitKey = theKey.split('.')
                                    lookupAcct = moneydance_data.getAccountByUUID(splitKey[0])

                                    if lookupAcct: continue     # Found one, probably caught above, so skip

                                    if lReset:
                                        LS.put(theKey, None)
                                    else:
                                        if splitKey[0] != last:
                                            last = splitKey[0]
                                            configData.append("\n>>Account: <NOT FOUND> ??? (probably a deleted account)")

                                        configData.append("LS Key: %s Value: %s" %(pad(theKey+":",55),str(value).strip()))

                    if lResetRegFilters or lResetRegViews:

                        last = None

                        for theKey in keys:
                            value = LS.get(theKey)

                            if lResetRegFilters:
                                if not check_for_just_register_filters_window_display_data(theKey, None):
                                    continue
                            elif lResetRegViews:
                                if not check_for_just_initial_view_filters_window_display_data(theKey, None):
                                    continue
                            else:
                                myPrint("B", "@@ ERROR: RESET WINDOW DISPLAY SETTINGS - Unexpected filter!?")
                                raise(Exception("@@ ERROR: RESET WINDOW DISPLAY SETTINGS - Unexpected filter!?"))

                            if lReset:
                                LS.put(theKey, None)
                            else:
                                splitKey = theKey.split('.')
                                if splitKey[0] != last:
                                    last = splitKey[0]
                                    lookupAcct = moneydance_data.getAccountByUUID(splitKey[0])
                                    if lookupAcct:
                                        configData.append("\n>>Account: %s" %(lookupAcct.getAccountName()))
                                    else:
                                        configData.append("\n>>Account: <NOT FOUND>???")

                                configData.append("LS Key: %s Value: %s" %(pad(theKey+":",55),str(value).strip()))

                    # END OF LocalStorage() search
                    ########################################################################################################

                configData.append("\n <END>")

                for i in range(0, len(configData)):
                    configData[i] = configData[i] + "\n"

                configData = "".join(configData)

                if not lReset:
                    jif = QuickJFrame("View the relevant RESET WINDOW DISPLAY SETTINGS that will be reset if you select OK to proceed", configData).show_the_frame()
                    return jif

                return

            st,tk = read_preferences_file(lSaveFirst=False)

            if not st:
                self.statusLabel.setText("ERROR: RESET WINDOW DISPLAY SETTINGS >> reading and sorting the data file - no changes made!...".ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            myPrint("D", "\nDisplaying the relevant RESET WINDOW DISPLAY SETTINGS (in various places) that I can reset.....:\n")

            theNewViewFrame = get_set_config(st, tk, False, lAll, lWinLocations, lRegFilters, lRegViews)

            if not myPopupAskQuestion(theNewViewFrame,
                                      "RESET WINDOW DISPLAY SETTINGS",
                                      "WARNING: Have you closed all Account Register windows and made sure only the Main Home Screen / Summary page is visible first??",
                                      JOptionPane.YES_NO_OPTION,
                                      JOptionPane.WARNING_MESSAGE):
                self.statusLabel.setText("WARNING: Please close all Account Register Windows and make sure only the Main Home Screen Summary/Dashboard is visible before running the Reset Windows Sizes tool..!".ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            if not myPopupAskQuestion(theNewViewFrame,
                                  "RESET WINDOW DISPLAY SETTINGS",
                                  "Are you sure you want to %s data?" %resetWhat,
                                  JOptionPane.YES_NO_OPTION,
                                  JOptionPane.ERROR_MESSAGE):

                self.statusLabel.setText("RESET WINDOW DISPLAY SETTINGS - User declined to proceed - no changes made....".ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            if not myPopupAskBackup(theNewViewFrame, "Would you like to perform a backup before RESET WINDOW DISPLAY SETTINGS?"):
                self.statusLabel.setText(("RESET WINDOW DISPLAY SETTINGS' - User chose to exit without the fix/update....").ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            disclaimer = myPopupAskForInput(theNewViewFrame,
                                            "RESET WINDOW DISPLAY SETTINGS",
                                            "DISCLAIMER:",
                                            "Are you really sure you want to %s data wherever I find it? Type 'IAGREE' to continue.." %resetWhat,
                                            "NO",
                                            False,
                                            JOptionPane.ERROR_MESSAGE)

            if not disclaimer == 'IAGREE':
                self.statusLabel.setText("User declined the disclaimer - no changes made....".ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            if not backup_config_dict():
                self.statusLabel.setText(("RESET WINDOW DISPLAY SETTINGS: ERROR making backup of config.dict - no changes made!").ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            if not backup_local_storage_settings():
                self.statusLabel.setText(("RESET WINDOW DISPLAY SETTINGS: ERROR making backup of LocalStorage() ./safe/settings - no changes made!").ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            # DO THE RESET HERE
            get_set_config(st, tk, True, lAll, lWinLocations, lRegFilters, lRegViews)

            moneydance.savePreferences()                # save config.dict
            moneydance_data.getLocalStorage().save()    # Flush local storage to safe/settings

            play_the_money_sound()

            myPopupInformationBox(theNewViewFrame, "SUCCESS - %s - PLEASE RESTART MONEYDANCE"%resetWhat, "RESET WINDOW DISPLAY SETTINGS", JOptionPane.WARNING_MESSAGE)

            myPrint("B", "SUCCESS - %s data reset in config.dict config file, internally by Account & Local Storage...."%resetWhat)

            self.statusLabel.setText(("OK - %s settings forgotten.... I SUGGEST YOU RESTART MONEYDANCE!" %resetWhat).ljust(800, " "))
            self.statusLabel.setForeground(Color.RED)

            return


    class ChangeFontsButtonAction(AbstractAction):

        def __init__(self, statusLabel):
            self.statusLabel = statusLabel

        def actionPerformed(self, event):
            global Toolbox_frame_, debug
            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

            if moneydance.getBuild() < 3030:
                myPrint("B", "Error - must be on Moneydance build 3030+ to change fonts!")
                self.statusLabel.setText(("Error - must be on Moneydance build 3030+ to change fonts!").ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            myPrint("DB", "User requested to change Moneydance Default Fonts!")

            if not backup_config_dict():
                self.statusLabel.setText("Error backing up config.dict preferences file before deletion - no changes made....".ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            prefs=moneydance_ui.getPreferences()

            systemFonts = GraphicsEnvironment.getLocalGraphicsEnvironment().getAvailableFontFamilyNames()
            for installedFont in systemFonts:
                myPrint("D","System OS Font %s is installed in your system..:" %installedFont)

            # These are taken from MD Code - build 3030 - watch out they may change...!
            Mac_fonts_main =     ["SF Pro Display", "SF Display", "Helvetica Neue", "Helvetica", "Lucida Grande", "Dialog"]
            Mac_fonts_mono =     ["Gill Sans", "Menlo", "Monaco", "Monospaced"]

            Windows_fonts_main = ["Dialog"]
            Windows_fonts_mono = ["Calibri","Monospaced"]

            Linux_fonts_main =   ["DejaVu Sans","Dialog"]
            Linux_fonts_mono =   ["Monospaced"]

            lExit=False
            lAnyFontChanges=False

            while True:
                if lExit: break

                mainF = prefs.getSetting("main_font", None)
                monoF = prefs.getSetting("mono_font", None)

                myPrint("DB",'@@ MONEYDANCE: Config.dict: "main_font" currently set to %s' %mainF)
                myPrint("DB",'@@ MONEYDANCE: Config.dict: "mono_font" currently set to %s' %monoF)

                display_main="None(Moneydance defaults)"
                display_mono="None(Moneydance defaults)"
                if mainF: display_main = mainF
                if monoF: display_mono = monoF

                MyPopUpDialogBox(Toolbox_frame_,"Config.dict - CURRENT FONTS:",
                                                '"main_font" currently set to %s\n"mono_font" currently set to %s' %(display_main,display_mono),
                                                150,"FONTS",OKButtonText="CONTINUE").go()

                _options=["MAIN: CHANGE SETTING", "MAIN: DELETE SETTING", "MONO: CHANGE SETTING", "MONO: DELETE SETTING"]
                selectedOption = JOptionPane.showInputDialog(Toolbox_frame_,
                                                             "What type of change do you want to make?",
                                                             "ALTER FONTS",
                                                             JOptionPane.WARNING_MESSAGE,
                                                             None,
                                                             _options,
                                                             None)

                if not selectedOption:
                    break

                lMain = (_options.index(selectedOption) == 0 or _options.index(selectedOption) == 1)
                lMono = (_options.index(selectedOption) == 2 or _options.index(selectedOption) == 3)

                lDelete = (_options.index(selectedOption) == 1 or _options.index(selectedOption) == 3)
                lChange = (_options.index(selectedOption) == 0 or _options.index(selectedOption) == 2)

                if lMain:
                    theKey = "main_font"
                elif lMono:
                    theKey = "mono_font"
                else:
                    raise(Exception("error"))

                if lDelete:
                    if myPopupAskQuestion(Toolbox_frame_,"DELETE FONT KEY","Are you sure you want to delete key: %s?" %theKey,JOptionPane.YES_NO_OPTION,JOptionPane.WARNING_MESSAGE):
                        prefs.setSetting(theKey,None)
                        moneydance.savePreferences()
                        lAnyFontChanges=True
                        myPrint("B", "Config.dict: key: %s DELETED - RESTART MD" %theKey)
                        myPopupInformationBox(None, "Config.dict: key: %s DELETED - RESTART MD" %theKey, "FONTS", JOptionPane.WARNING_MESSAGE)
                        continue
                    else:
                        continue

                elif lChange:

                    theFonts = None                                                                                 # noqa
                    if Platform.isOSX():
                        if lMain:
                            theFonts = Mac_fonts_main
                        elif lMono:
                            theFonts = Mac_fonts_mono
                        else: raise(Exception("error"))
                    elif Platform.isWindows():
                        if lMain:
                            theFonts = Windows_fonts_main
                        elif lMono:
                            theFonts = Windows_fonts_mono
                        else: raise(Exception("error"))
                    else:
                        if lMain:
                            theFonts = Linux_fonts_main
                        elif lMono:
                            theFonts = Linux_fonts_mono
                        else: raise(Exception("error"))

                    for x in theFonts:
                        myPrint("D","Possible internal default fonts for your Platform...: %s" %x)

                    # _options=["EXIT", "CHOOSE FROM MD INTERNAL LIST", "CAREFULLY ENTER YOUR OWN", "CHOOSE FROM SYSTEM INSTALLED"]
                    _options=["CHOOSE FROM MD INTERNAL LIST", "CHOOSE FROM YOUR OS' SYSTEM INSTALLED"]
                    selectedOption = JOptionPane.showInputDialog(Toolbox_frame_,
                                                                 "New Font Selection options for: %s?" %theKey,
                                                                 "ALTER FONTS",
                                                                 JOptionPane.WARNING_MESSAGE,
                                                                 None,
                                                                 _options,
                                                                 None)

                    if not selectedOption:
                        continue

                    if _options.index(selectedOption) == 0 or _options.index(selectedOption) == 1:

                        if _options.index(selectedOption) == 1: theFonts = systemFonts
                        selectedFont = JOptionPane.showInputDialog(Toolbox_frame_,
                                                                   "Select new Font to set for %s" %theKey,
                                                                   "ALTER FONTS",
                                                                   JOptionPane.WARNING_MESSAGE,
                                                                   None,
                                                                   theFonts,
                                                                   None)
                        if not selectedFont:
                            continue
                        else:
                            prefs.setSetting(theKey,selectedFont)
                            moneydance.savePreferences()
                            lAnyFontChanges=True
                            myPrint("B", 'Config.dict: key: %s CHANGED to "%s" - RESTART MD' %(theKey,selectedFont))
                            myPopupInformationBox(Toolbox_frame_, 'Config.dict: key: %s CHANGED to "%s"\nRESTART MD' %(theKey,selectedFont), "FONTS", JOptionPane.WARNING_MESSAGE)
                            continue

                    # elif _options.index(selectedOption) == 2:
                    #
                    #     if lMain: currentFont = mainF
                    #     elif lMono: currentFont = monoF
                    #     else: raise(Exception("error"))
                    #
                    #     newFont = myPopupAskForInput(None,
                    #                        "CHANGE FONT",
                    #                        "New Font",
                    #                        "Carefully type the name of the new Font",
                    #                        currentFont,
                    #                        False,
                    #                        JOptionPane.WARNING_MESSAGE)
                    #
                    #     if newFont == "" or newFont == currentFont:
                    #         lExit = True
                    #         myPrint("P", "NO FONT ACTION TAKEN")
                    #         myPopupInformationBox(None, "NO FONT ACTION TAKEN!", "FONTS", JOptionPane.WARNING_MESSAGE)
                    #         continue
                    #     else:
                    #         prefs.setSetting(theKey,newFont)
                    #         moneydance.savePreferences()
                    #         myPrint("B", 'Config.dict: key: %s CHANGED to "%s" - RESTART MD' %(theKey,newFont))
                    #         myPopupInformationBox(None, 'Config.dict: key: %s CHANGED to "%s"\nRESTART MD' %(theKey,newFont), "FONTS", JOptionPane.WARNING_MESSAGE)
                    #         continue
                    else:
                        raise(Exception("error"))

                continue

            if lAnyFontChanges:
                self.statusLabel.setText("Moneydance Font Changes made as requested - PLEASE RESTART MONEYDANCE (PS - config.dict was backed up too)....".ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
            else:
                myPrint("D", "NO FONT ACTIONS TAKEN")
                self.statusLabel.setText("NO FONT ACTIONS TAKEN! - no changes made....".ljust(800, " "))
                self.statusLabel.setForeground(Color.BLUE)
                myPopupInformationBox(Toolbox_frame_, "NO FONT ACTIONS TAKEN!", "FONTS", JOptionPane.WARNING_MESSAGE)


            myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
            return

    class DeleteConfigFileButtonAction(AbstractAction):

        def __init__(self, statusLabel):
            self.statusLabel = statusLabel

        def actionPerformed(self, event):
            global Toolbox_frame_, debug
            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

            myPrint("DB", "User requested to delete MD Config/Preferences file!")

            prefFile = str(Common.getPreferencesFile())
            if not os.path.exists(prefFile):
                self.statusLabel.setText(("Config/Preferences file %s does not exist to delete!" %prefFile).ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            if not myPopupAskQuestion(Toolbox_frame_,
                                  "DELETE MD Config/Preferences file?",
                                  "Are you **REALLY** **REALLY** sure you want to delete MD Config/Preferences file?",
                                      JOptionPane.YES_NO_OPTION,
                                      JOptionPane.ERROR_MESSAGE):
                self.statusLabel.setText("User declined to delete Config/Preferences file!".ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            myPrint("DB", "User confirmed to delete Config/Preferences file...")

            doubleCheck = myPopupAskForInput(Toolbox_frame_,
                                            "DELETE CONFIG.DICT",
                                            "DISCLAIMER:",
                                             "Type: 'DELETEIT' to delete the Config file.",
                                            "NO",
                                             False,
                                             JOptionPane.ERROR_MESSAGE)

            if not doubleCheck == "DELETEIT":
                self.statusLabel.setText("User chickened out on deleting Config/Preferences file!".ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            if not backup_config_dict():
                self.statusLabel.setText("Error backing up config.dict preferences file before deletion - no changes made....".ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            try:
                os.remove(prefFile)
                myPrint("B","Config file deleted! %s"+prefFile)
                play_the_money_sound()
                self.statusLabel.setText(("DELETED CONFIG/PREFERENCES FILE: I SUGGEST YOU RESTART MONEYDANCE!" + prefFile).ljust(800, " "))
                myPopupInformationBox(Toolbox_frame_, "CONFIG.DICT DELETED (Pointless!)", "DELETE CONFIG.DICT", JOptionPane.ERROR_MESSAGE)

            except:
                dump_sys_error_to_md_console_and_errorlog()
                self.statusLabel.setText(("ERROR DELETING CONFIG/PREFERENCES FILE??!!").ljust(800, " "))

            self.statusLabel.setForeground(Color.RED)

            myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
            return

    class ViewFileButtonAction(AbstractAction):
        class CloseAction(AbstractAction):

            def __init__(self, the_frame):
                self.theFrame = the_frame

            # noinspection PyUnusedLocal
            def actionPerformed(self, event):
                global debug
                myPrint("DB", "Inner View File Frame shutting down....")
                self.theFrame.dispose()
                return

        def __init__(self, statusLabel, theFile, displayText, lFile=True):
            self.statusLabel = statusLabel
            self.theFile = theFile
            self.displayText = displayText
            self.lFile = lFile

        def actionPerformed(self, event):
            global Toolbox_frame_, debug, myParameters, lIgnoreOutdatedExtensions_TB
            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

            lViewExtensions=False
            lDisplayPickle=False

            x = str(self.theFile)

            if x == "display_pickle()":
                x = display_pickle()
                lDisplayPickle=True

            if x == "display_help()":
                x = display_help()

            if x == "get_list_memorised_reports()":
                x = get_list_memorised_reports()

            if x == "get_ofx_related_data()":
                x = get_ofx_related_data()

            if x == "get_register_txn_sort_orders()":
                x = get_register_txn_sort_orders()

            if x == "view_check_num_settings()":
                x = view_check_num_settings(self.statusLabel)

            if x == "view_extensions_details()":
                x = view_extensions_details()
                lViewExtensions=True

            if x == "can_I_delete_security()":
                x = can_I_delete_security(self.statusLabel)
                if not x: return

            if x == "list_security_currency_decimal_places()":
                x = list_security_currency_decimal_places(self.statusLabel)
                if not x: return

            if x == "diagnose_currencies(False)":
                x = diagnose_currencies(self.statusLabel, False)
                if not x: return

            if x == "diagnose_currencies(True)":
                x = diagnose_currencies(self.statusLabel, True)
                if not x: return

            if not self.lFile:
                myPrint("DB", "User requested to view " + self.displayText + "data!")
                if not x or x == "":
                    if x:
                        self.statusLabel.setText(("Sorry - " + self.displayText + " data is empty!?: " + x).ljust(800, " "))
                        self.statusLabel.setForeground(Color.RED)
                    return
            else:
                myPrint("DB", "User requested to view " + self.displayText + "file!")
                if not os.path.exists(x):
                    self.statusLabel.setText(("Sorry - " + self.displayText + " file does not exist or is not available to view!?: " + x).ljust(800, " "))
                    self.statusLabel.setForeground(Color.RED)
                    return

            if not self.lFile:
                displayFile = x
            else:
                try:
                    with open(x, "r") as myFile:
                        displayFile = myFile.readlines()
                    # displayFile = '\n'.join(displayFile)

                    # If VMOptions, stick a "'" at the beginning for clipboard to Excel to work OK
                    if lCopyAllToClipBoard_TB and x.lower().endswith(".vmoptions"):
                        newDisplayFile=[]
                        for line in displayFile:
                            line ="'"+line
                            newDisplayFile.append(line)
                        displayFile = newDisplayFile
                    else:
                        displayFile.append("\n<END>")

                    displayFile = ''.join(displayFile)
                except:
                    displayFile = "Sorry - error opening file...."
                    dump_sys_error_to_md_console_and_errorlog()

            if x.lower().endswith(".vmoptions"):
                displayFile += """
-------------------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------------------
<INSTRUCTIONS>
You can allow for more memory by editing the 'Moneydance.vmoptions' file and set it to increase the amount of memory that Moneydance is allowed to use.
To achieve this you can try the following.

Navigate to the Moneydance.vmoptions file, located in the folder where Moneydance is installed, so most likely:

Windows - c:\Program Files\Moneydance\Moneydance.vmoptions
or
Linux - /opt/Moneydance/Moneydance.vmoptions

If you open that file with Notepad or any other text editor, you'll see some instructions for how to change it.
Close Moneydance first!
The basic recommendation is to changing the -Xmx1024m setting to -Xmx2048m which doubles the amount of memory that Moneydance is allowed to use.
You can give it more if you wish, E.g.: you make it -Xmx3000m, for optimal results.

In Windows - due to permissions, you might need to do this:
    In the 'Type here to Search' box on the Windows 10 Toolbar, type CMD (do not press enter)
    When Command Prompt appears, click Run as Administrator
    Click yes/agree to allow this app to make changes to this device / grant administrator permissions
    cd "\Program Files\Moneydance"      (and enter)
    notepad Moneydance.vmoptions        (and enter)
    edit the file and change the -Xmx1024 setting
    ctrl-s to save and then exit Notepad
    exit
    restart Moneydance
    
The limit is set deliberately low to enable it to work with computers having very small amounts of RAM.
-------------------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------------------
                """ # noqa

            if self.lFile:
                jif = QuickJFrame("View " + self.displayText + " file: " + x, displayFile).show_the_frame()
            else:
                jif = QuickJFrame("View " + self.displayText + " data", displayFile).show_the_frame()

            if lViewExtensions and lIgnoreOutdatedExtensions_TB:
                if myPopupAskQuestion(jif,
                                      "OUTDATED EXTENSIONS",
                                      "Turn startup warnings back on for Outdated Extns?",
                                      JOptionPane.YES_NO_OPTION,
                                      JOptionPane.QUESTION_MESSAGE):

                    self.statusLabel.setText(("OUTDATED EXTENSIONS - Startup warnings re-enabled").ljust(800, " "))
                    self.statusLabel.setForeground(Color.BLUE)
                    myPrint("B", "OUTDATED EXTENSIONS - Startup warnings re-enabled" )
                    lIgnoreOutdatedExtensions_TB = False

            if lDisplayPickle:

                if not myPopupAskQuestion(jif,
                                        "STUWARESOFTSYSTEMS' SAVED PARAMETERS PICKLE FILE",
                                        "Would you like to RESET/DELETE/EDIT saved parameters?",
                                        JOptionPane.YES_NO_OPTION,
                                        JOptionPane.WARNING_MESSAGE):
                    return

                _PICKLEDELALL          = 0
                _PICKLECHGONE          = 1
                _PICKLEDELONE          = 2
                _PICKLEADDONE          = 3

                what = ["PICKLE: DELETE ALL","PICKLE: CHANGE one variable","PICKLE: DELETE one variable", "PICKLE: ADD one variable"]

                while True:

                    lAdd = lChg = lDelAll = lDelOne = False
                    selectedWhat = JOptionPane.showInputDialog(jif, "STUWARESOFTSYSTEMS' SAVED PARAMETERS PICKLE FILE",
                                                               "Select the type of change you want to make?",
                                                               JOptionPane.WARNING_MESSAGE,
                                                               None,
                                                               what,
                                                               None)

                    if not selectedWhat: return

                    if selectedWhat == what[_PICKLEADDONE]: lAdd = True
                    if selectedWhat == what[_PICKLECHGONE]: lChg = True
                    if selectedWhat == what[_PICKLEDELONE]: lDelOne = True
                    if selectedWhat == what[_PICKLEDELALL]: lDelAll = True

                    if lDelAll:
                        myParameters = {}
                        self.statusLabel.setText(("STUWARESOFTSYSTEMS' PARAMETERS SAVED TO PICKLE FILE DELETED/RESET").ljust(800, " "))
                        self.statusLabel.setForeground(DARK_GREEN)
                        myPrint("B", "STUWARESOFTSYSTEMS' PARAMETERS SAVED TO PICKLE FILE DELETED/RESET" )
                        return

                    text = ""
                    if lChg: text = "CHANGE"
                    if lDelOne: text = "DELETE"

                    if lAdd:
                        addKey = myPopupAskForInput(jif,
                                                    "PICKLE: ADD KEY",
                                                    "KEY NAME:",
                                                    "Carefully enter the name of the key you want to add (cAseMaTTers!) - STRINGS ONLY:",
                                                    "",
                                                    False,
                                                    JOptionPane.WARNING_MESSAGE)

                        if not addKey or len(addKey) < 1: continue
                        addKey = addKey.strip()

                        if not check_if_key_string_valid(addKey):
                            myPopupInformationBox(jif, "ERROR: Key %s is NOT valid!" % addKey, "PICKLE: ADD", JOptionPane.ERROR_MESSAGE)
                            continue    # back to menu

                        testKeyExists = myParameters.get(addKey)

                        if testKeyExists:
                            myPopupInformationBox(jif, "ERROR: Key %s already exists - cannot add - aborting..!" % addKey, "PICKLE: ADD", JOptionPane.ERROR_MESSAGE)
                            continue    # back to menu

                        addValue = myPopupAskForInput(jif,
                                                      "PICKLE: ADD KEY VALUE",
                                                      "KEY VALUE:",
                                                      "Carefully enter the key value you want to add (STRINGS ONLY!):",
                                                      "",
                                                      False,
                                                      JOptionPane.WARNING_MESSAGE)

                        if not addValue or len(addValue) <1: continue
                        addValue = addValue.strip()

                        if not check_if_key_string_valid(addValue):
                            myPopupInformationBox(Toolbox_frame_, "ERROR: Key value %s is NOT valid!" % addValue, "PICKLE: ADD ", JOptionPane.ERROR_MESSAGE)
                            continue    # back to menu

                        myParameters[addKey] = addValue
                        myPrint("B","@@ PICKLEMODE: key: %s value: %s added @@" %(addKey,addValue))
                        myPopupInformationBox(jif,
                                              "SUCCESS: Key %s added!" % (addKey),
                                              "PICKLE: ADD ",
                                              JOptionPane.WARNING_MESSAGE)
                        continue

                    pickleKeys=sorted( myParameters.keys() )
                    # OK, so we are changing or deleting
                    if lChg or lDelOne:
                        selectedKey = JOptionPane.showInputDialog(jif, "PICKLE",
                                                                  "Select the key/setting you want to %s" % (text),
                                                                  JOptionPane.WARNING_MESSAGE,
                                                                  None,
                                                                  pickleKeys,
                                                                  None)
                        if not selectedKey: continue

                        value = myParameters.get(selectedKey)
                        chgValue = None

                        if lChg:
                            chgValue = myPopupAskForInput(jif,
                                                          "PICKLE: CHANGE KEY VALUE",
                                                          "KEY VALUE:",
                                                          "Carefully enter the new key value (as type: %s):" %type(value),
                                                          str(value),
                                                          False,
                                                          JOptionPane.WARNING_MESSAGE)

                            if not chgValue or len(chgValue) <1 or chgValue == value: continue
                            chgValue = chgValue.strip()

                            if isinstance(value, (int, float, bool, list)):
                                try:
                                    if isinstance(eval(chgValue), type(value) ):
                                        chgValue = eval(chgValue)
                                    else:
                                        myPopupInformationBox(jif,"ERROR: you must match the variable type to %s" %(type(value)),"PICKLE: CHANGE",JOptionPane.ERROR_MESSAGE)
                                        continue
                                except:
                                    myPopupInformationBox(jif,"ERROR: *EVAL* Could not set Key value %s - type %s" %(chgValue,type(value)),"PICKLE: CHANGE",JOptionPane.ERROR_MESSAGE)
                                    continue
                            elif isinstance(value,(str,unicode)):
                                if not check_if_key_string_valid(chgValue):
                                    myPopupInformationBox(jif,"ERROR: Key value %s is NOT valid!" %chgValue,"PICKLE: CHANGE",JOptionPane.ERROR_MESSAGE)
                                    continue    # back to menu
                            else:
                                myPopupInformationBox(jif,"SORRY: I cannot change Key value %s as it's type %s" %(chgValue,type(value)),"PICKLE: CHANGE",JOptionPane.ERROR_MESSAGE)
                                continue    # back to menu

                        if lDelOne:
                            myParameters.pop(selectedKey)
                        if lChg:
                            try:
                                myParameters[selectedKey] = chgValue
                            except:
                                myPopupInformationBox(jif,"ERROR: *set* Could not set Key value %s - type %s" %(chgValue,type(value)),"PICKLE: CHANGE",JOptionPane.ERROR_MESSAGE)
                                continue

                        if lDelOne:
                            myPrint("B","@@ PICKLEMODE: key: %s DELETED (old value: %s) @@" %(selectedKey,value))
                            myPopupInformationBox(jif,
                                                  "SUCCESS: key: %s DELETED (old value: %s)" %(selectedKey,value),
                                                  "PICKlE: DELETE",
                                                  JOptionPane.WARNING_MESSAGE)
                        if lChg:
                            myPrint("B","@@ PICKLERMODE: key: %s CHANGED to %s @@" %(selectedKey,chgValue))
                            myPopupInformationBox(jif,
                                                  "SUCCESS: key: %s CHANGED to %s" %(selectedKey,chgValue),
                                                  "PICKLE: CHANGE",
                                                  JOptionPane.WARNING_MESSAGE)
                        continue

            myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
            return

    class CopyConsoleLogFileButtonAction(AbstractAction):

        def __init__(self, statusLabel, theFile):
            self.statusLabel = statusLabel
            self.theFile = theFile

        def actionPerformed(self, event):
            global Toolbox_frame_, debug
            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

            x = str(self.theFile)
            if not os.path.exists(x):
                self.statusLabel.setText(("Sorry, the file does not seem to exist: " + x).ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            if Platform.isOSX():
                System.setProperty("com.apple.macos.use-file-dialog-packages","true")  # In theory prevents access to app file structure (but doesnt seem to work)
                System.setProperty("apple.awt.fileDialogForDirectories", "true")

            filename = FileDialog(Toolbox_frame_, "Select location to copy Console Log file to... (CANCEL=ABORT)")
            filename.setMultipleMode(False)
            filename.setMode(FileDialog.SAVE)
            filename.setFile('copy_of_errlog.txt')
            # filename.setDirectory(self.theFile.getParent())
            filename.setDirectory(get_home_dir())

            if (not Platform.isOSX() or not Platform.isOSXVersionAtLeast("10.13")):
                extFilter = ExtFilenameFilter("txt")
                filename.setFilenameFilter(extFilter)  # I'm not actually sure this works...?

            filename.setVisible(True)

            copyToFile = filename.getFile()

            if Platform.isOSX():
                System.setProperty("com.apple.macos.use-file-dialog-packages","true")  # In theory prevents access to app file structure (but doesnt seem to work)
                System.setProperty("apple.awt.fileDialogForDirectories", "false")

            if (copyToFile is None) or copyToFile == "":
                self.statusLabel.setText(("User did not select file location - no copy performed").ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return
            elif not str(copyToFile).endswith(".txt"):
                self.statusLabel.setText(
                    ("Sorry - please use a .txt file extension when copying  console log file").ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return
            elif ".moneydance" in filename.getDirectory():
                self.statusLabel.setText(
                    ("Sorry, please choose a location outside of the  Moneydance location").ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return
            else:
                # noinspection PyTypeChecker
                copyToFile = os.path.join(filename.getDirectory(), filename.getFile())

            if not check_file_writable(copyToFile):
                self.statusLabel.setText(
                    ("Sorry, that file/location does not appear allowed by the operating system!?").ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)

            try:
                toFile = File(filename.getDirectory(), filename.getFile())
                IOUtils.copy(self.theFile, toFile)
                myPrint("B", x + " copied to " + str(toFile))
                # noinspection PyTypeChecker
                if os.path.exists(os.path.join(filename.getDirectory(), filename.getFile())):
                    play_the_money_sound()
                    self.statusLabel.setText(("Console Log file copied as requested to: " + str(toFile)).ljust(800, " "))
                    self.statusLabel.setForeground(Color.RED)
                else:
                    myPrint("B", "ERROR - failed to copy file" + x + " to " + str(filename.getFile()))
                    self.statusLabel.setText(("Sorry, failed to copy console log file?!").ljust(800, " "))
                    self.statusLabel.setForeground(Color.RED)
            except:
                myPrint("B", "ERROR - failed to copy file" + x + " to " + str(filename.getFile()))
                dump_sys_error_to_md_console_and_errorlog()
                self.statusLabel.setText(("Sorry, failed to copy console log file?!").ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)

            return


    class ClipboardButtonAction(AbstractAction):
        theString = ""

        def __init__(self, theString, statusLabel):
            self.theString = theString
            self.statusLabel = statusLabel

        def actionPerformed(self, event):
            global Toolbox_frame_, debug
            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )
            x = StringSelection(self.theString)
            Toolkit.getDefaultToolkit().getSystemClipboard().setContents(x, None)

            self.statusLabel.setText(("Contents of all text below copied to Clipboard..").ljust(800, " "))
            self.statusLabel.setForeground(Color.RED)

            myPrint("DB", "Contents of diagnostic report copied to clipboard....!")

            myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
            return


    class FindDatasetButtonAction(AbstractAction):

        def __init__(self, statusLabel):
            self.statusLabel = statusLabel

        def actionPerformed(self, event):
            global Toolbox_frame_, debug, i_am_an_extension_so_run_headless

            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )


            if not myPopupAskQuestion(Toolbox_frame_,
                                      "SEARCH COMPUTER FOR MONEYDANCE DATASET(s)/BACKUP(s)",
                                      "This may be time consuming...Do you want to continue with search?",
                                      JOptionPane.YES_NO_OPTION,
                                      JOptionPane.WARNING_MESSAGE):


                self.statusLabel.setText(("User Aborted Dataset search...").ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            whatType = ["Datasets",
                         "Backups"]


            selectedWhat = JOptionPane.showInputDialog(Toolbox_frame_,
                                                        "WHAT TYPE OF DATASET?",
                                                        "Choose Datasets or Backups",
                                                       JOptionPane.INFORMATION_MESSAGE,
                                                       moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                       whatType,
                                                       None)
            if selectedWhat is None:
                self.statusLabel.setText("No Dataset Type was selected - aborting..".ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            if whatType.index(selectedWhat) == 0:
                lBackup=False
                theExtension = "*.moneydance".lower()
            elif whatType.index(selectedWhat) == 1:
                lBackup=True
                theExtension = "*.moneydancearchive".lower()
            else:
                self.statusLabel.setText("Dataset Type Error - aborting..".ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            myPrint("DB", "Dataset type: %s" %theExtension)

            if Platform.isWindows():
                theRoot = os.path.join("C:"+os.path.sep)
            else:
                theRoot = os.path.sep

            whereFrom = ["From UserDir: %s" %get_home_dir(),
                          "From Root: %s" %theRoot,
                          "Select your own start point"]

            selectedStart = JOptionPane.showInputDialog(Toolbox_frame_,
                                                           "WHERE TO SEARCH FROM",
                                                           "Select the Search start folder",
                                                        JOptionPane.INFORMATION_MESSAGE,
                                                        moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                        whereFrom,
                                                        None)
            if selectedStart is None:
                self.statusLabel.setText("No start point was selected - aborting..".ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            if whereFrom.index(selectedStart) == 2:
                if Platform.isOSX():
                    System.setProperty("com.apple.macos.use-file-dialog-packages", "true")  # In theory prevents access to app file structure (but doesnt seem to work)
                    System.setProperty("apple.awt.fileDialogForDirectories", "true")

                    fDialog = FileDialog(Toolbox_frame_, "Select location to start %s Dataset Search (CANCEL=ABORT)" % theExtension)
                    fDialog.setMultipleMode(False)
                    fDialog.setMode(FileDialog.LOAD)
                    fDialog.setDirectory(get_home_dir())

                    fDialog.setVisible(True)

                    System.setProperty("com.apple.macos.use-file-dialog-packages","true")  # In theory prevents access to app file structure (but doesnt seem to work)
                    System.setProperty("apple.awt.fileDialogForDirectories", "false")

                    if (fDialog.getDirectory() is None) or str(fDialog.getDirectory()) == "" or \
                            (fDialog.getFile() is None) or str(fDialog.getFile()) == "":
                        self.statusLabel.setText(("User did not select Search Directory... Aborting").ljust(800, " "))
                        self.statusLabel.setForeground(Color.RED)
                        return
                    # noinspection PyTypeChecker
                    theDir = os.path.join(fDialog.getDirectory(),str(fDialog.getFile()))

                else:
                    # UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName())
                    # Switch to JFileChooser for Folder selection on Windows/Linux - to allow folder selection
                    fileChooser = JFileChooser( get_home_dir() )

                    fileChooser.setMultiSelectionEnabled( False )

                    fileChooser.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY)

                    fileChooser.setDialogTitle("Select location to start %s Dataset Search (CANCEL=ABORT)"%theExtension)
                    fileChooser.setPreferredSize(Dimension(700, 700))
                    returnValue = fileChooser.showDialog(Toolbox_frame_, "START SEARCH")

                    if returnValue == JFileChooser.CANCEL_OPTION:
                        self.statusLabel.setText("No start point was selected - aborting..".ljust(800, " "))
                        self.statusLabel.setForeground(Color.RED)
                        return
                    elif fileChooser.getSelectedFile() is None or fileChooser.getSelectedFile().getName()=="":
                        self.statusLabel.setText("No start point was selected - aborting..".ljust(800, " "))
                        self.statusLabel.setForeground(Color.RED)
                        return
                    else:
                        theDir = fileChooser.getSelectedFile().getAbsolutePath()

            elif whereFrom.index(selectedStart) == 1:  # From ROOT
                theDir = theRoot
            elif whereFrom.index(selectedStart) == 0:  # From User Home Dir
                theDir = get_home_dir()
            else:
                self.statusLabel.setText(("Error Selecting Search Directory... Aborting").ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            diag = JDialog(Toolbox_frame_, "Please wait: searching..")
            label1 = JLabel(">>>Searching: ...... (PLEASE WAIT)")
            label1.setForeground(Color.BLUE)
            diag.add(label1)
            diag.setSize(400,200)
            # diag.pack()
            diag.setLocationRelativeTo(None)
            diag.setVisible(True)

            myPrint("P","Searching from Directory: %s" %theDir)

            def findDataset(pattern, path):
                iFound=0                                                                                            # noqa
                result = []
                dotCounter = 0

                lContinueToEnd=False

                if not i_am_an_extension_so_run_headless:
                    print "Searching for your %s Datasets (might be time consuming):."%theExtension,

                for root, dirs, files in os.walk(path):
                    if dotCounter % 1000 <1:
                        if not i_am_an_extension_so_run_headless: print ".",
                    if not dotCounter or (dotCounter % 10000 <1 and not lContinueToEnd):

                        options=["STOP HERE","SEARCH TO END", "KEEP ASKING"]
                        response = JOptionPane.showOptionDialog(Toolbox_frame_,
                                                                 "Are you OK to continue (%s found so far)?"%iFound,
                                                                 "SEARCH COMPUTER FOR MONEYDANCE DATASET(s)",
                                                                 0,
                                                                 JOptionPane.QUESTION_MESSAGE,
                                                                 None,
                                                                 options,
                                                                 options[2])
                        if response == 0:
                            self.statusLabel.setText(("User Aborted Dataset search...").ljust(800, " "))
                            self.statusLabel.setForeground(Color.RED)
                            return result

                        elif response == 1:
                            lContinueToEnd = True

                    dotCounter+=1

                    if lBackup:
                        for name in files:
                            if fnmatch.fnmatch(name, pattern):
                                result.append("File: "+os.path.join(root, name))
                    for name in dirs:
                        if fnmatch.fnmatch(name, pattern):
                            iFound+=1
                            result.append("Dir: "+os.path.join(root, name))
                    for name in root:
                        if fnmatch.fnmatch(name, pattern):
                            iFound+=1
                            result.append("Root: "+os.path.join(root, name))
                return result

            fileList = findDataset(theExtension, theDir)

            diag.setVisible(False)
            diag.dispose()

            iFound = len(fileList)
            print
            myPrint("B","Completed search for %s datafiles: %s found" %(theExtension,iFound))

            niceFileList="\n SEARCH FOR MONEYDANCE (%s) DATASETS\n"%theExtension
            niceFileList+="Search started from Directory: %s\n\n"%theDir
            if not iFound:
                niceFileList+="\n<NONE FOUND>\n"

            for x in fileList:
                myPrint("B","Found: %s" %x)
                niceFileList+=x+"\n"

            self.statusLabel.setText(("Find my %s datasets(s) found %s possible files/directories" %(theExtension,iFound)).ljust(800, " "))
            self.statusLabel.setForeground(DARK_GREEN)

            jif=QuickJFrame("LIST OF MONEYDANCE %s DATASETS FOUND" % theExtension, niceFileList).show_the_frame()

            myPopupInformationBox(jif, "%s %s Datasets located...." %(iFound,theExtension), "DATASET SEARCH", JOptionPane.INFORMATION_MESSAGE)

            myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
            return

    class OpenFolderButtonAction(AbstractAction):
        theString = ""

        def __init__(self, theString, statusLabel):
            self.theString = theString
            self.statusLabel = statusLabel

        def actionPerformed(self, event):
            global Toolbox_frame_, debug

            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

            helper = moneydance.getPlatformHelper()

            grabProgramDir = find_the_program_install_dir()
            if not os.path.exists((grabProgramDir)): grabProgramDir = None

            locations = [
                    "Show Preferences (config.dict) Folder",
                    "Show custom themes Folder",
                    "Show Console (error) log Folder",
                    "Show Contents of your current Dataset Folder",
                    "Show Extensions Folder",
                    "Show Auto Backup Folder",
                    "Show Last used (Manual) Backup Folder"]
            if grabProgramDir:
                locations.append("Open Program's Install Directory")

            # noinspection PyUnresolvedReferences
            locationsDirs = [
                    Common.getPreferencesFile(),
                    theme.Theme.customThemeFile,
                    moneydance.getLogFile(),
                    moneydance_data.getRootFolder(),
                    Common.getFeatureModulesDirectory(),
                    FileUtils.getBackupDir(moneydance.getPreferences()),
                    File(moneydance_ui.getPreferences().getSetting("backup.last_saved", ""))]

            if grabProgramDir:
                locationsDirs.append(File(grabProgramDir))

            selectedFolder = JOptionPane.showInputDialog(Toolbox_frame_, "Select Folder",
                                                         "Select the Folder you would like to open",
                                                         JOptionPane.INFORMATION_MESSAGE,
                                                         moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                         locations,
                                                         None)
            if not selectedFolder:
                self.statusLabel.setText(("No folder was selected to open..").ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            if not os.path.exists(str(locationsDirs[locations.index(selectedFolder)])):
                self.statusLabel.setText(("Sorry - File/Folder does not exist!").ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            helper.openDirectory(locationsDirs[locations.index(selectedFolder)])
            self.statusLabel.setText(("Folder " + selectedFolder + " opened..: " + str(
                    locationsDirs[locations.index(selectedFolder)])).ljust(800, " "))
            self.statusLabel.setForeground(Color.BLUE)

            myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
            return

    class ForgetOFXButtonAction(AbstractAction):
        theString = ""

        def __init__(self, theString, statusLabel):
            self.theString = theString
            self.statusLabel = statusLabel

        def actionPerformed(self, event):
            global Toolbox_frame_, debug

            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

            accounts = AccountUtil.allMatchesForSearch(moneydance_data, MyAcctFilter(10))

            selectedAccount = JOptionPane.showInputDialog(Toolbox_frame_, "Select an account (only these have remembered links)",
                                                          "FORGET OFX banking link",
                                                          JOptionPane.WARNING_MESSAGE,
                                                          None,
                                                          accounts.toArray(),
                                                          None)
            if not selectedAccount:
                self.statusLabel.setText(("No Account was selected - no changes made..").ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            if not myPopupAskQuestion(Toolbox_frame_,
                                  "RESET BANKING LINK",
                                  "Are you sure you want to forget OFX banking Import link for Acct: %s" %selectedAccount,
                                  JOptionPane.YES_NO_OPTION,
                                  JOptionPane.ERROR_MESSAGE):
                self.statusLabel.setText(("User did not say yes to forget OFX banking Import link - no changes made").ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            if not myPopupAskBackup(Toolbox_frame_, "Would you like to perform a backup before you FORGET OFX BANKING IMPORT LINK?"):
                self.statusLabel.setText(("RESET BANKING LINK - User chose to exit without the fix/update...").ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            disclaimer = myPopupAskForInput(Toolbox_frame_,"RESET BANKING LINK",
                                            "DISCLAIMER:", "Are you really sure you want to FORGET BANKING OFX IMPORT LINK? Type 'IAGREE' to continue..",
                                            "NO",
                                            False,
                                            JOptionPane.ERROR_MESSAGE)

            if not disclaimer == 'IAGREE':
                self.statusLabel.setText(("FORGET OFX BANKING IMPORT LINK - User declined Disclaimer... No fixes applied").ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            selectedAccount.removeParameter("ofx_import_acct_num")                                          # noqa
            selectedAccount.removeParameter("ofx_import_remember_acct_num")                                 # noqa
            selectedAccount.syncItem()                                                                      # noqa

            self.statusLabel.setText(("OFX Banking Import link successfully forgotten!").ljust(800, " "))
            self.statusLabel.setForeground(Color.RED)
            myPrint("B", "User selected to forget OFX banking Import link for account: " + str(selectedAccount))

            play_the_money_sound()

            myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
            return

    class ConvertSecondaryButtonAction(AbstractAction):
        theString = ""

        def __init__(self, theString, statusLabel):
            self.theString = theString
            self.statusLabel = statusLabel

        def actionPerformed(self, event):
            global Toolbox_frame_, debug

            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

            if moneydance_data.getLocalStorage().getBoolean("_is_master_node", True):
                self.statusLabel.setText(("Your dataset is already Master - no changes made..").ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            if myPopupAskQuestion(Toolbox_frame_,
                                  "MAKE this SECONDARY a PRIMARY/MASTER NODE",
                                  "Are you sure you want to make this secondary dataset the Primary?",
                                  JOptionPane.YES_NO_OPTION,
                                  JOptionPane.ERROR_MESSAGE):

                if not backup_local_storage_settings():
                    self.statusLabel.setText(("MAKE ME PRIMARY: ERROR making backup of LocalStorage() ./safe/settings - no changes made!").ljust(800, " "))
                    self.statusLabel.setForeground(Color.RED)
                    return

                moneydance_data.getLocalStorage().put("_is_master_node", True)
                moneydance_data.getLocalStorage().save()        # Flush local storage to safe/settings

                self.statusLabel.setText(("I have promoted your dataset to a Primary/Master Node/Dataset - I RECOMMEND THAT YOU EXIT & RESTART!".ljust(800, " ")))
                self.statusLabel.setForeground(Color.RED)
                myPopupInformationBox(Toolbox_frame_, "THIS IS NOW A PRIMARY / MASTER DATASET\nPLEASE EXIT & RESTART!", "PRIMARY DATASET", JOptionPane.WARNING_MESSAGE)

                myPrint("B", "Dataset promoted to a Master Node")
                play_the_money_sound()
            else:
                self.statusLabel.setText(("User did not say yes to Master Node promotion - no changes made").ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)

            myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
            return


    class FixDeleteOneSidedTxnsButtonAction(AbstractAction):
        theString = ""

        def __init__(self, theString, statusLabel):
            self.theString = theString
            self.statusLabel = statusLabel

        def actionPerformed(self, event):
            global Toolbox_frame_, debug

            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

            myPrint("B", "Script running to analyse whether you have any one sided transactions - usually from Quicken Imports....")
            myPrint("P", "--------------------------------------------------------------------------------------------------------")

            book = moneydance.getCurrentAccountBook()
            txnSet = book.getTransactionSet()
            txns = txnSet.iterableTxns()

            output = ""
            toDelete = []

            output +="\nLIST OF ONE SIDED TRANSACTIONS (usually from Quicken Imports)\n"
            output +="-------------------------------------------------------------\n"

            for txn in txns:
                if txn.getOtherTxnCount() == 0:
                    output += pad(str(txn.getUUID()),50)+" "
                    output += "Date: "+pad(str(txn.getDateInt()),15)
                    output += pad(str(txn.getAccount()),25)
                    output += pad(str(txn.getAccount().getAccountType()),25)
                    output += pad(str(txn.getTransferType()),15)
                    output += rpad(str(txn.getValue()),12)
                    output += "\n"

                    toDelete.append(txn)

            if not len(toDelete)>0:
                myPrint("J","Congratulations - You have no one-sided transactions to delete!!")

                myPopupInformationBox(Toolbox_frame_, "Congratulations - You have no one-sided transactions to delete!!", "DELETE ONE-SIDE TXNS", JOptionPane.INFORMATION_MESSAGE)

                self.statusLabel.setText(("Congratulations - You have no one-sided transactions to delete!!").ljust(800, " "))
                self.statusLabel.setForeground(DARK_GREEN)
                return

            output += "\n<END>"

            jif=QuickJFrame("LIST OF ONE SIDED TRANSACTIONS (usually from Quicken Imports)", output).show_the_frame()

            myPrint("J","You have %s one-sided transactions that can be deleted!!"%len(toDelete))
            myPopupInformationBox(jif, "You have %s one-sided transactions that can de deleted!!"%len(toDelete), "DELETE ONE-SIDE TXNS", JOptionPane.WARNING_MESSAGE)

            if not myPopupAskQuestion(jif,
                                      "DELETE ONE-SIDED TRANSACTIONS?",
                                      "Are you sure you want to delete %s one-sided transactions?" % len(toDelete),
                                      JOptionPane.YES_NO_OPTION,
                                      JOptionPane.ERROR_MESSAGE):

                self.statusLabel.setText(("User declined to delete one-sided transactions").ljust(800, " "))
                self.statusLabel.setForeground(DARK_GREEN)
                return

            if not myPopupAskBackup(jif, "Would you like to perform a backup before DELETING %s ONE-SIDED TRANSACTIONS" % len(toDelete)):
                self.statusLabel.setText(("'FIX: Delete %s One-Sided Transactions' - User chose to exit without the fix/update...."%len(toDelete)).ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            disclaimer = myPopupAskForInput(jif,
                                             "DELETE ONE-SIDED TRANSACTIONS",
                                             "DISCLAIMER:",
                                             "Are you really sure you want to delete %s one-sided transactions? Type 'IAGREE' to continue..",
                                             "NO",
                                             False,
                                             JOptionPane.ERROR_MESSAGE)


            if disclaimer == 'IAGREE':
                myPrint("B", "User accepted disclaimer to delete one-sided transactions. Proceeding.....")

                for t in toDelete:
                    myPrint("J", "Item %s deleted"%t.getUUID())
                    t.deleteItem()

                myPrint("B", "Deleted %s invalid one-sided transactions" % len(toDelete))
                play_the_money_sound()
                self.statusLabel.setText(("%s One-Sided Transactions DELETED!" %len(toDelete)).ljust(800, " "))
                self.statusLabel.setForeground(DARK_GREEN)
                myPopupInformationBox(jif,"Congratulations - All One Sided Transactions DELETED!!", "DELETE ONE-SIDE TXNS", JOptionPane.WARNING_MESSAGE)
            else:
                myPrint("B", "User declined final IAGREE confirmation to delete %s one-sided transactions - no changes applied..."%len(toDelete))
                self.statusLabel.setText(("User declined final IAGREE confirmation to delete %s one-sided transactions - no changes applied..."%len(toDelete)).ljust(800," "))
                self.statusLabel.setForeground(Color.RED)
                return

            myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
            return


    class FixRootAccountNameButtonAction(AbstractAction):
        theString = ""

        def __init__(self, theString, statusLabel):
            self.theString = theString
            self.statusLabel = statusLabel

        def actionPerformed(self, event):
            global Toolbox_frame_, debug

            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

            bookName = moneydance.getCurrentAccountBook().getName().strip()
            root = moneydance.getCurrentAccountBook().getRootAccount()
            rootName = root.getAccountName().strip()

            if rootName == bookName:
                myPopupInformationBox(Toolbox_frame_,
                                      "The name of your Root Account is already the same as your Dataset(or 'Book'): %s" % bookName,
                                      "RENAME ROOT ACCOUNT",
                                      JOptionPane.INFORMATION_MESSAGE)
                self.statusLabel.setText(("No changed applied as your Root Account name is already the same as your Dataset ('Book') name:" + bookName).ljust(800, " "))
                self.statusLabel.setForeground(DARK_GREEN)
                return

            myPrint("B", "User requested to fix Root Account Name")
            myPrint("B", "Dataset's ('Book') Name: ", bookName)
            myPrint("B", "Root's Account Name: ", rootName)

            myPopupInformationBox(Toolbox_frame_,
                                  "Dataset ('Book'): %s\n\nRoot: %s" % (bookName, rootName),
                                  "RENAME ROOT ACCOUNT",
                                  JOptionPane.INFORMATION_MESSAGE)

            if not myPopupAskQuestion(Toolbox_frame_,
                                      "RENAME ROOT ACCOUNT?",
                                      "Are you sure you want to rename your Root Account to: %s?" % bookName,
                                      JOptionPane.YES_NO_OPTION,
                                      JOptionPane.ERROR_MESSAGE):
                self.statusLabel.setText(("User declined to rename Root - no changes applied").ljust(800, " "))
                self.statusLabel.setForeground(DARK_GREEN)
                return

            if not myPopupAskBackup(Toolbox_frame_, "Would you like to perform a backup before RENAMING ROOT ACCOUNT?" ):
                self.statusLabel.setText(("'FIX: Rename Root Account' - User chose to exit without the fix/update...").ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            disclaimer = myPopupAskForInput(Toolbox_frame_,
                                            "RENAME ROOT ACCOUNT",
                                            "DISCLAIMER:",
                                            "Are you really sure you want to rename your Root Account? Type 'IAGREE' to continue..",
                                            "NO",
                                            False,
                                            JOptionPane.ERROR_MESSAGE)


            if disclaimer == 'IAGREE':
                myPrint("B", "User accepted disclaimer to reset Root Account Name. Proceeding.....")
                # Flush all in memory settings to config.dict file on disk
                moneydance.savePreferences()

                root.setAccountName(bookName)
                root.syncItem()

                myPrint("B", "Root account renamed to: %s" % bookName)

                play_the_money_sound()

                self.statusLabel.setText(("Root Account Name changed to : %s - I SUGGEST YOU RESTART MONEYDANCE!" % bookName.ljust(800, " ")))
                self.statusLabel.setForeground(DARK_GREEN)

            else:
                myPrint("B", "User declined final IAGREE confirmation to change Root Name - no changes applied...")
                self.statusLabel.setText(
                    ("User declined final IAGREE confirmation to change Root Name - no changes applied").ljust(800,
                                                                                                               " "))
                self.statusLabel.setForeground(Color.RED)
                return

            myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
            return

    class DeleteOFXServiceButtonAction(AbstractAction):
        theString = ""

        def __init__(self, theString, statusLabel):
            self.theString = theString
            self.statusLabel = statusLabel

        def actionPerformed(self, event):
            global Toolbox_frame_, debug

            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

            serviceList = moneydance.getCurrentAccountBook().getOnlineInfo().getAllServices()

            service = JOptionPane.showInputDialog(Toolbox_frame_,
                                                  "Select a service to delete",
                                                  "Select a Service to Delete",
                                                  JOptionPane.INFORMATION_MESSAGE,
                                                  moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                  serviceList.toArray(),
                                                  None)

            if not service:
                self.statusLabel.setText(("No Service was selected - no changes made..").ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            if not myPopupAskQuestion(Toolbox_frame_,
                                  "DELETE BANKING SERVICE",
                                  "Are you sure you want to delete banking service: " + str(service),
                                  JOptionPane.YES_NO_OPTION,
                                  JOptionPane.ERROR_MESSAGE):
                self.statusLabel.setText(("User did not say yes to delete bank service - no changes made").ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            if not myPopupAskBackup(Toolbox_frame_, "Would you like to perform a backup before DELETE BANKING SERVICE?"):
                self.statusLabel.setText(("'DELETE BANKING SERVICE' - User chose to exit without the fix/update....").ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            disclaimer = myPopupAskForInput(Toolbox_frame_,
                                            "DELETE BANKING SERVICE",
                                            "DISCLAIMER:",
                                            "Are you really sure you want to DELETE THIS BANKING SERVICE? Type 'IAGREE' to continue..",
                                            "NO",
                                            False,
                                            JOptionPane.ERROR_MESSAGE)

            if not disclaimer == 'IAGREE':
                self.statusLabel.setText("DELETE BANKING SERVICE - User declined the disclaimer - no changes made....".ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            # noinspection PyUnresolvedReferences
            service.deleteItem()
            # service.syncItem()
            play_the_money_sound()
            self.statusLabel.setText(("Banking service successfully deleted: " + str(service).ljust(800, " ")))
            self.statusLabel.setForeground(Color.RED)
            myPrint("B", "User selected to delete banking service: " + str(service))

            myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
            return

    class DisplayPasswordsButtonAction(AbstractAction):
        iSet = False
        saveForeground = None

        def __init__(self, statusLabel):
            self.statusLabel = statusLabel

        def actionPerformed(self, event):
            global Toolbox_frame_, debug
            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

            myPrint("DB","Displaying Passphrases button selected....!")
            if not self.iSet:
                self.iSet = True
                self.saveForeground = self.statusLabel.getForeground()
                passwords = buildDiagText(lGrabPasswords=True)
                self.statusLabel.setText(("MD STORED PASSPHRASES: " + passwords).ljust(800, " "))
                self.statusLabel.setForeground(Color.BLUE)
                myPrint("J", "User requested to display stored Passphrases in Toolbox status area")

            else:
                self.iSet = False
                passwords = "DIAG STATUS:"
                self.statusLabel.setText((passwords).ljust(800, " "))
                self.statusLabel.setForeground(Color.BLACK)

            myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
            return

    class DoTheMenu(AbstractAction):

        def __init__(self, statusLabel, displayPanel, menu, callingClass=None):
            self.statusLabel = statusLabel
            self.displayPanel = displayPanel
            self.menu = menu
            self.callingClass = callingClass

        def actionPerformed(self, event):
            global Toolbox_frame_, debug, DARK_GREEN, lCopyAllToClipBoard_TB, lGeekOutModeEnabled_TB, lHackerMode
            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

            if event.getActionCommand() == "Help":
                viewHelp = self.callingClass.ViewFileButtonAction(self.statusLabel, "display_help()", "HELP DOCUMENTATION", lFile=False)
                viewHelp.actionPerformed(None)

            if event.getActionCommand() == "About":
                about_this_script()

            if event.getActionCommand() == "Geek Out Mode":
                lGeekOutModeEnabled_TB = not lGeekOutModeEnabled_TB
                components = self.displayPanel.getComponents()
                for theComponent in components:
                    if isinstance(theComponent, JButton):
                        # noinspection PyUnresolvedReferences
                        buttonText = theComponent.getLabel().strip().upper()

                        if ("GEEK" in buttonText):
                            theComponent.setVisible(not theComponent.isVisible())

            if event.getActionCommand() == "Debug":
                if debug:
                    self.statusLabel.setText("Script Debug mode disabled".ljust(800, " "))
                    self.statusLabel.setForeground(DARK_GREEN)
                else:
                    self.statusLabel.setText("Script Debug mode enabled".ljust(800, " "))
                    self.statusLabel.setForeground(DARK_GREEN)
                    myPrint("B", "User has enabled script debug mode.......\n")
                debug = not debug

            if event.getActionCommand() == "Copy all Output to Clipboard":
                if lCopyAllToClipBoard_TB:
                    self.statusLabel.setText("Diagnostic outputs will not be copied to Clipboard".ljust(800, " "))
                    self.statusLabel.setForeground(DARK_GREEN)
                else:
                    self.statusLabel.setText("Diagnostic outputs will now all be copied to the Clipboard".ljust(800, " "))
                    self.statusLabel.setForeground(DARK_GREEN)
                    myPrint("B", "User has requested to copy all diagnostic output to clipboard.......\n")

                lCopyAllToClipBoard_TB = not lCopyAllToClipBoard_TB

            if event.getActionCommand() == "Hacker Mode":

                if not lHackerMode:
                    if not myPopupAskQuestion(Toolbox_frame_,
                                          "HACKER MODE",
                                          "HACKER MODE >> DISCLAIMER: DO YOU ACCEPT THAT YOU USE THIS TOOLBOX AT YOUR OWN RISK?",
                                              JOptionPane.YES_NO_OPTION,
                                              JOptionPane.ERROR_MESSAGE):
                        self.statusLabel.setText("HACKER MODE DISABLED AS USER DECLINED DISCLAIMER".ljust(800, " "))
                        self.statusLabel.setForeground(Color.RED)
                        myPrint("B", "User DECLINED the Disclaimer. Hacker Mode disabled........\n")
                        return
                    else:
                        myPrint("B", "User accepted Disclaimer and agreed to use Toolbox Hacker mode at own risk.....")

                        backup = BackupButtonAction(self.statusLabel, "Would you like to create a backup before starting Hacker mode?")
                        backup.actionPerformed(None)

                        if not backup_local_storage_settings():
                            self.statusLabel.setText(("HACKER MODE DISABLED: SORRY - ERROR WHEN SAVING LocalStorage() ./safe/settings to backup file!!??").ljust(800," "))
                            self.statusLabel.setForeground(Color.RED)
                            return

                        if not backup_config_dict():
                            self.statusLabel.setText(("HACKER MODE DISABLED: SORRY - ERROR WHEN SAVING config.dict to backup file!!??").ljust(800," "))
                            self.statusLabel.setForeground(Color.RED)
                            return

                        myPrint("B","@@ HACKER MODE ENABLED. config.dict and safe/settings have been backed up...! @@")

                        self.statusLabel.setText(("HACKER MODE SELECTED - ONLY USE THIS IF YOU KNOW WHAT YOU ARE DOING - THIS CAN CHANGE DATA!").ljust(800," "))
                        self.statusLabel.setForeground(Color.RED)
                else:
                    myPrint("B","HACKER MODE DISABLED <PHEW!>")
                    self.statusLabel.setText(("HACKER MODE DiSABLED <PHEW!>").ljust(800," "))
                    self.statusLabel.setForeground(Color.BLUE)

                lHackerMode = not lHackerMode

                components = self.displayPanel.getComponents()
                for theComponent in components:
                    if isinstance(theComponent, JButton):
                        # noinspection PyUnresolvedReferences
                        buttonText = theComponent.getLabel().strip().upper()

                        if ("HACK:" in buttonText):
                            theComponent.setVisible(lHackerMode)


            if event.getActionCommand() == "Advanced Mode":
                if myPopupAskQuestion(Toolbox_frame_,
                                      "ADVANCED MODE",
                                      "ADVANCED MODE >> DISCLAIMER: DO YOU ACCEPT THAT YOU USE THIS TOOLBOX AT YOUR OWN RISK?",
                                      JOptionPane.YES_NO_OPTION,
                                      JOptionPane.ERROR_MESSAGE):

                    myPrint("B", "User accepted Disclaimer and agreed to use Toolbox Advanced mode at own risk.....")

                    backup = BackupButtonAction(self.statusLabel, "Would you like to create a backup before starting Advanced mode?")
                    backup.actionPerformed(None)

                    self.statusLabel.setText(("ADVANCED MODE SELECTED - RED BUTTONS CAN CHANGE YOUR DATA - %s+I for Help"%moneydance_ui.ACCELERATOR_MASK_STR).ljust(800," "))
                    self.statusLabel.setForeground(Color.RED)

                    for i in range(0, self.menu.getItemCount()):
                        x = self.menu.getItem(i)
                        if x.getText() == "Advanced Mode":
                            x.setEnabled(False)
                        else:
                            x.setEnabled(True)

                    components = self.displayPanel.getComponents()
                    for theComponent in components:
                        if isinstance(theComponent, JButton):
                            # noinspection PyUnresolvedReferences
                            buttonText = theComponent.getLabel().strip().upper()

                            if ("FIX" in buttonText
                                  or "FONTS" in buttonText
                                  or "RESET" in buttonText
                                  or "DELETE" in buttonText
                                  or "FORGET" in buttonText):
                                theComponent.setVisible(True)
                else:
                    self.statusLabel.setText("ADVANCED MODE DISABLED AS USER DECLINED DISCLAIMER - BASIC MODE ONLY".ljust(800, " "))
                    self.statusLabel.setForeground(Color.RED)
                    myPrint("B", "User DECLINED the Disclaimer. Advanced Mode disabled........\n")

            if event.getActionCommand() == "Basic Mode":
                self.statusLabel.setText("BASIC MODE SELECTED".ljust(800, " "))
                self.statusLabel.setForeground(DARK_GREEN)

                for i in range(0, self.menu.getItemCount()):
                    x = self.menu.getItem(i)
                    if x.getText() == "Basic Mode":
                        x.setEnabled(False)
                    else:
                        x.setEnabled(True)

                components = self.displayPanel.getComponents()
                for theComponent in components:
                    if isinstance(theComponent, JButton):
                        # noinspection PyUnresolvedReferences
                        buttonText = theComponent.getLabel().strip().upper()
                        if "DIAG" in buttonText:
                            pass
                        elif ("FIX" in buttonText
                              or "FONTS" in buttonText
                              or "RESET" in buttonText
                              or "DELETE" in buttonText
                              or "FORGET" in buttonText):
                            theComponent.setVisible(False)

            myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
            return

    def openDisplay(self):
        global Toolbox_frame_, DARK_GREEN, lPickle_version_warning, lCopyAllToClipBoard_TB, myParameters, lIgnoreOutdatedExtensions_TB

        screenSize = Toolkit.getDefaultToolkit().getScreenSize()

        button_width = 230
        button_height = 40
        frame_width = screenSize.width - 20
        frame_height = screenSize.height - 20
        # panel_width = frame_width - 50
        # button_panel_height = button_height + 5

        JFrame.setDefaultLookAndFeelDecorated(True)
        Toolbox_frame_ = JFrame("StuWareSoftSystems: " + myScriptName + " (" + version_build + ")...  (%s+I for Help)    -    DATASET: %s" % (moneydance_ui.ACCELERATOR_MASK_STR, moneydance.getCurrentAccountBook().getName().strip()))
        # Toolbox_frame_.setLayout(FlowLayout())

        # icon = moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png")
        # icon = Toolkit.getDefaultToolkit().getImage("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png")
        # print type(icon)
        # Toolbox_frame_.setIconImage(icon)

        if (not Platform.isMac()):
            moneydance_ui.getImages()
            Toolbox_frame_.setIconImage(MDImages.getImage(moneydance_ui.getMain().getSourceInformation().getIconResource()))

        # Toolbox_frame_.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE)  # The CloseAction() and WindowListener() will handle dispose() - else change back to DISPOSE_ON_CLOSE
        Toolbox_frame_.setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE)  # The CloseAction() and WindowListener() will handle dispose() - else change back to DISPOSE_ON_CLOSE

        displayString = buildDiagText()
        statusLabel = JLabel(("DIAG STATUS: BASIC MODE RUNNING... - %s+I for Help (check out the Toolbox menu for more options/modes/features)"%moneydance_ui.ACCELERATOR_MASK_STR).ljust(800, " "), JLabel.LEFT)
        statusLabel.setForeground(DARK_GREEN)

        try:
            # If we are here then lCopyAllToClipBoard_TB was loaded from parameter file....
            if lCopyAllToClipBoard_TB:
                Toolkit.getDefaultToolkit().getSystemClipboard().setContents(StringSelection(displayString), None)
        except:
            myPrint("J","Error copying diagnostic's main screen contents to Clipboard")
            dump_sys_error_to_md_console_and_errorlog()

        shortcut = Toolkit.getDefaultToolkit().getMenuShortcutKeyMaskEx()

        # Add standard CMD-W keystrokes etc to close window
        Toolbox_frame_.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_W, shortcut), "close-window")
        Toolbox_frame_.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_F4, shortcut), "close-window")
        Toolbox_frame_.getRootPane().getActionMap().put("close-window", self.CloseAction(Toolbox_frame_))
        Toolbox_frame_.addWindowListener(self.WindowListener())

        Toolbox_frame_.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_P, shortcut), "display-pickle")
        Toolbox_frame_.getRootPane().getActionMap().put("display-pickle", self.ViewFileButtonAction(statusLabel, "display_pickle()", "StuWareSoftSystems Pickle Parameter File", lFile=False))

        Toolbox_frame_.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_I, shortcut), "display-help")
        Toolbox_frame_.getRootPane().getActionMap().put("display-help", self.ViewFileButtonAction(statusLabel, "display_help()", "HELP DOCUMENTATION", lFile=False))

        Toolbox_frame_.setPreferredSize(Dimension(frame_width, frame_height))
        # Toolbox_frame_.setPreferredSize(Dimension(1400,900))
        Toolbox_frame_.setExtendedState(JFrame.MAXIMIZED_BOTH)
        # Toolbox_frame_.getContentPane().setLayout(BorderLayout())
        displayPanel = JPanel()
        displayPanel.setLayout(FlowLayout(FlowLayout.LEFT))
        # displayPanel.setLayout(BorderLayout())
        displayPanel.setPreferredSize(Dimension(frame_width - 20, 300))

        backup_button = JButton("<html><center><B>EXPORT BACKUP</B></center></html>")
        backup_button.setToolTipText("This will allow you to take a backup of your Moneydance Dataset")
        backup_button.setBackground(DARK_GREEN)
        backup_button.setForeground(Color.WHITE)
        backup_button.addActionListener(BackupButtonAction(statusLabel, "Confirm you want to create a backup (same as MD Menu>File>Export Backup)?"))
        displayPanel.add(backup_button)

        if (not moneydance_data.getLocalStorage().getBoolean("_is_master_node", True)):
            convertSecondary_button = JButton("<html><center><B>FIX: Make me a<BR>Primary dataset</B></center></html>")
            convertSecondary_button.setToolTipText("This will allow you to make this Dataset a Primary / Master Dataset (typically used if you restored from a synchronised secondary dataset/backup). THIS CHANGES DATA!")
            convertSecondary_button.setBackground(Color.ORANGE)
            convertSecondary_button.setForeground(Color.WHITE)
            convertSecondary_button.addActionListener(self.ConvertSecondaryButtonAction(displayString, statusLabel))
            convertSecondary_button.setVisible(False)
            displayPanel.add(convertSecondary_button)

        if moneydance.getBuild() >= 3030:
            changeTheFont_button = JButton("<html><center>Set/Change Default<BR>Moneydance FONTS</center></html>")
            changeTheFont_button.setToolTipText("This will allow you to Set/Change the Default Moneydance Fonts. THIS CHANGES DATA!")
            changeTheFont_button.setForeground(Color.RED)
            changeTheFont_button.addActionListener(self.ChangeFontsButtonAction(statusLabel))
            changeTheFont_button.setVisible(False)
            displayPanel.add(changeTheFont_button)

        copy_button = JButton("<html><center>Copy Diagnostics<BR>below to Clipboard</center></html>")
        copy_button.setToolTipText("This will copy the contents in the diagnostic report below to your Clipboard")
        copy_button.addActionListener(self.ClipboardButtonAction(displayString, statusLabel))
        displayPanel.add(copy_button)

        displayPasswords_button = JButton("Display MD Passphrases")
        displayPasswords_button.setToolTipText("Display the passphrase used to open your Encrypted Dataset, and also your Sync passphrase (if set)")
        displayPasswords_button.addActionListener(self.DisplayPasswordsButtonAction(statusLabel))
        displayPanel.add(displayPasswords_button)

        viewConfigFile_button = JButton("View MD Config File")
        viewConfigFile_button.setToolTipText("View the contents of your Moneydance configuration file")
        viewConfigFile_button.addActionListener(self.ViewFileButtonAction(statusLabel, Common.getPreferencesFile(), "MD Config"))
        displayPanel.add(viewConfigFile_button)

        # noinspection PyUnresolvedReferences
        if os.path.exists(theme.Theme.customThemeFile.getAbsolutePath()):
            viewThemesFile_button = JButton("<html><center>View MD Custom<BR>Theme File</center></html>")
            viewThemesFile_button.setToolTipText("View the contents of your Moneydance custom Theme file (if you have set one up)")
            # noinspection PyUnresolvedReferences
            viewThemesFile_button.addActionListener(self.ViewFileButtonAction(statusLabel, theme.Theme.customThemeFile, "MD Custom Theme"))
            displayPanel.add(viewThemesFile_button)

            deleteThemeFile_button = JButton("<html><center>Delete Custom<BR>Theme file</center></html>")
            deleteThemeFile_button.setToolTipText("Delete your custom Theme file (if it exists). This is pretty safe. MD will create a new one if you select in Preferences. THIS DELETES A FILE!")
            deleteThemeFile_button.setForeground(Color.RED)
            deleteThemeFile_button.addActionListener(self.DeleteThemeFileButtonAction(statusLabel))
            deleteThemeFile_button.setVisible(False)
            displayPanel.add(deleteThemeFile_button)

        viewConsoleLogFile_button = JButton("View Console Log File")
        viewConsoleLogFile_button.setToolTipText("View the contents of your Moneydance Console (error) log file")
        viewConsoleLogFile_button.addActionListener(self.ViewFileButtonAction(statusLabel, moneydance.getLogFile(), "MD Console Log"))
        displayPanel.add(viewConsoleLogFile_button)

        copyConsoleLogFile_button = JButton("Copy Console Log File")
        copyConsoleLogFile_button.setToolTipText("Copy the Console Error log file to a directory of your choosing..")
        copyConsoleLogFile_button.addActionListener(self.CopyConsoleLogFileButtonAction(statusLabel, moneydance.getLogFile()))
        displayPanel.add(copyConsoleLogFile_button)

        grabProgramDir = find_the_program_install_dir()
        # noinspection PyTypeChecker
        if grabProgramDir and os.path.exists(os.path.join(grabProgramDir,"Moneydance.vmoptions")):
            viewJavaVMFileFile_button = JButton("<html><center>View Java VM<BR>Options File</center></html>")
            viewJavaVMFileFile_button.setToolTipText("View the contents of the Java VM Options runtime file that Moneydance uses")
            viewJavaVMFileFile_button.addActionListener(self.ViewFileButtonAction(statusLabel, File(grabProgramDir, "Moneydance.vmoptions"), "Java VM File"))
            displayPanel.add(viewJavaVMFileFile_button)

        openFolder_button = JButton("Open MD Folder")
        openFolder_button.setToolTipText("Open the selected Moneydance (internal) folder in Explorer/Finder window (etc)")
        openFolder_button.addActionListener(self.OpenFolderButtonAction(displayString, statusLabel))
        displayPanel.add(openFolder_button)

        findDataset_button = JButton("<html><center>Find My Dataset(s)<BR>and Backups</center></html>")
        findDataset_button.setToolTipText("This will search your hard disk for copies of your Moneydance Dataset(s) - incl Backups.... NOTE: Can be CPU & time intensive..!")
        findDataset_button.addActionListener(self.FindDatasetButtonAction(statusLabel))
        displayPanel.add(findDataset_button)

        viewMemorized_button = JButton("<html><center>View Memorised<BR>Reports</center></html>")
        viewMemorized_button.setToolTipText("View a list of your Memorised reports")
        viewMemorized_button.addActionListener(self.ViewFileButtonAction(statusLabel, "get_list_memorised_reports()", "Memorized Reports and Graphs", lFile=False))
        displayPanel.add(viewMemorized_button)

        viewTxnSort_button = JButton("<html><center>View Register<BR>TXNs Sort Orders</center></html>")
        viewTxnSort_button.setToolTipText("Allows you  to view the current transaction register sort orders in operation")
        viewTxnSort_button.addActionListener(self.ViewFileButtonAction(statusLabel, "get_register_txn_sort_orders()", "Register TXN Sort Orders etc", lFile=False))
        displayPanel.add(viewTxnSort_button)

        viewCheckNumSettings_button = JButton("<html><center>View Check Num<BR>Settings</center></html>")
        viewCheckNumSettings_button.setToolTipText("View the Check Number settings that will display in the Transaction Register")
        viewCheckNumSettings_button.addActionListener(self.ViewFileButtonAction(statusLabel, "view_check_num_settings()", "Check Number Settings etc", lFile=False))
        displayPanel.add(viewCheckNumSettings_button)

        viewExtnDetails_button = JButton("<html><center>View Extension(s)<BR>details</center></html>")
        viewExtnDetails_button.setToolTipText("View details about the Extensions installed in your Moneydance system")
        viewExtnDetails_button.addActionListener(self.ViewFileButtonAction(statusLabel, "view_extensions_details()", "Extension(s) details etc", lFile=False))
        displayPanel.add(viewExtnDetails_button)

        canIDeleteSecurity_button = JButton("<html><center>DIAG: Can I Delete<BR>Security?</center></html>")
        canIDeleteSecurity_button.setToolTipText("This will tell you whether a Selected Security is in use and whether you can delete it in Moneydance")
        canIDeleteSecurity_button.addActionListener(self.ViewFileButtonAction(statusLabel, "can_I_delete_security()", "CAN I DELETE A SECURITY?", lFile=False))
        displayPanel.add(canIDeleteSecurity_button)

        listSecurityCurrencyDecimalPlaces_button = JButton("<html><center>DIAG: List Sec/Curr<BR>dpc</center></html>")
        listSecurityCurrencyDecimalPlaces_button.setToolTipText("This will list your Security and Currency hidden decimal place settings (and attempt to advise of setup errors)")
        listSecurityCurrencyDecimalPlaces_button.addActionListener(self.ViewFileButtonAction(statusLabel, "list_security_currency_decimal_places()", "LIST SECURITY CURRENCY DECIMAL PLACES", lFile=False))
        displayPanel.add(listSecurityCurrencyDecimalPlaces_button)

        diagnoseCurrencies_button = JButton("<html><center>DIAG: Diagnose<BR>Currencies</center></html>")
        diagnoseCurrencies_button.setToolTipText("This will diagnose your Currency setup - checking relative currencies (and attempt to advise if you need to run a fix)")
        diagnoseCurrencies_button.addActionListener(self.ViewFileButtonAction(statusLabel, "diagnose_currencies(False)", "DIAGNOSE CURRENCIES (LOOK FOR ERRORS)", lFile=False))
        displayPanel.add(diagnoseCurrencies_button)

        fixCurrencies_button = JButton("<html><center>FIX: Fix Relative<BR>Currencies</center></html>")
        fixCurrencies_button.setToolTipText("This will apply fixes to your Currency / Relative Currency setup (use after running the diagnose currencies button first). THIS CHANGES DATA!")
        fixCurrencies_button.setForeground(Color.RED)
        fixCurrencies_button.addActionListener(self.ViewFileButtonAction(statusLabel, "diagnose_currencies(True)", "FIX RELATIVE CURRENCIES (FIX ERRORS)", lFile=False))
        fixCurrencies_button.setVisible(False)
        displayPanel.add(fixCurrencies_button)

        viewZeroBalCats_button = JButton("<html><center>DIAG: Categories<BR>and Balances Report</center></html>")
        viewZeroBalCats_button.setToolTipText("This will list all your Categories and show which have Zero Balances - USE ADVANCED MODE TO MAKE THESE INACTIVE")
        viewZeroBalCats_button.addActionListener(self.ZeroBalCategoriesButtonAction(statusLabel, False))
        displayPanel.add(viewZeroBalCats_button)

        inactivateZeroBalCats_button = JButton("<html><center>FIX: Make 0 Balance<BR>Categories Inactive</center></html>")
        inactivateZeroBalCats_button.setToolTipText("This will allow you Inactivate all Categories with Zero Balances (you will see the report first). THIS CHANGES DATA!")
        inactivateZeroBalCats_button.setForeground(Color.RED)
        inactivateZeroBalCats_button.addActionListener(self.ZeroBalCategoriesButtonAction(statusLabel, True))
        inactivateZeroBalCats_button.setVisible(False)
        displayPanel.add(inactivateZeroBalCats_button)

        viewOFX_button = JButton("<html><center>View OFX Bank<BR>Related Data</center></html>")
        viewOFX_button.setToolTipText("This will allow you to view any Online Banking related setup information linked to each Account")
        viewOFX_button.addActionListener(self.ViewFileButtonAction(statusLabel, "get_ofx_related_data()", "Display OFX Bank Related Data", lFile=False))
        displayPanel.add(viewOFX_button)

        forgetOFX_button = JButton("<html><center>Forget OFX Bank<BR>Import Link</center></html>")
        forgetOFX_button.setToolTipText("This will tell Moneydance to forget the OFX Banking Import link attributed to an Account. This means Moneydance will then ask you to recreate the link on the next import.. THIS CHANGES DATA!")
        forgetOFX_button.setForeground(Color.RED)
        forgetOFX_button.addActionListener(self.ForgetOFXButtonAction(displayString, statusLabel))
        forgetOFX_button.setVisible(False)
        displayPanel.add(forgetOFX_button)

        deleteOFX_service_button = JButton("<html><center>Delete OFX Bank<BR>Logon Profile/Svc</center></html>")
        deleteOFX_service_button.setToolTipText("This will allow you to delete an Online Banking logon / service profile (service) from Moneydance. E.g. you will have to set this up again. THIS CHANGES DATA!")
        deleteOFX_service_button.setForeground(Color.RED)
        deleteOFX_service_button.addActionListener(self.DeleteOFXServiceButtonAction(displayString, statusLabel))
        deleteOFX_service_button.setVisible(False)
        displayPanel.add(deleteOFX_service_button)

        bookName = moneydance.getCurrentAccountBook().getName().strip()
        root = moneydance.getCurrentAccountBook().getRootAccount()
        rootName = root.getAccountName().strip()
        if rootName != bookName:
            fixRootAccountName_button = JButton("<html><center>FIX: Correct<BR>Root Acct Name</center></html>")
            fixRootAccountName_button.setToolTipText("This allows you to change the (nearly) hidden Master/Parent Account Name in Moneydance (referred to as ROOT) to match the name of your Dataset (referred to as BOOK). THIS CHANGES DATA!")
            fixRootAccountName_button.setForeground(Color.RED)
            fixRootAccountName_button.addActionListener(self.FixRootAccountNameButtonAction(displayString, statusLabel))
            fixRootAccountName_button.setVisible(False)
            displayPanel.add(fixRootAccountName_button)

        fixDeleteOneSidedTxns_button = JButton("<html><center>FIX: Delete One-Sided<BR>Transactions</center></html>")
        fixDeleteOneSidedTxns_button.setToolTipText("This allows you to DELETE 'invalid' one-sided transactions - usually from a bad quicken import. THIS CHANGES DATA!")
        fixDeleteOneSidedTxns_button.setForeground(Color.RED)
        fixDeleteOneSidedTxns_button.addActionListener(self.FixDeleteOneSidedTxnsButtonAction(displayString, statusLabel))
        fixDeleteOneSidedTxns_button.setVisible(False)
        displayPanel.add(fixDeleteOneSidedTxns_button)

        if _AREYOUSURE:
            deleteConfigFile_button = JButton("<html><center>DELETE MD<BR>Config File</center></html>")
            deleteConfigFile_button.setToolTipText("This allows you to delete the Moneydance preferences file config.dict. Pretty pointless as Moneydance will recreate it upon exit. THIS DELETES A FILE!")
            deleteConfigFile_button.setForeground(Color.RED)
            deleteConfigFile_button.addActionListener(self.DeleteConfigFileButtonAction(statusLabel))
            deleteConfigFile_button.setVisible(False)
            displayPanel.add(deleteConfigFile_button)

        deleteOrphanedExtensions_button = JButton("<html><center>FIX: Delete Orphaned<BR>Extensions</center></html>")
        deleteOrphanedExtensions_button.setToolTipText("This will delete any references to orphaned / outdated Extensions (config.dict & .mxt files). THIS CHANGES DATA!")
        deleteOrphanedExtensions_button.setForeground(Color.RED)
        deleteOrphanedExtensions_button.addActionListener(self.ForceRemoveExtension(statusLabel))
        deleteOrphanedExtensions_button.setVisible(False)
        displayPanel.add(deleteOrphanedExtensions_button)

        resetWindowPositions_button = JButton("<html><center>RESET Window<BR>Display Settings</center></html>")
        resetWindowPositions_button.setToolTipText("This tells MD to 'forget' window display settings.CLOSE ALL REGISTER WINDOWS FIRST! The beauty is it keeps all other settings intact! THIS CHANGES DATA!")
        resetWindowPositions_button.setForeground(Color.RED)
        resetWindowPositions_button.addActionListener(self.ResetWindowPositionsButtonAction(statusLabel))
        resetWindowPositions_button.setVisible(False)
        displayPanel.add(resetWindowPositions_button)


        lTabbingModeNeedsChanging = False
        if Platform.isOSX() and Platform.isOSXVersionAtLeast("10.16") \
                and not DetectAndChangeMacTabbingMode(statusLabel, True).actionPerformed("quick check"):
            lTabbingModeNeedsChanging = True
            fixTabbingMode_button = JButton("<html><center><B>FIX: MacOS<BR>Tabbing Mode</B></center></html>")
            fixTabbingMode_button.setToolTipText("This allows you to check/fix your MacOS Tabbing Setting")
            fixTabbingMode_button.setBackground(Color.RED)
            fixTabbingMode_button.setForeground(Color.WHITE)
            fixTabbingMode_button.addActionListener(DetectAndChangeMacTabbingMode(statusLabel, False))
            fixTabbingMode_button.setVisible(False)
            displayPanel.add(fixTabbingMode_button)

        GeekOutMode_button = JButton("<html><B>Geek Out</B></html>")
        GeekOutMode_button.setToolTipText("This allows you to display very Technical Information on the Moneydance System and many key objects..... READONLY")
        GeekOutMode_button.setBackground(Color.MAGENTA)
        GeekOutMode_button.setForeground(Color.WHITE)
        GeekOutMode_button.addActionListener(self.GeekOutModeButtonAction(statusLabel))
        GeekOutMode_button.setVisible(lGeekOutModeEnabled_TB)
        displayPanel.add(GeekOutMode_button)

        HackerMode_button = JButton("<html><center><B>HACK: ADD/CHG/DEL<BR>System Keys/Values</B></center></html>")
        HackerMode_button.setToolTipText("This allows you to HACK (add/change/delete) config.dict and LocalStorage() (./safe/settings) keys..... CAN UPDATE DATA")
        HackerMode_button.setBackground(Color.RED)
        HackerMode_button.setForeground(Color.WHITE)
        HackerMode_button.addActionListener(self.HackerModeButtonAction(statusLabel))
        HackerMode_button.setVisible(False)
        displayPanel.add(HackerMode_button)

        components = displayPanel.getComponents()
        for theComponent in components:
            if isinstance(theComponent, JButton):
                theComponent.setPreferredSize(Dimension(button_width, button_height))
                theComponent.setBorderPainted(False)
                theComponent.setOpaque(True)
                if not (theComponent.getBackground() == Color.MAGENTA
                    or theComponent.getBackground() == Color.RED
                        or theComponent.getBackground() == Color.ORANGE
                            or theComponent.getBackground() == DARK_GREEN):
                    theComponent.setBackground(Color.LIGHT_GRAY)

        myDiagText = JTextArea(displayString)
        myDiagText.setEditable(False)
        myDiagText.setLineWrap(True)
        myDiagText.setWrapStyleWord(True)
        myDiagText.setFont( getMonoFont() )

        displayPanel.add(statusLabel)

        myScrollPane = JScrollPane(myDiagText, JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED,JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED)
        myScrollPane.setPreferredSize(Dimension(frame_width - 20, frame_height - 300))
        myScrollPane.setWheelScrollingEnabled(True)
        displayPanel.add(myScrollPane)

        keyToUse = shortcut

        if Platform.isWindows():
            keyToUse = InputEvent.ALT_MASK

        if Platform.isOSX():
            save_useScreenMenuBar= System.getProperty("apple.laf.useScreenMenuBar")
            System.setProperty("apple.laf.useScreenMenuBar", "false")

        mb = JMenuBar()
        menu1 = JMenu("<html><b>TOOLBOX Options</b></html>")
        menu1.setMnemonic(KeyEvent.VK_T)

        menuItem0 = JMenuItem("Basic Mode")
        menuItem0.setMnemonic(KeyEvent.VK_B)
        menuItem0.setAccelerator(KeyStroke.getKeyStroke(KeyEvent.VK_B, keyToUse))
        menuItem0.setToolTipText("Switch to basic (no harm) mode")
        menuItem0.addActionListener(self.DoTheMenu(statusLabel, displayPanel, menu1))
        menuItem0.setEnabled(False)
        menu1.add(menuItem0)

        menuItem1 = JMenuItem("Advanced Mode")
        menuItem1.setMnemonic(KeyEvent.VK_M)  # Can't think of a spare letter to use!!!!
        menuItem1.setAccelerator(KeyStroke.getKeyStroke(KeyEvent.VK_M, keyToUse))
        menuItem1.addActionListener(self.DoTheMenu(statusLabel, displayPanel, menu1))
        menuItem1.setToolTipText("Switch to Advanced / Fix Mode (can update data)")
        menu1.add(menuItem1)

        menuItemC = JCheckBoxMenuItem("Copy all Output to Clipboard")
        menuItemC.setMnemonic(KeyEvent.VK_O)  # Can't think of a spare letter to use!!!!
        menuItemC.setAccelerator(KeyStroke.getKeyStroke(KeyEvent.VK_O, keyToUse))
        menuItemC.addActionListener(self.DoTheMenu(statusLabel, displayPanel, menu1))
        menuItemC.setToolTipText("When selected copies the output of all displays to Clipboard")
        menuItemC.setSelected(lCopyAllToClipBoard_TB)
        menu1.add(menuItemC)

        menuItemG = JCheckBoxMenuItem("Geek Out Mode")
        menuItemG.setMnemonic(KeyEvent.VK_G)  # Can't think of a spare letter to use!!!!
        menuItemG.setAccelerator(KeyStroke.getKeyStroke(KeyEvent.VK_G, keyToUse))
        menuItemG.addActionListener(self.DoTheMenu(statusLabel, displayPanel, menu1))
        menuItemG.setToolTipText("Enables the Geek Out Button to show very technical stuff - readonly")
        menuItemG.setSelected(lGeekOutModeEnabled_TB)
        menu1.add(menuItemG)

        menuItemH = JCheckBoxMenuItem("Hacker Mode")
        menuItemH.addActionListener(self.DoTheMenu(statusLabel, displayPanel, menu1))
        menuItemH.setToolTipText("Enables 'Hacker' Mode - Do not do this unless you know what you are doing... Allows you to update data!")
        menuItemH.setSelected(False)
        menu1.add(menuItemH)

        menuItemD = JCheckBoxMenuItem("Debug")
        menuItemD.addActionListener(self.DoTheMenu(statusLabel, displayPanel, menu1))
        menuItemD.setToolTipText("Enables script to output debug information - technical stuff - readonly")
        menuItemD.setSelected(debug)
        menu1.add(menuItemD)

        menuItem2 = JMenuItem("Exit")
        menuItem2.setMnemonic(KeyEvent.VK_E)
        menuItem2.setAccelerator(KeyStroke.getKeyStroke(KeyEvent.VK_E, keyToUse))
        menuItem2.addActionListener(self.CloseAction(Toolbox_frame_))
        menuItem2.setToolTipText("Exit this Toolbox")
        menu1.add(menuItem2)

        mb.add(menu1)

        menuH = JMenu("<html>HELP</html>")
        menuH.setMnemonic(KeyEvent.VK_I)

        menuItemH = JMenuItem("Help")
        menuItemH.setMnemonic(KeyEvent.VK_I)
        menuItemH.setAccelerator(KeyStroke.getKeyStroke(KeyEvent.VK_I, keyToUse))
        menuItemH.setToolTipText("Display Help")
        menuItemH.addActionListener(self.DoTheMenu(statusLabel, displayPanel, menuH, self))
        menuItemH.setEnabled(True)
        menuH.add(menuItemH)
        mb.add(menuH)

        menuItemA = JMenuItem("About")
        menuItemA.setToolTipText("About...")
        menuItemA.addActionListener(self.DoTheMenu(statusLabel, displayPanel, menuH, self))
        menuItemA.setEnabled(True)
        menuH.add(menuItemA)
        mb.add(menuH)

        Toolbox_frame_.setJMenuBar(mb)

        Toolbox_frame_.add(displayPanel)
        Toolbox_frame_.pack()
        Toolbox_frame_.setLocationRelativeTo(None)
        Toolbox_frame_.setVisible(True)

        if Platform.isOSX():
            System.setProperty("apple.laf.useScreenMenuBar", save_useScreenMenuBar)                                 # noqa

        if not moneydance_data.getLocalStorage().getBoolean("_is_master_node", True):

            myPopupInformationBox(Toolbox_frame_,
                                  "This Dataset is running as a Secondary Node\n" +
                                  "- either you are Synchronising to it,\n" +
                                  "- or you have restored it from a backup/sync copy.\n" +
                                  "To convert to Primary, use Advanced Tools...\n" +
                                  "........\n",
                                  "SECONDARY DATASET/NODE",
                                  JOptionPane.WARNING_MESSAGE)


        if lTabbingModeNeedsChanging:
            myPopupInformationBox(Toolbox_frame_,
                                  "Your Mac has 'Tabbing Mode' set to 'always'\n" +
                                  "- You can find this in Settings>General>Prefer tabs:,\n" +
                                  "- THIS CAUSES STRANGE MONEYDANCE FREEZES.\n" +
                                  ">> To change this setting now, use Advanced Mode...\n" +
                                  "........\n",
                                  "MacOS TABBING MODE WARNING",
                                  JOptionPane.ERROR_MESSAGE)

        check_for_old_StuWareSoftSystems_scripts(statusLabel)

        check_for_updatable_extensions_on_startup(statusLabel)



if not i_am_an_extension_so_run_headless: print("""
Script is analysing your moneydance & system settings....
------------------------------------------------------------------------------
>> DISCLAIMER: This script has the ability to change your data
>> Always perform backup first before making any changes!
>> The Author of this script can take no responsibility for any harm caused
>> If you do not accept this, please exit the script
------------------------------------------------------------------------------
""")

if moneydance.getVersion() < 2020:
    myPrint("B", "Sorry, this Toolbox has only been tested on Moneydance version 2020 upwards... Existing.....")
    myPopupInformationBox(None,
                          "Sorry, this Toolbox has only been tested on Moneydance version 2020 upwards... Exiting.....",
                          "VERSION TOO OLD",
                          JOptionPane.ERROR_MESSAGE)
else:
    fixRCurrencyCheck = 0

    theDisplay = DiagnosticDisplay()
    theDisplay.openDisplay()

    myPrint("P","------------------------------------------------------------------------------------")
    myPrint("B", "StuWareSoftSystems - ", myScriptName, " script ending (frame is open/running)......")
    myPrint("P","------------------------------------------------------------------------------------")

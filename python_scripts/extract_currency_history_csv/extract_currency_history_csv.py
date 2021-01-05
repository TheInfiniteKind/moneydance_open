#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# extract_currency_history_csv build 1008 - November 2020 - Stuart Beesley StuWareSoftSystems
# Extracts your Currency rate history to CSV file (as MD doesn't do this)
# This script does not change any data!
# Thanks to DerekKent23 for his testing....
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
# V0.1 beta - Initial release
# V0.2 beta - Parameter enhancements, simplify option (for DerekKent23)
# V0.3 beta - Added UTF8 BOM to help Excel double-click open files. Changed open() to 'W' instead of 'wb'
# V0.4 beta - Changed to no rounding on price history... Added suffix to simple format
# V0.5 beta - Cosmetic display change; catch pickle.load() error (from restored file); extract format changes..
# V0.6 beta - Reverted to open() with 'wb'
# V1 - Initial release
# V1a - Changed pickle file to be unencrypted
# V1b - Slight change to myParameters; changed __file__ usage; code cleanup; version change

# Build: 1000 - IntelliJ code cleanup; made Extension ready; refresh bits with common code - script file renamed - no functional changes
# Build: 1000 - no functional changes; Added code fix for extension runtime to set moneydance variables (if not set)
# Build: 1000 - all print functions changed to work headless; added some popup warnings...; streamlined common code
# Build: 1000 - optional parameter whether to write BOM to export file; added date/time to console log
# Build: 1001 - Enhanced MyPrint to catch unicode utf-8 encode/decode errors
# Build: 1002 - fixed raise(Exception) clauses ;->
# Build: 1003 - Updated common codeset; leverage moneydance fonts
# Build: 1004 - Removed TxnSortOrder from common code
# Build: 1004 - Fix for Jython 2.7.1 where csv.writer expects a 1-byte string delimiter, not unicode....
# Build: 1004 - Write parameters out to csv file; added the fake JFrame() for icons...; moved parameter  save earlier
# Build: 1004 - Moved the currency table scan to only run if extract file selected...
# Build: 1004 - Fix for Jython 2.7.1 non handling of Unicode on csv.writerow on currency symbols
# Build: 1005 - Renames for module, REPO, url, Moneydance etc
# Build: 1006 - Tweak to common code (popups) and imports
# Build: 1007 - Updated parameter screens to use JCheckBox and JComboBox
# Build: 1008 - Added dataset path/name to extract

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
from javax.swing import JTextField, JPasswordField, Box, UIManager, JTable, JCheckBox
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
if isinstance(None, (JDateField,CurrencyUtil,Reminder,ParentTxn,SplitTxn,TxnSearch, JComboBox, JCheckBox,
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
version_build = "1008"                                                                                              # noqa
myScriptName = "extract_currency_history_csv.py(Extension)"                                                         # noqa
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
global __extract_currency_history_csv
global lStripASCII, csvDelimiter,csvfilename, scriptpath, lDisplayOnly, userdateformat
global lSimplify_ECH, userdateStart_ECH, userdateEnd_ECH, hideHiddenCurrencies_ECH
global lWriteBOMToExportFile_SWSS

# Other used by program
global baseCurrency, sdf, csvlines, extract_currency_history_csv_fake_frame_
# >>> END THIS SCRIPT'S GLOBALS ############################################################################################

# Set programmatic defaults/parameters for filters HERE.... Saved Parameters will override these now
# NOTE: You  can override in the pop-up screen
userdateformat = "%Y/%m/%d"                                                                                         # noqa
lStripASCII = False                                                                                                 # noqa
csvDelimiter = ","                                                                                                  # noqa
lSimplify_ECH = False                                                                                               # noqa
userdateStart_ECH = 19600101                                                                                        # noqa
userdateEnd_ECH = 20201231                                                                                          # noqa
hideHiddenCurrencies_ECH = True                                                                                     # noqa

scriptpath = ""                                                                                                     # noqa
lWriteBOMToExportFile_SWSS = True                                                                                   # noqa
extract_currency_history_csv_fake_frame_ = None                                                                     # noqa
extract_filename="extract_currency_history.csv"
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

        myScrollPane = JScrollPane(displayJText, JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED,JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED)
        if displayJText.getLineCount()>5:
            # myScrollPane.setMinimumSize(Dimension(self.theWidth-20, 10))
            # myScrollPane.setMaximumSize(Dimension(self.theWidth-20, maxHeight-100))
            myScrollPane.setWheelScrollingEnabled(True)
            _popupPanel.add(myScrollPane)
        else:
            _popupPanel.add(displayJText)

        buttonPanel = JPanel()
        if self.lModal or self.lCancelButton:
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

        if self.lAlertLevel>=2:
            # internalScrollPane.setBackground(Color.RED)
            # theJText.setBackground(Color.RED)
            # theJText.setForeground(Color.BLACK)
            displayJText.setBackground(Color.RED)
            displayJText.setForeground(Color.BLACK)
            _popupPanel.setBackground(Color.RED)
            _popupPanel.setForeground(Color.BLACK)
            buttonPanel.setBackground(Color.RED)
            myScrollPane.setBackground(Color.RED)

        elif self.lAlertLevel>=1:
            # internalScrollPane.setBackground(Color.YELLOW)
            # theJText.setBackground(Color.YELLOW)
            # theJText.setForeground(Color.BLACK)
            displayJText.setBackground(Color.YELLOW)
            displayJText.setForeground(Color.BLACK)
            _popupPanel.setBackground(Color.YELLOW)
            _popupPanel.setForeground(Color.BLACK)
            buttonPanel.setBackground(Color.YELLOW)
            myScrollPane.setBackground(Color.RED)

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
    global __extract_currency_history_csv
    global lStripASCII, csvDelimiter, scriptpath, userdateformat
    global lSimplify_ECH, userdateStart_ECH, userdateEnd_ECH, hideHiddenCurrencies_ECH
    global lWriteBOMToExportFile_SWSS                                                                                  # noqa

    myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )
    myPrint("DB", "Loading variables into memory...")

    if myParameters is None: myParameters = {}

    if myParameters.get("__extract_currency_history_csv") is not None: __extract_currency_history_csv = myParameters.get("__extract_currency_history_csv")
    if myParameters.get("userdateformat") is not None: userdateformat = myParameters.get("userdateformat")
    if myParameters.get("lStripASCII") is not None: lStripASCII = myParameters.get("lStripASCII")
    if myParameters.get("csvDelimiter") is not None: csvDelimiter = myParameters.get("csvDelimiter")

    if myParameters.get("lSimplify_ECH") is not None: lSimplify_ECH = myParameters.get("lSimplify_ECH")
    if myParameters.get("userdateStart_ECH") is not None: userdateStart_ECH = myParameters.get("userdateStart_ECH")
    if myParameters.get("userdateEnd_ECH") is not None: userdateEnd_ECH = myParameters.get("userdateEnd_ECH")
    if myParameters.get("hideHiddenCurrencies_ECH") is not None: hideHiddenCurrencies_ECH = myParameters.get("hideHiddenCurrencies_ECH")
    if myParameters.get("lWriteBOMToExportFile_SWSS") is not None: lWriteBOMToExportFile_SWSS = myParameters.get("lWriteBOMToExportFile_SWSS")                                                                                  # noqa

    if myParameters.get("scriptpath") is not None:
        scriptpath = myParameters.get("scriptpath")
        if not os.path.isdir(scriptpath):
            myPrint("DB", "Warning: loaded parameter scriptpath does not appear to be a valid directory:", scriptpath, "will ignore")
            scriptpath = ""

    myPrint("DB","myParameters{} set into memory (as variables).....")

    return

# >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
def dump_StuWareSoftSystems_parameters_from_memory():
    global debug, myParameters, lPickle_version_warning, version_build

    # >>> THESE ARE THIS SCRIPT's PARAMETERS TO SAVE
    global __extract_currency_history_csv
    global lStripASCII, csvDelimiter, scriptpath
    global lDisplayOnly, userdateformat
    global lSimplify_ECH, userdateStart_ECH, userdateEnd_ECH, hideHiddenCurrencies_ECH
    global lWriteBOMToExportFile_SWSS                                                                                  # noqa

    myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )

    # NOTE: Parameters were loaded earlier on... Preserve existing, and update any used ones...
    # (i.e. other StuWareSoftSystems programs might be sharing the same file)

    if myParameters is None: myParameters = {}

    myParameters["__extract_currency_history_csv"] = version_build
    myParameters["userdateformat"] = userdateformat
    myParameters["lStripASCII"] = lStripASCII
    myParameters["csvDelimiter"] = csvDelimiter
    myParameters["lSimplify_ECH"] = lSimplify_ECH
    myParameters["userdateStart_ECH"] = userdateStart_ECH
    myParameters["userdateEnd_ECH"] = userdateEnd_ECH
    myParameters["hideHiddenCurrencies_ECH"] = hideHiddenCurrencies_ECH
    myParameters["lWriteBOMToExportFile_SWSS"] = lWriteBOMToExportFile_SWSS

    if not lDisplayOnly and scriptpath != "" and os.path.isdir(scriptpath):
        myParameters["scriptpath"] = scriptpath

    myPrint("DB","variables dumped from memory back into myParameters{}.....")

    return


get_StuWareSoftSystems_parameters_from_file()
myPrint("DB", "DEBUG IS ON..")
# END ALL CODE COPY HERE ###############################################################################################

# Create fake JFrame() so that all popups have correct Moneydance Icons etc
extract_currency_history_csv_fake_frame_ = JFrame()
if (not Platform.isMac()):
    moneydance_ui.getImages()
    extract_currency_history_csv_fake_frame_.setIconImage(MDImages.getImage(moneydance_ui.getMain().getSourceInformation().getIconResource()))
extract_currency_history_csv_fake_frame_.setUndecorated(True)
extract_currency_history_csv_fake_frame_.setVisible(False)
extract_currency_history_csv_fake_frame_.setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE)

csvfilename = None

if decimalCharSep != "." and csvDelimiter == ",": csvDelimiter = ";"  # Override for EU countries or where decimal point is actually a comma...
myPrint("DB", "Decimal point:", decimalCharSep, "Grouping Separator", groupingCharSep, "CSV Delimiter set to:", csvDelimiter)

sdf = SimpleDateFormat("dd/MM/yyyy")

dateStrings=["dd/mm/yyyy", "mm/dd/yyyy", "yyyy/mm/dd", "yyyymmdd"]
# 1=dd/mm/yyyy, 2=mm/dd/yyyy, 3=yyyy/mm/dd, 4=yyyymmdd
label1 = JLabel("Select Output Date Format (default yyyy/mm/dd):")
user_dateformat = JComboBox(dateStrings)

if userdateformat == "%d/%m/%Y": user_dateformat.setSelectedItem("dd/mm/yyyy")
elif userdateformat == "%m/%d/%Y": user_dateformat.setSelectedItem("mm/dd/yyyy")
elif userdateformat == "%Y%m%d": user_dateformat.setSelectedItem("yyyymmdd")
else: user_dateformat.setSelectedItem("yyyy/mm/dd")

labelDateStart = JLabel("Date range start (enter as yyyy/mm/dd):")
user_selectDateStart = JDateField(CustomDateFormat("ymd"),15)   # Use MD API function (not std Python)
user_selectDateStart.setDateInt(userdateStart_ECH)

labelDateEnd = JLabel("Date range end (enter as yyyy/mm/dd):")
user_selectDateEnd = JDateField(CustomDateFormat("ymd"),15)   # Use MD API function (not std Python)
user_selectDateEnd.setDateInt(userdateEnd_ECH)
# user_selectDateEnd.gotoToday()

labelSimplify = JLabel("Simplify extract?")
user_selectSimplify = JCheckBox("", lSimplify_ECH)

labelHideHiddenCurrencies = JLabel("Hide Hidden Currencies?")
user_selectHideHiddenCurrencies = JCheckBox("", hideHiddenCurrencies_ECH)

label2 = JLabel("Strip non ASCII characters from CSV export?")
user_selectStripASCII = JCheckBox("", lStripASCII)

delimStrings = [";","|",","]
label3 = JLabel("Change CSV Export Delimiter from default to: ';|,'")
user_selectDELIMITER = JComboBox(delimStrings)
user_selectDELIMITER.setSelectedItem(csvDelimiter)

labelBOM = JLabel("Write BOM (Byte Order Mark) to file (helps Excel open files)?")
user_selectBOM = JCheckBox("", lWriteBOMToExportFile_SWSS)

label4 = JLabel("Turn DEBUG Verbose messages on?")
user_selectDEBUG = JCheckBox("", debug)

userFilters = JPanel(GridLayout(0, 2))
userFilters.add(label1)
userFilters.add(user_dateformat)

userFilters.add(labelDateStart)
userFilters.add(user_selectDateStart)

userFilters.add(labelDateEnd)
userFilters.add(user_selectDateEnd)

userFilters.add(labelSimplify)
userFilters.add(user_selectSimplify)

userFilters.add(labelHideHiddenCurrencies)
userFilters.add(user_selectHideHiddenCurrencies)

userFilters.add(label2)
userFilters.add(user_selectStripASCII)
userFilters.add(label3)
userFilters.add(user_selectDELIMITER)
userFilters.add(labelBOM)
userFilters.add(user_selectBOM)
userFilters.add(label4)
userFilters.add(user_selectDEBUG)

lExit = False
lDisplayOnly = False

options = ["Abort", "CSV Export"]

while True:

    userAction = (JOptionPane.showOptionDialog(extract_currency_history_csv_fake_frame_, userFilters, "%s(build: %s) Set Script Parameters...."%(myScriptName,version_build),
                                         JOptionPane.OK_CANCEL_OPTION,
                                         JOptionPane.QUESTION_MESSAGE,
                                         moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                         options, options[1]))
    if userAction != 1:
        myPrint("B", "User Cancelled Parameter selection.. Will abort..")
        myPopupInformationBox(extract_currency_history_csv_fake_frame_, "User Cancelled Parameter selection.. Will abort..", "PARAMETERS")
        lDisplayOnly = False
        lExit = True
        break

    if user_selectDateStart.getDateInt() <= user_selectDateEnd.getDateInt() \
            and user_selectDateEnd.getDateInt() >= user_selectDateStart.getDateInt():
        break   # Valid date range

    myPrint("P","Error - date range incorrect, please try again...")
    user_selectDateStart.setForeground(Color.RED)
    user_selectDateEnd.setForeground(Color.RED)
    continue   # Loop


if not lExit:
    myPrint("DB", "Parameters Captured",
        "User Date Format:", user_dateformat.getSelectedItem(),
        "Simplify:", user_selectSimplify.isSelected(),
        "Hide Hidden Currencies:", user_selectHideHiddenCurrencies.isSelected(),
        "Start date:", user_selectDateStart.getDateInt(),
        "End date:", user_selectDateEnd.getDateInt(),
        "Strip ASCII:", user_selectStripASCII.isSelected(),
        "Write BOM to file:", user_selectBOM.isSelected(),
        "Verbose Debug Messages: ", user_selectDEBUG.isSelected(),
        "CSV File Delimiter:", user_selectDELIMITER.getSelectedItem())
    # endif

    if user_dateformat.getSelectedItem() == "dd/mm/yyyy": userdateformat = "%d/%m/%Y"
    elif user_dateformat.getSelectedItem() == "mm/dd/yyyy": userdateformat = "%m/%d/%Y"
    elif user_dateformat.getSelectedItem() == "yyyy/mm/dd": userdateformat = "%Y/%m/%d"
    elif user_dateformat.getSelectedItem() == "yyyymmdd": userdateformat = "%Y%m%d"
    else:
        # PROBLEM /  default
        userdateformat = "%Y/%m/%d"

    lSimplify_ECH = user_selectSimplify.isSelected()
    hideHiddenCurrencies_ECH = user_selectHideHiddenCurrencies.isSelected()
    userdateStart_ECH = user_selectDateStart.getDateInt()
    userdateEnd_ECH = user_selectDateEnd.getDateInt()

    lStripASCII = user_selectStripASCII.isSelected()

    csvDelimiter = user_selectDELIMITER.getSelectedItem()
    if csvDelimiter == "" or (not (csvDelimiter in ";|,")):
        myPrint("B", "Invalid Delimiter:", csvDelimiter, "selected. Overriding with:','")
        csvDelimiter = ","
    if decimalCharSep == csvDelimiter:
        myPrint("B", "WARNING: The CSV file delimiter:", csvDelimiter, "cannot be the same as your decimal point character:", decimalCharSep, " - Proceeding without file export!!")
        lDisplayOnly = True

    lWriteBOMToExportFile_SWSS = user_selectBOM.isSelected()

    debug = user_selectDEBUG.isSelected()
    myPrint("DB", "DEBUG turned ON")

    myPrint("B","User Parameters...")

    if lSimplify_ECH:
        myPrint("B","Simplifying extract")
    else:
        myPrint("B","Providing a detailed extract")

    myPrint("B","user date format....:", userdateformat)

    myPrint("B", "Selected start date:", userdateStart_ECH)
    myPrint("B", "Selected end date:", userdateEnd_ECH)

    if hideHiddenCurrencies_ECH:
        myPrint("B", "Hiding hidden currencies...")

    # Now get the export filename
    csvfilename = None

    if not lDisplayOnly:  # i.e. we have asked for a file export - so get the filename

        if lStripASCII:
            myPrint("B","Will strip non-ASCII characters - e.g. Currency symbols from output file...", " Using Delimiter:", csvDelimiter)
        else:
            myPrint("B","Non-ASCII characters will not be stripped from file: ", " Using Delimiter:", csvDelimiter)

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

                System.setProperty("com.apple.macos.use-file-dialog-packages", "true")  # In theory prevents access to app file structure (but doesnt seem to work)
                System.setProperty("apple.awt.fileDialogForDirectories", "false")

            filename = FileDialog(extract_currency_history_csv_fake_frame_, "Select/Create CSV file for extract (CANCEL=NO EXPORT)")
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
                myPopupInformationBox(extract_currency_history_csv_fake_frame_,"User chose to cancel or no file selected >>  So no Extract will be performed... ","FILE SELECTION")
            elif str(csvfilename).endswith(".moneydance"):
                myPrint("B", "User selected file:", csvfilename)
                myPrint("B", "Sorry - User chose to use .moneydance extension - I will not allow it!... So no Extract will be performed...")
                myPopupInformationBox(extract_currency_history_csv_fake_frame_,"Sorry - User chose to use .moneydance extension - I will not allow it!... So no Extract will be performed...","FILE SELECTION")
                lDisplayOnly = True
                csvfilename = None
            elif ".moneydance" in filename.getDirectory():
                myPrint("B", "User selected file:", filename.getDirectory(), csvfilename)
                myPrint("B", "Sorry - FileDialog() User chose to save file in .moneydance location. NOT Good practice so I will not allow it!... So no Extract will be performed...")
                myPopupInformationBox(extract_currency_history_csv_fake_frame_,"Sorry - FileDialog() User chose to save file in .moneydance location. NOT Good practice so I will not allow it!... So no Extract will be performed...","FILE SELECTION")
                lDisplayOnly = True
                csvfilename = None
            else:
                csvfilename = os.path.join(filename.getDirectory(), filename.getFile())
                scriptpath = str(filename.getDirectory())

            if not lDisplayOnly:
                if os.path.exists(csvfilename) and os.path.isfile(csvfilename):
                    myPrint("D", "WARNING: file exists,but assuming user said OK to overwrite..")

            if not lDisplayOnly:
                if check_file_writable(csvfilename):
                    if lStripASCII:
                        myPrint("B", 'Will extract to file: ', csvfilename, "(NOTE: Should drop non utf8 characters...)")
                    else:
                        myPrint("B", 'Will extract to file: ', csvfilename, "...")
                    scriptpath = os.path.dirname(csvfilename)
                else:
                    myPrint("B", "Sorry - I just checked and you do not have permissions to create this file:", csvfilename)
                    myPopupInformationBox(extract_currency_history_csv_fake_frame_,"Sorry - I just checked and you do not have permissions to create this file: %s" %csvfilename,"FILE SELECTION")
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
        myPrint("B", "No Export will be performed")

    if not lDisplayOnly:
        save_StuWareSoftSystems_parameters_to_file()

        myPrint("P", "\nScript running to extract your currency rate history....")
        myPrint("P", "-------------------------------------------------------------------")
        if moneydance_data is None:
            myPrint("B", "MD Data file is empty - no data to scan - aborting...")
            myPopupInformationBox(extract_currency_history_csv_fake_frame_,"MD Data file is empty - no data to scan - aborting...","EMPTY DATASET")
            extract_currency_history_csv_fake_frame_.dispose()
            raise(Exception("MD Data file is empty - no data to scan - aborting..."))

        header = ["CurrencyName",
                  "CurrencyID",
                  "isBase",
                  "DecimalPlaces",
                  "Prefix",
                  "Suffix",
                  "CurrentRateR2B",
                  "CurrentRateB2R",
                  "Snap_Date",
                  "Snap_DailyRateR2B",
                  "Snap_DailyRateB2R"]

        def list_currency_rate_history():
            global hideHiddenCurrencies_ECH, lSimplify_ECH, userdateStart_ECH, userdateEnd_ECH

            curr_table=[]

            currencies = moneydance.getCurrentAccountBook().getCurrencies()
            baseCurr = currencies.getBaseType()

            myPrint("P","\nIterating the currency table...")
            for curr in currencies:

                # noinspection PyUnresolvedReferences
                if curr.getCurrencyType() != CurrencyType.Type.CURRENCY: continue   # Skip if not on a Currency record (i.e. a Security)

                if hideHiddenCurrencies_ECH and curr.getHideInUI(): continue   # Skip if hidden in MD

                myPrint("P","Currency: %s %s" %(curr, curr.getPrefix()) )

                currSnapshots = curr.getSnapshots()

                if not lSimplify_ECH and not len(currSnapshots) and curr == baseCurr:

                    row = []

                    row.append((curr.getName()))
                    row.append((curr.getIDString()))
                    row.append(curr == baseCurr)
                    row.append(curr.getDecimalPlaces())
                    row.append((curr.getPrefix()))
                    row.append((curr.getSuffix()))
                    row.append(1)
                    row.append(1)
                    row.append(None)
                    row.append(None)
                    row.append(None)
                    curr_table.append(row)

                # noinspection PyUnusedLocal
                dpc = curr.getDecimalPlaces()
                dpc = 8   # Override to 8dpc

                for currSnapshot in currSnapshots:
                    if currSnapshot.getDateInt() < userdateStart_ECH \
                            or currSnapshot.getDateInt() > userdateEnd_ECH:
                        continue   # Skip if out of date range

                    row = []

                    row.append((curr.getName()))
                    row.append((curr.getIDString()))
                    row.append(curr == baseCurr)
                    row.append(curr.getDecimalPlaces())
                    row.append((curr.getPrefix()))
                    row.append((curr.getSuffix()))
                    row.append(round(float(curr.getParameter("rate", None)),dpc))
                    row.append(round(1/float(curr.getParameter("rate", None)),dpc))

                    # I don't print relative currency as it's supposed to always be None or = Base..

                    row.append(currSnapshot.getDateInt())
                    row.append(round(float(currSnapshot.getRate()),dpc))
                    row.append(round(1/float(currSnapshot.getRate()),dpc))

                    curr_table.append(row)

            return curr_table

        currencyTable = list_currency_rate_history()

        def ExportDataToFile(theTable, header):                                                                 # noqa
            global debug, csvfilename, decimalCharSep, groupingCharSep, csvDelimiter, version_build, myScriptName
            global sdf, userdateformat, lGlobalErrorDetected
            global lWriteBOMToExportFile_SWSS

            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

            _CURRNAME = 0
            _CURRID = 1
            _SYMB =4
            _SNAPDATE = 8


            # NOTE - You can add sep=; to beginning of file to tell Excel what delimiter you are using
            if True:
                theTable = sorted(theTable, key=lambda x: (str(x[_CURRNAME]).upper(),x[_SNAPDATE]))

            myPrint("P", "Now pre-processing the file to convert integer dates to 'formatted' dates....")
            for row in theTable:
                try:
                    if row[_SNAPDATE]:
                        dateasdate = datetime.datetime.strptime(str(row[_SNAPDATE]),"%Y%m%d")  # Convert to Date field
                        dateoutput = dateasdate.strftime(userdateformat)
                        row[_SNAPDATE] = dateoutput

                except:
                    myPrint("B","Error on row below with curr:", row[_CURRNAME], "snap date:", row[_SNAPDATE])
                    myPrint("B",row)
                    continue

                if lStripASCII:
                    for col in range(0, len(row)):
                        row[col] = fixFormatsStr(row[col])

            theTable.insert(0,header)  # Insert Column Headings at top of list. A bit rough and ready, not great coding, but a short list...!

            # Write the theTable to a file
            myPrint("B", "Opening file and writing ", len(theTable), " records")

            try:
                # CSV Writer will take care of special characters / delimiters within fields by wrapping in quotes that Excel will decode
                # with open(csvfilename,"wb") as csvfile:  # PY2.7 has no newline parameter so opening in binary; just use "w" and newline='' in PY3.0
                with open(csvfilename,"wb") as csvfile:  # PY2.7 has no newline parameter so opening in binary; just use "w" and newline='' in PY3.0

                    if lWriteBOMToExportFile_SWSS:
                        csvfile.write(codecs.BOM_UTF8)   # This 'helps' Excel open file with double-click as UTF-8

                    writer = csv.writer(csvfile, dialect='excel', quoting=csv.QUOTE_MINIMAL, delimiter=fix_delimiter(csvDelimiter))

                    if csvDelimiter != ",":
                        writer.writerow(["sep=",""])  # Tells Excel to open file with the alternative delimiter (it will add the delimiter to this line)

                    if not lSimplify_ECH:
                        for i in range(0, len(theTable)):
                            try:
                                writer.writerow( theTable[i] )
                            except:
                                myPrint("B","Error writing row %s to file... Older Jython version?" %i)
                                myPrint("B","Row: ",theTable[i])
                                myPrint("B","Will attempt coding back to str()..... Let's see if this fails?!")
                                for _col in range(0, len(theTable[i])):
                                    theTable[i][_col] = fix_delimiter(theTable[i][_col])
                                writer.writerow( theTable[i] )
                        # NEXT
                        today = Calendar.getInstance()
                        writer.writerow([""])
                        writer.writerow(["StuWareSoftSystems - " + myScriptName + "(build: "
                                         + version_build
                                         + ")  Moneydance Python Script - Date of Extract: "
                                         + str(sdf.format(today.getTime()))])

                        writer.writerow([""])
                        writer.writerow(["Dataset path/name: %s" %(moneydance_data.getRootFolder()) ])

                        writer.writerow([""])
                        writer.writerow(["User Parameters..."])
                        writer.writerow(["Simplify Extract...........: %s" %(lSimplify_ECH)])
                        writer.writerow(["Hiding Hidden Currencies...: %s" %(hideHiddenCurrencies_ECH)])
                        writer.writerow(["Date format................: %s" %(userdateformat)])
                        writer.writerow(["Date Range Selected........: "+str(userdateStart_ECH) + " to " +str(userdateEnd_ECH)])

                    else:
                        # Simplify is for my tester 'buddy' DerekKent23 - it's actually an MS Money Import format
                        lCurr = None
                        for row in theTable[1:]:
                            # Write the table, but swap in the raw numbers (rather than formatted number strings)
                            if row[_CURRNAME] != lCurr:
                                if lCurr: writer.writerow("")
                                lCurr = row[_CURRNAME]
                                writer.writerow( [fix_delimiter(row[ _CURRNAME])
                                                  +" - "+fix_delimiter(row[_CURRID])
                                                  +" - "+fix_delimiter(row[_SYMB])
                                                  +fix_delimiter(row[_SYMB+1])] )
                                writer.writerow(["Date","Base to Rate","Rate to Base"])

                            writer.writerow([row[_SNAPDATE],
                                            row[_SNAPDATE+1],
                                            row[_SNAPDATE+2]])
                        # NEXT
                myPrint("B", "CSV file " + csvfilename + " created, records written, and file closed..")

            except IOError, e:
                lGlobalErrorDetected = True
                myPrint("B", "Oh no - File IO Error!", e)
                myPrint("B", "Path:", csvfilename)
                myPrint("B", "!!! ERROR - No file written - sorry! (was file open, permissions etc?)".upper())
                dump_sys_error_to_md_console_and_errorlog()
                myPopupInformationBox(extract_currency_history_csv_fake_frame_,"Sorry - error writing to export file!", "FILE EXTRACT")
        # enddef

        def fixFormatsStr(theString, lNumber=False, sFormat=""):
            global lStripASCII

            if isinstance(theString, bool): return theString

            if isinstance(theString, int) or isinstance(theString, float):
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

            if lStripASCII:
                all_ASCII = ''.join(char for char in theString if ord(char) < 128)  # Eliminate non ASCII printable Chars too....
            else:
                all_ASCII = theString
            return all_ASCII

        ExportDataToFile(currencyTable, header)
        if not lGlobalErrorDetected:
            myPopupInformationBox(extract_currency_history_csv_fake_frame_,"Your extract has been created as requested",myScriptName)
            try:
                helper = moneydance.getPlatformHelper()
                helper.openDirectory(File(csvfilename))
            except:
                pass


if extract_currency_history_csv_fake_frame_ is not None:
    extract_currency_history_csv_fake_frame_.dispose()
    del extract_currency_history_csv_fake_frame_

myPrint("P", "-----------------------------------------------------------------")
myPrint("B", "StuWareSoftSystems - ", myScriptName, " script ending......")

if not i_am_an_extension_so_run_headless: print(scriptExit)

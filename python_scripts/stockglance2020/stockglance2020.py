#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# StockGlance2020 build:1006 - October 2020 - Stuart Beesley

#   Original code StockGlance.java MoneyDance Extension Copyright James Larus - https://github.com/jameslarus/stockglance
#
#   Copyright (c) 2020, Stuart Beesley StuWareSoftSystems
#   All rights reserved.
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions are
#   met:
#   1. Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#   2. Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#   3. Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#   "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#   LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#   A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#   HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES LOSS OF USE,
#   DATA, OR PROFITS OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#   THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#   (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#   OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#  Modified by waynelloydsmith to run as standalone Python/Jython script StockGlance75.py and to show in which accounts the stocks are held.
#  https://github.com/waynelloydsmith/Moneydance-Scripts/blob/master/StockGlance75.py

#  Extensively modified/enhanced by Stuart Beesley - StuWareSoftSystems - September 2020 to create StockGlance2020.py with these features:
#  - This script basically shows all stocks/funds summarised into single stocks/funds per row. I.E. consolidates data across all Accounts
#  - Some of the code looks somewhat different to how I would write native Python, but it is as it is as it was converted from pure Java by waynelloydsmith
#  - Shows QTY of shares
#  - If you are running Windows and get file IO errors (e.g. 13) creating the extract, you likely have a permissions issue. Try a different location (e.g. your standard user directory)
#  - Removed all non-functional Java / Python code and general tidy up.
#  - Also fixed / replaced the JY/Java code to make JTable and the Scroll panes function properly
#  - Addressed bug hiding some securities when not all prices found (by date) - by eliminating % as not needed anyway.
#  - Price is taken from Current Price now, and NOT from price history. If you would like price history, let me know!
#  - Added Parameter/filter screen/options and export to file....
#  - The file will write a utf8 encoded file - so we strip out currency signs - else Excel treats them wrongly. You can specify to leave them included...
# -- We strip out all non ASCII characters below code 128 and also number separators. Delimiter will flip to a semi-colon if your decimal point is a comma!
# -- USAGE: Just execute and a popup will ask you to set parameters. You can just leave all as default if you wish.
# --        Change the defaults in the rows just below this statement...
# -- WARNING: Cash Balances are per account, not per security/currency.
# --          So the cash balances will always be for the whole account(s) included, not just  filtered securities etc...
# -- Added extra columns with raw number that don't get displayed. Planned to use for custom sort,
# --       but found a workaround stripping non numerics out of text... (so not used)
# -- Found that JFileChooser with file extension filters hangs on Macs, so use FileDialog on Mac to also get Mac(ish) GUI LaF
# -- Version 3 - fixed bug so that .moneydance extension test only checks end of filename (not middle)
# -- Version 3c fiddled with the Accounts filter; added extra total (securities + cash balance) where whole account selected
# -- Version 3d eliminated rounding on the totals in base currency (user request)
# --            don't display base currency in local currency where same; make all filters uppercase
# -- V3d Fix small bug on check for whether all securities were same currency (didn't really affect much);
# --     also tried to deal better with LOCALE decimal point and comma....
# -- V4 - Enhanced to use CSV File writer and write raw numbers into the CSV file - let CSV writer handle the special character handling.......;
# --      altered pricing rounding
# -- V4b - tweaked to use Jython syntax (rather than Java)...syntax; Added "copyright to file extract";
# --       added version number - all cosmetic only; replaced AcctFilter()
# -- V4b - enhanced filters to include Currency Name, and Security Name in searches....
# -- V4b - added option to split / securities within account (rather than total across the accounts)... Messy display, but requested
# -- V4c - now saving parameters to file (within MD) so that they persist.
# -- V4d - added script encoding utf-8 (removed again in v4e)
# -- V4e - Added MD Cost Basis and the Unrealised Gain (calculated); also now save export path to disk
# -- V4e - Added trap for file write errors; added parameter to allow user to exclude totals from csv file; cleaned up row highlighting and cell neg colours
# -- V4f - Added file permissions check; added code to display file to stdout if file error. Allows user to copy / paste into Excel...
# -- V4g - Added % to gain calculation (user request); changed default extract location (search for User Home) to avoid internal MD locations
# -- V4g - re-added UTF8 coding; tinkered with display formatting (bold rows); enabled scrolling on footer table (totals) (user request); allow footer to gain focus and CTRL-C (copy)
# -- V4h - format CSV Gain% field as a %string; fixed Gain% on the final total row...
# -- V5 -  Released version (from v4h)
# -- V5a - Some users report a problem saving files to some folders on Windows 10. It seems that Anti-malware or Windows Access Control is restrictiing access
# --       So, changed to FileDialog (from JFileChooser) for Windows as this seems to tell Windows to allow access.
# --       Added some console messages; fixed crash when no investment accounts exist.
# -- V5b - Removed the now redundant lUseMacFileChooser variable; enhanced some console messages...
# -- V5c - Code cleanup only - cosmetic only; Added parameter to allow User to select no rounding of price (useful if their settings on the security are set wrongly); switched to use MD's decimal setting
# -- v5d - Small tweak to parameter field (cosmetic only); Added a File BOM marker to help Excel open UTF-8 files (and changed open() to 'w' instead of 'wb')
# -- v5e - Cosmetic change to display; catch pickle.load() error (when restored dataset); Reverting to open() 'wb' - fix Excel CR/LF double line on Windows issue
# Build: 1000 - Slight change to myParameters; changed __file__ usage; code cleanup for IntelliJ; version_build change; changed versioning; changed export filename; Eliminated wait for script close..
# Build: 1000 - no functional changes; Added code fix for extension runtime to set moneydance variables (if not set);
# Build: 1000 - all print functions changed to work headless; added some popup warnings...; stream-lined common code.....
# Build: 1000 - Column widths now save....; optional parameter whether to write BOM to export file; added date/time to console log
# Build: 1001 - Cosmetic change to console to state when not splitting accounts; Added About menu (cosmetic)
# Build: 1002 - Cosmetic change to put main window in centre of screen; bug fix for text double-decimal point corrupting display in MyGainsRenderer()
# Build: 1002 - Enhanced MyPrint to catch unicode utf-8 encode/decode errors
# Build: 1003 - fixed raise(Exception) clauses ;->
# Build: 1004 - Updated common codeset; utilise Moneydance fonts
# Build: 1005 - User request to add option to extract future balance, rather than current balance; added fake JFrame() for icons
# Build: 1005 - Moved parameter save earlier...; added parameters to writer csv output
# Build: 1006 - Removed TxnSortOrder from common code
# Build: 1006 - Fix for Jython 2.7.1 where csv.writer expects a 1-byte string delimiter, not unicode....

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
myScriptName = "StockGlance2020.py(Extension)"                                                                      # noqa
debug = False                                                                                                       # noqa
myParameters = {}                                                                                                   # noqa
_resetParameters = False                                                                                            # noqa
lPickle_version_warning = False                                                                                     # noqa
lIamAMac = False                                                                                                    # noqa
lGlobalErrorDetected = False																						# noqa
# END SET THESE VARIABLES FOR ALL SCRIPTS ##############################################################################

# >>> THIS SCRIPT'S IMPORTS ############################################################################################
from java.awt.event import AdjustmentListener
from java.text import NumberFormat, SimpleDateFormat
from java.util import Comparator
from javax.swing import SortOrder

from javax.swing.border import CompoundBorder, MatteBorder
from javax.swing.table import DefaultTableCellRenderer, DefaultTableModel, TableRowSorter
from javax.swing.event import TableColumnModelListener
# >>> END THIS SCRIPT'S IMPORTS ########################################################################################

# >>> THIS SCRIPT'S GLOBALS ############################################################################################

# Saved to parameters file
global __StockGlance2020
global hideHiddenSecurities, hideInactiveAccounts, hideHiddenAccounts, lAllCurrency, filterForCurrency, lAllSecurity
global filterForSecurity, lAllAccounts, filterForAccounts, lIncludeCashBalances, lStripASCII, csvDelimiter, _column_widths_SG2020
global lSplitSecuritiesByAccount, lExcludeTotalsFromCSV, lRoundPrice, scriptpath
global lWriteBOMToExportFile_SWSS, lIncludeFutureBalances_SG2020

# Other used by program
global csvfilename, lDisplayOnly
global baseCurrency, sdf, StockGlance2020_frame_, rawDataTable, rawFooterTable, headingNames
global StockGlanceInstance  # holds the instance of StockGlance2020()
global _SHRS_FORMATTED, _SHRS_RAW, _PRICE_FORMATTED, _PRICE_RAW, _CVALUE_FORMATTED, _CVALUE_RAW, _BVALUE_FORMATTED, _BVALUE_RAW
global _CBVALUE_FORMATTED, _CBVALUE_RAW, _GAIN_FORMATTED, _GAIN_RAW, _SORT, _EXCLUDECSV, _GAINPCT
global acctSeparator, StockGlance2020_fake_frame_
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
lIncludeCashBalances = False                                                                                        # noqa
lSplitSecuritiesByAccount = False                                                                                   # noqa
lExcludeTotalsFromCSV = False                                                                                       # noqa
lIncludeFutureBalances_SG2020 = False                                                                               # noqa
lRoundPrice = True                                                                                                  # noqa
lStripASCII = False                                                                                                 # noqa
csvDelimiter = ","                                                                                                  # noqa
_column_widths_SG2020 = []                                                                                          # noqa

headingNames = ""                                                                                                   # noqa
acctSeparator = ' : '                                                                                               # noqa
scriptpath = ""                                                                                                     # noqa
lWriteBOMToExportFile_SWSS = True                                                                                   # noqa
StockGlance2020_fake_frame_ = None                                                                                  # noqa
extract_filename='StockGlance2020_extract_stock_balances.csv'
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

    global __StockGlance2020, hideHiddenSecurities, hideInactiveAccounts, hideHiddenAccounts, lAllCurrency, filterForCurrency
    global lAllSecurity, filterForSecurity, lAllAccounts, filterForAccounts, lIncludeCashBalances, lStripASCII, csvDelimiter, scriptpath
    global lSplitSecuritiesByAccount, lExcludeTotalsFromCSV, lRoundPrice, _column_widths_SG2020
    global lWriteBOMToExportFile_SWSS, lIncludeFutureBalances_SG2020

    myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )
    myPrint("DB", "Loading variables into memory...")

    if myParameters is None: myParameters = {}

    if myParameters.get("__StockGlance2020") is not None: __StockGlance2020 = myParameters.get("__StockGlance2020")
    if myParameters.get("hideHiddenSecurities") is not None: hideHiddenSecurities = myParameters.get("hideHiddenSecurities")
    if myParameters.get("hideInactiveAccounts") is not None: hideInactiveAccounts = myParameters.get("hideInactiveAccounts")
    if myParameters.get("hideHiddenAccounts") is not None: hideHiddenAccounts = myParameters.get("hideHiddenAccounts")
    if myParameters.get("lAllCurrency") is not None: lAllCurrency = myParameters.get("lAllCurrency")
    if myParameters.get("filterForCurrency") is not None: filterForCurrency = myParameters.get("filterForCurrency")
    if myParameters.get("lAllSecurity") is not None: lAllSecurity = myParameters.get("lAllSecurity")
    if myParameters.get("filterForSecurity") is not None: filterForSecurity = myParameters.get("filterForSecurity")
    if myParameters.get("lAllAccounts") is not None: lAllAccounts = myParameters.get("lAllAccounts")
    if myParameters.get("filterForAccounts") is not None: filterForAccounts = myParameters.get("filterForAccounts")
    if myParameters.get("lIncludeCashBalances") is not None: lIncludeCashBalances = myParameters.get("lIncludeCashBalances")
    if myParameters.get("lSplitSecuritiesByAccount") is not None: lSplitSecuritiesByAccount = myParameters.get("lSplitSecuritiesByAccount")
    if myParameters.get("lExcludeTotalsFromCSV") is not None: lExcludeTotalsFromCSV = myParameters.get("lExcludeTotalsFromCSV")
    if myParameters.get("lIncludeFutureBalances_SG2020") is not None: lIncludeFutureBalances_SG2020 = myParameters.get("lIncludeFutureBalances_SG2020")
    if myParameters.get("lDontRoundPrice") is not None: lRoundPrice = myParameters.get("lDontRoundPrice")
    if myParameters.get("lStripASCII") is not None: lStripASCII = myParameters.get("lStripASCII")
    if myParameters.get("csvDelimiter") is not None: csvDelimiter = myParameters.get("csvDelimiter")
    if myParameters.get("_column_widths_SG2020") is not None: _column_widths_SG2020 = myParameters.get("_column_widths_SG2020")
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
    global __StockGlance2020
    global hideHiddenSecurities, hideInactiveAccounts, hideHiddenAccounts, lAllCurrency, filterForCurrency
    global lAllSecurity, filterForSecurity, lAllAccounts, filterForAccounts, lIncludeCashBalances, lStripASCII, csvDelimiter, scriptpath
    global lSplitSecuritiesByAccount, lExcludeTotalsFromCSV, lRoundPrice
    global lDisplayOnly, _column_widths_SG2020, lIncludeFutureBalances_SG2020
    global lWriteBOMToExportFile_SWSS

    myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )

    # NOTE: Parameters were loaded earlier on... Preserve existing, and update any used ones...
    # (i.e. other StuWareSoftSystems programs might be sharing the same file)

    if myParameters is None: myParameters = {}

    myParameters["__StockGlance2020"] = version_build
    myParameters["hideHiddenSecurities"] = hideHiddenSecurities
    myParameters["hideInactiveAccounts"] = hideInactiveAccounts
    myParameters["hideHiddenAccounts"] = hideHiddenAccounts
    myParameters["lAllCurrency"] = lAllCurrency
    myParameters["filterForCurrency"] = filterForCurrency
    myParameters["lAllSecurity"] = lAllSecurity
    myParameters["filterForSecurity"] = filterForSecurity
    myParameters["lAllAccounts"] = lAllAccounts
    myParameters["filterForAccounts"] = filterForAccounts
    myParameters["lIncludeCashBalances"] = lIncludeCashBalances
    myParameters["lSplitSecuritiesByAccount"] = lSplitSecuritiesByAccount
    myParameters["lExcludeTotalsFromCSV"] = lExcludeTotalsFromCSV
    myParameters["lIncludeFutureBalances_SG2020"] = lIncludeFutureBalances_SG2020
    myParameters["lDontRoundPrice"] = lRoundPrice
    myParameters["lStripASCII"] = lStripASCII
    myParameters["csvDelimiter"] = csvDelimiter
    myParameters["_column_widths_SG2020"] = _column_widths_SG2020
    myParameters["lWriteBOMToExportFile_SWSS"] = lWriteBOMToExportFile_SWSS

    if not lDisplayOnly and scriptpath != "" and os.path.isdir(scriptpath):
        myParameters["scriptpath"] = scriptpath

    myPrint("DB","variables dumped from memory back into myParameters{}.....")

    return


get_StuWareSoftSystems_parameters_from_file()
myPrint("DB", "DEBUG IS ON..")
# END ALL CODE COPY HERE ###############################################################################################

# Create fake JFrame() so that all popups have correct Moneydance Icons etc
StockGlance2020_fake_frame_ = JFrame()
if (not Platform.isMac()):
    moneydance_ui.getImages()
    StockGlance2020_fake_frame_.setIconImage(MDImages.getImage(moneydance_ui.getMain().getSourceInformation().getIconResource()))
StockGlance2020_fake_frame_.setUndecorated(True)
StockGlance2020_fake_frame_.setVisible(False)
StockGlance2020_fake_frame_.setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE)


class CloseAboutAction(AbstractAction):
    # noinspection PyMethodMayBeStatic
    # noinspection PyUnusedLocal

    def __init__(self, theFrame):
        self.theFrame = theFrame

    def actionPerformed(self, event):
        global debug
        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event:", event)

        self.theFrame.dispose()

def about_this_script():
    global debug, scriptExit

    myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

    # noinspection PyUnresolvedReferences
    about_d = JDialog(StockGlance2020_frame_, "About", Dialog.ModalityType.MODELESS)

    shortcut = Toolkit.getDefaultToolkit().getMenuShortcutKeyMaskEx()
    about_d.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_W, shortcut), "close-window")
    about_d.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_F4, shortcut), "close-window")

    about_d.getRootPane().getActionMap().put("close-window", CloseAboutAction(about_d))

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

class DoTheMenu(AbstractAction):

    def __init__(self, menu, callingClass=None):
        self.menu = menu
        self.callingClass = callingClass

    def actionPerformed(self, event):																				# noqa
        global StockGlance2020_frame_, debug

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

        if event.getActionCommand() == "About":
            about_this_script()

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
        return

def terminate_script():
    global debug, StockGlance2020_frame_, i_am_an_extension_so_run_headless, scriptExit, csvfilename, lDisplayOnly, lGlobalErrorDetected

    myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

    if not lDisplayOnly and not lGlobalErrorDetected:
        try:
            helper = moneydance.getPlatformHelper()
            helper.openDirectory(File(csvfilename))
        except:
            dump_sys_error_to_md_console_and_errorlog()

    if not i_am_an_extension_so_run_headless: print(scriptExit)

    StockGlance2020_frame_.dispose()
    return


csvfilename = None

if decimalCharSep != "." and csvDelimiter == ",": csvDelimiter = ";"  # Override for EU countries or where decimal point is actually a comma...
myPrint("DB", "Decimal point:", decimalCharSep, "Grouping Separator", groupingCharSep, "CSV Delimiter set to:", csvDelimiter)

# Stores  the data table for export
rawDataTable = None
rawrawFooterTable = None

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

label7 = JLabel("Include Cash Balances for each account? (Y/N):")
user_selectCashBalances = JTextField(2)
user_selectCashBalances.setDocument(JTextFieldLimitYN(1, True, "YN"))
if lIncludeCashBalances: user_selectCashBalances.setText("Y")
else:               user_selectCashBalances.setText("N")

label7b = JLabel("Split Security Qtys by Account? (Y/N):")
user_splitSecurities = JTextField(2)
user_splitSecurities.setDocument(JTextFieldLimitYN(1, True, "YN"))
if lSplitSecuritiesByAccount:   user_splitSecurities.setText("Y")
else:                           user_splitSecurities.setText("N")

labelFutureBalances = JLabel("Include Future Balances (rather than current)? (Y/N):")
user_includeFutureBalances = JTextField(2)
user_includeFutureBalances.setDocument(JTextFieldLimitYN(1, True, "YN"))
if lIncludeFutureBalances_SG2020:   user_includeFutureBalances.setText("Y")
else:                               user_includeFutureBalances.setText("N")


label7c = JLabel("Exclude Totals from CSV extract (helps pivots)? (Y/N):")
user_excludeTotalsFromCSV = JTextField(2)
user_excludeTotalsFromCSV.setDocument(JTextFieldLimitYN(1, True, "YN"))
if lExcludeTotalsFromCSV:       user_excludeTotalsFromCSV.setText("Y")
else:                           user_excludeTotalsFromCSV.setText("N")

label7d = JLabel("Round calculated price using security dpc setting (N=No Rounding)? (Y/N):")
user_roundPrice = JTextField(2)
user_roundPrice.setDocument(JTextFieldLimitYN(1, True, "YN"))
if lRoundPrice:       user_roundPrice.setText("Y")
else:                 user_roundPrice.setText("N")

label8 = JLabel("Strip non ASCII characters from CSV export? (Y/N)")
user_selectStripASCII = JTextField(2)
user_selectStripASCII.setDocument(JTextFieldLimitYN(1, True, "YN"))
if lStripASCII: user_selectStripASCII.setText("Y")
else:               user_selectStripASCII.setText("N")

label9 = JLabel("Change CSV Export Delimiter from default to: ';|,'")
user_selectDELIMITER = JTextField(2)
user_selectDELIMITER.setDocument(JTextFieldLimitYN(1, True, "DELIM"))
user_selectDELIMITER.setText(csvDelimiter)

labelBOM = JLabel("Write BOM (Byte Order Mark) to file (helps Excel open files) (Y/N):")
user_selectBOM = JTextField(2)
user_selectBOM.setDocument(JTextFieldLimitYN(1, True, "YN"))
if lWriteBOMToExportFile_SWSS:  user_selectBOM.setText("Y")
else:                           user_selectBOM.setText("N")

label10 = JLabel("Turn DEBUG Verbose messages on? (Y/N)")
user_selectDEBUG = JTextField(2)
user_selectDEBUG.setDocument(JTextFieldLimitYN(1, True, "YN"))
if debug:  user_selectDEBUG.setText("Y")
else:           user_selectDEBUG.setText("N")

userFilters = JPanel(GridLayout(0, 2))
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
userFilters.add(user_selectCashBalances)
userFilters.add(label7b)
userFilters.add(user_splitSecurities)
userFilters.add(labelFutureBalances)
userFilters.add(user_includeFutureBalances)
userFilters.add(label7c)
userFilters.add(user_excludeTotalsFromCSV)
userFilters.add(label7d)
userFilters.add(user_roundPrice)
userFilters.add(label8)
userFilters.add(user_selectStripASCII)
userFilters.add(label9)
userFilters.add(user_selectDELIMITER)
userFilters.add(labelBOM)
userFilters.add(user_selectBOM)
userFilters.add(label10)
userFilters.add(user_selectDEBUG)

lExit = False
lDisplayOnly = False

options = ["Abort", "Display & CSV Export", "Display Only"]
userAction = (JOptionPane.showOptionDialog(StockGlance2020_fake_frame_,
                                     userFilters,
                                     "%s(build: %s) Set Script Parameters...." %(myScriptName,version_build),
                                     JOptionPane.OK_CANCEL_OPTION,
                                     JOptionPane.QUESTION_MESSAGE,
                                     moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                     options,
                                     options[2]))
if userAction == 1:  # Display & Export
    myPrint("DB", "Display and export chosen")
    lDisplayOnly = False
elif userAction == 2:  # Display Only
    lDisplayOnly = True
    myPrint("DB", "Display only with no export chosen")
else:
    # Abort
    myPrint("DB", "User Cancelled Parameter selection.. Will abort..")
    myPopupInformationBox(StockGlance2020_fake_frame_,"User Cancelled Parameter selection.. Will abort..","PARAMETERS")
    lDisplayOnly = False
    lExit = True

if not lExit:
    if debug:
        myPrint("DB", "Parameters Captured", "Sec: ", user_hideHiddenSecurities.getText(),
            "InActAct:", user_hideInactiveAccounts.getText(),
            "HidAct:", user_hideHiddenAccounts.getText(),
            "Curr:", user_selectCurrency.getText(),
            "Ticker:", user_selectTicker.getText(),
            "Filter Accts:", user_selectAccounts.getText(),
            "Include Cash Balances:", user_selectCashBalances.getText(),
            "Split Securities:", user_splitSecurities.getText(),
            "Include Future Balances:", user_includeFutureBalances.getText(),
            "Exclude Totals from CSV:", user_excludeTotalsFromCSV.getText(),
            "Round Calc Price:", user_roundPrice.getText(),
            "Strip ASCII:", user_selectStripASCII.getText(),
            "Write BOM to file:", user_selectBOM.getText(),
            "Verbose Debug Messages: ", user_selectDEBUG.getText(),
            "CSV File Delimiter:", user_selectDELIMITER.getText())
    # endif

    hideHiddenSecurities = user_hideHiddenSecurities.getText() == "Y"
    hideInactiveAccounts = user_hideInactiveAccounts.getText() == "Y"
    hideHiddenAccounts = user_hideHiddenAccounts.getText() == "Y"

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

    lIncludeCashBalances = user_selectCashBalances.getText() == "Y"
    lSplitSecuritiesByAccount = user_splitSecurities.getText() == "Y"
    lExcludeTotalsFromCSV = user_excludeTotalsFromCSV.getText() == "Y"
    lIncludeFutureBalances_SG2020 = user_includeFutureBalances.getText() == "Y"
    lRoundPrice = user_roundPrice.getText() == "Y"
    lStripASCII = user_selectStripASCII.getText() == "Y"

    csvDelimiter = user_selectDELIMITER.getText()
    if csvDelimiter == "" or (not (csvDelimiter in ";|,")):
        myPrint("DB", "Invalid Delimiter:", csvDelimiter, "selected. Overriding with:','")
        csvDelimiter = ","
    if decimalCharSep == csvDelimiter:
        myPrint("DB", "WARNING: The CSV file delimiter:", csvDelimiter, "cannot be the same as your decimal point character:", decimalCharSep, " - Proceeding without file export!!")
        lDisplayOnly = True

    lWriteBOMToExportFile_SWSS = user_selectBOM.getText() == "Y"

    debug = user_selectDEBUG.getText() == "Y"
    myPrint("DB", "DEBUG turned on")

    myPrint("B", "User Parameters...")
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

    if lIncludeCashBalances:
        myPrint("B", "Including Cash Balances - WARNING - this is per account!")
    else:
        myPrint("B", "Excluding Cash Balances")

    if lIncludeFutureBalances_SG2020:
        myPrint("B", "Including Future Balances...")
    else:
        myPrint("B", "Including Current Balances Only....")

    if lRoundPrice:
        myPrint("B", "Will round the calculated price to the security's decimal precision setting...")
    else:
        myPrint("B", "Will perform no rounding of calculated price...")

    if lSplitSecuritiesByAccount:
        myPrint("B", "Splitting Securities by account - WARNING, this will disable sorting....")
    else:
        myPrint("B", "No Splitting Securities by account will be performed....")

    # Now get the export filename
    csvfilename = None

    if not lDisplayOnly:  # i.e. we have asked for a file export - so get the filename

        if lStripASCII:
            myPrint("B", "Will strip non-ASCII characters - e.g. Currency symbols from output file...", " Using Delimiter:", csvDelimiter)
        else:
            myPrint("B", "Non-ASCII characters will not be stripped from file: ", " Using Delimiter:", csvDelimiter)

        if lWriteBOMToExportFile_SWSS:
            myPrint("B", "Script will add a BOM (Byte Order Mark) to front of the extracted file...")
        else:
            myPrint("B", "No BOM (Byte Order Mark) will be added to the extracted file...")

        if lExcludeTotalsFromCSV:
            myPrint("B",  "Will exclude Totals from CSV to assist Pivot tables")

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

            filename = FileDialog(StockGlance2020_fake_frame_, "Select/Create CSV file for extract (CANCEL=NO EXPORT)")
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
                myPopupInformationBox(StockGlance2020_fake_frame_,"User chose to cancel or no file selected >>  So no Extract will be performed... ","FILE SELECTION")
            elif str(csvfilename).endswith(".moneydance"):
                myPrint("B", "User selected file:", csvfilename)
                myPrint("B", "Sorry - User chose to use .moneydance extension - I will not allow it!... So no Extract will be performed...")
                myPopupInformationBox(StockGlance2020_fake_frame_,"Sorry - User chose to use .moneydance extension - I will not allow it!... So no Extract will be performed...","FILE SELECTION")
                lDisplayOnly = True
                csvfilename = None
            elif ".moneydance" in filename.getDirectory():
                myPrint("B", "User selected file:", filename.getDirectory(), csvfilename)
                myPrint("B", "Sorry - FileDialog() User chose to save file in .moneydance location. NOT Good practice so I will not allow it!... So no Extract will be performed...")
                myPopupInformationBox(StockGlance2020_fake_frame_,"Sorry - FileDialog() User chose to save file in .moneydance location. NOT Good practice so I will not allow it!... So no Extract will be performed...","FILE SELECTION")
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
                        myPrint("B", 'Will display Stock balances and extract to file: ', csvfilename, "(NOTE: Should drop non utf8 characters...)")
                    else:
                        myPrint("B", 'Will display Stock balances and extract to file: ', csvfilename, "...")
                    scriptpath = os.path.dirname(csvfilename)
                else:
                    myPrint("B", "Sorry - I just checked and you do not have permissions to create this file:", csvfilename)
                    myPopupInformationBox(StockGlance2020_fake_frame_,"Sorry - I just checked and you do not have permissions to create this file: %s" %csvfilename,"FILE SELECTION")
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

    # save here in case script crashes....
    save_StuWareSoftSystems_parameters_to_file()

    class StockGlance2020():  # MAIN program....
        def __init__(self):
            pass

        global debug, hideHiddenSecurities, hideInactiveAccounts, lSplitSecuritiesByAccount, acctSeparator, lRoundPrice, lIncludeFutureBalances_SG2020
        global rawDataTable, rawFooterTable, headingNames
        global _SHRS_FORMATTED, _SHRS_RAW, _PRICE_FORMATTED, _PRICE_RAW, _CVALUE_FORMATTED, _CVALUE_RAW, _BVALUE_FORMATTED, _BVALUE_RAW, _SORT
        global _CBVALUE_FORMATTED, _CBVALUE_RAW, _GAIN_FORMATTED, _GAIN_RAW, _EXCLUDECSV, _GAINPCT

        myPrint("D","In ", inspect.currentframe().f_code.co_name, "()")

        book = None
        table = None
        tableModel = None
        footerModel = None
        totalBalance = None  # total of all Stock.Securities in all Accounts inb local currency
        totalBalanceBase = None
        totalCashBalanceBase = None
        totalCostBasisBase = None
        totalGainBase = None

        sameCurrency = None
        allOneCurrency = True
        currXrate = None
        lRemoveCurrColumn = None

        QtyOfSharesTable = None
        AccountsTable = None
        CashBalancesTable = None
        CostBasisTotals = None
        CashBalanceTableData = []

        lightLightGray = Color(0xDCDCDC)

        rawFooterTable = []                                                                                      # noqa
        rawDataTable = []                                                                                        # noqa

        #  Per column metadata - fields 10 - 16 not actually used but contain the raw numbers from fields 2,3,5,6 + sortfield
        columnNames = ["Symbol", "Stock", "Shares/Units", "Price", "Curr", "Curr Value", "Base Value", "Cost Basis",
                       "UnRlsd Gain", "Gain%", "Accounts",
                       "_Shrs", "_Price", "_CValue", "_BValue", "_CBValue", "_Gain", "_SORT", "_Exclude"]
        columnTypes = ["Text", "Text", "TextNumber", "TextNumber", "TextC", "TextNumber", "TextNumber",
                       "TextNumber", "TextNumber", "%", "Text", "N",
                       "N", "N", "N", "N", "N", "N", "TEXT"]
        headingNames = columnNames                                                                              # noqa
        _SHRS_FORMATTED = 2                                                                                     # noqa
        _SHRS_RAW = 11                                                                                          # noqa
        _PRICE_FORMATTED = 3                                                                                    # noqa
        _PRICE_RAW = 12                                                                                         # noqa
        _CVALUE_FORMATTED = 5                                                                                   # noqa
        _CVALUE_RAW = 13                                                                                        # noqa
        _BVALUE_FORMATTED = 6                                                                                   # noqa
        _BVALUE_RAW = 14                                                                                        # noqa
        _CBVALUE_FORMATTED = 7                                                                                  # noqa
        _CBVALUE_RAW = 15                                                                                       # noqa
        _GAIN_FORMATTED = 8                                                                                     # noqa
        _GAIN_RAW = 16                                                                                          # noqa
        _GAINPCT = 9                                                                                            # noqa
        _SORT = 17                                                                                              # noqa
        _EXCLUDECSV = 18                                                                                        # noqa

        def getTableModel(self, book):
            global debug, baseCurrency, rawDataTable, lAllCurrency, filterForCurrency, lAllSecurity, filterForSecurity
            myPrint("D","In ", inspect.currentframe().f_code.co_name, "()")
            myPrint("D", "MD Book: ", book)

            ct = book.getCurrencies()

            baseCurrency = moneydance.getCurrentAccountBook().getCurrencies().getBaseType()
            myPrint("D", "Base Currency: ", baseCurrency.getIDString(), " : ", baseCurrency.getName())

            allCurrencies = ct.getAllCurrencies()

            rawDataTable = []
            today = Calendar.getInstance()
            myPrint("D", "Running today: ", sdf.format(today.getTime()))

            self.sumInfoBySecurity(book)  # Creates Dict(hashmap) QtyOfSharesTable, AccountsTable, CashTable : <CurrencyType, Long>  contains no account info

            if debug:
                myPrint("DB", "Result of sumInfoBySecurity(book) self.QtyOfSharesTable: \t", self.QtyOfSharesTable)
                myPrint("DB", "Result of sumInfoBySecurity(book) self.AccountsTable: \t", self.AccountsTable)
                myPrint("DB", "Result of sumInfoBySecurity(book) self.CashBalancesTable: \t", self.CashBalancesTable)
                myPrint("DB", "Result of sumInfoBySecurity(book) self.CostBasisTotals: \t", self.CostBasisTotals)

            if len(self.QtyOfSharesTable) < 1:
                myPrint("DB", "Sorry - you have no shares - exiting...")
                myPopupInformationBox(None, "Sorry - you have no shares - exiting...","StockGlance2020")
                return None

            self.totalBalance = 0.0
            self.totalBalanceBase = 0.0
            self.totalCashBalanceBase = 0.0
            self.totalCostBasisBase = 0.0
            self.totalGainBase = 0.0

            self.lRemoveCurrColumn = True

            myPrint("D", "Now processing all securities (currencies) and building my own table of results to build GUI....")
            for curr in allCurrencies:
                # noinspection PyUnresolvedReferences
                if ((hideHiddenSecurities and not curr.getHideInUI()) or (
                        not hideHiddenSecurities)) and curr.getCurrencyType() == CurrencyType.Type.SECURITY:
                    # NOTE: (1.0 / .getRelativeRate() ) gives you the 'Current Price' from the History Screen
                    # NOTE: .getPrice(None) gives you the Current Price relative to the current Base to Security Currency..
                    # .......So Base>Currency rate * .getRate(None) also gives Current Price

                    roundPrice = curr.getDecimalPlaces()
                    if lRoundPrice:
                        price = round(1.0 / curr.adjustRateForSplitsInt(DateUtil.convertCalToInt(today),curr.getRelativeRate()),roundPrice)
                    else:
                        price = (1.0 / curr.adjustRateForSplitsInt(DateUtil.convertCalToInt(today), curr.getRelativeRate()))

                    qty = self.QtyOfSharesTable.get(curr)
                    if qty is None: qty = 0

                    if lAllCurrency \
                            or (
                            filterForCurrency.upper().strip() in curr.getRelativeCurrency().getIDString().upper().strip()) \
                            or (
                            filterForCurrency.upper().strip() in curr.getRelativeCurrency().getName().upper().strip()):
                        if qty > 0:
                            if lAllSecurity \
                                    or (filterForSecurity.upper().strip() in curr.getTickerSymbol().upper().strip()) \
                                    or (filterForSecurity.upper().strip() in curr.getName().upper().strip()):
                                myPrint("D", "Found Security..: ", curr, curr.getTickerSymbol(), " Curr: ", curr.getRelativeCurrency().getIDString(),
                                        " Price: ", price, " Qty: ", curr.formatSemiFancy(qty, decimalCharSep))

                                securityCostBasis = self.CostBasisTotals.get(curr)

                                # This new loop in version_build v4b does the account split within Securities (a bit of a retrofit hack)
                                split_acct_array = self.AccountsTable.get(curr)

                                if len(split_acct_array) < 1:
                                    myPrint("B", "Major logic error... Aborting", curr.getName())
                                    raise(Exception("Split Security logic...Array len <1"))

                                for iSplitAcctArray in range(0, len(split_acct_array)):
                                    qtySplit = split_acct_array[iSplitAcctArray][1]

                                    balance = (0.0 if (qty is None) else curr.getDoubleValue(qty) * price)  # Value in Currency
                                    balanceSplit = (0.0 if (qtySplit is None) else curr.getDoubleValue(qtySplit) * price)  # Value in Currency
                                    exchangeRate = 1.0
                                    securityIsBase = True
                                    ct = curr.getTable()
                                    relativeToName = curr.getParameter(CurrencyType.TAG_RELATIVE_TO_CURR)
                                    if relativeToName is not None:
                                        self.currXrate = ct.getCurrencyByIDString(relativeToName)
                                        if self.currXrate.getIDString() == baseCurrency.getIDString():
                                            myPrint("D", "Found conversion rate - but it's already the base rate..: ", relativeToName)
                                        else:
                                            securityIsBase = False
                                            # exchangeRate = round(self.currXrate.getRate(baseCurrency),self.currXrate.getDecimalPlaces())
                                            exchangeRate = self.currXrate.getRate(baseCurrency)
                                            myPrint("D", "Found conversion rate: ", relativeToName, exchangeRate)
                                    else:
                                        myPrint("D", "No conversion rate found.... Assuming Base Currency")
                                        self.currXrate = baseCurrency

                                    # Check to see if all Security Currencies are the same...?
                                    if self.allOneCurrency:
                                        if self.sameCurrency is None:               self.sameCurrency = self.currXrate
                                        if self.sameCurrency != self.currXrate:     self.allOneCurrency = False

                                    balanceBase = (0.0 if (qty is None) else (curr.getDoubleValue(qty) * price / exchangeRate))  # Value in Base Currency
                                    balanceBaseSplit = (0.0 if (qtySplit is None) else (curr.getDoubleValue(qtySplit) * price / exchangeRate))  # Value in Base Currency

                                    costBasisBase = (0.0 if (securityCostBasis is None) else round(self.currXrate.getDoubleValue(securityCostBasis) / exchangeRate, 2))
                                    gainBase = round(balanceBase, 2) - costBasisBase

                                    costBasisBaseSplit = round(self.currXrate.getDoubleValue(split_acct_array[iSplitAcctArray][2]) / exchangeRate, 2)
                                    gainBaseSplit = round(balanceBaseSplit, 2) - costBasisBaseSplit

                                    if debug:
                                        if iSplitAcctArray == 0:
                                            myPrint("D", "Values found (local, base, cb, gain): ", balance, balanceBase, costBasisBase, gainBase)
                                        if lSplitSecuritiesByAccount:
                                            myPrint("D", "Split Values found (qty, local, base, cb, gain): ", qtySplit, balanceSplit, balanceBaseSplit, costBasisBaseSplit, gainBaseSplit)

                                    if not lSplitSecuritiesByAccount:
                                        break

                                    # If you're confused, these are the accounts within a security
                                    entry = []
                                    entry.append(curr.getTickerSymbol())  # c0
                                    entry.append(curr.getName())  # c1
                                    entry.append(curr.formatSemiFancy(qtySplit, decimalCharSep))  # c2
                                    entry.append(self.myNumberFormatter(price, False, self.currXrate, baseCurrency,
                                                                        roundPrice))  # c3
                                    entry.append(self.currXrate.getIDString())  # c4
                                    x = None
                                    if securityIsBase:
                                        entry.append(None)  # c5 - don't bother displaying if base curr
                                    else:
                                        self.lRemoveCurrColumn = False
                                        entry.append(self.myNumberFormatter(balanceSplit, False, self.currXrate,
                                                                            baseCurrency, 2))  # Local Curr Value
                                        x = round(balanceSplit, 2)
                                    entry.append(self.myNumberFormatter(balanceBaseSplit, True, self.currXrate,
                                                                   baseCurrency,
                                                                   2))  # Value Base Currency
                                    entry.append(self.myNumberFormatter(costBasisBaseSplit, True, self.currXrate,
                                                                        baseCurrency, 2))  # Cost Basis
                                    entry.append(self.myNumberFormatter(gainBaseSplit, True, self.currXrate,
                                                                   baseCurrency,
                                                                   2))  # Gain
                                    entry.append(round(gainBaseSplit / costBasisBaseSplit, 3))
                                    entry.append(split_acct_array[iSplitAcctArray][0].replace(acctSeparator, "",
                                                                                         1))  # Acct
                                    entry.append(curr.getDoubleValue(qtySplit))  # _Shrs
                                    entry.append(price)  # _Price
                                    entry.append(x)  # _CValue
                                    entry.append(round(balanceBaseSplit, 2))  # _BValue
                                    entry.append(costBasisBaseSplit)  # _Cost Basis
                                    entry.append(gainBaseSplit)  # _Gain
                                    entry.append(str(curr.getName()).upper() + "000" + split_acct_array[iSplitAcctArray][0].upper().replace(acctSeparator, "", 1))  # _SORT
                                    entry.append(False)  # Never exclude
                                    rawDataTable.append(entry)
                                # NEXT

                                # Now add the main total line for the security.....
                                if lSplitSecuritiesByAccount:
                                    blankEntry = []
                                    blankEntry.append("----------")
                                    blankEntry.append(None)
                                    blankEntry.append("----------")
                                    blankEntry.append(None)
                                    blankEntry.append(None)
                                    blankEntry.append(None)
                                    blankEntry.append("----------")
                                    blankEntry.append("----------")
                                    blankEntry.append("----------")
                                    blankEntry.append(None)
                                    blankEntry.append(None)
                                    blankEntry.append("----------")
                                    blankEntry.append(None)
                                    blankEntry.append(None)
                                    blankEntry.append("----------")
                                    blankEntry.append("----------")
                                    blankEntry.append("----------")
                                    blankEntry.append(str(curr.getName()).upper() + "555")
                                    blankEntry.append(lExcludeTotalsFromCSV)
                                    rawDataTable.append(blankEntry)

                                entry = []
                                if lSplitSecuritiesByAccount:
                                    entry.append("totals: " + curr.getTickerSymbol())  # c0
                                else:
                                    entry.append(curr.getTickerSymbol())  # c0
                                entry.append(curr.getName())  # c1
                                entry.append(curr.formatSemiFancy(qty, decimalCharSep))  # c2
                                entry.append(self.myNumberFormatter(price, False, self.currXrate, baseCurrency,
                                                                    roundPrice))  # c3
                                entry.append(self.currXrate.getIDString())  # c4
                                x = None
                                if securityIsBase:                                                                          # noqa
                                    entry.append(None)  # c5 - don't bother displaying if base curr
                                else:
                                    self.lRemoveCurrColumn = False
                                    entry.append(self.myNumberFormatter(balance, False, self.currXrate, baseCurrency,2))         # noqa
                                    x = round(balance, 2)

                                entry.append(self.myNumberFormatter(balanceBase, True, self.currXrate, baseCurrency,2))     # noqa
                                entry.append(self.myNumberFormatter(costBasisBase, True, self.currXrate, baseCurrency,2))   # noqa
                                entry.append(self.myNumberFormatter(gainBase, True, self.currXrate, baseCurrency,2))        # noqa
                                entry.append(round(gainBase / costBasisBase, 3))
                                buildAcctString = ""
                                for iIterateAccts in range(0, len(split_acct_array)):
                                    buildAcctString += split_acct_array[iIterateAccts][0]
                                buildAcctString = buildAcctString[:-len(acctSeparator)]
                                entry.append(buildAcctString)  # Acct
                                entry.append(curr.getDoubleValue(qty))  # _Shrs = (raw number)
                                entry.append(price)  # _Price = (raw number)
                                entry.append(x)  # _CValue =  (raw number)
                                entry.append(round(balanceBase, 2))  # _BValue =  (raw number)
                                entry.append(costBasisBase)  # _Cost Basis
                                entry.append(gainBase)  # _Gain
                                entry.append(str(curr.getName()).upper() + "888")  # _SORT
                                entry.append((False if (not lSplitSecuritiesByAccount) else lExcludeTotalsFromCSV))
                                rawDataTable.append(entry)

                                if lSplitSecuritiesByAccount:
                                    blankEntry = []
                                    blankEntry.append("          ")
                                    blankEntry.append(None)
                                    blankEntry.append(None)
                                    blankEntry.append(None)
                                    blankEntry.append(None)
                                    blankEntry.append(None)
                                    blankEntry.append("          ")
                                    blankEntry.append("          ")
                                    blankEntry.append("          ")
                                    blankEntry.append(None)
                                    blankEntry.append(None)
                                    blankEntry.append(None)
                                    blankEntry.append(None)
                                    blankEntry.append(None)
                                    blankEntry.append(None)
                                    blankEntry.append(None)
                                    blankEntry.append(None)
                                    blankEntry.append(str(curr.getName()).upper() + "999")
                                    blankEntry.append(lExcludeTotalsFromCSV)
                                    rawDataTable.append(blankEntry)

                                self.totalBalance += round(balance, 2)  # You can round here if you like....
                                self.totalBalanceBase += round(balanceBase, 2)  # You can round here if you like....

                                self.totalCostBasisBase += costBasisBase
                                self.totalGainBase += gainBase

                                if lIncludeCashBalances:
                                    cash = 0.0                                                                  # noqa
                                    # Search to see if Account exists/has been used already for Cash Balance - Only use once!
                                    acct_string = ""
                                    for keys in self.CashBalancesTable.keys():
                                        data = self.CashBalancesTable.get(keys)
                                        acct_array = self.AccountsTable.get(curr)
                                        for iArray in range(0, len(acct_array)):
                                            acct_string += acct_array[iArray][0]  # The account name
                                        # NEXT
                                        if (str(keys) + acctSeparator) in acct_string:
                                            myPrint("D", "CashBal Search - Found:", keys, "in", str(self.AccountsTable.get(curr)), "Cash Bal:", data)
                                            cash = data
                                            self.CashBalancesTable[keys] = 0.0  # Now delete it so it cannot be used again!
                                            self.totalCashBalanceBase = self.totalCashBalanceBase + cash
                                            self.CashBalanceTableData.append([keys, cash])
                                            continue
                                            # Keep searching as a Security may be used in many accounts...
                            else:
                                myPrint("D", "Skipping non Filtered Security/Ticker:", curr, curr.getTickerSymbol())
                        else:
                            myPrint("D", "Skipping Security with 0 shares..: ", curr, curr.getTickerSymbol(),
                                    " Curr: ", curr.getRelativeCurrency().getIDString(), " Price: ", price, " Qty: ", curr.formatSemiFancy(qty, decimalCharSep))
                    else:
                        myPrint("D", "Skipping non Filtered Security/Currency:", curr, curr.getTickerSymbol(), curr.getRelativeCurrency().getIDString())
                elif curr.getHideInUI() and curr.getCurrencyType() == CurrencyType.Type.SECURITY:
                    myPrint("D", "Skipping Hidden(inUI) Security..: ", curr, curr.getTickerSymbol(), " Curr: ", curr.getRelativeCurrency().getIDString())

                else:
                    myPrint("D", "Skipping non Security:", curr, curr.getTickerSymbol())

            if lSplitSecuritiesByAccount:
                rawDataTable = sorted(rawDataTable, key=lambda _x: (_x[_SORT]))
            # else:
            #     rawDataTable = sorted(rawDataTable, key=lambda _x: (_x[1]) )

            return DefaultTableModel(rawDataTable, self.columnNames)

        def getFooterModel(self):
            global debug, baseCurrency, rawFooterTable, lIncludeCashBalances
            myPrint("D","In ", inspect.currentframe().f_code.co_name, "()")
            myPrint("D", "Generating the footer table data....")

            blankEntry = []
            blankEntry.append("==========")
            blankEntry.append(None)
            blankEntry.append(None)
            blankEntry.append(None)
            blankEntry.append(None)
            blankEntry.append(None)
            blankEntry.append("==========")
            blankEntry.append("==========")
            blankEntry.append("==========")
            blankEntry.append(None)
            blankEntry.append(None)
            blankEntry.append(None)
            blankEntry.append(None)
            blankEntry.append(None)
            blankEntry.append(None)
            blankEntry.append(None)
            blankEntry.append(None)
            blankEntry.append(None)
            blankEntry.append(lExcludeTotalsFromCSV)

            entry = []
            entry.append("Total: Securities")
            entry.append(None)
            entry.append(None)
            entry.append(None)
            entry.append(None)
            x = None
            if self.allOneCurrency and (self.currXrate != baseCurrency):
                myPrint("D", "getFooterModel: sameCurrency=", self.currXrate)
                if self.currXrate is None:
                    entry.append(None)
                else:
                    x = self.totalBalance
                    entry.append(self.myNumberFormatter(self.totalBalance, False, self.currXrate, baseCurrency, 2))
            else:
                myPrint("D", "getFooterModel: was not allOneCurrency..")
                entry.append(None)
            entry.append(self.myNumberFormatter(self.totalBalanceBase, True, baseCurrency, baseCurrency, 2))
            entry.append(self.myNumberFormatter(self.totalCostBasisBase, True, baseCurrency, baseCurrency,2))  # Cost Basis
            entry.append(self.myNumberFormatter(self.totalGainBase, True, baseCurrency, baseCurrency, 2))  # Gain
            entry.append(round(self.totalGainBase / self.totalCostBasisBase, 3))
            entry.append("<<" + baseCurrency.getIDString())
            entry.append(None)
            entry.append(None)
            entry.append(x)
            entry.append(self.totalBalanceBase)
            entry.append(self.totalCostBasisBase)  # _Cost Basis
            entry.append(self.totalGainBase)  # _Gain
            entry.append(None)
            entry.append(lExcludeTotalsFromCSV)

            rawFooterTable = []
            rawFooterTable.append(entry)

            if lIncludeCashBalances:
                rawFooterTable.append(blankEntry)
                for _i in range(0, len(self.CashBalanceTableData)):
                    if self.CashBalanceTableData[_i][1] != 0:
                        entry = []
                        entry.append("Cash Bal/Acct:")
                        entry.append(None)
                        entry.append(None)
                        entry.append(None)
                        entry.append(None)
                        entry.append(None)
                        entry.append(self.myNumberFormatter(self.CashBalanceTableData[_i][1], True, baseCurrency,
                                                            baseCurrency, 2))
                        entry.append(None)
                        entry.append(None)
                        entry.append(None)
                        entry.append(str(self.CashBalanceTableData[_i][0]))
                        entry.append(None)  # Cost Basis
                        entry.append(None)  # Gain
                        entry.append(None)
                        entry.append(self.CashBalanceTableData[_i][1])
                        entry.append(None)  # _Cost Basis
                        entry.append(None)  # _Gain
                        entry.append(None)
                        entry.append(False)  # Always include
                        rawFooterTable.append(entry)

                rawFooterTable.append(blankEntry)
                entry = []
                entry.append("Cash Bal TOTAL:")
                entry.append(None)
                entry.append(None)
                entry.append(None)
                entry.append(None)
                entry.append(None)
                entry.append(self.myNumberFormatter(self.totalCashBalanceBase, True, baseCurrency, baseCurrency, 2))
                entry.append(None)
                entry.append(None)
                entry.append(None)
                entry.append("Across all Accounts involved in this table")
                entry.append(None)
                entry.append(None)
                entry.append(None)
                entry.append(self.totalCashBalanceBase)
                entry.append(None)
                entry.append(None)
                entry.append(None)
                entry.append(lExcludeTotalsFromCSV)
                rawFooterTable.append(entry)

                # I was limiting this total to only where no Security filters - but hey it's up to the user to know their data....
                if True or lAllSecurity:  # I don't add them up if selecting one security - probably makes the overal total wrong if multi securities in an account etc...
                    rawFooterTable.append(blankEntry)
                    entry = []
                    entry.append("TOTAL Securities+Cash Bal:")
                    entry.append(None)
                    entry.append(None)
                    entry.append(None)
                    entry.append(None)
                    entry.append(None)
                    entry.append(self.myNumberFormatter((self.totalBalanceBase + self.totalCashBalanceBase), True,
                                                        baseCurrency, baseCurrency, 2))
                    entry.append(self.myNumberFormatter(self.totalCostBasisBase, True, baseCurrency, baseCurrency,
                                                        2))  # Cost Basis
                    entry.append(self.myNumberFormatter(self.totalGainBase, True, baseCurrency, baseCurrency, 2))  # Gain
                    entry.append(round(self.totalGainBase / self.totalCostBasisBase, 3))
                    entry.append("Only valid where whole accounts selected!")
                    entry.append(None)
                    entry.append(None)
                    entry.append(None)
                    entry.append((self.totalBalanceBase + self.totalCashBalanceBase))
                    entry.append(self.totalCostBasisBase)  # _Cost Basis
                    entry.append(self.totalGainBase)  # _Gain
                    entry.append(None)
                    entry.append(lExcludeTotalsFromCSV)
                    rawFooterTable.append(entry)

            # endif

            return DefaultTableModel(rawFooterTable, self.columnNames)

        # Render a currency with given number of fractional digits. NaN or null is an empty cell.
        # noinspection PyMethodMayBeStatic
        def myNumberFormatter(self, theNumber, useBase, exchangeCurr, baseCurr, noDecimals):
            global debug, decimalCharSep, groupingCharSep

            noDecimalFormatter = NumberFormat.getNumberInstance()
            noDecimalFormatter.setMinimumFractionDigits(0)
            noDecimalFormatter.setMaximumFractionDigits(noDecimals)

            if noDecimals == 2: noDecimalFormatter.setMinimumFractionDigits(2)

            if theNumber is None or Double.isNaN(float(theNumber)): return ""

            if Math.abs(float(theNumber)) < 0.01: theNumber = 0L

            if useBase:
                if noDecimals == 0:
                    # MD format functions can't print comma-separated values without a decimal point so
                    # we have to do it ourselves
                    theNumber = baseCurr.getPrefix() + " " + noDecimalFormatter.format(float(theNumber)) + baseCurr.getSuffix()
                else:
                    theNumber = baseCurr.getPrefix() + " " + noDecimalFormatter.format(float(theNumber)) + baseCurr.getSuffix()
                    # theNumber = baseCurr.formatFancy(baseCurr.getLongValue(float(theNumber)), decimalSeparator)
            else:
                if noDecimals == 0:
                    # MD format functions can't print comma-separated values without a decimal point so
                    # we have to do it ourselves
                    theNumber = exchangeCurr.getPrefix() + " " + noDecimalFormatter.format(float(theNumber)) + exchangeCurr.getSuffix()
                else:
                    theNumber = exchangeCurr.getPrefix() + " " + noDecimalFormatter.format(float(theNumber)) + exchangeCurr.getSuffix()
                    # theNumber = exchangeCurr.formatFancy(exchangeCurr.getLongValue(float(theNumber)), decimalSeparator)

            return theNumber

        # noinspection PyArgumentList
        class MyAcctFilter(AcctFilter):

            def __init__(self, selectAccountType="ALL",                                                         # noqa
                         hideInactiveAccounts=True,                                                             # noqa
                         lAllAccounts=True,                                                                     # noqa
                         filterForAccounts="ALL",                                                               # noqa
                         hideHiddenAccounts=True,                                                               # noqa
                         hideHiddenSecurities=True,                                                             # noqa
                         lAllCurrency=True,                                                                     # noqa
                         filterForCurrency="ALL",                                                               # noqa
                         lAllSecurity=True,                                                                     # noqa
                         filterForSecurity="ALL",                                                               # noqa
                         findUUID=None):                                                                        # noqa
                super(AcctFilter, self).__init__()

                # noinspection PyUnresolvedReferences
                if selectAccountType == "ALL":                              pass
                elif selectAccountType == "CAT":                            pass
                elif selectAccountType == "NONCAT":                         pass
                elif selectAccountType == Account.AccountType.ROOT:          pass
                elif selectAccountType == Account.AccountType.BANK:          pass
                elif selectAccountType == Account.AccountType.CREDIT_CARD:   pass
                elif selectAccountType == Account.AccountType.INVESTMENT:    pass
                elif selectAccountType == Account.AccountType.SECURITY:      pass
                elif selectAccountType == Account.AccountType.ASSET:         pass
                elif selectAccountType == Account.AccountType.LIABILITY:     pass
                elif selectAccountType == Account.AccountType.LOAN:          pass
                elif selectAccountType == Account.AccountType.EXPENSE:       pass
                elif selectAccountType == Account.AccountType.INCOME:        pass
                else:   selectAccountType = "ALL"

                self.selectAccountType = selectAccountType
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

            def matches(self, acct):
                if self.findUUID is not None:  # If UUID supplied, override all other parameters...
                    if acct.getUUID() == self.findUUID: return True
                    else: return False
                # endif

                # noinspection PyUnresolvedReferences
                if self.selectAccountType == "ALL" or acct.getAccountType() == self.selectAccountType: pass
                elif self.selectAccountType == "CAT" and (
                        acct.getAccountType() == Account.AccountType.EXPENSE or acct.getAccountType() == Account.AccountType.INCOME): pass
                elif self.selectAccountType == "NONCAT" and not (
                        acct.getAccountType() == Account.AccountType.EXPENSE or acct.getAccountType() == Account.AccountType.INCOME): pass
                else: return False

                if self.hideInactiveAccounts:
                    # This logic replicates Moneydance AcctFilter.ACTIVE_ACCOUNTS_FILTER
                    if (acct.getAccountOrParentIsInactive()): return False
                    if (acct.getHideOnHomePage() and acct.getBalance() == 0): return False

                # noinspection PyUnresolvedReferences
                if acct.getAccountType() == Account.AccountType.SECURITY:
                    theAcct = acct.getParentAccount()  # Security Accounts are sub-accounts of Investment Accounts - so take the Parent
                else:
                    theAcct = acct
                # endif

                if self.lAllAccounts or (
                        self.filterForAccounts.upper().strip() in theAcct.getFullAccountName().upper().strip()): pass
                else: return False

                if ((not self.hideHiddenAccounts) or (
                        self.hideHiddenAccounts and not theAcct.getHideOnHomePage())):  pass
                else: return False

                curr = acct.getCurrencyType()
                currID = curr.getIDString()
                currName = curr.getName()

                # noinspection PyUnresolvedReferences
                if acct.getAccountType() == Account.AccountType.SECURITY:  # on Security Accounts, get the Currency from the Security master - else from the account)
                    if self.lAllSecurity:
                        pass
                    elif (self.filterForSecurity.upper().strip() in curr.getTickerSymbol().upper().strip()):
                        pass
                    elif (self.filterForSecurity.upper().strip() in curr.getName().upper().strip()):
                        pass
                    else: return False

                    if ((self.hideHiddenSecurities and not curr.getHideInUI()) or (not self.hideHiddenSecurities)):
                        pass
                    else:
                        return False

                    currID = curr.getRelativeCurrency().getIDString()
                    currName = curr.getRelativeCurrency().getName()

                else:
                    pass
                    # endif

                # All accounts and security records can have currencies
                if self.lAllCurrency:
                    pass
                elif (self.filterForCurrency.upper().strip() in currID.upper().strip()):
                    pass
                elif (self.filterForCurrency.upper().strip() in currName.upper().strip()):
                    pass

                else: return False

                # Phew! We made it....
                return True
            # enddef

        # endclass

        def sumInfoBySecurity(self, book):
            global debug, hideInactiveAccounts, hideHiddenAccounts, lAllAccounts, filterForAccounts, lIncludeCashBalances
            global lSplitSecuritiesByAccount, acctSeparator, i_am_an_extension_so_run_headless, lIncludeFutureBalances_SG2020

            myPrint("D","In ", inspect.currentframe().f_code.co_name, "()")

            totals = {}  # Dictionary <CurrencyType, Long>
            accounts = {}
            cashTotals = {}  # Dictionary<CurrencyType, Long>
            cbbasistotals = {}

            lDidIFindAny = False

            # noinspection PyUnresolvedReferences
            for acct in AccountUtil.allMatchesForSearch(book, self.MyAcctFilter(Account.AccountType.SECURITY,
                                                                                hideInactiveAccounts,
                                                                                lAllAccounts,
                                                                                filterForAccounts,
                                                                                hideHiddenAccounts,
                                                                                hideHiddenSecurities,
                                                                                lAllCurrency,
                                                                                filterForCurrency,
                                                                                lAllSecurity,
                                                                                filterForSecurity,
                                                                                None)):
                curr = acct.getCurrencyType()
                account = accounts.get(curr)  # this returns None if curr doesn't exist yet
                total = totals.get(curr)  # this returns None if security/curr doesn't exist yet
                costbasis = cbbasistotals.get(curr)

                if lIncludeFutureBalances_SG2020:
                    _getBalance = acct.getBalance()
                else:
                    _getBalance = acct.getCurrentBalance()

                if _getBalance != 0:  # we only want Securities with holdings
                    if debug and not i_am_an_extension_so_run_headless: print("Processing Acct:", acct.getParentAccount(), "Share/Fund Qty Balances for Security: ", curr, curr.formatSemiFancy(
                            _getBalance, decimalCharSep), " Shares/Units")

                    total = (0L if (total is None) else total) + _getBalance
                    totals[curr] = total

                    getTheCostBasis = InvestUtil.getCostBasis(acct)
                    costbasis = (0L if (costbasis is None) else costbasis) + getTheCostBasis
                    cbbasistotals[curr] = costbasis

                    lDidIFindAny = True

                    if lSplitSecuritiesByAccount:  # Build a mini table if split, else 1 row table...
                        if account is None:
                            accounts[curr] = [
                                    [str(acct.getParentAccount()) + acctSeparator, _getBalance,
                                     getTheCostBasis]]
                        else:
                            account.append([str(acct.getParentAccount()) + acctSeparator, _getBalance,
                                            getTheCostBasis])
                            accounts[curr] = account
                    else:
                        if account is None:
                            account = str(
                                    acct.getParentAccount()) + acctSeparator  # Important - keep the trailing ' :'
                        else:
                            account = account[0][0] + str(
                                    acct.getParentAccount()) + acctSeparator  # concatenate two strings here
                        accounts[curr] = [[account, _getBalance, getTheCostBasis]]

                    if lIncludeCashBalances:
                        # Now get the Currency  for the Security Parent Account - to get Cash  Balance
                        curr = acct.getParentAccount().getCurrencyType()

                        # WARNING Cash balances are by Account and not by Security!
                        if lIncludeFutureBalances_SG2020:
                            cashTotal = curr.getDoubleValue(
                                (acct.getParentAccount().getBalance())) / curr.getRate(
                                None)  # Will be the same Cash balance per account for all Securities..
                        else:
                            cashTotal = curr.getDoubleValue(
                                    (acct.getParentAccount().getCurrentBalance())) / curr.getRate(
                                    None)  # Will be the same Cash balance per account for all Securities..
                        myPrint("D","Cash balance for account:", cashTotal)
                        cashTotals[acct.getParentAccount()] = round(cashTotal, 2)
                        # endfor

            self.QtyOfSharesTable = totals
            self.AccountsTable = accounts
            self.CashBalancesTable = cashTotals
            self.CostBasisTotals = cbbasistotals

            return lDidIFindAny

        class MyJTable(JTable):  # (JTable)
            myPrint("D","In ", inspect.currentframe().f_code.co_name, "()")
            lInTheFooter = False

            def __init__(self, tableModel, lSortTheTable, lInTheFooter):
                global debug
                super(JTable, self).__init__(tableModel)
                self.lInTheFooter = lInTheFooter
                if lSortTheTable: self.fixTheRowSorter()

            def isCellEditable(self, row, column):                                                              # noqa
                return False

            #  Rendering depends on row (i.e. security's currency) as well as column
            # noinspection PyUnusedLocal
            def getCellRenderer(self, row, column):                                                             # noqa
                global StockGlanceInstance
                renderer = None

                if StockGlanceInstance.columnTypes[column] == "Text":
                    renderer = DefaultTableCellRenderer()
                    renderer.setHorizontalAlignment(JLabel.LEFT)
                elif StockGlanceInstance.columnTypes[column] == "TextNumber":
                    renderer = StockGlanceInstance.MyGainsRenderer()
                    renderer.setHorizontalAlignment(JLabel.RIGHT)
                elif StockGlanceInstance.columnTypes[column] == "%":
                    renderer = StockGlanceInstance.MyPercentRenderer()
                    renderer.setHorizontalAlignment(JLabel.RIGHT)
                elif StockGlanceInstance.columnTypes[column] == "TextC":
                    renderer = DefaultTableCellRenderer()
                    renderer.setHorizontalAlignment(JLabel.CENTER)
                else:
                    renderer = DefaultTableCellRenderer()
                return renderer

            class MyTextNumberComparator(Comparator):
                lSortNumber = False
                lSortRealNumber = False

                def __init__(self, sortType):
                    if sortType == "N":
                        self.lSortNumber = True
                    elif sortType == "%":
                        self.lSortRealNumber = True
                    else:
                        self.lSortNumber = False

                def compare(self, str1, str2):
                    global decimalCharSep
                    validString = "-0123456789" + decimalCharSep  # Yes this will strip % sign too, but that still works
                    if self.lSortNumber:
                        # strip non numerics from string so can convert back to float - yes, a bit of a reverse hack
                        conv_string1 = ""
                        if str1 is None or str1 == "": str1 = "0"
                        if str2 is None or str2 == "": str2 = "0"
                        for char in str1:
                            if char in validString:
                                conv_string1 = conv_string1 + char

                        conv_string2 = ""
                        for char in str2:
                            if char in validString:
                                conv_string2 = conv_string2 + char
                        str1 = float(conv_string1)
                        str2 = float(conv_string2)

                        if str1 > str2:
                            return 1
                        elif str1 == str2:
                            return 0
                        else:
                            return -1
                    elif self.lSortRealNumber:
                        if float(str1) > float(str2):
                            return 1
                        elif str1 == str2:
                            return 0
                        else:
                            return -1
                    else:
                        if str1.upper() > str2.upper():
                            return 1
                        elif str1.upper() == str2.upper():
                            return 0
                        else:
                            return -1

                # enddef

            def fixTheRowSorter(
                    self):  # by default everthing gets coverted to strings. We need to fix this and code for my string number formats
                global _SHRS_FORMATTED, _SHRS_RAW, _PRICE_FORMATTED, _PRICE_RAW, _CVALUE_FORMATTED, _CVALUE_RAW, _BVALUE_FORMATTED, _BVALUE_RAW, _SORT
                global _CBVALUE_FORMATTED, _CBVALUE_RAW, _GAIN_FORMATTED, _GAIN_RAW, _EXCLUDECSV, _GAINPCT

                sorter = TableRowSorter()
                self.setRowSorter(sorter)
                sorter.setModel(self.getModel())
                for _i in range(0, self.getColumnCount()):
                    if _i == _SHRS_FORMATTED:
                        sorter.setComparator(_i, self.MyTextNumberComparator("N"))
                    elif _i == _PRICE_FORMATTED:
                        sorter.setComparator(_i, self.MyTextNumberComparator("N"))
                    elif _i == _CVALUE_FORMATTED:
                        sorter.setComparator(_i, self.MyTextNumberComparator("N"))
                    elif _i == _BVALUE_FORMATTED:
                        sorter.setComparator(_i, self.MyTextNumberComparator("N"))
                    elif _i == _CBVALUE_FORMATTED:
                        sorter.setComparator(_i, self.MyTextNumberComparator("N"))
                    elif _i == _GAIN_FORMATTED:
                        sorter.setComparator(_i, self.MyTextNumberComparator("N"))
                    elif _i == _SORT:
                        sorter.setComparator(_i, self.MyTextNumberComparator("N"))
                    elif _i == _GAINPCT:
                        sorter.setComparator(_i, self.MyTextNumberComparator("%"))
                    else:
                        sorter.setComparator(_i, self.MyTextNumberComparator("T"))
                self.getRowSorter().toggleSortOrder(1)

            def prepareRenderer(self, renderer, row, column):  # make Banded rows
                global StockGlanceInstance, lSplitSecuritiesByAccount

                component = super(StockGlanceInstance.MyJTable, self).prepareRenderer(renderer, row, column)    # noqa
                if not self.isRowSelected(row):
                    if (self.lInTheFooter):
                        if "total" in str(self.getValueAt(row, 0)).lower():
                            component.setBackground(StockGlanceInstance.lightLightGray)
                            component.setFont(component.getFont().deriveFont(Font.BOLD))
                    elif (not lSplitSecuritiesByAccount):
                        component.setBackground(
                                self.getBackground() if row % 2 == 0 else StockGlanceInstance.lightLightGray)
                    elif str(self.getValueAt(row, 0)).lower()[:5] == "total":
                        component.setBackground(StockGlanceInstance.lightLightGray)

                return component

        # This copies the standard class and just changes the colour to RED if it detects a negative - leaves field intact
        # noinspection PyArgumentList
        class MyGainsRenderer(DefaultTableCellRenderer):

            def __init__(self):
                super(DefaultTableCellRenderer, self).__init__()

            def setValue(self, value):
                global decimalCharSep
                validString = "-0123456789" + decimalCharSep

                self.setText(value)

                if (value is None
                        or value.strip() == ""
                        or "==" in value
                        or "--" in value):
                    return

                # strip non numerics from string so can convert back to float - yes, a bit of a reverse hack
                conv_string1 = ""
                for char in value:
                    if char in validString:
                        conv_string1 = conv_string1 + char
                try:
                    str1 = float(conv_string1)
                    if float(str1) < 0.0:
                        self.setForeground(Color.RED)
                    else:
                        self.setForeground(Color.DARK_GRAY)
                except:
                    # No real harm done; so move on.... (was failing on 'Fr. 305.2' - double point in text)
                    self.setForeground(Color.DARK_GRAY)

    # This copies the standard class and just changes the colour to RED if it detects a negative - and formats as %
        # noinspection PyArgumentList
        class MyPercentRenderer(DefaultTableCellRenderer):

            def __init__(self):
                super(DefaultTableCellRenderer, self).__init__()

            def setValue(self, value):
                if value is None: return

                self.setText("{:.1%}".format(value))

                if value < 0.0:
                    self.setForeground(Color.RED)
                else:
                    self.setForeground(Color.DARK_GRAY)

        # Synchronises column widths of both JTables
        class ColumnChangeListener(TableColumnModelListener):
            sourceTable = None
            targetTable = None

            def __init__(self, source, target):
                self.sourceTable = source
                self.targetTable = target

            def columnAdded(self, e): pass

            def columnSelectionChanged(self, e): pass

            def columnRemoved(self, e): pass

            def columnMoved(self, e): pass

            # noinspection PyUnusedLocal
            def columnMarginChanged(self, e):
                global _column_widths_SG2020

                sourceModel = self.sourceTable.getColumnModel()
                targetModel = self.targetTable.getColumnModel()
                # listener = map.get(self.targetTable)

                # targetModel.removeColumnModelListener(listener)

                for _i in range(0, sourceModel.getColumnCount()):
                    targetModel.getColumn(_i).setPreferredWidth(sourceModel.getColumn(_i).getWidth())

                    # Saving for later... Yummy!!
                    _column_widths_SG2020[_i] = sourceModel.getColumn(_i).getWidth()
                    myPrint("D","Saving column %s as width %s for later..." %(_i,_column_widths_SG2020[_i]))

                # targetModel.addColumnModelListener(listener)
            # enddef

        # endclass

        # Sync horizontal scroll bars with footer (vertical sync disabled)
        class ScrollSynchronizer(AdjustmentListener):
            v1 = None
            h1 = None
            v2 = None
            h2 = None

            def __init__(self, sp1, sp2):
                # self.v1 = sp1.getVerticalScrollBar()
                self.h1 = sp1.getHorizontalScrollBar()
                # self.v2 = sp2.getVerticalScrollBar()
                self.h2 = sp2.getHorizontalScrollBar()

            def adjustmentValueChanged(self, e):
                scrollBar = e.getSource()
                value = scrollBar.getValue()
                target = None

                # if(scrollBar == self.v1): target = self.v2
                if (scrollBar == self.h1): target = self.h2
                # if(scrollBar == self.v2): target = self.v1
                if (scrollBar == self.h2): target = self.h1

                if target is not None: target.setValue(value)
            # enddef

        # endclass

        class WindowListener(WindowAdapter):
            def windowClosing(self, WindowEvent):                                                               # noqa
                global debug, StockGlance2020_frame_
                myPrint("D","In ", inspect.currentframe().f_code.co_name, "()")
                terminate_script()

        class CloseAction(AbstractAction):
            def actionPerformed(self, event):                                                                   # noqa
                global debug, StockGlance2020_frame_
                myPrint("D","In ", inspect.currentframe().f_code.co_name, "()")
                terminate_script()

        def createAndShowGUI(self):
            global debug, StockGlance2020_frame_, rawDataTable, rawFooterTable, lDisplayOnly, version_build, lSplitSecuritiesByAccount, _column_widths_SG2020
            global lIncludeFutureBalances_SG2020

            global _SHRS_FORMATTED, _SHRS_RAW, _PRICE_FORMATTED, _PRICE_RAW, _CVALUE_FORMATTED, _CVALUE_RAW, _BVALUE_FORMATTED, _BVALUE_RAW, _SORT
            global _CBVALUE_FORMATTED, _CBVALUE_RAW, _GAIN_FORMATTED, _GAIN_RAW, _EXCLUDECSV, _GAINPCT

            myPrint("D","In ", inspect.currentframe().f_code.co_name, "()")

            root = moneydance.getRootAccount()
            self.book = root.getBook()

            self.tableModel = self.getTableModel(self.book)  # Generates/populates the table data
            if self.tableModel is None: return False

            screenSize = Toolkit.getDefaultToolkit().getScreenSize()

            JFrame.setDefaultLookAndFeelDecorated(True)
            if lDisplayOnly:
                StockGlance2020_frame_ = JFrame("Stock Glance 2020 - StuWareSoftSystems(build: %s)..." % version_build)
            else:
                StockGlance2020_frame_ = JFrame("Stock Glance 2020 - StuWareSoftSystems(build: %s)... (NOTE: your file has already been exported)" % version_build)

            if (not Platform.isMac()):
                moneydance_ui.getImages()
                StockGlance2020_frame_.setIconImage(MDImages.getImage(moneydance_ui.getMain().getSourceInformation().getIconResource()))

            # StockGlance2020_frame_.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE)
            StockGlance2020_frame_.setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE)  # The CloseAction() and WindowListener() will handle dispose() - else change back to DISPOSE_ON_CLOSE

            shortcut = Toolkit.getDefaultToolkit().getMenuShortcutKeyMaskEx()

            # Add standard CMD-W keystrokes etc to close window
            StockGlance2020_frame_.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_W, shortcut), "close-window")
            StockGlance2020_frame_.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_F4, shortcut), "close-window")
            StockGlance2020_frame_.getRootPane().getActionMap().put("close-window", self.CloseAction())

            StockGlance2020_frame_.addWindowListener(self.WindowListener())

            if lSplitSecuritiesByAccount:
                self.table = self.MyJTable(self.tableModel, False,False)  # Creates JTable() with special sorting too
            else:
                self.table = self.MyJTable(self.tableModel, True,False)  # Creates JTable() with special sorting too

            self.tableHeader = self.table.getTableHeader()                                                      # noqa
            self.tableHeader.setReorderingAllowed(False)  # no more drag and drop columns, it didn't work (on the footer)
            self.table.getTableHeader().setDefaultRenderer(DefaultTableHeaderCellRenderer())

            self.footerModel = self.getFooterModel()  # Generate/populate the footer table data
            # Creates JTable() for footer - with disabled sorting too
            self.footerTable = self.MyJTable(self.footerModel, False, True)                                      # noqa

            # Column listeners to resize columns on both tables to keep them in sync
            cListener1 = self.ColumnChangeListener(self.table, self.footerTable)
            # cListener2=self.ColumnChangeListener(self.footerTable,self.table) # Not using this as footer headers not manually resizable (as hidden)

            tcm = self.table.getColumnModel()

            myDefaultWidths = [120,300,120,100,80,120,120,120,120,70,350,0,0,0,0,0,0,0,0]

            validCount=0
            lInvalidate=True
            if _column_widths_SG2020 is not None and isinstance(_column_widths_SG2020,(list)) and len(_column_widths_SG2020) == len(myDefaultWidths):
                if sum(_column_widths_SG2020[_SHRS_RAW:])<1:
                    for width in _column_widths_SG2020:
                        if width >= 0 and width <= 1000:                                                             # noqa
                            validCount += 1

            if validCount == len(myDefaultWidths): lInvalidate=False

            if lInvalidate:
                myPrint("DB","Found invalid saved columns = resetting to defaults")
                myPrint("DB","Found: %s" %_column_widths_SG2020)
                myPrint("DB","Resetting to: %s" %myDefaultWidths)
                _column_widths_SG2020 = myDefaultWidths
            else:
                myPrint("DB","Valid column widths loaded - Setting to: %s" %_column_widths_SG2020)
                myDefaultWidths = _column_widths_SG2020

            for _i in range(0, _SHRS_RAW): tcm.getColumn(_i).setPreferredWidth(myDefaultWidths[_i])

            # I'm hiding these columns for ease of data retrieval. The better option would be to remove the columns
            for _i in reversed(range(_SHRS_RAW, tcm.getColumnCount())):
                tcm.getColumn(_i).setMinWidth(0)
                tcm.getColumn(_i).setMaxWidth(0)
                tcm.getColumn(_i).setWidth(0)
                self.table.removeColumn(tcm.getColumn(_i))
            self.table.setAutoResizeMode(JTable.AUTO_RESIZE_OFF)

            myPrint("D","Hiding unused Currency Column...")
            # I'm hiding it rather than removing it so not to mess with sorting etc...
            if self.lRemoveCurrColumn:
                tcm.getColumn(_CVALUE_FORMATTED).setPreferredWidth(0)
                tcm.getColumn(_CVALUE_FORMATTED).setMinWidth(0)
                tcm.getColumn(_CVALUE_FORMATTED).setMaxWidth(0)
                tcm.getColumn(_CVALUE_FORMATTED).setWidth(0)


            cTotal=sum(myDefaultWidths)

            self.footerTable.setColumnSelectionAllowed(False)
            self.footerTable.setRowSelectionAllowed(True)
            # self.footerTable.setFocusable(False)

            # Put the listener here - else it sets the defaults wrongly above....
            tcm.addColumnModelListener(cListener1)

            tcm = self.footerTable.getColumnModel()
            # tcm.addColumnModelListener(cListener2)

            for _i in range(0, _SHRS_RAW): tcm.getColumn(_i).setPreferredWidth(myDefaultWidths[_i])

            # I'm hiding these columns for ease of data retrieval. The better option would be to remove the columns
            for _i in reversed(range(_SHRS_RAW, tcm.getColumnCount())):
                tcm.getColumn(_i).setMinWidth(0)
                tcm.getColumn(_i).setMaxWidth(0)
                tcm.getColumn(_i).setWidth(0)
                self.footerTable.removeColumn(tcm.getColumn(_i))
            self.footerTable.setAutoResizeMode(JTable.AUTO_RESIZE_OFF)

            # I'm hiding it rather than removing it so not to mess with sorting etc...
            if self.lRemoveCurrColumn:
                tcm.getColumn(_CVALUE_FORMATTED).setPreferredWidth(0)
                tcm.getColumn(_CVALUE_FORMATTED).setMinWidth(0)
                tcm.getColumn(_CVALUE_FORMATTED).setMaxWidth(0)
                tcm.getColumn(_CVALUE_FORMATTED).setWidth(0)

            self.footerTableHeader = self.footerTable.getTableHeader()                                        # noqa
            self.footerTableHeader.setEnabled(False)  # may have worked, but doesn't...
            self.footerTableHeader.setPreferredSize(Dimension(0, 0))  # this worked no more footer Table header

            self.scrollPane = JScrollPane(self.table, JScrollPane.VERTICAL_SCROLLBAR_ALWAYS,JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED)  # noqa
            self.scrollPane.getHorizontalScrollBar().setPreferredSize(Dimension(0, 0))
            self.scrollPane.setBorder(CompoundBorder(MatteBorder(0, 0, 1, 0, Color.gray), EmptyBorder(0, 0, 0, 0)))
            rowCount = self.table.getRowCount()
            rowHeight = self.table.getRowHeight()
            interCellSpacing = self.table.getIntercellSpacing().height
            headerHeight = self.table.getTableHeader().getPreferredSize().height
            insets = self.scrollPane.getInsets()
            scrollHeight = self.scrollPane.getHorizontalScrollBar().getPreferredSize()
            width = min(cTotal + 20, screenSize.width)  # width of all elements

            calcScrollPaneHeightRequired = (min(screenSize.height - 300, max(60, ((rowCount * rowHeight)
                    + ((rowCount) * (interCellSpacing)) + headerHeight + insets.top + insets.bottom + scrollHeight.height))))

            if debug:
                myPrint("D", "ScreenSize: ", screenSize)
                myPrint("D", "Main JTable heights....")
                myPrint("D", "Row Count: ", rowCount)
                myPrint("D", "RowHeight: ", rowHeight)
                myPrint("D", "Intercell spacing: ", interCellSpacing)
                myPrint("D", "Header height: ", headerHeight)
                myPrint("D", "Insets, Top/Bot: ", insets, insets.top, insets.bottom)
                myPrint("D", "Total scrollpane height: ", calcScrollPaneHeightRequired)
                myPrint("D", "Scrollbar height: ", scrollHeight, scrollHeight.height)

            # Basically set the main table to fill most of the screen maxing at 800, but allowing for the footer...
            self.scrollPane.setPreferredSize(Dimension(width, calcScrollPaneHeightRequired))

            StockGlance2020_frame_.add(self.scrollPane, BorderLayout.CENTER)

            self.footerScrollPane = JScrollPane(self.footerTable, JScrollPane.VERTICAL_SCROLLBAR_ALWAYS,JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED)  # noqa
            self.footerScrollPane.setBorder(CompoundBorder(MatteBorder(0, 0, 1, 0, Color.gray), EmptyBorder(0, 0, 0, 0)))

            myScrollSynchronizer = self.ScrollSynchronizer(self.scrollPane, self.footerScrollPane)
            # self.scrollPane.getVerticalScrollBar().addAdjustmentListener(myScrollSynchronizer)
            self.scrollPane.getHorizontalScrollBar().addAdjustmentListener(myScrollSynchronizer)
            # self.footerScrollPane.getVerticalScrollBar().addAdjustmentListener(myScrollSynchronizer)
            self.footerScrollPane.getHorizontalScrollBar().addAdjustmentListener(myScrollSynchronizer)

            frowCount = self.footerTable.getRowCount()
            frowHeight = self.footerTable.getRowHeight()
            finterCellSpacing = self.footerTable.getIntercellSpacing().height
            fheaderHeight = self.footerTable.getTableHeader().getPreferredSize().height
            finsets = self.footerScrollPane.getInsets()
            fscrollHeight = self.footerScrollPane.getHorizontalScrollBar().getPreferredSize()
            fcalcScrollPaneHeightRequired = min(220, (((frowCount * frowHeight) + ((
                                                                                           frowCount + 1) * finterCellSpacing) + fheaderHeight + finsets.top + finsets.bottom + fscrollHeight.height)))
            # fcalcScrollPaneHeightRequired = ((((frowCount * frowHeight) + ((frowCount + 1) * finterCellSpacing) + fheaderHeight + finsets.top + finsets.bottom + fscrollHeight.height)))

            if debug:
                myPrint("D","Footer JTable heights....")
                myPrint("D","Row Count: ", frowCount)
                myPrint("D","RowHeight: ", frowHeight)
                myPrint("D","Intercell spacing: ", finterCellSpacing)
                myPrint("D","Header height: ", fheaderHeight)
                myPrint("D","Insets, Top/Bot: ", finsets, finsets.top, finsets.bottom)
                myPrint("D","Total scrollpane height: ", fcalcScrollPaneHeightRequired)
                myPrint("D","Scrollbar height: ", fscrollHeight, fscrollHeight.height)

            self.footerScrollPane.setPreferredSize(Dimension(width, fcalcScrollPaneHeightRequired))
            StockGlance2020_frame_.add(self.footerScrollPane, BorderLayout.SOUTH)

            myPrint("D","Total frame height required: ", calcScrollPaneHeightRequired, " + ",
                fcalcScrollPaneHeightRequired, "+ Intercells: ", finsets.top, finsets.bottom, " = ",
                (calcScrollPaneHeightRequired + fcalcScrollPaneHeightRequired) +
                (finsets.top * 2) + (finsets.bottom * 2))

            # Seems to be working well without setting the frame sizes + pack()
            # StockGlance2020_frame_.setPreferredSize(Dimension(width, max(150,calcScrollPaneHeightRequired+fcalcScrollPaneHeightRequired+(finsets.top*2)+(finsets.bottom*2))))
            # StockGlance2020_frame_.setSize(width,calcScrollPaneHeightRequired+fcalcScrollPaneHeightRequired)   # for some reason this seems irrelevant?

            if Platform.isOSX():
                save_useScreenMenuBar= System.getProperty("apple.laf.useScreenMenuBar")
                System.setProperty("apple.laf.useScreenMenuBar", "false")

            mb = JMenuBar()
            menuH = JMenu("<html><B>ABOUT</b></html>")

            menuItemA = JMenuItem("About")
            menuItemA.setToolTipText("About...")
            menuItemA.addActionListener(DoTheMenu(menuH))
            menuItemA.setEnabled(True)
            menuH.add(menuItemA)
            mb.add(menuH)

            StockGlance2020_frame_.setJMenuBar(mb)

            if Platform.isOSX():
                System.setProperty("apple.laf.useScreenMenuBar", save_useScreenMenuBar)                                 # noqa

            StockGlance2020_frame_.pack()
            StockGlance2020_frame_.setLocationRelativeTo(None)
            StockGlance2020_frame_.setVisible(True)

            if True or Platform.isOSX():
                # StockGlance2020_frame_.setAlwaysOnTop(True)
                StockGlance2020_frame_.toFront()

            return True


    # endclass

    # The javax.swing package and its subpackages provide a fairly comprehensive set of default renderer implementations, suitable for customization via inheritance. A notable omission is the lack #of a default renderer for a JTableHeader in the public API. The renderer used by default is a Sun proprietary class, sun.swing.table.DefaultTableCellHeaderRenderer, which cannot be extended.
    # DefaultTableHeaderCellRenderer seeks to fill this void, by providing a rendering designed to be identical with that of the proprietary class, with one difference: the vertical alignment of #the header text has been set to BOTTOM, to provide a better match between DefaultTableHeaderCellRenderer and other custom renderers.
    # The name of the class has been chosen considering this to be a default renderer for the cells of a table header, and not the table cells of a header as implied by the proprietary class name


    class DefaultTableHeaderCellRenderer(DefaultTableCellRenderer):

        # /**
        # * Constructs a <code>DefaultTableHeaderCellRenderer</code>.
        # * <P>
        # * The horizontal alignment and text position are set as appropriate to a
        # * table header cell, and the opaque property is set to false.
        # */

        def __init__(self):
            # super(DefaultTableHeaderCellRenderer, self).__init__()
            self.setHorizontalAlignment(JLabel.CENTER)  # This one changes the text alignment
            self.setHorizontalTextPosition(
                    JLabel.RIGHT)  # This positions the  text to the  left/right of  the sort icon
            self.setVerticalAlignment(JLabel.BOTTOM)
            self.setOpaque(True)  # if this is false then it hides the background colour

        # enddef

        # /**
        # * returns the default table header cell renderer.
        # * <P>
        # * If the column is sorted, the appropriate icon is retrieved from the
        # * current Look and Feel, and a border appropriate to a table header cell
        # * is applied.
        # * <P>
        # * Subclasses may overide this method to provide custom content or
        # * formatting.
        # *
        # * @param table the <code>JTable</code>.
        # * @param value the value to assign to the header cell
        # * @param isSelected This parameter is ignored.
        # * @param hasFocus This parameter is ignored.
        # * @param row This parameter is ignored.
        # * @param column the column of the header cell to render
        # * @return the default table header cell renderer
        # */

        # noinspection PyUnusedLocal
        def getTableCellRendererComponent(self, table, value, isSelected, hasFocus, row, column):
            super(DefaultTableHeaderCellRenderer, self).getTableCellRendererComponent(table, value, isSelected,hasFocus, row, column)    # noqa
            tableHeader = table.getTableHeader()
            # if (tableHeader is not None): self.setForeground(tableHeader.getForeground())
            align = firstRowTableCellRenderer = table.getCellRenderer(0, column).getHorizontalAlignment()
            self.setHorizontalAlignment(align)
            if align == JLabel.RIGHT:
                self.setHorizontalTextPosition(JLabel.RIGHT)
            elif align == JLabel.LEFT:
                self.setHorizontalTextPosition(JLabel.LEFT)
            elif align == JLabel.CENTER:
                self.setHorizontalTextPosition(JLabel.LEFT)

            self.setIcon(self._getIcon(table, column))
            self.setBorder(UIManager.getBorder("TableHeader.cellBorder"))

            self.setForeground(Color.BLACK)
            self.setBackground(Color.lightGray)

            # self.setHorizontalAlignment(JLabel.CENTER)

            return self

        # enddef

        # /**
        # * Overloaded to return an icon suitable to the primary sorted column, or null if
        # * the column is not the primary sort key.
        # *
        # * @param table the <code>JTable</code>.
        # * @param column the column index.
        # * @return the sort icon, or null if the column is unsorted.
        # */
        def _getIcon(self, table, column):
            sortKey = self.getSortKey(table, column)
            if (sortKey is not None and table.convertColumnIndexToView(sortKey.getColumn()) == column):
                x = (sortKey.getSortOrder())
                if x == SortOrder.ASCENDING:      return UIManager.getIcon("Table.ascendingSortIcon")
                elif x == SortOrder.DESCENDING:   return UIManager.getIcon("Table.descendingSortIcon")
                elif x == SortOrder.UNSORTED:     return UIManager.getIcon("Table.naturalSortIcon")
            return None

        # enddef

        # /**
        # * returns the current sort key, or null if the column is unsorted.
        # *
        # * @param table the table
        # * @param column the column index
        # * @return the SortKey, or null if the column is unsorted
        # */
        def getSortKey(self, table, column):                                                                    # noqa
            rowSorter = table.getRowSorter()
            if (rowSorter is None): return None
            sortedColumns = rowSorter.getSortKeys()
            if (sortedColumns.size() > 0): return sortedColumns.get(0)
            return None
        # enddef


    StockGlanceInstance = StockGlance2020()

    if StockGlance2020.createAndShowGUI(StockGlanceInstance):

        if not lDisplayOnly:
            def ExportDataToFile():
                global debug, StockGlance2020_frame_, rawDataTable, rawFooterTable, headingNames, csvfilename, decimalCharSep, groupingCharSep, csvDelimiter, version_build
                global lSplitSecuritiesByAccount, lExcludeTotalsFromCSV, myScriptName, lRoundPrice, lGlobalErrorDetected, lIncludeFutureBalances_SG2020
                global lWriteBOMToExportFile_SWSS

                global _SHRS_FORMATTED, _SHRS_RAW, _PRICE_FORMATTED, _PRICE_RAW, _CVALUE_FORMATTED, _CVALUE_RAW, _BVALUE_FORMATTED, _BVALUE_RAW, _SORT
                global _CBVALUE_FORMATTED, _CBVALUE_RAW, _GAIN_FORMATTED, _GAIN_RAW, _EXCLUDECSV, _GAINPCT

                myPrint("D","In ", inspect.currentframe().f_code.co_name, "()")

                # NOTE - You can add sep=; to beginning of file to tell Excel what delimiter you are using
                if not lSplitSecuritiesByAccount:
                    rawDataTable = sorted(rawDataTable, key=lambda x: (str(x[1]).upper()))

                rawDataTable.insert(0,headingNames)  # Insert Column Headings at top of list. A bit rough and ready, not great coding, but a short list...!

                for _i in range(0, len(rawFooterTable)):
                    rawDataTable.append(rawFooterTable[_i])

                # Write the csvlines to a file
                myPrint("B", "Opening file and writing ", len(rawDataTable), " records")

                try:
                    # CSV Writer will take care of special characters / delimiters within fields by wrapping in quotes that Excel will decode
                    with open(csvfilename,"wb") as csvfile:  # PY2.7 has no newline parameter so opening in binary; juse "w" and newline='' in PY3.0

                        if lWriteBOMToExportFile_SWSS:
                            csvfile.write(codecs.BOM_UTF8)   # This 'helps' Excel open file with double-click as UTF-8

                        writer = csv.writer(csvfile, dialect='excel', quoting=csv.QUOTE_MINIMAL, delimiter=fix_delimiter(csvDelimiter))

                        if csvDelimiter != ",":
                            writer.writerow(["sep=",""])  # Tells Excel to open file with the alternative delimiter (it will add the delimiter to this line)

                        writer.writerow(rawDataTable[0][:_SHRS_RAW])  # Print the header, but not the extra _field headings

                        for _i in range(1, len(rawDataTable)):
                            if not rawDataTable[_i][_EXCLUDECSV]:
                                # Write the table, but swap in the raw numbers (rather than formatted number strings)
                                writer.writerow([
                                        fixFormatsStr(rawDataTable[_i][0], False),
                                        fixFormatsStr(rawDataTable[_i][1], False),
                                        fixFormatsStr(rawDataTable[_i][_SHRS_RAW], True),
                                        fixFormatsStr(rawDataTable[_i][_PRICE_RAW], True),
                                        fixFormatsStr(rawDataTable[_i][4], False),
                                        fixFormatsStr(rawDataTable[_i][_CVALUE_RAW], True),
                                        fixFormatsStr(rawDataTable[_i][_BVALUE_RAW], True),
                                        fixFormatsStr(rawDataTable[_i][_CBVALUE_RAW], True),
                                        fixFormatsStr(rawDataTable[_i][_GAIN_RAW], True),
                                        fixFormatsStr(rawDataTable[_i][_GAINPCT], True, "%"),
                                        fixFormatsStr(rawDataTable[_i][10], False),
                                        ""])
                            # ENDIF
                        # NEXT
                        today = Calendar.getInstance()
                        writer.writerow([""])
                        writer.writerow(["StuWareSoftSystems - " + myScriptName + "(build: "
                                         + version_build
                                         + ")  MoneyDance Python Script - Date of Extract: "
                                         + str(sdf.format(today.getTime()))])

                        writer.writerow([""])
                        writer.writerow(["User Parameters..."])

                        writer.writerow(["Hiding Hidden Securities...: %s" %(hideHiddenSecurities)])
                        writer.writerow(["Hiding Inactive Accounts...: %s" %(hideInactiveAccounts)])
                        writer.writerow(["Hiding Hidden Accounts.....: %s" %(hideHiddenAccounts)])
                        writer.writerow(["Security filter............: %s '%s'" %(lAllSecurity,filterForSecurity)])
                        writer.writerow(["Account filter.............: %s '%s'" %(lAllAccounts,filterForAccounts)])
                        writer.writerow(["Currency filter............: %s '%s'" %(lAllCurrency,filterForCurrency)])
                        writer.writerow(["Include Cash Balances......: %s" %(lIncludeCashBalances)])
                        writer.writerow(["Include Future Balances....: %s" %(lIncludeFutureBalances_SG2020)])
                        writer.writerow(["Default Price Rounding.....: %s" %(lRoundPrice)])
                        writer.writerow(["Split Securities by Account: %s" %(lSplitSecuritiesByAccount)])
                        writer.writerow(["Extract Totals from CSV....: %s" %(lExcludeTotalsFromCSV)])

                    myPrint("B", "CSV file " + csvfilename + " created, records written, and file closed..")

                except IOError, e:
                    lGlobalErrorDetected = True
                    myPrint("B", "Oh no - File IO Error!", e)
                    myPrint("B", "Path:", csvfilename)
                    myPrint("B", "!!! ERROR - No file written - sorry! (was file open, permissions etc?)".upper())
                    dump_sys_error_to_md_console_and_errorlog()
                    myPopupInformationBox(StockGlance2020_frame_,"Sorry - error writing to export file!", "FILE EXTRACT")
            # enddef

            def fixFormatsStr(theString, lNumber, sFormat=""):
                global lStripASCII

                if lNumber is None: lNumber = False
                if theString is None: theString = ""

                if sFormat == "%" and theString != "":
                    theString = "{:.1%}".format(theString)
                    return theString

                if lNumber: return str(theString)

                theString = theString.strip()  # remove leading and trailing spaces

                if theString[:3] == "===": theString = " " + theString  # Small fix as Libre Office doesn't like "=======" (it thinks it's a formula)

                theString = theString.replace("\n", "*")  # remove newlines within fields to keep csv format happy
                theString = theString.replace("\t", "*")  # remove tabs within fields to keep csv format happy

                if lStripASCII:
                    all_ASCII = ''.join(char for char in theString if
                                        ord(char) < 128)  # Eliminate non ASCII printable Chars too....
                else:
                    all_ASCII = theString
                return all_ASCII
            # enddef

            ExportDataToFile()
            if not lGlobalErrorDetected:
                myPopupInformationBox(StockGlance2020_frame_,"Your extract has been created as requested",myScriptName)

else:
    pass

if StockGlance2020_fake_frame_:
    StockGlance2020_fake_frame_.dispose()
    del StockGlance2020_fake_frame_

myPrint("B", "StuWareSoftSystems - %s script ending......" %myScriptName)

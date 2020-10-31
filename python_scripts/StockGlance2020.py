#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# StockGlance2020 v5a - October 2020 - Stuart Beesley

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
#  - This script basically shows all stocks/funds summarised into single stocks/funds per row. I.E. consolidates data accross all Accounts
#  - Some of the code looks somewhat different to how I would write native Python, but it is as it is as it was converted from pure Java by waynelloydsmith
#  - Shows QTY of shares
#  - If you are running Windows and get file IO errors (e.g. 13) creating the extract, you likely have a permissions issue. Try a different location (e.g. your standard user directory)
#  - Removed all non-functional Java / Python code and general tidy up.
#  - Also fixed / replaced the JY/Java code to make JTable and the Scrollpanes funtion properly
#  - Addressed bug hiding some securitys when not all prices found (by date) - by eliminating % as not needed anyway.
#  - Price is taken from Current Price now, and NOT from price history. If you would like price history, let me know!
#  - Added Parameter/filter screen/options and export to file....
#  - The file will write a utf8 encoded file - so we strip out currency signs - else Excel treats them wrongly. You can specify to leave them included...
# -- We strip out all non ASCII characters below code 128 and also number seperators. Delimiter will flip to a semi-colon if your decimal point is a comma!
# -- USAGE: Just execute and a popup will ask you to set parameters. You can just leave all as default if you wish.
# --        Change the defaults in the rows just below this statement...
# -- WARNING: Cash Balances are per account, not per security/currency.
# --          So the cash balaces will always be for the whole account(s) included, not just  filtered securities etc...
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
# -- V4e - Added MD Costbasis and the Unrealised Gain (calculated); also now save export path to disk
# -- V4e - Added trap for file write errors; added parameter to allow user to exclude totals from csv file; cleaned up row highlighting and cell neg colours
# -- V4f - Added file permissions check; added code to display file to stdout if file error. Allows user to copy / paste into Excel...
# -- V4g - Added % to gain calculation (user request); changed default extract location (search for User Home) to avoid internal MD locations
# -- V4g - re-added UTF8 coding; tinkered with display formatting (bold rows); enabled scrolling on footer table (totals) (user request); allow footer to gain focus and CRTL-C (copy)
# -- V4h - format CSV Gain% field as a %string; fixed Gain% on the final total row...
# -- V5 -  Released version (from v4h)
# -- V5a - Some users report a problem saving files to some folders on Windows 10. It seems that Anti-malware or Windows Access Control is restrictiing access
# --       So, changed to FileDialog (from JFileChooser) for Windows as this seems to tell Windows to allow access.
# --       Added some console messages; fixed crash when no investment accounts exist.

import sys

reload(sys)  # Dirty hack to eliminate UTF-8 coding errors
sys.setdefaultencoding('utf8')  # Dirty hack to eliminate UTF-8 coding errors
import platform

import datetime

from com.infinitekind.moneydance.model import *
from com.infinitekind.moneydance.model.Account import AccountType
from com.infinitekind.moneydance.model import AccountUtil, AcctFilter, CurrencyType, LocalStorage, InvestUtil
from com.moneydance.util import Platform

from com.infinitekind.util import DateUtil

from java.awt import *
from java.awt import BorderLayout, Color, Dimension, GridLayout, Toolkit, Component, FileDialog

from java.awt.event import WindowAdapter, AdjustmentListener
from java.awt import Font

from java.text import *
from java.text import NumberFormat, SimpleDateFormat, DecimalFormat

from java.util import *
from java.util import Arrays, Calendar, Comparator, Date
from java.util.List import *

from javax.swing import JScrollPane, WindowConstants, JFrame, JLabel, JPanel, JTable, JComponent, KeyStroke, \
    AbstractAction, SwingConstants
from javax.swing import JOptionPane, JFileChooser, JTextField
from javax.swing import Icon, RowSorter, UIManager, SortOrder

from javax.swing.RowSorter import SortKey
from javax.swing.border import CompoundBorder, EmptyBorder, MatteBorder
from javax.swing.table import DefaultTableCellRenderer, DefaultTableModel, TableModel, TableRowSorter
from javax.swing.text import PlainDocument
from javax.swing.event import TableColumnModelListener
import javax.swing.filechooser.FileNameExtensionFilter

import java.lang
from java.lang import System, Double, Math

import time

import os
import os.path

import java.io.File
from java.io import FileNotFoundException, FilenameFilter
from org.python.core.util import FileUtil

import inspect

import csv

import pickle

# StuWareSoftSystems common Globals
global debug  # Set to True if you want verbose messages, else set to False....
global hideHiddenSecurities, hideInactiveAccounts, hideHiddenAccounts, lAllCurrency, filterForCurrency, lAllSecurity, filterForSecurity, lAllAccounts, filterForAccounts, lIncludeCashBalances, lStripASCII, csvDelimiter
global lUseMacFileChooser, lIamAMac
global csvfilename, version, scriptpath, lDisplayOnly, myScriptName
global decimalCharSep, groupingCharSep, myParameters, _resetParameters

# This program's Globals
global baseCurrency, sdf, frame_, rawDataTable, rawFooterTable, headingNames
global StockGlanceInstance  # holds the instance of StockGlance2020()
global _SHRS_FORMATTED, _SHRS_RAW, _PRICE_FORMATTED, _PRICE_RAW, _CVALUE_FORMATTED, _CVALUE_RAW, _BVALUE_FORMATTED, _BVALUE_RAW
global _CBVALUE_FORMATTED, _CBVALUE_RAW, _GAIN_FORMATTED, _GAIN_RAW, _SORT, _EXCLUDECSV, _GAINPCT
global lSplitSecuritiesByAccount, acctSeperator, lExcludeTotalsFromCSV

version = "5a"

# Set programmatic defaults/parameters for filters HERE.... Saved Parameters will override these now
# NOTE: You  can override in the pop-up screen
hideHiddenSecurities = True
hideInactiveAccounts = True
hideHiddenAccounts = True
lAllCurrency = True
filterForCurrency = "ALL"
lAllSecurity = True
filterForSecurity = "ALL"
lAllAccounts = True
filterForAccounts = "ALL"
lIncludeCashBalances = False
lSplitSecuritiesByAccount = False
lExcludeTotalsFromCSV = False
lStripASCII = True
csvDelimiter = ","
debug = False
lUseMacFileChooser = True  # This will be ignored if you don't choose option to export to  a file
_resetParameters = False  # set this to True to prevent loading parameters from disk and use the defaults above...

lIamAMac = False
myParameters = {}

headingNames = ""
acctSeperator = ' : '
scriptpath = ""


myScriptName = os.path.basename(__file__)
if myScriptName.endswith(".py"):
    myScriptName = myScriptName[:-3]

def myPrint(where, *args):  # P=Display on Python Console, J=Display on MD (Java) Console Error Log, B=Both
    global myScriptName
    printString = ""
    for what in args:
        printString += str(what)
    if where == "P" or where == "B": print printString
    if where == "J" or where == "B": System.err.write(myScriptName+": "+printString+"\n")

myPrint("B", "StuWareSoftSystems...")
myPrint("B", os.path.basename(__file__),": Python Script Initialising.......", "Version:", version)


def getParameters():
    global debug  # Set to True if you want verbose messages, else set to False....
    global hideHiddenSecurities, hideInactiveAccounts, hideHiddenAccounts, lAllCurrency, filterForCurrency
    global lAllSecurity, filterForSecurity, lAllAccounts, filterForAccounts, lIncludeCashBalances, lStripASCII, csvDelimiter, scriptpath
    global lSplitSecuritiesByAccount, lExcludeTotalsFromCSV
    global lUseMacFileChooser, myParameters

    if debug: print "In ", inspect.currentframe().f_code.co_name, "()"

    dict_filename = os.path.join("..", "StuWareSoftSystems.dict")
    if debug: print "Now checking for parameter file:", dict_filename

    local_storage = moneydance.getCurrentAccountBook().getLocalStorage()
    if local_storage.exists(dict_filename):
        __StockGlance2020 = None

        myPrint("J","loading parameters from Pickle file:", dict_filename)
        if debug: print "Parameter file", dict_filename, "exists.."
        # Open the file
        try:
            istr = local_storage.openFileForReading(dict_filename)
            load_file = FileUtil.wrap(istr)
            myParameters = pickle.load(load_file)
            load_file.close()
        except FileNotFoundException as e:
            print "Error: failed to find parameter file..."
            myParameters = None
        except EOFError as e:
            print "Error: reached EOF on parameter file...."
            myParameters = None

        if myParameters is None:
            if debug: print "Parameters did not load, will keep defaults.."
            return
        else:
            if debug: print "Parameters successfully loaded from file..."
    else:
        if debug: print "Parameter file does not exist.. Will use defaults.."
        return

    if debug:
        print "myParameters read from file contains...:"
        for key in sorted(myParameters.keys()):
            print "...variable:", key, myParameters[key]

    if myParameters.get("__StockGlance2020") is not None: __StockGlance2020 = myParameters.get("__StockGlance2020")
    if myParameters.get("hideHiddenSecurities") is not None: hideHiddenSecurities = myParameters.get(
        "hideHiddenSecurities")
    if myParameters.get("hideInactiveAccounts") is not None: hideInactiveAccounts = myParameters.get(
        "hideInactiveAccounts")
    if myParameters.get("hideHiddenAccounts") is not None: hideHiddenAccounts = myParameters.get("hideHiddenAccounts")
    if myParameters.get("lAllCurrency") is not None: lAllCurrency = myParameters.get("lAllCurrency")
    if myParameters.get("filterForCurrency") is not None: filterForCurrency = myParameters.get("filterForCurrency")
    if myParameters.get("lAllSecurity") is not None: lAllSecurity = myParameters.get("lAllSecurity")
    if myParameters.get("filterForSecurity") is not None: filterForSecurity = myParameters.get("filterForSecurity")
    if myParameters.get("lAllAccounts") is not None: lAllAccounts = myParameters.get("lAllAccounts")
    if myParameters.get("filterForAccounts") is not None: filterForAccounts = myParameters.get("filterForAccounts")
    if myParameters.get("lIncludeCashBalances") is not None: lIncludeCashBalances = myParameters.get(
        "lIncludeCashBalances")
    if myParameters.get("lSplitSecuritiesByAccount") is not None: lSplitSecuritiesByAccount = myParameters.get(
        "lSplitSecuritiesByAccount")
    if myParameters.get("lExcludeTotalsFromCSV") is not None: lExcludeTotalsFromCSV = myParameters.get(
        "lExcludeTotalsFromCSV")
    if myParameters.get("lStripASCII") is not None: lStripASCII = myParameters.get("lStripASCII")
    if myParameters.get("csvDelimiter") is not None: csvDelimiter = myParameters.get("csvDelimiter")
    if myParameters.get("debug") is not None: debug = myParameters.get("debug")
    if myParameters.get("lUseMacFileChooser") is not None: lUseMacFileChooser = myParameters.get("lUseMacFileChooser")

    if myParameters.get("scriptpath") is not None:
        scriptpath = myParameters.get("scriptpath")
        if not os.path.isdir(scriptpath):
            print "Warning: loaded parameter scriptpath does not appear to be a valid directory:", scriptpath, "will ignore"
            scriptpath = ""

    if debug: print "Parameter file loaded if present and parameters set into memory....."


# ENDDEF

if not _resetParameters:
    getParameters()
else:
    print "User has specified to reset parameters... keeping defaults and skipping pickle()"

if debug: myPrint("B","DEBUG IS ON..")

def MDDiag():
    global debug
    if debug: print "MoneyDance Build:", moneydance.getVersion(), "Build:", moneydance.getBuild()


MDDiag()

if debug: print "System file encoding is:", sys.getfilesystemencoding()  # Not used, but interesting. Perhaps useful when switching between Windows/Macs and writing files...


def checkVersions():
    global debug

    lError = False
    plat_j = platform.system()
    plat_p = platform.python_implementation()
    python_maj = sys.version_info.major
    python_min = sys.version_info.minor

    if debug: print "Platform:", plat_p, plat_j, python_maj, ".", python_min
    if debug: print sys.version

    if plat_p != "Jython":
        lError = True
        print "Error: Script requires Jython"
    if plat_j != "Java":
        lError = True
        print "Error: Script requires Java  base"
    if (python_maj != 2 or python_min != 7):
        lError = True
        print "\n\nError: Script was  designed on version 2.7. By all means bypass this test and see what happens....."

    if lError:
        print "\n@@@ TERMINATING PROGRAM @@@\n"
        # raise

    return not lError


# enddef

if checkVersions():
    def who_am_i():
        try:
            username = System.getProperty("user.name")
        except:
            username = "???"

        return username


    if debug: print "I am user:", who_am_i()


    def getHomeDir():
        # Yup - this can be all over the place...
        print 'System.getProperty("user.dir")', System.getProperty("user.dir")
        print 'System.getProperty("UserHome")', System.getProperty("UserHome")
        print 'System.getProperty("user.home")', System.getProperty("user.home")
        print 'os.path.expanduser("~")', os.path.expanduser("~")
        print 'os.environ.get("HOMEPATH")', os.environ.get("HOMEPATH")
        return


    if debug: getHomeDir()


    def amIaMac():
        myPlat = System.getProperty("os.name")
        if myPlat is None: return False
        if debug: print "Platform:", myPlat
        if debug: print "OS Version:", System.getProperty("os.version")
        return myPlat == "Mac OS X"


    # enddef

    lIamAMac = amIaMac()
    if not lIamAMac: lUseMacFileChooser = False


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

        if debug: print "Home Directory selected...:", homeDir
        if homeDir is None: return ""
        return homeDir


    csvfilename = None


    def getDecimalPoint(lGetPoint=False, lGetGrouping=False):
        global debug
        decimalFormat = DecimalFormat.getInstance()
        decimalSymbols = decimalFormat.getDecimalFormatSymbols()

        if not lGetGrouping: lGetPoint = True
        if lGetGrouping and lGetPoint: return "error"

        if lGetPoint:
            decimalCharSep = decimalSymbols.getDecimalSeparator()
            if debug: print "Decimal Point Character:", decimalCharSep
            return decimalCharSep

        if lGetGrouping:
            groupingCharSep = decimalSymbols.getGroupingSeparator()
            if debug: print "Grouping Seperator Character:", groupingCharSep
            return groupingCharSep

        return "error"


    decimalCharSep = getDecimalPoint(lGetPoint=True)
    groupingCharSep = getDecimalPoint(lGetGrouping=True)
    if decimalCharSep != "." and csvDelimiter == ",": csvDelimiter = ";"  # Override for EU countries or where decimal point is actually a comma...
    if debug: print "Decimal point:", decimalCharSep, "Grouping Seperator", groupingCharSep, "CSV Delimiter set to:", csvDelimiter


    def check_file_writable(fnm):
        if debug: print "In ", inspect.currentframe().f_code.co_name, "()"
        if debug: print "Checking path:", fnm

        if os.path.exists(fnm):
            if debug: print "path exists.."
            # path exists
            if os.path.isfile(fnm):  # is it a file or a dir?
                if debug: print "path is a file.."
                # also works when file is a link and the target is writable
                return os.access(fnm, os.W_OK)
            else:
                if debug: print "path is not a file.."
                return False  # path is a dir, so cannot write as a file
        # target does not exist, check perms on parent dir
        if debug: print "path does not exist..."
        pdir = os.path.dirname(fnm)
        if not pdir: pdir = '.'
        # target is creatable if parent dir is writable
        return os.access(pdir, os.W_OK)


    # Stores  the data table for export
    rawDataTable = None
    rawrawFooterTable = None

    sdf = SimpleDateFormat("dd/MM/yyyy")


    # This allows me to filter inputs to Y/N and convert to uppercase - single digit responses..... (took hours to work out, but now I have it!)
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
            if (self.what == "YN" and (myString in "YN")) or (self.what == "DELIM" and (myString in ";|,")) or (
                    self.what == "CURR"):
                if ((self.getLength() + len(myString)) <= self.limit):
                    super(JTextFieldLimitYN, self).insertString(myOffset, myString, myAttr)


    # endclass

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

    label7c = JLabel("Exclude Totals from CSV extract (helps pivots)? (Y/N):")
    user_excludeTotalsFromCSV = JTextField(2)
    user_excludeTotalsFromCSV.setDocument(JTextFieldLimitYN(1, True, "YN"))
    if lExcludeTotalsFromCSV:       user_excludeTotalsFromCSV.setText("Y")
    else:                           user_excludeTotalsFromCSV.setText("N")

    label8 = JLabel("Strip non ASCII characters from CSV export? (Y/N)")
    user_selectStripASCII = JTextField(12)
    user_selectStripASCII.setDocument(JTextFieldLimitYN(1, True, "YN"))
    if lStripASCII: user_selectStripASCII.setText("Y")
    else:               user_selectStripASCII.setText("N")

    label9 = JLabel("Change CSV Export Delimiter from default to: ';|,'")
    user_selectDELIMITER = JTextField(2)
    user_selectDELIMITER.setDocument(JTextFieldLimitYN(1, True, "DELIM"))
    user_selectDELIMITER.setText(csvDelimiter)

    label10 = JLabel("Turn DEBUG Verbose messages on? (Y/N)")
    user_selectDEBUG = JTextField(2)
    user_selectDEBUG.setDocument(JTextFieldLimitYN(1, True, "YN"))
    if debug:  user_selectDEBUG.setText("Y")
    else:           user_selectDEBUG.setText("N")

    if lIamAMac:
        label11 = JLabel("Use Mac-like GUI for export filename selection? (Y/N)")
        user_selectMacFileChooser = JTextField(2)
        user_selectMacFileChooser.setDocument(JTextFieldLimitYN(1, True, "YN"))
        if lUseMacFileChooser:  user_selectMacFileChooser.setText("Y")
        else:                        user_selectMacFileChooser.setText("N")

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
    userFilters.add(user_selectCashBalances)
    userFilters.add(label7b)
    userFilters.add(user_splitSecurities)
    userFilters.add(label7c)
    userFilters.add(user_excludeTotalsFromCSV)
    userFilters.add(label8)
    userFilters.add(user_selectStripASCII)
    userFilters.add(label9)
    userFilters.add(user_selectDELIMITER)
    userFilters.add(label10)
    userFilters.add(user_selectDEBUG)
    if lIamAMac:
        userFilters.add(label11)
        userFilters.add(user_selectMacFileChooser)

    lExit = False
    lDisplayOnly = False

    options = ["Abort", "Display & CSV Export", "Display Only"]
    userAction = (
            JOptionPane.showOptionDialog(None, userFilters, "(" + version + ") Set Script Parameters....",
                                         JOptionPane.OK_CANCEL_OPTION,
                                         JOptionPane.QUESTION_MESSAGE, None, options, options[2]))
    if userAction == 1:  # Display & Export
        if debug: print "Display and export choosen"
        lDisplayOnly = False
    elif userAction == 2:  # Display Only
        lDisplayOnly = True
        if debug: print "Display only with no export chosen"
    else:
        # Abort
        print "User Cancelled Parameter selection.. Will abort.."
        lDisplayOnly = False
        lExit = True

    if not lExit:
        if debug:
            print "Parameters Captured", "Sec: ", user_hideHiddenSecurities.getText(), \
                "InActAct:", user_hideInactiveAccounts.getText(), \
                "HidAct:", user_hideHiddenAccounts.getText(), \
                "Curr:", user_selectCurrency.getText(), \
                "Ticker:", user_selectTicker.getText(), \
                "Filter Accts:", user_selectAccounts.getText(), \
                "Include Cash Balances:", user_selectCashBalances.getText(), \
                "Split Securities:", user_splitSecurities.getText(), \
                "Exclude Totals from CSV:", user_excludeTotalsFromCSV.getText(), \
                "Strip ASCII:", user_selectStripASCII.getText(), \
                "Verbose Debug Messages: ", user_selectDEBUG.getText(), \
                "CSV File Delimiter:", user_selectDELIMITER.getText()
            if lIamAMac: print "Use Mac-like Filename GUI:", user_selectMacFileChooser.getText()
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

        if user_selectCashBalances.getText() == "Y":    lIncludeCashBalances = True
        else:                                           lIncludeCashBalances = False

        if user_splitSecurities.getText() == "Y":       lSplitSecuritiesByAccount = True
        else:                                           lSplitSecuritiesByAccount = False

        if user_excludeTotalsFromCSV.getText() == "Y":  lExcludeTotalsFromCSV = True
        else:                                           lExcludeTotalsFromCSV = False

        if user_selectStripASCII.getText() == "Y":      lStripASCII = True
        else:                                           lStripASCII = False

        csvDelimiter = user_selectDELIMITER.getText()
        if csvDelimiter == "" or (not (csvDelimiter in ";|,")):
            print "Invalid Delimiter:", csvDelimiter, "selected. Overriding with:','"
            csvDelimiter = ","
        if decimalCharSep == csvDelimiter:
            print "WARNING: The CSV file delimiter:", csvDelimiter, "cannot be the same as your decimal point character:", decimalCharSep, " - Proceeding without file export!!"
            lDisplayOnly = True

        if user_selectDEBUG.getText() == "Y":   debug = True
        else:
            debug = False
        if debug: print "DEBUG turned on"

        if lIamAMac:
            if user_selectMacFileChooser.getText() == "Y":   lUseMacFileChooser = True
            else:                                            lUseMacFileChooser = False

        print "User Parameters..."
        if hideHiddenSecurities:
            print "Hiding Hidden Securities..."
        else:
            print "Including Hidden Securities..."
        if hideInactiveAccounts:
            print "Hiding Inactive Accounts..."
        else:
            print "Including Inactive Accounts..."

        if hideHiddenAccounts:
            print "Hiding Hidden Accounts..."
        else:
            print "Including Hidden Accounts..."

        if lAllCurrency:
            print "Selecting ALL Currencies..."
        else:
            print "Filtering for Currency containing: ", filterForCurrency

        if lAllSecurity:
            print "Selecting ALL Securities..."
        else:
            print "Filtering for Security/Ticker containing: ", filterForSecurity

        if lAllAccounts:
            print "Selecting ALL Accounts..."
        else:
            print "Filtering for Accounts containing: ", filterForAccounts

        if lIncludeCashBalances:
            print "Including Cash Balances - WARNING - this is per account!"
        else:
            print "Excluding Cash Balances"

        if lSplitSecuritiesByAccount:
            print "Splitting Securities by account - WARNING, this will disable sorting...."

        # Now get the export filename
        csvfilename = None

        if not lDisplayOnly:  # i.e. we have asked for a file export - so get the filename

            if lIamAMac:
                if lUseMacFileChooser:
                    if debug: print "I am a Mac. FileDialog Mac-like filename GUI choosen"
                else:
                    print "I am a Mac, but you requested to use older non-Mac GUI JFileChooser.."

            if lStripASCII:
                print "Will strip non-ASCII characters - e.g. Currency symbols from output file...", " Using Delimiter:", csvDelimiter
            else:
                print "Non-ASCII characters will not be stripped from file: ", " Using Delimiter:", csvDelimiter

            if lExcludeTotalsFromCSV:
                print "Will exclude Totals from CSV to assist Pivot tables"


            class ExtFilenameFilter(FilenameFilter):
                ext = ""

                def __init__(self, ext):
                    self.ext = "." + ext.upper()
                    # super(FilenameFilter, self).__init__()

                def accept(self, dir, filename):
                    if filename is not None and filename.upper().endswith(self.ext):
                        return True
                    return False


            # ENDCLASS

            def grabTheFile():
                global debug, lDisplayOnly, csvfilename, lIamAMac, lUseMacFileChooser, scriptpath, myScriptName
                if debug: print "In ", inspect.currentframe().f_code.co_name, "()"

                if scriptpath == "" or scriptpath is None:  # No parameter saved / loaded from disk
                    scriptpath = myDir()

                if debug: print "Default file export output path is....:", scriptpath

                csvfilename = ""
                if True or lIamAMac and lUseMacFileChooser:
                    if lIamAMac:
                        if debug: print "MacOS X detected: Therefore I will run FileDialog with no extension filters to get filename...."
                        # jFileChooser hangs on Mac when using file extension filters, also looks rubbish. So using Mac(ish)GUI

                        System.setProperty("com.apple.macos.use-file-dialog-packages",
                                           "true")  # In theory prevents access to app file structure (but doesnt seem to work)
                        System.setProperty("apple.awt.fileDialogForDirectories", "false")

                    filename = FileDialog(None, "Select/Create CSV file for Stock Balances extract (CANCEL=NO EXPORT)")
                    filename.setMultipleMode(False)
                    filename.setMode(FileDialog.SAVE)
                    filename.setFile('extract_stock_balances.csv')
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
                        print "User chose to cancel or no file selected >>  So no Extract will be performed... "
                    elif str(csvfilename).endswith(".moneydance"):
                        print "User selected file:", csvfilename
                        print "Sorry - User chose to use .moneydance extension - I will not allow it!... So no Extract will be performed..."
                        lDisplayOnly = True
                        csvfilename = None
                    elif ".moneydance" in filename.getDirectory():
                        print "User selected file:", filename.getDirectory(), csvfilename
                        print "Sorry - FileDialog() User chose to save file in .moneydance location. NOT Good practice so I will not allow it!... So no Extract will be performed..."
                        lDisplayOnly = True
                        csvfilename = None
                    else:
                        csvfilename = str(java.io.File(
                                filename.getDirectory() + os.path.sep + filename.getFile()))  # NOTE: FileDialog checks for file overwrite and seeks confirmation....
                        scriptpath = str(filename.getDirectory())

                    if not lDisplayOnly:
                        if os.path.exists(csvfilename) and os.path.isfile(
                                csvfilename): print "WARNING: file exists,but assuming user said OK to overwrite.."
                else:
                    if debug:
                        if lIamAMac:
                            print "Mac platform detected, but user specified to run JFileChooser()  to get filename...."
                        else:
                            print "Non Mac platform detected: Therefore I will run JFileChooser()  to get filename...."
                    filename = JFileChooser(scriptpath)

                    filename.setSelectedFile(java.io.File(scriptpath + os.path.sep + 'extract_stock_balances.csv'))
                    extfilter = javax.swing.filechooser.FileNameExtensionFilter("CSV file (CSV,TXT)", ["csv", "TXT"])

                    filename.setMultiSelectionEnabled(False)

                    if not lIamAMac:
                        # this locks up Macs
                        filename.setFileFilter(extfilter)

                    filename.setDialogTitle("Select/Create CSV file for Stock Balances extract (CANCEL=NO EXPORT)")
                    filename.setPreferredSize(Dimension(800, 800))
                    returnvalue = filename.showDialog(None, "Extract")

                    if returnvalue == JFileChooser.CANCEL_OPTION:
                        lDisplayOnly = True
                        csvfilename = None
                        print "User chose to cancel = So no Extract will be performed... "
                    elif filename.selectedFile == None:
                        lDisplayOnly = True
                        csvfilename = None
                        print "User chose no filename... So no Extract will be performed..."
                    elif str(filename.selectedFile).endswith(".moneydance"):
                        lDisplayOnly = True
                        csvfilename = None
                        print "User selected file:", str(filename.selectedFile)
                        print "Sorry - JFileChooser() User chose to use .moneydance extension - I will not allow it!... So no Extract will be performed..."
                    elif ".moneydance" in str(filename.selectedFile):
                        lDisplayOnly = True
                        csvfilename = None
                        print "User selected file:", str(filename.selectedFile)
                        print "Sorry - User chose to save file in .moneydance location. NOT Good practice so I will not allow it!... So no Extract will be performed..."
                    else:
                        csvfilename = str(filename.selectedFile)

                        if os.path.exists(csvfilename) and os.path.isfile(csvfilename):
                            # Uh-oh file exists - overwrite?
                            print "File already exists... Confirm..."
                            if (JOptionPane.showConfirmDialog(None, "File '" + os.path.basename(
                                    csvfilename) + "' exists... Press YES to overwrite and proceed, NO to continue with no Extract?",
                                                              "WARNING", JOptionPane.YES_NO_OPTION,
                                                              JOptionPane.WARNING_MESSAGE) == JOptionPane.YES_OPTION):
                                print "User agreed to overwrite file..."
                            else:
                                lDisplayOnly = True
                                csvfilename = None
                                print "User does not want to overwrite file... Proceeding without Extract..."
                            # endif
                        # endif
                    # endif

                # endif

                if not lDisplayOnly:
                    if check_file_writable(csvfilename):
                        print 'Will display Stock balances and then extract to file: ', csvfilename, "(NOTE: Should drop non utf8 characters...)"
                        scriptpath = os.path.dirname(csvfilename)
                    else:
                        print "Sorry - I just checked and you do not have permissions to create this file:", csvfilename
                        print "I will display the file to screen so you can copy/paste into Excel...!"
                        myPrint("J","Error - file is not writable...: ", csvfilename)
                        # csvfilename=""
                        # lDisplayOnly = True

                if "filename" in vars() or "filename" in globals():   del filename
                if "extfilter" in vars() or "extfilter" in globals():   del extfilter

                return


            # enddef

            if not lDisplayOnly: grabTheFile()
        else:
            pass
        # endif

        if csvfilename is None:
            lDisplayOnly = True
            print "No Export will be performed"


        class StockGlance2020():  # MAIN program....
            global debug, hideHiddenSecurities, hideInactiveAccounts, lSplitSecuritiesByAccount, acctSeperator
            global rawDataTable, rawFooterTable, headingNames
            global _SHRS_FORMATTED, _SHRS_RAW, _PRICE_FORMATTED, _PRICE_RAW, _CVALUE_FORMATTED, _CVALUE_RAW, _BVALUE_FORMATTED, _BVALUE_RAW, _SORT
            global _CBVALUE_FORMATTED, _CBVALUE_RAW, _GAIN_FORMATTED, _GAIN_RAW, _EXCLUDECSV, _GAINPCT

            if debug: print "In ", inspect.currentframe().f_code.co_name, "()"

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

            rawFooterTable = []  # one row of footer data
            rawDataTable = []  # the data retrieved from moneydance

            #  Per column metadata - fields 10 - 16 not actually used but contain the raw numbers from fields 2,3,5,6 + sortfield
            columnNames = ["Symbol", "Stock", "Shares/Units", "Price", "Curr", "Curr Value", "Base Value", "Cost Basis",
                           "UnRlsd Gain", "Gain%", "Accounts",
                           "_Shrs", "_Price", "_CValue", "_BValue", "_CBValue", "_Gain", "_SORT", "_Exclude"]
            columnTypes = ["Text", "Text", "TextNumber", "TextNumber", "TextC", "TextNumber", "TextNumber",
                           "TextNumber", "TextNumber", "%", "Text", "N",
                           "N", "N", "N", "N", "N", "N", "TEXT"]
            headingNames = columnNames
            _SHRS_FORMATTED = 2
            _SHRS_RAW = 11
            _PRICE_FORMATTED = 3
            _PRICE_RAW = 12
            _CVALUE_FORMATTED = 5
            _CVALUE_RAW = 13
            _BVALUE_FORMATTED = 6
            _BVALUE_RAW = 14
            _CBVALUE_FORMATTED = 7
            _CBVALUE_RAW = 15
            _GAIN_FORMATTED = 8
            _GAIN_RAW = 16
            _GAINPCT = 9
            _SORT = 17
            _EXCLUDECSV = 18

            def getTableModel(self, book):
                global debug, baseCurrency, rawDataTable, lAllCurrency, filterForCurrency, lAllSecurity, filterForSecurity
                if debug: print "In ", inspect.currentframe().f_code.co_name, "()"
                if debug: print "MD Book: ", book

                ct = book.getCurrencies()

                baseCurrency = moneydance.getCurrentAccountBook().getCurrencies().getBaseType()
                if debug: print "Base Currency: ", baseCurrency.getIDString(), " : ", baseCurrency.getName()

                allCurrencies = ct.getAllCurrencies()
                if debug: print "getAllCurrencies(): ", allCurrencies

                rawDataTable = []
                today = Calendar.getInstance()
                if debug: print "Running today: ", sdf.format(today.getTime())

                self.sumInfoBySecurity(
                    book)  # Creates Dict(hashmap) QtyOfSharesTable, AccountsTable, CashTable : <CurrencyType, Long>  contains no account info

                if debug:
                    print "Result of sumInfoBySecurity(book) self.QtyOfSharesTable: \t", self.QtyOfSharesTable
                    print "Result of sumInfoBySecurity(book) self.AccountsTable: \t", self.AccountsTable
                    print "Result of sumInfoBySecurity(book) self.CashBalancesTable: \t", self.CashBalancesTable
                    print "Result of sumInfoBySecurity(book) self.CostBasisTotals: \t", self.CostBasisTotals

                if len(self.QtyOfSharesTable) < 1:
                    print "Sorry - you have no shares - exiting..."
                    return None

                self.totalBalance = 0.0
                self.totalBalanceBase = 0.0
                self.totalCashBalanceBase = 0.0
                self.totalCostBasisBase = 0.0
                self.totalGainBase = 0.0

                self.lRemoveCurrColumn = True

                if debug: print "Now processing all securities (currencies) and building my own table of results to build GUI...."
                for curr in allCurrencies:
                    if ((hideHiddenSecurities and not curr.getHideInUI()) or (
                            not hideHiddenSecurities)) and curr.getCurrencyType() == CurrencyType.Type.SECURITY:
                        # NOTE: (1.0 / .getRelativeRate() ) gives you the 'Current Price' from the History Screen
                        # NOTE: .getPrice(None) gives you the Current Price relative to the current Base to Security Currency.. So Base>Currency rate * .getRate(None) also gives Current Price

                        roundPrice = curr.getDecimalPlaces()
                        price = round(
                                1.0 / curr.adjustRateForSplitsInt(DateUtil.convertCalToInt(today),
                                                                  curr.getRelativeRate()),
                                roundPrice)

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
                                    if debug: print "Found Security..: ", curr, curr.getTickerSymbol(), " Curr: ", curr.getRelativeCurrency().getIDString(), " Price: ", price, " Qty: ", curr.formatSemiFancy(
                                            qty, decimalCharSep)

                                    securityCostBasis = self.CostBasisTotals.get(curr)

                                    # This new loop in version v4b does the account split within Securities (a bit of a retrofit hack)
                                    split_acct_array = self.AccountsTable.get(curr)

                                    if len(split_acct_array) < 1:
                                        print "Major logic error... Aborting"
                                        ABORT

                                    for iSplitAcctArray in range(0, len(split_acct_array)):
                                        qtySplit = split_acct_array[iSplitAcctArray][1]

                                        balance = (0.0 if (qty is None) else curr.getDoubleValue(
                                            qty) * price)  # Value in Currency
                                        balanceSplit = (0.0 if (qtySplit is None) else curr.getDoubleValue(
                                            qtySplit) * price)  # Value in Currency
                                        exchangeRate = 1.0
                                        securityIsBase = True
                                        ct = curr.getTable()
                                        relativeToName = curr.getParameter(CurrencyType.TAG_RELATIVE_TO_CURR)
                                        if relativeToName is not None:
                                            self.currXrate = ct.getCurrencyByIDString(relativeToName)
                                            if self.currXrate.getIDString() == baseCurrency.getIDString():
                                                if debug: print "Found conversion rate - but it's already the base rate..: ", relativeToName
                                            else:
                                                securityIsBase = False
                                                # exchangeRate = round(self.currXrate.getRate(baseCurrency),self.currXrate.getDecimalPlaces())
                                                exchangeRate = self.currXrate.getRate(baseCurrency)
                                                if debug: print "Found conversion rate: ", relativeToName, exchangeRate
                                        else:
                                            if debug: print "No conversion rate found.... Assuming Base Currency"
                                            self.currXrate = baseCurrency

                                        # Check to see if all Security Currencies are the same...?
                                        if self.allOneCurrency:
                                            if self.sameCurrency is None:               self.sameCurrency = self.currXrate
                                            if self.sameCurrency != self.currXrate:     self.allOneCurrency = False

                                        balanceBase = (0.0 if (qty is None) else (curr.getDoubleValue(
                                            qty) * price / exchangeRate))  # Value in Base Currency
                                        balanceBaseSplit = (0.0 if (qtySplit is None) else (curr.getDoubleValue(
                                            qtySplit) * price / exchangeRate))  # Value in Base Currency

                                        costBasisBase = (0.0 if (securityCostBasis is None) else round(
                                            self.currXrate.getDoubleValue(securityCostBasis) / exchangeRate, 2))
                                        gainBase = round(balanceBase, 2) - costBasisBase

                                        costBasisBaseSplit = round(self.currXrate.getDoubleValue(
                                                split_acct_array[iSplitAcctArray][2]) / exchangeRate, 2)
                                        gainBaseSplit = round(balanceBaseSplit, 2) - costBasisBaseSplit

                                        if debug:
                                            if iSplitAcctArray == 0:
                                                print "Values found (local, base, cb, gain): ", balance, balanceBase, costBasisBase, gainBase
                                            if lSplitSecuritiesByAccount:
                                                print "Split Values found (qty, local, base, cb, gain): ", qtySplit, balanceSplit, balanceBaseSplit, costBasisBaseSplit, gainBaseSplit

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
                                        entry.append(
                                            self.myNumberFormatter(balanceBaseSplit, True, self.currXrate, baseCurrency,
                                                                   2))  # Value Base Currency
                                        entry.append(self.myNumberFormatter(costBasisBaseSplit, True, self.currXrate,
                                                                            baseCurrency, 2))  # Cost Basis
                                        entry.append(
                                            self.myNumberFormatter(gainBaseSplit, True, self.currXrate, baseCurrency,
                                                                   2))  # Gain
                                        entry.append(round(gainBaseSplit / costBasisBaseSplit, 3))
                                        entry.append(
                                            split_acct_array[iSplitAcctArray][0].replace(acctSeperator, "", 1))  # Acct
                                        entry.append(curr.getDoubleValue(qtySplit))  # _Shrs
                                        entry.append(price)  # _Price
                                        entry.append(x)  # _CValue
                                        entry.append(round(balanceBaseSplit, 2))  # _BValue
                                        entry.append(costBasisBaseSplit)  # _Cost Basis
                                        entry.append(gainBaseSplit)  # _Gain
                                        entry.append(
                                            str(curr.getName()).upper() + "000" + split_acct_array[iSplitAcctArray][
                                                0].upper().replace(acctSeperator, "", 1))  # _SORT
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
                                    if securityIsBase:
                                        entry.append(None)  # c5 - don't bother displaying if base curr
                                    else:
                                        self.lRemoveCurrColumn = False
                                        entry.append(
                                            self.myNumberFormatter(balance, False, self.currXrate, baseCurrency,
                                                                   2))  # c5
                                        x = round(balance, 2)

                                    entry.append(self.myNumberFormatter(balanceBase, True, self.currXrate, baseCurrency,
                                                                        2))  # c6
                                    entry.append(
                                        self.myNumberFormatter(costBasisBase, True, self.currXrate, baseCurrency,
                                                               2))  # Cost Basis
                                    entry.append(
                                        self.myNumberFormatter(gainBase, True, self.currXrate, baseCurrency, 2))  # Gain
                                    entry.append(round(gainBase / costBasisBase, 3))
                                    buildAcctString = ""
                                    for iIterateAccts in range(0, len(split_acct_array)):
                                        buildAcctString += split_acct_array[iIterateAccts][0]
                                    buildAcctString = buildAcctString[:-len(acctSeperator)]
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
                                        cash = 0.0
                                        # Search to see if Account exists/has been used already for Cash Balance - Only use once!
                                        acct_string = ""
                                        for keys in self.CashBalancesTable.keys():
                                            data = self.CashBalancesTable.get(keys)
                                            acct_array = self.AccountsTable.get(curr)
                                            for iArray in range(0, len(acct_array)):
                                                acct_string += acct_array[iArray][0]  # The account name
                                            # NEXT
                                            if (str(keys) + acctSeperator) in acct_string:
                                                if debug: print "CashBal Search - Found:", keys, "in", str(
                                                        self.AccountsTable.get(curr)), "Cash Bal:", data
                                                cash = data
                                                self.CashBalancesTable[
                                                    keys] = 0.0  # Now delete it so it cannot be used again!
                                                self.totalCashBalanceBase = self.totalCashBalanceBase + cash
                                                self.CashBalanceTableData.append([keys, cash])
                                                continue
                                                # Keep searching as a Security may be used in many accounts...
                                else:
                                    if debug: print "Skipping non Filtered Security/Ticker:", curr, curr.getTickerSymbol()
                            else:
                                if debug: print "Skipping Security with 0 shares..: ", curr, curr.getTickerSymbol(), " Curr: ", curr.getRelativeCurrency().getIDString(), " Price: ", price, " Qty: ", curr.formatSemiFancy(
                                        qty, decimalCharSep)
                        else:
                            if debug: print "Skipping non Filterered Security/Currency:", curr, curr.getTickerSymbol(), curr.getRelativeCurrency().getIDString()
                    elif curr.getHideInUI() and curr.getCurrencyType() == CurrencyType.Type.SECURITY:
                        if debug: print "Skipping Hidden(inUI) Security..: ", curr, curr.getTickerSymbol(), " Curr: ", curr.getRelativeCurrency().getIDString()

                    else:
                        if debug: print "Skipping non Security:", curr, curr.getTickerSymbol()

                if lSplitSecuritiesByAccount:
                    rawDataTable = sorted(rawDataTable, key=lambda x: (x[_SORT]))
                # else:
                #     rawDataTable = sorted(rawDataTable, key=lambda x: (x[1]) )

                return DefaultTableModel(rawDataTable, self.columnNames)

            def getFooterModel(self):
                global debug, baseCurrency, rawFooterTable, lIncludeCashBalances
                if debug: print "In ", inspect.currentframe().f_code.co_name, "()"
                if debug: print "Generating the footer table data...."

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
                    if debug: print "getFooterModel: sameCurrency=", self.currXrate
                    if self.currXrate == None:
                        entry.append(None)
                    else:
                        x = self.totalBalance
                        entry.append(self.myNumberFormatter(self.totalBalance, False, self.currXrate, baseCurrency, 2))
                else:
                    if debug: print "getFooterModel: was not allOneCurrency.."
                    entry.append(None)
                entry.append(self.myNumberFormatter(self.totalBalanceBase, True, baseCurrency, baseCurrency, 2))
                entry.append(
                    self.myNumberFormatter(self.totalCostBasisBase, True, baseCurrency, baseCurrency, 2))  # Cost Basis
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
                    for i in range(0, len(self.CashBalanceTableData)):
                        if self.CashBalanceTableData[i][1] != 0:
                            entry = []
                            entry.append("Cash Bal/Acct:")
                            entry.append(None)
                            entry.append(None)
                            entry.append(None)
                            entry.append(None)
                            entry.append(None)
                            entry.append(self.myNumberFormatter(self.CashBalanceTableData[i][1], True, baseCurrency,
                                                                baseCurrency, 2))
                            entry.append(None)
                            entry.append(None)
                            entry.append(None)
                            entry.append(str(self.CashBalanceTableData[i][0]))
                            entry.append(None)  # Cost Basis
                            entry.append(None)  # Gain
                            entry.append(None)
                            entry.append(self.CashBalanceTableData[i][1])
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
                        entry.append(
                            self.myNumberFormatter(self.totalGainBase, True, baseCurrency, baseCurrency, 2))  # Gain
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
            def myNumberFormatter(self, theNumber, useBase, exchangeCurr, baseCurr, noDecimals):
                global debug, decimalCharSep, groupingCharSep

                decimalSeparator = decimalCharSep
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
                        theNumber = baseCurr.getPrefix() + " " + noDecimalFormatter.format(
                                float(theNumber)) + baseCurr.getSuffix()
                    else:
                        theNumber = baseCurr.getPrefix() + " " + noDecimalFormatter.format(
                                float(theNumber)) + baseCurr.getSuffix()
                        # theNumber = baseCurr.formatFancy(baseCurr.getLongValue(float(theNumber)), decimalSeparator)
                else:
                    if noDecimals == 0:
                        # MD format functions can't print comma-separated values without a decimal point so
                        # we have to do it ourselves
                        theNumber = exchangeCurr.getPrefix() + " " + noDecimalFormatter.format(
                                float(theNumber)) + exchangeCurr.getSuffix()
                    else:
                        theNumber = exchangeCurr.getPrefix() + " " + noDecimalFormatter.format(
                                float(theNumber)) + exchangeCurr.getSuffix()
                        # theNumber = exchangeCurr.formatFancy(exchangeCurr.getLongValue(float(theNumber)), decimalSeparator)

                return theNumber

            class myAcctFilter(AcctFilter):

                def __init__(self, selectAccountType="ALL",
                             hideInactiveAccounts=True,
                             lAllAccounts=True,
                             filterForAccounts="ALL",
                             hideHiddenAccounts=True,
                             hideHiddenSecurities=True,
                             lAllCurrency=True,
                             filterForCurrency="ALL",
                             lAllSecurity=True,
                             filterForSecurity="ALL",
                             findUUID=None):
                    super(AcctFilter, self).__init__()

                    if selectAccountType == "ALL":                     pass
                    elif selectAccountType == "CAT":                     pass
                    elif selectAccountType == "NONCAT":                  pass
                    elif selectAccountType == AccountType.ROOT:          pass
                    elif selectAccountType == AccountType.BANK:          pass
                    elif selectAccountType == AccountType.CREDIT_CARD:   pass
                    elif selectAccountType == AccountType.INVESTMENT:    pass
                    elif selectAccountType == AccountType.SECURITY:      pass
                    elif selectAccountType == AccountType.ASSET:         pass
                    elif selectAccountType == AccountType.LIABILITY:     pass
                    elif selectAccountType == AccountType.LOAN:          pass
                    elif selectAccountType == AccountType.EXPENSE:       pass
                    elif selectAccountType == AccountType.INCOME:        pass
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

                    if self.selectAccountType == "ALL" or acct.getAccountType() == self.selectAccountType: pass
                    elif self.selectAccountType == "CAT" and (
                            acct.getAccountType() == AccountType.EXPENSE or acct.getAccountType() == AccountType.INCOME): pass
                    elif self.selectAccountType == "NONCAT" and not (
                            acct.getAccountType() == AccountType.EXPENSE or acct.getAccountType() == AccountType.INCOME): pass
                    else: return False

                    if self.hideInactiveAccounts:
                        # This logic replicates Moneydance AcctFilter.ACTIVE_ACCOUNTS_FILTER
                        if (acct.getAccountOrParentIsInactive()): return False
                        if (acct.getHideOnHomePage() and acct.getBalance() == 0): return False

                    if acct.getAccountType() == AccountType.SECURITY:
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

                    if acct.getAccountType() == AccountType.SECURITY:  # on Security Accounts, get the Currency from the Security master - else from the account)
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
                global lSplitSecuritiesByAccount, acctSeperator

                if debug: print "In ", inspect.currentframe().f_code.co_name, "()"

                totals = {}  # Dictionary <CurrencyType, Long>
                accounts = {}
                cashTotals = {}  # Dictionary<CurrencyType, Long>
                cbbasistotals = {}

                lDidIFindAny = False

                for acct in AccountUtil.allMatchesForSearch(book, self.myAcctFilter(AccountType.SECURITY,
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
                    if acct.getCurrentBalance() != 0:  # we only want Securities with holdings
                        if debug: print "Processing Acct:", acct.getParentAccount(), "Share/Fund Qty Balances for Security: ", curr, curr.formatSemiFancy(
                                acct.getCurrentBalance(), decimalCharSep), " Shares/Units"

                        total = (0L if (total is None) else total) + acct.getCurrentBalance()
                        totals[curr] = total

                        getTheCostBasis = InvestUtil.getCostBasis(acct)
                        costbasis = (0L if (costbasis is None) else costbasis) + getTheCostBasis
                        cbbasistotals[curr] = costbasis

                        lDidIFindAny = True

                        if lSplitSecuritiesByAccount:  # Build a mini table if split, else 1 row table...
                            if account is None:
                                accounts[curr] = [
                                        [str(acct.getParentAccount()) + acctSeperator, acct.getCurrentBalance(),
                                         getTheCostBasis]]
                            else:
                                account.append([str(acct.getParentAccount()) + acctSeperator, acct.getCurrentBalance(),
                                                getTheCostBasis])
                                accounts[curr] = account
                        else:
                            if account is None:
                                account = str(
                                    acct.getParentAccount()) + acctSeperator  # Important - keep the trailing ' :'
                            else:
                                account = account[0][0] + str(
                                    acct.getParentAccount()) + acctSeperator  # concatenate two strings here
                            accounts[curr] = [[account, acct.getCurrentBalance(), getTheCostBasis]]

                        if lIncludeCashBalances:
                            # Now get the Currency  for the Security Parent Account - to get Cash  Balance
                            curr = acct.getParentAccount().getCurrencyType()

                            # WARNING Cash balances are by Account and not by Security!
                            cashTotal = curr.getDoubleValue(
                                    (acct.getParentAccount().getCurrentBalance())) / curr.getRate(
                                None)  # Will be the same Cash balance per account for all Securities..
                            if debug: print "Cash balance for account:", cashTotal
                            cashTotals[acct.getParentAccount()] = round(cashTotal, 2)
                            # endfor

                self.QtyOfSharesTable = totals
                self.AccountsTable = accounts
                self.CashBalancesTable = cashTotals
                self.CostBasisTotals = cbbasistotals

                return lDidIFindAny

            class myJTable(JTable):  # (JTable)
                if debug: print "In ", inspect.currentframe().f_code.co_name, "()"
                lInTheFooter = False

                def __init__(self, tableModel, lSortTheTable, lInTheFooter):
                    global debug
                    super(JTable, self).__init__(tableModel)
                    self.lInTheFooter = lInTheFooter
                    if lSortTheTable: self.fixTheRowSorter()

                def isCellEditable(self, row, column):
                    return False

                #  Rendering depends on row (i.e. security's currency) as well as column
                def getCellRenderer(self, row, column):
                    global StockGlanceInstance
                    renderer = None
                    if StockGlanceInstance.columnTypes[column] == "Text":
                        renderer = DefaultTableCellRenderer()
                        renderer.setHorizontalAlignment(JLabel.LEFT)
                    elif StockGlanceInstance.columnTypes[column] == "TextNumber":
                        renderer = StockGlanceInstance.myGainsRenderer()
                        renderer.setHorizontalAlignment(JLabel.RIGHT)
                    elif StockGlanceInstance.columnTypes[column] == "%":
                        renderer = StockGlanceInstance.myPercentRenderer()
                        renderer.setHorizontalAlignment(JLabel.RIGHT)
                    elif StockGlanceInstance.columnTypes[column] == "TextC":
                        renderer = DefaultTableCellRenderer()
                        renderer.setHorizontalAlignment(JLabel.CENTER)
                    else:
                        renderer = DefaultTableCellRenderer()
                    return renderer

                class myTextNumberComparator(Comparator):
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
                            if str1 == None or str1 == "": str1 = "0"
                            if str2 == None or str2 == "": str2 = "0"
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
                    for i in range(0, self.getColumnCount()):
                        if i == _SHRS_FORMATTED:
                            sorter.setComparator(i, self.myTextNumberComparator("N"))
                        elif i == _PRICE_FORMATTED:
                            sorter.setComparator(i, self.myTextNumberComparator("N"))
                        elif i == _CVALUE_FORMATTED:
                            sorter.setComparator(i, self.myTextNumberComparator("N"))
                        elif i == _BVALUE_FORMATTED:
                            sorter.setComparator(i, self.myTextNumberComparator("N"))
                        elif i == _CBVALUE_FORMATTED:
                            sorter.setComparator(i, self.myTextNumberComparator("N"))
                        elif i == _GAIN_FORMATTED:
                            sorter.setComparator(i, self.myTextNumberComparator("N"))
                        elif i == _SORT:
                            sorter.setComparator(i, self.myTextNumberComparator("N"))
                        elif i == _GAINPCT:
                            sorter.setComparator(i, self.myTextNumberComparator("%"))
                        else:
                            sorter.setComparator(i, self.myTextNumberComparator("T"))
                    self.getRowSorter().toggleSortOrder(1)

                def prepareRenderer(self, renderer, row, column):  # make Banded rows
                    global StockGlanceInstance, lSplitSecuritiesByAccount

                    component = super(StockGlanceInstance.myJTable, self).prepareRenderer(renderer, row, column)
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
            class myGainsRenderer(DefaultTableCellRenderer):

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
                    str1 = float(conv_string1)

                    if float(str1) < 0.0:
                        self.setForeground(Color.RED)
                    else:
                        self.setForeground(Color.DARK_GRAY)

            # This copies the standard class and just changes the colour to RED if it detects a negative - and formats as %
            class myPercentRenderer(DefaultTableCellRenderer):

                def __init__(self):
                    super(DefaultTableCellRenderer, self).__init__()

                def setValue(self, value):
                    if value is None: return

                    self.setText("{:.1%}".format(value))

                    if value < 0.0:
                        self.setForeground(Color.RED)
                    else:
                        self.setForeground(Color.DARK_GRAY)

            # Syncronises column widths of both JTables
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

                def columnMarginChanged(self, e):
                    sourceModel = self.sourceTable.getColumnModel()
                    targetModel = self.targetTable.getColumnModel()
                    # listener = map.get(self.targetTable)

                    # targetModel.removeColumnModelListener(listener)

                    for i in range(0, sourceModel.getColumnCount()):
                        targetModel.getColumn(i).setPreferredWidth(sourceModel.getColumn(i).getWidth())

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
                def windowClosing(self, WindowEvent):
                    global debug, frame_
                    if debug: print "In ", inspect.currentframe().f_code.co_name, "()"
                    frame_.dispose()
                    return

            class CloseAction(AbstractAction):
                def actionPerformed(self, event):
                    global debug, frame_
                    if debug: print "in CloseAction(), Event: ", event
                    frame_.dispose()
                    return

            def createAndShowGUI(self):
                global debug, frame_, rawDataTable, rawFooterTable, lDisplayOnly, version, lSplitSecuritiesByAccount

                global _SHRS_FORMATTED, _SHRS_RAW, _PRICE_FORMATTED, _PRICE_RAW, _CVALUE_FORMATTED, _CVALUE_RAW, _BVALUE_FORMATTED, _BVALUE_RAW, _SORT
                global _CBVALUE_FORMATTED, _CBVALUE_RAW, _GAIN_FORMATTED, _GAIN_RAW, _EXCLUDECSV, _GAINPCT

                if debug: print "In ", inspect.currentframe().f_code.co_name, "()"

                root = moneydance.getRootAccount()
                self.book = root.getBook()

                self.tableModel = self.getTableModel(self.book)  # Generates/populates the table data
                if self.tableModel is None: return False

                screenSize = Toolkit.getDefaultToolkit().getScreenSize()

                if lDisplayOnly:
                    frame_ = JFrame("Stock Glance 2020 - StuWareSoftSystems(" + version + ")...")
                else:
                    frame_ = JFrame(
                            "Stock Glance 2020 - StuWareSoftSystems(" + version + ")... (CLOSE WINDOW TO EXPORT TO FILE)")

                # frame_.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE)
                frame_.setDefaultCloseOperation(
                        WindowConstants.DO_NOTHING_ON_CLOSE)  # The CloseAction() and WindowListener() will handle dispose() - else change back to DISPOSE_ON_CLOSE

                # Add standard CMD-W keystrokes etc to close window
                frame_.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(
                        KeyStroke.getKeyStroke("control W"), "close-window")
                frame_.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(
                        KeyStroke.getKeyStroke("meta W"), "close-window")
                frame_.getRootPane().getActionMap().put("close-window", self.CloseAction())

                frame_.addWindowListener(self.WindowListener())

                if lSplitSecuritiesByAccount:
                    self.table = self.myJTable(self.tableModel, False,
                                               False)  # Creates JTable() with special sorting too
                else:
                    self.table = self.myJTable(self.tableModel, True,
                                               False)  # Creates JTable() with special sorting too

                self.tableHeader = self.table.getTableHeader()
                self.tableHeader.setReorderingAllowed(
                    False)  # no more drag and drop columns, it didn't work (on the footer)
                self.table.getTableHeader().setDefaultRenderer(DefaultTableHeaderCellRenderer())

                self.footerModel = self.getFooterModel()  # Generate/populate the footer table data
                self.footerTable = self.myJTable(self.footerModel, False,
                                                 True)  # Creates JTable() for footer - with disabled sorting too

                # Column listeners to resize columns on both tables to keep them in sync
                cListener1 = self.ColumnChangeListener(self.table, self.footerTable)
                # cListener2=self.ColumnChangeListener(self.footerTable,self.table) # Not using this as footer headers not manually resizable (as hidden)

                tcm = self.table.getColumnModel()
                tcm.addColumnModelListener(cListener1)

                c0 = 120
                c1 = 300
                c2 = 120
                c3 = 100
                c4 = 80
                c5 = 120
                c6 = 120
                c7 = 120
                c8 = 120
                c9 = 70
                c10 = 350
                c11 = 0
                c12 = 0
                c13 = 0
                c14 = 0
                c15 = 0
                c16 = 0
                c17 = 0
                c18 = 0
                cTotal = c0 + c1 + c2 + c3 + c4 + c5 + c6 + c7 + c8 + c9 + c10 + c11 + c11 + c12 + c13 + c14 + c15 + c16 + c17 + c18

                tcm.getColumn(0).setPreferredWidth(c0)
                tcm.getColumn(1).setPreferredWidth(c1)
                tcm.getColumn(2).setPreferredWidth(c2)
                tcm.getColumn(3).setPreferredWidth(c3)
                tcm.getColumn(4).setPreferredWidth(c4)
                tcm.getColumn(5).setPreferredWidth(c5)
                tcm.getColumn(6).setPreferredWidth(c6)
                tcm.getColumn(7).setPreferredWidth(c7)
                tcm.getColumn(8).setPreferredWidth(c8)
                tcm.getColumn(9).setPreferredWidth(c9)
                tcm.getColumn(10).setPreferredWidth(c10)

                # I'm hiding these columns for ease of data retrieval. The better option would be to remove the columns
                for i in reversed(range(_SHRS_RAW, tcm.getColumnCount())):
                    tcm.getColumn(i).setMinWidth(0)
                    tcm.getColumn(i).setMaxWidth(0)
                    tcm.getColumn(i).setWidth(0)
                    self.table.removeColumn(tcm.getColumn(i))
                self.table.setAutoResizeMode(JTable.AUTO_RESIZE_OFF)

                if debug: print "Hiding unused Currency Column..."
                # I'm hiding it rather than removing it so not to mess with sorting etc...
                if self.lRemoveCurrColumn:
                    tcm.getColumn(_CVALUE_FORMATTED).setPreferredWidth(0)
                    tcm.getColumn(_CVALUE_FORMATTED).setMinWidth(0)
                    tcm.getColumn(_CVALUE_FORMATTED).setMaxWidth(0)
                    tcm.getColumn(_CVALUE_FORMATTED).setWidth(0)

                self.footerTable.setColumnSelectionAllowed(False)
                self.footerTable.setRowSelectionAllowed(True)
                # self.footerTable.setFocusable(False)

                tcm = self.footerTable.getColumnModel()
                # tcm.addColumnModelListener(cListener2)
                tcm.getColumn(0).setPreferredWidth(c0)
                tcm.getColumn(1).setPreferredWidth(c1)
                tcm.getColumn(2).setPreferredWidth(c2)
                tcm.getColumn(3).setPreferredWidth(c3)
                tcm.getColumn(4).setPreferredWidth(c4)
                tcm.getColumn(5).setPreferredWidth(c5)
                tcm.getColumn(6).setPreferredWidth(c6)
                tcm.getColumn(7).setPreferredWidth(c7)
                tcm.getColumn(8).setPreferredWidth(c8)
                tcm.getColumn(9).setPreferredWidth(c9)
                tcm.getColumn(10).setPreferredWidth(c10)

                # I'm hiding these columns for ease of data retrieval. The better option would be to remove the columns
                for i in reversed(range(_SHRS_RAW, tcm.getColumnCount())):
                    tcm.getColumn(i).setMinWidth(0)
                    tcm.getColumn(i).setMaxWidth(0)
                    tcm.getColumn(i).setWidth(0)
                    self.footerTable.removeColumn(tcm.getColumn(i))
                self.footerTable.setAutoResizeMode(JTable.AUTO_RESIZE_OFF)

                # I'm hiding it rather than removing it so not to mess with sorting etc...
                if self.lRemoveCurrColumn:
                    tcm.getColumn(_CVALUE_FORMATTED).setPreferredWidth(0)
                    tcm.getColumn(_CVALUE_FORMATTED).setMinWidth(0)
                    tcm.getColumn(_CVALUE_FORMATTED).setMaxWidth(0)
                    tcm.getColumn(_CVALUE_FORMATTED).setWidth(0)

                self.footerTableHeader = self.footerTable.getTableHeader()
                self.footerTableHeader.setEnabled(False)  # may have worked, but doesn't...
                self.footerTableHeader.setPreferredSize(Dimension(0, 0))  # this worked no more footer Table header

                self.scrollPane = JScrollPane(self.table, JScrollPane.VERTICAL_SCROLLBAR_ALWAYS,
                                              JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED)
                self.scrollPane.getHorizontalScrollBar().setPreferredSize(Dimension(0, 0))
                self.scrollPane.setBorder(CompoundBorder(MatteBorder(0, 0, 1, 0, Color.gray), EmptyBorder(0, 0, 0, 0)))
                rowCount = self.table.getRowCount()
                rowHeight = self.table.getRowHeight()
                interCellSpacing = self.table.getIntercellSpacing().height
                headerHeight = self.table.getTableHeader().getPreferredSize().height
                insets = self.scrollPane.getInsets()
                scrollHeight = self.scrollPane.getHorizontalScrollBar().getPreferredSize()
                width = min(cTotal + 20, screenSize.width)  # width of all elements

                calcScrollPaneHeightRequired = min(screenSize.height - 300, max(60, ((rowCount * rowHeight) + (
                        (rowCount) * (
                        interCellSpacing)) + headerHeight + insets.top + insets.bottom + scrollHeight.height)))

                if debug:
                    print "ScreenSize: ", screenSize
                    print "Main JTable heights...."
                    print "Row Count: ", rowCount
                    print "RowHeight: ", rowHeight
                    print "Intercell spacing: ", interCellSpacing
                    print "Header height: ", headerHeight
                    print "Insets, Top/Bot: ", insets, insets.top, insets.bottom
                    print "Total scrollpane height: ", calcScrollPaneHeightRequired
                    print "Scrollbar height: ", scrollHeight, scrollHeight.height

                # Basically set the main table to fill most of the screen maxing at 800, but allowing for the footer...
                self.scrollPane.setPreferredSize(Dimension(width, calcScrollPaneHeightRequired))

                frame_.add(self.scrollPane, BorderLayout.CENTER)

                self.footerScrollPane = JScrollPane(self.footerTable, JScrollPane.VERTICAL_SCROLLBAR_ALWAYS,
                                                    JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED)
                self.footerScrollPane.setBorder(
                    CompoundBorder(MatteBorder(0, 0, 1, 0, Color.gray), EmptyBorder(0, 0, 0, 0)))

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
                    print "Footer JTable heights...."
                    print "Row Count: ", frowCount
                    print "RowHeight: ", frowHeight
                    print "Intercell spacing: ", finterCellSpacing
                    print "Header height: ", fheaderHeight
                    print "Insets, Top/Bot: ", finsets, finsets.top, finsets.bottom
                    print "Total scrollpane height: ", fcalcScrollPaneHeightRequired
                    print "Scrollbar height: ", fscrollHeight, fscrollHeight.height

                self.footerScrollPane.setPreferredSize(Dimension(width, fcalcScrollPaneHeightRequired))
                frame_.add(self.footerScrollPane, BorderLayout.SOUTH)

                if debug: print "Total frame height required: ", calcScrollPaneHeightRequired, " + ", \
                    fcalcScrollPaneHeightRequired, "+ Intercells: ", finsets.top, finsets.bottom, " = ", \
                    (calcScrollPaneHeightRequired + fcalcScrollPaneHeightRequired) + \
                    (finsets.top * 2) + (finsets.bottom * 2)

                # Seems to be working well without setting the frame sizes + pack()
                # frame_.setPreferredSize(Dimension(width, max(150,calcScrollPaneHeightRequired+fcalcScrollPaneHeightRequired+(finsets.top*2)+(finsets.bottom*2))))
                # frame_.setSize(width,calcScrollPaneHeightRequired+fcalcScrollPaneHeightRequired)   # for some reason this seems irrelevant?

                frame_.pack()
                frame_.setVisible(True)
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

            def getTableCellRendererComponent(self, table, value, isSelected, hasFocus, row, column):
                super(DefaultTableHeaderCellRenderer, self).getTableCellRendererComponent(table, value, isSelected,
                                                                                          hasFocus, row, column)
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
            def getSortKey(self, table, column):
                rowSorter = table.getRowSorter()
                if (rowSorter is None): return None
                sortedColumns = rowSorter.getSortKeys()
                if (sortedColumns.size() > 0): return sortedColumns.get(0)
                return None
            # enddef


        # endclass

        if not lDisplayOnly: print "!!!FILE WILL BE GENERATED AFTER YOU CLOSE THE TABLE VIEW WINDOW!!!"

        StockGlanceInstance = StockGlance2020()

        if StockGlance2020.createAndShowGUI(StockGlanceInstance):
            # A bit of a fudge, but hey it works.....!
            i = 0
            while frame_.isVisible():
                i = i + 1
                time.sleep(1)
                if debug: print "Waiting for JFrame() to close... Wait number...:", i

            if debug: print "No longer waiting...."

            if not lDisplayOnly:
                def ExportDataToFile():
                    global debug, frame_, rawDataTable, rawFooterTable, headingNames, csvfilename, decimalCharSep, groupingCharSep, csvDelimiter, version
                    global lSplitSecuritiesByAccount, lExcludeTotalsFromCSV, myScriptName

                    global _SHRS_FORMATTED, _SHRS_RAW, _PRICE_FORMATTED, _PRICE_RAW, _CVALUE_FORMATTED, _CVALUE_RAW, _BVALUE_FORMATTED, _BVALUE_RAW, _SORT
                    global _CBVALUE_FORMATTED, _CBVALUE_RAW, _GAIN_FORMATTED, _GAIN_RAW, _EXCLUDECSV, _GAINPCT

                    if debug: print "In ", inspect.currentframe().f_code.co_name, "()"

                    # NOTE - You can add sep=; to beginning of file to tell Excel what delimiter you are using
                    if not lSplitSecuritiesByAccount:
                        rawDataTable = sorted(rawDataTable, key=lambda x: (str(x[1]).upper()))

                    rawDataTable.insert(0,
                                        headingNames)  # Insert Column Headings at top of list. A bit rough and ready, not great coding, but a short list...!

                    for i in range(0, len(rawFooterTable)):
                        rawDataTable.append(rawFooterTable[i])

                    # Write the csvlines to a file
                    if debug: print "Opening file and writing ", len(rawDataTable), " records"
                    myPrint("J", "Opening file and writing ", len(rawDataTable), " records" )

                    lFileError = False

                    try:
                        # CSV Writer will take care of special characters / delimiters within fields by wrapping in quotes that Excel will decode
                        with open(csvfilename,
                                  "wb") as csvfile:  # PY2.7 has no newline parameter so opening in binary; juse "w" and newline='' in PY3.0
                            writer = csv.writer(csvfile, dialect='excel', quoting=csv.QUOTE_MINIMAL,
                                                delimiter=csvDelimiter)

                            if csvDelimiter != ",":
                                writer.writerow(["sep=",
                                                 ""])  # Tells Excel to open file with the alternative delimiter (it will add the delimiter to this line)

                            writer.writerow(
                                    rawDataTable[0][:_SHRS_RAW])  # Print the header, but not the extra _field headings

                            for i in range(1, len(rawDataTable)):
                                if not rawDataTable[i][_EXCLUDECSV]:
                                    # Write the table, but swap in the raw numbers (rather than formatted number strings)
                                    writer.writerow([
                                            fixFormatsStr(rawDataTable[i][0], False),
                                            fixFormatsStr(rawDataTable[i][1], False),
                                            fixFormatsStr(rawDataTable[i][_SHRS_RAW], True),
                                            fixFormatsStr(rawDataTable[i][_PRICE_RAW], True),
                                            fixFormatsStr(rawDataTable[i][4], False),
                                            fixFormatsStr(rawDataTable[i][_CVALUE_RAW], True),
                                            fixFormatsStr(rawDataTable[i][_BVALUE_RAW], True),
                                            fixFormatsStr(rawDataTable[i][_CBVALUE_RAW], True),
                                            fixFormatsStr(rawDataTable[i][_GAIN_RAW], True),
                                            fixFormatsStr(rawDataTable[i][_GAINPCT], True, "%"),
                                            fixFormatsStr(rawDataTable[i][10], False),
                                            ""])
                                # ENDIF
                            # NEXT
                            today = Calendar.getInstance()
                            writer.writerow([""])
                            writer.writerow(["StuWareSoftSystems - "+myScriptName+"("
                                             + version
                                             + ")  MoneyDance Python Script - Date of Extract: "
                                             + str(sdf.format(today.getTime()))])
                        myPrint("B", "CSV file " + csvfilename + " created, records written, and file closed..")

                    except IOError, e:
                        print "Oh no - File IO Error!"
                        print e
                        print sys.exc_type
                        print "Path:", csvfilename
                        print "!!! ERROR - No file written - sorry! (was file open, permissions etc?)".upper()
                        lFileError = True

                    # Do it all again!?
                    if lFileError:
                        print "As file write failed, writing to console.....:\n\nUse Select/Copy and then paste into Excel. Select column and then Use Text to Columns..\n\n"
                        try:
                            # CSV Writer will take care of special characters / delimiters within fields by wrapping in quotes that Excel will decode
                            writer = csv.writer(sys.stdout, dialect='excel', quoting=csv.QUOTE_MINIMAL,
                                                delimiter=csvDelimiter)

                            if csvDelimiter != ",":
                                writer.writerow(["sep=",
                                                 ""])  # Tells Excel to open file with the alternative delimiter (it will add the delimiter to this line)

                            writer.writerow(
                                    rawDataTable[0][:_SHRS_RAW])  # Print the header, but not the extra _field headings

                            for i in range(1, len(rawDataTable)):
                                if not rawDataTable[i][_EXCLUDECSV]:
                                    # Write the table, but swap in the raw numbers (rather than formatted number strings)
                                    writer.writerow([
                                            fixFormatsStr(rawDataTable[i][0], False),
                                            fixFormatsStr(rawDataTable[i][1], False),
                                            fixFormatsStr(rawDataTable[i][_SHRS_RAW], True),
                                            fixFormatsStr(rawDataTable[i][_PRICE_RAW], True),
                                            fixFormatsStr(rawDataTable[i][4], False),
                                            fixFormatsStr(rawDataTable[i][_CVALUE_RAW], True),
                                            fixFormatsStr(rawDataTable[i][_BVALUE_RAW], True),
                                            fixFormatsStr(rawDataTable[i][_CBVALUE_RAW], True),
                                            fixFormatsStr(rawDataTable[i][_GAIN_RAW], True),
                                            fixFormatsStr(rawDataTable[i][_GAINPCT], True, "%"),
                                            fixFormatsStr(rawDataTable[i][10], False),
                                            ""])
                                # ENDIF
                            # NEXT
                            today = Calendar.getInstance()
                            writer.writerow([""])
                            writer.writerow(["StuWareSoftSystems - "+myScriptName+"("
                                             + version
                                             + ")  MoneyDance Python Script - Date of Extract: "
                                             + str(sdf.format(today.getTime()))])
                            print "\n\n\n"
                            print 'STDOUT: records displayed on console..'

                        except:
                            print "Oh no - Another error on stdout! (giving up)....."
                            lFileError = True


                # enddef

                def fixFormatsStr(theString, lNumber, sFormat=""):
                    global lStripASCII

                    if lNumber == None: lNumber = False
                    if theString == None: theString = ""

                    if sFormat == "%" and theString != "":
                        theString = "{:.1%}".format(theString)
                        return theString

                    if lNumber: return str(theString)

                    theString = theString.strip()  # remove leading and trailing spaces

                    if theString[:3] == "===": theString = " "+theString # Small fix as Libre Office doesn't like "=======" (it thinks it's a formula)

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


        def saveParameters():
            global debug  # Set to True if you want verbose messages, else set to False....
            global hideHiddenSecurities, hideInactiveAccounts, hideHiddenAccounts, lAllCurrency, filterForCurrency
            global lAllSecurity, filterForSecurity, lAllAccounts, filterForAccounts, lIncludeCashBalances, lStripASCII, csvDelimiter, scriptpath
            global lSplitSecuritiesByAccount, lExcludeTotalsFromCSV
            global lUseMacFileChooser, lDisplayOnly, version, myParameters

            if debug: print "In ", inspect.currentframe().f_code.co_name, "()"

            # NOTE: Parameters were loaded earlier on... Preserve existing, and update any used ones...
            # (i.e. other StuWareSoftSystems programs might be sharing the same file)

            if myParameters is None: myParameters = {}

            myParameters["__Author"] = "Stuart Beesley - (c) StuWareSoftSystems"
            myParameters["__StockGlance2020"] = version
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
            myParameters["lStripASCII"] = lStripASCII
            myParameters["csvDelimiter"] = csvDelimiter
            myParameters["debug"] = debug
            myParameters["lUseMacFileChooser"] = lUseMacFileChooser

            if not lDisplayOnly and scriptpath != "" and os.path.isdir(scriptpath):
                myParameters["scriptpath"] = scriptpath

            dict_filename = os.path.join("..", "StuWareSoftSystems.dict")
            if debug: print "Will try to save parameter file:", dict_filename

            local_storage = moneydance.getCurrentAccountBook().getLocalStorage()
            ostr = local_storage.openFileForWriting(dict_filename)

            myPrint("J","about to Pickle.dump and save parameters to file:", dict_filename)

            try:
                save_file = FileUtil.wrap(ostr)
                pickle.dump(myParameters, save_file)
                save_file.close()

                if debug:
                    print "myParameters now contains...:"
                    for key in sorted(myParameters.keys()):
                        print "...variable:", key, myParameters[key]

            except:
                print "Error - failed to create/write parameter file.. Ignoring and continuing....."
                return

            if debug: print "Parameter file written and parameters saved to disk....."


        # ENDDEF

        saveParameters()

    else:
        pass

    # Some cleanup of large / important objects....
    try:
        if debug: print "deleting old objects"
        if "frame_" in vars() or "frame_" in globals(): del frame_
        if "userFilters" in vars() or "userFilters" in globals(): del userFilters
        if "rawDataTable" in vars() or "rawDataTable" in globals(): del rawDataTable
        if "StockGlance2020" in vars() or "StockGlance2020" in globals(): del StockGlance2020
        if "rawrawFooterTable" in vars() or "rawrawFooterTable" in globals(): del rawrawFooterTable
        if "JTextFieldLimitYN" in vars() or "JTextFieldLimitYN" in globals(): del JTextFieldLimitYN
        if "StockGlanceInstance" in vars() or "StockGlanceInstance" in globals(): del StockGlanceInstance

    except:
        if debug: print "Objects did not exist.."

else:
    # Otherwise version error - ending
    pass

myPrint("B", "StuWareSoftSystems - ",os.path.basename(__file__)," script ending......")

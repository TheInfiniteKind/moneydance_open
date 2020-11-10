#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# extract_investment_transactions_csv.py - v1b - November 2020 - Stuart Beesley
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
# Use in MoneyDance Menu Window->Show Moneybot Console >> Open Script >> RUN
# NOTE: MiscExp & MiscInc with fees are just wrong... MD handles them incorrectly. I try to replicate MD until it's fixed

# Stuart Beesley Created 2020-11-01 tested on MacOS - MD2021 onwards - StuWareSoftSystems....
# v0.1 beta - Initial release; v0.2 beta - fixes; v0.3 beta - added options for opening balances and splits
# v0.4 beta - changed to getBalance() to include future dated txns; also tweaked to use MD decimal point
# v1 - Public release
# v1a - Fix small data issue on Memo fields with Opening Balances; also added Bal to Amount field (user request).
# v1b - Small tweak to input parameter field (cosmetic only)
# v1b - Add BOM mark to CSV file so Excel opens CSV with double-click (and changed open() to 'w' from 'wb'). Strip ASCII when requested.

import sys
reload(sys)  # Dirty hack to eliminate UTF-8 coding errors
sys.setdefaultencoding('utf8')  # Dirty hack to eliminate UTF-8 coding errors

import platform
import datetime

from com.infinitekind.moneydance.model import *
from com.infinitekind.moneydance.model import TxnUtil, TxnSearch, AbstractTxn, InvestTxnType, InvestUtil, Account
from com.moneydance.util import Platform

from java.awt import *
from java.awt import FileDialog, GridLayout

from java.text import SimpleDateFormat, DecimalFormat

from java.util import *
from java.util import Calendar

from javax.swing import JOptionPane, JTextField, JPanel, JLabel

from javax.swing.text import PlainDocument

from java.lang import System

from java.io import FileNotFoundException, FilenameFilter
from org.python.core.util import FileUtil

import codecs

import os
import os.path

import inspect

import csv
import pickle

# Note:
# moneydance is instance of <type 'com.moneydance.apps.md.controller.Main'>
# moneydance_data is instance of <type 'com.infinitekind.moneydance.model.AccountBook'>
# moneydance_ui is instance of <type 'com.moneydance.apps.md.view.gui.MoneydanceGUI'>


# StuWareSoftSystems common Globals
global debug  # Set to True if you want verbose messages, else set to False....
global hideHiddenSecurities, hideInactiveAccounts, hideHiddenAccounts, lAllCurrency, filterForCurrency, lAllSecurity, filterForSecurity, lAllAccounts, filterForAccounts
global lStripASCII, csvDelimiter
global lIamAMac
global csvfilename, version, scriptpath, lDisplayOnly, myScriptName
global decimalCharSep, groupingCharSep, myParameters, _resetParameters

# This program's Globals
global baseCurrency, sdf, lIncludeOpeningBalances, lAdjustForSplits, userdateformat

global transactionTable, dataKeys

version = "1b"

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
lIncludeOpeningBalances = True
lAdjustForSplits = True
userdateformat = "%Y/%m/%d"

lStripASCII = False
csvDelimiter = ","
debug = False
_resetParameters = False  # set this to True to prevent loading parameters from disk and use the defaults above...

lIamAMac = False
myParameters = {}
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
    if where == "J" or where == "B": System.err.write(myScriptName + ": " + printString + "\n")

myPrint("B", "StuWareSoftSystems...")
myPrint("B", os.path.basename(__file__), ": Python Script Initialising.......", "Version:", version)

def getParameters():
    global debug  # Set to True if you want verbose messages, else set to False....
    global hideHiddenSecurities, hideInactiveAccounts, hideHiddenAccounts, lAllCurrency, filterForCurrency
    global lAllSecurity, filterForSecurity, lAllAccounts, filterForAccounts, lStripASCII, csvDelimiter, scriptpath
    global lIncludeOpeningBalances, lAdjustForSplits, userdateformat

    global myParameters

    if debug: print "In ", inspect.currentframe().f_code.co_name, "()"

    dict_filename = os.path.join("..", "StuWareSoftSystems.dict")
    if debug: print "Now checking for parameter file:", dict_filename

    local_storage = moneydance.getCurrentAccountBook().getLocalStorage()
    if local_storage.exists(dict_filename):
        __StockGlance2020 = None

        myPrint("J", "loading parameters from Pickle file:", dict_filename)
        if debug: print "Parameter file", dict_filename, "exists.."
        # Open the file
        try:
            istr = local_storage.openFileForReading(dict_filename)
            load_file = FileUtil.wrap(istr)
            myParameters = pickle.load(load_file)
            load_file.close()
        except FileNotFoundException as e:
            myPrint("B", "Error: failed to find parameter file...")
            myParameters = None
        except EOFError as e:
            myPrint("B", "Error: reached EOF on parameter file....")
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
    if myParameters.get("debug") is not None: debug = myParameters.get("debug")
    if myParameters.get("lIncludeOpeningBalances") is not None: lIncludeOpeningBalances = myParameters.get("lIncludeOpeningBalances")
    if myParameters.get("lAdjustForSplits") is not None: lAdjustForSplits = myParameters.get("lAdjustForSplits")
    if myParameters.get("userdateformat") is not None: userdateformat = myParameters.get("userdateformat")

    if myParameters.get("lUseMacFileChooser") is not None:
        myPrint("B", "Detected old lUseMacFileChooser parameter/variable... Will delete it...")
        myParameters.pop("lUseMacFileChooser", None)  # Old variable - not used - delete from parameter file

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

if debug: myPrint("B", "DEBUG IS ON..")


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
        myPrint("J", "Platform version issue - will terminate script!")
        print "\n@@@ TERMINATING PROGRAM @@@\n"

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

        decimalPoint_MD = moneydance_ui.getPreferences().getSetting("decimal_character", ".")

        decimalFormat = DecimalFormat.getInstance()
        decimalSymbols = decimalFormat.getDecimalFormatSymbols()

        if not lGetGrouping: lGetPoint = True
        if lGetGrouping and lGetPoint: return "error"

        if lGetPoint:
            decimalCharSep = decimalSymbols.getDecimalSeparator()
            if debug: print "Decimal Point Character:", decimalCharSep

            if decimalPoint_MD != decimalCharSep:
                if debug: print "NOTE - MD decimal:", decimalPoint_MD, "is different to locale:", decimalCharSep, "- Will override to use MD's"
                decimalCharSep = decimalPoint_MD

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
            if (self.what == "YN" and (myString in "YN")) \
                    or (self.what == "DELIM" and (myString in ";|,")) \
                    or (self.what == "1234" and (myString in "1234")) \
                    or (self.what == "CURR"):
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

    label12 = JLabel("Turn DEBUG Verbose messages on? (Y/N)")
    user_selectDEBUG = JTextField(2)
    user_selectDEBUG.setDocument(JTextFieldLimitYN(1, True, "YN"))
    if debug:  user_selectDEBUG.setText("Y")
    else:           user_selectDEBUG.setText("N")

    userFilters = JPanel(GridLayout(13, 2))
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
    userFilters.add(label12)
    userFilters.add(user_selectDEBUG)

    lExit = False
    lDisplayOnly = False

    options = ["ABORT", "CSV Export"]
    userAction = (
            JOptionPane.showOptionDialog(None, userFilters, "(" + version + ")Set Script Parameters....", JOptionPane.OK_CANCEL_OPTION,
                                         JOptionPane.QUESTION_MESSAGE, None, options, options[1]))
    if userAction == 1:  # Export
        if debug: print "Export chosen"
        lDisplayOnly = False
    else:
        print "User Cancelled Parameter selection.. Will exit.."
        lDisplayOnly = False
        lExit = True

    if not lExit:
        if debug:
            print "Parameters Captured", \
                "Sec: ", user_hideHiddenSecurities.getText(), \
                "InActAct:", user_hideInactiveAccounts.getText(), \
                "HidAct:", user_hideHiddenAccounts.getText(), \
                "Curr:", user_selectCurrency.getText(), \
                "Ticker:", user_selectTicker.getText(), \
                "Filter Accts:", user_selectAccounts.getText(), \
                "Incl Open Bals:", user_selectOpeningBalances.getText(), \
                "Adj Splits:", user_selectAdjustSplits.getText(), \
                "User Date Format:", user_dateformat.getText(), \
                "Strip ASCII:", user_selectStripASCII.getText(), \
                "Verbose Debug Messages: ", user_selectDEBUG.getText(), \
                "CSV File Delimiter:", user_selectDELIMITER.getText()
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
            print "Invalid Delimiter:", csvDelimiter, "selected. Overriding with:','"
            csvDelimiter = ","
        if decimalCharSep == csvDelimiter:
            print "WARNING: The CSV file delimiter:", csvDelimiter, "cannot be the same as your decimal point character:", \
                decimalCharSep, " - Proceeding without file export!!"
            lDisplayOnly = True

        if user_selectDEBUG.getText() == "Y":   debug = True
        else:
            debug = False
        if debug: print "DEBUG turned on"

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

        if lIncludeOpeningBalances:
            print "Including Opening Balances..."
        else:
            print "Ignoring Opening Balances... "

        if lAdjustForSplits:
            print "Script will adjust for Stock Splits..."
        else:
            print "Not adjusting for Stock Splits..."

        print "user date format....:", userdateformat


        # Now get the export filename
        csvfilename = None

        if not lDisplayOnly:  # i.e. we have asked for a file export - so get the filename - Always False in this script1

            if lStripASCII:
                print "Will strip non-ASCII characters - e.g. Currency symbols from output file...", " Using Delimiter:", csvDelimiter
            else:
                print "Non-ASCII characters will not be stripped from file: ", " Using Delimiter:", csvDelimiter

            class ExtFilenameFilter(FilenameFilter):
                ext = ""

                def __init__(self, ext):
                    self.ext = "." + ext.upper()

                def accept(self, thedir, filename):
                    if filename is not None and filename.upper().endswith(self.ext):
                        return True
                    return False

            def grabTheFile():
                global debug, lDisplayOnly, csvfilename, lIamAMac, scriptpath, myScriptName
                if debug: print "In ", inspect.currentframe().f_code.co_name, "()"

                if scriptpath == "" or scriptpath is None:  # No parameter saved / loaded from disk
                    scriptpath = myDir()

                if debug: print "Default file export output path is....:", scriptpath

                csvfilename = ""
                if lIamAMac:
                    if debug: print "MacOS X detected: Therefore I will run FileDialog with no extension filters to get filename...."
                    # jFileChooser hangs on Mac when using file extension filters, also looks rubbish. So using Mac(ish)GUI

                    System.setProperty("com.apple.macos.use-file-dialog-packages",
                                       "true")  # In theory prevents access to app file structure (but doesnt seem to work)
                    System.setProperty("apple.awt.fileDialogForDirectories", "false")

                filename = FileDialog(None, "Select/Create CSV file for Investment Txns extract (CANCEL=NO EXPORT)")
                filename.setMultipleMode(False)
                filename.setMode(FileDialog.SAVE)
                filename.setFile('extract_investment_transactions.csv')
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
                    csvfilename = os.path.join(filename.getDirectory(), filename.getFile())
                    scriptpath = str(filename.getDirectory())

                if not lDisplayOnly:
                    if os.path.exists(csvfilename) and os.path.isfile(
                            csvfilename): print "WARNING: file exists,but assuming user said OK to overwrite.."

                if not lDisplayOnly:
                    if check_file_writable(csvfilename):
                        print 'Will extract investment transactions to file: ', csvfilename, "(NOTE: Should drop non utf8 characters...)"
                        scriptpath = os.path.dirname(csvfilename)
                    else:
                        print "Sorry - I just checked and you do not have permissions to create this file:", csvfilename
                        print "I will display the file to screen so you can copy/paste into Excel...!"
                        myPrint("J", "Error - file is not writable...: ", csvfilename)
                        # csvfilename=""
                        # lDisplayOnly = True

                if "filename" in vars() or "filename" in globals(): del filename
                if "extfilter" in vars() or "extfilter" in globals(): del extfilter

                return


            # enddef

            if not lDisplayOnly: grabTheFile()
        else:
            pass
        # endif

        if csvfilename is None:
            lDisplayOnly = True
            print "No Export will be performed"

        if not lDisplayOnly:

            class MyTxnSearchCostBasis(TxnSearch):

                def __init__(self,
                             hideInactiveAccounts=False,
                             lAllAccounts=True,
                             filterForAccounts="ALL",
                             hideHiddenAccounts=False,
                             hideHiddenSecurities=False,
                             lAllCurrency=True,
                             filterForCurrency="ALL",
                             lAllSecurity=True,
                             filterForSecurity="ALL",
                             findUUID=None):
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

                def matchesAll(self):
                    return False

                def matches(self, txn):
                    # NOTE: If not using the parameter selectAccountType=.SECURITY then the security filters won't work (without
                    # special extra coding!)

                    txnAcct = txn.getAccount()

                    if self.findUUID is not None:  # If UUID supplied, override all other parameters...
                        if txnAcct.getUUID() == self.findUUID:
                            return True
                        else:
                            return False

                    # Investment Accounts only
                    if txnAcct.getAccountType() != Account.AccountType.INVESTMENT:
                        return False

                    if self.hideInactiveAccounts:
                        # This logic replicates MoneyDance AcctFilter.ACTIVE_ACCOUNTS_FILTER
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
                    lParent = False
                    parent = txn.getParentTxn()
                    if txn == parent:
                        lParent = True

                    txnCurr = txnAcct.getCurrencyType()

                    if lAllSecurity:
                        securityCurr = None
                        securityTxn = None
                        securityAcct = None
                    else:

                        if not lParent: return False

                        # If we don't have a security record, then we are not interested!
                        securityTxn = TxnUtil.getSecurityPart(txn)
                        if securityTxn is None:
                            return False

                        securityAcct = securityTxn.getAccount()
                        securityCurr = securityAcct.getCurrencyType()

                        if not self.hideHiddenSecurities or (self.hideHiddenSecurities and not securityCurr.getHideInUI()):
                            pass
                        else:
                            return False

                        if self.lAllSecurity:
                            pass
                        elif self.filterForSecurity.upper().strip() in securityCurr.getTickerSymbol().upper().strip():
                            pass
                        elif self.filterForSecurity.upper().strip() in securityCurr.getName().upper().strip():
                            pass
                        else:
                            return False
                    #ENDIF

                    if lAllCurrency:
                        pass
                    else:
                        if securityCurr:
                            if txnCurr.getIDString().upper().strip() != securityCurr.getRelativeCurrency().getIDString().upper().strip():
                                print "LOGIC ERROR: I can't see how the Security's currency is different to the Account's currency? ",
                                print txnCurr.getIDString().upper().strip(), securityCurr.getRelativeCurrency().getIDString().upper().strip()
                                print repr(txn)
                                print repr(txnCurr)
                                print repr(securityCurr)
                                raise Exception("LOGIC Error - Security's currency: " \
                                        + securityCurr.getRelativeCurrency().getIDString().upper().strip() \
                                        + " is different to txn currency: " \
                                        + txnCurr.getIDString().upper().strip() \
                                        + " Aborting")


                        # All accounts and security records can have currencies
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
                            elif (self.filterForCurrency.upper().strip() in txnCurr.getIDString().upper().strip()) :
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

            if debug: print dataKeys

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

                            if debug: print row
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

                        if debug: print securityCurr, " - Found share splits..."
                        if debug: print securityTxn

                        stockSplits = sorted(stockSplits, key=lambda x: x.getDateInt(), reverse=True) # Sort date newest first...
                        for theSplit in stockSplits:
                            if row[dataKeys["_DATE"][_COLUMN]] >= theSplit.getDateInt():
                                continue
                            if debug: print securityCurr, " -  ShareSplits()... Applying ratio.... *", theSplit.getSplitRatio(), "Shares before:",  row[dataKeys["_SHRSAFTERSPLIT"][_COLUMN]]
                            lWasThereASplit=True
                            row[dataKeys["_SHRSAFTERSPLIT"][_COLUMN]] = row[dataKeys["_SHRSAFTERSPLIT"][_COLUMN]] * theSplit.getSplitRatio()
                            if debug: print securityCurr, " - Shares after:",  row[dataKeys["_SHRSAFTERSPLIT"][_COLUMN]]
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
                    price = ((row[dataKeys["_AMOUNT"][_COLUMN]] / (row[dataKeys["_SHARES"][_COLUMN]])))
                    row[dataKeys["_PRICE"][_COLUMN]] = price
                    price = None

                    if lAdjustForSplits:
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

                if debug: print row
                transactionTable.append(row)
                iCount += 1

            print "Investment Transaction Records selected:", len(transactionTable)
            if iBal: print "...and %s Manual Opening Balance entries created too..." %iBal
            ###########################################################################################################


            #sort the file: Account>Security>Date
            transactionTable = sorted(transactionTable, key=lambda x: (x[dataKeys["_ACCOUNT"][_COLUMN]],
                                                                       x[dataKeys["_DATE"][_COLUMN]]) )

            ###########################################################################################################


            def ExportDataToFile():
                global debug, csvfilename, decimalCharSep, groupingCharSep, csvDelimiter, version, myScriptName
                global transactionTable, userdateformat

                if debug: print "In ", inspect.currentframe().f_code.co_name, "()"

                headings = []
                sortDataFields = sorted(dataKeys.items(), key=lambda x: x[1][_COLUMN])
                for i in sortDataFields:
                    headings.append(i[1][_HEADING])
                print

                if debug: print "Nor pre-processing the file to convert integer dates and strip non-ASCII if requested...."
                for row in transactionTable:
                    dateasdate = datetime.datetime.strptime(str(row[dataKeys["_DATE"][_COLUMN]]),"%Y%m%d")  # Convert to Date field
                    dateoutput = dateasdate.strftime(userdateformat)
                    row[dataKeys["_DATE"][_COLUMN]] = dateoutput

                    if row[dataKeys["_TAXDATE"][_COLUMN]]:
                        dateasdate = datetime.datetime.strptime(str(row[dataKeys["_TAXDATE"][_COLUMN]]),"%Y%m%d")  # Convert to Date field
                        dateoutput = dateasdate.strftime(userdateformat)
                        row[dataKeys["_TAXDATE"][_COLUMN]] = dateoutput

                    for col in range(0, len(row)):
                        row[col] = fixFormatsStr(row[col])

                # NOTE - You can add sep=; to begining of file to tell Excel what delimiter you are using

                # Write the csvlines to a file
                if debug: print "Opening file and writing ", len(transactionTable), "records"
                myPrint("J", "Opening file and writing ", len(transactionTable), " records")

                lFileError = False

                try:
                    # CSV Writer will take care of special characters / delimiters within fields by wrapping in quotes that Excel will decode
                    # with open(csvfilename,"wb") as csvfile:  # PY2.7 has no newline parameter so opening in binary; juse "w" and newline='' in PY3.0
                    with open(csvfilename,"w") as csvfile:  # PY2.7 has no newline parameter so opening in binary; juse "w" and newline='' in PY3.0

                        csvfile.write(codecs.BOM_UTF8) # This 'helps' Excel open file with double-click as UTF-8

                        writer = csv.writer(csvfile, dialect='excel', quoting=csv.QUOTE_MINIMAL, delimiter=csvDelimiter)

                        if csvDelimiter != ",":
                            writer.writerow(["sep=", ""])  # Tells Excel to open file with the alternative delimiter (it will add the delimiter to this line)

                        writer.writerow(headings)  # Print the header, but not the extra _field headings

                        for i in range(0, len(transactionTable)):
                            writer.writerow(transactionTable[i])

                        today = Calendar.getInstance()
                        writer.writerow([""])
                        writer.writerow(["StuWareSoftSystems - " + myScriptName + "("
                                         + version
                                         + ")  MoneyDance Python Script - Date of Extract: "
                                         + str(sdf.format(today.getTime()))])
                    myPrint("B", "CSV file " + csvfilename + " created, records written, and file closed..")

                except IOError, e:
                    myPrint("B", "Oh no - File IO Error!")
                    myPrint("B", e)
                    myPrint("B", sys.exc_type)
                    myPrint("B", "Path:", csvfilename)
                    myPrint("B", "!!! ERROR - No file written - sorry! (was file open, permissions etc?)".upper())
                    lFileError = True


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

        def saveParameters():
            global debug  # Set to True if you want verbose messages, else set to False....
            global hideHiddenSecurities, hideInactiveAccounts, hideHiddenAccounts, lAllCurrency, filterForCurrency
            global lAllSecurity, filterForSecurity, lAllAccounts, filterForAccounts, lStripASCII, csvDelimiter, scriptpath
            global lDisplayOnly, version, myParameters
            global lIncludeOpeningBalances, lAdjustForSplits
            global userdateformat

            if debug: print "In ", inspect.currentframe().f_code.co_name, "()"

            # NOTE: Parameters were loaded earlier on... Preserve existing, and update any used ones...
            # (i.e. other StuWareSoftSystems programs might be sharing the same file)

            if myParameters is None: myParameters = {}

            myParameters["__Author"] = "Stuart Beesley - (c) StuWareSoftSystems"
            myParameters["__extract_investment_transactions"] = version
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
            myParameters["debug"] = debug

            myParameters["lIncludeOpeningBalances"] = lIncludeOpeningBalances
            myParameters["lAdjustForSplits"] = lAdjustForSplits
            myParameters["userdateformat"] = userdateformat


            if not lDisplayOnly and scriptpath != "" and os.path.isdir(scriptpath):
                myParameters["scriptpath"] = scriptpath

            dict_filename = os.path.join("..", "StuWareSoftSystems.dict")
            if debug: print "Will try to save parameter file:", dict_filename

            local_storage = moneydance.getCurrentAccountBook().getLocalStorage()
            ostr = local_storage.openFileForWriting(dict_filename)

            myPrint("J", "about to Pickle.dump and save parameters to file:", dict_filename)

            try:
                save_file = FileUtil.wrap(ostr)
                pickle.dump(myParameters, save_file)
                save_file.close()

                if debug:
                    print "myParameters now contains...:"
                    for key in sorted(myParameters.keys()):
                        print "...variable:", key, myParameters[key]

            except:
                myPrint("B", "Error - failed to create/write parameter file.. Ignoring and continuing.....")
                return

            if debug: print "Parameter file written and parameters saved to disk....."


        # ENDDEF

        saveParameters()


try:
    if debug: print "deleting old objects"
    if "JTextFieldLimitYN" in vars() or "JTextFieldLimitYN" in globals(): del JTextFieldLimitYN
    if "userFilters" in vars() or "userFilters" in globals(): del userFilters
    if "costBasisTable" in vars() or "costBasisTable" in globals(): del transactionTable

except:
    if debug: print "Objects did not exist.."

myPrint("B", "StuWareSoftSystems - ", os.path.basename(__file__), " script ending......")

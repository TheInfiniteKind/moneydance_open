#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# extract_data.py - build: 1005 - February 2021 - Stuart Beesley

# Consolidation of prior scripts into one:
# stockglance2020.py
# extract_reminders_csv.py
# extract_currency_history_csv.py
# extract_account_registers_csv.py
# extract_investment_transactions_csv.py
# #########################################################################################################################
# YES - there is some code inefficiency and duplication here.. It was a toss up between speed of consolidating the scripts,
# or spending a lot of time refining and probably introducing code errors..... This will be refined over time. You will also
# see the evolution of my coding from the first script I created to the last (clearly exposed when consolidated). I make no
# apologies for this, all the functions work well. Over time, I might harmonise / streamline the code......
# #########################################################################################################################
# MIT License
#
# Copyright (c) 2021 Stuart Beesley - StuWareSoftSystems
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

# CREDITS AND THANKS - StockGlance
#  Original StockGlance.java code - James Larus - https://github.com/jameslarus/stockglance
#  Modified to StockGlance75.py - waynelloydsmith - https://github.com/waynelloydsmith/Moneydance-Scripts/blob/master/StockGlance75.py

# CREDITS AND THANKS - Reminders
#  allangdavies - adgetreminderstocsv.py for the original code and concept(s)
#  Mike Enoch (April 2017) and his "swing example-moneydance_edit_reminders.py" script (used for my education)

# This script extracts various data items and can export to a csv file.
# It can also grab, decrypt, and extract/save your attachments
# For Investments and Reminders, it will display on screen (includes stockglance2020)

# Use in Moneydance Menu Window->Show Moneybot Console >> Open Script >> RUN

# Stuart Beesley Created 2021-02-10 tested on MacOS - MD2021 onwards - StuWareSoftSystems....
# Build: 1000 - Initial consolidation of all prior extract scripts
# Build: 1001 - Enhancement to extract_investment_transactions_csv so that accounts with no txns still output the opening balance...
# Build: 1001 - Enhancement to extract_account_registers_csv so that accounts with no txns still output the opening balance...
# Build: 1001 - On both the above, limit the opening balances when created within the date range....
# Build: 1001 - Append date_time to filename - user request....
# Build: 1001 - Enhance stockglance2020 to get cash balances for all accounts when the conditions are correct...
# Build: 1002 - Detect when already running and prevent situation
# Build: 1002 - Fix SG2020 display on account names with non-ascii characters; error trap all extract csv routines
# Build: 1003 - Tweak, block old MD versions
# Build: 1004 - tweak to common code for launch detection
# Build: 1005 - tweak to common code (minor non-functional change)

# Detect another instance of this code running in same namespace - i.e. a Moneydance Extension
# CUSTOMIZE AND COPY THIS ##############################################################################################
# CUSTOMIZE AND COPY THIS ##############################################################################################
# CUSTOMIZE AND COPY THIS ##############################################################################################

myModuleID = u"extract_data"
global extract_data_frame_

global moneydance, moneydance_data, moneydance_ui
global moneydance_extension_loader

from java.lang import System
from javax.swing import JFrame
from java.awt.event import WindowEvent

class MyJFrame(JFrame):

    def __init__(self, frameTitle=None):
        super(JFrame, self).__init__(frameTitle)
        self.myJFrameVersion = 2
        self.isActiveInMoneydance = False
        self.isRunTimeExtension = False
        self.MoneydanceAppListener = None
        self.HomePageViewObj = None

def getMyJFrame( moduleName ):
    try:
        frames = JFrame.getFrames()
        for fr in frames:
            if (fr.getName().lower().startswith(u"%s_main" %moduleName)
                    and type(fr).__name__ == MyJFrame.__name__                         # isinstance() won't work across namespaces
                    and fr.isActiveInMoneydance):
                print("%s: Found live frame: %s (MyJFrame() version: %s)" %(myModuleID,fr.getName(),fr.myJFrameVersion))
                System.err.write("%s: Found live frame: %s (MyJFrame() version: %s)\n" %(myModuleID, fr.getName(),fr.myJFrameVersion))
                if fr.isRunTimeExtension: print("%s: This extension is a run-time self-installed extension too..." %(myModuleID))
                if fr.isRunTimeExtension: System.err.write("%s: This extension is a run-time self-installed extension too...\n" %(myModuleID))
                return fr
    except:
        System.err.write("%s: Critical error in getMyJFrame(); caught and ignoring...!\n" %(myModuleID))
    return None


frameToResurrect = None
try:
    if (u"%s_frame_"%myModuleID in globals()
            and isinstance(extract_data_frame_, MyJFrame)
            and extract_data_frame_.isActiveInMoneydance):
        frameToResurrect = extract_data_frame_
    else:
        getFr = getMyJFrame( myModuleID )
        if getFr is not None:
            frameToResurrect = getFr
        del getFr
except:
    System.err.write("%s: Critical error checking frameToResurrect(1); caught and ignoring...!\n" %(myModuleID))

lTerminatedExtension = False

try:
    if frameToResurrect:  # and it's still alive.....
        if frameToResurrect.isRunTimeExtension:     # this must be an install/reinstall. I need to deactivate and re-register extension...
            print("%s: Detected that runtime extension %s is already running..... Assuming a re-installation... Taking appropriate action..." %(myModuleID, myModuleID))
            System.err.write("%s: Detected that runtime extension %s is already running..... Assuming a re-installation... Taking appropriate action...\n" %(myModuleID, myModuleID))
            frameToResurrect.isActiveInMoneydance = False
            try:
                frameToResurrect.setVisible(False)
                frameToResurrect.dispatchEvent(WindowEvent(frameToResurrect, WindowEvent.WINDOW_CLOSING))
                System.err.write("%s: Pushed a windowClosing event to existing extension... Hopefully it will close to allow re-installation...\n" %(myModuleID))
            except:
                System.err.write("%s: ERROR pushing a windowClosing event to existing extension!\n" %(myModuleID))

            lTerminatedExtension = True
            frameToResurrect = None
        else:
            print("%s: Detected that %s is already running..... Attempting to resurrect.." %(myModuleID, myModuleID))
            System.err.write("%s: Detected that %s is already running..... Attempting to resurrect..\n" %(myModuleID, myModuleID))
except:
    System.err.write("%s: Critical error checking frameToResurrect(2); caught and ignoring...!\n" %(myModuleID))

if float(moneydance.getBuild()) < 1904:     # Check for builds less than 1904 / version < 2019.4
    try:
        moneydance.getUI().showInfoMessage("SORRY YOUR VERSION IS TOO OLD FOR THIS SCRIPT/EXTENSION")
    except:
        raise Exception("SORRY YOUR MONEYDANCE VERSION IS TOO OLD FOR THIS SCRIPT/EXTENSION")

elif frameToResurrect:
    try:
        frameToResurrect.setVisible(True)
        if frameToResurrect.getExtendedState() == JFrame.ICONIFIED:
            frameToResurrect.setExtendedState(JFrame.NORMAL)
        frameToResurrect.toFront()
    except:
        print("%s: Failed to resurrect main Frame.. This duplicate Script/extension is now terminating....." %(myModuleID))
        System.err.write("%s: Failed to resurrect main Frame.. This duplicate Script/extension is now terminating.....\n" %(myModuleID))
        raise Exception("SORRY - YOU CAN ONLY HAVE ONE INSTANCE OF %s RUNNING AT ONCE" %(myModuleID.upper()))

else:
    del frameToResurrect

    if not lTerminatedExtension:
        print("%s: No other 'live' instances of this program detected (or I terminated it) - running as normal" %(myModuleID))
        System.err.write("%s: No other instances of this program detected (or I terminated it) - running as normal\n" %(myModuleID))
    else:
        print("%s: I terminated extension in memory, running script to allow new installation..." %(myModuleID))
        System.err.write("%s: I terminated extension in memory, running script to allow new installation...\n" %(myModuleID))

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

    from java.awt import Color, Dimension, FileDialog, FlowLayout, Toolkit, Font, GridBagLayout, GridLayout
    from java.awt import BorderLayout, Dialog, Insets
    from java.awt.event import KeyEvent, WindowAdapter, InputEvent
    from java.util import Date

    from java.text import DecimalFormat, SimpleDateFormat
    from java.util import Calendar, ArrayList
    from java.lang import Double, Math, Character
    from java.io import FileNotFoundException, FilenameFilter, File, FileInputStream, FileOutputStream, IOException, StringReader
    from java.io import BufferedReader, InputStreamReader
    if isinstance(None, (JDateField,CurrencyUtil,Reminder,ParentTxn,SplitTxn,TxnSearch, JComboBox, JCheckBox,
                         JTextArea, JMenuBar, JMenu, JMenuItem, JCheckBoxMenuItem, JFileChooser, JDialog,
                         JButton, FlowLayout, InputEvent, ArrayList, File, IOException, StringReader, BufferedReader,
                         InputStreamReader, Dialog, JTable, BorderLayout, Double, InvestUtil, JRadioButton, ButtonGroup,
                         AccountUtil, AcctFilter, CurrencyType, Account, TxnUtil, JScrollPane, WindowConstants, JFrame,
                         JComponent, KeyStroke, AbstractAction, UIManager, Color, Dimension, Toolkit, KeyEvent,
                         WindowAdapter, CustomDateFormat, SimpleDateFormat, Insets, FileDialog)): pass
    if codecs.BOM_UTF8 is not None: pass
    if csv.QUOTE_ALL is not None: pass
    if datetime.MINYEAR is not None: pass
    if Math.max(1,1): pass
    # END COMMON IMPORTS ###################################################################################################

    # COMMON GLOBALS #######################################################################################################
    global debug  # Set to True if you want verbose messages, else set to False....
    global myParameters, myScriptName, version_build, _resetParameters, i_am_an_extension_so_run_headless, moneydanceIcon
    global lPickle_version_warning, decimalCharSep, groupingCharSep, lIamAMac, lGlobalErrorDetected
    global MYPYTHON_DOWNLOAD_URL
    # END COMMON GLOBALS ###################################################################################################

    # SET THESE VARIABLES FOR ALL SCRIPTS ##################################################################################
    version_build = "1005"                                                                                              # noqa
    myScriptName = u"%s.py(Extension)" %myModuleID                                                                      # noqa
    debug = False                                                                                                       # noqa
    myParameters = {}                                                                                                   # noqa
    _resetParameters = False                                                                                            # noqa
    lPickle_version_warning = False                                                                                     # noqa
    lIamAMac = False                                                                                                    # noqa
    lGlobalErrorDetected = False																						# noqa
    MYPYTHON_DOWNLOAD_URL = "https://yogi1967.github.io/MoneydancePythonScripts/"                                       # noqa
    # END SET THESE VARIABLES FOR ALL SCRIPTS ##############################################################################

    # >>> THIS SCRIPT'S IMPORTS ############################################################################################

    # from extract_account_registers_csv & extract_investment_transactions_csv
    from copy import deepcopy
    import subprocess
    from com.moneydance.apps.md.controller import Util
    from com.moneydance.apps.md.view.gui import ConsoleWindow
    # from com.infinitekind.moneydance.model import DateRange

    # from stockglance2020 and extract_reminders_csv
    from java.awt.event import AdjustmentListener
    from java.text import NumberFormat, SimpleDateFormat
    from com.moneydance.apps.md.view.gui import EditRemindersWindow
    from java.awt.event import MouseAdapter
    from java.util import Comparator
    from javax.swing import SortOrder, ListSelectionModel
    from javax.swing.table import DefaultTableCellRenderer, DefaultTableModel, TableRowSorter
    from javax.swing.border import CompoundBorder, MatteBorder
    from javax.swing.event import TableColumnModelListener
    from java.lang import String, Number
    from java.awt.event import WindowEvent
    from java.lang import Runnable, Thread
    from com.moneydance.apps.md.controller import AppEventListener

    # from extract_currency_history
    # <none>

    # >>> END THIS SCRIPT'S IMPORTS ########################################################################################

    # >>> THIS SCRIPT'S GLOBALS ############################################################################################

    # Saved to parameters file

    # Common
    global __extract_data, extract_data_frame_, extract_filename
    global lStripASCII, scriptpath, csvDelimiter, userdateformat, lWriteBOMToExportFile_SWSS
    global hideInactiveAccounts, hideHiddenAccounts, hideHiddenSecurities
    global lAllSecurity, filterForSecurity, lAllAccounts, filterForAccounts, lAllCurrency, filterForCurrency
    global whichDefaultExtractToRun_SWSS

    # from extract_account_registers_csv
    global lIncludeSubAccounts_EAR
    global lIncludeOpeningBalances_EAR
    global userdateStart_EAR, userdateEnd_EAR
    global lAllTags_EAR, tagFilter_EAR, lExtractAttachments_EAR
    global saveDropDownAccountUUID_EAR, lIncludeInternalTransfers_EAR, saveDropDownDateRange_EAR
    global lAllText_EAR, textFilter_EAR

    # from extract_investment_transactions_csv
    global lIncludeOpeningBalances, lAdjustForSplits
    global lExtractAttachments_EIT

    # from stockglance2020
    global lIncludeCashBalances, _column_widths_SG2020
    global lSplitSecuritiesByAccount, lExcludeTotalsFromCSV, lRoundPrice
    global lIncludeFutureBalances_SG2020

    # from extract_reminders_csv
    global _column_widths_ERTC

    # from extract_currency_history
    global lSimplify_ECH, userdateStart_ECH, userdateEnd_ECH, hideHiddenCurrencies_ECH

    # ------------
    # Other used by program(s)
    global csvfilename, lDisplayOnly
    global baseCurrency, sdf

    # from extract_account_registers_csv & extract_investment_transactions_csv
    global transactionTable, dataKeys, attachmentDir, relativePath, lDidIUseAttachmentDir

    # from stockglance2020
    global rawDataTable, rawFooterTable, headingNames
    global StockGlanceInstance
    global _SHRS_FORMATTED, _SHRS_RAW, _PRICE_FORMATTED, _PRICE_RAW, _CVALUE_FORMATTED, _CVALUE_RAW, _BVALUE_FORMATTED, _BVALUE_RAW
    global _CBVALUE_FORMATTED, _CBVALUE_RAW, _GAIN_FORMATTED, _GAIN_RAW, _SORT, _EXCLUDECSV, _GAINPCT
    global acctSeparator

    # from extract_reminders_csv & extract_currency_history
    global csvlines, csvheaderline, headerFormats
    global table, focus, row, scrollpane, EditedReminderCheck, ReminderTable_Count, ExtractDetails_Count

    # >>> END THIS SCRIPT'S GLOBALS ############################################################################################

    # Set programmatic defaults/parameters for filters HERE.... Saved Parameters will override these now
    # NOTE: You  can override in the pop-up screen

    # Common
    scriptpath = ""																										# noqa
    csvDelimiter = ","																									# noqa
    userdateformat = "%Y/%m/%d"                                                                                         # noqa
    extract_filename="SELECT_FILENAME.csv"                                                                              # noqa
    lStripASCII = False                                                                                                 # noqa
    attachmentDir = ""                                                                                                  # noqa
    lDidIUseAttachmentDir = False                                                                                       # noqa
    lWriteBOMToExportFile_SWSS = True                                                                                   # noqa
    hideInactiveAccounts = True                                                                                         # noqa
    hideHiddenAccounts = True                                                                                           # noqa
    lAllAccounts = True                                                                                                 # noqa
    filterForAccounts = "ALL"                                                                                           # noqa
    hideHiddenSecurities = True                                                                                         # noqa
    lAllSecurity = True                                                                                                 # noqa
    filterForSecurity = "ALL"                                                                                           # noqa
    lAllCurrency = True                                                                                                 # noqa
    filterForCurrency = "ALL"                                                                                           # noqa
    whichDefaultExtractToRun_SWSS = None                                                                                # noqa

    # from extract_account_registers_csv
    lIncludeSubAccounts_EAR = False                                                                                     # noqa
    lIncludeOpeningBalances_EAR = True                                                                                  # noqa
    userdateStart_EAR = 19600101                                                                                        # noqa
    userdateEnd_EAR = 20301231                                                                                          # noqa
    lAllTags_EAR = True                                                                                                 # noqa
    tagFilter_EAR = "ALL"                                                                                               # noqa
    lAllText_EAR = True                                                                                                 # noqa
    textFilter_EAR = "ALL"                                                                                              # noqa
    lExtractAttachments_EAR=False                                                                                       # noqa
    saveDropDownAccountUUID_EAR = ""                                                                                    # noqa
    saveDropDownDateRange_EAR = ""                                                                                      # noqa
    lIncludeInternalTransfers_EAR = True                                                                                # noqa

    # from extract_investment_transactions_csv
    lIncludeOpeningBalances = True                                                                                      # noqa
    lAdjustForSplits = True                                                                                             # noqa
    lExtractAttachments_EIT=False                                                                                       # noqa

    # from stockglance2020
    lIncludeCashBalances = False                                                                                        # noqa
    lSplitSecuritiesByAccount = False                                                                                   # noqa
    lExcludeTotalsFromCSV = False                                                                                       # noqa
    lIncludeFutureBalances_SG2020 = False                                                                               # noqa
    lRoundPrice = True                                                                                                  # noqa
    _column_widths_SG2020 = []                                                                                          # noqa
    headingNames = ""                                                                                                   # noqa
    acctSeparator = u' : '                                                                                              # noqa

    # from extract_reminders_csv
    _column_widths_ERTC = []                                                                                          	# noqa

    # extract_currency_history
    lSimplify_ECH = False                                                                                               # noqa
    userdateStart_ECH = 19600101                                                                                        # noqa
    userdateEnd_ECH = 20301231                                                                                          # noqa
    hideHiddenCurrencies_ECH = True                                                                                     # noqa
    # >>> END THIS SCRIPT'S GLOBALS ############################################################################################

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
Thank you for using %s! The author has other useful Extensions / Moneybot Python scripts available...:

Extension (.mxt) format only:
toolbox                                 View Moneydance settings, diagnostics, fix issues, change settings and much more

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

    def is_moneydance_loaded_properly():
        global debug

        if debug or moneydance is None or moneydance_data is None or moneydance_ui is None:
            for theClass in ["moneydance",  moneydance], ["moneydance_ui",moneydance_ui], ["moneydance_data",moneydance]:
                myPrint("B","Moneydance Objects now....: Class: %s %s@{:x}".format(System.identityHashCode(theClass[1])) %(pad(theClass[0],20), theClass[1].__class__))
            myPrint("P","")

        if moneydance is not None and moneydance_data is not None and moneydance_ui is not None:                        # noqa
            if debug: myPrint("B","Success - Moneydance variables are already set....")
            return

        myPrint("B","ERROR - Moneydance variables are NOT set properly....!")

        # to cope with being run as Extension.... temporary
        if moneydance is not None and (moneydance_data is None or moneydance_ui is None):                                # noqa
            myPrint("B", "@@@ Moneydance variables not set (run as extension?) - attempting to manually set @@@")

            try:
                exec "global moneydance_ui;" + "moneydance_ui=moneydance.getUI();"
            except:
                myPrint("B","Failed to set moneydance_ui... This is a critical failure... (perhaps a run-time extension and too early - will continue)!")
                # raise

            try:
                exec "global moneydance_data;" + "moneydance_data=moneydance.getCurrentAccount().getBook();"
            except:
                myPrint("B","Failed to set moneydance_data... I expect I am executing at MD runtime to self-install as a FeatureModule extension.. no matter...")

        for theClass in ["moneydance",moneydance], ["moneydance_ui",moneydance_ui], ["moneydance_data",moneydance]:
            myPrint("B","Moneydance Objects after manual setting....: Class: %s %s@{:x}".format(System.identityHashCode(theClass[1])) %(pad(theClass[0],20), theClass[1].__class__))
        myPrint("P","")

        return

    is_moneydance_loaded_properly()

    def getMonoFont():
        global debug

        try:
            theFont = moneydance.getUI().getFonts().code
            # if debug: myPrint("B","Success setting Font set to Moneydance code: %s" %theFont)
        except:
            theFont = Font("monospaced", Font.PLAIN, 15)
            if debug: myPrint("B","Failed to Font set to Moneydance code - So using: %s" %theFont)

        return theFont

    def getTheSetting(what):
        x = moneydance.getPreferences().getSetting(what, None)
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

    # Copies Moneydance_ui.showInfoMessage
    def myPopupInformationBox(theParent=None, theMessage="What no message?!", theTitle="Info", theMessageType=JOptionPane.INFORMATION_MESSAGE):

        if theParent is None:
            if theMessageType == JOptionPane.PLAIN_MESSAGE or theMessageType == JOptionPane.INFORMATION_MESSAGE:
                icon_to_use=moneydance.getUI().getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png")
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
            moneydance.getUI().saveToBackup(None)
            return True

        elif response == 1:
            myPrint("B", "User DECLINED to perform Export Backup before update/fix...!")
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
                icon_to_use=moneydance.getUI().getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png")

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
                icon_to_use=moneydance.getUI().getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png")

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
                self.fakeJFrame = MyJFrame()
                self.fakeJFrame.setName(u"%s_fake_dialog" %(myModuleID))
                self.fakeJFrame.setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE)
                self.fakeJFrame.setUndecorated(True)
                self.fakeJFrame.setVisible( False )
                if not Platform.isOSX():
                    self.fakeJFrame.setIconImage(MDImages.getImage(moneydance.getSourceInformation().getIconResource()))

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
            self._popup_d.getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0), "close-window")
            self._popup_d.getRootPane().getActionMap().put("close-window", self.CancelButtonAction(self._popup_d, self.fakeJFrame,self.lResult))
            self._popup_d.addWindowListener(self.WindowListener(self._popup_d, self.fakeJFrame,self.lResult))

            if (not Platform.isMac()):
                # moneydance_ui.getImages()
                self._popup_d.setIconImage(MDImages.getImage(moneydance.getSourceInformation().getIconResource()))

            displayJText = JTextArea(self.theMessage)
            displayJText.setFont( getMonoFont() )
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
            moneydance.getUI().getSounds().playSound("cash_register.wav")
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
        moneydanceIcon = MDImages.getImage(moneydance.getSourceInformation().getIconResource())
    except:
        moneydanceIcon = None

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

        myFont = moneydance.getUI().getFonts().defaultText

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

        return

    if moneydance_ui is not None:
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
            homeDir = moneydance.getCurrentAccountBook().getRootFolder().getParent()  # Better than nothing!

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
        migratedFilename = os.path.join(moneydance.getCurrentAccountBook().getRootFolder().getAbsolutePath(),myFile)

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

    def save_StuWareSoftSystems_parameters_to_file(myFile="StuWareSoftSystems.dict"):
        global debug, myParameters, lPickle_version_warning, version_build

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )

        if myParameters is None: myParameters = {}

        # Don't forget, any parameters loaded earlier will be preserved; just add changed variables....
        myParameters["__Author"] = "Stuart Beesley - (c) StuWareSoftSystems"
        myParameters["debug"] = debug

        dump_StuWareSoftSystems_parameters_from_memory()

        # Pickle was originally encrypted, no need, migrating to unencrypted
        migratedFilename = os.path.join(moneydance.getCurrentAccountBook().getRootFolder().getAbsolutePath(),myFile)

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
        frames = JFrame.getFrames()
        for fr in frames:
            if fr.getName().lower().startswith(moduleName):
                myPrint("DB","Found old frame %s and active status is: %s" %(fr.getName(),fr.isActiveInMoneydance))
                # if fr.isActiveInMoneydance:
                try:
                    fr.isActiveInMoneydance = False
                    fr.setVisible(False)
                    fr.dispose()    # This should call windowClosed() which should remove MD listeners.....
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

    # END COMMON DEFINITIONS ###############################################################################################
    # END COMMON DEFINITIONS ###############################################################################################
    # END COMMON DEFINITIONS ###############################################################################################

    # >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
    # >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
    # >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
    def load_StuWareSoftSystems_parameters_into_memory():

        global debug, myParameters, lPickle_version_warning, version_build

        # >>> THESE ARE THIS SCRIPT's PARAMETERS TO LOAD

        # common
        global __extract_data
        global lWriteBOMToExportFile_SWSS, userdateformat, lStripASCII, csvDelimiter, scriptpath
        global lAllCurrency, filterForCurrency
        global hideHiddenSecurities, lAllSecurity, filterForSecurity
        global hideInactiveAccounts, hideHiddenAccounts, lAllAccounts, filterForAccounts
        global whichDefaultExtractToRun_SWSS

        # extract_account_registers_csv
        global lIncludeOpeningBalances_EAR
        global userdateStart_EAR, userdateEnd_EAR, lIncludeSubAccounts_EAR
        global lAllTags_EAR, tagFilter_EAR, lExtractAttachments_EAR
        global saveDropDownAccountUUID_EAR, lIncludeInternalTransfers_EAR, saveDropDownDateRange_EAR
        global lAllText_EAR, textFilter_EAR

        # extract_investment_transactions_csv
        global lIncludeOpeningBalances, lAdjustForSplits, lExtractAttachments_EIT

        # extract_currency_history_csv
        global lSimplify_ECH, userdateStart_ECH, userdateEnd_ECH, hideHiddenCurrencies_ECH

        # stockglance2020
        global lIncludeCashBalances
        global lSplitSecuritiesByAccount, lExcludeTotalsFromCSV, lRoundPrice, _column_widths_SG2020, lIncludeFutureBalances_SG2020

        # extract_reminders_csv
        global _column_widths_ERTC

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )
        myPrint("DB", "Loading variables into memory...")

        if myParameters is None: myParameters = {}


        # Delete superseded version keys from file - stops Toolbox complaining
        for deleteObsoleteKey in ["__extract_account_registers",
                                  "__extract_investment_transactions",
                                  "__extract_currency_history_csv",
                                  "__StockGlance2020",
                                  "__stockglance2020",
                                  "__extract_reminders_to_csv",
                                  "__extract_reminders_csv"]:

            if myParameters.get(deleteObsoleteKey) is not None:
                myPrint("B", "@@ Detected old %s extract version key... Will delete it..." %(deleteObsoleteKey))
                myParameters.pop(deleteObsoleteKey, None)  # Obsoleted extract version key - delete from parameter file


        # common
        if myParameters.get("__extract_data") is not None: __extract_data = myParameters.get("__extract_data")
        if myParameters.get("hideHiddenSecurities") is not None: hideHiddenSecurities = myParameters.get("hideHiddenSecurities")
        if myParameters.get("lAllSecurity") is not None: lAllSecurity = myParameters.get("lAllSecurity")
        if myParameters.get("filterForSecurity") is not None: filterForSecurity = myParameters.get("filterForSecurity")
        if myParameters.get("hideInactiveAccounts") is not None: hideInactiveAccounts = myParameters.get("hideInactiveAccounts")
        if myParameters.get("hideHiddenAccounts") is not None: hideHiddenAccounts = myParameters.get("hideHiddenAccounts")
        if myParameters.get("lAllAccounts") is not None: lAllAccounts = myParameters.get("lAllAccounts")
        if myParameters.get("filterForAccounts") is not None: filterForAccounts = myParameters.get("filterForAccounts")
        if myParameters.get("lAllCurrency") is not None: lAllCurrency = myParameters.get("lAllCurrency")
        if myParameters.get("filterForCurrency") is not None: filterForCurrency = myParameters.get("filterForCurrency")
        if myParameters.get("lStripASCII") is not None: lStripASCII = myParameters.get("lStripASCII")
        if myParameters.get("csvDelimiter") is not None: csvDelimiter = myParameters.get("csvDelimiter")
        if myParameters.get("userdateformat") is not None: userdateformat = myParameters.get("userdateformat")
        if myParameters.get("lWriteBOMToExportFile_SWSS") is not None: lWriteBOMToExportFile_SWSS = myParameters.get("lWriteBOMToExportFile_SWSS")                                                                                  # noqa
        if myParameters.get("whichDefaultExtractToRun_SWSS") is not None: whichDefaultExtractToRun_SWSS = myParameters.get("whichDefaultExtractToRun_SWSS")                                                                                  # noqa

        # extract_account_registers_csv
        if myParameters.get("lIncludeSubAccounts_EAR") is not None: lIncludeSubAccounts_EAR = myParameters.get("lIncludeSubAccounts_EAR")
        if myParameters.get("userdateStart_EAR") is not None: userdateStart_EAR = myParameters.get("userdateStart_EAR")
        if myParameters.get("userdateEnd_EAR") is not None: userdateEnd_EAR = myParameters.get("userdateEnd_EAR")
        if myParameters.get("lAllTags_EAR") is not None: lAllTags_EAR = myParameters.get("lAllTags_EAR")
        if myParameters.get("tagFilter_EAR") is not None: tagFilter_EAR = myParameters.get("tagFilter_EAR")
        if myParameters.get("lAllText_EAR") is not None: lAllText_EAR = myParameters.get("lAllText_EAR")
        if myParameters.get("textFilter_EAR") is not None: textFilter_EAR = myParameters.get("textFilter_EAR")
        if myParameters.get("lExtractAttachments_EAR") is not None: lExtractAttachments_EAR = myParameters.get("lExtractAttachments_EAR")
        if myParameters.get("lIncludeOpeningBalances_EAR") is not None: lIncludeOpeningBalances_EAR = myParameters.get("lIncludeOpeningBalances_EAR")
        if myParameters.get("saveDropDownAccountUUID_EAR") is not None: saveDropDownAccountUUID_EAR = myParameters.get("saveDropDownAccountUUID_EAR")                                                                                  # noqa
        if myParameters.get("saveDropDownDateRange_EAR") is not None: saveDropDownDateRange_EAR = myParameters.get("saveDropDownDateRange_EAR")                                                                                  # noqa
        if myParameters.get("lIncludeInternalTransfers_EAR") is not None: lIncludeInternalTransfers_EAR = myParameters.get("lIncludeInternalTransfers_EAR")                                                                                  # noqa

        # extract_investment_transactions_csv
        if myParameters.get("lIncludeOpeningBalances") is not None: lIncludeOpeningBalances = myParameters.get("lIncludeOpeningBalances")
        if myParameters.get("lAdjustForSplits") is not None: lAdjustForSplits = myParameters.get("lAdjustForSplits")
        if myParameters.get("lExtractAttachments_EIT") is not None: lExtractAttachments_EIT = myParameters.get("lExtractAttachments_EIT")                                                                                  # noqa

        # extract_currency_history_csv
        if myParameters.get("lSimplify_ECH") is not None: lSimplify_ECH = myParameters.get("lSimplify_ECH")
        if myParameters.get("userdateStart_ECH") is not None: userdateStart_ECH = myParameters.get("userdateStart_ECH")
        if myParameters.get("userdateEnd_ECH") is not None: userdateEnd_ECH = myParameters.get("userdateEnd_ECH")
        if myParameters.get("hideHiddenCurrencies_ECH") is not None: hideHiddenCurrencies_ECH = myParameters.get("hideHiddenCurrencies_ECH")

        # stockglance2020
        if myParameters.get("lIncludeCashBalances") is not None: lIncludeCashBalances = myParameters.get("lIncludeCashBalances")
        if myParameters.get("lSplitSecuritiesByAccount") is not None: lSplitSecuritiesByAccount = myParameters.get("lSplitSecuritiesByAccount")
        if myParameters.get("lExcludeTotalsFromCSV") is not None: lExcludeTotalsFromCSV = myParameters.get("lExcludeTotalsFromCSV")
        if myParameters.get("lIncludeFutureBalances_SG2020") is not None: lIncludeFutureBalances_SG2020 = myParameters.get("lIncludeFutureBalances_SG2020")
        if myParameters.get("lDontRoundPrice") is not None: lRoundPrice = myParameters.get("lDontRoundPrice")
        if myParameters.get("_column_widths_SG2020") is not None: _column_widths_SG2020 = myParameters.get("_column_widths_SG2020")

        # extract_reminders_csv
        if myParameters.get("_column_widths_ERTC") is not None: _column_widths_ERTC = myParameters.get("_column_widths_ERTC")

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

        # >>> THESE ARE THIS SCRIPT's PARAMETERS TO LOAD

        # common
        global __extract_data
        global lWriteBOMToExportFile_SWSS, userdateformat, lStripASCII, csvDelimiter, scriptpath
        global lAllCurrency, filterForCurrency
        global hideHiddenSecurities, lAllSecurity, filterForSecurity
        global hideInactiveAccounts, hideHiddenAccounts, lAllAccounts, filterForAccounts
        global whichDefaultExtractToRun_SWSS

        # extract_account_registers_csv
        global lIncludeOpeningBalances_EAR
        global userdateStart_EAR, userdateEnd_EAR, lIncludeSubAccounts_EAR
        global lAllTags_EAR, tagFilter_EAR, lExtractAttachments_EAR
        global saveDropDownAccountUUID_EAR, lIncludeInternalTransfers_EAR, saveDropDownDateRange_EAR
        global lAllText_EAR, textFilter_EAR

        # extract_investment_transactions_csv
        global lIncludeOpeningBalances, lAdjustForSplits, lExtractAttachments_EIT

        # extract_currency_history_csv
        global lSimplify_ECH, userdateStart_ECH, userdateEnd_ECH, hideHiddenCurrencies_ECH

        # stockglance2020
        global lIncludeCashBalances
        global lSplitSecuritiesByAccount, lExcludeTotalsFromCSV, lRoundPrice, _column_widths_SG2020, lIncludeFutureBalances_SG2020

        # extract_reminders_csv
        global _column_widths_ERTC

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )

        # NOTE: Parameters were loaded earlier on... Preserve existing, and update any used ones...
        # (i.e. other StuWareSoftSystems programs might be sharing the same file)

        if myParameters is None: myParameters = {}

        # common
        myParameters["__extract_data"] = version_build
        myParameters["lStripASCII"] = lStripASCII
        myParameters["csvDelimiter"] = csvDelimiter
        myParameters["lWriteBOMToExportFile_SWSS"] = lWriteBOMToExportFile_SWSS
        myParameters["whichDefaultExtractToRun_SWSS"] = whichDefaultExtractToRun_SWSS
        myParameters["userdateformat"] = userdateformat
        myParameters["hideInactiveAccounts"] = hideInactiveAccounts
        myParameters["hideHiddenAccounts"] = hideHiddenAccounts
        myParameters["lAllAccounts"] = lAllAccounts
        myParameters["filterForAccounts"] = filterForAccounts
        myParameters["lAllCurrency"] = lAllCurrency
        myParameters["filterForCurrency"] = filterForCurrency
        myParameters["hideHiddenSecurities"] = hideHiddenSecurities
        myParameters["lAllSecurity"] = lAllSecurity
        myParameters["filterForSecurity"] = filterForSecurity

        # extract_account_registers_csv
        myParameters["lIncludeSubAccounts_EAR"] = lIncludeSubAccounts_EAR
        myParameters["lIncludeOpeningBalances_EAR"] = lIncludeOpeningBalances_EAR
        myParameters["userdateStart_EAR"] = userdateStart_EAR
        myParameters["userdateEnd_EAR"] = userdateEnd_EAR
        myParameters["lAllTags_EAR"] = lAllTags_EAR
        myParameters["tagFilter_EAR"] = tagFilter_EAR
        myParameters["lAllText_EAR"] = lAllText_EAR
        myParameters["textFilter_EAR"] = textFilter_EAR
        myParameters["lExtractAttachments_EAR"] = lExtractAttachments_EAR
        myParameters["lIncludeInternalTransfers_EAR"] = lIncludeInternalTransfers_EAR
        myParameters["saveDropDownAccountUUID_EAR"] = saveDropDownAccountUUID_EAR
        myParameters["saveDropDownDateRange_EAR"] = saveDropDownDateRange_EAR

        # extract_investment_transactions_csv
        myParameters["lExtractAttachments_EIT"] = lExtractAttachments_EIT
        myParameters["lIncludeOpeningBalances"] = lIncludeOpeningBalances
        myParameters["lAdjustForSplits"] = lAdjustForSplits

        # extract_currency_history_csv
        myParameters["lSimplify_ECH"] = lSimplify_ECH
        myParameters["userdateStart_ECH"] = userdateStart_ECH
        myParameters["userdateEnd_ECH"] = userdateEnd_ECH
        myParameters["hideHiddenCurrencies_ECH"] = hideHiddenCurrencies_ECH

        # stockglance2020
        myParameters["lIncludeCashBalances"] = lIncludeCashBalances
        myParameters["lSplitSecuritiesByAccount"] = lSplitSecuritiesByAccount
        myParameters["lExcludeTotalsFromCSV"] = lExcludeTotalsFromCSV
        myParameters["lIncludeFutureBalances_SG2020"] = lIncludeFutureBalances_SG2020
        myParameters["lDontRoundPrice"] = lRoundPrice
        myParameters["_column_widths_SG2020"] = _column_widths_SG2020

        # extract_reminders_csv
        myParameters["_column_widths_ERTC"] = _column_widths_ERTC

        if not lDisplayOnly and scriptpath != "" and os.path.isdir(scriptpath):
            myParameters["scriptpath"] = scriptpath

        myPrint("DB","variables dumped from memory back into myParameters{}.....")

        return


    get_StuWareSoftSystems_parameters_from_file()
    myPrint("DB", "DEBUG IS ON..")

    # clear up any old left-overs....
    destroyOldFrames(myModuleID)

    # END ALL CODE COPY HERE ###############################################################################################
    # END ALL CODE COPY HERE ###############################################################################################
    # END ALL CODE COPY HERE ###############################################################################################

    if moneydance_data is None:
        myPrint("B", "Moneydance appears to be empty - no data to scan - aborting...")
        myPopupInformationBox(None,"Moneydance appears to be empty - no data to scan - aborting...","EMPTY DATASET")
        raise(Exception("Moneydance appears to be empty - no data to scan - aborting..."))

    moneydance_ui.firstMainFrame.setStatus(">> StuWareSoftSystems - %s launching......." %(myScriptName),0)

    # Create fake JFrame() so that all popups have correct Moneydance Icons etc
    JFrame.setDefaultLookAndFeelDecorated(True)
    extract_data_frame_ = MyJFrame()
    extract_data_frame_.setName(u"%s_fake" %(myModuleID))
    if (not Platform.isMac()):
        moneydance_ui.getImages()
        extract_data_frame_.setIconImage(MDImages.getImage(moneydance_ui.getMain().getSourceInformation().getIconResource()))
    extract_data_frame_.setVisible(False)
    extract_data_frame_.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE)

    csvfilename = None

    if decimalCharSep != "." and csvDelimiter == ",": csvDelimiter = ";"  # Override for EU countries or where decimal point is actually a comma...
    myPrint("DB", "Decimal point:", decimalCharSep, "Grouping Separator", groupingCharSep, "CSV Delimiter set to:", csvDelimiter)

    sdf = SimpleDateFormat("dd/MM/yyyy")

    saveColor = JLabel("TEST").getForeground()

    lExit = False
    lDisplayOnly = False

    if True:
        userFilters = JPanel(GridLayout(0, 1))
        user_stockglance2020 = JRadioButton("StockGlance2020 - display consolidated stock info on screen and/or extract to csv", False)
        user_reminders = JRadioButton("Reminders - display on screen, and/or extract to csv", False)
        user_account_txns = JRadioButton("Account register transactions - extract to csv (attachments optional)", False)
        user_investment_txns = JRadioButton("Investment transactions - extract to csv (attachments optional)", False)
        user_price_history = JRadioButton("Currency price history - extract to csv (simple or detailed formats)", False)

        bg = ButtonGroup()
        bg.add(user_stockglance2020)
        bg.add(user_reminders)
        bg.add(user_account_txns)
        bg.add(user_investment_txns)
        bg.add(user_price_history)
        bg.clearSelection()

        if whichDefaultExtractToRun_SWSS is not None:
            if whichDefaultExtractToRun_SWSS == "_SG2020": user_stockglance2020.setSelected(True)
            elif whichDefaultExtractToRun_SWSS == "_ERTC": user_reminders.setSelected(True)
            elif whichDefaultExtractToRun_SWSS == "_EAR": user_account_txns.setSelected(True)
            elif whichDefaultExtractToRun_SWSS == "_EIT": user_investment_txns.setSelected(True)
            elif whichDefaultExtractToRun_SWSS == "_ECH": user_price_history.setSelected(True)

        userFilters.add(user_stockglance2020)
        userFilters.add(user_reminders)
        userFilters.add(user_account_txns)
        userFilters.add(user_investment_txns)
        userFilters.add(user_price_history)

        lExtractStockGlance2020 = lExtractReminders = lExtractAccountTxns = lExtractInvestmentTxns = lExtractCurrencyHistory = False

        while True:
            options = ["EXIT", "PROCEED"]
            userAction = (JOptionPane.showOptionDialog(extract_data_frame_,
                                                       userFilters,
                                                       "StuWareSoftSystems EXTRACT DATA (build %s) - SELECT OPTION" %(version_build),
                                                       JOptionPane.OK_CANCEL_OPTION,
                                                       JOptionPane.QUESTION_MESSAGE,
                                                       moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                       options,
                                                       options[0]))
            if userAction != 1:
                myPrint("B","User chose to exit....")
                lExit = True
                break

            if user_stockglance2020.isSelected():
                myPrint("B","StockGlance2020 investment extract option has been chosen")
                lExtractStockGlance2020 = True
                break

            if user_reminders.isSelected():
                myPrint("B","Reminders display / extract option has been chosen")
                lExtractReminders = True
                break

            if user_account_txns.isSelected():
                myPrint("B","Account Transactions extract option has been chosen")
                lExtractAccountTxns = True
                break

            if user_investment_txns.isSelected():
                myPrint("B","Investment Transactions extract option has been chosen")
                lExtractInvestmentTxns = True
                break

            if user_price_history.isSelected():
                myPrint("B","Currency Price History extract option has been chosen")
                lExtractCurrencyHistory = True
                break

            continue

        if user_stockglance2020.isSelected():   whichDefaultExtractToRun_SWSS = "_SG2020"
        elif user_reminders.isSelected():       whichDefaultExtractToRun_SWSS = "_ERTC"
        elif user_account_txns.isSelected():    whichDefaultExtractToRun_SWSS = "_EAR"
        elif user_investment_txns.isSelected(): whichDefaultExtractToRun_SWSS = "_EIT"
        elif user_price_history.isSelected():   whichDefaultExtractToRun_SWSS = "_ECH"
        else:                                   whichDefaultExtractToRun_SWSS = None

        del options, bg, userFilters, user_stockglance2020, user_reminders, user_account_txns, user_investment_txns, user_price_history

    if lExit:
        myPrint("B", "User chose to cancel at extract choice screen.... exiting")
        myPopupInformationBox(extract_data_frame_, "User chose to cancel at extract choice screen.... exiting", "FILE EXPORT")

    if not lExit:

        if lExtractAccountTxns:
            # ##############################################
            # EXTRACT_ACCOUNT_REGISTERS_CSV PARAMETER SCREEN
            # ##############################################

            dropDownAccount_EAR = None

            userFilters = JPanel(GridLayout(0, 2))

            class PanelAction(AbstractAction):

                def __init__(self, thePanel):
                    self.thePanel=thePanel

                def actionPerformed(self, event):
                    global extract_data_frame_, debug
                    myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event)

                    theDateRangeDropDown = None
                    theAccountDropdown = None
                    theStartDate = None
                    theEndDate = None

                    theSubAccounts = None
                    theHideInactiveAccounts = None
                    theHideHiddenAccounts = None
                    theFilterAccounts = None
                    theFilterCurrency = None

                    _components = self.thePanel.getComponents()
                    for _theComponent in _components:
                        if isinstance(_theComponent, (JComboBox, JTextField, JCheckBox)):
                            if event.getSource().getName() == _theComponent.getName():
                                if _theComponent.getName() == "dateDropdown": theDateRangeDropDown  = _theComponent
                                if _theComponent.getName() == "accountDropdown": theAccountDropdown  = _theComponent

                            if _theComponent.getName() == "user_selectDateStart": theStartDate  = _theComponent
                            elif _theComponent.getName() == "user_selectDateEnd": theEndDate  = _theComponent
                            elif _theComponent.getName() == "user_includeSubAccounts": theSubAccounts  = _theComponent
                            elif _theComponent.getName() == "user_hideInactiveAccounts": theHideInactiveAccounts  = _theComponent
                            elif _theComponent.getName() == "user_hideHiddenAccounts": theHideHiddenAccounts  = _theComponent
                            elif _theComponent.getName() == "user_selectAccounts": theFilterAccounts  = _theComponent
                            elif _theComponent.getName() == "user_selectCurrency": theFilterCurrency  = _theComponent

                    if not theDateRangeDropDown and not theAccountDropdown: return

                    if theDateRangeDropDown:
                        _start, _end = getDateRange(theDateRangeDropDown.getSelectedItem())
                        if theDateRangeDropDown.getSelectedItem() == "custom_date":
                            theStartDate.setEnabled(True)
                            theEndDate.setEnabled(True)
                        else:
                            theStartDate.setEnabled(False)
                            theEndDate.setEnabled(False)

                        # noinspection PyUnresolvedReferences
                        theStartDate.setDateInt(_start)
                        # noinspection PyUnresolvedReferences
                        theEndDate.setDateInt(_end)

                    if theAccountDropdown:

                        if isinstance(theAccountDropdown.getSelectedItem(),(str,unicode)):
                            theSubAccounts.setEnabled(False)
                            theHideInactiveAccounts.setEnabled(True)
                            theHideHiddenAccounts.setEnabled(True)
                            theFilterAccounts.setEnabled(True)
                            theFilterCurrency.setEnabled(True)

                            theSubAccounts.setSelected(False)

                        else:
                            theSubAccounts.setEnabled(True)
                            theHideInactiveAccounts.setEnabled(False)
                            theHideHiddenAccounts.setEnabled(False)
                            theFilterAccounts.setEnabled(False)
                            theFilterCurrency.setEnabled(False)

                            theHideInactiveAccounts.setSelected(True)
                            theHideHiddenAccounts.setSelected(True)
                            theFilterAccounts.setText("ALL")
                            theFilterCurrency.setText("ALL")

                    myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
                    return


            labelHideInactiveAccounts = JLabel("Hide Inactive Accounts?")
            user_hideInactiveAccounts = JCheckBox("", hideInactiveAccounts)
            user_hideInactiveAccounts.setName("user_hideInactiveAccounts")

            labelHideHiddenAccounts = JLabel("Hide Hidden Accounts?")
            user_hideHiddenAccounts = JCheckBox("", hideHiddenAccounts)
            user_hideHiddenAccounts.setName("user_hideHiddenAccounts")

            labelFilterCurrency = JLabel("Filter for Currency containing text '...' or ALL:")
            user_selectCurrency = JTextField(12)
            user_selectCurrency.setName("user_selectCurrency")
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
            accountDropdown.setName("accountDropdown")

            if saveDropDownAccountUUID_EAR != "":
                findAccount = AccountUtil.findAccountWithID(moneydance.getRootAccount(), saveDropDownAccountUUID_EAR)
                if findAccount:
                    try:
                        accountDropdown.setSelectedItem(findAccount)
                    except:
                        pass

            labelFilterAccounts = JLabel("Filter for Accounts containing text '...' (or ALL):")
            user_selectAccounts = JTextField(12)
            user_selectAccounts.setName("user_selectAccounts")
            user_selectAccounts.setDocument(JTextFieldLimitYN(30, True, "CURR"))
            if lAllAccounts: user_selectAccounts.setText("ALL")
            else:            user_selectAccounts.setText(filterForAccounts)

            labelIncludeSubAccounts = JLabel("Include Sub Accounts?:")
            user_includeSubAccounts = JCheckBox("",lIncludeSubAccounts_EAR)
            user_includeSubAccounts.setName("user_includeSubAccounts")

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

            labelOpeningBalances = JLabel("Include Opening Balances?")
            user_selectOpeningBalances = JCheckBox("", lIncludeOpeningBalances_EAR)
            user_selectOpeningBalances.setName("user_selectOpeningBalances")

            if isinstance(accountDropdown.getSelectedItem(),(str,unicode)):
                user_includeSubAccounts.setEnabled(False)
                user_hideInactiveAccounts.setEnabled(True)
                user_hideHiddenAccounts.setEnabled(True)
                user_selectAccounts.setEnabled(True)
                user_selectCurrency.setEnabled(True)

                user_includeSubAccounts.setSelected(False)

            else:
                user_includeSubAccounts.setSelected(True)
                user_hideInactiveAccounts.setEnabled(False)
                user_hideHiddenAccounts.setEnabled(False)
                user_selectAccounts.setEnabled(False)
                user_selectCurrency.setEnabled(False)

                user_hideInactiveAccounts.setSelected(True)
                user_hideHiddenAccounts.setSelected(True)
                user_selectAccounts.setText("ALL")
                user_selectCurrency.setText("ALL")

            labelIncludeTransfers = JLabel("Include Transfers between Accounts Selected in this Extract?")
            user_selectIncludeTransfers = JCheckBox("", lIncludeInternalTransfers_EAR)
            user_selectIncludeTransfers.setName("user_selectIncludeTransfers")

            dateOptions = [ "year_to_date",
                            "fiscal_year_to_date",
                            "last_fiscal_quarter",
                            "quarter_to_date",
                            "month_to_date",
                            "this_year",
                            "this_fiscal_year",
                            "this_quarter",
                            "this_month",
                            "this_week",
                            "last_year",
                            "last_fiscal_year",
                            "last_quarter",
                            "last_month",
                            "last_12_months",
                            "last_365_days",
                            "last_30_days",
                            "last_1_day",
                            "all_dates",
                            "custom_date",
                            "last_week",]

            def getDateRange( selectedOption ):         # DateRange

                todayInt = Util.getStrippedDateInt()

                if selectedOption == "year_to_date":
                    return (DateUtil.firstDayInYear(todayInt), todayInt)
                elif selectedOption ==  "quarter_to_date":
                    return (DateUtil.firstDayInQuarter(todayInt), todayInt)
                elif selectedOption ==  "month_to_date":
                    return (DateUtil.firstDayInMonth(todayInt), todayInt)
                elif selectedOption ==  "this_year":
                    return (DateUtil.firstDayInYear(todayInt), DateUtil.lastDayInYear(todayInt))
                elif selectedOption ==  "this_fiscal_year":
                    return (DateUtil.firstDayInFiscalYear(todayInt), DateUtil.lastDayInFiscalYear(todayInt))
                elif selectedOption ==  "fiscal_year_to_date":
                    return (DateUtil.firstDayInFiscalYear(todayInt), todayInt)
                elif selectedOption ==  "last_fiscal_year":
                    return (DateUtil.decrementYear(DateUtil.firstDayInFiscalYear(todayInt)),
                                     DateUtil.decrementYear(DateUtil.lastDayInFiscalYear(todayInt)))
                elif selectedOption ==  "last_fiscal_quarter":
                    baseDate = DateUtil.incrementDate(todayInt, 0, -3, 0)
                    return (DateUtil.firstDayInFiscalQuarter(baseDate), DateUtil.lastDayInFiscalQuarter(baseDate))
                elif selectedOption ==  "this_quarter":
                    return (Util.firstDayInQuarter(todayInt), Util.lastDayInQuarter(todayInt))
                elif selectedOption ==  "this_month":
                    return (Util.firstDayInMonth(todayInt), Util.lastDayInMonth(todayInt))
                elif selectedOption ==  "this_week":
                    return (Util.firstDayInWeek(todayInt), Util.lastDayInWeek(todayInt))
                elif selectedOption ==  "last_year":
                    return (Util.firstDayInYear(Util.decrementYear(todayInt)),
                                     Util.lastDayInYear(Util.decrementYear(todayInt)))
                elif selectedOption ==  "last_quarter":
                    baseDate = DateUtil.incrementDate(todayInt, 0, -3, 0)
                    return (DateUtil.firstDayInQuarter(baseDate), DateUtil.lastDayInQuarter(baseDate))
                elif selectedOption ==  "last_month":
                    i = Util.firstDayInMonth(todayInt)
                    return (Util.incrementDate(i, 0, -1, 0), Util.incrementDate(i, 0, 0, -1))
                elif selectedOption ==  "last_week":
                    firstDayInWeek = Util.firstDayInWeek(todayInt)
                    return (Util.incrementDate(firstDayInWeek, 0, 0, -7), Util.incrementDate(firstDayInWeek, 0, 0, -1))
                elif selectedOption ==  "last_12_months":
                    firstDayInMonth = Util.firstDayInMonth(todayInt)
                    return (Util.incrementDate(firstDayInMonth, 0, -12, 0), Util.incrementDate(firstDayInMonth, 0, 0, -1))
                elif selectedOption ==  "last_1_day":
                    return (Util.incrementDate(todayInt, 0, 0, -1), Util.incrementDate(todayInt, 0, 0, 0))
                elif selectedOption == "last_30_days":
                    return (Util.incrementDate(todayInt, 0, 0, -30), todayInt)
                elif selectedOption ==  "last_365_days":
                    return (Util.incrementDate(todayInt, 0, 0, -365), todayInt)
                elif selectedOption ==  "custom_date":
                    pass
                elif selectedOption ==  "all_dates":
                    pass
                else:
                    pass
                    # raise(Exception("Error - date range incorrect"))

                # cal = Calendar.getInstance()
                # cal.add(1, 1)
                return 19600101,20301231


            dateDropdown = JComboBox(dateOptions)
            dateDropdown.setName("dateDropdown")
            if saveDropDownDateRange_EAR != "":
                try:
                    dateDropdown.setSelectedItem(saveDropDownDateRange_EAR)
                except:
                    pass


            labelDateDropDown = JLabel("Select Date Range:")


            labelDateStart = JLabel("Date range start (enter as yyyy/mm/dd):")
            user_selectDateStart = JDateField(CustomDateFormat("ymd"),15)   # Use MD API function (not std Python)
            user_selectDateStart.setName("user_selectDateStart")
            user_selectDateStart.setEnabled(False)
            user_selectDateStart.setDisabledTextColor(Color.gray)
            user_selectDateStart.setDateInt(userdateStart_EAR)

            labelDateEnd = JLabel("Date range end (enter as yyyy/mm/dd):")
            user_selectDateEnd = JDateField(CustomDateFormat("ymd"),15)   # Use MD API function (not std Python)
            user_selectDateEnd.setName("user_selectDateEnd")
            user_selectDateEnd.setEnabled(False)
            user_selectDateEnd.setDisabledTextColor(Color.gray)
            user_selectDateEnd.setDateInt(userdateEnd_EAR)

            if saveDropDownDateRange_EAR == "custom_date":
                user_selectDateStart.setEnabled(True)
                user_selectDateEnd.setEnabled(True)
            else:
                # Refresh the date range
                user_selectDateStart.setEnabled(False)
                user_selectDateEnd.setEnabled(False)
                _s, _e = getDateRange(saveDropDownDateRange_EAR)
                user_selectDateStart.setDateInt(_s)
                user_selectDateEnd.setDateInt(_e)

            labelTags = JLabel("Filter for Tags (separate with commas) or ALL:")
            user_selectTags = JTextField(12)
            user_selectTags.setName("user_selectTags")
            user_selectTags.setDocument(JTextFieldLimitYN(30, True, "CURR"))
            if lAllTags_EAR: user_selectTags.setText("ALL")
            else:            user_selectTags.setText(tagFilter_EAR)

            labelText = JLabel("Filter for Text in Description or Memo fields or ALL:")
            user_selectText = JTextField(12)
            user_selectText.setName("user_selectText")
            user_selectText.setDocument(JTextFieldLimitYN(30, True, "CURR"))
            if lAllText_EAR: user_selectText.setText("ALL")
            else:            user_selectText.setText(textFilter_EAR)

            labelAttachments = JLabel("Extract & Download Attachments?")
            user_selectExtractAttachments = JCheckBox("", lExtractAttachments_EAR)
            user_selectExtractAttachments.setName("user_selectExtractAttachments")

            dateStrings=["dd/mm/yyyy", "mm/dd/yyyy", "yyyy/mm/dd", "yyyymmdd"]
            labelDateFormat = JLabel("Select Output Date Format (default yyyy/mm/dd):")
            user_dateformat = JComboBox(dateStrings)
            user_dateformat.setName("user_dateformat")

            if userdateformat == "%d/%m/%Y": user_dateformat.setSelectedItem("dd/mm/yyyy")
            elif userdateformat == "%m/%d/%Y": user_dateformat.setSelectedItem("mm/dd/yyyy")
            elif userdateformat == "%Y%m%d": user_dateformat.setSelectedItem("yyyymmdd")
            else: user_dateformat.setSelectedItem("yyyy/mm/dd")

            labelStripASCII = JLabel("Strip non ASCII characters from CSV export?")
            user_selectStripASCII = JCheckBox("", lStripASCII)
            user_selectStripASCII.setName("user_selectStripASCII")

            delimStrings = [";","|",","]
            labelDelimiter = JLabel("Change CSV Export Delimiter from default to: '|,'")
            user_selectDELIMITER = JComboBox(delimStrings)
            user_selectDELIMITER.setName("user_selectDELIMITER")
            user_selectDELIMITER.setSelectedItem(csvDelimiter)

            labelBOM = JLabel("Write BOM (Byte Order Mark) to file (helps Excel open files)?")
            user_selectBOM = JCheckBox("", lWriteBOMToExportFile_SWSS)
            user_selectBOM.setName("user_selectBOM")

            labelDEBUG = JLabel("Turn DEBUG Verbose messages on?")
            user_selectDEBUG = JCheckBox("", debug)
            user_selectDEBUG.setName("user_selectDEBUG")

            labelSTATUSbar = JLabel("")
            labelSTATUSbar.setName("labelSTATUSbar")

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

            userFilters.add(labelDateDropDown)
            userFilters.add(dateDropdown)

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
            userFilters.add(labelDateFormat)
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

            components = userFilters.getComponents()
            for theComponent in components:
                if isinstance(theComponent, (JComboBox,JTextField)):
                    theComponent.addActionListener(PanelAction( userFilters ))


            options = ["ABORT", "CSV Export"]

            while True:

                userAction = (JOptionPane.showOptionDialog(extract_data_frame_,
                                                           userFilters, "%s(build: %s) Set Script Parameters...." % (myScriptName,version_build),
                                                           JOptionPane.OK_CANCEL_OPTION,
                                                           JOptionPane.QUESTION_MESSAGE,
                                                           moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                           options, options[1]))
                if userAction != 1:
                    myPrint("B", "User Cancelled Parameter selection.. Will abort..")
                    myPopupInformationBox(extract_data_frame_, "User Cancelled Parameter selection.. Will abort..", "PARAMETERS")
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

                if user_selectTags.getText() != "ALL" and user_selectOpeningBalances.isSelected():
                    user_selectTags.setForeground(Color.RED)
                    user_selectOpeningBalances.setForeground(Color.RED)
                    labelSTATUSbar.setText(">> Error - You cannot filter on Tags and Include Opening Balances..... <<".upper())
                    labelSTATUSbar.setForeground(Color.RED)
                    continue

                if user_selectText.getText() != "ALL" and user_selectOpeningBalances.isSelected():
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
                    if user_includeSubAccounts.isSelected():
                        user_includeSubAccounts.setSelected(False)
                        labelSTATUSbar.setText(">> Error - Dropdown Accounts <NONE> and Include Sub Accounts True... <<".upper())
                        labelSTATUSbar.setForeground(Color.RED)
                        user_includeSubAccounts.setForeground(Color.RED)
                        accountDropdown.setForeground(Color.RED)
                        continue
                elif isinstance(accountDropdown.getSelectedItem(),(Account)):

                    if (user_selectAccounts.getText() != "ALL" or user_selectCurrency.getText() != "ALL"
                            or (not user_hideInactiveAccounts.isSelected()) or (not user_hideHiddenAccounts.isSelected())):
                        user_selectAccounts.setText("ALL")
                        user_selectCurrency.setText("ALL")
                        user_hideInactiveAccounts.setSelected(True)
                        user_hideHiddenAccounts.setSelected(True)
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
                        "SubActs:", user_includeSubAccounts.isSelected(),
                        "InActAct:", user_hideInactiveAccounts.isSelected(),
                        "HidAct:", user_hideHiddenAccounts.isSelected(),
                        "Filter Accts:", user_selectAccounts.getText(),
                        "Filter Curr:", user_selectCurrency.getText(),
                        "Incl Open Bals:", user_selectOpeningBalances.isSelected(),
                        # "Incl Transfers:", user_selectIncludeTransfers.isSelected(),
                        "Date Range:", dateDropdown.getSelectedItem(),
                        "StartDate:", user_selectDateStart.getDateInt(),
                        "EndDate:", user_selectDateEnd.getDateInt(),
                        "DownldAttachments:", user_selectExtractAttachments.isSelected(),
                        "Tags:", user_selectTags.getText(),
                        "Text:", user_selectText.getText(),
                        "User Date Format:", user_dateformat.getSelectedItem(),
                        "Strip ASCII:", user_selectStripASCII.isSelected(),
                        "Write BOM to file:", user_selectBOM.isSelected(),
                        "Verbose Debug Messages: ", user_selectDEBUG.isSelected(),
                        "CSV File Delimiter:", user_selectDELIMITER.getSelectedItem())
                # endif

                hideInactiveAccounts = user_hideInactiveAccounts.isSelected()
                hideHiddenAccounts = user_hideHiddenAccounts.isSelected()
                lIncludeSubAccounts_EAR = user_includeSubAccounts.isSelected()
                lIncludeOpeningBalances_EAR = user_selectOpeningBalances.isSelected()
                lIncludeInternalTransfers_EAR = user_selectIncludeTransfers.isSelected()
                lExtractAttachments_EAR = user_selectExtractAttachments.isSelected()
                lWriteBOMToExportFile_SWSS = user_selectBOM.isSelected()
                lStripASCII = user_selectStripASCII.isSelected()
                debug = user_selectDEBUG.isSelected()

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

                if user_dateformat.getSelectedItem() == "dd/mm/yyyy": userdateformat = "%d/%m/%Y"
                elif user_dateformat.getSelectedItem() == "mm/dd/yyyy": userdateformat = "%m/%d/%Y"
                elif user_dateformat.getSelectedItem() == "yyyy/mm/dd": userdateformat = "%Y/%m/%d"
                elif user_dateformat.getSelectedItem() == "yyyymmdd": userdateformat = "%Y%m%d"
                else:
                    # PROBLEM /  default
                    userdateformat = "%Y/%m/%d"


                csvDelimiter = user_selectDELIMITER.getSelectedItem()
                if csvDelimiter == "" or (not (csvDelimiter in ";|,")):
                    myPrint("B", "Invalid Delimiter:", csvDelimiter, "selected. Overriding with:','")
                    csvDelimiter = ","
                if decimalCharSep == csvDelimiter:
                    myPrint("B", "WARNING: The CSV file delimiter:", csvDelimiter, "cannot be the same as your decimal point character:",
                            decimalCharSep, " - Proceeding without file export!!")
                    lDisplayOnly = True
                    myPopupInformationBox(None, "ERROR - The CSV file delimiter: %s ""cannot be the same as your decimal point character: %s. "
                                                "Proceeding without file export (i.e. I will do nothing)!!" %(csvDelimiter, decimalCharSep),
                                          "INVALID FILE DELIMITER", theMessageType=JOptionPane.ERROR_MESSAGE)

                saveDropDownDateRange_EAR = dateDropdown.getSelectedItem()

                if isinstance(accountDropdown.getSelectedItem(), Account):
                    dropDownAccount_EAR = accountDropdown.getSelectedItem()
                    # noinspection PyUnresolvedReferences
                    saveDropDownAccountUUID_EAR = dropDownAccount_EAR.getUUID()
                    labelIncludeSubAccounts = user_includeSubAccounts.isSelected()
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
                myPrint("B","Date range.................: %s" %(saveDropDownDateRange_EAR))
                myPrint("B","Selected Start Date........: %s" %(userdateStart_EAR))
                myPrint("B","Selected End Date..........: %s" %(userdateEnd_EAR))
                myPrint("B", "user date format..........: %s" %(userdateformat))

        elif lExtractInvestmentTxns:
            # ####################################################
            # EXTRACT_INVESTMENT_TRANSACTIONS_CSV PARAMETER SCREEN
            # ####################################################

            label1 = JLabel("Hide Hidden Securities?")
            user_hideHiddenSecurities = JCheckBox("", hideHiddenSecurities)

            label2 = JLabel("Hide Inactive Accounts?")
            user_hideInactiveAccounts = JCheckBox("", hideInactiveAccounts)

            label3 = JLabel("Hide Hidden Accounts?")
            user_hideHiddenAccounts = JCheckBox("", hideHiddenAccounts)

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

            label7 = JLabel("Include Opening Balances?")
            user_selectOpeningBalances = JCheckBox("", lIncludeOpeningBalances)

            label8 = JLabel("Adjust for stock splits/")
            user_selectAdjustSplits = JCheckBox("", lAdjustForSplits)

            dateStrings=["dd/mm/yyyy", "mm/dd/yyyy", "yyyy/mm/dd", "yyyymmdd"]
            label9 = JLabel("Select Output Date Format (default yyyy/mm/dd):")
            user_dateformat = JComboBox(dateStrings)

            if userdateformat == "%d/%m/%Y": user_dateformat.setSelectedItem("dd/mm/yyyy")
            elif userdateformat == "%m/%d/%Y": user_dateformat.setSelectedItem("mm/dd/yyyy")
            elif userdateformat == "%Y%m%d": user_dateformat.setSelectedItem("yyyymmdd")
            else: user_dateformat.setSelectedItem("yyyy/mm/dd")

            labelAttachments = JLabel("Extract & Download Attachments?")
            user_selectExtractAttachments = JCheckBox("", lExtractAttachments_EIT)
            user_selectExtractAttachments.setName("user_selectExtractAttachments")

            label10 = JLabel("Strip non ASCII characters from CSV export?")
            user_selectStripASCII = JCheckBox("", lStripASCII)

            delimStrings = [";","|",","]
            label11 = JLabel("Change CSV Export Delimiter from default to: ';|,'")
            user_selectDELIMITER = JComboBox(delimStrings)
            user_selectDELIMITER.setSelectedItem(csvDelimiter)

            labelBOM = JLabel("Write BOM (Byte Order Mark) to file (helps Excel open files)?")
            user_selectBOM = JCheckBox("", lWriteBOMToExportFile_SWSS)

            label12 = JLabel("Turn DEBUG Verbose messages on?")
            user_selectDEBUG = JCheckBox("", debug)

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
            userFilters.add(user_selectOpeningBalances)
            userFilters.add(label8)
            userFilters.add(user_selectAdjustSplits)
            userFilters.add(labelAttachments)
            userFilters.add(user_selectExtractAttachments)
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
            userAction = (JOptionPane.showOptionDialog(extract_data_frame_, userFilters, "%s(build: %s) Set Script Parameters...."%(myScriptName,version_build),
                                                       JOptionPane.OK_CANCEL_OPTION,
                                                       JOptionPane.QUESTION_MESSAGE,
                                                       moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                       options, options[1]))
            if userAction == 1:  # Export
                myPrint("DB", "Export chosen")
                lDisplayOnly = False
            else:
                myPrint("B", "User Cancelled Parameter selection.. Will exit..")
                myPopupInformationBox(extract_data_frame_, "User Cancelled Parameter selection.. Will abort..", "PARAMETERS")
                lDisplayOnly = False
                lExit = True

            if not lExit:
                myPrint("DB", "Parameters Captured",
                        "Sec: ", user_hideHiddenSecurities.isSelected(),
                        "InActAct:", user_hideInactiveAccounts.isSelected(),
                        "HidAct:", user_hideHiddenAccounts.isSelected(),
                        "Curr:", user_selectCurrency.getText(),
                        "Ticker:", user_selectTicker.getText(),
                        "Filter Accts:", user_selectAccounts.getText(),
                        "Incl Open Bals:", user_selectOpeningBalances.isSelected(),
                        "Adj Splits:", user_selectAdjustSplits.isSelected(),
                        "DownldAttachments:", user_selectExtractAttachments.isSelected(),
                        "User Date Format:", user_dateformat.getSelectedItem(),
                        "Strip ASCII:", user_selectStripASCII.isSelected(),
                        "Write BOM to file:", user_selectBOM.isSelected(),
                        "Verbose Debug Messages: ", user_selectDEBUG.isSelected(),
                        "CSV File Delimiter:", user_selectDELIMITER.getSelectedItem())

                hideHiddenSecurities = user_hideHiddenSecurities.isSelected()
                hideInactiveAccounts = user_hideInactiveAccounts.isSelected()
                hideHiddenAccounts = user_hideHiddenAccounts.isSelected()

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

                lIncludeOpeningBalances = user_selectOpeningBalances.isSelected()
                lAdjustForSplits = user_selectAdjustSplits.isSelected()
                lExtractAttachments_EIT = user_selectExtractAttachments.isSelected()

                if user_dateformat.getSelectedItem() == "dd/mm/yyyy": userdateformat = "%d/%m/%Y"
                elif user_dateformat.getSelectedItem() == "mm/dd/yyyy": userdateformat = "%m/%d/%Y"
                elif user_dateformat.getSelectedItem() == "yyyy/mm/dd": userdateformat = "%Y/%m/%d"
                elif user_dateformat.getSelectedItem() == "yyyymmdd": userdateformat = "%Y%m%d"
                else:
                    # PROBLEM /  default
                    userdateformat = "%Y/%m/%d"

                lStripASCII = user_selectStripASCII.isSelected()

                csvDelimiter = user_selectDELIMITER.getSelectedItem()
                if csvDelimiter == "" or (not (csvDelimiter in ";|,")):
                    myPrint("B", "Invalid Delimiter:", csvDelimiter, "selected. Overriding with:','")
                    csvDelimiter = ","
                if decimalCharSep == csvDelimiter:
                    myPrint("B", "WARNING: The CSV file delimiter:", csvDelimiter, "cannot be the same as your decimal point character:",
                            decimalCharSep, " - Proceeding without file export!!")
                    lDisplayOnly = True
                    myPopupInformationBox(None, "ERROR - The CSV file delimiter: %s ""cannot be the same as your decimal point character: %s. "
                                                "Proceeding without file export (i.e. I will do nothing)!!" %(csvDelimiter, decimalCharSep),
                                          "INVALID FILE DELIMITER", theMessageType=JOptionPane.ERROR_MESSAGE)

                lWriteBOMToExportFile_SWSS = user_selectBOM.isSelected()

                debug = user_selectDEBUG.isSelected()

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

        elif lExtractCurrencyHistory:
            # ####################################################
            # EXTRACT_CURRENCY_HISTORY_CSV PARAMETER SCREEN
            # ####################################################

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

                userAction = (JOptionPane.showOptionDialog(extract_data_frame_, userFilters, "%s(build: %s) Set Script Parameters...."%(myScriptName,version_build),
                                                           JOptionPane.OK_CANCEL_OPTION,
                                                           JOptionPane.QUESTION_MESSAGE,
                                                           moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                           options, options[1]))
                if userAction != 1:
                    myPrint("B", "User Cancelled Parameter selection.. Will abort..")
                    myPopupInformationBox(extract_data_frame_, "User Cancelled Parameter selection.. Will abort..", "PARAMETERS")
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
                    myPopupInformationBox(None, "ERROR - The CSV file delimiter: %s ""cannot be the same as your decimal point character: %s. "
                                                "Proceeding without file export (i.e. I will do nothing)!!" %(csvDelimiter, decimalCharSep),
                                          "INVALID FILE DELIMITER", theMessageType=JOptionPane.ERROR_MESSAGE)

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

        elif lExtractStockGlance2020:
            # ####################################################
            # STOCKGLANCE2020 PARAMETER SCREEN
            # ####################################################
            label1 = JLabel("Hide Hidden Securities?")
            user_hideHiddenSecurities = JCheckBox("", hideHiddenSecurities)

            label2 = JLabel("Hide Inactive Accounts?")
            user_hideInactiveAccounts = JCheckBox("", hideInactiveAccounts)

            label3 = JLabel("Hide Hidden Accounts?")
            user_hideHiddenAccounts = JCheckBox("", hideHiddenAccounts)

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

            label7 = JLabel("Include Cash Balances for each account?")
            user_selectCashBalances = JCheckBox("", lIncludeCashBalances)

            label7b = JLabel("Split Security Qtys by Account?")
            user_splitSecurities = JCheckBox("", lSplitSecuritiesByAccount)

            labelFutureBalances = JLabel("Include Future Balances (rather than current)?")
            user_includeFutureBalances = JCheckBox("", lIncludeFutureBalances_SG2020)

            label7c = JLabel("Exclude Totals from CSV extract (helps pivots)?")
            user_excludeTotalsFromCSV = JCheckBox("", lExcludeTotalsFromCSV)

            label7d = JLabel("Round calculated price using security dpc setting (N=No Rounding)?")
            user_roundPrice = JCheckBox("", lRoundPrice)

            labelRC = JLabel("Reset Column Widths to Defaults?")
            user_selectResetColumns = JCheckBox("", False)

            label8 = JLabel("Strip non ASCII characters from CSV export?")
            user_selectStripASCII = JCheckBox("", lStripASCII)

            delimStrings = [";","|",","]
            label9 = JLabel("Change CSV Export Delimiter from default to: ';|,'")
            user_selectDELIMITER = JComboBox(delimStrings)
            user_selectDELIMITER.setSelectedItem(csvDelimiter)

            labelBOM = JLabel("Write BOM (Byte Order Mark) to file (helps Excel open files)?")
            user_selectBOM = JCheckBox("", lWriteBOMToExportFile_SWSS)

            label10 = JLabel("Turn DEBUG Verbose messages on?")
            user_selectDEBUG = JCheckBox("", debug)

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
            userFilters.add(labelRC)
            userFilters.add(user_selectResetColumns)
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
            userAction = (JOptionPane.showOptionDialog(extract_data_frame_,
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
                myPopupInformationBox(extract_data_frame_,"User Cancelled Parameter selection.. Will abort..","PARAMETERS")
                lDisplayOnly = False
                lExit = True

            if not lExit:
                if debug:
                    myPrint("DB", "Parameters Captured",
                            "Sec: ", user_hideHiddenSecurities.isSelected(),
                            "InActAct:", user_hideInactiveAccounts.isSelected(),
                            "HidAct:", user_hideHiddenAccounts.isSelected(),
                            "Curr:", user_selectCurrency.getText(),
                            "Ticker:", user_selectTicker.getText(),
                            "Filter Accts:", user_selectAccounts.getText(),
                            "Include Cash Balances:", user_selectCashBalances.isSelected(),
                            "Split Securities:", user_splitSecurities.isSelected(),
                            "Include Future Balances:", user_includeFutureBalances.isSelected(),
                            "Exclude Totals from CSV:", user_excludeTotalsFromCSV.isSelected(),
                            "Round Calc Price:", user_roundPrice.isSelected(),
                            "Reset Columns:", user_selectResetColumns.isSelected(),
                            "Strip ASCII:", user_selectStripASCII.isSelected(),
                            "Write BOM to file:", user_selectBOM.isSelected(),
                            "Verbose Debug Messages: ", user_selectDEBUG.isSelected(),
                            "CSV File Delimiter:", user_selectDELIMITER.getSelectedItem())
                # endif

                if user_selectResetColumns.isSelected():
                    myPrint("B","User asked to reset columns.... Resetting Now....")
                    _column_widths_SG2020=[]  # This will invalidate the

                hideHiddenSecurities = user_hideHiddenSecurities.isSelected()
                hideInactiveAccounts = user_hideInactiveAccounts.isSelected()
                hideHiddenAccounts = user_hideHiddenAccounts.isSelected()

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

                lIncludeCashBalances = user_selectCashBalances.isSelected()
                lSplitSecuritiesByAccount = user_splitSecurities.isSelected()
                lExcludeTotalsFromCSV = user_excludeTotalsFromCSV.isSelected()
                lIncludeFutureBalances_SG2020 = user_includeFutureBalances.isSelected()
                lRoundPrice = user_roundPrice.isSelected()
                lStripASCII = user_selectStripASCII.isSelected()

                csvDelimiter = user_selectDELIMITER.getSelectedItem()
                if csvDelimiter == "" or (not (csvDelimiter in ";|,")):
                    myPrint("B", "Invalid Delimiter:", csvDelimiter, "selected. Overriding with:','")
                    csvDelimiter = ","
                if decimalCharSep == csvDelimiter:
                    myPrint("B", "WARNING: The CSV file delimiter:", csvDelimiter, "cannot be the same as your decimal point character:", decimalCharSep, " - Proceeding without file export!!")
                    lDisplayOnly = True
                    myPopupInformationBox(None, "ERROR - The CSV file delimiter: %s ""cannot be the same as your decimal point character: %s. "
                                                "Proceeding without file export (i.e. I will do nothing)!!" %(csvDelimiter, decimalCharSep),
                                          "INVALID FILE DELIMITER", theMessageType=JOptionPane.ERROR_MESSAGE)

                lWriteBOMToExportFile_SWSS = user_selectBOM.isSelected()

                debug = user_selectDEBUG.isSelected()
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

        elif lExtractReminders:
            # ####################################################
            # EXTRACT_REMINDERS_CSV PARAMETER SCREEN
            # ####################################################

            dateStrings=["dd/mm/yyyy", "mm/dd/yyyy", "yyyy/mm/dd", "yyyymmdd"]
            # 1=dd/mm/yyyy, 2=mm/dd/yyyy, 3=yyyy/mm/dd, 4=yyyymmdd
            label1 = JLabel("Select Output Date Format (default yyyy/mm/dd):")
            user_dateformat = JComboBox(dateStrings)

            if userdateformat == "%d/%m/%Y": user_dateformat.setSelectedItem("dd/mm/yyyy")
            elif userdateformat == "%m/%d/%Y": user_dateformat.setSelectedItem("mm/dd/yyyy")
            elif userdateformat == "%Y%m%d": user_dateformat.setSelectedItem("yyyymmdd")
            else: user_dateformat.setSelectedItem("yyyy/mm/dd")

            labelRC = JLabel("Reset Column Widths to Defaults?")
            user_selectResetColumns = JCheckBox("", False)

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
            userFilters.add(labelRC)
            userFilters.add(user_selectResetColumns)
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

            options = ["Abort", "Display & CSV Export", "Display Only"]
            userAction = (JOptionPane.showOptionDialog( extract_data_frame_,
                                                        userFilters,
                                                        "%s(build: %s) Set Script Parameters...." %(myScriptName, version_build),
                                                        JOptionPane.OK_CANCEL_OPTION,
                                                        JOptionPane.QUESTION_MESSAGE,
                                                        moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                        options,
                                                        options[2])
                          )
            if userAction == 1:  # Display & Export
                myPrint("DB", "Display and export chosen")
                lDisplayOnly = False
            elif userAction == 2:  # Display Only
                lDisplayOnly = True
                myPrint("DB", "Display only with no export chosen")
            else:
                # Abort
                myPrint("DB", "User Cancelled Parameter selection.. Will abort..")
                myPopupInformationBox(extract_data_frame_, "User Cancelled Parameter selection.. Will abort..", "PARAMETERS")
                lDisplayOnly = False
                lExit = True

            if not lExit:

                debug = user_selectDEBUG.isSelected()
                myPrint("DB", "DEBUG turned on")

                if debug:
                    myPrint("DB","Parameters Captured",
                            "User Date Format:", user_dateformat.getSelectedItem(),
                            "Reset Columns", user_selectResetColumns.isSelected(),
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

                if user_selectResetColumns.isSelected():
                    myPrint("B","User asked to reset columns.... Resetting Now....")
                    _column_widths_ERTC=[]  # This will invalidate them

                lStripASCII = user_selectStripASCII.isSelected()

                csvDelimiter = user_selectDELIMITER.getSelectedItem()
                if csvDelimiter == "" or (not (csvDelimiter in ";|,")):
                    myPrint("B", "Invalid Delimiter:", csvDelimiter, "selected. Overriding with:','")
                    csvDelimiter = ","
                if decimalCharSep == csvDelimiter:
                    myPrint("B", "WARNING: The CSV file delimiter:", csvDelimiter, "cannot be the same as your decimal point character:", decimalCharSep, " - Proceeding without file export!!")
                    lDisplayOnly = True
                    myPopupInformationBox(None, "ERROR - The CSV file delimiter: %s ""cannot be the same as your decimal point character: %s. "
                                                "Proceeding without file export (i.e. I will do nothing)!!" %(csvDelimiter, decimalCharSep),
                                          "INVALID FILE DELIMITER", theMessageType=JOptionPane.ERROR_MESSAGE)

                lWriteBOMToExportFile_SWSS = user_selectBOM.isSelected()

                myPrint("B", "User Parameters...")
                myPrint("B", "user date format....:", userdateformat)

        else:
            myPopupInformationBox(extract_data_frame_, "ERROR - Failed to detect correct parameter screen - will exit",theMessageType=JOptionPane.ERROR_MESSAGE)
            lExit = True


    if not lExit and (lExtractReminders or lExtractStockGlance2020):

        if lExtractStockGlance2020:
            # Stores  the data table for export
            rawDataTable = None
            rawrawFooterTable = None

        class CloseAboutAction(AbstractAction):
            # noinspection PyMethodMayBeStatic
            # noinspection PyUnusedLocal

            def __init__(self, theFrame):
                self.theFrame = theFrame

            def actionPerformed(self, event):
                global debug, extract_data_frame_

                myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event:", event)

                self.theFrame.dispose()

        def about_this_script():
            global debug, scriptExit, extract_data_frame_

            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

            # noinspection PyUnresolvedReferences
            about_d = JDialog(extract_data_frame_, "About", Dialog.ModalityType.MODELESS)

            shortcut = Toolkit.getDefaultToolkit().getMenuShortcutKeyMaskEx()
            about_d.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_W, shortcut), "close-window")
            about_d.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_F4, shortcut), "close-window")
            about_d.getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0), "close-window")
            about_d.getRootPane().getActionMap().put("close-window", CloseAboutAction(about_d))

            about_d.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE)  # The CloseAction() and WindowListener() will handle dispose() - else change back to DISPOSE_ON_CLOSE

            if (not Platform.isMac()):
                # moneydance_ui.getImages()
                about_d.setIconImage(MDImages.getImage(moneydance_ui.getMain().getSourceInformation().getIconResource()))

            aboutPanel=JPanel()
            aboutPanel.setLayout(FlowLayout(FlowLayout.LEFT))
            aboutPanel.setPreferredSize(Dimension(1070, 500))

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

        class MyRunnable(Runnable):

            def __init__(self, theFrame):
                self.theFrame = theFrame

            # noinspection PyMethodMayBeStatic
            def run(self):
                global debug

                myPrint("DB","Inside %s MyRunnable.... About to trigger WindowClosing event to close %s" %(myModuleID,myModuleID))
                try:
                    self.theFrame.dispatchEvent(WindowEvent(self.theFrame, WindowEvent.WINDOW_CLOSING))
                    myPrint("DB","Back from pushing a WINDOW_CLOSING Event to %s...." %myModuleID)
                except:
                    dump_sys_error_to_md_console_and_errorlog()
                    myPrint("B","@@ ERROR pushing a WINDOW_CLOSING Event to %s....  :-< " %myModuleID)

                return

        class MyEventListener(AppEventListener):

            def __init__(self, theFrame):
                self.alreadyClosed = False
                self.theFrame = theFrame
                self.myModuleID = myModuleID

            def getMyself(self):
                fm = moneydance.getModuleForID(self.myModuleID)
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

            # noinspection PyMethodMayBeStatic
            def handleEvent(self, appEvent):
                global debug

                myPrint("DB", "I am .handleEvent() within %s" %(classPrinter("MoneydanceAppListener", self.theFrame.MoneydanceAppListener)))
                if self.alreadyClosed:
                    myPrint("DB","....I'm actually still here (MD EVENT %s CALLED).. - Ignoring and returning back to MD...." %(appEvent))
                    return

                # MD doesn't call .unload() or .cleanup(), so if uninstalled I need to close myself
                fm, pyObject = self.getMyself()
                myPrint("DB", "Checking myself: %s : %s" %(fm, pyObject))
                # if (fm is None or pyObject is None) and appEvent != "md:app:exiting":
                if (fm is None or (self.theFrame.isRunTimeExtension and pyObject is None)) and appEvent != "md:app:exiting":
                    myPrint("B", "@@ ALERT - I've detected that I'm no longer installed as an extension - I will deactivate.. (switching event code to :close)")
                    appEvent = "%s:customevent:close" %self.myModuleID

                # I am only closing Toolbox when a new Dataset is opened.. I was calling it on MD Close/Exit, but it seemed to cause an Exception...
                if (appEvent == "md:file:closing"
                        or appEvent == "md:file:closed"
                        or appEvent == "md:file:opening"
                        or appEvent == "md:app:exiting"):
                    myPrint("DB","@@ Ignoring MD handleEvent: %s" %(appEvent))

                elif (appEvent == "md:file:opened" or appEvent == "%s:customevent:close" %self.myModuleID):
                    if debug:
                        myPrint("DB","MD event %s triggered.... Will call MyRunnable (on a new Thread) to push a WINDOW_CLOSING Event to %s to close itself (while I exit back to MD quickly) ...." %(appEvent, self.myModuleID))
                    else:
                        myPrint("B","Moneydance triggered event %s triggered - So I am closing %s now...." %(appEvent, self.myModuleID))
                    self.alreadyClosed = True
                    try:
                        t = Thread(MyRunnable(self.theFrame))
                        t.start()
                        myPrint("DB","Back from calling MyRunnable to push a WINDOW_CLOSING Event to %s.... ;-> ** I'm getting out quick! **" %(self.myModuleID))
                    except:
                        dump_sys_error_to_md_console_and_errorlog()
                        myPrint("B","@@ ERROR calling MyRunnable to push  a WINDOW_CLOSING Event to %s.... :-< ** I'm getting out quick! **" %(self.myModuleID))
                    if not debug: myPrint("DB","Returning back to Moneydance after calling for %s to close...." %self.myModuleID)
                    return

                myPrint("DB","@@ Detected MD handleEvent: %s" %(appEvent))

                # md:file:closing	The Moneydance file is being closed
                # md:file:closed	The Moneydance file has closed
                # md:file:opening	The Moneydance file is being opened
                # md:file:opened	The Moneydance file has opened
                # md:file:presave	The Moneydance file is about to be saved
                # md:file:postsave	The Moneydance file has been saved
                # md:app:exiting	Moneydance is shutting down
                # md:account:select	An account has been selected by the user
                # md:account:root	The root account has been selected
                # md:graphreport	An embedded graph or report has been selected
                # md:viewbudget	One of the budgets has been selected
                # md:viewreminders	One of the reminders has been selected
                # md:licenseupdated	The user has updated the license


    if not lExit:
        # Now get the export filename
        csvfilename = None

        if not lDisplayOnly:  # i.e. we have asked for a file export - so get the filename - Always False in this script1
            myPrint("B","Strip non-ASCII characters.: %s" %(lStripASCII))
            myPrint("B","Add BOM to front of file...: %s" %(lWriteBOMToExportFile_SWSS))
            myPrint("B","CSV Export Delimiter.......: %s" %(csvDelimiter))

            if lExcludeTotalsFromCSV:
                myPrint("B",  "Exclude Totals from CSV (to assist Pivot tables)..: %s" %(lExcludeTotalsFromCSV))

            if lExtractAccountTxns:
                extract_filename="extract_account_registers"+currentDateTimeMarker()+".csv"
            elif lExtractInvestmentTxns:
                extract_filename="extract_investment_transactions"+currentDateTimeMarker()+".csv"
            elif lExtractCurrencyHistory:
                extract_filename="extract_currency_history"+currentDateTimeMarker()+".csv"
            elif lExtractStockGlance2020:
                extract_filename="stockglance2020_extract_stock_balances"+currentDateTimeMarker()+".csv"
            elif lExtractReminders:
                extract_filename="extract_reminders"+currentDateTimeMarker()+".csv"

            def grabTheFile():
                global debug, lDisplayOnly, csvfilename, lIamAMac, scriptpath, myScriptName
                global attachmentDir, relativePath, lExtractAttachments_EAR, lExtractAttachments_EIT

                myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

                if scriptpath == "" or scriptpath is None:  # No parameter saved / loaded from disk
                    scriptpath = myDir()

                myPrint("DB", "Default file export output path is....:", scriptpath)

                csvfilename = ""
                if Platform.isOSX():
                    myPrint("DB", "MacOS X detected: Therefore I will run FileDialog with no extension filters to get filename....")
                    # jFileChooser hangs on Mac when using file extension filters, also looks rubbish. So using Mac(ish)GUI

                    System.setProperty("com.apple.macos.use-file-dialog-packages","true")  # In theory prevents access to app file structure (but doesnt seem to work)
                    System.setProperty("apple.awt.fileDialogForDirectories", "false")

                if (lExtractAccountTxns and lExtractAttachments_EAR) or (lExtractInvestmentTxns and lExtractAttachments_EIT):
                    filename = FileDialog(extract_data_frame_, "Select/Create CSV file for extract - MUST BE A UNIQUE NAME (CANCEL=NO EXPORT)")
                else:
                    filename = FileDialog(extract_data_frame_, "Select/Create CSV file for extract (CANCEL=NO EXPORT)")

                filename.setMultipleMode(False)
                filename.setMode(FileDialog.SAVE)

                # if (lExtractAccountTxns and lExtractAttachments_EAR) or (lExtractInvestmentTxns and lExtractAttachments_EIT):
                #     split_the_name = os.path.splitext(extract_filename)
                #     attachmentDir = split_the_name[0]+get_filename_addition()
                #     newName = attachmentDir+split_the_name[1]
                #     filename.setFile(newName)
                # else:
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
                    myPopupInformationBox(extract_data_frame_, "User chose to cancel or no file selected >>  So no Extract will be performed... ", "FILE EXPORT")
                elif str(csvfilename).endswith(".moneydance"):
                    myPrint("B", "User selected file:", csvfilename)
                    myPrint("B", "Sorry - User chose to use .moneydance extension - I will not allow it!... So no Extract will be performed...")
                    myPopupInformationBox(extract_data_frame_, "Sorry - User chose to use .moneydance extension - I will not allow it!... So no Extract will be performed...", "FILE EXPORT")
                    lDisplayOnly = True
                    csvfilename = None
                elif ".moneydance" in filename.getDirectory():
                    myPrint("B", "User selected file:", filename.getDirectory(), csvfilename)
                    myPrint("B", "Sorry - FileDialog() User chose to save file in .moneydance location. NOT Good practice so I will not allow it!... So no Extract will be performed...")
                    myPopupInformationBox(extract_data_frame_, "Sorry - FileDialog() User chose to save file in .moneydance location. NOT Good practice so I will not allow it!... So no Extract will be performed...", "FILE EXPORT")
                    lDisplayOnly = True
                    csvfilename = None
                else:
                    if not lDisplayOnly:
                        relativePath = os.path.splitext(csvfilename)[0]

                    csvfilename = os.path.join(filename.getDirectory(), filename.getFile())
                    scriptpath = str(filename.getDirectory())

                if not lDisplayOnly:
                    if os.path.exists(csvfilename) and os.path.isfile(csvfilename):
                        myPrint("DB", "WARNING: file exists,but assuming user said OK to overwrite..")

                if not lDisplayOnly:
                    if check_file_writable(csvfilename):
                        if lStripASCII:
                            myPrint("B", 'Will extract data to file: ', csvfilename, "(NOTE: Should drop non utf8 characters...)")
                        else:
                            myPrint("B", 'Will extract data to file: ', csvfilename, "...")
                        scriptpath = os.path.dirname(csvfilename)
                    else:
                        myPrint("B", "Sorry - I just checked and you do not have permissions to create this file:", csvfilename)
                        myPopupInformationBox(extract_data_frame_, "Sorry - I just checked and you do not have permissions to create this file: %s" % csvfilename, "FILE EXPORT")
                        csvfilename=""
                        lDisplayOnly = True
                        return

                    attachmentDir = None
                    if (lExtractAccountTxns and lExtractAttachments_EAR) or (lExtractInvestmentTxns and lExtractAttachments_EIT):
                        attachmentDir = os.path.splitext( csvfilename )[0]
                        if os.path.exists(attachmentDir):
                            myPrint("B", "Sorry - Attachment Directory already exists... I need to create it: %s" %attachmentDir)
                            myPopupInformationBox(extract_data_frame_, "Sorry - Attachment Directory already exists... I need to create it: %s" % attachmentDir, "ATTACHMENT DIRECTORY")
                            csvfilename=""
                            lDisplayOnly = True
                            return

                        try:
                            os.mkdir(attachmentDir)
                            myPrint("B", "Successfully created Attachment Directory: %s" %attachmentDir)
                            MyPopUpDialogBox(extract_data_frame_, theStatus="I have created Attachment Directory:", theMessage=attachmentDir, theWidth=200, theTitle="Info", lModal=True).go()

                        except:
                            myPrint("B", "Sorry - Failed to create Attachment Directory: %s",attachmentDir)
                            myPopupInformationBox(extract_data_frame_, "Sorry - Failed to create Attachment Directory: %s" % attachmentDir, "ATTACHMENT DIRECTORY")
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
            myPrint("DB", "No Export will be performed")

        # save here upfront - no need to do later
        save_StuWareSoftSystems_parameters_to_file()

        # ############################
        # START OF MAIN CODE EXECUTION
        # ############################

        if lExtractStockGlance2020:

            # ####################################################
            # STOCKGLANCE2020 EXECUTION
            # ####################################################
            def do_stockglance2020():
                global debug
                global decimalCharSep, lDidIUseAttachmentDir, csvfilename, myScriptName, lGlobalErrorDetected, lExit, lDisplayOnly
                global baseCurrency, sdf, rawDataTable, rawFooterTable, headingNames
                global StockGlanceInstance  # holds the instance of StockGlance2020()
                global _SHRS_FORMATTED, _SHRS_RAW, _PRICE_FORMATTED, _PRICE_RAW, _CVALUE_FORMATTED, _CVALUE_RAW, _BVALUE_FORMATTED, _BVALUE_RAW
                global _CBVALUE_FORMATTED, _CBVALUE_RAW, _GAIN_FORMATTED, _GAIN_RAW, _SORT, _EXCLUDECSV, _GAINPCT
                global acctSeparator

                global __extract_data, extract_data_frame_, extract_filename
                global lStripASCII, scriptpath, csvDelimiter, userdateformat, lWriteBOMToExportFile_SWSS
                global hideInactiveAccounts, hideHiddenAccounts, hideHiddenSecurities
                global lAllSecurity, filterForSecurity, lAllAccounts, filterForAccounts, lAllCurrency, filterForCurrency
                global whichDefaultExtractToRun_SWSS
                global lIncludeCashBalances, _column_widths_SG2020
                global lSplitSecuritiesByAccount, lExcludeTotalsFromCSV, lRoundPrice
                global lIncludeFutureBalances_SG2020

                def terminate_script():
                    global debug, extract_data_frame_, i_am_an_extension_so_run_headless, scriptExit, csvfilename, lDisplayOnly, lGlobalErrorDetected

                    myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

                    # We now do this earlier....
                    # try:
                    #     save_StuWareSoftSystems_parameters_to_file()
                    # except:
                    #     myPrint("B", "Error - failed to save parameters to pickle file...!")
                    #     dump_sys_error_to_md_console_and_errorlog()
                    #
                    if not lDisplayOnly and not lGlobalErrorDetected:
                        try:
                            helper = moneydance.getPlatformHelper()
                            helper.openDirectory(File(csvfilename))
                        except:
                            dump_sys_error_to_md_console_and_errorlog()

                    moneydance_ui.firstMainFrame.setStatus(">> StuWareSoftSystems - thanks for using >> %s......." %(myScriptName),0)
                    if not i_am_an_extension_so_run_headless: print(scriptExit)

                    try:
                        extract_data_frame_.dispose()
                    except:
                        myPrint("B","Error. Final dispose failed....?")
                        dump_sys_error_to_md_console_and_errorlog()

                    # Cleanup any mess and left-overs
                    foundFrames = JFrame.getFrames()
                    for frm in foundFrames:
                        if frm.getName().lower().startswith("extract_data"):
                            try:
                                myPrint("DB","Disposing left-over frame: %s" %(frm.getName()))
                                frm.dispose()
                            except:
                                pass

                    myPrint("B","Script/extension is terminating.....")

                    return

                class DoTheMenu(AbstractAction):

                    def __init__(self, menu):
                        self.menu = menu

                    def actionPerformed(self, event):																				# noqa
                        global extract_data_frame_, debug

                        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

                        if event.getActionCommand() == "About":
                            about_this_script()

                        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
                        return

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
                    moreCashBalanceAccounts = {}

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
                            myPrint("DB", "Result of sumInfoBySecurity(book) self.QtyOfSharesTable:        ", self.QtyOfSharesTable)
                            myPrint("DB", "Result of sumInfoBySecurity(book) self.AccountsTable:           ", self.AccountsTable)
                            myPrint("DB", "Result of sumInfoBySecurity(book) self.CashBalancesTable:       ", self.CashBalancesTable)
                            myPrint("DB", "Result of sumInfoBySecurity(book) self.CostBasisTotals:         ", self.CostBasisTotals)
                            myPrint("DB", "Result of sumInfoBySecurity(book) self.moreCashBalanceAccounts: ", self.moreCashBalanceAccounts)

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

                                _roundPrice = curr.getDecimalPlaces()
                                if lRoundPrice:
                                    price = round(1.0 / curr.adjustRateForSplitsInt(DateUtil.convertCalToInt(today),curr.getRelativeRate()), _roundPrice)       # noqa
                                else:
                                    price = (1.0 / curr.adjustRateForSplitsInt(DateUtil.convertCalToInt(today), curr.getRelativeRate()))                        # noqa

                                qty = self.QtyOfSharesTable.get(curr)
                                if qty is None: qty = 0

                                if lAllCurrency \
                                        or (filterForCurrency.upper().strip() in curr.getRelativeCurrency().getIDString().upper().strip()) \
                                        or (filterForCurrency.upper().strip() in curr.getRelativeCurrency().getName().upper().strip()):
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
                                                                                    _roundPrice))  # c3
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
                                                entry.append(split_acct_array[iSplitAcctArray][0].replace(acctSeparator, "",1))  # Acct
                                                entry.append(curr.getDoubleValue(qtySplit))  # _Shrs
                                                entry.append(price)  # _Price
                                                entry.append(x)  # _CValue
                                                entry.append(round(balanceBaseSplit, 2))  # _BValue
                                                entry.append(costBasisBaseSplit)  # _Cost Basis
                                                entry.append(gainBaseSplit)  # _Gain
                                                entry.append(curr.getName().upper() + "000" + split_acct_array[iSplitAcctArray][0].upper().replace(acctSeparator, "", 1))  # _SORT
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
                                                blankEntry.append(curr.getName().upper() + "555")
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
                                                                                _roundPrice))  # c3
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
                                            entry.append(curr.getName().upper() + "888")  # _SORT
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
                                                blankEntry.append(curr.getName().upper() + "999")
                                                blankEntry.append(lExcludeTotalsFromCSV)
                                                rawDataTable.append(blankEntry)

                                            self.totalBalance += round(balance, 2)  # You can round here if you like....
                                            self.totalBalanceBase += round(balanceBase, 2)  # You can round here if you like....

                                            self.totalCostBasisBase += costBasisBase
                                            self.totalGainBase += gainBase

                                            # if lIncludeCashBalances:
                                            #     cash = 0.0                                                                  # noqa
                                            #     # Search to see if Account exists/has been used already for Cash Balance - Only use once!
                                            #     acct_string = ""
                                            #     for keys in self.CashBalancesTable.keys():
                                            #         data = self.CashBalancesTable.get(keys)
                                            #         acct_array = self.AccountsTable.get(curr)
                                            #         for iArray in range(0, len(acct_array)):
                                            #             acct_string += acct_array[iArray][0]  # The account name
                                            #         # NEXT
                                            #         if (keys + acctSeparator) in acct_string:
                                            #             myPrint("D", "CashBal Search - Found:", keys, "in", self.AccountsTable.get(curr)f, "Cash Bal:", data)
                                            #             cash = data
                                            #             self.CashBalancesTable[keys] = 0.0  # Now delete it so it cannot be used again!
                                            #             self.totalCashBalanceBase = self.totalCashBalanceBase + cash
                                            #             self.CashBalanceTableData.append([keys, cash])
                                            #             continue
                                            #             # Keep searching as a Security may be used in many accounts...
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


                        # OK, throw in any extra cash balances
                        if lIncludeCashBalances:
                            for acct in self.moreCashBalanceAccounts.keys():
                                data = self.moreCashBalanceAccounts.get(acct)
                                myPrint("D", "Extra CashBal Search - Found:", acct, "Cash Bal:", data)
                                cash = data
                                self.totalCashBalanceBase += cash
                                self.CashBalanceTableData.append([acct, cash])
                                continue
                                # Keep searching as a Security may be used in many accounts...

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
                            for _iii in range(0, len(self.CashBalanceTableData)):
                                if self.CashBalanceTableData[_iii][1] != 0:
                                    entry = []
                                    entry.append("Cash Bal/Acct:")
                                    entry.append(None)
                                    entry.append(None)
                                    entry.append(None)
                                    entry.append(None)
                                    entry.append(None)
                                    entry.append(self.myNumberFormatter(self.CashBalanceTableData[_iii][1], True, baseCurrency, baseCurrency, 2))
                                    entry.append(None)
                                    entry.append(None)
                                    entry.append(None)
                                    entry.append(self.CashBalanceTableData[_iii][0].getAccountName())
                                    entry.append(None)  # Cost Basis
                                    entry.append(None)  # Gain
                                    entry.append(None)
                                    entry.append(self.CashBalanceTableData[_iii][1])
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
                            entry.append("** Across ALL Accounts **")
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

                    def sumInfoBySecurity(self, book):
                        global debug, hideInactiveAccounts, hideHiddenAccounts, lAllAccounts, filterForAccounts, lIncludeCashBalances
                        global lSplitSecuritiesByAccount, acctSeparator, i_am_an_extension_so_run_headless, lIncludeFutureBalances_SG2020

                        myPrint("D","In ", inspect.currentframe().f_code.co_name, "()")

                        totals = {}  # Dictionary <CurrencyType, Long>
                        accounts = {}
                        cashTotals = {}  # Dictionary<CurrencyType, Long>
                        cbbasistotals = {}

                        lDidIFindAny = False

                        # So this little bit is going to find the other accounts that have a cash balance...
                        if lIncludeCashBalances:
                            # noinspection PyUnresolvedReferences
                            moreCashAccounts = AccountUtil.allMatchesForSearch(book,self.MyAcctFilter(Account.AccountType.INVESTMENT,
                                                                                                      hideInactiveAccounts,
                                                                                                      lAllAccounts,
                                                                                                      filterForAccounts,
                                                                                                      hideHiddenAccounts,
                                                                                                      hideHiddenSecurities,
                                                                                                      lAllCurrency,
                                                                                                      filterForCurrency,
                                                                                                      lAllSecurity,
                                                                                                      filterForSecurity,
                                                                                                      None))
                            for acct in moreCashAccounts:
                                curr = acct.getCurrencyType()

                                if lIncludeFutureBalances_SG2020:
                                    cashTotal = curr.getDoubleValue((acct.getBalance())) / curr.getRate(None)
                                else:
                                    cashTotal = curr.getDoubleValue((acct.getCurrentBalance())) / curr.getRate(None)
                                myPrint("D","Cash balance for extra accounts searched:", cashTotal)

                                if cashTotal != 0:
                                    self.moreCashBalanceAccounts[acct] = round(cashTotal,2)


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
                                        accounts[curr] = [[acct.getParentAccount().getAccountName() + acctSeparator, _getBalance, getTheCostBasis]]
                                    else:
                                        account.append([acct.getParentAccount().getAccountName() + acctSeparator, _getBalance, getTheCostBasis])
                                        accounts[curr] = account
                                else:
                                    if account is None:
                                        account = acct.getParentAccount().getAccountName() + acctSeparator  # Important - keep the trailing ' :'
                                    else:
                                        account = account[0][0] + acct.getParentAccount().getAccountName() + acctSeparator  # concatenate two strings here
                                    accounts[curr] = [[account, _getBalance, getTheCostBasis]]

                            # if lIncludeCashBalances:
                            #
                            #     # If we found cash balance for the security parent, then delete it from the other list...
                            #     self.moreCashBalanceAccounts.pop(acct.getParentAccount(),None)
                            #
                            #     # Now get the Currency  for the Security Parent Account - to get Cash  Balance
                            #     curr = acct.getParentAccount().getCurrencyType()
                            #
                            #     # WARNING Cash balances are by Account and not by Security!
                            #     if lIncludeFutureBalances_SG2020:
                            #         cashTotal = curr.getDoubleValue((acct.getParentAccount().getBalance())) / curr.getRate(None)  # Will be the same Cash balance per account for all Securities..
                            #     else:
                            #         cashTotal = curr.getDoubleValue((acct.getParentAccount().getCurrentBalance())) / curr.getRate(None)  # Will be the same Cash balance per account for all Securities..
                            #     myPrint("D","Cash balance for account:", cashTotal)
                            #     cashTotals[acct.getParentAccount()] = round(cashTotal, 2)

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

                            renderer.setVerticalAlignment(JLabel.CENTER)

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
                                self):  # by default everything gets converted to strings. We need to fix this and code for my string number formats
                            global _SHRS_FORMATTED, _SHRS_RAW, _PRICE_FORMATTED, _PRICE_RAW, _CVALUE_FORMATTED, _CVALUE_RAW, _BVALUE_FORMATTED, _BVALUE_RAW, _SORT
                            global _CBVALUE_FORMATTED, _CBVALUE_RAW, _GAIN_FORMATTED, _GAIN_RAW, _EXCLUDECSV, _GAINPCT

                            sorter = TableRowSorter()
                            self.setRowSorter(sorter)
                            sorter.setModel(self.getModel())
                            for _iii in range(0, self.getColumnCount()):
                                if _iii == _SHRS_FORMATTED:
                                    sorter.setComparator(_iii, self.MyTextNumberComparator("N"))
                                elif _iii == _PRICE_FORMATTED:
                                    sorter.setComparator(_iii, self.MyTextNumberComparator("N"))
                                elif _iii == _CVALUE_FORMATTED:
                                    sorter.setComparator(_iii, self.MyTextNumberComparator("N"))
                                elif _iii == _BVALUE_FORMATTED:
                                    sorter.setComparator(_iii, self.MyTextNumberComparator("N"))
                                elif _iii == _CBVALUE_FORMATTED:
                                    sorter.setComparator(_iii, self.MyTextNumberComparator("N"))
                                elif _iii == _GAIN_FORMATTED:
                                    sorter.setComparator(_iii, self.MyTextNumberComparator("N"))
                                elif _iii == _SORT:
                                    sorter.setComparator(_iii, self.MyTextNumberComparator("N"))
                                elif _iii == _GAINPCT:
                                    sorter.setComparator(_iii, self.MyTextNumberComparator("%"))
                                else:
                                    sorter.setComparator(_iii, self.MyTextNumberComparator("T"))
                            self.getRowSorter().toggleSortOrder(1)

                        def prepareRenderer(self, renderer, row, column):                                                   # noqa
                            # make Banded rows
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

                            for _iii in range(0, sourceModel.getColumnCount()):
                                targetModel.getColumn(_iii).setPreferredWidth(sourceModel.getColumn(_iii).getWidth())

                                # Saving for later... Yummy!!
                                _column_widths_SG2020[_iii] = sourceModel.getColumn(_iii).getWidth()
                                myPrint("D","Saving column %s as width %s for later..." %(_iii,_column_widths_SG2020[_iii]))

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
                        def __init__(self, theFrame):
                            self.theFrame = theFrame        # type: MyJFrame

                        def windowClosing(self, WindowEvent):                                                           # noqa
                            global debug, extract_data_frame_
                            myPrint("D","In ", inspect.currentframe().f_code.co_name, "()")
                            terminate_script()

                        def windowClosed(self, WindowEvent):                                                                       # noqa
                            global debug

                            myPrint("D","In ", inspect.currentframe().f_code.co_name, "()")

                            self.theFrame.isActiveInMoneydance = False

                            myPrint("DB","applistener is %s" %(classPrinter("MoneydanceAppListener", self.theFrame.MoneydanceAppListener)))

                            if self.theFrame.MoneydanceAppListener is not None:
                                try:
                                    moneydance.removeAppEventListener(self.theFrame.MoneydanceAppListener)
                                    myPrint("DB","\n@@@ Removed my MD App Listener... %s\n" %(classPrinter("MoneydanceAppListener", self.theFrame.MoneydanceAppListener)))
                                    self.theFrame.MoneydanceAppListener = None
                                except:
                                    myPrint("B","FAILED to remove my MD App Listener... %s" %(classPrinter("MoneydanceAppListener", self.theFrame.MoneydanceAppListener)))
                                    dump_sys_error_to_md_console_and_errorlog()

                            if self.theFrame.HomePageViewObj is not None:
                                self.theFrame.HomePageViewObj.unload()
                                myPrint("DB","@@ Called HomePageView.unload() and Removed reference to HomePageView %s from MyJFrame()...@@\n" %(classPrinter("HomePageView", self.theFrame.HomePageViewObj)))
                                self.theFrame.HomePageViewObj = None

                            myPrint("D","Exit ", inspect.currentframe().f_code.co_name, "()")


                    class CloseAction(AbstractAction):
                        def actionPerformed(self, event):                                                               # noqa
                            global debug, extract_data_frame_
                            myPrint("D","In ", inspect.currentframe().f_code.co_name, "()")
                            terminate_script()

                    def createAndShowGUI(self):
                        global debug, extract_data_frame_, rawDataTable, rawFooterTable, lDisplayOnly, version_build, lSplitSecuritiesByAccount, _column_widths_SG2020
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
                            # extract_data_frame_ = JFrame("extract_data(StockGlance2020) - StuWareSoftSystems(build: %s)..." % version_build)
                            extract_data_frame_.setTitle("extract_data(StockGlance2020) - StuWareSoftSystems(build: %s)..." % version_build)
                        else:
                            # extract_data_frame_ = JFrame("extract_data(StockGlance2020) - StuWareSoftSystems(build: %s)... (NOTE: your file has already been exported)" % version_build)
                            extract_data_frame_.setTitle("extract_data(StockGlance2020) - StuWareSoftSystems(build: %s)... (NOTE: your file has already been exported)" % version_build)
                        extract_data_frame_.setName(u"%s_main_stockglance2020" %(myModuleID))

                        if (not Platform.isMac()):
                            moneydance_ui.getImages()
                            extract_data_frame_.setIconImage(MDImages.getImage(moneydance_ui.getMain().getSourceInformation().getIconResource()))

                        # extract_data_frame_.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE)
                        extract_data_frame_.setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE)  # The CloseAction() and WindowListener() will handle dispose() - else change back to DISPOSE_ON_CLOSE

                        shortcut = Toolkit.getDefaultToolkit().getMenuShortcutKeyMaskEx()

                        # Add standard CMD-W keystrokes etc to close window
                        extract_data_frame_.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_W, shortcut), "close-window")
                        extract_data_frame_.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_F4, shortcut), "close-window")
                        extract_data_frame_.getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0), "close-window")
                        extract_data_frame_.getRootPane().getActionMap().put("close-window", self.CloseAction())

                        extract_data_frame_.addWindowListener(self.WindowListener(extract_data_frame_))

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


                        fontSize = self.table.getFont().getSize()+5
                        self.table.setRowHeight(fontSize)
                        self.table.setRowMargin(0)
                        myPrint("DB","Setting main table row height to %s and intercellspacing to 0" %fontSize)

                        fontSize = self.footerTable.getFont().getSize()+5
                        self.footerTable.setRowHeight(fontSize)
                        self.footerTable.setRowMargin(0)
                        myPrint("DB","Setting footer table row height to %s and intercellspacing to 0" %fontSize)

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

                        for _iii in range(0, _SHRS_RAW): tcm.getColumn(_iii).setPreferredWidth(myDefaultWidths[_iii])

                        # I'm hiding these columns for ease of data retrieval. The better option would be to remove the columns
                        for _iii in reversed(range(_SHRS_RAW, tcm.getColumnCount())):
                            tcm.getColumn(_iii).setMinWidth(0)
                            tcm.getColumn(_iii).setMaxWidth(0)
                            tcm.getColumn(_iii).setWidth(0)
                            self.table.removeColumn(tcm.getColumn(_iii))
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

                        for _iii in range(0, _SHRS_RAW): tcm.getColumn(_iii).setPreferredWidth(myDefaultWidths[_iii])

                        # I'm hiding these columns for ease of data retrieval. The better option would be to remove the columns
                        for _iii in reversed(range(_SHRS_RAW, tcm.getColumnCount())):
                            tcm.getColumn(_iii).setMinWidth(0)
                            tcm.getColumn(_iii).setMaxWidth(0)
                            tcm.getColumn(_iii).setWidth(0)
                            self.footerTable.removeColumn(tcm.getColumn(_iii))
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

                        extract_data_frame_.add(self.scrollPane, BorderLayout.CENTER)

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
                        fcalcScrollPaneHeightRequired = min(250,
                             (((frowCount * frowHeight) + ((frowCount + 1) * finterCellSpacing) + fheaderHeight + finsets.top + finsets.bottom + fscrollHeight.height)))
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
                        extract_data_frame_.add(self.footerScrollPane, BorderLayout.SOUTH)

                        myPrint("D","Total frame height required: ", calcScrollPaneHeightRequired, " + ",
                                fcalcScrollPaneHeightRequired, "+ Intercells: ", finsets.top, finsets.bottom, " = ",
                                (calcScrollPaneHeightRequired + fcalcScrollPaneHeightRequired) +
                                (finsets.top * 2) + (finsets.bottom * 2))

                        # Seems to be working well without setting the frame sizes + pack()
                        # extract_data_frame_.setPreferredSize(Dimension(width, max(150,calcScrollPaneHeightRequired+fcalcScrollPaneHeightRequired+(finsets.top*2)+(finsets.bottom*2))))
                        # extract_data_frame_.setSize(width,calcScrollPaneHeightRequired+fcalcScrollPaneHeightRequired)   # for some reason this seems irrelevant?

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

                        extract_data_frame_.setJMenuBar(mb)

                        if Platform.isOSX():
                            System.setProperty("apple.laf.useScreenMenuBar", save_useScreenMenuBar)                                 # noqa

                        extract_data_frame_.pack()
                        extract_data_frame_.setLocationRelativeTo(None)
                        extract_data_frame_.setVisible(True)

                        try:
                            extract_data_frame_.MoneydanceAppListener = MyEventListener(extract_data_frame_)
                            moneydance.addAppEventListener(extract_data_frame_.MoneydanceAppListener)
                            myPrint("DB","@@ added AppEventListener() %s @@" %(classPrinter("MoneydanceAppListener", extract_data_frame_.MoneydanceAppListener)))
                        except:
                            myPrint("B","FAILED to add MD App Listener...")
                            dump_sys_error_to_md_console_and_errorlog()

                        extract_data_frame_.isActiveInMoneydance = True

                        if True or Platform.isOSX():
                            # extract_data_frame_.setAlwaysOnTop(True)
                            extract_data_frame_.toFront()

                        return True

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
                    # * Subclasses may override this method to provide custom content or
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
                    def getTableCellRendererComponent(self, table, value, isSelected, hasFocus, row, column):               # noqa
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
                    def _getIcon(self, _table, column):
                        sortKey = self.getSortKey(_table, column)
                        if (sortKey is not None and _table.convertColumnIndexToView(sortKey.getColumn()) == column):
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
                            global debug, extract_data_frame_, rawDataTable, rawFooterTable, headingNames, csvfilename, decimalCharSep, groupingCharSep, csvDelimiter, version_build
                            global lSplitSecuritiesByAccount, lExcludeTotalsFromCSV, myScriptName, lRoundPrice, lGlobalErrorDetected, lIncludeFutureBalances_SG2020
                            global lWriteBOMToExportFile_SWSS

                            global _SHRS_FORMATTED, _SHRS_RAW, _PRICE_FORMATTED, _PRICE_RAW, _CVALUE_FORMATTED, _CVALUE_RAW, _BVALUE_FORMATTED, _BVALUE_RAW, _SORT
                            global _CBVALUE_FORMATTED, _CBVALUE_RAW, _GAIN_FORMATTED, _GAIN_RAW, _EXCLUDECSV, _GAINPCT

                            myPrint("D","In ", inspect.currentframe().f_code.co_name, "()")

                            # NOTE - You can add sep=; to beginning of file to tell Excel what delimiter you are using
                            if not lSplitSecuritiesByAccount:
                                rawDataTable = sorted(rawDataTable, key=lambda x: (x[1].upper()))

                            rawDataTable.insert(0,headingNames)  # Insert Column Headings at top of list. A bit rough and ready, not great coding, but a short list...!

                            for _iii in range(0, len(rawFooterTable)):
                                rawDataTable.append(rawFooterTable[_iii])

                            # Write the csvlines to a file
                            myPrint("B", "Opening file and writing ", len(rawDataTable), " records")

                            try:
                                # CSV Writer will take care of special characters / delimiters within fields by wrapping in quotes that Excel will decode
                                with open(csvfilename,"wb") as csvfile:  # PY2.7 has no newline parameter so opening in binary; just use "w" and newline='' in PY3.0

                                    if lWriteBOMToExportFile_SWSS:
                                        csvfile.write(codecs.BOM_UTF8)   # This 'helps' Excel open file with double-click as UTF-8

                                    writer = csv.writer(csvfile, dialect='excel', quoting=csv.QUOTE_MINIMAL, delimiter=fix_delimiter(csvDelimiter))

                                    if csvDelimiter != ",":
                                        writer.writerow(["sep=",""])  # Tells Excel to open file with the alternative delimiter (it will add the delimiter to this line)

                                    writer.writerow(rawDataTable[0][:_SHRS_RAW])  # Print the header, but not the extra _field headings

                                    for _iii in range(1, len(rawDataTable)):
                                        if not rawDataTable[_iii][_EXCLUDECSV]:
                                            # Write the table, but swap in the raw numbers (rather than formatted number strings)
                                            try:
                                                writer.writerow([
                                                    fixFormatsStr(rawDataTable[_iii][0], False),
                                                    fixFormatsStr(rawDataTable[_iii][1], False),
                                                    fixFormatsStr(rawDataTable[_iii][_SHRS_RAW], True),
                                                    fixFormatsStr(rawDataTable[_iii][_PRICE_RAW], True),
                                                    fixFormatsStr(rawDataTable[_iii][4], False),
                                                    fixFormatsStr(rawDataTable[_iii][_CVALUE_RAW], True),
                                                    fixFormatsStr(rawDataTable[_iii][_BVALUE_RAW], True),
                                                    fixFormatsStr(rawDataTable[_iii][_CBVALUE_RAW], True),
                                                    fixFormatsStr(rawDataTable[_iii][_GAIN_RAW], True),
                                                    fixFormatsStr(rawDataTable[_iii][_GAINPCT], True, "%"),
                                                    fixFormatsStr(rawDataTable[_iii][10], False),
                                                    ""])
                                            except:
                                                dump_sys_error_to_md_console_and_errorlog()
                                                myPrint("B", "ERROR writing to CSV on row %s. Please review console" %_iii)
                                                myPrint("B", rawDataTable[_iii])
                                                myPopupInformationBox(extract_data_frame_,"ERROR writing to CSV on row %s. Please review console" %_iii)
                                                ConsoleWindow.showConsoleWindow(moneydance_ui)
                                                raise Exception("Aborting")
                                            # ENDIF
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
                                myPopupInformationBox(extract_data_frame_,"Sorry - error writing to export file!", "FILE EXTRACT")
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
                            myPopupInformationBox(extract_data_frame_,"Your extract has been created as requested",myScriptName)

            do_stockglance2020()


        elif lExtractReminders:

            # ####################################################
            # EXTRACT_REMINDERS_CSV EXECUTION
            # ####################################################

            def do_extract_reminders():
                global debug
                global decimalCharSep, lDidIUseAttachmentDir, csvfilename, myScriptName, lGlobalErrorDetected, lExit, lDisplayOnly
                global baseCurrency, sdf, csvlines, csvheaderline, headerFormats
                global table, focus, row, scrollpane, EditedReminderCheck, ReminderTable_Count, ExtractDetails_Count

                global __extract_data, extract_data_frame_, extract_filename
                global lStripASCII, scriptpath, csvDelimiter, userdateformat, lWriteBOMToExportFile_SWSS
                global hideInactiveAccounts, hideHiddenAccounts, hideHiddenSecurities
                global lAllSecurity, filterForSecurity, lAllAccounts, filterForAccounts, lAllCurrency, filterForCurrency
                global whichDefaultExtractToRun_SWSS
                global _column_widths_ERTC

                def terminate_script():
                    global debug, extract_data_frame_, lDisplayOnly, lGlobalErrorDetected

                    myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

                    # try:
                    #     save_StuWareSoftSystems_parameters_to_file()
                    # except:
                    #     myPrint("B", "Error - failed to save parameters to pickle file...!")
                    #     dump_sys_error_to_md_console_and_errorlog()
                    #
                    if not lDisplayOnly:
                        try:
                            ExportDataToFile()
                            if not lGlobalErrorDetected:
                                myPopupInformationBox(extract_data_frame_, "Your extract has been created as requested", myScriptName)
                                try:
                                    helper = moneydance.getPlatformHelper()
                                    helper.openDirectory(File(csvfilename))
                                except:
                                    pass
                        except:
                            lGlobalErrorDetected = True
                            myPopupInformationBox(extract_data_frame_, "ERROR WHILST CREATING EXPORT! Review Console Log", myScriptName)
                            dump_sys_error_to_md_console_and_errorlog()

                    moneydance_ui.firstMainFrame.setStatus(">> StuWareSoftSystems - thanks for using >> %s......." %(myScriptName),0)
                    if not i_am_an_extension_so_run_headless: print(scriptExit)

                    try:
                        extract_data_frame_.dispose()
                    except:
                        myPrint("B","Error. Final dispose failed....?")
                        dump_sys_error_to_md_console_and_errorlog()


                    # Cleanup any mess and left-overs
                    foundFrames = JFrame.getFrames()
                    for frm in foundFrames:
                        if frm.getName().lower().startswith("extract_data"):
                            try:
                                myPrint("DB","Disposing left-over frame: %s" %(frm.getName()))
                                frm.dispose()
                            except:
                                pass

                    myPrint("B","Script/extension is terminating.....")
                    return

                class DoTheMenu(AbstractAction):

                    def __init__(self, menu):
                        self.menu = menu

                    def actionPerformed(self, event):																				# noqa
                        global extract_data_frame_, debug

                        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

                        if event.getActionCommand().lower().startswith("refresh"):
                            RefreshMenuAction().refresh()

                        if event.getActionCommand().lower().startswith("extract") or event.getActionCommand().lower().startswith("close"):
                            ExtractMenuAction().extract_or_close()

                        if event.getActionCommand() == "About":
                            about_this_script()

                        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
                        return

                # Moneydance dates  are int yyyymmddd - convert to locale date string for CSV format
                def dateoutput(dateinput, theformat):

                    if dateinput == "EXPIRED": _dateoutput = dateinput
                    elif dateinput == "": _dateoutput = ""
                    elif dateinput == 0: _dateoutput = ""
                    elif dateinput == "0": _dateoutput = ""
                    else:
                        dateasdate = datetime.datetime.strptime(str(dateinput), "%Y%m%d")  # Convert to Date field
                        _dateoutput = dateasdate.strftime(theformat)

                    return _dateoutput

                def build_the_data_file(ind):
                    global sdf, userdateformat, csvlines, csvheaderline, myScriptName, baseCurrency, headerFormats
                    global debug, ExtractDetails_Count

                    ExtractDetails_Count += 1

                    myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", ind, " - On iteration/call: ", ExtractDetails_Count)

                    # ind == 1 means that this is a repeat call, so the table should be refreshed

                    root = moneydance.getCurrentAccountBook()

                    baseCurrency = moneydance_data.getCurrencies().getBaseType()

                    rems = root.getReminders().getAllReminders()

                    if rems.size() < 1:
                        return False

                    myPrint("B", 'Success: read ', rems.size(), 'reminders')
                    print
                    csvheaderline = [
                        "Number#",
                        "NextDue",
                        "ReminderType",
                        "Frequency",
                        "AutoCommitDays",
                        "LastAcknowledged",
                        "FirstDate",
                        "EndDate",
                        "ReminderDescription",
                        "NetAmount",
                        "TxfrType",
                        "Account",
                        "MainDescription",
                        "Split#",
                        "SplitAmount",
                        "Category",
                        "Description",
                        "Memo"
                    ]

                    headerFormats = [[Number,JLabel.CENTER],
                                     [String,JLabel.CENTER],
                                     [String,JLabel.LEFT],
                                     [String,JLabel.LEFT],
                                     [String,JLabel.LEFT],
                                     [String,JLabel.CENTER],
                                     [String,JLabel.CENTER],
                                     [String,JLabel.CENTER],
                                     [String,JLabel.LEFT],
                                     [Number,JLabel.RIGHT],
                                     [String,JLabel.LEFT],
                                     [String,JLabel.LEFT],
                                     [String,JLabel.LEFT],
                                     [String,JLabel.CENTER],
                                     [Number,JLabel.RIGHT],
                                     [String,JLabel.LEFT],
                                     [String,JLabel.LEFT],
                                     [String,JLabel.LEFT]
                                     ]

                    # Read each reminder and create a csv line for each in the csvlines array
                    csvlines = []  # Set up an empty array

                    for index in range(0, int(rems.size())):
                        rem = rems[index]  # Get the reminder

                        remtype = rem.getReminderType()  # NOTE or TRANSACTION
                        desc = rem.getDescription().replace(",", " ")  # remove commas to keep csv format happy
                        memo = str(rem.getMemo()).replace(",", " ").strip()  # remove commas to keep csv format happy
                        memo = str(memo).replace("\n", "*").strip()  # remove newlines to keep csv format happy

                        myPrint("P", "Reminder: ", index + 1, rem.getDescription())  # Name of Reminder

                        # determine the frequency of the transaction
                        daily = rem.getRepeatDaily()
                        weekly = rem.getRepeatWeeklyModifier()
                        monthly = rem.getRepeatMonthlyModifier()
                        yearly = rem.getRepeatYearly()
                        countfreqs = 0

                        remfreq = ''

                        if daily > 0:
                            remfreq += 'DAILY'
                            remfreq += '(every ' + str(daily) + ' days)'
                            countfreqs += 1

                        if len(rem.getRepeatWeeklyDays()) > 0 and rem.getRepeatWeeklyDays()[0] > 0:
                            for freq in range(0, len(rem.getRepeatWeeklyDays())):
                                if len(remfreq) > 0: remfreq += " & "
                                if weekly == Reminder.WEEKLY_EVERY:                remfreq += 'WEEKLY_EVERY'
                                if weekly == Reminder.WEEKLY_EVERY_FIFTH:            remfreq += 'WEEKLY_EVERY_FIFTH'
                                if weekly == Reminder.WEEKLY_EVERY_FIRST:            remfreq += 'WEEKLY_EVERY_FIRST'
                                if weekly == Reminder.WEEKLY_EVERY_FOURTH:            remfreq += 'WEEKLY_EVERY_FOURTH'
                                if weekly == Reminder.WEEKLY_EVERY_LAST:            remfreq += 'WEEKLY_EVERY_LAST'
                                if weekly == Reminder.WEEKLY_EVERY_SECOND:            remfreq += 'WEEKLY_EVERY_SECOND'
                                if weekly == Reminder.WEEKLY_EVERY_THIRD:            remfreq += 'WEEKLY_EVERY_THIRD'

                                if rem.getRepeatWeeklyDays()[freq] == 1: remfreq += '(on Sunday)'
                                if rem.getRepeatWeeklyDays()[freq] == 2: remfreq += '(on Monday)'
                                if rem.getRepeatWeeklyDays()[freq] == 3: remfreq += '(on Tuesday)'
                                if rem.getRepeatWeeklyDays()[freq] == 4: remfreq += '(on Wednesday)'
                                if rem.getRepeatWeeklyDays()[freq] == 5: remfreq += '(on Thursday)'
                                if rem.getRepeatWeeklyDays()[freq] == 6: remfreq += '(on Friday)'
                                if rem.getRepeatWeeklyDays()[freq] == 7: remfreq += '(on Saturday)'
                                if rem.getRepeatWeeklyDays()[freq] < 1 or rem.getRepeatWeeklyDays()[
                                    freq] > 7: remfreq += '(*ERROR*)'
                                countfreqs += 1

                        if len(rem.getRepeatMonthly()) > 0 and rem.getRepeatMonthly()[0] > 0:
                            for freq in range(0, len(rem.getRepeatMonthly())):
                                if len(remfreq) > 0: remfreq += " & "
                                if monthly == Reminder.MONTHLY_EVERY:                 remfreq += 'MONTHLY_EVERY'
                                if monthly == Reminder.MONTHLY_EVERY_FOURTH:         remfreq += 'MONTHLY_EVERY_FOURTH'
                                if monthly == Reminder.MONTHLY_EVERY_OTHER:         remfreq += 'MONTHLY_EVERY_OTHER'
                                if monthly == Reminder.MONTHLY_EVERY_SIXTH:         remfreq += 'MONTHLY_EVERY_SIXTH'
                                if monthly == Reminder.MONTHLY_EVERY_THIRD:         remfreq += 'MONTHLY_EVERY_THIRD'

                                theday = rem.getRepeatMonthly()[freq]
                                if theday == Reminder.LAST_DAY_OF_MONTH:
                                    remfreq += '(on LAST_DAY_OF_MONTH)'
                                else:
                                    if 4 <= theday <= 20 or 24 <= theday <= 30: suffix = "th"
                                    else:                                        suffix = ["st", "nd", "rd"][theday % 10 - 1]

                                    remfreq += '(on ' + str(theday) + suffix + ')'

                                countfreqs += 1

                        if yearly:
                            if len(remfreq) > 0: remfreq += " & "
                            remfreq += 'YEARLY'
                            countfreqs += 1

                        if len(
                                remfreq) < 1 or countfreqs == 0:         remfreq = '!ERROR! NO ACTUAL FREQUENCY OPTIONS SET PROPERLY ' + remfreq
                        if countfreqs > 1: remfreq = "**MULTI** " + remfreq

                        lastdate = rem.getLastDateInt()
                        if lastdate < 1:  # Detect if an enddate is set
                            remdate = str(rem.getNextOccurance(20991231))  # Use cutoff  far into the future
                        else:        remdate = str(rem.getNextOccurance(rem.getLastDateInt()))  # Stop at enddate

                        if lastdate < 1: lastdate = ''

                        if remdate == '0': remdate = "EXPIRED"

                        lastack = rem.getDateAcknowledgedInt()
                        if lastack == 0 or lastack == 19700101: lastack = ''

                        auto = rem.getAutoCommitDays()
                        if auto >= 0:    auto = 'YES: (' + str(auto) + ' days before scheduled)'
                        else:            auto = 'NO'

                        if str(remtype) == 'NOTE':
                            csvline = []
                            csvline.append(index + 1)
                            csvline.append(dateoutput(remdate, userdateformat))
                            csvline.append(str(rem.getReminderType()))
                            csvline.append(remfreq)
                            csvline.append(auto)
                            csvline.append(dateoutput(lastack, userdateformat))
                            csvline.append(dateoutput(rem.getInitialDateInt(), userdateformat))
                            csvline.append(dateoutput(lastdate, userdateformat))
                            csvline.append(desc)
                            csvline.append('')  # NetAmount
                            csvline.append('')  # TxfrType
                            csvline.append('')  # Account
                            csvline.append('')  # MainDescription
                            csvline.append(str(index + 1) + '.0')  # Split#
                            csvline.append('')  # SplitAmount
                            csvline.append('')  # Category
                            csvline.append('')  # Description
                            csvline.append('"' + memo + '"')  # Memo
                            csvlines.append(csvline)

                        elif str(remtype) == 'TRANSACTION':
                            txnparent = rem.getTransaction()
                            amount = baseCurrency.getDoubleValue(txnparent.getValue())

                            for index2 in range(0, int(txnparent.getOtherTxnCount())):
                                splitdesc = txnparent.getOtherTxn(index2).getDescription().replace(","," ")  # remove commas to keep csv format happy
                                splitmemo = txnparent.getMemo().replace(",", " ")  # remove commas to keep csv format happy
                                maindesc = txnparent.getDescription().replace(",", " ").strip()

                                if index2 > 0: amount = ''  # Don't repeat the new amount on subsequent split lines (so you can total column). The split amount will be correct

                                stripacct = str(txnparent.getAccount()).replace(",",
                                                                                " ").strip()  # remove commas to keep csv format happy
                                stripcat = str(txnparent.getOtherTxn(index2).getAccount()).replace(","," ").strip()  # remove commas to keep csv format happy

                                csvline = []
                                csvline.append(index + 1)
                                csvline.append(dateoutput(remdate, userdateformat))
                                csvline.append(str(rem.getReminderType()))
                                csvline.append(remfreq)
                                csvline.append(auto)
                                csvline.append(dateoutput(lastack, userdateformat))
                                csvline.append(dateoutput(rem.getInitialDateInt(), userdateformat))
                                csvline.append(dateoutput(lastdate, userdateformat))
                                csvline.append(desc)
                                csvline.append((amount))
                                csvline.append(txnparent.getTransferType())
                                csvline.append(stripacct)
                                csvline.append(maindesc)
                                csvline.append(str(index + 1) + '.' + str(index2 + 1))
                                csvline.append(baseCurrency.getDoubleValue(txnparent.getOtherTxn(index2).getValue()) * -1)
                                csvline.append(stripcat)
                                csvline.append(splitdesc)
                                csvline.append(splitmemo)
                                csvlines.append(csvline)

                        index += 1

                    ReminderTable(csvlines, ind)

                    myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name)
                    ExtractDetails_Count -= 1

                    return True

                # ENDDEF

                # Synchronises column widths of both JTables
                class ColumnChangeListener(TableColumnModelListener):
                    sourceTable = None
                    targetTable = None

                    def __init__(self, source):
                        self.sourceTable = source

                    def columnAdded(self, e): pass

                    def columnSelectionChanged(self, e): pass

                    def columnRemoved(self, e): pass

                    def columnMoved(self, e): pass

                    # noinspection PyUnusedLocal
                    def columnMarginChanged(self, e):
                        global _column_widths_ERTC

                        sourceModel = self.sourceTable.getColumnModel()

                        for _iii in range(0, sourceModel.getColumnCount()):
                            # Saving for later... Yummy!!
                            _column_widths_ERTC[_iii] = sourceModel.getColumn(_iii).getWidth()
                            myPrint("D","Saving column %s as width %s for later..." %(_iii,_column_widths_ERTC[_iii]))

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
                        self.setHorizontalTextPosition(JLabel.RIGHT)  # This positions the  text to the  left/right of  the sort icon
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

                    def getTableCellRendererComponent(self, table, value, isSelected, hasFocus, row, column):				# noqa
                        # noinspection PyUnresolvedReferences
                        super(DefaultTableHeaderCellRenderer, self).getTableCellRendererComponent(table, value, isSelected,hasFocus, row, column)
                        # tableHeader = table.getTableHeader()
                        # if (tableHeader is not None): self.setForeground(tableHeader.getForeground())
                        align = table.getCellRenderer(0, column).getHorizontalAlignment()
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
                    def _getIcon(self, table, column):																		# noqa
                        sortKey = self.getSortKey(table, column)
                        if (sortKey is not None and table.convertColumnIndexToView(sortKey.getColumn()) == column):
                            x = (sortKey.getSortOrder())
                            if x == SortOrder.ASCENDING: return UIManager.getIcon("Table.ascendingSortIcon")
                            elif x == SortOrder.DESCENDING: return UIManager.getIcon("Table.descendingSortIcon")
                            elif x == SortOrder.UNSORTED: return UIManager.getIcon("Table.naturalSortIcon")
                        return None

                    # enddef

                    # /**
                    # * returns the current sort key, or null if the column is unsorted.
                    # *
                    # * @param table the table
                    # * @param column the column index
                    # * @return the SortKey, or null if the column is unsorted
                    # */
                    # noinspection PyMethodMayBeStatic
                    # noinspection PyUnusedLocal
                    def getSortKey(self, table, column):																	# noqa
                        rowSorter = table.getRowSorter()
                        if (rowSorter is None): return None
                        sortedColumns = rowSorter.getSortKeys()
                        if (sortedColumns.size() > 0): return sortedColumns.get(0)
                        return None

                focus = "initial"
                row = 0
                EditedReminderCheck = False
                ReminderTable_Count = 0
                ExtractDetails_Count = 0

                class CloseAction(AbstractAction):
                    # noinspection PyMethodMayBeStatic
                    # noinspection PyUnusedLocal
                    def actionPerformed(self, event):
                        global extract_data_frame_, debug
                        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

                        terminate_script()

                class WindowListener(WindowAdapter):
                    def __init__(self, theFrame):
                        self.theFrame = theFrame        # type: MyJFrame

                    def windowClosing(self, WindowEvent):                                                               # noqa
                        global debug, extract_data_frame_
                        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

                        terminate_script()

                    def windowClosed(self, WindowEvent):                                                                       # noqa
                        global debug

                        myPrint("D","In ", inspect.currentframe().f_code.co_name, "()")

                        self.theFrame.isActiveInMoneydance = False

                        myPrint("DB","applistener is %s" %(classPrinter("MoneydanceAppListener", self.theFrame.MoneydanceAppListener)))

                        if self.theFrame.MoneydanceAppListener is not None:
                            try:
                                moneydance.removeAppEventListener(self.theFrame.MoneydanceAppListener)
                                myPrint("DB","\n@@@ Removed my MD App Listener... %s\n" %(classPrinter("MoneydanceAppListener", self.theFrame.MoneydanceAppListener)))
                                self.theFrame.MoneydanceAppListener = None
                            except:
                                myPrint("B","FAILED to remove my MD App Listener... %s" %(classPrinter("MoneydanceAppListener", self.theFrame.MoneydanceAppListener)))
                                dump_sys_error_to_md_console_and_errorlog()

                        if self.theFrame.HomePageViewObj is not None:
                            self.theFrame.HomePageViewObj.unload()
                            myPrint("DB","@@ Called HomePageView.unload() and Removed reference to HomePageView %s from MyJFrame()...@@\n" %(classPrinter("HomePageView", self.theFrame.HomePageViewObj)))
                            self.theFrame.HomePageViewObj = None

                        myPrint("D","Exit ", inspect.currentframe().f_code.co_name, "()")

                    # noinspection PyMethodMayBeStatic
                    # noinspection PyUnusedLocal
                    def windowGainedFocus(self, WindowEvent):                                                           # noqa
                        global focus, table, row, debug, EditedReminderCheck

                        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

                        if focus == "lost":
                            focus = "gained"
                            if EditedReminderCheck:  # Disable refresh data on all gained-focus events, just refresh if Reminder is Edited...
                                # To always refresh data remove this if statement and always run ExtractDetails(1)
                                myPrint("DB", "pre-build_the_data_file()")
                                build_the_data_file(1)  # Re-extract data when window focus gained - assume something changed
                                myPrint("DB", "back from build_the_data_file(), gained focus, row: ", row)
                                EditedReminderCheck = False
                            table.setRowSelectionInterval(0, row)
                            cellRect = table.getCellRect(row, 0, True)
                            table.scrollRectToVisible(cellRect)  # force the scrollpane to make the row visible
                            table.requestFocus()

                        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
                        return

                    # noinspection PyMethodMayBeStatic
                    # noinspection PyUnusedLocal
                    def windowLostFocus(self, WindowEvent):                                                             # noqa
                        global focus, table, row, debug

                        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

                        row = table.getSelectedRow()

                        if focus == "gained": focus = "lost"

                        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
                        return

                WL = WindowListener(extract_data_frame_)

                class MouseListener(MouseAdapter):
                    # noinspection PyMethodMayBeStatic
                    def mousePressed(self, event):
                        global table, row, debug
                        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")
                        clicks = event.getClickCount()
                        if clicks == 2:
                            row = table.getSelectedRow()
                            index = table.getValueAt(row, 0)
                            ShowEditForm(index)
                        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
                        return

                ML = MouseListener()

                class EnterAction(AbstractAction):
                    # noinspection PyMethodMayBeStatic
                    # noinspection PyUnusedLocal
                    def actionPerformed(self, event):
                        global focus, table, row, debug
                        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")
                        row = table.getSelectedRow()
                        index = table.getValueAt(row, 0)
                        ShowEditForm(index)
                        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
                        return

                class ExtractMenuAction():
                    def __init__(self):
                        pass

                    # noinspection PyMethodMayBeStatic
                    def extract_or_close(self):
                        global extract_data_frame_, debug
                        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")
                        myPrint("D", "inside ExtractMenuAction() ;->")

                        terminate_script()

                class RefreshMenuAction():
                    def __init__(self):
                        pass

                    # noinspection PyMethodMayBeStatic
                    def refresh(self):
                        global extract_data_frame_, table, row, debug
                        row = 0  # reset to row 1
                        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "\npre-extract details(1), row: ", row)
                        build_the_data_file(1)  # Re-extract data
                        myPrint("D", "back from extractdetails(1), row: ", row)
                        table.setRowSelectionInterval(0, row)
                        table.requestFocus()
                        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
                        return

                class MyJTable(JTable):
                    myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

                    def __init__(self, tableModel):
                        global debug
                        super(JTable, self).__init__(tableModel)
                        self.fixTheRowSorter()

                    # noinspection PyMethodMayBeStatic
                    # noinspection PyUnusedLocal
                    def isCellEditable(self, row, column):																	# noqa
                        return False

                    #  Rendering depends on row (i.e. security's currency) as well as column
                    # noinspection PyUnusedLocal
                    # noinspection PyMethodMayBeStatic
                    def getCellRenderer(self, row, column):																	# noqa
                        global headerFormats

                        if column == 0:
                            renderer = MyPlainNumberRenderer()
                        elif headerFormats[column][0] == Number:
                            renderer = MyNumberRenderer()
                        else:
                            renderer = DefaultTableCellRenderer()

                        renderer.setHorizontalAlignment(headerFormats[column][1])

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

                            # if debug: print str1, str2, self.lSortNumber, self.lSortRealNumber, type(str1), type(str2)

                            if isinstance(str1, (float,int)) or isinstance(str2,(float,int)):
                                if str1 is None or str1 == "": str1 = 0
                                if str2 is None or str2 == "": str2 = 0
                                if (str1) > (str2):
                                    return 1
                                elif str1 == str2:
                                    return 0
                                else:
                                    return -1

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

                    def fixTheRowSorter(self):  # by default everything gets converted to strings. We need to fix this and code for my string number formats

                        sorter = TableRowSorter()
                        self.setRowSorter(sorter)
                        sorter.setModel(self.getModel())
                        for _iii in range(0, self.getColumnCount()):
                            if _iii == 0:
                                sorter.setComparator(_iii, self.MyTextNumberComparator("%"))
                            if _iii == 9 or _iii == 14:
                                sorter.setComparator(_iii, self.MyTextNumberComparator("N"))
                            else:
                                sorter.setComparator(_iii, self.MyTextNumberComparator("T"))
                        self.getRowSorter().toggleSortOrder(0)

                    # make Banded rows
                    def prepareRenderer(self, renderer, row, column):  														# noqa

                        lightLightGray = Color(0xDCDCDC)
                        # noinspection PyUnresolvedReferences
                        component = super(MyJTable, self).prepareRenderer(renderer, row, column)
                        if not self.isRowSelected(row):
                            component.setBackground(self.getBackground() if row % 2 == 0 else lightLightGray)

                        return component

                # This copies the standard class and just changes the colour to RED if it detects a negative - leaves field intact
                # noinspection PyArgumentList
                class MyNumberRenderer(DefaultTableCellRenderer):
                    global baseCurrency

                    def __init__(self):
                        super(DefaultTableCellRenderer, self).__init__()

                    def setValue(self, value):
                        global decimalCharSep

                        myGreen = Color(0,102,0)

                        if isinstance(value, (float,int)):
                            if value < 0.0:
                                self.setForeground(Color.RED)
                            else:
                                # self.setForeground(Color.DARK_GRAY)
                                self.setForeground(myGreen)  # DARK_GREEN
                            self.setText(baseCurrency.formatFancy(int(value*100), decimalCharSep, True))
                        else:
                            self.setText(str(value))

                        return

                # noinspection PyArgumentList
                class MyPlainNumberRenderer(DefaultTableCellRenderer):
                    global baseCurrency

                    def __init__(self):
                        super(DefaultTableCellRenderer, self).__init__()

                    def setValue(self, value):

                        self.setText(str(value))

                        return

                def ReminderTable(tabledata, ind):
                    global extract_data_frame_, scrollpane, table, row, debug, ReminderTable_Count, csvheaderline, lDisplayOnly
                    global _column_widths_ERTC

                    ReminderTable_Count += 1
                    myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", ind, "  - On iteration/call: ", ReminderTable_Count)

                    myDefaultWidths = [70,95,110,150,150,95,95,95,120,100,80,100,150,50,100,150,150,150]

                    validCount=0
                    lInvalidate=True
                    if _column_widths_ERTC is not None and isinstance(_column_widths_ERTC,(list)) and len(_column_widths_ERTC) == len(myDefaultWidths):
                        # if sum(_column_widths_ERTC)<1:
                        for width in _column_widths_ERTC:
                            if width >= 0 and width <= 1000:																	# noqa
                                validCount += 1

                    if validCount == len(myDefaultWidths): lInvalidate=False

                    if lInvalidate:
                        myPrint("DB","Found invalid saved columns = resetting to defaults")
                        myPrint("DB","Found: %s" %_column_widths_ERTC)
                        myPrint("DB","Resetting to: %s" %myDefaultWidths)
                        _column_widths_ERTC = myDefaultWidths
                    else:
                        myPrint("DB","Valid column widths loaded - Setting to: %s" %_column_widths_ERTC)
                        myDefaultWidths = _column_widths_ERTC


                    # allcols = col0 + col1 + col2 + col3 + col4 + col5 + col6 + col7 + col8 + col9 + col10 + col11 + col12 + col13 + col14 + col15 + col16 + col17
                    allcols = sum(myDefaultWidths)

                    screenSize = Toolkit.getDefaultToolkit().getScreenSize()

                    # button_width = 220
                    # button_height = 40
                    # frame_width = min(screenSize.width-20, allcols + 100)
                    # frame_height = min(screenSize.height, 900)

                    frame_width = min(screenSize.width-20, max(1024,int(round(moneydance_ui.firstMainFrame.getSize().width *.95,0))))
                    frame_height = min(screenSize.height-20, max(768, int(round(moneydance_ui.firstMainFrame.getSize().height *.95,0))))

                    frame_width = min( allcols+100, frame_width)

                    # panel_width = frame_width - 50
                    # button_panel_height = button_height + 5

                    if ind == 1:    scrollpane.getViewport().remove(table)  # On repeat, just remove/refresh the table & rebuild the viewport

                    colnames = csvheaderline

                    table = MyJTable(DefaultTableModel(tabledata, colnames))

                    if ind == 0:  # Function can get called multiple times; only set main frames up once

                        JFrame.setDefaultLookAndFeelDecorated(True)
                        # extract_data_frame_ = JFrame("extract_data(Reminders) - StuWareSoftSystems(build: %s)..." % version_build)
                        extract_data_frame_.setTitle("extract_data(Reminders) - StuWareSoftSystems(build: %s)..." % version_build)
                        extract_data_frame_.setName(u"%s_main_reminders" %myModuleID)
                        # extract_data_frame_.setLayout(FlowLayout())

                        if (not Platform.isMac()):
                            moneydance_ui.getImages()
                            extract_data_frame_.setIconImage(MDImages.getImage(moneydance_ui.getMain().getSourceInformation().getIconResource()))

                        # extract_data_frame_.setPreferredSize(Dimension(frame_width, frame_height))
                        # extract_data_frame_.setExtendedState(JFrame.MAXIMIZED_BOTH)

                        extract_data_frame_.setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE)

                        shortcut = Toolkit.getDefaultToolkit().getMenuShortcutKeyMaskEx()

                        # Add standard CMD-W keystrokes etc to close window
                        extract_data_frame_.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_W, shortcut), "close-window")
                        extract_data_frame_.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_F4, shortcut), "close-window")
                        extract_data_frame_.getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0), "close-window")
                        extract_data_frame_.getRootPane().getActionMap().put("close-window", CloseAction())

                        extract_data_frame_.addWindowFocusListener(WL)
                        extract_data_frame_.addWindowListener(WL)

                        if Platform.isOSX():
                            save_useScreenMenuBar= System.getProperty("apple.laf.useScreenMenuBar")
                            System.setProperty("apple.laf.useScreenMenuBar", "false")

                        mb = JMenuBar()

                        menuO = JMenu("<html><B>OPTIONS</b></html>")

                        menuItemR = JMenuItem("Refresh Data/Default Sort")
                        menuItemR.setToolTipText("Refresh (re-extract) the data, revert to default sort  order....")
                        menuItemR.addActionListener(DoTheMenu(menuO))
                        menuItemR.setEnabled(True)
                        menuO.add(menuItemR)

                        if not lDisplayOnly:
                            menuItemE = JMenuItem("Extract to CSV")
                            menuItemE.setToolTipText("Extract the data to CSV and exit....")
                        else:
                            menuItemE = JMenuItem("Close Window")
                            menuItemE.setToolTipText("Exit and close the window")

                        menuItemE.addActionListener(DoTheMenu(menuO))
                        menuItemE.setEnabled(True)
                        menuO.add(menuItemE)

                        mb.add(menuO)

                        menuH = JMenu("<html><B>ABOUT</b></html>")

                        menuItemA = JMenuItem("About")
                        menuItemA.setToolTipText("About...")
                        menuItemA.addActionListener(DoTheMenu(menuH))
                        menuItemA.setEnabled(True)
                        menuH.add(menuItemA)

                        mb.add(menuH)

                        extract_data_frame_.setJMenuBar(mb)

                        if Platform.isOSX():
                            System.setProperty("apple.laf.useScreenMenuBar", save_useScreenMenuBar)                                 # noqa

                    table.getTableHeader().setReorderingAllowed(True)  # no more drag and drop columns, it didn't work (on the footer)
                    table.getTableHeader().setDefaultRenderer(DefaultTableHeaderCellRenderer())
                    table.selectionMode = ListSelectionModel.SINGLE_SELECTION

                    fontSize = table.getFont().getSize()+5
                    table.setRowHeight(fontSize)
                    table.setRowMargin(0)

                    table.getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke("ENTER"), "Enter")
                    table.getActionMap().put("Enter", EnterAction())

                    for _iii in range(0, table.getColumnModel().getColumnCount()):
                        table.getColumnModel().getColumn(_iii).setPreferredWidth(myDefaultWidths[_iii])

                    cListener1 = ColumnChangeListener(table)
                    # Put the listener here - else it sets the defaults wrongly above....
                    table.getColumnModel().addColumnModelListener(cListener1)


                    table.getTableHeader().setBackground(Color.LIGHT_GRAY)

                    # table.setAutoCreateRowSorter(True) # DON'T DO THIS - IT WILL OVERRIDE YOUR NICE CUSTOM SORT

                    table.addMouseListener(ML)

                    if ind == 0:
                        scrollpane = JScrollPane(JScrollPane.VERTICAL_SCROLLBAR_ALWAYS, JScrollPane.HORIZONTAL_SCROLLBAR_ALWAYS)  # On first call, create the scrollpane
                        scrollpane.setBorder(CompoundBorder(MatteBorder(1, 1, 1, 1, Color.gray), EmptyBorder(0, 0, 0, 0)))
                    # scrollpane.setPreferredSize(Dimension(frame_width-20, frame_height-20	))

                    table.setPreferredScrollableViewportSize(Dimension(frame_width-20, frame_height-100))
                    #
                    table.setAutoResizeMode(JTable.AUTO_RESIZE_OFF)
                    #
                    scrollpane.setViewportView(table)
                    if ind == 0:
                        extract_data_frame_.add(scrollpane)
                        extract_data_frame_.pack()
                        extract_data_frame_.setLocationRelativeTo(None)

                        try:
                            extract_data_frame_.MoneydanceAppListener = MyEventListener(extract_data_frame_)
                            moneydance.addAppEventListener(extract_data_frame_.MoneydanceAppListener)
                            myPrint("DB","@@ added AppEventListener() %s @@" %(classPrinter("MoneydanceAppListener", extract_data_frame_.MoneydanceAppListener)))
                        except:
                            myPrint("B","FAILED to add MD App Listener...")
                            dump_sys_error_to_md_console_and_errorlog()

                        extract_data_frame_.isActiveInMoneydance = True

                        if True or Platform.isOSX():
                            # extract_data_frame_.setAlwaysOnTop(True)
                            extract_data_frame_.toFront()

                    extract_data_frame_.setVisible(True)

                    myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
                    ReminderTable_Count -= 1

                    return

                def ShowEditForm(item):
                    global debug, EditedReminderCheck
                    myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")
                    reminders = moneydance_data.getReminders()
                    reminder = reminders.getAllReminders()[item-1]
                    myPrint("D", "Calling MD EditRemindersWindow() function...")
                    EditRemindersWindow.editReminder(None, moneydance_ui, reminder)
                    EditedReminderCheck = True
                    myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
                    return

                if build_the_data_file(0):

                    focus = "gained"																							# noqa

                    table.setRowSelectionInterval(0, row)
                    table.requestFocus()

                    if not lDisplayOnly:
                        def ExportDataToFile():
                            global debug, csvfilename, decimalCharSep, groupingCharSep, csvDelimiter, version_build, myScriptName
                            global sdf, userdateformat, csvlines, csvheaderline, lGlobalErrorDetected, extract_data_frame_
                            global lWriteBOMToExportFile_SWSS

                            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

                            # NOTE - You can add sep=; to beginning of file to tell Excel what delimiter you are using
                            # noinspection PyUnreachableCode
                            if False:
                                csvlines = sorted(csvlines, key=lambda x: (str(x[1]).upper()))

                            csvlines.insert(0,csvheaderline)  # Insert Column Headings at top of list. A bit rough and ready, not great coding, but a short list...!

                            # Write the csvlines to a file
                            myPrint("B", "Opening file and writing ", len(csvlines), "records")

                            try:
                                # CSV Writer will take care of special characters / delimiters within fields by wrapping in quotes that Excel will decode
                                with open(csvfilename,"wb") as csvfile:  # PY2.7 has no newline parameter so opening in binary; just use "w" and newline='' in PY3.0

                                    if lWriteBOMToExportFile_SWSS:
                                        csvfile.write(codecs.BOM_UTF8)   # This 'helps' Excel open file with double-click as UTF-8

                                    writer = csv.writer(csvfile, dialect='excel', quoting=csv.QUOTE_MINIMAL, delimiter=fix_delimiter(csvDelimiter))

                                    if csvDelimiter != ",":
                                        writer.writerow(["sep=",""])  # Tells Excel to open file with the alternative delimiter (it will add the delimiter to this line)

                                    for _iii in range(0, len(csvlines)):
                                        # Write the table, but swap in the raw numbers (rather than formatted number strings)
                                        try:
                                            writer.writerow([
                                                fixFormatsStr(csvlines[_iii][0], False),
                                                fixFormatsStr(csvlines[_iii][1], True),
                                                fixFormatsStr(csvlines[_iii][2], False),
                                                fixFormatsStr(csvlines[_iii][3], False),
                                                fixFormatsStr(csvlines[_iii][4], False),
                                                fixFormatsStr(csvlines[_iii][5], False),
                                                fixFormatsStr(csvlines[_iii][6], False),
                                                fixFormatsStr(csvlines[_iii][7], False),
                                                fixFormatsStr(csvlines[_iii][8], False),
                                                fixFormatsStr(csvlines[_iii][9], True),
                                                fixFormatsStr(csvlines[_iii][10], False),
                                                fixFormatsStr(csvlines[_iii][11], False),
                                                fixFormatsStr(csvlines[_iii][12], False),
                                                fixFormatsStr(csvlines[_iii][13], False),
                                                fixFormatsStr(csvlines[_iii][14], True),
                                                fixFormatsStr(csvlines[_iii][15], False),
                                                fixFormatsStr(csvlines[_iii][16], False),
                                                fixFormatsStr(csvlines[_iii][17], False),
                                                ""])
                                        except:
                                            dump_sys_error_to_md_console_and_errorlog()
                                            myPrint("B", "ERROR writing to CSV on row %s. Please review console" %_iii)
                                            myPrint("B", csvlines[_iii])
                                            myPopupInformationBox(extract_data_frame_,"ERROR writing to CSV on row %s. Please review console" %_iii)
                                            ConsoleWindow.showConsoleWindow(moneydance_ui)
                                            raise Exception("Aborting")
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
                                    writer.writerow(["Date format................: %s" %(userdateformat)])

                                myPrint("B", "CSV file " + csvfilename + " created, records written, and file closed..")

                            except IOError, e:
                                lGlobalErrorDetected = True
                                myPrint("B", "Oh no - File IO Error!", e)
                                myPrint("B", "Path:", csvfilename)
                                myPrint("B", "!!! ERROR - No file written - sorry! (was file open, permissions etc?)".upper())
                                dump_sys_error_to_md_console_and_errorlog()
                                myPopupInformationBox(extract_data_frame_, "Sorry - error writing to export file!", "FILE EXTRACT")
                        # enddef

                        def fixFormatsStr(theString, lNumber, sFormat=""):
                            global lStripASCII

                            if isinstance(theString, (int,float)):
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

                else:
                    myPopupInformationBox(extract_data_frame_,"You have no reminders to display or extract!",myScriptName)

            do_extract_reminders()

        elif not lDisplayOnly:

            if lExtractAccountTxns:
                # ##############################################
                # EXTRACT_ACCOUNT_REGISTERS_CSV EXECUTION
                # ##############################################

                def do_extract_account_registers():
                    global debug
                    global decimalCharSep, lDidIUseAttachmentDir, csvfilename, myScriptName, lGlobalErrorDetected, lExit, lDisplayOnly
                    global baseCurrency, sdf
                    global transactionTable, dataKeys, attachmentDir, relativePath

                    global __extract_data, extract_data_frame_, extract_filename
                    global lStripASCII, scriptpath, csvDelimiter, userdateformat, lWriteBOMToExportFile_SWSS
                    global hideInactiveAccounts, hideHiddenAccounts, hideHiddenSecurities
                    global lAllSecurity, filterForSecurity, lAllAccounts, filterForAccounts, lAllCurrency, filterForCurrency
                    global whichDefaultExtractToRun_SWSS
                    global lIncludeSubAccounts_EAR, lIncludeOpeningBalances_EAR, userdateStart_EAR, userdateEnd_EAR, lAllTags_EAR, tagFilter_EAR
                    global lAllText_EAR, textFilter_EAR, lExtractAttachments_EAR, saveDropDownAccountUUID_EAR, saveDropDownDateRange_EAR, lIncludeInternalTransfers_EAR

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

                    _msg = MyPopUpDialogBox(extract_data_frame_, "PLEASE WAIT....", "", 100, "Building Database", False)
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

                    transactionTable = []

                    myPrint("DB", dataKeys)

                    rootbook = moneydance.getCurrentAccountBook()

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
                    iAttachmentErrors=0

                    iCount = 0
                    iCountAttachmentsDownloaded = 0
                    uniqueFileNumber = 1

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

                    copyValidAccountList = ArrayList()
                    if lIncludeOpeningBalances_EAR:
                        for acctBal in validAccountList:
                            if acctBal.getStartBalance() != 0:
                                if userdateStart_EAR <= acctBal.getCreationDateInt() <= userdateEnd_EAR:
                                    copyValidAccountList.add(acctBal)

                    for txn in txns:

                        if not (userdateStart_EAR <= txn.getDateInt() <= userdateEnd_EAR):
                            continue

                        lParent = isinstance(txn, ParentTxn)

                        parent_Txn = txn.getParentTxn()
                        txnAcct = txn.getAccount()
                        acctCurr = txnAcct.getCurrencyType()  # Currency of the txn

                        # Only include opening balances if not filtering records.... (this is caught during parameter selection earlier)
                        if lIncludeOpeningBalances_EAR:

                            if txnAcct in copyValidAccountList:
                                copyValidAccountList.remove(txnAcct)

                            if accountBalances.get(txnAcct):
                                pass
                            else:
                                accountBalances[txnAcct] = True
                                if userdateStart_EAR <= txnAcct.getCreationDateInt() <= userdateEnd_EAR:
                                    openBal = acctCurr.getDoubleValue(txnAcct.getStartBalance())
                                    if openBal != 0:
                                        iBal+=1
                                        _row = ([None] * dataKeys["_END"][0])  # Create a blank row to be populated below...
                                        _row[dataKeys["_KEY"][_COLUMN]] = txnAcct.getUUID()
                                        _row[dataKeys["_ACCOUNTTYPE"][_COLUMN]] = str(txnAcct.getAccountType())
                                        _row[dataKeys["_ACCOUNT"][_COLUMN]] = txnAcct.getFullAccountName()
                                        _row[dataKeys["_CURR"][_COLUMN]] = acctCurr.getIDString()
                                        _row[dataKeys["_DESC"][_COLUMN]] = "MANUAL OPENING BALANCE"
                                        _row[dataKeys["_CHEQUE"][_COLUMN]] = "MANUAL"
                                        _row[dataKeys["_DATE"][_COLUMN]] = txnAcct.getCreationDateInt()
                                        _row[dataKeys["_SPLITIDX"][_COLUMN]] = 0
                                        if acctCurr == baseCurrency:
                                            _row[dataKeys["_TOTALAMOUNT"][_COLUMN]] = openBal
                                            _row[dataKeys["_SPLITAMOUNT"][_COLUMN]] = openBal
                                        else:
                                            _row[dataKeys["_TOTALAMOUNT"][_COLUMN]] = round(openBal / acctCurr.getRate(baseCurrency),2)
                                            _row[dataKeys["_SPLITAMOUNT"][_COLUMN]] = round(openBal / acctCurr.getRate(baseCurrency),2)
                                            _row[dataKeys["_FOREIGNTOTALAMOUNT"][_COLUMN]] = openBal
                                            _row[dataKeys["_FOREIGNSPLITAMOUNT"][_COLUMN]] = openBal


                                        myPrint("D", _row)
                                        transactionTable.append(_row)

                        keyIndex = 0
                        _row = ([None] * dataKeys["_END"][0])  # Create a blank row to be populated below...

                        txnKey = txn.getUUID()
                        _row[dataKeys["_KEY"][_COLUMN]] = txnKey + "-" + str(keyIndex).zfill(3)

                        _row[dataKeys["_ACCOUNTTYPE"][_COLUMN]] = str(txnAcct.getAccountType())
                        _row[dataKeys["_ACCOUNT"][_COLUMN]] = txnAcct.getFullAccountName()
                        _row[dataKeys["_CURR"][_COLUMN]] = acctCurr.getIDString()
                        _row[dataKeys["_DATE"][_COLUMN]] = txn.getDateInt()
                        if parent_Txn.getTaxDateInt() != txn.getDateInt():
                            _row[dataKeys["_TAXDATE"][_COLUMN]] = txn.getTaxDateInt()

                        _row[dataKeys["_CHEQUE"][_COLUMN]] = txn.getCheckNumber()

                        _row[dataKeys["_DESC"][_COLUMN]] = parent_Txn.getDescription()
                        if lParent:
                            _row[dataKeys["_MEMO"][_COLUMN]] = txn.getMemo()
                        else:
                            _row[dataKeys["_MEMO"][_COLUMN]] = txn.getDescription()
                        _row[dataKeys["_CLEARED"][_COLUMN]] = txn.getStatusChar()


                        if acctCurr == baseCurrency:
                            _row[dataKeys["_TOTALAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(txn.getValue())
                        else:
                            if lParent:
                                _row[dataKeys["_FOREIGNTOTALAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(txn.getValue())
                                localValue = getTotalLocalValue( txn )
                                _row[dataKeys["_TOTALAMOUNT"][_COLUMN]] = localValue
                            else:
                                _row[dataKeys["_FOREIGNTOTALAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(txn.getValue())
                                _row[dataKeys["_TOTALAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(txn.getAmount())

                        _row[dataKeys["_PARENTHASATTACHMENTS"][_COLUMN]] = parent_Txn.hasAttachments()
                        if str(parent_Txn.getKeywords()) != "[]": _row[dataKeys["_PARENTTAGS"][_COLUMN]] = str(parent_Txn.getKeywords())

                        lNeedToPrintTotalAmount = True

                        for _ii in range(0, int(parent_Txn.getOtherTxnCount())):        # If a split, then it will always make it here...

                            if not lParent and _ii > 0: break

                            splitRowCopy = deepcopy(_row)

                            if lParent:

                                if (not lAllTags_EAR
                                        and not tag_search(tagFilter_EAR, txn.getKeywords())
                                        and not tag_search(tagFilter_EAR, parent_Txn.getOtherTxn(_ii).getKeywords())):
                                    continue

                                if (not lAllText_EAR
                                        and textFilter_EAR not in (parent_Txn.getDescription().upper().strip()
                                                                   +txn.getMemo().upper().strip()
                                                                   +parent_Txn.getOtherTxn(_ii).getDescription().upper()).strip()):
                                    continue

                                splitMemo = parent_Txn.getOtherTxn(_ii).getDescription()
                                splitTags = str(parent_Txn.getOtherTxn(_ii).getKeywords())
                                splitCat = parent_Txn.getOtherTxn(_ii).getAccount().getFullAccountName()
                                splitHasAttachments = parent_Txn.getOtherTxn(_ii).hasAttachments()

                                splitFAmount = None
                                if parent_Txn.getOtherTxn(_ii).getAmount() != parent_Txn.getOtherTxn(_ii).getValue():
                                    splitFAmount = acctCurr.getDoubleValue(parent_Txn.getOtherTxn(_ii).getValue()) * -1
                                    splitAmount = acctCurr.getDoubleValue(parent_Txn.getOtherTxn(_ii).getAmount()) * -1
                                else:
                                    splitAmount = acctCurr.getDoubleValue(parent_Txn.getOtherTxn(_ii).getValue()) * -1

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
                                splitCat = parent_Txn.getAccount().getFullAccountName()
                                splitHasAttachments = txn.hasAttachments()


                                splitFAmount = None
                                if txn.getAmount() != txn.getValue():
                                    splitFAmount = acctCurr.getDoubleValue(txn.getValue())
                                    splitAmount = acctCurr.getDoubleValue(txn.getAmount())
                                else:
                                    splitAmount = acctCurr.getDoubleValue(txn.getValue())

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

                            if lNeedToPrintTotalAmount:
                                lNeedToPrintTotalAmount = False
                            else:
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
                            attachmentKeys = holdTheKeys                                                                # noqa
                            attachmentLocations = holdTheLocations
                            uniqueFileString=" "*5
                            for attachmentLocation in attachmentLocations:
                                uniqueFileString = str(uniqueFileNumber).strip().zfill(5)
                                outputFile = os.path.join(attachmentDir,str(uniqueFileString)+"-"+os.path.basename(attachmentLocation) )
                                try:
                                    _ostr = FileOutputStream( File(outputFile) )
                                    bytesCopied = _local_storage.readFile(attachmentLocation, _ostr)
                                    _ostr.close()
                                    myPrint("DB","Attachment %s bytes >> %s copied to %s" %(bytesCopied, attachmentLocation,outputFile))
                                    attachmentFileList.append(outputFile)
                                    iCountAttachmentsDownloaded += 1
                                    lDidIUseAttachmentDir = True
                                except:
                                    iAttachmentErrors+=1
                                    myPrint("B","ERROR - Could not extract %s" %(attachmentLocation))

                                uniqueFileNumber += 1

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

                    if lIncludeOpeningBalances_EAR and len(copyValidAccountList)>0:
                        myPrint("DB","Now iterating remaining %s Accounts with no txns for balances...." %(len(copyValidAccountList)))

                        # Yes I should just move this section from above so the code is not inefficient....
                        for acctBal in copyValidAccountList:

                            acctCurr = acctBal.getCurrencyType()  # Currency of the acct
                            openBal = acctCurr.getDoubleValue(acctBal.getStartBalance())

                            iBal+=1
                            _row = ([None] * dataKeys["_END"][0])  # Create a blank row to be populated below...
                            _row[dataKeys["_KEY"][_COLUMN]] = acctBal.getUUID()
                            _row[dataKeys["_ACCOUNTTYPE"][_COLUMN]] = str(acctBal.getAccountType())
                            _row[dataKeys["_ACCOUNT"][_COLUMN]] = acctBal.getFullAccountName()
                            _row[dataKeys["_CURR"][_COLUMN]] = acctCurr.getIDString()
                            _row[dataKeys["_DESC"][_COLUMN]] = "MANUAL OPENING BALANCE"
                            _row[dataKeys["_CHEQUE"][_COLUMN]] = "MANUAL"
                            _row[dataKeys["_DATE"][_COLUMN]] = acctBal.getCreationDateInt()
                            _row[dataKeys["_SPLITIDX"][_COLUMN]] = 0
                            if acctCurr == baseCurrency:
                                _row[dataKeys["_TOTALAMOUNT"][_COLUMN]] = openBal
                                _row[dataKeys["_SPLITAMOUNT"][_COLUMN]] = openBal
                            else:
                                _row[dataKeys["_TOTALAMOUNT"][_COLUMN]] = round(openBal / acctCurr.getRate(baseCurrency),2)
                                _row[dataKeys["_SPLITAMOUNT"][_COLUMN]] = round(openBal / acctCurr.getRate(baseCurrency),2)
                                _row[dataKeys["_FOREIGNTOTALAMOUNT"][_COLUMN]] = openBal
                                _row[dataKeys["_FOREIGNSPLITAMOUNT"][_COLUMN]] = openBal

                            myPrint("D", _row)
                            transactionTable.append(_row)

                    myPrint("P","")
                    myPrint("B", "Account Register Transaction Records (Parents, Splits, Attachments) selected:", len(transactionTable) )

                    if iCountAttachmentsDownloaded:
                        myPrint("B", ".. and I downloaded %s attachments for you too" %iCountAttachmentsDownloaded )

                    if iBal: myPrint("B", "...and %s Manual Opening Balance entries created too..." %iBal)

                    if iAttachmentErrors: myPrint("B", "@@ ...and %s Attachment Errors..." %iAttachmentErrors)
                    ###########################################################################################################

                    myPrint("P","Sorting... please wait....")
                    # sort the file:
                    transactionTable = sorted(transactionTable, key=lambda x: (x[dataKeys["_ACCOUNTTYPE"][_COLUMN]],
                                                                               x[dataKeys["_ACCOUNT"][_COLUMN]],
                                                                               x[dataKeys["_DATE"][_COLUMN]],
                                                                               x[dataKeys["_KEY"][_COLUMN]],
                                                                               x[dataKeys["_SPLITIDX"][_COLUMN]]) )
                    ###########################################################################################################


                    def ExportDataToFile(statusMsg):
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
                        for _theRow in transactionTable:
                            # try:
                            dateasdate = datetime.datetime.strptime(str(_theRow[dataKeys["_DATE"][_COLUMN]]), "%Y%m%d")  # Convert to Date field
                            _dateoutput = dateasdate.strftime(userdateformat)
                            _theRow[dataKeys["_DATE"][_COLUMN]] = _dateoutput
                            # except:
                            #     myPrint("B","Logic error post-processing _DATE on row: %s" %_row)

                            if _theRow[dataKeys["_TAXDATE"][_COLUMN]]:
                                dateasdate = datetime.datetime.strptime(str(_theRow[dataKeys["_TAXDATE"][_COLUMN]]), "%Y%m%d")  # Convert to Date field
                                _dateoutput = dateasdate.strftime(userdateformat)
                                _theRow[dataKeys["_TAXDATE"][_COLUMN]] = _dateoutput

                            for col in range(0, dataKeys["_ATTACHMENTLINK"][_COLUMN]):  # DO NOT MESS WITH ATTACHMENT LINK NAMES!!
                                _theRow[col] = fixFormatsStr(_theRow[col])

                        # NOTE - You can add sep= to beginning of file to tell Excel what delimiter you are using

                        # Write the csvlines to a file
                        myPrint("B", "Opening file and writing ", len(transactionTable), "records")


                        try:
                            # CSV Writer will take care of special characters / delimiters within fields by wrapping in quotes that Excel will decode
                            with open(csvfilename,"wb") as csvfile:  # PY2.7 has no newline parameter so opening in binary just use "w" and newline='' in PY3.0

                                if lWriteBOMToExportFile_SWSS:
                                    csvfile.write(codecs.BOM_UTF8)   # This 'helps' Excel open file with double-click as UTF-8

                                writer = csv.writer(csvfile, dialect='excel', quoting=csv.QUOTE_MINIMAL, delimiter=fix_delimiter(csvDelimiter))

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
                                    # writer.writerow(["FILE:///"])  # This attempts to allow access to whole folder subsystem....
                                    writer.writerow([""])

                                if lExtractAttachments_EAR:
                                    writer.writerow(headings[:dataKeys["_KEY"][_COLUMN]])  # Print the header, but not the extra _field headings
                                else:
                                    writer.writerow(headings[:dataKeys["_ATTACHMENTLINKREL"][_COLUMN]])  # Print the header, but not the extra _field headings

                                try:
                                    for i in range(0, len(transactionTable)):
                                        if lExtractAttachments_EAR:
                                            writer.writerow(transactionTable[i][:dataKeys["_KEY"][_COLUMN]])
                                        else:
                                            writer.writerow(transactionTable[i][:dataKeys["_ATTACHMENTLINKREL"][_COLUMN]])
                                except:
                                    dump_sys_error_to_md_console_and_errorlog()
                                    myPrint("B", "ERROR writing to CSV on row %s. Please review console" %i)
                                    myPrint("B", transactionTable[i])
                                    statusMsg.kill()
                                    myPopupInformationBox(extract_data_frame_,"ERROR writing to CSV on row %s. Please review console" %i)
                                    ConsoleWindow.showConsoleWindow(moneydance_ui)
                                    raise Exception("Aborting")

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
                                writer.writerow(["Date range.................: %s" %(saveDropDownDateRange_EAR)])
                                writer.writerow(["Selected Start Date........: %s" %(userdateStart_EAR)])
                                writer.writerow(["Selected End Date..........: %s" %(userdateEnd_EAR)])
                                writer.writerow(["user date format...........: %s" %(userdateformat)])

                            myPrint("B", "CSV file " + csvfilename + " created, records written, and file closed..")

                        except IOError, e:
                            lGlobalErrorDetected = True
                            myPrint("B", "Oh no - File IO Error!", e)
                            myPrint("B", "Path:", csvfilename)
                            myPrint("B", "!!! ERROR - No file written - sorry! (was file open, permissions etc?)".upper())
                            dump_sys_error_to_md_console_and_errorlog()
                            myPopupInformationBox(extract_data_frame_, "Sorry - error writing to export file!", "FILE EXTRACT")

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
                        # theString = theString.replace(";", "*")
                        # theString = theString.replace(",", "*")
                        # theString = theString.replace("|", "*")

                        if lStripASCII:
                            all_ASCII = ''.join(char for char in theString if ord(char) < 128)  # Eliminate non ASCII printable Chars too....
                        else:
                            all_ASCII = theString
                        return all_ASCII

                    if iBal+iCount > 0:
                        ExportDataToFile(_msg)
                        _msg.kill()

                        if not lGlobalErrorDetected:
                            xtra_msg=""
                            if lDidIUseAttachmentDir:

                                baseName = os.path.basename(csvfilename)
                                lShell = None
                                theCommand = None

                                if not Platform.isWindows():
                                    theCommand = 'zip -v -r "%s" "%s" "%s"' %(os.path.splitext(baseName)[0]+".zip",
                                                                              baseName,
                                                                              os.path.join(os.path.splitext(baseName)[0],""))

                                    lShell = True
                                else:
                                    try:
                                        if float(System.getProperty("os.version")) >= 10:
                                            theCommand = 'tar -a -cvf "%s" "%s" "%s"' %(os.path.splitext(baseName)[0]+".zip",
                                                                                        baseName,
                                                                                        os.path.join(os.path.splitext(baseName)[0],"*.*"))

                                            lShell = False
                                    except:
                                        pass
                                try:
                                    if theCommand:
                                        os.chdir(scriptpath)
                                        xx=subprocess.check_output( theCommand, shell=lShell)
                                        myPrint("B","Created zip using command: %s (output follows)" %theCommand)
                                        myPrint("B",xx)
                                        xtra_msg="\n(and I also zipped the file - review console / log for any messages)"
                                except:
                                    myPrint("B","Sorry, failed to create zip")
                                    xtra_msg="\n(with an error creating the zip file - review console / log for messages)"

                            MyPopUpDialogBox(extract_data_frame_,
                                             "Your extract has been created as requested:",
                                             "With %s rows and %s attachments downloaded %s\n"
                                             "\n(... and %s Attachment Errors...)" % (len(transactionTable),iCountAttachmentsDownloaded, xtra_msg,iAttachmentErrors),
                                             200,
                                             myScriptName, lModal=True).go()

                            try:
                                helper_EAR = moneydance.getPlatformHelper()
                                helper_EAR.openDirectory(File(csvfilename))
                            except:
                                pass
                    else:
                        _msg.kill()
                        myPopupInformationBox(extract_data_frame_, "No records selected and no extract file created....", myScriptName)

                    # Clean up...
                    if not lDidIUseAttachmentDir and attachmentDir:
                        try:
                            os.rmdir(attachmentDir)
                            myPrint("B", "Successfully removed unused/empty Attachment Directory: %s" %attachmentDir)

                        except:
                            myPrint("B", "Sorry - I failed to remove the unused/empty Attachment Directory: %s",attachmentDir)

                    # delete references to large objects
                    del transactionTable
                    del accountBalances

                do_extract_account_registers()

            elif lExtractInvestmentTxns:
                # ####################################################
                # EXTRACT_INVESTMENT_TRANSACTIONS_CSV EXECUTION
                # ####################################################

                def do_extract_investment_transactions():
                    global debug
                    global decimalCharSep, lDidIUseAttachmentDir, csvfilename, myScriptName, lGlobalErrorDetected, lExit, lDisplayOnly
                    global baseCurrency, sdf
                    global transactionTable, dataKeys, attachmentDir, relativePath

                    global __extract_data, extract_data_frame_, extract_filename
                    global lStripASCII, scriptpath, csvDelimiter, userdateformat, lWriteBOMToExportFile_SWSS
                    global hideInactiveAccounts, hideHiddenAccounts, hideHiddenSecurities
                    global lAllSecurity, filterForSecurity, lAllAccounts, filterForAccounts, lAllCurrency, filterForCurrency
                    global whichDefaultExtractToRun_SWSS
                    global lIncludeOpeningBalances, lAdjustForSplits, lExtractAttachments_EIT

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

                            if self.lAllSecurity:
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

                            if self.lAllCurrency:
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
                                        myPopupInformationBox(extract_data_frame_, "LOGIC ERROR: I can't see how the Security's currency is different to the Account's currency? ","LOGIC ERROR")
                                        # noinspection PyUnresolvedReferences
                                        extract_data_frame_.dispose()
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

                    # noinspection PyArgumentList
                    class MyAcctFilter(AcctFilter):

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

                            super(AcctFilter, self).__init__()

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
                                if acct.getUUID() == self.findUUID:
                                    return True
                                else:
                                    return False

                            # Investment Accounts only
                            # noinspection PyUnresolvedReferences
                            if acct.getAccountType() != Account.AccountType.INVESTMENT:
                                return False

                            if self.hideInactiveAccounts:
                                # This logic replicates Moneydance AcctFilter.ACTIVE_ACCOUNTS_FILTER
                                if acct.getAccountOrParentIsInactive(): return False
                                if acct.getHideOnHomePage() and acct.getBalance() == 0: return False

                            if self.lAllAccounts:
                                pass
                            elif (self.filterForAccounts.upper().strip() in acct.getFullAccountName().upper().strip()):
                                pass
                            else:
                                return False

                            if (not self.hideHiddenAccounts) or (self.hideHiddenAccounts and not acct.getHideOnHomePage()):
                                pass
                            else:
                                return False

                            if self.lAllSecurity:
                                pass
                            else:
                                return False

                            if self.lAllCurrency:
                                pass
                            else:
                                acctCurr = acct.getCurrencyType()                                                       # noqa
                                if (self.filterForCurrency.upper().strip() in acctCurr.getIDString().upper().strip()):
                                    pass
                                elif (self.filterForCurrency.upper().strip() in acctCurr.getName().upper().strip()):
                                    pass
                                else:
                                    return False

                            # Phew! We made it....
                            return True
                        # enddef


                    _COLUMN = 0
                    _HEADING = 1
                    dataKeys = {
                        "_ACCOUNT":             [0, "Account"],
                        "_DATE":                [1, "Date"],
                        "_TAXDATE":             [2, "TaxDate"],
                        "_CURR":                [3, "Currency"],
                        "_SECURITY":            [4, "Security"],
                        "_TICKER":              [5, "SecurityTicker"],
                        "_SECCURR":             [6, "SecurityCurrency"],
                        "_AVGCOST":             [7, "AverageCostControl"],
                        "_ACTION":              [8, "Action"],
                        "_TT":                  [9, "ActionType"],
                        "_CHEQUE":              [10, "Cheque"],
                        "_DESC":                [11, "Description"],
                        "_MEMO":                [12, "Memo"],
                        "_CLEARED":             [13, "Cleared"],
                        "_TRANSFER":            [14, "Transfer"],
                        "_CAT":                 [15, "Category"],
                        "_SHARES":              [16, "Shares"],
                        "_PRICE":               [17, "Price"],
                        "_AMOUNT":              [18, "Amount"],
                        "_FEE":                 [19, "Fee"],
                        "_FEECAT":              [20, "FeeCategory"],
                        "_TXNNETAMOUNT":        [21, "TransactionNetAmount"],
                        "_CASHIMPACT":          [22, "CashImpact"],
                        "_SHRSAFTERSPLIT":      [23, "CalculateSharesAfterSplit"],
                        "_PRICEAFTERSPLIT":     [24, "CalculatePriceAfterSplit"],
                        "_HASATTACHMENTS":      [25, "HasAttachments"],
                        "_LOTS":                [26, "Lot Data"],
                        "_ACCTCASHBAL":         [27, "AccountCashBalance"],
                        "_SECSHRHOLDING":       [28, "SecurityShareHolding"],
                        "_ATTACHMENTLINK":      [29, "AttachmentLink"],
                        "_ATTACHMENTLINKREL":   [30, "AttachmentLinkRelative"],
                        "_KEY":                 [31, "Key"],
                        "_END":                 [32, "_END"]
                    }

                    transactionTable = []

                    myPrint("DB", dataKeys)

                    rootbook = moneydance.getCurrentAccountBook()

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

                    validAccountList = AccountUtil.allMatchesForSearch(moneydance_data,MyAcctFilter(hideInactiveAccounts,
                                                                                                    lAllAccounts,
                                                                                                    filterForAccounts,
                                                                                                    hideHiddenAccounts,
                                                                                                    hideHiddenSecurities,
                                                                                                    lAllCurrency,
                                                                                                    filterForCurrency,
                                                                                                    lAllSecurity,
                                                                                                    filterForSecurity,
                                                                                                    None))

                    iCount = 0
                    iCountAttachmentsDownloaded = 0
                    uniqueFileNumber = 1

                    _local_storage = moneydance.getCurrentAccountBook().getLocalStorage()
                    iAttachmentErrors=0

                    iBal = 0
                    accountBalances = {}

                    copyValidAccountList = ArrayList()
                    if lIncludeOpeningBalances:
                        for acctBal in validAccountList:
                            if acctBal.getStartBalance() != 0:
                                # if userdateStart <= acctBal.getCreationDateInt() <= userdateEnd:
                                copyValidAccountList.add(acctBal)

                    for txn in txns:

                        txnAcct = txn.getAccount()
                        acctCurr = txnAcct.getCurrencyType()  # Currency of the Investment Account

                        if lIncludeOpeningBalances:

                            if txnAcct in copyValidAccountList:
                                copyValidAccountList.remove(txnAcct)

                            if accountBalances.get(txnAcct):
                                pass
                            else:
                                accountBalances[txnAcct] = True
                                openBal = acctCurr.getDoubleValue(txnAcct.getStartBalance())
                                if openBal != 0:
                                    iBal+=1
                                    _row = ([None] * dataKeys["_END"][0])  # Create a blank row to be populated below...
                                    _row[dataKeys["_ACCOUNT"][_COLUMN]] = txnAcct.getFullAccountName()
                                    _row[dataKeys["_CURR"][_COLUMN]] = acctCurr.getIDString()
                                    _row[dataKeys["_DESC"][_COLUMN]] = "MANUAL OPENING BALANCE"
                                    _row[dataKeys["_ACTION"][_COLUMN]] = "OpenBal"
                                    _row[dataKeys["_TT"][_COLUMN]] = "MANUAL"
                                    _row[dataKeys["_DATE"][_COLUMN]] = txnAcct.getCreationDateInt()
                                    _row[dataKeys["_AMOUNT"][_COLUMN]] = openBal
                                    _row[dataKeys["_CASHIMPACT"][_COLUMN]] = openBal
                                    _row[dataKeys["_ACCTCASHBAL"][_COLUMN]] = acctCurr.getDoubleValue(txnAcct.getBalance())

                                    myPrint("D", _row)
                                    transactionTable.append(_row)

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

                        keyIndex = 0
                        _row = ([None] * dataKeys["_END"][0])  # Create a blank row to be populated below...

                        txnKey = txn.getUUID()
                        _row[dataKeys["_KEY"][_COLUMN]] = txnKey + "-" + str(keyIndex).zfill(3)


                        if lParent and str(txn.getTransferType()).lower() == "xfrtp_bank" and str(txn.getInvestTxnType()).lower() == "bank" \
                                and not xfrTxn and feeTxn and not securityTxn:
                            # This seems to be an error! It's an XFR (fixing MD data bug)
                            xfrTxn = feeTxn
                            feeTxn = None
                            xfrAcct = feeAcct
                            feeAcct = None

                        _row[dataKeys["_ACCOUNT"][_COLUMN]] = txnAcct.getFullAccountName()
                        _row[dataKeys["_CURR"][_COLUMN]] = acctCurr.getIDString()

                        _row[dataKeys["_DATE"][_COLUMN]] = txn.getDateInt()
                        if txn.getTaxDateInt() != txn.getDateInt():
                            _row[dataKeys["_TAXDATE"][_COLUMN]] = txn.getTaxDateInt()


                        if securityTxn:
                            _row[dataKeys["_SECURITY"][_COLUMN]] = str(securityCurr.getName())
                            _row[dataKeys["_SECCURR"][_COLUMN]] = str(securityCurr.getRelativeCurrency().getIDString())
                            _row[dataKeys["_TICKER"][_COLUMN]] = str(securityCurr.getTickerSymbol())
                            _row[dataKeys["_SHARES"][_COLUMN]] = securityCurr.getDoubleValue(securityTxn.getValue())
                            _row[dataKeys["_PRICE"][_COLUMN]] = acctCurr.getDoubleValue(securityTxn.getAmount())
                            _row[dataKeys["_AVGCOST"][_COLUMN]] = securityAcct.getUsesAverageCost()
                            _row[dataKeys["_SECSHRHOLDING"][_COLUMN]] = securityCurr.formatSemiFancy(securityAcct.getBalance(),decimalCharSep)
                        else:
                            _row[dataKeys["_SECURITY"][_COLUMN]] = ""
                            _row[dataKeys["_SECCURR"][_COLUMN]] = ""
                            _row[dataKeys["_TICKER"][_COLUMN]] = ""
                            _row[dataKeys["_SHARES"][_COLUMN]] = 0
                            _row[dataKeys["_PRICE"][_COLUMN]] = 0
                            _row[dataKeys["_AVGCOST"][_COLUMN]] = ""
                            _row[dataKeys["_SECSHRHOLDING"][_COLUMN]] = 0

                        if lAdjustForSplits and securityTxn and _row[dataKeys["_SHARES"][_COLUMN]] != 0:
                            # Here we go.....
                            _row[dataKeys["_SHRSAFTERSPLIT"][_COLUMN]] = _row[dataKeys["_SHARES"][_COLUMN]]
                            stockSplits = securityCurr.getSplits()
                            if stockSplits and len(stockSplits)>0:
                                # Here we really go....1

                                myPrint("D", securityCurr, " - Found share splits...")
                                myPrint("D", securityTxn)

                                stockSplits = sorted(stockSplits, key=lambda x: x.getDateInt(), reverse=True)   # Sort date newest first...
                                for theSplit in stockSplits:
                                    if _row[dataKeys["_DATE"][_COLUMN]] >= theSplit.getDateInt():
                                        continue
                                    myPrint("D", securityCurr, " -  ShareSplits()... Applying ratio.... *", theSplit.getSplitRatio(), "Shares before:",  _row[dataKeys["_SHRSAFTERSPLIT"][_COLUMN]])
                                    # noinspection PyUnresolvedReferences
                                    _row[dataKeys["_SHRSAFTERSPLIT"][_COLUMN]] = _row[dataKeys["_SHRSAFTERSPLIT"][_COLUMN]] * theSplit.getSplitRatio()
                                    myPrint("D", securityCurr, " - Shares after:",  _row[dataKeys["_SHRSAFTERSPLIT"][_COLUMN]])
                                    # Keep going if more splits....
                                    continue


                        _row[dataKeys["_DESC"][_COLUMN]] = str(txn.getDescription())
                        _row[dataKeys["_ACTION"][_COLUMN]] = str(txn.getTransferType())
                        if lParent:
                            _row[dataKeys["_TT"][_COLUMN]] = str(txn.getInvestTxnType())
                        else:
                            _row[dataKeys["_TT"][_COLUMN]] = str(txn.getParentTxn().getInvestTxnType())

                        _row[dataKeys["_CLEARED"][_COLUMN]] = str(txn.getStatusChar())

                        if lParent:
                            if xfrTxn:
                                _row[dataKeys["_TRANSFER"][_COLUMN]] = xfrAcct.getFullAccountName()
                        else:
                            _row[dataKeys["_TRANSFER"][_COLUMN]] = txn.getParentTxn().getAccount().getFullAccountName()

                        if lParent:
                            if securityTxn:
                                _row[dataKeys["_AMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(securityTxn.getAmount())
                            else:
                                _row[dataKeys["_AMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(txn.getValue()) * -1
                        else:
                            _row[dataKeys["_AMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(txn.getValue())

                        if xfrTxn:  # Override the value set above. Why? It's the amount TXF'd out of the account....
                            _row[dataKeys["_AMOUNT"][_COLUMN]] = (acctCurr.getDoubleValue(xfrTxn.getAmount())) * -1
                        elif incTxn:
                            _row[dataKeys["_AMOUNT"][_COLUMN]] = (acctCurr.getDoubleValue(incTxn.getAmount())) * -1
                        elif expTxn:
                            _row[dataKeys["_AMOUNT"][_COLUMN]] = (acctCurr.getDoubleValue(expTxn.getAmount())) * -1

                        _row[dataKeys["_CHEQUE"][_COLUMN]] = str(txn.getCheckNumber())
                        if lParent:
                            _row[dataKeys["_MEMO"][_COLUMN]] = str(txn.getMemo())
                        else:
                            _row[dataKeys["_MEMO"][_COLUMN]] = str(txn.getParentTxn().getMemo())

                        if expTxn:
                            _row[dataKeys["_CAT"][_COLUMN]] = expAcct.getFullAccountName()

                        if incTxn:
                            _row[dataKeys["_CAT"][_COLUMN]] = incAcct.getFullAccountName()

                        if feeTxn:
                            _row[dataKeys["_FEECAT"][_COLUMN]] = feeAcct.getFullAccountName()

                        if incTxn:
                            if feeTxn:
                                _row[dataKeys["_FEE"][_COLUMN]] = acctCurr.getDoubleValue(feeTxn.getAmount())
                                _row[dataKeys["_TXNNETAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(incTxn.getAmount()*-1 + feeTxn.getAmount()*-1)

                                # # Match Moneydance bug - until MD is fixed
                                # if lParent and str(txn.getTransferType()) == "xfrtp_miscincexp" and str(txn.getInvestTxnType()) == "MISCINC" \
                                #         and not xfrTxn and feeTxn:
                                #     row[dataKeys["_FEE"][_COLUMN]] = acctCurr.getDoubleValue(feeTxn.getAmount())
                                #     row[dataKeys["_TXNNETAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(txn.getValue() + feeTxn.getAmount()*-1)

                            else:
                                _row[dataKeys["_TXNNETAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(incTxn.getAmount()*-1)

                        elif expTxn:
                            if feeTxn:
                                _row[dataKeys["_FEE"][_COLUMN]] = acctCurr.getDoubleValue(feeTxn.getAmount())
                                _row[dataKeys["_TXNNETAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(expTxn.getAmount()*-1 + feeTxn.getAmount())

                                # Match Moneydance bug - until MD is fixed
                                if lParent and str(txn.getTransferType()) == "xfrtp_miscincexp" and str(txn.getInvestTxnType()) == "MISCEXP" \
                                        and not xfrTxn and feeTxn:
                                    _row[dataKeys["_FEE"][_COLUMN]] = acctCurr.getDoubleValue(feeTxn.getAmount())
                                    _row[dataKeys["_TXNNETAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(txn.getValue())

                            else:
                                _row[dataKeys["_TXNNETAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(expTxn.getAmount()*-1)
                        elif securityTxn:
                            if feeTxn:
                                _row[dataKeys["_FEE"][_COLUMN]] = acctCurr.getDoubleValue(feeTxn.getAmount())
                                _row[dataKeys["_TXNNETAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(securityTxn.getAmount() + feeTxn.getAmount())
                            else:
                                _row[dataKeys["_TXNNETAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(securityTxn.getAmount())
                        else:
                            if feeTxn:
                                _row[dataKeys["_FEE"][_COLUMN]] = acctCurr.getDoubleValue(feeTxn.getAmount())
                                _row[dataKeys["_TXNNETAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(txn.getValue() + feeTxn.getAmount())
                            else:
                                _row[dataKeys["_TXNNETAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(txn.getValue())

                        if _row[dataKeys["_SHARES"][_COLUMN]] != 0:
                            # roundPrice = securityCurr.getDecimalPlaces()
                            # noinspection PyUnresolvedReferences
                            price = ((_row[dataKeys["_AMOUNT"][_COLUMN]] / (_row[dataKeys["_SHARES"][_COLUMN]])))
                            _row[dataKeys["_PRICE"][_COLUMN]] = price
                            # price = None

                            if lAdjustForSplits:
                                # noinspection PyUnresolvedReferences
                                price = ((_row[dataKeys["_AMOUNT"][_COLUMN]] / (_row[dataKeys["_SHRSAFTERSPLIT"][_COLUMN]])))
                                _row[dataKeys["_PRICEAFTERSPLIT"][_COLUMN]] = price
                                # price = None

                        if lParent and (str(txn.getInvestTxnType()) == "SELL_XFER" or str(txn.getInvestTxnType()) == "BUY_XFER"
                                        or str(txn.getInvestTxnType()) == "DIVIDEND_REINVEST" or str(txn.getInvestTxnType()) == "DIVIDENDXFR"):
                            _row[dataKeys["_CASHIMPACT"][_COLUMN]] = 0.0
                        elif incTxn or expTxn:
                            _row[dataKeys["_CASHIMPACT"][_COLUMN]] = _row[dataKeys["_TXNNETAMOUNT"][_COLUMN]]
                        elif securityTxn:
                            _row[dataKeys["_CASHIMPACT"][_COLUMN]] = _row[dataKeys["_TXNNETAMOUNT"][_COLUMN]]*-1
                        else:
                            _row[dataKeys["_CASHIMPACT"][_COLUMN]] = _row[dataKeys["_TXNNETAMOUNT"][_COLUMN]]

                        _row[dataKeys["_HASATTACHMENTS"][_COLUMN]] = txn.hasAttachments()

                        _row[dataKeys["_ACCTCASHBAL"][_COLUMN]] = acctCurr.getDoubleValue(txnAcct.getBalance())

                        # row[dataKeys["_CURRDPC"][_COLUMN]] = acctCurr.getDecimalPlaces()
                        # row[dataKeys["_SECDPC"][_COLUMN]] = securityCurr.getDecimalPlaces()

                        if securityTxn:
                            _row[dataKeys["_AVGCOST"][_COLUMN]] = securityAcct.getUsesAverageCost()

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
                                _row[dataKeys["_LOTS"][_COLUMN]] = lots
                            # endif
                        # endif

                        # ATTACHMENT ROUTINE
                        holdTheKeys = ArrayList()
                        holdTheLocations = ArrayList()

                        if lExtractAttachments_EIT and txn.hasAttachments():

                            masterRowCopy = deepcopy(_row)

                            # noinspection PyUnresolvedReferences
                            holdTheKeys = holdTheKeys + txn.getAttachmentKeys()
                            for _attachKey in txn.getAttachmentKeys():
                                # noinspection PyUnresolvedReferences
                                holdTheLocations.append(txn.getAttachmentTag(_attachKey))

                            # ok, we should still be on the first record here.... and we want to download attachments....
                            attachmentFileList=[]
                            attachmentKeys = holdTheKeys                                                                # noqa
                            attachmentLocations = holdTheLocations
                            uniqueFileString=" "*5
                            for attachmentLocation in attachmentLocations:
                                uniqueFileString = str(uniqueFileNumber).strip().zfill(5)
                                outputFile = os.path.join(attachmentDir,str(uniqueFileString)+"-"+os.path.basename(attachmentLocation) )
                                try:
                                    _ostr = FileOutputStream( File(outputFile) )
                                    bytesCopied = _local_storage.readFile(attachmentLocation, _ostr)
                                    _ostr.close()
                                    myPrint("DB","Attachment %s bytes >> %s copied to %s" %(bytesCopied, attachmentLocation,outputFile))
                                    attachmentFileList.append(outputFile)
                                    iCountAttachmentsDownloaded += 1
                                    lDidIUseAttachmentDir = True
                                except:
                                    iAttachmentErrors+=1
                                    myPrint("B","ERROR - Could not extract %s" %(attachmentLocation))

                                uniqueFileNumber += 1

                            if len(attachmentFileList) < 1:
                                myPrint("B", "@@Major Error whilst searching attachments! Will just move on to next record and skip attachment")
                                masterRowCopy[dataKeys["_ATTACHMENTLINK"][_COLUMN]] = "*ERROR*"
                                myPrint("B", masterRowCopy)
                                transactionTable.append(masterRowCopy)
                                keyIndex += 1
                                iCount += 1
                                continue

                            for _i in range(0,len(attachmentFileList)):
                                rowCopy = deepcopy(masterRowCopy)  # Otherwise passes by references and future changes affect the original(s)

                                if _i > 0:  # If not on first record, update the key...
                                    rowCopy[dataKeys["_KEY"][_COLUMN]] = txnKey + "-" + str(keyIndex).zfill(3)

                                if _i == 1:
                                    # Nuke repeated rows for Attachments (so totals are still OK)
                                    rowCopy[dataKeys["_SHARES"][_COLUMN]] = None
                                    rowCopy[dataKeys["_PRICE"][_COLUMN]] = None
                                    rowCopy[dataKeys["_AMOUNT"][_COLUMN]] = None
                                    rowCopy[dataKeys["_FEE"][_COLUMN]] = None
                                    rowCopy[dataKeys["_FEECAT"][_COLUMN]] = None
                                    rowCopy[dataKeys["_TXNNETAMOUNT"][_COLUMN]] = None
                                    rowCopy[dataKeys["_CASHIMPACT"][_COLUMN]] = None
                                    rowCopy[dataKeys["_SHRSAFTERSPLIT"][_COLUMN]] = None
                                    rowCopy[dataKeys["_PRICEAFTERSPLIT"][_COLUMN]] = None
                                    rowCopy[dataKeys["_LOTS"][_COLUMN]] = None
                                    rowCopy[dataKeys["_ACCTCASHBAL"][_COLUMN]] = None
                                    rowCopy[dataKeys["_SECSHRHOLDING"][_COLUMN]] = None

                                rowCopy[dataKeys["_ATTACHMENTLINK"][_COLUMN]] = '=HYPERLINK("'+attachmentFileList[_i]+'","FILE: '+os.path.basename(attachmentFileList[_i])[len(uniqueFileString)+1:]+'")'
                                rowCopy[dataKeys["_ATTACHMENTLINKREL"][_COLUMN]] = '=HYPERLINK("'+os.path.join(".",relativePath,os.path.basename(attachmentFileList[_i]))+'","FILE: '+os.path.basename(attachmentFileList[_i])[len(uniqueFileString)+1:]+'")'

                                transactionTable.append(rowCopy)

                                keyIndex += 1
                                iCount += 1

                        # END ATTACHMENT ROUTINE
                        else:
                            myPrint("D", _row)
                            transactionTable.append(_row)
                            iCount += 1

                    if lIncludeOpeningBalances and len(copyValidAccountList)>0:
                        myPrint("DB","Now iterating remaining %s Accounts with no txns for balances...." %(len(copyValidAccountList)))

                        # Yes I should just move this section from above so the code is not inefficient....
                        for acctBal in copyValidAccountList:
                            acctCurr = acctBal.getCurrencyType()  # Currency of the Investment Account
                            openBal = acctCurr.getDoubleValue(acctBal.getStartBalance())
                            if openBal != 0:
                                iBal+=1
                                _row = ([None] * dataKeys["_END"][0])  # Create a blank row to be populated below...
                                _row[dataKeys["_ACCOUNT"][_COLUMN]] = acctBal.getFullAccountName()
                                _row[dataKeys["_CURR"][_COLUMN]] = acctCurr.getIDString()
                                _row[dataKeys["_DESC"][_COLUMN]] = "MANUAL OPENING BALANCE"
                                _row[dataKeys["_ACTION"][_COLUMN]] = "OpenBal"
                                _row[dataKeys["_TT"][_COLUMN]] = "MANUAL"
                                _row[dataKeys["_DATE"][_COLUMN]] = acctBal.getCreationDateInt()
                                _row[dataKeys["_AMOUNT"][_COLUMN]] = openBal
                                _row[dataKeys["_CASHIMPACT"][_COLUMN]] = openBal
                                _row[dataKeys["_ACCTCASHBAL"][_COLUMN]] = acctCurr.getDoubleValue(acctBal.getBalance())

                                myPrint("D", _row)
                                transactionTable.append(_row)

                    myPrint("P","")
                    myPrint("B", "Investment Transaction Records selected:", len(transactionTable) )

                    if iCountAttachmentsDownloaded:
                        myPrint("B", ".. and I downloaded %s attachments for you too" %iCountAttachmentsDownloaded )

                    if iBal: myPrint("B", "...and %s Manual Opening Balance entries created too..." %iBal)

                    if iAttachmentErrors: myPrint("B", "@@ ...and %s Attachment Errors..." %iAttachmentErrors)
                    ###########################################################################################################


                    # sort the file: Account>Security>Date
                    if lExtractAttachments_EIT:
                        transactionTable = sorted(transactionTable, key=lambda x: (x[dataKeys["_ACCOUNT"][_COLUMN]],
                                                                                   x[dataKeys["_DATE"][_COLUMN]],
                                                                                   x[dataKeys["_KEY"][_COLUMN]]) )
                    else:
                        transactionTable = sorted(transactionTable, key=lambda x: (x[dataKeys["_ACCOUNT"][_COLUMN]],
                                                                                   x[dataKeys["_DATE"][_COLUMN]]))

                    ###########################################################################################################


                    def ExportDataToFile():
                        global debug, csvfilename, decimalCharSep, groupingCharSep, csvDelimiter, version_build, myScriptName
                        global transactionTable, userdateformat, lGlobalErrorDetected
                        global lWriteBOMToExportFile_SWSS, lExtractAttachments_EIT, relativePath

                        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

                        headings = []
                        sortDataFields = sorted(dataKeys.items(), key=lambda x: x[1][_COLUMN])
                        for i in sortDataFields:
                            headings.append(i[1][_HEADING])
                        print

                        myPrint("P", "Now pre-processing the file to convert integer dates and strip non-ASCII if requested....")
                        for _theRow in transactionTable:
                            dateasdate = datetime.datetime.strptime(str(_theRow[dataKeys["_DATE"][_COLUMN]]), "%Y%m%d")  # Convert to Date field
                            _dateoutput = dateasdate.strftime(userdateformat)
                            _theRow[dataKeys["_DATE"][_COLUMN]] = _dateoutput

                            if _theRow[dataKeys["_TAXDATE"][_COLUMN]]:
                                dateasdate = datetime.datetime.strptime(str(_theRow[dataKeys["_TAXDATE"][_COLUMN]]), "%Y%m%d")  # Convert to Date field
                                _dateoutput = dateasdate.strftime(userdateformat)
                                _theRow[dataKeys["_TAXDATE"][_COLUMN]] = _dateoutput

                            for col in range(0, dataKeys["_SECSHRHOLDING"][_COLUMN]):
                                _theRow[col] = fixFormatsStr(_theRow[col])

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

                                if lExtractAttachments_EIT and Platform.isOSX():
                                    writer.writerow([""])
                                    writer.writerow(["** On a Mac with Later versions of Excel, Apple 'Sand Boxing' prevents file access..."])
                                    writer.writerow(["** Edit this cell below, then press Enter and it will change to a Hyperlink (blue)"])
                                    writer.writerow(["** Click it, then Open, and then GRANT access to the folder.... (the links below will then work)"])
                                    writer.writerow([""])
                                    # writer.writerow(["FILE://" + os.path.join(".",relativePath)])
                                    writer.writerow(["FILE://" + scriptpath])
                                    # writer.writerow(["FILE:///"])  # This attempts to allow access to whole folder subsystem....
                                    writer.writerow([""])

                                if lExtractAttachments_EIT:
                                    if debug:
                                        writer.writerow(headings[:dataKeys["_END"][_COLUMN]])  # Print the header, but not the extra _field headings
                                    else:
                                        writer.writerow(headings[:dataKeys["_KEY"][_COLUMN]])  # Print the header, but not the extra _field headings
                                else:
                                    writer.writerow(headings[:dataKeys["_ATTACHMENTLINKREL"][_COLUMN]])  # Print the header, but not the extra _field headings

                                try:
                                    for i in range(0, len(transactionTable)):
                                        if lExtractAttachments_EIT:
                                            if debug:
                                                writer.writerow(transactionTable[i][:dataKeys["_END"][_COLUMN]])
                                            else:
                                                writer.writerow(transactionTable[i][:dataKeys["_KEY"][_COLUMN]])
                                        else:
                                            writer.writerow(transactionTable[i][:dataKeys["_ATTACHMENTLINKREL"][_COLUMN]])
                                except:
                                    dump_sys_error_to_md_console_and_errorlog()
                                    myPrint("B", "ERROR writing to CSV on row %s. Please review console" %i)
                                    myPrint("B", transactionTable[i])
                                    myPopupInformationBox(extract_data_frame_,"ERROR writing to CSV on row %s. Please review console" %i)
                                    ConsoleWindow.showConsoleWindow(moneydance_ui)
                                    raise Exception("Aborting")

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

                                writer.writerow(["Hiding Hidden Securities...: %s" %(hideHiddenSecurities)])
                                writer.writerow(["Hiding Inactive Accounts...: %s" %(hideInactiveAccounts)])
                                writer.writerow(["Hiding Hidden Accounts.....: %s" %(hideHiddenAccounts)])
                                writer.writerow(["Security filter............: %s '%s'" %(lAllSecurity,filterForSecurity)])
                                writer.writerow(["Account filter.............: %s '%s'" %(lAllAccounts,filterForAccounts)])
                                writer.writerow(["Currency filter............: %s '%s'" %(lAllCurrency,filterForCurrency)])
                                writer.writerow(["Include Opening Balances...: %s" %(lIncludeOpeningBalances)])
                                writer.writerow(["Adjust for Splits..........: %s" %(lAdjustForSplits)])
                                writer.writerow(["Split Securities by Account: %s" %(userdateformat)])
                                writer.writerow(["Download Attachments.......: %s" %(lExtractAttachments_EIT)])

                            myPrint("B", "CSV file " + csvfilename + " created, records written, and file closed..")

                        except IOError, e:
                            lGlobalErrorDetected = True
                            myPrint("B", "Oh no - File IO Error!", e)
                            myPrint("B", "Path:", csvfilename)
                            myPrint("B", "!!! ERROR - No file written - sorry! (was file open, permissions etc?)".upper())
                            dump_sys_error_to_md_console_and_errorlog()
                            myPopupInformationBox(extract_data_frame_,"Sorry - error writing to export file!", "FILE EXTRACT")

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
                        # theString = theString.replace(";", "*")  # remove tabs within fields to keep csv format happy
                        # theString = theString.replace(",", "*")  # remove tabs within fields to keep csv format happy
                        # theString = theString.replace("|", "*")  # remove tabs within fields to keep csv format happy

                        if lStripASCII:
                            all_ASCII = ''.join(char for char in theString if ord(char) < 128)  # Eliminate non ASCII printable Chars too....
                        else:
                            all_ASCII = theString
                        return all_ASCII

                    if len(transactionTable) > 0:

                        ExportDataToFile()

                        if not lGlobalErrorDetected:
                            xtra_msg=""
                            if lDidIUseAttachmentDir:

                                baseName = os.path.basename(csvfilename)
                                lShell = None
                                theCommand = None

                                if not Platform.isWindows():
                                    theCommand = 'zip -v -r "%s" "%s" "%s"' %(os.path.splitext(baseName)[0]+".zip",
                                                                              baseName,
                                                                              os.path.join(os.path.splitext(baseName)[0],""))

                                    lShell = True
                                else:
                                    try:
                                        if float(System.getProperty("os.version")) >= 10:
                                            theCommand = 'tar -a -cvf "%s" "%s" "%s"' %(os.path.splitext(baseName)[0]+".zip",
                                                                                        baseName,
                                                                                        os.path.join(os.path.splitext(baseName)[0],"*.*"))

                                            lShell = False
                                    except:
                                        pass
                                try:
                                    if theCommand:
                                        os.chdir(scriptpath)
                                        xx=subprocess.check_output( theCommand, shell=lShell)
                                        myPrint("B","Created zip using command: %s (output follows)" %theCommand)
                                        myPrint("B",xx)
                                        xtra_msg="\n(and I also zipped the file - review console / log for any messages)"
                                except:
                                    myPrint("B","Sorry, failed to create zip")
                                    xtra_msg="\n(with an error creating the zip file - review console / log for messages)"

                            MyPopUpDialogBox(extract_data_frame_,
                                             "Your extract has been created as requested:",
                                             "With %s rows and %s attachments downloaded %s\n"
                                             "\n(... and %s Attachment Errors...)" % (len(transactionTable),iCountAttachmentsDownloaded, xtra_msg,iAttachmentErrors),
                                             200,
                                             myScriptName, lModal=True).go()

                            try:
                                helper_EIT = moneydance.getPlatformHelper()
                                helper_EIT.openDirectory(File(csvfilename))
                            except:
                                pass
                    else:
                        myPopupInformationBox(extract_data_frame_, "No records selected and no extract file created....", myScriptName)

                    # Clean up...
                    if not lDidIUseAttachmentDir and attachmentDir:
                        try:
                            os.rmdir(attachmentDir)
                            myPrint("B", "Successfully removed unused/empty Attachment Directory: %s" %(attachmentDir))
                        except:
                            myPrint("B", "Sorry - I failed to remove the unused/empty Attachment Directory: %s",(attachmentDir))

                    # delete references to large objects
                    del transactionTable
                    del accountBalances

                do_extract_investment_transactions()

            elif lExtractCurrencyHistory:

                # ####################################################
                # EXTRACT_CURRENCY_HISTORY_CSV PARAMETER SCREEN
                # ####################################################

                def do_extract_currency_history():
                    global debug
                    global decimalCharSep, lDidIUseAttachmentDir, csvfilename, myScriptName, lGlobalErrorDetected, lExit, lDisplayOnly
                    global sdf, csvlines

                    global __extract_data, extract_data_frame_, extract_filename
                    global lStripASCII, scriptpath, csvDelimiter, userdateformat, lWriteBOMToExportFile_SWSS
                    global hideInactiveAccounts, hideHiddenAccounts, hideHiddenSecurities
                    global lAllSecurity, filterForSecurity, lAllAccounts, filterForAccounts, lAllCurrency, filterForCurrency
                    global whichDefaultExtractToRun_SWSS
                    global lSimplify_ECH, userdateStart_ECH, userdateEnd_ECH, hideHiddenCurrencies_ECH


                    myPrint("P", "\nScript running to extract your currency rate history....")
                    myPrint("P", "-------------------------------------------------------------------")

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

                                row = []                                                                                    # noqa

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

                                row = []                                                                                    # noqa

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
                        for row in theTable:                                                                                # noqa
                            try:
                                if row[_SNAPDATE]:
                                    dateasdate = datetime.datetime.strptime(str(row[_SNAPDATE]),"%Y%m%d")  # Convert to Date field
                                    _dateoutput = dateasdate.strftime(userdateformat)
                                    row[_SNAPDATE] = _dateoutput

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
                                    try:
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
                                    except:
                                        dump_sys_error_to_md_console_and_errorlog()
                                        myPrint("B", "ERROR writing to CSV on row %s. Please review console" %i)
                                        myPrint("B", theTable[i])
                                        myPopupInformationBox(extract_data_frame_,"ERROR writing to CSV on row %s. Please review console" %i)
                                        ConsoleWindow.showConsoleWindow(moneydance_ui)
                                        raise Exception("Aborting")

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
                                    try:
                                        iRowCounter=0
                                        for row in theTable[1:]:                                                                # noqa
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
                                            iRowCounter+=1
                                    except:
                                        dump_sys_error_to_md_console_and_errorlog()
                                        myPrint("B", "ERROR writing to CSV on row %s. Please review console" %iRowCounter)
                                        myPrint("B", row)
                                        myPopupInformationBox(extract_data_frame_,"ERROR writing to CSV on row %s. Please review console" %iRowCounter)
                                        ConsoleWindow.showConsoleWindow(moneydance_ui)
                                        raise Exception("Aborting")
                            myPrint("B", "CSV file " + csvfilename + " created, records written, and file closed..")

                        except IOError, e:
                            lGlobalErrorDetected = True
                            myPrint("B", "Oh no - File IO Error!", e)
                            myPrint("B", "Path:", csvfilename)
                            myPrint("B", "!!! ERROR - No file written - sorry! (was file open, permissions etc?)".upper())
                            dump_sys_error_to_md_console_and_errorlog()
                            myPopupInformationBox(extract_data_frame_,"Sorry - error writing to export file!", "FILE EXTRACT")
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
                        myPopupInformationBox(extract_data_frame_,"Your extract (%s records) has been created as requested." %(len(currencyTable)+1),myScriptName)
                        try:
                            helper_c = moneydance.getPlatformHelper()
                            helper_c.openDirectory(File(csvfilename))
                        except:
                            pass

                do_extract_currency_history()


    myPrint("B", "StuWareSoftSystems - ", myScriptName, " script ending......")

    if not extract_data_frame_.isActiveInMoneydance:
        destroyOldFrames(myModuleID)

    if lExit or (not lExtractReminders and not lExtractStockGlance2020):

        moneydance_ui.firstMainFrame.setStatus(">> StuWareSoftSystems - thanks for using >> %s......." %(myScriptName),0)
        if not i_am_an_extension_so_run_headless: print(scriptExit)

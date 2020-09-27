#!/usr/bin/env python

# StockGlance2020 v3b - September 2020 - Stuart Beesley
#  Original code StockGlance.java Moneydance Extension written by James Larus - Copyright below.
#  https://github.com/jameslarus/stockglance

#  Modified by waynelloydsmith to run as standalone Python script StockGlance75.py and to show which accounts the stocks are held.
#  https://github.com/waynelloydsmith/Moneydance-Scripts/blob/master/StockGlance75.py

#  Further extensively modified by Stuart Beesley - StuWareSoftSystems - September 2020 to create StockGlance2020.py with these features:
#  ---- This script basically shows all stocks/funds summarised into single stocks/funds per row. I.E. consolidates data accross all Accounts
#  ---- Some of the code looks somewhat different to how I would write native Python, but it is as it is as it was converted from pure Java by waynelloydsmith
#  ---- Shows QTY of shares
#  ---- Removed all non-functional Java / Python code and general tidy up
#  ---- Addressed bug hiding some securitys when not all prices found (by date) - by eliminating % as not needed anyway.
#  ---- Price is taken from Current Price now, and NOT from price history. If you would like price history, let me know!
#  ---- Added Parameter/filter screen/options and export to file....
#  ---- The file will write a utf8 encoded file - so we strip out currency signs - else Excel treats them wrongly. You can specify to leave them included...
#  ---- NOTE: price output display rounds to 2 decimal places, but the totals are correctly calculated 
# ----- USAGE: Just execute and a popup will ask you to set parameters. You can just leave all as default if you wish. Change the defaults in the rows just below this statement...
# ----- WARNING: Cash Balances are per account, not per security/currency. So the cash balaces will always be for the whole account(s) included, not just  filtered securities etc...
# ----- I've added extra columns with raw number that don't get displayed. I planned to use for custom sort, but I found a workaround stripping non numerics out of text... (so not used) 
# ----- Found that JFileChooser with file extension filters hangs on Macs, so use FileDialog on Mac to also get Mac(ish) GUI LaF
# ----- Version 3 - fixed bug so that .moneydance extension test only checks end of filename (not middle)

# ------------------------
#  StockGlance.java
# 
#  Copyright (c) 2015-16, James Larus
#   All rights reserved.
# 
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions are
#   met:
# 
#   1. Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# 
#   2. Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# 
#   3. Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
# 
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
# ------------------------

import sys
reload(sys)                         # Dirty hack to eliminate UTF-8 coding errors
sys.setdefaultencoding('utf8')      # Dirty hack to eliminate UTF-8 coding errors
import platform

import datetime

from com.infinitekind.moneydance.model import *
from com.infinitekind.moneydance.model.Account import AccountType
from com.infinitekind.moneydance.model import AccountUtil, AcctFilter, CurrencyType
from com.infinitekind.moneydance.model.CurrencyUtil import convertToBasePrice, getRawRate, convertValue
from com.infinitekind.moneydance.model.txtimport.TabularTextImportSpec import getDecimalPoint

from com.infinitekind.util import DateUtil, StringUtils
from com.moneydance.util.StringUtils import formatRate, formatShortRate
from com.moneydance.apps.md.view.gui import MoneydanceLAF


from java.awt import *
from java.awt import BorderLayout, Color, Dimension, GridLayout, Toolkit, Component, FileDialog

from java.awt.event import MouseAdapter, WindowAdapter, AdjustmentListener

from java.text import *
from java.text import NumberFormat, SimpleDateFormat

from java.util import *
from java.util import Arrays, Calendar, Comparator, Date, HashMap, Vector
from java.util.List import *

from javax.swing import JScrollPane, WindowConstants, BorderFactory, BoxLayout, JFrame, JLabel, JPanel, JTable, JComponent, KeyStroke, AbstractAction, JSeparator, SwingConstants
from javax.swing import JButton, JTextArea, JOptionPane, JRadioButton, ButtonGroup, JButton, JFileChooser, JTextField
from javax.swing import Icon, RowSorter,UIManager, SortOrder, SwingUtilities

from javax.swing.RowSorter import SortKey 
from javax.swing.border import CompoundBorder, EmptyBorder, MatteBorder
from javax.swing.table import AbstractTableModel, DefaultTableCellRenderer, DefaultTableModel, TableModel, TableRowSorter
from javax.swing.text import PlainDocument
from javax.swing.event import TableColumnModelListener
import javax.swing.filechooser.FileNameExtensionFilter

import java.lang
from java.lang import System, Double, Math

import time

import os
import os.path
import java.io.File

import inspect

global debug # Set to True if you want verbose messages, else set to False....

global StockGlanceInstance  # holds the instance of StockGlance2020()
global baseCurrency, sdf, frame_, rawDataTable, rawFooterTable, headingNames
global hideHiddenSecurities, hideInactiveAccounts, hideHiddenAccounts, lAllCurrency, filterForCurrency, lAllSecurity, filteForSecurity, lStripASCII
global csvfilename

# Set programatic defaults/parameters for filters HERE.... You  can override in the pop-up screen
hideHiddenSecurities=True
hideInactiveAccounts=True
hideHiddenAccounts=True
lAllCurrency=True
filterForCurrency="ALL"
lAllSecurity=True
filterForSecurity="ALL"
lAllAccounts=True
filterForAccounts="ALL"
lIncludeCashBalances=False
lStripASCII=True
debug = False
lUseMacFileChooser=True # This will be ignored if you don't choose option to export to  a file

headingNames=""
lIamAMac=False

def MDDiag():
    global debug
    if debug: print "Moneydance Build:",moneydance.getVersion(), "Build:", moneydance.getBuild()

MDDiag()

def checkVersions():
    global debug
    
    lError=False
    plat_j=platform.system()
    plat_p=platform.python_implementation()
    python_maj=sys.version_info.major
    python_min=sys.version_info.minor

    if debug: print "Platform:",plat_p,plat_j,python_maj,".",python_min
    if debug: print sys.version
        
    if plat_p <> "Jython":
        lError=True
        print "Error: Script requires Jython"
    if plat_j <> "Java":
        lError=True
        print "Error: Script requires Java  base"
    if (python_maj <> 2 or  python_min <> 7):
        lError=True
        print "\n\nError: Script was  designed on version 2.7. By all means bypass this test and see what happens....."
    
    if  lError:
        print "\n@@@ TERMINATING PROGRAM @@@\n"
        #raise
        
    return (not lError)
#enddef
    
if checkVersions():

    def amIaMac():
        myPlat = System.getProperty("os.name")
        if myPlat == None: Return(False)
        if debug: print "Platform:", myPlat
        return(myPlat == "Mac OS X")
    #enddef
    
    lIamAMac=amIaMac()
    if not lIamAMac: lUseMacFileChooser=False
        
    csvfilename=None

    # Stores  the data table for export
    rawDataTable=None
    rawrawFooterTable=None

    sdf = SimpleDateFormat("dd/MM/yyyy")  

    print "StuWareSoftSystems..."
    print "StockGlance2020.py......."
    if debug: print "DEBUG IS ON.."

    # This allows me to filter inputs to Y/N and convert to uppercase - single digit responses..... (took hours to work out, but now I have it!)
    class JTextFieldLimitYN(PlainDocument):
        limit=10 # Default
        toUpper=False
        what=""
        def __init__(self,limit,toUpper,what):
            super(PlainDocument, self).__init__()
            self.limit = limit
            self.toUpper=toUpper
            self.what=what

        def insertString(self, myOffset, myString, myAttr):
            if (myString == None): return
            if self.toUpper: myString=myString.upper()
            if (self.what=="YN" and (myString == "Y" or myString == "N")) or (self.what=="CURR"):
                if ((self.getLength() + len(myString)) <= self.limit):
                    super(JTextFieldLimitYN,self).insertString(myOffset, myString, myAttr)
    #endclass         

    label1 = JLabel("Hide Hidden Securities (Y/N)?:")
    user_hideHiddenSecurities=JTextField(2)
    user_hideHiddenSecurities.setDocument(JTextFieldLimitYN(1,True,"YN"))
    if     hideHiddenSecurities: user_hideHiddenSecurities.setText("Y")
    else:                        user_hideHiddenSecurities.setText("N")

    label2 = JLabel("Hide Inactive Accounts (Y/N)?:")
    user_hideInactiveAccounts=JTextField(2)
    user_hideInactiveAccounts.setDocument(JTextFieldLimitYN(1,True,"YN"))
    if     hideInactiveAccounts: user_hideInactiveAccounts.setText("Y")
    else:                        user_hideInactiveAccounts.setText("N")

    label3 = JLabel("Hide Hidden Accounts (Y/N):")
    user_hideHiddenAccounts=JTextField(2)
    user_hideHiddenAccounts.setDocument(JTextFieldLimitYN(1,True,"YN"))
    if     hideHiddenAccounts: user_hideHiddenAccounts.setText("Y")
    else:                      user_hideHiddenAccounts.setText("N")

    label4 = JLabel("Filter one Currency or ALL:")
    user_selectCurrency=JTextField(5)
    user_selectCurrency.setDocument(JTextFieldLimitYN(5,True,"CURR"))
    if lAllCurrency: user_selectCurrency.setText("ALL")
    else:            user_selectCurrency.setText(filterForCurrency)

    label5 = JLabel("Filter one Security/Ticker or ALL:")
    user_selectTicker=JTextField(12)
    user_selectTicker.setDocument(JTextFieldLimitYN(12,True,"CURR"))
    if lAllSecurity: user_selectTicker.setText("ALL")
    else:            user_selectTicker.setText(filterForSecurity)

    label6 = JLabel("Filter for Accounts Containing text '...' (or ALL):")
    user_selectAccounts=JTextField(12)
    user_selectAccounts.setDocument(JTextFieldLimitYN(20,True,"CURR"))
    if lAllAccounts: user_selectAccounts.setText("ALL")
    else:            user_selectAccounts.setText(filterForAccounts)

    label7 = JLabel("Include Cash Balances for each account? (Y/N):")
    user_selectCashBalances=JTextField(2)
    user_selectCashBalances.setDocument(JTextFieldLimitYN(1,True,"YN"))
    if     lIncludeCashBalances: user_selectCashBalances.setText("Y")
    else:               user_selectCashBalances.setText("N")

    label8 = JLabel("Strip currency symbols from CSV export? (Y/N)")
    user_selectStripASCII=JTextField(12)
    user_selectStripASCII.setDocument(JTextFieldLimitYN(1,True,"YN"))
    if     lStripASCII: user_selectStripASCII.setText("Y")
    else:               user_selectStripASCII.setText("N")

    
    label9 = JLabel("Turn DEBUG Verbose messages on? (Y/N)")
    user_selectDEBUG=JTextField(2)
    user_selectDEBUG.setDocument(JTextFieldLimitYN(1,True,"YN"))
    if      debug:  user_selectDEBUG.setText("Y")
    else:           user_selectDEBUG.setText("N")


    if lIamAMac:    
        label10 = JLabel("Use Mac-like GUI for export filename selection? (Y/N)")
        user_selectMacFileChooser=JTextField(2)
        user_selectMacFileChooser.setDocument(JTextFieldLimitYN(1,True,"YN"))
        if      lUseMacFileChooser:  user_selectMacFileChooser.setText("Y")
        else:                        user_selectMacFileChooser.setText("N")
        
    userFilters =JPanel(GridLayout(10, 2))
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
    userFilters.add(label8)
    userFilters.add(user_selectStripASCII)
    userFilters.add(label9)
    userFilters.add(user_selectDEBUG)
    if lIamAMac:
        userFilters.add(label10)
        userFilters.add(user_selectMacFileChooser)

    lExit=False
    lDisplayOnly=False
    
    options = ["Abort", "Display & CSV Export", "Display Only"]
    userAction=(JOptionPane.showOptionDialog(None, userFilters,"Set Script Parameters....",JOptionPane.OK_CANCEL_OPTION,JOptionPane.QUESTION_MESSAGE,None,options,options[2])) 
    if   userAction == 1: # Display & Export
        if debug: print "Display and export choosen"
        lDisplayOnly=False
    elif userAction == 2: # Display Only
        lDisplayOnly=True
        if debug: print "Display only with no export choosen"
    else:
        # Abort
        print "User Cancelled Parameter selection.. Will abort.."
        lDisplayOnly=False
        lExit=True

    if not lExit:

        if debug:
            print "Parameters Captured", "Sec: ",user_hideHiddenSecurities.getText(), "InActAct:", user_hideInactiveAccounts.getText(), "HidAct:", user_hideHiddenAccounts.getText(), "Curr:", user_selectCurrency.getText(), "Ticker:",user_selectTicker.getText(), "Filter Accts:",user_selectAccounts.getText(),"Include Cash Balances:",user_selectCashBalances.getText(), "Strip ASCII:", user_selectStripASCII.getText(), "Verbose Debug Messages: ", user_selectDEBUG.getText()
            if lIamAMac:print "Use Mac-like Filename GUI:", user_selectMacFileChooser.getText()
        #endif  
        
        hideHiddenSecurities=False
        hideInactiveAccounts=False
        hideHiddenAccounts=False
        if user_hideHiddenSecurities.getText() == "Y":  hideHiddenSecurities = True
        else:                                           hideHiddenSecurities = False
        if user_hideInactiveAccounts.getText() == "Y":  hideInactiveAccounts = True
        else:                                           hideInactiveAccounts = False
        if user_hideHiddenAccounts.getText()   == "Y":  hideHiddenAccounts   = True
        else:                                           hideHiddenAccounts   = False

        if user_selectCurrency.getText() == "ALL":      lAllCurrency=True
        else:
            lAllCurrency=False
            filterForCurrency=user_selectCurrency.getText()

        if user_selectTicker.getText() == "ALL":        lAllSecurity=True
        else:
            lAllSecurity=False
            filterForSecurity=user_selectTicker.getText()

        if user_selectAccounts.getText() == "ALL":      lAllAccounts=True
        else:
            lAllAccounts=False
            filterForAccounts=user_selectAccounts.getText()

        if user_selectCashBalances.getText() == "Y":    lIncludeCashBalances=True
        else:                                           lIncludeCashBalances=False

        if user_selectStripASCII.getText() == "Y":      lStripASCII=True
        else:                                           lStripASCII=False

        if user_selectDEBUG.getText() == "Y":   debug=True
        else:
            debug=False
        if debug: print "DEBUG turned on"

        if lIamAMac:
            if user_selectMacFileChooser.getText() == "Y":   lUseMacFileChooser=True
            else:                                            lUseMacFileChooser=False
            
        print "Parameters..."    
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
            print "Filtering for Currency: ", filterForCurrency

        if lAllSecurity:
            print "Selecting ALL Securities..."
        else:
            print "Filtering for Security/Ticker: ", filterForSecurity

        if lAllAccounts:
            print "Selecting ALL Accounts..."
        else:
            print "Filtering for Accounts containing: ", filterForAccounts

        if lIncludeCashBalances:
            print "Including Cash Balances - WARNING - this is per account!"
        else:
            print "Excluding Cash Balances"

              
        # Now get the export filename    
        csvfilename = None

        if not lDisplayOnly:  #i.e. we have asked for a file export - so get the filename

            if lIamAMac:
                if lUseMacFileChooser:
                    print "I am a Mac. FileDialog Mac-like filename GUI choosen"
                else:
                    print "I am a Mac, but User asked to use older non-Mac GUI JFileChooser.."
             
            if lStripASCII:
                print "Will strip non-ASCII characters - e.g. Currency symbols from output file..."
            else:
                print "Non-ASCII characters will not be stripped from file: "

            def myDir():
                homeDir = System.getProperty("user.home")
                if debug: print "Home Directory:", homeDir
                if homeDir == None: Return("")
                return homeDir

            def grabTheFile():
                global debug, lDisplayOnly, csvfilename, lIamAMac, lUseMacFileChooser
                if debug: print "In ", inspect.currentframe().f_code.co_name, "()"     

                scriptpath = moneydance_data.getRootFolder().getParent()        # Path to Folder holding MD Datafile
                if scriptpath == None:  scriptpath=myDir()
                if debug: print "Scriptpath:", scriptpath

                    
                csvfilename=""
                if  lIamAMac and lUseMacFileChooser:
                    if debug: print "MacOS X detected: Therefore I will run FileDialog with no extension filters to get filename...."
                    # jFileChooser hangs on Mac when using file extension filters, also looks rubbish. So using Mac(ish)GUI
                    System.setProperty("com.apple.macos.use-file-dialog-packages", "true") # In theory prevents access to app file structure (but doesnt seem to work)
                    System.setProperty("apple.awt.fileDialogForDirectories", "false")
                    filename = FileDialog(None, "Select/Create CSV file for Stock Balances extract (CANCEL=NO EXPORT)")
                    filename.setMultipleMode(False)
                    filename.setMode(FileDialog.SAVE)
                    filename.setFile('extract_stock_balances.csv')
                    if (scriptpath <> None and scriptpath <> ""): filename.setDirectory(scriptpath)
                    filename.setVisible(True)

                    csvfilename = filename.getFile()
            
                    if (csvfilename == None) or csvfilename == "":
                        lDisplayOnly=True
                        csvfilename=None
                        print "User chose to cancel or no file selected >>  So no Extract will be performed... "
                    elif str(csvfilename).endswith(".moneydance"):
                        print "User selected file:", csvfilename
                        print "Sorry - User chose to use .moneydance extension - I will not allow it!... So no Extract will be performed..."
                        lDisplayOnly = True
                        csvfilename = None
                    elif ".moneydance" in filename.getDirectory():
                        print "User selected file:", filename.getDirectory(),csvfilename
                        print "Sorry - FileDialog() User chose to save file in .moneydance location. NOT Good practice so I will not allow it!... So no Extract will be performed..."
                        lDisplayOnly = True
                        csvfilename = None
                    else:
                        csvfilename=str(java.io.File(filename.getDirectory()+os.path.sep+filename.getFile()))   # NOTE: FileDialog checks for file overwrite and seeks confirmation....
                    
                    if not lDisplayOnly:
                        if os.path.exists(csvfilename) and os.path.isfile(csvfilename):print "WARNING: file exists,but assuming user said OK to overwrite.."
                else:
                    if debug:
                        if lIamAMac:
                            print "Mac platform detected, but user specified to run JFileChooser()  to get filename...."
                        else:
                            print "Non Mac platform detected: Therefore I will run JFileChooser()  to get filename...."

                    filename = JFileChooser(scriptpath)

                    filename.setSelectedFile(java.io.File(scriptpath+os.path.sep+'extract_stock_balances.csv'))
                    extfilter = javax.swing.filechooser.FileNameExtensionFilter("CSV file (CSV,TXT)", ["csv","TXT"])

                    filename.setMultiSelectionEnabled(False)
                    if not lIamAMac:
                        # this locks up Macs
                        filename.setFileFilter(extfilter)
                        
                    filename.setDialogTitle("Select/Create CSV file for Stock Balances extract (CANCEL=NO EXPORT)")
                    filename.setPreferredSize(Dimension(800,800))
                    returnvalue = filename.showDialog(None,"Extract")

                    if returnvalue==JFileChooser.CANCEL_OPTION:
                        lDisplayOnly=True
                        csvfilename = None
                        print "User chose to cancel = So no Extract will be performed... "
                    elif filename.selectedFile==None:
                        lDisplayOnly=True
                        csvfilename = None
                        print "User chose no filename... So no Extract will be performed..."
                    elif str(filename.selectedFile).endswith(".moneydance"):
                        lDisplayOnly=True
                        csvfilename = None
                        print "User selected file:", filename.selectedFile
                        print "Sorry - User chose to use .moneydance extension - I will not allow it!... So no Extract will be performed..."
                    elif str(filename.selectedFile).endswith(".moneydance"):
                        lDisplayOnly=True
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
                            if (JOptionPane.showConfirmDialog(None, "File '"+os.path.basename(csvfilename)+"' exists... Press YES to overwrite and proceed, NO to continue with no Extract?","WARNING",JOptionPane.YES_NO_OPTION,JOptionPane.WARNING_MESSAGE)==JOptionPane.YES_OPTION):
                                print "User agreed to overwrite file..."
                            else:
                                lDisplayOnly=True
                                csvfilename = None
                                print "User does not want to overwrite file... Proceeding without Extract..."
                            #endif
                        #endif
                    #endif

                #endif

                if not lDisplayOnly: print 'Will display Stock balances and then extract to file: ', csvfilename, "(NOTE: Should drop non utf8 characters...)"

                if "filename"               in vars() or "filename"             in globals():   del filename
                if "extfilter"              in vars() or "extfilter"            in globals():   del extfilter

                return()
            #enddef
    

            if not lDisplayOnly: grabTheFile()
        else:
            pass
        #endif
                
        if csvfilename == None:
            lDisplayOnly=True
            print "No Export will be performed"

        class StockGlance2020():   # MAIN program....
            global debug, hideHiddenSecurities, hideInactiveAccounts
            global rawDataTable, rawFooterTable, headingNames

            if debug: print "In ", inspect.currentframe().f_code.co_name, "()"    

            book = None 
            table = None 
            tableModel = None  
            footerModel = None 
            totalBalance = None # total of all Stock.Securities in all Accounts inb local currency 
            totalBalanceBase = None 
            totalCashBalanceBase = None

            sameCurrency = None
            allOneCurrency = True
            currXrate = None

            QtyOfSharesTable = None
            AccountsTable = None
            CashBalancesTable = None
            CashBalanceTableData = Vector()

            lightLightGray = Color(0xDCDCDC)    

            rawFooterTable = Vector() # one row of footer data
            rawDataTable = Vector() # the data retrieved from moneydance

            #  Per column metadata - fields 8 - 11 not actually used but contain the raw numbers from fields 2,3,5,6
            # Fields       0          1         2                   3               4        5              6              7          8       9       10        11
            names =       ["Symbol", "Stock",  "Shares/Units",      "Price",        "Curr",  "Curr Value",  "Base Value",  "Accounts","_Shrs","_Price","_CValue","_BValue"]
            columnTypes = ["Text",   "Text",   "TextNumber",        "TextNumber",   "TextC", "TextNumber",  "TextNumber",  "Text",    "N",    "N",      "N",     "N"]
            columnNames = Vector(Arrays.asList(names))
            headingNames=names
            _SHRS_FORMATTED = 2
            _SHRS_RAW = 8
            _PRICE_FORMATTED = 3
            _PRICE_RAW = 9
            _CVALUE_FORMATTED = 5
            _CVALUE_RAW = 10
            _BVALUE_FORMATTED = 6
            _BVALUE_RAW = 11

            def getTableModel(self, book):
                global debug, baseCurrency, rawDataTable, lAllCurrency, filterForCurrency, lAllSecurity, filterForSecurity
                if debug: print "In ", inspect.currentframe().f_code.co_name, "()"
                if debug: print "MD Book: ",book

                ct = book.getCurrencies()

                baseCurrency = moneydance.getCurrentAccountBook().getCurrencies().getBaseType()
                if debug: print "Base Currency: ", baseCurrency.getIDString()," : ",baseCurrency.getName()

                allCurrencies = ct.getAllCurrencies()
                if debug: print "getAllCurrencies(): ", allCurrencies

                rawDataTable = Vector()
                today = Calendar.getInstance()
                if debug: print "Running today: ",sdf.format(today.getTime())

                self.sumInfoBySecurity(book)                    # Creates HashMaps QtyOfSharesTable, AccountsTable, CashTable : <CurrencyType, Long>  contains no account info

                if debug:
                    print "Result of sumInfoBySecurity(book): ", self.QtyOfSharesTable
                    print "Result of sumInfoBySecurity(book): ", self.AccountsTable
                    print "Result of sumInfoBySecurity(book): ", self.CashBalancesTable

                self.totalBalance = 0.0
                self.totalBalanceBase = 0.0
                self.totalCashBalanceBase = 0.0

                if debug: print "Now processing all securitys (currencies) and building my own table of results to build GUI...."
                for curr in allCurrencies:

                    if ((hideHiddenSecurities and not curr.getHideInUI() ) or (not hideHiddenSecurities) ) and curr.getCurrencyType() == CurrencyType.Type.SECURITY:
                        # NOTE: (1.0 / .getRelativeRate() ) gives you the 'Current Price' from the History Screen
                        # NOTE: .getPrice(None) gives you the Current Price relative to the current Base to Security Currency.. So Base>Currency rate * .getRate(None) also gives Current Price

                        price = 1.0/curr.adjustRateForSplitsInt(DateUtil.convertCalToInt(today),curr.getRelativeRate()) 

                        qty = self.QtyOfSharesTable.get(curr)
                        if qty == None: qty = 0

                        if lAllCurrency or curr.getRelativeCurrency().getIDString() == filterForCurrency: 
                            if qty > 0: #and curr.getTickerSymbol() == "YYY SEC":

                                if lAllSecurity or curr.getTickerSymbol() == filterForSecurity:
                                    if debug: print "Found Security..: ",curr, curr.getTickerSymbol()," Curr: ",curr.getRelativeCurrency().getIDString()," Price: ",price, " Qty: ",curr.formatSemiFancy(qty,".")
                                    if not lAllSecurity: print curr.getTickerSymbol() , filterForSecurity
                                    entry = Vector(len(self.names))
                                    balance = (0.0 if (qty == None) else curr.getDoubleValue(qty) * price)  # Value in Currency


                                    exchangeRate=1.0
                                    securityIsBase = True
                                    ct = curr.getTable()
                                    relativeToName = curr.getParameter(CurrencyType.TAG_RELATIVE_TO_CURR)
                                    if relativeToName != None:
                                        self.currXrate = ct.getCurrencyByIDString(relativeToName)
                                        if self.currXrate.getIDString() == baseCurrency.getIDString():
                                            if debug: print "Found conversion rate - but it's already the base rate..: ", relativeToName
                                        else:
                                            securityIsBase = False                            
                                            #exchangeRate = round(self.currXrate.getRate(baseCurrency),self.currXrate.getDecimalPlaces())
                                            exchangeRate = self.currXrate.getRate(baseCurrency)
                                            if debug: print "Found conversion rate: ", relativeToName, exchangeRate
                                    else:
                                        if debug: print "No conversion rate found.... Assuming Base Currency"
                                        self.currXrate = baseCurrency

                                    # Check to see if all Security Currencies are the same...?
                                    if self.allOneCurrency:
                                        if self.sameCurrency == None: self.sameCurrency = curr
                                        if self.sameCurrency <> curr: self.allOneCurrency = False


                                    balanceBase = (0.0 if (qty == None) else (curr.getDoubleValue(qty) * price/exchangeRate) ) # Value in Base Currency

                                    if debug: print "Values found (local, base): ",balance, balanceBase
                                    self.totalBalance += round(balance,0)               # The totals are displayed without decimals, so round the totals too...
                                    self.totalBalanceBase += round(balanceBase,0)       # The totals are displayed without decimals, so round the totals too...

                                    if lIncludeCashBalances:
                                        cash=0.0
                                        # Search to see if Account exists/has been used already for Cash Balance - Only use once!
                                        for keys in self.CashBalancesTable.keySet():
                                            data = self.CashBalancesTable.get(keys)
                                            if (str(keys)+' :') in str(self.AccountsTable.get(curr)):
                                                if debug: print "CashBal Search - Found:", keys, "in", str(self.AccountsTable.get(curr)), "Cash Bal:",data
                                                cash=data
                                                self.CashBalancesTable.put(keys,0.0) # Now delete it so it cannot be used again!
                                                self.totalCashBalanceBase = self.totalCashBalanceBase + cash
                                                rowDataEntry=Vector(2)
                                                rowDataEntry.add(keys)
                                                rowDataEntry.add(cash)
                                                self.CashBalanceTableData.add(rowDataEntry)
                                                continue
                                                # Keep searching as a Security may be used in many accounts...



                                    if debug:
                                        print "myNumberFormatter - Original Price: ", price, " :: ", self.myNumberFormatter(price, False, self.currXrate, baseCurrency, False)
                                            
                                    entry.add(curr.getTickerSymbol())                                                        # c0
                                    entry.add(curr.getName())                                                                # c1
                                    entry.add(curr.formatSemiFancy(qty,"."))                                                 # c2
                                    entry.add(self.myNumberFormatter(price, False, self.currXrate, baseCurrency, False)  )   # c3
                                    entry.add(self.currXrate.getIDString())                                                  # c4
                                    entry.add(self.myNumberFormatter(balance, False, self.currXrate, baseCurrency, True) )   # c5
                                    entry.add(self.myNumberFormatter(balanceBase, True, self.currXrate, baseCurrency, True)) # c6
                                    entry.add(self.AccountsTable.get(curr))                                                  # c7
                                    entry.add(curr.getDoubleValue(qty))                                                      # c8 _Shrs = c2 (raw number)
                                    entry.add(price)                                                                         # c9 _Price = c3 (raw number)
                                    entry.add(balance)                                                                       # c10 _CValue = c5 (raw number)
                                    entry.add(balanceBase)                                                                   # c11 _BValue = c6 (raw number)
                                    rawDataTable.add(entry)
                                else:
                                    if debug: print "Skipping non Filtered Security/Ticker:", curr, curr.getTickerSymbol()
                            else:
                                if debug: print "Skipping Security with 0 shares..: ",curr, curr.getTickerSymbol()," Curr: ",curr.getRelativeCurrency().getIDString()," Price: ",price, " Qty: ",curr.formatSemiFancy(qty,".")
                        else:
                            if debug: print "Skipping non Filterered Security/Currency:", curr, curr.getTickerSymbol(), curr.getRelativeCurrency().getIDString()
                    elif curr.getHideInUI() and curr.getCurrencyType() == CurrencyType.Type.SECURITY:
                            if debug: print "Skipping Hidden(inUI) Security..: ",curr, curr.getTickerSymbol()," Curr: ",curr.getRelativeCurrency().getIDString()

                    else: 
                        if debug: print "Skipping non Security:",curr, curr.getTickerSymbol()
                return DefaultTableModel(rawDataTable, self.columnNames)

            def getFooterModel(self):
                global debug, baseCurrency, rawFooterTable, lIncludeCashBalances
                if debug: print "In ", inspect.currentframe().f_code.co_name, "()"     

                entry = Vector(len(self.names)) 
                entry.add("Totals:")
                entry.add(None)
                entry.add(None)
                entry.add(None)
                entry.add(None)
                x=0
                if self.allOneCurrency:
                    if debug: print "getFooterModel: sameCurrency=",self.currXrate 
                    if self.currXrate==None:
                        entry.add(None)
                    else:
                        x=self.totalBalance
                        entry.add(self.myNumberFormatter(self.totalBalance, False, self.currXrate, baseCurrency, True))
                else:
                    entry.add(None)
                entry.add(self.myNumberFormatter(self.totalBalanceBase, True, baseCurrency, baseCurrency, True))
                entry.add("<<"+baseCurrency.getIDString())
                entry.add(0)
                entry.add(0)
                entry.add(x)
                entry.add(self.totalBalanceBase)
                rawFooterTable.clear()
                rawFooterTable.add(entry)
                if lIncludeCashBalances :
                    entry = Vector(len(self.names))
                    entry.add("---------")
                    entry.add(None)
                    entry.add(None)
                    entry.add(None)
                    entry.add(None)
                    entry.add(None)
                    entry.add("---------")
                    entry.add(None)
                    entry.add(0)
                    entry.add(0)
                    entry.add(0)
                    entry.add(0)
                    rawFooterTable.add(entry)

                    for i in range(0,len(self.CashBalanceTableData)):
                        if self.CashBalanceTableData[i][1] <> 0:
                            entry = Vector(len(self.names))
                            entry.add("Cash Bal/Acct:")
                            entry.add(None)
                            entry.add(None)
                            entry.add(None)
                            entry.add(None)
                            entry.add(None)
                            entry.add(self.myNumberFormatter(self.CashBalanceTableData[i][1], True, baseCurrency, baseCurrency, True))
                            entry.add(str(self.CashBalanceTableData[i][0]))
                            entry.add(0)
                            entry.add(0)
                            entry.add(0)
                            entry.add(0)
                            rawFooterTable.add(entry)
                    entry = Vector(len(self.names))
                    entry.add("==========")
                    entry.add(None)
                    entry.add(None)
                    entry.add(None)
                    entry.add(None)
                    entry.add(None)
                    entry.add("==========")
                    entry.add(None)
                    entry.add(0)
                    entry.add(0)
                    entry.add(0)
                    entry.add(0)
                    rawFooterTable.add(entry)
                    entry = Vector(len(self.names))
                    entry.add("Cash Bal TOTAL:")
                    entry.add(None)
                    entry.add(None)
                    entry.add(None)
                    entry.add(None)
                    entry.add(None)
                    entry.add(self.myNumberFormatter(self.totalCashBalanceBase, True, baseCurrency, baseCurrency, True))
                    entry.add("Across all Accounts involved in this table")
                    entry.add(0)
                    entry.add(0)
                    entry.add(0)
                    entry.add(0)
                    rawFooterTable.add(entry)

                return DefaultTableModel(rawFooterTable,self.columnNames)


            # Render a currency with given number of fractional digits. NaN or null is an empty cell.
            def myNumberFormatter(self, theNumber, useBase, exchangeCurr, baseCurr, noDecimals):
                global debug

                decimalSeparator = '.'
                noDecimalFormatter = NumberFormat.getNumberInstance()
                noDecimalFormatter.setMinimumFractionDigits(0)
                noDecimalFormatter.setMaximumFractionDigits(0)

                if theNumber == None or Double.isNaN(float(theNumber)): return("")

                if Math.abs(float(theNumber)) < 0.01: theNumber = 0L

                if useBase:
                    if noDecimals:
                        # MD format functions can't print comma-separated values without a decimal point so
                        # we have to do it ourselves
                        theNumber = baseCurr.getPrefix() + " " + noDecimalFormatter.format(float(theNumber)) + baseCurr.getSuffix()
                    else:

                        theNumber = baseCurr.formatFancy(baseCurr.getLongValue(float(value)), decimalSeparator)
                else:

                    if noDecimals:
                        # MD format functions can't print comma-separated values without a decimal point so
                        # we have to do it ourselves
                        theNumber = exchangeCurr.getPrefix() + " " + noDecimalFormatter.format(float(theNumber)) + exchangeCurr.getSuffix()
                    else:

                        theNumber = exchangeCurr.formatFancy(exchangeCurr.getLongValue(float(theNumber)), decimalSeparator)

                return(theNumber) 


            def sumInfoBySecurity(self, book):
                global debug, hideInactiveAccounts, hideHiddenAccounts, lAllAccounts, filterForAccounts, lIncludeCashBalances
                if debug: print "In ", inspect.currentframe().f_code.co_name, "()"     

                # FYI - Inactive accounts are always hidden from Home Screen
                if hideInactiveAccounts:
                    myFilter = AcctFilter.ACTIVE_ACCOUNTS_FILTER
                else:
                    myFilter = AcctFilter.ALL_ACCOUNTS_FILTER

                totals = HashMap() #  HashMap<CurrencyType, Long> 
                accounts = HashMap()
                cashTotals = HashMap() #  HashMap<CurrencyType, Long> 
                for acct in AccountUtil.allMatchesForSearch(book, myFilter ): # i.e. return all active accounts....
                    if (acct.getAccountType() == AccountType.SECURITY):
                        if lAllAccounts or (filterForAccounts.upper() in str(acct.getParentAccount()).upper()):     
                            if ((not hideHiddenAccounts) or (hideHiddenAccounts and not acct.getParentAccount().getHideOnHomePage())):
                                curr = acct.getCurrencyType()                                      
                                account = accounts.get(curr)# this returns None if curr doesn't exist yet
                                total = totals.get(curr) # this returns None if security/curr doesn't exist yet
                                if acct.getCurrentBalance() != 0: # we only want Securities with holdings
                                    if debug: print "Processing Acct:",acct.getParentAccount(), "Share/Fund Qty Balances for Security: ", curr, curr.formatSemiFancy(acct.getCurrentBalance(),".")," Shares/Units"

                                    total = (0L if (total == None) else total) + acct.getCurrentBalance()            
                                    totals.put(curr, total)

                                    if account == None: account = str(acct.getParentAccount())+' : '           # Important - keep the trailing ' :'
                                    else:               account = account + str(acct.getParentAccount())+' : ' # concatinate two strings here
                                    accounts.put(curr,account)

                                    if lIncludeCashBalances:
                                        # Now get the Currency  for the Security Parent Account - to get Cash  Balance
                                        curr = acct.getParentAccount().getCurrencyType()

                                        # WARNING Cash balances are by Account and not by Security!
                                        cashTotal = cashTotals.get(acct.getParentAccount()) # this returns None if Account doesn't exist yet
                                        cashTotal = curr.getDoubleValue((acct.getParentAccount().getCurrentBalance()))/curr.getRate(None) # Will be the same Cash balance per account for all Securities..
                                        if debug: print "Cash balance for account:", cashTotal 
                                        cashTotals.put(acct.getParentAccount(), cashTotal)


                            elif hideHiddenAccounts and acct.getHideOnHomePage():
                                if debug: print "Skipping hidden Account: ", acct.getParentAccount(), acct.getCurrencyType()

                self.QtyOfSharesTable=totals     
                self.AccountsTable=accounts
                self.CashBalancesTable=cashTotals
                return

            class myJTable(JTable): # (JTable)
                if debug: print "In ", inspect.currentframe().f_code.co_name, "()"     

                def __init__(self, tableModel,lSortTheTable):
                    global debug
                    super(JTable, self).__init__(tableModel)
                    if lSortTheTable: self.fixTheRowSorter() 

                def isCellEditable(self, row, column):
                    return False

                #  Rendering depends on row (i.e. security's currency) as well as column
                def getCellRenderer(self, row, column):
                    global StockGlanceInstance 
                    renderer = None
                    if StockGlanceInstance.columnTypes[column]=="Text":
                        renderer = DefaultTableCellRenderer()
                        renderer.setHorizontalAlignment(JLabel.LEFT)
                    elif StockGlanceInstance.columnTypes[column]=="TextNumber":
                        renderer = DefaultTableCellRenderer()
                        renderer.setHorizontalAlignment(JLabel.RIGHT)
                    elif StockGlanceInstance.columnTypes[column]=="TextC":
                        renderer = DefaultTableCellRenderer()
                        renderer.setHorizontalAlignment(JLabel.CENTER)
                    else:
                        renderer = DefaultTableCellRenderer()
                    return renderer

                class myTextNumberComparator (Comparator):
                    lSortNumber = False

                    def __init__(self, sortType):
                        if sortType=="N":
                            self.lSortNumber=True
                        else:
                            self.lSortNumber=False

                    def compare( self, str1 , str2):
                        validString="-0123456789."
                        if self.lSortNumber:
                            # strip non numerics from string so can convert back to float - yes, a bit of a reverse hack
                            conv_string1=""
                            if str1==None: str1="0"
                            if str2==None: str2="0"
                            for char in str1:
                                if char in validString:
                                    conv_string1 = conv_string1+char

                            conv_string2=""
                            for char in str2:
                                if char in validString:
                                    conv_string2 = conv_string2+char
                            str1=float(conv_string1)
                            str2=float(conv_string2)
                        else:
                            pass

                        if str1 > str2:
                            return 1
                        elif str1 == str2:
                            return 0
                        else:
                            return(-1)
                    #enddef 

                def fixTheRowSorter(self):    # by default everthing gets coverted to strings. We need to fix this and code for my string number formats
                    sorter = TableRowSorter()           
                    self.setRowSorter(sorter)                               
                    sorter.setModel(self.getModel())                          
                    for i in range (0 , self.getColumnCount() ) :  
                        if i==StockGlanceInstance._SHRS_FORMATTED:
                            sorter.setComparator(i,self.myTextNumberComparator("N"))    
                        elif i==StockGlanceInstance._PRICE_FORMATTED:
                            sorter.setComparator(i,self.myTextNumberComparator("N"))    
                        elif i==StockGlanceInstance._CVALUE_FORMATTED:
                            sorter.setComparator(i,self.myTextNumberComparator("N"))    
                        elif i==StockGlanceInstance._BVALUE_FORMATTED:
                            sorter.setComparator(i,self.myTextNumberComparator("N"))    
                        else:
                            sorter.setComparator(i,self.myTextNumberComparator("T"))    
                    self.getRowSorter().toggleSortOrder(0) 

                def prepareRenderer(self, renderer, row, column):  # make Banded rows
                    global StockGlanceInstance 
                    component = super(StockGlanceInstance.myJTable, self).prepareRenderer(renderer, row, column)
                    if not self.isRowSelected(row):
                        component.setBackground(self.getBackground() if row % 2 == 0 else StockGlanceInstance.lightLightGray)
                    return component

            # Syncronises column widths of both JTables
            class ColumnChangeListener(TableColumnModelListener):
                sourceTable=None
                targetTable=None

                def __init__(self, source, target):
                    self.sourceTable = source
                    self.targetTable = target

                def columnAdded(self, e ): pass
                def columnSelectionChanged(self, e ): pass
                def columnRemoved(self, e ): pass
                def columnMoved(self, e ): pass

                def columnMarginChanged(self,e):
                    sourceModel = self.sourceTable.getColumnModel()
                    targetModel = self.targetTable.getColumnModel()
                    #listener = map.get(self.targetTable)

                    #targetModel.removeColumnModelListener(listener)

                    for i in range(0, sourceModel.getColumnCount()):
                        targetModel.getColumn(i).setPreferredWidth(sourceModel.getColumn(i).getWidth())

                    #targetModel.addColumnModelListener(listener)
                #enddef
            #endclass

            # Sync horizontal scroll bars with footer (vertical sync disabled)
            class ScrollSynchronizer(AdjustmentListener):
                v1=None
                h1=None
                v2=None
                h2=None

                def __init__(self, sp1, sp2):
                    #self.v1 = sp1.getVerticalScrollBar()
                    self.h1 = sp1.getHorizontalScrollBar()
                    #self.v2 = sp2.getVerticalScrollBar()
                    self.h2 = sp2.getHorizontalScrollBar()

                def adjustmentValueChanged(self, e):
                    scrollBar = e.getSource()
                    value = scrollBar.getValue()
                    target = None

                    #if(scrollBar == self.v1): target = self.v2
                    if(scrollBar == self.h1): target = self.h2
                    #if(scrollBar == self.v2): target = self.v1
                    if(scrollBar == self.h2): target = self.h1

                    if target<>None: target.setValue(value)
                #enddef
            #endclass

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
                global debug, frame_, rawDataTable, rawFooterTable, lDisplayOnly

                if debug: print "In ", inspect.currentframe().f_code.co_name, "()"     

                root = moneydance.getRootAccount()
                self.book = root.getBook()

                screenSize = Toolkit.getDefaultToolkit().getScreenSize()

                if lDisplayOnly:
                    frame_ = JFrame("Stock Glance 2020 - StuWareSoftSystems...")
                else:
                    frame_ = JFrame("Stock Glance 2020 - StuWareSoftSystems... (CLOSE WINDOW TO EXPORT TO FILE)")

                #frame_.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE) 
                frame_.setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE) # The CloseAction() and WindowListener() will handle dispose() - else change back to DISPOSE_ON_CLOSE

                # Add standard CMD-W keystrokes etc to close window
                frame_.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke("control W"), "close-window")
                frame_.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke("meta W"), "close-window")
                frame_.getRootPane().getActionMap().put("close-window", self.CloseAction())

                frame_.addWindowListener(self.WindowListener())

                self.tableModel = self.getTableModel(self.book) # Generates/populates the table data

                self.table = self.myJTable(self.tableModel,True)      # Creates JTable() with special sorting too
                self.tableHeader = self.table.getTableHeader()
                self.tableHeader.setReorderingAllowed(False) # no more drag and drop columns, it didn't work (on the footer)
                self.table.getTableHeader().setDefaultRenderer(DefaultTableHeaderCellRenderer())

                self.footerModel = self.getFooterModel()        # Generate/populate the footer table data
                self.footerTable = self.myJTable(self.footerModel,False) # Creates JTable() for footer - with disabled sorting too


                # Column listeners to resize columns on both tables to keep them in sync
                cListener1=self.ColumnChangeListener(self.table,self.footerTable)
                #cListener2=self.ColumnChangeListener(self.footerTable,self.table) # Not using this as footer headers not manually resizable (as hidden)

                tcm = self.table.getColumnModel()
                tcm.addColumnModelListener(cListener1)

                c0=120 
                c1=300
                c2=120
                c3=80
                c4=80
                c5=120
                c6=120
                c7=350
                c8=0
                c9=0
                c10=0
                c11=0
                cTotal=c0+c1+c2+c3+c4+c5+c6+c7+c8+c9+c10+c11+c11


                tcm.getColumn(0).setPreferredWidth(c0)
                tcm.getColumn(1).setPreferredWidth(c1)
                tcm.getColumn(2).setPreferredWidth(c2)
                tcm.getColumn(3).setPreferredWidth(c3)
                tcm.getColumn(4).setPreferredWidth(c4)
                tcm.getColumn(5).setPreferredWidth(c5)
                tcm.getColumn(6).setPreferredWidth(c6)
                tcm.getColumn(7).setPreferredWidth(c7)

                # I'm hiding these columns for ease of data retrieval. The better option would be to remove the columns
                for i in reversed(range(8,tcm.getColumnCount())):
                    tcm.getColumn(i).setMinWidth(0)
                    tcm.getColumn(i).setMaxWidth(0)
                    tcm.getColumn(i).setWidth(0)
                    self.table.removeColumn(tcm.getColumn(i))
                self.table.setAutoResizeMode(JTable.AUTO_RESIZE_OFF )


                self.footerTable.setColumnSelectionAllowed(False)
                self.footerTable.setRowSelectionAllowed(False)
                self.footerTable.setFocusable(False)

                tcm = self.footerTable.getColumnModel()
                #tcm.addColumnModelListener(cListener2)
                tcm.getColumn(0).setPreferredWidth(c0)
                tcm.getColumn(1).setPreferredWidth(c1)
                tcm.getColumn(2).setPreferredWidth(c2)
                tcm.getColumn(3).setPreferredWidth(c3)
                tcm.getColumn(4).setPreferredWidth(c4)
                tcm.getColumn(5).setPreferredWidth(c5)
                tcm.getColumn(6).setPreferredWidth(c6)
                tcm.getColumn(7).setPreferredWidth(c7)

                # I'm hiding these columns for ease of data retrieval. The better option would be to remove the columns
                for i in reversed(range(8,tcm.getColumnCount())):
                    tcm.getColumn(i).setMinWidth(0)
                    tcm.getColumn(i).setMaxWidth(0)
                    tcm.getColumn(i).setWidth(0)
                    self.footerTable.removeColumn(tcm.getColumn(i))
                self.footerTable.setAutoResizeMode(JTable.AUTO_RESIZE_OFF )

                self.footerTableHeader = self.footerTable.getTableHeader()
                self.footerTableHeader.setEnabled(False) # may have worked, but doesn't...
                self.footerTableHeader.setPreferredSize(Dimension(0,0)) # this worked no more footer Table header


                self.scrollPane = JScrollPane(self.table, JScrollPane.VERTICAL_SCROLLBAR_ALWAYS, JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED)
                self.scrollPane.getHorizontalScrollBar().setPreferredSize(Dimension(0, 0))
                self.scrollPane.setBorder(CompoundBorder(MatteBorder(0, 0, 1, 0, Color.gray), EmptyBorder(0, 0, 0, 0)))
                rowCount = self.table.getRowCount()
                rowHeight = self.table.getRowHeight()
                interCellSpacing = self.table.getIntercellSpacing().height
                headerHeight = self.table.getTableHeader().getPreferredSize().height
                insets = self.scrollPane.getInsets()
                scrollHeight = self.scrollPane.getHorizontalScrollBar().getPreferredSize()
                width = min(cTotal+20,screenSize.width) # width of all elements

                calcScrollPaneHeightRequired = min(screenSize.height-100,max(60,((rowCount*rowHeight)+((rowCount)*(interCellSpacing))+headerHeight+insets.top+insets.bottom+scrollHeight.height)) )

                if debug:
                    print "ScreenSize: ", screenSize
                    print "Main JTable heights...."
                    print "Row Count: ", rowCount
                    print "RowHeight: ",rowHeight
                    print "Intercell spacing: ",interCellSpacing
                    print "Header height: ",headerHeight
                    print "Insets, Top/Bot: ",insets,insets.top, insets.bottom
                    print "Total scrollpane height: ", calcScrollPaneHeightRequired
                    print "Scrollbar height: ", scrollHeight, scrollHeight.height

                #Basically set the main table to fill most of the screen maxing at 800, but allowing for the footer...
                self.scrollPane.setPreferredSize(Dimension(width,calcScrollPaneHeightRequired)) 

                frame_.add(self.scrollPane, BorderLayout.CENTER)        

                self.footerScrollPane = JScrollPane(self.footerTable, JScrollPane.VERTICAL_SCROLLBAR_ALWAYS, JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED)
                self.footerScrollPane.setBorder(CompoundBorder(MatteBorder(0, 0, 1, 0, Color.gray), EmptyBorder(0, 0, 0, 0)))

                myScrollSynchronizer=self.ScrollSynchronizer(self.scrollPane,self.footerScrollPane)
                #self.scrollPane.getVerticalScrollBar().addAdjustmentListener(myScrollSynchronizer)
                self.scrollPane.getHorizontalScrollBar().addAdjustmentListener(myScrollSynchronizer)
                #self.footerScrollPane.getVerticalScrollBar().addAdjustmentListener(myScrollSynchronizer)
                self.footerScrollPane.getHorizontalScrollBar().addAdjustmentListener(myScrollSynchronizer)

                frowCount = self.footerTable.getRowCount()
                frowHeight = self.footerTable.getRowHeight()
                finterCellSpacing = self.footerTable.getIntercellSpacing().height
                fheaderHeight = self.footerTable.getTableHeader().getPreferredSize().height
                finsets = self.footerScrollPane.getInsets()
                fscrollHeight = self.footerScrollPane.getHorizontalScrollBar().getPreferredSize()
                fcalcScrollPaneHeightRequired = ( ((frowCount*frowHeight)+((frowCount+1)*finterCellSpacing)+fheaderHeight+finsets.top+finsets.bottom+fscrollHeight.height) )

                if debug:
                    print "Footer JTable heights...."
                    print "Row Count: ", frowCount
                    print "RowHeight: ",frowHeight
                    print "Intercell spacing: ",finterCellSpacing
                    print "Header height: ",fheaderHeight
                    print "Insets, Top/Bot: ",finsets,finsets.top, finsets.bottom
                    print "Total scrollpane height: ", fcalcScrollPaneHeightRequired
                    print "Scrollbar height: ", fscrollHeight, fscrollHeight.height

                self.footerScrollPane.setPreferredSize(Dimension(width,fcalcScrollPaneHeightRequired))
                frame_.add(self.footerScrollPane, BorderLayout.SOUTH)

                if debug: print "Total frame height required: ", calcScrollPaneHeightRequired," + ",fcalcScrollPaneHeightRequired, "+ Intercells: ",finsets.top,finsets.bottom, " = ",(calcScrollPaneHeightRequired+fcalcScrollPaneHeightRequired)+(finsets.top*2)+(finsets.bottom*2)


                # Seems to be working well without setting the frame sizes + pack()
                #frame_.setPreferredSize(Dimension(width, max(150,calcScrollPaneHeightRequired+fcalcScrollPaneHeightRequired+(finsets.top*2)+(finsets.bottom*2))))
                #frame_.setSize(width,calcScrollPaneHeightRequired+fcalcScrollPaneHeightRequired)   # for some reason this seems irrelevant?

                frame_.pack()
                frame_.setVisible(True)
        #endclass


        #The javax.swing package and its subpackages provide a fairly comprehensive set of default renderer implementations, suitable for customization via inheritance. A notable omission is the lack #of a default renderer for a JTableHeader in the public API. The renderer used by default is a Sun proprietary class, sun.swing.table.DefaultTableCellHeaderRenderer, which cannot be extended.
        #DefaultTableHeaderCellRenderer seeks to fill this void, by providing a rendering designed to be identical with that of the proprietary class, with one difference: the vertical alignment of #the header text has been set to BOTTOM, to provide a better match between DefaultTableHeaderCellRenderer and other custom renderers.
        #The name of the class has been chosen considering this to be a default renderer for the cells of a table header, and not the table cells of a header as implied by the proprietary class name
        class DefaultTableHeaderCellRenderer(DefaultTableCellRenderer):

            #/**
            #* Constructs a <code>DefaultTableHeaderCellRenderer</code>.
            #* <P>
            #* The horizontal alignment and text position are set as appropriate to a
            #* table header cell, and the opaque property is set to false.
            #*/

            def __init__(self):
                #super(DefaultTableHeaderCellRenderer, self).__init__()
                self.setHorizontalAlignment(JLabel.CENTER)   # This one changes the text alignment
                self.setHorizontalTextPosition(JLabel.RIGHT) # This positions the  text to the  left/right of  the sort icon
                self.setVerticalAlignment(JLabel.BOTTOM)
                self.setOpaque(True) # if this is false then it hides the background colour
            #enddef

            #/**
            #* Returns the default table header cell renderer.
            #* <P>
            #* If the column is sorted, the approapriate icon is retrieved from the
            #* current Look and Feel, and a border appropriate to a table header cell
            #* is applied.
            #* <P>
            #* Subclasses may overide this method to provide custom content or
            #* formatting.
            #*
            #* @param table the <code>JTable</code>.
            #* @param value the value to assign to the header cell
            #* @param isSelected This parameter is ignored.
            #* @param hasFocus This parameter is ignored.
            #* @param row This parameter is ignored.
            #* @param column the column of the header cell to render
            #* @return the default table header cell renderer
            #*/

            def getTableCellRendererComponent(self, table, value, isSelected, hasFocus, row, column):
                super(DefaultTableHeaderCellRenderer,self).getTableCellRendererComponent(table, value, isSelected, hasFocus, row, column)
                tableHeader = table.getTableHeader()
                #if (tableHeader != None): self.setForeground(tableHeader.getForeground())
                align=firstRowTableCellRenderer = table.getCellRenderer(0, column).getHorizontalAlignment()    
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

                #self.setHorizontalAlignment(JLabel.CENTER)

                return self
            #enddef

            #/**
            #* Overloaded to return an icon suitable to the primary sorted column, or null if
            #* the column is not the primary sort key.
            #*
            #* @param table the <code>JTable</code>.
            #* @param column the column index.
            #* @return the sort icon, or null if the column is unsorted.
            #*/
            def _getIcon(self, table,column):
                sortKey = self.getSortKey(table, column)
                if (sortKey != None and table.convertColumnIndexToView(sortKey.getColumn()) == column):
                    x=(sortKey.getSortOrder())
                    if x == SortOrder.ASCENDING:      return UIManager.getIcon("Table.ascendingSortIcon")
                    elif x == SortOrder.DESCENDING:   return UIManager.getIcon("Table.descendingSortIcon")
                    elif x == SortOrder.UNSORTED:     return UIManager.getIcon("Table.naturalSortIcon")
                return None
            #enddef

            #/**
            #* Returns the current sort key, or null if the column is unsorted.
            #*
            #* @param table the table
            #* @param column the column index
            #* @return the SortKey, or null if the column is unsorted
            #*/
            def getSortKey(self, table, column):
                rowSorter = table.getRowSorter()
                if (rowSorter == None): return None
                sortedColumns = rowSorter.getSortKeys()
                if (sortedColumns.size() > 0): return sortedColumns.get(0)
                return None
            #enddef
        #endclass
            
        if not lDisplayOnly: print "!!!FILE WILL BE GENERATED AFTER YOU CLOSE THE TABLE VIEW WINDOW!!!"
        
        StockGlanceInstance = StockGlance2020()
        StockGlance2020.createAndShowGUI(StockGlanceInstance)

        # A bit of a fudge, but hey it works.....!
        i=0
        while frame_.isVisible():
                i=i+1
                time.sleep(1)
                if debug: print "Waiting for JFrame() to close... Wait number...:", i

        if debug: print "No longer waiting...."

        if "StockGlance2020" in vars() or "StockGlance2020" in globals():           del StockGlance2020
        if "StockGlanceInstance" in vars() or "StockGlanceInstance" in globals():   del StockGlanceInstance

        if not lDisplayOnly: 

            # function to output the amount (held as integer in cents) to 2 dec place amount field
            def formatasnumberforExcel(amountInt):

                amount = amountInt                      # Temporarily convert to a positive and then ensure always three digits
                if amountInt < 0:   amount *= -1
                str_amount = str(amount)
                if len(str_amount)<3: str_amount = ("0"+str_amount) # PAD with zeros to ensure whole number exists
                if len(str_amount)<3: str_amount = ("0"+str_amount)

                wholeportion    = str_amount[0:-2]
                placesportion   = str_amount[-2:]

                if amountInt < 0: wholeportion = '-'+wholeportion       # Put the negative back

                outputfield=wholeportion+'.'+placesportion
                return outputfield
            #enddef

            def ExportDataToFile():
                
                global debug, frame_, rawDataTable, rawFooterTable, headingNames, csvfilename

                if debug: print "In ", inspect.currentframe().f_code.co_name, "()"     

                dataline=None
                datalines=[]

                rawDataTable=sorted(rawDataTable,key=getKey)
                rawDataTable.insert(0,headingNames) # Insert Column Headings at top of list. A bit rough and ready, not great coding, but a short list...! 
                for i in range(0,len(rawFooterTable)):
                    rawDataTable.append(rawFooterTable[i])

                for i in range(0,len(rawDataTable)):
                    if debug: print [i], rawDataTable[i]
                    #         f1 f2 f3 f4 f5 f6 f7 f8   
                    dataline='%s,%s,%s,%s,%s,%s,%s,%s\n' %(
                        fixFormatsStr(rawDataTable[i][0],False),
                        fixFormatsStr(rawDataTable[i][1],False),
                        fixFormatsStr(rawDataTable[i][2],True),
                        fixFormatsStr(rawDataTable[i][3],True),
                        fixFormatsStr(rawDataTable[i][4],False),
                        fixFormatsStr(rawDataTable[i][5],True),
                        fixFormatsStr(rawDataTable[i][6],True),
                        fixFormatsStr(rawDataTable[i][7],False)
                    )
                    datalines.append(dataline)

                # Write the csvlines to a file
                if debug: print "Opening file and writing ",len(rawDataTable),"records"
                f=open(csvfilename,"w")
                for output in datalines: f.write(output)
                f.close()
                print 'CSV file '+csvfilename+' created, records written, and file closed..'
            #enddef

            def getKey(item):
                return item[0]

            def fixFormatsStr(theString,lRemoveSpacesToo):
                global lStripASCII

                if lRemoveSpacesToo==None: lRemoveSpacesToo=False
                if theString==None: theString=""

                theString=theString.strip()                     # remove leading and trailing spaces
                theString=theString.replace(","," ")        	# remove commas to keep csv format happy
                theString=theString.replace("\n","*").strip()  	#remove newlines to keep csv format happy
                if lRemoveSpacesToo:
                    theString=theString.replace(" ","")        	# remove spaces to keep csv number formats happy
                if lStripASCII:
                    all_ASCII = ''.join(char for char in theString if ord(char) < 128)
                else:
                    all_ASCII = theString
                return( all_ASCII )

            #enddef
            
            ExportDataToFile()

    else:
        pass



    # Some cleanup of large / important objects....
    try:
        if debug: print "deleting old objects"
        if "frame_" in vars()               or "frame_" in globals():               del frame_
        if "JTextFieldLimitYN" in vars()    or "JTextFieldLimitYN" in globals():    del JTextFieldLimitYN
        if "userFilters" in vars()          or "userFilters" in globals():          del userFilters
        if "rawDataTable" in vars()         or "rawDataTable" in globals():         del rawDataTable
        if "rawrawFooterTable" in vars()    or "rawrawFooterTable" in globals():    del rawrawFooterTable

    except:
        if debug: print "Objects did not exist.."

else:
    # Otherwise version error - ending
    pass

    
    

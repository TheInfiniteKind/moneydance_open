# !/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Inspired by:
# https://infinitekind.tenderapp.com/discussions/moneydance-development/7713-how-to-createupdate-an-investment-transaction
# https://infinitekind.tenderapp.com/discussions/moneydance-development/10510-python-create-investment-transaction
# updated by Stuart Beesley December 2025 thru July 2026

# ######################################################################################################################
# MIT License
#
# Copyright (c) 2025-2026 @mmd and Infinite Kind
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


global moneydance, moneydance_ui, moneydance_data, moneydance_extension_parameter, moneydance_extension_loader, moneydance_this_fm
global moneydance_script_fixed_parameter, moneydance_action_context, moneydance_action_event

if "moneydance" in globals(): MD_REF = moneydance  # Make own copy of reference as MD removes it once main thread ends.. Don't use/hold on to _data variable
if "MD_REF" not in globals(): raise Exception("ERROR: 'moneydance' / 'MD_REF' NOT set!?")

from java.lang import System


import sys
import traceback
import csv
import ast
import json
from datetime import datetime

from java.awt import FileDialog
from javax.swing import SwingUtilities, JOptionPane
from javax.swing.filechooser import FileFilter
from java.io import File, FilenameFilter

from com.infinitekind.moneydance.model import ParentTxn, AbstractTxn, InvestTxnType, InvestFields, AccountUtil, TxnSearch, Account, AcctFilter
from com.moneydance.apps.md.controller import UserPreferences

if MD_REF.getBuild() >= 5100: from com.infinitekind.util import AppDebug                                                # noqa
if MD_REF.getBuild() >= 4097: from com.infinitekind.util import DateUtil

# NOTE - only put variables here that do not lock on to MD internals.. Ideally move all inside doMain()
useStuartsKey = 0

class QuickAbortThisScriptException(Exception): pass      # This is a way to quickly exit the script

#####################################################
class FileExtensionFilter(FileFilter, FilenameFilter):

    def __init__(self, acceptableExtensions, defaultExtension=None):
        self.extensions = []
        if defaultExtension is not None:
            self.defaultExtension = defaultExtension.lstrip('.').lower()
        else:
            self.defaultExtension = None

        for ext in acceptableExtensions:
            if ext is None: continue
            cleanExt = ext.lower()
            while cleanExt.startswith('.'):
                cleanExt = cleanExt[1:]
            if cleanExt and cleanExt not in self.extensions:
                self.extensions.append(cleanExt)

    # FilenameFilter
    def accept(self, dirOrFile, name=None):
        if name is None:
            f = dirOrFile
            return self.accept(f.getParentFile() or File("."), f.getName())

        dotIdx = name.rfind('.')
        if dotIdx <= 0: return False

        ext = name[dotIdx + 1:].lower()
        return ext in self.extensions

    def getDescription(self): return "Import Files"
#####################################################

def txnKey(row):
    if (useStuartsKey):
        if 'Amount' in row:
            rowAmount = row['Amount']
        elif 'Amount ($)' in row:
            rowAmount = row['Amount ($)']
        else:
            rowAmount = "?"
        
        key = "%s|%s|%s|%s|%s|%s|%s" % (
            row.get('Run Date') or row.get('Date'),
            row.get('Account',''),
            row.get('Action',''),
            rowAmount,
            row.get('Symbol',''),
            row.get('Quantity',''),
            row.get('Unique',''))
        return key
    else:
        return json.dumps(row, sort_keys=True, separators=(',', ':'))

def uniqueTime():
    if MD_REF.getBuild() >= 4097:
        return DateUtil.getUniqueCurrentTimeMillis()
    else:
        return System.currentTimeMillis()

def myPrint(msg):
    print("%s" %(msg))
#    MD_REF.getUI().setStatus(msg, -1.0)
    System.err.println("%s" %(msg))

def parseAmount(s):
    if s is None: return 0.0
    if not s: return 0.0
    return float(s)

def getSecurityAcct(investAcct, securityName, tickerSymbol):
    for secAcct in investAcct.getSubAccounts():
        if secAcct.getAccountType() != Account.AccountType.SECURITY: continue
        if securityName and secAcct.getCurrencyType().getName() == securityName:
            return secAcct
        if tickerSymbol and secAcct.getCurrencyType().getTickerSymbol().strip().lower() == tickerSymbol.strip().lower():
            return secAcct
    return None

def dump():
    tb = traceback.format_exc()
    trace = traceback.format_stack()
    theText =  ".\n" \
               "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n" \
               "@@@@@ Unexpected error caught!\n".upper()
    theText += tb
    for trace_line in trace: theText += trace_line
    theText += "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
    myPrint(theText)


def doMain():
    # initialise these here so that their scope is local to doMain - i.e. they will evaporate once doMain completes
    global MD_REF
    mdGUI = MD_REF.getUI()
    book = MD_REF.getCurrentAccountBook()
    root = MD_REF.getCurrentAccount()
    strings = mdGUI.getStrings()
    prefs = MD_REF.getPreferences()

    # define locally scoped variables here...
    csvFileName = None
    # csvFileName = '/Users/username/Downloads/fidelity.csv'
    accountNamePrefix = 'Fidelity '
    debug = 0
    online = 1
    MY_IMPORT_DIR_KEY = "custom_fidelity_import_dir"

    FIID = 'script:import_fidelity.py'
    protocolId = 100 # change to 100
    oldProtocolId = 99

    buyStrings = [' BOUGHT ', 'REINVESTMENT ', 'Contributions', 'PURCHASE ']
    buyXferStrings = [ 'TRANSFER OF ASSETS ACAT RECEIVE', 'TRANSFERRED TO' ]
    sellStrings = ['REDEMPTION ', 'SOLD ', 'IN LIEU OF FRX SHARE']
    sellXferStrings = [ 'TRANSFER OF ASSETS ACAT DELIVER', 'TRANSFERRED FROM' ]
    divStrings = ['DIVIDEND RECEIVED ', 'REGULATORY FEE ADJ', 'INTEREST', 'EXEMPT INT' ]
    divReinvestStrings = ['Dividend']
    incStrings = ['LONG-TERM', 'SHORT-TERM']
    miscExpStrings = ['FEE CHARGED', 'TAX PAID']

    importantMessages = ''

    try:

        if csvFileName is None:

            fwin = mdGUI.getFileChooser(None, strings.choose_import_file + " (CSV, TSV, TXT)", FileDialog.LOAD,
                                  FileExtensionFilter(["csv", "tsv", "txt"]), [MY_IMPORT_DIR_KEY, UserPreferences.IMPORT_DIR, UserPreferences.DATA_DIR])
            fwin.setVisible(True)
            fileName = fwin.getFile()
            dirName = fwin.getDirectory()

            if (fileName is None or dirName is None):
                raise QuickAbortThisScriptException

            prefs.setSetting(MY_IMPORT_DIR_KEY, dirName)
            
            fileToImport = File(dirName, fileName)
            myPrint("File selected: %s" %(fileToImport))
            if (not fileToImport.exists() or not fileToImport.canRead()):
                msg = strings.unable_to_read_file + ": " + fileToImport.getAbsolutePath()
                myPrint(msg)
                mdGUI.showErrorMessage(msg)
                raise QuickAbortThisScriptException
            csvFileName = fileToImport.getAbsolutePath()

        with open(csvFileName, 'rb') as csvFile:        # correct approach for python 2.7 - unicode strings...

            # strip out BOM (if it exists)
            first = csvFile.read(3)
            if first != '\xef\xbb\xbf': csvFile.seek(0)

            reader = csv.reader(csvFile)
            firstRow = next(reader)

            try:
                while not any(firstRow): firstRow = next(reader)
            except:
                mdGUI.showErrorMessage("ERROR reading csv file")
                raise

            dict_reader = csv.DictReader(csvFile, fieldnames=firstRow)

            countDuplicates = 0
            if (online):
                # Remove entries already in Moneydance
                new_dict = {}
                for row in dict_reader:
                    if txnKey(row) in new_dict:
                        # Duplicate entry in CSV file
                        row['Unique']=str(uniqueTime())
                    new_dict[txnKey(row)] = row

                class IsMatch(TxnSearch):
                    def matchesAll(self):
                        return False

                    def matches(self, txn):
                        if isinstance(txn, ParentTxn):
                            newTxnId = None
                            oldTxnId = txn.getFiTxnId(oldProtocolId)
                            if (oldTxnId):
                                try:
                                    loadedDict = ast.literal_eval(oldTxnId)
                                    newTxnId = json.dumps(loadedDict, sort_keys=True, separators=(',', ':'))
                                except ValueError as e:
                                    print("Error evaluating string: %s" %e)

                                if newTxnId:
                                    txn.setEditingMode()
                                    txn.setFiTxnId(protocolId, newTxnId)
                                    txn.setFiTxnId(oldProtocolId, None)
                                    txn.getParentTxn().syncItem()

                            newTxnId = txn.getFiTxnId(protocolId)
                            if (newTxnId):
                                if (newTxnId in new_dict):
                                   del new_dict[newTxnId]
                                   return True
                        else:
                            return False

                results = book.getTransactionSet().getTransactions(IsMatch())                                           # noqa
                countDuplicates = results.getSize()
                dict_reader = list(new_dict.values())


            # Create dicts of investment accounts by name and by number
            allAccounts = AccountUtil.allMatchesForSearch(book, AcctFilter.ALL_ACCOUNTS_FILTER)
            investAccountsByName = {}
            investAccountsByNumber = {}
            for account in allAccounts:
                if account.getAccountType() == Account.AccountType.INVESTMENT:
                    accountName = account.getAccountName().strip().lower()
                    if accountName:
                        if accountName in investAccountsByName:
                            txt = "WARN: more than one investment account with name: '%s'" %(accountName)
                            importantMessages += txt + '\n';
                            myPrint(txt)
                        else:
                            investAccountsByName[accountName] = account

                    accountNumber = account.getInvestAccountNumber().strip().lower()
                    if accountNumber:
                        if accountNumber in investAccountsByNumber:
                            txt = "WARN: more than one investment account with number: '%s'" %(accountNumber)
                            importantMessages += txt + '\n';
                            myPrint(txt)
                        else:
                            investAccountsByNumber[accountNumber] = account
                
            countCreated = 0
            accountForSingleAccountCsv = None
            for row in dict_reader:
                if ('Action' not in row):
                    if ('Transaction Type' not in row):
                        continue
                if ('Action' in row and not row['Action']):
                    continue
                if ('Transaction Type' in row and not row['Transaction Type']):
                    continue
                if (debug): myPrint(row)

                account = None
                if ('Account' not in row):
                    if (not accountForSingleAccountCsv):
                        investAccountNames = sorted(investAccountsByName.keys())
                        selection = JOptionPane.showInputDialog(
                            None,
                            "Select an investment account:",
                            "Investment Account Selection Dialog",
                            JOptionPane.QUESTION_MESSAGE,
                            None,
                            investAccountNames,
                            investAccountNames[0])

                        if selection is None:
                            continue

                        accountForSingleAccountCsv = investAccountsByName[selection]

                    account = accountForSingleAccountCsv
                    
                else:
                    accountName1 = accountNamePrefix + row['Account']
                    accountName1 = accountName1.strip().lower()
                    if (accountName1 in investAccountsByName):
                        account = investAccountsByName[accountName1]
                    else:
                        accountName2 = row['Account'].strip().lower()
                        if (accountName2 in investAccountsByName):
                            account = investAccountsByName[accountName2]
                        else:
                            accountNumber = row.get('Account Number', '').strip().lower()
                            if (accountNumber and accountNumber in investAccountsByNumber):
                                account = investAccountsByNumber[accountNumber]
                            else:
                                txt = "ERROR: account: '%s' AND '%s' with number '%s' NOT found" %(accountName1, accountName2, accountNumber)
                                importantMessages += txt + '\n';
                                myPrint(txt)
                                continue

                if (account):
                    if 'Action' in row:
                        rowAction = row['Action']
                    elif 'Transaction Type' in row:
                        rowAction = row['Transaction Type']
                    else:
                        txt = "ERROR: action not found: '%s'" %(row)
                        importantMessages += txt + '\n';
                        myPrint(txt)
                        continue

                    if 'Amount' in row:
                        rowAmount = row['Amount']
                    elif 'Amount ($)' in row:
                        rowAmount = row['Amount ($)']
                    else:
                        txt = "ERROR: amount not found: '%s'" %(row)
                        importantMessages += txt + '\n';
                        myPrint(txt)
                        continue

                    if 'Run Date' in row:
                        date_string = row['Run Date']
                    elif 'Date' in row:
                        date_string = row['Date']
                    else:
                        txt = "ERROR: date not found: '%s'" %(row)
                        importantMessages += txt + '\n';
                        myPrint(txt)
                        continue

                    try:
                        format_string = "%m/%d/%Y"
                        dateDate = datetime.strptime(date_string, format_string).date()
                    except ValueError:
                        format_string = "%m-%d-%Y"
                        dateDate = datetime.strptime(date_string, format_string).date()

                    dateString = dateDate.strftime('%Y%m%d')
                    date = int(dateString)

                    desc = rowAction
                    memo = rowAction
                    niceCheckNum = ""

                    pTxn = ParentTxn.makeParentTxn(
                        book,
                        date,
                        date,
                        uniqueTime(),
                        niceCheckNum,
                        account,
                        desc,
                        memo,
                        -1L,
                        AbstractTxn.ClearedStatus.UNRECONCILED.legacyValue())                                           # noqa

                    fields = InvestFields()
                    action = rowAction
                    if any(substring in action for substring in buyStrings):
                        txnType = InvestTxnType.BUY
                    elif any(substring in action for substring in buyXferStrings):
                        txnType = InvestTxnType.BUY_XFER
                    elif any(substring in action for substring in sellStrings):
                        txnType = InvestTxnType.SELL
                    elif any(substring in action for substring in sellXferStrings):
                        txnType = InvestTxnType.SELL_XFER
                    elif any(substring in action for substring in divStrings):
                        txnType = InvestTxnType.DIVIDEND
                    elif any(substring in action for substring in divReinvestStrings):
                        txnType = InvestTxnType.DIVIDEND_REINVEST
                    elif any(substring in action for substring in incStrings):
                        txnType = InvestTxnType.MISCINC
                    elif any(substring in action for substring in miscExpStrings):
                        txnType = InvestTxnType.MISCEXP
                    else:
                        symbol = row.get('Symbol', '').strip()
                        if (symbol):
                            txt = "ERROR: unknown action: '%s' . Will record as Xfr" %(action)
                            importantMessages += txt + '\n';
                            myPrint(txt)
                        txnType = InvestTxnType.BANK

                    if (txnType in [InvestTxnType.BUY, InvestTxnType.SELL, InvestTxnType.DIVIDEND, InvestTxnType.BUY_XFER, InvestTxnType.SELL_XFER, InvestTxnType.MISCINC, InvestTxnType.DIVIDEND_REINVEST, InvestTxnType.MISCEXP]):
                        if 'Description' in row:
                            csvDescription = row['Description']
                        elif 'Transaction Type' in row:
                            # note: this is a workaround for someone's csv export (401k / 403b) in Fidelity which switches some fields around
                            csvDescription = row['Investment']
                        else:
                            txt = "ERROR: description not found: '%s'" %(row)
                            importantMessages += txt + '\n';
                            myPrint(txt)
                            continue

                        if 'Symbol' in row:
                            symbol = row['Symbol']
                        else:
                            symbol = '' # not present in retirement account CSV files 

                        securityAccount = getSecurityAcct(account, csvDescription, symbol)
                        if (not securityAccount):
                            if (csvDescription != "No Description"):
                                txt = "ERROR: security account: '%s' '%s' NOT found when processing invest account '%s.' Please manually create security and/or add it to the invest account. Will process as Xfr" %(csvDescription, symbol, account.getAccountName())
                                importantMessages += txt + '\n';
                                myPrint(txt)
                                
                            txnType = InvestTxnType.BANK
                        else:
                            security = securityAccount.getCurrencyType()
                            if (not security):
                                txt = "ERROR: security: '%s' '%s' NOT found. Will process as Xfr" %(csvDescription, symbol)
                                importantMessages += txt + '\n';
                                myPrint(txt)
                                txnType = InvestTxnType.BANK
                            else:
                                fields.setFieldStatus(txnType, pTxn)
                                fields.security = securityAccount
                                fields.amount = fields.curr.getLongValue(abs(parseAmount(rowAmount)))

                                if (txnType == InvestTxnType.DIVIDEND or txnType == InvestTxnType.MISCINC or txnType == InvestTxnType.MISCEXP):
                                    fields.shares = 0
                                    fields.price = 1
                                else:
                                    totalAmount = abs(parseAmount(rowAmount))

                                    if 'Quantity' in row:
                                        rowQuantity = row['Quantity']
                                    elif 'Shares/Unit' in row:
                                        rowQuantity = row['Shares/Unit']
                                    else:
                                        txt = "ERROR: quantity not found: '%s'" %(row)
                                        importantMessages += txt + '\n';
                                        myPrint(txt)
                                        continue

                                    shares = abs(parseAmount(rowQuantity))

                                    # Fix for Fidelity bug in 401k where quantity is listed in Price column
                                    if (shares == 0.0):
                                        if 'Price' in row:
                                            rowQuantity = row['Price']
                                            shares = abs(parseAmount(rowQuantity))
                                        elif 'Price ($)' in row:
                                            rowQuantity = row['Price ($)']
                                            shares = abs(parseAmount(rowQuantity))

                                    price = 1.0 if (totalAmount == 0.0 or shares == 0.0) else totalAmount/shares

                                    fields.shares = securityAccount.getCurrencyType().getLongValue(shares)
                                    fields.price = price

                    if (txnType == InvestTxnType.BANK):
                        fields.setFieldStatus(txnType, pTxn)
                        fields.amount = fields.curr.getLongValue(parseAmount(rowAmount))

                    fields.date = date
                    fields.taxDate = date
                    fields.checkNum = niceCheckNum
                    fields.payee = desc
                    fields.memo = memo

                    fields.xfrAcct = AccountUtil.getDefaultTransferAcct(account)
                    fields.fee = 0
                    if MD_REF.getBuild() >= 5202:
                        fields.feeAcct = AccountUtil.getDefaultFeeCategoryForAcct(account)                              # noqa
                    else:
                        fields.feeAcct = AccountUtil.getDefaultCategoryForAcct(account)
                    fields.category = AccountUtil.getDefaultCategoryForAcct(account)
                    fields.storeFields(pTxn)
                    pTxn.setIsNew(1)
                    if (online):
                        pTxn.setFIID(FIID)
                        pTxn.setFiTxnId(protocolId, txnKey(row)) 
                        pTxn.setParameter("ol.orig-payee", desc)
                        pTxn.setParameter("ol.orig-memo", memo)
                    pTxn.syncItem()
                    countCreated += 1
                    if (debug): myPrint("stored fields %s as txn %s" %(fields, pTxn))

        if (countDuplicates):
            msg = "Created %s transactions\nIgnored %s duplicate transactions" %(countCreated, countDuplicates)
        else:
            msg = "Created %s transactions" %(countCreated)
        if (importantMessages):
            msg += '\n\n' + importantMessages + ' '; # + ' ' needed to not skip last word of message
        myPrint(msg)
        mdGUI.showInfoMessage(msg)

    except QuickAbortThisScriptException: pass
    except:
        e_type, exc_value, exc_traceback = sys.exc_info()
        txt = "Error detected whilst running script: '%s'" %(exc_value)
        myPrint(txt)
        dump()
        mdGUI.showErrorMessage(txt + " (review console)")

    finally:
        # nuke moneydance references that can prevent garbage collection...
        del mdGUI
        del book
        del root
        del strings
        del prefs
        del MD_REF


SwingUtilities.invokeLater(doMain)

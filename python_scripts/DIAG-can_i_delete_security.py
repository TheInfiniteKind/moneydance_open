#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# DIAG-can_i_delete_security.py v2 - October 2020 - Stuart Beesley StuWareSoftSystems
# Analyses selected Security and tells you whether you can delete it, or where it's used..
# This script does not change any data!
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
# V1 - Initial release
# V2 - Cosmetic changes....

import sys
reload(sys)  # Dirty hack to eliminate UTF-8 coding errors
sys.setdefaultencoding('utf8')  # Dirty hack to eliminate UTF-8 coding errors. Without this str() fails on unicode strings...

from com.infinitekind.moneydance.model import *
from com.infinitekind.moneydance.model import AccountUtil
from com.infinitekind.moneydance.model import AcctFilter
from com.infinitekind.moneydance.model import CurrencyType
from com.infinitekind.moneydance.model.Account import AccountType

from javax.swing import JOptionPane

import os.path
from java.lang import System

global debug  # Set to True if you want verbose messages, else set to False....
global version

version = "2"
debug = True

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

def MDDiag():
    global debug
    if debug: print "MoneyDance Build:", moneydance.getVersion(), "Build:", moneydance.getBuild()

MDDiag()

print "\nScript running to analyse whether you can delete a Security, or show where it's used...."
print "-------------------------------------------------------------------"
if moneydance_data is None:
    print "no data to scan - aborting"
    raise Exception("MD Data file is empty - no data to scan - aborting...")

usageCount = 0
countPriceHistory = 0
sumShares = 0

while True:

    if moneydance_data is None:
        print "no data to scan - aborting"
        break

    root = moneydance.getRootAccount()
    book = moneydance.getCurrentAccountBook()
    allCurrencies = book.getCurrencies().getAllCurrencies()

    securities = []

    for currency in allCurrencies:
        if currency.getCurrencyType() == CurrencyType.Type.SECURITY:
            securities.append(currency)

    securities = sorted( securities, key=lambda x: (x.getName().upper()))

    baseCurr = moneydance_data.getCurrencies().getBaseType()

    selectedSecurity = JOptionPane.showInputDialog(None,
                                                   "Select Security", "Select the security to analyse",
                                                   JOptionPane.INFORMATION_MESSAGE,
                                                   None,
                                                   securities,
                                                   None)
    if selectedSecurity is None:
        print "No security was selected; exiting"
        break

    print "\nYou want me to look for Security: %s\n" % selectedSecurity
    class myAcctFilter(AcctFilter):

        def __init__(self, selectAccountType):
            self.selectAccountType = selectAccountType

        def matches(self, acct):
            if acct.getAccountType() == self.selectAccountType:
                return True
            else:
                return False
    # endclass

    accountsList = AccountUtil.allMatchesForSearch(book, myAcctFilter(AccountType.SECURITY))
    print "Searching through %s security (sub) accounts.." % (len(accountsList))

    for account in accountsList:
        if account.getCurrencyType() == selectedSecurity:
            print "   >> Security: %s is used in Account: %s - Share holding balance: %s" \
                  % (selectedSecurity, account.getParentAccount().getAccountName(), selectedSecurity.getDoubleValue(account.getBalance()))
            sumShares += selectedSecurity.getDoubleValue(account.getBalance())
            usageCount += 1

    if not usageCount:
        print "   >> Security not found in any accounts."

    print "\nChecking security for price history...:"

    secSnapshots = selectedSecurity.getSnapshots()
    countPriceHistory = secSnapshots.size()
    if countPriceHistory > 0:
        print("   >> Security has %s historical prices!" % (secSnapshots.size()))
    else:
        print("   >> Security has no historical prices. ")


    print "-----------------------------------------------------------------"
    if usageCount:
        print "\nUSAGE FOUND: You are using security: %s in %s accounts!\n... with a share balance of: %s. These would need to be removed before security deletion" \
            % (selectedSecurity, usageCount, sumShares)
        myPrint("J", "StuWareSoftSystems - ", os.path.basename(__file__), ">> NO - Security cannot be deleted as it's being used:"+str(selectedSecurity))

    if countPriceHistory:
        print "\nPRICE HISTORY FOUND: You have %s price records - If you delete Security then these will be lost. Is that OK with you?  " \
              % (countPriceHistory)

    if not usageCount and not countPriceHistory:
        print "\nNo usage of security %s found! You should be able to safely delete the Security" % selectedSecurity


    break
# ENDWHILE

print
myPrint("B", "StuWareSoftSystems - ", os.path.basename(__file__), " script ending......")
print

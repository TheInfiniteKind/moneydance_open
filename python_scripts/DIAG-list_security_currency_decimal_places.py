#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# DIAG-list_security_currency_decimal_places.py v1 - November 2020 - Stuart Beesley StuWareSoftSystems
# Lists the  decimal places configured in your Moneydance securities. This script does not change any data!
# -- NOTE - This setting is hidden in Moneydance and fixed once set (as data is stored scaled * 10*dpc)
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

import sys
reload(sys)  # Dirty hack to eliminate UTF-8 coding errors
sys.setdefaultencoding('utf8')  # Dirty hack to eliminate UTF-8 coding errors. Without this str() fails on unicode strings...

import os.path
from java.lang import System

from com.infinitekind.moneydance.model import CurrencyUtil

global debug  # Set to True if you want verbose messages, else set to False....
global version

version = "1"
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

print "Script is analysing your Security decimal place settings...."
print "-------------------------------------------------------------------"
if moneydance_data is None:
	print "no data to scan - aborting"
	raise Exception("MD Data file is empty - no data to scan - aborting...")

iWarnings = 0
mylen=20

decimalPoint_MD = moneydance_ui.getPreferences().getSetting("decimal_character", ".")

currs = moneydance_data.getCurrencies().getAllCurrencies()
baseCurr = moneydance_data.getCurrencies().getBaseType()

currs = sorted(currs, key=lambda x: str(x.getName()).upper())

def analyse_curr( theCurr, theType ):
	iWarn = 0
	for sec_curr in theCurr:
		if str(sec_curr.getCurrencyType()) != theType: continue

		foo = str(CurrencyUtil.getUserRate(sec_curr, sec_curr.getRelativeCurrency()))
		priceDecimals = max(sec_curr.getDecimalPlaces(), min(6, len(foo.split(decimalPoint_MD)[-1])))
		print str(sec_curr).ljust(mylen)[:mylen], "\tDPC:",\
			sec_curr.getDecimalPlaces(),\
			"\t", \
			"Relative to:", sec_curr.getRelativeCurrency(), "\t",\
			"Current rate:", foo,\
			"\tRate dpc:", priceDecimals,
		if sec_curr.getDecimalPlaces() < priceDecimals and theType == "SECURITY":
			iWarn += 1
			print " ***"
		else:
			print ""
	return iWarn

print "=============="
print "--- SECURITIES ----"
print "=============="

iWarnings+=analyse_curr(currs, "SECURITY")

print "=============="
print "--- CURRENCIES ----"
print "=============="
iWarnings+=analyse_curr(currs, "CURRENCY")


print "-----------------------------------------------------------------"
if iWarnings:
	print "\nYou have %s Warning(s).." % iWarnings
	print "These are where your security decimal place settings seem less than 4 or not equal to price history dpc; This might be OK - depends on your setup"
	print "NOTE: It's quite hard to determine the stored dpc, so use this as guidance only, not definitive!"
	print "NOTE: - This setting is fixed. The only resolution is to create a new security and alter your txns to use the new security..."
	print "DISCLAIMER: Always backup your data before changing your data. I can take no responsibility for any changes...."
else:
	print "\nAll good, decimal places look clean! Congratulations!"

print
myPrint("B", "StuWareSoftSystems - ", os.path.basename(__file__), " script ending......")
print


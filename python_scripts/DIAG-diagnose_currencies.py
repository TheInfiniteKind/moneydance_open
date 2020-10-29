#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# DIAG-diagnose_currencies.py v1 - October 2020 - Stuart Beesley StuWareSoftSystems (based on Moneydance support script)
# Diagnoses your Moneydance currencies. This script does not change any data!
# -- especially where base rate is not 1, or base relative rate is not 1, and/or has price history
# -- a script fix is available, but should be requested via support (any fix can of course damage your data - so backup first)
# -- Request 'reset_relative_currencies.py'
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

from com.infinitekind.moneydance.model import *
from com.infinitekind.util import *

from com.infinitekind.moneydance.model import CurrencyType

global lNeedFixScript, lWarning, iWarnings

lWarning = False
lNeedFixScript = False
iWarnings = 0

print "\nDIAG-diagnose_currencies.py running to diagnose your currencies...."
print "-------------------------------------------------------------------"
if moneydance_data is None:
    print "no data to scan - aborting"
    raise Exception("MD Data file is empty - no data to scan - aborting...")
    

def reset_relative_currencies():
    global lNeedFixScript, lWarning, iWarnings

    currencies = moneydance_data.getCurrencies()
    baseCurr = currencies.getBaseType()

    print "Analysing the Base currency setup...."
    print "Base currency: %s" % baseCurr

    if not baseCurr.getDoubleParameter("rrate", 1.0) == 1.0:
        print("ERROR - base currency has non-identity relative rate (rrate): "+baseCurr.getParameter("rrate", "null"))
        lNeedFixScript = True

    if not baseCurr.getDoubleParameter("rate", 1.0) == 1.0:
        print("ERROR - base currency has non-identity rate: "+baseCurr.getParameter("rate", "null"))
        lNeedFixScript = True

    if not lNeedFixScript:
        print "Base currency has Rate (rate) of: %s and Relative Rate (rrate): of %s.  This is Correct..." \
              % (baseCurr.getParameter("rate", "null"), baseCurr.getParameter("rrate", "null"))

    baseSnapshots = baseCurr.getSnapshots()
    if baseSnapshots.size() > 0:
        lNeedFixScript = True
        print("ERROR: base currency has %s historical prices! These need to be deleted!" % (baseSnapshots.size()))
        for baseSnapshot in baseSnapshots:
            print("  snapshot: %s" % baseSnapshot)
    else:
        print("Base currency has no historical prices. This is correct")

    root = moneydance_data.getRootAccount()
    if root.getCurrencyType() != baseCurr:
        lNeedFixScript = True
        print "ERROR - The root account's currency is not set to base! This needs correcting!"
        print "Root account's currency: %s, Base currency: %s" % (root.getCurrencyType(), baseCurr)
    else:
        print "Good, the root account's currency is set to the base currency! Root: %s, Base: %s" % (root.getCurrencyType(), baseCurr)

    lWarning = False
    print "\nAnalysing the currency table..."
    for curr in currencies:
        if curr.getCurrencyType() == CurrencyType.Type.SECURITY:
            continue
        print("\nChecking currency: %s" % curr)
        print "relative_to_currid:", curr.getParameter("relative_to_currid")
        if curr.getParameter("relative_to_currid") is not None and curr.getParameter("relative_to_currid") != baseCurr.getParameter("currid"):
            lWarning = True
            iWarnings += 1
            print "WARNING: relative_to_currid should be set to None or your base currency (perhaps)?"
        print "Rate: %s (inversed: %s)" % (curr.getParameter("rate", "null"), 1/float(curr.getParameter("rate", "null")))
        if curr.getParameter("rrate", None) is not None:
            print "Relative Rate: %s (inversed: %s)" % (curr.getParameter("rrate", None), 1/float(curr.getParameter("rrate", None)))

        print("  details: %s" % (curr.getSyncInfo().toMultilineHumanReadableString()))

        print "  pricing history:"
        currSnapshots = curr.getSnapshots()
        if currSnapshots.size() > 0:
            i = 0
            for currSnapshot in reversed(currSnapshots):
                i += 1
                print("  snapshot: %s (reversed: %s)" % (currSnapshot, currSnapshot.getRate()))
                if i > 5:
                    print "  stopping after 5 price history records, but more does exist..."
                    break
        else:
            if curr != baseCurr:
                print("  This currency has no historical prices? Is this correct?")
            else:
                print "  This currency has no historical prices..."
    return


reset_relative_currencies()

print "-----------------------------------------------------------------"
if lNeedFixScript:
    print "\nERROR: You have currency errors.. "
    print "Please discuss details with support and potentially request script: reset_relative_currencies.py from support "
    print "DISCLAIMER: Always backup your data before running change scripts. I can take no responsibility for the execution of said script"
elif lWarning:
    print "\nYou have %s Warning(s).." % iWarnings
    print "These are where your currency records show a relative currency that's not None or the base currency...; This might be OK - depends on your setup"
    print "Only if you are seeing currency problems, then discuss with support and potentially request script: reset_relative_currencies.py from support "
    print "This would reset your relative currency back to None..."
    print "DISCLAIMER: Always backup your data before running change scripts. I can take no responsibility for the execution of said script"
else:
    print "\nAll good, currencies look clean! Congratulations!"

print "\n\n---------------------------------------------- End of StuWareSoftSystems script --------\n\n"

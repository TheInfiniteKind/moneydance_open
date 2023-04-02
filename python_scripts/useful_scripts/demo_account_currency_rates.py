#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# demo_account_currency_rates.py - Build: 2

# A basic demo Python (Jython) script to get you started - Stuart Beesley - StuWareSoftSystems - Jan 2021
# Allows user to select an account, select a date, select a currency
# script will get the Account's balance for that date, and convert to base currency, the relative currency, and selected currency

global moneydance, moneydance_data, moneydance_ui

if float(moneydance.getBuild()) < 1904:     # Check for builds less than 1904 / version < 2019.4
    try:
        moneydance.getUI().showInfoMessage("SORRY YOUR VERSION IS TOO OLD FOR THESE SCRIPTS")
    except:
        pass
    raise Exception("SORRY YOUR VERSION IS TOO OLD FOR THESE SCRIPTS")


import sys
reload(sys)  # Dirty hack to eliminate UTF-8 coding errors
sys.setdefaultencoding('utf8')  # Dirty hack to eliminate UTF-8 coding errors. Without this str() fails on unicode strings...

from com.infinitekind.moneydance.model import *
from com.infinitekind.moneydance.model import Account, AccountUtil, AcctFilter, CurrencyType
from com.infinitekind.util import DateUtil, CustomDateFormat
from com.moneydance.awt import JDateField
from java.awt import GridLayout
from javax.swing import JLabel, JPanel, JOptionPane

# noinspection PyUnresolvedReferences
class MyAcctFilter(AcctFilter):

    def __init__(self):
        pass

    @staticmethod
    def matches(theAcct):

        if not (theAcct.getAccountType() == Account.AccountType.BANK
                or theAcct.getAccountType() == Account.AccountType.CREDIT_CARD
                or theAcct.getAccountType() == Account.AccountType.INVESTMENT):
            return False

        if (theAcct.getAccountOrParentIsInactive()): return False
        if (theAcct.getHideOnHomePage() and theAcct.getBalance() == 0): return False

        return True


accountsList = AccountUtil.allMatchesForSearch(moneydance_data, MyAcctFilter())
accountsList = sorted(accountsList, key=lambda sort_x: (sort_x.getFullAccountName().upper()))

acct = JOptionPane.showInputDialog(None,
                                         "Select Acct",
                                         "ACCOUNT LIST",
                                         JOptionPane.INFORMATION_MESSAGE,
                                         moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                         accountsList,
                                         None)      # type: Account

if not acct: raise Exception("ERROR")

get_a_date = JLabel("enter a date (enter as yyyy/mm/dd):")
user_selectDateStart = JDateField(CustomDateFormat("ymd"),15)   # Use MD API function (not std Python)
user_selectDateStart.setDateInt(DateUtil.getStrippedDateInt())

datePanel = JPanel(GridLayout(0, 1))
datePanel.add(get_a_date)
datePanel.add(user_selectDateStart)
options = ["Cancel", "OK"]

userAction = JOptionPane.showOptionDialog(None,
                                          datePanel,
                                          "Select a Date for balance:",
                                          JOptionPane.OK_CANCEL_OPTION,
                                          JOptionPane.QUESTION_MESSAGE,
                                          None,
                                          options,
                                          options[0])  # type: int

if userAction != 1: raise Exception("No date entered")
theDate = user_selectDateStart.getDateInt()

allCurrs=[]
currencies = moneydance_data.getCurrencies().getAllCurrencies()
for curr in currencies:
    if curr.getCurrencyType() != CurrencyType.Type.CURRENCY: continue                                  # noqa
    allCurrs.append(curr)
selectedCurr = JOptionPane.showInputDialog(None,
                                           "Select Currency",
                                           "CURRENCY LIST",
                                           JOptionPane.INFORMATION_MESSAGE,
                                           moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                           allCurrs,
                                           None)      # type: CurrencyType

if not selectedCurr: raise Exception("ERROR no currency selected")


# noinspection PyUnresolvedReferences
acct_ct = acct.getCurrencyType()

balanceRaw = AccountUtil.getBalanceAsOfDate(moneydance_data, acct, theDate)
balance_as_decimal = acct_ct.getDoubleValue(balanceRaw)

print "Acct", acct, "Balances:", balanceRaw, balance_as_decimal, acct_ct.formatSemiFancy(balanceRaw,".")
print

base = moneydance_data.getCurrencies().getBaseType()
print "Base is: %s" %base
print

rateToBase = 1/acct_ct.getRate(None, user_selectDateStart.getDateInt())
print "rate to base on", theDate, "=", rateToBase
print "%s Balances:" %base, balanceRaw/rateToBase, balance_as_decimal/rateToBase
print

acct_relative = acct_ct.getRelativeCurrency()
rate_to_acct_rel = 1/acct_ct.getRate(acct_relative, user_selectDateStart.getDateInt())
print "Relative currency = ", acct_relative
print "rate to %s on" %acct_relative, theDate, "=", rate_to_acct_rel
print "%s Balances:" %acct_relative, balanceRaw/rate_to_acct_rel, balance_as_decimal/rate_to_acct_rel
print

rate_to_selected = 1/acct_ct.getRate(selectedCurr, user_selectDateStart.getDateInt())
print "Selected currency = ", selectedCurr
print "rate to %s on" %selectedCurr, theDate, "=", rate_to_selected
print "%s Balances:" %selectedCurr, balanceRaw/rate_to_selected, balance_as_decimal/rate_to_selected
print

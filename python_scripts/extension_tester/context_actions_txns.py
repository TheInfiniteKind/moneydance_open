#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# You would only use/need this script if using script_info {"type" = "txn_menu", "name" = "xxx", "script_file" = "context_actions_txns.py"}
# This gets called when you right-click on selected transactions in Moneydance...
# If you are using the ExtensionClass() method and an initializer, then you do not need this file...

global moneydance, moneydance_ui, moneydance_data
global MY_EXTENSION_OBJ, myPrint

global moneydance_script_fixed_parameter, moneydance_action_context, moneydance_action_event

myPrint(u"@@ Extension Tester >> context_actions_txns.py was invoked.")
myPrint(u"  moneydance:                         %s" %(moneydance))
myPrint(u"  moneydance_ui:                      %s" %(moneydance_ui))
myPrint(u"  moneydance_data:                    %s" %(moneydance_data))

myPrint(u"  moneydance_script_fixed_parameter: '%s'" %(moneydance_script_fixed_parameter))
myPrint(u"  moneydance_action_context:         '%s'" %(moneydance_action_context))
myPrint(u"  moneydance_action_event:           '%s'" %(moneydance_action_event))

myPrint(u"::getActionsForContext(%s)" %(moneydance_action_context))
myPrint(u"  type:         %s" %moneydance_action_context.getType())
myPrint(u"  component:    %s" %moneydance_action_context.getComponent())
myPrint(u"  dateRange:    %s" %moneydance_action_context.getDateRange())
myPrint(u"  items:        %s" %len(moneydance_action_context.getItems()))
myPrint(u"  accounts:     %s" %len(moneydance_action_context.getAccounts()))
myPrint(u"  transactions: %s" %len(moneydance_action_context.getTransactions()))

# PUT YOUR CODE HERE

# Note you should be in the same namespace as your other scripts within the same extension...
# To reference, use global on the object and then just refer to it - e.g.
global thisObjectExistsEverywhere, ExtensionTester
if u"thisObjectExistsEverywhere" in globals():
    myPrint(u"context_actions_txns.py - 'thisObjectExistsEverywhere' exists and contains: %s" %(thisObjectExistsEverywhere))

    # The next line is an example - you would not normally do this. I.e. you handle the getActionsForContext() here... This demos calling the ExtensionClass().getActionsForContext()
    #ExtensionTester.getActionsForContext(MY_EXTENSION_OBJ, moneydance_action_context)

    # from com.infinitekind.moneydance.model import CurrencyUtil
    # base = moneydance_action_context.getAppGUI().getMain().getCurrentAccountBook().getCurrencies().getBaseType()
    # acctsBal = 0.0
    # countAccts = 0
    # for acct in moneydance_action_context.getAccounts():
    #     curr = acct.getCurrencyType()
    #     acctsBal += base.getDoubleValue(CurrencyUtil.convertValue(acct.getBalance(), curr, base))
    #     countAccts += 1
    # moneydance_action_context.getAppGUI().showInfoMessage(u"Extn script - ContextMenu: %s accts - total accts bal: %s" %(countAccts, acctsBal))

    from com.infinitekind.moneydance.model import CurrencyUtil
    base = moneydance_action_context.getAppGUI().getMain().getCurrentAccountBook().getCurrencies().getBaseType()
    txnsVal = 0.0
    countTxns = 0
    for txn in moneydance_action_context.getTransactions():
        acct = txn.getAccount()
        curr = acct.getCurrencyType()
        txnsVal += base.getDoubleValue(CurrencyUtil.convertValue(txn.getValue(), curr, base))
        countTxns += 1
    bal = 0.0
    moneydance_action_context.getAppGUI().showInfoMessage("Extn script - ContextMenu: %s txns - value: %s" %(countTxns, txnsVal))


else:
    myPrint(u"context_actions_txns.py - Uh-Oh 'thisObjectExistsEverywhere' does not exist?")

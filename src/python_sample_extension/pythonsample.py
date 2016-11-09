#!/usr/bin/env python
# Python script to be run in Moneydance to perform amazing feats of financial scripting

from com.infinitekind.moneydance.model import *

import sys
import time

# get the default environment variables, set by Moneydance
print "The Moneydance app controller: %s"%(moneydance)
print "The current data set: %s"%(moneydance_data)
print "The UI: %s"%(moneydance_ui)

if moneydance_data:
  txnSet = moneydance_data.getTransactionSet()
  counter = 0
  invAcct = moneydance_data.getAccountByUUID("a4e52ab1-c16d-4274-add0-aa870f7a1405")
  baseCurr = moneydance_data.getCurrencies().getBaseType()
  invAcct.setCurrencyType(baseCurr)
  invAcct.syncItem()

class ExampleExtension:
    myContext = None
    myExtensionObject = None

    # The initialize method is called when the extension is loaded and provides the
    # extension's context.  The context implements the methods defined in the FeatureModuleContext:
    # http://infinitekind.com/dev/apidoc/com/moneydance/apps/md/controller/FeatureModuleContext.html
    def initialize(self, extension_context, extension_object):
        self.myContext = extension_context
        self.myExtensionObject = extension_object

        # here we register ourselves with a menu item to invoke a feature
        # (ignore the button and icon mentions in the docs)
        self.myContext.registerFeature(extension_object, "doSomethingCool", None, "Do Something Cool!")

    # moneydance_event_invoked is called when we receive a callback for the feature that
    # we registered in the initialize method
    def moneydance_event_invoked(self, eventString=""):
        print "Hey, we got an event! %s" % (eventString)


# setting the "moneydance_extension" variable tells Moneydance to register that object
# as an extension
moneydance_extension = ExampleExtension()

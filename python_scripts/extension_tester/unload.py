#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# You would only use/need this script if using script_info {"type" = "method", "method" = "unload", "script_file" = "unload.py"}
# This gets called when the extension is uninstalled, or is reinstalled and before the nex extension runs. You should clean up here.
# If you are using the ExtensionClass() method and an initializer, then you do NOT need this file...

global moneydance, moneydance_ui, moneydance_data, moneydance_extension_parameter, moneydance_extension_loader
global MY_EXTENSION_OBJ, MD_REF, MD_REF_UI

from java.lang import System

def myPrint(theTest):
    print(theTest)
    System.err.write(u"%s\n" %(theTest))


myPrint(u"@@ Extension Tester >> unload.py was invoked.")
myPrint(u"  moneydance: %s"%((moneydance)))
myPrint(u"  moneydance_ui: %s"%((moneydance_ui)))
myPrint(u"  moneydance_data: %s"%((moneydance_data)))
myPrint(u"  moneydance_extension_loader: %s"%((moneydance_extension_loader)))

# PUT YOUR CODE HERE

# Note you should be in the same namespace as your other scripts within the same extension...
# To reference, use global on the object and then just refer to it - e.g.
global thisObjectExistsEverywhere, ExtensionTester
if u"thisObjectExistsEverywhere" in globals():
    myPrint(u"invoke.py - 'thisObjectExistsEverywhere' exists and contains: %s" %(thisObjectExistsEverywhere))
    myPrint(u"@@@ Doing unload actions.... Ideally delete references to moneydance and especially data objects, remove listeners....")
else:
    myPrint(u"invoke.py - Uh-Oh 'thisObjectExistsEverywhere' does not exist?")

# Remove my own references... Release any references to data objects here too..!
del MD_REF, MD_REF_UI, MY_EXTENSION_OBJ

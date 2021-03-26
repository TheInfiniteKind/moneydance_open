#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# You would only use/need this script if using script_info {"type" = "method", "method" = "invoke", "script_file" = "invoke.py"}
# This gets called when moneydance.showURL() is called. It might get called when clicking on the menu item, depending on the combination of options used.
# If you are using the ExtensionClass() method and an initializer, then you do not need this file...

global moneydance, moneydance_ui, moneydance_data, moneydance_extension_parameter, moneydance_extension_loader
global MY_EXTENSION_OBJ

from java.lang import System

def myPrint(theTest):
    print(theTest)
    System.err.write(u"%s\n" %(theTest))


myPrint(u"@@ Extension Tester >> invoke.py was invoked.")
myPrint(u"  parameter: %s" %((moneydance_extension_parameter)))
myPrint(u"  moneydance: %s" %((moneydance)))
myPrint(u"  moneydance_ui: %s" %((moneydance_ui)))
myPrint(u"  moneydance_data: %s" %((moneydance_data)))
myPrint(u"  moneydance_extension_loader: %s" %((moneydance_extension_loader)))

# PUT YOUR CODE HERE

# Note you should be in the same namespace as your other scripts within the same extension...
# To reference, use global on the object and then just refer to it - e.g.
global thisObjectExistsEverywhere, ExtensionTester
if u"thisObjectExistsEverywhere" in globals():
    myPrint(u"invoke.py - 'thisObjectExistsEverywhere' exists and contains: %s" %(thisObjectExistsEverywhere))

    # The next line is an example - you would not normally do this. I.e. you handle the invoke here... This demos calling the ExtensionClass().invoke()
    ExtensionTester.invoke(MY_EXTENSION_OBJ, u"i_called_you_from_invoke.py:%s" %(moneydance_extension_parameter))
else:
    myPrint(u"invoke.py - Uh-Oh 'thisObjectExistsEverywhere' does not exist?")

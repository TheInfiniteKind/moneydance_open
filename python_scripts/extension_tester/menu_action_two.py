#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# You would only use this script if using script_info "type" = "menu" and click on the extensions menu

global moneydance, moneydance_ui, moneydance_data, moneydance_extension_parameter, moneydance_extension_loader
global MY_EXTENSION_OBJ

from java.lang import System

def myPrint(theTest):
    print(theTest)
    System.err.write(u"%s\n" %(theTest))


myPrint(u"@@ Extension Tester >> menu_action_two.py was invoked.")
myPrint(u"  moneydance: %s"%((moneydance)))
myPrint(u"  moneydance_ui: %s"%((moneydance_ui)))
myPrint(u"  moneydance_data: %s"%((moneydance_data)))
myPrint(u"  moneydance_extension_loader: %s"%((moneydance_extension_loader)))

# Note you should be in the same namespace as your other scripts within the same extension...
# To reference, use global on the object and then just refer to it - e.g.
global thisObjectExistsEverywhere, ExtensionTester
if u"thisObjectExistsEverywhere" in globals():
    myPrint(u"menu_action_two.py - 'thisObjectExistsEverywhere' exists and contains: %s" %(thisObjectExistsEverywhere))

    # The next line is an example - you would not normally do this. I.e. you handle the script code here... This demos calling the ExtensionClass().invoke()
    moneydance.showURL(u"moneydance:fmodule:extension_tester:my_invoke_command:menu_two")   # another example - you would not do this here normally
else:
    myPrint(u"menu_action_two.py - Uh-Oh 'thisObjectExistsEverywhere' does not exist?")

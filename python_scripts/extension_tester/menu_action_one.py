#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# You would only use this script if using script_info "type" = "menu" and click on the extensions menu
# Without an 'initializer' this would be where your main script is executed

global moneydance, moneydance_ui, moneydance_data, moneydance_extension_parameter, moneydance_script_fixed_parameter
global MY_EXTENSION_OBJ, myPrint

myPrint(u"@@ Extension Tester >> menu_action_one.py was invoked.")
myPrint(u"  moneydance: %s"%((moneydance)))
myPrint(u"  moneydance_ui: %s"%((moneydance_ui)))
myPrint(u"  moneydance_data: %s"%((moneydance_data)))

# PUT YOUR CODE HERE

# Note you should be in the same namespace as your other scripts within the same extension...
# To reference, use global on the object and then just refer to it - e.g.
global thisObjectExistsEverywhere, ExtensionTester
if u"thisObjectExistsEverywhere" in globals():
    myPrint(u"menu_action_one.py - 'thisObjectExistsEverywhere' exists and contains: %s" %(thisObjectExistsEverywhere))
    if u"moneydance_script_fixed_parameter" in globals():
        myPrint(u"... 'moneydance_script_fixed_parameter' was set to: '%s'" %(moneydance_script_fixed_parameter))

    # The next line is an example - you would not normally do this. I.e. you handle the script code here... This demos calling the ExtensionClass().invoke()
    ExtensionTester.invoke(MY_EXTENSION_OBJ, u"i_called_you_from_menu_action_one.py")
else:
    myPrint(u"menu_action_one.py - Uh-Oh 'thisObjectExistsEverywhere' does not exist?")

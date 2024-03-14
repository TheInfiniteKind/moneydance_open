#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# You would only use/need this script if using script_info {"type" = "method", "method" = "handle_event", "script_file" = "handle_event.py"}
# This gets called when an moneydance 'event' is triggered - see notes at end for the events.
# If you are using the ExtensionClass() method and an initializer, then you do not need this file...

global moneydance, moneydance_ui, moneydance_data, moneydance_extension_parameter, moneydance_extension_loader, moneydance_script_fixed_parameter
global MY_EXTENSION_OBJ, myPrint

myPrint(u"@@ Extension Tester >> handle_event.py was invoked.")
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
    myPrint(u"handle_event.py - 'thisObjectExistsEverywhere' exists and contains: %s" %(thisObjectExistsEverywhere))
    if u"moneydance_script_fixed_parameter" in globals():
        myPrint(u"... 'moneydance_script_fixed_parameter' was set to: '%s'" %(moneydance_script_fixed_parameter))

    # The next line is an example - you would not normally do this. I.e. you handle the event here... This demos calling the ExtensionClass().handleEvent()
    ExtensionTester.handle_event(MY_EXTENSION_OBJ, u"i_called_you_from_handle_event.py:%s" %(moneydance_extension_parameter))
else:
    myPrint(u"handle_event.py - Uh-Oh 'thisObjectExistsEverywhere' does not exist?")

# These are the MD events...
# md:file:opened is the key one when the dataset and the GUI are loaded.

# You should release any reference to MD data objects if dataset is closed/opened!

# md:file:closing	The Moneydance file is being closed
# md:file:closed	The Moneydance file has closed
# md:file:opening	The Moneydance file is being opened
# md:file:opened	The Moneydance file has opened
# md:file:presave	The Moneydance file is about to be saved
# md:file:postsave	The Moneydance file has been saved
# md:app:exiting	Moneydance is shutting down
# md:account:select	An account has been selected by the user
# md:account:root	The root account has been selected
# md:graphreport	An embedded graph or report has been selected
# md:viewbudget	One of the budgets has been selected
# md:viewreminders	One of the reminders has been selected
# md:licenseupdated	The user has updated the license

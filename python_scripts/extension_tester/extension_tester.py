#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# DEMO SCRIPT extension_tester.py
# This DEMO script is set up as a 'method' script extension. To change to a true ExtensionClass() switch the script_info.dict file and rebuild the extension

# ---
# This is called by your script_info 'initializer' if it's to be a run-time extension and you define an ExtensionClass()
# ---
# OR - call it via {"type" = "menu", "script_file" = "extension_tester.py", "name" = "Extension Tester"} in script_info
# if it's to run when clicked on the extensions menu only... If you do this, please also use the unload.py script as a minimum
# ---

# Note: to get the .invoke(), .handle_event(), .unload() methods below to work in the ExtensionClass(), you will have to
# ..remove the "type" = "method" entries in script_info.dict - it's one or the other, not both...

global moneydance, moneydance_ui, moneydance_data, moneydance_extension_parameter, moneydance_extension_loader

from java.lang import System

def myPrint(theTest):
    print(theTest)
    System.err.write(u"%s\n" %(theTest))


myPrint(u"@@ Extension Tester object.init")
myPrint(u"  moneydance: %s" %((moneydance)))
myPrint(u"  moneydance_ui: %s" %((moneydance_ui)))
myPrint(u"  moneydance_data: %s" %((moneydance_data)))
myPrint(u"  moneydance_extension_loader: %s" %((moneydance_extension_loader)))

# example of the namespace....
thisObjectExistsEverywhere = u"Yup - I really do exist everywhere.... ;->"      # This will be a global variable


########################################################################################################################
# If you do not want a run-time extension - i.e. your script just executes when you click the extensions menu, then..
# do NOT use script_info "type" = "initializer", and just use script_info "type" = "menu".
# ... and put your code here
MD_REF = moneydance
MD_REF_UI = moneydance_ui
# CODE HERE - Do not use the code below....



########################################################################################################################
# If you want a run-time extension..... THEN call this script using script_info "type" = "initializer"
# This is your extension class. Put your extension's code in here.... Note the name of the Class will be fed back to MD
class ExtensionTester():        # This can be called whatever you want - but set it below too...

    # Your own initialisation routines
    def __init__(self):
        myPrint(u"@@ Extension Tester object.init")
        self.md_ui = moneydance_ui  # NOTE: This may be None. You need to test/grab at key points using self.ext_context.getUI()
        self.ext_context = None     # This is the same as the moneydance variable
        self.moneydanceExtensionObject = None
        self.moneydanceExtensionLoader = moneydance_extension_loader  # This is the class loader for the whole extension

    # Moneydance will come back and call this method after it knows your class name. It stores this for later use
    def initialize(self, context, extension_wrapper):
        myPrint(u"\n@@ Extension Tester object.initialize with context %s\n...and wrapper %s" %((context), (extension_wrapper)))
        self.ext_context = context
        self.moneydanceExtensionObject = extension_wrapper  # This is com.moneydance.apps.md.controller.PythonExtension

        # This next line will install an item on the Extension menu.. This is optional. It causes MD to call .invoke() in your class
        # You can also do this using script_info "type" = "menu" option to run a script.
        # Use moneydance.showURL("moneydance:fmodule:extension_tester:my_invoke_command:menu_three") for example - to call
        self.ext_context.registerFeature(self.moneydanceExtensionObject, "my_invoke_command:menu_three", None, "Extension Tester >> THREE")

    # noinspection PyMethodMayBeStatic
    def invoke(self, uri):  # This method is called when requested by .showURL(), or from the extension menu - when item clicked
        myPrint(u"@@ Extension Tester object.invoke was called with uri %s" %(uri))

    # noinspection PyMethodMayBeStatic
    def handle_event(self, uri):    # Called on all MD events - Unless you are using script_info "method" = "handle_event"
        myPrint(u"@@ Extension Tester object.handle_event was called with parameter %s" %(uri))

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

    # noinspection PyMethodMayBeStatic
    def unload(self):               # Called when extension uninstalled (re-installed) - unless using script_info "method" = "unload"
        myPrint(u"@@ Extension Tester object.unload was called.")


moneydance_extension = ExtensionTester()    # Pass the name of your class back to MD - this will be called later.

# You don't normally need this line - demo only
MY_EXTENSION_OBJ = moneydance_extension
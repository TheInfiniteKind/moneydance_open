#!/usr/bin/env python
# -*- coding: UTF-8 -*-


class ExtensionTester:

    def __init__(self):
        print("Tester object.init")
        self.md_ui = moneydance_ui
        
    def initialize(self, context, extension_wrapper):
        print("Tester object.initialize with context %s and wrapper %s"%(str(context), str(extension_wrapper)))
        self.ext_context = context
    
    def invoke(self, uri):
        print("Tester object.invoke was called with uri %s"%(uri))
    
    def handleEvent(self, uri):
        print("Tester object.handleEvent was called with parameter %s"%(uri))
    
    def invoke(self, uri):
        print("Tester object.cleanup was called with uri %s"%(uri))
    
    def invoke(self, uri):
        print("Tester object.unload was called with uri %s"%(uri))
        

moneydance_extension = ExtensionTester()


    
    
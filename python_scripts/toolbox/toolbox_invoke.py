#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# You would only use/need this script if using script_info {"type" = "method", "method" = "invoke", "script_file" = "invoke.py"}
# This gets called when moneydance.showURL() is called. It might get called when clicking on the menu item, depending on the combination of options used.
# If you are using the ExtensionClass() method and an initializer, then you do not need this file...

global moneydance_extension_parameter, moneydance_invoke_called, bootstrapped_extension

try: moneydance_invoke_called(moneydance_extension_parameter)
except:
    try: bootstrapped_extension.moneydance_invoke_called(moneydance_extension_parameter)
    except: pass

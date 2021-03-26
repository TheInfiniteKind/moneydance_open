#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Initializer file for extension - this will only run from build 3056 onwards - otherwise ignored

from java.lang import System

_THIS_IS_ = u"extract_data"

msg = u"\n#####################################################################\n" \
      u"%s: %s_init.py initializer script running - doing nothing - will exit....\n" \
      u"#####################################################################\n\n" %(_THIS_IS_,_THIS_IS_)

print(msg)
System.err.write(msg)
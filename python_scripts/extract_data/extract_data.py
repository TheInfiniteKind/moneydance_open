#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# extract_data.py - build: 1037 - Oct 2023 - Stuart Beesley
#                   You can auto invoke by launching MD with one of the following:
#                           '-d [datasetpath] -invoke=moneydance:fmodule:extract_data:autoextract:noquit'
#                           '-d [datasetpath] -invoke=moneydance:fmodule:extract_data:autoextract:quit'
#                                             ...NOTE: MD will auto-quit after executing this way...
#
#                 Using the parameter -nobackup will disable backups for that MD session (from build 5047 onwards)
#
#                 You can also enable the 'auto extract every time dataset is closed' option
#                     WARNING: This will execute all extracts (except attachments) everytime dataset is closed.
#                     Thus, you could launch MD with:
#                           '-d [datasetpath] -invoke_and_quit=moneydance:fmodule:extract_data:hello'
#                           ('hello' does not exist and does nothing, but MD will then start shutdown and if the
#                            option is set then it will initiate the auto extracts)
#                     NOTE: This runs silently.. MD will appear to hang. View help/console (errlog.txt) for messages....


# ######################################################################################################################
# Consolidation of prior many scripts into one - including...:
# stockglance2020.py, extract_reminders_csv.py, extract_currency_history_csv.py, extract_account_registers_csv.py
# extract_investment_transactions_csv.py
#
# YES - there is code inefficiency and duplication here.. It was a toss up between speed of consolidating the scripts,
# or spending a lot of time refining and probably introducing code errors..... This will be refined over time. You will
# also see the evolution of my coding from the first script I created to the most recent (clearly exposed when
# consolidated). I make no apologies for this, all the functions work well.  You will certainly see an over use of
# Globals. Over time, I will enhance the code as I rework functions......
# ######################################################################################################################

# MIT License
#
# Copyright (c) 2021-2023 Stuart Beesley - StuWareSoftSystems
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
###############################################################################

# CREDITS AND THANKS - StockGlance
#  Original StockGlance.java code - James Larus - https://github.com/jameslarus/stockglance
#  Modified to StockGlance75.py - waynelloydsmith - https://github.com/waynelloydsmith/Moneydance-Scripts/blob/master/StockGlance75.py

# CREDITS AND THANKS - Reminders
#  allangdavies - adgetreminderstocsv.py for the original code and concept(s)
#  Mike Enoch (April 2017) and his "swing example-moneydance_edit_reminders.py" script (used for my education)

# This script exports various data items from Moneydance; and can extract the data to a csv file.
# It can also grab, decrypt, and extract/save your attachments
# For Investments and Reminders, it will display on screen (includes stockglance2020)

# Use in Moneydance Menu Window->Show Moneybot Console >> Open Script >> RUN

# Stuart Beesley Created 2021-02-10 tested on MacOS - MD2021 onwards - StuWareSoftSystems....
# Build: 1000 - Initial consolidation of all prior extract scripts
# Build: 1001 - Enhancement to extract_investment_transactions_csv so that accounts with no txns still output the opening balance...
# Build: 1001 - Enhancement to extract_account_registers_csv so that accounts with no txns still output the opening balance...
# Build: 1001 - On both the above, limit the opening balances when created within the date range....
# Build: 1001 - Append date_time to filename - user request....
# Build: 1001 - Enhance stockglance2020 to get cash balances for all accounts when the conditions are correct...
# Build: 1002 - Detect when already running and prevent situation
# Build: 1002 - Fix SG2020 display on account names with non-ascii characters; error trap all extract csv routines
# Build: 1003 - Tweak, block old MD versions
# Build: 1004 - tweak to common code for launch detection
# Build: 1005 - tweak to common code (minor non-functional change)
# Build: 1006 - Switch to SwingUtilities.invokeLater() rather than Thread(); other small internal tweaks; ; fix toolbar location on older versions
# build: 1006 - Build 3051 of Moneydance... fix references to moneydance_* variables;
# build: 1007 - Build 3056 'deal' with the Python loader changes..
# build: 1008 - Build 3056 Utilise .unload() method...
# build: 1009 - Common code tweaks
# build: 1010 - Incorporated new category filter in Extract Account Registers - mods by IK user @mark - thanks!
# build: 1011 - Conforming to IK design requirements... Minor tweaks...
# build: 1012 - Fixed pickle.dump/load common code to work properly cross-platform (e.g. Windows to Mac) by (stripping \r when needed)
# build: 1013 - StockGlance2020 Disabled rounding to Security.getDecimalPlaces() as this is the share balance, not price rounding..!
# build: 1013 - StockGlance2020 Enhanced rounding options with user parameters for mac decimal places rounding, and use current price (or latest price history price)
# build: 1013 - Common code tweaks
# build: 1014 - Trap ZeroDivisionError: when cost basis is zero. Also trap all errors with a user popup
# build: 1014 - New print options for StockGlance2020 and Extract_Data
# build: 1015 - Common code tweaks; fixed colors for Dark themes and to be more MD 'compatible'
# build: 1016 - Common code tweaks; Flat Dark Theme
# build: 1017 - SG2020: Fix print to PDF to make 2 parts to avoid overwriting the same pdf file....
# build: 1018 - Common code tweaks
# build: 1019 - Common code tweaks; catch error in myPrint() on Asian double-byte characters; Other Asian Double-Byte fixes (more str() issues!!)
# build: 1019 - Fix JMenu()s - remove <html> tags (affects colors on older Macs); newer MyJFrame().dispose()
# build: 1020 - Tweak extract reminders - Monkey Patched the display / sort / extract date format....
# build: 1021 - Added <PREVIEW> tag to JFrame titlebar if detected...
# build: 1021 - Added <html> tags to JMenu() titles to stop becoming invisible when mouse hovers
# build: 1022 - Changed JDateField to use user's date format
# build: 1022 - Eliminated common code globals :->
# build: 1022 - Extract Account Registers. Include LOAN and LIABILITY accounts too..
# build: 1023 - Added lWriteParametersToExportFile_SWSS by user request (GitHub: Michael Thompson)
# build: 1023 - Bug fix for .getSubAccounts() - as of build 4069 this is an unmodifiable list; also trap SwingWorker errors
# build: 1023 - Added lOmitLOTDataFromExtract_EIT to Extract Investment Txns to allow user to omit LOT matching data from extract
# build: 1023 - Added lAllowEscapeExitApp_SWSS to allow/block escape key exiting main app's window;  Tweaked the JMenuBar() to say "MENU"
# build: 1023 - Upgraded the Edit Reminders popup so that escape will cancel the popup dialog window.
# build: 1023 - Added showRawItemDetails() to reminders popup right-click menu
# build: 1024 - Fixed call to .setEscapeKeyCancels() on older versions of MD
# build: 1025 - Tweak; Common code
# build: 1025 - FileDialog() (refer: java.desktop/sun/lwawt/macosx/CFileDialog.java) seems to no longer use "com.apple.macos.use-file-dialog-packages" in favor of "apple.awt.use-file-dialog-packages" since Monterrey...
# build: 1025 - Common code update - remove Decimal Grouping Character - not necessary to collect and crashes on newer Java versions (> byte)
# build: 1025 - Add date range selector/filter to extract_investment_registers
# build: 1025 - Fix SG2020 cost_basis conversion back to base on certain non-base security situations (it wrongly assumed the cost basis was always base)
# build: 1026 - Tweak common code
# build: 1027 - Tweak init message with time
# build: 1028 - Added fields to extract investment transactions extract... SecurityID and [optional] security account information (e.g. type, apr, subtype etc)
# build: 1029 - Added new extract_security_balances for Dainius Krusinskas: dainiusforex@gmail.com / dainius.krusinskas@outlook.com (dainiusforex)
# build: 1029 - DAMN! I hit the method/file too large (to compile) problem.. Still not proud of the duplications and use of globals. Anyway, rejigged the script to put more sections in methods...
# build: 1030 - Added bootstrap to execute compiled version of extension (faster to load)....
# build: 1031 - MD2023 (Kotlin compiled version) fixes - especially for (now unadjusted) Start Balance(s) and new Balance Adjustment(s)....
#               Fix common code for MD2023...
# build: 1032 - Common code tweaks; Changed Cleared status for Reconciling from 'x' to 'r' via .getStatusCharRevised(txn)
# build: 1033 - MAJOR UPDATE. NEW Auto Extract Mode (and Extensions Menu option). Allows Multi-extracts in one go; All extracts now via SwingWorker...
# build: 1034 - Added extract future reminders option...; Added extract Trunk; Added extract attachments...
# build: 1034 - You can call extension and auto-extract by launching MD with '-invoke=moneydance:fmodule:extract_data:autoextract' parameter
# build: 1035 - Added extract raw data as JSON file option
# build: 1035 - Added handle_event ability to auto extract upon 'md:file:closing' command...
# build: 1036 - Release references to Model objects...... (so they don't stay in memory etc)....;
#               Increased use of DateRange(); Fixed last1/30/365 days options
#               Added "_CURRENTVALUETOBASE" and "_CURRENTVALUEINVESTCURR" fields to Extract Security Balances report.
# build: 1037 - Further tweaks to DateRangeChooser() last1/30/365 days options inline with build 5051
#               Common code - FileFilter fix...; put options into scrollpane (was cutting off screen)

# todo - EAR: Switch to 'proper' usage of DateRangeChooser() (rather than my own 'copy')
# todo - From client version: add Extract Account Balances; update Extract Security Balances with cash and asof date... (consider asof cost basis)
# todo - StockGlance2020 asof balance date...
# todo - extract budget data?
# todo - import excel writer?

# CUSTOMIZE AND COPY THIS ##############################################################################################
# CUSTOMIZE AND COPY THIS ##############################################################################################
# CUSTOMIZE AND COPY THIS ##############################################################################################

# SET THESE LINES
myModuleID = u"extract_data"
version_build = "1037"
MIN_BUILD_REQD = 1904                                               # Check for builds less than 1904 / version < 2019.4
_I_CAN_RUN_AS_MONEYBOT_SCRIPT = True

global moneydance, moneydance_ui, moneydance_extension_loader, moneydance_extension_parameter

global MD_REF, MD_REF_UI
if "moneydance" in globals(): MD_REF = moneydance           # Make my own copy of reference as MD removes it once main thread ends.. Don't use/hold on to _data variable
if "moneydance_ui" in globals(): MD_REF_UI = moneydance_ui  # Necessary as calls to .getUI() will try to load UI if None - we don't want this....
if "MD_REF" not in globals(): raise Exception("ERROR: 'moneydance' / 'MD_REF' NOT set!?")
if "MD_REF_UI" not in globals(): raise Exception("ERROR: 'moneydance_ui' / 'MD_REF_UI' NOT set!?")

# Nuke unwanted (direct/indirect) reference(s) to AccountBook etc....
if "moneydance_data" in globals():
    moneydance_data = None
    del moneydance_data

if "moneybot" in globals():
    moneybot = None
    del moneybot

from java.lang import Boolean
global debug
if "debug" not in globals():
    # if Moneydance is launched with -d, or this property is set, or extension is being (re)installed with Console open.
    debug = (False or MD_REF.DEBUG or Boolean.getBoolean("moneydance.debug"))

global extract_data_frame_
# SET LINES ABOVE ^^^^

# COPY >> START
import __builtin__ as builtins

def checkObjectInNameSpace(objectName):
    """Checks globals() and builtins for the existence of the object name (used for StuWareSoftSystems' bootstrap)"""
    if objectName is None or not isinstance(objectName, basestring) or objectName == u"": return False
    if objectName in globals(): return True
    return objectName in dir(builtins)


if MD_REF is None: raise Exception(u"CRITICAL ERROR - moneydance object/variable is None?")
if checkObjectInNameSpace(u"moneydance_extension_loader"):
    MD_EXTENSION_LOADER = moneydance_extension_loader
else:
    MD_EXTENSION_LOADER = None

if (u"__file__" in globals() and __file__.startswith(u"bootstrapped_")): del __file__       # Prevent bootstrapped loader setting this....

from java.lang import System, Runnable
from javax.swing import JFrame, SwingUtilities, SwingWorker
from java.awt.event import WindowEvent

class QuickAbortThisScriptException(Exception): pass

class MyJFrame(JFrame):

    def __init__(self, frameTitle=None):
        super(JFrame, self).__init__(frameTitle)
        self.disposing = False
        self.myJFrameVersion = 4
        self.isActiveInMoneydance = False
        self.isRunTimeExtension = False
        self.MoneydanceAppListener = None
        self.HomePageViewObj = None

    def dispose(self):
        # This removes all content as Java/Swing (often) retains the JFrame reference in memory...
        if self.disposing: return
        try:
            self.disposing = True
            self.getContentPane().removeAll()
            if self.getJMenuBar() is not None: self.setJMenuBar(None)
            rootPane = self.getRootPane()
            if rootPane is not None:
                rootPane.getInputMap().clear()
                rootPane.getActionMap().clear()
            super(self.__class__, self).dispose()
        except:
            _msg = "%s: ERROR DISPOSING OF FRAME: %s\n" %(myModuleID, self)
            print(_msg); System.err.write(_msg)
        finally:
            self.disposing = False

class GenericWindowClosingRunnable(Runnable):

    def __init__(self, theFrame):
        self.theFrame = theFrame

    def run(self):
        self.theFrame.setVisible(False)
        self.theFrame.dispatchEvent(WindowEvent(self.theFrame, WindowEvent.WINDOW_CLOSING))

class GenericDisposeRunnable(Runnable):
    def __init__(self, theFrame):
        self.theFrame = theFrame

    def run(self):
        self.theFrame.setVisible(False)
        self.theFrame.dispose()

class GenericVisibleRunnable(Runnable):
    def __init__(self, theFrame, lVisible=True, lToFront=False):
        self.theFrame = theFrame
        self.lVisible = lVisible
        self.lToFront = lToFront

    def run(self):
        self.theFrame.setVisible(self.lVisible)
        if self.lVisible and self.lToFront:
            if self.theFrame.getExtendedState() == JFrame.ICONIFIED:
                self.theFrame.setExtendedState(JFrame.NORMAL)
            self.theFrame.toFront()

def getMyJFrame(moduleName):
    try:
        frames = JFrame.getFrames()
        for fr in frames:
            if (fr.getName().lower().startswith(u"%s_main" %moduleName)
                    and (type(fr).__name__ == MyJFrame.__name__ or type(fr).__name__ == u"MyCOAWindow")  # isinstance() won't work across namespaces
                    and fr.isActiveInMoneydance):
                _msg = "%s: Found live frame: %s (MyJFrame() version: %s)\n" %(myModuleID,fr.getName(),fr.myJFrameVersion)
                print(_msg); System.err.write(_msg)
                if fr.isRunTimeExtension:
                    _msg = "%s: ... and this is a run-time self-installed extension too...\n" %(myModuleID)
                    print(_msg); System.err.write(_msg)
                return fr
    except:
        _msg = "%s: Critical error in getMyJFrame(); caught and ignoring...!\n" %(myModuleID)
        print(_msg); System.err.write(_msg)
    return None


frameToResurrect = None
try:
    # So we check own namespace first for same frame variable...
    if (u"%s_frame_"%myModuleID in globals()
            and (isinstance(extract_data_frame_, MyJFrame)                 # EDIT THIS
                 or type(extract_data_frame_).__name__ == u"MyCOAWindow")  # EDIT THIS
            and extract_data_frame_.isActiveInMoneydance):                 # EDIT THIS
        frameToResurrect = extract_data_frame_                             # EDIT THIS
    else:
        # Now check all frames in the JVM...
        getFr = getMyJFrame( myModuleID )
        if getFr is not None:
            frameToResurrect = getFr
        del getFr
except:
    msg = "%s: Critical error checking frameToResurrect(1); caught and ignoring...!\n" %(myModuleID)
    print(msg); System.err.write(msg)

# ############################
# Trap startup conditions here.... The 'if's pass through to oblivion (and thus a clean exit)... The final 'else' actually runs the script
if int(MD_REF.getBuild()) < MIN_BUILD_REQD:     # Check for builds less than 1904 (version 2019.4) or build 3056 accordingly
    msg = "SORRY YOUR MONEYDANCE VERSION IS TOO OLD FOR THIS SCRIPT/EXTENSION (min build %s required)" %(MIN_BUILD_REQD)
    print(msg); System.err.write(msg)
    try:    MD_REF_UI.showInfoMessage(msg)
    except: raise Exception(msg)

elif frameToResurrect and frameToResurrect.isRunTimeExtension:
    msg = "%s: Sorry - runtime extension already running. Please uninstall/reinstall properly. Must be on build: %s onwards. Now exiting script!\n" %(myModuleID, MIN_BUILD_REQD)
    print(msg); System.err.write(msg)
    try: MD_REF_UI.showInfoMessage(msg)
    except: raise Exception(msg)

elif not _I_CAN_RUN_AS_MONEYBOT_SCRIPT and u"__file__" in globals():
    msg = "%s: Sorry - this script cannot be run in Moneybot console. Please install mxt and run extension properly. Must be on build: %s onwards. Now exiting script!\n" %(myModuleID, MIN_BUILD_REQD)
    print(msg); System.err.write(msg)
    try: MD_REF_UI.showInfoMessage(msg)
    except: raise Exception(msg)

elif not _I_CAN_RUN_AS_MONEYBOT_SCRIPT and not checkObjectInNameSpace(u"moneydance_extension_loader"):
    msg = "%s: Error - moneydance_extension_loader seems to be missing? Must be on build: %s onwards. Now exiting script!\n" %(myModuleID, MIN_BUILD_REQD)
    print(msg); System.err.write(msg)
    try: MD_REF_UI.showInfoMessage(msg)
    except: raise Exception(msg)

elif frameToResurrect:  # and it's active too...
    try:
        msg = "%s: Detected that %s is already running..... Attempting to resurrect..\n" %(myModuleID, myModuleID)
        print(msg); System.err.write(msg)
        SwingUtilities.invokeLater(GenericVisibleRunnable(frameToResurrect, True, True))
    except:
        msg  = "%s: Failed to resurrect main Frame.. This duplicate Script/extension is now terminating.....\n" %(myModuleID)
        print(msg); System.err.write(msg)
        raise Exception(msg)

else:
    del frameToResurrect
    msg = "%s: Startup conditions passed (and no other instances of this program detected). Now executing....\n" %(myModuleID)
    print(msg); System.err.write(msg)

    # COMMON IMPORTS #######################################################################################################
    # COMMON IMPORTS #######################################################################################################
    # COMMON IMPORTS #######################################################################################################

    global sys
    if "sys" not in globals():
        # NOTE: As of MD2022(4040), python.getSystemState().setdefaultencoding("utf8") is called on the python interpreter at script launch...
        import sys
        reload(sys)                     # Dirty hack to eliminate UTF-8 coding errors
        sys.setdefaultencoding('utf8')  # Without this str() fails on unicode strings...

    import os
    import os.path
    import codecs
    import inspect
    import pickle
    import platform
    import csv
    import datetime
    import traceback
    import subprocess

    from org.python.core.util import FileUtil

    from com.moneydance.util import Platform
    from com.moneydance.awt import JTextPanel, GridC, JDateField
    from com.moneydance.apps.md.view.gui import MDImages

    from com.infinitekind.util import DateUtil, CustomDateFormat, StringUtils

    from com.infinitekind.moneydance.model import *
    from com.infinitekind.moneydance.model import AccountUtil, AcctFilter, CurrencyType, CurrencyUtil
    from com.infinitekind.moneydance.model import Account, Reminder, ParentTxn, SplitTxn, TxnSearch, InvestUtil, TxnUtil

    from com.moneydance.apps.md.controller import AccountBookWrapper, AppEventManager                                   # noqa
    from com.infinitekind.moneydance.model import AccountBook
    from com.infinitekind.tiksync import SyncRecord                                                                     # noqa
    from com.infinitekind.util import StreamTable                                                                       # noqa

    from javax.swing import JButton, JScrollPane, WindowConstants, JLabel, JPanel, JComponent, KeyStroke, JDialog, JComboBox
    from javax.swing import JOptionPane, JTextArea, JMenuBar, JMenu, JMenuItem, AbstractAction, JCheckBoxMenuItem, JFileChooser
    from javax.swing import JTextField, JPasswordField, Box, UIManager, JTable, JCheckBox, JRadioButton, ButtonGroup
    from javax.swing.text import PlainDocument
    from javax.swing.border import EmptyBorder
    from javax.swing.filechooser import FileFilter

    exec("from javax.print import attribute")       # IntelliJ doesnt like the use of 'print' (as it's a keyword). Messy, but hey!
    exec("from java.awt.print import PrinterJob")   # IntelliJ doesnt like the use of 'print' (as it's a keyword). Messy, but hey!
    global attribute, PrinterJob

    from java.awt.datatransfer import StringSelection
    from javax.swing.text import DefaultHighlighter
    from javax.swing.event import AncestorListener

    from java.awt import Color, Dimension, FileDialog, FlowLayout, Toolkit, Font, GridBagLayout, GridLayout
    from java.awt import BorderLayout, Dialog, Insets, Point
    from java.awt.event import KeyEvent, WindowAdapter, InputEvent
    from java.util import Date, Locale, UUID

    from java.text import DecimalFormat, SimpleDateFormat, MessageFormat
    from java.util import Calendar, ArrayList
    from java.lang import Thread, IllegalArgumentException, String, Integer, Long
    from java.lang import Double, Math, Character, NoSuchFieldException, NoSuchMethodException, Boolean
    from java.lang.reflect import Modifier
    from java.io import FileNotFoundException, FilenameFilter, File, FileInputStream, FileOutputStream, IOException, StringReader
    from java.io import BufferedReader, InputStreamReader
    from java.nio.charset import Charset

    if int(MD_REF.getBuild()) >= 3067:
        from com.moneydance.apps.md.view.gui.theme import ThemeInfo                                                     # noqa
    else:
        from com.moneydance.apps.md.view.gui.theme import Theme as ThemeInfo                                            # noqa

    if isinstance(None, (JDateField,CurrencyUtil,Reminder,ParentTxn,SplitTxn,TxnSearch, JComboBox, JCheckBox,
                         AccountBook, AccountBookWrapper, Long, Integer, Boolean,
                         JTextArea, JMenuBar, JMenu, JMenuItem, JCheckBoxMenuItem, JFileChooser, JDialog,
                         JButton, FlowLayout, InputEvent, ArrayList, File, IOException, StringReader, BufferedReader,
                         InputStreamReader, Dialog, JTable, BorderLayout, Double, InvestUtil, JRadioButton, ButtonGroup,
                         AccountUtil, AcctFilter, CurrencyType, Account, TxnUtil, JScrollPane, WindowConstants, JFrame,
                         JComponent, KeyStroke, AbstractAction, UIManager, Color, Dimension, Toolkit, KeyEvent, GridLayout,
                         WindowAdapter, CustomDateFormat, SimpleDateFormat, Insets, FileDialog, Thread, SwingWorker)): pass
    if codecs.BOM_UTF8 is not None: pass
    if csv.QUOTE_ALL is not None: pass
    if datetime.MINYEAR is not None: pass
    if Math.max(1,1): pass
    # END COMMON IMPORTS ###################################################################################################

    # COMMON GLOBALS #######################################################################################################
    # All common globals have now been eliminated :->
    # END COMMON GLOBALS ###################################################################################################
    # COPY >> END

    # SET THESE VARIABLES FOR ALL SCRIPTS ##################################################################################
    if "GlobalVars" in globals():   # Prevent wiping if 'buddy' extension - like Toolbox - is running too...
        global GlobalVars
    else:
        class GlobalVars:        # Started using this method for storing global variables from August 2021
            CONTEXT = MD_REF
            defaultPrintService = None
            defaultPrinterAttributes = None
            defaultPrintFontSize = None
            defaultPrintLandscape = None
            defaultDPI = 72     # NOTE: 72dpi is Java2D default for everything; just go with it. No easy way to change
            STATUS_LABEL = None
            DARK_GREEN = Color(0, 192, 0)
            resetPickleParameters = False
            decimalCharSep = "."
            lGlobalErrorDetected = False
            MYPYTHON_DOWNLOAD_URL = "https://yogi1967.github.io/MoneydancePythonScripts/"
            i_am_an_extension_so_run_headless = None
            parametersLoadedFromFile = {}
            thisScriptName = None
            MD_MDPLUS_BUILD = 4040                          # 2022.0
            MD_ALERTCONTROLLER_BUILD = 4077                 # 2022.3
            def __init__(self): pass    # Leave empty

            class Strings:
                def __init__(self): pass    # Leave empty

    GlobalVars.MD_PREFERENCE_KEY_CURRENT_THEME = "gui.current_theme"
    GlobalVars.thisScriptName = u"%s.py(Extension)" %(myModuleID)

    GlobalVars.Strings.MD_KEY_BALANCE_ADJUSTMENT = "baladj"
    # END SET THESE VARIABLES FOR ALL SCRIPTS ##############################################################################

    # >>> THIS SCRIPT'S IMPORTS ############################################################################################

    from com.infinitekind.moneydance.model import DateRange
    from java.awt.event import HierarchyListener

    # from extract_account_registers_csv & extract_investment_transactions_csv
    from copy import deepcopy
    import subprocess
    from com.infinitekind.util import IOUtils as MDIOUtils
    from com.moneydance.apps.md.controller import Util
    from com.moneydance.apps.md.view.gui import DateRangeChooser
    from com.infinitekind.moneydance.model import SecurityType, AbstractTxn                                             # noqa

    # from extract raw JSON file
    from com.moneydance.apps.md.view.gui import ExportWindow                                                            # noqa

    # from stockglance2020 and extract_reminders_csv
    from java.awt.event import AdjustmentListener
    from java.text import NumberFormat, SimpleDateFormat

    from com.moneydance.apps.md.view.gui import EditRemindersWindow                                                     # noqa
    from com.moneydance.apps.md.view.gui import LoanTxnReminderNotificationWindow                                       # noqa
    from com.moneydance.apps.md.view.gui import TxnReminderNotificationWindow                                           # noqa
    from com.moneydance.apps.md.view.gui import BasicReminderNotificationWindow                                         # noqa
    from com.moneydance.apps.md.view.gui import LoanTxnReminderInfoWindow                                               # noqa
    from com.moneydance.apps.md.view.gui import TxnReminderInfoWindow                                                   # noqa
    from com.moneydance.apps.md.view.gui import BasicReminderInfoWindow                                                 # noqa
    from com.infinitekind.moneydance.model import ReminderListener                                                      # noqa

    from java.awt.event import MouseAdapter
    from java.util import Comparator
    from javax.swing import SortOrder, ListSelectionModel, JPopupMenu
    from javax.swing.table import DefaultTableCellRenderer, DefaultTableModel, TableRowSorter
    from javax.swing.border import CompoundBorder, MatteBorder
    from javax.swing.event import TableColumnModelListener
    from java.lang import Number
    from com.moneydance.apps.md.controller import AppEventListener
    from com.infinitekind.util import StringUtils
    exec("from java.awt.print import Book")     # IntelliJ doesnt like the use of 'print' (as it's a keyword). Messy, but hey!
    global Book

    # from extract_currency_history
    # <none>

    # >>> END THIS SCRIPT'S IMPORTS ########################################################################################

    # >>> THIS SCRIPT'S GLOBALS ############################################################################################

    # Saved to parameters file

    # Common
    global __extract_data, extract_filename
    global lStripASCII, csvDelimiter, userdateformat, lWriteBOMToExportFile_SWSS
    global hideInactiveAccounts, hideHiddenAccounts, hideHiddenSecurities
    global lAllSecurity, filterForSecurity, lAllAccounts, filterForAccounts, lAllCurrency, filterForCurrency
    global whichDefaultExtractToRun_SWSS, lWriteParametersToExportFile_SWSS, lAllowEscapeExitApp_SWSS

    # all
    global autoExtract_SG2020, autoExtract_ERTC, autoExtract_EAR, autoExtract_EIT, autoExtract_ECH, autoExtract_ESB, autoExtract_ETRUNK, autoExtract_JSON, autoExtract_EATTACH

    # from extract_account_registers_csv
    global lIncludeSubAccounts_EAR
    global lIncludeOpeningBalances_EAR
    global lIncludeBalanceAdjustments_EAR
    global userdateStart_EAR, userdateEnd_EAR
    global lAllTags_EAR, tagFilter_EAR, lExtractAttachments_EAR
    global saveDropDownAccountUUID_EAR, lIncludeInternalTransfers_EAR, saveDropDownDateRange_EAR
    global lAllText_EAR, textFilter_EAR, lAllCategories_EAR, categoriesFilter_EAR

    # from extract_investment_transactions_csv
    global lIncludeOpeningBalances, lIncludeBalanceAdjustments, lAdjustForSplits
    global lExtractAttachments_EIT, lOmitLOTDataFromExtract_EIT, lExtractExtraSecurityAcctInfo
    global lFilterDateRange_EIT, filterDateStart_EIT, filterDateEnd_EIT

    # from stockglance2020
    global lIncludeCashBalances, _column_widths_SG2020
    global lSplitSecuritiesByAccount, lExcludeTotalsFromCSV
    global lIncludeFutureBalances_SG2020
    global maxDecimalPlacesRounding_SG2020, lUseCurrentPrice_SG2020

    # from extract_reminders_csv
    global _column_widths_ERTC, lExtractFutureRemindersToo_ERTC

    # from extract_currency_history
    global lSimplify_ECH, userdateStart_ECH, userdateEnd_ECH, hideHiddenCurrencies_ECH

    # from extract_security_balances

    # ------------
    # Other used by program(s)

    # from extract_account_registers_csv & extract_investment_transactions_csv
    global dataKeys, attachmentDir, relativePath, lDidIUseAttachmentDir

    # from stockglance2020
    global headingNames
    global _SHRS_FORMATTED, _SHRS_RAW, _PRICE_FORMATTED, _PRICE_RAW, _CVALUE_FORMATTED, _CVALUE_RAW, _BVALUE_FORMATTED, _BVALUE_RAW
    global _CBVALUE_FORMATTED, _CBVALUE_RAW, _GAIN_FORMATTED, _GAIN_RAW, _SORT, _EXCLUDECSV, _GAINPCT
    global acctSeparator

    # from extract_reminders_csv & extract_currency_history
    global csvheaderline, headerFormats
    global focus, row, EditedReminderCheck, ReminderTable_Count, ExtractDetails_Count

    # Set programmatic defaults/parameters for filters HERE.... Saved Parameters will override these now
    # NOTE: You  can override in the pop-up screen

    # Common
    csvDelimiter = ","																									# noqa
    userdateformat = "%Y/%m/%d"                                                                                         # noqa
    extract_filename="SELECT_FILENAME.csv"                                                                              # noqa
    lStripASCII = False                                                                                                 # noqa
    attachmentDir = ""                                                                                                  # noqa
    lDidIUseAttachmentDir = False                                                                                       # noqa
    lWriteBOMToExportFile_SWSS = True                                                                                   # noqa
    lWriteParametersToExportFile_SWSS = True                                                                            # noqa
    hideInactiveAccounts = True                                                                                         # noqa
    hideHiddenAccounts = True                                                                                           # noqa
    lAllAccounts = True                                                                                                 # noqa
    filterForAccounts = "ALL"                                                                                           # noqa
    hideHiddenSecurities = True                                                                                         # noqa
    lAllSecurity = True                                                                                                 # noqa
    filterForSecurity = "ALL"                                                                                           # noqa

    lAllCurrency = True                                                                                                 # noqa
    filterForCurrency = "ALL"                                                                                           # noqa
    whichDefaultExtractToRun_SWSS = None                                                                                # noqa
    lAllowEscapeExitApp_SWSS = True                                                                                     # noqa

    # from extract_account_registers_csv
    lIncludeSubAccounts_EAR = False                                                                                     # noqa
    lIncludeOpeningBalances_EAR = True                                                                                  # noqa
    lIncludeBalanceAdjustments_EAR = True                                                                               # noqa
    userdateStart_EAR = DateRange().getStartDateInt()                                                                   # noqa
    userdateEnd_EAR = DateRange().getEndDateInt()                                                                       # noqa
    lAllTags_EAR = True                                                                                                 # noqa
    tagFilter_EAR = "ALL"                                                                                               # noqa
    lAllText_EAR = True                                                                                                 # noqa
    textFilter_EAR = "ALL"                                                                                              # noqa
    lAllCategories_EAR = True                                                                                           # noqa
    categoriesFilter_EAR = "ALL"                                                                                        # noqa
    lExtractAttachments_EAR=False                                                                                       # noqa
    saveDropDownAccountUUID_EAR = ""                                                                                    # noqa
    saveDropDownDateRange_EAR = ""                                                                                      # noqa
    lIncludeInternalTransfers_EAR = True                                                                                # noqa

    # from extract_investment_transactions_csv
    lIncludeOpeningBalances = True                                                                                      # noqa
    lIncludeBalanceAdjustments = True                                                                                   # noqa
    lAdjustForSplits = True                                                                                             # noqa
    lExtractAttachments_EIT = False                                                                                     # noqa
    lOmitLOTDataFromExtract_EIT = False                                                                                 # noqa
    lExtractExtraSecurityAcctInfo = False                                                                               # noqa
    lFilterDateRange_EIT = False                                                                                        # noqa
    filterDateStart_EIT = 0                                                                                             # noqa
    filterDateEnd_EIT = 0                                                                                               # noqa

    # from stockglance2020
    lIncludeCashBalances = False                                                                                        # noqa
    lSplitSecuritiesByAccount = False                                                                                   # noqa
    lExcludeTotalsFromCSV = False                                                                                       # noqa
    lIncludeFutureBalances_SG2020 = False                                                                               # noqa
    maxDecimalPlacesRounding_SG2020 = 4                                                                                 # noqa
    lUseCurrentPrice_SG2020 = True                                                                                      # noqa
    _column_widths_SG2020 = []                                                                                          # noqa
    headingNames = ""                                                                                                   # noqa
    acctSeparator = u' : '                                                                                              # noqa

    # from extract_reminders_csv
    _column_widths_ERTC = []                                                                                          	# noqa
    lExtractFutureRemindersToo_ERTC = False                                                                             # noqa

    # extract_currency_history
    lSimplify_ECH = False                                                                                               # noqa
    userdateStart_ECH = DateRange().getStartDateInt()                                                                   # noqa
    userdateEnd_ECH = DateRange().getEndDateInt()                                                                       # noqa
    hideHiddenCurrencies_ECH = True                                                                                     # noqa

    autoExtract_SG2020 = False                                                                                          # noqa
    autoExtract_ERTC = False                                                                                            # noqa
    autoExtract_EAR = False                                                                                             # noqa
    autoExtract_EIT = False                                                                                             # noqa
    autoExtract_ECH = False                                                                                             # noqa
    autoExtract_ESB = False                                                                                             # noqa
    autoExtract_ETRUNK = False                                                                                          # noqa
    autoExtract_JSON = False                                                                                            # noqa
    autoExtract_EATTACH = False                                                                                         # noqa

    # Do these once here (for objects that might hold Model objects etc) and then release at the end... (not the cleanest method...)
    GlobalVars.dropDownAccount_EAR = None
    GlobalVars.baseCurrency = None
    GlobalVars.scrollpane = None
    GlobalVars.table = None
    GlobalVars.stockGlanceInstance = None
    GlobalVars.transactionTable = None
    GlobalVars.csvlines_reminders_future = None
    GlobalVars.tableHeaderRowList_reminders_future = None

    GlobalVars.sdf = None
    GlobalVars.csvfilename = None
    GlobalVars.csvfilename_future = None
    GlobalVars.scriptpath = ""
    GlobalVars.extractFolderName = None

    # StockGlance2020 - converted from globals
    GlobalVars.rawDataTable_sg2020 = None
    GlobalVars.rawFooterTable_sg2020 = None

    # from extract_reminders_csv - converted from globals
    GlobalVars.csvlines_reminders = None
    GlobalVars.csvlines_reminders_future = None
    GlobalVars.tableHeaderRowList_reminders_future = None

    GlobalVars.daysToLookForward_LFR = 365

    # >>> END THIS SCRIPT'S GLOBALS ############################################################################################

    # COPY >> START
    # COMMON CODE ######################################################################################################
    # COMMON CODE ################# VERSION 108 ########################################################################
    # COMMON CODE ######################################################################################################
    GlobalVars.i_am_an_extension_so_run_headless = False
    try:
        GlobalVars.thisScriptName = os.path.basename(__file__)
    except:
        GlobalVars.i_am_an_extension_so_run_headless = True

    scriptExit = """
----------------------------------------------------------------------------------------------------------------------
Thank you for using %s!
The author has other useful Extensions / Moneybot Python scripts available...:

Extension (.mxt) format only:
Toolbox: View Moneydance settings, diagnostics, fix issues, change settings and much more
         + Extension menus: Total selected txns; Move Investment Txns; Zap md+/ofx/qif (default) memo fields;

Custom Balances (net_account_balances): Summary Page (HomePage) widget. Display the total of selected Account Balances

Extension (.mxt) and Script (.py) Versions available:
Extract Data: Extract various data to screen /or csv.. (also auto-extract mode): Includes:
    - StockGlance2020: Securities/stocks, total by security across investment accounts;
    - Reminders; Account register transaction (attachments optional);
    - Investment transactions (attachments optional); Security Balances; Currency price history;
    - Decrypt / extract raw 'Trunk' file; Extract raw data as JSON file; All attachments;

List Future Reminders:                  View future reminders on screen. Allows you to set the days to look forward
Security Performance Graph:             Graphs selected securities, calculating relative price performance as percentage
Accounts Categories Mega Search Window: Combines MD Menu> Tools>Accounts/Categories and adds Quick Search box/capability

A collection of useful ad-hoc scripts (zip file)
useful_scripts:                         Just unzip and select the script you want for the task at hand...

Visit: %s (Author's site)
----------------------------------------------------------------------------------------------------------------------
""" %(GlobalVars.thisScriptName, GlobalVars.MYPYTHON_DOWNLOAD_URL)

    def cleanup_references():
        global MD_REF, MD_REF_UI, MD_EXTENSION_LOADER
        # myPrint("DB","About to delete reference to MD_REF, MD_REF_UI and MD_EXTENSION_LOADER....!")
        # del MD_REF, MD_REF_UI, MD_EXTENSION_LOADER

        resetGlobalVariables()

        myPrint("DB", "... destroying own reference to frame('extract_data_frame_')...")
        global extract_data_frame_
        extract_data_frame_ = None
        del extract_data_frame_

    def load_text_from_stream_file(theStream):
        myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()")

        cs = Charset.forName("UTF-8")

        istream = theStream

        if not istream:
            myPrint("B","... Error - the input stream is None")
            return "<NONE>"

        fileContents = ""
        istr = bufr = None
        try:
            istr = InputStreamReader(istream, cs)
            bufr = BufferedReader(istr)
            while True:
                line = bufr.readLine()
                if line is not None:
                    line += "\n"                   # not very efficient - should convert this to "\n".join() to contents
                    fileContents+=line
                    continue
                break
            fileContents+="\n<END>"
        except:
            myPrint("B", "ERROR reading from input stream... ")
            dump_sys_error_to_md_console_and_errorlog()

        try: bufr.close()
        except: pass

        try: istr.close()
        except: pass

        try: istream.close()
        except: pass

        myPrint("DB", "Exiting ", inspect.currentframe().f_code.co_name, "()")

        return fileContents

    # P=Display on Python Console, J=Display on MD (Java) Console Error Log, B=Both, D=If Debug Only print, DB=print both
    def myPrint(where, *args):
        if where[0] == "D" and not debug: return

        try:
            printString = ""
            for what in args:
                printString += "%s " %what
            printString = printString.rstrip(" ")

            if where == "P" or where == "B" or where[0] == "D":
                if not GlobalVars.i_am_an_extension_so_run_headless:
                    try:
                        print(printString)
                    except:
                        print("Error writing to screen...")
                        dump_sys_error_to_md_console_and_errorlog()

            if where == "J" or where == "B" or where == "DB":
                dt = datetime.datetime.now().strftime("%Y/%m/%d-%H:%M:%S")
                try:
                    System.err.write(GlobalVars.thisScriptName + ":" + dt + ": ")
                    System.err.write(printString)
                    System.err.write("\n")
                except:
                    System.err.write(GlobalVars.thisScriptName + ":" + dt + ": " + "Error writing to console")
                    dump_sys_error_to_md_console_and_errorlog()

        except IllegalArgumentException:
            myPrint("B","ERROR - Probably on a multi-byte character..... Will ignore as code should just continue (PLEASE REPORT TO DEVELOPER).....")
            dump_sys_error_to_md_console_and_errorlog()

        return


    if debug: myPrint("B", "** DEBUG IS ON **")

    def dump_sys_error_to_md_console_and_errorlog(lReturnText=False):

        tb = traceback.format_exc()
        trace = traceback.format_stack()
        theText =  ".\n" \
                   "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n" \
                   "@@@@@ Unexpected error caught!\n".upper()
        theText += tb
        for trace_line in trace: theText += trace_line
        theText += "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
        myPrint("B", theText)
        if lReturnText: return theText
        return

    def safeStr(_theText): return ("%s" %(_theText))

    def pad(theText, theLength, padChar=u" "):
        if not isinstance(theText, (unicode, str)): theText = safeStr(theText)
        theText = theText[:theLength].ljust(theLength, padChar)
        return theText

    def rpad(theText, theLength, padChar=u" "):
        if not isinstance(theText, (unicode, str)): theText = safeStr(theText)
        theText = theText[:theLength].rjust(theLength, padChar)
        return theText

    def cpad(theText, theLength, padChar=u" "):
        if not isinstance(theText, (unicode, str)): theText = safeStr(theText)
        if len(theText) >= theLength: return theText[:theLength]
        padLength = int((theLength - len(theText)) / 2)
        theText = theText[:theLength]
        theText = ((padChar * padLength)+theText+(padChar * padLength))[:theLength]
        return theText

    myPrint("B", GlobalVars.thisScriptName, ": Python Script Initialising.......", "Build:", version_build)

    def getMonoFont():
        try:
            theFont = MD_REF.getUI().getFonts().code
            # if debug: myPrint("B","Success setting Font set to Moneydance code: %s" %theFont)
        except:
            theFont = Font("monospaced", Font.PLAIN, 15)
            if debug: myPrint("B","Failed to Font set to Moneydance code - So using: %s" %theFont)

        return theFont

    def isOSXVersionAtLeast(compareVersion):
        # type: (basestring) -> bool
        """Pass a string in the format 'x.x.x'. Will check that this MacOSX version is at least that version. The 3rd micro number is optional"""

        try:
            if not Platform.isOSX(): return False

            def convertVersion(convertString):
                _os_major = _os_minor = _os_micro = 0
                _versionNumbers = []

                for versionPart in StringUtils.splitIntoList(convertString, '.'):
                    strippedPart = StringUtils.stripNonNumbers(versionPart, '.')
                    if (StringUtils.isInteger(strippedPart)):
                        _versionNumbers.append(Integer.valueOf(Integer.parseInt(strippedPart)))
                    else:
                        _versionNumbers.append(0)

                if len(_versionNumbers) >= 1: _os_major = max(0, _versionNumbers[0])
                if len(_versionNumbers) >= 2: _os_minor = max(0, _versionNumbers[1])
                if len(_versionNumbers) >= 3: _os_micro = max(0, _versionNumbers[2])

                return _os_major, _os_minor, _os_micro


            os_major, os_minor, os_micro = convertVersion(System.getProperty("os.version", "0.0.0"))
            myPrint("DB", "MacOS Version number(s): %s.%s.%s" %(os_major, os_minor, os_micro))

            if not isinstance(compareVersion, basestring) or len(compareVersion) < 1:
                myPrint("B", "ERROR: Invalid compareVersion of '%s' passed - returning False" %(compareVersion))
                return False

            chk_os_major, chk_os_minor, chk_os_micro = convertVersion(compareVersion)
            myPrint("DB", "Comparing against Version(s): %s.%s.%s" %(chk_os_major, chk_os_minor, chk_os_micro))


            if os_major < chk_os_major: return False
            if os_major > chk_os_major: return True

            if os_minor < chk_os_minor: return False
            if os_minor > chk_os_minor: return True

            if os_micro < chk_os_micro: return False
            return True

        except:
            myPrint("B", "ERROR: isOSXVersionAtLeast() failed - returning False")
            dump_sys_error_to_md_console_and_errorlog()
            return False

    def isOSXVersionCheetahOrLater():       return isOSXVersionAtLeast("10.0")
    def isOSXVersionPumaOrLater():          return isOSXVersionAtLeast("10.1")
    def isOSXVersionJaguarOrLater():        return isOSXVersionAtLeast("10.2")
    def isOSXVersionPantherOrLater():       return isOSXVersionAtLeast("10.3")
    def isOSXVersionTigerOrLater():         return isOSXVersionAtLeast("10.4")
    def isOSXVersionLeopardOrLater():       return isOSXVersionAtLeast("10.5")
    def isOSXVersionSnowLeopardOrLater():   return isOSXVersionAtLeast("10.6")
    def isOSXVersionLionOrLater():          return isOSXVersionAtLeast("10.7")
    def isOSXVersionMountainLionOrLater():  return isOSXVersionAtLeast("10.8")
    def isOSXVersionMavericksOrLater():     return isOSXVersionAtLeast("10.9")
    def isOSXVersionYosemiteOrLater():      return isOSXVersionAtLeast("10.10")
    def isOSXVersionElCapitanOrLater():     return isOSXVersionAtLeast("10.11")
    def isOSXVersionSierraOrLater():        return isOSXVersionAtLeast("10.12")
    def isOSXVersionHighSierraOrLater():    return isOSXVersionAtLeast("10.13")
    def isOSXVersionMojaveOrLater():        return isOSXVersionAtLeast("10.14")
    def isOSXVersionCatalinaOrLater():      return isOSXVersionAtLeast("10.15")
    def isOSXVersionBigSurOrLater():        return isOSXVersionAtLeast("10.16")  # BigSur is officially 11.0, but started at 10.16
    def isOSXVersionMontereyOrLater():      return isOSXVersionAtLeast("12.0")
    def isOSXVersionVenturaOrLater():       return isOSXVersionAtLeast("13.0")

    def get_home_dir():
        homeDir = None

        # noinspection PyBroadException
        try:
            if Platform.isOSX():
                homeDir = System.getProperty(u"UserHome")  # On a Mac in a Java VM, the homedir is hidden
            else:
                # homeDir = System.getProperty("user.home")
                homeDir = os.path.expanduser(u"~")  # Should work on Unix and Windows
                if homeDir is None or homeDir == u"":
                    homeDir = System.getProperty(u"user.home")
                if homeDir is None or homeDir == u"":
                    homeDir = os.environ.get(u"HOMEPATH")
        except:
            pass

        if homeDir is None or homeDir == u"":
            homeDir = MD_REF.getCurrentAccountBook().getRootFolder().getParent()  # Better than nothing!

        if homeDir is None or homeDir == u"":
            homeDir = u""

        myPrint("DB", "Home Directory detected...:", homeDir)
        return homeDir

    def getDecimalPoint():
        decimalFormat = DecimalFormat.getInstance()
        # noinspection PyUnresolvedReferences
        decimalSymbols = decimalFormat.getDecimalFormatSymbols()

        try:
            _decimalCharSep = decimalSymbols.getDecimalSeparator()
            myPrint(u"D",u"Decimal Point Character: %s" %(_decimalCharSep))
            return _decimalCharSep
        except:
            myPrint(u"B",u"Error in getDecimalPoint() routine....?")
            dump_sys_error_to_md_console_and_errorlog()
        return u"error"

    GlobalVars.ALLOWED_CSV_FILE_DELIMITER_STRINGS = [";", "|", ","]
    GlobalVars.decimalCharSep = getDecimalPoint()


    def isMacDarkModeDetected():
        darkResponse = "LIGHT"
        if Platform.isOSX():
            try:
                darkResponse = subprocess.check_output("defaults read -g AppleInterfaceStyle", shell=True)
                darkResponse = darkResponse.strip().lower()
            except: pass
        return ("dark" in darkResponse)

    def isMDThemeDark():
        try:
            currentTheme = MD_REF.getUI().getCurrentTheme()
            try:
                if currentTheme.isSystemDark(): return True     # NOTE: Only VAQua has isSystemDark()
            except: pass
            if "dark" in currentTheme.getThemeID().lower(): return True
            if isMDThemeFlatDark(): return True
            if isMDThemeDarcula(): return True
        except: pass
        return False

    def isMDThemeDarcula():
        try:
            currentTheme = MD_REF.getUI().getCurrentTheme()
            if isMDThemeFlatDark(): return False                    # Flat Dark pretends to be Darcula!
            if "darcula" in currentTheme.getThemeID(): return True
        except: pass
        return False

    def isMDThemeCustomizable():
        try:
            currentTheme = MD_REF.getUI().getCurrentTheme()
            if currentTheme.isCustomizable(): return True
        except: pass
        return False

    def isMDThemeHighContrast():
        try:
            currentTheme = MD_REF.getUI().getCurrentTheme()
            if "high_contrast" in currentTheme.getThemeID(): return True
        except: pass
        return False

    def isMDThemeDefault():
        try:
            currentTheme = MD_REF.getUI().getCurrentTheme()
            if "default" in currentTheme.getThemeID(): return True
        except: pass
        return False

    def isMDThemeClassic():
        try:
            currentTheme = MD_REF.getUI().getCurrentTheme()
            if "classic" in currentTheme.getThemeID(): return True
        except: pass
        return False

    def isMDThemeSolarizedLight():
        try:
            currentTheme = MD_REF.getUI().getCurrentTheme()
            if "solarized_light" in currentTheme.getThemeID(): return True
        except: pass
        return False

    def isMDThemeSolarizedDark():
        try:
            currentTheme = MD_REF.getUI().getCurrentTheme()
            if "solarized_dark" in currentTheme.getThemeID(): return True
        except: pass
        return False

    def isMDThemeFlatDark():
        try:
            currentTheme = MD_REF.getUI().getCurrentTheme()
            if "flat dark" in currentTheme.toString().lower(): return True
        except: pass
        return False

    def isMDThemeVAQua():
        if Platform.isOSX():
            try:
                # currentTheme = MD_REF.getUI().getCurrentTheme()       # Not reset when changed in-session as it's a final variable!
                # if ".vaqua" in safeStr(currentTheme.getClass()).lower(): return True
                currentTheme = ThemeInfo.themeForID(MD_REF.getUI(), MD_REF.getPreferences().getSetting(GlobalVars.MD_PREFERENCE_KEY_CURRENT_THEME, ThemeInfo.DEFAULT_THEME_ID))
                if ".vaqua" in currentTheme.getClass().getName().lower(): return True                                   # noqa
            except:
                myPrint("B", "@@ Error in isMDThemeVAQua() - Alert author! Error:", sys.exc_info()[1])
        return False

    def isIntelX86_32bit():
        """Detect Intel x86 32bit system"""
        return String(System.getProperty("os.arch", "null").strip()).toLowerCase(Locale.ROOT) == "x86"

    def getMDIcon(startingIcon=None, lAlwaysGetIcon=False):
        if lAlwaysGetIcon or isIntelX86_32bit():
            return MD_REF.getUI().getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png")
        return startingIcon

    # JOptionPane.DEFAULT_OPTION, JOptionPane.YES_NO_OPTION, JOptionPane.YES_NO_CANCEL_OPTION, JOptionPane.OK_CANCEL_OPTION
    # JOptionPane.ERROR_MESSAGE, JOptionPane.INFORMATION_MESSAGE, JOptionPane.WARNING_MESSAGE, JOptionPane.QUESTION_MESSAGE, JOptionPane.PLAIN_MESSAGE

    # Copies MD_REF.getUI().showInfoMessage (but a newer version now exists in MD internal code)
    def myPopupInformationBox(theParent=None, theMessage="What no message?!", theTitle="Info", theMessageType=JOptionPane.INFORMATION_MESSAGE):

        if theParent is None and (theMessageType == JOptionPane.PLAIN_MESSAGE or theMessageType == JOptionPane.INFORMATION_MESSAGE):
            icon = getMDIcon(lAlwaysGetIcon=True)
        else:
            icon = getMDIcon(None)
        JOptionPane.showMessageDialog(theParent, JTextPanel(theMessage), theTitle, theMessageType, icon)

    def wrapLines(message, numChars=40):
        charCount = 0
        result=""
        for ch in message:
            if ch == '\n' or ch == '\r':
                charCount = 0
            elif charCount > numChars and not Character.isWhitespace(ch):
                result+="\n"
                charCount = 0
            else:
                charCount+=1
            result+=ch
        return result

    def myPopupAskBackup(theParent=None, theMessage="What no message?!", lReturnTheTruth=False):

        _options=["STOP", "PROCEED WITHOUT BACKUP", "DO BACKUP NOW"]
        response = JOptionPane.showOptionDialog(theParent,
                                                theMessage,
                                                "PERFORM BACKUP BEFORE UPDATE?",
                                                0,
                                                JOptionPane.WARNING_MESSAGE,
                                                getMDIcon(),
                                                _options,
                                                _options[0])

        if response == 2:
            myPrint("B", "User requested to create a backup before update/fix - calling Moneydance's 'Export Backup' routine...")
            MD_REF.getUI().setStatus("%s is creating a backup...." %(GlobalVars.thisScriptName),-1.0)
            MD_REF.getUI().saveToBackup(None)
            MD_REF.getUI().setStatus("%s create (export) backup process completed...." %(GlobalVars.thisScriptName),0)
            return True

        elif response == 1:
            myPrint("B", "User DECLINED to create a backup before update/fix...!")
            if not lReturnTheTruth:
                return True

        return False

    # Copied MD_REF.getUI().askQuestion
    def myPopupAskQuestion(theParent=None,
                           theTitle="Question",
                           theQuestion="What?",
                           theOptionType=JOptionPane.YES_NO_OPTION,
                           theMessageType=JOptionPane.QUESTION_MESSAGE):

        if theParent is None and (theMessageType == JOptionPane.PLAIN_MESSAGE or theMessageType == JOptionPane.INFORMATION_MESSAGE):
            icon = getMDIcon(lAlwaysGetIcon=True)
        else:
            icon = getMDIcon(None)

        # question = wrapLines(theQuestion)
        question = theQuestion
        result = JOptionPane.showConfirmDialog(theParent,
                                               question,
                                               theTitle,
                                               theOptionType,
                                               theMessageType,
                                               icon)
        return result == 0

    # Copies Moneydance .askForQuestion
    def myPopupAskForInput(theParent,
                           theTitle,
                           theFieldLabel,
                           theFieldDescription="",
                           defaultValue=None,
                           isPassword=False,
                           theMessageType=JOptionPane.INFORMATION_MESSAGE):

        if theParent is None and (theMessageType == JOptionPane.PLAIN_MESSAGE or theMessageType == JOptionPane.INFORMATION_MESSAGE):
            icon = getMDIcon(lAlwaysGetIcon=True)
        else:
            icon = getMDIcon(None)

        p = JPanel(GridBagLayout())
        defaultText = None
        if defaultValue: defaultText = defaultValue
        if isPassword:
            field = JPasswordField(defaultText)
        else:
            field = JTextField(defaultText)
        field.addAncestorListener(RequestFocusListener())

        _x = 0
        if theFieldLabel:
            p.add(JLabel(theFieldLabel), GridC.getc(_x, 0).east())
            _x+=1

        p.add(field, GridC.getc(_x, 0).field())
        p.add(Box.createHorizontalStrut(244), GridC.getc(_x, 0))
        if theFieldDescription:
            p.add(JTextPanel(theFieldDescription), GridC.getc(_x, 1).field().colspan(_x + 1))
        if (JOptionPane.showConfirmDialog(theParent,
                                          p,
                                          theTitle,
                                          JOptionPane.OK_CANCEL_OPTION,
                                          theMessageType,
                                          icon) == 0):
            return field.getText()
        return None

    # APPLICATION_MODAL, DOCUMENT_MODAL, MODELESS, TOOLKIT_MODAL
    class MyPopUpDialogBox():

        def __init__(self,
                     theParent=None,
                     theStatus="",
                     theMessage="",
                     maxSize=Dimension(0,0),
                     theTitle="Info",
                     lModal=True,
                     lCancelButton=False,
                     OKButtonText="OK",
                     lAlertLevel=0):

            self.theParent = theParent
            self.theStatus = theStatus
            self.theMessage = theMessage
            self.maxSize = maxSize
            self.theTitle = theTitle
            self.lModal = lModal
            self.lCancelButton = lCancelButton
            self.OKButtonText = OKButtonText
            self.lAlertLevel = lAlertLevel
            self.fakeJFrame = None
            self._popup_d = None
            self.lResult = [None]
            self.statusLabel = None
            self.messageJText = None
            if not self.theMessage.endswith("\n"): self.theMessage+="\n"
            if self.OKButtonText == "": self.OKButtonText="OK"
            if isMDThemeDark() or isMacDarkModeDetected(): self.lAlertLevel = 0

        def updateMessages(self, newTitle=None, newStatus=None, newMessage=None, lPack=True):
            # We wait when on the EDT as most scripts execute on the EDT.. So this is probably an in execution update message
            # ... if we invokeLater() then the message will (probably) only appear after the EDT script finishes....
            genericSwingEDTRunner(False, True, self._updateMessages, newTitle, newStatus, newMessage, lPack)

        def _updateMessages(self, newTitle=None, newStatus=None, newMessage=None, lPack=True):
            if not newTitle and not newStatus and not newMessage: return
            if newTitle:
                self.theTitle = newTitle
                self._popup_d.setTitle(self.theTitle)
            if newStatus:
                self.theStatus = newStatus
                self.statusLabel.setText(self.theStatus)
            if newMessage:
                self.theMessage = newMessage
                self.messageJText.setText(self.theMessage)
            if lPack: self._popup_d.pack()

        class WindowListener(WindowAdapter):

            def __init__(self, theDialog, theFakeFrame, lResult):
                self.theDialog = theDialog
                self.theFakeFrame = theFakeFrame
                self.lResult = lResult

            def windowClosing(self, WindowEvent):                                                                       # noqa
                myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", WindowEvent)
                myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

                myPrint("DB", "JDialog Frame shutting down....")

                self.lResult[0] = False

                # Note - listeners are already on the EDT
                if self.theFakeFrame is not None:
                    self.theDialog.dispose()
                    self.theFakeFrame.dispose()
                else:
                    self.theDialog.dispose()

                myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
                return

        class OKButtonAction(AbstractAction):

            def __init__(self, theDialog, theFakeFrame, lResult):
                self.theDialog = theDialog
                self.theFakeFrame = theFakeFrame
                self.lResult = lResult

            def actionPerformed(self, event):
                myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event)
                myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

                self.lResult[0] = True

                # Note - listeners are already on the EDT
                if self.theFakeFrame is not None:
                    self.theDialog.dispose()
                    self.theFakeFrame.dispose()
                else:
                    self.theDialog.dispose()

                myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
                return

        class CancelButtonAction(AbstractAction):

            def __init__(self, theDialog, theFakeFrame, lResult):
                self.theDialog = theDialog
                self.theFakeFrame = theFakeFrame
                self.lResult = lResult

            def actionPerformed(self, event):
                myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event)
                myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

                self.lResult[0] = False

                # Note - listeners are already on the EDT
                if self.theFakeFrame is not None:
                    self.theDialog.dispose()
                    self.theFakeFrame.dispose()
                else:
                    self.theDialog.dispose()

                myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
                return

        def kill(self):
            myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()")
            myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

            if not SwingUtilities.isEventDispatchThread():
                SwingUtilities.invokeLater(GenericVisibleRunnable(self._popup_d, False))
                if self.fakeJFrame is not None:
                    SwingUtilities.invokeLater(GenericDisposeRunnable(self._popup_d))
                    SwingUtilities.invokeLater(GenericDisposeRunnable(self.fakeJFrame))
                else:
                    SwingUtilities.invokeLater(GenericDisposeRunnable(self._popup_d))
            else:
                self._popup_d.setVisible(False)
                if self.fakeJFrame is not None:
                    self._popup_d.dispose()
                    self.fakeJFrame.dispose()
                else:
                    self._popup_d.dispose()

            myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

        def result(self): return self.lResult[0]

        def go(self):
            myPrint("DB", "In MyPopUpDialogBox.", inspect.currentframe().f_code.co_name, "()")
            myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

            class MyPopUpDialogBoxRunnable(Runnable):
                def __init__(self, callingClass):
                    self.callingClass = callingClass

                def run(self):                                                                                          # noqa
                    myPrint("DB", "In MyPopUpDialogBoxRunnable.", inspect.currentframe().f_code.co_name, "()")
                    myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

                    # Create a fake JFrame so we can set the Icons...
                    if self.callingClass.theParent is None:
                        self.callingClass.fakeJFrame = MyJFrame()
                        self.callingClass.fakeJFrame.setName(u"%s_fake_dialog" %(myModuleID))
                        self.callingClass.fakeJFrame.setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE)
                        self.callingClass.fakeJFrame.setUndecorated(True)
                        self.callingClass.fakeJFrame.setVisible(False)
                        if not Platform.isOSX():
                            self.callingClass.fakeJFrame.setIconImage(MDImages.getImage(MD_REF.getSourceInformation().getIconResource()))

                    class MyJDialog(JDialog):
                        def __init__(self, maxSize, *args):
                            self.maxSize = maxSize                                                                      # type: Dimension
                            super(self.__class__, self).__init__(*args)

                        # On Windows, the height was exceeding the screen height when default size of Dimension (0,0), so set the max....
                        def getPreferredSize(self):
                            calcPrefSize = super(self.__class__, self).getPreferredSize()
                            newPrefSize = Dimension(min(calcPrefSize.width, self.maxSize.width), min(calcPrefSize.height, self.maxSize.height))
                            return newPrefSize

                    screenSize = Toolkit.getDefaultToolkit().getScreenSize()

                    if isinstance(self.callingClass.maxSize, Dimension)\
                            and self.callingClass.maxSize.height and self.callingClass.maxSize.width:
                        maxDialogWidth = min(screenSize.width-20, self.callingClass.maxSize.width)
                        maxDialogHeight = min(screenSize.height-40, self.callingClass.maxSize.height)
                        maxDimension = Dimension(maxDialogWidth,maxDialogHeight)
                    else:
                        maxDialogWidth = min(screenSize.width-20, max(GetFirstMainFrame.DEFAULT_MAX_WIDTH, int(round(GetFirstMainFrame.getSize().width *.9,0))))
                        maxDialogHeight = min(screenSize.height-40, max(GetFirstMainFrame.DEFAULT_MAX_WIDTH, int(round(GetFirstMainFrame.getSize().height *.9,0))))
                        maxDimension = Dimension(maxDialogWidth,maxDialogHeight)

                    # noinspection PyUnresolvedReferences
                    self.callingClass._popup_d = MyJDialog(maxDimension,
                                                           self.callingClass.theParent, self.callingClass.theTitle,
                                                           Dialog.ModalityType.APPLICATION_MODAL if (self.callingClass.lModal) else Dialog.ModalityType.MODELESS)

                    self.callingClass._popup_d.getContentPane().setLayout(BorderLayout())
                    self.callingClass._popup_d.setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE)

                    shortcut = Toolkit.getDefaultToolkit().getMenuShortcutKeyMaskEx()

                    # Add standard CMD-W keystrokes etc to close window
                    self.callingClass._popup_d.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_W, shortcut), "close-window")
                    self.callingClass._popup_d.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_F4, shortcut), "close-window")
                    self.callingClass._popup_d.getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0), "close-window")
                    self.callingClass._popup_d.getRootPane().getActionMap().put("close-window", self.callingClass.CancelButtonAction(self.callingClass._popup_d, self.callingClass.fakeJFrame,self.callingClass.lResult))
                    self.callingClass._popup_d.addWindowListener(self.callingClass.WindowListener(self.callingClass._popup_d, self.callingClass.fakeJFrame,self.callingClass.lResult))

                    if (not Platform.isMac()):
                        # MD_REF.getUI().getImages()
                        self.callingClass._popup_d.setIconImage(MDImages.getImage(MD_REF.getSourceInformation().getIconResource()))

                    self.callingClass.messageJText = JTextArea(self.callingClass.theMessage)
                    self.callingClass.messageJText.setFont(getMonoFont())
                    self.callingClass.messageJText.setEditable(False)
                    self.callingClass.messageJText.setLineWrap(False)
                    self.callingClass.messageJText.setWrapStyleWord(False)

                    _popupPanel = JPanel(BorderLayout())
                    _popupPanel.setBorder(EmptyBorder(8, 8, 8, 8))

                    if self.callingClass.theStatus:
                        _statusPnl = JPanel(BorderLayout())
                        self.callingClass.statusLabel = JLabel(self.callingClass.theStatus)
                        self.callingClass.statusLabel.setForeground(getColorBlue())
                        self.callingClass.statusLabel.setBorder(EmptyBorder(8, 0, 8, 0))
                        _popupPanel.add(self.callingClass.statusLabel, BorderLayout.NORTH)

                    myScrollPane = JScrollPane(self.callingClass.messageJText, JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED,JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED)
                    myScrollPane.setWheelScrollingEnabled(True)
                    _popupPanel.add(myScrollPane, BorderLayout.CENTER)

                    buttonPanel = JPanel()
                    if self.callingClass.lModal or self.callingClass.lCancelButton:
                        buttonPanel.setLayout(FlowLayout(FlowLayout.CENTER))

                        if self.callingClass.lCancelButton:
                            cancel_button = JButton("CANCEL")
                            cancel_button.setPreferredSize(Dimension(100,40))
                            cancel_button.setBackground(Color.LIGHT_GRAY)
                            cancel_button.setBorderPainted(False)
                            cancel_button.setOpaque(True)
                            cancel_button.setBorder(EmptyBorder(8, 8, 8, 8))

                            cancel_button.addActionListener(self.callingClass.CancelButtonAction(self.callingClass._popup_d, self.callingClass.fakeJFrame,self.callingClass.lResult) )
                            buttonPanel.add(cancel_button)

                        if self.callingClass.lModal:
                            ok_button = JButton(self.callingClass.OKButtonText)
                            if len(self.callingClass.OKButtonText) <= 2:
                                ok_button.setPreferredSize(Dimension(100,40))
                            else:
                                ok_button.setPreferredSize(Dimension(200,40))

                            ok_button.setBackground(Color.LIGHT_GRAY)
                            ok_button.setBorderPainted(False)
                            ok_button.setOpaque(True)
                            ok_button.setBorder(EmptyBorder(8, 8, 8, 8))
                            ok_button.addActionListener( self.callingClass.OKButtonAction(self.callingClass._popup_d, self.callingClass.fakeJFrame, self.callingClass.lResult) )
                            buttonPanel.add(ok_button)

                        _popupPanel.add(buttonPanel, BorderLayout.SOUTH)

                    if self.callingClass.lAlertLevel >= 2:
                        # internalScrollPane.setBackground(Color.RED)
                        self.callingClass.messageJText.setBackground(Color.RED)
                        self.callingClass.messageJText.setForeground(Color.BLACK)
                        self.callingClass.messageJText.setOpaque(True)
                        _popupPanel.setBackground(Color.RED)
                        _popupPanel.setForeground(Color.BLACK)
                        _popupPanel.setOpaque(True)
                        buttonPanel.setBackground(Color.RED)
                        buttonPanel.setOpaque(True)

                    elif self.callingClass.lAlertLevel >= 1:
                        # internalScrollPane.setBackground(Color.YELLOW)
                        self.callingClass.messageJText.setBackground(Color.YELLOW)
                        self.callingClass.messageJText.setForeground(Color.BLACK)
                        self.callingClass.messageJText.setOpaque(True)
                        _popupPanel.setBackground(Color.YELLOW)
                        _popupPanel.setForeground(Color.BLACK)
                        _popupPanel.setOpaque(True)
                        buttonPanel.setBackground(Color.YELLOW)
                        buttonPanel.setOpaque(True)

                    self.callingClass._popup_d.add(_popupPanel, BorderLayout.CENTER)
                    self.callingClass._popup_d.pack()
                    self.callingClass._popup_d.setLocationRelativeTo(self.callingClass.theParent)
                    self.callingClass._popup_d.setVisible(True)

            if not SwingUtilities.isEventDispatchThread():
                if not self.lModal:
                    myPrint("DB",".. Not running on the EDT, but also NOT Modal, so will .invokeLater::MyPopUpDialogBoxRunnable()...")
                    SwingUtilities.invokeLater(MyPopUpDialogBoxRunnable(self))
                else:
                    myPrint("DB",".. Not running on the EDT so calling .invokeAndWait::MyPopUpDialogBoxRunnable()...")
                    SwingUtilities.invokeAndWait(MyPopUpDialogBoxRunnable(self))
            else:
                myPrint("DB",".. Already on the EDT, just executing::MyPopUpDialogBoxRunnable() now...")
                MyPopUpDialogBoxRunnable(self).run()

            myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

            return self.lResult[0]

    def play_the_money_sound():

        # Seems to cause a crash on Virtual Machine with no Audio - so just in case....
        try:
            if MD_REF.getPreferences().getSetting("beep_on_transaction_change", "y") == "y":
                MD_REF.getUI().getSounds().playSound("cash_register.wav")
        except:
            pass

        return

    def get_filename_addition():

        cal = Calendar.getInstance()
        hhmm = str(10000 + cal.get(11) * 100 + cal.get(12))[1:]
        nameAddition = "-" + str(DateUtil.getStrippedDateInt()) + "-"+hhmm

        return nameAddition

    def check_file_writable(fnm):
        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )
        myPrint("DB","Checking path: ", fnm)

        if os.path.exists(fnm):
            myPrint("DB", "path exists..")
            # path exists
            if os.path.isfile(fnm):  # is it a file or a dir?
                myPrint("DB","path is a file..")
                # also works when file is a link and the target is writable
                return os.access(fnm, os.W_OK)
            else:
                myPrint("DB", "path is not a file..")
                return False  # path is a dir, so cannot write as a file
        # target does not exist, check perms on parent dir
        myPrint("DB","path does not exist...")
        pdir = os.path.dirname(fnm)
        if not pdir: pdir = '.'
        # target is creatable if parent dir is writable
        return os.access(pdir, os.W_OK)

    class ExtFilenameFilter(FilenameFilter):
        """File extension filter for FileDialog"""
        def __init__(self, ext): self.ext = "." + ext.upper()                                                           # noqa

        def accept(self, thedir, filename):                                                                             # noqa
            # type: (File, str) -> bool
            if filename is not None and filename.upper().endswith(self.ext): return True
            return False

    class ExtFileFilterJFC(FileFilter):
        """File extension filter for JFileChooser"""
        def __init__(self, ext): self.ext = "." + ext.upper()

        def getDescription(self): return "*"+self.ext                                                                   # noqa

        def accept(self, _theFile):                                                                                     # noqa
            # type: (File) -> bool
            if _theFile is None: return False
            if _theFile.isDirectory(): return True
            return _theFile.getName().upper().endswith(self.ext)

    def MDDiag():
        myPrint("D", "Moneydance Build:", MD_REF.getVersion(), "Build:", MD_REF.getBuild())


    MDDiag()

    myPrint("DB","System file encoding is:", sys.getfilesystemencoding() )   # Not used, but interesting. Perhaps useful when switching between Windows/Macs and writing files...

    def checkVersions():
        lError = False
        plat_j = platform.system()
        plat_p = platform.python_implementation()
        python_maj = sys.version_info.major
        python_min = sys.version_info.minor

        myPrint("DB","Platform:", plat_p, plat_j, python_maj, ".", python_min)
        myPrint("DB", sys.version)

        if plat_p != "Jython":
            lError = True
            myPrint("DB", "Error: Script requires Jython")
        if plat_j != "Java":
            lError = True
            myPrint("DB", "Error: Script requires Java  base")
        if (python_maj != 2 or python_min != 7):
            lError = True
            myPrint("DB", "\n\nError: Script was  designed on version 2.7. By all means bypass this test and see what happens.....")

        if lError:
            myPrint("J", "Platform version issue - will terminate script!")
            myPrint("P", "\n@@@ TERMINATING PROGRAM @@@\n")
            raise(Exception("Platform version issue - will terminate script!"))

        return not lError


    checkVersions()

    def setDefaultFonts():
        """Grabs the MD defaultText font, reduces default size down to below 18, sets UIManager defaults (if runtime extension, will probably error, so I catch and skip)"""
        if MD_REF_UI is None: return

        # If a runtime extension, then this may fail, depending on timing... Just ignore and return...
        try:
            myFont = MD_REF.getUI().getFonts().defaultText
        except:
            myPrint("B","ERROR trying to call .getUI().getFonts().defaultText - skipping setDefaultFonts()")
            return

        if myFont is None:
            myPrint("B","WARNING: In setDefaultFonts(): calling .getUI().getFonts().defaultText has returned None (but moneydance_ui was set) - skipping setDefaultFonts()")
            return

        if myFont.getSize()>18:
            try:
                myFont = myFont.deriveFont(16.0)
                myPrint("B", "I have reduced the font size down to point-size 16 - Default Fonts are now set to: %s" %(myFont))
            except:
                myPrint("B","ERROR - failed to override font point size down to 16.... will ignore and continue. Font set to: %s" %(myFont))
        else:
            myPrint("DB", "Attempting to set default font to %s" %myFont)

        try:
            UIManager.getLookAndFeelDefaults().put("defaultFont", myFont )

            # https://thebadprogrammer.com/swing-uimanager-keys/
            UIManager.put("CheckBoxMenuItem.acceleratorFont", myFont)
            UIManager.put("Button.font", myFont)
            UIManager.put("ToggleButton.font", myFont)
            UIManager.put("RadioButton.font", myFont)
            UIManager.put("CheckBox.font", myFont)
            UIManager.put("ColorChooser.font", myFont)
            UIManager.put("ComboBox.font", myFont)
            UIManager.put("Label.font", myFont)
            UIManager.put("List.font", myFont)
            UIManager.put("MenuBar.font", myFont)
            UIManager.put("Menu.acceleratorFont", myFont)
            UIManager.put("RadioButtonMenuItem.acceleratorFont", myFont)
            UIManager.put("MenuItem.acceleratorFont", myFont)
            UIManager.put("MenuItem.font", myFont)
            UIManager.put("RadioButtonMenuItem.font", myFont)
            UIManager.put("CheckBoxMenuItem.font", myFont)
            UIManager.put("OptionPane.buttonFont", myFont)
            UIManager.put("OptionPane.messageFont", myFont)
            UIManager.put("Menu.font", myFont)
            UIManager.put("PopupMenu.font", myFont)
            UIManager.put("OptionPane.font", myFont)
            UIManager.put("Panel.font", myFont)
            UIManager.put("ProgressBar.font", myFont)
            UIManager.put("ScrollPane.font", myFont)
            UIManager.put("Viewport.font", myFont)
            UIManager.put("TabbedPane.font", myFont)
            UIManager.put("Slider.font", myFont)
            UIManager.put("Table.font", myFont)
            UIManager.put("TableHeader.font", myFont)
            UIManager.put("TextField.font", myFont)
            UIManager.put("Spinner.font", myFont)
            UIManager.put("PasswordField.font", myFont)
            UIManager.put("TextArea.font", myFont)
            UIManager.put("TextPane.font", myFont)
            UIManager.put("EditorPane.font", myFont)
            UIManager.put("TabbedPane.smallFont", myFont)
            UIManager.put("TitledBorder.font", myFont)
            UIManager.put("ToolBar.font", myFont)
            UIManager.put("ToolTip.font", myFont)
            UIManager.put("Tree.font", myFont)
            UIManager.put("FormattedTextField.font", myFont)
            UIManager.put("IconButton.font", myFont)
            UIManager.put("InternalFrame.optionDialogTitleFont", myFont)
            UIManager.put("InternalFrame.paletteTitleFont", myFont)
            UIManager.put("InternalFrame.titleFont", myFont)
        except:
            myPrint("B","Failed to set Swing default fonts to use Moneydance defaults... sorry")

        myPrint("DB",".setDefaultFonts() successfully executed...")
        return

    setDefaultFonts()

    def who_am_i():
        try: username = System.getProperty("user.name")
        except: username = "???"
        return username

    def getHomeDir():
        # Yup - this can be all over the place...
        myPrint("D", 'System.getProperty("user.dir")', System.getProperty("user.dir"))
        myPrint("D", 'System.getProperty("UserHome")', System.getProperty("UserHome"))
        myPrint("D", 'System.getProperty("user.home")', System.getProperty("user.home"))
        myPrint("D", 'os.path.expanduser("~")', os.path.expanduser("~"))
        myPrint("D", 'os.environ.get("HOMEPATH")', os.environ.get("HOMEPATH"))
        return

    myPrint("D", "I am user:", who_am_i())
    if debug: getHomeDir()

    # noinspection PyArgumentList
    class JTextFieldLimitYN(PlainDocument):

        limit = 10  # Default
        toUpper = False
        what = ""

        def __init__(self, limit, toUpper, what):

            super(PlainDocument, self).__init__()
            self.limit = limit
            self.toUpper = toUpper
            self.what = what

        def insertString(self, myOffset, myString, myAttr):

            if (myString is None): return
            if self.toUpper: myString = myString.upper()
            if (self.what == "YN" and (myString in "YN")) \
                    or (self.what == "DELIM" and (myString in ";|,")) \
                    or (self.what == "1234" and (myString in "1234")) \
                    or (self.what == "CURR"):
                if ((self.getLength() + len(myString)) <= self.limit):
                    super(JTextFieldLimitYN, self).insertString(myOffset, myString, myAttr)                             # noqa

    def fix_delimiter( theDelimiter ):

        try:
            if sys.version_info.major >= 3: return theDelimiter
            if sys.version_info.major <  2: return str(theDelimiter)

            if sys.version_info.minor >  7: return theDelimiter
            if sys.version_info.minor <  7: return str(theDelimiter)

            if sys.version_info.micro >= 2: return theDelimiter
        except:
            pass

        return str( theDelimiter )

    def get_StuWareSoftSystems_parameters_from_file(myFile="StuWareSoftSystems.dict"):
        global debug    # This global for debug must be here as we set it from loaded parameters

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )

        if GlobalVars.resetPickleParameters:
            myPrint("B", "User has specified to reset parameters... keeping defaults and skipping pickle()")
            GlobalVars.parametersLoadedFromFile = {}
            return

        migratedFilename = os.path.join(MD_REF.getCurrentAccountBook().getRootFolder().getAbsolutePath(), myFile)

        myPrint("DB", "Now checking for parameter file:", migratedFilename)

        if os.path.exists(migratedFilename):
            myPrint("DB", "loading parameters from (non-encrypted) Pickle file:", migratedFilename)
            myPrint("DB", "Parameter file", migratedFilename, "exists..")
            # Open the file
            try:
                # Really we should open() the file in binary mode and read/write as binary, then we wouldn't get platform differences!
                istr = FileInputStream(migratedFilename)
                load_file = FileUtil.wrap(istr)
                if not Platform.isWindows():
                    load_string = load_file.read().replace('\r', '')    # This allows for files migrated from windows (strip the extra CR)
                else:
                    load_string = load_file.read()

                GlobalVars.parametersLoadedFromFile = pickle.loads(load_string)
                load_file.close()
            except FileNotFoundException:
                myPrint("B", "Error: failed to find parameter file...")
                GlobalVars.parametersLoadedFromFile = None
            except EOFError:
                myPrint("B", "Error: reached EOF on parameter file....")
                GlobalVars.parametersLoadedFromFile = None
            except:
                myPrint("B", "Error opening Pickle File Unexpected error:", sys.exc_info()[0], "Error:", sys.exc_info()[1], "Line:", sys.exc_info()[2].tb_lineno)
                myPrint("B", ">> Will ignore saved parameters, and create a new file...")
                GlobalVars.parametersLoadedFromFile = None

            if GlobalVars.parametersLoadedFromFile is None:
                GlobalVars.parametersLoadedFromFile = {}
                myPrint("DB","Parameters did NOT load, will use defaults..")
            else:
                myPrint("DB","Parameters successfully loaded from file...")
        else:
            myPrint("DB", "Parameter Pickle file does NOT exist - will use default and create new file..")
            GlobalVars.parametersLoadedFromFile = {}

        if not GlobalVars.parametersLoadedFromFile: return

        myPrint("DB","GlobalVars.parametersLoadedFromFile read from file contains...:")
        for key in sorted(GlobalVars.parametersLoadedFromFile.keys()):
            myPrint("DB","...variable:", key, GlobalVars.parametersLoadedFromFile[key])

        if GlobalVars.parametersLoadedFromFile.get("debug") is not None: debug = GlobalVars.parametersLoadedFromFile.get("debug")

        myPrint("DB","Parameter file loaded if present and GlobalVars.parametersLoadedFromFile{} dictionary set.....")

        # Now load into memory!
        load_StuWareSoftSystems_parameters_into_memory()

        return

    def save_StuWareSoftSystems_parameters_to_file(myFile="StuWareSoftSystems.dict"):
        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )

        if GlobalVars.parametersLoadedFromFile is None: GlobalVars.parametersLoadedFromFile = {}

        # Don't forget, any parameters loaded earlier will be preserved; just add changed variables....
        GlobalVars.parametersLoadedFromFile["__Author"] = "Stuart Beesley - (c) StuWareSoftSystems"
        GlobalVars.parametersLoadedFromFile["debug"] = debug

        dump_StuWareSoftSystems_parameters_from_memory()

        # Pickle was originally encrypted, no need, migrating to unencrypted
        migratedFilename = os.path.join(MD_REF.getCurrentAccountBook().getRootFolder().getAbsolutePath(),myFile)

        myPrint("DB","Will try to save parameter file:", migratedFilename)

        ostr = FileOutputStream(migratedFilename)

        myPrint("DB", "about to Pickle.dump and save parameters to unencrypted file:", migratedFilename)

        try:
            save_file = FileUtil.wrap(ostr)
            pickle.dump(GlobalVars.parametersLoadedFromFile, save_file, protocol=0)
            save_file.close()

            myPrint("DB","GlobalVars.parametersLoadedFromFile now contains...:")
            for key in sorted(GlobalVars.parametersLoadedFromFile.keys()):
                myPrint("DB","...variable:", key, GlobalVars.parametersLoadedFromFile[key])

        except:
            myPrint("B", "Error - failed to create/write parameter file.. Ignoring and continuing.....")
            dump_sys_error_to_md_console_and_errorlog()

            return

        myPrint("DB","Parameter file written and parameters saved to disk.....")

        return

    def get_time_stamp_as_nice_text(timeStamp, _format=None, lUseHHMMSS=True):

        if _format is None: _format = MD_REF.getPreferences().getShortDateFormat()

        humanReadableDate = ""
        try:
            c = Calendar.getInstance()
            c.setTime(Date(timeStamp))
            longHHMMSSText = " HH:mm:ss(.SSS) Z z zzzz" if (lUseHHMMSS) else ""
            dateFormatter = SimpleDateFormat("%s%s" %(_format, longHHMMSSText))
            humanReadableDate = dateFormatter.format(c.getTime())
        except: pass
        return humanReadableDate

    def currentDateTimeMarker():
        c = Calendar.getInstance()
        dateformat = SimpleDateFormat("_yyyyMMdd_HHmmss")
        _datetime = dateformat.format(c.getTime())
        return _datetime

    def destroyOldFrames(moduleName):
        myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()")
        myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))
        frames = JFrame.getFrames()
        for fr in frames:
            if fr.getName().lower().startswith(moduleName+"_"):
                myPrint("DB","Found old frame %s and active status is: %s" %(fr.getName(),fr.isActiveInMoneydance))
                try:
                    fr.isActiveInMoneydance = False
                    if not SwingUtilities.isEventDispatchThread():
                        SwingUtilities.invokeLater(GenericVisibleRunnable(fr, False, False))
                        SwingUtilities.invokeLater(GenericDisposeRunnable(fr))  # This should call windowClosed() which should remove MD listeners.....
                    else:
                        fr.setVisible(False)
                        fr.dispose()            # This should call windowClosed() which should remove MD listeners.....
                    myPrint("DB","disposed of old frame: %s" %(fr.getName()))
                except:
                    myPrint("B","Failed to dispose old frame: %s" %(fr.getName()))
                    dump_sys_error_to_md_console_and_errorlog()

    def classPrinter(className, theObject):
        try:
            text = "Class: %s %s@{:x}".format(System.identityHashCode(theObject)) %(className, theObject.__class__)
        except:
            text = "Error in classPrinter(): %s: %s" %(className, theObject)
        return text

    def getColorBlue():
        # if not isMDThemeDark() and not isMacDarkModeDetected(): return(MD_REF.getUI().getColors().reportBlueFG)
        # return (MD_REF.getUI().getColors().defaultTextForeground)
        return MD_REF.getUI().getColors().reportBlueFG

    def getColorRed(): return (MD_REF.getUI().getColors().errorMessageForeground)

    def getColorDarkGreen(): return (MD_REF.getUI().getColors().budgetHealthyColor)

    def setDisplayStatus(_theStatus, _theColor=None):
        """Sets the Display / Status label on the main diagnostic display: G=Green, B=Blue, R=Red, DG=Dark Green"""

        if GlobalVars.STATUS_LABEL is None or not isinstance(GlobalVars.STATUS_LABEL, JLabel): return

        class SetDisplayStatusRunnable(Runnable):
            def __init__(self, _status, _color):
                self.status = _status; self.color = _color

            def run(self):
                GlobalVars.STATUS_LABEL.setText((_theStatus))
                if self.color is None or self.color == "": self.color = "X"
                self.color = self.color.upper()
                if self.color == "R":    GlobalVars.STATUS_LABEL.setForeground(getColorRed())
                elif self.color == "B":  GlobalVars.STATUS_LABEL.setForeground(getColorBlue())
                elif self.color == "DG": GlobalVars.STATUS_LABEL.setForeground(getColorDarkGreen())
                else:                    GlobalVars.STATUS_LABEL.setForeground(MD_REF.getUI().getColors().defaultTextForeground)

        if not SwingUtilities.isEventDispatchThread():
            SwingUtilities.invokeLater(SetDisplayStatusRunnable(_theStatus, _theColor))
        else:
            SetDisplayStatusRunnable(_theStatus, _theColor).run()

    def setJFileChooserParameters(_jf, lReportOnly=False, lDefaults=False, lPackagesT=None, lApplicationsT=None, lOptionsButton=None, lNewFolderButton=None):
        """sets up Client Properties for JFileChooser() to behave as required >> Mac only"""

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        if not Platform.isOSX(): return
        if not isinstance(_jf, JFileChooser): return

        _PKG = "JFileChooser.packageIsTraversable"
        _APP = "JFileChooser.appBundleIsTraversable"
        _OPTIONS = "JFileChooser.optionsPanelEnabled"
        _NEWFOLDER = "JFileChooser.canCreateDirectories"

        # JFileChooser defaults: https://violetlib.org/vaqua/filechooser.html
        # "JFileChooser.packageIsTraversable"   default False   >> set "true" to allow Packages to be traversed
        # "JFileChooser.appBundleIsTraversable" default False   >> set "true" to allow App Bundles to be traversed
        # "JFileChooser.optionsPanelEnabled"    default False   >> set "true" to allow Options button
        # "JFileChooser.canCreateDirectories"   default False   >> set "true" to allow New Folder button

        if debug or lReportOnly:
            myPrint("B", "Parameters set: ReportOnly: %s, Defaults:%s, PackagesT: %s, ApplicationsT:%s, OptionButton:%s, NewFolderButton: %s" %(lReportOnly, lDefaults, lPackagesT, lApplicationsT, lOptionsButton, lNewFolderButton))
            txt = ("Before setting" if not lReportOnly else "Reporting only")
            for setting in [_PKG, _APP, _OPTIONS, _NEWFOLDER]: myPrint("DB", "%s: '%s': '%s'" %(pad(txt,14), pad(setting,50), _jf.getClientProperty(setting)))
            if lReportOnly: return

        if lDefaults:
            _jf.putClientProperty(_PKG, None)
            _jf.putClientProperty(_APP, None)
            _jf.putClientProperty(_OPTIONS, None)
            _jf.putClientProperty(_NEWFOLDER, None)
        else:
            if lPackagesT       is not None: _jf.putClientProperty(_PKG, lPackagesT)
            if lApplicationsT   is not None: _jf.putClientProperty(_APP, lApplicationsT)
            if lOptionsButton   is not None: _jf.putClientProperty(_OPTIONS, lOptionsButton)
            if lNewFolderButton is not None: _jf.putClientProperty(_NEWFOLDER, lNewFolderButton)

        for setting in [_PKG, _APP, _OPTIONS, _NEWFOLDER]: myPrint("DB", "%s: '%s': '%s'" %(pad("After setting",14), pad(setting,50), _jf.getClientProperty(setting)))

        return

    def setFileDialogParameters(lReportOnly=False, lDefaults=False, lSelectDirectories=None, lPackagesT=None):
        """sets up System Properties for FileDialog() to behave as required >> Mac only"""

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        if not Platform.isOSX(): return

        _TRUE = "true"
        _FALSE = "false"

        _DIRS_FD = "apple.awt.fileDialogForDirectories"        # When True you can select a Folder (rather than a file)
        _PKGS_FD = "apple.awt.use-file-dialog-packages"        # When True allows you to select a 'bundle' as a file; False means navigate inside the bundle
        # "com.apple.macos.use-file-dialog-packages"           # DEPRECATED since Monterrey - discovered this about MD2022.5(4090) - refer: java.desktop/sun/lwawt/macosx/CFileDialog.java

        # FileDialog defaults
        # "apple.awt.fileDialogForDirectories"       default "false" >> set "true"  to allow Directories to be selected
        # "apple.awt.use-file-dialog-packages"       default "true"  >> set "false" to allow access to Mac 'packages'

        if debug or lReportOnly:
            myPrint("B", "Parameters set: ReportOnly: %s, Defaults:%s, SelectDirectories:%s, PackagesT:%s" % (lReportOnly, lDefaults, lSelectDirectories, lPackagesT))
            txt = ("Before setting" if not lReportOnly else "Reporting only")
            for setting in [_DIRS_FD, _PKGS_FD]: myPrint("DB", "%s: '%s': '%s'" %(pad(txt,14), pad(setting,50), System.getProperty(setting)))
            if lReportOnly: return

        if lDefaults:
            System.setProperty(_DIRS_FD,_FALSE)
            System.setProperty(_PKGS_FD,_TRUE)
        else:
            if lSelectDirectories is not None: System.setProperty(_DIRS_FD, (_TRUE if lSelectDirectories   else _FALSE))
            if lPackagesT         is not None: System.setProperty(_PKGS_FD, (_TRUE if lPackagesT           else _FALSE))

        for setting in [_DIRS_FD, _PKGS_FD]: myPrint("DB", "After setting:  '%s': '%s'" %(pad(setting,50), System.getProperty(setting)))

        return

    def getFileFromFileChooser(fileChooser_parent,                  # The Parent Frame, or None
                               fileChooser_starting_dir,            # The Starting Dir
                               fileChooser_filename,                # Default filename (or None)
                               fileChooser_title,                   # The Title (with FileDialog, only works on SAVE)
                               fileChooser_multiMode,               # Normally False (True has not been coded!)
                               fileChooser_open,                    # True for Open/Load, False for Save
                               fileChooser_selectFiles,             # True for files, False for Directories
                               fileChooser_OK_text,                 # Normally None, unless set - use text
                               fileChooser_fileFilterText=None,     # E.g. "txt" or "qif"
                               lForceJFC=False,
                               lForceFD=False,
                               lAllowTraversePackages=None,
                               lAllowTraverseApplications=None,     # JFileChooser only..
                               lAllowNewFolderButton=True,          # JFileChooser only..
                               lAllowOptionsButton=None):           # JFileChooser only..
        """Launches FileDialog on Mac, or JFileChooser on other platforms... NOTE: Do not use Filter on Macs!"""

        _THIS_METHOD_NAME = "Dynamic File Chooser"

        if fileChooser_multiMode:
            myPrint("B","@@ SORRY Multi File Selection Mode has not been coded! Exiting...")
            return None

        if fileChooser_starting_dir is None or fileChooser_starting_dir == "" or not os.path.exists(fileChooser_starting_dir):
            fileChooser_starting_dir = MD_REF.getPreferences().getSetting("gen.data_dir", None)

        if fileChooser_starting_dir is None or not os.path.exists(fileChooser_starting_dir):
            fileChooser_starting_dir = None
            myPrint("B","ERROR: Starting Path does not exist - will start with no starting path set..")

        else:
            myPrint("DB", "Preparing the Dynamic File Chooser with path: %s" %(fileChooser_starting_dir))
            if Platform.isOSX() and "/Library/Containers/" in fileChooser_starting_dir:
                myPrint("DB", "WARNING: Folder will be restricted by MacOSx...")
                if not lForceJFC:
                    txt = ("FileDialog: MacOSx restricts Java Access to 'special' locations like 'Library\n"
                          "Folder: %s\n"
                          "Please navigate to this location manually in the next popup. This grants permission"
                          %(fileChooser_starting_dir))
                else:
                    txt = ("JFileChooser: MacOSx restricts Java Access to 'special' locations like 'Library\n"
                          "Folder: %s\n"
                          "Your files will probably be hidden.. If so, switch to FileDialog()...(contact author)"
                          %(fileChooser_starting_dir))
                MyPopUpDialogBox(fileChooser_parent,
                                 "NOTE: Mac Security Restriction",
                                 txt,
                                 theTitle=_THIS_METHOD_NAME,
                                 lAlertLevel=1).go()

        if (Platform.isOSX() and not lForceJFC) or lForceFD:

            setFileDialogParameters(lPackagesT=lAllowTraversePackages, lSelectDirectories=(not fileChooser_selectFiles))

            myPrint("DB", "Preparing FileDialog() with path: %s" %(fileChooser_starting_dir))
            if fileChooser_filename is not None: myPrint("DB", "... and filename:                 %s" %(fileChooser_filename))

            fileDialog = FileDialog(fileChooser_parent, fileChooser_title)

            fileDialog.setTitle(fileChooser_title)

            if fileChooser_starting_dir is not None:    fileDialog.setDirectory(fileChooser_starting_dir)
            if fileChooser_filename is not None:        fileDialog.setFile(fileChooser_filename)

            fileDialog.setMultipleMode(fileChooser_multiMode)

            if fileChooser_open:
                fileDialog.setMode(FileDialog.LOAD)
            else:
                fileDialog.setMode(FileDialog.SAVE)

            # if fileChooser_fileFilterText is not None and (not Platform.isOSX() or not Platform.isOSXVersionAtLeast("10.13")):
            if fileChooser_fileFilterText is not None and (not Platform.isOSX() or isOSXVersionMontereyOrLater()):
                myPrint("DB",".. Adding file filter for: %s" %(fileChooser_fileFilterText))
                fileDialog.setFilenameFilter(ExtFilenameFilter(fileChooser_fileFilterText))

            fileDialog.setVisible(True)

            setFileDialogParameters(lDefaults=True)

            myPrint("DB", "FileDialog returned File:      %s" %(fileDialog.getFile()))
            myPrint("DB", "FileDialog returned Directory: %s" %(fileDialog.getDirectory()))

            if fileDialog.getFile() is None or fileDialog.getFile() == "": return None

            _theFile = os.path.join(fileDialog.getDirectory(), fileDialog.getFile())

        else:

            myPrint("DB", "Preparing JFileChooser() with path: %s" %(fileChooser_starting_dir))
            if fileChooser_filename is not None: myPrint("DB", "... and filename:                   %s" %(fileChooser_filename))

            if fileChooser_starting_dir is not None:
                jfc = JFileChooser(fileChooser_starting_dir)
            else:
                jfc = JFileChooser()

            if fileChooser_filename is not None: jfc.setSelectedFile(File(fileChooser_filename))
            setJFileChooserParameters(jfc,
                                      lPackagesT=lAllowTraversePackages,
                                      lApplicationsT=lAllowTraverseApplications,
                                      lNewFolderButton=lAllowNewFolderButton,
                                      lOptionsButton=lAllowOptionsButton)

            jfc.setDialogTitle(fileChooser_title)
            jfc.setMultiSelectionEnabled(fileChooser_multiMode)

            if fileChooser_selectFiles:
                jfc.setFileSelectionMode(JFileChooser.FILES_ONLY)         # FILES_ONLY, DIRECTORIES_ONLY, FILES_AND_DIRECTORIES
            else:
                jfc.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY)   # FILES_ONLY, DIRECTORIES_ONLY, FILES_AND_DIRECTORIES

            # if fileChooser_fileFilterText is not None and (not Platform.isOSX() or not Platform.isOSXVersionAtLeast("10.13")):
            if fileChooser_fileFilterText is not None and (not Platform.isOSX() or isOSXVersionMontereyOrLater()):
                myPrint("DB",".. Adding file filter for: %s" %(fileChooser_fileFilterText))
                jfc.setFileFilter(ExtFileFilterJFC(fileChooser_fileFilterText))

            if fileChooser_OK_text is not None:
                returnValue = jfc.showDialog(fileChooser_parent, fileChooser_OK_text)
            else:
                if fileChooser_open:
                    returnValue = jfc.showOpenDialog(fileChooser_parent)
                else:
                    returnValue = jfc.showSaveDialog(fileChooser_parent)

            if returnValue == JFileChooser.CANCEL_OPTION \
                    or (jfc.getSelectedFile() is None or jfc.getSelectedFile().getName()==""):
                myPrint("DB","JFileChooser was cancelled by user, or no file was selected...")
                return None

            _theFile = jfc.getSelectedFile().getAbsolutePath()
            myPrint("DB","JFileChooser returned File/path..: %s" %(_theFile))

        myPrint("DB","...File/path exists..: %s" %(os.path.exists(_theFile)))
        return _theFile

    class RequestFocusListener(AncestorListener):
        """Add this Listener to a JTextField by using .addAncestorListener(RequestFocusListener()) before calling JOptionPane.showOptionDialog()"""

        def __init__(self, removeListener=True):
            self.removeListener = removeListener

        def ancestorAdded(self, e):
            component = e.getComponent()
            component.requestFocusInWindow()
            component.selectAll()
            if (self.removeListener): component.removeAncestorListener(self)

        def ancestorMoved(self, e): pass
        def ancestorRemoved(self, e): pass

    class SearchAction(AbstractAction):

        def __init__(self, theFrame, searchJText):
            self.theFrame = theFrame
            self.searchJText = searchJText
            self.lastSearch = ""
            self.lastPosn = -1
            self.previousEndPosn = -1
            self.lastDirection = 0

        def actionPerformed(self, event):
            myPrint("D","in SearchAction(), Event: ", event)

            p = JPanel(FlowLayout())
            lbl = JLabel("Enter the search text:")
            tf = JTextField(self.lastSearch,20)
            p.add(lbl)
            p.add(tf)

            tf.addAncestorListener(RequestFocusListener())

            _search_options = [ "Next", "Previous", "Cancel" ]

            defaultDirection = _search_options[self.lastDirection]

            response = JOptionPane.showOptionDialog(self.theFrame,
                                                    p,
                                                    "Search for text",
                                                    JOptionPane.OK_CANCEL_OPTION,
                                                    JOptionPane.QUESTION_MESSAGE,
                                                    getMDIcon(None),
                                                    _search_options,
                                                    defaultDirection)

            lSwitch = False
            if (response == 0 or response == 1):
                if response != self.lastDirection: lSwitch = True
                self.lastDirection = response
                searchWhat = tf.getText()
            else:
                searchWhat = None

            del p, lbl, tf, _search_options

            if not searchWhat or searchWhat == "": return

            theText = self.searchJText.getText().lower()
            highlighter = self.searchJText.getHighlighter()
            highlighter.removeAllHighlights()

            startPos = 0

            if response == 0:
                direction = "[forwards]"
                if searchWhat == self.lastSearch:
                    startPos = self.lastPosn
                    if lSwitch: startPos=startPos+len(searchWhat)+1
                self.lastSearch = searchWhat

                # if startPos+len(searchWhat) >= len(theText):
                #     startPos = 0
                #
                pos = theText.find(searchWhat.lower(),startPos)     # noqa
                myPrint("DB", "Search %s Pos: %s, searchWhat: '%s', startPos: %s, endPos: %s" %(direction, pos, searchWhat,startPos, -1))

            else:
                direction = "[backwards]"
                endPos = len(theText)-1

                if searchWhat == self.lastSearch:
                    if self.previousEndPosn < 0: self.previousEndPosn = len(theText)-1
                    endPos = max(0,self.previousEndPosn)
                    if lSwitch: endPos = max(0,self.lastPosn-1)

                self.lastSearch = searchWhat

                pos = theText.rfind(searchWhat.lower(),startPos,endPos)     # noqa
                myPrint("DB", "Search %s Pos: %s, searchWhat: '%s', startPos: %s, endPos: %s" %(direction, pos, searchWhat,startPos,endPos))

            if pos >= 0:
                self.searchJText.setCaretPosition(pos)
                try:
                    highlighter.addHighlight(pos,min(pos+len(searchWhat),len(theText)),DefaultHighlighter.DefaultPainter)
                except: pass
                if response == 0:
                    self.lastPosn = pos+len(searchWhat)
                    self.previousEndPosn = len(theText)-1
                else:
                    self.lastPosn = pos-len(searchWhat)
                    self.previousEndPosn = pos-1
            else:
                self.lastPosn = 0
                self.previousEndPosn = len(theText)-1
                myPopupInformationBox(self.theFrame,"Searching %s text not found" %direction)

            return

    def saveOutputFile(_theFrame, _theTitle, _fileName, _theText):

        theTitle = "Select location to save the current displayed output... (CANCEL=ABORT)"
        copyToFile = getFileFromFileChooser(_theFrame,          # Parent frame or None
                                            get_home_dir(),     # Starting path
                                            _fileName,          # Default Filename
                                            theTitle,           # Title
                                            False,              # Multi-file selection mode
                                            False,              # True for Open/Load, False for Save
                                            True,               # True = Files, else Dirs
                                            None,               # Load/Save button text, None for defaults
                                            "txt",              # File filter (non Mac only). Example: "txt" or "qif"
                                            lAllowTraversePackages=False,
                                            lForceJFC=False,
                                            lForceFD=True,
                                            lAllowNewFolderButton=True,
                                            lAllowOptionsButton=True)

        if copyToFile is None or copyToFile == "":
            return
        elif not safeStr(copyToFile).endswith(".txt"):
            myPopupInformationBox(_theFrame, "Sorry - please use a .txt file extension when saving output txt")
            return
        elif ".moneydance" in os.path.dirname(copyToFile):
            myPopupInformationBox(_theFrame, "Sorry, please choose a location outside of the Moneydance location")
            return

        if not check_file_writable(copyToFile):
            myPopupInformationBox(_theFrame, "Sorry, that file/location does not appear allowed by the operating system!?")

        toFile = copyToFile
        try:
            with open(toFile, 'w') as f: f.write(_theText)
            myPrint("B", "%s: text output copied to: %s" %(_theTitle, toFile))

            if os.path.exists(toFile):
                play_the_money_sound()
                txt = "%s: Output text saved as requested to: %s" %(_theTitle, toFile)
                setDisplayStatus(txt, "B")
                myPopupInformationBox(_theFrame, txt)
            else:
                txt = "ERROR - failed to write output text to file: %s" %(toFile)
                myPrint("B", txt)
                myPopupInformationBox(_theFrame, txt)
        except:
            txt = "ERROR - failed to write output text to file: %s" %(toFile)
            dump_sys_error_to_md_console_and_errorlog()
            myPopupInformationBox(_theFrame, txt)

        return

    if MD_REF_UI is not None:       # Only action if the UI is loaded - e.g. scripts (not run time extensions)
        try: GlobalVars.defaultPrintFontSize = eval("MD_REF.getUI().getFonts().print.getSize()")   # Do this here as MD_REF disappears after script ends...
        except: GlobalVars.defaultPrintFontSize = 12
    else:
        GlobalVars.defaultPrintFontSize = 12

    ####################################################################################################################
    # PRINTING UTILITIES...: Points to MM, to Inches, to Resolution: Conversion routines etc
    _IN2MM = 25.4; _IN2CM = 2.54; _IN2PT = 72
    def pt2dpi(_pt,_resolution):    return _pt * _resolution / _IN2PT
    def mm2pt(_mm):                 return _mm * _IN2PT / _IN2MM
    def mm2mpt(_mm):                return _mm * 1000 * _IN2PT / _IN2MM
    def pt2mm(_pt):                 return round(_pt * _IN2MM / _IN2PT, 1)
    def mm2in(_mm):                 return _mm / _IN2MM
    def in2mm(_in):                 return _in * _IN2MM
    def in2mpt(_in):                return _in * _IN2PT * 1000
    def in2pt(_in):                 return _in * _IN2PT
    def mpt2in(_mpt):               return _mpt / _IN2PT / 1000
    def mm2px(_mm, _resolution):    return mm2in(_mm) * _resolution
    def mpt2px(_mpt, _resolution):  return mpt2in(_mpt) * _resolution

    def printDeducePrintableWidth(_thePageFormat, _pAttrs):

        _BUFFER_PCT = 0.95

        myPrint("DB", "PageFormat after user dialog: Portrait=%s Landscape=%s W: %sMM(%spts) H: %sMM(%spts) Paper: %s Paper W: %sMM(%spts) H: %sMM(%spts)"
                %(_thePageFormat.getOrientation()==_thePageFormat.PORTRAIT, _thePageFormat.getOrientation()==_thePageFormat.LANDSCAPE,
                  pt2mm(_thePageFormat.getWidth()),_thePageFormat.getWidth(), pt2mm(_thePageFormat.getHeight()),_thePageFormat.getHeight(),
                  _thePageFormat.getPaper(),
                  pt2mm(_thePageFormat.getPaper().getWidth()), _thePageFormat.getPaper().getWidth(), pt2mm(_thePageFormat.getPaper().getHeight()), _thePageFormat.getPaper().getHeight()))

        if _pAttrs.get(attribute.standard.MediaSizeName):
            myPrint("DB", "Requested Media: %s" %(_pAttrs.get(attribute.standard.MediaSizeName)))

        if not _pAttrs.get(attribute.standard.MediaPrintableArea):
            raise Exception("ERROR: MediaPrintableArea not present in pAttrs!?")

        mediaPA = _pAttrs.get(attribute.standard.MediaPrintableArea)
        myPrint("DB", "MediaPrintableArea settings from Printer Attributes..: w%sMM h%sMM MediaPrintableArea: %s, getPrintableArea: %s "
                % (mediaPA.getWidth(attribute.standard.MediaPrintableArea.MM),
                   mediaPA.getHeight(attribute.standard.MediaPrintableArea.MM),
                   mediaPA, mediaPA.getPrintableArea(attribute.standard.MediaPrintableArea.MM)))

        if (_thePageFormat.getOrientation()==_thePageFormat.PORTRAIT):
            deducedWidthMM = mediaPA.getWidth(attribute.standard.MediaPrintableArea.MM)
        elif (_thePageFormat.getOrientation()==_thePageFormat.LANDSCAPE):
            deducedWidthMM = mediaPA.getHeight(attribute.standard.MediaPrintableArea.MM)
        else:
            raise Exception("ERROR: thePageFormat.getOrientation() was not PORTRAIT or LANDSCAPE!?")

        myPrint("DB","Paper Orientation: %s" %("LANDSCAPE" if _thePageFormat.getOrientation()==_thePageFormat.LANDSCAPE else "PORTRAIT"))

        _maxPaperWidthPTS = mm2px(deducedWidthMM, GlobalVars.defaultDPI)
        _maxPaperWidthPTS_buff = _maxPaperWidthPTS * _BUFFER_PCT

        myPrint("DB", "MediaPrintableArea: deduced printable width: %sMM(%sPTS) (using factor of *%s = %sPTS)" %(round(deducedWidthMM,1), round(_maxPaperWidthPTS,1), _BUFFER_PCT, _maxPaperWidthPTS_buff))
        return deducedWidthMM, _maxPaperWidthPTS, _maxPaperWidthPTS_buff

    def loadDefaultPrinterAttributes(_pAttrs=None):

        if _pAttrs is None:
            _pAttrs = attribute.HashPrintRequestAttributeSet()
        else:
            _pAttrs.clear()

        # Refer: https://docs.oracle.com/javase/7/docs/api/javax/print/attribute/standard/package-summary.html
        _pAttrs.add(attribute.standard.DialogTypeSelection.NATIVE)
        if GlobalVars.defaultPrintLandscape:
            _pAttrs.add(attribute.standard.OrientationRequested.LANDSCAPE)
        else:
            _pAttrs.add(attribute.standard.OrientationRequested.PORTRAIT)
        _pAttrs.add(attribute.standard.Chromaticity.MONOCHROME)
        _pAttrs.add(attribute.standard.JobSheets.NONE)
        _pAttrs.add(attribute.standard.Copies(1))
        _pAttrs.add(attribute.standard.PrintQuality.NORMAL)

        return _pAttrs

    def printOutputFile(_callingClass=None, _theTitle=None, _theJText=None, _theString=None):

        # Possible future modification, leverage MDPrinter, and it's classes / methods to save/load preferences and create printers
        try:
            if _theJText is None and _theString is None: return
            if _theJText is not None and len(_theJText.getText()) < 1: return
            if _theString is not None and len(_theString) < 1: return

            # Make a new one for printing
            if _theJText is not None:
                printJTextArea = JTextArea(_theJText.getText())
            else:
                printJTextArea = JTextArea(_theString)

            printJTextArea.setEditable(False)
            printJTextArea.setLineWrap(True)    # As we are reducing the font size so that the width fits the page width, this forces any remainder to wrap
            # if _callingClass is not None: printJTextArea.setLineWrap(_callingClass.lWrapText)  # Mirror the word wrap set by user
            printJTextArea.setWrapStyleWord(False)
            printJTextArea.setOpaque(False); printJTextArea.setBackground(Color(0,0,0,0)); printJTextArea.setForeground(Color.BLACK)
            printJTextArea.setBorder(EmptyBorder(0, 0, 0, 0))

            # IntelliJ doesnt like the use of 'print' (as it's a keyword)
            try:
                if checkObjectInNameSpace("MD_REF"):
                    usePrintFontSize = eval("MD_REF.getUI().getFonts().print.getSize()")
                elif checkObjectInNameSpace("moneydance"):
                    usePrintFontSize = eval("moneydance.getUI().getFonts().print.getSize()")
                else:
                    usePrintFontSize = GlobalVars.defaultPrintFontSize  # Just in case cleanup_references() has tidied up once script ended
            except:
                usePrintFontSize = 12   # Font print did not exist before build 3036

            theFontToUse = getMonoFont()       # Need Monospaced font, but with the font set in MD preferences for print
            theFontToUse = theFontToUse.deriveFont(float(usePrintFontSize))
            printJTextArea.setFont(theFontToUse)

            def computeFontSize(_theComponent, _maxPaperWidth, _dpi):

                # Auto shrink font so that text fits on one line when printing
                # Note: Java seems to operate it's maths at 72DPI (so must factor that into the maths)
                try:
                    _DEFAULT_MIN_WIDTH = mm2px(100, _dpi)   # 100MM
                    _minFontSize = 5                        # Below 5 too small
                    theString = _theComponent.getText()
                    _startingComponentFont = _theComponent.getFont()

                    if not theString or len(theString) < 1: return -1

                    fm = _theComponent.getFontMetrics(_startingComponentFont)
                    _maxFontSize = curFontSize = _startingComponentFont.getSize()   # Max out at the MD default for print font size saved in preferences
                    myPrint("DB","Print - starting font:", _startingComponentFont)
                    myPrint("DB","... calculating.... The starting/max font size is:", curFontSize)

                    maxLineWidthInFile = _DEFAULT_MIN_WIDTH
                    longestLine = ""
                    for line in theString.split("\n"):              # Look for the widest line adjusted for font style
                        _w = pt2dpi(fm.stringWidth(line), _dpi)
                        # myPrint("DB", "Found line (len: %s):" %(len(line)), line)
                        # myPrint("DB", "...calculated length metrics: %s/%sPTS (%sMM)" %(fm.stringWidth(line), _w, pt2mm(_w)))
                        if _w > maxLineWidthInFile:
                            longestLine = line
                            maxLineWidthInFile = _w
                    myPrint("DB","longest line width %s chars; maxLineWidthInFile now: %sPTS (%sMM)" %(len(longestLine),maxLineWidthInFile, pt2mm(maxLineWidthInFile)))

                    # Now shrink the font size to fit.....
                    while (pt2dpi(fm.stringWidth(longestLine) + 5,_dpi) > _maxPaperWidth):
                        myPrint("DB","At font size: %s; (pt2dpi(fm.stringWidth(longestLine) + 5,_dpi):" %(curFontSize), (pt2dpi(fm.stringWidth(longestLine) + 5,_dpi)), pt2mm(pt2dpi(fm.stringWidth(longestLine) + 5,_dpi)), "MM", " >> max width:", _maxPaperWidth)
                        curFontSize -= 1
                        fm = _theComponent.getFontMetrics(Font(_startingComponentFont.getName(), _startingComponentFont.getStyle(), curFontSize))
                        myPrint("DB","... next will be: at font size: %s; (pt2dpi(fm.stringWidth(longestLine) + 5,_dpi):" %(curFontSize), (pt2dpi(fm.stringWidth(longestLine) + 5,_dpi)), pt2mm(pt2dpi(fm.stringWidth(longestLine) + 5,_dpi)), "MM")

                        myPrint("DB","... calculating.... length of line still too long... reducing font size to:", curFontSize)
                        if curFontSize < _minFontSize:
                            myPrint("DB","... calculating... Next font size is too small... exiting the reduction loop...")
                            break

                    if not Platform.isMac():
                        curFontSize -= 1   # For some reason, sometimes on Linux/Windows still too big....
                        myPrint("DB","..knocking 1 off font size for good luck...! Now: %s" %(curFontSize))

                    # Code to increase width....
                    # while (pt2dpi(fm.stringWidth(theString) + 5,_dpi) < _maxPaperWidth):
                    #     curSize += 1
                    #     fm = _theComponent.getFontMetrics(Font(_startingComponentFont.getName(), _startingComponentFont.getStyle(), curSize))

                    curFontSize = max(_minFontSize, curFontSize); curFontSize = min(_maxFontSize, curFontSize)
                    myPrint("DB","... calculating.... Adjusted final font size to:", curFontSize)

                except:
                    myPrint("B", "ERROR: computeFontSize() crashed?"); dump_sys_error_to_md_console_and_errorlog()
                    return -1
                return curFontSize

            myPrint("DB", "Creating new PrinterJob...")
            printer_job = PrinterJob.getPrinterJob()

            if GlobalVars.defaultPrintService is not None:
                printer_job.setPrintService(GlobalVars.defaultPrintService)
                myPrint("DB","Assigned remembered PrintService...: %s" %(printer_job.getPrintService()))

            if GlobalVars.defaultPrinterAttributes is not None:
                pAttrs = attribute.HashPrintRequestAttributeSet(GlobalVars.defaultPrinterAttributes)
            else:
                pAttrs = loadDefaultPrinterAttributes(None)

            pAttrs.remove(attribute.standard.JobName)
            pAttrs.add(attribute.standard.JobName("%s: %s" %(myModuleID.capitalize(), _theTitle), None))

            if GlobalVars.defaultDPI != 72:
                pAttrs.remove(attribute.standard.PrinterResolution)
                pAttrs.add(attribute.standard.PrinterResolution(GlobalVars.defaultDPI, GlobalVars.defaultDPI, attribute.standard.PrinterResolution.DPI))

            for atr in pAttrs.toArray(): myPrint("DB", "Printer attributes before user dialog: %s:%s" %(atr.getName(), atr))

            if not printer_job.printDialog(pAttrs):
                myPrint("DB","User aborted the Print Dialog setup screen, so exiting...")
                return

            selectedPrintService = printer_job.getPrintService()
            myPrint("DB", "User selected print service:", selectedPrintService)

            thePageFormat = printer_job.getPageFormat(pAttrs)

            # .setPrintable() seems to modify pAttrs & adds MediaPrintableArea. Do this before printDeducePrintableWidth()
            header = MessageFormat(_theTitle)
            footer = MessageFormat("- page {0} -")
            printer_job.setPrintable(printJTextArea.getPrintable(header, footer), thePageFormat)    # Yes - we do this twice

            for atr in pAttrs.toArray(): myPrint("DB", "Printer attributes **AFTER** user dialog (and setPrintable): %s:%s" %(atr.getName(), atr))

            deducedWidthMM, maxPaperWidthPTS, maxPaperWidthPTS_buff = printDeducePrintableWidth(thePageFormat, pAttrs)

            if _callingClass is None or not _callingClass.lWrapText:

                newFontSize = computeFontSize(printJTextArea, int(maxPaperWidthPTS), GlobalVars.defaultDPI)

                if newFontSize > 0:
                    theFontToUse = theFontToUse.deriveFont(float(newFontSize))
                    printJTextArea.setFont(theFontToUse)

            # avoiding Intellij errors
            # eval("printJTextArea.print(header, footer, False, selectedPrintService, pAttrs, True)")  # If you do this, then native features like print to PDF will get ignored - so print via PrinterJob

            # Yup - calling .setPrintable() twice - before and after .computeFontSize()
            printer_job.setPrintable(printJTextArea.getPrintable(header, footer), thePageFormat)
            eval("printer_job.print(pAttrs)")

            del printJTextArea

            myPrint("DB", "Saving current print service:", printer_job.getPrintService())
            GlobalVars.defaultPrinterAttributes = attribute.HashPrintRequestAttributeSet(pAttrs)
            GlobalVars.defaultPrintService = printer_job.getPrintService()

        except:
            myPrint("B", "ERROR in printing routines.....:"); dump_sys_error_to_md_console_and_errorlog()
        return

    def pageSetup():

        myPrint("DB","Printer Page setup routines..:")

        myPrint("DB", 'NOTE: A4        210mm x 297mm	8.3" x 11.7"	Points: w595 x h842')
        myPrint("DB", 'NOTE: Letter    216mm x 279mm	8.5" x 11.0"	Points: w612 x h791')

        pj = PrinterJob.getPrinterJob()

        # Note: PrintService is not used/remembered/set by .pageDialog

        if GlobalVars.defaultPrinterAttributes is not None:
            pAttrs = attribute.HashPrintRequestAttributeSet(GlobalVars.defaultPrinterAttributes)
        else:
            pAttrs = loadDefaultPrinterAttributes(None)

        for atr in pAttrs.toArray(): myPrint("DB", "Printer attributes before Page Setup: %s:%s" %(atr.getName(), atr))

        if not pj.pageDialog(pAttrs):
            myPrint("DB", "User cancelled Page Setup - exiting...")
            return

        for atr in pAttrs.toArray(): myPrint("DB", "Printer attributes **AFTER** Page Setup: %s:%s" %(atr.getName(), atr))

        if debug: printDeducePrintableWidth(pj.getPageFormat(pAttrs), pAttrs)

        myPrint("DB", "Printer selected: %s" %(pj.getPrintService()))

        GlobalVars.defaultPrinterAttributes = attribute.HashPrintRequestAttributeSet(pAttrs)
        myPrint("DB", "Printer Attributes saved....")

        return

    class SetupMDColors:

        OPAQUE = None
        FOREGROUND = None
        FOREGROUND_REVERSED = None
        BACKGROUND = None
        BACKGROUND_REVERSED = None

        def __init__(self): raise Exception("ERROR - Should not create instance of this class!")

        @staticmethod
        def updateUI():
            myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()")

            SetupMDColors.OPAQUE = False

            SetupMDColors.FOREGROUND = GlobalVars.CONTEXT.getUI().getColors().defaultTextForeground
            SetupMDColors.FOREGROUND_REVERSED = SetupMDColors.FOREGROUND

            SetupMDColors.BACKGROUND = GlobalVars.CONTEXT.getUI().getColors().defaultBackground
            SetupMDColors.BACKGROUND_REVERSED = SetupMDColors.BACKGROUND

            if ((not isMDThemeVAQua() and not isMDThemeDark() and isMacDarkModeDetected())
                    or (not isMacDarkModeDetected() and isMDThemeDarcula())):
                SetupMDColors.FOREGROUND_REVERSED = GlobalVars.CONTEXT.getUI().colors.defaultBackground
                SetupMDColors.BACKGROUND_REVERSED = GlobalVars.CONTEXT.getUI().colors.defaultTextForeground

    global ManuallyCloseAndReloadDataset            # Declare it for QuickJFrame/IDE, but not present in common code. Other code will ignore it

    class GetFirstMainFrame:

        DEFAULT_MAX_WIDTH = 1024
        DEFAULT_MAX_HEIGHT = 768

        def __init__(self): raise Exception("ERROR: DO NOT CREATE INSTANCE OF GetFirstMainFrame!")

        @staticmethod
        def getSize(defaultWidth=None, defaultHeight=None):
            if defaultWidth is None: defaultWidth = GetFirstMainFrame.DEFAULT_MAX_WIDTH
            if defaultHeight is None: defaultHeight = GetFirstMainFrame.DEFAULT_MAX_HEIGHT
            try:
                firstMainFrame = MD_REF.getUI().firstMainFrame
                return firstMainFrame.getSize()
            except: pass
            return Dimension(defaultWidth, defaultHeight)

        @staticmethod
        def getSelectedAccount():
            try:
                firstMainFrame = MD_REF.getUI().firstMainFrame
                return firstMainFrame.getSelectedAccount()
            except: pass
            return None

    class QuickJFrame():

        def __init__(self,
                     title,
                     output,
                     lAlertLevel=0,
                     copyToClipboard=False,
                     lJumpToEnd=False,
                     lWrapText=True,
                     lQuitMDAfterClose=False,
                     lRestartMDAfterClose=False,
                     screenLocation=None,
                     lAutoSize=False):
            self.title = title
            self.output = output
            self.lAlertLevel = lAlertLevel
            self.returnFrame = None
            self.copyToClipboard = copyToClipboard
            self.lJumpToEnd = lJumpToEnd
            self.lWrapText = lWrapText
            self.lQuitMDAfterClose = lQuitMDAfterClose
            self.lRestartMDAfterClose = lRestartMDAfterClose
            self.screenLocation = screenLocation
            self.lAutoSize = lAutoSize
            # if Platform.isOSX() and int(float(MD_REF.getBuild())) >= 3039: self.lAlertLevel = 0    # Colors don't work on Mac since VAQua
            if isMDThemeDark() or isMacDarkModeDetected(): self.lAlertLevel = 0

        class QJFWindowListener(WindowAdapter):

            def __init__(self, theFrame, lQuitMDAfterClose=False, lRestartMDAfterClose=False):
                self.theFrame = theFrame
                self.lQuitMDAfterClose = lQuitMDAfterClose
                self.lRestartMDAfterClose = lRestartMDAfterClose
                self.saveMD_REF = MD_REF

            def windowClosing(self, WindowEvent):                                                                       # noqa
                myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", WindowEvent)
                myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

                myPrint("DB", "QuickJFrame() Frame shutting down.... Calling .dispose()")
                self.theFrame.dispose()

                myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

            def windowClosed(self, WindowEvent):                                                                       # noqa
                myPrint("DB","In ", inspect.currentframe().f_code.co_name, "()")
                myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

                if self.lQuitMDAfterClose or self.lRestartMDAfterClose:
                    if "ManuallyCloseAndReloadDataset" not in globals():
                        myPrint("DB", "'ManuallyCloseAndReloadDataset' not in globals(), so just exiting MD the easy way...")
                        myPrint("B", "@@ EXITING MONEYDANCE @@")
                        MD_REF.getUI().exit()
                    else:
                        if self.lQuitMDAfterClose:
                            myPrint("B", "Quit MD after Close triggered... Now quitting MD")
                            ManuallyCloseAndReloadDataset.moneydanceExitOrRestart(lRestart=False)
                        elif self.lRestartMDAfterClose:
                            myPrint("B", "Restart MD after Close triggered... Now restarting MD")
                            ManuallyCloseAndReloadDataset.moneydanceExitOrRestart(lRestart=True)
                else:
                    myPrint("DB", "FYI No Quit MD after Close triggered... So doing nothing...")

        class CloseAction(AbstractAction):

            def __init__(self, theFrame):
                self.theFrame = theFrame

            def actionPerformed(self, event):
                myPrint("D","in CloseAction(), Event: ", event)
                myPrint("DB", "QuickJFrame() Frame shutting down....")

                try:
                    if not SwingUtilities.isEventDispatchThread():
                        SwingUtilities.invokeLater(GenericDisposeRunnable(self.theFrame))
                    else:
                        self.theFrame.dispose()
                except:
                    myPrint("B","Error. QuickJFrame dispose failed....?")
                    dump_sys_error_to_md_console_and_errorlog()


        class ToggleWrap(AbstractAction):

            def __init__(self, theCallingClass, theJText):
                self.theCallingClass = theCallingClass
                self.theJText = theJText

            def actionPerformed(self, event):
                myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

                self.theCallingClass.lWrapText = not self.theCallingClass.lWrapText
                self.theJText.setLineWrap(self.theCallingClass.lWrapText)

        class QuickJFrameNavigate(AbstractAction):

            def __init__(self, theJText, lTop=False, lBottom=False):
                self.theJText = theJText
                self.lTop = lTop
                self.lBottom = lBottom

            def actionPerformed(self, event):
                myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

                if self.lBottom: self.theJText.setCaretPosition(self.theJText.getDocument().getLength())
                if self.lTop:    self.theJText.setCaretPosition(0)

        class QuickJFramePrint(AbstractAction):

            def __init__(self, theCallingClass, theJText, theTitle=""):
                self.theCallingClass = theCallingClass
                self.theJText = theJText
                self.theTitle = theTitle

            def actionPerformed(self, event):
                myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )
                printOutputFile(_callingClass=self.theCallingClass, _theTitle=self.theTitle, _theJText=self.theJText)

        class QuickJFramePageSetup(AbstractAction):

            def __init__(self): pass

            def actionPerformed(self, event):
                myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )
                pageSetup()

        class QuickJFrameSaveTextToFile(AbstractAction):

            def __init__(self, theText, callingFrame):
                self.theText = theText
                self.callingFrame = callingFrame

            def actionPerformed(self, event):
                myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )
                saveOutputFile(self.callingFrame, "QUICKJFRAME", "%s_output.txt" %(myModuleID), self.theText)

        def show_the_frame(self):

            class MyQuickJFrameRunnable(Runnable):

                def __init__(self, callingClass):
                    self.callingClass = callingClass

                def run(self):                                                                                          # noqa
                    screenSize = Toolkit.getDefaultToolkit().getScreenSize()
                    frame_width = min(screenSize.width-20, max(GetFirstMainFrame.DEFAULT_MAX_WIDTH, int(round(GetFirstMainFrame.getSize().width *.9,0))))
                    frame_height = min(screenSize.height-20, max(GetFirstMainFrame.DEFAULT_MAX_HEIGHT, int(round(GetFirstMainFrame.getSize().height *.9,0))))

                    # JFrame.setDefaultLookAndFeelDecorated(True)   # Note: Darcula Theme doesn't like this and seems to be OK without this statement...
                    if self.callingClass.lQuitMDAfterClose:
                        extraText =  ">> MD WILL QUIT AFTER VIEWING THIS <<"
                    elif self.callingClass.lRestartMDAfterClose:
                        extraText =  ">> MD WILL RESTART AFTER VIEWING THIS <<"
                    else:
                        extraText = ""

                    jInternalFrame = MyJFrame(self.callingClass.title + " (%s+F to find/search for text)%s" %(MD_REF.getUI().ACCELERATOR_MASK_STR, extraText))
                    jInternalFrame.setName(u"%s_quickjframe" %myModuleID)

                    if not Platform.isOSX(): jInternalFrame.setIconImage(MDImages.getImage(MD_REF.getSourceInformation().getIconResource()))

                    jInternalFrame.setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE)
                    jInternalFrame.setResizable(True)

                    shortcut = Toolkit.getDefaultToolkit().getMenuShortcutKeyMaskEx()
                    jInternalFrame.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_W,  shortcut), "close-window")
                    jInternalFrame.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_F4, shortcut), "close-window")
                    jInternalFrame.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_F,  shortcut), "search-window")
                    jInternalFrame.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_P, shortcut),  "print-me")
                    jInternalFrame.getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0), "close-window")

                    theJText = JTextArea(self.callingClass.output)
                    theJText.setEditable(False)
                    theJText.setLineWrap(self.callingClass.lWrapText)
                    theJText.setWrapStyleWord(False)
                    theJText.setFont(getMonoFont())

                    jInternalFrame.getRootPane().getActionMap().put("close-window", self.callingClass.CloseAction(jInternalFrame))
                    jInternalFrame.getRootPane().getActionMap().put("search-window", SearchAction(jInternalFrame,theJText))
                    jInternalFrame.getRootPane().getActionMap().put("print-me", self.callingClass.QuickJFramePrint(self.callingClass, theJText, self.callingClass.title))
                    jInternalFrame.addWindowListener(self.callingClass.QJFWindowListener(jInternalFrame, self.callingClass.lQuitMDAfterClose, self.callingClass.lRestartMDAfterClose))

                    internalScrollPane = JScrollPane(theJText, JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED,JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED)

                    if self.callingClass.lAlertLevel>=2:
                        # internalScrollPane.setBackground(Color.RED)
                        theJText.setBackground(Color.RED)
                        theJText.setForeground(Color.BLACK)
                        theJText.setOpaque(True)
                    elif self.callingClass.lAlertLevel>=1:
                        # internalScrollPane.setBackground(Color.YELLOW)
                        theJText.setBackground(Color.YELLOW)
                        theJText.setForeground(Color.BLACK)
                        theJText.setOpaque(True)

                    if not self.callingClass.lAutoSize:
                        jInternalFrame.setPreferredSize(Dimension(frame_width, frame_height))

                    SetupMDColors.updateUI()

                    printButton = JButton("Print")
                    printButton.setToolTipText("Prints the output displayed in this window to your printer")
                    printButton.setOpaque(SetupMDColors.OPAQUE)
                    printButton.setBackground(SetupMDColors.BACKGROUND); printButton.setForeground(SetupMDColors.FOREGROUND)
                    printButton.addActionListener(self.callingClass.QuickJFramePrint(self.callingClass, theJText, self.callingClass.title))

                    if GlobalVars.defaultPrinterAttributes is None:
                        printPageSetup = JButton("Page Setup")
                        printPageSetup.setToolTipText("Printer Page Setup")
                        printPageSetup.setOpaque(SetupMDColors.OPAQUE)
                        printPageSetup.setBackground(SetupMDColors.BACKGROUND); printPageSetup.setForeground(SetupMDColors.FOREGROUND)
                        printPageSetup.addActionListener(self.callingClass.QuickJFramePageSetup())

                    saveButton = JButton("Save to file")
                    saveButton.setToolTipText("Saves the output displayed in this window to a file")
                    saveButton.setOpaque(SetupMDColors.OPAQUE)
                    saveButton.setBackground(SetupMDColors.BACKGROUND); saveButton.setForeground(SetupMDColors.FOREGROUND)
                    saveButton.addActionListener(self.callingClass.QuickJFrameSaveTextToFile(self.callingClass.output, jInternalFrame))

                    wrapOption = JCheckBox("Wrap Contents (Screen & Print)", self.callingClass.lWrapText)
                    wrapOption.addActionListener(self.callingClass.ToggleWrap(self.callingClass, theJText))
                    wrapOption.setForeground(SetupMDColors.FOREGROUND_REVERSED); wrapOption.setBackground(SetupMDColors.BACKGROUND_REVERSED)

                    topButton = JButton("Top")
                    topButton.setOpaque(SetupMDColors.OPAQUE)
                    topButton.setBackground(SetupMDColors.BACKGROUND); topButton.setForeground(SetupMDColors.FOREGROUND)
                    topButton.addActionListener(self.callingClass.QuickJFrameNavigate(theJText, lTop=True))

                    botButton = JButton("Bottom")
                    botButton.setOpaque(SetupMDColors.OPAQUE)
                    botButton.setBackground(SetupMDColors.BACKGROUND); botButton.setForeground(SetupMDColors.FOREGROUND)
                    botButton.addActionListener(self.callingClass.QuickJFrameNavigate(theJText, lBottom=True))

                    closeButton = JButton("Close")
                    closeButton.setOpaque(SetupMDColors.OPAQUE)
                    closeButton.setBackground(SetupMDColors.BACKGROUND); closeButton.setForeground(SetupMDColors.FOREGROUND)
                    closeButton.addActionListener(self.callingClass.CloseAction(jInternalFrame))

                    if Platform.isOSX():
                        save_useScreenMenuBar= System.getProperty("apple.laf.useScreenMenuBar")
                        if save_useScreenMenuBar is None or save_useScreenMenuBar == "":
                            save_useScreenMenuBar= System.getProperty("com.apple.macos.useScreenMenuBar")
                        System.setProperty("apple.laf.useScreenMenuBar", "false")
                        System.setProperty("com.apple.macos.useScreenMenuBar", "false")
                    else:
                        save_useScreenMenuBar = "true"

                    mb = JMenuBar()
                    mb.setBorder(EmptyBorder(0, 0, 0, 0))
                    mb.add(Box.createRigidArea(Dimension(10, 0)))
                    mb.add(topButton)
                    mb.add(Box.createRigidArea(Dimension(10, 0)))
                    mb.add(botButton)
                    mb.add(Box.createHorizontalGlue())
                    mb.add(wrapOption)

                    if GlobalVars.defaultPrinterAttributes is None:
                        mb.add(Box.createRigidArea(Dimension(10, 0)))
                        mb.add(printPageSetup)                                                                          # noqa

                    mb.add(Box.createHorizontalGlue())
                    mb.add(printButton)
                    mb.add(Box.createRigidArea(Dimension(10, 0)))
                    mb.add(saveButton)
                    mb.add(Box.createRigidArea(Dimension(10, 0)))
                    mb.add(closeButton)
                    mb.add(Box.createRigidArea(Dimension(30, 0)))

                    jInternalFrame.setJMenuBar(mb)

                    jInternalFrame.add(internalScrollPane)

                    jInternalFrame.pack()
                    if self.callingClass.screenLocation and isinstance(self.callingClass.screenLocation, Point):
                        jInternalFrame.setLocation(self.callingClass.screenLocation)
                    else:
                        jInternalFrame.setLocationRelativeTo(None)

                    jInternalFrame.setVisible(True)

                    if Platform.isOSX():
                        System.setProperty("apple.laf.useScreenMenuBar", save_useScreenMenuBar)
                        System.setProperty("com.apple.macos.useScreenMenuBar", save_useScreenMenuBar)

                    if "errlog.txt" in self.callingClass.title or self.callingClass.lJumpToEnd:
                        theJText.setCaretPosition(theJText.getDocument().getLength())

                    try:
                        if self.callingClass.copyToClipboard:
                            Toolkit.getDefaultToolkit().getSystemClipboard().setContents(StringSelection(self.callingClass.output), None)
                    except:
                        myPrint("J","Error copying contents to Clipboard")
                        dump_sys_error_to_md_console_and_errorlog()

                    self.callingClass.returnFrame = jInternalFrame

            if not SwingUtilities.isEventDispatchThread():
                myPrint("DB",".. Not running within the EDT so calling via MyQuickJFrameRunnable()...")
                SwingUtilities.invokeAndWait(MyQuickJFrameRunnable(self))
            else:
                myPrint("DB",".. Already within the EDT so calling naked...")
                MyQuickJFrameRunnable(self).run()

            return (self.returnFrame)

    class AboutThisScript(AbstractAction, Runnable):

        def __init__(self, theFrame):
            self.theFrame = theFrame
            self.aboutDialog = None

        def actionPerformed(self, event):
            myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()", "Event:", event)
            self.aboutDialog.dispose()  # Listener is already on the Swing EDT...

        def go(self):
            myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()")

            if not SwingUtilities.isEventDispatchThread():
                myPrint("DB",".. Not running within the EDT so calling via MyAboutRunnable()...")
                SwingUtilities.invokeAndWait(self)
            else:
                myPrint("DB",".. Already within the EDT so calling naked...")
                self.run()

        def run(self):                                                                                                  # noqa
            myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()")
            myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

            # noinspection PyUnresolvedReferences
            self.aboutDialog = JDialog(self.theFrame, "About", Dialog.ModalityType.MODELESS)

            shortcut = Toolkit.getDefaultToolkit().getMenuShortcutKeyMaskEx()
            self.aboutDialog.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_W, shortcut), "close-window")
            self.aboutDialog.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_F4, shortcut), "close-window")
            self.aboutDialog.getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0), "close-window")

            self.aboutDialog.getRootPane().getActionMap().put("close-window", self)
            self.aboutDialog.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE)

            if (not Platform.isMac()):
                # MD_REF.getUI().getImages()
                self.aboutDialog.setIconImage(MDImages.getImage(MD_REF.getSourceInformation().getIconResource()))

            aboutPanel = JPanel()
            aboutPanel.setLayout(FlowLayout(FlowLayout.LEFT))
            aboutPanel.setPreferredSize(Dimension(1120, 550))

            _label1 = JLabel(pad("Author: Stuart Beesley", 800))
            _label1.setForeground(getColorBlue())
            aboutPanel.add(_label1)

            _label2 = JLabel(pad("StuWareSoftSystems (2020-2023)", 800))
            _label2.setForeground(getColorBlue())
            aboutPanel.add(_label2)

            _label3 = JLabel(pad("Script/Extension: %s (build: %s)" %(GlobalVars.thisScriptName, version_build), 800))
            _label3.setForeground(getColorBlue())
            aboutPanel.add(_label3)

            displayString = scriptExit
            displayJText = JTextArea(displayString)
            displayJText.setFont(getMonoFont())
            displayJText.setEditable(False)
            displayJText.setLineWrap(False)
            displayJText.setWrapStyleWord(False)
            displayJText.setMargin(Insets(8, 8, 8, 8))

            aboutPanel.add(displayJText)

            self.aboutDialog.add(aboutPanel)

            self.aboutDialog.pack()
            self.aboutDialog.setLocationRelativeTo(None)
            self.aboutDialog.setVisible(True)

            myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

    def isGoodRate(theRate):

        if Double.isNaN(theRate) or Double.isInfinite(theRate) or theRate == 0:
            return False
        return True

    def safeInvertRate(theRate):

        if not isGoodRate(theRate):
            return theRate
        return (1.0 / theRate)

    def convertBytesGBs(_size): return round((_size/(1000.0*1000.0*1000)),1)

    def convertBytesMBs(_size): return round((_size/(1000.0*1000.0)),1)

    def convertBytesKBs(_size): return round((_size/(1000.0)),1)

    def convertMDShortDateFormat_strftimeFormat(lIncludeTime=False, lForceYYMMDDHMS=False):
        """Returns a Python strftime format string in accordance with MD Preferences for Date Format"""
        # https://strftime.org

        _MDFormat = MD_REF.getPreferences().getShortDateFormat()

        rtnFormat = "%Y-%m-%d"

        if lForceYYMMDDHMS:
            lIncludeTime = True
        else:
            if _MDFormat == "MM/dd/yyyy":
                rtnFormat = "%m/%d/%Y"
            elif _MDFormat == "MM.dd.yyyy":
                rtnFormat = "%m.%d.%Y"
            elif _MDFormat == "yyyy/MM/dd":
                rtnFormat = "%Y/%m/%d"
            elif _MDFormat == "yyyy.MM.dd":
                rtnFormat = "%Y.%m.%d"
            elif _MDFormat == "dd/MM/yyyy":
                rtnFormat = "%d/%m/%Y"
            elif _MDFormat == "dd.MM.yyyy":
                rtnFormat = "%d.%m.%Y"

        if lIncludeTime: rtnFormat += " %H:%M:%S"
        return rtnFormat

    def getHumanReadableDateTimeFromTimeStamp(_theTimeStamp, lIncludeTime=False, lForceYYMMDDHMS=False):
        return datetime.datetime.fromtimestamp(_theTimeStamp).strftime(convertMDShortDateFormat_strftimeFormat(lIncludeTime=lIncludeTime, lForceYYMMDDHMS=lForceYYMMDDHMS))

    def getHumanReadableModifiedDateTimeFromFile(_theFile, lIncludeTime=True, lForceYYMMDDHMS=True):
        return getHumanReadableDateTimeFromTimeStamp(os.path.getmtime(_theFile), lIncludeTime=lIncludeTime, lForceYYMMDDHMS=lForceYYMMDDHMS)

    def convertStrippedIntDateFormattedText(strippedDateInt, _format=None):

        # if _format is None: _format = "yyyy/MM/dd"
        if _format is None: _format = MD_REF.getPreferences().getShortDateFormat()

        if strippedDateInt is None or strippedDateInt == 0:
            return "<not set>"

        try:
            c = Calendar.getInstance()
            dateFromInt = DateUtil.convertIntDateToLong(strippedDateInt)
            c.setTime(dateFromInt)
            dateFormatter = SimpleDateFormat(_format)
            convertedDate = dateFormatter.format(c.getTime())
        except:
            return "<error>"

        return convertedDate

    def selectHomeScreen():

        try:
            currentViewAccount = MD_REF.getUI().firstMainFrame.getSelectedAccount()
            if currentViewAccount != MD_REF.getRootAccount():
                myPrint("DB","Switched to Home Page Summary Page (from: %s)" %(currentViewAccount))
                MD_REF.getUI().firstMainFrame.selectAccount(MD_REF.getRootAccount())
        except:
            myPrint("B","@@ Error switching to Summary Page (Home Page)")

    def fireMDPreferencesUpdated():
        """This triggers MD to firePreferencesUpdated().... Hopefully refreshing Home Screen Views too"""
        myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()" )

        class FPSRunnable(Runnable):
            def __init__(self): pass

            def run(self):
                myPrint("DB",".. Inside FPSRunnable() - calling firePreferencesUpdated()...")
                myPrint("B","Triggering an update to the Summary/Home Page View")
                MD_REF.getPreferences().firePreferencesUpdated()

        if not SwingUtilities.isEventDispatchThread():
            myPrint("DB",".. Not running within the EDT so calling via FPSRunnable()...")
            SwingUtilities.invokeLater(FPSRunnable())
        else:
            myPrint("DB",".. Already running within the EDT so calling FPSRunnable() naked...")
            FPSRunnable().run()
        return

    def decodeCommand(passedEvent):
        param = ""
        uri = passedEvent
        command = uri
        theIdx = uri.find('?')
        if(theIdx>=0):
            command = uri[:theIdx]
            param = uri[theIdx+1:]
        else:
            theIdx = uri.find(':')
            if(theIdx>=0):
                command = uri[:theIdx]
                param = uri[theIdx+1:]
        return command, param

    def getFieldByReflection(theObj, fieldName, isInt=False):
        try: theClass = theObj.getClass()
        except TypeError: theClass = theObj     # This catches where the object is already the Class
        reflectField = None
        while theClass is not None:
            try:
                reflectField = theClass.getDeclaredField(fieldName)
                break
            except NoSuchFieldException:
                theClass = theClass.getSuperclass()
        if reflectField is None: raise Exception("ERROR: could not find field: %s in class hierarchy" %(fieldName))
        if Modifier.isPrivate(reflectField.getModifiers()): reflectField.setAccessible(True)
        elif Modifier.isProtected(reflectField.getModifiers()): reflectField.setAccessible(True)
        isStatic = Modifier.isStatic(reflectField.getModifiers())
        if isInt: return reflectField.getInt(theObj if not isStatic else None)
        return reflectField.get(theObj if not isStatic else None)

    def invokeMethodByReflection(theObj, methodName, params, *args):
        try: theClass = theObj.getClass()
        except TypeError: theClass = theObj     # This catches where the object is already the Class
        reflectMethod = None
        while theClass is not None:
            try:
                if params is None:
                    reflectMethod = theClass.getDeclaredMethod(methodName)
                    break
                else:
                    reflectMethod = theClass.getDeclaredMethod(methodName, params)
                    break
            except NoSuchMethodException:
                theClass = theClass.getSuperclass()
        if reflectMethod is None: raise Exception("ERROR: could not find method: %s in class hierarchy" %(methodName))
        reflectMethod.setAccessible(True)
        return reflectMethod.invoke(theObj, *args)

    def setFieldByReflection(theObj, fieldName, newValue):
        try: theClass = theObj.getClass()
        except TypeError: theClass = theObj     # This catches where the object is already the Class
        reflectField = None
        while theClass is not None:
            try:
                reflectField = theClass.getDeclaredField(fieldName)
                break
            except NoSuchFieldException:
                theClass = theClass.getSuperclass()
        if reflectField is None: raise Exception("ERROR: could not find field: %s in class hierarchy" %(fieldName))
        if Modifier.isPrivate(reflectField.getModifiers()): reflectField.setAccessible(True)
        elif Modifier.isProtected(reflectField.getModifiers()): reflectField.setAccessible(True)
        isStatic = Modifier.isStatic(reflectField.getModifiers())
        return reflectField.set(theObj if not isStatic else None, newValue)

    def find_feature_module(theModule):
        # type: (str) -> bool
        """Searches Moneydance for a specific extension loaded"""
        fms = MD_REF.getLoadedModules()
        for fm in fms:
            if fm.getIDStr().lower() == theModule:
                myPrint("DB", "Found extension: %s" %(theModule))
                return fm
        return None

    GlobalVars.MD_KOTLIN_COMPILED_BUILD = 5000                                                                          # 2023.0
    def isKotlinCompiledBuild(): return (float(MD_REF.getBuild()) >= GlobalVars.MD_KOTLIN_COMPILED_BUILD)                                           # 2023.0(5000)

    def isMDPlusEnabledBuild(): return (float(MD_REF.getBuild()) >= GlobalVars.MD_MDPLUS_BUILD)                         # 2022.0

    def isAlertControllerEnabledBuild(): return (float(MD_REF.getBuild()) >= GlobalVars.MD_ALERTCONTROLLER_BUILD)       # 2022.3

    def genericSwingEDTRunner(ifOffEDTThenRunNowAndWait, ifOnEDTThenRunNowAndWait, codeblock, *args):
        """Will detect and then run the codeblock on the EDT"""

        isOnEDT = SwingUtilities.isEventDispatchThread()
        # myPrint("DB", "** In .genericSwingEDTRunner(), ifOffEDTThenRunNowAndWait: '%s', ifOnEDTThenRunNowAndWait: '%s', codeblock: '%s', args: '%s'" %(ifOffEDTThenRunNowAndWait, ifOnEDTThenRunNowAndWait, codeblock, args))
        myPrint("DB", "** In .genericSwingEDTRunner(), ifOffEDTThenRunNowAndWait: '%s', ifOnEDTThenRunNowAndWait: '%s', codeblock: <codeblock>, args: <args>" %(ifOffEDTThenRunNowAndWait, ifOnEDTThenRunNowAndWait))
        myPrint("DB", "** In .genericSwingEDTRunner(), isOnEDT:", isOnEDT)

        class GenericSwingEDTRunner(Runnable):

            def __init__(self, _codeblock, arguments):
                self.codeBlock = _codeblock
                self.params = arguments

            def run(self):
                myPrint("DB", "** In .genericSwingEDTRunner():: GenericSwingEDTRunner().run()... about to execute codeblock.... isOnEDT:", SwingUtilities.isEventDispatchThread())
                self.codeBlock(*self.params)
                myPrint("DB", "** In .genericSwingEDTRunner():: GenericSwingEDTRunner().run()... finished executing codeblock....")

        _gser = GenericSwingEDTRunner(codeblock, args)

        if ((isOnEDT and not ifOnEDTThenRunNowAndWait) or (not isOnEDT and not ifOffEDTThenRunNowAndWait)):
            myPrint("DB", "... calling codeblock via .invokeLater()...")
            SwingUtilities.invokeLater(_gser)
        elif not isOnEDT:
            myPrint("DB", "... calling codeblock via .invokeAndWait()...")
            SwingUtilities.invokeAndWait(_gser)
        else:
            myPrint("DB", "... calling codeblock.run() naked...")
            _gser.run()

        myPrint("DB", "... finished calling the codeblock via method reported above...")

    def genericThreadRunner(daemon, codeblock, *args):
        """Will run the codeblock on a new Thread"""

        # myPrint("DB", "** In .genericThreadRunner(), codeblock: '%s', args: '%s'" %(codeblock, args))
        myPrint("DB", "** In .genericThreadRunner(), codeblock: <codeblock>, args: <args>")

        class GenericThreadRunner(Runnable):

            def __init__(self, _codeblock, arguments):
                self.codeBlock = _codeblock
                self.params = arguments

            def run(self):
                myPrint("DB", "** In .genericThreadRunner():: GenericThreadRunner().run()... about to execute codeblock....")
                self.codeBlock(*self.params)
                myPrint("DB", "** In .genericThreadRunner():: GenericThreadRunner().run()... finished executing codeblock....")

        _gtr = GenericThreadRunner(codeblock, args)

        _t = Thread(_gtr, "NAB_GenericThreadRunner".lower())
        _t.setDaemon(daemon)
        _t.start()

        myPrint("DB", "... finished calling the codeblock...")

    GlobalVars.EXTN_PREF_KEY = "stuwaresoftsystems" + "." + myModuleID
    GlobalVars.EXTN_PREF_KEY_ENABLE_OBSERVER = "enable_observer"
    GlobalVars.EXTN_PREF_KEY_DISABLE_FORESIGHT = "disable_moneyforesight"

    class StreamTableFixed(StreamTable):
        """Replicates StreamTable. Provide a source to merge. Method .getBoolean() is 'fixed' to be backwards compatible with builds prior to Kotlin (Y/N vs 0/1)"""
        def __init__(self, _streamTableToCopy):
            # type: (StreamTable) -> None
            if not isinstance(_streamTableToCopy, StreamTable): raise Exception("LOGIC ERROR: Must pass a StreamTable! (Passed: %s)" %(type(_streamTableToCopy)))
            self.merge(_streamTableToCopy)

        def getBoolean(self, key, defaultVal):
            # type: (basestring, bool) -> bool
            if isKotlinCompiledBuild():     # MD2023.0 First Kotlin release - changed the code from detecting only Y/N to Y/N/T/F/0/1
                return super(self.__class__, self).getBoolean(key, defaultVal)
            _value = self.get(key, None)
            if _value in ["1", "Y", "y", "T", "t", "true", True]: return True
            if _value in ["0", "N", "n", "F", "f", "false", False]: return False
            return defaultVal

    def getExtensionDatasetSettings():
        # type: () -> SyncRecord
        _extnSettings =  GlobalVars.CONTEXT.getCurrentAccountBook().getLocalStorage().getSubset(GlobalVars.EXTN_PREF_KEY)
        if debug: myPrint("B", "Retrieved Extension Dataset Settings from LocalStorage: %s" %(_extnSettings))
        return _extnSettings

    def saveExtensionDatasetSettings(newExtnSettings):
        # type: (SyncRecord) -> None
        if not isinstance(newExtnSettings, SyncRecord):
            raise Exception("ERROR: 'newExtnSettings' is not a SyncRecord (given: '%s')" %(type(newExtnSettings)))
        _localStorage = GlobalVars.CONTEXT.getCurrentAccountBook().getLocalStorage()
        _localStorage.put(GlobalVars.EXTN_PREF_KEY, newExtnSettings)
        if debug: myPrint("B", "Stored Extension Dataset Settings into LocalStorage: %s" %(newExtnSettings))

    def getExtensionGlobalPreferences(enhancedBooleanCheck=True):
        # type: (bool) -> StreamTable
        _extnPrefs =  GlobalVars.CONTEXT.getPreferences().getTableSetting(GlobalVars.EXTN_PREF_KEY, StreamTable())
        if not isKotlinCompiledBuild():
            if enhancedBooleanCheck:
                _extnPrefs = StreamTableFixed(_extnPrefs)
                myPrint("DB", "... copied retrieved Extension Global Preferences into enhanced StreamTable for backwards .getBoolean() capability...")
        if debug: myPrint("B", "Retrieved Extension Global Preference: %s" %(_extnPrefs))
        return _extnPrefs

    def saveExtensionGlobalPreferences(newExtnPrefs):
        # type: (StreamTable) -> None
        if not isinstance(newExtnPrefs, StreamTable):
            raise Exception("ERROR: 'newExtnPrefs' is not a StreamTable (given: '%s')" %(type(newExtnPrefs)))
        GlobalVars.CONTEXT.getPreferences().setSetting(GlobalVars.EXTN_PREF_KEY, newExtnPrefs)
        if debug: myPrint("B", "Stored Extension Global Preferences: %s" %(newExtnPrefs))

    # END COMMON DEFINITIONS ###############################################################################################
    # END COMMON DEFINITIONS ###############################################################################################
    # END COMMON DEFINITIONS ###############################################################################################
    # COPY >> END

    # >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
    # >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
    # >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
    def load_StuWareSoftSystems_parameters_into_memory():

        # >>> THESE ARE THIS SCRIPT's PARAMETERS TO LOAD

        # common
        global __extract_data
        global lWriteBOMToExportFile_SWSS, userdateformat, lStripASCII, csvDelimiter
        global lAllCurrency, filterForCurrency
        global hideHiddenSecurities, lAllSecurity, filterForSecurity
        global hideInactiveAccounts, hideHiddenAccounts, lAllAccounts, filterForAccounts
        global whichDefaultExtractToRun_SWSS, lWriteParametersToExportFile_SWSS, lAllowEscapeExitApp_SWSS

        # all
        global autoExtract_SG2020, autoExtract_ERTC, autoExtract_EAR, autoExtract_EIT, autoExtract_ECH, autoExtract_ESB, autoExtract_ETRUNK, autoExtract_JSON, autoExtract_EATTACH

        # extract_account_registers_csv
        global lIncludeOpeningBalances_EAR, lIncludeBalanceAdjustments_EAR
        global userdateStart_EAR, userdateEnd_EAR, lIncludeSubAccounts_EAR
        global lAllTags_EAR, tagFilter_EAR, lExtractAttachments_EAR
        global saveDropDownAccountUUID_EAR, lIncludeInternalTransfers_EAR, saveDropDownDateRange_EAR
        global lAllText_EAR, textFilter_EAR
        global lAllCategories_EAR, categoriesFilter_EAR

        # extract_investment_transactions_csv
        global lIncludeOpeningBalances, lIncludeBalanceAdjustments, lAdjustForSplits, lExtractAttachments_EIT, lOmitLOTDataFromExtract_EIT, lExtractExtraSecurityAcctInfo
        global lFilterDateRange_EIT, filterDateStart_EIT, filterDateEnd_EIT

        # extract_security_balances_csv
        # None

        # extract_currency_history_csv
        global lSimplify_ECH, userdateStart_ECH, userdateEnd_ECH, hideHiddenCurrencies_ECH

        # stockglance2020
        global lIncludeCashBalances
        global lSplitSecuritiesByAccount, lExcludeTotalsFromCSV, _column_widths_SG2020, lIncludeFutureBalances_SG2020
        global maxDecimalPlacesRounding_SG2020, lUseCurrentPrice_SG2020

        # extract_reminders_csv
        global _column_widths_ERTC, lExtractFutureRemindersToo_ERTC

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )
        myPrint("DB", "Loading variables into memory...")

        if GlobalVars.parametersLoadedFromFile is None: GlobalVars.parametersLoadedFromFile = {}


        # Delete superseded version keys from file - stops Toolbox complaining
        for deleteObsoleteKey in ["__extract_account_registers",
                                  "__extract_investment_transactions",
                                  "__extract_currency_history_csv",
                                  "__StockGlance2020",
                                  "__stockglance2020",
                                  "__extract_reminders_to_csv",
                                  "__extract_reminders_csv",
                                  "lRoundPrice"]:

            if GlobalVars.parametersLoadedFromFile.get(deleteObsoleteKey) is not None:
                myPrint("B", "@@ Detected old %s extract version key... Will delete it..." %(deleteObsoleteKey))
                GlobalVars.parametersLoadedFromFile.pop(deleteObsoleteKey, None)  # Obsoleted extract version key - delete from parameter file


        # common
        if GlobalVars.parametersLoadedFromFile.get("__extract_data") is not None: __extract_data = GlobalVars.parametersLoadedFromFile.get("__extract_data")
        if GlobalVars.parametersLoadedFromFile.get("hideHiddenSecurities") is not None: hideHiddenSecurities = GlobalVars.parametersLoadedFromFile.get("hideHiddenSecurities")
        if GlobalVars.parametersLoadedFromFile.get("lAllSecurity") is not None: lAllSecurity = GlobalVars.parametersLoadedFromFile.get("lAllSecurity")
        if GlobalVars.parametersLoadedFromFile.get("filterForSecurity") is not None: filterForSecurity = GlobalVars.parametersLoadedFromFile.get("filterForSecurity")
        if GlobalVars.parametersLoadedFromFile.get("hideInactiveAccounts") is not None: hideInactiveAccounts = GlobalVars.parametersLoadedFromFile.get("hideInactiveAccounts")
        if GlobalVars.parametersLoadedFromFile.get("hideHiddenAccounts") is not None: hideHiddenAccounts = GlobalVars.parametersLoadedFromFile.get("hideHiddenAccounts")
        if GlobalVars.parametersLoadedFromFile.get("lAllAccounts") is not None: lAllAccounts = GlobalVars.parametersLoadedFromFile.get("lAllAccounts")
        if GlobalVars.parametersLoadedFromFile.get("filterForAccounts") is not None: filterForAccounts = GlobalVars.parametersLoadedFromFile.get("filterForAccounts")
        if GlobalVars.parametersLoadedFromFile.get("lAllCurrency") is not None: lAllCurrency = GlobalVars.parametersLoadedFromFile.get("lAllCurrency")
        if GlobalVars.parametersLoadedFromFile.get("filterForCurrency") is not None: filterForCurrency = GlobalVars.parametersLoadedFromFile.get("filterForCurrency")
        if GlobalVars.parametersLoadedFromFile.get("lStripASCII") is not None: lStripASCII = GlobalVars.parametersLoadedFromFile.get("lStripASCII")
        if GlobalVars.parametersLoadedFromFile.get("csvDelimiter") is not None: csvDelimiter = GlobalVars.parametersLoadedFromFile.get("csvDelimiter")
        if GlobalVars.parametersLoadedFromFile.get("userdateformat") is not None: userdateformat = GlobalVars.parametersLoadedFromFile.get("userdateformat")
        if GlobalVars.parametersLoadedFromFile.get("lWriteBOMToExportFile_SWSS") is not None: lWriteBOMToExportFile_SWSS = GlobalVars.parametersLoadedFromFile.get("lWriteBOMToExportFile_SWSS")                          # noqa
        if GlobalVars.parametersLoadedFromFile.get("whichDefaultExtractToRun_SWSS") is not None: whichDefaultExtractToRun_SWSS = GlobalVars.parametersLoadedFromFile.get("whichDefaultExtractToRun_SWSS")                 # noqa
        if GlobalVars.parametersLoadedFromFile.get("lWriteParametersToExportFile_SWSS") is not None: lWriteParametersToExportFile_SWSS = GlobalVars.parametersLoadedFromFile.get("lWriteParametersToExportFile_SWSS")     # noqa
        if GlobalVars.parametersLoadedFromFile.get("lAllowEscapeExitApp_SWSS") is not None: lAllowEscapeExitApp_SWSS = GlobalVars.parametersLoadedFromFile.get("lAllowEscapeExitApp_SWSS")                                # noqa


        # All have this options
        if GlobalVars.parametersLoadedFromFile.get("autoExtract_SG2020") is not None: autoExtract_SG2020 = GlobalVars.parametersLoadedFromFile.get("autoExtract_SG2020")                                                   # noqa
        if GlobalVars.parametersLoadedFromFile.get("autoExtract_ERTC") is not None: autoExtract_ERTC = GlobalVars.parametersLoadedFromFile.get("autoExtract_ERTC")                                                         # noqa
        if GlobalVars.parametersLoadedFromFile.get("autoExtract_EAR") is not None: autoExtract_EAR = GlobalVars.parametersLoadedFromFile.get("autoExtract_EAR")                                                            # noqa
        if GlobalVars.parametersLoadedFromFile.get("autoExtract_EIT") is not None: autoExtract_EIT = GlobalVars.parametersLoadedFromFile.get("autoExtract_EIT")                                                            # noqa
        if GlobalVars.parametersLoadedFromFile.get("autoExtract_ECH") is not None: autoExtract_ECH = GlobalVars.parametersLoadedFromFile.get("autoExtract_ECH")                                                            # noqa
        if GlobalVars.parametersLoadedFromFile.get("autoExtract_ESB") is not None: autoExtract_ESB = GlobalVars.parametersLoadedFromFile.get("autoExtract_ESB")                                                            # noqa
        if GlobalVars.parametersLoadedFromFile.get("autoExtract_ETRUNK") is not None: autoExtract_ETRUNK = GlobalVars.parametersLoadedFromFile.get("autoExtract_ETRUNK")                                                            # noqa
        if GlobalVars.parametersLoadedFromFile.get("autoExtract_JSON") is not None: autoExtract_JSON = GlobalVars.parametersLoadedFromFile.get("autoExtract_JSON")                                                            # noqa
        if GlobalVars.parametersLoadedFromFile.get("autoExtract_EATTACH") is not None: autoExtract_EATTACH = GlobalVars.parametersLoadedFromFile.get("autoExtract_EATTACH")                                                            # noqa

        # extract_account_registers_csv
        if GlobalVars.parametersLoadedFromFile.get("lIncludeSubAccounts_EAR") is not None: lIncludeSubAccounts_EAR = GlobalVars.parametersLoadedFromFile.get("lIncludeSubAccounts_EAR")
        if GlobalVars.parametersLoadedFromFile.get("userdateStart_EAR") is not None: userdateStart_EAR = GlobalVars.parametersLoadedFromFile.get("userdateStart_EAR")
        if GlobalVars.parametersLoadedFromFile.get("userdateEnd_EAR") is not None: userdateEnd_EAR = GlobalVars.parametersLoadedFromFile.get("userdateEnd_EAR")
        if GlobalVars.parametersLoadedFromFile.get("lAllTags_EAR") is not None: lAllTags_EAR = GlobalVars.parametersLoadedFromFile.get("lAllTags_EAR")
        if GlobalVars.parametersLoadedFromFile.get("tagFilter_EAR") is not None: tagFilter_EAR = GlobalVars.parametersLoadedFromFile.get("tagFilter_EAR")
        if GlobalVars.parametersLoadedFromFile.get("lAllText_EAR") is not None: lAllText_EAR = GlobalVars.parametersLoadedFromFile.get("lAllText_EAR")
        if GlobalVars.parametersLoadedFromFile.get("textFilter_EAR") is not None: textFilter_EAR = GlobalVars.parametersLoadedFromFile.get("textFilter_EAR")
        if GlobalVars.parametersLoadedFromFile.get("lAllCategories_EAR") is not None: lAllCategories_EAR = GlobalVars.parametersLoadedFromFile.get("lAllCategories_EAR")
        if GlobalVars.parametersLoadedFromFile.get("categoriesFilter_EAR") is not None: categoriesFilter_EAR = GlobalVars.parametersLoadedFromFile.get("categoriesFilter_EAR")
        if GlobalVars.parametersLoadedFromFile.get("lExtractAttachments_EAR") is not None: lExtractAttachments_EAR = GlobalVars.parametersLoadedFromFile.get("lExtractAttachments_EAR")
        if GlobalVars.parametersLoadedFromFile.get("lIncludeOpeningBalances_EAR") is not None: lIncludeOpeningBalances_EAR = GlobalVars.parametersLoadedFromFile.get("lIncludeOpeningBalances_EAR")
        if GlobalVars.parametersLoadedFromFile.get("lIncludeBalanceAdjustments_EAR") is not None: lIncludeBalanceAdjustments_EAR = GlobalVars.parametersLoadedFromFile.get("lIncludeBalanceAdjustments_EAR")
        if GlobalVars.parametersLoadedFromFile.get("saveDropDownAccountUUID_EAR") is not None: saveDropDownAccountUUID_EAR = GlobalVars.parametersLoadedFromFile.get("saveDropDownAccountUUID_EAR")                     # noqa
        if GlobalVars.parametersLoadedFromFile.get("saveDropDownDateRange_EAR") is not None: saveDropDownDateRange_EAR = GlobalVars.parametersLoadedFromFile.get("saveDropDownDateRange_EAR")                           # noqa
        if GlobalVars.parametersLoadedFromFile.get("lIncludeInternalTransfers_EAR") is not None: lIncludeInternalTransfers_EAR = GlobalVars.parametersLoadedFromFile.get("lIncludeInternalTransfers_EAR")               # noqa

        # extract_investment_transactions_csv
        if GlobalVars.parametersLoadedFromFile.get("lIncludeOpeningBalances") is not None: lIncludeOpeningBalances = GlobalVars.parametersLoadedFromFile.get("lIncludeOpeningBalances")
        if GlobalVars.parametersLoadedFromFile.get("lIncludeBalanceAdjustments") is not None: lIncludeBalanceAdjustments = GlobalVars.parametersLoadedFromFile.get("lIncludeBalanceAdjustments")
        if GlobalVars.parametersLoadedFromFile.get("lAdjustForSplits") is not None: lAdjustForSplits = GlobalVars.parametersLoadedFromFile.get("lAdjustForSplits")
        if GlobalVars.parametersLoadedFromFile.get("lExtractAttachments_EIT") is not None: lExtractAttachments_EIT = GlobalVars.parametersLoadedFromFile.get("lExtractAttachments_EIT")                                 # noqa
        if GlobalVars.parametersLoadedFromFile.get("lOmitLOTDataFromExtract_EIT") is not None: lOmitLOTDataFromExtract_EIT = GlobalVars.parametersLoadedFromFile.get("lOmitLOTDataFromExtract_EIT")                     # noqa
        if GlobalVars.parametersLoadedFromFile.get("lExtractExtraSecurityAcctInfo") is not None: lExtractExtraSecurityAcctInfo = GlobalVars.parametersLoadedFromFile.get("lExtractExtraSecurityAcctInfo")               # noqa
        if GlobalVars.parametersLoadedFromFile.get("lFilterDateRange_EIT") is not None: lFilterDateRange_EIT = GlobalVars.parametersLoadedFromFile.get("lFilterDateRange_EIT")                                          # noqa
        if GlobalVars.parametersLoadedFromFile.get("filterDateStart_EIT") is not None: filterDateStart_EIT = GlobalVars.parametersLoadedFromFile.get("filterDateStart_EIT")                                             # noqa
        if GlobalVars.parametersLoadedFromFile.get("filterDateEnd_EIT") is not None: filterDateEnd_EIT = GlobalVars.parametersLoadedFromFile.get("filterDateEnd_EIT")                                                   # noqa

        # extract_security_balances_csv
        # None

        # extract_currency_history_csv
        if GlobalVars.parametersLoadedFromFile.get("lSimplify_ECH") is not None: lSimplify_ECH = GlobalVars.parametersLoadedFromFile.get("lSimplify_ECH")
        if GlobalVars.parametersLoadedFromFile.get("userdateStart_ECH") is not None: userdateStart_ECH = GlobalVars.parametersLoadedFromFile.get("userdateStart_ECH")
        if GlobalVars.parametersLoadedFromFile.get("userdateEnd_ECH") is not None: userdateEnd_ECH = GlobalVars.parametersLoadedFromFile.get("userdateEnd_ECH")
        if GlobalVars.parametersLoadedFromFile.get("hideHiddenCurrencies_ECH") is not None: hideHiddenCurrencies_ECH = GlobalVars.parametersLoadedFromFile.get("hideHiddenCurrencies_ECH")

        # stockglance2020
        if GlobalVars.parametersLoadedFromFile.get("lIncludeCashBalances") is not None: lIncludeCashBalances = GlobalVars.parametersLoadedFromFile.get("lIncludeCashBalances")
        if GlobalVars.parametersLoadedFromFile.get("lSplitSecuritiesByAccount") is not None: lSplitSecuritiesByAccount = GlobalVars.parametersLoadedFromFile.get("lSplitSecuritiesByAccount")
        if GlobalVars.parametersLoadedFromFile.get("lExcludeTotalsFromCSV") is not None: lExcludeTotalsFromCSV = GlobalVars.parametersLoadedFromFile.get("lExcludeTotalsFromCSV")
        if GlobalVars.parametersLoadedFromFile.get("lIncludeFutureBalances_SG2020") is not None: lIncludeFutureBalances_SG2020 = GlobalVars.parametersLoadedFromFile.get("lIncludeFutureBalances_SG2020")
        if GlobalVars.parametersLoadedFromFile.get("maxDecimalPlacesRounding_SG2020") is not None: maxDecimalPlacesRounding_SG2020 = GlobalVars.parametersLoadedFromFile.get("maxDecimalPlacesRounding_SG2020")
        if GlobalVars.parametersLoadedFromFile.get("lUseCurrentPrice_SG2020") is not None: lUseCurrentPrice_SG2020 = GlobalVars.parametersLoadedFromFile.get("lUseCurrentPrice_SG2020")

        if GlobalVars.parametersLoadedFromFile.get("_column_widths_SG2020") is not None: _column_widths_SG2020 = GlobalVars.parametersLoadedFromFile.get("_column_widths_SG2020")

        # extract_reminders_csv
        if GlobalVars.parametersLoadedFromFile.get("_column_widths_ERTC") is not None: _column_widths_ERTC = GlobalVars.parametersLoadedFromFile.get("_column_widths_ERTC")
        if GlobalVars.parametersLoadedFromFile.get("lExtractFutureRemindersToo_ERTC") is not None: lExtractFutureRemindersToo_ERTC = GlobalVars.parametersLoadedFromFile.get("lExtractFutureRemindersToo_ERTC")
        if GlobalVars.parametersLoadedFromFile.get("daysToLookForward_LFR") is not None: GlobalVars.daysToLookForward_LFR = GlobalVars.parametersLoadedFromFile.get("daysToLookForward_LFR")

        if GlobalVars.parametersLoadedFromFile.get("scriptpath") is not None:
            GlobalVars.scriptpath = GlobalVars.parametersLoadedFromFile.get("scriptpath")
            if not os.path.isdir(GlobalVars.scriptpath):
                myPrint("B","Warning: loaded parameter scriptpath does not appear to be a valid directory:", GlobalVars.scriptpath, "will ignore")
                GlobalVars.scriptpath = ""

        myPrint("DB","parametersLoadedFromFile{} set into memory (as variables).....")

        return

    # >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
    def dump_StuWareSoftSystems_parameters_from_memory():
        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )

        # NOTE: Parameters were loaded earlier on... Preserve existing, and update any used ones...
        # (i.e. other StuWareSoftSystems programs might be sharing the same file)

        if GlobalVars.parametersLoadedFromFile is None: GlobalVars.parametersLoadedFromFile = {}

        # common
        GlobalVars.parametersLoadedFromFile["__extract_data"] = version_build
        GlobalVars.parametersLoadedFromFile["lStripASCII"] = lStripASCII
        GlobalVars.parametersLoadedFromFile["csvDelimiter"] = csvDelimiter
        GlobalVars.parametersLoadedFromFile["lWriteBOMToExportFile_SWSS"] = lWriteBOMToExportFile_SWSS
        GlobalVars.parametersLoadedFromFile["lWriteParametersToExportFile_SWSS"] = lWriteParametersToExportFile_SWSS
        GlobalVars.parametersLoadedFromFile["whichDefaultExtractToRun_SWSS"] = whichDefaultExtractToRun_SWSS
        GlobalVars.parametersLoadedFromFile["lAllowEscapeExitApp_SWSS"] = lAllowEscapeExitApp_SWSS
        GlobalVars.parametersLoadedFromFile["userdateformat"] = userdateformat
        GlobalVars.parametersLoadedFromFile["hideInactiveAccounts"] = hideInactiveAccounts
        GlobalVars.parametersLoadedFromFile["hideHiddenAccounts"] = hideHiddenAccounts
        GlobalVars.parametersLoadedFromFile["lAllAccounts"] = lAllAccounts
        GlobalVars.parametersLoadedFromFile["filterForAccounts"] = filterForAccounts
        GlobalVars.parametersLoadedFromFile["lAllCurrency"] = lAllCurrency
        GlobalVars.parametersLoadedFromFile["filterForCurrency"] = filterForCurrency
        GlobalVars.parametersLoadedFromFile["hideHiddenSecurities"] = hideHiddenSecurities
        GlobalVars.parametersLoadedFromFile["lAllSecurity"] = lAllSecurity
        GlobalVars.parametersLoadedFromFile["filterForSecurity"] = filterForSecurity

        # All have this option
        GlobalVars.parametersLoadedFromFile["autoExtract_SG2020"] = autoExtract_SG2020
        GlobalVars.parametersLoadedFromFile["autoExtract_ERTC"] = autoExtract_ERTC
        GlobalVars.parametersLoadedFromFile["autoExtract_EAR"] = autoExtract_EAR
        GlobalVars.parametersLoadedFromFile["autoExtract_EIT"] = autoExtract_EIT
        GlobalVars.parametersLoadedFromFile["autoExtract_ECH"] = autoExtract_ECH
        GlobalVars.parametersLoadedFromFile["autoExtract_ESB"] = autoExtract_ESB
        GlobalVars.parametersLoadedFromFile["autoExtract_ETRUNK"] = autoExtract_ETRUNK
        GlobalVars.parametersLoadedFromFile["autoExtract_JSON"] = autoExtract_JSON
        GlobalVars.parametersLoadedFromFile["autoExtract_EATTACH"] = autoExtract_EATTACH

        # extract_account_registers_csv
        GlobalVars.parametersLoadedFromFile["lIncludeSubAccounts_EAR"] = lIncludeSubAccounts_EAR
        GlobalVars.parametersLoadedFromFile["lIncludeOpeningBalances_EAR"] = lIncludeOpeningBalances_EAR
        GlobalVars.parametersLoadedFromFile["lIncludeBalanceAdjustments_EAR"] = lIncludeBalanceAdjustments_EAR
        GlobalVars.parametersLoadedFromFile["userdateStart_EAR"] = userdateStart_EAR
        GlobalVars.parametersLoadedFromFile["userdateEnd_EAR"] = userdateEnd_EAR
        GlobalVars.parametersLoadedFromFile["lAllTags_EAR"] = lAllTags_EAR
        GlobalVars.parametersLoadedFromFile["tagFilter_EAR"] = tagFilter_EAR
        GlobalVars.parametersLoadedFromFile["lAllText_EAR"] = lAllText_EAR
        GlobalVars.parametersLoadedFromFile["textFilter_EAR"] = textFilter_EAR
        GlobalVars.parametersLoadedFromFile["lAllCategories_EAR"] = lAllCategories_EAR
        GlobalVars.parametersLoadedFromFile["categoriesFilter_EAR"] = categoriesFilter_EAR
        GlobalVars.parametersLoadedFromFile["lExtractAttachments_EAR"] = lExtractAttachments_EAR
        GlobalVars.parametersLoadedFromFile["lIncludeInternalTransfers_EAR"] = lIncludeInternalTransfers_EAR
        GlobalVars.parametersLoadedFromFile["saveDropDownAccountUUID_EAR"] = saveDropDownAccountUUID_EAR
        GlobalVars.parametersLoadedFromFile["saveDropDownDateRange_EAR"] = saveDropDownDateRange_EAR

        # extract_investment_transactions_csv
        GlobalVars.parametersLoadedFromFile["lExtractAttachments_EIT"] = lExtractAttachments_EIT
        GlobalVars.parametersLoadedFromFile["lOmitLOTDataFromExtract_EIT"] = lOmitLOTDataFromExtract_EIT
        GlobalVars.parametersLoadedFromFile["lExtractExtraSecurityAcctInfo"] = lExtractExtraSecurityAcctInfo
        GlobalVars.parametersLoadedFromFile["lFilterDateRange_EIT"] = lFilterDateRange_EIT
        GlobalVars.parametersLoadedFromFile["filterDateStart_EIT"] = filterDateStart_EIT
        GlobalVars.parametersLoadedFromFile["filterDateEnd_EIT"] = filterDateEnd_EIT
        GlobalVars.parametersLoadedFromFile["lIncludeOpeningBalances"] = lIncludeOpeningBalances
        GlobalVars.parametersLoadedFromFile["lIncludeBalanceAdjustments"] = lIncludeBalanceAdjustments
        GlobalVars.parametersLoadedFromFile["lAdjustForSplits"] = lAdjustForSplits

        # extract_security_balances_csv
        # None

        # extract_currency_history_csv
        GlobalVars.parametersLoadedFromFile["lSimplify_ECH"] = lSimplify_ECH
        GlobalVars.parametersLoadedFromFile["userdateStart_ECH"] = userdateStart_ECH
        GlobalVars.parametersLoadedFromFile["userdateEnd_ECH"] = userdateEnd_ECH
        GlobalVars.parametersLoadedFromFile["hideHiddenCurrencies_ECH"] = hideHiddenCurrencies_ECH

        # stockglance2020
        GlobalVars.parametersLoadedFromFile["lIncludeCashBalances"] = lIncludeCashBalances
        GlobalVars.parametersLoadedFromFile["lSplitSecuritiesByAccount"] = lSplitSecuritiesByAccount
        GlobalVars.parametersLoadedFromFile["lExcludeTotalsFromCSV"] = lExcludeTotalsFromCSV
        GlobalVars.parametersLoadedFromFile["lIncludeFutureBalances_SG2020"] = lIncludeFutureBalances_SG2020
        GlobalVars.parametersLoadedFromFile["maxDecimalPlacesRounding_SG2020"] = maxDecimalPlacesRounding_SG2020
        GlobalVars.parametersLoadedFromFile["lUseCurrentPrice_SG2020"] = lUseCurrentPrice_SG2020

        GlobalVars.parametersLoadedFromFile["_column_widths_SG2020"] = _column_widths_SG2020

        # extract_reminders_csv
        GlobalVars.parametersLoadedFromFile["_column_widths_ERTC"] = _column_widths_ERTC
        GlobalVars.parametersLoadedFromFile["lExtractFutureRemindersToo_ERTC"] = lExtractFutureRemindersToo_ERTC
        GlobalVars.parametersLoadedFromFile["daysToLookForward_LFR"] = GlobalVars.daysToLookForward_LFR

        if GlobalVars.scriptpath != "" and os.path.isdir(GlobalVars.scriptpath):
            GlobalVars.parametersLoadedFromFile["scriptpath"] = GlobalVars.scriptpath

        myPrint("DB","variables dumped from memory back into parametersLoadedFromFile{}.....")

    # clear up any old left-overs....
    destroyOldFrames(myModuleID)

    get_StuWareSoftSystems_parameters_from_file()

    myPrint("DB", "DEBUG IS ON..")

    if SwingUtilities.isEventDispatchThread():
        myPrint("DB", "FYI - This script/extension is currently running within the Swing Event Dispatch Thread (EDT)")
    else:
        myPrint("DB", "FYI - This script/extension is NOT currently running within the Swing Event Dispatch Thread (EDT)")

    def cleanup_actions(theFrame=None):
        myPrint("DB", "In", inspect.currentframe().f_code.co_name, "()")
        myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

        if theFrame is not None and not theFrame.isActiveInMoneydance:
            destroyOldFrames(myModuleID)

        try:
            if not GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE:
                MD_REF.getUI().setStatus(">> StuWareSoftSystems - thanks for using >> %s......." %(GlobalVars.thisScriptName),0)
        except: pass  # If this fails, then MD is probably shutting down.......

        if not GlobalVars.i_am_an_extension_so_run_headless: print(scriptExit)

        cleanup_references()

    # .moneydance_invoke_called() is used via the _invoke.py script as defined in script_info.dict. Not used for runtime extensions
    def moneydance_invoke_called(theCommand):
        # ... modify as required to handle .showURL() events sent to this extension/script...
        myPrint("B", "INVOKE - Received extension command: '%s'" %(theCommand))

    GlobalVars.defaultPrintLandscape = True
    # END ALL CODE COPY HERE ###############################################################################################
    # END ALL CODE COPY HERE ###############################################################################################
    # END ALL CODE COPY HERE ###############################################################################################

    def resetGlobalVariables():
        myPrint("DB", "@@ RESETTING KEY GLOBAL REFERENCES.....")
        # Do these once here (for objects that might hold Model objects etc) and then release at the end... (not the cleanest method...)
        GlobalVars.dropDownAccount_EAR = None
        GlobalVars.baseCurrency = None
        GlobalVars.scrollpane = None
        GlobalVars.table = None
        GlobalVars.stockGlanceInstance = None
        GlobalVars.transactionTable = None
        GlobalVars.csvlines_reminders_future = None
        GlobalVars.tableHeaderRowList_reminders_future = None

        # StockGlance2020 - converted from globals
        GlobalVars.rawDataTable_sg2020 = None
        GlobalVars.rawFooterTable_sg2020 = None

        # from extract_reminders_csv - converted from globals
        GlobalVars.csvlines_reminders = None
        GlobalVars.csvlines_reminders_future = None
        GlobalVars.tableHeaderRowList_reminders_future = None


    resetGlobalVariables()


    if isKotlinCompiledBuild():
        from okio import BufferedSource, Buffer, Okio                                                                   # noqa
        if debug: myPrint("B", "** Kotlin compiled build detected, new libraries enabled.....")

    def convertBufferedSourceToInputStream(bufferedSource):
        if isKotlinCompiledBuild() and isinstance(bufferedSource, BufferedSource):
            return bufferedSource.inputStream()
        return bufferedSource

    def getUnadjustedStartBalance(theAccount):
        if isKotlinCompiledBuild(): return theAccount.getUnadjustedStartBalance()
        return theAccount.getStartBalance()

    def getBalanceAdjustment(theAccount):
        if isKotlinCompiledBuild(): return theAccount.getBalanceAdjustment()
        return theAccount.getLongParameter(GlobalVars.Strings.MD_KEY_BALANCE_ADJUSTMENT, 0)

    def getStatusCharRevised(txn):                  # Requested by Ron Lewin - changes Reconciling from 'x' to 'r'
        status = unicode(txn.getStatusChar())
        if status == u"x": return "r"
        return status

    def isPreviewBuild():
        if MD_EXTENSION_LOADER is not None:
            try:
                stream = MD_EXTENSION_LOADER.getResourceAsStream("/_PREVIEW_BUILD_")
                if stream is not None:
                    myPrint("B", "@@ PREVIEW BUILD (%s) DETECTED @@" %(version_build))
                    stream.close()
                    return True
            except: pass
        return False

    # Mirror code in list_future_reminders (ensure identical)
    def printJTable(_theFrame, _theJTable, _theTitle, _secondJTable=None):

        # todo - enable print for StockGlance via Book() (to get one print job) - instead of two outputs
        # refer: https://stackoverflow.com/questions/14775753/printing-multiple-jtables-as-one-job-book-object-only-prints-1st-table

        # Possible future modification, leverage MDPrinter, and it's classes / methods to save/load preferences and create printers
        try:
            if _theJTable is None or _theFrame is None: return

            myPrint("DB", "Creating new PrinterJob...")
            printer_job = PrinterJob.getPrinterJob()

            if GlobalVars.defaultPrintService is not None:
                printer_job.setPrintService(GlobalVars.defaultPrintService)
                myPrint("DB","Assigned remembered PrintService...: %s" %(printer_job.getPrintService()))

            if GlobalVars.defaultPrinterAttributes is not None:
                pAttrs = attribute.HashPrintRequestAttributeSet(GlobalVars.defaultPrinterAttributes)
            else:
                pAttrs = loadDefaultPrinterAttributes(None)

            pAttrs.remove(attribute.standard.JobName)
            pAttrs.add(attribute.standard.JobName("%s: %s" %(myModuleID.capitalize(), _theTitle), None))

            if GlobalVars.defaultDPI != 72:
                pAttrs.remove(attribute.standard.PrinterResolution)
                pAttrs.add(attribute.standard.PrinterResolution(GlobalVars.defaultDPI, GlobalVars.defaultDPI, attribute.standard.PrinterResolution.DPI))

            if not printer_job.printDialog(pAttrs):
                myPrint("DB","User aborted the Print Dialog setup screen, so exiting...")
                return

            selectedPrintService = printer_job.getPrintService()

            toFile = pAttrs.containsKey(attribute.standard.Destination)

            # noinspection PyUnusedLocal
            printURI = printFile = printFilePath = printFileSplit = None
            if toFile:
                printURI = pAttrs.get(attribute.standard.Destination).getURI()
                myPrint("B", "User has selected to print to destination: %s (may be split into two files/parts)" %(printURI))
                if printURI.getScheme().lower().startswith("file"):
                    printFile = File(printURI)
                    printFilePath = printFile.getCanonicalPath()
                    printFileSplit = list(os.path.splitext(printFilePath))
                    if printFileSplit[0].endswith("."): printFileSplit[0] = printFileSplit[0][:-1]                      # noqa
                else:
                    toFile = False
            else:
                myPrint("DB", "User selected print service:", selectedPrintService)

            thePageFormat = printer_job.getPageFormat(pAttrs)

            header = MessageFormat(_theTitle)
            footer = MessageFormat("- page {0} -")

            # NOTE: _ there is a bug in VAqua... The JTable.print() method doesn't work!!
            vaqua_laf = "com.apple.laf.AquaLookAndFeel"                                                                 # noqa
            metal_laf = "javax.swing.plaf.metal.MetalLookAndFeel"

            the_laf = None
            using_vaqua = False
            if Platform.isOSX():
                the_laf = UIManager.getLookAndFeel()
                if "vaqua" in the_laf.getName().lower():                                                                # noqa
                    using_vaqua = True
                    myPrint("B", "VAqua LAF Detected... Must switch the LAF for print to work (due to a Java Bug)....")

                    # Without this the JMenuBar gets messed up
                    save_useScreenMenuBar= System.getProperty("apple.laf.useScreenMenuBar")
                    if save_useScreenMenuBar is None or save_useScreenMenuBar == "": save_useScreenMenuBar= System.getProperty("com.apple.macos.useScreenMenuBar")
                    System.setProperty("apple.laf.useScreenMenuBar", "false")
                    System.setProperty("com.apple.macos.useScreenMenuBar", "false")

                    UIManager.setLookAndFeel(metal_laf)     # Really don't like doing this....!

            try:
                if using_vaqua:
                    myPrint("DB", "... Updating the JFrame()'s component tree to the temporary LAF....")
                    SwingUtilities.updateComponentTreeUI(_theFrame)

                if _secondJTable is None:
                    printer_job.setPrintable(_theJTable.getPrintable(JTable.PrintMode.FIT_WIDTH, header, footer), thePageFormat)        # noqa
                    eval("printer_job.print(pAttrs)")
                else:

                    # java.awt.print.Book() won't work as it passes the book page number instead of the Printable's page number...
                    footer = MessageFormat("<page {0} : continued on the next page>")
                    if toFile:
                        pAttrs.remove(attribute.standard.Destination)
                        newPath = printFileSplit[0]+"_part1" + printFileSplit[1]
                        myPrint("DB","Print to file (main section) changed to %s" %(newPath))
                        pAttrs.add(attribute.standard.Destination(File(newPath).toURI()))
                    printer_job.setPrintable(_theJTable.getPrintable(JTable.PrintMode.FIT_WIDTH, header, footer), thePageFormat)        # noqa
                    eval("printer_job.print(pAttrs)")
                    # for atr in pAttrs.toArray(): myPrint("DB", "Printer attributes after .print()1: %s:%s" %(atr.getName(), atr))

                    header = MessageFormat(_theTitle+" (Total/Summary Table)")
                    footer = MessageFormat("<END>")

                    if toFile:
                        pAttrs.remove(attribute.standard.Destination)
                        newPath = printFileSplit[0]+"_part2" + printFileSplit[1]
                        myPrint("DB","Print to file (summary table) changed to %s" %(newPath))
                        pAttrs.add(attribute.standard.Destination(File(newPath).toURI()))
                    printer_job.setPrintable(_secondJTable.getPrintable(JTable.PrintMode.FIT_WIDTH, header, footer), thePageFormat)    # noqa
                    eval("printer_job.print(pAttrs)")
                    # for atr in pAttrs.toArray(): myPrint("DB", "Printer attributes after .print()2: %s:%s" %(atr.getName(), atr))

            except:
                myPrint("B", "ERROR: Printing routines failed?")
                dump_sys_error_to_md_console_and_errorlog()
                toFile = False                                                                                          # noqa
                raise

            finally:
                if using_vaqua:
                    UIManager.setLookAndFeel(the_laf)     # Switch back quick
                    myPrint("B", "...quick switch of LAF to print complete. LAF restored to:", UIManager.getLookAndFeel())

                    myPrint("DB", "... Switching the JFrame()'s component tree back to VAqua....")
                    SwingUtilities.updateComponentTreeUI(_theFrame)

                    # Without this the JMenuBar gets screwed up
                    System.setProperty("apple.laf.useScreenMenuBar", save_useScreenMenuBar)                             # noqa
                    System.setProperty("com.apple.macos.useScreenMenuBar", save_useScreenMenuBar)                       # noqa

            while pAttrs.containsKey(attribute.standard.JobName): pAttrs.remove(attribute.standard.JobName)
            while pAttrs.containsKey(attribute.standard.Destination): pAttrs.remove(attribute.standard.Destination)

            myPrint("DB", "Saving current print service:", printer_job.getPrintService())
            GlobalVars.defaultPrinterAttributes = attribute.HashPrintRequestAttributeSet(pAttrs)
            GlobalVars.defaultPrintService = printer_job.getPrintService()

            if toFile: myPopupInformationBox(_theFrame,"NOTE: Output destination changed: '_part1' & '_part2' appended to filename")

        except:
            myPrint("B", "ERROR in printing routines.....:"); dump_sys_error_to_md_console_and_errorlog()

        return

    class MyJScrollPaneForJOptionPane(JScrollPane, HierarchyListener):   # Allows a scrollable/resizeable menu in JOptionPane
        def __init__(self, _component, _frame, _max_w=800, _max_h=600):
            super(JScrollPane, self).__init__(_component)
            self.maxWidth = _max_w
            self.maxHeight = _max_h
            self.parentFrame = _frame
            self.borders = 90
            self.screenSize = Toolkit.getDefaultToolkit().getScreenSize()
            self.setOpaque(False)
            self.setViewportBorder(EmptyBorder(5, 5, 5, 5))
            self.addHierarchyListener(self)

        def getPreferredSize(self):
            if self.parentFrame is None:
                frame_width = 1024
                frame_height = 768
            else:
                frame_width = int(round((self.parentFrame.getSize().width - self.borders) *.9,0))
                frame_height = int(round((self.parentFrame.getSize().height - self.borders) *.9,0))
            return Dimension(min(self.maxWidth, frame_width), min(self.maxHeight, frame_height))

        def hierarchyChanged(self, e):                                                                                  # noqa
            dialog = SwingUtilities.getWindowAncestor(self)
            if isinstance(dialog, Dialog):
                if not dialog.isResizable():
                    dialog.setResizable(True)

    def getExtractChoice(defaultSelection):
        _exit = False

        extnSettings = getExtensionDatasetSettings()
        EXTN_PREF_KEY_AUTO_EXTRACT_WHEN_FILE_CLOSING = "auto_extract_when_file_closing"

        _userFilters = JPanel(GridLayout(0, 1))
        user_stockglance2020 = JRadioButton("StockGlance2020 - display consolidated stock info on screen **OR** extract to csv", False)
        user_reminders = JRadioButton("Reminders - display on screen **OR** extract to csv", False)
        user_account_txns = JRadioButton("Account register transactions - extract to csv (attachments optional)", False)
        user_investment_txns = JRadioButton("Investment transactions - extract to csv (attachments optional)", False)
        user_security_balances = JRadioButton("Security Balances - extract to csv", False)
        user_price_history = JRadioButton("Currency price history - extract to csv (simple or detailed formats)", False)
        user_extract_trunk = JRadioButton("Decrypt & extract raw Trunk file", False)
        user_extract_json = JRadioButton("Extract raw data as JSON file", False)
        user_extract_attachments = JRadioButton("Attachments - extract to disk", False)
        user_AccountNumbers = JRadioButton("Produce report of Accounts and bank/account number information (Useful for legacy / Will making)", False)
        user_autoExtractWhenFileClosing = JCheckBox("Enable auto extract EVERY TIME this dataset closes (USE WITH CARE!)?", extnSettings.getBoolean(EXTN_PREF_KEY_AUTO_EXTRACT_WHEN_FILE_CLOSING, False))
        user_autoExtractWhenFileClosing.setToolTipText("WARNING: When enabled, all the selected 'auto extracts' will execute every time this dataset closes!")

        bg = ButtonGroup()
        bg.add(user_stockglance2020)
        bg.add(user_reminders)
        bg.add(user_account_txns)
        bg.add(user_investment_txns)
        bg.add(user_security_balances)
        bg.add(user_price_history)
        bg.add(user_extract_trunk)
        bg.add(user_extract_json)
        bg.add(user_extract_attachments)
        bg.add(user_AccountNumbers)
        bg.clearSelection()

        if defaultSelection is not None:
            if defaultSelection == "_SG2020": user_stockglance2020.setSelected(True)
            elif defaultSelection == "_ERTC": user_reminders.setSelected(True)
            elif defaultSelection == "_EAR": user_account_txns.setSelected(True)
            elif defaultSelection == "_EIT": user_investment_txns.setSelected(True)
            elif defaultSelection == "_ESB": user_security_balances.setSelected(True)
            elif defaultSelection == "_ECH": user_price_history.setSelected(True)
            elif defaultSelection == "_ETRUNK": user_extract_trunk.setSelected(True)
            elif defaultSelection == "_JSON": user_extract_json.setSelected(True)
            elif defaultSelection == "_EATTACH": user_extract_attachments.setSelected(True)

        _userFilters.add(user_stockglance2020)
        _userFilters.add(user_reminders)
        _userFilters.add(user_account_txns)
        _userFilters.add(user_investment_txns)
        _userFilters.add(user_security_balances)
        _userFilters.add(user_price_history)
        _userFilters.add(user_extract_trunk)
        _userFilters.add(user_extract_json)
        _userFilters.add(user_extract_attachments)
        _userFilters.add(user_AccountNumbers)
        _userFilters.add(JLabel("---------"))
        _userFilters.add(user_autoExtractWhenFileClosing)

        _lExtractStockGlance2020 = _lExtractReminders = _lExtractAccountTxns = _lExtractInvestmentTxns = _lExtractSecurityBalances = _lExtractCurrencyHistory = _lExtractTrunk = _lExtractJSON = _lExtractAttachments = False

        class WarningMessage(AbstractAction):
            def __init__(self, _dialog, _user_autoExtractWhenFileClosing):
                self.dialog = _dialog
                self.user_autoExtractWhenFileClosing = _user_autoExtractWhenFileClosing
                self.enableListener = True

            def setEnableListener(self, _enableListener): self.enableListener = _enableListener
            def isEnableListener(self,): return self.enableListener

            def actionPerformed(self, event):
                if self.isEnabled():
                    option = event.getSource()
                    if isinstance(option, JCheckBox): pass
                    if option.isSelected():
                        if option is self.user_autoExtractWhenFileClosing:
                            _msg = "Are you really sure? This will trigger auto extract every time this dataset closes!"
                            if not myPopupAskQuestion(theParent=self.dialog, theTitle="WARNING", theQuestion=_msg):
                                option.setSelected(False)
                        else: raise Exception("LOGIC ERROR: event unknown: %s; %s" %(option, event))
                else:
                    myPrint("DB", "@@ WarningMessage:: .actionPerformed() - disabled - doing nothing....")


        _options = ["EXIT", "PROCEED"]

        while True:
            rowHeight = 24
            rows = 12
            jsp = MyJScrollPaneForJOptionPane(_userFilters, None, 750, rows * rowHeight)
            pane = JOptionPane()
            pane.setIcon(getMDIcon(lAlwaysGetIcon=True))
            pane.setMessage(jsp)
            pane.setMessageType(JOptionPane.QUESTION_MESSAGE)
            pane.setOptionType(JOptionPane.OK_CANCEL_OPTION)
            pane.setOptions(_options)
            dlg = pane.createDialog(extract_data_frame_, "EXTRACT DATA: SELECT OPTION")
            warnAlert = WarningMessage(dlg, user_autoExtractWhenFileClosing)
            user_autoExtractWhenFileClosing.addActionListener(warnAlert)
            dlg.setVisible(True)

            rtnValue = pane.getValue()
            _userAction = -1
            for i in range(0, len(_options)):
                if _options[i] == rtnValue:
                    _userAction = i
                    break

            if _userAction != 1:
                myPrint("B", "User chose to exit....")
                _exit = True
                break

            if user_stockglance2020.isSelected():
                myPrint("B", "StockGlance2020 investment extract option has been chosen")
                _lExtractStockGlance2020 = True
                break

            if user_reminders.isSelected():
                myPrint("B", "Reminders display / extract option has been chosen")
                _lExtractReminders = True
                break

            if user_account_txns.isSelected():
                myPrint("B", "Account Transactions extract option has been chosen")
                _lExtractAccountTxns = True
                break

            if user_investment_txns.isSelected():
                myPrint("B","Investment Transactions extract option has been chosen")
                _lExtractInvestmentTxns = True
                break

            if user_security_balances.isSelected():
                myPrint("B", "Security Balances extract option has been chosen")
                _lExtractSecurityBalances = True
                break

            if user_price_history.isSelected():
                myPrint("B", "Currency Price History extract option has been chosen")
                _lExtractCurrencyHistory = True
                break

            if user_extract_trunk.isSelected():
                myPrint("B", "Decrypt & extract raw Trunk file option has been chosen")
                _lExtractTrunk  = True
                break

            if user_extract_json.isSelected():
                myPrint("B", "Extract raw data as JSON file option has been chosen")
                _lExtractJSON  = True
                break

            if user_extract_attachments.isSelected():
                myPrint("B", "Attachments extract option has been chosen")
                _lExtractAttachments  = True
                break

            if user_AccountNumbers.isSelected():
                myPrint("B", "Produce report of Accounts and bank/account number information (Useful for legacy / Will making) - has been chosen")
                myPopupInformationBox(extract_data_frame_, "PLEASE USE Toolbox Extension >> 'MENU: Account & Category Tools' to produce the Account Numbers report", "USE TOOLBOX", theMessageType=JOptionPane.WARNING_MESSAGE)
                continue

            continue

        extnSettings.put(EXTN_PREF_KEY_AUTO_EXTRACT_WHEN_FILE_CLOSING, user_autoExtractWhenFileClosing.isSelected())
        myPrint("DB", "'%s' parameter set to: %s" %(EXTN_PREF_KEY_AUTO_EXTRACT_WHEN_FILE_CLOSING, extnSettings.getBoolean(EXTN_PREF_KEY_AUTO_EXTRACT_WHEN_FILE_CLOSING, False)))

        myPrint("DB", "Saving Extension's Dataset Settings(s) back to local storage..." )
        saveExtensionDatasetSettings(extnSettings)

        if user_stockglance2020.isSelected():       newDefault = "_SG2020"
        elif user_reminders.isSelected():           newDefault = "_ERTC"
        elif user_account_txns.isSelected():        newDefault = "_EAR"
        elif user_investment_txns.isSelected():     newDefault = "_EIT"
        elif user_security_balances.isSelected():   newDefault = "_ESB"
        elif user_price_history.isSelected():       newDefault = "_ECH"
        elif user_extract_trunk.isSelected():       newDefault = "_ETRUNK"
        elif user_extract_json.isSelected():        newDefault = "_JSON"
        elif user_extract_attachments.isSelected(): newDefault = "_EATTACH"
        else:                                       newDefault = None

        return _exit, newDefault, _lExtractStockGlance2020, _lExtractReminders, _lExtractAccountTxns, _lExtractInvestmentTxns, _lExtractSecurityBalances, _lExtractCurrencyHistory, _lExtractTrunk, _lExtractJSON, _lExtractAttachments

    def validateCSVFileDelimiter(requestedDelimiter=None):
        decimalStrings = [".", ","]
        delimStrings = GlobalVars.ALLOWED_CSV_FILE_DELIMITER_STRINGS
        currentDecimal = MD_REF.getPreferences().getDecimalChar()
        if currentDecimal not in decimalStrings:
            myPrint("B", "@@ WARNING: MD Decimal ('%s') appears invalid... Overriding to '.' @@" %(currentDecimal))
            currentDecimal = "."
        if requestedDelimiter is None or not isinstance(requestedDelimiter, basestring) or len(requestedDelimiter) != 1:
            if currentDecimal != ",":
                requestedDelimiter = ","
            myPrint("DB", "Attempting to set default Delimiter >> will attempt: '%s'" %(requestedDelimiter))
        else:
            myPrint("DB", "Validating requested Delimiter: '%s'" %(requestedDelimiter))
        if currentDecimal in decimalStrings and requestedDelimiter in delimStrings and currentDecimal != requestedDelimiter:
            myPrint("DB", "Requested Delimiter: '%s' validated (current Decimal: '%s')" %(requestedDelimiter, currentDecimal))
            return requestedDelimiter
        if currentDecimal == ".":
            newDelimiter = ","            
        else:
            newDelimiter = ";"
        myPrint("B", "Invalid Delimiter: '%s' requested (Decimal: '%s') >> OVERRIDING Delimiter to: '%s'"
                %(requestedDelimiter, currentDecimal, newDelimiter))
        return newDelimiter

    def listCommonExtractParameters():
        myPrint("B","---------------------------------------------------------------------------------------")
        myPrint("B","Common Data Extract Parameters: All extracts:")
        myPrint("B", "  Strip non-ASCII characters...........: %s" %(lStripASCII))
        myPrint("B", "  Add BOM to front of file.............: %s" %(lWriteBOMToExportFile_SWSS))
        myPrint("B", "  Write Parameters to end of file......: %s" %(lWriteParametersToExportFile_SWSS))
        myPrint("B", "  CSV extract Delimiter................: %s" %(csvDelimiter))
        myPrint("B","---------------------------------------------------------------------------------------")

    def listExtractSG2020Parameters():
        myPrint("B","---------------------------------------------------------------------------------------")
        myPrint("B","Parameters: Extract StockGlance2020:")
        myPrint("B", "  Hide Hidden Securities...............:", hideHiddenSecurities)
        myPrint("B", "  Hide Inactive Accounts...............:", hideInactiveAccounts)
        myPrint("B", "  Hide Hidden Accounts.................:", hideHiddenAccounts)
        myPrint("B", "  Currency filter......................: %s '%s'" %(lAllCurrency, filterForCurrency))
        myPrint("B", "  Security filter......................: %s '%s'" %(lAllSecurity, filterForSecurity))
        myPrint("B", "  Account filter.......................: %s '%s'" %(lAllAccounts, filterForAccounts))
        myPrint("B", "  Include Cash Balances (per account)..:", lIncludeCashBalances)
        myPrint("B", "  Split Securities by Account..........:", lSplitSecuritiesByAccount)
        myPrint("B", "  Include Future Balances..............:", lIncludeFutureBalances_SG2020)
        myPrint("B", "  Exclude Totals from extract..........:", lExcludeTotalsFromCSV)
        myPrint("B", "  Use Current Price (else Price Hist.).:", lUseCurrentPrice_SG2020)
        myPrint("B", "  Max decimal rounding on calc'd prices:", maxDecimalPlacesRounding_SG2020)
        myPrint("B", "  Auto Extract.........................:", autoExtract_SG2020)
        myPrint("B","---------------------------------------------------------------------------------------")

    def setupExtractSG2020Parameters():
        # ####################################################
        # STOCKGLANCE2020 PARAMETER SCREEN
        # ####################################################
        global debug
        global lWriteParametersToExportFile_SWSS

        global lDidIUseAttachmentDir
        global headingNames
        global _SHRS_FORMATTED, _SHRS_RAW, _PRICE_FORMATTED, _PRICE_RAW, _CVALUE_FORMATTED, _CVALUE_RAW, _BVALUE_FORMATTED, _BVALUE_RAW
        global _CBVALUE_FORMATTED, _CBVALUE_RAW, _GAIN_FORMATTED, _GAIN_RAW, _SORT, _EXCLUDECSV, _GAINPCT
        global acctSeparator

        global __extract_data, extract_filename
        global lStripASCII, csvDelimiter, userdateformat, lWriteBOMToExportFile_SWSS
        global hideInactiveAccounts, hideHiddenAccounts, hideHiddenSecurities
        global lAllSecurity, filterForSecurity, lAllAccounts, filterForAccounts, lAllCurrency, filterForCurrency
        global whichDefaultExtractToRun_SWSS
        global lIncludeCashBalances, _column_widths_SG2020
        global lSplitSecuritiesByAccount, lExcludeTotalsFromCSV
        global maxDecimalPlacesRounding_SG2020, lUseCurrentPrice_SG2020
        global lIncludeFutureBalances_SG2020

        global autoExtract_SG2020

        label1 = JLabel("Hide Hidden Securities?")
        user_hideHiddenSecurities = JCheckBox("", hideHiddenSecurities)

        label2 = JLabel("Hide Inactive Accounts?")
        user_hideInactiveAccounts = JCheckBox("", hideInactiveAccounts)

        label3 = JLabel("Hide Hidden Accounts?")
        user_hideHiddenAccounts = JCheckBox("", hideHiddenAccounts)

        label4 = JLabel("Filter for Currency containing text '...' or ALL:")
        user_selectCurrency = JTextField(5)
        user_selectCurrency.setDocument(JTextFieldLimitYN(5, True, "CURR"))
        if lAllCurrency: user_selectCurrency.setText("ALL")
        else:            user_selectCurrency.setText(filterForCurrency)

        label5 = JLabel("Filter for Security/Ticker containing text '...' or ALL:")
        user_selectTicker = JTextField(12)
        user_selectTicker.setDocument(JTextFieldLimitYN(12, True, "CURR"))
        if lAllSecurity: user_selectTicker.setText("ALL")
        else:            user_selectTicker.setText(filterForSecurity)

        label6 = JLabel("Filter for Accounts containing text '...' (or ALL):")
        user_selectAccounts = JTextField(12)
        user_selectAccounts.setDocument(JTextFieldLimitYN(20, True, "CURR"))
        if lAllAccounts: user_selectAccounts.setText("ALL")
        else:            user_selectAccounts.setText(filterForAccounts)

        label7 = JLabel("Include Cash Balances for each account?")
        user_selectCashBalances = JCheckBox("", lIncludeCashBalances)

        label7b = JLabel("Split Security Qtys by Account?")
        user_splitSecurities = JCheckBox("", lSplitSecuritiesByAccount)

        labelFutureBalances = JLabel("Include Future Balances (rather than current)?")
        user_includeFutureBalances = JCheckBox("", lIncludeFutureBalances_SG2020)

        label7c = JLabel("Exclude Totals from CSV extract (helps pivots)?")
        user_excludeTotalsFromCSV = JCheckBox("", lExcludeTotalsFromCSV)

        labelUseCurrentPrice = JLabel("Ticked = Use 'Current Price' (else latest dated history price)")
        user_useCurrentPrice = JCheckBox("", lUseCurrentPrice_SG2020)

        labelMaxDecimalRounding = JLabel("Set maximum decimal rounding on calculated price (default=4)")
        user_maxDecimalRounding = JTextField(2)
        user_maxDecimalRounding.setText(str(maxDecimalPlacesRounding_SG2020))

        labelRC = JLabel("Reset Column Widths to Defaults?")
        user_selectResetColumns = JCheckBox("", False)

        label8 = JLabel("Strip non ASCII characters from CSV extract?")
        user_selectStripASCII = JCheckBox("", lStripASCII)

        label9 = JLabel("Change CSV extract Delimiter from default:")
        user_selectDELIMITER = JComboBox(GlobalVars.ALLOWED_CSV_FILE_DELIMITER_STRINGS)
        user_selectDELIMITER.setSelectedItem(csvDelimiter)

        labelBOM = JLabel("Write BOM (Byte Order Mark) to file (helps Excel open files)?")
        user_selectBOM = JCheckBox("", lWriteBOMToExportFile_SWSS)

        labelExportParameters = JLabel("Write parameters out to file (added as rows at EOF)?")
        user_ExportParameters = JCheckBox("", lWriteParametersToExportFile_SWSS)

        labelAutoExtract = JLabel("Enable Auto Extract?")
        user_AutoExtract = JCheckBox("", autoExtract_SG2020)

        label10 = JLabel("Turn DEBUG Verbose messages on?")
        user_selectDEBUG = JCheckBox("", debug)

        userFilters = JPanel(GridLayout(0, 2))
        userFilters.add(label1)
        userFilters.add(user_hideHiddenSecurities)
        userFilters.add(label2)
        userFilters.add(user_hideInactiveAccounts)
        userFilters.add(label3)
        userFilters.add(user_hideHiddenAccounts)
        userFilters.add(label4)
        userFilters.add(user_selectCurrency)
        userFilters.add(label5)
        userFilters.add(user_selectTicker)
        userFilters.add(label6)
        userFilters.add(user_selectAccounts)
        userFilters.add(label7)
        userFilters.add(user_selectCashBalances)
        userFilters.add(label7b)
        userFilters.add(user_splitSecurities)
        userFilters.add(labelFutureBalances)
        userFilters.add(user_includeFutureBalances)
        userFilters.add(label7c)
        userFilters.add(user_excludeTotalsFromCSV)
        userFilters.add(labelUseCurrentPrice)
        userFilters.add(user_useCurrentPrice)
        userFilters.add(labelMaxDecimalRounding)
        userFilters.add(user_maxDecimalRounding)
        userFilters.add(labelRC)
        userFilters.add(user_selectResetColumns)
        userFilters.add(label8)
        userFilters.add(user_selectStripASCII)
        userFilters.add(label9)
        userFilters.add(user_selectDELIMITER)
        userFilters.add(labelBOM)
        userFilters.add(user_selectBOM)
        userFilters.add(labelExportParameters)
        userFilters.add(user_ExportParameters)
        userFilters.add(labelAutoExtract)
        userFilters.add(user_AutoExtract)
        userFilters.add(label10)
        userFilters.add(user_selectDEBUG)

        _exit = False

        options = ["Abort", "Display Data", "CSV Extract Data"]

        rowHeight = 24
        rows = 20
        jsp = MyJScrollPaneForJOptionPane(userFilters, None, 1100, rows * rowHeight)
        userAction = (JOptionPane.showOptionDialog(extract_data_frame_,
                                                   jsp,
                                                   "StockGlance2020 - Summarise Stocks/Funds: Set Script Parameters....",
                                                   JOptionPane.OK_CANCEL_OPTION,
                                                   JOptionPane.QUESTION_MESSAGE,
                                                   getMDIcon(lAlwaysGetIcon=True),
                                                   options,
                                                   options[1]))
        if userAction == 1:  # Display Data
            myPrint("DB", "Display Data (no extract) selected")
            GlobalVars.DISPLAY_DATA = True
            GlobalVars.EXTRACT_DATA = False
        elif userAction == 2:  # CSV Extract Data
            myPrint("DB", "Extract Data (no display) selected")
            GlobalVars.DISPLAY_DATA = False
            GlobalVars.EXTRACT_DATA = True
        else:
            myPrint("B", "User Cancelled Parameter selection.. Will abort..")
            _exit = True
            GlobalVars.DISPLAY_DATA = False
            GlobalVars.EXTRACT_DATA = False

        if not _exit:
            if user_selectResetColumns.isSelected():
                myPrint("B","User asked to reset columns.... Resetting Now....")
                _column_widths_SG2020=[]  # This will invalidate the

            hideHiddenSecurities = user_hideHiddenSecurities.isSelected()
            hideInactiveAccounts = user_hideInactiveAccounts.isSelected()
            hideHiddenAccounts = user_hideHiddenAccounts.isSelected()

            if user_selectCurrency.getText() == "ALL" or user_selectCurrency.getText().strip() == "":
                lAllCurrency = True
                filterForCurrency = "ALL"
            else:
                lAllCurrency = False
                filterForCurrency = user_selectCurrency.getText()

            if user_selectTicker.getText() == "ALL" or user_selectTicker.getText().strip() == "":
                lAllSecurity = True
                filterForSecurity = "ALL"
            else:
                lAllSecurity = False
                filterForSecurity = user_selectTicker.getText()

            if user_selectAccounts.getText() == "ALL" or user_selectAccounts.getText().strip() == "":
                lAllAccounts = True
                filterForAccounts = "ALL"
            else:
                lAllAccounts = False
                filterForAccounts = user_selectAccounts.getText()

            lIncludeCashBalances = user_selectCashBalances.isSelected()
            lSplitSecuritiesByAccount = user_splitSecurities.isSelected()
            lExcludeTotalsFromCSV = user_excludeTotalsFromCSV.isSelected()
            lIncludeFutureBalances_SG2020 = user_includeFutureBalances.isSelected()

            lUseCurrentPrice_SG2020 = user_useCurrentPrice.isSelected()
            del user_useCurrentPrice, labelUseCurrentPrice

            getVal = user_maxDecimalRounding.getText()
            if StringUtils.isInteger(getVal) and int(getVal) >= 0 and int(getVal) <= 12:
                maxDecimalPlacesRounding_SG2020 = int(getVal)
            else:
                myPrint("B", "Parameter Max Decimal Places '%s 'invalid, overriding to a default of max 4pc rounding...." %(getVal))
                maxDecimalPlacesRounding_SG2020 = 4
            del user_maxDecimalRounding, labelMaxDecimalRounding

            lStripASCII = user_selectStripASCII.isSelected()

            csvDelimiter = validateCSVFileDelimiter(user_selectDELIMITER.getSelectedItem())

            lWriteBOMToExportFile_SWSS = user_selectBOM.isSelected()
            lWriteParametersToExportFile_SWSS = user_ExportParameters.isSelected()
            autoExtract_SG2020 = user_AutoExtract.isSelected()

            debug = user_selectDEBUG.isSelected()

            listExtractSG2020Parameters()

        return _exit

    def listExtractRemindersParameters():
        myPrint("B","---------------------------------------------------------------------------------------")
        myPrint("B","Parameters: Extract Reminders:")
        myPrint("B", "  User date format.....................:", userdateformat)
        myPrint("B", "  Calc. Future Reminders (Extract only):", lExtractFutureRemindersToo_ERTC)
        myPrint("B", "  Future Reminders: Look Forward Days..:", GlobalVars.daysToLookForward_LFR)
        myPrint("B", "  Auto Extract.........................:", autoExtract_ERTC,
                "Cutoff: '%s'"%(convertStrippedIntDateFormattedText(DateUtil.incrementDate(DateUtil.getStrippedDateInt(), 0, 0, GlobalVars.daysToLookForward_LFR))))
        myPrint("B","---------------------------------------------------------------------------------------")

    def setupExtractRemindersParameters():
        # ####################################################
        # EXTRACT_REMINDERS_CSV PARAMETER SCREEN
        # ####################################################

        global debug
        global lWriteParametersToExportFile_SWSS

        global lDidIUseAttachmentDir
        global csvheaderline, headerFormats
        global focus, row, EditedReminderCheck, ReminderTable_Count, ExtractDetails_Count

        global __extract_data, extract_filename
        global lStripASCII, csvDelimiter, userdateformat, lWriteBOMToExportFile_SWSS
        global hideInactiveAccounts, hideHiddenAccounts, hideHiddenSecurities
        global lAllSecurity, filterForSecurity, lAllAccounts, filterForAccounts, lAllCurrency, filterForCurrency
        global whichDefaultExtractToRun_SWSS
        global _column_widths_ERTC, lExtractFutureRemindersToo_ERTC

        global autoExtract_ERTC

        # 1=dd/mm/yyyy, 2=mm/dd/yyyy, 3=yyyy/mm/dd, 4=yyyymmdd
        dateStrings = ["dd/mm/yyyy", "mm/dd/yyyy", "yyyy/mm/dd", "yyyymmdd"]

        label1 = JLabel("Select Output Date Format (default yyyy/mm/dd):")
        user_dateformat = JComboBox(dateStrings)

        if userdateformat == "%d/%m/%Y": user_dateformat.setSelectedItem("dd/mm/yyyy")
        elif userdateformat == "%m/%d/%Y": user_dateformat.setSelectedItem("mm/dd/yyyy")
        elif userdateformat == "%Y%m%d": user_dateformat.setSelectedItem("yyyymmdd")
        else: user_dateformat.setSelectedItem("yyyy/mm/dd")

        labelEFR = JLabel("Calculate Future Reminders too (Extract Only)?")
        user_selectEFR = JCheckBox("", lExtractFutureRemindersToo_ERTC)

        labelDaysLookForward = JLabel("Future Reminders days to look forward?")
        user_daysLookForward = JTextField(3)
        user_daysLookForward.setText(str(GlobalVars.daysToLookForward_LFR))

        labelRC = JLabel("Reset Column Widths to Defaults?")
        user_selectResetColumns = JCheckBox("", False)

        label2 = JLabel("Strip non ASCII characters from CSV extract?")
        user_selectStripASCII = JCheckBox("", lStripASCII)

        label3 = JLabel("Change CSV extract Delimiter from default:")
        user_selectDELIMITER = JComboBox(GlobalVars.ALLOWED_CSV_FILE_DELIMITER_STRINGS)
        user_selectDELIMITER.setSelectedItem(csvDelimiter)

        labelBOM = JLabel("Write BOM (Byte Order Mark) (helps Excel open files)?")
        user_selectBOM = JCheckBox("", lWriteBOMToExportFile_SWSS)

        labelExportParameters = JLabel("Write parameters out to file (added as rows at EOF)?")
        user_ExportParameters = JCheckBox("", lWriteParametersToExportFile_SWSS)

        labelAutoExtract = JLabel("Enable Auto Extract?")
        user_AutoExtract = JCheckBox("", autoExtract_ERTC)

        label4 = JLabel("Turn DEBUG Verbose messages on?")
        user_selectDEBUG = JCheckBox("", debug)


        userFilters = JPanel(GridLayout(0, 2))
        userFilters.add(label1)
        userFilters.add(user_dateformat)
        userFilters.add(labelEFR)
        userFilters.add(user_selectEFR)
        userFilters.add(labelDaysLookForward)
        userFilters.add(user_daysLookForward)
        userFilters.add(labelRC)
        userFilters.add(user_selectResetColumns)
        userFilters.add(label2)
        userFilters.add(user_selectStripASCII)
        userFilters.add(label3)
        userFilters.add(user_selectDELIMITER)
        userFilters.add(labelBOM)
        userFilters.add(user_selectBOM)
        userFilters.add(labelExportParameters)
        userFilters.add(user_ExportParameters)
        userFilters.add(labelAutoExtract)
        userFilters.add(user_AutoExtract)
        userFilters.add(label4)
        userFilters.add(user_selectDEBUG)

        _exit = False

        options = ["Abort", "Display Data", "CSV Extract Data"]
        rowHeight = 24
        rows = 11
        jsp = MyJScrollPaneForJOptionPane(userFilters, None, 800, rows * rowHeight)
        userAction = (JOptionPane.showOptionDialog( extract_data_frame_,
                                                    jsp,
                                                    "EXTRACT REMINDERS: Set Script Parameters....",
                                                    JOptionPane.OK_CANCEL_OPTION,
                                                    JOptionPane.QUESTION_MESSAGE,
                                                    getMDIcon(lAlwaysGetIcon=True),
                                                    options,
                                                    options[1]))

        if userAction == 1:  # Display Data
            myPrint("DB", "Display Data (no extract) selected")
            GlobalVars.DISPLAY_DATA = True
            GlobalVars.EXTRACT_DATA = False
        elif userAction == 2:  # CSV Extract Data
            myPrint("DB", "Extract Data (no display) selected")
            GlobalVars.DISPLAY_DATA = False
            GlobalVars.EXTRACT_DATA = True
        else:
            myPrint("B", "User Cancelled Parameter selection.. Will abort..")
            _exit = True
            GlobalVars.DISPLAY_DATA = False
            GlobalVars.EXTRACT_DATA = False

        if not _exit:

            debug = user_selectDEBUG.isSelected()

            if user_dateformat.getSelectedItem() == "dd/mm/yyyy": userdateformat = "%d/%m/%Y"
            elif user_dateformat.getSelectedItem() == "mm/dd/yyyy": userdateformat = "%m/%d/%Y"
            elif user_dateformat.getSelectedItem() == "yyyy/mm/dd": userdateformat = "%Y/%m/%d"
            elif user_dateformat.getSelectedItem() == "yyyymmdd": userdateformat = "%Y%m%d"
            else:
                userdateformat = "%Y/%m/%d"  # PROBLEM / default

            if user_selectEFR.isSelected():
                myPrint("DB", "User asked calculate and extract Future Reminders too....")
                lExtractFutureRemindersToo_ERTC = user_selectEFR.isSelected()

            days = user_daysLookForward.getText()
            if StringUtils.isEmpty(days): days = "0"

            if StringUtils.isInteger(days) and int(days) > 0 and int(days) <= 365:
                GlobalVars.daysToLookForward_LFR = int(days)
                myPrint("DB", "Future Reminders - Days to look forward changed set at: %s" %(GlobalVars.daysToLookForward_LFR))
            else:
                GlobalVars.daysToLookForward_LFR = 365
                myPrint("DB", "Future Reminders - Look forward days invalid (should be 1 to 365 days) - defaulting to 365....")

            if user_selectResetColumns.isSelected():
                myPrint("B", "User asked to reset columns.... Resetting Now....")
                _column_widths_ERTC = []  # This will invalidate them

            lStripASCII = user_selectStripASCII.isSelected()
            csvDelimiter = validateCSVFileDelimiter(user_selectDELIMITER.getSelectedItem())
            lWriteBOMToExportFile_SWSS = user_selectBOM.isSelected()
            lWriteParametersToExportFile_SWSS = user_ExportParameters.isSelected()
            autoExtract_ERTC = user_AutoExtract.isSelected()

            listExtractRemindersParameters()

        return _exit

    def listExtractAccountTxnsParameters():
        myPrint("B","---------------------------------------------------------------------------------------")
        myPrint("B","Parameters: Extract Account Registers:")

        if GlobalVars.dropDownAccount_EAR:
            myPrint("B", "  Dropdown Account selected............: %s" %(GlobalVars.dropDownAccount_EAR.getAccountName()))         # noqa
            myPrint("B", "  Include Sub Accounts.................: %s" %(lIncludeSubAccounts_EAR))
        else:
            myPrint("B", "  Hide Inactive Accounts...............:", hideInactiveAccounts)
            myPrint("B", "  Hide Hidden Accounts.................:", hideHiddenAccounts)
            myPrint("B", "  Account filter.......................: %s '%s'" %(lAllAccounts, filterForAccounts))
            myPrint("B", "  Currency filter......................: %s '%s'" %(lAllCurrency, filterForCurrency))

        myPrint("B", "  Date range...........................: %s" %(saveDropDownDateRange_EAR))
        myPrint("B", "  Selected Start Date..................: %s" %(userdateStart_EAR))
        myPrint("B", "  Selected End Date....................: %s" %(userdateEnd_EAR))
        myPrint("B", "  Tag filter...........................: %s '%s'" %(lAllTags_EAR, tagFilter_EAR))
        myPrint("B", "  Text filter..........................: %s '%s'" %(lAllText_EAR, textFilter_EAR))
        myPrint("B", "  Categories filter....................: %s '%s'" %(lAllCategories_EAR, categoriesFilter_EAR))
        myPrint("B", "  Include Unadjusted Opening Balances..:", lIncludeOpeningBalances_EAR)
        myPrint("B", "  Including Balance Adjustments........:", lIncludeBalanceAdjustments_EAR)
        myPrint("B", "  Download Attachments.................: %s" %(lExtractAttachments_EAR))
        myPrint("B", "  Auto Extract.........................:", autoExtract_EAR)
        myPrint("B", "  User date format.....................:", userdateformat)
        myPrint("B","---------------------------------------------------------------------------------------")

    def setupExtractAccountTxnsParameters():
        # ##############################################
        # EXTRACT_ACCOUNT_REGISTERS_CSV PARAMETER SCREEN
        # ##############################################

        global debug
        global lWriteParametersToExportFile_SWSS

        global lDidIUseAttachmentDir
        global dataKeys, attachmentDir, relativePath

        global __extract_data, extract_filename
        global lStripASCII, csvDelimiter, userdateformat, lWriteBOMToExportFile_SWSS
        global hideInactiveAccounts, hideHiddenAccounts, hideHiddenSecurities
        global lAllSecurity, filterForSecurity, lAllAccounts, filterForAccounts, lAllCurrency, filterForCurrency
        global whichDefaultExtractToRun_SWSS
        global lIncludeSubAccounts_EAR, lIncludeOpeningBalances_EAR, lIncludeBalanceAdjustments_EAR, userdateStart_EAR, userdateEnd_EAR, lAllTags_EAR, tagFilter_EAR
        global lAllText_EAR, textFilter_EAR, lAllCategories_EAR, categoriesFilter_EAR, lExtractAttachments_EAR, saveDropDownAccountUUID_EAR, saveDropDownDateRange_EAR, lIncludeInternalTransfers_EAR

        global autoExtract_EAR

        saveColor = JLabel("TEST").getForeground()

        _exit = False

        _userFilters = JPanel(GridLayout(0, 2))

        class PanelAction(AbstractAction):

            def __init__(self, thePanel):
                self.thePanel=thePanel

            def actionPerformed(self, event):
                myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event)

                theDateRangeDropDown = None
                theAccountDropdown = None
                theStartDate = None
                theEndDate = None

                theSubAccounts = None
                theHideInactiveAccounts = None
                theHideHiddenAccounts = None
                theFilterAccounts = None
                theFilterCurrency = None

                _components = self.thePanel.getComponents()
                for _theComponent in _components:
                    if isinstance(_theComponent, (JComboBox, JTextField, JCheckBox)):
                        if event.getSource().getName() == _theComponent.getName():
                            if _theComponent.getName() == "dateDropdown": theDateRangeDropDown  = _theComponent
                            if _theComponent.getName() == "accountDropdown": theAccountDropdown  = _theComponent

                        if _theComponent.getName() == "user_selectDateStart": theStartDate  = _theComponent
                        elif _theComponent.getName() == "user_selectDateEnd": theEndDate  = _theComponent
                        elif _theComponent.getName() == "user_includeSubAccounts": theSubAccounts  = _theComponent
                        elif _theComponent.getName() == "user_hideInactiveAccounts": theHideInactiveAccounts  = _theComponent
                        elif _theComponent.getName() == "user_hideHiddenAccounts": theHideHiddenAccounts  = _theComponent
                        elif _theComponent.getName() == "user_selectAccounts": theFilterAccounts  = _theComponent
                        elif _theComponent.getName() == "user_selectCurrency": theFilterCurrency  = _theComponent

                if not theDateRangeDropDown and not theAccountDropdown: return

                if theDateRangeDropDown:
                    _start, _end = getDateRange(theDateRangeDropDown.getSelectedItem())
                    if theDateRangeDropDown.getSelectedItem() == "custom_date":
                        theStartDate.setEnabled(True)
                        theEndDate.setEnabled(True)
                    else:
                        theStartDate.setEnabled(False)
                        theEndDate.setEnabled(False)

                    # noinspection PyUnresolvedReferences
                    theStartDate.setDateInt(_start)
                    # noinspection PyUnresolvedReferences
                    theEndDate.setDateInt(_end)

                if theAccountDropdown:

                    if isinstance(theAccountDropdown.getSelectedItem(),(str,unicode)):
                        theSubAccounts.setEnabled(False)
                        theHideInactiveAccounts.setEnabled(True)
                        theHideHiddenAccounts.setEnabled(True)
                        theFilterAccounts.setEnabled(True)
                        theFilterCurrency.setEnabled(True)

                        theSubAccounts.setSelected(False)

                    else:
                        theSubAccounts.setEnabled(True)
                        theHideInactiveAccounts.setEnabled(False)
                        theHideHiddenAccounts.setEnabled(False)
                        theFilterAccounts.setEnabled(False)
                        theFilterCurrency.setEnabled(False)

                        theHideInactiveAccounts.setSelected(True)
                        theHideHiddenAccounts.setSelected(True)
                        theFilterAccounts.setText("ALL")
                        theFilterCurrency.setText("ALL")

                myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
                return


        labelHideInactiveAccounts = JLabel("Hide Inactive Accounts?")
        user_hideInactiveAccounts = JCheckBox("", hideInactiveAccounts)
        user_hideInactiveAccounts.setName("user_hideInactiveAccounts")

        labelHideHiddenAccounts = JLabel("Hide Hidden Accounts?")
        user_hideHiddenAccounts = JCheckBox("", hideHiddenAccounts)
        user_hideHiddenAccounts.setName("user_hideHiddenAccounts")

        labelFilterCurrency = JLabel("Filter for Currency containing text '...' or ALL:")
        user_selectCurrency = JTextField(12)
        user_selectCurrency.setName("user_selectCurrency")
        user_selectCurrency.setDocument(JTextFieldLimitYN(30, True, "CURR"))
        if lAllCurrency: user_selectCurrency.setText("ALL")
        else:            user_selectCurrency.setText(filterForCurrency)

        # noinspection PyArgumentList
        class MyAcctFilterForDropdown(AcctFilter):

            def __init__(self):
                super(AcctFilter, self).__init__()

            def matches(self, acct):                                                                                    # noqa

                # noinspection PyUnresolvedReferences
                if not (acct.getAccountType() == Account.AccountType.BANK
                        or acct.getAccountType() == Account.AccountType.CREDIT_CARD
                        or acct.getAccountType() == Account.AccountType.LOAN
                        or acct.getAccountType() == Account.AccountType.LIABILITY
                        or acct.getAccountType() == Account.AccountType.ASSET):
                    return False

                # This logic replicates Moneydance AcctFilter.ACTIVE_ACCOUNTS_FILTER
                if (acct.getAccountOrParentIsInactive()): return False
                if (acct.getHideOnHomePage() and acct.getBalance() == 0): return False

                return True

        class StoreAccount:
            def __init__(self, _acct):
                if not isinstance(_acct, Account): raise Exception("Error: Object: %s(%s) is not an Account Object!" %(_acct, type(_acct)))
                self.acct = _acct

            def getAccount(self): return self.acct

            def __str__(self):      return "%s : %s" %(self.getAccount().getAccountType(), self.getAccount().getAccountName())
            def __repr__(self):     return self.__str__()
            def toString(self):     return self.__str__()


        labelSelectOneAccount = JLabel("Select One Account here....")
        mdAcctList = AccountUtil.allMatchesForSearch(MD_REF.getCurrentAccountBook(), MyAcctFilterForDropdown())
        textToUse = "<NONE SELECTED - USE FILTERS BELOW>"

        acctList = ArrayList()
        acctList.add(0,textToUse)
        for getAcct in mdAcctList: acctList.add(StoreAccount(getAcct))
        del mdAcctList

        accountDropdown = JComboBox(acctList)
        accountDropdown.setName("accountDropdown")

        if saveDropDownAccountUUID_EAR != "":
            findAccount = AccountUtil.findAccountWithID(MD_REF.getRootAccount(), saveDropDownAccountUUID_EAR)
            if findAccount is not None:
                for acctObj in acctList:
                    if isinstance(acctObj, StoreAccount) and acctObj.getAccount() == findAccount:
                        accountDropdown.setSelectedItem(acctObj)
                        break

        labelFilterAccounts = JLabel("Filter for Accounts containing text '...' (or ALL):")
        user_selectAccounts = JTextField(12)
        user_selectAccounts.setName("user_selectAccounts")
        user_selectAccounts.setDocument(JTextFieldLimitYN(30, True, "CURR"))
        if lAllAccounts: user_selectAccounts.setText("ALL")
        else:            user_selectAccounts.setText(filterForAccounts)

        labelIncludeSubAccounts = JLabel("Include Sub Accounts?:")
        user_includeSubAccounts = JCheckBox("", lIncludeSubAccounts_EAR)
        user_includeSubAccounts.setName("user_includeSubAccounts")

        labelSeparator1 = JLabel("-"*53)
        labelSeparator2 = JLabel("--<<Select Account above *OR* ACCT filters below>>---".upper())
        labelSeparator2.setForeground(getColorBlue())
        labelSeparator3 = JLabel("-"*53)                                                                                # noqa
        labelSeparator4 = JLabel("-"*53)                                                                                # noqa
        labelSeparator5 = JLabel("-"*53)
        labelSeparator6 = JLabel("------<<Filters below are AND (not OR)>> ------------")
        labelSeparator6.setForeground(getColorBlue())
        labelSeparator7 = JLabel("-"*53)
        labelSeparator8 = JLabel("-"*53)

        labelOpeningBalances = JLabel("Include Unadjusted Opening Balances?")
        user_selectOpeningBalances = JCheckBox("", lIncludeOpeningBalances_EAR)
        user_selectOpeningBalances.setName("user_selectOpeningBalances")

        labelBalancesAdjustments = JLabel("Include Balance Adjustments?")
        user_selectBalanceAdjustments = JCheckBox("", lIncludeBalanceAdjustments_EAR)
        user_selectBalanceAdjustments.setName("user_selectBalanceAdjustments")

        if isinstance(accountDropdown.getSelectedItem(),(str,unicode)):
            user_includeSubAccounts.setEnabled(False)
            user_hideInactiveAccounts.setEnabled(True)
            user_hideHiddenAccounts.setEnabled(True)
            user_selectAccounts.setEnabled(True)
            user_selectCurrency.setEnabled(True)

            user_includeSubAccounts.setSelected(False)

        else:
            user_includeSubAccounts.setSelected(True)
            user_hideInactiveAccounts.setEnabled(False)
            user_hideHiddenAccounts.setEnabled(False)
            user_selectAccounts.setEnabled(False)
            user_selectCurrency.setEnabled(False)

            user_hideInactiveAccounts.setSelected(True)
            user_hideHiddenAccounts.setSelected(True)
            user_selectAccounts.setText("ALL")
            user_selectCurrency.setText("ALL")

        # noinspection PyUnusedLocal
        labelIncludeTransfers = JLabel("Include Transfers between Accounts Selected in this Extract?")
        user_selectIncludeTransfers = JCheckBox("", lIncludeInternalTransfers_EAR)
        user_selectIncludeTransfers.setName("user_selectIncludeTransfers")

        dateOptions = [ "year_to_date",
                        "fiscal_year_to_date",
                        "last_fiscal_quarter",
                        "quarter_to_date",
                        "month_to_date",
                        "this_year",
                        "this_fiscal_year",
                        "this_quarter",
                        "this_month",
                        "this_week",
                        "last_year",
                        "last_fiscal_year",
                        "last_quarter",
                        "last_month",
                        "last_12_months",
                        "last_365_days",
                        "last_30_days",
                        "last_1_day",
                        "all_dates",
                        "custom_date",
                        "last_week",]

        def getDateRange(selectedOption):         # DateRange

            todayInt = Util.getStrippedDateInt()
            # yesterdayInt = DateUtil.incrementDate(todayInt, 0, 0, -1)

            if selectedOption == "year_to_date":
                return (DateUtil.firstDayInYear(todayInt), todayInt)
            elif selectedOption ==  "quarter_to_date":
                return (DateUtil.firstDayInQuarter(todayInt), todayInt)
            elif selectedOption ==  "month_to_date":
                return (DateUtil.firstDayInMonth(todayInt), todayInt)
            elif selectedOption ==  "this_year":
                return (DateUtil.firstDayInYear(todayInt), DateUtil.lastDayInYear(todayInt))
            elif selectedOption ==  "this_fiscal_year":
                return (DateUtil.firstDayInFiscalYear(todayInt), DateUtil.lastDayInFiscalYear(todayInt))
            elif selectedOption ==  "fiscal_year_to_date":
                return (DateUtil.firstDayInFiscalYear(todayInt), todayInt)
            elif selectedOption ==  "last_fiscal_year":
                return (DateUtil.decrementYear(DateUtil.firstDayInFiscalYear(todayInt)),
                        DateUtil.decrementYear(DateUtil.lastDayInFiscalYear(todayInt)))
            elif selectedOption ==  "last_fiscal_quarter":
                baseDate = DateUtil.incrementDate(todayInt, 0, -3, 0)
                return (DateUtil.firstDayInFiscalQuarter(baseDate), DateUtil.lastDayInFiscalQuarter(baseDate))
            elif selectedOption ==  "this_quarter":
                return (Util.firstDayInQuarter(todayInt), Util.lastDayInQuarter(todayInt))
            elif selectedOption ==  "this_month":
                return (Util.firstDayInMonth(todayInt), Util.lastDayInMonth(todayInt))
            elif selectedOption ==  "this_week":
                return (Util.firstDayInWeek(todayInt), Util.lastDayInWeek(todayInt))
            elif selectedOption ==  "last_year":
                return (Util.firstDayInYear(Util.decrementYear(todayInt)),
                        Util.lastDayInYear(Util.decrementYear(todayInt)))
            elif selectedOption ==  "last_quarter":
                baseDate = DateUtil.incrementDate(todayInt, 0, -3, 0)
                return (DateUtil.firstDayInQuarter(baseDate), DateUtil.lastDayInQuarter(baseDate))
            elif selectedOption ==  "last_month":
                i = Util.firstDayInMonth(todayInt)
                return (Util.incrementDate(i, 0, -1, 0), Util.incrementDate(i, 0, 0, -1))
            elif selectedOption ==  "last_week":
                firstDayInWeek = Util.firstDayInWeek(todayInt)
                return (Util.incrementDate(firstDayInWeek, 0, 0, -7), Util.incrementDate(firstDayInWeek, 0, 0, -1))
            elif selectedOption ==  "last_12_months":
                firstDayInMonth = Util.firstDayInMonth(todayInt)
                return (Util.incrementDate(firstDayInMonth, 0, -12, 0), Util.incrementDate(firstDayInMonth, 0, 0, -1))
            elif selectedOption ==  "last_1_day":
                return (Util.incrementDate(todayInt, 0, 0, -1), todayInt)    # from build 5051: actually 2 days (today & yesterday)
            elif selectedOption == "last_30_days":
                return (Util.incrementDate(todayInt, 0, 0, -29), todayInt)   # from build 5051: 30 days including today
            elif selectedOption ==  "last_365_days":
                return (Util.incrementDate(todayInt, 0, 0, -364), todayInt)  # from build 5051: 30 days including today
            elif selectedOption ==  "custom_date":
                pass
            elif selectedOption ==  "all_dates":
                pass
            else:
                pass
                # raise(Exception("Error - date range incorrect"))

            return DateRange().getStartDateInt(), DateRange().getEndDateInt()


        dateDropdown = JComboBox(dateOptions)
        dateDropdown.setName("dateDropdown")
        if saveDropDownDateRange_EAR != "":
            try:
                dateDropdown.setSelectedItem(saveDropDownDateRange_EAR)
            except: pass

        labelDateDropDown = JLabel("Select Date Range:")

        labelDateStart = JLabel("Date range start:")
        user_selectDateStart = JDateField(MD_REF.getUI())   # Use MD API function (not std Python)
        user_selectDateStart.setName("user_selectDateStart")                                                            # noqa
        user_selectDateStart.setEnabled(False)                                                                          # noqa
        # user_selectDateStart.setDisabledTextColor(Color.gray)                                                         # noqa
        user_selectDateStart.setDateInt(userdateStart_EAR)

        labelDateEnd = JLabel("Date range end:")
        user_selectDateEnd = JDateField(MD_REF.getUI())   # Use MD API function (not std Python)
        user_selectDateEnd.setName("user_selectDateEnd")                                                                # noqa
        user_selectDateEnd.setEnabled(False)                                                                            # noqa
        # user_selectDateEnd.setDisabledTextColor(Color.gray)                                                           # noqa
        user_selectDateEnd.setDateInt(userdateEnd_EAR)

        if saveDropDownDateRange_EAR == "custom_date":
            user_selectDateStart.setEnabled(True)                                                                       # noqa
            user_selectDateEnd.setEnabled(True)                                                                         # noqa
        else:
            # Refresh the date range
            user_selectDateStart.setEnabled(False)                                                                      # noqa
            user_selectDateEnd.setEnabled(False)                                                                        # noqa
            _s, _e = getDateRange(saveDropDownDateRange_EAR)
            user_selectDateStart.setDateInt(_s)
            user_selectDateEnd.setDateInt(_e)

        labelTags = JLabel("Filter for Tags (separate with commas) or ALL:")
        user_selectTags = JTextField(12)
        user_selectTags.setName("user_selectTags")
        user_selectTags.setDocument(JTextFieldLimitYN(30, True, "CURR"))
        if lAllTags_EAR: user_selectTags.setText("ALL")
        else:            user_selectTags.setText(tagFilter_EAR)

        labelText = JLabel("Filter for Text in Description or Memo fields or ALL:")
        user_selectText = JTextField(12)
        user_selectText.setName("user_selectText")
        user_selectText.setDocument(JTextFieldLimitYN(30, True, "CURR"))
        if lAllText_EAR: user_selectText.setText("ALL")
        else:            user_selectText.setText(textFilter_EAR)

        labelCategories = JLabel("Filter for Text in Category or ALL:")
        user_selectCategories = JTextField(12)
        user_selectCategories.setName("user_selectCategories")
        user_selectCategories.setDocument(JTextFieldLimitYN(30, True, "CURR"))
        if lAllCategories_EAR: user_selectCategories.setText("ALL")
        else:            user_selectCategories.setText(categoriesFilter_EAR)

        labelAttachments = JLabel("Extract & Download Attachments?")
        user_selectExtractAttachments = JCheckBox("", lExtractAttachments_EAR)
        user_selectExtractAttachments.setName("user_selectExtractAttachments")

        dateStrings=["dd/mm/yyyy", "mm/dd/yyyy", "yyyy/mm/dd", "yyyymmdd"]
        labelDateFormat = JLabel("Select Output Date Format (default yyyy/mm/dd):")
        user_dateformat = JComboBox(dateStrings)
        user_dateformat.setName("user_dateformat")

        if userdateformat == "%d/%m/%Y": user_dateformat.setSelectedItem("dd/mm/yyyy")
        elif userdateformat == "%m/%d/%Y": user_dateformat.setSelectedItem("mm/dd/yyyy")
        elif userdateformat == "%Y%m%d": user_dateformat.setSelectedItem("yyyymmdd")
        else: user_dateformat.setSelectedItem("yyyy/mm/dd")

        labelStripASCII = JLabel("Strip non ASCII characters from CSV extract?")
        user_selectStripASCII = JCheckBox("", lStripASCII)
        user_selectStripASCII.setName("user_selectStripASCII")

        labelDelimiter = JLabel("Change CSV extract Delimiter from default to: '|,'")
        user_selectDELIMITER = JComboBox(GlobalVars.ALLOWED_CSV_FILE_DELIMITER_STRINGS)
        user_selectDELIMITER.setName("user_selectDELIMITER")
        user_selectDELIMITER.setSelectedItem(csvDelimiter)

        labelBOM = JLabel("Write BOM (Byte Order Mark) to file (helps Excel open files)?")
        user_selectBOM = JCheckBox("", lWriteBOMToExportFile_SWSS)
        user_selectBOM.setName("user_selectBOM")

        labelExportParameters = JLabel("Write parameters out to file (added as rows at EOF)?")
        user_ExportParameters = JCheckBox("", lWriteParametersToExportFile_SWSS)
        user_ExportParameters.setName("user_ExportParameters")

        labelAutoExtract = JLabel("Enable Auto Extract?")
        user_AutoExtract = JCheckBox("", autoExtract_EAR)
        user_AutoExtract.setName("user_AutoExtract")

        labelDEBUG = JLabel("Turn DEBUG Verbose messages on?")
        user_selectDEBUG = JCheckBox("", debug)
        user_selectDEBUG.setName("user_selectDEBUG")

        labelSTATUSbar = JLabel("")
        labelSTATUSbar.setName("labelSTATUSbar")

        _userFilters.add(labelSelectOneAccount)
        _userFilters.add(accountDropdown)
        _userFilters.add(labelIncludeSubAccounts)
        _userFilters.add(user_includeSubAccounts)
        _userFilters.add(labelSeparator1)
        _userFilters.add(labelSeparator2)
        _userFilters.add(labelHideInactiveAccounts)
        _userFilters.add(user_hideInactiveAccounts)
        _userFilters.add(labelHideHiddenAccounts)
        _userFilters.add(user_hideHiddenAccounts)
        _userFilters.add(labelFilterAccounts)
        _userFilters.add(user_selectAccounts)
        _userFilters.add(labelFilterCurrency)
        _userFilters.add(user_selectCurrency)
        _userFilters.add(labelSeparator5)
        _userFilters.add(labelSeparator6)

        _userFilters.add(labelDateDropDown)
        _userFilters.add(dateDropdown)

        _userFilters.add(labelDateStart)
        _userFilters.add(user_selectDateStart)
        _userFilters.add(labelDateEnd)
        _userFilters.add(user_selectDateEnd)
        _userFilters.add(labelTags)
        _userFilters.add(user_selectTags)
        _userFilters.add(labelText)
        _userFilters.add(user_selectText)
        _userFilters.add(labelCategories)
        _userFilters.add(user_selectCategories)
        _userFilters.add(labelSeparator7)
        _userFilters.add(labelSeparator8)
        _userFilters.add(labelOpeningBalances)
        _userFilters.add(user_selectOpeningBalances)
        _userFilters.add(labelBalancesAdjustments)
        _userFilters.add(user_selectBalanceAdjustments)
        # _userFilters.add(labelIncludeTransfers)
        # _userFilters.add(user_selectIncludeTransfers)
        _userFilters.add(labelAttachments)
        _userFilters.add(user_selectExtractAttachments)
        _userFilters.add(labelDateFormat)
        _userFilters.add(user_dateformat)
        _userFilters.add(labelStripASCII)
        _userFilters.add(user_selectStripASCII)
        _userFilters.add(labelDelimiter)
        _userFilters.add(user_selectDELIMITER)
        _userFilters.add(labelBOM)
        _userFilters.add(user_selectBOM)
        _userFilters.add(labelExportParameters)
        _userFilters.add(user_ExportParameters)
        _userFilters.add(labelAutoExtract)
        _userFilters.add(user_AutoExtract)
        _userFilters.add(labelDEBUG)
        _userFilters.add(user_selectDEBUG)

        _userFilters.add(labelSTATUSbar)

        components = _userFilters.getComponents()
        for theComponent in components:
            if isinstance(theComponent, (JComboBox,JTextField)):
                theComponent.addActionListener(PanelAction(_userFilters))


        options = ["ABORT", "CSV Extract"]

        while True:
            rowHeight = 24
            rows = 26
            jsp = MyJScrollPaneForJOptionPane(_userFilters, None, 1200, rows * rowHeight)
            userAction = (JOptionPane.showOptionDialog(extract_data_frame_,
                                                       jsp, "EXTRACT ACCOUNT REGISTERS: Set Script Parameters....",
                                                       JOptionPane.OK_CANCEL_OPTION,
                                                       JOptionPane.QUESTION_MESSAGE,
                                                       getMDIcon(lAlwaysGetIcon=True),
                                                       options, options[1]))
            if userAction != 1:
                myPrint("B", "User Cancelled Parameter selection.. Will abort..")
                GlobalVars.DISPLAY_DATA = False
                GlobalVars.EXTRACT_DATA = False
                _exit = True
                break

            if not (user_selectDateStart.getDateInt() <= user_selectDateEnd.getDateInt()
                    and user_selectDateEnd.getDateInt() >= user_selectDateStart.getDateInt()):
                user_selectDateStart.setForeground(getColorRed())                                                       # noqa
                user_selectDateEnd.setForeground(getColorRed())                                                         # noqa
                labelSTATUSbar.setText(">> Error - date range incorrect, please try again... <<".upper())
                labelSTATUSbar.setForeground(getColorRed())
                continue

            if user_selectTags.getText() != "ALL" and (user_selectOpeningBalances.isSelected() or user_selectBalanceAdjustments.isSelected()):
                user_selectTags.setForeground(getColorRed())
                user_selectOpeningBalances.setForeground(getColorRed())
                user_selectBalanceAdjustments.setForeground(getColorRed())
                labelSTATUSbar.setText(">> Error: CANNOT filter on Tags & Balances <<".upper())
                labelSTATUSbar.setForeground(getColorRed())
                continue

            if user_selectText.getText() != "ALL" and (user_selectOpeningBalances.isSelected() or user_selectBalanceAdjustments.isSelected()):
                user_selectText.setForeground(getColorRed())
                user_selectOpeningBalances.setForeground(getColorRed())
                user_selectBalanceAdjustments.setForeground(getColorRed())
                labelSTATUSbar.setText(">> Error: CANNOT filter on Text & Balances <<".upper())
                labelSTATUSbar.setForeground(getColorRed())
                continue

            if user_selectCategories.getText() != "ALL" and (user_selectOpeningBalances.isSelected() or user_selectBalanceAdjustments.isSelected()):
                user_selectCategories.setForeground(getColorRed())
                user_selectOpeningBalances.setForeground(getColorRed())
                user_selectBalanceAdjustments.setForeground(getColorRed())
                labelSTATUSbar.setText(">> Error: CANNOT filter on Categories & Balances <<".upper())
                labelSTATUSbar.setForeground(getColorRed())
                continue

            user_selectDateStart.setForeground(saveColor)                                                               # noqa
            user_selectDateEnd.setForeground(saveColor)                                                                 # noqa
            labelSTATUSbar.setText("")

            if isinstance(accountDropdown.getSelectedItem(),(str,unicode)) and accountDropdown.getSelectedItem() == textToUse:
                # So <NONE> Selected in Account dropdown....
                if user_includeSubAccounts.isSelected():
                    user_includeSubAccounts.setSelected(False)
                    labelSTATUSbar.setText(">> Error: Dropdown Accounts <NONE> & Include Sub Accts <<".upper())
                    labelSTATUSbar.setForeground(getColorRed())
                    user_includeSubAccounts.setForeground(getColorRed())
                    accountDropdown.setForeground(getColorRed())
                    continue
            elif isinstance(accountDropdown.getSelectedItem(),(StoreAccount)):

                if (user_selectAccounts.getText() != "ALL" or user_selectCurrency.getText() != "ALL"
                        or (not user_hideInactiveAccounts.isSelected()) or (not user_hideHiddenAccounts.isSelected())):
                    user_selectAccounts.setText("ALL")
                    user_selectCurrency.setText("ALL")
                    user_hideInactiveAccounts.setSelected(True)
                    user_hideHiddenAccounts.setSelected(True)
                    labelSTATUSbar.setText(">> Error - Dropdown Accounts Selected. FILTERS RESET TO DEFAULTS <<".upper())
                    labelSTATUSbar.setForeground(getColorRed())
                    user_selectAccounts.setForeground(getColorRed())
                    user_selectCurrency.setForeground(getColorRed())
                    user_hideHiddenAccounts.setForeground(getColorRed())
                    user_hideInactiveAccounts.setForeground(getColorRed())
                    continue
            else:
                txt = "@@@ LOGIC ERROR IN PARAMETER DROPDOWN - ABORTING"
                myPrint("B", txt)
                raise Exception(txt)

            accountDropdown.setForeground(saveColor)
            user_includeSubAccounts.setForeground(saveColor)
            user_selectAccounts.setForeground(saveColor)
            user_selectCurrency.setForeground(saveColor)
            user_hideHiddenAccounts.setForeground(saveColor)
            user_hideInactiveAccounts.setForeground(saveColor)

            break   # Loop

        if not _exit:

            GlobalVars.DISPLAY_DATA = False
            GlobalVars.EXTRACT_DATA = True

            hideInactiveAccounts = user_hideInactiveAccounts.isSelected()
            hideHiddenAccounts = user_hideHiddenAccounts.isSelected()
            lIncludeSubAccounts_EAR = user_includeSubAccounts.isSelected()
            lIncludeOpeningBalances_EAR = user_selectOpeningBalances.isSelected()
            lIncludeBalanceAdjustments_EAR = user_selectBalanceAdjustments.isSelected()
            lIncludeInternalTransfers_EAR = user_selectIncludeTransfers.isSelected()
            lExtractAttachments_EAR = user_selectExtractAttachments.isSelected()
            lWriteBOMToExportFile_SWSS = user_selectBOM.isSelected()
            lWriteParametersToExportFile_SWSS = user_ExportParameters.isSelected()
            autoExtract_EAR = user_AutoExtract.isSelected()

            lStripASCII = user_selectStripASCII.isSelected()
            debug = user_selectDEBUG.isSelected()

            if user_selectTags.getText() == "ALL" or user_selectTags.getText().strip() == "":
                lAllTags_EAR = True
                tagFilter_EAR = "ALL"
            else:
                lAllTags_EAR = False
                tagFilter_EAR = user_selectTags.getText()

            if user_selectText.getText() == "ALL" or user_selectText.getText().strip() == "":
                lAllText_EAR = True
                textFilter_EAR = "ALL"
            else:
                lAllText_EAR = False
                textFilter_EAR = user_selectText.getText()

            if user_selectCategories.getText() == "ALL" or user_selectCategories.getText().strip() == "":
                lAllCategories_EAR = True
                categoriesFilter_EAR = "ALL"
            else:
                lAllCategories_EAR = False
                categoriesFilter_EAR = user_selectCategories.getText()

            userdateStart_EAR = user_selectDateStart.getDateInt()
            userdateEnd_EAR = user_selectDateEnd.getDateInt()

            if user_dateformat.getSelectedItem() == "dd/mm/yyyy": userdateformat = "%d/%m/%Y"
            elif user_dateformat.getSelectedItem() == "mm/dd/yyyy": userdateformat = "%m/%d/%Y"
            elif user_dateformat.getSelectedItem() == "yyyy/mm/dd": userdateformat = "%Y/%m/%d"
            elif user_dateformat.getSelectedItem() == "yyyymmdd": userdateformat = "%Y%m%d"
            else:
                # PROBLEM /  default
                userdateformat = "%Y/%m/%d"

            csvDelimiter = validateCSVFileDelimiter(user_selectDELIMITER.getSelectedItem())

            saveDropDownDateRange_EAR = dateDropdown.getSelectedItem()

            if isinstance(accountDropdown.getSelectedItem(), StoreAccount):
                GlobalVars.dropDownAccount_EAR = accountDropdown.getSelectedItem().getAccount()                                    # noqa
                # noinspection PyUnresolvedReferences
                saveDropDownAccountUUID_EAR = GlobalVars.dropDownAccount_EAR.getUUID()
                lIncludeSubAccounts_EAR = user_includeSubAccounts.isSelected()
                lAllAccounts = True
                lAllCurrency = True
                filterForAccounts = "ALL"
                filterForCurrency = "ALL"
                hideInactiveAccounts = True
                hideHiddenAccounts = True
            else:
                GlobalVars.dropDownAccount_EAR = None
                saveDropDownAccountUUID_EAR = None
                lIncludeSubAccounts_EAR = False
                if user_selectAccounts.getText() == "ALL" or user_selectAccounts.getText().strip() == "":
                    lAllAccounts = True
                    filterForAccounts = "ALL"
                else:
                    lAllAccounts = False
                    filterForAccounts = user_selectAccounts.getText()

                if user_selectCurrency.getText() == "ALL" or user_selectCurrency.getText().strip() == "":
                    lAllCurrency = True
                    filterForCurrency = "ALL"
                else:
                    lAllCurrency = False
                    filterForCurrency = user_selectCurrency.getText()


            myPrint("DB", "DEBUG still turned ON (from Parameters)")

            listExtractAccountTxnsParameters()

        return _exit

    def listExtractInvestmentAccountParameters():
        myPrint("B","---------------------------------------------------------------------------------------")
        myPrint("B","Parameters: Extract Investment Transactions:")
        myPrint("B", "  Hide Hidden Securities...............:", hideHiddenSecurities)
        myPrint("B", "  Hide Inactive Accounts...............:", hideInactiveAccounts)
        myPrint("B", "  Hide Hidden Accounts.................:", hideHiddenAccounts)
        myPrint("B", "  Currency filter......................: %s '%s'" %(lAllCurrency, filterForCurrency))
        myPrint("B", "  Security filter......................: %s '%s'" %(lAllSecurity, filterForSecurity))
        myPrint("B", "  Account filter.......................: %s '%s'" %(lAllAccounts, filterForAccounts))

        if lFilterDateRange_EIT and filterDateStart_EIT != 0 and filterDateEnd_EIT != 0:
            myPrint("B", "  Filtering Transactions by date range.: (Start: %s End: %s)"
                    %(convertStrippedIntDateFormattedText(filterDateStart_EIT), convertStrippedIntDateFormattedText(filterDateEnd_EIT)))
        else:
            myPrint("B", "  Selecting all dates (no date filter).:", True)

        myPrint("B", "  Include Unadjusted Opening Balances..:", lIncludeOpeningBalances)
        myPrint("B", "  Including Balance Adjustments........:", lIncludeBalanceAdjustments)
        myPrint("B", "  Adjust for Stock Splits..............:", lAdjustForSplits)
        myPrint("B", "  OMIT Buy/Sell LOT matching data......:", lOmitLOTDataFromExtract_EIT)
        myPrint("B", "  Extract extra security account info..:", lExtractExtraSecurityAcctInfo )
        myPrint("B", "  Download Attachments.................: %s" %(lExtractAttachments_EIT))
        myPrint("B", "  Auto Extract.........................:", autoExtract_EIT)
        myPrint("B", "  User date format.....................:", userdateformat)
        myPrint("B","---------------------------------------------------------------------------------------")

    def setupExtractInvestmentAccountParameters():
        # ####################################################
        # EXTRACT_INVESTMENT_TRANSACTIONS_CSV PARAMETER SCREEN
        # ####################################################

        global debug
        global lWriteParametersToExportFile_SWSS

        global lDidIUseAttachmentDir
        global dataKeys, attachmentDir, relativePath

        global __extract_data, extract_filename
        global lStripASCII, csvDelimiter, userdateformat, lWriteBOMToExportFile_SWSS
        global hideInactiveAccounts, hideHiddenAccounts, hideHiddenSecurities
        global lAllSecurity, filterForSecurity, lAllAccounts, filterForAccounts, lAllCurrency, filterForCurrency
        global lFilterDateRange_EIT, filterDateStart_EIT, filterDateEnd_EIT
        global whichDefaultExtractToRun_SWSS
        global lIncludeOpeningBalances, lIncludeBalanceAdjustments, lAdjustForSplits, lExtractAttachments_EIT
        global lOmitLOTDataFromExtract_EIT, lExtractExtraSecurityAcctInfo

        global autoExtract_EIT


        label1 = JLabel("Hide Hidden Securities?")
        user_hideHiddenSecurities = JCheckBox("", hideHiddenSecurities)

        label2 = JLabel("Hide Inactive Accounts?")
        user_hideInactiveAccounts = JCheckBox("", hideInactiveAccounts)

        label3 = JLabel("Hide Hidden Accounts?")
        user_hideHiddenAccounts = JCheckBox("", hideHiddenAccounts)

        label4 = JLabel("Filter for Currency containing text '...' or ALL:")
        user_selectCurrency = JTextField(5)
        user_selectCurrency.setDocument(JTextFieldLimitYN(5, True, "CURR"))
        if lAllCurrency: user_selectCurrency.setText("ALL")
        else:            user_selectCurrency.setText(filterForCurrency)

        label5 = JLabel("Filter for Security/Ticker containing text '...' or ALL:")
        user_selectTicker = JTextField(12)
        user_selectTicker.setDocument(JTextFieldLimitYN(12, True, "CURR"))
        if lAllSecurity: user_selectTicker.setText("ALL")
        else:            user_selectTicker.setText(filterForSecurity)

        label6 = JLabel("Filter for Accounts containing text '...' (or ALL):")
        user_selectAccounts = JTextField(12)
        user_selectAccounts.setDocument(JTextFieldLimitYN(20, True, "CURR"))
        if lAllAccounts: user_selectAccounts.setText("ALL")
        else:            user_selectAccounts.setText(filterForAccounts)

        user_dateRangeChooser = DateRangeChooser(MD_REF.getUI())

        label_dateRange = JLabel("Filter transactions by date range:")
        user_filterDateRange = JCheckBox("", lFilterDateRange_EIT)

        label_dateStart = user_dateRangeChooser.getStartLabel()
        if lFilterDateRange_EIT and filterDateStart_EIT != 0: user_dateRangeChooser.setStartDate(filterDateStart_EIT)
        user_dateStart = user_dateRangeChooser.getStartField()
        if lFilterDateRange_EIT and filterDateEnd_EIT != 0: user_dateRangeChooser.setEndDate(filterDateEnd_EIT)
        label_dateEnd = user_dateRangeChooser.getEndLabel()
        user_dateEnd = user_dateRangeChooser.getEndField()

        label7 = JLabel("Include Unadjusted Opening Balances?")
        user_selectOpeningBalances = JCheckBox("", lIncludeOpeningBalances)

        label7b = JLabel("Include Balance Adjustments?")
        user_selectBalanceAdjustments = JCheckBox("", lIncludeBalanceAdjustments)

        label8 = JLabel("Adjust for stock splits/")
        user_selectAdjustSplits = JCheckBox("", lAdjustForSplits)

        dateStrings=["dd/mm/yyyy", "mm/dd/yyyy", "yyyy/mm/dd", "yyyymmdd"]
        label9 = JLabel("Select Output Date Format (default yyyy/mm/dd):")
        user_dateformat = JComboBox(dateStrings)

        if userdateformat == "%d/%m/%Y": user_dateformat.setSelectedItem("dd/mm/yyyy")
        elif userdateformat == "%m/%d/%Y": user_dateformat.setSelectedItem("mm/dd/yyyy")
        elif userdateformat == "%Y%m%d": user_dateformat.setSelectedItem("yyyymmdd")
        else: user_dateformat.setSelectedItem("yyyy/mm/dd")

        labelOmitLOTDataFromExtract_EIT = JLabel("Omit Buy/Sell LOT Matching Data from extract file")
        user_lOmitLOTDataFromExtract_EIT = JCheckBox("", lOmitLOTDataFromExtract_EIT)
        user_lOmitLOTDataFromExtract_EIT.setName("user_lOmitLOTDataFromExtract_EIT")

        labelExtractExtraSecurityAcctInfo = JLabel("Extract extra security account info")
        user_lExtractExtraSecurityAcctInfo = JCheckBox("", lExtractExtraSecurityAcctInfo)
        user_lExtractExtraSecurityAcctInfo.setName("user_lExtractExtraSecurityAcctInfo")

        labelAttachments = JLabel("Extract & Download Attachments?")
        user_selectExtractAttachments = JCheckBox("", lExtractAttachments_EIT)
        user_selectExtractAttachments.setName("user_selectExtractAttachments")

        label10 = JLabel("Strip non ASCII characters from CSV extract?")
        user_selectStripASCII = JCheckBox("", lStripASCII)

        label11 = JLabel("Change CSV extract Delimiter from default:")
        user_selectDELIMITER = JComboBox(GlobalVars.ALLOWED_CSV_FILE_DELIMITER_STRINGS)
        user_selectDELIMITER.setSelectedItem(csvDelimiter)

        labelBOM = JLabel("Write BOM (Byte Order Mark) (helps Excel open files)?")
        user_selectBOM = JCheckBox("", lWriteBOMToExportFile_SWSS)

        labelExportParameters = JLabel("Write parameters out to file (added as rows at EOF)?")
        user_ExportParameters = JCheckBox("", lWriteParametersToExportFile_SWSS)

        labelAutoExtract = JLabel("Enable Auto Extract?")
        user_AutoExtract = JCheckBox("", autoExtract_EIT)

        label12 = JLabel("Turn DEBUG Verbose messages on?")
        user_selectDEBUG = JCheckBox("", debug)

        userFilters = JPanel(GridLayout(0, 2))
        userFilters.add(label1)
        userFilters.add(user_hideHiddenSecurities)
        userFilters.add(label2)
        userFilters.add(user_hideInactiveAccounts)
        userFilters.add(label3)
        userFilters.add(user_hideHiddenAccounts)
        userFilters.add(label4)
        userFilters.add(user_selectCurrency)
        userFilters.add(label5)
        userFilters.add(user_selectTicker)
        userFilters.add(label6)
        userFilters.add(user_selectAccounts)

        # Date Range options
        userFilters.add(JLabel("-"*30)); userFilters.add(JLabel("-"*30))
        userFilters.add(label_dateRange)
        userFilters.add(user_filterDateRange)
        userFilters.add(user_dateRangeChooser.getChoiceLabel())
        userFilters.add(user_dateRangeChooser.getChoice())
        userFilters.add(label_dateStart)
        userFilters.add(user_dateStart)
        userFilters.add(label_dateEnd)
        userFilters.add(user_dateEnd)
        userFilters.add(JLabel("-"*30)); userFilters.add(JLabel("-"*30))

        userFilters.add(label7)
        userFilters.add(user_selectOpeningBalances)
        userFilters.add(label7b)
        userFilters.add(user_selectBalanceAdjustments)
        userFilters.add(label8)
        userFilters.add(user_selectAdjustSplits)
        userFilters.add(labelOmitLOTDataFromExtract_EIT)
        userFilters.add(user_lOmitLOTDataFromExtract_EIT)
        userFilters.add(labelExtractExtraSecurityAcctInfo)
        userFilters.add(user_lExtractExtraSecurityAcctInfo)
        userFilters.add(labelAttachments)
        userFilters.add(user_selectExtractAttachments)
        userFilters.add(label9)
        userFilters.add(user_dateformat)
        userFilters.add(label10)
        userFilters.add(user_selectStripASCII)
        userFilters.add(label11)
        userFilters.add(user_selectDELIMITER)
        userFilters.add(labelBOM)
        userFilters.add(user_selectBOM)
        userFilters.add(labelExportParameters)
        userFilters.add(user_ExportParameters)
        userFilters.add(labelAutoExtract)
        userFilters.add(user_AutoExtract)
        userFilters.add(label12)
        userFilters.add(user_selectDEBUG)

        _exit = False

        options = ["ABORT", "CSV Extract"]
        rowHeight = 24
        rows = 26
        jsp = MyJScrollPaneForJOptionPane(userFilters, None, 1200, rows * rowHeight)
        userAction = (JOptionPane.showOptionDialog(extract_data_frame_, jsp, "EXTRACT INVESTMENT TRANSACTIONS: Set Script Parameters....",
                                                   JOptionPane.OK_CANCEL_OPTION,
                                                   JOptionPane.QUESTION_MESSAGE,
                                                   getMDIcon(lAlwaysGetIcon=True),
                                                   options, options[1]))
        if userAction == 1:
            myPrint("DB", "Extract chosen")
            GlobalVars.DISPLAY_DATA = False
            GlobalVars.EXTRACT_DATA = True
        else:
            myPrint("B", "User Cancelled Parameter selection.. Will abort..")
            _exit = True
            GlobalVars.DISPLAY_DATA = False
            GlobalVars.EXTRACT_DATA = False

        if not _exit:

            hideHiddenSecurities = user_hideHiddenSecurities.isSelected()
            hideInactiveAccounts = user_hideInactiveAccounts.isSelected()
            hideHiddenAccounts = user_hideHiddenAccounts.isSelected()

            if user_selectCurrency.getText() == "ALL" or user_selectCurrency.getText().strip() == "":
                lAllCurrency = True
                filterForCurrency = "ALL"
            else:
                lAllCurrency = False
                filterForCurrency = user_selectCurrency.getText()

            if user_selectTicker.getText() == "ALL" or user_selectTicker.getText().strip() == "":
                lAllSecurity = True
                filterForSecurity = "ALL"
            else:
                lAllSecurity = False
                filterForSecurity = user_selectTicker.getText()

            if user_selectAccounts.getText() == "ALL" or user_selectAccounts.getText().strip() == "":
                lAllAccounts = True
                filterForAccounts = "ALL"
            else:
                lAllAccounts = False
                filterForAccounts = user_selectAccounts.getText()

            lFilterDateRange_EIT = user_filterDateRange.isSelected()
            if lFilterDateRange_EIT:
                filterDateStart_EIT = user_dateRangeChooser.getDateRange().getStartDateInt()
                filterDateEnd_EIT = user_dateRangeChooser.getDateRange().getEndDateInt()
                if user_dateRangeChooser.getAllDatesSelected():
                    filterDateEnd_EIT = DateRange().getEndDateInt()  # Fix for DRC ALL_DATES Only returning +1 year! (upto builds 5046)
                    myPrint("DB", "@@ All Dates detected; overriding filterDateEnd_EIT to: %s" %(filterDateEnd_EIT))
            else:
                filterDateStart_EIT = 0
                filterDateEnd_EIT = 0

            lIncludeOpeningBalances = user_selectOpeningBalances.isSelected()
            lIncludeBalanceAdjustments = user_selectBalanceAdjustments.isSelected()
            lAdjustForSplits = user_selectAdjustSplits.isSelected()
            lOmitLOTDataFromExtract_EIT = user_lOmitLOTDataFromExtract_EIT.isSelected()
            lExtractExtraSecurityAcctInfo = user_lExtractExtraSecurityAcctInfo.isSelected()
            lExtractAttachments_EIT = user_selectExtractAttachments.isSelected()

            if user_dateformat.getSelectedItem() == "dd/mm/yyyy": userdateformat = "%d/%m/%Y"
            elif user_dateformat.getSelectedItem() == "mm/dd/yyyy": userdateformat = "%m/%d/%Y"
            elif user_dateformat.getSelectedItem() == "yyyy/mm/dd": userdateformat = "%Y/%m/%d"
            elif user_dateformat.getSelectedItem() == "yyyymmdd": userdateformat = "%Y%m%d"
            else:
                # PROBLEM /  default
                userdateformat = "%Y/%m/%d"

            lStripASCII = user_selectStripASCII.isSelected()

            csvDelimiter = validateCSVFileDelimiter(user_selectDELIMITER.getSelectedItem())

            lWriteBOMToExportFile_SWSS = user_selectBOM.isSelected()
            lWriteParametersToExportFile_SWSS = user_ExportParameters.isSelected()
            autoExtract_EIT = user_AutoExtract.isSelected()

            debug = user_selectDEBUG.isSelected()

            listExtractInvestmentAccountParameters()

        return _exit

    def listExtractCurrencyHistoryParameters():
        myPrint("B","---------------------------------------------------------------------------------------")
        myPrint("B","Parameters: Extract Currency History:")
        myPrint("B", "  user date format.....................:", userdateformat)
        myPrint("B", "  Selected start date..................:", userdateStart_ECH)
        myPrint("B", "  Selected end date....................:", userdateEnd_ECH)
        myPrint("B", "  Detailed extract.....................:", (not lSimplify_ECH), "(Simplified: %s)" %(lSimplify_ECH))
        myPrint("B", "  Hide hidden currencies...............:", hideHiddenCurrencies_ECH)
        myPrint("B", "  Auto Extract.........................:", autoExtract_ECH)
        myPrint("B","---------------------------------------------------------------------------------------")

    def setupExtractCurrencyHistoryParameters():
        # ####################################################
        # EXTRACT_CURRENCY_HISTORY_CSV PARAMETER SCREEN
        # ####################################################

        global debug
        global lWriteParametersToExportFile_SWSS

        global lDidIUseAttachmentDir

        global __extract_data, extract_filename
        global lStripASCII, csvDelimiter, userdateformat, lWriteBOMToExportFile_SWSS
        global hideInactiveAccounts, hideHiddenAccounts, hideHiddenSecurities
        global lAllSecurity, filterForSecurity, lAllAccounts, filterForAccounts, lAllCurrency, filterForCurrency
        global whichDefaultExtractToRun_SWSS
        global lSimplify_ECH, userdateStart_ECH, userdateEnd_ECH, hideHiddenCurrencies_ECH

        global autoExtract_ECH

        dateStrings = ["dd/mm/yyyy", "mm/dd/yyyy", "yyyy/mm/dd", "yyyymmdd"]
        # 1=dd/mm/yyyy, 2=mm/dd/yyyy, 3=yyyy/mm/dd, 4=yyyymmdd
        label1 = JLabel("Select Output Date Format (default yyyy/mm/dd):")
        user_dateformat = JComboBox(dateStrings)

        if userdateformat == "%d/%m/%Y": user_dateformat.setSelectedItem("dd/mm/yyyy")
        elif userdateformat == "%m/%d/%Y": user_dateformat.setSelectedItem("mm/dd/yyyy")
        elif userdateformat == "%Y%m%d": user_dateformat.setSelectedItem("yyyymmdd")
        else: user_dateformat.setSelectedItem("yyyy/mm/dd")

        labelDateStart = JLabel("Date range start:")
        user_selectDateStart = JDateField(MD_REF.getUI())   # Use MD API function (not std Python)
        user_selectDateStart.setDateInt(userdateStart_ECH)

        labelDateEnd = JLabel("Date range end:")
        user_selectDateEnd = JDateField(MD_REF.getUI())   # Use MD API function (not std Python)
        user_selectDateEnd.setDateInt(userdateEnd_ECH)
        # user_selectDateEnd.gotoToday()

        labelSimplify = JLabel("Simplify extract?")
        user_selectSimplify = JCheckBox("", lSimplify_ECH)

        labelHideHiddenCurrencies = JLabel("Hide Hidden Currencies?")
        user_selectHideHiddenCurrencies = JCheckBox("", hideHiddenCurrencies_ECH)

        label2 = JLabel("Strip non ASCII characters from CSV extract?")
        user_selectStripASCII = JCheckBox("", lStripASCII)

        label3 = JLabel("Change CSV extract Delimiter from default:")
        user_selectDELIMITER = JComboBox(GlobalVars.ALLOWED_CSV_FILE_DELIMITER_STRINGS)
        user_selectDELIMITER.setSelectedItem(csvDelimiter)

        labelBOM = JLabel("Write BOM (Byte Order Mark) to file (helps Excel open files)?")
        user_selectBOM = JCheckBox("", lWriteBOMToExportFile_SWSS)

        labelExportParameters = JLabel("Write parameters out to file (added as rows at EOF)?")
        user_ExportParameters = JCheckBox("", lWriteParametersToExportFile_SWSS)

        labelAutoExtract = JLabel("Enable Auto Extract?")
        user_AutoExtract = JCheckBox("", autoExtract_ECH)

        label4 = JLabel("Turn DEBUG Verbose messages on?")
        user_selectDEBUG = JCheckBox("", debug)

        userFilters = JPanel(GridLayout(0, 2))
        userFilters.add(label1)
        userFilters.add(user_dateformat)

        userFilters.add(labelDateStart)
        userFilters.add(user_selectDateStart)

        userFilters.add(labelDateEnd)
        userFilters.add(user_selectDateEnd)

        userFilters.add(labelSimplify)
        userFilters.add(user_selectSimplify)

        userFilters.add(labelHideHiddenCurrencies)
        userFilters.add(user_selectHideHiddenCurrencies)

        userFilters.add(label2)
        userFilters.add(user_selectStripASCII)
        userFilters.add(label3)
        userFilters.add(user_selectDELIMITER)
        userFilters.add(labelBOM)
        userFilters.add(user_selectBOM)
        userFilters.add(labelExportParameters)
        userFilters.add(user_ExportParameters)
        userFilters.add(labelAutoExtract)
        userFilters.add(user_AutoExtract)
        userFilters.add(label4)
        userFilters.add(user_selectDEBUG)

        _exit = False
        options = ["Abort", "CSV Extract"]

        while True:
            rowHeight = 24
            rows = 12
            jsp = MyJScrollPaneForJOptionPane(userFilters, None, 900, rows * rowHeight)
            userAction = (JOptionPane.showOptionDialog(extract_data_frame_, jsp, "EXTRACT CURRENCY HISTORY: Set Script Parameters....",
                                                       JOptionPane.OK_CANCEL_OPTION,
                                                       JOptionPane.QUESTION_MESSAGE,
                                                       getMDIcon(lAlwaysGetIcon=True),
                                                       options, options[1]))
            if userAction != 1:
                myPrint("B", "User Cancelled Parameter selection.. Will abort..")
                _exit = True
                GlobalVars.DISPLAY_DATA = False
                GlobalVars.EXTRACT_DATA = False
                break

            if user_selectDateStart.getDateInt() <= user_selectDateEnd.getDateInt() \
                    and user_selectDateEnd.getDateInt() >= user_selectDateStart.getDateInt():
                break

            user_selectDateStart.setForeground(getColorRed())                                                           # noqa
            user_selectDateEnd.setForeground(getColorRed())                                                             # noqa
            continue

        if not _exit:
            GlobalVars.DISPLAY_DATA = False
            GlobalVars.EXTRACT_DATA = True

            if user_dateformat.getSelectedItem() == "dd/mm/yyyy": userdateformat = "%d/%m/%Y"
            elif user_dateformat.getSelectedItem() == "mm/dd/yyyy": userdateformat = "%m/%d/%Y"
            elif user_dateformat.getSelectedItem() == "yyyy/mm/dd": userdateformat = "%Y/%m/%d"
            elif user_dateformat.getSelectedItem() == "yyyymmdd": userdateformat = "%Y%m%d"
            else:
                # PROBLEM /  default
                userdateformat = "%Y/%m/%d"

            lSimplify_ECH = user_selectSimplify.isSelected()
            hideHiddenCurrencies_ECH = user_selectHideHiddenCurrencies.isSelected()
            userdateStart_ECH = user_selectDateStart.getDateInt()
            userdateEnd_ECH = user_selectDateEnd.getDateInt()

            lStripASCII = user_selectStripASCII.isSelected()

            csvDelimiter = validateCSVFileDelimiter(user_selectDELIMITER.getSelectedItem())

            lWriteBOMToExportFile_SWSS = user_selectBOM.isSelected()
            lWriteParametersToExportFile_SWSS = user_ExportParameters.isSelected()
            autoExtract_ECH = user_AutoExtract.isSelected()

            debug = user_selectDEBUG.isSelected()

            listExtractCurrencyHistoryParameters()

        return _exit

    def listExtractSecurityBalancesParameters():
        myPrint("B","---------------------------------------------------------------------------------------")
        myPrint("B","Parameters: Extract Security Balances:")

        myPrint("B", "  Hide Hidden Securities...............:", hideHiddenSecurities)
        myPrint("B", "  Hide Inactive Accounts...............:", hideInactiveAccounts)
        myPrint("B", "  Hide Hidden Accounts.................:", hideHiddenAccounts)

        myPrint("B", "  Currency filter......................: %s '%s'" %(lAllCurrency, filterForCurrency))
        myPrint("B", "  Security filter......................: %s '%s'" %(lAllSecurity, filterForSecurity))
        myPrint("B", "  Account filter.......................: %s '%s'" %(lAllAccounts, filterForAccounts))
        myPrint("B", "  Auto Extract.........................:", autoExtract_ESB)
        myPrint("B", "  User date format.....................:", userdateformat)
        myPrint("B","---------------------------------------------------------------------------------------")

    def setupExtractSecurityBalancesParameters():
        # ##############################################
        # EXTRACT_SECURITY_BALANCES_CSV PARAMETER SCREEN
        # ##############################################

        global debug
        global lWriteParametersToExportFile_SWSS

        global dataKeys

        global __extract_data, extract_filename
        global lStripASCII, csvDelimiter, userdateformat, lWriteBOMToExportFile_SWSS
        global hideInactiveAccounts, hideHiddenAccounts, hideHiddenSecurities
        global lAllSecurity, filterForSecurity, lAllAccounts, filterForAccounts, lAllCurrency, filterForCurrency
        global whichDefaultExtractToRun_SWSS

        global autoExtract_ESB

        label1 = JLabel("Hide Hidden Securities?")
        user_hideHiddenSecurities = JCheckBox("", hideHiddenSecurities)

        label2 = JLabel("Hide Inactive Accounts?")
        user_hideInactiveAccounts = JCheckBox("", hideInactiveAccounts)

        label3 = JLabel("Hide Hidden Accounts?")
        user_hideHiddenAccounts = JCheckBox("", hideHiddenAccounts)

        label4 = JLabel("Filter for Currency containing text '...' or ALL:")
        user_selectCurrency = JTextField(5)
        user_selectCurrency.setDocument(JTextFieldLimitYN(5, True, "CURR"))
        if lAllCurrency: user_selectCurrency.setText("ALL")
        else:            user_selectCurrency.setText(filterForCurrency)

        label5 = JLabel("Filter for Security/Ticker containing text '...' or ALL:")
        user_selectTicker = JTextField(12)
        user_selectTicker.setDocument(JTextFieldLimitYN(12, True, "CURR"))
        if lAllSecurity: user_selectTicker.setText("ALL")
        else:            user_selectTicker.setText(filterForSecurity)

        label6 = JLabel("Filter for Accounts containing text '...' (or ALL):")
        user_selectAccounts = JTextField(12)
        user_selectAccounts.setDocument(JTextFieldLimitYN(20, True, "CURR"))
        if lAllAccounts: user_selectAccounts.setText("ALL")
        else:            user_selectAccounts.setText(filterForAccounts)

        dateStrings=["dd/mm/yyyy", "mm/dd/yyyy", "yyyy/mm/dd", "yyyymmdd"]
        label9 = JLabel("Select Output Date Format (default yyyy/mm/dd):")
        user_dateformat = JComboBox(dateStrings)

        if userdateformat == "%d/%m/%Y": user_dateformat.setSelectedItem("dd/mm/yyyy")
        elif userdateformat == "%m/%d/%Y": user_dateformat.setSelectedItem("mm/dd/yyyy")
        elif userdateformat == "%Y%m%d": user_dateformat.setSelectedItem("yyyymmdd")
        else: user_dateformat.setSelectedItem("yyyy/mm/dd")

        label10 = JLabel("Strip non ASCII characters from CSV extract?")
        user_selectStripASCII = JCheckBox("", lStripASCII)

        label11 = JLabel("Change CSV extract Delimiter from default:")
        user_selectDELIMITER = JComboBox(GlobalVars.ALLOWED_CSV_FILE_DELIMITER_STRINGS)
        user_selectDELIMITER.setSelectedItem(csvDelimiter)

        labelBOM = JLabel("Write BOM (Byte Order Mark) to file (helps Excel open files)?")
        user_selectBOM = JCheckBox("", lWriteBOMToExportFile_SWSS)

        labelExportParameters = JLabel("Write parameters out to file (added as rows at EOF)?")
        user_ExportParameters = JCheckBox("", lWriteParametersToExportFile_SWSS)

        labelAutoExtract = JLabel("Enable Auto Extract?")
        user_AutoExtract = JCheckBox("", autoExtract_ESB)

        label12 = JLabel("Turn DEBUG Verbose messages on?")
        user_selectDEBUG = JCheckBox("", debug)

        userFilters = JPanel(GridLayout(0, 2))
        userFilters.add(label1)
        userFilters.add(user_hideHiddenSecurities)
        userFilters.add(label2)
        userFilters.add(user_hideInactiveAccounts)
        userFilters.add(label3)
        userFilters.add(user_hideHiddenAccounts)
        userFilters.add(label4)
        userFilters.add(user_selectCurrency)
        userFilters.add(label5)
        userFilters.add(user_selectTicker)
        userFilters.add(label6)
        userFilters.add(user_selectAccounts)

        userFilters.add(JLabel("-"*30)); userFilters.add(JLabel("-"*30))

        userFilters.add(label9)
        userFilters.add(user_dateformat)
        userFilters.add(label10)
        userFilters.add(user_selectStripASCII)
        userFilters.add(label11)
        userFilters.add(user_selectDELIMITER)
        userFilters.add(labelBOM)
        userFilters.add(user_selectBOM)
        userFilters.add(labelExportParameters)
        userFilters.add(user_ExportParameters)
        userFilters.add(labelAutoExtract)
        userFilters.add(user_AutoExtract)
        userFilters.add(label12)
        userFilters.add(user_selectDEBUG)

        _exit = False

        options = ["ABORT", "CSV Extract"]
        rowHeight = 24
        rows = 15
        jsp = MyJScrollPaneForJOptionPane(userFilters, None, 900, rows * rowHeight)
        userAction = (JOptionPane.showOptionDialog(extract_data_frame_, jsp, "EXTRACT SECURITY BALANCES: Set Script Parameters....",
                                                   JOptionPane.OK_CANCEL_OPTION,
                                                   JOptionPane.QUESTION_MESSAGE,
                                                   getMDIcon(lAlwaysGetIcon=True),
                                                   options, options[1]))
        if userAction == 1:
            myPrint("DB", "Extract chosen")
            GlobalVars.DISPLAY_DATA = False
            GlobalVars.EXTRACT_DATA = True
        else:
            myPrint("B", "User Cancelled Parameter selection.. Will abort..")
            _exit = True
            GlobalVars.DISPLAY_DATA = False
            GlobalVars.EXTRACT_DATA = False

        if not _exit:
            hideHiddenSecurities = user_hideHiddenSecurities.isSelected()
            hideInactiveAccounts = user_hideInactiveAccounts.isSelected()
            hideHiddenAccounts = user_hideHiddenAccounts.isSelected()

            if user_selectCurrency.getText() == "ALL" or user_selectCurrency.getText().strip() == "":
                lAllCurrency = True
                filterForCurrency = "ALL"
            else:
                lAllCurrency = False
                filterForCurrency = user_selectCurrency.getText()

            if user_selectTicker.getText() == "ALL" or user_selectTicker.getText().strip() == "":
                lAllSecurity = True
                filterForSecurity = "ALL"
            else:
                lAllSecurity = False
                filterForSecurity = user_selectTicker.getText()

            if user_selectAccounts.getText() == "ALL" or user_selectAccounts.getText().strip() == "":
                lAllAccounts = True
                filterForAccounts = "ALL"
            else:
                lAllAccounts = False
                filterForAccounts = user_selectAccounts.getText()

            if user_dateformat.getSelectedItem() == "dd/mm/yyyy": userdateformat = "%d/%m/%Y"
            elif user_dateformat.getSelectedItem() == "mm/dd/yyyy": userdateformat = "%m/%d/%Y"
            elif user_dateformat.getSelectedItem() == "yyyy/mm/dd": userdateformat = "%Y/%m/%d"
            elif user_dateformat.getSelectedItem() == "yyyymmdd": userdateformat = "%Y%m%d"
            else:
                # PROBLEM /  default
                userdateformat = "%Y/%m/%d"

            lStripASCII = user_selectStripASCII.isSelected()

            csvDelimiter = validateCSVFileDelimiter(user_selectDELIMITER.getSelectedItem())

            lWriteBOMToExportFile_SWSS = user_selectBOM.isSelected()
            lWriteParametersToExportFile_SWSS = user_ExportParameters.isSelected()
            autoExtract_ESB = user_AutoExtract.isSelected()

            debug = user_selectDEBUG.isSelected()

            listExtractSecurityBalancesParameters()

        return _exit

    def listExtractTrunkParameters():
        myPrint("B","---------------------------------------------------------------------------------------")
        myPrint("B","Parameters: Decrypt & extract raw Trunk file:")
        myPrint("B", "  Auto Extract.........................:", autoExtract_ETRUNK)
        myPrint("B","---------------------------------------------------------------------------------------")

    def setupExtractTrunkParameters():
        # ##############################################
        # EXTRACT_TRUNK PARAMETER SCREEN
        # ##############################################

        global debug
        global autoExtract_ETRUNK

        labelAutoExtract = JLabel("Enable Auto Extract?")
        user_AutoExtract = JCheckBox("", autoExtract_ETRUNK)

        labelDEBUG = JLabel("Turn DEBUG Verbose messages on?")
        user_selectDEBUG = JCheckBox("", debug)

        userFilters = JPanel(GridLayout(0, 2))
        userFilters.add(labelAutoExtract)
        userFilters.add(user_AutoExtract)
        userFilters.add(labelDEBUG)
        userFilters.add(user_selectDEBUG)

        _exit = False

        options = ["ABORT", "DECRYPT & EXTRACT TRUNK"]
        userAction = (JOptionPane.showOptionDialog(extract_data_frame_, userFilters, "DECRYPT & EXTRACT raw Trunk file: Set Script Parameters....",
                                                   JOptionPane.OK_CANCEL_OPTION,
                                                   JOptionPane.QUESTION_MESSAGE,
                                                   getMDIcon(lAlwaysGetIcon=True),
                                                   options, options[1]))
        if userAction == 1:
            myPrint("DB", "Extract chosen")
            GlobalVars.DISPLAY_DATA = False
            GlobalVars.EXTRACT_DATA = True
        else:
            myPrint("B", "User Cancelled Parameter selection.. Will abort..")
            _exit = True
            GlobalVars.DISPLAY_DATA = False
            GlobalVars.EXTRACT_DATA = False

        if not _exit:
            autoExtract_ETRUNK = user_AutoExtract.isSelected()
            debug = user_selectDEBUG.isSelected()
            listExtractTrunkParameters()

        return _exit

    def listExtractJSONParameters():
        myPrint("B","---------------------------------------------------------------------------------------")
        myPrint("B","Parameters: Extract raw data as JSON file:")
        myPrint("B", "  Auto Extract.........................:", autoExtract_JSON)
        myPrint("B","---------------------------------------------------------------------------------------")

    def setupExtractJSONParameters():
        # ##############################################
        # EXTRACT_JSON PARAMETER SCREEN
        # ##############################################

        global debug
        global autoExtract_JSON

        labelAutoExtract = JLabel("Enable Auto Extract?")
        user_AutoExtract = JCheckBox("", autoExtract_JSON)

        labelDEBUG = JLabel("Turn DEBUG Verbose messages on?")
        user_selectDEBUG = JCheckBox("", debug)

        userFilters = JPanel(GridLayout(0, 2))
        userFilters.add(labelAutoExtract)
        userFilters.add(user_AutoExtract)
        userFilters.add(labelDEBUG)
        userFilters.add(user_selectDEBUG)

        _exit = False

        options = ["ABORT", "EXTRACT RAW JSON"]
        userAction = (JOptionPane.showOptionDialog(extract_data_frame_, userFilters, "EXTRACT raw data as JSON file: Set Script Parameters....",
                                                   JOptionPane.OK_CANCEL_OPTION,
                                                   JOptionPane.QUESTION_MESSAGE,
                                                   getMDIcon(lAlwaysGetIcon=True),
                                                   options, options[1]))
        if userAction == 1:
            myPrint("DB", "Extract chosen")
            GlobalVars.DISPLAY_DATA = False
            GlobalVars.EXTRACT_DATA = True
        else:
            myPrint("B", "User Cancelled Parameter selection.. Will abort..")
            _exit = True
            GlobalVars.DISPLAY_DATA = False
            GlobalVars.EXTRACT_DATA = False

        if not _exit:
            autoExtract_JSON = user_AutoExtract.isSelected()
            debug = user_selectDEBUG.isSelected()
            listExtractJSONParameters()

        return _exit

    def listExtractAttachmentsParameters():
        myPrint("B","---------------------------------------------------------------------------------------")
        myPrint("B","Parameters: Extract Attachments:")
        myPrint("B", "  Auto Extract.........................:", autoExtract_EATTACH)
        myPrint("B","---------------------------------------------------------------------------------------")

    def setupExtractAttachmentsParameters():
        # ##############################################
        # EXTRACT_ATTACHMENTS PARAMETER SCREEN
        # ##############################################

        global debug
        global autoExtract_EATTACH

        labelAutoExtract = JLabel("Enable Auto Extract?")
        user_AutoExtract = JCheckBox("", autoExtract_EATTACH)

        labelDEBUG = JLabel("Turn DEBUG Verbose messages on?")
        user_selectDEBUG = JCheckBox("", debug)

        userFilters = JPanel(GridLayout(0, 2))
        userFilters.add(labelAutoExtract)
        userFilters.add(user_AutoExtract)
        userFilters.add(labelDEBUG)
        userFilters.add(user_selectDEBUG)

        _exit = False

        options = ["ABORT", "EXTRACT ATTACHMENTS"]
        userAction = (JOptionPane.showOptionDialog(extract_data_frame_, userFilters, "Extract Attachments: Set Script Parameters....",
                                                   JOptionPane.OK_CANCEL_OPTION,
                                                   JOptionPane.QUESTION_MESSAGE,
                                                   getMDIcon(lAlwaysGetIcon=True),
                                                   options, options[1]))
        if userAction == 1:
            myPrint("DB", "Extract chosen")
            GlobalVars.DISPLAY_DATA = False
            GlobalVars.EXTRACT_DATA = True
        else:
            myPrint("B", "User Cancelled Parameter selection.. Will abort..")
            _exit = True
            GlobalVars.DISPLAY_DATA = False
            GlobalVars.EXTRACT_DATA = False

        if not _exit:
            autoExtract_EATTACH = user_AutoExtract.isSelected()
            debug = user_selectDEBUG.isSelected()
            listExtractAttachmentsParameters()

        return _exit

    class StoreDateInt:
        def __init__(self, dateInt, dateFormat):
            self.dateInt        = dateInt
            self.dateFormat     = dateFormat
            self.expired        = False

        def setExpired(self, lExpired): self.expired = lExpired
        def getDateInt(self):           return self.dateInt

        def getDateIntFormatted(self):
            if self.expired: return "EXPIRED"
            if self.getDateInt() == 0 or self.getDateInt() == 19700101: return ""

            dateasdate = datetime.datetime.strptime(str(self.getDateInt()), "%Y%m%d")  # Convert to Date field
            return dateasdate.strftime(self.dateFormat)

        def __str__(self):      return self.getDateIntFormatted()
        def __repr__(self):     return self.__str__()                                                                   # noqa
        def toString(self):     return self.__str__()                                                                   # noqa

    class MyMoneydanceEventListener(AppEventListener):

        def __init__(self, theFrame):
            self.alreadyClosed = False
            self.theFrame = theFrame
            self.myModuleID = myModuleID

        def getMyself(self):
            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")
            fm = MD_REF.getModuleForID(self.myModuleID)
            if fm is None: return None, None
            try:
                pyObject = getFieldByReflection(fm, "extensionObject")
            except:
                myPrint("DB","Error retrieving my own Python extension object..?")
                dump_sys_error_to_md_console_and_errorlog()
                return None, None

            return fm, pyObject

        # noinspection PyMethodMayBeStatic
        def handleEvent(self, appEvent):
            myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()")
            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
            myPrint("DB", "I am .handleEvent() within %s" %(classPrinter("MoneydanceAppListener", self.theFrame.MoneydanceAppListener)))
            myPrint("DB","Extension .handleEvent() received command: %s" %(appEvent))

            if self.alreadyClosed:
                myPrint("DB","....I'm actually still here (MD EVENT %s CALLED).. - Ignoring and returning back to MD...." %(appEvent))
                return

            # MD doesn't call .unload() or .cleanup(), so if uninstalled I need to close myself
            fm, pyObject = self.getMyself()
            myPrint("DB", "Checking myself: %s : %s" %(fm, pyObject))
            if (((fm is None and "__file__" not in globals()) or (self.theFrame.isRunTimeExtension and pyObject is None))
                    and appEvent != AppEventManager.APP_EXITING):
                myPrint("B", "@@ ALERT - I've detected that I'm no longer installed as an extension - I will deactivate.. (switching event code to :close)")
                appEvent = "%s:customevent:close" %self.myModuleID

            # I am only closing Toolbox when a new Dataset is opened.. I was calling it on MD Close/Exit, but it seemed to cause an Exception...
            if (appEvent == AppEventManager.FILE_CLOSING
                    or appEvent == AppEventManager.FILE_CLOSED
                    or appEvent == AppEventManager.FILE_OPENING
                    or appEvent == AppEventManager.APP_EXITING):
                myPrint("DB","@@ Ignoring MD handleEvent: %s" %(appEvent))

            elif (appEvent == AppEventManager.FILE_OPENED or appEvent == "%s:customevent:close" %self.myModuleID):
                if debug:
                    myPrint("DB","MD event %s triggered.... Will call GenericWindowClosingRunnable (via the Swing EDT) to push a WINDOW_CLOSING Event to %s to close itself (while I exit back to MD quickly) ...." %(appEvent, self.myModuleID))
                else:
                    myPrint("B","Moneydance triggered event %s triggered - So I am closing %s now...." %(appEvent, self.myModuleID))
                self.alreadyClosed = True
                try:
                    # t = Thread(GenericWindowClosingRunnable(self.theFrame))
                    # t.start()
                    SwingUtilities.invokeLater(GenericWindowClosingRunnable(self.theFrame))
                    myPrint("DB","Back from calling GenericWindowClosingRunnable to push a WINDOW_CLOSING Event (via the Swing EDT) to %s.... ;-> ** I'm getting out quick! **" %(self.myModuleID))
                except:
                    dump_sys_error_to_md_console_and_errorlog()
                    myPrint("B","@@ ERROR calling GenericWindowClosingRunnable to push a WINDOW_CLOSING Event (via the Swing EDT) to %s.... :-< ** I'm getting out quick! **" %(self.myModuleID))
                if not debug: myPrint("DB","Returning back to Moneydance after calling for %s to close...." %self.myModuleID)

    ####################################################################################################################

    if checkObjectInNameSpace(u"moneydance_extension_parameter") and GlobalVars.i_am_an_extension_so_run_headless:
        MD_EXTENSION_PARAMETER = moneydance_extension_parameter
        cmd, cmdParam = decodeCommand(MD_EXTENSION_PARAMETER)
    else:
        MD_EXTENSION_PARAMETER = ""
        cmd = cmdParam = ""

    cmd = cmd.lower()
    cmdParam = cmdParam.lower()

    GlobalVars.AUTO_INVOKE_CALLED = (cmd == "autoextract")

    GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE = (MD_EXTENSION_PARAMETER == AppEventManager.FILE_CLOSING)
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

    GlobalVars.AUTO_EXTRACT_MODE = (cmd == "menu2_auto" or GlobalVars.AUTO_INVOKE_CALLED or GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE)

    GlobalVars.AUTO_INVOKE_THEN_QUIT = False
    if GlobalVars.AUTO_INVOKE_CALLED:
        GlobalVars.AUTO_INVOKE_THEN_QUIT = (cmdParam == "quit")

    myPrint("B", "Book: '%s', Auto Extract Mode: %s, Auto Invoke: %s (MD Quit after extract: %s), Handle_Event triggered: %s (Menu/Parameter/Event detected: '%s')"
            %(MD_REF.getCurrentAccountBook(), GlobalVars.AUTO_EXTRACT_MODE, GlobalVars.AUTO_INVOKE_CALLED, GlobalVars.AUTO_INVOKE_THEN_QUIT, GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE, MD_EXTENSION_PARAMETER))

    ####################################################################################################################
    if not GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE:
        MD_REF.getUI().setStatus(">> StuWareSoftSystems - %s launching......." %(GlobalVars.thisScriptName),0)
    ####################################################################################################################


    class MainAppRunnable(Runnable):
        def __init__(self): pass

        def run(self):                                                                                                  # noqa
            global extract_data_frame_      # global as defined / changed here

            # common
            global lWriteBOMToExportFile_SWSS, userdateformat, lStripASCII, csvDelimiter
            global lAllCurrency, filterForCurrency
            global hideHiddenSecurities, lAllSecurity, filterForSecurity
            global hideInactiveAccounts, hideHiddenAccounts, lAllAccounts, filterForAccounts
            global whichDefaultExtractToRun_SWSS, lWriteParametersToExportFile_SWSS, lAllowEscapeExitApp_SWSS

            # all
            global autoExtract_SG2020, autoExtract_ERTC, autoExtract_EAR, autoExtract_EIT, autoExtract_ECH, autoExtract_ESB, autoExtract_ETRUNK, autoExtract_JSON, autoExtract_EATTACH

            # extract_account_registers_csv
            global lIncludeOpeningBalances_EAR, lIncludeBalanceAdjustments_EAR
            global userdateStart_EAR, userdateEnd_EAR, lIncludeSubAccounts_EAR
            global lAllTags_EAR, tagFilter_EAR, lExtractAttachments_EAR
            global saveDropDownAccountUUID_EAR, lIncludeInternalTransfers_EAR, saveDropDownDateRange_EAR
            global lAllText_EAR, textFilter_EAR
            global lAllCategories_EAR, categoriesFilter_EAR

            # extract_investment_transactions_csv
            global lIncludeOpeningBalances, lIncludeBalanceAdjustments, lAdjustForSplits, lExtractAttachments_EIT, lOmitLOTDataFromExtract_EIT, lExtractExtraSecurityAcctInfo
            global lFilterDateRange_EIT, filterDateStart_EIT, filterDateEnd_EIT

            # extract_security_balances_csv
            # None

            # extract_currency_history_csv
            global lSimplify_ECH, userdateStart_ECH, userdateEnd_ECH, hideHiddenCurrencies_ECH

            # stockglance2020
            global lIncludeCashBalances
            global lSplitSecuritiesByAccount, lExcludeTotalsFromCSV, _column_widths_SG2020, lIncludeFutureBalances_SG2020
            global maxDecimalPlacesRounding_SG2020, lUseCurrentPrice_SG2020

            # extract_reminders_csv
            global _column_widths_ERTC, lExtractFutureRemindersToo_ERTC


            myPrint("DB", "In MainAppRunnable()", inspect.currentframe().f_code.co_name, "()")
            myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

            if not SwingUtilities.isEventDispatchThread():
                if GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE:
                    myPrint("B", "Allowing auto extract(s) to run on non-EDT thread - as triggered from file closing event....")
                else:
                    raise Exception("LOGIC ERROR: Should only be run on the EDT!?")

            if MD_REF.getCurrentAccountBook() is None:
                msgTxt = "Moneydance appears to be empty - no data to scan - aborting..."
                myPrint("B", msgTxt)
                if not GlobalVars.AUTO_EXTRACT_MODE:
                    myPopupInformationBox(None, msgTxt, "EMPTY DATASET", theMessageType=JOptionPane.ERROR_MESSAGE)
                raise Exception(msgTxt)

            if GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE:
                extract_data_frame_ = None
            else:
                # Create application JFrame() so that all popups have correct Moneydance Icons etc
                # JFrame.setDefaultLookAndFeelDecorated(True)   # Note: Darcula Theme doesn't like this and seems to be OK without this statement...
                extract_data_frame_ = MyJFrame()
                extract_data_frame_.setName(u"%s_main" %(myModuleID))
                if (not Platform.isMac()):
                    MD_REF.getUI().getImages()
                    extract_data_frame_.setIconImage(MDImages.getImage(MD_REF.getSourceInformation().getIconResource()))
                extract_data_frame_.setVisible(False)
                extract_data_frame_.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE)
                myPrint("DB","Main JFrame %s for application created.." %(extract_data_frame_.getName()))

            try:

                GlobalVars.csvfilename = None
                GlobalVars.csvfilename_future = None
                GlobalVars.decimalCharSep = MD_REF.getPreferences().getDecimalChar()
                csvDelimiter = validateCSVFileDelimiter(csvDelimiter)   # Get initial default delimiter (NOTE: Parameters already preloaded at this point)
                myPrint("DB", "MD's Decimal point: '%s', CSV Delimiter set to: '%s'" %(GlobalVars.decimalCharSep, csvDelimiter))

                GlobalVars.sdf = SimpleDateFormat("dd/MM/yyyy")

                GlobalVars.DISPLAY_DATA = False
                GlobalVars.EXTRACT_DATA = False

                GlobalVars.AUTO_MESSAGES = []

                #######################
                # Validate auto extract

                GlobalVars.defaultFileName_SG2020 = "stockglance2020_extract_stock_balances"
                GlobalVars.defaultFileName_ERTC = "extract_reminders"
                GlobalVars.defaultFileName_future_ERTC = "extract_future_reminders"
                GlobalVars.defaultFileName_EAR = "extract_account_registers"
                GlobalVars.defaultFileName_EIT = "extract_investment_transactions"
                GlobalVars.defaultFileName_ECH = "extract_currency_history"
                GlobalVars.defaultFileName_ESB = "extract_security_balances"
                GlobalVars.defaultFileName_ETRUNK = "extract_trunk"
                GlobalVars.defaultFileName_JSON = "extract_json"
                GlobalVars.defaultFileName_EATTACH = "extract_attachments"


                didDisableALL_attachments = False

                if GlobalVars.AUTO_EXTRACT_MODE:
                    iCountAutos = 0
                    for checkAutoExtract in [autoExtract_SG2020, autoExtract_ERTC, autoExtract_EAR, autoExtract_EIT, autoExtract_ECH, autoExtract_ESB, autoExtract_ETRUNK, autoExtract_JSON, autoExtract_EATTACH]:
                        if checkAutoExtract: iCountAutos += 1

                    if iCountAutos < 1:
                        GlobalVars.AUTO_EXTRACT_MODE = False
                        msgTxt = "@@ AUTO EXTRACT MODE DISABLED - No auto extracts found/enabled @@"
                        myPrint("B", msgTxt)
                        if not GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE:
                            MyPopUpDialogBox(extract_data_frame_, theStatus=msgTxt,
                                             theMessage="Configure Auto Extract Mode by running required extract(s) manually first (and selecting 'auto extract')",
                                             theTitle="EXTRACT_DATA: AUTO_MODE",
                                             lModal=False).go()

                    elif GlobalVars.scriptpath is None or GlobalVars.scriptpath == "" or not os.path.isdir(GlobalVars.scriptpath):
                        GlobalVars.AUTO_EXTRACT_MODE = False
                        msgTxt = "@@ AUTO EXTRACT MODE DISABLED: Pre-saved extract folder appears invalid @@"
                        myPrint("B", "%s: '%s'" %(msgTxt, GlobalVars.scriptpath))
                        if not GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE:
                            MyPopUpDialogBox(extract_data_frame_, theStatus=msgTxt,
                                             theMessage="Configure Auto Extract Mode by running required extract(s) manually first (and selecting the folder to save extracts)\n"
                                                                "Invalid extract folder:\n"
                                                                "'%s'" %(GlobalVars.scriptpath),
                                             theTitle="EXTRACT_DATA: AUTO_MODE",
                                             lModal=False).go()

                    else:

                        for checkFileName in [GlobalVars.defaultFileName_SG2020, GlobalVars.defaultFileName_ERTC,
                                              GlobalVars.defaultFileName_future_ERTC,
                                              GlobalVars.defaultFileName_EAR, GlobalVars.defaultFileName_EIT,
                                              GlobalVars.defaultFileName_ECH, GlobalVars.defaultFileName_ESB,
                                              GlobalVars.defaultFileName_ETRUNK, GlobalVars.defaultFileName_JSON]:

                            if "_trunk".lower() in checkFileName.lower(): chkExtnType = ""
                            elif "_json".lower() in checkFileName.lower(): chkExtnType = ".json"
                            else: chkExtnType = ".csv"

                            checkPath = os.path.join(GlobalVars.scriptpath, MD_REF.getCurrentAccountBook().getName() + "_" + checkFileName + chkExtnType)
                            if check_file_writable(checkPath):
                                myPrint("B", "AUTO EXTRACT: CONFIRMED >> Path: '%s' writable... (exists/overwrite: %s)" %(checkPath, os.path.exists(checkPath)))
                            else:
                                GlobalVars.AUTO_EXTRACT_MODE = False
                                msgTxt = "@@ AUTO EXTRACT MODE DISABLED: Default extract path invalid (review console) @@"
                                myPrint("B", "%s: '%s'" %(msgTxt, checkPath))
                                if not GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE:
                                    MyPopUpDialogBox(extract_data_frame_, theStatus=msgTxt,
                                                     theMessage="Configure Auto Extract Mode by running required extract(s) manually first (and selecting the directory to save extracts)\n"
                                                                "Invalid path:\n"
                                                                "'%s'" %(checkPath),
                                                     theTitle="EXTRACT_DATA: AUTO_MODE",
                                                     lModal=False).go()
                                break

                    if not GlobalVars.AUTO_EXTRACT_MODE:
                        myPrint("B", "@@ AUTO EXTRACT DISABLED - Aborting execution.....! @@")
                        raise QuickAbortThisScriptException

                #######################


                if GlobalVars.AUTO_EXTRACT_MODE:
                    exitScript = False
                    lExtractStockGlance2020 = autoExtract_SG2020
                    lExtractReminders = autoExtract_ERTC
                    lExtractAccountTxns = autoExtract_EAR
                    lExtractInvestmentTxns = autoExtract_EIT
                    lExtractSecurityBalances = autoExtract_ESB
                    lExtractCurrencyHistory = autoExtract_ECH
                    lExtractTrunk = autoExtract_ETRUNK
                    lExtractJSON = autoExtract_JSON
                    lExtractAttachments = autoExtract_EATTACH
                    GlobalVars.DISPLAY_DATA = False
                    GlobalVars.EXTRACT_DATA = True

                    if GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE and lExtractAttachments:
                        didDisableALL_attachments = True
                        lExtractAttachments = False

                    myPrint("B", "AUTO EXTRACT MODE: Will auto extract the following...:\n"
                                 "     StockGlance2020.........: %s\n"
                                 "     Reminders...............: %s\n"
                                 "     Account Transactions....: %s\n"
                                 "     Investment Transactions.: %s\n"
                                 "     Security Balances.......: %s\n"
                                 "     Currency History........: %s\n"
                                 "     Decrypt & Extract Trunk.: %s\n"
                                 "     Extract raw data as JSON: %s\n"
                                 "     Attachments.............: %s%s\n"
                            %(autoExtract_SG2020, autoExtract_ERTC, autoExtract_EAR, autoExtract_EIT, autoExtract_ESB, autoExtract_ECH, autoExtract_ETRUNK, autoExtract_JSON,
                              autoExtract_EATTACH, "" if not (didDisableALL_attachments) else " *** DISABLING extract of ALL ATTACHMENTS (when in auto extract on file closing mode) ***"))

                    if lExtractAttachments_EAR or lExtractAttachments_EIT:
                        if lExtractAttachments_EAR:
                            txt = "*** DISABLING extract of ATTACHMENTS for: Account Register Transaction ***"
                            GlobalVars.AUTO_MESSAGES.append(txt)
                            myPrint("B", txt)
                            lExtractAttachments_EAR = False

                        if lExtractAttachments_EIT:
                            txt = "*** DISABLING extract of ATTACHMENTS for: Investment Transactions      ***"
                            GlobalVars.AUTO_MESSAGES.append(txt)
                            myPrint("B", txt)
                            lExtractAttachments_EIT = False
                        GlobalVars.AUTO_MESSAGES.append("")

                    if lExtractStockGlance2020:     listExtractSG2020Parameters()
                    if lExtractReminders:           listExtractRemindersParameters()
                    if lExtractAccountTxns:         listExtractAccountTxnsParameters()
                    if lExtractInvestmentTxns:      listExtractInvestmentAccountParameters()
                    if lExtractCurrencyHistory:     listExtractCurrencyHistoryParameters()
                    if lExtractSecurityBalances:    listExtractSecurityBalancesParameters()
                    if lExtractTrunk:               listExtractTrunkParameters()
                    if lExtractJSON:                listExtractJSONParameters()
                    if lExtractAttachments:         listExtractAttachmentsParameters()

                else:
                    exitScript, whichDefaultExtractToRun_SWSS, lExtractStockGlance2020, lExtractReminders, lExtractAccountTxns, lExtractInvestmentTxns, lExtractSecurityBalances, lExtractCurrencyHistory, lExtractTrunk, lExtractJSON, lExtractAttachments \
                        = getExtractChoice(whichDefaultExtractToRun_SWSS)

                if exitScript:
                    myPrint("B", "User chose to cancel at extract choice screen.... exiting")
                    raise QuickAbortThisScriptException

                # Set up the parameters for each separate extract
                if not GlobalVars.AUTO_EXTRACT_MODE:

                    if lExtractAccountTxns:
                        exitScript = setupExtractAccountTxnsParameters()

                    elif lExtractInvestmentTxns:
                        exitScript = setupExtractInvestmentAccountParameters()

                    elif lExtractSecurityBalances:
                        exitScript = setupExtractSecurityBalancesParameters()

                    elif lExtractCurrencyHistory:
                        exitScript = setupExtractCurrencyHistoryParameters()

                    elif lExtractStockGlance2020:
                        exitScript = setupExtractSG2020Parameters()

                    elif lExtractReminders:
                        exitScript = setupExtractRemindersParameters()

                    elif lExtractTrunk:
                        exitScript = setupExtractTrunkParameters()

                    elif lExtractJSON:
                        exitScript = setupExtractJSONParameters()

                    elif lExtractAttachments:
                        exitScript = setupExtractAttachmentsParameters()

                    else:
                        msgTxt = "ERROR - Failed to detect correct parameter screen - will exit"
                        myPrint("B", msgTxt)
                        myPopupInformationBox(extract_data_frame_, msgTxt, theMessageType=JOptionPane.ERROR_MESSAGE)
                        exitScript = True


                if exitScript:raise QuickAbortThisScriptException

                myPrint("DB", "DEBUG IS ON..")

                # Now get the extract filename
                GlobalVars.csvfilename = None
                GlobalVars.csvfilename_future = None

                if GlobalVars.EXTRACT_DATA:
                    listCommonExtractParameters()

                    if lExcludeTotalsFromCSV:
                        myPrint("B",  "Exclude Totals from CSV (to assist Pivot tables)..: %s" %(lExcludeTotalsFromCSV))

                if not GlobalVars.AUTO_EXTRACT_MODE:

                    if GlobalVars.EXTRACT_DATA:

                        name_addition = "" + currentDateTimeMarker() + ".csv"
                        if lExtractAccountTxns:
                            extract_filename = GlobalVars.defaultFileName_EAR + name_addition
                        elif lExtractInvestmentTxns:
                            extract_filename = GlobalVars.defaultFileName_EIT + name_addition
                        elif lExtractSecurityBalances:
                            extract_filename = GlobalVars.defaultFileName_ESB + name_addition
                        elif lExtractCurrencyHistory:
                            extract_filename = GlobalVars.defaultFileName_ECH + name_addition
                        elif lExtractStockGlance2020:
                            extract_filename = GlobalVars.defaultFileName_SG2020 + name_addition
                        elif lExtractReminders:
                            extract_filename = GlobalVars.defaultFileName_ERTC + name_addition
                        elif lExtractTrunk:
                            name_addition = "" + currentDateTimeMarker() + ""
                            extract_filename = GlobalVars.defaultFileName_ETRUNK + name_addition
                        elif lExtractJSON:
                            name_addition = "" + currentDateTimeMarker() + ".json"
                            extract_filename = GlobalVars.defaultFileName_JSON + name_addition
                        elif lExtractAttachments:
                            name_addition = "" + "_" + UUID.randomUUID().toString() + currentDateTimeMarker()
                            extract_filename = GlobalVars.defaultFileName_EATTACH + name_addition

                        else:
                            raise Exception("@@ ERROR - Invalid extract detected....?!")

                        extract_filename = MD_REF.getCurrentAccountBook().getName() + "_" + extract_filename


                        if lExtractAttachments:

                            def grabTheFolderForAttachmentsExtract():
                                myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

                                if GlobalVars.scriptpath == "" or GlobalVars.scriptpath is None:  # No parameter saved / loaded from disk
                                    GlobalVars.scriptpath = get_home_dir()

                                myPrint("DB", "Default file extract output path is....:", GlobalVars.scriptpath)

                                GlobalVars.extractFolderName = ""

                                theTitle = "Select Folder for extract (CANCEL=NO EXTRACT)"

                                GlobalVars.extractFolderName = getFileFromFileChooser(extract_data_frame_,      # Parent frame or None
                                                                    GlobalVars.scriptpath,                      # Starting path
                                                                    None,                                       # Default Filename
                                                                    theTitle,                                   # Title
                                                                    False,                                      # Multi-file selection mode
                                                                    True,                                       # True for Open/Load, False for Save
                                                                    False,                                      # True = Files, else Dirs
                                                                    "EXTRACT ATTACHMENTS",                      # Load/Save button text, None for defaults
                                                                    None,                                       # File filter (non Mac only). Example: "txt" or "qif"
                                                                    lAllowTraversePackages=True,
                                                                    lForceJFC=False,
                                                                    lForceFD=False,
                                                                    lAllowNewFolderButton=True,
                                                                    lAllowOptionsButton=True)

                                if (GlobalVars.extractFolderName is None) or GlobalVars.extractFolderName == "":
                                    GlobalVars.EXTRACT_DATA = False
                                    GlobalVars.extractFolderName = None
                                    _txt = "User chose to cancel or no folder selected >>  So no Extract will be performed... "
                                    myPrint("B", _txt)
                                    myPopupInformationBox(extract_data_frame_, _txt, "FILE EXTRACT")
                                    return

                                if not os.path.exists(GlobalVars.extractFolderName) or not os.path.isdir(GlobalVars.extractFolderName):
                                    _txt = "Error: Folder does not exist?"
                                    myPrint("B", _txt)
                                    myPopupInformationBox(extract_data_frame_, _txt, "FILE EXTRACT")
                                    GlobalVars.extractFolderName = ""
                                    GlobalVars.EXTRACT_DATA = False
                                    return

                                GlobalVars.scriptpath = GlobalVars.extractFolderName

                                GlobalVars.extractFolderName = os.path.join(GlobalVars.extractFolderName, extract_filename)
                                if os.path.exists(GlobalVars.extractFolderName):
                                    raise Exception("ERROR: Folder '%s' already exists?" %(GlobalVars.extractFolderName))

                                myPrint("B", "Folder that will be created is:", GlobalVars.extractFolderName)

                            grabTheFolderForAttachmentsExtract()
                            GlobalVars.csvfilename = GlobalVars.extractFolderName   # Just populate with something

                        else:

                            def grabTheFile():
                                global attachmentDir, relativePath, lExtractAttachments_EAR, lExtractAttachments_EIT

                                myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

                                if GlobalVars.scriptpath == "" or GlobalVars.scriptpath is None:  # No parameter saved / loaded from disk
                                    GlobalVars.scriptpath = get_home_dir()

                                myPrint("DB", "Default file extract output path is....:", GlobalVars.scriptpath)

                                GlobalVars.csvfilename = ""
                                GlobalVars.csvfilename_future = ""

                                if (lExtractAccountTxns and lExtractAttachments_EAR) or (lExtractInvestmentTxns and lExtractAttachments_EIT):
                                    theTitle = "Select/Create CSV file for extract - MUST BE A UNIQUE NAME (CANCEL=NO EXTRACT)"
                                else:
                                    theTitle = "Select/Create CSV file for extract (CANCEL=NO EXTRACT)"

                                if lExtractTrunk: extnType = None
                                elif lExtractJSON: extnType = "json"
                                else: extnType = "csv"

                                GlobalVars.csvfilename = getFileFromFileChooser(extract_data_frame_,    # Parent frame or None
                                                                    GlobalVars.scriptpath,              # Starting path
                                                                    extract_filename,                   # Default Filename
                                                                    theTitle,                           # Title
                                                                    False,                              # Multi-file selection mode
                                                                    False,                              # True for Open/Load, False for Save
                                                                    True,                               # True = Files, else Dirs
                                                                    None,                               # Load/Save button text, None for defaults
                                                                    extnType,                           # File filter. Examples: None, "txt", "qif"
                                                                    lAllowTraversePackages=True,
                                                                    lForceJFC=False,
                                                                    lForceFD=True,
                                                                    lAllowNewFolderButton=True,
                                                                    lAllowOptionsButton=True)

                                if (GlobalVars.csvfilename is None) or GlobalVars.csvfilename == "":
                                    GlobalVars.EXTRACT_DATA = False
                                    GlobalVars.csvfilename = None
                                    GlobalVars.csvfilename_future = None
                                    _txt = "User chose to cancel or no file selected >>  So no Extract will be performed... "
                                    myPrint("B", _txt); myPopupInformationBox(extract_data_frame_, _txt, "FILE EXTRACT")
                                elif safeStr(GlobalVars.csvfilename).endswith(".moneydance"):
                                    myPrint("B", "User selected file:", GlobalVars.csvfilename)
                                    _txt = "Sorry - User chose to use .moneydance extension - I will not allow it!... So no Extract will be performed..."
                                    myPrint("B", _txt); myPopupInformationBox(extract_data_frame_, _txt, "FILE EXTRACT")
                                    GlobalVars.EXTRACT_DATA = False
                                    GlobalVars.csvfilename = None
                                    GlobalVars.csvfilename_future = None
                                elif ".moneydance" in os.path.dirname(GlobalVars.csvfilename):
                                    myPrint("B", "User selected file: %s" %(GlobalVars.csvfilename))
                                    _txt = "Sorry - User chose to save file in .moneydance location. NOT Good practice so I will not allow it!... So no Extract will be performed..."
                                    myPrint("B", _txt); myPopupInformationBox(extract_data_frame_, _txt, "FILE EXTRACT")
                                    GlobalVars.EXTRACT_DATA = False
                                    GlobalVars.csvfilename = None
                                    GlobalVars.csvfilename_future = None
                                else:
                                    if GlobalVars.EXTRACT_DATA: relativePath = os.path.splitext(os.path.basename(GlobalVars.csvfilename))[0]
                                    GlobalVars.scriptpath = os.path.dirname(GlobalVars.csvfilename)

                                if GlobalVars.EXTRACT_DATA:
                                    if os.path.exists(GlobalVars.csvfilename) and os.path.isfile(GlobalVars.csvfilename):
                                        myPrint("DB", "WARNING: file exists,but assuming user said OK to overwrite..")


                                if GlobalVars.EXTRACT_DATA:
                                    if check_file_writable(GlobalVars.csvfilename):
                                        if lStripASCII:
                                            myPrint("B", "Will extract data to file: %s (NOTE: Should drop non utf8 characters...)" %(GlobalVars.csvfilename))
                                        else:
                                            myPrint("B", "Will extract data to file: %s" %(GlobalVars.csvfilename))
                                    else:
                                        _txt = "Sorry - I just checked and you do not have permissions to create this file: %s" %(GlobalVars.csvfilename)
                                        myPrint("B", _txt)
                                        myPopupInformationBox(extract_data_frame_, _txt, "FILE EXTRACT")
                                        GlobalVars.csvfilename = ""
                                        GlobalVars.csvfilename_future = ""
                                        GlobalVars.EXTRACT_DATA = False
                                        return

                                    attachmentDir = None
                                    if (lExtractAccountTxns and lExtractAttachments_EAR) or (lExtractInvestmentTxns and lExtractAttachments_EIT):
                                        attachmentDir = os.path.splitext(GlobalVars.csvfilename )[0]

                                        if os.path.exists(attachmentDir):
                                            _txt = "ERROR: Attachment Directory MUST NOT PRE-EXIST: '%s'" %(attachmentDir)
                                            myPrint("B", _txt)
                                            myPopupInformationBox(extract_data_frame_, _txt, "ATTACHMENT DIRECTORY", theMessageType=JOptionPane.ERROR_MESSAGE)
                                            GlobalVars.csvfilename = ""
                                            GlobalVars.EXTRACT_DATA = False
                                            return

                                        try:
                                            os.mkdir(attachmentDir)
                                            _txt = "CREATED attachment directory: '%s'" %(attachmentDir)
                                            myPrint("B", _txt)
                                        except:
                                            _txt = "@@ FAILED to create Attachment Directory: '%s' @@" %(attachmentDir)
                                            myPrint("B", _txt)
                                            myPopupInformationBox(extract_data_frame_, _txt, "ATTACHMENT DIRECTORY", theMessageType=JOptionPane.ERROR_MESSAGE)
                                            GlobalVars.csvfilename = ""
                                            GlobalVars.EXTRACT_DATA = False
                                            return

                                    if lExtractFutureRemindersToo_ERTC and GlobalVars.csvfilename is not None and GlobalVars.csvfilename != "":
                                        dn = os.path.dirname(GlobalVars.csvfilename)
                                        full_fn = os.path.basename(GlobalVars.csvfilename)
                                        fn, extn = os.path.splitext(full_fn)
                                        if GlobalVars.csvfilename_future.endswith(name_addition):
                                            GlobalVars.csvfilename_future =  os.path.join(dn, fn.replace(name_addition, "_future_reminders" + name_addition) + extn)
                                        else:
                                            GlobalVars.csvfilename_future =  os.path.join(dn, fn + "_future_reminders" + extn)
                                        myPrint("B", "Future Reminders path set to:", GlobalVars.csvfilename_future)
                                return

                            grabTheFile()

                    if GlobalVars.csvfilename is None or GlobalVars.csvfilename == "":
                        GlobalVars.EXTRACT_DATA = False

                    # save here upfront - no need to do later
                    save_StuWareSoftSystems_parameters_to_file()

                # ############################
                # START OF MAIN CODE EXECUTION
                # ############################

                if lExtractReminders and GlobalVars.DISPLAY_DATA and lExtractFutureRemindersToo_ERTC:
                    txt = "@@ Calculation of Future Reminders IGNORED - Extract only option @@"
                    myPrint("B", txt)

                if not GlobalVars.DISPLAY_DATA and not GlobalVars.EXTRACT_DATA:
                    txt = "@@ No extract filename selected - aborting @@"
                    myPrint("B", txt)
                    raise QuickAbortThisScriptException

                if GlobalVars.AUTO_EXTRACT_MODE and GlobalVars.DISPLAY_DATA:
                    raise Exception("LOGIC ERROR - Cannot be in Auto Extract mode AND Display Data mode!?")
                elif GlobalVars.AUTO_EXTRACT_MODE and not GlobalVars.EXTRACT_DATA:
                    raise Exception("LOGIC ERROR - Cannot be in Auto Extract mode AND not in Extract Data mode!?")
                elif not GlobalVars.DISPLAY_DATA and not GlobalVars.EXTRACT_DATA:
                    raise Exception("LOGIC ERROR - not in Extract Data mode AND not in Display Data mode!?")
                elif not GlobalVars.AUTO_EXTRACT_MODE and GlobalVars.DISPLAY_DATA and GlobalVars.EXTRACT_DATA:
                    raise Exception("LOGIC ERROR - Single Extract Mode AND Extract Data mode AND Display Data mode NOT allowed!?")

                GlobalVars.countFilesCreated = 0
                GlobalVars.countErrorsDuringExtract = 0

                class DoExtractsSwingWorker(SwingWorker):

                    pleaseWaitDiag = None       # Single Instance class - so not too worried about multiple access etc

                    @staticmethod
                    def getPleaseWait():
                        # type: () -> MyPopUpDialogBox
                        return DoExtractsSwingWorker.pleaseWaitDiag

                    @staticmethod
                    def setPleaseWait(pleaseWaitDiag):
                        # type: (MyPopUpDialogBox) -> None
                        DoExtractsSwingWorker.pleaseWaitDiag = pleaseWaitDiag

                    @staticmethod
                    def killPleaseWait():
                        # type: () -> None
                        pwd = DoExtractsSwingWorker.getPleaseWait()
                        if pwd is not None:
                            pwd.kill()
                            DoExtractsSwingWorker.setPleaseWait(None)

                    def __init__(self, pleaseWaitDiag):
                        # type: (MyPopUpDialogBox) -> None
                        self.setPleaseWait(pleaseWaitDiag)

                    def process(self, chunks):              # This executes on the EDT
                        if isinstance(chunks, list): pass
                        pwd = self.getPleaseWait()
                        if pwd is not None:
                            if not self.isDone() and not self.isCancelled():
                                for pMsg in chunks:
                                    _msgTxt = pad("PLEASE WAIT - PROCESSING: %s" %(pMsg), 100, padChar=".")
                                    pwd.updateMessages(newTitle=_msgTxt, newStatus=_msgTxt)

                    def doInBackground(self):
                        myPrint("DB", "In DoExtractsSwingWorker()", inspect.currentframe().f_code.co_name, "()")
                        myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

                        GlobalVars.baseCurrency = MD_REF.getCurrentAccountBook().getCurrencies().getBaseType()

                        try:
                            cThread = Thread.currentThread()
                            if "_extn_ED" not in cThread.getName(): cThread.setName(u"%s_extn_ED" %(cThread.getName()))
                            del cThread

                            if lExtractStockGlance2020:
                                # ####################################################
                                # STOCKGLANCE2020 EXECUTION
                                # ####################################################

                                _THIS_EXTRACT_NAME = pad("EXTRACT: StockGlance2020:", 34)
                                GlobalVars.lGlobalErrorDetected = False

                                if not GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE:
                                    self.super__publish([_THIS_EXTRACT_NAME.strip()])                                   # noqa

                                if GlobalVars.AUTO_EXTRACT_MODE:
                                    GlobalVars.csvfilename = os.path.join(GlobalVars.scriptpath, MD_REF.getCurrentAccountBook().getName() + "_" + GlobalVars.defaultFileName_SG2020 + ".csv")

                                def do_stockglance2020():

                                    global lDidIUseAttachmentDir
                                    global headingNames
                                    global _SHRS_FORMATTED, _SHRS_RAW, _PRICE_FORMATTED, _PRICE_RAW, _CVALUE_FORMATTED, _CVALUE_RAW, _BVALUE_FORMATTED, _BVALUE_RAW
                                    global _CBVALUE_FORMATTED, _CBVALUE_RAW, _GAIN_FORMATTED, _GAIN_RAW, _SORT, _EXCLUDECSV, _GAINPCT
                                    global acctSeparator

                                    global __extract_data, extract_filename
                                    global lStripASCII, csvDelimiter, userdateformat, lWriteBOMToExportFile_SWSS
                                    global hideInactiveAccounts, hideHiddenAccounts, hideHiddenSecurities
                                    global lAllSecurity, filterForSecurity, lAllAccounts, filterForAccounts, lAllCurrency, filterForCurrency
                                    global whichDefaultExtractToRun_SWSS
                                    global lIncludeCashBalances, _column_widths_SG2020
                                    global lSplitSecuritiesByAccount, lExcludeTotalsFromCSV
                                    global maxDecimalPlacesRounding_SG2020, lUseCurrentPrice_SG2020
                                    global lIncludeFutureBalances_SG2020

                                    def terminate_script():
                                        myPrint("DB", _THIS_EXTRACT_NAME + "In ", inspect.currentframe().f_code.co_name, "()")
                                        myPrint("DB", _THIS_EXTRACT_NAME + "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

                                        # We have to do this here too to save the dynamic column widths....
                                        try:
                                            save_StuWareSoftSystems_parameters_to_file()
                                        except:
                                            myPrint("B", _THIS_EXTRACT_NAME + "Error - failed to save parameters to pickle file...!")
                                            dump_sys_error_to_md_console_and_errorlog()

                                        try:
                                            # NOTE - .dispose() - The windowClosed event should set .isActiveInMoneydance False and .removeAppEventListener()
                                            if not SwingUtilities.isEventDispatchThread():
                                                SwingUtilities.invokeLater(GenericDisposeRunnable(extract_data_frame_))
                                            else:
                                                extract_data_frame_.dispose()
                                        except:
                                            myPrint("B", _THIS_EXTRACT_NAME + "Error. Final dispose failed....?")
                                            dump_sys_error_to_md_console_and_errorlog()


                                    class DoTheMenu(AbstractAction):

                                        def __init__(self): pass

                                        def actionPerformed(self, event):															# noqa
                                            global lAllowEscapeExitApp_SWSS     # global as we can set this here

                                            myPrint("D", _THIS_EXTRACT_NAME + "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

                                            if event.getActionCommand().lower().startswith("page setup"):
                                                pageSetup()

                                            if event.getActionCommand().lower().startswith("about"):
                                                AboutThisScript(extract_data_frame_).go()

                                            if event.getActionCommand().lower().startswith("allow escape"):
                                                lAllowEscapeExitApp_SWSS = not lAllowEscapeExitApp_SWSS
                                                if lAllowEscapeExitApp_SWSS:
                                                    extract_data_frame_.getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0), "close-window")
                                                else:
                                                    extract_data_frame_.getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).remove(KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0))

                                                # Note: save_StuWareSoftSystems_parameters_to_file() is called within terminate_script() - so will save on exit
                                                myPrint("B", _THIS_EXTRACT_NAME + "Escape key can exit the app's main screen: %s" %(lAllowEscapeExitApp_SWSS))

                                            myPrint("D", _THIS_EXTRACT_NAME + "Exiting ", inspect.currentframe().f_code.co_name, "()")

                                    class StockGlance2020():  # MAIN program....

                                        def __init__(self): pass

                                        global hideHiddenSecurities, hideInactiveAccounts, lSplitSecuritiesByAccount, acctSeparator, lIncludeFutureBalances_SG2020
                                        global maxDecimalPlacesRounding_SG2020, lUseCurrentPrice_SG2020
                                        global headingNames
                                        global _SHRS_FORMATTED, _SHRS_RAW, _PRICE_FORMATTED, _PRICE_RAW, _CVALUE_FORMATTED, _CVALUE_RAW, _BVALUE_FORMATTED, _BVALUE_RAW, _SORT
                                        global _CBVALUE_FORMATTED, _CBVALUE_RAW, _GAIN_FORMATTED, _GAIN_RAW, _EXCLUDECSV, _GAINPCT

                                        myPrint("D", _THIS_EXTRACT_NAME + "In ", inspect.currentframe().f_code.co_name, "()")

                                        book = MD_REF.getCurrentAccountBook()

                                        GlobalVars.table = None
                                        tableModel = None
                                        footerModel = None
                                        totalBalance = None  # total of all Stock.Securities in all Accounts inb local currency
                                        totalBalanceBase = None
                                        totalCashBalanceBase = None
                                        totalCostBasisBase = None
                                        totalGainBase = None

                                        sameCurrency = None
                                        allOneCurrency = True
                                        currXrate = None
                                        lRemoveCurrColumn = None

                                        QtyOfSharesTable = None
                                        AccountsTable = None
                                        CashBalancesTable = None
                                        CostBasisTotals = None
                                        CashBalanceTableData = []
                                        moreCashBalanceAccounts = {}

                                        GlobalVars.rawFooterTable_sg2020 = None
                                        GlobalVars.rawDataTable_sg2020 = None

                                        #  Per column metadata - fields 10 - 16 not actually used but contain the raw numbers from fields 2,3,5,6 + sortfield
                                        columnNames = ["Symbol", "Stock", "Shares/Units", "Price", "Curr", "Curr Value", "Base Value", "Cost Basis",
                                                       "UnRlsd Gain", "Gain%", "Accounts",
                                                       "_Shrs", "_Price", "_CValue", "_BValue", "_CBValue", "_Gain", "_SORT", "_Exclude"]
                                        columnTypes = ["Text", "Text", "TextNumber", "TextNumber", "TextC", "TextNumber", "TextNumber",
                                                       "TextNumber", "TextNumber", "%", "Text", "N",
                                                       "N", "N", "N", "N", "N", "N", "TEXT"]
                                        headingNames = columnNames                                                      # noqa
                                        _SHRS_FORMATTED = 2                                                             # noqa
                                        _SHRS_RAW = 11                                                                  # noqa
                                        _PRICE_FORMATTED = 3                                                            # noqa
                                        _PRICE_RAW = 12                                                                 # noqa
                                        _CVALUE_FORMATTED = 5                                                           # noqa
                                        _CVALUE_RAW = 13                                                                # noqa
                                        _BVALUE_FORMATTED = 6                                                           # noqa
                                        _BVALUE_RAW = 14                                                                # noqa
                                        _CBVALUE_FORMATTED = 7                                                          # noqa
                                        _CBVALUE_RAW = 15                                                               # noqa
                                        _GAIN_FORMATTED = 8                                                             # noqa
                                        _GAIN_RAW = 16                                                                  # noqa
                                        _GAINPCT = 9                                                                    # noqa
                                        _SORT = 17                                                                      # noqa
                                        _EXCLUDECSV = 18                                                                # noqa

                                        def getTableModel(self): return self.tableModel
                                        def getFooterModel(self): return self.footerModel

                                        def generateTableModels(self, book):
                                            self.tableModel = self.generateMainTableModel(book)
                                            self.footerModel = self.generateFooterTableModel()

                                        def generateMainTableModel(self, book):
                                            global lAllCurrency, filterForCurrency, lAllSecurity, filterForSecurity

                                            myPrint("D", _THIS_EXTRACT_NAME + "In ", inspect.currentframe().f_code.co_name, "()")
                                            myPrint("D", _THIS_EXTRACT_NAME + "MD Book: ", book)

                                            _baseCurrency = MD_REF.getCurrentAccountBook().getCurrencies().getBaseType()

                                            GlobalVars.rawDataTable_sg2020 = []

                                            ct = book.getCurrencies()

                                            myPrint("D", _THIS_EXTRACT_NAME + "Base Currency: ", _baseCurrency.getIDString(), " : ", _baseCurrency.getName())

                                            allCurrencies = ct.getAllCurrencies()

                                            today = Calendar.getInstance()
                                            myPrint("D", _THIS_EXTRACT_NAME + "Running today: ", GlobalVars.sdf.format(today.getTime()))

                                            self.sumInfoBySecurity(book)  # Creates Dict(hashmap) QtyOfSharesTable, AccountsTable, CashTable : <CurrencyType, Long>  contains no account info

                                            if debug:
                                                myPrint("DB", _THIS_EXTRACT_NAME + "Result of sumInfoBySecurity(book) self.QtyOfSharesTable:        ", self.QtyOfSharesTable)
                                                myPrint("DB", _THIS_EXTRACT_NAME + "Result of sumInfoBySecurity(book) self.AccountsTable:           ", self.AccountsTable)
                                                myPrint("DB", _THIS_EXTRACT_NAME + "Result of sumInfoBySecurity(book) self.CashBalancesTable:       ", self.CashBalancesTable)
                                                myPrint("DB", _THIS_EXTRACT_NAME + "Result of sumInfoBySecurity(book) self.CostBasisTotals:         ", self.CostBasisTotals)
                                                myPrint("DB", _THIS_EXTRACT_NAME + "Result of sumInfoBySecurity(book) self.moreCashBalanceAccounts: ", self.moreCashBalanceAccounts)

                                            if len(self.QtyOfSharesTable) < 1:
                                                _msgTxt = "@@ Sorry - you have no securities - exiting... @@"
                                                GlobalVars.AUTO_MESSAGES.append(_THIS_EXTRACT_NAME + _msgTxt)
                                                myPrint("B", _THIS_EXTRACT_NAME + _msgTxt)
                                                if not GlobalVars.AUTO_EXTRACT_MODE:
                                                    DoExtractsSwingWorker.killPleaseWait()
                                                    genericSwingEDTRunner(True, True, myPopupInformationBox, extract_data_frame_, _msgTxt, "StockGlance2020", JOptionPane.WARNING_MESSAGE)
                                                return None

                                            self.totalBalance = 0.0
                                            self.totalBalanceBase = 0.0
                                            self.totalCashBalanceBase = 0.0
                                            self.totalCostBasisBase = 0.0
                                            self.totalGainBase = 0.0

                                            self.lRemoveCurrColumn = True

                                            myPrint("DB", _THIS_EXTRACT_NAME + "Now processing all securities (currencies) and building my own table of results to build GUI....")
                                            for curr in allCurrencies:
                                                # noinspection PyUnresolvedReferences
                                                if ((hideHiddenSecurities and not curr.getHideInUI()) or (
                                                        not hideHiddenSecurities)) and curr.getCurrencyType() == CurrencyType.Type.SECURITY:

                                                    # NOTE: (1.0 / .getRelativeRate() ) gives you the 'Current Price' from the History Screen
                                                    # NOTE: .getPrice(None) gives you the Current Price relative to the current Base to Security Currency..
                                                    # .......So Base>Currency rate * .getRate(None) also gives Current Price

                                                    _roundPrice = maxDecimalPlacesRounding_SG2020   # Don't use currency.getDecimalPlaces() as this is for stock qty balances, not price...!

                                                    priceDate = (0 if (lUseCurrentPrice_SG2020) else DateUtil.convertCalToInt(today))
                                                    price = round(1.0 / curr.adjustRateForSplitsInt(DateUtil.convertCalToInt(today),curr.getRelativeRate(priceDate)), _roundPrice)

                                                    qty = self.QtyOfSharesTable.get(curr)
                                                    if qty is None: qty = 0

                                                    if lAllCurrency \
                                                            or (filterForCurrency.upper().strip() in curr.getRelativeCurrency().getIDString().upper().strip()) \
                                                            or (filterForCurrency.upper().strip() in curr.getRelativeCurrency().getName().upper().strip()):
                                                        if qty > 0:
                                                            if lAllSecurity \
                                                                    or (filterForSecurity.upper().strip() in curr.getTickerSymbol().upper().strip()) \
                                                                    or (filterForSecurity.upper().strip() in curr.getName().upper().strip()):
                                                                myPrint("D", _THIS_EXTRACT_NAME + "Found Security..: ", curr, curr.getTickerSymbol(), " Curr: ", curr.getRelativeCurrency().getIDString(),
                                                                        " Price: ", price, " Qty: ", curr.formatSemiFancy(qty, GlobalVars.decimalCharSep))

                                                                securityCostBasis = self.CostBasisTotals.get(curr)

                                                                # This new loop in version_build v4b does the account split within Securities (a bit of a retrofit hack)
                                                                split_acct_array = self.AccountsTable.get(curr)

                                                                if len(split_acct_array) < 1:
                                                                    myPrint("B", _THIS_EXTRACT_NAME + "Major logic error... Aborting", curr.getName())
                                                                    raise Exception("Split Security logic...Array len <1")

                                                                for iSplitAcctArray in range(0, len(split_acct_array)):
                                                                    qtySplit = split_acct_array[iSplitAcctArray][1]

                                                                    balance = (0.0 if (qty is None) else curr.getDoubleValue(qty) * price)  # Value in Currency
                                                                    balanceSplit = (0.0 if (qtySplit is None) else curr.getDoubleValue(qtySplit) * price)  # Value in Currency
                                                                    exchangeRate = 1.0
                                                                    securityIsBase = True
                                                                    ct = curr.getTable()
                                                                    relativeToName = curr.getParameter(CurrencyType.TAG_RELATIVE_TO_CURR)
                                                                    if relativeToName is not None:
                                                                        self.currXrate = ct.getCurrencyByIDString(relativeToName)
                                                                        if self.currXrate.getIDString() == _baseCurrency.getIDString():
                                                                            myPrint("D", _THIS_EXTRACT_NAME + "Found conversion rate - but it's already the base rate..: ", relativeToName)
                                                                        else:
                                                                            securityIsBase = False
                                                                            # exchangeRate = round(self.currXrate.getRate(_baseCurrency),self.currXrate.getDecimalPlaces())
                                                                            exchangeRate = self.currXrate.getRate(_baseCurrency)
                                                                            myPrint("D", _THIS_EXTRACT_NAME + "Found conversion rate: ", relativeToName, exchangeRate)
                                                                    else:
                                                                        myPrint("D", _THIS_EXTRACT_NAME + "No conversion rate found.... Assuming Base Currency")
                                                                        self.currXrate = _baseCurrency

                                                                    # Check to see if all Security Currencies are the same...?
                                                                    if self.allOneCurrency:
                                                                        if self.sameCurrency is None:               self.sameCurrency = self.currXrate
                                                                        if self.sameCurrency != self.currXrate:     self.allOneCurrency = False

                                                                    balanceBase = (0.0 if (qty is None) else (curr.getDoubleValue(qty) * price / exchangeRate))                 # Value in Base Currency
                                                                    balanceBaseSplit = (0.0 if (qtySplit is None) else (curr.getDoubleValue(qtySplit) * price / exchangeRate))  # Value in Base Currency

                                                                    # costBasisBase = (0.0 if (securityCostBasis is None) else round(self.currXrate.getDoubleValue(securityCostBasis) / exchangeRate, 2))
                                                                    costBasisBase = (0.0 if (securityCostBasis is None) else round(self.currXrate.getDoubleValue(securityCostBasis), 2))
                                                                    gainBase = round(balanceBase, 2) - costBasisBase

                                                                    # costBasisBaseSplit = round(self.currXrate.getDoubleValue(split_acct_array[iSplitAcctArray][2]) / exchangeRate, 2)
                                                                    costBasisBaseSplit = round(self.currXrate.getDoubleValue(split_acct_array[iSplitAcctArray][2]), 2)
                                                                    gainBaseSplit = round(balanceBaseSplit, 2) - costBasisBaseSplit

                                                                    if debug:
                                                                        if iSplitAcctArray == 0:
                                                                            myPrint("D", _THIS_EXTRACT_NAME + "Values found (local, base, cb, gain): ", balance, balanceBase, costBasisBase, gainBase)
                                                                        if lSplitSecuritiesByAccount:
                                                                            myPrint("D", _THIS_EXTRACT_NAME + "Split Values found (qty, local, base, cb, gain): ", qtySplit, balanceSplit, balanceBaseSplit, costBasisBaseSplit, gainBaseSplit)

                                                                    if not lSplitSecuritiesByAccount:
                                                                        break

                                                                    # If you're confused, these are the accounts within a security
                                                                    entry = []
                                                                    entry.append(curr.getTickerSymbol())                                                                # c0
                                                                    entry.append(curr.getName())                                                                        # c1
                                                                    entry.append(curr.formatSemiFancy(qtySplit, GlobalVars.decimalCharSep))                             # c2
                                                                    entry.append(self.myNumberFormatter(price, False, self.currXrate, _baseCurrency, _roundPrice))       # c3
                                                                    entry.append(self.currXrate.getIDString())                                                          # c4
                                                                    x = None
                                                                    if securityIsBase:
                                                                        entry.append(None)                                                                              # c5 - don't bother displaying if base curr
                                                                    else:
                                                                        self.lRemoveCurrColumn = False
                                                                        entry.append(self.myNumberFormatter(balanceSplit, False, self.currXrate, _baseCurrency, 2))      # Local Curr Value
                                                                        x = round(balanceSplit, 2)
                                                                    entry.append(self.myNumberFormatter(balanceBaseSplit, True, self.currXrate, _baseCurrency, 2))       # Value Base Currency
                                                                    entry.append(self.myNumberFormatter(costBasisBaseSplit, True, self.currXrate, _baseCurrency, 2))     # Cost Basis
                                                                    entry.append(self.myNumberFormatter(gainBaseSplit, True, self.currXrate, _baseCurrency, 2))          # Gain

                                                                    try: entry.append(round(gainBaseSplit / costBasisBaseSplit, 3))
                                                                    except ZeroDivisionError: entry.append(0.0)

                                                                    entry.append(split_acct_array[iSplitAcctArray][0].replace(acctSeparator, "",1))                     # Acct
                                                                    entry.append(curr.getDoubleValue(qtySplit))                                                         # _Shrs
                                                                    entry.append(price)                                                                                 # _Price = raw number
                                                                    entry.append(x)                                                                                     # _CValue
                                                                    entry.append(round(balanceBaseSplit, 2))                                                            # _BValue
                                                                    entry.append(costBasisBaseSplit)                                                                    # _Cost Basis
                                                                    entry.append(gainBaseSplit)                                                                         # _Gain
                                                                    entry.append(curr.getName().upper() + "000" + split_acct_array[iSplitAcctArray][0].upper().replace(acctSeparator, "", 1))  # _SORT
                                                                    entry.append(False)                                                                                 # Never exclude
                                                                    GlobalVars.rawDataTable_sg2020.append(entry)
                                                                # NEXT

                                                                # Now add the main total line for the security.....
                                                                if lSplitSecuritiesByAccount:
                                                                    blankEntry = []
                                                                    blankEntry.append("----------")
                                                                    blankEntry.append(None)
                                                                    blankEntry.append("----------")
                                                                    blankEntry.append(None)
                                                                    blankEntry.append(None)
                                                                    blankEntry.append(None)
                                                                    blankEntry.append("----------")
                                                                    blankEntry.append("----------")
                                                                    blankEntry.append("----------")
                                                                    blankEntry.append(None)
                                                                    blankEntry.append(None)
                                                                    blankEntry.append("----------")
                                                                    blankEntry.append(None)
                                                                    blankEntry.append(None)
                                                                    blankEntry.append("----------")
                                                                    blankEntry.append("----------")
                                                                    blankEntry.append("----------")
                                                                    blankEntry.append(curr.getName().upper() + "555")
                                                                    blankEntry.append(lExcludeTotalsFromCSV)
                                                                    GlobalVars.rawDataTable_sg2020.append(blankEntry)

                                                                entry = []
                                                                if lSplitSecuritiesByAccount:
                                                                    entry.append("totals: " + curr.getTickerSymbol())                                           # c0
                                                                else:
                                                                    entry.append(curr.getTickerSymbol())                                                        # c0
                                                                entry.append(curr.getName())                                                                    # c1
                                                                entry.append(curr.formatSemiFancy(qty, GlobalVars.decimalCharSep))                              # c2
                                                                entry.append(self.myNumberFormatter(price, False, self.currXrate, _baseCurrency, _roundPrice))   # c3
                                                                entry.append(self.currXrate.getIDString())                                                      # c4
                                                                x = None
                                                                if securityIsBase:                                                                              # noqa
                                                                    entry.append(None)                                                                          # c5 - don't bother displaying if base curr
                                                                else:
                                                                    self.lRemoveCurrColumn = False
                                                                    entry.append(self.myNumberFormatter(balance, False, self.currXrate, _baseCurrency,2))        # noqa
                                                                    x = round(balance, 2)

                                                                entry.append(self.myNumberFormatter(balanceBase, True, self.currXrate, _baseCurrency,2))         # noqa
                                                                entry.append(self.myNumberFormatter(costBasisBase, True, self.currXrate, _baseCurrency,2)) ;     # noqa
                                                                entry.append(self.myNumberFormatter(gainBase, True, self.currXrate, _baseCurrency,2))            # noqa

                                                                try: entry.append(round(gainBase / costBasisBase, 3))
                                                                except ZeroDivisionError: entry.append(0.0)

                                                                buildAcctString = ""
                                                                for iIterateAccts in range(0, len(split_acct_array)):
                                                                    buildAcctString += split_acct_array[iIterateAccts][0]
                                                                buildAcctString = buildAcctString[:-len(acctSeparator)]
                                                                entry.append(buildAcctString)                                                                   # Acct
                                                                entry.append(curr.getDoubleValue(qty))                                                          # _Shrs = (raw number)
                                                                entry.append(price)                                                                             # _Price = (raw number)
                                                                entry.append(x)                                                                                 # _CValue =  (raw number)
                                                                entry.append(round(balanceBase, 2))                                                             # _BValue =  (raw number)
                                                                entry.append(costBasisBase)                                                                     # _Cost Basis
                                                                entry.append(gainBase)                                                                          # _Gain
                                                                entry.append(curr.getName().upper() + "888")                                                    # _SORT
                                                                entry.append((False if (not lSplitSecuritiesByAccount) else lExcludeTotalsFromCSV))
                                                                GlobalVars.rawDataTable_sg2020.append(entry)

                                                                if lSplitSecuritiesByAccount:
                                                                    blankEntry = []
                                                                    blankEntry.append("          ")
                                                                    blankEntry.append(None)
                                                                    blankEntry.append(None)
                                                                    blankEntry.append(None)
                                                                    blankEntry.append(None)
                                                                    blankEntry.append(None)
                                                                    blankEntry.append("          ")
                                                                    blankEntry.append("          ")
                                                                    blankEntry.append("          ")
                                                                    blankEntry.append(None)
                                                                    blankEntry.append(None)
                                                                    blankEntry.append(None)
                                                                    blankEntry.append(None)
                                                                    blankEntry.append(None)
                                                                    blankEntry.append(None)
                                                                    blankEntry.append(None)
                                                                    blankEntry.append(None)
                                                                    blankEntry.append(curr.getName().upper() + "999")
                                                                    blankEntry.append(lExcludeTotalsFromCSV)
                                                                    GlobalVars.rawDataTable_sg2020.append(blankEntry)

                                                                self.totalBalance += round(balance, 2)                              # You can round here if you like....
                                                                self.totalBalanceBase += round(balanceBase, 2)                      # You can round here if you like....

                                                                self.totalCostBasisBase += costBasisBase
                                                                self.totalGainBase += gainBase

                                                                # if lIncludeCashBalances:
                                                                #     cash = 0.0                                                    # noqa
                                                                #     # Search to see if Account exists/has been used already for Cash Balance - Only use once!
                                                                #     acct_string = ""
                                                                #     for keys in self.CashBalancesTable.keys():
                                                                #         data = self.CashBalancesTable.get(keys)
                                                                #         acct_array = self.AccountsTable.get(curr)
                                                                #         for iArray in range(0, len(acct_array)):
                                                                #             acct_string += acct_array[iArray][0]  # The account name
                                                                #         # NEXT
                                                                #         if (keys + acctSeparator) in acct_string:
                                                                #             myPrint("D", _THIS_EXTRACT_NAME + "CashBal Search - Found:", keys, "in", self.AccountsTable.get(curr)f, "Cash Bal:", data)
                                                                #             cash = data
                                                                #             self.CashBalancesTable[keys] = 0.0  # Now delete it so it cannot be used again!
                                                                #             self.totalCashBalanceBase = self.totalCashBalanceBase + cash
                                                                #             self.CashBalanceTableData.append([keys, cash])
                                                                #             continue
                                                                #             # Keep searching as a Security may be used in many accounts...
                                                            else:
                                                                myPrint("D", _THIS_EXTRACT_NAME + "Skipping non Filtered Security/Ticker:", curr, curr.getTickerSymbol())
                                                        else:
                                                            myPrint("D", _THIS_EXTRACT_NAME + "Skipping Security with 0 shares..: ", curr, curr.getTickerSymbol(),
                                                                    " Curr: ", curr.getRelativeCurrency().getIDString(), " Price: ", price, " Qty: ", curr.formatSemiFancy(qty, GlobalVars.decimalCharSep))
                                                    else:
                                                        myPrint("D", _THIS_EXTRACT_NAME + "Skipping non Filtered Security/Currency:", curr, curr.getTickerSymbol(), curr.getRelativeCurrency().getIDString())
                                                elif curr.getHideInUI() and curr.getCurrencyType() == CurrencyType.Type.SECURITY:
                                                    myPrint("D", _THIS_EXTRACT_NAME + "Skipping Hidden(inUI) Security..: ", curr, curr.getTickerSymbol(), " Curr: ", curr.getRelativeCurrency().getIDString())

                                                else:
                                                    myPrint("D", _THIS_EXTRACT_NAME + "Skipping non Security:", curr, curr.getTickerSymbol())


                                            # OK, throw in any extra cash balances
                                            if lIncludeCashBalances:
                                                for acct in self.moreCashBalanceAccounts.keys():
                                                    data = self.moreCashBalanceAccounts.get(acct)
                                                    myPrint("D", _THIS_EXTRACT_NAME + "Extra CashBal Search - Found:", acct, "Cash Bal:", data)
                                                    cash = data
                                                    self.totalCashBalanceBase += cash
                                                    self.CashBalanceTableData.append([acct, cash])
                                                    continue
                                                    # Keep searching as a Security may be used in many accounts...

                                            if lSplitSecuritiesByAccount:
                                                GlobalVars.rawDataTable_sg2020 = sorted(GlobalVars.rawDataTable_sg2020, key=lambda _x: (_x[_SORT]))
                                            # else:
                                            #     GlobalVars.rawDataTable_sg2020 = sorted(GlobalVars.rawDataTable_sg2020, key=lambda _x: (_x[1]) )

                                            return DefaultTableModel(GlobalVars.rawDataTable_sg2020, self.columnNames)

                                        def generateFooterTableModel(self):
                                            global lIncludeCashBalances

                                            _baseCurrency = MD_REF.getCurrentAccountBook().getCurrencies().getBaseType()

                                            GlobalVars.rawFooterTable_sg2020 = []
                                            if self.getTableModel() is None: return None

                                            myPrint("D", _THIS_EXTRACT_NAME + "In ", inspect.currentframe().f_code.co_name, "()")
                                            myPrint("D", _THIS_EXTRACT_NAME + "Generating the footer table data....")

                                            blankEntry = []
                                            blankEntry.append("==========")
                                            blankEntry.append(None)
                                            blankEntry.append(None)
                                            blankEntry.append(None)
                                            blankEntry.append(None)
                                            blankEntry.append(None)
                                            blankEntry.append("==========")
                                            blankEntry.append("==========")
                                            blankEntry.append("==========")
                                            blankEntry.append(None)
                                            blankEntry.append(None)
                                            blankEntry.append(None)
                                            blankEntry.append(None)
                                            blankEntry.append(None)
                                            blankEntry.append(None)
                                            blankEntry.append(None)
                                            blankEntry.append(None)
                                            blankEntry.append(None)
                                            blankEntry.append(lExcludeTotalsFromCSV)

                                            entry = []
                                            entry.append("Total: Securities")
                                            entry.append(None)
                                            entry.append(None)
                                            entry.append(None)
                                            entry.append(None)
                                            x = None
                                            if self.allOneCurrency and (self.currXrate != _baseCurrency):
                                                myPrint("D", _THIS_EXTRACT_NAME + "getFooterModel: sameCurrency=", self.currXrate)
                                                if self.currXrate is None:
                                                    entry.append(None)
                                                else:
                                                    x = self.totalBalance
                                                    entry.append(self.myNumberFormatter(self.totalBalance, False, self.currXrate, _baseCurrency, 2))
                                            else:
                                                myPrint("D", _THIS_EXTRACT_NAME + "getFooterModel: was not allOneCurrency..")
                                                entry.append(None)
                                            entry.append(self.myNumberFormatter(self.totalBalanceBase, True, _baseCurrency, _baseCurrency, 2))
                                            entry.append(self.myNumberFormatter(self.totalCostBasisBase, True, _baseCurrency, _baseCurrency,2))  # Cost Basis
                                            entry.append(self.myNumberFormatter(self.totalGainBase, True, _baseCurrency, _baseCurrency, 2))  # Gain

                                            try: entry.append(round(self.totalGainBase / self.totalCostBasisBase, 3))
                                            except ZeroDivisionError: entry.append(0.0)

                                            entry.append("<<" + _baseCurrency.getIDString())
                                            entry.append(None)
                                            entry.append(None)
                                            entry.append(x)
                                            entry.append(self.totalBalanceBase)
                                            entry.append(self.totalCostBasisBase)  # _Cost Basis
                                            entry.append(self.totalGainBase)  # _Gain
                                            entry.append(None)
                                            entry.append(lExcludeTotalsFromCSV)

                                            GlobalVars.rawFooterTable_sg2020.append(entry)

                                            if lIncludeCashBalances:
                                                GlobalVars.rawFooterTable_sg2020.append(blankEntry)
                                                for _iii in range(0, len(self.CashBalanceTableData)):
                                                    if self.CashBalanceTableData[_iii][1] != 0:
                                                        entry = []
                                                        entry.append("Cash Bal/Acct:")
                                                        entry.append(None)
                                                        entry.append(None)
                                                        entry.append(None)
                                                        entry.append(None)
                                                        entry.append(None)
                                                        entry.append(self.myNumberFormatter(self.CashBalanceTableData[_iii][1], True, _baseCurrency, _baseCurrency, 2))
                                                        entry.append(None)
                                                        entry.append(None)
                                                        entry.append(None)
                                                        entry.append(self.CashBalanceTableData[_iii][0].getAccountName())
                                                        entry.append(None)  # Cost Basis
                                                        entry.append(None)  # Gain
                                                        entry.append(None)
                                                        entry.append(self.CashBalanceTableData[_iii][1])
                                                        entry.append(None)  # _Cost Basis
                                                        entry.append(None)  # _Gain
                                                        entry.append(None)
                                                        entry.append(False)  # Always include
                                                        GlobalVars.rawFooterTable_sg2020.append(entry)

                                                GlobalVars.rawFooterTable_sg2020.append(blankEntry)
                                                entry = []
                                                entry.append("Cash Bal TOTAL:")
                                                entry.append(None)
                                                entry.append(None)
                                                entry.append(None)
                                                entry.append(None)
                                                entry.append(None)
                                                entry.append(self.myNumberFormatter(self.totalCashBalanceBase, True, _baseCurrency, _baseCurrency, 2))
                                                entry.append(None)
                                                entry.append(None)
                                                entry.append(None)
                                                entry.append("** Across ALL Accounts **")
                                                entry.append(None)
                                                entry.append(None)
                                                entry.append(None)
                                                entry.append(self.totalCashBalanceBase)
                                                entry.append(None)
                                                entry.append(None)
                                                entry.append(None)
                                                entry.append(lExcludeTotalsFromCSV)
                                                GlobalVars.rawFooterTable_sg2020.append(entry)

                                                # I was limiting this total to only where no Security filters - but hey it's up to the user to know their data....
                                                if True or lAllSecurity:  # I don't add them up if selecting one security - probably makes the overal total wrong if multi securities in an account etc...
                                                    GlobalVars.rawFooterTable_sg2020.append(blankEntry)
                                                    entry = []
                                                    entry.append("TOTAL Securities+Cash Bal:")
                                                    entry.append(None)
                                                    entry.append(None)
                                                    entry.append(None)
                                                    entry.append(None)
                                                    entry.append(None)
                                                    entry.append(self.myNumberFormatter((self.totalBalanceBase + self.totalCashBalanceBase), True, _baseCurrency, _baseCurrency, 2))
                                                    entry.append(self.myNumberFormatter(self.totalCostBasisBase, True, _baseCurrency, _baseCurrency, 2))  # Cost Basis
                                                    entry.append(self.myNumberFormatter(self.totalGainBase, True, _baseCurrency, _baseCurrency, 2))  # Gain

                                                    try: entry.append(round(self.totalGainBase / self.totalCostBasisBase, 3))
                                                    except ZeroDivisionError: entry.append(0.0)

                                                    entry.append("Only valid where whole accounts selected!")
                                                    entry.append(None)
                                                    entry.append(None)
                                                    entry.append(None)
                                                    entry.append((self.totalBalanceBase + self.totalCashBalanceBase))
                                                    entry.append(self.totalCostBasisBase)  # _Cost Basis
                                                    entry.append(self.totalGainBase)  # _Gain
                                                    entry.append(None)
                                                    entry.append(lExcludeTotalsFromCSV)
                                                    GlobalVars.rawFooterTable_sg2020.append(entry)

                                            return DefaultTableModel(GlobalVars.rawFooterTable_sg2020, self.columnNames)

                                        # Render a currency with given number of fractional digits. NaN or null is an empty cell.
                                        # noinspection PyMethodMayBeStatic
                                        def myNumberFormatter(self, theNumber, useBase, exchangeCurr, baseCurr, noDecimals):
                                            noDecimalFormatter = NumberFormat.getNumberInstance()
                                            noDecimalFormatter.setMinimumFractionDigits(0)
                                            noDecimalFormatter.setMaximumFractionDigits(noDecimals)

                                            if noDecimals == 2: noDecimalFormatter.setMinimumFractionDigits(2)

                                            if theNumber is None or Double.isNaN(float(theNumber)): return ""

                                            # if Math.abs(float(theNumber)) < 0.01: theNumber = 0L

                                            if useBase:
                                                if noDecimals == 0:
                                                    # MD format functions can't print comma-separated values without a decimal point so
                                                    # we have to do it ourselves
                                                    theNumber = baseCurr.getPrefix() + " " + noDecimalFormatter.format(float(theNumber)) + baseCurr.getSuffix()
                                                else:
                                                    theNumber = baseCurr.getPrefix() + " " + noDecimalFormatter.format(float(theNumber)) + baseCurr.getSuffix()
                                                    # theNumber = baseCurr.formatFancy(baseCurr.getLongValue(float(theNumber)), decimalSeparator)
                                            else:
                                                if noDecimals == 0:
                                                    # MD format functions can't print comma-separated values without a decimal point so
                                                    # we have to do it ourselves
                                                    theNumber = exchangeCurr.getPrefix() + " " + noDecimalFormatter.format(float(theNumber)) + exchangeCurr.getSuffix()
                                                else:
                                                    theNumber = exchangeCurr.getPrefix() + " " + noDecimalFormatter.format(float(theNumber)) + exchangeCurr.getSuffix()
                                                    # theNumber = exchangeCurr.formatFancy(exchangeCurr.getLongValue(float(theNumber)), decimalSeparator)

                                            return theNumber

                                        # noinspection PyArgumentList
                                        class MyAcctFilterSG2020(AcctFilter):

                                            def __init__(self, selectAccountType="ALL",                                             # noqa
                                                         hideInactiveAccounts=True,                                                 # noqa
                                                         lAllAccounts=True,                                                         # noqa
                                                         filterForAccounts="ALL",                                                   # noqa
                                                         hideHiddenAccounts=True,                                                   # noqa
                                                         hideHiddenSecurities=True,                                                 # noqa
                                                         lAllCurrency=True,                                                         # noqa
                                                         filterForCurrency="ALL",                                                   # noqa
                                                         lAllSecurity=True,                                                         # noqa
                                                         filterForSecurity="ALL",                                                   # noqa
                                                         findUUID=None):                                                            # noqa
                                                super(AcctFilter, self).__init__()

                                                # noinspection PyUnresolvedReferences
                                                if selectAccountType == "ALL":                                  pass
                                                elif selectAccountType == "CAT":                                pass
                                                elif selectAccountType == "NONCAT":                             pass
                                                elif selectAccountType == Account.AccountType.ROOT:             pass
                                                elif selectAccountType == Account.AccountType.BANK:             pass
                                                elif selectAccountType == Account.AccountType.CREDIT_CARD:      pass
                                                elif selectAccountType == Account.AccountType.INVESTMENT:       pass
                                                elif selectAccountType == Account.AccountType.SECURITY:         pass
                                                elif selectAccountType == Account.AccountType.ASSET:            pass
                                                elif selectAccountType == Account.AccountType.LIABILITY:        pass
                                                elif selectAccountType == Account.AccountType.LOAN:             pass
                                                elif selectAccountType == Account.AccountType.EXPENSE:          pass
                                                elif selectAccountType == Account.AccountType.INCOME:           pass
                                                else:   selectAccountType = "ALL"

                                                self.selectAccountType = selectAccountType
                                                self.hideInactiveAccounts = hideInactiveAccounts
                                                self.lAllAccounts = lAllAccounts
                                                self.filterForAccounts = filterForAccounts
                                                self.hideHiddenAccounts = hideHiddenAccounts
                                                self.hideHiddenSecurities = hideHiddenSecurities
                                                self.lAllCurrency = lAllCurrency
                                                self.filterForCurrency = filterForCurrency
                                                self.lAllSecurity = lAllSecurity
                                                self.filterForSecurity = filterForSecurity
                                                self.findUUID = findUUID

                                            def matches(self, acct):
                                                if self.findUUID is not None:  # If UUID supplied, override all other parameters...
                                                    if acct.getUUID() == self.findUUID: return True
                                                    else: return False

                                                # noinspection PyUnresolvedReferences
                                                if self.selectAccountType == "ALL" or acct.getAccountType() == self.selectAccountType: pass
                                                elif self.selectAccountType == "CAT" and (
                                                        acct.getAccountType() == Account.AccountType.EXPENSE or acct.getAccountType() == Account.AccountType.INCOME): pass
                                                elif self.selectAccountType == "NONCAT" and not (
                                                        acct.getAccountType() == Account.AccountType.EXPENSE or acct.getAccountType() == Account.AccountType.INCOME): pass
                                                else: return False

                                                if self.hideInactiveAccounts:
                                                    # This logic replicates Moneydance AcctFilter.ACTIVE_ACCOUNTS_FILTER
                                                    if (acct.getAccountOrParentIsInactive()): return False
                                                    if (acct.getHideOnHomePage() and acct.getBalance() == 0): return False

                                                # noinspection PyUnresolvedReferences
                                                if acct.getAccountType() == Account.AccountType.SECURITY:
                                                    theAcct = acct.getParentAccount()  # Security Accounts are sub-accounts of Investment Accounts - so take the Parent
                                                else:
                                                    theAcct = acct

                                                if self.lAllAccounts or (
                                                        self.filterForAccounts.upper().strip() in theAcct.getFullAccountName().upper().strip()): pass
                                                else: return False

                                                if ((not self.hideHiddenAccounts) or (
                                                        self.hideHiddenAccounts and not theAcct.getHideOnHomePage())):  pass
                                                else: return False

                                                curr = acct.getCurrencyType()
                                                currID = curr.getIDString()
                                                currName = curr.getName()

                                                # noinspection PyUnresolvedReferences
                                                if acct.getAccountType() == Account.AccountType.SECURITY:  # on Security Accounts, get the Currency from the Security master - else from the account)
                                                    if self.lAllSecurity:
                                                        pass
                                                    elif (self.filterForSecurity.upper().strip() in curr.getTickerSymbol().upper().strip()):
                                                        pass
                                                    elif (self.filterForSecurity.upper().strip() in curr.getName().upper().strip()):
                                                        pass
                                                    else: return False

                                                    if ((self.hideHiddenSecurities and not curr.getHideInUI()) or (not self.hideHiddenSecurities)):
                                                        pass
                                                    else:
                                                        return False

                                                    currID = curr.getRelativeCurrency().getIDString()
                                                    currName = curr.getRelativeCurrency().getName()

                                                else: pass

                                                # All accounts and security records can have currencies
                                                if self.lAllCurrency:
                                                    pass
                                                elif (self.filterForCurrency.upper().strip() in currID.upper().strip()):
                                                    pass
                                                elif (self.filterForCurrency.upper().strip() in currName.upper().strip()):
                                                    pass

                                                else: return False

                                                # Phew! We made it....
                                                return True

                                        def sumInfoBySecurity(self, book):
                                            global hideInactiveAccounts, hideHiddenAccounts, lAllAccounts, filterForAccounts, lIncludeCashBalances
                                            global lSplitSecuritiesByAccount, acctSeparator, lIncludeFutureBalances_SG2020

                                            myPrint("D", _THIS_EXTRACT_NAME + "In ", inspect.currentframe().f_code.co_name, "()")

                                            base = MD_REF.getCurrentAccountBook().getCurrencies().getBaseType()

                                            totals = {}  # Dictionary <CurrencyType, Long>
                                            accounts = {}
                                            cashTotals = {}  # Dictionary<CurrencyType, Long>
                                            cbbasistotals = {}

                                            lDidIFindAny = False

                                            # So this little bit is going to find the other accounts that have a cash balance...
                                            if lIncludeCashBalances:
                                                # noinspection PyUnresolvedReferences
                                                moreCashAccounts = AccountUtil.allMatchesForSearch(book,self.MyAcctFilterSG2020(Account.AccountType.INVESTMENT,
                                                                                                                                hideInactiveAccounts,
                                                                                                                                lAllAccounts,
                                                                                                                                filterForAccounts,
                                                                                                                                hideHiddenAccounts,
                                                                                                                                hideHiddenSecurities,
                                                                                                                                lAllCurrency,
                                                                                                                                filterForCurrency,
                                                                                                                                lAllSecurity,
                                                                                                                                filterForSecurity,
                                                                                                                                None))
                                                for acct in moreCashAccounts:
                                                    curr = acct.getCurrencyType()

                                                    if lIncludeFutureBalances_SG2020:
                                                        cashTotal = curr.getDoubleValue((acct.getBalance())) / curr.getRate(None)
                                                    else:
                                                        cashTotal = curr.getDoubleValue((acct.getCurrentBalance())) / curr.getRate(None)
                                                    myPrint("D", _THIS_EXTRACT_NAME + "Cash balance for extra accounts searched:", cashTotal)

                                                    if cashTotal != 0:
                                                        self.moreCashBalanceAccounts[acct] = round(cashTotal,2)


                                            # noinspection PyUnresolvedReferences
                                            for acct in AccountUtil.allMatchesForSearch(book, self.MyAcctFilterSG2020(Account.AccountType.SECURITY,
                                                                                                                    hideInactiveAccounts,
                                                                                                                    lAllAccounts,
                                                                                                                    filterForAccounts,
                                                                                                                    hideHiddenAccounts,
                                                                                                                    hideHiddenSecurities,
                                                                                                                    lAllCurrency,
                                                                                                                    filterForCurrency,
                                                                                                                    lAllSecurity,
                                                                                                                    filterForSecurity,
                                                                                                                    None)):
                                                curr = acct.getCurrencyType()
                                                account = accounts.get(curr)    # this returns None if curr doesn't exist yet
                                                total = totals.get(curr)        # this returns None if security/curr doesn't exist yet
                                                costbasis = cbbasistotals.get(curr)

                                                if lIncludeFutureBalances_SG2020:
                                                    _getBalance = acct.getBalance()
                                                else:
                                                    _getBalance = acct.getCurrentBalance()

                                                if _getBalance != 0:  # we only want Securities with holdings
                                                    if debug and not GlobalVars.i_am_an_extension_so_run_headless: print("Processing Acct:", acct.getParentAccount(), "Share/Fund Qty Balances for Security: ", curr, curr.formatSemiFancy(
                                                        _getBalance, GlobalVars.decimalCharSep), " Shares/Units")

                                                    total = (0L if (total is None) else total) + _getBalance
                                                    totals[curr] = total

                                                    # getTheCostBasis = InvestUtil.getCostBasis(acct)
                                                    getTheCostBasis = CurrencyUtil.convertValue(InvestUtil.getCostBasis(acct), acct.getParentAccount().getCurrencyType(), base)
                                                    costbasis = (0L if (costbasis is None) else costbasis) + getTheCostBasis
                                                    cbbasistotals[curr] = costbasis

                                                    lDidIFindAny = True

                                                    if lSplitSecuritiesByAccount:  # Build a mini table if split, else 1 row table...
                                                        if account is None:
                                                            accounts[curr] = [[acct.getParentAccount().getAccountName() + acctSeparator, _getBalance, getTheCostBasis]]
                                                        else:
                                                            account.append([acct.getParentAccount().getAccountName() + acctSeparator, _getBalance, getTheCostBasis])
                                                            accounts[curr] = account
                                                    else:
                                                        if account is None:
                                                            account = acct.getParentAccount().getAccountName() + acctSeparator  # Important - keep the trailing ' :'
                                                        else:
                                                            account = account[0][0] + acct.getParentAccount().getAccountName() + acctSeparator  # concatenate two strings here
                                                        accounts[curr] = [[account, _getBalance, getTheCostBasis]]

                                                # if lIncludeCashBalances:
                                                #
                                                #     # If we found cash balance for the security parent, then delete it from the other list...
                                                #     self.moreCashBalanceAccounts.pop(acct.getParentAccount(),None)
                                                #
                                                #     # Now get the Currency  for the Security Parent Account - to get Cash  Balance
                                                #     curr = acct.getParentAccount().getCurrencyType()
                                                #
                                                #     # WARNING Cash balances are by Account and not by Security!
                                                #     if lIncludeFutureBalances_SG2020:
                                                #         cashTotal = curr.getDoubleValue((acct.getParentAccount().getBalance())) / curr.getRate(None)  # Will be the same Cash balance per account for all Securities..
                                                #     else:
                                                #         cashTotal = curr.getDoubleValue((acct.getParentAccount().getCurrentBalance())) / curr.getRate(None)  # Will be the same Cash balance per account for all Securities..
                                                #     myPrint("D", _THIS_EXTRACT_NAME + "Cash balance for account:", cashTotal)
                                                #     cashTotals[acct.getParentAccount()] = round(cashTotal, 2)

                                            self.QtyOfSharesTable = totals
                                            self.AccountsTable = accounts
                                            self.CashBalancesTable = cashTotals
                                            self.CostBasisTotals = cbbasistotals

                                            return lDidIFindAny

                                        class MyJTable(JTable):  # (JTable)
                                            myPrint("D", _THIS_EXTRACT_NAME + "In ", inspect.currentframe().f_code.co_name, "()")
                                            lInTheFooter = False

                                            def __init__(self, tableModel, lSortTheTable, lInTheFooter):
                                                super(JTable, self).__init__(tableModel)
                                                self.lInTheFooter = lInTheFooter
                                                if lSortTheTable: self.fixTheRowSorter()

                                            def isCellEditable(self, row, column):                                                  # noqa
                                                return False

                                            #  Rendering depends on row (i.e. security's currency) as well as column
                                            # noinspection PyUnusedLocal
                                            def getCellRenderer(self, row, column):                                                 # noqa
                                                renderer = None

                                                if GlobalVars.stockGlanceInstance.columnTypes[column] == "Text":
                                                    renderer = DefaultTableCellRenderer()
                                                    renderer.setHorizontalAlignment(JLabel.LEFT)
                                                elif GlobalVars.stockGlanceInstance.columnTypes[column] == "TextNumber":
                                                    renderer = GlobalVars.stockGlanceInstance.MyGainsRenderer()
                                                    renderer.setHorizontalAlignment(JLabel.RIGHT)
                                                elif GlobalVars.stockGlanceInstance.columnTypes[column] == "%":
                                                    renderer = GlobalVars.stockGlanceInstance.MyPercentRenderer()
                                                    renderer.setHorizontalAlignment(JLabel.RIGHT)
                                                elif GlobalVars.stockGlanceInstance.columnTypes[column] == "TextC":
                                                    renderer = DefaultTableCellRenderer()
                                                    renderer.setHorizontalAlignment(JLabel.CENTER)
                                                else:
                                                    renderer = DefaultTableCellRenderer()

                                                renderer.setVerticalAlignment(JLabel.CENTER)

                                                return renderer

                                            class MyTextNumberComparator(Comparator):
                                                lSortNumber = False
                                                lSortRealNumber = False

                                                def __init__(self, sortType):
                                                    if sortType == "N":
                                                        self.lSortNumber = True
                                                    elif sortType == "%":
                                                        self.lSortRealNumber = True
                                                    else:
                                                        self.lSortNumber = False

                                                def compare(self, str1, str2):
                                                    validString = "-0123456789" + GlobalVars.decimalCharSep  # Yes this will strip % sign too, but that still works
                                                    if self.lSortNumber:
                                                        # strip non numerics from string so can convert back to float - yes, a bit of a reverse hack
                                                        conv_string1 = ""
                                                        if str1 is None or str1 == "": str1 = "0"
                                                        if str2 is None or str2 == "": str2 = "0"
                                                        for char in str1:
                                                            if char in validString:
                                                                conv_string1 = conv_string1 + char

                                                        conv_string2 = ""
                                                        for char in str2:
                                                            if char in validString:
                                                                conv_string2 = conv_string2 + char
                                                        str1 = float(conv_string1)
                                                        str2 = float(conv_string2)

                                                        if str1 > str2:
                                                            return 1
                                                        elif str1 == str2:
                                                            return 0
                                                        else:
                                                            return -1
                                                    elif self.lSortRealNumber:
                                                        if float(str1) > float(str2):
                                                            return 1
                                                        elif str1 == str2:
                                                            return 0
                                                        else:
                                                            return -1
                                                    else:
                                                        if str1.upper() > str2.upper():
                                                            return 1
                                                        elif str1.upper() == str2.upper():
                                                            return 0
                                                        else:
                                                            return -1

                                                # enddef

                                            def fixTheRowSorter(
                                                    self):  # by default everything gets converted to strings. We need to fix this and code for my string number formats
                                                global _SHRS_FORMATTED, _SHRS_RAW, _PRICE_FORMATTED, _PRICE_RAW, _CVALUE_FORMATTED, _CVALUE_RAW, _BVALUE_FORMATTED, _BVALUE_RAW, _SORT
                                                global _CBVALUE_FORMATTED, _CBVALUE_RAW, _GAIN_FORMATTED, _GAIN_RAW, _EXCLUDECSV, _GAINPCT

                                                sorter = TableRowSorter()
                                                self.setRowSorter(sorter)
                                                sorter.setModel(self.getModel())
                                                for _iii in range(0, self.getColumnCount()):
                                                    if _iii == _SHRS_FORMATTED:
                                                        sorter.setComparator(_iii, self.MyTextNumberComparator("N"))
                                                    elif _iii == _PRICE_FORMATTED:
                                                        sorter.setComparator(_iii, self.MyTextNumberComparator("N"))
                                                    elif _iii == _CVALUE_FORMATTED:
                                                        sorter.setComparator(_iii, self.MyTextNumberComparator("N"))
                                                    elif _iii == _BVALUE_FORMATTED:
                                                        sorter.setComparator(_iii, self.MyTextNumberComparator("N"))
                                                    elif _iii == _CBVALUE_FORMATTED:
                                                        sorter.setComparator(_iii, self.MyTextNumberComparator("N"))
                                                    elif _iii == _GAIN_FORMATTED:
                                                        sorter.setComparator(_iii, self.MyTextNumberComparator("N"))
                                                    elif _iii == _SORT:
                                                        sorter.setComparator(_iii, self.MyTextNumberComparator("N"))
                                                    elif _iii == _GAINPCT:
                                                        sorter.setComparator(_iii, self.MyTextNumberComparator("%"))
                                                    else:
                                                        sorter.setComparator(_iii, self.MyTextNumberComparator("T"))
                                                self.getRowSorter().toggleSortOrder(1)

                                            def prepareRenderer(self, renderer, row, column):                                       # noqa
                                                # make Banded rows
                                                global lSplitSecuritiesByAccount

                                                component = super(GlobalVars.stockGlanceInstance.MyJTable, self).prepareRenderer(renderer, row, column)    # noqa
                                                if not self.isRowSelected(row):
                                                    if (self.lInTheFooter):
                                                        component.setBackground(MD_REF.getUI().getColors().registerBG1 if row % 2 == 0 else MD_REF.getUI().getColors().registerBG2)
                                                        if "total" in str(self.getValueAt(row, 0)).lower():
                                                            component.setForeground(MD_REF.getUI().getColors().headerFG)
                                                            component.setBackground(MD_REF.getUI().getColors().headerBG1)
                                                            component.setFont(component.getFont().deriveFont(Font.BOLD))
                                                    elif (not lSplitSecuritiesByAccount):
                                                        component.setBackground(MD_REF.getUI().getColors().registerBG1 if row % 2 == 0 else MD_REF.getUI().getColors().registerBG2)
                                                    elif str(self.getValueAt(row, 0)).lower()[:5] == "total":
                                                        component.setBackground(MD_REF.getUI().getColors().registerBG1)
                                                return component

                                        # This copies the standard class and just changes the colour to RED if it detects a negative - leaves field intact
                                        # noinspection PyArgumentList
                                        class MyGainsRenderer(DefaultTableCellRenderer):

                                            def __init__(self):
                                                super(DefaultTableCellRenderer, self).__init__()

                                            def setValue(self, value):
                                                validString = "-0123456789" + GlobalVars.decimalCharSep

                                                self.setText(value)

                                                if (value is None
                                                        or value.strip() == ""
                                                        or "==" in value
                                                        or "--" in value):
                                                    return

                                                # strip non numerics from string so can convert back to float - yes, a bit of a reverse hack
                                                conv_string1 = ""
                                                for char in value:
                                                    if char in validString:
                                                        conv_string1 = conv_string1 + char
                                                try:
                                                    str1 = float(conv_string1)
                                                    if float(str1) < 0.0:
                                                        self.setForeground(MD_REF.getUI().getColors().budgetAlertColor)
                                                    else:
                                                        self.setForeground(MD_REF.getUI().getColors().defaultTextForeground)
                                                except:
                                                    # No real harm done; so move on.... (was failing on 'Fr. 305.2' - double point in text)
                                                    self.setForeground(MD_REF.getUI().getColors().defaultTextForeground)

                                        # This copies the standard class and just changes the colour to RED if it detects a negative - and formats as %
                                        # noinspection PyArgumentList
                                        class MyPercentRenderer(DefaultTableCellRenderer):

                                            def __init__(self):
                                                super(DefaultTableCellRenderer, self).__init__()

                                            def setValue(self, value):
                                                if value is None: return

                                                self.setText("{:.1%}".format(value))

                                                if value < 0.0:
                                                    self.setForeground(MD_REF.getUI().getColors().budgetAlertColor)
                                                else:
                                                    self.setForeground(MD_REF.getUI().getColors().defaultTextForeground)

                                        # Synchronises column widths of both JTables
                                        class ColumnChangeListener(TableColumnModelListener):
                                            sourceTable = None
                                            targetTable = None

                                            def __init__(self, source, target):
                                                self.sourceTable = source
                                                self.targetTable = target

                                            def columnAdded(self, evt): pass

                                            def columnSelectionChanged(self, evt): pass

                                            def columnRemoved(self, evt): pass

                                            def columnMoved(self, evt): pass

                                            # noinspection PyUnusedLocal
                                            def columnMarginChanged(self, evt):
                                                global _column_widths_SG2020

                                                sourceModel = self.sourceTable.getColumnModel()
                                                targetModel = self.targetTable.getColumnModel()
                                                # listener = map.get(self.targetTable)

                                                # targetModel.removeColumnModelListener(listener)

                                                for _iii in range(0, sourceModel.getColumnCount()):
                                                    targetModel.getColumn(_iii).setPreferredWidth(sourceModel.getColumn(_iii).getWidth())

                                                    # Saving for later... Yummy!!
                                                    _column_widths_SG2020[_iii] = sourceModel.getColumn(_iii).getWidth()
                                                    myPrint("D", _THIS_EXTRACT_NAME + "Saving column %s as width %s for later..." %(_iii,_column_widths_SG2020[_iii]))

                                                # targetModel.addColumnModelListener(listener)
                                            # enddef

                                        # Sync horizontal scroll bars with footer (vertical sync disabled)
                                        class ScrollSynchronizer(AdjustmentListener):
                                            v1 = None
                                            h1 = None
                                            v2 = None
                                            h2 = None

                                            def __init__(self, sp1, sp2):
                                                # self.v1 = sp1.getVerticalScrollBar()
                                                self.h1 = sp1.getHorizontalScrollBar()
                                                # self.v2 = sp2.getVerticalScrollBar()
                                                self.h2 = sp2.getHorizontalScrollBar()

                                            def adjustmentValueChanged(self, evt):
                                                scrollBar = evt.getSource()
                                                value = scrollBar.getValue()
                                                target = None

                                                # if(scrollBar == self.v1): target = self.v2
                                                if (scrollBar == self.h1): target = self.h2
                                                # if(scrollBar == self.v2): target = self.v1
                                                if (scrollBar == self.h2): target = self.h1

                                                if target is not None: target.setValue(value)
                                            # enddef

                                        class WindowListener(WindowAdapter):
                                            def __init__(self, theFrame):
                                                self.theFrame = theFrame                                                # type: MyJFrame

                                            def windowClosing(self, WindowEvent):                                       # noqa
                                                myPrint("DB", _THIS_EXTRACT_NAME + "In ", inspect.currentframe().f_code.co_name, "()")
                                                terminate_script()

                                            def windowClosed(self, WindowEvent):                                        # noqa
                                                myPrint("DB", _THIS_EXTRACT_NAME + "In ", inspect.currentframe().f_code.co_name, "()")
                                                myPrint("DB", _THIS_EXTRACT_NAME + "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

                                                self.theFrame.isActiveInMoneydance = False

                                                myPrint("DB", _THIS_EXTRACT_NAME + "applistener is %s" %(classPrinter("MoneydanceAppListener", self.theFrame.MoneydanceAppListener)))

                                                if self.theFrame.MoneydanceAppListener is not None:
                                                    try:
                                                        MD_REF.removeAppEventListener(self.theFrame.MoneydanceAppListener)
                                                        myPrint("DB", _THIS_EXTRACT_NAME + "\n@@@ Removed my MD App Listener... %s\n" %(classPrinter("MoneydanceAppListener", self.theFrame.MoneydanceAppListener)))
                                                        self.theFrame.MoneydanceAppListener = None
                                                    except:
                                                        myPrint("B", _THIS_EXTRACT_NAME + "FAILED to remove my MD App Listener... %s" %(classPrinter("MoneydanceAppListener", self.theFrame.MoneydanceAppListener)))
                                                        dump_sys_error_to_md_console_and_errorlog()

                                                if self.theFrame.HomePageViewObj is not None:
                                                    self.theFrame.HomePageViewObj.unload()
                                                    myPrint("DB", _THIS_EXTRACT_NAME + "@@ Called HomePageView.unload() and Removed reference to HomePageView %s from MyJFrame()...@@\n" %(classPrinter("HomePageView", self.theFrame.HomePageViewObj)))
                                                    self.theFrame.HomePageViewObj = None

                                                cleanup_actions(self.theFrame)

                                        class CloseAction(AbstractAction):
                                            def actionPerformed(self, event):                                                       # noqa
                                                myPrint("D", _THIS_EXTRACT_NAME + "In ", inspect.currentframe().f_code.co_name, "()")
                                                terminate_script()

                                        class PrintJTable(AbstractAction):
                                            def __init__(self, _frame, _table, _title, _footerTable):
                                                self._frame = _frame
                                                self._table = _table
                                                self._title = _title
                                                self.footerTable = _footerTable

                                            def actionPerformed(self, event):                                                       # noqa
                                                printJTable(_theFrame=self._frame, _theJTable=self._table, _theTitle=self._title, _secondJTable=self.footerTable)

                                        def createAndShowGUI(self):
                                            global lSplitSecuritiesByAccount, _column_widths_SG2020
                                            global lIncludeFutureBalances_SG2020

                                            global _SHRS_FORMATTED, _SHRS_RAW, _PRICE_FORMATTED, _PRICE_RAW, _CVALUE_FORMATTED, _CVALUE_RAW, _BVALUE_FORMATTED, _BVALUE_RAW, _SORT
                                            global _CBVALUE_FORMATTED, _CBVALUE_RAW, _GAIN_FORMATTED, _GAIN_RAW, _EXCLUDECSV, _GAINPCT

                                            myPrint("D", _THIS_EXTRACT_NAME + "In ", inspect.currentframe().f_code.co_name, "()")

                                            if not SwingUtilities.isEventDispatchThread():
                                                myPrint("DB", "Relaunching createAndShowGUI() on the EDT.....")
                                                genericSwingEDTRunner(False, False, self.createAndShowGUI)
                                                return None

                                            self.generateTableModels(MD_REF.getCurrentAccountBook())
                                            if self.getTableModel() is None: return False

                                            if GlobalVars.DISPLAY_DATA:

                                                # JFrame.setDefaultLookAndFeelDecorated(True)   # Note: Darcula Theme doesn't like this and seems to be OK without this statement...

                                                titleExtraTxt = u"" if not isPreviewBuild() else u"<PREVIEW BUILD: %s>" %(version_build)

                                                if not GlobalVars.EXTRACT_DATA:
                                                    extract_data_frame_.setTitle(u"StockGlance2020 - Summarise Stocks/Funds...   %s" %(titleExtraTxt))
                                                else:
                                                    extract_data_frame_.setTitle(u"StockGlance2020 - Summarise Stocks/Funds... (NOTE: your file has already been extracted)   %s" %(titleExtraTxt))

                                                extract_data_frame_.setName(u"%s_main_stockglance2020" %(myModuleID))

                                                if (not Platform.isMac()):
                                                    MD_REF.getUI().getImages()
                                                    extract_data_frame_.setIconImage(MDImages.getImage(MD_REF.getSourceInformation().getIconResource()))

                                                # extract_data_frame_.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE)
                                                extract_data_frame_.setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE)  # The CloseAction() and WindowListener() will handle dispose() - else change back to DISPOSE_ON_CLOSE

                                                shortcut = Toolkit.getDefaultToolkit().getMenuShortcutKeyMaskEx()

                                                # Add standard CMD-W keystrokes etc to close window
                                                extract_data_frame_.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_W, shortcut),  "close-window")
                                                extract_data_frame_.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_F4, shortcut), "close-window")
                                                extract_data_frame_.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_P, shortcut),  "print-me")

                                                if lAllowEscapeExitApp_SWSS:
                                                    extract_data_frame_.getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0), "close-window")

                                                extract_data_frame_.getRootPane().getActionMap().put("close-window", self.CloseAction())

                                                extract_data_frame_.addWindowListener(self.WindowListener(extract_data_frame_))

                                            if lSplitSecuritiesByAccount:
                                                self.table = self.MyJTable(self.tableModel, False,False)  # Creates JTable() with special sorting too
                                            else:
                                                self.table = self.MyJTable(self.tableModel, True,False)  # Creates JTable() with special sorting too

                                            if GlobalVars.DISPLAY_DATA:
                                                screenSize = Toolkit.getDefaultToolkit().getScreenSize()
                                                self.tableHeader = self.table.getTableHeader()                                      # noqa
                                                self.tableHeader.setReorderingAllowed(False)  # no more drag and drop columns, it didn't work (on the footer)
                                                self.table.getTableHeader().setDefaultRenderer(DefaultTableHeaderCellRenderer())

                                                # self.footerModel = self.generateFooterTableModel(()  # Generate/populate the footer table data

                                                # Creates JTable() for footer - with disabled sorting too
                                                self.footerTable = self.MyJTable(self.footerModel, False, True)                     # noqa

                                                extract_data_frame_.getRootPane().getActionMap().put("print-me", self.PrintJTable(extract_data_frame_, self.table, "StockGlance2020", self.footerTable))

                                                fontSize = self.table.getFont().getSize()+5
                                                self.table.setRowHeight(fontSize)
                                                self.table.setRowMargin(0)
                                                myPrint("DB", _THIS_EXTRACT_NAME + "Setting main table row height to %s and intercellspacing to 0" %fontSize)
                                                myPrint("DB", _THIS_EXTRACT_NAME + "\n\t\tTable Font: %s,\n\t\tMD.defaultSystemFont: %s,\n\t\tMD.defaultText: %s,\n\t\tMD.register: %s\n"
                                                        %(self.table.getFont(),
                                                          MD_REF.getUI().getFonts().defaultSystemFont,
                                                          MD_REF.getUI().getFonts().defaultText,
                                                          MD_REF.getUI().getFonts().register))

                                                fontSize = self.footerTable.getFont().getSize()+5
                                                self.footerTable.setRowHeight(fontSize)
                                                self.footerTable.setRowMargin(0)
                                                myPrint("DB", _THIS_EXTRACT_NAME + "Setting footer table row height to %s and intercellspacing to 0" %fontSize)

                                                # Column listeners to resize columns on both tables to keep them in sync
                                                cListener1 = self.ColumnChangeListener(self.table, self.footerTable)
                                                # cListener2=self.ColumnChangeListener(self.footerTable,self.table) # Not using this as footer headers not manually resizable (as hidden)

                                                tcm = self.table.getColumnModel()

                                                myDefaultWidths = [120,300,120,100,80,120,120,120,120,70,350,0,0,0,0,0,0,0,0]

                                                validCount=0
                                                lInvalidate=True
                                                if _column_widths_SG2020 is not None and isinstance(_column_widths_SG2020,(list)) and len(_column_widths_SG2020) == len(myDefaultWidths):
                                                    if sum(_column_widths_SG2020[_SHRS_RAW:])<1:
                                                        for width in _column_widths_SG2020:
                                                            if width >= 0 and width <= 1000:
                                                                validCount += 1

                                                if validCount == len(myDefaultWidths): lInvalidate=False

                                                if lInvalidate:
                                                    myPrint("DB", _THIS_EXTRACT_NAME + "Found invalid saved columns = resetting to defaults")
                                                    myPrint("DB", _THIS_EXTRACT_NAME + "Found: %s" %_column_widths_SG2020)
                                                    myPrint("DB", _THIS_EXTRACT_NAME + "Resetting to: %s" %myDefaultWidths)
                                                    _column_widths_SG2020 = myDefaultWidths
                                                else:
                                                    myPrint("DB", _THIS_EXTRACT_NAME + "Valid column widths loaded - Setting to: %s" %_column_widths_SG2020)
                                                    myDefaultWidths = _column_widths_SG2020

                                                for _iii in range(0, _SHRS_RAW): tcm.getColumn(_iii).setPreferredWidth(myDefaultWidths[_iii])

                                                # I'm hiding these columns for ease of data retrieval. The better option would be to remove the columns
                                                for _iii in reversed(range(_SHRS_RAW, tcm.getColumnCount())):
                                                    tcm.getColumn(_iii).setMinWidth(0)
                                                    tcm.getColumn(_iii).setMaxWidth(0)
                                                    tcm.getColumn(_iii).setWidth(0)
                                                    self.table.removeColumn(tcm.getColumn(_iii))
                                                self.table.setAutoResizeMode(JTable.AUTO_RESIZE_OFF)

                                                myPrint("D", _THIS_EXTRACT_NAME + "Hiding unused Currency Column...")
                                                # I'm hiding it rather than removing it so not to mess with sorting etc...
                                                if self.lRemoveCurrColumn:
                                                    tcm.getColumn(_CVALUE_FORMATTED).setPreferredWidth(0)
                                                    tcm.getColumn(_CVALUE_FORMATTED).setMinWidth(0)
                                                    tcm.getColumn(_CVALUE_FORMATTED).setMaxWidth(0)
                                                    tcm.getColumn(_CVALUE_FORMATTED).setWidth(0)

                                                cTotal=sum(myDefaultWidths)

                                                self.footerTable.setColumnSelectionAllowed(False)
                                                self.footerTable.setRowSelectionAllowed(True)
                                                # self.footerTable.setFocusable(False)

                                                # Put the listener here - else it sets the defaults wrongly above....
                                                tcm.addColumnModelListener(cListener1)

                                                tcm = self.footerTable.getColumnModel()
                                                # tcm.addColumnModelListener(cListener2)

                                                for _iii in range(0, _SHRS_RAW): tcm.getColumn(_iii).setPreferredWidth(myDefaultWidths[_iii])

                                                # I'm hiding these columns for ease of data retrieval. The better option would be to remove the columns
                                                for _iii in reversed(range(_SHRS_RAW, tcm.getColumnCount())):
                                                    tcm.getColumn(_iii).setMinWidth(0)
                                                    tcm.getColumn(_iii).setMaxWidth(0)
                                                    tcm.getColumn(_iii).setWidth(0)
                                                    self.footerTable.removeColumn(tcm.getColumn(_iii))
                                                self.footerTable.setAutoResizeMode(JTable.AUTO_RESIZE_OFF)

                                                # I'm hiding it rather than removing it so not to mess with sorting etc...
                                                if self.lRemoveCurrColumn:
                                                    tcm.getColumn(_CVALUE_FORMATTED).setPreferredWidth(0)
                                                    tcm.getColumn(_CVALUE_FORMATTED).setMinWidth(0)
                                                    tcm.getColumn(_CVALUE_FORMATTED).setMaxWidth(0)
                                                    tcm.getColumn(_CVALUE_FORMATTED).setWidth(0)

                                                self.footerTableHeader = self.footerTable.getTableHeader()                          # noqa
                                                self.footerTableHeader.setEnabled(False)  # may have worked, but doesn't...
                                                self.footerTableHeader.setPreferredSize(Dimension(0, 0))  # this worked no more footer Table header

                                                self.scrollPane = JScrollPane(self.table, JScrollPane.VERTICAL_SCROLLBAR_ALWAYS,JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED)  # noqa
                                                self.scrollPane.getHorizontalScrollBar().setPreferredSize(Dimension(0, 0))
                                                self.scrollPane.setBorder(CompoundBorder(MatteBorder(0, 0, 1, 0, MD_REF.getUI().getColors().hudBorderColor), EmptyBorder(0, 0, 0, 0)))
                                                rowCount = self.table.getRowCount()
                                                rowHeight = self.table.getRowHeight()
                                                interCellSpacing = self.table.getIntercellSpacing().height
                                                headerHeight = self.table.getTableHeader().getPreferredSize().height
                                                insets = self.scrollPane.getInsets()
                                                scrollHeight = self.scrollPane.getHorizontalScrollBar().getPreferredSize()
                                                width = min(cTotal + 20, screenSize.width)  # width of all elements

                                                calcScrollPaneHeightRequired = (min(screenSize.height - 300, max(60, ((rowCount * rowHeight)
                                                                                                                      + ((rowCount) * (interCellSpacing)) + headerHeight + insets.top + insets.bottom + scrollHeight.height))))

                                                if debug:
                                                    myPrint("D", _THIS_EXTRACT_NAME + "ScreenSize: ", screenSize)
                                                    myPrint("D", _THIS_EXTRACT_NAME + "Main JTable heights....")
                                                    myPrint("D", _THIS_EXTRACT_NAME + "Row Count: ", rowCount)
                                                    myPrint("D", _THIS_EXTRACT_NAME + "RowHeight: ", rowHeight)
                                                    myPrint("D", _THIS_EXTRACT_NAME + "Intercell spacing: ", interCellSpacing)
                                                    myPrint("D", _THIS_EXTRACT_NAME + "Header height: ", headerHeight)
                                                    myPrint("D", _THIS_EXTRACT_NAME + "Insets, Top/Bot: ", insets, insets.top, insets.bottom)
                                                    myPrint("D", _THIS_EXTRACT_NAME + "Total scrollpane height: ", calcScrollPaneHeightRequired)
                                                    myPrint("D", _THIS_EXTRACT_NAME + "Scrollbar height: ", scrollHeight, scrollHeight.height)

                                                # Basically set the main table to fill most of the screen maxing at 800, but allowing for the footer...
                                                self.scrollPane.setPreferredSize(Dimension(width, calcScrollPaneHeightRequired))

                                                extract_data_frame_.add(self.scrollPane, BorderLayout.CENTER)

                                                self.footerScrollPane = JScrollPane(self.footerTable, JScrollPane.VERTICAL_SCROLLBAR_ALWAYS,JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED)  # noqa
                                                self.footerScrollPane.setBorder(CompoundBorder(MatteBorder(0, 0, 1, 0, MD_REF.getUI().getColors().hudBorderColor), EmptyBorder(0, 0, 0, 0)))

                                                myScrollSynchronizer = self.ScrollSynchronizer(self.scrollPane, self.footerScrollPane)
                                                # self.scrollPane.getVerticalScrollBar().addAdjustmentListener(myScrollSynchronizer)
                                                self.scrollPane.getHorizontalScrollBar().addAdjustmentListener(myScrollSynchronizer)
                                                # self.footerScrollPane.getVerticalScrollBar().addAdjustmentListener(myScrollSynchronizer)
                                                self.footerScrollPane.getHorizontalScrollBar().addAdjustmentListener(myScrollSynchronizer)

                                                frowCount = self.footerTable.getRowCount()
                                                frowHeight = self.footerTable.getRowHeight()
                                                finterCellSpacing = self.footerTable.getIntercellSpacing().height
                                                fheaderHeight = self.footerTable.getTableHeader().getPreferredSize().height
                                                finsets = self.footerScrollPane.getInsets()
                                                fscrollHeight = self.footerScrollPane.getHorizontalScrollBar().getPreferredSize()
                                                fcalcScrollPaneHeightRequired = min(250,
                                                                                    (((frowCount * frowHeight) + ((frowCount + 1) * finterCellSpacing) + fheaderHeight + finsets.top + finsets.bottom + fscrollHeight.height)))
                                                # fcalcScrollPaneHeightRequired = ((((frowCount * frowHeight) + ((frowCount + 1) * finterCellSpacing) + fheaderHeight + finsets.top + finsets.bottom + fscrollHeight.height)))

                                                if debug:
                                                    myPrint("D", _THIS_EXTRACT_NAME + "Footer JTable heights....")
                                                    myPrint("D", _THIS_EXTRACT_NAME + "Row Count: ", frowCount)
                                                    myPrint("D", _THIS_EXTRACT_NAME + "RowHeight: ", frowHeight)
                                                    myPrint("D", _THIS_EXTRACT_NAME + "Intercell spacing: ", finterCellSpacing)
                                                    myPrint("D", _THIS_EXTRACT_NAME + "Header height: ", fheaderHeight)
                                                    myPrint("D", _THIS_EXTRACT_NAME + "Insets, Top/Bot: ", finsets, finsets.top, finsets.bottom)
                                                    myPrint("D", _THIS_EXTRACT_NAME + "Total scrollpane height: ", fcalcScrollPaneHeightRequired)
                                                    myPrint("D", _THIS_EXTRACT_NAME + "Scrollbar height: ", fscrollHeight, fscrollHeight.height)

                                                self.footerScrollPane.setPreferredSize(Dimension(width, fcalcScrollPaneHeightRequired))
                                                extract_data_frame_.add(self.footerScrollPane, BorderLayout.SOUTH)

                                                myPrint("D", _THIS_EXTRACT_NAME + "Total frame height required: ", calcScrollPaneHeightRequired, " + ",
                                                        fcalcScrollPaneHeightRequired, "+ Intercells: ", finsets.top, finsets.bottom, " = ",
                                                        (calcScrollPaneHeightRequired + fcalcScrollPaneHeightRequired) +
                                                        (finsets.top * 2) + (finsets.bottom * 2))

                                                # Seems to be working well without setting the frame sizes + pack()
                                                # extract_data_frame_.setPreferredSize(Dimension(width, max(150,calcScrollPaneHeightRequired+fcalcScrollPaneHeightRequired+(finsets.top*2)+(finsets.bottom*2))))
                                                # extract_data_frame_.setSize(width,calcScrollPaneHeightRequired+fcalcScrollPaneHeightRequired)   # for some reason this seems irrelevant?

                                                if Platform.isOSX():
                                                    save_useScreenMenuBar = System.getProperty("apple.laf.useScreenMenuBar")
                                                    if save_useScreenMenuBar is None or save_useScreenMenuBar == "":
                                                        save_useScreenMenuBar = System.getProperty("com.apple.macos.useScreenMenuBar")
                                                    System.setProperty("apple.laf.useScreenMenuBar", "false")
                                                    System.setProperty("com.apple.macos.useScreenMenuBar", "false")
                                                else:
                                                    save_useScreenMenuBar = "true"

                                                SetupMDColors.updateUI()

                                                printButton = JButton("Print")
                                                printButton.setToolTipText("Prints the output displayed in this window to your printer")
                                                printButton.setOpaque(SetupMDColors.OPAQUE)
                                                printButton.setBackground(SetupMDColors.BACKGROUND); printButton.setForeground(SetupMDColors.FOREGROUND)
                                                printButton.addActionListener(self.PrintJTable(extract_data_frame_, self.table, "StockGlance2020", self.footerTable))

                                                mb = JMenuBar()
                                                menuH = JMenu("<html><B>MENU</b></html>")
                                                # menuH = JMenu("ABOUT")
                                                menuH.setForeground(SetupMDColors.FOREGROUND_REVERSED); menuH.setBackground(SetupMDColors.BACKGROUND_REVERSED)

                                                menuItemA = JMenuItem("About")
                                                menuItemA.setToolTipText("About...")
                                                menuItemA.addActionListener(DoTheMenu())
                                                menuH.add(menuItemA)

                                                menuItemPS = JMenuItem("Page Setup")
                                                menuItemPS.setToolTipText("Printer Page Setup...")
                                                menuItemPS.addActionListener(DoTheMenu())
                                                menuH.add(menuItemPS)

                                                menuItemEsc = JCheckBoxMenuItem("Allow Escape to Exit")
                                                menuItemEsc.setToolTipText("When enabled, allows the Escape key to exit the main screen")
                                                menuItemEsc.addActionListener(DoTheMenu())
                                                menuItemEsc.setSelected(lAllowEscapeExitApp_SWSS)
                                                menuH.add(menuItemEsc)

                                                mb.add(menuH)

                                                mb.add(Box.createHorizontalGlue())
                                                mb.add(printButton)
                                                mb.add(Box.createRigidArea(Dimension(10, 0)))

                                                extract_data_frame_.setJMenuBar(mb)

                                                if Platform.isOSX():
                                                    System.setProperty("apple.laf.useScreenMenuBar", save_useScreenMenuBar)
                                                    System.setProperty("com.apple.macos.useScreenMenuBar", save_useScreenMenuBar)

                                                extract_data_frame_.pack()
                                                extract_data_frame_.setLocationRelativeTo(None)
                                                extract_data_frame_.setVisible(True)
                                                extract_data_frame_.toFront()

                                                try:
                                                    extract_data_frame_.MoneydanceAppListener = MyMoneydanceEventListener(extract_data_frame_)
                                                    MD_REF.addAppEventListener(extract_data_frame_.MoneydanceAppListener)
                                                    myPrint("DB", _THIS_EXTRACT_NAME + "@@ added AppEventListener() %s @@" %(classPrinter("MoneydanceAppListener", extract_data_frame_.MoneydanceAppListener)))
                                                except:
                                                    myPrint("B", _THIS_EXTRACT_NAME + "FAILED to add MD App Listener...")
                                                    dump_sys_error_to_md_console_and_errorlog()

                                                extract_data_frame_.isActiveInMoneydance = True

                                            return True

                                    class DefaultTableHeaderCellRenderer(DefaultTableCellRenderer):

                                        # /**
                                        # * Constructs a <code>DefaultTableHeaderCellRenderer</code>.
                                        # * <P>
                                        # * The horizontal alignment and text position are set as appropriate to a
                                        # * table header cell, and the opaque property is set to false.
                                        # */

                                        def __init__(self):
                                            # super(DefaultTableHeaderCellRenderer, self).__init__()
                                            self.setHorizontalAlignment(JLabel.CENTER)  # This one changes the text alignment
                                            self.setHorizontalTextPosition(
                                                JLabel.RIGHT)  # This positions the  text to the  left/right of  the sort icon
                                            self.setVerticalAlignment(JLabel.BOTTOM)
                                            self.setOpaque(True)  # if this is false then it hides the background colour

                                        # enddef

                                        # /**
                                        # * returns the default table header cell renderer.
                                        # * <P>
                                        # * If the column is sorted, the appropriate icon is retrieved from the
                                        # * current Look and Feel, and a border appropriate to a table header cell
                                        # * is applied.
                                        # * <P>
                                        # * Subclasses may override this method to provide custom content or
                                        # * formatting.
                                        # *
                                        # * @param table the <code>JTable</code>.
                                        # * @param value the value to assign to the header cell
                                        # * @param isSelected This parameter is ignored.
                                        # * @param hasFocus This parameter is ignored.
                                        # * @param row This parameter is ignored.
                                        # * @param column the column of the header cell to render
                                        # * @return the default table header cell renderer
                                        # */

                                        # noinspection PyUnusedLocal
                                        def getTableCellRendererComponent(self, table, value, isSelected, hasFocus, row, column):   # noqa
                                            super(DefaultTableHeaderCellRenderer, self).getTableCellRendererComponent(table, value, isSelected,hasFocus, row, column)    # noqa
                                            tableHeader = table.getTableHeader()
                                            # if (tableHeader is not None): self.setForeground(tableHeader.getForeground())
                                            align = firstRowTableCellRenderer = table.getCellRenderer(0, column).getHorizontalAlignment()
                                            self.setHorizontalAlignment(align)
                                            if align == JLabel.RIGHT:
                                                self.setHorizontalTextPosition(JLabel.RIGHT)
                                            elif align == JLabel.LEFT:
                                                self.setHorizontalTextPosition(JLabel.LEFT)
                                            elif align == JLabel.CENTER:
                                                self.setHorizontalTextPosition(JLabel.LEFT)

                                            self.setIcon(self._getIcon(table, column))
                                            self.setBorder(UIManager.getBorder("TableHeader.cellBorder"))

                                            self.setForeground(MD_REF.getUI().getColors().headerFG)
                                            self.setBackground(MD_REF.getUI().getColors().headerBG1)

                                            # self.setHorizontalAlignment(JLabel.CENTER)

                                            return self

                                        # enddef

                                        # /**
                                        # * Overloaded to return an icon suitable to the primary sorted column, or null if
                                        # * the column is not the primary sort key.
                                        # *
                                        # * @param table the <code>JTable</code>.
                                        # * @param column the column index.
                                        # * @return the sort icon, or null if the column is unsorted.
                                        # */
                                        def _getIcon(self, _table, column):
                                            sortKey = self.getSortKey(_table, column)
                                            if (sortKey is not None and _table.convertColumnIndexToView(sortKey.getColumn()) == column):
                                                x = (sortKey.getSortOrder())
                                                if x == SortOrder.ASCENDING:      return UIManager.getIcon("Table.ascendingSortIcon")
                                                elif x == SortOrder.DESCENDING:   return UIManager.getIcon("Table.descendingSortIcon")
                                                elif x == SortOrder.UNSORTED:     return UIManager.getIcon("Table.naturalSortIcon")
                                            return None

                                        # enddef

                                        # /**
                                        # * returns the current sort key, or null if the column is unsorted.
                                        # *
                                        # * @param table the table
                                        # * @param column the column index
                                        # * @return the SortKey, or null if the column is unsorted
                                        # */
                                        def getSortKey(self, table, column):                                                        # noqa
                                            rowSorter = table.getRowSorter()
                                            if (rowSorter is None): return None
                                            sortedColumns = rowSorter.getSortKeys()
                                            if (sortedColumns.size() > 0): return sortedColumns.get(0)
                                            return None
                                        # enddef

                                    GlobalVars.stockGlanceInstance = StockGlance2020()

                                    if GlobalVars.DISPLAY_DATA:
                                        GlobalVars.stockGlanceInstance.createAndShowGUI()      # Will relaunch itself onto the EDT

                                    else:

                                        def ExtractDataToFile():
                                            global headingNames, csvDelimiter
                                            global lSplitSecuritiesByAccount, lExcludeTotalsFromCSV, lIncludeFutureBalances_SG2020
                                            global maxDecimalPlacesRounding_SG2020, lUseCurrentPrice_SG2020
                                            global lWriteBOMToExportFile_SWSS

                                            global _SHRS_FORMATTED, _SHRS_RAW, _PRICE_FORMATTED, _PRICE_RAW, _CVALUE_FORMATTED, _CVALUE_RAW, _BVALUE_FORMATTED, _BVALUE_RAW, _SORT
                                            global _CBVALUE_FORMATTED, _CBVALUE_RAW, _GAIN_FORMATTED, _GAIN_RAW, _EXCLUDECSV, _GAINPCT

                                            myPrint("D", _THIS_EXTRACT_NAME + "In ", inspect.currentframe().f_code.co_name, "()")

                                            if not lSplitSecuritiesByAccount:
                                                GlobalVars.rawDataTable_sg2020 = sorted(GlobalVars.rawDataTable_sg2020, key=lambda x: (x[1].upper()))

                                            GlobalVars.rawDataTable_sg2020.insert(0,headingNames)  # Insert Column Headings at top of list. A bit rough and ready, not great coding, but a short list...!

                                            for _iii in range(0, len(GlobalVars.rawFooterTable_sg2020)):
                                                GlobalVars.rawDataTable_sg2020.append(GlobalVars.rawFooterTable_sg2020[_iii])

                                            myPrint("B", _THIS_EXTRACT_NAME + "Opening file and writing %s records" %(len(GlobalVars.rawDataTable_sg2020)))

                                            try:
                                                # CSV Writer will take care of special characters / delimiters within fields by wrapping in quotes that Excel will decode
                                                with open(GlobalVars.csvfilename,"wb") as csvfile:  # PY2.7 has no newline parameter so opening in binary; just use "w" and newline='' in PY3.0

                                                    if lWriteBOMToExportFile_SWSS:
                                                        csvfile.write(codecs.BOM_UTF8)   # This 'helps' Excel open file with double-click as UTF-8

                                                    writer = csv.writer(csvfile, dialect='excel', quoting=csv.QUOTE_MINIMAL, delimiter=fix_delimiter(csvDelimiter))

                                                    if csvDelimiter != ",":
                                                        writer.writerow(["sep=",""])  # Tells Excel to open file with the alternative delimiter (it will add the delimiter to this line)

                                                    writer.writerow(GlobalVars.rawDataTable_sg2020[0][:_SHRS_RAW])  # Print the header, but not the extra _field headings

                                                    for _iii in range(1, len(GlobalVars.rawDataTable_sg2020)):
                                                        if not GlobalVars.rawDataTable_sg2020[_iii][_EXCLUDECSV]:
                                                            # Write the table, but swap in the raw numbers (rather than formatted number strings)
                                                            try:
                                                                writer.writerow([
                                                                    fixFormatsStr(GlobalVars.rawDataTable_sg2020[_iii][0], False),
                                                                    fixFormatsStr(GlobalVars.rawDataTable_sg2020[_iii][1], False),
                                                                    fixFormatsStr(GlobalVars.rawDataTable_sg2020[_iii][_SHRS_RAW], True),
                                                                    fixFormatsStr(GlobalVars.rawDataTable_sg2020[_iii][_PRICE_RAW], True),
                                                                    fixFormatsStr(GlobalVars.rawDataTable_sg2020[_iii][4], False),
                                                                    fixFormatsStr(GlobalVars.rawDataTable_sg2020[_iii][_CVALUE_RAW], True),
                                                                    fixFormatsStr(GlobalVars.rawDataTable_sg2020[_iii][_BVALUE_RAW], True),
                                                                    fixFormatsStr(GlobalVars.rawDataTable_sg2020[_iii][_CBVALUE_RAW], True),
                                                                    fixFormatsStr(GlobalVars.rawDataTable_sg2020[_iii][_GAIN_RAW], True),
                                                                    fixFormatsStr(GlobalVars.rawDataTable_sg2020[_iii][_GAINPCT], True, "%"),
                                                                    fixFormatsStr(GlobalVars.rawDataTable_sg2020[_iii][10], False),
                                                                    ""])
                                                            except:
                                                                _msgTxt = _THIS_EXTRACT_NAME + "@@ ERROR writing to CSV on row %s. Please review console" %(_iii)
                                                                GlobalVars.AUTO_MESSAGES.append(_msgTxt)
                                                                myPrint("B", _msgTxt)
                                                                myPrint("B", GlobalVars.rawDataTable_sg2020[_iii])
                                                                raise

                                                    if lWriteParametersToExportFile_SWSS:
                                                        today = Calendar.getInstance()
                                                        writer.writerow([""])
                                                        writer.writerow(["StuWareSoftSystems - " + GlobalVars.thisScriptName + "(build: "
                                                                         + version_build
                                                                         + ")  Moneydance Python Script - Date of Extract: "
                                                                         + str(GlobalVars.sdf.format(today.getTime()))])

                                                        writer.writerow([""])
                                                        writer.writerow(["Dataset path/name: %s" %(MD_REF.getCurrentAccountBook().getRootFolder()) ])

                                                        writer.writerow([""])
                                                        writer.writerow(["User Parameters..."])

                                                        writer.writerow(["Hiding Hidden Securities...: %s" %(hideHiddenSecurities)])
                                                        writer.writerow(["Hiding Inactive Accounts...: %s" %(hideInactiveAccounts)])
                                                        writer.writerow(["Hiding Hidden Accounts.....: %s" %(hideHiddenAccounts)])
                                                        writer.writerow(["Security filter............: %s '%s'" %(lAllSecurity,filterForSecurity)])
                                                        writer.writerow(["Account filter.............: %s '%s'" %(lAllAccounts,filterForAccounts)])
                                                        writer.writerow(["Currency filter............: %s '%s'" %(lAllCurrency,filterForCurrency)])
                                                        writer.writerow(["Include Cash Balances......: %s" %(lIncludeCashBalances)])
                                                        writer.writerow(["Include Future Balances....: %s" %(lIncludeFutureBalances_SG2020)])
                                                        writer.writerow(["Use Current Price..........: %s (False means use the latest dated price history price)" %(lUseCurrentPrice_SG2020)])
                                                        writer.writerow(["Max Price dpc Rounding.....: %s" %(maxDecimalPlacesRounding_SG2020)])
                                                        writer.writerow(["Split Securities by Account: %s" %(lSplitSecuritiesByAccount)])
                                                        writer.writerow(["Extract Totals from CSV....: %s" %(lExcludeTotalsFromCSV)])

                                                _msgTxt = _THIS_EXTRACT_NAME + "CSV file: '%s' created (%s records)" %(GlobalVars.csvfilename, len(GlobalVars.rawDataTable_sg2020))
                                                myPrint("B", _msgTxt)
                                                GlobalVars.AUTO_MESSAGES.append(_msgTxt)
                                                GlobalVars.countFilesCreated += 1

                                            except:
                                                e_type, exc_value, exc_traceback = sys.exc_info()                       # noqa
                                                _msgTxt = _THIS_EXTRACT_NAME + "@@ ERROR '%s' detected writing file: '%s' - Extract ABORTED!" %(exc_value, GlobalVars.csvfilename)
                                                GlobalVars.AUTO_MESSAGES.append(_msgTxt)
                                                myPrint("B", _msgTxt)
                                                raise

                                        def fixFormatsStr(theString, lNumber, sFormat=""):
                                            if lNumber is None: lNumber = False
                                            if theString is None: theString = ""

                                            if sFormat == "%" and theString != "":
                                                theString = "{:.1%}".format(theString)
                                                return theString

                                            if lNumber: return str(theString)

                                            theString = theString.strip()  # remove leading and trailing spaces

                                            if theString[:3] == "===": theString = " " + theString  # Small fix as Libre Office doesn't like "=======" (it thinks it's a formula)

                                            theString = theString.replace("\n", "*")  # remove newlines within fields to keep csv format happy
                                            theString = theString.replace("\t", "*")  # remove tabs within fields to keep csv format happy

                                            if lStripASCII:
                                                all_ASCII = ''.join(char for char in theString if
                                                                    ord(char) < 128)  # Eliminate non ASCII printable Chars too....
                                            else:
                                                all_ASCII = theString
                                            return all_ASCII

                                        GlobalVars.stockGlanceInstance.generateTableModels(MD_REF.getCurrentAccountBook())

                                        if GlobalVars.stockGlanceInstance.getTableModel() is not None:
    
                                            ExtractDataToFile()
    
                                            if not GlobalVars.lGlobalErrorDetected:
                                                sTxt = "Extract file CREATED:"
                                                mTxt = "With %s rows (%s footer rows)\n" % (len(GlobalVars.rawDataTable_sg2020), len(GlobalVars.rawFooterTable_sg2020))
                                                myPrint("B", _THIS_EXTRACT_NAME + "%s\n%s" %(sTxt, mTxt))
                                            else:
                                                _msgTextx = _THIS_EXTRACT_NAME + "ERROR Creating extract (review console for error messages)...."
                                                GlobalVars.AUTO_MESSAGES.append(_msgTextx)
                                        else:
                                            _msgTextx = _THIS_EXTRACT_NAME + "@@ No records selected and no extract file created @@"
                                            GlobalVars.AUTO_MESSAGES.append(_msgTextx)
                                            myPrint("B", _msgTextx)

                                            # The 'You have no securities' message already pops up earlier....
                                            # if not GlobalVars.AUTO_EXTRACT_MODE:
                                            #     DoExtractsSwingWorker.killPleaseWait()
                                            #     genericSwingEDTRunner(True, True, myPopupInformationBox, extract_data_frame_, _msgTextx, GlobalVars.thisScriptName, JOptionPane.WARNING_MESSAGE)
    
                                        # delete references to large objects
                                        del GlobalVars.rawDataTable_sg2020, GlobalVars.rawFooterTable_sg2020

                                try:
                                    do_stockglance2020()
                                except:
                                    GlobalVars.lGlobalErrorDetected = True

                                if GlobalVars.lGlobalErrorDetected:
                                    GlobalVars.countErrorsDuringExtract += 1
                                    _txt = _THIS_EXTRACT_NAME + "@@ ERROR: do_stockglance2020() has failed (review console)!"
                                    GlobalVars.AUTO_MESSAGES.append(_txt)
                                    myPrint("B", _txt)
                                    dump_sys_error_to_md_console_and_errorlog()
                                    if not GlobalVars.AUTO_EXTRACT_MODE:
                                        DoExtractsSwingWorker.killPleaseWait()
                                        genericSwingEDTRunner(True, True, myPopupInformationBox, extract_data_frame_, _txt, "ERROR", JOptionPane.ERROR_MESSAGE)
                                        return False
                            #### ENDIF lExtractStockGlance2020 ####

                            if lExtractReminders:
                                # ####################################################
                                # EXTRACT_REMINDERS_CSV EXECUTION
                                # ####################################################

                                _THIS_EXTRACT_NAME = pad("EXTRACT: Reminders:", 34)
                                GlobalVars.lGlobalErrorDetected = False

                                if not GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE:
                                    self.super__publish([_THIS_EXTRACT_NAME.strip()])                                   # noqa

                                if GlobalVars.AUTO_EXTRACT_MODE:
                                    GlobalVars.csvfilename = os.path.join(GlobalVars.scriptpath, MD_REF.getCurrentAccountBook().getName() + "_" + GlobalVars.defaultFileName_ERTC + ".csv")
                                    GlobalVars.csvfilename_future = os.path.join(GlobalVars.scriptpath, MD_REF.getCurrentAccountBook().getName() + "_" + GlobalVars.defaultFileName_future_ERTC + ".csv")

                                def do_extract_reminders():
                                    global lDidIUseAttachmentDir
                                    global csvheaderline, headerFormats
                                    global focus, row, EditedReminderCheck, ReminderTable_Count, ExtractDetails_Count

                                    global __extract_data, extract_filename
                                    global lStripASCII, csvDelimiter, userdateformat, lWriteBOMToExportFile_SWSS
                                    global hideInactiveAccounts, hideHiddenAccounts, hideHiddenSecurities
                                    global lAllSecurity, filterForSecurity, lAllAccounts, filterForAccounts, lAllCurrency, filterForCurrency
                                    global whichDefaultExtractToRun_SWSS
                                    global _column_widths_ERTC, lExtractFutureRemindersToo_ERTC

                                    def terminate_script():
                                        myPrint("DB", _THIS_EXTRACT_NAME + "In ", inspect.currentframe().f_code.co_name, "()")
                                        myPrint("DB", _THIS_EXTRACT_NAME + "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

                                        # We have to do this here too to save the dynamic column widths....
                                        try:
                                            save_StuWareSoftSystems_parameters_to_file()
                                        except:
                                            myPrint("B", _THIS_EXTRACT_NAME + "Error - failed to save parameters to pickle file...!")
                                            dump_sys_error_to_md_console_and_errorlog()

                                        try:
                                            # NOTE - .dispose() - The windowClosed event should set .isActiveInMoneydance False and .removeAppEventListener()
                                            if not SwingUtilities.isEventDispatchThread():
                                                SwingUtilities.invokeLater(GenericDisposeRunnable(extract_data_frame_))
                                            else:
                                                extract_data_frame_.dispose()
                                        except:
                                            myPrint("B", _THIS_EXTRACT_NAME + "Error. Final dispose failed....?")
                                            dump_sys_error_to_md_console_and_errorlog()

                                    class DoTheMenu(AbstractAction):

                                        def __init__(self): pass

                                        def actionPerformed(self, event):															# noqa
                                            global lAllowEscapeExitApp_SWSS     # global as we can set this here

                                            myPrint("D", _THIS_EXTRACT_NAME + "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

                                            if event.getActionCommand().lower().startswith("show reminder"):
                                                reminders = MD_REF.getCurrentAccountBook().getReminders()
                                                reminder = reminders.getAllReminders()[GlobalVars.table.getValueAt(row, 0) - 1]
                                                MD_REF.getUI().showRawItemDetails(reminder, extract_data_frame_)

                                            if event.getActionCommand().lower().startswith("page setup"):
                                                pageSetup()

                                            if event.getActionCommand().lower().startswith("refresh"):
                                                RefreshMenuAction().refresh()

                                            if event.getActionCommand().lower().startswith("close"):
                                                NoExtractMenuJustCloseAction().no_extract_just_close()

                                            if event.getActionCommand() == "About":
                                                AboutThisScript(extract_data_frame_).go()

                                            if event.getActionCommand().lower().startswith("allow escape"):
                                                lAllowEscapeExitApp_SWSS = not lAllowEscapeExitApp_SWSS
                                                if lAllowEscapeExitApp_SWSS:
                                                    extract_data_frame_.getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0), "close-window")
                                                else:
                                                    extract_data_frame_.getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).remove(KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0))

                                                # Note: save_StuWareSoftSystems_parameters_to_file() is called within terminate_script() - so will save on exit
                                                myPrint("B", _THIS_EXTRACT_NAME + "Escape key can exit the app's main screen: %s" %(lAllowEscapeExitApp_SWSS))

                                            myPrint("D", _THIS_EXTRACT_NAME + "Exiting ", inspect.currentframe().f_code.co_name, "()")
                                            return

                                    def convertIntDateFormattedString(dateInt, formatStr):
                                        if dateInt == 0 or dateInt == 19700101: return ""
                                        dateasdate = datetime.datetime.strptime(str(dateInt), "%Y%m%d")  # Convert to Date field
                                        return dateasdate.strftime(formatStr)

                                    def myGetNextOccurance(theRem, startDate, maximumDate):
                                        cal = Calendar.getInstance()
                                        ackPlusOne = theRem.getDateAcknowledgedInt()
                                        if ackPlusOne > 0:
                                            ackPlusOne = DateUtil.incrementDate(ackPlusOne, 0, 0, 1)
                                        DateUtil.setCalendarDate(cal, Math.max(startDate, ackPlusOne))
                                        while True:
                                            intDate = DateUtil.convertCalToInt(cal)
                                            if (intDate > maximumDate or (theRem.getLastDateInt() > 0 and intDate > theRem.getLastDateInt())):	# noqa
                                                return 0
                                            if (theRem.occursOnDate(cal)):
                                                return DateUtil.convertCalToInt(cal)
                                            cal.add(Calendar.DAY_OF_MONTH, 1)

                                    # Copied from list_future_reminders.py script....
                                    def build_future_reminders_table(reminderTable):

                                        FUTURE_MAX_END_DATE = 20991231

                                        baseCurr = MD_REF.getCurrentAccount().getBook().getCurrencies().getBaseType()

                                        # Future Reminders Table
                                        GlobalVars.tableHeaderRowList_reminders_future = [
                                            "Next Due",
                                            "Account Name",
                                            "Reminder Description",
                                            "Reminder Memo",
                                            "Net Amount",
                                            "Categories(amounts)"
                                        ]

                                        GlobalVars.csvlines_reminders_future = []
                                        GlobalVars.csvlines_reminders_future.append(GlobalVars.tableHeaderRowList_reminders_future)

                                        for index in range(0, int(reminderTable.size())):
                                            rem = reminderTable[index]  # Get the reminder

                                            remtype = rem.getReminderType()  # NOTE or TRANSACTION
                                            desc = rem.getDescription().replace(",", " ")
                                            memo = rem.getMemo().replace(",", " ").strip()
                                            memo = memo.replace("\n", "*").strip()

                                            todayInt = DateUtil.getStrippedDateInt()
                                            lastdate = rem.getLastDateInt()

                                            if lastdate < 1:  # Detect if an enddate is set
                                                stopDate = min(DateUtil.incrementDate(todayInt, 0, 0, GlobalVars.daysToLookForward_LFR), FUTURE_MAX_END_DATE)
                                            else:
                                                stopDate = min(DateUtil.incrementDate(todayInt, 0, 0, GlobalVars.daysToLookForward_LFR), lastdate)

                                            nextDate = rem.getNextOccurance(stopDate)
                                            if nextDate < 1: continue

                                            loopDetector = 0

                                            while True:

                                                loopDetector += 1
                                                if loopDetector > 10000:
                                                    raise Exception("Loop detected..? Aborting.... Reminder:", rem)

                                                calcNext = myGetNextOccurance(rem, nextDate, stopDate)

                                                if calcNext < 1: break

                                                remdate = calcNext

                                                nextDate = DateUtil.incrementDate(calcNext, 0, 0, 1)

                                                lastack = rem.getDateAcknowledgedInt()
                                                if lastack == 0 or lastack == 19700101: lastack = ''											# noqa

                                                if str(remtype) == 'NOTE':
                                                    csvline = []

                                                    # csvline.append(rem)

                                                    csvline.append(remdate)
                                                    csvline.append("")
                                                    csvline.append(desc)
                                                    csvline.append(memo)
                                                    csvline.append("")
                                                    csvline.append("")
                                                    GlobalVars.csvlines_reminders_future.append(csvline)

                                                elif str(remtype) == 'TRANSACTION':
                                                    txnparent = rem.getTransaction()
                                                    amount = baseCurr.getDoubleValue(txnparent.getValue())
                                                    stripacct = txnparent.getAccount().getFullAccountName().strip()

                                                    catsAmounts = ""
                                                    for iRemSplit in range(0, txnparent.getOtherTxnCount()):
                                                        remSplit = txnparent.getOtherTxn(iRemSplit)
                                                        stripCat = remSplit.getAccount().getFullAccountName().strip()
                                                        splitValue = GlobalVars.baseCurrency.getDoubleValue(remSplit.getValue()) * -1
                                                        catsAmounts += "{%s;%s}" %(stripCat, splitValue)

                                                    csvline = []
                                                    csvline.append(remdate)
                                                    csvline.append(stripacct)
                                                    csvline.append(desc)
                                                    csvline.append(memo)
                                                    csvline.append((amount))
                                                    csvline.append(catsAmounts)
                                                    GlobalVars.csvlines_reminders_future.append(csvline)

                                            index += 1

                                    def build_the_data_file(ind):
                                        global userdateformat, csvheaderline, headerFormats, ExtractDetails_Count

                                        ExtractDetails_Count += 1

                                        myPrint("D", _THIS_EXTRACT_NAME + "In ", inspect.currentframe().f_code.co_name, "()", ind, " - On iteration/call: ", ExtractDetails_Count)

                                        # ind == 1 means that this is a repeat call, so the table should be refreshed

                                        root = MD_REF.getCurrentAccountBook()

                                        rems = root.getReminders().getAllReminders()

                                        if rems.size() < 1:
                                            return False

                                        myPrint("B", _THIS_EXTRACT_NAME + "Success: read: %s reminders" %(rems.size()))

                                        csvheaderline = [
                                            "Number#",
                                            "NextDue",
                                            "ReminderType",
                                            "Frequency",
                                            "AutoCommitDays",
                                            "LastAcknowledged",
                                            "FirstDate",
                                            "EndDate",
                                            "ReminderDescription",
                                            "NetAmount",
                                            "TxfrType",
                                            "Account",
                                            "MainDescription",
                                            "Split#",
                                            "SplitAmount",
                                            "Category",
                                            "Description",
                                            "Memo"
                                        ]

                                        headerFormats = [[Number,JLabel.CENTER],
                                                         [String,JLabel.CENTER],
                                                         [String,JLabel.LEFT],
                                                         [String,JLabel.LEFT],
                                                         [String,JLabel.LEFT],
                                                         [String,JLabel.CENTER],
                                                         [String,JLabel.CENTER],
                                                         [String,JLabel.CENTER],
                                                         [String,JLabel.LEFT],
                                                         [Number,JLabel.RIGHT],
                                                         [String,JLabel.LEFT],
                                                         [String,JLabel.LEFT],
                                                         [String,JLabel.LEFT],
                                                         [String,JLabel.CENTER],
                                                         [Number,JLabel.RIGHT],
                                                         [String,JLabel.LEFT],
                                                         [String,JLabel.LEFT],
                                                         [String,JLabel.LEFT]
                                                         ]

                                        # Read each reminder and create a csv line for each in the GlobalVars.csvlines_reminders array
                                        GlobalVars.csvlines_reminders = []

                                        for index in range(0, int(rems.size())):
                                            rem = rems[index]  # Get the reminder

                                            remtype = rem.getReminderType()  # NOTE or TRANSACTION
                                            desc = rem.getDescription().replace(",", " ")  # remove commas to keep csv format happy
                                            memo = rem.getMemo().replace(",", " ").strip()  # remove commas to keep csv format happy
                                            memo = memo.replace("\n", "*").strip()  # remove newlines to keep csv format happy

                                            # determine the frequency of the transaction
                                            daily = rem.getRepeatDaily()
                                            weekly = rem.getRepeatWeeklyModifier()
                                            monthly = rem.getRepeatMonthlyModifier()
                                            yearly = rem.getRepeatYearly()
                                            countfreqs = 0

                                            remfreq = ''

                                            if daily > 0:
                                                remfreq += 'DAILY'
                                                remfreq += '(every ' + str(daily) + ' days)'
                                                countfreqs += 1

                                            if len(rem.getRepeatWeeklyDays()) > 0 and rem.getRepeatWeeklyDays()[0] > 0:
                                                for freq in range(0, len(rem.getRepeatWeeklyDays())):
                                                    if len(remfreq) > 0: remfreq += " & "
                                                    if weekly == Reminder.WEEKLY_EVERY:                remfreq += 'WEEKLY_EVERY'
                                                    if weekly == Reminder.WEEKLY_EVERY_FIFTH:            remfreq += 'WEEKLY_EVERY_FIFTH'
                                                    if weekly == Reminder.WEEKLY_EVERY_FIRST:            remfreq += 'WEEKLY_EVERY_FIRST'
                                                    if weekly == Reminder.WEEKLY_EVERY_FOURTH:            remfreq += 'WEEKLY_EVERY_FOURTH'
                                                    if weekly == Reminder.WEEKLY_EVERY_LAST:            remfreq += 'WEEKLY_EVERY_LAST'
                                                    if weekly == Reminder.WEEKLY_EVERY_SECOND:            remfreq += 'WEEKLY_EVERY_SECOND'
                                                    if weekly == Reminder.WEEKLY_EVERY_THIRD:            remfreq += 'WEEKLY_EVERY_THIRD'

                                                    if rem.getRepeatWeeklyDays()[freq] == 1: remfreq += '(on Sunday)'
                                                    if rem.getRepeatWeeklyDays()[freq] == 2: remfreq += '(on Monday)'
                                                    if rem.getRepeatWeeklyDays()[freq] == 3: remfreq += '(on Tuesday)'
                                                    if rem.getRepeatWeeklyDays()[freq] == 4: remfreq += '(on Wednesday)'
                                                    if rem.getRepeatWeeklyDays()[freq] == 5: remfreq += '(on Thursday)'
                                                    if rem.getRepeatWeeklyDays()[freq] == 6: remfreq += '(on Friday)'
                                                    if rem.getRepeatWeeklyDays()[freq] == 7: remfreq += '(on Saturday)'
                                                    if rem.getRepeatWeeklyDays()[freq] < 1 or rem.getRepeatWeeklyDays()[
                                                        freq] > 7: remfreq += '(*ERROR*)'
                                                    countfreqs += 1

                                            if len(rem.getRepeatMonthly()) > 0 and rem.getRepeatMonthly()[0] > 0:
                                                for freq in range(0, len(rem.getRepeatMonthly())):
                                                    if len(remfreq) > 0: remfreq += " & "
                                                    if monthly == Reminder.MONTHLY_EVERY:                 remfreq += 'MONTHLY_EVERY'
                                                    if monthly == Reminder.MONTHLY_EVERY_FOURTH:         remfreq += 'MONTHLY_EVERY_FOURTH'
                                                    if monthly == Reminder.MONTHLY_EVERY_OTHER:         remfreq += 'MONTHLY_EVERY_OTHER'
                                                    if monthly == Reminder.MONTHLY_EVERY_SIXTH:         remfreq += 'MONTHLY_EVERY_SIXTH'
                                                    if monthly == Reminder.MONTHLY_EVERY_THIRD:         remfreq += 'MONTHLY_EVERY_THIRD'

                                                    theday = rem.getRepeatMonthly()[freq]
                                                    if theday == Reminder.LAST_DAY_OF_MONTH:
                                                        remfreq += '(on LAST_DAY_OF_MONTH)'
                                                    else:
                                                        if 4 <= theday <= 20 or 24 <= theday <= 30: suffix = "th"
                                                        else:                                        suffix = ["st", "nd", "rd"][theday % 10 - 1]

                                                        remfreq += '(on ' + str(theday) + suffix + ')'

                                                    countfreqs += 1

                                            if yearly:
                                                if len(remfreq) > 0: remfreq += " & "
                                                remfreq += 'YEARLY'
                                                countfreqs += 1

                                            if len(remfreq) < 1 or countfreqs == 0:
                                                remfreq = '!ERROR! NO ACTUAL FREQUENCY OPTIONS SET PROPERLY ' + remfreq

                                            if countfreqs > 1:
                                                remfreq = "**MULTI** " + remfreq

                                            lastdate = rem.getLastDateInt()
                                            if lastdate < 1:  # Detect if an enddate is set
                                                # remdate = rem.getNextOccurance(20991231)                                              # Use cutoff  far into the future
                                                remdate = StoreDateInt(rem.getNextOccurance(20991231), userdateformat)                  # Use cutoff  far into the future
                                            else:
                                                # remdate = rem.getNextOccurance(rem.getLastDateInt())                                  # Stop at enddate
                                                remdate = StoreDateInt(rem.getNextOccurance(rem.getLastDateInt()), userdateformat)      # Stop at enddate

                                            if remdate.getDateInt() == 0: remdate.setExpired(True)

                                            auto = rem.getAutoCommitDays()
                                            if auto >= 0:    auto = 'YES: (' + str(auto) + ' days before scheduled)'
                                            else:            auto = 'NO'

                                            if str(remtype) == 'NOTE':
                                                csvline = []
                                                csvline.append(index + 1)
                                                csvline.append(remdate)
                                                csvline.append(safeStr(rem.getReminderType()))
                                                csvline.append(remfreq)
                                                csvline.append(auto)
                                                csvline.append(StoreDateInt(rem.getDateAcknowledgedInt(), userdateformat))
                                                csvline.append(StoreDateInt(rem.getInitialDateInt(), userdateformat))
                                                csvline.append(StoreDateInt(lastdate, userdateformat))
                                                csvline.append(desc)
                                                csvline.append('')  # NetAmount
                                                csvline.append('')  # TxfrType
                                                csvline.append('')  # Account
                                                csvline.append('')  # MainDescription
                                                csvline.append(str(index + 1) + '.0')  # Split#
                                                csvline.append('')  # SplitAmount
                                                csvline.append('')  # Category
                                                csvline.append('')  # Description
                                                csvline.append('"' + memo + '"')  # Memo
                                                GlobalVars.csvlines_reminders.append(csvline)

                                            elif str(remtype) == 'TRANSACTION':
                                                txnparent = rem.getTransaction()
                                                amount = GlobalVars.baseCurrency.getDoubleValue(txnparent.getValue())

                                                for index2 in range(0, int(txnparent.getOtherTxnCount())):
                                                    splitdesc = txnparent.getOtherTxn(index2).getDescription().replace(","," ")  # remove commas to keep csv format happy
                                                    splitmemo = txnparent.getMemo().replace(",", " ")  # remove commas to keep csv format happy
                                                    maindesc = txnparent.getDescription().replace(",", " ").strip()

                                                    if index2 > 0: amount = ''  # Don't repeat the new amount on subsequent split lines (so you can total column). The split amount will be correct

                                                    # stripacct = str(txnparent.getAccount()).replace(",", " ").strip()  # remove commas to keep csv format happy
                                                    stripacct = txnparent.getAccount().getFullAccountName().replace(",", " ").strip()  # remove commas to keep csv format happy

                                                    # stripcat = str(txnparent.getOtherTxn(index2).getAccount()).replace(","," ").strip()  # remove commas to keep csv format happy
                                                    stripcat = txnparent.getOtherTxn(index2).getAccount().getFullAccountName().replace(","," ").strip()  # remove commas to keep csv format happy

                                                    csvline = []
                                                    csvline.append(index + 1)
                                                    csvline.append(remdate)
                                                    csvline.append(safeStr(rem.getReminderType()))
                                                    csvline.append(remfreq)
                                                    csvline.append(auto)
                                                    csvline.append(StoreDateInt(rem.getDateAcknowledgedInt(), userdateformat))
                                                    csvline.append(StoreDateInt(rem.getInitialDateInt(), userdateformat))
                                                    csvline.append(StoreDateInt(lastdate, userdateformat))
                                                    csvline.append(desc)
                                                    csvline.append((amount))
                                                    csvline.append(txnparent.getTransferType())
                                                    csvline.append(stripacct)
                                                    csvline.append(maindesc)
                                                    csvline.append(str(index + 1) + '.' + str(index2 + 1))
                                                    csvline.append(GlobalVars.baseCurrency.getDoubleValue(txnparent.getOtherTxn(index2).getValue()) * -1)
                                                    csvline.append(stripcat)
                                                    csvline.append(splitdesc)
                                                    csvline.append(splitmemo)
                                                    GlobalVars.csvlines_reminders.append(csvline)

                                            index += 1

                                        if GlobalVars.EXTRACT_DATA and ind == 0 and lExtractFutureRemindersToo_ERTC:
                                            build_future_reminders_table(rems)

                                        if GlobalVars.DISPLAY_DATA:
                                            myPrint("DB", "Launching ReminderTable() via (and waiting on) the EDT.....")
                                            genericSwingEDTRunner(True, True, ReminderTable, GlobalVars.csvlines_reminders, ind)

                                        ExtractDetails_Count -= 1

                                        if ind == 0:
                                            if GlobalVars.DISPLAY_DATA:
                                                def remindersGrabFocus():
                                                    myPrint("DB", "In .remindersGrabFocus()")
                                                    global focus
                                                    focus = "gained"											        # noqa
                                                    GlobalVars.table.setRowSelectionInterval(0, row)
                                                    GlobalVars.table.requestFocus()

                                                myPrint("DB", "Launching remindersGrabFocus() via the EDT.....")
                                                genericSwingEDTRunner(False, False, remindersGrabFocus)

                                        myPrint("D", _THIS_EXTRACT_NAME + "Exiting ", inspect.currentframe().f_code.co_name)
                                        return True

                                    # Synchronises column widths of both JTables
                                    class ColumnChangeListener(TableColumnModelListener):
                                        sourceTable = None
                                        targetTable = None

                                        def __init__(self, source):
                                            self.sourceTable = source

                                        def columnAdded(self, evt): pass

                                        def columnSelectionChanged(self, evt): pass

                                        def columnRemoved(self, evt): pass

                                        def columnMoved(self, evt): pass

                                        # noinspection PyUnusedLocal
                                        def columnMarginChanged(self, evt):
                                            global _column_widths_ERTC

                                            sourceModel = self.sourceTable.getColumnModel()

                                            for _iii in range(0, sourceModel.getColumnCount()):
                                                # Saving for later... Yummy!!
                                                _column_widths_ERTC[_iii] = sourceModel.getColumn(_iii).getWidth()
                                                myPrint("D", _THIS_EXTRACT_NAME + "Saving column %s as width %s for later..." %(_iii,_column_widths_ERTC[_iii]))

                                    class DefaultTableHeaderCellRenderer(DefaultTableCellRenderer):

                                        # /**
                                        # * Constructs a <code>DefaultTableHeaderCellRenderer</code>.
                                        # * <P>
                                        # * The horizontal alignment and text position are set as appropriate to a
                                        # * table header cell, and the opaque property is set to false.
                                        # */

                                        def __init__(self):
                                            # super(DefaultTableHeaderCellRenderer, self).__init__()
                                            self.setHorizontalAlignment(JLabel.CENTER)  # This one changes the text alignment
                                            self.setHorizontalTextPosition(JLabel.RIGHT)  # This positions the  text to the  left/right of  the sort icon
                                            self.setVerticalAlignment(JLabel.BOTTOM)
                                            self.setOpaque(True)  # if this is false then it hides the background colour

                                        # enddef

                                        # /**
                                        # * returns the default table header cell renderer.
                                        # * <P>
                                        # * If the column is sorted, the appropriate icon is retrieved from the
                                        # * current Look and Feel, and a border appropriate to a table header cell
                                        # * is applied.
                                        # * <P>
                                        # * Subclasses may overide this method to provide custom content or
                                        # * formatting.
                                        # *
                                        # * @param table the <code>JTable</code>.
                                        # * @param value the value to assign to the header cell
                                        # * @param isSelected This parameter is ignored.
                                        # * @param hasFocus This parameter is ignored.
                                        # * @param row This parameter is ignored.
                                        # * @param column the column of the header cell to render
                                        # * @return the default table header cell renderer
                                        # */

                                        def getTableCellRendererComponent(self, table, value, isSelected, hasFocus, row, column):	# noqa
                                            # noinspection PyUnresolvedReferences
                                            super(DefaultTableHeaderCellRenderer, self).getTableCellRendererComponent(table, value, isSelected,hasFocus, row, column)
                                            # tableHeader = table.getTableHeader()
                                            # if (tableHeader is not None): self.setForeground(tableHeader.getForeground())
                                            align = table.getCellRenderer(0, column).getHorizontalAlignment()
                                            self.setHorizontalAlignment(align)
                                            if align == JLabel.RIGHT:
                                                self.setHorizontalTextPosition(JLabel.RIGHT)
                                            elif align == JLabel.LEFT:
                                                self.setHorizontalTextPosition(JLabel.LEFT)
                                            elif align == JLabel.CENTER:
                                                self.setHorizontalTextPosition(JLabel.LEFT)

                                            self.setIcon(self._getIcon(table, column))
                                            self.setBorder(UIManager.getBorder("TableHeader.cellBorder"))

                                            self.setForeground(MD_REF.getUI().getColors().headerFG)
                                            self.setBackground(MD_REF.getUI().getColors().headerBG1)

                                            # self.setHorizontalAlignment(JLabel.CENTER)

                                            return self

                                        # enddef

                                        # /**
                                        # * Overloaded to return an icon suitable to the primary sorted column, or null if
                                        # * the column is not the primary sort key.
                                        # *
                                        # * @param table the <code>JTable</code>.
                                        # * @param column the column index.
                                        # * @return the sort icon, or null if the column is unsorted.
                                        # */
                                        def _getIcon(self, table, column):															# noqa
                                            sortKey = self.getSortKey(table, column)
                                            if (sortKey is not None and table.convertColumnIndexToView(sortKey.getColumn()) == column):
                                                x = (sortKey.getSortOrder())
                                                if x == SortOrder.ASCENDING: return UIManager.getIcon("Table.ascendingSortIcon")
                                                elif x == SortOrder.DESCENDING: return UIManager.getIcon("Table.descendingSortIcon")
                                                elif x == SortOrder.UNSORTED: return UIManager.getIcon("Table.naturalSortIcon")
                                            return None

                                        # enddef

                                        # /**
                                        # * returns the current sort key, or null if the column is unsorted.
                                        # *
                                        # * @param table the table
                                        # * @param column the column index
                                        # * @return the SortKey, or null if the column is unsorted
                                        # */
                                        # noinspection PyMethodMayBeStatic
                                        # noinspection PyUnusedLocal
                                        def getSortKey(self, table, column):														# noqa
                                            rowSorter = table.getRowSorter()
                                            if (rowSorter is None): return None
                                            sortedColumns = rowSorter.getSortKeys()
                                            if (sortedColumns.size() > 0): return sortedColumns.get(0)
                                            return None

                                    focus = "initial"
                                    row = 0
                                    EditedReminderCheck = False
                                    ReminderTable_Count = 0
                                    ExtractDetails_Count = 0

                                    class CloseAction(AbstractAction):
                                        # noinspection PyMethodMayBeStatic
                                        # noinspection PyUnusedLocal
                                        def actionPerformed(self, event):
                                            myPrint("D", _THIS_EXTRACT_NAME + "In ", inspect.currentframe().f_code.co_name, "()")

                                            terminate_script()

                                    class PrintJTable(AbstractAction):
                                        def __init__(self, _frame, _table, _title):
                                            self._frame = _frame
                                            self._table = _table
                                            self._title = _title

                                        def actionPerformed(self, event):                                                           # noqa
                                            printJTable(_theFrame=self._frame, _theJTable=self._table, _theTitle=self._title)

                                    class WindowListener(WindowAdapter):
                                        def __init__(self, theFrame):
                                            self.theFrame = theFrame        # type: MyJFrame

                                        def windowClosing(self, WindowEvent):                                                       # noqa
                                            myPrint("DB", _THIS_EXTRACT_NAME + "In ", inspect.currentframe().f_code.co_name, "()")

                                            terminate_script()

                                        def windowClosed(self, WindowEvent):                                                        # noqa
                                            myPrint("DB", _THIS_EXTRACT_NAME + "In ", inspect.currentframe().f_code.co_name, "()")
                                            myPrint("DB", _THIS_EXTRACT_NAME + "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

                                            self.theFrame.isActiveInMoneydance = False

                                            myPrint("DB", _THIS_EXTRACT_NAME + "applistener is %s" %(classPrinter("MoneydanceAppListener", self.theFrame.MoneydanceAppListener)))

                                            if self.theFrame.MoneydanceAppListener is not None:
                                                try:
                                                    MD_REF.removeAppEventListener(self.theFrame.MoneydanceAppListener)
                                                    myPrint("DB", _THIS_EXTRACT_NAME + "\n@@@ Removed my MD App Listener... %s\n" %(classPrinter("MoneydanceAppListener", self.theFrame.MoneydanceAppListener)))
                                                    self.theFrame.MoneydanceAppListener = None
                                                except:
                                                    myPrint("B", _THIS_EXTRACT_NAME + "FAILED to remove my MD App Listener... %s" %(classPrinter("MoneydanceAppListener", self.theFrame.MoneydanceAppListener)))
                                                    dump_sys_error_to_md_console_and_errorlog()

                                            if self.theFrame.HomePageViewObj is not None:
                                                self.theFrame.HomePageViewObj.unload()
                                                myPrint("DB", _THIS_EXTRACT_NAME + "@@ Called HomePageView.unload() and Removed reference to HomePageView %s from MyJFrame()...@@\n" %(classPrinter("HomePageView", self.theFrame.HomePageViewObj)))
                                                self.theFrame.HomePageViewObj = None

                                            cleanup_actions(self.theFrame)

                                        # noinspection PyMethodMayBeStatic
                                        # noinspection PyUnusedLocal
                                        def windowGainedFocus(self, WindowEvent):                                                   # noqa
                                            global focus, row, EditedReminderCheck

                                            myPrint("D", _THIS_EXTRACT_NAME + "In ", inspect.currentframe().f_code.co_name, "()")

                                            if focus == "lost":
                                                focus = "gained"
                                                if EditedReminderCheck:  # Disable refresh data on all gained-focus events, just refresh if Reminder is Edited...
                                                    # To always refresh data remove this if statement and always run ExtractDetails(1)
                                                    myPrint("DB", _THIS_EXTRACT_NAME + "pre-build_the_data_file()")
                                                    build_the_data_file(1)  # Re-extract data when window focus gained - assume something changed
                                                    myPrint("DB", _THIS_EXTRACT_NAME + "back from build_the_data_file(), gained focus, row: ", row)
                                                    EditedReminderCheck = False
                                                GlobalVars.table.setRowSelectionInterval(0, row)
                                                cellRect = GlobalVars.table.getCellRect(row, 0, True)
                                                GlobalVars.table.scrollRectToVisible(cellRect)  # force the scrollpane to make the row visible
                                                GlobalVars.table.requestFocus()

                                            myPrint("D", _THIS_EXTRACT_NAME + "Exiting ", inspect.currentframe().f_code.co_name, "()")
                                            return

                                        # noinspection PyMethodMayBeStatic
                                        # noinspection PyUnusedLocal
                                        def windowLostFocus(self, WindowEvent):                                         # noqa
                                            global focus, debug

                                            myPrint("D", _THIS_EXTRACT_NAME + "In ", inspect.currentframe().f_code.co_name, "()")

                                            if focus == "gained": focus = "lost"

                                            myPrint("D", _THIS_EXTRACT_NAME + "Exiting ", inspect.currentframe().f_code.co_name, "()")

                                    WL = WindowListener(extract_data_frame_)

                                    class MouseListener(MouseAdapter):

                                        # noinspection PyMethodMayBeStatic
                                        def mouseClicked(self, event):
                                            global row
                                            myPrint("D", _THIS_EXTRACT_NAME + "In ", inspect.currentframe().f_code.co_name, "()")

                                            # Select the row when right-click initiated
                                            point = event.getPoint()
                                            row = GlobalVars.table.rowAtPoint(point)
                                            GlobalVars.table.setRowSelectionInterval(row, row)
                                            myPrint("D", _THIS_EXTRACT_NAME + "Exiting ", inspect.currentframe().f_code.co_name, "()")

                                        # noinspection PyMethodMayBeStatic
                                        def mousePressed(self, event):
                                            global row
                                            myPrint("D", _THIS_EXTRACT_NAME + "In ", inspect.currentframe().f_code.co_name, "()")
                                            clicks = event.getClickCount()
                                            if clicks == 2:
                                                row = GlobalVars.table.getSelectedRow()
                                                index = GlobalVars.table.getValueAt(row, 0)
                                                ShowEditForm(index)
                                            myPrint("D", _THIS_EXTRACT_NAME + "Exiting ", inspect.currentframe().f_code.co_name, "()")

                                    ML = MouseListener()

                                    class EnterAction(AbstractAction):
                                        # noinspection PyMethodMayBeStatic
                                        # noinspection PyUnusedLocal
                                        def actionPerformed(self, event):
                                            global focus, row, debug
                                            myPrint("D", _THIS_EXTRACT_NAME + "In ", inspect.currentframe().f_code.co_name, "()")
                                            row = GlobalVars.table.getSelectedRow()
                                            index = GlobalVars.table.getValueAt(row, 0)
                                            ShowEditForm(index)
                                            myPrint("D", _THIS_EXTRACT_NAME + "Exiting ", inspect.currentframe().f_code.co_name, "()")
                                            return

                                    class NoExtractMenuJustCloseAction():
                                        def __init__(self): pass

                                        # noinspection PyMethodMayBeStatic
                                        def no_extract_just_close(self):
                                            myPrint("D", _THIS_EXTRACT_NAME + "In ", inspect.currentframe().f_code.co_name, "()")
                                            myPrint("D", _THIS_EXTRACT_NAME + "inside NoExtractMenuJustCloseAction() ;->")

                                            terminate_script()

                                    class RefreshMenuAction():
                                        def __init__(self): pass

                                        # noinspection PyMethodMayBeStatic
                                        def refresh(self):
                                            global row

                                            row = 0  # reset to row 1
                                            myPrint("D", _THIS_EXTRACT_NAME + "In ", inspect.currentframe().f_code.co_name, "()", "\npre-extract details(1), row: ", row)
                                            build_the_data_file(1)  # Re-extract data
                                            myPrint("D", _THIS_EXTRACT_NAME + "back from extractdetails(1), row: ", row)
                                            GlobalVars.table.setRowSelectionInterval(0, row)
                                            GlobalVars.table.requestFocus()
                                            myPrint("D", _THIS_EXTRACT_NAME + "Exiting ", inspect.currentframe().f_code.co_name, "()")
                                            return

                                    class MyJTable(JTable):
                                        myPrint("D", _THIS_EXTRACT_NAME + "In ", inspect.currentframe().f_code.co_name, "()")

                                        def __init__(self, tableModel):
                                            global debug
                                            super(JTable, self).__init__(tableModel)
                                            self.fixTheRowSorter()

                                        # noinspection PyMethodMayBeStatic
                                        # noinspection PyUnusedLocal
                                        def isCellEditable(self, row, column):														# noqa
                                            return False

                                        #  Rendering depends on row (i.e. security's currency) as well as column
                                        # noinspection PyUnusedLocal
                                        # noinspection PyMethodMayBeStatic
                                        def getCellRenderer(self, row, column):														# noqa
                                            global headerFormats

                                            if column == 0:
                                                renderer = MyPlainNumberRenderer()

                                            elif headerFormats[column][0] == Number:
                                                renderer = MyNumberRenderer()
                                            else:
                                                renderer = DefaultTableCellRenderer()

                                            renderer.setHorizontalAlignment(headerFormats[column][1])

                                            return renderer

                                        class MyTextNumberComparator(Comparator):
                                            lSortNumber = False
                                            lSortRealNumber = False

                                            def __init__(self, sortType):
                                                if sortType == "N":
                                                    self.lSortNumber = True
                                                elif sortType == "%":
                                                    self.lSortRealNumber = True
                                                else:
                                                    self.lSortNumber = False

                                            def compare(self, str1, str2):
                                                validString = "-0123456789" + GlobalVars.decimalCharSep  # Yes this will strip % sign too, but that still works

                                                if isinstance(str1, StoreDateInt) or isinstance(str2, StoreDateInt):
                                                    if str1.getDateInt() > str2.getDateInt():
                                                        return 1
                                                    elif str1.getDateInt() == str2.getDateInt():
                                                        return 0
                                                    else:
                                                        return -1

                                                if isinstance(str1, (float,int)) or isinstance(str2,(float,int)):
                                                    if str1 is None or str1 == "": str1 = 0
                                                    if str2 is None or str2 == "": str2 = 0
                                                    if (str1) > (str2):
                                                        return 1
                                                    elif str1 == str2:
                                                        return 0
                                                    else:
                                                        return -1

                                                if self.lSortNumber:
                                                    # strip non numerics from string so can convert back to float - yes, a bit of a reverse hack
                                                    conv_string1 = ""
                                                    if str1 is None or str1 == "": str1 = "0"
                                                    if str2 is None or str2 == "": str2 = "0"
                                                    for char in str1:
                                                        if char in validString:
                                                            conv_string1 = conv_string1 + char

                                                    conv_string2 = ""
                                                    for char in str2:
                                                        if char in validString:
                                                            conv_string2 = conv_string2 + char
                                                    str1 = float(conv_string1)
                                                    str2 = float(conv_string2)

                                                    if str1 > str2:
                                                        return 1
                                                    elif str1 == str2:
                                                        return 0
                                                    else:
                                                        return -1
                                                elif self.lSortRealNumber:
                                                    if float(str1) > float(str2):
                                                        return 1
                                                    elif str1 == str2:
                                                        return 0
                                                    else:
                                                        return -1
                                                else:
                                                    if str1.upper() > str2.upper():
                                                        return 1
                                                    elif str1.upper() == str2.upper():
                                                        return 0
                                                    else:
                                                        return -1

                                        def fixTheRowSorter(self):  # by default everything gets converted to strings. We need to fix this and code for my string number formats

                                            sorter = TableRowSorter()
                                            self.setRowSorter(sorter)
                                            sorter.setModel(self.getModel())
                                            for _iii in range(0, self.getColumnCount()):
                                                if _iii == 0:
                                                    sorter.setComparator(_iii, self.MyTextNumberComparator("%"))
                                                if _iii == 9 or _iii == 14:
                                                    sorter.setComparator(_iii, self.MyTextNumberComparator("N"))
                                                else:
                                                    sorter.setComparator(_iii, self.MyTextNumberComparator("T"))
                                            self.getRowSorter().toggleSortOrder(0)

                                        # make Banded rows
                                        def prepareRenderer(self, renderer, row, column):  											# noqa

                                            # noinspection PyUnresolvedReferences
                                            component = super(MyJTable, self).prepareRenderer(renderer, row, column)
                                            if not self.isRowSelected(row):
                                                component.setBackground(MD_REF.getUI().getColors().registerBG1 if row % 2 == 0 else MD_REF.getUI().getColors().registerBG2)

                                            return component

                                    # This copies the standard class and just changes the colour to RED if it detects a negative - leaves field intact
                                    # noinspection PyArgumentList
                                    class MyNumberRenderer(DefaultTableCellRenderer):

                                        def __init__(self):
                                            super(DefaultTableCellRenderer, self).__init__()

                                        def setValue(self, value):
                                            if isinstance(value, (float,int)):
                                                if value < 0.0:
                                                    self.setForeground(MD_REF.getUI().getColors().budgetAlertColor)
                                                else:
                                                    self.setForeground(MD_REF.getUI().getColors().budgetHealthyColor)
                                                base = MD_REF.getCurrentAccountBook().getCurrencies().getBaseType()
                                                self.setText(base.formatFancy(int(value*100), GlobalVars.decimalCharSep, True))
                                            else:
                                                if isinstance(value, StoreDateInt):
                                                    self.setText(value.getDateIntFormatted())
                                                else:
                                                    self.setText(str(value))

                                            return

                                    class MyPlainNumberRenderer(DefaultTableCellRenderer):
                                        def __init__(self):
                                            super(DefaultTableCellRenderer, self).__init__()                                        # noqa

                                        def setValue(self, value):
                                            if isinstance(value, StoreDateInt):
                                                self.setText(value.getDateIntFormatted())
                                            else:
                                                self.setText(str(value))

                                    def ReminderTable(tabledata, ind):
                                        global row, ReminderTable_Count, csvheaderline
                                        global _column_widths_ERTC, lExtractFutureRemindersToo_ERTC

                                        ReminderTable_Count += 1
                                        myPrint("D", _THIS_EXTRACT_NAME + "In ", inspect.currentframe().f_code.co_name, "()", ind, "  - On iteration/call: ", ReminderTable_Count)

                                        myDefaultWidths = [70,95,110,150,150,95,95,95,120,100,80,100,150,50,100,150,150,150]

                                        validCount=0
                                        lInvalidate=True
                                        if _column_widths_ERTC is not None and isinstance(_column_widths_ERTC,(list)) and len(_column_widths_ERTC) == len(myDefaultWidths):
                                            # if sum(_column_widths_ERTC)<1:
                                            for width in _column_widths_ERTC:
                                                if width >= 0 and width <= 1000:													# noqa
                                                    validCount += 1

                                        if validCount == len(myDefaultWidths): lInvalidate=False

                                        if lInvalidate:
                                            myPrint("DB", _THIS_EXTRACT_NAME + "Found invalid saved columns = resetting to defaults")
                                            myPrint("DB", _THIS_EXTRACT_NAME + "Found: %s" %_column_widths_ERTC)
                                            myPrint("DB", _THIS_EXTRACT_NAME + "Resetting to: %s" %myDefaultWidths)
                                            _column_widths_ERTC = myDefaultWidths
                                        else:
                                            myPrint("DB", _THIS_EXTRACT_NAME + "Valid column widths loaded - Setting to: %s" %_column_widths_ERTC)
                                            myDefaultWidths = _column_widths_ERTC


                                        # allcols = col0 + col1 + col2 + col3 + col4 + col5 + col6 + col7 + col8 + col9 + col10 + col11 + col12 + col13 + col14 + col15 + col16 + col17
                                        allcols = sum(myDefaultWidths)

                                        screenSize = Toolkit.getDefaultToolkit().getScreenSize()

                                        # button_width = 220
                                        # button_height = 40
                                        # frame_width = min(screenSize.width-20, allcols + 100)
                                        # frame_height = min(screenSize.height, 900)

                                        frame_width = min(screenSize.width-20, max(1024,int(round(GetFirstMainFrame.getSize().width *.95,0))))
                                        frame_height = min(screenSize.height-20, max(768, int(round(GetFirstMainFrame.getSize().height *.95,0))))

                                        frame_width = min( allcols+100, frame_width)

                                        # panel_width = frame_width - 50
                                        # button_panel_height = button_height + 5

                                        if ind == 1:    GlobalVars.scrollpane.getViewport().remove(GlobalVars.table)  # On repeat, just remove/refresh the table & rebuild the viewport

                                        colnames = csvheaderline

                                        GlobalVars.table = MyJTable(DefaultTableModel(tabledata, colnames))

                                        if ind == 0:  # Function can get called multiple times; only set main frames up once

                                            # JFrame.setDefaultLookAndFeelDecorated(True)   # Note: Darcula Theme doesn't like this and seems to be OK without this statement...
                                            # extract_data_frame_ = JFrame("extract_data(Reminders) - StuWareSoftSystems(build: %s)..." % version_build)

                                            titleExtraTxt = u"" if not isPreviewBuild() else u"<PREVIEW BUILD: %s>" %(version_build)

                                            extract_data_frame_.setTitle(u"Extract Reminders...   %s" %(titleExtraTxt))
                                            extract_data_frame_.setName(u"%s_main_reminders" %myModuleID)
                                            # extract_data_frame_.setLayout(FlowLayout())

                                            if (not Platform.isMac()):
                                                MD_REF.getUI().getImages()
                                                extract_data_frame_.setIconImage(MDImages.getImage(MD_REF.getSourceInformation().getIconResource()))

                                            # extract_data_frame_.setPreferredSize(Dimension(frame_width, frame_height))
                                            # extract_data_frame_.setExtendedState(JFrame.MAXIMIZED_BOTH)

                                            extract_data_frame_.setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE)

                                            shortcut = Toolkit.getDefaultToolkit().getMenuShortcutKeyMaskEx()

                                            # Add standard CMD-W keystrokes etc to close window
                                            extract_data_frame_.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_W, shortcut),  "close-window")
                                            extract_data_frame_.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_F4, shortcut), "close-window")
                                            extract_data_frame_.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_P, shortcut),  "print-me")

                                            if lAllowEscapeExitApp_SWSS:
                                                extract_data_frame_.getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0), "close-window")

                                            extract_data_frame_.getRootPane().getActionMap().put("close-window", CloseAction())

                                            extract_data_frame_.addWindowFocusListener(WL)
                                            extract_data_frame_.addWindowListener(WL)

                                            if Platform.isOSX():
                                                save_useScreenMenuBar= System.getProperty("apple.laf.useScreenMenuBar")
                                                if save_useScreenMenuBar is None or save_useScreenMenuBar == "":
                                                    save_useScreenMenuBar= System.getProperty("com.apple.macos.useScreenMenuBar")
                                                System.setProperty("apple.laf.useScreenMenuBar", "false")
                                                System.setProperty("com.apple.macos.useScreenMenuBar", "false")
                                            else:
                                                save_useScreenMenuBar = "true"

                                            SetupMDColors.updateUI()

                                            printButton = JButton("Print")
                                            printButton.setToolTipText("Prints the output displayed in this window to your printer")
                                            printButton.setOpaque(SetupMDColors.OPAQUE)
                                            printButton.setBackground(SetupMDColors.BACKGROUND); printButton.setForeground(SetupMDColors.FOREGROUND)
                                            printButton.addActionListener(PrintJTable(extract_data_frame_, GlobalVars.table, "Extract Reminders"))

                                            mb = JMenuBar()

                                            menuO = JMenu("<html><B>MENU</b></html>")
                                            # menuO = JMenu("OPTIONS")
                                            menuO.setForeground(SetupMDColors.FOREGROUND_REVERSED); menuO.setBackground(SetupMDColors.BACKGROUND_REVERSED)

                                            menuItemA = JMenuItem("About")
                                            menuItemA.setToolTipText("About...")
                                            menuItemA.addActionListener(DoTheMenu())
                                            menuO.add(menuItemA)

                                            menuItemR = JMenuItem("Refresh Data/Default Sort")
                                            menuItemR.setToolTipText("Refresh (re-extract) the data, revert to default sort  order....")
                                            menuItemR.addActionListener(DoTheMenu())
                                            menuO.add(menuItemR)

                                            menuItemPS = JMenuItem("Page Setup")
                                            menuItemPS.setToolTipText("Printer Page Setup....")
                                            menuItemPS.addActionListener(DoTheMenu())
                                            menuO.add(menuItemPS)

                                            menuItemEsc = JCheckBoxMenuItem("Allow Escape to Exit")
                                            menuItemEsc.setToolTipText("When enabled, allows the Escape key to exit the main screen")
                                            menuItemEsc.addActionListener(DoTheMenu())
                                            menuItemEsc.setSelected(lAllowEscapeExitApp_SWSS)
                                            menuO.add(menuItemEsc)

                                            menuItemC = JMenuItem("Close Window")
                                            menuItemC.setToolTipText("Exit and close the window")
                                            menuItemC.addActionListener(DoTheMenu())
                                            menuO.add(menuItemC)

                                            mb.add(menuO)

                                            mb.add(Box.createHorizontalGlue())
                                            mb.add(printButton)
                                            mb.add(Box.createRigidArea(Dimension(10, 0)))

                                            extract_data_frame_.setJMenuBar(mb)

                                            if Platform.isOSX():
                                                System.setProperty("apple.laf.useScreenMenuBar", save_useScreenMenuBar)
                                                System.setProperty("com.apple.macos.useScreenMenuBar", save_useScreenMenuBar)

                                        # As the JTable is new each time, add this here....
                                        extract_data_frame_.getRootPane().getActionMap().remove("print-me")
                                        extract_data_frame_.getRootPane().getActionMap().put("print-me", PrintJTable(extract_data_frame_, GlobalVars.table, "Extract Reminders"))

                                        GlobalVars.table.getTableHeader().setReorderingAllowed(True)  # no more drag and drop columns, it didn't work (on the footer)
                                        GlobalVars.table.getTableHeader().setDefaultRenderer(DefaultTableHeaderCellRenderer())
                                        GlobalVars.table.selectionMode = ListSelectionModel.SINGLE_SELECTION

                                        fontSize = GlobalVars.table.getFont().getSize()+5
                                        GlobalVars.table.setRowHeight(fontSize)
                                        GlobalVars.table.setRowMargin(0)

                                        GlobalVars.table.getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke("ENTER"), "Enter")
                                        GlobalVars.table.getActionMap().put("Enter", EnterAction())

                                        for _iii in range(0, GlobalVars.table.getColumnModel().getColumnCount()):
                                            GlobalVars.table.getColumnModel().getColumn(_iii).setPreferredWidth(myDefaultWidths[_iii])

                                        cListener1 = ColumnChangeListener(GlobalVars.table)
                                        # Put the listener here - else it sets the defaults wrongly above....
                                        GlobalVars.table.getColumnModel().addColumnModelListener(cListener1)

                                        # GlobalVars.table.getTableHeader().setBackground(Color.LIGHT_GRAY)

                                        # GlobalVars.table.setAutoCreateRowSorter(True) # DON'T DO THIS - IT WILL OVERRIDE YOUR NICE CUSTOM SORT


                                        popupMenu = JPopupMenu()
                                        showDetails = JMenuItem("Show Reminder's raw details")
                                        showDetails.addActionListener(DoTheMenu())
                                        popupMenu.add(showDetails)

                                        GlobalVars.table.addMouseListener(ML)
                                        GlobalVars.table.setComponentPopupMenu(popupMenu)

                                        if ind == 0:
                                            GlobalVars.scrollpane = JScrollPane(JScrollPane.VERTICAL_SCROLLBAR_ALWAYS, JScrollPane.HORIZONTAL_SCROLLBAR_ALWAYS)  # On first call, create the scrollpane
                                            GlobalVars.scrollpane.setBorder(CompoundBorder(MatteBorder(1, 1, 1, 1, MD_REF.getUI().getColors().hudBorderColor), EmptyBorder(0, 0, 0, 0)))
                                        # GlobalVars.scrollpane.setPreferredSize(Dimension(frame_width-20, frame_height-20	))

                                        GlobalVars.table.setPreferredScrollableViewportSize(Dimension(frame_width-20, frame_height-100))
                                        #
                                        GlobalVars.table.setAutoResizeMode(JTable.AUTO_RESIZE_OFF)
                                        #
                                        GlobalVars.scrollpane.setViewportView(GlobalVars.table)
                                        if ind == 0:
                                            extract_data_frame_.add(GlobalVars.scrollpane)
                                            extract_data_frame_.pack()
                                            extract_data_frame_.setLocationRelativeTo(None)

                                            try:
                                                extract_data_frame_.MoneydanceAppListener = MyMoneydanceEventListener(extract_data_frame_)
                                                MD_REF.addAppEventListener(extract_data_frame_.MoneydanceAppListener)
                                                myPrint("DB", _THIS_EXTRACT_NAME + "@@ added AppEventListener() %s @@" %(classPrinter("MoneydanceAppListener", extract_data_frame_.MoneydanceAppListener)))
                                            except:
                                                myPrint("B", _THIS_EXTRACT_NAME + "FAILED to add MD App Listener...")
                                                dump_sys_error_to_md_console_and_errorlog()

                                            extract_data_frame_.isActiveInMoneydance = True

                                        # Already within the EDT
                                        extract_data_frame_.setVisible(True)
                                        extract_data_frame_.toFront()

                                        myPrint("D", _THIS_EXTRACT_NAME + "Exiting ", inspect.currentframe().f_code.co_name, "()")
                                        ReminderTable_Count -= 1

                                        return

                                    def ShowEditForm(item):
                                        global EditedReminderCheck

                                        myPrint("D", _THIS_EXTRACT_NAME + "In ", inspect.currentframe().f_code.co_name, "()")
                                        reminders = MD_REF.getCurrentAccountBook().getReminders()
                                        reminder = reminders.getAllReminders()[item-1]
                                        myPrint("D", _THIS_EXTRACT_NAME + "Calling MD EditRemindersWindow() function...")

                                        # EditRemindersWindow.editReminder(None, MD_REF.getUI(), reminder)

                                        r = reminder
                                        book = MD_REF.getCurrentAccountBook()
                                        reminderSet = MD_REF.getUI().getCurrentBook().getReminders()
                                        # noinspection PyUnresolvedReferences
                                        if r.getReminderType() == Reminder.Type.TRANSACTION:
                                            if r.isLoanReminder():
                                                win = LoanTxnReminderInfoWindow(MD_REF.getUI(), extract_data_frame_, r, book, r.getTransaction().getSplit(0).getAccount())
                                            else:
                                                win = TxnReminderInfoWindow(MD_REF.getUI(), extract_data_frame_, r, reminderSet.getAccountBook())
                                        # noinspection PyUnresolvedReferences
                                        elif r.getReminderType() == Reminder.Type.NOTE:
                                            win = BasicReminderInfoWindow(MD_REF.getUI(), r, reminderSet, extract_data_frame_)
                                        else: raise Exception("Unknown reminder class: " + r.getClass())

                                        try: win.setEscapeKeyCancels(True)
                                        except: pass

                                        win.setVisible(True)

                                        EditedReminderCheck = True

                                        myPrint("D", _THIS_EXTRACT_NAME + "Exiting ", inspect.currentframe().f_code.co_name, "()")
                                        return

                                    if build_the_data_file(0):

                                        if GlobalVars.EXTRACT_DATA:
                                            def ExtractDataToFile():
                                                global csvDelimiter
                                                global userdateformat, csvheaderline
                                                global lWriteBOMToExportFile_SWSS

                                                myPrint("D", _THIS_EXTRACT_NAME + "In ", inspect.currentframe().f_code.co_name, "()")

                                                # noinspection PyUnreachableCode
                                                if False:
                                                    GlobalVars.csvlines_reminders = sorted(GlobalVars.csvlines_reminders, key=lambda x: (str(x[1]).upper()))

                                                GlobalVars.csvlines_reminders.insert(0, csvheaderline)  # Insert Column Headings at top of list. A bit rough and ready, not great coding, but a short list...!

                                                myPrint("B", _THIS_EXTRACT_NAME + "Opening file and writing %s records" %(len(GlobalVars.csvlines_reminders)))

                                                try:
                                                    # CSV Writer will take care of special characters / delimiters within fields by wrapping in quotes that Excel will decode
                                                    with open(GlobalVars.csvfilename, "wb") as csvfile:  # PY2.7 has no newline parameter so opening in binary; just use "w" and newline='' in PY3.0

                                                        if lWriteBOMToExportFile_SWSS:
                                                            csvfile.write(codecs.BOM_UTF8)   # This 'helps' Excel open file with double-click as UTF-8

                                                        writer = csv.writer(csvfile, dialect='excel', quoting=csv.QUOTE_MINIMAL, delimiter=fix_delimiter(csvDelimiter))

                                                        if csvDelimiter != ",":
                                                            writer.writerow(["sep=",""])  # Tells Excel to open file with the alternative delimiter (it will add the delimiter to this line)

                                                        for _iii in range(0, len(GlobalVars.csvlines_reminders)):
                                                            # Write the table, but swap in the raw numbers (rather than formatted number strings)
                                                            try:

                                                                if _iii == 0:
                                                                    f1 = fixFormatsStr(GlobalVars.csvlines_reminders[_iii][1], True)
                                                                    f5 = fixFormatsStr(GlobalVars.csvlines_reminders[_iii][5], True)
                                                                    f6 = fixFormatsStr(GlobalVars.csvlines_reminders[_iii][6], True)
                                                                    f7 = fixFormatsStr(GlobalVars.csvlines_reminders[_iii][7], True)
                                                                else:
                                                                    f1 = GlobalVars.csvlines_reminders[_iii][1].getDateIntFormatted()
                                                                    f5 = GlobalVars.csvlines_reminders[_iii][5].getDateIntFormatted()
                                                                    f6 = GlobalVars.csvlines_reminders[_iii][6].getDateIntFormatted()
                                                                    f7 = GlobalVars.csvlines_reminders[_iii][7].getDateIntFormatted()

                                                                writer.writerow([
                                                                    fixFormatsStr(GlobalVars.csvlines_reminders[_iii][0], False),
                                                                    f1,
                                                                    fixFormatsStr(GlobalVars.csvlines_reminders[_iii][2], False),
                                                                    fixFormatsStr(GlobalVars.csvlines_reminders[_iii][3], False),
                                                                    fixFormatsStr(GlobalVars.csvlines_reminders[_iii][4], False),
                                                                    f5,
                                                                    f6,
                                                                    f7,
                                                                    fixFormatsStr(GlobalVars.csvlines_reminders[_iii][8], False),
                                                                    fixFormatsStr(GlobalVars.csvlines_reminders[_iii][9], True),
                                                                    fixFormatsStr(GlobalVars.csvlines_reminders[_iii][10], False),
                                                                    fixFormatsStr(GlobalVars.csvlines_reminders[_iii][11], False),
                                                                    fixFormatsStr(GlobalVars.csvlines_reminders[_iii][12], False),
                                                                    fixFormatsStr(GlobalVars.csvlines_reminders[_iii][13], False),
                                                                    fixFormatsStr(GlobalVars.csvlines_reminders[_iii][14], True),
                                                                    fixFormatsStr(GlobalVars.csvlines_reminders[_iii][15], False),
                                                                    fixFormatsStr(GlobalVars.csvlines_reminders[_iii][16], False),
                                                                    fixFormatsStr(GlobalVars.csvlines_reminders[_iii][17], False),
                                                                    ""])
                                                            except:
                                                                _msgTxt = _THIS_EXTRACT_NAME + "@@ ERROR writing to CSV on row %s. Please review console" %(_iii)
                                                                GlobalVars.AUTO_MESSAGES.append(_msgTxt)
                                                                myPrint("B", _msgTxt)
                                                                myPrint("B", GlobalVars.csvlines_reminders[_iii])
                                                                raise

                                                        if lWriteParametersToExportFile_SWSS:
                                                            today = Calendar.getInstance()
                                                            writer.writerow([""])
                                                            writer.writerow(["StuWareSoftSystems - " + GlobalVars.thisScriptName + "(build: "
                                                                             + version_build
                                                                             + ")  Moneydance Python Script - Date of Extract: "
                                                                             + str(GlobalVars.sdf.format(today.getTime()))])

                                                            writer.writerow([""])
                                                            writer.writerow(["Dataset path/name: %s" %(MD_REF.getCurrentAccountBook().getRootFolder()) ])

                                                            writer.writerow([""])
                                                            writer.writerow(["User Parameters..."])
                                                            writer.writerow(["Date format................: %s" %(userdateformat)])

                                                    _msgTxt = _THIS_EXTRACT_NAME + "CSV file: '%s' created (%s records)" %(GlobalVars.csvfilename, len(GlobalVars.csvlines_reminders))
                                                    myPrint("B", _msgTxt)
                                                    GlobalVars.AUTO_MESSAGES.append(_msgTxt)
                                                    GlobalVars.countFilesCreated += 1

                                                except:
                                                    e_type, exc_value, exc_traceback = sys.exc_info()                   # noqa
                                                    _msgTxt = _THIS_EXTRACT_NAME + "@@ ERROR '%s' detected writing file: '%s' - Extract ABORTED!" %(exc_value, GlobalVars.csvfilename)
                                                    GlobalVars.AUTO_MESSAGES.append(_msgTxt)
                                                    myPrint("B", _msgTxt)
                                                    raise

                                            def ExtractDataToFile_Future_Reminders():
                                                myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

                                                myPrint("B", _THIS_EXTRACT_NAME + "(Future Reminders) Opening file and writing %s records" %(len(GlobalVars.csvlines_reminders_future)))

                                                try:
                                                    # CSV Writer will take care of special characters / delimiters within fields by wrapping in quotes that Excel will decode
                                                    with open(GlobalVars.csvfilename_future, "wb") as csvfile:  # PY2.7 has no newline parameter so opening in binary; just use "w" and newline='' in PY3.0
                                                        if lWriteBOMToExportFile_SWSS:
                                                            csvfile.write(codecs.BOM_UTF8)   # This 'helps' Excel open file with double-click as UTF-8

                                                        writer = csv.writer(csvfile, dialect='excel', quoting=csv.QUOTE_MINIMAL, delimiter=fix_delimiter(csvDelimiter))

                                                        if csvDelimiter != ",":
                                                            writer.writerow(["sep=",""])  # Tells Excel to open file with the alternative delimiter (it will add the delimiter to this line)

                                                        for iRow in range(0, len(GlobalVars.csvlines_reminders_future)):
                                                            # Write the table, but swap in the raw numbers (rather than formatted number strings)
                                                            try:
                                                                if iRow == 0:
                                                                    writer.writerow(GlobalVars.csvlines_reminders_future[iRow])
                                                                else:
                                                                    future_row = []
                                                                    for iCol in range(0, len(GlobalVars.csvlines_reminders_future[iRow])):
                                                                        colData = GlobalVars.csvlines_reminders_future[iRow][iCol]
                                                                        if isinstance(colData, int) and (len(str(colData)) == 8):
                                                                            writeColData = convertIntDateFormattedString(colData, userdateformat)
                                                                        elif isinstance(colData, (float, int)):
                                                                            writeColData = fixFormatsStr(colData, True)
                                                                        else:
                                                                            writeColData = fixFormatsStr(colData, False)
                                                                        future_row.append(writeColData)

                                                                    future_row.append("")
                                                                    writer.writerow(future_row)
                                                            except:
                                                                _msgTxt = _THIS_EXTRACT_NAME + "(Future Reminders) @@ ERROR writing to CSV on row %s. Please review console" %(iRow)
                                                                GlobalVars.AUTO_MESSAGES.append(_msgTxt)
                                                                myPrint("B", _msgTxt)
                                                                myPrint("B", GlobalVars.csvlines_reminders[iRow])
                                                                raise

                                                    _msgTxt = _THIS_EXTRACT_NAME + "(Future Reminders) CSV file: '%s' created (%s records)" %(GlobalVars.csvfilename_future, len(GlobalVars.csvlines_reminders_future))
                                                    myPrint("B", _msgTxt)
                                                    GlobalVars.AUTO_MESSAGES.append(_msgTxt)
                                                    GlobalVars.countFilesCreated += 1

                                                except:
                                                    e_type, exc_value, exc_traceback = sys.exc_info()                   # noqa
                                                    _msgTxt = _THIS_EXTRACT_NAME + "@@ ERROR '%s' detected writing file: '%s' - Extract ABORTED!" %(exc_value, GlobalVars.csvfilename_future)
                                                    GlobalVars.AUTO_MESSAGES.append(_msgTxt)
                                                    myPrint("B", _msgTxt)
                                                    raise

                                            def fixFormatsStr(theString, lNumber, sFormat=""):
                                                if isinstance(theString, (int,float)):
                                                    lNumber = True

                                                if lNumber is None: lNumber = False
                                                if theString is None: theString = ""

                                                if sFormat == "%" and theString != "":
                                                    theString = "{:.1%}".format(theString)
                                                    return theString

                                                if lNumber: return str(theString)

                                                theString = theString.strip()  # remove leading and trailing spaces

                                                theString = theString.replace("\n", "*")  # remove newlines within fields to keep csv format happy
                                                theString = theString.replace("\t", "*")  # remove tabs within fields to keep csv format happy

                                                if lStripASCII:
                                                    all_ASCII = ''.join(char for char in theString if ord(char) < 128)  # Eliminate non ASCII printable Chars too....
                                                else:
                                                    all_ASCII = theString
                                                return all_ASCII

                                            ExtractDataToFile()                                                         

                                            if not GlobalVars.lGlobalErrorDetected:
                                                _msgTextx = "Extract file CREATED"
                                                myPrint("B", _msgTextx)
                                            else:
                                                _msgTextx = _THIS_EXTRACT_NAME + "ERROR Creating extract (review console for error messages)...."
                                                GlobalVars.AUTO_MESSAGES.append(_msgTextx)

                                            if lExtractFutureRemindersToo_ERTC:
                                                ExtractDataToFile_Future_Reminders()

                                                if not GlobalVars.lGlobalErrorDetected:
                                                    _msgTextx = "Extract file CREATED"
                                                    myPrint("B", _msgTextx)
                                                else:
                                                    _msgTextx = _THIS_EXTRACT_NAME + "(Future Reminders) ERROR Creating extract (review console for error messages)...."
                                                    GlobalVars.AUTO_MESSAGES.append(_msgTextx)

                                    else:
                                        _msgTextx ="@@ You have no reminders to display or extract! @@"
                                        GlobalVars.AUTO_MESSAGES.append(_THIS_EXTRACT_NAME + _msgTextx)
                                        myPrint("B", _THIS_EXTRACT_NAME + _msgTextx)
                                        if not GlobalVars.AUTO_EXTRACT_MODE:
                                            DoExtractsSwingWorker.killPleaseWait()
                                            genericSwingEDTRunner(True, True, myPopupInformationBox, extract_data_frame_, _msgTextx, "Extract Reminders", JOptionPane.WARNING_MESSAGE)

                                        _msgTextx = _THIS_EXTRACT_NAME + "@@ No records selected and no extract file created @@"
                                        GlobalVars.AUTO_MESSAGES.append(_msgTextx)
                                        myPrint("B", _msgTextx)

                                    # delete references to large objects
                                    del GlobalVars.csvlines_reminders

                                try:
                                    do_extract_reminders()
                                except:
                                    GlobalVars.lGlobalErrorDetected = True

                                if GlobalVars.lGlobalErrorDetected:
                                    GlobalVars.countErrorsDuringExtract += 1
                                    _txt = _THIS_EXTRACT_NAME + "@@ ERROR: do_extract_reminders() has failed (review console)!"
                                    GlobalVars.AUTO_MESSAGES.append(_txt)
                                    myPrint("B", _txt)
                                    dump_sys_error_to_md_console_and_errorlog()
                                    if not GlobalVars.AUTO_EXTRACT_MODE:
                                        DoExtractsSwingWorker.killPleaseWait()
                                        genericSwingEDTRunner(True, True, myPopupInformationBox, extract_data_frame_, _txt, "ERROR", JOptionPane.ERROR_MESSAGE)
                                        return False
                            #### ENDIF lExtractReminders ####

                            if lExtractAccountTxns:
                                # ##############################################
                                # EXTRACT_ACCOUNT_REGISTERS_CSV EXECUTION
                                # ##############################################

                                _THIS_EXTRACT_NAME = pad("EXTRACT: Account Registers:", 34)
                                GlobalVars.lGlobalErrorDetected = False

                                if not GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE:
                                    self.super__publish([_THIS_EXTRACT_NAME.strip()])                                   # noqa

                                if GlobalVars.AUTO_EXTRACT_MODE:
                                    GlobalVars.csvfilename = os.path.join(GlobalVars.scriptpath, MD_REF.getCurrentAccountBook().getName() + "_" + GlobalVars.defaultFileName_EAR + ".csv")

                                def do_extract_account_registers():
                                    global lDidIUseAttachmentDir
                                    global dataKeys, attachmentDir, relativePath

                                    global __extract_data, extract_filename
                                    global lStripASCII, csvDelimiter, userdateformat, lWriteBOMToExportFile_SWSS
                                    global hideInactiveAccounts, hideHiddenAccounts, hideHiddenSecurities
                                    global lAllSecurity, filterForSecurity, lAllAccounts, filterForAccounts, lAllCurrency, filterForCurrency
                                    global whichDefaultExtractToRun_SWSS
                                    global lIncludeSubAccounts_EAR, lIncludeOpeningBalances_EAR, lIncludeBalanceAdjustments_EAR, userdateStart_EAR, userdateEnd_EAR, lAllTags_EAR, tagFilter_EAR
                                    global lAllText_EAR, textFilter_EAR, lAllCategories_EAR, categoriesFilter_EAR, lExtractAttachments_EAR, saveDropDownAccountUUID_EAR, saveDropDownDateRange_EAR, lIncludeInternalTransfers_EAR

                                    # noinspection PyArgumentList
                                    class MyAcctFilterEAT(AcctFilter):

                                        def __init__(self,
                                                     _hideInactiveAccounts=True,
                                                     _hideHiddenAccounts=True,
                                                     _lAllAccounts=True,
                                                     _filterForAccounts="ALL",
                                                     _lAllCurrency=True,
                                                     _filterForCurrency="ALL"):
                                            super(AcctFilter, self).__init__()

                                            self._hideHiddenAccounts = _hideHiddenAccounts
                                            self._hideInactiveAccounts = _hideInactiveAccounts
                                            self._lAllAccounts = _lAllAccounts
                                            self._filterForAccounts = _filterForAccounts
                                            self._lAllCurrency = _lAllCurrency
                                            self._filterForCurrency = _filterForCurrency

                                        def matches(self, acct):

                                            # noinspection PyUnresolvedReferences
                                            if not (acct.getAccountType() == Account.AccountType.BANK
                                                    or acct.getAccountType() == Account.AccountType.CREDIT_CARD
                                                    or acct.getAccountType() == Account.AccountType.LOAN
                                                    or acct.getAccountType() == Account.AccountType.LIABILITY
                                                    or acct.getAccountType() == Account.AccountType.ASSET):
                                                return False

                                            if self._hideInactiveAccounts:

                                                # This logic replicates Moneydance AcctFilter.ACTIVE_ACCOUNTS_FILTER
                                                if (acct.getAccountOrParentIsInactive()): return False
                                                if (acct.getHideOnHomePage() and acct.getBalance() == 0): return False

                                            if self._lAllAccounts or (self._filterForAccounts.upper().strip() in acct.getFullAccountName().upper().strip()):
                                                pass
                                            else:
                                                return False

                                            curr = acct.getCurrencyType()
                                            currID = curr.getIDString()
                                            currName = curr.getName()

                                            # All accounts and security records can have currencies
                                            if self._lAllCurrency:
                                                pass
                                            elif (self._filterForCurrency.upper().strip() in currID.upper().strip()):
                                                pass
                                            elif (self._filterForCurrency.upper().strip() in currName.upper().strip()):
                                                pass
                                            else:
                                                return False

                                            # Phew! We made it....
                                            return True
                                        # enddef

                                    def isCategory(theAccount):
                                        theAccountType = theAccount.getAccountType()

                                        # noinspection PyUnresolvedReferences
                                        if (theAccountType == Account.AccountType.INCOME
                                                or theAccountType == Account.AccountType.EXPENSE):
                                            return True

                                        return False

                                    if GlobalVars.dropDownAccount_EAR:
                                        if lIncludeSubAccounts_EAR:
                                            # noinspection PyUnresolvedReferences
                                            validAccountList = ArrayList(GlobalVars.dropDownAccount_EAR.getSubAccounts())
                                        else:
                                            validAccountList = ArrayList()
                                        validAccountList.add(0, GlobalVars.dropDownAccount_EAR)
                                    else:
                                        validAccountList = AccountUtil.allMatchesForSearch(MD_REF.getCurrentAccountBook(),
                                                                                           MyAcctFilterEAT(_hideInactiveAccounts=hideInactiveAccounts,
                                                                                                           _hideHiddenAccounts=hideHiddenAccounts,
                                                                                                           _lAllAccounts=lAllAccounts,
                                                                                                           _filterForAccounts=filterForAccounts,
                                                                                                           _lAllCurrency=lAllCurrency,
                                                                                                           _filterForCurrency=filterForCurrency))

                                    if debug:
                                        myPrint("DB", _THIS_EXTRACT_NAME + "%s Accounts selected in filters" %len(validAccountList))
                                        for element in validAccountList: myPrint("D", _THIS_EXTRACT_NAME + "...selected acct: %s" %element)

                                    # _msg = MyPopUpDialogBox(extract_data_frame_, theStatus="PLEASE WAIT....", theTitle="Building Database", lModal=False)
                                    # _msg.go()

                                    _COLUMN = 0
                                    _HEADING = 1
                                    dataKeys = {
                                        "_ACCOUNTTYPE":             [0,  "AccountType"],
                                        "_ACCOUNT":                 [1,  "Account"],
                                        "_DATE":                    [2,  "Date"],
                                        "_TAXDATE":                 [3,  "TaxDate"],
                                        "_CURR":                    [4,  "Currency"],
                                        "_CHEQUE":                  [5,  "Cheque"],
                                        "_DESC":                    [6,  "Description"],
                                        "_MEMO":                    [7,  "Memo"],
                                        "_CLEARED":                 [8,  "Cleared"],
                                        "_TOTALAMOUNT":             [9,  "TotalAmount"],
                                        "_FOREIGNTOTALAMOUNT":      [10, "ForeignTotalAmount"],
                                        "_PARENTTAGS":              [11, "ParentTags"],
                                        "_PARENTHASATTACHMENTS":    [12, "ParentHasAttachments"],
                                        "_SPLITIDX":                [13, "SplitIndex"],
                                        "_SPLITMEMO":               [14, "SplitMemo"],
                                        "_SPLITCAT":                [15, "SplitCategory"],
                                        "_SPLITAMOUNT":             [16, "SplitAmount"],
                                        "_FOREIGNSPLITAMOUNT":      [17, "ForeignSplitAmount"],
                                        "_SPLITTAGS":               [18, "SplitTags"],
                                        "_ISTRANSFERTOACCT":        [19, "isTransferToAnotherAccount"],
                                        "_ISTRANSFERSELECTED":      [20, "isTransferWithinThisExtract"],
                                        "_SPLITHASATTACHMENTS":     [21, "SplitHasAttachments"],
                                        "_ATTACHMENTLINK":          [22, "AttachmentLink"],
                                        "_ATTACHMENTLINKREL":       [23, "AttachmentLinkRelative"],
                                        "_KEY":                     [24, "Key"],
                                        "_END":                     [25, "_END"]
                                    }

                                    GlobalVars.transactionTable = []

                                    myPrint("DB", _THIS_EXTRACT_NAME, dataKeys)

                                    book = MD_REF.getCurrentAccountBook()

                                    # noinspection PyArgumentList
                                    class MyTxnSearchCostBasisEAT(TxnSearch):

                                        def __init__(self, _validAccounts):
                                            super(TxnSearch, self).__init__()
                                            self._validAccounts = _validAccounts

                                        # noinspection PyMethodMayBeStatic
                                        def matchesAll(self):
                                            return False

                                        def matches(self, _txn):

                                            _txnAcct = _txn.getAccount()

                                            if _txnAcct in self._validAccounts:
                                                return True
                                            else:
                                                return False

                                    txns = book.getTransactionSet().getTransactions(MyTxnSearchCostBasisEAT(validAccountList))

                                    iBal = 0
                                    accountBalances = {}

                                    _local_storage = MD_REF.getCurrentAccountBook().getLocalStorage()
                                    iAttachmentErrors=0

                                    iCount = 0
                                    iCountAttachmentsDownloaded = 0
                                    uniqueFileNumber = 1

                                    def tag_search( searchForTags, theTagListToSearch ):

                                        searchTagList = searchForTags.upper().strip().split(",")

                                        for tag in theTagListToSearch:
                                            for searchTag in searchTagList:
                                                if searchTag in tag.upper().strip():
                                                    return True

                                        return False

                                    def getTotalLocalValue( theTxn ):

                                        lValue = 0

                                        for _iSplit in range(0, (theTxn.getOtherTxnCount())):
                                            lValue += GlobalVars.baseCurrency.getDoubleValue(parent_Txn.getOtherTxn(_iSplit).getValue()) * -1

                                        return lValue

                                    copyValidAccountList = ArrayList()
                                    if lIncludeOpeningBalances_EAR:
                                        for acctBal in validAccountList:
                                            if getUnadjustedStartBalance(acctBal) != 0:
                                                if userdateStart_EAR <= acctBal.getCreationDateInt() <= userdateEnd_EAR:
                                                    copyValidAccountList.add(acctBal)

                                    if lIncludeBalanceAdjustments_EAR:
                                        for acctBal in validAccountList:
                                            if getBalanceAdjustment(acctBal) != 0:
                                                if acctBal not in copyValidAccountList:
                                                    copyValidAccountList.add(acctBal)

                                    for txn in txns:

                                        if not (userdateStart_EAR <= txn.getDateInt() <= userdateEnd_EAR):
                                            continue

                                        lParent = isinstance(txn, ParentTxn)

                                        parent_Txn = txn.getParentTxn()
                                        txnAcct = txn.getAccount()
                                        acctCurr = txnAcct.getCurrencyType()  # Currency of the txn

                                        # Only include opening balances if not filtering records.... (this is caught during parameter selection earlier)
                                        if (lIncludeOpeningBalances_EAR or lIncludeBalanceAdjustments_EAR):
                                            if txnAcct in copyValidAccountList:
                                                copyValidAccountList.remove(txnAcct)

                                            if accountBalances.get(txnAcct):
                                                pass
                                            else:
                                                accountBalances[txnAcct] = True
                                                if (lIncludeOpeningBalances_EAR):
                                                    if userdateStart_EAR <= txnAcct.getCreationDateInt() <= userdateEnd_EAR:
                                                        openBal = acctCurr.getDoubleValue(getUnadjustedStartBalance(txnAcct))
                                                        if openBal != 0:
                                                            iBal += 1
                                                            _row = ([None] * dataKeys["_END"][0])  # Create a blank row to be populated below...
                                                            _row[dataKeys["_KEY"][_COLUMN]] = txnAcct.getUUID()
                                                            _row[dataKeys["_ACCOUNTTYPE"][_COLUMN]] = safeStr(txnAcct.getAccountType())
                                                            _row[dataKeys["_ACCOUNT"][_COLUMN]] = txnAcct.getFullAccountName()
                                                            _row[dataKeys["_CURR"][_COLUMN]] = acctCurr.getIDString()
                                                            _row[dataKeys["_DESC"][_COLUMN]] = "MANUAL (UNADJUSTED) OPENING BALANCE"
                                                            _row[dataKeys["_CHEQUE"][_COLUMN]] = "MANUAL"
                                                            _row[dataKeys["_DATE"][_COLUMN]] = txnAcct.getCreationDateInt()
                                                            _row[dataKeys["_SPLITIDX"][_COLUMN]] = 0
                                                            if acctCurr == GlobalVars.baseCurrency:
                                                                _row[dataKeys["_TOTALAMOUNT"][_COLUMN]] = openBal
                                                                _row[dataKeys["_SPLITAMOUNT"][_COLUMN]] = openBal
                                                            else:
                                                                _row[dataKeys["_TOTALAMOUNT"][_COLUMN]] = round(openBal / acctCurr.getRate(GlobalVars.baseCurrency),2)
                                                                _row[dataKeys["_SPLITAMOUNT"][_COLUMN]] = round(openBal / acctCurr.getRate(GlobalVars.baseCurrency),2)
                                                                _row[dataKeys["_FOREIGNTOTALAMOUNT"][_COLUMN]] = openBal
                                                                _row[dataKeys["_FOREIGNSPLITAMOUNT"][_COLUMN]] = openBal

                                                            myPrint("D", _THIS_EXTRACT_NAME, _row)
                                                            GlobalVars.transactionTable.append(_row)
                                                            del openBal

                                                if (lIncludeBalanceAdjustments_EAR):
                                                    adjBal = acctCurr.getDoubleValue(getBalanceAdjustment(txnAcct))
                                                    if adjBal != 0:
                                                        iBal += 1
                                                        _row = ([None] * dataKeys["_END"][0])  # Create a blank row to be populated below...
                                                        _row[dataKeys["_KEY"][_COLUMN]] = txnAcct.getUUID()
                                                        _row[dataKeys["_ACCOUNTTYPE"][_COLUMN]] = safeStr(txnAcct.getAccountType())
                                                        _row[dataKeys["_ACCOUNT"][_COLUMN]] = txnAcct.getFullAccountName()
                                                        _row[dataKeys["_CURR"][_COLUMN]] = acctCurr.getIDString()
                                                        _row[dataKeys["_DESC"][_COLUMN]] = "MANUAL BALANCE ADJUSTMENT (MD2023 onwards)"
                                                        _row[dataKeys["_CHEQUE"][_COLUMN]] = "MANUAL"
                                                        _row[dataKeys["_DATE"][_COLUMN]] = DateUtil.getStrippedDateInt()
                                                        _row[dataKeys["_SPLITIDX"][_COLUMN]] = 0
                                                        if acctCurr == GlobalVars.baseCurrency:
                                                            _row[dataKeys["_TOTALAMOUNT"][_COLUMN]] = adjBal
                                                            _row[dataKeys["_SPLITAMOUNT"][_COLUMN]] = adjBal
                                                        else:
                                                            _row[dataKeys["_TOTALAMOUNT"][_COLUMN]] = round(adjBal / acctCurr.getRate(GlobalVars.baseCurrency),2)
                                                            _row[dataKeys["_SPLITAMOUNT"][_COLUMN]] = round(adjBal / acctCurr.getRate(GlobalVars.baseCurrency),2)
                                                            _row[dataKeys["_FOREIGNTOTALAMOUNT"][_COLUMN]] = adjBal
                                                            _row[dataKeys["_FOREIGNSPLITAMOUNT"][_COLUMN]] = adjBal


                                                        myPrint("D", _THIS_EXTRACT_NAME, _row)
                                                        GlobalVars.transactionTable.append(_row)
                                                        del adjBal

                                        keyIndex = 0
                                        _row = ([None] * dataKeys["_END"][0])  # Create a blank row to be populated below...

                                        txnKey = txn.getUUID()
                                        _row[dataKeys["_KEY"][_COLUMN]] = txnKey + "-" + str(keyIndex).zfill(3)

                                        _row[dataKeys["_ACCOUNTTYPE"][_COLUMN]] = safeStr(txnAcct.getAccountType())
                                        _row[dataKeys["_ACCOUNT"][_COLUMN]] = txnAcct.getFullAccountName()
                                        _row[dataKeys["_CURR"][_COLUMN]] = acctCurr.getIDString()
                                        _row[dataKeys["_DATE"][_COLUMN]] = txn.getDateInt()
                                        if parent_Txn.getTaxDateInt() != txn.getDateInt():
                                            _row[dataKeys["_TAXDATE"][_COLUMN]] = txn.getTaxDateInt()

                                        _row[dataKeys["_CHEQUE"][_COLUMN]] = txn.getCheckNumber()

                                        _row[dataKeys["_DESC"][_COLUMN]] = parent_Txn.getDescription()
                                        if lParent:
                                            _row[dataKeys["_MEMO"][_COLUMN]] = txn.getMemo()
                                        else:
                                            _row[dataKeys["_MEMO"][_COLUMN]] = txn.getDescription()
                                        _row[dataKeys["_CLEARED"][_COLUMN]] = getStatusCharRevised(txn)


                                        if acctCurr == GlobalVars.baseCurrency:
                                            _row[dataKeys["_TOTALAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(txn.getValue())
                                        else:
                                            if lParent:
                                                _row[dataKeys["_FOREIGNTOTALAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(txn.getValue())
                                                localValue = getTotalLocalValue( txn )
                                                _row[dataKeys["_TOTALAMOUNT"][_COLUMN]] = localValue
                                            else:
                                                _row[dataKeys["_FOREIGNTOTALAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(txn.getValue())
                                                _row[dataKeys["_TOTALAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(txn.getAmount())

                                        _row[dataKeys["_PARENTHASATTACHMENTS"][_COLUMN]] = parent_Txn.hasAttachments()
                                        if str(parent_Txn.getKeywords()) != "[]": _row[dataKeys["_PARENTTAGS"][_COLUMN]] = safeStr(parent_Txn.getKeywords())

                                        lNeedToPrintTotalAmount = True

                                        for _ii in range(0, int(parent_Txn.getOtherTxnCount())):        # If a split, then it will always make it here...

                                            if not lParent and _ii > 0: break

                                            splitRowCopy = deepcopy(_row)

                                            if lParent:

                                                if (not lAllTags_EAR
                                                        and not tag_search(tagFilter_EAR, txn.getKeywords())
                                                        and not tag_search(tagFilter_EAR, parent_Txn.getOtherTxn(_ii).getKeywords())):
                                                    continue

                                                if (not lAllText_EAR
                                                        and textFilter_EAR not in (parent_Txn.getDescription().upper().strip()
                                                                                   +txn.getMemo().upper().strip()
                                                                                   +parent_Txn.getOtherTxn(_ii).getDescription().upper()).strip()):
                                                    continue

                                                # The category logic below was added by IK user @Mark
                                                if (not lAllCategories_EAR):        # Note: we only select Accounts, thus Parents are always Accounts (not categories)
                                                    splitTxnAccount = parent_Txn.getOtherTxn(_ii).getAccount()
                                                    parentAccount = parent_Txn.getAccount()
                                                    if ( (isCategory(parentAccount) and categoriesFilter_EAR in (parentAccount.getFullAccountName().upper().strip()))
                                                            or (isCategory(splitTxnAccount) and categoriesFilter_EAR in (splitTxnAccount.getFullAccountName().upper().strip())) ):
                                                        pass
                                                    else:
                                                        continue

                                                splitMemo = parent_Txn.getOtherTxn(_ii).getDescription()
                                                splitTags = safeStr(parent_Txn.getOtherTxn(_ii).getKeywords())
                                                splitCat = parent_Txn.getOtherTxn(_ii).getAccount().getFullAccountName()
                                                splitHasAttachments = parent_Txn.getOtherTxn(_ii).hasAttachments()

                                                splitFAmount = None
                                                if parent_Txn.getOtherTxn(_ii).getAmount() != parent_Txn.getOtherTxn(_ii).getValue():
                                                    splitFAmount = acctCurr.getDoubleValue(parent_Txn.getOtherTxn(_ii).getValue()) * -1
                                                    splitAmount = acctCurr.getDoubleValue(parent_Txn.getOtherTxn(_ii).getAmount()) * -1
                                                else:
                                                    splitAmount = acctCurr.getDoubleValue(parent_Txn.getOtherTxn(_ii).getValue()) * -1

                                                transferAcct = parent_Txn.getOtherTxn(_ii).getAccount()
                                                transferType = transferAcct.getAccountType()

                                                # noinspection PyUnresolvedReferences
                                                if transferAcct != txnAcct and not (
                                                        transferType == Account.AccountType.ROOT
                                                        or transferType == Account.AccountType.INCOME
                                                        or transferType == Account.AccountType.EXPENSE):
                                                    isTransfer = True
                                                else:
                                                    isTransfer = False

                                                isTransferWithinExtract = (isTransfer and transferAcct in validAccountList)

                                                if splitTags == "[]": splitTags = ""

                                            else:
                                                # ######################################################################################
                                                # We are on a split - which is a standalone transfer in/out
                                                if (not lAllTags_EAR
                                                        and not tag_search(tagFilter_EAR, txn.getKeywords())
                                                        and not tag_search(tagFilter_EAR, parent_Txn.getKeywords())):
                                                    break

                                                if (not lAllText_EAR
                                                        and textFilter_EAR not in (txn.getDescription().upper().strip()
                                                                                   +parent_Txn.getDescription().upper().strip()
                                                                                   +parent_Txn.getMemo().upper().strip())):
                                                    break

                                                # The category logic below was added by IK user @Mark (and amended by me.....)
                                                if (not lAllCategories_EAR):
                                                    parentAcct = parent_Txn.getAccount()
                                                    splitTxnAcct = txn.getAccount()
                                                    if ( (isCategory(parentAcct) and categoriesFilter_EAR in parentAcct.getFullAccountName().upper().strip())
                                                            or (isCategory(splitTxnAcct) and categoriesFilter_EAR in splitTxnAcct.getFullAccountName().upper().strip()) ):
                                                        pass
                                                    else:
                                                        break

                                                splitMemo = txn.getDescription()
                                                splitTags = safeStr(txn.getKeywords())
                                                splitCat = parent_Txn.getAccount().getFullAccountName()
                                                splitHasAttachments = txn.hasAttachments()


                                                splitFAmount = None
                                                if txn.getAmount() != txn.getValue():
                                                    splitFAmount = acctCurr.getDoubleValue(txn.getValue())
                                                    splitAmount = acctCurr.getDoubleValue(txn.getAmount())
                                                else:
                                                    splitAmount = acctCurr.getDoubleValue(txn.getValue())

                                                transferAcct = parent_Txn.getAccount()
                                                transferType = transferAcct.getAccountType()

                                                # noinspection PyUnresolvedReferences
                                                if transferAcct != txnAcct and not (
                                                        transferType == Account.AccountType.ROOT
                                                        or transferType == Account.AccountType.INCOME
                                                        or transferType == Account.AccountType.EXPENSE):
                                                    isTransfer = True
                                                else:
                                                    isTransfer = False

                                                isTransferWithinExtract = (isTransfer and transferAcct in validAccountList)

                                                if splitTags == "[]": splitTags = ""

                                            if lNeedToPrintTotalAmount:
                                                lNeedToPrintTotalAmount = False
                                            else:
                                                splitRowCopy[dataKeys["_TOTALAMOUNT"][_COLUMN]] = None  # Don't repeat this on subsequent rows
                                                splitRowCopy[dataKeys["_FOREIGNTOTALAMOUNT"][_COLUMN]] = None  # Don't repeat this on subsequent rows

                                            splitRowCopy[dataKeys["_KEY"][_COLUMN]] = txnKey + "-" + str(keyIndex).zfill(3)
                                            splitRowCopy[dataKeys["_SPLITIDX"][_COLUMN]] = _ii
                                            splitRowCopy[dataKeys["_SPLITMEMO"][_COLUMN]] = splitMemo
                                            splitRowCopy[dataKeys["_SPLITAMOUNT"][_COLUMN]] = splitAmount
                                            splitRowCopy[dataKeys["_FOREIGNSPLITAMOUNT"][_COLUMN]] = splitFAmount
                                            splitRowCopy[dataKeys["_SPLITTAGS"][_COLUMN]] = splitTags
                                            splitRowCopy[dataKeys["_SPLITCAT"][_COLUMN]] = splitCat
                                            splitRowCopy[dataKeys["_SPLITHASATTACHMENTS"][_COLUMN]] = splitHasAttachments
                                            splitRowCopy[dataKeys["_ISTRANSFERTOACCT"][_COLUMN]] = isTransfer
                                            splitRowCopy[dataKeys["_ISTRANSFERSELECTED"][_COLUMN]] = isTransferWithinExtract

                                            holdTheKeys = ArrayList()
                                            holdTheLocations = ArrayList()

                                            if _ii == 0 and txn.hasAttachments():
                                                # noinspection PyUnresolvedReferences
                                                holdTheKeys = holdTheKeys + txn.getAttachmentKeys()
                                                for _attachKey in txn.getAttachmentKeys():
                                                    # noinspection PyUnresolvedReferences
                                                    holdTheLocations.append(txn.getAttachmentTag(_attachKey))

                                            if lParent and parent_Txn.getOtherTxn(_ii).hasAttachments():
                                                holdTheKeys = holdTheKeys + parent_Txn.getOtherTxn(_ii).getAttachmentKeys()
                                                for _attachKey in parent_Txn.getOtherTxn(_ii).getAttachmentKeys():
                                                    # noinspection PyUnresolvedReferences
                                                    holdTheLocations.append(parent_Txn.getOtherTxn(_ii).getAttachmentTag(_attachKey))

                                            if not lExtractAttachments_EAR or not holdTheKeys:
                                                if holdTheKeys:
                                                    splitRowCopy[dataKeys["_ATTACHMENTLINK"][_COLUMN]] = safeStr(holdTheKeys)
                                                myPrint("D", _THIS_EXTRACT_NAME, splitRowCopy)
                                                GlobalVars.transactionTable.append(splitRowCopy)
                                                # abort
                                                keyIndex += 1
                                                iCount += 1
                                                continue

                                            # ok, we should still be on the first split record here.... and we want to download attachments....
                                            attachmentFileList=[]
                                            attachmentKeys = holdTheKeys                                                # noqa
                                            attachmentLocations = holdTheLocations
                                            uniqueFileString= " " * 5
                                            for attachmentLocation in attachmentLocations:
                                                uniqueFileString = str(uniqueFileNumber).strip().zfill(5)
                                                outputFile = os.path.join(attachmentDir,str(uniqueFileString)+"-"+os.path.basename(attachmentLocation) )
                                                try:
                                                    _ostr = FileOutputStream( File(outputFile) )
                                                    bytesCopied = _local_storage.readFile(attachmentLocation, _ostr)
                                                    _ostr.close()
                                                    myPrint("DB", _THIS_EXTRACT_NAME + "Attachment %s bytes >> %s copied to %s" %(bytesCopied, attachmentLocation,outputFile))
                                                    attachmentFileList.append(outputFile)
                                                    iCountAttachmentsDownloaded += 1
                                                    lDidIUseAttachmentDir = True
                                                except:
                                                    iAttachmentErrors += 1
                                                    myPrint("B", _THIS_EXTRACT_NAME + "@@ ERROR - Could not extract %s" %(attachmentLocation))

                                                uniqueFileNumber += 1

                                            if len(attachmentFileList) < 1:
                                                myPrint("B", _THIS_EXTRACT_NAME + "@@Major Error whilst searching attachments! Will just move on to next record and skip attachment")
                                                splitRowCopy[dataKeys["_ATTACHMENTLINK"][_COLUMN]] = "*ERROR*"
                                                myPrint("B", splitRowCopy)
                                                GlobalVars.transactionTable.append(splitRowCopy)
                                                keyIndex += 1
                                                iCount += 1
                                                continue
                                            else:
                                                for _i in range(0,len(attachmentFileList)):
                                                    rowCopy = deepcopy(splitRowCopy)  # Otherwise passes by references and future changes affect the original(s)

                                                    if _i > 0:  # If not on first record, update the key...
                                                        rowCopy[dataKeys["_KEY"][_COLUMN]] = txnKey + "-" + str(keyIndex).zfill(3)

                                                    if _i > 0:
                                                        rowCopy[dataKeys["_TOTALAMOUNT"][_COLUMN]] = None
                                                        rowCopy[dataKeys["_FOREIGNTOTALAMOUNT"][_COLUMN]] = None

                                                    if _i > 0:  # Inefficient, but won't happen very often - nuke the replicated fields on extra rows
                                                        for _c in range(dataKeys["_PARENTHASATTACHMENTS"][_COLUMN]+1,dataKeys["_ATTACHMENTLINK"][_COLUMN]):
                                                            rowCopy[_c] = None

                                                    rowCopy[dataKeys["_SPLITIDX"][_COLUMN]] = _ii
                                                    # rowCopy[dataKeys["_ATTACHMENTLINK"][_COLUMN]]     = "FILE://" + attachmentFileList[_i]
                                                    rowCopy[dataKeys["_ATTACHMENTLINK"][_COLUMN]] = '=HYPERLINK("'+attachmentFileList[_i]+'","FILE: '+os.path.basename(attachmentFileList[_i])[len(uniqueFileString)+1:]+'")'
                                                    rowCopy[dataKeys["_ATTACHMENTLINKREL"][_COLUMN]] = '=HYPERLINK("'+os.path.join(".",relativePath,os.path.basename(attachmentFileList[_i]))+'","FILE: '+os.path.basename(attachmentFileList[_i])[len(uniqueFileString)+1:]+'")'
                                                    GlobalVars.transactionTable.append(rowCopy)
                                                    keyIndex += 1
                                                    iCount += 1

                                    if (lIncludeOpeningBalances_EAR or lIncludeBalanceAdjustments_EAR) and len(copyValidAccountList) > 0:
                                        myPrint("DB", _THIS_EXTRACT_NAME + "Now iterating remaining %s Accounts with no txns for balances...." %(len(copyValidAccountList)))

                                        # Yes I should just move this section from above so the code is not inefficient....
                                        for acctBal in copyValidAccountList:

                                            acctCurr = acctBal.getCurrencyType()  # Currency of the acct

                                            if (lIncludeOpeningBalances_EAR):
                                                openBal = acctCurr.getDoubleValue(getUnadjustedStartBalance(acctBal))
                                                if openBal != 0:
                                                    iBal += 1
                                                    _row = ([None] * dataKeys["_END"][0])  # Create a blank row to be populated below...
                                                    _row[dataKeys["_KEY"][_COLUMN]] = acctBal.getUUID()
                                                    _row[dataKeys["_ACCOUNTTYPE"][_COLUMN]] = safeStr(acctBal.getAccountType())
                                                    _row[dataKeys["_ACCOUNT"][_COLUMN]] = acctBal.getFullAccountName()
                                                    _row[dataKeys["_CURR"][_COLUMN]] = acctCurr.getIDString()
                                                    _row[dataKeys["_DESC"][_COLUMN]] = "MANUAL (UNADJUSTED) OPENING BALANCE"
                                                    _row[dataKeys["_CHEQUE"][_COLUMN]] = "MANUAL"
                                                    _row[dataKeys["_DATE"][_COLUMN]] = acctBal.getCreationDateInt()
                                                    _row[dataKeys["_SPLITIDX"][_COLUMN]] = 0
                                                    if acctCurr == GlobalVars.baseCurrency:
                                                        _row[dataKeys["_TOTALAMOUNT"][_COLUMN]] = openBal
                                                        _row[dataKeys["_SPLITAMOUNT"][_COLUMN]] = openBal
                                                    else:
                                                        _row[dataKeys["_TOTALAMOUNT"][_COLUMN]] = round(openBal / acctCurr.getRate(GlobalVars.baseCurrency),2)
                                                        _row[dataKeys["_SPLITAMOUNT"][_COLUMN]] = round(openBal / acctCurr.getRate(GlobalVars.baseCurrency),2)
                                                        _row[dataKeys["_FOREIGNTOTALAMOUNT"][_COLUMN]] = openBal
                                                        _row[dataKeys["_FOREIGNSPLITAMOUNT"][_COLUMN]] = openBal

                                                    myPrint("D", _THIS_EXTRACT_NAME, _row)
                                                    GlobalVars.transactionTable.append(_row)
                                                    del openBal

                                            if (lIncludeBalanceAdjustments_EAR):
                                                adjBal = acctCurr.getDoubleValue(getBalanceAdjustment(acctBal))
                                                if adjBal != 0:
                                                    iBal += 1
                                                    _row = ([None] * dataKeys["_END"][0])  # Create a blank row to be populated below...
                                                    _row[dataKeys["_KEY"][_COLUMN]] = acctBal.getUUID()
                                                    _row[dataKeys["_ACCOUNTTYPE"][_COLUMN]] = safeStr(acctBal.getAccountType())
                                                    _row[dataKeys["_ACCOUNT"][_COLUMN]] = acctBal.getFullAccountName()
                                                    _row[dataKeys["_CURR"][_COLUMN]] = acctCurr.getIDString()
                                                    _row[dataKeys["_DESC"][_COLUMN]] = "MANUAL BALANCE ADJUSTMENT (MD2023 onwards)"
                                                    _row[dataKeys["_CHEQUE"][_COLUMN]] = "MANUAL"
                                                    _row[dataKeys["_DATE"][_COLUMN]] = DateUtil.getStrippedDateInt()
                                                    _row[dataKeys["_SPLITIDX"][_COLUMN]] = 0
                                                    if acctCurr == GlobalVars.baseCurrency:
                                                        _row[dataKeys["_TOTALAMOUNT"][_COLUMN]] = adjBal
                                                        _row[dataKeys["_SPLITAMOUNT"][_COLUMN]] = adjBal
                                                    else:
                                                        _row[dataKeys["_TOTALAMOUNT"][_COLUMN]] = round(adjBal / acctCurr.getRate(GlobalVars.baseCurrency),2)
                                                        _row[dataKeys["_SPLITAMOUNT"][_COLUMN]] = round(adjBal / acctCurr.getRate(GlobalVars.baseCurrency),2)
                                                        _row[dataKeys["_FOREIGNTOTALAMOUNT"][_COLUMN]] = adjBal
                                                        _row[dataKeys["_FOREIGNSPLITAMOUNT"][_COLUMN]] = adjBal

                                                    myPrint("D", _THIS_EXTRACT_NAME, _row)
                                                    GlobalVars.transactionTable.append(_row)
                                                    del adjBal

                                    myPrint("B", _THIS_EXTRACT_NAME + "Account Register Transaction Records (Parents, Splits, Attachments) selected:", len(GlobalVars.transactionTable) )

                                    if iCountAttachmentsDownloaded:
                                        myPrint("B", _THIS_EXTRACT_NAME + ".. and I downloaded %s attachments for you too" %iCountAttachmentsDownloaded )

                                    if iBal: myPrint("B", _THIS_EXTRACT_NAME + "...and %s Manual Opening Balance / Adjustment (MD2023 onwards) entries created too..." %iBal)

                                    if iAttachmentErrors: myPrint("B", _THIS_EXTRACT_NAME + "@@ ...and %s Attachment Errors..." %iAttachmentErrors)
                                    ###########################################################################################################

                                    # sort the file:
                                    GlobalVars.transactionTable = sorted(GlobalVars.transactionTable, key=lambda x: (x[dataKeys["_ACCOUNTTYPE"][_COLUMN]],
                                                                                                                 x[dataKeys["_ACCOUNT"][_COLUMN]],
                                                                                                                 x[dataKeys["_DATE"][_COLUMN]],
                                                                                                                 x[dataKeys["_KEY"][_COLUMN]],
                                                                                                                 x[dataKeys["_SPLITIDX"][_COLUMN]]) )
                                    ###########################################################################################################

                                    def ExtractDataToFile():
                                        global csvDelimiter
                                        global userdateformat
                                        global lWriteBOMToExportFile_SWSS
                                        global lAllTags_EAR, tagFilter_EAR
                                        global lAllText_EAR, textFilter_EAR
                                        global lAllCategories_EAR, categoriesFilter_EAR
                                        global lExtractAttachments_EAR, relativePath

                                        myPrint("D", _THIS_EXTRACT_NAME + "In ", inspect.currentframe().f_code.co_name, "()")

                                        headings = []
                                        sortDataFields = sorted(dataKeys.items(), key=lambda x: x[1][_COLUMN])
                                        for i in sortDataFields:
                                            headings.append(i[1][_HEADING])
                                        print

                                        myPrint("DB", _THIS_EXTRACT_NAME + "Now pre-processing the file to convert integer dates and strip non-ASCII if requested....")
                                        for _theRow in GlobalVars.transactionTable:
                                            dateasdate = datetime.datetime.strptime(str(_theRow[dataKeys["_DATE"][_COLUMN]]), "%Y%m%d")  # Convert to Date field
                                            _dateoutput = dateasdate.strftime(userdateformat)
                                            _theRow[dataKeys["_DATE"][_COLUMN]] = _dateoutput

                                            if _theRow[dataKeys["_TAXDATE"][_COLUMN]]:
                                                dateasdate = datetime.datetime.strptime(str(_theRow[dataKeys["_TAXDATE"][_COLUMN]]), "%Y%m%d")  # Convert to Date field
                                                _dateoutput = dateasdate.strftime(userdateformat)
                                                _theRow[dataKeys["_TAXDATE"][_COLUMN]] = _dateoutput

                                            for col in range(0, dataKeys["_ATTACHMENTLINK"][_COLUMN]):  # DO NOT MESS WITH ATTACHMENT LINK NAMES!!
                                                _theRow[col] = fixFormatsStr(_theRow[col])

                                        myPrint("B", _THIS_EXTRACT_NAME + "Opening file and writing %s records"  %(len(GlobalVars.transactionTable)))


                                        try:
                                            # CSV Writer will take care of special characters / delimiters within fields by wrapping in quotes that Excel will decode
                                            with open(GlobalVars.csvfilename, "wb") as csvfile:  # PY2.7 has no newline parameter so opening in binary just use "w" and newline='' in PY3.0

                                                if lWriteBOMToExportFile_SWSS:
                                                    csvfile.write(codecs.BOM_UTF8)   # This 'helps' Excel open file with double-click as UTF-8

                                                writer = csv.writer(csvfile, dialect='excel', quoting=csv.QUOTE_MINIMAL, delimiter=fix_delimiter(csvDelimiter))

                                                if csvDelimiter != ",":
                                                    writer.writerow(["sep=", ""])  # Tells Excel to open file with the alternative delimiter (it will add the delimiter to this line)

                                                if lExtractAttachments_EAR and Platform.isOSX():
                                                    writer.writerow([""])
                                                    writer.writerow(["** On a Mac with Later versions of Excel, Apple 'Sand Boxing' prevents file access..."])
                                                    writer.writerow(["** Edit this cell below, then press Enter and it will change to a Hyperlink (blue)"])
                                                    writer.writerow(["** Click it, then Open, and then GRANT access to the folder.... (the links below will then work)"])
                                                    writer.writerow([""])
                                                    # writer.writerow(["FILE://" + os.path.join(".",relativePath)])
                                                    writer.writerow(["FILE://" + GlobalVars.scriptpath])
                                                    # writer.writerow(["FILE:///"])  # This attempts to allow access to whole folder subsystem....
                                                    writer.writerow([""])

                                                if lExtractAttachments_EAR:
                                                    writer.writerow(headings[:dataKeys["_KEY"][_COLUMN]])  # Print the header, but not the extra _field headings
                                                else:
                                                    writer.writerow(headings[:dataKeys["_ATTACHMENTLINKREL"][_COLUMN]])  # Print the header, but not the extra _field headings

                                                try:
                                                    for i in range(0, len(GlobalVars.transactionTable)):
                                                        if lExtractAttachments_EAR:
                                                            writer.writerow(GlobalVars.transactionTable[i][:dataKeys["_KEY"][_COLUMN]])
                                                        else:
                                                            writer.writerow(GlobalVars.transactionTable[i][:dataKeys["_ATTACHMENTLINKREL"][_COLUMN]])
                                                except:
                                                    _msgTxt = _THIS_EXTRACT_NAME + "@@ ERROR writing to CSV on row %s. Please review console" %(i)
                                                    GlobalVars.AUTO_MESSAGES.append(_msgTxt)
                                                    myPrint("B", _msgTxt)
                                                    myPrint("B", GlobalVars.transactionTable[i])
                                                    raise

                                                if lWriteParametersToExportFile_SWSS:
                                                    today = Calendar.getInstance()
                                                    writer.writerow([""])
                                                    writer.writerow(["StuWareSoftSystems - " + GlobalVars.thisScriptName + "(build: "
                                                                     + version_build
                                                                     + ")  Moneydance Python Script - Date of Extract: "
                                                                     + str(GlobalVars.sdf.format(today.getTime()))])

                                                    writer.writerow([""])
                                                    writer.writerow(["Dataset path/name: %s" %(MD_REF.getCurrentAccountBook().getRootFolder()) ])

                                                    writer.writerow([""])
                                                    writer.writerow(["User Parameters..."])

                                                    if GlobalVars.dropDownAccount_EAR:
                                                        # noinspection PyUnresolvedReferences
                                                        writer.writerow(["Dropdown Account selected......: %s" %(GlobalVars.dropDownAccount_EAR.getAccountName())])
                                                        writer.writerow(["Include Sub Accounts...........: %s" %(lIncludeSubAccounts_EAR)])
                                                    else:
                                                        writer.writerow(["Hiding Inactive Accounts.......: %s" %(hideInactiveAccounts)])
                                                        writer.writerow(["Hiding Hidden Accounts.........: %s" %(hideHiddenAccounts)])
                                                        writer.writerow(["Account filter.................: %s '%s'" %(lAllAccounts,filterForAccounts)])
                                                        writer.writerow(["Currency filter................: %s '%s'" %(lAllCurrency,filterForCurrency)])

                                                    writer.writerow(["Include Unadjusted Opening Balances: %s" %(lIncludeOpeningBalances_EAR)])
                                                    writer.writerow(["Include Balance Adjustments........: %s" %(lIncludeBalanceAdjustments_EAR)])
                                                    # writer.writerow(["Include Acct Transfers............: %s" %(lIncludeInternalTransfers_EAR)])
                                                    writer.writerow(["Tag filter.........................: %s '%s'" %(lAllTags_EAR,tagFilter_EAR)])
                                                    writer.writerow(["Text filter........................: %s '%s'" %(lAllText_EAR,textFilter_EAR)])
                                                    writer.writerow(["Category filter....................: %s '%s'" %(lAllCategories_EAR,categoriesFilter_EAR)])
                                                    writer.writerow(["Download Attachments...............: %s" %(lExtractAttachments_EAR)])
                                                    writer.writerow(["Date range.........................: %s" %(saveDropDownDateRange_EAR)])
                                                    writer.writerow(["Selected Start Date................: %s" %(userdateStart_EAR)])
                                                    writer.writerow(["Selected End Date..................: %s" %(userdateEnd_EAR)])
                                                    writer.writerow(["user date format...................: %s" %(userdateformat)])

                                            _msgTxt = _THIS_EXTRACT_NAME + "CSV file: '%s' created (%s records)" %(GlobalVars.csvfilename, len(GlobalVars.transactionTable))
                                            myPrint("B", _msgTxt)
                                            GlobalVars.AUTO_MESSAGES.append(_msgTxt)
                                            GlobalVars.countFilesCreated += 1

                                        except:
                                            e_type, exc_value, exc_traceback = sys.exc_info()                           # noqa
                                            _msgTxt = _THIS_EXTRACT_NAME + "@@ ERROR '%s' detected writing file: '%s' - Extract ABORTED!" %(exc_value, GlobalVars.csvfilename)
                                            GlobalVars.AUTO_MESSAGES.append(_msgTxt)
                                            myPrint("B", _msgTxt)
                                            raise

                                    def fixFormatsStr(theString, lNumber=False, sFormat=""):
                                        if isinstance(theString, bool): return theString
                                        if isinstance(theString, tuple): return theString
                                        if isinstance(theString, dict): return theString
                                        if isinstance(theString, list): return theString

                                        if isinstance(theString, int) or isinstance(theString, float) or isinstance(theString, long):
                                            lNumber = True

                                        if lNumber is None: lNumber = False
                                        if theString is None: theString = ""

                                        if sFormat == "%" and theString != "":
                                            theString = "{:.1%}".format(theString)
                                            return theString

                                        if lNumber: return str(theString)

                                        theString = theString.strip()  # remove leading and trailing spaces

                                        theString = theString.replace("\n", "*")  # remove newlines within fields to keep csv format happy
                                        theString = theString.replace("\t", "*")  # remove tabs within fields to keep csv format happy
                                        # theString = theString.replace(";", "*")
                                        # theString = theString.replace(",", "*")
                                        # theString = theString.replace("|", "*")

                                        if lStripASCII:
                                            all_ASCII = ''.join(char for char in theString if ord(char) < 128)  # Eliminate non ASCII printable Chars too....
                                        else:
                                            all_ASCII = theString
                                        return all_ASCII

                                    if iBal+iCount > 0:
                                        ExtractDataToFile()

                                        if not GlobalVars.lGlobalErrorDetected:
                                            xtra_msg=""
                                            if lDidIUseAttachmentDir:

                                                baseName = os.path.basename(GlobalVars.csvfilename)
                                                lShell = None
                                                theCommand = None

                                                if not Platform.isWindows():
                                                    theCommand = 'zip -v -r "%s" "%s" "%s"' %(os.path.splitext(baseName)[0]+".zip",
                                                                                              baseName,
                                                                                              os.path.join(os.path.splitext(baseName)[0],""))

                                                    lShell = True
                                                else:
                                                    try:
                                                        if float(System.getProperty("os.version")) >= 10:
                                                            theCommand = 'tar -a -cvf "%s" "%s" "%s"' %(os.path.splitext(baseName)[0]+".zip",
                                                                                                        baseName,
                                                                                                        os.path.join(os.path.splitext(baseName)[0],"*.*"))

                                                            lShell = False
                                                    except: pass
                                                try:
                                                    if theCommand:
                                                        os.chdir(GlobalVars.scriptpath)
                                                        xx = subprocess.check_output( theCommand, shell=lShell)
                                                        myPrint("B", _THIS_EXTRACT_NAME + "Created zip using command: %s (output follows)" %theCommand)
                                                        myPrint("B", _THIS_EXTRACT_NAME + xx)
                                                        xtra_msg = _THIS_EXTRACT_NAME + "\n(and I also zipped the file - review console / log for any messages)"
                                                except:
                                                    myPrint("B", _THIS_EXTRACT_NAME + "Sorry, failed to create zip")
                                                    xtra_msg = "\n(with an error creating the zip file - review console / log for messages)"

                                            sTxt = "Extract file CREATED:"
                                            mTxt = ("With %s rows and %s attachments downloaded %s\n"
                                                    "\n(... and %s Attachment Errors...)"
                                                    % (len(GlobalVars.transactionTable),iCountAttachmentsDownloaded, xtra_msg,iAttachmentErrors))
                                            myPrint("B", _THIS_EXTRACT_NAME + "%s\n%s" %(sTxt, mTxt))
                                        else:
                                            _msgTextx = _THIS_EXTRACT_NAME + "ERROR Creating extract (review console for error messages)...."
                                            GlobalVars.AUTO_MESSAGES.append(_msgTextx)
                                    else:
                                        _msgTextx = _THIS_EXTRACT_NAME + "@@ No records selected and no extract file created @@"
                                        GlobalVars.AUTO_MESSAGES.append(_msgTextx)
                                        myPrint("B", _msgTextx)
                                        if not GlobalVars.AUTO_EXTRACT_MODE:
                                            DoExtractsSwingWorker.killPleaseWait()
                                            genericSwingEDTRunner(True, True, myPopupInformationBox, extract_data_frame_, _msgTextx, GlobalVars.thisScriptName, JOptionPane.WARNING_MESSAGE)

                                    # Clean up...
                                    if not lDidIUseAttachmentDir and attachmentDir:
                                        try:
                                            os.rmdir(attachmentDir)
                                            myPrint("B", _THIS_EXTRACT_NAME + "REMOVED unused/empty attachment directory: '%s'" %attachmentDir)

                                        except:
                                            myPrint("B", _THIS_EXTRACT_NAME + "FAILED to remove the unused/empty attachment directory: '%s'" %(attachmentDir))

                                    # delete references to large objects
                                    GlobalVars.transactionTable = None
                                    del accountBalances

                                try:
                                    do_extract_account_registers()
                                except:
                                    GlobalVars.lGlobalErrorDetected = True

                                if GlobalVars.lGlobalErrorDetected:
                                    GlobalVars.countErrorsDuringExtract += 1
                                    _txt = _THIS_EXTRACT_NAME + "@@ ERROR: do_extract_account_registers() has failed (review console)!"
                                    GlobalVars.AUTO_MESSAGES.append(_txt)
                                    myPrint("B", _txt)
                                    dump_sys_error_to_md_console_and_errorlog()
                                    if not GlobalVars.AUTO_EXTRACT_MODE:
                                        DoExtractsSwingWorker.killPleaseWait()
                                        genericSwingEDTRunner(True, True, myPopupInformationBox, extract_data_frame_, _txt, "ERROR", JOptionPane.ERROR_MESSAGE)
                                        return False
                            #### ENDIF lExtractAccountTxns ####

                            if lExtractInvestmentTxns:
                                # ####################################################
                                # EXTRACT_INVESTMENT_TRANSACTIONS_CSV EXECUTION
                                # ####################################################

                                _THIS_EXTRACT_NAME = pad("EXTRACT: Investment Transactions:", 34)
                                GlobalVars.lGlobalErrorDetected = False

                                if not GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE:
                                    self.super__publish([_THIS_EXTRACT_NAME.strip()])                                   # noqa

                                if GlobalVars.AUTO_EXTRACT_MODE:
                                    GlobalVars.csvfilename = os.path.join(GlobalVars.scriptpath, MD_REF.getCurrentAccountBook().getName() + "_" + GlobalVars.defaultFileName_EIT + ".csv")

                                def do_extract_investment_transactions():
                                    global lDidIUseAttachmentDir
                                    global dataKeys, attachmentDir, relativePath

                                    global __extract_data, extract_filename
                                    global lStripASCII, csvDelimiter, userdateformat, lWriteBOMToExportFile_SWSS
                                    global hideInactiveAccounts, hideHiddenAccounts, hideHiddenSecurities
                                    global lAllSecurity, filterForSecurity, lAllAccounts, filterForAccounts, lAllCurrency, filterForCurrency
                                    global lFilterDateRange_EIT, filterDateStart_EIT, filterDateEnd_EIT
                                    global lOmitLOTDataFromExtract_EIT, lExtractExtraSecurityAcctInfo
                                    global whichDefaultExtractToRun_SWSS
                                    global lIncludeOpeningBalances, lIncludeBalanceAdjustments, lAdjustForSplits, lExtractAttachments_EIT

                                    # noinspection PyArgumentList
                                    class MyTxnSearchCostBasisEIT(TxnSearch):

                                        def __init__(self,
                                                     hideInactiveAccounts=False,                                        # noqa
                                                     lAllAccounts=True,                                                 # noqa
                                                     filterForAccounts="ALL",                                           # noqa
                                                     hideHiddenAccounts=False,                                          # noqa
                                                     hideHiddenSecurities=False,                                        # noqa
                                                     lAllCurrency=True,                                                 # noqa
                                                     filterForCurrency="ALL",                                           # noqa
                                                     lAllSecurity=True,                                                 # noqa
                                                     filterForSecurity="ALL",                                           # noqa
                                                     findUUID=None):                                                    # noqa
                                            super(TxnSearch, self).__init__()

                                            self.hideInactiveAccounts = hideInactiveAccounts
                                            self.lAllAccounts = lAllAccounts
                                            self.filterForAccounts = filterForAccounts
                                            self.hideHiddenAccounts = hideHiddenAccounts
                                            self.hideHiddenSecurities = hideHiddenSecurities
                                            self.lAllCurrency = lAllCurrency
                                            self.filterForCurrency = filterForCurrency
                                            self.lAllSecurity = lAllSecurity
                                            self.filterForSecurity = filterForSecurity
                                            self.findUUID = findUUID

                                        # noinspection PyMethodMayBeStatic
                                        def matchesAll(self):
                                            return False


                                        def matches(self, txn):                                                         # noqa
                                            # NOTE: If not using the parameter selectAccountType=.SECURITY then the security filters won't work (without
                                            # special extra coding!)

                                            txnAcct = txn.getAccount()                                                  # noqa

                                            if self.findUUID is not None:  # If UUID supplied, override all other parameters...
                                                if txnAcct.getUUID() == self.findUUID:
                                                    return True
                                                else:
                                                    return False

                                            # Investment Accounts only
                                            # noinspection PyUnresolvedReferences
                                            if txnAcct.getAccountType() != Account.AccountType.INVESTMENT:
                                                return False

                                            if self.hideInactiveAccounts:
                                                # This logic replicates Moneydance AcctFilter.ACTIVE_ACCOUNTS_FILTER
                                                if txnAcct.getAccountOrParentIsInactive(): return False
                                                if txnAcct.getHideOnHomePage() and txnAcct.getBalance() == 0: return False
                                                # Don't repeat the above check on the security sub accounts as probably needed for cost basis reporting

                                            if self.lAllAccounts:
                                                pass
                                            elif (self.filterForAccounts.upper().strip() in txnAcct.getFullAccountName().upper().strip()):
                                                pass
                                            else:
                                                return False

                                            if (not self.hideHiddenAccounts) or (self.hideHiddenAccounts and not txnAcct.getHideOnHomePage()):
                                                pass
                                            else:
                                                return False

                                            # Check that we are on a parent. If we are on a split, in an Investment Account, then it must be a cash txfr only
                                            lParent = False                                                             # noqa
                                            parent = txn.getParentTxn()                                                 # noqa
                                            if txn == parent:
                                                lParent = True                                                          # noqa

                                            txnCurr = txnAcct.getCurrencyType()

                                            if self.lAllSecurity:
                                                securityCurr = None                                                     # noqa
                                                securityTxn = None                                                      # noqa
                                                securityAcct = None                                                     # noqa
                                            else:

                                                if not lParent: return False

                                                # If we don't have a security record, then we are not interested!
                                                securityTxn = TxnUtil.getSecurityPart(txn)                              # noqa
                                                if securityTxn is None:
                                                    return False

                                                securityAcct = securityTxn.getAccount()                                 # noqa
                                                securityCurr = securityAcct.getCurrencyType()                           # noqa

                                                if not self.hideHiddenSecurities or (self.hideHiddenSecurities and not securityCurr.getHideInUI()):
                                                    pass
                                                else:
                                                    return False

                                                # noinspection PyUnresolvedReferences
                                                if self.lAllSecurity:
                                                    pass
                                                elif self.filterForSecurity.upper().strip() in securityCurr.getTickerSymbol().upper().strip():
                                                    pass
                                                elif self.filterForSecurity.upper().strip() in securityCurr.getName().upper().strip():
                                                    pass
                                                else:
                                                    return False

                                            if self.lAllCurrency:
                                                pass
                                            else:
                                                if securityCurr:
                                                    # noinspection PyUnresolvedReferences
                                                    if txnCurr.getIDString().upper().strip() != securityCurr.getRelativeCurrency().getIDString().upper().strip():
                                                        _msgTxt = _THIS_EXTRACT_NAME + "LOGIC ERROR: I can't see how the Security's currency is different to the Account's currency?"
                                                        myPrint("B", _msgTxt)
                                                        # noinspection PyUnresolvedReferences
                                                        myPrint("B", _THIS_EXTRACT_NAME, txnCurr.getIDString().upper().strip(), securityCurr.getRelativeCurrency().getIDString().upper().strip())
                                                        myPrint("B", _THIS_EXTRACT_NAME, repr(txn))
                                                        myPrint("B", _THIS_EXTRACT_NAME, repr(txnCurr))
                                                        myPrint("B", _THIS_EXTRACT_NAME, repr(securityCurr))
                                                        # noinspection PyUnresolvedReferences
                                                        if not GlobalVars.AUTO_EXTRACT_MODE:
                                                            DoExtractsSwingWorker.killPleaseWait()
                                                            genericSwingEDTRunner(True, True, myPopupInformationBox, extract_data_frame_, _msgTxt, "LOGIC ERROR", JOptionPane.ERROR_MESSAGE)
                                                        # noinspection PyUnresolvedReferences
                                                        raise Exception(_THIS_EXTRACT_NAME + "LOGIC Error - Security's currency: "
                                                                        + securityCurr.getRelativeCurrency().getIDString().upper().strip()              # noqa
                                                                        + " is different to txn currency: "
                                                                        + txnCurr.getIDString().upper().strip()
                                                                        + " Aborting")


                                                    # All accounts and security records can have currencies
                                                    # noinspection PyUnresolvedReferences
                                                    if self.lAllCurrency:
                                                        pass
                                                    elif (self.filterForCurrency.upper().strip() in txnCurr.getIDString().upper().strip()) \
                                                            and (
                                                            self.filterForCurrency.upper().strip() in securityCurr.getRelativeCurrency().getIDString().upper().strip()):
                                                        pass
                                                    elif (self.filterForCurrency.upper().strip() in txnCurr.getName().upper().strip()) \
                                                            and (
                                                            self.filterForCurrency.upper().strip() in securityCurr.getRelativeCurrency().getName().upper().strip()):
                                                        pass
                                                    else:
                                                        return False

                                                else:
                                                    # All accounts and security records can have currencies
                                                    if self.lAllCurrency:
                                                        pass
                                                    elif (self.filterForCurrency.upper().strip() in txnCurr.getIDString().upper().strip()):
                                                        pass
                                                    elif (self.filterForCurrency.upper().strip() in txnCurr.getName().upper().strip()):
                                                        pass
                                                    else:
                                                        return False

                                            # Phew! We made it....
                                            return True
                                        # enddef

                                    # noinspection PyArgumentList
                                    class MyAcctFilterEIT(AcctFilter):

                                        def __init__(self,
                                                     hideInactiveAccounts=False,                                        # noqa
                                                     lAllAccounts=True,                                                 # noqa
                                                     filterForAccounts="ALL",                                           # noqa
                                                     hideHiddenAccounts=False,                                          # noqa
                                                     hideHiddenSecurities=False,                                        # noqa
                                                     lAllCurrency=True,                                                 # noqa
                                                     filterForCurrency="ALL",                                           # noqa
                                                     lAllSecurity=True,                                                 # noqa
                                                     filterForSecurity="ALL",                                           # noqa
                                                     findUUID=None):                                                    # noqa

                                            super(AcctFilter, self).__init__()

                                            self.hideInactiveAccounts = hideInactiveAccounts
                                            self.lAllAccounts = lAllAccounts
                                            self.filterForAccounts = filterForAccounts
                                            self.hideHiddenAccounts = hideHiddenAccounts
                                            self.hideHiddenSecurities = hideHiddenSecurities
                                            self.lAllCurrency = lAllCurrency
                                            self.filterForCurrency = filterForCurrency
                                            self.lAllSecurity = lAllSecurity
                                            self.filterForSecurity = filterForSecurity
                                            self.findUUID = findUUID

                                        def matches(self, acct):

                                            if self.findUUID is not None:  # If UUID supplied, override all other parameters...
                                                if acct.getUUID() == self.findUUID:
                                                    return True
                                                else:
                                                    return False

                                            # Investment Accounts only
                                            # noinspection PyUnresolvedReferences
                                            if acct.getAccountType() != Account.AccountType.INVESTMENT:
                                                return False

                                            if self.hideInactiveAccounts:
                                                # This logic replicates Moneydance AcctFilter.ACTIVE_ACCOUNTS_FILTER
                                                if acct.getAccountOrParentIsInactive(): return False
                                                if acct.getHideOnHomePage() and acct.getBalance() == 0: return False

                                            if self.lAllAccounts:
                                                pass
                                            elif (self.filterForAccounts.upper().strip() in acct.getFullAccountName().upper().strip()):
                                                pass
                                            else:
                                                return False

                                            if (not self.hideHiddenAccounts) or (self.hideHiddenAccounts and not acct.getHideOnHomePage()):
                                                pass
                                            else:
                                                return False

                                            if self.lAllSecurity:
                                                pass
                                            else:
                                                return False

                                            if self.lAllCurrency:
                                                pass
                                            else:
                                                acctCurr = acct.getCurrencyType()                                       # noqa
                                                if (self.filterForCurrency.upper().strip() in acctCurr.getIDString().upper().strip()):
                                                    pass
                                                elif (self.filterForCurrency.upper().strip() in acctCurr.getName().upper().strip()):
                                                    pass
                                                else:
                                                    return False

                                            # Phew! We made it....
                                            return True
                                        # enddef


                                    _COLUMN = 0
                                    _HEADING = 1

                                    dki = 0
                                    dataKeys = {}                                                                       # noqa
                                    dataKeys["_ACCOUNT"]             = [dki, "Account"];                   dki += 1
                                    dataKeys["_DATE"]                = [dki, "Date"];                      dki += 1
                                    dataKeys["_TAXDATE"]             = [dki, "TaxDate"];                   dki += 1
                                    dataKeys["_CURR"]                = [dki, "Currency"];                  dki += 1
                                    dataKeys["_SECURITY"]            = [dki, "Security"];                  dki += 1
                                    dataKeys["_SECURITYID"]          = [dki, "SecurityID"];                dki += 1
                                    dataKeys["_TICKER"]              = [dki, "SecurityTicker"];            dki += 1
                                    dataKeys["_SECCURR"]             = [dki, "SecurityCurrency"];          dki += 1
                                    dataKeys["_AVGCOST"]             = [dki, "AverageCostControl"];        dki += 1

                                    if lExtractExtraSecurityAcctInfo:
                                        dataKeys["_SECINFO_TYPE"]              = [dki, "Sec_Type"];                     dki += 1
                                        dataKeys["_SECINFO_SUBTYPE"]           = [dki, "Sec_SubType"];                  dki += 1
                                        dataKeys["_SECINFO_STK_DIV"]           = [dki, "Sec_Stock_Div"];                dki += 1
                                        dataKeys["_SECINFO_CD_APR"]            = [dki, "Sec_CD_APR"];                   dki += 1
                                        dataKeys["_SECINFO_CD_COMPOUNDING"]    = [dki, "Sec_CD_Compounding"];           dki += 1
                                        dataKeys["_SECINFO_CD_YEARS"]          = [dki, "Sec_CD_Years"];                 dki += 1
                                        dataKeys["_SECINFO_BOND_TYPE"]         = [dki, "Sec_Bond_Type"];                dki += 1
                                        dataKeys["_SECINFO_BOND_FACEVALUE"]    = [dki, "Sec_Bond_FaceValue"];           dki += 1
                                        dataKeys["_SECINFO_BOND_MATURITYDATE"] = [dki, "Sec_Bond_MaturityDate"];        dki += 1
                                        dataKeys["_SECINFO_BOND_APR"]          = [dki, "Sec_Bond_APR"];                 dki += 1
                                        dataKeys["_SECINFO_STKOPT_CALLPUT"]    = [dki, "Sec_StockOpt_CallPut"];         dki += 1
                                        dataKeys["_SECINFO_STKOPT_STKPRICE"]   = [dki, "Sec_StockOpt_StockPrice"];      dki += 1
                                        dataKeys["_SECINFO_STKOPT_EXPRICE"]    = [dki, "Sec_StockOpt_ExercisePrice"];   dki += 1
                                        dataKeys["_SECINFO_STKOPT_EXMONTH"]    = [dki, "Sec_StockOpt_ExerciseMonth"];   dki += 1

                                    dataKeys["_ACTION"]              = [dki, "Action"];                    dki += 1
                                    dataKeys["_TT"]                  = [dki, "ActionType"];                dki += 1
                                    dataKeys["_CHEQUE"]              = [dki, "Cheque"];                    dki += 1
                                    dataKeys["_DESC"]                = [dki, "Description"];               dki += 1
                                    dataKeys["_MEMO"]                = [dki, "Memo"];                      dki += 1
                                    dataKeys["_CLEARED"]             = [dki, "Cleared"];                   dki += 1
                                    dataKeys["_TRANSFER"]            = [dki, "Transfer"];                  dki += 1
                                    dataKeys["_CAT"]                 = [dki, "Category"];                  dki += 1
                                    dataKeys["_SHARES"]              = [dki, "Shares"];                    dki += 1
                                    dataKeys["_PRICE"]               = [dki, "Price"];                     dki += 1
                                    dataKeys["_AMOUNT"]              = [dki, "Amount"];                    dki += 1
                                    dataKeys["_FEE"]                 = [dki, "Fee"];                       dki += 1
                                    dataKeys["_FEECAT"]              = [dki, "FeeCategory"];               dki += 1
                                    dataKeys["_TXNNETAMOUNT"]        = [dki, "TransactionNetAmount"];      dki += 1
                                    dataKeys["_CASHIMPACT"]          = [dki, "CashImpact"];                dki += 1
                                    dataKeys["_SHRSAFTERSPLIT"]      = [dki, "CalculateSharesAfterSplit"]; dki += 1
                                    dataKeys["_PRICEAFTERSPLIT"]     = [dki, "CalculatePriceAfterSplit"];  dki += 1
                                    dataKeys["_HASATTACHMENTS"]      = [dki, "HasAttachments"];            dki += 1
                                    dataKeys["_LOTS"]                = [dki, "Lot Data"];                  dki += 1
                                    dataKeys["_ACCTCASHBAL"]         = [dki, "AccountCashBalance"];        dki += 1
                                    dataKeys["_SECSHRHOLDING"]       = [dki, "SecurityShareHolding"];      dki += 1
                                    dataKeys["_ATTACHMENTLINK"]      = [dki, "AttachmentLink"];            dki += 1
                                    dataKeys["_ATTACHMENTLINKREL"]   = [dki, "AttachmentLinkRelative"];    dki += 1
                                    dataKeys["_KEY"]                 = [dki, "Key"];                       dki += 1
                                    dataKeys["_END"]                 = [dki, "_END"];                      dki += 1

                                    GlobalVars.transactionTable = []

                                    myPrint("DB", _THIS_EXTRACT_NAME, dataKeys)

                                    book = MD_REF.getCurrentAccountBook()

                                    txns = book.getTransactionSet().getTransactions(MyTxnSearchCostBasisEIT(hideInactiveAccounts,
                                                                                                            lAllAccounts,
                                                                                                            filterForAccounts,
                                                                                                            hideHiddenAccounts,
                                                                                                            hideHiddenSecurities,
                                                                                                            lAllCurrency,
                                                                                                            filterForCurrency,
                                                                                                            lAllSecurity,
                                                                                                            filterForSecurity,
                                                                                                            None))

                                    validAccountList = AccountUtil.allMatchesForSearch(book, MyAcctFilterEIT(hideInactiveAccounts,
                                                                                                             lAllAccounts,
                                                                                                             filterForAccounts,
                                                                                                             hideHiddenAccounts,
                                                                                                             hideHiddenSecurities,
                                                                                                             lAllCurrency,
                                                                                                             filterForCurrency,
                                                                                                             lAllSecurity,
                                                                                                             filterForSecurity,
                                                                                                             None))

                                    iCount = 0
                                    iCountAttachmentsDownloaded = 0
                                    uniqueFileNumber = 1

                                    _local_storage = MD_REF.getCurrentAccountBook().getLocalStorage()
                                    iAttachmentErrors=0

                                    iBal = 0
                                    accountBalances = {}

                                    copyValidAccountList = ArrayList()
                                    if lIncludeOpeningBalances:
                                        for acctBal in validAccountList:
                                            if getUnadjustedStartBalance(acctBal) != 0:
                                                if (not lFilterDateRange_EIT or
                                                        (lFilterDateRange_EIT and acctBal.getCreationDateInt() >= filterDateStart_EIT and acctBal.getCreationDateInt() <= filterDateEnd_EIT)):
                                                    copyValidAccountList.add(acctBal)

                                    if lIncludeBalanceAdjustments:
                                        for acctBal in validAccountList:
                                            if getBalanceAdjustment(acctBal) != 0:
                                                if acctBal not in copyValidAccountList:
                                                    copyValidAccountList.add(acctBal)

                                    for txn in txns:

                                        txnAcct = txn.getAccount()
                                        acctCurr = txnAcct.getCurrencyType()  # Currency of the Investment Account

                                        if (lIncludeOpeningBalances or lIncludeBalanceAdjustments):

                                            if txnAcct in copyValidAccountList:
                                                copyValidAccountList.remove(txnAcct)

                                            if accountBalances.get(txnAcct):
                                                pass

                                            else:
                                                accountBalances[txnAcct] = True

                                                if (not lFilterDateRange_EIT
                                                        or (txnAcct.getCreationDateInt() >= filterDateStart_EIT and txnAcct.getCreationDateInt() <= filterDateEnd_EIT)):

                                                    if (lIncludeOpeningBalances):
                                                        openBal = acctCurr.getDoubleValue(getUnadjustedStartBalance(txnAcct))
                                                        if openBal != 0:
                                                            iBal += 1
                                                            _row = ([None] * dataKeys["_END"][0])  # Create a blank row to be populated below...
                                                            _row[dataKeys["_ACCOUNT"][_COLUMN]] = txnAcct.getFullAccountName()
                                                            _row[dataKeys["_CURR"][_COLUMN]] = acctCurr.getIDString()
                                                            _row[dataKeys["_DESC"][_COLUMN]] = "MANUAL (UNADJUSTED) OPENING BALANCE"
                                                            _row[dataKeys["_ACTION"][_COLUMN]] = "OpenBal"
                                                            _row[dataKeys["_TT"][_COLUMN]] = "MANUAL"
                                                            _row[dataKeys["_DATE"][_COLUMN]] = txnAcct.getCreationDateInt()
                                                            _row[dataKeys["_AMOUNT"][_COLUMN]] = openBal
                                                            _row[dataKeys["_CASHIMPACT"][_COLUMN]] = openBal
                                                            _row[dataKeys["_ACCTCASHBAL"][_COLUMN]] = acctCurr.getDoubleValue(txnAcct.getBalance())

                                                            myPrint("D", _THIS_EXTRACT_NAME, _row)
                                                            GlobalVars.transactionTable.append(_row)
                                                            del openBal

                                                if (lIncludeBalanceAdjustments):
                                                    adjBal = acctCurr.getDoubleValue(getBalanceAdjustment(txnAcct))
                                                    if adjBal != 0:
                                                        iBal += 1
                                                        _row = ([None] * dataKeys["_END"][0])  # Create a blank row to be populated below...
                                                        _row[dataKeys["_ACCOUNT"][_COLUMN]] = txnAcct.getFullAccountName()
                                                        _row[dataKeys["_CURR"][_COLUMN]] = acctCurr.getIDString()
                                                        _row[dataKeys["_DESC"][_COLUMN]] = "MANUAL BALANCE ADJUSTMENT (MD2023 onwards)"
                                                        _row[dataKeys["_ACTION"][_COLUMN]] = "BalAdj"
                                                        _row[dataKeys["_TT"][_COLUMN]] = "MANUAL"
                                                        _row[dataKeys["_DATE"][_COLUMN]] = DateUtil.getStrippedDateInt()
                                                        _row[dataKeys["_AMOUNT"][_COLUMN]] = adjBal
                                                        _row[dataKeys["_CASHIMPACT"][_COLUMN]] = adjBal
                                                        _row[dataKeys["_ACCTCASHBAL"][_COLUMN]] = acctCurr.getDoubleValue(txnAcct.getBalance())

                                                        myPrint("D", _THIS_EXTRACT_NAME, _row)
                                                        GlobalVars.transactionTable.append(_row)
                                                        del adjBal

                                        if lFilterDateRange_EIT and (txn.getDateInt() < filterDateStart_EIT or txn.getDateInt() > filterDateEnd_EIT):
                                            continue

                                        # Check that we are on a parent. If we are on a split, in an Investment Account, then it must be a cash txfr only
                                        parent = txn.getParentTxn()
                                        if txn == parent:
                                            lParent = True
                                        else:
                                            lParent = False

                                        securityCurr = None
                                        securityTxn = feeTxn = xfrTxn = incTxn = expTxn = None
                                        feeAcct = incAcct = expAcct = xfrAcct = securityAcct = None

                                        cbTags = None
                                        if lParent:
                                            securityTxn = TxnUtil.getSecurityPart(txn)
                                            if securityTxn:
                                                securityAcct = securityTxn.getAccount()
                                                securityCurr = securityAcct.getCurrencyType()  # the Security master record
                                                cbTags = TxnUtil.parseCostBasisTag(securityTxn)

                                            xfrTxn = TxnUtil.getXfrPart(txn)
                                            if xfrTxn: xfrAcct = xfrTxn.getAccount()

                                            feeTxn = TxnUtil.getCommissionPart(txn)
                                            if feeTxn: feeAcct = feeTxn.getAccount()

                                            incTxn = TxnUtil.getIncomePart(txn)
                                            if incTxn: incAcct = incTxn.getAccount()

                                            expTxn = TxnUtil.getExpensePart(txn)
                                            if expTxn:expAcct = expTxn.getAccount()

                                        keyIndex = 0
                                        _row = ([None] * dataKeys["_END"][0])  # Create a blank row to be populated below...

                                        txnKey = txn.getUUID()
                                        _row[dataKeys["_KEY"][_COLUMN]] = txnKey + "-" + str(keyIndex).zfill(3)


                                        if lParent and str(txn.getTransferType()).lower() == "xfrtp_bank" and str(txn.getInvestTxnType()).lower() == "bank" \
                                                and not xfrTxn and feeTxn and not securityTxn:
                                            # This seems to be an error! It's an XFR (fixing MD data bug)
                                            xfrTxn = feeTxn
                                            feeTxn = None
                                            xfrAcct = feeAcct
                                            feeAcct = None

                                        _row[dataKeys["_ACCOUNT"][_COLUMN]] = txnAcct.getFullAccountName()
                                        _row[dataKeys["_CURR"][_COLUMN]] = acctCurr.getIDString()

                                        _row[dataKeys["_DATE"][_COLUMN]] = txn.getDateInt()
                                        if txn.getTaxDateInt() != txn.getDateInt():
                                            _row[dataKeys["_TAXDATE"][_COLUMN]] = txn.getTaxDateInt()

                                        if lExtractExtraSecurityAcctInfo:
                                            _row[dataKeys["_SECINFO_TYPE"][_COLUMN]] = ""
                                            _row[dataKeys["_SECINFO_SUBTYPE"][_COLUMN]] = ""
                                            _row[dataKeys["_SECINFO_STK_DIV"][_COLUMN]] = ""
                                            _row[dataKeys["_SECINFO_CD_APR"][_COLUMN]] = ""
                                            _row[dataKeys["_SECINFO_CD_COMPOUNDING"][_COLUMN]] = ""
                                            _row[dataKeys["_SECINFO_CD_YEARS"][_COLUMN]] = ""
                                            _row[dataKeys["_SECINFO_BOND_TYPE"][_COLUMN]] = ""
                                            _row[dataKeys["_SECINFO_BOND_FACEVALUE"][_COLUMN]] = ""
                                            _row[dataKeys["_SECINFO_BOND_MATURITYDATE"][_COLUMN]] = ""
                                            _row[dataKeys["_SECINFO_BOND_APR"][_COLUMN]] = ""
                                            _row[dataKeys["_SECINFO_STKOPT_CALLPUT"][_COLUMN]] = ""
                                            _row[dataKeys["_SECINFO_STKOPT_STKPRICE"][_COLUMN]] = ""
                                            _row[dataKeys["_SECINFO_STKOPT_EXPRICE"][_COLUMN]] = ""
                                            _row[dataKeys["_SECINFO_STKOPT_EXMONTH"][_COLUMN]] = ""

                                        if securityTxn:
                                            _row[dataKeys["_SECURITY"][_COLUMN]] = safeStr(securityCurr.getName())
                                            _row[dataKeys["_SECURITYID"][_COLUMN]] = safeStr(securityCurr.getIDString())
                                            _row[dataKeys["_SECCURR"][_COLUMN]] = safeStr(securityCurr.getRelativeCurrency().getIDString())
                                            _row[dataKeys["_TICKER"][_COLUMN]] = safeStr(securityCurr.getTickerSymbol())
                                            _row[dataKeys["_SHARES"][_COLUMN]] = securityCurr.getDoubleValue(securityTxn.getValue())
                                            _row[dataKeys["_PRICE"][_COLUMN]] = acctCurr.getDoubleValue(securityTxn.getAmount())
                                            _row[dataKeys["_AVGCOST"][_COLUMN]] = securityAcct.getUsesAverageCost()
                                            _row[dataKeys["_SECSHRHOLDING"][_COLUMN]] = securityCurr.formatSemiFancy(securityAcct.getBalance(),GlobalVars.decimalCharSep)

                                            if lExtractExtraSecurityAcctInfo:
                                                try:
                                                    _row[dataKeys["_SECINFO_TYPE"][_COLUMN]] = unicode(securityAcct.getSecurityType())
                                                    _row[dataKeys["_SECINFO_SUBTYPE"][_COLUMN]] = securityAcct.getSecuritySubType()

                                                    if securityAcct.getSecurityType() == SecurityType.STOCK:
                                                        _row[dataKeys["_SECINFO_STK_DIV"][_COLUMN]] = "" if (securityAcct.getDividend() == 0) else acctCurr.format(securityAcct.getDividend(), GlobalVars.decimalCharSep)

                                                    if securityAcct.getSecurityType() == SecurityType.MUTUAL: pass

                                                    if securityAcct.getSecurityType() == SecurityType.CD:
                                                        _row[dataKeys["_SECINFO_CD_APR"][_COLUMN]] = "" if (securityAcct.getAPR() == 0.0) else securityAcct.getAPR()
                                                        _row[dataKeys["_SECINFO_CD_COMPOUNDING"][_COLUMN]] = unicode(securityAcct.getCompounding())

                                                        numYearsChoice = ["0.5"]
                                                        for iYears in range(1, 51): numYearsChoice.append(str(iYears))
                                                        _row[dataKeys["_SECINFO_CD_YEARS"][_COLUMN]] = numYearsChoice[-1] if (len(numYearsChoice) < securityAcct.getNumYears()) else numYearsChoice[securityAcct.getNumYears()]

                                                    if securityAcct.getSecurityType() == SecurityType.BOND:
                                                        bondTypes = [MD_REF.getUI().getStr("gov_bond"), MD_REF.getUI().getStr("mun_bond"), MD_REF.getUI().getStr("corp_bond"), MD_REF.getUI().getStr("zero_bond")]

                                                        _row[dataKeys["_SECINFO_BOND_TYPE"][_COLUMN]] = "ERROR" if (securityAcct.getBondType() > len(bondTypes)) else bondTypes[securityAcct.getBondType()]
                                                        _row[dataKeys["_SECINFO_BOND_FACEVALUE"][_COLUMN]] = "" if (securityAcct.getFaceValue() == 0) else acctCurr.format(securityAcct.getFaceValue(), GlobalVars.decimalCharSep)
                                                        _row[dataKeys["_SECINFO_BOND_APR"][_COLUMN]] = "" if (securityAcct.getAPR() == 0.0) else securityAcct.getAPR()

                                                        if (securityAcct.getMaturity() != 0 and securityAcct.getMaturity() != 39600000):
                                                            _row[dataKeys["_SECINFO_BOND_MATURITYDATE"][_COLUMN]] = DateUtil.convertLongDateToInt(securityAcct.getMaturity())

                                                    if securityAcct.getSecurityType() == SecurityType.OPTION:
                                                        _row[dataKeys["_SECINFO_STKOPT_CALLPUT"][_COLUMN]] = "Put" if securityAcct.getPut() else "Call"
                                                        _row[dataKeys["_SECINFO_STKOPT_STKPRICE"][_COLUMN]] = "" if (securityAcct.getOptionPrice() == 0.0) else securityAcct.getOptionPrice()
                                                        _row[dataKeys["_SECINFO_STKOPT_EXPRICE"][_COLUMN]] = "" if (securityAcct.getStrikePrice()) == 0 else acctCurr.format(securityAcct.getStrikePrice(), GlobalVars.decimalCharSep)

                                                        monthOptions = [MD_REF.getUI().getStr("january"), MD_REF.getUI().getStr("february"), MD_REF.getUI().getStr("march"), MD_REF.getUI().getStr("april"), MD_REF.getUI().getStr("may"), MD_REF.getUI().getStr("june"), MD_REF.getUI().getStr("july"), MD_REF.getUI().getStr("august"), MD_REF.getUI().getStr("september"), MD_REF.getUI().getStr("october"), MD_REF.getUI().getStr("november"), MD_REF.getUI().getStr("december")]
                                                        _row[dataKeys["_SECINFO_STKOPT_EXMONTH"][_COLUMN]] = "ERROR" if (securityAcct.getMonth() > len(monthOptions)) else monthOptions[securityAcct.getMonth()]

                                                    if securityAcct.getSecurityType() == SecurityType.OTHER: pass

                                                except: pass

                                        else:
                                            _row[dataKeys["_SECURITY"][_COLUMN]] = ""
                                            _row[dataKeys["_SECURITYID"][_COLUMN]] = ""
                                            _row[dataKeys["_SECCURR"][_COLUMN]] = ""
                                            _row[dataKeys["_TICKER"][_COLUMN]] = ""
                                            _row[dataKeys["_SHARES"][_COLUMN]] = 0
                                            _row[dataKeys["_PRICE"][_COLUMN]] = 0
                                            _row[dataKeys["_AVGCOST"][_COLUMN]] = ""
                                            _row[dataKeys["_SECSHRHOLDING"][_COLUMN]] = 0

                                        if lAdjustForSplits and securityTxn and _row[dataKeys["_SHARES"][_COLUMN]] != 0:
                                            # Here we go.....
                                            _row[dataKeys["_SHRSAFTERSPLIT"][_COLUMN]] = _row[dataKeys["_SHARES"][_COLUMN]]
                                            stockSplits = securityCurr.getSplits()
                                            if stockSplits and len(stockSplits)>0:
                                                # Here we really go....1

                                                myPrint("D", _THIS_EXTRACT_NAME, securityCurr, " - Found share splits...")
                                                myPrint("D", _THIS_EXTRACT_NAME, securityTxn)

                                                stockSplits = sorted(stockSplits, key=lambda x: x.getDateInt(), reverse=True)   # Sort date newest first...
                                                for theSplit in stockSplits:
                                                    if _row[dataKeys["_DATE"][_COLUMN]] >= theSplit.getDateInt():
                                                        continue
                                                    myPrint("D", _THIS_EXTRACT_NAME, securityCurr, " -  ShareSplits()... Applying ratio.... *", theSplit.getSplitRatio(), "Shares before:",  _row[dataKeys["_SHRSAFTERSPLIT"][_COLUMN]])
                                                    # noinspection PyUnresolvedReferences
                                                    _row[dataKeys["_SHRSAFTERSPLIT"][_COLUMN]] = _row[dataKeys["_SHRSAFTERSPLIT"][_COLUMN]] * theSplit.getSplitRatio()
                                                    myPrint("D", _THIS_EXTRACT_NAME, securityCurr, " - Shares after:",  _row[dataKeys["_SHRSAFTERSPLIT"][_COLUMN]])
                                                    # Keep going if more splits....
                                                    continue


                                        _row[dataKeys["_DESC"][_COLUMN]] = safeStr(txn.getDescription())
                                        _row[dataKeys["_ACTION"][_COLUMN]] = safeStr(txn.getTransferType())
                                        if lParent:
                                            _row[dataKeys["_TT"][_COLUMN]] = safeStr(txn.getInvestTxnType())
                                        else:
                                            _row[dataKeys["_TT"][_COLUMN]] = safeStr(txn.getParentTxn().getInvestTxnType())

                                        _row[dataKeys["_CLEARED"][_COLUMN]] = getStatusCharRevised(txn)

                                        if lParent:
                                            if xfrTxn:
                                                _row[dataKeys["_TRANSFER"][_COLUMN]] = xfrAcct.getFullAccountName()
                                        else:
                                            _row[dataKeys["_TRANSFER"][_COLUMN]] = txn.getParentTxn().getAccount().getFullAccountName()

                                        if lParent:
                                            if securityTxn:
                                                _row[dataKeys["_AMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(securityTxn.getAmount())
                                            else:
                                                _row[dataKeys["_AMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(txn.getValue()) * -1
                                        else:
                                            _row[dataKeys["_AMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(txn.getValue())

                                        if xfrTxn:  # Override the value set above. Why? It's the amount TXF'd out of the account....
                                            _row[dataKeys["_AMOUNT"][_COLUMN]] = (acctCurr.getDoubleValue(xfrTxn.getAmount())) * -1
                                        elif incTxn:
                                            _row[dataKeys["_AMOUNT"][_COLUMN]] = (acctCurr.getDoubleValue(incTxn.getAmount())) * -1
                                        elif expTxn:
                                            _row[dataKeys["_AMOUNT"][_COLUMN]] = (acctCurr.getDoubleValue(expTxn.getAmount())) * -1

                                        _row[dataKeys["_CHEQUE"][_COLUMN]] = safeStr(txn.getCheckNumber())
                                        if lParent:
                                            _row[dataKeys["_MEMO"][_COLUMN]] = safeStr(txn.getMemo())
                                        else:
                                            _row[dataKeys["_MEMO"][_COLUMN]] = safeStr(txn.getParentTxn().getMemo())

                                        if expTxn:
                                            _row[dataKeys["_CAT"][_COLUMN]] = expAcct.getFullAccountName()

                                        if incTxn:
                                            _row[dataKeys["_CAT"][_COLUMN]] = incAcct.getFullAccountName()

                                        if feeTxn:
                                            _row[dataKeys["_FEECAT"][_COLUMN]] = feeAcct.getFullAccountName()

                                        if incTxn:
                                            if feeTxn:
                                                _row[dataKeys["_FEE"][_COLUMN]] = acctCurr.getDoubleValue(feeTxn.getAmount())
                                                _row[dataKeys["_TXNNETAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(incTxn.getAmount()*-1 + feeTxn.getAmount()*-1)

                                                # # Match Moneydance bug - until MD is fixed
                                                # if lParent and str(txn.getTransferType()) == "xfrtp_miscincexp" and str(txn.getInvestTxnType()) == "MISCINC" \
                                                #         and not xfrTxn and feeTxn:
                                                #     row[dataKeys["_FEE"][_COLUMN]] = acctCurr.getDoubleValue(feeTxn.getAmount())
                                                #     row[dataKeys["_TXNNETAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(txn.getValue() + feeTxn.getAmount()*-1)

                                            else:
                                                _row[dataKeys["_TXNNETAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(incTxn.getAmount()*-1)

                                        elif expTxn:
                                            if feeTxn:
                                                _row[dataKeys["_FEE"][_COLUMN]] = acctCurr.getDoubleValue(feeTxn.getAmount())
                                                _row[dataKeys["_TXNNETAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(expTxn.getAmount()*-1 + feeTxn.getAmount())

                                                # Match Moneydance bug - until MD is fixed
                                                if lParent and str(txn.getTransferType()) == "xfrtp_miscincexp" and str(txn.getInvestTxnType()) == "MISCEXP" \
                                                        and not xfrTxn and feeTxn:
                                                    _row[dataKeys["_FEE"][_COLUMN]] = acctCurr.getDoubleValue(feeTxn.getAmount())
                                                    _row[dataKeys["_TXNNETAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(txn.getValue())

                                            else:
                                                _row[dataKeys["_TXNNETAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(expTxn.getAmount()*-1)
                                        elif securityTxn:
                                            if feeTxn:
                                                _row[dataKeys["_FEE"][_COLUMN]] = acctCurr.getDoubleValue(feeTxn.getAmount())
                                                _row[dataKeys["_TXNNETAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(securityTxn.getAmount() + feeTxn.getAmount())
                                            else:
                                                _row[dataKeys["_TXNNETAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(securityTxn.getAmount())
                                        else:
                                            if feeTxn:
                                                _row[dataKeys["_FEE"][_COLUMN]] = acctCurr.getDoubleValue(feeTxn.getAmount())
                                                _row[dataKeys["_TXNNETAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(txn.getValue() + feeTxn.getAmount())
                                            else:
                                                _row[dataKeys["_TXNNETAMOUNT"][_COLUMN]] = acctCurr.getDoubleValue(txn.getValue())

                                        if _row[dataKeys["_SHARES"][_COLUMN]] != 0:
                                            # roundPrice = securityCurr.getDecimalPlaces()
                                            # noinspection PyUnresolvedReferences
                                            price = ((_row[dataKeys["_AMOUNT"][_COLUMN]] / (_row[dataKeys["_SHARES"][_COLUMN]])))
                                            _row[dataKeys["_PRICE"][_COLUMN]] = price
                                            # price = None

                                            if lAdjustForSplits:
                                                # noinspection PyUnresolvedReferences
                                                price = ((_row[dataKeys["_AMOUNT"][_COLUMN]] / (_row[dataKeys["_SHRSAFTERSPLIT"][_COLUMN]])))
                                                _row[dataKeys["_PRICEAFTERSPLIT"][_COLUMN]] = price
                                                # price = None

                                        if lParent and (str(txn.getInvestTxnType()) == "SELL_XFER" or str(txn.getInvestTxnType()) == "BUY_XFER"
                                                        or str(txn.getInvestTxnType()) == "DIVIDEND_REINVEST" or str(txn.getInvestTxnType()) == "DIVIDENDXFR"):
                                            _row[dataKeys["_CASHIMPACT"][_COLUMN]] = 0.0
                                        elif incTxn or expTxn:
                                            _row[dataKeys["_CASHIMPACT"][_COLUMN]] = _row[dataKeys["_TXNNETAMOUNT"][_COLUMN]]
                                        elif securityTxn:
                                            _row[dataKeys["_CASHIMPACT"][_COLUMN]] = _row[dataKeys["_TXNNETAMOUNT"][_COLUMN]]*-1
                                        else:
                                            _row[dataKeys["_CASHIMPACT"][_COLUMN]] = _row[dataKeys["_TXNNETAMOUNT"][_COLUMN]]

                                        _row[dataKeys["_HASATTACHMENTS"][_COLUMN]] = txn.hasAttachments()

                                        _row[dataKeys["_ACCTCASHBAL"][_COLUMN]] = acctCurr.getDoubleValue(txnAcct.getBalance())

                                        # row[dataKeys["_CURRDPC"][_COLUMN]] = acctCurr.getDecimalPlaces()
                                        # row[dataKeys["_SECDPC"][_COLUMN]] = securityCurr.getDecimalPlaces()

                                        if securityTxn:
                                            _row[dataKeys["_AVGCOST"][_COLUMN]] = securityAcct.getUsesAverageCost()

                                        if securityTxn and cbTags:
                                            if not lOmitLOTDataFromExtract_EIT:
                                                lots = []
                                                for cbKey in cbTags.keys():
                                                    relatedCBTxn = book.getTransactionSet().getTxnByID(cbKey)
                                                    if relatedCBTxn is not None:
                                                        lots.append([cbKey,
                                                                     relatedCBTxn.getTransferType(),
                                                                     relatedCBTxn.getOtherTxn(0).getInvestTxnType(),
                                                                     relatedCBTxn.getDateInt(),
                                                                     acctCurr.formatSemiFancy(relatedCBTxn.getValue(), GlobalVars.decimalCharSep),
                                                                     acctCurr.getDoubleValue(relatedCBTxn.getAmount()),
                                                                     ])
                                                # endfor
                                                if len(lots) > 0:
                                                    _row[dataKeys["_LOTS"][_COLUMN]] = lots

                                        # ATTACHMENT ROUTINE
                                        holdTheKeys = ArrayList()
                                        holdTheLocations = ArrayList()

                                        if lExtractAttachments_EIT and txn.hasAttachments():

                                            masterRowCopy = deepcopy(_row)

                                            # noinspection PyUnresolvedReferences
                                            holdTheKeys = holdTheKeys + txn.getAttachmentKeys()
                                            for _attachKey in txn.getAttachmentKeys():
                                                # noinspection PyUnresolvedReferences
                                                holdTheLocations.append(txn.getAttachmentTag(_attachKey))

                                            # ok, we should still be on the first record here.... and we want to download attachments....
                                            attachmentFileList= []
                                            attachmentKeys = holdTheKeys                                                # noqa
                                            attachmentLocations = holdTheLocations
                                            uniqueFileString = " " * 5
                                            for attachmentLocation in attachmentLocations:
                                                uniqueFileString = str(uniqueFileNumber).strip().zfill(5)
                                                outputFile = os.path.join(attachmentDir,str(uniqueFileString)+"-"+os.path.basename(attachmentLocation) )
                                                try:
                                                    _ostr = FileOutputStream( File(outputFile) )
                                                    bytesCopied = _local_storage.readFile(attachmentLocation, _ostr)
                                                    _ostr.close()
                                                    myPrint("DB", _THIS_EXTRACT_NAME + "Attachment %s bytes >> %s copied to %s" %(bytesCopied, attachmentLocation,outputFile))
                                                    attachmentFileList.append(outputFile)
                                                    iCountAttachmentsDownloaded += 1
                                                    lDidIUseAttachmentDir = True
                                                except:
                                                    iAttachmentErrors += 1
                                                    myPrint("B", _THIS_EXTRACT_NAME + "ERROR - Could not extract %s" %(attachmentLocation))

                                                uniqueFileNumber += 1

                                            if len(attachmentFileList) < 1:
                                                myPrint("B", _THIS_EXTRACT_NAME + "@@ Major Error whilst searching attachments! Will just move on to next record and skip attachment")
                                                masterRowCopy[dataKeys["_ATTACHMENTLINK"][_COLUMN]] = "*ERROR*"
                                                myPrint("B", _THIS_EXTRACT_NAME, masterRowCopy)
                                                GlobalVars.transactionTable.append(masterRowCopy)
                                                keyIndex += 1
                                                iCount += 1
                                                continue

                                            for _i in range(0, len(attachmentFileList)):
                                                rowCopy = deepcopy(masterRowCopy)  # Otherwise passes by references and future changes affect the original(s)

                                                if _i > 0:  # If not on first record, update the key...
                                                    rowCopy[dataKeys["_KEY"][_COLUMN]] = txnKey + "-" + str(keyIndex).zfill(3)

                                                if _i == 1:
                                                    # Nuke repeated rows for Attachments (so totals are still OK)
                                                    rowCopy[dataKeys["_SHARES"][_COLUMN]] = None
                                                    rowCopy[dataKeys["_PRICE"][_COLUMN]] = None
                                                    rowCopy[dataKeys["_AMOUNT"][_COLUMN]] = None
                                                    rowCopy[dataKeys["_FEE"][_COLUMN]] = None
                                                    rowCopy[dataKeys["_FEECAT"][_COLUMN]] = None
                                                    rowCopy[dataKeys["_TXNNETAMOUNT"][_COLUMN]] = None
                                                    rowCopy[dataKeys["_CASHIMPACT"][_COLUMN]] = None
                                                    rowCopy[dataKeys["_SHRSAFTERSPLIT"][_COLUMN]] = None
                                                    rowCopy[dataKeys["_PRICEAFTERSPLIT"][_COLUMN]] = None
                                                    rowCopy[dataKeys["_LOTS"][_COLUMN]] = None
                                                    rowCopy[dataKeys["_ACCTCASHBAL"][_COLUMN]] = None
                                                    rowCopy[dataKeys["_SECSHRHOLDING"][_COLUMN]] = None

                                                rowCopy[dataKeys["_ATTACHMENTLINK"][_COLUMN]] = '=HYPERLINK("'+attachmentFileList[_i]+'","FILE: '+os.path.basename(attachmentFileList[_i])[len(uniqueFileString)+1:]+'")'
                                                rowCopy[dataKeys["_ATTACHMENTLINKREL"][_COLUMN]] = '=HYPERLINK("'+os.path.join(".",relativePath,os.path.basename(attachmentFileList[_i]))+'","FILE: '+os.path.basename(attachmentFileList[_i])[len(uniqueFileString)+1:]+'")'

                                                GlobalVars.transactionTable.append(rowCopy)

                                                keyIndex += 1
                                                iCount += 1

                                        # END ATTACHMENT ROUTINE
                                        else:
                                            myPrint("D", _THIS_EXTRACT_NAME, _row)
                                            GlobalVars.transactionTable.append(_row)
                                            iCount += 1

                                    if (lIncludeOpeningBalances or lIncludeBalanceAdjustments) and len(copyValidAccountList) > 0:
                                        myPrint("DB", _THIS_EXTRACT_NAME + "Now iterating remaining %s Accounts with no txns for opening balances / manual adjustments (MD2023 onwards)...." %(len(copyValidAccountList)))

                                        # Yes I should just move this section from above so the code is not inefficient....
                                        for acctBal in copyValidAccountList:
                                            acctCurr = acctBal.getCurrencyType()  # Currency of the Investment Account
                                            openBal = acctCurr.getDoubleValue(getUnadjustedStartBalance(acctBal))
                                            if (lIncludeOpeningBalances):
                                                if openBal != 0:
                                                    iBal+=1
                                                    _row = ([None] * dataKeys["_END"][0])  # Create a blank row to be populated below...
                                                    _row[dataKeys["_ACCOUNT"][_COLUMN]] = acctBal.getFullAccountName()
                                                    _row[dataKeys["_CURR"][_COLUMN]] = acctCurr.getIDString()
                                                    _row[dataKeys["_DESC"][_COLUMN]] = "MANUAL (UNADJUSTED) OPENING BALANCE"
                                                    _row[dataKeys["_ACTION"][_COLUMN]] = "OpenBal"
                                                    _row[dataKeys["_TT"][_COLUMN]] = "MANUAL"
                                                    _row[dataKeys["_DATE"][_COLUMN]] = acctBal.getCreationDateInt()
                                                    _row[dataKeys["_AMOUNT"][_COLUMN]] = openBal
                                                    _row[dataKeys["_CASHIMPACT"][_COLUMN]] = openBal
                                                    _row[dataKeys["_ACCTCASHBAL"][_COLUMN]] = acctCurr.getDoubleValue(acctBal.getBalance())

                                                    myPrint("D", _THIS_EXTRACT_NAME, _row)
                                                    GlobalVars.transactionTable.append(_row)
                                                    del openBal

                                            if (lIncludeBalanceAdjustments):
                                                adjBal = acctCurr.getDoubleValue(getBalanceAdjustment(acctBal))
                                                if adjBal != 0:
                                                    iBal += 1
                                                    _row = ([None] * dataKeys["_END"][0])  # Create a blank row to be populated below...
                                                    _row[dataKeys["_ACCOUNT"][_COLUMN]] = acctBal.getFullAccountName()
                                                    _row[dataKeys["_CURR"][_COLUMN]] = acctCurr.getIDString()
                                                    _row[dataKeys["_DESC"][_COLUMN]] = "MANUAL BALANCE ADJUSTMENT (MD2023 onwards)"
                                                    _row[dataKeys["_ACTION"][_COLUMN]] = "BalAdj"
                                                    _row[dataKeys["_TT"][_COLUMN]] = "MANUAL"
                                                    _row[dataKeys["_DATE"][_COLUMN]] = DateUtil.getStrippedDateInt()
                                                    _row[dataKeys["_AMOUNT"][_COLUMN]] = adjBal
                                                    _row[dataKeys["_CASHIMPACT"][_COLUMN]] = adjBal
                                                    _row[dataKeys["_ACCTCASHBAL"][_COLUMN]] = acctCurr.getDoubleValue(acctBal.getBalance())

                                                    myPrint("D", _THIS_EXTRACT_NAME, _row)
                                                    GlobalVars.transactionTable.append(_row)
                                                    del adjBal

                                    myPrint("B", _THIS_EXTRACT_NAME + "Investment Transaction Records selected:", len(GlobalVars.transactionTable) )

                                    if iCountAttachmentsDownloaded:
                                        myPrint("B", _THIS_EXTRACT_NAME + ".. and I downloaded %s attachments for you too" %iCountAttachmentsDownloaded )

                                    if iBal: myPrint("B", _THIS_EXTRACT_NAME + "...and %s Manual Opening Balance / Adjustment (MD2023 onwards) entries created too..." %iBal)

                                    if iAttachmentErrors: myPrint("B", _THIS_EXTRACT_NAME + "@@ ...and %s Attachment Errors..." %iAttachmentErrors)
                                    ###########################################################################################################


                                    # sort the file: Account>Security>Date
                                    if lExtractAttachments_EIT:
                                        GlobalVars.transactionTable = sorted(GlobalVars.transactionTable, key=lambda x: (x[dataKeys["_ACCOUNT"][_COLUMN]],
                                                                                                   x[dataKeys["_DATE"][_COLUMN]],
                                                                                                   x[dataKeys["_KEY"][_COLUMN]]))
                                    else:
                                        GlobalVars.transactionTable = sorted(GlobalVars.transactionTable, key=lambda x: (x[dataKeys["_ACCOUNT"][_COLUMN]],
                                                                                                   x[dataKeys["_DATE"][_COLUMN]]))

                                    ###########################################################################################################


                                    def ExtractDataToFile():
                                        global csvDelimiter
                                        global userdateformat
                                        global lWriteBOMToExportFile_SWSS, lExtractAttachments_EIT, relativePath

                                        myPrint("D", _THIS_EXTRACT_NAME + "In ", inspect.currentframe().f_code.co_name, "()")

                                        headings = []
                                        sortDataFields = sorted(dataKeys.items(), key=lambda x: x[1][_COLUMN])
                                        for i in sortDataFields:
                                            headings.append(i[1][_HEADING])
                                        print

                                        myPrint("DB", _THIS_EXTRACT_NAME + "Now pre-processing the file to convert integer dates and strip non-ASCII if requested....")
                                        for _theRow in GlobalVars.transactionTable:
                                            dateasdate = datetime.datetime.strptime(str(_theRow[dataKeys["_DATE"][_COLUMN]]), "%Y%m%d")  # Convert to Date field
                                            _dateoutput = dateasdate.strftime(userdateformat)
                                            _theRow[dataKeys["_DATE"][_COLUMN]] = _dateoutput

                                            if _theRow[dataKeys["_TAXDATE"][_COLUMN]]:
                                                dateasdate = datetime.datetime.strptime(str(_theRow[dataKeys["_TAXDATE"][_COLUMN]]), "%Y%m%d")  # Convert to Date field
                                                _dateoutput = dateasdate.strftime(userdateformat)
                                                _theRow[dataKeys["_TAXDATE"][_COLUMN]] = _dateoutput

                                            for col in range(0, dataKeys["_SECSHRHOLDING"][_COLUMN]):
                                                _theRow[col] = fixFormatsStr(_theRow[col])

                                        myPrint("B", _THIS_EXTRACT_NAME + "Opening file and writing %s records" %(len(GlobalVars.transactionTable)))


                                        try:
                                            # CSV Writer will take care of special characters / delimiters within fields by wrapping in quotes that Excel will decode
                                            with open(GlobalVars.csvfilename, "wb") as csvfile:  # PY2.7 has no newline parameter so opening in binary; juse "w" and newline='' in PY3.0

                                                if lWriteBOMToExportFile_SWSS:
                                                    csvfile.write(codecs.BOM_UTF8)   # This 'helps' Excel open file with double-click as UTF-8

                                                writer = csv.writer(csvfile, dialect='excel', quoting=csv.QUOTE_MINIMAL, delimiter=fix_delimiter(csvDelimiter))

                                                if csvDelimiter != ",":
                                                    writer.writerow(["sep=", ""])  # Tells Excel to open file with the alternative delimiter (it will add the delimiter to this line)

                                                if lExtractAttachments_EIT and Platform.isOSX():
                                                    writer.writerow([""])
                                                    writer.writerow(["** On a Mac with Later versions of Excel, Apple 'Sand Boxing' prevents file access..."])
                                                    writer.writerow(["** Edit this cell below, then press Enter and it will change to a Hyperlink (blue)"])
                                                    writer.writerow(["** Click it, then Open, and then GRANT access to the folder.... (the links below will then work)"])
                                                    writer.writerow([""])
                                                    # writer.writerow(["FILE://" + os.path.join(".",relativePath)])
                                                    writer.writerow(["FILE://" + GlobalVars.scriptpath])
                                                    # writer.writerow(["FILE:///"])  # This attempts to allow access to whole folder subsystem....
                                                    writer.writerow([""])

                                                if lExtractAttachments_EIT:
                                                    if debug:
                                                        writer.writerow(headings[:dataKeys["_END"][_COLUMN]])  # Print the header, but not the extra _field headings
                                                    else:
                                                        writer.writerow(headings[:dataKeys["_KEY"][_COLUMN]])  # Print the header, but not the extra _field headings
                                                else:
                                                    writer.writerow(headings[:dataKeys["_ATTACHMENTLINKREL"][_COLUMN]])  # Print the header, but not the extra _field headings

                                                try:
                                                    for i in range(0, len(GlobalVars.transactionTable)):
                                                        if lExtractAttachments_EIT:
                                                            if debug:
                                                                writer.writerow(GlobalVars.transactionTable[i][:dataKeys["_END"][_COLUMN]])
                                                            else:
                                                                writer.writerow(GlobalVars.transactionTable[i][:dataKeys["_KEY"][_COLUMN]])
                                                        else:
                                                            writer.writerow(GlobalVars.transactionTable[i][:dataKeys["_ATTACHMENTLINKREL"][_COLUMN]])
                                                except:
                                                    _msgTxt = _THIS_EXTRACT_NAME + "@@ ERROR writing to CSV on row %s. Please review console" %(i)
                                                    GlobalVars.AUTO_MESSAGES.append(_msgTxt)
                                                    myPrint("B", _msgTxt)
                                                    myPrint("B", _THIS_EXTRACT_NAME, GlobalVars.transactionTable[i])
                                                    raise

                                                if lWriteParametersToExportFile_SWSS:
                                                    today = Calendar.getInstance()
                                                    writer.writerow([""])
                                                    writer.writerow(["StuWareSoftSystems - " + GlobalVars.thisScriptName + "(build: "
                                                                     + version_build
                                                                     + ")  Moneydance Python Script - Date of Extract: "
                                                                     + str(GlobalVars.sdf.format(today.getTime()))])

                                                    writer.writerow([""])
                                                    writer.writerow(["Dataset path/name: %s" %(MD_REF.getCurrentAccountBook().getRootFolder()) ])

                                                    writer.writerow([""])
                                                    writer.writerow(["User Parameters..."])

                                                    writer.writerow(["Hiding Hidden Securities...........: %s" %(hideHiddenSecurities)])
                                                    writer.writerow(["Hiding Inactive Accounts...........: %s" %(hideInactiveAccounts)])
                                                    writer.writerow(["Hiding Hidden Accounts.............: %s" %(hideHiddenAccounts)])
                                                    writer.writerow(["Security filter....................: %s '%s'" %(lAllSecurity,filterForSecurity)])
                                                    writer.writerow(["Account filter.....................: %s '%s'" %(lAllAccounts,filterForAccounts)])
                                                    writer.writerow(["Currency filter....................: %s '%s'" %(lAllCurrency,filterForCurrency)])

                                                    writer.writerow(["Txn Date filter....................: %s %s" %(lFilterDateRange_EIT,
                                                                     "" if (not lFilterDateRange_EIT) else "(start date: %s, end date: %s"
                                                                                   %(convertStrippedIntDateFormattedText(filterDateStart_EIT),
                                                                                     convertStrippedIntDateFormattedText(filterDateEnd_EIT)))])

                                                    writer.writerow(["Include Unadjusted Opening Balances: %s" %(lIncludeOpeningBalances)])
                                                    writer.writerow(["Include Balance Adjustments........: %s" %(lIncludeBalanceAdjustments)])
                                                    writer.writerow(["Adjust for Splits..................: %s" %(lAdjustForSplits)])
                                                    writer.writerow(["Split Securities by Account........: %s" %(userdateformat)])
                                                    writer.writerow(["Omit LOT matching data.............: %s" %(lOmitLOTDataFromExtract_EIT)])
                                                    writer.writerow(["Extract extra Sec Acct Info........: %s" %(lExtractExtraSecurityAcctInfo)])
                                                    writer.writerow(["Download Attachments...............: %s" %(lExtractAttachments_EIT)])

                                            _msgTxt = _THIS_EXTRACT_NAME + "CSV file: '%s' created (%s records)" %(GlobalVars.csvfilename, len(GlobalVars.transactionTable))
                                            myPrint("B", _msgTxt)
                                            GlobalVars.AUTO_MESSAGES.append(_msgTxt)
                                            GlobalVars.countFilesCreated += 1

                                        except:
                                            e_type, exc_value, exc_traceback = sys.exc_info()                           # noqa
                                            _msgTxt = _THIS_EXTRACT_NAME + "@@ ERROR '%s' detected writing file: '%s' - Extract ABORTED!" %(exc_value, GlobalVars.csvfilename)
                                            GlobalVars.AUTO_MESSAGES.append(_msgTxt)
                                            myPrint("B", _msgTxt)
                                            raise

                                    def fixFormatsStr(theString, lNumber=False, sFormat=""):
                                        if isinstance(theString, bool): return theString
                                        if isinstance(theString, tuple): return theString
                                        if isinstance(theString, dict): return theString
                                        if isinstance(theString, list): return theString

                                        if isinstance(theString, int) or isinstance(theString, float) or isinstance(theString, long):
                                            lNumber = True

                                        if lNumber is None: lNumber = False
                                        if theString is None: theString = ""

                                        if sFormat == "%" and theString != "":
                                            theString = "{:.1%}".format(theString)
                                            return theString

                                        if lNumber: return str(theString)

                                        theString = theString.strip()  # remove leading and trailing spaces

                                        theString = theString.replace("\n", "*")  # remove newlines within fields to keep csv format happy
                                        theString = theString.replace("\t", "*")  # remove tabs within fields to keep csv format happy
                                        # theString = theString.replace(";", "*")  # remove tabs within fields to keep csv format happy
                                        # theString = theString.replace(",", "*")  # remove tabs within fields to keep csv format happy
                                        # theString = theString.replace("|", "*")  # remove tabs within fields to keep csv format happy

                                        if lStripASCII:
                                            all_ASCII = ''.join(char for char in theString if ord(char) < 128)  # Eliminate non ASCII printable Chars too....
                                        else:
                                            all_ASCII = theString
                                        return all_ASCII

                                    if len(GlobalVars.transactionTable) > 0:

                                        ExtractDataToFile()

                                        if not GlobalVars.lGlobalErrorDetected:
                                            xtra_msg=""
                                            if lDidIUseAttachmentDir:

                                                baseName = os.path.basename(GlobalVars.csvfilename)
                                                lShell = None
                                                theCommand = None

                                                if not Platform.isWindows():
                                                    theCommand = 'zip -v -r "%s" "%s" "%s"' %(os.path.splitext(baseName)[0]+".zip",
                                                                                              baseName,
                                                                                              os.path.join(os.path.splitext(baseName)[0],""))

                                                    lShell = True
                                                else:
                                                    try:
                                                        if float(System.getProperty("os.version")) >= 10:
                                                            theCommand = 'tar -a -cvf "%s" "%s" "%s"' %(os.path.splitext(baseName)[0]+".zip",
                                                                                                        baseName,
                                                                                                        os.path.join(os.path.splitext(baseName)[0],"*.*"))

                                                            lShell = False
                                                    except: pass
                                                try:
                                                    if theCommand:
                                                        os.chdir(GlobalVars.scriptpath)
                                                        xx = subprocess.check_output( theCommand, shell=lShell)
                                                        myPrint("B", _THIS_EXTRACT_NAME + "Created zip using command: %s (output follows)" %theCommand)
                                                        myPrint("B", xx)
                                                        xtra_msg = _THIS_EXTRACT_NAME + "\n(and I also zipped the file - review console / log for any messages)"
                                                except:
                                                    myPrint("B", _THIS_EXTRACT_NAME + "Sorry, failed to create zip")
                                                    xtra_msg = _THIS_EXTRACT_NAME + "\n(with an error creating the zip file - review console / log for messages)"

                                            sTxt = "Extract file CREATED:"
                                            mTxt = ("With %s rows and %s attachments downloaded %s\n"
                                                    "\n(... and %s Attachment Errors...)" % (len(GlobalVars.transactionTable),iCountAttachmentsDownloaded, xtra_msg,iAttachmentErrors))
                                            myPrint("B", _THIS_EXTRACT_NAME + "%s\n%s" %(sTxt, mTxt))
                                        else:
                                            _msgTextx = _THIS_EXTRACT_NAME + "ERROR Creating extract (review console for error messages)...."
                                            GlobalVars.AUTO_MESSAGES.append(_msgTextx)
                                    else:
                                        _msgTextx = _THIS_EXTRACT_NAME + "@@ No records selected and no extract file created @@"
                                        GlobalVars.AUTO_MESSAGES.append(_msgTextx)
                                        myPrint("B", _msgTextx)
                                        if not GlobalVars.AUTO_EXTRACT_MODE:
                                            DoExtractsSwingWorker.killPleaseWait()
                                            genericSwingEDTRunner(True, True, myPopupInformationBox, extract_data_frame_, _msgTextx, GlobalVars.thisScriptName, JOptionPane.WARNING_MESSAGE)

                                    # Clean up...
                                    if not lDidIUseAttachmentDir and attachmentDir:
                                        try:
                                            os.rmdir(attachmentDir)
                                            myPrint("B", _THIS_EXTRACT_NAME + "REMOVED unused/empty attachment directory: '%s'" %(attachmentDir))
                                        except:
                                            myPrint("B", _THIS_EXTRACT_NAME + "FAILED to remove the unused/empty attachment directory: '%s'" %(attachmentDir))

                                    # delete references to large objects
                                    GlobalVars.transactionTable = None
                                    del accountBalances


                                try:
                                    do_extract_investment_transactions()
                                except:
                                    GlobalVars.lGlobalErrorDetected = True

                                if GlobalVars.lGlobalErrorDetected:
                                    GlobalVars.countErrorsDuringExtract += 1
                                    _txt = _THIS_EXTRACT_NAME + "@@ ERROR: do_extract_investment_transactions() has failed (review console)!"
                                    GlobalVars.AUTO_MESSAGES.append(_txt)
                                    myPrint("B", _txt)
                                    dump_sys_error_to_md_console_and_errorlog()
                                    if not GlobalVars.AUTO_EXTRACT_MODE:
                                        DoExtractsSwingWorker.killPleaseWait()
                                        genericSwingEDTRunner(True, True, myPopupInformationBox, extract_data_frame_, _txt, "ERROR", JOptionPane.ERROR_MESSAGE)
                                        return False
                            #### ENDIF lExtractInvestmentTxns ####

                            if lExtractCurrencyHistory:

                                # ####################################################
                                # EXTRACT_CURRENCY_HISTORY_CSV PARAMETER SCREEN
                                # ####################################################

                                _THIS_EXTRACT_NAME = pad("EXTRACT: Currency History:", 34)
                                GlobalVars.lGlobalErrorDetected = False

                                if not GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE:
                                    self.super__publish([_THIS_EXTRACT_NAME.strip()])                                   # noqa

                                if GlobalVars.AUTO_EXTRACT_MODE:
                                    GlobalVars.csvfilename = os.path.join(GlobalVars.scriptpath, MD_REF.getCurrentAccountBook().getName() + "_" + GlobalVars.defaultFileName_ECH + ".csv")

                                def do_extract_currency_history():
                                    global lDidIUseAttachmentDir

                                    global __extract_data, extract_filename
                                    global lStripASCII, csvDelimiter, userdateformat, lWriteBOMToExportFile_SWSS
                                    global hideInactiveAccounts, hideHiddenAccounts, hideHiddenSecurities
                                    global lAllSecurity, filterForSecurity, lAllAccounts, filterForAccounts, lAllCurrency, filterForCurrency
                                    global whichDefaultExtractToRun_SWSS
                                    global lSimplify_ECH, userdateStart_ECH, userdateEnd_ECH, hideHiddenCurrencies_ECH


                                    myPrint("DB", _THIS_EXTRACT_NAME + "\nScript running to extract your currency rate history....")
                                    myPrint("DB", _THIS_EXTRACT_NAME + "-------------------------------------------------------------------")

                                    header = ["CurrencyName",
                                              "CurrencyID",
                                              "isBase",
                                              "DecimalPlaces",
                                              "Prefix",
                                              "Suffix",
                                              "CurrentRateR2B",
                                              "CurrentRateB2R",
                                              "Snap_Date",
                                              "Snap_DailyRateR2B",
                                              "Snap_DailyRateB2R"]

                                    def list_currency_rate_history():
                                        global hideHiddenCurrencies_ECH, lSimplify_ECH, userdateStart_ECH, userdateEnd_ECH

                                        curr_table = []

                                        currencies = MD_REF.getCurrentAccountBook().getCurrencies()
                                        baseCurr = currencies.getBaseType()

                                        myPrint("DB", _THIS_EXTRACT_NAME + "\nIterating the currency table...")
                                        for curr in currencies:

                                            # noinspection PyUnresolvedReferences
                                            if curr.getCurrencyType() != CurrencyType.Type.CURRENCY: continue   # Skip if not on a Currency record (i.e. a Security)

                                            if hideHiddenCurrencies_ECH and curr.getHideInUI(): continue   # Skip if hidden in MD

                                            myPrint("DB", _THIS_EXTRACT_NAME + "Currency: %s %s" %(curr, curr.getPrefix()) )

                                            currSnapshots = curr.getSnapshots()

                                            if not lSimplify_ECH and not len(currSnapshots) and curr == baseCurr:

                                                row = []                                                                # noqa

                                                row.append((curr.getName()))
                                                row.append((curr.getIDString()))
                                                row.append(curr == baseCurr)
                                                row.append(curr.getDecimalPlaces())
                                                row.append((curr.getPrefix()))
                                                row.append((curr.getSuffix()))
                                                row.append(1)
                                                row.append(1)
                                                row.append(None)
                                                row.append(None)
                                                row.append(None)
                                                curr_table.append(row)

                                            dpc = 8   # Override to 8dpc


                                            for currSnapshot in currSnapshots:
                                                if currSnapshot.getDateInt() < userdateStart_ECH \
                                                        or currSnapshot.getDateInt() > userdateEnd_ECH:
                                                    continue   # Skip if out of date range

                                                row = []                                                                # noqa

                                                row.append((curr.getName()))
                                                row.append((curr.getIDString()))
                                                row.append(curr == baseCurr)
                                                row.append(curr.getDecimalPlaces())
                                                row.append((curr.getPrefix()))
                                                row.append((curr.getSuffix()))
                                                row.append(round(float(curr.getParameter("rate", None)),dpc))
                                                row.append(round(1/float(curr.getParameter("rate", None)),dpc))

                                                # I don't print relative currency as it's supposed to always be None or = Base..

                                                row.append(currSnapshot.getDateInt())
                                                row.append(round(float(currSnapshot.getRate()),dpc))
                                                row.append(round(1/float(currSnapshot.getRate()),dpc))

                                                curr_table.append(row)

                                        return curr_table

                                    currencyTable = list_currency_rate_history()

                                    def ExtractDataToFile(theTable, _header):                                           # noqa
                                        global csvDelimiter, userdateformat, lWriteBOMToExportFile_SWSS

                                        myPrint("D", _THIS_EXTRACT_NAME + "In ", inspect.currentframe().f_code.co_name, "()")

                                        _CURRNAME = 0
                                        _CURRID = 1
                                        _SYMB =4
                                        _SNAPDATE = 8

                                        if True:
                                            theTable = sorted(theTable, key=lambda x: (safeStr(x[_CURRNAME]).upper(),x[_SNAPDATE]))

                                        myPrint("DB", _THIS_EXTRACT_NAME + "Now pre-processing the file to convert integer dates to 'formatted' dates....")
                                        for row in theTable:                                                            # noqa
                                            try:
                                                if row[_SNAPDATE]:
                                                    dateasdate = datetime.datetime.strptime(str(row[_SNAPDATE]),"%Y%m%d")  # Convert to Date field
                                                    _dateoutput = dateasdate.strftime(userdateformat)
                                                    row[_SNAPDATE] = _dateoutput

                                            except:
                                                myPrint("B", _THIS_EXTRACT_NAME + "Error on row below with curr:", row[_CURRNAME], "snap date:", row[_SNAPDATE])
                                                myPrint("B", _THIS_EXTRACT_NAME, row)
                                                continue

                                            if lStripASCII:
                                                for col in range(0, len(row)):
                                                    row[col] = fixFormatsStr(row[col])

                                        theTable.insert(0,_header)  # Insert Column Headings at top of list. A bit rough and ready, not great coding, but a short list...!

                                        # Write the theTable to a file
                                        myPrint("B", _THIS_EXTRACT_NAME + "Opening file and writing %s records" %(len(theTable)))

                                        try:
                                            # CSV Writer will take care of special characters / delimiters within fields by wrapping in quotes that Excel will decode
                                            # with open(GlobalVars.csvfilename, "wb") as csvfile:  # PY2.7 has no newline parameter so opening in binary; just use "w" and newline='' in PY3.0
                                            with open(GlobalVars.csvfilename, "wb") as csvfile:  # PY2.7 has no newline parameter so opening in binary; just use "w" and newline='' in PY3.0

                                                if lWriteBOMToExportFile_SWSS:
                                                    csvfile.write(codecs.BOM_UTF8)   # This 'helps' Excel open file with double-click as UTF-8

                                                writer = csv.writer(csvfile, dialect='excel', quoting=csv.QUOTE_MINIMAL, delimiter=fix_delimiter(csvDelimiter))

                                                if csvDelimiter != ",":
                                                    writer.writerow(["sep=",""])  # Tells Excel to open file with the alternative delimiter (it will add the delimiter to this line)

                                                if not lSimplify_ECH:
                                                    try:
                                                        for i in range(0, len(theTable)):
                                                            try:
                                                                writer.writerow( theTable[i] )
                                                            except:
                                                                myPrint("B", _THIS_EXTRACT_NAME + "Error writing row %s to file... Older Jython version?" %i)
                                                                myPrint("B", _THIS_EXTRACT_NAME + "Row: ", theTable[i])
                                                                myPrint("B", _THIS_EXTRACT_NAME + "Will attempt coding back to str()..... Let's see if this fails?!")
                                                                for _col in range(0, len(theTable[i])):
                                                                    theTable[i][_col] = fix_delimiter(theTable[i][_col])
                                                                writer.writerow( theTable[i] )
                                                    except:
                                                        _msgTxt = _THIS_EXTRACT_NAME + "@@ ERROR writing to CSV on row %s. Please review console" %(i)
                                                        GlobalVars.AUTO_MESSAGES.append(_msgTxt)
                                                        myPrint("B", _msgTxt)
                                                        myPrint("B", _THIS_EXTRACT_NAME, theTable[i])
                                                        raise

                                                    if lWriteParametersToExportFile_SWSS:
                                                        today = Calendar.getInstance()
                                                        writer.writerow([""])
                                                        writer.writerow(["StuWareSoftSystems - " + GlobalVars.thisScriptName + "(build: "
                                                                         + version_build
                                                                         + ")  Moneydance Python Script - Date of Extract: "
                                                                         + str(GlobalVars.sdf.format(today.getTime()))])

                                                        writer.writerow([""])
                                                        writer.writerow(["Dataset path/name: %s" %(MD_REF.getCurrentAccountBook().getRootFolder()) ])

                                                        writer.writerow([""])
                                                        writer.writerow(["User Parameters..."])
                                                        writer.writerow(["Simplify Extract...........: %s" %(lSimplify_ECH)])
                                                        writer.writerow(["Hiding Hidden Currencies...: %s" %(hideHiddenCurrencies_ECH)])
                                                        writer.writerow(["Date format................: %s" %(userdateformat)])
                                                        writer.writerow(["Date Range Selected........: "+str(userdateStart_ECH) + " to " +str(userdateEnd_ECH)])

                                                else:
                                                    # Simplify is for my tester 'buddy' DerekKent23 - it's actually an MS Money Import format
                                                    lCurr = None
                                                    try:
                                                        iRowCounter=0
                                                        for row in theTable[1:]:                                        # noqa
                                                            # Write the table, but swap in the raw numbers (rather than formatted number strings)
                                                            if row[_CURRNAME] != lCurr:
                                                                if lCurr: writer.writerow("")
                                                                lCurr = row[_CURRNAME]
                                                                writer.writerow( [fix_delimiter(row[ _CURRNAME])
                                                                                  +" - "+fix_delimiter(row[_CURRID])
                                                                                  +" - "+fix_delimiter(row[_SYMB])
                                                                                  +fix_delimiter(row[_SYMB+1])] )
                                                                writer.writerow(["Date","Base to Rate","Rate to Base"])

                                                            writer.writerow([row[_SNAPDATE],
                                                                             row[_SNAPDATE+1],
                                                                             row[_SNAPDATE+2]])
                                                            iRowCounter += 1
                                                    except:
                                                        _msgTxt = _THIS_EXTRACT_NAME + "@@ ERROR writing to CSV on row %s. Please review console" %(iRowCounter)
                                                        GlobalVars.AUTO_MESSAGES.append(_msgTxt)
                                                        myPrint("B", _msgTxt)
                                                        myPrint("B", _THIS_EXTRACT_NAME, row)
                                                        raise

                                            _msgTxt = _THIS_EXTRACT_NAME + "CSV file: '%s' created (%s records)" %(GlobalVars.csvfilename, len(theTable))
                                            myPrint("B", _msgTxt)
                                            GlobalVars.AUTO_MESSAGES.append(_msgTxt)
                                            GlobalVars.countFilesCreated += 1

                                        except:
                                            e_type, exc_value, exc_traceback = sys.exc_info()                           # noqa
                                            _msgTxt = _THIS_EXTRACT_NAME + "@@ ERROR '%s' detected writing file: '%s' - Extract ABORTED!" %(exc_value, GlobalVars.csvfilename)
                                            GlobalVars.AUTO_MESSAGES.append(_msgTxt)
                                            myPrint("B", _msgTxt)
                                            raise

                                    def fixFormatsStr(theString, lNumber=False, sFormat=""):
                                        if isinstance(theString, bool): return theString

                                        if isinstance(theString, int) or isinstance(theString, float):
                                            lNumber = True

                                        if lNumber is None: lNumber = False
                                        if theString is None: theString = ""

                                        if sFormat == "%" and theString != "":
                                            theString = "{:.1%}".format(theString)
                                            return theString

                                        if lNumber: return str(theString)

                                        theString = theString.strip()  # remove leading and trailing spaces

                                        theString = theString.replace("\n", "*")  # remove newlines within fields to keep csv format happy
                                        theString = theString.replace("\t", "*")  # remove tabs within fields to keep csv format happy

                                        if lStripASCII:
                                            all_ASCII = ''.join(char for char in theString if ord(char) < 128)  # Eliminate non ASCII printable Chars too....
                                        else:
                                            all_ASCII = theString
                                        return all_ASCII

                                    ExtractDataToFile(currencyTable, header)
                                    if not GlobalVars.lGlobalErrorDetected:
                                        _msgTextx = _THIS_EXTRACT_NAME + "Extract file CREATED (%s records)" %(len(currencyTable)+1)
                                        myPrint("B", _msgTextx)
                                    else:
                                        _msgTextx = _THIS_EXTRACT_NAME + "ERROR Creating extract (review console for error messages)...."
                                        GlobalVars.AUTO_MESSAGES.append(_msgTextx)
                                    del currencyTable

                                try:
                                    do_extract_currency_history()
                                except:
                                    GlobalVars.lGlobalErrorDetected = True

                                if GlobalVars.lGlobalErrorDetected:
                                    GlobalVars.countErrorsDuringExtract += 1
                                    _txt = "@@ ERROR: do_extract_currency_history() has failed (review console)!"
                                    GlobalVars.AUTO_MESSAGES.append(_txt)
                                    myPrint("B", _txt)
                                    dump_sys_error_to_md_console_and_errorlog()
                                    if not GlobalVars.AUTO_EXTRACT_MODE:
                                        DoExtractsSwingWorker.killPleaseWait()
                                        genericSwingEDTRunner(True, True, myPopupInformationBox, extract_data_frame_, _txt, "ERROR", JOptionPane.ERROR_MESSAGE)
                                        return False
                            #### ENDIF lExtractCurrencyHistory ####

                            if lExtractSecurityBalances:
                                # ####################################################
                                # EXTRACT_SECURITY_BALANCES_CSV EXECUTION
                                # ####################################################

                                _THIS_EXTRACT_NAME = pad("EXTRACT: Security Balances:", 34)
                                GlobalVars.lGlobalErrorDetected = False

                                if not GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE:
                                    self.super__publish([_THIS_EXTRACT_NAME.strip()])                                   # noqa

                                if GlobalVars.AUTO_EXTRACT_MODE:
                                    GlobalVars.csvfilename = os.path.join(GlobalVars.scriptpath, MD_REF.getCurrentAccountBook().getName() + "_" + GlobalVars.defaultFileName_ESB + ".csv")

                                def do_extract_security_balances():
                                    global dataKeys

                                    global __extract_data, extract_filename
                                    global lStripASCII, csvDelimiter, userdateformat, lWriteBOMToExportFile_SWSS
                                    global hideInactiveAccounts, hideHiddenAccounts, hideHiddenSecurities
                                    global lAllSecurity, filterForSecurity, lAllAccounts, filterForAccounts, lAllCurrency, filterForCurrency
                                    global whichDefaultExtractToRun_SWSS

                                    # noinspection PyArgumentList
                                    class MyAcctFilterESB(AcctFilter):

                                        def __init__(self,
                                                     _hideInactiveAccounts=True,
                                                     _lAllAccounts=True,
                                                     _filterForAccounts="ALL",
                                                     _hideHiddenAccounts=True,
                                                     _hideHiddenSecurities=True,
                                                     _lAllCurrency=True,
                                                     _filterForCurrency="ALL",
                                                     _lAllSecurity=True,
                                                     _filterForSecurity="ALL",
                                                     _findUUID=None):

                                            self.hideInactiveAccounts = _hideInactiveAccounts
                                            self.lAllAccounts = _lAllAccounts
                                            self.filterForAccounts = _filterForAccounts
                                            self.hideHiddenAccounts = _hideHiddenAccounts
                                            self.hideHiddenSecurities = _hideHiddenSecurities
                                            self.lAllCurrency = _lAllCurrency
                                            self.filterForCurrency = _filterForCurrency
                                            self.lAllSecurity = _lAllSecurity
                                            self.filterForSecurity = _filterForSecurity
                                            self.findUUID = _findUUID

                                        def matches(self, acct):
                                            if self.findUUID is not None:  # If UUID supplied, override all other parameters...
                                                if acct.getUUID() == self.findUUID: return True
                                                else: return False

                                            if acct.getAccountType() is not Account.AccountType.SECURITY:               # noqa
                                                return False

                                            if self.hideInactiveAccounts:
                                                # This logic replicates Moneydance AcctFilter.ACTIVE_ACCOUNTS_FILTER
                                                if (acct.getAccountOrParentIsInactive()): return False
                                                if (acct.getHideOnHomePage() and acct.getBalance() == 0): return False

                                            theAcct = acct.getParentAccount()

                                            if (self.lAllAccounts
                                                    or (self.filterForAccounts.upper().strip() in theAcct.getFullAccountName().upper().strip())):
                                                pass
                                            else: return False

                                            if ((not self.hideHiddenAccounts)
                                                    or (self.hideHiddenAccounts and not theAcct.getHideOnHomePage())):
                                                pass
                                            else: return False

                                            curr = acct.getCurrencyType()
                                            currID = curr.getIDString()
                                            currName = curr.getName()

                                            # noinspection PyUnresolvedReferences
                                            if acct.getAccountType() == Account.AccountType.SECURITY:  # on Security Accounts, get the Currency from the Security master - else from the account)
                                                if self.lAllSecurity:
                                                    pass
                                                elif (self.filterForSecurity.upper().strip() in curr.getTickerSymbol().upper().strip()):
                                                    pass
                                                elif (self.filterForSecurity.upper().strip() in curr.getName().upper().strip()):
                                                    pass
                                                else: return False

                                                if ((self.hideHiddenSecurities and not curr.getHideInUI()) or (not self.hideHiddenSecurities)):
                                                    pass
                                                else:
                                                    return False

                                                currID = curr.getRelativeCurrency().getIDString()
                                                currName = curr.getRelativeCurrency().getName()

                                            else:
                                                pass

                                            # All accounts and security records can have currencies
                                            if self.lAllCurrency:
                                                pass
                                            elif (self.filterForCurrency.upper().strip() in currID.upper().strip()):
                                                pass
                                            elif (self.filterForCurrency.upper().strip() in currName.upper().strip()):
                                                pass

                                            else: return False

                                            return True

                                    _COLUMN = 0
                                    _HEADING = 1

                                    usedSecurityMasters = {}

                                    dki = 0
                                    dataKeys = {}                                                                       # noqa
                                    dataKeys["_ACCOUNT"]                   = [dki, "Account"];                      dki += 1
                                    dataKeys["_ACCTCURR"]                  = [dki, "AcctCurrency"];                 dki += 1
                                    dataKeys["_BASECURR"]                  = [dki, "BaseCurrency"];                 dki += 1
                                    dataKeys["_SECURITY"]                  = [dki, "Security"];                     dki += 1
                                    dataKeys["_SECURITYID"]                = [dki, "SecurityID"];                   dki += 1
                                    dataKeys["_TICKER"]                    = [dki, "SecurityTicker"];               dki += 1
                                    dataKeys["_SECMSTRUUID"]               = [dki, "SecurityMasterUUID"];           dki += 1
                                    dataKeys["_AVGCOST"]                   = [dki, "AverageCostControl"];           dki += 1

                                    dataKeys["_SECINFO_TYPE"]              = [dki, "Sec_Type"];                     dki += 1
                                    dataKeys["_SECINFO_SUBTYPE"]           = [dki, "Sec_SubType"];                  dki += 1
                                    dataKeys["_SECINFO_STK_DIV"]           = [dki, "Sec_Stock_Div"];                dki += 1
                                    dataKeys["_SECINFO_CD_APR"]            = [dki, "Sec_CD_APR"];                   dki += 1
                                    dataKeys["_SECINFO_CD_COMPOUNDING"]    = [dki, "Sec_CD_Compounding"];           dki += 1
                                    dataKeys["_SECINFO_CD_YEARS"]          = [dki, "Sec_CD_Years"];                 dki += 1
                                    dataKeys["_SECINFO_BOND_TYPE"]         = [dki, "Sec_Bond_Type"];                dki += 1
                                    dataKeys["_SECINFO_BOND_FACEVALUE"]    = [dki, "Sec_Bond_FaceValue"];           dki += 1
                                    dataKeys["_SECINFO_BOND_MATURITYDATE"] = [dki, "Sec_Bond_MaturityDate"];        dki += 1
                                    dataKeys["_SECINFO_BOND_APR"]          = [dki, "Sec_Bond_APR"];                 dki += 1
                                    dataKeys["_SECINFO_STKOPT_CALLPUT"]    = [dki, "Sec_StockOpt_CallPut"];         dki += 1
                                    dataKeys["_SECINFO_STKOPT_STKPRICE"]   = [dki, "Sec_StockOpt_StockPrice"];      dki += 1
                                    dataKeys["_SECINFO_STKOPT_EXPRICE"]    = [dki, "Sec_StockOpt_ExercisePrice"];   dki += 1
                                    dataKeys["_SECINFO_STKOPT_EXMONTH"]    = [dki, "Sec_StockOpt_ExerciseMonth"];   dki += 1

                                    dataKeys["_SECSHRHOLDING"]             = [dki, "SecurityShareHolding"];         dki += 1
                                    dataKeys["_ACCTCOSTBASIS"]             = [dki, "AcctCostBasis"];                dki += 1
                                    dataKeys["_BASECOSTBASIS"]             = [dki, "BaseCostBasis"];                dki += 1
                                    dataKeys["_CURRENTPRICE"]              = [dki, "CurrentPrice"];                 dki += 1
                                    dataKeys["_SECRELCURR"]                = [dki, "SecurityRelCurrency"];          dki += 1
                                    dataKeys["_CURRENTPRICETOBASE"]        = [dki, "CurrentPriceToBase"];           dki += 1
                                    dataKeys["_CURRENTPRICEINVESTCURR"]    = [dki, "CurrentPriceInvestCurr"];       dki += 1

                                    dataKeys["_CURRENTVALUETOBASE"]        = [dki, "CurrentValueToBase"];           dki += 1
                                    dataKeys["_CURRENTVALUEINVESTCURR"]    = [dki, "CurrentValueInvestCurr"];       dki += 1

                                    dataKeys["_KEY"]                       = [dki, "Key"];                          dki += 1
                                    dataKeys["_END"]                       = [dki, "_END"];                         dki += 1

                                    GlobalVars.transactionTable = []

                                    myPrint("DB", _THIS_EXTRACT_NAME, dataKeys)

                                    book = MD_REF.getCurrentAccountBook()

                                    for sAcct in AccountUtil.allMatchesForSearch(book, MyAcctFilterESB(hideInactiveAccounts,
                                                                                                       lAllAccounts,
                                                                                                       filterForAccounts,
                                                                                                       hideHiddenAccounts,
                                                                                                       hideHiddenSecurities,
                                                                                                       lAllCurrency,
                                                                                                       filterForCurrency,
                                                                                                       lAllSecurity,
                                                                                                       filterForSecurity,
                                                                                                       None)):

                                        if sAcct.getAccountType() is not Account.AccountType.SECURITY: raise Exception("LOGIC ERROR")  # noqa

                                        investAcct = sAcct.getParentAccount()
                                        investAcctCurr = investAcct.getCurrencyType()

                                        securityAcct = sAcct
                                        securityCurr = securityAcct.getCurrencyType()  # the Security master record
                                        del sAcct

                                        _row = ([None] * dataKeys["_END"][0])  # Create a blank row to be populated below...

                                        usedSecurityMasters[securityCurr] = True

                                        _row[dataKeys["_KEY"][_COLUMN]] = ""

                                        _row[dataKeys["_ACCOUNT"][_COLUMN]] = investAcct.getFullAccountName()
                                        _row[dataKeys["_ACCTCURR"][_COLUMN]] = investAcctCurr.getIDString()
                                        _row[dataKeys["_BASECURR"][_COLUMN]] = GlobalVars.baseCurrency.getIDString()

                                        costBasis = InvestUtil.getCostBasis(securityAcct)
                                        costBasisBase = CurrencyUtil.convertValue(costBasis, investAcctCurr, GlobalVars.baseCurrency)

                                        _row[dataKeys["_ACCTCOSTBASIS"][_COLUMN]] = investAcctCurr.getDoubleValue(costBasis)
                                        _row[dataKeys["_BASECOSTBASIS"][_COLUMN]] = GlobalVars.baseCurrency.getDoubleValue(costBasisBase)

                                        _row[dataKeys["_SECURITY"][_COLUMN]] = unicode(securityCurr.getName())
                                        _row[dataKeys["_SECURITYID"][_COLUMN]] = unicode(securityCurr.getIDString())
                                        _row[dataKeys["_SECMSTRUUID"][_COLUMN]] = securityCurr.getUUID()
                                        _row[dataKeys["_TICKER"][_COLUMN]] = unicode(securityCurr.getTickerSymbol())
                                        _row[dataKeys["_AVGCOST"][_COLUMN]] = securityAcct.getUsesAverageCost()

                                        secShrHolding = securityCurr.getDoubleValue(securityAcct.getBalance())
                                        _row[dataKeys["_SECSHRHOLDING"][_COLUMN]] = secShrHolding

                                        _row[dataKeys["_SECRELCURR"][_COLUMN]] = unicode(securityCurr.getRelativeCurrency().getIDString())

                                        cPriceToBase = (1.0 / securityCurr.getBaseRate())                               # same as .getRate(None)
                                        cPriceInvestCurr = (1.0 / securityCurr.getRate(investAcctCurr))

                                        _row[dataKeys["_CURRENTPRICE"][_COLUMN]] = (1.0 / securityCurr.getRelativeRate())
                                        _row[dataKeys["_CURRENTPRICETOBASE"][_COLUMN]] = cPriceToBase
                                        _row[dataKeys["_CURRENTPRICEINVESTCURR"][_COLUMN]] = cPriceInvestCurr

                                        _row[dataKeys["_CURRENTVALUETOBASE"][_COLUMN]] = cPriceToBase * secShrHolding
                                        _row[dataKeys["_CURRENTVALUEINVESTCURR"][_COLUMN]] = cPriceInvestCurr * secShrHolding

                                        _row[dataKeys["_SECINFO_TYPE"][_COLUMN]] = ""
                                        _row[dataKeys["_SECINFO_SUBTYPE"][_COLUMN]] = ""
                                        _row[dataKeys["_SECINFO_STK_DIV"][_COLUMN]] = ""
                                        _row[dataKeys["_SECINFO_CD_APR"][_COLUMN]] = ""
                                        _row[dataKeys["_SECINFO_CD_COMPOUNDING"][_COLUMN]] = ""
                                        _row[dataKeys["_SECINFO_CD_YEARS"][_COLUMN]] = ""
                                        _row[dataKeys["_SECINFO_BOND_TYPE"][_COLUMN]] = ""
                                        _row[dataKeys["_SECINFO_BOND_FACEVALUE"][_COLUMN]] = ""
                                        _row[dataKeys["_SECINFO_BOND_MATURITYDATE"][_COLUMN]] = ""
                                        _row[dataKeys["_SECINFO_BOND_APR"][_COLUMN]] = ""
                                        _row[dataKeys["_SECINFO_STKOPT_CALLPUT"][_COLUMN]] = ""
                                        _row[dataKeys["_SECINFO_STKOPT_STKPRICE"][_COLUMN]] = ""
                                        _row[dataKeys["_SECINFO_STKOPT_EXPRICE"][_COLUMN]] = ""
                                        _row[dataKeys["_SECINFO_STKOPT_EXMONTH"][_COLUMN]] = ""

                                        _row[dataKeys["_SECINFO_TYPE"][_COLUMN]] = unicode(securityAcct.getSecurityType())
                                        _row[dataKeys["_SECINFO_SUBTYPE"][_COLUMN]] = securityAcct.getSecuritySubType()

                                        if securityAcct.getSecurityType() == SecurityType.STOCK:
                                            _row[dataKeys["_SECINFO_STK_DIV"][_COLUMN]] = "" if (securityAcct.getDividend() == 0) else investAcctCurr.format(securityAcct.getDividend(), GlobalVars.decimalCharSep)

                                        if securityAcct.getSecurityType() == SecurityType.MUTUAL: pass

                                        if securityAcct.getSecurityType() == SecurityType.CD:
                                            _row[dataKeys["_SECINFO_CD_APR"][_COLUMN]] = "" if (securityAcct.getAPR() == 0.0) else securityAcct.getAPR()
                                            _row[dataKeys["_SECINFO_CD_COMPOUNDING"][_COLUMN]] = unicode(securityAcct.getCompounding())

                                            numYearsChoice = ["0.5"]
                                            for iYears in range(1, 51): numYearsChoice.append(str(iYears))
                                            _row[dataKeys["_SECINFO_CD_YEARS"][_COLUMN]] = numYearsChoice[-1] if (len(numYearsChoice) < securityAcct.getNumYears()) else numYearsChoice[securityAcct.getNumYears()]

                                        if securityAcct.getSecurityType() == SecurityType.BOND:
                                            bondTypes = [MD_REF.getUI().getStr("gov_bond"), MD_REF.getUI().getStr("mun_bond"), MD_REF.getUI().getStr("corp_bond"), MD_REF.getUI().getStr("zero_bond")]

                                            _row[dataKeys["_SECINFO_BOND_TYPE"][_COLUMN]] = "ERROR" if (securityAcct.getBondType() > len(bondTypes)) else bondTypes[securityAcct.getBondType()]
                                            _row[dataKeys["_SECINFO_BOND_FACEVALUE"][_COLUMN]] = "" if (securityAcct.getFaceValue() == 0) else investAcctCurr.format(securityAcct.getFaceValue(), GlobalVars.decimalCharSep)
                                            _row[dataKeys["_SECINFO_BOND_APR"][_COLUMN]] = "" if (securityAcct.getAPR() == 0.0) else securityAcct.getAPR()

                                            if (securityAcct.getMaturity() != 0 and securityAcct.getMaturity() != 39600000):
                                                _row[dataKeys["_SECINFO_BOND_MATURITYDATE"][_COLUMN]] = DateUtil.convertLongDateToInt(securityAcct.getMaturity())

                                        if securityAcct.getSecurityType() == SecurityType.OPTION:
                                            _row[dataKeys["_SECINFO_STKOPT_CALLPUT"][_COLUMN]] = "Put" if securityAcct.getPut() else "Call"
                                            _row[dataKeys["_SECINFO_STKOPT_STKPRICE"][_COLUMN]] = "" if (securityAcct.getOptionPrice() == 0.0) else securityAcct.getOptionPrice()
                                            _row[dataKeys["_SECINFO_STKOPT_EXPRICE"][_COLUMN]] = "" if (securityAcct.getStrikePrice()) == 0 else investAcctCurr.format(securityAcct.getStrikePrice(), GlobalVars.decimalCharSep)

                                            monthOptions = [MD_REF.getUI().getStr("january"), MD_REF.getUI().getStr("february"), MD_REF.getUI().getStr("march"), MD_REF.getUI().getStr("april"), MD_REF.getUI().getStr("may"), MD_REF.getUI().getStr("june"), MD_REF.getUI().getStr("july"), MD_REF.getUI().getStr("august"), MD_REF.getUI().getStr("september"), MD_REF.getUI().getStr("october"), MD_REF.getUI().getStr("november"), MD_REF.getUI().getStr("december")]
                                            _row[dataKeys["_SECINFO_STKOPT_EXMONTH"][_COLUMN]] = "ERROR" if (securityAcct.getMonth() > len(monthOptions)) else monthOptions[securityAcct.getMonth()]

                                        if securityAcct.getSecurityType() == SecurityType.OTHER: pass

                                        myPrint("D", _THIS_EXTRACT_NAME, _row)
                                        GlobalVars.transactionTable.append(_row)

                                    # noinspection PyUnresolvedReferences
                                    unusedSecurityMasters = [secCurr for secCurr in MD_REF.getCurrentAccountBook().getCurrencies().getAllCurrencies()
                                                             if (secCurr.getCurrencyType() is CurrencyType.Type.SECURITY and secCurr not in usedSecurityMasters)]

                                    if len(unusedSecurityMasters) > 0:
                                        myPrint("B", _THIS_EXTRACT_NAME + "Adding %s unused security master records...." %(len(unusedSecurityMasters)))
                                        for secCurr in unusedSecurityMasters:

                                            _row = ([None] * dataKeys["_END"][0])  # Create a blank row to be populated below...
                                            _row[dataKeys["_KEY"][_COLUMN]] = ""
                                            _row[dataKeys["_ACCOUNT"][_COLUMN]] = "__SecurityMaster__"
                                            _row[dataKeys["_BASECURR"][_COLUMN]] = GlobalVars.baseCurrency.getIDString()

                                            _row[dataKeys["_SECURITY"][_COLUMN]] = unicode(secCurr.getName())
                                            _row[dataKeys["_SECURITYID"][_COLUMN]] = unicode(secCurr.getIDString())
                                            _row[dataKeys["_SECRELCURR"][_COLUMN]] = unicode(secCurr.getRelativeCurrency().getIDString())
                                            _row[dataKeys["_SECMSTRUUID"][_COLUMN]] = secCurr.getUUID()
                                            _row[dataKeys["_TICKER"][_COLUMN]] = unicode(secCurr.getTickerSymbol())
                                            _row[dataKeys["_SECSHRHOLDING"][_COLUMN]] = 0.0
                                            _row[dataKeys["_CURRENTPRICE"][_COLUMN]] = (1.0 / secCurr.getRelativeRate())
                                            _row[dataKeys["_CURRENTPRICETOBASE"][_COLUMN]] = (1.0 / secCurr.getBaseRate())          # same as .getRate(None)

                                            myPrint("D", _THIS_EXTRACT_NAME, _row)
                                            GlobalVars.transactionTable.append(_row)

                                    myPrint("B", _THIS_EXTRACT_NAME + "Security Balance(s) Records selected:", len(GlobalVars.transactionTable))
                                    ###########################################################################################################

                                    GlobalVars.transactionTable = sorted(GlobalVars.transactionTable, key=lambda x: (x[dataKeys["_SECURITY"][_COLUMN]].lower(),
                                                                                               x[dataKeys["_ACCOUNT"][_COLUMN]].lower()))

                                    ###########################################################################################################


                                    def ExtractDataToFile():
                                        global csvDelimiter
                                        global userdateformat
                                        global lWriteBOMToExportFile_SWSS

                                        myPrint("D", _THIS_EXTRACT_NAME + "In ", inspect.currentframe().f_code.co_name, "()")

                                        headings = []
                                        sortDataFields = sorted(dataKeys.items(), key=lambda x: x[1][_COLUMN])
                                        for i in sortDataFields:
                                            headings.append(i[1][_HEADING])
                                        print

                                        myPrint("DB", _THIS_EXTRACT_NAME + "Now pre-processing the file to convert integer dates and strip non-ASCII if requested....")
                                        for _theRow in GlobalVars.transactionTable:

                                            mDate = _theRow[dataKeys["_SECINFO_BOND_MATURITYDATE"][_COLUMN]]
                                            if mDate is not None and mDate != "":
                                                dateasdate = datetime.datetime.strptime(str(mDate), "%Y%m%d")                       # Convert to Date field
                                                _dateoutput = dateasdate.strftime(userdateformat)
                                                _theRow[dataKeys["_SECINFO_BOND_MATURITYDATE"][_COLUMN]] = _dateoutput

                                            for col in range(0, dataKeys["_SECINFO_STK_DIV"][_COLUMN]):
                                                _theRow[col] = fixFormatsStr(_theRow[col])

                                        myPrint("B", _THIS_EXTRACT_NAME + "Opening file and writing %s records" %(len(GlobalVars.transactionTable)))

                                        try:
                                            # CSV Writer will take care of special characters / delimiters within fields by wrapping in quotes that Excel will decode
                                            with open(GlobalVars.csvfilename, "wb") as csvfile:  # PY2.7 has no newline parameter so opening in binary; juse "w" and newline='' in PY3.0

                                                if lWriteBOMToExportFile_SWSS:
                                                    csvfile.write(codecs.BOM_UTF8)   # This 'helps' Excel open file with double-click as UTF-8

                                                writer = csv.writer(csvfile, dialect='excel', quoting=csv.QUOTE_MINIMAL, delimiter=fix_delimiter(csvDelimiter))

                                                if csvDelimiter != ",":
                                                    writer.writerow(["sep=", ""])  # Tells Excel to open file with the alternative delimiter (it will add the delimiter to this line)

                                                writer.writerow(headings[:dataKeys["_KEY"][_COLUMN]])  # Print the header, but not the extra _field headings

                                                try:
                                                    for i in range(0, len(GlobalVars.transactionTable)):
                                                        writer.writerow(GlobalVars.transactionTable[i][:dataKeys["_KEY"][_COLUMN]])
                                                except:
                                                    _msgTxt = _THIS_EXTRACT_NAME + "@@ ERROR writing to CSV on row %s. Please review console" %(i)
                                                    GlobalVars.AUTO_MESSAGES.append(_msgTxt)
                                                    myPrint("B", _msgTxt)
                                                    myPrint("B", _THIS_EXTRACT_NAME, GlobalVars.transactionTable[i])
                                                    raise

                                                if lWriteParametersToExportFile_SWSS:
                                                    today = Calendar.getInstance()
                                                    writer.writerow([""])
                                                    writer.writerow(["StuWareSoftSystems - " + GlobalVars.thisScriptName + "(build: "
                                                                     + version_build
                                                                     + ")  Moneydance Python Script - Date of Extract: "
                                                                     + str(GlobalVars.sdf.format(today.getTime()))])

                                                    writer.writerow([""])
                                                    writer.writerow(["Dataset path/name: %s" %(MD_REF.getCurrentAccountBook().getRootFolder()) ])

                                                    writer.writerow([""])
                                                    writer.writerow(["User Parameters..."])

                                                    writer.writerow(["Hiding Hidden Securities...: %s" %(hideHiddenSecurities)])
                                                    writer.writerow(["Hiding Inactive Accounts...: %s" %(hideInactiveAccounts)])
                                                    writer.writerow(["Hiding Hidden Accounts.....: %s" %(hideHiddenAccounts)])
                                                    writer.writerow(["Security filter............: %s '%s'" %(lAllSecurity,filterForSecurity)])
                                                    writer.writerow(["Account filter.............: %s '%s'" %(lAllAccounts,filterForAccounts)])
                                                    writer.writerow(["Currency filter............: %s '%s'" %(lAllCurrency,filterForCurrency)])

                                            _msgTxt = _THIS_EXTRACT_NAME + "CSV file: '%s' created (%s records)" %(GlobalVars.csvfilename, len(GlobalVars.transactionTable))
                                            myPrint("B", _msgTxt)
                                            GlobalVars.AUTO_MESSAGES.append(_msgTxt)
                                            GlobalVars.countFilesCreated += 1

                                        except:
                                            e_type, exc_value, exc_traceback = sys.exc_info()                           # noqa
                                            _msgTxt = _THIS_EXTRACT_NAME + "@@ ERROR '%s' detected writing file: '%s' - Extract ABORTED!" %(exc_value, GlobalVars.csvfilename)
                                            GlobalVars.AUTO_MESSAGES.append(_msgTxt)
                                            myPrint("B", _msgTxt)
                                            raise

                                    def fixFormatsStr(theString, lNumber=False, sFormat=""):
                                        if isinstance(theString, bool): return theString
                                        if isinstance(theString, tuple): return theString
                                        if isinstance(theString, dict): return theString
                                        if isinstance(theString, list): return theString

                                        if isinstance(theString, int) or isinstance(theString, float) or isinstance(theString, long):
                                            lNumber = True

                                        if lNumber is None: lNumber = False
                                        if theString is None: theString = ""

                                        if sFormat == "%" and theString != "":
                                            theString = "{:.1%}".format(theString)
                                            return theString

                                        if lNumber: return str(theString)

                                        theString = theString.strip()  # remove leading and trailing spaces

                                        theString = theString.replace("\n", "*")  # remove newlines within fields to keep csv format happy
                                        theString = theString.replace("\t", "*")  # remove tabs within fields to keep csv format happy
                                        # theString = theString.replace(";", "*")  # remove tabs within fields to keep csv format happy
                                        # theString = theString.replace(",", "*")  # remove tabs within fields to keep csv format happy
                                        # theString = theString.replace("|", "*")  # remove tabs within fields to keep csv format happy

                                        if lStripASCII:
                                            all_ASCII = ''.join(char for char in theString if ord(char) < 128)  # Eliminate non ASCII printable Chars too....
                                        else:
                                            all_ASCII = theString
                                        return all_ASCII

                                    if len(GlobalVars.transactionTable) > 0:

                                        ExtractDataToFile()

                                        if not GlobalVars.lGlobalErrorDetected:
                                            sTxt = "Extract file CREATED:"
                                            mTxt = "With %s rows\n" % (len(GlobalVars.transactionTable))
                                            myPrint("B", _THIS_EXTRACT_NAME + "%s\n%s" %(sTxt, mTxt))
                                        else:
                                            _msgTextx = _THIS_EXTRACT_NAME + "ERROR Creating extract (review console for error messages)...."
                                            GlobalVars.AUTO_MESSAGES.append(_msgTextx)
                                    else:
                                        _msgTextx = _THIS_EXTRACT_NAME + "@@ No records selected and no extract file created @@"
                                        GlobalVars.AUTO_MESSAGES.append(_msgTextx)
                                        myPrint("B", _msgTextx)
                                        if not GlobalVars.AUTO_EXTRACT_MODE:
                                            DoExtractsSwingWorker.killPleaseWait()
                                            genericSwingEDTRunner(True, True, myPopupInformationBox, extract_data_frame_, _msgTextx, GlobalVars.thisScriptName, JOptionPane.WARNING_MESSAGE)

                                    # delete references to large objects
                                    GlobalVars.transactionTable = None

                                try:
                                    do_extract_security_balances()
                                except:
                                    GlobalVars.lGlobalErrorDetected = True

                                if GlobalVars.lGlobalErrorDetected:
                                    GlobalVars.countErrorsDuringExtract += 1
                                    _txt = _THIS_EXTRACT_NAME + "@@ ERROR: do_extract_security_balances() has failed (review console)!"
                                    GlobalVars.AUTO_MESSAGES.append(_txt)
                                    myPrint("B", _txt)
                                    dump_sys_error_to_md_console_and_errorlog()
                                    if not GlobalVars.AUTO_EXTRACT_MODE:
                                        DoExtractsSwingWorker.killPleaseWait()
                                        genericSwingEDTRunner(True, True, myPopupInformationBox, extract_data_frame_, _txt, "ERROR", JOptionPane.ERROR_MESSAGE)
                                        return False
                            #### ENDIF lExtractSecurityBalances ####

                            if lExtractTrunk:
                                # ####################################################
                                # EXTRACT_TRUNK_FILE EXECUTION
                                # ####################################################

                                _THIS_EXTRACT_NAME = pad("EXTRACT: Trunk file:", 34)
                                GlobalVars.lGlobalErrorDetected = False

                                if not GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE:
                                    self.super__publish([_THIS_EXTRACT_NAME.strip()])                                   # noqa

                                if GlobalVars.AUTO_EXTRACT_MODE:
                                    GlobalVars.csvfilename = os.path.join(GlobalVars.scriptpath, MD_REF.getCurrentAccountBook().getName() + "_" + GlobalVars.defaultFileName_ETRUNK + "")

                                def do_extract_trunk():

                                    def ExtractDataToFile():
                                        myPrint("D", _THIS_EXTRACT_NAME + "In ", inspect.currentframe().f_code.co_name, "()")

                                        try:
                                            localStorage = MD_REF.getCurrentAccountBook().getLocalStorage()
                                            trunkName = "tiksync/trunk"     # Syncer.TRUNK_FILE_NAME
                                            if not localStorage.exists(trunkName):
                                                raise Exception(_THIS_EXTRACT_NAME + "@@ ERROR - could not locate Trunk: '%s'" %(trunkName))

                                            myPrint("B", "Located Trunk file at:", trunkName)
                                            myPrint("B", "Saving txns, saving Trunk file...")
                                            MD_REF.saveCurrentAccount()
                                            MD_REF.getCurrentAccountBook().saveTrunkFile()

                                            fout = FileOutputStream(File(GlobalVars.csvfilename))
                                            localStorage.readFile(trunkName, fout)
                                            fout.close()


                                            _msgTxt = _THIS_EXTRACT_NAME + "Trunk file decrypted and extracted to disk: '%s'" %(GlobalVars.csvfilename)
                                            myPrint("B", _msgTxt)
                                            GlobalVars.AUTO_MESSAGES.append(_msgTxt)
                                            GlobalVars.countFilesCreated += 1

                                        except:
                                            e_type, exc_value, exc_traceback = sys.exc_info()                           # noqa
                                            _msgTxt = _THIS_EXTRACT_NAME + "@@ ERROR '%s' detected writing file: '%s' - Extract ABORTED!" %(exc_value, GlobalVars.csvfilename)
                                            GlobalVars.AUTO_MESSAGES.append(_msgTxt)
                                            myPrint("B", _msgTxt)
                                            raise

                                    ExtractDataToFile()

                                    if not GlobalVars.lGlobalErrorDetected:
                                        sTxt = "Extract file CREATED:"
                                        mTxt = "Raw Trunk file has been decrypted and extracted"
                                        myPrint("B", _THIS_EXTRACT_NAME + "%s\n%s" %(sTxt, mTxt))
                                    else:
                                        _msgTextx = _THIS_EXTRACT_NAME + "ERROR Creating extract (review console for error messages)...."
                                        GlobalVars.AUTO_MESSAGES.append(_msgTextx)

                                try:
                                    do_extract_trunk()
                                except:
                                    GlobalVars.lGlobalErrorDetected = True

                                if GlobalVars.lGlobalErrorDetected:
                                    GlobalVars.countErrorsDuringExtract += 1
                                    _txt = _THIS_EXTRACT_NAME + "@@ ERROR: do_extract_trunk() has failed (review console)!"
                                    GlobalVars.AUTO_MESSAGES.append(_txt)
                                    myPrint("B", _txt)
                                    dump_sys_error_to_md_console_and_errorlog()
                                    if not GlobalVars.AUTO_EXTRACT_MODE:
                                        DoExtractsSwingWorker.killPleaseWait()
                                        genericSwingEDTRunner(True, True, myPopupInformationBox, extract_data_frame_, _txt, "ERROR", JOptionPane.ERROR_MESSAGE)
                                        return False
                            #### ENDIF lExtractTrunk ####

                            if lExtractJSON:
                                # ####################################################
                                # EXTRACT_JSON_FILE EXECUTION
                                # ####################################################

                                _THIS_EXTRACT_NAME = pad("EXTRACT: JSON file:", 34)
                                GlobalVars.lGlobalErrorDetected = False

                                if not GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE:
                                    self.super__publish([_THIS_EXTRACT_NAME.strip()])                                   # noqa

                                if GlobalVars.AUTO_EXTRACT_MODE:
                                    GlobalVars.csvfilename = os.path.join(GlobalVars.scriptpath, MD_REF.getCurrentAccountBook().getName() + "_" + GlobalVars.defaultFileName_JSON + ".json")

                                def do_extract_json():

                                    def ExtractDataToFile():
                                        myPrint("D", _THIS_EXTRACT_NAME + "In ", inspect.currentframe().f_code.co_name, "()")

                                        try:
                                            myPrint("B", "Saving txns, flushing sync to disk...")
                                            MD_REF.saveCurrentAccount()

                                            myPrint("B", "Starting JSON extract..... to file: '%s'" %(GlobalVars.csvfilename))
                                            exportWindow = ExportWindow(None, MD_REF.getCurrentAccounts(), MD_REF.getUI())
                                            invokeMethodByReflection(exportWindow, "exportToJSON", [File], [File(GlobalVars.csvfilename)])
                                            myPrint("B", "... JSON extract COMPLETED.....")
                                            del exportWindow

                                            _msgTxt = _THIS_EXTRACT_NAME + "JSON file decrypted and extracted to disk: '%s'" %(GlobalVars.csvfilename)
                                            myPrint("B", _msgTxt)
                                            GlobalVars.AUTO_MESSAGES.append(_msgTxt)
                                            GlobalVars.countFilesCreated += 1

                                        except:
                                            e_type, exc_value, exc_traceback = sys.exc_info()                           # noqa
                                            _msgTxt = _THIS_EXTRACT_NAME + "@@ ERROR '%s' detected writing file: '%s' - Extract ABORTED!" %(exc_value, GlobalVars.csvfilename)
                                            GlobalVars.AUTO_MESSAGES.append(_msgTxt)
                                            myPrint("B", _msgTxt)
                                            raise

                                    ExtractDataToFile()

                                    if not GlobalVars.lGlobalErrorDetected:
                                        sTxt = "Extract file CREATED:"
                                        mTxt = "Raw JSON file has been decrypted and extracted"
                                        myPrint("B", _THIS_EXTRACT_NAME + "%s\n%s" %(sTxt, mTxt))
                                    else:
                                        _msgTextx = _THIS_EXTRACT_NAME + "ERROR Creating extract (review console for error messages)...."
                                        GlobalVars.AUTO_MESSAGES.append(_msgTextx)

                                try:
                                    do_extract_json()
                                except:
                                    GlobalVars.lGlobalErrorDetected = True

                                if GlobalVars.lGlobalErrorDetected:
                                    GlobalVars.countErrorsDuringExtract += 1
                                    _txt = _THIS_EXTRACT_NAME + "@@ ERROR: do_extract_json() has failed (review console)!"
                                    GlobalVars.AUTO_MESSAGES.append(_txt)
                                    myPrint("B", _txt)
                                    dump_sys_error_to_md_console_and_errorlog()
                                    if not GlobalVars.AUTO_EXTRACT_MODE:
                                        DoExtractsSwingWorker.killPleaseWait()
                                        genericSwingEDTRunner(True, True, myPopupInformationBox, extract_data_frame_, _txt, "ERROR", JOptionPane.ERROR_MESSAGE)
                                        return False
                            #### ENDIF lExtractJSON ####

                            if lExtractAttachments:
                                # ####################################################
                                # EXTRACT_ATTACHMENTS EXECUTION
                                # ####################################################

                                _THIS_EXTRACT_NAME = pad("EXTRACT: Attachments:", 34)
                                GlobalVars.lGlobalErrorDetected = False

                                if not GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE:
                                    self.super__publish([_THIS_EXTRACT_NAME.strip()])                                   # noqa

                                if GlobalVars.AUTO_EXTRACT_MODE:
                                    _name_addition = "" + "_" + UUID.randomUUID().toString() + currentDateTimeMarker()
                                    GlobalVars.extractFolderName = os.path.join(GlobalVars.scriptpath, MD_REF.getCurrentAccountBook().getName() + "_" + GlobalVars.defaultFileName_EATTACH + _name_addition)
                                    GlobalVars.csvfilename = GlobalVars.extractFolderName   # Just populate with something

                                def do_extract_attachments():

                                    def ExtractDataToFile():
                                        myPrint("D", _THIS_EXTRACT_NAME + "In ", inspect.currentframe().f_code.co_name, "()")

                                        try:
                                            iSkip = 0
                                            iCountAttachments = 0
                                            attachmentsLog = "\n%s:\n" \
                                                      " ===================\n\n" %(_THIS_EXTRACT_NAME)

                                            attachmentsLog += "Base extract folder: %s%s\n\n" %(GlobalVars.extractFolderName, os.path.sep)
                                            attachmentsExtractedTxt = []

                                            File(GlobalVars.extractFolderName).mkdirs()
                                            myPrint("B", _THIS_EXTRACT_NAME + "Extracting all attachments to:", GlobalVars.extractFolderName)

                                            txnSet = MD_REF.getCurrentAccountBook().getTransactionSet()

                                            for txn in txnSet:
                                                for attachKey in txn.getAttachmentKeys():
                                                    iCountAttachments += 1
                                                    attachTag = txn.getAttachmentTag(attachKey)
                                                    txnDate = txn.getDateInt()
                                                    attachFile = File(attachTag).getName()
                                                    attachFolder = os.path.join(GlobalVars.extractFolderName,
                                                                                "ACCT-TYPE-%s" %(txn.getAccount().getAccountType()),
                                                                                "ACCT-%s" %(txn.getAccount().getAccountName()))
                                                    File(attachFolder).mkdirs()
                                                    outputPath = os.path.join(attachFolder, "{:04d}-{:02d}-{:02d}-{}-{}".format(txnDate / 10000, (txnDate / 100) % 100,
                                                                                                                                txnDate % 100, str(iCountAttachments).zfill(5),
                                                                                                                                attachFile))
                                                    if os.path.exists(outputPath):
                                                        iSkip += 1
                                                        myPrint("B", "Error - path: %s already exists... SKIPPING THIS ONE!" %(outputPath))
                                                        attachmentsLog += ("Error - path: %s already exists... SKIPPING THIS ONE!\n" %(outputPath))
                                                    else:
                                                        myPrint("DB", "Exporting attachment [%s]" %(os.path.basename(outputPath)))
                                                        try:
                                                            outStream = FileOutputStream(File(outputPath))
                                                            inStream = convertBufferedSourceToInputStream(MD_REF.getCurrentAccountBook().getLocalStorage().openFileForReading(attachTag))
                                                            MDIOUtils.copyStream(inStream, outStream)
                                                            outStream.close()
                                                            inStream.close()
                                                            attachmentsExtractedTxt.append([txn.getAccount().getAccountType(), txn.getAccount().getAccountName(), txn.getDateInt(),
                                                                                "%s %s %s %s %s .%s\n"
                                                                                %(pad(str(txn.getAccount().getAccountType()), 15),
                                                                                  pad(txn.getAccount().getAccountName(), 30),
                                                                                  convertStrippedIntDateFormattedText(txn.getDateInt()),
                                                                                  rpad(txn.getValue() / 100.0, 10),
                                                                                  pad(txn.getDescription(), 20),
                                                                                  outputPath[len(GlobalVars.extractFolderName):])])
                                                        except:
                                                            _msgTxt = "Error extracting file - will SKIP : %s" %(outputPath)
                                                            myPrint("B", _msgTxt)
                                                            attachmentsLog += ("%s\n" %(_msgTxt))
                                                            iSkip += 1
                                            del txnSet

                                            attachmentsExtractedTxt = sorted(attachmentsExtractedTxt, key=lambda _sort: (_sort[0], _sort[1], _sort[2]))
                                            for r in attachmentsExtractedTxt: attachmentsLog += r[3]

                                            if iSkip: attachmentsLog += "\nERRORS/SKIPPED: %s (review console log for details)\n" %(iSkip)

                                            attachmentsLog += "\n<END>"

                                            try:
                                                log = open(os.path.join(GlobalVars.extractFolderName, "Extract_Attachments_LOG.txt"), "w")
                                                log.write(attachmentsLog)
                                                log.close()
                                            except: pass

                                            _msgTxt = _THIS_EXTRACT_NAME + "%s Attachments extracted to disk (%s skipped)" %(iCountAttachments, iSkip)
                                            myPrint("B", _msgTxt)
                                            GlobalVars.AUTO_MESSAGES.append(_msgTxt)
                                            GlobalVars.countFilesCreated += 1

                                        except:
                                            e_type, exc_value, exc_traceback = sys.exc_info()                           # noqa
                                            _msgTxt = _THIS_EXTRACT_NAME + "@@ ERROR '%s' detected writing attachments: '%s' - Extract ABORTED!" %(exc_value, GlobalVars.csvfilename)
                                            GlobalVars.AUTO_MESSAGES.append(_msgTxt)
                                            myPrint("B", _msgTxt)
                                            raise

                                    ExtractDataToFile()

                                    if not GlobalVars.lGlobalErrorDetected:
                                        sTxt = "Extract of Attachments CREATED:"
                                        mTxt = "Attachments have been decrypted and extracted"
                                        myPrint("B", _THIS_EXTRACT_NAME + "%s\n%s" %(sTxt, mTxt))
                                    else:
                                        _msgTextx = _THIS_EXTRACT_NAME + "ERROR Creating extract (review console for error messages)...."
                                        GlobalVars.AUTO_MESSAGES.append(_msgTextx)

                                try:
                                    do_extract_attachments()
                                except:
                                    GlobalVars.lGlobalErrorDetected = True

                                if GlobalVars.lGlobalErrorDetected:
                                    GlobalVars.countErrorsDuringExtract += 1
                                    _txt = _THIS_EXTRACT_NAME + "@@ ERROR: do_extract_attachments() has failed (review console)!"
                                    GlobalVars.AUTO_MESSAGES.append(_txt)
                                    myPrint("B", _txt)
                                    dump_sys_error_to_md_console_and_errorlog()
                                    if not GlobalVars.AUTO_EXTRACT_MODE:
                                        DoExtractsSwingWorker.killPleaseWait()
                                        genericSwingEDTRunner(True, True, myPopupInformationBox, extract_data_frame_, _txt, "ERROR", JOptionPane.ERROR_MESSAGE)
                                        return False
                            #### ENDIF lExtractAttachments ####


                            GlobalVars.lGlobalErrorDetected = False

                        except:
                            e_type, exc_value, exc_traceback = sys.exc_info()                                           # noqa
                            GlobalVars.lGlobalErrorDetected = True
                            myPrint("B", "@@ ERROR '%s' Detected within DoExtractsSwingWorker()" %(exc_value))
                            dump_sys_error_to_md_console_and_errorlog()
                            return False

                        myPrint("DB", "DoExtractsSwingWorker.doInBackground() completed...")
                        return True

                    # noinspection PyMethodMayBeStatic
                    def done(self):
                        myPrint("DB", "In DoExtractsSwingWorker()", inspect.currentframe().f_code.co_name, "()")
                        myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

                        if not GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE:
                            myPrint("DB", "... calling done:get()")
                            self.get()     # wait for task to complete
                            myPrint("DB", "... after done:get()")

                        DoExtractsSwingWorker.killPleaseWait()

                        # EXTRACT(s) COMPLETED
                        if GlobalVars.EXTRACT_DATA:
                            msgs = []
                            msgs.append(">>>")
                            msgs.append("--------------------------------")
                            msgs.append("EXTRACT DATA: MESSAGES & SUMMARY")
                            msgs.append("")
                            if GlobalVars.AUTO_EXTRACT_MODE:
                                msgs.append("AUTO EXTRACT MODE ENABLED")
                            else:
                                msgs.append("SINGLE DATA FILE EXTRACT MODE ENABLED")
                            msgs.append("")

                            if GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE:
                                msgs.append("EXTRACT TRIGGERED BY FILE CLOSING EVENT")
                                msgs.append("")

                            if GlobalVars.AUTO_INVOKE_CALLED:
                                if GlobalVars.AUTO_INVOKE_THEN_QUIT:
                                    msgs.append("AUTO INVOKE CALLED >> WILL TRIGGER SHUTDOWN...")
                                else:
                                    msgs.append("AUTO INVOKE CALLED >> Moneydance will remain running after extract(s)...")
                                msgs.append("")

                            if lExtractStockGlance2020:     msgs.append("Extract StockGlance2020            REQUESTED")
                            if lExtractReminders:           msgs.append("Extract Reminders                  REQUESTED")
                            if lExtractAccountTxns:         msgs.append("Extract Account Registers          REQUESTED")
                            if lExtractInvestmentTxns:      msgs.append("Extract Investment Transactions    REQUESTED")
                            if lExtractCurrencyHistory:     msgs.append("Extract Currency History           REQUESTED")
                            if lExtractSecurityBalances:    msgs.append("Extract Security Balances          REQUESTED")
                            if lExtractTrunk:               msgs.append("Extract raw Trunk file             REQUESTED")
                            if lExtractJSON:                msgs.append("Extract raw JSON file              REQUESTED")
                            if lExtractAttachments:         msgs.append("Extract Attachments                REQUESTED")
                            if didDisableALL_attachments:   msgs.append("Extract Attachments                *DISABLED*")

                            msgs.append("")
                            msgs.extend(GlobalVars.AUTO_MESSAGES)
                            msgs.append("")

                            msgs.append("Extract csv files / folders created..: %s" %(GlobalVars.countFilesCreated))
                            msgs.append("Extract errors during extract........: %s" %(GlobalVars.countErrorsDuringExtract))

                            if GlobalVars.lGlobalErrorDetected or GlobalVars.countErrorsDuringExtract > 0:
                                msgs.append("")
                                msgs.append("*** EXTRACT FAILED WITH ERROR >> REVIEW CONSOLE FOR DETAILS ***")
                                msgs.append("")

                            msgs.append("--------------------------------")
                            msgs.append("")

                            endMsg = "\n".join(msgs)
                            myPrint("B", endMsg)

                            if not GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE:
                                MyPopUpDialogBox(None, theStatus="EXTRACT PROCESS COMPLETED >> review status below:)", theMessage=endMsg, theTitle="EXTRACT_DATA: AUTO_MODE", lModal=False).go()

                                if not GlobalVars.AUTO_EXTRACT_MODE and GlobalVars.countFilesCreated > 0:
                                    try:
                                        helper = MD_REF.getPlatformHelper()
                                        helper.openDirectory(File(GlobalVars.csvfilename))
                                    except: pass

                            cleanup_actions(extract_data_frame_)

                        if GlobalVars.AUTO_INVOKE_CALLED:
                            if GlobalVars.AUTO_INVOKE_THEN_QUIT:
                                myPrint("B", "@@ COMPLETED - Triggering shutdown @@")
                                MD_REF.saveCurrentAccount()
                                genericThreadRunner(True, MD_REF.getUI().shutdownApp, False)
                            else:
                                myPrint("B", "@@ COMPLETED (Moneydance will remain running) @@")

                _msgPad = 100
                _msg = pad("PLEASE WAIT: Extracting Data", _msgPad, padChar=".")
                if GlobalVars.DISPLAY_DATA or GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE:
                    pleaseWait = None
                else:
                    pleaseWait = MyPopUpDialogBox(extract_data_frame_, theStatus=_msg, theTitle=_msg, lModal=False, OKButtonText="WAIT")
                    pleaseWait.go()

                if GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE:
                    # Run / block calling MD thread...
                    sw = DoExtractsSwingWorker(pleaseWait)
                    sw.doInBackground()
                    sw.done()
                else:
                    sw = DoExtractsSwingWorker(pleaseWait)
                    sw.execute()

            except QuickAbortThisScriptException:
                myPrint("DB", "Caught Exception: QuickAbortThisScriptException... Doing nothing (assume exit requested)...")

            except:
                crash_txt = "ERROR - Extract_Data has crashed. Please review MD Menu>Help>Console Window for details".upper()
                myPrint("B", crash_txt)
                crash_output = dump_sys_error_to_md_console_and_errorlog(True)
                if not GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE:
                    jif = QuickJFrame("ERROR - Extract_Data:", crash_output).show_the_frame()
                    MyPopUpDialogBox(jif, theStatus="ERROR: Extract_Data has crashed", theMessage=crash_txt, theTitle="ERROR", lAlertLevel=2, lModal=False).go()
                raise


    if GlobalVars.HANDLE_EVENT_AUTO_EXTRACT_ON_CLOSE:
        # Keep / block the same calling Moneydance event thread....
        myPrint("DB", "Executing code on the same Moneydance handle_event thread to block Moneydance whilst auto extract runs....")
        MainAppRunnable().run()
    else:
        SwingUtilities.invokeLater(MainAppRunnable())

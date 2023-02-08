#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# net_account_balances.py build: 1020 - Jan 2023 - Stuart Beesley - StuWareSoftSystems
# Display Name in MD changed to 'Custom Balances' (was 'Net Account Balances') >> 'id' remains: 'net_account_balances'

# Thanks and credit to Dan T Davis and Derek Kent(23) for their suggestions and extensive testing...
# further thanks to Kevin(N) and dwg for their testing and input too...
########################################################################################################################
# This extension creates a 'widget' that displays Totals for items you select on the Moneydance Summary Page (Home Page)
#
# Double-click .mxt, or Drag & drop .mxt onto left side bar, or Extensions, Manage Extensions, add from file to install.
# Once installed, visit Preferences > Summary Page, and then move the new widget to the desired Summary Page location
#
# This widget allows you to select multiple accounts / categories / Securities and filter Active/Inactive items
# The balances are totalled and displayed on the Summary Page widget, converted to the Currency you select to display
#
# Review net_account_balances_readme.txt for more details
#
# As of Dec 2021:   this extension allows you to select how many rows you require and configure each row
#                   ... select a currency conversion per row, include/exclude Active/Inactive accounts
#                   ... auto sum whole accounts (or when off, manually select sub accounts / securities)
#                   ... QuickSearch Filters too.
#
#                   On Income/Expense categories you can select a date range, and widget will recalculate balances
#                   ... and allows custom date ranges too
#                   WARNING: This is potentially an 'expensive' operation. Do not use for heavy reporting...
########################################################################################################################
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

# Built to operate on Moneydance 2021.1 build 3056 onwards (as this is when the Py Extensions became fully functional)

# Build: 1 - Initial release
# Build: 2 - Screensize tweaks; ability to set widget display name; alter startup behaviour
# Build: 2 - Renamed to net_account_balances (removed _to_zero); common code/startup
# Build: 3 - properly convert fx accounts back to base currency; allow all account types in selection..
# Build: 4 - Tweak to security currency conversion to base...
# Build: 5 - Enhance JList colors and handling of clicks (so as not to unselect all on new click); add clear selection button
# Build: 1000 - Formal release
# Build: 1001 - Enhancements to incorporate VAqua on Mac; Fix JMenuBar() appearing in wrong place after File/Open(switch datasets)
# Build: 1001 - Change startup common code to detect 'wrong' startup conditions. Make build 3056 the minimum for my extensions (as they leverage .unload() etc)
# Build: 1001 - Fix condition when -invoke[_and_quit] was used to prevent refresh erroring when MD actually closing...
# Build: 1002 - Build 3067 of MD renamed com.moneydance.apps.md.view.gui.theme.Theme to com.moneydance.apps.md.view.gui.theme.ThemeInfo
# Build: 1003 - Small tweaks to conform to IK design standards
# Build: 1004 - Fixed pickle.dump/load common code to work properly cross-platform (e.g. Windows to Mac) by (stripping \r when needed)
# Build: 1004 - Common code tweaks
# Build: 1005 - Common code tweaks; Tweaked colors for Dark themes and to be more MD 'compatible'
# Build: 1006 - Common code tweaks; Flat Dark Theme
# Build: 1007 - Common code tweaks
# Build: 1008 - Common code tweaks; Multi-row, currency conversion options(s)
# Build: 1009 - Accounts/Categories/Securities Selection Option(s) - PREVIEW BUILD
# Build: 1010 - Further enhancements from preview release. Added Filters for Active/Inactive. AutoSum Investment Accts Option
# Build: 1010 - QuickSearch filter; added balances to list window; replaced callingClass with reference to single instance name
# Build: 1010 - Tweaks to ensure [list of] double-byte characters don't crash debug messages...
# Build: 1011 - Enhance Income/Expense totalling by date range. Multi threaded with SwingWorker. New filters.
# Build: 1011 - Renamed display name to 'Custom Balances'
# Build: 1012 - Added <PREVIEW> tag to GUI title bar if preview detected...; Tweak to catching MD closing 'book' trap
# Build: 1013 - Added <html> tags to JMenu() titles to stop becoming invisible when mouse hovers
# Build: 1013 - Added Security currencies into currency display table... Allows shares to be used etc...
# Build: 1013 - Fixes for 4069 Alpha onwards.. Calls to getUI() off the EDT are now (properly) blocked by MD.....
# Build: 1013 - Fix when setting lastRefreshTriggerWasAccountModified and HPV.view is None (closing the GUI would error)
# build: 1013 - Eliminated common code globals :->; tweak to setDefaultFonts() - catch when returned font is None (build 4071)
# build: 1013 - Moved .decodeCommand() to common code
# build: 1014 - Tweak; Common code
# build: 1014 - FileDialog() (refer: java.desktop/sun/lwawt/macosx/CFileDialog.java) seems to no longer use "com.apple.macos.use-file-dialog-packages" in favor of "apple.awt.use-file-dialog-packages" since Monterrey...
# build: 1014 - Common code update - remove Decimal Grouping Character - not necessary to collect and crashes on newer Java versions (> byte)
# build: 1014 - Bug fix... When old format parameters were loaded, then switch to newer format parameters, migratedParameters flag was sticking as True, and hence loading wrong autoSum defaults...
# build: 1014 - Small fix for possible MD GUI hang on startup (EDT thing....)
# build: 1014 - Added icon to allow user to collapse widget.....; Added row separator functionality...
# build: 1015 - Added support for Indian numbering system...: refer: https://en.wikipedia.org/wiki/Indian_numbering_system
# build: 1015 - Added new options to allow auto hiding of rows when balance is xxx...
# build: 1016 - Fix phantom linking of account selection when using duplicate row function...
# build: 1017 - Enable blinking of auto hidden rows....; Added option to hide decimals...; use my code for all .formatXXX() calls...
# build: 1017 - Added underline 'dots' to match the other Summary Screen visual laf... Also option to enable / disable...
# build: 1017 - Reengineered the row popup selector to fix background issues...
# build: 1017 - Added option for autohide row when value is not x (rather than zero); change blink to per row...
# build: 1018 - Change blink to per row... Added rounding(towards X) when auto-hiding rows with hide decimals enabled...
# build: 1018 - Added Avg / by: value - when set, you can produce an average using custom divisor...
# build: 1019 - Tweaks / fixes to auto-hide when average; location of average maths; fixed switchFromHomeScreen bug-ette;
# build: 1019 - roundTowards() when hiding decimals; tweak common code
# build: 1020 - Bold'ified [sic] blinking cells...
# build: 1020 - MAJOR 'upgrade' to (re)code to cope with multiple home screens (that caused 'disappearing' widgets)
#               There is a design fault when opening a new MD HomeScreen (so you have multiple running) whereby
#               the custom_balances widget would disappear from the previous home screen.. This was because MD's 'internal' home
#               screen widgets are NEW instances per home screen. I.e. Each RootAccountDetailPanel (instance) creates new
#               ViewFactory() instance(s) which calls .reloadViews() which creates/adds NEW instances of all 'internal' views,
#               but for extensions it ONLY adds a reference to the same/original 'external' view(s).
#               I.e. extension's external view(s) are single instance, whereas internal views are multi instances...
#               Swing objects cannot exist in two places, hence the last place wins and previous locations disappear...
#               NOTE: This issue affects all extension / external views...
#               This code-fix deals with this issue by generating a new panel on every call of .getGUIView() and maintains
#               internal knowledge of its views with special code to detect whether they are still alive/valid.
#               When the view(s) are refreshed the code iterates all known views and simply builds a new view from the same data.
# build: 1020 - Changed refresh time delay to 3 seconds (was 10 seconds)....
# build: 1020 - Added capability for other extensions to request the last set of results using invoke "net_account_balances:customevent:returnLastResults"
# build: 1020 - Added bootstrap to execute compiled version of extension (faster to load)....

# todo add 'as of' balance date option (for non inc/exp rows) - perhaps??

# CUSTOMIZE AND COPY THIS ##############################################################################################
# CUSTOMIZE AND COPY THIS ##############################################################################################
# CUSTOMIZE AND COPY THIS ##############################################################################################

# SET THESE LINES
myModuleID = u"net_account_balances"
version_build = "1020"
MIN_BUILD_REQD = 3056  # 2021.1 Build 3056 is when Python extensions became fully functional (with .unload() method for example)
_I_CAN_RUN_AS_MONEYBOT_SCRIPT = False

if u"debug" in globals():
    global debug
else:
    debug = False
global net_account_balances_frame_
# SET LINES ABOVE ^^^^

# COPY >> START
import __builtin__ as builtins

def checkObjectInNameSpace(objectName):
    """Checks globals() and builtins for the existence of the object name (used for StuWareSoftSystems' bootstrap)"""
    if objectName is None or not isinstance(objectName, basestring) or objectName == u"": return False
    if objectName in globals(): return True
    return objectName in dir(builtins)


global moneydance, moneydance_ui, moneydance_extension_loader, moneydance_extension_parameter
MD_REF = moneydance             # Make my own copy of reference as MD removes it once main thread ends.. Don't use/hold on to _data variable
MD_REF_UI = moneydance_ui       # Necessary as calls to .getUI() will try to load UI if None - we don't want this....
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
        self.myJFrameVersion = 3
        self.isActiveInMoneydance = False
        self.isRunTimeExtension = False
        self.MoneydanceAppListener = None
        self.HomePageViewObj = None

    def dispose(self):
        # This removes all content as VAqua retains the JFrame reference in memory...
        if self.disposing: return
        try:
            self.disposing = True
            self.removeAll()
            if self.getJMenuBar() is not None: self.setJMenuBar(None)
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
            and (isinstance(net_account_balances_frame_, MyJFrame)                 # EDIT THIS
                 or type(net_account_balances_frame_).__name__ == u"MyCOAWindow")  # EDIT THIS
            and net_account_balances_frame_.isActiveInMoneydance):                 # EDIT THIS
        frameToResurrect = net_account_balances_frame_                             # EDIT THIS
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

    # NOTE: As of MD2022(4040) python.getSystemState().setdefaultencoding("utf8") is called on the python interpreter at launch...
    import sys
    reload(sys)  # Dirty hack to eliminate UTF-8 coding errors
    sys.setdefaultencoding('utf8')  # Dirty hack to eliminate UTF-8 coding errors. Without this str() fails on unicode strings...

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

    from com.moneydance.apps.md.controller import AccountBookWrapper
    from com.infinitekind.moneydance.model import AccountBook

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
    from java.util import Date, Locale

    from java.text import DecimalFormat, SimpleDateFormat, MessageFormat
    from java.util import Calendar, ArrayList
    from java.lang import Thread, IllegalArgumentException, String, Integer, Long
    from java.lang import Double, Math, Character, NoSuchFieldException, NoSuchMethodException, Boolean
    from java.lang.reflect import Modifier
    from java.io import FileNotFoundException, FilenameFilter, File, FileInputStream, FileOutputStream, IOException, StringReader
    from java.io import BufferedReader, InputStreamReader
    from java.nio.charset import Charset
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
            MD_MDPLUS_BUILD = 4040
            MD_ALERTCONTROLLER_BUILD = 4077
            def __init__(self): pass    # Leave empty

            class Strings:
                def __init__(self): pass    # Leave empty

    GlobalVars.thisScriptName = u"%s.py(Extension)" %(myModuleID)

    # END SET THESE VARIABLES FOR ALL SCRIPTS ##############################################################################

    # >>> THIS SCRIPT'S IMPORTS ############################################################################################
    import copy
    import threading
    from com.moneydance.awt import GridC, JLinkListener, JLinkLabel, AwtUtil, QuickSearchField, JRateField
    # from com.moneydance.awt import CollapsibleRefresher
    from com.moneydance.apps.md.view import HomePageView
    from com.moneydance.apps.md.view.gui import MoneydanceLAF, DateRangeChooser, ConsoleWindow, MainFrame
    from com.moneydance.apps.md.controller import FeatureModule, PreferencesListener
    from com.moneydance.apps.md.controller.time import DateRangeOption
    from com.infinitekind.moneydance.model import AccountListener, AbstractTxn, CurrencyListener, DateRange
    # from com.infinitekind.moneydance.model import TxnIterator
    from com.infinitekind.util import StringUtils, StreamVector

    from javax.swing import JList, ListSelectionModel, DefaultComboBoxModel, DefaultListSelectionModel, JSeparator
    from javax.swing import DefaultListCellRenderer, BorderFactory, Timer as SwingTimer
    from javax.swing.event import DocumentListener, ListSelectionListener
    # from javax.swing.text import View

    from java.awt import RenderingHints, BasicStroke, Graphics2D, Rectangle
    from java.awt.event import FocusAdapter, MouseListener, ActionListener
    from java.awt.geom import Path2D

    from java.lang import ArrayIndexOutOfBoundsException, Integer, InterruptedException, Character
    from java.lang.ref import WeakReference
    from java.util import Comparator, Iterator, Collections, Iterator, UUID
    from java.util.concurrent import CancellationException
    # from java.util import ConcurrentModificationException

    # renamed in MD build 3067
    if int(MD_REF.getBuild()) >= 3067:
        from com.moneydance.apps.md.view.gui.theme import ThemeInfo                                                     # noqa
    else:
        from com.moneydance.apps.md.view.gui.theme import Theme as ThemeInfo                                            # noqa

    # from com.moneydance.apps.md.controller import URLUtil
    # >>> END THIS SCRIPT'S IMPORTS ########################################################################################

    # >>> THIS SCRIPT'S GLOBALS ############################################################################################
    GlobalVars.specialDebug = False

    GlobalVars.Strings.MD_GLYPH_APPICON_64 = "/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"
    GlobalVars.Strings.MD_GLYPH_REFRESH = "/com/moneydance/apps/md/view/gui/glyphs/glyph_refresh.png"
    GlobalVars.Strings.MD_GLYPH_TRIANGLE_RIGHT = "/com/moneydance/apps/md/view/gui/glyphs/glyph_triangle_right.png"
    GlobalVars.Strings.MD_GLYPH_TRIANGLE_DOWN = "/com/moneydance/apps/md/view/gui/glyphs/glyph_triangle_down.png"
    GlobalVars.Strings.MD_GLYPH_REMINDERS = "/com/moneydance/apps/md/view/gui/glyphs/glyph_reminders.png"

    GlobalVars.Strings.UNICODE_CROSS = u"\u2716"
    GlobalVars.Strings.UNICODE_UP_ARROW = u"\u2191"
    GlobalVars.Strings.UNICODE_DOWN_ARROW = u"\u2193"
    GlobalVars.Strings.UNICODE_THIN_SPACE = u"\u2009"

    GlobalVars.Strings.LEGACYID = "Net_account_balances (HomePageView)"  # Switched to a better convention - DO NOT CHANGE THIS EVER!

    GlobalVars.__net_account_balances_extension = None

    GlobalVars.EXTENSION_LOCK = threading.Lock()

    # Old version parameters - will be migrated and deleted (if they exist)
    GlobalVars.extn_param_listAccountUUIDs_NAB              = None
    GlobalVars.extn_param_balanceType_NAB                   = None
    GlobalVars.extn_param_widget_display_name_NAB           = None

    # New multi-row variables
    GlobalVars.extn_param_NEW_listAccountUUIDs_NAB          = None
    GlobalVars.extn_param_NEW_balanceType_NAB               = None
    GlobalVars.extn_param_NEW_widget_display_name_NAB       = None
    GlobalVars.extn_param_NEW_currency_NAB                  = None
    GlobalVars.extn_param_NEW_disableCurrencyFormatting_NAB = None
    GlobalVars.extn_param_NEW_includeInactive_NAB           = None
    GlobalVars.extn_param_NEW_autoSumAccounts_NAB           = None
    GlobalVars.extn_param_NEW_incomeExpenseDateRange_NAB    = None
    GlobalVars.extn_param_NEW_showWarningsTable_NAB         = None
    GlobalVars.extn_param_NEW_customDatesTable_NAB          = None
    GlobalVars.extn_param_NEW_rowSeparatorTable_NAB         = None
    GlobalVars.extn_param_NEW_blinkTable_NAB                = None
    GlobalVars.extn_param_NEW_hideRowWhenXXXTable_NAB       = None
    GlobalVars.extn_param_NEW_hideRowXValueTable_NAB        = None
    GlobalVars.extn_param_NEW_displayAverageTable_NAB       = None

    GlobalVars.extn_param_NEW_disableWidgetTitle_NAB        = None
    GlobalVars.extn_param_NEW_autoSumDefault_NAB            = None
    GlobalVars.extn_param_NEW_showDashesInsteadOfZeros_NAB  = None
    GlobalVars.extn_param_NEW_treatSecZeroBalInactive_NAB   = None

    GlobalVars.extn_param_NEW_useIndianNumberFormat_NAB     = None
    GlobalVars.extn_param_NEW_hideDecimals_NAB              = None
    GlobalVars.extn_param_NEW_displayVisualUnderDots_NAB    = None

    GlobalVars.extn_param_NEW_expandedView_NAB              = None

    GlobalVars.DEFAULT_WIDGET_DISPLAY_NAME          = "Custom Balances"
    GlobalVars.DEFAULT_WIDGET_ROW_NOT_CONFIGURED    = "<NOT CONFIGURED>"
    GlobalVars.WIDGET_ROW_DISABLED                  = "** ROW HIDDEN/DISABLED **"

    GlobalVars.BALTYPE_BALANCE = 0
    GlobalVars.BALTYPE_CURRENTBALANCE = 1
    GlobalVars.BALTYPE_CLEAREDBALANCE = 2

    GlobalVars.DATE_RANGE_VALID = 19000101

    GlobalVars.ROW_SEPARATOR_NEVER      = 0
    GlobalVars.ROW_SEPARATOR_ABOVE      = 1
    GlobalVars.ROW_SEPARATOR_BELOW      = 2
    GlobalVars.ROW_SEPARATOR_BOTH       = 3

    GlobalVars.HIDE_ROW_WHEN_NEVER          = 0
    GlobalVars.HIDE_ROW_WHEN_ALWAYS         = 1
    GlobalVars.HIDE_ROW_WHEN_ZERO_OR_X      = 2     
    GlobalVars.HIDE_ROW_WHEN_NEGATIVE_OR_X  = 3     
    GlobalVars.HIDE_ROW_WHEN_POSITIVE_OR_X  = 4     
    GlobalVars.HIDE_ROW_WHEN_NOT_ZERO_OR_X  = 5     

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
Toolbox:                                View Moneydance settings, diagnostics, fix issues, change settings and much more
                                        + Extension Menus: Total selected transactions & Move Investment Transactions
Custom Balances (net_account_balances): Summary Page (HomePage) widget. Display the total of selected Account Balances

Extension (.mxt) and Script (.py) Versions available:
Extract Data:                           Extract various data to screen and/or csv.. Consolidation of:
- stockglance2020                       View summary of Securities/Stocks on screen, total by Security, export to csv 
- extract_reminders_csv                 View reminders on screen, edit if required, extract all to csv
- extract_currency_history_csv          Extract currency history to csv
- extract_investment_transactions_csv   Extract investment transactions to csv
- extract_account_registers_csv         Extract Account Register(s) to csv along with any attachments

List Future Reminders:                  View future reminders on screen. Allows you to set the days to look forward
Accounts Categories Mega Search Window: Combines MD Menu> Tools>Accounts/Categories and adds Quick Search box/capability
Security Performance Graph:             Graphs selected securities, calculating relative price performance as percentage

A collection of useful ad-hoc scripts (zip file)
useful_scripts:                         Just unzip and select the script you want for the task at hand...

Visit: %s (Author's site)
----------------------------------------------------------------------------------------------------------------------
""" %(GlobalVars.thisScriptName, GlobalVars.MYPYTHON_DOWNLOAD_URL)

    def cleanup_references():
        global MD_REF, MD_REF_UI, MD_EXTENSION_LOADER
        # myPrint("DB","About to delete reference to MD_REF, MD_REF_UI and MD_EXTENSION_LOADER....!")
        # del MD_REF, MD_REF_UI, MD_EXTENSION_LOADER

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
            printString = printString.strip()

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
                    System.err.write(GlobalVars.thisScriptName + ":" + dt + ": "+"Error writing to console")
                    dump_sys_error_to_md_console_and_errorlog()

        except IllegalArgumentException:
            myPrint("B","ERROR - Probably on a multi-byte character..... Will ignore as code should just continue (PLEASE REPORT TO DEVELOPER).....")
            dump_sys_error_to_md_console_and_errorlog()

        return

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
                currentTheme = MD_REF.getUI().getCurrentTheme()
                if ".vaqua" in safeStr(currentTheme.getClass()).lower(): return True
            except: pass
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
            # if Platform.isOSX() and int(float(MD_REF.getBuild())) >= 3039: self.lAlertLevel = 0    # Colors don't work on Mac since VAQua
            if isMDThemeDark() or isMacDarkModeDetected(): self.lAlertLevel = 0

        def updateMessages(self, newTitle=None, newStatus=None, newMessage=None, lPack=True):
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
            return

        def result(self):
            return self.lResult[0]

        def go(self):
            myPrint("DB", "In MyPopUpDialogBox.", inspect.currentframe().f_code.co_name, "()")
            myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

            class MyPopUpDialogBoxRunnable(Runnable):
                def __init__(self, callingClass):
                    self.callingClass = callingClass

                def run(self):                                                                                                      # noqa

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
                        # self.callingClass._popup_d.setPreferredSize(Dimension(maxDialogWidth,maxDialogHeight))
                    else:
                        maxDialogWidth = min(screenSize.width-20, max(GetFirstMainFrame.DEFAULT_MAX_WIDTH, int(round(GetFirstMainFrame.getSize().width *.9,0))))
                        maxDialogHeight = min(screenSize.height-40, max(GetFirstMainFrame.DEFAULT_MAX_WIDTH, int(round(GetFirstMainFrame.getSize().height *.9,0))))
                        maxDimension = Dimension(maxDialogWidth,maxDialogHeight)
                        # self.callingClass._popup_d.setPreferredSize(Dimension(maxDialogWidth,maxDialogHeight))

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
                myPrint("DB",".. Not running within the EDT so calling via MyPopUpDialogBoxRunnable()...")
                SwingUtilities.invokeAndWait(MyPopUpDialogBoxRunnable(self))
            else:
                myPrint("DB",".. Already within the EDT so calling naked...")
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
            if filename is not None and filename.upper().endswith(self.ext): return True
            return False

    class ExtFileFilterJFC(FileFilter):
        """File extension filter for JFileChooser"""
        def __init__(self, ext): self.ext = "." + ext.upper()

        def getDescription(self): return "*"+self.ext                                                                   # noqa

        def accept(self, _theFile):                                                                                     # noqa
            if _theFile is None: return False
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

        old_dict_filename = os.path.join("..", myFile)

        # Pickle was originally encrypted, no need, migrating to unencrypted
        migratedFilename = os.path.join(MD_REF.getCurrentAccountBook().getRootFolder().getAbsolutePath(),myFile)

        myPrint("DB", "Now checking for parameter file:", migratedFilename)

        if os.path.exists( migratedFilename ):

            myPrint("DB", "loading parameters from non-encrypted Pickle file:", migratedFilename)
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
                myPrint("B","Error opening Pickle File (will try encrypted version) - Unexpected error ", sys.exc_info()[0])
                myPrint("B","Error opening Pickle File (will try encrypted version) - Unexpected error ", sys.exc_info()[1])
                myPrint("B","Error opening Pickle File (will try encrypted version) - Line Number: ", sys.exc_info()[2].tb_lineno)

                # OK, so perhaps from older version - encrypted, try to read
                try:
                    local_storage = MD_REF.getCurrentAccountBook().getLocalStorage()
                    istr = local_storage.openFileForReading(old_dict_filename)
                    load_file = FileUtil.wrap(istr)
                    # noinspection PyTypeChecker
                    GlobalVars.parametersLoadedFromFile = pickle.load(load_file)
                    load_file.close()
                    myPrint("B","Success loading Encrypted Pickle file - will migrate to non encrypted")
                except:
                    myPrint("B","Opening Encrypted Pickle File - Unexpected error ", sys.exc_info()[0])
                    myPrint("B","Opening Encrypted Pickle File - Unexpected error ", sys.exc_info()[1])
                    myPrint("B","Error opening Pickle File - Line Number: ", sys.exc_info()[2].tb_lineno)
                    myPrint("B", "Error: Pickle.load() failed.... Is this a restored dataset? Will ignore saved parameters, and create a new file...")
                    GlobalVars.parametersLoadedFromFile = None

            if GlobalVars.parametersLoadedFromFile is None:
                GlobalVars.parametersLoadedFromFile = {}
                myPrint("DB","Parameters did not load, will keep defaults..")
            else:
                myPrint("DB","Parameters successfully loaded from file...")
        else:
            myPrint("J", "Parameter Pickle file does not exist - will use default and create new file..")
            myPrint("D", "Parameter Pickle file does not exist - will use default and create new file..")
            GlobalVars.parametersLoadedFromFile = {}

        if not GlobalVars.parametersLoadedFromFile: return

        myPrint("DB","GlobalVars.parametersLoadedFromFile read from file contains...:")
        for key in sorted(GlobalVars.parametersLoadedFromFile.keys()):
            myPrint("DB","...variable:", key, GlobalVars.parametersLoadedFromFile[key])

        if GlobalVars.parametersLoadedFromFile.get("debug") is not None: debug = GlobalVars.parametersLoadedFromFile.get("debug")
        if GlobalVars.parametersLoadedFromFile.get("lUseMacFileChooser") is not None:
            myPrint("B", "Detected old lUseMacFileChooser parameter/variable... Will delete it...")
            GlobalVars.parametersLoadedFromFile.pop("lUseMacFileChooser", None)  # Old variable - not used - delete from parameter file

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
        if not isMDThemeDark() and not isMacDarkModeDetected(): return(Color.BLUE)
        return (MD_REF.getUI().getColors().defaultTextForeground)

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

            _label2 = JLabel(pad("StuWareSoftSystems (2020-2022)", 800))
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

    def isMDPlusEnabledBuild(): return (float(MD_REF.getBuild()) >= GlobalVars.MD_MDPLUS_BUILD)                         # 2022.0

    def isAlertControllerEnabledBuild(): return (float(MD_REF.getBuild()) >= GlobalVars.MD_ALERTCONTROLLER_BUILD)       # 2022.3

    # END COMMON DEFINITIONS ###############################################################################################
    # END COMMON DEFINITIONS ###############################################################################################
    # END COMMON DEFINITIONS ###############################################################################################
    # COPY >> END



    # >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
    # >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
    # >>> CUSTOMISE & DO THIS FOR EACH SCRIPT

    def selectAllHomeScreens():

        try:
            firstMF = MD_REF.getUI().firstMainFrame
            secWindows = [secWin for secWin in MD_REF.getUI().getSecondaryWindows() if (isinstance(secWin, MainFrame) and secWin is not firstMF)]
            secWindows.append(firstMF)
            for secWin in secWindows:
                currentViewAccount = secWin.getSelectedAccount()
                if currentViewAccount != MD_REF.getRootAccount():
                    myPrint("DB","Switched to Home Page Summary Page (from: %s) - on main frame: %s" %(currentViewAccount, secWin))
                    secWin.selectAccount(MD_REF.getRootAccount())
        except:
            myPrint("B","@@ Error switching to Summary Page (Home Page)")


    class NoneLock:
        """Used as a 'do-nothing' alternative to a real 'with:' lock"""
        def __init__(self): pass
        def __enter__(self): pass
        def __exit__(self, *args): pass

    def getSwingObjectProxyName(swComponent):
        if swComponent is None: return "None"
        try: rtnStr = unicode(swComponent.__class__.__bases__[0])
        except: rtnStr = "Error"
        return rtnStr

    def load_StuWareSoftSystems_parameters_into_memory():
        myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()" )
        myPrint("DB", "Loading variables into memory...")

        if GlobalVars.parametersLoadedFromFile is None: GlobalVars.parametersLoadedFromFile = {}

        # >>> THESE ARE THIS SCRIPT's PARAMETERS TO LOAD
        if GlobalVars.parametersLoadedFromFile.get("__net_account_balances_extension") is not None:             GlobalVars.__net_account_balances_extension = GlobalVars.parametersLoadedFromFile.get("__net_account_balances_extension")

        if GlobalVars.parametersLoadedFromFile.get("extn_param_listAccountUUIDs_NAB") is not None:              GlobalVars.extn_param_listAccountUUIDs_NAB = GlobalVars.parametersLoadedFromFile.get("extn_param_listAccountUUIDs_NAB")
        if GlobalVars.parametersLoadedFromFile.get("extn_param_balanceType_NAB") is not None:                   GlobalVars.extn_param_balanceType_NAB = GlobalVars.parametersLoadedFromFile.get("extn_param_balanceType_NAB")
        if GlobalVars.parametersLoadedFromFile.get("extn_param_widget_display_name_NAB") is not None:           GlobalVars.extn_param_widget_display_name_NAB = GlobalVars.parametersLoadedFromFile.get("extn_param_widget_display_name_NAB")

        if GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_listAccountUUIDs_NAB") is not None:          GlobalVars.extn_param_NEW_listAccountUUIDs_NAB = GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_listAccountUUIDs_NAB")
        if GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_balanceType_NAB") is not None:               GlobalVars.extn_param_NEW_balanceType_NAB = GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_balanceType_NAB")
        if GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_incomeExpenseDateRange_NAB") is not None:    GlobalVars.extn_param_NEW_incomeExpenseDateRange_NAB = GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_incomeExpenseDateRange_NAB")
        if GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_customDatesTable_NAB") is not None:          GlobalVars.extn_param_NEW_customDatesTable_NAB = GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_customDatesTable_NAB")
        if GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_rowSeparatorTable_NAB") is not None:         GlobalVars.extn_param_NEW_rowSeparatorTable_NAB = GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_rowSeparatorTable_NAB")
        if GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_blinkTable_NAB") is not None:                GlobalVars.extn_param_NEW_blinkTable_NAB = GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_blinkTable_NAB")
        if GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_autoSumAccounts_NAB") is not None:           GlobalVars.extn_param_NEW_autoSumAccounts_NAB = GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_autoSumAccounts_NAB")
        if GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_includeInactive_NAB") is not None:           GlobalVars.extn_param_NEW_includeInactive_NAB = GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_includeInactive_NAB")
        if GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_widget_display_name_NAB") is not None:       GlobalVars.extn_param_NEW_widget_display_name_NAB = GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_widget_display_name_NAB")
        if GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_currency_NAB") is not None:                  GlobalVars.extn_param_NEW_currency_NAB = GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_currency_NAB")
        if GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_disableCurrencyFormatting_NAB") is not None: GlobalVars.extn_param_NEW_disableCurrencyFormatting_NAB = GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_disableCurrencyFormatting_NAB")
        if GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_showWarningsTable_NAB") is not None:         GlobalVars.extn_param_NEW_showWarningsTable_NAB = GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_showWarningsTable_NAB")
        if GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_hideRowWhenXXXTable_NAB") is not None:       GlobalVars.extn_param_NEW_hideRowWhenXXXTable_NAB = GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_hideRowWhenXXXTable_NAB")
        if GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_hideRowXValueTable_NAB") is not None:        GlobalVars.extn_param_NEW_hideRowXValueTable_NAB = GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_hideRowXValueTable_NAB")
        if GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_displayAverageTable_NAB") is not None:       GlobalVars.extn_param_NEW_displayAverageTable_NAB = GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_displayAverageTable_NAB")

        if GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_autoSumDefault_NAB") is not None:            GlobalVars.extn_param_NEW_autoSumDefault_NAB = GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_autoSumDefault_NAB")
        if GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_disableWidgetTitle_NAB") is not None:        GlobalVars.extn_param_NEW_disableWidgetTitle_NAB = GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_disableWidgetTitle_NAB")
        if GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_showDashesInsteadOfZeros_NAB") is not None:  GlobalVars.extn_param_NEW_showDashesInsteadOfZeros_NAB = GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_showDashesInsteadOfZeros_NAB")
        if GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_treatSecZeroBalInactive_NAB") is not None:   GlobalVars.extn_param_NEW_treatSecZeroBalInactive_NAB = GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_treatSecZeroBalInactive_NAB")

        if GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_useIndianNumberFormat_NAB") is not None:     GlobalVars.extn_param_NEW_useIndianNumberFormat_NAB = GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_useIndianNumberFormat_NAB")
        if GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_hideDecimals_NAB") is not None:              GlobalVars.extn_param_NEW_hideDecimals_NAB = GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_hideDecimals_NAB")
        if GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_displayVisualUnderDots_NAB") is not None:    GlobalVars.extn_param_NEW_displayVisualUnderDots_NAB = GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_displayVisualUnderDots_NAB")

        if GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_expandedView_NAB") is not None:              GlobalVars.extn_param_NEW_expandedView_NAB = GlobalVars.parametersLoadedFromFile.get("extn_param_NEW_expandedView_NAB")

        myPrint("DB", "parametersLoadedFromFile{} set into memory (as variables).....:",                        GlobalVars.parametersLoadedFromFile)

        return

    # >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
    def dump_StuWareSoftSystems_parameters_from_memory():
        myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()" )

        # NOTE: Parameters were loaded earlier on... Preserve existing, and update any used ones...
        # (i.e. other StuWareSoftSystems programs might be sharing the same file)

        if GlobalVars.parametersLoadedFromFile is None: GlobalVars.parametersLoadedFromFile = {}

        # >>> THESE ARE THIS SCRIPT's PARAMETERS TO SAVE
        GlobalVars.parametersLoadedFromFile["__net_account_balances_extension"] = version_build

        # Purge old parameters
        for key in ["extn_param_listAccountUUIDs_NAB",
                    "extn_param_balanceType_NAB",
                    "extn_param_widget_display_name_NAB",
                    "extn_param_NEW_acctsCatsSecurities_NAB",
                    "extn_param_NEW_showWarningsDefault_NAB",
                    "extn_param_NEW_autoSumInvestmentAccts_NAB"]:
            if GlobalVars.parametersLoadedFromFile.get(key) is not None: GlobalVars.parametersLoadedFromFile.pop(key)

        # Save newer multi-instance parameters
        GlobalVars.parametersLoadedFromFile["extn_param_NEW_listAccountUUIDs_NAB"]             = GlobalVars.extn_param_NEW_listAccountUUIDs_NAB
        GlobalVars.parametersLoadedFromFile["extn_param_NEW_balanceType_NAB"]                  = GlobalVars.extn_param_NEW_balanceType_NAB
        GlobalVars.parametersLoadedFromFile["extn_param_NEW_incomeExpenseDateRange_NAB"]       = GlobalVars.extn_param_NEW_incomeExpenseDateRange_NAB
        GlobalVars.parametersLoadedFromFile["extn_param_NEW_customDatesTable_NAB"]             = GlobalVars.extn_param_NEW_customDatesTable_NAB
        GlobalVars.parametersLoadedFromFile["extn_param_NEW_rowSeparatorTable_NAB"]            = GlobalVars.extn_param_NEW_rowSeparatorTable_NAB
        GlobalVars.parametersLoadedFromFile["extn_param_NEW_blinkTable_NAB"]                   = GlobalVars.extn_param_NEW_blinkTable_NAB
        GlobalVars.parametersLoadedFromFile["extn_param_NEW_autoSumAccounts_NAB"]              = GlobalVars.extn_param_NEW_autoSumAccounts_NAB
        GlobalVars.parametersLoadedFromFile["extn_param_NEW_includeInactive_NAB"]              = GlobalVars.extn_param_NEW_includeInactive_NAB
        GlobalVars.parametersLoadedFromFile["extn_param_NEW_widget_display_name_NAB"]          = GlobalVars.extn_param_NEW_widget_display_name_NAB
        GlobalVars.parametersLoadedFromFile["extn_param_NEW_currency_NAB"]                     = GlobalVars.extn_param_NEW_currency_NAB
        GlobalVars.parametersLoadedFromFile["extn_param_NEW_disableCurrencyFormatting_NAB"]    = GlobalVars.extn_param_NEW_disableCurrencyFormatting_NAB
        GlobalVars.parametersLoadedFromFile["extn_param_NEW_showWarningsTable_NAB"]            = GlobalVars.extn_param_NEW_showWarningsTable_NAB
        GlobalVars.parametersLoadedFromFile["extn_param_NEW_hideRowWhenXXXTable_NAB"]          = GlobalVars.extn_param_NEW_hideRowWhenXXXTable_NAB
        GlobalVars.parametersLoadedFromFile["extn_param_NEW_hideRowXValueTable_NAB"]           = GlobalVars.extn_param_NEW_hideRowXValueTable_NAB
        GlobalVars.parametersLoadedFromFile["extn_param_NEW_displayAverageTable_NAB"]          = GlobalVars.extn_param_NEW_displayAverageTable_NAB

        GlobalVars.parametersLoadedFromFile["extn_param_NEW_autoSumDefault_NAB"]               = GlobalVars.extn_param_NEW_autoSumDefault_NAB
        GlobalVars.parametersLoadedFromFile["extn_param_NEW_disableWidgetTitle_NAB"]           = GlobalVars.extn_param_NEW_disableWidgetTitle_NAB
        GlobalVars.parametersLoadedFromFile["extn_param_NEW_showDashesInsteadOfZeros_NAB"]     = GlobalVars.extn_param_NEW_showDashesInsteadOfZeros_NAB
        GlobalVars.parametersLoadedFromFile["extn_param_NEW_treatSecZeroBalInactive_NAB"]      = GlobalVars.extn_param_NEW_treatSecZeroBalInactive_NAB

        GlobalVars.parametersLoadedFromFile["extn_param_NEW_useIndianNumberFormat_NAB"]        = GlobalVars.extn_param_NEW_useIndianNumberFormat_NAB
        GlobalVars.parametersLoadedFromFile["extn_param_NEW_hideDecimals_NAB"]                 = GlobalVars.extn_param_NEW_hideDecimals_NAB
        GlobalVars.parametersLoadedFromFile["extn_param_NEW_displayVisualUnderDots_NAB"]       = GlobalVars.extn_param_NEW_displayVisualUnderDots_NAB

        GlobalVars.parametersLoadedFromFile["extn_param_NEW_expandedView_NAB"]                 = GlobalVars.extn_param_NEW_expandedView_NAB

        myPrint("DB", "variables dumped from memory back into parametersLoadedFromFile{}.....:", GlobalVars.parametersLoadedFromFile)

        return

    # clear up any old left-overs....
    destroyOldFrames(myModuleID)

    myPrint("DB", "DEBUG IS ON..")

    if SwingUtilities.isEventDispatchThread():
        myPrint("DB", "FYI - This script/extension is currently running within the Swing Event Dispatch Thread (EDT)")
    else:
        myPrint("DB", "FYI - This script/extension is NOT currently running within the Swing Event Dispatch Thread (EDT)")

    def cleanup_actions(theFrame, md_reference):
        myPrint("DB", "In", inspect.currentframe().f_code.co_name, "()")
        myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

        if theFrame: pass
        # if not theFrame.isActiveInMoneydance:
        #     destroyOldFrames(myModuleID)  # This was killing frames just launched/reinstalled... not needed (I think)
        #
        try:
            md_reference.getUI().setStatus(">> StuWareSoftSystems - thanks for using >> %s......." %(GlobalVars.thisScriptName),0)
        except:
            pass  # If this fails, then MD is probably shutting down.......

        if not GlobalVars.i_am_an_extension_so_run_headless: print(scriptExit)

        cleanup_references()

    # .moneydance_invoke_called() is used via the _invoke.py script as defined in script_info.dict. Not used for runtime extensions
    def moneydance_invoke_called(theCommand):
        # ... modify as required to handle .showURL() events sent to this extension/script...
        myPrint("B", "INVOKE - Received extension command: '%s'" %(theCommand))

    GlobalVars.defaultPrintLandscape = False
    # END ALL CODE COPY HERE ###############################################################################################
    # END ALL CODE COPY HERE ###############################################################################################
    # END ALL CODE COPY HERE ###############################################################################################

    def genericSwingEDTRunner(ifOffEDTThenRunNowAndWait, ifOnEDTThenRunNowAndWait, codeblock, *args):
        """Will detect and then run the codeblock on the EDT"""

        isOnEDT = SwingUtilities.isEventDispatchThread()
        myPrint("DB", "** In .genericSwingEDTRunner(), ifOffEDTThenRunNowAndWait: '%s', ifOnEDTThenRunNowAndWait: '%s', codeblock: '%s', args: '%s'" %(ifOffEDTThenRunNowAndWait, ifOnEDTThenRunNowAndWait, codeblock, args))
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

        myPrint("DB", "** In .genericThreadRunner(), codeblock: '%s', args: '%s'" %(codeblock, args))

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

    def roundTowards(value, target):
        assert (isinstance(value, float)), "ERROR - roundTowards() must be supplied a double/float value! >> received: %s(%s)" %(value, type(value))
        roundedValue = value
        if value < target:
            roundedValue = Math.ceil(value)
        elif value > target:
            roundedValue = Math.floor(value)
        return roundedValue

    # com.infinitekind.moneydance.model.CurrencyType.formatSemiFancy(long, char) : String
    def formatSemiFancy(ct, amt, decimalChar, indianFormat=False):
        # type: (CurrencyType, long, basestring, bool) -> basestring
        """Replicates MD API .formatSemiFancy(), but can override for Indian Number format"""
        if not indianFormat: return ct.formatSemiFancy(amt, decimalChar)                # Just call the MD original for efficiency
        return formatFancy(ct, amt, decimalChar, True, False, indianFormat=indianFormat)

    # com.infinitekind.moneydance.model.CurrencyType.formatFancy(long, char, boolean) : String
    def formatFancy(ct, amt, decimalChar, includeDecimals=True, fancy=True, indianFormat=False, roundingTarget=0.0):
        # type: (CurrencyType, long, basestring, bool, bool, bool, float) -> basestring
        """Replicates MD API .formatFancy() / .formatSemiFancy(), but can override for Indian Number format"""

        # Disabled the standard as .formatSemiFancy() has no option to deselect decimal places!! :-(
        # if not indianFormat:
        #     if not fancy: return ct.formatSemiFancy(amt, decimalChar)                   # Just call the MD original for efficiency
        #     return ct.formatFancy(amt, decimalChar, includeDecimals)                    # Just call the MD original for efficiency

        # decStr = "."; comma = GlobalVars.Strings.UNICODE_THIN_SPACE
        decStr = "." if (decimalChar == ".") else ","
        comma = "," if (decimalChar == ".") else "."

        # Do something special for round towards target (not zero)....
        if not includeDecimals and roundingTarget != 0.0:
            origAmt = ct.getDoubleValue(amt)
            roundedAmt = roundTowards(origAmt, roundingTarget)
            amt = ct.getLongValue(roundedAmt)
            # myPrint("B", "@@ Special formatting rounding towards zero triggered.... Original: %s, Target: %s, Rounded: %s" %(origAmt, roundingTarget, roundedAmt));

        sb = invokeMethodByReflection(ct, "formatBasic", [Long.TYPE, Character.TYPE, Boolean.TYPE], [Long(amt), Character(decimalChar), includeDecimals])
        decPlace = sb.lastIndexOf(decStr)
        if decPlace < 0: decPlace = sb.length()
        minPlace = 1 if (amt < 0) else 0

        commaDividingPos = 3
        while (decPlace - commaDividingPos > minPlace):
            decPlace -= commaDividingPos
            sb.insert(decPlace, comma)
            if indianFormat: commaDividingPos = 2   # In the Indian Number system, numbers > 1000 have commas every 2 places (not 3)....

        if not fancy: return sb.toString()

        sb.insert(0, " ")
        sb.insert(0, ct.getPrefix())
        sb.append(" ")
        sb.append(ct.getSuffix())
        return sb.toString().strip()

    # noinspection PyUnresolvedReferences
    def isAccountActive(acct, balType, checkParents=True, sudoAccount=None):                                            # noqa
        if checkParents:
            if (acct.getAccountOrParentIsInactive()): return False
        else:
            if (acct.getAccountIsInactive()): return False

        # switch this line below back on to ignore inactives when using I/E date range options
        # if sudoAccount is None: sudoAccount = acct
        sudoAccount = acct

        if (sudoAccount.getAccountType() == Account.AccountType.SECURITY):
            if (sudoAccount.getCurrencyType().getHideInUI()): return False
            if (NetAccountBalancesExtension.getNAB().savedTreatSecZeroBalInactive
                    and StoreAccountList.getXBalance(balType, sudoAccount) == 0):
                return False
        else:
            if (sudoAccount.getHideOnHomePage()
                    and StoreAccountList.getXBalance(balType, sudoAccount) == 0):
                return False
        return True

    def accountIncludesInactiveChildren(acct, balType, sudoAccount=None):                                               # noqa
        # type: (Account, int, HoldBalance) -> bool

        for child in acct.getSubAccounts():

            # Delete this line below to ignore inactives when using I/E date range options
            sudoAccount = None

            sudoChild = None
            if sudoAccount is not None:
                sudoChild = sudoAccount.getSubAccountsBalanceObject(child)                                              # noqa

            if (not isAccountActive(child, balType, checkParents=False, sudoAccount=sudoChild)
                    and StoreAccountList.getRecursiveXBalance(balType, (child if sudoChild is None else sudoChild)) != 0):
                return child
            childResult = accountIncludesInactiveChildren(child, balType, sudoAccount=sudoAccount)
            if childResult: return childResult
        return None


    class MyAcctFilter(AcctFilter):

        def __init__(self, _filterIncludeInactive, _autoSum, _preSelectedList, _balType, _incExpDateRange):
            self._filterIncludeInactive = _filterIncludeInactive
            self._autoSum = _autoSum
            self._preSelectedList = _preSelectedList
            self._balType = _balType
            self._incExpDateRange = _incExpDateRange
            myPrint("DB", "MyAcctFilter passed parameters: Only Include Active Accounts: %s. AutoSum: %s. BalType: %s. IncExp Date Range Option: %s. Pre-selected list contains %s entries"
                    %(not _filterIncludeInactive,
                      _autoSum,
                      _balType,
                      _incExpDateRange,
                      len(_preSelectedList)))

        # noinspection PyMethodMayBeStatic
        def matches(self, acct):

            # noinspection PyUnresolvedReferences
            if acct.getAccountType() == Account.AccountType.ROOT: return False

            # if not self._filterIncludeInactive:
            #     if acct.getUUID() not in self._preSelectedList:
            #         return isAccountActive(acct, self._balType)

            return True

    class MyTxnSearch(TxnSearch):
        def __init__(self):     pass
        def matchesAll(self):   return True

    def html_strip_chars(_textToStrip):
        _textToStrip = _textToStrip.replace("  ","&nbsp;&nbsp;")
        _textToStrip = _textToStrip.replace("<","&lt;")
        _textToStrip = _textToStrip.replace(">","&gt;")
        return _textToStrip

    def wrap_HTML_italics(_textToWrap):
        return "<html><i>%s</i></html>" %(html_strip_chars(_textToWrap))

    def wrap_HTML_small(_bigText, _smallText, _smallColor=None, stripBigChars=True, stripSmallChars=True):
        if _smallColor is None: _smallColor = GlobalVars.CONTEXT.getUI().colors.tertiaryTextFG
        _smallColorHex = AwtUtil.hexStringForColor(_smallColor)
        _htmlBigText = html_strip_chars(_bigText) if stripBigChars else _bigText
        _htmlSmallText = html_strip_chars(_smallText) if stripSmallChars else _smallText
        return "<html>%s<small><font color=#%s>%s</font></small></html>" %(_htmlBigText, _smallColorHex, _htmlSmallText)

    class StoreAccountList():

        def __init__(self, obj, _autoSum):
            self.obj = None
            self._autoSum = _autoSum
            if isinstance(obj,Account): self.obj = obj  # type: Account

        @staticmethod
        def getUserXBalance(_type, _acct):
            # type: (int, Account) -> int
            if _type == GlobalVars.BALTYPE_BALANCE:
                return _acct.getUserBalance()
            elif _type == GlobalVars.BALTYPE_CURRENTBALANCE:
                return _acct.getUserCurrentBalance()
            elif _type == GlobalVars.BALTYPE_CLEAREDBALANCE:
                return _acct.getUserClearedBalance()

        @staticmethod
        def getXBalance(_type, _acct):
            # type: (int, Account) -> int
            if _type == GlobalVars.BALTYPE_BALANCE:
                return _acct.getBalance()
            elif _type == GlobalVars.BALTYPE_CURRENTBALANCE:
                return _acct.getCurrentBalance()
            elif _type == GlobalVars.BALTYPE_CLEAREDBALANCE:
                return _acct.getClearedBalance()

        @staticmethod
        def getRecursiveUserXBalance(_type, _acct):
            # type: (int, Account) -> int
            if _type == GlobalVars.BALTYPE_BALANCE:
                return _acct.getRecursiveUserBalance()
            elif _type == GlobalVars.BALTYPE_CURRENTBALANCE:
                return _acct.getRecursiveUserCurrentBalance()
            elif _type == GlobalVars.BALTYPE_CLEAREDBALANCE:
                return _acct.getRecursiveUserClearedBalance()

        @staticmethod
        def getRecursiveXBalance(_type, _acct):
            # type: (int, Account) -> int
            if _type == GlobalVars.BALTYPE_BALANCE:
                return _acct.getRecursiveBalance()
            elif _type == GlobalVars.BALTYPE_CURRENTBALANCE:
                return _acct.getRecursiveCurrentBalance()
            elif _type == GlobalVars.BALTYPE_CLEAREDBALANCE:
                return _acct.getRecursiveClearedBalance()

        def getAccount(self): return self.obj

        def __str__(self):
            if self.obj is None: return "Invalid Acct Obj or None"
            return self.getAccount().toString()

        def __repr__(self): return self.__str__()

        def toString(self): return self.__str__()

    # noinspection PyUnusedLocal
    class MyQuickSearchDocListener(DocumentListener):
        def __init__(self, _what):      self._what = _what
        def changedUpdate(self, evt):   self._what.searchFiltersUpdated()
        def removeUpdate(self, evt):    self._what.searchFiltersUpdated()
        def insertUpdate(self, evt):    self._what.searchFiltersUpdated()

    # noinspection PyUnusedLocal
    class MyQuickSearchFocusAdapter(FocusAdapter):
        def __init__(self, _searchField, _document):
            self._searchField = _searchField
            self._document = _document

        def focusGained(self, e): self._searchField.setCaretPosition(self._document.getLength())

    def sendMessage(extensionID, theMessage):
        myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()")
        # replicating moneydance.showURL("moneydance:fmodule:net_account_balances:myCommand_here?thisIsMyParameter")

        frs = getMyJFrame(extensionID)
        if frs:
            myPrint("DB", "... found frame: %s - requesting .invoke(%s)" %(frs, theMessage))
            return frs.MoneydanceAppListener.invoke("%s:customevent:%s" %(extensionID,theMessage))
        else:
            myPrint("DB", ".. Sorry - did not find my application (JFrame) to send message....")
        return


    # My attempts below to switch my GUI's LaF to match MD after a Theme switch
    # Basically doesn't work... As MD doesn't set all properties up properly after a switch
    # So user just needs to restart MD.....
    # All properties: https://thebadprogrammer.com/swing-uimanager-keys/


    def setJComponentStandardUIDefaults(component, opaque=False, border=False, background=True, foreground=True, font=True):

        if isinstance(component,    JPanel):            key = "Panel"
        elif isinstance(component,  JLabel):            key = "Label"
        elif isinstance(component,  JComboBox):         key = "ComboBox"
        elif isinstance(component,  JButton):           key = "Button"
        elif isinstance(component,  JRadioButton):      key = "RadioButton"
        elif isinstance(component,  JTextField):        key = "TextField"
        elif isinstance(component,  JCheckBox):         key = "CheckBox"
        elif isinstance(component,  JScrollPane):       key = "ScrollPane"
        elif isinstance(component,  JMenu):             key = "Menu"
        elif isinstance(component,  JMenuBar):          key = "MenuBar"
        elif isinstance(component,  JCheckBoxMenuItem): key = "CheckBoxMenuItem"
        elif isinstance(component,  JMenuItem):         key = "MenuItem"
        elif isinstance(component,  JSeparator):        key = "Separator"
        else: raise Exception("Error in setJComponentStandardUIDefaults() - unknown Component instance: %s" %(component))

        if opaque: component.setOpaque(UIManager.getBoolean("%s.opaque" %(key)))

        if isinstance(component, (JMenu)) or component.getClientProperty("%s.id.reversed" %(myModuleID)):
            SetupMDColors.updateUI()
            component.setForeground(SetupMDColors.FOREGROUND_REVERSED)
            component.setBackground(SetupMDColors.BACKGROUND_REVERSED)
        else:
            if foreground: component.setForeground(UIManager.getColor("%s.foreground" %(key)))
            if background and (component.isOpaque() or isinstance(component, (JComboBox, JTextField, JMenuBar))):
                component.setBackground(UIManager.getColor("%s.background" %(key)))

        if border: component.setBorder(UIManager.getBorder("%s.border" %(key)))
        if font:   component.setFont(UIManager.getFont("%s.font" %(key)))

    class MyJPanel(JPanel):

        def __init__(self, *args, **kwargs):
            super(self.__class__, self).__init__(*args, **kwargs)

        def updateUI(self):
            super(self.__class__, self).updateUI()
            setJComponentStandardUIDefaults(self)

    class MyJLabel(JLabel):

        def __init__(self, *args, **kwargs):
            self.hasMDHeaderBorder = False
            super(self.__class__, self).__init__(*args, **kwargs)

        def updateUI(self):
            super(self.__class__, self).updateUI()
            setJComponentStandardUIDefaults(self)

            if self.hasMDHeaderBorder: self.setMDHeaderBorder()

        def setMDHeaderBorder(self):
            self.hasMDHeaderBorder = True
            self.setBorder(BorderFactory.createLineBorder(GlobalVars.CONTEXT.getUI().colors.headerBorder))

    class MyJComboBox(JComboBox):

        def __init__(self, *args, **kwargs):
            super(self.__class__, self).__init__(*args, **kwargs)

        def updateUI(self):
            super(self.__class__, self).updateUI()
            setJComponentStandardUIDefaults(self)

    class MyJButton(JButton):

        def __init__(self, *args, **kwargs):
            super(self.__class__, self).__init__(*args, **kwargs)

        def updateUI(self):
            super(self.__class__, self).updateUI()
            # setJComponentStandardUIDefaults(self, key, opaque=True, border=True)
            setJComponentStandardUIDefaults(self)

    class MyJRadioButton(JRadioButton):

        def __init__(self, *args, **kwargs):
            super(self.__class__, self).__init__(*args, **kwargs)

        def updateUI(self):
            super(self.__class__, self).updateUI()
            # setJComponentStandardUIDefaults(self, key, opaque=True, border=True)
            setJComponentStandardUIDefaults(self)

    class MyJTextField(JTextField):

        def __init__(self, *args, **kwargs):
            super(self.__class__, self).__init__(*args, **kwargs)

        def updateUI(self):
            super(self.__class__, self).updateUI()
            setJComponentStandardUIDefaults(self)

    class MyJRateFieldXValue(JRateField):

        def __init__(self, *args, **kwargs):
            super(self.__class__, self).__init__(*args, **kwargs)
            self.setShortRatesEnabled(True)
            self.setDefaultValue(0.0)
            self.setAllowBlank(False)

        def updateUI(self):
            super(self.__class__, self).updateUI()
            setJComponentStandardUIDefaults(self)

    class MyJRateFieldAverage(JRateField):

        def __init__(self, *args, **kwargs):
            super(self.__class__, self).__init__(*args, **kwargs)
            self._defaultValue = 1.0
            self.setShortRatesEnabled(True)
            self.setDefaultValue(self._defaultValue)
            self.setAllowBlank(False)

        def getDefaultValue(self): return self._defaultValue

        def notAllowed(self): return 0.0

        def getValue(self):
            val = super(self.__class__, self).getValue()
            if val is None or val == self.notAllowed():
                val = self.getDefaultValue()
            return val

        def setValue(self, val):
            if val is None or val == self.notAllowed():
                val = self.getDefaultValue()
            super(self.__class__, self).setValue(val)

        def updateUI(self):
            super(self.__class__, self).updateUI()
            setJComponentStandardUIDefaults(self)

    class MyJCheckBox(JCheckBox):

        def __init__(self, *args, **kwargs):
            super(self.__class__, self).__init__(*args, **kwargs)

        def updateUI(self):
            super(self.__class__, self).updateUI()
            # setJComponentStandardUIDefaults(self, border=True)
            setJComponentStandardUIDefaults(self)

    class MyJScrollPane(JScrollPane):

        def __init__(self, *args, **kwargs):
            super(self.__class__, self).__init__(*args, **kwargs)

        def updateUI(self):
            super(self.__class__, self).updateUI()
            setJComponentStandardUIDefaults(self, border=True)

    class MyJMenu(JMenu):

        def __init__(self, *args, **kwargs):
            super(self.__class__, self).__init__(*args, **kwargs)

        def updateUI(self):
            super(self.__class__, self).updateUI()
            # setJComponentStandardUIDefaults(self)

    class MyJMenuBar(JMenuBar):

        def __init__(self, *args, **kwargs):
            super(self.__class__, self).__init__(*args, **kwargs)

        def updateUI(self):
            super(self.__class__, self).updateUI()
            # setJComponentStandardUIDefaults(self)

    class MyJCheckBoxMenuItem(JCheckBoxMenuItem):

        def __init__(self, *args, **kwargs):
            super(self.__class__, self).__init__(*args, **kwargs)

        def updateUI(self):
            super(self.__class__, self).updateUI()
            # setJComponentStandardUIDefaults(self, border=True)

    class MyJMenuItem(JMenuItem):

        def __init__(self, *args, **kwargs):
            super(self.__class__, self).__init__(*args, **kwargs)

        def updateUI(self):
            super(self.__class__, self).updateUI()
            # setJComponentStandardUIDefaults(self, border=True)

    class MyJSeparator(JSeparator):

        def __init__(self, *args, **kwargs):
            super(self.__class__, self).__init__(*args, **kwargs)

        def updateUI(self):
            super(self.__class__, self).updateUI()
            setJComponentStandardUIDefaults(self, border=True, background=False)

    class MyQuickSearchField(QuickSearchField):

        def __init__(self, *args, **kwargs):
            super(self.__class__, self).__init__(*args, **kwargs)

        def updateUI(self):
            super(self.__class__, self).updateUI()
            self.setBackground(GlobalVars.CONTEXT.getUI().colors.defaultBackground)
            self.setOuterBackground(GlobalVars.CONTEXT.getUI().colors.headerBG)
            self.setForeground(GlobalVars.CONTEXT.getUI().colors.defaultTextForeground)

    # ------------------------------------------------------------------------------------------------------------------
    # com.infinitekind.moneydance.model.AccountUtil.ACCOUNT_TYPE_NAME_COMPARATOR : Comparator


    def compareAccountType(acctType1, acctType2):
        code1 = acctType1.code()
        code2 = acctType2.code()
        if code1 < code2: return -1
        if code1 > code2: return 1
        return 0


    def compareAccountsByHierarchy(a1, a2):
        # com.infinitekind.moneydance.model.AccountUtil.compareAccountsByHierarchy(Account, Account) : int
        if (a1 is None and a2 is None):
            return 0
        elif a1 is None:
            return -1
        elif a2 is None:
            return 1

        depth1 = a1.getDepth()
        depth2 = a2.getDepth()
        maxDepth = Math.max(depth1, depth2) + 1

        for i in range(0,maxDepth):
            parent1 = a1.getParentAtDepth(i)
            parent2 = a2.getParentAtDepth(i)

            if parent1 is None and parent2 is None: return 0
            if parent1 is None: return -1
            if parent2 is None: return 1

            if parent1 != parent2:
                typeComparison = compareAccountType(parent1.getAccountType(), parent2.getAccountType())
                if typeComparison != 0:
                    return typeComparison

                nameComparison = String(parent1.getAccountName()).compareToIgnoreCase(String(parent2.getAccountName()))
                if nameComparison != 0:
                    return nameComparison

                uuidComparison = String(parent1.getUUID()).compareToIgnoreCase(String(parent2.getUUID()))
                if uuidComparison != 0:
                    return uuidComparison
        return 0


    class AccountItemSorter(Comparator):
        def compare(self, o1, o2): return compareAccountsByHierarchy(o1, o2)

    class MyAccountIterator(Iterator):
        # com.infinitekind.moneydance.model.AccountIterator

        accountItemSorter = AccountItemSorter()

        def __init__(self, book):

            if book is None:
                self.allAccounts = None
                self.nextAccount = None
            else:
                allItems = book.getItemsWithType("acct")
                Collections.sort(allItems, MyAccountIterator.accountItemSorter)
                self.allAccounts = allItems.iterator()
                self.findNextItem()

        def hasNext(self): return self.nextAccount is not None

        def next(self):
            returnVal = self.nextAccount
            self.findNextItem()
            return returnVal

        def findNextItem(self):
            if self.allAccounts is None:
                self.nextAccount = None
                return

            while self.allAccounts.hasNext():
                self.nextAccount = self.allAccounts.next()
                return
            self.nextAccount = None


    def allMatchesForSearch(book, search):
        # com.infinitekind.moneydance.model.AccountUtil.allMatchesForSearch(AccountBook, AcctFilter) : List
        accts = []
        ai = MyAccountIterator(book)
        for _acct in ai:
            if search.matches(_acct): accts.append(_acct)
        return accts
    # ------------------------------------------------------------------------------------------------------------------

    # noinspection PyUnresolvedReferences
    def isIncomeExpenseAcct(_acct):
        return (_acct.getAccountType() == Account.AccountType.EXPENSE or _acct.getAccountType() == Account.AccountType.INCOME)

    # noinspection PyUnresolvedReferences
    def isSecurityAcct(_acct):      return (_acct.getAccountType() == Account.AccountType.SECURITY)

    # noinspection PyUnresolvedReferences
    def isInvestmentAcct(_acct):    return (_acct.getAccountType() == Account.AccountType.INVESTMENT)

    # noinspection PyUnresolvedReferences
    def isRootAcct(_acct):          return (_acct.getAccountType() == Account.AccountType.ROOT)


    class MyAcctFilterIncExpOnly(AcctFilter):
        def __init__(self):         pass
        def matches(self, acct):    return isIncomeExpenseAcct(acct)


    def isIncomeExpenseAllDatesSelected(index):
        NAB = NetAccountBalancesExtension.getNAB()
        return (NAB.savedIncomeExpenseDateRange[index] == NAB.incomeExpenseDateRangeDefault())

    def buildEmptyTxnOrBalanceArray():
        # type: () -> [{}]
        NAB = NetAccountBalancesExtension.getNAB()
        table = []
        for i in range(0, NAB.getNumberOfRows()): table.append({})
        return table

    def buildEmptyDateRangeArray():
        # type: () -> [[]]
        NAB = NetAccountBalancesExtension.getNAB()
        table = []
        for i in range(0, NAB.getNumberOfRows()): table.append([])
        return table

    def buildEmptyAccountList():
        # type: () -> [[]]
        NAB = NetAccountBalancesExtension.getNAB()
        table = []
        for i in range(0, NAB.getNumberOfRows()): table.append([])
        return table

    def isParallelBalanceTableOperational():
        NAB = NetAccountBalancesExtension.getNAB()

        lAnyParallel = False
        for iRowIndex in range(0, NAB.getNumberOfRows()):
            onRow = iRowIndex+1
            if NAB.savedIncomeExpenseDateRange[iRowIndex] != NAB.incomeExpenseDateRangeDefault():
                myPrint("DB", "** Row: %s >> Parallel Balances based on Txns is in operation.." %(onRow))
                lAnyParallel = True

        myPrint("DB", "** Setting Parallel Balances Detected flag to '%s'" %(lAnyParallel))
        NAB.parallelBalanceTableOperating = lAnyParallel
        return NAB.parallelBalanceTableOperating

    def rebuildParallelAccountBalances(swClass):
        # type: (SwingWorker) -> [{Account: [HoldBalance]}]

        myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()" )

        NAB = NetAccountBalancesExtension.getNAB()
        iRowIdx = NAB.getSelectedRowIndex()

        if isIncomeExpenseAllDatesSelected(iRowIdx):
            myPrint("DB", ".. Skipping build of parallel balances table for Income/Expense as not needed (as using all dates)...")
            return buildEmptyTxnOrBalanceArray()

        getAccounts = allMatchesForSearch(NAB.moneydanceContext.getCurrentAccountBook(), MyAcctFilterIncExpOnly())

        myPrint("DB", "Building Parallel Account Balances Table for Income/Expense (from Txs)....:")

        incExpTxnTable = buildEmptyTxnOrBalanceArray()         # type: [{Account: [AbstractTxn]}]
        for acct in getAccounts: incExpTxnTable[iRowIdx][acct] = []

        if not swClass.isCancelled():
            returnTransactionsForAccounts(incExpTxnTable, swClass)

        incExpBalanceTable = None

        if not swClass.isCancelled():
            incExpBalanceTable = convertTxnTableIntoBalances(incExpTxnTable, swClass, lBuildParallelTable=True)

        del getAccounts, incExpTxnTable

        return incExpBalanceTable

    def returnThisAccountAndAllChildren(_acct, _listAccounts=None, autoSum=False, justIncomeExpense=True):
        # type: (Account, [Account], bool, bool) -> [Account]
        if _listAccounts is None: _listAccounts = []

        if justIncomeExpense and not isIncomeExpenseAcct(_acct): return _listAccounts

        if _acct not in _listAccounts: _listAccounts.append(_acct)
        if autoSum:
            for child in _acct.getSubAccounts(): returnThisAccountAndAllChildren(child, _listAccounts, autoSum=autoSum, justIncomeExpense=justIncomeExpense)
        return _listAccounts

    def isValidDateRange(_startInt, _endInt):

        if not isinstance(_startInt, int):              return False
        if not isinstance(_endInt, int):                return False
        if _startInt <= GlobalVars.DATE_RANGE_VALID:    return False
        if _endInt   <= GlobalVars.DATE_RANGE_VALID:    return False
        if _startInt > _endInt:                         return False
        return True

    def getDateRangeSelected(_fromRangeKey, _fromCustomDates):
        # type: (str, list) -> DateRange

        # myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()" )
        # myPrint("DB", ".. Passed '%s'Date Range with '%s':" %(_fromRangeKey, _fromCustomDates))

        if _fromRangeKey == DateRangeOption.DR_ALL_DATES.getResourceKey():
            raise Exception("ERROR: getDateRangeSelected should not be passed: '%s'" %(_fromRangeKey))

        if _fromRangeKey == DateRangeOption.DR_CUSTOM_DATE.getResourceKey():

            if isValidDateRange(_fromCustomDates[0], _fromCustomDates[1]):
                # myPrint("DB", "... Returning custom date range for key: '%s'" %(_fromRangeKey))
                dateRange = DateRange(Integer(_fromCustomDates[0]), Integer(_fromCustomDates[1]))
            else:
                # myPrint("DB", "..... ALERT >> No valid custom start/end dates found! Will use defaults")
                dateRange = DateRangeOption.DR_CUSTOM_DATE.getDateRange()
        else:
            dateRange = DateRangeOption.fromKey(_fromRangeKey).getDateRange()

        # myPrint("DB", ".. '%s'Date Range set to:" %(_fromRangeKey), dateRange)
        return dateRange

    def updateIncExpTableWithTxn(_txn, _table, _dateRangeArray):
        # type: (AbstractTxn, [{Account: [AbstractTxn]}], [[int, int]]) -> None

        for iRow in range(len(_table)):

            if len(_table[iRow]) < 1: continue

            _acct = _txn.getAccount()
            if _acct not in _table[iRow]: continue

            dateInt = _txn.getDateInt()
            if dateInt >= _dateRangeArray[iRow][0] and dateInt <= _dateRangeArray[iRow][1]:
                _table[iRow][_acct].append(_txn)

    def zapIncExpTableOfTxns(_table):
        # type: ([{Account: [AbstractTxn]}]) -> None

        for iRow in range(len(_table)):
            for acct in _table[iRow]:
                _table[iRow][acct] = []

    # def searchIncExpTableForAccount(_acct, _table):
    #     # type: (Account, [{Account: [AbstractTxn]}]) -> bool
    #     for iRow in range(len(_table)):
    #         if _acct in _table[iRow]: return True
    #     return False

    class HoldBalance():

        def __init__(self, acct, autoSum):
            self.acct = acct
            self.startBalance = 0
            self.balance = 0
            self.currentBalance = 0
            self.clearedBalance = 0
            self.subAccountsBalanceObjects = {}
            self.autoSum = autoSum
            self.autoSum = autoSum
            self.NAB = NetAccountBalancesExtension.getNAB()

            if not isinstance(acct, Account):
                raise Exception("ERROR: HoldBalance can only hold Account objects")

            if not isIncomeExpenseAcct(acct):
                raise Exception("ERROR: HoldBalance only programmed for Income/Expense Categories")

        def getAccount(self):               return self.acct

        def getAccountName(self):           return self.getAccount().getAccountName()
        def getFullAccountName(self):       return self.getAccount().getFullAccountName()
        def getAccountType(self):           return self.getAccount().getAccountType()
        def getCurrencyType(self):          return self.getAccount().getCurrencyType()
        def getHideOnHomePage(self):        return self.getAccount().getHideOnHomePage()

        def shouldIncludeInactive(self):    return (self.NAB.savedIncludeInactive[self.NAB.getSelectedRowIndex()])

        def isAutoSum(self):                                        return self.autoSum
        def setSubAccountsBalanceObjects(self, _subAccountObjects): self.subAccountsBalanceObjects = _subAccountObjects
        def getSubAccountsBalanceObject(self, _acct):               return self.subAccountsBalanceObjects[_acct]

        def getXBalance(self, _balType, _autoSum):
            if _balType == GlobalVars.BALTYPE_BALANCE:          return self.getBalance()         if not _autoSum else self.getRecursiveBalance()
            elif _balType == GlobalVars.BALTYPE_CURRENTBALANCE: return self.getCurrentBalance()  if not _autoSum else self.getRecursiveCurrentBalance()
            elif _balType == GlobalVars.BALTYPE_CLEAREDBALANCE: return self.getClearedBalance()  if not _autoSum else self.getRecursiveClearedBalance()

        def getStartBalance(self):       return (self.startBalance)

        def getBalance(self):
            # if not self.shouldIncludeInactive() and not isAccountActive(self.getAccount(),GlobalVars.BALTYPE_BALANCE, self): return 0
            return (self.getStartBalance() + self.balance)

        def getCurrentBalance(self):
            # if not self.shouldIncludeInactive() and not isAccountActive(self.getAccount(),GlobalVars.BALTYPE_CURRENTBALANCE, self): return 0
            return (self.getStartBalance() + self.currentBalance)

        def getClearedBalance(self):
            # if not self.shouldIncludeInactive() and not isAccountActive(self.getAccount(),GlobalVars.BALTYPE_CLEAREDBALANCE, self): return 0
            return (self.getStartBalance() + self.clearedBalance)

        def balanceIsNegated(self):      return self.getAccount().balanceIsNegated()

        def getUserBalance(self):        return (-self.getBalance()        if self.balanceIsNegated() else self.getBalance())
        def getUserCurrentBalance(self): return (-self.getCurrentBalance() if self.balanceIsNegated() else self.getCurrentBalance())
        def getUserClearedBalance(self): return (-self.getClearedBalance() if self.balanceIsNegated() else self.getClearedBalance())

        def getRecursiveUserBalance(self):        return (-self.getRecursiveBalance()        if self.balanceIsNegated() else self.getRecursiveBalance())
        def getRecursiveUserCurrentBalance(self): return (-self.getRecursiveCurrentBalance() if self.balanceIsNegated() else self.getRecursiveCurrentBalance())
        def getRecursiveUserClearedBalance(self): return (-self.getRecursiveClearedBalance() if self.balanceIsNegated() else self.getRecursiveClearedBalance())

        def setStartBalance(self, _bal):    self.startBalance   = _bal
        def setBalance(self, _bal):         self.balance        = _bal
        def setCurrentBalance(self, _bal):  self.currentBalance = _bal
        def setClearedBalance(self, _bal):  self.clearedBalance = _bal

        def getRecursiveStartBalance(self):
            bal = self.getStartBalance()
            if not self.isAutoSum(): return bal
            thisAcct = self.getAccount()
            for i in reversed(range(0, thisAcct.getSubAccountCount())):
                subAcct = thisAcct.getSubAccount(i)
                try:
                    bal += CurrencyUtil.convertValue(self.getSubAccountsBalanceObject(subAcct).getRecursiveStartBalance(),
                                                     subAcct.getCurrencyType(),
                                                     thisAcct.getCurrencyType())
                except: dump_sys_error_to_md_console_and_errorlog()
            return bal

        def getRecursiveBalance(self):
            bal = self.getBalance()
            if not self.isAutoSum(): return bal
            thisAcct = self.getAccount()
            for i in reversed(range(0, thisAcct.getSubAccountCount())):
                subAcct = thisAcct.getSubAccount(i)
                try:
                    bal += CurrencyUtil.convertValue(self.getSubAccountsBalanceObject(subAcct).getRecursiveBalance(),
                                                     subAcct.getCurrencyType(),
                                                     thisAcct.getCurrencyType())
                except: dump_sys_error_to_md_console_and_errorlog()
            return bal


        def getRecursiveCurrentBalance(self):
            bal = self.getCurrentBalance()
            if not self.isAutoSum(): return bal
            thisAcct = self.getAccount()
            for i in reversed(range(0, thisAcct.getSubAccountCount())):
                subAcct = thisAcct.getSubAccount(i)
                try:
                    bal += CurrencyUtil.convertValue(self.getSubAccountsBalanceObject(subAcct).getRecursiveCurrentBalance(),
                                                     subAcct.getCurrencyType(),
                                                     thisAcct.getCurrencyType())
                except: dump_sys_error_to_md_console_and_errorlog()
            return bal

        def getRecursiveClearedBalance(self):
            bal = self.getClearedBalance()
            if not self.isAutoSum(): return bal
            thisAcct = self.getAccount()
            for i in reversed(range(0, thisAcct.getSubAccountCount())):
                subAcct = thisAcct.getSubAccount(i)
                try:
                    bal += CurrencyUtil.convertValue(self.getSubAccountsBalanceObject(subAcct).getRecursiveClearedBalance(),
                                                     subAcct.getCurrencyType(),
                                                     thisAcct.getCurrencyType())
                except: dump_sys_error_to_md_console_and_errorlog()
            return bal

        def __str__(self):
            return ("Account: %s Bal: %s, CurBal: %s, ClearedBal: %s, RBal: %s, RCurBal: %s, RClearedBal: %s"
                    %(self.getAccount(),
                      self.getBalance(), self.getCurrentBalance(), self.getClearedBalance(),
                      self.getRecursiveBalance(), self.getRecursiveCurrentBalance(), self.getRecursiveClearedBalance()))

        def __repr__(self): return self.__str__()
        def toString(self): return self.__str__()


    def convertTxnTableIntoBalances(_incExpTable, swClass, lBuildParallelTable=False):
        # type: ([{Account: [AbstractTxn]}], SwingWorker, bool) -> [{Account: [HoldBalance]}]

        myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()" )

        NAB = NetAccountBalancesExtension.getNAB()

        _incExpBalanceTable = buildEmptyTxnOrBalanceArray()

        today = DateUtil.getStrippedDateInt()

        for iRow in range(len(_incExpTable)):

            for acct in _incExpTable[iRow]:

                if swClass.isCancelled(): break

                balanceObj = HoldBalance(acct, (True if lBuildParallelTable else NAB.savedAutoSumAccounts[iRow]))
                if balanceObj.getBalance() != 0: raise Exception("ERROR: Acct: %s getBalance(%s) != ZERO?" %(acct, balanceObj.getBalance()))

                # dateRange = DateRangeOption.fromKey(NAB.savedIncomeExpenseDateRange[iRow])
                dateRange = getDateRangeSelected(NAB.savedIncomeExpenseDateRange[iRow], NAB.savedCustomDatesTable[iRow])
                # if (acct.getCreationDateInt() >= dateRange.getDateRange().getStartDateInt()
                #         and acct.getCreationDateInt() <= dateRange.getDateRange().getEndDateInt()):
                if (acct.getCreationDateInt() >= dateRange.getStartDateInt()
                        and acct.getCreationDateInt() <= dateRange.getEndDateInt()):
                    myPrint("DB", ".. @@ Adding in start balance of: %s to Account: %s" %(acct.getStartBalance(), acct))
                    balanceObj.setStartBalance(acct.getStartBalance())

                for txn in _incExpTable[iRow][acct]:
                    txnAcct = txn.getAccount()
                    if txnAcct != acct: raise Exception("ERROR: Acct:%s does not match txn acct: %s" %(acct, txnAcct))

                    txnVal = txn.getValue()
                    txnDate = txn.getDateInt()
                    txnStatus = txn.getClearedStatus()

                    balanceObj.setBalance(balanceObj.getBalance() + txnVal)

                    if txnDate <= today:
                        balanceObj.setCurrentBalance(balanceObj.getCurrentBalance() + txnVal)

                    # noinspection PyUnresolvedReferences
                    if txnStatus == AbstractTxn.ClearedStatus.CLEARED:
                        balanceObj.setClearedBalance(balanceObj.getClearedBalance() + txnVal)

                balanceObj.setSubAccountsBalanceObjects(_incExpBalanceTable[iRow])
                _incExpBalanceTable[iRow][acct] = balanceObj

        if debug:
            myPrint("DB", "-------------------------------------")
            myPrint("DB", ">> Analysis of new I/E Balance Table:")
            myPrint("DB", ">> _incExpBalanceTable Contains: %s rows" %(len(_incExpBalanceTable)))
            for i in range(0, len(_incExpBalanceTable)):
                myPrint("DB", "..RowIdx: %s >> " %(i))
                row = _incExpBalanceTable[i]
                for acct in row: myPrint("DB", "....", acct, _incExpBalanceTable[i][acct])
            myPrint("DB", "------------------------------------")

        return _incExpBalanceTable

    def returnTransactionsForAccounts(_incExpTable, swClass):
        # type: ([{Account: [AbstractTxn]}], SwingWorker) -> [{Account: [AbstractTxn]}]

        myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()" )

        startTime = System.currentTimeMillis()

        NAB = NetAccountBalancesExtension.getNAB()

        md = GlobalVars.CONTEXT
        book = md.getCurrentAccountBook()

        # pre-build table containing valid date ranges - for speed....
        _dateRangeArray = buildEmptyDateRangeArray()
        for iRow in range(len(_incExpTable)):

            if len(_incExpTable[iRow]) < 1: continue

            dateRange = getDateRangeSelected(NAB.savedIncomeExpenseDateRange[iRow], NAB.savedCustomDatesTable[iRow])
            _dateRangeArray[iRow] = [dateRange.getStartDateInt(), dateRange.getEndDateInt()]

        iTxns = 0                                                                                                       # noqa
        attempts = 0

        ################################################################################################################
        # This way returns the "flipped" SplitTxns (which is OK), but the TxnSet is not locked and can crash if list modified
        #
        # while True:
        #     if swClass.isCancelled(): break
        #
        #     # One sweep big of Txns
        #     try:
        #         attempts += 1
        #         txnIterator = TxnIterator(book.getTransactionSet())
        #
        #         iTxns = 0
        #
        #         for txn in txnIterator:
        #
        #             if swClass.isCancelled(): break
        #
        #             iTxns += 1
        #             # if not searchIncExpTableForAccount(txn.getAccount(), _incExpTable): continue
        #             updateIncExpTableWithTxn(txn, _incExpTable, _dateRangeArray)
        #
        #         del txnIterator
        #
        #     except ConcurrentModificationException:
        #         myPrint("B", "@@ Error: Caught 'ConcurrentModificationException' in returnTransactionsForAccounts() whilst iterating txns.. Attempts so far: %s" %(attempts))
        #         myPrint("B", "@@ Current SwingWorkers are:", NAB.swingWorkers)
        #         # dump_sys_error_to_md_console_and_errorlog()
        #         if attempts < 3 and not swClass.isCancelled():
        #             myPrint("B", "... Will sleep on it and then retry....")
        #             Thread.sleep(2000)
        #             zapIncExpTableOfTxns(_incExpTable)
        #             continue
        #
        #         myPrint("B", "... Aborting attempts.....")
        #         raise
        #
        #     break       # We made it!


        ################################################################################################################
        # One sweep big of Txns: This method returns the 'old' ParentTxn/SplitTxn records AND the TxnSet is locked....
        try:
            attempts += 1

            txnSet = book.getTransactionSet().getTransactions(MyTxnSearch())        # using matchesAll() TRUE is faster

            iTxns = 0

            for txn in txnSet:

                if swClass.isCancelled(): break

                iTxns += 1
                # if not searchIncExpTableForAccount(txn.getAccount(), _incExpTable): continue
                updateIncExpTableWithTxn(txn, _incExpTable, _dateRangeArray)

            del txnSet

        except:
            myPrint("B", "@@ ERROR: .returnTransactionsForAccounts() failed whilst iterating TxnSet: book.getTransactionSet().getTransactions(MyTxnSearch())")
            dump_sys_error_to_md_console_and_errorlog()
            raise

        if debug:
            myPrint("DB", "------------------------------")
            myPrint("DB", "Attempts: %s" %(attempts))
            myPrint("DB", ">> Analysis of I/E Txns Table:")
            myPrint("DB", ">> IncExpTable Contains: %s rows" %(len(_incExpTable)))
            for i in range(0, len(_incExpTable)):
                myPrint("DB", ".... RowIdx: %s Contains: %s accounts" %(i, len(_incExpTable[i])))
                for a in _incExpTable[i]:
                    myPrint("DB", "...... >> Account: %s Contains %s Harvested Txns" %(a.getAccountName(), len(_incExpTable[i][a])))
            myPrint("DB", "------------------------------")


        myPrint("DB", ">>  returnTransactionsForAccounts (Txn Iterator) TOOK: %s milliseconds (%s seconds) - to parse %s Txns"
                %((System.currentTimeMillis() - startTime), (System.currentTimeMillis() - startTime) / 1000.0, iTxns))

        return _incExpTable

    def debugMDDateRangeOption():
        if not debug: return
        today = DateUtil.getStrippedDateInt()
        myPrint("B", "Analysis of MD DateRangeOption used in NAB:")
        myPrint("B", "-------------------------------------------")
        for v in sorted(DateRangeOption.values(), key=lambda x: (x.getSortKey())):
            # if v == DateRangeOption.DR_CUSTOM_DATE: continue
            dr = v.getDateRange()
            start = dr.getStartDateInt()                                                                                # noqa
            end = dr.getEndDateInt()
            future = ("**future**" if end > today else pad("",10))
            myPrint("B", "DR Option: %s Range: %s %s" %(pad(v,30), dr, future))
        myPrint("B", "-------------------------------------------")

    def detectMDClosingError(e):
        if "'NoneType' object has no attribute".lower() in e.message.lower():
            myPrint("B", "Detected that MD is probably closing... Aborting whatever I was doing...")
            return True
        return False

    class MyCollapsibleRefresher:
        """"com.moneydance.awt.CollapsibleRefresher
        Class that enables easy collapsible refreshing.  That is, if you expect to receive a lot of updates
        to a data model that the UI can't keep up with, you can use this to enqueue a Runnable that will
        refresh your UI that won't queue up more than one Runnable on the swing event dispatch thread.

        Multiple .enqueue()s will get ignored.... The first gets pushed to the EDT via .invokeLater()
        EXCEPT: Where an enqueued job has started on the EDT, then the next enqueued will get pushed onto the Queue

        NOTE: HomePageView.ViewPanel gets created as a new instance each time the summary page is requested
              Hence, a new ViewPanel instance will get created with it's own CollapsibleRefresher
              So new .enqueue()s to this Refresher will load whilst the old one might be dead/dying as de-referenced."""

        @staticmethod
        class MyQueueableRefresher(Runnable):
            def __init__(self, collapsibleRefresherClass):
                # type: (Runnable) -> None
                self.collapsibleRefresherClass = collapsibleRefresherClass

            # noinspection PyMethodMayBeStatic
            def run(self):
                myPrint("DB", "Inside MyQueueableRefresher.... Calling MyCollapsibleRefresher.refreshable.run() Calling Instance:", self.collapsibleRefresherClass)
                self.collapsibleRefresherClass.isPendingRefresh = False
                self.collapsibleRefresherClass.refreshable.run()

        def __init__(self, refreshable):
            # type: (Runnable, bool) -> None
            myPrint("DB", "Initialising MyCollapsibleRefresher.... Instance: %s. Refreshable: %s" %(self, refreshable))
            self.isPendingRefresh = False
            self.refreshable = refreshable
            self.queueableRefresher = MyCollapsibleRefresher.MyQueueableRefresher(self)

        def enqueueRefresh(self):
            myPrint("DB", "Inside MyCollapsibleRefresher (instance: %s).... invokeLater(%s) .." %(self, self.queueableRefresher))
            if self.isPendingRefresh:
                myPrint("DB", "... DISCARDING enqueueRefresh request as one is already pending... Discarded:", self.queueableRefresher)
                return
            myPrint("DB", "... REQUESTING .invokeLater() on:", self.queueableRefresher)
            self.isPendingRefresh = True
            SwingUtilities.invokeLater(self.queueableRefresher)


    class ShowConsoleRunnable(Runnable):

        def __init__(self): pass

        def run(self):      ConsoleWindow.showConsoleWindow(GlobalVars.CONTEXT.getUI())


    def isSwingComponentValid(swComponent): return not isSwingComponentInvalid(swComponent)

    def isSwingComponentInvalid(swComponent):
        return (swComponent is None
                or not swComponent.isVisible() or not swComponent.isValid() or not swComponent.isDisplayable()
                or SwingUtilities.getWindowAncestor(swComponent) is None)

    class BlinkSwingTimer(SwingTimer, ActionListener):
        ALL_BLINKERS = []
        blinker_LOCK = threading.Lock()

        @staticmethod
        def stopAllBlinkers():
            myPrint("DB", "BlinkSwingTimer.stopAllBlinkers() called....")
            with BlinkSwingTimer.blinker_LOCK:
                for i in range(0, len(BlinkSwingTimer.ALL_BLINKERS)):
                    blinker = BlinkSwingTimer.ALL_BLINKERS[i]
                    try:
                        blinker.stop()
                        myPrint("DB", "... stopped blinker: id: %s" %(blinker.uuid))
                    except:
                        myPrint("DB", ">> ERROR stopping blinker: id: %s" %(blinker.uuid))
                del BlinkSwingTimer.ALL_BLINKERS[:]

        def __init__(self, timeMS, swComponents, flipColor=None, flipBold=False):
            with BlinkSwingTimer.blinker_LOCK:
                self.uuid = UUID.randomUUID().toString()
                self.isForeground = True
                self.countBlinkLoops = 0

                if isinstance(swComponents, JComponent):
                    swComponents = [swComponents]
                elif not isinstance(swComponents, list) or len(swComponents) < 1:
                    return

                self.swComponents = []
                for swComponent in swComponents:
                    font = swComponent.getFont()
                    self.swComponents.append([swComponent,
                                              swComponent.getForeground(),
                                              swComponent.getBackground() if (flipColor is None) else flipColor,
                                              font.deriveFont(font.getStyle() | Font.BOLD) if (flipBold) else font,
                                              font.deriveFont(font.getStyle() & ~Font.BOLD) if (flipBold) else font
                                              ])
                super(self.__class__, self).__init__(max(timeMS, 1200), None)   # Less than 1000ms will prevent whole application from closing when requested...
                if self.getInitialDelay() > 0: self.setInitialDelay(int(self.getInitialDelay()/2))
                self.addActionListener(self)
                BlinkSwingTimer.ALL_BLINKERS.append(self)
                myPrint("DB", "Blinker initiated - id: %s; with %s components" %(self.uuid, len(swComponents)))

        def actionPerformed(self, event):                                                                               # noqa
            try:
                with BlinkSwingTimer.blinker_LOCK:
                    for i in range(0, len(self.swComponents)):
                        swComponent = self.swComponents[i][0]
                        if isSwingComponentInvalid(swComponent):
                            myPrint("DB", ">>> Shutting down blinker (id: %s) as component index: %s no longer available" %(self.uuid, i))
                            self.stop()
                            BlinkSwingTimer.ALL_BLINKERS.remove(self)
                            return

                    for i in range(0, len(self.swComponents)):
                        swComponent = self.swComponents[i][0]
                        fg = self.swComponents[i][1]
                        bg = self.swComponents[i][2]
                        boldON = self.swComponents[i][3]
                        boldOFF = self.swComponents[i][4]
                        swComponent.setForeground(fg if self.isForeground else bg)
                        swComponent.setFont(boldON if self.isForeground else boldOFF)

                    self.countBlinkLoops += 1
                    self.isForeground = not self.isForeground
                    if self.countBlinkLoops % 100 == 0:
                        myPrint("DB", "** Blinker (id: %s), has now iterated %s blink loops" %(self.uuid, self.countBlinkLoops))

            except: pass

    def hideUnideCollapsiblePanels(startingComponent, lSetVisible):
        # type: (JComponent, bool) -> None

        # if isinstance(startingComponent, JPanel) and startingComponent.getClientProperty("%s.collapsible" %(myModuleID)) is not None:
        if isinstance(startingComponent, JComponent) and startingComponent.getClientProperty("%s.collapsible" %(myModuleID)) == "true":
            startingComponent.setVisible(lSetVisible)

        for subComp in startingComponent.getComponents():
            hideUnideCollapsiblePanels(subComp, lSetVisible=lSetVisible)

    ####################################################################################################################

    myPrint("B", "HomePageView widget / extension is now running...")

    class NetAccountBalancesExtension(FeatureModule, PreferencesListener):

        NAB = None

        @staticmethod
        def getNAB():
            if NetAccountBalancesExtension.NAB is not None: return NetAccountBalancesExtension.NAB
            with GlobalVars.EXTENSION_LOCK:
                myPrint("DB", "Creating and returning a new single instance of NetAccountBalancesExtension() using a lock....")
                NetAccountBalancesExtension.NAB = NetAccountBalancesExtension()
            return NetAccountBalancesExtension.NAB

        def __init__(self):  # This is the class' own initialise, just to set up variables
            self.myModuleID = myModuleID

            myPrint("B", "\n##########################################################################################")
            myPrint("B", "Extension: %s:%s (HomePageView widget) initialising...." %(self.myModuleID, GlobalVars.DEFAULT_WIDGET_DISPLAY_NAME))
            myPrint("B", "##########################################################################################\n")

            if GlobalVars.specialDebug: myPrint("B", "@@ SPECIAL DEBUG enabled")

            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

            self.NAB_LOCK = threading.Lock()

            self.moneydanceContext = MD_REF
            self.moneydanceExtensionObject = None

            self.decimal = None
            self.comma = None
            self.themeID = None

            if float(self.moneydanceContext.getBuild()) >= 3051:
                self.moneydanceExtensionLoader = moneydance_extension_loader  # This is the class loader for the whole extension
                myPrint("DB", "... Build is >= 3051 so using moneydance_extension_loader: %s" %(self.moneydanceExtensionLoader))
            else:
                self.moneydanceExtensionLoader = None

            self.alreadyClosed = False
            self.configSaved = True

            self.migratedParameters = False
            self.warningInParametersDetected = False
            self.warningInParametersDetectedType = False
            self.warningInParametersDetectedInRow = None
            self.parallelBalanceTableOperating = False

            self.parametersLoaded = False
            self.listenersActive = False

            self.myCounter = 0
            self.theFrame = None
            self.isUIavailable = False
            self.saveMyHomePageView = None
            self.helpFile = "<NONE>"

            self.saveActionListener = None

            self.quickSearchField = None

            self.savedAccountListUUIDs          = None
            self.savedBalanceType               = None
            self.savedAutoSumAccounts           = None
            self.savedWidgetName                = None
            self.savedCurrencyTable             = None      # Only contains UUID strings
            self.savedDisableCurrencyFormatting = None
            self.savedIncludeInactive           = None
            self.savedIncomeExpenseDateRange    = None
            self.savedCustomDatesTable          = None
            self.savedRowSeparatorTable         = None
            self.savedBlinkTable                = None
            self.savedShowWarningsTable         = None
            self.savedHideRowWhenXXXTable       = None
            self.savedHideRowXValueTable        = None
            self.savedDisplayAverageTable       = None

            self.savedAutoSumDefault            = None
            self.savedDisableWidgetTitle        = None
            self.savedShowDashesInsteadOfZeros  = None
            self.savedTreatSecZeroBalInactive   = None

            self.savedUseIndianNumberFormat     = None
            self.savedHideDecimals              = None
            self.savedDisplayVisualUnderDots    = None

            self.savedExpandedView              = None

            self.isPreview = None

            self.menuItemDEBUG = None
            self.menuItemAutoSumDefault = None
            self.menuItemDisableWidgetTitle = None
            self.menuItemShowDashesInsteadOfZeros = None
            self.menuItemTreatSecZeroBalInactive = None
            self.menuItemUseIndianNumberFormat = None

            self.menuBarItemHideControlPanel_CB = None
            self.savedHideControlPanel = False

            self.mainMenuBar = None

            self.configPanelOpen = False

            self.jlst                               = None
            self.balanceType_COMBO                  = None
            self.incomeExpenseDateRange_COMBO       = None
            self.currency_COMBO                     = None                  # Contains a Class holding Currency Objects
            self.disableCurrencyFormatting_CB       = None
            self.widgetNameField_JTF                = None
            self.separatorSelectorNone_JRB          = None
            self.separatorSelectorAbove_JRB         = None
            self.separatorSelectorBelow_JRB         = None
            self.separatorSelectorBoth_JRB          = None
            self.includeInactive_COMBO              = None
            self.autoSumAccounts_CB                 = None
            self.showWarnings_CB                    = None
            self.hideRowWhenNever_JRB               = None
            self.hideRowWhenAlways_JRB              = None
            self.hideRowWhenZeroOrX_JRB             = None
            self.hideRowWhenLtEqZeroOrX_JRB         = None
            self.hideRowWhenGrEqZeroOrX_JRB         = None
            self.hideRowWhenNotZeroOrX_JRB          = None
            self.hideRowXValue_JRF                  = None
            self.displayAverage_JRF                 = None
            self.blinkRow_CB                        = None
            self.filterOutZeroBalAccts_INACTIVE_CB  = None
            self.filterOutZeroBalAccts_ACTIVE_CB    = None
            self.filterIncludeSelected_CB           = None
            self.filterOnlyShowSelected_CB          = None
            self.filterOnlyAccountType_COMBO        = None

            self.keyLabel = None
            self.dateRangeLabel = None
            self.parallelBalancesWarningLabel = None

            self.rowSelectedSaved = 0
            self.rowSelected_COMBO = None

            self.simulateTotal_label = None
            self.warning_label = None

            self.switchFromHomeScreen = False

            self.rememberLastResultsTable = None

            self.swingWorkers_LOCK = threading.Lock()
            with self.swingWorkers_LOCK:
                self.swingWorkers = []


            myPrint("DB", "Exiting ", inspect.currentframe().f_code.co_name, "()")
            myPrint("DB", "##########################################################################################")

        def initialize(self, extension_context, extension_object):  # This is called by Moneydance after the run-time extension self installs itself
            myPrint("DB", "##########################################################################################")
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

            # These extension_* variables are set by Moneydance before calling this script via the PY Interpreter
            self.moneydanceContext = extension_context  # This is the same as the moneydance variable and com.moneydance.apps.md.controller.Main
            self.moneydanceExtensionObject = extension_object  # This is com.moneydance.apps.md.controller.PythonExtension

            if debug:
                myPrint("DB", "meta_info.dict 'id' = %s" %(self.moneydanceExtensionObject.getIDStr()))
                myPrint("DB", "meta_info.dict 'module_build' = %s" %(self.moneydanceExtensionObject.getBuild()))
                myPrint("DB", "meta_info.dict 'desc' = %s" %(self.moneydanceExtensionObject.getDescription()))
                myPrint("DB", "script path: %s" %(self.moneydanceExtensionObject.getSourceFile()))

            self.preferencesUpdated()
            self.moneydanceContext.getPreferences().addListener(self)

            self.moneydanceContext.registerFeature(extension_object, "%s:customevent:showConfig" %(self.myModuleID), None, GlobalVars.DEFAULT_WIDGET_DISPLAY_NAME.title())
            myPrint("DB", "@@ Registered self as an Extension onto the Extension Menu @@")

            self.saveMyHomePageView = MyHomePageView.getHPV()

            if self.getMoneydanceUI():         # Only do this if the UI is loaded and dataset loaded...
                myPrint("B", "@@ Assuming an extension reinstall...")

                myPrint("B", "...Checking Home Screen Display Order Layout (lefties/righties/unused)")
                self.configureLeftiesRightiesAtInstall(self.saveMyHomePageView.getID(), GlobalVars.Strings.LEGACYID)

                myPrint("B", "...Selecting Home Screen (on all main frames) in preparation to receive new widget....")
                selectAllHomeScreens()
                self.load_saved_parameters()

            else:
                # Runtime install... Let's just check we are visible.....
                self.configureLeftiesRightiesAtRuntime(self.saveMyHomePageView.getID())

            self.moneydanceContext.registerHomePageView(extension_object, self.saveMyHomePageView)
            myPrint("DB", "@@ Registered extension_object as containing a Home Page View (Summary Page / Dashboard object) @@")

            # If the UI is loaded, then probably a re-install... Refresh the UI with a new window....
            if self.getMoneydanceUI():         # Only do this if the UI is loaded and dataset loaded...
                myPrint("B", "@@ Assuming an extension reinstall. Reloading the Dashboard to refresh the view....")
                # moneydance_ui.selectAccountNewWindow(self.moneydanceContext.getCurrentAccountBook().getRootAccount())
                fireMDPreferencesUpdated()

            myPrint("DB", "Exiting ", inspect.currentframe().f_code.co_name, "()")
            myPrint("DB", "##########################################################################################")

        ################################################################################################################
        def areSwingWorkersRunning(self):
            with self.swingWorkers_LOCK: return len(self.swingWorkers) > 0

        def listAllSwingWorkers(self):
            with self.swingWorkers_LOCK:
                if len(self.swingWorkers) < 1:
                    myPrint("DB", "No SwingWorkers found...")
                else:
                    for sw in self.swingWorkers:                                                                        # type: SwingWorker
                        myPrint("DB", "... Found SwingWorker:", sw)
                        myPrint("DB", "....... Status - isDone: %s, isCancelled: %s" %(sw.isDone(), sw.isCancelled()))
                    return

        def isWidgetRefreshRunning_NOLOCKFIRST(self):
            for sw in self.swingWorkers:                                                                                # type: SwingWorker
                if sw.isBuildHomePageWidgetSwingWorker():
                    # myPrint("DB", "isWidgetRefreshRunning() reports TRUE on SwingWorker:", sw)
                    return True
            # myPrint("DB", "isSimulateRunning() reports False")
            return False

        def isWidgetRefreshRunning_LOCKFIRST(self):
            with self.swingWorkers_LOCK: return self.isWidgetRefreshRunning_NOLOCKFIRST()

        def isSimulateRunning_NOLOCKFIRST(self):
            for sw in self.swingWorkers:                                                                                # type: SwingWorker
                if sw.isSimulateTotalForRowSwingWorker():
                    # myPrint("DB", "isSimulateRunning() reports TRUE on SwingWorker:", sw)
                    return True
            # myPrint("DB", "isSimulateRunning() reports False")
            return False

        def isSimulateRunning_LOCKFIRST(self):
            with self.swingWorkers_LOCK: return self.isSimulateRunning_NOLOCKFIRST()

        def isParallelRebuildRunning_NOLOCKFIRST(self):
            for sw in self.swingWorkers:                                                                                # type: SwingWorker
                if sw.isRebuildParallelBalanceTableSwingWorker():
                    # myPrint("DB", "isParallelRebuildRunning() reports TRUE on SwingWorker:", sw)
                    return True
            # myPrint("DB", "isParallelRebuildRunning() reports False")
            return False

        def isParallelRebuildRunning_LOCKFIRST(self):
            with self.swingWorkers_LOCK: return self.isParallelRebuildRunning_NOLOCKFIRST()

        def cancelSwingWorkers(self, lSimulates=False, lParallelRebuilds=False, lBuildHomePageWidgets=False):
            lCancelledAny = False
            for sw in self.swingWorkers:                                                                                # type: SwingWorker
                if ((lSimulates and sw.isSimulateTotalForRowSwingWorker())
                        or (lParallelRebuilds and sw.isRebuildParallelBalanceTableSwingWorker())
                        or (lBuildHomePageWidgets and sw.isBuildHomePageWidgetSwingWorker())):
                    if not sw.isCancelled() and not sw.isDone():
                        myPrint("`DB", "cancelSwingWorkers() sending CANCEL COMMAND to running SwingWorker:", sw)
                        if not sw.cancel(True):
                            myPrint("`DB", " @@ ALERT - SwingWorker.cancel(True) failed >> Moving on.....:", sw)
                        else:
                            lCancelledAny = True
                    else:
                        myPrint("DB", "cancelSwingWorkers() skipping cancellation of SwingWorker as isDone: %s isCancelled: %s ... SW:" %(sw.isDone(), sw.isCancelled()), sw)

            if not lCancelledAny: myPrint("DB", "cancelSwingWorkers() no SwingWorker(s) to cancel....")
            return lCancelledAny
        ################################################################################################################


        def preferencesUpdated(self):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))

            NAB = NetAccountBalancesExtension.getNAB()                                                                  # noqa
            prefs = self.moneydanceContext.getPreferences()

            self.decimal = prefs.getDecimalChar()
            self.comma = "." if self.decimal == "," else ","
            myPrint("DB", ".. Decimal set to '%s', Comma set to '%s'" %(self.decimal, self.comma))

            newThemeID = prefs.getSetting("gui.current_theme", ThemeInfo.DEFAULT_THEME_ID)
            if self.themeID and self.themeID != newThemeID:
                myPrint("DB", ".. >> Detected Preferences ThemeID change from '%s' to '%s'" %(self.themeID, newThemeID))
                myPrint("DB", ".. >> Moneydance have already called 'SwingUtilities.updateComponentTreeUI()' on all frames including mine....")

                # if self.theFrame is not None and self.isUIavailable:
                #
                #     class UpdateCTUIRunnable(Runnable):
                #         def __init__(self): pass
                #
                #         def run(self):
                #             myPrint("DB", "Inside UpdateCTUIRunnable() - about to call SwingUtilities.updateComponentTreeUI() to update my LaF")
                #
                #             myPrint("DB", "UIManager reports laf: '%s' : '%s'" %(UIManager.getLookAndFeel(), UIManager.getLookAndFeel().getName()))
                #
                #             if True:
                #                 myPrint("DB", "Update to own LaF (due to Preferences change) disabled... Please just restart the Extension/MD to refresh after Theme update")
                #             else:
                #                 for _c in self.getAllComponents(NAB.theFrame):                                        # noqa
                #                     myPrint("DB", ".. Calling updateUI() on: " %(_c.panel_name))                      # noqa
                #                     _c.update()                                                                       # noqa
                #                 SwingUtilities.updateComponentTreeUI(NAB.theFrame)                                    # noqa
                #
                #         def getAllComponents(self, c):
                #             compList = []
                #             for comp in c.getComponents():
                #                 myPrint("DB", ".. iterating comp:", comp)
                #                 if isinstance(comp, (MyJPanel)):
                #                     compList.append(comp)
                #                     for cc in self.getAllComponents(comp):
                #                         if isinstance(cc, MyJPanel): compList.append(cc)
                #             return compList
                #
                #     SwingUtilities.invokeLater(UpdateCTUIRunnable())
                # else:
                #     myPrint("DB", "Cannot update my LaF as my Frame is '%s' and the MD GUI isAvailable is '%s'" %(self.theFrame, self.isUIavailable))

            else:
                myPrint("DB", ".. Preferences ThemeID is set to: '%s' (no change)" %(newThemeID))
            self.themeID = newThemeID
            del prefs

        class SaveSettingsRunnable(Runnable):
            def __init__(self): pass

            def run(self):
                NAB = NetAccountBalancesExtension.getNAB()
                NAB.saveSettings(lFromHomeScreen=True)

        def saveSettings(self, lFromHomeScreen=False):
            global debug        # Need this here as we set it below

            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))

            myPrint("B", "SAVINGS PARAMETERS HomePageView widget back to disk..")

            NAB = NetAccountBalancesExtension.getNAB()

            NAB.validateIncExpDateOptions()
            NAB.dumpSavedOptions()

            NAB.migratedParameters = False
            GlobalVars.extn_param_NEW_listAccountUUIDs_NAB          = NAB.savedAccountListUUIDs
            GlobalVars.extn_param_NEW_balanceType_NAB               = NAB.savedBalanceType
            GlobalVars.extn_param_NEW_incomeExpenseDateRange_NAB    = NAB.savedIncomeExpenseDateRange
            GlobalVars.extn_param_NEW_customDatesTable_NAB          = NAB.savedCustomDatesTable
            GlobalVars.extn_param_NEW_rowSeparatorTable_NAB         = NAB.savedRowSeparatorTable
            GlobalVars.extn_param_NEW_blinkTable_NAB                = NAB.savedBlinkTable
            GlobalVars.extn_param_NEW_autoSumAccounts_NAB           = NAB.savedAutoSumAccounts
            GlobalVars.extn_param_NEW_includeInactive_NAB           = NAB.savedIncludeInactive
            GlobalVars.extn_param_NEW_widget_display_name_NAB       = NAB.savedWidgetName
            GlobalVars.extn_param_NEW_currency_NAB                  = NAB.savedCurrencyTable
            GlobalVars.extn_param_NEW_disableCurrencyFormatting_NAB = NAB.savedDisableCurrencyFormatting
            GlobalVars.extn_param_NEW_showWarningsTable_NAB         = NAB.savedShowWarningsTable
            GlobalVars.extn_param_NEW_hideRowWhenXXXTable_NAB       = NAB.savedHideRowWhenXXXTable
            GlobalVars.extn_param_NEW_hideRowXValueTable_NAB        = NAB.savedHideRowXValueTable
            GlobalVars.extn_param_NEW_displayAverageTable_NAB       = NAB.savedDisplayAverageTable

            GlobalVars.extn_param_NEW_autoSumDefault_NAB            = NAB.savedAutoSumDefault
            GlobalVars.extn_param_NEW_disableWidgetTitle_NAB        = NAB.savedDisableWidgetTitle
            GlobalVars.extn_param_NEW_showDashesInsteadOfZeros_NAB  = NAB.savedShowDashesInsteadOfZeros
            GlobalVars.extn_param_NEW_treatSecZeroBalInactive_NAB   = NAB.savedTreatSecZeroBalInactive

            GlobalVars.extn_param_NEW_useIndianNumberFormat_NAB     = NAB.savedUseIndianNumberFormat
            GlobalVars.extn_param_NEW_hideDecimals_NAB              = NAB.savedHideDecimals
            GlobalVars.extn_param_NEW_displayVisualUnderDots_NAB    = NAB.savedDisplayVisualUnderDots

            GlobalVars.extn_param_NEW_expandedView_NAB              = NAB.savedExpandedView

            try:
                # Preventing debug ON from being saved... Stops users leaving 'expensive' debug logging on

                saveDebug = debug
                myPrint("DB", "@@ ALERT: I am saving debug OFF to parameters file so that debugging will not be enabled at next load (prevents long console debug logs)")
                debug = False

                save_StuWareSoftSystems_parameters_to_file(myFile="%s_extension.dict" %(NAB.myModuleID))

                debug = saveDebug

            except:
                myPrint("B", "@@ Error saving parameters back to pickle file....?")
                dump_sys_error_to_md_console_and_errorlog()

            NAB.configSaved = True
            if lFromHomeScreen:
                MyHomePageView.getHPV().lastRefreshTriggerWasAccountModified = False
                NAB.executeRefresh()

        def getSudoAccountFromParallel(self, acctObj, rowIndex):
            ## type: (StoreAccountList, int) -> [Account, HoldBalance]

            NAB = NetAccountBalancesExtension.getNAB()
            if (isIncomeExpenseAcct(acctObj.getAccount()) and not isIncomeExpenseAllDatesSelected(rowIndex)):
                sudoAcctRef = NAB.jlst.parallelAccountBalances[rowIndex][acctObj.getAccount()]                          # type: HoldBalance
            else:
                sudoAcctRef = acctObj.getAccount()                                                                      # type: Account
            return sudoAcctRef

        def searchFiltersUpdated(self):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            self.filterModel(self.jlst.getModel(), self.quickSearchField.getText().strip())                             # noqa

        def filterModel(self, _model, _filterText):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))

            NAB = NetAccountBalancesExtension.getNAB()

            myPrint("DB", "...filter: %s" %(_filterText))

            row = NAB.getSelectedRowIndex()

            filteredListAccounts = []

            for obj in self.jlst.originalListObjects:

                sudoAccount = self.getSudoAccountFromParallel(obj, NAB.getSelectedRowIndex())
                if (self.filterOnlyShowSelected_CB.isSelected()
                        and obj not in NAB.jlst.listOfSelectedObjects):
                    continue

                lAllAccountTypes = NAB.filterOnlyAccountType_COMBO.getSelectedItem() == "All Account Types"
                selectedAccountType = NAB.filterOnlyAccountType_COMBO.getSelectedItem()

                if (not self.savedIncludeInactive[row]
                        and not isAccountActive(obj.getAccount(), self.savedBalanceType[row])):
                    if not self.filterIncludeSelected_CB.isSelected() or obj not in NAB.jlst.listOfSelectedObjects:
                        continue

                if (_filterText.lower() not in obj.getAccount().getFullAccountName().lower()):
                    if not self.filterIncludeSelected_CB.isSelected() or obj not in NAB.jlst.listOfSelectedObjects:
                        continue

                if (self.filterOutZeroBalAccts_INACTIVE_CB.isSelected()
                        and not isAccountActive(obj.getAccount(), NAB.savedBalanceType[row])
                        and StoreAccountList.getRecursiveXBalance(NAB.savedBalanceType[row], sudoAccount) == 0):
                    if not self.filterIncludeSelected_CB.isSelected() or obj not in NAB.jlst.listOfSelectedObjects:
                        continue

                if (self.filterOutZeroBalAccts_ACTIVE_CB.isSelected()
                        and isAccountActive(obj.getAccount(), NAB.savedBalanceType[row])
                        and StoreAccountList.getRecursiveXBalance(NAB.savedBalanceType[row], sudoAccount) == 0):
                    if not self.filterIncludeSelected_CB.isSelected() or obj not in NAB.jlst.listOfSelectedObjects:
                        continue

                if not lAllAccountTypes and obj.getAccount().getAccountType() != selectedAccountType:
                    if not self.filterIncludeSelected_CB.isSelected() or obj not in NAB.jlst.listOfSelectedObjects:
                        continue

                # myPrint("DB", "... adding %s to filtered list" %(obj.getAccount().getFullAccountName()))
                filteredListAccounts.append(obj)

            self.setJListDataAndSelection(filteredListAccounts, lFilter=True)

        def resetQuickSearch(self):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            self.quickSearchField.setText("")                                                                           # noqa
            self.quickSearchField.setCaretPosition(0)                                                                   # noqa
            self.quickSearchField.repaint()                                                                             # noqa

        def configureLeftiesRightiesAtRuntime(self, widgetID):

            KEY_LEFTIES = "gui.home.lefties"
            KEY_RIGHTIES = "gui.home.righties"
            KEY_UNUSED = "gui.home.unused"

            prefs = self.moneydanceContext.getPreferences()

            lefties = prefs.getVectorSetting(KEY_LEFTIES, StreamVector())
            righties = prefs.getVectorSetting(KEY_RIGHTIES, StreamVector())
            unused = prefs.getVectorSetting(KEY_UNUSED, StreamVector())

            iCount = 0
            myPrint("DB", "Confirming WidgetID: %s exists in Summary Page layout (somewhere)" %(widgetID))
            for where_key, where in [[KEY_LEFTIES, lefties], [KEY_RIGHTIES, righties], [KEY_UNUSED, unused]]:
                for iIndex in range(0, where.size()):
                    theID = where.elementAt(iIndex)
                    if theID == widgetID:
                        myPrint("DB", ".. WidgetID: '%s' found in '%s' on row: %s" %(theID, where_key, iIndex+1))
                        iCount += 1

            if iCount > 0:
                myPrint("DB", "Found WidgetID: %s in Summary Page layout - so doing nothing..." %(widgetID))
                return

            myPrint("B", ".. Widget: '%s'... Adding to first position in '%s' (Summary Page top left)"  %(widgetID, KEY_LEFTIES))
            lefties.insertElementAt(widgetID, 0)

            prefs.setSetting(KEY_LEFTIES, lefties)

        def configureLeftiesRightiesAtInstall(self, widgetID, legacyID):

            KEY_LEFTIES = "gui.home.lefties"
            KEY_RIGHTIES = "gui.home.righties"
            KEY_UNUSED = "gui.home.unused"

            prefs = self.moneydanceContext.getPreferences()

            lefties = prefs.getVectorSetting(KEY_LEFTIES, StreamVector())
            righties = prefs.getVectorSetting(KEY_RIGHTIES, StreamVector())
            unused = prefs.getVectorSetting(KEY_UNUSED, StreamVector())

            for where_key, where in [[KEY_LEFTIES, lefties], [KEY_RIGHTIES, righties], [KEY_UNUSED, unused]]:
                myPrint("DB", "%s '%s': %s" %("Starting...", where_key, where))

            # Remove from unused as presumably user wants to install and use...
            for theID in [widgetID, legacyID]:
                while theID in unused:
                    myPrint("DB", ".. Removing WidgetID: '%s' from '%s' layout area"  %(theID, KEY_UNUSED))
                    unused.remove(theID)

            # Remove duplicates...
            for where_key, where in [[KEY_LEFTIES, lefties], [KEY_RIGHTIES, righties]]:
                for theID in [widgetID, legacyID]:
                    while where.lastIndexOf(theID) > where.indexOf(theID):
                        myPrint("DB", ".. Removing duplicated WidgetID: '%s' from '%s' layout area (row: %s)"
                                %(theID, where_key, where.lastIndexOf(theID)+1))
                        where.removeElementAt(where.lastIndexOf(theID))

            # Check we don't have both new and legacy IDs...
            for where_key, where in [[KEY_LEFTIES, lefties], [KEY_RIGHTIES, righties]]:
                if widgetID in where and legacyID in where:
                    while legacyID in where:
                        myPrint("DB", ".. Removing WidgetID: '%s' from '%s' layout area as WidgetID: '%s' already exists"
                                %(legacyID, where_key, widgetID))
                        where.remove(legacyID)

            # Migrate old ID to latest ID in layout....
            for where_key, where in [[KEY_LEFTIES, lefties], [KEY_RIGHTIES, righties]]:
                if legacyID in where:
                    myPrint("DB", ".. Legacy WidgetID: '%s' found in '%s'.. Migrating to latestID ('%s') in layout (row: %s)"
                            %(legacyID, where_key, widgetID, where.lastIndexOf(legacyID)+1))
                    where.insertElementAt(widgetID, where.indexOf(legacyID))
                    where.remove(legacyID)

            # Make sure not in lefties and righties...
            if widgetID in lefties:

                while widgetID in righties:
                    myPrint("DB", ".. Removing WidgetID: '%s' from '%s' layout area as already in '%s'"  %(widgetID, KEY_RIGHTIES, KEY_LEFTIES))
                    righties.remove(widgetID)

                myPrint("DB", ".. Widget: '%s' configured in '%s'... Will not change Layout any further"  %(widgetID, KEY_LEFTIES))

            if widgetID in righties:

                if righties[-1] != widgetID:
                    myPrint("DB", ".. Widget: '%s' already configured in '%s' (not last)... Will not change Layout further"  %(widgetID, KEY_RIGHTIES))
                else:
                    myPrint("DB", ".. Widget: '%s'... Will remove from last position in '%s' (Summary Page bottom right)"  %(widgetID, KEY_RIGHTIES))
                    righties.remove(widgetID)

            if widgetID not in lefties and widgetID not in righties:
                myPrint("B", ".. Widget: '%s'... Adding to first position in '%s' (Summary Page top left)"  %(widgetID, KEY_LEFTIES))
                lefties.insertElementAt(widgetID, 0)

            prefs.setSetting(KEY_LEFTIES,   lefties)
            prefs.setSetting(KEY_RIGHTIES,  righties)
            prefs.setSetting(KEY_UNUSED,    unused)

            for where_key, where in [[KEY_LEFTIES, lefties], [KEY_RIGHTIES, righties], [KEY_UNUSED, unused]]:
                myPrint("DB", "%s '%s': %s" %("Ending...", where_key, where))


        class CloseAction(AbstractAction):

            def __init__(self, theFrame):
                self.theFrame = theFrame

            def actionPerformed(self, event):                                                                           # noqa

                myPrint("DB", "In %s.%s() - Event: %s" %(self, inspect.currentframe().f_code.co_name, event))
                myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
                myPrint("DB", ".. main application frame being disposed (will shut down application)....")

                myPrint("DB", "action = %s" %(event.getActionCommand()))

                # Listeners are already on the Swing EDT
                self.theFrame.dispose()  # Should call WindowListener; windowClosed()

        class HideAction(AbstractAction):

            def __init__(self, theFrame):
                self.theFrame = theFrame

            def actionPerformed(self, event):                                                                           # noqa

                myPrint("DB", "In %s.%s() - Event: %s" %(self, inspect.currentframe().f_code.co_name, event))
                myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
                myPrint("DB", "Setting MyJFrame to invisible....")

                NetAccountBalancesExtension.getNAB().configPanelOpen = False

                # Listeners are already on the Swing EDT
                self.theFrame.setVisible(False)

        class HelpAction(AbstractAction):

            def __init__(self, theFrame):
                self.theFrame = theFrame

            def actionPerformed(self, event):                                                                           # noqa

                myPrint("DB", "In %s.%s() - Event: %s" %(self, inspect.currentframe().f_code.co_name, event))
                myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

                NAB = NetAccountBalancesExtension.getNAB()
                QuickJFrame("%s:%s - Help" %(NAB.myModuleID, GlobalVars.DEFAULT_WIDGET_DISPLAY_NAME), NAB.helpFile, lWrapText=False, lAutoSize=True).show_the_frame()

        class StoreCurrencyAsText():
            """Stores a Currency Obj as just text components; prevents holding on to the object"""

            def __init__(self, theCurr, baseCurr):
                self.IDString = theCurr.getIDString()
                self.name = theCurr.getName()
                self.UUID = theCurr.getUUID()
                self.isBase = (theCurr is baseCurr)
                self.isCurr = theCurr.getCurrencyType() == CurrencyType.Type.CURRENCY                                   # noqa

            def getIDString(self): return self.IDString

            def getName(self): return self.name

            def getUUID(self): return self.UUID

            def __str__(self):
                return "%s: %s (%s)" %(("C" if self.isCurr else "S"),self.getName(), self.getIDString())

            def __repr__(self): return self.__str__()

        def widgetRowDefault(self):                 return GlobalVars.DEFAULT_WIDGET_ROW_NOT_CONFIGURED
        def accountListDefault(self):               return []
        def currencyDefault(self):                  return None
        def disableCurrencyFormattingDefault(self): return False
        def balanceDefault(self):                   return 0
        def incomeExpenseDateRangeDefault(self):    return DateRangeOption.DR_ALL_DATES.getResourceKey()
        def customDatesDefault(self):               return [0, 0]
        def rowSeparatorDefault(self):              return GlobalVars.ROW_SEPARATOR_NEVER
        def blinkDefault(self):                     return False
        def includeInactiveDefault(self):           return 0
        def autoSumDefault(self):                   return (False if self.savedAutoSumDefault is None else self.savedAutoSumDefault)
        def showWarningsDefault(self):              return True
        def disableRowDefault(self):                return False
        def hideRowWhenXXXDefault(self):            return GlobalVars.HIDE_ROW_WHEN_NEVER
        def hideRowXValueDefault(self):             return 0.0
        def displayAverageDefault(self):            return 1.0
        def disableWidgetTitleDefault(self):        return False
        def showDashesInsteadOfZerosDefault(self):  return False
        def treatSecZeroBalInactiveDefault(self):   return False
        def useIndianNumberFormatDefault(self):     return False
        def hideDecimalsDefault(self):              return False
        def displayVisualUnderDotsDefault(self):    return False
        def expandedViewDefault(self):              return True

        # noinspection PyUnusedLocal
        def validateParameters(self):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))

            # New parameter - pre-populate with default (None = Base)
            if self.savedCurrencyTable == [self.currencyDefault()] and len(self.savedCurrencyTable) != self.getNumberOfRows():
                self.savedCurrencyTable = [self.currencyDefault() for i in range(0,self.getNumberOfRows())]             # Don't just do [] * n (as you will get references to same list)
                myPrint("B", "New parameter savedCurrencyTable detected, pre-populating with %s (= base currency)" %(self.savedCurrencyTable))

            # New parameter - pre-populate with default (0 = Active)
            if self.savedDisableCurrencyFormatting == [self.disableCurrencyFormattingDefault()] and len(self.savedDisableCurrencyFormatting) != self.getNumberOfRows():
                self.savedDisableCurrencyFormatting = [self.disableCurrencyFormattingDefault() for i in range(0,self.getNumberOfRows())]      # Don't just do [] * n (as you will get references to same list)
                myPrint("B", "New parameter savedDisableCurrencyFormatting detected, pre-populating with %s (= Normal Currency Formatting)" %(self.savedDisableCurrencyFormatting))

            # New parameter - pre-populate with default (0 = Active)
            if self.savedIncludeInactive == [self.includeInactiveDefault()] and len(self.savedIncludeInactive) != self.getNumberOfRows():
                self.savedIncludeInactive = [self.includeInactiveDefault() for i in range(0,self.getNumberOfRows())]    # Don't just do [] * n (as you will get references to same list)
                myPrint("B", "New parameter savedIncludeInactive detected, pre-populating with %s (= Active items only)" %(self.savedIncludeInactive))

            # New parameter - pre-populate with default
            if self.savedAutoSumAccounts == [self.autoSumDefault()] and len(self.savedAutoSumAccounts) != self.getNumberOfRows():
                self.savedAutoSumAccounts = [self.autoSumDefault() for i in range(0,self.getNumberOfRows())]            # Don't just do [] * n (as you will get references to same list)
                myPrint("B", "New parameter savedAutoSumAccounts detected, pre-populating with %s (= Auto Sum Accounts)" %(self.savedAutoSumAccounts))

            # New parameter - pre-populate with default
            if self.savedIncomeExpenseDateRange == [self.incomeExpenseDateRangeDefault()] and len(self.savedIncomeExpenseDateRange) != self.getNumberOfRows():
                self.savedIncomeExpenseDateRange = [self.incomeExpenseDateRangeDefault() for i in range(0,self.getNumberOfRows())]      # Don't just do [] * n (as you will get references to same list)
                myPrint("B", "New parameter savedIncomeExpenseDateRange detected, pre-populating with %s (= Income/Expense All Dates)" %(self.savedIncomeExpenseDateRange))

            # New parameter - pre-populate with default
            if self.savedCustomDatesTable == [self.customDatesDefault()] and len(self.savedCustomDatesTable) != self.getNumberOfRows():
                self.savedCustomDatesTable = [self.customDatesDefault() for i in range(0,self.getNumberOfRows())]       # Don't just do [] * n (as you will get references to same list)
                myPrint("B", "New parameter savedCustomDatesTable detected, pre-populating with %s (= no custom dates)" %(self.savedCustomDatesTable))

            # New parameter - pre-populate with default
            if self.savedShowWarningsTable == [self.showWarningsDefault()] and len(self.savedShowWarningsTable) != self.getNumberOfRows():
                self.savedShowWarningsTable = [self.showWarningsDefault() for i in range(0,self.getNumberOfRows())]     # Don't just do [] * n (as you will get references to same list)
                myPrint("B", "New parameter savedShowWarningsTable detected, pre-populating with %s (= Default Show Warnings per row)" %(self.savedShowWarningsTable))

            # New parameter - pre-populate with default
            if self.savedHideRowWhenXXXTable == [self.hideRowWhenXXXDefault()] and len(self.savedHideRowWhenXXXTable) != self.getNumberOfRows():
                self.savedHideRowWhenXXXTable = [self.hideRowWhenXXXDefault() for i in range(0,self.getNumberOfRows())]  # Don't just do [] * n (as you will get references to same list)
                myPrint("B", "New parameter savedHideRowWhenXXXTable detected, pre-populating with %s (= Default row not hidden - i.e. it's visible)" %(self.savedHideRowWhenXXXTable))

            # New parameter - pre-populate with default
            if self.savedHideRowXValueTable == [self.hideRowXValueDefault()] and len(self.savedHideRowXValueTable) != self.getNumberOfRows():
                self.savedHideRowXValueTable = [self.hideRowXValueDefault() for i in range(0,self.getNumberOfRows())]  # Don't just do [] * n (as you will get references to same list)
                myPrint("B", "New parameter savedHideRowXValueTable detected, pre-populating with %s (= Default row not hidden x value = 0)" %(self.savedHideRowXValueTable))

            # New parameter - pre-populate with default
            if self.savedDisplayAverageTable == [self.displayAverageDefault()] and len(self.savedDisplayAverageTable) != self.getNumberOfRows():
                self.savedDisplayAverageTable = [self.displayAverageDefault() for i in range(0,self.getNumberOfRows())]  # Don't just do [] * n (as you will get references to same list)
                myPrint("B", "New parameter savedDisplayAverageTable detected, pre-populating with %s (= 1.0 = don't display average)" %(self.savedDisplayAverageTable))

            # New parameter - pre-populate with default
            if self.savedRowSeparatorTable == [self.rowSeparatorDefault()] and len(self.savedRowSeparatorTable) != self.getNumberOfRows():
                self.savedRowSeparatorTable = [self.rowSeparatorDefault() for i in range(0,self.getNumberOfRows())]     # Don't just do [] * n (as you will get references to same list)
                myPrint("B", "New parameter savedRowSeparatorTable detected, pre-populating with %s (= Default no row separators)" %(self.savedRowSeparatorTable))

            # New parameter - pre-populate with default
            if self.savedBlinkTable == [self.blinkDefault()] and len(self.savedBlinkTable) != self.getNumberOfRows():
                self.savedBlinkTable = [self.blinkDefault() for i in range(0,self.getNumberOfRows())]     # Don't just do [] * n (as you will get references to same list)
                myPrint("B", "New parameter savedBlinkTable detected, pre-populating with %s (= Default Blinking OFF)" %(self.savedBlinkTable))

            if self.savedAccountListUUIDs is None or not isinstance(self.savedAccountListUUIDs, list) or self.getNumberOfRows() < 1:
                self.resetParameters(1)
            elif self.savedBalanceType is None or not isinstance(self.savedBalanceType, list) or len(self.savedBalanceType) < 1:
                self.resetParameters(2)
            elif self.savedWidgetName is None or not isinstance(self.savedWidgetName, list) or len(self.savedWidgetName) < 1:
                self.resetParameters(3)
            elif self.savedCurrencyTable is None or not isinstance(self.savedCurrencyTable, list) or len(self.savedCurrencyTable) < 1:
                self.resetParameters(4)
            elif self.savedIncludeInactive is None or not isinstance(self.savedIncludeInactive, list) or len(self.savedIncludeInactive) < 1:
                self.resetParameters(5)
            elif self.savedDisableCurrencyFormatting is None or not isinstance(self.savedDisableCurrencyFormatting, list) or len(self.savedDisableCurrencyFormatting) < 1:
                self.resetParameters(6)
            elif self.savedAutoSumAccounts is None or not isinstance(self.savedAutoSumAccounts, list) or len(self.savedAutoSumAccounts) < 1:
                self.resetParameters(7)
            elif self.savedIncomeExpenseDateRange is None or not isinstance(self.savedIncomeExpenseDateRange, list) or len(self.savedIncomeExpenseDateRange) < 1:
                self.resetParameters(8)
            elif self.savedCustomDatesTable is None or not isinstance(self.savedCustomDatesTable, list) or len(self.savedCustomDatesTable) < 1:
                self.resetParameters(9)
            elif self.savedRowSeparatorTable is None or not isinstance(self.savedRowSeparatorTable, list) or len(self.savedRowSeparatorTable) < 1:
                self.resetParameters(10)
            elif self.savedBlinkTable is None or not isinstance(self.savedBlinkTable, list) or len(self.savedBlinkTable) < 1:
                self.resetParameters(11)
            elif self.savedShowWarningsTable is None or not isinstance(self.savedShowWarningsTable, list) or len(self.savedShowWarningsTable) < 1:
                self.resetParameters(12)
            elif self.savedHideRowWhenXXXTable is None or not isinstance(self.savedHideRowWhenXXXTable, list) or len(self.savedHideRowWhenXXXTable) < 1:
                self.resetParameters(13)
            elif self.savedHideRowXValueTable is None or not isinstance(self.savedHideRowXValueTable, list) or len(self.savedHideRowXValueTable) < 1:
                self.resetParameters(15)
            elif self.savedDisplayAverageTable is None or not isinstance(self.savedDisplayAverageTable, list) or len(self.savedDisplayAverageTable) < 1:
                self.resetParameters(16)
            elif self.savedAutoSumDefault is None or not isinstance(self.savedAutoSumDefault, bool):
                self.resetParameters(17)
            elif self.savedShowDashesInsteadOfZeros is None or not isinstance(self.savedShowDashesInsteadOfZeros, bool):
                self.resetParameters(19)
            elif self.savedDisableWidgetTitle is None or not isinstance(self.savedDisableWidgetTitle, bool):
                self.resetParameters(21)
            elif self.savedTreatSecZeroBalInactive is None or not isinstance(self.savedTreatSecZeroBalInactive, bool):
                self.resetParameters(23)
            elif self.savedUseIndianNumberFormat is None or not isinstance(self.savedUseIndianNumberFormat, bool):
                self.resetParameters(25)
            elif self.savedHideDecimals is None or not isinstance(self.savedHideDecimals, bool):
                self.resetParameters(29)
            elif self.savedDisplayVisualUnderDots is None or not isinstance(self.savedDisplayVisualUnderDots, bool):
                self.resetParameters(30)
            elif self.savedExpandedView is None or not isinstance(self.savedExpandedView, bool):
                self.resetParameters(32)
            elif len(self.savedBalanceType) != self.getNumberOfRows():
                self.resetParameters(35)
            elif len(self.savedWidgetName) != self.getNumberOfRows():
                self.resetParameters(37)
            elif len(self.savedCurrencyTable) != self.getNumberOfRows():
                self.resetParameters(39)
            elif len(self.savedIncludeInactive) != self.getNumberOfRows():
                self.resetParameters(41)
            elif len(self.savedDisableCurrencyFormatting) != self.getNumberOfRows():
                self.resetParameters(43)
            elif len(self.savedAutoSumAccounts) != self.getNumberOfRows():
                self.resetParameters(45)
            elif len(self.savedIncomeExpenseDateRange) != self.getNumberOfRows():
                self.resetParameters(47)
            elif len(self.savedCustomDatesTable) != self.getNumberOfRows():
                self.resetParameters(49)
            elif len(self.savedShowWarningsTable) != self.getNumberOfRows():
                self.resetParameters(51)
            elif len(self.savedRowSeparatorTable) != self.getNumberOfRows():
                self.resetParameters(53)
            elif len(self.savedBlinkTable) != self.getNumberOfRows():
                self.resetParameters(54)
            elif len(self.savedHideRowWhenXXXTable) != self.getNumberOfRows():
                self.resetParameters(55)
            elif len(self.savedHideRowXValueTable) != self.getNumberOfRows():
                self.resetParameters(57)
            elif len(self.savedDisplayAverageTable) != self.getNumberOfRows():
                self.resetParameters(59)
            else:
                for i in range(0, self.getNumberOfRows()):
                    if self.savedAccountListUUIDs[i] is None or not isinstance(self.savedAccountListUUIDs[i], list):
                        myPrint("B", "Resetting parameter '%s' on RowIdx: %s" %("savedAccountListUUIDs", i))
                        self.savedAccountListUUIDs[i] = self.accountListDefault()
                    if self.savedBalanceType[i] is None or not isinstance(self.savedBalanceType[i], int) or self.savedBalanceType[i] < 0 or self.savedBalanceType[i] > 2:
                        myPrint("B", "Resetting parameter '%s' on RowIdx: %s" %("savedBalanceType", i))
                        self.savedBalanceType[i] = self.balanceDefault()
                    if self.savedWidgetName[i] is None or not isinstance(self.savedWidgetName[i], basestring) or self.savedWidgetName[i] == "":
                        myPrint("B", "Resetting parameter '%s' on RowIdx: %s" %("savedWidgetName", i))
                        self.savedWidgetName[i] = self.widgetRowDefault()
                    if self.savedCurrencyTable[i] is not None and (not isinstance(self.savedCurrencyTable[i], basestring) or self.savedCurrencyTable[i] == ""):
                        myPrint("B", "Resetting parameter '%s' on RowIdx: %s" %("savedCurrencyTable", i))
                        self.savedCurrencyTable[i] = self.currencyDefault()                                             # noqa
                    if self.savedIncludeInactive[i] is None or not isinstance(self.savedIncludeInactive[i], int) or self.savedIncludeInactive[i] < 0 or self.savedIncludeInactive[i] > 1:
                        myPrint("B", "Resetting parameter '%s' on RowIdx: %s" %("savedIncludeInactive", i))
                        self.savedIncludeInactive[i] = self.includeInactiveDefault()
                    if self.savedDisableCurrencyFormatting[i] is None or not isinstance(self.savedDisableCurrencyFormatting[i], bool):
                        myPrint("B", "Resetting parameter '%s' on RowIdx: %s" %("savedDisableCurrencyFormatting", i))
                        self.savedDisableCurrencyFormatting[i] = self.disableCurrencyFormattingDefault()
                    if self.savedAutoSumAccounts[i] is None or not isinstance(self.savedAutoSumAccounts[i], bool):
                        myPrint("B", "Resetting parameter '%s' on RowIdx: %s" %("savedAutoSumAccounts", i))
                        self.savedAutoSumAccounts[i] = self.autoSumDefault()
                    if self.savedIncomeExpenseDateRange[i] is None or not isinstance(self.savedIncomeExpenseDateRange[i], basestring) or self.savedIncomeExpenseDateRange[i] == "":
                        myPrint("B", "Resetting parameter '%s' on RowIdx: %s" %("savedIncomeExpenseDateRange", i))
                        self.savedIncomeExpenseDateRange[i] = self.incomeExpenseDateRangeDefault()
                    if self.savedCustomDatesTable[i] is None or not isinstance(self.savedCustomDatesTable[i], list) or len(self.savedCustomDatesTable[i]) != 2:
                        myPrint("B", "Resetting parameter '%s' on RowIdx: %s" %("savedCustomDatesTable", i))
                        self.savedCustomDatesTable[i] = self.customDatesDefault()
                    if self.savedRowSeparatorTable[i] is None or not isinstance(self.savedRowSeparatorTable[i], int) or self.savedRowSeparatorTable[i] < GlobalVars.ROW_SEPARATOR_NEVER or self.savedRowSeparatorTable[i] > GlobalVars.ROW_SEPARATOR_BOTH:
                        myPrint("B", "Resetting parameter '%s' on RowIdx: %s" %("savedRowSeparatorTable", i))
                        self.savedRowSeparatorTable[i] = self.rowSeparatorDefault()
                    if self.savedBlinkTable[i] is None or not isinstance(self.savedBlinkTable[i], bool):
                        myPrint("B", "Resetting parameter '%s' on RowIdx: %s" %("savedBlinkTable", i))
                        self.savedBlinkTable[i] = self.blinkDefault()
                    if not isValidDateRange(self.savedCustomDatesTable[i][0], self.savedCustomDatesTable[i][1]):
                        self.savedCustomDatesTable[i] = self.customDatesDefault()
                    if self.savedShowWarningsTable[i] is None or not isinstance(self.savedShowWarningsTable[i], bool):
                        myPrint("B", "Resetting parameter '%s' on RowIdx: %s" %("savedShowWarningsTable", i))
                        self.savedShowWarningsTable[i] = self.showWarningsDefault()
                    if self.savedHideRowWhenXXXTable[i] is None or not isinstance(self.savedHideRowWhenXXXTable[i], int) or self.savedHideRowWhenXXXTable[i] < GlobalVars.HIDE_ROW_WHEN_NEVER or self.savedHideRowWhenXXXTable[i] > GlobalVars.HIDE_ROW_WHEN_NOT_ZERO_OR_X:
                        myPrint("B", "Resetting parameter '%s' on RowIdx: %s" %("savedHideRowWhenXXXTable", i))
                        self.savedHideRowWhenXXXTable[i] = self.hideRowWhenXXXDefault()
                    if self.savedHideRowXValueTable[i] is None or not isinstance(self.savedHideRowXValueTable[i], float):
                        myPrint("B", "Resetting parameter '%s' on RowIdx: %s" %("savedHideRowXValueTable", i))
                        self.savedHideRowXValueTable[i] = self.hideRowXValueDefault()
                    if self.savedDisplayAverageTable[i] is None or not isinstance(self.savedDisplayAverageTable[i], float) or self.savedDisplayAverageTable[i] == 0.0:
                        myPrint("B", "Resetting parameter '%s' on RowIdx: %s" %("savedHideRowXValueTable", i))
                        self.savedDisplayAverageTable[i] = self.displayAverageDefault()

        def resetParameters(self, iError=None, lJustRowSettings=False):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))

            if iError is None and lJustRowSettings:
                myPrint("B", "Initialising to 1 row with default settings....")
            elif iError is None:
                myPrint("B", "Initialising PARAMETERS....")
            else:
                myPrint("B", "RESET PARAMETERS Called/Triggered (Error code: %s)... Resetting...." %(iError))

            self.savedAccountListUUIDs              = [self.accountListDefault()]
            self.savedBalanceType                   = [self.balanceDefault()]
            self.savedIncomeExpenseDateRange        = [self.incomeExpenseDateRangeDefault()]
            self.savedCustomDatesTable              = [self.customDatesDefault()]
            self.savedRowSeparatorTable             = [self.rowSeparatorDefault()]
            self.savedBlinkTable                    = [self.blinkDefault()]
            self.savedIncludeInactive               = [self.includeInactiveDefault()]
            self.savedAutoSumAccounts               = [self.autoSumDefault()]
            self.savedWidgetName                    = [self.widgetRowDefault()]
            self.savedCurrencyTable                 = [self.currencyDefault()]
            self.savedDisableCurrencyFormatting     = [self.disableCurrencyFormattingDefault()]
            self.savedShowWarningsTable             = [self.showWarningsDefault()]
            self.savedHideRowWhenXXXTable           = [self.hideRowWhenXXXDefault()]
            self.savedHideRowXValueTable            = [self.hideRowXValueDefault()]
            self.savedDisplayAverageTable           = [self.displayAverageDefault()]

            if not lJustRowSettings:
                self.savedAutoSumDefault            = self.autoSumDefault()
                self.savedDisableWidgetTitle        = self.disableWidgetTitleDefault()
                self.savedShowDashesInsteadOfZeros  = self.showDashesInsteadOfZerosDefault()
                self.savedTreatSecZeroBalInactive   = self.treatSecZeroBalInactiveDefault()
                self.savedUseIndianNumberFormat     = self.useIndianNumberFormatDefault()
                self.savedHideDecimals              = self.hideDecimalsDefault()
                self.savedDisplayVisualUnderDots    = self.displayVisualUnderDotsDefault()
                self.savedExpandedView              = self.expandedViewDefault()

            self.setSelectedRowIndex(0)

        def getEndDate(self, _endDate, _balType):
            today = min(DateUtil.getStrippedDateInt(), _endDate)
            return (today if (_balType == GlobalVars.BALTYPE_CURRENTBALANCE) else _endDate)

        def setDateRangeLabel(self, _row):
            NAB = NetAccountBalancesExtension.getNAB()

            myPrint("DB", "about to set date range label..")

            dateFormat = NAB.moneydanceContext.getPreferences().getShortDateFormat()

            dateExtraTxt = ("(up to today's date)" if (NAB.savedBalanceType[_row] == GlobalVars.BALTYPE_CURRENTBALANCE) else "")

            if NAB.savedIncomeExpenseDateRange[_row] != NAB.incomeExpenseDateRangeDefault():
                # dateRange = DateRangeOption.fromKey(NAB.savedIncomeExpenseDateRange[_row]).getDateRange()
                dateRange = getDateRangeSelected(NAB.savedIncomeExpenseDateRange[_row], NAB.savedCustomDatesTable[_row])
                endDate = NAB.getEndDate(dateRange.getEndDateInt(), NAB.savedBalanceType[_row])
                NAB.dateRangeLabel.setText(wrap_HTML_italics("I/E Date Range: %s to %s - Others: All dates %s"
                    %(convertStrippedIntDateFormattedText(dateRange.getStartDateInt(), dateFormat),
                      convertStrippedIntDateFormattedText(endDate, dateFormat), dateExtraTxt)))
                NAB.dateRangeLabel.setHorizontalAlignment(JLabel.LEFT)
                NAB.dateRangeLabel.repaint()
            else:
                NAB.dateRangeLabel.setText(wrap_HTML_italics("Date Range: ALL DATES %s" %(dateExtraTxt)))
                NAB.dateRangeLabel.setHorizontalAlignment(JLabel.LEFT)
                NAB.dateRangeLabel.repaint()

        def setKeyLabel(self, _row):
            NAB = NetAccountBalancesExtension.getNAB()
            myPrint("DB", "about to set key label..")
            if not NAB.savedIncludeInactive[_row]:
                if NAB.keyLabel.getIcon() is None:
                    mdImages = NAB.moneydanceContext.getUI().getImages()
                    iconTintInactive = NAB.moneydanceContext.getUI().colors.errorMessageForeground
                    iconInactive = mdImages.getIconWithColor(MDImages.GRIP_VERTICAL, iconTintInactive)
                    NAB.keyLabel.setIcon(iconInactive)
                NAB.keyLabel.setText(wrap_HTML_small("","WARNING: Total Includes Inactive Children", NAB.moneydanceContext.getUI().colors.defaultTextForeground))
                NAB.keyLabel.setHorizontalAlignment(JLabel.RIGHT)
                NAB.keyLabel.setHorizontalTextPosition(JLabel.LEFT)
                NAB.keyLabel.repaint()
            else:
                NAB.keyLabel.setText("")
                NAB.keyLabel.setIcon(None)
                NAB.keyLabel.repaint()

        def setParallelBalancesWarningLabel(self, _row):
            NAB = NetAccountBalancesExtension.getNAB()
            myPrint("DB", "about to set parallelBalancesWarningLabel..")
            if not isIncomeExpenseAllDatesSelected(_row):
                if NAB.parallelBalancesWarningLabel.getIcon() is None:
                    mdImages = NAB.moneydanceContext.getUI().getImages()
                    iconTintParallel = NAB.moneydanceContext.getUI().colors.errorMessageForeground
                    iconParallel = mdImages.getIconWithColor(GlobalVars.Strings.MD_GLYPH_REFRESH, iconTintParallel)
                    NAB.parallelBalancesWarningLabel.setIcon(iconParallel)
                NAB.parallelBalancesWarningLabel.setText(wrap_HTML_small("","PARALLEL BALANCE TABLE"))
                NAB.parallelBalancesWarningLabel.setHorizontalAlignment(JLabel.LEFT)
                NAB.parallelBalancesWarningLabel.setHorizontalTextPosition(JLabel.RIGHT)
                NAB.parallelBalancesWarningLabel.repaint()
            else:
                NAB.parallelBalancesWarningLabel.setText("")
                NAB.parallelBalancesWarningLabel.setIcon(None)
                NAB.parallelBalancesWarningLabel.repaint()

        class DateRangeSingleOption:

            @staticmethod
            def findAllDates(_list):
                for i in len(_list):
                    if _list[i].getDR() == DateRangeOption.DR_ALL_DATES: return i
                return 0

            def __init__(self, DR):
                # type: (DateRangeOption) -> None
                self.DR = DR

            def getDR(self):        return self.DR
            def __str__(self):      return NetAccountBalancesExtension.getNAB().moneydanceContext.getUI().getStr(self.getDR().getResourceKey())  # noqa
            def __repr__(self):     return self.__str__()                                                               # noqa
            def toString(self):     return self.__str__()                                                               # noqa


        def findDateRange(self, _key):
            tmpList = []
            for i in range(0, self.incomeExpenseDateRange_COMBO.getItemCount()):
                if self.incomeExpenseDateRange_COMBO.getItemAt(i).getDR().getResourceKey() == _key:
                    myPrint("DB", ".. Found & returning Date Range Key: %s at Index: %s" %(_key, i))
                    return i
                tmpList.append(self.incomeExpenseDateRange_COMBO.getItemAt(i))

            myPrint("DB", ".. WARNING: Did not find Date Range Key: %s >> Returning All Dates Key" %(_key))
            return self.DateRangeSingleOption.findAllDates(tmpList)

        def rebuildFrameComponents(self, selectRowIndex=0):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))

            self.setSelectedRowIndex(selectRowIndex)

            allSwingControlObjects = [self.rowSelected_COMBO,
                                      self.balanceType_COMBO,
                                      self.incomeExpenseDateRange_COMBO,
                                      self.currency_COMBO,
                                      self.separatorSelectorNone_JRB,
                                      self.separatorSelectorAbove_JRB,
                                      self.separatorSelectorBelow_JRB,
                                      self.separatorSelectorBoth_JRB,
                                      self.disableCurrencyFormatting_CB,
                                      self.includeInactive_COMBO,
                                      self.filterOutZeroBalAccts_INACTIVE_CB,
                                      self.filterOutZeroBalAccts_ACTIVE_CB,
                                      self.filterIncludeSelected_CB,
                                      self.filterOnlyShowSelected_CB,
                                      self.filterOnlyAccountType_COMBO,
                                      self.showWarnings_CB,
                                      self.hideRowWhenNever_JRB,
                                      self.hideRowWhenAlways_JRB,
                                      self.hideRowWhenZeroOrX_JRB,
                                      self.hideRowWhenLtEqZeroOrX_JRB,
                                      self.hideRowWhenGrEqZeroOrX_JRB,
                                      self.hideRowWhenNotZeroOrX_JRB,
                                      self.blinkRow_CB,
                                      self.autoSumAccounts_CB]

            saveMyActionListeners = {}
            for comp in allSwingControlObjects:
                myPrint("DB", ".. saving and removing listeners from %s: %s" %(comp.getName(), comp.getActionListeners()))
                saveMyActionListeners[comp.getName()] = comp.getActionListeners()
                for comboListener in comp.getActionListeners(): comp.removeActionListener(comboListener)

            # Remove listeners from QuickSearch
            myPrint("DB", ".. saving and removing listeners from QuickSearch()")
            saveQSFocusListeners = self.quickSearchField.getFocusListeners()                                            # noqa
            for listener in saveQSFocusListeners: self.quickSearchField.removeFocusListener(listener)                   # noqa
            saveQSDocListeners = self.quickSearchField.getDocument().getDocumentListeners()                             # noqa
            for listener in saveQSDocListeners: self.quickSearchField.getDocument().removeDocumentListener(listener)    # noqa

            # Reset QuickSearch
            myPrint("DB", "..about to reset QuickSearch..")
            self.resetQuickSearch()

            # Reset Filter filterOutZeroBalAccts_INACTIVE_CB
            myPrint("DB", "..about to reset filterOutZeroBalAccts_INACTIVE_CB ..")
            self.filterOutZeroBalAccts_INACTIVE_CB.setSelected(False)

            # Reset Filter filterOutZeroBalAccts_ACTIVE_CB
            myPrint("DB", "..about to reset filterOutZeroBalAccts_ACTIVE_CB ..")
            self.filterOutZeroBalAccts_ACTIVE_CB.setSelected(False)

            # Reset Filter filterIncludeSelected_CB
            myPrint("DB", "..about to reset filterIncludeSelected_CB ..")
            self.filterIncludeSelected_CB.setSelected(False)

            # Reset Filter filterOnlyShowSelected_CB
            myPrint("DB", "..about to reset filterOnlyShowSelected_CB ..")
            self.filterOnlyShowSelected_CB.setSelected(False)

            # Reset Filter filterOnlyAccountType_COMBO
            myPrint("DB", "..about to reset filterOnlyAccountType_COMBO ..")
            self.filterOnlyAccountType_COMBO.setSelectedItem("All Account Types")

            # Rebuild Select Row Dropdown
            myPrint("DB", "..about to set rowSelected_COMBO..")
            rowItems = []
            for i in range(0, self.getNumberOfRows()):
                if self.savedHideRowWhenXXXTable[i] == GlobalVars.HIDE_ROW_WHEN_ALWAYS:
                    thisRowItemTxt = "*" if (self.savedHideRowWhenXXXTable[i] > GlobalVars.HIDE_ROW_WHEN_NEVER) else " "
                elif self.savedHideRowWhenXXXTable[i] >= GlobalVars.HIDE_ROW_WHEN_ZERO_OR_X:
                    thisRowItemTxt = "~" if (self.savedHideRowWhenXXXTable[i] > GlobalVars.HIDE_ROW_WHEN_NEVER) else " "
                else:
                    thisRowItemTxt = " "
                thisRowItemTxt += pad(i + 1, 2)
                rowItems.append(thisRowItemTxt)
            # self.rowSelected_COMBO.setModel(DefaultComboBoxModel([str(i) for i in range(1,self.getNumberOfRows()+1)]))
            self.rowSelected_COMBO.setModel(DefaultComboBoxModel(rowItems))
            self.rowSelected_COMBO.setSelectedIndex(selectRowIndex)

            myPrint("DB", "..about to set balanceType_COMBO..")
            self.balanceType_COMBO.setSelectedIndex(self.savedBalanceType[selectRowIndex])

            myPrint("DB", "..about to set incomeExpenseDateRange_COMBO..")
            self.incomeExpenseDateRange_COMBO.setSelectedIndex(self.findDateRange(self.savedIncomeExpenseDateRange[selectRowIndex]))

            myPrint("DB", "..about to set includeInactive_COMBO..")
            self.includeInactive_COMBO.setSelectedIndex(self.savedIncludeInactive[selectRowIndex])

            myPrint("DB", "..about to set autoSumAccounts_CB..")
            self.autoSumAccounts_CB.setSelected(self.savedAutoSumAccounts[selectRowIndex])

            myPrint("DB", "..about to set separatorSelectorNone_JRB, separatorSelectorAbove_JRB, separatorSelectorBelow_JRB, separatorSelectorBoth_JRB..")
            self.separatorSelectorNone_JRB.setSelected(  True if self.savedRowSeparatorTable[selectRowIndex] == GlobalVars.ROW_SEPARATOR_NEVER else False)
            self.separatorSelectorAbove_JRB.setSelected( True if self.savedRowSeparatorTable[selectRowIndex] == GlobalVars.ROW_SEPARATOR_ABOVE else False)
            self.separatorSelectorBelow_JRB.setSelected( True if self.savedRowSeparatorTable[selectRowIndex] == GlobalVars.ROW_SEPARATOR_BELOW else False)
            self.separatorSelectorBoth_JRB.setSelected(  True if self.savedRowSeparatorTable[selectRowIndex] == GlobalVars.ROW_SEPARATOR_BOTH  else False)

            myPrint("DB", "..about to set savedShowWarningsTable..")
            self.showWarnings_CB.setSelected(self.savedShowWarningsTable[selectRowIndex])

            myPrint("DB", "..about to set hideRowWhenNever_JRB, hideRowWhenAlways_JRB, hideRowWhenZeroOrX_JRB, hideRowWhenLtEqZeroOrX_JRB, hideRowWhenGrEqZeroOrX_JRB, hideRowWhenNotZeroOrX_JRB..")
            self.hideRowWhenNever_JRB.setSelected(       True if self.savedHideRowWhenXXXTable[selectRowIndex] == GlobalVars.HIDE_ROW_WHEN_NEVER            else False)
            self.hideRowWhenAlways_JRB.setSelected(      True if self.savedHideRowWhenXXXTable[selectRowIndex] == GlobalVars.HIDE_ROW_WHEN_ALWAYS           else False)
            self.hideRowWhenZeroOrX_JRB.setSelected(     True if self.savedHideRowWhenXXXTable[selectRowIndex] == GlobalVars.HIDE_ROW_WHEN_ZERO_OR_X        else False)
            self.hideRowWhenLtEqZeroOrX_JRB.setSelected( True if self.savedHideRowWhenXXXTable[selectRowIndex] == GlobalVars.HIDE_ROW_WHEN_NEGATIVE_OR_X    else False)
            self.hideRowWhenGrEqZeroOrX_JRB.setSelected( True if self.savedHideRowWhenXXXTable[selectRowIndex] == GlobalVars.HIDE_ROW_WHEN_POSITIVE_OR_X    else False)
            self.hideRowWhenNotZeroOrX_JRB.setSelected(  True if self.savedHideRowWhenXXXTable[selectRowIndex] == GlobalVars.HIDE_ROW_WHEN_NOT_ZERO_OR_X    else False)

            myPrint("DB", "..about to set savedBlinkTable..")
            self.blinkRow_CB.setSelected(self.savedBlinkTable[selectRowIndex])

            myPrint("DB", "about to set hideRowXValue_JRF..")
            self.hideRowXValue_JRF.setValue(self.savedHideRowXValueTable[selectRowIndex])

            myPrint("DB", "about to set displayAverage_JRF..")
            self.displayAverage_JRF.setValue(self.savedDisplayAverageTable[selectRowIndex])

            myPrint("DB", "about to set widget name..")
            self.widgetNameField_JTF.setText(self.savedWidgetName[selectRowIndex])

            self.setKeyLabel(selectRowIndex)
            self.setParallelBalancesWarningLabel(selectRowIndex)
            self.setDateRangeLabel(selectRowIndex)

            # Rebuild Currency Dropdown, and pre-select correct one
            currencyChoices = []
            base = self.moneydanceContext.getCurrentAccountBook().getCurrencies().getBaseType()
            allCurrencies = self.moneydanceContext.getCurrentAccount().getBook().getCurrencies().getAllCurrencies()
            # allCurrencies = sorted(allCurrencies, key=lambda sort_x: ((0 if sort_x is base else 1), sort_x.getName().upper()))
            allCurrencies = sorted(allCurrencies, key=lambda sort_x: ((0 if sort_x is base else 1),
                                                                      (0 if sort_x.getCurrencyType() == CurrencyType.Type.CURRENCY else 1), # noqa
                                                                      sort_x.getName().upper()))

            # for curr in allCurrencies:
            #     # noinspection PyUnresolvedReferences
            #     if curr.getCurrencyType() == CurrencyType.Type.CURRENCY: currencyChoices.append(self.StoreCurrencyAsText(curr, base))
            for curr in allCurrencies: currencyChoices.append(self.StoreCurrencyAsText(curr, base))
            del allCurrencies

            myPrint("DB", "about to set currency_COMBO..")
            self.currency_COMBO.setModel(DefaultComboBoxModel(currencyChoices))

            if self.savedCurrencyTable[selectRowIndex] is not None:
                for c in currencyChoices:
                    if c.getUUID() == self.savedCurrencyTable[selectRowIndex]:
                        self.currency_COMBO.setSelectedItem(c)
                        break
                    del c
            del currencyChoices

            myPrint("DB", "..about to set savedDisableCurrencyFormatting..")
            self.disableCurrencyFormatting_CB.setSelected(self.savedDisableCurrencyFormatting[selectRowIndex])

            myPrint("DB", "about to rebuild jlist..")
            self.rebuildJList()

            for comp in allSwingControlObjects:
                myPrint("DB", ".. retrieving and re-adding listeners to %s: %s" %(comp.getName(), saveMyActionListeners[comp.getName()]))
                for comboListener in saveMyActionListeners[comp.getName()]: comp.addActionListener(comboListener)
            del saveMyActionListeners

            # Add listeners back into QuickSearch
            myPrint("DB", ".. Adding listeners back into QuickSearch()")
            for listener in saveQSFocusListeners: self.quickSearchField.addFocusListener(listener)                      # noqa
            for listener in saveQSDocListeners: self.quickSearchField.getDocument().addDocumentListener(listener)       # noqa

            myPrint("DB", "...Setup complete for Config screen >> row: %s"   %([selectRowIndex+1]))
            myPrint("DB", ".....%s accountsToShow stored in JList"           %(self.jlst.getModel().getSize()))
            myPrint("DB", ".....savedAccountListUUIDs: %s"                   %(self.savedAccountListUUIDs[selectRowIndex]))
            myPrint("DB", ".....savedBalanceType: %s"                        %(self.savedBalanceType[selectRowIndex]))
            myPrint("DB", ".....balanceType_COMBO: %s"                       %(self.balanceType_COMBO.getSelectedIndex()))
            myPrint("DB", ".....savedIncomeExpenseDateRange: %s"             %(self.savedIncomeExpenseDateRange[selectRowIndex]))
            myPrint("DB", ".....incomeExpenseDateRange_COMBO: %s"            %(self.incomeExpenseDateRange_COMBO.getSelectedItem()))
            myPrint("DB", ".....savedCustomDatesTable: %s"                   %(self.savedCustomDatesTable[selectRowIndex]))
            myPrint("DB", ".....savedRowSeparatorTable: %s"                  %(self.savedRowSeparatorTable[selectRowIndex]))
            myPrint("DB", ".....separatorSelectorNone_JRB: %s"               %(self.separatorSelectorNone_JRB.isSelected()))
            myPrint("DB", ".....separatorSelectorAbove_JRB: %s"              %(self.separatorSelectorAbove_JRB.isSelected()))
            myPrint("DB", ".....separatorSelectorBelow_JRB: %s"              %(self.separatorSelectorBelow_JRB.isSelected()))
            myPrint("DB", ".....separatorSelectorBoth_JRB: %s"               %(self.separatorSelectorBoth_JRB.isSelected()))
            myPrint("DB", ".....savedIncludeInactive: %s"                    %(self.savedIncludeInactive[selectRowIndex]))
            myPrint("DB", ".....includeInactive_COMBO: %s"                   %(self.includeInactive_COMBO.getSelectedIndex()))
            myPrint("DB", ".....savedAutoSumAccounts: %s"                    %(self.savedAutoSumAccounts[selectRowIndex]))
            myPrint("DB", ".....autoSumAccounts_CB: %s"                      %(self.autoSumAccounts_CB.isSelected()))
            myPrint("DB", ".....savedShowWarningsTable: %s"                  %(self.savedShowWarningsTable[selectRowIndex]))
            myPrint("DB", ".....showWarnings_CB: %s"                         %(self.showWarnings_CB.isSelected()))
            myPrint("DB", ".....savedHideRowWhenXXXTable: %s"                %(self.savedHideRowWhenXXXTable[selectRowIndex]))
            myPrint("DB", ".....savedHideRowXValueTable: %s"                 %(self.savedHideRowXValueTable[selectRowIndex]))
            myPrint("DB", ".....hideRowWhenNever_JRB: %s"                    %(self.hideRowWhenNever_JRB.isSelected()))
            myPrint("DB", ".....hideRowWhenAlways_JRB: %s"                   %(self.hideRowWhenAlways_JRB.isSelected()))
            myPrint("DB", ".....hideRowWhenZeroOrX_JRB: %s"                  %(self.hideRowWhenZeroOrX_JRB.isSelected()))
            myPrint("DB", ".....hideRowWhenLtEqZeroOrX_JRB: %s"              %(self.hideRowWhenLtEqZeroOrX_JRB.isSelected()))
            myPrint("DB", ".....hideRowWhenGrEqZeroOrX_JRB: %s"              %(self.hideRowWhenGrEqZeroOrX_JRB.isSelected()))
            myPrint("DB", ".....hideRowWhenNotZeroOrX_JRB: %s"               %(self.hideRowWhenNotZeroOrX_JRB.isSelected()))
            myPrint("DB", ".....hideRowXValue_JRF: %s"                       %(self.hideRowXValue_JRF.getValue()))
            myPrint("DB", ".....savedDisplayAverageTable: %s"                %(self.savedDisplayAverageTable[selectRowIndex]))
            myPrint("DB", ".....displayAverage_JRF: %s"                      %(self.displayAverage_JRF.getValue()))
            myPrint("DB", ".....savedBlinkTable: %s"                         %(self.savedBlinkTable[selectRowIndex]))
            myPrint("DB", ".....blinkRow_CB: %s"                             %(self.blinkRow_CB.isSelected()))
            myPrint("DB", ".....filterOutZeroBalAccts_INACTIVE_CB: %s"       %(self.filterOutZeroBalAccts_INACTIVE_CB.isSelected()))
            myPrint("DB", ".....filterOutZeroBalAccts_ACTIVE_CB: %s"         %(self.filterOutZeroBalAccts_ACTIVE_CB.isSelected()))
            myPrint("DB", ".....filterIncludeSelected_CB: %s"                %(self.filterIncludeSelected_CB.isSelected()))
            myPrint("DB", ".....filterOnlyShowSelected_CB: %s"               %(self.filterOnlyShowSelected_CB.isSelected()))
            myPrint("DB", ".....filterOnlyAccountType_COMBO: %s"             %(self.filterOnlyAccountType_COMBO.getSelectedItem()))
            myPrint("DB", ".....savedCurrencyTable: %s"                      %(self.savedCurrencyTable[selectRowIndex]))
            myPrint("DB", ".....savedDisableCurrencyFormatting: %s"          %(self.savedDisableCurrencyFormatting[selectRowIndex]))
            myPrint("DB", ".....savedWidgetName: %s"                         %(self.savedWidgetName[selectRowIndex]))

            myPrint("DB", ".....savedAutoSumDefault: %s"                     %(self.savedAutoSumDefault))
            myPrint("DB", ".....savedDisableWidgetTitle: %s"                 %(self.savedDisableWidgetTitle))
            myPrint("DB", ".....savedShowDashesInsteadOfZeros: %s"           %(self.savedShowDashesInsteadOfZeros))
            myPrint("DB", ".....savedTreatSecZeroBalInactive: %s"            %(self.savedTreatSecZeroBalInactive))

            myPrint("DB", ".....savedUseIndianNumberFormat: %s"              %(self.savedUseIndianNumberFormat))
            myPrint("DB", ".....savedHideDecimals: %s"                       %(self.savedHideDecimals))
            myPrint("DB", ".....savedDisplayVisualUnderDots: %s"             %(self.savedDisplayVisualUnderDots))

            myPrint("DB", ".....savedExpandedView: %s"                       %(self.savedExpandedView))

            myPrint("DB", ".....%s accountsToShow matched UUIDs and selected in JList" %(len(self.jlst.getSelectedIndices())))

        def setSelectedRowIndex(self, row): self.rowSelectedSaved = row
        def getSelectedRowIndex(self):      return (self.rowSelectedSaved)
        def getSelectedRow(self):           return (self.getSelectedRowIndex() + 1)

        def getNumberOfRows(self):          return len(self.savedAccountListUUIDs)

        def storeJTextFieldsForSelectedRow(self):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))

            if self.switchFromHomeScreen:
                myPrint("DB", ".. switchFromHomeScreen detected... ignoring....")
                self.switchFromHomeScreen = False
            else:
                myPrint("DB", ".. selectedRowIndex(): %s was: '%s', will set to: '%s'" %(self.getSelectedRowIndex(), self.savedWidgetName[self.getSelectedRowIndex()], self.widgetNameField_JTF.getText()))
                if self.savedWidgetName[self.getSelectedRowIndex()] != self.widgetNameField_JTF.getText():
                    myPrint("DB", "..... saving widget name....")
                    self.savedWidgetName[self.getSelectedRowIndex()] = self.widgetNameField_JTF.getText()
                    self.configSaved = False

                jrfValue = self.hideRowXValue_JRF.getValue()
                myPrint("DB", ".. selectedRowIndex(): %s was: '%s', will set to: '%s'" %(self.getSelectedRowIndex(), self.savedHideRowXValueTable[self.getSelectedRowIndex()], jrfValue))
                if self.savedHideRowXValueTable[self.getSelectedRowIndex()] != jrfValue:
                    myPrint("DB", "..... saving hide row's X-Value....")
                    self.savedHideRowXValueTable[self.getSelectedRowIndex()] = jrfValue
                    self.configSaved = False

                jrfValue = self.displayAverage_JRF.getValue()
                myPrint("DB", ".. selectedRowIndex(): %s was: '%s', will set to: '%s'" %(self.getSelectedRowIndex(), self.savedDisplayAverageTable[self.getSelectedRowIndex()], jrfValue))
                if self.savedDisplayAverageTable[self.getSelectedRowIndex()] != jrfValue:
                    myPrint("DB", "..... saving display average value....")
                    self.savedDisplayAverageTable[self.getSelectedRowIndex()] = jrfValue
                    self.configSaved = False

        def storeCurrentJListSelected(self):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            del self.savedAccountListUUIDs[self.getSelectedRowIndex()][:]
            myPrint("DB", "Storing account list for HomePageView widget for row: %s into memory.." %(self.getSelectedRow()))
            for selectedAccount in self.jlst.getSelectedValuesList():
                myPrint("DB", "...storing account %s into memory..." %(selectedAccount))
                self.savedAccountListUUIDs[self.getSelectedRowIndex()].append(selectedAccount.getAccount().getUUID())

        def resetJListModel(self):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))

            if isinstance(self.jlst, JList):
                myPrint("DB", "Setting JList ListData model to [] to release any references to objects")
                self.jlst.disableSelectionListeners()                                                                   # noqa
                self.jlst.setListData([])
                self.jlst.originalListObjects = []
                self.jlst.listOfSelectedObjects = []
                self.jlst.parallelAccountBalances = buildEmptyTxnOrBalanceArray()

                myPrint("DB", "Removing any JList ListSelectionListeners...")
                for listener in self.jlst.getListSelectionListeners(): self.jlst.removeListSelectionListener(listener)

            else:
                myPrint("DB", "self.jlst is None or not JList (no action)")

        def setJListDataAndSelection(self, _listOfAccountsForJList, lFilter=False):
            try:
                myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))

                if lFilter: myPrint("DB", ".... FILTER MODE: %s" %(lFilter))

                myPrint("DB", ".. Was passed:", _listOfAccountsForJList)

                countMatch = 0
                index = 0
                _indexesToSelect = []
                _objectsToSelect = []

                if not lFilter:
                    verificationList = self.savedAccountListUUIDs[self.getSelectedRowIndex()]
                else:
                    verificationList = [obj.getAccount().getUUID() for obj in self.jlst.listOfSelectedObjects]

                for a in _listOfAccountsForJList:
                    if a.getAccount().getUUID() in verificationList:
                        countMatch += 1
                        myPrint("DB", "...RowIdx: %s >> selecting %s in JList()" %(self.getSelectedRowIndex(), a))
                        _indexesToSelect.append(index)
                        _objectsToSelect.append(a)

                    index += 1

                self.jlst.disableSelectionListeners()
                self.jlst.setListData(_listOfAccountsForJList)
                if len(_indexesToSelect):
                    self.jlst.setSelectedIndices(_indexesToSelect)
                    self.jlst.ensureIndexIsVisible(_indexesToSelect[0])
                    self.jlst.scrollRectToVisible(self.jlst.getCellBounds(_indexesToSelect[0],_indexesToSelect[0]+1))

                self.jlst.enableSelectionListeners()

                if not lFilter:
                    myPrint("DB", ".. Saving Original List too...")
                    self.jlst.originalListObjects = _listOfAccountsForJList
                    self.jlst.listOfSelectedObjects = _objectsToSelect

                self.jlst.repaint()

            except:
                myPrint("DB", "@@ ERROR in setJListDataAndSelection() routine ?")
                dump_sys_error_to_md_console_and_errorlog()
                raise

        class RebuildParallelBalanceTableSwingWorker(SwingWorker):
            def __init__(self):
                NetAccountBalancesExtension.getNAB().swingWorkers.append(self)      # Already locked from calling code

            def isBuildHomePageWidgetSwingWorker(self):         return False
            def isSimulateTotalForRowSwingWorker(self):         return False
            def isRebuildParallelBalanceTableSwingWorker(self): return True

            def doInBackground(self):                                                                                   # Runs on a worker thread
                myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))

                ct = Thread.currentThread()
                if "_extn_NAB" not in ct.getName(): ct.setName(u"%s_extn_NAB" %(ct.getName()))

                NAB = NetAccountBalancesExtension.getNAB()
                NAB.jlst.parallelAccountBalances = buildEmptyTxnOrBalanceArray()

                NAB.jlst.parallelAccountBalances = rebuildParallelAccountBalances(self)

                return not self.isCancelled()

            def done(self):                                                                                             # Executes on the EDT
                try:
                    myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))

                    NAB = NetAccountBalancesExtension.getNAB()

                    self.get()  # wait for process to finish
                    NAB.searchFiltersUpdated()
                    # NAB.jlst.repaint()

                    NAB.simulateTotalForRow(lFromParallel=True)

                except InterruptedException:
                    myPrint("DB", "@@ RebuildParallelBalanceTableSwingWorker InterruptedException - aborting...")

                except CancellationException:
                    myPrint("DB", "@@ RebuildParallelBalanceTableSwingWorker CancellationException - aborting...")

                except:
                    myPrint("B", "@@ ERROR: RebuildParallelBalanceTableSwingWorker:Done() has failed?")
                    dump_sys_error_to_md_console_and_errorlog()
                    raise

                finally:
                    NAB = NetAccountBalancesExtension.getNAB()
                    with NAB.swingWorkers_LOCK:
                        if self in NAB.swingWorkers:
                            NAB.swingWorkers.remove(self)
                        else:
                            raise Exception("@@ ALERT: I did not find myself within swingWorkers list, so doing nothing...: %s" %(self))

        def rebuildParallelBalanceTable(self):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))

            if self.swingWorkers_LOCK.locked():
                myPrint("DB", "@@.. ALERT In .rebuildParallelBalanceTable() >> swingWorkers_LOCK locked. Request might wait....")

            self.cancelSwingWorkers(lSimulates=True, lParallelRebuilds=True)  # Running outside of lock....

            with self.swingWorkers_LOCK:

                if not self.isParallelRebuildRunning_NOLOCKFIRST():
                    sw = self.RebuildParallelBalanceTableSwingWorker()
                    sw.execute()
                else:
                    myPrint("DB", "@@..Sorry parallelRebuildRunning already running, cancelled request.... Try later....")


        def rebuildJList(self):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))

            listOfAllAccountsForJList = []
            # getAccounts = AccountUtil.allMatchesForSearch(self.moneydanceContext.getCurrentAccountBook(),
            getAccounts = allMatchesForSearch(self.moneydanceContext.getCurrentAccountBook(),
                MyAcctFilter(self.savedIncludeInactive[self.getSelectedRowIndex()],
                             self.savedAutoSumAccounts[self.getSelectedRowIndex()],
                             self.savedAccountListUUIDs[self.getSelectedRowIndex()],
                             self.savedBalanceType[self.getSelectedRowIndex()],
                             self.savedIncomeExpenseDateRange[self.getSelectedRowIndex()]))

            for acct in getAccounts: listOfAllAccountsForJList.append(StoreAccountList(acct, self.savedAutoSumAccounts[self.getSelectedRowIndex()]))
            del getAccounts

            self.rebuildParallelBalanceTable()

            self.setJListDataAndSelection(listOfAllAccountsForJList)

        def dumpSavedOptions(self):

            if not debug: return

            NAB = NetAccountBalancesExtension.getNAB()

            myPrint("B", "NAB: Analysis of saved options:")
            myPrint("B", "-------------------------------------------")
            myPrint("B", " %s" %(pad("savedAutoSumDefault",30)),            NAB.savedAutoSumDefault)
            myPrint("B", " %s" %(pad("savedDisableWidgetTitle",30)),        NAB.savedDisableWidgetTitle)
            myPrint("B", " %s" %(pad("savedShowDashesInsteadOfZeros",30)),  NAB.savedShowDashesInsteadOfZeros)
            myPrint("B", " %s" %(pad("savedTreatSecZeroBalInactive",30)),   NAB.savedTreatSecZeroBalInactive)
            myPrint("B", " %s" %(pad("savedUseIndianNumberFormat",30)),     NAB.savedUseIndianNumberFormat)
            myPrint("B", " %s" %(pad("savedHideDecimals",30)),              NAB.savedHideDecimals)
            myPrint("B", " %s" %(pad("savedDisplayVisualUnderDots",30)),    NAB.savedDisplayVisualUnderDots)
            myPrint("B", " %s" %(pad("savedExpandedView",30)),              NAB.savedExpandedView)
            myPrint("B", " ----")

            for iRowIdx in range(0, NAB.getNumberOfRows()):
                onRow = iRowIdx+1
                myPrint("B", "  Row: %s" %(onRow))
                myPrint("B", "  %s" %(pad("savedWidgetName",60)),               NAB.savedWidgetName[iRowIdx])
                myPrint("B", "  %s" %(pad("savedAccountListUUIDs",60)),         NAB.savedAccountListUUIDs[iRowIdx])
                myPrint("B", "  %s" %(pad("savedCurrencyTable",60)),            NAB.savedCurrencyTable[iRowIdx])
                myPrint("B", "  %s" %(pad("savedDisableCurrencyFormatting",60)),NAB.savedDisableCurrencyFormatting[iRowIdx])
                myPrint("B", "  %s" %(pad("savedBalanceType",60)),              NAB.savedBalanceType[iRowIdx])
                myPrint("B", "  %s" %(pad("savedAutoSumAccounts",60)),          NAB.savedAutoSumAccounts[iRowIdx])
                myPrint("B", "  %s" %(pad("savedIncludeInactive",60)),          NAB.savedIncludeInactive[iRowIdx])
                myPrint("B", "  %s" %(pad("savedShowWarningsTable",60)),        NAB.savedShowWarningsTable[iRowIdx])
                myPrint("B", "  %s" %(pad("savedHideRowWhenXXXTable",60)),      NAB.savedHideRowWhenXXXTable[iRowIdx])
                myPrint("B", "  %s" %(pad("savedHideRowXValueTable",60)),       NAB.savedHideRowXValueTable[iRowIdx])
                myPrint("B", "  %s" %(pad("savedDisplayAverageTable",60)),      NAB.savedDisplayAverageTable[iRowIdx])
                myPrint("B", "  %s" %(pad("savedIncomeExpenseDateRange",60)),   NAB.savedIncomeExpenseDateRange[iRowIdx])
                myPrint("B", "  %s" %(pad("savedCustomDatesTable",60)),         NAB.savedCustomDatesTable[iRowIdx])
                myPrint("B", "  %s" %(pad("savedRowSeparatorTable",60)),        NAB.savedRowSeparatorTable[iRowIdx])
                myPrint("B", "  %s" %(pad("savedBlinkTable",60)),               NAB.savedBlinkTable[iRowIdx])

                dateRange = DateRangeOption.fromKey(NAB.savedIncomeExpenseDateRange[iRowIdx])
                myPrint("B", "  %s" %(pad(">> System Default for savedIncomeExpenseDateRange will be:",60)),   dateRange.getDateRange())
                myPrint("B", "  ----")

        def validateIncExpDateOptions(self):
            myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()")

            myPrint("DB", ".. Validating savedIncomeExpenseDateRange parameters...")
            NAB = NetAccountBalancesExtension.getNAB()

            for iRowIdx in range(0,NAB.getNumberOfRows()):
                onRow = iRowIdx+1

                if isIncomeExpenseAllDatesSelected(iRowIdx): continue

                lFoundAnyIncExp = False
                for accID in NAB.savedAccountListUUIDs[iRowIdx]:
                    acct = NAB.moneydanceContext.getCurrentAccountBook().getAccountByUUID(accID)

                    if acct is None:
                        myPrint("DB", "... WARNING: Row: %s >> Account for UUID: '%s' NOT FOUND... Ignoring this error...." %(onRow, accID))
                        continue
                    else:
                        if isIncomeExpenseAcct(acct):
                            lFoundAnyIncExp = True
                            break
                    continue

                if not lFoundAnyIncExp:
                    myPrint("B", "... ALERT: Saved Parameters - Row: %s >> Inc/Exp Date Range: '%s' selected but no Income/Expense Accounts.... "
                                "RESETTING BACK TO ALL DATES" %(onRow, NAB.savedIncomeExpenseDateRange[iRowIdx]))
                    NAB.savedIncomeExpenseDateRange[iRowIdx] = NAB.incomeExpenseDateRangeDefault()

        class WindowListener(WindowAdapter):

            def __init__(self, theFrame, moduleID):
                self.theFrame = theFrame        # type: MyJFrame
                self.myModuleID = moduleID

            # noinspection PyMethodMayBeStatic
            def windowActivated(self, WindowEvent):                                                                     # noqa

                myPrint("DB", "In %s.%s() - Event: %s" %(self, inspect.currentframe().f_code.co_name, WindowEvent))
                myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

                NAB = NetAccountBalancesExtension.getNAB()

                # ######################################################################################################
                # On Mac,since VAqua was used builds 3039 onwards, the JMenuBar() would sometimes appear in the wrong place
                # It seems that the useScreenMenuBar=false setting needs to be in play as the JFrame is made visible
                # or perhaps when the JMenuBar() is added.... Hence doing it here. A bit messy I know.....
                # ... probably I should create a new JFrame() with every config call, but then I would have to change the launch checks...
                # ######################################################################################################

                myPrint("DB", "...Creating and setting the JMenuBar() now....: %s" %(NAB.mainMenuBar))
                NAB.createMenus()

                # ##################################################################################################

                if NAB.configPanelOpen:
                    myPrint("DB", ".. Application's config panel is already open... Just select correct row if different...")
                    if NAB.rowSelected_COMBO.getSelectedIndex() != NAB.getSelectedRowIndex():
                        myPrint("DB", "... Need to switch row....")
                        NAB.rowSelected_COMBO.setSelectedIndex(NAB.getSelectedRowIndex())
                    else:
                        myPrint("DB", "... Row selected is already correct - no change....")

                elif (NAB.moneydanceContext.getCurrentAccount() is not None
                      and NAB.moneydanceContext.getCurrentAccount().getBook() is not None):

                    myPrint("DB", ".. Application's config panel was not open already...")
                    NAB.configPanelOpen = True
                    NAB.rebuildFrameComponents(NAB.getSelectedRowIndex())

                    NAB.savedExpandedView = NAB.expandedViewDefault()   # Force widget to be fully visible....

                else:
                    myPrint("B", "WARNING: getCurrentAccount() or 'Book' is None.. Perhaps MD is shutting down.. Will do nothing....")

                # The below is in case of a LaF/Theme change
                pnls = []
                subPnls = []
                for comp in NAB.theFrame.getContentPane().getComponents():
                    if isinstance(comp, JPanel) and comp.getClientProperty("%s.id" %(NAB.myModuleID)) == "controlPnl": pnls.append(comp)
                    for subComp in comp.getComponents():
                        if isinstance(subComp, JPanel) and subComp.getClientProperty("%s.id" %(NAB.myModuleID)) == "controlPnl": subPnls.append(comp)

                for comp in subPnls:
                    myPrint("DB", ".... invalidating: %s" %(comp))
                    comp.revalidate()
                    comp.repaint()

                for comp in pnls:
                    myPrint("DB", ".... invalidating: %s" %(comp))
                    comp.revalidate()
                    comp.repaint()

                NAB.switchFromHomeScreen = False
                myPrint("DB", "Exiting ", inspect.currentframe().f_code.co_name, "()")

            # noinspection PyMethodMayBeStatic
            def windowDeactivated(self, WindowEvent):                                                                   # noqa
                myPrint("DB", "In %s.%s() - Event: %s" %(self, inspect.currentframe().f_code.co_name, WindowEvent))

                NAB = NetAccountBalancesExtension.getNAB()

                myPrint("DB", "...setting JMenuBar() to None")
                NAB.theFrame.setJMenuBar(None)

            # noinspection PyMethodMayBeStatic
            def windowDeiconified(self, WindowEvent):                                                                   # noqa
                myPrint("DB", "In %s.%s() - Event: %s" %(self, inspect.currentframe().f_code.co_name, WindowEvent))

            # noinspection PyMethodMayBeStatic
            def windowGainedFocus(self, WindowEvent):                                                                   # noqa
                myPrint("DB", "In %s.%s() - Event: %s" %(self, inspect.currentframe().f_code.co_name, WindowEvent))

            # noinspection PyMethodMayBeStatic
            def windowLostFocus(self, WindowEvent):                                                                     # noqa
                myPrint("DB", "In %s.%s() - Event: %s" %(self, inspect.currentframe().f_code.co_name, WindowEvent))

            # noinspection PyMethodMayBeStatic
            def windowIconified(self, WindowEvent):                                                                     # noqa
                myPrint("DB", "In %s.%s() - Event: %s" %(self, inspect.currentframe().f_code.co_name, WindowEvent))

            # noinspection PyMethodMayBeStatic
            def windowOpened(self, WindowEvent):                                                                        # noqa
                myPrint("DB", "In %s.%s() - Event: %s" %(self, inspect.currentframe().f_code.co_name, WindowEvent))

            # noinspection PyMethodMayBeStatic
            def windowStateChanged(self, WindowEvent):                                                                  # noqa
                myPrint("DB", "In %s.%s() - Event: %s" %(self, inspect.currentframe().f_code.co_name, WindowEvent))

            def terminate_script(self):
                myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()")
                myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

                try:
                    # NOTE - .dispose() - The windowClosed event should set .isActiveInMoneydance False and .removeAppEventListener()
                    if not SwingUtilities.isEventDispatchThread():
                        SwingUtilities.invokeLater(GenericDisposeRunnable(self.theFrame))
                    else:
                        GenericDisposeRunnable(self.theFrame).run()
                except:
                    myPrint("B", "@@ Error. Final dispose of application failed....?")
                    dump_sys_error_to_md_console_and_errorlog()

            def windowClosing(self, WindowEvent):                                                                       # noqa

                myPrint("DB", "In %s.%s() - Event: %s" %(self, inspect.currentframe().f_code.co_name, WindowEvent))
                myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

                NAB = NetAccountBalancesExtension.getNAB()
                HPV = MyHomePageView.getHPV()

                NAB.configPanelOpen = False

                if self.theFrame.isVisible():
                    myPrint("DB", ".. in windowClosing, but isVisible is True, let's trigger a widget refresh....")

                    NAB.cancelSwingWorkers(lSimulates=True, lParallelRebuilds=True, lBuildHomePageWidgets=True)

                    HPV.lastRefreshTriggerWasAccountModified = False

                    NAB.resetJListModel()
                    NAB.executeRefresh()
                else:
                    myPrint("DB", ".. in windowClosing, and isVisible is False, so will start termination....")
                    self.terminate_script()

            def windowClosed(self, WindowEvent):                                                                        # noqa

                myPrint("DB", "In %s.%s() - Event: %s" %(self, inspect.currentframe().f_code.co_name, WindowEvent))
                myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

                NAB = NetAccountBalancesExtension.getNAB()

                NAB.configPanelOpen = False

                self.theFrame.isActiveInMoneydance = False

                if self.theFrame.MoneydanceAppListener is not None and not self.theFrame.MoneydanceAppListener.alreadyClosed:

                    try:
                        myPrint("DB", "\n@@@ Calling .unload() to deactivate extension and close the HomePageView... \n")
                        self.theFrame.MoneydanceAppListener.unload(True)
                    except:
                        myPrint("B", "@@@ FAILED to call .unload() to deactivate extension and close the HomePageView... \n")
                        dump_sys_error_to_md_console_and_errorlog()

                elif self.theFrame.MoneydanceAppListener is not None and self.theFrame.MoneydanceAppListener.alreadyClosed:
                    myPrint("DB", "Skipping .unload() as I'm assuming that's where I was called from (alreadyClosed was set)...")
                else:
                    myPrint("DB", "MoneydanceAppListener is None so Skipping .unload()..")

                self.theFrame.MoneydanceAppListener.alreadyClosed = True
                self.theFrame.MoneydanceAppListener = None

                cleanup_actions(self.theFrame, NAB.moneydanceContext)

        class MyJFieldFocusAdapter(FocusAdapter):
            def __init__(self): pass

            def focusLost(self, event):
                myPrint("DB", "In MyJFieldFocusAdapter.focusLost() ... Checking whether I need to capture / set JTextField contents..")
                NAB = NetAccountBalancesExtension.getNAB()
                if event.getSource().getName().lower() == "widgetNameField_JTF".lower():
                    if NAB.savedWidgetName[NAB.getSelectedRowIndex()] != event.getSource().getText():
                        myPrint("DB", "... Yup - Setting widgetNameField_JTF to: '%s'" %(event.getSource().getText()))
                        NAB.savedWidgetName[NAB.getSelectedRowIndex()] = event.getSource().getText()
                        NAB.configSaved = False
                    else:
                        myPrint("DB", "... Nope.. No change to widgetNameField_JTF")

                lShoudSimulate = False
                if event.getSource().getName().lower() == "hideRowXValue_JRF".lower():
                    jrfValue = event.getSource().getValue()
                    if NAB.savedHideRowXValueTable[NAB.getSelectedRowIndex()] != jrfValue:
                        myPrint("DB", "... Yup - Setting hideRowXValue_JRF to: %s (was: %s" %(jrfValue, NAB.savedHideRowXValueTable[NAB.getSelectedRowIndex()]))
                        NAB.savedHideRowXValueTable[NAB.getSelectedRowIndex()] = jrfValue
                        NAB.configSaved = False
                        lShoudSimulate = True
                    else:
                        myPrint("DB", "... Nope.. No change to hideRowXValue_JRF(%s)" %(NAB.savedHideRowXValueTable[NAB.getSelectedRowIndex()]))

                if event.getSource().getName().lower() == "displayAverage_JRF".lower():
                    jrfValue = event.getSource().getValue()
                    if NAB.savedDisplayAverageTable[NAB.getSelectedRowIndex()] != jrfValue:
                        myPrint("DB", "... Yup - Setting displayAverage_JRF to: %s (was: %s" %(jrfValue, NAB.savedDisplayAverageTable[NAB.getSelectedRowIndex()]))
                        NAB.savedDisplayAverageTable[NAB.getSelectedRowIndex()] = jrfValue
                        NAB.configSaved = False
                        lShoudSimulate = True
                    else:
                        myPrint("DB", "... Nope.. No change to displayAverage_JRF(%s)" %(NAB.savedDisplayAverageTable[NAB.getSelectedRowIndex()]))

                if lShoudSimulate: NAB.simulateTotalForRow()


        class MyRefreshRunnable(Runnable):

            def __init__(self): pass

            # noinspection PyMethodMayBeStatic
            def run(self):

                NAB = NetAccountBalancesExtension.getNAB()

                myPrint("DB", "Inside %s MyRefreshRunnable.... About call HomePageView .refresh()\n" %(NAB.myModuleID))
                myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
                try:
                    NAB.saveMyHomePageView.refresh()
                    myPrint("DB", "Back from calling HomePageView .refresh() on %s...." %(NAB.myModuleID))
                except:
                    dump_sys_error_to_md_console_and_errorlog()
                    myPrint("B", "@@ ERROR calling .refresh() in HomePageView on %s....  :-< " %(NAB.myModuleID))
                return

        def executeRefresh(self):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            myPrint("DB", "... About to call HomePageView .refresh() after updating accounts list via SwingUtilities.invokeLater(MyRefreshRunnable())")
            SwingUtilities.invokeLater(self.MyRefreshRunnable())

        def getWarningType(self, _type):
            if _type == 0:
                return("MULTI-WARNINGS")
            elif _type == 1:
                return("AUTOSUM: ALSO IN PARENT WARNING")
            elif _type == 2:
                return("INCLUDES INACTIVE CHILD WARNING")
            elif _type == 3:
                return("PARENT IS INACTIVE WARNING")
            elif _type == 4:
                return("MIXING ACCTS/CATS/SECS WARNING")
            return("WARNING ? DETECTED")


        class SimulateTotalForRowSwingWorker(SwingWorker):
            def __init__(self):
                NetAccountBalancesExtension.getNAB().swingWorkers.append(self)  # Already locked by calling class

            def isBuildHomePageWidgetSwingWorker(self):         return False
            def isSimulateTotalForRowSwingWorker(self):         return True
            def isRebuildParallelBalanceTableSwingWorker(self): return False

            def doInBackground(self):                                                                                   # Runs on a worker thread
                # type: () -> [{Account: [HoldBalance]}]

                myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))

                ct = Thread.currentThread()
                if "_extn_NAB" not in ct.getName(): ct.setName(u"%s_extn_NAB" %(ct.getName()))

                NAB = NetAccountBalancesExtension.getNAB()
                md = NAB.moneydanceContext

                totalBalanceTable = None

                if not self.isCancelled():
                    book = md.getCurrentAccountBook()
                    totalBalanceTable = MyHomePageView.calculateBalances(book, NAB.getSelectedRowIndex(), lFromSimulate=True, swClass=self)

                return totalBalanceTable

            def done(self):                                                                                             # Executes on the EDT
                try:
                    myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))

                    NAB = NetAccountBalancesExtension.getNAB()

                    md = NAB.moneydanceContext

                    BlinkSwingTimer.stopAllBlinkers()

                    baseCurr = NAB.moneydanceContext.getCurrentAccountBook().getCurrencies().getBaseType()
                    altFG = md.getUI().colors.tertiaryTextFG

                    totalBalanceTable = self.get()  # wait for process to finish

                    if isinstance(totalBalanceTable, list): pass

                    NAB.simulateTotal_label.setForeground(md.getUI().colors.defaultTextForeground)
                    NAB.warning_label.setForeground(md.getUI().colors.defaultTextForeground)

                    if NAB.warningInParametersDetected and NAB.savedShowWarningsTable[NAB.getSelectedRowIndex()]:
                        NAB.warning_label.setText("*%s*" %(NAB.getWarningType(NAB.warningInParametersDetectedType)))
                        NAB.warning_label.setForeground(md.getUI().colors.errorMessageForeground)
                    elif NAB.savedShowWarningsTable[NAB.getSelectedRowIndex()]:
                        NAB.warning_label.setText(wrap_HTML_small("", "no warnings detected", altFG))
                    elif not NAB.savedShowWarningsTable[NAB.getSelectedRowIndex()]:
                        NAB.warning_label.setText(wrap_HTML_small("", "warnings turned off", altFG))
                    else:
                        NAB.warning_label.setText("?")

                    if len(totalBalanceTable) < NAB.getSelectedRow():
                        myPrint("@@ ERROR: Returned totalBalanceTable is incorrect?")
                        NAB.simulateTotal_label.setText("<ERROR>")
                        NAB.simulateTotal_label.setForeground(md.getUI().colors.errorMessageForeground)
                    else:
                        myPrint("DB", "Result of simulation:", totalBalanceTable)
                        _curIdx = 0; _valIdx = 1; _secLabelTextIdx = 2

                        i = NAB.getSelectedRowIndex()

                        lUseAverage = (NAB.savedDisplayAverageTable[i] != 1.0)
                        balanceOrAverage = totalBalanceTable[i][_valIdx]

                        if NAB.savedHideRowWhenXXXTable[i] == GlobalVars.HIDE_ROW_WHEN_ALWAYS:
                            NAB.simulateTotal_label.setText(GlobalVars.WIDGET_ROW_DISABLED)
                        elif balanceOrAverage is None:
                            NAB.simulateTotal_label.setText(GlobalVars.DEFAULT_WIDGET_ROW_NOT_CONFIGURED.lower())
                        else:
                            showCurrText = ""
                            if totalBalanceTable[i][_curIdx] is not baseCurr: showCurrText = " (%s)" %(totalBalanceTable[i][_curIdx].getIDString())

                            showAverageText = ""
                            if lUseAverage:
                                showAverageText = " (avg)"
                                balanceOrAverage = totalBalanceTable[i][_curIdx].getLongValue(totalBalanceTable[i][_curIdx].getDoubleValue(balanceOrAverage) / NAB.savedDisplayAverageTable[i])
                                myPrint("DB", ":: Row: %s using average / by: %s" %(i+1, NAB.savedDisplayAverageTable[i]))

                            theFormattedValue = formatFancy(totalBalanceTable[i][_curIdx],
                                                            balanceOrAverage,
                                                            NAB.decimal,
                                                            fancy=(not NAB.savedDisableCurrencyFormatting[i]),
                                                            indianFormat=NAB.savedUseIndianNumberFormat,
                                                            includeDecimals=(not NAB.savedHideDecimals),
                                                            roundingTarget=(0.0 if (not NAB.savedHideDecimals) else NAB.savedHideRowXValueTable[i]))

                            resultTxt = wrap_HTML_small(theFormattedValue, showCurrText + showAverageText, altFG)
                            NAB.simulateTotal_label.setText(resultTxt)

                            if balanceOrAverage < 0:
                                NAB.simulateTotal_label.setForeground(md.getUI().colors.negativeBalFG)
                            else:
                                if "default" == ThemeInfo.themeForID(md.getUI(), md.getUI().getPreferences().getSetting("gui.current_theme", ThemeInfo.DEFAULT_THEME_ID)).getThemeID():
                                    NAB.simulateTotal_label.setForeground(md.getUI().colors.budgetHealthyColor)
                                else:
                                    NAB.simulateTotal_label.setForeground(md.getUI().colors.positiveBalFG)

                            if NAB.savedBlinkTable[i]:
                                BlinkSwingTimer(1200, [NAB.simulateTotal_label], flipColor=(MD_REF.getUI().getColors().defaultTextForeground), flipBold=True).start()


                except InterruptedException:
                    myPrint("DB", "@@ SimulateTotalForRowSwingWorker InterruptedException - aborting...")

                except CancellationException:
                    myPrint("DB", "@@ SimulateTotalForRowSwingWorker CancellationException - aborting...")

                except AttributeError as e:
                    if not detectMDClosingError(e): raise

                except:
                    myPrint("B", "@@ ERROR: SimulateTotalForRowSwingWorker:Done() has failed?")
                    dump_sys_error_to_md_console_and_errorlog()
                    raise

                finally:
                    NAB = NetAccountBalancesExtension.getNAB()
                    with NAB.swingWorkers_LOCK:
                        if self in NAB.swingWorkers:
                            NAB.swingWorkers.remove(self)
                        else:
                            raise Exception("@@ ALERT: I did not find myself within swingWorkers list, so doing nothing...: %s" %(self))


        def simulateTotalForRow(self, lFromParallel=False):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))

            if self.swingWorkers_LOCK.locked():
                myPrint("DB", "@@.. ALERT In .simulateTotalForRow() >> swingWorkers_LOCK locked. Request might wait....")

            self.cancelSwingWorkers(lSimulates=True)  # Running outside of lock....

            with self.swingWorkers_LOCK:

                if not lFromParallel and self.isParallelRebuildRunning_NOLOCKFIRST():
                    myPrint("DB", "..Sorry Simulate cannot run as Parallel rebuild already running, cancelled request.... Try later....")
                elif self.isSimulateRunning_NOLOCKFIRST():
                    myPrint("DB", "..Sorry Simulate already running, cancelled request.... Try later....")
                else:
                    sw = self.SimulateTotalForRowSwingWorker()
                    sw.execute()

        class MyActionListener(AbstractAction):

            def __init__(self): pass

            def actionPerformed(self, event):
                global debug    # Keep this here as we change debug further down

                myPrint("DB", "In %s.%s() - Event: %s" %(self, inspect.currentframe().f_code.co_name, event))
                myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
                myPrint("DB", "... Action Command:", event.getActionCommand(), "(event.source.name: %s)" %(event.getSource().getName()))

                lShouldSaveParameters = False
                lShouldRefreshHomeScreenWidget = False

                NAB = NetAccountBalancesExtension.getNAB()

                allRowVariables = [NAB.savedAccountListUUIDs,
                                   NAB.savedBalanceType,
                                   NAB.savedIncomeExpenseDateRange,
                                   NAB.savedCustomDatesTable,
                                   NAB.savedRowSeparatorTable,
                                   NAB.savedBlinkTable,
                                   NAB.savedAutoSumAccounts,
                                   NAB.savedIncludeInactive,
                                   NAB.savedShowWarningsTable,
                                   NAB.savedHideRowWhenXXXTable,
                                   NAB.savedHideRowXValueTable,
                                   NAB.savedDisplayAverageTable,
                                   NAB.savedWidgetName,
                                   NAB.savedDisableCurrencyFormatting,
                                   NAB.savedCurrencyTable
                                   ]

                # ##########################################################################################################
                if event.getActionCommand().lower() == "about":
                    AboutThisScript(NAB.theFrame).go()

                # ##########################################################################################################
                if event.getActionCommand().lower() == "help":
                    QuickJFrame("%s:%s - Help" %(NAB.myModuleID, GlobalVars.DEFAULT_WIDGET_DISPLAY_NAME), NAB.helpFile, lWrapText=False, lAutoSize=True).show_the_frame()

                # ######################################################################################################
                if event.getActionCommand().lower().startswith("AutoSum Accts".lower()):
                    if event.getSource().getName().lower() == "autoSumAccounts_CB".lower():
                        if NAB.savedAutoSumAccounts[NAB.getSelectedRowIndex()] != event.getSource().isSelected():
                            myPrint("DB", ".. setting savedAutoSumAccounts to: %s for row: %s" %(event.getSource().isSelected(), NAB.getSelectedRow()))
                            NAB.savedAutoSumAccounts[NAB.getSelectedRowIndex()] = event.getSource().isSelected()
                            NAB.configSaved = False
                            NAB.simulateTotalForRow()
                            NAB.jlst.repaint()

                # ######################################################################################################
                if event.getActionCommand().lower().startswith("Disable Currency Formatting".lower()):
                    if event.getSource().getName().lower() == "disableCurrencyFormatting_CB".lower():
                        if NAB.savedDisableCurrencyFormatting[NAB.getSelectedRowIndex()] != event.getSource().isSelected():
                            myPrint("DB", ".. setting savedDisableCurrencyFormatting to: %s for row: %s" %(event.getSource().isSelected(), NAB.getSelectedRow()))
                            NAB.savedDisableCurrencyFormatting[NAB.getSelectedRowIndex()] = event.getSource().isSelected()
                            NAB.configSaved = False
                            NAB.simulateTotalForRow()
                            NAB.jlst.repaint()

                # ######################################################################################################
                if event.getActionCommand().lower().startswith("Show Warnings".lower()):
                    if event.getSource().getName().lower() == "showWarnings_CB".lower():
                        if NAB.savedShowWarningsTable[NAB.getSelectedRowIndex()] != event.getSource().isSelected():
                            myPrint("DB", ".. setting savedShowWarningsTable to: %s for row: %s" %(event.getSource().isSelected(), NAB.getSelectedRow()))
                            NAB.savedShowWarningsTable[NAB.getSelectedRowIndex()] = event.getSource().isSelected()
                            NAB.configSaved = False
                            NAB.simulateTotalForRow()

                # ######################################################################################################
                if event.getActionCommand().lower().startswith("hideRowWhen".lower()):
                    if event.getSource().getName().lower().startswith("hideRowWhen".lower()):
                        hideWhenCodeSelected = GlobalVars.HIDE_ROW_WHEN_NEVER
                        if event.getSource().getName().lower() == "hideRowWhenAlways_JRB".lower() and event.getSource().isSelected():
                            hideWhenCodeSelected = GlobalVars.HIDE_ROW_WHEN_ALWAYS
                        elif event.getSource().getName().lower() == "hideRowWhenZeroOrX_JRB".lower() and event.getSource().isSelected():
                            hideWhenCodeSelected = GlobalVars.HIDE_ROW_WHEN_ZERO_OR_X
                        elif event.getSource().getName().lower() == "hideRowWhenLtEqZeroOrX_JRB".lower() and event.getSource().isSelected():
                            hideWhenCodeSelected = GlobalVars.HIDE_ROW_WHEN_NEGATIVE_OR_X
                        elif event.getSource().getName().lower() == "hideRowWhenGrEqZeroOrX_JRB".lower() and event.getSource().isSelected():
                            hideWhenCodeSelected = GlobalVars.HIDE_ROW_WHEN_POSITIVE_OR_X
                        elif event.getSource().getName().lower() == "hideRowWhenNotZeroOrX_JRB".lower() and event.getSource().isSelected():
                            hideWhenCodeSelected = GlobalVars.HIDE_ROW_WHEN_NOT_ZERO_OR_X

                        if NAB.savedHideRowWhenXXXTable[NAB.getSelectedRowIndex()] != hideWhenCodeSelected:
                            myPrint("DB", ".. setting savedHideRowWhenXXXTable to: %s for row: %s" %(hideWhenCodeSelected, NAB.getSelectedRow()))
                            NAB.savedHideRowWhenXXXTable[NAB.getSelectedRowIndex()] = hideWhenCodeSelected
                            NAB.configSaved = False
                            NAB.simulateTotalForRow()

                # ######################################################################################################
                if event.getActionCommand().lower().startswith("separatorSelector".lower()):
                    if event.getSource().getName().lower().startswith("separatorSelector".lower()):
                        rowSeparatorCodeSelected = GlobalVars.ROW_SEPARATOR_NEVER
                        if event.getSource().getName().lower() == "separatorSelectorAbove_JRB".lower() and event.getSource().isSelected():
                            rowSeparatorCodeSelected = GlobalVars.ROW_SEPARATOR_ABOVE
                        elif event.getSource().getName().lower() == "separatorSelectorBelow_JRB".lower() and event.getSource().isSelected():
                            rowSeparatorCodeSelected = GlobalVars.ROW_SEPARATOR_BELOW
                        elif event.getSource().getName().lower() == "separatorSelectorBoth_JRB".lower() and event.getSource().isSelected():
                            rowSeparatorCodeSelected = GlobalVars.ROW_SEPARATOR_BOTH

                        if NAB.savedRowSeparatorTable[NAB.getSelectedRowIndex()] != rowSeparatorCodeSelected:
                            myPrint("DB", ".. setting savedRowSeparatorTable to: %s for row: %s" %(rowSeparatorCodeSelected, NAB.getSelectedRow()))
                            NAB.savedRowSeparatorTable[NAB.getSelectedRowIndex()] = rowSeparatorCodeSelected
                            NAB.configSaved = False

                # ######################################################################################################
                if event.getActionCommand().lower().startswith("Blink".lower()):
                    if event.getSource().getName().lower() == "blinkRow_CB".lower():
                        if NAB.savedBlinkTable[NAB.getSelectedRowIndex()] != event.getSource().isSelected():
                            myPrint("DB", ".. setting savedBlinkTable to: %s for row: %s" %(event.getSource().isSelected(), NAB.getSelectedRow()))
                            NAB.savedBlinkTable[NAB.getSelectedRowIndex()] = event.getSource().isSelected()
                            NAB.configSaved = False
                            NAB.simulateTotalForRow()
                            NAB.jlst.repaint()

                # ######################################################################################################
                if event.getActionCommand().lower().startswith("Filter Out Zeros Inactive".lower()):
                    if event.getSource().getName().lower() == "filterOutZeroBalAccts_INACTIVE_CB".lower():
                        myPrint("DB", ".. setting filterOutZeroBalAccts_INACTIVE_CB to: %s for row: %s" %(event.getSource().isSelected(), NAB.getSelectedRow()))
                        NAB.searchFiltersUpdated()

                if event.getActionCommand().lower().startswith("Filter Out Zeros Active".lower()):
                    if event.getSource().getName().lower() == "filterOutZeroBalAccts_ACTIVE_CB".lower():
                        myPrint("DB", ".. setting filterOutZeroBalAccts_ACTIVE_CB to: %s for row: %s" %(event.getSource().isSelected(), NAB.getSelectedRow()))
                        NAB.searchFiltersUpdated()

                if event.getActionCommand().lower().startswith("Filter Include Selected".lower()):
                    if event.getSource().getName().lower() == "filterIncludeSelected_CB".lower():
                        myPrint("DB", ".. setting filterIncludeSelected_CB to: %s for row: %s" %(event.getSource().isSelected(), NAB.getSelectedRow()))
                        NAB.searchFiltersUpdated()

                if event.getActionCommand().lower().startswith("Only Show Selected".lower()):
                    if event.getSource().getName().lower() == "filterOnlyShowSelected_CB".lower():
                        myPrint("DB", ".. setting filterOnlyShowSelected_CB to: %s for row: %s" %(event.getSource().isSelected(), NAB.getSelectedRow()))
                        NAB.searchFiltersUpdated()

                if event.getActionCommand().lower().startswith("comboBoxChanged".lower()):

                    if event.getSource().getName().lower() == "includeInactive_COMBO".lower():
                        if NAB.savedIncludeInactive[NAB.getSelectedRowIndex()] != event.getSource().getSelectedIndex():
                            myPrint("DB", ".. setting savedIncludeInactive to: %s for row: %s" %(event.getSource().getSelectedIndex(), NAB.getSelectedRow()))
                            NAB.savedIncludeInactive[NAB.getSelectedRowIndex()] = event.getSource().getSelectedIndex()
                            NAB.setKeyLabel(NAB.getSelectedRowIndex())
                            # NAB.rebuildJList()
                            NAB.configSaved = False
                            NAB.searchFiltersUpdated()

                    if event.getSource().getName().lower() == "filterOnlyAccountType_COMBO".lower():
                        myPrint("DB", ".. setting filterOnlyAccountType_COMBO to: %s for row: %s" %(event.getSource().getSelectedItem(), NAB.getSelectedRow()))
                        NAB.searchFiltersUpdated()

                # ######################################################################################################
                if event.getActionCommand().lower().startswith("comboBoxChanged".lower()):

                    if event.getSource().getName().lower() == "balanceType_COMBO".lower():
                        if NAB.savedBalanceType[NAB.getSelectedRowIndex()] != event.getSource().getSelectedIndex():
                            myPrint("DB", ".. setting savedBalanceType to: %s for row: %s" %(event.getSource().getSelectedIndex(), NAB.getSelectedRow()))
                            NAB.savedBalanceType[NAB.getSelectedRowIndex()] = event.getSource().getSelectedIndex()
                            NAB.configSaved = False
                            NAB.setDateRangeLabel(NAB.getSelectedRowIndex())    # Balance option affects end date
                            NAB.searchFiltersUpdated()
                            NAB.getNAB().simulateTotalForRow()
                            NAB.getNAB().jlst.repaint()

                    if event.getSource().getName().lower() == "incomeExpenseDateRange_COMBO".lower():

                        lSetCustomDates = False
                        dr = None

                        if event.getSource().getSelectedItem().getDR().getResourceKey() == DateRangeOption.DR_CUSTOM_DATE.getResourceKey():
                            myPrint("DB", "User has selected Custom Date option....")

                            dateRanger = DateRangeChooser(NAB.moneydanceContext.getUI())
                            dateRanger.setOption(event.getSource().getSelectedItem().getDR().getResourceKey())

                            if isValidDateRange(NAB.savedCustomDatesTable[NAB.getSelectedRowIndex()][0],
                                                NAB.savedCustomDatesTable[NAB.getSelectedRowIndex()][1]):
                                dateRanger.setStartDate(NAB.savedCustomDatesTable[NAB.getSelectedRowIndex()][0])
                                dateRanger.setEndDate(NAB.savedCustomDatesTable[NAB.getSelectedRowIndex()][1])
                            else:
                                myPrint("DB", "... Invalid custom dates, reverting to defaults...")

                            tmpPanel = JPanel()
                            tmpPanel.add(dateRanger.getChoice())
                            tmpPanel.add(dateRanger.getStartField())
                            tmpPanel.add(dateRanger.getEndField())
                            options=["SAVE DATES","Cancel"]
                            if (JOptionPane.showOptionDialog(NAB.theFrame, tmpPanel, "Enter Custom Date Range:",
                                                             JOptionPane.OK_CANCEL_OPTION, JOptionPane.QUESTION_MESSAGE,
                                                             NAB.moneydanceContext.getUI().getIcon(GlobalVars.Strings.MD_GLYPH_APPICON_64),
                                                             options,
                                                             options[0])
                                    != 0):
                                myPrint("DB", "... User aborted entering new custom dates....")

                            else:
                                dr = dateRanger.getDateRange()
                                myPrint("DB", "... User entered dates:", dr)
                                lSetCustomDates = True

                        if (NAB.savedIncomeExpenseDateRange[NAB.getSelectedRowIndex()] != event.getSource().getSelectedItem().getDR().getResourceKey()
                                or lSetCustomDates):

                            # if (event.getSource().getSelectedItem().getDR().getResourceKey() != NAB.incomeExpenseDateRangeDefault()):
                            #     myPopupInformationBox(NAB.theFrame,
                            #                           theTitle="Inc/Exp Date Range",
                            #                           theMessage="ALERT: Custom date range scans all txns each time widget refreshes",
                            #                           theMessageType=JOptionPane.WARNING_MESSAGE)

                            myPrint("DB", ".. setting savedIncomeExpenseDateRange to: %s for row: %s" %(event.getSource().getSelectedItem().getDR().getResourceKey(), NAB.getSelectedRow()))
                            NAB.savedIncomeExpenseDateRange[NAB.getSelectedRowIndex()] = event.getSource().getSelectedItem().getDR().getResourceKey()

                            if lSetCustomDates:
                                NAB.savedCustomDatesTable[NAB.getSelectedRowIndex()][0] = dr.getStartDateInt()
                                NAB.savedCustomDatesTable[NAB.getSelectedRowIndex()][1] = dr.getEndDateInt()

                            NAB.configSaved = False
                            NAB.setParallelBalancesWarningLabel(NAB.getSelectedRowIndex())
                            NAB.setDateRangeLabel(NAB.getSelectedRowIndex())
                            NAB.rebuildParallelBalanceTable()

                    if event.getSource().getName().lower() == "currency_COMBO".lower():
                        selCur = event.getSource().getSelectedItem()
                        myPrint("DB", "selCur: %s" %(selCur))
                        if selCur.isBase:
                            selCurUUID = None
                        else:
                            selCurUUID = selCur.getUUID()
                        if NAB.savedCurrencyTable[NAB.getSelectedRowIndex()] != selCurUUID:
                            myPrint("DB", ".. setting savedCurrencyTable to: %s (%s) for row: %s" %(selCurUUID, selCur, NAB.getSelectedRow()))
                            NAB.savedCurrencyTable[NAB.getSelectedRowIndex()] = selCurUUID
                            NAB.configSaved = False
                            NAB.searchFiltersUpdated()
                            NAB.simulateTotalForRow()
                            NAB.jlst.repaint()

                    if event.getSource().getName().lower() == "rowSelected_COMBO".lower():
                        myPrint("DB", ".. setting selected row to configure to: %s" %(event.getSource().getSelectedIndex()+1))

                        NAB.storeJTextFieldsForSelectedRow()
                        NAB.rebuildFrameComponents(selectRowIndex=event.getSource().getSelectedIndex())

                # ######################################################################################################

                if event.getActionCommand().lower().startswith("Duplicate Row".lower()):
                    if myPopupAskQuestion(NAB.theFrame,"DUPLICATE ROW","Duplicate this row: %s (and insert) to new row: %s?" %(NAB.getSelectedRow(),NAB.getSelectedRow()+1)):
                        myPrint("DB", ".. duplicating row number %s" %(NAB.getSelectedRow()))

                        oldPos = NAB.getSelectedRowIndex()
                        newPos = oldPos+1

                        for obj in allRowVariables: obj.insert(newPos, copy.copy(obj[oldPos]))

                        NAB.rebuildFrameComponents(selectRowIndex=newPos)
                        NAB.configSaved = False

                if event.getActionCommand().lower().startswith("Insert Row before".lower()):
                    if myPopupAskQuestion(NAB.theFrame,"INSERT ROW","Insert a new row %s (before this row)?" %(NAB.getSelectedRow())):
                        myPrint("DB", ".. inserting a new row number %s (before)" %(NAB.getSelectedRow()))
                        NAB.savedAccountListUUIDs.insert(NAB.getSelectedRowIndex(),         NAB.accountListDefault())
                        NAB.savedBalanceType.insert(NAB.getSelectedRowIndex(),              NAB.balanceDefault())
                        NAB.savedIncomeExpenseDateRange.insert(NAB.getSelectedRowIndex(),   NAB.incomeExpenseDateRangeDefault())
                        NAB.savedCustomDatesTable.insert(NAB.getSelectedRowIndex(),         NAB.customDatesDefault())
                        NAB.savedRowSeparatorTable.insert(NAB.getSelectedRowIndex(),        NAB.rowSeparatorDefault())
                        NAB.savedBlinkTable.insert(NAB.getSelectedRowIndex(),               NAB.blinkDefault())
                        NAB.savedAutoSumAccounts.insert(NAB.getSelectedRowIndex(),          NAB.autoSumDefault())
                        NAB.savedWidgetName.insert(NAB.getSelectedRowIndex(),               NAB.widgetRowDefault())
                        NAB.savedCurrencyTable.insert(NAB.getSelectedRowIndex(),            NAB.currencyDefault())
                        NAB.savedDisableCurrencyFormatting.insert(NAB.getSelectedRowIndex(),NAB.disableCurrencyFormattingDefault())
                        NAB.savedIncludeInactive.insert(NAB.getSelectedRowIndex(),          NAB.includeInactiveDefault())
                        NAB.savedShowWarningsTable.insert(NAB.getSelectedRowIndex(),        NAB.showWarningsDefault())
                        NAB.savedHideRowWhenXXXTable.insert(NAB.getSelectedRowIndex(),      NAB.hideRowWhenXXXDefault())
                        NAB.savedHideRowXValueTable.insert(NAB.getSelectedRowIndex(),       NAB.hideRowXValueDefault())
                        NAB.savedDisplayAverageTable.insert(NAB.getSelectedRowIndex(),      NAB.displayAverageDefault())

                        NAB.rebuildFrameComponents(selectRowIndex=NAB.getSelectedRowIndex())
                        NAB.configSaved = False

                if event.getActionCommand().lower().startswith("Insert Row after".lower()):
                    if myPopupAskQuestion(NAB.theFrame,"INSERT ROW","Insert a new row %s (after this row)?" %(NAB.getSelectedRow()+1)):
                        myPrint("DB", ".. inserting a new row number %s (after)" %(NAB.getSelectedRow()+1))

                        NAB.savedAccountListUUIDs.insert(NAB.getSelectedRowIndex()+1,           NAB.accountListDefault())
                        NAB.savedBalanceType.insert(NAB.getSelectedRowIndex()+1,                NAB.balanceDefault())
                        NAB.savedIncomeExpenseDateRange.insert(NAB.getSelectedRowIndex()+1,     NAB.incomeExpenseDateRangeDefault())
                        NAB.savedCustomDatesTable.insert(NAB.getSelectedRowIndex()+1,           NAB.customDatesDefault())
                        NAB.savedRowSeparatorTable.insert(NAB.getSelectedRowIndex()+1,          NAB.rowSeparatorDefault())
                        NAB.savedBlinkTable.insert(NAB.getSelectedRowIndex()+1,                 NAB.blinkDefault())
                        NAB.savedAutoSumAccounts.insert(NAB.getSelectedRowIndex()+1,            NAB.autoSumDefault())
                        NAB.savedWidgetName.insert(NAB.getSelectedRowIndex()+1,                 NAB.widgetRowDefault())
                        NAB.savedCurrencyTable.insert(NAB.getSelectedRowIndex()+1,              NAB.currencyDefault())
                        NAB.savedDisableCurrencyFormatting.insert(NAB.getSelectedRowIndex()+1,  NAB.disableCurrencyFormattingDefault())
                        NAB.savedIncludeInactive.insert(NAB.getSelectedRowIndex()+1,            NAB.includeInactiveDefault())
                        NAB.savedShowWarningsTable.insert(NAB.getSelectedRowIndex()+1,          NAB.showWarningsDefault())
                        NAB.savedHideRowWhenXXXTable.insert(NAB.getSelectedRowIndex()+1,        NAB.hideRowWhenXXXDefault())
                        NAB.savedHideRowXValueTable.insert(NAB.getSelectedRowIndex()+1,         NAB.hideRowXValueDefault())
                        NAB.savedDisplayAverageTable.insert(NAB.getSelectedRowIndex()+1,        NAB.displayAverageDefault())

                        NAB.rebuildFrameComponents(selectRowIndex=NAB.getSelectedRowIndex()+1)
                        NAB.configSaved = False

                if event.getActionCommand().lower().startswith("Delete Row".lower()):
                    if myPopupAskQuestion(NAB.theFrame,"DELETE ROW","Delete row: %s from Home Page Widget?" %(NAB.getSelectedRow())):
                        myPrint("DB", ".. deleting row: %s" %(NAB.getSelectedRow()))

                        if NAB.getNumberOfRows() <= 1:
                            NAB.resetParameters(lJustRowSettings=True)
                        else:
                            for obj in allRowVariables: del obj[NAB.getSelectedRowIndex()]

                        NAB.rebuildFrameComponents(selectRowIndex=(min(NAB.getSelectedRowIndex(), NAB.getNumberOfRows()-1)))
                        NAB.configSaved = False

                if event.getActionCommand().lower().startswith("Move Row".lower()):
                    if NAB.getNumberOfRows() < 2:
                        myPopupInformationBox(NAB.theFrame,"Not enough rows to move!",theMessageType=JOptionPane.WARNING_MESSAGE)
                    else:
                        newPosition = myPopupAskForInput(NAB.theFrame,
                                                         "MOVE ROW",
                                                         "New row position:",
                                                         "Enter the new row position (currently %s, max %s)" %(NAB.getSelectedRow(), NAB.getNumberOfRows()),
                                                         defaultValue=None)
                        if newPosition and StringUtils.isInteger(newPosition):
                            newPosition = int(newPosition)
                            if newPosition >= 1 and newPosition <= NAB.getNumberOfRows() and newPosition != NAB.getSelectedRow():
                                myPrint("DB", ".. moving row from position/row %s to position/row %s" %(NAB.getSelectedRow(), newPosition))

                                oldPos = NAB.getSelectedRowIndex()
                                newPos = newPosition-1

                                for obj in allRowVariables: obj.insert(newPos, obj.pop(oldPos))

                                NAB.rebuildFrameComponents(selectRowIndex=newPos)
                                NAB.configSaved = False
                            else:
                                myPrint("B", "User entered an invalid new row position (%s) to move from (%s) - no action taken" %(newPosition, NAB.getSelectedRow()))
                        else:
                            myPrint("B", "User did not enter a valid new row position - no action taken")
                # ######################################################################################################

                if event.getActionCommand().lower().startswith("Reset".lower()):
                    if myPopupAskQuestion(NAB.theFrame,"RESET","Wipe all saved settings & reset to defaults with one row?"):
                        myPrint("DB", ".. RESET: Wiping all saved settings and resetting to defaults with one row")

                        NAB.resetParameters()
                        NAB.rebuildFrameComponents(selectRowIndex=0)

                        NAB.configSaved = False

                # ######################################################################################################
                if event.getActionCommand().lower().startswith("reload"):
                    myPrint("DB", "Dumping changes and reloading saved settings")
                    NAB.load_saved_parameters(lForceReload=True)
                    NAB.rebuildFrameComponents(selectRowIndex=0)
                    NAB.updateMenus()

                # ######################################################################################################
                if event.getActionCommand().lower().startswith("save"):

                    # Buttons auto-save themselves
                    NAB.storeJTextFieldsForSelectedRow()
                    NAB.storeCurrentJListSelected()

                    if NAB.savedWidgetName[NAB.getSelectedRowIndex()].strip() == "":
                        NAB.savedWidgetName[NAB.getSelectedRowIndex()] = NAB.widgetRowDefault()

                    NAB.configPanelOpen = False
                    NAB.theFrame.setVisible(False)    # Listener, so already on Swing EDT

                    lShouldRefreshHomeScreenWidget = True
                    lShouldSaveParameters = True

                # ######################################################################################################
                if event.getActionCommand().lower().startswith("clear"):
                    myPrint("DB", "...clearing account list selection...")
                    NAB.jlst.clearSelection()

                # ######################################################################################################
                if event.getActionCommand().lower().startswith("store"):
                    myPrint("DB", "...storing account list selection into memory...")
                    NAB.migratedParameters = False
                    NAB.storeCurrentJListSelected()
                    NAB.configSaved = False
                    NAB.simulateTotalForRow()

                # ######################################################################################################
                if event.getActionCommand().lower().startswith("undo"):
                    myPrint("DB", "...undoing account list selection changes and reverting to previously saved account list")
                    NAB.rebuildJList()

                # ######################################################################################################
                if event.getActionCommand().lower().startswith("debug"):
                    if debug:
                        myPrint("B", "User has DISABLED debug mode.......")
                    else:
                        myPrint("B", "User has ENABLED debug mode.......")

                    debug = not debug
                    NAB.menuItemDEBUG.setSelected(debug)

                # ######################################################################################################
                if event.getActionCommand().lower().startswith("AutoSum Default".lower()):
                    NAB.savedAutoSumDefault = not NAB.savedAutoSumDefault
                    NAB.menuItemAutoSumDefault.setSelected(NAB.savedAutoSumDefault)
                    NAB.configSaved = False
                    myPrint("B", "User has changed 'AutoSum Default for new rows' to: %s" %(NAB.savedAutoSumDefault))

                # ######################################################################################################
                if event.getActionCommand().lower().startswith("Show Dashes".lower()):
                    NAB.savedShowDashesInsteadOfZeros = not NAB.savedShowDashesInsteadOfZeros
                    NAB.menuItemShowDashesInsteadOfZeros.setSelected(NAB.savedShowDashesInsteadOfZeros)
                    NAB.simulateTotalForRow()
                    NAB.jlst.repaint()
                    NAB.configSaved = False
                    myPrint("B", "User has changed 'Show Dashes instead of Zeros' to: %s" %(NAB.savedShowDashesInsteadOfZeros))

                # ######################################################################################################
                if event.getActionCommand().lower().startswith("Use Indian number format".lower()):
                    NAB.savedUseIndianNumberFormat = not NAB.savedUseIndianNumberFormat
                    NAB.menuItemUseIndianNumberFormat.setSelected(NAB.savedUseIndianNumberFormat)
                    NAB.simulateTotalForRow()
                    NAB.jlst.repaint()
                    NAB.configSaved = False
                    myPrint("B", "User has changed 'Use Indian number format' to: %s" %(NAB.savedUseIndianNumberFormat))

                # ######################################################################################################
                if event.getActionCommand().lower().startswith("Hide Decimal places".lower()):
                    NAB.savedHideDecimals = not NAB.savedHideDecimals
                    NAB.menuItemHideDecimals.setSelected(NAB.savedHideDecimals)
                    NAB.simulateTotalForRow()
                    NAB.jlst.repaint()
                    NAB.configSaved = False
                    myPrint("B", "User has changed 'Hide Decimal places' to: %s" %(NAB.savedHideDecimals))

                # ######################################################################################################
                if event.getActionCommand().lower().startswith("Display underline dots".lower()):
                    NAB.savedDisplayVisualUnderDots = not NAB.savedDisplayVisualUnderDots
                    NAB.menuDisplayVisualUnderDots.setSelected(NAB.savedDisplayVisualUnderDots)
                    NAB.simulateTotalForRow()
                    NAB.jlst.repaint()
                    NAB.configSaved = False
                    myPrint("B", "User has changed 'Display underline dots' to: %s" %(NAB.savedDisplayVisualUnderDots))

                # ######################################################################################################
                if event.getActionCommand().lower().startswith("Disable Widget Title".lower()):
                    NAB.savedDisableWidgetTitle = not NAB.savedDisableWidgetTitle
                    NAB.menuItemDisableWidgetTitle.setSelected(NAB.savedDisableWidgetTitle)
                    NAB.configSaved = False
                    myPrint("B", "User has changed 'Disable Widget Title' to: %s" %(NAB.savedDisableWidgetTitle))

                # ######################################################################################################
                if event.getActionCommand().lower().startswith("Treat Securities".lower()):
                    NAB.savedTreatSecZeroBalInactive = not NAB.savedTreatSecZeroBalInactive
                    NAB.menuItemTreatSecZeroBalInactive.setSelected(NAB.savedTreatSecZeroBalInactive)

                    # NAB.rebuildJList()
                    NAB.searchFiltersUpdated()
                    NAB.configSaved = False
                    myPrint("B", "User has changed 'Treat Securities With Zero Balance as Inactive' to: %s" %(NAB.savedTreatSecZeroBalInactive))

                # ######################################################################################################
                if event.getActionCommand().lower().startswith("Hide Controls".lower()):
                    NAB.savedHideControlPanel = not NAB.savedHideControlPanel
                    NAB.menuBarItemHideControlPanel_CB.setSelected(NAB.savedHideControlPanel)

                    hideUnideCollapsiblePanels(NAB.theFrame, not NAB.savedHideControlPanel)
                    myPrint("DB", "User has changed 'Hide Control Panel' to: %s" %(NAB.savedHideControlPanel))

                # ######################################################################################################
                if event.getActionCommand().lower().startswith("deactivate"):

                    myPrint("DB", "User has clicked deactivate - sending 'close' request via .showURL().......")
                    NAB.moneydanceContext.showURL("moneydance:fmodule:%s:%s:customevent:close" %(NAB.myModuleID,NAB.myModuleID))

                # ######################################################################################################
                if event.getActionCommand().lower().startswith("uninstall"):

                    myPrint("DB", "User has clicked uninstall - sending 'uninstall' request via .showURL().......")
                    NAB.moneydanceContext.showURL("moneydance:fmodule:%s:%s:customevent:uninstall" %(NAB.myModuleID,NAB.myModuleID))

                # ######################################################################################################
                if lShouldRefreshHomeScreenWidget:
                    NAB.executeRefresh()

                # ######################################################################################################
                if lShouldSaveParameters:
                    NAB.saveSettings()

                # ######################################################################################################

                myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

        class MyJListRenderer(DefaultListCellRenderer):     # Reference: com.moneydance.apps.md.view.gui.AccountTreeCellRenderer

            def __init__(self):

                self.coord_x = None
                self.coord_y = None
                self.coord_w = None
                self.coord_h = None
                self.INITIAL_SHIFT = 12
                self.leftMargin = self.INITIAL_SHIFT
                self.imageHeight = 24
                self.preferredHeight = 38
                self.smallFont = None
                self.defaultFont = None
                self.valueWidth = None
                self.defaultValue = ("0"*15)

                self.drawAcctType = True
                self.fillAllSpace = False
                self.nullEntryLabel = ""
                self.nullEntryColor = None
                self.paintIcons = True

                self.showFullAccountName = False
                self.acctDepthIncrement = 14
                self.showCurrency = False
                self.includeInactive = None
                self.sudoAccountHoldBalanceObj = None

                self.isAllIncExpDatesSelected = True
                self.hasInactiveChildren = False
                self.isSelected = False
                self.account = None
                self.isAccountActive = None
                self.incomeExpenseFlag = None
                self.listItem = None
                self.acctName = None
                self.acctType = None
                self.acctDepth = 0
                self.acctSubAcctCount = 0
                self.userXBalance = None
                self.userXBalanceStr = None
                self.recursiveUserXBalance = None
                self.recursiveUserXBalanceStr = None
                self.isParallelBalance = False
                self.hasDisabledCurrencyFormatting = False

                self.mdImages = NetAccountBalancesExtension.getNAB().moneydanceContext.getUI().getImages()

                super(self.__class__, self).__init__()

            def setNullEntryLabel(self, nullEntryLabel):self.nullEntryLabel = nullEntryLabel
            def setNullEntryColor(self, nullEntryColor): self.nullEntryColor = nullEntryColor

            def initFont(self, font):
                if self.defaultFont is None:
                    self.defaultFont = UIManager.getFont("Label.font")
                    if self.defaultFont is None:
                        self.defaultFont = font
                    self.preferredHeight = Math.max(self.imageHeight, self.getFontMetrics(self.defaultFont).getHeight()) + 14
                    self.smallFont = self.defaultFont.deriveFont(0, (self.defaultFont.getSize() - 1))
                    self.valueWidth = self.getFontMetrics(self.defaultFont).stringWidth(self.defaultValue)

            def getPreferredSize(self):
                self.initFont(self.getFont())
                return Dimension(500 if self.fillAllSpace else (300 if self.drawAcctType else 100), self.preferredHeight)

            def getMinimumSize(self):
                return Dimension(500 if self.fillAllSpace else 50, self.preferredHeight)

            def setBounds(self, coord_x, coord_y, coord_w, coord_h):
                super(self.__class__, self).setBounds(coord_x, coord_y, coord_w, coord_h)
                self.coord_w = coord_w
                self.coord_h = coord_h

            def updateUI(self):
                self.defaultFont = None
                self.smallFont = None
                super(self.__class__, self).updateUI()

            def setFillAllSpace(self, fillAllSpace):                self.fillAllSpace = fillAllSpace
            def setPaintIcons(self, paintIcons):                    self.paintIcons = paintIcons
            def setDrawAccountTypes(self, drawThem):                self.drawAcctType = drawThem
            def setOverrideBackground(self, bgcolor):               self.setBackground(bgcolor)
            def setOverrideForeground(self, fgcolor):               self.setForeground(fgcolor)
            def setShowFullAccountName(self, showFullAccountName):  self.showFullAccountName = showFullAccountName
            def setShowCurrency(self, showCurrency):                self.showCurrency = showCurrency
            def setAcctDepthIncrement(self, acctDepthIncrement):    self.acctDepthIncrement = acctDepthIncrement

            def getListCellRendererComponent(self, thelist, value, index, isSelected, cellHasFocus):
                c = super(self.__class__, self).getListCellRendererComponent(thelist, value, index, isSelected, cellHasFocus)

                md = NetAccountBalancesExtension.getNAB().moneydanceContext
                baseCurr = md.getCurrentAccountBook().getCurrencies().getBaseType()

                NAB = NetAccountBalancesExtension.getNAB()

                self.listItem = value
                if isinstance(self.listItem, StoreAccountList) and isinstance(self.listItem.getAccount(), Account):
                    self.account = self.listItem.getAccount()
                    self.acctDepth = self.account.getDepth()
                    self.acctSubAcctCount = self.account.getSubAccountCount()
                    self.acctName = self.account.getFullAccountName() if self.showFullAccountName else self.account.getAccountName()
                    self.acctType = NAB.moneydanceContext.getUI().getResources().getShortAccountType(self.account.getAccountType())
                    self.isAllIncExpDatesSelected = isIncomeExpenseAllDatesSelected(NAB.getSelectedRowIndex())

                    if self.isAllIncExpDatesSelected or not isIncomeExpenseAcct((self.account)):
                        self.isParallelBalance = False
                        self.sudoAccountHoldBalanceObj = self.account
                        self.isAccountActive = isAccountActive(self.account, NAB.savedBalanceType[NAB.getSelectedRowIndex()])
                        self.hasInactiveChildren = accountIncludesInactiveChildren(self.account, NAB.savedBalanceType[NAB.getSelectedRowIndex()])
                    else:
                        self.isParallelBalance = True
                        if NAB.isParallelRebuildRunning_NOLOCKFIRST():
                            self.sudoAccountHoldBalanceObj = self.account   # Temporarily switch to Account whilst rebuild running...
                        else:
                            try:
                                self.sudoAccountHoldBalanceObj = NAB.jlst.parallelAccountBalances[NAB.getSelectedRowIndex()][self.account]
                            except KeyError:
                                myPrint("B", "-------------------")
                                myPrint("B", "@@ KeyError accessing parallel balances on RowInd: %s (Acct: '%s')- REPORT TO DEVELOPER - WHAT WERE YOU DOING? @@" %(NAB.getSelectedRowIndex(), self.account))
                                myPrint("B", "@@ parallelAccountBalances[%s] contains:" %(NAB.getSelectedRowIndex()), NAB.jlst.parallelAccountBalances[NAB.getSelectedRowIndex()])
                                myPrint("B", "-------------------")
                                raise

                        self.isAccountActive = isAccountActive(self.account, NAB.savedBalanceType[NAB.getSelectedRowIndex()], sudoAccount=self.sudoAccountHoldBalanceObj)
                        self.hasInactiveChildren = accountIncludesInactiveChildren(self.account, NAB.savedBalanceType[NAB.getSelectedRowIndex()], sudoAccount=self.sudoAccountHoldBalanceObj)

                    acctCurr = self.account.getCurrencyType()
                    balType = NAB.savedBalanceType[NAB.getSelectedRowIndex()]
                    thisRowCurr = MyHomePageView.getCurrencyByUUID(NAB.savedCurrencyTable[NAB.getSelectedRowIndex()], baseCurr)

                    self.includeInactive = NAB.savedIncludeInactive[NAB.getSelectedRowIndex()]
                    self.hasDisabledCurrencyFormatting = NAB.savedDisableCurrencyFormatting[NAB.getSelectedRowIndex()]

                    mult = 1
                    # noinspection PyUnresolvedReferences
                    if self.account.getAccountType() == Account.AccountType.INCOME:
                        self.incomeExpenseFlag = "I"
                    elif self.account.getAccountType() == Account.AccountType.EXPENSE:
                        self.incomeExpenseFlag = "E"
                        mult = -1
                    else:
                        self.incomeExpenseFlag = ""

                    self.userXBalance = StoreAccountList.getUserXBalance(balType, self.sudoAccountHoldBalanceObj) * mult
                    if not NAB.savedShowDashesInsteadOfZeros or self.userXBalance:
                        if self.userXBalance != 0 and acctCurr != thisRowCurr:
                            self.userXBalance = CurrencyUtil.convertValue(self.userXBalance, acctCurr, thisRowCurr)


                        # self.userXBalanceStr = (thisRowCurr.formatFancy(self.userXBalance, NAB.decimal) if (not self.hasDisabledCurrencyFormatting)
                        #                         else thisRowCurr.formatSemiFancy(self.userXBalance, NAB.decimal))

                        self.userXBalanceStr = formatFancy(thisRowCurr, self.userXBalance, NAB.decimal, fancy=(not self.hasDisabledCurrencyFormatting), indianFormat=NAB.savedUseIndianNumberFormat)
                    else:
                        self.userXBalanceStr = "-"

                    if NAB.isParallelRebuildRunning_NOLOCKFIRST(): self.userXBalanceStr = "<rebuilding>"

                    if self.acctSubAcctCount > 0:
                        self.recursiveUserXBalance = StoreAccountList.getRecursiveUserXBalance(balType, self.sudoAccountHoldBalanceObj) * mult
                        if not NAB.savedShowDashesInsteadOfZeros or self.recursiveUserXBalance:
                            if self.recursiveUserXBalance != 0 and acctCurr != thisRowCurr:
                                self.recursiveUserXBalance = CurrencyUtil.convertValue(self.recursiveUserXBalance, acctCurr, thisRowCurr)

                            # self.recursiveUserXBalanceStr = (thisRowCurr.formatFancy(self.recursiveUserXBalance, NAB.decimal) if (not self.hasDisabledCurrencyFormatting)
                            #                                  else thisRowCurr.formatSemiFancy(self.recursiveUserXBalance, NAB.decimal))

                            self.recursiveUserXBalanceStr = formatFancy(thisRowCurr, self.recursiveUserXBalance, NAB.decimal, fancy=(not self.hasDisabledCurrencyFormatting), indianFormat=NAB.savedUseIndianNumberFormat)
                        else:
                            self.recursiveUserXBalanceStr = "-"
                    else:
                        self.recursiveUserXBalance = 0
                        self.recursiveUserXBalanceStr = ""

                    if NAB.isParallelRebuildRunning_NOLOCKFIRST(): self.recursiveUserXBalanceStr = "<rebuilding>"

                else:
                    self.account = None
                    self.acctDepth = 0
                    self.acctSubAcctCount = 0
                    self.acctName = safeStr(self.listItem)
                    self.acctType = ""
                    self.isAccountActive = None
                    self.isAllIncExpDatesSelected = True
                    self.sudoAccountHoldBalanceObj = None
                    self.isParallelBalance = False
                    self.hasDisabledCurrencyFormatting = False

                    self.userXBalance = 0
                    self.userXBalanceStr = ""
                    self.recursiveUserXBalance = 0
                    self.recursiveUserXBalanceStr = ""

                self.isSelected = isSelected

                # Create a line separator between accounts
                c.setBorder(BorderFactory.createMatteBorder(0, 0, 1, 0, NAB.moneydanceContext.getUI().colors.headerBorder))

                return c

            # com.moneydance.apps.md.view.gui.AccountTreeCellRenderer
            def paintComponent(self, g2d):

                if g2d is None: return

                md = NetAccountBalancesExtension.getNAB().moneydanceContext

                g2d.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING, RenderingHints.VALUE_TEXT_ANTIALIAS_ON)
                self.initFont(g2d.getFont())
                fm = g2d.getFontMetrics()
                textheight = fm.getMaxAscent()
                texty = self.coord_h / 2 + textheight / 2

                bg = (md.getUI().colors.sidebarSelectedBG if self.isSelected else md.getUI().colors.defaultBackground)
                if self.isSelected:
                    fg = md.getUI().colors.sidebarSelectedFG
                    altFG = md.getUI().colors.sidebarSelectedFG                                                         # noqa
                else:
                    fg = md.getUI().colors.defaultTextForeground
                    altFG = md.getUI().colors.tertiaryTextFG                                                            # noqa

                g2d.setColor(bg)
                g2d.fillRect(0, 0, self.coord_w, self.coord_h)
                g2d.setColor(fg)

                if self.account is None:
                    if self.listItem is None:
                        label = self.nullEntryLabel
                    elif isinstance(self.listItem, Account):
                        label = self.listItem.getFullAccountName() if self.showFullAccountName else self.listItem.getAccountName()
                    else:
                        label = safeStr(self.listItem)
                    g2d.drawString(label, self.INITIAL_SHIFT, texty)
                    return

                xshift = self.INITIAL_SHIFT if self.showFullAccountName else (12 + Math.max(self.acctDepth - 1, 0) * self.acctDepthIncrement)
                x_right_shift = 12

                iconPathAccount = MDImages.getIconPathForAccountType(self.account.getAccountType())
                iconTintAccount = md.getUI().colors.sidebarSelectedFG if self.isSelected else self.mdImages.getIconTintForAccountType(self.account.getAccountType())
                iconTintInactive = md.getUI().colors.sidebarSelectedFG if self.isSelected else md.getUI().colors.errorMessageForeground

                iconAccount = self.mdImages.getIconWithColor(iconPathAccount, iconTintAccount)

                # iconInactive = (self.mdImages.getIconWithColor(MDImages.GRIP_VERTICAL, iconTintInactive) if (not self.isParallelBalance and not self.includeInactive and self.hasInactiveChildren) else None)
                iconInactive = (self.mdImages.getIconWithColor(MDImages.GRIP_VERTICAL, iconTintInactive) if (not self.includeInactive and self.hasInactiveChildren) else None)

                if self.account is not None:
                    if not self.isAccountActive:
                        if self.isSelected:
                            fg = md.getUI().colors.sidebarSelectedFG
                        else:
                            # fg = md.getUI().colors.secondaryTextFG
                            fg = md.getUI().colors.tertiaryTextFG
                        g2d.setColor(fg)

                    g2d.setFont(self.smallFont if self.account.getDepth() > 1 else self.defaultFont)
                    if not self.isAccountActive: g2d.setFont(g2d.getFont().deriveFont(Font.ITALIC))

                fm = g2d.getFontMetrics()
                textheight = fm.getMaxAscent()
                texty = self.coord_h / 2 + textheight / 2
                if iconAccount is not None and self.paintIcons:
                    iconAccount.paintIcon(self, g2d, xshift, (self.coord_h - iconAccount.getIconHeight()) / 2)
                    xshift += iconAccount.getIconWidth() + 5

                if iconInactive is not None and self.paintIcons:
                    iconInactive.paintIcon(self, g2d, self.coord_w - x_right_shift, (self.coord_h - iconInactive.getIconHeight()) / 2)

                oldClip = g2d.getClip()                                                                                 # noqa

                balText = self.userXBalanceStr
                recurBalText = self.recursiveUserXBalanceStr

                flagWidth = 0
                if self.incomeExpenseFlag:
                    # g2d.setPaint(altFG)
                    flagWidth = fm.stringWidth(self.incomeExpenseFlag)
                    g2d.drawString(self.incomeExpenseFlag, self.coord_w - x_right_shift - (self.valueWidth * 2) - flagWidth - self.INITIAL_SHIFT, texty)
                    # g2d.setPaint(fg)

                if balText is not None:
                    # g2d.setPaint(altFG)
                    balWidth = fm.stringWidth(balText)
                    g2d.drawString(balText, self.coord_w - x_right_shift - (self.valueWidth * 1) - balWidth - self.INITIAL_SHIFT, texty)
                    # g2d.setPaint(fg)

                if recurBalText is not None:
                    balWidth = fm.stringWidth(recurBalText)
                    g2d.drawString(recurBalText, self.coord_w - x_right_shift - (self.valueWidth * 0) - balWidth - self.INITIAL_SHIFT, texty)

                g2d.clipRect(0, 0, self.coord_w - x_right_shift - (self.valueWidth * 2) - flagWidth - self.INITIAL_SHIFT - 2, self.coord_h)
                g2d.drawString(self.acctName, xshift, texty)
                g2d.dispose()

        def load_saved_parameters(self, lForceReload=False):
            myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()")
            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
            myPrint("DB", "... parametersLoaded: %s .getCurrentAccountBook(): %s" %(self.parametersLoaded, self.moneydanceContext.getCurrentAccountBook()))

            with self.NAB_LOCK:
                if not self.parametersLoaded or lForceReload:
                    if self.moneydanceContext.getCurrentAccountBook() is None:
                        myPrint("DB", "... getCurrentAccountBook() reports None - skipping parameter load...")
                    else:
                        # self.configPanelOpen = False

                        self.resetParameters()

                        GlobalVars.extn_param_NEW_listAccountUUIDs_NAB              = [self.accountListDefault()]                # Loading will overwrite if saved, else pre-load defaults
                        GlobalVars.extn_param_NEW_balanceType_NAB                   = [self.balanceDefault()]                    # Loading will overwrite if saved, else pre-load defaults
                        GlobalVars.extn_param_NEW_widget_display_name_NAB           = [self.widgetRowDefault()]                  # Loading will overwrite if saved, else pre-load defaults

                        GlobalVars.extn_param_NEW_currency_NAB                      = [self.currencyDefault()]                   # Loading will overwrite if saved, else pre-load defaults
                        GlobalVars.extn_param_NEW_disableCurrencyFormatting_NAB     = [self.disableCurrencyFormattingDefault()]  # Loading will overwrite if saved, else pre-load defaults
                        GlobalVars.extn_param_NEW_includeInactive_NAB               = [self.includeInactiveDefault()]            # Loading will overwrite if saved, else pre-load defaults
                        GlobalVars.extn_param_NEW_autoSumAccounts_NAB               = [self.autoSumDefault()]                    # Loading will overwrite if saved, else pre-load defaults
                        GlobalVars.extn_param_NEW_incomeExpenseDateRange_NAB        = [self.incomeExpenseDateRangeDefault()]     # Loading will overwrite if saved, else pre-load defaults
                        GlobalVars.extn_param_NEW_customDatesTable_NAB              = [self.customDatesDefault()]                # Loading will overwrite if saved, else pre-load defaults
                        GlobalVars.extn_param_NEW_rowSeparatorTable_NAB             = [self.rowSeparatorDefault()]               # Loading will overwrite if saved, else pre-load defaults
                        GlobalVars.extn_param_NEW_blinkTable_NAB                    = [self.blinkDefault()]                      # Loading will overwrite if saved, else pre-load defaults
                        GlobalVars.extn_param_NEW_showWarningsTable_NAB             = [self.showWarningsDefault()]               # Loading will overwrite if saved, else pre-load defaults
                        GlobalVars.extn_param_NEW_hideRowWhenXXXTable_NAB           = [self.hideRowWhenXXXDefault()]             # Loading will overwrite if saved, else pre-load defaults
                        GlobalVars.extn_param_NEW_hideRowXValueTable_NAB            = [self.hideRowXValueDefault()]              # Loading will overwrite if saved, else pre-load defaults
                        GlobalVars.extn_param_NEW_displayAverageTable_NAB           = [self.displayAverageDefault()]             # Loading will overwrite if saved, else pre-load defaults

                        GlobalVars.extn_param_NEW_autoSumDefault_NAB                = self.autoSumDefault()                      # Loading will overwrite if saved, else pre-load defaults
                        GlobalVars.extn_param_NEW_disableWidgetTitle_NAB            = self.disableWidgetTitleDefault()           # Loading will overwrite if saved, else pre-load defaults
                        GlobalVars.extn_param_NEW_showDashesInsteadOfZeros_NAB      = self.showDashesInsteadOfZerosDefault()     # Loading will overwrite if saved, else pre-load defaults
                        GlobalVars.extn_param_NEW_treatSecZeroBalInactive_NAB       = self.treatSecZeroBalInactiveDefault()      # Loading will overwrite if saved, else pre-load defaults

                        GlobalVars.extn_param_NEW_useIndianNumberFormat_NAB         = self.useIndianNumberFormatDefault()        # Loading will overwrite if saved, else pre-load defaults
                        GlobalVars.extn_param_NEW_hideDecimals_NAB                  = self.hideDecimalsDefault()                 # Loading will overwrite if saved, else pre-load defaults
                        GlobalVars.extn_param_NEW_displayVisualUnderDots_NAB        = self.displayVisualUnderDotsDefault()       # Loading will overwrite if saved, else pre-load defaults

                        GlobalVars.extn_param_NEW_expandedView_NAB                  = self.expandedViewDefault()                 # Loading will overwrite if saved, else pre-load defaults

                        get_StuWareSoftSystems_parameters_from_file(myFile="%s_extension.dict" %(self.myModuleID))

                        # Migrate parameters from old to new multi-row format....
                        if ((GlobalVars.extn_param_listAccountUUIDs_NAB is not None and len(GlobalVars.extn_param_listAccountUUIDs_NAB) > 0)
                                and (len(GlobalVars.extn_param_NEW_listAccountUUIDs_NAB[0]) < 1)):
                            myPrint("B", "MIGRATING OLD PARAMETERS TO NEW MULTI-ROW PARAMETERS (and adding new parameters as defaults)")

                            self.migratedParameters = True
                            GlobalVars.extn_param_NEW_listAccountUUIDs_NAB          = [GlobalVars.extn_param_listAccountUUIDs_NAB]
                            GlobalVars.extn_param_NEW_balanceType_NAB               = [GlobalVars.extn_param_balanceType_NAB]
                            GlobalVars.extn_param_NEW_widget_display_name_NAB       = [GlobalVars.extn_param_widget_display_name_NAB]

                            GlobalVars.extn_param_NEW_currency_NAB                  = [self.currencyDefault()]                   # Did not exist previously
                            GlobalVars.extn_param_NEW_disableCurrencyFormatting_NAB = [self.disableCurrencyFormattingDefault()]  # Loading will overwrite if saved, else pre-load defaults
                            GlobalVars.extn_param_NEW_includeInactive_NAB           = [self.includeInactiveDefault()]            # Did not exist previously
                            GlobalVars.extn_param_NEW_autoSumAccounts_NAB           = [self.autoSumDefault()]                    # Did not exist previously
                            GlobalVars.extn_param_NEW_incomeExpenseDateRange_NAB    = [self.incomeExpenseDateRangeDefault()]     # Did not exist previously
                            GlobalVars.extn_param_NEW_customDatesTable_NAB          = [self.customDatesDefault()]                # Loading will overwrite if saved, else pre-load defaults
                            GlobalVars.extn_param_NEW_rowSeparatorTable_NAB         = [self.rowSeparatorDefault()]               # Loading will overwrite if saved, else pre-load defaults
                            GlobalVars.extn_param_NEW_blinkTable_NAB                = [self.blinkDefault()]                      # Loading will overwrite if saved, else pre-load defaults
                            GlobalVars.extn_param_NEW_showWarningsTable_NAB         = [self.showWarningsDefault()]               # Loading will overwrite if saved, else pre-load defaults
                            GlobalVars.extn_param_NEW_hideRowWhenXXXTable_NAB       = [self.hideRowWhenXXXDefault()]             # Loading will overwrite if saved, else pre-load defaults
                            GlobalVars.extn_param_NEW_hideRowXValueTable_NAB        = [self.hideRowXValueDefault()]              # Loading will overwrite if saved, else pre-load defaults
                            GlobalVars.extn_param_NEW_displayAverageTable_NAB       = [self.displayAverageDefault()]              # Loading will overwrite if saved, else pre-load defaults

                            GlobalVars.extn_param_NEW_autoSumDefault_NAB            = self.autoSumDefault()                      # Loading will overwrite if saved, else pre-load defaults
                            GlobalVars.extn_param_NEW_disableWidgetTitle_NAB        = self.disableWidgetTitleDefault()           # Loading will overwrite if saved, else pre-load defaults
                            GlobalVars.extn_param_NEW_showDashesInsteadOfZeros_NAB  = self.showDashesInsteadOfZerosDefault()     # Loading will overwrite if saved, else pre-load defaults
                            GlobalVars.extn_param_NEW_treatSecZeroBalInactive_NAB   = self.treatSecZeroBalInactiveDefault()      # Loading will overwrite if saved, else pre-load defaults

                            GlobalVars.extn_param_NEW_useIndianNumberFormat_NAB     = self.useIndianNumberFormatDefault()        # Loading will overwrite if saved, else pre-load defaults
                            GlobalVars.extn_param_NEW_hideDecimals_NAB              = self.hideDecimalsDefault()                 # Loading will overwrite if saved, else pre-load defaults
                            GlobalVars.extn_param_NEW_displayVisualUnderDots_NAB    = self.displayVisualUnderDotsDefault()       # Loading will overwrite if saved, else pre-load defaults

                            GlobalVars.extn_param_NEW_expandedView_NAB              = self.expandedViewDefault()                 # Loading will overwrite if saved, else pre-load defaults

                            GlobalVars.extn_param_listAccountUUIDs_NAB      = None
                            GlobalVars.extn_param_balanceType_NAB           = None
                            GlobalVars.extn_param_widget_display_name_NAB   = None

                        else:
                            myPrint("DB", "No migration of (old) parameters to new multi-row parameters performed....")
                            self.migratedParameters = False

                        self.parametersLoaded = True
                        self.savedAccountListUUIDs          = GlobalVars.extn_param_NEW_listAccountUUIDs_NAB
                        self.savedBalanceType               = GlobalVars.extn_param_NEW_balanceType_NAB
                        self.savedIncomeExpenseDateRange    = GlobalVars.extn_param_NEW_incomeExpenseDateRange_NAB
                        self.savedCustomDatesTable          = GlobalVars.extn_param_NEW_customDatesTable_NAB
                        self.savedRowSeparatorTable         = GlobalVars.extn_param_NEW_rowSeparatorTable_NAB
                        self.savedBlinkTable                = GlobalVars.extn_param_NEW_blinkTable_NAB
                        self.savedIncludeInactive           = GlobalVars.extn_param_NEW_includeInactive_NAB
                        self.savedAutoSumAccounts           = GlobalVars.extn_param_NEW_autoSumAccounts_NAB
                        self.savedWidgetName                = GlobalVars.extn_param_NEW_widget_display_name_NAB
                        self.savedCurrencyTable             = GlobalVars.extn_param_NEW_currency_NAB
                        self.savedDisableCurrencyFormatting = GlobalVars.extn_param_NEW_disableCurrencyFormatting_NAB
                        self.savedHideRowWhenXXXTable       = GlobalVars.extn_param_NEW_hideRowWhenXXXTable_NAB
                        self.savedHideRowXValueTable        = GlobalVars.extn_param_NEW_hideRowXValueTable_NAB
                        self.savedDisplayAverageTable       = GlobalVars.extn_param_NEW_displayAverageTable_NAB
                        self.savedShowWarningsTable         = GlobalVars.extn_param_NEW_showWarningsTable_NAB

                        self.savedAutoSumDefault            = GlobalVars.extn_param_NEW_autoSumDefault_NAB
                        self.savedDisableWidgetTitle        = GlobalVars.extn_param_NEW_disableWidgetTitle_NAB
                        self.savedShowDashesInsteadOfZeros  = GlobalVars.extn_param_NEW_showDashesInsteadOfZeros_NAB
                        self.savedTreatSecZeroBalInactive   = GlobalVars.extn_param_NEW_treatSecZeroBalInactive_NAB

                        self.savedUseIndianNumberFormat     = GlobalVars.extn_param_NEW_useIndianNumberFormat_NAB
                        self.savedHideDecimals              = GlobalVars.extn_param_NEW_hideDecimals_NAB
                        self.savedDisplayVisualUnderDots    = GlobalVars.extn_param_NEW_displayVisualUnderDots_NAB

                        self.savedExpandedView              = GlobalVars.extn_param_NEW_expandedView_NAB

                        self.setSelectedRowIndex(0)

                        self.validateParameters()
                        self.configSaved = True

                        self.dumpSavedOptions()

                        debugMDDateRangeOption()

        # method getName() must exist as the interface demands it.....
        def getName(self): return GlobalVars.DEFAULT_WIDGET_DISPLAY_NAME.title()

        # Not really used, but returns this value if print or repr is used on the class to retrieve its name....
        def __str__(self): return u"%s:%s (Extension)" %(self.myModuleID.capitalize(), GlobalVars.DEFAULT_WIDGET_DISPLAY_NAME.title())

        def __repr__(self): return self.__str__()

        def getMyself(self):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            fm = self.moneydanceContext.getModuleForID(self.myModuleID)
            if fm is None: return None, None
            try:
                pyObject = getFieldByReflection(fm, "extensionObject")
            except:
                myPrint("B", "@@ Error retrieving my own Python extension object..?")
                dump_sys_error_to_md_console_and_errorlog()
                return None, None

            return fm, pyObject

        def unloadMyself(self):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))

            fm, pyObject = self.getMyself()

            if fm is None:
                myPrint("DB", "Failed to retrieve myself - exiting")
                return False
            myPrint("DB", "Retrieved myself: %s" %(fm))

            try:
                invokeMethodByReflection(self.moneydanceContext, "unloadModule", [FeatureModule], [fm])
            except:
                myPrint("B", "@@ Error unloading my own extension object..?")
                dump_sys_error_to_md_console_and_errorlog()
                return False

            myPrint("B", "@@ Success! Unloaded / deactivated myself..! ;->")
            return True

        def removeMyself(self):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))

            fm, pyObject = self.getMyself()

            if fm is None:
                myPrint("DB", "Failed to retrieve myself - exiting")
                return False
            myPrint("DB", "Retrieved myself: %s" %(fm))

            try:
                myPrint("DB", "... about to ask MD to uninstall myself....")
                self.moneydanceContext.uninstallModule(fm)
            except:
                myPrint("B", "@@ Error uninstalling my own extension object..?")
                dump_sys_error_to_md_console_and_errorlog()
                return False

            myPrint("B", "@@ Success! Removed / uninstalled myself..! ;->")
            return True

        def isPreviewBuild(self):
            if self.moneydanceExtensionLoader is not None:
                try:
                    stream = self.moneydanceExtensionLoader.getResourceAsStream("/_PREVIEW_BUILD_")
                    if stream is not None:
                        myPrint("B", "@@ PREVIEW BUILD (%s) DETECTED @@" %(version_build))
                        stream.close()
                        return True
                except: pass
            return False

        def createMenus(self):
            # Called by Listener(s) so will be on the EDT

            NAB = NetAccountBalancesExtension.getNAB()

            # Recreate the Menu system each time - Damn Mac!!
            NAB.mainMenuBar = MyJMenuBar()

            menuO = MyJMenu("<html><B>Options</b></html>")
            menuO.setForeground(SetupMDColors.FOREGROUND_REVERSED)
            menuO.setBackground(SetupMDColors.BACKGROUND_REVERSED)

            NAB.menuItemDEBUG = MyJCheckBoxMenuItem("Debug")
            NAB.menuItemDEBUG.addActionListener(NAB.saveActionListener)
            NAB.menuItemDEBUG.setToolTipText("Enables extension to output debug information (internal technical stuff)")
            NAB.menuItemDEBUG.setSelected(debug)
            menuO.add(NAB.menuItemDEBUG)

            NAB.menuItemAutoSumDefault = MyJCheckBoxMenuItem("AutoSum Default (setting for new/inserted rows)")
            NAB.menuItemAutoSumDefault.addActionListener(NAB.saveActionListener)
            NAB.menuItemAutoSumDefault.setToolTipText("Sets the default flag for AutoSum on new rows - does not affect existing/saved rows")
            NAB.menuItemAutoSumDefault.setSelected(NAB.savedAutoSumDefault)
            menuO.add(NAB.menuItemAutoSumDefault)

            NAB.menuItemDisableWidgetTitle = MyJCheckBoxMenuItem("Disable Widget Title")
            NAB.menuItemDisableWidgetTitle.addActionListener(NAB.saveActionListener)
            NAB.menuItemDisableWidgetTitle.setToolTipText("Disables the Widget's Title on the Summary Page screen")
            NAB.menuItemDisableWidgetTitle.setSelected(NAB.savedShowDashesInsteadOfZeros)
            menuO.add(NAB.menuItemDisableWidgetTitle)

            NAB.menuItemShowDashesInsteadOfZeros = MyJCheckBoxMenuItem("Show Dashes instead of Zeros")
            NAB.menuItemShowDashesInsteadOfZeros.addActionListener(NAB.saveActionListener)
            NAB.menuItemShowDashesInsteadOfZeros.setToolTipText("Replaces the list display to show a '-' in place of '<CURR>0.0'")
            NAB.menuItemShowDashesInsteadOfZeros.setSelected(NAB.savedShowDashesInsteadOfZeros)
            menuO.add(NAB.menuItemShowDashesInsteadOfZeros)

            NAB.menuItemTreatSecZeroBalInactive = MyJCheckBoxMenuItem("Treat Securities with Zero Balance as Inactive")
            NAB.menuItemTreatSecZeroBalInactive.addActionListener(NAB.saveActionListener)
            NAB.menuItemTreatSecZeroBalInactive.setToolTipText("When enabled will treat securities with a zero balance as 'Inactive'")
            NAB.menuItemTreatSecZeroBalInactive.setSelected(NAB.savedTreatSecZeroBalInactive)
            menuO.add(NAB.menuItemTreatSecZeroBalInactive)

            NAB.menuItemUseIndianNumberFormat = MyJCheckBoxMenuItem("Use Indian number format")
            NAB.menuItemUseIndianNumberFormat.addActionListener(NAB.saveActionListener)
            NAB.menuItemUseIndianNumberFormat.setToolTipText("Enable Indian number formats (>10k, group powers of 100 - e.g. 10,00,000 not 1,000,000)")
            NAB.menuItemUseIndianNumberFormat.setSelected(NAB.savedUseIndianNumberFormat)
            menuO.add(NAB.menuItemUseIndianNumberFormat)

            NAB.menuItemHideDecimals = MyJCheckBoxMenuItem("Hide Decimal places")
            NAB.menuItemHideDecimals.addActionListener(NAB.saveActionListener)
            NAB.menuItemHideDecimals.setToolTipText("Enable the hiding of all decimal places (i.e. 1.99 will show as 1)")
            NAB.menuItemHideDecimals.setSelected(NAB.savedHideDecimals)
            menuO.add(NAB.menuItemHideDecimals)

            NAB.menuDisplayVisualUnderDots = MyJCheckBoxMenuItem("Display underline dots")
            NAB.menuDisplayVisualUnderDots.addActionListener(NAB.saveActionListener)
            NAB.menuDisplayVisualUnderDots.setToolTipText("Display 'underline' dots that fill the blank space between row names and values...")
            NAB.menuDisplayVisualUnderDots.setSelected(NAB.savedDisplayVisualUnderDots)
            menuO.add(NAB.menuDisplayVisualUnderDots)

            menuItemDeactivate = MyJMenuItem("Deactivate Extension")
            menuItemDeactivate.addActionListener(NAB.saveActionListener)
            menuItemDeactivate.setToolTipText("Deactivates this extension and also the HomePage 'widget' (will reactivate upon MD restart)")
            menuItemDeactivate.setSelected(True)
            if debug:
                menuO.add(menuItemDeactivate)  # Removed at the request of Sean (IK) to allow onto extensions list

            menuItemUninstall = MyJMenuItem("Uninstall Extension")
            menuItemUninstall.addActionListener(NAB.saveActionListener)
            menuItemUninstall.setToolTipText("Uninstalls and removes this extension (and also the HomePage 'widget'). This is permanent until you reinstall...")
            menuItemUninstall.setSelected(True)
            if debug:
                menuO.add(menuItemUninstall)  # Removed at the request of Sean (IK) to allow onto extensions list

            NAB.mainMenuBar.add(menuO)

            menuA = MyJMenu("<html><B>About</b></html>")
            menuA.setForeground(SetupMDColors.FOREGROUND_REVERSED)
            menuA.setBackground(SetupMDColors.BACKGROUND_REVERSED)

            menuItemA = MyJMenuItem("About")
            menuItemA.setToolTipText("About...")
            menuItemA.addActionListener(NAB.saveActionListener)
            menuItemA.setEnabled(True)
            menuA.add(menuItemA)

            menuItemH = MyJMenuItem("Help")
            menuItemH.setToolTipText("Help - show the readme.txt file...")
            menuItemH.addActionListener(NAB.saveActionListener)
            menuItemH.setEnabled(True)
            menuA.add(menuItemH)

            NAB.mainMenuBar.add(menuA)

            NAB.mainMenuBar.add(Box.createHorizontalGlue())

            NAB.menuBarItemHideControlPanel_CB = MyJCheckBox("Hide Controls", NAB.savedHideControlPanel)
            NAB.menuBarItemHideControlPanel_CB.putClientProperty("%s.id" %(NAB.myModuleID), "menuBarItemHideControlPanel_CB")
            NAB.menuBarItemHideControlPanel_CB.putClientProperty("%s.id.reversed" %(NAB.myModuleID), True)
            NAB.menuBarItemHideControlPanel_CB.setName("menuBarItemHideControlPanel_CB")
            NAB.menuBarItemHideControlPanel_CB.setToolTipText("Hides some of the Control panel to give you more screen space for the selection list")
            NAB.menuBarItemHideControlPanel_CB.addActionListener(NAB.saveActionListener)
            NAB.mainMenuBar.add(NAB.menuBarItemHideControlPanel_CB)

            # NAB.mainMenuBar.add(Box.createHorizontalGlue())
            NAB.mainMenuBar.add(Box.createRigidArea(Dimension(10, 0)))


            if Platform.isOSX():
                save_useScreenMenuBar = System.getProperty("apple.laf.useScreenMenuBar")
                if save_useScreenMenuBar is None or save_useScreenMenuBar == "":
                    save_useScreenMenuBar= System.getProperty("com.apple.macos.useScreenMenuBar")
                System.setProperty("apple.laf.useScreenMenuBar", "false")
                System.setProperty("com.apple.macos.useScreenMenuBar", "false")
            else:
                save_useScreenMenuBar = None

            NAB.theFrame.setJMenuBar(NAB.mainMenuBar)
            NAB.mainMenuBar.revalidate()
            NAB.mainMenuBar.repaint()

            if Platform.isOSX():
                System.setProperty("apple.laf.useScreenMenuBar", save_useScreenMenuBar)
                System.setProperty("com.apple.macos.useScreenMenuBar", save_useScreenMenuBar)

            self.updateMenus()

        def updateMenus(self):
            NAB = NetAccountBalancesExtension.getNAB()
            NAB.menuItemDEBUG.setSelected(debug)
            NAB.menuItemAutoSumDefault.setSelected(NAB.savedAutoSumDefault)
            NAB.menuItemDisableWidgetTitle.setSelected(NAB.savedDisableWidgetTitle)
            NAB.menuItemShowDashesInsteadOfZeros.setSelected(NAB.savedShowDashesInsteadOfZeros)
            NAB.menuItemTreatSecZeroBalInactive.setSelected(NAB.savedTreatSecZeroBalInactive)
            NAB.menuItemUseIndianNumberFormat.setSelected(NAB.savedUseIndianNumberFormat)
            NAB.menuItemHideDecimals.setSelected(NAB.savedHideDecimals)
            NAB.menuDisplayVisualUnderDots.setSelected(NAB.savedDisplayVisualUnderDots)

        def build_main_frame(self):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

            if self.theFrame is not None:
                myPrint("DB", ".. main JFrame is already built: %s - so exiting" %(self.theFrame))
                return

            SetupMDColors.updateUI()

            class BuildMainFrameRunnable(Runnable):
                def __init__(self): pass

                def run(self):                                                                                          # noqa
                    global net_account_balances_frame_  # Keep this here as we set it below

                    NAB = NetAccountBalancesExtension.getNAB()

                    myPrint("DB", "Creating main JFrame for application...")

                    NAB.quickSearchField = MyQuickSearchField()
                    document = NAB.quickSearchField.getDocument()                                                       # noqa
                    document.addDocumentListener(MyQuickSearchDocListener(NAB))
                    NAB.quickSearchField.addFocusListener(MyQuickSearchFocusAdapter(NAB.quickSearchField,document))     # noqa


                    # At startup, create dummy settings to build frame if nothing set.. Real settings will get loaded later
                    if NAB.savedAccountListUUIDs is None: NAB.resetParameters()

                    if NAB.isPreview is None:
                        myPrint("DB", "Checking for Preview build status...")
                        NAB.isPreview = NAB.isPreviewBuild()
                    titleExtraTxt = u"" if not NAB.isPreview else u"<PREVIEW BUILD: %s>" %(version_build)

                    # Called from getMoneydanceUI() so assume the Moneydance GUI is loaded...
                    # JFrame.setDefaultLookAndFeelDecorated(True)   # Note: Darcula Theme doesn't like this and seems to be OK without this statement...
                    net_account_balances_frame_ = MyJFrame(u"%s: Configure Summary Page (Home Page) widget's settings   %s"
                                                           %(GlobalVars.DEFAULT_WIDGET_DISPLAY_NAME.title(), titleExtraTxt))
                    NAB.theFrame = net_account_balances_frame_
                    NAB.theFrame.setName(u"%s_main" %(NAB.myModuleID))

                    NAB.theFrame.isActiveInMoneydance = True
                    NAB.theFrame.isRunTimeExtension = True

                    NAB.theFrame.MoneydanceAppListener = NAB
                    NAB.theFrame.HomePageViewObj = NAB.saveMyHomePageView

                    class MyDefaultListSelectionModel(DefaultListSelectionModel):  # build_main_frame() only runs once, so this is fine to do here...
                        # Change the selector - so not to deselect items when selecting others...
                        def __init__(self):
                            super(self.__class__, self).__init__()

                        def setSelectionInterval(self, start, end):
                            if (start != end):
                                super(self.__class__, self).setSelectionInterval(start, end)
                            elif self.isSelectedIndex(start):
                                self.removeSelectionInterval(start, end)
                            else:
                                self.addSelectionInterval(start, end)

                    class MyJList(JList, ListSelectionListener):
                        def __init__(self):
                            super(self.__class__, self).__init__([])
                            self.originalListObjects = []
                            self.listOfSelectedObjects = []
                            self.savedListeners = []
                            self.parallelAccountBalances = buildEmptyTxnOrBalanceArray()    # type: [{Account: HoldBalance}]

                        def valueChanged(self, e):
                            try:
                                myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
                                myPrint("DB", "In JList Selection Listener .valueChanged(): %s" %(e))

                                if e.getValueIsAdjusting():
                                    myPrint("DB", ".. getValueIsAdjusting() is True.... Ignoring.....")
                                    return

                                myPrint("DB", ".. internal master list of selected was:", self.listOfSelectedObjects)

                                i = -1
                                dataModel = self.getModel()
                                try:
                                    for i in range(e.getFirstIndex(), e.getLastIndex()+1):
                                        obj = dataModel.getElementAt(i)
                                        if self.isSelectedIndex(i):
                                            if obj not in self.listOfSelectedObjects:
                                                self.listOfSelectedObjects.append(obj)
                                        else:
                                            if obj in self.listOfSelectedObjects:
                                                self.listOfSelectedObjects.remove(obj)

                                except ArrayIndexOutOfBoundsException:
                                    # When filtering the list, the getLastIndex() seems to go out of bounds... ignore...
                                    if debug:
                                        myPrint("DB", "@@ Error managing internal selected objects list")
                                        myPrint("DB", "e.getFirstIndex():%s, e.getLastIndex()+1:%s" %(e.getFirstIndex(), e.getLastIndex()+1))
                                        myPrint("DB", "Was on i: %s" %(i))
                                        raise

                                except:
                                    myPrint("B", "@@ Error managing internal selected objects list")
                                    dump_sys_error_to_md_console_and_errorlog()
                                    raise

                                myPrint("DB", ".. internal master list of selected is now:", self.listOfSelectedObjects)
                            except:
                                myPrint("B", "@@ ERROR in .valueChanged() routine")
                                dump_sys_error_to_md_console_and_errorlog()
                                raise

                        def enableSelectionListeners(self):
                            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))

                            if len(self.getListSelectionListeners()) > 0:
                                myPrint("DB", ".. %s Selection listeners found - no action" %(len(self.getListSelectionListeners())))
                                return

                            if len(self.savedListeners) > 0:
                                myPrint("DB", ".. %s saved Selection listeners found - will reactivate them.." %(len(self.savedListeners)))
                                for listener in self.savedListeners: self.addListSelectionListener(listener)
                                return

                            myPrint("DB", "No saved listeners found... Will create one....")
                            self.addListSelectionListener(self)

                        def disableSelectionListeners(self):
                            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))

                            if len(self.getListSelectionListeners()) < 1:
                                myPrint("DB", ".. no existing Selection listeners found - no action")
                                return

                            myPrint("DB", ".. saving any existing listeners")
                            self.savedListeners = self.getListSelectionListeners()

                            for listener in self.savedListeners:
                                myPrint("DB", ".. removing listener: %s" %(listener))
                                self.removeListSelectionListener(listener)

                    renderer = NAB.MyJListRenderer()
                    renderer.setShowCurrency(True)
                    renderer.setFillAllSpace(False)
                    renderer.setPaintIcons(True)
                    renderer.setDrawAccountTypes(False)
                    renderer.setShowFullAccountName(False)

                    NAB.jlst = MyJList()
                    NAB.jlst.setBackground(NAB.moneydanceContext.getUI().colors.listBackground)
                    NAB.jlst.setCellRenderer(renderer)
                    NAB.jlst.setFixedCellHeight(NAB.jlst.getFixedCellHeight()+30)
                    NAB.jlst.setSelectionMode(ListSelectionModel.MULTIPLE_INTERVAL_SELECTION)
                    NAB.jlst.setSelectionModel(MyDefaultListSelectionModel())

                    NAB.saveActionListener = NAB.MyActionListener()

                    controlPnl = MyJPanel(GridBagLayout())
                    controlPnl.putClientProperty("%s.id" %(NAB.myModuleID), "controlPnl")

                    padx = 80
                    colLeftInset = 3
                    colRightInset = 3
                    colInsetFiller = 13

                    # --------------------------------------------------------------------------------------------------
                    onRow = 0
                    onCol = 0

                    topInset = 12
                    rowSelected_COMBOLabel = MyJLabel("Select Row to Configure:")
                    rowSelected_COMBOLabel.putClientProperty("%s.id" %(NAB.myModuleID), "rowSelected_COMBOLabel")
                    controlPnl.add(rowSelected_COMBOLabel, GridC.getc(onCol, onRow).leftInset(colLeftInset).rightInset(colInsetFiller).fillx().topInset(topInset))
                    onCol += 1

                    NAB.rowSelected_COMBO = MyJComboBox([None])
                    NAB.rowSelected_COMBO.setName("rowSelected_COMBO")
                    NAB.rowSelected_COMBO.putClientProperty("%s.id" %(NAB.myModuleID), "rowSelected_COMBO")
                    NAB.rowSelected_COMBO.setToolTipText("Select the row you would like to configure")
                    NAB.rowSelected_COMBO.addActionListener(NAB.saveActionListener)
                    controlPnl.add(NAB.rowSelected_COMBO, GridC.getc(onCol, onRow).west().topInset(topInset).leftInset(colInsetFiller))

                    class RowComboListRenderer(DefaultListCellRenderer):
                        def __init__(self):
                            super(self.__class__, self).__init__()

                        def getListCellRendererComponent(self, _list, value, index, isSelected, cellHasFocus):
                            c = super(self.__class__, self).getListCellRendererComponent(_list, value, index, isSelected, cellHasFocus)

                            md = NetAccountBalancesExtension.getNAB().moneydanceContext
                            bg = (md.getUI().colors.sidebarSelectedBG if isSelected else md.getUI().colors.defaultBackground)

                            if isSelected:
                                fg = md.getUI().colors.sidebarSelectedFG
                                altFG = md.getUI().colors.sidebarSelectedFG                                             # noqa
                            else:
                                fg = md.getUI().colors.defaultTextForeground
                                altFG = md.getUI().colors.tertiaryTextFG                                                # noqa

                            if isinstance(value, basestring) and ("*" in value or "~" in value):
                                fg = getColorRed()

                            c.setBackground(bg)
                            c.setForeground(fg)
                            # if Platform.isMac(): c.setOpaque(False)
                            if isMDThemeVAQua(): c.setOpaque(False)
                            return c

                    NAB.rowSelected_COMBO.setRenderer(RowComboListRenderer())

                    onCol += 1

                    NAB.warning_label = MyJLabel("",JLabel.CENTER)
                    NAB.warning_label.putClientProperty("%s.id" %(NAB.myModuleID), "warning_label")
                    NAB.warning_label.setMDHeaderBorder()
                    controlPnl.add(NAB.warning_label, GridC.getc(onCol, onRow).colspan(2).leftInset(colInsetFiller).topInset(topInset).rightInset(colRightInset).fillx())

                    onRow += 1
                    # --------------------------------------------------------------------------------------------------

                    onCol = 0

                    insertBefore_button = MyJButton("Insert Row before")
                    insertBefore_button.putClientProperty("%s.id" %(NAB.myModuleID), "insertBefore_button")
                    insertBefore_button.putClientProperty("%s.id.reversed" %(NAB.myModuleID), False)
                    insertBefore_button.setToolTipText("Inserts a new row before this one...")
                    insertBefore_button.putClientProperty("%s.collapsible" %(NAB.myModuleID), "true")
                    insertBefore_button.addActionListener(NAB.saveActionListener)
                    controlPnl.add(insertBefore_button, GridC.getc(onCol, onRow).padx(padx).leftInset(colLeftInset).fillx())
                    onCol += 1

                    insertAfter_button = MyJButton("Insert Row after")
                    insertAfter_button.putClientProperty("%s.id" %(NAB.myModuleID), "insertAfter_button")
                    insertAfter_button.putClientProperty("%s.id.reversed" %(NAB.myModuleID), False)
                    insertAfter_button.setToolTipText("Inserts a new row after this one...")
                    insertAfter_button.putClientProperty("%s.collapsible" %(NAB.myModuleID), "true")
                    insertAfter_button.addActionListener(NAB.saveActionListener)
                    controlPnl.add(insertAfter_button, GridC.getc(onCol, onRow).padx(padx).leftInset(colInsetFiller).fillx())
                    onCol += 1

                    deleteRow_button = MyJButton("Delete Row")
                    deleteRow_button.putClientProperty("%s.id" %(NAB.myModuleID), "deleteRow_button")
                    deleteRow_button.putClientProperty("%s.id.reversed" %(NAB.myModuleID), False)
                    deleteRow_button.setToolTipText("Deletes this row...")
                    deleteRow_button.putClientProperty("%s.collapsible" %(NAB.myModuleID), "true")
                    deleteRow_button.addActionListener(NAB.saveActionListener)
                    controlPnl.add(deleteRow_button, GridC.getc(onCol, onRow).padx(padx).leftInset(colInsetFiller).fillx())
                    onCol += 1

                    moveRow_button = MyJButton("Move Row")
                    moveRow_button.putClientProperty("%s.id" %(NAB.myModuleID), "moveRow_button")
                    moveRow_button.putClientProperty("%s.id.reversed" %(NAB.myModuleID), False)
                    moveRow_button.setToolTipText("Moves this row elsewhere...")
                    moveRow_button.putClientProperty("%s.collapsible" %(NAB.myModuleID), "true")
                    moveRow_button.addActionListener(NAB.saveActionListener)
                    controlPnl.add(moveRow_button, GridC.getc(onCol, onRow).padx(padx).leftInset(colInsetFiller).rightInset(colRightInset).fillx())
                    onCol += 1

                    onRow += 1
                    # --------------------------------------------------------------------------------------------------

                    onCol = 0

                    duplicateRow_button = MyJButton("Duplicate Row")
                    duplicateRow_button.putClientProperty("%s.id" %(NAB.myModuleID), "duplicateRow_button")
                    duplicateRow_button.putClientProperty("%s.id.reversed" %(NAB.myModuleID), False)
                    duplicateRow_button.setToolTipText("Duplicates this row...")
                    duplicateRow_button.putClientProperty("%s.collapsible" %(NAB.myModuleID), "true")
                    duplicateRow_button.addActionListener(NAB.saveActionListener)
                    controlPnl.add(duplicateRow_button, GridC.getc(onCol, onRow).leftInset(colLeftInset).fillx())
                    onCol += 1

                    cancelChanges_button = MyJButton("Reload Settings")
                    cancelChanges_button.putClientProperty("%s.id" %(NAB.myModuleID), "cancelChanges_button")
                    cancelChanges_button.putClientProperty("%s.id.reversed" %(NAB.myModuleID), False)
                    cancelChanges_button.setToolTipText("Reloads all settings from last saved")
                    cancelChanges_button.putClientProperty("%s.collapsible" %(NAB.myModuleID), "true")
                    cancelChanges_button.addActionListener(NAB.saveActionListener)
                    controlPnl.add(cancelChanges_button, GridC.getc(onCol, onRow).leftInset(colInsetFiller).fillx())
                    onCol += 1

                    resetDefaults_button = MyJButton("Reset Defaults")
                    resetDefaults_button.putClientProperty("%s.id" %(NAB.myModuleID), "resetDefaults_button")
                    resetDefaults_button.putClientProperty("%s.id.reversed" %(NAB.myModuleID), False)
                    resetDefaults_button.setToolTipText("Wipes all saved settings, resets to defaults with 1 row (does not save)")
                    resetDefaults_button.putClientProperty("%s.collapsible" %(NAB.myModuleID), "true")
                    resetDefaults_button.addActionListener(NAB.saveActionListener)
                    controlPnl.add(resetDefaults_button, GridC.getc(onCol, onRow).leftInset(colInsetFiller).fillx())
                    onCol += 1

                    onRow += 1

                    # --------------------------------------------------------------------------------------------------

                    onCol = 0
                    topInset = 8
                    bottomInset = 5

                    js = MyJSeparator()
                    js.putClientProperty("%s.collapsible" %(NAB.myModuleID), "true")
                    controlPnl.add(js, GridC.getc(onCol, onRow).leftInset(colLeftInset).topInset(topInset).rightInset(colRightInset).bottomInset(bottomInset).colspan(4).fillx())
                    onRow += 1

                    # --------------------------------------------------------------------------------------------------

                    onCol = 0
                    topInset = 4

                    rowNameLabel = MyJLabel("Row Name:")
                    rowNameLabel.putClientProperty("%s.id" %(NAB.myModuleID), "rowNameLabel")
                    controlPnl.add(rowNameLabel, GridC.getc(onCol, onRow).east().leftInset(colLeftInset).topInset(topInset))
                    onCol += 1

                    focusAdapterOnJTFs = NAB.MyJFieldFocusAdapter()

                    NAB.widgetNameField_JTF = MyJTextField(NAB.savedWidgetName[0])
                    NAB.widgetNameField_JTF.putClientProperty("%s.id" %(NAB.myModuleID), "widgetNameField_JTF")
                    NAB.widgetNameField_JTF.setName("widgetNameField_JTF")
                    NAB.widgetNameField_JTF.addFocusListener(focusAdapterOnJTFs)
                    controlPnl.add(NAB.widgetNameField_JTF, GridC.getc(onCol, onRow).colspan(2).leftInset(colInsetFiller).topInset(topInset).fillboth())
                    onCol += 2

                    NAB.simulateTotal_label = MyJLabel("<html><i>result here</i></html>",JLabel.CENTER)
                    NAB.simulateTotal_label.putClientProperty("%s.id" %(NAB.myModuleID), "simulateTotal_label")
                    NAB.simulateTotal_label.setMDHeaderBorder()
                    controlPnl.add(NAB.simulateTotal_label, GridC.getc(onCol, onRow).leftInset(colInsetFiller).topInset(topInset).rightInset(colRightInset).fillx())

                    onRow += 1

                    # --------------------------------------------------------------------------------------------------

                    onCol = 0
                    topInset = 2

                    balanceOptionLabel = MyJLabel("Balance Option:")
                    balanceOptionLabel.putClientProperty("%s.id" %(NAB.myModuleID), "balanceOptionLabel")
                    balanceOptionLabel.putClientProperty("%s.collapsible" %(NAB.myModuleID), "true")
                    controlPnl.add(balanceOptionLabel, GridC.getc(onCol, onRow).east().leftInset(colLeftInset))
                    onCol += 1

                    balanceTypes = ["Balance", "Current Balance", "Cleared Balance"]
                    NAB.balanceType_COMBO = MyJComboBox(balanceTypes)
                    NAB.balanceType_COMBO.putClientProperty("%s.id" %(NAB.myModuleID), "balanceType_COMBO")
                    NAB.balanceType_COMBO.setName("balanceType_COMBO")
                    NAB.balanceType_COMBO.setToolTipText("Select the balance type to total: Balance (i.e. the final balance), Current Balance (as of today), Cleared Balance")
                    NAB.balanceType_COMBO.putClientProperty("%s.collapsible" %(NAB.myModuleID), "true")
                    NAB.balanceType_COMBO.addActionListener(NAB.saveActionListener)
                    controlPnl.add(NAB.balanceType_COMBO, GridC.getc(onCol, onRow).leftInset(colInsetFiller).topInset(topInset).fillx().padx(padx))
                    onCol += 1

                    NAB.autoSumAccounts_CB = MyJCheckBox("AutoSum Accts", True)
                    NAB.autoSumAccounts_CB.putClientProperty("%s.id" %(NAB.myModuleID), "autoSumAccounts_CB")
                    NAB.autoSumAccounts_CB.putClientProperty("%s.id.reversed" %(NAB.myModuleID), False)
                    NAB.autoSumAccounts_CB.setName("autoSumAccounts_CB")
                    NAB.autoSumAccounts_CB.setToolTipText("AutoSum will auto sum/total the account recursively down the tree, including Securities. AutoSum=OFF means each item is totalled separately")
                    NAB.autoSumAccounts_CB.putClientProperty("%s.collapsible" %(NAB.myModuleID), "true")
                    NAB.autoSumAccounts_CB.addActionListener(NAB.saveActionListener)
                    controlPnl.add(NAB.autoSumAccounts_CB, GridC.getc(onCol, onRow).leftInset(colInsetFiller).topInset(topInset).colspan(1).fillx().padx(padx))
                    onCol += 1

                    NAB.showWarnings_CB = MyJCheckBox("Show Warnings", True)
                    NAB.showWarnings_CB.putClientProperty("%s.id" %(NAB.myModuleID), "showWarnings_CB")
                    NAB.showWarnings_CB.putClientProperty("%s.id.reversed" %(NAB.myModuleID), False)
                    NAB.showWarnings_CB.setName("showWarnings_CB")
                    NAB.showWarnings_CB.setToolTipText("Warnings on 'illogical' calculations will be shown for this row...")
                    NAB.showWarnings_CB.putClientProperty("%s.collapsible" %(NAB.myModuleID), "true")
                    NAB.showWarnings_CB.addActionListener(NAB.saveActionListener)
                    controlPnl.add(NAB.showWarnings_CB, GridC.getc(onCol, onRow).leftInset(colInsetFiller).topInset(topInset).colspan(1).rightInset(colRightInset).fillx().padx(padx))

                    onRow += 1

                    # --------------------------------------------------------------------------------------------------

                    onCol = 0
                    topInset = 2

                    displayCurrencyLabel = MyJLabel("Display Currency:")
                    displayCurrencyLabel.putClientProperty("%s.id" %(NAB.myModuleID), "displayCurrencyLabel")
                    displayCurrencyLabel.putClientProperty("%s.collapsible" %(NAB.myModuleID), "true")
                    controlPnl.add(displayCurrencyLabel, GridC.getc(onCol, onRow).east().leftInset(colLeftInset))
                    onCol += 1

                    NAB.currency_COMBO = MyJComboBox([None])
                    NAB.currency_COMBO.setPrototypeDisplayValue(""*45)
                    NAB.currency_COMBO.putClientProperty("%s.id" %(NAB.myModuleID), "currency_COMBO")
                    NAB.currency_COMBO.setName("currency_COMBO")
                    NAB.currency_COMBO.setToolTipText("Select the Currency to convert / display totals (default = your base currency)")
                    NAB.currency_COMBO.putClientProperty("%s.collapsible" %(NAB.myModuleID), "true")
                    NAB.currency_COMBO.addActionListener(NAB.saveActionListener)
                    controlPnl.add(NAB.currency_COMBO, GridC.getc(onCol, onRow).leftInset(colInsetFiller).topInset(topInset).colspan(2).fillx())
                    onCol += 2

                    NAB.disableCurrencyFormatting_CB = MyJCheckBox("Disable Currency Formatting", True)
                    NAB.disableCurrencyFormatting_CB.putClientProperty("%s.id" %(NAB.myModuleID), "disableCurrencyFormatting_CB")
                    NAB.disableCurrencyFormatting_CB.putClientProperty("%s.id.reversed" %(NAB.myModuleID), False)
                    NAB.disableCurrencyFormatting_CB.setName("disableCurrencyFormatting_CB")
                    NAB.disableCurrencyFormatting_CB.setToolTipText("Disable Currency Formatting (just present 'raw' numbers)")
                    NAB.disableCurrencyFormatting_CB.putClientProperty("%s.collapsible" %(NAB.myModuleID), "true")
                    NAB.disableCurrencyFormatting_CB.addActionListener(NAB.saveActionListener)
                    controlPnl.add(NAB.disableCurrencyFormatting_CB, GridC.getc(onCol, onRow).leftInset(colInsetFiller).topInset(topInset).rightInset(colRightInset).fillx())
                    onCol += 1

                    onRow += 1

                    # --------------------------------------------------------------------------------------------------
                    onCol = 0
                    pady = 5

                    # --
                    hideWhenSelector_pnl = MyJPanel(GridBagLayout())

                    hideWhenSelector_lbl = MyJLabel("Hide row:")
                    hideWhenSelector_lbl.putClientProperty("%s.id" %(NAB.myModuleID), "hideWhenSelector_lbl")
                    hideWhenSelector_lbl.putClientProperty("%s.collapsible" %(NAB.myModuleID), "true")
                    controlPnl.add(hideWhenSelector_lbl, GridC.getc(onCol, onRow).east().leftInset(colLeftInset))
                    onCol += 1

                    # NAB.hideRowWhenNever_JRB = MyJRadioButton(wrap_HTML_small("", "Never", MD_REF.getUI().getColors().defaultTextForeground))
                    NAB.hideRowWhenNever_JRB = MyJRadioButton("Never")
                    NAB.hideRowWhenNever_JRB.setName("hideRowWhenNever_JRB")

                    # NAB.hideRowWhenAlways_JRB = MyJRadioButton(wrap_HTML_small("", "Always", MD_REF.getUI().getColors().defaultTextForeground))
                    NAB.hideRowWhenAlways_JRB = MyJRadioButton("Always")
                    NAB.hideRowWhenAlways_JRB.setName("hideRowWhenAlways_JRB")

                    # NAB.hideRowWhenZeroOrX_JRB = MyJRadioButton(wrap_HTML_small("", "=x", MD_REF.getUI().getColors().defaultTextForeground))
                    NAB.hideRowWhenZeroOrX_JRB = MyJRadioButton("=X")
                    NAB.hideRowWhenZeroOrX_JRB.setName("hideRowWhenZeroOrX_JRB")

                    # NAB.hideRowWhenLtEqZeroOrX_JRB = MyJRadioButton(wrap_HTML_small("", "<=x", MD_REF.getUI().getColors().defaultTextForeground))
                    NAB.hideRowWhenLtEqZeroOrX_JRB = MyJRadioButton("<=X")
                    NAB.hideRowWhenLtEqZeroOrX_JRB.setName("hideRowWhenLtEqZeroOrX_JRB")

                    # NAB.hideRowWhenGrEqZeroOrX_JRB = MyJRadioButton(wrap_HTML_small("", ">=x", MD_REF.getUI().getColors().defaultTextForeground))
                    NAB.hideRowWhenGrEqZeroOrX_JRB = MyJRadioButton(">=X")
                    NAB.hideRowWhenGrEqZeroOrX_JRB.setName("hideRowWhenGrEqZeroOrX_JRB")

                    # NAB.hideRowWhenNotZeroOrX_JRB = MyJRadioButton(wrap_HTML_small("", "Not x", MD_REF.getUI().getColors().defaultTextForeground))
                    NAB.hideRowWhenNotZeroOrX_JRB = MyJRadioButton("Not X")
                    NAB.hideRowWhenNotZeroOrX_JRB.setName("hideRowWhenNotZeroOrX_JRB")

                    hideWhenButtonGroup = ButtonGroup()

                    onHideWhenRow = 0
                    onHideWhenCol = 0

                    for jrb in [NAB.hideRowWhenNever_JRB, NAB.hideRowWhenAlways_JRB, NAB.hideRowWhenZeroOrX_JRB, NAB.hideRowWhenLtEqZeroOrX_JRB, NAB.hideRowWhenGrEqZeroOrX_JRB, NAB.hideRowWhenNotZeroOrX_JRB]:
                        hideWhenButtonGroup.add(jrb)
                        jrb.setActionCommand(jrb.getName())
                        jrb.putClientProperty("%s.id" %(NAB.myModuleID), jrb.getName())
                        jrb.putClientProperty("%s.id.reversed" %(NAB.myModuleID), False)
                        jrb.setToolTipText("Allows hiding of this row. Options: Never, Always(disabled), When balance is ...: =x, <=x, >=x)")
                        jrb.putClientProperty("%s.collapsible" %(NAB.myModuleID), "true")
                        jrb.addActionListener(NAB.saveActionListener)
                        if jrb is NAB.hideRowWhenNotZeroOrX_JRB: continue  # disable this option
                        hideWhenSelector_pnl.add(jrb, GridC.getc(onHideWhenCol, onHideWhenRow).leftInset(0).rightInset(5))
                        onHideWhenCol += 1

                    # --------------------------------------------------------------------------------------------------

                    hideXValue_lbl = MyJLabel("X=")
                    hideXValue_lbl.putClientProperty("%s.id" %(NAB.myModuleID), "hideXValue_lbl")
                    hideXValue_lbl.putClientProperty("%s.collapsible" %(NAB.myModuleID), "true")
                    hideWhenSelector_pnl.add(hideXValue_lbl, GridC.getc(onHideWhenCol, onHideWhenRow).leftInset(5))
                    onHideWhenCol += 1

                    NAB.hideRowXValue_JRF = MyJRateFieldXValue(NAB.decimal)
                    if isinstance(NAB.hideRowXValue_JRF, (MyJRateFieldXValue, JRateField, JTextField)): pass
                    NAB.hideRowXValue_JRF.putClientProperty("%s.id" %(NAB.myModuleID), "hideRowXValue_JRF")
                    NAB.hideRowXValue_JRF.putClientProperty("%s.collapsible" %(NAB.myModuleID), "true")
                    NAB.hideRowXValue_JRF.setName("hideRowXValue_JRF")
                    NAB.hideRowXValue_JRF.setToolTipText("Enter the 'X' value to be used when using the hide row when option(s). Default is zero. ")
                    NAB.hideRowXValue_JRF.addFocusListener(focusAdapterOnJTFs)
                    hideWhenSelector_pnl.add(NAB.hideRowXValue_JRF, GridC.getc(onHideWhenCol, onHideWhenRow))
                    onHideWhenCol += 1

                    controlPnl.add(hideWhenSelector_pnl, GridC.getc(onCol, onRow).west().leftInset(colInsetFiller).fillx().pady(pady).filly().colspan(2))
                    onCol += 2
                    onRow += 1
                    # --------------------------------------------------------------------------------------------------
                    onCol = 0

                    rowFormatting_lbl = MyJLabel("Row formatting:")
                    rowFormatting_lbl.putClientProperty("%s.id" %(NAB.myModuleID), "rowFormatting_lbl")
                    rowFormatting_lbl.putClientProperty("%s.collapsible" %(NAB.myModuleID), "true")
                    controlPnl.add(rowFormatting_lbl, GridC.getc(onCol, onRow).east().leftInset(colLeftInset))
                    onCol += 1

                    separatorSelector_pnl = MyJPanel(GridBagLayout())

                    # separatorSelector_lbl = MyJLabel(wrap_HTML_small("", "Separator:", _smallColor=MD_REF.getUI().getColors().defaultTextForeground))
                    separatorSelector_lbl = MyJLabel("Separator:")
                    separatorSelector_lbl.putClientProperty("%s.id" %(NAB.myModuleID), "separatorSelector_lbl")
                    separatorSelector_lbl.putClientProperty("%s.collapsible" %(NAB.myModuleID), "true")

                    # NAB.separatorSelectorNone_JRB = MyJRadioButton(wrap_HTML_small("", GlobalVars.Strings.UNICODE_CROSS, MD_REF.getUI().getColors().defaultTextForeground))
                    NAB.separatorSelectorNone_JRB = MyJRadioButton(GlobalVars.Strings.UNICODE_CROSS)
                    NAB.separatorSelectorNone_JRB = MyJRadioButton("None")
                    NAB.separatorSelectorNone_JRB.setName("separatorSelectorNone_JRB")

                    # NAB.separatorSelectorAbove_JRB = MyJRadioButton(wrap_HTML_small("", GlobalVars.Strings.UNICODE_UP_ARROW, MD_REF.getUI().getColors().defaultTextForeground))
                    NAB.separatorSelectorAbove_JRB = MyJRadioButton(GlobalVars.Strings.UNICODE_UP_ARROW)
                    NAB.separatorSelectorAbove_JRB.setName("separatorSelectorAbove_JRB")

                    # NAB.separatorSelectorBelow_JRB = MyJRadioButton(wrap_HTML_small("", GlobalVars.Strings.UNICODE_DOWN_ARROW, MD_REF.getUI().getColors().defaultTextForeground))
                    NAB.separatorSelectorBelow_JRB = MyJRadioButton(GlobalVars.Strings.UNICODE_DOWN_ARROW)
                    NAB.separatorSelectorBelow_JRB.setName("separatorSelectorBelow_JRB")

                    # NAB.separatorSelectorBoth_JRB = MyJRadioButton(wrap_HTML_small("", GlobalVars.Strings.UNICODE_UP_ARROW + GlobalVars.Strings.UNICODE_DOWN_ARROW, MD_REF.getUI().getColors().defaultTextForeground))
                    NAB.separatorSelectorBoth_JRB = MyJRadioButton(GlobalVars.Strings.UNICODE_UP_ARROW + GlobalVars.Strings.UNICODE_DOWN_ARROW)
                    NAB.separatorSelectorBoth_JRB.setName("separatorSelectorBoth_JRB")

                    separatorButtonGroup = ButtonGroup()

                    onSepRow = 0
                    onSepCol = 0

                    separatorSelector_pnl.add(separatorSelector_lbl, GridC.getc(onSepCol, onSepRow))
                    onSepCol += 1

                    for jrb in [NAB.separatorSelectorNone_JRB, NAB.separatorSelectorAbove_JRB, NAB.separatorSelectorBelow_JRB, NAB.separatorSelectorBoth_JRB]:
                        separatorButtonGroup.add(jrb)
                        jrb.setActionCommand(jrb.getName())
                        jrb.putClientProperty("%s.id" %(NAB.myModuleID), jrb.getName())
                        jrb.putClientProperty("%s.id.reversed" %(NAB.myModuleID), False)
                        jrb.setToolTipText(u"Define a separator for this row... Either None%s, Above%s, Below%s, or Above and Below%s"
                                           %(GlobalVars.Strings.UNICODE_CROSS, GlobalVars.Strings.UNICODE_UP_ARROW, GlobalVars.Strings.UNICODE_DOWN_ARROW, GlobalVars.Strings.UNICODE_UP_ARROW + GlobalVars.Strings.UNICODE_DOWN_ARROW))
                        jrb.putClientProperty("%s.collapsible" %(NAB.myModuleID), "true")
                        jrb.addActionListener(NAB.saveActionListener)
                        separatorSelector_pnl.add(jrb, GridC.getc(onSepCol, onSepRow).leftInset(0).rightInset(0))
                        onSepCol += 1

                    controlPnl.add(separatorSelector_pnl, GridC.getc(onCol, onRow).leftInset(colInsetFiller+2).rightInset(colRightInset).fillx().pady(pady).filly().west())
                    onCol += 1

                    NAB.blinkRow_CB = MyJCheckBox("Blink", True)
                    NAB.blinkRow_CB.putClientProperty("%s.id" %(NAB.myModuleID), "blinkRow_CB")
                    NAB.blinkRow_CB.putClientProperty("%s.id.reversed" %(NAB.myModuleID), False)
                    NAB.blinkRow_CB.setName("blinkRow_CB")
                    NAB.blinkRow_CB.setToolTipText("When enabled, the calculated balance will blink (when this row is visible)")
                    NAB.blinkRow_CB.putClientProperty("%s.collapsible" %(NAB.myModuleID), "true")
                    NAB.blinkRow_CB.addActionListener(NAB.saveActionListener)
                    controlPnl.add(NAB.blinkRow_CB, GridC.getc(onCol, onRow).leftInset(colInsetFiller).topInset(topInset).colspan(1).fillx().padx(padx))
                    onCol += 1

                    onAverageRow = 0
                    onAverageCol = 0
                    displayAverage_pnl = MyJPanel(GridBagLayout())
                    displayAverage_lbl = MyJLabel("Avg/by:")
                    displayAverage_lbl.putClientProperty("%s.id" %(NAB.myModuleID), "displayAverage_lbl")
                    displayAverage_lbl.putClientProperty("%s.collapsible" %(NAB.myModuleID), "true")
                    displayAverage_pnl.add(displayAverage_lbl, GridC.getc(onAverageCol, onAverageRow))
                    onAverageCol += 1

                    NAB.displayAverage_JRF = MyJRateFieldAverage(NAB.decimal)
                    if isinstance(NAB.displayAverage_JRF, (MyJRateFieldAverage, JRateField, JTextField)): pass
                    NAB.displayAverage_JRF.putClientProperty("%s.id" %(NAB.myModuleID), "displayAverage_JRF")
                    NAB.displayAverage_JRF.putClientProperty("%s.collapsible" %(NAB.myModuleID), "true")
                    NAB.displayAverage_JRF.setName("displayAverage_JRF")
                    NAB.displayAverage_JRF.setToolTipText("Set the  % by x value to display average instead of balance (default 1.0)")
                    NAB.displayAverage_JRF.addFocusListener(focusAdapterOnJTFs)
                    displayAverage_pnl.add(NAB.displayAverage_JRF, GridC.getc(onAverageCol, onAverageRow).leftInset(5))
                    onAverageCol += 1

                    # controlPnl.add(displayAverage_pnl, GridC.getc(onCol, onRow).leftInset(colInsetFiller).topInset(topInset).colspan(1).fillx().padx(padx))
                    controlPnl.add(displayAverage_pnl, GridC.getc(onCol, onRow).west().leftInset(colInsetFiller))
                    onCol += 1
                    onRow += 1

                    # --------------------------------------------------------------------------------------------------
                    onCol = 0
                    topInset = 2

                    incExpDateRangeOptionLabel = MyJLabel("Inc/Exp Date Range:")
                    incExpDateRangeOptionLabel.putClientProperty("%s.id" %(NAB.myModuleID), "incExpDateRangeOptionLabel")
                    incExpDateRangeOptionLabel.putClientProperty("%s.collapsible" %(NAB.myModuleID), "true")
                    controlPnl.add(incExpDateRangeOptionLabel, GridC.getc(onCol, onRow).east().leftInset(colLeftInset))
                    onCol += 1

                    incExpDateRangeOptions = []
                    for drange in sorted(DateRangeOption.values(), key=lambda x: (x.getSortKey())):
                        # if drange == DateRangeOption.DR_CUSTOM_DATE: continue
                        incExpDateRangeOptions.append(NAB.DateRangeSingleOption(drange))

                    NAB.incomeExpenseDateRange_COMBO = MyJComboBox(incExpDateRangeOptions)
                    NAB.incomeExpenseDateRange_COMBO.putClientProperty("%s.id" %(NAB.myModuleID), "incomeExpenseDateRange_COMBO")
                    NAB.incomeExpenseDateRange_COMBO.setName("incomeExpenseDateRange_COMBO")
                    NAB.incomeExpenseDateRange_COMBO.setToolTipText("Specify a dynamic date range for Income / Expense Category calculations ('Custom' is always fixed) - does not affect other accounts/securities")
                    NAB.incomeExpenseDateRange_COMBO.putClientProperty("%s.collapsible" %(NAB.myModuleID), "true")
                    NAB.incomeExpenseDateRange_COMBO.addActionListener(NAB.saveActionListener)
                    controlPnl.add(NAB.incomeExpenseDateRange_COMBO, GridC.getc(onCol, onRow).colspan(2).leftInset(colInsetFiller).topInset(topInset).fillx())

                    onCol += 2
                    topInset = 0
                    bottomInset = 0

                    NAB.parallelBalancesWarningLabel = MyJLabel("Key:")
                    NAB.parallelBalancesWarningLabel.putClientProperty("%s.id" %(NAB.myModuleID), "parallelBalancesWarningLabel")
                    NAB.parallelBalancesWarningLabel.putClientProperty("%s.collapsible" %(NAB.myModuleID), "true")
                    controlPnl.add(NAB.parallelBalancesWarningLabel, GridC.getc(onCol, onRow).insets(topInset,colLeftInset,bottomInset,colRightInset))

                    onRow += 1
                    # --------------------------------------------------------------------------------------------------

                    onCol = 1
                    topInset = 0
                    bottomInset = 0

                    NAB.dateRangeLabel = MyJLabel("Date Range:")
                    NAB.dateRangeLabel.putClientProperty("%s.id" %(NAB.myModuleID), "dateRangeLabel")
                    NAB.dateRangeLabel.putClientProperty("%s.collapsible" %(NAB.myModuleID), "true")
                    controlPnl.add(NAB.dateRangeLabel, GridC.getc(onCol, onRow).colspan(3).fillx().insets(topInset,colInsetFiller,bottomInset,colRightInset))

                    onRow += 1

                    # --------------------------------------------------------------------------------------------------

                    onCol = 0
                    topInset = 7

                    clearList_button = MyJButton("Clear Selection")
                    clearList_button.putClientProperty("%s.id" %(NAB.myModuleID), "clearList_button")
                    clearList_button.putClientProperty("%s.id.reversed" %(NAB.myModuleID), False)
                    clearList_button.setToolTipText("Clears the current selection(s)...")
                    clearList_button.addActionListener(NAB.saveActionListener)
                    controlPnl.add(clearList_button, GridC.getc(onCol, onRow).leftInset(colInsetFiller).topInset(topInset).fillx())
                    onCol += 1

                    undoListChanges_button = MyJButton("Undo List Changes")
                    undoListChanges_button.putClientProperty("%s.id" %(NAB.myModuleID), "undoListChanges_button")
                    undoListChanges_button.putClientProperty("%s.id.reversed" %(NAB.myModuleID), False)
                    undoListChanges_button.setToolTipText("Undo your account list changes and revert to last saved list")
                    undoListChanges_button.addActionListener(NAB.saveActionListener)
                    controlPnl.add(undoListChanges_button, GridC.getc(onCol, onRow).leftInset(colInsetFiller).topInset(topInset).fillx())
                    onCol += 1

                    storeAccountList_button = MyJButton("Store List Changes")
                    storeAccountList_button.putClientProperty("%s.id" %(NAB.myModuleID), "storeAccountList_button")
                    storeAccountList_button.putClientProperty("%s.id.reversed" %(NAB.myModuleID), False)
                    storeAccountList_button.setToolTipText("Stores the selected account list into memory (does not save)")
                    storeAccountList_button.addActionListener(NAB.saveActionListener)
                    controlPnl.add(storeAccountList_button, GridC.getc(onCol, onRow).leftInset(colInsetFiller).topInset(topInset).fillx())
                    onCol += 1

                    saveSettings_button = MyJButton("Save All Settings".upper())
                    saveSettings_button.putClientProperty("%s.id" %(NAB.myModuleID), "saveSettings_button")
                    saveSettings_button.putClientProperty("%s.id.reversed" %(NAB.myModuleID), False)
                    saveSettings_button.setToolTipText("Saves all the changes made to settings")
                    saveSettings_button.addActionListener(NAB.saveActionListener)
                    controlPnl.add(saveSettings_button, GridC.getc(onCol, onRow).leftInset(colInsetFiller).topInset(topInset).rightInset(colRightInset).fillx())

                    onRow += 1

                    # --------------------------------------------------------------------------------------------------

                    onCol = 0
                    topInset = 8
                    bottomInset = 5
                    controlPnl.add(MyJSeparator(), GridC.getc(onCol, onRow).leftInset(colLeftInset).topInset(topInset).rightInset(colRightInset).bottomInset(bottomInset).colspan(4).fillx())

                    onRow += 1
                    # --------------------------------------------------------------------------------------------------

                    onCol = 0
                    topInset = 0
                    bottomInset = 0

                    filterLabel = MyJLabel(wrap_HTML_small("","FILTERS:", NAB.moneydanceContext.getUI().colors.defaultTextForeground))
                    filterLabel.putClientProperty("%s.id" %(NAB.myModuleID), "filterLabel")
                    filterLabel.putClientProperty("%s.collapsible" %(NAB.myModuleID), "true")
                    controlPnl.add(filterLabel, GridC.getc(onCol, onRow).southEast().fillx().insets(topInset,colLeftInset+2,bottomInset,colRightInset))

                    onRow += 1
                    # --------------------------------------------------------------------------------------------------

                    onCol = 0
                    topInset = 0
                    bottomInset = 2

                    includeInactiveOptions = ["Active Only", "Include Inactive"]
                    NAB.includeInactive_COMBO = MyJComboBox(includeInactiveOptions)
                    NAB.includeInactive_COMBO.putClientProperty("%s.id" %(NAB.myModuleID), "includeInactive_COMBO")
                    NAB.includeInactive_COMBO.setName("includeInactive_COMBO")
                    NAB.includeInactive_COMBO.setToolTipText("Select to only list Active items, or also include Inactive too")
                    NAB.includeInactive_COMBO.addActionListener(NAB.saveActionListener)
                    controlPnl.add(NAB.includeInactive_COMBO, GridC.getc(onCol, onRow).leftInset(colLeftInset).topInset(topInset+3).fillx())
                    onCol += 1

                    NAB.filterOutZeroBalAccts_INACTIVE_CB = MyJCheckBox("Filter Out Zeros Inactive", True)
                    NAB.filterOutZeroBalAccts_INACTIVE_CB.putClientProperty("%s.id" %(NAB.myModuleID), "filterOutZeroBalAccts_INACTIVE_CB")
                    NAB.filterOutZeroBalAccts_INACTIVE_CB.putClientProperty("%s.id.reversed" %(NAB.myModuleID), False)
                    NAB.filterOutZeroBalAccts_INACTIVE_CB.setName("filterOutZeroBalAccts_INACTIVE_CB")
                    NAB.filterOutZeroBalAccts_INACTIVE_CB.setToolTipText("Applies an additional filter: hide inactive accounts with a zero balance")
                    NAB.filterOutZeroBalAccts_INACTIVE_CB.addActionListener(NAB.saveActionListener)
                    controlPnl.add(NAB.filterOutZeroBalAccts_INACTIVE_CB, GridC.getc(onCol, onRow).leftInset(colInsetFiller).topInset(topInset).bottomInset(bottomInset).colspan(1).fillboth())
                    onCol += 1

                    NAB.filterIncludeSelected_CB = MyJCheckBox("Filter Include Selected", True)
                    NAB.filterIncludeSelected_CB.putClientProperty("%s.id" %(NAB.myModuleID), "filterIncludeSelected_CB")
                    NAB.filterIncludeSelected_CB.putClientProperty("%s.id.reversed" %(NAB.myModuleID), False)
                    NAB.filterIncludeSelected_CB.setName("filterIncludeSelected_CB")
                    NAB.filterIncludeSelected_CB.setToolTipText("Applies an additional filter: when filtering, always include selected lines too")
                    NAB.filterIncludeSelected_CB.addActionListener(NAB.saveActionListener)
                    controlPnl.add(NAB.filterIncludeSelected_CB, GridC.getc(onCol, onRow).leftInset(colInsetFiller).topInset(topInset).bottomInset(bottomInset).colspan(1).fillboth())
                    onCol += 1

                    onRow += 1
                    # --------------------------------------------------------------------------------------------------

                    onCol = 0
                    topInset = 5

                    # noinspection PyUnresolvedReferences
                    includeAccountType = ["All Account Types",
                                          Account.AccountType.BANK,
                                          Account.AccountType.CREDIT_CARD,
                                          Account.AccountType.INVESTMENT,
                                          Account.AccountType.SECURITY,
                                          Account.AccountType.ASSET,
                                          Account.AccountType.LIABILITY,
                                          Account.AccountType.LOAN,
                                          Account.AccountType.INCOME,
                                          Account.AccountType.EXPENSE]

                    NAB.filterOnlyAccountType_COMBO = MyJComboBox(includeAccountType)
                    NAB.filterOnlyAccountType_COMBO.putClientProperty("%s.id" %(NAB.myModuleID), "filterOnlyAccountType_COMBO")
                    NAB.filterOnlyAccountType_COMBO.setName("filterOnlyAccountType_COMBO")
                    NAB.filterOnlyAccountType_COMBO.setToolTipText("Applies an additional filter: Only show the selected account type")
                    NAB.filterOnlyAccountType_COMBO.addActionListener(NAB.saveActionListener)
                    controlPnl.add(NAB.filterOnlyAccountType_COMBO, GridC.getc(onCol, onRow).leftInset(colLeftInset).topInset(topInset).bottomInset(bottomInset).colspan(1).fillboth())
                    onCol += 1

                    topInset = 0

                    NAB.filterOutZeroBalAccts_ACTIVE_CB = MyJCheckBox("Filter Out Zeros Active", True)
                    NAB.filterOutZeroBalAccts_ACTIVE_CB.putClientProperty("%s.id" %(NAB.myModuleID), "filterOutZeroBalAccts_ACTIVE_CB")
                    NAB.filterOutZeroBalAccts_ACTIVE_CB.putClientProperty("%s.id.reversed" %(NAB.myModuleID), False)
                    NAB.filterOutZeroBalAccts_ACTIVE_CB.setName("filterOutZeroBalAccts_ACTIVE_CB")
                    NAB.filterOutZeroBalAccts_ACTIVE_CB.setToolTipText("Applies an additional filter: hide active accounts with a zero balance")
                    NAB.filterOutZeroBalAccts_ACTIVE_CB.addActionListener(NAB.saveActionListener)
                    controlPnl.add(NAB.filterOutZeroBalAccts_ACTIVE_CB, GridC.getc(onCol, onRow).leftInset(colInsetFiller).topInset(topInset).bottomInset(bottomInset).colspan(1).fillboth())
                    onCol += 1

                    NAB.filterOnlyShowSelected_CB = MyJCheckBox("Only Show Selected", True)
                    NAB.filterOnlyShowSelected_CB.putClientProperty("%s.id" %(NAB.myModuleID), "filterOnlyShowSelected_CB")
                    NAB.filterOnlyShowSelected_CB.putClientProperty("%s.id.reversed" %(NAB.myModuleID), False)
                    NAB.filterOnlyShowSelected_CB.setName("filterOnlyShowSelected_CB")
                    NAB.filterOnlyShowSelected_CB.setToolTipText("Applies an additional filter: Only show all selected lines")
                    NAB.filterOnlyShowSelected_CB.addActionListener(NAB.saveActionListener)
                    controlPnl.add(NAB.filterOnlyShowSelected_CB, GridC.getc(onCol, onRow).leftInset(colInsetFiller).topInset(topInset).bottomInset(bottomInset).colspan(1).fillboth())


                    onRow += 1
                    # --------------------------------------------------------------------------------------------------

                    onCol = 0
                    topInset = 2
                    bottomInset = 0

                    controlPnl.add(NAB.quickSearchField,GridC.getc(onCol, onRow).colspan(4).fillx().insets(topInset,colLeftInset,bottomInset,colRightInset))

                    onRow += 1
                    # --------------------------------------------------------------------------------------------------

                    onCol = 2
                    NAB.keyLabel = MyJLabel("Key:")
                    NAB.keyLabel.putClientProperty("%s.id" %(NAB.myModuleID), "keyLabel")
                    NAB.keyLabel.putClientProperty("%s.collapsible" %(NAB.myModuleID), "true")
                    controlPnl.add(NAB.keyLabel, GridC.getc(onCol, onRow).southEast().colspan(2).fillx().insets(topInset,colLeftInset,bottomInset,colRightInset+2))

                    onRow += 1
                    # --------------------------------------------------------------------------------------------------

                    scrollpane = MyJScrollPane(NAB.jlst, JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED,JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED)
                    scrollpane.putClientProperty("%s.id" %(NAB.myModuleID), "scrollpane")
                    scrollpane.setViewportBorder(EmptyBorder(5, colLeftInset, 5, colRightInset))
                    scrollpane.setOpaque(False)

                    screenSize = Toolkit.getDefaultToolkit().getScreenSize()                                            # noqa
                    desired_scrollPane_width = 800                                                                      # noqa
                    desired_frame_height_max = min(650, int(round(screenSize.height * 0.9,0)))                          # noqa
                    desired_frame_height_max = min(500, int(round(screenSize.height * 0.9,0)))                          # noqa
                    scrollPaneTop = scrollpane.getY()                                                                   # noqa
                    calcScrollPaneHeight = (desired_frame_height_max - scrollPaneTop - 70)                              # noqa

                    scrollpane.setPreferredSize(Dimension(0, calcScrollPaneHeight))
                    # scrollpane.setMinimumSize(Dimension(desired_scrollPane_width, calcScrollPaneHeight))
                    # scrollpane.setMaximumSize(Dimension(int(round(screenSize.width * 0.9,0)), int(round((screenSize.height * 0.9) - scrollPaneTop - 70,0))))

                    # -----------------------------------------------------------------------------------
                    mainPnl = MyJPanel(BorderLayout())
                    mainPnl.putClientProperty("%s.id" %(NAB.myModuleID), "mainPnl")
                    mainPnl.add(controlPnl, BorderLayout.NORTH)
                    mainPnl.add(scrollpane, BorderLayout.CENTER)

                    NAB.theFrame.getContentPane().setLayout(BorderLayout())
                    NAB.theFrame.getContentPane().add(mainPnl, BorderLayout.CENTER)

                    # -----------------------------------------------------------------------------------
                    NAB.theFrame.setDefaultCloseOperation(WindowConstants.HIDE_ON_CLOSE)

                    shortcut = Toolkit.getDefaultToolkit().getMenuShortcutKeyMaskEx()

                    # Add standard CMD-W keystrokes etc to close window
                    NAB.theFrame.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_W, shortcut), "hide-window")
                    NAB.theFrame.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_F4, shortcut), "hide-window")
                    NAB.theFrame.getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0), "hide-window")
                    NAB.theFrame.getRootPane().getActionMap().put("close-window", NAB.CloseAction(NAB.theFrame))
                    NAB.theFrame.getRootPane().getActionMap().put("hide-window", NAB.HideAction(NAB.theFrame))

                    if NAB.moneydanceExtensionLoader:
                        try:
                            NAB.helpFile = load_text_from_stream_file(NAB.moneydanceExtensionLoader.getResourceAsStream("/%s_readme.txt" %(NAB.myModuleID)))
                            myPrint("DB", "Contents loaded from /%s_readme.txt" %(NAB.myModuleID))
                        except:
                            myPrint("B", "@@ Error loading contents from /%s_readme.txt" %(NAB.myModuleID))

                    NAB.theFrame.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_I, shortcut), "display-help")
                    NAB.theFrame.getRootPane().getActionMap().put("display-help", NAB.HelpAction(NAB.theFrame))

                    NAB.theFrame.addWindowListener(NAB.WindowListener(NAB.theFrame, NAB.myModuleID))

                    # self.theFrame.setPreferredSize(Dimension(600, 800))
                    NAB.theFrame.setExtendedState(JFrame.NORMAL)
                    NAB.theFrame.setResizable(True)

                    # No longer setting up menu here....

                    NAB.theFrame.pack()
                    NAB.theFrame.setLocationRelativeTo(None)

                    NAB.jlst.requestFocusInWindow()           # Set initial focus on the account selector

                    NAB.theFrame.setVisible(False)

                    if (not Platform.isOSX()):
                        NAB.moneydanceContext.getUI().getImages()
                        NAB.theFrame.setIconImage(MDImages.getImage(NAB.moneydanceContext.getUI().getMain().getSourceInformation().getIconResource()))


            if not SwingUtilities.isEventDispatchThread():
                myPrint("DB", ".. build_main_frame() Not running within the EDT so calling via BuildMainFrameRunnable()...")
                SwingUtilities.invokeLater(BuildMainFrameRunnable())
            else:
                myPrint("DB", ".. build_main_frame() Already within the EDT so calling naked...")
                BuildMainFrameRunnable().run()


        # .invoke() is called when this extension is selected on the Extension Menu.
        # the eventString is set to the string set when the class self-installed itself via .registerFeature() - e.g. "showConfig"
        def invoke(self, eventString=""):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
            myPrint("DB", "Extension .invoke() received command: %s. Passing onto .handleEvent()" %(eventString))

            result = self.handle_event(eventString, True)

            myPrint("DB", "Exiting ", inspect.currentframe().f_code.co_name, "()")
            return result

        def getMoneydanceUI(self):
            global debug    # global statement must be here as we can set debug here
            saveDebug = debug

            if GlobalVars.specialDebug:
                debug = True
                myPrint("B", "*** Switching on SPECIAL DEBUG here for .getMoneydanceUI() only......")

            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

            if not self.isUIavailable:
                myPrint("DB", "Checking to see whether the Moneydance UI is loaded yet....")

                f_ui_result = getFieldByReflection(self.moneydanceContext, "ui")

                myPrint("DB", "** SPECIAL: f_ui_result:", f_ui_result)
                if f_ui_result is None or f_ui_result.firstMainFrame is None:
                    myPrint("DB", ".. Nope - the Moneydance UI is NOT yet loaded (fully)..... so exiting...")
                    debug = saveDebug
                    return False

                myPrint("DB", "** SPECIAL: book:", self.moneydanceContext.getCurrentAccountBook())
                if self.moneydanceContext.getCurrentAccountBook() is None:
                    myPrint("DB", ".. The UI is loaded, but the dataset is not yet loaded... so exiting ...")
                    debug = saveDebug
                    return False

                try:
                    # I'm calling this on firstMainFrame rather than just .getUI().setStatus() to confirm GUI is properly loaded.....
                    myPrint("DB", "SPECIAL: pre-calling .firstMainFrame.setStatus()")

                    # self.moneydanceContext.getUI().firstMainFrame.setStatus(">> StuWareSoftSystems - %s:%s runtime extension installing......." %(self.myModuleID.capitalize(),GlobalVars.DEFAULT_WIDGET_DISPLAY_NAME.title()), -1.0)

                    genericSwingEDTRunner(False, False,
                                          self.moneydanceContext.getUI().firstMainFrame.setStatus,
                                          ">> StuWareSoftSystems - %s:%s runtime extension installing......." %(self.myModuleID.capitalize(),GlobalVars.DEFAULT_WIDGET_DISPLAY_NAME.title()),-1.0)

                    myPrint("DB", "SPECIAL: post-calling .firstMainFrame.setStatus()")

                except:
                    dump_sys_error_to_md_console_and_errorlog()
                    myPrint("B", "@@ ERROR - failed using the UI..... will just exit for now...")
                    debug = saveDebug
                    return False

                myPrint("DB", "Success - the Moneydance UI is loaded.... Extension can execute properly now...!")

                # Have to do .getUI() etc stuff here (and not at startup) as UI not loaded then. As of 4069, is blocked by MD!
                myPrint("DB", "SPECIAL: pre-calling setDefaultFonts()")

                genericSwingEDTRunner(False, False, setDefaultFonts)

                myPrint("DB", "SPECIAL: post-calling setDefaultFonts()")

                try: GlobalVars.defaultPrintFontSize = eval("MD_REF.getUI().getFonts().print.getSize()")
                except: GlobalVars.defaultPrintFontSize = 12

                myPrint("DB", "SPECIAL: pre-calling build_main_frame()")
                self.build_main_frame()
                self.isUIavailable = True
                myPrint("DB", "SPECIAL: post-calling build_main_frame()")
            else:
                myPrint("DB", "..UI is available - returning True....")

            myPrint("DB", "Exiting ", inspect.currentframe().f_code.co_name, "()")

            debug = saveDebug
            return True


        class UnloadUninstallSwingWorker(SwingWorker):
            def __init__(self, unload=False, uninstall=False):
                self.unload = unload
                self.uninstall = uninstall

            # noinspection PyMethodMayBeStatic
            def doInBackground(self):
                myPrint("DB", "In UnloadUninstallSwingWorker()", inspect.currentframe().f_code.co_name, "()")

                ct = Thread.currentThread()
                if "_extn_NAB" not in ct.getName(): ct.setName(u"%s_extn_NAB" %(ct.getName()))

                NAB = NetAccountBalancesExtension.getNAB()

                if self.unload:
                    myPrint("DB", "... calling .unloadMyself()")
                    NAB.unloadMyself()
                elif self.uninstall:
                    myPrint("DB", "... calling .removeMyself()")
                    NAB.removeMyself()

            # noinspection PyMethodMayBeStatic
            def done(self):
                myPrint("DB", "In UnloadUninstallSwingWorker()", inspect.currentframe().f_code.co_name, "()")
                myPrint("DB", "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

        def handle_event(self, appEvent, lPassedFromInvoke=False):

            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))

            if self.alreadyClosed:
                myPrint("DB", "....alreadyClosed (deactivated by user) but the listener is still here (MD EVENT %s CALLED).. - Ignoring and returning back to MD.... (restart to clear me out)..." %(appEvent))
                return

            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
            myPrint("DB", "Extension .handle_event() received command: %s (from .invoke() flag = %s)" %(appEvent, lPassedFromInvoke))

            if appEvent == "md:file:closing" or appEvent == "md:file:closed":

                self.rememberLastResultsTable = None

                self.parametersLoaded = self.configPanelOpen = False

                if self.theFrame is not None and self.theFrame.isVisible():
                    myPrint("DB", "Requesting application JFrame to go invisible...")
                    SwingUtilities.invokeLater(GenericVisibleRunnable(self.theFrame, False))

                self.resetJListModel()

                if appEvent == "md:file:closing":

                    with self.swingWorkers_LOCK:
                        myPrint("DB", "Cancelling any active SwingWorkers - all types....")
                        self.cancelSwingWorkers(lSimulates=True, lParallelRebuilds=True, lBuildHomePageWidgets=True)

                    myPrint("DB", "Closing all resources and listeners being used by View(s)")
                    MyHomePageView.getHPV().cleanupAsBookClosing()

            elif (appEvent == "md:file:opening"):  # Precedes file opened
                myPrint("DB", "%s Dataset is opening... Internal list of SwingWorkers as follows...:" %(appEvent))
                # self.swingWorkers = [];
                self.listAllSwingWorkers()

            elif (appEvent == "md:file:opened"):  # This is the key event when a file is opened

                if GlobalVars.specialDebug: myPrint("B", "'%s' >> SPECIAL DEBUG - Checking to see whether UI loaded and create application Frame" %(appEvent))
                myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

                class GetMoneydanceUIRunnable(Runnable):
                    def __init__(self, callingClass): self.callingClass = callingClass
                    def run(self):
                        cumulativeSleepTimeMS = 0
                        abortAfterSleepMS = (1000.0 * 15)     # Abort after 15 seconds of waiting..... Tough luck....!
                        sleepTimeMS = 500
                        if GlobalVars.specialDebug or debug: myPrint("B", "... GetMoneydanceUIRunnable sleeping for %sms..." %(sleepTimeMS))
                        Thread.sleep(sleepTimeMS)
                        cumulativeSleepTimeMS += sleepTimeMS
                        while cumulativeSleepTimeMS < abortAfterSleepMS:
                            _bk = self.callingClass.moneydanceContext.getCurrentAccountBook()
                            if _bk is not None:
                                _syncer = _bk.getSyncer()
                                if _syncer is not None:
                                    if _syncer.isSyncing():
                                        if GlobalVars.specialDebug or debug: myPrint("B", "... Moneydance appears to be syncing... will wait %sms..." %(sleepTimeMS))
                                        Thread.sleep(sleepTimeMS)
                                        cumulativeSleepTimeMS += sleepTimeMS
                                        continue
                                    else:
                                        myPrint("B", "... Moneydance reports that it's NOT syncing... so will continue to load UI...")
                            break

                        if cumulativeSleepTimeMS >= abortAfterSleepMS: myPrint("B", "... WARNING: sleep/wait loop aborted (after %sms) waiting for MD sync to finish... Continuing anyway..." %(cumulativeSleepTimeMS))

                        if GlobalVars.specialDebug or debug: myPrint("B", "... GetMoneydanceUIRunnable calling getMoneydanceUI()...")
                        self.callingClass.getMoneydanceUI()  # Check to see if the UI & dataset are loaded.... If so, create the JFrame too...

                if GlobalVars.specialDebug or debug: myPrint("B", "... firing off call to getMoneydanceUI() via new thread (so-as not to hang MD)...")
                _t = Thread(GetMoneydanceUIRunnable(self), "NAB_GetMoneydanceUIRunnable".lower())
                _t.setDaemon(True)
                _t.start()

                # myPrint("DB", "%s Checking to see whether UI loaded and create application Frame" %(appEvent))
                # self.getMoneydanceUI()  # Check to see if the UI & dataset are loaded.... If so, create the JFrame too...

                myPrint("B", "... end of routines after receiving  'md:file:opened' command....")

            elif (appEvent.lower().startswith(("%s:customevent:showConfig" %(self.myModuleID)).lower())):
                myPrint("DB", "%s Config screen requested - I might show it if conditions are appropriate" %(appEvent))

                self.getMoneydanceUI()  # Check to see if the UI & dataset are loaded.... If so, create the JFrame too...

                requestedRow = decodeCommand(appEvent)[1]
                if StringUtils.isInteger(requestedRow) and int(requestedRow) > 0:
                    myPrint("DB", "COMMAND: %s received... Detected Row Parameter: %s" %(appEvent, requestedRow))

                    if self.configPanelOpen:
                        self.storeJTextFieldsForSelectedRow()
                        myPrint("DB", "..Storing JTF/JRFs (Widget name, XValue) last edited on GUI before any switch of row...")
                    else:
                        myPrint("DB", "..Skipping store of JTF/JRFs (Widget name, XValue) as GUI is not open...")

                    self.switchFromHomeScreen = True
                    self.setSelectedRowIndex(int(requestedRow)-1)

                if self.theFrame is not None and self.isUIavailable and self.theFrame.isActiveInMoneydance:
                    myPrint("DB", "... launching the config screen...")
                    SwingUtilities.invokeLater(GenericVisibleRunnable(self.theFrame, True, True))
                else:
                    myPrint("DB", "Sorry, conditions are not right to allow the GUI to load. Ignoring request....")
                    myPrint("DB", "self.theFrame: %s" %(self.theFrame))
                    myPrint("DB", "self.isUIavailable: %s" %(self.isUIavailable))
                    myPrint("DB", "self.theFrame.isActiveInMoneydance: %s" %(self.theFrame.isActiveInMoneydance))       # noqa

            elif (appEvent.lower().startswith(("%s:customevent:saveSettings" %(self.myModuleID)).lower())):
                myPrint("DB", "%s Save settings requested - I might trigger a save if conditions are appropriate" %(appEvent))

                self.getMoneydanceUI()  # Check to see if the UI & dataset are loaded.... If so, create the JFrame too...

                if self.theFrame is not None and self.theFrame.isActiveInMoneydance:
                    myPrint("DB", "Triggering saveSettings() via Runnable....")
                    SwingUtilities.invokeLater(self.SaveSettingsRunnable())

            elif (appEvent.lower().startswith(("%s:customevent:showConsole" %(self.myModuleID)).lower())):
                myPrint("B", "%s Save settings requested - Triggering Help>Show Console" %(appEvent))
                SwingUtilities.invokeLater(ShowConsoleRunnable())

            elif (appEvent.lower().startswith(("%s:customevent:returnLastResults" %(self.myModuleID)).lower())):
                myPrint("B", "%s Return last results requested..." %(appEvent))

                _return = None
                try:
                    if self.rememberLastResultsTable is not None and len(self.rememberLastResultsTable) > 0:
                        # This builds a remembered table for other extensions to leverage....
                        _return = []
                        for i in range(0, len(self.rememberLastResultsTable)):
                            _row = self.rememberLastResultsTable[i]
                            _rowName = copy.copy(self.savedWidgetName[i])
                            _curr = copy.copy(_row[0].getUUID())      # Remove any objects, store only text
                            _val = copy.copy(_row[1])
                            _txt = copy.copy(_row[2])
                            _return.append([_rowName, _curr, _val, _txt])
                except:
                    myPrint("B", "ERROR building remembered results table... Will ignore and continue...")
                    dump_sys_error_to_md_console_and_errorlog()

                return _return

            elif (appEvent == "%s:customevent:close" %(self.myModuleID)):
                if debug:
                    myPrint("DB", "@@ Custom event %s triggered.... Will call .unloadMyself() to deactivate (via SwingWorker)...." %(appEvent))
                else:
                    myPrint("B", "@@ %s triggered - So I will deactivate myself...." %(appEvent))

                sw = self.UnloadUninstallSwingWorker(unload=True)
                sw.execute()
                myPrint("DB", "Back from calling .unloadMyself() via SwingWorker to deactivate... ;-> ** I'm getting out quick! **")

            elif (appEvent == "%s:customevent:uninstall" %(self.myModuleID)):
                if debug:
                    myPrint("DB", "@@ Custom event %s triggered.... Will call .removeMyself() to uninstall (via SwingWorker)...." %(appEvent))
                else:
                    myPrint("B", "@@ %s triggered - So I will uninstall/remove myself...." %(appEvent))

                sw = self.UnloadUninstallSwingWorker(uninstall=True)
                sw.execute()
                myPrint("DB", "Back from calling .removeMyself() via SwingWorker to deactivate... ;-> ** I'm getting out quick! **")

            else:
                myPrint("DB", "@@ Ignoring handle_event: %s (from .invoke() = %s) @@" %(appEvent,lPassedFromInvoke))

            if lPassedFromInvoke: return True

            return

        def unload(self, lFromDispose=False):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

            myPrint("B", "@@ Extension Unload called, either a uninstall or reinstall (or deactivate request)... Deactivate and unload...")

            NAB = NetAccountBalancesExtension.getNAB()

            self.theFrame.isActiveInMoneydance = False

            self.alreadyClosed = True

            if not lFromDispose:
                if not SwingUtilities.isEventDispatchThread():
                    SwingUtilities.invokeLater(GenericDisposeRunnable(self.theFrame))
                    myPrint("DB", "Pushed dispose() - via SwingUtilities.invokeLater() - Hopefully I will close to allow re-installation...\n")
                else:
                    GenericDisposeRunnable(self.theFrame).run()
                    myPrint("DB", "Called dispose() (direct as already on EDT) - Hopefully I will close to allow re-installation...\n")

            self.saveMyHomePageView.unload()
            myPrint("DB", "@@ Called HomePageView.unload()")

            try:
                myPrint("DB", "Removing myself from PreferenceListeners...")
                NAB.moneydanceContext.getPreferences().removeListener(self)
            except:
                myPrint("B", "@@ ERROR - failed to remove myself from PreferenceListeners?")

            self.moneydanceContext.getUI().setStatus(">> StuWareSoftSystems - thanks for using >> %s....... >> I am now unloaded...." %(GlobalVars.thisScriptName),0)

            myPrint("DB", "... Completed unload routines...")

    class SpecialJLinkLabel(JLinkLabel):
        def __init__(self, *args):
            super(self.__class__, self).__init__(*args)

            self.NAB = NetAccountBalancesExtension.getNAB()
            self.md = self.NAB.moneydanceContext
            self.fonts = self.md.getUI().getFonts()
            self.fonts.updateMetricsIfNecessary(self.getGraphics())
            self.maxBaseline = self.fonts.defaultMetrics.getMaxDescent()
            self.underlineStroke = BasicStroke(1.0, BasicStroke.CAP_BUTT, BasicStroke.JOIN_BEVEL, 1.0, [1.0, 6.0], 1.0 if (self.getHorizontalAlignment() == JLabel.LEFT) else 0.0)

        def paintComponent(self, g2d):
            if isinstance(self, JLabel): pass                                                                           # trick IDE into type checking
            if isinstance(g2d, Graphics2D): pass                                                                        # trick IDE into type checking

            super(self.__class__, self).paintComponent(g2d)
            if (not self.NAB.savedDisplayVisualUnderDots or g2d is None): return

            # html_view = self.getClientProperty("html")
            # if html_view is None: return
            # if isinstance(html_view, View): pass

            isLeftAlign = (self.getHorizontalAlignment() == JLabel.LEFT)

            x = 0
            y = 0
            w = self.getWidth()
            h = self.getHeight()
            insets = self.getInsets()

            # self.fonts.updateMetricsIfNecessary(g2d)
            # g2d.setFont(self.fonts.defaultText)

            viewR = Rectangle(w, h)
            iconR = Rectangle()
            textR = Rectangle()

            clippedText = SwingUtilities.layoutCompoundLabel(
                self,
                g2d.getFontMetrics(),
                self.getText(),
                self.getIcon(),
                self.getVerticalAlignment(),
                self.getHorizontalAlignment(),
                self.getVerticalTextPosition(),
                self.getHorizontalTextPosition(),
                viewR,
                iconR,
                textR,
                self.getIconTextGap()
            )
            if clippedText is None: pass

            visibleTextWidth = int(textR.getWidth())

            # visibleTextWidth = int(html_view.getPreferredSpan(View.X_AXIS))   # Only useful when html...

            baselineY = (y + self.getHeight() - self.maxBaseline - 1)

            if isLeftAlign:
                startDots = (visibleTextWidth + insets.left)
                lengthOfDots = (self.getWidth() - startDots)
            else:
                startDots = x
                lengthOfDots = (self.getWidth() - visibleTextWidth - insets.right)

            line = Path2D.Double()                                                                                      # noqa
            line.moveTo(w if isLeftAlign else 0.0, baselineY - insets.top)
            line.lineTo(0.0 if isLeftAlign else w, baselineY - insets.top)

            g2d.setColor(self.md.getUI().colors.defaultTextForeground)
            g2d.clipRect(startDots, 0, lengthOfDots, h)
            g2d.setStroke(self.underlineStroke)
            g2d.draw(line)

    class MyHomePageView(HomePageView, AccountListener, CurrencyListener):

        HPV = None

        @staticmethod
        def getHPV():
            if MyHomePageView.HPV is not None: return MyHomePageView.HPV
            with GlobalVars.EXTENSION_LOCK:
                myPrint("DB", "Creating and returning a new single instance of MyHomePageView() using extension lock....")
                MyHomePageView.HPV = MyHomePageView()
            return MyHomePageView.HPV

        def __init__(self):

            self.myModuleID = myModuleID

            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

            self.generatedView = None       # Transitory object
            self.views = []                 # New for build 1020.. Enabling multi home screen views....
            self.viewPnlCounter = 0
            self.myModuleID = myModuleID

            self.refresher = None
            self.lastRefreshTimeDelayMs = 3000      # was originally 10000
            self.lastRefreshTriggerWasAccountModified = False

            self.is_unloaded = False

            # my attempt to replicate Java's 'synchronized' statements
            self.HPV_LOCK = threading.Lock()

            # self.refresher = CollapsibleRefresher(self.GUIRunnable(self))
            self.refresher = MyCollapsibleRefresher(self.GUIRunnable())

        # noinspection PyMethodMayBeStatic
        def getID(self): return self.myModuleID

        # noinspection PyMethodMayBeStatic
        def __str__(self): return GlobalVars.DEFAULT_WIDGET_DISPLAY_NAME.title()

        # noinspection PyMethodMayBeStatic
        def __repr__(self): return self.__str__()

        # noinspection PyMethodMayBeStatic
        def toString(self): return self.__str__()

        def currencyTableModified(self, currencyTable):                                                                 # noqa
            myPrint("DB", "In MyHomePageView.currencyTableModified()")
            self.listenerTriggeredAction()

        def accountModified(self, paramAccount):                                                                        # noqa
            myPrint("DB", "In MyHomePageView.accountModified()")
            self.listenerTriggeredAction(lFromAccountListener=True)

        def accountBalanceChanged(self, paramAccount):                                                                  # noqa
            myPrint("DB", "In MyHomePageView.accountBalanceChanged()")
            self.listenerTriggeredAction(lFromAccountListener=True)

        def accountDeleted(self, paramAccount):                                                                         # noqa
            myPrint("DB", "In MyHomePageView.accountDeleted()")
            myPrint("DB", "... ignoring....")

        def accountAdded(self, paramAccount):                                                                           # noqa
            myPrint("DB", "In MyHomePageView.accountAdded()")
            myPrint("DB", "... ignoring....")

        def listenerTriggeredAction(self, lFromAccountListener=False):
            myPrint("DB", ".listenerTriggeredAction(lFromAccountListener=%s) triggered" %(lFromAccountListener))
            if self.areAnyViewsActive(False):
                myPrint("DB", "... calling refresh(lFromAccountListener=%s)" %(lFromAccountListener))
                self.refresh(lFromAccountListener=lFromAccountListener)
            else:
                myPrint("DB", "... no views appear active... deactivating listeners...")
                # genericThreadRunner(True, self.deactivateListeners)
                self.deactivateListeners()

        def activateListeners(self):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
            NAB = NetAccountBalancesExtension.getNAB()
            with NAB.NAB_LOCK:
                if not NAB.listenersActive:
                    myPrint("DB", ".. activateListeners().. Adding myself as (HomePageView) AccountBook & Currency listener(s)...")
                    book = NetAccountBalancesExtension.getNAB().moneydanceContext.getCurrentAccountBook()
                    myPrint("DB", "... activateListeners() detected book:", book)
                    book.addAccountListener(self)
                    book.getCurrencies().addCurrencyListener(self)
                else:
                    myPrint("DB", ".. activateListeners().. SKIPPING adding myself as (HomePageView) AccountBook & Currency listener(s) - as already active...")
                NAB.listenersActive = True

        def deactivateListeners(self):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
            NAB = NetAccountBalancesExtension.getNAB()
            book = NAB.moneydanceContext.getCurrentAccountBook()
            with NAB.NAB_LOCK:
                if NAB.listenersActive:
                    myPrint("DB", ".. deactivateListeners().. Removing myself as (HomePageView) AccountBook & Currency listener(s)... Book:", book)
                    try:
                        book.removeAccountListener(self)
                    except:
                        e, exc_value, exc_traceback = sys.exc_info()                                                    # noqa
                        myPrint("B", "@@ ERROR calling .removeAccountListener() on:", self)
                        myPrint("B", "Error:", e)
                        myPrint("B", ".. will ignore and continue")

                    try:
                        book.getCurrencies().removeCurrencyListener(self)
                    except:
                        e, exc_value, exc_traceback = sys.exc_info()                                                    # noqa
                        myPrint("B", "@@ ERROR calling .removeCurrencyListener() on:", self)
                        myPrint("B", "Error:", e)
                        myPrint("B", ".. will ignore and continue")
                else:
                    myPrint("DB", ".. deactivateListeners().. SKIPPING removing myself as (HomePageView) AccountBook & Currency listener(s) - as already NOT active... Book:", book)

                NAB.listenersActive = False


        # The Runnable for CollapsibleRefresher() >> Doesn't really need to be a Runnable as .run() is called directly
        class GUIRunnable(Runnable):

            def __init__(self):
                myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))

            # noinspection PyMethodMayBeStatic
            def run(self):
                myPrint("DB", "Inside GUIRunnable.... Calling .reallyRefresh()..")
                MyHomePageView.getHPV().reallyRefresh()

        @staticmethod
        def getCurrencyByUUID(uuid, defaultBase):
            # myPrint("DB", ".getCurrencyByUUID() passed: '%s' '%s'" %(uuid, defaultBase))
            if uuid is None or uuid == "":
                curr = defaultBase
                # myPrint("DB", "Currency uuid passed was '%s' - returning defaultBase: %s" %(uuid, curr))
            else:
                curr = NetAccountBalancesExtension.getNAB().moneydanceContext.getCurrentAccountBook().getCurrencies().getCurrencyByUUID(uuid)

                if curr is None:
                    myPrint("DB", "WARNING.... Currency for uuid: %s MISSING: Reverting to base: %s" %(uuid, defaultBase))
                    curr = defaultBase
                else:
                    # myPrint("DB", "Currency for uuid: %s found: %s" %(uuid, curr))
                    pass

            return curr

        def areAnyViewsActive(self, obtainLockFirst=True):
            with (self.HPV_LOCK if (obtainLockFirst) else NoneLock()):
                for _viewWR in self.views:
                    _view = _viewWR.get()
                    if isSwingComponentValid(_view): return True
                return False

        def cleanupDeadViews(self, obtainLockFirst=True):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            with (self.HPV_LOCK if (obtainLockFirst) else NoneLock()):
                myPrint("DB", "... Pre-purge - Number of remembered Views(widgets): %s" %(len(self.views)))
                for i in reversed(range(0, len(self.views))):
                    _viewWR = self.views[i]
                    if isSwingComponentInvalid(_viewWR.get()):
                        myPrint("DB", "... Erasing (old) View(WIDGET) from my memory as seems to no longer exist (or is invalid):", _viewWR)
                        self.views.pop(i)
                if debug:
                    myPrint("B", "... Post-purge - Number of remembered Views(widgets): %s" %(len(self.views)))
                    for _viewWR in self.views:
                        _view = _viewWR.get()
                        if _view is not None:
                            myPrint("B", "...... keeping valid view: %s (valid: %s)" %(classPrinter(_view.getName(), _view), isSwingComponentValid(_view)))

        # Called by Moneydance; Must returns a (swing JComponent) GUI component that provides a view for the given data file.
        def getGUIView(self, book):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
            myPrint("DB", "HomePageView: .getGUIView(%s)" %(book))

            NAB = NetAccountBalancesExtension.getNAB()

            if self.is_unloaded:
                myPrint("DB", "HomePageView is unloaded, so ignoring....")
                return None     # this hides the widget from the home screen

            if not NAB.parametersLoaded:
                myPrint("DB", "LOADING PARAMETERS..... (if not already set)....")
                NAB.load_saved_parameters()

            myPrint("DB", "... Setting up CreateViewPanelRunnable to create ViewPanel etc....")


            class CreateViewPanelRunnable(Runnable):

                def __init__(self): pass

                # noinspection PyMethodMayBeStatic
                def run(self):
                    HPV = MyHomePageView.getHPV()
                    myPrint("DB", "Inside CreateViewPanelRunnable().... Calling creating ViewPanel..")
                    HPV.generatedView = HPV.ViewPanel()

            with self.HPV_LOCK:
                if not SwingUtilities.isEventDispatchThread():
                    myPrint("DB", ".. Not running within the EDT so calling via CreateViewPanelRunnable()...")
                    SwingUtilities.invokeAndWait(CreateViewPanelRunnable())
                else:
                    myPrint("DB", ".. Already within the EDT so calling CreateViewPanelRunnable() naked...")
                    CreateViewPanelRunnable().run()

                self.viewPnlCounter += 1
                self.generatedView.setName("%s_ViewPanel_%s" %(self.myModuleID, str(self.viewPnlCounter)))
                myPrint("DB", "... Created ViewPanel: %s" %(classPrinter(self.generatedView.getName(), self.generatedView)))

                _returnView = self.generatedView
                self.generatedView = None
                self.views.append(WeakReference(_returnView))
                # self.refresh()    # Not sure this is needed as .setActive(True) should follow soon after...

                self.activateListeners()

                return _returnView

        def getBalancesBuildView(self, swClass):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

            HPV = self
            book = NetAccountBalancesExtension.getNAB().moneydanceContext.getCurrentAccountBook()

            totalBalanceTable = []

            if HPV.is_unloaded:
                myPrint("DB", "HomePageView is unloaded, so ignoring & returning zero....")
                return totalBalanceTable

            if book is None:
                myPrint("DB", "HomePageView: book is None - returning zero...")
                return totalBalanceTable

            if NetAccountBalancesExtension.getNAB().getNumberOfRows() < 1:
                myPrint("DB", "...savedAccountListUUIDs is empty - returning zero...")
                return totalBalanceTable

            myPrint("DB", "HomePageView: (re)calculating balances")

            if not swClass.isCancelled():
                totalBalanceTable = MyHomePageView.calculateBalances(book, swClass=swClass)

            return totalBalanceTable

        @staticmethod
        def calculateBalances(_book, justIndex=None, lFromSimulate=False, swClass=None):                                # noqa

            myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()")

            NAB = NetAccountBalancesExtension.getNAB()

            if _book is None or (swClass and swClass.isCancelled()): return []

            baseCurr = _book.getCurrencies().getBaseType()

            _curIdx = 0; _valIdx = 1; _secLabelTextIdx = 2
            _totalBalanceTable = []

            incExpTxnTable = buildEmptyTxnOrBalanceArray()

            try:
                startTime = System.currentTimeMillis()

                # saveTheRowIndex = (NAB.getSelectedRowIndex() if not lFromSimulate else None)

                isParallelBalanceTableOperational()

                # --------------------------------------------------------------------------------------------------
                accountsToShow = buildEmptyAccountList()
                for iAccountLoop in range(0, NAB.getNumberOfRows()):

                    if swClass and swClass.isCancelled(): return []

                    onRow = iAccountLoop + 1

                    if justIndex is not None and iAccountLoop != justIndex: continue
                    if NAB.savedHideRowWhenXXXTable[iAccountLoop] == GlobalVars.HIDE_ROW_WHEN_ALWAYS: continue

                    myPrint("DB", "HomePageView: Finding selected accounts for row: %s" %(onRow))
                    # if not lFromSimulate: NAB.setSelectedRowIndex(iAccountLoop)

                    for accID in NAB.savedAccountListUUIDs[iAccountLoop]:

                        if swClass and swClass.isCancelled(): return []

                        myPrint("DB", "... Row: %s - looking for Account with UUID: %s" %(onRow, accID))
                        # acct = AccountUtil.findAccountWithID(_book.getRootAccount(), accID)                       # Very slow...
                        acct = NAB.moneydanceContext.getCurrentAccountBook().getAccountByUUID(accID)

                        if acct is not None:
                            # myPrint("DB", "....found and adding account to list: %s" %acct)
                            accountsToShow[iAccountLoop].append(acct)

                        else:
                            myPrint("B", "....WARNING - Row: %s >> Account with UUID %s not found..? Skipping this one...." %(onRow, accID))

                tookTime = System.currentTimeMillis() - startTime
                myPrint("DB", "calculateBalances() STAGE1>> TOOK: %s milliseconds (%s seconds)" %(tookTime, tookTime / 1000.0))
                startTime = System.currentTimeMillis()

                # Printing of lists containing objects which return multi-bye characters (e.g. Asian) will error - e.g. print [acct]
                try: myPrint("DB", "accountsToShow table: %s" %accountsToShow)
                except: pass

                # --------------------------------------------------------------------------------------------------
                lIncExpData = False

                # Income / Expense harvest associated accounts
                for iAccountLoop in range(0, NAB.getNumberOfRows()):

                    if swClass and swClass.isCancelled(): return []

                    # if not lFromSimulate: NAB.setSelectedRowIndex(iAccountLoop)

                    onRow = iAccountLoop + 1

                    incExpAccountsList = []

                    if justIndex is not None and iAccountLoop != justIndex: continue
                    if NAB.savedHideRowWhenXXXTable[iAccountLoop] == GlobalVars.HIDE_ROW_WHEN_ALWAYS: continue

                    if not isIncomeExpenseAllDatesSelected(iAccountLoop):
                        myPrint("DB", "HomePageView: Income/Expense Date Range '%s' used on Row: %s (will gather child accounts (if AutoSum) and all related income/expense transactions). AutoSum = %s"
                                %(NAB.savedIncomeExpenseDateRange[iAccountLoop], onRow, NAB.savedAutoSumAccounts[iAccountLoop]))

                        for acct in accountsToShow[iAccountLoop]:

                            if swClass and swClass.isCancelled(): return []

                            returnThisAccountAndAllChildren(acct, _listAccounts=incExpAccountsList,autoSum=NAB.savedAutoSumAccounts[iAccountLoop], justIncomeExpense=True)

                        if len(incExpAccountsList) > 0:
                            myPrint("DB", "...incExpAccountsList contains %s Income/Expense accounts... Populating Inc/Exp table - row: %s" %(len(incExpAccountsList), onRow))

                            lIncExpData = True

                            for acct in incExpAccountsList:
                                incExpTxnTable[iAccountLoop][acct] = []
                        else:

                            myPrint("DB", "...No Income/Expense Accounts found for row: %s" %(onRow))

                tookTime = System.currentTimeMillis() - startTime
                myPrint("DB", "calculateBalances() STAGE2>> TOOK: %s milliseconds (%s seconds)" %(tookTime, tookTime / 1000.0))
                startTime = System.currentTimeMillis()

                # Income / Expense harvest associated Txns - all in one sweep....
                if not lIncExpData:
                    myPrint("DB", "HomePageView: No IncExp Data requested or no accounts found... Skipping the harvesting of associated Txns...")
                    incExpBalanceTable = []

                else:

                    myPrint("DB", "HomePageView: IncExp Data found... Harvesting associated Txns")
                    returnTransactionsForAccounts(incExpTxnTable, swClass)
                    if swClass and swClass.isCancelled(): return []

                    myPrint("DB", "HomePageView: Converting IncExp Txns into Balances...")
                    incExpBalanceTable = convertTxnTableIntoBalances(incExpTxnTable, swClass)
                    if swClass and swClass.isCancelled(): return []

                # --------------------------------------------------------------------------------------------------

                lWarningDetected = False
                iWarningType = None
                iWarningDetectedInRow = None

                # Iterate each row
                for iAccountLoop in range(0, len(accountsToShow)):

                    if swClass and swClass.isCancelled(): return []

                    # if not lFromSimulate: NAB.setSelectedRowIndex(iAccountLoop)

                    lFoundAutoSumParentInThisRowWarning = False
                    lFoundAutoSumInActiveChildInThisThisRowWarning = False
                    lFoundAutoSumInActiveParentInThisThisRowWarning = False

                    onRow = iAccountLoop + 1

                    iCountIncomeExpense = 0
                    iCountAccounts = 0
                    iCountNonInvestAccounts = 0
                    iCountSecurities = 0

                    lFoundNonSecurity = False
                    secLabelText = ""

                    thisRowCurr = MyHomePageView.getCurrencyByUUID(NAB.savedCurrencyTable[iAccountLoop], baseCurr)

                    myPrint("DB", "HomePageView: calculating balances for widget row: %s '%s' (currency to display: %s)" %(onRow, NAB.savedWidgetName[iAccountLoop], thisRowCurr))

                    if len(accountsToShow[iAccountLoop]) < 1:
                        totalBalance = None

                    else:

                        totalBalance = 0

                        # Iterate each selected account within the row...
                        for acct in accountsToShow[iAccountLoop]:

                            if swClass and swClass.isCancelled(): return []

                            # noinspection PyUnresolvedReferences
                            if acct.getAccountType() == Account.AccountType.SECURITY:
                                iCountSecurities += 1
                            elif isIncomeExpenseAcct(acct):
                                iCountIncomeExpense += 1
                            else:
                                # noinspection PyUnresolvedReferences
                                if acct.getAccountType() != Account.AccountType.INVESTMENT:
                                    iCountNonInvestAccounts += 1
                                iCountAccounts += 1

                            realAutoSum = NAB.savedAutoSumAccounts[iAccountLoop]

                            if debug or (NAB.savedShowWarningsTable[iAccountLoop]):

                                # Validate selections.... Look for AutoSum'd accounts where a parent has been selected..
                                if not NAB.migratedParameters:
                                    myPrint("DB", "... Verifying for illogical calculations up/down hierarchy...")
                                    if realAutoSum:

                                        if not lFoundAutoSumParentInThisRowWarning:
                                            parentPath = acct.getPath()[:-1]
                                            for checkParentAcct in parentPath:
                                                if checkParentAcct in accountsToShow[iAccountLoop]:
                                                    lWarningDetected = True
                                                    iWarningType = (1 if (iWarningType is None or iWarningType == 1) else 0)
                                                    iWarningDetectedInRow = (onRow if (iWarningDetectedInRow is None or iWarningDetectedInRow == onRow) else 0)
                                                    myPrint("B", "WARNING: Row: %s >> AutoSum ON and Selected acct '%s' is being double totalled by selected AutoSum'd parent acct: '%s'"
                                                                " (stopping further checks...)" %(onRow, acct, checkParentAcct))
                                                    lFoundAutoSumParentInThisRowWarning = True
                                                    break

                                        # Eliminated this slow way of doing it....
                                        # for checkAcct in accountsToShow[iAccountLoop]:
                                        #
                                        #     if swClass and swClass.isCancelled(): return []
                                        #
                                        #     if acct == checkAcct: continue
                                        #
                                        #     if acct in checkAcct.getPath()[:-1]:
                                        #         lWarningDetected = True
                                        #         iWarningType = (1 if (iWarningType is None or iWarningType == 1) else 0)
                                        #         iWarningDetectedInRow = (onRow if (iWarningDetectedInRow is None or iWarningDetectedInRow == onRow) else 0)
                                        #         myPrint("B", "WARNING: Row: %s >> AutoSum ON and Selected acct: %s found in parent acct hierarchy: '%s' "
                                        #                      "when ultimate parent: '%s' also selected" %(onRow, checkAcct, checkAcct.getPath()[:-1], acct));

                                        if not lFoundAutoSumInActiveChildInThisThisRowWarning:
                                            if not NAB.savedIncludeInactive[iAccountLoop]:
                                                inactiveChild = accountIncludesInactiveChildren(acct, NAB.savedBalanceType[iAccountLoop])
                                                if inactiveChild:
                                                    lWarningDetected = True
                                                    iWarningType = (2 if (iWarningType is None or iWarningType == 2) else 0)
                                                    iWarningDetectedInRow = (onRow if (iWarningDetectedInRow is None or iWarningDetectedInRow == onRow) else 0)
                                                    myPrint("B", "WARNING: Row: %s >> AutoSum ON, Excluding Inactive Accounts, BUT account: '%s' includes inactive child with a balance: '%s'"
                                                                " (stopping further checks...)" %(onRow, acct, inactiveChild))
                                                    lFoundAutoSumInActiveChildInThisThisRowWarning = True

                                    if not lFoundAutoSumInActiveParentInThisThisRowWarning:
                                        if not NAB.savedIncludeInactive[iAccountLoop] and not isAccountActive(acct, NAB.savedBalanceType[iAccountLoop]):
                                            lWarningDetected = True
                                            iWarningType = (3 if (iWarningType is None or iWarningType == 3) else 0)
                                            iWarningDetectedInRow = (onRow if (iWarningDetectedInRow is None or iWarningDetectedInRow == onRow) else 0)
                                            myPrint("B", "WARNING: Row: %s >> Excluding Inactive Accounts, BUT selected acct / parent hierarchy flagged as inactive somewhere: %s"
                                                        " (stopping further checks...)" %(onRow, acct))
                                            lFoundAutoSumInActiveParentInThisThisRowWarning = True

                            # noinspection PyUnresolvedReferences
                            if acct.getAccountType() != Account.AccountType.SECURITY:
                                lFoundNonSecurity = True
                            elif not lFoundNonSecurity:
                                secLabelText = " (Securities)"

                            if NAB.migratedParameters:
                                # noinspection PyUnresolvedReferences
                                if acct.getAccountType() == Account.AccountType.INVESTMENT:
                                    autoSumFlag = True
                                else:
                                    autoSumFlag = False
                                myPrint("DB", "Migrated parameters... Overriding AutoSum from %s to %s on acct: %s" %(realAutoSum, autoSumFlag, acct))
                            else:
                                autoSumFlag = realAutoSum

                            # 0 = "Balance", 1 = "Current Balance", 2 = "Cleared Balance"

                            acctCurr = acct.getCurrencyType()
                            if (isIncomeExpenseAcct(acct) and not isIncomeExpenseAllDatesSelected(iAccountLoop)):
                                myPrint("DB", ">> RowIdx: %s - Income/Expense date range: %s - Swapping in recalculated balances....:" %(iAccountLoop, NAB.savedIncomeExpenseDateRange[iAccountLoop]))

                                try: sudoAcctRef = incExpBalanceTable[iAccountLoop][acct]                           # type: HoldBalance
                                except KeyError:
                                    myPrint("B", "@@ KeyError - Row: %s - Trying to access 'incExpBalanceTable[%s]' with Account: '%s'" %(onRow, iAccountLoop,acct))
                                    raise

                            else:
                                myPrint("DB", ">> RowIdx: %s - No Special Income/Expense date range - retaining system calculated balances....:" %(iAccountLoop))
                                sudoAcctRef = acct                                                                  # type: Account

                            if NAB.savedBalanceType[iAccountLoop] == GlobalVars.BALTYPE_BALANCE:
                                bal = sudoAcctRef.getBalance() if not autoSumFlag else sudoAcctRef.getRecursiveBalance()
                                # myPrint("DB", "HomePageView: adding acct: %s Balance: %s - RecursiveAutoSum: %s"
                                #         %((sudoAcctRef.getFullAccountName()), rpad(acctCurr.formatSemiFancy(bal, NAB.decimal),12), autoSumFlag))
                                myPrint("DB", "HomePageView: adding acct: %s Balance: %s - RecursiveAutoSum: %s"
                                        %((sudoAcctRef.getFullAccountName()), rpad(formatSemiFancy(acctCurr, bal, NAB.decimal, indianFormat=NAB.savedUseIndianNumberFormat),12), autoSumFlag))
                            elif NAB.savedBalanceType[iAccountLoop] == GlobalVars.BALTYPE_CURRENTBALANCE:
                                bal = sudoAcctRef.getCurrentBalance() if not autoSumFlag else sudoAcctRef.getRecursiveCurrentBalance()
                                # myPrint("DB", "HomePageView: adding acct: %s Current Balance: %s - RecursiveAutoSum: %s"
                                #         %((sudoAcctRef.getFullAccountName()), rpad(acctCurr.formatSemiFancy(bal, NAB.decimal),12), autoSumFlag))
                                myPrint("DB", "HomePageView: adding acct: %s Current Balance: %s - RecursiveAutoSum: %s"
                                        %((sudoAcctRef.getFullAccountName()), rpad(formatSemiFancy(acctCurr, bal, NAB.decimal, indianFormat=NAB.savedUseIndianNumberFormat),12), autoSumFlag))
                            elif NAB.savedBalanceType[iAccountLoop] == GlobalVars.BALTYPE_CLEAREDBALANCE:
                                bal = sudoAcctRef.getClearedBalance() if not autoSumFlag else sudoAcctRef.getRecursiveClearedBalance()
                                # myPrint("DB", "HomePageView: adding acct: %s Cleared Balance: %s - RecursiveAutoSum: %s"
                                #         %((sudoAcctRef.getFullAccountName()), rpad(acctCurr.formatSemiFancy(bal, NAB.decimal),12), autoSumFlag))
                                myPrint("DB", "HomePageView: adding acct: %s Cleared Balance: %s - RecursiveAutoSum: %s"
                                        %((sudoAcctRef.getFullAccountName()), rpad(formatSemiFancy(acctCurr, bal, NAB.decimal, indianFormat=NAB.savedUseIndianNumberFormat),12), autoSumFlag))
                            else:
                                bal = 0
                                myPrint("B", "@@ HomePageView widget - INVALID BALANCE TYPE: %s?" %(NAB.savedBalanceType[iAccountLoop]))

                            mult = 1
                            if isIncomeExpenseAcct(acct): mult = -1

                            # This bit is neat, as it seems to work for Securities with just the qty balance!!
                            if bal != 0 and acctCurr != thisRowCurr:
                                balConv = CurrencyUtil.convertValue(bal, acctCurr, thisRowCurr)                     # todo - should this include an asof date?
                                # myPrint("DB", ".. Converted %s to %s (%s)" %(acctCurr.formatSemiFancy(bal, NAB.decimal), thisRowCurr.formatSemiFancy(balConv, NAB.decimal), thisRowCurr))
                                myPrint("DB", ".. Converted %s to %s (%s)"
                                        %(formatSemiFancy(acctCurr, bal, NAB.decimal, indianFormat=NAB.savedUseIndianNumberFormat),
                                          formatSemiFancy(thisRowCurr, balConv, NAB.decimal, indianFormat=NAB.savedUseIndianNumberFormat), thisRowCurr))
                                totalBalance += (balConv * mult)
                            else:
                                totalBalance += (bal * mult)

                        if debug or NAB.savedShowWarningsTable[iAccountLoop]:
                            # DETECT ILLOGICAL CALCULATIONS
                            if ((iCountIncomeExpense and (iCountAccounts))
                                    or (iCountSecurities and (iCountIncomeExpense))):

                                lWarningDetected = True
                                iWarningType = (4 if (iWarningType is None or iWarningType == 4) else 0)
                                iWarningDetectedInRow = (onRow if (iWarningDetectedInRow is None or iWarningDetectedInRow == onRow) else 0)

                                myPrint("B", "WARNING: Row: %s >> Mix and match of different accounts/categories/securities detected. Accts: %s, NonInvestAccts: %s, Securities: %s, I/E Categories: %s"
                                        %(onRow, iCountAccounts, iCountNonInvestAccounts, iCountSecurities, iCountIncomeExpense))


                    _totalBalanceTable.append([thisRowCurr,totalBalance,secLabelText])

                del accountsToShow, totalBalance, incExpTxnTable, incExpAccountsList

                tookTime = System.currentTimeMillis() - startTime
                myPrint("DB", "calculateBalances() STAGE3>> TOOK: %s milliseconds (%s seconds)" %(tookTime, tookTime / 1000.0))
                startTime = System.currentTimeMillis()

                for i in range(0,len(_totalBalanceTable)):
                    if _totalBalanceTable[i][_valIdx] is None:
                        result = "<NONE>"
                    elif _totalBalanceTable[i][_valIdx] == 0:
                        result = "<ZERO>"
                    else:
                        result = _totalBalanceTable[i][_valIdx] / 100.0
                    myPrint("DB", ".. Row: %s - DEBUG >> Calculated a total (potentially mixed currency) total of %s" %(i+1, result))

                NAB.warningInParametersDetected = lWarningDetected
                NAB.warningInParametersDetectedType = iWarningType
                NAB.warningInParametersDetectedInRow = iWarningDetectedInRow
                if NAB.warningInParametersDetected: myPrint("B", "@@ WARNING(S) in parameter setup detected... review setup....")

                # if not lFromSimulate: NAB.setSelectedRowIndex(saveTheRowIndex);

                tookTime = System.currentTimeMillis() - startTime
                if debug or (tookTime >= 1000):
                    myPrint("B", ">> CALCULATE BALANCES TOOK: %s milliseconds (%s seconds)"
                            %(tookTime, tookTime / 1000.0))

            except AttributeError as e:
                _totalBalanceTable = []
                if not detectMDClosingError(e): raise

            except IllegalArgumentException:
                _totalBalanceTable = []
                myPrint("B", "@@ ERROR - Probably on a multi-byte character.....")
                dump_sys_error_to_md_console_and_errorlog()
                raise

            return _totalBalanceTable

        class BuildHomePageWidgetSwingWorker(SwingWorker):

            def __init__(self, pleaseWaitLabel, callingClass):
                self.pleaseWaitLabel = pleaseWaitLabel
                self.callingClass = callingClass
                self.netAmountTable = None
                self.widgetOnPnlRow = 0
                self.widgetSeparatorsUsed = []

                NAB = NetAccountBalancesExtension.getNAB()
                with NAB.swingWorkers_LOCK:
                    NAB.swingWorkers.append(self)

            def isBuildHomePageWidgetSwingWorker(self):         return True
            def isSimulateTotalForRowSwingWorker(self):         return False
            def isRebuildParallelBalanceTableSwingWorker(self): return False

            def doInBackground(self):                                                                                   # Runs on a worker thread
                myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))

                ct = Thread.currentThread()
                if "_extn_NAB" not in ct.getName(): ct.setName(u"%s_extn_NAB" %(ct.getName()))

                result = False

                try:
                    NAB = NetAccountBalancesExtension.getNAB()
                    HPV = MyHomePageView.getHPV()

                    if HPV.lastRefreshTriggerWasAccountModified:
                        myPrint("DB", "** BuildHomePageWidgetSwingWorker.doInBackground() will now sleep for %s seconds as last trigger for .reallyRefresh() was an Account Listener... (unless I get superceded and cancelled)"
                                %(HPV.lastRefreshTimeDelayMs / 1000.0))
                        Thread.sleep(HPV.lastRefreshTimeDelayMs)
                        myPrint("DB", ".. >> Back from my sleep.... Now will reallyRefresh....!")

                    self.netAmountTable = self.callingClass.getBalancesBuildView(self)

                    NAB.rememberLastResultsTable = self.netAmountTable

                    if self.netAmountTable is not None and len(self.netAmountTable) > 0:
                        result = True

                except AttributeError as e:
                    if not detectMDClosingError(e): raise

                except InterruptedException:
                    myPrint("DB", "@@ BuildHomePageWidgetSwingWorker InterruptedException - aborting...")

                except CancellationException:
                    myPrint("DB", "@@ BuildHomePageWidgetSwingWorker CancellationException - aborting...")

                except:
                    myPrint("B", "@@ ERROR Detected in BuildHomePageWidgetSwingWorker running: getBalancesBuildView() inside ViewPanel")
                    dump_sys_error_to_md_console_and_errorlog()

                return result

            def addRowSeparator(self, theView):
                countConsecutive = 0
                for i in [1, 2]:
                    if (self.widgetOnPnlRow - i) in self.widgetSeparatorsUsed:
                        countConsecutive += 1
                if countConsecutive >= 2: return
                theView.listPanel.add(JSeparator(), GridC.getc().xy(0, self.widgetOnPnlRow).wx(1.0).fillx().pady(2).leftInset(15).rightInset(15).colspan(2))
                self.widgetSeparatorsUsed.append(self.widgetOnPnlRow)
                self.widgetOnPnlRow += 1

            def done(self):  # Executes on the EDT
                myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))

                NAB = NetAccountBalancesExtension.getNAB()
                HPV = MyHomePageView.getHPV()
                md = NAB.moneydanceContext

                with HPV.HPV_LOCK:
                    blinkers = []
                    thisViewsBlinkers = []                                                                              # noqa

                    try:
                        result = self.get()  # wait for process to finish
                        myPrint("DB", "..done() reports: %s" %(result))

                        for _viewWR in HPV.views:
                            _view = _viewWR.get()
                            if _view is None:
                                myPrint("DB", "... skipping View(WIDGET) as no longer exists (or is invalid):", _viewWR)
                                continue

                            self.widgetOnPnlRow = 0
                            self.widgetSeparatorsUsed = []
                            thisViewsBlinkers = []

                            if debug:
                                mfRef = SwingUtilities.getWindowAncestor(_view)
                                mfName = "None" if (mfRef is None) else classPrinter(getSwingObjectProxyName(mfRef), mfRef)
                                myPrint("B", ".. Rebuilding the widget view panel... view: %s, main frame: %s (valid: %s)"
                                        %(classPrinter(_view.getName(), _view), mfName, isSwingComponentValid(_view)))
                                del mfRef, mfName

                            _view.setVisible(False)
                            _view.listPanel.removeAll()

                            if NAB.savedDisableWidgetTitle:
                                if _view.headerPanel in _view.getComponents():
                                    _view.remove(_view.headerPanel)
                            else:
                                if _view.headerPanel not in _view.getComponents():
                                    _view.add(_view.headerPanel, GridC.getc().xy(0, 0).wx(1.0).fillx())

                            altFG = md.getUI().colors.tertiaryTextFG

                            if result and not NAB.savedExpandedView: pass
                            elif result:

                                baseCurr = md.getCurrentAccountBook().getCurrencies().getBaseType()

                                _curIdx = 0; _valIdx = 1; _secLabelTextIdx = 2

                                hiddenRows = False

                                if not NAB.configSaved:
                                    rowText = " ** CLICK TO SAVE SETTINGS **"
                                    nameLabel = JLinkLabel(rowText, "saveSettings", JLabel.LEFT)
                                    nameLabel.setForeground(md.getUI().colors.negativeBalFG)                            # noqa
                                    nameLabel.setDrawUnderline(False)
                                    nameLabel.setBorder(_view.nameBorder)                                               # noqa

                                    _view.listPanel.add(nameLabel, GridC.getc().xy(0, self.widgetOnPnlRow).wx(1.0).filly().west().pady(2))
                                    self.widgetOnPnlRow += 1

                                    nameLabel.addLinkListener(_view)
                                    thisViewsBlinkers.append(nameLabel)

                                    self.addRowSeparator(_view)

                                for i in range(0, len(self.netAmountTable)):

                                    onRow = i + 1

                                    if NAB.savedHideRowWhenXXXTable[i] == GlobalVars.HIDE_ROW_WHEN_ALWAYS:
                                        myPrint("DB", "** Skipping disabled row %s" %(onRow))
                                        hiddenRows = True
                                        continue

                                    lUseAverage = (NAB.savedDisplayAverageTable[i] != 1.0)
                                    balanceOrAverage = self.netAmountTable[i][_valIdx]

                                    if balanceOrAverage is not None:
                                        skippingRow = False

                                        if lUseAverage:
                                            balanceOrAverage = self.netAmountTable[i][_curIdx].getLongValue(self.netAmountTable[i][_curIdx].getDoubleValue(balanceOrAverage) / NAB.savedDisplayAverageTable[i])
                                            myPrint("DB", ":: Row: %s - converted calculated balance of: %s into average (/by: %s) of: %s"
                                                    %(onRow, self.netAmountTable[i][_curIdx].getDoubleValue(self.netAmountTable[i][_valIdx]), NAB.savedDisplayAverageTable[i], self.netAmountTable[i][_curIdx].getDoubleValue(balanceOrAverage)))

                                        netAmtDbl_toCompare = self.netAmountTable[i][_curIdx].getDoubleValue(balanceOrAverage)

                                        if NAB.savedHideRowWhenXXXTable[i] == GlobalVars.HIDE_ROW_WHEN_ZERO_OR_X:

                                            if NAB.savedHideDecimals:
                                                if float(int(netAmtDbl_toCompare)) == netAmtDbl_toCompare:
                                                    myPrint("DB", ":: Row: %s Decimals hidden... NOTE: calculated balance (%s) is already a whole number so no rounding... NOTE: XValue (%s)"
                                                            %(onRow, netAmtDbl_toCompare, NAB.savedHideRowXValueTable[i]))
                                                elif float(int(NAB.savedHideRowXValueTable[i])) != NAB.savedHideRowXValueTable[i]:
                                                    myPrint("DB", ":: Row: %s Decimals hidden... BUT will NOT round calculated balance (%s) as XValue (%s) demands decimal precision"
                                                            %(onRow, netAmtDbl_toCompare, NAB.savedHideRowXValueTable[i]))
                                                else:
                                                    netAmtDbl_toCompare = roundTowards(netAmtDbl_toCompare, NAB.savedHideRowXValueTable[i])

                                                    myPrint("DB", ":: Row: %s Decimals hidden... Will compare rounded(towards X) calculated balance (original: %s, rounded: %s) against XValue: %s"
                                                            %(onRow, self.netAmountTable[i][_curIdx].getDoubleValue(balanceOrAverage), netAmtDbl_toCompare, NAB.savedHideRowXValueTable[i]))

                                            if netAmtDbl_toCompare == NAB.savedHideRowXValueTable[i]:
                                                myPrint("DB", "** Hiding/skipping (x=)%s balance row %s" %(NAB.savedHideRowXValueTable[i], onRow))
                                                skippingRow = True

                                        if NAB.savedHideRowWhenXXXTable[i] == GlobalVars.HIDE_ROW_WHEN_NEGATIVE_OR_X:
                                            if netAmtDbl_toCompare <= NAB.savedHideRowXValueTable[i]:
                                                myPrint("DB", "** Hiding/skipping <=(x)%s balance row %s" %(NAB.savedHideRowXValueTable[i], onRow))
                                                skippingRow = True

                                        if NAB.savedHideRowWhenXXXTable[i] == GlobalVars.HIDE_ROW_WHEN_POSITIVE_OR_X:
                                            if netAmtDbl_toCompare >= NAB.savedHideRowXValueTable[i]:
                                                myPrint("DB", "** Hiding/skipping >=(x)%s balance row %s" %(NAB.savedHideRowXValueTable[i], onRow))
                                                skippingRow = True

                                        if NAB.savedHideRowWhenXXXTable[i] == GlobalVars.HIDE_ROW_WHEN_NOT_ZERO_OR_X:
                                            if netAmtDbl_toCompare != NAB.savedHideRowXValueTable[i]:
                                                myPrint("DB", "** Hiding/skipping !=(x)%s balance row %s" %(NAB.savedHideRowXValueTable[i], onRow))
                                                skippingRow = True

                                        if skippingRow:
                                            if NAB.savedRowSeparatorTable[i] > GlobalVars.ROW_SEPARATOR_NEVER: self.addRowSeparator(_view)
                                            hiddenRows = True
                                            continue

                                    if NAB.savedRowSeparatorTable[i] == GlobalVars.ROW_SEPARATOR_ABOVE or NAB.savedRowSeparatorTable[i] == GlobalVars.ROW_SEPARATOR_BOTH:
                                        self.addRowSeparator(_view)

                                    showCurrText = ""
                                    if self.netAmountTable[i][_curIdx] is not baseCurr:
                                        showCurrText = " (%s)" %(self.netAmountTable[i][_curIdx].getIDString())

                                    showAverageText = ""
                                    if lUseAverage: myPrint("DB", ":: Row: %s using average / by: %s" %(onRow, NAB.savedDisplayAverageTable[i]))
                                    if lUseAverage: showAverageText = " (Avg/by: %s)" %(NAB.savedDisplayAverageTable[i])

                                    rowText = wrap_HTML_small(NAB.savedWidgetName[i], self.netAmountTable[i][_secLabelTextIdx] + showCurrText + showAverageText, altFG)

                                    nameLabel = SpecialJLinkLabel(rowText, "showConfig?%s" %(str(onRow)), JLabel.LEFT)

                                    if balanceOrAverage is None:
                                        netTotalLbl = JLinkLabel(GlobalVars.DEFAULT_WIDGET_ROW_NOT_CONFIGURED.lower(), "showConfig?%s" %(str(onRow)), JLabel.RIGHT)
                                        netTotalLbl.setFont((md.getUI().getFonts()).mono)                               # noqa

                                    else:

                                        theFormattedValue = formatFancy(self.netAmountTable[i][_curIdx],
                                                                        balanceOrAverage,
                                                                        NAB.decimal,
                                                                        fancy=(not NAB.savedDisableCurrencyFormatting[i]),
                                                                        indianFormat=NAB.savedUseIndianNumberFormat,
                                                                        includeDecimals=(not NAB.savedHideDecimals),
                                                                        roundingTarget=(0.0 if (not NAB.savedHideDecimals) else NAB.savedHideRowXValueTable[i]))

                                        netTotalLbl = SpecialJLinkLabel(theFormattedValue, "showConfig?%s" %(onRow), JLabel.RIGHT)
                                        netTotalLbl.setFont((md.getUI().getFonts()).mono)                               # noqa

                                        if balanceOrAverage < 0:
                                            netTotalLbl.setForeground(md.getUI().colors.negativeBalFG)                  # noqa
                                        else:
                                            if "default" == ThemeInfo.themeForID(md.getUI(), md.getUI().getPreferences().getSetting("gui.current_theme", ThemeInfo.DEFAULT_THEME_ID)).getThemeID():
                                                netTotalLbl.setForeground(md.getUI().colors.budgetHealthyColor)         # noqa
                                            else:
                                                netTotalLbl.setForeground(md.getUI().colors.positiveBalFG)              # noqa

                                    nameLabel.setBorder(_view.nameBorder)                                               # noqa
                                    netTotalLbl.setBorder(_view.amountBorder)                                           # noqa

                                    nameLabel.setDrawUnderline(False)
                                    netTotalLbl.setDrawUnderline(False)

                                    _view.listPanel.add(nameLabel, GridC.getc().xy(0, self.widgetOnPnlRow).wx(1.0).fillboth().pady(2))
                                    _view.listPanel.add(netTotalLbl, GridC.getc().xy(1, self.widgetOnPnlRow).fillboth().pady(2))
                                    self.widgetOnPnlRow += 1

                                    nameLabel.addLinkListener(_view)
                                    netTotalLbl.addLinkListener(_view)

                                    if NAB.savedBlinkTable[i]: thisViewsBlinkers.append(netTotalLbl)

                                    if NAB.savedRowSeparatorTable[i] == GlobalVars.ROW_SEPARATOR_BELOW or NAB.savedRowSeparatorTable[i] == GlobalVars.ROW_SEPARATOR_BOTH:
                                        self.addRowSeparator(_view)

                                blinkers.extend(thisViewsBlinkers)

                                if NAB.isPreview is None:
                                    myPrint("DB", "Checking for Preview build status...")
                                    NAB.isPreview = NAB.isPreviewBuild()

                                lAnyShowWarningsEnabled  = False
                                lAnyShowWarningsDisabled = False
                                for showWarn in NAB.savedShowWarningsTable:
                                    if showWarn: lAnyShowWarningsEnabled = True
                                    if not showWarn: lAnyShowWarningsDisabled = True

                                if NAB.warningInParametersDetected and lAnyShowWarningsEnabled:
                                    warningTypeText = NAB.getWarningType(NAB.warningInParametersDetectedType)
                                    warningText = "** '%s' IN PARAMETERS DETECTED (row: %s) **" %(warningTypeText, "multi" if not NAB.warningInParametersDetectedInRow else NAB.warningInParametersDetectedInRow)

                                    if not NAB.warningInParametersDetectedInRow:
                                        nameLabel = JLinkLabel(warningText, "showConfig", JLabel.LEFT)
                                    else:
                                        nameLabel = JLinkLabel(warningText, "showConfig?%s" %(str(NAB.warningInParametersDetectedInRow)), JLabel.LEFT)
                                    nameLabel.setBorder(_view.nameBorder)                                               # noqa
                                    nameLabel.setDrawUnderline(False)
                                    nameLabel.setForeground(md.getUI().colors.errorMessageForeground)                   # noqa
                                    nameLabel.addLinkListener(_view)
                                    _view.listPanel.add(nameLabel, GridC.getc().xy(0, self.widgetOnPnlRow).wx(1.0).fillboth().west().pady(2))
                                    self.widgetOnPnlRow += 1

                                if NAB.isPreview or debug:
                                    self.widgetOnPnlRow += 1
                                    previewText = "" if not NAB.isPreview else "*PREVIEW(%s)* " %(version_build)
                                    debugText = "" if not debug else "*DEBUG* "
                                    migratedText = "" if not NAB.migratedParameters else "*MIGRATED PARAMS* "
                                    warningCheckText = "" if not NAB.warningInParametersDetected else "*WARNING!* "
                                    warningsTurnedOffText = "" if not lAnyShowWarningsDisabled else "*SOME WARNINGS OFF* "
                                    parallelText = "" if not NAB.parallelBalanceTableOperating else "*PARALLEL BAL CALCS* "
                                    hiddenRowsText = "" if not hiddenRows else "*HIDDEN ROW(s)* "
                                    rowText = wrap_HTML_small("", previewText+debugText+migratedText+warningCheckText+warningsTurnedOffText+parallelText+hiddenRowsText, altFG)
                                    nameLabel = MyJLabel(rowText, JLabel.LEFT)
                                    nameLabel.setBorder(_view.nameBorder)
                                    _view.listPanel.add(nameLabel, GridC.getc().xy(0, self.widgetOnPnlRow).wx(1.0).fillboth().west().pady(2))

                            else:
                                myPrint("B", "@@ ERROR BuildHomePageWidgetSwingWorker:done().get() reported FALSE >> Either crashed or MD is closing (the 'book')...")

                                _view.setVisible(False)
                                _view.listPanel.removeAll()
                                self.widgetOnPnlRow = 0

                                rowText = "%s ERROR DETECTED? (review console)" %(GlobalVars.DEFAULT_WIDGET_DISPLAY_NAME)
                                nameLabel = JLinkLabel(rowText, "showConsole", JLabel.LEFT)
                                nameLabel.setDrawUnderline(False)
                                nameLabel.setForeground(md.getUI().colors.errorMessageForeground)                       # noqa
                                nameLabel.setBorder(_view.nameBorder)                                                   # noqa
                                nameLabel.addLinkListener(_view)
                                _view.listPanel.add(nameLabel, GridC.getc().xy(0, self.widgetOnPnlRow).wx(1.0).fillboth().west().pady(2))
                                blinkers.append(nameLabel)

                        self.netAmountTable = None

                    except AttributeError as e:
                        if detectMDClosingError(e):
                            return
                        else:
                            raise

                    except InterruptedException:
                        myPrint("DB", "@@ BuildHomePageWidgetSwingWorker InterruptedException - aborting...")

                    except CancellationException:
                        myPrint("DB", "@@ BuildHomePageWidgetSwingWorker CancellationException - aborting...")

                    except:

                        myPrint("B", "@@ ERROR BuildHomePageWidgetSwingWorker ERROR Detected building the viewPanel(s)..")
                        dump_sys_error_to_md_console_and_errorlog()

                        for _viewWR in HPV.views:
                            _view = _viewWR.get()
                            if _view is None: continue

                            _view.setVisible(False)
                            _view.listPanel.removeAll()
                            self.widgetOnPnlRow = 0

                            rowText = "%s ERROR DETECTED! (review console)" %(GlobalVars.DEFAULT_WIDGET_DISPLAY_NAME)
                            nameLabel = MyJLabel(rowText, JLabel.LEFT)
                            nameLabel.setForeground(md.getUI().colors.errorMessageForeground)
                            nameLabel.setBorder(_view.nameBorder)
                            _view.listPanel.add(nameLabel, GridC.getc().xy(0, self.widgetOnPnlRow).wx(1.0).fillboth().west().pady(2))
                            blinkers.append(nameLabel)

                    finally:
                        NAB = NetAccountBalancesExtension.getNAB()
                        with NAB.swingWorkers_LOCK:
                            if self in NAB.swingWorkers:
                                NAB.swingWorkers.remove(self)
                            else:
                                myPrint("DB", "@@ ALERT: I did not find myself within swingworkers list, so doing nothing...:", self)

                    for _viewWR in HPV.views:
                        _view = _viewWR.get()
                        if _view is None: continue

                        _view.setVisible(True)  # Already on the Swing Event Dispatch Thread (EDT) so can just call directly....
                        _view.invalidate()
                        parent = _view.getParent()
                        while parent is not None:
                            parent.repaint()
                            parent.validate()
                            parent = parent.getParent()

                    if len(blinkers) > 0: BlinkSwingTimer(1200, blinkers, flipColor=(MD_REF.getUI().getColors().defaultTextForeground), flipBold=True).start()

        class ViewPanel(JPanel, JLinkListener, MouseListener):

            def linkActivated(self, link, event):                                                                       # noqa
                myPrint("DB", "In ViewPanel.linkActivated()")
                myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
                myPrint("DB", "... link: %s" %(link))

                NAB = NetAccountBalancesExtension.getNAB()
                HPV = MyHomePageView.getHPV()

                if isinstance(link, basestring):
                    if (link.lower().startswith("showConfig".lower())):
                        myPrint("DB", ".. calling .showURL() to call up %s panel" %(link))
                        NAB.moneydanceContext.showURL("moneydance:fmodule:%s:%s:customevent:%s" %(HPV.myModuleID,HPV.myModuleID,link))

                    if (link.lower().startswith("saveSettings".lower())):
                        myPrint("DB", ".. calling .showURL() to trigger a save of settings ('%s')..." %(link))
                        NAB.moneydanceContext.showURL("moneydance:fmodule:%s:%s:customevent:%s" %(HPV.myModuleID,HPV.myModuleID,link))

                    if (link.lower().startswith("showConsole".lower())):
                        myPrint("DB", ".. calling .showURL() to trigger Help>Console Window ('%s')..." %(link))
                        NAB.moneydanceContext.showURL("moneydance:fmodule:%s:%s:customevent:%s" %(HPV.myModuleID,HPV.myModuleID,link))

            def mouseClicked(self, evt):
                myPrint("DB", "In mouseClicked. Event:", evt, evt.getSource())
                if evt.getSource() is self.collapsableIconLbl:
                    myPrint("DB", "mouseClicked: detected collapsableIconLbl... going for toggle collapse....")
                    self.toggleExpandCollapse()

            def mousePressed(self, evt): pass
            def mouseReleased(self, evt): pass
            def mouseExited(self, evt): pass
            def mouseEntered(self, evt): pass

            def toggleExpandCollapse(self):
                NAB = NetAccountBalancesExtension.getNAB()
                if not NAB.configSaved:
                    myPrint("B", "Alert - Blocking expand/collapse widget as (changed) parameters not yet saved...!")
                elif NAB.configPanelOpen:
                    myPrint("B", "Alert - Blocking expand/collapse widget as widget config gui is open...!")
                else:
                    NAB.savedExpandedView = not NAB.savedExpandedView

                    SwingUtilities.invokeLater(NAB.SaveSettingsRunnable())
                    MyHomePageView.getHPV().refresher.enqueueRefresh()

            def __init__(self):

                super(self.__class__, self).__init__()

                myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
                myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

                NAB = NetAccountBalancesExtension.getNAB()

                self.nameBorder = EmptyBorder(3, 14, 3, 0)
                self.amountBorder = EmptyBorder(3, 0, 3, 14)

                gridbag = GridBagLayout()
                self.setLayout(gridbag)

                self.setOpaque(False)
                self.setBorder(MoneydanceLAF.homePageBorder)

                self.headerPanel = JPanel(GridBagLayout())
                self.headerPanel.setOpaque(False)

                self.headerLabel = JLinkLabel(" ", "showConfig", JLabel.LEFT)
                self.headerLabel.setDrawUnderline(False)
                self.headerLabel.setFont(NAB.moneydanceContext.getUI().getFonts().header)                               # noqa
                # self.headerLabel.setBorder(self.nameBorder)                                                           # noqa

                self.balTypeLabel = JLinkLabel("", "showConfig", JLabel.RIGHT)
                self.balTypeLabel.setFont(NAB.moneydanceContext.getUI().getFonts().defaultText)                         # noqa
                self.balTypeLabel.setBorder(self.amountBorder)                                                          # noqa
                self.balTypeLabel.setDrawUnderline(False)

                self.headerLabel.addLinkListener(self)
                self.balTypeLabel.addLinkListener(self)

                self.titlePnl = JPanel(GridBagLayout())
                self.titlePnl.setOpaque(False)

                self.collapsableIconLbl = JLabel(" ")
                self.collapsableIconLbl.setFont(NAB.moneydanceContext.getUI().getFonts().header)
                self.collapsableIconLbl.setBorder(self.nameBorder)

                self.titlePnl.add(self.collapsableIconLbl, GridC.getc().xy(0, 0).wx(0.1).east())
                self.titlePnl.add(self.headerLabel, GridC.getc().xy(1, 0).wx(9.0).fillx().west())

                # self.headerPanel.add(self.headerLabel, GridC.getc().xy(0, 0).wx(1.0).fillx().west())
                self.headerPanel.add(self.titlePnl, GridC.getc().xy(0, 0).wx(1.0).fillx().east())
                self.headerPanel.add(self.balTypeLabel, GridC.getc().xy(1, 0))

                if NAB.savedDisableWidgetTitle:
                    myPrint("DB", "Skipping adding the Widget's title to the ViewPanel")
                else:
                    self.add(self.headerPanel, GridC.getc().xy(0, 0).wx(1.0).fillx())

                self.listPanel = JPanel(gridbag)        # Don't need to use MyJPanel as LaF / Theme change calls a refresh/rebuild of this anyway
                self.add(self.listPanel, GridC.getc(0, 1).wx(1.0).fillboth())
                self.add(Box.createVerticalStrut(2), GridC.getc(0, 2).wy(1.0))
                self.listPanel.setOpaque(False)

                self.collapsableIconLbl.addMouseListener(self)

            def updateUI(self):
                myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
                super(self.__class__, self).updateUI()

        # Sets the view as active or inactive. When not active, a view should not have any registered listeners
        # with other parts of the program. This will be called when an view is added to the home page,
        # or the home page is refreshed after not being visible for a while.


        def setActive(self, active):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
            myPrint("DB", "HomePageView: .setActive(%s)" %(active))

            if self.is_unloaded:
                myPrint("DB", "HomePageView is unloaded, so ignoring....")
                return

            if not active:
                myPrint("DB", "... setActive() (as of build 1020) doing nothing...")
            else:
                self.refresh()

        # Forces a refresh of the information in the view. For example, this is called after the preferences are updated.
        def refresh(self, lFromAccountListener=False):                                                                  # noqa
            myPrint("DB", "In MyHomePageView: %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

            if self.is_unloaded:
                myPrint("DB", "HomePageView is unloaded, so ignoring....")
                return

            HPV = self

            myPrint("DB", ".. lastRefreshTriggerWasAccountModified: %s" %(HPV.lastRefreshTriggerWasAccountModified))
            HPV.lastRefreshTriggerWasAccountModified = lFromAccountListener

            if NetAccountBalancesExtension.getNAB().moneydanceContext.getUI().getSuspendRefreshes():
                myPrint("DB", "... .getUI().getSuspendRefreshes() is True so ignoring...")
                return

            if self.refresher is not None:
                myPrint("DB", "... calling refresher.enqueueRefresh()")
                self.refresher.enqueueRefresh()
            else:
                myPrint("DB", "... refresher is None - just returning without refresh...")



        def reallyRefresh(self):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
            myPrint("DB", "HomePageView .reallyRefresh().. rebuilding the panel(s) and contents...")

            NAB = NetAccountBalancesExtension.getNAB()
            md = NAB.moneydanceContext

            NAB.cancelSwingWorkers(lBuildHomePageWidgets=True)

            # launch -invoke[_and_quit] can cause program to fall over as it's shutting down.. Detect None condition
            if md.getCurrentAccountBook() is None:
                myPrint("DB", "@@ .reallyRefresh() detected .getCurrentAccountBook() is None... Perhaps -invoke[_and_quit].. Just ignore and exit this refresh..")
                return

            lShouldStartSwingWorker = False

            with self.HPV_LOCK:

                self.cleanupDeadViews(False)

                for _viewWR in self.views:
                    _view = _viewWR.get()
                    if isSwingComponentInvalid(_view):
                        myPrint("DB", "... skipping View(WIDGET) as no longer exists (or is invalid):", _viewWR)
                        continue

                    if debug:
                        mfRef = SwingUtilities.getWindowAncestor(_view)
                        mfName = "None" if (mfRef is None) else classPrinter(mfRef.getName(), mfRef)
                        myPrint("B", "... view: %s, main frame: %s (valid: %s)"
                                %(classPrinter(_view.getName(), _view), mfName, isSwingComponentValid(_view)))
                        del mfRef, mfName

                    _view.headerLabel.setText(GlobalVars.DEFAULT_WIDGET_DISPLAY_NAME.title())                           # noqa
                    _view.headerLabel.setForeground(md.getUI().colors.secondaryTextFG)                                  # noqa

                    if not NAB.savedExpandedView and NAB.configSaved:
                        myPrint("DB", "Widget is collapsed, so doing nothing....")
                        _view.collapsableIconLbl.setIcon(md.getUI().getImages().getIconWithColor(GlobalVars.Strings.MD_GLYPH_TRIANGLE_RIGHT, _view.collapsableIconLbl.getForeground()))
                        _view.listPanel.removeAll()
                        _view.listPanel.getParent().revalidate()
                        _view.listPanel.getParent().repaint()

                    else:

                        NAB.savedExpandedView = True        # Override as expanded in case it was collapsed but not saved....

                        if not NAB.configSaved:
                            _view.collapsableIconLbl.setIcon(md.getUI().getImages().getIconWithColor(GlobalVars.Strings.MD_GLYPH_REMINDERS, _view.collapsableIconLbl.getForeground()))
                        else:
                            _view.collapsableIconLbl.setIcon(md.getUI().getImages().getIconWithColor(GlobalVars.Strings.MD_GLYPH_TRIANGLE_DOWN, _view.collapsableIconLbl.getForeground()))
                            _view.collapsableIconLbl.setIcon(md.getUI().getImages().getIconWithColor(GlobalVars.Strings.MD_GLYPH_TRIANGLE_DOWN, _view.collapsableIconLbl.getForeground()))

                        _view.balTypeLabel.setText("Calculated Total")                                                  # noqa
                        _view.balTypeLabel.setForeground(md.getUI().colors.secondaryTextFG)                             # noqa

                        # if isParallelBalanceTableOperational():
                        if debug:
                            _view.listPanel.removeAll()
                            onPnlRow = 0

                            mdImages = NAB.moneydanceContext.getUI().getImages()
                            iconTintPleaseWait = NAB.moneydanceContext.getUI().colors.errorMessageForeground
                            iconPleaseWait = mdImages.getIconWithColor(GlobalVars.Strings.MD_GLYPH_REFRESH, iconTintPleaseWait)

                            pleaseWaitLabel = JLabel("Please wait - widget is updating...")
                            pleaseWaitLabel.setIcon(iconPleaseWait)
                            pleaseWaitLabel.setHorizontalAlignment(JLabel.CENTER)
                            pleaseWaitLabel.setHorizontalTextPosition(JLabel.LEFT)
                            pleaseWaitLabel.setForeground(md.getUI().colors.errorMessageForeground)
                            pleaseWaitLabel.setBorder(_view.nameBorder)

                            onCol = 0
                            _view.listPanel.add(pleaseWaitLabel, GridC.getc().xy(onCol, onPnlRow).wx(1.0).filly().colspan(2).pady(2))
                            _view.listPanel.getParent().revalidate()
                            _view.listPanel.getParent().repaint()

                        else:
                            pleaseWaitLabel = JLabel("")

                        lShouldStartSwingWorker = True

            if lShouldStartSwingWorker:
                myPrint("DB", "About to start swing worker to offload processing to non EDT thread....")
                sw = self.BuildHomePageWidgetSwingWorker(pleaseWaitLabel, self)
                sw.execute()


        # Called when the view should clean up everything. For example, this is called when a file is closed and the GUI
        #  is reset. The view should disconnect from any resources that are associated with the currently opened data file.
        def reset(self):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

            myPrint("DB", ".... .reset() (as of build 1020) doing nothing")


        def unload(self):   # This is my own method (not overridden from HomePageView)
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))
            myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))
            myPrint("B", "HomePageView: .unload() extension called - so I will wipe all panels and deactivate myself....")

            self.cleanupAsBookClosing()

            with self.HPV_LOCK: self.is_unloaded = True

        def cleanupAsBookClosing(self):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))

            with self.HPV_LOCK:
                for _viewWR in self.views:
                    _view = _viewWR.get()
                    if _view is None:
                        myPrint("DB", "... skipping wiping of view as it no longer exists:", _viewWR)
                    else:
                        myPrint("DB", "... wiping view:", classPrinter(_view.getName(), _view))
                        _view.removeAll()       # Hopefully already within the EDT....
                del self.views[:]
                self.reset()
                self.deactivateListeners()


    # Don't worry about the Swing EDT for initialisation... The GUI won't be loaded on MD startup anyway....
    myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

    # Moneydance queries this variable after script exit and uses it to install the extension
    moneydance_extension = NetAccountBalancesExtension.getNAB()

    myPrint("B", "StuWareSoftSystems - ", GlobalVars.thisScriptName, " initialisation routines ending......")

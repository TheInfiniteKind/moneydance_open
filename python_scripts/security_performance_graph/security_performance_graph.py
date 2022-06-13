#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# security_performance_graph.py build: 1001 - May 2022 - Stuart Beesley StuWareSoftSystems

# requires: MD 2021.1(3069) due to NPE on SwingUtilities - something to do with 'theGenerator.setInfo(reportSpec)'

###############################################################################
# MIT License
#
# Copyright (c) 2021-2022 Stuart Beesley - StuWareSoftSystems
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
# Use in Moneydance Menu Window->Show Moneybot Console >> Open Script >> RUN

# build: 1000 - Initial Release: Recreates the internal MD graph engine and create a special security performance report by percentage
# build: 1001 - Tweaks; Common code; Fixed JTable sorting....

# todo - Memorise (save versions) along with choose/delete etc saved versions
# todo - add markers for splits, buy/sells

# CUSTOMIZE AND COPY THIS ##############################################################################################
# CUSTOMIZE AND COPY THIS ##############################################################################################
# CUSTOMIZE AND COPY THIS ##############################################################################################

# SET THESE LINES
myModuleID = u"security_performance_graph"
version_build = "1001"
MIN_BUILD_REQD = 3069
_I_CAN_RUN_AS_MONEYBOT_SCRIPT = True

if u"debug" in globals():
    global debug
else:
    debug = False

global security_performance_graph_frame_
# SET LINES ABOVE ^^^^

# COPY >> START
global moneydance, moneydance_ui, moneydance_extension_loader, moneydance_extension_parameter
MD_REF = moneydance             # Make my own copy of reference as MD removes it once main thread ends.. Don't use/hold on to _data variable
MD_REF_UI = moneydance_ui       # Necessary as calls to .getUI() will try to load UI if None - we don't want this....
if MD_REF is None: raise Exception("CRITICAL ERROR - moneydance object/variable is None?")
if u"moneydance_extension_loader" in globals():
    MD_EXTENSION_LOADER = moneydance_extension_loader
else:
    MD_EXTENSION_LOADER = None

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
            and (isinstance(security_performance_graph_frame_, MyJFrame)                 # EDIT THIS
                 or type(security_performance_graph_frame_).__name__ == u"MyCOAWindow")  # EDIT THIS
            and security_performance_graph_frame_.isActiveInMoneydance):                 # EDIT THIS
        frameToResurrect = security_performance_graph_frame_                             # EDIT THIS
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

elif not _I_CAN_RUN_AS_MONEYBOT_SCRIPT and u"moneydance_extension_loader" not in globals():
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

    from java.lang import Thread, IllegalArgumentException, String

    from com.moneydance.util import Platform
    from com.moneydance.awt import JTextPanel, GridC, JDateField
    from com.moneydance.apps.md.view.gui import MDImages

    from com.infinitekind.util import DateUtil, CustomDateFormat
    from com.infinitekind.moneydance.model import *
    from com.infinitekind.moneydance.model import AccountUtil, AcctFilter, CurrencyType, CurrencyUtil
    from com.infinitekind.moneydance.model import Account, Reminder, ParentTxn, SplitTxn, TxnSearch, InvestUtil, TxnUtil

    from com.moneydance.apps.md.controller import AccountBookWrapper
    from com.moneydance.apps.md.view.gui import WelcomeWindow
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
    from java.lang import Double, Math, Character, NoSuchFieldException, NoSuchMethodException, Boolean
    from java.lang.reflect import Modifier
    from java.io import FileNotFoundException, FilenameFilter, File, FileInputStream, FileOutputStream, IOException, StringReader
    from java.io import BufferedReader, InputStreamReader
    from java.nio.charset import Charset
    if isinstance(None, (JDateField,CurrencyUtil,Reminder,ParentTxn,SplitTxn,TxnSearch, JComboBox, JCheckBox,
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
            groupingCharSep = ","
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
    from java.lang import Integer, Boolean, Long                                                                        # noqa
    from java.util import Collections, Comparator, TreeSet                                                              # noqa
    from javax.swing import BorderFactory, RowSorter
    from java.awt import Event
    from java.awt.event import ActionEvent, ActionListener, ItemListener
    from java.awt import Frame, Window                                                                                  # noqa

    from javax.swing import SortOrder
    from javax.swing.border import CompoundBorder, MatteBorder                                                          # noqa
    from javax.swing.table import DefaultTableCellRenderer, DefaultTableModel, TableRowSorter, TableCellRenderer
    from javax.swing.event import TableColumnModelListener

    from com.moneydance.apps.md.view.gui import MDAction
    from java.beans import PropertyChangeListener, PropertyChangeEvent                                                  # noqa

    from com.infinitekind.moneydance.model import CurrencyTable

    from com.moneydance.apps.md.view.gui.select import ClickLabelListPanel

    from com.moneydance.apps.md.controller import Main
    from com.infinitekind.util import StringUtils
    from com.infinitekind.tiksync import SyncRecord
    from com.infinitekind.moneydance.model import ReportSpec, CurrencySnapshot, ReportSpec, AccountBook
    from com.moneydance.apps.md.view.gui import GraphReportGenerator, IntervalChooser, DateRangeChooser
    from com.moneydance.apps.md.view.gui import SecondaryDialog, OKButtonPanel, OKButtonListener
    from com.moneydance.apps.md.view.resources import MDResourceProvider
    from com.moneydance.apps.md.view.gui.graphtool import GraphSet, GraphGenerator, GraphViewer                         # noqa
    from com.moneydance.apps.md.view.gui import MoneydanceGUI
    from com.moneydance.apps.md.controller import PreferencesListener, AppEventListener
    from com.moneydance.apps.md.controller.time import TimeInterval, TimeIntervalUtil
    from com.moneydance.awt.graph import GraphDataSet
    from com.moneydance.util import UiUtil
    from com.moneydance.awt import AwtUtil
    from com.moneydance.apps.md.view.gui.reporttool import GraphReportUtil
    from com.moneydance.apps.md.controller.time import DateRangeOption

    exec("from com.moneydance.apps.md.view.gui.print import MDPrintable, MDPrinter")
    global MDPrintable, MDPrinter

    from java.awt.datatransfer import DataFlavor, UnsupportedFlavorException, Transferable, ClipboardOwner, Clipboard   # noqa

    from org.jfree.data.time import TimeSeries
    from java.util import HashMap, Arrays                                                                               # noqa
    from java.awt import LayoutManager, GradientPaint, Graphics, Graphics2D, RenderingHints, BasicStroke, Rectangle
    from java.awt.image import BufferedImage
    from java.awt.geom import Ellipse2D
    from java.io import OutputStream
    from java.text import NumberFormat, FieldPosition
    from java.lang import Comparable, StringBuilder, StringBuffer
    from com.moneydance.awt.graph import ColorEnumerator
    from org.jfree.data.general import AbstractSeriesDataset
    from org.jfree.chart import ChartPanel, JFreeChart
    from org.jfree.chart.axis import DateAxis, NumberAxis
    from org.jfree.chart.labels import StandardXYToolTipGenerator
    from org.jfree.chart.plot import XYPlot
    from org.jfree.chart.renderer.xy import XYLineAndShapeRenderer
    from org.jfree.data.time import TimeSeries, TimeSeriesCollection, RegularTimePeriod, TimeTableXYDataset
    from org.jfree.data.xy import XYDataset
    from org.jfree.chart import ChartUtilities
    from org.jfree.chart.block import BlockBorder
    from org.jfree.ui import RectangleInsets
    from org.jfree.chart.title import LegendTitle, TextTitle, Title                                                     # noqa
    from org.jfree.chart import ChartFactory
    from org.jfree.chart.renderer.xy import AbstractXYItemRenderer
    from org.jfree.chart.axis import TickUnits, DateTickUnitType
    from org.jfree.data.time import TimeSeriesDataItem
    from org.jfree.data import Range

    # renamed in MD build 3067
    if int(MD_REF.getBuild()) >= 3067:
        from com.moneydance.apps.md.view.gui.theme import ThemeInfo                                                     # noqa
    else:
        from com.moneydance.apps.md.view.gui.theme import Theme as ThemeInfo                                            # noqa

    # >>> END THIS SCRIPT'S IMPORTS ########################################################################################

    # >>> THIS SCRIPT'S GLOBALS ############################################################################################
    GlobalVars.__security_performance_graph = None
    GlobalVars.extn_param_graph_params_SPG = None
    GlobalVars.extn_param_column_widths_SPG = []
    GlobalVars.Strings.GRAPH_NAME = u"Security Performance Graph"
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

    def getDecimalPoint(lGetPoint=False, lGetGrouping=False):
        decimalFormat = DecimalFormat.getInstance()
        # noinspection PyUnresolvedReferences
        decimalSymbols = decimalFormat.getDecimalFormatSymbols()

        if not lGetGrouping: lGetPoint = True
        if lGetGrouping and lGetPoint: return u"error"

        try:
            if lGetPoint:
                _decimalCharSep = decimalSymbols.getDecimalSeparator()
                myPrint(u"D",u"Decimal Point Character: %s" %(_decimalCharSep))
                return _decimalCharSep

            if lGetGrouping:
                _groupingCharSep = decimalSymbols.getGroupingSeparator()
                if _groupingCharSep is None or _groupingCharSep == u"":
                    myPrint(u"B", u"Caught empty Grouping Separator")
                    return u""
                if ord(_groupingCharSep) >= 128:    # Probably a nbsp (160) = e.g. South Africa for example..!
                    myPrint(u"B", u"Caught special character in Grouping Separator. Ord(%s)" %(ord(_groupingCharSep)))
                    if ord(_groupingCharSep) == 160:
                        return u" (non breaking space character)"
                    return u" (non printable character)"
                myPrint(u"D",u"Grouping Separator Character:", _groupingCharSep)
                return _groupingCharSep
        except:
            myPrint(u"B",u"Error in getDecimalPoint() routine....?")
            dump_sys_error_to_md_console_and_errorlog()

        return u"error"


    GlobalVars.decimalCharSep = getDecimalPoint(lGetPoint=True)
    GlobalVars.groupingCharSep = getDecimalPoint(lGetGrouping=True)

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

    def doesUserAcceptDisclaimer(theParent, theTitle, disclaimerQuestion):
        disclaimer = myPopupAskForInput(theParent,
                                        theTitle,
                                        "DISCLAIMER:",
                                        "%s Type 'IAGREE' to continue.." %(disclaimerQuestion),
                                        "NO",
                                        False,
                                        JOptionPane.ERROR_MESSAGE)
        agreed = (disclaimer == "IAGREE")
        if agreed:
            myPrint("B", "%s: User AGREED to disclaimer question: '%s'" %(theTitle, disclaimerQuestion))
        else:
            myPrint("B", "%s: User DECLINED disclaimer question: '%s' - no action/changes made" %(theTitle, disclaimerQuestion))
        return agreed

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
            myPrint("B", "User requested to create a backup before update/fix - calling moneydance 'Export Backup' routine...")
            MD_REF.getUI().setStatus("%s is creating a backup...." %(GlobalVars.thisScriptName),-1.0)
            MD_REF.getUI().saveToBackup(None)
            MD_REF.getUI().setStatus("%s create (export) backup process completed...." %(GlobalVars.thisScriptName),0)
            return True

        elif response == 1:
            myPrint("B", "User DECLINED to create a backup before update/fix...!")
            if not lReturnTheTruth:
                return True

        return False

    def confirm_backup_confirm_disclaimer(theFrame, theTitleToDisplay, theAction):

        if not myPopupAskQuestion(theFrame,
                                  theTitle=theTitleToDisplay,
                                  theQuestion=theAction,
                                  theOptionType=JOptionPane.YES_NO_OPTION,
                                  theMessageType=JOptionPane.ERROR_MESSAGE):

            txt = "'%s' User did not say yes to '%s' - no changes made" %(theTitleToDisplay, theAction)
            setDisplayStatus(txt, "R")
            myPrint("B", txt)
            myPopupInformationBox(theFrame,"User did not agree to proceed - no changes made...","NO UPDATE",JOptionPane.ERROR_MESSAGE)
            return False

        if not myPopupAskBackup(theFrame, "Would you like to perform a backup before %s" %(theTitleToDisplay)):
            txt = "'%s' - User chose to exit without the fix/update...."%(theTitleToDisplay)
            setDisplayStatus(txt, "R")
            myPrint("B","'%s' User aborted at the backup prompt to '%s' - no changes made" %(theTitleToDisplay, theAction))
            myPopupInformationBox(theFrame,"User aborted at the backup prompt - no changes made...","DISCLAIMER",JOptionPane.ERROR_MESSAGE)
            return False

        if not doesUserAcceptDisclaimer(theFrame, theTitleToDisplay, theAction):
            setDisplayStatus("'%s' - User declined the disclaimer - no changes made...." %(theTitleToDisplay), "R")
            myPrint("B","'%s' User did not say accept Disclaimer to '%s' - no changes made" %(theTitleToDisplay, theAction))
            myPopupInformationBox(theFrame,"User did not accept Disclaimer - no changes made...","DISCLAIMER",JOptionPane.ERROR_MESSAGE)
            return False

        myPrint("B","'%s' - User has been offered opportunity to create a backup and they accepted the DISCLAIMER on Action: %s - PROCEEDING" %(theTitleToDisplay, theAction))
        return True

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
            myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()")
            myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

            class MyPopUpDialogBoxRunnable(Runnable):
                def __init__(self, callingClass):
                    self.callingClass = callingClass

                def run(self):                                                                                                      # noqa

                    myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()")
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

                    if self.callingClass.lModal:
                        # noinspection PyUnresolvedReferences
                        self.callingClass._popup_d = JDialog(self.callingClass.theParent, self.callingClass.theTitle, Dialog.ModalityType.APPLICATION_MODAL)
                    else:
                        # noinspection PyUnresolvedReferences
                        self.callingClass._popup_d = JDialog(self.callingClass.theParent, self.callingClass.theTitle, Dialog.ModalityType.MODELESS)

                    screenSize = Toolkit.getDefaultToolkit().getScreenSize()

                    if isinstance(self.callingClass.maxSize, Dimension)\
                            and self.callingClass.maxSize.height and self.callingClass.maxSize.width:
                        frame_width = min(screenSize.width-20, self.callingClass.maxSize.width)
                        frame_height = min(screenSize.height-20, self.callingClass.maxSize.height)
                        self.callingClass._popup_d.setPreferredSize(Dimension(frame_width,frame_height))

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

                    # maxHeight = 500
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

                    if self.callingClass.lAlertLevel>=2:
                        # internalScrollPane.setBackground(Color.RED)
                        self.callingClass.messageJText.setBackground(Color.RED)
                        self.callingClass.messageJText.setForeground(Color.BLACK)
                        self.callingClass.messageJText.setOpaque(True)
                        _popupPanel.setBackground(Color.RED)
                        _popupPanel.setForeground(Color.BLACK)
                        _popupPanel.setOpaque(True)
                        buttonPanel.setBackground(Color.RED)
                        buttonPanel.setOpaque(True)

                    elif self.callingClass.lAlertLevel>=1:
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
                    self.callingClass._popup_d.setLocationRelativeTo(None)
                    self.callingClass._popup_d.setVisible(True)  # Keeping this modal....

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

        # GlobalVars.STATUS_LABEL.setText((_theStatus).ljust(800, " "))
        GlobalVars.STATUS_LABEL.setText((_theStatus))

        if _theColor is None or _theColor == "": _theColor = "X"
        _theColor = _theColor.upper()
        if _theColor == "R":    GlobalVars.STATUS_LABEL.setForeground(getColorRed())
        elif _theColor == "B":  GlobalVars.STATUS_LABEL.setForeground(getColorBlue())
        elif _theColor == "DG": GlobalVars.STATUS_LABEL.setForeground(getColorDarkGreen())
        else:                   GlobalVars.STATUS_LABEL.setForeground(MD_REF.getUI().getColors().defaultTextForeground)
        return

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

        _DIRS_FD = "apple.awt.fileDialogForDirectories"        # Changes Behaviour. When True you can select a Folder (rather than a file)
        _PKGS_FD = "com.apple.macos.use-file-dialog-packages"

        # FileDialog defaults
        # "apple.awt.fileDialogForDirectories"       default "false" >> set "true"  to allow Directories to be selected
        # "com.apple.macos.use-file-dialog-packages" default "true"  >> set "false" to allow access to Mac 'packages'

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

            if fileChooser_fileFilterText is not None and (not Platform.isOSX() or not Platform.isOSXVersionAtLeast("10.13")):
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

            if fileChooser_fileFilterText is not None and (not Platform.isOSX() or not Platform.isOSXVersionAtLeast("10.13")):
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
                if "MD_REF" in globals():
                    usePrintFontSize = eval("MD_REF.getUI().getFonts().print.getSize()")
                elif "moneydance" in globals():
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

                if self.lQuitMDAfterClose:
                    myPrint("B", "Quit MD after Close triggered... Now quitting MD")
                    ManuallyCloseAndReloadDataset.moneydanceExitOrRestart(lRestart=False)
                elif self.lRestartMDAfterClose:
                    myPrint("B", "Restart MD after Close triggered... Now restarting MD")
                    ManuallyCloseAndReloadDataset.moneydanceExitOrRestart(lRestart=True)
                else:
                    myPrint("DB", "FYI No Quit MD after Close triggered... So doing nothing")

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

                def run(self):                                                                                                      # noqa
                    screenSize = Toolkit.getDefaultToolkit().getScreenSize()
                    frame_width = min(screenSize.width-20, max(1024,int(round(MD_REF.getUI().firstMainFrame.getSize().width *.9,0))))
                    frame_height = min(screenSize.height-20, max(768, int(round(MD_REF.getUI().firstMainFrame.getSize().height *.9,0))))

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
                    theJText.setFont( getMonoFont() )

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

            displayString=scriptExit
            displayJText = JTextArea(displayString)
            displayJText.setFont( getMonoFont() )
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

    def isMDPlusEnabledBuild(): return (float(MD_REF.getBuild()) >= GlobalVars.MD_MDPLUS_BUILD)

    def isAlertControllerEnabledBuild(): return (float(MD_REF.getBuild()) >= GlobalVars.MD_ALERTCONTROLLER_BUILD)

    def shutdownMDPlusPoller():
        if isMDPlusEnabledBuild():
            myPrint("DB", "Shutting down the MD+ poller")
            plusPoller = MD_REF.getUI().getPlusController()
            if plusPoller is not None:
                invokeMethodByReflection(plusPoller, "shutdown", None)
                setFieldByReflection(MD_REF.getUI(), "plusPoller", None)
            # NOTE: MDPlus.licenseCache should be reset too, but it's a 'private static final' field....
            #       hence restart MD if changing (importing/zapping) the license object
            myPrint("DB", "... MD+ poller shutdown...")

    def shutdownMDAlertController():
        if isAlertControllerEnabledBuild():
            myPrint("DB", "Shutting down the Alert Controller")
            alertController = MD_REF.getUI().getAlertController()
            if alertController is not None:
                invokeMethodByReflection(alertController, "shutdown", None)
                setFieldByReflection(MD_REF.getUI(), "alertController", None)

    class ManuallyCloseAndReloadDataset(Runnable):

        @staticmethod
        def closeSecondaryWindows():
            myPrint("DB", "In ManuallyCloseAndReloadDataset.closeSecondaryWindows()")
            if not SwingUtilities.isEventDispatchThread(): return False
            if not ManuallyCloseAndReloadDataset.isSafeToCloseDataset(): return False
            return invokeMethodByReflection(MD_REF.getUI(), "closeSecondaryWindows", [Boolean.TYPE], [False])

        @staticmethod
        def isSafeToCloseDataset():
            # type: () -> bool
            """Checks with MD whether all the Secondary Windows report that they are in a state to close"""
            myPrint("DB", "In ManuallyCloseAndReloadDataset.isSafeToCloseDataset()")
            if not SwingUtilities.isEventDispatchThread(): return False
            return invokeMethodByReflection(MD_REF.getUI(), "isOKToCloseFile", None)

        @staticmethod
        def moneydanceExitOrRestart(lRestart=True, lAllowSaveWorkspace=True):
            # type: (bool, bool) -> bool
            """Checks with MD whether all the Secondary Windows report that they are in a state to close"""
            myPrint("DB", "In ManuallyCloseAndReloadDataset.moneydanceExitOrRestart() - lRestart: %s, lAllowSaveWorkspace: %s" %(lRestart, lAllowSaveWorkspace))

            if lRestart and not lAllowSaveWorkspace: raise Exception("Sorry: you cannot use lRestart=True and lAllowSaveWorkspace=False together...!")

            if lRestart:
                myPrint("B", "@@ RESTARTING MONEYDANCE >> RELOADING SAME DATASET @@")
                Thread(ManuallyCloseAndReloadDataset()).start()
            else:
                if lAllowSaveWorkspace:
                    myPrint("B", "@@ EXITING MONEYDANCE @@")
                    MD_REF.getUI().exit()
                else:
                    myPrint("B", "@@ SHUTTING DOWN MONEYDANCE >> NOT SAVING 'WORKSPACE' @@")
                    MD_REF.getUI().shutdownApp(False)

        @staticmethod
        def manuallyCloseDataset(theBook, lCloseWindows=True):
            # type: (AccountBook, bool) -> bool
            """Mimics .setCurrentBook(None) but avoids the Auto Backup 'issue'. Also closes open SecondaryWindows, pauses MD+ etc
            You should decide whether to run this on the EDT or on a new background thread when calling this method"""

            myPrint("DB", "In ManuallyCloseAndReloadDataset.manuallyCloseDataset(), lCloseWindows:", lCloseWindows)

            if lCloseWindows:
                if not SwingUtilities.isEventDispatchThread():
                    raise Exception("ERROR: you must run manuallyCloseDataset() on the EDT if you wish to also call closeSecondaryWindows()...!")
                if not ManuallyCloseAndReloadDataset.closeSecondaryWindows(): return False

            # Shutdown the MD+ poller... When we open a new dataset it should reset itself.....
            shutdownMDPlusPoller()

            # Shutdown the Alert Controller... When we open a new dataset it should reset itself.....
            shutdownMDAlertController()

            setFieldByReflection(MD_REF.getUI(), "olMgr", None)

            myPrint("DB", "... saving LocalStorage..")
            theBook.getLocalStorage().save()                        # Flush LocalStorage...

            myPrint("DB", "... Mimicking .setCurrentBook(None)....")

            MD_REF.fireAppEvent("md:file:closing")
            MD_REF.saveCurrentAccount()           # Flush any current txns in memory and start a new sync record..

            MD_REF.fireAppEvent("md:file:closed")

            myPrint("DB", "... calling .cleanUp() ....")
            theBook.cleanUp()

            setFieldByReflection(MD_REF, "currentBook", None)
            myPrint("B", "Closed current dataset (book: %s)" %(theBook))

            myPrint("DB", "... FINISHED Closing down the dataset")
            return True

        THIS_APPS_FRAME_REFERENCE = None

        def __init__(self, lQuitThisAppToo=True):
            self.lQuitThisAppToo = (lQuitThisAppToo and self.__class__.THIS_APPS_FRAME_REFERENCE is not None)
            self.result = None

        def getResult(self): return self.result     # Caution - only call this when you have waited for Thread to complete..... ;->

        def run(self):
            # type: () -> bool
            self.result = self.manuallyCloseAndReloadDataset()

        def manuallyCloseAndReloadDataset(self):
            # type: () -> bool
            """Manually closes current dataset, then reloads the same dataset.. Use when you want to refresh MD's internals"""

            if SwingUtilities.isEventDispatchThread(): raise Exception("ERROR - you must run manuallyCloseAndReloadDataset() from a new non-EDT thread!")

            cswResult = [None]
            class CloseSecondaryWindows(Runnable):
                def __init__(self, result): self.result = result
                def run(self): self.result[0] = ManuallyCloseAndReloadDataset.closeSecondaryWindows()

            SwingUtilities.invokeAndWait(CloseSecondaryWindows(cswResult))
            if not cswResult[0]: return False

            currentBook = MD_REF.getCurrentAccountBook()
            fCurrentFilePath = currentBook.getRootFolder()

            if not ManuallyCloseAndReloadDataset.manuallyCloseDataset(currentBook, lCloseWindows=False): return False

            newWrapper = AccountBookWrapper.wrapperForFolder(fCurrentFilePath)
            if newWrapper is None: raise Exception("ERROR: 'AccountBookWrapper.wrapperForFolder' returned None")
            myPrint("DB", "Successfully obtained 'wrapper' for dataset: %s\n" %(fCurrentFilePath.getCanonicalPath()))

            myPrint("B", "Opening dataset: %s" %(fCurrentFilePath.getCanonicalPath()))

            # .setCurrentBook() always pushes mdGUI().dataFileOpened() on the EDT (if not already on the EDT)....
            openResult = MD_REF.setCurrentBook(newWrapper)
            if not openResult or newWrapper.getBook() is None:
                txt = "Failed to open Dataset (wrong password?).... Will show the Welcome Window...."
                setDisplayStatus(txt, "R"); myPrint("B", txt)
                WelcomeWindow.showWelcomeWindow(MD_REF.getUI())

                if self.lQuitThisAppToo:
                    # Remember... the file opened event closes my extensions with app listeners, so do this if file could not be opened....
                    if self.__class__.THIS_APPS_FRAME_REFERENCE is not None:
                        if isinstance(self.__class__.THIS_APPS_FRAME_REFERENCE, JFrame):
                            # Do this after .setCurrentBook() so-as not to co-modify listeners.....
                            SwingUtilities.invokeLater(GenericWindowClosingRunnable(self.__class__.THIS_APPS_FRAME_REFERENCE))

                return False

            return True


    # END COMMON DEFINITIONS ###############################################################################################
    # END COMMON DEFINITIONS ###############################################################################################
    # END COMMON DEFINITIONS ###############################################################################################
    # COPY >> END

    # >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
    # >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
    # >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
    def load_StuWareSoftSystems_parameters_into_memory():

        if GlobalVars.parametersLoadedFromFile.get("__security_performance_graph") is not None: GlobalVars.__security_performance_graph = GlobalVars.parametersLoadedFromFile.get("__security_performance_graph")
        if GlobalVars.parametersLoadedFromFile.get("extn_param_graph_params_SPG") is not None: GlobalVars.extn_param_graph_params_SPG = GlobalVars.parametersLoadedFromFile.get("extn_param_graph_params_SPG")
        if GlobalVars.parametersLoadedFromFile.get("extn_param_column_widths_SPG") is not None: GlobalVars.extn_param_column_widths_SPG = GlobalVars.parametersLoadedFromFile.get("extn_param_column_widths_SPG")

        return

    # >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
    def dump_StuWareSoftSystems_parameters_from_memory():
        myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()" )

        # NOTE: Parameters were loaded earlier on... Preserve existing, and update any used ones...
        # (i.e. other StuWareSoftSystems programs might be sharing the same file)

        if GlobalVars.parametersLoadedFromFile is None: GlobalVars.parametersLoadedFromFile = {}

        # >>> THESE ARE THIS SCRIPT's PARAMETERS TO SAVE
        GlobalVars.parametersLoadedFromFile["__security_performance_graph"] = version_build
        GlobalVars.parametersLoadedFromFile["extn_param_graph_params_SPG"] = GlobalVars.extn_param_graph_params_SPG
        GlobalVars.parametersLoadedFromFile["extn_param_column_widths_SPG"] = GlobalVars.extn_param_column_widths_SPG

        myPrint("DB","variables dumped from memory back into parametersLoadedFromFile{}.....:", GlobalVars.parametersLoadedFromFile)
        return

    # Just grab debug etc... Nothing extra
    get_StuWareSoftSystems_parameters_from_file(myFile="%s_extension.dict" %(myModuleID))

    # clear up any old left-overs....
    destroyOldFrames(myModuleID)

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
            MD_REF.getUI().setStatus(">> StuWareSoftSystems - thanks for using >> %s......." %(GlobalVars.thisScriptName),0)
        except:
            pass  # If this fails, then MD is probably shutting down.......

        if not GlobalVars.i_am_an_extension_so_run_headless: print(scriptExit)

        cleanup_references()

    # .moneydance_invoke_called() is used via the _invoke.py script as defined in script_info.dict. Not used for runtime extensions
    def moneydance_invoke_called(theCommand):
        # ... modify as required to handle .showURL() events sent to this extension/script...
        myPrint("B","INVOKE - Received extension command: '%s'" %(theCommand))

    GlobalVars.defaultPrintLandscape = False
    # END ALL CODE COPY HERE ###############################################################################################
    # END ALL CODE COPY HERE ###############################################################################################
    # END ALL CODE COPY HERE ###############################################################################################

    def getPosNegColor(value):
        if value < 0.0:
            color = MD_REF.getUI().colors.negativeBalFG
        else:
            if "default" == ThemeInfo.themeForID(MD_REF.getUI(), MD_REF.getUI().getPreferences().getSetting("gui.current_theme", ThemeInfo.DEFAULT_THEME_ID)).getThemeID():
                color = MD_REF.getUI().colors.budgetHealthyColor
            else:
                color = MD_REF.getUI().colors.positiveBalFG
        return color

    def html_strip_chars(_textToStrip):
        _textToStrip = _textToStrip.replace("  ","&nbsp;&nbsp;")
        _textToStrip = _textToStrip.replace("<","&lt;")
        _textToStrip = _textToStrip.replace(">","&gt;")
        return _textToStrip

    def wrap_HTML_italics(_textToWrap):
        return "<html><i>%s</i></html>" %(html_strip_chars(_textToWrap))

    def wrap_HTML_small(_bigText, _smallText, _smallColor=None):
        if _smallColor is None: _smallColor = GlobalVars.CONTEXT.getUI().colors.tertiaryTextFG
        _smallColorHex = AwtUtil.hexStringForColor(_smallColor)
        _htmlBigText = html_strip_chars(_bigText)
        _htmlSmallText = html_strip_chars(_smallText)
        return "<html>%s<small><font color=#%s>%s</font></small></html>" %(_htmlBigText, _smallColorHex, _htmlSmallText)

    def wrap_HTML_text_then_Percent(_text, _pct):
        _colorHex = AwtUtil.hexStringForColor(getPosNegColor(_pct))
        _text = html_strip_chars(_text)
        strPct = "{:.2%}".format(_pct)
        return "<html>%s<font color=#%s>%s</font></html>" %(_text, _colorHex, strPct)


    # class MyJList(JList):
    #
    #     KEY = "selected_securities"
    #
    #     def __init__(self, moneydanceContext, ctable, includeHiddenSecuritiesChoice, *args):
    #         # type: (Main, CurrencyTable, JCheckBox, any) -> None
    #         self.moneydanceContext = moneydanceContext
    #         self.ctable = ctable
    #         self.includeHiddenSecuritiesChoice = includeHiddenSecuritiesChoice
    #         super(self.__class__, self).__init__(*args)                                                                 # noqa
    #         self.saveSelectedSecList = None
    #
    #     def loadDataModel(self):
    #         # type: () -> None
    #         securityList = []
    #         for curSec in sorted(self.ctable.getAllCurrencies(), key=lambda x: safeStr(x.getName()).upper()):
    #             # noinspection PyUnresolvedReferences
    #             if curSec.getCurrencyType() != CurrencyType.Type.SECURITY: continue
    #             if curSec.getHideInUI() and not self.includeHiddenSecuritiesChoice.isSelected(): continue
    #             securityList.append(StoreCurrencyType(curSec))
    #         self.setListData(securityList)
    #
    #     def selectSecurities(self):
    #
    #         if len(self.saveSelectedSecList) < 1: return False
    #
    #         listModel = self.getModel()
    #         if listModel.getSize() < 1: return False
    #
    #         securitiesToSelect = []
    #         for key in self.saveSelectedSecList:
    #             foundSecurity = self.moneydanceContext.getCurrentAccountBook().getCurrencyByUUID(self.saveSelectedSecList[key])
    #             if foundSecurity is not None: securitiesToSelect.append(foundSecurity)
    #
    #         indicesToSelect = []
    #
    #         for i in range(0, listModel.getSize()):
    #             modelSec = listModel.getElementAt(i)    # type: StoreCurrencyType
    #             if modelSec.getCurrencyType() in securitiesToSelect:
    #                 indicesToSelect.append(i)
    #         if len(indicesToSelect) < 1: return False
    #         self.setSelectedIndices(indicesToSelect)
    #         return True
    #
    #     def loadFromParameters(self, parameters, loadKey=None):
    #         # type: (SyncRecord, str) -> bool
    #
    #         if loadKey is None: loadKey = self.__class__.KEY
    #
    #         self.loadDataModel()
    #
    #         self.saveSelectedSecList = parameters.getSubset(loadKey)
    #
    #         return self.selectSecurities()
    #
    #     def storeToParameters(self, parameters, saveKey=None):
    #         # type: (SyncRecord, str) -> None
    #
    #         if saveKey is None: saveKey = self.__class__.KEY
    #
    #         selectedSecurities = self.getSelectedValues()
    #         if len(selectedSecurities) < 1:
    #             parameters.removeSubset(saveKey)
    #         else:
    #             securityUUIDsToSave = []
    #             for sec in selectedSecurities:
    #                 securityUUIDsToSave.append(sec.getUUID())
    #             parameters.put(saveKey, securityUUIDsToSave)
    #
    # class MyJListRenderer(DefaultListCellRenderer):
    #
    #     def __init__(self):
    #         super(self.__class__, self).__init__()                                                                     # noqa
    #
    #     def getListCellRendererComponent(self, thelist, value, index, isSelected, cellHasFocus):
    #         lightLightGray = Color(0xDCDCDC)
    #         c = super(self.__class__, self).getListCellRendererComponent(thelist, value, index, isSelected, cellHasFocus) # noqa
    #         # c.setBackground(self.getBackground() if index % 2 == 0 else lightLightGray)
    #
    #         # Create a line separator between accounts
    #         c.setBorder(BorderFactory.createMatteBorder(0, 0, 1, 0, lightLightGray))
    #         return c
    #
    # class MyDefaultListSelectionModel(DefaultListSelectionModel):
    #     # Change the selector - so not to deselect items when selecting others...
    #     def __init__(self):
    #         super(self.__class__, self).__init__()                                                                      # noqa
    #
    #     def setSelectionInterval(self, start, end):
    #         if (start != end):
    #             super(self.__class__, self).setSelectionInterval(start, end)                                            # noqa
    #         elif self.isSelectedIndex(start):
    #             self.removeSelectionInterval(start, end)
    #         else:
    #             self.addSelectionInterval(start, end)
    #
    # class StoreCurrencyType():
    #     def __init__(self, obj):
    #         self.obj = obj      # type: CurrencyType
    #
    #     def getCurrencyType(self):  return self.obj
    #     def getUUID(self):          return self.getCurrencyType().getUUID()
    #     def getSnapshots(self):     return self.getCurrencyType().getSnapshots()
    #
    #     def __str__(self):
    #         ct = self.getCurrencyType()
    #         # name = ct.getName()
    #         # if name is not None and len(name.trim()) > 0: return name
    #         # return ct.getIDString() + ":" + ct.getIDString()
    #         return ct.toString()
    #
    #     def __repr__(self):         return self.__str__()
    #     def toString(self):         return self.__str__()

    class MyAcctFilter(AcctFilter):
        def __init__(self, securities):
            # type: ([CurrencyType]) -> None
            self.securities = securities

        def matches(self, acct):
            # type: (Account) -> bool
            # noinspection PyUnresolvedReferences
            if not acct.getAccountType() == Account.AccountType.SECURITY: return False
            if acct.getCurrencyType() not in self.securities: return False
            return True

    # class MyTxnSearchFilter(TxnSearch):
    #
    #     def __init__(self, security, dateStart, dateEnd):
    #         self.security = security
    #         self.dateStart = dateStart
    #         self.dateEnd = dateEnd
    #
    #     def matchesAll(self): return False
    #
    #     def matches(self, txn):
    #         if txn.getDateInt() < self.dateStart or txn.getDateInt() > self.dateEnd: return False
    #         if txn.getAccount().getCurrencyType() != self.security: return False
    #         return True

    class MyDateRangeChooser(DateRangeChooser):
        def __init__(self, *args):
            self.specialListener = None
            super(self.__class__, self).__init__(*args)

        def setSpecialListener(self, specialListener): self.specialListener = specialListener
        def getSpecialListener(self): return self.specialListener

        def propertyChange(self, event):
            super(self.__class__, self).propertyChange(event)
            if self.specialListener is not None: self.specialListener.propertyChange(event)

    class ShowPopupTableChooser(JCheckBox):

        KEY = "show_popup_table_option"
        LABEL = "Show popup table:"
        LABEL_EXTRA = "(shows a summary table of data relevant to the graph)"

        def __init__(self, showPopupTable):
            # type: (bool) -> None
            super(self.__class__, self).__init__(self.__class__.LABEL_EXTRA)
            self.setSelected(showPopupTable)

        def getChoiceLabel(self): return JLabel(self.__class__.LABEL)

        def storeToParameters(self, parameters, saveKey=None):
            # type: (SyncRecord, str) -> None
            if saveKey is None: saveKey = self.__class__.KEY
            parameters.put(saveKey, self.isSelected())

        def loadFromParameters(self, parameters, loadKey=None):
            # type: (SyncRecord, str) -> None
            if loadKey is None: loadKey = self.__class__.KEY
            self.setSelected(parameters.getBoolean(loadKey, False))

    class IncludeHiddenSecuritiesChooser(JPanel):

        KEY = "include_hidden_securities_option"
        LABEL = "Hidden securities:"
        LABEL_INCLUDE = "Include"
        LABEL_EXCLUDE = "Exclude"
        LABEL_EXCLUDE_WHEN_ZERO = "Exclude when zero shares held throughout date range"
        INCLUDE_HIDDEN_KEY = "include_hidden"
        EXCLUDE_HIDDEN_KEY = "exclude_hidden"
        EXCLUDE_HIDDEN_ZERO_WHEN_KEY = "exclude_hidden_when_zero"

        def __init__(self, *args):
            # type: (any) -> None
            super(self.__class__, self).__init__(*args)

            self.buttonGroup = ButtonGroup()
            self.includeHiddenButton = JRadioButton(self.__class__.LABEL_INCLUDE, True)
            self.excludeHiddenButton = JRadioButton(self.__class__.LABEL_EXCLUDE, False)
            self.excludeHiddenWhenZeroButton = JRadioButton(self.__class__.LABEL_EXCLUDE_WHEN_ZERO, False)
            for btn in self.getAllButtons():
                self.buttonGroup.add(btn)
                self.add(btn)

        def getAllButtons(self): return [self.includeHiddenButton, self.excludeHiddenButton, self.excludeHiddenWhenZeroButton]
        def getChoiceLabel(self): return JLabel(self.__class__.LABEL)

        def getSelectedItem(self):
            if self.includeHiddenButton.isSelected(): return self.__class__.INCLUDE_HIDDEN_KEY
            if self.excludeHiddenButton.isSelected(): return self.__class__.EXCLUDE_HIDDEN_KEY
            if self.excludeHiddenWhenZeroButton.isSelected(): return self.__class__.EXCLUDE_HIDDEN_ZERO_WHEN_KEY

        def isIncludeHidden(self): return self.includeHiddenButton.isSelected()
        def isExcludeHidden(self): return self.excludeHiddenButton.isSelected()
        def isExcludeHiddenWhenZero(self): return self.excludeHiddenWhenZeroButton.isSelected()

        def setIncludeHidden(self, val): self.includeHiddenButton.setSelected(val)
        def setExcludeHidden(self, val): self.excludeHiddenButton.setSelected(val)
        def setExcludeHiddenWhenZero(self, val): self.excludeHiddenWhenZeroButton.setSelected(val)

        def getIncludeHiddenBtn(self): return self.includeHiddenButton
        def getExcludeHiddenBtn(self): return self.excludeHiddenButton
        def getExcludeHiddenWhenZeroBtn(self): return self.excludeHiddenWhenZeroButton

        def setEnabled(self, enabled):
            for btn in self.getAllButtons(): btn.setEnabled(enabled)

        def storeToParameters(self, parameters, saveKey=None):
            # type: (SyncRecord, str) -> None
            if saveKey is None: saveKey = self.__class__.KEY
            parameters.put(saveKey, self.getSelectedItem())

        def loadFromParameters(self, parameters, loadKey=None):
            # type: (SyncRecord, str) -> None
            if loadKey is None: loadKey = self.__class__.KEY
            loadOption = parameters.getStr(loadKey, self.__class__.INCLUDE_HIDDEN_KEY)
            for btn in self.getAllButtons(): btn.setSelected(False)
            if loadOption == self.__class__.INCLUDE_HIDDEN_KEY: self.includeHiddenButton.setSelected(True)
            elif loadOption == self.__class__.EXCLUDE_HIDDEN_KEY: self.excludeHiddenButton.setSelected(True)
            elif loadOption == self.__class__.EXCLUDE_HIDDEN_ZERO_WHEN_KEY: self.excludeHiddenWhenZeroButton.setSelected(True)
            else: self.includeHiddenButton.setSelected(True)

    class DisplayDataOptionChooser(JPanel):

        KEY = "display_data_option"
        LABEL = "Display data:"
        LABEL_WITHIN_BALANCE = "Only within share balance range"
        LABEL_WHOLE_DATE_RANGE = "Through whole date range"
        ONLY_WHERE_BALANCE_KEY = "only_where_balance"
        WHOLE_DATE_RANGE_KEY = "whole_date_range"

        def __init__(self):
            # type: () -> None
            super(self.__class__, self).__init__()
            self.buttonGroup = ButtonGroup()
            self.withinBalanceRangeButton = JRadioButton(self.__class__.LABEL_WITHIN_BALANCE, False)
            self.throughoutWholeRangeButton = JRadioButton(self.__class__.LABEL_WHOLE_DATE_RANGE, True)
            for btn in self.getAllButtons():
                self.buttonGroup.add(btn)
                self.add(btn)

        def getAllButtons(self): return [self.withinBalanceRangeButton, self.throughoutWholeRangeButton]
        def getChoiceLabel(self): return JLabel(self.__class__.LABEL)
        def getSelectedItem(self): return self.__class__.ONLY_WHERE_BALANCE_KEY if (self.withinBalanceRangeButton.isSelected()) else self.__class__.WHOLE_DATE_RANGE_KEY
        def isOnlyWithinBalanceRange(self): return self.withinBalanceRangeButton.isSelected()
        def isThroughoutWholeDateRange(self): return self.throughoutWholeRangeButton.isSelected()
        def setOnlyWithinBalanceRange(self, val): self.withinBalanceRangeButton.setSelected(val)
        def setAllDates(self, val): self.throughoutWholeRangeButton.setSelected(val)
        def getOnlyWithinBalanceRangeBtn(self): return self.withinBalanceRangeButton
        def getAllDatesBtn(self): return self.throughoutWholeRangeButton

        def setEnabled(self, enabled):
            for btn in self.getAllButtons(): btn.setEnabled(enabled)

        def isEnabled(self):
            for btn in self.getAllButtons():
                if not btn.isEnabled(): return False
            return True

        def storeToParameters(self, parameters, saveKey=None):
            # type: (SyncRecord, str) -> None
            if saveKey is None: saveKey = self.__class__.KEY
            parameters.put(saveKey, self.getSelectedItem())

        def loadFromParameters(self, parameters, loadKey=None):
            # type: (SyncRecord, str) -> None
            if loadKey is None: loadKey = self.__class__.KEY

            if parameters.getStr(loadKey, "") == self.__class__.ONLY_WHERE_BALANCE_KEY:
                self.withinBalanceRangeButton.setSelected(True)
                self.throughoutWholeRangeButton.setSelected(False)
            else:
                self.withinBalanceRangeButton.setSelected(False)
                self.throughoutWholeRangeButton.setSelected(True)

    class RebasePerformanceChooser(JPanel):

        KEY = "rebase_option"
        LABEL = "Rebase performance:"
        LABEL_REBASE_WITH_SHARE_BALANCE = "Rebase with share balance"
        LABEL_REBASE_FROM_START = "Rebase from start"
        REBASE_WITH_BALANCE_KEY = "rebase_with_balance"
        REBASE_FROM_START_KEY = "rebase_from_start"

        def __init__(self):
            # type: () -> None
            super(self.__class__, self).__init__()
            self.buttonGroup = ButtonGroup()
            self.rebaseWithinBalanceRangeButton = JRadioButton(self.__class__.LABEL_REBASE_WITH_SHARE_BALANCE, False)
            self.rebaseFromStartButton = JRadioButton(self.__class__.LABEL_REBASE_FROM_START, True)
            for btn in self.getAllButtons():
                self.buttonGroup.add(btn)
                self.add(btn)

        def getAllButtons(self): return [self.rebaseWithinBalanceRangeButton, self.rebaseFromStartButton]
        def getChoiceLabel(self): return JLabel(self.__class__.LABEL)
        def getSelectedItem(self): return self.__class__.REBASE_WITH_BALANCE_KEY if (self.rebaseWithinBalanceRangeButton.isSelected()) else self.__class__.REBASE_FROM_START_KEY
        def isRebaseWithBalance(self): return self.rebaseWithinBalanceRangeButton.isSelected()
        def isRebaseFromStart(self): return self.rebaseFromStartButton.isSelected()
        def setRebaseWithBalance(self, val): self.rebaseWithinBalanceRangeButton.setSelected(val)
        def setRebaseFromStart(self, val): self.rebaseFromStartButton.setSelected(val)
        def getRebaseWithBalanceBtn(self): return self.rebaseWithinBalanceRangeButton
        def getRebaseFromStartBtn(self): return self.rebaseFromStartButton

        def setEnabled(self, enabled):
            for btn in self.getAllButtons(): btn.setEnabled(enabled)

        def isEnabled(self):
            for btn in self.getAllButtons():
                if not btn.isEnabled(): return False
            return True

        def storeToParameters(self, parameters, saveKey=None):
            # type: (SyncRecord, str) -> None
            if saveKey is None: saveKey = self.__class__.KEY
            parameters.put(saveKey, self.getSelectedItem())

        def loadFromParameters(self, parameters, loadKey=None):
            # type: (SyncRecord, str) -> None
            if loadKey is None: loadKey = self.__class__.KEY
            if parameters.getStr(loadKey, "") == self.__class__.REBASE_WITH_BALANCE_KEY:
                self.rebaseWithinBalanceRangeButton.setSelected(True)
                self.rebaseFromStartButton.setSelected(False)
            else:
                self.rebaseWithinBalanceRangeButton.setSelected(False)
                self.rebaseFromStartButton.setSelected(True)

    class PercentageOrPriceChooser(JPanel):

        KEY = "percentage_price_balance_value"
        LABEL = "Relative performance:"
        LABEL_PERCENTAGE = "Show relative performance %"
        LABEL_PRICE = "Show absolute price"
        LABEL_SHARES = "Show number of shares"
        LABEL_VALUE = "Show absolute value"
        PERCENTAGE_KEY = "percentage"
        PRICE_KEY = "price"
        BALANCE_KEY = "balance"
        VALUE_KEY = "value"

        Y_AXIS_PERCENTAGE = "Relative price performance as %"
        Y_AXIS_PRICE = "Displaying absolute price"
        Y_AXIS_BALANCE = "Displaying number of shares held"
        Y_AXIS_VALUE = "Displaying absolute value of shares held"

        def __init__(self):
            # type: () -> None
            super(self.__class__, self).__init__()
            self.buttonGroup = ButtonGroup()
            self.percentageButton = JRadioButton(self.__class__.LABEL_PERCENTAGE, True)
            self.priceButton = JRadioButton(self.__class__.LABEL_PRICE, False)
            self.balanceButton = JRadioButton(self.__class__.LABEL_SHARES, False)
            self.valueButton = JRadioButton(self.__class__.LABEL_VALUE, False)
            for btn in self.getAllButtons():
                self.buttonGroup.add(btn)
                self.add(btn)

        def getAllButtons(self): return [self.percentageButton, self.priceButton, self.balanceButton, self.valueButton]
        def getChoiceLabel(self): return JLabel(self.__class__.LABEL)

        def getSelectedItem(self):
            if self.percentageButton.isSelected():  return self.__class__.PERCENTAGE_KEY
            if self.priceButton.isSelected():       return self.__class__.PRICE_KEY
            if self.balanceButton.isSelected():     return self.__class__.BALANCE_KEY
            if self.valueButton.isSelected():       return self.__class__.VALUE_KEY

        def getYAxisLabel(self):
            if self.isPercentage(): return self.__class__.Y_AXIS_PERCENTAGE
            if self.isPrice(): return self.__class__.Y_AXIS_PRICE
            if self.isBalance(): return self.__class__.Y_AXIS_BALANCE
            if self.isValue(): return self.__class__.Y_AXIS_VALUE

        def isPercentage(self): return self.percentageButton.isSelected()
        def isPrice(self): return self.priceButton.isSelected()
        def isBalance(self): return self.balanceButton.isSelected()
        def isValue(self): return self.valueButton.isSelected()

        def setPercentage(self, val): self.percentageButton.setSelected(val)
        def setPrice(self, val): self.priceButton.setSelected(val)
        def setBalance(self, val): self.balanceButton.setSelected(val)
        def setValue(self, val): self.valueButton.setSelected(val)

        def getPercentageBtn(self): return self.percentageButton
        def getPriceBtn(self): return self.priceButton
        def getBalanceBtn(self): return self.balanceButton
        def getValueBtn(self): return self.valueButton

        def setEnabled(self, enabled):
            for btn in self.getAllButtons(): btn.setEnabled(enabled)

        def isEnabled(self):
            for btn in self.getAllButtons():
                if not btn.isEnabled(): return False
            return True

        def storeToParameters(self, parameters, saveKey=None):
            # type: (SyncRecord, str) -> None
            if saveKey is None: saveKey = self.__class__.KEY
            parameters.put(saveKey, self.getSelectedItem())

        def loadFromParameters(self, parameters, loadKey=None):
            # type: (SyncRecord, str) -> None
            if loadKey is None: loadKey = self.__class__.KEY
            loadOption = parameters.getStr(loadKey, self.__class__.PERCENTAGE_KEY)
            for btn in self.getAllButtons(): btn.setSelected(False)
            if loadOption == self.__class__.PERCENTAGE_KEY:   self.percentageButton.setSelected(True)
            elif loadOption == self.__class__.PRICE_KEY:      self.priceButton.setSelected(True)
            elif loadOption == self.__class__.BALANCE_KEY:    self.balanceButton.setSelected(True)
            elif loadOption == self.__class__.VALUE_KEY:      self.valueButton.setSelected(True)
            else: self.percentageButton.setSelected(True)

    class SecurityFilterPanel(JPanel, ActionListener):

        KEY = "filter_include_hidden_securities_option"
        KEY_ACTION_ALL = "list_select_all"
        KEY_ACTION_NONE = "list_select_none"

        KEY_ACTION_MODE = "list_select_mode"

        KEY_ACTION_LABEL_TEXT = "Auto options:"

        KEY_ACTION_TOGGLE_AUTOSELECT_ON = "list_select_auto"
        KEY_ACTION_TOGGLE_AUTOSELECT_OFF = "list_select_manual"
        KEY_ACTION_TOGGLE_AUTOSELECT_ON_TEXT = "Auto-selecting all securities"
        KEY_ACTION_TOGGLE_AUTOSELECT_OFF_TEXT = "Manual selection mode"

        def __init__(self, moneydanceContext, callingClass):
            super(self.__class__, self).__init__()
            self.moneydanceContext = moneydanceContext
            self.callingClass = callingClass

            self.securityFilterPnl = ClickLabelListPanel()
            self.securityFilterPnl.addLabel("Select:")
            self.securityFilterPnl.addLabel(MDAction.makeKeyedAction(None,
                                                                "All",
                                                                self.__class__.KEY_ACTION_ALL,
                                                                self))

            self.securityFilterPnl.addLabel(MDAction.makeKeyedAction(None,
                                                                "None",
                                                                self.__class__.KEY_ACTION_NONE,
                                                                self))

            self.securityFilterPnl.addLabel(self.__class__.KEY_ACTION_LABEL_TEXT)

            self.autoSelectMode = False
            text = self.getAutoSelectText(self.getCurrentModeFromBool(self.getAutoSelectMode()))
            self._modeAction = MDAction.make(text).command(self.__class__.KEY_ACTION_MODE).callback(self.actionPerformed)
            self.securityFilterPnl.addLabel(self._modeAction)

            self.securityFilterPnl.layoutUI()
            self.add(self.securityFilterPnl)

        def getAutoSelectMode(self): return self.autoSelectMode
        def setAutoSelectMode(self, setting): self.autoSelectMode = setting

        def getCurrentModeFromBool(self, autoSelect):
            if autoSelect: return self.__class__.KEY_ACTION_TOGGLE_AUTOSELECT_ON
            return self.__class__.KEY_ACTION_TOGGLE_AUTOSELECT_OFF

        def getAutoSelectText(self, key):
            if key == self.__class__.KEY_ACTION_TOGGLE_AUTOSELECT_ON:
                text = self.__class__.KEY_ACTION_TOGGLE_AUTOSELECT_ON_TEXT
            else:
                text = self.__class__.KEY_ACTION_TOGGLE_AUTOSELECT_OFF_TEXT
            return text

        def updateAutoSelectToggleButton(self):
            self._modeAction.setNonKeyLabel(self.getAutoSelectText(self.getCurrentModeFromBool(self.getAutoSelectMode())))
            # self.callingClass.securityListChoiceJCB.storeSelectedUUIDs()
            # self.callingClass.securityListChoiceJCB.loadDataModel()
            # self.callingClass.securityListChoiceJCB.selectSecurities()

        def actionPerformed(self, event):
            #type: (ActionEvent) -> None

            myPrint("DB","SecurityFilterPanel.actionPerformed()", event)

            cmd = event.getActionCommand()

            if cmd == self.__class__.KEY_ACTION_MODE:
                myPrint("DB","*** Clicked auto-select on/off toggle")
                self.setAutoSelectMode(not self.getAutoSelectMode())
                self.updateAutoSelectToggleButton()
                if self.getAutoSelectMode():
                    self.callingClass.securityListChoiceJCB.selectAllNoneSecurities(True)

            elif cmd == self.__class__.KEY_ACTION_ALL:
                myPrint("DB","*** Clicked ALL")
                self.setAutoSelectMode(False)
                self.updateAutoSelectToggleButton()
                self.callingClass.securityListChoiceJCB.selectAllNoneSecurities(True)

            elif cmd == self.__class__.KEY_ACTION_NONE:
                myPrint("DB","*** Clicked NONE")
                self.setAutoSelectMode(False)
                self.updateAutoSelectToggleButton()
                self.callingClass.securityListChoiceJCB.selectAllNoneSecurities(False)

            elif isinstance(event.getSource(), SecurityChooser.SecurityJCheckBox):
                myPrint("DB","*** Security was selected/deselected (%s)" %(cmd))
                self.setAutoSelectMode(False)
                self.updateAutoSelectToggleButton()

            else:
                myPrint("DB","UNKNOWN ACTION? %s" %(cmd))
                return

            self.securityFilterPnl.invalidate()                                                                         # noqa
            self.securityFilterPnl.layoutUI()
            self.invalidate()
            self.revalidate()

        # noinspection PyUnusedLocal
        def storeToParameters(self, parameters, saveKey=None):
            # type: (SyncRecord, str) -> None
            if saveKey is None: saveKey = self.__class__.KEY
            parameters.put(saveKey, self.getAutoSelectMode())

        # noinspection PyUnusedLocal
        def loadFromParameters(self, parameters, loadKey=None):
            # type: (SyncRecord, str) -> None
            if loadKey is None: loadKey = self.__class__.KEY
            self.setAutoSelectMode(parameters.getBoolean(loadKey, True))
            self.updateAutoSelectToggleButton()

    class SecurityChooser(JScrollPane):

        KEY = "selected_securities"
        LABEL = "Securities:"

        class SecurityJCheckBox(JCheckBox, ActionListener):
            def __init__(self, _security, parentListener):
                # type: (CurrencyType, ActionListener) -> None
                self.securityCT = _security
                super(self.__class__, self).__init__(wrap_HTML_small(_security.toString(), " (hidden)" if (_security.getHideInUI()) else ""))
                self.parentListener = parentListener
                self.addActionListener(self)

            def getSecurity(self): return self.securityCT

            def actionPerformed(self, event):
                myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event)

                if debug:
                    myPrint("B","** actionL", event.getSource())
                    myPrint("B","** actionL", event.getSource().getName())
                    myPrint("B","** actionL", event.getActionCommand())

                self.parentListener.actionPerformed(event)


        def __init__(self, moneydanceContext, ctable, securityFilter):
            # type: (Main, CurrencyTable, SecurityFilterPanel) -> None
            self.moneydanceContext = moneydanceContext
            self.securityFilter = securityFilter
            self.ctable = ctable

            super(self.__class__, self).__init__()

            self.saveSelectedSecUUIDList = None         # type: SyncRecord
            self.baseSecurityList = []                  # type: [CurrencyType]
            self.securityJCheckBoxList = []             # type: [SecurityChooser.SecurityJCheckBox]

            self.pnlJCheckBoxList = JPanel(GridBagLayout())
            self.pnlJCheckBoxList.setBorder(BorderFactory.createEmptyBorder(4, 8, 4, 8))

            self.setViewportView(self.pnlJCheckBoxList)
            self.setViewportBorder(EmptyBorder(5, 5, 5, 5))

        def recreateJCheckBoxListPnl(self):
            y = 1
            self.pnlJCheckBoxList.removeAll()

            needsTitleIfHidden = True
            for selectJCB in self.securityJCheckBoxList:

                if selectJCB.getSecurity().getHideInUI() and needsTitleIfHidden:
                    needsTitleIfHidden = False
                    self.pnlJCheckBoxList.add(JLabel(("---Hidden securities---")), GridC.getc(1, y).field()); y += 1

                self.pnlJCheckBoxList.add(selectJCB, GridC.getc(1, y).field()); y += 1
            self.pnlJCheckBoxList.add(Box.createVerticalStrut(2), GridC.getc(1, y).wy(1.0))

            self.pnlJCheckBoxList.revalidate()
            self.pnlJCheckBoxList.repaint()

        def recreateJCheckBoxList(self):
            self.securityJCheckBoxList = []
            for sec in self.baseSecurityList:
                self.securityJCheckBoxList.append(self.__class__.SecurityJCheckBox(sec, self.securityFilter))

        def loadDataModel(self):
            securityList = []
            for curSec in sorted(self.ctable.getAllCurrencies(), key=lambda x: (0 if not (x.getHideInUI()) else 1, safeStr(x.getName()).upper())):
                # noinspection PyUnresolvedReferences
                if curSec.getCurrencyType() != CurrencyType.Type.SECURITY: continue
                # if curSec.getHideInUI() and not self.securityFilter.getIncludeHiddenSecurities(): continue
                securityList.append(curSec)
            self.baseSecurityList = securityList

            self.recreateJCheckBoxList()
            self.recreateJCheckBoxListPnl()

        def selectSecurities(self, lForceAll=False):

            if len(self.saveSelectedSecUUIDList) < 1 and not lForceAll: return False
            listModel = self.baseSecurityList
            if len(listModel) < 1: return False
            securitiesToSelect = []

            if lForceAll:
                listUUIDs = []
                allCurrencies = self.moneydanceContext.getCurrentAccount().getBook().getCurrencies().getAllCurrencies()
                for currSec in allCurrencies:
                    # noinspection PyUnresolvedReferences
                    if currSec.getCurrencyType() == CurrencyType.Type.SECURITY:
                        securitiesToSelect.append(currSec)
                        listUUIDs.append(currSec.getUUID())
                self.saveSelectedSecUUIDList = SyncRecord.createFrom(listUUIDs)

            else:
                for key in self.saveSelectedSecUUIDList:
                    foundSecurity = self.moneydanceContext.getCurrentAccountBook().getCurrencyByUUID(self.saveSelectedSecUUIDList[key])     # noqa
                    if foundSecurity is not None: securitiesToSelect.append(foundSecurity)

            for jcb in self.securityJCheckBoxList:
                jcb.setSelected(jcb.getSecurity() in securitiesToSelect)
            return True

        def selectAllNoneSecurities(self, select):
            for jcb in self.securityJCheckBoxList:
                jcb.setSelected(select)
            self.storeSelectedUUIDs()

        def getSelectedValues(self):
            selectedSecurities = []
            for secJCB in self.securityJCheckBoxList:
                if secJCB.isSelected():
                    selectedSecurities.append(secJCB.getSecurity())
            return selectedSecurities

        def storeSelectedUUIDs(self):
            selectedSecurities = self.getSelectedValues()
            listUUIDs = []
            for sec in selectedSecurities: listUUIDs.append(sec.getUUID())
            self.saveSelectedSecUUIDList = SyncRecord.createFrom(listUUIDs)

        def storeToParameters(self, parameters, saveKey=None):
            # type: (SyncRecord, str) -> None

            if saveKey is None: saveKey = self.__class__.KEY

            self.storeSelectedUUIDs()

            if len(self.saveSelectedSecUUIDList) < 1:
                parameters.removeSubset(saveKey)
            else:
                parameters.put(saveKey, self.saveSelectedSecUUIDList)

        def loadFromParameters(self, parameters, loadKey=None):
            # type: (SyncRecord, str) -> bool

            if loadKey is None: loadKey = self.__class__.KEY

            self.loadDataModel()

            self.saveSelectedSecUUIDList = parameters.getSubset(loadKey)        # type: SyncRecord

            result = self.selectSecurities(lForceAll=self.securityFilter.getAutoSelectMode())
            return result

    class MyGraphSet():     # copies: com.moneydance.apps.md.view.gui.graphtool.GraphSet
        def __init__(self, title):
            # super(self.__class__, self).__init__(title)     # We are only extending GraphSet so that later methods recognise the passed class
            self.subTitle = None
            self.vertical = False
            self.showKey = True
            self.title = title
            self.popupTableData = None                  # type: {}
            self.currency = None
            self.settings = None            # type: SyncRecord
            self.sectionMap = HashMap()
            self.timeData = None            # type: TimeSeriesCollection
            self.lastTimeSeries = None      # type: TimeSeries
            self.show3D = True
            self.rateFormatString = None
            self.yAxisLabel = None
            self.xAxisLabel = None
            self.showLegend = True
            self.shouldPrintTitle = None
            self.shouldShowTitle = None
            self.setShouldShowTitle(False)

        def getShouldPrintTitle(self): return self.shouldPrintTitle
        def getShouldShowTitle(self): return self.shouldShowTitle
        def setShouldShowTitle(self, shouldShowTitle):
            self.shouldShowTitle = shouldShowTitle
            self.shouldPrintTitle = not self.shouldShowTitle

        def setShowLegend(self, showLegend): self.showLegend = showLegend
        def getShowLegend(self): return self.showLegend

        def setYAxisLabel(self, label): self.yAxisLabel = label
        def getYAxisLabel(self): return self.yAxisLabel

        def setXAxisLabel(self, label): self.xAxisLabel = label
        def getXAxisLabel(self): return self.xAxisLabel

        def setPopupTableData(self, _tableData): self.popupTableData = _tableData
        def getPopupTableData(self): return self.popupTableData
        def getCurrency(self): return self.currency
        def setSettings(self, settings): self.settings = settings
        def getSettings(self): return self.settings

        def getDetailsByName(self, name):
            # type: (str) -> MyGraphSet.LineGraphSection
            return self.sectionMap.get(name)

        def addTimeSeries(self, name, details, currency, uri):
            # type: (str, [str], CurrencyType, str) -> TimeSeries
            if self.timeData is None:
                self.timeData = TimeSeriesCollection()
            self.lastTimeSeries = TimeSeries(name)
            section = MyGraphSet.LineGraphSection(name, details, currency, uri)
            self.lastTimeSeries.setKey(section)
            self.timeData.addSeries(self.lastTimeSeries)
            self.currency = currency
            self.sectionMap.put(name, section)
            return self.lastTimeSeries

        # def addTimeData(self, period, value):
        #     # type: (RegularTimePeriod, float) -> None
        #     try:
        #         self.lastTimeSeries.addOrUpdate(period, value)
        #     except SeriesException as se:
        #         myPrint("B", "possibly duplicate interval: " + se)

        # def getTimeSeries(self):
        #     # type: () -> TimeSeries
        #     return self.lastTimeSeries


        def setShowKey(self, showKey): self.showKey = showKey
        def getShowKey(self): return self.showKey

        def getTitle(self): return self.title
        def setTitle(self, title): self.title = title

        def getSubTitle(self): return self.subTitle
        def setSubTitle(self, title): self.subTitle = title

        def setShowIn3D(self, show): self.show3D = show
        def getShowIn3D(self): return self.show3D

        def setIsVertical(self, vertical): self.vertical = vertical
        def isVertical(self): return self.vertical

        def getMainGraph(self):
            # type: () -> XYDataset
            return self.timeData

        def setRateFormatString(self, rateFormatString): self.rateFormatString = rateFormatString
        def getRateFormatString(self, dec): return self.rateFormatString                                                # noqa

        class LineGraphSection(Comparable):
            def __init__(self, name, details, currency, uri):
                # type: (str, [str], CurrencyType, str) -> None
                self.name = String(name)
                self.details = details
                self.uri = uri
                self.currency = currency

            def toString(self): return self.name

            def compareTo(self, other):
                # type (LineGraphSection) -> int
                return String(self.toString()).compareTo(String(other.toString()))

            def equals(self, other):
                if other == self:
                    return True
                if isinstance(other, MyGraphSet.LineGraphSection):
                    return (self.compareTo(other) == 0)
                return False

            def hashCode(self): return self.name.hashCode()


    # class MyCurrencyType:
    #     def __init__(self, name, decimalPlaces, prefix, suffix, specialLabel, dec):
    #         self.name = name
    #         self.decimalPlaces = decimalPlaces
    #         self.prefix = prefix
    #         self.suffix = suffix
    #         self.specialLabel = specialLabel
    #         self.dec = dec
    #
    #     def getComma(self):
    #         if self.dec != ".": return "."
    #         return ","
    #
    #         specialFormat = "#,##0.00%"      # Gets used by DecimalFormat()
    #         graphData.setRateFormatString(specialFormat)
    #
    #     def formatFancy(self, amt):
    #         amtStr =
    #
    #
    #
    # copies com.moneydance.apps.md.view.gui.graphtool.CurrencyGraph
    class MySecurityPerformanceGraph(GraphGenerator):

        title = "Graph"
        CURRENCY_LABEL_KEY = "graph_label_key"
        moneydanceContext = MD_REF

        class StoreSecurityRow:
            def __init__(self, secCT, valueStart, valueEnd, priceStart, priceEnd):
                self.sec = secCT
                self.valueStart = valueStart
                self.valueEnd = valueEnd
                self.priceStart = priceStart
                self.priceEnd = priceEnd

                if self.priceStart == 0.0 or self.priceEnd == 0.0:
                    self.ownPricePerformance = 0.0
                else:
                    self.ownPricePerformance = ((self.priceEnd - self.priceStart) / self.priceStart)

                if self.valueStart == 0 or self.valueEnd == 0:
                    self.ownValuePerformance = 0.0
                else:
                    self.ownValuePerformance = (float(self.valueEnd - self.valueStart) / float(self.valueStart))

        class StorePopupTableData:

            HEADINGS = ["Security ", "Starting valuation ", "Ending valuation ", "% valuation change ", "% of end value total ", "Starting Price ", "Ending Price ", "Price Performance % "]
            FORMATS =  ["str",       "val_long",            "val_long",          "pct",                 "pct",                   "price",           "price",         "pct"]

            def __init__(self, base, dec):
                self.base = base
                self.dec = dec
                self.startDate = None
                self.endDate = None
                self.startPrice = None
                self.endPrice = None
                self.portfolioStartValue = None
                self.portfolioEndValue = None
                self.portfolioValueChange = None
                self.securityObjs = []          # type: [MySecurityPerformanceGraph.StoreSecurityRow]

            def getPortfolioStartValueFancy(self): return self.base.formatFancy(self.portfolioStartValue, self.dec)
            def getPortfolioEndValueFancy(self): return self.base.formatFancy(self.portfolioEndValue, self.dec)

            def storeSecurityRow(self, secObj):
                # type: (MySecurityPerformanceGraph.StoreSecurityRow) -> None
                self.securityObjs.append(secObj)

            def generateTableData(self):
                # type: () -> [str, long, long, float, float]
                returnTable = []
                if len(self.securityObjs) < 1: return returnTable

                for storedSecObj in self.securityObjs:
                    if storedSecObj.valueEnd == 0 or self.portfolioEndValue == 0:
                        pct = 0.0
                    else:
                        pct = (float(storedSecObj.valueEnd) / float(self.portfolioEndValue))
                    returnTable.append([storedSecObj.sec.getName(),
                                        storedSecObj.valueStart,
                                        storedSecObj.valueEnd,
                                        storedSecObj.ownValuePerformance,
                                        pct,
                                        storedSecObj.priceStart,
                                        storedSecObj.priceEnd,
                                        storedSecObj.ownPricePerformance])

                return returnTable

            def dumpSelf(self):
                myPrint("B","StorePopupTableData:\n"
                            "startDate:            %s\n"
                            "endDate:              %s\n"
                            "startPrice:           %s\n"
                            "endPrice:             %s\n"
                            "portfolioStartValue:  %s\n"
                            "portfolioEndValue:    %s\n"
                            "portfolioValueChange: %s\n"
                        %(self.startDate, self.endDate, self.startPrice, self.endPrice, self.portfolioStartValue, self.portfolioEndValue, self.portfolioValueChange))
                ownList = self.generateTableData()
                for row in ownList: myPrint("B", "... row: ", row)

        def __init__(self, title=None):
            super(self.__class__, self).__init__()
            self.renamedConfigPanel = None              # type: JPanel
            self.dateRanger = None                      # type: MyDateRangeChooser
            self.intervalChoice = None                  # type: IntervalChooser
            self.displayDataChoice = None               # type: DisplayDataOptionChooser
            self.rebaseChoice = None                    # type: RebasePerformanceChooser
            self.percentageChoice = None                # type: PercentageOrPriceChooser
            self.includeHiddenSecuritiesChoice = None   # type: IncludeHiddenSecuritiesChooser
            self.showPopupTableChoice = None            # type: ShowPopupTableChooser
            # self.securityListChoice = None            # type: JList
            self.securityFilter = None                  # type: SecurityFilterPanel
            self.securityListChoiceJCB = None           # type: SecurityChooser
            self.suppressMessages = False
            self.book = MySecurityPerformanceGraph.moneydanceContext.getCurrentAccountBook()
            self.ctable = self.book.getCurrencies()
            self.base = self.book.getCurrencies().getBaseType()
            self.dec = MySecurityPerformanceGraph.moneydanceContext.getPreferences().getDecimalChar()
            if title is not None: MySecurityPerformanceGraph.setTitle(title)

        def getName(self): return MySecurityPerformanceGraph.getTitle()

        @staticmethod
        def getTitle(): return MySecurityPerformanceGraph.title

        @staticmethod
        def setTitle(newTitle): MySecurityPerformanceGraph.title = newTitle

        def checkForDefaultSettings(self, currentSettings, reset):
            # type: (SyncRecord, bool) -> SyncRecord

            if reset or currentSettings is None or currentSettings.isEmpty():
                newSettings = SyncRecord()
                newSettings.put(DateRangeOption.CONFIG_KEY, DateRangeChooser.DR_YEAR_TO_DATE)
                newSettings.put(self.PARAM_GROUP_BY, "m")
                return newSettings

            return currentSettings

        def setParameters(self, settings):
            # type: (SyncRecord) -> None
            reset = self.checkForResetSignal(settings)
            self.getConfigPanel(reset)
            loadedSettings = self.checkForDefaultSettings(settings, reset)

            myPrint("DB","Loaded settings now: %s" %(loadedSettings))

            self.dateRanger.loadFromParameters(loadedSettings)

            if loadedSettings.containsKey(self.PARAM_GROUP_BY):
                self.intervalChoice.selectFromParams(loadedSettings.getStr(self.PARAM_GROUP_BY, ""))

            self.displayDataChoice.loadFromParameters(loadedSettings)
            self.rebaseChoice.loadFromParameters(loadedSettings)
            self.percentageChoice.loadFromParameters(loadedSettings)
            self.showPopupTableChoice.loadFromParameters(loadedSettings)
            self.securityFilter.loadFromParameters(loadedSettings)
            self.includeHiddenSecuritiesChoice.loadFromParameters(loadedSettings)
            # self.securityListChoice.loadFromParameters(loadedSettings)
            self.securityListChoiceJCB.loadFromParameters(loadedSettings)

            self.checkButtons()

        def checkButtons(self):
            # Override rebase if main selection is all dates (and not within balance range)
            if self.displayDataChoice.isThroughoutWholeDateRange() or not self.percentageChoice.isPercentage():
                self.rebaseChoice.setRebaseWithBalance(False)
                self.rebaseChoice.setRebaseFromStart(True)
                self.rebaseChoice.setEnabled(False)
            else:
                self.rebaseChoice.setEnabled(True)

        def setupConfigPanel(self, reset):
            # type: (bool) -> None

            # Override .setupConfigPanel() to rename self.configPanel as Jython auto-generates setters and getters
            # .. this (causes .getConfigPanel() to get called (in error) whenever self.configPanel was referred to.....

            if reset and self.renamedConfigPanel is not None:
                self.renamedConfigPanel.removeAll()
            else:
                self.renamedConfigPanel = JPanel(GridBagLayout())
                self.renamedConfigPanel.setBorder(BorderFactory.createEmptyBorder(4, 8, 4, 8))

            self.dateRanger = MyDateRangeChooser(MySecurityPerformanceGraph.moneydanceContext.getUI())
            self.loadSettingsFromPreferences()

        def getConfigPanel(self, reset):
            # type: (bool) -> JPanel

            if not reset and self.renamedConfigPanel is not None: return self.renamedConfigPanel
            self.setupConfigPanel(reset)

            self.intervalChoice = IntervalChooser(MySecurityPerformanceGraph.moneydanceContext.getUI(), True, 2)

            self.displayDataChoice = DisplayDataOptionChooser()
            self.rebaseChoice = RebasePerformanceChooser()
            self.percentageChoice = PercentageOrPriceChooser()

            self.showPopupTableChoice = ShowPopupTableChooser(False)

            self.includeHiddenSecuritiesChoice = IncludeHiddenSecuritiesChooser()

            self.securityFilter = SecurityFilterPanel(MySecurityPerformanceGraph.moneydanceContext, self)

            self.securityListChoiceJCB = SecurityChooser(MySecurityPerformanceGraph.moneydanceContext, self.ctable, self.securityFilter)

            # self.securityListChoice = MyJList(MySecurityPerformanceGraph.moneydanceContext, self.ctable, self.includeHiddenSecuritiesChoice, [])
            # self.securityListChoice.setBackground(MySecurityPerformanceGraph.moneydanceContext.getUI().getColors().listBackground)
            # self.securityListChoice.setCellRenderer(MyJListRenderer())
            # self.securityListChoice.setFixedCellHeight(self.securityListChoice.getFixedCellHeight()+30)
            # self.securityListChoice.setSelectionMode(ListSelectionModel.MULTIPLE_INTERVAL_SELECTION)
            # self.securityListChoice.setSelectionModel(MyDefaultListSelectionModel())
            #
            # scrollpane = JScrollPane(self.securityListChoice, JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED,JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED)
            # scrollpane.setViewportBorder(EmptyBorder(5, 5, 5, 5))
            # scrollpane.setOpaque(False)

            y = 0
            if isinstance(self.renamedConfigPanel, JPanel): pass
            self.renamedConfigPanel.add(self.dateRanger.getChoiceLabel(), GridC.getc(1, y).label())
            self.renamedConfigPanel.add(self.dateRanger.getChoice(), GridC.getc(2, y).field());        y += 1
            self.renamedConfigPanel.add(self.dateRanger.getStartLabel(), GridC.getc(1, y).label())
            self.renamedConfigPanel.add(self.dateRanger.getStartField(), GridC.getc(2, y).field());    y += 1
            self.renamedConfigPanel.add(self.dateRanger.getEndLabel(), GridC.getc(1, y).label())
            self.renamedConfigPanel.add(self.dateRanger.getEndField(), GridC.getc(2, y).field());      y += 1

            self.renamedConfigPanel.add(JLabel(UiUtil.getLabelText((MySecurityPerformanceGraph.moneydanceContext.getUI()), "graph_groupby")), GridC.getc(1, y).label())
            self.renamedConfigPanel.add(self.intervalChoice, GridC.getc(2, y).field());                y += 1

            self.renamedConfigPanel.add(self.showPopupTableChoice.getChoiceLabel(), GridC.getc(1, y).label())
            self.renamedConfigPanel.add(self.showPopupTableChoice, GridC.getc(2, y).west());            y += 1

            self.renamedConfigPanel.add(self.displayDataChoice.getChoiceLabel(), GridC.getc(1, y).label())
            self.renamedConfigPanel.add(self.displayDataChoice, GridC.getc(2, y).west());       y += 1
            self.renamedConfigPanel.add(self.rebaseChoice.getChoiceLabel(), GridC.getc(1, y).label())
            self.renamedConfigPanel.add(self.rebaseChoice, GridC.getc(2, y).west());                   y += 1
            self.renamedConfigPanel.add(self.percentageChoice.getChoiceLabel(), GridC.getc(1, y).label())
            self.renamedConfigPanel.add(self.percentageChoice, GridC.getc(2, y).west());               y += 1

            self.renamedConfigPanel.add(self.includeHiddenSecuritiesChoice.getChoiceLabel(), GridC.getc(1, y).label())
            self.renamedConfigPanel.add(self.includeHiddenSecuritiesChoice, GridC.getc(2, y).west());   y += 1

            self.renamedConfigPanel.add(self.securityFilter, GridC.getc(2, y).west());                  y += 1

            self.renamedConfigPanel.add(JLabel("Securities"), GridC.getc(1, y).label())
            # self.renamedConfigPanel.add(scrollpane, GridC.getc(2, y).wxy(1.0, 1.0).fillboth().insets(GridC.TOP_FIELD_INSET, GridC.LEFT_FIELD_INSET, GridC.BOTTOM_FIELD_INSET, GridC.RIGHT_FIELD_INSET)); y += 1

            self.renamedConfigPanel.add(self.securityListChoiceJCB, GridC.getc(2, y).wxy(1.0, 1.0).fillboth().insets(GridC.TOP_FIELD_INSET, GridC.LEFT_FIELD_INSET, GridC.BOTTOM_FIELD_INSET, GridC.RIGHT_FIELD_INSET)); y += 1

            # Graphs
            # jchecklistbox
            # IconedCellRenderer

            # self.renamedConfigPanel.add(Box.createVerticalStrut(2), GridC.getc(2, y).wy(1.0))

            class MyActionListener(ItemListener, ActionListener):
                def __init__(self, callingClass):
                    self.callingClass = callingClass

                def actionPerformed(self, event):
                    myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event)

                    if debug:
                        myPrint("B","** actionL", event.getSource())
                        myPrint("B","** actionL", event.getSource().getName())
                        myPrint("B","** actionL", event.getActionCommand())

                    if (event.getSource() in self.callingClass.displayDataChoice.getAllButtons()
                            or event.getSource() in self.callingClass.percentageChoice.getAllButtons()):
                        self.callingClass.checkButtons()

                    if event.getSource() is self.callingClass.includeHiddenSecuritiesChoice:
                        pass
                        # # self.callingClass.securityListChoice.loadDataModel()
                        # # self.callingClass.securityListChoice.selectSecurities()
                        #
                        # self.callingClass.securityListChoiceJCB.storeSelectedUUIDs()
                        # self.callingClass.securityListChoiceJCB.loadDataModel()
                        # self.callingClass.securityListChoiceJCB.selectSecurities()

                def propertyChange(self, event):
                    myPrint("DB", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event)

                    if debug:
                        myPrint("B","** actionP", event.getSource())
                        myPrint("B","** actionP", event.getSource().getName())
                        myPrint("B","** actionP", event.getPropertyName())
                        myPrint("B","** actionP", event.getOldValue())
                        myPrint("B","** actionP", event.getNewValue())

                def itemStateChanged(self, e):
                    myPrint("DB","** itemStateC", e.getSource().getName())
                    # if ((e.getSource().getName() == "SELECT_SOURCE_ACCOUNT" and e.getStateChange() == ItemEvent.SELECTED)
                    #         or (e.getSource().getName() == "ENABLE_SECURITY_FILTER" and e.getSource().isSelected())):
                    #     subAccts = []
                    #     if self.selectSource.getSelectedItem() is not None:
                    #         for sAcct in self.selectSource.getSelectedItem().getSubAccounts(): subAccts.append(StoreAccountSecurity(sAcct))
                    #     self.filterSecurity.setModel(DefaultComboBoxModel(subAccts))
                    #     self.filterSecurity.setSelectedIndex(-1)

            myActionListener = MyActionListener(self)
            self.dateRanger.setSpecialListener(myActionListener)
            for c in self.renamedConfigPanel.getComponents():
                if isinstance(c, (JComboBox, JCheckBox)): c.addActionListener(myActionListener)
                if isinstance(c, (JPanel)):
                    for cc in c.getComponents():
                        if cc in self.displayDataChoice.getAllButtons() or cc in self.percentageChoice.getAllButtons():
                            cc.addActionListener(myActionListener)

            return self.renamedConfigPanel

        def loadSettingsFromPreferences(self):
            # type: () -> None
            super(self.__class__, self).loadSettingsFromPreferences()                                                   # noqa

        def checkForResetSignal(self, currentSettings):
            # type: (SyncRecord) -> bool
            return super(self.__class__, self).checkForResetSignal(currentSettings)                                     # noqa

        def setSuppressMessages(self, lSuppress): self.suppressMessages = lSuppress

        def generate(self):
            # type: () -> MyGraphSet

            self.loadSettingsFromPreferences()      # Just loads the current MD Preferences (not report settings)

            graphParameters = SyncRecord()
            graphParameters.put(self.PARAM_GROUP_BY, self.intervalChoice.getSelectedInterval().getConfigKey())

            self.displayDataChoice.storeToParameters(graphParameters)
            self.rebaseChoice.storeToParameters(graphParameters)
            self.percentageChoice.storeToParameters(graphParameters)

            self.showPopupTableChoice.storeToParameters(graphParameters)

            self.securityFilter.storeToParameters(graphParameters)

            self.includeHiddenSecuritiesChoice.storeToParameters(graphParameters)
            # self.securityListChoice.storeToParameters(graphParameters)

            self.securityListChoiceJCB.storeToParameters(graphParameters)

            self.dateRanger.storeToParameters(graphParameters)

            graphParameters.put(DisplayDataOptionChooser.KEY, self.displayDataChoice.getSelectedItem())
            graphParameters.put(RebasePerformanceChooser.KEY, self.rebaseChoice.getSelectedItem())
            graphParameters.put(PercentageOrPriceChooser.KEY, self.percentageChoice.getSelectedItem())

            GraphDataSet.resetColors()
            graphData = MySecurityPerformanceGraph.generateGraph(MySecurityPerformanceGraph.moneydanceContext.getUI(),
                                                                      self.dec,
                                                                      self.includeHiddenSecuritiesChoice,
                                                                      self.displayDataChoice,
                                                                      self.rebaseChoice,
                                                                      self.percentageChoice,
                                                                      self.securityListChoiceJCB.getSelectedValues(),
                                                                      self.intervalChoice.getSelectedInterval(),
                                                                      self.dateRanger)
            if graphData is None:
                if not self.suppressMessages:
                    MySecurityPerformanceGraph.moneydanceContext.getUI().showErrorMessage(MySecurityPerformanceGraph.moneydanceContext.getUI().getStr("nothing_to_graph"))
                return None

            self.getInfo().setReportParameters(graphParameters)

            graphData.setSettings(graphParameters)
            return graphData

        @staticmethod
        def getFirstValue(theList):
            # type: ([any]) -> any
            if len(theList) > 0:
                for i in range(0, len(theList)):
                    value = theList[i]
                    if value is not None: return value
            return None

        @staticmethod
        def getLastValue(theList):
            # type: ([any]) -> any
            if len(theList) > 0:
                for i in reversed(range(0, len(theList))):
                    value = theList[i]
                    if value is not None: return value
            return None

        @staticmethod
        def generateGraph(resources, dec, includeHiddenSecuritiesChoice, displayDataChoice, rebaseChoice, percentageChoice, selectedSecurities, interval, dateRangeChooser):
            # type: (MDResourceProvider, str, IncludeHiddenSecuritiesChooser, DisplayDataOptionChooser, RebasePerformanceChooser, PercentageOrPriceChooser, [CurrencyType], TimeInterval, MyDateRangeChooser) -> TimeSeries

            myPrint("DB", "In .generateGraph()")

            dateRange = dateRangeChooser.getDateRange()
            beginDate = dateRange.getStartDateInt()
            endDate = dateRange.getEndDateInt()

            graphData = None   # type: MyGraphSet
            tableData = None   # type: MySecurityPerformanceGraph.StorePopupTableData

            myPrint("DB","selectedSecurities:", selectedSecurities)

            try:
                if len(selectedSecurities) < 1: return None

                if dateRangeChooser.getAllDatesSelected() or endDate > DateUtil.getStrippedDateInt():
                    # Work out the start/end dates when 'all dates' selected. Base this on price history found...
                    ALL_DATES_KEY = "all_dates"
                    dates = MySecurityPerformanceGraph.getSnapshotDates(selectedSecurities, beginDate, endDate, ALL_DATES_KEY, dateRangeChooser.getAllDatesSelected())
                    if dates[ALL_DATES_KEY].size() != 2:
                        myPrint("B", "** ALL DATES selected... No price history range found to recalculate a new valid date range... Will abort graph")
                        return None
                    beginDate = dates[ALL_DATES_KEY].first()
                    endDate = dates[ALL_DATES_KEY].last()
                    myPrint("B", "** ALL DATES selected... Recalculated dates to range where price history exists - [Start: %s End: %s]"
                            %(convertStrippedIntDateFormattedText(beginDate), convertStrippedIntDateFormattedText(endDate)))

                    if debug:
                        for checkDateKey in dates: myPrint("B","dates: %s" %(checkDateKey), dates[checkDateKey])

                # Now grab the start/end price history range per security...
                dates = MySecurityPerformanceGraph.getSnapshotDates(selectedSecurities, beginDate, endDate, None)
                if debug:
                    for checkDateKey in dates: myPrint("B","dates: %s" %(checkDateKey), dates[checkDateKey])

                intervalUtil = TimeIntervalUtil()   # type: TimeIntervalUtil
                firstInterval = intervalUtil.getIntervalStart(beginDate, interval)
                lastInterval = intervalUtil.getIntervalEnd(endDate, interval)
                numIntervals = intervalUtil.getNumIntervals(firstInterval, lastInterval, interval)
                intervals = intervalUtil.getIntervalPoints(numIntervals, firstInterval, interval)

                if debug:
                    myPrint("B","interval: %s, firstInterval: %s, lastInterval: %s, numIntervals: %s" %(interval, firstInterval, lastInterval, numIntervals))
                    myPrint("B","intervals: %s" %(intervals))

                if len(intervals) < 2: return None

                _book = MySecurityPerformanceGraph.moneydanceContext.getCurrentAccountBook()
                base = _book.getCurrencies().getBaseType()

                # if dec == ".":
                #     specialFormat = "#,##0.00%"      # Gets used by DecimalFormat()
                # else:
                #     specialFormat = "#.##0,00%"      # Gets used by DecimalFormat()
                # graphData.setRateFormatString(specialFormat)

                def createFakeCurrency(_decimals, _labelText, _prefix, _suffix, _name):
                    fakeBook = AccountBook.fakeAccountBook()
                    fakeCT = CurrencyType(fakeBook.getCurrencies())
                    fakeCT.setEditingMode()
                    fakeCT.setRelativeRate(1.0)
                    fakeCT.setTickerSymbol("SPECIAL")
                    fakeCT.setIDString("^SPECIAL")
                    fakeCT.setDecimalPlaces(_decimals)
                    fakeCT.setPrefix(_prefix)
                    fakeCT.setSuffix(_suffix)
                    fakeCT.setName(_name)
                    if _labelText is not None:
                        fakeCT.setParameter(MySecurityPerformanceGraph.CURRENCY_LABEL_KEY, _labelText)
                    return fakeCT

                DECIMALS_PERCENTAGE = base.getDecimalPlaces()
                DECIMALS_PRICE = 4
                DECIMALS_BALANCE = 1
                DECIMALS_VALUE = base.getDecimalPlaces()

                if percentageChoice.isPercentage():
                    yAxisLabelText = ""
                    specialCT = createFakeCurrency(DECIMALS_PERCENTAGE, "Performance:", "", "%", "Special % Currency")
                elif percentageChoice.isPrice():
                    yAxisLabelText = " (%s)" %(base.getPrefix())
                    specialCT = createFakeCurrency(DECIMALS_PRICE, "Price:", base.getPrefix(), base.getSuffix(), "Special Price Currency")
                elif percentageChoice.isBalance():
                    yAxisLabelText = ""
                    specialCT = createFakeCurrency(DECIMALS_BALANCE, "Share balance:", "", " units", "Special Balance Currency")
                elif percentageChoice.isValue():
                    yAxisLabelText = " (%s)" %(base.getPrefix())
                    specialCT = createFakeCurrency(DECIMALS_VALUE, "Value:", base.getPrefix(), base.getSuffix(), "Special Value Currency")
                else: raise Exception("ERROR: percentage/price/balance/value choice invalid!")

                table_valueStart = 0
                table_valueEnd = 0

                for sec in selectedSecurities:

                    if includeHiddenSecuritiesChoice.isIncludeHidden() and sec.getHideInUI():
                        myPrint("DB","%s: NOTE keeping hidden security as IncludeHidden selected..." %(sec))

                    if includeHiddenSecuritiesChoice.isExcludeHidden() and sec.getHideInUI():
                        myPrint("DB","%s: SKIPPING hidden security as ExcludeHidden was requested..." %(sec))
                        continue

                    if dates[sec].size() < 2:
                        myPrint("DB","%s: SKIPPING as dates < 2" %(sec))
                        continue

                    # Limit the date range to where price history exists
                    thisSecPriceHistBeginDate = int(dates[sec].first())
                    thisSecPriceHistEndDate = int(dates[sec].last())

                    thisSecPriceHistBeginInterval = intervalUtil.getIntervalStart(thisSecPriceHistBeginDate, interval)
                    thisSecPriceHistEndInterval = intervalUtil.getIntervalEnd(thisSecPriceHistEndDate, interval)

                    if thisSecPriceHistBeginInterval == thisSecPriceHistEndInterval:
                        myPrint("DB","%s: SKIPPING as thisSecPriceHistBeginInterval == thisSecPriceHistEndInterval" %(sec))
                        continue

                    thisSecWithinBalBeginInterval = thisSecPriceHistBeginInterval
                    thisSecWithinBalEndInterval = thisSecPriceHistEndInterval

                    # if displayDataChoice.isOnlyWithinBalanceRange():
                    acctBalancesForDatesPerSecurity = {}

                    secStartPrice = CurrencyUtil.getSplitAdjustedRelativeUserPrice(sec, base, beginDate)
                    secEndPrice = CurrencyUtil.getSplitAdjustedRelativeUserPrice(sec, base, endDate)

                    thisSecurityTotalStartValue = 0
                    thisSecurityTotalEndValue = 0

                    # Get the Security Accounts 'attached' to this Security(Currency)
                    securityAccts = AccountUtil.allMatchesForSearch(MySecurityPerformanceGraph.moneydanceContext.getCurrentAccount().getBook(), MyAcctFilter([sec]))
                    for secAcct in securityAccts:
                        acctBalancesForDatesPerSecurity[secAcct] = AccountUtil.getBalancesAsOfDates(_book, secAcct, intervals, True)

                        # startBal = sec.getDoubleValue(AccountUtil.getBalanceAsOfDate(_book, secAcct, beginDate))
                        # endBal = sec.getDoubleValue(AccountUtil.getBalanceAsOfDate(_book, secAcct, endDate))
                        # startValue = base.getLongValue(startBal * secStartPrice)
                        # endValue = base.getLongValue(endBal * secEndPrice)

                        startBal = AccountUtil.getBalanceAsOfDate(_book, secAcct, beginDate)
                        endBal = AccountUtil.getBalanceAsOfDate(_book, secAcct, endDate)
                        startValue = CurrencyTable.convertValue(startBal, sec, base, beginDate)
                        endValue = CurrencyTable.convertValue(endBal, sec, base, endDate)

                        thisSecurityTotalStartValue += startValue
                        thisSecurityTotalEndValue += endValue

                    if debug:
                        for checkBalancesKey in acctBalancesForDatesPerSecurity:
                            myPrint("DB", "acctBalancesForDatesPerSecurity: %s" %(checkBalancesKey), acctBalancesForDatesPerSecurity[checkBalancesKey])

                    # Now grand total the balances by date for all security accounts holding the same security(currency)
                    yValues_balances = [0.0] * len(intervals)
                    for acctBal in acctBalancesForDatesPerSecurity:
                        acctBalRow = acctBalancesForDatesPerSecurity[acctBal]
                        for i in range(0, len(intervals)):
                            yValues_balances[i] += sec.getDoubleValue(acctBalRow[i])

                    if includeHiddenSecuritiesChoice.isExcludeHiddenWhenZero() and sec.getHideInUI():
                        myPrint("DB","%s: Hidden security found and ExcludeHiddenWhenZero was selected.... checking...."  %(sec))
                        foundBalance = False
                        for i in range(0, len(intervals)):
                            if yValues_balances[i] != 0:
                                foundBalance = True
                                break
                        if foundBalance:
                            myPrint("DB","%s: .... found a balance.... will keep...." %(sec))
                        else:
                            myPrint("DB","%s: SKIPPING hidden security as ExcludeHiddenWhenZero was requested and NO BALANCE FOUND IN DATE RANGE PERIOD.." %(sec))
                            continue

                    if displayDataChoice.isOnlyWithinBalanceRange():

                        foundStart = False
                        for i in range(0, len(intervals)):
                            if yValues_balances[i] != 0:
                                foundStart = True
                                thisSecWithinBalBeginInterval = max(thisSecWithinBalBeginInterval, intervals[i])
                                break
                            yValues_balances[i] = None
                        if not foundStart:
                            myPrint("DB","%s: SKIPPING as not foundStart" %(sec))
                            continue

                        foundEnd = False
                        for i in reversed(range(0, len(intervals))):
                            if yValues_balances[i] != 0:
                                foundEnd = True
                                thisSecWithinBalEndInterval = min(thisSecWithinBalEndInterval, intervals[i])
                                break
                            yValues_balances[i] = None
                        if not foundEnd:
                            myPrint("DB","%s: SKIPPING as not foundEnd" %(sec))
                            continue

                        if thisSecWithinBalBeginInterval == thisSecWithinBalEndInterval:
                            myPrint("DB","%s: SKIPPING as thisSecWithinBalBeginInterval == thisSecWithinBalEndInterval" %(sec))
                            continue

                        # dates = MySecurityPerformanceGraph.getTxnDates(sec, beginDate, endDate)
                        # if dates.size() <= 1: continue
                        # Collections.sort(dates)
                        # thisSecWithinBalBeginDate = int(dates.get(0))
                        # thisSecWithinBalEndDate = int(dates.get(dates.size() - 1))

                    myPrint("DB", "thisSecPriceHistBeginDate: %s, thisSecPriceHistEndDate: %s, thisSecPriceHistBeginInterval: %s, thisSecPriceHistEndInterval: %s, thisSecWithinBalBeginInterval: %s, thisSecWithinBalEndInterval: %s"
                            %(thisSecPriceHistBeginDate, thisSecPriceHistEndDate, thisSecPriceHistBeginInterval, thisSecPriceHistEndInterval, thisSecWithinBalBeginInterval, thisSecWithinBalEndInterval))
                    del thisSecPriceHistBeginDate, thisSecPriceHistEndDate

                    # startPrice = None if rebaseChoice.isRebaseWithBalance() else CurrencyUtil.getSplitAdjustedRelativeUserPrice(sec, base, intervals[0])
                    startPrice = None

                    if rebaseChoice.isRebaseFromStart():
                        # Hunt for the start point - where price history starts (rather than the earliest start date for all securities)...
                        for i in range(0, len(intervals)):
                            if intervals[i] >= thisSecPriceHistBeginInterval:
                                startPrice = CurrencyUtil.getSplitAdjustedRelativeUserPrice(sec, base, intervals[i])
                                break
                        if startPrice is None: raise Exception("Error: could not find startPrice!?")
                        myPrint("DB", "startPrice (rebaseChoice.isRebaseFromStart()): %s" %(startPrice))

                    yValues_price = [None] * len(intervals)
                    yValues_price_unsplit = [None] * len(intervals)
                    yValues_percentagePerformance = [None] * len(intervals)

                    # yValues_value = [None] * len(intervals)
                    yValues_value_new = [None] * len(intervals)
                    yValues_valuePerformance = [None] * len(intervals)

                    for i in range(0, len(yValues_percentagePerformance)):
                        if ((displayDataChoice.isThroughoutWholeDateRange() and (intervals[i] >= thisSecPriceHistBeginInterval and intervals[i] <= thisSecPriceHistEndInterval)) or
                                (displayDataChoice.isOnlyWithinBalanceRange() and (intervals[i] >= thisSecWithinBalBeginInterval and intervals[i] <= thisSecWithinBalEndInterval))):
                            calcPrice = CurrencyUtil.getSplitAdjustedRelativeUserPrice(sec, base, intervals[i])
                            if startPrice is None:
                                startPrice = calcPrice
                                myPrint("DB", "startPrice (rebaseChoice.isRebaseWithBalance()): %s" %(startPrice))
                            yValues_percentagePerformance[i] = ((calcPrice - startPrice) / startPrice) * 100.0 * Math.pow(10, DECIMALS_PERCENTAGE)
                            yValues_price[i] = calcPrice

                            unSplitPrice = CurrencyUtil.getUserRate(sec, base, intervals[i])
                            yValues_price_unsplit[i] = unSplitPrice

                    minRate = None
                    maxRate = None
                    totalRate = 0.0
                    used = 0

                    myPrint("DB", "%s: yValues_price:" %(sec), yValues_price)
                    myPrint("DB", "%s: yValues_percentagePerformance:" %(sec), yValues_percentagePerformance)

                    myPrint("DB", "%s: yValues_price_unsplit:" %(sec), yValues_price_unsplit)

                    myPrint("DB", "%s: yValues_balances:" %(sec), yValues_balances)

                    valueCount = 0
                    for val in yValues_percentagePerformance:
                        if val is not None: valueCount += 1
                    if valueCount < 2:
                        myPrint("DB", "%s: SKIPPING as valueCount (x-axis graph points) < 2" %(sec))
                        continue
                    del valueCount

                    for i in range(0, len(yValues_percentagePerformance)):
                        if yValues_percentagePerformance[i] is not None:
                            # yValues_value[i] = (yValues_price[i] * yValues_balances[i])
                            yValues_value_new[i] = base.getDoubleValue(CurrencyTable.convertValue(sec.getLongValue(yValues_balances[i]), sec, base, intervals[i]))

                    # myPrint("DB", "%s: yValues_value:" %(sec), yValues_value)
                    myPrint("DB", "%s: yValues_value_new:" %(sec), yValues_value_new)
                    myPrint("DB", "%s: yValues_valuePerformance:" %(sec), yValues_valuePerformance)

                    for i in range(0, len(yValues_percentagePerformance)):
                        if yValues_percentagePerformance[i] is not None:
                            if percentageChoice.isPercentage():
                                tmpVal = yValues_percentagePerformance[i]
                            elif percentageChoice.isPrice():
                                # tmpVal =  yValues_price[i]
                                tmpVal =  yValues_price_unsplit[i]
                            elif percentageChoice.isBalance():
                                tmpVal =  yValues_balances[i]
                            elif percentageChoice.isValue():
                                # tmpVal =  yValues_value[i]
                                tmpVal =  yValues_value_new[i]
                            else: raise Exception("ERROR: percentage/price/balance/value choice invalid!")
                            totalRate += tmpVal
                            if minRate is None: minRate = tmpVal
                            if maxRate is None: maxRate = tmpVal
                            minRate = min(minRate, tmpVal)
                            maxRate = max(maxRate, tmpVal)
                            used += 1

                    myPrint("DB", "minRate: %s, maxRate: %s, totalRate: %s" %(minRate, maxRate, totalRate))
                    minBalStr = resources.getStr("graph_min") + " " + StringUtils.formatRate(minRate, dec)
                    maxBalStr = resources.getStr("graph_max") + " " + StringUtils.formatRate(maxRate, dec)
                    avgBalStr = resources.getStr("graph_avg") + " " + StringUtils.formatRate(totalRate / used, dec)

                    if graphData is None:
                        graphData = MyGraphSet(MySecurityPerformanceGraph.getTitle())    # type: MyGraphSet

                        graphOptions = "(graph options: "

                        graphOptions += "display: "
                        graphOptions += displayDataChoice.LABEL_WITHIN_BALANCE if displayDataChoice.isOnlyWithinBalanceRange() else displayDataChoice.LABEL_WHOLE_DATE_RANGE

                        if rebaseChoice.isEnabled():
                            graphOptions += ", "
                            graphOptions += "rebase: "
                            graphOptions += rebaseChoice.LABEL_REBASE_FROM_START if rebaseChoice.isRebaseFromStart() else rebaseChoice.LABEL_REBASE_WITH_SHARE_BALANCE

                        if not includeHiddenSecuritiesChoice.isIncludeHidden():
                            graphOptions += ", hidden securities: excluded"
                            if includeHiddenSecuritiesChoice.isExcludeHiddenWhenZero():
                                graphOptions += " when zero shares held throughout date range"
                        graphOptions += ")"

                        graphData.setShowLegend(True)
                        graphData.setYAxisLabel(percentageChoice.getYAxisLabel() + yAxisLabelText)
                        graphData.setXAxisLabel(None)
                        graphData.setShowKey(True)
                        graphData.setSubTitle(graphOptions)
                        graphData.setShouldShowTitle(False)

                    series = graphData.addTimeSeries(sec.getName(), [minBalStr, maxBalStr, avgBalStr], specialCT, None)  # type: TimeSeries

                    table_valueStart += thisSecurityTotalStartValue
                    table_valueEnd += thisSecurityTotalEndValue

                    for i in range(0, len(intervals)):
                        if yValues_price[i] is not None:            yValues_price[i]            *= Math.pow(10, DECIMALS_PRICE)
                        if yValues_price_unsplit[i] is not None:    yValues_price_unsplit[i]    *= Math.pow(10, DECIMALS_PRICE)
                        if yValues_balances[i] is not None:         yValues_balances[i]         *= Math.pow(10, DECIMALS_BALANCE)
                        # if yValues_value[i] is not None:          yValues_value[i]            *= Math.pow(10, DECIMALS_VALUE)
                        if yValues_value_new[i] is not None:        yValues_value_new[i]        *= Math.pow(10, DECIMALS_VALUE)

                    for i in range(0, len(intervals)):
                        if percentageChoice.isPercentage():
                            tmpVal = yValues_percentagePerformance[i]
                        elif percentageChoice.isPrice():
                            # tmpVal =  yValues_price[i]
                            tmpVal =  yValues_price_unsplit[i]
                        elif percentageChoice.isBalance():
                            tmpVal =  yValues_balances[i]
                        elif percentageChoice.isValue():
                            # tmpVal =  yValues_value[i]
                            tmpVal =  yValues_value_new[i]
                        else: raise Exception("ERROR: percentage/price/balance/value choice invalid!")

                        series.addOrUpdate(MySecurityPerformanceGraph.getIntervalObj(interval, intervals[i]), tmpVal)

                    if tableData is None: tableData = MySecurityPerformanceGraph.StorePopupTableData(base, dec)
                    tableData.storeSecurityRow(MySecurityPerformanceGraph.StoreSecurityRow(sec, thisSecurityTotalStartValue, thisSecurityTotalEndValue, secStartPrice, secEndPrice))

                del specialCT

            except:
                dump_sys_error_to_md_console_and_errorlog()
                raise

            if tableData is not None:
                tableData.startDate = beginDate
                tableData.endDate = endDate
                tableData.portfolioStartValue = table_valueStart
                tableData.portfolioEndValue = table_valueEnd
                if table_valueEnd == 0 or table_valueStart == 0:
                    tableData.portfolioValueChange = 0.0
                else:
                    tableData.portfolioValueChange = (float(table_valueEnd) - float(table_valueStart)) / float(table_valueStart)

            if graphData is not None: graphData.setPopupTableData(tableData)

            return graphData

        # def ensureFullXAxis(self, graphData, firstUsedInterval, lastUsedInterval):
        #     #type: (MyGraphSet, CurrencyType, int, int) -> None
        #
        #     graphData.addTimeSeries("", [0], None, None)
        #     graphData.addTimeData(self.getIntervalObj(self.interval, self.intervals[firstUsedInterval]), 0.0)
        #     graphData.addTimeData(self.getIntervalObj(self.interval, self.intervals[lastUsedInterval]), 0.0)


        @staticmethod
        def getSnapshotDates(securities, begin, end, _key, allDatesSelected=None):
            # type: ([CurrencyType], int, int, str, bool) -> {CurrencyType: [int]}

            # note: snapshots are already sorted via a TreeSet with comparator on date.
            #       HENCE... The order is guaranteed to be oldest to newest

            class SnapShotComparator(Comparator):
                def compare(self, o1, o2):
                    # type: (int, int) -> int
                    return (o1 - o2)

            snapshotComparator = SnapShotComparator()

            lGetOverallDates = (_key is not None)
            lGetDatesBySecurity = not lGetOverallDates

            datesBySecurity = {}

            today = recalcBeginDate = recalcEndDate = DateUtil.getStrippedDateInt()

            if lGetOverallDates:
                datesBySecurity[_key] = TreeSet(snapshotComparator)   # Note: single thread, so no need for: SortedSet s = Collections.synchronizedSortedSet(new TreeSet(...));

            for sec in securities:
                snaps = sec.getSnapshots()    # type: [CurrencySnapshot]

                if lGetOverallDates:
                    if snaps.size() > 0:
                        recalcBeginDate = min(recalcBeginDate, snaps[0].getDateInt()) if (allDatesSelected) else begin
                        recalcEndDate = max(recalcEndDate, snaps[-1].getDateInt())
                        myPrint("DB","*** Sec: %s earliest snap: %s, latest snap: %s" %(sec, snaps[0].getDateInt(), snaps[-1].getDateInt()))

                if lGetDatesBySecurity:
                    datesBySecurity[sec] = TreeSet(snapshotComparator)

                    # search forwards (oldest to newest)
                    newestPriorDate = None  # Save this so we know if a earlier price exists (rather than any of the .getSnapshotForDate() etc methods)
                    for i in range(0, snaps.size()):
                        snap = snaps[i]
                        if snap.getRate() == 0.0: continue
                        snapDate = snap.getDateInt()
                        if snapDate < begin:
                            newestPriorDate = snapDate if (newestPriorDate is None) else max(newestPriorDate, snapDate)
                        if snapDate >= begin and snapDate <= end:
                            datesBySecurity[sec].add(Integer.valueOf(snapDate))
                            break
                    if newestPriorDate is not None:
                        datesBySecurity[sec].add(Integer.valueOf(newestPriorDate))  # TreeSet so will be in correct date order

                    # search backwards (newest to oldest)
                    foundEndDateWithinRange = False
                    for i in reversed(range(0, snaps.size())):
                        snap = snaps[i]
                        if snap.getRate() == 0.0: continue
                        snapDate = snap.getDateInt()
                        if snapDate >= begin and snapDate <= end:
                            datesBySecurity[sec].add(Integer.valueOf(snapDate))
                            foundEndDateWithinRange = True
                            break
                    if foundEndDateWithinRange:
                        datesBySecurity[sec].add(Integer.valueOf(today))  # If we found a begin date, then we should always run to today

            if lGetOverallDates:
                if recalcBeginDate >= today or recalcBeginDate >= recalcEndDate or recalcEndDate <= recalcBeginDate:
                    myPrint("B", "** No price history found to (re)calculate overall price history date range... [Start: %s End: %s]"
                            %(convertStrippedIntDateFormattedText(recalcBeginDate), convertStrippedIntDateFormattedText(recalcEndDate)))
                else:
                    myPrint("B", "** (Re)calculated dates to range where price history exists = [Start: %s End: %s]"
                            %(convertStrippedIntDateFormattedText(recalcBeginDate), convertStrippedIntDateFormattedText(recalcEndDate)))
                    datesBySecurity[_key].add(Integer.valueOf(recalcBeginDate))
                    datesBySecurity[_key].add(Integer.valueOf(recalcEndDate))

            return datesBySecurity

        # @staticmethod
        # def getTxnDates(theSecurity, begin, end):
        #     # type: (CurrencyType, int, int) -> [int]
        #
        #     dates = ArrayList()
        #
        #     _book = MySecurityPerformanceGraph.moneydanceContext.getCurrentAccountBook()
        #     tset = _book.getTransactionSet().getTransactions(MyTxnSearchFilter(theSecurity, begin, end))
        #     for txn in tset:
        #         date = txn.getDateInt()
        #         if date >= begin and date <= end:
        #             dates.add(Integer.valueOf(date))
        #     Collections.sort(dates)
        #
        #     i = 1
        #     while (i < dates.size()):
        #         if dates.get(i - 1) == dates.get(i):
        #             dates.remove(i)
        #             i -= 1
        #         i += 1
        #     return dates

        @staticmethod
        def sortLongArray(array):
            # type: ([int]) -> None
            MySecurityPerformanceGraph.quicksortAscending(array, 0, array.size() - 1)

        @staticmethod
        def quicksortAscending(array, first, last):
            # type: ([int], int, int) -> None
            if first < last:
                piv_index = MySecurityPerformanceGraph.partitionAscending(array, first, last)
                MySecurityPerformanceGraph.quicksortAscending(array, first, piv_index - 1)
                MySecurityPerformanceGraph.quicksortAscending(array, piv_index, last)

        @staticmethod
        def partitionAscending(array, first, last):
            # type: ([int], int, int) -> int
            pivot = int(array.get((first + last) / 2))
            while (first <= last):
                while (int(array.get(first)) < pivot):
                    first += 1
                while (int(array.get(last)) > pivot):
                    last -= 1
                if first <= last:
                    temp = int(array.get(first))
                    array.set(first, array.get(last))
                    array.set(last, Integer.valueOf(temp))
                    first += 1
                    last -= 1
            return first

        def goneAway(self):
            # type: () -> None
            super(self.__class__, self).goneAway()                                                                      # noqa

    # copies com.moneydance.apps.md.view.gui.reporttool.BuildOneReportWindow
    class MyGraphDialog(SecondaryDialog, ActionListener, OKButtonListener):
        def __init__(self, mdGUI, moduleID, theGenerator, theShowGraphWindowObj):
            # type: (MoneydanceGUI, str, GraphReportGenerator, MyShowGraphWindow) -> None

            self.mdGUI = mdGUI
            self.myModuleID = moduleID
            self.theGenerator = theGenerator
            self.theShowGraphWindowObj = theShowGraphWindowObj

            lModal = True

            super(self.__class__, self).__init__(mdGUI, theShowGraphWindowObj.getFrame(), theGenerator.getName(), lModal)

            p = JPanel(BorderLayout())
            p.setBorder(EmptyBorder(8, 10, 8, 10))
            self.settingsPanel = JPanel(BorderLayout())
            self.settingsPanel.add(self.theGenerator.getConfigPanel(False), BorderLayout.CENTER)
            self.settingsPanel.setBorder(EmptyBorder(0, 0, 8, 0))
            p.add(self.settingsPanel, BorderLayout.CENTER)
            buttonPanel = OKButtonPanel(mdGUI, self, 3)
            resetButton = JButton(mdGUI.getStr("reset"))
            resetButton.addActionListener(self)
            buttonPanel.setExtraButtons([resetButton])
            p.add(buttonPanel, BorderLayout.SOUTH)
            self.setContentPane(p)
            self.setRememberSizeLocationKeys("gui.%s_params_size" %(self.myModuleID), "gui.%s_params_location" %(self.myModuleID), Dimension(800, 800))
            try: self.setEscapeKeyCancels(True)
            except: pass
            self.setUsesDataFile(True)

        def actionPerformed(self, event):
            if isinstance(event, ActionEvent): pass
            self.doReset(self.theGenerator, self.settingsPanel, None)

        def doReset(self, generator, settingsPanel, layout):
            # type: (GraphReportGenerator, JPanel, JCheckBox) -> None
            generator.setParameters(None)
            settingsPanel.validate()
            if layout is not None: layout.setSelected(generator.isLandscape())

        def getWindowName(self): return self.theGenerator.getName()+"_config"

        def goneAway(self):
            self.theGenerator.goneAway()

        def goAwayNow(self):
            super(self.__class__, self).goAwayNow()

        def goAway(self):
            super(self.__class__, self).goAway()

        def buttonPressed(self, answerCode):
            # type: (int) -> None

            if answerCode == OKButtonPanel.ANSWER_OK:
                graphData = self.buildReport()

                if graphData is not None:
                    repParams = self.theGenerator.getInfo().getReportParameters()
                    GlobalVars.extn_param_graph_params_SPG = repParams.writeToString()
                    save_StuWareSoftSystems_parameters_to_file(myFile="%s_extension.dict" %(self.myModuleID))
                    myPrint("DB","Graph parameters encoded to string and saved to pickle file: '%s'" %(GlobalVars.extn_param_graph_params_SPG))
                    self.goAwayNow()

            elif answerCode == OKButtonPanel.ANSWER_CANCEL:
                self.goAwayNow()

        def buildReport(self):
            # type: () -> MyGraphSet

            graphData = self.theGenerator.generate()
            self.theShowGraphWindowObj.setGraph(graphData)
            return graphData

    # copies com.moneydance.apps.md.view.gui.reporttool.BuildOneReportWindow
    class MyPopupTableDialog(SecondaryDialog):
        def __init__(self, mdGUI, moduleID, theGenerator, theShowGraphWindowObj, theData):
            # type: (MoneydanceGUI, str, GraphReportGenerator, MyShowGraphWindow, MySecurityPerformanceGraph.StorePopupTableData) -> None

            self.mdGUI = mdGUI
            self.myModuleID = moduleID
            self.theGenerator = theGenerator
            self.theShowGraphWindowObj = theShowGraphWindowObj


            tableHeadings = theData.HEADINGS
            tableData = theData.generateTableData()
            tableStartDate = theData.startDate
            tableEndDate = theData.endDate
            tablePortfolioStartValue = theData.getPortfolioStartValueFancy()
            tablePortfolioEndValue = theData.getPortfolioEndValueFancy()
            tablePortfolioValueChange = theData.portfolioValueChange

            if debug: theData.dumpSelf()

            if debug: myPrint("DB", "** tableData:", tableData, "(%s)" %(type(tableData)))
            theJTable = MyJTable(self.mdGUI, self.mdGUI.getMain(), 6, MyDefaultTableModel(tableData, tableHeadings))

            lModal = False

            super(self.__class__, self).__init__(mdGUI, theShowGraphWindowObj.getFrame(), theGenerator.getName(), lModal)

            p = JPanel(BorderLayout())
            p.setBorder(EmptyBorder(8, 10, 8, 10))
            self.tablePanel = JPanel(BorderLayout())

            sp = JScrollPane(JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED, JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED)
            # sp.setBorder(CompoundBorder(MatteBorder(1, 1, 1, 1, mdGUI.getColors().hudBorderColor), EmptyBorder(0, 0, 0, 0)))
            # scrollpane.setPreferredSize(Dimension(frame_width-20, frame_height-20	))
            # theJTable.setPreferredScrollableViewportSize(Dimension(frame_width-20, frame_height-100))
            # theJTable.setAutoResizeMode(JTable.AUTO_RESIZE_OFF)
            sp.setViewportView(theJTable)

            self.tablePanel.add(sp, BorderLayout.CENTER)
            self.tablePanel.setBorder(EmptyBorder(0, 0, 8, 0))
            p.add(self.tablePanel, BorderLayout.CENTER)

            footerPnl = JPanel(GridBagLayout())
            footerPnl.setBorder(EmptyBorder(10, 10, 10, 10))
            x = 0
            y = 0
            footerPnl.add(JLabel("Start: %s" %(convertStrippedIntDateFormattedText(tableStartDate))),
                          AwtUtil.getConstraints(x, y, 0.0, 0.0, 1, 1, True, True));                   x += 1
            footerPnl.add(Box.createHorizontalStrut(20),
                          AwtUtil.getConstraints(x, y, 0.0, 0.0, 1, 1, True, True)); x += 1
            footerPnl.add(JLabel("End: %s" %(convertStrippedIntDateFormattedText(tableEndDate))),
                          AwtUtil.getConstraints(x, y, 0.0, 0.0, 1, 1, True, True));                   x += 1
            # footerPnl.add(Box.createHorizontalStrut(20),
            #               AwtUtil.getConstraints(x, y, 0.0, 0.0, 1, 1, True, True)); x += 1
            x = 0
            y += 1
            footerPnl.add(JLabel("Total start value: %s" %(tablePortfolioStartValue)),
                          AwtUtil.getConstraints(x, y, 0.0, 0.0, 1, 1, True, True));                   x += 1
            footerPnl.add(Box.createHorizontalStrut(20),
                          AwtUtil.getConstraints(x, y, 0.0, 0.0, 1, 1, True, True)); x += 1
            footerPnl.add(JLabel("Total end value: %s" %(tablePortfolioEndValue)),
                          AwtUtil.getConstraints(x, y, 0.0, 0.0, 1, 1, True, True));                   x += 1
            footerPnl.add(Box.createHorizontalStrut(20),
                          AwtUtil.getConstraints(x, y, 0.0, 0.0, 1, 1, True, True)); x += 1
            footerPnl.add(JLabel(wrap_HTML_text_then_Percent("Change%: ", tablePortfolioValueChange)),
                          AwtUtil.getConstraints(x, y, 0.0, 0.0, 1, 1, True, True));                   x += 1
            # footerPnl.add(Box.createHorizontalStrut(20), AwtUtil.getConstraints(x, 0, 1.0, 0.0, 1, 1, True, True)); x += 1
            p.add(footerPnl, BorderLayout.SOUTH)

            self.setContentPane(p)
            self.setRememberSizeLocationKeys("gui.%s_popup_table_size" %(self.myModuleID), "gui.%s_popup_table_location" %(self.myModuleID), Dimension(800, 800))
            try: self.setEscapeKeyCancels(True)
            except: pass
            self.setUsesDataFile(True)

        def getWindowName(self): return self.theGenerator.getName()+"_popup_table"

        def goingAway(self):
            return True

        def goneAway(self):
            super(self.__class__, self).goneAway()

        def goAwayNow(self):
            super(self.__class__, self).goAwayNow()

        def goAway(self):
            super(self.__class__, self).goAway()


    def terminate_script(_theFrame):
        myPrint("DB","In ", inspect.currentframe().f_code.co_name, "()")

        # also do this here to save JTable column widths
        try:
            save_StuWareSoftSystems_parameters_to_file()
        except:
            myPrint("B", "Error - failed to save parameters to pickle file...!")
            dump_sys_error_to_md_console_and_errorlog()

        try:
            # NOTE - .dispose() - The windowClosed event should set .isActiveInMoneydance False and .removeAppEventListener()
            if not SwingUtilities.isEventDispatchThread():
                SwingUtilities.invokeLater(GenericDisposeRunnable(_theFrame))
            else:
                _theFrame.dispose()
        except:
            myPrint("B","Error. Final dispose failed....?")
            dump_sys_error_to_md_console_and_errorlog()

    class MyMoneydanceEventListener(AppEventListener):

        def __init__(self, theFrame, moneydanceContext):
            self.alreadyClosed = False
            self.theFrame = theFrame
            self.myModuleID = myModuleID
            self.moneydanceContext = moneydanceContext

        def getMyself(self):
            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")
            fm = self.moneydanceContext.getModuleForID(self.myModuleID)
            if fm is None: return None, None
            try:
                pyObject = getFieldByReflection(fm, "extensionObject")
            except:
                myPrint("DB","Error retrieving my own Python extension object..?")
                dump_sys_error_to_md_console_and_errorlog()
                return None, None

            return fm, pyObject

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
            # if (fm is None or pyObject is None) and appEvent != "md:app:exiting":
            if (fm is None or (self.theFrame.isRunTimeExtension and pyObject is None)) and appEvent != "md:app:exiting":
                myPrint("B", "@@ ALERT - I've detected that I'm no longer installed as an extension - I will deactivate.. (switching event code to :close)")
                appEvent = "%s:customevent:close" %self.myModuleID

            # I am only closing Extension when a new Dataset is opened.. I was calling it on MD Close/Exit, but it seemed to cause an Exception...
            if (appEvent == "md:file:closing"
                    or appEvent == "md:file:closed"
                    or appEvent == "md:file:opening"
                    or appEvent == "md:app:exiting"):
                myPrint("DB","@@ Ignoring MD handleEvent: %s" %(appEvent))

            elif (appEvent == "md:file:opened" or appEvent == "%s:customevent:close" %self.myModuleID):
                if debug:
                    myPrint("DB","MD event %s triggered.... Will call GenericWindowClosingRunnable (via the Swing EDT) to push a WINDOW_CLOSING Event to %s to close itself (while I exit back to MD quickly) ...." %(appEvent, self.myModuleID))
                else:
                    myPrint("B","Moneydance triggered event %s triggered - So I am closing %s now...." %(appEvent, self.myModuleID))
                self.alreadyClosed = True
                try:
                    SwingUtilities.invokeLater(GenericWindowClosingRunnable(self.theFrame))
                    myPrint("DB","Back from calling GenericWindowClosingRunnable to push a WINDOW_CLOSING Event (via the Swing EDT) to %s.... ;-> ** I'm getting out quick! **" %(self.myModuleID))
                except:
                    dump_sys_error_to_md_console_and_errorlog()
                    myPrint("B","@@ ERROR calling GenericWindowClosingRunnable to push  a WINDOW_CLOSING Event (via the Swing EDT) to %s.... :-< ** I'm getting out quick! **" %(self.myModuleID))
                if not debug: myPrint("DB","Returning back to Moneydance after calling for %s to close...." %self.myModuleID)

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

    class MyDefaultTableModel(DefaultTableModel):
        def __init__(self, *args):
            super(self.__class__, self).__init__(*args)

        def getColumnClass(self, columnIndex):

            val = self.getValueAt(0, columnIndex)
            if isinstance(val, (int)): return Integer.TYPE
            if isinstance(val, (long)): return Long.TYPE
            if isinstance(val, (float)): return Double.TYPE
            if isinstance(val, (str, unicode)): return String

            return self.getValueAt(0, columnIndex).getClass()

    class HeaderRenderer(TableCellRenderer):

        def __init__(self, table):
            super(self.__class__, self).__init__()
            self.renderer = table.getTableHeader().getDefaultRenderer()
            self.renderer.setHorizontalAlignment(JLabel.RIGHT)          # This one changes the text alignment
            self.renderer.setVerticalAlignment(JLabel.BOTTOM)

        def getTableCellRendererComponent(self, table, value, isSelected, hasFocus, row, col):
            if col == 0:
                self.renderer.setHorizontalAlignment(JLabel.LEFT)
            else:
                self.renderer.setHorizontalAlignment(JLabel.RIGHT)
            return self.renderer.getTableCellRendererComponent(table, value, isSelected, hasFocus, row, col)


    class MyTableColumnModelListener(TableColumnModelListener):
        ## noinspection PyUnusedLocal

        def columnMarginChanged(self, e):
            # super(self.__class__, self).columnMarginChanged(e)
            columnModel = e.getSource()

            if len(GlobalVars.extn_param_column_widths_SPG) != columnModel.getColumnCount():
                GlobalVars.extn_param_column_widths_SPG = [None] * columnModel.getColumnCount()

            for i in range(0, columnModel.getColumnCount()):
                colWidth = columnModel.getColumn(i).getWidth()
                GlobalVars.extn_param_column_widths_SPG[i] = colWidth
                # myPrint("DB","Saving column %s as width %s for later..." %(i, colWidth))

        def columnMoved(self, e): pass
        def columnAdded(self, e): pass
        def columnRemoved(self, e): pass
        def columnSelectionChanged(self, e): pass

    class LongComparator(Comparator):
        def compare(self, o1, o2): return Long.compare(Long(o1), Long(o2))

    class IntegerComparator(Comparator):
        def compare(self, o1, o2): return Integer.compare(Integer(o1), Integer(o2))

    class DoubleComparator(Comparator):
        def compare(self, o1, o2): return Double.compare(Double(o1), Double(o2))

    class MyTableRowSorter(TableRowSorter):

        def __init__(self): super(self.__class__, self).__init__()

        def getComparator(self, column):
            columnClass = self.getModel().getColumnClass(column)                                                        # noqa
            if columnClass == Integer.TYPE: return IntegerComparator()
            if columnClass == Long.TYPE: return LongComparator()
            if columnClass == Double.TYPE: return DoubleComparator()
            return super(self.__class__, self).getComparator(column)

    class MyJTable(JTable):
        def __init__(self, mdGUI, moneydanceContext, sortByColumIndex, tableModel):
            super(self.__class__, self).__init__(tableModel)
            self.mdGUI = mdGUI
            self.moneydanceContext = moneydanceContext
            self.tableModel = tableModel

            sorter = MyTableRowSorter()
            sorter.setModel(self.getModel())
            sortKeys = ArrayList()
            sortKeys.add(RowSorter.SortKey(sortByColumIndex, SortOrder.DESCENDING))                                     # noqa
            sorter.setSortKeys(sortKeys)
            self.setRowSorter(sorter)

            # self.setAutoCreateRowSorter(True)
            # self.getTableHeader().setDefaultRenderer(DefaultTableHeaderCellRenderer())
            self.getTableHeader().setDefaultRenderer(HeaderRenderer(self))

            self.validateLoadSavedColumnWidths()
            self.getColumnModel().addColumnModelListener(MyTableColumnModelListener())

        def validateLoadSavedColumnWidths(self):
            tcm = self.getColumnModel()
            validCount = 0
            lInvalidate = True
            if (GlobalVars.extn_param_column_widths_SPG is not None
                    and isinstance(GlobalVars.extn_param_column_widths_SPG,(list))
                    and len(GlobalVars.extn_param_column_widths_SPG) == tcm.getColumnCount()):
                for width in GlobalVars.extn_param_column_widths_SPG:
                    if isinstance(width, (int)) and width >= 0 and width <= 1000:																	# noqa
                        validCount += 1

            if validCount == len(MySecurityPerformanceGraph.StorePopupTableData.HEADINGS):
                lInvalidate = False

            if lInvalidate:
                myPrint("DB","Found invalid saved columns = resetting to defaults")
                myPrint("DB","Found: %s" %(GlobalVars.extn_param_column_widths_SPG))
                myPrint("DB","Resetting to: %s" %([]))
                GlobalVars.extn_param_column_widths_SPG = []
                tcm.getColumn(0).setPreferredWidth(250)

            else:
                myPrint("DB","Restoring valid column widths loaded: %s" %(GlobalVars.extn_param_column_widths_SPG))
                for i in range(0, tcm.getColumnCount()):
                    tcm.getColumn(i).setPreferredWidth(GlobalVars.extn_param_column_widths_SPG[i])
                self.setAutoResizeMode(JTable.AUTO_RESIZE_OFF)


        def isCellEditable(self, row, column): return False                                                             # noqa

        # noinspection PyUnusedLocal
        def getCellRenderer(self, row, column):                                                                         # noqa
            renderer = None

            val = self.getValueAt(row, column)

            if isinstance(val, (str, unicode)) or MySecurityPerformanceGraph.StorePopupTableData.FORMATS[column] == "str":
                renderer = DefaultTableCellRenderer()
                renderer.setHorizontalAlignment(JLabel.LEFT)

            elif isinstance(val, (CurrencyType)):
                renderer = DefaultTableCellRenderer()
                renderer.setHorizontalAlignment(JLabel.LEFT)

            elif isinstance(val, (float)) and MySecurityPerformanceGraph.StorePopupTableData.FORMATS[column] == "pct":
                renderer = self.MyPercentRenderer(self)
                renderer.setHorizontalAlignment(JLabel.RIGHT)

            elif isinstance(val, (float)) and MySecurityPerformanceGraph.StorePopupTableData.FORMATS[column] == "price":
                renderer = self.MyPriceRenderer(self)
                renderer.setHorizontalAlignment(JLabel.RIGHT)

            elif isinstance(val, (int, long)) or MySecurityPerformanceGraph.StorePopupTableData.FORMATS[column] == "val_long":
                renderer = self.MyIntLongRenderer(self)
                renderer.setHorizontalAlignment(JLabel.RIGHT)

            else:
                renderer = DefaultTableCellRenderer()
                renderer.setVerticalAlignment(JLabel.CENTER)

            return renderer

        class MyIntLongRenderer(DefaultTableCellRenderer):

            def __init__(self, callingClass):
                super(self.__class__, self).__init__()
                self.callingClass = callingClass
                self.base = self.callingClass.moneydanceContext.getCurrentAccount().getBook().getCurrencies().getBaseType()
                self.dec = self.callingClass.moneydanceContext.getPreferences().getDecimalChar()

            def setValue(self, value):
                if value is None: return
                self.setText(self.base.formatFancy(value, self.dec))
                if value < 0.0:
                    self.setForeground(self.callingClass.mdGUI.getColors().budgetAlertColor)
                else:
                    self.setForeground(self.callingClass.mdGUI.getColors().defaultTextForeground)

        class MyPriceRenderer(DefaultTableCellRenderer):

            def __init__(self, callingClass):
                super(self.__class__, self).__init__()
                self.callingClass = callingClass
                self.base = self.callingClass.moneydanceContext.getCurrentAccount().getBook().getCurrencies().getBaseType()
                self.dec = self.callingClass.moneydanceContext.getPreferences().getDecimalChar()

            def setValue(self, value):
                if value is None: return
                self.setText("{:.4f}".format(value))

        class MyPercentRenderer(DefaultTableCellRenderer):

            def __init__(self, callingClass):
                super(self.__class__, self).__init__()
                self.callingClass = callingClass
                self.base = self.callingClass.moneydanceContext.getCurrentAccount().getBook().getCurrencies().getBaseType()
                self.dec = self.callingClass.moneydanceContext.getPreferences().getDecimalChar()

            def setValue(self, value):
                if value is None: return
                self.setText("{:.2%}".format(value))
                if value < 0.0:
                    self.setForeground(self.callingClass.mdGUI.getColors().budgetAlertColor)
                else:
                    self.setForeground(self.callingClass.mdGUI.getColors().defaultTextForeground)

        def prepareRenderer(self, renderer, row, column):                                                               # noqa
            # make Banded rows
            component = super(self.__class__, self).prepareRenderer(renderer, row, column)                              # noqa
            if not self.isRowSelected(row):
                component.setBackground(self.mdGUI.getColors().registerBG1 if row % 2 == 0 else self.mdGUI.getColors().registerBG2)
            else:
                component.setForeground(self.mdGUI.getColors().sidebarSelectedFG)

            renderer.setBorder(BorderFactory.createEmptyBorder(0, 0, 0, 5))

            return component

    # class MyGraphViewer(GraphViewer):       # copies: com.moneydance.apps.md.view.gui.graphtool.GraphViewer
    class MyGraphViewer(JPanel, MDPrintable):       # copies: com.moneydance.apps.md.view.gui.graphtool.GraphViewer

        # Extending GraphViewer (which is a bit of a fudge) so that the GraphReportUtil methods accept 'viewer'
        # otherwise just use class MyGraphViewer(JPanel, MDPrintable):

        circleShape = Ellipse2D.Float(-2.5, -2.5, 5.0, 5.0)                                                             # noqa

        class GraphLayoutManager(LayoutManager):
            def __init__(self, callingClass, *args):                                                                    # noqa
                self.callingClass = callingClass

            def addLayoutComponent(self, *args): pass

            def layoutContainer(self, container):
                sz = container.getSize()
                insets = container.getInsets()
                usableWidth = int(sz.width - insets.left + insets.right)
                usableHeight = int(sz.height - insets.top + insets.bottom)

                if self.callingClass.mainChartPanel is not None:
                    self.callingClass.mainChartPanel.setBounds(insets.left, insets.top, usableWidth, usableHeight)

            def minimumLayoutSize(self, container): return Dimension(20, 20)                                            # noqa
            def preferredLayoutSize(self, container): return Dimension(500, 450)                                        # noqa
            def removeLayoutComponent(self, *args): pass

        class TimeSeriesToolTipGenerator(StandardXYToolTipGenerator):
            def __init__(self, callingClass, *args):
                self.callingClass = callingClass
                super(self.__class__, self).__init__(*args)                                                             # noqa

            def generateToolTip(self, dataset, series, item):
                if isinstance(dataset, AbstractSeriesDataset):
                    asData = dataset                                            # type: AbstractSeriesDataset
                    key = asData.getSeriesKey(series)                           # type: Comparable
                    lgs = self.callingClass.getGraphSet().getDetailsByName(String.valueOf(key))
                    if lgs is None: return None
                    sb = StringBuilder()
                    sb.append(lgs.name)
                    if isinstance(dataset, TimeSeriesCollection):
                        timeSeries = dataset.getSeries(series)
                        regularTimePeriod = timeSeries.getTimePeriod(item)      # type: RegularTimePeriod
                        if regularTimePeriod is not None:
                            sb.append("; ")
                            sb.append(regularTimePeriod)
                    if isinstance(dataset, TimeTableXYDataset):
                        timeInMs = dataset.getX(series, item)
                        if timeInMs is not None:
                            sb.append("; ")
                            sb.append(self.callingClass.dateFormat.format(Date(timeInMs.longValue())))
                    sb.append("; ")
                    currency = lgs.currency                                     # type: CurrencyType
                    if currency is not None:
                        extraTxt = currency.getParameter(MySecurityPerformanceGraph.CURRENCY_LABEL_KEY, "")
                        sb.append(extraTxt + " " + currency.formatFancy(Math.round(dataset.getYValue(series, item)), self.callingClass.dec))
                    else:
                        sb.append(self.callingClass.rateFormat.format(dataset.getYValue(series, item)))
                    return sb.toString()

                return super(self.__class__, self).generateToolTip(dataset, series, item)                               # noqa

        class CurrencyNumberFormat(NumberFormat):

            def __init__(self, curr, callingClass):
                # type: (CurrencyType, MyGraphViewer) -> None
                self.curr = curr
                self.callingClass = callingClass

            # noinspection PyUnusedLocal
            def parse(self, text, pos):
                return Long(self.curr.parse(text, self.callingClass.this.dec))

            # noinspection PyUnusedLocal
            def format(self, number, toAppendTo, pos):
                # type: ((long, float), StringBuffer, FieldPosition) -> StringBuffer
                if toAppendTo is None:
                    toAppendTo = StringBuffer()
                if isinstance(number, long):
                    toAppendTo.append(self.curr.formatFancy(number, self.callingClass.dec))
                    # toAppendTo.append(self.curr.formatSemiFancy(number, self.callingClass.dec))
                elif isinstance(number, float):
                    toAppendTo.append(self.curr.formatFancy(Math.round(number), self.callingClass.dec))
                    # toAppendTo.append(self.curr.formatSemiFancy(Math.round(number), self.callingClass.dec))
                else:
                    raise Exception("CHECK DATA TYPES")
                return toAppendTo

        def __init__(self, mdGUI):
            # super(self.__class__, self).__init__(mdGUI)

            self.paintBounds = Rectangle(0, 0, 0, 0)

            self.mdGUI = mdGUI

            self.mainChart = None           # type: JFreeChart
            self.mainChartPanel = None      # type: ChartPanel
            self.graphSet = None            # type: MyGraphSet

            self.dec = mdGUI.getPreferences().getDecimalChar()
            self.dateFormat = mdGUI.getPreferences().getShortDateFormatter()
            self.colors = mdGUI.getColors()

            self.setLayout(self.GraphLayoutManager(self))
            self.setOpaque(True)
            self.setBackground((mdGUI.getColors()).defaultBackground)
            self.graphGridColor = GradientPaint(0.0, 0.0, self.colors.homePageBG, 0.0, 700.0, self.colors.homePageAltBG)
            self.rateFormat = DecimalFormat("#" + self.dec + "######")
            self.xyToolTipGenerator = self.TimeSeriesToolTipGenerator(self)

        def setGraph(self, graphSet):
            # type: (MyGraphSet) -> None
            self.graphSet = graphSet

            overrideFormatString = graphSet.getRateFormatString(self.dec)
            if overrideFormatString is not None:
                self.rateFormat = DecimalFormat(overrideFormatString)

            self.removeAll()
            colorEnum = ColorEnumerator()
            stroke = BasicStroke(2.0, 1, 1)
            self.mainChart = None
            self.mainChartPanel = None
            mainModel = graphSet.getMainGraph()
            if mainModel is not None:
                showLegend = graphSet.getShowLegend()

                self.mainChart = ChartFactory.createTimeSeriesChart(None,
                                                                    graphSet.getXAxisLabel(),
                                                                    graphSet.getYAxisLabel(),
                                                                    mainModel,
                                                                    showLegend,
                                                                    True,
                                                                    False)

                # x Axis = Domain Axis
                # y Axis = Range Axis

                # review this for additional markers: com.moneydance.apps.md.view.gui.SecurityDetailPanel.createChart()

                plot = self.mainChart.getPlot()
                if isinstance(plot, XYPlot): pass

                # Fix the (domain) x-axis to prevent hours, minutes, seconds, milliseconds (etc) appearing
                newTickUnits = TickUnits()
                axis = plot.getDomainAxis()
                tus = axis.getStandardTickUnits()
                for i in range(0, tus.size()):                                                                          # noqa
                    stu = tus.get(i)                                                                                    # noqa
                    tusType = stu.getUnitType()
                    if tusType in [DateTickUnitType.DAY, DateTickUnitType.MONTH, DateTickUnitType.YEAR]:
                        newTickUnits.add(stu)
                axis.setStandardTickUnits(newTickUnits)


                # add axis labels
                if plot.getDomainAxis().getLabel() is not None:
                    plot.getDomainAxis().setLabelPaint(self.colors.defaultTextForeground)
                if plot.getRangeAxis().getLabel() is not None:
                    plot.getRangeAxis().setLabelPaint(self.colors.defaultTextForeground)


                # add title
                if graphSet.getShouldShowTitle() and graphSet.getTitle() is not None and len(graphSet.getTitle()) > 0:
                    titleTxt = TextTitle(graphSet.getTitle())
                    titleTxt.setPaint(self.colors.defaultTextForeground)
                    self.mainChart.setTitle(titleTxt)

                # add subtitle
                subTitle = graphSet.getSubTitle()
                if subTitle is not None and len(subTitle) > 0:
                    sub = TextTitle(subTitle)
                    sub.setPaint(self.colors.defaultTextForeground)
                    self.mainChart.addSubtitle(0, sub)

                self.mainChart.setBackgroundPaint(self.colors.defaultBackground)
                self.mainChart.setBackgroundImageAlpha(1.0)

                plot.setRangeZeroBaselineVisible(True)
                curr = graphSet.getCurrency()
                if mainModel.getSeriesCount() > 0:
                    mainKey = mainModel.getSeriesKey(0)
                    if curr is None and isinstance(mainKey, MyGraphSet.LineGraphSection):
                        curr = mainKey.currency
                    yAxis = plot.getRangeAxis()
                    if curr is not None and isinstance(yAxis, NumberAxis):
                        yAxis.setNumberFormatOverride(MyGraphViewer.CurrencyNumberFormat(curr, self))
                        yAxis.setAutoRangeIncludesZero(False)


                # Fix the y-axis min/max range (for some reason it chops when using Python version - internal MD version is OK
                # I think the problem is in here.. either dataformats or lack of java casting perhaps: org.jfree.chart.plot.XYPlot.getDataRange(ValueAxis)

                myPrint("DB", "Fixing plot range - was:", plot.getRangeAxis().getRange())

                lowerValue = upperValue = None
                for i in range(0, mainModel.getSeriesCount()):
                    s = mainModel.getSeries(i)
                    seriesItems = s.getItems()
                    for item in seriesItems:                # type: TimeSeriesDataItem
                        # myPrint("B",item.getPeriod(), item.getValue(), item.getPeriod().getStart(), item.getPeriod().getEnd())
                        val = item.getValue()
                        if lowerValue is None or upperValue is None: lowerValue = upperValue = val
                        if val is not None: lowerValue = min(lowerValue, val)
                        if val is not None: upperValue = max(upperValue, val)
                myPrint("DB","upper/lower values found:", lowerValue, upperValue)

                # lowerMult = upperMult = 1.0
                # if lowerValue < 0.0: lowerMult *= -1
                # if upperValue < 0.0: upperMult *= -1
                #
                # # lowerMargin = lowerValue - (lowerValue * (plot.getRangeAxis().getLowerMargin() * lowerMult))
                # # upperMargin = upperValue + (upperValue * (plot.getRangeAxis().getUpperMargin() * upperMult))
                #
                # lowerMargin = lowerValue - (lowerValue * (0.02 * lowerMult))
                # upperMargin = upperValue + (upperValue * (0.02 * upperMult))

                if lowerValue == 0.0 and upperValue == 0.0:
                    plot.getRangeAxis().setRange(-5.0E-9, 5.0E-9)
                else:
                    # plot.getRangeAxis().setRange(lowerMargin, upperMargin)
                    newRange = Range(lowerValue, upperValue)
                    plot.getRangeAxis().setRangeWithMargins(newRange)

                # vap = plot.getRangeAxis()
                # vap.setAutoRange(False)
                # vap.setAutoRange(True)
                # myPrint("B","** getDefaultAutoRange()", vap.getDefaultAutoRange());
                # myPrint("B","** vap.getDataRange(this)", plot.getDataRange(vap));

                myPrint("DB", "Plot range - now:", plot.getRangeAxis().getRange())


                mainColors = HashMap()
                existing = plot.getRenderer()

                if isinstance(existing, AbstractXYItemRenderer):
                    renderer = existing
                    renderer.setBaseToolTipGenerator(self.xyToolTipGenerator)
                    renderer.setBaseLegendTextPaint(self.colors.defaultTextForeground)
                    for i in range(mainModel.getSeriesCount()):
                        seriesPaint = colorEnum.nextColor()
                        renderer.setSeriesPaint(i, seriesPaint)
                        renderer.setSeriesStroke(i, stroke)
                        renderer.setSeriesShape(i, MyGraphViewer.circleShape)
                        mainColors.put(mainModel.getSeriesKey(i), seriesPaint)
                if isinstance(existing, XYLineAndShapeRenderer):
                    existing.setBaseShapesVisible(True)
                    existing.setBaseShapesFilled(True)

                plot.setDomainGridlinePaint(self.graphGridColor)
                plot.setRangeGridlinePaint(self.graphGridColor)
                plot.setOutlineVisible(False)
                plot.setBackgroundPaint(self.colors.graphBGGradient)
                plot.setBackgroundImageAlpha(0.0)
                plot.setDomainCrosshairVisible(True)
                plot.setRangeCrosshairVisible(True)
                plot.getDomainAxis().setTickLabelPaint(self.colors.defaultTextForeground)
                plot.getRangeAxis().setTickLabelPaint(self.colors.defaultTextForeground)
                domainAxis = plot.getDomainAxis()
                if isinstance(domainAxis, DateAxis):
                    axis = domainAxis
                    axis.setAxisLineVisible(False)
                self.mainChart.setPadding(RectangleInsets(0.0, 0.0, 0.0, 0.0))
                self.mainChart.setBorderVisible(False)
                if showLegend:
                    self.mainChart.getLegend().setBackgroundPaint(self.colors.defaultBackground)
                    self.mainChart.getLegend().setFrame(BlockBorder(self.colors.headerBorder))

                self.mainChartPanel = ChartPanel(self.mainChart, False)
                if isinstance(self.mainChartPanel, JPanel): pass
                self.mainChartPanel.setInitialDelay(0)
                self.mainChartPanel.setReshowDelay(0)
                self.mainChartPanel.setDismissDelay(Integer.MAX_VALUE)
                self.mainChartPanel.setMaximumDrawWidth(2048)
                self.mainChartPanel.setMaximumDrawHeight(1536)
                self.mainChartPanel.setMinimumDrawWidth(32)
                self.mainChartPanel.setMinimumDrawHeight(32)
                self.mainChartPanel.setMouseZoomable(True)
                self.mainChartPanel.setOpaque(False)
                self.mainChartPanel.setBackground(self.colors.homePageBG)

            if self.mainChartPanel is not None:
                self.add(self.mainChartPanel, GridC.getc(0, 1).wxy(1.0, 1.0).fillboth())

            self.validate()

        def getTitle(self): return self.getGraphSet().getTitle()

        def getGraphSet(self):
            # type: () ->  GraphSet
            return self.graphSet

        def getSettingsKey(self): return "graphs"

        def paintComponent(self, g):
            # type: (Graphics) -> None
            if isinstance(g, Graphics2D):
                g2 = g      # type: Graphics2D
                oldPaint = g2.getPaint()
                g2.setPaint(self.colors.graphBGGradient)
                g2.fill(self.getBounds(self.paintBounds))
                g2.setPaint(oldPaint)
            # super(self.__class__, self).paintComponent(g)

        def saveGraph(self, outStream):
            # type: (OutputStream) -> None
            img = self.getGraphAsImage()     # type: BufferedImage
            ChartUtilities.writeBufferedImageAsPNG(outStream, img)

        def getGraphAsImage(self):
            # type: (BufferedImage) ->  BufferedImage
            sz = self.getSize()
            img = BufferedImage(sz.width, sz.height, BufferedImage.TYPE_4BYTE_ABGR)
            graphics = img.getGraphics()
            graphics.setColor(self.colors.defaultBackground)
            graphics.fillRect(0, 0, sz.width, sz.height)
            self.renderGraphs(graphics, sz.width, sz.height)
            return img

        def usesWholePage(self): return False

        def isLandscape(self):  return True

        # noinspection PyUnusedLocal
        def printPage(self, g, pageNum, width, height, resolution):
            self.renderGraphs(g, int(width), int(height))
            return False

        def renderGraphs(self, g, w, h):
            # type: (Graphics, int, int) -> None
            try:
                fontSize = 10
                try:
                    prefs = self.mdGUI.getMain().getPreferences()
                    f = g.getFont()
                    fontName = prefs.getSetting("print.font_name", f.getName())
                    fontSize = prefs.getIntSetting("print.font_size", 10)
                    g.setFont(Font(fontName, 1, fontSize + 2))
                except Exception as e:
                    myPrint("B", "Warning: unable to set preferred font:", e)

                fm = g.getFontMetrics()
                lineHeight = int(fm.getMaxAscent() + fm.getMaxDescent() + 2)                                                # noqa
                headerFont = g.getFont().deriveFont(1, fontSize * 2.0)
                fmHeader = g.getFontMetrics(headerFont)
                hdrHeight = int(fmHeader.getMaxAscent() + fmHeader.getMaxDescent() + 2 + 2)
                g.setColor(self.colors.defaultTextForeground)
                currentX = 5
                if self.getGraphSet().getShouldPrintTitle():
                    strx = String.valueOf(self.getGraphSet().getTitle())
                    if not StringUtils.isBlank(strx):
                        bounds = fmHeader.getStringBounds(strx, g)
                        if bounds.getWidth() < w:
                            currentX = int((w - bounds.getWidth()) / 2.0)
                        currentY = int(hdrHeight - fmHeader.getMaxDescent())
                        oldHint = None
                        if isinstance(g, Graphics2D):
                            oldHint = g.getRenderingHint(RenderingHints.KEY_ANTIALIASING)
                            g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON)
                        oldFont = g.getFont()
                        g.setFont(headerFont)
                        g.drawString(strx, currentX, currentY)
                        g.setFont(oldFont)
                        if isinstance(g, Graphics2D):
                            g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, oldHint)
                gh = int(h - hdrHeight)
                self.mainChart.draw(g, Rectangle(int(0), int(hdrHeight), int(w), int(gh)))
            except Exception as e:
                self.mdGUI.showErrorMessage(self.mdGUI.getStr("save_graph_err") + ": ", e)
                dump_sys_error_to_md_console_and_errorlog()

        # @staticmethod
        # def addLegend(graphSet, plot, chart):
        #     # type: (GraphSet, PiePlot, JFreeChart) -> None
        #     BOB
        #     plot.setLabelGenerator(None)
        #     if graphSet.isVertical():
        #         columnArrangement = ColumnArrangement()                                                                 # noqa
        #         edge = RectangleEdge.BOTTOM
        #         flowArrangement = None
        #     else:
        #         flowArrangement = FlowArrangement()
        #         edge = RectangleEdge.RIGHT
        #     legend = LegendTitle(plot, flowArrangement, ColumnArrangement())
        #     legend.setMargin(0.0, 0.0, 0.0, 12.0)
        #     legend.setPadding(8.0, 12.0, 8.0, 12.0)
        #     legend.setFrame(LineBorder())
        #     legend.setItemLabelPadding(RectangleInsets(6.0, 6.0, 6.0, 6.0))
        #     legend.setPosition(edge)
        #     legend.setBackgroundPaint(None)
        #     sources = legend.getSources()
        #     copier = graphSet.getLegendCopier()
        #     if copier is not None and sources is not None:
        #         copier.copyFrom(sources[0])
        #         legend.setSources([copier])
        #     legend.addChangeListener(chart)
        #     chart.addLegend(legend)

    class MyGraphReportUtil(GraphReportUtil):       # Copies: com.moneydance.apps.md.view.gui.reporttool.GraphReportUtil

        class ImageSelection(Transferable, ClipboardOwner):
            def __init__(self, image):
                self.image = image

            def getTransferDataFlavors(self): return [DataFlavor.imageFlavor]
            def isDataFlavorSupported(self, flavor): return DataFlavor.imageFlavor.equals(flavor)

            def getTransferData(self, flavor):
                if not DataFlavor.imageFlavor.equals(flavor): raise UnsupportedFlavorException(flavor)
                return self.image

            # noinspection PyUnusedLocal
            def lostOwnership(self, clipboard, contents): self.image = None

        class PngFilenameFilter(FilenameFilter):
            # noinspection PyUnusedLocal
            def accept(self, dirname, filename): return (filename is not None and filename.upper().endswith(".PNG"))

        @staticmethod
        def getFileFromFileDialog(parentFrame, mdGUI):
            fwin = mdGUI.getFileChooser(parentFrame, mdGUI.getStr("choose_png_file"),
                                        FileDialog.SAVE,
                                        MyGraphReportUtil.PngFilenameFilter(),
                                        Arrays.asList(["gen.graph_dir", "gen.data_dir"]))
            fwin.setFile("MoneydanceGraph.png")
            fwin.setVisible(True)
            fileName = fwin.getFile()
            dirName = fwin.getDirectory()
            if fileName is None or dirName is None: return None
            if not mdGUI.getMain().getPlatformHelper().isConstrainedToSandbox() and not fileName.upper().endswith(".PNG"):
                fileName = fileName + ".png"
            return File(dirName, fileName)

        @staticmethod
        def printGraph(mdGUI, viewer):                                                                                  # noqa
            exec("MDPrinter.createPrinter(mdGUI).print(viewer, AwtUtil.getFrame(viewer))")

        @staticmethod
        def saveGraph(mdGUI, viewer):
            outputFile = MyGraphReportUtil.getFileFromFileDialog(AwtUtil.getFrame(viewer), mdGUI)
            if outputFile is None: return
            try:
                mdGUI.getPreferences().setSetting("gen.graph_dir", outputFile.getAbsolutePath())
                fout = FileOutputStream(outputFile)
                viewer.saveGraph(fout)
                fout.close()
            except Exception as e:
                mdGUI.showErrorMessage(mdGUI.getStr("err_save_graph" + ": ", e))
                dump_sys_error_to_md_console_and_errorlog()


        @staticmethod
        def copyGraph(mdGUI, viewer):                                                                                   # noqa
            image = viewer.getGraphAsImage()
            if image is not None:
                imageSelect = MyGraphReportUtil.ImageSelection(image)
                Toolkit.getDefaultToolkit().getSystemClipboard().setContents(imageSelect, imageSelect)

    class MyShowGraphWindow(PreferencesListener, ActionListener):
        def __init__(self, moneydanceContext, mdGUI, _moduleID, info):
            # type: (Main, MoneydanceGUI, str, ReportSpec) -> None

            self.moneydanceContext = moneydanceContext

            self.prefs = moneydanceContext.getPreferences()

            self.mdGUI = mdGUI
            self.moduleID = _moduleID
            self.info = info

            self.generator = None

            self.frame = MyJFrame(GlobalVars.Strings.GRAPH_NAME)
            self.frame.setName(u"%s_main" %(self.moduleID))

            self._defaultSize = Dimension(400, 300)
            self._saveSizeKey = None
            self._saveLocKey = None

            if float(self.moneydanceContext.getBuild()) >= 3051 and MD_EXTENSION_LOADER is not None:
                self.moneydanceExtensionLoader = MD_EXTENSION_LOADER  # This is the class loader for the whole extension
                myPrint("DB", "... Build is >= 3051 so using moneydance_extension_loader: %s" %(self.moneydanceExtensionLoader))
            else:
                self.moneydanceExtensionLoader = None

            if (not Platform.isOSX()):
                self.mdGUI.getImages()
                self.frame.setIconImage(MDImages.getImage(self.moneydanceContext.getSourceInformation().getIconResource()))

            self.frame.setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE)  # The CloseAction() and WindowListener() will handle dispose() - else change back to DISPOSE_ON_CLOSE

            shortcut = Toolkit.getDefaultToolkit().getMenuShortcutKeyMaskEx()

            # Add standard CMD-W keystrokes etc to close window
            self.frame.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_W, shortcut), "close-window")
            self.frame.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_F4, shortcut), "close-window")
            self.frame.getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(KeyStroke.getKeyStroke(KeyEvent.VK_W, shortcut), "close-window")
            self.frame.getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(KeyStroke.getKeyStroke(KeyEvent.VK_F4, shortcut), "close-window")
            self.frame.getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0), "close-window")
            self.frame.getRootPane().getActionMap().put("close-window", self.CloseAction(self.frame, self))

            self.frame.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_P, shortcut), "click-print")
            self.frame.getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(KeyStroke.getKeyStroke(KeyEvent.VK_P, shortcut), "click-print")
            self.frame.getRootPane().getActionMap().put("click-print", self.PrintAction(self.frame, self))

            self.frame.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_D, (shortcut | Event.SHIFT_MASK)), "enable-debug")
            self.frame.getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(KeyStroke.getKeyStroke(KeyEvent.VK_D, (shortcut | Event.SHIFT_MASK)), "enable-debug")
            self.frame.getRootPane().getActionMap().put("enable-debug", self.ToggleDebugAction(self))

            self.frame.addWindowListener(self.WindowListener(self.frame, self))

            screenSize = Toolkit.getDefaultToolkit().getScreenSize()
            frame_width = min(1024, min(screenSize.width-20, max(1024,int(round(self.mdGUI.firstMainFrame.getSize().width *.95,0)))))
            frame_height = min(screenSize.height-20, max(768, int(round(self.mdGUI.firstMainFrame.getSize().height *.95,0))))

            self.frame.setPreferredSize(Dimension(frame_width, frame_height))

            self.frame.setExtendedState(JFrame.NORMAL)
            self.frame.getContentPane().setLayout(BorderLayout())

            self.doneButton = JButton(mdGUI.getStr("done"))
            self.editButton = JButton(mdGUI.getStr("edit"))
            self.printButton = JButton(mdGUI.getStr("graph_print"))
            self.saveButton = JButton(mdGUI.getStr("graph_save"))
            self.copyButton = JButton(mdGUI.getStr("edit_copy"))
            self.copyButton.setEnabled(False)

            self.STATUS_LABEL = JLabel("")
            self.setDisplayStatus("" if not debug else "<DEBUG ON>", "R")

            p = JPanel(BorderLayout())

            self.viewer = MyGraphViewer(mdGUI)

            p.add(self.viewer, BorderLayout.CENTER)

            bp = JPanel(GridBagLayout())
            bp.setBorder(EmptyBorder(10, 10, 10, 10))
            x = 0
            bp.add(self.printButton, AwtUtil.getConstraints(x, 0, 0.0, 0.0, 1, 1, True, True));              x += 1
            bp.add(self.saveButton, AwtUtil.getConstraints(x, 0, 0.0, 0.0, 1, 1, True, True));               x += 1
            bp.add(self.copyButton, AwtUtil.getConstraints(x, 0, 0.0, 0.0, 1, 1, True, True));               x += 1
            bp.add(self.editButton, AwtUtil.getConstraints(x, 0, 0.0, 0.0, 1, 1, True, True));               x += 1
            bp.add(Box.createHorizontalStrut(20), AwtUtil.getConstraints(x, 0, 0.0, 0.0, 1, 1, True, True)); x += 1
            bp.add(self.STATUS_LABEL, AwtUtil.getConstraints(x, 0, 0.0, 0.0, 1, 1, True, True));       x += 1

            if self.isPreviewBuild():
                previewLbl = JLabel("<PREVIEW BUILD>")
                previewLbl.setForeground(getColorRed())
                bp.add(Box.createHorizontalStrut(20), AwtUtil.getConstraints(x, 0, 0.0, 0.0, 1, 1, True, True)); x += 1
                bp.add(previewLbl, AwtUtil.getConstraints(x, 0, 0.0, 0.0, 1, 1, True, True));                    x += 1

            bp.add(Box.createHorizontalStrut(20), AwtUtil.getConstraints(x, 0, 1.0, 0.0, 1, 1, True, True)); x += 1

            bp.add(self.doneButton, AwtUtil.getConstraints(x, 0, 0.0, 0.0, 1, 1, True, True));               x += 1
            p.add(bp, BorderLayout.SOUTH)
            self.doneButton.addActionListener(self)
            self.saveButton.addActionListener(self)
            self.printButton.addActionListener(self)
            self.copyButton.addActionListener(self)
            self.editButton.addActionListener(self)
            self.frame.getContentPane().add(p)

            self.setRememberSizeLocationKeys("gui.%s_size" %(self.moduleID), "gui.%s_location" %(self.moduleID), Dimension(1200, 1200))

            self.popupTableDialog = None        # type: MyPopupTableDialog

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

        def setDisplayStatus(self, _theStatus, _theColor=None):
            if self.STATUS_LABEL is None or not isinstance(self.STATUS_LABEL, JLabel): return

            self.STATUS_LABEL.setText(_theStatus)

            if _theColor is None or _theColor == "": _theColor = "X"
            _theColor = _theColor.upper()
            if _theColor == "R":    self.STATUS_LABEL.setForeground(getColorRed())
            elif _theColor == "B":  self.STATUS_LABEL.setForeground(getColorBlue())
            elif _theColor == "DG": self.STATUS_LABEL.setForeground(getColorDarkGreen())
            else:                   self.STATUS_LABEL.setForeground(self.mdGUI.getColors().defaultTextForeground)
            return

        def getFrame(self): return self.frame

        def showNoData(self):
            myPopupInformationBox(self.getFrame(), self.mdGUI.getStr("nothing_to_graph"), theMessageType=JOptionPane.WARNING_MESSAGE)

        def setRememberSizeLocationKeys(self, sizePrefsKey, locationPrefsKey, defaultSize=None):
            # type: (str, str, Dimension) -> None
            self._saveSizeKey = sizePrefsKey
            self._saveLocKey = locationPrefsKey
            if defaultSize is not None: self._defaultSize = defaultSize

        def saveSizeAndLocation(self):
            myPrint("DB","Saving window size and location: size('%s'): %s, location('%s'): %s" %(self._saveSizeKey, self.frame.getSize(), self._saveLocKey, self.frame.getLocation()))
            if self._saveSizeKey is not None: self.prefs.setSizeSetting(self._saveSizeKey, self.frame.getSize())
            if self._saveLocKey is not None: self.prefs.setXYSetting(self._saveLocKey, self.frame.getLocation())

        def loadSizeAndLocation(self, window=None, saveSizeKey=None, saveLocKey=None, defaultSize=None):
            # type: (Window, str, str, Dimension) -> None

            if window is None: window = self.getFrame()
            if saveSizeKey is None: saveSizeKey = self._saveSizeKey
            if saveLocKey is None: saveLocKey = self._saveLocKey
            if defaultSize is None: defaultSize = self._defaultSize

            sizeSetting = defaultSize if saveSizeKey is None else self.prefs.getSizeSetting(saveSizeKey)
            loc = None if saveLocKey is None else self.prefs.getSizeSetting(saveLocKey)
            if loc is None or sizeSetting.width == 0 or sizeSetting.height == 0:
                myPrint("DB","Loading window size and location: size('%s'): %s, location('%s'): %s" %(saveSizeKey, defaultSize, saveLocKey, window.getParent()))
                AwtUtil.setupWindow(window, defaultSize.width, defaultSize.height, window.getParent())
            else:
                myPrint("DB","Loading window size and location: size('%s'): %s, location('%s'): %s" %(saveSizeKey, sizeSetting, saveLocKey, saveLocKey))
                AwtUtil.setupWindow(window, sizeSetting.width, sizeSetting.height, loc.width, loc.height, window.getParent())

        def go(self):

            self.frame.pack()
            # self.frame.setLocationRelativeTo(None)
            self.loadSizeAndLocation()

            try:
                self.frame.MoneydanceAppListener = MyMoneydanceEventListener(self.frame, self.moneydanceContext)
                self.moneydanceContext.addAppEventListener(self.frame.MoneydanceAppListener)
                myPrint("DB","@@ added AppEventListener() %s @@" %(classPrinter("MoneydanceAppListener", self.frame.MoneydanceAppListener)))
            except:
                myPrint("B","FAILED to add MD App Listener...")
                dump_sys_error_to_md_console_and_errorlog()

            self.frame.setVisible(True)     # already on the EDT
            self.frame.toFront()            # already on the EDT
            self.frame.isActiveInMoneydance = True

            myPrint("DB","Adding Preferences listener:", self)
            self.moneydanceContext.getPreferences().addListener(self)

            if self.getGraph() is None:
                self.showNoData()
            else:
                self.showPopupTableDialog()

        def preferencesUpdated(self):
            myPrint("DB", "In %s.%s()" %(self, inspect.currentframe().f_code.co_name))

            myPrint("B","Your MD Preferences have been updated... I am closing this extension... Please relaunch if you want to use it...")
            SwingUtilities.invokeLater(GenericWindowClosingRunnable(self.frame))
            myPrint("DB","Back from calling GenericWindowClosingRunnable to push a WINDOW_CLOSING Event (via the Swing EDT) to %s...." %(self.moduleID))

        class ToggleDebugAction(AbstractAction):

            def __init__(self, callingClass):
                self.callingClass = callingClass

            def actionPerformed(self, event):                                                                           # noqa
                global debug
                debug = not debug
                self.callingClass.setDisplayStatus("" if not debug else "<DEBUG ON>", "R")
                myPopupInformationBox(None, "Debug status flipped - now set to: %s" %(debug))

        class CloseAction(AbstractAction):

            def __init__(self, theFrame, callingClass):
                self.theFrame = theFrame
                self.callingClass = callingClass

            def actionPerformed(self, event):                                                                           # noqa
                myPrint("DB","In CloseAction().", inspect.currentframe().f_code.co_name, "()")
                myPrint("DB", "MyShowGraphWindow() Frame shutting down....")

                myPrint("DB",".. calling terminate_script()")

                terminate_script(self.theFrame)

        class PrintAction(AbstractAction):

            def __init__(self, theFrame, callingClass):
                self.theFrame = theFrame
                self.callingClass = callingClass

            def actionPerformed(self, event):                                                                           # noqa
                myPrint("DB","In PrintAction().", inspect.currentframe().f_code.co_name, "()")
                self.callingClass.actionPerformed(event)

        class WindowListener(WindowAdapter):

            def __init__(self, theFrame, callingClass):
                self.theFrame = theFrame        # type: MyJFrame
                self.callingClass = callingClass

            def windowClosing(self, evt):                                                                               # noqa
                myPrint("DB","In ", inspect.currentframe().f_code.co_name, "()")
                myPrint("DB", "MyShowGraphWindow() Frame shutting down....")

                myPrint("DB",".. calling terminate_script()")
                terminate_script(self.theFrame)

            def windowClosed(self, evt):                                                                                # noqa
                myPrint("DB","In ", inspect.currentframe().f_code.co_name, "()")
                myPrint("DB", "... SwingUtilities.isEventDispatchThread() returns: %s" %(SwingUtilities.isEventDispatchThread()))

                self.callingClass.saveSizeAndLocation()

                self.theFrame.isActiveInMoneydance = False

                myPrint("DB","applistener is %s" %(classPrinter("MoneydanceAppListener", self.theFrame.MoneydanceAppListener)))

                if self.theFrame.MoneydanceAppListener is not None:
                    try:
                        self.callingClass.moneydanceContext.removeAppEventListener(self.theFrame.MoneydanceAppListener)
                        myPrint("DB","\n@@@ Removed my MD App Listener... %s\n" %(classPrinter("MoneydanceAppListener", self.theFrame.MoneydanceAppListener)))
                        self.theFrame.MoneydanceAppListener = None
                    except:
                        myPrint("B","FAILED to remove my MD App Listener... %s" %(classPrinter("MoneydanceAppListener", self.theFrame.MoneydanceAppListener)))
                        dump_sys_error_to_md_console_and_errorlog()

                if self.theFrame.HomePageViewObj is not None:
                    self.theFrame.HomePageViewObj.unload()
                    myPrint("DB","@@ Called HomePageView.unload() and Removed reference to HomePageView %s from MyJFrame()...@@\n" %(classPrinter("HomePageView", self.theFrame.HomePageViewObj)))
                    self.theFrame.HomePageViewObj = None

                myPrint("DB", "Removing Preferences listener:", self.callingClass)
                self.callingClass.moneydanceContext.getPreferences().removeListener(self.callingClass)

                cleanup_actions(self.theFrame)

        def editParameters(self):
            self.generator.setSuppressMessages(True)
            configWin = MyGraphDialog(self.mdGUI, self.moduleID, self.generator, self)
            configWin.setVisible(True)

        def actionPerformed(self, evt):
            # type: (ActionEvent) -> None

            myPrint("DB","In ", inspect.currentframe().f_code.co_name, "()")
            myPrint("DB", "event: %s" %(evt))
            myPrint("DB", "eventSource: %s" %(evt.getSource()))
            myPrint("DB", "getActionCommand: %s" %(evt.getActionCommand()))

            src = evt.getSource()
            if src is self.doneButton:
                terminate_script(self.getFrame())
            elif src is self.printButton or evt.getActionCommand().lower() == "p":
                MyGraphReportUtil.printGraph(self.mdGUI, self.viewer)
            elif src is self.saveButton:
                MyGraphReportUtil.saveGraph(self.mdGUI, self.viewer)
            elif src is self.copyButton:
                MyGraphReportUtil.copyGraph(self.mdGUI, self.viewer)
            elif src is self.editButton:
                self.editParameters()

        def showPopupTableDialog(self):

            if self.popupTableDialog is not None:
                self.popupTableDialog.goAwayNow()

            theData = self.viewer.getGraphSet().getPopupTableData()                                                     # noqa
            if theData is not None and self.generator.showPopupTableChoice.isSelected():

                # if debug: myPrint("DB","** theData:", theData, "(%s)" %(type(theData)))

                self.popupTableDialog = MyPopupTableDialog(self.mdGUI, self.moduleID, self.generator, self, theData)
                self.popupTableDialog.setVisible(True)
            else:
                self.popupTableDialog = None


        def setGraph(self, graphs):
            # type: (MyGraphSet) -> None
            if graphs is not None:
                self.viewer.setGraph(graphs)
                self.copyButton.setEnabled((graphs is not None))

                if self.frame.isVisible():
                    self.showPopupTableDialog()
            else:
                if self.frame.isVisible():
                    self.showNoData()

        def getGenerator(self):
            # type: () -> GraphReportGenerator
            return self.generator

        def setGenerator(self, theGenerator):
            # type: (GraphReportGenerator) -> None
            self.generator = theGenerator

        def getGraph(self): return self.viewer.getGraphSet()

    class MyReportSpec(ReportSpec):
        def __init__(self, *args):
            super(self.__class__, self).__init__(*args)

        def getReportGenerator(self): return None

    try:
        class MainAppRunnable(Runnable):
            def __init__(self): pass

            def run(self):                                                                                              # noqa
                global security_performance_graph_frame_    # global as defined here

                myPrint("DB", "In MainAppRunnable()", inspect.currentframe().f_code.co_name, "()")
                myPrint("DB", "SwingUtilities.isEventDispatchThread() = %s" %(SwingUtilities.isEventDispatchThread()))

                book = moneydance.getCurrentAccount().getBook()

                reportSpec = MyReportSpec(book)   # type: ReportSpec
                reportSpec.setName(GlobalVars.Strings.GRAPH_NAME)
                reportSpec.setReportID(myModuleID)
                reportSpec.setMemorized(False)

                theParams = SyncRecord()
                if GlobalVars.extn_param_graph_params_SPG is not None\
                        and isinstance(GlobalVars.extn_param_graph_params_SPG, (str, unicode))\
                        and len(GlobalVars.extn_param_graph_params_SPG)>2\
                        and GlobalVars.extn_param_graph_params_SPG.strip().startswith(":"):
                    theParams.readSet(StringReader(GlobalVars.extn_param_graph_params_SPG))
                    myPrint("DB","Graph parameters successfully loaded: %s" %(theParams))
                    reportSpec.setReportParameters(theParams)
                else:
                    myPrint("B","No graph parameters found (or invalid), resetting to defaults....")
                    reportSpec.setReportParameters(None)

                if debug:
                    myPrint("B","---")
                    myPrint("B",reportSpec.getReportParameters())
                    myPrint("B","---")
                    myPrint("B",reportSpec.getSyncInfo().toMultilineHumanReadableString())
                    myPrint("B","---")

                # copies com.moneydance.apps.md.view.gui.GraphReportGenerator.showReport(ReportSpec, MoneydanceGUI) : void

                # theGenerator = GraphReportGenerator.getGenerator(theReportSpec, MD_REF.getUI())			# type: GraphReportGenerator
                theGenerator = MySecurityPerformanceGraph(reportSpec.getName())
                theGenerator.setGUI(MD_REF.getUI())
                theGenerator.setSuppressMessages(True)
                theGenerator.setInfo(reportSpec)
                graphReportObj = theGenerator.generate()

                graphWinObj = MyShowGraphWindow(MD_REF, MD_REF.getUI(), myModuleID, reportSpec)
                security_performance_graph_frame_ = graphWinObj.getFrame()

                graphWinObj.setGraph(graphReportObj)
                graphWinObj.setGenerator(theGenerator)
                graphWinObj.go()

                myPrint("DB","Main JFrame %s for application created.." %(security_performance_graph_frame_.getName()))

        if not SwingUtilities.isEventDispatchThread():
            myPrint("DB",".. Main App Not running within the EDT so calling via MainAppRunnable()...")
            SwingUtilities.invokeAndWait(MainAppRunnable())
        else:
            myPrint("DB",".. Main App Already within the EDT so calling naked...")
            MainAppRunnable().run()

    except QuickAbortThisScriptException:
        myPrint("DB", "Caught Exception: QuickAbortThisScriptException... Doing nothing...")

    except:
        crash_txt = ("ERROR - %s has crashed. Please review MD Menu>Help>Console Window for details" %(myModuleID)).upper()
        myPrint("B",crash_txt)
        crash_output = dump_sys_error_to_md_console_and_errorlog(True)
        jifr = QuickJFrame("ERROR - %s:" %(myModuleID),crash_output).show_the_frame()
        myPopupInformationBox(jifr,crash_txt,theMessageType=JOptionPane.ERROR_MESSAGE)

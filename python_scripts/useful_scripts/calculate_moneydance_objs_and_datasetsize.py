#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# calculate_moneydance_objs_and_datasetsize.py build: 4 - Feb 2021 - Stuart Beesley StuWareSoftSystems

# COMMON IMPORTS #######################################################################################################
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

from org.python.core.util import FileUtil

from com.moneydance.util import Platform
from com.moneydance.awt import JTextPanel, GridC, JDateField
from com.moneydance.apps.md.view.gui import MDImages

from com.infinitekind.util import DateUtil, CustomDateFormat
from com.infinitekind.moneydance.model import *
from com.infinitekind.moneydance.model import AccountUtil, AcctFilter, CurrencyType, CurrencyUtil
from com.infinitekind.moneydance.model import Account, Reminder, ParentTxn, SplitTxn, TxnSearch, InvestUtil, TxnUtil

from javax.swing import JButton, JScrollPane, WindowConstants, JFrame, JLabel, JPanel, JComponent, KeyStroke, JDialog, JComboBox
from javax.swing import JOptionPane, JTextArea, JMenuBar, JMenu, JMenuItem, AbstractAction, JCheckBoxMenuItem, JFileChooser
from javax.swing import JTextField, JPasswordField, Box, UIManager, JTable, JCheckBox, JRadioButton, ButtonGroup
from javax.swing.text import PlainDocument
from javax.swing.border import EmptyBorder

from java.awt import Color, Dimension, FileDialog, FlowLayout, Toolkit, Font, GridBagLayout, GridLayout
from java.awt import BorderLayout, Dialog, Insets
from java.awt.event import KeyEvent, WindowAdapter, InputEvent

from java.text import DecimalFormat, SimpleDateFormat
from java.util import Calendar, ArrayList
from java.lang import System, Double, Math, Character
from java.io import FileNotFoundException, FilenameFilter, File, FileInputStream, FileOutputStream, IOException, StringReader
from java.io import BufferedReader, InputStreamReader
if isinstance(None, (JDateField,CurrencyUtil,Reminder,ParentTxn,SplitTxn,TxnSearch, JComboBox, JCheckBox,
                     JTextArea, JMenuBar, JMenu, JMenuItem, JCheckBoxMenuItem, JFileChooser, JDialog,
                     JButton, FlowLayout, InputEvent, ArrayList, File, IOException, StringReader, BufferedReader,
                     InputStreamReader, Dialog, JTable, BorderLayout, Double, InvestUtil, JRadioButton, ButtonGroup,
                     AccountUtil, AcctFilter, CurrencyType, Account, TxnUtil, JScrollPane, WindowConstants, JFrame,
                     JComponent, KeyStroke, AbstractAction, UIManager, Color, Dimension, Toolkit, KeyEvent,
                     WindowAdapter, CustomDateFormat, SimpleDateFormat, Insets)): pass
if codecs.BOM_UTF8 is not None: pass
if csv.QUOTE_ALL is not None: pass
if datetime.MINYEAR is not None: pass
if Math.max(1,1): pass
# END COMMON IMPORTS ###################################################################################################

# COMMON GLOBALS #######################################################################################################
global debug  # Set to True if you want verbose messages, else set to False....
global myParameters, myScriptName, version_build, _resetParameters, i_am_an_extension_so_run_headless, moneydanceIcon
global lPickle_version_warning, decimalCharSep, groupingCharSep, lIamAMac, lGlobalErrorDetected
global MYPYTHON_DOWNLOAD_URL
# END COMMON GLOBALS ###################################################################################################

# SET THESE VARIABLES FOR ALL SCRIPTS ##################################################################################
version_build = "4"                                                                                                 # noqa
myScriptName = "calculate_moneydance_objs_and_datasetsize.py(Extension)"                                            # noqa
debug = False                                                                                                       # noqa
myParameters = {}                                                                                                   # noqa
_resetParameters = False                                                                                            # noqa
lPickle_version_warning = False                                                                                     # noqa
lIamAMac = False                                                                                                    # noqa
lGlobalErrorDetected = False																						# noqa
MYPYTHON_DOWNLOAD_URL = "https://yogi1967.github.io/MoneydancePythonScripts/"                                       # noqa
# END SET THESE VARIABLES FOR ALL SCRIPTS ##############################################################################

# >>> THIS SCRIPT'S IMPORTS ############################################################################################
from com.infinitekind.moneydance.model import MoneydanceSyncableItem
from com.infinitekind.moneydance.model import OnlineTxnList, OnlinePayeeList, OnlinePaymentList
from com.moneydance.apps.md.controller import Common
from com.moneydance.apps.md.view.gui.sync import SyncFolderUtil
from com.moneydance.apps.md.controller.io import FileUtils, AccountBookUtil
# >>> THIS SCRIPT'S GLOBALS ############################################################################################
# >>> END THIS SCRIPT'S GLOBALS ############################################################################################


# COMMON CODE ##########################################################################################################
i_am_an_extension_so_run_headless = False                                                                           # noqa
try:
    myScriptName = os.path.basename(__file__)
except:
    i_am_an_extension_so_run_headless = True                                                                        # noqa

scriptExit = """
----------------------------------------------------------------------------------------------------------------------
Thank you for using %s! The author has other useful Extensions / Moneybot Python scripts available...:

Extension (.mxt) format only:
toolbox                                 View Moneydance settings, diagnostics, fix issues, change settings and much more

Extension (.mxt) and Script (.py) Versions available:
stockglance2020                         View summary of Securities/Stocks on screen, total by Security, export to csv 
extract_reminders_csv                   View reminders on screen, edit if required, extract all to csv
extract_currency_history_csv            Extract currency history to csv
extract_investment_transactions_csv     Extract investment transactions to csv
extract_account_registers_csv           Extract Account Register(s) to csv along with any attachments

A collection of useful ad-hoc scripts (zip file)
useful_scripts:                         Just unzip and select the script you want for the task at hand...

Visit: %s (Author's site)
----------------------------------------------------------------------------------------------------------------------
""" %(myScriptName, MYPYTHON_DOWNLOAD_URL)

# P=Display on Python Console, J=Display on MD (Java) Console Error Log, B=Both, D=If Debug Only print, DB=print both
def myPrint(where, *args):
    global myScriptName, debug, i_am_an_extension_so_run_headless

    if where[0] == "D" and not debug: return

    printString = ""
    for what in args:
        printString += "%s " %what
    printString = printString.strip()

    if where == "P" or where == "B" or where[0] == "D":
        if not i_am_an_extension_so_run_headless:
            try:
                print(printString)
            except:
                print("Error writing to screen...")
                dump_sys_error_to_md_console_and_errorlog()

    if where == "J" or where == "B" or where == "DB":
        dt = datetime.datetime.now().strftime("%Y/%m/%d-%H:%M:%S")
        try:
            System.err.write(myScriptName + ":" + dt + ": ")
            System.err.write(printString)
            System.err.write("\n")
        except:
            System.err.write(myScriptName + ":" + dt + ": "+"Error writing to console")
            dump_sys_error_to_md_console_and_errorlog()
    return

def dump_sys_error_to_md_console_and_errorlog( lReturnText=False ):

    theText = ""
    myPrint("B","Unexpected error caught: %s" %(sys.exc_info()[0]))
    myPrint("B","Unexpected error caught: %s" %(sys.exc_info()[1]))
    myPrint("B","Error on Script Line Number: %s" %(sys.exc_info()[2].tb_lineno))

    if lReturnText:
        theText += "\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
        theText += "Unexpected error caught: %s\n" %(sys.exc_info()[0])
        theText += "Unexpected error caught: %s\n" %(sys.exc_info()[1])
        theText += "Error on Script Line Number: %s\n" %(sys.exc_info()[2].tb_lineno)
        theText += "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
        return theText

    return

def pad(theText, theLength):
    theText = theText[:theLength].ljust(theLength, u" ")
    return theText

def rpad(theText, theLength):
    if not (isinstance(theText, unicode) or isinstance(theText, str)):
        theText = str(theText)

    theText = theText[:theLength].rjust(theLength, u" ")
    return theText

def cpad(theText, theLength):
    if not (isinstance(theText, unicode) or isinstance(theText, str)):
        theText = str(theText)

    if len(theText)>=theLength: return theText[:theLength]

    padLength = int((theLength - len(theText)) / 2)
    theText = theText[:theLength]
    theText = ((" "*padLength)+theText+(" "*padLength))[:theLength]

    return theText


myPrint("B", myScriptName, ": Python Script Initialising.......", "Build:", version_build)

def is_moneydance_loaded_properly():
    global debug

    if debug or moneydance_data is None or moneydance_ui is None:
        for theClass in ["moneydance",  moneydance], ["moneydance_ui",moneydance_ui], ["moneydance_data",moneydance_data]:
            myPrint("B","Moneydance Objects now....: Class: %s %s@{:x}".format(System.identityHashCode(theClass[1])) %(pad(theClass[0],20), theClass[1].__class__))
        myPrint("P","")

    if moneydance is not None and moneydance_data is not None and moneydance_ui is not None:                        # noqa
        if debug: myPrint("B","Success - Moneydance variables are already set....")
        return

    # to cope with being run as Extension.... temporary
    if moneydance is not None and moneydance_data is None and moneydance_ui is None:                                # noqa
        myPrint("B", "@@@ Moneydance variables not set (run as extension?) - attempting to manually set @@@")
        exec "global moneydance_ui;" + "moneydance_ui=moneydance.getUI();"
        exec "global moneydance_data;" + "moneydance_data=moneydance.getCurrentAccount().getBook();"

        for theClass in ["moneydance",moneydance], ["moneydance_ui",moneydance_ui], ["moneydance_data",moneydance_data]:
            myPrint("B","Moneydance Objects after manual setting....: Class: %s %s@{:x}".format(System.identityHashCode(theClass[1])) %(pad(theClass[0],20), theClass[1].__class__))
        myPrint("P","")

    return


is_moneydance_loaded_properly()


def getMonoFont():
    global debug

    try:
        theFont = moneydance_ui.getFonts().code
        # if debug: myPrint("B","Success setting Font set to Moneydance code: %s" %theFont)
    except:
        theFont = Font("monospaced", Font.PLAIN, 15)
        if debug: myPrint("B","Failed to Font set to Moneydance code - So using: %s" %theFont)

    return theFont

def getTheSetting(what):
    x = moneydance_ui.getPreferences().getSetting(what, None)
    if not x or x == u"": return None
    return what + u": %s" %(x)

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

    if not homeDir: homeDir = u"?"
    return homeDir

def getDecimalPoint(lGetPoint=False, lGetGrouping=False):
    global debug

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


decimalCharSep = getDecimalPoint(lGetPoint=True)
groupingCharSep = getDecimalPoint(lGetGrouping=True)

# JOptionPane.DEFAULT_OPTION, JOptionPane.YES_NO_OPTION, JOptionPane.YES_NO_CANCEL_OPTION, JOptionPane.OK_CANCEL_OPTION
# JOptionPane.ERROR_MESSAGE, JOptionPane.INFORMATION_MESSAGE, JOptionPane.WARNING_MESSAGE, JOptionPane.QUESTION_MESSAGE, JOptionPane.PLAIN_MESSAGE

# Copies Moneydance_ui.showInfoMessage
def myPopupInformationBox(theParent=None, theMessage="What no message?!", theTitle="Info", theMessageType=JOptionPane.INFORMATION_MESSAGE):

    if theParent is None:
        if theMessageType == JOptionPane.PLAIN_MESSAGE or theMessageType == JOptionPane.INFORMATION_MESSAGE:
            icon_to_use=moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png")
            JOptionPane.showMessageDialog(theParent, JTextPanel(theMessage), theTitle, theMessageType, icon_to_use)
            return
    JOptionPane.showMessageDialog(theParent, JTextPanel(theMessage), theTitle, theMessageType)
    return

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

def myPopupAskBackup(theParent=None, theMessage="What no message?!"):

    _options=["STOP", "PROCEED WITHOUT BACKUP", "DO BACKUP NOW"]
    response = JOptionPane.showOptionDialog(theParent,
                                            theMessage,
                                            "PERFORM BACKUP BEFORE UPDATE?",
                                            0,
                                            JOptionPane.WARNING_MESSAGE,
                                            None,
                                            _options,
                                            _options[0])

    if response == 2:
        myPrint("B", "User requested to perform Export Backup before update/fix - calling moneydance export backup routine...")
        moneydance_ui.saveToBackup(None)
        return True

    elif response == 1:
        myPrint("B", "User DECLINED to perform Export Backup before update/fix...!")
        return True

    return False

# Copied Moneydance_ui.askQuestion
def myPopupAskQuestion(theParent=None,
                       theTitle="Question",
                       theQuestion="What?",
                       theOptionType=JOptionPane.YES_NO_OPTION,
                       theMessageType=JOptionPane.QUESTION_MESSAGE):

    icon_to_use = None
    if theParent is None:
        if theMessageType == JOptionPane.PLAIN_MESSAGE or theMessageType == JOptionPane.INFORMATION_MESSAGE:
            icon_to_use=moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png")

    # question = wrapLines(theQuestion)
    question = theQuestion
    result = JOptionPane.showConfirmDialog(theParent,
                                           question,
                                           theTitle,
                                           theOptionType,
                                           theMessageType,
                                           icon_to_use)  # getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"))

    return result == 0

# Copies Moneydance .askForQuestion
def myPopupAskForInput(theParent,
                       theTitle,
                       theFieldLabel,
                       theFieldDescription="",
                       defaultValue=None,
                       isPassword=False,
                       theMessageType=JOptionPane.INFORMATION_MESSAGE):

    icon_to_use = None
    if theParent is None:
        if theMessageType == JOptionPane.PLAIN_MESSAGE or theMessageType == JOptionPane.INFORMATION_MESSAGE:
            icon_to_use=moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png")

    p = JPanel(GridBagLayout())
    defaultText = None
    if defaultValue: defaultText = defaultValue
    if isPassword:
        field = JPasswordField(defaultText)
    else:
        field = JTextField(defaultText)

    x = 0
    if theFieldLabel:
        p.add(JLabel(theFieldLabel), GridC.getc(x, 0).east())
        x+=1

    p.add(field, GridC.getc(x, 0).field())
    p.add(Box.createHorizontalStrut(244), GridC.getc(x, 0))
    if theFieldDescription:
        p.add(JTextPanel(theFieldDescription), GridC.getc(x, 1).field().colspan(x + 1))
    if (JOptionPane.showConfirmDialog(theParent,
                                      p,
                                      theTitle,
                                      JOptionPane.OK_CANCEL_OPTION,
                                      theMessageType,
                                      icon_to_use) == 0):
        return field.getText()
    return None

# APPLICATION_MODAL, DOCUMENT_MODAL, MODELESS, TOOLKIT_MODAL
class MyPopUpDialogBox():

    def __init__(self, theParent=None, theStatus="", theMessage="", theWidth=200, theTitle="Info", lModal=True, lCancelButton=False, OKButtonText="OK", lAlertLevel=0):
        self.theParent = theParent
        self.theStatus = theStatus
        self.theMessage = theMessage
        self.theWidth = max(80,theWidth)
        self.theTitle = theTitle
        self.lModal = lModal
        self.lCancelButton = lCancelButton
        self.OKButtonText = OKButtonText
        self.lAlertLevel = lAlertLevel
        self.fakeJFrame = None
        self._popup_d = None
        self.lResult = [None]
        if not self.theMessage.endswith("\n"): self.theMessage+="\n"
        if self.OKButtonText == "": self.OKButtonText="OK"

    class WindowListener(WindowAdapter):

        def __init__(self, theDialog, theFakeFrame, lResult):
            self.theDialog = theDialog
            self.theFakeFrame = theFakeFrame
            self.lResult = lResult

        def windowClosing(self, WindowEvent):                                                                       # noqa
            global debug
            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", WindowEvent)

            myPrint("DB", "JDialog Frame shutting down....")

            self.lResult[0] = False

            if self.theFakeFrame is not None:
                self.theDialog.dispose()
                self.theFakeFrame.dispose()
            else:
                self.theDialog.dispose()

            myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
            return

    class OKButtonAction(AbstractAction):
        # noinspection PyMethodMayBeStatic

        def __init__(self, theDialog, theFakeFrame, lResult):
            self.theDialog = theDialog
            self.theFakeFrame = theFakeFrame
            self.lResult = lResult

        def actionPerformed(self, event):
            global debug
            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event)

            self.lResult[0] = True

            if self.theFakeFrame is not None:
                self.theDialog.dispose()
                self.theFakeFrame.dispose()
            else:
                self.theDialog.dispose()

            myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
            return

    class CancelButtonAction(AbstractAction):
        # noinspection PyMethodMayBeStatic

        def __init__(self, theDialog, theFakeFrame, lResult):
            self.theDialog = theDialog
            self.theFakeFrame = theFakeFrame
            self.lResult = lResult

        def actionPerformed(self, event):
            global debug
            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event)

            self.lResult[0] = False

            if self.theFakeFrame is not None:
                self.theDialog.dispose()
                self.theFakeFrame.dispose()
            else:
                self.theDialog.dispose()

            myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
            return

    def kill(self):

        global debug
        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        self._popup_d.setVisible(False)
        if self.fakeJFrame is not None:
            self._popup_d.dispose()
            self.fakeJFrame.dispose()
        else:
            self._popup_d.dispose()

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
        return

    def result(self):

        global debug
        return self.lResult[0]

    def go(self):
        global debug

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        # Create a fake JFrame so we can set the Icons...
        if self.theParent is None:
            self.fakeJFrame = JFrame()
            self.fakeJFrame.setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE)
            self.fakeJFrame.setUndecorated(True)
            self.fakeJFrame.setVisible( False )
            if not Platform.isOSX():
                self.fakeJFrame.setIconImage(MDImages.getImage(moneydance_ui.getMain().getSourceInformation().getIconResource()))

        if self.lModal:
            # noinspection PyUnresolvedReferences
            self._popup_d = JDialog(self.theParent, self.theTitle, Dialog.ModalityType.APPLICATION_MODAL)
        else:
            # noinspection PyUnresolvedReferences
            self._popup_d = JDialog(self.theParent, self.theTitle, Dialog.ModalityType.MODELESS)

        self._popup_d.setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE)

        shortcut = Toolkit.getDefaultToolkit().getMenuShortcutKeyMaskEx()

        # Add standard CMD-W keystrokes etc to close window
        self._popup_d.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_W, shortcut), "close-window")
        self._popup_d.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_F4, shortcut), "close-window")
        self._popup_d.getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0), "close-window")
        self._popup_d.getRootPane().getActionMap().put("close-window", self.CancelButtonAction(self._popup_d, self.fakeJFrame,self.lResult))
        self._popup_d.addWindowListener(self.WindowListener(self._popup_d, self.fakeJFrame,self.lResult))

        if (not Platform.isMac()):
            # moneydance_ui.getImages()
            self._popup_d.setIconImage(MDImages.getImage(moneydance_ui.getMain().getSourceInformation().getIconResource()))

        displayJText = JTextArea(self.theMessage)
        displayJText.setFont( getMonoFont() )
        displayJText.setEditable(False)
        displayJText.setLineWrap(False)
        displayJText.setWrapStyleWord(False)

        _popupPanel=JPanel()

        # maxHeight = 500
        _popupPanel.setLayout(GridLayout(0,1))
        _popupPanel.setBorder(EmptyBorder(8, 8, 8, 8))
        # _popupPanel.setMinimumSize(Dimension(self.theWidth, 0))
        # _popupPanel.setMaximumSize(Dimension(self.theWidth, maxHeight))

        if self.theStatus:
            _label1 = JLabel(pad(self.theStatus,self.theWidth-20))
            _label1.setForeground(Color.BLUE)
            _popupPanel.add(_label1)

        myScrollPane = JScrollPane(displayJText, JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED,JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED)
        if displayJText.getLineCount()>5:
            # myScrollPane.setMinimumSize(Dimension(self.theWidth-20, 10))
            # myScrollPane.setMaximumSize(Dimension(self.theWidth-20, maxHeight-100))
            myScrollPane.setWheelScrollingEnabled(True)
            _popupPanel.add(myScrollPane)
        else:
            _popupPanel.add(displayJText)

        buttonPanel = JPanel()
        if self.lModal or self.lCancelButton:
            buttonPanel.setLayout(FlowLayout(FlowLayout.CENTER))

            if self.lCancelButton:
                cancel_button = JButton("CANCEL")
                cancel_button.setPreferredSize(Dimension(100,40))
                cancel_button.setBackground(Color.LIGHT_GRAY)
                cancel_button.setBorderPainted(False)
                cancel_button.setOpaque(True)
                cancel_button.addActionListener( self.CancelButtonAction(self._popup_d, self.fakeJFrame,self.lResult) )
                buttonPanel.add(cancel_button)

            if self.lModal:
                ok_button = JButton(self.OKButtonText)
                if len(self.OKButtonText) <= 2:
                    ok_button.setPreferredSize(Dimension(100,40))
                else:
                    ok_button.setPreferredSize(Dimension(200,40))

                ok_button.setBackground(Color.LIGHT_GRAY)
                ok_button.setBorderPainted(False)
                ok_button.setOpaque(True)
                ok_button.addActionListener( self.OKButtonAction(self._popup_d, self.fakeJFrame, self.lResult) )
                buttonPanel.add(ok_button)

            _popupPanel.add(buttonPanel)

        if self.lAlertLevel>=2:
            # internalScrollPane.setBackground(Color.RED)
            # theJText.setBackground(Color.RED)
            # theJText.setForeground(Color.BLACK)
            displayJText.setBackground(Color.RED)
            displayJText.setForeground(Color.BLACK)
            _popupPanel.setBackground(Color.RED)
            _popupPanel.setForeground(Color.BLACK)
            buttonPanel.setBackground(Color.RED)
            myScrollPane.setBackground(Color.RED)

        elif self.lAlertLevel>=1:
            # internalScrollPane.setBackground(Color.YELLOW)
            # theJText.setBackground(Color.YELLOW)
            # theJText.setForeground(Color.BLACK)
            displayJText.setBackground(Color.YELLOW)
            displayJText.setForeground(Color.BLACK)
            _popupPanel.setBackground(Color.YELLOW)
            _popupPanel.setForeground(Color.BLACK)
            buttonPanel.setBackground(Color.YELLOW)
            myScrollPane.setBackground(Color.RED)

        self._popup_d.add(_popupPanel)
        self._popup_d.pack()
        self._popup_d.setLocationRelativeTo(None)
        self._popup_d.setVisible(True)

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

        return self.lResult[0]

def play_the_money_sound():

    # Seems to cause a crash on Virtual Machine with no Audio - so just in case....
    try:
        moneydance_ui.getSounds().playSound("cash_register.wav")
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
    ext = ""

    def __init__(self, ext):
        self.ext = "." + ext.upper()

    def accept(self, thedir, filename):                                                                             # noqa
        if filename is not None and filename.upper().endswith(self.ext):
            return True
        return False


moneydanceIcon = MDImages.getImage(moneydance_ui.getMain().getSourceInformation().getIconResource())

def MDDiag():
    global debug
    myPrint("D", "Moneydance Build:", moneydance.getVersion(), "Build:", moneydance.getBuild())


MDDiag()

myPrint("DB","System file encoding is:", sys.getfilesystemencoding() )   # Not used, but interesting. Perhaps useful when switching between Windows/Macs and writing files...

def checkVersions():
    global debug

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

    myFont = moneydance_ui.getFonts().defaultText

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

    return


setDefaultFonts()

def who_am_i():
    try:
        username = System.getProperty("user.name")
    except:
        username = "???"

    return username

def getHomeDir():
    # Yup - this can be all over the place...
    myPrint("D", 'System.getProperty("user.dir")', System.getProperty("user.dir"))
    myPrint("D", 'System.getProperty("UserHome")', System.getProperty("UserHome"))
    myPrint("D", 'System.getProperty("user.home")', System.getProperty("user.home"))
    myPrint("D", 'os.path.expanduser("~")', os.path.expanduser("~"))
    myPrint("D", 'os.environ.get("HOMEPATH")', os.environ.get("HOMEPATH"))
    return

def amIaMac():
    myPlat = System.getProperty("os.name")
    if myPlat is None: return False
    myPrint("DB", "Platform:", myPlat)
    myPrint("DB", "OS Version:", System.getProperty("os.version"))
    return myPlat == "Mac OS X"


myPrint("D", "I am user:", who_am_i())
if debug: getHomeDir()
lIamAMac = amIaMac()

def myDir():
    global lIamAMac
    homeDir = None

    try:
        if lIamAMac:
            homeDir = System.getProperty("UserHome")  # On a Mac in a Java VM, the homedir is hidden
        else:
            # homeDir = System.getProperty("user.home")
            homeDir = os.path.expanduser("~")  # Should work on Unix and Windows
            if homeDir is None or homeDir == "":
                homeDir = System.getProperty("user.home")
            if homeDir is None or homeDir == "":
                homeDir = os.environ.get("HOMEPATH")
    except:
        pass

    if homeDir is None or homeDir == "":
        homeDir = moneydance_data.getRootFolder().getParent()  # Better than nothing!

    myPrint("DB", "Home Directory selected...:", homeDir)
    if homeDir is None: return ""
    return homeDir

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
                super(JTextFieldLimitYN, self).insertString(myOffset, myString, myAttr)                         # noqa

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

def get_StuWareSoftSystems_parameters_from_file():
    global debug, myParameters, lPickle_version_warning, version_build, _resetParameters                            # noqa

    myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )

    if _resetParameters:
        myPrint("B", "User has specified to reset parameters... keeping defaults and skipping pickle()")
        myParameters = {}
        return

    myFile = "StuWareSoftSystems.dict"
    old_dict_filename = os.path.join("..", myFile)

    # Pickle was originally encrypted, no need, migrating to unencrypted
    migratedFilename = os.path.join(moneydance_data.getRootFolder().getAbsolutePath(),myFile)

    myPrint("DB", "Now checking for parameter file:", migratedFilename)

    if os.path.exists( migratedFilename ):

        myPrint("DB", "loading parameters from non-encrypted Pickle file:", migratedFilename)
        myPrint("DB", "Parameter file", migratedFilename, "exists..")
        # Open the file
        try:
            istr = FileInputStream(migratedFilename)
            load_file = FileUtil.wrap(istr)
            # noinspection PyTypeChecker
            myParameters = pickle.load(load_file)
            load_file.close()
        except FileNotFoundException:
            myPrint("B", "Error: failed to find parameter file...")
            myParameters = None
        except EOFError:
            myPrint("B", "Error: reached EOF on parameter file....")
            myParameters = None
        except:
            myPrint("B","Error opening Pickle File (will try encrypted version) - Unexpected error ", sys.exc_info()[0])
            myPrint("B","Error opening Pickle File (will try encrypted version) - Unexpected error ", sys.exc_info()[1])
            myPrint("B","Error opening Pickle File (will try encrypted version) - Line Number: ", sys.exc_info()[2].tb_lineno)

            # OK, so perhaps from older version - encrypted, try to read
            try:
                local_storage = moneydance.getCurrentAccountBook().getLocalStorage()
                istr = local_storage.openFileForReading(old_dict_filename)
                load_file = FileUtil.wrap(istr)
                # noinspection PyTypeChecker
                myParameters = pickle.load(load_file)
                load_file.close()
                myPrint("B","Success loading Encrypted Pickle file - will migrate to non encrypted")
                lPickle_version_warning = True
            except:
                myPrint("B","Opening Encrypted Pickle File - Unexpected error ", sys.exc_info()[0])
                myPrint("B","Opening Encrypted Pickle File - Unexpected error ", sys.exc_info()[1])
                myPrint("B","Error opening Pickle File - Line Number: ", sys.exc_info()[2].tb_lineno)
                myPrint("B", "Error: Pickle.load() failed.... Is this a restored dataset? Will ignore saved parameters, and create a new file...")
                myParameters = None

        if myParameters is None:
            myParameters = {}
            myPrint("DB","Parameters did not load, will keep defaults..")
        else:
            myPrint("DB","Parameters successfully loaded from file...")
    else:
        myPrint("J", "Parameter Pickle file does not exist - will use default and create new file..")
        myPrint("D", "Parameter Pickle file does not exist - will use default and create new file..")
        myParameters = {}

    if not myParameters: return

    myPrint("DB","myParameters read from file contains...:")
    for key in sorted(myParameters.keys()):
        myPrint("DB","...variable:", key, myParameters[key])

    if myParameters.get("debug") is not None: debug = myParameters.get("debug")
    if myParameters.get("lUseMacFileChooser") is not None:
        myPrint("B", "Detected old lUseMacFileChooser parameter/variable... Will delete it...")
        myParameters.pop("lUseMacFileChooser", None)  # Old variable - not used - delete from parameter file

    myPrint("DB","Parameter file loaded if present and myParameters{} dictionary set.....")

    # Now load into memory!
    load_StuWareSoftSystems_parameters_into_memory()

    return

def save_StuWareSoftSystems_parameters_to_file():
    global debug, myParameters, lPickle_version_warning, version_build

    myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )

    if myParameters is None: myParameters = {}

    # Don't forget, any parameters loaded earlier will be preserved; just add changed variables....
    myParameters["__Author"] = "Stuart Beesley - (c) StuWareSoftSystems"
    myParameters["debug"] = debug

    dump_StuWareSoftSystems_parameters_from_memory()

    myFile = "StuWareSoftSystems.dict"
    # Pickle was originally encrypted, no need, migrating to unencrypted
    migratedFilename = os.path.join(moneydance_data.getRootFolder().getAbsolutePath(),myFile)

    myPrint("DB","Will try to save parameter file:", migratedFilename)

    ostr = FileOutputStream(migratedFilename)

    myPrint("DB", "about to Pickle.dump and save parameters to unencrypted file:", migratedFilename)

    try:
        save_file = FileUtil.wrap(ostr)
        # noinspection PyTypeChecker
        pickle.dump(myParameters, save_file)
        save_file.close()

        myPrint("DB","myParameters now contains...:")
        for key in sorted(myParameters.keys()):
            myPrint("DB","...variable:", key, myParameters[key])

    except:
        myPrint("B", "Error - failed to create/write parameter file.. Ignoring and continuing.....")
        dump_sys_error_to_md_console_and_errorlog()

        return

    myPrint("DB","Parameter file written and parameters saved to disk.....")

    return

# END COMMON DEFINITIONS ###############################################################################################
# END COMMON DEFINITIONS ###############################################################################################
# END COMMON DEFINITIONS ###############################################################################################


if isinstance(None, FileDialog): pass

startDir=moneydance_data.getRootFolder().getCanonicalPath()
print("\nDataset path:        %s" %(startDir))
print("Autobackup location: %s\n"
      %(moneydance_ui.getPreferences().getSetting("backup.location",FileUtils.getDefaultBackupDir().getAbsolutePath())))

attach = moneydance.getCurrentAccountBook().getAttachmentsFolder()
keyDir = startDir
trunkDir = os.path.join(startDir,"safe","tiksync")
attachDir = os.path.join(startDir,"safe", attach)
settingsDir = os.path.join(startDir,"safe")
archiveDir = os.path.join(startDir,"safe","archive")
sync_outDir = os.path.join(startDir,"safe","tiksync", "out")

sync_outCount = 0
sync_outSize = 0

safe_settingsSize = 0
safe_attachmentsSize = 0
countAttachments = 0
safe_archiveSize = 0
countArchiveFiles = 0
safe_trunkSize = 0
safe_tiksyncSize = 0
countTIKfiles = 0
safe_tmpSize = 0
keySize = 0
countValidFiles=0
countNonValidFiles=0
validSize=0
nonValidSize=0
listNonValidFiles=[]
listLargeFiles=[]

total_size = 0
start_path = startDir  # To get size of current directory
for path, dirs, files in os.walk(start_path):
    for f in files:
        lValidFile = False

        fp = os.path.join(path, f)
        thisFileSize = os.path.getsize(fp)

        total_size += thisFileSize

        if os.path.basename(f) == "key" and path==keyDir and len:
            lValidFile = True
            keySize=thisFileSize
        if os.path.basename(f) == "settings" and path==settingsDir:
            lValidFile = True
            safe_settingsSize=thisFileSize
        if os.path.basename(f) == "trunk" and path==trunkDir:
            lValidFile = True
            safe_trunkSize=thisFileSize
        if path[:len(sync_outDir)] == sync_outDir and (f.endswith(".txn") ):
            lValidFile = True
            sync_outSize+=thisFileSize
            sync_outCount+=1
        if path[:len(trunkDir)] == trunkDir and (f.endswith("trunk") or f.endswith(".mdtxn") or f.endswith("processed.dct") or f.endswith("delete_to_push_sync_info") or f.endswith(".txn") or f.endswith("force_push_resync") ):
            lValidFile = True
            safe_tiksyncSize+=thisFileSize
            countTIKfiles+=1
        if path[:len(attachDir)] == attachDir:
            lValidFile = True
            safe_attachmentsSize+=thisFileSize
            countAttachments+=1
        if path[:len(archiveDir)] == archiveDir and f.endswith(".mdtxnarchive"):
            lValidFile = True
            safe_archiveSize+=thisFileSize
            countArchiveFiles+=1

        if lValidFile:
            countValidFiles+=1
            validSize+=thisFileSize
            if thisFileSize>500000:
                listLargeFiles.append([fp,
                                      thisFileSize,
                                      pad(datetime.datetime.fromtimestamp(os.path.getmtime(fp)).strftime('%Y-%m-%d %H:%M:%S'),11)])
        else:
            countNonValidFiles+=1
            nonValidSize+=thisFileSize
            listNonValidFiles.append([fp,
                                      thisFileSize,
                                      pad(datetime.datetime.fromtimestamp(os.path.getmtime(fp)).strftime('%Y-%m-%d %H:%M:%S'),11)])

print("Dataset size:               %sMB" %(rpad(round((total_size/(1000.0*1000.0)),1),12)))
print("- settings file size:       %sKB" %(rpad(round((safe_settingsSize/(1000.0)),1),12)))
print("- key file size:            %sKB" %(rpad(round((keySize/   (1000.0)),1),12)))
print("- tiksync folder size:      %sMB (with %s files)" %(rpad(round((safe_tiksyncSize/(1000.0*1000.0)),1),12),countTIKfiles))
print("  (note trunk file size:    %sMB)" %(rpad(round((safe_trunkSize/(1000.0*1000.0)),1),12)))

if sync_outCount:
    print("  (WAITING Sync 'Out' size: %sMB with %s files)" %(rpad(round((sync_outSize/(1000.0*1000.0)),1),12),sync_outCount))

print("- attachments size:         %sMB (in %s attachments)" %(rpad(round((safe_attachmentsSize/(1000.0*1000.0)),1),12),countAttachments))
print("- archive size:             %sMB (in %s files)" %(rpad(round((safe_archiveSize/(1000.0*1000.0)),1),12),countArchiveFiles))
print("---------------------------------------------")
print("Valid files size:           %sMB (in %s files)" %(rpad(round((validSize/(1000.0*1000.0)),1),12),countValidFiles))
print
print("Non-core file(s) size:      %sMB (in %s files)" %(rpad(round((nonValidSize/(1000.0*1000.0)),1),12),countNonValidFiles))
for nonValid in listNonValidFiles:
    print("   - %sMB Mod: %s %s" %(rpad(round((nonValid[1]/(1000.0*1000.0)),1),5),nonValid[2], nonValid[0]))
print

if len(listLargeFiles):
    print("\nLARGE (core) file(s) > 0.5MB....:")
    for largefile in listLargeFiles:
        print("   - %sMB Mod: %s %s" %(rpad(round((largefile[1]/(1000.0*1000.0)),1),5),largefile[2], largefile[0]))
    print


def tell_me_if_dropbox_folder_exists():

    userHomeProperty = System.getProperty("UserHome", System.getProperty("user.home", "."))
    baseFolder = File(userHomeProperty, "Dropbox")
    dropbox = File(baseFolder, ".moneydancesync")

    # If Dropbox folder does not exist then do nothing
    if baseFolder.exists() and baseFolder.isDirectory() and dropbox.exists() and dropbox.isDirectory():
        return dropbox.getCanonicalPath()

    return False


def find_other_datasets():
    output = ""
    output+=("\nQUICK SEARCH FOR OTHER DATASETS:\n"
             "---------------------------------\n")

    md_extn = ".moneydance"
    md_archive = ".moneydancearchive"

    saveFiles={}
    saveArchiveFiles={}

    myDataset = moneydance_data.getRootFolder().getCanonicalPath()

    internalDir = Common.getDocumentsDirectory().getCanonicalPath()
    dirList =  os.listdir(internalDir)
    for fileName in dirList:
        fullPath = os.path.join(internalDir,fileName)
        if fileName.endswith(md_extn):
            saveFiles[fullPath] = True
        elif fileName.endswith(md_archive):
            saveArchiveFiles[fullPath] = True
    del internalDir, dirList

    parentofDataset = moneydance_data.getRootFolder().getParent()
    if os.path.exists(parentofDataset):
        dirList =  os.listdir(parentofDataset)
        for fileName in dirList:
            fullPath = os.path.join(parentofDataset,fileName)
            if fileName.endswith(md_extn):
                saveFiles[fullPath] = True
            elif fileName.endswith(md_archive):
                saveArchiveFiles[fullPath] = True
        del dirList
    del parentofDataset

    externalFiles = AccountBookUtil.getExternalAccountBooks()
    for wrapper in externalFiles:
        saveFiles[wrapper.getBook().getRootFolder().getCanonicalPath()] = True
        externalDir = wrapper.getBook().getRootFolder().getParent()
        if os.path.exists(externalDir):
            dirList =  os.listdir(externalDir)
            for fileName in dirList:
                fullPath = os.path.join(externalDir,fileName)
                if fileName.endswith(md_extn):
                    saveFiles[fullPath] = True
                elif fileName.endswith(md_archive):
                    saveArchiveFiles[fullPath] = True
            del dirList
    del externalFiles

    for backupLocation in [ FileUtils.getBackupDir(moneydance.getPreferences()).getCanonicalPath(),
                            moneydance_ui.getPreferences().getSetting("backup.location",""),
                            moneydance_ui.getPreferences().getSetting("backup.last_saved",""),
                            moneydance_ui.getPreferences().getSetting("backup.last_browsed","")]:
        if backupLocation is not None and backupLocation != "" and os.path.exists(backupLocation):
            dirList =  os.listdir(backupLocation)
            for fileName in dirList:
                fullPath = os.path.join(backupLocation,fileName)
                if fileName.endswith(md_extn):
                    if saveFiles.get(fileName) is not None:
                        saveFiles[fullPath] = True
                elif fileName.endswith(md_archive):
                    saveArchiveFiles[fullPath] = True
            del dirList
    del backupLocation

    saveFiles[myDataset] = None

    listTheFiles=sorted(saveFiles.keys())
    listTheArchiveFiles=sorted(saveArchiveFiles.keys())

    for _f in listTheFiles:
        if saveFiles[_f] is not None:
            output+=("Dataset: Mod: %s %s\n"
                     % (pad(datetime.datetime.fromtimestamp(os.path.getmtime(_f)).strftime('%Y-%m-%d %H:%M:%S'), 11), _f))
    del listTheFiles

    output+=("\nBACKUP FILES\n"
             "-------------\n")

    for _f in listTheArchiveFiles:
        if saveArchiveFiles[_f] is not None:
            output+=("Archive: Mod: %s %s\n"
                     % (pad(datetime.datetime.fromtimestamp(os.path.getmtime(_f)).strftime('%Y-%m-%d %H:%M:%S'), 11), _f))
    del listTheArchiveFiles

    output+=("\nSYNC FOLDERS FOUND:\n"
             "---------------------\n")

    saveSyncFolder=None
    try:
        syncMethods = SyncFolderUtil.getAvailableFolderConfigurers(moneydance_ui, moneydance_ui.getCurrentAccounts())
        syncMethod = SyncFolderUtil.getConfigurerForFile(moneydance_ui, moneydance_ui.getCurrentAccounts(), syncMethods)

        if syncMethod is not None and syncMethod.getSyncFolder() is not None:
            # noinspection PyUnresolvedReferences
            syncBaseFolder = syncMethod.getSyncFolder().getSyncBaseFolder()

            saveSyncFolder = syncBaseFolder.getCanonicalPath()
            dirList =  os.listdir(saveSyncFolder)

            for fileName in dirList:
                fullPath = os.path.join(saveSyncFolder,fileName)
                if len(fileName)>32:
                    output+=("Sync Folder: %s %s\n"
                             % (pad(datetime.datetime.fromtimestamp(os.path.getmtime(fullPath)).strftime('%Y-%m-%d %H:%M:%S'), 11), fullPath))
        else:
            output+=("<NONE FOUND>\n")

        del syncMethod, syncMethods
    except:
        pass

    dropboxPath = tell_me_if_dropbox_folder_exists()
    if dropboxPath and dropboxPath is not None and dropboxPath != saveSyncFolder:

        output+=("\nDROPBOX FOLDERS FOUND:\n"
                 "-----------------------\n")
        dirList =  os.listdir(dropboxPath)

        for fileName in dirList:
            fullPath = os.path.join(dropboxPath,fileName)
            if len(fileName)>32:
                output+=("Dropbox Sync Folder: %s %s\n"
                         % (pad(datetime.datetime.fromtimestamp(os.path.getmtime(fullPath)).strftime('%Y-%m-%d %H:%M:%S'), 11), fullPath))
    del dropboxPath

    output+="\n\n(for a more extensive search please use Toolbox - Find my Datasets and Backups button\n\n"

    return output

def count_database_objects():
    output = ""
    output+=("\nDATABASE OBJECT COUNT        (count) (est.size KBs):\n"
             "-----------------------------------------------------\n")
    foundStrange=0
    types={}

    onlineTxns=0
    onlineTxnsCharacters=0
    onlinePayees=0
    onlinePayments=0

    for mdItem in moneydance_data.getSyncer().getSyncedDocument().allItems():
        if isinstance(mdItem, MoneydanceSyncableItem):

            if isinstance(mdItem, OnlineTxnList):
                onlineTxns      +=mdItem.getTxnCount()
                for olKey in mdItem.getParameterKeys():
                    onlineTxnsCharacters += len(olKey)
                    onlineTxnsCharacters += len(mdItem.getParameter(olKey))

            if isinstance(mdItem, OnlinePayeeList):     onlinePayees    +=mdItem.getPayeeCount()
            if isinstance(mdItem, OnlinePaymentList):   onlinePayments  +=mdItem.getPaymentCount()

            getTheSavedData = types.get(mdItem.getParameter("obj_type", "UNKNOWN"))
            if getTheSavedData is not None:
                x,theLength = getTheSavedData
            else:
                x = 0
                theLength = 0

            theSyncInfo = mdItem.getSyncInfo()
            theDescription = theSyncInfo.toMultilineHumanReadableString()  # format is "key: data\n" but file is '&key=data'
            theLength += len( ("mod.%s:" %(mdItem.getParameter("obj_type",""))) )
            theLength += len(theDescription)
            theLength -= len(mdItem.getParameterKeys())  # remove the number of "\n"s

            types[mdItem.getParameter("obj_type", "UNKNOWN")] = [x+1, theLength]
        else:
            foundStrange+=1
    i=0
    charCount=0
    for x in types.keys():
        i+=types[x][0]
        charCount+=types[x][1]
        extraText = ""
        if x == "oltxns":
            if onlineTxns:
                extraText = "(containing %s Online Txns consuming %s KBs)" %(onlineTxns, round(onlineTxnsCharacters/1000.0,1))
        elif x == "olpayees":
            if onlinePayees:
                extraText = "(containing %s Online Payees)" %(onlinePayees)
        elif x == "olpmts":
            if onlinePayments:
                extraText = "(containing %s Online Payments)" %(onlinePayments)

        output+=("Object: %s %s   %s %s\n" %(pad(x,15),rpad(types[x][0],12),rpad(round(types[x][1] / (1000.0),1),12), extraText))

    if foundStrange:
        output+=("\n@@ I also found %s non Moneydance Syncable Items?! Why? @@\n" %(foundStrange))
    output+=(" ==========\n TOTAL:                 %s   %s\n\n" %(rpad(i,12),rpad(round(charCount/(1000.0),1),12)))
    del types
    del foundStrange
    return output


print
print count_database_objects()
print
print find_other_datasets()
print

myPrint("B", "StuWareSoftSystems - ", myScriptName, " script ending......")

if not i_am_an_extension_so_run_headless: print(scriptExit)

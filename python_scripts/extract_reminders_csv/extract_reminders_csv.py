#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# extract_reminders_csv.py (build: 1008)

###############################################################################
# MIT License
#
# Copyright (c) 2020 Stuart Beesley - StuWareSoftSystems
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

# Thanks to allangdavies adgetreminderstocsv.py for the original code and concept(s)
# Further thanks to Mike Enoch (April 2017) and his "swing example-moneydance_edit_reminders.py" script (used for my education)

# Stuart Beesley Created 2020-06-18 tested on MacOS - MD2019.4 onwards - StuWareSoftSystems....
# v3 upgraded script to ask for extract filename and extract date formats in pop up windows; also fix amounts less than 1
# v4 major upgrade to display results first and allow CSV creation.. Functions upgraded with latest learnings....
# v4a - small tweak to change default dateformat if parameter invalid; also switched to  use MD's decimal point setting
# v4b - small tweak to parameter field (cosmetic); added BOM to csv file to help Excel open UTF8 file with double-click (changed open() to 'w' from 'wb')
# v4c - Cosmetic tweak to display message; catch pickle.load() error (when restored dataset).
# v4d - Reverting to open() 'wb' - fix Excel CRLF double line on Windows issue
# v4e - Convert pickle file to unencrypted
# v4f - Slight change to myParameters; changed __file__ usage; code cleanup; version change

# Build: 1000 - IntelliJ code cleanup; made Extension ready; Extract file without waiting; refresh bits with common code - no functional changes
# Build: 1000 - no functional changes; Added code fix for extension runtime to set moneydance variables (if not set)
# Build: 1000 - all print functions changed to work headless; added some popup warnings...; stream-lined common code; renamed script dropping _to_
# Build: 1000 - column widths now save; optional parameter whether to write BOM to export file; added datetime to console log
# Build: 1001 - Added About menu (cosmetic only)
# Build: 1002 - Cosmetic change to put main window in centre of screen
# Build: 1002 - Enhanced MyPrint to catch unicode utf-8 encode/decode errors
# Build: 1003 - fixed raise(Exception) clauses ;->
# Build: 1004 - Updated common codeset, leverage Moneydance fonts
# Build: 1005 - Removed TxnSortOrder from common code
# Build: 1005 - Fix for Jython 2.7.1 where csv.writer expects a 1-byte string delimiter, not unicode....
# Build: 1005 - Write parameters to csv extract; added fake JFrame() for icons...;moved parameter save earlier
# Build: 1006 - Renames of REPO, Moneydance, url etc
# Build: 1007 - Moved parameter save back to last to catch column changes
# Build: 1008 - Tweak to common code (Popups); leverage moneydance window sizes too; fix row height for odd fonts..
# Build: 1008 - Changed parameter screen to use JCheckBox and JComboBox

# Displays Moneydance reminders and allows extract to a csv file (compatible with Excel)

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
from javax.swing import JTextField, JPasswordField, Box, UIManager, JTable, JCheckBox
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
						InputStreamReader, Dialog, JTable, BorderLayout, Double, InvestUtil,
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
# END COMMON GLOBALS ###################################################################################################

# SET THESE VARIABLES FOR ALL SCRIPTS ##################################################################################
version_build = "1008"           																					# noqa
myScriptName = "extract_reminders_csv.py(Extension)"																# noqa
debug = False                                                                                                       # noqa
myParameters = {}                                                                                                   # noqa
_resetParameters = False                                                                                            # noqa
lPickle_version_warning = False                                                                                     # noqa
lIamAMac = False                                                                                                    # noqa
lGlobalErrorDetected = False																						# noqa
# END SET THESE VARIABLES FOR ALL SCRIPTS ##############################################################################

# >>> THIS SCRIPT'S IMPORTS ############################################################################################
from com.moneydance.apps.md.view.gui import EditRemindersWindow
from java.awt.event import MouseAdapter
from java.util import Comparator
from javax.swing import SortOrder, ListSelectionModel
from javax.swing.table import DefaultTableCellRenderer, DefaultTableModel, TableRowSorter
from javax.swing.border import CompoundBorder, MatteBorder
from javax.swing.event import TableColumnModelListener
from java.lang import String, Number
# >>> END THIS SCRIPT'S IMPORTS ########################################################################################

# >>> THIS SCRIPT'S GLOBALS ############################################################################################

# Saved to parameters file
global __extract_reminders_csv, userdateformat, lStripASCII, csvDelimiter, _column_widths_ERTC, scriptpath
global lWriteBOMToExportFile_SWSS

# Other used by this program
global csvfilename, lDisplayOnly
global baseCurrency, sdf, csvlines, csvheaderline, headerFormats, extract_reminders_csv_fake_frame_
global table, focus, row, extract_reminders_csv_frame_, scrollpane, EditedReminderCheck, ReminderTable_Count, ExtractDetails_Count
# >>> END THIS SCRIPT'S GLOBALS ############################################################################################

# Set programmatic defaults/parameters for filters HERE.... Saved Parameters will override these now
# NOTE: You  can override in the pop-up screen
userdateformat = "%Y/%m/%d"																							# noqa
lStripASCII = False																									# noqa
csvDelimiter = ","																									# noqa
scriptpath = ""																										# noqa
_column_widths_ERTC = []                                                                                          	# noqa
lWriteBOMToExportFile_SWSS = True                                                                                   # noqa
extract_reminders_csv_fake_frame_ = None																			# noqa
extract_filename="extract_reminders.csv"
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

Visit: https://yogi1967.github.io/MoneydancePythonScripts/ (Author's site)
----------------------------------------------------------------------------------------------------------------------
""" %myScriptName

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


myPrint("B", "StuWareSoftSystems...")
myPrint("B", myScriptName, ": Python Script Initialising.......", "Build:", version_build)

def is_moneydance_loaded_properly():
	global debug

	if debug or moneydance_data is None or moneydance_ui is None:
		for theClass in ["moneydance",moneydance], ["moneydance_ui",moneydance_ui], ["moneydance_data",moneydance_data]:
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
		if debug: myPrint("B","Success setting Font set to Moneydance code: %s" %theFont)
	except:
		theFont = Font("monospaced", Font.PLAIN, 15)
		if debug: myPrint("B","Failed to Font set to Moneydance code - So using: %s" %theFont)

	return theFont

def getTheSetting(what):
	x = moneydance_ui.getPreferences().getSetting(what, None)
	if not x or x == "": return None
	return what + ": " + str(x)

def get_home_dir():
	homeDir = None

	# noinspection PyBroadException
	try:
		if Platform.isOSX():
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

	if not homeDir: homeDir = "?"
	return homeDir

def getDecimalPoint(lGetPoint=False, lGetGrouping=False):
	global debug

	decimalFormat = DecimalFormat.getInstance()
	# noinspection PyUnresolvedReferences
	decimalSymbols = decimalFormat.getDecimalFormatSymbols()

	if not lGetGrouping: lGetPoint = True
	if lGetGrouping and lGetPoint: return "error"

	if lGetPoint:
		_decimalCharSep = decimalSymbols.getDecimalSeparator()
		myPrint("DB","Decimal Point Character:", _decimalCharSep)
		return _decimalCharSep

	if lGetGrouping:
		_groupingCharSep = decimalSymbols.getGroupingSeparator()
		myPrint("DB","Grouping Separator Character:", _groupingCharSep)
		return _groupingCharSep

	return "error"


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
		self._popup_d.getRootPane().getActionMap().put("close-window", self.CancelButtonAction(self._popup_d, self.fakeJFrame,self.lResult))
		self._popup_d.addWindowListener(self.WindowListener(self._popup_d, self.fakeJFrame,self.lResult))

		if (not Platform.isMac()):
			# moneydance_ui.getImages()
			self._popup_d.setIconImage(MDImages.getImage(moneydance_ui.getMain().getSourceInformation().getIconResource()))

		displayJText = JTextArea(self.theMessage)
		# displayJText.setFont( getMonoFont() )
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


# >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
def load_StuWareSoftSystems_parameters_into_memory():
	global debug, myParameters, lPickle_version_warning, version_build

	# >>> THESE ARE THIS SCRIPT's PARAMETERS TO LOAD
	global __extract_reminders_csv, lStripASCII, csvDelimiter, scriptpath, userdateformat, _column_widths_ERTC
	global lWriteBOMToExportFile_SWSS                                                                                  # noqa

	myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )
	myPrint("DB", "Loading variables into memory...")

	if myParameters is None: myParameters = {}

	if myParameters.get("__extract_reminders_csv") is not None:
		__extract_reminders_csv = myParameters.get("__extract_reminders_csv")
	elif myParameters.get("__extract_reminders_to_csv") is not None:					# Get old(er) key then delete it
		__extract_reminders_csv = myParameters.get("__extract_reminders_to_csv")
	if myParameters.get("__extract_reminders_to_csv") is not None:
		myParameters.pop("__extract_reminders_to_csv", None)  # Old variable - not used - delete from parameter file

	if myParameters.get("userdateformat") is not None: userdateformat = myParameters.get("userdateformat")
	if myParameters.get("lStripASCII") is not None: lStripASCII = myParameters.get("lStripASCII")
	if myParameters.get("csvDelimiter") is not None: csvDelimiter = myParameters.get("csvDelimiter")
	if myParameters.get("_column_widths_ERTC") is not None: _column_widths_ERTC = myParameters.get("_column_widths_ERTC")
	if myParameters.get("lWriteBOMToExportFile_SWSS") is not None: lWriteBOMToExportFile_SWSS = myParameters.get("lWriteBOMToExportFile_SWSS")                                                                                  # noqa

	if myParameters.get("scriptpath") is not None:
		scriptpath = myParameters.get("scriptpath")
		if not os.path.isdir(scriptpath):
			myPrint("B", "Warning: loaded parameter scriptpath does not appear to be a valid directory:", scriptpath, "will ignore")
			scriptpath = ""

	myPrint("DB","myParameters{} set into memory (as variables).....")

	return

# >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
def dump_StuWareSoftSystems_parameters_from_memory():
	global debug, myParameters, lPickle_version_warning, version_build
	global lWriteBOMToExportFile_SWSS                                                                                  # noqa

	# >>> THESE ARE THIS SCRIPT's PARAMETERS TO SAVE
	global __extract_reminders_csv, lStripASCII, csvDelimiter, scriptpath, lDisplayOnly, userdateformat, _column_widths_ERTC

	myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )

	# NOTE: Parameters were loaded earlier on... Preserve existing, and update any used ones...
	# (i.e. other StuWareSoftSystems programs might be sharing the same file)

	if myParameters is None: myParameters = {}

	myParameters["__extract_reminders_csv"] = version_build
	myParameters["userdateformat"] = userdateformat
	myParameters["lStripASCII"] = lStripASCII
	myParameters["csvDelimiter"] = csvDelimiter
	myParameters["_column_widths_ERTC"] = _column_widths_ERTC
	myParameters["lWriteBOMToExportFile_SWSS"] = lWriteBOMToExportFile_SWSS

	if not lDisplayOnly and scriptpath != "" and os.path.isdir(scriptpath):
		myParameters["scriptpath"] = scriptpath

	myPrint("DB","variables dumped from memory back into myParameters{}.....")

	return


get_StuWareSoftSystems_parameters_from_file()
myPrint("DB", "DEBUG IS ON..")
# END ALL CODE COPY HERE ###############################################################################################

# Create fake JFrame() so that all popups have correct Moneydance Icons etc
extract_reminders_csv_fake_frame_ = JFrame()
if (not Platform.isMac()):
	moneydance_ui.getImages()
	extract_reminders_csv_fake_frame_.setIconImage(MDImages.getImage(moneydance_ui.getMain().getSourceInformation().getIconResource()))
extract_reminders_csv_fake_frame_.setUndecorated(True)
extract_reminders_csv_fake_frame_.setVisible(False)
extract_reminders_csv_fake_frame_.setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE)

class CloseAboutAction(AbstractAction):
	# noinspection PyMethodMayBeStatic
	# noinspection PyUnusedLocal

	def __init__(self, theFrame):
		self.theFrame = theFrame

	def actionPerformed(self, event):
		global debug
		myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event:", event)

		self.theFrame.dispose()

def about_this_script():
	global debug, scriptExit

	myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

	# noinspection PyUnresolvedReferences
	about_d = JDialog(extract_reminders_csv_frame_, "About", Dialog.ModalityType.MODELESS)

	shortcut = Toolkit.getDefaultToolkit().getMenuShortcutKeyMaskEx()
	about_d.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_W, shortcut), "close-window")
	about_d.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_F4, shortcut), "close-window")

	about_d.getRootPane().getActionMap().put("close-window", CloseAboutAction(about_d))

	about_d.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE)  # The CloseAction() and WindowListener() will handle dispose() - else change back to DISPOSE_ON_CLOSE

	if (not Platform.isMac()):
		# moneydance_ui.getImages()
		about_d.setIconImage(MDImages.getImage(moneydance_ui.getMain().getSourceInformation().getIconResource()))

	aboutPanel=JPanel()
	aboutPanel.setLayout(FlowLayout(FlowLayout.LEFT))
	aboutPanel.setPreferredSize(Dimension(1070, 400))

	_label1 = JLabel(pad("Author: Stuart Beesley", 800))
	_label1.setForeground(Color.BLUE)
	aboutPanel.add(_label1)

	_label2 = JLabel(pad("StuWareSoftSystems (2020)", 800))
	_label2.setForeground(Color.BLUE)
	aboutPanel.add(_label2)

	displayString=scriptExit
	displayJText = JTextArea(displayString)
	displayJText.setFont( getMonoFont() )
	displayJText.setEditable(False)
	# displayJText.setCaretPosition(0)
	displayJText.setLineWrap(False)
	displayJText.setWrapStyleWord(False)
	displayJText.setMargin(Insets(8, 8, 8, 8))
	# displayJText.setBackground((mdGUI.getColors()).defaultBackground)
	# displayJText.setForeground((mdGUI.getColors()).defaultTextForeground)

	aboutPanel.add(displayJText)

	about_d.add(aboutPanel)

	about_d.pack()
	about_d.setLocationRelativeTo(None)
	about_d.setVisible(True)
	return


class DoTheMenu(AbstractAction):

	def __init__(self, menu, callingClass=None):
		self.menu = menu
		self.callingClass = callingClass

	def actionPerformed(self, event):																				# noqa
		global extract_reminders_csv_frame_, debug

		myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

		if event.getActionCommand() == "About":
			about_this_script()

		myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
		return


def terminate_script():
	global debug, extract_reminders_csv_frame_, lDisplayOnly, lGlobalErrorDetected

	myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

	try:
		save_StuWareSoftSystems_parameters_to_file()
	except:
		myPrint("B", "Error - failed to save parameters to pickle file...!")
		dump_sys_error_to_md_console_and_errorlog()

	if not lDisplayOnly:
		try:
			ExportDataToFile()
			if not lGlobalErrorDetected:
				myPopupInformationBox(extract_reminders_csv_frame_, "Your extract has been created as requested", myScriptName)
				try:
					helper = moneydance.getPlatformHelper()
					helper.openDirectory(File(csvfilename))
				except:
					pass
		except:
			lGlobalErrorDetected = True
			myPopupInformationBox(extract_reminders_csv_frame_, "ERROR WHILST CREATING EXPORT! Review Console Log", myScriptName)
			dump_sys_error_to_md_console_and_errorlog()

	if not i_am_an_extension_so_run_headless: print(scriptExit)

	extract_reminders_csv_frame_.dispose()
	return


csvfilename = None

if decimalCharSep != "." and csvDelimiter == ",": csvDelimiter = ";"  # Override for EU countries or where decimal point is actually a comma...
myPrint("DB", "Decimal point:", decimalCharSep, "Grouping Separator", groupingCharSep, "CSV Delimiter set to:", csvDelimiter)

sdf = SimpleDateFormat("dd/MM/yyyy")

dateStrings=["dd/mm/yyyy", "mm/dd/yyyy", "yyyy/mm/dd", "yyyymmdd"]
# 1=dd/mm/yyyy, 2=mm/dd/yyyy, 3=yyyy/mm/dd, 4=yyyymmdd
label1 = JLabel("Select Output Date Format (default yyyy/mm/dd):")
user_dateformat = JComboBox(dateStrings)

if userdateformat == "%d/%m/%Y": user_dateformat.setSelectedItem("dd/mm/yyyy")
elif userdateformat == "%m/%d/%Y": user_dateformat.setSelectedItem("mm/dd/yyyy")
elif userdateformat == "%Y%m%d": user_dateformat.setSelectedItem("yyyymmdd")
else: user_dateformat.setSelectedItem("yyyy/mm/dd")

label2 = JLabel("Strip non ASCII characters from CSV export?")
user_selectStripASCII = JCheckBox("", lStripASCII)

delimStrings = [";","|",","]
label3 = JLabel("Change CSV Export Delimiter from default to: ';|,'")
user_selectDELIMITER = JComboBox(delimStrings)
user_selectDELIMITER.setSelectedItem(csvDelimiter)

labelBOM = JLabel("Write BOM (Byte Order Mark) to file (helps Excel open files)?")
user_selectBOM = JCheckBox("", lWriteBOMToExportFile_SWSS)

label4 = JLabel("Turn DEBUG Verbose messages on?")
user_selectDEBUG = JCheckBox("", debug)


userFilters = JPanel(GridLayout(0, 2))
userFilters.add(label1)
userFilters.add(user_dateformat)
userFilters.add(label2)
userFilters.add(user_selectStripASCII)
userFilters.add(label3)
userFilters.add(user_selectDELIMITER)
userFilters.add(labelBOM)
userFilters.add(user_selectBOM)
userFilters.add(label4)
userFilters.add(user_selectDEBUG)

lExit = False
lDisplayOnly = False

options = ["Abort", "Display & CSV Export", "Display Only"]
userAction = (JOptionPane.showOptionDialog( extract_reminders_csv_fake_frame_,
											userFilters,
											"%s(build: %s) Set Script Parameters...." %(myScriptName, version_build),
											JOptionPane.OK_CANCEL_OPTION,
											JOptionPane.QUESTION_MESSAGE,
											moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
											options,
											options[2])
											)
if userAction == 1:  # Display & Export
	myPrint("DB", "Display and export chosen")
	lDisplayOnly = False
elif userAction == 2:  # Display Only
	lDisplayOnly = True
	myPrint("DB", "Display only with no export chosen")
else:
	# Abort
	myPrint("DB", "User Cancelled Parameter selection.. Will abort..")
	myPopupInformationBox(extract_reminders_csv_fake_frame_, "User Cancelled Parameter selection.. Will abort..", "PARAMETERS")
	lDisplayOnly = False
	lExit = True

if not lExit:

	debug = user_selectDEBUG.isSelected()
	myPrint("DB", "DEBUG turned on")

	if debug:
		myPrint("DB","Parameters Captured",
			"User Date Format:", user_dateformat.getSelectedItem(),
			"Strip ASCII:", user_selectStripASCII.isSelected(),
			"Write BOM to file:", user_selectBOM.isSelected(),
			"Verbose Debug Messages: ", user_selectDEBUG.isSelected(),
			"CSV File Delimiter:", user_selectDELIMITER.getSelectedItem())
	# endif

	if user_dateformat.getSelectedItem() == "dd/mm/yyyy": userdateformat = "%d/%m/%Y"
	elif user_dateformat.getSelectedItem() == "mm/dd/yyyy": userdateformat = "%m/%d/%Y"
	elif user_dateformat.getSelectedItem() == "yyyy/mm/dd": userdateformat = "%Y/%m/%d"
	elif user_dateformat.getSelectedItem() == "yyyymmdd": userdateformat = "%Y%m%d"
	else:
		# PROBLEM /  default
		userdateformat = "%Y/%m/%d"

	lStripASCII = user_selectStripASCII.isSelected()

	csvDelimiter = user_selectDELIMITER.getSelectedItem()
	if csvDelimiter == "" or (not (csvDelimiter in ";|,")):
		myPrint("DB", "Invalid Delimiter:", csvDelimiter, "selected. Overriding with:','")
		csvDelimiter = ","
	if decimalCharSep == csvDelimiter:
		myPrint("DB", "WARNING: The CSV file delimiter:", csvDelimiter, "cannot be the same as your decimal point character:", decimalCharSep, " - Proceeding without file export!!")
		lDisplayOnly = True

	lWriteBOMToExportFile_SWSS = user_selectBOM.isSelected()

	myPrint("B", "User Parameters...")
	myPrint("B", "user date format....:", userdateformat)

	# Now get the export filename
	csvfilename = None

	if not lDisplayOnly:  # i.e. we have asked for a file export - so get the filename

		if lStripASCII:
			myPrint("DB", "Will strip non-ASCII characters - e.g. Currency symbols from output file...", " Using Delimiter:", csvDelimiter)
		else:
			myPrint("DB", "Non-ASCII characters will not be stripped from file: ", " Using Delimiter:", csvDelimiter)

		if lWriteBOMToExportFile_SWSS:
			myPrint("B", "Script will add a BOM (Byte Order Mark) to front of the extracted file...")
		else:
			myPrint("B", "No BOM (Byte Order Mark) will be added to the extracted file...")


		def grabTheFile():
			global debug, lDisplayOnly, csvfilename, lIamAMac, scriptpath, myScriptName
			myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

			if scriptpath == "" or scriptpath is None:  # No parameter saved / loaded from disk
				scriptpath = myDir()

			myPrint("DB", "Default file export output path is....:", scriptpath)

			csvfilename = ""
			if lIamAMac:
				myPrint("D", "MacOS X detected: Therefore I will run FileDialog with no extension filters to get filename....")
				# jFileChooser hangs on Mac when using file extension filters, also looks rubbish. So using Mac(ish)GUI

				System.setProperty("com.apple.macos.use-file-dialog-packages","true")  # In theory prevents access to app file structure (but doesnt seem to work)
				System.setProperty("apple.awt.fileDialogForDirectories", "false")

			filename = FileDialog(extract_reminders_csv_fake_frame_, "Select/Create CSV file for extract (CANCEL=NO EXPORT)")
			filename.setMultipleMode(False)
			filename.setMode(FileDialog.SAVE)
			filename.setFile(extract_filename)
			if (scriptpath is not None and scriptpath != ""): filename.setDirectory(scriptpath)

			# Copied from MD code... File filters only work on non Macs (or Macs below certain versions)
			if (not Platform.isOSX() or not Platform.isOSXVersionAtLeast("10.13")):
				extfilter = ExtFilenameFilter("csv")
				filename.setFilenameFilter(extfilter)  # I'm not actually sure this works...?

			filename.setVisible(True)

			csvfilename = filename.getFile()

			if (csvfilename is None) or csvfilename == "":
				lDisplayOnly = True
				csvfilename = None
				myPrint("B", "User chose to cancel or no file selected >>  So no Extract will be performed... ")
				myPopupInformationBox(extract_reminders_csv_fake_frame_, "User chose to cancel or no file selected >>  So no Extract will be performed... ","FILE SELECTION")
			elif str(csvfilename).endswith(".moneydance"):
				myPrint("B", "User selected file:", csvfilename)
				myPrint("B", "Sorry - User chose to use .moneydance extension - I will not allow it!... So no Extract will be performed...")
				myPopupInformationBox(extract_reminders_csv_fake_frame_, "Sorry - User chose to use .moneydance extension - I will not allow it!... So no Extract will be performed...","FILE SELECTION")
				lDisplayOnly = True
				csvfilename = None
			elif ".moneydance" in filename.getDirectory():
				myPrint("B", "User selected file:", filename.getDirectory(), csvfilename)
				myPrint("B", "Sorry - FileDialog() User chose to save file in .moneydance location. NOT Good practice so I will not allow it!... So no Extract will be performed...")
				myPopupInformationBox(extract_reminders_csv_fake_frame_, "Sorry - FileDialog() User chose to save file in .moneydance location. NOT Good practice so I will not allow it!... So no Extract will be performed...","FILE SELECTION")
				lDisplayOnly = True
				csvfilename = None
			else:
				csvfilename = os.path.join(filename.getDirectory(), filename.getFile())
				scriptpath = str(filename.getDirectory())

			if not lDisplayOnly:
				if os.path.exists(csvfilename) and os.path.isfile(csvfilename):
					myPrint("DB", "WARNING: file exists,but assuming user said OK to overwrite..")

			if not lDisplayOnly:
				if check_file_writable(csvfilename):
					if lStripASCII:
						myPrint("B", 'Will display Reminders and then extract to file: ', csvfilename, "(NOTE: Should drop non utf8 characters...)")
					else:
						myPrint("B", 'Will display Reminders and then extract to file: ', csvfilename, "...")
					scriptpath = os.path.dirname(csvfilename)
				else:
					myPrint("B", "Sorry - I just checked and you do not have permissions to create this file:", csvfilename)
					myPopupInformationBox(extract_reminders_csv_fake_frame_,"Sorry - I just checked and you do not have permissions to create this file: %s" %csvfilename,"FILE SELECTION")
					csvfilename=""
					lDisplayOnly = True

			return


		# enddef

		if not lDisplayOnly: grabTheFile()
	else:
		pass
	# endif

	if csvfilename is None:
		lDisplayOnly = True
		myPrint("B","No Export will be performed")

	# save here in case script crashes....
	save_StuWareSoftSystems_parameters_to_file()

	# Moneydance dates  are int yyyymmddd - convert to locale date string for CSV format
	def dateoutput(dateinput, theformat):

		if dateinput == "EXPIRED": _dateoutput = dateinput
		elif dateinput == "": _dateoutput = ""
		elif dateinput == 0: _dateoutput = ""
		elif dateinput == "0": _dateoutput = ""
		else:
			dateasdate = datetime.datetime.strptime(str(dateinput), "%Y%m%d")  # Convert to Date field
			_dateoutput = dateasdate.strftime(theformat)

		return _dateoutput


	def build_the_data_file(ind):
		global sdf, userdateformat, csvlines, csvheaderline, myScriptName, baseCurrency, headerFormats
		global debug, ExtractDetails_Count

		ExtractDetails_Count += 1

		myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", ind, " - On iteration/call: ", ExtractDetails_Count)

		# ind == 1 means that this is a repeat call, so the table should be refreshed

		root = moneydance.getCurrentAccountBook()

		baseCurrency = moneydance_data.getCurrencies().getBaseType()

		rems = root.getReminders().getAllReminders()

		if rems.size() < 1:
			return False

		myPrint("B", 'Success: read ', rems.size(), 'reminders')
		print
		csvheaderline = [
						"Number#",
						"NextDue",
						"ReminderType",
						"Frequency",
						"AutoCommitDays",
						"LastAcknowledged",
						"FirstDate",
						"EndDate",
						"ReminderDecription",
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

		# Read each reminder and create a csv line for each in the csvlines array
		csvlines = []  # Set up an ampty array

		for index in range(0, int(rems.size())):
			rem = rems[index]  # Get the reminder

			remtype = rem.getReminderType()  # NOTE or TRANSACTION
			desc = rem.getDescription().replace(",", " ")  # remove commas to keep csv format happy
			memo = str(rem.getMemo()).replace(",", " ").strip()  # remove commas to keep csv format happy
			memo = str(memo).replace("\n", "*").strip()  # remove newlines to keep csv format happy

			myPrint("P", "Reminder: ", index + 1, rem.getDescription())  # Name of Reminder

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

			if len(
					remfreq) < 1 or countfreqs == 0:         remfreq = '!ERROR! NO ACTUAL FREQUENCY OPTIONS SET PROPERLY ' + remfreq
			if countfreqs > 1: remfreq = "**MULTI** " + remfreq

			lastdate = rem.getLastDateInt()
			if lastdate < 1:  # Detect if an enddate is set
				remdate = str(rem.getNextOccurance(20991231))  # Use cutoff  far into the future
			else:        remdate = str(rem.getNextOccurance(rem.getLastDateInt()))  # Stop at enddate

			if lastdate < 1: lastdate = ''

			if remdate == '0': remdate = "EXPIRED"

			lastack = rem.getDateAcknowledgedInt()
			if lastack == 0 or lastack == 19700101: lastack = ''

			auto = rem.getAutoCommitDays()
			if auto >= 0:    auto = 'YES: (' + str(auto) + ' days before scheduled)'
			else:            auto = 'NO'

			if str(remtype) == 'NOTE':
				csvline = []
				csvline.append(index + 1)
				csvline.append(dateoutput(remdate, userdateformat))
				csvline.append(str(rem.getReminderType()))
				csvline.append(remfreq)
				csvline.append(auto)
				csvline.append(dateoutput(lastack, userdateformat))
				csvline.append(dateoutput(rem.getInitialDateInt(), userdateformat))
				csvline.append(dateoutput(lastdate, userdateformat))
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
				csvlines.append(csvline)

			elif str(remtype) == 'TRANSACTION':
				txnparent = rem.getTransaction()
				amount = baseCurrency.getDoubleValue(txnparent.getValue())

				for index2 in range(0, int(txnparent.getOtherTxnCount())):
					splitdesc = txnparent.getOtherTxn(index2).getDescription().replace(","," ")  # remove commas to keep csv format happy
					splitmemo = txnparent.getMemo().replace(",", " ")  # remove commas to keep csv format happy
					maindesc = txnparent.getDescription().replace(",", " ").strip()

					if index2 > 0: amount = ''  # Don't repeat the new amount on subsequent split lines (so you can total column). The split amount will be correct

					stripacct = str(txnparent.getAccount()).replace(",",
																	" ").strip()  # remove commas to keep csv format happy
					stripcat = str(txnparent.getOtherTxn(index2).getAccount()).replace(","," ").strip()  # remove commas to keep csv format happy

					csvline = []
					csvline.append(index + 1)
					csvline.append(dateoutput(remdate, userdateformat))
					csvline.append(str(rem.getReminderType()))
					csvline.append(remfreq)
					csvline.append(auto)
					csvline.append(dateoutput(lastack, userdateformat))
					csvline.append(dateoutput(rem.getInitialDateInt(), userdateformat))
					csvline.append(dateoutput(lastdate, userdateformat))
					csvline.append(desc)
					csvline.append((amount))
					csvline.append(txnparent.getTransferType())
					csvline.append(stripacct)
					csvline.append(maindesc)
					csvline.append(str(index + 1) + '.' + str(index2 + 1))
					csvline.append(baseCurrency.getDoubleValue(txnparent.getOtherTxn(index2).getValue()) * -1)
					csvline.append(stripcat)
					csvline.append(splitdesc)
					csvline.append(splitmemo)
					csvlines.append(csvline)

			index += 1

		ReminderTable(csvlines, ind)

		myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name)
		ExtractDetails_Count -= 1

		return True

	# ENDDEF

	# Synchronises column widths of both JTables
	class ColumnChangeListener(TableColumnModelListener):
		sourceTable = None
		targetTable = None

		def __init__(self, source):
			self.sourceTable = source

		def columnAdded(self, e): pass

		def columnSelectionChanged(self, e): pass

		def columnRemoved(self, e): pass

		def columnMoved(self, e): pass

		# noinspection PyUnusedLocal
		def columnMarginChanged(self, e):
			global _column_widths_ERTC

			sourceModel = self.sourceTable.getColumnModel()

			for _i in range(0, sourceModel.getColumnCount()):
				# Saving for later... Yummy!!
				_column_widths_ERTC[_i] = sourceModel.getColumn(_i).getWidth()
				myPrint("D","Saving column %s as width %s for later..." %(_i,_column_widths_ERTC[_i]))


	# The javax.swing package and its subpackages provide a fairly comprehensive set of default renderer implementations, suitable for customization via inheritance. A notable omission is the lack #of a default renderer for a JTableHeader in the public API. The renderer used by default is a Sun proprietary class, sun.swing.table.DefaultTableCellHeaderRenderer, which cannot be extended.
	# DefaultTableHeaderCellRenderer seeks to fill this void, by providing a rendering designed to be identical with that of the proprietary class, with one difference: the vertical alignment of #the header text has been set to BOTTOM, to provide a better match between DefaultTableHeaderCellRenderer and other custom renderers.
	# The name of the class has been chosen considering this to be a default renderer for the cells of a table header, and not the table cells of a header as implied by the proprietary class name


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

		def getTableCellRendererComponent(self, table, value, isSelected, hasFocus, row, column):				# noqa
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

			self.setForeground(Color.BLACK)
			self.setBackground(Color.lightGray)

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
		def _getIcon(self, table, column):																		# noqa
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
		def getSortKey(self, table, column):																	# noqa
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


	class WindowListener(WindowAdapter):

		def windowClosing(self, WindowEvent):                                                               # noqa
			global debug, extract_reminders_csv_frame_
			myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")
			terminate_script()

		# noinspection PyMethodMayBeStatic
		# noinspection PyUnusedLocal
		def windowGainedFocus(self, WindowEvent):
			global focus, table, row, debug, EditedReminderCheck

			myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

			if focus == "lost":
				focus = "gained"
				if EditedReminderCheck:  # Disable refresh data on all gained-focus events, just refresh if Reminder is Edited...
					# To always refresh data remove this if statement and always run ExtractDetails(1)
					myPrint("DB", "pre-build_the_data_file()")
					build_the_data_file(1)  # Re-extract data when window focus gained - assume something changed
					myPrint("DB", "back from build_the_data_file(), gained focus, row: ", row)
					EditedReminderCheck = False
				table.setRowSelectionInterval(0, row)
				cellRect = table.getCellRect(row, 0, True)
				table.scrollRectToVisible(cellRect)  # force the scrollpane to make the row visible
				table.requestFocus()

			myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
			return

		# noinspection PyMethodMayBeStatic
		# noinspection PyUnusedLocal
		def windowLostFocus(self, WindowEvent):
			global focus, table, row, debug

			myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

			row = table.getSelectedRow()

			if focus == "gained": focus = "lost"

			myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
			return


	WL = WindowListener()


	class MouseListener(MouseAdapter):
		# noinspection PyMethodMayBeStatic
		def mousePressed(self, event):
			global table, row, debug
			myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")
			clicks = event.getClickCount()
			if clicks == 2:
				row = table.getSelectedRow()
				index = table.getValueAt(row, 0)
				ShowEditForm(index)
			myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
			return


	ML = MouseListener()


	class EnterAction(AbstractAction):
		# noinspection PyMethodMayBeStatic
		# noinspection PyUnusedLocal
		def actionPerformed(self, event):
			global focus, table, row, debug
			myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")
			row = table.getSelectedRow()
			index = table.getValueAt(row, 0)
			ShowEditForm(index)
			myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
			return


	class CloseAction(AbstractAction):
		# noinspection PyMethodMayBeStatic
		# noinspection PyUnusedLocal
		def actionPerformed(self, event):
			global extract_reminders_csv_frame_, debug
			myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

			terminate_script()


	class DateformatButtonAction(AbstractAction):
		# noinspection PyMethodMayBeStatic
		# noinspection PyUnusedLocal
		def actionPerformed(self, event):
			global extract_reminders_csv_frame_, debug
			myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")
			myPrint("D", "inside DateformatButtonAction() ;->")
			myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
			return


	class ExtractButtonAction(AbstractAction):
		# noinspection PyMethodMayBeStatic
		# noinspection PyUnusedLocal
		def actionPerformed(self, event):
			global extract_reminders_csv_frame_, debug
			myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")
			myPrint("D", "inside ExtractButtonAction() ;->")

			terminate_script()


	class RefreshButtonAction(AbstractAction):
		# noinspection PyMethodMayBeStatic
		def actionPerformed(self, event):
			global extract_reminders_csv_frame_, table, row, debug
			row = 0  # reset to row 1
			myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event, "\npre-extract details(1), row: ", row)
			build_the_data_file(1)  # Re-extract data
			myPrint("D", "back from extractdetails(1), row: ", row)
			table.setRowSelectionInterval(0, row)
			table.requestFocus()
			myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
			return

	class MyJTable(JTable):
		myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

		def __init__(self, tableModel):
			global debug
			super(JTable, self).__init__(tableModel)
			self.fixTheRowSorter()

		# noinspection PyMethodMayBeStatic
		# noinspection PyUnusedLocal
		def isCellEditable(self, row, column):																	# noqa
			return False

		#  Rendering depends on row (i.e. security's currency) as well as column
		# noinspection PyUnusedLocal
		# noinspection PyMethodMayBeStatic
		def getCellRenderer(self, row, column):																	# noqa
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
				global decimalCharSep
				validString = "-0123456789" + decimalCharSep  # Yes this will strip % sign too, but that still works

				# if debug: print str1, str2, self.lSortNumber, self.lSortRealNumber, type(str1), type(str2)

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

			# enddef

		def fixTheRowSorter(self):  # by default everything gets converted to strings. We need to fix this and code for my string number formats

			sorter = TableRowSorter()
			self.setRowSorter(sorter)
			sorter.setModel(self.getModel())
			for _i in range(0, self.getColumnCount()):
				if _i == 0:
					sorter.setComparator(_i, self.MyTextNumberComparator("%"))
				if _i == 9 or _i == 14:
					sorter.setComparator(_i, self.MyTextNumberComparator("N"))
				else:
					sorter.setComparator(_i, self.MyTextNumberComparator("T"))
			self.getRowSorter().toggleSortOrder(0)

		# make Banded rows
		def prepareRenderer(self, renderer, row, column):  														# noqa

			lightLightGray = Color(0xDCDCDC)
			# noinspection PyUnresolvedReferences
			component = super(MyJTable, self).prepareRenderer(renderer, row, column)
			if not self.isRowSelected(row):
				component.setBackground(self.getBackground() if row % 2 == 0 else lightLightGray)

			return component

	# This copies the standard class and just changes the colour to RED if it detects a negative - leaves field intact
	# noinspection PyArgumentList
	class MyNumberRenderer(DefaultTableCellRenderer):
		global baseCurrency

		def __init__(self):
			super(DefaultTableCellRenderer, self).__init__()

		def setValue(self, value):
			global decimalCharSep

			myGreen = Color(0,102,0)

			if isinstance(value, (float,int)):
				if value < 0.0:
					self.setForeground(Color.RED)
				else:
					# self.setForeground(Color.DARK_GRAY)
					self.setForeground(myGreen)  # DARK_GREEN
				self.setText(baseCurrency.formatFancy(int(value*100), decimalCharSep, True))
			else:
				self.setText(str(value))

			return

	# noinspection PyArgumentList
	class MyPlainNumberRenderer(DefaultTableCellRenderer):
		global baseCurrency

		def __init__(self):
			super(DefaultTableCellRenderer, self).__init__()

		def setValue(self, value):

			self.setText(str(value))

			return

	def ReminderTable(tabledata, ind):
		global extract_reminders_csv_frame_, scrollpane, table, row, debug, ReminderTable_Count, csvheaderline, lDisplayOnly
		global _column_widths_ERTC

		ReminderTable_Count += 1
		myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", ind, "  - On iteration/call: ", ReminderTable_Count)

		myDefaultWidths = [70,95,110,150,150,95,95,95,120,100,80,100,150,50,100,150,150,150]

		# col0 = 70
		# col1 = 95
		# col2 = 110
		# col3 = 150
		# col4 = 150
		# col5 = 95
		# col6 = 95
		# col7 = 95
		# col8 = 120
		# col9 = 100
		# col10 = 80
		# col11 = 100
		# col12 = 150
		# col13 = 50
		# col14 = 100
		# col15 = 150
		# col16 = 150
		# col17 = 150

		validCount=0
		lInvalidate=True
		if _column_widths_ERTC is not None and isinstance(_column_widths_ERTC,(list)) and len(_column_widths_ERTC) == len(myDefaultWidths):
			# if sum(_column_widths_ERTC)<1:
			for width in _column_widths_ERTC:
				if width >= 0 and width <= 1000:																	# noqa
					validCount += 1

		if validCount == len(myDefaultWidths): lInvalidate=False

		if lInvalidate:
			myPrint("DB","Found invalid saved columns = resetting to defaults")
			myPrint("DB","Found: %s" %_column_widths_ERTC)
			myPrint("DB","Resetting to: %s" %myDefaultWidths)
			_column_widths_ERTC = myDefaultWidths
		else:
			myPrint("DB","Valid column widths loaded - Setting to: %s" %_column_widths_ERTC)
			myDefaultWidths = _column_widths_ERTC


		# allcols = col0 + col1 + col2 + col3 + col4 + col5 + col6 + col7 + col8 + col9 + col10 + col11 + col12 + col13 + col14 + col15 + col16 + col17
		allcols = sum(myDefaultWidths)

		screenSize = Toolkit.getDefaultToolkit().getScreenSize()

		button_width = 220
		button_height = 40
		# frame_width = min(screenSize.width-20, allcols + 100)
		# frame_height = min(screenSize.height, 900)

		frame_width = min(screenSize.width-20, max(1024,int(round(moneydance_ui.firstMainFrame.getSize().width *.95,0))))
		frame_height = min(screenSize.height-20, max(768, int(round(moneydance_ui.firstMainFrame.getSize().height *.95,0))))

		frame_width = min( allcols+100, frame_width)

		panel_width = frame_width - 50
		button_panel_height = button_height + 5

		if ind == 0:  # Function can get called multiple times; only set main frames up once

			JFrame.setDefaultLookAndFeelDecorated(True)
			extract_reminders_csv_frame_ = JFrame("All Reminders - StuWareSoftSystems(build: %s)..." % version_build)
			extract_reminders_csv_frame_.setLayout(FlowLayout())

			if (not Platform.isMac()):
				moneydance_ui.getImages()
				extract_reminders_csv_frame_.setIconImage(MDImages.getImage(moneydance_ui.getMain().getSourceInformation().getIconResource()))

			extract_reminders_csv_frame_.setPreferredSize(Dimension(frame_width, frame_height))
			# frame.setExtendedState(JFrame.MAXIMIZED_BOTH)

			extract_reminders_csv_frame_.setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE)

			shortcut = Toolkit.getDefaultToolkit().getMenuShortcutKeyMaskEx()

			# Add standard CMD-W keystrokes etc to close window
			extract_reminders_csv_frame_.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_W, shortcut), "close-window")
			extract_reminders_csv_frame_.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_F4, shortcut), "close-window")
			extract_reminders_csv_frame_.getRootPane().getActionMap().put("close-window", CloseAction())

			extract_reminders_csv_frame_.addWindowFocusListener(WL)
			extract_reminders_csv_frame_.addWindowListener(WL)

			button_panel = JPanel()
			button_panel.setLayout(FlowLayout())
			button_panel.setPreferredSize(Dimension((panel_width), button_panel_height))

			# dateformat_button = JButton("Choose Dateformat")
			# dateformat_button.setPreferredSize(Dimension(button_width, button_height))
			# dateformat_button.setBackground(Color.LIGHT_GRAY)
			# dateformat_button.setBorderPainted(False)
			# dateformat_button.setOpaque(True)
			# dateformat_button.addActionListener(DateformatButtonAction())
			# button_panel.add(dateformat_button)

			refresh_button = JButton("Refresh data / Default Sort")
			refresh_button.setPreferredSize(Dimension(button_width, button_height))
			refresh_button.setBackground(Color.LIGHT_GRAY)
			refresh_button.setBorderPainted(False)
			refresh_button.setOpaque(True)
			refresh_button.addActionListener(RefreshButtonAction())

			button_panel.add(refresh_button)

			if not lDisplayOnly:
				extract_button = JButton("Extract to CSV")
				extract_button.setPreferredSize(Dimension(button_width, button_height))
				extract_button.setBackground(Color.LIGHT_GRAY)
				extract_button.setBorderPainted(False)
				extract_button.setOpaque(True)
				extract_button.addActionListener(ExtractButtonAction())
			else:
				extract_button = JButton("Close Window")
				extract_button.setPreferredSize(Dimension(button_width, button_height))
				extract_button.setBackground(Color.LIGHT_GRAY)
				extract_button.setBorderPainted(False)
				extract_button.setOpaque(True)
				extract_button.addActionListener(ExtractButtonAction())

			button_panel.add(extract_button)

			extract_reminders_csv_frame_.add(button_panel)

			tableview_panel = JPanel()

			if Platform.isOSX():
				save_useScreenMenuBar= System.getProperty("apple.laf.useScreenMenuBar")
				System.setProperty("apple.laf.useScreenMenuBar", "false")

			mb = JMenuBar()
			menuH = JMenu("<html><B>ABOUT</b></html>")

			menuItemA = JMenuItem("About")
			menuItemA.setToolTipText("About...")
			menuItemA.addActionListener(DoTheMenu(menuH))
			menuItemA.setEnabled(True)
			menuH.add(menuItemA)
			mb.add(menuH)

			extract_reminders_csv_frame_.setJMenuBar(mb)

			if Platform.isOSX():
				System.setProperty("apple.laf.useScreenMenuBar", save_useScreenMenuBar)                                 # noqa

		# button_panel.setBackground(Color.LIGHT_GRAY)

		if ind == 1:    scrollpane.getViewport().remove(table)  # On repeat, just remove/refresh the table & rebuild the viewport

		colnames = csvheaderline

		table = MyJTable(DefaultTableModel(tabledata, colnames))

		table.getTableHeader().setReorderingAllowed(True)  # no more drag and drop columns, it didn't work (on the footer)
		table.getTableHeader().setDefaultRenderer(DefaultTableHeaderCellRenderer())
		table.selectionMode = ListSelectionModel.SINGLE_SELECTION

		fontSize = table.getFont().getSize()+5
		table.setRowHeight(fontSize)
		table.setRowMargin(0)

		table.getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke("ENTER"), "Enter")
		table.getActionMap().put("Enter", EnterAction())

		for _i in range(0, table.getColumnModel().getColumnCount()):
			table.getColumnModel().getColumn(_i).setPreferredWidth(myDefaultWidths[_i])

		cListener1 = ColumnChangeListener(table)
		# Put the listener here - else it sets the defaults wrongly above....
		table.getColumnModel().addColumnModelListener(cListener1)


		table.getTableHeader().setBackground(Color.LIGHT_GRAY)

		# table.setAutoCreateRowSorter(True) # DON'T DO THIS - IT WILL OVERRIDE YOUR NICE CUSTOM SORT

		table.addMouseListener(ML)

		if ind == 0:
			scrollpane = JScrollPane(JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED, JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED)  # On first call, create the scrollpane
			scrollpane.setBorder(CompoundBorder(MatteBorder(1, 1, 1, 1, Color.gray), EmptyBorder(0, 0, 0, 0)))

		table.setPreferredScrollableViewportSize(Dimension(panel_width, frame_height - button_panel_height - 100))

		table.setAutoResizeMode(JTable.AUTO_RESIZE_OFF)

		scrollpane.setViewportView(table)
		if ind == 0:
			tableview_panel.add(scrollpane)																		# noqa
			extract_reminders_csv_frame_.add(tableview_panel)
			extract_reminders_csv_frame_.pack()
			extract_reminders_csv_frame_.setLocationRelativeTo(None)

			if True or Platform.isOSX():
				# extract_reminders_csv_frame_.setAlwaysOnTop(True)
				extract_reminders_csv_frame_.toFront()

		extract_reminders_csv_frame_.setVisible(True)

		myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
		ReminderTable_Count -= 1

		return

	def FormatAmount(oldamount):
		# Amount is held as an integer in pence
		# Remove - sign if present
		if oldamount < 0:
			oldamount = oldamount * -1

		oldamount = str(oldamount)

		# Ensure at least 3 character
		if len(oldamount) < 3:
			oldamount = "000" + oldamount
			oldamount = (oldamount)[-3:]

		# Extract whole portion of amount
		whole = (oldamount)[0:-2]
		if len(whole) == 0:
			whole = "0"

		# Extract decimal part of amount
		decimal = (oldamount)[-2:]
		declen = len(decimal)
		if declen == 0:
			decimal = "00"
			whole = "0"
		if declen == 1:
			decimal = "0" + decimal
			whole = "0"

		# Insert , commas in whole part
		wholelist = list(whole)
		listlen = len(wholelist)
		if wholelist[0] == "-":
			listlen = listlen - 1
		listpos = 3
		while listpos < listlen:
			wholelist.insert(-listpos, ",")
			listpos = listpos + 4
			listlen = listlen + 1

		newwhole = "".join(wholelist)
		newamount = newwhole + "." + decimal
		return newamount

	def FormatDate(olddate):
		# Date is held as an integer in format YYYYMMDD
		olddate = str(olddate)
		if len(olddate) < 8:
			olddate = "00000000"
		year = olddate[0:4]
		month = olddate[4:6]
		day = olddate[6:8]

		newdate = day + "/" + month + "/" + year
		if newdate == "00/00/0000":
			newdate = "Unavailable"

		return newdate

	def ShowEditForm(item):
		global debug, EditedReminderCheck
		myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")
		reminders = moneydance_data.getReminders()
		reminder = reminders.getAllReminders()[item-1]
		myPrint("D", "Calling MD EditRemindersWindow() function...")
		EditRemindersWindow.editReminder(None, moneydance_ui, reminder)
		EditedReminderCheck = True
		myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
		return

	def getKey(item): return item[2]


	if build_the_data_file(0):

		focus = "gained"																							# noqa

		table.setRowSelectionInterval(0, row)
		table.requestFocus()

		if not lDisplayOnly:
			def ExportDataToFile():
				global debug, csvfilename, decimalCharSep, groupingCharSep, csvDelimiter, version_build, myScriptName
				global sdf, userdateformat, csvlines, csvheaderline, lGlobalErrorDetected, extract_reminders_csv_frame_
				global lWriteBOMToExportFile_SWSS

				myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

				# NOTE - You can add sep=; to beginning of file to tell Excel what delimiter you are using
				# noinspection PyUnreachableCode
				if False:
					csvlines = sorted(csvlines, key=lambda x: (str(x[1]).upper()))

				csvlines.insert(0,csvheaderline)  # Insert Column Headings at top of list. A bit rough and ready, not great coding, but a short list...!

				# Write the csvlines to a file
				myPrint("B", "Opening file and writing ", len(csvlines), "records")

				try:
					# CSV Writer will take care of special characters / delimiters within fields by wrapping in quotes that Excel will decode
					with open(csvfilename,"wb") as csvfile:  # PY2.7 has no newline parameter so opening in binary; juse "w" and newline='' in PY3.0

						if lWriteBOMToExportFile_SWSS:
							csvfile.write(codecs.BOM_UTF8)   # This 'helps' Excel open file with double-click as UTF-8

						writer = csv.writer(csvfile, dialect='excel', quoting=csv.QUOTE_MINIMAL, delimiter=fix_delimiter(csvDelimiter))

						if csvDelimiter != ",":
							writer.writerow(["sep=",""])  # Tells Excel to open file with the alternative delimiter (it will add the delimiter to this line)

						for _i in range(0, len(csvlines)):
							# Write the table, but swap in the raw numbers (rather than formatted number strings)
							writer.writerow([
									fixFormatsStr(csvlines[_i][0], False),
									fixFormatsStr(csvlines[_i][1], True),
									fixFormatsStr(csvlines[_i][2], False),
									fixFormatsStr(csvlines[_i][3], False),
									fixFormatsStr(csvlines[_i][4], False),
									fixFormatsStr(csvlines[_i][5], False),
									fixFormatsStr(csvlines[_i][6], False),
									fixFormatsStr(csvlines[_i][7], False),
									fixFormatsStr(csvlines[_i][8], False),
									fixFormatsStr(csvlines[_i][9], True),
									fixFormatsStr(csvlines[_i][10], False),
									fixFormatsStr(csvlines[_i][11], False),
									fixFormatsStr(csvlines[_i][12], False),
									fixFormatsStr(csvlines[_i][13], False),
									fixFormatsStr(csvlines[_i][14], True),
									fixFormatsStr(csvlines[_i][15], False),
									fixFormatsStr(csvlines[_i][16], False),
									fixFormatsStr(csvlines[_i][17], False),
									""])
						# NEXT
						today = Calendar.getInstance()
						writer.writerow([""])
						writer.writerow(["StuWareSoftSystems - " + myScriptName + "(build: "
										+ version_build
										+ ")  Moneydance Python Script - Date of Extract: "
										+ str(sdf.format(today.getTime()))])

						writer.writerow([""])
						writer.writerow(["User Parameters..."])
						writer.writerow(["Date format................: %s" %(userdateformat)])

					myPrint("B", "CSV file " + csvfilename + " created, records written, and file closed..")

				except IOError, e:
					lGlobalErrorDetected = True
					myPrint("B", "Oh no - File IO Error!", e)
					myPrint("B", "Path:", csvfilename)
					myPrint("B", "!!! ERROR - No file written - sorry! (was file open, permissions etc?)".upper())
					dump_sys_error_to_md_console_and_errorlog()
					myPopupInformationBox(extract_reminders_csv_frame_, "Sorry - error writing to export file!", "FILE EXTRACT")
			# enddef

			def fixFormatsStr(theString, lNumber, sFormat=""):
				global lStripASCII

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

	else:
		myPopupInformationBox(extract_reminders_csv_fake_frame_,"You have no reminders to display or extract!",myScriptName)

	# ENDDEF

if extract_reminders_csv_fake_frame_:
	extract_reminders_csv_fake_frame_.dispose()
	del extract_reminders_csv_fake_frame_

myPrint("B", "StuWareSoftSystems - %s script ending......" %myScriptName)

#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# extract_reminders_to_csv.py (version 4a)

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

# Displays Moneydance reminders and allows extract to a csv file (compatible with Excel)

# Use in MoneyDance Menu Window->Show Moneybot Console >> Open Script >> RUN

import sys

reload(sys)  # Dirty hack to eliminate UTF-8 coding errors
sys.setdefaultencoding('utf8')  # Dirty hack to eliminate UTF-8 coding errors
import platform

import datetime

from com.infinitekind.moneydance.model import *
from com.infinitekind.moneydance.model import Reminder
from com.moneydance.util import Platform
from com.moneydance.apps.md.view.gui import EditRemindersWindow

from java.awt import *
from java.awt import Color, Dimension, GridLayout, FileDialog, FlowLayout, Toolkit

from java.awt.event import MouseAdapter, WindowAdapter

from java.text import *
from java.text import SimpleDateFormat, DecimalFormat

from java.util import *
from java.util import Calendar, Comparator

from javax.swing import JScrollPane, JFrame, JLabel, JPanel, JTable, JComponent, KeyStroke
from javax.swing.border import CompoundBorder, EmptyBorder, MatteBorder

from javax.swing import JButton, AbstractAction

from javax.swing import JOptionPane, JTextField
from javax.swing import UIManager, SortOrder
from javax.swing import ListSelectionModel as LSM

from javax.swing.table import DefaultTableCellRenderer, DefaultTableModel, TableRowSorter
from javax.swing.text import PlainDocument

from java.lang import System, String, Number

import os
import os.path

from java.io import FileNotFoundException, FilenameFilter
from org.python.core.util import FileUtil

import time

import inspect

import csv

import pickle

# StuWareSoftSystems common Globals
global debug  # Set to True if you want verbose messages, else set to False....
global lStripASCII, csvDelimiter
global lIamAMac
global csvfilename, version, scriptpath, lDisplayOnly, myScriptName
global decimalCharSep, groupingCharSep, myParameters, _resetParameters, baseCurrency

# This program's Globals
global sdf, userdateformat, csvlines, csvheaderline, headerFormats

global table, focus, row, debug, frame_, scrollpane, EditedReminderCheck, ReminderTable_Count, ExtractDetails_Count

version = "4a"

# Set programmatic defaults/parameters for filters HERE.... Saved Parameters will override these now
# NOTE: You  can override in the pop-up screen
userdateformat = "%Y/%m/%d"
lStripASCII = True
csvDelimiter = ","
debug = False
_resetParameters = False  # set this to True to prevent loading parameters from disk and use the defaults above...

lIamAMac = False
myParameters = {}

scriptpath = ""

myScriptName = os.path.basename(__file__)
if myScriptName.endswith(".py"):
	myScriptName = myScriptName[:-3]


def myPrint(where, *args):  # P=Display on Python Console, J=Display on MD (Java) Console Error Log, B=Both
	global myScriptName
	printString = ""
	for what in args:
		printString += str(what)
	if where == "P" or where == "B": print printString
	if where == "J" or where == "B": System.err.write(myScriptName + ": " + printString + "\n")


myPrint("B", "StuWareSoftSystems...")
myPrint("B", os.path.basename(__file__), ": Python Script Initialising.......", "Version:", version)


def getParameters():
	global debug  # Set to True if you want verbose messages, else set to False....
	global lStripASCII, csvDelimiter, scriptpath
	global myParameters
	global userdateformat

	if debug: print "In ", inspect.currentframe().f_code.co_name, "()"

	dict_filename = os.path.join("..", "StuWareSoftSystems.dict")
	if debug: print "Now checking for parameter file:", dict_filename

	local_storage = moneydance.getCurrentAccountBook().getLocalStorage()
	if local_storage.exists(dict_filename):
		__extract_reminders_to_csv = None

		myPrint("J", "loading parameters from Pickle file:", dict_filename)
		if debug: print "Parameter file", dict_filename, "exists.."
		# Open the file
		try:
			istr = local_storage.openFileForReading(dict_filename)
			load_file = FileUtil.wrap(istr)
			myParameters = pickle.load(load_file)
			load_file.close()
		except FileNotFoundException as e:
			myPrint("B", "Error: failed to find parameter file...")
			myParameters = None
		except EOFError as e:
			myPrint("B", "Error: reached EOF on parameter file....")
			myParameters = None

		if myParameters is None:
			if debug: print "Parameters did not load, will keep defaults.."
			return
		else:
			if debug: print "Parameters successfully loaded from file..."
	else:
		if debug: print "Parameter file does not exist.. Will use defaults.."
		return

	if debug:
		print "myParameters read from file contains...:"
		for key in sorted(myParameters.keys()):
			print "...variable:", key, myParameters[key]

	if myParameters.get("__extract_reminders_to_csv") is not None: __extract_reminders_to_csv = myParameters.get("__extract_reminders_to_csv")
	if myParameters.get("userdateformat") is not None: userdateformat = myParameters.get("userdateformat")
	if myParameters.get("lStripASCII") is not None: lStripASCII = myParameters.get("lStripASCII")
	if myParameters.get("csvDelimiter") is not None: csvDelimiter = myParameters.get("csvDelimiter")
	if myParameters.get("debug") is not None: debug = myParameters.get("debug")

	if myParameters.get("lUseMacFileChooser") is not None:
		myPrint("B", "Detected old lUseMacFileChooser parameter/variable... Will delete it...")
		myParameters.pop("lUseMacFileChooser", None)  # Old variable - not used - delete from parameter file

	if myParameters.get("scriptpath") is not None:
		scriptpath = myParameters.get("scriptpath")
		if not os.path.isdir(scriptpath):
			print "Warning: loaded parameter scriptpath does not appear to be a valid directory:", scriptpath, "will ignore"
			scriptpath = ""

	if debug: print "Parameter file loaded if present and parameters set into memory....."


# ENDDEF

if not _resetParameters:
	getParameters()
else:
	print "User has specified to reset parameters... keeping defaults and skipping pickle()"

if debug: myPrint("B", "DEBUG IS ON..")

def MDDiag():
	global debug
	if debug: print "MoneyDance Build:", moneydance.getVersion(), "Build:", moneydance.getBuild()


MDDiag()

if debug: print "System file encoding is:", sys.getfilesystemencoding()  # Not used, but interesting. Perhaps useful when switching between Windows/Macs and writing files...


def checkVersions():
	global debug

	lError = False
	plat_j = platform.system()
	plat_p = platform.python_implementation()
	python_maj = sys.version_info.major
	python_min = sys.version_info.minor

	if debug: print "Platform:", plat_p, plat_j, python_maj, ".", python_min
	if debug: print sys.version

	if plat_p != "Jython":
		lError = True
		print "Error: Script requires Jython"
	if plat_j != "Java":
		lError = True
		print "Error: Script requires Java  base"
	if (python_maj != 2 or python_min != 7):
		lError = True
		print "\n\nError: Script was  designed on version 2.7. By all means bypass this test and see what happens....."

	if lError:
		myPrint("J", "Platform version issue - will terminate script!")
		print "\n@@@ TERMINATING PROGRAM @@@\n"

	return not lError


# enddef

if checkVersions():
	def who_am_i():
		try:
			username = System.getProperty("user.name")
		except:
			username = "???"

		return username


	if debug: print "I am user:", who_am_i()


	def getHomeDir():
		# Yup - this can be all over the place...
		print 'System.getProperty("user.dir")', System.getProperty("user.dir")
		print 'System.getProperty("UserHome")', System.getProperty("UserHome")
		print 'System.getProperty("user.home")', System.getProperty("user.home")
		print 'os.path.expanduser("~")', os.path.expanduser("~")
		print 'os.environ.get("HOMEPATH")', os.environ.get("HOMEPATH")
		return


	if debug: getHomeDir()


	def amIaMac():
		myPlat = System.getProperty("os.name")
		if myPlat is None: return False
		if debug: print "Platform:", myPlat
		if debug: print "OS Version:", System.getProperty("os.version")
		return myPlat == "Mac OS X"


	# enddef

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

		if debug: print "Home Directory selected...:", homeDir
		if homeDir is None: return ""
		return homeDir


	csvfilename = None


	def getDecimalPoint(lGetPoint=False, lGetGrouping=False):
		global debug

		decimalPoint_MD = moneydance_ui.getPreferences().getSetting("decimal_character", ".")

		decimalFormat = DecimalFormat.getInstance()
		decimalSymbols = decimalFormat.getDecimalFormatSymbols()

		if not lGetGrouping: lGetPoint = True
		if lGetGrouping and lGetPoint: return "error"

		if lGetPoint:
			decimalCharSep = decimalSymbols.getDecimalSeparator()
			if debug: print "Decimal Point Character:", decimalCharSep

			if decimalPoint_MD != decimalCharSep:
				if debug: print "NOTE - MD decimal:", decimalPoint_MD, "is different to locale:", decimalCharSep, "- Will override to use MD's"
				decimalCharSep = decimalPoint_MD

			return decimalCharSep

		if lGetGrouping:
			groupingCharSep = decimalSymbols.getGroupingSeparator()
			if debug: print "Grouping Seperator Character:", groupingCharSep
			return groupingCharSep

		return "error"


	decimalCharSep = getDecimalPoint(lGetPoint=True)
	groupingCharSep = getDecimalPoint(lGetGrouping=True)
	if decimalCharSep != "." and csvDelimiter == ",": csvDelimiter = ";"  # Override for EU countries or where decimal point is actually a comma...
	if debug: print "Decimal point:", decimalCharSep, "Grouping Seperator", groupingCharSep, "CSV Delimiter set to:", csvDelimiter


	def check_file_writable(fnm):
		if debug: print "In ", inspect.currentframe().f_code.co_name, "()"
		if debug: print "Checking path:", fnm

		if os.path.exists(fnm):
			if debug: print "path exists.."
			# path exists
			if os.path.isfile(fnm):  # is it a file or a dir?
				if debug: print "path is a file.."
				# also works when file is a link and the target is writable
				return os.access(fnm, os.W_OK)
			else:
				if debug: print "path is not a file.."
				return False  # path is a dir, so cannot write as a file
		# target does not exist, check perms on parent dir
		if debug: print "path does not exist..."
		pdir = os.path.dirname(fnm)
		if not pdir: pdir = '.'
		# target is creatable if parent dir is writable
		return os.access(pdir, os.W_OK)


	# Stores  the data table for export
	# rawDataTable = None
	# rawrawFooterTable = None

	sdf = SimpleDateFormat("dd/MM/yyyy")


	# This allows me to filter inputs to Y/N and convert to uppercase - single digit responses..... (took hours to work out, but now I have it!)
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
					super(JTextFieldLimitYN, self).insertString(myOffset, myString, myAttr)


	# endclass

	label1 = JLabel("Output Date Format 1=dd/mm/yyyy, 2=mm/dd/yyyy, 3=yyyy/mm/dd, 4=yyyymmdd:")
	user_dateformat = JTextField(2)
	user_dateformat.setDocument(JTextFieldLimitYN(1, True, "1234"))

	if userdateformat == "%d/%m/%Y": user_dateformat.setText("1")
	elif userdateformat == "%m/%d/%Y": user_dateformat.setText("2")
	elif userdateformat == "%Y/%m/%d": user_dateformat.setText("3")
	elif userdateformat == "%Y%m%d": user_dateformat.setText("4")
	else: user_dateformat.setText("3")

	label2 = JLabel("Strip non ASCII characters from CSV export? (Y/N)")
	user_selectStripASCII = JTextField(12)
	user_selectStripASCII.setDocument(JTextFieldLimitYN(1, True, "YN"))
	if lStripASCII: user_selectStripASCII.setText("Y")
	else:               user_selectStripASCII.setText("N")

	label3 = JLabel("Change CSV Export Delimiter from default to: ';|,'")
	user_selectDELIMITER = JTextField(2)
	user_selectDELIMITER.setDocument(JTextFieldLimitYN(1, True, "DELIM"))
	user_selectDELIMITER.setText(csvDelimiter)

	label4 = JLabel("Turn DEBUG Verbose messages on? (Y/N)")
	user_selectDEBUG = JTextField(2)
	user_selectDEBUG.setDocument(JTextFieldLimitYN(1, True, "YN"))
	if debug:  user_selectDEBUG.setText("Y")
	else:           user_selectDEBUG.setText("N")

	userFilters = JPanel(GridLayout(14, 2))
	userFilters.add(label1)
	userFilters.add(user_dateformat)
	userFilters.add(label2)
	userFilters.add(user_selectStripASCII)
	userFilters.add(label3)
	userFilters.add(user_selectDELIMITER)
	userFilters.add(label4)
	userFilters.add(user_selectDEBUG)

	lExit = False
	lDisplayOnly = False

	options = ["Abort", "Display & CSV Export", "Display Only"]
	userAction = (
			JOptionPane.showOptionDialog(None, userFilters, "(" + version + ") Set Script Parameters....",
										 JOptionPane.OK_CANCEL_OPTION,
										 JOptionPane.QUESTION_MESSAGE, None, options, options[2]))
	if userAction == 1:  # Display & Export
		if debug: print "Display and export choosen"
		lDisplayOnly = False
	elif userAction == 2:  # Display Only
		lDisplayOnly = True
		if debug: print "Display only with no export chosen"
	else:
		# Abort
		print "User Cancelled Parameter selection.. Will abort.."
		lDisplayOnly = False
		lExit = True

	if not lExit:
		if debug:
			print "Parameters Captured", \
				"User Date Format:", user_dateformat.getText(), \
				"Strip ASCII:", user_selectStripASCII.getText(), \
				"Verbose Debug Messages: ", user_selectDEBUG.getText(), \
				"CSV File Delimiter:", user_selectDELIMITER.getText()
		# endif

		if user_dateformat.getText() == "1": userdateformat = "%d/%m/%Y"
		elif user_dateformat.getText() == "2": userdateformat = "%m/%d/%Y"
		elif user_dateformat.getText() == "3": userdateformat = "%Y/%m/%d"
		elif user_dateformat.getText() == "4": userdateformat = "%Y%m%d"
		else:
			# PROBLEM /  default
			userdateformat = "%Y/%m/%d"

		if user_selectStripASCII.getText() == "Y":      lStripASCII = True
		else:                                           lStripASCII = False

		csvDelimiter = user_selectDELIMITER.getText()
		if csvDelimiter == "" or (not (csvDelimiter in ";|,")):
			print "Invalid Delimiter:", csvDelimiter, "selected. Overriding with:','"
			csvDelimiter = ","
		if decimalCharSep == csvDelimiter:
			print "WARNING: The CSV file delimiter:", csvDelimiter, "cannot be the same as your decimal point character:", decimalCharSep, " - Proceeding without file export!!"
			lDisplayOnly = True

		if user_selectDEBUG.getText() == "Y":   debug = True
		else:
			debug = False
		if debug: print "DEBUG turned on"

		print "User Parameters..."
		print "user date format....:", userdateformat

		# Now get the export filename
		csvfilename = None

		if not lDisplayOnly:  # i.e. we have asked for a file export - so get the filename

			if lStripASCII:
				print "Will strip non-ASCII characters - e.g. Currency symbols from output file...", " Using Delimiter:", csvDelimiter
			else:
				print "Non-ASCII characters will not be stripped from file: ", " Using Delimiter:", csvDelimiter


			class ExtFilenameFilter(FilenameFilter):
				ext = ""

				def __init__(self, ext):
					self.ext = "." + ext.upper()

				def accept(self, thedir, filename):
					if filename is not None and filename.upper().endswith(self.ext):
						return True
					return False


			def grabTheFile():
				global debug, lDisplayOnly, csvfilename, lIamAMac, scriptpath, myScriptName
				if debug: print "In ", inspect.currentframe().f_code.co_name, "()"

				if scriptpath == "" or scriptpath is None:  # No parameter saved / loaded from disk
					scriptpath = myDir()

				if debug: print "Default file export output path is....:", scriptpath

				csvfilename = ""
				if lIamAMac:
					if debug: print "MacOS X detected: Therefore I will run FileDialog with no extension filters to get filename...."
					# jFileChooser hangs on Mac when using file extension filters, also looks rubbish. So using Mac(ish)GUI

					System.setProperty("com.apple.macos.use-file-dialog-packages",
									   "true")  # In theory prevents access to app file structure (but doesnt seem to work)
					System.setProperty("apple.awt.fileDialogForDirectories", "false")

				filename = FileDialog(None, "Select/Create CSV file for Reminders extract (CANCEL=NO EXPORT)")
				filename.setMultipleMode(False)
				filename.setMode(FileDialog.SAVE)
				filename.setFile('extract_reminders.csv')
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
					print "User chose to cancel or no file selected >>  So no Extract will be performed... "
				elif str(csvfilename).endswith(".moneydance"):
					print "User selected file:", csvfilename
					print "Sorry - User chose to use .moneydance extension - I will not allow it!... So no Extract will be performed..."
					lDisplayOnly = True
					csvfilename = None
				elif ".moneydance" in filename.getDirectory():
					print "User selected file:", filename.getDirectory(), csvfilename
					print "Sorry - FileDialog() User chose to save file in .moneydance location. NOT Good practice so I will not allow it!... So no Extract will be performed..."
					lDisplayOnly = True
					csvfilename = None
				else:
					csvfilename = os.path.join(filename.getDirectory(), filename.getFile())
					scriptpath = str(filename.getDirectory())

				if not lDisplayOnly:
					if os.path.exists(csvfilename) and os.path.isfile(
							csvfilename): print "WARNING: file exists,but assuming user said OK to overwrite.."

				if not lDisplayOnly:
					if check_file_writable(csvfilename):
						print 'Will display Reminders and then extract to file: ', csvfilename, "(NOTE: Should drop non utf8 characters...)"
						scriptpath = os.path.dirname(csvfilename)
					else:
						print "Sorry - I just checked and you do not have permissions to create this file:", csvfilename
						print "I will display the file to screen so you can copy/paste into Excel...!"
						myPrint("J", "Error - file is not writable...: ", csvfilename)
				# csvfilename=""
				# lDisplayOnly = True

				if "filename" in vars() or "filename" in globals(): del filename
				if "extfilter" in vars() or "extfilter" in globals(): del extfilter

				return


			# enddef

			if not lDisplayOnly: grabTheFile()
		else:
			pass
		# endif

		if csvfilename is None:
			lDisplayOnly = True
			print "No Export will be performed"


		# Moneydance dates  are int yyyymmddd - convert to locale date string for CSV format
		def dateoutput(dateinput, theformat):
			if dateinput == "EXPIRED": dateoutput = dateinput
			elif dateinput == "": dateoutput = ""
			elif dateinput == 0: dateoutput = ""
			elif dateinput == "0": dateoutput = ""
			else:
				dateasdate = datetime.datetime.strptime(str(dateinput), "%Y%m%d")  # Convert to Date field
				dateoutput = dateasdate.strftime(theformat)

			# print "Input: ",dateinput,"  Format: ",theformat,' Output: ',dateoutput
			return dateoutput


		def build_the_data_file(ind):
			global sdf, userdateformat, csvlines, csvheaderline, myScriptName, baseCurrency, headerFormats
			global debug, ExtractDetails_Count

			ExtractDetails_Count += 1

			if debug: print "In ", inspect.currentframe().f_code.co_name, "()", ind, " - On iteration/call: ", ExtractDetails_Count

			# ind == 1 means that this is a repeat call, so the table should be refreshed

			root = moneydance.getCurrentAccountBook()

			baseCurrency = moneydance_data.getCurrencies().getBaseType()

			rems = root.getReminders().getAllReminders()
			print 'Success: read ', rems.size(), 'reminders'
			print
			csvheaderline = ["Number#",
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
							 "Memo"]

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
							 [String,JLabel.LEFT]]

			# Read each reminder and create a csv line for each in the csvlines array
			csvlines = []  # Set up an ampty array

			for index in range(0, int(rems.size())):
				rem = rems[index]  # Get the reminder

				remtype = rem.getReminderType()  # NOTE or TRANSACTION
				desc = rem.getDescription().replace(",", " ")  # remove commas to keep csv format happy
				memo = str(rem.getMemo()).replace(",", " ").strip()  # remove commas to keep csv format happy
				memo = str(memo).replace("\n", "*").strip()  # remove newlines to keep csv format happy

				print index + 1, rem.getDescription()  # Name of Reminder

				# determine the frequency of the transaction
				daily = rem.getRepeatDaily()
				weekly = rem.getRepeatWeeklyModifier()
				monthly = rem.getRepeatMonthlyModifier()
				yearly = rem.getRepeatYearly()
				numperiods = 0
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
						splitdesc = txnparent.getOtherTxn(index2).getDescription().replace(",",
																						   " ")  # remove commas to keep csv format happy
						splitmemo = txnparent.getMemo().replace(",", " ")  # remove commas to keep csv format happy
						maindesc = txnparent.getDescription().replace(",", " ").strip()

						if index2 > 0: amount = ''  # Don't repeat the new amount on subsequent split lines (so you can total column). The split amount will be correct

						stripacct = str(txnparent.getAccount()).replace(",",
																		" ").strip()  # remove commas to keep csv format happy
						stripcat = str(txnparent.getOtherTxn(index2).getAccount()).replace(",",
																						   " ").strip()  # remove commas to keep csv format happy

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

			if debug: print "Exiting ", inspect.currentframe().f_code.co_name
			ExtractDetails_Count -= 1

		# ENDDEF


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

			def getTableCellRendererComponent(self, table, value, isSelected, hasFocus, row, column):
				super(DefaultTableHeaderCellRenderer, self).getTableCellRendererComponent(table, value, isSelected,
																						  hasFocus, row, column)
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
			def _getIcon(self, table, column):
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
			def getSortKey(self, table, column):
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
			def windowGainedFocus(self, WindowEvent):
				global focus, table, row, debug, EditedReminderCheck

				if debug: print "In ", inspect.currentframe().f_code.co_name, "()"

				if focus == "lost":
					focus = "gained"
					if EditedReminderCheck:  # Disable refresh data on all gained-focus events, just refresh if Reminder is Edited...
						# To always refresh data remove this if statement and always run ExtractDetails(1)
						if debug: print "pre-build_the_data_file()"
						build_the_data_file(1)  # Re-extract data when window focus gained - assume something changed
						if debug: print "back from build_the_data_file(), gained focus, row: ", row
						EditedReminderCheck = False
					table.setRowSelectionInterval(0, row)
					cellRect = table.getCellRect(row, 0, True)
					table.scrollRectToVisible(cellRect)  # force the scrollpane to make the row visible
					table.requestFocus()

				if debug: print "Exiting ", inspect.currentframe().f_code.co_name, "()"
				return

			def windowLostFocus(self, WindowEvent):
				global focus, table, row, debug

				if debug: print "In ", inspect.currentframe().f_code.co_name, "()"

				row = table.getSelectedRow()

				if focus == "gained": focus = "lost"

				if debug: print "Exiting ", inspect.currentframe().f_code.co_name, "()"
				return


		WL = WindowListener()


		class MouseListener(MouseAdapter):
			def mousePressed(self, event):
				global table, row, debug
				if debug: print "In ", inspect.currentframe().f_code.co_name, "()"
				clicks = event.getClickCount()
				if clicks == 2:
					row = table.getSelectedRow()
					index = table.getValueAt(row, 0)
					ShowEditForm(index)
				if debug: print "Exiting ", inspect.currentframe().f_code.co_name, "()"
				return


		ML = MouseListener()


		class EnterAction(AbstractAction):
			def actionPerformed(self, event):
				global focus, table, row, debug
				if debug: print "In ", inspect.currentframe().f_code.co_name, "()"
				row = table.getSelectedRow()
				index = table.getValueAt(row, 0)
				ShowEditForm(index)
				if debug: print "Exiting ", inspect.currentframe().f_code.co_name, "()"
				return


		class CloseAction(AbstractAction):
			def actionPerformed(self, event):
				global frame_, debug
				if debug: print "In ", inspect.currentframe().f_code.co_name, "()"
				frame_.dispose()
				if debug: print "Exiting ", inspect.currentframe().f_code.co_name, "()"
				return


		class dateformat_button_action(AbstractAction):
			def actionPerformed(self, event):
				global frame_, debug
				if debug: print "In ", inspect.currentframe().f_code.co_name, "()"
				if debug: print "inside dateformat_button_action() ;->"
				if debug: print "Exiting ", inspect.currentframe().f_code.co_name, "()"
				return


		class extract_button_action(AbstractAction):
			def actionPerformed(self, event):
				global frame_, debug
				if debug: print "In ", inspect.currentframe().f_code.co_name, "()"
				if debug: print "inside extract_button_action() ;->"

				# Kill the frame - this will call file creation or plain exit anyway....
				frame_.dispose()

				if debug: print "Exiting ", inspect.currentframe().f_code.co_name, "()"
				return


		class refresh_button_action(AbstractAction):
			def actionPerformed(self, event):
				global frame_, table, row, debug
				row = 0  # reset to row 1
				if debug: print "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event, "\npre-extract details(1), row: ", row
				build_the_data_file(1)  # Re-extract data
				if debug: print "back from extractdetails(1), row: ", row
				table.setRowSelectionInterval(0, row)
				table.requestFocus()
				if debug: print "Exiting ", inspect.currentframe().f_code.co_name, "()"
				return

		class myJTable(JTable):
			if debug: print "In ", inspect.currentframe().f_code.co_name, "()"

			def __init__(self, tableModel):
				global debug
				super(JTable, self).__init__(tableModel)
				self.fixTheRowSorter()

			def isCellEditable(self, row, column):
				return False

			#  Rendering depends on row (i.e. security's currency) as well as column
			def getCellRenderer(self, row, column):
				global headerFormats

				if column == 0:
					renderer = myPlainNumberRenderer()
				elif headerFormats[column][0] == Number:
					renderer = myNumberRenderer()
				else:
					renderer = DefaultTableCellRenderer()

				renderer.setHorizontalAlignment(headerFormats[column][1])

				return renderer

			class myTextNumberComparator(Comparator):
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

					if type(str1) == type(1.0) or type(str1) == type(1)\
						or type(str2) == type(1.0) or type(str2) == type(1):
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
				for i in range(0, self.getColumnCount()):
					if i == 0:
						sorter.setComparator(i, self.myTextNumberComparator("%"))
					if i == 9 or i == 14:
						sorter.setComparator(i, self.myTextNumberComparator("N"))
					else:
						sorter.setComparator(i, self.myTextNumberComparator("T"))
				self.getRowSorter().toggleSortOrder(0)

			def prepareRenderer(self, renderer, row, column):  # make Banded rows

				lightLightGray = Color(0xDCDCDC)
				component = super(myJTable, self).prepareRenderer(renderer, row, column)
				if not self.isRowSelected(row):
						component.setBackground(self.getBackground() if row % 2 == 0 else lightLightGray)

				return component

		# This copies the standard class and just changes the colour to RED if it detects a negative - leaves field intact
		class myNumberRenderer(DefaultTableCellRenderer):
			global baseCurrency

			def __init__(self):
				super(DefaultTableCellRenderer, self).__init__()

			def setValue(self, value):
				global decimalCharSep

				myGreen = Color(0,102,0)


				if type(value) == type(1) or type(value) == type(1.0):
					if value < 0.0:
						self.setForeground(Color.RED)
					else:
						# self.setForeground(Color.DARK_GRAY)
						self.setForeground(myGreen) #DARK_GREEN
					self.setText(baseCurrency.formatFancy(int(value*100), decimalCharSep, True))
				else:
					self.setText(str(value))

				return

		class myPlainNumberRenderer(DefaultTableCellRenderer):
			global baseCurrency

			def __init__(self):
				super(DefaultTableCellRenderer, self).__init__()

			def setValue(self, value):

				self.setText(str(value))

				return

		def ReminderTable(tabledata, ind):
			global frame_, scrollpane, table, row, debug, ReminderTable_Count, csvheaderline, lDisplayOnly

			ReminderTable_Count += 1
			if debug: print "In ", inspect.currentframe().f_code.co_name, "()", ind, "  - On iteration/call: ", ReminderTable_Count

			col0 = 70
			col1 = 95
			col2 = 110
			col3 = 150
			col4 = 150
			col5 = 95
			col6 = 95
			col7 = 95
			col8 = 120
			col9 = 100
			col10 = 80
			col11 = 100
			col12 = 150
			col13 = 50
			col14 = 100
			col15 = 150
			col16 = 150
			col17 = 150
			allcols = col0 + col1 + col2 + col3 + col4 + col5 + col6 + col7 + col8 + col9 + col10 + col11 + col12 + col13 + col14 + col15 + col16 + col17

			screenSize = Toolkit.getDefaultToolkit().getScreenSize()

			button_width = 220
			button_height = 40
			frame_width = min(screenSize.width-20, allcols + 100)
			frame_height = min(screenSize.height, 900)
			panel_width = frame_width - 50
			button_panel_height = button_height + 5

			if ind == 0:  # Funtion can get called multiple times; only set main frames up once
				frame_ = JFrame("All Reminders")
				frame_.setLayout(FlowLayout())

				frame_.setPreferredSize(Dimension(frame_width, frame_height))
				# frame.setExtendedState(JFrame.MAXIMIZED_BOTH)

				frame_.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE)

				frame_.addWindowFocusListener(WL)

				# Add standard CMD-W keystrokes etc to close window
				frame_.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(
					KeyStroke.getKeyStroke("control W"), "close-window")
				frame_.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(
					KeyStroke.getKeyStroke("meta W"), "close-window")
				frame_.getRootPane().getActionMap().put("close-window", CloseAction())

				button_panel = JPanel()
				button_panel.setLayout(FlowLayout())
				button_panel.setPreferredSize(Dimension((panel_width), button_panel_height))

				# dateformat_button = JButton("Choose Dateformat")
				# dateformat_button.setPreferredSize(Dimension(button_width, button_height))
				# dateformat_button.setBackground(Color.LIGHT_GRAY)
				# dateformat_button.setBorderPainted(False)
				# dateformat_button.setOpaque(True)
				# dateformat_button.addActionListener(dateformat_button_action())
				# button_panel.add(dateformat_button)

				refresh_button = JButton("Refresh data / Default Sort")
				refresh_button.setPreferredSize(Dimension(button_width, button_height))
				refresh_button.setBackground(Color.LIGHT_GRAY)
				refresh_button.setBorderPainted(False)
				refresh_button.setOpaque(True)
				refresh_button.addActionListener(refresh_button_action())

				button_panel.add(refresh_button)

				if not lDisplayOnly:
					extract_button = JButton("Extract to CSV")
					extract_button.setPreferredSize(Dimension(button_width, button_height))
					extract_button.setBackground(Color.LIGHT_GRAY)
					extract_button.setBorderPainted(False)
					extract_button.setOpaque(True)
					extract_button.addActionListener(extract_button_action())
				else:
					extract_button = JButton("Close Window")
					extract_button.setPreferredSize(Dimension(button_width, button_height))
					extract_button.setBackground(Color.LIGHT_GRAY)
					extract_button.setBorderPainted(False)
					extract_button.setOpaque(True)
					extract_button.addActionListener(extract_button_action())

				button_panel.add(extract_button)

				frame_.add(button_panel)

				tableview_panel = JPanel()
			# button_panel.setBackground(Color.LIGHT_GRAY)

			if ind == 1:    scrollpane.getViewport().remove(table)  # On repeat, just remove/refresh the table & rebuild the viewport

			colnames = csvheaderline

			table = myJTable(DefaultTableModel(tabledata, colnames))

			table.getTableHeader().setReorderingAllowed(True)  # no more drag and drop columns, it didn't work (on the footer)
			table.getTableHeader().setDefaultRenderer(DefaultTableHeaderCellRenderer())
			table.selectionMode = LSM.SINGLE_SELECTION

			table.getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke("ENTER"), "Enter")
			table.getActionMap().put("Enter", EnterAction())

			table.getColumnModel().getColumn(0).setPreferredWidth(col0)
			table.getColumnModel().getColumn(1).setPreferredWidth(col1)
			table.getColumnModel().getColumn(2).setPreferredWidth(col2)
			table.getColumnModel().getColumn(3).setPreferredWidth(col3)
			table.getColumnModel().getColumn(4).setPreferredWidth(col4)
			table.getColumnModel().getColumn(5).setPreferredWidth(col5)
			table.getColumnModel().getColumn(6).setPreferredWidth(col6)
			table.getColumnModel().getColumn(7).setPreferredWidth(col7)
			table.getColumnModel().getColumn(8).setPreferredWidth(col8)
			table.getColumnModel().getColumn(9).setPreferredWidth(col9)
			table.getColumnModel().getColumn(10).setPreferredWidth(col10)
			table.getColumnModel().getColumn(11).setPreferredWidth(col11)
			table.getColumnModel().getColumn(12).setPreferredWidth(col12)
			table.getColumnModel().getColumn(13).setPreferredWidth(col13)
			table.getColumnModel().getColumn(14).setPreferredWidth(col14)
			table.getColumnModel().getColumn(15).setPreferredWidth(col15)
			table.getColumnModel().getColumn(16).setPreferredWidth(col16)
			table.getColumnModel().getColumn(17).setPreferredWidth(col17)

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
				tableview_panel.add(scrollpane)
				frame_.add(tableview_panel)
				frame_.pack()

			frame_.setVisible(True)

			if debug: print "Exiting ", inspect.currentframe().f_code.co_name, "()"
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
			if debug: print "In ", inspect.currentframe().f_code.co_name, "()"
			reminders = moneydance_data.getReminders()
			reminder = reminders.getAllReminders()[item-1]
			if debug: print "Calling MD EditRemindersWindow() function..."
			EditRemindersWindow.editReminder(None, moneydance_ui, reminder)
			EditedReminderCheck = True
			if debug: print "Exiting ", inspect.currentframe().f_code.co_name, "()"
			return


		def getKey(item):
			return item[2]


		build_the_data_file(0)

		focus = "gained"

		table.setRowSelectionInterval(0, row)
		table.requestFocus()

		# A bit of a fudge, but hey it works.....!
		i = 0
		while frame_.isVisible():
			i = i + 1
			time.sleep(1)
			if debug: print "Waiting for JFrame() to close... Wait number...:", i

		if debug: print "No longer waiting...."

		if not lDisplayOnly:
			def ExportDataToFile():
				global debug, csvfilename, decimalCharSep, groupingCharSep, csvDelimiter, version, myScriptName
				global sdf, userdateformat, csvlines, csvheaderline

				if debug: print "In ", inspect.currentframe().f_code.co_name, "()"

				# NOTE - You can add sep=; to beginning of file to tell Excel what delimiter you are using
				if False:
					csvlines = sorted(csvlines, key=lambda x: (str(x[1]).upper()))

				csvlines.insert(0,
								csvheaderline)  # Insert Column Headings at top of list. A bit rough and ready, not great coding, but a short list...!

				# Write the csvlines to a file
				if debug: print "Opening file and writing ", len(csvlines), "records"
				myPrint("J", "Opening file and writing ", len(csvlines), " records")

				try:
					# CSV Writer will take care of special characters / delimiters within fields by wrapping in quotes that Excel will decode
					with open(csvfilename,
							  "wb") as csvfile:  # PY2.7 has no newline parameter so opening in binary; juse "w" and newline='' in PY3.0
						writer = csv.writer(csvfile, dialect='excel', quoting=csv.QUOTE_MINIMAL, delimiter=csvDelimiter)

						if csvDelimiter != ",":
							writer.writerow(["sep=",
											 ""])  # Tells Excel to open file with the alternative delimiter (it will add the delimiter to this line)

						for i in range(0, len(csvlines)):
							# Write the table, but swap in the raw numbers (rather than formatted number strings)
							writer.writerow([
									fixFormatsStr(csvlines[i][0], False),
									fixFormatsStr(csvlines[i][1], True),
									fixFormatsStr(csvlines[i][2], False),
									fixFormatsStr(csvlines[i][3], False),
									fixFormatsStr(csvlines[i][4], False),
									fixFormatsStr(csvlines[i][5], False),
									fixFormatsStr(csvlines[i][6], False),
									fixFormatsStr(csvlines[i][7], False),
									fixFormatsStr(csvlines[i][8], False),
									fixFormatsStr(csvlines[i][9], True),
									fixFormatsStr(csvlines[i][10], False),
									fixFormatsStr(csvlines[i][11], False),
									fixFormatsStr(csvlines[i][12], False),
									fixFormatsStr(csvlines[i][13], False),
									fixFormatsStr(csvlines[i][14], True),
									fixFormatsStr(csvlines[i][15], False),
									fixFormatsStr(csvlines[i][16], False),
									fixFormatsStr(csvlines[i][17], False),
									""])
						# NEXT
						today = Calendar.getInstance()
						writer.writerow([""])
						writer.writerow(["StuWareSoftSystems - " + myScriptName + "("
										 + version
										 + ")  MoneyDance Python Script - Date of Extract: "
										 + str(sdf.format(today.getTime()))])
					myPrint("B", "CSV file " + csvfilename + " created, records written, and file closed..")

				except IOError, e:
					myPrint("B", "Oh no - File IO Error!")
					myPrint("B", e)
					myPrint("B", sys.exc_type)
					myPrint("B", "Path:", csvfilename)
					myPrint("B", "!!! ERROR - No file written - sorry! (was file open, permissions etc?)".upper())
			# enddef

			def fixFormatsStr(theString, lNumber, sFormat=""):
				global lStripASCII

				if type(theString) == type(1) or type(theString) == type(1.1):
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
					all_ASCII = ''.join(char for char in theString if
										ord(char) < 128)  # Eliminate non ASCII printable Chars too....
				else:
					all_ASCII = theString
				return all_ASCII

			ExportDataToFile()


		def saveParameters():
			global debug  # Set to True if you want verbose messages, else set to False....
			global lStripASCII, csvDelimiter, scriptpath
			global lDisplayOnly, version, myParameters
			global userdateformat

			if debug: print "In ", inspect.currentframe().f_code.co_name, "()"

			# NOTE: Parameters were loaded earlier on... Preserve existing, and update any used ones...
			# (i.e. other StuWareSoftSystems programs might be sharing the same file)

			if myParameters is None: myParameters = {}

			myParameters["__Author"] = "Stuart Beesley - (c) StuWareSoftSystems"
			myParameters["__extract_reminders_to_csv"] = version
			myParameters["userdateformat"] = userdateformat
			myParameters["lStripASCII"] = lStripASCII
			myParameters["csvDelimiter"] = csvDelimiter
			myParameters["debug"] = debug

			if not lDisplayOnly and scriptpath != "" and os.path.isdir(scriptpath):
				myParameters["scriptpath"] = scriptpath

			dict_filename = os.path.join("..", "StuWareSoftSystems.dict")
			if debug: print "Will try to save parameter file:", dict_filename

			local_storage = moneydance.getCurrentAccountBook().getLocalStorage()
			ostr = local_storage.openFileForWriting(dict_filename)

			myPrint("J", "about to Pickle.dump and save parameters to file:", dict_filename)

			try:
				save_file = FileUtil.wrap(ostr)
				pickle.dump(myParameters, save_file)
				save_file.close()

				if debug:
					print "myParameters now contains...:"
					for key in sorted(myParameters.keys()):
						print "...variable:", key, myParameters[key]

			except:
				myPrint("B", "Error - failed to create/write parameter file.. Ignoring and continuing.....")
				return

			if debug: print "Parameter file written and parameters saved to disk....."


		# ENDDEF

		saveParameters()

else:
	pass

# Some cleanup of large / important objects....
try:
	if debug: print "deleting old objects"
	if "frame_" in vars() or "frame_" in globals(): del frame_
	if "userFilters" in vars() or "userFilters" in globals(): del userFilters
	if "JTextFieldLimitYN" in vars() or "JTextFieldLimitYN" in globals(): del JTextFieldLimitYN

except:
	if debug: print "Objects did not exist.."

myPrint("B", "StuWareSoftSystems - ", os.path.basename(__file__), " script ending......")

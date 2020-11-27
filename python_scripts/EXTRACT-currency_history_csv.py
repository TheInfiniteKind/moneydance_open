#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# EXTRACT-currency_history_csv v1a - November 2020 - Stuart Beesley StuWareSoftSystems
# Extracts your Currency rate history to CSV file (as MD doesn't do this)
# This script does not change any data!
# Thanks to DerekKent23 for his testing....
###############################################################################
# MIT License
#
# Copyright (c) 2020 Stuart Beesley - StuWareSoftSystems & Moneydance
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
# V0.1 beta - Initial release
# V0.2 beta - Parameter enhancements, simplify option (for DerekKent23)
# V0.3 beta - Added UTF8 BOM to help Excel double-click open files. Changed open() to 'W' instead of 'wb'
# V0.4 beta - Changed to no rounding on price history... Added suffix to simple format
# V0.5 beta - Cosmetic dipslay change; catch pickle.load() error (from restored file); extract format changes..
# V0.6 beta - Reverted to open() with 'wb'
# V1 - Initial release
# V1a - Changed pickle file to be unencrypted

import sys

reload(sys)  # Dirty hack to eliminate UTF-8 coding errors
sys.setdefaultencoding('utf8')  # Dirty hack to eliminate UTF-8 coding errors
import platform

import datetime

import codecs

from com.infinitekind.moneydance.model import *
from com.infinitekind.util import CustomDateFormat
from com.moneydance.util import Platform
from com.moneydance.awt import JDateField
from com.infinitekind.moneydance.model import CurrencyType

from java.awt import *
from java.awt import GridLayout, FileDialog
from java.awt import Color

from java.text import *
from java.text import SimpleDateFormat, DecimalFormat

from java.util import *
from java.util import Calendar


from javax.swing import JLabel, JPanel, JOptionPane, JTextField
from javax.swing.text import PlainDocument

from java.lang import System

from java.io import FileInputStream, FileOutputStream, IOException, StringReader
from java.io import FileNotFoundException, FilenameFilter

import os
import os.path

from org.python.core.util import FileUtil

import inspect
import csv
import pickle

# StuWareSoftSystems common Globals
global debug  # Set to True if you want verbose messages, else set to False....
global lStripASCII, csvDelimiter
global lIamAMac
global csvfilename, version, scriptpath, lDisplayOnly, myScriptName
global decimalCharSep, groupingCharSep, _resetParameters, baseCurrency, userdateformat
global lSimplify_ECH, userdateStart_ECH, userdateEnd_ECH, hideHiddenCurrencies_ECH

# This program's Globals
global sdf, csvlines


version = "1a"

# Set programmatic defaults/parameters for filters HERE.... Saved Parameters will override these now
# NOTE: You  can override in the pop-up screen
userdateformat = "%Y/%m/%d"
lStripASCII = False
csvDelimiter = ","
debug = False

lSimplify_ECH = True
userdateStart_ECH = 19700101
userdateEnd_ECH = 20201231
hideHiddenCurrencies_ECH = True


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

def get_StuWareSoftSystems_parameters_from_file():
    global debug  # Set to True if you want verbose messages, else set to False....
    global lStripASCII, csvDelimiter, scriptpath
    global myParameters
    global userdateformat
    global lSimplify_ECH, userdateStart_ECH, userdateEnd_ECH, hideHiddenCurrencies_ECH

    if debug: print "In ", inspect.currentframe().f_code.co_name, "()"

    myFile = "StuWareSoftSystems.dict"
    old_dict_filename = os.path.join("..", myFile)

    # Pickle was originally encrypted, no need, migrating to unencrypted
    migratedFilename = os.path.join(moneydance_data.getRootFolder().getAbsolutePath(),myFile)

    if debug: print "Now checking for parameter file:", migratedFilename

    if os.path.exists( migratedFilename ):

        myPrint("J", "loading parameters from non-encrypted Pickle file:", migratedFilename)
        if debug: print "Parameter file", migratedFilename, "exists.."
        # Open the file
        try:
            istr = FileInputStream(migratedFilename)
            load_file = FileUtil.wrap(istr)
            myParameters = pickle.load(load_file)
            load_file.close()
        except FileNotFoundException as e:
            myPrint("B", "Error: failed to find parameter file...")
            myParameters = None
        except EOFError as e:
            myPrint("B", "Error: reached EOF on parameter file....")
            myParameters = None
        except:
            myPrint("B","Error opening Pickle File (will try  encrypted version) - Unexpected error ", sys.exc_info()[0])
            myPrint("B","Error opening Pickle File (will try  encrypted version) - Unexpected error ", sys.exc_info()[1])

            # OK, so perhaps from older version - encrypted, try to read
            try:
                local_storage = moneydance.getCurrentAccountBook().getLocalStorage()
                istr = local_storage.openFileForReading(old_dict_filename)
                load_file = FileUtil.wrap(istr)
                myParameters = pickle.load(load_file)
                load_file.close()
                myPrint("B","Success loading Encrypted Pickle file - will migrate to non encrypted")
            except:
                myPrint("B","Opening Encrypted Pickle File (will try  encrypted version) - Unexpected error ", sys.exc_info()[0])
                myPrint("B","Opening Encrypted Pickle File (will try  encrypted version) - Unexpected error ", sys.exc_info()[1])
                myParameters = None
                myPrint("B", "Error: Pickle.load() failed.... Is this a restored dataset? Will ignore saved parameters, and create a new file...")

        if myParameters is None:
            if debug: print "Parameters did not load, will keep defaults.."
        else:
            if debug: print "Parameters successfully loaded from file..."
    else:
        myPrint("J", "Parameter Pickle file does not exist - will use default and create new file..")
        if debug: myPrint("P", "Parameter Pickle file does not exist - will use default and create new file..")
        myParameters = None

    if not myParameters: return

    if debug:
        print "myParameters read from file contains...:"
        for key in sorted(myParameters.keys()):
            print "...variable:", key, myParameters[key]

    if myParameters.get("__extract_currency_history_csv") is not None: __extract_currency_history_csv = myParameters.get("__extract_currency_history_csv")
    if myParameters.get("userdateformat") is not None: userdateformat = myParameters.get("userdateformat")
    if myParameters.get("lStripASCII") is not None: lStripASCII = myParameters.get("lStripASCII")
    if myParameters.get("csvDelimiter") is not None: csvDelimiter = myParameters.get("csvDelimiter")
    if myParameters.get("debug") is not None: debug = myParameters.get("debug")

    if myParameters.get("lSimplify_ECH") is not None: lSimplify_ECH = myParameters.get("lSimplify_ECH")
    if myParameters.get("userdateStart_ECH") is not None: userdateStart_ECH = myParameters.get("userdateStart_ECH")
    if myParameters.get("userdateEnd_ECH") is not None: userdateEnd_ECH = myParameters.get("userdateEnd_ECH")
    if myParameters.get("hideHiddenCurrencies_ECH") is not None: hideHiddenCurrencies_ECH = myParameters.get("hideHiddenCurrencies_ECH")

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
    get_StuWareSoftSystems_parameters_from_file()
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

    labelDateStart = JLabel("Date range start (enter as yyyy/mm/dd):")
    user_selectDateStart = JDateField(CustomDateFormat("ymd"),15) # Use MD API function (not std Python)
    user_selectDateStart.setDateInt(userdateStart_ECH)

    labelDateEnd = JLabel("Date range end (enter as yyyy/mm/dd):")
    user_selectDateEnd = JDateField(CustomDateFormat("ymd"),15) # Use MD API function (not std Python)
    user_selectDateEnd.setDateInt(userdateEnd_ECH)
    # user_selectDateEnd.gotoToday()

    labelSimplify = JLabel("Simplify extract (Y/N):")
    user_selectSimplify = JTextField(2)
    user_selectSimplify.setDocument(JTextFieldLimitYN(1, True, "YN"))
    if lSimplify_ECH: user_selectSimplify.setText("Y")
    else:             user_selectSimplify.setText("N")

    labelHideHiddenCurrencies = JLabel("Hide Hidden Currencies (Y/N):")
    user_selectHideHiddenCurrencies = JTextField(2)
    user_selectHideHiddenCurrencies.setDocument(JTextFieldLimitYN(1, True, "YN"))
    if hideHiddenCurrencies_ECH: user_selectHideHiddenCurrencies.setText("Y")
    else:                        user_selectHideHiddenCurrencies.setText("N")

    label2 = JLabel("Strip non ASCII characters from CSV export? (Y/N)")
    user_selectStripASCII = JTextField(2)
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
    else:      user_selectDEBUG.setText("N")

    userFilters = JPanel(GridLayout(8, 2))
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
    userFilters.add(label4)
    userFilters.add(user_selectDEBUG)

    lExit = False
    lDisplayOnly = False

    options = ["Abort", "CSV Export"]

    while True:
        userAction = (
                JOptionPane.showOptionDialog(None, userFilters, "(" + version + ") Set Script Parameters....",
                                             JOptionPane.OK_CANCEL_OPTION,
                                             JOptionPane.QUESTION_MESSAGE, None, options, options[1]))
        if userAction != 1:
            print "User Cancelled Parameter selection.. Will abort.."
            lDisplayOnly = False
            lExit = True
            break

        if user_selectDateStart.getDateInt() <= user_selectDateEnd.getDateInt() \
                and user_selectDateEnd.getDateInt() >= user_selectDateStart.getDateInt():
            break # Valid date range

        print "Error - date range incorrect, please try again..."
        user_selectDateStart.setForeground(Color.RED)
        user_selectDateEnd.setForeground(Color.RED)
        continue # Loop


    if not lExit:
        if debug:
            print "Parameters Captured", \
                "User Date Format:", user_dateformat.getText(), \
                "Simplify:", user_selectSimplify.getText(), \
                "Hide Hidden Currencies:", user_selectHideHiddenCurrencies.getText(), \
                "Start date:", user_selectDateStart.getDateInt(), \
                "End date:", user_selectDateEnd.getDateInt(), \
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

        lSimplify_ECH = user_selectSimplify.getText() == "Y"
        hideHiddenCurrencies_ECH = user_selectHideHiddenCurrencies.getText() == "Y"
        userdateStart_ECH = user_selectDateStart.getDateInt()
        userdateEnd_ECH = user_selectDateEnd.getDateInt()

        lStripASCII = user_selectStripASCII.getText() == "Y"

        csvDelimiter = user_selectDELIMITER.getText()
        if csvDelimiter == "" or (not (csvDelimiter in ";|,")):
            print "Invalid Delimiter:", csvDelimiter, "selected. Overriding with:','"
            csvDelimiter = ","
        if decimalCharSep == csvDelimiter:
            print "WARNING: The CSV file delimiter:", csvDelimiter, "cannot be the same as your decimal point character:", decimalCharSep, " - Proceeding without file export!!"
            lDisplayOnly = True

        debug = user_selectDEBUG.getText() == "Y"
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

                filename = FileDialog(None, "Select/Create CSV file for Currency Rate History extract (CANCEL=NO EXPORT)")
                filename.setMultipleMode(False)
                filename.setMode(FileDialog.SAVE)
                filename.setFile('extract_currency_rate_history.csv')
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
                        if lStripASCII:
                            print 'Will extract currency rate history to file: ', csvfilename, "(NOTE: Should drop non utf8 characters...)"
                        else:
                            print 'Will extract currency rate history to file: ', csvfilename, "..."
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

        print "\nScript running to extract your currency rate history...."
        print "-------------------------------------------------------------------"
        if moneydance_data is None:
            print "no data to scan - aborting"
            raise Exception("MD Data file is empty - no data to scan - aborting...")

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

            curr_table=[]

            currencies = moneydance.getCurrentAccountBook().getCurrencies()
            baseCurr = currencies.getBaseType()

            print "\nIterating the currency table..."
            for curr in currencies:

                if curr.getCurrencyType() != CurrencyType.Type.CURRENCY: continue # Skip if not on a Currency record (i.e. a Security)

                if hideHiddenCurrencies_ECH and curr.getHideInUI(): continue # Skip if hidden in MD

                print("Currency: %s %s" %(curr, curr.getPrefix()) )

                currSnapshots = curr.getSnapshots()

                if not lSimplify_ECH \
                        and not len(currSnapshots) and curr == baseCurr:

                    row = []

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

                dpc = curr.getDecimalPlaces()
                dpc = 8 # Override to 8dpc

                for currSnapshot in currSnapshots:
                    if currSnapshot.getDateInt() < userdateStart_ECH \
                            or currSnapshot.getDateInt() > userdateEnd_ECH:
                        continue # Skip if out of date range

                    row = []

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

        if not lDisplayOnly:
            def ExportDataToFile(theTable, header):
                global debug, csvfilename, decimalCharSep, groupingCharSep, csvDelimiter, version, myScriptName
                global sdf, userdateformat

                if debug: print "In ", inspect.currentframe().f_code.co_name, "()"

                _CURRNAME = 0
                _CURRID = 1
                _SYMB =4
                _SNAPDATE = 8


                # NOTE - You can add sep=; to beginning of file to tell Excel what delimiter you are using
                if True:
                    theTable = sorted(theTable, key=lambda x: (str(x[_CURRNAME]).upper(),x[_SNAPDATE]))

                if debug: print "Now pre-processing the file to convert integer dates to 'formatted' dates...."
                for row in theTable:
                    try:
                        if row[_SNAPDATE]:
                            dateasdate = datetime.datetime.strptime(str(row[_SNAPDATE]),"%Y%m%d")  # Convert to Date field
                            dateoutput = dateasdate.strftime(userdateformat)
                            row[_SNAPDATE] = dateoutput

                    except:
                        print "Error on row below with curr:", row[_CURRNAME], "snap date:", row[_SNAPDATE]
                        print row
                        continue

                    if lStripASCII:
                        for col in range(0, len(row)):
                            row[col] = fixFormatsStr(row[col])

                theTable.insert(0,header)  # Insert Column Headings at top of list. A bit rough and ready, not great coding, but a short list...!

                # Write the theTable to a file
                if debug: print "Opening file and writing ", len(theTable), "records"
                myPrint("J", "Opening file and writing ", len(theTable), " records")

                try:
                    # CSV Writer will take care of special characters / delimiters within fields by wrapping in quotes that Excel will decode
                    # with open(csvfilename,"wb") as csvfile:  # PY2.7 has no newline parameter so opening in binary; just use "w" and newline='' in PY3.0
                    with open(csvfilename,"wb") as csvfile:  # PY2.7 has no newline parameter so opening in binary; just use "w" and newline='' in PY3.0

                        csvfile.write(codecs.BOM_UTF8) # This 'helps' Excel open file with double-click as UTF-8

                        writer = csv.writer(csvfile, dialect='excel', quoting=csv.QUOTE_MINIMAL, delimiter=csvDelimiter)


                        if csvDelimiter != ",":
                            writer.writerow(["sep=",""])  # Tells Excel to open file with the alternative delimiter (it will add the delimiter to this line)

                        if not lSimplify_ECH:
                            for i in range(0, len(theTable)):
                                # Write the table, but swap in the raw numbers (rather than formatted number strings)
                                writer.writerow( theTable[i] )
                            # NEXT
                            today = Calendar.getInstance()
                            writer.writerow([""])
                            writer.writerow(["StuWareSoftSystems - " + myScriptName + "("
                                             + version
                                             + ")  MoneyDance Python Script - Date of Extract: "
                                             + str(sdf.format(today.getTime()))])
                            writer.writerow(["Date Range Selected: "+str(userdateStart_ECH) + " to " +str(userdateEnd_ECH)])
                        else:
                            # Simplify is for my tester 'buddy' DerekKent23 - it's actually an MS Money Import format
                            lCurr = None
                            for row in theTable[1:]:
                                # Write the table, but swap in the raw numbers (rather than formatted number strings)
                                if row[_CURRNAME] != lCurr:
                                    if lCurr: writer.writerow("")
                                    lCurr = row[_CURRNAME]
                                    writer.writerow( [row[ _CURRNAME]+" - "+row[_CURRID]+" - "+row[_SYMB]+row[_SYMB+1]] )
                                    writer.writerow(["Date","Base to Rate","Rate to Base"])

                                writer.writerow([row[_SNAPDATE],
                                                row[_SNAPDATE+1],
                                                row[_SNAPDATE+2]])
                            # NEXT
                    myPrint("B", "CSV file " + csvfilename + " created, records written, and file closed..")

                except IOError, e:
                    myPrint("B", "Oh no - File IO Error!")
                    myPrint("B", e)
                    myPrint("B", sys.exc_type)
                    myPrint("B", "Path:", csvfilename)
                    myPrint("B", "!!! ERROR - No file written - sorry! (was file open, permissions etc?)".upper())
            # enddef

            def fixFormatsStr(theString, lNumber=False, sFormat=""):
                global lStripASCII

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
                    all_ASCII = ''.join(char for char in theString if
                                        ord(char) < 128)  # Eliminate non ASCII printable Chars too....
                else:
                    all_ASCII = theString
                return all_ASCII

            ExportDataToFile(currencyTable, header)

        def save_StuWareSoftSystems_parameters_to_file():
            global debug  # Set to True if you want verbose messages, else set to False....
            global lStripASCII, csvDelimiter, scriptpath
            global lDisplayOnly, version, myParameters
            global userdateformat
            global lSimplify_ECH, userdateStart_ECH, userdateEnd_ECH, hideHiddenCurrencies_ECH

            if debug: print "In ", inspect.currentframe().f_code.co_name, "()"

            # NOTE: Parameters were loaded earlier on... Preserve existing, and update any used ones...
            # (i.e. other StuWareSoftSystems programs might be sharing the same file)

            if myParameters is None: myParameters = {}

            myParameters["__Author"] = "Stuart Beesley - (c) StuWareSoftSystems"
            myParameters["__extract_currency_history_csv"] = version
            myParameters["userdateformat"] = userdateformat
            myParameters["lStripASCII"] = lStripASCII
            myParameters["csvDelimiter"] = csvDelimiter
            myParameters["debug"] = debug

            myParameters["lSimplify_ECH"] = lSimplify_ECH
            myParameters["userdateStart_ECH"] = userdateStart_ECH
            myParameters["userdateEnd_ECH"] = userdateEnd_ECH
            myParameters["hideHiddenCurrencies_ECH"] = hideHiddenCurrencies_ECH

            if not lDisplayOnly and scriptpath != "" and os.path.isdir(scriptpath):
                myParameters["scriptpath"] = scriptpath

            myFile = "StuWareSoftSystems.dict"
            # Pickle was originally encrypted, no need, migrating to unencrypted
            migratedFilename = os.path.join(moneydance_data.getRootFolder().getAbsolutePath(),myFile)

            if debug: print "Will try to save parameter file:", migratedFilename

            ostr = FileOutputStream(migratedFilename)

            myPrint("J", "about to Pickle.dump and save parameters to unencrypted file:", migratedFilename)

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

            return
        # ENDDEF

        save_StuWareSoftSystems_parameters_to_file()

else:
    pass


print "-----------------------------------------------------------------"
print
myPrint("B", "StuWareSoftSystems - ", os.path.basename(__file__), " script ending......")
print

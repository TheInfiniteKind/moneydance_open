#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# ######################################################################################################################
# The Infinite Kind (Moneydance) - Co-authored by Stuart Beesley in collaboration with Moneydance as a support tool
#
# Moneydance Support Tool
# ######################################################################################################################

# toolbox.py build: 1026 - November 2020 thru February 2021 - Stuart Beesley StuWareSoftSystems (~500 programming hours)
# Thanks and credit to Derek Kent(23) for his extensive testing and suggestions....
# Further thanks to Kevin(N), Dan T Davis, and dwg for their testing, input and OFX Bank help/input.....
# Credit of course to Moneydance and they retain all copyright over Moneydance internal code
# Designed to show user a number of settings / fixes / updates they may find useful (some normally hidden)
# The Basic / Geek Out Mode(s) are very safe and do not change any data or settings
# If you switch to Advanced / Hacker mode(s) then you have the ability to perform fixes, change data, change config etc
# NOTE: Any change that impacts config.dict, custom_theme.properties, LocalStorage() ./safe/settings...
#       will always backup that single config/settings file (in the directory where it's located).
#       This is not the same as backing up your Dataset that contains your financial data.

# NOTE: You will see some usage of globals... I wrote this when I was learning Python and Java... Know I know a lot more,
# I would do this differently, but leaving this as-is for now...

# DISCLAIMER >> PLEASE ALWAYS BACKUP YOUR DATA BEFORE MAKING CHANGES (Menu>Export Backup will achieve this)

# Includes previous / standalone scripts (which I have now decommissioned):
# FIX-reset_window_location_data.py 0.2beta
# DIAG-can_i_delete_security.py v2
# DIAG-list_security_currency_decimal_places.py v1
# DIAG-diagnose_currencies.py v2a
# fix_macos_tabbing_mode.py v1b

# Also includes these MD scripts (enhanced)
# reset_relative_currencies.py                          (from Moneydance support)
# remove_ofx_account_bindings.py                        (from Moneydance support)
# convert_secondary_to_primary_data_set.py              (from Moneydance support)
# remove_one_service.py                                 (from Moneydance support)
# delete_invalid_txns.py                                (from Moneydance support)
# price_history_thinner.py                              (from Moneydance support)
# fix_dropbox_one_way_syncing.py                        (from Moneydance support)
# reset_sync_and_dropbox_settings.py                    (from Moneydance support)
# force_change_account_currency.py                      (from Moneydance support)
# fix_restored_accounts.py (check only)                 (from Moneydance support)
# export_all_attachments.py                             (from Moneydance support)
# fix_account_parent.py                                 (from Moneydance support)
# (... and old check_root_structure.py)                 (from Moneydance support)
# fix_non-hierarchical_security_account_txns.py         (from Moneydance support)
# (... and fix_investment_txns_to_wrong_security.py)    (from Moneydance support)
# remove_ofx_security_bindings.py                       (from Moneydance support)
# show_object_type_quantities.py                        (from Moneydance support)
# delete_intermediate_downloaded_transaction_caches.py  (from Moneydance support)
# delete_orphaned_downloaded_txn_lists.py               (from Moneydance support)
# set_account_type.py                                   (from Moneydance support)
# force_change_all_currencies.py                        (from Moneydance support)
# fix_invalid_currency_rates.py                         (from Moneydance support)
# reverse_txn_amounts.py                                (from Moneydance support)
# reverse_txn_exchange_rates_by_account_and_date.py     (from Moneydance support)
# show_open_tax_lots.py                                 (author unknown)
# MakeFifoCost.py                                       (author unknown)
# change-security-cusip.py                              (from Finite Mobius, LLC / Jason R. Miller)
# https://github.com/finitemobius/moneydance-py

###############################################################################
# MIT License
#
# Copyright (c) 2020 Stuart Beesley - StuWareSoftSystems & Infinite Kind (Moneydance)
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

# Build: 999 PREVIEW RELEASE
# Build: 999a Added some instructions on how to properly edit Moneydance.vmoptions file; added to help file(s)
# Build: 999a Now finds the application directory for MacOS too....
# Build: 1000 INITIAL PUBLIC RELEASE
# Build: 1001 Enhanced MyPrint to catch unicode utf-8 encode/decode errors
# Build: 1002 - fixed raise(Exception) clauses ;->
# Build: 1002 - Now leveraging the Default font set in Moneydance; added change Fonts Button
# Build: 1003 - Updated common codeset
# Build: 1004 - Removed TxnSortOrder from common code, and catch error on import for earlier versions of MD
# Build: 1004 - Fix for Jython 2.7.1 where csv.writer expects a 1-byte string delimiter, not unicode....
# Build: 1005 - Tweaked for 2021 build 3032 (fonts/preferences)
# Build: 1006 - Detect when the .moneydancesync folder is missing and add button to fix this
# Build: 1006 - Detect current Toolbox version from github.. added downloadStuWareSoftSystemsExtensions() to common code
# Build: 1007 - Renamed REPO, Moneydance and ID to lowercase ready for signing (Sean request)...
# Build: 1008 - Cosmetic changes to searching window; update available windows...
# Build: 1008 - new button; search for ios sync data for sync key recovery....
# Build: 1008 - New hacker buttons; Moneydance internal DEBUG ON/OFF; Moneydance ofx connection console debug ON/OFF check; set check days
# Build: 1009 - Changed JFrame() to leverage internal moneydance's main frame size/dimensions etc.... (IK request)
# Build: 1010 - Tweaks to popup boxes to fit text for certain fonts and common imports
# Build: 1011 - Added "code_font" setting (which got sneaked into MD).... (and the print font setting too while I was at it); also corrected where font set to 'null' in config.dict
# Build: 1012 - Tweak to code_font display message
# Build: 1013 - Added Diagnose Attachments button(also detects Orphans)
# Build: 1014 - Added size and date to search for dataset outputs
# Build: 1014 - Enhanced main Frame to resize components on resize....; also the QuickJFrame; Small fix to Geek out mode error....:->
# Build: 1015 - Added more scripts as buttons: price_history_thinner.py
# Build: 1016 - Added Hacker button; save trunk file (false)
# Build: 1016 - Added Advanced Mode Button - fix one way syncing
# Build: 1017 - Added script: change-security-cusip.py; print message when checking dataset name vs root name; enhancements to price_history_thinner
# Build: 1018 - Override and reduce font point-size down to 18 max
# Build: 1018 - Tweaks to reset_relative_currencies - fix known error conditions / bugs in MD
# Build: 1019 - Added database objects count t  o main diagnostic screen.....
# Build: 1019 - Added support script: force_change_account_currency.py as a new button
# Build: 1019 - Added Hacker mode button to suppress the your file is stored in Dropbox warning (with disclaimer etc)
# Build: 1019 - Move the triple confirmation, backup, disclaimer messages to one common function
# Build: 1019 - Moved all OFX Function to a new Online Bank (OFX) Menu
# Build: 1019 - Changed the GeekOut mode to sort some objects first before selection....; major update to fix relative currencies
# Build: 1020 - Added button to analise dataset objects, files and sizes...; enhanced debug mode (same as console); use mono font in common code MyPopUpDialogBox()
# Build: 1020 - Massive update to OFX management, new button, menu, updated outputs with extensive data...; updates to Hacker mode
# Build: 1020 - Allow escape in common QuickJFrames and Popup dialogs.... (triggers cancel)
# Build: 1020 - Detect missing or invalid ROOT account based on fix_restored_accounts.py (but no fix as I don;t think it's needed any more)...
# Build: 1020 - Extract Attachments button
# Build: 1020 - added fix_account_parent.py script as a button
# Build: 1020 - added show_open_tax_lots.py script as a button
# Build: 1020 - added MakeFifoCost.py script as a button
# Build: 1020 - added Linux instructions to view .vmoptions for screen scaling
# Build: 1020 - change to use common function for backup confirm disclaimer etc....
# Build: 1020 - Geekout and searches for OFX bank data significantly improved
# Build: 1020 - Bug fix finding location of backup dir
# Build: 1020 - Enabled auto-pruning of internal backups of config.dict, settings, custom_themes
# Build: 1020 - Added Hacker buttons to clean up the external file/open list and also delete these datasets, and also internal datasets
# Build: 1020 - added .dispose and del of FileDialog objects after usage as otherwise it remembers the last directory selected.....
# Build: 1020 - Removed OFX console debug window; not needed. The debug in console is good enough/better already
# Build: 1020 - Forces all Moneydance Debugs ON - same as console window - at launch (rather than launching console window)
# Build: 1020 - New Hacker button for extra debug options
# Build: 1020 - Listen to MD Events.. Close Toolbox down when switching datasets.... (called when MD flags new file has been opened)
# Build: 1020 - save parameters everytime the menu option changes (in case program is killed or MD exits)
# Build: 1020 - script now checks for version information online and updates it's own defaults....
# Build: 1020 - Added button / script fix_non-hierarchical_security_account_txns.py (and fix_investment_txns_to_wrong_security.py)
# Build: 1020 - script now dials home to check for updated version information etc.... (any error/not found, it just ignores and carries on)
# Build: 1020 - RELEASE 2.0: New Diag and Fix buttons (incl. Thin Price History and more); New OFX Bank Management Menu; many updates to Hacker mode
# Build: 1021 - Tweak to delete int/ext files workflow; changed open file to JFileChooser() when I don't want remembered directories (Java 'feature')
# Build: 1021 - Tweak to find my dataset, don't report .moneydance folder as a dataset in the counts.. fixed display of archives found count..
# Build: 1021 - Applied same cosmetic tweaks to Find iOS Dataset too....
# Build: 1021 - Added please wait message when extracting attachments....
# Build: 1021 - Somehow lost the Hack menu DEBUG toggle button... Put back....
# Build: 1022 - Cosmetic tweak to curr/sec dpc to show something when blank name...
# Build: 1022 - Added the older Import QIF file button; added service.clearAuthenticationCache() to remove_one_service.py script
# Build: 1022 - Added delete_intermediate_downloaded_transaction_caches.py script to OFX banking menu
# Build: 1022 - Re-badged as InfiniteKind - co-authored by Stuart Beesley
# Build: 1022 - Added size of database objects to analyse objects button
# Build: 1023 - Added option after search for datasets to add missing files to config.dict and file open menu; also excluded /System from search on Macs
# Build: 1023 - Added Force change Account type button to advanced menu (set_account_type.py)
# Build: 1023 - Added Force change all Accounts' currencies to advanced menu (force_change_all_currencies.py)
# Build: 1023 - Started the journey (due to learning) to ensure unicode used everywhere (rather than byte strings) (yes; I learnt coding back in the 80s!)
# Build: 1023 - Error trapped diagnostic display - crashed on non utf8 characters - and also when decimal local grouping character was nbsp (chr(160)) - fixed....
# Build: 1023 - added button fix invalid currency rates to advanced menu (fix_invalid_currency_rates.py)
# Build: 1023 - Updated search datasets and search ios backups to skip symbolic links.... also skip some system dirs on some platforms
# Build: 1024 - Updated search so that it asks again after 10 mins, but then also carries on if no response after 10 seconds
# Build: 1024 - Moved some buttons to the toolbar...
# Build: 1024 - Fix for when System Property "HomeDir" is None on Mac (thanks Sean!). Comma in wrong place....!
# Build: 1025 - New hacker button - Import a file into Local storeage....
# Build: 1025 - Allow " " and "'" in key data values when editing in Hacker mode..; Added option to demote Primary to Secondary Sync Node
# Build: 1025 - Added script reverse_txn_amounts.py to Transaction Menu - advanced mode
# Build: 1025 - Added script reverse_txn_exchange_rates_by_account_and_date.py to Transaction Menu - advanced mode
# Build: 1025 - Revamped button/menu system. As many buttons as poss on sub-menus...
# Build: 1025 - small fix for is_moneydance_loaded_properly() when using MD build 2012
# Build: 1026 - Enhancements to detect when extension is already running....
# Build: 1026 - Detect when .moneydance and or .moneydancesync folder(s) are readonly/hidden - alert only

# todo - Known  issue  on Linux: Any drag to  resize main window, causes width to maximise. No issue on Mac or Windows..

# NOTE - I Use IntelliJ IDE - you may see # noinspection Pyxxxx or # noqa comments
# These tell the IDE to ignore certain irrelevant/erroneous warnings being reporting:
# Also: These objects: moneydance_ui, moneydance_data, moneydance are set as ignore Unresolved References (as they exist at run time)
# Further options at: https://www.jetbrains.com/help/pycharm/disabling-and-enabling-inspections.html#comments-ref


# Detect another instance of this code running in same namespace - i.e. a Moneydance Extension
# CUSTOMIZE AND COPY THIS ##############################################################################################
# CUSTOMIZE AND COPY THIS ##############################################################################################
# CUSTOMIZE AND COPY THIS ##############################################################################################

global toolbox_frame_, myModuleID

myModuleID = u"toolbox"                                                                                              # noqa

from java.lang import System
from javax.swing import JFrame

class MyJFrame(JFrame):

    def __init__(self, frameTitle=None):
        super(JFrame, self).__init__(frameTitle)
        self.isActiveInMoneydance = False
        self.MoneydanceAppListener = None


def getMyJFrame( moduleName ):
    frames = JFrame.getFrames()
    for fr in frames:
        if (fr.getName().lower().startswith(u"%s_main" %moduleName)
                and type(fr).__name__ == MyJFrame.__name__                         # isinstance() won't work across namespaces
                and fr.isActiveInMoneydance):
            print("%s: Found live frame: %s" %(myModuleID,fr.getName()))
            System.err.write("%s: Found live frame: %s\n" %(myModuleID, fr.getName()))
            return fr
    return None


frameToResurrect = None
if (u"%s_frame_"%myModuleID in globals()
        and isinstance(toolbox_frame_, MyJFrame)
        and toolbox_frame_.isActiveInMoneydance):
    frameToResurrect = toolbox_frame_
    print("%s: Detected that %s is already running in same namespace..... Attempting to resurrect.." %(myModuleID, myModuleID))
    System.err.write("%s: Detected that %s is already running in same namespace..... Attempting to resurrect..\n" %(myModuleID, myModuleID))
elif getMyJFrame( myModuleID ) is not None:
    frameToResurrect = getMyJFrame( myModuleID )
    print("%s: Detected that %s is already running in another namespace..... Attempting to resurrect.." %(myModuleID, myModuleID))
    System.err.write("%s: Detected that %s is already running in another namespace..... Attempting to resurrect..\n" %(myModuleID, myModuleID))

if frameToResurrect:
    try:
        frameToResurrect.setVisible(True)
        if frameToResurrect.getExtendedState() == JFrame.ICONIFIED:
            frameToResurrect.setExtendedState(JFrame.NORMAL)
        frameToResurrect.toFront()
    except:
        print("%s: Failed to resurrect main Frame.. This duplicate Script/extension is now terminating....." %(myModuleID))
        System.err.write("%s: Failed to resurrect main Frame.. This duplicate Script/extension is now terminating.....\n" %(myModuleID))
        raise Exception("SORRY - YOU CAN ONLY HAVE ONE INSTANCE OF %s RUNNING AT ONCE" %(myModuleID.upper()))

else:
    print("%s: No other 'live' instances of this program detected - running as normal" %(myModuleID))
    System.err.write("%s: No other instances of this program detected - running as normal\n" %(myModuleID))

    # COMMON IMPORTS #######################################################################################################
    # COMMON IMPORTS #######################################################################################################
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

    from javax.swing import JButton, JScrollPane, WindowConstants, JLabel, JPanel, JComponent, KeyStroke, JDialog, JComboBox
    from javax.swing import JOptionPane, JTextArea, JMenuBar, JMenu, JMenuItem, AbstractAction, JCheckBoxMenuItem, JFileChooser
    from javax.swing import JTextField, JPasswordField, Box, UIManager, JTable, JCheckBox, JRadioButton, ButtonGroup
    from javax.swing.text import PlainDocument
    from javax.swing.border import EmptyBorder

    from java.awt import Color, Dimension, FileDialog, FlowLayout, Toolkit, Font, GridBagLayout, GridLayout
    from java.awt import BorderLayout, Dialog, Insets
    from java.awt.event import KeyEvent, WindowAdapter, InputEvent
    from java.util import Date

    from java.text import DecimalFormat, SimpleDateFormat
    from java.util import Calendar, ArrayList
    from java.lang import Double, Math, Character
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
    version_build = "1026"                                                                                              # noqa
    myScriptName = u"%s.py(Extension)" %myModuleID                                                                      # noqa
    debug = False                                                                                                       # noqa
    myParameters = {}                                                                                                   # noqa
    _resetParameters = False                                                                                            # noqa
    lPickle_version_warning = False                                                                                     # noqa
    lIamAMac = False                                                                                                    # noqa
    lGlobalErrorDetected = False																						# noqa
    MYPYTHON_DOWNLOAD_URL = "https://yogi1967.github.io/MoneydancePythonScripts/"                                       # noqa
    # END SET THESE VARIABLES FOR ALL SCRIPTS ##############################################################################

    # >>> THIS SCRIPT'S IMPORTS ############################################################################################
    import re
    import fnmatch
    import subprocess
    import time
    import shutil

    from java.util import Timer, TimerTask

    from com.moneydance.apps.md.view.gui import theme
    from com.moneydance.apps.md.view.gui.theme import Theme
    from com.moneydance.apps.md.view.gui.sync import SyncFolderUtil
    from com.moneydance.apps.md.controller import ModuleMetaData
    from com.moneydance.apps.md.controller import LocalStorageCipher
    from com.moneydance.apps.md.controller import Common
    from com.moneydance.apps.md.controller import BalanceType
    from com.moneydance.apps.md.controller.io import FileUtils, AccountBookUtil
    from com.moneydance.apps.md.controller import ModuleLoader
    from java.awt import GraphicsEnvironment, Desktop

    from java.awt.event import WindowEvent
    from java.lang import Runnable, Thread

    from com.infinitekind.util import StreamTable, StreamVector, IOUtils, StringUtils, CustomDateFormat
    from com.infinitekind.moneydance.model import ReportSpec, AddressBookEntry, OnlineService, MoneydanceSyncableItem
    from com.infinitekind.moneydance.model import OnlinePayeeList, OnlinePaymentList, InvestFields
    from com.infinitekind.moneydance.model import CurrencySnapshot, CurrencySplit, OnlineTxnList
    from com.infinitekind.tiksync import SyncRecord
    from com.moneydance.apps.md.controller import Util
    from com.infinitekind.tiksync import SyncableItem

    from com.moneydance.apps.md.view.gui.txnreg import DownloadedTxnsView
    from com.moneydance.apps.md.view.gui import OnlineUpdateTxnsWindow

    from com.moneydance.apps.md.controller import AppEventListener

    from com.moneydance.apps.md.view.gui import ConsoleWindow
    from com.infinitekind.tiksync import Syncer
    from com.moneydance.apps.md.controller.olb.ofx import OFXConnection
    from com.moneydance.apps.md.controller.olb import MoneybotURLStreamHandlerFactory
    from com.infinitekind.moneydance.online import OnlineTxnMerger
    from com.moneydance.apps.md.view.gui import MDAccountProxy
    from java.lang import Integer

    from java.awt.datatransfer import StringSelection
    from java.net import URL
    from java.nio.charset import Charset

    from java.awt.event import ComponentAdapter

    from java.util import UUID

    try:
        from com.infinitekind.moneydance.model import TxnSortOrder
        lImportOK = True
    except:
        lImportOK = False
    # >>> END THIS SCRIPT'S IMPORTS ########################################################################################

    # >>> THIS SCRIPT'S GLOBALS ############################################################################################
    global __TOOLBOX
    global toolbox_frame_, fixRCurrencyCheck, DARK_GREEN, lCopyAllToClipBoard_TB, _COLWIDTHS, lGeekOutModeEnabled_TB
    global lHackerMode, lAdvancedMode, lIgnoreOutdatedExtensions_TB, lMustRestartAfterSnapChanges, lAutoPruneInternalBackups_TB
    global globalSaveFI_data, globalSave_DEBUG_FI_data
    global OFX_SETUP_MATCH_MD_BUILD, TOOLBOX_MINIMUM_TESTED_MD_VERSION, TOOLBOX_MAXIMUM_TESTED_MD_VERSION, TOOLBOX_MAXIMUM_TESTED_MD_BUILD
    global MD_OFX_BANK_SETTINGS_DIR, MD_OFX_DEFAULT_SETTINGS_FILE, MD_OFX_DEBUG_SETTINGS_FILE, MD_EXTENSIONS_DIRECTORY_FILE
    global TOOLBOX_VERSION_VALIDATION_URL, TOOLBOX_STOP_NOW
    DARK_GREEN = Color(0, 192, 0)                                                                                       # noqa
    lCopyAllToClipBoard_TB = False                                                                                      # noqa
    lGeekOutModeEnabled_TB = False                                                                                      # noqa
    lIgnoreOutdatedExtensions_TB = False                                                                                # noqa
    lAutoPruneInternalBackups_TB = False                                                                                # noqa
    lHackerMode = False                                                                                                 # noqa
    lAdvancedMode = False                                                                                               # noqa
    _COLWIDTHS = ["bank", "cc", "invest", "security", "loan", "misc", "split","rec_credits","rec_debits","secdetail"]   # noqa
    lMustRestartAfterSnapChanges = False                                                                                # noqa
    globalSaveFI_data = None                                                                                            # noqa
    globalSave_DEBUG_FI_data = None                                                                                     # noqa
    TOOLBOX_STOP_NOW = False                                                                                            # noqa
    OFX_SETUP_MATCH_MD_BUILD =          3034                                                                            # noqa
    TOOLBOX_MINIMUM_TESTED_MD_VERSION = 2020.0                                                                          # noqa
    TOOLBOX_MAXIMUM_TESTED_MD_VERSION = 2021.1                                                                          # noqa
    TOOLBOX_MAXIMUM_TESTED_MD_BUILD =   3034                                                                            # noqa
    MD_OFX_BANK_SETTINGS_DIR = "https://infinitekind.com/app/md/fis/"                                                   # noqa
    MD_OFX_DEFAULT_SETTINGS_FILE = "https://infinitekind.com/app/md/fi2004.dict"                                        # noqa
    MD_OFX_DEBUG_SETTINGS_FILE = "https://infinitekind.com/app/md.debug/fi2004.dict"                                    # noqa
    MD_EXTENSIONS_DIRECTORY_FILE = "https://infinitekind.com/app/md/extensions.dct"                                     # noqa
    TOOLBOX_VERSION_VALIDATION_URL = "https://raw.githubusercontent.com/yogi1967/MoneydancePythonScripts/master/source/toolbox/toolbox_version_requirements.dict" # noqa
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
extract_data                            Extract various data to screen and/or csv.. Consolidation of:
- stockglance2020                       View summary of Securities/Stocks on screen, total by Security, export to csv 
- extract_reminders_csv                 View reminders on screen, edit if required, extract all to csv
- extract_currency_history_csv          Extract currency history to csv
- extract_investment_transactions_csv   Extract investment transactions to csv
- extract_account_registers_csv         Extract Account Register(s) to csv along with any attachments

list_future_reminders:                  View future reminders on screen. Allows you to set the days to look forward

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

        if debug or moneydance is None or moneydance_data is None or moneydance_ui is None:
            for theClass in ["moneydance",  moneydance], ["moneydance_ui",moneydance_ui], ["moneydance_data",moneydance]:
                myPrint("B","Moneydance Objects now....: Class: %s %s@{:x}".format(System.identityHashCode(theClass[1])) %(pad(theClass[0],20), theClass[1].__class__))
            myPrint("P","")

        if moneydance is not None and moneydance_data is not None and moneydance_ui is not None:                        # noqa
            if debug: myPrint("B","Success - Moneydance variables are already set....")
            return

        myPrint("B","ERROR - Moneydance variables are NOT set properly....!")

        # to cope with being run as Extension.... temporary
        if moneydance is not None and (moneydance_data is None or moneydance_ui is None):                                # noqa
            myPrint("B", "@@@ Moneydance variables not set (run as extension?) - attempting to manually set @@@")
            exec "global moneydance_ui;" + "moneydance_ui=moneydance.getUI();"
            exec "global moneydance_data;" + "moneydance_data=moneydance.getCurrentAccount().getBook();"

        for theClass in ["moneydance",moneydance], ["moneydance_ui",moneydance_ui], ["moneydance_data",moneydance]:
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
                self.fakeJFrame = MyJFrame()
                self.fakeJFrame.setName(u"%s_fake_dialog" %(myModuleID))
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

    def get_time_stamp_as_nice_text( timeStamp ):

        prettyDate = ""
        try:
            c = Calendar.getInstance()
            c.setTime(Date(timeStamp))
            dateFormatter = SimpleDateFormat("yyyy/MM/dd HH:mm:ss(.SSS) Z z zzzz")
            prettyDate = dateFormatter.format(c.getTime())
        except:
            pass

        return prettyDate

    def currentDateTimeMarker():
        c = Calendar.getInstance()
        dateformat = SimpleDateFormat("_yyyyMMdd_HHmmss")
        _datetime = dateformat.format(c.getTime())
        return _datetime

    def destroyOldFrames(moduleName):
        frames = JFrame.getFrames()
        for fr in frames:
            if fr.getName().lower().startswith(moduleName):
                myPrint("DB","Found old frame %s and active status is: %s" %(fr.getName(),fr.isActiveInMoneydance))
                # if fr.isActiveInMoneydance:
                try:
                    fr.isActiveInMoneydance = False
                    fr.setVisible(False)
                    fr.dispose()    # This should call windowClosed() which should remove MD listeners.....
                    myPrint("DB","disposed of old frame: %s" %(fr.getName()))
                except:
                    myPrint("B","Failed to dispose old frame: %s" %(fr.getName()))
                    dump_sys_error_to_md_console_and_errorlog()

    # END COMMON DEFINITIONS ###############################################################################################
    # END COMMON DEFINITIONS ###############################################################################################
    # END COMMON DEFINITIONS ###############################################################################################

    # >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
    # >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
    # >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
    def load_StuWareSoftSystems_parameters_into_memory():
        global debug, myParameters, lPickle_version_warning, version_build

        # >>> THESE ARE THIS SCRIPT's PARAMETERS TO LOAD
        global __TOOLBOX, lCopyAllToClipBoard_TB, lGeekOutModeEnabled_TB, lIgnoreOutdatedExtensions_TB, lAutoPruneInternalBackups_TB

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )
        myPrint("DB", "Loading variables into memory...")

        if myParameters is None: myParameters = {}

        if myParameters.get("__TOOLBOX") is not None: __TOOLBOX = myParameters.get("__TOOLBOX")
        if myParameters.get("lCopyAllToClipBoard_TB") is not None: lCopyAllToClipBoard_TB = myParameters.get("lCopyAllToClipBoard_TB")
        if myParameters.get("lGeekOutModeEnabled_TB") is not None: lGeekOutModeEnabled_TB = myParameters.get("lGeekOutModeEnabled_TB")
        if myParameters.get("lIgnoreOutdatedExtensions_TB") is not None: lIgnoreOutdatedExtensions_TB = myParameters.get("lIgnoreOutdatedExtensions_TB")
        if myParameters.get("lAutoPruneInternalBackups_TB") is not None: lAutoPruneInternalBackups_TB = myParameters.get("lAutoPruneInternalBackups_TB")

        myPrint("DB","myParameters{} set into memory (as variables).....")

        return

    # >>> CUSTOMISE & DO THIS FOR EACH SCRIPT
    def dump_StuWareSoftSystems_parameters_from_memory():
        global debug, myParameters, lPickle_version_warning, version_build

        # >>> THESE ARE THIS SCRIPT's PARAMETERS TO SAVE
        global __TOOLBOX, lCopyAllToClipBoard_TB, lGeekOutModeEnabled_TB, lIgnoreOutdatedExtensions_TB, lAutoPruneInternalBackups_TB

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )

        # NOTE: Parameters were loaded earlier on... Preserve existing, and update any used ones...
        # (i.e. other StuWareSoftSystems programs might be sharing the same file)

        if myParameters is None: myParameters = {}

        myParameters["__TOOLBOX"] = version_build
        myParameters["lCopyAllToClipBoard_TB"] = lCopyAllToClipBoard_TB
        myParameters["lGeekOutModeEnabled_TB"] = lGeekOutModeEnabled_TB
        myParameters["lIgnoreOutdatedExtensions_TB"] = lIgnoreOutdatedExtensions_TB
        myParameters["lAutoPruneInternalBackups_TB"] = lAutoPruneInternalBackups_TB

        myPrint("DB","variables dumped from memory back into myParameters{}.....")

        return

    get_StuWareSoftSystems_parameters_from_file()
    myPrint("DB", "DEBUG IS ON..")

    # clear up any old left-overs....
    destroyOldFrames(myModuleID)

    # END ALL CODE COPY HERE ###############################################################################################
    # END ALL CODE COPY HERE ###############################################################################################
    # END ALL CODE COPY HERE ###############################################################################################

    # noinspection PyBroadException
    def downloadStuWareSoftSystemsExtensions( what ):
        global i_am_an_extension_so_run_headless, debug

        dictInfo = StreamTable()

        inx = None
        theDict = "https://raw.githubusercontent.com/yogi1967/MoneydancePythonScripts/master/source/%s/meta_info.dict" %what

        try:
            myPrint("DB","About to open url: %s" %theDict)
            urlDict = URL(theDict)
            inx = BufferedReader(InputStreamReader(urlDict.openStream(), "UTF8"))
            dictInfo.readFrom(inx)
        except:
            myPrint("J","")
            myPrint("B", "ERROR downloading meta-info.dict from GitHub... ")
            if debug: dump_sys_error_to_md_console_and_errorlog()
            return False

        finally:
            if inx:
                try:
                    inx.close()
                except:
                    myPrint("B", "Error closing URL stream (%s)" %theDict)
                    dump_sys_error_to_md_console_and_errorlog()

        return dictInfo

    class DetectAndChangeMacTabbingMode(AbstractAction):

        def __init__(self,statusLabel,lQuickCheckOnly):
            self.statusLabel = statusLabel
            self.lQuickCheckOnly = lQuickCheckOnly

        def actionPerformed(self, event):
            global toolbox_frame_, debug

            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

            if not Platform.isOSX():
                if self.lQuickCheckOnly: return True
                myPrint("B", "Change Mac Tabbing Mode - This can only be run on a Mac!")
                self.statusLabel.setText("Change Mac Tabbing Mode - This can only be run on a Mac!".ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                myPopupInformationBox(toolbox_frame_,"Change Mac Tabbing Mode - This can only be run on a Mac!", theMessageType=JOptionPane.WARNING_MESSAGE)
                return

            if not Platform.isOSXVersionAtLeast("10.16"):
                if self.lQuickCheckOnly: return True
                myPrint("B", "Change Mac Tabbing Mode - You are not running Big Sur - no changes made!")
                self.statusLabel.setText(("Change Mac Tabbing Mode - You are not running Big Sur - no changes made!").ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                myPopupInformationBox(toolbox_frame_,"Change Mac Tabbing Mode - You are not running Big Sur - no changes made!", theMessageType=JOptionPane.WARNING_MESSAGE)
                return

            if (float(moneydance.getBuild()) > 1929 and float(moneydance.getBuild()) < 2008):                                         # noqa
                myPrint("B", "Change Mac Tabbing Mode - You are running 2021.build %s - This version has problems with DUAL MONITORS\nPlease upgrade to at least 2021. build 2012:\nhttps://infinitekind.com/preview" %moneydance.getBuild())
                self.statusLabel.setText(("You are running 2021.build %s - This version has problems with DUAL MONITORS - Upgrade to at least 2021. build 2012: https://infinitekind.com/preview" %moneydance.getBuild()).ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                myPopupInformationBox(toolbox_frame_,"Change Mac Tabbing Mode - You are running 2021.build %s - This version has problems with DUAL MONITORS\nPlease upgrade to at least 2021 first! build 2012:\nhttps://infinitekind.com/preview" %moneydance.getBuild(),theMessageType=JOptionPane.ERROR_MESSAGE)
                return

            prefFile = os.path.join(System.getProperty("UserHome", "Library/Preferences/.GlobalPreferences.plist"))
            if not os.path.exists(prefFile):
                if self.lQuickCheckOnly: return True
                myPrint("B", "Change Mac Tabbing Mode - Sorry - For some reason I could not find: %s - no changes made!" %prefFile)
                self.statusLabel.setText(("Change Mac Tabbing Mode - Sorry - For some reason I could not find: %s - no changes made!" %prefFile).ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                myPopupInformationBox(toolbox_frame_,"Change Mac Tabbing Mode - Sorry - For some reason I could not find: %s - no changes made!" %prefFile,theMessageType=JOptionPane.ERROR_MESSAGE)
                return

            try:
                tabbingMode = subprocess.check_output("defaults read -g AppleWindowTabbingMode", shell=True)
            except:
                if self.lQuickCheckOnly: return True
                myPrint("B", "Change Mac Tabbing Mode - Sorry - error getting your Tabbing mode! - no changes made!")
                self.statusLabel.setText(("Change Mac Tabbing Mode - Sorry - error getting your Tabbing mode! - no changes made!").ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                myPopupInformationBox(toolbox_frame_,"Change Mac Tabbing Mode\nSorry - error getting your Tabbing mode!\nno changes made!",theMessageType=JOptionPane.ERROR_MESSAGE)
                dump_sys_error_to_md_console_and_errorlog()
                return

            tabbingMode=tabbingMode.strip().lower()
            if not (tabbingMode == "fullscreen" or tabbingMode == "manual" or tabbingMode == "always"):
                if self.lQuickCheckOnly: return True
                myPrint("B", "Change Mac Tabbing Mode - Sorry - I don't understand your tabbing mode: %s - no changes made!" %tabbingMode)
                self.statusLabel.setText(("Change Mac Tabbing Mode - Sorry - I don't understand your tabbing mode: %s - no changes made!" %tabbingMode).ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                myPopupInformationBox(toolbox_frame_,"Change Mac Tabbing Mode - Sorry - I don't understand your tabbing mode:\n%s - no changes made!" %tabbingMode, theMessageType=JOptionPane.ERROR_MESSAGE)
                return

            if tabbingMode == "fullscreen" or tabbingMode == "manual":
                if self.lQuickCheckOnly:
                    myPrint("J","Quick check of MacOS tabbing showed it's OK and set to: %s" %tabbingMode)
                    return True
                myPrint("B", "\n@@@ Change Mac Tabbing Mode - NO PROBLEM FOUND - Your tabbing mode is: %s - no changes made!" %tabbingMode)
                self.statusLabel.setText(("Change Mac Tabbing Mode - NO PROBLEM FOUND - Your tabbing mode is: %s - no changes made!" %tabbingMode).ljust(800, " "))
                self.statusLabel.setForeground(Color.BLUE)
                myPopupInformationBox(toolbox_frame_,"Change Mac Tabbing Mode - NO PROBLEM FOUND - Your tabbing mode is: %s - no changes made!" %tabbingMode)
                return

            if self.lQuickCheckOnly:
                myPrint("J","Quick check of MacOS tabbing showed it's NEEDS CHANGING >> It's set to: %s" %tabbingMode)
                return False

            myPrint("B","More information here: https://support.apple.com/en-gb/guide/mac-help/mchla4695cce/mac")

            myPrint("B", "@@@ PROBLEM - Your Tabbing Mode is set to: %s - NEEDS CHANGING" %tabbingMode)
            myPopupInformationBox(toolbox_frame_,"@@@ PROBLEM - Your Tabbing Mode is set to: %s\nTHIS NEEDS CHANGING!" %tabbingMode,theMessageType=JOptionPane.ERROR_MESSAGE)
            myPopupInformationBox(toolbox_frame_,"Info:\n<https://support.apple.com/en-gb/guide/mac-help/mchla4695cce/mac>\nPress OK to select new mode...",theMessageType=JOptionPane.ERROR_MESSAGE)

            mode_options = ["fullscreen", "manual"]
            selectedMode = JOptionPane.showInputDialog(toolbox_frame_,
                                                        "TABBING MODE", "Select the new Tabbing Mode?",
                                                        JOptionPane.WARNING_MESSAGE,
                                                        moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                        mode_options,
                                                        None)
            if selectedMode is None:
                self.statusLabel.setText("Change Mac Tabbing Mode - No new Tabbing Mode was selected - aborting..".ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                myPopupInformationBox(toolbox_frame_,"Change Mac Tabbing Mode - No new Tabbing Mode was selected - aborting..")
                return

            disclaimer = myPopupAskForInput(toolbox_frame_,
                                            "TABBING MODE",
                                            "DISCLAIMER:",
                                            "Are you really sure you want to change MacOS system setting>>Tabbing Mode? Type 'IAGREE' to continue..",
                                            "NO",
                                            False,
                                            JOptionPane.ERROR_MESSAGE)

            if not disclaimer == 'IAGREE':
                self.statusLabel.setText("Change Mac Tabbing Mode - User declined the disclaimer - no changes made....".ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                myPopupInformationBox(toolbox_frame_,"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
                return

            try:
                tabbingModeChanged = subprocess.check_output('defaults write -g AppleWindowTabbingMode -string "%s"' %selectedMode, shell=True)
                if tabbingModeChanged.strip() != "":
                    myPrint("B", "Tabbing mode change output>>>>")
                    myPrint("B", tabbingModeChanged)
                myPrint("B","!!! Your tabbing mode has been changed to %s - Please exit and restart Moneydance" %selectedMode)
            except:
                myPrint("B", "Change Mac Tabbing Mode - Sorry - error setting your Tabbing mode! - no changes made!")
                self.statusLabel.setText((")").ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                myPopupInformationBox(toolbox_frame_,"Change Mac Tabbing Mode\nSorry - error getting your Tabbing mode! - no changes made!", theMessageType=JOptionPane.ERROR_MESSAGE)
                dump_sys_error_to_md_console_and_errorlog()
                return

            if tabbingModeChanged.strip() != "":
                myPopupInformationBox(toolbox_frame_,"Change Mac Tabbing Mode: Response: %s" %tabbingModeChanged, JOptionPane.WARNING_MESSAGE)

            self.statusLabel.setText(("MacOS Tabbing Mode: OK I Made the Change to your Mac Tabbing Mode: Please exit and restart Moneydance...").ljust(800, " "))
            self.statusLabel.setForeground(Color.RED)
            myPopupInformationBox(toolbox_frame_,"OK I Made the Change to your Mac Tabbing Mode: Please exit and restart Moneydance...",theMessageType=JOptionPane.WARNING_MESSAGE)

            return

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

    # noinspection PyBroadException
    def buildDiagText():

        textArray = []                                                                                                  # noqa

        textArray.append(u"Moneydance Version / Build: %s" %(moneydance.getVersion()) + u"  Build: %s" %(moneydance.getBuild()))
        textArray.append(u"Moneydance Config file reports: %s" %moneydance_ui.getPreferences().getSetting(u"current_version", u""))
        textArray.append(u"Moneydance updater version to track: %s" %moneydance_ui.getPreferences().getSetting(u"updater.version_to_track",u""))

        currLicense = moneydance_ui.getPreferences().getSetting(u"gen.lic_key2021",
                                                                moneydance_ui.getPreferences().getSetting(u"gen.lic_key2019",
                                                                moneydance_ui.getPreferences().getSetting(u"gen.lic_key2017",
                                                                moneydance_ui.getPreferences().getSetting(u"gen.lic_key2015",
                                                                moneydance_ui.getPreferences().getSetting(u"gen.lic_key2014",
                                                                moneydance_ui.getPreferences().getSetting(u"gen.lic_key2011",
                                                                moneydance_ui.getPreferences().getSetting(u"gen.lic_key2010",
                                                                moneydance_ui.getPreferences().getSetting(u"gen.lic_key2004",
                                                                moneydance_ui.getPreferences().getSetting(u"gen.lic_key",u"?")))))))))

        license2021 = moneydance_ui.getPreferences().getSetting(u"gen.lic_key2021", None)                               # noqa
        license2019 = moneydance_ui.getPreferences().getSetting(u"gen.lic_key2019", None)
        license2017 = moneydance_ui.getPreferences().getSetting(u"gen.lic_key2017", None)
        license2015 = moneydance_ui.getPreferences().getSetting(u"gen.lic_key2015", None)
        license2014 = moneydance_ui.getPreferences().getSetting(u"gen.lic_key2014", None)
        license2011 = moneydance_ui.getPreferences().getSetting(u"gen.lic_key2011", None)
        license2010 = moneydance_ui.getPreferences().getSetting(u"gen.lic_key2010", None)
        license2004 = moneydance_ui.getPreferences().getSetting(u"gen.lic_key2004", None)

        if moneydance_ui.getMain().isRegistered():
            textArray.append(u"LICENSED: %s" %currLicense)
        else:
            textArray.append(u"UNLICENSED!")

        if license2019:      textArray.append(u" >old licenses (2019): " + license2019)
        if license2017:      textArray.append(u" >old licenses (2017): " + license2017)
        if license2015:      textArray.append(u" >old licenses (2015): " + license2015)
        if license2014:      textArray.append(u" >old licenses (2014): " + license2014)
        if license2011:      textArray.append(u" >old licenses (2011): " + license2011)
        if license2010:      textArray.append(u" >old licenses (2010): " + license2010)
        if license2004:      textArray.append(u" >old licenses (2004): " + license2004)

        if not moneydance_data: textArray.append(u"Moneydance datafile is empty")
        x = moneydance_ui.getPreferences().getSetting(u"current_accountbook", None)
        y = moneydance_ui.getPreferences().getSetting(u"current_account_file", None)

        theExtn = os.path.splitext((moneydance_data.getRootFolder().getCanonicalPath()))

        if x:
            textArray.append(u"Current Dataset: %s" %(x))
        if y:
            textArray.append(u"Current Dataset: %s" %(y))

        textArray.append(u"Full location of this Dataset: %s" %(moneydance_data.getRootFolder()))

        x = find_the_program_install_dir()
        if x:
            textArray.append(u"Application Install Directory: %s" %(x))
        else:
            textArray.append(u"UNABLE TO DETERMINE Application's Install Directory?!")


        lDropbox, lSuppressed = check_dropbox_and_suppress_warnings()
        if lDropbox:
            textArray.append(u"\n@@ WARNING: You have your dataset installed in Dropbox - This can damage your data!")
            if lSuppressed:
                textArray.append(u"@@ WARNING: You have also SUPPRESSED the warning messages - THIS IS AT YOUR OWN RISK!")
            textArray.append(u"@@ The recommendation is to move your Dataset to your local drive (out of Dropbox) and a) use MD's internal Sync feature, or b) set Dropbox as the location for MD Backups\n")

        textArray.append(u"\nRUNTIME ENVIRONMENT")

        textArray.append(u"Java version: %s"  %(System.getProperty(u"java.version")))
        textArray.append(u"Java vendor: %s"  %(System.getProperty(u"java.vendor")))

        textArray.append(u"Platform: " + platform.python_implementation()
                         + u" " + platform.system() + " %s" %(sys.version_info.major)
                         + u"" + ".%s" %(sys.version_info.minor))

        textArray.append(u"SandBoxed: %s" %(moneydance.getPlatformHelper().isSandboxed()))
        textArray.append(u"Restricted: %s" %(moneydance.getPlatformHelper().isConstrainedToSandbox()))

        if moneydance.getExecutionMode() == moneydance.EXEC_MODE_APP:
            textArray.append(u"MD Execution Mode: %s" %(moneydance.getExecutionMode()) + u" = APP (Normal App)")
        elif moneydance.getExecutionMode() == moneydance.EXEC_MODE_APPLET:
            textArray.append(u"MD Execution Mode: %s" %(moneydance.getExecutionMode()) + u" = APPLET (probably from an AppStore?")
        else:
            textArray.append(u"MD Execution Mode: %s" %(moneydance.getExecutionMode()))

        textArray.append(u"MD Debug Mode: %s" %(moneydance.DEBUG))
        textArray.append(u"Beta Features: %s" %(moneydance.BETA_FEATURES))
        textArray.append(u"Architecture: %s" %(System.getProperty(u"os.arch")))

        if theExtn and theExtn[1].strip() != u"":
            textArray.append(u"File Extension: %s" %theExtn[1])
        else:
            textArray.append(u"File Extension: %s" %(moneydance.FILE_EXTENSION))

        textArray.append(u"Operating System file encoding is: %s" %(Charset.defaultCharset()))
        textArray.append(u"Python default character encoding has been set to: %s" %(sys.getfilesystemencoding()) + u" (the normal default is ASCII)")

        try:
            # New for MD2020.2012
            x = moneydance_ui.getFonts().code
        except:
            myPrint("B",u"Failed to get Moneydance code font (must be older version), loading older mono")
            x = moneydance_ui.getFonts().mono

        textArray.append(u"Python default display font: " + x.getFontName() + u" size: %s" %(x.getSize()))

        textArray.append(u"\nMaster Node (dataset): %s" %(moneydance_data.getLocalStorage().getBoolean(u"_is_master_node", True)))

        textArray.append(u"\nENCRYPTION")
        x = moneydance_ui.getCurrentAccounts().getEncryptionKey()
        if x is None or x == u"":
            x = u"Encryption not set! - This means an internal Moneydance passphrase is being used to encrypt your dataset!"
        else:
            x = u"***************"
        textArray.append(u"'Master' / Encryption Passphrase: %s" %x)

        x = u"Encryption Store Online Banking (OFX) Passwords in File: %s" %(moneydance_ui.getCurrentAccounts().getBook().getLocalStorage().getBoolean(u"store_passwords", False))
        if moneydance_ui.getCurrentAccounts().getBook().getLocalStorage().getBoolean(u"store_passwords", False):
            textArray.append(x+u" (This means you are able to save your online banking passwords)")
        else:
            textArray.append(x+u"\n>>You cannot save online banking passwords until you set a 'Master' (encryption) password **AND** select 'Store Online Passwords in File'\n")

        x = moneydance_ui.getCurrentAccounts().getEncryptionHint()
        if x is None or x == u"":
            x = u"Encryption passphrase hint not set!"
        else:
            x = u"***************"
        textArray.append(u"Encryption passphrase hint: %s" %x)

        # if moneydance_ui.getCurrentAccounts().getEncryptionLevel(): # Always reports des - is this legacy?
        if moneydance.getRootAccount().getParameter(u"md.crypto_level", None):
            x = u"Encryption level - Moneydance reports: %s (but I believe this is a legacy encryption method??)" %moneydance_ui.getCurrentAccounts().getEncryptionLevel()
            textArray.append(x)
        else:
            x = u"My Encryption 'test' of your key/passphrase reports: %s\n" %(getMDEncryptionKey())
            x += u"I understand the dataset encryption is: AES 128-bit. Passphrase encrypted using PBKDF2WithHmacSHA512 " \
                 u"(fixed internal salt, high iteration) and then your (secure/random) key is encrypted and used to encrypt " \
                 u"data to disk using AES/CBC/PKCS5Padding with a fixed internal IV"
            textArray.append(x)

        textArray.append(u"\nSYNC DETAILS")
        # SYNC details
        x = moneydance_ui.getCurrentAccounts().getSyncEncryptionPassword()
        if x is None or x == u"":
            x = u"Sync passphrase not set!"
        else:
            x = u"***************"
        textArray.append(u"Sync Password: %s" %x)

        syncMethods = SyncFolderUtil.getAvailableFolderConfigurers(moneydance_ui, moneydance_ui.getCurrentAccounts())
        noSyncOption = SyncFolderUtil.configurerForIDFromList(u"none", syncMethods)
        syncMethod = SyncFolderUtil.getConfigurerForFile(moneydance_ui, moneydance_ui.getCurrentAccounts(), syncMethods)
        if syncMethod is None:
            syncMethod = noSyncOption
        else:
            syncMethod = syncMethod
        textArray.append(u"Sync Method: %s" %(syncMethod.getSyncFolder()))

        if not check_for_dropbox_folder():
            textArray.append(u"Sync WARNING: Dropbox sync will not work until you add the missing .moneydancesync folder - use advanced mode to fix!")

        textArray.append(u"\nTHEMES")
        textArray.append(u"Your selected Theme: %s" %(moneydance_ui.getPreferences().getSetting(u"gui.current_theme", Theme.DEFAULT_THEME_ID)))
        # noinspection PyUnresolvedReferences
        x = theme.Theme.customThemeFile.getCanonicalPath()
        if not os.path.exists(x):
            x = u" custom_theme.properties file DOES NOT EXIST!"
        textArray.append(u"Custom Theme File: %s" %(x))
        # noinspection PyUnresolvedReferences
        textArray.append(u"Available themes: %s" %(theme.Theme.getAllThemes()))

        textArray.append(u"\nENVIRONMENT")

        try:
            username = System.getProperty(u"user.name")
        except:
            username = u"???"
        textArray.append(u"Username: %s" %username)

        textArray.append(u"OS Platform: %s" %System.getProperty(u"os.name") + u"OS Version: %s" %(System.getProperty(u"os.version")))

        textArray.append(u"Home Directory: " + get_home_dir())

        if System.getProperty(u"user.dir"): textArray.append(u"  user.dir: %s" %System.getProperty(u"user.dir"))
        if System.getProperty(u"UserHome"): textArray.append(u"  UserHome: %s" %System.getProperty(u"UserHome"))
        if os.path.expanduser(u"~"): textArray.append(u"  ~: %s" %os.path.expanduser(u"~"))
        if os.environ.get(u"HOMEPATH"): textArray.append(u"  HOMEPATH: %s" %os.environ.get(u"HOMEPATH"))

        textArray.append(u"Moneydance decimal point: %s" %moneydance_ui.getPreferences().getSetting(u"decimal_character", u"."))
        textArray.append(u"System Locale Decimal Point: %s" %(getDecimalPoint(lGetPoint=True)) + u" Grouping Char: %s" %(getDecimalPoint(lGetGrouping=True)))
        if moneydance_ui.getPreferences().getSetting(u"decimal_character", u".") != getDecimalPoint(lGetPoint=True):
            textArray.append(u"NOTE - MD Decimal point is DIFFERENT to the Locale decimal point!!!")
        textArray.append(u"Locale Country: %s" %(moneydance_ui.getPreferences().getSetting(u"locale.country", u"")))
        textArray.append(u"Locale Language: %s" %(moneydance_ui.getPreferences().getSetting(u"locale.language", u"")))

        textArray.append(u"\nFOLDER / FILE LOCATIONS")

        textArray.append(u"moneydance_data Dataset internal top level (root) Directory: %s" %(moneydance_data.getRootFolder().getParent()))
        textArray.append(u"Auto Backup Folder: %s " %(FileUtils.getBackupDir(moneydance.getPreferences()).getCanonicalPath() ) )
        textArray.append(u"(Last backup location: %s)" %(moneydance_ui.getPreferences().getSetting(u"backup.last_saved", u"")))

        internalFiles = AccountBookUtil.getInternalAccountBooks()
        externalFiles = AccountBookUtil.getExternalAccountBooks()

        if internalFiles.size() + externalFiles.size() > 1:
            textArray.append(u"\nOther MD Datasets I am aware of...:")

        for wrapper in internalFiles:
            if moneydance_ui.getCurrentAccounts() is not None and moneydance_ui.getCurrentAccounts().getBook() == wrapper.getBook():
                pass
            else:
                textArray.append(u"Internal file: %s" %(wrapper.getBook().getRootFolder().getCanonicalPath()))

        for wrapper in externalFiles:
            if (moneydance_ui.getCurrentAccounts() is not None and moneydance_ui.getCurrentAccounts().getBook() == wrapper.getBook()):
                pass
            else:
                textArray.append(u"External file: %s" %(wrapper.getBook().getRootFolder().getCanonicalPath()))

        if internalFiles.size() + externalFiles.size() > 1:
            textArray.append(u"\n")

        textArray.append(u"MD System Root Directory: %s" %(Common.getRootDirectory().getCanonicalPath()))

        textArray.append(u"MD Log file: %s" %(moneydance.getLogFile().getCanonicalPath()))
        textArray.append(u"Preferences File: %s" %(Common.getPreferencesFile().getCanonicalPath()))

        if os.path.exists((Common.getArchiveDirectory().getCanonicalPath())):
            textArray.append(u"Archive Directory: %s" %(Common.getArchiveDirectory().getCanonicalPath()))
        if os.path.exists((Common.getFeatureModulesDirectory().getCanonicalPath())):
            textArray.append(u"Extensions Directory: %s" %(Common.getFeatureModulesDirectory().getCanonicalPath()))
        if os.path.exists((Common.getCertificateDirectory().getCanonicalPath())):
            textArray.append(u"Certificates Directory: %s" %(Common.getCertificateDirectory().getCanonicalPath()))
        if os.path.exists((Common.getDocumentsDirectory().getCanonicalPath())):
            textArray.append(u"Documents Directory: %s" %(Common.getDocumentsDirectory().getCanonicalPath()))

        if getTheSetting(u"gen.report_dir"):
            textArray.append(getTheSetting(u"gen.report_dir"))
        if getTheSetting(u"gen.data_dir"):
            textArray.append(getTheSetting(u"gen.data_dir"))
        if getTheSetting(u"gen.import_dir"):
            textArray.append(getTheSetting(u"gen.import_dir"))

        textArray.append(u"\n")
        if os.path.exists((Common.getPythonDirectory().getCanonicalPath())):
            textArray.append(u"Python Directory: %s" %(Common.getPythonDirectory().getCanonicalPath()))
        if getTheSetting(u"gen.last_ext_file_dir"):
            textArray.append(getTheSetting(u"gen.last_ext_file_dir"))
        if getTheSetting(u"gen.python_default_file"):
            textArray.append(getTheSetting(u"gen.python_default_file"))
        if getTheSetting(u"gen.python_dir"):
            textArray.append(getTheSetting(u"gen.python_dir"))
        if getTheSetting(u"gen.graph_dir"):
            textArray.append(getTheSetting(u"gen.graph_dir"))
        if getTheSetting(u"gen.recent_files"):
            textArray.append(getTheSetting(u"gen.recent_files"))

        textArray.append(u"System 'python.path': %s" %System.getProperty(u"python.path"))
        textArray.append(u"System 'python.cachedir': %s" %System.getProperty(u"python.cachedir"))
        textArray.append(u"System 'python.cachedir.skip': %s" %System.getProperty(u"python.cachedir.skip"))

        try:
            textArray.append(u"\nEXTENSIONS / EDITORS / VIEWS")

            textArray.append(u"Extensions enabled: %s" %moneydance_ui.getMain().getSourceInformation().getExtensionsEnabled())

            x = moneydance.getExternalAccountEditors()
            for y in x:
                textArray.append(u"External Account Editor: %s" %(y))
            x = moneydance.getExternalViews()
            for y in x:
                textArray.append(u"External View(er): %s" %(y))
            x = moneydance.getLoadedModules()
            for y in x:
                textArray.append(u"Extension Loaded: %s" %(y.getDisplayName()))
            x = moneydance.getSuppressedExtensionIDs()
            for y in x:
                textArray.append(u"Internal/suppressed/secret extensions: %s" %(y))
            x = moneydance.getOutdatedExtensionIDs()
            for y in x:
                textArray.append(u"Outdated extensions (not loaded): %s" %(y))

            try:
                theUpdateList = get_extension_update_info()

                for key in theUpdateList.keys():
                    updateInfo = theUpdateList[key]
                    textArray.append(u"** UPDATABLE EXTENSION: %s to version: %s" %(pad(key,20),(updateInfo[0].getBuild())) )
            except:
                textArray.append(u"ERROR: Failed to retrieve / download Extension update list....")
                dump_sys_error_to_md_console_and_errorlog()

        except:
            pass

        orphan_prefs, orphan_files, orphan_confirmed_extn_keys = get_orphaned_extension()

        if len(orphan_prefs)<1 and len(orphan_files)<1 and len(orphan_confirmed_extn_keys)<1:
            textArray.append(u"\nCONGRATULATIONS - NO ORPHAN EXTENSIONS DETECTED!!\n")
        else:
            textArray.append(u"\nWARNING: Orphan Extensions detected (%s in config.dict) & (%s in .MXT files)\n" %(len(orphan_prefs)+len(orphan_confirmed_extn_keys),len(orphan_files)))
            myPrint(u"B", u"WARNING: Orphan Extensions detected (%s in config.dict) & (%s in .MXT files)\n" %(len(orphan_prefs)+len(orphan_confirmed_extn_keys),len(orphan_files)))


        textArray.append(count_database_objects())

        textArray.append(u"\n ======================================================================================")
        textArray.append(u"USER PREFERENCES")
        textArray.append(u"-----------------")
        textArray.append(u">> GENERAL")
        textArray.append(u"Show Full Account Paths: %s" %(moneydance_ui.getPreferences().getBoolSetting(u"show_full_account_path", True)))
        textArray.append(u"Register Follows Recorded Txns: %s" %(moneydance_ui.getPreferences().getBoolSetting(u"gui.register_follows_txns", True)))
        textArray.append(u"Use VAT/GST: %s" %(moneydance_ui.getPreferences().getBoolSetting(u"gen.use_vat", False)))
        textArray.append(u"Case Sensitive Auto-Complete: %s" %(moneydance_ui.getPreferences().getBoolSetting(u"gen.case_sensitive_ac", False)))
        textArray.append(u"Auto Insert Decimal Points: %s" %(moneydance_ui.getPreferences().getBoolSetting(u"gui.quickdecimal", False)))
        textArray.append(u"Auto Create New Transactions: %s" %(moneydance_ui.getPreferences().getBoolSetting(u"gui.new_txn_on_record", True)))
        textArray.append(u"Separate Tax Date for Transactions: %s" %(moneydance_ui.getPreferences().getBoolSetting(u"gen.separate_tax_date", False)))
        textArray.append(u"Show All Accounts in Popup: %s" %(moneydance_ui.getPreferences().getBoolSetting(u"gui.show_all_accts_in_popup", False)))
        textArray.append(u"Beep when Transactions Change: %s" %(moneydance_ui.getPreferences().getBoolSetting(u"beep_on_transaction_change", True)))
        if float(moneydance.getBuild()) < 3032:
            textArray.append(u"Theme: %s" %(moneydance_ui.getPreferences().getSetting(u"gui.current_theme", Theme.DEFAULT_THEME_ID)))
        textArray.append(u"Show Selection Details: %s" %(moneydance_ui.getPreferences().getSetting(u"details_view_mode", u"inwindow")))
        textArray.append(u"Side Bar Balance Type: %s" %(moneydance_ui.getPreferences().getSideBarBalanceType()))
        textArray.append(u"Date Format: %5s" %(moneydance_ui.getPreferences().getSetting(u"date_format", None)))
        # this.prefs.getShortDateFormat());
        textArray.append(u"Decimal Character: %s" %(moneydance_ui.getPreferences().getSetting(u"decimal_character", ".")))
        # this.prefs.getDecimalChar()));
        textArray.append(u"Locale: %s" %(moneydance_ui.getPreferences().getLocale()))

        i = moneydance_ui.getPreferences().getIntSetting(u"gen.fiscal_year_start_mmdd", 101)
        if i == 101: i = u"January 1"
        elif i == 201: i = u"February 1"
        elif i == 301: i = u"March 1"
        elif i == 401: i = u"April 1"
        elif i == 406: i = u"April 6 (UK Tax Year Start Date)"
        elif i == 501: i = u"May 1"
        elif i == 601: i = u"June 1"
        elif i == 701: i = u"July 1"
        elif i == 801: i = u"August 1"
        elif i == 901: i = u"September 1"
        elif i == 1001: i = u"October 1"
        elif i == 1101: i = u"November 1"
        elif i == 1201: i = u"December 1"
        else: i = i
        textArray.append(u"Fiscal Year Start: %s" %(i))

        if float(moneydance.getBuild()) < 3032:
            textArray.append(u"Font Size: +%s" %(moneydance_ui.getPreferences().getIntSetting(u"gui.font_increment", 0)))

        if float(moneydance.getBuild()) >= 3032:
            textArray.append(u"\n>> APPEARANCE")
            textArray.append(u"Theme: %s" %(moneydance_ui.getPreferences().getSetting(u"gui.current_theme", Theme.DEFAULT_THEME_ID)))
            if (moneydance_ui.getPreferences().getSetting(u"main_font")) != u"null":
                textArray.append(u"Font: %s" %(moneydance_ui.getPreferences().getSetting(u"main_font")))
            else:
                textArray.append(u"Font: (None/Default)")

            if (moneydance_ui.getPreferences().getSetting(u"mono_font")) != u"null":
                textArray.append(u"Numeric Font: %s" %(moneydance_ui.getPreferences().getSetting(u"mono_font")))
            else:
                textArray.append(u"Numeric Font: (None/Default)")

            if (moneydance_ui.getPreferences().getSetting(u"code_font")) != u"null":
                textArray.append(u"Moneybot Coding (monospaced) Font: %s" %(moneydance_ui.getPreferences().getSetting(u"code_font")))
            else:
                textArray.append(u"Numeric Font: (None/Default)")

            if (moneydance_ui.getPreferences().getSetting(u"print.font_name")) != u"null":
                textArray.append(u"Printing Font: %s" %(moneydance_ui.getPreferences().getSetting(u"print.font_name")))
            else:
                textArray.append(u"Printing Font: (None/Default)")

            textArray.append(u"Font Size: %s" %(moneydance_ui.getPreferences().getSetting(u"print.font_size", u"12")))
            textArray.append(u"Font Size: +%s" %(moneydance_ui.getPreferences().getIntSetting(u"gui.font_increment", 0)))

        textArray.append(u"\n>> NETWORK")
        textArray.append(u"Automatically Download in Background: %s" %(moneydance_ui.getPreferences().getBoolSetting(u"net.auto_download", False)))
        textArray.append(u"Automatically Merge Downloaded Transactions: %s" %(moneydance_ui.getPreferences().getBoolSetting(u"gen.preprocess_dwnlds", False)))
        textArray.append(u"Mark Transactions as Cleared When Confirmed: %s" %(moneydance_ui.getPreferences().getBoolSetting(u"net.clear_confirmed_txns", False)))
        textArray.append(u"Use Bank Dates for Merged Transactions: %s" %(moneydance_ui.getPreferences().getBoolSetting(u"olb.prefer_bank_dates", False)))
        textArray.append(u"Ignore Transaction Types in Favor of Amount Signs: %s" %(moneydance_ui.getPreferences().getBoolSetting(u"prefer_amt_sign_to_txn_type", False)))

        dataStorage = moneydance_data.getLocalStorage()
        autocommit = not dataStorage or dataStorage.getBoolean(u"do_autocommits",moneydance_ui.getCurrentAccounts().isMasterSyncNode())
        textArray.append(u"Auto-Commit Reminders (applies to current file on this computer): %s" %(autocommit))

        textArray.append(u"Use Proxy: %s" %(moneydance_ui.getPreferences().getBoolSetting(u"net.use_proxy", False)))
        textArray.append(u" Proxy Host: %s" %(moneydance_ui.getPreferences().getSetting(u"net.proxy_host", "")))
        textArray.append(u" Proxy Port: %s" %(moneydance_ui.getPreferences().getIntSetting(u"net.proxy_port", 80)))
        textArray.append(u"Proxy Requires Authentication: %s" %(moneydance_ui.getPreferences().getBoolSetting(u"net.auth_proxy", False)))
        textArray.append(u" Proxy Username: %s" %(moneydance_ui.getPreferences().getSetting(u"net.proxy_user", "")))
        textArray.append(u" Proxy Password: %s" %(moneydance_ui.getPreferences().getSetting(u"net.proxy_pass", "")))
        textArray.append(u"Observe Online Payment Date Restrictions: %s" %(moneydance_ui.getPreferences().getBoolSetting(u"ofx.observe_bp_window", True)))
        i = moneydance_ui.getPreferences().getIntSetting(u"net.downloaded_txn_date_window", -1)
        if i < 0: i = u"Default"
        textArray.append(u"Only Match downloaded transactions when they are at most %s days apart" %(i))

        textArray.append(u"\n>> CHEQUE PRINTING")
        textArray.append(u"preferences not listed here...")

        if float(moneydance.getBuild()) < 3032:
            textArray.append(u"\n>> PRINTING")
            textArray.append(u"Font: %s" %(moneydance_ui.getPreferences().getSetting(u"print.font_name", u"")))
            textArray.append(u"Font Size: %s" %(moneydance_ui.getPreferences().getSetting(u"print.font_size", u"12")))

        textArray.append(u"\n>> BACKUPS")

        destroyBackupChoices = moneydance_ui.getPreferences().getSetting(u"backup.destroy_number", u"5")
        returnedBackupType = moneydance_ui.getPreferences().getSetting(u"backup.backup_type", u"every_x_days")
        if returnedBackupType == u"every_time":
            dailyBackupCheckbox = True
            destroyBackupChoices = 1
        elif returnedBackupType == u"every_x_days":
            dailyBackupCheckbox = True
        else:
            dailyBackupCheckbox = False

        textArray.append(u"Save Backups Daily: %s" %(dailyBackupCheckbox))
        textArray.append(u"Keep no more than %s" %(destroyBackupChoices) + u" backups")

        textArray.append(u"separate Backup Folder: %s" %(moneydance_ui.getPreferences().getBoolSetting(u"backup.location_selected", True)))
        textArray.append(u"Backup Folder: %s " %(FileUtils.getBackupDir(moneydance.getPreferences()).getCanonicalPath() ))

        textArray.append(u"\n>> SUMMARY PAGE")
        textArray.append(u"preferences not listed here...")
        textArray.append(u" ======================================================================================\n")

        textArray.append(u"\nHOME SCREEN USER SELECTED PREFERENCES")
        textArray.append(u"----------------------------")
        textArray.append(u"Home Screen Configured: %s" %moneydance_ui.getPreferences().getSetting(u"gui.home.configured", u"NOT SET"))

        if moneydance_ui.getPreferences().getSetting(u"sidebar_bal_type", False):
            textArray.append(u"Side Bar Balance Type: %s" %(BalanceType.fromInt(moneydance_ui.getPreferences().getIntSetting(u"sidebar_bal_type",0))))
        textArray.append(u"Dashboard Item Selected: %s" %moneydance_ui.getPreferences().getSetting(u"gui.dashboard.item", u"NOT SET"))
        textArray.append(u"Quick Graph Selected: %s" %moneydance_ui.getPreferences().getSetting(u"gui.quick_graph_type", u"NOT SET"))
        textArray.append(u"Budget Bar Date Range Selected: %s" %moneydance_ui.getPreferences().getSetting(u"budgetbars_date_range", u"NOT SET"))
        textArray.append(u"Reminders View: %s" %moneydance_ui.getPreferences().getSetting(u"upcoming_setting", u"NOT SET"))

        textArray.append(u"Exchange Rates View - Invert?: %s" %moneydance_ui.getPreferences().getSetting(u"gui.home.invert_rates", u"NOT SET"))

        textArray.append(u"BANK Accounts Expanded: %s" %moneydance_ui.getPreferences().getSetting(u"gui.home.bank_expanded", u"NOT SET"))
        if moneydance_ui.getPreferences().getSetting(u"gui.home.bank_bal_type", False):
            textArray.append(u">Balance Displayed: %s" %(BalanceType.fromInt(moneydance_ui.getPreferences().getIntSetting(u"gui.home.bank_bal_type",0))))

        textArray.append(u"LOAN Accounts Expanded: %s" %moneydance_ui.getPreferences().getSetting(u"gui.home.loan_expanded", u"NOT SET"))
        if moneydance_ui.getPreferences().getSetting(u"gui.home.loan_bal_type", False):
            textArray.append(u">Balance Displayed: %s" %(BalanceType.fromInt(moneydance_ui.getPreferences().getIntSetting(u"gui.home.loan_bal_type",0))))

        textArray.append(u"LIABILITY Accounts Expanded: %s" %moneydance_ui.getPreferences().getSetting(u"gui.home.liability_expanded", u"NOT SET"))
        if moneydance_ui.getPreferences().getSetting(u"gui.home.liability_bal_type", False):
            textArray.append(u">Balance Displayed: %s" %(BalanceType.fromInt(moneydance_ui.getPreferences().getIntSetting(u"gui.home.liability_bal_type",0))))

        textArray.append(u"INVESTMENT Accounts Expanded: %s" %moneydance_ui.getPreferences().getSetting(u"gui.home.invst_expanded", u"NOT SET"))
        if moneydance_ui.getPreferences().getSetting(u"gui.home.invst_bal_type", False):
            textArray.append(u">Balance Displayed: %s" %(BalanceType.fromInt(moneydance_ui.getPreferences().getIntSetting(u"gui.home.invst_bal_type",0))))

        textArray.append(u"CREDIT CARD Accounts Expanded: %s" %moneydance_ui.getPreferences().getSetting(u"gui.home.cc_expanded", u"NOT SET"))
        if moneydance_ui.getPreferences().getSetting(u"gui.home.cc_bal_type", False):
            textArray.append(u">Balance Displayed: %s" %(BalanceType.fromInt(moneydance_ui.getPreferences().getIntSetting(u"gui.home.cc_bal_type",0))))

        textArray.append(u"ASSET Accounts Expanded: %s" %moneydance_ui.getPreferences().getSetting(u"gui.home.asset_expanded", u"NOT SET"))
        if moneydance_ui.getPreferences().getSetting(u"gui.home.asset_bal_type", False):
            textArray.append(u">Balance Displayed: %s" %(BalanceType.fromInt(moneydance_ui.getPreferences().getIntSetting(u"gui.home.asset_bal_type",0))))


        textArray.append(u" ======================================================================================\n")

        try:
            textArray.append(u"\nFONTS")
            textArray.append(u">> Swing Manager default: %s" %(UIManager.getFont("Label.font")))
            textArray.append(u">> Moneydance default: %s" %(moneydance_ui.getFonts().defaultSystemFont))
            textArray.append(u">> Moneydance mono: %s" %(moneydance_ui.getFonts().mono))
            textArray.append(u">> Moneydance default text: %s" %(moneydance_ui.getFonts().defaultText))
            textArray.append(u">> Moneydance default title: %s" %(moneydance_ui.getFonts().detailTitle))
            textArray.append(u">> Moneydance calendar title: %s" %(moneydance_ui.getFonts().calendarTitle))
            textArray.append(u">> Moneydance header: %s" %(moneydance_ui.getFonts().header))
            textArray.append(u">> Moneydance register: %s" %(moneydance_ui.getFonts().register))
            textArray.append(u">> Moneydance report header: %s" %(moneydance_ui.getFonts().reportHeader))
            textArray.append(u">> Moneydance report title: %s" %(moneydance_ui.getFonts().reportTitle))

            try:
                textArray.append(u">> Moneydance code: %s" %(moneydance_ui.getFonts().code))
            except:
                pass

        except:
            myPrint(u"B",u"Error getting fonts..?")
            dump_sys_error_to_md_console_and_errorlog()

        textArray.append(u"\n>> OTHER INTERESTING SETTINGS....")

        if getTheSetting(u"net.default_browser"):
            textArray.append(getTheSetting(u"net.default_browser"))
        if getTheSetting(u"gen.import_dt_fmt_idx"):
            textArray.append(getTheSetting(u"gen.import_dt_fmt_idx"))
        if getTheSetting(u"txtimport_datefmt"):
            textArray.append(getTheSetting(u"txtimport_datefmt"))
        if getTheSetting(u"txtimport_csv_delim"):
            textArray.append(getTheSetting(u"txtimport_csv_delim"))
        if getTheSetting(u"txtimport_csv_decpoint"):
            textArray.append(getTheSetting(u"txtimport_csv_decpoint"))

        textArray.append(u"")

        if getTheSetting(u"ofx.app_id"):
            textArray.append(getTheSetting(u"ofx.app_id"))
        if getTheSetting(u"ofx.app_version"):
            textArray.append(getTheSetting(u"ofx.app_version"))
        if getTheSetting(u"ofx.bp_country"):
            textArray.append(getTheSetting(u"ofx.bp_country"))
        if getTheSetting(u"ofx.app_version"):
            textArray.append(getTheSetting(u"ofx.app_version"))

        textArray.append(u"")
        textArray.append(u"System Properties containing references to Moneydance")
        for x in System.getProperties():

            # noinspection PyUnresolvedReferences
            if u"moneydance" in System.getProperty(x).lower():
                textArray.append(u">> %s:\t%s" %(x, System.getProperty(x)))

        textArray.append(u"\n\n<END>\n")

        # This catches exceptions.UnicodeDecodeError 'utf-8' codec can't decode byte 0xa0 in position 46: unexpected code byte'
        # First spotted with South African Locale and nbsp used for decimal grouping character....

        try:
            returnString = u"\n".join(textArray)
            myPrint(u"DB",u"Success joining diagnostics text array.....")
        except:
            myPrint(u"B",u"UH-OH - Seems like we probably caught an utf8 error... trying to rectify")
            myPrint(u"B", dump_sys_error_to_md_console_and_errorlog(True))
            returnString = u""
            for i in range(0, len(textArray)):
                for char in textArray[i]:
                    if ord(char)>=128:
                        myPrint(u"B",u"char ord(%s) found in row %s; position %s" %(ord(char),i,textArray[i].find(char)))
                        myPrint(u"B",u"@@ FAILING ROW STARTS: '%s'" %(textArray[i][:textArray[i].find(char)]))
                        break
                returnString += (u"".join(char for char in textArray[i] if ord(char) < 128) )+u"\n"
            returnString += u"\n(** NOTE: I had to strip non ASCII characters **)\n"

        return returnString

    def get_list_memorised_reports():
        # Build a quick virtual file of Memorized reports and graphs to display
        memz = []

        iCount = 0
        for x in moneydance_data.getMemorizedItems().getMemorizedGraphs():
            iCount+=1
            memz.append("Graph: %s" % (x.getName()))

        for x in moneydance_data.getMemorizedItems().getMemorizedReports():
            iCount+=1
            memz.append("Report: %s" % (x.getName()))

        memz = sorted(memz, key=lambda sort_x: ((sort_x[0]).upper()))

        memz.insert(0,"YOUR MEMORIZED REPORTS\n ======================\n")

        memz.append("\nYOUR MEMORIZED REPORTS in detail\n ======================\n")

        iGs = 0
        for x in moneydance_data.getMemorizedItems().getMemorizedGraphs():
            if iGs:
                memz.append("\n ---")
            iGs+=1
            memz.append("Graph:           %s" % (x.getName()))
            memz.append(">> SyncItemType: %s" %(x.getSyncItemType()))
            # memz.append(">> Graph ID:     %s" %(x.getReportID()))
            memz.append(">> Graph Genr:   %s" %(x.getReportGenerator()))
            y = x.getReportParameters()
            for yy in y:
                if yy.lower().strip() == "accounts" or yy.lower().strip() == "source_accts":
                    memz.append(">> Parameter key: %s: %s" %(yy, "<not displayed - but contains %s accounts>" %(y.get(yy).count(",")+1)))
                else:
                    memz.append(">> Parameter key: %s: %s" %(yy, y.get(yy)))

        iRs = 0
        for x in moneydance_data.getMemorizedItems().getMemorizedReports():
            if iRs or iGs:
                memz.append("\n ---")
            iRs+=1
            memz.append("Report           %s" % (x.getName()))
            memz.append(">> SyncItemType: %s" %(x.getSyncItemType()))
            # memz.append(">> Report ID:    %s" %(x.getReportID()))
            memz.append(">> Report Genr:  %s" %(x.getReportGenerator()))
            y = x.getReportParameters()
            for yy in y:
                if yy.lower().strip() == "accounts" or yy.lower().strip() == "source_accts":
                    memz.append(">> Parameter key: %s: %s" %(yy, "<not displayed - but contains %s accounts>" %(y.get(yy).count(",")+1)))
                else:
                    memz.append(">> Parameter key: %s: %s" %(yy, y.get(yy)))

        memz.append("\n\n\n====== DEFAULT REPORTS SETTINGS/PARAMETERS (from Local Storage) RAW DUMP ======\n")
        LS = moneydance_ui.getCurrentAccounts().getBook().getLocalStorage()

        last = None
        keys=sorted(LS.keys())
        for theKey in keys:
            value = LS.get(theKey)
            if not theKey.lower().startswith("report_params."): continue
            split_key = theKey.split(".",2)
            if split_key[1] != last:
                memz.append("")
                last = split_key[1]

            if theKey.lower().strip().endswith(".accounts") or theKey.lower().strip().endswith(".source_accts"):
                memz.append("Key:%s Value: %s" % (pad(theKey,70), "<not displayed - but contains %s accounts>" %(value.count(",")+1)))
            else:
                memz.append("Key:%s Value: %s" % (pad(theKey,70), value.strip()))

        x=LS.get("grfRepDefaultParams")
        if x:
            memz.append("\n\nDefault Parameters: 'grfRepDefaultParams' (Probably Legacy keys)")
            memz.append("%s" %x)
            memz.append("")

        memz.append("\n<END>")

        for i in range(0, len(memz)):
            memz[i] = memz[i] + "\n"
        memz = "".join(memz)
        return memz

    def view_extensions_details():
        theData = []                                                                                                    # noqa

        theData.append("EXTENSION(s) DETAILS")
        theData.append(" =====================\n")

        theData.append("Extensions enabled: %s\n" %moneydance_ui.getMain().getSourceInformation().getExtensionsEnabled())

        theUpdateList = get_extension_update_info()

        # noinspection PyBroadException
        try:
            x = moneydance.getLoadedModules()
            for y in x:
                isUpdatable= "(latest version)"
                updateInfo = theUpdateList.get(y.getIDStr().lower())
                if updateInfo:
                    isUpdatable+= "\t******* Updatable to version: %s *******" % (updateInfo[0].getBuild()).upper()
                theData.append("Extension ID:           %s" %y.getIDStr())
                theData.append("Extension Name:         %s" %y.getName())
                theData.append("Extension Display Name: %s" %y.getDisplayName())
                theData.append("Extension Description:  %s" %y.getDescription())
                theData.append("Extension Version:      %s" %(y.getBuild()) + isUpdatable)
                theData.append("Extension Source File:  %s" %(y.getSourceFile()))
                theData.append("Extension Vendor:       %s" %y.getVendor())
                theData.append("Extension isBundled:    %s" %(y.isBundled()))
                theData.append("Extension isVerified:   %s" %(y.isVerified()))
                if moneydance_ui.getPreferences().getSetting("confirmedext."+str(y.getName()).strip(), None):
                    theData.append("** User has Confirmed this unsigned Extension can run - version: " + moneydance_ui.getPreferences().getSetting("confirmedext."+str(y.getName()).strip(), None))
                theData.append("\n\n")

            x = moneydance.getSuppressedExtensionIDs()
            for y in x:
                theData.append("Internal/suppressed/secret extensions: %s" %(y))

            x = moneydance.getOutdatedExtensionIDs()
            for y in x:
                theData.append("Outdated extensions (not loaded): %s" %(y))
        except:
            theData.append("\nERROR READING EXTENSION DATA!!!!\n")
            dump_sys_error_to_md_console_and_errorlog()

        orphan_prefs, orphan_files, orphan_confirmed_extn_keys = get_orphaned_extension()

        if len(orphan_prefs)<1 and len(orphan_files)<1 and len(orphan_confirmed_extn_keys)<1:
            theData.append("\nCONGRATULATIONS - NO ORPHAN EXTENSIONS DETECTED!!\n")

        else:
            theData.append("\nLISTING EXTENSIONS ORPHANED IN CONFIG.DICT OR FILES (*.MXT)\n")

            for x in orphan_prefs.keys():
                theData.append("%s Extension: %s is %s" %(pad("config.dict:",40),pad(x,40),pad(orphan_prefs[x],40)))

            theData.append("")

            for x in orphan_confirmed_extn_keys.keys():
                _theVersion = moneydance_ui.getPreferences().getSetting(orphan_confirmed_extn_keys[x][1],None)
                theData.append("%s Extension: %s Key: %s (build: %s) is %s" %(pad("config.dict:",40),pad(x,40),pad(orphan_confirmed_extn_keys[x][1],40),_theVersion, pad(orphan_confirmed_extn_keys[x][0],40)))

            theData.append("")

            for x in orphan_files.keys():
                theData.append("%s Extension: %s is %s" %(pad("File: "+orphan_files[x][1],40),pad(x,40),pad(orphan_files[x][0],40)))

        theData.append("\n<END>")

        # Build a quick virtual 'file' of Memorized reports and graphs to display
        for i in range(0, len(theData)):
            theData[i] = theData[i] + "\n"
        theData = "".join(theData)
        return theData


    class ToolboxBuildInfo:

        def __init__(self, buildObject):
            self.obj =                                  buildObject
            self.build =                                buildObject.getInt("build", 0)
            self.disable =                              buildObject.getBoolean("disable", False)
            self.OFX_SETUP_MATCH_MD_BUILD =             buildObject.getInt("OFX_SETUP_MATCH_MD_BUILD", 0)
            self.TOOLBOX_MINIMUM_TESTED_MD_VERSION =    float(buildObject.getStr("TOOLBOX_MINIMUM_TESTED_MD_VERSION", "0.0"))
            self.TOOLBOX_MAXIMUM_TESTED_MD_VERSION =    float(buildObject.getStr("TOOLBOX_MAXIMUM_TESTED_MD_VERSION", "0.0"))
            self.TOOLBOX_MAXIMUM_TESTED_MD_BUILD =      buildObject.getInt("TOOLBOX_MAXIMUM_TESTED_MD_BUILD", 0)
            self.MD_OFX_BANK_SETTINGS_DIR =             buildObject.getStr("MD_OFX_BANK_SETTINGS_DIR", "")
            self.MD_OFX_DEFAULT_SETTINGS_FILE =         buildObject.getStr("MD_OFX_DEFAULT_SETTINGS_FILE", "")
            self.MD_OFX_DEBUG_SETTINGS_FILE =           buildObject.getStr("MD_OFX_DEBUG_SETTINGS_FILE", "")
            self.MD_EXTENSIONS_DIRECTORY_FILE =         buildObject.getStr("MD_EXTENSIONS_DIRECTORY_FILE", "")
            self.MYPYTHON_DOWNLOAD_URL =                buildObject.getStr("MYPYTHON_DOWNLOAD_URL", "")

            # noinspection PyChainedComparsons
            if self.build > 1000 and self.build < 9999 and self.disable: return                                             # noqa

            # noinspection PyChainedComparsons
            if (self.build < 1000 or self.build > 9999
                    or (self.OFX_SETUP_MATCH_MD_BUILD > 0           and self.OFX_SETUP_MATCH_MD_BUILD)         < 3034       # noqa
                    or (self.TOOLBOX_MINIMUM_TESTED_MD_VERSION > 0  and self.TOOLBOX_MINIMUM_TESTED_MD_VERSION < 2020.0)    # noqa
                    or (self.TOOLBOX_MAXIMUM_TESTED_MD_VERSION > 0  and self.TOOLBOX_MAXIMUM_TESTED_MD_VERSION < 2021.1)    # noqa
                    or (self.TOOLBOX_MAXIMUM_TESTED_MD_BUILD > 0    and self.TOOLBOX_MAXIMUM_TESTED_MD_BUILD   < 3034)      # noqa
                    or (len(self.MD_OFX_BANK_SETTINGS_DIR) > 0      and len(self.MD_OFX_BANK_SETTINGS_DIR)     < 10)        # noqa
                    or (len(self.MD_OFX_DEFAULT_SETTINGS_FILE) > 0  and len(self.MD_OFX_DEFAULT_SETTINGS_FILE) < 10)        # noqa
                    or (len(self.MD_OFX_DEBUG_SETTINGS_FILE) > 0    and len(self.MD_OFX_DEBUG_SETTINGS_FILE)   < 10)        # noqa
                    or (len(self.MD_EXTENSIONS_DIRECTORY_FILE) > 0  and len(self.MD_EXTENSIONS_DIRECTORY_FILE) < 10)        # noqa
                    or (len(self.MYPYTHON_DOWNLOAD_URL) > 0         and len(self.MYPYTHON_DOWNLOAD_URL) < 10)):      # noqa

                myPrint("DB","Error with toolbox downloaded data - invalidating it - was: %s" %(self.obj))
                self.build =                                0
                self.disable =                              False
                self.OFX_SETUP_MATCH_MD_BUILD =             None
                self.TOOLBOX_MINIMUM_TESTED_MD_VERSION =    None
                self.TOOLBOX_MAXIMUM_TESTED_MD_VERSION =    None
                self.TOOLBOX_MAXIMUM_TESTED_MD_BUILD =      None
                self.MD_OFX_BANK_SETTINGS_DIR =             None
                self.MD_OFX_DEFAULT_SETTINGS_FILE =         None
                self.MD_OFX_DEBUG_SETTINGS_FILE =           None
                self.MD_EXTENSIONS_DIRECTORY_FILE =         None
                self.MYPYTHON_DOWNLOAD_URL =                 None


        def __str__(self):
            return "Toolbox build info Obj. Build: %s Disabled: %s {%s}" %(self.build,self.disable, self.obj)

        def __repr__(self):
            return "Toolbox build info Obj. Build: %s Disabled: %s {%s}" %(self.build,self.disable, self.obj)

    def download_toolbox_version_info():
        global debug, TOOLBOX_STOP_NOW, TOOLBOX_VERSION_VALIDATION_URL, version_build
        global OFX_SETUP_MATCH_MD_BUILD, TOOLBOX_MINIMUM_TESTED_MD_VERSION, TOOLBOX_MAXIMUM_TESTED_MD_VERSION, TOOLBOX_MAXIMUM_TESTED_MD_BUILD
        global MD_OFX_BANK_SETTINGS_DIR, MD_OFX_DEFAULT_SETTINGS_FILE, MD_OFX_DEBUG_SETTINGS_FILE, MD_EXTENSIONS_DIRECTORY_FILE, MYPYTHON_DOWNLOAD_URL

        myPrint("J","Checking online for updated Toolbox version / build information.....")

        this_toolbox_build = int(version_build)
        if this_toolbox_build < 1000:
            myPrint("B", "ERROR with Toolbox build %s  - will just proceed without safeguards" %(this_toolbox_build))
            return

        downloadBuilds = StreamTable()

        myPrint("DB","Checking online for Toolbox version/build information....")

        inx = None
        try:
            url = URL(TOOLBOX_VERSION_VALIDATION_URL)
            inx = BufferedReader(InputStreamReader(url.openStream(), "UTF8"))
            downloadBuilds.readFrom(inx)
            myPrint("DB","Success getting online version/build info for Toolbox....")
        except:
            myPrint("J","")
            myPrint("B", "ERROR downloading version/build info from Toolbox website...: %s" %(TOOLBOX_VERSION_VALIDATION_URL))
        finally:
            if inx:
                try:
                    inx.close()
                except:
                    myPrint("B", "Error closing Toolbox Version/build info URL stream: %s" %(TOOLBOX_VERSION_VALIDATION_URL))

        if not downloadBuilds or downloadBuilds is None:
            myPrint("B", "Error: Toolbox version/build info after download is Empty - will just proceed without safeguards")
            return

        lastUpdated = downloadBuilds.getStr("last_updated", "UNKNOWN")
        myPrint("DB","Last Updated: %s" %(lastUpdated))

        TOOLBOX_STOP_NOW = downloadBuilds.getBoolean("disable_all", False)
        if TOOLBOX_STOP_NOW:
            myPrint("B","Uh-oh... disable_all has been set by the Developer.... Toolbox must close... Sorry")
            return
        else:
            myPrint("DB","Phew! disable_all NOT set....")

        buildList = downloadBuilds.get("builds", None)                   # type: StreamVector
        if not buildList or buildList is None:
            myPrint("B","Error - failed to download or decode build list - - will just proceed without safeguards")
            return

        buildTable=[]

        try:
            for buildObj in buildList:                                      # type: StreamTable
                if not (isinstance(buildObj, StreamTable)):
                    myPrint("DB", "ERROR - Retrieved toolbox build info is not a StreamTable(). It's %s %s" %(type(buildObj),buildObj))
                    continue

                # myPrint("D", "BuildObj contains: %s" %(buildObj))
                buildTable.append(ToolboxBuildInfo(buildObj))

        except:
            dump_sys_error_to_md_console_and_errorlog()
            myPrint("B", "ERROR decoding downloading toolbox version/build data!  - will just proceed without safeguards...")
            return

        if len(buildTable)<1:
            myPrint("B", "ERROR decoded downloaded toolbox version/build data is empty!  - will just proceed without safeguards...")
            return

        buildTable = sorted(buildTable, key=lambda _x: (_x.build), reverse=True)          # type: [ToolboxBuildInfo]
        # Already sorted - newest build first
        for moduleBuild in buildTable:          # type: ToolboxBuildInfo
            if moduleBuild.build < 1000:
                myPrint("D","Found INVALID downloaded module build %s (ignoring and stopping search)... (%s)" %(moduleBuild.build, moduleBuild.obj ))
                return
            elif moduleBuild.build > this_toolbox_build:
                myPrint("D","Found NEWER downloaded module build %s (ignoring and continuing search).. (%s)" %(moduleBuild.build, moduleBuild.obj ))
                continue
            elif moduleBuild.build == this_toolbox_build:
                myPrint("D","Found EXACT-HIT downloaded module build %s OVERRIDING PROGRAM's DEFAULTS....! (%s)" %(moduleBuild.build, moduleBuild.obj ))

                if debug:
                    myPrint("D","Program defaults were...:")
                    myPrint("D"," TOOLBOX_STOP_NOW:                     %s"     %(TOOLBOX_STOP_NOW))
                    myPrint("D"," OFX_SETUP_MATCH_MD_BUILD:             %s"     %(OFX_SETUP_MATCH_MD_BUILD))
                    myPrint("D"," TOOLBOX_MINIMUM_TESTED_MD_VERSION:    %s"     %(TOOLBOX_MINIMUM_TESTED_MD_VERSION))
                    myPrint("D"," TOOLBOX_MAXIMUM_TESTED_MD_VERSION:    %s"     %(TOOLBOX_MAXIMUM_TESTED_MD_VERSION))
                    myPrint("D"," TOOLBOX_MAXIMUM_TESTED_MD_BUILD:      %s"     %(TOOLBOX_MAXIMUM_TESTED_MD_BUILD))
                    myPrint("D"," MD_OFX_BANK_SETTINGS_DIR:             %s"     %(MD_OFX_BANK_SETTINGS_DIR))
                    myPrint("D"," MD_OFX_DEFAULT_SETTINGS_FILE:         %s"     %(MD_OFX_DEFAULT_SETTINGS_FILE))
                    myPrint("D"," MD_OFX_DEBUG_SETTINGS_FILE:           %s"     %(MD_OFX_DEBUG_SETTINGS_FILE))
                    myPrint("D"," MD_EXTENSIONS_DIRECTORY_FILE:         %s"     %(MD_EXTENSIONS_DIRECTORY_FILE))
                    myPrint("D"," MYPYTHON_DOWNLOAD_URL:                %s"     %(MYPYTHON_DOWNLOAD_URL))

                TOOLBOX_STOP_NOW =                      moduleBuild.disable
                if moduleBuild.OFX_SETUP_MATCH_MD_BUILD > 0:
                    OFX_SETUP_MATCH_MD_BUILD =              moduleBuild.OFX_SETUP_MATCH_MD_BUILD
                if moduleBuild.TOOLBOX_MINIMUM_TESTED_MD_VERSION > 0:
                    TOOLBOX_MINIMUM_TESTED_MD_VERSION =     moduleBuild.TOOLBOX_MINIMUM_TESTED_MD_VERSION
                if moduleBuild.TOOLBOX_MAXIMUM_TESTED_MD_VERSION:
                    TOOLBOX_MAXIMUM_TESTED_MD_VERSION =     moduleBuild.TOOLBOX_MAXIMUM_TESTED_MD_VERSION
                if moduleBuild.TOOLBOX_MAXIMUM_TESTED_MD_BUILD > 0:
                    TOOLBOX_MAXIMUM_TESTED_MD_BUILD =       moduleBuild.TOOLBOX_MAXIMUM_TESTED_MD_BUILD
                if len(moduleBuild.MD_OFX_BANK_SETTINGS_DIR) > 0:
                    MD_OFX_BANK_SETTINGS_DIR =              moduleBuild.MD_OFX_BANK_SETTINGS_DIR
                if len(moduleBuild.MD_OFX_DEFAULT_SETTINGS_FILE) > 0:
                    MD_OFX_DEFAULT_SETTINGS_FILE =          moduleBuild.MD_OFX_DEFAULT_SETTINGS_FILE
                if len(moduleBuild.MD_OFX_DEBUG_SETTINGS_FILE) > 0:
                    MD_OFX_DEBUG_SETTINGS_FILE =            moduleBuild.MD_OFX_DEBUG_SETTINGS_FILE
                if len(moduleBuild.MD_EXTENSIONS_DIRECTORY_FILE) > 0:
                    MD_EXTENSIONS_DIRECTORY_FILE =          moduleBuild.MD_EXTENSIONS_DIRECTORY_FILE
                if len(moduleBuild.MYPYTHON_DOWNLOAD_URL) > 0:
                    MYPYTHON_DOWNLOAD_URL =                  moduleBuild.MYPYTHON_DOWNLOAD_URL

                if debug:
                    myPrint("D","Program variables are now...:")
                    myPrint("D"," TOOLBOX_STOP_NOW:                     %s"     %(TOOLBOX_STOP_NOW))
                    myPrint("D"," OFX_SETUP_MATCH_MD_BUILD:             %s"     %(OFX_SETUP_MATCH_MD_BUILD))
                    myPrint("D"," TOOLBOX_MINIMUM_TESTED_MD_VERSION:    %s"     %(TOOLBOX_MINIMUM_TESTED_MD_VERSION))
                    myPrint("D"," TOOLBOX_MAXIMUM_TESTED_MD_VERSION:    %s"     %(TOOLBOX_MAXIMUM_TESTED_MD_VERSION))
                    myPrint("D"," TOOLBOX_MAXIMUM_TESTED_MD_BUILD:      %s"     %(TOOLBOX_MAXIMUM_TESTED_MD_BUILD))
                    myPrint("D"," MD_OFX_BANK_SETTINGS_DIR:             %s"     %(MD_OFX_BANK_SETTINGS_DIR))
                    myPrint("D"," MD_OFX_DEFAULT_SETTINGS_FILE:         %s"     %(MD_OFX_DEFAULT_SETTINGS_FILE))
                    myPrint("D"," MD_OFX_DEBUG_SETTINGS_FILE:           %s"     %(MD_OFX_DEBUG_SETTINGS_FILE))
                    myPrint("D"," MD_EXTENSIONS_DIRECTORY_FILE:         %s"     %(MD_EXTENSIONS_DIRECTORY_FILE))
                    myPrint("D"," MYPYTHON_DOWNLOAD_URL:                %s"     %(MYPYTHON_DOWNLOAD_URL))

                if TOOLBOX_STOP_NOW:
                    myPrint("B","Uh-oh... disable has been set by the Developer for this build.... Toolbox must close... Sorry")

                return

            else:
                myPrint("D","Found LOWER downloaded module build %s - so I will keep program's defaults, and ignore these - exiting search... (%s) " %(moduleBuild.build, moduleBuild.obj ))
                return

        myPrint("D","No suitable module build info found.. (so I will keep program's defaults, and ignore these - exiting search)")

        return

    def downloadExtensions():
        global MD_EXTENSIONS_DIRECTORY_FILE

        downloadInfo = StreamTable()
        if moneydance_ui.getMain().getSourceInformation().getExtensionsEnabled():
            inx = None
            try:
                url = URL(System.getProperty("moneydance.extension_list_url", MD_EXTENSIONS_DIRECTORY_FILE))
                inx = BufferedReader(InputStreamReader(url.openStream(), "UTF8"))
                downloadInfo.readFrom(inx)
            except:
                myPrint("B", "ERROR downloading from Moneydance extensions list website... ")
                dump_sys_error_to_md_console_and_errorlog()

            finally:
                if inx:
                    try:
                        inx.close()
                    except:
                        myPrint("B", "Error closing URL stream")
                        dump_sys_error_to_md_console_and_errorlog()
            return downloadInfo
        else:
            myPrint("B", "@@ Extensions not enabled!!?? @@")
        return False

    def check_if_key_string_valid(test_str):
        # http://docs.python.org/library/re.html
        # re.search returns None if no position in the string matches the pattern
        # pattern to search for any character other than "._-A-Za-z0-9"
        pattern = r'[^a-zA-Z0-9-_.:&=;,@]'
        if re.search(pattern, test_str):
            myPrint("DB","Invalid: %r" %(test_str))
            return False
        else:
            myPrint("DB","Valid: %r" %(test_str))
            return True

    def check_if_key_data_string_valid(test_str):
        # http://docs.python.org/library/re.html
        # re.search returns None if no position in the string matches the pattern
        # pattern to search for any character other than "._-A-Za-z0-9"
        pattern = r"[^a-zA-Z0-9-' _.:&=;,@]"
        if re.search(pattern, test_str):
            myPrint("DB","Invalid: %r" %(test_str))
            return False
        else:
            myPrint("DB","Valid: %r" %(test_str))
            return True

    def get_extension_update_info():
        availableExtensionInfo=downloadExtensions()
        moduleList = availableExtensionInfo.get(u"feature_modules")      # StreamVector

        installed = moneydance_ui.getMain().getLoadedModules()          # FeatureModule[]
        excludedIDs = moneydance.getSuppressedExtensionIDs()            # List<String>
        for installedMod in installed:
            if installedMod.isBundled():
                excludedIDs.add(installedMod.getIDStr().toLowerCase())

        miniUpdateList={}

        try:
            if moduleList:
                for obj in moduleList:
                    if not (isinstance(obj, StreamTable)):
                        myPrint(u"J", u"ERROR - Retrieved data is not a StreamTable()", obj)
                        continue

                    extInfo = ModuleMetaData(obj)       # ModuleMetaData

                    # noinspection PyUnresolvedReferences
                    if excludedIDs.contains(extInfo.getModuleID().lower()):     # Probably internal modules like Python/Jython
                        continue
                    if not (1928 >= extInfo.getMinimumSupportedBuild() and 1928 <= extInfo.getMaximumSupportedBuild()):  # noqa
                        continue
                    if not (extInfo.getMinimumSupportedBuild() >= 1000):
                        continue
                    if not(extInfo.isMacSandboxFriendly() or not Platform.isMac() or not moneydance_ui.getMain().getPlatformHelper().isConstrainedToSandbox()):
                        continue
                    existingMod = None          # FeatureModule
                    for mod in installed:

                        # noinspection PyUnresolvedReferences
                        if mod.getIDStr().lower() == extInfo.getModuleID().lower():
                            existingMod = mod
                            break
                    isInstalled = (existingMod is not None)     # boolean
                    isUpdatable = (existingMod is not None and existingMod.getBuild() < extInfo.getBuild())
                    if existingMod and isInstalled and isUpdatable:

                        # noinspection PyUnresolvedReferences
                        miniUpdateList[extInfo.getModuleID().lower()] = [extInfo, isInstalled, isUpdatable]

            else:
                myPrint(u"J", u"ERROR - Failed to download module list!)")
        except:
            myPrint(u"B", u"ERROR decoding downloaded module list!)")
            dump_sys_error_to_md_console_and_errorlog()

        return miniUpdateList

    def get_register_txn_sort_orders():

        # Flush in memory settings to disk
        moneydance.savePreferences()

        theSortData = []                                                                                                # noqa

        theSortData.append("VIEW REGISTER TXN SORT ORDERS (for Accounts - excluding legacy keys)")
        theSortData.append(" ==================================================================\n")

        theSortData.append("DEFAULTS (from config.dict)\n")

        for x in _COLWIDTHS:

            if      x == "bank":        theType = "Bank"
            elif    x == "cc":          theType = "Credit Card"
            elif    x == "invest":      theType = "Investment"
            elif    x == "loan":        theType = "Loan"
            elif    x == "security":    theType = "Security"
            elif    x == "misc":        theType = "Asset/Liability/Expense/Income/Other"
            elif    x == "rec_credits": theType = "Reconciling window - credits"
            elif    x == "rec_debits":  theType = "Reconciling window - debits"
            elif    x == "secdetail":   theType = "Security Detail"
            elif    x == "split":       theType = "Split Window"
            else:                       theType = "????"

            result = loadMDPreferences(None,x)
            if result:
                oneLineMode = result[0]
                splitReg    = result[1]
                splitSz     = result[2]
                sortID      = result[3]
                position    = result[4]
                ascending   = result[5]
                widths      = result[6]
                position2   = result[7]

                theSortData.append("\nType: %s (%s) Register Sort Data:"%(theType,x))
                theSortData.append(">> Sort Order: %s" %sortID)
                theSortData.append(">> Ascending: %s" %ascending)
                theSortData.append(">> One Line View: %s" %oneLineMode)
                theSortData.append(">> Split Register View: %s (%s)" %(splitReg,splitSz))
                theSortData.append(">> Position: %s Widths: %s Position2 %s\n" %(position, widths, position2))


        theSortData.append("\nDATA SAVED INTERNALLY BY (ACTIVE) ACCOUNT")
        theSortData.append("-----------------------------------------\n")

        accounts = AccountUtil.allMatchesForSearch(moneydance_data, MyAcctFilter(1))
        for acct in accounts:

            for x in _COLWIDTHS:

                if      x == "bank":        theType = "Bank"
                elif    x == "cc":          theType = "Credit Card"
                elif    x == "invest":      theType = "Investment"
                elif    x == "loan":        theType = "Loan"
                elif    x == "security":    theType = "Security"
                elif    x == "misc":        theType = "Asset/Liability/Expense/Income/Other"
                elif    x == "rec_credits": theType = "Reconciling window - credits"
                elif    x == "rec_debits":  theType = "Reconciling window - debits"
                elif    x == "secdetail":   theType = "Security Detail"
                elif    x == "split":       theType = "Split Window"
                else:                       theType = "????"

                result = loadMDPreferences(acct,x, False)

                if result:
                    oneLineMode = result[0]
                    splitReg    = result[1]
                    splitSz     = result[2]
                    sortID      = result[3]
                    position    = result[4]
                    ascending   = result[5]
                    widths      = result[6]
                    position2   = result[7]

                    theSortData.append("\nAccount: %s Account Type: %s Key Type: %s (%s) Register Sort Data:"%(acct.getAccountName(), acct.getAccountType(),theType,x))
                    theSortData.append(">> Sort Order: %s" %sortID)
                    theSortData.append(">> Ascending: %s" %ascending)
                    theSortData.append(">> One Line View: %s" %oneLineMode)
                    theSortData.append(">> Split Register View: %s (%s)" %(splitReg,splitSz))
                    theSortData.append(">> Position: %s Widths: %s Position2 %s\n" %(position, widths, position2))

        theSortData.append("\n<END>")

        for i in range(0, len(theSortData)):
            theSortData[i] = theSortData[i] + "\n"
        theSortData = "".join(theSortData)
        return theSortData

    def view_check_num_settings(statusLabel):
        try:
            from com.infinitekind.moneydance.model import CheckNumSettings
        except:
            statusLabel.setText(("Sorry - your version of MD is too early to use this function, must be at least Moneydance 2020.1 (1925)").ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            return

        theData = []                                                                                                    # noqa

        theData.append("CHECK NUMBER SETTINGS")
        theData.append(" =====================\n")

        acct = root = moneydance.getCurrentAccountBook().getRootAccount()
        x = root.getCheckNumSettings(True)  # False means don't return defaults
        theData.append("\nMaster Dataset & defaults (root account): " + moneydance.getCurrentAccountBook().getName())
        if not x:  # Assume old style check numbers
            theData.append(
                " >>Old style Check numbers as default: %s" %(moneydance_ui.getResources().getCheckNumberList(acct)))
            theData.append("\n\n")
        else:
            theData.append(" >>Fixed Chq Items: %s" %(x.getPopupStrings()))
            theData.append(
                " >>Complete list of all Items in Chq Popup: %s" %(moneydance_ui.getResources().getCheckNumberList(acct)))
            y = x.getRecentsOption()

            # noinspection PyUnresolvedReferences
            if y == CheckNumSettings.IncludeRecentsOption.ACCOUNT: y = "Include from Same Account"
            elif y == CheckNumSettings.IncludeRecentsOption.GLOBAL: y = "Include from All Accounts"
            elif y == CheckNumSettings.IncludeRecentsOption.NONE: y = "Don't Include"

            theData.append(" >>Recent Entries:          %s" %(y))
            theData.append(" >>Max Entries:             %s" %(x.getMaximumRecents()))
            theData.append(" >>Show Next-Check Number:  %s" %(x.getIncludeNextCheckNumber()))
            theData.append(" >>Show Print-Check Option: %s" %(x.getIncludePrintCheckMarker()))
            theData.append("\n")

        accounts = AccountUtil.allMatchesForSearch(moneydance_data, MyAcctFilter(3))

        for acct in accounts:

            # noinspection PyUnresolvedReferences
            if acct.getAccountType() == Account.AccountType.ROOT: continue

            x = acct.getCheckNumSettings(False)  # False means don't return defaults

            if not x:
                theData.append("Account: " + acct.getFullAccountName() + " (Settings: NONE/Default)")
                theData.append(" >>Complete list of all Items in Chq Popup: %s" %(moneydance_ui.getResources().getCheckNumberList(acct)))
                theData.append("\n")
            else:
                theData.append("Account: " + pad(acct.getFullAccountName(), 80))
                theData.append(" >>Fixed Chq Items: %s" %(x.getPopupStrings()))
                if acct.getAccountType() != Account.AccountType.ROOT:                                               # noqa
                    theData.append(" >>Complete list of all Items in Chq Popup: %s" %(moneydance_ui.getResources().getCheckNumberList(acct)))

                y = x.getRecentsOption()
                if y == CheckNumSettings.IncludeRecentsOption.ACCOUNT:                                              # noqa
                    y = "Include from Same Account"
                elif y == CheckNumSettings.IncludeRecentsOption.GLOBAL:                                             # noqa
                    y = "Include from All Accounts"
                elif y == CheckNumSettings.IncludeRecentsOption.NONE:                                               # noqa
                    y = "Don't Include"

                theData.append(" >>Recent Entries:          %s" %(y))
                theData.append(" >>Max Entries:             %s" %(x.getMaximumRecents()))
                theData.append(" >>Show Next-Check Number:  %s" %(x.getIncludeNextCheckNumber()))
                theData.append(" >>Show Print-Check Option: %s" %(x.getIncludePrintCheckMarker()))
                theData.append("\n")
                # CheckNumSettings.IncludeRecentsOption

        theData.append(("\n<END>"))

        # Build a quick virtual file of Memorized reports and graphs to display
        for i in range(0, len(theData)):
            theData[i] = theData[i] + "\n"
        theData = "".join(theData)
        return theData

    def isUserEncryptionPassphraseSet():

        try:
            keyFile = File(moneydance_data.getRootFolder(), "key")

            keyInfo = SyncRecord()
            fin = FileInputStream(keyFile)
            keyInfo.readSet(fin)
            fin.close()
            return keyInfo.getBoolean("userpass", False)
        except:
            pass
        return False


    def getMDEncryptionKey():

        try:
            keyFile = File(moneydance_data.getRootFolder(), u"key")

            keyInfo = SyncRecord()
            fin = FileInputStream(keyFile)
            keyInfo.readSet(fin)
            fin.close()

            # noinspection PyUnresolvedReferences
            cipherLevel = LocalStorageCipher.MDCipherLevel.GOOD

            keyString=keyInfo.getString(u"key",None)
            test_with_random = u"E6520436865636B2C2062616279206F6E65203220312074776F4D6963726F7068306E6520436865636B204D6963723070686F6"
            y=StringUtils.decodeHex(test_with_random[int(len(test_with_random)/2):]+test_with_random[:int(len(test_with_random)/2)])
            z=""
            for x in y: z+=chr(x)
            newPassphrase = z
            encryptedKeyBytes = StringUtils.decodeHex(keyString)
            if keyInfo.getBoolean(u"userpass", False):
                newPassphrase = moneydance_ui.getCurrentAccounts().getEncryptionKey()
                if not newPassphrase:
                    return u"Not sure: Error retrieving your Encryption key!"
            try:

                # This next line triggers a message in the console error log file: "loading with 128 bit encryption key"
                myPrint(u"J",u"Checking encryption key....")
                key = LocalStorageCipher.encryptionKeyFromBytesAndPassword(encryptedKeyBytes, list(newPassphrase), cipherLevel)
                # cipher = LocalStorageCipher(key, cipherLevel)
            except:
                return u"Not sure: could not validate your encryption!"

            theFormat  = key.getFormat()
            theAlg = key.getAlgorithm()
        except:
            return u"Not sure: Error in decryption routine - oh well!!"


        return u"%s / %s" % (theFormat, theAlg)

    def check_dropbox_and_suppress_warnings():

        dataFile = moneydance_data.getRootFolder()
        suppressFile = File(dataFile, "suppress_file_in_dropbox_restriction.txt")

        fileIsUnderDropbox = False
        suppressionFileExists = suppressFile.exists()
        parent = dataFile
        while parent is not None:
            if "dropbox" in parent.getName().lower():
                fileIsUnderDropbox = True
                break
            parent = parent.getParentFile()

        return fileIsUnderDropbox, suppressionFileExists


    def OFX_view_online_txns_payees_payments(statusLabel):

        _OBJOFXTXNS     =  0
        _OBJOFXOLPAYEES =  1
        _OBJOFXOLPAYMNT =  2

        objWhat = [
                    "OFX Online Transactions",                  # onlineTxnList             "oltxns"
                    "OFX Online Payees",                        # onlinePayeeList           "olpayees"
                    "OFX Online Payments"                       # onlinePaymentList         "olpmts"
            ]

        selectedAcct = None
        selectedObject = None
        textType = ""

        while True:

            selectedObjType = JOptionPane.showInputDialog(toolbox_frame_,
                                                       "Select the type of Online data you want to view",
                                                       "OFX View Online Data",
                                                       JOptionPane.INFORMATION_MESSAGE,
                                                       moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                       objWhat,
                                                       None)
            if not selectedObjType:
                statusLabel.setText(("No online data type was selected to view ..").ljust(800, " "))
                statusLabel.setForeground(Color.RED)
                return

            if objWhat.index(selectedObjType) == _OBJOFXTXNS:
                accountsListForOlTxns = AccountUtil.allMatchesForSearch(moneydance_data, MyAcctFilter(15))
            elif objWhat.index(selectedObjType) == _OBJOFXOLPAYEES:
                accountsListForOlTxns = AccountUtil.allMatchesForSearch(moneydance_data, MyAcctFilter(16))
            elif objWhat.index(selectedObjType) == _OBJOFXOLPAYMNT:
                accountsListForOlTxns = AccountUtil.allMatchesForSearch(moneydance_data, MyAcctFilter(17))
            else: continue

            accountsListForOlTxns = sorted(accountsListForOlTxns, key=lambda sort_x: (sort_x.getFullAccountName().upper()))
            selectedAcct = JOptionPane.showInputDialog(toolbox_frame_,
                                                       "Select the Acct to view Online Data:",
                                                       "Select ACCOUNT",
                                                       JOptionPane.INFORMATION_MESSAGE,
                                                       moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                       accountsListForOlTxns,
                                                       None)  # type: Account
            if not selectedAcct: continue

            textType = ""
            if objWhat.index(selectedObjType) == _OBJOFXTXNS:
                selectedObject = MyGetDownloadedTxns(selectedAcct)           # Use my version to prevent creation of default record(s)
                textType = "Online Txns"
            elif objWhat.index(selectedObjType) == _OBJOFXOLPAYEES:
                selectedObject = MyGetOnlinePayees(selectedAcct)             # Use my version to prevent creation of default record(s)
                textType = "Online Payees"
            elif objWhat.index(selectedObjType) == _OBJOFXOLPAYMNT:
                selectedObject = MyGetOnlinePayments(selectedAcct)           # Use my version to prevent creation of default record(s)
                textType = "Online Payments"
            else: continue

            break

        output = "VIEW SAVED ONLINE DATA: %s\n" \
                 " ===================================\n\n" %(textType.upper())

        output += "Object Type: %s\n\n" %(type(selectedObject))

        # noinspection PyUnresolvedReferences
        output += "Linked Account Type: %s Acct Name: %s\n" %(selectedAcct.getAccountType(), selectedAcct.getFullAccountName())

        if isinstance(selectedObject, OnlineTxnList):
            output += "\n\nMD User Representation of Data Held by this Account/OnlineTxnList record:\n"
            output += " ==========================================================================  \n"
            output += "%s %s\n" % (pad("getTxnCount():",50),                        selectedObject.getTxnCount()  )
            output += "%s %s (%s)\n" % (pad("getOFXLastTxnUpdate():",50),           selectedObject.getOFXLastTxnUpdate(), DateUtil.convertLongDateToInt(selectedObject.getOFXLastTxnUpdate())  )
            output += "%s %s\n" % (pad("hasOnlineAvailBalance():",50),              selectedObject.hasOnlineAvailBalance()  )
            output += "%s %s\n" % (pad("getOnlineAvailBalance():",50),              selectedObject.getOnlineAvailBalance()  )
            output += "%s %s (%s)\n" % (pad("getOnlineAvailBalanceDate():",50),     selectedObject.getOnlineAvailBalanceDate(), DateUtil.convertLongDateToInt(selectedObject.getOnlineAvailBalanceDate())  )
            output += "%s %s\n" % (pad("hasOnlineLedgerBalance():",50),             selectedObject.hasOnlineLedgerBalance()  )
            output += "%s %s\n" % (pad("getOnlineLedgerBalance():",50),             selectedObject.getOnlineLedgerBalance()  )
            output += "%s %s (%s)\n" % (pad("getOnlineLedgerBalanceDate():",50),    selectedObject.getOnlineLedgerBalanceDate(), DateUtil.convertLongDateToInt(selectedObject.getOnlineLedgerBalanceDate())  )

        if isinstance(selectedObject, OnlinePayeeList):
            output += "\n\nMD User Representation of Data Held by this Account/OnlinePayeeList record:\n"
            output += " ==========================================================================  \n"
            output += "%s %s\n" % (pad("getPayeeCount():",50),             selectedObject.getPayeeCount()  )

        if isinstance(selectedObject, OnlinePaymentList):
            output += "\n\nMD User Representation of Data Held by this Account/OnlinePaymentList record:\n"
            output += " ==========================================================================  \n"
            output += "%s %s\n" % (pad("getPaymentCount():",50),           selectedObject.getPaymentCount()  )

        output+="\n"

        for convertTimeStamp in ["ts", "rec_dt", "dtentered", "creation_date"]:
            if selectedObject.getLongParameter(convertTimeStamp, 0) > 0:
                output += "%s %s\n" % (pad("TIMESTAMP('%s'):" %(convertTimeStamp),50), get_time_stamp_as_nice_text(selectedObject.getLongParameter(convertTimeStamp, 0))  )

        keys = sorted(selectedObject.getParameterKeys())
        for theKey in keys:
            # noinspection PyUnresolvedReferences
            value = selectedObject.getParameter(theKey)
            output += pad("Key:%s" %theKey,50)+" Value: '%s'\n" %(value.strip())

        output+="\n\n<END>"

        QuickJFrame("VIEW SAVED ONLINE DATA",output).show_the_frame()

        return

    def get_ofx_related_data():

        from java.lang.reflect import Modifier

        OFX = []

        lCachePasswords = \
            (isUserEncryptionPassphraseSet() and moneydance_ui.getCurrentAccounts().getBook().getLocalStorage().getBoolean("store_passwords", False))

        # Build a list of Moneydance accounts that are enabled for download and have a service profile linked....
        listAccountMDProxies=[]
        olAccounts = AccountUtil.allMatchesForSearch(moneydance_data, MyAcctFilter(11))
        if len(olAccounts) > 0:
            for acctObj in olAccounts:
                acct = acctObj                                 # type: Account
                svcBank = acct.getBankingFI()                  # type: OnlineService
                svcBP = acct.getBillPayFI()                    # type: OnlineService
                if acct.getBankingFI() is not None:
                    listAccountMDProxies.append([MDAccountProxy(acct, False),svcBank,False])
                if acct.getBillPayFI() is not None:
                    listAccountMDProxies.append([MDAccountProxy(acct, True),svcBP,True])

        OFX.append("VIEW YOUR INSTALLED OFX SERVICE / BANK LOGON PROFILES\n"
                   " ====================================================\n\n")

        if lCachePasswords:
            OFX.append("MD Will allow you to Cache your Authentication (means you have set an encryption key and selected store passwords..")
        else:
            OFX.append("MD Cache Authentication ** DISABLED ** (either no user encryption key or store passwords = no..")

        OFX.append("")

        OFX.append("MD Accounts enabled for OFX Downloads with linked Service / Bank logon profiles:")
        if len(listAccountMDProxies)<1:
            OFX.append("<NONE FOUND>")
        else:
            for olAcct in listAccountMDProxies:
                if not olAcct[2]:
                    OFX.append("- %s Bank Profile: %s" %(pad(olAcct[0].getAccount().getFullAccountName(),40),olAcct[1]))
                else:
                    OFX.append("- %s BillPay Profile: %s" %(pad(olAcct[0].getAccount().getFullAccountName(),40),olAcct[1]))
        OFX.append("")

        for service in moneydance_data.getOnlineInfo().getAllServices():

            # Find the MD accounts specifically linked to this service profile
            thisServiceMDAccountProxies=[]
            for olacct in listAccountMDProxies:
                if olacct[1] is service:
                    thisServiceMDAccountProxies.append(olacct)

            OFX.append(pad("Service/Profile:".upper(),40)       + str(service))
            OFX.append(pad("----------------",40))
            OFX.append(pad(">>Moneydance TIK Service ID:",40)   + str(service.getTIKServiceID()))
            OFX.append(pad(">>OFX Version:",40)                 + str(service.getOFXVersion()))
            OFX.append(pad(">>Service Id:",40)                  + str(service.getServiceId()))
            OFX.append(pad(">>Service Type:",40)                + str(service.getServiceType()))
            OFX.append(pad(">>Realms:",40)                      + str(service.getRealms()))
            OFX.append(pad(">>Bootstrap URL:",40)               + str(service.getBootstrapURL()))

            OFX.append(pad(">>Needs FI Profile Check()?:",40)   + str(service.needsFIProfileCheck()))

            OFX.append(pad("\n>>Accounts configured within bank profile:",120))
            if len(service.getAvailableAccounts())<1:
                OFX.append("<NONE FOUND>")
            else:
                OFX.append(pad(" -- List All accounts configured in profile:",40) + str(service.getAvailableAccounts()))
                for availAccount in service.getAvailableAccounts():
                    OFX.append(">> ACCOUNT: %s (%s)" %(availAccount.getDescription(),availAccount.getAccountNumber()))

                    try:
                        # Rather than listing all methods by hand, just iterate and call them all.. I have checked they are all safe...
                        meths = availAccount.getClass().getDeclaredMethods()
                        for meth in meths:
                            if not Modifier.isPublic(meth.getModifiers()): continue
                            if meth.getName().lower().startswith("get") or meth.getName().lower().startswith("is") \
                                    and meth.getParameterCount()<1:
                                result = meth.invoke(availAccount)
                                if result is not None:
                                    OFX.append(" >> %s %s" %(pad(meth.getName(),40),result) )
                    except:
                        pass

            OFX.append("")

            OFX.append(pad("\n>>MD Accounts linked to this service / bank profile:",120))
            if len(thisServiceMDAccountProxies)<1:
                OFX.append("<NONE FOUND>")
            else:
                for olacct in thisServiceMDAccountProxies:
                    if not olacct[2]:
                        OFX.append(" >> Banking: %s" %(olacct[0].getAccount().getFullAccountName()))
                    else:
                        OFX.append(" >> BillPay: %s" %(olacct[0].getAccount().getFullAccountName()))

            OFX.append("")

            try:
                p_getAuthenticationCachePrefix=service.getClass().getDeclaredMethod("getAuthenticationCachePrefix")
                p_getAuthenticationCachePrefix.setAccessible(True)
                OFX.append(pad("AuthenticationCachePrefix:",33) + str(p_getAuthenticationCachePrefix.invoke(service)))
                p_getAuthenticationCachePrefix.setAccessible(False)

                p_getSessionCookiePrefix=service.getClass().getDeclaredMethod("getSessionCookiePrefix")
                p_getSessionCookiePrefix.setAccessible(True)
                OFX.append(pad("SessionCookiePrefix:",33    ) + str(p_getSessionCookiePrefix.invoke(service)))
                p_getSessionCookiePrefix.setAccessible(False)
            except:
                pass

            OFX.append(pad("\n>>REALMs configured:",120))
            realmsToCheck = service.getRealms()
            if "DEFAULT" not in realmsToCheck:
                realmsToCheck.insert(0,"DEFAULT")
            for realm in realmsToCheck:
                OFX.append("Realm: %s User ID: %s" %(realm, service.getUserId(realm, None)))
                for olacct in thisServiceMDAccountProxies:

                    if lCachePasswords:
                        authKey = "ofx:" + realm
                        authObj = service.getCachedAuthentication(authKey)
                        OFX.append("Realm: %s Cached Authentication: %s" %(realm, authObj))

                        authKey = "ofx:" + (realm + "::" + olacct[0].getAccountKey())
                        authObj = service.getCachedAuthentication(authKey)
                        OFX.append("Realm: %s Account Key: %s Cached Authentication: %s" %(realm, olacct[0].getAccountKey(),authObj))

                    userID=service.getUserId(realm, olacct[0])
                    OFX.append("Realm: %s UserID: %s" %(realm, userID))

                    if service.getSessionCookie(userID) is not None:
                        OFX.append("Session Cookie: %s" %(service.getSessionCookie(userID)))

            OFX.append("getFIId()                        %s" %(service.getFIId()                             ))
            if service.getUpdatedFIId() != service.getFIId():
                OFX.append("getUpdatedFIId()             %s" %(service.getUpdatedFIId()                      ))
            OFX.append("getFIName()                      %s" %(service.getFIName()                           ))
            OFX.append("getFIOrg()                       %s" %(service.getFIOrg()                            ))
            if service.getUpdatedFIOrg() != service.getUpdatedFIOrg():
                OFX.append("getUpdatedFIOrg()            %s" %(service.getUpdatedFIOrg()                     ))
            OFX.append("usesFITag()                      %s" %(service.usesFITag()                           ))
            OFX.append("usesPTTAcctIDField()             %s" %(service.usesPTTAcctIDField()                  ))
            OFX.append("getFIUrl()                       %s" %(service.getFIUrl()                            ))
            OFX.append("getFIUrlIsRedirect()             %s" %(service.getFIUrlIsRedirect()                  ))

            OFX.append("getIgnoreTxnsBeforeLastUpdate()  %s" %(service.getIgnoreTxnsBeforeLastUpdate()       ))

            OFX.append("getTxnDownloadOverlap()          %s" %(service.getTxnDownloadOverlap()               ))
            OFX.append("getDateAvailAcctsUpdated()       %s" %(service.getDateAvailAcctsUpdated()            ))
            OFX.append("getAlwaysSendDateRange()         %s" %(service.getAlwaysSendDateRange()              ))


            OFX.append("getUseProfileRequest()           %s" %(service.getUseProfileRequest()                ))
            OFX.append("getUseClientSpecificUIDS()       %s" %(service.getUseClientSpecificUIDS()            ))
            OFX.append("getUseFileUIDs()                 %s" %(service.getUseFileUIDs()                      ))
            OFX.append("getUseBPFileUIDs()               %s" %(service.getUseBPFileUIDs()                    ))
            OFX.append("useTerribleTLSV1Hack()           %s" %(service.useTerribleTLSV1Hack()                ))
            OFX.append("getFIEmail()                     %s" %(service.getFIEmail()                          ))
            OFX.append("getTechServicePhone()            %s" %(service.getTechServicePhone()                 ))

            OFX.append("getInvstBrokerID()               %s" %(service.getInvstBrokerID()                    ))

            OFX.append("usesBillPayExtendedAcctTo()      %s" %(service.usesBillPayExtendedAcctTo()           ))

            OFX.append("getServiceType()                 %s" %(service.getServiceType()                      ))

            OFX.append("getUseShortDates()               %s" %(service.getUseShortDates()                    ))
            OFX.append("shouldDecrementLastTxnDate()     %s" %(service.shouldDecrementLastTxnDate()          ))

            OFX.append("getSignupAcctsAvail()            %s" %(service.getSignupAcctsAvail()                 ))
            OFX.append("getSignupCanActivateAcct()       %s" %(service.getSignupCanActivateAcct()            ))
            OFX.append("getSignupCanChgUserInfo()        %s" %(service.getSignupCanChgUserInfo()             ))
            OFX.append("getSignupCanPreauth()            %s" %(service.getSignupCanPreauth()                 ))
            OFX.append("getSignupClientAcctNumReq()      %s" %(service.getSignupClientAcctNumReq()           ))
            OFX.append("getSignupViaClient()             %s" %(service.getSignupViaClient()                  ))
            OFX.append("getSignupViaOther()              %s" %(service.getSignupViaOther()                   ))
            OFX.append("getSignupViaOtherMsg()           %s" %(service.getSignupViaOtherMsg()                ))
            OFX.append("getSignupViaWeb()                %s" %(service.getSignupViaWeb()                     ))
            OFX.append("getSignupViaWebUrl()             %s" %(service.getSignupViaWebUrl()                  ))
            OFX.append("getStopChkCanUseDescription()    %s" %(service.getStopChkCanUseDescription()         ))
            OFX.append("getStopChkCanUseRange()          %s" %(service.getStopChkCanUseRange()               ))
            OFX.append("getStopChkFee()                  %s" %(service.getStopChkFee()                       ))
            OFX.append("getStopChkProcessingDaysOff()    %s" %(service.getStopChkProcessingDaysOff()         ))
            OFX.append("getStopChkProcessingEndTime()    %s" %(service.getStopChkProcessingEndTime()         ))

            for x in service.getRealms():
                OFX.append("getClientIDRequired(x)           %s" %(service.getClientIDRequired(x)             ))
                OFX.append("getUserCanChangePIN(x)           %s" %(service.getUserCanChangePIN(x)             ))
                OFX.append("getMaxPasswdLength(x)            %s" %(service.getMaxPasswdLength(x)              ))
                OFX.append("getMinPasswdLength(x)            %s" %(service.getMinPasswdLength(x)              ))
                OFX.append("getMustChngPINFirst(x)           %s" %(service.getMustChngPINFirst(x)             ))
                OFX.append("getPasswdCanHaveSpaces(x)        %s" %(service.getPasswdCanHaveSpaces(x)          ))
                OFX.append("getPasswdCanHaveSpecialChars(x)  %s" %(service.getPasswdCanHaveSpecialChars(x)    ))
                OFX.append("getPasswdCaseSensitive(x)        %s" %(service.getPasswdCaseSensitive(x)          ))
                OFX.append("getPasswdCharType(x)             %s" %(service.getPasswdCharType(x)               ))
                OFX.append("getPasswdType(x)                 %s" %(service.getPasswdType(x)                   ))

            OFX.append("getDateUpdated()                 %s (%s)" %(service.getDateUpdated(), DateUtil.convertLongDateToInt(service.getDateUpdated())))
            OFX.append("getLastTransactionID()           %s" %(service.getLastTransactionID()                  ))
            OFX.append("getMaxFITIDLength()              %s" %(service.getMaxFITIDLength()                     ))
            OFX.append("getInvalidAcctTypes()            %s" %(service.getInvalidAcctTypes()                   ))

            p_getMsgSetTag=service.getClass().getDeclaredMethod("getMsgSetTag",[Integer.TYPE])
            p_getMsgSetTag.setAccessible(True)

            for msgType in (0,1,3,4,5,6,7,8,9,10,11,12):
                if service.supportsMsgSet(msgType) or msgType==0:
                    tag=p_getMsgSetTag.invoke(service,[msgType])
                    OFX.append("---")
                    OFX.append("  Supports Message Tag:            %s" %(tag))
                    OFX.append("  getMsgSetLanguage(msgType)       %s" %(service.getMsgSetLanguage(msgType)             ))
                    OFX.append("  getMsgSetRspnsFileErrors(msgType)%s" %(service.getMsgSetRspnsFileErrors(msgType)      ))
                    OFX.append("  getMsgSetSecurity(msgType)       %s" %(service.getMsgSetSecurity(msgType)             ))
                    OFX.append("  getMsgSetSignonRealm(msgType)    %s" %(service.getMsgSetSignonRealm(msgType)          ))
                    OFX.append("  getMsgSetSyncMode(msgType)       %s" %(service.getMsgSetSyncMode(msgType)             ))
                    OFX.append("  getMsgSetTransportSecure(msgType)%s" %(service.getMsgSetTransportSecure(msgType)      ))
                    OFX.append("  getMsgSetURL(msgType)            %s" %(service.getMsgSetURL(msgType)                  ))
                    OFX.append("  getMsgSetVersion(msgType)        %s" %(service.getMsgSetVersion(msgType)              ))
            p_getMsgSetTag.setAccessible(False)

            OFX.append("---")

            OFX.append("getCreditCardClosingAvail()      %s" %(service.getCreditCardClosingAvail()           ))
            OFX.append("getCustServicePhone()            %s" %(service.getCustServicePhone()                 ))
            OFX.append("getBankClosingAvail()            %s" %(service.getBankClosingAvail()                 ))
            OFX.append("getBankXfrCanModifyModels()      %s" %(service.getBankXfrCanModifyModels()           ))
            OFX.append("getBankXfrCanModifyTransfers()   %s" %(service.getBankXfrCanModifyTransfers()        ))
            OFX.append("getBankXfrCanScheduleRecurring() %s" %(service.getBankXfrCanScheduleRecurring()      ))
            OFX.append("getBankXfrCanScheduleTransfers() %s" %(service.getBankXfrCanScheduleTransfers()      ))
            OFX.append("getBankXfrDaysWithdrawn()        %s" %(service.getBankXfrDaysWithdrawn()             ))
            OFX.append("getBankXfrDefaultDaysToPay()     %s" %(service.getBankXfrDefaultDaysToPay()          ))
            OFX.append("getBankXfrModelWindow()          %s" %(service.getBankXfrModelWindow()               ))
            OFX.append("getBankXfrNeedsTAN()             %s" %(service.getBankXfrNeedsTAN()                  ))
            OFX.append("getBankXfrProcessingDaysOff()    %s" %(service.getBankXfrProcessingDaysOff()         ))
            OFX.append("getBankXfrProcessingEndTime()    %s" %(service.getBankXfrProcessingEndTime()         ))
            OFX.append("getBankXfrSupportsDTAvail()      %s" %(service.getBankXfrSupportsDTAvail()           ))
            OFX.append("getBillPayCanAddPayee()          %s" %(service.getBillPayCanAddPayee()               ))
            OFX.append("getBillPayCanModPayments()       %s" %(service.getBillPayCanModPayments()            ))
            OFX.append("getBillPayDaysWithdrawn()        %s" %(service.getBillPayDaysWithdrawn()             ))
            OFX.append("getBillPayDefaultDaysToPay()     %s" %(service.getBillPayDefaultDaysToPay()          ))
            OFX.append("getBillPayHasExtendedPmt()       %s" %(service.getBillPayHasExtendedPmt()            ))
            OFX.append("getBillPayNeedsTANPayee()        %s" %(service.getBillPayNeedsTANPayee()             ))
            OFX.append("getBillPayNeedsTANPayment()      %s" %(service.getBillPayNeedsTANPayment()           ))
            OFX.append("getBillPayPostProcessingWindow() %s" %(service.getBillPayPostProcessingWindow()      ))
            OFX.append("getBillPayProcessingDaysOff()    %s" %(service.getBillPayProcessingDaysOff()         ))
            OFX.append("getBillPayProcessingEndTime()    %s" %(service.getBillPayProcessingEndTime()         ))
            OFX.append("getBillPaySupportsDifftFirstPmt()%s" %(service.getBillPaySupportsDifftFirstPmt()     ))
            OFX.append("getBillPaySupportsDifftLastPmt() %s" %(service.getBillPaySupportsDifftLastPmt()      ))
            OFX.append("getBillPaySupportsDtAvail()      %s" %(service.getBillPaySupportsDtAvail()           ))
            OFX.append("getBillPaySupportsPmtByAddr()    %s" %(service.getBillPaySupportsPmtByAddr()         ))
            OFX.append("getBillPaySupportsPmtByPayeeId() %s" %(service.getBillPaySupportsPmtByPayeeId()      ))
            OFX.append("getBillPaySupportsPmtByXfr()     %s" %(service.getBillPaySupportsPmtByXfr()          ))
            OFX.append("getBillPaySupportsStatusModRs()  %s" %(service.getBillPaySupportsStatusModRs()       ))
            OFX.append("getBillPayXfrDaysWith()          %s" %(service.getBillPayXfrDaysWith()               ))
            OFX.append("getBillPayXfrDefaultDaysToPay()  %s" %(service.getBillPayXfrDefaultDaysToPay()       ))
            OFX.append("getEmailSupportsGeneric()        %s" %(service.getEmailSupportsGeneric()             ))
            OFX.append("getEmailSupportsGetMime()        %s" %(service.getEmailSupportsGetMime()             ))
            OFX.append("getInvstCanDownloadBalances()    %s" %(service.getInvstCanDownloadBalances()         ))
            OFX.append("getInvstCanDownloadOOs()         %s" %(service.getInvstCanDownloadOOs()              ))
            OFX.append("getInvstCanDownloadPositions()   %s" %(service.getInvstCanDownloadPositions()        ))
            OFX.append("getInvstCanDownloadTxns()        %s" %(service.getInvstCanDownloadTxns()             ))
            OFX.append("getInvstCanEmail()               %s" %(service.getInvstCanEmail()                    ))
            OFX.append("getSecListCanDownloadSecurities()%s" %(service.getSecListCanDownloadSecurities()     ))

            OFX.append("")

            sortKeys=sorted(service.getParameterKeys())
            OFX.append(pad("Raw Parameter keys:",40))
            for x in sortKeys:
                OFX.append("%s %s" %(pad(x,40),service.getParameter(x,None)))

            OFX.append("\n------------------------------------------------------------------\n\n")

        OFX.append("\n<END>")
        for i in range(0, len(OFX)):
            OFX[i] = OFX[i] + "\n"
        OFX = "".join(OFX)

        # <WOW! Phew - we actually made it!>
        QuickJFrame("VIEW INSTALLED SERVICE / BANK LOGON PROFILES",OFX).show_the_frame()

        return

    def display_help():
        global debug, MYPYTHON_DOWNLOAD_URL

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )

        help_data = """
The Infinite Kind (Moneydance) - Co-authored by Stuart Beesley in collaboration with Moneydance as a support tool

Original Author: Stuart Beesley - StuWareSoftSystems (Nov 2020 thru Feb 2021 - a lockdown project ~500 programming hours)
Credit: Derek Kent(23) for his extensive texting and many hours on this project!
        Also thanks to Kevin(N), Dan T Davis, and dwg for their testing, input and OFX Bank help/input.....

Get more Scripts/Extensions from: %s

Minimum Moneydance version for use as an Extension: 2021 (build: 2012) - (Minimum version %s if run as a script)
NOTE: You may need to download the MD preview version from: https://infinitekind.com/preview
(If you have installed the extension, but nothing happens, then check your Moneydance version)

This is a Python(Jython 2.7) script that runs inside of Moneydance via the Moneybox Python Interpreter
As such it has full access to Moneydance's internals.
However, where possible this script uses the published APIs. In certain circumstances, it calls internal functions.
The script will never change anything without your permission - and it will always ask you for such (several times).

DISCLAIMER: YOU USE THIS SCRIPT AT YOUR OWN RISK AND YOU ACCEPT ANY CONSEQUENCES OF CHANGING YOUR DATA!

PLEASE ALWAYS BACKUP YOUR DATA FIRST! You  can use the Export Backup (green) button top-left in Toolbox to do this.

PURPOSE

To enable the User to self-diagnose problems, or access key diagnostics to enable support to help
- Basic (default) mode is very safe - it contains view options only
- Advanced Mode - Allows user to run fixes - THIS CHANGES DATA
- Geek Mode - Allows user to view technical information/settings in various places (this is readonly)
- Hacker Mode - Allows the user to manually add/change/delete config.dict and LocalStorage() keys/values - ONLY USE IF YOU KNOW WHAT YOU ARE DOING
                Also allows you to toggle Moneydance internal settings like DEBUG

- The Toolbox offers the option to Backup first  - ALWAYS BACKUP (But this is your choice!)
- The Toolbox will *ALWAYS* make a copy of config.dict, custom theme file, LocalStorage() ./safe/settings before any changes
>> These backup files will have a unique (timestamp-like) number and _$SAVED$ appended to the end of the filename

>> Your dataset backups will be located wherever you choose to save them (USE THE 'EXPORT BACKUP' button (top left in green)
>> Note the normal Moneydance Backup is a complete dataset, but does not include config.dict, custom theme file, extensions etc

- All updates (and other key messages) get written to the Moneydance console error log

# Includes my previous / standalone scripts (now withdrawn):
# FIX-reset_window_location_data.py 0.2beta
# DIAG-can_i_delete_security.py v2
# DIAG-list_security_currency_decimal_places.py v1
# DIAG-diagnose_currencies.py v2a
# fix_macos_tabbing_mode.py v1b

# Also includes these MD scripts (enhanced)
# reset_relative_currencies.py                          (from Moneydance support)
# remove_ofx_account_bindings.py                        (from Moneydance support)
# convert_secondary_to_primary_data_set.py              (from Moneydance support)
# remove_one_service.py                                 (from Moneydance support)
# delete_invalid_txns.py                                (from Moneydance support)
# price_history_thinner.py                              (from Moneydance support)
# fix_dropbox_one_way_syncing.py                        (from Moneydance support)
# reset_sync_and_dropbox_settings.py                    (from Moneydance support)
# force_change_account_currency.py                      (from Moneydance support)
# fix_restored_accounts.py (check only)                 (from Moneydance support)
# export_all_attachments.py                             (from Moneydance support)
# fix_account_parent.py                                 (from Moneydance support)
# (... and old check_root_structure.py)                 (from Moneydance support)
# fix_non-hierarchical_security_account_txns.py         (from Moneydance support)
# (... and fix_investment_txns_to_wrong_security.py)    (from Moneydance support)
# remove_ofx_security_bindings.py                       (from Moneydance support)
# show_object_type_quantities.py                        (from Moneydance support)
# delete_intermediate_downloaded_transaction_caches.py  (from Moneydance support)
# delete_orphaned_downloaded_txn_lists.py               (from Moneydance support)
# set_account_type.py                                   (from Moneydance support)
# force_change_all_currencies.py                        (from Moneydance support)
# fix_invalid_currency_rates.py                         (from Moneydance support)
# reverse_txn_amounts.py                                (from Moneydance support)
# reverse_txn_exchange_rates_by_account_and_date.py     (from Moneydance support)
# show_open_tax_lots.py                                 (author unknown)
# MakeFifoCost.py                                       (author unknown)
# change-security-cusip.py                              (from Finite Mobius, LLC / Jason R. Miller)

Features:
- Main window shows various diagnostic data and MD Preferences

** Toolbox turns on all Moneydance's internal DEBUG messages at startup. This puts extra messages into the Console window
   This is a useful tip - i.e. have the console window open and you will get more information when running tasks (e.g. OFX)

NOTE: Where CMD is specified, this may be CTRL (or ALT) in Windows / Linux

CMD-I - This  Help Instruction Information

CMD-O - Copy all outputs to Clipboard

TOOLBAR / MENU BAR Contains the following:
    - Toolbox Options Menu
    - Help menu
    - Button: Launch Console Window (opens the Moneydance Help>Show Console Window)
    - Button: Save Console Log (to a file of your choosing)
    - Button: Open MD Folder (Preferences, Themes, Console log, Dataset, Extensions, Auto-backup folder, last backup folder[, Install Dir])
    - Button: Copy Diagnostics below to Clipboard (copies the main screen output to clipboard)

ALT-B - Basic Mode
- Basic mode: Buttons
    - EXPORT BACKUP (This calls the Moneydance function to backup your dataset)
    - Analyse Dataset Objects Size & Files
    - Find my Dataset (Search for *.moneydance & *.moneydancearchive Datasets)
    - MENU: General Tools (contains a variety of general Diagnostics, Fixes and Tools...)
        - Display Dataset Password/Hint and Sync Passphrase
        - View MD Config.dict file
        - View MD Custom Theme file  (only appears if it exists)
        - View your Java .vmoptions file (only appears if it exists) - INCLUDES VARIOUS INSTRUCTIONS TOO
        - View Extensions details
        - View memorised reports (parameters and default settings)
        - Find my Sync Encryption password(s) in iOS Backup(s)
        - Execute the 'older' Import QIF file and set parameters for import (useful if you want to import Account Structure Only)
    - MENU: Online (OFX) Banking Tools:
        - Search for stored OFX related data
        - View your installed Service / Bank logon profiles
        - View full list of all MD's Bank dynamic setup profiles (and then select one to view specific details)
        - View your Online saved Txns, Payees, Payments
        - Toggle Moneydance DEBUG (turns ON all MD internal Debug messages - same as view console)
    - MENU: Accounts & Categories tools
        - View Check number settings
        - DIAGnostics - View Categories with zero balance. You can also inactivate using Advanced mode.
    - MENU: Currency & Security tools:
        - DIAGnostics - Can I delete a Security (tells you whether a security/stock is being used - and where)
        - DIAGnostics - List decimal places (currency & security). Shows you hidden settings etc.
        - DIAGnostics - Show your open LOTs on stocks/shares (when using LOT control) (show_open_tax_lots.py)
        - DIAGnostics - Diagnose relative currencies (currency & security's key settings). If errors, then go to FIX below
    - MENU: Transactions tools
        - View Register Txn Sort Orders
        - Extract your Attachments (this decrypts and extracts your attachments to a directory of your choice) (export_all_attachments.py)
        - DIAGnostics - Analise your  attachments (and Detect Orphans)

ALT-M - Advanced Mode
    - These first four buttons will appear only if they are necessary / possible in your system 
        - FIX - Make me a Primary Dataset (convert from secondary dataset to enable Sync)) (convert_secondary_to_primary_data_set.py)
        - FIX - Create Dropbox Sync Folder (creates the missing .moneydancesync folder if missing from Dropbox)
        - FIX - Check / fix MacOS Tabbing Mode on Big Sur (when set to always). It will allow you to change it to fullscreen or manual/never.
                More information here: https://support.apple.com/en-gb/guide/mac-help/mchla4695cce/mac
        - FIX - Fix Dropbox One Way Syncing (runs the fix_dropbox_one_way_syncing.py / reset_sync_and_dropbox_settings.py script / fix). Removes key "migrated.netsync.dropbox.fileid"
    - MENU: General Tools (contains a variety of general Diagnostics, Fixes and Tools...)
        - FIX - Change Moneydance Fonts
        - FIX - Delete Custom Theme file
        - FIX - Delete Orphaned/Outdated Extensions (from config.dict and .mxt files)
        - FIX - RESET Window Display Settings
                This allows you to tell Moneydance to forget remembered Display settings:
                1. RESET>> Just Window locations (i.e. it leaves the other settings intact).
                2. RESET>> Just Register Transaction Filters.
                3. RESET>> Just Register Transaction Initial Views (e.g. In investments, start on Portfolio or Security View
                4. RESET>> Window locations, Size, Sort Orders, One-line, Split Reg, Offset, Column Widths; Dividers, isOpen,
                isExpanded, isMaximised settings (this does not reset Filters or Initial views)
    - MENU: Online (OFX) Banking Tools:
        - All basic mode settings plus:
        - Forget OFX Banking Import Link (so that it asks you which account when importing ofx files) (remove_ofx_account_bindings.py)
        - Delete OFX Banking Logon Profile / Service (these are logon profiles that allow you to connect to your bank) (remove_one_service.py)
        - Reset/Fix/Edit/Add CUSIP Banking Link. This is the link for downloaded securities.... (remove_ofx_security_bindings.py and change-security-cusip.py)
        - Update OFXLastTxnUpdate Last Download Date for Online Txns
        - Delete single cached OnlineTxnList record/Txns
        - Delete ALL cached OnlineTxnList record/Txns (delete_intermediate_downloaded_transaction_caches.py)
        - OFX Cookie Management (some options also required Hacker mode)
        - OFX Authentication Management (some options also required Hacker mode)
    - MENU: Accounts & Categories tools
        - FIX - Inactivate all Categories with Zero Balance
        - FIX - FORCE change an Account's Type (use with care. Does not update any transactions) (set_account_type.py)
        - FIX - FORCE change an Account's Currency (use with care. Does not update any transactions) (force_change_account_currency.py)
        - FIX - FORCE change ALL Account's currencies (use with care. Does not update any transactions) (force_change_all_currencies.py)
        - FIX - Account's Invalid Parent Account (script fix_account_parent.py)
        - FIX - Correct the Name of Root to match Dataset
    - MENU: Currency & Security tools:
        - FIX - Fix relative currencies (fixes your currency & security's key settings) (reset_relative_currencies.py)
        - FIX - Convert Stock to LOT Controlled and Allocate LOTs using FiFo method (MakeFifoCost.py)
        - FIX - Convert Stock to Average Cost Control (and wipe any LOT control records)
        - FIX - Thin/Purge Price History (allows you to thin/prune your price history based on parameters you input; also fix 'orphans') (price_history_thinner.py)
        - FIX - Fix invalid relative currency (& security) rates (fixes relative rates where <0 or >9999999999) (fix_invalid_currency_rates.py)
        - FIX - FORCE change an Account's Currency (use with care. Does not update any transactions) (force_change_account_currency.py)
        - FIX - FORCE change ALL Account's currencies (use with care. Does not update any transactions) (force_change_all_currencies.py)
    - MENU: Transactions tools
        - FIX - Non Hierarchical Security Account Txns (cross-linked securities) (fix_non-hierarchical_security_account_txns.py & fix_investment_txns_to_wrong_security.py)
        - FIX - Delete One-Sided Txns (delete_invalid_txns.py)
        - FIX - Reverse Transaction Amounts between dates (reverse_txn_amounts.py)
        - FIX - Reverse Transaction Exchange rates between dates (reverse_txn_amounts.py)

ALT-G - GEEK OUT MODE
    >> Allows you to view raw settings
    - Search for keys or key-data containing filter characters (you specify)
    - ROOT Parameter keys
    - Local Storage - Settings
    - User Preferences
    - All Accounts' preference keys
    - View single Object's Keys/Data (Account, Category, Currency, Security, Report / Graph, Reminder, Address, OFX Service, by UUID, TXNs)
    - All Sync Settings
    - All Online Banking Settings
    - All Settings related to window sizes/positions/locations etc
    - All Environment Variables
    - All Java Properties

Menu - HACKER MODE
    >> VERY TECHNICAL - DO NOT USE UNLESS YOU KNOW WHAT YOU ARE DOING
    - Toggle other known DEBUG settings on (extra messages in Console)
    - Toggle all internal Moneydance DEBUG settings ON/OFF (same as viewing console)
    - Extract (a single) File from within LocalStorage. Decrypts a LocalStorage file to TMP dir for viewing (file self destructs after MD restart)
    - Import (a single) File back into LocalStorage. Encrypts a file of your choosing and puts it into LocalStorage/safe/TMP...
    - Allows User to Add/Change/Delete Settings/Prefs >> key/value in config.dict or LocalStorage() (./safe/settings)
    - Edit/Change/Delete an Object's Parameter keys (this can change data in your dataset/database directly)
    - Remove Int/Ext Files from File-list.
        >> External locations > Edits config.dict to remove references to external files for File/open - AND ALLOWS YOU TO DELETE THE FILES TOO
        >> Default / Internal locations > ALLOWS YOU TO DELETE THE Dataset from disk (this then removes it from the File/Open menu)
    - Call Save Trunk File option....
    - DEMOTE your Primary Sync dataset/node back to a Secondary Node..
    - Suppress the "Your file seems to be in a shared folder (Dropbox)" warning... (optional when condition exists)

CMD-P - View parameters file (StuWareSoftSystems). Also allows user to Delete all, and/or change/delete single saved parameters

Menu - DEBUG MODE
    >> Turns on this Extension's own internal debug messages...

Menu - Auto Prune of Internal Backup files
    >> Toolbox makes extra backups of config.dict, ./safe/settings and custom_theme.properties. This setting auto-prunes
       keeping at least 5 copies of each and / or 5 days
<END>
""" %(MYPYTHON_DOWNLOAD_URL, TOOLBOX_MINIMUM_TESTED_MD_VERSION)

        help_data = "".join(help_data)

        return help_data

    # noinspection PyArgumentList
    class MyTxnSearchFilter(TxnSearch):

        def __init__(self,dateStart,dateEnd):
            super(TxnSearch, self).__init__()

            self.dateStart = dateStart
            self.dateEnd = dateEnd

        def matchesAll(self):                                                                                           # noqa
            return False

        def matches(self, txn):

            if txn.getDateInt() >= self.dateStart and txn.getDateInt() <= self.dateEnd:                                 # noqa
                return True
            return False

    class MyAcctFilter(AcctFilter):
        selectType = 0

        def __init__(self, selectType=0):
            self.selectType = selectType

        def matches(self, acct):
            if self.selectType == 0:
                # noinspection PyUnresolvedReferences
                if not (acct.getAccountType() == Account.AccountType.BANK
                        or acct.getAccountType() == Account.AccountType.CREDIT_CARD
                        or acct.getAccountType() == Account.AccountType.INVESTMENT):
                    return False

            if self.selectType == 10:
                # noinspection PyUnresolvedReferences
                if not (acct.getAccountType() == Account.AccountType.BANK
                        or acct.getAccountType() == Account.AccountType.CREDIT_CARD
                        or acct.getAccountType() == Account.AccountType.INVESTMENT):
                    return False

                if acct.getParameter("ofx_import_acct_num", None) is not None \
                        or acct.getParameter("ofx_import_remember_acct_num", None) is not None:
                    return True
                return False

            if self.selectType == 1:
                # noinspection PyUnresolvedReferences
                if not (acct.getAccountType() == Account.AccountType.BANK
                        or acct.getAccountType() == Account.AccountType.CREDIT_CARD
                        or acct.getAccountType() == Account.AccountType.LOAN
                        or acct.getAccountType() == Account.AccountType.ASSET
                        or acct.getAccountType() == Account.AccountType.ROOT
                        or acct.getAccountType() == Account.AccountType.LIABILITY
                        or acct.getAccountType() == Account.AccountType.INVESTMENT):
                    return False

            if self.selectType == 2:
                # noinspection PyUnresolvedReferences
                if acct.getAccountType() == Account.AccountType.SECURITY: return True
                else: return False

            if self.selectType == 3:
                # noinspection PyUnresolvedReferences
                if not (acct.getAccountType() == Account.AccountType.BANK
                        or acct.getAccountType() == Account.AccountType.ROOT):
                    return False

            if self.selectType == 4:
                # noinspection PyUnresolvedReferences
                if not (acct.getAccountType() == Account.AccountType.EXPENSE
                        or acct.getAccountType() == Account.AccountType.INCOME):
                    return False
                return True

            if self.selectType == 5:
                # noinspection PyUnresolvedReferences
                if not (acct.getAccountType() == Account.AccountType.BANK
                        or acct.getAccountType() == Account.AccountType.CREDIT_CARD
                        or acct.getAccountType() == Account.AccountType.LOAN
                        or acct.getAccountType() == Account.AccountType.ASSET
                        or acct.getAccountType() == Account.AccountType.LIABILITY
                        or acct.getAccountType() == Account.AccountType.INVESTMENT):
                    return False
                return True

            if self.selectType == 6:
                # if not (acct.getAccountType() == Account.AccountType.BANK
                #         or acct.getAccountType() == Account.AccountType.CREDIT_CARD
                #         or acct.getAccountType() == Account.AccountType.LOAN
                #         or acct.getAccountType() == Account.AccountType.ASSET
                #         or acct.getAccountType() == Account.AccountType.ROOT
                #         or acct.getAccountType() == Account.AccountType.LIABILITY
                #         or acct.getAccountType() == Account.AccountType.INVESTMENT):
                #     return False
                return True

            if self.selectType == 7:
                # noinspection PyUnresolvedReferences
                if not (acct.getAccountType() == Account.AccountType.BANK
                        or acct.getAccountType() == Account.AccountType.CREDIT_CARD
                        or acct.getAccountType() == Account.AccountType.LOAN
                        or acct.getAccountType() == Account.AccountType.ASSET
                        or acct.getAccountType() == Account.AccountType.LIABILITY
                        or acct.getAccountType() == Account.AccountType.INVESTMENT):
                    return False
                return True

            if self.selectType == 8:
                # noinspection PyUnresolvedReferences
                if not (acct.getAccountType() == Account.AccountType.EXPENSE
                        or acct.getAccountType() == Account.AccountType.INCOME):
                    return False
                return True

            if self.selectType == 9:
                # noinspection PyUnresolvedReferences
                if not acct.getAccountType() == Account.AccountType.SECURITY:
                    return False
                return True

            if self.selectType == 11:
                if acct.canDownloadTxns() and not acct.getAccountIsInactive():
                    return True
                else:
                    return False

            if self.selectType == 12:
                # noinspection PyUnresolvedReferences
                if acct.getAccountType() == Account.AccountType.ROOT:
                    return True
                else:
                    return False

            if self.selectType == 13:
                # noinspection PyUnresolvedReferences
                if acct.getAccountType() != Account.AccountType.SECURITY: return False
                if not acct.getUsesAverageCost(): return False
                else: return True

            if self.selectType == 14:
                # noinspection PyUnresolvedReferences
                if acct.getAccountType() != Account.AccountType.SECURITY: return False
                if not acct.getUsesAverageCost():
                    return True
                else:
                    # Check for accounts using avg cost control with LOTS set....
                    txnSet = moneydance_data.getTransactionSet().getTransactionsForAccount(acct)
                    for theTxn in txnSet:
                        if (InvestUtil.isSaleTransaction(theTxn.getParentTxn().getInvestTxnType())
                                and (theTxn.getParameter("cost_basis", None) is not None)):
                            myPrint("DB","MyAcctFilter: Account: %s Found LOT Tags %s" %(acct,theTxn.getParameter("cost_basis", None)))
                            return True

                # OK, No LOTs found on average cost controlled accounts.....
                return False

            if self.selectType == 15 or self.selectType == 16 or self.selectType == 17 or self.selectType == 18:
                # noinspection PyUnresolvedReferences
                if not (acct.getAccountType() == Account.AccountType.BANK
                        or acct.getAccountType() == Account.AccountType.CREDIT_CARD
                        or acct.getAccountType() == Account.AccountType.ASSET
                        or acct.getAccountType() == Account.AccountType.INVESTMENT):
                    return False

                if self.selectType == 15:
                    x = MyGetDownloadedTxns(acct)
                    if x is not None and x.getTxnCount() >= 0:          # change to > 0 for only those with txns etc
                        return True
                elif self.selectType == 18:
                    x = MyGetDownloadedTxns(acct)
                    if x is not None and x.getTxnCount() >= 0:
                        return True
                elif self.selectType == 16:
                    x = MyGetOnlinePayees(acct)
                    if x is not None and x.getPayeeCount() >= 0:        # change to > 0 for only those with payees etc
                        return True
                elif self.selectType == 17:
                    x = MyGetOnlinePayments(acct)
                    if x is not None and x.getPaymentCount() >= 0:      # change to > 0 for only those with payments etc
                        return True

                return False

            if self.selectType == 19:
                # noinspection PyUnresolvedReferences
                if acct.getAccountType() == Account.AccountType.SECURITY or acct.getAccountType() == Account.AccountType.ROOT: return False
                else: return True

            if self.selectType == 20:
                # noinspection PyUnresolvedReferences
                if not (acct.getAccountType() == Account.AccountType.BANK
                        or acct.getAccountType() == Account.AccountType.CREDIT_CARD
                        or acct.getAccountType() == Account.AccountType.LOAN
                        or acct.getAccountType() == Account.AccountType.ASSET
                        or acct.getAccountType() == Account.AccountType.LIABILITY):
                    return False
                return True

            if (acct.getAccountOrParentIsInactive()): return False
            if (acct.getHideOnHomePage() and acct.getBalance() == 0): return False

            return True


    def MyGetOnlinePayees(theAcct):     # Use my version to prevent creation of default record(s)
        payeesListID = theAcct.getParameter("ol_payees_list_id", None)

        if payeesListID is not None:
            payeesObj = moneydance_data.getItemForID(payeesListID)    # type: SyncableItem
            if payeesObj is not None and isinstance(payeesObj, OnlinePayeeList):
                return payeesObj    # type: OnlinePayeeList

        # payees = OnlinePayeeList(moneydance_data)   # type: OnlinePayeeList
        # moneydance_data.logModifiedItem(payees)
        # theAcct.setOnlinePayees(payees)
        # return payees

        return None


    def MyGetOnlinePayments(theAcct):       # Use my version to prevent creation of default record(s)
        paymentsListID = theAcct.getParameter("ol_payments_list_id", None)
        if paymentsListID is not None:
            paymentsObj = moneydance_data.getItemForID(paymentsListID)      # type: SyncableItem
            if paymentsObj is not None and isinstance(paymentsObj, OnlinePaymentList):
                return paymentsObj  # type: OnlinePaymentList

        # payments = OnlinePaymentList(moneydance_data)   # type: OnlinePaymentList
        # moneydance_data.logModifiedItem(payments)
        # theAcct.setOnlinePayments(payments)
        # return payments

        return None

    def MyGetDownloadedTxns(theAcct):       # Use my version to prevent creation of default record(s)

        myID = theAcct.getParameter("id", None)
        defaultTxnsListID = myID + ".oltxns"

        if myID is not None and myID != "":
            defaultTxnList = moneydance_data.getItemForID(defaultTxnsListID)   # type: SyncableItem
            if defaultTxnList is not None and isinstance(defaultTxnList, OnlineTxnList):
                return defaultTxnList

        txnsListID = theAcct.getParameter("ol_txns_list_id", None)
        if txnsListID is None or txnsListID == "":
            if myID is not None and myID != "":
                txnsListID = defaultTxnsListID

        if txnsListID is not None and txnsListID != "":
            txnsObj = moneydance_data.getItemForID(txnsListID)              # type: SyncableItem
            if (txnsObj is not None and isinstance(txnsObj, OnlineTxnList)):
                return txnsObj

        # WE DON'T WANT TO DO THIS!
        # if myID is not None and myID != "":
        #     txns = OnlineTxnList(moneydance_data)                 # type: OnlineTxnList
        #     txns.setParameter("id", defaultTxnsListID)
        #     moneydance_data.logModifiedItem(txns)
        #     return txns
        #
        return None

    class ClipboardButtonAction(AbstractAction):
        theString = ""

        def __init__(self, theString, statusLabel):
            self.theString = theString
            self.statusLabel = statusLabel

        def actionPerformed(self, event):
            global toolbox_frame_, debug
            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )
            x = StringSelection(self.theString)
            Toolkit.getDefaultToolkit().getSystemClipboard().setContents(x, None)

            self.statusLabel.setText(("Contents of all text below copied to Clipboard..").ljust(800, " "))
            self.statusLabel.setForeground(Color.BLUE)

            myPrint("DB", "Contents of diagnostic report copied to clipboard....!")

            myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
            return


    class ShowTheConsole(AbstractAction):

        def __init__(self, statusLabel):
            self.statusLabel = statusLabel

        def actionPerformed(self, event):
            global debug

            myPrint("D","In ", inspect.currentframe().f_code.co_name, "()", "Event:", event)

            ConsoleWindow.showConsoleWindow(moneydance_ui)

            self.statusLabel.setText(("Standard Moneydance Console Window Launched....").ljust(800, " "))
            self.statusLabel.setForeground(Color.BLUE)

            myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

    class CopyConsoleLogFileButtonAction(AbstractAction):

        def __init__(self, statusLabel, theFile):
            self.statusLabel = statusLabel
            self.theFile = theFile

        def actionPerformed(self, event):
            global toolbox_frame_, debug
            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

            x = str(self.theFile)
            if not os.path.exists(x):
                self.statusLabel.setText(("Sorry, the file does not seem to exist: " + x).ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            if Platform.isOSX():
                System.setProperty("com.apple.macos.use-file-dialog-packages","true")  # In theory prevents access to app file structure (but doesnt seem to work)
                System.setProperty("apple.awt.fileDialogForDirectories", "true")

            filename = FileDialog(toolbox_frame_, "Select location to copy Console Log file to... (CANCEL=ABORT)")
            filename.setMultipleMode(False)
            filename.setMode(FileDialog.SAVE)
            filename.setFile('copy_of_errlog.txt')
            # filename.setDirectory(self.theFile.getParent())
            filename.setDirectory(get_home_dir())

            if (not Platform.isOSX() or not Platform.isOSXVersionAtLeast("10.13")):
                extFilter = ExtFilenameFilter("txt")
                filename.setFilenameFilter(extFilter)  # I'm not actually sure this works...?

            filename.setVisible(True)

            copyToFile = filename.getFile()

            if Platform.isOSX():
                System.setProperty("com.apple.macos.use-file-dialog-packages","true")  # In theory prevents access to app file structure (but doesnt seem to work)
                System.setProperty("apple.awt.fileDialogForDirectories", "false")

            if (copyToFile is None) or copyToFile == "":
                self.statusLabel.setText(("User did not select file location - no copy performed").ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                filename.dispose()
                del filename
                return
            elif not str(copyToFile).endswith(".txt"):
                self.statusLabel.setText(("Sorry - please use a .txt file extension when copying  console log file").ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                filename.dispose()
                del filename
                return
            elif ".moneydance" in filename.getDirectory():
                self.statusLabel.setText(("Sorry, please choose a location outside of the  Moneydance location").ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                filename.dispose()
                del filename
                return

            copyToFile = os.path.join(filename.getDirectory(), filename.getFile())

            if not check_file_writable(copyToFile):
                self.statusLabel.setText(("Sorry, that file/location does not appear allowed by the operating system!?").ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)

            try:
                toFile = File(filename.getDirectory(), filename.getFile())
                IOUtils.copy(self.theFile, toFile)
                myPrint("B", x + " copied to " + str(toFile))
                # noinspection PyTypeChecker
                if os.path.exists(os.path.join(filename.getDirectory(), filename.getFile())):
                    play_the_money_sound()
                    self.statusLabel.setText(("Console Log file save as requested to: " + str(toFile)).ljust(800, " "))
                    self.statusLabel.setForeground(Color.BLUE)
                else:
                    myPrint("B", "ERROR - failed to copy file" + x + " to " + str(filename.getFile()))
                    self.statusLabel.setText(("Sorry, failed to save console log file?!").ljust(800, " "))
                    self.statusLabel.setForeground(Color.RED)
            except:
                myPrint("B", "ERROR - failed to copy file" + x + " to " + str(filename.getFile()))
                dump_sys_error_to_md_console_and_errorlog()
                self.statusLabel.setText(("Sorry, failed to save console log file?!").ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)

            filename.dispose()
            del filename

            return


    class QuickJFrame():

        def __init__(self, title, output, lAlertLevel=0):
            self.title = title
            self.output = output
            self.lAlertLevel = lAlertLevel

        class ReSizeListener(ComponentAdapter):

            def __init__(self, theFrame, theScrollPane):
                self.theFrame = theFrame
                self.theScrollPane = theScrollPane

            def componentResized(self, componentEvent):                                                                 # noqa
                global debug, toolbox_frame_

                myPrint("D","In ", inspect.currentframe().f_code.co_name, "()")

                # calcWidth = self.theFrame.getSize().width-20
                # calcHeight = self.theFrame.getSize().height-20
                #
                # self.theFrame.setSize(Dimension(calcWidth, calcHeight))
                #
                # self.theScrollPane.revalidate()
                # self.theFrame.repaint()

                myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

        class CloseAction(AbstractAction):

            def __init__(self, theFrame):
                self.theFrame = theFrame

            def actionPerformed(self, event):
                global debug
                myPrint("D","in CloseAction(), Event: ", event)

                myPrint("DB", "QuickJFrame() Frame shutting down....")

                self.theFrame.dispose()
                return

        def show_the_frame(self):
            global lCopyAllToClipBoard_TB, debug, toolbox_frame_

            screenSize = Toolkit.getDefaultToolkit().getScreenSize()
            # frame_width = screenSize.width - 20
            # frame_height = screenSize.height - 20

            frame_width = min(screenSize.width-20, max(1024,int(round(moneydance_ui.firstMainFrame.getSize().width *.9,0))))
            frame_height = min(screenSize.height-20, max(768, int(round(moneydance_ui.firstMainFrame.getSize().height *.9,0))))

            JFrame.setDefaultLookAndFeelDecorated(True)

            jInternalFrame = MyJFrame(self.title)
            jInternalFrame.setName(u"%s_quickjframe" %myModuleID)

            if not Platform.isOSX():
                jInternalFrame.setIconImage(MDImages.getImage(moneydance_ui.getMain().getSourceInformation().getIconResource()))

            jInternalFrame.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE)
            jInternalFrame.setResizable(True)

            shortcut = Toolkit.getDefaultToolkit().getMenuShortcutKeyMaskEx()
            jInternalFrame.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_W, shortcut), "close-window")
            jInternalFrame.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_F4, shortcut), "close-window")
            jInternalFrame.getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0), "close-window")

            jInternalFrame.getRootPane().getActionMap().put("close-window", self.CloseAction(jInternalFrame))

            theJText = JTextArea(self.output)
            theJText.setEditable(False)
            theJText.setLineWrap(True)
            theJText.setWrapStyleWord(True)
            # theJText.setFont(Font("monospaced", Font.PLAIN, 15))
            theJText.setFont( getMonoFont() )

            internalScrollPane = JScrollPane(theJText, JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED,JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED)

            if self.lAlertLevel>=2:
                internalScrollPane.setBackground(Color.RED)
                theJText.setBackground(Color.RED)
                theJText.setForeground(Color.BLACK)
            elif self.lAlertLevel>=1:
                internalScrollPane.setBackground(Color.YELLOW)
                theJText.setBackground(Color.YELLOW)
                theJText.setForeground(Color.BLACK)

            # jInternalFrame.setMinimumSize(Dimension(frame_width, 0))
            # jInternalFrame.setMaximumSize(Dimension(frame_width, frame_height))

            jInternalFrame.setPreferredSize(Dimension(frame_width, frame_height))


            # if Platform.isWindows():
            #     if theJText.getLineCount() > 30:
            #         jInternalFrame.setPreferredSize(Dimension(frame_width - 50, frame_height - 100))
            #

            jInternalFrame.add(internalScrollPane)

            jInternalFrame.pack()
            jInternalFrame.setLocationRelativeTo(toolbox_frame_)

            # jInternalFrame.getRootPane().addComponentListener(self.ReSizeListener(jInternalFrame, internalScrollPane))

            jInternalFrame.setVisible(True)

            if "errlog.txt" in self.title:
                theJText.setCaretPosition(theJText.getDocument().getLength())

            try:
                if lCopyAllToClipBoard_TB:
                    Toolkit.getDefaultToolkit().getSystemClipboard().setContents(StringSelection(self.output), None)
            except:

                myPrint("J","Error copying contents to Clipboard")
                dump_sys_error_to_md_console_and_errorlog()

            return (jInternalFrame)

    def display_pickle():
        global debug, myParameters

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )

        if myParameters is None: myParameters = {}

        params = []
        for key in sorted(myParameters.keys()):
            params.append("Key: " + pad(str(key),50) + " Type: " + pad(str(type(myParameters[key])),20) + "Value: " + str(myParameters[key]) + "\n")

        params.append("\n<END>")

        params = "".join(params)

        return params

    def can_I_delete_security(statusLabel):
        global toolbox_frame_, debug
        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )

        myPrint("B", "Script running to analyse whether you can delete a Security, or show where it's used....")
        myPrint("P", "----------------------------------------------------------------------------------------")

        if moneydance_data is None: return

        usageCount = 0
        sumShares = 0

        book = moneydance.getCurrentAccountBook()
        allCurrencies = book.getCurrencies().getAllCurrencies()

        securities = []

        for currency in allCurrencies:
            # noinspection PyUnresolvedReferences
            if currency.getCurrencyType() == CurrencyType.Type.SECURITY:
                securities.append(currency)

        securities = sorted(securities, key=lambda x: (x.getName().upper()))

        selectedSecurity = JOptionPane.showInputDialog(toolbox_frame_,
                                                       "Select Security", "Select the security to analyse",
                                                       JOptionPane.INFORMATION_MESSAGE,
                                                       moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                       securities,
                                                       None)
        if selectedSecurity is None:
            statusLabel.setText("No security was selected - aborting..".ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            return

        output = "\nYou want me to look for Security: " + str(selectedSecurity) + "\n"

        accountsList = AccountUtil.allMatchesForSearch(book, MyAcctFilter(2))
        output += "Searching through %s security (sub) accounts.." % (len(accountsList)) + "\n"

        for account in accountsList:
            if account.getCurrencyType() == selectedSecurity:
                # noinspection PyUnresolvedReferences
                output += "   >> Security: %s is used in Account: %s - Share holding balance: %s" \
                          % (selectedSecurity, account.getParentAccount().getAccountName(),
                             selectedSecurity.getDoubleValue(account.getBalance())) + "\n"
                # noinspection PyUnresolvedReferences
                sumShares += selectedSecurity.getDoubleValue(account.getBalance())
                usageCount += 1

        if not usageCount:
            output += "   >> Security not found in any accounts.\n"

        output += "\nChecking security for price history...:\n"

        # noinspection PyUnresolvedReferences
        secSnapshots = selectedSecurity.getSnapshots()
        countPriceHistory = secSnapshots.size()
        if countPriceHistory > 0:
            output += "   >> Security has %s historical prices!" % (secSnapshots.size()) + "\n"
        else:
            output += "   >> Security has no historical prices. \n"

        output += "-----------------------------------------------------------------\n"
        if usageCount:
            output += "\nUSAGE FOUND: You are using security: %s in %s accounts!\n... with a share balance of: %s. These would need to be removed before security deletion" \
                      % (selectedSecurity, usageCount, sumShares) + "\n"
            myPrint("J", ">> NO - Security cannot be deleted as it's being used:" + str(selectedSecurity))

        if countPriceHistory:
            output += "\nPRICE HISTORY FOUND: You have %s price records - If you delete Security then these will be lost..." \
                      % countPriceHistory + "\n"

        if not usageCount and not countPriceHistory:
            output += "\nNo usage of security %s found! You should be able to safely delete the Security" % selectedSecurity + "\n"
            statusLabel.setText(("No usage of security %s found! You should be able to safely delete the Security" % selectedSecurity).ljust(800, " "))
        else:
            statusLabel.setText(("Sorry - usage of Security: %s found - refer to script output for details.." % selectedSecurity).ljust(800,
                                                                                                                        " "))

        statusLabel.setForeground(Color.RED)

        output += "\n<END>"
        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
        return output

    def list_security_currency_decimal_places(statusLabel):
        global toolbox_frame_, debug, DARK_GREEN
        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )

        myPrint("B", "Script is analysing your Security decimal place settings...........")
        myPrint("P", "-------------------------------------------------------------------")

        if moneydance_data is None: return

        iWarnings = 0
        myLen = 50

        decimalPoint_MD = moneydance_ui.getPreferences().getSetting("decimal_character", ".")

        currs = moneydance_data.getCurrencies().getAllCurrencies()

        currs = sorted(currs, key=lambda x: str(x.getName()).upper())

        output = ""

        def get_curr_sec_name(curr_sec):
            if curr_sec.getName() is not None and len(curr_sec.getName().strip()) > 0:
                return curr_sec.getName()
            return (curr_sec.getIDString() + ":" + curr_sec.getIDString())

        def analyse_curr(theCurr, theType):
            output = ""                                                                                                 # noqa
            iWarn = 0
            for sec_curr in theCurr:
                if str(sec_curr.getCurrencyType()) != theType: continue

                foo = str(round(CurrencyUtil.getUserRate(sec_curr, sec_curr.getRelativeCurrency()), 8))
                priceDecimals = max(sec_curr.getDecimalPlaces(), min(8, len(foo.split(decimalPoint_MD)[-1])))

                output += pad(get_curr_sec_name(sec_curr),myLen) + "\tDPC: " + \
                          str(sec_curr.getDecimalPlaces()) + \
                          "\t" + \
                          "Relative to: " + str(sec_curr.getRelativeCurrency())[:20].ljust(20, " ") + \
                          "\t" + \
                          "Current rate: " + str(foo)[:20].ljust(20, " ") + \
                          "\tRate dpc: " + str(priceDecimals)
                if (sec_curr.getDecimalPlaces() < priceDecimals and theType == "SECURITY") and \
                        not foo.endswith(".0"):
                    iWarn += 1
                    output += " ***\n"
                else:
                    output += "\n"
            return iWarn, output

        output += " ==============\n"
        output += " --- SECURITIES ----\n"
        output += " ==============\n"

        result = analyse_curr(currs, "SECURITY")
        iWarnings += result[0]
        output += result[1]

        output += " ==============\n"
        output += " --- CURRENCIES ----\n"
        output += " ==============\n"
        result = analyse_curr(currs, "CURRENCY")
        iWarnings += result[0]
        output += result[1]

        output += "-----------------------------------------------------------------"
        if iWarnings:
            output += "\nYou have %s Warning(s)..\n" % iWarnings
            output += "These are where your security decimal place settings seem less than 4 or not equal to price history dpc; This might be OK - depends on your setup\n"
            output += "NOTE: It's quite hard to determine the stored dpc, so use this as guidance only, not definitive!\n"
            output += "NOTE: - This setting is fixed. The only resolution is to create a new security and alter your txns to use the new security...\n"
            output += "DISCLAIMER: Always backup your data before changing your data. I can take no responsibility for any changes....\n"
            myPrint("J", "Decimal places: You have %s Warning(s).. Refer diagnostic file...\n" % iWarnings)
            statusLabel.setText(
                ("Decimal places: You have %s Warning(s).. Refer diagnostic file..." % iWarnings).ljust(800, " "))
            statusLabel.setForeground(Color.RED)
        else:
            output += "\nAll good, decimal places look clean! Congratulations!\n"
            myPrint("J", "All good, decimal places look clean! Congratulations!")
            statusLabel.setText("All good, decimal places look clean! Congratulations!".ljust(800, " "))
            statusLabel.setForeground(DARK_GREEN)

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

        output += "\n<END>"
        return output

    def read_preferences_file(lSaveFirst=False):

        cf = Common.getPreferencesFile()

        if lSaveFirst:
            moneydance.savePreferences()

        try:
            st = StreamTable()
            st.readFromFile(str(cf))
            tk = st.getKeyArray()
            tk = sorted(tk)
        except:
            st, tk = None, None
            dump_sys_error_to_md_console_and_errorlog()

        return st,tk

    def check_for_window_display_data( theKey, theValue ):

        if not isinstance(theValue, (str,unicode)):             return False
        if theKey.startswith("gui.current_theme"):              return False
        if theKey.startswith("gui.dashboard.item"):             return False
        if theKey.startswith("gui.font_increment"):             return False
        if theKey.startswith("gui.new_txn_on_record"):          return False
        if theKey.startswith("gui.quickdecimal"):               return False
        if theKey.startswith("gui.register_follows_txns"):      return False
        if theKey.startswith("gui.show_all_accts_in_popup"):    return False
        if theKey.startswith("gui.source_list_visible"):        return False

        # Preferences Home Screen options
        if theKey.startswith("gui.home.lefties"):               return False
        if theKey.startswith("gui.home.righties"):              return False
        if theKey.startswith("gui.home.unused"):                return False

        if not (theKey.startswith("ext_mgmt_win")
                or theKey.startswith("moneybot_py_divider")
                or theKey.startswith("mbot.loc")
                or theKey.startswith("gui.")
                or theKey.endswith("rec_reg.credit")
                or theKey.endswith("rec_reg.debit")
                or "col_widths." in theKey
                or ("sel_" in theKey and theKey.endswith("_filter"))
                or "sel_inv_view" in theKey):
            return False

        if not ("window" in theKey
                or "win_loc" in theKey
                or "width" in theKey
                or "isopen" in theKey
                or "winloc" in theKey
                or "winsize" in theKey
                or "winsz" in theKey
                or "divider" in theKey
                or "location" in theKey
                or "size" in theKey
                or "rec_reg.credit" in theKey
                or "rec_reg.debit" in theKey
                or "mbot.loc" in theKey
                or "_expanded" in theKey
                or "_filter" in theKey
                or "maximized" in theKey
                or "sel_inv_view" in theKey):
            return False

        return True

    def check_for_just_locations_window_display_data( theKey, theValue ):

        # Assumes you have called check_for_window_display_data() first!

        # Locations are  number x number - e.g. 10x100
        if "x" not in theValue.lower(): return False

        if not ("win_loc" in theKey
                or "winloc" in theKey
                or "location" in theKey
                or "mbot.loc" in theKey):
            return False

        return True

    # noinspection PyUnusedLocal
    def check_for_just_register_filters_window_display_data( theKey, theValue ):

        # Assumes you have called check_for_window_display_data() first!

        if  not ("sel_" in theKey and theKey.endswith("_filter") ):
            return False

        return True

    # noinspection PyUnusedLocal
    def check_for_just_initial_view_filters_window_display_data( theKey, theValue ):

        if  not ("sel_" in theKey and theKey.endswith("_view") ):
            return False

        return True

    # copied from Moneydance TxnRegister.class
    def loadMDPreferences(dataObject,  preferencesKey, lGetDefaultForObject=True):   # dataObject should always = Account.

        preferencesKey = preferencesKey

        if not preferencesKey:
            dataPrefKey = "col_widths"
        else:
            dataPrefKey = "col_widths." + preferencesKey

        colWidthPrefs = None

        if dataObject:
            colWidthPrefs = dataObject.getPreference(dataPrefKey, None)

        if not lGetDefaultForObject and dataObject and not colWidthPrefs: return None

        if StringUtils.isBlank(colWidthPrefs) and preferencesKey:
            colWidthPrefs = moneydance_ui.getPreferences().getSetting(dataPrefKey, None)

        if not colWidthPrefs or StringUtils.isBlank(colWidthPrefs):
            return None

        if not colWidthPrefs.startswith(":"):
            colWidthPrefs = ":" + colWidthPrefs

        params = SyncRecord()
        try:
            params.readSet(StringReader(colWidthPrefs))
        except IOException:
            myPrint("B", "Error parsing register settings: " + colWidthPrefs + " key=" + preferencesKey)
            return None

        widths = params.getIntArray("cols")                                                     # int[]

        if params.getBoolean("splitreg", False):
            splitReg = True
            splitSz = Dimension(10, Math.max(0, params.getInt("splitsz", 100)))                   # Dimension
        else:
            splitSz = None
            splitReg = False

        ascending = params.getBoolean("ascending", True)
        sortID = TxnSortOrder.fromInt(params.getInt("sort", -1), ascending)                     # TxnSortOrder

        if sortID:
            pass

        oneLineMode = params.getBoolean("oneline", False)                                     # boolean

        position = params.getString("position", params.getString("offset", None))               # String
        if position:
            pass

        position2 = params.getString("position2", params.getString("offset2", None))            # String
        if position2:
            pass

        theUUID = None
        if dataObject: theUUID = dataObject.getUUID()

        if debug:
            myPrint("D","Object: ", dataObject, theUUID)
            myPrint("D","Analysing the key: %s" %preferencesKey)
            myPrint("D",":oneline:", oneLineMode, type(oneLineMode))
            myPrint("D","splitreg:", splitReg, type(splitReg))
            myPrint("D","splitsz:", splitSz, type(splitSz))
            myPrint("D","sort:", sortID, type(sortID))
            myPrint("D","position:", position, type(position))
            myPrint("D","ascending:", ascending, type(ascending))
            myPrint("D","cols:", widths, type(widths))
            myPrint("D","position2:", position2, type(position2))

        return [oneLineMode, splitReg, splitSz, sortID, position, ascending, widths, position2]

    def extract_StuWareSoftSystems_version(theVersionToCheck):

        _MAJOR = 0
        _MINOR = 1

        theVersionToCheck = str(theVersionToCheck).strip()

        if len(theVersionToCheck) < 1: return [0,0]

        if len(theVersionToCheck) == 1: return [int(theVersionToCheck),0]

        if "." in theVersionToCheck:
            x = theVersionToCheck.split(".")
            return [int(x[0]),x[1]]

        major = minor = ""

        for char in theVersionToCheck:
            if (not minor) and (char >= "0" and char <= "9"): # noqa
                major += char
                continue
            minor+=char

        if debug:
            myPrint("D","Decoded: %s.%s" %(major,minor))

        try:
            return [int(major),minor]
        except:
            return [0,0]

    def check_for_updatable_extensions_on_startup(statusLabel):
        global lIgnoreOutdatedExtensions_TB

        Toolbox_version = 0

        displayData = u"\nALERT INFORMATION ABOUT YOUR EXTENSIONS:\n\n"

        try:
            theUpdateList = get_extension_update_info()

            if not theUpdateList or len(theUpdateList)<1:
                return Toolbox_version

            for key in theUpdateList.keys():
                updateInfo = theUpdateList[key]
                displayData+=u"** UPGRADEABLE EXTENSION: %s to version: %s\n" %(pad(key,20),(updateInfo[0].getBuild()))
                myPrint(u"B", u"** UPGRADEABLE EXTENSION: %s to version: %s" %(pad(key,20),(updateInfo[0].getBuild())))
                if key.lower() == u"%s" %myModuleID and int(updateInfo[0].getBuild()) > 0:
                    Toolbox_version = int(updateInfo[0].getBuild())
        except:
            dump_sys_error_to_md_console_and_errorlog()
            return Toolbox_version

        displayData+=u"\n<END>\n"

        howMany = int(len(theUpdateList))

        if not lIgnoreOutdatedExtensions_TB:
            statusLabel.setText( (u"ALERT - YOU HAVE %s EXTENSION(S) THAT CAN BE UPGRADED!..." %howMany ).ljust(800, u" "))
            statusLabel.setForeground(Color.BLUE)
            jif = QuickJFrame(u"EXTENSIONS ALERT!", displayData, 1).show_the_frame()
            options=[u"OK (keep reminding me)",u"OK - DON'T TELL ME AGAIN ON STARTUP!"]
            response = JOptionPane.showOptionDialog(jif,
                                                    u"INFO: You have %s older Extensions that can be upgraded" %howMany,
                                                    u"OUTDATED EXTENSIONS",
                                                    0,
                                                    JOptionPane.QUESTION_MESSAGE,
                                                    None,
                                                    options,
                                                    options[0])

            if response:
                myPrint(u"B",u"User requested to ignore Outdated warning extensions going forward..... I will obey!!")
                lIgnoreOutdatedExtensions_TB = True
        else:
            statusLabel.setText( (u"ALERT - YOU HAVE %s EXTENSION(S) THAT CAN BE UPGRADED!...STARTUP POPUP WARNINGS SUPPRESSED (by you)" %howMany ).ljust(800, " "))
            statusLabel.setForeground(Color.BLUE)

        return Toolbox_version

    def check_for_old_StuWareSoftSystems_scripts(statusLabel):
        global lPickle_version_warning, myParameters, i_am_an_extension_so_run_headless, debug
        global MYPYTHON_DOWNLOAD_URL

        lVersionWarning = False

        if not myParameters and not lPickle_version_warning:
            return

        displayData = "\nStuWareSoftSystems: ALERT INFORMATION ABOUT SCRIPTS:\n\n"

        if lPickle_version_warning:
            displayData += "I detected an older (encrypted) version of saved parameter file for use with my Python scripts\n"
            displayData += "No problem, I have updated / converted it.\n\n"

        _MAJOR = 0
        _MINOR = 1
        iCountOldScripts = 0

        if myParameters:

            for key in sorted(myParameters.keys()):
                if key.startswith("__") and key != "__Author":
                    myPrint("DB","Decoding old script versions for key: %s version_build: %s" %(key,myParameters[key]))
                    theVersion = extract_StuWareSoftSystems_version(myParameters[key])
                    if key == "__extract_currency_history_csv":
                        if theVersion[_MAJOR] <  1000:
                            pass
                        else: continue
                    elif key == "__StockGlance2020":
                        if theVersion[_MAJOR] <  1000:
                            pass
                        else: continue
                    elif key == "__extract_reminders_to_csv":     # Old key - renamed... but see if it's around....
                        if theVersion[_MAJOR] <  1000:
                            pass
                        else: continue
                    elif key == "__extract_reminders_csv":
                        if theVersion[_MAJOR] <  1000:
                            pass
                        else: continue
                    elif key == "__extract_investment_transactions":
                        if theVersion[_MAJOR] <  1000:
                            pass
                        else: continue
                    else: continue
                    displayData+="ALERT: Script: %s is out of date - you have version_build: %s_%s\n" %(key,theVersion[_MAJOR],theVersion[_MINOR])
                    myPrint("DB", "Script %s is out of date - PLEASE UPDATE"%key)
                    iCountOldScripts+=1
                    lVersionWarning = True


        if lPickle_version_warning or lVersionWarning:
            displayData+="""

CURRENT SCRIPT VERSIONS ARE:

toolbox.py:                             >1000

extract_data:                           >1000
This is a consolidation of all prior extract scripts - including:
- stockglance2020.py:                     
- extract_reminders_csv.py:               
- extract_currency_history_csv.py:        
- extract_investment_transactions_csv.py: 
- extract_account_registers_csv           

Please update any that you use to at least these versions listed above....

Download from here: %s
""" %(MYPYTHON_DOWNLOAD_URL)

            jif = QuickJFrame("StuWareSoftSystems - Scripts alert!", displayData, 1).show_the_frame()

            statusLabel.setText( ("PLEASE UPDATE OLDER VERSIONS OF STUWARESOFTSYSTEMS SCRIPTS!...").ljust(800, " "))
            statusLabel.setForeground(Color.BLUE)

            myPopupInformationBox(jif, "You have %s older StuWareSoftSystems scripts - please upgrade them!" % iCountOldScripts, "STUWARESOFTSYSTEMS' SCRIPTS", JOptionPane.WARNING_MESSAGE)

        return

    def find_the_program_install_dir():

        theDir = ""

        if Platform.isOSX():
            # Derive from these - not great, but OK: java.home, java.library.path, sun.boot.library.path

            test = System.getProperty("java.home").strip()
            _i = test.lower().find(".app/")                                                                             # noqa
            if _i > 0:
                theDir = test[:_i+4]
        else:
            theDir = System.getProperty("install4j.exeDir").strip()

        if not os.path.exists(theDir):
            theDir = ""

        return theDir


    def get_orphaned_extension():

        extension_prefs = moneydance_ui.getPreferences().getTableSetting("gen.fmodules",StreamTable())

        # Get all keys in config dict
        st,tk = read_preferences_file(lSaveFirst=True)  # Must flush memory to disk first before we read the file....
        confirmed_extn_keys = {}
        for theKey in tk:
            if not theKey.lower().startswith("confirmedext."):
                continue    # skip
            confirmed_extn_keys[theKey.split('.')[1].lower().strip()]  = theKey

        outdated={}
        x = moneydance.getOutdatedExtensionIDs()
        for y in x: outdated[y.lower().strip()] = True

        ok={}
        x = moneydance.getLoadedModules()
        for y in x: ok[str(y.getIDStr()).lower().strip()] = True
        x = moneydance.getSuppressedExtensionIDs()
        for y in x: ok[str(y).lower().strip()] = True

        orphan_outdated_prefs = {}
        for extn_pref in extension_prefs:
            if not ok.get(extn_pref.lower().strip()) and not outdated.get(extn_pref.lower().strip()):
                orphan_outdated_prefs[extn_pref] = "ORPHAN"
            elif outdated.get(extn_pref.lower().strip()):
                orphan_outdated_prefs[extn_pref] = "OUTDATED"

        orphan_confirmed_extn_keys = {}
        for extn_pref in confirmed_extn_keys:
            if not ok.get(extn_pref.lower().strip()) and not outdated.get(extn_pref.lower().strip()):
                orphan_confirmed_extn_keys[extn_pref] = ["ORPHAN",confirmed_extn_keys.get(extn_pref.lower().strip())]
            elif outdated.get(extn_pref.lower().strip()):
                orphan_confirmed_extn_keys[extn_pref] = ["OUTDATED",confirmed_extn_keys.get(extn_pref.lower().strip())]

        orphan_outdated_files={}
        extn_files_found=[]

        extensionDir = Common.getFeatureModulesDirectory()
        if extensionDir:
            # noinspection PyTypeChecker
            for root, dirs, files in os.walk(extensionDir.getAbsolutePath()):
                for filename in files:
                    for extn in ModuleLoader.FEATURE_MODULE_EXTENSIONS:
                        if filename.endswith("."+extn):
                            # got an Extension
                            extn_files_found.append([os.path.splitext(filename)[0].lower().strip(),filename])
                            pass

        for extn_file in extn_files_found:
            if not ok.get(extn_file[0]):
                if outdated.get(extn_file[0]):
                    orphan_outdated_files[extn_file[0]] = ["OUTDATED",extn_file[1]]
                else:
                    orphan_outdated_files[extn_file[0]] = ["ORPHAN",extn_file[1]]

        myPrint("DB","OK Extensions:", ok)
        myPrint("DB","OUTDATED: Extensions:", outdated)
        myPrint("DB","ORPHAN/OUTDATED Extension Preferences:", orphan_outdated_prefs)
        myPrint("DB","ORPHAN/OUTDATED Extension Files:", orphan_outdated_files)
        return [orphan_outdated_prefs, orphan_outdated_files, orphan_confirmed_extn_keys]

    def diagnose_currencies(statusLabel, lFix=False):
        global toolbox_frame_, debug, fixRCurrencyCheck, DARK_GREEN
        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )

        # reset_relative_currencies.py

        if lFix:
            myPrint("B", "Script running to FIX your relative currencies...............")
            myPrint("P", "---------------------------------------------------------")
        else:
            myPrint("B", "Script running to diagnose your relative currencies...............")
            myPrint("P", "---------------------------------------------------------")

        if moneydance_data is None: return

        VERBOSE=True
        lFixErrors=lFixWarnings=False
        lCurrencies=lSecurities=True

        if lFix:
            if not fixRCurrencyCheck:
                statusLabel.setText(("Sorry, you must run 'DIAG: Diagnose Currencies' first!").ljust(800, " "))
                statusLabel.setForeground(Color.RED)
                myPopupInformationBox(toolbox_frame_,"Sorry, you must run the 'DIAG: Diagnose Currencies' option first! - NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
                return
            elif fixRCurrencyCheck == 1:
                statusLabel.setText(("'DIAG: Diagnose Currencies' reported no issues - so I will not run fixes").ljust(800, " "))
                statusLabel.setForeground(Color.RED)
                myPopupInformationBox(toolbox_frame_,"'DIAG: Diagnose Currencies' reported no issues - so I will not run fixes - NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
                return
            elif fixRCurrencyCheck == 2:
                pass
            elif fixRCurrencyCheck != 3:
                statusLabel.setText(("LOGIC ERROR reviewing 'DIAG: Diagnose Currencies' - so I will not run fixes").ljust(800, " "))
                statusLabel.setForeground(Color.RED)
                myPopupInformationBox(toolbox_frame_,"LOGIC ERROR reviewing 'DIAG: Diagnose Currencies' - so I will not run fixes - NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
                return

            user_fixOnlyErrors = JRadioButton("Fix only Errors (ignore warnings)?", False)
            user_fixErrorsAndWarnings = JRadioButton("Fix Errors AND warnings?", False)
            bg1 = ButtonGroup()
            bg1.add(user_fixOnlyErrors)
            bg1.add(user_fixErrorsAndWarnings)

            user_fixOnlyCurrencies = JRadioButton("Fix only Currencies?", False)
            user_fixOnlySecurities = JRadioButton("Fix only Securities?", False)
            user_fixBothCurrenciesAndSecurities = JRadioButton("Fix BOTH Currencies AND Securities?", False)
            bg2 = ButtonGroup()
            bg2.add(user_fixOnlyCurrencies)
            bg2.add(user_fixOnlySecurities)
            bg2.add(user_fixBothCurrenciesAndSecurities)

            user_VERBOSE = JCheckBox("Verbose Output?",True)
            userFilters = JPanel(GridLayout(0, 1))

            if fixRCurrencyCheck != 2:
                userFilters.add(user_fixOnlyErrors)
            userFilters.add(user_fixErrorsAndWarnings)
            userFilters.add(JLabel("-------------"))
            userFilters.add(user_fixOnlyCurrencies)
            userFilters.add(user_fixOnlySecurities)
            userFilters.add(user_fixBothCurrenciesAndSecurities)
            userFilters.add(JLabel("-------------"))
            userFilters.add(user_VERBOSE)

            while True:
                options = ["EXIT", "PROCEED"]
                userAction = (JOptionPane.showOptionDialog(toolbox_frame_,
                                                           userFilters,
                                                           "FIX RELATIVE CURRENCIES",
                                                           JOptionPane.OK_CANCEL_OPTION,
                                                           JOptionPane.QUESTION_MESSAGE,
                                                           moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                           options, options[0]))
                if userAction != 1:
                    statusLabel.setText(("'FIX RELATIVE CURRENCIES' - No changes made.....").ljust(800, " "))
                    statusLabel.setForeground(Color.BLUE)
                    myPopupInformationBox(toolbox_frame_,"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
                    return

                if not user_fixOnlyErrors.isSelected() and not user_fixErrorsAndWarnings.isSelected():
                    continue
                if not user_fixOnlyCurrencies.isSelected() and not user_fixOnlySecurities.isSelected() and not user_fixBothCurrenciesAndSecurities.isSelected():
                    continue
                break

            del userFilters, bg1, bg2

            if not confirm_backup_confirm_disclaimer(toolbox_frame_, statusLabel,"FIX RELATIVE CURRENCIES", "EXECUTE FIX RELATIVE CURRENCIES?"):
                return

            VERBOSE = user_VERBOSE.isSelected()
            lFixErrors=True
            lFixWarnings=user_fixErrorsAndWarnings.isSelected()
            lCurrencies=(user_fixOnlyCurrencies.isSelected() or user_fixBothCurrenciesAndSecurities.isSelected())
            lSecurities=(user_fixOnlySecurities.isSelected() or user_fixBothCurrenciesAndSecurities.isSelected())

        # OK - let's do it!
        fixRCurrencyCheck = None

        lNeedFixScript = False
        iWarnings = 0

        currencies = moneydance_data.getCurrencies()
        baseCurr = currencies.getBaseType()

        if lFix:
            output = "FIX RELATIVE CURRENCIES/SECURITIES\n" \
                     " =================================\n\n"
        else:
            output = "DIAGNOSE RELATIVE CURRENCIES & SECURITIES\n" \
                     " ========================================\n\n"

        if lFix:
            output += "FIX MODE:\n" \
                      " ========\n" \
                      "Parameters Selected:\n" \
                      "- Fix Errors: %s\n" \
                      "- Fix Errors and Warnings: %s\n" \
                      "- Fix Currencies: %s\n" \
                      "- Fix Securities: %s\n" \
                      "- VERBOSE: %s\n\n" \
                      % (lFixErrors, lFixWarnings, lCurrencies, lSecurities, VERBOSE)

        if not lFix or lCurrencies:
            output += "Analysing the Base currency setup....\n"
            output += "Base currency: %s\n" % baseCurr

            if baseCurr.getParameter("rrate", None) is None or baseCurr.getDoubleParameter("rrate", 0.0) != 1.0:
                myPrint("J", "@@ERROR@@ - base currency %s has relative rate (rrate) <> 1: %s" %(baseCurr, baseCurr.getParameter("rrate", None)))
                output += "----\n@@ ERROR @@ - base currency %s has relative rate (rrate) <> 1: %s\n----\n" %(baseCurr, baseCurr.getParameter("rrate", None))
                lNeedFixScript = True
                if lFix:
                    baseCurr.setParameter("rrate", 1.0)
                    myPrint("J", "@@CURRENCY FIX APPLIED@@")
                    output += "----\n@@CURRENCY FIX APPLIED@@\n----\n"

            if baseCurr.getParameter("rate", None) is None or baseCurr.getDoubleParameter("rate", 0.0) != 1.0:
                myPrint("J", "@@ERROR@@ - base currency has rate <> 1: %s" %(baseCurr.getParameter("rate", None)))
                output += "----\n@@ ERROR @@ - base currency has rate <> 1: %s\n----\n" %(baseCurr.getParameter("rate", None))
                lNeedFixScript = True
                if lFix:
                    baseCurr.setParameter("rate", 1.0)
                    myPrint("J", "@@CURRENCY FIX APPLIED@@")
                    output += "----\n@@CURRENCY FIX APPLIED@@\n----\n"

            if lFix and lNeedFixScript:
                baseCurr.syncItem()

            if not lNeedFixScript:
                output += ("Base currency has Rate (rate) of: %s and Relative Rate (rrate): of %s.  This is Correct...\n"
                           % (baseCurr.getParameter("rate", None), baseCurr.getParameter("rrate", None)))

            baseSnapshots = baseCurr.getSnapshots()
            if baseSnapshots.size() > 0:
                lNeedFixScript = True
                myPrint("J","ERROR: base currency has %s historical prices! These need to be deleted!" % (baseSnapshots.size()))
                output += "----\n@@ ERROR: base currency has %s historical prices! These need to be deleted!\n----\n" % (baseSnapshots.size())
                for baseSnapshot in baseSnapshots:
                    if lFix:
                        output += "  @@DELETING@@: %s\n" % (baseSnapshot)
                        baseSnapshot.deleteItem()
                    else:
                        if VERBOSE:
                            output += "  snapshot: %s\n" % baseSnapshot
            else:
                output += "\nBase currency has no historical prices. This is correct\n"

            root = moneydance_data.getRootAccount()
            if root.getCurrencyType() != baseCurr:
                lNeedFixScript = True

                myPrint("J", "Root account's currency: %s, Base currency: %s" % (root.getCurrencyType(), baseCurr))
                output += "Root account's currency: %s, Base currency: %s\n" % (root.getCurrencyType(), baseCurr)

                myPrint("J", "ERROR - The root account's currency is not set to base! This needs correcting!")
                output += "----\n@@ ERROR - The root account's currency is not set to base! This needs correcting!\n----\n"

                if lFix:
                    root.setCurrencyType(baseCurr)
                    root.syncItem()
                    myPrint("J", "@@CURRENCY FIX APPLIED@@")
                    output += "----\n@@CURRENCY FIX APPLIED@@\n----\n"

            else:
                output += "GOOD, the root account's currency is set to the base currency! Root: %s, Base: %s\n" % (root.getCurrencyType(), baseCurr)

        currencies = sorted(currencies, key=lambda x: (x.getCurrencyType(), x.getName().upper()))

        last = None
        lWarning = False
        output += "\nAnalysing the Currency / Security table...\n" \
                  " ===========================================\n"

        for curr in currencies:

            if curr.getCurrencyType() != last:
                output += "\n\n TYPE: %s\n" \
                          " ========================\n" %(curr.getCurrencyType())
                last = curr.getCurrencyType()

            # noinspection PyUnresolvedReferences
            if curr.getCurrencyType() == CurrencyType.Type.SECURITY:

                # SECURITIES
                if lFix and not lSecurities: continue

                lSyncNeeded=False

                if VERBOSE:
                    output += "Checking security: %s\n" % curr

                if curr.getParameter("relative_to_currid",None) is not None and curr.getParameter("relative_to_currid",None) == baseCurr.getParameter("currid"):
                    myPrint("J", "@@ WARNING: %s relative_to_currid should only be None or NOT your base currency (currently %s)!" % (curr,curr.getParameter("relative_to_currid")))
                    output += "---\n@@ WARNING: %s relative_to_currid should only be None or NOT your base currency (currently %s)!\n----\n" % (curr,curr.getParameter("relative_to_currid"))
                    if lFix and lFixWarnings:
                        lSyncNeeded=True
                        curr.setParameter("relative_to_currid", None)
                        myPrint("J", "@@SECURITY FIX APPLIED@@")
                        output += "----\n@@SECURITY FIX APPLIED@@\n----\n"
                    else:
                        lWarning = True
                        iWarnings += 1

                if curr.getParameter("rrate", None) is None and curr.getDoubleParameter("rate", 0.0) > 0.0 \
                        and (curr.getParameter("relative_to_currid",None) is None or curr.getParameter("relative_to_currid",None) == baseCurr.getParameter("currid",None)):
                    newRate= 1.0 / Util.safeRate(CurrencyUtil.getUserRate(curr, baseCurr))  # Copied from the MD code.....
                    myPrint("J","@@ WARNING: %s Relative Rate ('rrate') is set to: %s (whereas 'rate' is currently %s). It should be %s\n" %(curr, curr.getParameter("rrate", None),curr.getParameter("rate"), newRate))
                    output += "---\n@@ WARNING: %s Relative Rate ('rrate') is set to: %s (whereas 'rate' is currently %s). It should be %s (inverted %s)\n---\n" %(curr, curr.getParameter("rrate", None),curr.getParameter("rate"), newRate, 1/newRate)
                    if lFix and lFixWarnings:
                        lSyncNeeded=True
                        curr.setRate(newRate, baseCurr)
                        myPrint("J", "@@SECURITY FIX APPLIED@@")
                        output += "----\n@@SECURITY FIX APPLIED@@\n----\n"
                    else:
                        lWarning = True
                        iWarnings  += 1

                if lFix and lSyncNeeded:
                    curr.syncItem()

                continue

            # CURRENCIES
            if lFix and not lCurrencies: continue

            output += "\nChecking currency: %s\n" % curr
            getRelative = curr.getParameter("relative_to_currid")
            if getRelative:
                getRelative = str(getRelative)
            else:
                getRelative = str(getRelative)+" (this is OK and means the Base Rate will be used)"
            output += "relative_to_currid: " + getRelative + "\n"
            if curr.getParameter("relative_to_currid") is not None:
                myPrint("J", "@@ WARNING: %s relative_to_currid should be set to None!" % curr)
                output += "----\n@@ WARNING: %s relative_to_currid should be set to None!\n----\n" % curr

                if lFix and lFixWarnings:
                    curr.setParameter("relative_to_currid", None)
                    curr.syncItem()
                    myPrint("J", "@@CURRENCY FIX APPLIED@@")
                    output += "----\n@@CURRENCY FIX APPLIED@@\n----\n"
                else:
                    lWarning = True
                    iWarnings += 1

            output += "Rate: %s (inverted: %s)\n" % (curr.getParameter("rate", None), 1 / float(curr.getParameter("rate", None)))

            if curr.getParameter("rrate", None) is not None:
                output += "Relative Rate: %s (inverted: %s)\n" % (curr.getParameter("rrate", None), 1 / float(curr.getParameter("rrate", None)))

            if not lFix and VERBOSE:
                output += "  details:\n"
                output += "\t" + "ID: " + str(curr.getID()) + "\n"
                output += "\t" + "Name: " + str(curr.getName()) + "\n"
                output += "\t" + "Ticker: " + str(curr.getTickerSymbol()) + "\n"
                output += "\t" + "Is Base: " + str(curr == baseCurr) + "\n"
                output += "\t" + "Curr_ID: " + str(curr.getIDString()) + "\n"
                output += "\t" + "Decimal Places: " + str(curr.getDecimalPlaces()) + "\n"
                output += "\t" + "Hide in UI: " + str(curr.getHideInUI()) + "\n"
                output += "\t" + "Effective Date: " + str(curr.getEffectiveDateInt()) + "\n"
                output += "\t" + "Prefix: " + str(curr.getPrefix()) + "\n"
                output += "\t" + "Suffix: " + str(curr.getSuffix()) + "\n"

                output += "  pricing history:\n"
                currSnapshots = curr.getSnapshots()
                if currSnapshots.size() > 0:
                    i = 0
                    for currSnapshot in reversed(currSnapshots):
                        i += 1
                        output += "  snapshot: %s (reversed: %s)\n" % (currSnapshot, currSnapshot.getRate())
                        if i > 5:
                            output += "  stopping after 5 price history records, but more does exist...\n"
                            break
                else:
                    if curr != baseCurr:
                        output += "  This currency has no historical prices? Is this correct?\n"
                    else:
                        output += "  This currency has no historical prices...\n"

        output += "-----------------------------------------------------------------\n"
        if lFix:
            fixRCurrencyCheck = None
            myPrint("B", ">> Currency errors / warning - FIXES APPLIED..")
            output += "\nRELEVANT FIXES APPLIED\n\n"
            output += "\nDISCLAIMER: I take no responsibility for the execution of this currency fix script\n"

            if lWarning:
                output += "\n@@@@ You still have %s Warning(s)..\n" % iWarnings

            statusLabel.setText(("@@ CURRENCY / SECURITY FIXES APPLIED (as per your parameters) - Please review diagnostic report for details!").ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            play_the_money_sound()
            myPopupInformationBox(toolbox_frame_,"RELEVANT FIXES APPLIED","FIX RELATIVE CURR/SECs",JOptionPane.WARNING_MESSAGE)

        else:
            if lNeedFixScript:
                fixRCurrencyCheck = 3
                myPrint("B", ">> Currency / Security errors detected - Possible use of FIX required..!?")
                output += " >> Currency / Security errors detected - Possible use of FIX required..!?\n"
                output += "\nERROR: You have Currency / Security errors..\n"
                output += "Please discuss details with support and potentially run the FIX Relative Currencies option\n"
                output += "DISCLAIMER: Always backup your data before running change scripts. I can take no responsibility for the execution of said script\n"
                statusLabel.setText(("ERROR: You have Currency / Security errors.. Please review diagnostic report!").ljust(800, " "))
                statusLabel.setForeground(Color.RED)
            elif lWarning:
                fixRCurrencyCheck = 2
                myPrint("B", "You have %s Warning(s).." % iWarnings)
                output += "You have %s Warning(s)..\n" % iWarnings
                output += "These are where your Currency records show a relative currency that's not None...; I believe this to be a data error!\n" \
                          "... or where Securities have an incorrect relative currency set..\n"\
                          "... or where a Security's 'rrate' (relative rate) is not set, or different to the 'rate' (rate)...\n"
                output += "If you are seeing currency problems, then discuss with support and potentially run the FIX Relative Currencies option\n"
                output += "This would address these issues...\n"
                output += "DISCLAIMER: Always backup your data before running change scripts. I can take no responsibility for the execution of this function\n"
                statusLabel.setText(("ERROR: You have Currency / Security warnings.. Please review diagnostic report!").ljust(800, " "))
                statusLabel.setForeground(Color.RED)
            else:
                fixRCurrencyCheck = 1
                myPrint("J", "All good, Currencies / Securities look clean! Congratulations!")
                output += "\nAll good, Currencies / Securities look clean! Congratulations!\n"
                statusLabel.setText(("All good, Currencies / Securities look clean! Congratulations!").ljust(800, " "))
                statusLabel.setForeground(DARK_GREEN)

        output += "\n<END>"

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

        return output

    class BackupButtonAction(AbstractAction):
        theString = ""

        def __init__(self, statusLabel, theQuestion):
            self.statusLabel = statusLabel
            self.theQuestion = theQuestion

        def actionPerformed(self, event):
            global toolbox_frame_, debug
            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

            if myPopupAskQuestion(toolbox_frame_,
                                      "PERFORM BACKUP",
                                  self.theQuestion,
                                  JOptionPane.YES_NO_OPTION,
                                  JOptionPane.WARNING_MESSAGE):


                myPrint("J", "User requested to perform Export Backup")
                moneydance_ui.saveToBackup(None)
                play_the_money_sound()

                self.statusLabel.setText(("Backup created as requested..").ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
            else:
                self.statusLabel.setText(("User declined to create backup..").ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)

            myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
            return

    def backup_custom_theme_file():

        # noinspection PyUnresolvedReferences
        themeFile = theme.Theme.customThemeFile

        newFileName = os.path.splitext(themeFile.getName())[0]+get_filename_addition()+os.path.splitext(themeFile.getName())[1]+"_$SAVED$"
        newFile = File(themeFile.getParent(), newFileName)

        try:
            IOUtils.copy(themeFile, newFile)
            myPrint("B", "Custom theme file: backup / copied to %s prior to deletion...."%newFileName)
            return True
        except:
            myPrint("B", "Error: Failed to backup/copy custom theme file prior to deletion....")
            dump_sys_error_to_md_console_and_errorlog()

        return False

    def backup_local_storage_settings( lSaveFirst=True ):

        if lSaveFirst:
            moneydance_data.getLocalStorage().save()  # Flush settings to disk before changes

        # I would rather have called LocalStorage() to get the filepath, but it doesn't give the path
        # NOTE  - This backup copy will be encrypted, so you can just put it back to ./safe/settings.
        localStorage_file = File(os.path.join(moneydance_data.getRootFolder().getAbsolutePath(),"safe","settings"))
        copy_localStorage_filename = os.path.join(moneydance_data.getRootFolder().getAbsolutePath(),"settings")

        try:
            newFileName = copy_localStorage_filename+get_filename_addition()+"_$SAVED$"
            newFile = File(newFileName)

            IOUtils.copy(localStorage_file, newFile)
            myPrint("B", "LocalStorage() ./safe/settings copied to %s prior to any changes...."%newFileName)
            return True

        except:
            myPrint("B","@@ ERROR - failed to copy LocalStorage() ./safe/settings prior to any changes!?")
            dump_sys_error_to_md_console_and_errorlog()

        return False

    def backup_config_dict( lSaveFirst=True ):

        if lSaveFirst:
            moneydance.savePreferences()  # Flush settings to disk before copy

        try:
            configFile = Common.getPreferencesFile()
            newFileName = os.path.splitext(configFile.getName())[0]+get_filename_addition()+os.path.splitext(configFile.getName())[1]+"_$SAVED$"
            newFile = File(configFile.getParent(), newFileName)

            IOUtils.copy(configFile, newFile)
            myPrint("B", "config.dict backup/copy made to %s prior to changes...."%newFileName)
            return True
        except:
            myPrint("B","@@ ERROR - failed to backup/copy config.dict prior to changes!?")
            dump_sys_error_to_md_console_and_errorlog()

        return False


    class CloseAction(AbstractAction):

        def __init__(self, theFrame):
            self.theFrame = theFrame

        def actionPerformed(self, event):                                                                           # noqa
            global debug
            myPrint("D","In ", inspect.currentframe().f_code.co_name, "()")

            self.theFrame.dispose()
            return


    def check_for_dropbox_folder():

        syncMethods = SyncFolderUtil.getAvailableFolderConfigurers(moneydance_ui, moneydance_ui.getCurrentAccounts())
        syncMethod = SyncFolderUtil.getConfigurerForFile(moneydance_ui, moneydance_ui.getCurrentAccounts(), syncMethods)

        dropboxOption = SyncFolderUtil.configurerForIDFromList("dropbox_folder", syncMethods)
        if (not dropboxOption) or syncMethod.getSyncFolder():
            return True

        userHomeProperty = System.getProperty("UserHome", System.getProperty("user.home", "."))
        baseFolder = File(userHomeProperty, "Dropbox")
        dropbox = File(baseFolder, ".moneydancesync")

        # If Dropbox folder does not exist then do nothing
        if not (baseFolder.exists() and baseFolder.isDirectory()):
            return True

        if dropbox.exists() and dropbox.isDirectory():
            return True

        return False

    def tell_me_if_dropbox_folder_exists():

        userHomeProperty = System.getProperty("UserHome", System.getProperty("user.home", "."))
        baseFolder = File(userHomeProperty, "Dropbox")
        dropbox = File(baseFolder, ".moneydancesync")

        # If Dropbox folder does not exist then do nothing
        if baseFolder.exists() and baseFolder.isDirectory() and dropbox.exists() and dropbox.isDirectory():
            return dropbox.getCanonicalPath()

        return False

    def about_this_script():
        global toolbox_frame_, debug, scriptExit

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        # noinspection PyUnresolvedReferences
        about_d = JDialog(toolbox_frame_, "About", Dialog.ModalityType.MODELESS)

        shortcut = Toolkit.getDefaultToolkit().getMenuShortcutKeyMaskEx()
        about_d.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_W, shortcut), "close-window")
        about_d.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_F4, shortcut), "close-window")
        about_d.getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0), "close-window")
        about_d.getRootPane().getActionMap().put("close-window", CloseAction(about_d))

        about_d.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE)  # The CloseAction() and WindowListener() will handle dispose() - else change back to DISPOSE_ON_CLOSE

        if (not Platform.isMac()):
            # moneydance_ui.getImages()
            about_d.setIconImage(MDImages.getImage(moneydance_ui.getMain().getSourceInformation().getIconResource()))

        aboutPanel=JPanel()
        aboutPanel.setLayout(FlowLayout(FlowLayout.LEFT))
        aboutPanel.setPreferredSize(Dimension(1070, 500))

        _label0 = JLabel(pad("Infinite Kind (Moneydance)", 800))
        _label0.setForeground(Color.BLUE)
        aboutPanel.add(_label0)

        _label1 = JLabel(pad("Co-Author: Stuart Beesley", 800))
        _label1.setForeground(Color.BLUE)
        aboutPanel.add(_label1)

        _label2 = JLabel(pad("StuWareSoftSystems (2020-2021)", 800))
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


    def terminate_script():
        global debug, toolbox_frame_, lGlobalErrorDetected

        myPrint("D","In ", inspect.currentframe().f_code.co_name, "()")

        # We now do this whenever a parameter changes to avoid all doing this at once when MD switches datasets
        # try:
        #     save_StuWareSoftSystems_parameters_to_file()
        # except:
        #     myPrint("B", "Error - failed to save parameters to pickle file...!")
        #     dump_sys_error_to_md_console_and_errorlog()
        #
        try:
            if not i_am_an_extension_so_run_headless: print(scriptExit)
        except:
            pass

        try:
            moneydance_ui.firstMainFrame.setStatus(">> Infinite Kind (co-authored by Stuart Beesley: StuWareSoftSystems) - Thanks for using Toolbox.......",0)
        except:
            pass  # If this fails, then MD is probably shutting down.......

        try:
            toolbox_frame_.dispose()    # NOTE - The windowClosed event should set .isActiveInMoneydance False and .removeAppEventListener()
        except:
            myPrint("B","Error. Final dispose failed....?")
            dump_sys_error_to_md_console_and_errorlog()

        # Cleanup any mess and left-overs
        destroyOldFrames(myModuleID)

        myPrint("B","Script/extension is terminating.....")

        return

    def confirm_backup_confirm_disclaimer(theFrame, theStatusLabel, theTitleToDisplay, theAction):

        if not myPopupAskQuestion(theFrame,
                                  theTitle=theTitleToDisplay,
                                  theQuestion=theAction,
                                  theOptionType=JOptionPane.YES_NO_OPTION,
                                  theMessageType=JOptionPane.ERROR_MESSAGE):
            theStatusLabel.setText(("'%s' User did not say yes to '%s' - no changes made" %(theTitleToDisplay, theAction)).ljust(800, " "))
            theStatusLabel.setForeground(Color.RED)
            myPrint("B","'%s' User did not say yes to '%s' - no changes made" %(theTitleToDisplay, theAction))
            myPopupInformationBox(theFrame,"User did not accept to proceed - no changes made...","NO UPDATE",JOptionPane.ERROR_MESSAGE)
            return False

        if not myPopupAskBackup(theFrame, "Would you like to perform a backup before %s" %(theTitleToDisplay)):
            theStatusLabel.setText(("'%s' - User chose to exit without the fix/update...."%(theTitleToDisplay)).ljust(800, " "))
            theStatusLabel.setForeground(Color.RED)
            myPrint("B","'%s' User aborted at the backup prompt to '%s' - no changes made" %(theTitleToDisplay, theAction))
            myPopupInformationBox(theFrame,"User aborted at the backup prompt - no changes made...","DISCLAIMER",JOptionPane.ERROR_MESSAGE)
            return False

        disclaimer = myPopupAskForInput(theFrame,
                                        theTitle=theTitleToDisplay,
                                        theFieldLabel="DISCLAIMER:",
                                        theFieldDescription="Are you really sure you want to '%s' Type 'IAGREE' to continue.." %(theAction),
                                        defaultValue="NO",
                                        isPassword=False,
                                        theMessageType=JOptionPane.ERROR_MESSAGE)

        if not disclaimer == 'IAGREE':
            theStatusLabel.setText(("'%s' - User declined the disclaimer - no changes made...." %(theTitleToDisplay)).ljust(800, " "))
            theStatusLabel.setForeground(Color.RED)
            myPrint("B","'%s' User did not say accept Disclaimer to '%s' - no changes made" %(theTitleToDisplay, theAction))
            myPopupInformationBox(theFrame,"User did not accept Disclaimer - no changes made...","DISCLAIMER",JOptionPane.ERROR_MESSAGE)
            return False

        myPrint("B","'%s' - User has been offered opportunity to create a backup and they accepted the DISCLAIMER on Action: %s - PROCEEDING" %(theTitleToDisplay, theAction))

        return True

    def clearOneServiceAuthCache(statusLabel):
        global toolbox_frame_, debug

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        authKeyPrefix = "_authentication."
        output = "VIEW ALL EXISTING AUTHENTICATION KEYS\n" \
                 " ====================================\n\n"
        LS = moneydance_ui.getCurrentAccounts().getBook().getLocalStorage()
        keys=sorted(LS.keys())
        for theKey in keys:
            value = LS.get(theKey)    # NOTE: .get loses the underlying type and thus becomes a string
            if not theKey.lower().startswith(authKeyPrefix): continue
            output+="%s %s\n" %(pad(theKey,40),value)
        output+="\n<END>"
        jif = QuickJFrame("VIEW ALL EXISTING AUTHENTICATION KEYS",output,lAlertLevel=2).show_the_frame()

        serviceList = moneydance.getCurrentAccountBook().getOnlineInfo().getAllServices()

        service = JOptionPane.showInputDialog(jif,
                                              "Select a service to delete",
                                              "CLEAR AUTHENTICATION FROM ONE SERVICE",
                                              JOptionPane.INFORMATION_MESSAGE,
                                              moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                              serviceList.toArray(),
                                              None)

        if not service:
            statusLabel.setText(("CLEAR AUTHENTICATION FROM ONE SERVICE - No Service was selected - no changes made..").ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            jif.dispose()
            return

        if not backup_local_storage_settings():
            myPrint("B", "'CLEAR AUTHENTICATION FROM ONE SERVICE': ERROR making backup of LocalStorage() ./safe/settings - no changes made!")
            statusLabel.setText(("'CLEAR AUTHENTICATION FROM ONE SERVICE': ERROR making backup of LocalStorage() ./safe/settings - no changes made!").ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            jif.dispose()
            return

        if confirm_backup_confirm_disclaimer(jif,statusLabel,"CLEAR AUTHENTICATION FROM ONE SERVICE","Clear Authentication Password(s) for service:%s?" %(service)):
            # noinspection PyUnresolvedReferences
            service.clearAuthenticationCache()
            LS = moneydance_ui.getCurrentAccounts().getBook().getLocalStorage()
            LS.save()
            play_the_money_sound()
            statusLabel.setText((("CLEAR AUTHENTICATION FROM ONE SERVICE - Password(s) for %s have been cleared" %(service)).ljust(800, " ")))
            statusLabel.setForeground(Color.RED)
            myPrint("B", "CLEAR AUTHENTICATION FROM ONE SERVICE - Password(s) for %s have been cleared" %(service))
            play_the_money_sound()
            myPopupInformationBox(jif,"All Password(s) for %s have been cleared" %(service),
                                  "CLEAR AUTHENTICATION FROM ONE SERVICE",JOptionPane.WARNING_MESSAGE)

        jif.dispose()

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
        return

    def clearAllServicesAuthCache(statusLabel):
        global toolbox_frame_, debug

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        authKeyPrefix = "_authentication."
        output = "VIEW ALL EXISTING AUTHENTICATION KEYS\n" \
                 " ====================================\n\n"
        LS = moneydance_ui.getCurrentAccounts().getBook().getLocalStorage()
        keys=sorted(LS.keys())
        for theKey in keys:
            value = LS.get(theKey)    # NOTE: .get loses the underlying type and thus becomes a string
            if not theKey.lower().startswith(authKeyPrefix): continue
            output+="%s %s\n" %(pad(theKey,40),value)
        output+="\n<END>"
        jif = QuickJFrame("VIEW ALL EXISTING AUTHENTICATION KEYS",output,lAlertLevel=2).show_the_frame()

        if not backup_local_storage_settings():
            myPrint("B", "'CLEAR ALL SERVICE(S)' AUTHENTICATION': ERROR making backup of LocalStorage() ./safe/settings - no changes made!")
            statusLabel.setText(("'CLEAR ALL SERVICE(S)' AUTHENTICATION': ERROR making backup of LocalStorage() ./safe/settings - no changes made!").ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            jif.dispose()
            return

        if confirm_backup_confirm_disclaimer(jif,statusLabel,"CLEAR ALL SERVICE(S)' AUTHENTICATION","Clear Authentication All Password(s) for **ALL** service(s)?"):

            moneydance_ui.getOnlineManager().clearAuthenticationCache()
            play_the_money_sound()
            statusLabel.setText((("CLEAR ALL SERVICE(S)' AUTHENTICATION - **ALL** Password(s) for ALL Services have been cleared" ).ljust(800, " ")))
            statusLabel.setForeground(Color.RED)
            myPrint("B", "CLEAR ALL SERVICE(S)' AUTHENTICATION - ALL Password(s) for ALL Services have been cleared!" )
            myPopupInformationBox(jif,"CLEAR ALL SERVICE(S)' AUTHENTICATION - ALL Password(s) for ALL Services have been cleared!",
                                  "CLEAR ALL AUTHENTICATION",JOptionPane.WARNING_MESSAGE)

        jif.dispose()

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
        return


    def check_OFX_USERID_Key_valid(test_str):
        pattern = r'[^a-zA-Z0-9-_.:]'
        if re.search(pattern, test_str):
            myPrint("DB","OFX UserID Key Invalid: %r" %(test_str))
            return False
        else:
            myPrint("DB","OFX UserID Key Valid: %r" %(test_str))
            return True

    def check_OFX_USERID_Data_valid(test_str):
        pattern = r'[^a-zA-Z0-9-_.]'
        if re.search(pattern, test_str):
            myPrint("DB","OFX UserID Data Invalid: %r" %(test_str))
            return False
        else:
            myPrint("DB","OFX UserID Data Valid: %r" %(test_str))
            return True



    def manualEditOfUserIDs(statusLabel):
        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        if moneydance_data is None: return

        userIDKeyPrefix="ofx.client_uid"

        root = moneydance_data.getRootAccount()

        _DELETEONE  = 0
        _DELETEALL  = 1
        _EDITONE    = 2
        _ADDONE     = 3

        what = [
            "Delete One OFX UserID record",
            "Delete All OFX UserID record(s)",
            "Edit One OFX UserID record (key and data)",
            "Add One OFX UserID record (key and data)"]

        while True:

            lDoIHaveAnyKeys=True

            output = "LIST OF OFX BANK USERIDs STORED ON THE ROOT ACCOUNT\n" \
                     "===================================================\n\n"
            userIDKeys=[]
            rootKeys=sorted(root.getParameterKeys())
            for userKey in rootKeys:
                if userKey.startswith(userIDKeyPrefix):
                    userIDKeys.append(userKey)
                    output+="Key: %s Data: %s\n" %(pad(userKey,40),root.getParameter(userKey, None))

            output+="\n<END>"

            if len(userIDKeys)<1:
                statusLabel.setText(("Sorry - You have no Bank OFX UserIDs stored on the Root Account").ljust(800, " "))
                statusLabel.setForeground(Color.RED)
                myPopupInformationBox(toolbox_frame_,"FYI - You have no Bank OFX UserIDs stored on the Root Account","OFX BANK UserIDs",JOptionPane.WARNING_MESSAGE)
                lDoIHaveAnyKeys=False

            jif=QuickJFrame("REVIEW OFX BANK USERIDs (stored on ROOT) BEFORE CHANGES",output).show_the_frame()

            if lDoIHaveAnyKeys:
                selectedWhat = JOptionPane.showInputDialog(jif,
                                                           "What you want to do?",
                                                           "OFX USERID MANAGEMENT",
                                                           JOptionPane.INFORMATION_MESSAGE,
                                                           moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                           what,
                                                           None)
            else:
                selectedWhat = JOptionPane.showInputDialog(jif,
                                                           "What you want to do?",
                                                           "OFX USERID MANAGEMENT",
                                                           JOptionPane.INFORMATION_MESSAGE,
                                                           moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                           [what[_ADDONE]],
                                                           None)

            if not selectedWhat:
                statusLabel.setText(("OFX USERID MANAGEMENT - No option was selected..").ljust(800, " "))
                statusLabel.setForeground(Color.RED)
                jif.dispose()
                return

            lEditOne = lDeleteOne = lDeleteAll = lAddOne = False

            if selectedWhat == what[_EDITONE]:      lEditOne=True
            elif selectedWhat == what[_DELETEONE]:  lDeleteOne=True
            elif selectedWhat == what[_DELETEALL]:  lDeleteAll=True
            elif selectedWhat == what[_ADDONE]:     lAddOne=True
            else:
                jif.dispose()
                continue

            do_what=""
            if lDeleteOne:  do_what="DELETE"
            if lEditOne:    do_what="EDIT"
            if lDeleteAll:  do_what="DELETE ALL"
            if lAddOne:     do_what="ADD ONE"

            selectedUserIDKey=None
            UserIDKeyValue=None

            if lDeleteOne or lEditOne:

                selectedUserIDKey = JOptionPane.showInputDialog(jif,
                                                             "Select a UserID to %s" %(do_what),
                                                             "OFX USERID MANAGEMENT",
                                                             JOptionPane.INFORMATION_MESSAGE,
                                                             moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                             userIDKeys,
                                                             None)
                if not selectedUserIDKey:
                    jif.dispose()
                    continue

                UserIDKeyValue = root.getParameter(selectedUserIDKey, None)

            chgKey=None
            chgValue=None
            if lEditOne:
                chgKey = myPopupAskForInput(jif,
                                              theTitle="OFX USERID MANAGEMENT",
                                              theFieldLabel="EDIT USERID PARAMETER KEY [optional]:",
                                              theFieldDescription="Carefully edit/change the key. (JUST ENTER TO KEEP THE SAME))",
                                              defaultValue=selectedUserIDKey,
                                              isPassword=False,
                                              theMessageType=JOptionPane.WARNING_MESSAGE)   # type: str

                if not chgKey or len(chgKey.strip()) <1:
                    myPopupInformationBox(jif,"ERROR - The edited key was not specified or blank!","OFX USERID MANAGEMENT",JOptionPane.ERROR_MESSAGE)
                    jif.dispose()
                    continue
                chgKey = chgKey.strip()
                if not chgKey.startswith(userIDKeyPrefix) or not check_OFX_USERID_Key_valid(chgKey) \
                        or (chgKey != selectedUserIDKey and root.getParameter(chgKey,None) is not None):
                    myPopupInformationBox(jif,"ERROR - The new key %s was invalid or must start with '%s'" %(chgKey,userIDKeyPrefix),"OFX USERID MANAGEMENT",JOptionPane.ERROR_MESSAGE)
                    jif.dispose()
                    continue

                chgValue = myPopupAskForInput(jif,
                                              theTitle="OFX USERID MANAGEMENT",
                                              theFieldLabel="EDIT USERID PARAMETER VALUE:",
                                              theFieldDescription="Carefully edit/change the data. NOTE: There will be little validation...",
                                              defaultValue=UserIDKeyValue,
                                              isPassword=False,
                                              theMessageType=JOptionPane.WARNING_MESSAGE)    # type: str
                if not chgValue or len(chgValue.strip()) <1:
                    jif.dispose()
                    continue
                chgValue = chgValue.strip()
                if not check_OFX_USERID_Key_valid(chgValue):
                    myPopupInformationBox(jif,"ERROR - The changed key data %s was invalid" %(chgValue),"OFX USERID MANAGEMENT",JOptionPane.ERROR_MESSAGE)
                    jif.dispose()
                    continue

            if lAddOne:
                chgKey = myPopupAskForInput(jif,
                                            theTitle="OFX USERID MANAGEMENT",
                                            theFieldLabel="ADD NEW USERID PARAMETER KEY:",
                                            theFieldDescription="Carefully complete the new key (must start with '%s')" %(userIDKeyPrefix),
                                            defaultValue=userIDKeyPrefix,
                                            isPassword=False,
                                            theMessageType=JOptionPane.WARNING_MESSAGE)    # type: str

                if not chgKey or len(chgKey.strip()) <1:
                    myPopupInformationBox(jif,"ERROR - The new key was not specified or blank!","OFX USERID MANAGEMENT",JOptionPane.ERROR_MESSAGE)
                    jif.dispose()
                    continue
                chgKey = chgKey.strip()
                if not chgKey.startswith(userIDKeyPrefix) or not check_OFX_USERID_Key_valid(chgKey) or root.getParameter(chgKey,None) is not None:
                    myPopupInformationBox(jif,"ERROR - The new key %s was invalid or must start with '%s'" %(chgKey,userIDKeyPrefix),"OFX USERID MANAGEMENT",JOptionPane.ERROR_MESSAGE)
                    jif.dispose()
                    continue

                chgValue = myPopupAskForInput(jif,
                                              theTitle="OFX USERID MANAGEMENT",
                                              theFieldLabel="ADD NEW USERID PARAMETER VALUE:",
                                              theFieldDescription="Carefully enter the new data. NOTE: There will be little validation...",
                                              defaultValue=UserIDKeyValue,
                                              isPassword=False,
                                              theMessageType=JOptionPane.WARNING_MESSAGE)   # type: str
                if not chgValue or len(chgValue.strip()) <1:
                    jif.dispose()
                    continue
                chgValue = chgValue.strip()
                if not check_OFX_USERID_Key_valid(chgValue):
                    myPopupInformationBox(jif,"ERROR - The new key data %s was invalid" %(chgValue),"OFX USERID MANAGEMENT",JOptionPane.ERROR_MESSAGE)
                    jif.dispose()
                    continue

            if not confirm_backup_confirm_disclaimer(jif,statusLabel, "OFX USERID MANAGEMENT","OFX USERIDs %s?" %(do_what)):
                jif.dispose()
                return

            if lEditOne:
                if chgKey != selectedUserIDKey:
                    myPrint("B","setting new key %s to %s" %(chgKey,chgValue))
                    myPrint("DB", "NEW pre %s %s" %(chgKey,root.getParameter(chgKey)))
                    root.setParameter(chgKey, chgValue)
                    root.syncItem()
                    myPrint("DB", "NEW post %s %s" %(chgKey,root.getParameter(chgKey)))

                    myPrint("B","setting old key %s to None" %(selectedUserIDKey))
                    myPrint("DB", "OLD pre %s %s" %(selectedUserIDKey,root.getParameter(selectedUserIDKey)))
                    root.setParameter(selectedUserIDKey,None)
                    root.syncItem()
                    myPrint("DB", "OLD post %s %s" %(selectedUserIDKey,root.getParameter(selectedUserIDKey)))
                else:
                    myPrint("DB", "KEYSAME pre %s %s" %(selectedUserIDKey,root.getParameter(selectedUserIDKey)))
                    myPrint("B","setting %s to %s" %(selectedUserIDKey,chgValue))
                    root.setParameter(selectedUserIDKey, chgValue)
                    root.syncItem()
                    myPrint("DB", "KEYSAME post %s %s" %(selectedUserIDKey,root.getParameter(selectedUserIDKey)))
                myPrint("B", "OFX UserID Record key %s now %s changed from %s to %s" %(selectedUserIDKey,chgKey,UserIDKeyValue,chgValue))
                statusLabel.setText(("OFX UserID Record key %s now %s changed from %s to %s" %(selectedUserIDKey,chgKey,UserIDKeyValue,chgValue)).ljust(800, " "))
                statusLabel.setForeground(Color.RED)

            if lAddOne:
                root.setParameter(chgKey,chgValue)
                root.syncItem()
                myPrint("B", "OFX new UserID parameter %s CREATED with data: %s" %(chgKey,chgValue))
                statusLabel.setText(("OFX new UserID parameter %s CREATED with data: %s" %(chgKey,chgValue)).ljust(800, " "))
                statusLabel.setForeground(Color.RED)

            if lDeleteOne:
                root.setParameter(selectedUserIDKey, None)
                root.syncItem()
                myPrint("B", "OFX UserID parameter %s DELETED (was: %s)" %(selectedUserIDKey,UserIDKeyValue))
                statusLabel.setText(("OFX UserID parameter %s DELETED (was: %s)" %(selectedUserIDKey,UserIDKeyValue)).ljust(800, " "))
                statusLabel.setForeground(Color.RED)

            if lDeleteAll:
                for keyToDelete in userIDKeys:
                    root.setParameter(keyToDelete, None)
                    root.syncItem()
                    myPrint("B", "DELETED OFX UserID Parameter %s from ROOT!" %(keyToDelete))
                statusLabel.setText(("ALL OFX UserID records DELETED from ROOT").ljust(800, " "))
                statusLabel.setForeground(Color.RED)

            del userIDKeys
            play_the_money_sound()
            myPopupInformationBox(jif,"Your %s changes have been made and saved!" %(do_what),"OFX USERID MANAGEMENT",JOptionPane.WARNING_MESSAGE)
            jif.dispose()
            continue

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
        return

    class StoreAccountList():
        def __init__(self, obj):
            if isinstance(obj,Account):
                self.obj = obj                          # type: Account
            else:
                self.obj = None

        def __str__(self):
            if self.obj is None:
                return "Invalid Acct Obj or None"
            return "%s : %s" %(self.obj.getAccountType(),self.obj.getFullAccountName())

        def __repr__(self):
            if self.obj is None:
                return "Invalid Acct Obj or None"
            return "%s : %s" %(self.obj.getAccountType(),self.obj.getFullAccountName())

    class StoreTheOnlineTxnList():
        def __init__(self, obj, acct):
            self.obj = obj                          # type: OnlineTxnList
            self.acct = acct                        # type: Account
            if self.obj is not None:
                self.txnCount = obj.getTxnCount()
            else:
                self.txnCount = 0

        def __str__(self):
            return "OnlineTxnList Obj on Acct %s (holding %s Txns)" %(self.acct,self.txnCount)

        def __repr__(self):
            return "OnlineTxnList Obj on Acct %s (holding %s Txns)" %(self.acct,self.txnCount)

    class StoreTheOnlinePayeeList():
        def __init__(self, obj, acct):
            self.obj = obj                          # type: OnlinePayeeList
            self.acct = acct                        # type: Account
            if self.obj is not None:
                self.payeeCount = obj.getPayeeCount()
            else:
                self.payeeCount = 0

        def __str__(self):
            return "OnlinePayeeList Obj on Acct %s (holding %s Payees)" %(self.acct,self.payeeCount)

        def __repr__(self):
            return "OnlinePayeeList Obj on Acct %s (holding %s Payees)" %(self.acct,self.payeeCount)

    class StoreTheOnlinePaymentList():
        def __init__(self, obj, acct):
            self.obj = obj                          # type: OnlinePaymentList
            self.acct = acct                        # type: Account
            if self.obj is not None:
                self.paymentCount = obj.getPaymentCount()
            else:
                self.paymentCount = 0

        def __str__(self):
            return "OnlinePaymentList Obj on Acct %s (holding %s Payments)" %(self.acct,self.paymentCount)

        def __repr__(self):
            return "OnlinePaymentList Obj on Acct %s (holding %s Payments)" %(self.acct,self.paymentCount)

    def OFX_update_OFXLastTxnUpdate(statusLabel):
        global lAdvancedMode, lHackerMode

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        if moneydance_data is None: return
        if not (lAdvancedMode): return

        accountsListForOlTxns = AccountUtil.allMatchesForSearch(moneydance_data, MyAcctFilter(15))
        accountsListForOlTxns = sorted(accountsListForOlTxns, key=lambda sort_x: (sort_x.getFullAccountName().upper()))

        selectedAcct = JOptionPane.showInputDialog(toolbox_frame_,
                                                   "Select the Acct to Hack the OFXLastTxnUpdate date field:",
                                                   "OFX OFXLastTxnUpdate - Select ACCOUNT",
                                                   JOptionPane.INFORMATION_MESSAGE,
                                                   moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                   accountsListForOlTxns,
                                                   None)
        if not selectedAcct:
            statusLabel.setText(("No Account was selected..").ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            return

        theOnlineTxnRecord = StoreTheOnlineTxnList(MyGetDownloadedTxns(selectedAcct),selectedAcct)       # Use my version to prevent creation of default record(s)
        if theOnlineTxnRecord is None or theOnlineTxnRecord.obj is None:
            statusLabel.setText(("No OnlineTxnList record found... Exiting..").ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            return

        theCurrentDate = theOnlineTxnRecord.obj.getOFXLastTxnUpdate()

        if theCurrentDate > 0:
            theCurrentDatePretty = get_time_stamp_as_nice_text(theCurrentDate)
        else:
            theCurrentDatePretty = "NOT SET"

        myPopupInformationBox(toolbox_frame_,"OFXLastTxnUpdate is currently: %s (which means: %s)" %(theCurrentDate, theCurrentDatePretty))

        labelUpdateDate = JLabel("Select the new OFXLastTxnUpdate download Date (enter as yyyy/mm/dd):")
        user_selectDateStart = JDateField(CustomDateFormat("ymd"),15)   # Use MD API function (not std Python)
        user_selectDateStart.setDateInt(DateUtil.getStrippedDateInt())

        datePanel = JPanel(GridLayout(0, 1))
        datePanel.add(labelUpdateDate)
        datePanel.add(user_selectDateStart)

        options = ["Cancel", "OK"]

        while True:
            userAction = JOptionPane.showOptionDialog(toolbox_frame_,
                                                      datePanel,
                                                      "Select new Date for the OFXLastTxnUpdate field:",
                                                      JOptionPane.OK_CANCEL_OPTION,
                                                      JOptionPane.QUESTION_MESSAGE,
                                                      None,
                                                      options,
                                                      options[0])

            if userAction != 1:
                statusLabel.setText(("OFX: User cancelled entering a new OFXLastTxnUpdate date - exiting").ljust(800, " "))
                statusLabel.setForeground(Color.RED)
                return

            if user_selectDateStart.getDateInt() < 20150101 or user_selectDateStart.getDateInt() > DateUtil.getStrippedDateInt():
                statusLabel.setText(("OFX: User cancelled entering an invalid OFXLastTxnUpdate date...").ljust(800, " "))
                statusLabel.setForeground(Color.RED)
                user_selectDateStart.setDateInt(DateUtil.getStrippedDateInt())
                user_selectDateStart.setForeground(Color.RED)
                continue

            break   # Valid date

        if not confirm_backup_confirm_disclaimer(toolbox_frame_,statusLabel, "OFX UPDATE OFXLastTxnUpdate","Update the OFXLastTxnUpdate field to %s?" %(user_selectDateStart.getDateInt())):
            return

        newDate = DateUtil.convertIntDateToLong(user_selectDateStart.getDateInt()).getTime()

        theOnlineTxnRecord.obj.setOFXLastTxnUpdate(newDate)
        theOnlineTxnRecord.obj.syncItem()

        play_the_money_sound()
        statusLabel.setText(("OFX HACK OFXLastTxnUpdate date for acct: %s successfully set to: %s (%s)" %(selectedAcct,newDate,user_selectDateStart.getDateInt())).ljust(800, " "))
        statusLabel.setForeground(Color.RED)
        myPrint("B", "OFX HACK OFXLastTxnUpdate date for acct: %s successfully set to: %s (%s)" %(selectedAcct,newDate,user_selectDateStart.getDateInt()))
        myPopupInformationBox(toolbox_frame_,"OFX HACK OFXLastTxnUpdate date for acct: %s successfully set to: %s (%s)" %(selectedAcct,newDate,user_selectDateStart.getDateInt()),"OFX UPDATE OFXLastTxnUpdate",JOptionPane.WARNING_MESSAGE)

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

    def OFX_delete_ALL_saved_online_txns(statusLabel):
        global lAdvancedMode

        # delete_intermediate_downloaded_transaction_caches.py
        # delete_orphaned_downloaded_txn_lists.py

        # CREATE TEST DATA
        # allAccounts = AccountUtil.allMatchesForSearch(moneydance_data, AcctFilter.NON_CATEGORY_FILTER)
        # for acct in allAccounts:
        #     if "TEST"  != acct.getFullAccountName().upper() and "TEST2"  != acct.getFullAccountName().upper(): continue
        #     print "found: %s" %(acct)
        #     olTxns = acct.getDownloadedTxns()  # Note - this actually creates a new OnlineTxnList object if it didn't exist
        #     for i in range(0,10):
        #         olTxn = olTxns.newTxn()
        #         olTxn.setFIID("qif")
        #         olTxn.setName("Desc1" +str(i))
        #         olTxn.setDatePostedInt(	20200115+i )
        #         olTxn.setAmount( 9999+i )
        #         olTxn.setAllowDuplicateIDs(True)
        #         olTxns.addNewTxn(olTxn)
        #     olTxns.syncItem()
        #     print olTxns.getSyncInfo()
        # END CREATE TEST DATA

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        if moneydance_data is None: return
        if not (lAdvancedMode): return

        # quick check first...
        olTxnLists = moneydance_data.getItemsWithType("oltxns")
        lAny=False
        for txnList in olTxnLists:
            if txnList.getTxnCount() > 0:
                lAny=True
                break

        if not lAny and not myPopupAskQuestion(toolbox_frame_,"OFX PURGE OnlineTxnList OBJECTS","You don't seem to have any cached Online Txns. Proceed anyway (with general cleanup)?",theMessageType=JOptionPane.WARNING_MESSAGE):
            statusLabel.setText(("OFX PURGE OnlineTxnList OBJECTS. You have no cached Txns - no changes made...." ).ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            myPopupInformationBox(toolbox_frame_,"OFX PURGE OnlineTxnList OBJECTS. You have no cached Txns - no changes made....",theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        if not confirm_backup_confirm_disclaimer(toolbox_frame_,statusLabel, "OFX PURGE OnlineTxnList OBJECTS","Purge/Clean all Cached OnlineTxnList Txns (very safe to run)?"):
            return

        myPrint("B","Purging / cleaning all OnlineTxnList Cached txns.....")

        allAccounts = AccountUtil.allMatchesForSearch(moneydance_data, AcctFilter.NON_CATEGORY_FILTER)

        output = "PURGE/CLEAN ALL CACHED OnlineTxnList TXN RECORDS\n" \
                 " ===============================================\n\n"

        output += (" Found %s accounts and %s OnlineTxnList objects\n" % (len(allAccounts), len(olTxnLists)))
        shouldSaveTrunk = False

        # delete all online transactions from all downloaded-transaction-list objects,
        # which includes lists that are no longer associated with accounts
        for txnList in olTxnLists:
            output+=("OnlineTxnList %s    with    %s cached txns\n" % (pad(txnList.getUUID(),50), rpad(txnList.getTxnCount(),12)))
            if txnList.getTxnCount() > 0:
                myPrint("J", "OnlineTxnList %s - DELETING %s cached txns" % (pad(txnList.getUUID(),50), rpad(txnList.getTxnCount(),12)))
                shouldSaveTrunk = True
                output+=("   >> DELETING Cached Txns....\n")
                while txnList.getTxnCount() > 0:
                    txnList.removeTxn(txnList.getTxnCount() - 1)
                txnList.syncItem()
                output+=("   OnlineTxnList %s now has %s cached txns\n" % (pad(txnList.getUUID(),50), rpad(txnList.getTxnCount(),12)))

        output += "\n--------\n\n"

        for acct in allAccounts:
            olTxns = acct.getDownloadedTxns()  # Note - this actually creates a new OnlineTxnList object if it didn't exist
            olTxnsIdx = olTxnLists.indexOf(olTxns)
            if olTxnsIdx >= 0:
                if olTxns.getTxnCount() > 0:    # Note - I think this never finds any, as it will have been caught in the loop above....
                    shouldSaveTrunk = True
                    output+=("Found OnlineTxnList %s at index %s for account %s - DELETING %s cached txns\n"
                          % (pad(olTxns.getUUID(),50), rpad(olTxnsIdx,10), pad(acct.getAccountName(),30), olTxns.getTxnCount()))
                    myPrint("J", "Found OnlineTxnList %s at index %s for account %s - DELETING %s cached txns"
                            % (pad(olTxns.getUUID(),50), rpad(olTxnsIdx,10), pad(acct.getAccountName(),30), olTxns.getTxnCount()))
                    while olTxns.getTxnCount() > 0:
                        olTxns.removeTxn(olTxns.getTxnCount() - 1)
                    olTxns.syncItem()
                    output+=("   OnlineTxnList %s                        >now has %s cached txns\n" % (pad(olTxns.getUUID(),50), rpad(olTxns.getTxnCount(),12)))
                olTxnLists.remove(olTxns)  # This check is OK though.....
            # else:
            #     output+=("@@ OnlineTxnList record NOT FOUND (orphaned), containing %s cached txns\n" % (rpad(olTxns.getTxnCount(),12)))

        output += "\n--------\n\n"

        output+=("Remaining/orphan OnlineTxnList objects to delete:\n")

        for txnList in olTxnLists:
            output+=(">> DELETING ORPHAN >> OnlineTxnList %s with %s cached txns\n" % (pad(txnList.getUUID(),50), rpad(txnList.getTxnCount(),12)))
            myPrint("J", ">> DELETING ORPHAN >> OnlineTxnList %s with %s cached txns" % (pad(txnList.getUUID(),50), rpad(txnList.getTxnCount(),12)))
            txnList.deleteItem()
            shouldSaveTrunk = True

        output += "\n--------\n\n"

        moneydance_data.logRemovedItems(olTxnLists)
        if shouldSaveTrunk:
            myPrint("J","Purge/Clean ALL OnlineTxnList objects - Saving Trunk file now....")
            output+=("SAVING TRUNK FILE...\n")
            moneydance_data.saveTrunkFile()
        else:
            myPrint("J","Purge/Clean ALL OnlineTxnList objects - NO CHANGES MADE....")
            output+=("Purge/Clean ALL OnlineTxnList objects - NO CHANGES MADE....\n")

        output+="\n<END>"

        myPrint("P",output)

        jif = QuickJFrame("OFX PURGE ALL OnlineTxnList OBJECTS",output).show_the_frame()

        play_the_money_sound()
        statusLabel.setText(("OFX: Purge / Clean ALL OnlineTxnList Objects cached Txns completed...").ljust(800, " "))
        statusLabel.setForeground(Color.RED)
        myPrint("B", "OFX: Purge / Clean ALL OnlineTxnList Objects cached Txns completed...")
        myPopupInformationBox(jif,"OFX: ALL OnlineTxnList Objects cached Txns purged/cleaned...","OFX PURGE ALL OnlineTxnList",JOptionPane.ERROR_MESSAGE)

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

    def OFX_delete_saved_online_txns(statusLabel):
        global lAdvancedMode, lHackerMode

        # delete_intermediate_downloaded_transaction_caches.py
        # delete_orphaned_downloaded_txn_lists.py

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        if moneydance_data is None: return
        if not (lAdvancedMode): return

        accountsListForOlTxns = AccountUtil.allMatchesForSearch(moneydance_data, MyAcctFilter(18))
        accountsListForOlTxns = sorted(accountsListForOlTxns, key=lambda sort_x: (sort_x.getFullAccountName().upper()))

        selectedAcct = JOptionPane.showInputDialog(toolbox_frame_,
                                                   "Select the Acct to Hack the Online Txn List record:",
                                                   "Select ACCOUNT",
                                                   JOptionPane.INFORMATION_MESSAGE,
                                                   moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                   accountsListForOlTxns,
                                                   None)
        if not selectedAcct:
            statusLabel.setText(("No Account was selected..").ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            return

        theOnlineTxnRecord = StoreTheOnlineTxnList(MyGetDownloadedTxns(selectedAcct),selectedAcct)       # Use my version to prevent creation of default record(s)
        if theOnlineTxnRecord is None or theOnlineTxnRecord.obj is None:
            statusLabel.setText(("No OnlineTxnList record found... Exiting..").ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            return

        saveTxnCount = theOnlineTxnRecord.txnCount

        while True:
            _options=["HACK: DELETE All %s Txns stored on this record" %(saveTxnCount),
                      "HACK: DELETE the whole OnlineTxnList record"]

            selectedOption = JOptionPane.showInputDialog(toolbox_frame_,
                                                         "What type of Hack to OnlineTxnList record do you want to make?",
                                                         "OFX Hack OnlineTxns",
                                                         JOptionPane.WARNING_MESSAGE,
                                                         None,
                                                         _options,
                                                         None)

            if not selectedOption:
                statusLabel.setText(("No Hack for OnlineTxnList record selected - exiting..").ljust(800, " "))
                statusLabel.setForeground(Color.RED)
                return

            lDeleteAllTxns  = (_options.index(selectedOption) == 0)
            lDeleteRecord   = (_options.index(selectedOption) == 1)

            if lDeleteAllTxns and saveTxnCount<1: continue

            break

        do_what=""
        if lDeleteAllTxns: do_what="Delete all %s stored Txns within the record" %(saveTxnCount)
        if lDeleteRecord:  do_what="Delete the whole OnlineTxnList record"

        if not confirm_backup_confirm_disclaimer(toolbox_frame_,statusLabel, "OFX DELETE HACK OnlineTxnList","%s?" %(do_what)):
            return

        if lDeleteRecord:
            theOnlineTxnRecord.obj.deleteItem()
            play_the_money_sound()
            statusLabel.setText(("OFX HACK OnlineTxnList whole record for acct: %s successfully deleted: " %(selectedAcct)).ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            myPrint("B", "OFX HACK OnlineTxnList whole record for acct: %s successfully deleted: " %(selectedAcct))
            myPopupInformationBox(toolbox_frame_,"OnlineTxnList record for acct: %s DELETED" %(selectedAcct),"OFX DELETE HACK OnlineTxnList",JOptionPane.ERROR_MESSAGE)

        elif lDeleteAllTxns:

            while theOnlineTxnRecord.obj.getTxnCount() > 0:
                theOnlineTxnRecord.obj.removeTxn(theOnlineTxnRecord.obj.getTxnCount() - 1)
            theOnlineTxnRecord.obj.syncItem()

            # for i in reversed(range(0,saveTxnCount)):
            #     theOnlineTxnRecord.obj.removeTxn(i)
            # theOnlineTxnRecord.obj.syncItem()
            #
            play_the_money_sound()
            statusLabel.setText(("OFX HACK OnlineTxnList Record for acct: %s: %s Txns deleted" %(selectedAcct, saveTxnCount)).ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            myPrint("B", "OFX HACK OnlineTxnList Record for acct: %s: %s Txns deleted" %(selectedAcct, saveTxnCount))
            myPopupInformationBox(toolbox_frame_,"OnlineTxnList acct: %s: %s Txns deleted" %(selectedAcct, saveTxnCount),"OFX DELETE HACK OnlineTxnList Txns",JOptionPane.ERROR_MESSAGE)

        del theOnlineTxnRecord

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

    def OFX_authentication_management(statusLabel):
        global lAdvancedMode, lHackerMode

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        if moneydance_data is None: return

        if not (isUserEncryptionPassphraseSet()
                and moneydance_ui.getCurrentAccounts().getBook().getLocalStorage().getBoolean("store_passwords", False)):
            myPopupInformationBox(toolbox_frame_,"WARNING: Your system is not setup to cache/store Authentication details. I suggest you exit","Manage OFX Authentication",JOptionPane.ERROR_MESSAGE)

        user_clearOneServiceAuthCache =         JRadioButton("Clear the Authentication Cache (Passwords) for One Service / Bank Profile", False)
        user_clearAllServicesAuthCache =        JRadioButton("Clear ALL Authentication Cache (Passwords)", False)

        user_manualEditOfUserIDs =              JRadioButton("Manual Edit of Stored UserIDs (Only in ADV+Hacker mode)", False)
        user_manualEditOfUserIDs.setEnabled(lHackerMode)
        user_manualEditOfUserIDs.setForeground(Color.RED)

        userFilters = JPanel(GridLayout(0, 1))

        bg = ButtonGroup()
        bg.add(user_clearOneServiceAuthCache)
        bg.add(user_clearAllServicesAuthCache)
        bg.add(user_manualEditOfUserIDs)
        bg.clearSelection()

        userFilters.add(user_clearOneServiceAuthCache)
        userFilters.add(user_clearAllServicesAuthCache)
        userFilters.add(user_manualEditOfUserIDs)

        while True:
            options = ["EXIT", "PROCEED"]
            userAction = (JOptionPane.showOptionDialog(toolbox_frame_,
                                                       userFilters,
                                                       "Online Banking (OFX) AUTHENTICATION MANAGEMENT",
                                                       JOptionPane.OK_CANCEL_OPTION,
                                                       JOptionPane.QUESTION_MESSAGE,
                                                       moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                       options, options[0]))

            if userAction != 1:
                statusLabel.setText(("Online Banking (OFX) AUTHENTICATION MANAGEMENT - No changes made.....").ljust(800, " "))
                statusLabel.setForeground(Color.BLUE)
                return

            if user_clearOneServiceAuthCache.isSelected():
                clearOneServiceAuthCache(statusLabel)

            if user_clearAllServicesAuthCache.isSelected():
                clearAllServicesAuthCache(statusLabel)

            if user_manualEditOfUserIDs.isSelected():
                manualEditOfUserIDs(statusLabel)

            continue

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

    def OFX_cookie_management(statusLabel):
        global lAdvancedMode, lHackerMode

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        if not lAdvancedMode or not lHackerMode: return

        cookieKey="ofxcookies"

        LS = moneydance_ui.getCurrentAccounts().getBook().getLocalStorage()

        _EDITONE = 0
        _DELETEONE = 1
        _DELETEALL = 2

        what = [
            "Edit One OFX Cookie's data",
            "Delete One OFX Cookie",
            "Delete All OFX Cookies"]

        while True:

            allCookieStrings = LS.getStringList(cookieKey)

            # LS = moneydance_ui.getCurrentAccounts().getBook().getLocalStorage()
            # LS.put("ofxcookies.0","CBDIdleTimer=1585100844282|false|13|15; path=%2F; domain=google.com")
            # LS.put("ofxcookies.1","HNWPRD=A11; path=%2F; domain=google.com")
            # LS.put("ofxcookies.2","ADRUM_BTs=R:0|s:p; Sun, 10-Jan-2021 20:34:19 MST; path=%2F; domain=vesnc.billy.com")
            # LS.put("ofxcookies.3","ADRUM_BT1=R:0|i:52128|e:20; Tue, 12-Jan-2021 16:24:22 MST; path=%2F; domain=vesnc.apple.com")

            _i = 0
            msgStr=""
            for _i in range(0, len(allCookieStrings)):
                msgStr+="%s\n" %(allCookieStrings.get(_i))
                # print MDCookie.loadFromStorage(allCookieStrings.get(_i))
                _i+=1

            MyPopUpDialogBox(toolbox_frame_,
                             theStatus="Your current cookies are:",
                             theMessage=msgStr,
                             theWidth=300,
                             theTitle="OFX COOKIE MANAGEMENT",
                             OKButtonText="CONTINUE").go()

            selectedWhat = JOptionPane.showInputDialog(toolbox_frame_,
                                                       "What you want to do?",
                                                       "OFX COOKIE MANAGEMENT",
                                                       JOptionPane.INFORMATION_MESSAGE,
                                                       moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                       what,
                                                       None)
            if not selectedWhat:
                statusLabel.setText(("No data type was selected to Geek out on..").ljust(800, " "))
                statusLabel.setForeground(Color.RED)
                return

            lEditOne = lDeleteOne = lDeleteAll = False

            if selectedWhat == what[_EDITONE]: lEditOne=True
            elif selectedWhat == what[_DELETEONE]: lDeleteOne=True
            elif selectedWhat == what[_DELETEALL]: lDeleteAll=True
            else: continue

            do_what=""
            if lDeleteOne: do_what="DELETE"
            if lEditOne: do_what="EDIT"
            if lDeleteAll: do_what="DELETE ALL"

            selectedCookie=None
            selectedCookieIndex=None

            if lDeleteOne or lEditOne:

                selectedCookie = JOptionPane.showInputDialog(toolbox_frame_,
                                                             "Select a Cookie to %s" %(do_what),
                                                             "OFX COOKIE MANAGEMENT",
                                                             JOptionPane.INFORMATION_MESSAGE,
                                                             moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                             allCookieStrings,
                                                             None)
                if not selectedCookie: continue
                selectedCookieIndex=allCookieStrings.indexOf(selectedCookie)

            chgValue=None
            if lEditOne:
                chgValue = myPopupAskForInput(toolbox_frame_,
                                              theTitle="OFX COOKIE MANAGEMENT",
                                              theFieldLabel="EDIT COOKIE VALUE:",
                                              theFieldDescription="Carefully edit/change the data. NOTE: There will be no validation...",
                                              defaultValue=selectedCookie,
                                              isPassword=False,
                                              theMessageType=JOptionPane.WARNING_MESSAGE)
                if not chgValue or len(chgValue.strip()) <1 or chgValue == selectedCookie: continue
                chgValue = chgValue.strip()

            if not confirm_backup_confirm_disclaimer(toolbox_frame_,statusLabel, "OFX BANK MANAGEMENT","OFX COOKIES %s?" %(do_what)):
                continue

            if not backup_local_storage_settings():
                myPrint("B", "'OFX COOKIE MANAGEMENT': ERROR making backup of LocalStorage() ./safe/settings - no changes made!")
                statusLabel.setText(("'OFX COOKIE MANAGEMENT': ERROR making backup of LocalStorage() ./safe/settings - no changes made!").ljust(800, " "))
                statusLabel.setForeground(Color.RED)
                return

            if lEditOne:
                allCookieStrings[selectedCookieIndex] = chgValue
                myPrint("B", "OFX Cookie %s changed from %s to %s" %(selectedCookieIndex+1,selectedCookie,chgValue))
                statusLabel.setText(("OFX Cookie %s changed from %s to %s" %(selectedCookieIndex+1,selectedCookie,chgValue)).ljust(800, " "))
                statusLabel.setForeground(Color.RED)

            if lDeleteOne:
                allCookieStrings.remove(selectedCookieIndex)
                myPrint("B", "OFX Cookie %s DELETED (was: %s)" %(selectedCookieIndex+1,selectedCookie))
                statusLabel.setText(("OFX Cookie %s DELETED (was: %s)" %(selectedCookieIndex+1,selectedCookie)).ljust(800, " "))
                statusLabel.setForeground(Color.RED)

            if lDeleteAll:
                allCookieStrings.clear()
                myPrint("B", "ALL OFX Cookies DELETED!" )
                statusLabel.setText(("ALL OFX Cookies DELETED").ljust(800, " "))
                statusLabel.setForeground(Color.RED)

            myPrint("B","OFX Bank Management: Writing all Cookies back to Local Storage (after: %s)...." %(do_what))
            LS.put(cookieKey, allCookieStrings)
            LS.save()
            myPopupInformationBox(toolbox_frame_,"Your %s changes have been made and saved!" %(do_what),"OFX BANK MANAGEMENT",JOptionPane.WARNING_MESSAGE)
            continue

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
        return


    def OFXDEBUGToggle(statusLabel):
        global toolbox_frame_, debug, DARK_GREEN, lCopyAllToClipBoard_TB
        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        key = "ofx.debug.console"
        props_ofx_debug = System.getProperty(key, None)

        toggleText = "ON"
        if (props_ofx_debug is not None and props_ofx_debug!="false"):
            toggleText = "OFF"

        ask = MyPopUpDialogBox(toolbox_frame_,"OFX DEBUG CONSOLE STATUS:",
                               'System.getProperty("%s") currently set to: %s\n'%(key,props_ofx_debug),
                               200,"TOGGLE MONEYDANCE INTERNAL OFX DEBUG",
                               lCancelButton=True,OKButtonText="SET to %s" %toggleText)
        if not ask.go():
            statusLabel.setText(("HACKER MODE: NO CHANGES MADE TO OFX DEBUG CONSOLE!").ljust(800, " "))
            statusLabel.setForeground(Color.BLUE)
            return

        myPrint("B","HACKER MODE: User requested to toggle System Property '%s' to %s - setting this now...!" %(key,toggleText))
        if toggleText == "OFF":
            System.clearProperty(key)
        else:
            System.setProperty(key, "true")

        statusLabel.setText(("Moneydance internal debug ofx debug console setting turned %s" %toggleText).ljust(800, " "))
        statusLabel.setForeground(Color.BLUE)
        myPopupInformationBox(toolbox_frame_,"Moneydance internal ofx debug console setting turned %s" %toggleText,"TOGGLE MONEYDANCE INTERNAL OFX DEBUG",JOptionPane.WARNING_MESSAGE)

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

        return

    # noinspection PyUnresolvedReferences
    def CUSIPFix(statusLabel):
        global toolbox_frame_, debug

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        currID = "curr_id."

        # Credit to: Finite Mobius, LLC / Jason R. Miller" for original code (https://github.com/finitemobius/moneydance-py)
        # change-security-cusip.py
        # Variant of remove_ofx_security_bindings.py

        # Find Securities with CUSIP(s) set...
        dropdownSecs=ArrayList()
        allSecs=ArrayList()
        currencies = moneydance_data.getCurrencies().getAllCurrencies()
        for curr in currencies:
            if curr.getCurrencyType() != CurrencyType.Type.SECURITY: continue                                  # noqa
            allSecs.append(curr)
            for key in curr.getParameterKeys():
                if key.startswith(currID):
                    dropdownSecs.add(curr)
                    break

        theSchemes = None
        selectedSecurity = None
        selectedSecurityMoveTo = None
        lReset = lEdit = lMove = lAdd = False

        if len(dropdownSecs)<1:
            x="You have no existing CUSIP(s); Would you like to add a CUSIP?"
        else:
            x="You have %s securities with CUSIP(s) set; Would you like to manually add a CUSIP? (No brings up more options)" %(len(dropdownSecs))

        if not myPopupAskQuestion(toolbox_frame_,"FIX CUSIP",x,theMessageType=JOptionPane.WARNING_MESSAGE):
            if len(dropdownSecs)<1:
                statusLabel.setText(("FIX CUSIP - You have no existing CUSIP(s) set on Securities - No changes made...").ljust(800, " "))
                statusLabel.setForeground(Color.RED)
                return
        else:
            allSecs=sorted(allSecs, key=lambda sort_x: (sort_x.getName().upper()))
            selectedSecurity = JOptionPane.showInputDialog(toolbox_frame_,
                                                           "Select the security to add CUSIP data",
                                                           "FIX CUSIP",
                                                           JOptionPane.INFORMATION_MESSAGE,
                                                           moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                           allSecs,
                                                           None)

            if not selectedSecurity:
                statusLabel.setText(("FIX CUSIP - No Security was selected - no changes made..").ljust(800, " "))
                statusLabel.setForeground(Color.RED)
                return

            lAdd = True

        if not lAdd:
            dropdownSecs=sorted(dropdownSecs, key=lambda sort_x: (sort_x.getName().upper()))
            selectedSecurity = JOptionPane.showInputDialog(toolbox_frame_,
                                                           "Select the security with CUSIP data to view/change",
                                                           "FIX CUSIP",
                                                           JOptionPane.INFORMATION_MESSAGE,
                                                           moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                           dropdownSecs,
                                                           None)

            if not selectedSecurity:
                statusLabel.setText(("FIX CUSIP - No Security was selected - no changes made..").ljust(800, " "))
                statusLabel.setForeground(Color.RED)
                return

            del dropdownSecs

            schemeText=""
            theSchemes=[]
            for key in selectedSecurity.getParameterKeys():
                if key.startswith(currID):
                    findScheme = key[len(currID):]
                    theSchemes.append([selectedSecurity,findScheme,selectedSecurity.getIDForScheme(findScheme)])
                    schemeText+="Scheme: %s ID: %s\n" %(findScheme,selectedSecurity.getIDForScheme(findScheme))

            if len(theSchemes)<1:
                myPrint("B","FIX CUSIP - error iterating keys on %s for CUSIP(s)" %selectedSecurity)
                statusLabel.setText(("FIX CUSIP - Sorry - something went wrong - no changes made..").ljust(800, " "))
                statusLabel.setForeground(Color.RED)
                return

            ask=MyPopUpDialogBox(toolbox_frame_,"Showing CUSIP data for Security: %s" %(selectedSecurity),schemeText,theTitle="FIX CUSIP",OKButtonText="NEXT STEP",lCancelButton=True)
            if not ask.go():
                statusLabel.setText(("FIX CUSIP - no changes made..").ljust(800, " "))
                statusLabel.setForeground(Color.BLUE)
                return

            options = ["EXIT", "RESET CUSIP(s)", "EDIT ONE CUSIP", "MOVE ALL TO DIFFERENT SECURITY", "ADD NEW CUSIP KEY"]
            selectedOption = JOptionPane.showInputDialog(toolbox_frame_,
                                                         "Select CUSIP Option you want to action",
                                                         "FIX CUSIP",
                                                         JOptionPane.INFORMATION_MESSAGE,
                                                         moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                         options,
                                                         None)

            if not selectedOption or options.index(selectedOption) == 0:
                statusLabel.setText(("FIX CUSIP - No CUSIP option selected - no changes made..").ljust(800, " "))
                statusLabel.setForeground(Color.RED)
                return

            if options.index(selectedOption) == 1: lReset = True
            elif options.index(selectedOption) == 2: lEdit = True
            elif options.index(selectedOption) == 3: lMove = True
            elif options.index(selectedOption) == 4: lAdd = True
            else:
                statusLabel.setText(("FIX CUSIP - Unknown option selected - no changes made").ljust(800, " "))
                statusLabel.setForeground(Color.RED)
                return

            dropdownSecsMoveTo = selectedSecurityMoveTo = None                                                      # noqa

        if lMove:
            dropdownSecsMoveTo = ArrayList()
            currencies = moneydance_data.getCurrencies().getAllCurrencies()
            for curr in currencies:
                if curr.getCurrencyType() != CurrencyType.Type.SECURITY: continue                               # noqa
                if curr == selectedSecurity: continue
                dropdownSecsMoveTo.add(curr)

            if len(dropdownSecsMoveTo)<1:
                myPopupInformationBox(toolbox_frame_,"You have no other Securities to move to - will abort...","FIX CUSIP",JOptionPane.ERROR_MESSAGE)
                statusLabel.setText(("FIX CUSIP - You have no other Securities to move to - No changes made...").ljust(800, " "))
                statusLabel.setForeground(Color.RED)
                return

            dropdownSecsMoveTo=sorted(dropdownSecsMoveTo, key=lambda sort_x: (sort_x.getName().upper()))
            selectedSecurityMoveTo = JOptionPane.showInputDialog(toolbox_frame_,
                                                                 "Select the security to move the CUSIP data to:",
                                                                 "FIX CUSIP",
                                                                 JOptionPane.INFORMATION_MESSAGE,
                                                                 moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                                 dropdownSecsMoveTo,
                                                                 None)

            if not selectedSecurityMoveTo:
                statusLabel.setText(("FIX CUSIP - No Move to Security was selected - no changes made..").ljust(800, " "))
                statusLabel.setForeground(Color.RED)
                return

            lAlreadyHasData = False
            for key in selectedSecurityMoveTo.getParameterKeys():
                if key.startswith(currID):
                    lAlreadyHasData=True
                    break
            if lAlreadyHasData:
                if not myPopupAskQuestion(toolbox_frame_,
                                          "FIX CUSIP",
                                          "Security: %s already has CUSIP data. OK will overwrite matching CUSIP key(s) (Cancel to exit)" %(selectedSecurityMoveTo),
                                          theMessageType=JOptionPane.WARNING_MESSAGE):
                    statusLabel.setText(("FIX CUSIP - Security: %s already has CUSIP data. User asked to Exit..." %(selectedSecurityMoveTo)).ljust(800, " "))
                    statusLabel.setForeground(Color.RED)
                    return
                myPrint("B", "FIX CUSIP - User selected to overwrite existing CUSIP data in Security: %s" %selectedSecurityMoveTo)

        if confirm_backup_confirm_disclaimer(toolbox_frame_,statusLabel,"FIX CUSIP","Are you sure you want to change CUSIP data on security: %s?" %(selectedSecurity)):
            if lReset:
                for key in list(selectedSecurity.getParameterKeys()):
                    if key.startswith(currID):
                        findScheme = key[len(currID):]
                        # noinspection PyUnresolvedReferences
                        oldData = selectedSecurity.getIDForScheme(findScheme)
                        # noinspection PyUnresolvedReferences
                        selectedSecurity.setIDForScheme(findScheme, None)
                        myPrint("B","FIX CUSIP: Deleted CUSIP on Security: %s (Was: Scheme: %s ID: %s)" %(selectedSecurity,findScheme,oldData) )
                selectedSecurity.syncItem()
                myPopupInformationBox(toolbox_frame_,"CUSIP data on Security: %s Reset/Deleted!" %(selectedSecurity),"FIX CUSIP",JOptionPane.WARNING_MESSAGE)

            elif lMove:
                for key in list(selectedSecurity.getParameterKeys()):
                    if key.startswith(currID):
                        findScheme = key[len(currID):]
                        moveData = selectedSecurity.getIDForScheme(findScheme)

                        moveToOldData = selectedSecurityMoveTo.getIDForScheme(findScheme)
                        if moveToOldData:
                            myPrint("B", "FIX CUSIP: Overwriting old data on destination security: %s (Was: Scheme: %s ID: %s)" %(selectedSecurityMoveTo,findScheme,moveToOldData))

                        myPrint("B","FIX CUSIP: Moving CUSIP data from %s to %s Scheme: %s ID: %s" %(selectedSecurity, selectedSecurityMoveTo,findScheme,moveData))
                        selectedSecurityMoveTo.setIDForScheme(findScheme, moveData)
                        selectedSecurity.setIDForScheme(findScheme, None)

                selectedSecurity.syncItem()
                selectedSecurityMoveTo.syncItem()
                myPopupInformationBox(toolbox_frame_,"CUSIP data on Security: %s Moved to Security: %s!" %(selectedSecurity,selectedSecurityMoveTo),"FIX CUSIP",JOptionPane.WARNING_MESSAGE)

            elif lEdit:

                listData=[]
                for x in theSchemes:
                    listData.append(x[1])

                selectedSchemeToChange = JOptionPane.showInputDialog(toolbox_frame_,
                                                                     "Select the CUSIP to edit:",
                                                                     "FIX CUSIP",
                                                                     JOptionPane.INFORMATION_MESSAGE,
                                                                     moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                                     listData,
                                                                     None)

                if not selectedSchemeToChange:
                    statusLabel.setText(("FIX CUSIP - No CUSIP selected to edit - no changes made..").ljust(800, " "))
                    statusLabel.setForeground(Color.RED)
                    return

                newID = myPopupAskForInput(toolbox_frame_,"FIX CUSIP","ENTER NEW ID DATA:","Enter the new CUSIP data for Security: %s CUSIP: %s"
                                           %(selectedSecurity,selectedSchemeToChange),selectedSecurity.getIDForScheme(selectedSchemeToChange))

                if not newID or newID == selectedSecurity.getIDForScheme(selectedSchemeToChange):
                    statusLabel.setText(("FIX CUSIP - EDIT - new data not entered - no changes made").ljust(800, " "))
                    statusLabel.setForeground(Color.RED)
                    return

                myPrint("B","FIX CUSIP - EDIT. Changing Security: %s CUSPID: %s from %s to %s"
                        %(selectedSecurity,selectedSchemeToChange,selectedSecurity.getIDForScheme(selectedSchemeToChange),newID))

                selectedSecurity.setIDForScheme(selectedSchemeToChange,newID)
                selectedSecurity.syncItem()
                myPopupInformationBox(toolbox_frame_,"CUSIP data on Security: %s CUSIP: %s changed to: %s"
                                      %(selectedSecurity, selectedSchemeToChange,newID),"FIX CUSIP",JOptionPane.WARNING_MESSAGE)

            elif lAdd:

                newScheme = myPopupAskForInput(toolbox_frame_,"FIX CUSIP","NEW CUSIP Scheme/Key:","Enter the new CUSIP Scheme/Key to add to Security: %s"
                                               %(selectedSecurity))

                if not newScheme or newScheme == "":
                    statusLabel.setText(("FIX CUSIP - EDIT - new CUSIP Scheme/Key not entered - no changes made").ljust(800, " "))
                    statusLabel.setForeground(Color.RED)
                    return

                newID = myPopupAskForInput(toolbox_frame_,"FIX CUSIP","NEW CUSIP ID:","Enter the new CUSIP ID for Scheme/Key: %s to add to Security: %s"
                                           %(newScheme,selectedSecurity))

                if not newID or newID == "":
                    statusLabel.setText(("FIX CUSIP - EDIT - new CUSIP ID not entered for new Scheme: %s to add to Security: %s - no changes made" %(newScheme,selectedSecurity)).ljust(800, " "))
                    statusLabel.setForeground(Color.RED)
                    return

                myPrint("B","FIX CUSIP - ADD. Adding CUSIP: %s ID %s to Security: %s"
                        %(newScheme, newID, selectedSecurity))

                selectedSecurity.setIDForScheme(newScheme,newID)
                selectedSecurity.syncItem()
                myPopupInformationBox(toolbox_frame_,"CUSIP Scheme/Key: %s ID: %s added to Security: %s"
                                      %(newScheme, newID, selectedSecurity),"FIX CUSIP",JOptionPane.WARNING_MESSAGE)

            else:
                statusLabel.setText(("FIX CUSIP - Unknown option selected - no changes made").ljust(800, " "))
                statusLabel.setForeground(Color.RED)
                return

            play_the_money_sound()
            statusLabel.setText(("FIX CUSIP - Changes successfully applied to Security: %s" %(selectedSecurity)).ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            myPrint("B", "FIX CUSIP - Changes successfully applied to Security: %s" %(selectedSecurity))

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
        return



    def deleteOFXService(statusLabel):
        global toolbox_frame_, debug

        # remove_one_service.py

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        serviceList = moneydance.getCurrentAccountBook().getOnlineInfo().getAllServices()

        service = JOptionPane.showInputDialog(toolbox_frame_,
                                              "Select a service to delete",
                                              "DELETE SERVICE",
                                              JOptionPane.INFORMATION_MESSAGE,
                                              moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                              serviceList.toArray(),
                                              None)

        if not service:
            statusLabel.setText(("No Service was selected - no changes made..").ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            return

        if confirm_backup_confirm_disclaimer(toolbox_frame_,statusLabel,"DELETE BANK SERVICE","Delete Bank Service/Logon profile %s?" %(service)):
            # noinspection PyUnresolvedReferences
            service.clearAuthenticationCache()
            # noinspection PyUnresolvedReferences
            service.deleteItem()
            LS = moneydance_data.getLocalStorage()
            LS.save()
            play_the_money_sound()
            statusLabel.setText(("Banking service / logon profile successfully deleted: " + str(service).ljust(800, " ")))
            statusLabel.setForeground(Color.RED)
            myPrint("B", "User selected to delete banking service: %s" %(service))
            myPopupInformationBox(toolbox_frame_,"Banking Logon Profile/Service %s DELETED!" %(service),"DELETE BANKING SERVICE",JOptionPane.WARNING_MESSAGE)

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
        return


    def forgetOFXImportLink(statusLabel):
        global toolbox_frame_, debug

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        accounts = AccountUtil.allMatchesForSearch(moneydance_data, MyAcctFilter(10))
        selectedAccount = JOptionPane.showInputDialog(toolbox_frame_,
                                                      "Select an account (only these have remembered links)",
                                                      "FORGET OFX banking link",
                                                      JOptionPane.WARNING_MESSAGE,
                                                      None,
                                                      accounts.toArray(),
                                                      None)
        if not selectedAccount:
            statusLabel.setText(("'RESET BANKING LINK' No Account was selected - no changes made..").ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            return

        if confirm_backup_confirm_disclaimer(toolbox_frame_,statusLabel,"RESET BANKING LINK", "Forget OFX banking Import link for Acct: %s?" %(selectedAccount) ):

            selectedAccount.removeParameter("ofx_import_acct_num")                                          # noqa
            selectedAccount.removeParameter("ofx_import_remember_acct_num")                                 # noqa
            selectedAccount.syncItem()                                                                      # noqa

            statusLabel.setText(("OFX Banking Import link successfully forgotten!").ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            myPrint("B", "'RESET BANKING LINK' User selected to forget OFX banking Import link for account: %s - EXECUTED" %(selectedAccount))
            play_the_money_sound()
            myPopupInformationBox(toolbox_frame_, "Banking link on account: %s forgotten!" %(selectedAccount), "RESET BANKING LINK",JOptionPane.WARNING_MESSAGE)

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
        return


    def download_md_fiscal_setup_for_one_bank(bankID):
        global globalSaveFI_data, MD_OFX_BANK_SETTINGS_DIR

        if globalSaveFI_data is None or len(globalSaveFI_data)<1:
            return

        FI=MD_OFX_BANK_SETTINGS_DIR+bankID.strip()+".dct"
        output = ""
        inx = None

        try:
            url = URL(FI)
            urlConn = url.openConnection()
            if urlConn is not None:
                rc = urlConn.getResponseCode()                                                                          # noqa
                if rc == 200:
                    inx = BufferedReader(InputStreamReader(urlConn.getInputStream(), "UTF8"))
                    while True:
                        lineofdata = inx.readLine()
                        if lineofdata is None: break
                        output+=(lineofdata+"\n")                                                                      # noqa
        except:
            myPrint("B", "ERROR downloading from Moneydance Fiscal Setup profiles link: %s " %(FI))
            output+="\n@@ERROR downloading from Moneydance Fiscal Setup profiles link: %s\n" %(FI)
            output+=dump_sys_error_to_md_console_and_errorlog(True)
        finally:
            if inx:
                try:
                    inx.close()
                except:
                    myPrint("B", "Error closing URL stream %s" %(FI))
                    output+="\n@@Error closing URL stream %s\n" %(FI)
                    output+=dump_sys_error_to_md_console_and_errorlog(True)

        return output

    class FIInfo():
        def __init__(self, info):
            self.info = info
            self.id = info.getStr("id", "")
            self.name = info.getStr("fi_name", "")
            self.lowerName = self.name.lower()

        def __str__(self):
            return "%s (%s)" %(self.name,self.id)

        def __repr__(self):
            return "%s (%s)" %(self.name,self.id)

    # noinspection PyUnresolvedReferences
    def download_md_fiscal_setup():
        global globalSaveFI_data, globalSave_DEBUG_FI_data
        global OFX_SETUP_MATCH_MD_BUILD, MD_OFX_DEFAULT_SETTINGS_FILE, MD_OFX_DEBUG_SETTINGS_FILE

        downloadInfo = StreamTable()

        inx = None
        tagText=""
        wait = None

        if globalSaveFI_data is None or len(globalSaveFI_data)<1:

            wait = MyPopUpDialogBox(toolbox_frame_,"PLEASE WAIT - RETRIEVING FISCAL SETUP DATA...",theWidth=100,lModal=False)
            wait.go()

            for theFile in [MD_OFX_DEBUG_SETTINGS_FILE,MD_OFX_DEFAULT_SETTINGS_FILE]:
                myPrint("DB", "Attempting to download: %s" %(theFile))
                try:
                    url = URL(theFile)
                    urlConn = url.openConnection()
                    if urlConn is not None:
                        rc = urlConn.getResponseCode()                                                                     # noqa
                        if rc == 200:
                            inx = BufferedReader(InputStreamReader(urlConn.getInputStream(), "UTF8"))
                            downloadInfo.readFrom(inx)
                            myPrint("DB", "Success downloading: %s" %(theFile))
                except:
                    myPrint("B", "ERROR downloading from Moneydance Fiscal Setup profiles link: %s " %(theFile))
                    dump_sys_error_to_md_console_and_errorlog(False)
                finally:
                    if inx:
                        try:
                            inx.close()
                        except:
                            myPrint("B", "Error closing URL stream %s" %(theFile))
                            dump_sys_error_to_md_console_and_errorlog()

                matches=None
                overrideMessage = downloadInfo.getStr("override_msg", None)
                ifNoneAvailableMessage = downloadInfo.getStr("no_fis_msg", None)
                infoMessage = downloadInfo.getStr("extra_msg", None)
                if overrideMessage is not None:
                    tagText=overrideMessage
                else:
                    matchesObj = downloadInfo.get("matches")
                    matches = ArrayList()
                    if isinstance(matchesObj,(StreamVector)):
                        matchesVector = matchesObj
                        for matchObj in matchesVector:
                            if isinstance(matchObj, StreamTable):
                                matches.add(FIInfo(matchObj))
                    matchCount = 0
                    for i in range(0, matches.size()):
                        if matches is None: break
                        match = matches.get(i)
                        minVersion = match.info.getInt("min_version", 0)                                                    # noqa
                        maxVersion = match.info.getInt("max_version", 99999999)                                             # noqa
                        if (OFX_SETUP_MATCH_MD_BUILD < minVersion or OFX_SETUP_MATCH_MD_BUILD > maxVersion):
                            matches.remove(i)
                            # i-=1
                        else:
                            matchCount+=1
                            i+=1
                    if matchCount == 0 and ifNoneAvailableMessage is not None:
                        tagText= ifNoneAvailableMessage
                    elif infoMessage is not None:
                        tagText=infoMessage

                if theFile == MD_OFX_DEFAULT_SETTINGS_FILE:
                    globalSaveFI_data=matches
                    globalSaveFI_data = sorted(globalSaveFI_data, key=lambda sort_x: (sort_x.lowerName, sort_x.id))
                else:
                    globalSave_DEBUG_FI_data=matches
                    globalSave_DEBUG_FI_data = sorted(globalSave_DEBUG_FI_data, key=lambda sort_x: (sort_x.lowerName, sort_x.id))

        output="Moneydance's Fiscal Institution Initial Dynamic Setup profiles..\n" \
               " ==============================================================\n\n"

        if len(tagText)>0:
            output+="\n%s\n\n" %(tagText)

        miniList=[]
        for bankSetup in globalSaveFI_data:
            output += "\nName: %s (%s)\n" %(bankSetup.name,bankSetup.id)
            miniList.append(bankSetup.lowerName)
            for element in bankSetup.info:
                if element == "id" or element == "fi_name": continue
                output+=" %s %s\n" %(pad(element+":",30), bankSetup.info.get(element))

        miniListDEBUG=[]
        for bankSetup in globalSave_DEBUG_FI_data:
            miniListDEBUG.append(bankSetup.lowerName)

        if len(globalSaveFI_data)<1:
            output+="\nNO SETUP FOUND... DID SOMETHING GO WRONG? REVIEW CONSOLE ERROR LOG..!\n\n"

        output+="\n<END>"

        if wait is not None: wait.kill()

        jif = QuickJFrame("VIEW Moneydance's Dynamic / live Fiscal Institution setup profiles", output).show_the_frame()

        if len(miniList)>0:
            selectedID = JOptionPane.showInputDialog(jif,
                                                     "Select Bank Profile to view specific setup data",
                                                      "VIEW SPECIFIC SETUP DATA",
                                                      JOptionPane.INFORMATION_MESSAGE,
                                                      None,
                                                      globalSaveFI_data,
                                                      None)
            if selectedID:
                specificText = download_md_fiscal_setup_for_one_bank(selectedID.id)

                output="Moneydance's Fiscal Institution Initial Dynamic Setup profiles..\n" \
                       " ==============================================================\n\n" \
                       "Initial/Default Setup:\n" \
                       "----------------------\n"

                output += "\nName: %s (%s)\n" %(selectedID.name,selectedID.id)
                for element in selectedID.info:
                    if element == "id" or element == "fi_name": continue

                    extraText=""
                    if element == "dt_prof_updated": extraText="(%s)" %(get_time_stamp_as_nice_text(int(selectedID.info.get(element))))
                    output+=" %s %s %s\n" %(pad(element+":",30), selectedID.info.get(element),extraText)

                try:
                    output += "\n\nDEBUG Setup:\n" \
                              "--------------------------\n"
                    for findID in globalSave_DEBUG_FI_data:
                        if findID.id == selectedID.id:
                            for element in findID.info:
                                if element == "id" or element == "fi_name": continue
                                extraText=""
                                if element == "dt_prof_updated": extraText="(%s)" %(get_time_stamp_as_nice_text(int(findID.info.get(element))))
                                output+=" %s %s %s\n" %(pad(element+":",30), findID.info.get(element),extraText)
                            break
                except:
                    pass

                output += "\n\nSPECIFIC OVERRIDING Setup:\n" \
                       "--------------------------\n"
                output+=specificText
                output+="\n<END>"

                QuickJFrame("VIEW Moneydance's Specific (dynamic) Fiscal Institution setup profiles", output).show_the_frame()

        return

    def get_the_objects_for_geekout_and_hacker_edit(objWhat, selectedObjType, statusLabel, titleStr, lForceOneTxn):

        # Yes, I know, repeated from calling function.... EDIT IN BOTH PLACES!
        # You need to edit the below in the sub def function too!!! (sorry ;-> )
        _OBJROOT        =  0
        _OBJACCT        =  1
        _OBJCAT         =  2
        _OBJACCTSEC     =  3
        _OBJCURR        =  4
        _OBJSEC         =  5
        _OBJREMINDERS   =  6
        _REPORT_MEM     =  7
        _GRAPH_MEM      =  8
        _REPORT_DEF     =  9
        _GRAPH_DEF      =  10
        _OBJADDRESSES   =  11
        _OBJOFXONLINE   =  12
        _OBJBYUUID      =  13
        _OBJTRANSACTION =  14
        _OBJSECSUBTYPES =  15
        _OBJOFXOLPAYEES =  16
        _OBJOFXOLPAYMNT =  17
        _OBJOFXTXNS     =  18

        lReportDefaultsSelected = False

        def getCurrTable(cType):

            cTable=ArrayList()
            myTable = moneydance.getCurrentAccountBook().getCurrencies()
            myTable = sorted(myTable, key=lambda sort_x: (sort_x.getCurrencyType(), sort_x.getName().upper()))
            for curr in myTable:
                if curr.getCurrencyType() == cType:
                    cTable.add(curr)
            return cTable

        def getReportsTable(memorized_default_or_all, report_or_graph_or_all):

            theReports = None

            repTable=ArrayList()
            if report_or_graph_or_all == "ALL":
                if memorized_default_or_all == "ALL":
                    return moneydance_data.getMemorizedItems().getAllItems()
                elif memorized_default_or_all == "MEMORIZED":
                    return  moneydance_data.getMemorizedItems().getAllMemorizedItems()
                elif memorized_default_or_all == "DEFAULT":
                    theReports = moneydance_data.getMemorizedItems().getAllItems()
                else:
                    assert("ERROR - Report  type not defined: %s %s" %(memorized_default_or_all,report_or_graph_or_all))
            elif report_or_graph_or_all == "REPORT":
                if memorized_default_or_all == "ALL":
                    return moneydance_data.getMemorizedItems().getAllReports()
                elif memorized_default_or_all == "MEMORIZED":
                    return  moneydance_data.getMemorizedItems().getMemorizedReports()
                elif memorized_default_or_all == "DEFAULT":
                    theReports = moneydance_data.getMemorizedItems().getAllReports()
                else:
                    assert("ERROR - Report  type not defined: %s %s" %(memorized_default_or_all,report_or_graph_or_all))
            elif report_or_graph_or_all == "GRAPH":
                if memorized_default_or_all == "ALL":
                    return moneydance_data.getMemorizedItems().getAllGraphs()
                elif memorized_default_or_all == "MEMORIZED":
                    return  moneydance_data.getMemorizedItems().getMemorizedGraphs()
                elif memorized_default_or_all == "DEFAULT":
                    theReports = moneydance_data.getMemorizedItems().getAllGraphs()
                else:
                    assert("ERROR - Report  type not defined: %s %s" %(memorized_default_or_all,report_or_graph_or_all))
            else:
                assert("ERROR - Report  type not defined: %s %s" %(memorized_default_or_all,report_or_graph_or_all))

            # For Default return non memorized Items
            for rep in theReports:
                if not rep.isMemorized():
                    repTable.add(rep)

            return repTable

        objects = None
        try:
            if objWhat.index(selectedObjType) == _OBJROOT:
                obj_x = AccountUtil.allMatchesForSearch(moneydance_data, MyAcctFilter(12))
                # The palaver below is to get the list sorted.....
                objects = ArrayList()
                for o in obj_x: objects.add(o)
                objects = objects.toArray()
            elif objWhat.index(selectedObjType) == _OBJACCT:
                obj_x = AccountUtil.allMatchesForSearch(moneydance_data, MyAcctFilter(7))
                # The palaver below is to get the list sorted.....
                obj_x = sorted(obj_x, key=lambda sort_x: (sort_x.getAccountType(), sort_x.getFullAccountName().upper()))
                objects = ArrayList()
                for o in obj_x: objects.add(o)
                objects = objects.toArray()
            elif objWhat.index(selectedObjType) == _OBJCAT:
                obj_x = AccountUtil.allMatchesForSearch(moneydance_data, MyAcctFilter(8)).toArray()
                obj_x = sorted(obj_x, key=lambda sort_x: (sort_x.getAccountType(), sort_x.getFullAccountName().upper()))
                objects = ArrayList()
                for o in obj_x: objects.add(o)
                objects = objects.toArray()
            elif objWhat.index(selectedObjType) == _OBJACCTSEC:
                obj_x = AccountUtil.allMatchesForSearch(moneydance_data, MyAcctFilter(9)).toArray()
                obj_x = sorted(obj_x, key=lambda sort_x: (sort_x.getAccountType(), sort_x.getFullAccountName().upper()))
                objects = ArrayList()
                for o in obj_x: objects.add(o)
                objects = objects.toArray()
            elif objWhat.index(selectedObjType) == _OBJCURR:
                # noinspection PyUnresolvedReferences
                objects = getCurrTable(CurrencyType.Type.CURRENCY)
            elif objWhat.index(selectedObjType) == _OBJSEC:
                # noinspection PyUnresolvedReferences
                objects = getCurrTable(CurrencyType.Type.SECURITY)
            elif objWhat.index(selectedObjType) == _REPORT_MEM:
                objects = getReportsTable("MEMORIZED", "REPORT")
                objects = sorted(objects, key=lambda x: (x.isMemorized(), x.getName().upper()))
            elif objWhat.index(selectedObjType) == _GRAPH_MEM:
                objects = getReportsTable("MEMORIZED", "GRAPH")
                objects = sorted(objects, key=lambda x: (x.isMemorized(), x.getName().upper()))
            elif objWhat.index(selectedObjType) == _REPORT_DEF:
                lReportDefaultsSelected = True
                objects = getReportsTable("DEFAULT", "REPORT")
                objects = sorted(objects, key=lambda x: (x.isMemorized(), x.getName().upper()))
            elif objWhat.index(selectedObjType) == _GRAPH_DEF:
                lReportDefaultsSelected = True
                objects = getReportsTable("DEFAULT", "GRAPH")
                objects = sorted(objects, key=lambda x: (x.isMemorized(), x.getName().upper()))
            elif objWhat.index(selectedObjType) == _OBJREMINDERS:
                root = moneydance.getCurrentAccountBook()
                objects = root.getReminders().getAllReminders()
                objects = sorted(objects, key=lambda x: (x.getDescription().upper()))
            elif objWhat.index(selectedObjType) == _OBJADDRESSES:
                root = moneydance.getCurrentAccountBook()
                objects = root.getAddresses().getAllEntries()
                objects = sorted(objects, key=lambda x: (x.getName().upper()))
            elif objWhat.index(selectedObjType) == _OBJOFXONLINE:
                objects = moneydance_data.getOnlineInfo().getAllServices()
                objects = sorted(objects, key=lambda x: (x.getFIName().upper()))
            elif objWhat.index(selectedObjType) == _OBJBYUUID:
                pass
            elif objWhat.index(selectedObjType) == _OBJTRANSACTION:
                pass
            elif objWhat.index(selectedObjType) == _OBJSECSUBTYPES:
                item = moneydance_data.getItemForID("security_subtypes")                      # type: MoneydanceSyncableItem
                if item is None:
                    statusLabel.setText(("%s: Sorry - You don't have a 'security_subtypes' to view..!" %(titleStr)).ljust(800, " "))
                    statusLabel.setForeground(Color.RED)
                    return None, lReportDefaultsSelected
                else:
                    objects = [item]

            elif (objWhat.index(selectedObjType) == _OBJOFXOLPAYEES
                  or objWhat.index(selectedObjType) == _OBJOFXOLPAYMNT
                  or objWhat.index(selectedObjType) == _OBJOFXTXNS):

                accountsListForOlTxns = None
                if objWhat.index(selectedObjType) == _OBJOFXTXNS:
                    accountsListForOlTxns = AccountUtil.allMatchesForSearch(moneydance_data, MyAcctFilter(15))
                elif objWhat.index(selectedObjType) == _OBJOFXOLPAYEES:
                    accountsListForOlTxns = AccountUtil.allMatchesForSearch(moneydance_data, MyAcctFilter(16))
                elif objWhat.index(selectedObjType) == _OBJOFXOLPAYMNT:
                    accountsListForOlTxns = AccountUtil.allMatchesForSearch(moneydance_data, MyAcctFilter(17))

                accountsListForOlTxns = sorted(accountsListForOlTxns, key=lambda sort_x: (sort_x.getFullAccountName().upper()))

                selectedAcct = JOptionPane.showInputDialog(toolbox_frame_,
                                                             "Select the Acct to find Online Data about:",
                                                             "Select ACCOUNT",
                                                             JOptionPane.INFORMATION_MESSAGE,
                                                             moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                             accountsListForOlTxns,
                                                             None)
                if not selectedAcct:
                    statusLabel.setText(("No Account was selected..").ljust(800, " "))
                    statusLabel.setForeground(Color.RED)
                    return None, lReportDefaultsSelected

                if objWhat.index(selectedObjType) == _OBJOFXTXNS:
                    objects = [StoreTheOnlineTxnList(MyGetDownloadedTxns(selectedAcct),selectedAcct)]       # Use my version to prevent creation of default record(s)
                elif objWhat.index(selectedObjType) == _OBJOFXOLPAYEES:
                    objects = [StoreTheOnlinePayeeList(MyGetOnlinePayees(selectedAcct),selectedAcct)]       # Use my version to prevent creation of default record(s)
                elif objWhat.index(selectedObjType) == _OBJOFXOLPAYMNT:
                    objects = [StoreTheOnlinePaymentList(MyGetOnlinePayments(selectedAcct),selectedAcct)]       # Use my version to prevent creation of default record(s)

            else:
                return None, lReportDefaultsSelected
        except:
            dump_sys_error_to_md_console_and_errorlog( True )
            return None, lReportDefaultsSelected

        if objWhat.index(selectedObjType) == _OBJTRANSACTION:

            dateStart = 20251231
            dateEnd = 20251231

            dateTxt=""
            if lForceOneTxn:
                labelDateStart = JLabel("Select the Date (enter as yyyy/mm/dd):")
            else:
                dateTxt="Range "
                labelDateStart = JLabel("Date range start (enter as yyyy/mm/dd):")
            user_selectDateStart = JDateField(CustomDateFormat("ymd"),15)   # Use MD API function (not std Python)
            user_selectDateStart.setDateInt(dateStart)

            labelDateEnd = JLabel("Date range end (enter as yyyy/mm/dd):")
            user_selectDateEnd = JDateField(CustomDateFormat("ymd"),15)   # Use MD API function (not std Python)
            user_selectDateEnd.setDateInt(dateEnd)

            datePanel = JPanel(GridLayout(0, 2))
            datePanel.add(labelDateStart)
            datePanel.add(user_selectDateStart)

            if not lForceOneTxn:
                datePanel.add(labelDateEnd)
                datePanel.add(user_selectDateEnd)

            options = ["Cancel", "OK"]

            while True:
                userAction = JOptionPane.showOptionDialog(toolbox_frame_,
                                                          datePanel,
                                                          "%s: Select Date %sfor TXNs (less is better)" %(titleStr,dateTxt),
                                                          JOptionPane.OK_CANCEL_OPTION,
                                                          JOptionPane.QUESTION_MESSAGE,
                                                          None,
                                                          options,
                                                          options[1])

                if userAction != 1:
                    statusLabel.setText(("%s: User cancelled Date Selection for TXN Search" %(titleStr)).ljust(800, " "))
                    statusLabel.setForeground(Color.RED)
                    return None, lReportDefaultsSelected

                if lForceOneTxn:
                    user_selectDateEnd.setDateInt( user_selectDateStart.getDateInt() )

                if user_selectDateStart.getDateInt() <= user_selectDateEnd.getDateInt() \
                        and user_selectDateEnd.getDateInt() >= user_selectDateStart.getDateInt():
                    break   # Valid date range

                user_selectDateStart.setForeground(Color.RED)
                user_selectDateEnd.setForeground(Color.RED)
                continue   # Loop

            if objWhat.index(selectedObjType) == _OBJTRANSACTION:
                txns = moneydance.getCurrentAccountBook().getTransactionSet().getTransactions(
                                            MyTxnSearchFilter(user_selectDateStart.getDateInt(),user_selectDateEnd.getDateInt()))
            else:
                txns = []

            if not txns or txns.getSize() <1:
                statusLabel.setText(("%s: No Transactions Found.."  %(titleStr)).ljust(800, " "))
                statusLabel.setForeground(Color.RED)
                return None, lReportDefaultsSelected

            if not lForceOneTxn:
                if txns.getSize() > 20:
                    if not myPopupAskQuestion(toolbox_frame_, "SEARCH TXNs BY DATE", "YOU HAVE SELECTED %s TXNS.. PROCEED?" % txns.getSize()):
                        statusLabel.setText(("%s:TXN SEARCH FOUND %s TXNs. USER ABORTED...."%(titleStr,txns.getSize())).ljust(800, " "))
                        statusLabel.setForeground(Color.RED)
                        return None, lReportDefaultsSelected

            if lForceOneTxn:
                objects=ArrayList()
                for txn in txns:
                    objects.add(txn)
            else:
                objects = txns

        if objWhat.index(selectedObjType) == _OBJBYUUID:
            theUUID = myPopupAskForInput(toolbox_frame_, "GET SINGLE OBJECT BY UUID", "UUID:", "%s: Enter the UUID of the Object to get" %(titleStr), "", False)

            if not theUUID or theUUID == "":
                statusLabel.setText(("%s: No Object UUID was entered.." %(titleStr)).ljust(800, " "))
                statusLabel.setForeground(Color.RED)
                return None, lReportDefaultsSelected

            selectedObject = moneydance_data.getItemForID(theUUID.strip())
            objects  = [selectedObject]
            if not selectedObject:
                statusLabel.setText(("%s: No Object was found for UUID: %s" %(titleStr,theUUID)).ljust(800, " "))
                statusLabel.setForeground(Color.RED)
                return None, lReportDefaultsSelected


        if (objWhat.index(selectedObjType) == _OBJTRANSACTION and not lForceOneTxn):
            pass
        else:
            selectedObject = JOptionPane.showInputDialog(toolbox_frame_,
                                                         "Select the specific Object to %s" %(titleStr),
                                                         "Select Specific Object",
                                                         JOptionPane.INFORMATION_MESSAGE,
                                                         moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                         objects,
                                                         None)
            objects  = [selectedObject]
            if not selectedObject:
                statusLabel.setText(("%s: No Object was selected.." %(titleStr)).ljust(800, " "))
                statusLabel.setForeground(Color.RED)
                return None, lReportDefaultsSelected

            if (objWhat.index(selectedObjType) == _OBJOFXTXNS
                    or objWhat.index(selectedObjType) == _OBJOFXOLPAYEES
                    or objWhat.index(selectedObjType) == _OBJOFXOLPAYMNT):
                # noinspection PyUnresolvedReferences
                objects = [selectedObject.obj]       # Use my version to prevent creation of default record(s)

        return objects, lReportDefaultsSelected


    def hackerRemoveInternalFilesSettings(statusLabel):
        thisDataset = moneydance_data.getRootFolder().getCanonicalPath()

        filesToRemove = []
        for wrapper in AccountBookUtil.getInternalAccountBooks():
            internal_filepath = wrapper.getBook().getRootFolder().getCanonicalPath()
            if internal_filepath == thisDataset:
                continue
            filesToRemove.append(internal_filepath)

        if len(filesToRemove)<1:
            statusLabel.setText(("HACK: DELETE internal / Default Dataset(s) from DISK - You have no files to DELETE - no changes made...." ).ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            myPopupInformationBox(toolbox_frame_,"You have no 'Internal' / default files to DELETE - NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        iFilesOnDiskRemoved = 0

        while True:

            selectedFile = None
            if len(filesToRemove) > 0:
                saveOK = UIManager.get("OptionPane.okButtonText")
                saveCancel = UIManager.get("OptionPane.cancelButtonText")
                UIManager.put("OptionPane.okButtonText", "DELETE DATASET FROM DISK")
                UIManager.put("OptionPane.cancelButtonText", "EXIT")

                selectedFile = JOptionPane.showInputDialog(toolbox_frame_,
                                                           "Select the default/internal location Dataset to DELETE from disk",
                                                           "HACKER - DELETE FROM DISK",
                                                           JOptionPane.ERROR_MESSAGE,
                                                           None,
                                                           filesToRemove,
                                                           None)

                UIManager.put("OptionPane.okButtonText", saveOK)
                UIManager.put("OptionPane.cancelButtonText", saveCancel)

            if not selectedFile:
                if iFilesOnDiskRemoved<1:
                    statusLabel.setText(("Thank you for using HACKER MODE!.. No changes made").ljust(800, " "))
                    statusLabel.setForeground(Color.BLUE)
                    myPopupInformationBox(toolbox_frame_,"NO CHANGES MADE!",theMessageType=JOptionPane.INFORMATION_MESSAGE)
                else:
                    statusLabel.setText(("Thank you for using HACKER MODE!.. %s Datasets DELETED" %(iFilesOnDiskRemoved)).ljust(800, " "))
                    statusLabel.setForeground(Color.BLUE)
                    myPopupInformationBox(toolbox_frame_,
                                          "HACKER MODE!.. %s Datasets DELETED - PLEASE RESTART MD" %(iFilesOnDiskRemoved),
                                          theMessageType=JOptionPane.ERROR_MESSAGE)
                return

            if os.path.exists(selectedFile):
                if not myPopupAskQuestion(toolbox_frame_,
                                      "HACKER - DISCLAIMER - ARE YOU SURE?",
                                      "Are you SURE you REALLY want me to DELETE the %s dataset from disk?" %(selectedFile),
                                      theMessageType=JOptionPane.ERROR_MESSAGE):
                    continue

                filesToRemove.remove(selectedFile)

                try:
                    shutil.rmtree(selectedFile)
                    myPrint("B","Hacker - Dataset %s removed from disk" %(selectedFile))
                    iFilesOnDiskRemoved+=1
                    play_the_money_sound()
                    statusLabel.setForeground(Color.RED)
                    statusLabel.setText(("@@ HACKERMODE: Dataset %s removed from disk" %(selectedFile)).ljust(800, " "))
                    myPopupInformationBox(toolbox_frame_,
                                          "@@ HACKERMODE: Dataset %s removed from disk" %(selectedFile),
                                          "HACKER - DELETE FILE FROM DISK",
                                          JOptionPane.ERROR_MESSAGE)
                except:
                    dump_sys_error_to_md_console_and_errorlog()
                    myPrint("B","@ERROR@ Hacker - Dataset %s FAILED TO remove from disk" %(selectedFile))
                    statusLabel.setForeground(Color.RED)
                    statusLabel.setText(("@ERROR@ Hacker - Dataset %s FAILED TO remove from disk" %(selectedFile)).ljust(800, " "))
                    myPopupInformationBox(toolbox_frame_,
                                          "@ERROR@ Hacker - Dataset %s FAILED TO remove from disk" %(selectedFile),
                                          "HACKER - ERROR",
                                          JOptionPane.ERROR_MESSAGE)

            continue

        del filesToRemove

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

        return

    def hackerRemoveExternalFilesSettings(statusLabel):
        global toolbox_frame_, debug, DARK_GREEN, lCopyAllToClipBoard_TB
        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        if moneydance_data is None: return

        if not backup_config_dict():
            statusLabel.setText("HACK: Remove files from 'External' (non-default) filelist in File/Open - Error backing up config.dict preferences file - no changes made....".ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            myPopupInformationBox(toolbox_frame_,"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        theKey = "external_files"
        prefs = moneydance_ui.getPreferences()
        thisDataset = moneydance_data.getRootFolder().getCanonicalPath()

        externalFilesVector = prefs.getVectorSetting("external_files", StreamVector())

        filesToRemove = []
        for externalFileObj in externalFilesVector:
            if externalFileObj != thisDataset:
                filesToRemove.append(externalFileObj)

        if externalFilesVector is None or len(filesToRemove)<1:
            statusLabel.setText(("HACK: Remove files from 'External' (non-default) filelist in File/Open - You have no %s files in config.dict to edit - no changes made...." %(theKey)).ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            myPopupInformationBox(toolbox_frame_,"You have no 'External' file references in config.dict to remove - NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        iReferencesRemoved = 0
        iFilesOnDiskRemoved = 0

        while True:

            selectedFile = None
            if len(filesToRemove) > 0:
                saveOK = UIManager.get("OptionPane.okButtonText")
                saveCancel = UIManager.get("OptionPane.cancelButtonText")
                UIManager.put("OptionPane.okButtonText", "REMOVE FILE REFERENCE FROM File/Open")
                UIManager.put("OptionPane.cancelButtonText", "EXIT")

                selectedFile = JOptionPane.showInputDialog(toolbox_frame_,
                                                           "Select the 'External' (non-default) file reference to remove",
                                                           "HACKER",
                                                           JOptionPane.WARNING_MESSAGE,
                                                           None,
                                                           filesToRemove,
                                                           None)

                UIManager.put("OptionPane.okButtonText", saveOK)
                UIManager.put("OptionPane.cancelButtonText", saveCancel)

            if not selectedFile:
                if (iReferencesRemoved+iFilesOnDiskRemoved)<1:
                    statusLabel.setText(("Thank you for using HACKER MODE!.. No changes made").ljust(800, " "))
                    statusLabel.setForeground(Color.BLUE)
                    myPopupInformationBox(toolbox_frame_,"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
                    return
                else:
                    statusLabel.setText(("Thank you for using HACKER MODE!.. %s references removed and %s Datasets DELETED" %(iReferencesRemoved, iFilesOnDiskRemoved)).ljust(800, " "))
                    statusLabel.setForeground(Color.BLUE)
                    myPopupInformationBox(toolbox_frame_,
                                          "HACKER MODE!.. %s references removed and %s Datasets DELETED - PLEASE RESTART MD"
                                          %(iReferencesRemoved, iFilesOnDiskRemoved),
                                          theMessageType=JOptionPane.ERROR_MESSAGE)
                return

            iReferencesRemoved+=1
            filesToRemove.remove(selectedFile)

            externalFilesVector.remove(selectedFile)
            prefs.setSetting("external_files", externalFilesVector)
            moneydance.savePreferences()
            myPrint("B","OK I have removed the reference to file %s from config.dict (and file/open menu if present)" %(selectedFile))
            myPopupInformationBox(toolbox_frame_,"OK I have removed the reference to file %s from config.dict (and file/open menu if present)" %(selectedFile),"HACKER",JOptionPane.WARNING_MESSAGE)

            if not os.path.exists(selectedFile): continue

            if not myPopupAskQuestion(toolbox_frame_,
                                  "HACKER",
                                  "Would you like me to DELETE the %s dataset from disk too?" %(selectedFile),
                                  theMessageType=JOptionPane.ERROR_MESSAGE):
                continue

            try:

                shutil.rmtree(selectedFile)
                iFilesOnDiskRemoved+=1

                myPrint("B","Hacker - Dataset %s removed from disk" %(selectedFile))
                play_the_money_sound()
                statusLabel.setText(("Hacker - Dataset %s removed from disk" %(selectedFile)).ljust(800, " "))
                statusLabel.setForeground(Color.RED)
                myPopupInformationBox(toolbox_frame_,
                                      "Dataset %s removed from disk" %(selectedFile),
                                      "HACKER",
                                      JOptionPane.ERROR_MESSAGE)
            except:
                dump_sys_error_to_md_console_and_errorlog()
                myPrint("B","@ERROR@ Hacker - Dataset %s FAILED TO remove from disk" %(selectedFile))
                myPopupInformationBox(toolbox_frame_,
                                      "@@ HACKERMODE: ERROR - FAILED to DELETE Dataset %s from disk!" %(selectedFile),
                                      "HACKER",
                                      JOptionPane.WARNING_MESSAGE)

            continue

        del filesToRemove

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

        return

    # END OF DEFs

    # START OF CLASSES
    class MyRunnable(Runnable):

        def __init__(self, theFrame):
            self.theFrame = theFrame

        # noinspection PyMethodMayBeStatic
        def run(self):
            global debug

            myPrint("DB","Inside %s MyRunnable.... About to trigger WindowClosing event to close %s" %(myModuleID,myModuleID))
            try:
                self.theFrame.dispatchEvent(WindowEvent(self.theFrame, WindowEvent.WINDOW_CLOSING))
                myPrint("DB","Back from pushing a WINDOW_CLOSING Event to %s...." %myModuleID)
            except:
                dump_sys_error_to_md_console_and_errorlog()
                myPrint("B","@@ ERROR pushing a WINDOW_CLOSING Event to %s....  :-< " %myModuleID)

            return

    class MyEventListener(AppEventListener):

        def __init__(self, theFrame):
            self.alreadyClosed = False
            self.theFrame = theFrame

        # noinspection PyMethodMayBeStatic
        def handleEvent(self, appEvent):
            global debug

            if self.alreadyClosed:
                myPrint("DB","....I'm actually still here (MD EVENT %s CALLED).. - Ignoring and returning back to MD...." %(appEvent))
                return

            # I am only closing Toolbox when a new Dataset is opened.. I was calling it on MD Close/Exit, but it seemed to cause an Exception...
            if (appEvent == "md:file:closing"
                    or appEvent == "md:file:closed"
                    or appEvent == "md:file:opening"
                    or appEvent == "md:app:exiting"):
                myPrint("DB","@@ Ignoring MD handleEvent: %s" %(appEvent))

            elif (appEvent == "md:file:opened"):
                if debug:
                    myPrint("DB","MD event %s triggered.... Will call MyRunnable (on a new Thread) to push a WINDOW_CLOSING Event to %s to close itself (while I exit back to MD quickly) ...." %(appEvent, myModuleID))
                else:
                    myPrint("B","Moneydance triggered event %s triggered - So I am closing %s now...." %(appEvent, myModuleID))
                self.alreadyClosed = True
                try:
                    t = Thread(MyRunnable(self.theFrame))
                    t.start()
                    myPrint("DB","Back from calling MyRunnable to push a WINDOW_CLOSING Event to %s.... ;-> ** I'm getting out quick! **" %(myModuleID))
                except:
                    dump_sys_error_to_md_console_and_errorlog()
                    myPrint("B","@@ ERROR calling MyRunnable to push  a WINDOW_CLOSING Event to %s.... :-< ** I'm getting out quick! **" %(myModuleID))
                if not debug: myPrint("DB","Returning back to Moneydance after calling for %s to close...." %myModuleID)
                return

            myPrint("DB","@@ Detected MD handleEvent: %s" %(appEvent))

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


    class GeekOutModeButtonAction(AbstractAction):

        def __init__(self, statusLabel, lOFX=False, EDIT_MODE=False):
            self.statusLabel = statusLabel
            self.lOFX = lOFX
            self.EDIT_MODE = EDIT_MODE

        def actionPerformed(self, event):
            global toolbox_frame_, debug, DARK_GREEN, lCopyAllToClipBoard_TB, lGeekOutModeEnabled_TB
            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

            if moneydance_data is None: return

            _SEARCH   = 0
            _ROOTKEYS = 1
            _BOOKKEYS = 2
            _PREFKEYS = 3
            _ACCTKEYS = 4
            _OBJKEYS  = 5
            _SYNCKEYS = 6
            _BANKKEYS = 7
            _SIZEKEYS = 8
            _OSPROPS  = 9
            _OSENV    = 10

            what = [
                "Search for a key/data (in most places  - but not txns)",
                "Show ROOT Account's Parameter Keys and data",
                "Show Dataset's Local Storage Keys and data (from ./safe/settings)",
                "Show All User Preferences loaded into Memory (from config.dict)",
                "Show Accounts' Parameter's Keys and Data",
                "Show an Obj's settings/data (Acct, Cat, Curr, Security, Reports, Reminders, Addrs, OFX, by UUID, TXNs)",
                "Show All Sync Settings",
                "Show All Online Banking (Searches for OFX) Settings",
                "Show all Settings relating to Window Locations/Sizes/Widths/Sort Order/Filters/Initial Reg View etc..",
                "Show all Operating 'System' Properties",
                "Show all Operating System Environment Variables"]

            # You need to edit the below in the sub function and edit function too!!! (sorry ;-> )
            _OBJROOT        =  0
            _OBJACCT        =  1
            _OBJCAT         =  2
            _OBJACCTSEC     =  3
            _OBJCURR        =  4
            _OBJSEC         =  5
            _OBJREMINDERS   =  6
            _REPORT_MEM     =  7
            _GRAPH_MEM      =  8
            _REPORT_DEF     =  9
            _GRAPH_DEF      =  10
            _OBJADDRESSES   =  11
            _OBJOFXONLINE   =  12
            _OBJBYUUID      =  13
            _OBJTRANSACTION =  14
            _OBJSECSUBTYPES =  15
            _OBJOFXOLPAYEES =  16
            _OBJOFXOLPAYMNT =  17
            _OBJOFXTXNS     =  18

            objWhat = [                 # Note - I haven't included csnaps/csplit - they don't actually return the map / keys.....
                "ROOT (the master/parent/top-level Account)",
                "Account",
                "Category",
                "Security sub-account",
                "Currency",
                "Security (from Currency Table)",
                "Reminders",
                "Report (Memorized)",
                "Graph (Memorized)",
                "Report (Default)",
                "Graph (Default)",
                "Address Book Entry",
                "Online OFX Services (Bank Logon Profiles)",
                "Object by UUID",
                "Object Transactions (by date)",                # TransactionSet(ParentTxn) "txn"
                "Security Sub Types"                            # moneydanceSyncableItem    "secsubtypes"
            ]

            if not self.lOFX:                                   # ... and not self.EDIT_MODE:
                objWhat += [
                    "OFX Online Payees",                         # onlinePayeeList           "olpayees"
                    "OFX Online Payments",                       # onlinePaymentList         "olpmts"
                    "OFX Online Transactions"                    # onlineTxnList             "oltxns"
                ]

            if self.lOFX:
                selectedWhat = what[_BANKKEYS]
            elif self.EDIT_MODE:
                selectedWhat = what[_OBJKEYS]
            else:
                selectedWhat = JOptionPane.showInputDialog(toolbox_frame_,
                                                           "Select the type of Key data you want to view",
                                                           "GEEK OUT",
                                                           JOptionPane.INFORMATION_MESSAGE,
                                                           moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                           what,
                                                           None)
                if not selectedWhat:
                    self.statusLabel.setText(("No data type was selected to Geek out on..").ljust(800, " "))
                    self.statusLabel.setForeground(Color.RED)
                    return

            myPrint("J", "User has requested to view internal Moneydance Settings (Geek Out Mode): %s"%selectedWhat)

            lObject = False
            selectedObject = None                                                                               # noqa
            lReportDefaultsSelected = False

            root = moneydance.getCurrentAccountBook().getRootAccount()

            output = ""

            searchWhat = ""
            lSearch = lKeys = lKeyData = False
            if selectedWhat == what[_SEARCH]:
                lSearch = True

                selectedSearch = JOptionPane.showInputDialog(toolbox_frame_,
                                                             "SEARCH: Keys or Key Data?",
                                                             "GEEK OUT",
                                                             JOptionPane.INFORMATION_MESSAGE,
                                                             moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                             ["Keys","Key Data"],
                                                             None)
                if not selectedSearch:
                    self.statusLabel.setText(("No Search type selected (to Geek out on..)").ljust(800, " "))
                    self.statusLabel.setForeground(Color.RED)
                    return

                if selectedSearch == "Keys": lKeys = True
                elif selectedSearch == "Key Data": lKeyData = True
                else:
                    raise(Exception("ERROR: Unknown Geekout Search Key type selected!?"))

                searchWhat = myPopupAskForInput(toolbox_frame_, "GEEK OUT: SEARCH", "%s:" % selectedSearch, "Enter the (partial) string to search for within %s..." % selectedSearch, "", False)
                if not searchWhat or searchWhat == "":
                    self.statusLabel.setText(("No Search data selected (to Geek out on..)").ljust(800, " "))
                    self.statusLabel.setForeground(Color.RED)
                    return
                searchWhat=searchWhat.strip()

            if selectedWhat == what[_OBJKEYS]:
                lObject = True

                titleText="GEEK OUT"
                moreText="VIEW"
                lFindInHackerMode=False
                if self.EDIT_MODE:
                    titleText="HACK"
                    lFindInHackerMode=True
                    moreText="HACK/CHANGE"

                selectedObjType = JOptionPane.showInputDialog(toolbox_frame_,
                                                              "Select the type of Object you want to %s" %(moreText),
                                                              "%s" %(titleText),
                                                              JOptionPane.INFORMATION_MESSAGE,
                                                              moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                              objWhat,
                                                              None)
                if not selectedObjType:
                    self.statusLabel.setText(("%s: No Object type was selected.."%(titleText)).ljust(800, " "))
                    self.statusLabel.setForeground(Color.RED)
                    return

                baseCurr = moneydance_data.getCurrencies().getBaseType()

                objects, lReportDefaultsSelected = get_the_objects_for_geekout_and_hacker_edit(objWhat, selectedObjType, self.statusLabel,"%s" %(titleText), lFindInHackerMode)
                if self.EDIT_MODE:
                    return objects
                else:
                    if objects is None:
                        return

            lSync = lOFX = lSizes = False
            if selectedWhat == what[_SYNCKEYS]: lSync = True
            if selectedWhat == what[_BANKKEYS]: lOFX = True
            if selectedWhat == what[_SIZEKEYS]: lSizes = True

            try:
                if lObject:  # selected object

                    output += "\n ====== SELECTED OBJECT's RAW PARAMETER KEYS ======\n"

                    for selectedObject in objects:                                                          # noqa
                        # noinspection PyUnresolvedReferences
                        keys=sorted(selectedObject.getParameterKeys())
                        output += "\nObject Type: %s\n" %type(selectedObject)

                        if isinstance(selectedObject, Account):
                            # noinspection PyUnresolvedReferences
                            if selectedObject.getAccountType() == Account.AccountType.ROOT:
                                output += "\n@@OBJECT IS ACCOUNT AND IT IS ROOT\n"
                            else:
                                output += "\nAccount  Type: %s\n" %selectedObject.getAccountType()

                        if isinstance(selectedObject, (ParentTxn,SplitTxn)):
                            output += "Account: %s\n" %selectedObject.getAccount()

                        for theKey in keys:
                            # noinspection PyUnresolvedReferences
                            value = selectedObject.getParameter(theKey)
                            output += pad("Key:%s" %theKey,50)+" Value: '%s'\n" %(value.strip())

                        for convertTimeStamp in ["ts", "rec_dt", "dtentered", "creation_date"]:
                            if selectedObject.getLongParameter(convertTimeStamp, 0) > 0:
                                output += "%s %s\n" % (pad("TIMESTAMP('%s'):" %(convertTimeStamp),50), get_time_stamp_as_nice_text(selectedObject.getLongParameter(convertTimeStamp, 0))  )

                        if isinstance(selectedObject, OnlineTxnList):
                            output += "\nMD User Representation of Data Held by this Account/OnlineTxnList record:\n"
                            output += " ==========================================================================  \n"
                            output += "%s %s\n" % (pad("getTxnCount():",50),                        selectedObject.getTxnCount()  )
                            output += "%s %s (%s)\n" % (pad("getOFXLastTxnUpdate():",50),           selectedObject.getOFXLastTxnUpdate(), DateUtil.convertLongDateToInt(selectedObject.getOFXLastTxnUpdate())  )
                            output += "%s %s\n" % (pad("hasOnlineAvailBalance():",50),              selectedObject.hasOnlineAvailBalance()  )
                            output += "%s %s\n" % (pad("getOnlineAvailBalance():",50),              selectedObject.getOnlineAvailBalance()  )
                            output += "%s %s (%s)\n" % (pad("getOnlineAvailBalanceDate():",50),     selectedObject.getOnlineAvailBalanceDate(), DateUtil.convertLongDateToInt(selectedObject.getOnlineAvailBalanceDate())  )
                            output += "%s %s\n" % (pad("hasOnlineLedgerBalance():",50),             selectedObject.hasOnlineLedgerBalance()  )
                            output += "%s %s\n" % (pad("getOnlineLedgerBalance():",50),             selectedObject.getOnlineLedgerBalance()  )
                            output += "%s %s (%s)\n" % (pad("getOnlineLedgerBalanceDate():",50),    selectedObject.getOnlineLedgerBalanceDate(), DateUtil.convertLongDateToInt(selectedObject.getOnlineLedgerBalanceDate())  )

                        if isinstance(selectedObject, OnlinePayeeList):
                            output += "\nMD User Representation of Data Held by this Account/OnlinePayeeList record:\n"
                            output += " ==========================================================================  \n"
                            output += "%s %s\n" % (pad("getPayeeCount():",50),             selectedObject.getPayeeCount()  )

                        if isinstance(selectedObject, OnlinePaymentList):
                            output += "\nMD User Representation of Data Held by this Account/OnlinePaymentList record:\n"
                            output += " ==========================================================================  \n"
                            output += "%s %s\n" % (pad("getPaymentCount():",50),           selectedObject.getPaymentCount()  )

                        if isinstance(selectedObject, Account):
                            try:
                                theCurr = selectedObject.getCurrencyType()
                                output += "\nMD User Representation of Data Held by this Account/Category\n"
                                output += " =============================================================\n"
                                output += "%s %s\n" % (pad("Object's Sync Type:",50),                selectedObject.getSyncItemType()  )
                                output += "%s %s\n" % (pad("Account Name:",50),                      selectedObject.getAccountName()   )
                                if selectedObject.getParentAccount() is not None:
                                    output += "%s %s\n" % (pad("Parent Account Name:",50),           selectedObject.getParentAccount().getAccountName() )
                                output += "%s %s\n" % (pad("Full Account Name:",50),                 selectedObject.getFullAccountName()                )
                                output += "%s %s\n" % (pad("Account Type:",50),                      selectedObject.getAccountType()                    )
                                output += "%s %s\n" % (pad("Account Description:",50),               selectedObject.getAccountDescription()             )
                                output += "%s %s\n" % (pad("Account Start Date:",50),                selectedObject.getCreationDateInt()                )
                                output += "%s %s\n" % (pad("Comment:",50),                           selectedObject.getComment()                        )
                                output += "%s %s\n" % (pad("Account Number (Legacy):",50),           selectedObject.getAccountNum()                     )
                                output += "%s %s\n" % (pad("Account Is Inactive:",50),               selectedObject.getAccountIsInactive()              )
                                output += "%s %s\n" % (pad("Account Or Parent Is Inactive:",50),     selectedObject.getAccountOrParentIsInactive()      )
                                output += "%s %s\n" % (pad("Hidden from Home Screen:",50),           selectedObject.getHideOnHomePage()                 )
                                output += "%s %s\n" % (pad("This Accounts Depth (from top):",50),    selectedObject.getDepth()                          )
                                output += "%s %s\n" % (pad("Parent Accounts back to Root:",50),      selectedObject.getAllAccountNames()                )
                                output += "%s %s\n" % (pad("This Acct's sub accounts:",50),          selectedObject.getSubAccounts()                    )
                                output += "%s %s\n" % (pad("Account Currency:",50),                  selectedObject.getCurrencyType()                   )
                                output += "%s %s\n" % (pad("Count of Sub Accounts:",50),             selectedObject.getSubAccountCount()                )
                                output += "%s %s\n" % (pad("Account Number:",50),                    selectedObject.getBankAccountNumber()              )
                                output += "%s %s\n" % (pad("Bank Name:",50),                         selectedObject.getBankName()                       )
                                output += "%s %s\n" % (pad("Default Category:",50),                  selectedObject.getDefaultCategory()                )
                                if selectedObject.getDefaultTransferAccount():
                                    output += "%s %s\n" % (pad("Default Transfer Acct:",50),         selectedObject.getDefaultTransferAccount()         )
                                output += "%s %s\n" % (pad("Tax related:",50),                       selectedObject.isTaxRelated()                      )
                                if selectedObject.isDeductible():
                                    output += "%s %s\n" % (pad("is Deductible:",50),                 selectedObject.isDeductible()                      )
                                if selectedObject.getTaxCategory():
                                    output += "%s %s\n" % (pad("Tax Category:",50),                 selectedObject.getTaxCategory()                     )

                                # noinspection PyUnresolvedReferences
                                if selectedObject.getAccountType() == Account.AccountType.CREDIT_CARD:
                                    output += "%s %s\n" % (pad("Card Number:",50),                  selectedObject.getCardNumber()                 )
                                    output += "%s %s\n" % (pad("Card Expiration Month:",50),        selectedObject.getCardExpirationMonth()        )
                                    output += "%s %s\n" % (pad("Card Expiation Year:",50),          selectedObject.getCardExpirationYear()         )
                                    output += "%s %s\n" % (pad("Credit Limit:",50),                 selectedObject.getCreditLimit()                )
                                    output += "%s %s\n" % (pad("APR %:",50),                        selectedObject.getAPRPercent()                 )

                                output += "%s %s\n" % (pad("Transactions within this Account:",50),  selectedObject.getTxnCount()                  )
                                output += "%s %s\n" % (pad("Unconfirmed Transactions:",50),          selectedObject.getUnconfirmedTxnCount()       )

                                if selectedObject.getReminder():
                                    output += "%s %s\n" % (pad("Reminder:",50),                      selectedObject.getReminder()                  )

                                # noinspection PyUnresolvedReferences
                                if selectedObject.getAccountType() == Account.AccountType.BANK \
                                        or selectedObject.getAccountType() == Account.AccountType.CREDIT_CARD \
                                        or selectedObject.getAccountType() == Account.AccountType.INVESTMENT:
                                    if selectedObject.isOnlineEnabled():
                                        output += "%s %s\n" % (pad("Online Enabled:",50),                selectedObject.isOnlineEnabled()                 )
                                    if selectedObject.isOnlineBankingCandidate():
                                        output += "%s %s\n" % (pad("Online Banking Candidate:",50),      selectedObject.isOnlineBankingCandidate()        )
                                    if selectedObject.isOnlineBillpayCandidate():
                                        output += "%s %s\n" % (pad("Online Bill Pay Candidate:",50),     selectedObject.isOnlineBillpayCandidate()        )
                                    if selectedObject.getBankingFI():
                                        output += "%s %s\n" % (pad("OFX Banking Service:",50),           selectedObject.getBankingFI()                    )
                                    if selectedObject.getBillPayFI():
                                        output += "%s %s\n" % (pad("OFX Bill Pay Service:",50),          selectedObject.getBillPayFI()                    )
                                    if selectedObject.getOFXAccountType():
                                        output += "%s %s\n" % (pad("OFX Account Type:",50),              selectedObject.getOFXAccountType()               )
                                    if selectedObject.getOFXAccountNumber():
                                        output += "%s %s\n" % (pad("OFX Account Number:",50),            selectedObject.getOFXAccountNumber()             )
                                    if selectedObject.getOFXBankID():
                                        output += "%s %s\n" % (pad("OFX Bank ID:",50),                   selectedObject.getOFXBankID()                    )
                                    if selectedObject.getOFXBranchID():
                                        output += "%s %s\n" % (pad("OFX Branch ID:",50),                 selectedObject.getOFXBranchID()                  )
                                    if selectedObject.getOFXBrokerID():
                                        output += "%s %s\n" % (pad("OFX Broker ID:",50),                 selectedObject.getOFXBrokerID()                  )
                                    if selectedObject.getOFXAccountKey():
                                        output += "%s %s\n" % (pad("OFX Account Key:",50),               selectedObject.getOFXAccountKey()                )
                                    if selectedObject.getOFXAccountMsgType():
                                        output += "%s %s\n" % (pad("OFX Acct Message Type:",50),         selectedObject.getOFXAccountMsgType()            )
                                    if selectedObject.getOFXBillPayAccountNumber():
                                        output += "%s %s\n" % (pad("OFX Bill Pay Acct Number:",50),      selectedObject.getOFXBillPayAccountNumber()      )
                                    if selectedObject.getOFXBillPayAccountType():
                                        output += "%s %s\n" % (pad("OFX Bill Pay Acct Type:",50),        selectedObject.getOFXBillPayAccountType()        )
                                    if selectedObject.getOFXBillPayBankID():
                                        output += "%s %s\n" % (pad("OFX Bill Pay Bank ID:",50),          selectedObject.getOFXBillPayBankID()             )

                                output += "%s %s\n" % ( pad("Start Balance:",50),                        theCurr.getDoubleValue(selectedObject.getStartBalance()))
                                output += "%s %s\n" % ( pad("Balance:",50),                              theCurr.getDoubleValue(selectedObject.getBalance()))
                                output += "%s %s\n" % ( pad("Cleared Balance:",50),                      theCurr.getDoubleValue(selectedObject.getClearedBalance()))
                                output += "%s %s\n" % ( pad("Current Balance:",50),                      theCurr.getDoubleValue(selectedObject.getCurrentBalance()))
                                output += "%s %s\n" % ( pad("Confirmed Balance:",50),                    theCurr.getDoubleValue(selectedObject.getConfirmedBalance()))
                                output += "%s %s\n" % ( pad("Reconciling Balance:",50),                  theCurr.getDoubleValue(selectedObject.getReconcilingBalance()))

                                output += "%s %s\n" % ( pad("User Start Balance:",50),                   theCurr.getDoubleValue(selectedObject.getUserStartBalance()))
                                output += "%s %s\n" % ( pad("User Balance:",50),                         theCurr.getDoubleValue(selectedObject.getUserBalance()))
                                output += "%s %s\n" % ( pad("User Cleared Balance:",50),                 theCurr.getDoubleValue(selectedObject.getUserClearedBalance()))
                                output += "%s %s\n" % ( pad("User Confirmed Balance:",50),               theCurr.getDoubleValue(selectedObject.getUserConfirmedBalance()))
                                output += "%s %s\n" % ( pad("User Current Balance:",50),                 theCurr.getDoubleValue(selectedObject.getUserCurrentBalance()))
                                output += "%s %s\n" % ( pad("User Reconciling Balance:",50),             theCurr.getDoubleValue(selectedObject.getUserReconcilingBalance()))

                                output += "%s %s\n" % ( pad("Recursive Start Balance:",50),              theCurr.getDoubleValue(selectedObject.getRecursiveStartBalance()))
                                output += "%s %s\n" % ( pad("Recursive Balance:",50),                    theCurr.getDoubleValue(selectedObject.getRecursiveBalance()))
                                output += "%s %s\n" % ( pad("Recursive Cleared Balance:",50),            theCurr.getDoubleValue(selectedObject.getRecursiveClearedBalance()))
                                output += "%s %s\n" % ( pad("Recursive Current Balance:",50),            theCurr.getDoubleValue(selectedObject.getRecursiveCurrentBalance()))
                                output += "%s %s\n" % ( pad("Recursive Reconciling Balance:",50),        theCurr.getDoubleValue(selectedObject.getRecursiveReconcilingBalance()))

                                output += "%s %s\n" % ( pad("User Recursive Start Balance:",50),         theCurr.getDoubleValue(selectedObject.getRecursiveUserStartBalance()))
                                output += "%s %s\n" % ( pad("User Recursive Balance:",50),               theCurr.getDoubleValue(selectedObject.getRecursiveUserBalance()))
                                output += "%s %s\n" % ( pad("User Recursive Cleared Balance:",50),       theCurr.getDoubleValue(selectedObject.getRecursiveUserClearedBalance()))
                                output += "%s %s\n" % ( pad("User Recursive Current Balance:",50),       theCurr.getDoubleValue(selectedObject.getRecursiveUserCurrentBalance()))
                                output += "%s %s\n" % ( pad("User Recursive Reconciling Balance:",50),   theCurr.getDoubleValue(selectedObject.getRecursiveUserReconcilingBalance()))

                                # noinspection PyUnresolvedReferences
                                if selectedObject.getAccountType() == Account.AccountType.CREDIT_CARD \
                                        or selectedObject.getAccountType() == Account.AccountType.LOAN:

                                    if selectedObject.getInstitutionName():
                                        output += "%s %s\n" % pad("Institution Name:",50),               selectedObject.getInstitutionName()
                                    if selectedObject.getInitialPrincipal():
                                        output += "%s %s\n" % (pad("Initial Principle:",50),             selectedObject.getInitialPrincipal())
                                    if selectedObject.getPermanentAPR():
                                        output += "%s %s\n" % (pad("Permanent APR:",50),                  selectedObject.getPermanentAPR())
                                    if selectedObject.getPoints():
                                        output += "%s %s\n" % (pad("%loan added as fee to Principle.:",50),selectedObject.getPoints())
                                    if selectedObject.getPaymentsPerYear():
                                        output += "%s %s\n" % (pad("Payments per year:",50),              selectedObject.getPaymentsPerYear())
                                    if selectedObject.getInterestAccount():
                                        output += "%s %s\n" % (pad("Interest Account:",50),               selectedObject.getInterestAccount())
                                    if selectedObject.getEscrowAccount():
                                        output += "%s %s\n" % (pad("Escrow Account:",50),                selectedObject.getEscrowAccount())
                                    if selectedObject.getEscrowPayment():
                                        output += "%s %s\n" % (pad("Escrow Payment:",50),                selectedObject.getEscrowPayment())
                                    if selectedObject.getInterestRate():
                                        output += "%s %s\n" % (pad("Interest Rate:",50),                 selectedObject.getInterestRate())
                                    if selectedObject.getFixedMonthlyPaymentAmount():
                                        output += "%s %s\n" % (pad("Fixed Payment Amt:",50),             selectedObject.getFixedMonthlyPaymentAmount())
                                    if selectedObject.getRateChangeDate():
                                        output += "%s %s\n" % (pad("Date Rate  Changed:",50),            selectedObject.getRateChangeDate())
                                    if selectedObject.getDebtPaymentAmount():
                                        output += "%s %s\n" % (pad("Val Pmts made to this CC:",50),      selectedObject.getDebtPaymentAmount())
                                    if selectedObject.getDebtPaymentProportion():
                                        output += "%s %s\n" % (pad("%value Pmts made to this cc:",50),   selectedObject.getDebtPaymentProportion())
                                    if selectedObject.getDebtPaymentSpec():
                                        output += "%s %s\n" % (pad("Pmt  Plan Used:",50),                selectedObject.getDebtPaymentSpec())

                                    if selectedObject.getPaymentSchedule():
                                        output += "%s %s\n" % (pad("Payment Schedule:",50),               selectedObject.getPaymentSchedule())
                                    if selectedObject.hasExpiringRate():
                                        output += "%s %s\n" % (pad("Has Expiring Rate:",50),              selectedObject.hasExpiringRate())
                                    if selectedObject.getCalcPmt():
                                        output += "%s %s\n" % (pad("Calc Payment:",50),                   selectedObject.getCalcPmt())

                                if selectedObject.getInvestAccountNumber():
                                    output += "%s %s\n" % (pad("Investment Account Number:",50),          selectedObject.getInvestAccountNumber())

                                # noinspection PyUnresolvedReferences
                                if selectedObject.getAccountType() == Account.AccountType.SECURITY:
                                    if selectedObject.getBroker():
                                        output += "%s %s\n" % (pad("Broker:",50),                           selectedObject.getBroker())
                                    if selectedObject.getBrokerPhone():
                                        output += "%s %s\n" % (pad("Broker Phone:",50),                     selectedObject.getBrokerPhone())
                                    if selectedObject.getInvstCommissionAcct():
                                        output += "%s %s\n" % (pad("Investment Commission Account",50),     selectedObject.getInvstCommissionAcct())
                                    if selectedObject.getAnnualFee():
                                        output += "%s %s\n" % (pad("Annual Fee:",50),                       selectedObject.getAnnualFee())
                                    if selectedObject.getDividend():
                                        output += "%s %s\n" % (pad("Dividend:",50),                         selectedObject.getDividend())
                                    if selectedObject.getUsesAverageCost():
                                        output += "%s %s\n" % (pad("Uses Average Cost:",50),                selectedObject.getUsesAverageCost())
                                    if selectedObject.getSecurityType():
                                        output += "%s %s\n" % (pad("Security Type:",50),                    selectedObject.getSecurityType())
                                    if selectedObject.getSecuritySubType():
                                        output += "%s %s\n" % (pad("`Security Sub Type`:",50),              selectedObject.getSecuritySubType())
                                    if selectedObject.getBondType():
                                        output += "%s %s\n" % (pad("Bond Type:",50),                        selectedObject.getBondType())
                                    if selectedObject.getMaturity():
                                        output += "%s %s\n" % (pad("Maturity:",50),                         selectedObject.getMaturity())
                                    if selectedObject.getNumYears():
                                        output += "%s %s\n" % (pad("Maturity Year (6=six Mnths):",50),      selectedObject.getNumYears())
                                    if selectedObject.getCompounding():
                                        output += "%s %s\n" % (pad("CD Compounding:",50),                   selectedObject.getCompounding())
                                    if selectedObject.getOptionPrice():
                                        output += "%s %s\n" % (pad("Option Price:",50),                     selectedObject.getOptionPrice())
                                    if selectedObject.getMonth():
                                        output += "%s %s\n" % (pad("Option Exercise Month (0-11 3rd Fri):",50),selectedObject.getMonth())
                                    if selectedObject.getStrikePrice():
                                        output += "%s %s\n" % (pad("Option Strike Price:",50),               selectedObject.getStrikePrice())
                                    if selectedObject.getPut():
                                        output += "%s %s\n" % (pad("Option Put(T), Call(F):",50),           selectedObject.getPut())
                                    if selectedObject.getEscrow():
                                        output += "%s %s\n" % (pad("Escrow?:",50),                          selectedObject.getEscrow())
                                    if selectedObject.getExchange():
                                        output += "%s %s\n" % (pad("Trading Platform:",50),                 selectedObject.getExchange())
                                    if selectedObject.getFaceValue():
                                        output += "%s %s\n" % (pad("Bond face value:",50),                  selectedObject.getFaceValue())

                            except:
                                output += dump_sys_error_to_md_console_and_errorlog( True )

                        elif isinstance(selectedObject, CurrencyType):
                            try:
                                output += "\nMD User Representation of Data Held by this Currency/Security\n"
                                output += " =============================================================-\n"
                                if selectedObject == baseCurr:                                                              # noqa
                                    output += "THIS IS THE BASE RATE!\n"
                                output += "%s %s\n" % (pad("Sync Item Type:",50),       selectedObject.getSyncItemType()  )
                                output += "%s %s\n" % (pad("Currency Type:",50),        selectedObject.getCurrencyType()  )
                                output += "%s %s\n" % (pad("Name:",50),                 selectedObject.getName()  )
                                output += "%s %s\n" % (pad("Hide in UI?:",50),          selectedObject.getHideInUI()  )
                                output += "%s %s\n" % (pad("ID:",50),                   selectedObject.getID()  )
                                output += "%s %s\n" % (pad("ID String:",50),            selectedObject.getIDString()  )
                                output += "%s %s\n" % (pad("Ticker Symbol:",50),        selectedObject.getTickerSymbol()  )
                                output += "%s %s\n" % (pad("Prefix:",50),               selectedObject.getPrefix()  )
                                output += "%s %s\n" % (pad("Suffix:",50),               selectedObject.getSuffix()  )
                                output += "%s %s\n" % (pad("Decimal Places:",50),       selectedObject.getDecimalPlaces()  )
                                output += "%s %s\n" % (pad("Curr Start Date:",50),      selectedObject.getEffectiveDateInt()  )
                                output += "%s %s\n" % (pad("RATE:",50),                 selectedObject.getRate(None)  )
                                output += "%s %s\n" % (pad("RATE Inverted:",50),        1/selectedObject.getRate(None)  )
                                output += "%s %s\n" % (pad("RATE in terms of Base:",50),selectedObject.getBaseRate()  )
                                output += "%s %s\n" % (pad("Relative Currency:",50),    selectedObject.getRelativeCurrency()  )
                                output += "%s %s\n" % (pad("Relative Rate:",50),        selectedObject.getRelativeRate()  )
                                output += "%s %s\n" % (pad("Count Price History:",50),  len(selectedObject.getSnapshots()  ))
                                output += "%s %s\n" % (pad("Count Stock Splits:",50),   len(selectedObject.getSplits()  ))
                                output += "%s %s\n" % (pad("Daily Change:",50),         selectedObject.getDailyChange()  )
                                output += "%s %s\n" % (pad("Daily Volume:",50),         selectedObject.getDailyVolume()  )
                                output += "<END>\n"
                            except:
                                output += dump_sys_error_to_md_console_and_errorlog( True )

                        elif isinstance(selectedObject, ReportSpec):

                            if lReportDefaultsSelected:
                                LS = moneydance_ui.getCurrentAccounts().getBook().getLocalStorage()
                                keys=sorted(LS.keys())

                                found_any = False
                                for theKey in keys:
                                    value = LS.get(theKey)
                                    if not theKey.lower().startswith("report_params."+selectedObject.getReportGenerator().getShortID()): continue
                                    if not found_any:
                                        output += "\nDEFAULT REPORT PARAMETERS (SET BY USER):\n"
                                        found_any = True
                                    output += "Key:%s Value: %s\n" % (pad(theKey,70), value.strip())
                        elif isinstance(selectedObject, Reminder):
                            pass
                        elif isinstance(selectedObject, AddressBookEntry):
                            pass
                        elif isinstance(selectedObject, OnlineService):
                            pass

                if selectedWhat == what[_PREFKEYS] or lSync or lOFX or lSizes or lSearch:  # User  Preferences

                    output += "\n ====== USER PREFERENCES LOADED INTO MEMORY (May or may not be quite the same as config.dict) ======\n"

                    # This bit below is really, really cool!!!! But I am not using it as it only gets pre-defined settings from config.dict.
                    # prefs=[]
                    # what_x = moneydance_ui.getPreferences()
                    # members = [attr for attr in dir(what_x) if not callable(getattr(what_x, attr)) and not attr.startswith("__")]
                    # for mem in members:
                    #     if not mem.upper() == mem: continue
                    #     try:
                    #         convertKey = getattr(UserPreferences, mem)
                    #     except:
                    #         continue
                    #     if not convertKey or convertKey=="" : continue
                    #     value = moneydance_ui.getPreferences().getSetting(getattr(UserPreferences, mem))
                    #     if value: prefs.append([convertKey, mem, value])
                    # prefs =sorted(prefs) # Sort the result (as the input is only a reference to a reference)

                    # As all settings in memory actually come from config.dict (or go back to config.dict) then we look there instead to get the keys
                    st,tk = read_preferences_file(lSaveFirst=True)  # Must flush memory to disk first before we read the file....
                    prefs=sorted(tk)

                    for theKey in prefs:
                        value = st.get(theKey)
                        if lSync and not ("sync" in theKey.lower()): continue
                        if lOFX and not ("ofx" in theKey.lower() or "ol." in theKey.lower() or "olb." in theKey.lower()): continue
                        if lSizes and not check_for_window_display_data(theKey,value): continue
                        if lSearch:
                            myTestValue = value
                            if not isinstance(myTestValue,(str,unicode)): myTestValue  = repr(myTestValue)  # Force the StreamTable / StreamVector into a string for search comparison
                            # noinspection PyUnresolvedReferences
                            if lKeys and not (searchWhat.lower() in theKey.lower()): continue
                            elif lKeyData and not (searchWhat.lower() in myTestValue.lower()): continue
                        # noinspection PyUnresolvedReferences
                        output += (pad("Key:%s" % (theKey),35)+ " Value: %s\n" %((value)))


                if selectedWhat == what[_ROOTKEYS] or lSync or lOFX or lSizes or lSearch:  # ROOT

                    keys=sorted(root.getParameterKeys())
                    output += '\n ====== ROOT PARAMETER KEYS (Preferences will mostly be in Local Storage) ======\n'
                    for theKey in keys:

                        value = root.getParameter(theKey)

                        if lSync and ("sync" not in theKey.lower()): continue
                        if lOFX and not ("ofx" in theKey.lower() or "ol." in theKey.lower() or "olb." in theKey.lower()): continue
                        if lSizes and not check_for_window_display_data(theKey,value): continue
                        if lSearch:
                            if lKeys and not (searchWhat.lower() in theKey.lower()): continue
                            elif lKeyData and not (searchWhat.lower() in value.lower()): continue
                        if theKey.lower() == "netsync.synckey": value = "<*****>"
                        output += pad("Key:%s" %theKey,50)+" Value: %s\n" %(value.strip())

                    if selectedWhat == what[_ROOTKEYS]:
                        output+="\n"
                        for convertTimeStamp in ["ts", "rec_dt", "dtentered", "creation_date"]:
                            if root.getLongParameter(convertTimeStamp, 0) > 0:
                                output += "%s %s\n" % (pad("TIMESTAMP('%s'):" %(convertTimeStamp),50), get_time_stamp_as_nice_text(root.getLongParameter(convertTimeStamp, 0))  )

                if selectedWhat == what[_BOOKKEYS] or lSync or lOFX or lSizes or lSearch:  # Local Storage

                    output += '\n ====== BOOK>LOCAL STORAGE KEYS ======\n'
                    LS = moneydance_ui.getCurrentAccounts().getBook().getLocalStorage()
                    keys=sorted(LS.keys())

                    last = None
                    for theKey in keys:
                        value = LS.get(theKey)    # NOTE: .get loses the underlying type and thus becomes a string
                        if lSync and "sync" not in theKey.lower(): continue
                        if lOFX and not ("ofx" in theKey.lower() or "ol." in theKey.lower() or "olb." in theKey.lower()): continue
                        if lSizes and not check_for_window_display_data(theKey,value): continue
                        if lSearch:
                            if lKeys and not (searchWhat.lower() in theKey.lower()): continue
                            elif lKeyData and not (searchWhat.lower() in value.lower()): continue

                        if theKey.lower() == "netsync.synckey": value = "<*****>"

                        splitKey = theKey.split('.')
                        if splitKey[0] != last:
                            last = splitKey[0]
                            lookupAcct = moneydance_data.getAccountByUUID(splitKey[0])
                            if lookupAcct:
                                output += ("\n>> Account: %s\n" %(lookupAcct.getFullAccountName()))
                            else:
                                output += "\n"

                        output += pad("Key:%s" %theKey,70)+" Value: %s\n" %(value.strip())

                if selectedWhat == what[_ACCTKEYS] or lSync or lOFX or lSizes or lSearch:  # Accounts (excluding Root)

                    output += "\n ====== ACCOUNTS' PARAMETER KEYS  (Preferences will mostly be in Local Storage) ======\n"
                    accounts = AccountUtil.allMatchesForSearch(moneydance_data, MyAcctFilter(5))
                    lastAcct = None
                    for acct in accounts:

                        if acct != lastAcct:
                            output += "\n>> Account: %s\n" %acct.getFullAccountName()
                            lastAcct = acct

                        if lOFX:
                            output += "\nSpecific OFX Data:\n"
                            if (acct.canDownloadTxns() and not acct.getAccountIsInactive()):
                                output += pad(">> Can Download Txns:",50)+str(acct.canDownloadTxns() and not acct.getAccountIsInactive())+"\n"

                            if acct.getBankingFI() is not None:
                                output += pad(">> Bank Service/Logon profile:",50)+str(acct.getBankingFI())+"\n"

                            if acct.getBillPayFI() is not None:
                                output += pad(">> BillPay Service/Logon profile:",50)+str(acct.getBillPayFI())+"\n"

                            getOnlineData = MyGetDownloadedTxns(acct)
                            if getOnlineData is not None:
                                output += (">> OnlineTxnList data:\n")
                                for _k in sorted(getOnlineData.getParameterKeys()):
                                    _v = getOnlineData.getParameter(_k)
                                    output += pad("  >> Key:%s" %(_k),50)+" Value: %s\n" %(_v.strip())
                                for convertTimeStamp in ["ts", "ofx_last_txn_update", "ol.ledgerbalasof"]:
                                    if getOnlineData.getLongParameter(convertTimeStamp, 0) > 0:
                                        output += "%s %s\n" % (pad("   >> TIMESTAMP('%s'):" %(convertTimeStamp),50), get_time_stamp_as_nice_text(getOnlineData.getLongParameter(convertTimeStamp, 0))  )

                            getOnlineData = MyGetOnlinePayees(acct)
                            if getOnlineData is not None:
                                output += (">> OnlinePayees data:\n")
                                for _k in sorted(getOnlineData.getParameterKeys()):
                                    _v = getOnlineData.getParameter(_k)
                                    output += pad("  >> Key:%s" %(_k),50)+" Value: %s\n" %(_v.strip())
                                for convertTimeStamp in ["ts", "ofx_last_txn_update", "ol.ledgerbalasof"]:
                                    if getOnlineData.getLongParameter(convertTimeStamp, 0) > 0:
                                        output += "%s %s\n" % (pad("   >> TIMESTAMP('%s'):" %(convertTimeStamp),50), get_time_stamp_as_nice_text(getOnlineData.getLongParameter(convertTimeStamp, 0))  )

                            getOnlineData = MyGetOnlinePayments(acct)
                            if getOnlineData is not None:
                                output += (">> OnlinePayments data:\n")
                                for _k in sorted(getOnlineData.getParameterKeys()):
                                    _v = getOnlineData.getParameter(_k)
                                    output += pad("  >> Key:%s" %(_k),50)+" Value: %s\n" %(_v.strip())
                                for convertTimeStamp in ["ts", "ofx_last_txn_update", "ol.ledgerbalasof"]:
                                    if getOnlineData.getLongParameter(convertTimeStamp, 0) > 0:
                                        output += "%s %s\n" % (pad("   >> TIMESTAMP('%s'):" %(convertTimeStamp),50), get_time_stamp_as_nice_text(getOnlineData.getLongParameter(convertTimeStamp, 0))  )

                            output += "\n"

                        keys = sorted(acct.getParameterKeys())
                        for theKey in keys:

                            value = acct.getParameter(theKey)
                            if lSync and not ("sync" in theKey.lower()): continue
                            if lOFX and not ("ofx" in theKey.lower() or "ol." in theKey.lower() or "olb." in theKey.lower()): continue
                            if lSizes and not check_for_window_display_data(theKey,value): continue
                            if lSearch:
                                if lKeys and not (searchWhat.lower() in theKey.lower()): continue
                                elif lKeyData and not (searchWhat.lower() in value.lower()): continue

                            if theKey.lower() == "netsync.synckey": value = "<*****>"
                            if theKey.lower() == "bank_account_number": value = "<*****>"

                            if lOFX and value.strip() == "": continue

                            output += pad("Key:%s" %(theKey),50)+" Value: %s\n" %(value.strip())

                        if selectedWhat == what[_ACCTKEYS]:
                            output+="\n"
                            for convertTimeStamp in ["ts", "rec_dt", "dtentered", "creation_date"]:
                                if acct.getLongParameter(convertTimeStamp, 0) > 0:
                                    output += "%s %s\n" % (pad("TIMESTAMP('%s'):" %(convertTimeStamp),50), get_time_stamp_as_nice_text(acct.getLongParameter(convertTimeStamp, 0))  )

                if lOFX or lSearch:
                    output += "\n ========= OFX Online Banking Service ' PARAMETER KEYS =========\n"
                    output += "\n (NOTE: More information will be in view bank service / login profiles)\n"

                    lastService = None
                    services = moneydance_data.getOnlineInfo().getAllServices()
                    for service in services:
                        keys = sorted(service.getParameterKeys())
                        for theKey in keys:

                            value = service.getParameter(theKey)

                            if lSearch:
                                if lKeys and not (searchWhat.lower() in theKey.lower()): continue
                                elif lKeyData and not (searchWhat.lower() in value.lower()): continue

                            if service != lastService:
                                output += "\nOFX SERVICE: %s\n" %service
                                output += "--------------------------------------------\n"
                                lastService = service

                            output += pad("Key:%s" %theKey,50)+ " Value: %s\n" %(value)

                if selectedWhat == what[_OSPROPS]:  # System.Properties

                    output += "\n ====== (Operating) System.Properties.....======\n"

                    props = sorted(System.getProperties())
                    for prop in props:
                        output += pad("Property:%s" %prop,50)+ " Value: %s\n"%(System.getProperty(prop))

                if selectedWhat == what[_OSENV]:    # Environment variables

                    output += "\n ====== Operating System Environment Variables.....======\n"

                    for k, v in os.environ.items():
                        output += pad("Variable: %s" %k,50)+ " Value: %s\n" %(v)

            except:
                output += dump_sys_error_to_md_console_and_errorlog( True )

            output += "<END>\n"

            jif=QuickJFrame("Geek Out on....: %s" % selectedWhat, output).show_the_frame()

            if self.lOFX:
                return jif
            else:
                self.statusLabel.setText(("I hope you enjoyed Geeking Out on...: %s" % selectedWhat).ljust(800, " "))
                self.statusLabel.setForeground(DARK_GREEN)

            myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
            return

    def prune_internal_backups(statusLabel, lStartup=False):
        myPrint("D","In ", inspect.currentframe().f_code.co_name, "()")

        myPrint("J","Auto-prune is enabled.... auto-pruning internal backups of config.dict and settings now.....")

        try:

            backup_extn = "_$SAVED$"

            backup_localStorage_path = os.path.join(moneydance_data.getRootFolder().getCanonicalPath())
            backup_config_path = os.path.dirname(Common.getPreferencesFile().getCanonicalPath())
            # backup_custom_theme_path = os.path.dirname(theme.Theme.customThemeFile.getCanonicalPath())

            settingsFile = "settings"
            # backup_localStorage_filename = os.path.join(moneydance_data.getRootFolder().getAbsolutePath(),"settings")
            # configFile = Common.getPreferencesFile().getName()
            # themeFile = theme.Theme.customThemeFile.getName()

            themeFiles = []
            configFiles = []
            settingsFiles = []

            iCountConfig = iCountSettings = iCountTheme = 0

            for _path in [backup_localStorage_path, backup_config_path]:
                for _file in os.listdir(_path):
                    filepath = os.path.join(_path, _file)
                    if _file.startswith(settingsFile) and _file.endswith(backup_extn):
                        settingsFiles.append(filepath)
                        iCountSettings+=1
                    elif _file.startswith("config-") and _file.endswith(".dict"+backup_extn):
                        configFiles.append(filepath)
                        iCountConfig+=1
                    elif _file.startswith("custom_theme-") and _file.endswith(".properties"+backup_extn):
                        themeFiles.append(filepath)
                        iCountTheme+=1
                    else:
                        pass

            myPrint("DB", "Found %s settings backup files" %(iCountSettings))
            myPrint("DB", "Found %s config.dict backup files" %(iCountConfig))
            myPrint("DB", "Found %s custom themes backup files" %(iCountTheme))

            settingsFiles = sorted(settingsFiles, key=lambda _x: (os.path.getmtime(_x)), reverse=True)
            configFiles = sorted(configFiles, key=lambda _x: (os.path.getmtime(_x)), reverse=True)
            themeFiles = sorted(themeFiles, key=lambda _x: (os.path.getmtime(_x)), reverse=True)

            files_to_keep = 5
            days_to_look_back = 5

            lookBack = datetime.datetime.today() - datetime.timedelta(days=(days_to_look_back+1))

            myPrint("DB", "Look-back cutoff date for auto-prune internal backup files set to: %s " %(get_time_stamp_as_nice_text(lookBack)))

            iDeletedConfig = iDeletedThemes = iDeletedSettings = 0

            iErrors=0
            for filelist in [settingsFiles, configFiles, themeFiles]:
                iRecords=0
                for _fp in filelist:
                    iRecords += 1
                    if iRecords <= files_to_keep:
                        myPrint("D", "skipping-keeping %s files: %s %s" %(files_to_keep,datetime.datetime.fromtimestamp(os.path.getmtime(_fp)).strftime('%Y-%m-%d %H:%M:%S'),_fp))
                        continue
                    file_ts = datetime.datetime.fromtimestamp(os.path.getmtime(_fp))
                    if file_ts >= lookBack:
                        myPrint("D","skipping < %s days: %s %s" %(days_to_look_back, file_ts.strftime('%Y-%m-%d %H:%M:%S'),_fp))
                        continue
                    myPrint("DB", "DELETING: %s %s" %(file_ts.strftime('%Y-%m-%d %H:%M:%S'),_fp))
                    if "settings" in _fp:
                        iDeletedSettings+=1
                    elif "config-" in _fp:
                        iDeletedConfig+=1
                    elif "custom_theme-" in _fp:
                        iDeletedThemes+=1
                    try:
                        os.remove(_fp)
                    except:
                        iErrors+=1
                        myPrint("B","@ERROR deleting file: %s - skipping and moving on....." %(_fp))
                        dump_sys_error_to_md_console_and_errorlog()
        except:
            myPrint("B","@@ ERROR auto-pruning internal backup files... continuing.....")
            statusLabel.setText(("@@ ERROR auto-pruning internal backup files... continuing.....").ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            dump_sys_error_to_md_console_and_errorlog()
            return

        del themeFiles
        del configFiles
        del settingsFiles

        myPrint("J","Auto-prune of internal backups completed - deleted %s config.dict, %s settings and %s custom_theme files (with %s errors)..."
                %(iDeletedConfig,iDeletedSettings,iDeletedThemes,iErrors))

        if not lStartup:
            statusLabel.setText(("Auto-prune of internal backups completed - deleted %s config.dict, %s settings and %s custom_theme files (with %s errors)..." %(iDeletedConfig,iDeletedSettings,iDeletedThemes,iErrors)).ljust(800, " "))
            statusLabel.setForeground(Color.RED)

        if iErrors:
            myPopupInformationBox(toolbox_frame_, "Auto-prune of internal backups completed - deleted %s config.dict, %s settings and %s custom_theme files (with %s errors)..."
                                  %(iDeletedConfig,iDeletedSettings,iDeletedThemes,iErrors),
                                  "AUTO-PRUNE INTERNAL BACKUPS",
                                  JOptionPane.ERROR_MESSAGE)

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
        return

    class ViewFileButtonAction(AbstractAction):

        class CloseAction(AbstractAction):

            def __init__(self, the_frame):
                self.theFrame = the_frame

            # noinspection PyUnusedLocal
            def actionPerformed(self, event):
                global debug
                myPrint("DB", "Inner View File Frame shutting down....")
                self.theFrame.dispose()
                return

        def __init__(self, statusLabel, theFile, displayText, lFile=True):
            self.statusLabel = statusLabel
            self.theFile = theFile
            self.displayText = displayText
            self.lFile = lFile

        def actionPerformed(self, event):
            global toolbox_frame_, debug, myParameters, lIgnoreOutdatedExtensions_TB
            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

            lViewExtensions=False
            lDisplayPickle=False

            x = str(self.theFile)

            if x == "display_pickle()":
                x = display_pickle()
                lDisplayPickle=True

            if x == "display_help()":
                x = display_help()

            if x == "get_list_memorised_reports()":
                x = get_list_memorised_reports()

            if x == "get_register_txn_sort_orders()":
                x = get_register_txn_sort_orders()

            if x == "view_check_num_settings()":
                x = view_check_num_settings(self.statusLabel)

            if x == "view_extensions_details()":
                x = view_extensions_details()
                lViewExtensions=True

            if x == "can_I_delete_security()":
                x = can_I_delete_security(self.statusLabel)
                if not x: return

            if x == "list_security_currency_decimal_places()":
                x = list_security_currency_decimal_places(self.statusLabel)
                if not x: return

            if x == "diagnose_currencies(False)":
                x = diagnose_currencies(self.statusLabel, False)
                if not x: return

            if x == "diagnose_currencies(True)":
                x = diagnose_currencies(self.statusLabel, True)
                if not x: return

            if not self.lFile:
                myPrint("DB", "User requested to view " + self.displayText + "data!")
                if not x or x == "":
                    if x:
                        self.statusLabel.setText(("Sorry - " + self.displayText + " data is empty!?: " + x).ljust(800, " "))
                        self.statusLabel.setForeground(Color.RED)
                    return
            else:
                myPrint("DB", "User requested to view " + self.displayText + "file!")
                if not os.path.exists(x):
                    self.statusLabel.setText(("Sorry - " + self.displayText + " file does not exist or is not available to view!?: " + x).ljust(800, " "))
                    self.statusLabel.setForeground(Color.RED)
                    return

            if not self.lFile:
                displayFile = x
            else:
                try:
                    with open(x, "r") as myFile:
                        displayFile = myFile.readlines()
                    # displayFile = '\n'.join(displayFile)

                    # If VMOptions, stick a "'" at the beginning for clipboard to Excel to work OK
                    if lCopyAllToClipBoard_TB and x.lower().endswith(".vmoptions"):
                        newDisplayFile=[]
                        for line in displayFile:
                            line ="'"+line
                            newDisplayFile.append(line)
                        displayFile = newDisplayFile
                    else:
                        displayFile.append("\n<END>")

                    displayFile = ''.join(displayFile)
                except:
                    displayFile = "Sorry - error opening file...."
                    dump_sys_error_to_md_console_and_errorlog()

            if x.lower().endswith(".vmoptions"):
                displayFile += """
-------------------------------------------------------------------------------------------------------------------------------------------
<INSTRUCTIONS - MEMORY>
======================
You can allow for more memory by editing the 'Moneydance.vmoptions' file and set it to increase the amount of memory that
Moneydance is allowed to use. To achieve this you can try the following:

Navigate to the Moneydance.vmoptions file, located in the folder where Moneydance is installed:

If you open that file with Notepad or any other text editor, you'll see some instructions for how to change it.
Close Moneydance first!

The basic recommendation is to changing the -Xmx1024m setting to -Xmx2048m which doubles the amount of memory that Moneydance is allowed to use.
You can give it more if you wish, E.g.: you make it -Xmx3000m, for optimal results.

NOTE: The limit is set deliberately low to enable it to work with computers having very small amounts of RAM.

"""  # noqa
                windowsExtra = """
-----
Windows file location: c:\Program Files\Moneydance\Moneydance.vmoptions

In Windows - due to permissions, you will need to do this:
In the 'Type here to Search' box on the Windows 10 Toolbar, type CMD (do not press enter)
When Command Prompt appears, click Run as Administrator
Click yes/agree to allow this app to make changes to this device / grant administrator permissions
cd "\Program Files\Moneydance"      (and enter)
notepad Moneydance.vmoptions        (and enter)
edit the file and change the -Xmx1024 setting
ctrl-s to save and then exit Notepad
exit
restart Moneydance
-------------------------------------------------------------------------------------------------------------------------------------------
"""  # noqa

                linuxExtra = """
<INSTRUCTIONS - Linux and High Resolution Screens>
=================================================
When running Linux on a computer with a high resolution display, some distributions will let you adjust the "scaling" of 
the interface to provide clearer graphics at a larger size. If you use scaling on your Linux desktop but the contents of
the Moneydance window appears very small then you may need to adjust Moneydance's scaling.

To change the scaling, open Moneydance.vmoptions with a text editor (as per instructions below) add the following two
lines to the bottom of the file:

-Dsun.java2d.uiScale=2
-Dsun.java2d.uiScale.enabled=true

>>PLEASE NOTE: that as of this writing, non-integer scales (for example, 1.2) are not supported.
refer: https://infinitekind.tenderapp.com/kb/linux/linux-and-hidpi-high-resolution-screens

-----
Linux file location: /opt/Moneydance/Moneydance.vmoptions

In Linux - due to permissions, you will need to do this:
a) Either edit in Terminal using sudo before the command (e.g. sudo vi Moneydance.vmoptions) , or;

b) You ideally need to be able to open files as root via a right click.
- This assumes you are on a Debian based system
1. Open the Terminal
2. Type sudo su and press enter. Provide your password and press enter
3. Then type apt-get install -y nautilus-admin and press enter
4. Now type nautilus -q and press enter
5. Finally type exit and press enter, and close the terminal window
6. All set. Now when you want to open a file as root, simply right click the FOLDER and select Open as Root (or Administrator).

So, now find the /Opt folder, right click on the Moneydance FOLDER, Open as Root. Enter your password. Now you can edit the Moneydance.vmoptions file....
>> Note: You may need to logoff and then login to see the changes!

now after saving the file, restart Moneydance
-------------------------------------------------------------------------------------------------------------------------------------------
"""  # noqa
                if Platform.isWindows():
                    displayFile += windowsExtra
                elif Platform.isUnix():
                    displayFile += linuxExtra
                try:
                    helper = moneydance.getPlatformHelper()
                    helper.openDirectory(self.theFile)
                except:
                    pass
                time.sleep(0.5)

            if self.lFile:
                jif = QuickJFrame("View " + self.displayText + " file: " + x, displayFile).show_the_frame()
            else:
                jif = QuickJFrame("View " + self.displayText + " data", displayFile).show_the_frame()

            jif.toFront()

            if lViewExtensions and lIgnoreOutdatedExtensions_TB:
                if myPopupAskQuestion(jif,
                                      "OUTDATED EXTENSIONS",
                                      "Turn startup warnings back on for Outdated Extns?",
                                      JOptionPane.YES_NO_OPTION,
                                      JOptionPane.QUESTION_MESSAGE):

                    self.statusLabel.setText(("OUTDATED EXTENSIONS - Startup warnings re-enabled").ljust(800, " "))
                    self.statusLabel.setForeground(Color.BLUE)
                    myPrint("B", "OUTDATED EXTENSIONS - Startup warnings re-enabled" )
                    lIgnoreOutdatedExtensions_TB = False

            if lDisplayPickle:

                if not myPopupAskQuestion(jif,
                                          "STUWARESOFTSYSTEMS' SAVED PARAMETERS PICKLE FILE",
                                          "Would you like to RESET/DELETE/EDIT saved parameters?",
                                          JOptionPane.YES_NO_OPTION,
                                          JOptionPane.WARNING_MESSAGE):
                    return

                _PICKLEDELALL          = 0
                _PICKLECHGONE          = 1
                _PICKLEDELONE          = 2
                _PICKLEADDONE          = 3

                what = ["PICKLE: DELETE ALL","PICKLE: CHANGE one variable","PICKLE: DELETE one variable", "PICKLE: ADD one variable"]

                while True:

                    lAdd = lChg = lDelAll = lDelOne = False
                    selectedWhat = JOptionPane.showInputDialog(jif,
                                                               "Select the type of change you want to make?",
                                                               "STUWARESOFTSYSTEMS' SAVED PARAMETERS PICKLE FILE",
                                                               JOptionPane.WARNING_MESSAGE,
                                                               None,
                                                               what,
                                                               None)

                    if not selectedWhat:
                        try:
                            save_StuWareSoftSystems_parameters_to_file()
                        except:
                            myPrint("B", "Error - failed to save parameters to pickle file...!")
                            dump_sys_error_to_md_console_and_errorlog()
                        return

                    if selectedWhat == what[_PICKLEADDONE]: lAdd = True
                    if selectedWhat == what[_PICKLECHGONE]: lChg = True
                    if selectedWhat == what[_PICKLEDELONE]: lDelOne = True
                    if selectedWhat == what[_PICKLEDELALL]: lDelAll = True

                    if lDelAll:
                        myParameters = {}
                        self.statusLabel.setText(("STUWARESOFTSYSTEMS' PARAMETERS SAVED TO PICKLE FILE DELETED/RESET").ljust(800, " "))
                        self.statusLabel.setForeground(DARK_GREEN)
                        myPrint("B", "STUWARESOFTSYSTEMS' PARAMETERS SAVED TO PICKLE FILE DELETED/RESET" )

                        try:
                            save_StuWareSoftSystems_parameters_to_file()
                        except:
                            myPrint("B", "Error - failed to save parameters to pickle file...!")
                            dump_sys_error_to_md_console_and_errorlog()
                        return

                    text = ""
                    if lChg: text = "CHANGE"
                    if lDelOne: text = "DELETE"

                    if lAdd:
                        addKey = myPopupAskForInput(jif,
                                                    "PICKLE: ADD KEY",
                                                    "KEY NAME:",
                                                    "Carefully enter the name of the key you want to add (cAseMaTTers!) - STRINGS ONLY:",
                                                    "",
                                                    False,
                                                    JOptionPane.WARNING_MESSAGE)

                        if not addKey or len(addKey.strip()) < 1: continue
                        addKey = addKey.strip()

                        if not check_if_key_string_valid(addKey):
                            myPopupInformationBox(jif, "ERROR: Key %s is NOT valid!" % addKey, "PICKLE: ADD", JOptionPane.ERROR_MESSAGE)
                            continue    # back to menu

                        testKeyExists = myParameters.get(addKey)

                        if testKeyExists:
                            myPopupInformationBox(jif, "ERROR: Key %s already exists - cannot add - aborting..!" % addKey, "PICKLE: ADD", JOptionPane.ERROR_MESSAGE)
                            continue    # back to menu

                        addValue = myPopupAskForInput(jif,
                                                      "PICKLE: ADD KEY VALUE",
                                                      "KEY VALUE:",
                                                      "Carefully enter the key value you want to add (STRINGS ONLY!):",
                                                      "",
                                                      False,
                                                      JOptionPane.WARNING_MESSAGE)

                        if not addValue or len(addValue.strip()) <1: continue
                        addValue = addValue.strip()

                        if not check_if_key_data_string_valid(addValue):
                            myPopupInformationBox(toolbox_frame_, "ERROR: Key value %s is NOT valid!" % addValue, "PICKLE: ADD ", JOptionPane.ERROR_MESSAGE)
                            continue    # back to menu

                        myParameters[addKey] = addValue
                        myPrint("B","@@ PICKLEMODE: key: %s value: %s added @@" %(addKey,addValue))
                        myPopupInformationBox(jif,
                                              "SUCCESS: Key %s added!" % (addKey),
                                              "PICKLE: ADD ",
                                              JOptionPane.WARNING_MESSAGE)
                        continue

                    pickleKeys=sorted( myParameters.keys() )
                    # OK, so we are changing or deleting
                    if lChg or lDelOne:
                        selectedKey = JOptionPane.showInputDialog(jif,
                                                                  "Select the key/setting you want to %s" % (text),
                                                                  "PICKLE",
                                                                  JOptionPane.WARNING_MESSAGE,
                                                                  None,
                                                                  pickleKeys,
                                                                  None)
                        if not selectedKey: continue

                        value = myParameters.get(selectedKey)
                        chgValue = None

                        if lChg:
                            chgValue = myPopupAskForInput(jif,
                                                          "PICKLE: CHANGE KEY VALUE",
                                                          "KEY VALUE:",
                                                          "Carefully enter the new key value (as type: %s):" %type(value),
                                                          str(value),
                                                          False,
                                                          JOptionPane.WARNING_MESSAGE)

                            if not chgValue or len(chgValue.strip()) <1 or chgValue == value: continue
                            chgValue = chgValue.strip()

                            if isinstance(value, (int, float, bool, list)):
                                try:
                                    if isinstance(eval(chgValue), type(value) ):
                                        chgValue = eval(chgValue)
                                    else:
                                        myPopupInformationBox(jif,"ERROR: you must match the variable type to %s" %(type(value)),"PICKLE: CHANGE",JOptionPane.ERROR_MESSAGE)
                                        continue
                                except:
                                    myPopupInformationBox(jif,"ERROR: *EVAL* Could not set Key value %s - type %s" %(chgValue,type(value)),"PICKLE: CHANGE",JOptionPane.ERROR_MESSAGE)
                                    continue
                            elif isinstance(value,(str,unicode)):
                                if not check_if_key_data_string_valid(chgValue):
                                    myPopupInformationBox(jif,"ERROR: Key value %s is NOT valid!" %chgValue,"PICKLE: CHANGE",JOptionPane.ERROR_MESSAGE)
                                    continue    # back to menu
                            else:
                                myPopupInformationBox(jif,"SORRY: I cannot change Key value %s as it's type %s" %(chgValue,type(value)),"PICKLE: CHANGE",JOptionPane.ERROR_MESSAGE)
                                continue    # back to menu

                        if lDelOne:
                            myParameters.pop(selectedKey)
                        if lChg:
                            try:
                                myParameters[selectedKey] = chgValue
                            except:
                                myPopupInformationBox(jif,"ERROR: *set* Could not set Key value %s - type %s" %(chgValue,type(value)),"PICKLE: CHANGE",JOptionPane.ERROR_MESSAGE)
                                continue

                        if lDelOne:
                            myPrint("B","@@ PICKLEMODE: key: %s DELETED (old value: %s) @@" %(selectedKey,value))
                            myPopupInformationBox(jif,
                                                  "SUCCESS: key: %s DELETED (old value: %s)" %(selectedKey,value),
                                                  "PICKlE: DELETE",
                                                  JOptionPane.WARNING_MESSAGE)
                        if lChg:
                            myPrint("B","@@ PICKLERMODE: key: %s CHANGED to %s @@" %(selectedKey,chgValue))
                            myPopupInformationBox(jif,
                                                  "SUCCESS: key: %s CHANGED to %s" %(selectedKey,chgValue),
                                                  "PICKLE: CHANGE",
                                                  JOptionPane.WARNING_MESSAGE)
                        continue

            myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
            return


    def zero_bal_categories(statusLabel, lFix):
        global toolbox_frame_, debug, DARK_GREEN, lCopyAllToClipBoard_TB

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        if lFix:
            myPrint("DB","User requested to Inactivate Zero Balance Categories!")
        else:
            myPrint("D", "User requested to View Zero Balance Categories!")

        if lFix:
            myPrint("B", "Script running to Analyse your Active Categories for Zero Balance...............")
            myPrint("P", "---------------------------------------------------------")
        else:
            myPrint("B", "Script running to de-activate your Categories with Zero Balance...............")
            myPrint("P", "---------------------------------------------------------")

        if moneydance_data is None: return

        output = ""
        output += "Analysing your categories for Zero Balances....\n\n"

        baseCurr = moneydance_data.getCurrencies().getBaseType()


        # ==========================================
        # Search reminders first
        root = moneydance.getCurrentAccountBook()
        rems = root.getReminders().getAllReminders()

        listOfRems={}

        for rem in rems:
            remType = rem.getReminderType()  # NOTE or TRANSACTION

            if str(remType) != 'TRANSACTION': continue

            lastDate = rem.getLastDateInt()
            if not lastDate:
                pass    # No end date set, so proceed
            else:
                remDate = rem.getNextOccurance(lastDate)    # Stop at enddate
                if not remDate: continue    # Expired so skip

                if not remDate >= DateUtil.getStrippedDateInt(): continue
                # Right, got one!

            desc = rem.getDescription()

            txnParent = rem.getTransaction()

            for index2 in range(0, int(txnParent.getOtherTxnCount())):
                splitDesc = txnParent.getOtherTxn(index2).getDescription()
                acct = txnParent.getAccount()
                cat = txnParent.getOtherTxn(index2).getAccount()
                catValue = baseCurr.getDoubleValue(txnParent.getOtherTxn(index2).getValue()) * -1

                if catValue:
                    theReminder = [acct, cat, catValue, desc, splitDesc]
                    listOfRems[cat]=theReminder

        # ==========================================


        # Now the Categories
        accounts = AccountUtil.allMatchesForSearch(moneydance_data, MyAcctFilter(4))    # This returns active and inactive accounts
        accounts = sorted(accounts, key=lambda x: (x.getAccountType(), str(x.getFullAccountName()).upper()))

        categoriesToInactivate = {}

        output += "LISTING ACTIVE CATEGORIES WITH ZERO BALANCES:\n\n"

        # Run 1 - get the initial list
        for cat in accounts:
            if cat.getAccountOrParentIsInactive(): continue
            if (cat.getBalance() == 0
                    # and cat.getClearedBalance() == 0
                    and cat.getConfirmedBalance() == 0
                    and cat.getCurrentBalance() == 0
                    # and cat.getReconcilingBalance() == 0
                    and cat.getRecursiveBalance() == 0
                    # and cat.getRecursiveClearedBalance() == 0
                    and cat.getRecursiveCurrentBalance() == 0
                    # and cat.getRecursiveReconcilingBalance() == 0
            ):
                if listOfRems.get(cat):     # Found a reminder!
                    pass
                else:
                    categoriesToInactivate[cat]=True

        # Run 2 - filter out parents.... if we are retaining any sub cats
        for cat in accounts:
            if cat.getAccountOrParentIsInactive(): continue
            if not categoriesToInactivate.get(cat):     # Select categories that we are not deactivating

                # Look for its parents in the list of Cats to deactivate
                parentCats = cat.getPath()
                for theParent in parentCats:
                    if categoriesToInactivate.get(theParent):   # Found a parent - so don't deactivate it!
                        categoriesToInactivate[theParent]=False

        last = None
        iCountForInactivation = 0
        sortedCategoriesToInactivate=sorted(list(categoriesToInactivate), key=lambda x: (x.getAccountType(),x.getFullAccountName()) )

        # for cat in categoriesToInactivate.keys():
        for cat in sortedCategoriesToInactivate:
            if categoriesToInactivate.get(cat):
                iCountForInactivation+=1

                if not last or last != cat.getAccountType():
                    output += "\nCATEGORY TYPE: %s\n" % cat.getAccountType()
                    last = cat.getAccountType()

                output += "Category: %s has Zero Balances\n" % pad(cat.getFullAccountName(),100)
            else:
                output += "Category: %s ** But cannot be deactivated as it's the Parent of an active Category **\n" % pad(cat.getFullAccountName(),100)


        output += "--------------------------------------------------------------------------------------------------\n"
        output += ("You have %s categories with Zero Balances - these can be made Inactive using Advanced Mode......\n" % iCountForInactivation).upper()
        output += "---------------------------------------------------------------------------------------------------\n\n"

        output += "LISTING ACTIVE CATEGORIES WITH ZERO BALANCES - BUT WITH FUTURE REMINDERS PRESENT:\n\n"

        output += pad("Category Name", 78)
        output += " " + pad("Account", 20)
        output += " " + pad("Reminder Description", 35)
        output += " " + rpad("Rem Amount", 12)
        output += " " + pad("Split Desc", 35)
        # output += " " + rpad("RcrsRecBal", 12)
        output += "\n"

        last = None
        for cat in accounts:
            if cat.getAccountOrParentIsInactive(): continue
            if (cat.getBalance() == 0
                    # and cat.getClearedBalance() == 0
                    and cat.getConfirmedBalance() == 0
                    and cat.getCurrentBalance() == 0
                    # and cat.getReconcilingBalance() == 0
                    and cat.getRecursiveBalance() == 0
                    # and cat.getRecursiveClearedBalance() == 0
                    and cat.getRecursiveCurrentBalance() == 0
                    # and cat.getRecursiveReconcilingBalance() == 0
            ):
                if not last or last != cat.getAccountType():
                    output += "\nCATEGORY TYPE: %s\n" % cat.getAccountType()
                    last = cat.getAccountType()

                foundRem = listOfRems.get(cat)
                if foundRem:    # Found a reminder!
                    output += "Category: %s Reminder Details: " % pad(cat.getFullAccountName(),50)
                    output += pad(foundRem[0].getAccountName(),20)+" "
                    output += pad(foundRem[3],35)+" "
                    output += rpad(foundRem[2],12)+" "
                    output += pad(foundRem[4],35)+"\n"

        output += "-----------------------------------------------------------------------------------------------------------\n"


        output += "\n\nLISTING INACTIVE CATEGORIES WITH ZERO BALANCES:\n\n"

        ii=0
        last = None
        for cat in accounts:
            if not cat.getAccountOrParentIsInactive(): continue
            if (cat.getBalance() == 0
                    # and cat.getClearedBalance() == 0
                    and cat.getConfirmedBalance() == 0
                    and cat.getCurrentBalance() == 0
                    # and cat.getReconcilingBalance() == 0
                    and cat.getRecursiveBalance() == 0
                    # and cat.getRecursiveClearedBalance() == 0
                    and cat.getRecursiveCurrentBalance() == 0 ):  # and cat.getRecursiveReconcilingBalance() == 0


                if not last or last != cat.getAccountType():
                    output += "\nCATEGORY TYPE: %s\n" % cat.getAccountType()
                    last = cat.getAccountType()

                output += "Inactive Category: %s has Zero Balances\n" % pad(cat.getFullAccountName(),100)
                ii+=1

        if not ii:
            output += "<NONE FOUND>\n\n"

        output += "--------------------------------------------------------------------------------------------------\n"

        output += "LISTING ACTIVE CATEGORIES WITH BALANCES:\n\n"

        output += pad("Category Name", 85)
        output += " " + rpad("Balance", 12)
        # output += " " + rpad("ClrdBal", 12)
        # output += " " + rpad("ConfBal", 12)
        output += " " + rpad("CurrBal", 12)
        # output += " " + rpad("RecBal", 12)
        output += " " + rpad("RcrsBal", 12)
        # output += " " + rpad("RcrsClrdBal", 12)
        output += " " + rpad("RcrsCurrBal", 12)
        # output += " " + rpad("RcrsRecBal", 12)
        output += "\n"

        ii = 0
        last = None
        for cat in accounts:
            if cat.getAccountOrParentIsInactive(): continue
            if not (cat.getBalance() == 0
                    # and cat.getClearedBalance() == 0
                    and cat.getConfirmedBalance() == 0
                    and cat.getCurrentBalance() == 0
                    # and cat.getReconcilingBalance() == 0
                    and cat.getRecursiveBalance() == 0
                    # and cat.getRecursiveClearedBalance() == 0
                    and cat.getRecursiveCurrentBalance() == 0):     # and cat.getRecursiveReconcilingBalance() == 0
                if not last or last != cat.getAccountType():
                    output += "\nCATEGORY TYPE: %s\n" % cat.getAccountType()
                    last = cat.getAccountType()

                output += "%s" % pad(cat.getFullAccountName(), 85)

                mult = 1
                # noinspection PyUnresolvedReferences
                if cat.getAccountType() == Account.AccountType.EXPENSE: mult = -1

                output += " " + rpad("%s" % baseCurr.getDoubleValue(cat.getUserBalance()*mult), 12)
                # output += " " + rpad("%s" % baseCurr.getDoubleValue(cat.getUserClearedBalance()*mult), 12)
                # output += " " + rpad("%s" % baseCurr.getDoubleValue(cat.getUserConfirmedBalance()*mult), 12)
                output += " " + rpad("%s" % baseCurr.getDoubleValue(cat.getUserCurrentBalance()*mult), 12)
                # output += " " + rpad("%s" % baseCurr.getDoubleValue(cat.getUserReconcilingBalance()*mult), 12)
                output += " " + rpad("%s" % baseCurr.getDoubleValue(cat.getRecursiveUserBalance()*mult), 12)
                # output += " " + rpad("%s" % baseCurr.getDoubleValue(cat.getRecursiveUserClearedBalance()*mult), 12)
                output += " " + rpad("%s" % baseCurr.getDoubleValue(cat.getRecursiveUserCurrentBalance()*mult), 12)
                # output += " " + rpad("%s" % baseCurr.getDoubleValue(cat.getRecursiveUserReconcilingBalance()*-1), 12)
                output += "\n"
                ii+=1
        if not ii:
            output += "<NONE FOUND>\n\n"

        output += "----------------------------------------------------------------------------\n\n"

        output += "LISTING INACTIVE CATEGORIES WITH BALANCES:\n\n"

        output += pad("Category Name", 85)
        output += " " + rpad("Balance", 12)
        # output += " " + rpad("ClrdBal", 12)
        # output += " " + rpad("ConfBal", 12)
        output += " " + rpad("CurrBal", 12)
        # output += " " + rpad("RecBal", 12)
        output += " " + rpad("RcrsBal", 12)
        # output += " " + rpad("RcrsClrdBal", 12)
        output += " " + rpad("RcrsCurrBal", 12)
        # output += " " + rpad("RcrsRecBal", 12)
        output += "\n"

        ii=0
        last = None
        for cat in accounts:
            if not cat.getAccountOrParentIsInactive(): continue
            if not (cat.getBalance() == 0
                    # and cat.getClearedBalance() == 0
                    and cat.getConfirmedBalance() == 0
                    and cat.getCurrentBalance() == 0
                    # and cat.getReconcilingBalance() == 0
                    and cat.getRecursiveBalance() == 0
                    # and cat.getRecursiveClearedBalance() == 0
                    and cat.getRecursiveCurrentBalance() == 0):       # and cat.getRecursiveReconcilingBalance() == 0

                if not last or last != cat.getAccountType():
                    output += "\nCATEGORY TYPE: %s\n" % cat.getAccountType()
                    last = cat.getAccountType()

                output += "%s" % pad(cat.getFullAccountName(), 85)

                mult = 1
                # noinspection PyUnresolvedReferences
                if cat.getAccountType() == Account.AccountType.EXPENSE: mult = -1

                output += " " + rpad("%s" % baseCurr.getDoubleValue(cat.getUserBalance()*mult), 12)
                # output += " " + rpad("%s" % baseCurr.getDoubleValue(cat.getUserClearedBalance()*mult), 12)
                # output += " " + rpad("%s" % baseCurr.getDoubleValue(cat.getUserConfirmedBalance()*mult), 12)
                output += " " + rpad("%s" % baseCurr.getDoubleValue(cat.getUserCurrentBalance()*mult), 12)
                # output += " " + rpad("%s" % baseCurr.getDoubleValue(cat.getUserReconcilingBalance()*mult), 12)
                output += " " + rpad("%s" % baseCurr.getDoubleValue(cat.getRecursiveUserBalance()*mult), 12)
                # output += " " + rpad("%s" % baseCurr.getDoubleValue(cat.getRecursiveUserClearedBalance()*mult), 12)
                output += " " + rpad("%s" % baseCurr.getDoubleValue(cat.getRecursiveUserCurrentBalance()*mult), 12)
                # output += " " + rpad("%s" % baseCurr.getDoubleValue(cat.getRecursiveUserReconcilingBalance()*mult), 12)
                output += "\n"
                ii+=1

        if not ii:
            output += "<NONE FOUND>\n\n"

        output += "----------------------------------------------------------------------------\n\n"

        output += "\nLEGEND:\n"
        output += "** NOTE: The Balances shown on a Parent Category in any section may not be the sum of its Child Categories shown in the same section.\n"
        output += "         The calculation matches the Moneydance Tools>Categories method and will include the balances(s) from all its Child Categories whether active, inactive or otherwise....\n\n"
        output += "Balance = Account Balance\n"
        # output += "ClrdBal = Cleared Balance (Normally Zero on a Category). Balance excluding uncleared or reconciling txns\n"
        # output += "ConfBal = Confirmed Balance (The Balance less any unconfirmed Online / Downloaded Bank txns\n"
        output += "CurrBal = Current Balance\n"
        # output += "RecBal = Reconciling Balance (Normally Zero on a Category)\n"
        output += "RcrsBal = Recursive (through all sub categories) Account Balance (Note: may contain balances from inactive sub-categories as per Moneydance)\n"
        # output += "RcrsClrdBal = Recursive (through all sub categories) Cleared Balance (Normally Zero on a Category)\n"
        output += "RcrsCurrBal = Recursive (through all sub categories) Current Balance (Note: may contain balances from inactive sub-categories as per Moneydance)\n"
        # output += "RcrsRecBal = Recursive (through all sub categories) Reconciling Balance (Normally Zero on a Category)\n"
        output += "----------------------------------------------------------------------------\n\n"
        output += "<END>"

        if lFix:
            output += "\nDISCLAIMER: I take no responsibility if you decide to execute the Inactivate Zero Balance Category fix script!\n"

        if not lFix:
            jif = QuickJFrame("View your Active Categories with Zero Balances....", output).show_the_frame()
        else:
            jif = QuickJFrame("View your Active Categories with Zero Balances.... CLICK OK WHEN READY TO PROCEED", output).show_the_frame()

        myPrint("J", "There are %s Active Categories with Zero Balances that could be Inactivated!" % iCountForInactivation)

        if not lFix:
            statusLabel.setText( ("VIEW ZERO BALANCE CATEGORIES: YOU HAVE %s Zero Balance Categories..." % iCountForInactivation).ljust(800, " "))
            statusLabel.setForeground(DARK_GREEN)
            myPopupInformationBox(jif, "You have %s Active Categories with Zero Balances" % iCountForInactivation, "ZERO BALANCE CATEGORIES", JOptionPane.INFORMATION_MESSAGE)
            return

        if iCountForInactivation < 1:
            statusLabel.setText(("FIX ZERO BALANCE CATEGORIES: You have no Zero Balance Categories to fix - no fixes applied...").ljust(800, " "))
            statusLabel.setForeground(DARK_GREEN)
            myPopupInformationBox(jif, "No Zero Balance Categories >> No fixes will be applied !", "ZERO BALANCE CATEGORIES", JOptionPane.INFORMATION_MESSAGE)
            return

        if not confirm_backup_confirm_disclaimer(jif,statusLabel, "FIX - INACTIVATE ZERO BALANCE CATEGORIES", "Inactivate these %s Zero Balance Categories?" %(iCountForInactivation)):
            return

        # OK - so we are fixing...!
        myPrint("B", ">> User selected to Inactivate %s Zero Balance Categories!?" % iCountForInactivation)

        moneydance_data.setRecalcBalances(False)
        moneydance_ui.setSuspendRefresh(True)

        for cat in categoriesToInactivate.keys():
            if categoriesToInactivate.get(cat):
                myPrint("B", "Cat: " + cat.getFullAccountName() + " with Zero Balances, Set to INACTIVE!")
                cat.setAccountIsInactive(True)
                cat.syncItem()

        moneydance_ui.getMain().saveCurrentAccount()
        moneydance_data.setRecalcBalances(True)
        moneydance_ui.setSuspendRefresh(False)		# This does this too: book.notifyAccountModified(root)

        myPrint("B", "Finished Inactivating %s Categories with Zero Balances..." % iCountForInactivation)

        statusLabel.setText(("FIX - I have set %s Categories with Zero Balances to Inactive as requested!" % iCountForInactivation).ljust(800, " "))
        statusLabel.setForeground(Color.RED)
        myPopupInformationBox(jif,"OK - I have set %s Active Categories with Zero Balances to INACTIVE!" % iCountForInactivation,"INACTIVATE ZERO BALANCE CATEGORIES",JOptionPane.WARNING_MESSAGE)
        play_the_money_sound()

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
        return

    def fix_account_parent(statusLabel):
        global toolbox_frame_, debug

        # fix_account_parent.py (and old check_root_structure.py)

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        myPrint("B", "Diagnosing INVALID Parent Accounts....")
        myPrint("P", "--------------------------------------")

        book = moneydance.getCurrentAccountBook()
        root = book.getRootAccount()
        allAccounts = book.getItemsWithType(Account.SYNCABLE_TYPE_VALUE)


        def validate_path(check_acct):
            _acct = check_acct
            iterations = 0
            while True:
                # noinspection PyUnresolvedReferences
                if _acct.getAccountType() == Account.AccountType.ROOT:      return True
                if _acct is None:                                           return False
                if iterations > 100:                                        return False
                iterations+=1
                _acct = _acct.getParentAccount()
                continue


        output = "FIX ACCOUNT(s)' INVALID PARENT ACCOUNTS:\n" \
                 " ========================================\n\n"

        def check_fix_accounts(lFix=False):

            iErrors=0
            textFixed=""

            for acct in allAccounts:

                # skip root
                # noinspection PyUnresolvedReferences
                if acct == root or acct.getAccountType() == Account.AccountType.ROOT: continue

                parent = acct.getParentAccount()
                if ((parent is None or parent == acct)
                        or (parent is not None and parent != root and not validate_path(acct))):
                    iErrors+=1
                    if lFix:
                        myPrint("B","Resetting parent account for %s to root" %(acct.getAccountName()))
                        textFixed+=("Resetting parent account for %s to root\n" %(acct.getAccountName()))
                        acct.setParentAccount(root)
                        acct.syncItem()
                    else:
                        myPrint("B", "@@ ERROR - NEEDS RESET - Account: %s\n" % acct.getAccountName())
                        textFixed+="NEEDS RESET - Account: %s\n" % acct.getAccountName()

            return iErrors, textFixed

        iCountErrors, x =  check_fix_accounts(lFix=False)
        output += x

        if iCountErrors<1:
            statusLabel.setText(("'FIX: Account(s)'s Invalid Parent - CONGRATULATIONS - I found no Invalid parents.......").ljust(800, " "))
            statusLabel.setForeground(Color.BLUE)
            myPrint("B", "'FIX: Account(s)'s Invalid Parent - CONGRATULATIONS - I found no Invalid parents.......")
            myPopupInformationBox(toolbox_frame_,"CONGRATULATIONS - I found no Accounts with Invalid parents...")
            return

        myPrint("B","FIX - Account(s)' Invalid Parent Accounts - found %s errors..." %(iCountErrors))

        jif=QuickJFrame("VIEW ACCOUNT(s) WITH INVALID PARENT ACCOUNTS", output).show_the_frame()

        if not confirm_backup_confirm_disclaimer(jif,statusLabel,"FIX ACCOUNT(S)' INVALID PARENTS","FIX %s Acct(s)'s Invalid Parent Accts?" %(iCountErrors)):
            return

        jif.dispose()
        myPrint("B", "User accepted disclaimer to FIX Account(s)' Invalid Parent Accounts. Proceeding.....")

        output += "\n\nRUNNING FIX ON PARENT ACCOUNTS\n" \
                  "--------------------------------\n\n"

        moneydance_data.setRecalcBalances(False)
        moneydance_ui.setSuspendRefresh(True)

        iCountErrors, x =  check_fix_accounts(lFix=True)
        output += x
        output += "\n<END>"

        moneydance_ui.getMain().saveCurrentAccount()
        moneydance_data.setRecalcBalances(True)
        moneydance_ui.setSuspendRefresh(False)		# This does this too: book.notifyAccountModified(root)
        root = moneydance.getRootAccount()
        moneydance_data.notifyAccountModified(root)

        myPrint("B", "FIXED %s invalid Parent Accounts" %(iCountErrors))
        play_the_money_sound()
        statusLabel.setText(("FIXED %s invalid Parent Accounts" %(iCountErrors)).ljust(800, " "))
        statusLabel.setForeground(DARK_GREEN)
        jif=QuickJFrame("VIEW ACCOUNT(s) WITH INVALID PARENT ACCOUNTS", output).show_the_frame()
        myPopupInformationBox(jif,"FIXED %s invalid Parent Accounts" %(iCountErrors), "FIX INVALID PARENT ACCOUNTS", JOptionPane.WARNING_MESSAGE)

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
        return


    def fix_root_account_name(statusLabel):
        global toolbox_frame_, debug

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        bookName = moneydance.getCurrentAccountBook().getName().strip()
        root = moneydance.getCurrentAccountBook().getRootAccount()
        rootName = root.getAccountName().strip()

        if rootName == bookName:
            myPopupInformationBox(toolbox_frame_,
                                  "The name of your Root Account is already the same as your Dataset(or 'Book'): %s" % (bookName),
                                  "RENAME ROOT ACCOUNT",
                                  JOptionPane.INFORMATION_MESSAGE)
            statusLabel.setText(("No changed applied as your Root Account name is already the same as your Dataset ('Book') name: %s" %(bookName)).ljust(800, " "))
            statusLabel.setForeground(Color.BLUE)
            myPopupInformationBox(toolbox_frame_,"The name of your Root Account is already the same as your Dataset - NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        myPrint("B", "User requested to fix Root Account Name")
        myPrint("B", "Dataset's ('Book') Name: ", bookName)
        myPrint("B", "Root's Account Name: ", rootName)

        MyPopUpDialogBox(toolbox_frame_,
                         "RENAME ROOT ACCOUNT",
                         "Your Dataset ('book') name is: %s (this is the name that will be used)\nYour Root Account name is: %s" %(bookName,rootName),
                         theTitle="RENAME ROOT ACCOUNT").go()

        if not confirm_backup_confirm_disclaimer(toolbox_frame_, statusLabel, "RENAME ROOT ACCOUNT", "rename your Root Account to: %s?" %(bookName)):
            return

        myPrint("B", "User accepted disclaimer to reset Root Account Name. Proceeding.....")
        # Flush all in memory settings to config.dict file on disk
        moneydance.savePreferences()

        root.setAccountName(bookName)
        root.syncItem()

        moneydance_data.notifyAccountModified(root)

        myPrint("B", "Root account renamed to: %s" % (bookName))
        play_the_money_sound()

        statusLabel.setText((("Root Account Name changed to : %s - I SUGGEST YOU RESTART MONEYDANCE!" %(bookName)).ljust(800, " ")))
        statusLabel.setForeground(Color.RED)
        myPopupInformationBox(toolbox_frame_,"Root Account Name changed to : %s - I SUGGEST YOU RESTART MONEYDANCE!"%(bookName),"RENAME ROOT",JOptionPane.WARNING_MESSAGE)

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
        return

    # noinspection PyUnresolvedReferences
    def force_change_account_type(statusLabel):
        global toolbox_frame_, debug

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        # set_account_type.py
        ask=MyPopUpDialogBox(toolbox_frame_,
                             theStatus="Are you sure you want to FORCE change an Account's Type?",
                             theTitle="FORCE CHANGE TYPE",
                             theMessage="This is normally a BAD idea, unless you know you want to do it....!\n"
                                        "The typical scenario is where you have have created an Account with the wrong Type\n"
                                        "This fix will NOT attempt to check that the Acct has Txns that are valid in the new Account Type.\n"
                                        "It simply changes the Type set on the account to the new Type.\n"
                                        "You should carefully review your data afterwards and revert\n"
                                        "to a backup if you are not happy with the results....\n"
                                        "\n",
                             lCancelButton=True,
                             OKButtonText="I AGREE - PROCEED",
                             lAlertLevel=2)

        if not ask.go():
            statusLabel.setText(("User did not say yes to FORCE change an Account's type - no changes made").ljust(800, " "))
            statusLabel.setForeground(Color.BLUE)
            myPopupInformationBox(toolbox_frame_,"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return
        del ask

        accounts = AccountUtil.allMatchesForSearch(moneydance_data, MyAcctFilter(19))
        accounts = sorted(accounts, key=lambda sort_x: (sort_x.getAccountType(), sort_x.getFullAccountName().upper()))
        newAccounts = []
        for acct in accounts:
            newAccounts.append(StoreAccountList(acct))

        selectedAccount = JOptionPane.showInputDialog(toolbox_frame_,
                                                      "Select the Account to FORCE change its Type",
                                                      "FORCE CHANGE ACCOUNT's TYPE",
                                                      JOptionPane.WARNING_MESSAGE,
                                                      None,
                                                      newAccounts,
                                                      None)  # type: StoreAccountList
        if not selectedAccount:
            statusLabel.setText(("User did not Select an Account to FORCE change its Type - no changes made").ljust(800, " "))
            statusLabel.setForeground(Color.BLUE)
            myPopupInformationBox(toolbox_frame_,"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        selectedAccount = selectedAccount.obj       # type: Account

        if selectedAccount.getAccountType() == Account.AccountType.ROOT:
            if not myPopupAskQuestion(toolbox_frame_,"FORCE CHANGE ACCOUNT TYPE","THIS ACCOUNT IS ROOT (SPECIAL). DO YOU REALLY WANT TO CHANGE IT'S TYPE (Normally a bad idea!) ?", theMessageType=JOptionPane.ERROR_MESSAGE):
                statusLabel.setText(("User Aborted change of Root's Account Type (phew!) - no changes made").ljust(800, " "))
                statusLabel.setForeground(Color.BLUE)
                myPopupInformationBox(toolbox_frame_,"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
                return

        possTypes = Account.AccountType.values()
        possTypes.remove(Account.AccountType.ROOT)
        possTypes.remove(Account.AccountType.SECURITY)
        if selectedAccount.getAccountType() in possTypes:
            possTypes.remove(selectedAccount.getAccountType())

        selectedType = JOptionPane.showInputDialog(toolbox_frame_,
                                                   "Select the new Account Type",
                                                   "FORCE CHANGE ACCOUNT's TYPE",
                                                   JOptionPane.WARNING_MESSAGE,
                                                   None,
                                                   possTypes,
                                                   None)  # type: Account.AccountType
        if not selectedType:
            statusLabel.setText(("User did not Select a new Account Type - no changes made").ljust(800, " "))
            statusLabel.setForeground(Color.BLUE)
            myPopupInformationBox(toolbox_frame_,"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        if selectedType == Account.AccountType.ROOT:
            if not myPopupAskQuestion(toolbox_frame_,"FORCE CHANGE ACCOUNT TYPE","DO YOU REALLY WANT TO CHANGE TO ROOT (Normally a bad idea!)?", theMessageType=JOptionPane.ERROR_MESSAGE):
                statusLabel.setText(("User Aborted change Account to type Root (phew!) - no changes made").ljust(800, " "))
                statusLabel.setForeground(Color.BLUE)
                myPopupInformationBox(toolbox_frame_,"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
                return

        ask=MyPopUpDialogBox(toolbox_frame_,
                             theStatus="Are you sure you want to FORCE change this Account's Type?",
                             theTitle="FORCE CHANGE TYPE",
                             theMessage="Account: %s\n"
                                        "Old Type: %s\n"
                                        "New Type: %s\n"
                                        %(selectedAccount.getFullAccountName(), selectedAccount.getAccountType(),selectedType),  # noqa
                             lCancelButton=True,
                             OKButtonText="I AGREE - PROCEED",
                             lAlertLevel=2)

        if not ask.go():
            statusLabel.setText(("User aborted the FORCE change to an Account's type - no changes made").ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            myPopupInformationBox(toolbox_frame_,"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        if not confirm_backup_confirm_disclaimer(toolbox_frame_, statusLabel, "FORCE CHANGE TYPE", "FORCE CHANGE ACCOUNT %s TYPE to %s" %(selectedAccount.getFullAccountName(),selectedType)):    # noqa
            return

        myPrint("B","@@ User requested to Force Change the Type of Account: %s from: %s to %s - APPLYING UPDATE NOW...."
                %(selectedAccount.getFullAccountName(),selectedAccount.getAccountType(),selectedType))          # noqa

        moneydance_data.setRecalcBalances(False)
        moneydance_ui.setSuspendRefresh(True)

        selectedAccount.setAccountType(selectedType)                                                            # noqa
        selectedAccount.syncItem()                                                                              # noqa

        moneydance_ui.getMain().saveCurrentAccount()
        moneydance_data.setRecalcBalances(True)
        moneydance_ui.setSuspendRefresh(False)		# This does this too: book.notifyAccountModified(root)

        root = moneydance.getRootAccount()
        moneydance_data.notifyAccountModified(root)

        statusLabel.setText(("The Account: %s has been changed to Type: %s- PLEASE REVIEW"
                                  %(selectedAccount.getAccountName(),selectedAccount.getAccountType())).ljust(800, " "))   # noqa
        statusLabel.setForeground(Color.RED)

        play_the_money_sound()
        myPopupInformationBox(toolbox_frame_,"The Account: %s has been changed to Type: %s - PLEASE RESTART MD & REVIEW"
                              %(selectedAccount.getAccountName(),selectedAccount.getAccountType()),theMessageType=JOptionPane.ERROR_MESSAGE)   # noqa

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
        return

    # noinspection PyUnresolvedReferences
    def force_change_all_accounts_currencies(statusLabel):
        global toolbox_frame_, debug

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        # force_change_all_currencies.py
        ask=MyPopUpDialogBox(toolbox_frame_,
                             theStatus="Are you sure you want to FORCE change ALL Account's Currencies?",
                             theTitle="FORCE CHANGE ALL ACCOUNTS' CURRENCIES",
                             theMessage="This is normally a BAD idea, unless you know you want to do it....!\n"
                                        "The typical scenario is where you have a missing currency, or need to change them all\n"
                                        "This fix will not touch the ROOT account nor Security sub-accounts (which are stocks/shares)\n"
                                        "This fix will NOT attempt to correct any transactions or fx rates etc... It simply changes the currency\n"
                                        "set on all accounts to the new currency. You should carefully review your data afterwards and revert\n"
                                        "to a backup if you are not happy with the results....\n"
                                        "\n",
                             lCancelButton=True,
                             OKButtonText="I AGREE - PROCEED",
                             lAlertLevel=2)

        if not ask.go():
            statusLabel.setText(("User did not say yes to FORCE change ALL Account's currencies - no changes made").ljust(800, " "))
            statusLabel.setForeground(Color.BLUE)
            myPopupInformationBox(toolbox_frame_,"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return
        del ask

        accounts = AccountUtil.allMatchesForSearch(moneydance_data, MyAcctFilter(19))
        accounts = sorted(accounts, key=lambda sort_x: (sort_x.getAccountType(), sort_x.getFullAccountName().upper()))

        currencies=[]
        book = moneydance.getCurrentAccountBook()
        allCurrencies = book.getCurrencies().getAllCurrencies()
        for c in allCurrencies:
            if c.getCurrencyType() == CurrencyType.Type.CURRENCY:                                               # noqa
                currencies.append(c)
        currencies = sorted(currencies, key=lambda sort_x: (sort_x.getName().upper()))

        if len(currencies) < 1:
            myPrint("B", "FORCE CHANGE ALL ACCOUNTS' CURRENCIES - Creating new currency record!")
            selectedCurrency = CurrencyType(book.getCurrencies())       # Creates a null:null CT record
            selectedCurrency.setName("NEW CURRENCY - PLEASE EDIT ME LATER")
            selectedCurrency.setIDString("AAA")
            selectedCurrency.setDecimalPlaces(2)
            selectedCurrency.syncItem()
            myPrint("B", "FORCE CHANGE ALL ACCOUNTS' CURRENCIES - Creating new currency: %s" %(selectedCurrency))
            myPopupInformationBox(toolbox_frame_,"FYI - I have created a new Currency %s for you (Edit me later)" %(selectedCurrency),
                                  "FORCE CHANGE ALL ACCOUNTS' CURRENCIES")
        else:
            selectedCurrency = JOptionPane.showInputDialog(toolbox_frame_,
                                                           "Select a currency to assign to *ALL* accounts",
                                                           "FORCE CHANGE ALL ACCOUNT's CURRENCIES",
                                                           JOptionPane.ERROR_MESSAGE,
                                                           None,
                                                           currencies,
                                                           None)  # type: CurrencyType

        if not selectedCurrency:
            statusLabel.setText(("User did not Select a new currency for FORCE change ALL Accounts' Currencies - no changes made").ljust(800, " "))
            statusLabel.setForeground(Color.BLUE)
            myPopupInformationBox(toolbox_frame_,"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        if not confirm_backup_confirm_disclaimer(toolbox_frame_, statusLabel, "FORCE CHANGE ALL ACCOUNTS' CURRENCIES", "FORCE CHANGE ALL %s ACCOUNT's CURRENCIES TO %s?" %(len(accounts),selectedCurrency)):    # noqa
            return

        myPrint("B","@@ User requested to Force Change the Currency of ALL %s Accounts to %s - APPLYING UPDATE NOW...."
                %(len(accounts),selectedCurrency))     # noqa

        moneydance_data.setRecalcBalances(False)
        moneydance_ui.setSuspendRefresh(True)

        accountsChanged = 0
        for account in accounts:
            if account.getAccountType() == Account.AccountType.ROOT:
                continue
            if account.getAccountType() == Account.AccountType.SECURITY:
                continue
            if account.getCurrencyType() == selectedCurrency:
                continue

            myPrint("B","Setting account %s to currency %s" %(account, selectedCurrency))
            account.setCurrencyType(selectedCurrency)
            account.syncItem()
            accountsChanged += 1

        moneydance_ui.getMain().saveCurrentAccount()
        moneydance_data.setRecalcBalances(True)
        moneydance_ui.setSuspendRefresh(False)

        root = moneydance.getRootAccount()
        moneydance_data.notifyAccountModified(root)

        statusLabel.setText(("FORCE CHANGE ALL ACCOUNTS' CURRENCIES: %s Accounts changed to currency: %s - PLEASE RESTART MD & REVIEW"
                                  %(accountsChanged,selectedCurrency)).ljust(800, " "))   # noqa
        statusLabel.setForeground(Color.RED)
        myPrint("B", "FORCE CHANGE ALL ACCOUNTS' CURRENCIES: %s Accounts changed to currency: %s - PLEASE RESTART MD & REVIEW"
                %(accountsChanged,selectedCurrency))
        play_the_money_sound()
        myPopupInformationBox(toolbox_frame_,"%s Accounts changed to currency: %s - PLEASE RESTART MD & REVIEW"
                              %(accountsChanged,selectedCurrency),theMessageType=JOptionPane.ERROR_MESSAGE)   # noqa

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
        return

    def fix_invalid_relative_currency_rates(statusLabel):
        global toolbox_frame_, debug

        myPrint(u"D", u"In ", inspect.currentframe().f_code.co_name, u"()")

        if moneydance_data is None: return

        book = moneydance.getCurrentAccountBook()
        currencies = book.getCurrencies().getAllCurrencies()
        currencies = sorted(currencies, key=lambda sort_x: (sort_x.getCurrencyType(),sort_x.getName().upper()))

        output=u"FIX INVALID RELATIVE CURRENCIES\n" \
               u" ==============================\n\n"

        upperLimit = 9999999999
        iErrors = 0
        for curr in currencies:
            if curr.getRelativeRate() <= 0 or curr.getRelativeRate() > upperLimit:
                iErrors += 1
                output += u"Invalid - Type: %s Name: %s Relative Rate: %s\n" %(curr.getCurrencyType(),pad(curr.getName(),25),rpad(curr.getRelativeRate(),20))

        if iErrors < 1:
            statusLabel.setText((u"FIX INVALID REL CURR RATES: You have no relative rates <0 or >%s to fix - NO CHANGES MADE" %upperLimit).ljust(800, u" "))
            statusLabel.setForeground(Color.BLUE)
            myPopupInformationBox(toolbox_frame_,u"You have no relative rates <0 or >%s to fix - NO CHANGES MADE" %upperLimit,u"FIX INVALID REL CURR RATES")
            return

        jif=QuickJFrame(u"FIX INVALID RELATIVE CURRENCIES",output).show_the_frame()

        # force_change_account_currency.py
        ask=MyPopUpDialogBox(jif,
                             theStatus=u"Are you sure you want to FIX these %s INVALID RELATIVE CURRENCIES?" %iErrors,
                             theTitle=u"FIX INVALID RELATIVE CURRENCIES",
                             theMessage=u"Do not proceed unless you know you want to do this....!\n"
                                        u"This fix will NOT attempt to correct any transactions or fx rates etc... It simply changes the relative rate(s)\n"
                                        u"You should carefully review your data afterwards and revert to a backup if you are not happy with the results....\n",
                             lCancelButton=True,
                             OKButtonText=u"I AGREE - PROCEED",
                             lAlertLevel=2)

        if not ask.go():
            statusLabel.setText((u"User did not say yes to fix invalid relative currencies - no changes made").ljust(800, " "))
            statusLabel.setForeground(Color.BLUE)
            myPopupInformationBox(toolbox_frame_,u"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return
        del ask


        if not confirm_backup_confirm_disclaimer(jif, statusLabel, u"FIX INVALID RELATIVE CURR RATES", u"FIX %s INVALID RELATIVE CURRENCY RATES" %(iErrors)):
            return

        jif.dispose()

        myPrint(u"B",u"@@ User requested to fix %s invalid relative currency rates - APPLYING UPDATE NOW...." %(iErrors) )

        output += u"\n\n APPLYING FIXES\n" \
                  u" ==============\n\n"

        moneydance_data.setRecalcBalances(False)
        moneydance_ui.setSuspendRefresh(True)

        for curr in currencies:
            if curr.getRelativeRate() <= 0 or curr.getRelativeRate() > upperLimit:
                output += u"FIXING >> Invalid - Type: %s Name: %s Relative Rate: %s - RESET TO 1.0\n" %(curr.getCurrencyType(),pad(curr.getName(),25),rpad(curr.getRelativeRate(),20))

                myPrint(u"B", u"FIXING >> Invalid - Type: %s Name: %s Relative Rate: %s - RESET TO 1.0" %(curr.getCurrencyType(),pad(curr.getName(),25),rpad(curr.getRelativeRate(),20)))

                curr.setRelativeRate(1.0)
                curr.syncItem()

        myPrint(u"P", output)

        moneydance_ui.getMain().saveCurrentAccount()
        moneydance_data.setRecalcBalances(True)
        moneydance_ui.setSuspendRefresh(False)		# This does this too: book.notifyAccountModified(root)

        jif=QuickJFrame(u"FIX INVALID RELATIVE CURRENCIES",output).show_the_frame()

        statusLabel.setText((u"FIX INVALID RELATIVE CURRENCIES: %s Invalid Currency relative rates have been reset to 1.0 - PLEASE REVIEW" %(iErrors)).ljust(800, u" "))   # noqa
        statusLabel.setForeground(Color.RED)
        play_the_money_sound()
        myPopupInformationBox(jif,u"%s Invalid Currency relative rates have been reset to 1.0 - PLEASE RESTART MD & REVIEW" %(iErrors),
                              u"FIX INVALID RELATIVE CURRENCIES",
                              theMessageType=JOptionPane.ERROR_MESSAGE)   # noqa

        myPrint(u"D", u"Exiting ", inspect.currentframe().f_code.co_name, u"()")
        return

    def force_change_account_currency(statusLabel):
        global toolbox_frame_, debug

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        # force_change_account_currency.py
        ask=MyPopUpDialogBox(toolbox_frame_,
                             theStatus="Are you sure you want to FORCE change an Account's Currency?",
                             theTitle="FORCE CHANGE CURRENCY",
                             theMessage="This is normally a BAD idea, unless you know you want to do it....!\n"
                                        "The typical scenario is where you have duplicated Currencies and you want to move\n"
                                        "transactions from one account to another, but the system prevents you unless they are the same currency\n"
                                        "This fix will NOT attempt to correct any transactions or fx rates etc... It simply changes the currency\n"
                                        "set on the account to the new currency. You should carefully review your data afterwards and revert\n"
                                        "to a backup if you are not happy with the results....\n"
                                        "\n",
                             lCancelButton=True,
                             OKButtonText="I AGREE - PROCEED",
                             lAlertLevel=2)

        if not ask.go():
            statusLabel.setText(("User did not say yes to FORCE change an Account's currency - no changes made").ljust(800, " "))
            statusLabel.setForeground(Color.BLUE)
            myPopupInformationBox(toolbox_frame_,"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return
        del ask

        currencies=[]
        book = moneydance.getCurrentAccountBook()
        allCurrencies = book.getCurrencies().getAllCurrencies()
        for c in allCurrencies:
            if c.getCurrencyType() == CurrencyType.Type.CURRENCY:                                               # noqa
                currencies.append(c)
        currencies = sorted(currencies, key=lambda sort_x: (sort_x.getName().upper()))

        accounts = AccountUtil.allMatchesForSearch(moneydance_data, MyAcctFilter(5))
        accounts = sorted(accounts, key=lambda sort_x: (sort_x.getAccountType(), sort_x.getFullAccountName().upper()))
        newAccounts = []
        for acct in accounts:
            newAccounts.append(StoreAccountList(acct))

        selectedAccount = JOptionPane.showInputDialog(toolbox_frame_,
                                                      "Select the Account to FORCE change currency",
                                                      "FORCE CHANGE ACCOUNT's CURRENCY",
                                                      JOptionPane.WARNING_MESSAGE,
                                                      None,
                                                      newAccounts,
                                                      None)  # type: StoreAccountList
        if not selectedAccount:
            statusLabel.setText(("User did not Select an Account to FORCE change currency - no changes made").ljust(800, " "))
            statusLabel.setForeground(Color.BLUE)
            myPopupInformationBox(toolbox_frame_,"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        selectedAccount = selectedAccount.obj       # type: Account

        # noinspection PyUnresolvedReferences
        currencies.remove(selectedAccount.getCurrencyType())

        selectedCurrency = JOptionPane.showInputDialog(toolbox_frame_,
                                                       "Old Currency: %s >> Select the new currency for the account" %(selectedAccount.getCurrencyType()),                    # noqa
                                                       "FORCE CHANGE ACCOUNT's CURRENCY",
                                                       JOptionPane.ERROR_MESSAGE,
                                                       None,
                                                       currencies,
                                                       None)  # type: CurrencyType
        if not selectedCurrency:
            statusLabel.setText(("User did not Select an new currency for Account FORCE change - no changes made").ljust(800, " "))
            statusLabel.setForeground(Color.BLUE)
            myPopupInformationBox(toolbox_frame_,"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        ask=MyPopUpDialogBox(toolbox_frame_,
                             theStatus="Are you sure you want to FORCE change this Account's Currency?",
                             theTitle="FORCE CHANGE CURRENCY",
                             theMessage="Account: %s\n"
                                        "Old Currency: %s\n"
                                        "New Currency: %s\n"
                                        %(selectedAccount.getFullAccountName(), selectedAccount.getCurrencyType(),selectedCurrency),  # noqa
                             lCancelButton=True,
                             OKButtonText="I AGREE - PROCEED",
                             lAlertLevel=2)

        if not ask.go():
            statusLabel.setText(("User aborted the FORCE change to an Account's currency - no changes made").ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            myPopupInformationBox(toolbox_frame_,"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        if not confirm_backup_confirm_disclaimer(toolbox_frame_, statusLabel, "FORCE CHANGE CURRENCY", "FORCE CHANGE ACCOUNT %s CURRENCY" %(selectedAccount.getFullAccountName())):    # noqa
            return

        myPrint("B","@@ User requested to Force Change the Currency of Account: %s from: %s to %s - APPLYING UPDATE NOW...."
                %(selectedAccount.getFullAccountName(),selectedAccount.getCurrencyType(),selectedCurrency))     # noqa

        moneydance_data.setRecalcBalances(False)
        moneydance_ui.setSuspendRefresh(True)

        selectedAccount.setCurrencyType(selectedCurrency)                                                       # noqa
        selectedAccount.syncItem()                                                                              # noqa

        moneydance_ui.getMain().saveCurrentAccount()
        moneydance_data.setRecalcBalances(True)
        moneydance_ui.setSuspendRefresh(False)

        root = moneydance.getRootAccount()
        moneydance_data.notifyAccountModified(root)

        statusLabel.setText(("The Account: %s has been changed to Currency: %s- PLEASE REVIEW"
                                  %(selectedAccount.getAccountName(),selectedAccount.getCurrencyType())).ljust(800, " "))   # noqa
        statusLabel.setForeground(Color.RED)

        play_the_money_sound()
        myPopupInformationBox(toolbox_frame_,"The Account: %s has been changed to Currency: %s - PLEASE RESTART MD & REVIEW"
                              %(selectedAccount.getAccountName(),selectedAccount.getCurrencyType()),theMessageType=JOptionPane.ERROR_MESSAGE)   # noqa

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
        return

    def reverse_txn_amounts(statusLabel):
        global toolbox_frame_, debug

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        # reverse_txn_amounts.py
        ask=MyPopUpDialogBox(toolbox_frame_,
                             theStatus="Are you sure you want to REVERSE Transaction amounts on an Account's Transactions (between two dates)?",
                             theTitle="REVERSE TRANSACTIONAL AMOUNTS",
                             theMessage="This is normally a BAD idea, unless you know you want to do it....!\n"
                                        "The typical scenario is where you perhaps imported transactions with the wrong +/- sign\n"
                                        "..or perhaps you  have changed an account's type\n"
                                        "This fix will not touch the ROOT account nor Investment/Security sub-accounts (which are stocks/shares)\n"
                                        "You should carefully review your data afterwards and revert to a backup if you are not happy with the results....",
                             lCancelButton=True,
                             OKButtonText="I AGREE - PROCEED",
                             lAlertLevel=2)

        if not ask.go():
            statusLabel.setText(("User did not say yes to REVERSE TXN AMOUNTS - no changes made").ljust(800, " "))
            statusLabel.setForeground(Color.BLUE)
            myPopupInformationBox(toolbox_frame_,"User did not say yes to REVERSE TXN AMOUNTS - NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return
        del ask

        accounts = AccountUtil.allMatchesForSearch(moneydance_data, MyAcctFilter(20))
        accounts = sorted(accounts, key=lambda sort_x: (sort_x.getAccountType(), sort_x.getFullAccountName().upper()))

        newAccounts = []
        for acct in accounts:
            newAccounts.append(StoreAccountList(acct))

        selectedAccount = JOptionPane.showInputDialog(toolbox_frame_,
                                                      "Select the Account to REVERSE Transactional Amounts",
                                                      "REVERSE ACCOUNT's TXN AMOUNTS",
                                                      JOptionPane.WARNING_MESSAGE,
                                                      None,
                                                      newAccounts,
                                                      None)  # type: StoreAccountList

        if not selectedAccount:
            statusLabel.setText(("User did not Select an Account to REVERSE Transactional Amounts - no changes made").ljust(800, " "))
            statusLabel.setForeground(Color.BLUE)
            myPopupInformationBox(toolbox_frame_,"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        selectedAccount = selectedAccount.obj       # type: Account

        dateField = JDateField(moneydance_ui)
        if not JOptionPane.showConfirmDialog(toolbox_frame_, dateField, "Select Starting Date for reverse", JOptionPane.OK_CANCEL_OPTION)==JOptionPane.OK_OPTION:
            statusLabel.setText(("User did not select start date - no changes made").ljust(800, " "))
            statusLabel.setForeground(Color.BLUE)
            myPopupInformationBox(toolbox_frame_,"User did not select start date - NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return
        startDate = dateField.getDateInt()

        dateField.gotoToday()

        if not JOptionPane.showConfirmDialog(toolbox_frame_, dateField, "Select Ending Date for reverse", JOptionPane.OK_CANCEL_OPTION)==JOptionPane.OK_OPTION:
            statusLabel.setText(("User did not select end date - no changes made").ljust(800, " "))
            statusLabel.setForeground(Color.BLUE)
            myPopupInformationBox(toolbox_frame_,"User did not select end date - NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return
        endDate = dateField.getDateInt()

        txnSet = moneydance_data.getTransactionSet()
        txns = txnSet.iterableTxns()

        iTxnsFound = 0
        for txn in txns:
            if txn.getDateInt() < startDate: continue
            if txn.getDateInt() > endDate: continue
            acct = txn.getAccount()
            if not acct == selectedAccount: continue
            iTxnsFound += 1

        if iTxnsFound < 1:
            statusLabel.setText(("REVERSE TXN AMOUNTS - Sorry - no transactions found - NO CHANGES MADE").ljust(800, " "))
            statusLabel.setForeground(Color.BLUE)
            myPopupInformationBox(toolbox_frame_,"REVERSE TXN AMOUNTS - Sorry - no transactions found - NO CHANGES MADE",theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        if not confirm_backup_confirm_disclaimer(toolbox_frame_, statusLabel, "REVERSE ACCT TXN AMOUNTS", "ACCOUNT %s - REVERSE %s Txns' amounts between %s - %s?" %(selectedAccount,iTxnsFound,startDate,endDate)):
            return

        myPrint("B","@@ User requested to REVERSE the (%s) Txn Amounts on Account %s between %s to %s - APPLYING UPDATE NOW...." %(iTxnsFound, selectedAccount, startDate, endDate))

        moneydance_data.setRecalcBalances(False)
        moneydance_ui.setSuspendRefresh(True)

        for txn in txns:
            if txn.getDateInt() < startDate: continue
            if txn.getDateInt() > endDate: continue
            acct = txn.getAccount()
            if not acct == selectedAccount: continue

            myPrint("B","Reversing the amount on %s" %(txn))
            ptxn = txn.getParentTxn()

            ptxn.setEditingMode()

            if ptxn == txn:             # this is the parent part of the txn
                myPrint("B", "  - is a parent, changing each split")
                for splitIdx in range(0, txn.getSplitCount()):
                    txn.getSplit(splitIdx).negateAmount()
            else:
                myPrint("B", "  - is a split")
                txn.negateAmount()

            ptxn.syncItem()

        moneydance_ui.getMain().saveCurrentAccount()
        moneydance_data.setRecalcBalances(True)
        moneydance_ui.setSuspendRefresh(False)		# This does this too: book.notifyAccountModified(root)

        statusLabel.setText(("REVERSE %s Txns Amounts on Account %s between %s - %s COMPLETED - PLEASE REVIEW" %(iTxnsFound,selectedAccount,startDate, endDate)).ljust(800, " "))
        statusLabel.setForeground(Color.RED)
        myPrint("B", "REVERSE %s Txns Amounts on Account %s between %s - %s COMPLETED - PLEASE REVIEW" %(iTxnsFound,selectedAccount,startDate, endDate))
        play_the_money_sound()
        myPopupInformationBox(toolbox_frame_,
                              "REVERSE %s Txns Amounts on Account %s between %s - %s COMPLETED - PLEASE REVIEW" %(iTxnsFound,selectedAccount,startDate, endDate),
                              theMessageType=JOptionPane.ERROR_MESSAGE)

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
        return

    def reverse_txn_exchange_rates_by_account_and_date(statusLabel):
        global toolbox_frame_, debug

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        # reverse_txn_exchange_rates_by_account_and_date.py

        ask=MyPopUpDialogBox(toolbox_frame_,
                             theStatus="Are you sure you want to REVERSE Exchange Rates on an Account's Transactions (between two dates)?",
                             theTitle="REVERSE TRANSACTIONAL EXCHANGE RATES",
                             theMessage="This is normally a BAD idea, unless you know you want to do it....!\n"
                                        "The typical scenario is where you perhaps imported transactions with the fx rates inversed \n"
                                        "This fix will not touch the Currency price history...!\n"
                                        "This fix will not touch the ROOT account nor Investment/Security sub-accounts (which are stocks/shares)\n"
                                        "You should carefully review your data afterwards and revert to a backup if you are not happy with the results....",
                             lCancelButton=True,
                             OKButtonText="I AGREE - PROCEED",
                             lAlertLevel=2)

        if not ask.go():
            statusLabel.setText(("User did not say yes to REVERSE TXN EXCHANGE RATES - no changes made").ljust(800, " "))
            statusLabel.setForeground(Color.BLUE)
            myPopupInformationBox(toolbox_frame_,"User did not say yes to REVERSE TXN EXCHANGE RATES - NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return
        del ask

        accounts = AccountUtil.allMatchesForSearch(moneydance_data, MyAcctFilter(20))
        accounts = sorted(accounts, key=lambda sort_x: (sort_x.getAccountType(), sort_x.getFullAccountName().upper()))

        newAccounts = []
        for acct in accounts:
            newAccounts.append(StoreAccountList(acct))

        selectedAccount = JOptionPane.showInputDialog(toolbox_frame_,
                                                      "Select the Account to REVERSE Transactional Exchange Rates",
                                                      "REVERSE ACCOUNT's TXN EXCHANGE RATES",
                                                      JOptionPane.WARNING_MESSAGE,
                                                      None,
                                                      newAccounts,
                                                      None)  # type: StoreAccountList

        if not selectedAccount:
            statusLabel.setText(("User did not select an Account to REVERSE Transactional Exchange Rates - no changes made").ljust(800, " "))
            statusLabel.setForeground(Color.BLUE)
            myPopupInformationBox(toolbox_frame_,"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        selectedAccount = selectedAccount.obj       # type: Account

        dateField = JDateField(moneydance_ui)
        if not JOptionPane.showConfirmDialog(toolbox_frame_, dateField, "Select STARTING Date for reverse", JOptionPane.OK_CANCEL_OPTION)==JOptionPane.OK_OPTION:
            statusLabel.setText(("User did not select start date - no changes made").ljust(800, " "))
            statusLabel.setForeground(Color.BLUE)
            myPopupInformationBox(toolbox_frame_,"User did not select start date - NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return
        startDate = dateField.getDateInt()

        dateField.gotoToday()

        if not JOptionPane.showConfirmDialog(toolbox_frame_, dateField, "Select ENDING Date for reverse", JOptionPane.OK_CANCEL_OPTION)==JOptionPane.OK_OPTION:
            statusLabel.setText(("User did not select end date - no changes made").ljust(800, " "))
            statusLabel.setForeground(Color.BLUE)
            myPopupInformationBox(toolbox_frame_,"User did not select end date - NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return
        endDate = dateField.getDateInt()

        txnSet = moneydance_data.getTransactionSet()
        txns = txnSet.iterableTxns()

        iTxnsFound = 0

        for txn in txns:
            if txn.getDateInt() < startDate: continue
            if txn.getDateInt() > endDate: continue

            acct = txn.getAccount()
            if not acct == selectedAccount: continue

            if txn.getParentTxn() == txn:   # Parent
                for splitNum in range(0, txn.getSplitCount()):
                    split = txn.getSplit(splitNum)
                    if split.getAmount() != split.getValue():
                        iTxnsFound += 1
                        break
            else:   # Split
                if txn.getAmount() != txn.getValue():
                    iTxnsFound += 1

        if iTxnsFound < 1:
            statusLabel.setText(("REVERSE TXN EXCHANGE RATES - Sorry - no transactions found (with fx) - NO CHANGES MADE").ljust(800, " "))
            statusLabel.setForeground(Color.BLUE)
            myPopupInformationBox(toolbox_frame_,"REVERSE TXN EXCHANGE RATES - Sorry - no transactions found (with fx) - NO CHANGES MADE",theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        if not confirm_backup_confirm_disclaimer(toolbox_frame_, statusLabel, "REVERSE ACCT TXN EXCHANGE RATES", "ACCOUNT %s - REVERSE %s Txns' exchange rates between %s - %s?" %(selectedAccount,iTxnsFound,startDate,endDate)):
            return

        myPrint("B","@@ User requested to REVERSE the (%s) Txn Exchange Rates on Account %s between %s to %s - APPLYING UPDATE NOW...." %(iTxnsFound, selectedAccount, startDate, endDate))

        moneydance_data.setRecalcBalances(False)
        moneydance_ui.setSuspendRefresh(True)

        for txn in txns:
            if txn.getDateInt() < startDate: continue
            if txn.getDateInt() > endDate: continue

            acct = txn.getAccount()
            if not acct == selectedAccount: continue

            ptxn = txn.getParentTxn()
            needsSync = False

            if ptxn == txn:
                for splitNum in range(0, txn.getSplitCount()):
                    split = txn.getSplit(splitNum)
                    if split.getAmount() != split.getValue():
                        if not needsSync:
                            myPrint("B","Reversing exchange rate on %s" %(txn))
                            myPrint("B", "  - is a parent, changing each split")
                            ptxn.setEditingMode()
                        needsSync = True
                        parentVal = split.getParentValue()
                        rate = split.getRate()
                        split.setParentAmount(1/rate, parentVal)
            else:
                split = txn
                if split.getAmount() != split.getValue():
                    myPrint("B","Reversing exchange rate on %s" %(txn))
                    myPrint("B", "  - This is a split - changing...")
                    if not needsSync:
                        ptxn.setEditingMode()
                    needsSync = True
                    parentVal = split.getParentValue()
                    rate = split.getRate()
                    split.setParentAmount(1/rate, parentVal)

            if needsSync:
                ptxn.syncItem()

        moneydance_ui.getMain().saveCurrentAccount()
        moneydance_data.setRecalcBalances(True)
        moneydance_ui.setSuspendRefresh(False)		# This does this too: book.notifyAccountModified(root)

        statusLabel.setText(("REVERSE %s Txns Exchange Rates on Account %s between %s - %s COMPLETED - PLEASE REVIEW" %(iTxnsFound,selectedAccount,startDate, endDate)).ljust(800, " "))
        statusLabel.setForeground(Color.RED)
        myPrint("B", "REVERSE %s Txns Exchange Rates on Account %s between %s - %s COMPLETED - PLEASE REVIEW" %(iTxnsFound,selectedAccount,startDate, endDate))
        play_the_money_sound()
        myPopupInformationBox(toolbox_frame_,
                              "REVERSE %s Txns Exchange Rates on Account %s between %s - %s COMPLETED - PLEASE REVIEW" %(iTxnsFound,selectedAccount,startDate, endDate),
                              theMessageType=JOptionPane.ERROR_MESSAGE)

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
        return

    def thin_price_history(statusLabel):
        global toolbox_frame_, debug, lMustRestartAfterSnapChanges

        # based on: price_history_thinner.py
        # (also includes elements from 2017_remove_orphaned_currency_history_entries.py)

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        if moneydance_data is None: return

        if lMustRestartAfterSnapChanges:
            x="Sorry - you have to RESTART MD after running 'FIX - Thin/Purge Price History' to update the csnap cache....."
            myPrint("B",x)
            statusLabel.setText((x).ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            myPopupInformationBox(toolbox_frame_,x,"FIX - THIN/PURGE PRICE HISTORY",JOptionPane.ERROR_MESSAGE)
            return

        # prune historical exchange rates and price history from the given currency
        # this thins price history older than a year by keeping no more than one price per week
        # prices within the last year (or the age_limit_days parameter) are not removed

        totalChangesMade = 0

        diagDisplay = "DIAGNOSE CURRENCY PRICE HISTORY (csnaps)\n"
        diagDisplay += " =======================================\n\n"

        def objects_by_type():
            text = "Objects by type summary:\n"
            objectTypes = [ CurrencyType.SYNCABLE_TYPE_VALUE, CurrencySnapshot.SYNCABLE_TYPE_VALUE, CurrencySplit.SYNCABLE_TYPE_VALUE]
            for objectType in objectTypes:
                xx=""
                if objectType == CurrencyType.SYNCABLE_TYPE_VALUE: xx=" (Currency/Security records)"                     # noqa
                if objectType == CurrencySnapshot.SYNCABLE_TYPE_VALUE: xx=" (Currency/Security price history records)"   # noqa
                if objectType == CurrencySplit.SYNCABLE_TYPE_VALUE: xx=" (Security Stock Split records)"                 # noqa
                objects = moneydance_data.getItemsWithType(objectType)
                text+="  %s: %s %s\n"%(pad(objectType,9), rpad(len(objects),12), xx)
            text+="\n"
            return text

        diagDisplay += objects_by_type()

        def hunt_down_orphans():
            # Hunt down the poor little orphans...!
            orphanSnaps = totalSnaps = 0                                                                        # noqa
            text = ""
            saveRawSnaps={}
            for mdItem in moneydance.getRootAccount().getBook().getSyncer().getSyncedDocument().allItems():
                if not (isinstance(mdItem, MoneydanceSyncableItem)): continue
                if mdItem.getParameter("obj_type", None) != CurrencySnapshot.SYNCABLE_TYPE_VALUE: continue
                saveRawSnaps[mdItem.getParameter("id")] = mdItem
            _currencies = moneydance_data.getCurrencies()
            for _curr in _currencies:
                snapshots = _curr.getSnapshots()
                for snap in snapshots:
                    saveRawSnaps.pop(snap.getParameter("id"))

            oList=[]
            if len(saveRawSnaps)>0:
                lAllValid=True
                for _value in saveRawSnaps.values():
                    if not _value.getCurrencyParameter(None, "curr", None): lAllValid=False
                    oList.append(_value)
                if lAllValid:
                    # Sort and make pretty for Derek ;->
                    oList = sorted(oList, key=lambda sort_x: (sort_x.getCurrencyParameter(None, "curr", None).getCurrencyType(),sort_x.getParameter("curr", None),sort_x.getDateInt()))

                _last = None
                for _x in oList:
                    orphanSnaps += 1
                    chk = _x.getCurrencyParameter(None, "curr", None)
                    if chk: chk = _x.getCurrencyParameter(None, "curr", None).getCurrencyType()
                    if _last != chk:
                        text+=" \n%s:\n" %(chk)
                        _last = chk
                    if debug:
                        text+=" >> Orp/Dup: %s %s\n" %(_x.getUUID(),_x)
                    else:
                        text+=" >> Orp/Dup: %s\n" %(_x)

            for snap in moneydance_data.getItemsWithType(CurrencySnapshot.SYNCABLE_TYPE_VALUE):
                totalSnaps += 1
                if snap.getParameter("curr", None) is None or moneydance_data.getItemForID(snap.getParameter("curr", None)) is None:
                    if not saveRawSnaps.get(snap.getParameter("id",None)):
                        orphanSnaps += 1
                        saveRawSnaps[snap.getParameter("id")] = snap
                        if debug:
                            text+=" >> Orp (no Curr): %s %s\n" %(snap.getUUID(), snap)
                        else:
                            text+=" >> Orp (no Curr): %s\n" %(snap)
                        oList.append(snap)

            if orphanSnaps:
                text+="\nWARNING: %s of %s currency or security snapshots were orphans/duplicates/stranded (or had no Currency link)\n" %(orphanSnaps, totalSnaps)
                text+="(NOTE: The system 'hides' duplicate price history records for the same currency/date.....)   \n"
            else:
                text+="No price history snapshot orphans/duplicates detected!\n"

            del saveRawSnaps

            oList = sorted(oList, key=lambda sort_x: (sort_x.getParameter("curr", None),sort_x.getDateInt()))

            return text, orphanSnaps, oList

        txt, orphanSnaps, orphans_to_delete = hunt_down_orphans()
        diagDisplay += txt

        def snaps_by_currency():
            text = ""
            _currencies = moneydance_data.getCurrencies().getAllCurrencies()
            _currencies = sorted(_currencies, key=lambda sort_x: (sort_x.getName().upper()))
            lastC = None
            # noinspection PyUnresolvedReferences
            iAll=iCurrs=iSecs=0
            for theCType in [CurrencyType.Type.CURRENCY, CurrencyType.Type.SECURITY]:                           # noqa
                for _currency in _currencies:
                    if _currency.getCurrencyType() != theCType: continue
                    iAll+=1
                    if _currency.getCurrencyType() == CurrencyType.Type.CURRENCY: iCurrs+=1                     # noqa
                    if _currency.getCurrencyType() == CurrencyType.Type.SECURITY: iSecs+=1                      # noqa
                    if lastC != _currency.getCurrencyType():
                        text+="\n%s:\n" % _currency.getCurrencyType()
                        lastC = _currency.getCurrencyType()
                    _snapshots = _currency.getSnapshots()
                    text+="  %s (snapshots: %s, splits: %s)\n" %(pad(_currency.getName(), 45), rpad(_snapshots.size(),10), rpad(_currency.getSplits().size(),10))

            text+="\n-----\nTotal Curr/Sec listed: %s Currencies: %s Securities: %s\n" %(iAll,iCurrs,iSecs)

            return text

        diagDisplay += snaps_by_currency()

        def does_base_has_snaps(lDelete=False,lVerbose=True):

            baseCurr = moneydance_data.getCurrencies().getBaseType()
            baseSnapshots = baseCurr.getSnapshots()

            iCountBaseSnapsDeleted = 0
            text = ""
            if baseSnapshots.size() > 0:
                text += "ERROR: base currency %s has %s historical prices! These should be deleted!" % (baseCurr, baseSnapshots.size())
                if lDelete and not lVerbose: myPrint("J","@@ Deleting all snapshots from base Currency @@")
                for baseSnapshot in baseSnapshots:
                    if lDelete:
                        if lVerbose:
                            text += "  @@DELETING@@: %s\n" %(baseSnapshot)
                            myPrint("J","Deleting Base Currency snapshot: %s" %(baseSnapshot))
                        baseSnapshot.deleteItem()
                        iCountBaseSnapsDeleted+=1
                    else:
                        if lVerbose:
                            text += "  snapshot: %s\n" %(baseSnapshot)
            else:
                text += "\n\nBase currency %s has NO historical prices! These is correct!\n\n" % (baseCurr)

            return text, iCountBaseSnapsDeleted

        x, y = does_base_has_snaps()
        diagDisplay += x

        jif = QuickJFrame("Price History Analysis", diagDisplay).show_the_frame()


        if orphanSnaps>0:
            MyPopUpDialogBox(jif,
                             "YOU HAVE ORPHAN/STRANDED Price History Records - READ THIS FIRST",
                             theMessage="These are either 'Orphaned' records with no Currency linkage;\n"
                                        "or they are duplicated records (i.e. multiple records with the same date due to a MD bug)..\n"
                                        "These are 'stranded' / hidden from view. Once you delete the visible record, any Orphan on the same date will reappear\n"
                                        "BEST PRACTICE (after reviewing the Simulation Log) is as follows:\n"
                                        "1. Select 'Only Delete Orphans Mode' and ALL Currencies and ALL Securities. Then Execute\n"
                                        "2. Exit and restart Moneydance (as MD's cache needs refreshing)\n"
                                        "3. Come back here and then choose your desired Purge/Thin mode (if required - optional)\n"
                                        "If you don't follow this sequence, then as you purge, previously hidden records will start appearing\n"
                                        "..(inside or outside the purge/thin window date range you selected)\n"
                                        "(NOTE: Any 'Orphans' that start appearing are harmless, it means they've become visible)",
                             theWidth=180,
                             theTitle="THIN/PURGE PRICE HISTORY",
                             OKButtonText="ACKNOWLEDGE",lAlertLevel=1).go()

        saveColor = JLabel("TEST").getForeground()

        # prune historical exchange rates and price history from the given currency
        # this thins price history older than a year by keeping no more than one price per week
        # prices within the last year (or the age_limit_days parameter) are not removed

        dropdownCurrs=ArrayList()
        dropdownSecs=ArrayList()
        currencies = moneydance_data.getCurrencies().getAllCurrencies()
        for curr in currencies:
            if curr.getCurrencyType() == CurrencyType.Type.CURRENCY: dropdownCurrs.add(curr)                    # noqa
            if curr.getCurrencyType() == CurrencyType.Type.SECURITY: dropdownSecs.add(curr)                     # noqa
        dropdownCurrs=sorted(dropdownCurrs, key=lambda sort_x: (sort_x.getName().upper()))
        dropdownSecs=sorted(dropdownSecs, key=lambda sort_x: (sort_x.getName().upper()))
        dropdownCurrs.insert(0,"<EXCLUDE Currencies>")
        dropdownCurrs.insert(0,"<ALL Currencies>")
        dropdownSecs.insert(0,"<EXCLUDE Securities>")
        dropdownSecs.insert(0,"<ALL Securities>")
        del currencies

        label_simulate = JLabel("Simulate with no changes?")
        user_simulate = JCheckBox("(Uncheck to make changes)", True)
        user_simulate.setName("user_simulate")

        purgeStrings = ["<DO NOTHING>",
                        "Thin Mode (Thin older than cutoff)",
                        "Purge Mode (Delete all older than cutoff)",
                        "Only Delete Orphans Mode (No Purge/Thin, just Delete Orphans)"]

        if moneydance_data.getCurrencies().getBaseType().getSnapshots().size()>0:
            purgeStrings.append("Only Delete Base Records (No Purge/Thin, just Delete Base Records)")

        labelPurgeOrThinMode = JLabel("Select the mode of operation:")
        user_purgeOrThinMode = JComboBox(purgeStrings)
        user_purgeOrThinMode.setName("user_purgeOrThinMode")
        user_purgeOrThinMode.setSelectedIndex(0)

        label_age_limit_days = JLabel("Thin/Purge records older than how many days? (1 to 1825 days)")
        user_age_limit_days = JTextField(5)
        user_age_limit_days.setDocument(JTextFieldLimitYN(5, False, "CURR"))
        user_age_limit_days.setText("")
        user_age_limit_days.setName("user_age_limit_days")
        user_age_limit_days.setEnabled(False)

        label_max_days_between_thinned = JLabel("When Thinning, keep no more than one price per x days? (1 to 31 days)")
        user_max_days_between_thinned = JTextField(3)
        user_max_days_between_thinned.setDocument(JTextFieldLimitYN(3, False, "CURR"))
        user_max_days_between_thinned.setText("")
        user_max_days_between_thinned.setName("user_max_days_between_thinned")
        user_max_days_between_thinned.setEnabled(False)

        label_includeCurrencies = JLabel("Thin/purge Currencies (All/Exclude/Select)?")
        user_includeCurrencies = JComboBox(dropdownCurrs)
        user_includeCurrencies.setSelectedIndex(1)
        user_includeCurrencies.setName("user_includeCurrencies")
        user_includeCurrencies.setEnabled(False)

        label_includeSecurities = JLabel("Thin/purge Securities (All/Exclude/Select)?")
        user_includeSecurities = JComboBox(dropdownSecs)
        user_includeSecurities.setSelectedIndex(1)
        user_includeSecurities.setName("user_includeSecurities")
        user_includeSecurities.setEnabled(False)

        labelPurgeOrphans = JLabel("While Purging/Thinning, also delete any/all Orphan/duplicate Snapshots found?")
        user_purgeOrphans = JCheckBox("(will only delete Orphans matching your ^^Curr/Sec^^ filters above)", False)
        user_purgeOrphans.setEnabled( orphanSnaps>0 )
        user_purgeOrphans.setName("user_purgeOrphans")
        user_purgeOrphans.setEnabled(False)

        labelPurgeBase = JLabel("While Purging/Thinning, also delete all Snapshots found on Base Currency?")
        user_purgeBase = JCheckBox("(will delete all Base Currency snapshots)", False)
        user_purgeBase.setEnabled(moneydance_data.getCurrencies().getBaseType().getSnapshots().size()>0 )
        user_purgeBase.setName("user_purgeBase")
        user_purgeBase.setEnabled(False)

        labelSaveTrunk = JLabel("Consolidate into new Trunk File after mass thin/purge process?")
        user_SaveTrunk = JCheckBox("(compacts/rewrites Dataset (trunk file) & clears *.mdtxn files)", False)
        user_SaveTrunk.setName("user_SaveTrunk")
        user_SaveTrunk.setEnabled(False)

        labelVERBOSE = JLabel("VERBOSE mode = Extra logfile output on all steps?")
        user_VERBOSE = JCheckBox("", False)
        user_VERBOSE.setName("user_VERBOSE")
        user_VERBOSE.setEnabled(False)

        labelSTATUS = JLabel("")
        labelSTATUS2 = JLabel("")

        userFilters = JPanel(GridLayout(0, 2))

        class PanelAction(AbstractAction):

            def __init__(self, thePanel, iOrphs):
                self.thePanel=thePanel
                self.iOrphs=iOrphs

            def actionPerformed(self, event):                                                                   # noqa
                global debug
                myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event)

                the_simulate = None
                the_purgeOrThinMode = None
                the_age_limit_days = None
                the_max_days_between_thinned = None
                the_includeCurrencies = None
                the_includeSecurities = None
                the_purgeOrphans = None
                the_purgeBase = None
                the_SaveTrunk = None
                the_VERBOSE = None
                saveDropDownStateToo = None

                _components = self.thePanel.getComponents()
                for _theComponent in _components:

                    if isinstance(_theComponent, (JComboBox, JTextField, JCheckBox, JButton)):
                        if event.getSource().getName() == _theComponent.getName():
                            if _theComponent.getName() == "user_purgeOrThinMode": the_purgeOrThinMode  = _theComponent

                        if _theComponent.getName() == "user_purgeOrThinMode": saveDropDownStateToo  = _theComponent
                        if _theComponent.getName() == "user_simulate": the_simulate  = _theComponent
                        if _theComponent.getName() == "user_includeCurrencies": the_includeCurrencies  = _theComponent
                        if _theComponent.getName() == "user_includeSecurities": the_includeSecurities  = _theComponent
                        if _theComponent.getName() == "user_purgeOrphans": the_purgeOrphans  = _theComponent
                        if _theComponent.getName() == "user_purgeBase": the_purgeBase  = _theComponent
                        if _theComponent.getName() == "user_age_limit_days": the_age_limit_days  = _theComponent
                        if _theComponent.getName() == "user_max_days_between_thinned": the_max_days_between_thinned  = _theComponent
                        if _theComponent.getName() == "user_SaveTrunk": the_SaveTrunk  = _theComponent
                        if _theComponent.getName() == "user_VERBOSE": the_VERBOSE  = _theComponent

                if the_simulate:
                    if not the_simulate.isSelected():
                        if saveDropDownStateToo.getSelectedIndex() > 0:
                            the_SaveTrunk.setEnabled(True)
                        else:
                            the_SaveTrunk.setEnabled(False)
                            the_SaveTrunk.setSelected(False)
                    else:
                        the_SaveTrunk.setEnabled(False)
                        the_SaveTrunk.setSelected(False)

                # noinspection PyUnresolvedReferences
                if the_purgeOrThinMode:
                    if the_purgeOrThinMode.getSelectedItem().lower().startswith("<DO NOTHING>".lower()):        # noqa
                        the_age_limit_days.setEnabled(False)
                        the_max_days_between_thinned.setEnabled(False)
                        the_includeCurrencies.setEnabled(False)
                        the_includeSecurities.setEnabled(False)
                        the_purgeOrphans.setEnabled(False)
                        the_purgeBase.setEnabled(False)
                        the_SaveTrunk.setEnabled(False)
                        the_VERBOSE.setEnabled(False)
                    elif the_purgeOrThinMode.getSelectedItem().lower().startswith("Thin Mode".lower()):         # noqa
                        the_age_limit_days.setEnabled(True)
                        the_age_limit_days.setText("90")
                        the_max_days_between_thinned.setEnabled(True)
                        the_max_days_between_thinned.setText("7")
                        the_includeCurrencies.setEnabled(True)
                        the_includeSecurities.setEnabled(True)
                        the_purgeOrphans.setEnabled(self.iOrphs>0)
                        the_purgeBase.setEnabled(moneydance_data.getCurrencies().getBaseType().getSnapshots().size()>0)
                        the_SaveTrunk.setEnabled(True)
                        the_VERBOSE.setEnabled(True)
                    elif the_purgeOrThinMode.getSelectedItem().lower().startswith("Purge Mode".lower()):        # noqa
                        the_age_limit_days.setEnabled(True)
                        the_age_limit_days.setText("730")
                        the_max_days_between_thinned.setText("")
                        the_max_days_between_thinned.setEnabled(False)
                        the_includeCurrencies.setEnabled(True)
                        the_includeSecurities.setEnabled(True)
                        the_purgeOrphans.setEnabled(self.iOrphs>0)
                        the_purgeBase.setEnabled(moneydance_data.getCurrencies().getBaseType().getSnapshots().size()>0)
                        the_SaveTrunk.setEnabled(True)
                        the_VERBOSE.setEnabled(True)
                    elif the_purgeOrThinMode.getSelectedItem().lower().startswith("Only Delete Orphans".lower()):  # noqa
                        if self.iOrphs>0:
                            the_age_limit_days.setEnabled(False)
                            the_age_limit_days.setText("")
                            the_max_days_between_thinned.setText("")
                            the_max_days_between_thinned.setEnabled(False)
                            the_includeCurrencies.setEnabled(True)
                            the_includeCurrencies.setSelectedIndex(1)
                            the_includeSecurities.setEnabled(True)
                            the_includeSecurities.setSelectedIndex(1)
                            the_purgeOrphans.setEnabled(False)
                            the_purgeOrphans.setSelected(False)
                            the_purgeBase.setEnabled(False)
                            the_purgeBase.setSelected(False)
                            the_VERBOSE.setEnabled(True)
                            if not(the_simulate.isSelected()):
                                the_SaveTrunk.setEnabled(True)
                        else:
                            the_purgeOrThinMode.setSelectedIndex(0)
                    elif the_purgeOrThinMode.getSelectedItem().lower().startswith("Only Delete Base Records".lower()):  # noqa
                        if moneydance_data.getCurrencies().getBaseType().getSnapshots().size()>0:
                            the_age_limit_days.setEnabled(False)
                            the_age_limit_days.setText("")
                            the_max_days_between_thinned.setText("")
                            the_max_days_between_thinned.setEnabled(False)
                            the_includeCurrencies.setEnabled(False)
                            the_includeCurrencies.setSelectedIndex(1)
                            the_includeSecurities.setEnabled(False)
                            the_includeSecurities.setSelectedIndex(1)
                            the_purgeOrphans.setEnabled(False)
                            the_purgeOrphans.setSelected(False)
                            the_purgeBase.setEnabled(False)
                            the_purgeBase.setSelected(False)
                            the_VERBOSE.setEnabled(True)
                            if not(the_simulate.isSelected()):
                                the_SaveTrunk.setEnabled(True)
                        else:
                            the_purgeOrThinMode.setSelectedIndex(0)

                myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
                return

        userFilters.add(label_simulate)
        userFilters.add(user_simulate)
        userFilters.add(labelPurgeOrThinMode)
        userFilters.add(user_purgeOrThinMode)
        userFilters.add(label_age_limit_days)
        userFilters.add(user_age_limit_days)
        userFilters.add(label_max_days_between_thinned)
        userFilters.add(user_max_days_between_thinned)
        userFilters.add(label_includeCurrencies)
        userFilters.add(user_includeCurrencies)
        userFilters.add(label_includeSecurities)
        userFilters.add(user_includeSecurities)
        userFilters.add(labelPurgeOrphans)
        userFilters.add(user_purgeOrphans)
        userFilters.add(labelPurgeBase)
        userFilters.add(user_purgeBase)
        userFilters.add(labelSaveTrunk)
        userFilters.add(user_SaveTrunk)
        userFilters.add(labelVERBOSE)
        userFilters.add(user_VERBOSE)
        userFilters.add(labelSTATUS)
        userFilters.add(labelSTATUS2)

        components = userFilters.getComponents()
        for theComponent in components:
            if isinstance(theComponent, (JComboBox,JTextField,JCheckBox)):
                theComponent.addActionListener(PanelAction( userFilters, orphanSnaps))

        while True:
            options = ["EXIT", "PROCEED"]
            userAction = (JOptionPane.showOptionDialog(jif,
                                                       userFilters,
                                                       "THIN PRICE HISTORY",
                                                       JOptionPane.OK_CANCEL_OPTION,
                                                       JOptionPane.QUESTION_MESSAGE,
                                                       moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                       options, options[0]))
            if userAction != 1:
                statusLabel.setText(("THIN PRICE HISTORY - No changes made.....").ljust(800, " "))
                statusLabel.setForeground(Color.BLUE)
                myPopupInformationBox(jif,"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
                return

            lDoNOTHING = purgeStrings.index(user_purgeOrThinMode.getSelectedItem())== 0
            lThinMode = purgeStrings.index(user_purgeOrThinMode.getSelectedItem())== 1
            lPurgeMode = purgeStrings.index(user_purgeOrThinMode.getSelectedItem())== 2
            purgeOrphansONLY = purgeStrings.index(user_purgeOrThinMode.getSelectedItem())== 3
            purgeBaseONLY = purgeStrings.index(user_purgeOrThinMode.getSelectedItem())== 4

            simulate = user_simulate.isSelected()
            age_limit_days = user_age_limit_days.getText()
            max_days_between_thinned = user_max_days_between_thinned.getText()
            purgeOrphans = user_purgeOrphans.isSelected()
            purgeBase = user_purgeBase.isSelected()
            confirmedSaveTrunk = user_SaveTrunk.isSelected()
            VERBOSE = user_VERBOSE.isSelected()

            if isinstance(user_includeCurrencies.getSelectedItem(),(str,unicode)):
                if str(user_includeCurrencies.getSelectedItem()).startswith("<ALL"):
                    includeCurrencies=True
                elif str(user_includeCurrencies.getSelectedItem()).startswith("<EXCL"):
                    includeCurrencies=False
                else:
                    raise(Exception("THIN PRICE HISTORY INCLUDE CURRENCIES PARAMETER ERROR"))
            elif isinstance(user_includeCurrencies.getSelectedItem(),(CurrencyType)):
                includeCurrencies = user_includeCurrencies.getSelectedItem()
            else:
                raise(Exception("THIN PRICE HISTORY INCLUDE CURRENCIES PARAMETER ERROR2"))

            if isinstance(user_includeSecurities.getSelectedItem(),(str,unicode)):
                if str(user_includeSecurities.getSelectedItem()).startswith("<ALL"):
                    includeSecurities=True
                elif str(user_includeSecurities.getSelectedItem()).startswith("<EXCL"):
                    includeSecurities=False
                else:
                    raise(Exception("THIN PRICE HISTORY INCLUDE SECURITIES PARAMETER ERROR"))
            elif isinstance(user_includeSecurities.getSelectedItem(),(CurrencyType)):
                includeSecurities = user_includeSecurities.getSelectedItem()
            else:
                raise(Exception("THIN PRICE HISTORY INCLUDE SECURITIES PARAMETER ERROR2"))

            paramError=False
            labelSTATUS.setText("")
            labelSTATUS.setForeground(Color.RED)

            if lDoNOTHING:
                labelSTATUS.setText("ERROR: I CANNOT DO NOTHING? PLEASE CHOOSE AN OPTION!")
                continue

            if lThinMode or lPurgeMode:
                # noinspection PyChainedComparsons
                if not StringUtils.isInteger(age_limit_days) or not (int(age_limit_days) >0 and int(age_limit_days) <= (365*5)):        # noqa
                    user_age_limit_days.setForeground(Color.RED)
                    labelSTATUS.setText("ERROR: age limit days parameter must be between 0 and 1825 (5 years)")
                    paramError=True
                else:
                    age_limit_days=int(age_limit_days)
                    user_age_limit_days.setForeground(saveColor)
            else:
                age_limit_days=0

            if lThinMode:
                # noinspection PyChainedComparsons
                if not StringUtils.isInteger(max_days_between_thinned) or not (int(max_days_between_thinned) >0 and int(max_days_between_thinned) <= (31)):   # noqa
                    user_max_days_between_thinned.setForeground(Color.RED)
                    labelSTATUS.setText("ERROR: max days between dates parameter must be between 0 and 31")
                    paramError=True
                else:
                    max_days_between_thinned=int(max_days_between_thinned)
                    user_max_days_between_thinned.setForeground(saveColor)
            else:
                max_days_between_thinned = 0

            if purgeOrphans and purgeOrphansONLY:
                user_purgeOrphans.setForeground(Color.RED)
                user_purgeOrThinMode.setForeground(Color.RED)
                labelSTATUS.setText("ERROR: you cannot select both purge Orphans and purge ONLY orphans")
                paramError=True
            else:
                user_purgeOrphans.setForeground(saveColor)
                user_purgeOrThinMode.setForeground(saveColor)

            if (purgeOrphans or purgeOrphansONLY) and orphanSnaps < 1:
                user_purgeOrphans.setForeground(Color.RED)
                user_purgeOrThinMode.setForeground(Color.RED)
                labelSTATUS.setText("ERROR: You have no Orphan records to purge - please deselect these options")
                paramError=True
            else:
                user_purgeOrphans.setForeground(saveColor)
                user_purgeOrThinMode.setForeground(saveColor)

            if purgeBase and purgeBaseONLY:
                user_purgeBase.setForeground(Color.RED)
                user_purgeOrThinMode.setForeground(Color.RED)
                labelSTATUS.setText("ERROR: you cannot select both delete Base records and delete ONLY base records")
                paramError=True
            else:
                user_purgeBase.setForeground(saveColor)
                user_purgeOrThinMode.setForeground(saveColor)

            if (purgeBase or purgeBaseONLY) and moneydance_data.getCurrencies().getBaseType().getSnapshots().size() < 1:
                user_purgeBase.setForeground(Color.RED)
                user_purgeOrThinMode.setForeground(Color.RED)
                labelSTATUS.setText("ERROR: You have no Base Currency snapshot records to delete - please deselect these options")
                paramError=True
            else:
                user_purgeBase.setForeground(saveColor)
                user_purgeOrThinMode.setForeground(saveColor)

            if not includeCurrencies and not includeSecurities and (lThinMode or lPurgeMode or purgeOrphansONLY):
                user_includeSecurities.setForeground(Color.RED)
                user_includeCurrencies.setForeground(Color.RED)
                labelSTATUS.setText("ERROR: Please select Security(s) / Currency(s) to process/filter...")
                paramError = True
            else:
                user_includeSecurities.setForeground(saveColor)
                user_includeCurrencies.setForeground(saveColor)

            if (includeCurrencies or includeSecurities) and (purgeBaseONLY):
                user_includeSecurities.setForeground(Color.RED)
                user_includeCurrencies.setForeground(Color.RED)
                labelSTATUS.setText("ERROR: Delete Base Currency records IGNORES filters. Please Deselect Security(s) / Currency(s) filter(s)...")
                paramError = True
            else:
                user_includeSecurities.setForeground(saveColor)
                user_includeCurrencies.setForeground(saveColor)

            if paramError: continue

            break

        components = userFilters.getComponents()
        for theComponent in components:
            if isinstance(theComponent, (JComboBox,JTextField, JCheckBox)):
                for al in theComponent.getActionListeners():
                    theComponent.removeActionListener(al)
        del userFilters

        if lDoNOTHING: raise Exception("ERROR: Why is lDoNOTHING set?")

        if not simulate:
            if not confirm_backup_confirm_disclaimer(jif, statusLabel, "THIN PRICE HISTORY", "Thin Price History?"):
                return

        jif.dispose()

        myPrint("B","THIN PRICE HISTORY - User choose parameters: "
                    "Simulate: %s "
                    "Thin Mode: %s "
                    "Purge Mode: %s "
                    "age_limit_days: %s "
                    "max_days_between_thinned: %s "
                    "includeCurrencies: %s "
                    "includeSecurities: %s "
                    "purgeOrphans: %s "
                    "purgeOrphansONLY: %s "
                    "purgeBase: %s"
                    "purgeBaseONLY: %s"
                    "SaveTrunk: %s"
                    "verbose: %s"
                %(simulate, lThinMode, lPurgeMode, age_limit_days, max_days_between_thinned, includeCurrencies, includeSecurities, purgeOrphans, purgeOrphansONLY, purgeBase, purgeBaseONLY, confirmedSaveTrunk,  VERBOSE))

        del orphanSnaps

        def prune_snapshots(_curr, THINMODE, age_limit_days, max_days_between_thinned, lDelete=False, lVerbose=False):        # noqa

            if THINMODE: ThnTxt="THIN"
            else: ThnTxt="PURGE"

            age_limit_date = DateUtil.incrementDate(DateUtil.getStrippedDateInt(), 0, 0, -(age_limit_days))
            text = "\n>%s: %s'ing snapshots older than %s\n" %(_curr, ThnTxt, age_limit_date)
            text += "  %s BEFORE %s (snapshots: %s, splits: %s)\n"%(_curr, ThnTxt, _curr.getSnapshots().size(), _curr.getSplits().size())
            _snapshots = _curr.getSnapshots()
            old_snapshots = []
            countChanges  = 0
            saveFirstSnapPreserved = None
            for snapshot in _snapshots:
                if snapshot.getDateInt() < age_limit_date:
                    if len(old_snapshots)+1 >= len(_snapshots):
                        text += "  > NOTE: Preserving the newest and last Price History record (so you always have 1): %s\n" %snapshot
                        saveFirstSnapPreserved = snapshot.getDateInt()
                    else:
                        old_snapshots.append(snapshot)
                else:
                    if saveFirstSnapPreserved is None:
                        saveFirstSnapPreserved = snapshot.getDateInt()

            if saveFirstSnapPreserved is None:
                myPrint("B","@@ LOGIC ERROR why saveFirstSnapPreserved == None?")
                saveFirstSnapPreserved = age_limit_date

            last_date = 0
            text += "  %s snapshot(s) are older than cutoff date and eligible to be %s'd'..\n" %(len(old_snapshots),ThnTxt)
            num_thinned = 0
            # This presumes the data is presented oldest, to newest, which the inbuilt comparator/sort seems to do...

            # for snapshot in old_snapshots:
            for _i in range(0, len(old_snapshots)):
                snapshot = old_snapshots[_i]
                snap_date = snapshot.getDateInt()

                if _i+1 < len(old_snapshots):                        # not at end of the records
                    safetyDate = old_snapshots[_i+1].getDateInt()    # take a peek at the next record..
                else:
                    safetyDate = saveFirstSnapPreserved

                if (not THINMODE) \
                        or (THINMODE and DateUtil.calculateDaysBetween(last_date, snap_date) < max_days_between_thinned
                            and DateUtil.calculateDaysBetween(last_date, safetyDate) < max_days_between_thinned+1):  # This ensures there's no huge leap to the next date......
                    if lVerbose:
                        text += "    *** delete snapshot dated %s\n"%(snap_date)
                    num_thinned += 1
                    if lDelete:
                        if lVerbose:
                            myPrint("B","%s PRICE HISTORY: Deleting snapshot: %s" %(ThnTxt,repr(snapshot)))
                        countChanges+=1
                        snapshot.deleteItem()
                else:
                    # don't thin this snapshot, and set the last seen date to it
                    if  lVerbose:
                        text += "    > Not deleting snapshot dated %s (preserving 1 per interval specified)\n"%(snap_date)
                    last_date = snap_date
                _i+=1

            if len(old_snapshots):
                text += "  >> %s'd %s of %s eligible (old) snapshots (%s percent) from %s\n"%(ThnTxt, num_thinned, len(old_snapshots), 100*num_thinned/len(old_snapshots), _curr.getName())
                text += "  >> %s'd %s of %s total snapshots          (%s percent) from %s\n"%(ThnTxt, num_thinned, len(_snapshots), 100*num_thinned/len(_snapshots), _curr.getName())
            else:
                text += "  >> No old snapshots %s'd from %s\n" %(ThnTxt, _curr.getName())

            return text, countChanges

        def prune_all_snapshots(THIN_MODE, age_limit_days, max_days_between_thinned, incCurrencies, incSecurities, lVerbose=False, lDelete=False):       # noqa
            countTheChanges = 0
            _currs = moneydance_data.getCurrencies().getAllCurrencies()
            lastC = None
            text = ""

            if THIN_MODE: Thn_Txt="THIN"
            else: Thn_Txt="PURGE"

            theList = []
            if incCurrencies: theList.append(CurrencyType.Type.CURRENCY)                                        # noqa
            if incSecurities: theList.append(CurrencyType.Type.SECURITY)                                        # noqa

            for theCType in theList:

                for _curr in _currs:

                    if _curr.getCurrencyType() != theCType: continue

                    if (_curr.getCurrencyType() == CurrencyType.Type.CURRENCY                                                  # noqa
                            and incCurrencies and isinstance(incCurrencies,(CurrencyType)) and _curr != incCurrencies):
                        continue
                    if (_curr.getCurrencyType() == CurrencyType.Type.SECURITY                                                   # noqa
                            and incSecurities and isinstance(incSecurities,(CurrencyType)) and _curr != incSecurities):
                        continue

                    if lastC != _curr.getCurrencyType():
                        text+="\n%s:\n" %_curr.getCurrencyType()
                        lastC = _curr.getCurrencyType()

                    _snaps = _curr.getSnapshots()
                    if _snaps.size() >= 1:
                        _txt, _i = prune_snapshots(_curr, THIN_MODE, age_limit_days, max_days_between_thinned, lDelete, lVerbose)
                        text += _txt
                        countTheChanges += _i
                        _snaps = _curr.getSnapshots()
                        text += "  %s AFTER %s (snapshots: %s, splits: %s)\n"%(_curr, Thn_Txt, _snaps.size(), _curr.getSplits().size())
            return text, countTheChanges

        def prune_orphans(_orphans, incCurrencies, incSecurities, lVerbose=False, lDelete=False):

            iPurgeCount=0

            _orphanSnaps = len(_orphans)
            text = "\nReviewing 'orphan' (or duplicates/stranded) snaps...:\n"

            theList = []
            theList.append(None)
            if incCurrencies: theList.append(CurrencyType.Type.CURRENCY)                                        # noqa
            if incSecurities: theList.append(CurrencyType.Type.SECURITY)                                        # noqa

            filteredOrphanList=[]
            for theCType in theList:
                for _o in _orphans:
                    theCurr = _o.getCurrencyParameter(None, "curr", None)

                    if theCType is None:
                        if theCurr is not None: continue
                    else:
                        if theCurr.getCurrencyType() != theCType: continue

                    if theCurr:
                        if (theCurr.getCurrencyType() == CurrencyType.Type.CURRENCY                                                  # noqa
                                and incCurrencies and isinstance(incCurrencies,(CurrencyType)) and theCurr != incCurrencies):
                            continue
                        if (theCurr.getCurrencyType() == CurrencyType.Type.SECURITY                                                   # noqa
                                and incSecurities and isinstance(incSecurities,(CurrencyType)) and theCurr != incSecurities):
                            continue
                    filteredOrphanList.append(_o)

            del _orphans

            if len(filteredOrphanList)<1:
                text += "\nNo *filtered* currency or security snapshots were 'orphans' (duplicates/stranded)\n\n"
            else:
                text += "\n%s *filtered* currency or security snapshots were 'orphans' (duplicates/stranded)\n\n"%(len(filteredOrphanList))
                if lDelete:
                    myPrint("B","Logging 'orphan' snaps for deletion....")
                    text += "Logging 'orphan' snaps for deletion....\n"
                    if lVerbose:
                        for _o in filteredOrphanList:
                            text += "Logging 'Orphan' to delete: %s\n" %(repr(_o))
                            myPrint("B","Logging 'Orphan' to delete: %s" %(repr(_o)))
                    moneydance_data.logRemovedItems(filteredOrphanList)
                    iPurgeCount+=len(filteredOrphanList)
                else:
                    if lVerbose:
                        for _o in filteredOrphanList: text += "  'Orphan' found: %s\n" %(_o)
                    text += "\nSimulation so no 'orphan' snaps will be deleted....\n"
            del filteredOrphanList

            return text, iPurgeCount

        if lThinMode: ThnPurgeTxt="THIN"
        elif lPurgeMode: ThnPurgeTxt="PURGE"
        elif purgeOrphansONLY: ThnPurgeTxt="PURGE ORPHANS"
        elif purgeBaseONLY: ThnPurgeTxt="PURGE BASE CURRENCY RECORDS"
        else: ThnPurgeTxt="THIN/PURGE"

        if simulate: x="SIMULATE"
        else: x="DATABASE UPDATE"

        purgingMsg = MyPopUpDialogBox(toolbox_frame_,"Please wait: Processing your %s request (%s).." %(ThnPurgeTxt,x),
                                      theTitle="FIX - Thin/Purge",
                                      theWidth=100, lModal=False,OKButtonText="WAIT")
        purgingMsg.go()

        diagDisplay += "\n\n *** EXECUTING %s PRICE HISTORY ***\n" %(ThnPurgeTxt)
        diagDisplay += "\nUser choose parameters:\n" \
                       " >> Simulate:                 %s\n" \
                       " >> Purge Mode:               %s\n" \
                       " >> Thin Mode:                %s\n" \
                       " >> age_limit_days:           %s (%s)\n" \
                       " >> max_days_between_thinned: %s\n" \
                       " >> includeCurrencies:        %s\n" \
                       " >> includeSecurities:        %s\n" \
                       " >> purgeOrphans:             %s\n" \
                       " >> purgeOrphansONLY:         %s\n" \
                       " >> purgeBase:                %s\n" \
                       " >> purgeBaseONLY:            %s\n" \
                       " >> confirmedSaveTrunk:       %s\n" \
                       " >> VERBOSE:                  %s\n" \
                       %(simulate, lPurgeMode, lThinMode, age_limit_days, DateUtil.incrementDate(DateUtil.getStrippedDateInt(), 0, 0, -(age_limit_days)),max_days_between_thinned, includeCurrencies, includeSecurities, purgeOrphans, purgeOrphansONLY, purgeBase, purgeBaseONLY, confirmedSaveTrunk, VERBOSE)

        diagDisplay+="\n%s PRICE HISTORY\n" \
                     " =================\n" %(ThnPurgeTxt)

        if not simulate:
            moneydance_data.setRecalcBalances(False)
            moneydance_ui.setSuspendRefresh(True)

        if simulate:
            diagDisplay += "\n ** SIMULATION MODE - NO CHANGES MADE ** \n"
        else:
            diagDisplay += "\n ** %s MODE - CHANGES BEING MADE! ** \n" %(ThnPurgeTxt)

        if purgeOrphans or purgeOrphansONLY:
            x,i = prune_orphans(orphans_to_delete, includeCurrencies, includeSecurities, lVerbose=VERBOSE, lDelete=(not simulate))
            diagDisplay += x
            totalChangesMade += i

        if purgeBase or purgeBaseONLY:
            x,i = does_base_has_snaps(lDelete=(not simulate), lVerbose=VERBOSE)
            diagDisplay += x
            totalChangesMade += i

        if lPurgeMode or lThinMode:  # Mutually exclusive!
            txt, i = prune_all_snapshots(lThinMode, age_limit_days, max_days_between_thinned, includeCurrencies, includeSecurities, lVerbose=VERBOSE, lDelete=(not simulate))
            diagDisplay += txt
            totalChangesMade += i

        if not simulate:
            moneydance_ui.getMain().saveCurrentAccount()
            moneydance_data.setRecalcBalances(True)
            moneydance_ui.setSuspendRefresh(False)		# This does this too: book.notifyAccountModified(root)

        if confirmedSaveTrunk:
            if not simulate:
                if totalChangesMade > 0:
                    myPrint("B","%s PRICE HISTORY: Calling saveTrunkFile()...." %(ThnPurgeTxt))
                    diagDisplay += "\n\n ======\nSaving Trunk File.....\n ======\n\n"
                    moneydance_data.saveTrunkFile()
                else:
                    myPrint("B","%s PRICE HISTORY: No changes made - so NOT Calling saveTrunkFile()...." %(ThnPurgeTxt))
                    diagDisplay += "No changes made, so **NOT** Saving Trunk File.....\n"
            else:
                diagDisplay += "Simulation mode >> (Not) Saving Trunk File.....\n"

        purgingMsg.kill()

        diagDisplay+="\n\n ANALYSIS AFTER %s:\n" %(ThnPurgeTxt)
        diagDisplay+="===============================\n"

        diagDisplay += objects_by_type()

        diagDisplay += snaps_by_currency()

        diagDisplay+="\n"

        if simulate:
            x="SIMULATION MODE ONLY"
        else:
            x="UPDATE/%s MODE" %(ThnPurgeTxt)

        if totalChangesMade > 0:
            lMustRestartAfterSnapChanges = True
            diagDisplay += ("\n\n *** %s changes were made! ***\n\n" %(totalChangesMade)).upper()
        else:
            diagDisplay += "\n\n *** no changes were made! ***\n\n".upper()

        diagDisplay+="\n%s PRICE HISTORY in %s COMPLETED!\n" %(ThnPurgeTxt,x)
        diagDisplay+="\n<END>"

        statusLabel.setText((("%s PRICE HISTORY - %s >> Successfully executed (%s changes made)" %(ThnPurgeTxt,x,totalChangesMade)).ljust(800, " ")))
        statusLabel.setForeground(Color.RED)
        myPrint("B", "%s PRICE HISTORY - %s >> Successfully executed (%s changes made)" %(ThnPurgeTxt,x,totalChangesMade))

        jif = QuickJFrame("Price History Analysis", diagDisplay).show_the_frame()
        if simulate:
            MyPopUpDialogBox(jif, "%s PRICE HISTORY - %s >> Successfully executed" %(ThnPurgeTxt,x),"",200,"THIN/PRUNE PRICE HISTORY").go()
        else:
            if totalChangesMade > 0:
                play_the_money_sound()
                MyPopUpDialogBox(jif, "%s PRICE HISTORY - %s >> Successfully executed %s changes - PLEASE RESTART MD NOW" %(ThnPurgeTxt,x,totalChangesMade),"",200,"THIN/PRUNE PRICE HISTORY").go()
            else:
                MyPopUpDialogBox(jif, "%s PRICE HISTORY - %s >> Successfully executed - NO CHANGES NECESSARY / MADE" %(ThnPurgeTxt,x),"",200,"THIN/PRUNE PRICE HISTORY").go()

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
        return

    def extract_attachments(statusLabel):
        global toolbox_frame_, debug, MYPYTHON_DOWNLOAD_URL

        # export_all_attachments.py

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        ask=MyPopUpDialogBox(toolbox_frame_,"EXTRACT ATTACHMENTS - For Your Information",
                             "This will extract all your attachments to a directory....\n"
                             "I also have two scripts which will extract attachments alongside your Investment or Bank Account Registers\n"
                             "- extract_account_registers_csv.py\n"
                             "- extract_investment_transactions_csv.py\n"
                             "Visit: %s to download\n\n"
                             "Please select a directory to extract attachments to...\n"
                             "I will create a sub-directory called 'EXTRACT_MD_ATTACHMENTS-x' (I will append a unique number)"
                             % (MYPYTHON_DOWNLOAD_URL),
                             theWidth=225,
                             theTitle="EXTRACT ATTACHMENTS",
                             OKButtonText="PROCEED", lCancelButton=True)
        if not ask.go():
            return

        while True:
            theDir=None
            lExit=False
            if Platform.isOSX():
                System.setProperty("com.apple.macos.use-file-dialog-packages", "true")  # In theory prevents access to app file structure (but doesnt seem to work)
                System.setProperty("apple.awt.fileDialogForDirectories", "true")

                fDialog = FileDialog(toolbox_frame_, "Select location to Extract Attachments to... (CANCEL=ABORT)")
                fDialog.setMultipleMode(False)
                fDialog.setMode(FileDialog.LOAD)
                fDialog.setDirectory(get_home_dir())

                fDialog.setVisible(True)

                System.setProperty("com.apple.macos.use-file-dialog-packages","true")  # In theory prevents access to app file structure (but doesnt seem to work)
                System.setProperty("apple.awt.fileDialogForDirectories", "false")

                if (fDialog.getDirectory() is None) or str(fDialog.getDirectory()) == "" or \
                        (fDialog.getFile() is None) or str(fDialog.getFile()) == "":
                    myPrint("P", "User did not select Search Directory... Aborting")
                    lExit=True
                    fDialog.dispose()
                    del fDialog
                    break
                else:
                    # noinspection PyTypeChecker
                    theDir = os.path.join(fDialog.getDirectory(),str(fDialog.getFile()))
                    fDialog.dispose()
                    del fDialog
            else:
                # UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName())
                # Switch to JFileChooser for Folder selection on Windows/Linux - to allow folder selection
                fileChooser = JFileChooser( get_home_dir() )
                fileChooser.setMultiSelectionEnabled( False )
                fileChooser.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY)

                fileChooser.setDialogTitle("Select location to Extract Attachments to... (CANCEL=ABORT)")
                fileChooser.setPreferredSize(Dimension(700, 700))
                returnValue = fileChooser.showDialog(toolbox_frame_, "EXTRACT ATTACHMENTS")

                if returnValue == JFileChooser.CANCEL_OPTION:
                    myPrint("P", "No start point was selected - aborting..")
                    lExit=True
                    break
                elif fileChooser.getSelectedFile() is None or fileChooser.getSelectedFile().getName()=="":
                    myPrint("P", "No start point was selected - aborting..")
                    lExit=True
                    break
                else:
                    theDir = fileChooser.getSelectedFile().getAbsolutePath()

            if not os.path.exists(theDir):
                myPopupInformationBox(toolbox_frame_, "ERROR - the folder does not exist?", "SELECT EXTRACT FOLDER", JOptionPane.WARNING_MESSAGE)
                continue

            theDir = os.path.join(theDir,"EXTRACT_MD_ATTACHMENTS-%s" %(UUID.randomUUID().toString()))
            if os.path.exists(theDir):
                myPopupInformationBox(toolbox_frame_, "SORRY - the folder %s already exists... I need to create it myself...", "SELECT EXTRACT FOLDER", JOptionPane.WARNING_MESSAGE)
                continue

            break

        iSkip=0
        iCountAttachments = 0
        textLog = "\nEXTRACT ATTACHMENTS:\n" \
                  "====================\n\n"
        textLog += "Base extract folder: %s%s\n\n" %(theDir,os.path.sep)
        textRecords = []

        if not lExit and theDir is not None:
            exportFolder = theDir

            txnSet = moneydance_data.getTransactionSet()

            File(exportFolder).mkdirs()

            myPrint("B", "Will export all attachments to %s"%(exportFolder))

            pleaseWait = MyPopUpDialogBox(toolbox_frame_,
                                          "Please wait: extracting attachments..",
                                          theTitle="EXTRACT ATTACHMENTS",
                                          theWidth=100,
                                          lModal=False,
                                          OKButtonText="WAIT")
            pleaseWait.go()

            for txn in txnSet.iterableTxns():
                for attachKey in txn.getAttachmentKeys():
                    iCountAttachments+=1
                    attachTag = txn.getAttachmentTag(attachKey)
                    txnDate = txn.getDateInt()
                    attachFile = File(attachTag).getName()
                    attachFolder = os.path.join(exportFolder,"ACCT-TYPE-%s"%(txn.getAccount().getAccountType()),"ACCT-%s" %(txn.getAccount().getAccountName()))
                    File(attachFolder).mkdirs()
                    outputPath = os.path.join(attachFolder, "{:04d}-{:02d}-{:02d}-{}-{}".format(txnDate/10000, (txnDate/100)%100,  txnDate%100, str(iCountAttachments).zfill(5), attachFile))
                    if os.path.exists(outputPath):
                        iSkip+=1
                        myPrint("B", "Error - path: %s already exists... SKIPPING THIS ONE!" %outputPath)
                        textLog+=("Error - path: %s already exists... SKIPPING THIS ONE!\n" %outputPath)
                    else:
                        myPrint("P", "Exporting attachment [%s]" %(os.path.basename(outputPath)))
                        try:
                            outStream = FileOutputStream(File(outputPath))
                            inStream = moneydance_data.getLocalStorage().openFileForReading(attachTag)
                            IOUtils.copyStream(inStream, outStream)
                            outStream.close()
                            inStream.close()
                            textRecords.append([txn.getAccount().getAccountType(), txn.getAccount().getAccountName(), txn.getDateInt(),
                                                "%s %s %s %s %s .%s\n"
                                                %(pad(str(txn.getAccount().getAccountType()),15),pad(txn.getAccount().getAccountName(),30),txn.getDateInt(),rpad(txn.getValue()/100.0,10),pad(txn.getDescription(),20),outputPath[len(exportFolder):])])
                        except:
                            myPrint("B","Error extracting file - will SKIP : %s" %(outputPath))
                            textLog+=("Error extracting file - will SKIP : %s\n" %(outputPath))
                            iSkip+=1

            textRecords=sorted(textRecords, key=lambda _sort: (_sort[0],_sort[1],_sort[2]))
            for r in textRecords:
                textLog+=r[3]

            if iSkip:
                textLog+="\nERRORS/SKIPPED: %s (review console log for details)\n" %(iSkip)

            textLog+="\n<END>"

            try:
                log=open(os.path.join(exportFolder,"Extract_Attachments_LOG.txt"), "w")
                log.write(textLog)
                log.close()
            except:
                pass

            pleaseWait.kill()

            statusLabel.setText(("FINISHED: %s attachments extracted (%s skipped)..." %(iCountAttachments,iSkip)).ljust(800, " "))
            statusLabel.setForeground(Color.BLUE)

            play_the_money_sound()

            myPrint("B", "\n@@FINISHED: %s attachments extracted (%s skipped)...\n" %(iCountAttachments,iSkip))

            if iSkip <1:
                myPopupInformationBox(toolbox_frame_,"I have extracted %s attachments for you.." %(iCountAttachments))
            else:
                myPopupInformationBox(toolbox_frame_,"I have extracted %s attachments for you.. AND YOU HAD %s Missing/Errors?" %(iCountAttachments,iSkip),theMessageType=JOptionPane.ERROR_MESSAGE)

            try:
                helper = moneydance.getPlatformHelper()
                helper.openDirectory(File(exportFolder))
            except:
                pass

        else:
            statusLabel.setText(("NO ATTACHMENTS EXTRACTED!").ljust(800, " "))
            statusLabel.setForeground(Color.RED)

        return

    def diagnose_attachments(statusLabel):
        global toolbox_frame_, debug, DARK_GREEN, lCopyAllToClipBoard_TB
        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        if moneydance_data is None: return

        scanningMsg = MyPopUpDialogBox(toolbox_frame_,"Please wait: searching Database and filesystem for attachments..",
                                       theTitle="ATTACHMENT(S) SEARCH",
                                       theWidth=100, lModal=False,OKButtonText="WAIT")
        scanningMsg.go()

        myPrint("P", "Scanning database for attachment data..")
        book = moneydance_data

        attachmentList={}
        attachmentLocations={}

        iObjectsScanned=0
        iTxnsScanned=0

        iTxnsWithAttachments = 0
        iAttachmentsFound = 0
        iAttachmentsNotInLS = 0
        iDuplicateKeys = 0
        attachmentsNotInLS=[]

        diagDisplay="ANALYSIS OF ATTACHMENTS\n\n"

        attachmentFullPath = os.path.join(moneydance_data.getRootFolder().getCanonicalPath(), "safe", moneydance.getCurrentAccountBook().getAttachmentsFolder())

        LS = moneydance.getCurrentAccountBook().getLocalStorage()

        txnSet = book.getTransactionSet()
        for _mdItem in txnSet.iterableTxns():

            iObjectsScanned+=1

            if not (_mdItem.hasAttachments() or len(_mdItem.getAttachmentKeys())>0):
                continue

            iTxnsWithAttachments+=1
            x="Found Record with %s Attachment(s): %s" %(len(_mdItem.getAttachmentKeys()),_mdItem)
            myPrint("D",x)
            if debug: diagDisplay+=(x+"\n")

            if attachmentList.get(_mdItem.getUUID()):
                iDuplicateKeys += 1
                x="@@ Error %s already exists in my attachment list...!?" %_mdItem.getUUID()
                myPrint("DB", x)
                if debug: diagDisplay+=(x+"\n")

            attachmentList[_mdItem.getUUID()] = [
                _mdItem.getUUID(),
                _mdItem.getAccount().getAccountName(),
                _mdItem.getAccount().getAccountType(),
                _mdItem.getDateInt(),
                _mdItem.getValue(),
                _mdItem.getAttachmentKeys()
            ]
            x="Attachment keys: %s" %_mdItem.getAttachmentKeys()
            myPrint("D",x)
            if debug: diagDisplay+=(x+"\n")

            for _key in _mdItem.getAttachmentKeys():
                iAttachmentsFound+=1
                if attachmentLocations.get(_mdItem.getAttachmentTag(_key)):
                    iDuplicateKeys += 1
                    x="@@ Error %s already exists in my attachment location list...!?" %_mdItem.getUUID()
                    myPrint("B", )
                    if debug: diagDisplay+=(x+"\n")

                attachmentLocations[_mdItem.getAttachmentTag(_key)] = [
                    _mdItem.getAttachmentTag(_key),
                    _key,
                    _mdItem.getUUID(),
                    LS.exists(_mdItem.getAttachmentTag(_key))
                ]
                if not LS.exists(_mdItem.getAttachmentTag(_key)):
                    iAttachmentsNotInLS+=1
                    attachmentsNotInLS.append([
                        _mdItem.getUUID(),
                        _mdItem.getAccount().getAccountName(),
                        _mdItem.getAccount().getAccountType(),
                        _mdItem.getDateInt(),
                        _mdItem.getValue(),
                        _mdItem.getAttachmentKeys()
                    ])

                    x="@@ Error - Attachment for Txn DOES NOT EXIST! - Attachment tag: %s" %_mdItem.getAttachmentTag(_key)
                    myPrint("B",x)
                    diagDisplay+=(x+"\n")
                else:
                    x="Attachment tag: %s" %_mdItem.getAttachmentTag(_key)
                    myPrint("D", x)
                    if debug: diagDisplay+=(x+"\n")


        # Now scan the file system for attachments
        myPrint("P", "Now scanning attachment directory(s) and files...:")

        attachmentsRawListFound = []

        typesFound={}

        for root, dirs, files in os.walk(attachmentFullPath):

            for name in files:
                theFile = os.path.join(root,name)[len(attachmentFullPath)-len(moneydance.getCurrentAccountBook().getAttachmentsFolder()):]
                byteSize = os.path.getsize(os.path.join(root,name))
                modified = datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(root,name))).strftime('%Y-%m-%d %H:%M:%S')
                attachmentsRawListFound.append([theFile, byteSize, modified])
                theExtension = os.path.splitext(theFile)[1].lower()

                iCountExtensions = 0
                iBytes = 0
                if typesFound.get(theExtension):
                    iCountExtensions = typesFound.get(theExtension)[1]
                    iBytes = typesFound.get(theExtension)[2]
                typesFound[theExtension] = [theExtension, iCountExtensions+1, iBytes+byteSize ]

                x="Found Attachment File: %s" %theFile
                myPrint("D", x)
                if debug: diagDisplay+=(x+"\n")

        # Now match file system to the list from the database
        iOrphans=0
        iOrphanBytes=0

        orphanList=[]

        for fileDetails in attachmentsRawListFound:
            deriveTheKey = fileDetails[0]
            deriveTheBytes = fileDetails[1]
            deriveTheModified = fileDetails[2]
            if attachmentLocations.get(deriveTheKey.replace(os.path.sep,"/")):
                x="Attachment file system link found in Moneydance database"
                myPrint("D", x)
                if debug: diagDisplay+=(x+"\n")
            else:
                x="Error: Attachment filesystem link missing in Moneydance database: %s" %deriveTheKey
                myPrint("DB", x)
                if debug: diagDisplay+=(x+"\n")
                iOrphans+=1
                iOrphanBytes+=deriveTheBytes
                orphanList.append([deriveTheKey,deriveTheBytes, deriveTheModified])

        msgStr=""

        myPrint("P","\n"*5)

        x="----------------------------------"
        myPrint("B", x)
        msgStr+=(x+"\n")
        diagDisplay+=(x+"\n")

        x = "Objects scanned: %s" %iObjectsScanned
        myPrint("B", x)
        msgStr+=(x+"\n")
        diagDisplay+=(x+"\n")

        x="Transactions scanned: %s" %iTxnsScanned
        myPrint("B", x)
        msgStr+=(x+"\n")
        diagDisplay+=(x+"\n")
        x="Transactions with attachments: %s" %iTxnsWithAttachments
        myPrint("B", x)
        msgStr+=(x+"\n")
        diagDisplay+=(x+"\n")
        x="Total Attachments referenced in Moneydance database (a txn may have multi-attachments): %s" %iAttachmentsFound
        myPrint("B", x)
        msgStr+=(x+"\n")
        diagDisplay+=(x+"\n")
        x="Attachments missing from Local Storage: %s" %iAttachmentsNotInLS
        myPrint("B", x)
        msgStr+=(x+"\n")
        diagDisplay+=(x+"\n")
        x="Total Attachments found in file system: %s (difference %s)" %(len(attachmentsRawListFound),len(attachmentsRawListFound)-iAttachmentsFound)
        myPrint("B", x)
        msgStr+=(x+"\n")
        diagDisplay+=(x+"\n")


        myPrint("P","\n"*1)

        x="Attachment extensions found: %s" %len(typesFound)
        myPrint("B", x)
        diagDisplay+=("\n"+x+"\n")

        iTotalBytes = 0
        sortedExtensions = sorted(typesFound.values(), key=lambda _x: (_x[2]), reverse=True)

        for x in sortedExtensions:
            iTotalBytes+=x[2]

            x="Extension: %s Number: %s Size: %sMB" %(pad(x[0],6),rpad(x[1],12),rpad(round(x[2]/(1000.0 * 1000.0),2),12))
            myPrint("B", x)
            diagDisplay+=(x+"\n")

        x="Attachments on disk are taking: %sMB" %(round(iTotalBytes/(1000.0 * 1000.0),2))
        myPrint("B", x)
        diagDisplay+=(x+"\n")
        msgStr+=(x+"\n")
        x="----------------------------------"
        myPrint("B", x)
        msgStr+=(x+"\n")
        diagDisplay+=(x+"\n\n")

        lErrors=False
        if iAttachmentsNotInLS:
            x = "@@ ERROR: You have %s missing attachment(s) referenced on Moneydance Txns!" %(iAttachmentsNotInLS)
            msgStr+=x+"\n"
            diagDisplay+=(x+"\n\n")
            myPrint("P","")
            myPrint("B",x)
            statusLabel.setText((x.upper()).ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            lErrors=True
            attachmentsNotInLS=sorted(attachmentsNotInLS, key=lambda _x: (_x[3]), reverse=False)
            for theOrphanRecord in attachmentsNotInLS:
                x="Attachment is missing from this Txn: AcctType: %s Account: %s Date: %s Value: %s AttachKey: %s" %(theOrphanRecord[1],
                                                                                                                     theOrphanRecord[2],
                                                                                                                     theOrphanRecord[3],
                                                                                                                     theOrphanRecord[4],
                                                                                                                     theOrphanRecord[5])
                myPrint("B", x)
                diagDisplay+=(x+"\n")
            diagDisplay+="\n"

        if iOrphans:
            x = "@@ ERROR: %s Orphan attachment(s) found, taking up %sMBs" %(iOrphans,round(iOrphanBytes/(1000.0 * 1000.0),2))
            msgStr+=x+"\n"
            diagDisplay+=(x+"\n\n")
            myPrint("P","")
            statusLabel.setText((x.upper()).ljust(800, " "))
            statusLabel.setForeground(Color.RED)

            myPrint("B",x)
            x="Base Attachment Directory is: %s" %os.path.join(moneydance_data.getRootFolder().getCanonicalPath(), "safe","")
            myPrint("P",x)
            diagDisplay+=(x+"\n")
            lErrors=True
            orphanList=sorted(orphanList, key=lambda _x: (_x[2]), reverse=False)
            for theOrphanRecord in orphanList:

                x="Orphaned Attachment >> Txn Size: %sKB Modified %s for file: %s" %(rpad(round(theOrphanRecord[1]/(1000.0),1),6),
                                                                                     pad(theOrphanRecord[2],19),
                                                                                     theOrphanRecord[0])
                diagDisplay+=(x+"\n")
                myPrint("B", x)

        if not lErrors:
            x= "Congratulations! - No orphan attachments detected!".upper()
            myPrint("B",x)
            diagDisplay+=(x+"\n")
            statusLabel.setText((x.upper()).ljust(800, " "))
            statusLabel.setForeground(Color.BLUE)


        if iAttachmentsFound:
            diagDisplay+="\n\nLISTING VALID ATTACHMENTS FOR REFERENCE\n"
            diagDisplay+=" ======================================\n"
            x="\nBase Attachment Directory is: %s" %os.path.join(moneydance_data.getRootFolder().getCanonicalPath(), "safe","")
            diagDisplay+=(x+"\n-----------\n")

            for validLocation in attachmentLocations:
                locationRecord = attachmentLocations[validLocation]
                record = attachmentList[locationRecord[2]]
                diagDisplay+="AT: %s ACT: %s DT: %s Val: %s FILE: %s\n" \
                             %(pad(repr(record[2]),12),
                               pad(str(record[1]),20),
                               record[3],
                               rpad(record[4]/100.0,10),
                               validLocation)

        diagDisplay+='\n<END>'

        scanningMsg.kill()

        jif = QuickJFrame("ATTACHMENT ANALYSIS",diagDisplay).show_the_frame()

        if iOrphans:
            msg = MyPopUpDialogBox(jif,
                                   "You have %s Orphan attachment(s) found, taking up %sMBs" %(iOrphans,round(iOrphanBytes/(1000.0 * 1000.0),2)),
                                   msgStr+"CLICK TO VIEW ORPHANS, or CANCEL TO EXIT",
                                   200,"ORPHANED ATTACHMENTS",
                                   lCancelButton=True,
                                   OKButtonText="CLICK TO VIEW",
                                   lAlertLevel=1)
        elif iAttachmentsNotInLS:
            msg = MyPopUpDialogBox(jif,
                                   "You have %s missing attachment(s) referenced on Moneydance Txns!" %(iAttachmentsNotInLS),
                                   msgStr,
                                   200,"MISSING ATTACHMENTS",
                                   lCancelButton=False,
                                   OKButtonText="OK",
                                   lAlertLevel=1)

        if lErrors:
            pass
        else:
            msg = MyPopUpDialogBox(jif,
                                   x,
                                   msgStr,
                                   200,"ATTACHMENTS STATUS",
                                   lCancelButton=False,
                                   OKButtonText="OK",
                                   lAlertLevel=0)

        myPrint("P","\n"*2)

        if iOrphans:
            if msg.go():        # noqa
                while True:
                    selectedOrphan = JOptionPane.showInputDialog(jif,
                                                                 "Select an Orphan to View",
                                                                 "VIEW ORPHAN (Escape or Cancel to exit)",
                                                                 JOptionPane.WARNING_MESSAGE,
                                                                 None,
                                                                 orphanList,
                                                                 None)
                    if not selectedOrphan:
                        break

                    try:
                        tmpDir = File(moneydance_data.getRootFolder(), "tmp")
                        tmpDir.mkdirs()
                        attachFileName = (File(tmpDir, selectedOrphan[0])).getName()            # noqa
                        tmpFile = File.createTempFile(str(System.currentTimeMillis() % 10000L), attachFileName, tmpDir)
                        tmpFile.deleteOnExit()
                        fout = FileOutputStream(tmpFile)
                        LS.readFile(selectedOrphan[0], fout)                                    # noqa
                        fout.close()
                        Desktop.getDesktop().open(tmpFile)

                    except:
                        myPrint("B","Sorry, could not open attachment file....: %s" %selectedOrphan[0])     # noqa

        else:
            msg.go()        # noqa

        del attachmentList
        del attachmentLocations
        del typesFound
        del attachmentsRawListFound
        del attachmentsNotInLS

        toolbox_frame_.toFront()
        jif.toFront()

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
        return

    def fix_non_hier_sec_acct_txns(statusLabel):
        global toolbox_frame_, debug

        # fix_non-hierarchical_security_account_txns.py
        # (replaces fix_investment_txns_to_wrong_security.py)

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        myPrint("B", "Diagnosing Investment Transactions where Security's Account is not linked properly to the Parent Txn's Acct")
        myPrint("P", "-----------------------------------------------------------------------------------------------------------")

        output = "FIX Investment Transactions where Security's Account is not linked properly to the Parent Txn's Acct:\n" \
                 " =====================================================================================================\n\n"

        txnSet = moneydance_data.getTransactionSet()
        txns = txnSet.iterableTxns()
        fields = InvestFields()

        def review_security_accounts(FIX_MODE=False):

            count_the_errors = 0
            count_unfixable_yet = 0
            errors_fixed = 0
            text = ""
            for txn in txns:
                if txn.getParentTxn() != txn: continue   # only work with parent transactions

                acct = txn.getAccount()
                # noinspection PyUnresolvedReferences
                if acct.getAccountType() != Account.AccountType.INVESTMENT: continue

                # at this point we are only dealing with investment parent txns
                fields.setFieldStatus(txn)

                if fields.hasSecurity and not acct.isAncestorOf(fields.security):
                    count_the_errors += 1
                    text+=("Must fix txn %s\n >%s\n > in %s with sec acct %s\n" %(fields.txnType, txn, acct, fields.security.getFullAccountName()))

                    # This fix assumes that the split / security bit should sit within the txn's parent account. It seeks for the same
                    # security in this account and reattaches it.

                    # Alternatively you could txn.setAccount() to be the split security's parent account
                    # e.g. txn.setAccount(fields.security.getParentAccount())

                    secCurr = fields.security.getCurrencyType()
                    correctSecAcct = None
                    for subacct in AccountUtil.getAccountIterator(acct):
                        if subacct.getCurrencyType() == secCurr:
                            correctSecAcct = subacct
                            break
                    if correctSecAcct:
                        if FIX_MODE:
                            errors_fixed += 1
                            text+=(" -> ASSIGNING txn to %s\n" %(correctSecAcct.getFullAccountName()))
                            fields.security = correctSecAcct
                            fields.storeFields(txn)
                            txn.syncItem()
                        else:
                            text+=(" -> need to assign txn to %s\n" %(correctSecAcct.getFullAccountName()))
                    else:
                        count_unfixable_yet += 1
                        text+=(" !!! You need to manually create a security sub-account by adding the security %s to the investment account %s\n" %(secCurr.getName(), acct.getFullAccountName()))

            return text, count_the_errors, count_unfixable_yet, errors_fixed

        x, iCountErrors, iCountUnfixable, iErrorsFixed = review_security_accounts(False)
        output += x

        output += "\n\nYou have %s errors, with %s needing manual fixes first... I have fixed %s\n\n" %(iCountErrors, iCountUnfixable, iErrorsFixed)

        if iCountErrors<1:
            statusLabel.setText(("FIX: Investment Security Txns with Invalid Parent Accounts - CONGRATULATIONS - I found no Invalid txns.......").ljust(800, " "))
            statusLabel.setForeground(Color.BLUE)
            myPrint("B", "'FIX: Investment Security Txns with Invalid Parent Accounts' - CONGRATULATIONS - I found no Invalid parent accounts.......")
            myPopupInformationBox(toolbox_frame_,"CONGRATULATIONS - I found no Investment Security Txns with Invalid parent accounts...")
            return

        myPrint("B","FIX: Investment Security Txns with Invalid Parent Accounts' - found %s errors... with %s needing manual fixes" %(iCountErrors, iCountUnfixable))

        jif=QuickJFrame("VIEW Investment Security Txns with Invalid Parent Accounts".upper(), output).show_the_frame()

        if iCountUnfixable>0:
            statusLabel.setText(("'FIX: Investment Security Txns with Invalid Parent Accounts' - You have %s errors to manually first first!" %(iCountUnfixable)).ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            myPrint("B", "'FIX: Investment Security Txns with Invalid Parent Accounts' - You have %s errors to manually first first!" %(iCountUnfixable))
            myPopupInformationBox(jif,"You have %s errors to manually first first!" %(iCountUnfixable), "FIX: Investment Security Txns with Invalid Parent Accounts",JOptionPane.ERROR_MESSAGE)
            return

        if not confirm_backup_confirm_disclaimer(jif,statusLabel,"FIX %s SECURITY TXNS INVALID PARENT ACCTS" %(iCountErrors),"FIX %s Security Txns with Invalid Parent Accts?" %(iCountErrors)):
            return

        jif.dispose()
        myPrint("B", "User accepted disclaimer to FIX Investment Security Txns with Invalid Parent Accounts. Proceeding.....")

        output += "\n\nRUNNING FIX ON SECURITY TXNS TO RE-LINK PARENT ACCOUNTS\n" \
                  "------------------------------------------------------------\n\n"

        moneydance_data.setRecalcBalances(False)
        moneydance_ui.setSuspendRefresh(True)

        x, iCountErrors, iCountUnfixable, iErrorsFixed = review_security_accounts(FIX_MODE=True)

        moneydance_ui.getMain().saveCurrentAccount()
        moneydance_data.setRecalcBalances(True)
        moneydance_ui.setSuspendRefresh(False)		# This does this too: book.notifyAccountModified(root)

        output += x
        output += "\n\nYou had %s errors, with %s needing manual fixes first... I HAVE FIXED %s\n\n" %(iCountErrors, iCountUnfixable, iErrorsFixed)
        output += "\n<END>"

        myPrint("B", "FIXED %s Investment Security Txns with Invalid Parent Accounts" %(iErrorsFixed))
        play_the_money_sound()
        statusLabel.setText(("FIXED %s Investment Security Txns with Invalid Parent Accounts" %(iErrorsFixed)).ljust(800, " "))
        statusLabel.setForeground(DARK_GREEN)
        jif=QuickJFrame("VIEW Investment Security Txns with Invalid Parent Accounts".upper(), output).show_the_frame()
        myPopupInformationBox(jif,"FIXED %s Investment Security Txns with Invalid Parent Accounts" %(iErrorsFixed), "FIX    Investment Security Txns with Invalid Parent Accounts", JOptionPane.WARNING_MESSAGE)

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
        return

    def fix_delete_one_sided_txns(statusLabel):
        global toolbox_frame_, debug

        # delete_invalid_txns.py
        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        myPrint("B", "Script running to analyse whether you have any one sided transactions - usually from Quicken Imports....")
        myPrint("P", "--------------------------------------------------------------------------------------------------------")

        book = moneydance.getCurrentAccountBook()
        txnSet = book.getTransactionSet()
        txns = txnSet.iterableTxns()

        output = ""
        toDelete = []

        output +="\nLIST OF ONE SIDED TRANSACTIONS (usually from Quicken Imports)\n"
        output +="-------------------------------------------------------------\n"

        for txn in txns:
            if txn.getOtherTxnCount() == 0:
                output += pad(str(txn.getUUID()),50)+" "
                output += "Date: "+pad(str(txn.getDateInt()),15)+" "
                output += pad(str(txn.getAccount()),25)+" "
                output += pad(str(txn.getAccount().getAccountType()),25)+" "
                output += pad(str(txn.getTransferType()),15)+" "
                output += rpad(str(txn.getValue()),12)+" "
                output += "\n"

                toDelete.append(txn)

        if not len(toDelete)>0:
            myPrint("J","Congratulations - You have no one-sided transactions to delete!!")

            statusLabel.setText(("Congratulations - You have no one-sided transactions to delete!!").ljust(800, " "))
            statusLabel.setForeground(Color.BLUE)

            myPopupInformationBox(toolbox_frame_, "Congratulations - You have no one-sided transactions to delete!!", "DELETE ONE-SIDE TXNS", JOptionPane.INFORMATION_MESSAGE)
            return

        output += "\n<END>"

        jif=QuickJFrame("LIST OF ONE SIDED TRANSACTIONS (usually from Quicken Imports)", output).show_the_frame()

        myPrint("J","You have %s one-sided transactions that can be deleted!!"%len(toDelete))
        myPopupInformationBox(jif, "You have %s one-sided transactions that can de deleted!!"%len(toDelete), "DELETE ONE-SIDE TXNS", JOptionPane.WARNING_MESSAGE)

        if not confirm_backup_confirm_disclaimer(jif, statusLabel, "DELETE ONE-SIDED TRANSACTIONS", "delete %s one-sided transactions?" %(len(toDelete))):
            return

        moneydance_data.setRecalcBalances(False)
        moneydance_ui.setSuspendRefresh(True)

        for t in toDelete:
            myPrint("J", "Item %s deleted" %t.getUUID())
            t.deleteItem()

        moneydance_ui.getMain().saveCurrentAccount()
        moneydance_data.setRecalcBalances(True)
        moneydance_ui.setSuspendRefresh(False)		# This does this too: book.notifyAccountModified(root)

        myPrint("B", "Deleted %s invalid one-sided transactions" % len(toDelete))
        play_the_money_sound()
        statusLabel.setText(("%s One-Sided Transactions DELETED!" %len(toDelete)).ljust(800, " "))
        statusLabel.setForeground(DARK_GREEN)
        myPopupInformationBox(jif,"Congratulations - All One Sided Transactions DELETED!!", "DELETE ONE-SIDE TXNS", JOptionPane.WARNING_MESSAGE)

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
        return

    def convert_stock_avg_cst_control(statusLabel):
        global toolbox_frame_, debug

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        if moneydance_data is None: return

        if not myPopupAskQuestion(toolbox_frame_,"CONVERT ACCT/STOCK TO Avg Cst Ctrl","Do you want to convert a stock to Average Cost Control and reset/wipe any LOT data?",theMessageType=JOptionPane.WARNING_MESSAGE):
            myPopupInformationBox(toolbox_frame_,"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        accountsList = AccountUtil.allMatchesForSearch(moneydance_data, MyAcctFilter(14))
        accountsList = sorted(accountsList, key=lambda sort_x: (sort_x.getFullAccountName().upper()))

        accountSec = JOptionPane.showInputDialog(toolbox_frame_,
                                                 "Select a LOT Controlled Acct/Stock to convert to Avg Cost Control",
                                                 "CONVERT ACCT/STOCK TO Avg Cst Ctrl",
                                                 JOptionPane.INFORMATION_MESSAGE,
                                                 moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                 accountsList,
                                                 None)

        if not accountSec:
            statusLabel.setText(("CONVERT ACCT/STOCK TO Avg Cst Ctrl - No Account/Security was selected - no changes made..").ljust(800, " "))
            statusLabel.setForeground(Color.BLUE)
            myPopupInformationBox(toolbox_frame_,"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        class SecurityObj:
            def __init__(self,Obj,Book):                                                                        # noqa
                self.Obj = Obj
                self.Acct = Obj.getParentAccount()
                self.TxnSet = Book.getTransactionSet().getTransactionsForAccount(Obj)
                self.Name = Obj.getAccountName()
                self.Num = Obj.getAccountNum()
                self.Type = "SECURITY"
                self.AvgCost = Obj.getUsesAverageCost()
                self.Txns = []
                for _Txn in self.TxnSet: self.Txns.append(TxnObj(_Txn))

        class TxnObj:
            def __init__(self,Txn):                                                                             # noqa
                self.Obj = Txn
                self.Parent = Txn.getParentTxn()
                self.ID = Txn.getUUID()
                self.DateInt = Txn.getDateInt()
                self.Type = self.Parent.getInvestTxnType().getIDString()
                self.saveCostBasisState = self.Obj.getParameter("cost_basis",None)

        Book = moneydance.getCurrentAccountBook()

        # We are forcing just the one selected Security into the List (the original script allowed user to hard code several)
        Securities = [SecurityObj(accountSec,Book)]

        iErrors=0
        for Security in Securities:
            for Txn in Security.Txns:
                if (InvestUtil.isSaleTransaction(Txn.Parent.getInvestTxnType())
                        and (Txn.Obj.getParameter("cost_basis", None) is not None)):
                    iErrors+=1

        if not confirm_backup_confirm_disclaimer(toolbox_frame_,statusLabel,"CONVERT ACCT/STOCK TO Avg Cst Ctrl","Convert %s to Avg Cst Control and wipe %s LOT records?" %(accountSec,iErrors)):
            return

        listWiped=""
        for Security in Securities:
            myPrint("B","@@ User requested to convert Acct/Security %s to Average Lot Control and wipe %s LOT records... EXECUTING NOW" %(Security.Obj, iErrors))
            for Txn in Security.Txns:
                if (InvestUtil.isSaleTransaction(Txn.Parent.getInvestTxnType())
                        and (Txn.Obj.getParameter("cost_basis", None) is not None)):
                    listWiped+=" %s Wiped LOT tag on record (was: %s)\n" %(Security.Obj, Txn.Obj.getParameter("cost_basis", None))
                    myPrint("B","@@ Security %s Wiping LOT record on %s" %(Security.Obj, Txn.Obj))
                    Txn.Obj.setParameter("cost_basis", None)
                    Txn.Obj.syncItem()

            Security.Obj.setUsesAverageCost(True)
            Security.AvgCost = True
            Security.Obj.syncItem()


        myPrint("B", "CONVERT ACCT/STOCK TO Avg Cst Ctrl - Security %s Changed to Average Cost Control (and %s LOT records wiped)"%(accountSec,iErrors))

        statusLabel.setText(("CONVERT ACCT/STOCK TO Avg Cst Ctrl - Security %s Changed to Average Cost Control (and %s LOT records wiped)"%(accountSec,iErrors)).ljust(800, " "))
        statusLabel.setForeground(Color.RED)
        play_the_money_sound()
        MyPopUpDialogBox(toolbox_frame_,
                         theStatus="Security %s converted to Average Cost Control (I wiped %s LOT records - shown below)" %(accountSec,iErrors),
                         theMessage="%s" %(listWiped),
                         theWidth=200,
                         theTitle="CONVERT ACCT/STOCK TO Avg Cst Ctrl",
                         lAlertLevel=1).go()

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
        return

    def convert_stock_lot_FIFO(statusLabel):
        global toolbox_frame_, debug

        # MakeFifoCost.py (author unknown)

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        if moneydance_data is None: return

        if not myPopupAskQuestion(toolbox_frame_,"CONVERT ACCT/STOCK TO LOT/FIFO","Do you want to attempt to convert a stock to LOT Controlled and match Sells to Buys using FiFo?",theMessageType=JOptionPane.WARNING_MESSAGE):
            myPopupInformationBox(toolbox_frame_,"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        accountsList = AccountUtil.allMatchesForSearch(moneydance_data, MyAcctFilter(13))
        accountsList = sorted(accountsList, key=lambda sort_x: (sort_x.getFullAccountName().upper()))

        accountSec = JOptionPane.showInputDialog(toolbox_frame_,
                                                 "Select an Avg Cost Controlled Acct/Stock to convert to LOT/FiFo",
                                                 "CONVERT STOCK FIFO",
                                                 JOptionPane.INFORMATION_MESSAGE,
                                                 moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                 accountsList,
                                                 None)

        if not accountSec:
            statusLabel.setText(("CONVERT STOCK FIFO - No Account/Security was selected - no changes made..").ljust(800, " "))
            statusLabel.setForeground(Color.BLUE)
            myPopupInformationBox(toolbox_frame_,"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        # noinspection PyUnresolvedReferences
        if len(accountSec.getCurrencyType().getSplits()) >0:

            # noinspection PyUnresolvedReferences
            statusLabel.setText(("CONVERT STOCK FIFO - SORRY - You have %s split(s) on this security %s. I have not been programmed to deal with these - contact the author...." %(len(accountSec.getCurrencyType().getSplits()),accountSec)).ljust(800, " "))
            statusLabel.setForeground(Color.RED)

            # noinspection PyUnresolvedReferences
            myPopupInformationBox(toolbox_frame_,
                                  "SORRY - You have %s split(s) on this security %s. I have not been programmed to deal with these - contact the author...." %(len(accountSec.getCurrencyType().getSplits()),accountSec),
                                  "CONVERT STOCK FIFO",
                                  JOptionPane.ERROR_MESSAGE)
            return


        MyPopUpDialogBox(toolbox_frame_,
                         theStatus="Information before you proceed: %s" %(accountSec),
                         theMessage="This function updates the Acct/Security records as it progresses to generate the report\n"
                                    "There is no pre-report for you to validate/confirm\n"
                                    "1. It will ask you to confirm I can wipe any existing LOT tags incorrectly set first (I will save these)\n"
                                    "2. The report will run, Convert to LOT Control, update the LOT records, and show you the results\n"
                                    "3. If you are not happy, I can reset the Security back to Avg Cost Control (removing/resetting LOT tags)\n"
                                    "4. I will restore wiped (incorrect) LOT tags back to the saved data from step 1.\n"
                                    "** You will be asked to confirm and perform a backup then proceed in the next step....",
                         theWidth=200,
                         theTitle="CONVERT STOCK FIFO",
                         OKButtonText="I HAVE READ THIS",
                         lAlertLevel=1).go()

        if not confirm_backup_confirm_disclaimer(toolbox_frame_,statusLabel,"CONVERT STOCK FIFO","Convert %s to LOT control and assign FiFio?" %(accountSec)):
            return

        class SecurityObj:
            def __init__(self,Obj,Book):                                                                        # noqa
                self.Obj = Obj
                self.Acct = Obj.getParentAccount()
                self.TxnSet = Book.getTransactionSet().getTransactionsForAccount(Obj)
                self.Name = Obj.getAccountName()
                self.Num = Obj.getAccountNum()
                self.Type = "SECURITY"
                self.Balance = Obj.getBalance()
                self.CurTyp = Obj.getCurrencyType()
                self.AvgCost = Obj.getUsesAverageCost()
                self.Txns = []
                for _Txn in self.TxnSet:
                    self.Txns.append(TxnObj(_Txn))
                self.Txns.sort(key=lambda l: l.Date)

        class TxnObj:
            def __init__(self,Txn):                                                                             # noqa
                self.Obj = Txn
                self.Parent = Txn.getParentTxn()
                self.ID = Txn.getUUID()
                self.DateInt = Txn.getDateInt()
                self.Type = self.Parent.getInvestTxnType().getIDString()
                # noinspection PyUnresolvedReferences
                self.Date = datetime.datetime.fromtimestamp(DateUtil.convertIntDateToLong(Txn.getDateInt()).time/1e3)
                self.LngShrs = Txn.getValue()
                securityAcct = Txn.getAccount()
                securityCurr = securityAcct.getCurrencyType()
                self.Shares = securityCurr.getDoubleValue(Txn.getValue())
                self.saveCostBasisState = self.Obj.getParameter("cost_basis",None)

        def MakeCostsFifo(Security,Book, INCLUDE_THE_ZEROS):            # noqa
            WrngCnt = 0                                                 # noqa

            textLog = ""

            if not Security.AvgCost:
                statusLabel.setText(("CONVERT STOCK FIFO - ERROR - Security is already using LOT control - LOGIC ERROR - ABORTING!").ljust(800, " "))
                statusLabel.setForeground(Color.RED)
                return
            else:
                textLog+=("Setting the Security '{}:{}' to FIFO lot matching.\n\n".format(Security.Acct.getAccountName(),Security.Name))

                # If you don't do this here, then InvestUtil.getRemainingLots() returns None
                Security.Obj.setUsesAverageCost(False)
                Security.AvgCost = False
                Security.Obj.syncItem()

                for Txn in Security.Txns:                                                                       # noqa
                    if (InvestUtil.isSaleTransaction(Txn.Parent.getInvestTxnType())
                            and (Txn.LngShrs != 0 or INCLUDE_THE_ZEROS)):
                        RLots = InvestUtil.getRemainingLots(Book,Security.Obj,Txn.Obj.getDateInt())
                        ShrsLeft = -(Txn.LngShrs)
                        Buys = ""
                        prettyBuys = ""
                        for Txn2 in Security.Txns:
                            if Txn2.LngShrs > 0 and Txn2.ID in RLots:
                                RInfo = RLots.get(Txn2.ID)
                                # noinspection PyUnresolvedReferences
                                RShrs = RInfo.getAvailableShares()
                                if RShrs >= ShrsLeft:
                                    Buys += "{}:{};".format(Txn2.ID,ShrsLeft)
                                    prettyBuys += "BUY-{}:{};".format(Txn2.DateInt,Txn.Obj.getAccount().getCurrencyType().getDoubleValue(ShrsLeft))
                                    ShrsLeft = 0
                                    break
                                elif RShrs > 0:
                                    Buys += "{}:{};".format(Txn2.ID,RShrs)
                                    prettyBuys += "BUY-{}:{};".format(Txn2.DateInt,Txn.Obj.getAccount().getCurrencyType().getDoubleValue(RShrs))
                                    ShrsLeft -= RShrs
                        if ShrsLeft > 0:
                            textLog+=("@@ WARNING! Came up short %s shares for ID='%s' on date=%s!\n" %(rpad(Txn.Obj.getAccount().getCurrencyType().getDoubleValue(ShrsLeft),12),Txn.ID,Txn.Date.strftime("%Y/%m/%d")))
                            WrngCnt += 1
                        if len(Buys) > 0:
                            Txn.Obj.setParameter("cost_basis",Buys)
                            Txn.Obj.syncItem()
                            Txn.Obj.getParentTxn().syncItem()
                            textLog+=("cost_basis for the sale dated: %s of %s shares on %s set to '%s'\n" %(Txn.DateInt,rpad(Txn.Shares,12),Txn.Date.strftime("%Y/%m/%d"),prettyBuys))
                    else:
                        if (InvestUtil.isSaleTransaction(Txn.Parent.getInvestTxnType())):
                            textLog+=("skipped ZERO sale dated: %s of %s shares...'\n" %(Txn.DateInt,rpad(Txn.Shares,12)))

            return WrngCnt, textLog

        output = "CONVERT STOCK FIFO (Convert Accounts/Security using Avg Cost Control to LOT control & assign FiFo)\n" \
                 " =================================================================================================\n\n"

        WrngCnt = 0
        Book = moneydance.getCurrentAccountBook()

        # We are forcing just the one selected Security into the List (the original script allowed user to hard code several)
        Securities = [SecurityObj(accountSec,Book)]

        iErrors=0
        for Security in Securities:
            for Txn in Security.Txns:
                if (InvestUtil.isSaleTransaction(Txn.Parent.getInvestTxnType())
                        and (Txn.Obj.getParameter("cost_basis", None) is not None)):
                    iErrors+=1
        if iErrors>0:
            if not myPopupAskQuestion(toolbox_frame_,"CONVERT STOCK FIFO",
                                      "WARNING: I found %s LOTS already set on account/security. Do you want to proceed (and overwrite) these?" %(iErrors),
                                      theMessageType=JOptionPane.ERROR_MESSAGE):
                myPrint("B", "CONVERT STOCK FIFO - ABORTED - as Acct/Security %s already had %s LOT records!!??"%(accountSec, iErrors))
                statusLabel.setText(("CONVERT STOCK FIFO - ABORTED - as Acct/Security %s already had %s LOT records!!??"%(accountSec, iErrors)).ljust(800, " "))
                statusLabel.setForeground(Color.RED)
                myPopupInformationBox(toolbox_frame_,"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
                return

            myPrint("B", "CONVERT STOCK FIFO - RESETTING %s LOT TAGS on Acct/Security %s!!"%(iErrors, accountSec))
            output+=("\nRESETTING %s LOT TAGS on Acct/Security %s!!\n"%(iErrors, accountSec))

            for Security in Securities:
                for Txn in Security.Txns:
                    if (InvestUtil.isSaleTransaction(Txn.Parent.getInvestTxnType())
                            and (Txn.Obj.getParameter("cost_basis", None) is not None)):
                        output+=" > Found LOT tag on Sale record, when it should be None... Resetting to None (was SELL %s Shrs Dated:%s: %s)\n" %(rpad(Txn.Shares,12),Txn.DateInt,Txn.Obj.getParameter("cost_basis", None))
                        Txn.Obj.setParameter("cost_basis", None)
                        Txn.Obj.syncItem()

        iSellZeros=0
        for Security in Securities:
            for Txn in Security.Txns:
                if (InvestUtil.isSaleTransaction(Txn.Parent.getInvestTxnType()) and Txn.LngShrs == 0):
                    iSellZeros+=1

        lIncludeSellZeros=False
        if iSellZeros>0:
            if myPopupAskQuestion(toolbox_frame_,"CONVERT STOCK FIFO",
                                  "WARNING: I found %s Sale Txns for ZERO shares. YES = INCLUDE and match these to Zero Buys; NO = SKIP/IGNORE them?" %(iSellZeros),
                                  theMessageType=JOptionPane.WARNING_MESSAGE):
                myPrint("B", "CONVERT STOCK FIFO: Acct/Security %s - Will match %s ZERO sales too..."%(accountSec, iSellZeros))
                lIncludeSellZeros = True

        for Security in Securities:
            count, text = MakeCostsFifo(Security,Book, lIncludeSellZeros)
            WrngCnt += count
            output += text

        if iSellZeros>0:
            if lIncludeSellZeros:
                output+="\n\n @@ ALERT - I have matched Sales for ZERO shares to BUYS... @@\n\n"
            else:
                output+="\n\n @@ ALERT - The MD LOT Window will pop up wanting you to match the Zero Sells, which you can't.. You can just press Cancel on this (or re-run and Include them) @@\n\n"

        output+=("\nFinished. Processed {} securities producing {} warnings.\n".format(len(Securities),WrngCnt))

        jif=QuickJFrame("CONVERT STOCK FIFO - REVIEW RESULTS", output).show_the_frame()

        ask=MyPopUpDialogBox(jif,
                             theStatus="Please review results on security: %s" %(accountSec),
                             theMessage="These changes have already been made to your dataset\n"
                                        "To reset the security back to Avg Cost Control and reset/remove these altered LOT records select CANCEL\n"
                                        "(NOTE: I will put the LOT records back to the same state before this script ran)"
                                        "[OK KEEP RESULTS] will accept these changes",
                             theWidth=200,
                             theTitle="CONVERT STOCK FIFO",
                             OKButtonText="OK KEEP RESULTS",
                             lCancelButton=True,
                             lAlertLevel=1)
        if not ask.go():
            jif.dispose()
            myPrint("B", "\nREVERTING CHANGES - RESETTING ACCOUNT/SECURITY %s BACK TO AVERAGE COST CONTROL!!\n"%(accountSec))
            myPrint("B", "CONVERT STOCK FIFO - RESETTING LOT TAGS on Acct/Security %s!!"%(accountSec))

            output+=("\nREVERTING CHANGES - RESETTING ACCOUNT/SECURITY %s BACK TO AVERAGE COST CONTROL!!\n"%(accountSec))
            output+=("\nRESETTING LOT TAGS on Acct/Security %s!!\n"%(accountSec))

            for Security in Securities:

                myPrint("B","CONVERT STOCK FIFO - Reverting Security %s back to Average Cost Control" %(accountSec))
                output+=("@@ CONVERT STOCK FIFO - Reverting Security %s back to Average Cost Control@@\n" %(accountSec))

                for Txn in Security.Txns:
                    if InvestUtil.isSaleTransaction(Txn.Parent.getInvestTxnType()):
                        if Txn.Obj.getParameter("cost_basis", None) != Txn.saveCostBasisState:
                            output+="  >> Reverting LOT record to: %s\n" %(Txn.saveCostBasisState)
                            Txn.Obj.setParameter("cost_basis", Txn.saveCostBasisState)
                            Txn.Obj.syncItem()
                output+=" > Reverting to Average Cost Control...\n"
                Security.Obj.setUsesAverageCost(True)
                Security.AvgCost = True
                Security.Obj.syncItem()
                output+="\n<END>"
                statusLabel.setText(("CONVERT STOCK FIFO - Changes to Security %s REJECTED and REVERSED - review report"%(accountSec)).ljust(800, " "))
                statusLabel.setForeground(Color.RED)
        else:
            jif.dispose()
            output+="\nCHANGES ACCEPTED and RETAINED...\n" \
                    "\n<END>"
            statusLabel.setText(("CONVERT STOCK FIFO - Changes to Security %s Accepted and retained - review report"%(accountSec)).ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            myPrint("B", "CONVERT STOCK FIFO - Changes to Security %s Accepted and retained - review report"%(accountSec))


        jif=QuickJFrame("CONVERT STOCK FIFO - REVIEW RESULTS", output).show_the_frame()
        play_the_money_sound()
        myPopupInformationBox(jif, "REVIEW REPORT", "CONVERT STOCK FIFO", JOptionPane.WARNING_MESSAGE)


        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
        return

    def show_open_share_lots(statusLabel):
        global toolbox_frame_, debug, DARK_GREEN, lCopyAllToClipBoard_TB
        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        if moneydance_data is None: return

        class LotInfo:
            def __init__(self, _date, _buyPrice, _availableShares, _costBasis, _currentPrice, _currentValue):
                self.date = _date
                self.buyPrice = _buyPrice
                self.availableShares = _availableShares
                self.costBasis = _costBasis
                self.currentPrice = _currentPrice
                self.currentValue = _currentValue

        book = moneydance.getCurrentAccountBook()
        date = datetime.datetime.today()

        # diag = MyPopUpDialogBox(toolbox_frame_,"Please wait: Scanning investments....",theTitle="SEARCH", theWidth=100, lModal=False,OKButtonText="WAIT")
        # diag.go()
        #
        output="\n\nANALYSING SHARES/SECURITIES WITH OPEN (Unconsumed LOTS)\n" \
               " ======================================================\n\n"

        output+='Outstanding Tax Lots as of %s\n\n'%(date.strftime("%m/%d/%y"))
        output+=("%s %s %s %s %s %s\n"
                 %(pad("Buy Date",10),
                   rpad("Buy Price",12),
                   rpad("Avail. Shares",12),
                   rpad("Cost Basis",12),
                   rpad("Current Price",12),
                   rpad("Current Value",14)))

        iFound=0
        for acct in AccountUtil.getAccountIterator(book):
            if acct.getAccountType() ==  acct.AccountType.SECURITY:
                if  not acct.getUsesAverageCost():
                    if InvestUtil.getCostBasis(acct)  > 0:
                        output+="\n%s\n\n" %(acct.getFullAccountName())
                        totalCostBasis = float(0)
                        totalAvailableShares = float(0)
                        currentPrice = float(1)/float(acct.getCurrencyType().getRelativeRate())
                        lotList = []
                        lots = InvestUtil.getRemainingLots(book, acct, DateUtil.getStrippedDateInt())

                        # noinspection PyUnresolvedReferences
                        for transaction, availSharesTracker in lots.items():
                            availableShares = float(availSharesTracker.getAvailableShares())/10000
                            if availableShares > 0:
                                t = book.getTransactionSet().getTxnByID(transaction)
                                # noinspection PyUnresolvedReferences
                                date = datetime.datetime.fromtimestamp(DateUtil.convertIntDateToLong(t.getDateInt()).time/1e3)
                                adjustedBuyPrice = float(1)/acct.getCurrencyType().adjustRateForSplitsInt(t.getDateInt(), t.getRate())*100
                                costBasis = availableShares*adjustedBuyPrice
                                currentValue = currentPrice*availableShares
                                totalCostBasis += costBasis
                                totalAvailableShares += availableShares
                                lotList.append(LotInfo(date, adjustedBuyPrice, availableShares, costBasis, currentPrice, currentValue))
                        lotList.sort(key=lambda sort_l: sort_l.date)
                        lotCount = 0
                        for _lot in lotList:
                            lotCount += 1
                            output+=("%s %s %s %s %s %s\n"
                                     %(pad(_lot.date.strftime("%m/%d/%y"),10),
                                       rpad(_lot.buyPrice,12),
                                       rpad(_lot.availableShares,12),
                                       rpad(_lot.costBasis,12),
                                       rpad(_lot.currentPrice,12),
                                       rpad(_lot.currentValue,14)))
                            iFound+=1
                        if lotCount > 1:
                            output+=("%s %s %s %s %s %s\n"
                                     %(pad("",10),
                                       rpad("",12),
                                       rpad("----------",12),
                                       rpad("----------",12),
                                       rpad("",12),
                                       rpad("----------",14)))
                            output+=("%s %s %s %s %s %s\n"
                                     %(pad("",10),
                                       rpad("",12),
                                       rpad(totalAvailableShares,12),
                                       rpad(totalCostBasis,12),
                                       rpad("",12),
                                       rpad(totalAvailableShares*currentPrice,14)))
                        output+="\n"
        output+="\n<END>"

        # diag.kill()
        #
        if iFound<1:
            statusLabel.setText(("VIEW OPEN LOTS - You have no open / unconsumed LOTs to display!").ljust(800, " "))
            statusLabel.setForeground(Color.BLUE)
            myPopupInformationBox(toolbox_frame_,"You have no open / unconsumed LOTs to display!","VIEW OPEN LOTS")
        else:
            toolbox_frame_.toFront()
            statusLabel.setText(("VIEW OPEN LOTS - Displaying %s open LOTS!" %(iFound)).ljust(800, " "))
            statusLabel.setForeground(Color.BLUE)
            jif = QuickJFrame("VIEW OPEN LOTS", output).show_the_frame()
            myPopupInformationBox(jif,"Showing %s Open LOTS" %(iFound))

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
        return

    class OpenFolderButtonAction(AbstractAction):

        def __init__(self, statusLabel):
            self.statusLabel = statusLabel

        def actionPerformed(self, event):
            global toolbox_frame_, debug

            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

            helper = moneydance.getPlatformHelper()

            grabProgramDir = find_the_program_install_dir()
            if not os.path.exists((grabProgramDir)): grabProgramDir = None

            locations = [
                "Show Preferences (config.dict) Folder",
                "Show custom themes Folder",
                "Show Console (error) log Folder",
                "Show Contents of your current Dataset Folder",
                "Show Extensions Folder",
                "Show Auto Backup Folder",
                "Show Last used (Manual) Backup Folder"]
            if grabProgramDir:
                locations.append("Open Program's Install Directory")

            # noinspection PyUnresolvedReferences
            locationsDirs = [
                Common.getPreferencesFile(),
                theme.Theme.customThemeFile,
                moneydance.getLogFile(),
                moneydance_data.getRootFolder(),
                Common.getFeatureModulesDirectory(),
                FileUtils.getBackupDir(moneydance.getPreferences()),
                File(moneydance_ui.getPreferences().getSetting("backup.last_saved", ""))]

            if grabProgramDir:
                locationsDirs.append(File(grabProgramDir))

            selectedFolder = JOptionPane.showInputDialog(toolbox_frame_,
                                                         "Select the Folder you would like to open",
                                                         "Select Folder",
                                                         JOptionPane.INFORMATION_MESSAGE,
                                                         moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                         locations,
                                                         None)
            if not selectedFolder:
                self.statusLabel.setText(("No folder was selected to open..").ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            if not os.path.exists(str(locationsDirs[locations.index(selectedFolder)])):
                self.statusLabel.setText(("Sorry - File/Folder does not exist!").ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                return

            helper.openDirectory(locationsDirs[locations.index(selectedFolder)])
            self.statusLabel.setText(("Folder " + selectedFolder + " opened..: " + str(locationsDirs[locations.index(selectedFolder)])).ljust(800, " "))
            self.statusLabel.setForeground(Color.BLUE)

            myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
            return

    def display_passwords(statusLabel):
        global toolbox_frame_, debug

        myPrint(u"D", u"In ", inspect.currentframe().f_code.co_name, u"()")

        MD_enc = moneydance_ui.getCurrentAccounts().getEncryptionKey()
        MD_hnt = moneydance_ui.getCurrentAccounts().getEncryptionHint()
        MD_sync_pwd = moneydance_ui.getCurrentAccounts().getSyncEncryptionPassword()

        msg = u"'Master' Encryption Passphrase ('password'): "
        displayMsg = u"'Master' Encryption Passphrase ('password'): "

        if MD_enc is not None and MD_enc != u"":
            msg += u"%s" %(MD_enc)
            displayMsg += u"%s" %(MD_enc)
            if MD_hnt is not None and MD_hnt != u"":
                msg += u"  >> Encryption Passphrase Hint: %s" %(MD_hnt)
                displayMsg += u"  >> Encryption Passphrase Hint: %s" %(MD_hnt)
            else:
                msg += u"  >> Encryption Passphrase Hint: (NOT SET)"
                displayMsg += u"  >> Encryption Passphrase Hint: (NOT SET)"

            msg += u"\n"
            displayMsg += u"  -  "
        else:
            msg += u"(NOT SET - this means a default 'internal' encryption passphrase is being used)\n"
            displayMsg += u"(NOT SET - this means a default 'internal' encryption passphrase is being used)  -  "

        msg += u"Sync Passphrase: "
        displayMsg += u"Sync Passphrase: "

        if MD_sync_pwd is not None and MD_sync_pwd != u"":
            msg += u"%s" %(MD_sync_pwd)
            displayMsg += u"%s" %(MD_sync_pwd)
        else:
            msg += u"(NOT SET)"
            displayMsg += u"(NOT SET)"

        myPrint(u"B",u"Displaying Moneydance Encryption & Sync Passphrase(s) ....!")

        statusLabel.setText((u"Moneydance Encryption Passphrases: %s" %(displayMsg)).ljust(800, " "))
        statusLabel.setForeground(Color.BLUE)

        MyPopUpDialogBox(toolbox_frame_,u"Moneydance Encryption Passphrases:",msg,theTitle=u"PASSWORDS",lAlertLevel=1).go()

        myPrint(u"D", u"Exiting ", inspect.currentframe().f_code.co_name, u"()")
        return msg, displayMsg


    def change_fonts(statusLabel):
        global toolbox_frame_, debug
        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        if float(moneydance.getBuild()) < 3030:
            myPrint("B", "Error - must be on Moneydance build 3030+ to change fonts!")
            statusLabel.setText(("Error - must be on Moneydance build 3030+ to change fonts!").ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            myPopupInformationBox(toolbox_frame_,"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        myPrint("DB", "User requested to change Moneydance Default Fonts!")

        if not backup_config_dict():
            statusLabel.setText("Error backing up config.dict preferences file before deletion - no changes made....".ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            myPopupInformationBox(toolbox_frame_,"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        prefs=moneydance_ui.getPreferences()

        systemFonts = GraphicsEnvironment.getLocalGraphicsEnvironment().getAvailableFontFamilyNames()
        for installedFont in systemFonts:
            myPrint("D","System OS Font %s is installed in your system..:" %installedFont)

        # These are taken from MD Code - build 3034 - watch out they may change...!
        Mac_fonts_main =     ["SF Pro Display", "SF Display", "Helvetica Neue", "Helvetica", "Lucida Grande", "Dialog"]
        Mac_fonts_mono =     ["Gill Sans", "Menlo", "Monaco", "Monospaced"]

        Windows_fonts_main = ["Dialog"]
        Windows_fonts_mono = ["Calibri","Monospaced"]

        Linux_fonts_main =   ["Dialog"]
        Linux_fonts_mono =   ["Monospaced"]

        all_fonts_code =   ["Hack", "Monospaced"]
        all_fonts_print =   ["Helvetica", "Dialog"]

        lExit=False
        lAnyFontChanges=False

        for checkFont in ["main_font","mono_font","code_font","print.font_name"]:
            x = prefs.getSetting(checkFont, None)
            if x is not None and x == "null":
                lAnyFontChanges=True
                prefs.setSetting(checkFont,None)
                myPrint("B","@@ Font setting %s in config.dict was set to 'null'. I have corrected this and deleted the setting.." %checkFont)

        if lAnyFontChanges:
            moneydance.savePreferences()

        while True:
            if lExit: break

            mainF = prefs.getSetting("main_font", None)
            monoF = prefs.getSetting("mono_font", None)
            codeF = prefs.getSetting("code_font", None)
            printF = prefs.getSetting("print.font_name", None)

            myPrint("DB",'@@ MONEYDANCE: Config.dict: "main_font" currently set to %s' %mainF)
            myPrint("DB",'@@ MONEYDANCE: Config.dict: "mono_font" currently set to %s' %monoF)
            myPrint("DB",'@@ MONEYDANCE: Config.dict: "code_font" currently set to %s' %codeF)
            myPrint("DB",'@@ MONEYDANCE: Config.dict: "print.font_name" currently set to %s' %printF)

            display_main="None(Moneydance defaults)"
            display_mono="None(Moneydance defaults)"
            display_code="None(Moneydance defaults)"
            display_print="None(Moneydance defaults)"
            if mainF and mainF != "null": display_main = mainF
            if monoF and monoF != "null": display_mono = monoF
            if codeF and codeF != "null": display_code = codeF
            if printF and printF != "null": display_print = printF

            MyPopUpDialogBox(toolbox_frame_,"Config.dict - CURRENT FONTS:",
                             '"main_font" currently set to %s\n'
                             '"mono_font" currently set to %s  (Used for mainly numbers)\n'
                             '"code_font" currently set to %s  (the Moneybot / Python Font >> IMPACTS OUTPUT COLUMN ALIGNMENT <<)\n'
                             '"print.font_name" currently set to %s' %(display_main,display_mono,display_code,display_print),
                             150,"FONTS",OKButtonText="CONTINUE").go()

            _options=["MAIN: CHANGE SETTING",
                      "MAIN: DELETE SETTING",
                      "MONO: CHANGE SETTING",
                      "MONO: DELETE SETTING",
                      "CODE: CHANGE SETTING",
                      "CODE: DELETE SETTING",
                      "PRINT: CHANGE SETTING",
                      "PRINT: DELETE SETTING"]

            selectedOption = JOptionPane.showInputDialog(toolbox_frame_,
                                                         "What type of change do you want to make?",
                                                         "ALTER FONTS",
                                                         JOptionPane.WARNING_MESSAGE,
                                                         None,
                                                         _options,
                                                         None)

            if not selectedOption:
                break

            lMain = (_options.index(selectedOption) == 0 or _options.index(selectedOption) == 1)
            lMono = (_options.index(selectedOption) == 2 or _options.index(selectedOption) == 3)
            lCode = (_options.index(selectedOption) == 4 or _options.index(selectedOption) == 5)
            lPrint = (_options.index(selectedOption) == 6 or _options.index(selectedOption) == 7)

            lDelete = (_options.index(selectedOption) == 1 or _options.index(selectedOption) == 3 or _options.index(selectedOption) == 5 or _options.index(selectedOption) == 7)
            lChange = (_options.index(selectedOption) == 0 or _options.index(selectedOption) == 2 or _options.index(selectedOption) == 4 or _options.index(selectedOption) == 6)

            if lMain:
                theKey = "main_font"
            elif lMono:
                theKey = "mono_font"
            elif lCode:
                theKey = "code_font"
            elif lPrint:
                theKey = "print.font_name"
            else:
                raise(Exception("error"))

            if lDelete:
                if myPopupAskQuestion(toolbox_frame_,"DELETE FONT KEY","Are you sure you want to delete key: %s?" %theKey,JOptionPane.YES_NO_OPTION,JOptionPane.WARNING_MESSAGE):
                    prefs.setSetting(theKey,None)
                    moneydance.savePreferences()
                    lAnyFontChanges=True
                    myPrint("B", "Config.dict: key: %s DELETED - RESTART MD" %theKey)
                    myPopupInformationBox(toolbox_frame_, "Config.dict: key: %s DELETED - RESTART MD" %theKey, "FONTS", JOptionPane.WARNING_MESSAGE)
                    continue
                else:
                    continue

            elif lChange:

                theFonts = None                                                                                 # noqa
                if Platform.isOSX():
                    if lMain:
                        theFonts = Mac_fonts_main
                    elif lMono:
                        theFonts = Mac_fonts_mono
                    elif lCode:
                        theFonts = all_fonts_code
                    elif lPrint:
                        theFonts = all_fonts_print
                    else: raise(Exception("error"))
                elif Platform.isWindows():
                    if lMain:
                        theFonts = Windows_fonts_main
                    elif lMono:
                        theFonts = Windows_fonts_mono
                    elif lCode:
                        theFonts = all_fonts_code
                    elif lPrint:
                        theFonts = all_fonts_print
                    else: raise(Exception("error"))
                else:
                    if lMain:
                        theFonts = Linux_fonts_main
                    elif lMono:
                        theFonts = Linux_fonts_mono
                    elif lCode:
                        theFonts = all_fonts_code
                    elif lPrint:
                        theFonts = all_fonts_print
                    else: raise(Exception("error"))

                for x in theFonts:
                    myPrint("D","Possible internal default fonts for your Platform...: %s" %x)

                _options=["CHOOSE FROM MD INTERNAL LIST", "CHOOSE FROM YOUR OS' SYSTEM INSTALLED"]
                selectedOption = JOptionPane.showInputDialog(toolbox_frame_,
                                                             "New Font Selection options for: %s?" %theKey,
                                                             "ALTER FONTS",
                                                             JOptionPane.WARNING_MESSAGE,
                                                             None,
                                                             _options,
                                                             None)

                if not selectedOption:
                    continue

                if _options.index(selectedOption) == 0 or _options.index(selectedOption) == 1:

                    if _options.index(selectedOption) == 1: theFonts = systemFonts
                    selectedFont = JOptionPane.showInputDialog(toolbox_frame_,
                                                               "Select new Font to set for %s" %theKey,
                                                               "ALTER FONTS",
                                                               JOptionPane.WARNING_MESSAGE,
                                                               None,
                                                               theFonts,
                                                               None)
                    if not selectedFont:
                        continue
                    else:
                        prefs.setSetting(theKey,selectedFont)
                        moneydance.savePreferences()
                        lAnyFontChanges=True
                        myPrint("B", 'Config.dict: key: %s CHANGED to "%s" - RESTART MD' %(theKey,selectedFont))
                        myPopupInformationBox(toolbox_frame_, 'Config.dict: key: %s CHANGED to "%s"\nRESTART MD' %(theKey,selectedFont), "FONTS", JOptionPane.WARNING_MESSAGE)
                        continue

                else:
                    raise(Exception("error"))

            continue

        if lAnyFontChanges:
            statusLabel.setText("Moneydance Font Changes made as requested - PLEASE RESTART MONEYDANCE (PS - config.dict was backed up too)....".ljust(800, " "))
            statusLabel.setForeground(Color.RED)
        else:
            myPrint("D", "NO FONT ACTIONS TAKEN")
            statusLabel.setText("NO FONT ACTIONS TAKEN! - no changes made....".ljust(800, " "))
            statusLabel.setForeground(Color.BLUE)
            myPopupInformationBox(toolbox_frame_, "NO FONT ACTIONS / CHANGES TAKEN !", "FONTS", JOptionPane.WARNING_MESSAGE)

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
        return

    def delete_theme_file(statusLabel):
        global toolbox_frame_, debug
        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )

        myPrint("DB", "User requested to delete custom theme file!")

        # noinspection PyUnresolvedReferences
        customThemeFile = str(theme.Theme.customThemeFile)
        if not os.path.exists(customThemeFile):
            statusLabel.setText("Custom Theme file does not exist to delete!".ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            myPopupInformationBox(toolbox_frame_,"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        if not myPopupAskQuestion(toolbox_frame_,
                                  "DELETE MD custom Theme file?",
                                  "Are you sure you want to delete custom Theme file?",
                                  JOptionPane.YES_NO_OPTION,
                                  JOptionPane.ERROR_MESSAGE):

            statusLabel.setText("User declined to delete custom Theme file!".ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            myPopupInformationBox(toolbox_frame_,"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        disclaimer = myPopupAskForInput(toolbox_frame_,
                                        "DELETE MD custom Theme file",
                                        "DISCLAIMER:",
                                        "Type 'IAGREE' to DELETE custom theme file",
                                        "NO",
                                        False,
                                        JOptionPane.ERROR_MESSAGE)
        if disclaimer != "IAGREE":
            statusLabel.setText("User declined to agree to disclaimer >> custom Theme file!".ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            myPopupInformationBox(toolbox_frame_,"User declined to agree to disclaimer - NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        myPrint("DB", "User confirmed to delete custom Theme file...")

        try:
            if not backup_custom_theme_file():
                statusLabel.setText("Error backing up custom theme file prior to deletion - no changes made!".ljust(800, " "))
                statusLabel.setForeground(Color.RED)
                myPopupInformationBox(toolbox_frame_,"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
                return

            os.remove(customThemeFile)
            statusLabel.setText(("DELETED CUSTOM THEME FILE: " + customThemeFile).ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            myPrint("B", "User requested to delete custom theme file: ", customThemeFile, " - DELETED!")
            myPopupInformationBox(toolbox_frame_, "DELETED CUSTOM THEME FILE: %s" % customThemeFile, "DELETE CUSTOM THEME FILE", JOptionPane.WARNING_MESSAGE)

        except:
            myPrint("B", "Error deleting custom theme file", "File:", customThemeFile)
            dump_sys_error_to_md_console_and_errorlog()
            statusLabel.setText(("ERROR DELETING CUSTOM THEME FILE: " + customThemeFile).ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            myPopupInformationBox(toolbox_frame_, "ERROR DELETING CUSTOM THEME FILE: %s" % customThemeFile, "DELETE CUSTOM THEME FILE", JOptionPane.ERROR_MESSAGE)

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
        return

    def find_IOS_sync_data(statusLabel):
        global toolbox_frame_, debug, i_am_an_extension_so_run_headless

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        if not(Platform.isOSX() or Platform.isWindows()):
            myPrint("B","FindIOSSyncDataButtonAction() called, but not OSx or Windows!?")
            statusLabel.setText(("FindIOSSyncDataButtonAction() called, but not OSx or Windows!?").ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            return

        instructions = """
INSTRUCTIONS TO ATTEMPT TO RETRIEVE YOUR MONEYDANCE SYNC ENCRYPTION KEY FROM iPHONE/iPAD

NOTE: As of 15th January 2021, there is a new iOS app in Beta Test, this allows you to view your encryption passphrase
... I understand an Android version is also coming... Ideally use these first if you have access to your mobile

OTHERWISE:
STEP 1. Ensure you have the Moneydance iOS App working & Syncing on an iphone/iPad.
STEP 2. Perform an iPhone/iPad backup to your computer Using iTunes (or Finder on Mac Big Sur). Instructions below....
STEP 3. RETURN HERE and let Toolbox attempt search; or search manually yourself (instructions below)

-----------------------------------------------------------------------------------------------------------------------------        
NOTE: If on a Mac, and you want Toolbox to search in step 3, then you must change these Mac Settings first...        
>>The system prevents programmatic access to the backups.. 
>> Go to Mac / Settings / Security & Privacy. Privacy Tab
- Click the padlock to unlock the settings
- Scroll down left side to Full Disk Access
- On the right, find Moneydance and tick it (or click the + to add and tick it) to Grant Access
- Exit and restart Moneydance, then run this Toolbox option again (if you don't do this, it will not find your backups!)..
>> Change this setting back afterwards.....
-----------------------------------------------------------------------------------------------------------------------------        

NOTE: DO NOT EDIT THE FILE MENTIONED BELOW. ALWAYS QUIT WITHOUT SAVING.
IF YOU COPY THE FILE TO YOUR DESKTOP, MAKE SURE YOU COPY (and not move)...
(Normally you hold down the CTRL, or OPTION/ALT key whilst dragging so the icon changes to a plus and copy)


================================
Mac (easiest option if possible) 
================================
Please review these instructions:
https://support.apple.com/en-gb/guide/iphone/iph3ecf67d29/ios
- Essentially install iTunes (not needed on Mac Big Sur - which uses finder)
- Go to the iPhone/iPad tab, General options
- Perform a local backup (NOT ENCRYPTED)

>> Come back here after backup completed and then run this Toolbox option to search backups........ <<

OR MANUAL INSTRUCTIONS BELOW

This link has details on the backup location: https://support.apple.com/en-gb/HT204215

>> Locate your backup(s) in Finder: 
- Open Finder. Menu GO 
- Go To Folder 
- Copy and paste this:

~/Library/Application Support/MobileSync/Backup/ 
Press Return.

You will see a list of backups. (e.g. 00008030-000E31343A02802E) 
Right click this folder (the most recent) 
Select "New terminal at folder". Then terminal will open at this folder. 

Copy / paste this command below and press enter...

grep -rl tik_dropbox_md *

...wait...

It will find something like this: 
c8/c8c8dcebf5eab9bb14012e7df9ff46aa1d333a7c 
This is the file you need, stay in Terminal

plutil -p c8/c8c8dcebf5eab9bb14012e7df9ff46aa1d333a7c 
(and you will see the information on the screen next to "tik_dropbox_md_sync_key" =>

or do this: 
open -a TextEdit c8/c8c8dcebf5eab9bb14012e7df9ff46aa1d333a7c

And you will see text and gibberish..... but also your key... Your key should be visible... See example. My was after the text 'last_account_used2V'

(of course, now you know the file, you can find it, copy it to desktop, open with other text viewers....)


================================
WINDOWS 
================================
Download and install iTunes, plug in iPhone. Select the iPhone icon and you should see  (General) options
(Help here: https://support.apple.com/en-gb/guide/iphone/iph3ecf67d29/ios)

Perform a local backup, DESELECT Encrypt local backup. Select Backup NOW 

...wait...

>> Come back here after backup completed and then run this Toolbox option to search backups........ <<

OR MANUAL INSTRUCTIONS BELOW

When finished, locate your backup - help here: https://support.apple.com/en-gb/HT204215

In the taskbar search box, type command (no enter) and when there is a popup select run as administrator 
type 
cd %userprofile% (Or a different folder if in a different place) 
cd apple 
cd mobilesync 
cd backup 
dir 
Your backups will be listed. If only one, skip this next step, else find the latest…. Select/copy the name 
cd <the selected name>

So you will now be at something like...: 
C:\\Users\\<username>\\Apple\\MobileSync\\Backup\\00008030-000E31343A02802E> 
or 
C:\\Users\\<username>>\\Apple\\MobileSync\\Backup> (if only one backup)

Now type this and enter:

findstr /S /I /M /C:"tik_dropbox_md" *.* 
... wait ...

It will show you something like this..:

00008030-000E31343A02802E\\c8\\c8c8dcebf5eab9bb14012e7df9ff46aa1d333a7c

Backup name: 00008030-000E31343A02802E 
SubDir: c8 
Actual file name you want: c8c8dcebf5eab9bb14012e7df9ff46aa1d333a7c

Now copy/paste the whole string (one line) and type this (paste the long name) and enter

start notepad 00008030-000E31343A02802E\\c8\\c8c8dcebf5eab9bb14012e7df9ff46aa1d333a7c

Notepad is rubbish, so use the cursor and move right along the lines until you see your key... 
---

On both the above options, you can find and copy the file to your desktop. Rename the desktop copy to 'key.plist' for ease of use after you have it.

Once you have the file..: 
On windows you can download and use this tool: 
https://www.imactools.com/iphonebackupviewer/download/win 
Run the program, select the 3 line menu button top right, Tools, Property List View, then open the key.plist file you saved to your desktop..

On Mac, in terminal 
cd /Users/<yourname>/Desktop 
type and enter 
plutil -convert xml1 key.plist 
Now you will have a text readable version of the file you can open in a text editor..

<END>            
"""

        jif = QuickJFrame("View Instructions:", instructions,lAlertLevel=1).show_the_frame()
        jif.setLocationRelativeTo(toolbox_frame_)

        if not myPopupAskQuestion(jif,
                                  "SEARCH COMPUTER iOS BACKUP(s)",
                                  "This may be time consuming...Do you want to continue with the search for Encryption Sync Passphrases now?",
                                  JOptionPane.YES_NO_OPTION,
                                  JOptionPane.WARNING_MESSAGE):

            statusLabel.setText(("User Aborted iOS backup(s) search...").ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            return

        jif.dispose()

        if Platform.isOSX():
            searchList = ["Library/Application Support/MobileSync/Backup"]
        else:
            searchList = ["Apple\\MobileSync\\Backup",
                          "Apple Computer\\MobileSync\\Backup",
                          "AppData\\Roaming\\Apple\\MobileSync\\Backup",
                          "AppData\\Roaming\\Apple Computer\\MobileSync\\Backup"]


        miniText=""
        pathList = []
        for x in (searchList):
            fullPath = os.path.join(get_home_dir(), x)
            miniText += "%s\n" %fullPath
            if os.path.exists(fullPath) and os.path.isdir(fullPath):
                pathList.append(fullPath)

        if len(pathList)<1:
            statusLabel.setText(("Sorry - could not find your IOS Backup directory(s)...").ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            myPrint("B", "Sorry - could not find your IOS Backup directory(s) in %s ....:" %get_home_dir())
            myPrint("B", searchList)
            MyPopUpDialogBox(toolbox_frame_,"Search for iOS Backup(s) - could not find your directory(s):",
                             miniText,theTitle="RECOVER IOS SYNC KEY",OKButtonText="ABORT").go()
            return

        theIKReference = "c8c8dcebf5eab9bb14012e7df9ff46aa1d333a7c"  # WARNING, this may change? Might have to switch to finding the key..!
        diag = MyPopUpDialogBox(toolbox_frame_,"Please wait: searching iOS Backup(s)..",theTitle="SEARCH", theWidth=100, lModal=False,OKButtonText="WAIT")
        diag.go()

        def findIOSBackup(pattern, path):
            iFound=0                                                                                            # noqa
            result = []
            dotCounter = 0

            lContinueToEnd=False

            if not i_am_an_extension_so_run_headless:
                print "Searching for your iOS Backups (might be time consuming):.....",

            for root, dirs, files in os.walk(path):

                if dotCounter % 1000 <1:
                    if not i_am_an_extension_so_run_headless: print ".",

                if not dotCounter or (dotCounter % 10000 <1 and not lContinueToEnd):

                    options=["STOP HERE","SEARCH TO END", "KEEP ASKING"]
                    response = JOptionPane.showOptionDialog(toolbox_frame_,
                                                            "Are you OK to continue (%s found so far)?"%iFound,
                                                            "SEARCH COMPUTER FOR iOS BACKUP(s)",
                                                            0,
                                                            JOptionPane.QUESTION_MESSAGE,
                                                            None,
                                                            options,
                                                            options[2])
                    if response == 0:
                        statusLabel.setText(("User Aborted iOS Backup(s) search...").ljust(800, " "))
                        statusLabel.setForeground(Color.RED)
                        return result, iFound

                    elif response == 1:
                        lContinueToEnd = True

                dotCounter+=1

                if debug: myPrint("DB","Searching: %s" %(root))

                for name in files:
                    fp = os.path.join(root, name)
                    if os.path.islink(fp):
                        myPrint("DB", "found file link! %s - will skip" %fp)
                        continue
                    if fnmatch.fnmatch(name, pattern):
                        iFound+=1
                        result.append(fp)

                for name in dirs:
                    fp = os.path.join(root, name)
                    if os.path.islink(fp):
                        myPrint("DB", "found dir link! %s - will skip" %fp)
                        continue
                    if fnmatch.fnmatch(name, pattern):
                        iFound+=1
                        result.append(fp)

            return result, iFound

        iFound = 0
        fileList=[]

        for theDir in pathList:
            myPrint("P","Searching from Directory: %s" %theDir)

            holdFileList, holdFound = findIOSBackup(theIKReference, theDir)
            fileList += holdFileList
            iFound += holdFound

        diag.kill()

        print
        myPrint("B","Completed search for iOS Backup(s): %s found (called: %s)" %(iFound, theIKReference))

        if iFound < 1:
            statusLabel.setText(("Sorry - could not find the Moneydance Sync file(s) (%s) in iOS backup(s)..." %theIKReference).ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            myPrint("B", "Sorry - could not find the Moneydance Sync file(s) (%s) in iOS backup(s)..." %theIKReference)
            myPrint("B", fileList)
            x=""
            if Platform.isOSX():
                x="PLEASE CHECK YOU GRANTED FULL DISK ACCESS (READ INSTRUCTIONS)\n\n"
            MyPopUpDialogBox(toolbox_frame_,"Search for iOS Backups - SORRY >> COULD NOT FIND the Moneydance App Sync File (%s) in these directories:"%theIKReference,
                             x+miniText,theTitle="RECOVER IOS SYNC KEY",OKButtonText="CLOSE").go()
            return


        # ###############################################################################################
        # https://github.com/provegard/binaryplist/
        # Copyright (c) 2011, Per Rovegard <per@rovegard.se>
        # Licensed under the 3-clause BSD license.
        from struct import unpack
        from datetime import tzinfo, timedelta

        def dump_plist(obj, _format):
            if 'plist' == (_format or 'plist'):
                from plistlib import writePlist
                writePlist(obj, sys.stdout)
            elif 'json' == _format:
                import json
                s = json.dumps(obj, indent=2)
                print(s)

        def decode_plist(_filename, _format="plist", _search="ALL"):   # Can be "plist" or "json"
            with open(_filename, 'rb') as fd:
                try:
                    plist_root = read_binary_plist(fd)

                    if _search == "ALL":
                        dump_plist(plist_root, _format)
                    else:
                        if _search in plist_root:
                            return plist_root[_search]
                        else:
                            return "NOT FOUND"

                except PListFormatError as e:
                    myPrint("B","Format error: %s" % (e.message))
                    return "ERROR"
                except PListUnhandledError as e:
                    myPrint("B","Unhandled: %s" % (e.message))
                    return "ERROR"

        # HEADER
        #         magic number ("bplist")
        #         file format version
        #
        # OBJECT TABLE
        #         variable-sized objects
        #
        #         Object Formats (marker byte followed by additional info in some cases)
        #         null    0000 0000
        #         bool    0000 1000                       // false
        #         bool    0000 1001                       // true
        #         fill    0000 1111                       // fill byte
        #         int     0001 nnnn       ...             // # of bytes is 2^nnnn, big-endian bytes
        #         real    0010 nnnn       ...             // # of bytes is 2^nnnn, big-endian bytes
        #         date    0011 0011       ...             // 8 byte float follows, big-endian bytes
        #         data    0100 nnnn       [int]   ...     // nnnn is number of bytes unless 1111 then int count follows, followed by bytes
        #         string  0101 nnnn       [int]   ...     // ASCII string, nnnn is # of chars, else 1111 then int count, then bytes
        #         string  0110 nnnn       [int]   ...     // Unicode string, nnnn is # of chars, else 1111 then int count, then big-endian 2-byte uint16_t
        #                 0111 xxxx                       // unused
        #         uid     1000 nnnn       ...             // nnnn+1 is # of bytes
        #                 1001 xxxx                       // unused
        #         array   1010 nnnn       [int]   objref* // nnnn is count, unless '1111', then int count follows
        #                 1011 xxxx                       // unused
        #         set     1100 nnnn       [int]   objref* // nnnn is count, unless '1111', then int count follows
        #         dict    1101 nnnn       [int]   keyref* objref* // nnnn is count, unless '1111', then int count follows
        #                 1110 xxxx                       // unused
        #                 1111 xxxx                       // unused
        #
        # OFFSET TABLE
        #         list of ints, byte size of which is given in trailer
        #         -- these are the byte offsets into the file
        #         -- number of these is in the trailer
        #
        # TRAILER
        #         byte size of offset ints in offset table
        #         byte size of object refs in arrays and dicts
        #         number of offsets in offset table (also is number of objects)
        #         element # in offset table which is top level object
        #         offset table offset


        try:
            unichr(8364)                                                                                       # noqa
        except NameError:
            # Python 3
            def unichr(x):                                                                                                  # noqa
                return chr(x)

        # From CFDate Reference: "Absolute time is measured in seconds relative to the
        # absolute reference date of Jan 1 2001 00:00:00 GMT".
        SECS_EPOCH_TO_2001 = 978307200

        MARKER_NULL = 0X00
        MARKER_FALSE = 0X08
        MARKER_TRUE = 0X09
        MARKER_FILL = 0X0F                                                                                       # noqa
        MARKER_INT = 0X10
        MARKER_REAL = 0X20
        MARKER_DATE = 0X33
        MARKER_DATA = 0X40
        MARKER_ASCIISTRING = 0X50
        MARKER_UNICODE16STRING = 0X60
        MARKER_UID = 0X80
        MARKER_ARRAY = 0XA0
        MARKER_SET = 0XC0
        MARKER_DICT = 0XD0


        def read_binary_plist(fd):
            """Read an object from a binary plist.
            The binary plist format is described in CFBinaryPList.c at
            http://opensource.apple.com/source/CF/CF-550/CFBinaryPList.c. Only the top
            level object is returned.
            Raise a PListFormatError or a PListUnhandledError if the input data cannot
            be fully understood.
            Arguments:
            fd -- a file-like object that is seekable
            """
            r = BinaryPListReader(fd)
            return r.read()


        class PListFormatError(Exception):
            """Represent a binary plist format error."""
            pass


        class PListUnhandledError(Exception):
            """Represent a binary plist error due to an unhandled feature."""
            pass


        class ObjectRef(object):
            def __init__(self, index):
                self.index = index

            def resolve(self, lst):
                return lst[self.index]


        class BinaryPListReader(object):

            def __init__(self, fd):
                self._fd = fd
                self._offsets = None
                self.objectRefSize = None

            def read(self):
                fd = self._fd

                # start from the beginning to check the signature
                fd.seek(0, 0)
                buf = fd.read(7)

                # verify the signature; the first version digit is always 0
                if buf != b"bplist0":
                    raise PListFormatError("Invalid signature: %s" % (buf, ))

                # seek to and read the trailer (validation omitted for now)
                fd.seek(-32, 2)
                buf = fd.read(32)

                _, offsetIntSize, self.objectRefSize, numObjects, topObject, offsetTableOffset = unpack(">5x3B3Q", buf)

                # read the object offsets
                fd.seek(offsetTableOffset, 0)
                self._offsets = [self._read_sized_int(offsetIntSize) for _ in range(0, numObjects)]

                # read the actual objects
                objects = [self._read_object(offs) for offs in self._offsets]

                # resolve lazy values (references to the object list)
                self._resolve_objects(objects)

                return objects[topObject]

            # noinspection PyMethodMayBeStatic
            def _resolve_objects(self, objects):
                # all resolutions are in-place, to avoid breaking references to
                # the outer objects!
                for obj in objects:
                    if isinstance(obj, list):
                        for i in range(0, len(obj)):
                            obj[i] = obj[i].resolve(objects)
                    if isinstance(obj, set):
                        temp = [item.resolve(objects) for item in obj]
                        obj.clear()
                        obj.update(temp)
                    if isinstance(obj, dict):
                        temp = {k.resolve(objects): v.resolve(objects) for k, v in list(obj.items())}
                        obj.clear()
                        obj.update(temp)

            def _read_object(self, offset=-1):
                if offset >= 0:
                    self._fd.seek(offset)
                else:
                    offset = self._fd.tell()  # for the error message
                marker = ord(self._fd.read(1))
                nb1 = marker & 0xf0
                nb2 = marker & 0x0f

                obj = None
                if nb1 == MARKER_NULL:
                    if marker == MARKER_NULL:
                        obj = None
                    elif marker == MARKER_FALSE:
                        obj = False
                    elif marker == MARKER_TRUE:
                        obj = True
                    # TO DO: Fill byte, skip over
                elif nb1 == MARKER_INT:
                    count = 1 << nb2
                    obj = self._read_sized_int(count)
                elif nb1 == MARKER_REAL:
                    obj = self._read_sized_float(nb2)
                elif marker == MARKER_DATE:  # marker!
                    secs = self._read_sized_float(3)
                    secs += SECS_EPOCH_TO_2001
                    obj = datetime.datetime.fromtimestamp(secs, UTC())
                elif nb1 == MARKER_DATA:
                    # Binary data
                    count = self._read_count(nb2)
                    obj = self._fd.read(count)
                elif nb1 == MARKER_ASCIISTRING:
                    # ASCII string
                    count = self._read_count(nb2)
                    obj = self._fd.read(count).decode("ascii")
                elif nb1 == MARKER_UNICODE16STRING:
                    # UTF-16 string
                    count = self._read_count(nb2)
                    data = self._fd.read(count * 2)
                    chars = unpack(">%dH" % (count, ), data)
                    s = u''
                    for ch in chars:
                        s += unichr(ch)
                    obj = s
                elif nb1 == MARKER_UID:
                    count = 1 + nb2
                    obj = self._read_sized_int(count)
                elif nb1 == MARKER_ARRAY:
                    count = self._read_count(nb2)
                    # we store lazy references to the object list
                    obj = [ObjectRef(self._read_sized_int(self.objectRefSize)) for _ in range(0, count)]
                elif nb1 == MARKER_SET:
                    count = self._read_count(nb2)
                    # we store lazy references to the object list
                    obj = set([ObjectRef(self._read_sized_int(self.objectRefSize)) for _ in range(0, count)])
                elif nb1 == MARKER_DICT:
                    count = self._read_count(nb2)
                    # first N keys, then N values
                    # we store lazy references to the object list
                    keys = [ObjectRef(self._read_sized_int(self.objectRefSize)) for _ in range(0, count)]
                    values = [ObjectRef(self._read_sized_int(self.objectRefSize)) for _ in range(0, count)]
                    obj = dict(list(zip(keys, values)))

                try:
                    return obj
                except NameError:
                    raise PListFormatError("Unknown marker at position %d: %d" %
                                           (offset, marker))

            def _read_count(self, nb2):
                count = nb2
                if count == 0xf:
                    count = self._read_object()
                return count

            def _read_sized_float(self, log2count):
                if log2count == 2:
                    # 32 bits
                    ret, = unpack(">f", self._fd.read(4))
                elif log2count == 3:
                    # 64 bits
                    ret, = unpack(">d", self._fd.read(8))
                else:
                    raise PListUnhandledError("Unhandled real size: %d" %
                                              (1 << log2count, ))
                return ret

            def _read_sized_int(self, count):
                # in format version '00', 1, 2, and 4-byte integers have to be
                # interpreted as unsigned, whereas 8-byte integers are signed
                # (and 16-byte when available). negative 1, 2, 4-byte integers
                # are always emitted as 8 bytes in format '00'
                buf = self._fd.read(count)
                if count == 1:
                    ret = ord(buf)
                elif count == 2:
                    ret, = unpack(">H", buf)
                elif count == 4:
                    ret, = unpack(">I", buf)
                elif count == 8:
                    ret, = unpack(">q", buf)
                else:
                    raise PListUnhandledError("Unhandled int size: %d" %
                                              (count, ))
                return ret


        class UTC(tzinfo):

            def utcoffset(self, dt):
                return timedelta(0)

            def tzname(self, dt):
                return "UTC"

            def dst(self, dt):
                return timedelta(0)

        # typedef struct {
        #    uint8_t  _unused[5];
        #    uint8_t  _sortVersion;
        #    uint8_t  _offsetIntSize;
        #    uint8_t  _objectRefSize;
        #    uint64_t _numObjects;
        #    uint64_t _topObject;
        #    uint64_t _offsetTableOffset;
        # } CFBinaryPlistTrailer;

        syncPassphrases=[]
        for foundFile in fileList:
            try:
                theSyncKey = decode_plist(foundFile,_format="plist",_search="tik_dropbox_md_sync_key")
                syncPassphrases.append(theSyncKey)
            except:
                syncPassphrases.append("Sorry - caught an error decoding the file")

        niceFileList="\n SEARCH FOR MONEYDANCE (%s) iOS Backup(s)\n"%theIKReference
        niceFileList+="Search for these Directories:\n"
        niceFileList+=miniText
        niceFileList+="\nFound these Directories:\n"

        for x in pathList:
            niceFileList+="%s\n" %x
        niceFileList+="\n"

        if not iFound:
            niceFileList+="\n<NONE FOUND>\n"

        for x in fileList:
            myPrint("B","Found: %s" %x)
            niceFileList+=x+"\n"

        niceFileList+="\nPOSSIBLE SYNC ENCRYPTION PASSPHRASES:\n"
        if len(syncPassphrases) < 1:
            niceFileList+="\n<NONE FOUND>\n"

        for encryptionKey in syncPassphrases:
            niceFileList+="%s\n" %encryptionKey

        niceFileList+="\n\n<END>"
        statusLabel.setText(("Find my iOS Backup(s) found %s files, with %s possible Sync Encryption keys" %(iFound,len(syncPassphrases))).ljust(800, " "))
        statusLabel.setForeground(DARK_GREEN)

        jif=QuickJFrame("LIST OF MONEYDANCE iOS Backups and Sync Encryption keys FOUND".upper(), niceFileList, lAlertLevel=1).show_the_frame()

        myPopupInformationBox(jif, "%s Sync Encryption keys found...." %(len(syncPassphrases)), "iOS BACKUP SEARCH", JOptionPane.INFORMATION_MESSAGE)

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
        return

    def import_QIF(statusLabel):
        global toolbox_frame_, debug, DARK_GREEN, lCopyAllToClipBoard_TB
        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        if Platform.isOSX():
            System.setProperty("com.apple.macos.use-file-dialog-packages", "true")  # In theory prevents access to app file structure (but doesnt seem to work)
            System.setProperty("apple.awt.fileDialogForDirectories", "false")

        fDialog = FileDialog(toolbox_frame_, "Select QIF file for import")
        fDialog.setMultipleMode(False)
        fDialog.setMode(FileDialog.LOAD)
        fDialog.setFile("select_your_file.qif")
        fDialog.setDirectory(get_home_dir())

        # Copied from MD code... File filters only work on non Macs (or Macs below certain versions)
        if (not Platform.isOSX() or not Platform.isOSXVersionAtLeast("10.13")):
            extfilter = ExtFilenameFilter("qif")
            fDialog.setFilenameFilter(extfilter)

        fDialog.setVisible(True)

        if (fDialog.getFile() is None) or fDialog.getFile() == "":
            statusLabel.setText(("QIF IMPORT: User chose to cancel or no file selected >>  So no Import will be performed... ").ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            myPopupInformationBox(toolbox_frame_,"User chose to cancel or no file selected >>  So no Import will be performed... ","QIF FILE SELECTION", theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        QIFfilename = os.path.join(fDialog.getDirectory(), fDialog.getFile())

        if not os.path.exists(QIFfilename) or not os.path.isfile(QIFfilename):
            statusLabel.setText(("QIF IMPORT: Sorry, file selected to import either does not exist or is not a file").ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            myPopupInformationBox(toolbox_frame_,"QIF IMPORT: Sorry, file selected to import either does not exist or is not a file","QIF FILE SELECTION", theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        dropdownAccts=AccountUtil.allMatchesForSearch(moneydance_data, MyAcctFilter(5))
        dropdownAccts=sorted(dropdownAccts, key=lambda sort_x: (sort_x.getAccountType(), sort_x.getFullAccountName().upper()))  # type: [Account]
        dropdownAccts.insert(0,"<NONE: USE QIF SPECIFIED>")

        label_QIF = JLabel("%s" %(os.path.basename(QIFfilename)))

        label_accounts = JLabel("Select Default Account if none specified in QIF:")
        user_accounts = JComboBox(dropdownAccts)

        # QIF_FORMATS = ["QIF_FORMAT_AUTO", "QIF_FORMAT_MMDDYY", "QIF_FORMAT_DDMMYY", "QIF_FORMAT_YYMMDD"]
        QIF_FORMATS = ["QIF_FORMAT_AUTO", "QIF_FORMAT_MMDDYY", "QIF_FORMAT_DDMMYY", "QIF_FORMAT_YYMMDD"]
        label_qif_format = JLabel("Select QIF Format")
        user_QIF_format = JComboBox(QIF_FORMATS)

        decimalStrings = [".",","]
        label_decimal = JLabel("Select your decimal point character")
        user_selectDecimal = JComboBox(decimalStrings)
        user_selectDecimal.setSelectedIndex(0)

        dropdownCurrs=[]
        currencies = moneydance_data.getCurrencies().getAllCurrencies()
        for curr in currencies:
            if curr.getCurrencyType() != CurrencyType.Type.CURRENCY: continue                                  # noqa
            dropdownCurrs.append(curr)
        dropdownCurrs=sorted(dropdownCurrs, key=lambda sort_x: (sort_x.getName().upper()))
        label_currency = JLabel("Select Default Currency for any Accounts created:")
        user_currency = JComboBox(dropdownCurrs)
        user_currency.setSelectedItem(moneydance_data.getCurrencies().getBaseType())

        IMPORT_TYPE = ["QIF_MODE_TRANSFER", "QIF_MODE_DOWNLOAD"]
        # label_import_type = JLabel("Select Import Type")
        # user_import_type = JComboBox(IMPORT_TYPE)
        #

        label_import_type_transfer = JLabel("TRANSFER MODE?")
        user_import_type_transfer = JRadioButton("(transfer)", True)
        label_import_type_download = JLabel("DOWNLOAD (from bank) MODE?")
        user_import_type_download = JRadioButton("(disabled - use newer function)",False)
        user_import_type_download.setEnabled(False)
        bg2 = ButtonGroup()
        bg2.add(user_import_type_transfer)
        bg2.add(user_import_type_download)

        label_importStructure = JLabel("Import Structure only (no data)?")
        user_importStructureOnly = JRadioButton("(structure only)", False)
        label_importAllData = JLabel("Import all data?")
        user_importAllData = JRadioButton("(all data)", False)
        bg = ButtonGroup()
        bg.add(user_importStructureOnly)
        bg.add(user_importAllData)

        userFilters = JPanel(GridLayout(0, 2))
        userFilters.add(JLabel("IMPORT FILE:"))
        userFilters.add(label_QIF)
        userFilters.add(label_qif_format)
        userFilters.add(user_QIF_format)
        userFilters.add(label_decimal)
        userFilters.add(user_selectDecimal)
        userFilters.add(label_currency)
        userFilters.add(user_currency)
        userFilters.add(label_accounts)
        userFilters.add(user_accounts)
        userFilters.add(JLabel(""))
        userFilters.add(JLabel("---"))
        # userFilters.add(label_import_type)
        # userFilters.add(user_import_type)
        userFilters.add(label_import_type_transfer)
        userFilters.add(user_import_type_transfer)
        userFilters.add(label_import_type_download)
        userFilters.add(user_import_type_download)
        userFilters.add(JLabel(""))
        userFilters.add(JLabel("---"))
        userFilters.add(label_importStructure)
        userFilters.add(user_importStructureOnly)
        userFilters.add(label_importAllData)
        userFilters.add(user_importAllData)


        while True:
            options = ["EXIT", "IMPORT"]
            userAction = (JOptionPane.showOptionDialog(toolbox_frame_,
                                                       userFilters,
                                                       "IMPORT QIF (Older MD Function)",
                                                       JOptionPane.OK_CANCEL_OPTION,
                                                       JOptionPane.QUESTION_MESSAGE,
                                                       moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                       options, options[0]))
            if userAction != 1:
                statusLabel.setText(("QIF IMPORT: - User aborted - No changes made.....").ljust(800, " "))
                statusLabel.setForeground(Color.BLUE)
                myPopupInformationBox(toolbox_frame_,"QIF IMPORT: User Aborted - NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
                return

            if not user_importStructureOnly.isSelected() and not user_importAllData.isSelected():
                user_importStructureOnly.setForeground(Color.RED)
                user_importAllData.setForeground(Color.RED)
                continue

            if not user_import_type_transfer.isSelected() and not user_import_type_download.isSelected():
                user_import_type_transfer.setForeground(Color.RED)
                user_import_type_download.setForeground(Color.RED)
                continue

            break

        if user_QIF_format.getSelectedItem() == "QIF_FORMAT_AUTO":
            theQIFFormat = Common.QIF_FORMAT_AUTO
        elif user_QIF_format.getSelectedItem() == "QIF_FORMAT_MMDDYY":
            theQIFFormat = Common.QIF_FORMAT_MMDDYY
        elif user_QIF_format.getSelectedItem() == "QIF_FORMAT_DDMMYY":
            theQIFFormat = Common.QIF_FORMAT_DDMMYY
        elif user_QIF_format.getSelectedItem() == "QIF_FORMAT_YYMMDD":
            theQIFFormat = Common.QIF_FORMAT_YYMMDD
        else:
            statusLabel.setText(("QIF IMPORT: Error - QIF Format %s unknown / unsupported by Moneydance now....?!" %(user_QIF_format.getSelectedItem())).ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            myPopupInformationBox(toolbox_frame_,"QIF IMPORT: Error - QIF Format %s unknown / unsupported by Moneydance now....?! NO CHANGES MADE","QIF IMPORT" %(user_QIF_format.getSelectedItem()), theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        if user_import_type_transfer.isSelected():
            theImportType = Common.QIF_MODE_TRANSFER
        elif user_import_type_download.isSelected():
            theImportType = Common.QIF_MODE_DOWNLOAD
        else:
            statusLabel.setText(("QIF IMPORT: Error - QIF MODE unknown / unsupported by Moneydance now....?!" ).ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            myPopupInformationBox(toolbox_frame_,"QIF IMPORT: Error - QIF MODE unknown / unsupported by Moneydance now....?! NO CHANGES MADE","QIF IMPORT", theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        # if user_import_type.getSelectedItem() == "QIF_MODE_TRANSFER":
        #     theImportType = Common.QIF_MODE_TRANSFER
        # elif user_import_type.getSelectedItem() == "QIF_MODE_DOWNLOAD":
        #     theImportType = Common.QIF_MODE_DOWNLOAD
        # else:
        #     statusLabel.setText(("QIF IMPORT: Error - QIF MODE %s unknown / unsupported by Moneydance now....?!" %(user_import_type.getSelectedItem())).ljust(800, " "))
        #     statusLabel.setForeground(Color.RED)
        #     myPopupInformationBox(toolbox_frame_,"QIF IMPORT: Error - QIF MODE %s unknown / unsupported by Moneydance now....?! NO CHANGES MADE","QIF IMPORT" %(user_import_type.getSelectedItem()), theMessageType=JOptionPane.WARNING_MESSAGE)
        #     return

        theAcct = None
        if isinstance(user_accounts.getSelectedItem(), Account):
            theAcct = user_accounts.getSelectedItem()

        msg =  "File name:        %s\n"         %(QIFfilename)
        msg += "QIF Format:       %s (%s)\n"    %(user_QIF_format.getSelectedItem(),theQIFFormat)
        msg += "Decimal Char:     %s\n"         %(user_selectDecimal.getSelectedItem())
        msg += "Default Currency: %s\n"         %(user_currency.getSelectedItem())
        msg += "Default Account:  %s\n"         %(user_accounts.getSelectedItem())
        msg += "Import Type:      %s (%s)\n"    %(IMPORT_TYPE[theImportType],theImportType)
        msg += "Structure Only:   %s\n"         %(user_importStructureOnly.isSelected())

        ask=MyPopUpDialogBox(toolbox_frame_,
                             theStatus="Please confirm parameters:",
                             theMessage=msg,
                             theWidth=225,
                             theTitle="QIF IMPORT",
                             OKButtonText="PROCEED",
                             lCancelButton=True)
        if (not ask.go()
                or not myPopupAskBackup(toolbox_frame_,"Do you want to make a Backup before your QIF Import?")):
            statusLabel.setText(("QIF IMPORT: User aborted - NO CHANGES MADE").ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            myPopupInformationBox(toolbox_frame_,"User aborted, NO CHANGES MADE","QIF IMPORT", theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        myPrint("B","User has requested a QIF import with these following parameters:\n")
        myPrint("B",msg)
        myPrint("J",">>EXECUTING IMPORT................\n")

        moneydance.importQIFIntoAccount(    moneydance_data,
                                            File(QIFfilename),
                                            theQIFFormat,                           # one of Common.QIF_FORMAT_MMDDYY, QIF_FORMAT_YYMMDD, QIF_FORMAT_DDMMYY, QIF_FORMAT_AUTO
                                            user_selectDecimal.getSelectedItem(),   # your decimal place character.
                                            user_currency.getSelectedItem(),        # the default currency to use for any new accounts that are created
                                            theAcct,                                # the default account to import into (though the QIF file may also specify multiple accounts with names)
                                            theImportType,                          # Common.QIF_MODE_DOWNLOAD or Common.QIF_MODE_TRANSFER
                                            user_importStructureOnly.isSelected())  # if true, only import the account and category structure

        myPrint("J",">>FINISHED IMPORT................\n")

        statusLabel.setText(("QIF IMPORT: File %s imported - review console log for messaged" %(os.path.basename(QIFfilename))).ljust(800, " "))
        statusLabel.setForeground(Color.BLUE)
        play_the_money_sound()
        myPopupInformationBox(toolbox_frame_,
                              "File %s imported - review console log for messaged" %(os.path.basename(QIFfilename)),
                              "QIF IMPORT",
                              theMessageType=JOptionPane.WARNING_MESSAGE)

        ConsoleWindow.showConsoleWindow(moneydance_ui)

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

        return

    def force_remove_extension(statusLabel):
        global toolbox_frame_, debug
        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )

        myPrint("DB", "User requested to delete all references to orphaned/outdated Extensions from config.dict and *.mxt files...")

        orphan_prefs, orphan_files, orphan_confirmed_extn_keys = get_orphaned_extension()

        if len(orphan_prefs)<1 and len(orphan_files)<1 and len(orphan_confirmed_extn_keys)<1:
            statusLabel.setText("No orphaned Extension preferences or files detected - nothing to do!".ljust(800, " "))
            statusLabel.setForeground(Color.BLUE)
            myPopupInformationBox(toolbox_frame_,"No orphaned Extension preferences or files detected - nothing to do! - NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        displayData="\nLISTING EXTENSIONS ORPHANED IN CONFIG.DICT OR FILES (*.MXT)\n\n"

        for x in orphan_prefs.keys():
            displayData+="%s Extension: %s is %s\n" %(pad("config.dict:",40),pad(x,40),pad(orphan_prefs[x],40))

        displayData+="\n"

        for x in orphan_confirmed_extn_keys.keys():
            _theVersion = moneydance_ui.getPreferences().getSetting(orphan_confirmed_extn_keys[x][1],None)
            displayData+="%s Extension: %s Key: %s (build: %s) is %s\n" %(pad("config.dict: ",40),pad(x,40),pad(orphan_confirmed_extn_keys[x][1],40),_theVersion,pad(orphan_confirmed_extn_keys[x][0],40))

        displayData+="\n"

        for x in orphan_files.keys():
            displayData+="%s Extension: %s is %s\n" %(pad("File: "+orphan_files[x][1],40),pad(x,40),pad(orphan_files[x][0],40))

        displayData+="\n<END>"
        jif = QuickJFrame("ORPHANED EXTENSIONS", displayData).show_the_frame()

        if not confirm_backup_confirm_disclaimer(jif, statusLabel, "DELETE ORPHANED EXTENSIONS", "delete the Extension Orphans?"):
            return

        extensionDir = Common.getFeatureModulesDirectory()
        if not extensionDir:
            statusLabel.setText("DELETE ORPHANED EXTENSIONS - Error getting Extensions directory - no changes made....".ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            myPopupInformationBox(jif,"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        if not backup_config_dict():
            statusLabel.setText("DELETE ORPHANED EXTENSIONS - Error backing up config.dict preferences file - no changes made....".ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            myPopupInformationBox(jif,"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        # reload latest preferences
        extension_prefs = moneydance_ui.getPreferences().getTableSetting("gen.fmodules",None)
        if not extension_prefs:
            statusLabel.setText("DELETE ORPHANED EXTENSIONS - Error getting gen.fmodules setting - no changes made....".ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            myPopupInformationBox(jif,"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        # OK - let's go....!! Delete away!!!
        for x in orphan_prefs.keys():
            extension_prefs.put(x,None)
            myPrint("B","Orphaned extension %s removed from config.dict!" %x)

        moneydance_ui.getPreferences().setSetting("gen.fmodules",extension_prefs)
        myPrint("B","config.dict gen.fmodules setting re-saved....")

        for x in orphan_confirmed_extn_keys:
            moneydance_ui.getPreferences().setSetting(orphan_confirmed_extn_keys[x][1],None)
            myPrint("B","Orphaned extension key %s removed from config.dict!" %orphan_confirmed_extn_keys[x][1])

        moneydance.savePreferences()

        lError=False
        # extensionDir = Common.getFeatureModulesDirectory()
        for x in orphan_files.keys():
            # noinspection PyTypeChecker
            fileToDelete = os.path.join(extensionDir.getAbsolutePath(),orphan_files[x][1])
            if not os.path.exists(fileToDelete):
                lError=True
                myPrint("B","ERROR orphaned extension file %s MISSING" %fileToDelete)
            else:
                try:
                    os.remove(fileToDelete)
                    myPrint("B","Orphaned extension file %s deleted" %fileToDelete)
                except:
                    lError=True
                    myPrint("B","ERROR deleting orphaned extension file %s deleted" %fileToDelete)
                    dump_sys_error_to_md_console_and_errorlog()

        play_the_money_sound()

        statusLabel.setForeground(Color.RED)

        if lError:
            myPrint("B", "Orphaned Extensions have been deleted - WITH ERRORS - from config.dict and the .MXT files from the Extensions folder....")
            statusLabel.setText("YOUR ORPHANED EXTENSIONS HAVE BEEN DELETED - WITH ERRORS - PLEASE REVIEW CONSOLE ERROR LOG!".ljust(800, " "))
            myPopupInformationBox(jif, "YOUR ORPHANED EXTENSIONS HAVE BEEN DELETED (WITH ERRORS) - PLEASE REVIEW MONEYBOT SCREEN AND CONSOLE ERROR LOG!", "DELETE ORPHANED EXTENSIONS", JOptionPane.ERROR_MESSAGE)
        else:
            myPrint("B", "SUCCESS - Your Orphaned Extensions have been deleted from config.dict and the .MXT files from the Extensions folder....")
            statusLabel.setText("SUCCESS - YOUR ORPHANED EXTENSIONS HAVE BEEN DELETED - I SUGGEST YOU RESTART MONEYDANCE!".ljust(800, " "))
            myPopupInformationBox(jif, "SUCCESS YOUR ORPHANED EXTENSIONS HAVE BEEN DELETED - PLEASE RESTART MONEYDANCE", "DELETE ORPHANED EXTENSIONS", JOptionPane.WARNING_MESSAGE)

        return

    def reset_window_positions(statusLabel):
        global toolbox_frame_, debug
        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        _RESETWINLOC    = 0
        _RESETREGFILT   = 1
        _RESETREGVIEW   = 2
        _RESETALL       = 3

        what = [
            "RESET - Only Window Locations on their own (Excludes Filters & Views)",
            "RESET - Only Transaction Register Filters",
            "RESET - Only Transaction Register Initial / Current View screen",
            "RESET - Window display settings (Sizes, Locations, Sorts, Widths etc) - Everything EXCEPT Filters & Views"
        ]

        resetWhat = JOptionPane.showInputDialog(toolbox_frame_,
                                                "Select the Window display setting(s) to RESET",
                                                "RESET WINDOW DISPLAY SETTINGS",
                                                JOptionPane.WARNING_MESSAGE,
                                                None,
                                                what,
                                                None)
        if not resetWhat:
            statusLabel.setText(("No RESET WINDOW DISPLAY SETTINGS TYPE option was chosen - no changes made!").ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            myPopupInformationBox(toolbox_frame_,"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        myPrint("DB", "User requested to %s settings from config.dict, LocalStorage() ./safe/settings , and by account!" %resetWhat)

        lAll = lWinLocations = lRegFilters = lRegViews = False

        if resetWhat == what[_RESETALL]:        lAll            = True
        if resetWhat == what[_RESETWINLOC]:     lWinLocations   = True
        if resetWhat == what[_RESETREGFILT]:    lRegFilters     = True
        if resetWhat == what[_RESETREGVIEW]:    lRegViews       = True

        def get_set_config(st, tk, lReset, lResetAll, lResetWinLoc, lResetRegFilters, lResetRegViews ):                                                               # noqa
            # As of 2021.2010   Window locations are only in config.dict.
            #                   Register Filters and Initial Register Views are only in LocalStorage()
            #                   column width, sort orders, etc are everywhere......

            configData = []

            if not lReset:
                configData.append("\nDATA STORED WITHIN CONFIG.DICT (effectively defaults where not specifically set by Account):")
                configData.append("--------------------------------------------------------------------------------------------")

            lastKey = None
            for theKey in tk:
                # Skip config settings we don't want to reset

                # Main safety filter here
                value = st.get(theKey)
                if not check_for_window_display_data(theKey, value): continue

                if lResetAll:
                    pass
                elif lResetWinLoc:
                    if not check_for_just_locations_window_display_data(theKey, value): continue
                elif lResetRegFilters:
                    if not check_for_just_register_filters_window_display_data(theKey, None): continue
                elif lResetRegViews:
                    if not check_for_just_initial_view_filters_window_display_data(theKey, None): continue
                else:
                    myPrint("B", "@@@ ERROR in get_set_config(): unexpected parameter!?")
                    raise(Exception("@@@ ERROR in get_set_config(): unexpected parameter!?"))

                test = "col_widths."
                if theKey.startswith(test):
                    if lReset:
                        moneydance.getPreferences().setSetting(theKey, None)
                    else:
                        if theKey[:len(test)] != lastKey:
                            lastKey = theKey[:len(test)]
                            configData.append("COLUMN WIDTHS:")

                        configData.append(pad(theKey+":",30) + moneydance.getPreferences().getSetting(theKey, None).strip())
                    continue

                test = "ext_mgmt_win"
                if theKey.startswith(test):
                    if lReset:
                        moneydance.getPreferences().setSetting(theKey, None)
                    else:
                        if theKey[:len(test)] != lastKey:
                            lastKey = theKey[:len(test)]
                            configData.append("\nEXTENSIONS WINDOW:")
                        configData.append(pad(theKey+":",30) + moneydance.getPreferences().getSetting(theKey, None).strip())
                    continue

                test = "moneybot_py_divider"
                if theKey.startswith(test):
                    if lReset:
                        moneydance.getPreferences().setSetting(theKey, None)
                    else:
                        if theKey[:len(test)] != lastKey:
                            lastKey = theKey[:len(test)]
                            configData.append("\nMONEYBOT:")
                        configData.append(pad(theKey+":",30) + moneydance.getPreferences().getSetting(theKey, None).strip())
                    continue

                test = "mbot."
                if theKey.startswith(test):
                    if lReset:
                        moneydance.getPreferences().setSetting(theKey, None)
                    else:
                        if theKey[:len(test)] != lastKey:
                            lastKey = theKey[:len(test)]
                            configData.append("\nMONEYBOT:")
                        configData.append(pad(theKey+":",30) + moneydance.getPreferences().getSetting(theKey, None).strip())
                    continue

                test = "gui."
                if theKey.startswith(test):
                    if lReset:
                        moneydance.getPreferences().setSetting(theKey, None)
                    else:
                        if theKey[:len(test)] != lastKey:
                            lastKey = theKey[:len(test)]
                            configData.append("\nGUI.:")
                        configData.append(pad(theKey+":",30) + moneydance.getPreferences().getSetting(theKey, None).strip())
                    continue

                myPrint("B","@@ RESET WINDOW DATA - ERROR >> What is this key: %s ? @@" %theKey)
                raise(Exception("ERROR - caught an un-coded key: " + str(theKey)))

            # END OF config.dict search
            ########################################################################################################

            if lResetAll or lResetRegFilters or lResetRegViews:
                # Now get the same data for each account
                accounts = AccountUtil.allMatchesForSearch(moneydance_data, MyAcctFilter(6))

                if not lReset:
                    configData.append("\nDATA STORED INTERNALLY BY ACCOUNT (not config.dict):")
                    configData.append("-----------------------------------------------------")

                dataPrefKey = "col_widths."
                dataPrefKeys_legacy = [  "gui.col_widths",
                                         "rec_reg.credit",
                                         "rec_reg.debit" ]

                keyIterator=[]
                if lResetRegFilters:    keyIterator.append("sel_reg_filter")
                if lResetRegFilters:    keyIterator.append("sel_invreg_filter")
                if lResetRegViews:      keyIterator.append("sel_inv_view")

                for acct in accounts:

                    last = None

                    if lResetAll:
                        for x in _COLWIDTHS:
                            xx = acct.getPreference(dataPrefKey+x, None)

                            if xx:
                                if lReset:
                                    # NOTE: This really sets the preference in LocalStorage() with the acct's UUII+"." prepended as the key!!!! (Sneaky eh!!??)
                                    acct.setPreference(dataPrefKey+x, None)
                                    # acct.syncItem() # Not entirely sure about this.... If Preference goes to LocalStorage() then Acct shouldn't be affected..
                                else:
                                    if last != acct:
                                        last = acct
                                        configData.append("\n>>Account: %s" %(acct.getAccountName()))

                                    configData.append("Key: %s Value: %s" %(pad(dataPrefKey+x+":",30),str(xx).strip()))

                    if lResetRegFilters or lResetRegViews:
                        for x in keyIterator:
                            xx = acct.getPreference(x, None)

                            if xx:
                                if lReset:
                                    # NOTE: This really sets the preference in LocalStorage() with the acct's UUII+"." prepended as the key!!!! (Sneaky eh!!??)
                                    acct.setPreference(x, None)
                                    # acct.syncItem() # Not entirely sure about this.... If Preference goes to LocalStorage() then Acct shouldn't be affected..
                                else:
                                    if last != acct:
                                        last = acct
                                        configData.append("\n>>Account: %s" %(acct.getAccountName()))

                                    configData.append("Key: %s Value: %s" %(pad(x+":",30),str(xx).strip()))

                    lNeedsSync = False

                    if lResetAll:
                        for theLegacyKey in dataPrefKeys_legacy:

                            # Look for legacy keys actually on the account..!
                            yy = acct.getParameter(theLegacyKey, None)

                            if yy:  # Should be a legacy setting
                                if lReset:
                                    acct.setParameter(theLegacyKey, None)
                                    lNeedsSync = True
                                else:
                                    if last != acct:
                                        last = acct
                                        configData.append("\n>>Account: %s" %(acct.getAccountName()))

                                    configData.append("Legacy Key: %s Value: %s" %(pad(theLegacyKey+":",30-7),str(yy).strip()))

                    if lResetRegFilters or lResetRegViews:
                        for theLegacyKey in keyIterator:

                            # Look for legacy keys actually on the account..!
                            yy = acct.getParameter(theLegacyKey, None)

                            if yy:  # Should be a legacy setting
                                if lReset:
                                    acct.setParameter(theLegacyKey, None)
                                    lNeedsSync = True
                                else:
                                    if last != acct:
                                        last = acct
                                        configData.append("\n>>Account: %s" %(acct.getAccountName()))

                                    configData.append("Legacy Key: %s Value: %s" %(pad(theLegacyKey+":",30-7),str(yy).strip()))

                    if lReset and lNeedsSync:
                        acct.syncItem()

                # END OF Accounts search
                ########################################################################################################

                if not lReset:
                    configData.append("\nDATA STORED INTERNALLY WITHIN LOCAL STORAGE (not config.dict):")
                    configData.append("----------------------------------------------------------------")

                LS = moneydance_ui.getCurrentAccounts().getBook().getLocalStorage()
                keys=sorted(LS.keys())

                if lResetAll:

                    last = None

                    for theKey in keys:
                        value = LS.get(theKey)

                        for theTypeToCheck in dataPrefKeys_legacy:

                            if theKey.endswith("."+theTypeToCheck):

                                if lReset:
                                    LS.put(theKey, None)
                                else:
                                    splitKey = theKey.split('.')
                                    if splitKey[0] != last:
                                        last = splitKey[0]
                                        lookupAcct = moneydance_data.getAccountByUUID(splitKey[0])
                                        if lookupAcct:
                                            configData.append("\n>>Account: %s" %(lookupAcct.getAccountName()))
                                        else:
                                            configData.append("\n>>Account: <NOT FOUND> ???")

                                    configData.append("LS Key: %s Value: %s" %(pad(theKey+":",55),str(value).strip()))

                        # Now look for keys not linked to Accounts... Perhaps deleted ones?
                        for theTypeToCheck in _COLWIDTHS:

                            if theKey.endswith(".col_widths."+theTypeToCheck):

                                splitKey = theKey.split('.')
                                lookupAcct = moneydance_data.getAccountByUUID(splitKey[0])

                                if lookupAcct: continue     # Found one, probably caught above, so skip

                                if lReset:
                                    LS.put(theKey, None)
                                else:
                                    if splitKey[0] != last:
                                        last = splitKey[0]
                                        configData.append("\n>>Account: <NOT FOUND> ??? (probably a deleted account)")

                                    configData.append("LS Key: %s Value: %s" %(pad(theKey+":",55),str(value).strip()))

                if lResetRegFilters or lResetRegViews:

                    last = None

                    for theKey in keys:
                        value = LS.get(theKey)

                        if lResetRegFilters:
                            if not check_for_just_register_filters_window_display_data(theKey, None):
                                continue
                        elif lResetRegViews:
                            if not check_for_just_initial_view_filters_window_display_data(theKey, None):
                                continue
                        else:
                            myPrint("B", "@@ ERROR: RESET WINDOW DISPLAY SETTINGS - Unexpected filter!?")
                            raise(Exception("@@ ERROR: RESET WINDOW DISPLAY SETTINGS - Unexpected filter!?"))

                        if lReset:
                            LS.put(theKey, None)
                        else:
                            splitKey = theKey.split('.')
                            if splitKey[0] != last:
                                last = splitKey[0]
                                lookupAcct = moneydance_data.getAccountByUUID(splitKey[0])
                                if lookupAcct:
                                    configData.append("\n>>Account: %s" %(lookupAcct.getAccountName()))
                                else:
                                    configData.append("\n>>Account: <NOT FOUND>???")

                            configData.append("LS Key: %s Value: %s" %(pad(theKey+":",55),str(value).strip()))

                # END OF LocalStorage() search
                ########################################################################################################

            configData.append("\n <END>")

            for i in range(0, len(configData)):
                configData[i] = configData[i] + "\n"

            configData = "".join(configData)

            if not lReset:
                jif = QuickJFrame("View the relevant RESET WINDOW DISPLAY SETTINGS that will be reset if you select OK to proceed", configData).show_the_frame()
                return jif

            return

        st,tk = read_preferences_file(lSaveFirst=False)

        if not st:
            statusLabel.setText("ERROR: RESET WINDOW DISPLAY SETTINGS >> reading and sorting the data file - no changes made!...".ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            myPopupInformationBox(None,"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        myPrint("D", "\nDisplaying the relevant RESET WINDOW DISPLAY SETTINGS (in various places) that I can reset.....:\n")

        theNewViewFrame = get_set_config(st, tk, False, lAll, lWinLocations, lRegFilters, lRegViews)

        if not myPopupAskQuestion(theNewViewFrame,
                                  "RESET WINDOW DISPLAY SETTINGS",
                                  "WARNING: Have you closed all Account Register windows and made sure only the Main Home Screen / Summary page is visible first??",
                                  JOptionPane.YES_NO_OPTION,
                                  JOptionPane.WARNING_MESSAGE):
            statusLabel.setText("WARNING: Please close all Account Register Windows and make sure only the Main Home Screen Summary/Dashboard is visible before running the Reset Windows Sizes tool..!".ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            myPopupInformationBox(theNewViewFrame,"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        if not confirm_backup_confirm_disclaimer(theNewViewFrame, statusLabel, "RESET WINDOW DISPLAY SETTINGS", "%s data?" %(resetWhat)):
            return

        if not backup_config_dict():
            statusLabel.setText(("RESET WINDOW DISPLAY SETTINGS: ERROR making backup of config.dict - no changes made!").ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            myPopupInformationBox(theNewViewFrame,"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        if not backup_local_storage_settings():
            statusLabel.setText(("RESET WINDOW DISPLAY SETTINGS: ERROR making backup of LocalStorage() ./safe/settings - no changes made!").ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            myPopupInformationBox(theNewViewFrame,"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        # DO THE RESET HERE
        get_set_config(st, tk, True, lAll, lWinLocations, lRegFilters, lRegViews)

        moneydance.savePreferences()                # save config.dict
        moneydance_data.getLocalStorage().save()    # Flush local storage to safe/settings

        play_the_money_sound()
        myPrint("B", "SUCCESS - %s data reset in config.dict config file, internally by Account & Local Storage...."%resetWhat)
        statusLabel.setText(("OK - %s settings forgotten.... I SUGGEST YOU RESTART MONEYDANCE!" %resetWhat).ljust(800, " "))
        statusLabel.setForeground(Color.RED)
        myPopupInformationBox(theNewViewFrame, "SUCCESS - %s - PLEASE RESTART MONEYDANCE"%resetWhat, "RESET WINDOW DISPLAY SETTINGS", JOptionPane.WARNING_MESSAGE)

        return

    def hacker_mode_suppress_dropbox_warning(statusLabel):
        global toolbox_frame_, debug, DARK_GREEN, lCopyAllToClipBoard_TB
        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        ask=MyPopUpDialogBox(toolbox_frame_,theStatus="You can suppress the 'Your file seems to be in a shared folder' Warning..",
                             theMessage="Moneydance support states that you should NEVER store your dataset in Dropbox.\n"
                                        "... and that you should store your dataset locally and use Moneydance's built-in syncing instead to share across computers and devices.\n"
                                        "THEREFORE YOU PROCEED AT ENTIRELY YOUR OWN RISK AND ACCEPT THAT STORING IN DROPBOX MIGHT DAMAGE YOUR DATA!",
                             theWidth=200,
                             theTitle="SUPPRESS DROPBOX WARNING",
                             lCancelButton=True,
                             OKButtonText="ACCEPT RISK",
                             lAlertLevel=3)

        if not ask.go():
            statusLabel.setText(("'SUPPRESS DROPBOX WARNING' - User chose to exit  - no changes made").ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            return

        if confirm_backup_confirm_disclaimer(toolbox_frame_, statusLabel, "SUPPRESS DROPBOX WARNING", "Suppress 'Your data is stored in a shared folder' (Dropbox) message?"):
            suppressFile = os.path.join(moneydance_data.getRootFolder().getCanonicalPath(), "suppress_file_in_dropbox_restriction.txt")
            if not os.path.exists(suppressFile):
                try:
                    x=open(suppressFile, "w")
                    x.write("DISCLAIMER - YOU SUPPRESS THE 'Your file is stored in a shared folder' (Dropbox) WARNING AT YOUR OWN RISK\n"
                            "STORING YOUR MD DATASET IN DROPBOX CAN DAMAGE YOUR DATASET\n\n"
                            "(Warning courtesy of Toolbox)")

                    x.close()
                    myPrint("B","HACKER MODE: 'SUPPRESS DROPBOX WARNING': User requested to suppress the 'Your file is stored in a shared folder' (dropbox) warning....")
                    myPrint("B", "@@User accepted warnings and disclaimer about dataset damage and instructed Toolbox to create %s - EXECUTED" %(suppressFile))
                    play_the_money_sound()
                    statusLabel.setText("'SUPPRESS DROPBOX WARNING' - OK, I have suppressed the 'Your file is stored in a shared folder' (dropbox) warning. I suggest a restart of MD".ljust(800, " "))
                    statusLabel.setForeground(Color.RED)
                    myPopupInformationBox(toolbox_frame_,"OK, I have suppressed the 'Your file is stored in a shared folder' (dropbox) warning. I suggest a restart of MD","'SUPPRESS DROPBOX WARNING'",JOptionPane.ERROR_MESSAGE)
                    return
                except:
                    myPrint("B","'SUPPRESS DROPBOX WARNING' - Error creating %s" %(suppressFile))
                    dump_sys_error_to_md_console_and_errorlog()

            statusLabel.setText("'SUPPRESS DROPBOX WARNING' - ERROR - either the file already exists, or I failed to create the file..(review console log)?".ljust(800, " "))
            statusLabel.setForeground(Color.RED)

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

        return

    def hacker_mode_save_trunk_file(statusLabel):
        global toolbox_frame_, debug, DARK_GREEN, lCopyAllToClipBoard_TB
        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()" )


        if not confirm_backup_confirm_disclaimer(toolbox_frame_,statusLabel,"SAVE TRUNK FILE","execute Save Trunk File function?"):
            return

        myPrint("B","HACKER MODE: 'SAVE TRUNK FILE': Calling saveTrunkFile() now at user request....")
        moneydance_data.saveTrunkFile()
        play_the_money_sound()
        statusLabel.setText("'SAVE TRUNK FILE' - OK, I have executed the Save Trunk File function. I suggest a restart of MD".ljust(800, " "))
        statusLabel.setForeground(Color.RED)
        myPopupInformationBox(toolbox_frame_,"OK, I have executed the Save Trunk File function. I suggest a restart of MD","SAVE TRUNK FILE",JOptionPane.ERROR_MESSAGE)

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

        return

    def hacker_mode_set_check_days(statusLabel):
        global toolbox_frame_, debug, DARK_GREEN, lCopyAllToClipBoard_TB
        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        key = "moneydance.checknum_series_threshold"
        props_lookback_days = System.getProperty(key, "180")

        ask = MyPopUpDialogBox(toolbox_frame_,"Next Check Number Algorithm look-back Threshold:",
                               'System.getProperty("%s") currently set to: %s\n'%(key,props_lookback_days),
                               200,"NEXT CHEQUE NUMBER ALGORITHM",
                               lCancelButton=True,OKButtonText="CHANGE")
        if not ask.go():
            statusLabel.setText(("HACKER MODE: NO CHANGES MADE TO NEXT CHECK NUMBER LOOK-BACK THRESHOLD").ljust(800, " "))
            statusLabel.setForeground(Color.BLUE)
            return

        lDidIChangeDays=False

        while True:
            days_response = myPopupAskForInput(toolbox_frame_,"CHANGE NEXT CHECK NUMBER LOOK-BACK THRESHOLD","Days:",
                                               "Enter new number of days (1 to 365):",props_lookback_days)

            if days_response is None:
                days_response = 0
                break
            elif days_response == props_lookback_days:
                break
            elif not StringUtils.isInteger(days_response):
                continue
            elif int(days_response)>0 and int(days_response)<365:                                               # noqa
                lDidIChangeDays = True
                break

        if lDidIChangeDays:
            System.setProperty(key,str(days_response))
            myPrint("B","HACKER MODE: System Property '%s' set to %s" %(key,days_response))
        else:
            statusLabel.setText(("HACKER MODE: NO CHANGES MADE TO NEXT CHECK NUMBER LOOK-BACK THRESHOLD").ljust(800, " "))
            statusLabel.setForeground(Color.BLUE)
            return

        myPopupInformationBox(toolbox_frame_,"HACKER MODE: Next Check Number Algorithm look-back Threshold set to %s (days)" %days_response,"NEXT CHEQUE NUMBER ALGORITHM",JOptionPane.WARNING_MESSAGE)
        statusLabel.setText(("HACKER MODE: Next Check Number Algorithm look-back Threshold set to %s (days)" %days_response).ljust(800, " "))
        statusLabel.setForeground(Color.BLUE)

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

        return

    def hacker_mode_edit_parameter_keys(statusLabel):
        global toolbox_frame_, debug, DARK_GREEN, lCopyAllToClipBoard_TB
        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        if moneydance_data is None: return

        if not myPopupAskQuestion(toolbox_frame_,"HACKER: EDIT OBJ'S MODE","DANGER - ARE YOU SURE YOU WANT TO VISIT THIS FUNCTION?",
                                  theMessageType=JOptionPane.ERROR_MESSAGE):
            statusLabel.setText(("Hacker Edit Obj Mode - User declined to proceed - aborting..").ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            return

        objSelecter = GeekOutModeButtonAction(statusLabel, lOFX=False, EDIT_MODE=True)
        theObject = objSelecter.actionPerformed("")  # type: list
        del objSelecter

        if theObject is None or len(theObject)!=1:
            # statusLabel.setText(("Hacker Edit Obj Mode - No Object selected/found - aborting..").ljust(800, " "))
            # statusLabel.setForeground(Color.RED)
            return

        theObject = theObject[0]            # type: MoneydanceSyncableItem

        _HACK_KEYADD          = 0
        _HACK_KEYCHG          = 1
        _HACK_KEYDEL          = 2
        _HACK_RECORDDELETE    = 3

        what = [
            "HACK: Object ADD    Parameter Key (and data)",
            "HACK: Object CHANGE Parameter Key's Data",
            "HACK: Object DELETE Parameter Key (and it's data)",
            "HACK: DELETE OBJECT - NOT RECOMMENDED!"
        ]

        while True:

            lAdd = lChg = lDel = lDeleteRecord = False

            selectedWhat = JOptionPane.showInputDialog(toolbox_frame_,
                                                       "Select the option for the HACK (on %s)?" %(theObject),
                                                       "HACKER",
                                                       JOptionPane.WARNING_MESSAGE,
                                                       None,
                                                       what,
                                                       None)

            if not selectedWhat:
                statusLabel.setText(("Thank you for using HACKER MODE!.. Exiting").ljust(800, " "))
                statusLabel.setForeground(Color.BLUE)
                return

            if selectedWhat == what[_HACK_KEYADD]:          lAdd = True
            if selectedWhat == what[_HACK_KEYCHG]:          lChg = True
            if selectedWhat == what[_HACK_KEYDEL]:          lDel = True
            if selectedWhat == what[_HACK_RECORDDELETE]:    lDeleteRecord = True

            text = ""
            if lChg:            text = "ADD"
            if lChg:            text = "CHANGE"
            if lDel:            text = "DELETE"
            if lDeleteRecord:   text = "DELETE OBJECT"

            if lAdd:
                addKey = myPopupAskForInput(toolbox_frame_,
                                            "HACKER: ADD PARAMETER TO %s" % (theObject),
                                            "PARAMETER:",
                                            "Carefully enter the name of the Parameter you want to add (cAseMaTTers!) - STRINGS ONLY:",
                                            "",
                                            False,
                                            JOptionPane.WARNING_MESSAGE)

                if not addKey or len(addKey.strip()) < 1: continue
                addKey = addKey.strip()

                if not check_if_key_string_valid(addKey):
                    myPopupInformationBox(toolbox_frame_, "ERROR: Parameter %s is NOT valid!" % addKey, "HACKER: ADD TO %s" %(theObject), JOptionPane.ERROR_MESSAGE)
                    continue    # back to Hacker menu

                testKeyExists = theObject.getParameter(addKey,None)                                             # noqa

                if testKeyExists:
                    myPopupInformationBox(toolbox_frame_, "ERROR: Parameter %s already exists - cannot add - aborting..!" %(addKey), "HACKER: ADD TO %s" %(theObject), JOptionPane.ERROR_MESSAGE)
                    continue    # back to Hacker menu

                addValue = myPopupAskForInput(toolbox_frame_,
                                              "HACKER: ADD PARAMETER VALUE TO %s" %(theObject),
                                              "VALUE:",
                                              "Carefully enter the value you want to add (STRINGS ONLY! CaSE MattERS):",
                                              "",
                                              False,
                                              JOptionPane.WARNING_MESSAGE)

                if not addValue or len(addValue.strip()) <1: continue
                addValue = addValue.strip()

                if not check_if_key_data_string_valid(addValue):
                    myPopupInformationBox(toolbox_frame_, "ERROR: Parameter value %s is NOT valid!" %(addValue), "HACKER: ADD TO %s" %(theObject), JOptionPane.ERROR_MESSAGE)
                    continue    # back to Hacker menu

                if confirm_backup_confirm_disclaimer(toolbox_frame_,statusLabel,"HACKER MODE","ADD PARAMETER VALUE TO %s" %(theObject)):

                    theObject.setParameter(addKey,addValue)                                                     # noqa
                    theObject.syncItem()                                                                        # noqa
                    play_the_money_sound()
                    myPrint("B","@@ HACKERMODE: Parameter: %s Value: %s added to %s @@" %(addKey,addValue,theObject))
                    statusLabel.setText(("@@ HACKERMODE: Parameter: %s Value: %s added to %s @@" %(addKey,addValue,theObject)).ljust(800, " "))
                    statusLabel.setForeground(Color.RED)
                    myPopupInformationBox(toolbox_frame_,
                                          "SUCCESS: Key %s added to %s!" % (addKey,theObject),
                                          "HACKER: ADD TO %s" %(theObject),
                                          JOptionPane.WARNING_MESSAGE)
                    continue

                continue

            # DELETE OBJECT  :-<
            if lDeleteRecord:

                output =  "%s PLEASE REVIEW PARAMETER & VALUE BEFORE DELETING OBJECT\n" %(theObject)
                output += "---------------------------------------------------------\n\n"

                paramKeys = sorted(theObject.getParameterKeys())                                                # noqa

                for param in paramKeys:
                    value = theObject.getParameter(param, None)                                                 # noqa
                    output += "\nParameter: %s Value: %s\n" %(pad(param,40), value)

                output += "\n<END>"
                jif = QuickJFrame("REVIEW THE OBJECT's DATA BEFORE DELETION", output).show_the_frame()

                if confirm_backup_confirm_disclaimer(jif,statusLabel,"HACKER: DELETE OBJECT","DELETE OBJECT %s" %(theObject)):

                    theObject.deleteItem()                                                                      # noqa
                    play_the_money_sound()

                    myPrint("B","@@ HACKERMODE: OBJECT %s DELETED @@" %(theObject))

                    statusLabel.setText(("@@ HACKERMODE: OBJECT %s DELETED @@" %(theObject)).ljust(800, " "))
                    statusLabel.setForeground(Color.RED)

                    myPopupInformationBox(jif,
                                          "SUCCESS: OBJECT %s DELETED" %(theObject),
                                          "HACKER: DELETE OBJECT",
                                          JOptionPane.ERROR_MESSAGE)
                    return

                continue

            # OK, so we are changing or deleting
            if lChg or lDel:

                paramKeys = sorted(theObject.getParameterKeys())                                                # noqa
                selectedKey = JOptionPane.showInputDialog(toolbox_frame_,
                                                          "Select the %s Parameter you want to %s" % (theObject,text),
                                                          "HACKER",
                                                          JOptionPane.WARNING_MESSAGE,
                                                          None,
                                                          paramKeys,
                                                          None)
                if not selectedKey: continue

                value = theObject.getParameter(selectedKey, None)                                               # noqa

                output =  "%s PLEASE REVIEW PARAMETER & VALUE BEFORE MAKING CHANGES\n" %(theObject)
                output += "------------------------------------------------\n\n"

                output += "\n@@ This '%s' key can be changed/deleted by this script @@\n" % selectedKey

                output += "\n%s %s\n" %(pad("%s PARAMETER:"%(theObject),25),selectedKey)
                output += "\n%s %s\n" %(pad("Type:",25), type(value))
                output += "\n%s %s\n" %(pad("Value:",25), value)

                output += "\n<END>"
                jif = QuickJFrame("REVIEW THE KEY BEFORE CHANGES to %s" %(theObject), output).show_the_frame()

                chgValue = None

                if lChg:
                    chgValue = myPopupAskForInput(jif,
                                                  "HACKER: CHANGE PARAMETER VALUE IN %s" %(theObject),
                                                  "VALUE:",
                                                  "Carefully enter the new value (STRINGS ONLY! CaSE MattERS):",
                                                  value,
                                                  False,
                                                  JOptionPane.WARNING_MESSAGE)

                    if not chgValue or len(chgValue.strip()) <1 or chgValue == value: continue
                    chgValue = chgValue.strip()

                    if not check_if_key_data_string_valid(chgValue):
                        myPopupInformationBox(jif,"ERROR: value %s is NOT valid!" %chgValue,"HACKER: CHANGE IN %s" %(theObject),JOptionPane.ERROR_MESSAGE)
                        continue    # back to Hacker menu

                confAction = ""
                if lDel:
                    confAction = "%s key: %s (with old value: %s)" %(text,selectedKey,value)
                if lChg:
                    confAction = "%s key: %s to new value: %s" %(text,selectedKey,chgValue)

                if confirm_backup_confirm_disclaimer(jif,statusLabel,"HACKER: %s VALUE IN %s" %(text,theObject),confAction):

                    if lDel:
                        theObject.setParameter(selectedKey,None)                                                # noqa
                    if lChg:
                        theObject.setParameter(selectedKey,chgValue)                                            # noqa
                    theObject.syncItem()                                                                        # noqa

                    moneydance.savePreferences()            # Flush all in memory settings to config.dict file on disk
                    play_the_money_sound()

                    if lDel:
                        myPrint("B","@@ HACKERMODE: Parameter: %s DELETED from %s (old value: %s) @@" %(selectedKey,theObject,value))
                        myPopupInformationBox(jif,
                                              "SUCCESS: Parameter: %s DELETED from %s (old value: %s)" %(selectedKey,theObject,value),
                                              "HACKER: DELETE IN %s" %theObject,
                                              JOptionPane.WARNING_MESSAGE)
                    if lChg:
                        myPrint("B","@@ HACKERMODE: Parameter: %s CHANGED to %s in %s @@" %(selectedKey,chgValue, theObject))
                        myPopupInformationBox(jif,
                                              "SUCCESS: Parameter: %s CHANGED to %s in %s" %(selectedKey,chgValue, theObject),
                                              "HACKER: CHANGE IN %s" %theObject,
                                              JOptionPane.WARNING_MESSAGE)
                    jif.dispose()
                    continue

                jif.dispose()
                continue

        # ENDWHILE

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

        return

    def hacker_remove_int_external_files_settings(statusLabel):
        global toolbox_frame_, debug, DARK_GREEN, lCopyAllToClipBoard_TB
        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        if moneydance_data is None: return

        options = ["Remove 'External' entries from File>Open menu [and optionally DELETE dataset from disk too]",
                   "DELETE 'Internal' / Default location dataset(s) from Disk (which will also remove entry from File>Open)"]

        selectedOption = JOptionPane.showInputDialog(toolbox_frame_,
                                                     "Select the option you require",
                                                     "HACKER: DELETE INT/EXT DATASET",
                                                     JOptionPane.WARNING_MESSAGE,
                                                     moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                     options,
                                                     None)

        if not selectedOption or options.index(selectedOption) > 1:
            statusLabel.setText(("No option selected.. No changes made").ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            myPopupInformationBox(toolbox_frame_,"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        theText = ""
        lInternal = lExternal = False
        if options.index(selectedOption) == 0:
            lExternal = True
            theText = ( "This allows you to REMOVE references to Datasets stored in the non-default/External locations\n"
                        "This removes the entries from the MD File>Open Menu.\n"
                        "(These may not actually exist on disk any more)\n"
                        "I will offer you each Dataset name one-by-one\n"
                        "You will not be offered, or allowed, to delete the current open dataset\n"
                        "OPTIONALLY - You can choose to also DELETE these dataset(s) FROM DISK (after your confirmation)\n"
                        "There will not be any backup prompts - please do this yourself first!\n"
                        "(RESTART MD AFTER USING TO REFRESH THE File>Open list)\n\n"
                        "THIS IS THE DISCLAIMER UP FRONT - CLICK I AGREE TO PROCEED" )
        elif options.index(selectedOption) == 1:
            lInternal = True
            theText = ( "This allows you to DELETE Datasets from the MD Internal/Default location\n"
                        "I will offer you each Dataset name one-by-one\n"
                        "You will not be offered, or allowed, to delete the current open dataset\n"
                        "Each one you select will be DELETED FROM DISK (after your confirmation)\n"
                        "(This will therefore remove the entry from the MD File>Open Menu)\n"
                        "There will not be any backup prompts - please do this yourself first!\n"
                        "(RESTART MD AFTER USING TO REFRESH THE File>Open list)\n\n"
                        "THIS IS THE DISCLAIMER UP FRONT - CLICK I AGREE TO PROCEED" )

        ask=MyPopUpDialogBox(toolbox_frame_,
                             "For Your Information",
                             theText,
                             theWidth=225,
                             theTitle="HACK: REMOVE ENTRIES/DATASETS",
                             OKButtonText="I AGREE - PROCEED", lCancelButton=True,
                             lAlertLevel=2)
        if not ask.go():
            statusLabel.setText(("No agreement to proceed.. No changes made").ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            myPopupInformationBox(toolbox_frame_,"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        if lInternal:
            hackerRemoveInternalFilesSettings(statusLabel)

        elif lExternal:
            hackerRemoveExternalFilesSettings(statusLabel)

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

        return

    def hacker_mode(statusLabel):
        global toolbox_frame_, debug, DARK_GREEN, lCopyAllToClipBoard_TB
        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        if moneydance_data is None: return

        _HACKCONFIGADD          = 0
        _HACKCONFIGCHG          = 1
        _HACKCONFIGDEL          = 2
        _HACKLOCALSTORAGEADD    = 3
        _HACKLOCALSTORAGECHG    = 4
        _HACKLOCALSTORAGEDEL    = 5

        what = [
            "HACK: config.dict ADD setting",
            "HACK: config.dict CHANGE setting",
            "HACK: config.dict DELETE setting",
            "HACK Local Storage Setting ADD setting",
            "HACK Local Storage Setting CHANGE setting",
            "HACK Local Storage Setting DELETE setting"
        ]

        while True:

            lAdd = lChg = lDel = False
            lConfigDict = lLocalStorage = False

            # noinspection PyUnusedLocal
            LS = st = tk = prefs = fileType = None

            selectedWhat = JOptionPane.showInputDialog(toolbox_frame_,
                                                       "Select the Key data / option for the Hack",
                                                       "HACKER",
                                                       JOptionPane.WARNING_MESSAGE,
                                                       None,
                                                       what,
                                                       None)

            if not selectedWhat:
                statusLabel.setText(("Thank you for using HACKER MODE!..").ljust(800, " "))
                statusLabel.setForeground(Color.BLUE)
                return

            if selectedWhat == what[_HACKCONFIGADD]: lAdd = True
            if selectedWhat == what[_HACKCONFIGCHG]: lChg = True
            if selectedWhat == what[_HACKCONFIGDEL]: lDel = True
            if selectedWhat == what[_HACKLOCALSTORAGEADD]: lAdd = True
            if selectedWhat == what[_HACKLOCALSTORAGECHG]: lChg = True
            if selectedWhat == what[_HACKLOCALSTORAGEDEL]: lDel = True

            if selectedWhat == what[_HACKCONFIGADD]: lConfigDict = True
            if selectedWhat == what[_HACKCONFIGCHG]: lConfigDict = True
            if selectedWhat == what[_HACKCONFIGDEL]: lConfigDict = True
            if selectedWhat == what[_HACKLOCALSTORAGEADD]: lLocalStorage = True
            if selectedWhat == what[_HACKLOCALSTORAGECHG]: lLocalStorage = True
            if selectedWhat == what[_HACKLOCALSTORAGEDEL]: lLocalStorage = True

            LS = moneydance_ui.getCurrentAccounts().getBook().getLocalStorage()

            if lConfigDict:
                fileType = "config.dict"
                st,tk = read_preferences_file(lSaveFirst=True)  # Must flush memory to disk first before we read the file....
                prefs=sorted(tk)
            elif lLocalStorage:
                fileType = "LocalStorage() ./safe/settings"
                ls_keys = LS.keys()
                prefs=sorted(ls_keys)
            else:
                raise(Exception("ERROR - Unknown type!"))

            text = ""
            if lChg: text = "CHANGE"
            if lDel: text = "DELETE"

            if lAdd:
                addKey = myPopupAskForInput(toolbox_frame_,
                                            "HACKER: ADD KEY TO %s" % fileType,
                                            "KEY NAME:",
                                            "Carefully enter the name of the key you want to add (cAseMaTTers!) - STRINGS ONLY:",
                                            "",
                                            False,
                                            JOptionPane.WARNING_MESSAGE)

                if not addKey or len(addKey.strip()) < 1: continue
                addKey = addKey.strip()

                if not check_if_key_string_valid(addKey):
                    myPopupInformationBox(toolbox_frame_, "ERROR: Key %s is NOT valid!" % addKey, "HACKER: ADD TO %s" % fileType, JOptionPane.ERROR_MESSAGE)
                    continue    # back to Hacker menu

                testKeyExists = True
                if lConfigDict:     testKeyExists = moneydance_ui.getPreferences().getSetting(addKey,None)
                if lLocalStorage:   testKeyExists = LS.get(addKey)

                if testKeyExists:
                    myPopupInformationBox(toolbox_frame_, "ERROR: Key %s already exists - cannot add - aborting..!" % addKey, "HACKER: ADD TO %s" % fileType, JOptionPane.ERROR_MESSAGE)
                    continue    # back to Hacker menu

                addValue = myPopupAskForInput(toolbox_frame_,
                                              "HACKER: ADD KEY VALUE TO %s" % fileType,
                                              "KEY VALUE:",
                                              "Carefully enter the key value you want to add (STRINGS ONLY!):",
                                              "",
                                              False,
                                              JOptionPane.WARNING_MESSAGE)

                if not addValue or len(addValue.strip()) <1: continue
                addValue = addValue.strip()

                if not check_if_key_data_string_valid(addValue):
                    myPopupInformationBox(toolbox_frame_, "ERROR: Key value %s is NOT valid!" % addValue, "HACKER: ADD TO %s" % fileType, JOptionPane.ERROR_MESSAGE)
                    continue    # back to Hacker menu

                disclaimer = myPopupAskForInput(toolbox_frame_,
                                                "HACKER: ADD KEY VALUE TO %s" % fileType,
                                                "DISCLAIMER:",
                                                "Type 'IAGREE' to add key: %s with value: %s" % (addKey,addValue),
                                                "NO",
                                                False,
                                                JOptionPane.ERROR_MESSAGE)
                if disclaimer == "IAGREE":
                    if lConfigDict:
                        moneydance_ui.getPreferences().setSetting(addKey,addValue)
                        moneydance.savePreferences()                # Flush all in memory settings to config.dict file on disk
                    if lLocalStorage:
                        LS.put(addKey,addValue)
                        LS.save()    # Flush local storage to safe/settings

                    play_the_money_sound()
                    myPrint("B","@@ HACKERMODE: key: %s value: %s added to %s @@" %(addKey,addValue,fileType))
                    myPopupInformationBox(toolbox_frame_,
                                          "SUCCESS: Key %s added to %s!" % (addKey,fileType),
                                          "HACKER: ADD TO %s" % fileType,
                                          JOptionPane.WARNING_MESSAGE)
                    continue

                myPopupInformationBox(toolbox_frame_, "NO CHANGES MADE!", "HACKER", JOptionPane.INFORMATION_MESSAGE)
                continue

            # OK, so we are changing or deleting
            if lChg or lDel:
                selectedKey = JOptionPane.showInputDialog(toolbox_frame_,
                                                          "Select the %s key/setting you want to %s" % (fileType,text),
                                                          "HACKER",
                                                          JOptionPane.WARNING_MESSAGE,
                                                          None,
                                                          prefs,
                                                          None)
                if not selectedKey: continue

                lOK_to_Change = False
                value = None
                if lConfigDict:
                    # value = moneydance_ui.getPreferences().getSetting(selectedKey)
                    value = st.get(selectedKey)   # Have to use the backdoor to maintain the real instance type

                if lLocalStorage:
                    value = LS.get(selectedKey)
                    valueTest = LS.getString(selectedKey, "")

                    try:
                        # Is it a StreamTable?
                        valueTest_st = StreamTable()
                        valueTest_st.readFrom(valueTest)
                        value = valueTest_st
                    except:
                        # Is it a StreamVector?
                        valueTest_sv = StreamVector()
                        try:
                            valueTest_sv.readFrom(valueTest)
                            value = valueTest_sv
                        except:
                            pass

                output =  "%s PLEASE REVIEW KEY & VALUE BEFORE MAKING CHANGES\n" %fileType
                output += "%s------------------------------------------------\n\n" %("-"*len(fileType))

                if isinstance(value,(StreamTable,StreamVector)) and lChg:
                    output += "\n@@ Sorry: StreamTable & StreamVector keys cannot be changed by this script (only deleted) @@\n"
                elif not isinstance(value, (str, unicode)) and lChg:
                    output += "\n@@ Sorry: %s keys cannot be changed by this script (only deleted) @@\n" % type(value)
                else:
                    lOK_to_Change = True
                    output += "\n@@ This '%s' key can be changed/deleted by this script @@\n" % selectedKey

                output += "\n%s %s\n" %(pad("%s KEY:"%fileType,25),selectedKey)
                output += "\n%s %s\n" %(pad("Type:",25), type(value))

                if isinstance(value,(StreamTable,StreamVector)):
                    output += "\n%s\n%s\n" %("Value:", value)
                else:
                    output += "\n%s %s\n" %(pad("Value:",25), value)

                output += "\n<END>"
                jif = QuickJFrame("REVIEW THE KEY BEFORE CHANGES to %s" %fileType, output).show_the_frame()

                if lChg and not lOK_to_Change:
                    myPopupInformationBox(jif,
                                          "SORRY: I cannot change the key %s in %s" %(selectedKey,fileType),
                                          "HACKER: CHANGE KEY IN %s" %fileType,
                                          JOptionPane.ERROR_MESSAGE)
                    continue

                chgValue = None

                if lChg:
                    chgValue = myPopupAskForInput(jif,
                                                  "HACKER: CHANGE KEY VALUE IN %s" %(fileType),
                                                  "KEY VALUE:",
                                                  "Carefully enter the new key value (STRINGS ONLY!):",
                                                  value,
                                                  False,
                                                  JOptionPane.WARNING_MESSAGE)

                    if not chgValue or len(chgValue.strip()) <1 or chgValue == value: continue
                    chgValue = chgValue.strip()

                    if not check_if_key_data_string_valid(chgValue):
                        myPopupInformationBox(jif,"ERROR: Key value %s is NOT valid!" %chgValue,"HACKER: CHANGE IN %s" %fileType,JOptionPane.ERROR_MESSAGE)
                        continue    # back to Hacker menu

                disclaimer = None
                if lDel:
                    disclaimer = myPopupAskForInput(jif,
                                                    "HACKER: %s KEY VALUE IN %s" %(text,fileType),
                                                    "DISCLAIMER:",
                                                    "Type 'IAGREE' to %s key: %s (with old value: %s)" %(text,selectedKey,value),
                                                    "NO",
                                                    False,
                                                    JOptionPane.ERROR_MESSAGE)
                if lChg:
                    disclaimer = myPopupAskForInput(jif,
                                                    "HACKER: %s KEY VALUE IN %s" %(text,fileType),
                                                    "DISCLAIMER:",
                                                    "Type 'IAGREE' to %s key: %s to new value: %s" %(text,selectedKey,chgValue),
                                                    "NO",
                                                    False,
                                                    JOptionPane.ERROR_MESSAGE)

                if disclaimer == "IAGREE":
                    if lConfigDict:
                        if lDel:
                            moneydance_ui.getPreferences().setSetting(selectedKey,None)
                        if lChg:
                            moneydance_ui.getPreferences().setSetting(selectedKey,chgValue)
                        moneydance.savePreferences()            # Flush all in memory settings to config.dict file on disk
                    if lLocalStorage:
                        if lDel:
                            LS.put(selectedKey,None)
                        if lChg:
                            LS.put(selectedKey,chgValue)
                        LS.save()                               # Flush local storage to safe/settings

                    play_the_money_sound()

                    if lDel:
                        myPrint("B","@@ HACKERMODE: key: %s DELETED from %s (old value: %s) @@" %(selectedKey,fileType,value))
                        myPopupInformationBox(jif,
                                              "SUCCESS: key: %s DELETED from %s (old value: %s)" %(selectedKey,fileType,value),
                                              "HACKER: DELETE IN %s" %fileType,
                                              JOptionPane.WARNING_MESSAGE)
                    if lChg:
                        myPrint("B","@@ HACKERMODE: key: %s CHANGED to %s in %s @@" %(selectedKey,chgValue, fileType))
                        myPopupInformationBox(jif,
                                              "SUCCESS: key: %s CHANGED to %s in %s" %(selectedKey,chgValue, fileType),
                                              "HACKER: CHANGE IN %s" %fileType,
                                              JOptionPane.WARNING_MESSAGE)
                    continue

                myPopupInformationBox(jif,"NO CHANGES MADE!", "HACKER", JOptionPane.INFORMATION_MESSAGE)
                continue

        # ENDWHILE

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

        return

    def hacker_mode_encrypt_file(statusLabel):
        global toolbox_frame_, debug, DARK_GREEN, lCopyAllToClipBoard_TB
        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        myPopupInformationBox(toolbox_frame_,"OK.. Please select a non-encrypted file. I will encrypt it and save it in the TMP directory of this current dataset (details will be in the console log)")

        LS = moneydance.getCurrentAccountBook().getLocalStorage()
        attachmentFullPath = os.path.join(moneydance_data.getRootFolder().getCanonicalPath())

        if Platform.isOSX():
            System.setProperty("com.apple.macos.use-file-dialog-packages", "false")  # Allow access to packages as directories
            System.setProperty("apple.awt.fileDialogForDirectories", "false")

        fileDialog = FileDialog(toolbox_frame_, "Select file to import (encrypt) and save in the LocalStorage TMP directory")
        fileDialog.setMultipleMode(False)
        fileDialog.setMode(FileDialog.LOAD)
        fileDialog.setDirectory(attachmentFullPath)
        fileDialog.setVisible(True)

        if Platform.isOSX():
            System.setProperty("com.apple.macos.use-file-dialog-packages","true")  # In theory prevents access to app file structure (but doesnt seem to work)
            System.setProperty("apple.awt.fileDialogForDirectories", "false")

        selectedFile = fileDialog.getFile()
        if (selectedFile is None) or selectedFile == "":
            statusLabel.setText(("No file selected to import/encrypt/save..!").ljust(800, " "))
            statusLabel.setForeground(Color.BLUE)
            fileDialog.dispose()
            del fileDialog
            return

        selectedFile = os.path.join(fileDialog.getDirectory(), fileDialog.getFile())
        fileDialog.dispose()
        del fileDialog

        if not os.path.exists(selectedFile) or not os.path.isfile(selectedFile):
            statusLabel.setText(("Sorry, file selected to import / encrypt either does not exist or is not a file").ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            return

        try:
            copyFileName = File(selectedFile).getName()
            tmpFile = "tmp" + os.path.sep + str(System.currentTimeMillis() % 10000L) +  "-" + copyFileName
            fis = FileInputStream(File(selectedFile))
            LS.writeFile(tmpFile, fis)
            fis.close()
            helper = moneydance.getPlatformHelper()
            helper.openDirectory(File(os.path.join(moneydance_data.getRootFolder().getCanonicalPath(), "safe","tmp")))
        except:
            myPrint("B", "HACKER MODE: SORRY - Failed to import (encrypt) file %s (view console error log)" %selectedFile)
            statusLabel.setText(("HACKER MODE: SORRY - Failed to import (encrypt) file %s (view console error log)" %selectedFile).ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            return

        myPrint("B","User requested to import (encrypt) file: %s into LocalStorage() TMP dir... SUCCESS!" %(selectedFile))

        statusLabel.setText(("HACKER MODE: File %s encrypted and saved in the TMP dir" %selectedFile).ljust(800, " "))
        statusLabel.setForeground(Color.BLUE)

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

        return

    def hacker_mode_decrypt_file(statusLabel):
        global toolbox_frame_, debug, DARK_GREEN, lCopyAllToClipBoard_TB
        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        myPopupInformationBox(toolbox_frame_,"OK.. Please select an internal MD encrypted file from within the 'safe'. I will decrypt it and save it in the TMP directory of this current dataset (details will be in the console log)")

        LS = moneydance.getCurrentAccountBook().getLocalStorage()
        attachmentFullPath = os.path.join(moneydance_data.getRootFolder().getCanonicalPath(), "safe")

        if Platform.isOSX():
            System.setProperty("com.apple.macos.use-file-dialog-packages", "false")  # Allow access to packages as directories
            System.setProperty("apple.awt.fileDialogForDirectories", "false")

        # Dumped FileDialog as it remembers the last directory - useless for this - we want this directory....!
        # fileDialog = FileDialog(toolbox_frame_, "Select file to extract and copy to TMP directory")
        # fileDialog.setMultipleMode(False)
        # fileDialog.setMode(FileDialog.LOAD)
        # fileDialog.setDirectory(attachmentFullPath)
        # fileDialog.setVisible(True)

        # UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName())
        encryptedFilename = JFileChooser(attachmentFullPath)
        encryptedFilename.setMultiSelectionEnabled(False)
        encryptedFilename.setFileSelectionMode(JFileChooser.FILES_ONLY)
        encryptedFilename.setDialogTitle("Select Moneydance internal file to extract and copy to TMP directory")
        # encryptedFilename.setPreferredSize(Dimension(800,800))
        returnvalue = encryptedFilename.showDialog(toolbox_frame_,"Extract")

        if Platform.isOSX():
            System.setProperty("com.apple.macos.use-file-dialog-packages","true")  # In theory prevents access to app file structure (but doesnt seem to work)
            System.setProperty("apple.awt.fileDialogForDirectories", "false")

        if (returnvalue != JFileChooser.APPROVE_OPTION
                or encryptedFilename.getSelectedFile() is None
                or encryptedFilename.getSelectedFile().getName() == ""):
            statusLabel.setText(("No file selected to extract/decrypt/copy..!").ljust(800, " "))
            statusLabel.setForeground(Color.BLUE)
            return

        selectedFile = encryptedFilename.getSelectedFile().getCanonicalPath()   # type: str

        if not os.path.exists(selectedFile) or not os.path.isfile(selectedFile):
            statusLabel.setText(("Sorry, file selected to extract either does not exist or is not a file").ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            return

        searchForSafe = selectedFile.lower().find(".moneydance"+os.path.sep+"safe"+os.path.sep)
        if searchForSafe <= 0:
            statusLabel.setText(("Sorry, file selected to extract must be within the MD Dataset 'safe'").ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            return

        truncatedPath = selectedFile[searchForSafe+len(".moneydance"+os.path.sep+"safe"+os.path.sep):]

        try:
            tmpDir = File(moneydance_data.getRootFolder(), "tmp")
            tmpDir.mkdirs()
            copyFileName = (File(selectedFile)).getName()
            tmpFile = File.createTempFile(str(System.currentTimeMillis() % 10000L), "-"+copyFileName, tmpDir)
            tmpFile.deleteOnExit()
            fout = FileOutputStream(tmpFile)
            LS.readFile(truncatedPath, fout)
            fout.close()
            helper = moneydance.getPlatformHelper()
            helper.openDirectory(tmpDir)
        except:
            myPrint("B", "HACKER MODE: SORRY - Failed to extract file %s (view console error log)" %selectedFile)
            statusLabel.setText(("HACKER MODE: SORRY - Failed to extract file %s (view console error log)" %selectedFile).ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            return

        myPrint("B","User requested to extract file: %s from LocalStorage()/safe and copy to TMP dir... SUCCESS!" %(selectedFile))

        statusLabel.setText(("HACKER MODE: File %s decrypted and copied to TMP dir" %selectedFile).ljust(800, " "))
        statusLabel.setForeground(Color.BLUE)

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

        return

    def hacker_mode_DEBUG(statusLabel, lForceON=False):
        global toolbox_frame_, debug, DARK_GREEN, lCopyAllToClipBoard_TB
        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        key = "moneydance.debug"
        md_debug = moneydance_ui.getMain().DEBUG
        props_debug = System.getProperty(key, None)

        toggleText = "ON"

        if not lForceON:
            if md_debug or (props_debug is not None and props_debug!="false"):
                toggleText = "OFF"

            ask = MyPopUpDialogBox(toolbox_frame_,"DEBUG STATUS:",
                                   "main.DEBUG                             currently set to: %s\n"
                                   'System.getProperty("%s") currently set to: %s\n'
                                   'OFXConnection.DEBUG_MESSAGES           currently set to: %s\n'
                                   'MoneybotURLStreamHandlerFactory.DEBUG  currently set to: %s\n'
                                   'OnlineTxnMerger.DEBUG                  currently set to: %s\n'
                                   'Syncer.DEBUG                           currently set to: %s\n'
                                   %(md_debug,key,props_debug,OFXConnection.DEBUG_MESSAGES,MoneybotURLStreamHandlerFactory.DEBUG,OnlineTxnMerger.DEBUG,Syncer.DEBUG),
                                   200,"TOGGLE MONEYDANCE INTERNAL DEBUG",
                                   lCancelButton=True,OKButtonText="SET ALL to %s" %toggleText)
            if not ask.go():
                statusLabel.setText(("HACKER MODE: NO CHANGES MADE TO DEBUG!").ljust(800, " "))
                statusLabel.setForeground(Color.BLUE)
                return

            myPrint("B","HACKER MODE: User requested to change all internal DEBUG modes to %s - setting these now...!" %(toggleText))

        if toggleText == "OFF":
            moneydance_ui.getMain().DEBUG = False
            System.clearProperty(key)
            OFXConnection.DEBUG_MESSAGES = False
            MoneybotURLStreamHandlerFactory.DEBUG = False
            OnlineTxnMerger.DEBUG = False
            Syncer.DEBUG = False
        else:
            moneydance_ui.getMain().DEBUG = True
            System.setProperty(key, "true")
            OFXConnection.DEBUG_MESSAGES = True
            MoneybotURLStreamHandlerFactory.DEBUG = True
            OnlineTxnMerger.DEBUG = True
            Syncer.DEBUG = True

        if lForceON:
            myPrint("DB","Moneydance Debug turned ON (same as launching Console window)......")
            return

        statusLabel.setText(("All Moneydance internal debug settings turned %s" %toggleText).ljust(800, " "))
        statusLabel.setForeground(Color.BLUE)
        myPopupInformationBox(toolbox_frame_,"All Moneydance internal debug settings turned %s" %toggleText,"TOGGLE MONEYDANCE INTERNAL DEBUG",JOptionPane.WARNING_MESSAGE)

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

        return

    def hacker_mode_other_DEBUG(statusLabel):
        global toolbox_frame_, debug, DARK_GREEN, lCopyAllToClipBoard_TB
        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        debugKeys = ["com.moneydance.apps.md.view.gui.txnreg.DownloadedTxnsView.DEBUG",
                     "com.moneydance.apps.md.view.gui.OnlineUpdateTxnsWindow.DEBUG"]

        selectedKey = JOptionPane.showInputDialog(toolbox_frame_,
                                                  "Select the DEBUG Setting you want to view/toggle",
                                                  "HACKER: OTHER DEBUG",
                                                  JOptionPane.INFORMATION_MESSAGE,
                                                  moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                  debugKeys,
                                                  None)

        if not selectedKey or debugKeys.index(selectedKey) > 1:
            statusLabel.setText(("No Debug key was selected to view/toggle..").ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            return

        currentSetting = False
        if debugKeys.index(selectedKey) == 0:
            currentSetting = DownloadedTxnsView.DEBUG
        elif debugKeys.index(selectedKey) == 1:
            currentSetting = OnlineUpdateTxnsWindow.DEBUG

        ask = MyPopUpDialogBox(toolbox_frame_,"OTHER DEBUG STATUS:",
                               "%s currently set to: %s" %(selectedKey, currentSetting),
                               200,"TOGGLE THIS MONEYDANCE INTERNAL OTHER DEBUG",
                               lCancelButton=True,OKButtonText="SET to %s" %(not currentSetting))
        if not ask.go():
            statusLabel.setText(("HACKER MODE: NO CHANGES MADE TO OTHER DEBUG!").ljust(800, " "))
            statusLabel.setForeground(Color.BLUE)
            return

        myPrint("B","HACKER MODE: User requested to change DEBUG %s to %s - setting now...!" %(selectedKey,not currentSetting))

        if debugKeys.index(selectedKey) == 0:
            DownloadedTxnsView.DEBUG = not currentSetting
        elif debugKeys.index(selectedKey) == 1:
            OnlineUpdateTxnsWindow.DEBUG = not currentSetting

        statusLabel.setText(("Moneydance internal debug settings %s turned %s" %(selectedKey, not currentSetting)).ljust(800, " "))
        statusLabel.setForeground(Color.BLUE)
        myPopupInformationBox(toolbox_frame_,"Moneydance internal debug settings %s turned %s" %(selectedKey, not currentSetting),"TOGGLE MONEYDANCE INTERNAL OTHER DEBUG",JOptionPane.WARNING_MESSAGE)

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

        return

    def convert_primary(statusLabel):
        global toolbox_frame_, debug

        # the reverse of convert_secondary_to_primary_data_set

        myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

        if not moneydance_ui.getCurrentAccounts().isMasterSyncNode():
            statusLabel.setText(("Your dataset is already Secondary - no changes made..").ljust(800, " "))
            statusLabel.setForeground(Color.RED)
            myPopupInformationBox(toolbox_frame_,"Your dataset is already Secondary - NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        if myPopupAskQuestion(toolbox_frame_,
                              "MAKE this PRIMARY a SECONDARY NODE",
                              "Are you sure you want to make this primary dataset a Secondary?",
                              JOptionPane.YES_NO_OPTION,
                              JOptionPane.ERROR_MESSAGE):

            disclaimer = myPopupAskForInput(toolbox_frame_,
                                            "MAKE this PRIMARY a SECONDARY NODE",
                                            "DISCLAIMER:",
                                            "Are you really sure you want to DEMOTE this primary into a Secondary ? Type 'IAGREE' to continue..",
                                            "NO",
                                            False,
                                            JOptionPane.ERROR_MESSAGE)

            if disclaimer == 'IAGREE':

                if not backup_local_storage_settings():
                    statusLabel.setText(("DEMOTE this PRIMARY to a SECONDARY NODE: ERROR making backup of LocalStorage() ./safe/settings - no changes made!").ljust(800, " "))
                    statusLabel.setForeground(Color.RED)
                    myPopupInformationBox(toolbox_frame_,"DEMOTE this PRIMARY to a SECONDARY NODE: ERROR making backup of LocalStorage() ./safe/settings - NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
                    return

                moneydance_ui.getCurrentAccounts().setIsMasterSyncNode( False )
                moneydance_data.getLocalStorage().save()        # Flush local storage to safe/settings

                play_the_money_sound()
                myPrint("B", "Dataset DEMOTED to a Secondary Node")
                statusLabel.setText(("I have DEMOTED your dataset to a secondary (non-Primary/Master) Node/Dataset - I RECOMMEND THAT YOU EXIT & RESTART!".ljust(800, " ")))
                statusLabel.setForeground(Color.RED)
                myPopupInformationBox(toolbox_frame_, "I have DEMOTED your dataset to a secondary (non-Primary/Master) Node/Dataset\nPLEASE EXIT & RESTART!", "PRIMARY DATASET", JOptionPane.WARNING_MESSAGE)
                return

        statusLabel.setText(("User did not say yes to Master Node DEMOTION - no changes made").ljust(800, " "))
        statusLabel.setForeground(Color.RED)
        myPopupInformationBox(toolbox_frame_,"User did not say yes to Master Node DEMOTION - NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)

        myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
        return


    def checkForREADONLY(statusLabel):

        checkDropbox = tell_me_if_dropbox_folder_exists()
        datasetPath = moneydance_data.getRootFolder().getCanonicalPath()

        if not os.access(datasetPath, os.W_OK) or (checkDropbox and not os.access(checkDropbox, os.W_OK)):
            myPrint("B", "@@@ ERROR: YOUR KEY FOLDERS ARE NOT WRITABLE! @@@")
            myPrint("B", "\n>> %s - Writable: %s\n"
                         ">> %s - Writable: %s\n"
                    %(checkDropbox, os.access(checkDropbox, os.W_OK), datasetPath, os.access(datasetPath, os.W_OK)))

            play_the_money_sound()
            MyPopUpDialogBox(toolbox_frame_,
                                   "ERROR: YOUR KEY FOLDERS ARE NOT WRITABLE! - YOU NEED TO EXIT MD AND FIX MANUALLY",
                                   "%s - Writable: %s\n"
                                   "%s - Writable: %s"
                                   %(checkDropbox, os.access(checkDropbox, os.W_OK), datasetPath, os.access(datasetPath, os.W_OK)),
                                   theTitle="FOLDER PROBLEM",
                                   OKButtonText="OK - I WILL EXIT",
                                   lAlertLevel=2).go()

            statusLabel.setText(("ERROR: YOUR KEY FOLDERS ARE NOT WRITABLE! - YOU NEED TO EXIT MD AND FIX MANUALLY").ljust(800, " "))
            statusLabel.setForeground(Color.RED)

        return

# END OF GLOBAL CLASSES and DEFs


    class DiagnosticDisplay():

        def __init__(self):
            self.myScrollPane = None

        class WindowListener(WindowAdapter):

            def __init__(self, theFrame):
                self.theFrame = theFrame        # type: MyJFrame

            def windowClosing(self, WindowEvent):                                                                       # noqa
                global debug

                myPrint("D","In ", inspect.currentframe().f_code.co_name, "()")

                myPrint("DB", "DiagnosticDisplay() Frame shutting down....")

                terminate_script()

            def windowClosed(self, WindowEvent):                                                                       # noqa
                global debug

                myPrint("D","In ", inspect.currentframe().f_code.co_name, "()")

                self.theFrame.isActiveInMoneydance = False

                if self.theFrame.MoneydanceAppListener is not None:
                    try:
                        moneydance.removeAppEventListener(self.theFrame.MoneydanceAppListener)
                        myPrint("DB","\n@@@ Removed my MD App Listener...\n")
                    except:
                        myPrint("B","FAILED to remove my MD App Listener...")
                        dump_sys_error_to_md_console_and_errorlog()

                myPrint("D","Exit ", inspect.currentframe().f_code.co_name, "()")


        class ReSizeListener(ComponentAdapter):

            def __init__(self, theFrame, thePanel, theScrollPane):
                self.theFrame = theFrame
                self.thePanel = thePanel
                self.theScrollPane = theScrollPane

            # def componentHidden(self, componentEvent):                                                                   # noqa
            #     pass
            #
            # def componentMoved(self, componentEvent):                                                                    # noqa
            #     pass
            #
            # def componentShown(self, componentEvent):                                                                    # noqa
            #     pass

            def componentResized(self, componentEvent):                                                                 # noqa
                global debug, toolbox_frame_

                myPrint("D","In ", inspect.currentframe().f_code.co_name, "()")

                if self.theFrame.getExtendedState() == JFrame.ICONIFIED:
                    myPrint("D","Frame state: ICONIFIED Size: %s" %(self.theFrame.getSize()))

                elif self.theFrame.getExtendedState() == JFrame.NORMAL:
                    # myPrint("D","Frame state: NORMAL Size: %s"  %(self.theFrame.getSize()))
                    pass
                else:
                    myPrint("D","Frame state: MAXIMISED %s - Size: %s" %(str(self.theFrame.getExtendedState()),self.theFrame.getSize()))
                    # MAXIMIZED_HORIZ
                    # MAXIMIZED_VERT
                    # MAXIMIZED_BOTH

                calcWidth = self.theFrame.getSize().width - 30

                # if Platform.isUnix() or Platform.isLinux:
                #     self.thePanel.setSize(Dimension(calcWidth, self.thePanel.getSize().height))
                #
                scrollPaneTop = self.theScrollPane.getY()
                calcHeight = (self.theFrame.getSize().height - scrollPaneTop - 70)

                self.theScrollPane.setSize(Dimension(calcWidth, calcHeight))

                self.theScrollPane.revalidate()
                self.theFrame.repaint()

                myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")


        class CloseAction(AbstractAction):

            def __init__(self, theFrame):
                self.theFrame = theFrame

            def actionPerformed(self, event):                                                                           # noqa
                global debug, toolbox_frame_
                myPrint("D","In ", inspect.currentframe().f_code.co_name, "()")

                myPrint("DB", "DiagnosticDisplay() Frame shutting down....")

                terminate_script()

                return

        class OnlineBankingToolsButtonAction(AbstractAction):

            def __init__(self, statusLabel):
                self.statusLabel = statusLabel

            def actionPerformed(self, event):
                global toolbox_frame_, debug
                global lAdvancedMode, lHackerMode

                # OFX BANKING MENU

                myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

                user_searchOFXData = JRadioButton("Search for stored OFX related data", False)
                user_searchOFXData.setToolTipText("This searches for Online Banking (OFX) related setup information in most places...")

                user_viewInstalledBankProfiles = JRadioButton("View your installed Bank / Service Profiles", False)
                user_viewInstalledBankProfiles.setToolTipText("This will display all the setup data stored on your service/banking logon profile(s)")

                user_viewListALLMDServices = JRadioButton("View list of MD's Bank dynamic setup profiles (then select one)", False)
                user_viewListALLMDServices.setToolTipText("This will display Moneydance's dynamic setup profiles for all banks - pulled from Infinite Kind's website..")

                user_viewOnlineTxnsPayeesPayments = JRadioButton("View your Online Txns/Payees/Payments", False)
                user_viewOnlineTxnsPayeesPayments.setToolTipText("This will show you your cached Online Txns (there should be none) and also your saved online payees and payments")

                user_toggleMDDebug = JRadioButton("Toggle Moneydance Debug (ONLY use for debugging)", False)
                user_toggleMDDebug.setToolTipText("This toggles Moneydance's internal DEBUG(s) on/off. When ON you get more messages in the Console Log (the same as opening console)")

                user_forgetOFXBankingLink = JRadioButton("Forget OFX Banking File Import Link (remove_ofx_account_bindings.py)", False)
                user_forgetOFXBankingLink.setToolTipText("This will tell Moneydance to forget the OFX Banking Import link attributed to an Account. Moneydance will ask you to recreate the link on next import.. THIS CHANGES DATA! (remove_ofx_account_bindings.py)")
                user_forgetOFXBankingLink.setEnabled(lAdvancedMode)
                user_forgetOFXBankingLink.setForeground(Color.RED)

                user_manageCUSIPLink = JRadioButton("Reset/Fix/Edit/Add CUSIP Banking Link (remove_ofx_security_bindings.py)", False)
                user_manageCUSIPLink.setToolTipText("Allows you to reset/add/edit/move your CUSIP banking link between security records. THIS CHANGES DATA! (remove_ofx_security_bindings.py)")
                user_manageCUSIPLink.setEnabled(lAdvancedMode)
                user_manageCUSIPLink.setForeground(Color.RED)

                user_updateOFXLastTxnUpdate = JRadioButton("Update the OFX Last Txn Update Date (Downloaded) field for an account", False)
                user_updateOFXLastTxnUpdate.setToolTipText("Allows you to edit the last download Txn date which is used to set the start date for Txn downloads - THIS CHANGES DATA!")
                user_updateOFXLastTxnUpdate.setEnabled(lAdvancedMode)
                user_updateOFXLastTxnUpdate.setForeground(Color.RED)

                user_deleteOFXBankingLogonProfile = JRadioButton("Delete OFX Banking Service / Logon Profile (remove_one_service.py)", False)
                user_deleteOFXBankingLogonProfile.setToolTipText("This will allow you to delete an Online Banking logon / service profile (service) from Moneydance. E.g. you will have to set this up again. THIS CHANGES DATA! (remove_one_service.py)")
                user_deleteOFXBankingLogonProfile.setEnabled(lAdvancedMode)
                user_deleteOFXBankingLogonProfile.setForeground(Color.RED)

                user_authenticationManagement = JRadioButton("OFX Authentication Management", False)
                user_authenticationManagement.setToolTipText("Brings up the sub menu. Allows you to clear your authentication cache (single or all) and edit user IDs. THIS CAN CHANGE DATA!")
                user_authenticationManagement.setEnabled(lAdvancedMode)
                user_authenticationManagement.setForeground(Color.RED)

                user_deleteOnlineTxns = JRadioButton("Delete Single cached OnlineTxnList Record/Txns", False)
                user_deleteOnlineTxns.setToolTipText("Allows you to surgically remove your cached Online Txn List txns - THESE SHOULD NOT BE HERE! THIS CHANGES DATA!")
                user_deleteOnlineTxns.setEnabled(lAdvancedMode)
                user_deleteOnlineTxns.setForeground(Color.RED)

                user_deleteALLOnlineTxns = JRadioButton("Delete ALL cached OnlineTxnList Record/Txns (delete_intermediate_downloaded_transaction_caches.py)", False)
                user_deleteALLOnlineTxns.setToolTipText("Purges/cleans any/all your cached Online Txn List records / txns - THERE SHOULD BE NONE! VERY SAFE TO RUN! THIS CHANGES DATA! (delete_intermediate_downloaded_transaction_caches.py)")
                user_deleteALLOnlineTxns.setEnabled(lAdvancedMode)
                user_deleteALLOnlineTxns.setForeground(Color.RED)

                user_cookieManagement = JRadioButton("OFX Cookie Management (Hacker Mode only)", False)
                user_cookieManagement.setToolTipText("Brings up the sub menu. Allows you to manage your OFX cookies - Advanced + Hacker Mode only. THIS CAN CHANGE DATA!")
                user_cookieManagement.setEnabled(lAdvancedMode and lHackerMode)
                user_cookieManagement.setForeground(Color.RED)

                labelFYI2 = JLabel("       ** to activate Exit, Select Toolbox Options, Advanced mode **")
                labelFYI2.setForeground(Color.RED)

                labelFYI3 = JLabel("       ** to activate Exit, Select Toolbox Options, both Advanced & Hacker modes **")
                labelFYI3.setForeground(Color.RED)

                userFilters = JPanel(GridLayout(0, 1))

                bg = ButtonGroup()
                bg.add(user_forgetOFXBankingLink)
                bg.add(user_deleteOFXBankingLogonProfile)
                bg.add(user_manageCUSIPLink)
                bg.add(user_searchOFXData)
                bg.add(user_viewInstalledBankProfiles)
                bg.add(user_viewOnlineTxnsPayeesPayments)
                bg.add(user_cookieManagement)
                bg.add(user_authenticationManagement)
                bg.add(user_deleteOnlineTxns)
                bg.add(user_deleteALLOnlineTxns)
                bg.add(user_updateOFXLastTxnUpdate)
                bg.add(user_viewListALLMDServices)
                # bg.add(user_toggleOFXDebug)
                bg.add(user_toggleMDDebug)
                bg.clearSelection()

                userFilters.add(JLabel(" "))
                userFilters.add(JLabel("---------- READONLY FUNCTIONS ----------"))
                userFilters.add(user_searchOFXData)
                userFilters.add(user_viewInstalledBankProfiles)
                userFilters.add(user_viewListALLMDServices)
                userFilters.add(user_viewOnlineTxnsPayeesPayments)
                userFilters.add(user_toggleMDDebug)
                # userFilters.add(user_toggleOFXDebug)
                userFilters.add(JLabel(" "))
                userFilters.add(JLabel("----------- UPDATE FUNCTIONS -----------"))
                if not lAdvancedMode:
                    userFilters.add(labelFYI2)
                userFilters.add(user_forgetOFXBankingLink)
                userFilters.add(user_manageCUSIPLink)
                userFilters.add(user_updateOFXLastTxnUpdate)
                userFilters.add(user_deleteOFXBankingLogonProfile)
                userFilters.add(user_authenticationManagement)
                userFilters.add(user_deleteOnlineTxns)
                userFilters.add(user_deleteALLOnlineTxns)
                userFilters.add(JLabel(" "))
                userFilters.add(JLabel("---- ADVANCED + HACKER MODE ONLY  -----"))
                if not lAdvancedMode or not lHackerMode:
                    userFilters.add(labelFYI3)
                userFilters.add(user_cookieManagement)


                while True:
                    options = ["EXIT", "PROCEED"]
                    userAction = (JOptionPane.showOptionDialog(toolbox_frame_,
                                                               userFilters,
                                                               "Online Banking (OFX) Tools",
                                                               JOptionPane.OK_CANCEL_OPTION,
                                                               JOptionPane.QUESTION_MESSAGE,
                                                               moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                               options, options[0]))
                    if userAction != 1:
                        self.statusLabel.setText(("Online Banking (OFX) Tools - No changes made.....").ljust(800, " "))
                        self.statusLabel.setForeground(Color.BLUE)
                        return

                    # for button in bg.getElements():
                    #     if button.isSelected(): break
                    #

                    if user_forgetOFXBankingLink.isSelected():
                        forgetOFXImportLink(self.statusLabel)

                    if user_deleteOFXBankingLogonProfile.isSelected():
                        deleteOFXService(self.statusLabel)

                    if user_manageCUSIPLink.isSelected():
                        CUSIPFix(self.statusLabel)

                    # if user_toggleOFXDebug.isSelected():
                    #     OFXDEBUGToggle(self.statusLabel)
                    #
                    if user_searchOFXData.isSelected():
                        viewer = GeekOutModeButtonAction(self.statusLabel, lOFX=True)
                        viewer.actionPerformed("")
                        del viewer
                        self.statusLabel.setText(("OFX: Your OFX Bank related settings have been searched and displayed....").ljust(800, " "))
                        self.statusLabel.setForeground(Color.BLUE)
                        return

                    if user_toggleMDDebug.isSelected():
                        hacker_mode_DEBUG(self.statusLabel)

                    if user_authenticationManagement.isSelected():
                        OFX_authentication_management(self.statusLabel)

                    if user_cookieManagement.isSelected():
                        OFX_cookie_management(self.statusLabel)

                    if user_viewListALLMDServices.isSelected():
                        download_md_fiscal_setup()
                        self.statusLabel.setText(("OFX: Moneydance's Dynamic Fiscal Institution Setup profiles have been retrieved and displayed....").ljust(800, " "))
                        self.statusLabel.setForeground(Color.BLUE)
                        return

                    if user_viewOnlineTxnsPayeesPayments.isSelected():
                        OFX_view_online_txns_payees_payments(self.statusLabel)
                        self.statusLabel.setText(("OFX: Your Online saved Txns, Payees, Payments have been retrieved and displayed....").ljust(800, " "))
                        self.statusLabel.setForeground(Color.BLUE)
                        return

                    if user_viewInstalledBankProfiles.isSelected():
                        get_ofx_related_data()
                        self.statusLabel.setText(("OFX: Your installed Service / Bank logon profiles have been displayed....").ljust(800, " "))
                        self.statusLabel.setForeground(Color.BLUE)
                        return

                    if user_deleteOnlineTxns.isSelected():
                        OFX_delete_saved_online_txns(self.statusLabel)

                    if user_deleteALLOnlineTxns.isSelected():
                        OFX_delete_ALL_saved_online_txns(self.statusLabel)
                        return

                    if user_updateOFXLastTxnUpdate.isSelected():
                        OFX_update_OFXLastTxnUpdate(self.statusLabel)

                    continue

                myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
                return

        class FixDropboxOneWaySyncButtonAction(AbstractAction):
            def __init__(self, statusLabel, myButton):
                self.statusLabel = statusLabel
                self.myButton = myButton

            def actionPerformed(self, event):
                global toolbox_frame_, debug, DARK_GREEN, lCopyAllToClipBoard_TB
                myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

                # fix_dropbox_one_way_syncing.py
                # reset_sync_and_dropbox_settings.py
                theKey = "migrated.netsync.dropbox.fileid"

                if not confirm_backup_confirm_disclaimer(toolbox_frame_,self.statusLabel,"FIX DROPBOX ONE WAY SYNC","Fix Dropbox One-Way Syncing?"):
                    return

                myPrint("B","FIX DROPBOX ONE WAY SYNC: Removing key '%s' from LocalStorage() at user request...." %(theKey))

                LS = moneydance_ui.getCurrentAccounts().getBook().getLocalStorage()
                LS.remove(theKey)
                LS.save()

                moneydance_data.saveTrunkFile()
                play_the_money_sound()

                self.myButton.setVisible(False)
                self.myButton.setEnabled(False)

                self.statusLabel.setText("'FIX DROPBOX ONE WAY SYNC' - OK, I have executed reset Dropbox One-Way Sync. I suggest a restart of MD".ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                myPopupInformationBox(toolbox_frame_,"OK, I have executed reset Dropbox One-Way Sync. I suggest a restart of MD","FIX DROPBOX ONE WAY SYNC",JOptionPane.WARNING_MESSAGE)

                myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

                return

        class MakeDropBoxSyncFolder(AbstractAction):

            def __init__(self, statusLabel, myButton):
                self.statusLabel = statusLabel
                self.myButton = myButton

            def actionPerformed(self, event):
                global toolbox_frame_, debug
                myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

                if check_for_dropbox_folder():
                    self.statusLabel.setText("Sorry - Fix: Create .moneydancesync folder button not available!?".ljust(800, " "))
                    self.statusLabel.setForeground(Color.RED)
                    myPrint("B","MakeDropBoxSyncFolder() called, but check_for_dropbox_folder() returned True - so we should not be here? FIX NOT AVAILABLE")
                    myPopupInformationBox(toolbox_frame_,"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
                    return

                if not myPopupAskQuestion(toolbox_frame_,
                                          "DROPBOX",
                                          "Create missing Dropbox .moneydancesync folder?",
                                          JOptionPane.YES_NO_OPTION,
                                          JOptionPane.ERROR_MESSAGE):

                    self.statusLabel.setText("User declined to create missing Dropbox .moneydancesync folder ".ljust(800, " "))
                    self.statusLabel.setForeground(Color.RED)
                    myPopupInformationBox(toolbox_frame_,"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
                    return

                self.myButton.setVisible(False)
                self.myButton.setEnabled(False)

                userHomeProperty = System.getProperty("UserHome", System.getProperty("user.home", "."))
                baseFolder = File(userHomeProperty, "Dropbox")

                try:
                    if File(baseFolder, ".moneydancesync").mkdir():
                        self.statusLabel.setText(("Created Dropbox .moneydancesync folder").ljust(800, " "))
                        self.statusLabel.setForeground(Color.BLUE)
                        myPrint("B", "Created .moneydancesync folder in dropbox")
                        myPopupInformationBox(toolbox_frame_, ".moneydancesync folder created!", "DROPBOX", JOptionPane.WARNING_MESSAGE)
                        return

                except:
                    dump_sys_error_to_md_console_and_errorlog()

                myPrint("B", "Error creating Dropbox .moneydancesync folder!?")
                self.statusLabel.setText(("Error creating Dropbox .moneydancesync folder!?").ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                myPopupInformationBox(toolbox_frame_, "Error creating Dropbox .moneydancesync folder!?", "DROPBOX", JOptionPane.ERROR_MESSAGE)

                myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
                return

        class FindDatasetButtonAction(AbstractAction):

            def __init__(self, statusLabel):
                self.statusLabel = statusLabel

            def actionPerformed(self, event):
                global toolbox_frame_, debug, i_am_an_extension_so_run_headless

                myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )


                if not myPopupAskQuestion(toolbox_frame_,
                                          "SEARCH COMPUTER FOR MONEYDANCE DATASET(s)/BACKUP(s)",
                                          "This may be time consuming...Do you want to continue with search?",
                                          JOptionPane.YES_NO_OPTION,
                                          JOptionPane.WARNING_MESSAGE):


                    self.statusLabel.setText(("User Aborted Dataset search...").ljust(800, " "))
                    self.statusLabel.setForeground(Color.RED)
                    return

                whatType = ["Datasets",
                             "Backups"]


                selectedWhat = JOptionPane.showInputDialog(toolbox_frame_,
                                                            "WHAT TYPE OF DATASET?",
                                                            "Choose Datasets or Backups",
                                                           JOptionPane.INFORMATION_MESSAGE,
                                                           moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                           whatType,
                                                           None)
                if selectedWhat is None:
                    self.statusLabel.setText("No Dataset Type was selected - aborting..".ljust(800, " "))
                    self.statusLabel.setForeground(Color.RED)
                    return

                if whatType.index(selectedWhat) == 0:
                    lBackup=False
                    theExtension = "*.moneydance".lower()
                elif whatType.index(selectedWhat) == 1:
                    lBackup=True
                    theExtension = "*.moneydancearchive".lower()
                else:
                    self.statusLabel.setText("Dataset Type Error - aborting..".ljust(800, " "))
                    self.statusLabel.setForeground(Color.RED)
                    return

                myPrint("DB", "Dataset type: %s" %theExtension)

                if Platform.isWindows():
                    theRoot = os.path.join("C:"+os.path.sep)
                else:
                    theRoot = os.path.sep

                lRootExclusions = False

                whereFrom = ["From UserDir: %s" %get_home_dir(),
                              "From Root: %s (excluding some system locations and other volumes)" %theRoot,
                              "From Root: %s (nothing excluded - might take a long time / never finish)" %theRoot,
                              "Select your own start point"]

                selectedStart = JOptionPane.showInputDialog(toolbox_frame_,
                                                            "Select the Search start folder",
                                                            "WHERE TO SEARCH FROM",
                                                            JOptionPane.INFORMATION_MESSAGE,
                                                            moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                            whereFrom,
                                                            None)
                if selectedStart is None:
                    self.statusLabel.setText("No start point was selected - aborting..".ljust(800, " "))
                    self.statusLabel.setForeground(Color.RED)
                    return

                if whereFrom.index(selectedStart) == 3:
                    if Platform.isOSX():
                        System.setProperty("com.apple.macos.use-file-dialog-packages", "true")  # In theory prevents access to app file structure (but doesnt seem to work)
                        System.setProperty("apple.awt.fileDialogForDirectories", "true")

                        fDialog = FileDialog(toolbox_frame_, "Select location to start %s Dataset Search (CANCEL=ABORT)" % theExtension)
                        fDialog.setMultipleMode(False)
                        fDialog.setMode(FileDialog.LOAD)
                        fDialog.setDirectory(get_home_dir())

                        fDialog.setVisible(True)

                        System.setProperty("com.apple.macos.use-file-dialog-packages","true")  # In theory prevents access to app file structure (but doesnt seem to work)
                        System.setProperty("apple.awt.fileDialogForDirectories", "false")

                        if (fDialog.getDirectory() is None) or str(fDialog.getDirectory()) == "" or \
                                (fDialog.getFile() is None) or str(fDialog.getFile()) == "":
                            self.statusLabel.setText(("User did not select Search Directory... Aborting").ljust(800, " "))
                            self.statusLabel.setForeground(Color.RED)
                            fDialog.dispose()
                            del fDialog
                            return
                        # noinspection PyTypeChecker
                        theDir = os.path.join(fDialog.getDirectory(),str(fDialog.getFile()))
                        fDialog.dispose()
                        del fDialog

                    else:
                        # UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName())
                        # Switch to JFileChooser for Folder selection on Windows/Linux - to allow folder selection
                        fileChooser = JFileChooser( get_home_dir() )

                        fileChooser.setMultiSelectionEnabled( False )

                        fileChooser.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY)

                        fileChooser.setDialogTitle("Select location to start %s Dataset Search (CANCEL=ABORT)"%theExtension)
                        fileChooser.setPreferredSize(Dimension(700, 700))
                        returnValue = fileChooser.showDialog(toolbox_frame_, "START SEARCH")

                        if returnValue == JFileChooser.CANCEL_OPTION:
                            self.statusLabel.setText("No start point was selected - aborting..".ljust(800, " "))
                            self.statusLabel.setForeground(Color.RED)
                            return
                        elif fileChooser.getSelectedFile() is None or fileChooser.getSelectedFile().getName()=="":
                            self.statusLabel.setText("No start point was selected - aborting..".ljust(800, " "))
                            self.statusLabel.setForeground(Color.RED)
                            return
                        else:
                            theDir = fileChooser.getSelectedFile().getAbsolutePath()

                elif whereFrom.index(selectedStart) == 2:  # From ROOT with no exclusions
                    theDir = theRoot
                elif whereFrom.index(selectedStart) == 1:  # From ROOT with exclusions
                    lRootExclusions = True
                    theDir = theRoot
                elif whereFrom.index(selectedStart) == 0:  # From User Home Dir
                    theDir = get_home_dir()
                else:
                    self.statusLabel.setText(("Error Selecting Search Directory... Aborting").ljust(800, " "))
                    self.statusLabel.setForeground(Color.RED)
                    return

                diag = MyPopUpDialogBox(toolbox_frame_,"Please wait: searching..",theTitle="SEARCH", theWidth=100, lModal=False,OKButtonText="WAIT")
                diag.go()

                save_list_of_found_files=[]

                myPrint("B","DATASET Search >> Searching from Directory: %s" %theDir)

                def findDataset(pattern, path):
                    global debug

                    iFound=0                                                                                            # noqa
                    result = []
                    dotCounter = 0
                    thingsSearched = 0

                    lContinueToEnd=False

                    if not i_am_an_extension_so_run_headless:
                        print "Searching for your %s Datasets (might be time consuming):."%theExtension,

                    exclude_these_dirs = []

                    if lRootExclusions:
                        if Platform.isOSX():
                            exclude_these_dirs = ["/System", "/Library"]
                        elif Platform.isUnix():
                            exclude_these_dirs = ["/media", "/boot", "/cdrom", "/sys", "/proc", "/dev", "/mnt"]
                        myPrint("B","Root exclusions requested... These are: %s" %(exclude_these_dirs))

                    start_time = time.time()
                    timeOutCheckBackMinutes = 10.0
                    timeOutSeconds = 10

                    class MyTimerTask(TimerTask):

                        def __init__(self, dlg, theTimer):
                            self.dlg = dlg
                            self.theTimer = theTimer

                        def run(self):
                            global debug
                            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()")

                            myPrint("D","Timer task triggered - closing the JOption Pane....")
                            self.dlg.setVisible(False)
                            self.theTimer.cancel()

                            myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
                            return

                    class MyJOptionPaneListener(ComponentAdapter):

                        def __init__(self, timeout, dlg):
                            self.timeout = timeout
                            self.dlg = dlg
                            self.t = None

                        def componentShown(self, e):
                            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", e)
                            super(MyJOptionPaneListener, self).componentShown(e)                                        # noqa
                            myPrint("D","Toolbox setting up Timer Task for Search function to kill Search dialog...")
                            self.t = Timer()
                            self.t.schedule(MyTimerTask(self.dlg,self.t), self.timeout)
                            myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

                        def componentHidden(self, e):
                            myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", e)
                            super(MyJOptionPaneListener, self).componentHidden(e)                                        # noqa
                            myPrint("D","Killing Timer Task for Search function as dialog closed...")
                            self.t.cancel()
                            myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")

                    # showOptionDialog(Component parentComponent, Object message, String title, int optionType, int messageType, Icon icon, Object[] options, Object initialValue)
                    def showConfirmDialogWithTimeout(theFrame, theMessage, theTitle, theOptionType, theMessageType, theIcon, theChoices, theInitialValue, timeout_ms, timeoutChoice):
                        msg = JOptionPane(theMessage, theMessageType, theOptionType, theIcon, theChoices, theInitialValue)
                        dlg = msg.createDialog(theFrame, theTitle)
                        dlg.setAlwaysOnTop(True)
                        dlg.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE)
                        theListener = MyJOptionPaneListener( timeout_ms, dlg )
                        dlg.addComponentListener( theListener )
                        dlg.setVisible(True)
                        selectedValue = msg.getValue()
                        dlg.removeComponentListener( theListener )
                        del theListener
                        if selectedValue is None or selectedValue < 0:
                            return -1
                        try:
                            return theChoices.index(selectedValue)
                        except:
                            pass    # Probably "uninitializedValue"

                        return theChoices.index(timeoutChoice)

                    options=["STOP HERE","SEARCH TO END", "KEEP ASKING"]

                    for root, dirs, files in os.walk(path, topdown=True):

                        if debug: myPrint("DB","Searching: %s" %(root))

                        if dotCounter % 1000 <1:
                            if not i_am_an_extension_so_run_headless: print ".",

                        if (not dotCounter
                                or (dotCounter % 10000 <1 and not lContinueToEnd)
                                or (time.time() - start_time > (timeOutCheckBackMinutes*60))):

                            start_time = time.time()

                            # ####
                            response = showConfirmDialogWithTimeout(toolbox_frame_,
                                                                    "Are you OK to continue (so far..: %s found / %s files/searched)?" %(iFound, thingsSearched),
                                                                    "SEARCH COMPUTER FOR MONEYDANCE DATASET(s)",
                                                                    JOptionPane.YES_NO_OPTION,
                                                                    JOptionPane.QUESTION_MESSAGE,
                                                                    None,
                                                                    options,
                                                                    options[2],
                                                                    timeOutSeconds * 1000,
                                                                    options[2])

                            # response = JOptionPane.showOptionDialog(toolbox_frame_,
                            #                                          "Are you OK to continue (so far..: %s found / %s files/searched)?" %(iFound, thingsSearched),
                            #                                          "SEARCH COMPUTER FOR MONEYDANCE DATASET(s)",
                            #                                          JOptionPane.YES_NO_OPTION,
                            #                                          JOptionPane.QUESTION_MESSAGE,
                            #                                          None,
                            #                                          options,
                            #                                          options[2])

                            if response < 1:
                                self.statusLabel.setText(("User Aborted Dataset search...").ljust(800, " "))
                                self.statusLabel.setForeground(Color.RED)
                                myPrint("B", "@@ Dataset search was abandoned by user.......")
                                return result, iFound
                            elif response == 1:
                                lContinueToEnd = True
                            elif response == 2:
                                pass

                        dotCounter+=1

                        # Remove /System dir etc on Mac/Linux....
                        if lRootExclusions:
                            for d in list(dirs):
                                for ex in exclude_these_dirs:
                                    if (root+d).startswith(ex):
                                        dirs.remove(d)

                        if lBackup:

                            for name in files:
                                fp = os.path.join(root,name)
                                if os.path.islink(fp):
                                    myPrint("DB", "found file link! %s - will skip" %fp)
                                    continue

                                thingsSearched+=1
                                if fnmatch.fnmatch(name, pattern):
                                    iFound+=1
                                    result.append("File >> Sz: %sMB Mod: %s Name: %s "
                                                  %(rpad(round(os.path.getsize(os.path.join(root, name))/(1000.0*1000.0),1),6),
                                                    pad(datetime.datetime.fromtimestamp(os.path.getmtime(fp)).strftime('%Y-%m-%d %H:%M:%S'),11),
                                                    os.path.join(root, name)))
                        for name in dirs:
                            fp = os.path.join(root,name)
                            if os.path.islink(fp):
                                myPrint("DB", "found dir link! %s - will skip" %fp)
                                continue

                            thingsSearched+=1
                            if fnmatch.fnmatch(name, pattern):
                                if name != ".moneydance":
                                    save_list_of_found_files.append(fp)
                                    iFound+=1
                                result.append("Dir >> Modified: %s %s"
                                              %(pad(datetime.datetime.fromtimestamp(os.path.getmtime(fp)).strftime('%Y-%m-%d %H:%M:%S'),11),
                                              os.path.join(root, name)))
                    return result, iFound

                fileList, iFound = findDataset(theExtension, theDir)

                diag.kill()

                print
                myPrint("B","Completed search for %s datafiles: %s found" %(theExtension,iFound))

                niceFileList="\n SEARCH FOR MONEYDANCE (%s) DATASETS\n" %(theExtension)
                niceFileList+="Search started from Directory: %s\n\n" %(theDir)

                if lRootExclusions:
                    niceFileList+="(NOTE: Root search exclusions of other volumes and some system locations were requested too)\n\n"

                if not iFound:
                    niceFileList+="\n<NONE FOUND>\n"

                for x in fileList:
                    myPrint("B","Found: %s" %x)
                    niceFileList+=x+"\n"

                self.statusLabel.setText(("Find my %s datasets(s) found %s possible files/directories" %(theExtension,iFound)).ljust(800, " "))
                self.statusLabel.setForeground(DARK_GREEN)

                jif=QuickJFrame("LIST OF MONEYDANCE %s DATASETS FOUND" % theExtension, niceFileList, lAlertLevel=1).show_the_frame()

                myPopupInformationBox(jif, "%s %s Datasets located...." %(iFound,theExtension), "DATASET SEARCH", JOptionPane.INFORMATION_MESSAGE)

                if not lBackup:
                    add_to_ext_list=[]
                    internalDir = Common.getDocumentsDirectory().getCanonicalPath()

                    externalFiles = AccountBookUtil.getExternalAccountBooks()
                    externalFiles_asList = []
                    for ext in externalFiles:
                        externalFiles_asList.append(ext.getBook().getRootFolder().getCanonicalPath())

                    for filename in save_list_of_found_files:
                        if not os.path.exists(filename):
                            continue
                        if internalDir in filename:
                            continue
                        if filename in externalFiles_asList:
                            continue
                        add_to_ext_list.append(filename)

                    myPrint("DB","Found %s external files that can be added to config.dict: %s" %(len(add_to_ext_list),add_to_ext_list))

                    if (len(add_to_ext_list) > 0
                            and myPopupAskQuestion(jif, "SEARCH FOR DATASETS", "%s of these datasets are not showing in your File/Open menu list(and config.dict)? WOULD YOU LIKE TO ADD ANY OF THEM?" %(len(add_to_ext_list))) ):

                        backup_config_dict(True)

                        iAdded = 0
                        externalFilesVector = moneydance_ui.getPreferences().getVectorSetting("external_files", StreamVector())
                        for add_this_file in add_to_ext_list:
                            if not myPopupAskQuestion(jif,"ADD FILE TO FILE/OPEN MENU","ADD: %s?" %((add_this_file))):
                                continue
                            iAdded+=1
                            myPrint("B","SEARCH FOR DATASETS - %s added to config.dict and file/open menu" %(add_this_file))
                            externalFilesVector.add(add_this_file)
                            moneydance_ui.getPreferences().setSetting("external_files", externalFilesVector)

                        if iAdded:
                            moneydance.savePreferences()
                            myPopupInformationBox(jif, "SEARCH FOR DATASETS - %s files added to config.dict and file/open menu (RESTART MD REQUIRED)" %(iAdded), "DATASET SEARCH", JOptionPane.INFORMATION_MESSAGE)

                myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
                return

        class AccountsCategoriesMenuButtonAction(AbstractAction):

            def __init__(self, statusLabel):
                self.statusLabel = statusLabel

            def actionPerformed(self, event):
                global toolbox_frame_, debug
                global lAdvancedMode, lHackerMode, fixRCurrencyCheck

                myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

                user_view_check_number_settings = JRadioButton("View Check Number Settings", False)
                user_view_check_number_settings.setToolTipText("View the Check Number settings that will display in the Transaction Register")

                user_force_change_accounts_currency = JRadioButton("FIX: FORCE Change an Account's Currency (force_change_account_currency.py)", False)
                user_force_change_accounts_currency.setToolTipText("This allows you to FORCE change an Account's currency - USE WITH CARE!.. THIS CHANGES DATA! (force_change_account_currency.py)")
                user_force_change_accounts_currency.setEnabled(lAdvancedMode)
                user_force_change_accounts_currency.setForeground(Color.RED)

                user_force_change_all_accounts_currency = JRadioButton("FIX: FORCE Change ALL Account's Currencies (force_change_all_currencies.py)", False)
                user_force_change_all_accounts_currency.setToolTipText("This allows you to FORCE change ALL Account's Currencies - USE WITH CARE!.. THIS CHANGES DATA! (force_change_all_currencies.py)")
                user_force_change_all_accounts_currency.setEnabled(lAdvancedMode)
                user_force_change_all_accounts_currency.setForeground(Color.RED)

                user_force_change_an_accounts_type = JRadioButton("FIX: FORCE Change an Account's Type (set_account_type.py)", False)
                user_force_change_an_accounts_type.setToolTipText("This allows you to FORCE change an Account's Type - USE WITH CARE!.. THIS CHANGES DATA! (set_account_type.py)")
                user_force_change_an_accounts_type.setEnabled(lAdvancedMode)
                user_force_change_an_accounts_type.setForeground(Color.RED)

                user_view_zero_bal_cats = JRadioButton("DIAG: Categories and Balances Report", False)
                user_view_zero_bal_cats.setToolTipText("This will list all your Categories and show which have Zero Balances - USE ADVANCED MODE TO MAKE THESE INACTIVE")

                user_inactivate_zero_bal_cats = JRadioButton("FIX: Make Zero Balance Categories Inactive", False)
                user_inactivate_zero_bal_cats.setToolTipText("This will allow you Inactivate all Categories with Zero Balances (you will see the report first). THIS CHANGES DATA!")
                user_inactivate_zero_bal_cats.setEnabled(lAdvancedMode)
                user_inactivate_zero_bal_cats.setForeground(Color.RED)

                user_fix_accounts_parent = JRadioButton("FIX: Account's Invalid Parent Account (fix_account_parent.py)", False)
                user_fix_accounts_parent.setToolTipText("This will diagnose your Parent Accounts and fix if invalid. THIS CHANGES DATA! (fix_account_parent.py)")
                user_fix_accounts_parent.setEnabled(lAdvancedMode)
                user_fix_accounts_parent.setForeground(Color.RED)

                bookName = moneydance.getCurrentAccountBook().getName().strip()
                root = moneydance.getCurrentAccountBook().getRootAccount()
                rootName = root.getAccountName().strip()
                user_fix_root_account_name = JRadioButton("FIX: Correct Root Account Name (Only enabled if the name is incorrect)", False)
                user_fix_root_account_name.setToolTipText("This allows you to change the (nearly) hidden Master/Parent Account Name in Moneydance (referred to as ROOT) to match the name of your Dataset (referred to as BOOK). THIS CHANGES DATA!")
                user_fix_root_account_name.setEnabled(lAdvancedMode and (rootName != bookName))
                user_fix_root_account_name.setForeground(Color.RED)

                labelFYI2 = JLabel("       ** to activate Exit, Select Toolbox Options, Advanced mode **")
                labelFYI2.setForeground(Color.RED)

                userFilters = JPanel(GridLayout(0, 1))

                bg = ButtonGroup()
                bg.add(user_view_check_number_settings)
                bg.add(user_view_zero_bal_cats)
                bg.add(user_inactivate_zero_bal_cats)
                bg.add(user_force_change_an_accounts_type)
                bg.add(user_force_change_accounts_currency)
                bg.add(user_force_change_all_accounts_currency)
                bg.add(user_fix_accounts_parent)
                bg.add(user_fix_root_account_name)
                bg.clearSelection()

                userFilters.add(JLabel(" "))
                userFilters.add(JLabel("---------- READONLY FUNCTIONS ----------"))
                userFilters.add(user_view_check_number_settings)
                userFilters.add(user_view_zero_bal_cats)
                userFilters.add(JLabel(" "))
                userFilters.add(JLabel("----------- UPDATE FUNCTIONS -----------"))

                if not lAdvancedMode:
                    userFilters.add(labelFYI2)

                userFilters.add(user_inactivate_zero_bal_cats)
                userFilters.add(user_force_change_an_accounts_type)
                userFilters.add(user_force_change_accounts_currency)
                userFilters.add(user_force_change_all_accounts_currency)
                userFilters.add(user_fix_accounts_parent)
                userFilters.add(user_fix_root_account_name)

                while True:

                    bookName = moneydance.getCurrentAccountBook().getName().strip()
                    root = moneydance.getCurrentAccountBook().getRootAccount()
                    rootName = root.getAccountName().strip()
                    user_fix_root_account_name.setEnabled(lAdvancedMode and (rootName != bookName))
                    bg.clearSelection()

                    options = ["EXIT", "PROCEED"]
                    userAction = (JOptionPane.showOptionDialog(toolbox_frame_,
                                                               userFilters,
                                                               "Accounts / Categories Diagnostics, Tools, Fixes",
                                                               JOptionPane.OK_CANCEL_OPTION,
                                                               JOptionPane.QUESTION_MESSAGE,
                                                               moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                               options, options[0]))
                    if userAction != 1:
                        return

                    if user_view_check_number_settings.isSelected():
                        x = ViewFileButtonAction(self.statusLabel, "view_check_num_settings()", "Check Number Settings etc", lFile=False)
                        x.actionPerformed(None)
                        return

                    if user_view_zero_bal_cats.isSelected():
                        zero_bal_categories(self.statusLabel, False)
                        return

                    if user_inactivate_zero_bal_cats.isSelected():
                        zero_bal_categories(self.statusLabel, True)
                        return

                    if user_force_change_an_accounts_type.isSelected():
                        force_change_account_type(self.statusLabel)

                    if user_force_change_accounts_currency.isSelected():
                        force_change_account_currency(self.statusLabel)

                    if user_force_change_all_accounts_currency.isSelected():
                        force_change_all_accounts_currencies(self.statusLabel)

                    if user_fix_accounts_parent.isSelected():
                        fix_account_parent(self.statusLabel)
                        return

                    if user_fix_root_account_name.isSelected():
                        fix_root_account_name(self.statusLabel)

                    continue

                myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
                return

        class CurrencySecurityMenuButtonAction(AbstractAction):

            def __init__(self, statusLabel):
                self.statusLabel = statusLabel

            def actionPerformed(self, event):
                global toolbox_frame_, debug
                global lAdvancedMode, lHackerMode, fixRCurrencyCheck

                myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

                user_show_open_share_lots = JRadioButton("DIAG: Show Open Share LOTS (unconsumed) (show_open_tax_lots.py)", False)
                user_show_open_share_lots.setToolTipText("This will list all Stocks/Shares with Open/Unconsumed LOTS (when LOT Control ON) - READONLY (show_open_tax_lots.py)")

                user_convert_stock_lot_FIFO = JRadioButton("FIX: Convert Stock to LOT controlled with FIFO lot matching (MakeFifoCost.py)", False)
                user_convert_stock_lot_FIFO.setToolTipText("Convert Average Cost Controlled Stock to LOT Controlled and Allocate LOTs using FiFo method - THIS CHANGES DATA! (MakeFifoCost.py)")
                user_convert_stock_lot_FIFO.setEnabled(lAdvancedMode)
                user_convert_stock_lot_FIFO.setForeground(Color.RED)

                user_convert_stock_avg_cst_control = JRadioButton("FIX: Convert Stock to Average Cost Control", False)
                user_convert_stock_avg_cst_control.setToolTipText("Convert LOT Controlled Stock to Average Cost Control (and wipe any LOT records) - THIS CHANGES DATA!")
                user_convert_stock_avg_cst_control.setEnabled(lAdvancedMode)
                user_convert_stock_avg_cst_control.setForeground(Color.RED)

                user_thin_price_history = JRadioButton("FIX: Thin/Purge Price History (price_history_thinner.py)", False)
                user_thin_price_history.setToolTipText("This will allow you to Thin / Prune your Price History based on user parameters. THIS CHANGES DATA! (price_history_thinner.py)")
                user_thin_price_history.setEnabled(lAdvancedMode)
                user_thin_price_history.setForeground(Color.RED)

                user_can_i_delete_security = JRadioButton("DIAG: Can I Delete a Security?", False)
                user_can_i_delete_security.setToolTipText("This will tell you whether a Selected Security is in use and whether you can delete it in Moneydance")

                user_list_curr_sec_dpc = JRadioButton("DIAG: List Security / Currency decimal place settings", False)
                user_list_curr_sec_dpc.setToolTipText("This will list your Security and Currency hidden decimal place settings (and attempt to advise of setup errors)")

                user_diag_curr_sec = JRadioButton("DIAG: Diagnose your Currencies (& securities) (reset_relative_currencies.py)", False)
                user_diag_curr_sec.setToolTipText("This will diagnose your Currency (& Security) setup - checking relative currencies (and advise if you need to run a fix) (reset_relative_currencies.py)")

                user_fix_curr_sec = JRadioButton("FIX: Fix Relative Currencies (& securities) (reset_relative_currencies.py) - MUST RUN DIAGNOSE ABOVE FIRST", False)
                user_fix_curr_sec.setToolTipText("This will apply fixes to your Currency (& security) / Relative Currency setup (use after running the diagnose option first). THIS CHANGES DATA!  (reset_relative_currencies.py)")
                user_fix_curr_sec.setEnabled(lAdvancedMode and fixRCurrencyCheck is not None and fixRCurrencyCheck>1)
                user_fix_curr_sec.setForeground(Color.RED)

                user_fix_invalid_curr_sec = JRadioButton("FIX: Fix Invalid Relative Currency (& security) Rates (fix_invalid_currency_rates.py)", False)
                user_fix_invalid_curr_sec.setToolTipText("This will reset any relative rates back to 1.0 where < 0 or > 9999999999. THIS CHANGES DATA!  (fix_invalid_currency_rates.py)")
                user_fix_invalid_curr_sec.setEnabled(lAdvancedMode)
                user_fix_invalid_curr_sec.setForeground(Color.RED)

                user_force_change_accounts_currency = JRadioButton("FIX: FORCE Change an Account's Currency (force_change_account_currency.py)", False)
                user_force_change_accounts_currency.setToolTipText("This allows you to FORCE change an Account's currency - USE WITH CARE!.. THIS CHANGES DATA! (force_change_account_currency.py)")
                user_force_change_accounts_currency.setEnabled(lAdvancedMode)
                user_force_change_accounts_currency.setForeground(Color.RED)

                user_force_change_all_accounts_currency = JRadioButton("FIX: FORCE Change ALL Account's Currencies (force_change_all_currencies.py)", False)
                user_force_change_all_accounts_currency.setToolTipText("This allows you to FORCE change ALL Account's Currencies - USE WITH CARE!.. THIS CHANGES DATA! (force_change_all_currencies.py)")
                user_force_change_all_accounts_currency.setEnabled(lAdvancedMode)
                user_force_change_all_accounts_currency.setForeground(Color.RED)

                labelFYI2 = JLabel("       ** to activate Exit, Select Toolbox Options, Advanced mode **")
                labelFYI2.setForeground(Color.RED)

                userFilters = JPanel(GridLayout(0, 1))

                bg = ButtonGroup()
                bg.add(user_show_open_share_lots)
                bg.add(user_convert_stock_lot_FIFO)
                bg.add(user_convert_stock_avg_cst_control)
                bg.add(user_thin_price_history)
                bg.add(user_can_i_delete_security)
                bg.add(user_list_curr_sec_dpc)
                bg.add(user_diag_curr_sec)
                bg.add(user_fix_curr_sec)
                bg.add(user_fix_invalid_curr_sec)
                bg.add(user_force_change_accounts_currency)
                bg.add(user_force_change_all_accounts_currency)
                bg.clearSelection()

                userFilters.add(JLabel(" "))
                userFilters.add(JLabel("---------- READONLY FUNCTIONS ----------"))
                userFilters.add(user_can_i_delete_security)
                userFilters.add(user_list_curr_sec_dpc)
                userFilters.add(user_show_open_share_lots)
                userFilters.add(user_diag_curr_sec)
                userFilters.add(JLabel(" "))
                userFilters.add(JLabel("----------- UPDATE FUNCTIONS -----------"))

                if not lAdvancedMode:
                    userFilters.add(labelFYI2)

                userFilters.add(user_fix_curr_sec)
                userFilters.add(user_convert_stock_lot_FIFO)
                userFilters.add(user_convert_stock_avg_cst_control)
                userFilters.add(user_thin_price_history)
                userFilters.add(user_fix_invalid_curr_sec)
                userFilters.add(user_force_change_accounts_currency)
                userFilters.add(user_force_change_all_accounts_currency)

                while True:

                    user_fix_curr_sec.setEnabled(lAdvancedMode and fixRCurrencyCheck is not None and fixRCurrencyCheck>1)
                    bg.clearSelection()

                    options = ["EXIT", "PROCEED"]
                    userAction = (JOptionPane.showOptionDialog(toolbox_frame_,
                                                               userFilters,
                                                               "Currency / Security Diagnostics, Tools, Fixes",
                                                               JOptionPane.OK_CANCEL_OPTION,
                                                               JOptionPane.QUESTION_MESSAGE,
                                                               moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                               options, options[0]))
                    if userAction != 1:
                        return

                    if user_can_i_delete_security.isSelected():
                        x = ViewFileButtonAction(self.statusLabel, "can_I_delete_security()", "CAN I DELETE A SECURITY?", lFile=False)
                        x.actionPerformed(None)
                        return

                    if user_list_curr_sec_dpc.isSelected():
                        x=ViewFileButtonAction(self.statusLabel, "list_security_currency_decimal_places()", "LIST SECURITY CURRENCY DECIMAL PLACES", lFile=False)
                        x.actionPerformed(None)
                        return

                    if user_diag_curr_sec.isSelected():
                        x=ViewFileButtonAction(self.statusLabel, "diagnose_currencies(False)", "DIAGNOSE CURRENCIES (LOOK FOR ERRORS)", lFile=False)
                        x.actionPerformed(None)
                        return

                    if user_fix_curr_sec.isSelected():
                        x=ViewFileButtonAction(self.statusLabel, "diagnose_currencies(True)", "FIX RELATIVE CURRENCIES (FIX ERRORS)", lFile=False)
                        x.actionPerformed(None)
                        return

                    if user_fix_invalid_curr_sec.isSelected():
                        fix_invalid_relative_currency_rates(self.statusLabel)
                        return

                    if user_thin_price_history.isSelected():
                        thin_price_history(self.statusLabel)
                        return

                    if user_show_open_share_lots.isSelected():
                        show_open_share_lots(self.statusLabel)
                        return

                    if user_convert_stock_lot_FIFO.isSelected():
                        convert_stock_lot_FIFO(self.statusLabel)
                        return

                    if user_convert_stock_avg_cst_control.isSelected():
                        convert_stock_avg_cst_control(self.statusLabel)
                        return

                    if user_force_change_accounts_currency.isSelected():
                        force_change_account_currency(self.statusLabel)

                    if user_force_change_all_accounts_currency.isSelected():
                        force_change_all_accounts_currencies(self.statusLabel)

                    continue

                myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
                return

        class TransactionMenuButtonAction(AbstractAction):

            def __init__(self, statusLabel):
                self.statusLabel = statusLabel

            def actionPerformed(self, event):
                global toolbox_frame_, debug
                global lAdvancedMode, lHackerMode, fixRCurrencyCheck

                myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

                user_view_txn_sort = JRadioButton("View Register Transactional Sort Orders", False)
                user_view_txn_sort.setToolTipText("Allows you  to view the current transaction register sort orders in operation")

                user_extract_attachments = JRadioButton("Extract Attachments to Folder", False)
                user_extract_attachments.setToolTipText("Extract all your attachments to a folder of your choosing...")

                user_diagnose_attachments = JRadioButton("DIAG: Diagnose Attachments and detect Orphans too", False)
                user_diagnose_attachments.setToolTipText("This will analise your Attachments, show you the file storage consumed, and detect Orphans/issues")

                user_fix_non_hier_sec_acct_txns = JRadioButton("FIX: Non-Hierarchical Security Acct Txns (fix_non-hierarchical_security_account_txns.py)", False)
                user_fix_non_hier_sec_acct_txns.setToolTipText("This reviews your Investment Security Txns and fixes where the Account reference is cross-linked and incorrect (fix_non-hierarchical_security_account_txns.py & fix_investment_txns_to_wrong_security.py)")
                user_fix_non_hier_sec_acct_txns.setEnabled(lAdvancedMode)
                user_fix_non_hier_sec_acct_txns.setForeground(Color.RED)

                user_fix_delete_one_sided_txns = JRadioButton("FIX: Delete One-Sided Transactions (delete_invalid_txns.py)", False)
                user_fix_delete_one_sided_txns.setToolTipText("This allows you to DELETE 'invalid' one-sided transactions - usually from a bad quicken import. THIS CHANGES DATA! (delete_invalid_txns.py)")
                user_fix_delete_one_sided_txns.setEnabled(lAdvancedMode)
                user_fix_delete_one_sided_txns.setForeground(Color.RED)

                user_reverse_txn_amounts = JRadioButton("FIX: Reverse Transaction Amounts (reverse_txn_amounts.py)", False)
                user_reverse_txn_amounts.setToolTipText("This allows you to REVERSE the transaction values/amounts for an account within a date range. THIS CHANGES DATA! (reverse_txn_amounts.py)")
                user_reverse_txn_amounts.setEnabled(lAdvancedMode)
                user_reverse_txn_amounts.setForeground(Color.RED)

                user_reverse_txn_exchange_rates_by_account_and_date = JRadioButton("FIX: Reverse Transaction Exchange Rates (reverse_txn_exchange_rates_by_account_and_date)", False)
                user_reverse_txn_exchange_rates_by_account_and_date.setToolTipText("This allows you to REVERSE the transactional exchange rates for an account within a date range. THIS CHANGES DATA! (reverse_txn_exchange_rates_by_account_and_date)")
                user_reverse_txn_exchange_rates_by_account_and_date.setEnabled(lAdvancedMode)
                user_reverse_txn_exchange_rates_by_account_and_date.setForeground(Color.RED)

                labelFYI2 = JLabel("       ** to activate Exit, Select Toolbox Options, Advanced mode **")
                labelFYI2.setForeground(Color.RED)

                userFilters = JPanel(GridLayout(0, 1))

                bg = ButtonGroup()
                bg.add(user_view_txn_sort)
                bg.add(user_extract_attachments)
                bg.add(user_diagnose_attachments)
                bg.add(user_fix_non_hier_sec_acct_txns)
                bg.add(user_fix_delete_one_sided_txns)
                bg.add(user_reverse_txn_amounts)
                bg.add(user_reverse_txn_exchange_rates_by_account_and_date)
                bg.clearSelection()

                userFilters.add(JLabel(" "))
                userFilters.add(JLabel("---------- READONLY FUNCTIONS ----------"))
                userFilters.add(user_view_txn_sort)
                userFilters.add(user_extract_attachments)
                userFilters.add(user_diagnose_attachments)
                userFilters.add(JLabel(" "))
                userFilters.add(JLabel("----------- UPDATE FUNCTIONS -----------"))

                if not lAdvancedMode:
                    userFilters.add(labelFYI2)

                userFilters.add(user_fix_non_hier_sec_acct_txns)
                userFilters.add(user_fix_delete_one_sided_txns)
                userFilters.add(user_reverse_txn_amounts)
                userFilters.add(user_reverse_txn_exchange_rates_by_account_and_date)

                while True:

                    options = ["EXIT", "PROCEED"]
                    userAction = (JOptionPane.showOptionDialog(toolbox_frame_,
                                                               userFilters,
                                                               "Transaction(s) Diagnostics, Tools, Fixes",
                                                               JOptionPane.OK_CANCEL_OPTION,
                                                               JOptionPane.QUESTION_MESSAGE,
                                                               moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                               options, options[0]))
                    if userAction != 1:
                        return

                    if user_view_txn_sort.isSelected():
                        x = ViewFileButtonAction(self.statusLabel, "get_register_txn_sort_orders()", "Register TXN Sort Orders etc", lFile=False)
                        x.actionPerformed(None)
                        return

                    if user_extract_attachments.isSelected():
                        extract_attachments(self.statusLabel)
                        return

                    if user_diagnose_attachments.isSelected():
                        diagnose_attachments(self.statusLabel)
                        return

                    if user_fix_non_hier_sec_acct_txns.isSelected():
                        fix_non_hier_sec_acct_txns(self.statusLabel)
                        return

                    if user_fix_delete_one_sided_txns.isSelected():
                        fix_delete_one_sided_txns(self.statusLabel)
                        return

                    if user_reverse_txn_amounts.isSelected():
                        reverse_txn_amounts(self.statusLabel)
                        return

                    if user_reverse_txn_exchange_rates_by_account_and_date.isSelected():
                        reverse_txn_exchange_rates_by_account_and_date(self.statusLabel)
                        return

                    continue

                myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
                return

        class GeneralToolsMenuButtonAction(AbstractAction):

            def __init__(self, statusLabel):
                self.statusLabel = statusLabel

            def actionPerformed(self, event):
                global toolbox_frame_, debug
                global lAdvancedMode, lHackerMode, fixRCurrencyCheck

                myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

                user_display_passwords = JRadioButton("Display Dataset Password/Hint and Sync Passphrase", False)
                user_display_passwords.setToolTipText("Display the password/hint used to open your Encrypted Dataset, and also your Sync passphrase (if set)")

                user_view_MD_config_file = JRadioButton("View MD Config File", False)
                user_view_MD_config_file.setToolTipText("View the contents of your Moneydance configuration file")

                user_view_MD_custom_theme_file = JRadioButton("View MD Custom Theme File", False)
                user_view_MD_custom_theme_file.setToolTipText("View the contents of your Moneydance custom Theme file (if you have set one up)")
                user_view_MD_custom_theme_file.setEnabled(os.path.exists(theme.Theme.customThemeFile.getAbsolutePath()))    # noqa

                grabProgramDir = find_the_program_install_dir()
                user_view_java_vmoptions = JRadioButton("View Java VM Options File", False)
                user_view_java_vmoptions.setToolTipText("View the contents of the Java VM Options runtime file that Moneydance uses")
                user_view_java_vmoptions.setEnabled(grabProgramDir and os.path.exists(os.path.join(grabProgramDir,"Moneydance.vmoptions")))

                user_view_extensions_details = JRadioButton("View Extension(s) details", False)
                user_view_extensions_details.setToolTipText("View details about the Extensions installed in your Moneydance system")

                user_view_memorised_reports = JRadioButton("View Memorised Reports", False)
                user_view_memorised_reports.setToolTipText("View a list of your Memorised reports")

                user_find_sync_password_in_ios_backups = JRadioButton("Find Sync Password in iOS Backups (only on Windows and Mac)", False)
                user_find_sync_password_in_ios_backups.setToolTipText("This search for iOS backup(s) and look for your Sync Encryption password(s)")
                user_find_sync_password_in_ios_backups.setEnabled(Platform.isOSX() or Platform.isWindows())

                user_import_QIF = JRadioButton("'Older' Import QIF file and set parameters", False)
                user_import_QIF.setToolTipText("Runs the 'older' MD importQIFIntoAccount() function and allows you to set parameters (you can select create Account Structure Only) - WILL IMPORT / CHANGE DATA!")

                user_change_moneydance_fonts = JRadioButton("Set/Change Default Moneydance FONTS", False)
                user_change_moneydance_fonts.setToolTipText("This will allow you to Set/Change the Default Moneydance Fonts. THIS CHANGES DATA!")
                user_change_moneydance_fonts.setEnabled(lAdvancedMode and float(moneydance.getBuild()) >= 3030)
                user_change_moneydance_fonts.setForeground(Color.RED)

                user_delete_custom_theme_file = JRadioButton("Delete Custom Theme file", False)
                user_delete_custom_theme_file.setToolTipText("Delete your custom Theme file (if it exists). This is pretty safe. MD will create a new one if you select in Preferences. THIS DELETES A FILE!")
                user_delete_custom_theme_file.setEnabled(lAdvancedMode and os.path.exists(theme.Theme.customThemeFile.getAbsolutePath()))   # noqa
                user_delete_custom_theme_file.setForeground(Color.RED)

                user_delete_orphan_extensions = JRadioButton("FIX: Delete Orphaned Extensions", False)
                user_delete_orphan_extensions.setToolTipText("This will delete any references to orphaned / outdated Extensions (config.dict & .mxt files). THIS CHANGES DATA!")
                user_delete_orphan_extensions.setEnabled(lAdvancedMode)
                user_delete_orphan_extensions.setForeground(Color.RED)

                user_reset_window_display_settings = JRadioButton("RESET Window Display Settings", False)
                user_reset_window_display_settings.setToolTipText("This tells MD to 'forget' window display settings. CLOSE ALL REGISTER WINDOWS FIRST! The beauty is it keeps all other settings intact! THIS CHANGES DATA!")
                user_reset_window_display_settings.setEnabled(lAdvancedMode)
                user_reset_window_display_settings.setForeground(Color.RED)

                labelFYI2 = JLabel("       ** to activate Exit, Select Toolbox Options, Advanced mode **")
                labelFYI2.setForeground(Color.RED)

                userFilters = JPanel(GridLayout(0, 1))

                bg = ButtonGroup()
                bg.add(user_display_passwords)
                bg.add(user_view_MD_config_file)
                bg.add(user_view_MD_custom_theme_file)
                bg.add(user_view_java_vmoptions)
                bg.add(user_view_extensions_details)
                bg.add(user_view_memorised_reports)
                bg.add(user_find_sync_password_in_ios_backups)
                bg.add(user_import_QIF)
                bg.add(user_change_moneydance_fonts)
                bg.add(user_delete_custom_theme_file)
                bg.add(user_delete_orphan_extensions)
                bg.add(user_reset_window_display_settings)
                bg.clearSelection()

                userFilters.add(JLabel(" "))
                userFilters.add(JLabel("---------- READONLY FUNCTIONS ----------"))
                userFilters.add(user_display_passwords)
                userFilters.add(user_view_MD_config_file)
                userFilters.add(user_view_MD_custom_theme_file)
                userFilters.add(user_view_java_vmoptions)
                userFilters.add(user_view_extensions_details)
                userFilters.add(user_view_memorised_reports)
                userFilters.add(user_find_sync_password_in_ios_backups)
                userFilters.add(user_import_QIF)
                userFilters.add(JLabel(" "))
                userFilters.add(JLabel("----------- UPDATE FUNCTIONS -----------"))

                if not lAdvancedMode:
                    userFilters.add(labelFYI2)

                userFilters.add(user_change_moneydance_fonts)
                userFilters.add(user_delete_custom_theme_file)
                userFilters.add(user_delete_orphan_extensions)
                userFilters.add(user_reset_window_display_settings)

                while True:

                    grabProgramDir = find_the_program_install_dir()
                    user_view_java_vmoptions.setEnabled(grabProgramDir and os.path.exists(os.path.join(grabProgramDir,"Moneydance.vmoptions")))
                    user_view_MD_custom_theme_file.setEnabled(os.path.exists(theme.Theme.customThemeFile.getAbsolutePath()))                    # noqa
                    user_delete_custom_theme_file.setEnabled(lAdvancedMode and os.path.exists(theme.Theme.customThemeFile.getAbsolutePath()))   # noqa
                    bg.clearSelection()

                    options = ["EXIT", "PROCEED"]
                    userAction = (JOptionPane.showOptionDialog(toolbox_frame_,
                                                               userFilters,
                                                               "General Diagnostics, Tools, Fixes",
                                                               JOptionPane.OK_CANCEL_OPTION,
                                                               JOptionPane.QUESTION_MESSAGE,
                                                               moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                               options, options[0]))
                    if userAction != 1:
                        return

                    if user_display_passwords.isSelected():
                        display_passwords(self.statusLabel)

                    if user_view_MD_config_file.isSelected():
                        x = ViewFileButtonAction(self.statusLabel, Common.getPreferencesFile(), "MD Config")
                        x.actionPerformed(None)
                        return

                    if user_view_MD_custom_theme_file.isSelected():
                        x = ViewFileButtonAction(self.statusLabel, theme.Theme.customThemeFile, "MD Custom Theme")          # noqa
                        x.actionPerformed(None)
                        return

                    if user_view_java_vmoptions.isSelected():
                        x = ViewFileButtonAction(self.statusLabel, File(grabProgramDir, "Moneydance.vmoptions"), "Java VM File")
                        x.actionPerformed(None)
                        return

                    if user_view_extensions_details.isSelected():
                        x = ViewFileButtonAction(self.statusLabel, "view_extensions_details()", "Extension(s) details etc", lFile=False)
                        x.actionPerformed(None)
                        return

                    if user_view_memorised_reports.isSelected():
                        x = ViewFileButtonAction(self.statusLabel, "get_list_memorised_reports()", "Memorized Reports and Graphs", lFile=False)
                        x.actionPerformed(None)
                        return

                    if user_find_sync_password_in_ios_backups.isSelected():
                        find_IOS_sync_data(self.statusLabel)
                        return

                    if user_import_QIF.isSelected():
                        import_QIF(self.statusLabel)

                    if user_change_moneydance_fonts.isSelected():
                        change_fonts(self.statusLabel)

                    if user_delete_custom_theme_file.isSelected():
                        delete_theme_file(self.statusLabel)

                    if user_delete_orphan_extensions.isSelected():
                        force_remove_extension(self.statusLabel)
                        return

                    if user_reset_window_display_settings.isSelected():
                        reset_window_positions(self.statusLabel)
                        return

                    continue

                myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
                return

        class HackerMenuButtonAction(AbstractAction):

            def __init__(self, statusLabel):
                self.statusLabel = statusLabel

            def actionPerformed(self, event):
                global toolbox_frame_, debug
                global lAdvancedMode, lHackerMode, fixRCurrencyCheck

                myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

                if not lHackerMode: return

                user_hacker_mode_edit_prefs = JRadioButton("HACK: ADD/CHG/DEL System Settings/Prefs (ie config.dict / LocalStorage() settings", False)
                user_hacker_mode_edit_prefs.setToolTipText("This allows you to HACK (add/change/delete) config.dict and LocalStorage() (./safe/settings) keys..... CAN UPDATE DATA")
                user_hacker_mode_edit_prefs.setForeground(Color.RED)

                user_hacker_edit_param_keys = JRadioButton("HACK: ADD/CHG/DEL Database Object (ie Account, Currency, any object)", False)
                user_hacker_edit_param_keys.setToolTipText("This allows you to HACK (add/change/delete) an Object's Parameter keys..... CAN UPDATE DATA - ONLY USE IF YOU KNOW WHAT YOU ARE DOING")
                user_hacker_edit_param_keys.setForeground(Color.RED)

                user_hacker_delete_int_ext_files = JRadioButton("HACK: DELETE Files from Filelist and DISK", False)
                user_hacker_delete_int_ext_files.setToolTipText("This allows you to delete internal/external filenames from the list of File>Open files settings>> AND ASKS IF YOU WANT TO DELETE THE FILES TOO..... UPDATES CONFIG.DICT/CAN DELETE FILES")
                user_hacker_delete_int_ext_files.setForeground(Color.RED)

                user_hacker_toggle_DEBUG = JRadioButton("HACK: Toggle Moneydance DEBUG", False)
                user_hacker_toggle_DEBUG.setToolTipText("This will toggle Moneydance's internal DEBUG setting(s) ON/OFF.....")
                user_hacker_toggle_DEBUG.setForeground(Color.RED)

                user_hacker_toggle_other_DEBUGs = JRadioButton("HACK: Toggle Other Moneydance DEBUGs", False)
                user_hacker_toggle_other_DEBUGs.setToolTipText("This will allow you to toggle other known Moneydance internal DEBUG setting(s) ON/OFF..... (these add extra messages to Console output))")
                user_hacker_toggle_other_DEBUGs.setForeground(Color.RED)

                user_hacker_extract_from_storage = JRadioButton("HACK: Extract a File from LocalStorage", False)
                user_hacker_extract_from_storage.setToolTipText("This allows you to select & extract (decrypt) a file from inside LocalStorage (copied to TMP dir)..... FILE SELF DESTRUCTS AFTER RESTART")
                user_hacker_extract_from_storage.setForeground(Color.RED)

                user_hacker_import_to_storage = JRadioButton("HACK: Import a File back into LocalStorage", False)
                user_hacker_import_to_storage.setToolTipText("This allows you to select & import (encrypt) a file back into LocalStorage/safe/tmp dir.....")
                user_hacker_import_to_storage.setForeground(Color.RED)

                user_hacker_save_trunk = JRadioButton("HACK: Save Trunk File", False)
                user_hacker_save_trunk.setToolTipText("This allows you to call the Save Trunk File function)..... UPDATES YOUR DATASET")
                user_hacker_save_trunk.setForeground(Color.RED)

                user_convert_to_primary = JRadioButton("HACK: DEMOTE Primary dataset back to a Secondary Node", False)
                user_convert_to_primary.setToolTipText("This allows you to DEMOTE your Primary Sync Node/Dataset back to a Secondary Node)..... UPDATES YOUR DATASET")
                user_convert_to_primary.setEnabled(moneydance_ui.getCurrentAccounts().isMasterSyncNode())
                user_convert_to_primary.setForeground(Color.RED)

                lDropbox, lSuppressed = check_dropbox_and_suppress_warnings()
                user_hacker_suppress_dropbox_warning = JRadioButton("HACK: Suppress File in Dropbox Warning", False)
                user_hacker_suppress_dropbox_warning.setToolTipText("This allows you to suppress the 'Your file seems to be in a shared folder (Dropbox)' warning")
                user_hacker_suppress_dropbox_warning.setEnabled(lDropbox and not lSuppressed)
                user_hacker_suppress_dropbox_warning.setForeground(Color.RED)

                userFilters = JPanel(GridLayout(0, 1))

                bg = ButtonGroup()
                bg.add(user_hacker_toggle_DEBUG)
                bg.add(user_hacker_toggle_other_DEBUGs)
                bg.add(user_hacker_extract_from_storage)
                bg.add(user_hacker_import_to_storage)
                bg.add(user_hacker_mode_edit_prefs)
                bg.add(user_hacker_edit_param_keys)
                bg.add(user_hacker_delete_int_ext_files)
                bg.add(user_hacker_save_trunk)
                bg.add(user_convert_to_primary)
                bg.add(user_hacker_suppress_dropbox_warning)
                bg.clearSelection()

                userFilters.add(JLabel(" "))
                userFilters.add(JLabel("--- READONLY / NON-UPDATE FUNCTIONS ---"))
                userFilters.add(user_hacker_toggle_DEBUG)
                userFilters.add(user_hacker_toggle_other_DEBUGs)
                userFilters.add(user_hacker_extract_from_storage)
                userFilters.add(JLabel(" "))
                userFilters.add(JLabel("----------- UPDATE FUNCTIONS -----------"))
                userFilters.add(user_hacker_import_to_storage)
                userFilters.add(user_hacker_mode_edit_prefs)
                userFilters.add(user_hacker_edit_param_keys)
                userFilters.add(user_hacker_delete_int_ext_files)
                userFilters.add(user_hacker_save_trunk)
                userFilters.add(user_convert_to_primary)
                userFilters.add(user_hacker_suppress_dropbox_warning)

                while True:

                    lDropbox, lSuppressed = check_dropbox_and_suppress_warnings()
                    user_hacker_suppress_dropbox_warning.setEnabled(lDropbox and not lSuppressed)
                    user_convert_to_primary.setEnabled(moneydance_ui.getCurrentAccounts().isMasterSyncNode())
                    bg.clearSelection()

                    options = ["EXIT", "PROCEED"]
                    userAction = (JOptionPane.showOptionDialog(toolbox_frame_,
                                                               userFilters,
                                                               "HACKER - Diagnostics, Tools, Fixes",
                                                               JOptionPane.OK_CANCEL_OPTION,
                                                               JOptionPane.QUESTION_MESSAGE,
                                                               moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                               options, options[0]))
                    if userAction != 1:
                        return


                    if user_hacker_toggle_DEBUG.isSelected():
                        hacker_mode_DEBUG(self.statusLabel)

                    if user_hacker_toggle_other_DEBUGs.isSelected():
                        hacker_mode_other_DEBUG(self.statusLabel)

                    if user_hacker_extract_from_storage.isSelected():
                        hacker_mode_decrypt_file(self.statusLabel)

                    if user_hacker_import_to_storage.isSelected():
                        hacker_mode_encrypt_file(self.statusLabel)

                    if user_hacker_mode_edit_prefs.isSelected():
                        hacker_mode(self.statusLabel)
                        return

                    if user_hacker_edit_param_keys.isSelected():
                        hacker_mode_edit_parameter_keys(self.statusLabel)
                        return

                    if user_hacker_delete_int_ext_files.isSelected():
                        hacker_remove_int_external_files_settings(self.statusLabel)
                        return

                    if user_hacker_save_trunk.isSelected():
                        hacker_mode_save_trunk_file(self.statusLabel)

                    if user_convert_to_primary.isSelected():
                        convert_primary(self.statusLabel)

                    if user_hacker_suppress_dropbox_warning.isSelected():
                        hacker_mode_suppress_dropbox_warning(self.statusLabel)

                    continue

                myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
                return

        class ConvertSecondaryButtonAction(AbstractAction):
            theString = ""

            def __init__(self, theString, statusLabel):
                self.theString = theString
                self.statusLabel = statusLabel

            def actionPerformed(self, event):
                global toolbox_frame_, debug

                # convert_secondary_to_primary_data_set

                myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

                if moneydance_data.getLocalStorage().getBoolean("_is_master_node", True):
                    self.statusLabel.setText(("Your dataset is already Master - no changes made..").ljust(800, " "))
                    self.statusLabel.setForeground(Color.RED)
                    myPopupInformationBox(toolbox_frame_,"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
                    return

                if myPopupAskQuestion(toolbox_frame_,
                                      "MAKE this SECONDARY a PRIMARY/MASTER NODE",
                                      "Are you sure you want to make this secondary dataset the Primary?",
                                      JOptionPane.YES_NO_OPTION,
                                      JOptionPane.ERROR_MESSAGE):

                    disclaimer = myPopupAskForInput(toolbox_frame_,
                                                    "MAKE this SECONDARY a PRIMARY/MASTER NODE",
                                                    "DISCLAIMER:",
                                                    "Are you really sure you want to change this secondary into the Primary? Type 'IAGREE' to continue..",
                                                    "NO",
                                                    False,
                                                    JOptionPane.ERROR_MESSAGE)

                    if disclaimer == 'IAGREE':

                        if not backup_local_storage_settings():
                            self.statusLabel.setText(("MAKE ME PRIMARY: ERROR making backup of LocalStorage() ./safe/settings - no changes made!").ljust(800, " "))
                            self.statusLabel.setForeground(Color.RED)
                            myPopupInformationBox(toolbox_frame_,"NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)
                            return

                        moneydance_data.getLocalStorage().put("_is_master_node", True)
                        moneydance_data.getLocalStorage().save()        # Flush local storage to safe/settings

                        play_the_money_sound()
                        myPrint("B", "Dataset promoted to a Master Node")
                        self.statusLabel.setText(("I have promoted your dataset to a Primary/Master Node/Dataset - I RECOMMEND THAT YOU EXIT & RESTART!".ljust(800, " ")))
                        self.statusLabel.setForeground(Color.RED)
                        myPopupInformationBox(toolbox_frame_, "THIS IS NOW A PRIMARY / MASTER DATASET\nPLEASE EXIT & RESTART!", "PRIMARY DATASET", JOptionPane.WARNING_MESSAGE)
                        return

                self.statusLabel.setText(("User did not say yes to Master Node promotion - no changes made").ljust(800, " "))
                self.statusLabel.setForeground(Color.RED)
                myPopupInformationBox(toolbox_frame_,"User did not say yes to Master Node promotion - NO CHANGES MADE!",theMessageType=JOptionPane.WARNING_MESSAGE)

                myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
                return

        class AnalyseDatasetSizeButtonAction(AbstractAction):
            def __init__(self, statusLabel):
                self.statusLabel = statusLabel

            def actionPerformed(self, event):
                global toolbox_frame_, debug

                # show_object_type_quantities.py

                myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

                output = "DATASET FILE ANALYSIS\n" \
                         " ====================\n\n"

                startDir=moneydance_data.getRootFolder().getCanonicalPath()
                output += "Dataset path: %s\n\n" %(startDir)

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
                # safe_tmpSize = 0
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

                output+=("Dataset size:               %sMB\n" %(rpad(round((total_size/(1000.0*1000.0)),1),12)))
                output+=("- settings file size:       %sKB\n" %(rpad(round((safe_settingsSize/(1000.0)),1),12)))
                output+=("- key file size:            %sKB\n" %(rpad(round((keySize/   (1000.0)),1),12)))
                output+=("- tiksync folder size:      %sMB (with %s files)\n" %(rpad(round((safe_tiksyncSize/(1000.0*1000.0)),1),12),countTIKfiles))
                output+=("  (note trunk file size:    %sMB)\n" %(rpad(round((safe_trunkSize/(1000.0*1000.0)),1),12)))

                if sync_outCount:
                    output+=("  (WAITING Sync 'Out' size: %sMB with %s files)\n" %(rpad(round((sync_outSize/(1000.0*1000.0)),1),12),sync_outCount))

                output+=("- attachments size:         %sMB (in %s attachments)\n" %(rpad(round((safe_attachmentsSize/(1000.0*1000.0)),1),12),countAttachments))
                output+=("- archive size:             %sMB (in %s files)\n" %(rpad(round((safe_archiveSize/(1000.0*1000.0)),1),12),countArchiveFiles))
                output+=("---------------------------------------------\n")
                output+=("Valid files size:           %sMB (in %s files)\n\n" %(rpad(round((validSize/(1000.0*1000.0)),1),12),countValidFiles))
                output+=("Non-core file(s) size:      %sMB (in %s files)\n" %(rpad(round((nonValidSize/(1000.0*1000.0)),1),12),countNonValidFiles))
                for nonValid in listNonValidFiles:
                    output+=("   - Non-core: %sMB %s\n" %(rpad(round((nonValid[1]/(1000.0*1000.0)),1),5),nonValid[0]))
                output+="\n\n"

                if len(listLargeFiles):
                    output+=("\nLARGE (core) file(s) > 0.5MB....:\n")
                    for largefile in listLargeFiles:
                        output+=("   - %sMB Mod: %s %s\n" %(rpad(round((largefile[1]/(1000.0*1000.0)),1),5),largefile[2], largefile[0]))
                output+="\n\n"

                output+=(count_database_objects())

                output+=(find_other_datasets())

                output+="<END>"

                QuickJFrame("VIEW DATASET FILE ANALYSIS", output).show_the_frame()

                self.statusLabel.setText(("Your dataset contains %s files and is %sMB. %s non-core files were found consuming %sMB"
                                          %(countValidFiles,round((validSize/(1000.0*1000.0)),1),countNonValidFiles,round((nonValidSize/(1000.0*1000.0)),1))).ljust(800, " "))
                self.statusLabel.setForeground(Color.BLUE)

                myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
                return

        class DoTheMenu(AbstractAction):

            def __init__(self, statusLabel, displayPanel, menu, callingClass=None):
                self.statusLabel = statusLabel
                self.displayPanel = displayPanel
                self.menu = menu
                self.callingClass = callingClass

            def actionPerformed(self, event):
                global toolbox_frame_, debug, DARK_GREEN, lCopyAllToClipBoard_TB, lGeekOutModeEnabled_TB, lHackerMode, lAdvancedMode
                global lAutoPruneInternalBackups_TB

                myPrint("D", "In ", inspect.currentframe().f_code.co_name, "()", "Event: ", event )

                # ##########################################################################################################
                if event.getActionCommand() == "Help":
                    viewHelp = ViewFileButtonAction(self.statusLabel, "display_help()", "HELP DOCUMENTATION", lFile=False)
                    viewHelp.actionPerformed(None)

                # ##########################################################################################################
                if event.getActionCommand() == "About Toolbox":
                    about_this_script()

                # ##########################################################################################################
                if event.getActionCommand() == "About Moneydance":
                    moneydance_ui.showAbout()

                # ##########################################################################################################
                if event.getActionCommand() == "Auto Prune Internal Backups":

                    if not lAutoPruneInternalBackups_TB:
                        if not myPopupAskQuestion(toolbox_frame_,
                                                  "AUTO PRUNE INTERNAL BACKUPS",
                                                  "Turn on Auto-Prune of internal backups of config.dict & settings (will always keep 5 days and/or 5 copies)?",
                                                  JOptionPane.YES_NO_OPTION,
                                                  JOptionPane.WARNING_MESSAGE):
                            self.statusLabel.setText("AUTO-PRUNE INTERNAL BACKUPS DISABLED AS USER DECLINED TO PROCEED".ljust(800, " "))
                            self.statusLabel.setForeground(Color.RED)

                            for i in range(0, self.menu.getItemCount()):
                                x = self.menu.getItem(i)
                                if x.getText() == "Auto Prune Internal Backups":
                                    x.setSelected(False)
                                    break

                            return
                        else:
                            myPrint("B", "@@ User asked to turn ON auto-prune of internal backups of config.dict and settings (5 days/5 copies).....")
                    else:
                        myPrint("B", "User asked to turn OFF the auto-prune of internal backups of config.dict and settings.....")

                    lAutoPruneInternalBackups_TB = not lAutoPruneInternalBackups_TB

                    if lAutoPruneInternalBackups_TB:
                        prune_internal_backups(self.statusLabel)

                # ##########################################################################################################
                if event.getActionCommand() == "Geek Out Mode":
                    lGeekOutModeEnabled_TB = not lGeekOutModeEnabled_TB
                    components = self.displayPanel.getComponents()
                    for theComponent in components:
                        if isinstance(theComponent, JButton):
                            # noinspection PyUnresolvedReferences
                            buttonText = theComponent.getLabel().strip().upper()

                            if ("GEEK" in buttonText):
                                theComponent.setVisible(not theComponent.isVisible())

                    # Force a repaint to calculate scrollpane height....
                    self.callingClass.ReSizeListener(toolbox_frame_, self.displayPanel, self.callingClass.myScrollPane).componentResized("")

                # ##########################################################################################################
                if event.getActionCommand() == "Debug":
                    if debug:
                        self.statusLabel.setText("Script Debug mode disabled".ljust(800, " "))
                        self.statusLabel.setForeground(DARK_GREEN)
                    else:
                        self.statusLabel.setText("Script Debug mode enabled".ljust(800, " "))
                        self.statusLabel.setForeground(DARK_GREEN)
                        myPrint("B", "User has enabled script debug mode.......\n")

                    debug = not debug

                # ##########################################################################################################
                if event.getActionCommand() == "Copy all Output to Clipboard":
                    if lCopyAllToClipBoard_TB:
                        self.statusLabel.setText("Diagnostic outputs will not be copied to Clipboard".ljust(800, " "))
                        self.statusLabel.setForeground(DARK_GREEN)
                    else:
                        self.statusLabel.setText("Diagnostic outputs will now all be copied to the Clipboard".ljust(800, " "))
                        self.statusLabel.setForeground(DARK_GREEN)
                        myPrint("B", "User has requested to copy all diagnostic output to clipboard.......\n")

                    lCopyAllToClipBoard_TB = not lCopyAllToClipBoard_TB

                # ##########################################################################################################
                if event.getActionCommand() == "Hacker Mode":

                    if not lHackerMode:
                        if not myPopupAskQuestion(toolbox_frame_,
                                              "HACKER MODE",
                                              "HACKER MODE >> DISCLAIMER: DO YOU ACCEPT THAT YOU USE THIS TOOLBOX AT YOUR OWN RISK?",
                                                  JOptionPane.YES_NO_OPTION,
                                                  JOptionPane.ERROR_MESSAGE):
                            self.statusLabel.setText("HACKER MODE DISABLED AS USER DECLINED DISCLAIMER".ljust(800, " "))
                            self.statusLabel.setForeground(Color.RED)
                            myPrint("B", "User DECLINED the Disclaimer. Hacker Mode disabled........\n")

                            for i in range(0, self.menu.getItemCount()):
                                x = self.menu.getItem(i)
                                if x.getText() == "Hacker Mode":
                                    x.setSelected(False)
                                    break
                            return
                        else:
                            myPrint("B", "User accepted Disclaimer and agreed to use Toolbox Hacker mode at own risk.....")

                            backup = BackupButtonAction(self.statusLabel, "Would you like to create a backup before starting Hacker mode?")
                            backup.actionPerformed(None)

                            if not backup_local_storage_settings() or not backup_config_dict():
                                self.statusLabel.setText(("HACKER MODE DISABLED: SORRY - ERROR WHEN SAVING LocalStorage() ./safe/settings and config.dict to backup file!!??").ljust(800," "))
                                self.statusLabel.setForeground(Color.RED)
                                for i in range(0, self.menu.getItemCount()):
                                    x = self.menu.getItem(i)
                                    if x.getText() == "Hacker Mode":
                                        x.setSelected(False)
                                        break
                                return

                            myPrint("B","@@ HACKER MODE ENABLED. config.dict and safe/settings have been backed up...! @@")

                            self.statusLabel.setText(("HACKER MODE SELECTED - ONLY USE THIS IF YOU KNOW WHAT YOU ARE DOING - THIS CAN CHANGE DATA!").ljust(800," "))
                            self.statusLabel.setForeground(Color.RED)
                    else:
                        myPrint("B","HACKER MODE DISABLED <PHEW!>")
                        self.statusLabel.setText(("HACKER MODE DISABLED <PHEW!>").ljust(800," "))
                        self.statusLabel.setForeground(Color.BLUE)

                    lHackerMode = not lHackerMode

                    components = self.displayPanel.getComponents()
                    for theComponent in components:
                        if isinstance(theComponent, JButton):
                            # noinspection PyUnresolvedReferences
                            buttonText = theComponent.getLabel().strip().upper()

                            if ("HACKER" in buttonText):
                                theComponent.setVisible(lHackerMode)

                    # Force a repaint to calculate scrollpane height....
                    self.callingClass.ReSizeListener(toolbox_frame_, self.displayPanel, self.callingClass.myScrollPane).componentResized("")

                # ##########################################################################################################
                if event.getActionCommand() == "Advanced Mode":
                    if myPopupAskQuestion(toolbox_frame_,
                                          "ADVANCED MODE",
                                          "ADVANCED MODE >> DISCLAIMER: DO YOU ACCEPT THAT YOU USE THIS TOOLBOX AT YOUR OWN RISK?",
                                          JOptionPane.YES_NO_OPTION,
                                          JOptionPane.ERROR_MESSAGE):

                        myPrint("B", "User accepted Disclaimer and agreed to use Toolbox Advanced mode at own risk.....")

                        backup = BackupButtonAction(self.statusLabel, "Would you like to create a backup before starting Advanced mode?")
                        backup.actionPerformed(None)

                        self.statusLabel.setText(("ADVANCED MODE SELECTED - RED BUTTONS CAN CHANGE YOUR DATA - %s+I for Help"%moneydance_ui.ACCELERATOR_MASK_STR).ljust(800," "))
                        self.statusLabel.setForeground(Color.RED)

                        lAdvancedMode = True

                        for i in range(0, self.menu.getItemCount()):
                            x = self.menu.getItem(i)
                            if x.getText() == "Advanced Mode":
                                x.setEnabled(False)
                            else:
                                x.setEnabled(True)

                        components = self.displayPanel.getComponents()
                        for theComponent in components:
                            if isinstance(theComponent, JButton):
                                # noinspection PyUnresolvedReferences
                                buttonText = theComponent.getLabel().strip().upper()

                                if  "HACKER" in buttonText:
                                    pass
                                elif("FIX" in buttonText
                                      or "FONTS" in buttonText
                                      or "RESET" in buttonText
                                      or "DELETE" in buttonText
                                      or "FORGET" in buttonText):
                                    theComponent.setVisible(True)

                                if "MENU:".upper() in buttonText.upper():
                                    theComponent.setForeground(Color.RED)

                        # Force a repaint to calculate scrollpane height....
                        self.callingClass.ReSizeListener(toolbox_frame_, self.displayPanel, self.callingClass.myScrollPane).componentResized("")

                    else:
                        self.statusLabel.setText("ADVANCED MODE DISABLED AS USER DECLINED DISCLAIMER - BASIC MODE ONLY".ljust(800, " "))
                        self.statusLabel.setForeground(Color.RED)
                        myPrint("B", "User DECLINED the Disclaimer. Advanced Mode disabled........\n")

                # ##########################################################################################################
                if event.getActionCommand() == "Basic Mode":
                    self.statusLabel.setText("BASIC MODE SELECTED".ljust(800, " "))
                    self.statusLabel.setForeground(DARK_GREEN)

                    lAdvancedMode = False

                    for i in range(0, self.menu.getItemCount()):
                        x = self.menu.getItem(i)
                        if x.getText() == "Basic Mode":
                            x.setEnabled(False)
                        else:
                            x.setEnabled(True)

                    components = self.displayPanel.getComponents()
                    for theComponent in components:
                        if isinstance(theComponent, JButton):
                            # noinspection PyUnresolvedReferences
                            buttonText = theComponent.getLabel().strip().upper()

                            if "DIAG" in buttonText:
                                pass
                            elif "HACKER" in buttonText:
                                pass
                            elif ("FIX" in buttonText
                                  or "FONTS" in buttonText
                                  or "RESET" in buttonText
                                  or "DELETE" in buttonText
                                  or "FORGET" in buttonText):
                                theComponent.setVisible(False)

                            if "MENU:".upper() in buttonText.upper():
                                theComponent.setForeground(Color(74,74,74))

                    # Force a repaint to calculate scrollpane height....
                    self.callingClass.ReSizeListener(toolbox_frame_, self.displayPanel, self.callingClass.myScrollPane).componentResized("")


                # Save parameters now...
                if (event.getActionCommand() == "Copy all Output to Clipboard"
                        or event.getActionCommand() == "Debug"
                        or event.getActionCommand() == "Geek Out Mode"
                        or event.getActionCommand() == "Auto Prune Internal Backups"):

                    try:
                        save_StuWareSoftSystems_parameters_to_file()
                    except:
                        myPrint("B", "Error - failed to save parameters to pickle file...!")
                        dump_sys_error_to_md_console_and_errorlog()


                myPrint("D", "Exiting ", inspect.currentframe().f_code.co_name, "()")
                return

        def openDisplay(self):
            global toolbox_frame_, DARK_GREEN, lPickle_version_warning, lCopyAllToClipBoard_TB, myParameters, lIgnoreOutdatedExtensions_TB, version_build
            global lAdvancedMode, lHackerMode, lAutoPruneInternalBackups_TB, MYPYTHON_DOWNLOAD_URL

            # ConsoleWindow.showConsoleWindow(moneydance_ui)
            hacker_mode_DEBUG(None,lForceON=True)

            screenSize = Toolkit.getDefaultToolkit().getScreenSize()

            button_width = 230
            button_height = 40
            # panel_width = frame_width - 50
            # button_panel_height = button_height + 5
            # frame_width = screenSize.width - 20
            # frame_height = screenSize.height - 20

            frame_width = min(screenSize.width-20, max(1024,int(round(moneydance_ui.firstMainFrame.getSize().width *.95,0))))
            frame_height = min(screenSize.height-20, max(768, int(round(moneydance_ui.firstMainFrame.getSize().height *.95,0))))

            JFrame.setDefaultLookAndFeelDecorated(True)
            toolbox_frame_ = MyJFrame("Infinite Kind (co-authored by StuWareSoftSystems): " + myScriptName + " (" + version_build + ")...  (%s+I for Help)    -    DATASET: %s" % (moneydance_ui.ACCELERATOR_MASK_STR, moneydance.getCurrentAccountBook().getName().strip()))
            toolbox_frame_.setName(u"%s_main" %myModuleID)
            # toolbox_frame_.setLayout(FlowLayout())

            # icon = moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png")
            # icon = Toolkit.getDefaultToolkit().getImage("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png")
            # print type(icon)
            # toolbox_frame_.setIconImage(icon)

            if (not Platform.isMac()):
                moneydance_ui.getImages()
                toolbox_frame_.setIconImage(MDImages.getImage(moneydance_ui.getMain().getSourceInformation().getIconResource()))

            # toolbox_frame_.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE)  # The CloseAction() and WindowListener() will handle dispose() - else change back to DISPOSE_ON_CLOSE
            toolbox_frame_.setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE)  # The CloseAction() and WindowListener() will handle dispose() - else change back to DISPOSE_ON_CLOSE

            displayString = buildDiagText()
            statusLabel = JLabel(("Infinite Kind (Moneydance) support tool >> DIAG STATUS: BASIC MODE RUNNING... - %s+I for Help (check out the Toolbox menu for more options/modes/features)"%moneydance_ui.ACCELERATOR_MASK_STR).ljust(800, " "), JLabel.LEFT)
            statusLabel.setForeground(DARK_GREEN)

            try:
                # If we are here then lCopyAllToClipBoard_TB was loaded from parameter file....
                if lCopyAllToClipBoard_TB:
                    Toolkit.getDefaultToolkit().getSystemClipboard().setContents(StringSelection(displayString), None)
            except:
                myPrint("J","Error copying diagnostic's main screen contents to Clipboard")
                dump_sys_error_to_md_console_and_errorlog()

            shortcut = Toolkit.getDefaultToolkit().getMenuShortcutKeyMaskEx()

            # Add standard CMD-W keystrokes etc to close window
            toolbox_frame_.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_W, shortcut), "close-window")
            toolbox_frame_.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_F4, shortcut), "close-window")
            toolbox_frame_.getRootPane().getActionMap().put("close-window", self.CloseAction(toolbox_frame_))
            toolbox_frame_.addWindowListener(self.WindowListener(toolbox_frame_))

            toolbox_frame_.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_P, shortcut), "display-pickle")
            toolbox_frame_.getRootPane().getActionMap().put("display-pickle", ViewFileButtonAction(statusLabel, "display_pickle()", "StuWareSoftSystems Pickle Parameter File", lFile=False))

            toolbox_frame_.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT).put(KeyStroke.getKeyStroke(KeyEvent.VK_I, shortcut), "display-help")
            toolbox_frame_.getRootPane().getActionMap().put("display-help", ViewFileButtonAction(statusLabel, "display_help()", "HELP DOCUMENTATION", lFile=False))

            toolbox_frame_.setPreferredSize(Dimension(frame_width, frame_height))

            # if moneydance_ui.firstMainFrame.getExtendedState() != JFrame.ICONIFIED:
            #     toolbox_frame_.setExtendedState(moneydance_ui.firstMainFrame.getExtendedState())
            # else:
            #     toolbox_frame_.setExtendedState(JFrame.MAXIMIZED_BOTH)
            #
            toolbox_frame_.setExtendedState(JFrame.NORMAL)

            displayPanel = JPanel()
            displayPanel.setLayout(FlowLayout(FlowLayout.LEFT))

            displayPanel.setPreferredSize(Dimension(frame_width - 30, 300))

            if lAutoPruneInternalBackups_TB:
                prune_internal_backups(statusLabel,lStartup=True)
            else:
                myPrint("J","Auto-prune of internal backups of config.dict, custom_theme.properties, ./safe/settings files is disabled... so no action")

            # START OF BUTTONS
            backup_button = JButton("<html><center><B>EXPORT BACKUP</B></center></html>")
            backup_button.setToolTipText("This will allow you to take a backup of your Moneydance Dataset")
            backup_button.setBackground(DARK_GREEN)
            backup_button.setForeground(Color.WHITE)
            backup_button.addActionListener(BackupButtonAction(statusLabel, "Confirm you want to create a backup (same as MD Menu>File>Export Backup)?"))
            displayPanel.add(backup_button)

            # These are instant fix buttons
            if (not moneydance_data.getLocalStorage().getBoolean("_is_master_node", True)):
                convertSecondary_button = JButton("<html><center><B>FIX: Make me a<BR>Primary dataset</B></center></html>")
                convertSecondary_button.setToolTipText("This will allow you to make this Dataset a Primary / Master Dataset (typically used if you restored from a synchronised secondary dataset/backup). THIS CHANGES DATA!")
                convertSecondary_button.setBackground(Color.ORANGE)
                convertSecondary_button.setForeground(Color.WHITE)
                convertSecondary_button.addActionListener(self.ConvertSecondaryButtonAction(displayString, statusLabel))
                convertSecondary_button.setVisible(False)
                displayPanel.add(convertSecondary_button)

            if (not check_for_dropbox_folder()):
                createMoneydanceSyncFolder_button = JButton("<html><center><B>FIX: Create Dropbox<BR>Sync Folder</B></center></html>")
                createMoneydanceSyncFolder_button.setToolTipText("This will allow you to add the missing .moneydancesync folder in Dropbox. THIS CREATES A FOLDER!")
                createMoneydanceSyncFolder_button.setBackground(Color.ORANGE)
                createMoneydanceSyncFolder_button.setForeground(Color.WHITE)
                createMoneydanceSyncFolder_button.addActionListener(self.MakeDropBoxSyncFolder(statusLabel, createMoneydanceSyncFolder_button))
                createMoneydanceSyncFolder_button.setVisible(False)
                displayPanel.add(createMoneydanceSyncFolder_button)

            lTabbingModeNeedsChanging = False
            if Platform.isOSX() and Platform.isOSXVersionAtLeast("10.16") \
                    and not DetectAndChangeMacTabbingMode(statusLabel, True).actionPerformed("quick check"):
                lTabbingModeNeedsChanging = True
                fixTabbingMode_button = JButton("<html><center><B>FIX: MacOS<BR>Tabbing Mode</B></center></html>")
                fixTabbingMode_button.setToolTipText("This allows you to check/fix your MacOS Tabbing Setting")
                fixTabbingMode_button.setBackground(Color.ORANGE)
                fixTabbingMode_button.setForeground(Color.WHITE)
                fixTabbingMode_button.addActionListener(DetectAndChangeMacTabbingMode(statusLabel, False))
                fixTabbingMode_button.setVisible(False)
                displayPanel.add(fixTabbingMode_button)

            if moneydance_data.getLocalStorage().getStr("migrated.netsync.dropbox.fileid", None):
                FixDropboxOneWaySync_button = JButton("<html><center><B>FIX: Fix Dropbox<BR>One Way Syncing</B></center></html>")
                FixDropboxOneWaySync_button.setToolTipText("This removes the key migrated.netsync.dropbox.fileid to fix Dropbox One-way Syncing (reset_sync_and_dropbox_settings.py)")
                FixDropboxOneWaySync_button.setBackground(Color.ORANGE)
                FixDropboxOneWaySync_button.setForeground(Color.WHITE)
                FixDropboxOneWaySync_button.addActionListener(self.FixDropboxOneWaySyncButtonAction(statusLabel, FixDropboxOneWaySync_button))
                FixDropboxOneWaySync_button.setVisible(False)
                displayPanel.add(FixDropboxOneWaySync_button)
            # end of instant fix buttons

            analiseDatasetSize_button = JButton("<html><center>Analyse Dataset<BR>Objs, Size & Files</center></html>")
            analiseDatasetSize_button.setToolTipText("This quickly analyse the contents of your dataset and show you your Object counts, file sizes, what's taking space, and non-valid files...(show_object_type_quantities.py)")
            analiseDatasetSize_button.addActionListener(self.AnalyseDatasetSizeButtonAction(statusLabel))
            displayPanel.add(analiseDatasetSize_button)

            findDataset_button = JButton("<html><center>Find My Dataset(s)<BR>and Backups</center></html>")
            findDataset_button.setToolTipText("This will search your hard disk for copies of your Moneydance Dataset(s) - incl Backups.... NOTE: Can be CPU & time intensive..!")
            findDataset_button.addActionListener(self.FindDatasetButtonAction(statusLabel))
            displayPanel.add(findDataset_button)

            generalToolsMenu_button = JButton("<html><center>MENU: General<BR>tools</center></html>")
            generalToolsMenu_button.setToolTipText("Menu containing a variety of general Diagnostics, Fixes and Tools...")
            generalToolsMenu_button.addActionListener(self.GeneralToolsMenuButtonAction(statusLabel))
            displayPanel.add(generalToolsMenu_button)

            onlineBankingTools_button = JButton("<html><center>MENU: Online Banking<BR>(OFX) Tools</center></html>")
            onlineBankingTools_button.setToolTipText("A selection of tools for Online Banking - SOME OPTIONS CAN CHANGE DATA!")
            onlineBankingTools_button.addActionListener(self.OnlineBankingToolsButtonAction(statusLabel))
            displayPanel.add(onlineBankingTools_button)

            currencySecurityMenu_button = JButton("<html><center>MENU: Currency<BR>& Security tools</center></html>")
            currencySecurityMenu_button.setToolTipText("Menu containing Currency/Security Diagnostics, Fixes and Tools...")
            currencySecurityMenu_button.addActionListener(self.CurrencySecurityMenuButtonAction(statusLabel))
            displayPanel.add(currencySecurityMenu_button)

            accountsCategoryMenu_button = JButton("<html><center>MENU: Accounts<BR>& Categories tools</center></html>")
            accountsCategoryMenu_button.setToolTipText("Menu containing Account and Category Diagnostics, Fixes and Tools...")
            accountsCategoryMenu_button.addActionListener(self.AccountsCategoriesMenuButtonAction(statusLabel))
            displayPanel.add(accountsCategoryMenu_button)

            transactionMenu_button = JButton("<html><center>MENU: Transactions<BR>tools</center></html>")
            transactionMenu_button.setToolTipText("Menu containing Transactional Diagnostics, Fixes and Tools...")
            transactionMenu_button.addActionListener(self.TransactionMenuButtonAction(statusLabel))
            displayPanel.add(transactionMenu_button)

            GeekOutMode_button = JButton("<html><B>Geek Out</B></html>")
            GeekOutMode_button.setToolTipText("This allows you to display very Technical Information on the Moneydance System and many key objects..... READONLY")
            GeekOutMode_button.setBackground(Color.MAGENTA)
            GeekOutMode_button.setForeground(Color.WHITE)
            GeekOutMode_button.addActionListener(GeekOutModeButtonAction(statusLabel))
            GeekOutMode_button.setVisible(lGeekOutModeEnabled_TB)
            displayPanel.add(GeekOutMode_button)

            hackerMenu_button = JButton("<html><center><B>HACKER MODE</B></center></html>")
            hackerMenu_button.setToolTipText("Menu containing 'Hacker' Tools...")
            hackerMenu_button.addActionListener(self.HackerMenuButtonAction(statusLabel))
            hackerMenu_button.setBackground(Color.RED)
            hackerMenu_button.setForeground(Color.WHITE)
            hackerMenu_button.setVisible(False)
            displayPanel.add(hackerMenu_button)

            components = displayPanel.getComponents()
            for theComponent in components:
                if isinstance(theComponent, JButton):
                    theComponent.setPreferredSize(Dimension(button_width, button_height))
                    theComponent.setBorderPainted(False)
                    theComponent.setOpaque(True)
                    if not (theComponent.getBackground() == Color.MAGENTA
                        or theComponent.getBackground() == Color.RED
                            or theComponent.getBackground() == Color.ORANGE
                                or theComponent.getBackground() == DARK_GREEN):
                        theComponent.setBackground(Color.LIGHT_GRAY)

            myDiagText = JTextArea(displayString)
            myDiagText.setEditable(False)
            myDiagText.setLineWrap(True)
            myDiagText.setWrapStyleWord(True)
            myDiagText.setFont( getMonoFont() )

            displayPanel.add(statusLabel)

            self.myScrollPane = JScrollPane(myDiagText, JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED,JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED)
            self.myScrollPane.setPreferredSize(Dimension(frame_width - 30, frame_height - displayPanel.getPreferredSize().height))

            self.myScrollPane.setWheelScrollingEnabled(True)
            displayPanel.add(self.myScrollPane)

            keyToUse = shortcut

            if Platform.isWindows():
                keyToUse = InputEvent.ALT_MASK

            if Platform.isOSX():
                save_useScreenMenuBar= System.getProperty("apple.laf.useScreenMenuBar")
                System.setProperty("apple.laf.useScreenMenuBar", "false")

            mb = JMenuBar()
            menu1 = JMenu("<html><b>TOOLBOX Options</b></html>")
            menu1.setMnemonic(KeyEvent.VK_T)

            menuItem0 = JMenuItem("Basic Mode")
            menuItem0.setMnemonic(KeyEvent.VK_B)
            menuItem0.setAccelerator(KeyStroke.getKeyStroke(KeyEvent.VK_B, keyToUse))
            menuItem0.setToolTipText("Switch to basic (no harm) mode")
            menuItem0.addActionListener(self.DoTheMenu(statusLabel, displayPanel, menu1, self))
            menuItem0.setEnabled(False)
            menu1.add(menuItem0)

            menuItem1 = JMenuItem("Advanced Mode")
            menuItem1.setMnemonic(KeyEvent.VK_M)  # Can't think of a spare letter to use!!!!
            menuItem1.setAccelerator(KeyStroke.getKeyStroke(KeyEvent.VK_M, keyToUse))
            menuItem1.addActionListener(self.DoTheMenu(statusLabel, displayPanel, menu1, self))
            menuItem1.setToolTipText("Switch to Advanced / Fix Mode (can update data)")
            menu1.add(menuItem1)

            menuItemC = JCheckBoxMenuItem("Copy all Output to Clipboard")
            menuItemC.setMnemonic(KeyEvent.VK_O)  # Can't think of a spare letter to use!!!!
            menuItemC.setAccelerator(KeyStroke.getKeyStroke(KeyEvent.VK_O, keyToUse))
            menuItemC.addActionListener(self.DoTheMenu(statusLabel, displayPanel, menu1, self))
            menuItemC.setToolTipText("When selected copies the output of all displays to Clipboard")
            menuItemC.setSelected(lCopyAllToClipBoard_TB)
            menu1.add(menuItemC)

            menuItemG = JCheckBoxMenuItem("Geek Out Mode")
            menuItemG.setMnemonic(KeyEvent.VK_G)  # Can't think of a spare letter to use!!!!
            menuItemG.setAccelerator(KeyStroke.getKeyStroke(KeyEvent.VK_G, keyToUse))
            menuItemG.addActionListener(self.DoTheMenu(statusLabel, displayPanel, menu1, self))
            menuItemG.setToolTipText("Enables the Geek Out Button to show very technical stuff - readonly")
            menuItemG.setSelected(lGeekOutModeEnabled_TB)
            menu1.add(menuItemG)

            menuItemH = JCheckBoxMenuItem("Hacker Mode")
            menuItemH.addActionListener(self.DoTheMenu(statusLabel, displayPanel, menu1, self))
            menuItemH.setToolTipText("Enables 'Hacker' Mode - Do not do this unless you know what you are doing... Allows you to update data!")
            menuItemH.setSelected(False)
            menu1.add(menuItemH)

            menuItemD = JCheckBoxMenuItem("Debug")
            menuItemD.addActionListener(self.DoTheMenu(statusLabel, displayPanel, menu1, self))
            menuItemD.setToolTipText("Enables script to output debug information - technical stuff - readonly")
            menuItemD.setSelected(debug)
            menu1.add(menuItemD)

            menuItemP = JCheckBoxMenuItem("Auto Prune Internal Backups")
            menuItemP.addActionListener(self.DoTheMenu(statusLabel, displayPanel, menu1, self))
            menuItemP.setToolTipText("Enables auto pruning of the internal backups that Toolbox makes of config.dict, custom_theme.properties, and ./safe/settings")
            menuItemP.setSelected(lAutoPruneInternalBackups_TB)
            menu1.add(menuItemP)

            menuItem2 = JMenuItem("Exit")
            menuItem2.setMnemonic(KeyEvent.VK_E)
            menuItem2.setAccelerator(KeyStroke.getKeyStroke(KeyEvent.VK_E, keyToUse))
            menuItem2.addActionListener(self.CloseAction(toolbox_frame_))
            menuItem2.setToolTipText("Exit this Toolbox")
            menu1.add(menuItem2)

            mb.add(menu1)

            menuH = JMenu("<html>HELP</html>")
            menuH.setMnemonic(KeyEvent.VK_I)

            menuItemH = JMenuItem("Help")
            menuItemH.setMnemonic(KeyEvent.VK_I)
            menuItemH.setAccelerator(KeyStroke.getKeyStroke(KeyEvent.VK_I, keyToUse))
            menuItemH.setToolTipText("Display Help")
            menuItemH.addActionListener(self.DoTheMenu(statusLabel, displayPanel, menuH, self))
            menuItemH.setEnabled(True)
            menuH.add(menuItemH)

            menuItemA = JMenuItem("About Toolbox")
            menuItemA.setToolTipText("About...")
            menuItemA.addActionListener(self.DoTheMenu(statusLabel, displayPanel, menuH, self))
            menuItemA.setEnabled(True)
            menuH.add(menuItemA)

            menuItemAMD = JMenuItem("About Moneydance")
            menuItemAMD.setToolTipText("About...")
            menuItemAMD.addActionListener(self.DoTheMenu(statusLabel, displayPanel, menuH, self))
            menuItemAMD.setEnabled(True)
            menuH.add(menuItemAMD)

            mb.add(menuH)

            # ##############

            mb.add(Box.createHorizontalGlue())

            btnConsole = JButton("Launch Console Window")
            btnConsole.setToolTipText("launches the Moneydance Console Window (and turns DEBUG on).. Useful for extra diagnostics!")
            btnConsole.setOpaque(True)
            btnConsole.setBackground(Color.WHITE)
            btnConsole.setForeground(Color.BLACK)

            btnSaveConsole = JButton("Save Console Log")
            btnSaveConsole.setToolTipText("Copy/save the Console Error log file to a directory of your choosing..")
            btnSaveConsole.setOpaque(True)
            btnSaveConsole.setBackground(Color.WHITE)
            btnSaveConsole.setForeground(Color.BLACK)

            btnOpenMDFolder = JButton("Open MD Folder")
            btnOpenMDFolder.setToolTipText("Open the selected Moneydance (internal) folder in Explorer/Finder window (etc)")
            btnOpenMDFolder.setOpaque(True)
            btnOpenMDFolder.setBackground(Color.WHITE)
            btnOpenMDFolder.setForeground(Color.BLACK)

            btnCopyDiagnostics = JButton("Copy Diagnostics below to Clipboard")
            btnCopyDiagnostics.setToolTipText("Copies the contents of the main diagnostics window (below) to the Clipboard..")
            btnCopyDiagnostics.setOpaque(True)
            btnCopyDiagnostics.setBackground(Color.WHITE)
            btnCopyDiagnostics.setForeground(Color.BLACK)

            mb.add(btnConsole)
            mb.add(Box.createRigidArea(Dimension(10, 0)))
            mb.add(btnSaveConsole)
            mb.add(Box.createRigidArea(Dimension(10, 0)))
            mb.add(btnOpenMDFolder)
            mb.add(Box.createRigidArea(Dimension(10, 0)))
            mb.add(btnCopyDiagnostics)

            mb.add(Box.createRigidArea(Dimension(30, 0)))

            btnConsole.addActionListener(ShowTheConsole(statusLabel))
            btnSaveConsole.addActionListener(CopyConsoleLogFileButtonAction(statusLabel, moneydance.getLogFile()))
            btnOpenMDFolder.addActionListener(OpenFolderButtonAction(statusLabel))
            btnCopyDiagnostics.addActionListener(ClipboardButtonAction(displayString, statusLabel))
            # ##############

            toolbox_frame_.setJMenuBar(mb)

            toolbox_frame_.add(displayPanel)

            toolbox_frame_.pack()
            toolbox_frame_.setLocationRelativeTo(None)

            try:
                toolbox_frame_.MoneydanceAppListener = MyEventListener(toolbox_frame_)
                moneydance.addAppEventListener(toolbox_frame_.MoneydanceAppListener)
                myPrint("DB","@@@ Added MD App Listener...")
            except:
                myPrint("B","FAILED to add MD App Listener...")
                dump_sys_error_to_md_console_and_errorlog()

            toolbox_frame_.getRootPane().addComponentListener(self.ReSizeListener(toolbox_frame_, displayPanel, self.myScrollPane))
            toolbox_frame_.setVisible(True)
            toolbox_frame_.isActiveInMoneydance = True

            # Force a repaint to calculate scrollpane height....
            self.ReSizeListener(toolbox_frame_, displayPanel, self.myScrollPane).componentResized("")

            if Platform.isOSX():
                System.setProperty("apple.laf.useScreenMenuBar", save_useScreenMenuBar)                                 # noqa

            if not moneydance_data.getLocalStorage().getBoolean("_is_master_node", True):

                MyPopUpDialogBox(toolbox_frame_,"!! WARNING / ALERT !!:",
                                                 "This Dataset is running as a Secondary Node\n" 
                                                 "- either you are Synchronising to it,\n" 
                                                 "- or you have restored it from a backup/sync copy.\n" 
                                                 "To convert to Primary, use Advanced Tools Menu",
                                                 120,
                                                 "SECONDARY DATASET/NODE",
                                                 OKButtonText="ACKNOWLEDGE",
                                                 lAlertLevel=1).go()

            if lTabbingModeNeedsChanging:
                myPopupInformationBox(toolbox_frame_,
                                      "Your Mac has 'Tabbing Mode' set to 'always'\n" +
                                      "- You can find this in Settings>General>Prefer tabs:,\n" +
                                      "- THIS CAUSES STRANGE MONEYDANCE FREEZES.\n" +
                                      ">> To change this setting now, use Advanced Mode...\n" +
                                      "........\n",
                                      "MacOS TABBING MODE WARNING",
                                      JOptionPane.ERROR_MESSAGE)

            if Platform.isOSX() and System.getProperty(u"UserHome") is None:
                myPopupInformationBox(toolbox_frame_,
                                      "Your Mac's System Property 'UserHome' is not set\n" +
                                      "Some features in Toolbox may not work as expected",
                                      "MacOS UserHome Warning",
                                      JOptionPane.WARNING_MESSAGE)


            check_for_old_StuWareSoftSystems_scripts(statusLabel)

            _tb_extn_avail_version = check_for_updatable_extensions_on_startup(statusLabel)

            checkModule = myModuleID
            myExtensions = downloadStuWareSoftSystemsExtensions(checkModule)
            if myExtensions:
                myModule = myExtensions.get("id")
                if myModule == checkModule:
                    availableFromGitHubVersion = int(myExtensions.get("module_build"))
                    if availableFromGitHubVersion > int(version_build):
                        myPrint("DB","Toolbox upgrade to version %s is available from GitHub to download...." %(availableFromGitHubVersion))
                        theStr = "You are running version %s\n" %version_build
                        if _tb_extn_avail_version > int(version_build):
                            theStr += "Extension version %s is available from Moneydance Menu>Manage Extensions Menu\n" %_tb_extn_avail_version
                        if availableFromGitHubVersion > _tb_extn_avail_version:
                            theStr += "Version %s is available from %s" %(availableFromGitHubVersion, MYPYTHON_DOWNLOAD_URL)

                        MyPopUpDialogBox(toolbox_frame_,"Toolbox Version:",theStr,200,"UPGRADE AVAILABLE",OKButtonText="Acknowledge").go()
                    else:
                        myPrint("DB","I've checked GitHub and Toolbox is running latest version: %s" %availableFromGitHubVersion)

            checkForREADONLY(statusLabel)


    if not i_am_an_extension_so_run_headless: print("""
Script is analysing your moneydance & system settings....
------------------------------------------------------------------------------
>> DISCLAIMER: This script has the ability to change your data
>> Always perform backup first before making any changes!
>> The Author of this script can take no responsibility for any harm caused
>> If you do not accept this, please exit the script
------------------------------------------------------------------------------
""")

    # This gets the latest build info from the developer... and it overrides the program defaults...
    download_toolbox_version_info()

    lAbort=False
    if TOOLBOX_STOP_NOW:
        lAbort = True
    elif float(moneydance.getVersion()) < TOOLBOX_MINIMUM_TESTED_MD_VERSION or not lImportOK:
        lAbort = True
    elif int(float(moneydance.getVersion())) > int(TOOLBOX_MAXIMUM_TESTED_MD_VERSION):  # Just stick to major version checks....
        lAbort = True
    else:
        if (float(moneydance.getBuild()) <= TOOLBOX_MAXIMUM_TESTED_MD_BUILD
                    or myPopupAskQuestion(None,"Toolbox(build: %s) - Moneydance Version/Build" %(version_build),
                                      "MD build (%s)%s is newer than the Toolbox tested build of (%s)%s - Proceed?"
                                      %(moneydance.getVersion(),moneydance.getBuild(),TOOLBOX_MAXIMUM_TESTED_MD_VERSION,TOOLBOX_MAXIMUM_TESTED_MD_BUILD),
                                      JOptionPane.WARNING_MESSAGE)):

            # if float(moneydance.getBuild()) > TOOLBOX_MAXIMUM_TESTED_MD_BUILD:
            #     myPrint("B","@@ WARNING - MD build (%s)%s is newer than the Toolbox tested build of (%s)%s....!"
            #             %(moneydance.getVersion(),moneydance.getBuild(),TOOLBOX_MAXIMUM_TESTED_MD_VERSION,TOOLBOX_MAXIMUM_TESTED_MD_BUILD))

            fixRCurrencyCheck = 0

            moneydance_ui.firstMainFrame.setStatus(">> Infinite Kind (co-authored by Stuart Beesley: StuWareSoftSystems) - Toolbox launching.......",0)

            # These checks already run at Dataset Load time:
            # >> com.infinitekind.moneydance.model.AccountBook.performPostLoadVerification()
            # That Currency BaseType is set
            #   >> com.infinitekind.moneydance.model.CurrencyType.performPostLoadVerification()
            #       >> Relative currency loops, zero rate
            #   >> Orphan snapshots with no registered Currency - deletes them
            #   >> Redundant Base currency snapshots - deletes them
            #   >> On each snapshot com.infinitekind.moneydance.model.CurrencySnapshot.performPostLoadVerification
            #       >> resets relative rates < 0 relative to base rate
            #   >> For csplits registered with currency
            #   >> Then sorts the Currency's snapshots and cplits
            # That Account structures are valid
            #   >> Broken acct numbers (old)
            #   >> Validates account structures: com.infinitekind.moneydance.model.Account.ensureAccountStructure()
            #       >> Iterates all accounts. If it finds acct eq type ROOT validates it's the root, fixes duplicate roots, replaces root
            #       >> where not ROOT, validates the parent of this acct has sub accounts
            #   >> Then checks that getRootAccount() is not None - else:
            #       >> it finds it & sets it, or creates it
            #       >> also it also detects and cleans up duplicate roots
            #   >> It also finds orphan accounts, with no parent and links them to root
            # That budget structures are OK.
            # That Txns are valid
            #   >> Txns with getOtherCount() <= 0 get deleted (when a parent)
            #   >> That Txns are not linked to Root (warning only)
            #   >> If Account does not exist:
            #       >> Makes a new account (with ts = 0 = ghost account)
            # Then sorts Accounts
            # Then refreshes balances

            # Check based on fix_restored_accounts.py
            _root = moneydance_data.getRootAccount()   # Should never happen!
            if _root is None or _root.getAccountType()!=Account.AccountType.ROOT:                                       # noqa
                myPopupInformationBox(None,"ERROR: I've Detected that your ROOT Account is Missing or not type ROOT! Contact support or the Author of Toolbox for a fix",
                                      "ROOT ACCOUNT WARNING",JOptionPane.ERROR_MESSAGE)
                myPrint("B","@@ ERROR: I've Detected that your ROOT Account is Missing or not type ROOT! Contact support or the Author of Toolbox for a fix")
                myPrint("B","@@ FYI - there used to be scripts called fix_restored_accounts.py or fix_root_account_type.py for this (but the last time I looked they were broken.....")
            else:
                theDisplay = DiagnosticDisplay()
                theDisplay.openDisplay()

                myPrint("P","-----------------------------------------------------------------------------------------------------------")
                myPrint("B", "Infinite Kind in conjunction with StuWareSoftSystems - ", myScriptName, " script ending (frame is open/running)......")
                myPrint("P","-----------------------------------------------------------------------------------------------------------")
        else:
            lAbort = True

    if lAbort:
        if TOOLBOX_STOP_NOW:
            myPrint("B", "STOP-NOW COMMAND RECEIVED!")
            myPopupInformationBox(None,
                                  "Sorry, Toolbox has received a STOP-NOW command from developer....!",
                                  "Toolbox- STOP-NOW",
                                  JOptionPane.ERROR_MESSAGE)
        else:
            myPrint("B", "Sorry, this Toolbox (build %s) has only been tested on Moneydance versions %s thru' %s(build %s)... Yours is %s(%s) >> Exiting....."
                    %(version_build, TOOLBOX_MINIMUM_TESTED_MD_VERSION, TOOLBOX_MAXIMUM_TESTED_MD_VERSION,TOOLBOX_MAXIMUM_TESTED_MD_BUILD,moneydance.getVersion(),moneydance.getBuild()))
            myPopupInformationBox(None,
                                  "Sorry, this Toolbox (build %s) has only been tested on Moneydance versions %s thru' %s(build %s)... Yours is %s(%s) >> Exiting....."
                                  %(version_build, TOOLBOX_MINIMUM_TESTED_MD_VERSION, TOOLBOX_MAXIMUM_TESTED_MD_VERSION,TOOLBOX_MAXIMUM_TESTED_MD_BUILD,moneydance.getVersion(),moneydance.getBuild()),
                                  "Toolbox- VERSION TOO NEW",
                                  JOptionPane.ERROR_MESSAGE)

#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# demo_calling_import_functions.py - Build: 4
# A basic demo Python (Jython) script to get you started - Stuart Beesley - StuWareSoftSystems - Feb 2021
# Allows you to call the Moneydance Import File function, set parameters, and bypass the popup screens
# It's written with code to demo what it possible.. You should taylor the flow/setup accordingly....

# Reverse engineered from:
# com.moneydance.apps.md.view.gui.MoneydanceGUI.importFile(fileToImport, newAccountSet=False, contextAccount=moneydance_ui.firstMainFrame.getSelectedAccount())

global moneydance, moneydance_data, moneydance_ui

if float(moneydance.getBuild()) < 1904:     # Check for builds less than 1904 / version < 2019.4
    try:
        moneydance.getUI().showInfoMessage("SORRY YOUR VERSION IS TOO OLD FOR THESE SCRIPTS")
    except:
        pass
    raise Exception("SORRY YOUR VERSION IS TOO OLD FOR THESE SCRIPTS")


import os
from java.lang import System
from java.io import File, FileInputStream
from javax.swing import JOptionPane
from com.infinitekind.moneydance.model import Account
from com.moneydance.apps.md.controller.fileimport import FileImporter
from com.moneydance.apps.md.controller import AccountBookWrapper
from com.infinitekind.moneydance.model.txtimport import ImportDataSourceType
from com.moneydance.apps.md.controller.fileimport import TextFileImporter
from com.moneydance.apps.md.view.gui.txtimport import TextImport
from com.moneydance.apps.md.view.gui import QIFImportSettingsWindow
from com.moneydance.apps.md.controller.fileimport import QIFFileImporter
# from com.moneydance.apps.md.view.gui import ImportTask
from com.moneydance.util import Platform
from java.awt import FileDialog

# ######################################################################################################################
# ######################################################################################################################
# SET PARAMETERS HERE......!
i_want_popups = False    # False = Run headless.. True = Run just like like Moneydance does normally

# default_import_type = ImportDataSourceType.DOWNLOADED
default_import_type = ImportDataSourceType.MIGRATED_FROM_ANOTHER_APP

# Set this if you want to run headless.... or set to None
# fileToImport=None
fileToImport="/Users/stu/Documents/Moneydance/My Python Scripts/test data/WO_Flag.qif"

# True = use the currently selected account in the sidebar....
use_side_bar_selected_account = True  # Set this to False if you want to pre-select your account below

# OPTIONAL - Pre-select your Account name here - If using sidebar select just leave as is.....
acct=moneydance.getRootAccount().getAccountByName("Enter Exact Name Here",
                                                  Account.AccountType.BANK)                                          # noqa
# Options are: ASSET, BANK, CREDIT_CARD, EXPENSE, INCOME, INVESTMENT, LIABILITY, LOAN, ROOT, SECURITY

# ######################################################################################################################
# ######################################################################################################################

if moneydance_data is None: raise Exception("ERROR - No MD data exists - aborting")

if use_side_bar_selected_account:
    contextAccount = moneydance_ui.firstMainFrame.getSelectedAccount()  # This takes the selected account on the sidebar. Set to a specific account if you like
else:
    if acct is None:
        raise Exception("Sorry - that account does not exist")

    contextAccount = acct

if (contextAccount is None or contextAccount.getAccountType() == Account.AccountType.ROOT) and not i_want_popups:   # noqa
    raise Exception("ERROR - No account pre-specified and no Account selected in side bar...?!")

if contextAccount is not None:
    print "I will import into Account: % s" %(contextAccount.getFullAccountName())

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


if i_want_popups or fileToImport is None or not os.path.exists(fileToImport):
    if Platform.isOSX():
        System.setProperty("com.apple.macos.use-file-dialog-packages", "true")  # In theory prevents access to app file structure (but doesnt seem to work)
        System.setProperty("apple.awt.fileDialogForDirectories", "false")

    fDialog = FileDialog(None, "Select file for import")
    fDialog.setMultipleMode(False)
    fDialog.setMode(FileDialog.LOAD)
    if fileToImport is None:
        fDialog.setFile("select_your_file")
        fDialog.setDirectory(get_home_dir())
    else:
        fDialog.setFile(fileToImport)
    fDialog.setVisible(True)

    if (fDialog.getFile() is None) or fDialog.getFile() == "":
        raise Exception("User chose to cancel or no file selected >>  So no Import will be performed... ")

    fileToImport = os.path.join(fDialog.getDirectory(), fDialog.getFile())

    if not os.path.exists(fileToImport) or not os.path.isfile(fileToImport):
        raise Exception("IMPORT: Sorry, file selected to import either does not exist or is not a file")

print "I will import from file: %s" %(fileToImport)

fileToImport=File(fileToImport)

# set the parameters
newAccountSet = False           # True Creates a new account set!!! DANGER!!

filename = fileToImport.getName()
extension = os.path.splitext(filename)[1].upper()

wrapper = moneydance_ui.getCurrentAccounts()  # type: AccountBookWrapper
book = moneydance_data

importWasSuccessful = True

dirName = fileToImport.getParent()
try:
    fPath = fileToImport.getAbsolutePath()  # type: str
    fPath = fPath.upper().strip()
    if not moneydance_ui.saveCurrentAccount(): raise Exception("ERROR Save Failed")
    importer = moneydance_ui.getFileImporter(fileToImport)  # type: FileImporter
    if (importer is not None):

        # You can also get/set these, before or after the pre-scan
        # importer.getSpec().setHasSingleTargetAccount(True)                          # True or False
        # importer.getSpec().setDateFieldOrder(dateFieldOrder)                        # One of: ImportDateFieldOrder.MDY, DMY, YMD, YDM, DYM, MYD
        # importer.getSpec().setDecimalChar(decimalChar)                              # '.' or ','
        # importer.getSpec().setDelimiter(delimiter)                                  # e.g. ';'
        # importer.getSpec().setUIProxy(uiProxy)                                      #
        # importer.getSpec().setColumnTypes(columnTypes)                              # [ImportFieldType.CATEGORY, AMOUNT, CHECKNUM etc]
        # importer.getSpec().setFileEncoding(fileEncoding)                            # e.g. 'utf-8'
        # importer.getSpec().setDuplicateDateDiffLimit(duplicateDateDiffLimit)        #
        # importer.getSpec().setShouldMergeTransactions(shouldMergeTransactions)      # True or False
        # importer.getSpec().setShouldConfirmTransactions(shouldConfirmTransactions)  # True or False

        if i_want_popups:
            import_option = JOptionPane.showInputDialog(None,
                                                  "Select Import Type",
                                                  "IMPORT",
                                                  JOptionPane.INFORMATION_MESSAGE,
                                                  moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                  ImportDataSourceType.values(),
                                                  default_import_type)
            if not import_option:
                print "No import option selected"
                raise Exception("No import type selected")

            importer.getSpec().setSourceType(import_option)
        else:
            importer.getSpec().setSourceType(default_import_type)

        importer.getSpec().setTargetAccount(contextAccount)

        # You can also get/set these, before or after the pre-scan
        # importer.getSpec().setHasSingleTargetAccount(True)                          # True or False
        # importer.getSpec().setDateFieldOrder(dateFieldOrder)                        # One of: ImportDateFieldOrder.MDY, DMY, YMD, YDM, DYM, MYD
        # importer.getSpec().setDecimalChar(decimalChar)                              # '.' or ','
        # importer.getSpec().setDelimiter(delimiter)                                  # e.g. ';'
        # importer.getSpec().setUIProxy(uiProxy)                                      #
        # importer.getSpec().setColumnTypes(columnTypes)                              # [ImportFieldType.CATEGORY, AMOUNT, CHECKNUM etc]
        # importer.getSpec().setFileEncoding(fileEncoding)                            # e.g. 'utf-8'
        # importer.getSpec().setDuplicateDateDiffLimit(duplicateDateDiffLimit)        #
        # importer.getSpec().setShouldMergeTransactions(shouldMergeTransactions)      # True or False
        # importer.getSpec().setShouldConfirmTransactions(shouldConfirmTransactions)  # True or False

        fis = FileInputStream(fileToImport)

        if i_want_popups:
            # EITHER CALL THIS FOR THE NORMAL FLOW WITH POPUP SCREENS
            moneydance_ui.doImport(importer, fis)
        else:

            # HEADLESS MODE
            # OR DO THIS BELOW ////
            importer.init(moneydance_data, fis)

            # load/saveSpecFromPreferences() gets/sets these config.dict variables
            # "txtimport_fields"
            # "txtimport_datefmt"
            # "txtimport_csv_delim"

            importer.loadSpecFromPreferences(moneydance_ui.getPreferences())  # Optional - probably not needed if you are setting programmatically
            importer.doPrescan()  # This should be a thread...

            confirmedImport = True

            if i_want_popups:  # I've left this here (effectively disabled) for demo purposes only
                # THESE ARE THE POPUP WINDOWS - BYPASSED....
                if isinstance(importer, TextFileImporter):
                    confirmedImport = TextImport(moneydance_ui, importer).showImportWindow(moneydance_ui.getFirstMainFrame())
                elif isinstance(importer, QIFFileImporter):
                    confirmedImport = QIFImportSettingsWindow(moneydance_ui, moneydance_ui.getFirstMainFrame(), importer).showImportWindow()
                else:
                    confirmedImport = None

            if confirmedImport:
                moneydance_data.setRecalcBalances(False)
                moneydance_ui.setSuspendRefresh(True)
                try:
                    importer.doImport()  # This should be a thread...
                    importer.saveSpecToPreferences(moneydance_ui.getPreferences())  # Optional - probably not needed if you are setting programmatically
                    moneydance_ui.getMain().setCurrentBook(wrapper)
                    moneydance_ui.getMain().saveCurrentAccount()
                except:
                    print "Error during import!"

                finally:
                    moneydance_data.setRecalcBalances(True)
                    moneydance_ui.setSuspendRefresh(False)
            # END OF OPTIONAL SECTION ^^^^

    else:
        book = None
        print "ERROR", fileToImport.getName(), "Unsupported import type"
except:
    print "ERROR: read error."

finally:
    if importWasSuccessful and book is not None:
        print "Imported book: %s root: %s" %(book, book.getRootAccount())
        book.notifyAccountModified(book.getRootAccount())

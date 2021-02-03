#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# demo_calling_import_functions.py - Build: 1
# A basic demo Python (Jython) script to get you started - Stuart Beesley - StuWareSoftSystems - Feb 2021
# Allows you to call the Moneydance Import File function, set parameters, and bypass the popup screens

# Reverse engineered from:
# com.moneydance.apps.md.view.gui.MoneydanceGUI.importFile(fileToImport, newAccountSet=False, contextAccount=moneydance_ui.firstMainFrame.getSelectedAccount())

import os
from java.lang import System
from java.io import File, FileInputStream
from javax.swing import JOptionPane
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

# SET PARAMETERS HERE......!
i_want_popups = False

# default_import_type = ImportDataSourceType.DOWNLOADED
default_import_type = ImportDataSourceType.MIGRATED_FROM_ANOTHER_APP

# Set this if you want to run headless.... or set to =None
# fileToImport=None
fileToImport="/Users/stu/Documents/Moneydance/My Python Scripts/test data/WO_Flag.qif"

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


if i_want_popups or fileToImport is None or fileToImport == "":
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

fileToImport=File(fileToImport)

# set the parameters
newAccountSet = False
contextAccount = moneydance_ui.firstMainFrame.getSelectedAccount()

filename = fileToImport.getName()
extension = os.path.splitext(filename)[1].upper()

if moneydance_data is None: raise Exception("ERROR - No data")
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

        if i_want_popups:
            import_option = JOptionPane.showInputDialog(None,
                                                  "Select Import Type",
                                                  "IMPORT",
                                                  JOptionPane.INFORMATION_MESSAGE,
                                                  moneydance_ui.getIcon("/com/moneydance/apps/md/view/gui/glyphs/appicon_64.png"),
                                                  ImportDataSourceType.values(),
                                                  importer.getSpec().getSourceType())
            if not import_option:
                raise Exception("No import type selected")

            importer.getSpec().setSourceType(import_option)
        else:
            importer.getSpec().setSourceType(default_import_type)

        importer.getSpec().setTargetAccount(contextAccount)

        fis = FileInputStream(fileToImport)

        if i_want_popups:
            # EITHER CALL THIS FOR THE NORMAL FLOW WITH POPUP SCREENS
            moneydance_ui.doImport(importer, fis)
        else:
            # OR DO THIS BELOW ////
            importer.init(moneydance_data, fis)
            importer.loadSpecFromPreferences(moneydance_ui.getPreferences())
            importer.doPrescan()  # This should be a thread...

            confirmedImport = True

            if i_want_popups:
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
                    importer.saveSpecToPreferences(moneydance_ui.getPreferences())
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
    print "ERROR: read error"

finally:
    if importWasSuccessful and book is not None:
        print "Imported book: %s root: %s" %(book, book.getRootAccount())
        book.notifyAccountModified(book.getRootAccount())

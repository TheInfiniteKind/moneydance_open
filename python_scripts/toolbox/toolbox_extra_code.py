#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# toolbox_extra_code.py build: 1003 - Jan 2025 - Stuart Beesley StuWareSoftSystems

# To avoid the dreaded issue below, moving some code here....:
# java.lang.RuntimeException: java.lang.RuntimeException: For unknown reason, too large method code couldn't be resolved

# build: 1000 - NEW SCRIPT
#               Rebuilt all the encrypt/decrypt file to/from Dataset/Sync... Now can access Dropbox Cloud Sync files online too...
# build: 1001 - Show encryption details report added - advanced_show_encryption_keys() ...
# build: 1002 - Relocated advanced_clone_dataset() into here.
# build: 1003 - Added delete all reports/graphs, and reset all inbuilt report/graph parameters to defaults...
###############################################################################
# MIT License
#
# Copyright (c) 2020-2025 Stuart Beesley - StuWareSoftSystems & Infinite Kind (Moneydance)
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

# Just copy these as needed from main script - do not redefine....

# python definitions
global os

# Moneydance definitions
global Account, AccountBookWrapper, AccountBook, Common, GridC, MDIOUtils, StringUtils, DropboxSyncConfigurer
global DateUtil, AccountBookUtil, AccountUtil, AcctFilter, ParentTxn, CurrencySnapshot, CurrencyUtil
global TxnSearch, ReportSpec, MoneydanceSyncableItem, CurrencyType
global CostCalculation, CustomURLStreamHandlerFactory, OnlineTxnMerger, OnlineUpdateTxnsWindow, MoneybotURLStreamHandlerFactory
global OFXConnection, PlaidConnection, StreamTable, Syncer, DownloadedTxnsView, SplitTxn

# Java definitions
global SwingUtilities
global File, FileInputStream, FileOutputStream, IOException, JOptionPane, System, String, Boolean, FilenameFilter
global JList, ListSelectionModel, DefaultListCellRenderer, DefaultListSelectionModel, Color, Desktop
global BorderFactory, JSeparator, DefaultComboBoxModel, SwingWorker, JPanel, GridLayout, JLabel, GridBagLayout, BorderLayout
global Paths, Files, StandardCopyOption, Charset
global AbstractAction, UUID
global JTextField, JCheckBox, ArrayList, HashMap, Collections

# My definitions
global toolbox_frame_
global MD_REF, GlobalVars, debug, myPrint, QuickAbortThisScriptException
global myPopupInformationBox, myPopupAskForInput, getFileFromFileChooser, get_home_dir, myPopupAskQuestion
global invokeMethodByReflection, getFieldByReflection, setFieldByReflection
global MyPopUpDialogBox, logToolboxUpdates, file_chooser_wrapper, dump_sys_error_to_md_console_and_errorlog
global get_sync_folder, pad, rpad, cpad, padTruncateWithDots
global setDisplayStatus, doesUserAcceptDisclaimer, get_time_stamp_as_nice_text
global MyJScrollPaneForJOptionPane, getMDIcon, QuickJFrame
global genericSwingEDTRunner, genericThreadRunner
global getColorBlue, getColorRed, getColorDarkGreen, MoneybotURLDebug
global isKotlinCompiledBuild, convertBufferedSourceToInputStream
global confirm_backup_confirm_disclaimer, backup_local_storage_settings, getNetSyncKeys, play_the_money_sound
global ManuallyCloseAndReloadDataset, perform_qer_quote_loader_check, safeStr, convertStrippedIntDateFormattedText
global count_database_objects, SyncerDebug, calculateMoneydanceDatasetSize, removeEmptyDirs
global isAppDebugEnabledBuild, isKotlinCompiledBuildAll, isMDPlusEnabledBuild, isMDPlusGetPlaidClientEnabledBuild
global isNetWorthUpgradedBuild, isPriceDisplayDecimalsBuild
global MyAcctFilter, StoreAccountList
global getMemorizedReports, safeInvertRate
global CuriousViewInternalSettingsButtonAction, check_if_key_data_string_valid, check_if_key_string_valid
global detect_duplicate_securities

# New definitions
from com.moneydance.apps.md.controller.sync import AbstractSyncFolder, MDSyncCipher
from com.moneydance.apps.md.controller import LocalStorageCipher
from com.moneydance.security import SecretKeyCallback
from com.moneydance.apps.md.controller import MDException
from java.util.zip import ZipOutputStream
from javax.swing import DefaultListModel
from java.lang import InterruptedException
from java.util.concurrent import CancellationException
from java.io import BufferedOutputStream
from java.util import LinkedHashMap

from bisect import bisect_left
from fractions import Fraction

try:
    if GlobalVars.EXTRA_CODE_INITIALISED: raise QuickAbortThisScriptException

    myPrint("DB", "Extra Code Initialiser loading....")

    def _extra_code_initialiser():
        GlobalVars.EXTRA_CODE_INITIALISED = True
        myPrint("B", ">> extra_code script initialised <<")

    def stripReplaceCharacters(inputStr):
        TAB_SYMBOL = "⇥"
        LINEFEED_SYMBOL = "⏎"
        inputStr = inputStr.replace("\t", TAB_SYMBOL)
        inputStr = inputStr.replace("\r\n", LINEFEED_SYMBOL)    # Windows
        inputStr = inputStr.replace("\n", LINEFEED_SYMBOL)      # Unix/macOS
        inputStr = inputStr.replace("\r", LINEFEED_SYMBOL)      # 'old' Mac
        return inputStr

    class CloudDirectoryEntry:
        @staticmethod
        def completePath(sPath): return sPath if (sPath is None or sPath == "" or sPath.endswith("/")) else sPath + "/"  # Assume always need "/" not os.path.sep here...

        def __init__(self, _cloudEntry, _cloudPath, isFolder=False, isFile=False, size=0, _timeStamp=0):
            self.cloudFiles = []                                                                                        # type: [CloudDirectoryEntry]
            self.isCloudFile = isFile
            self.isCloudFolder = isFolder
            self.cloudEntry = _cloudEntry if not self.isCloudFolder else self.completePath(_cloudEntry)
            self.cloudPath = self.completePath(_cloudPath)
            self.fileSize = size
            self.fileTimeStamp = _timeStamp

        def getTimeStampStr(self):
            if self.fileTimeStamp == 0: return ""
            return get_time_stamp_as_nice_text(self.fileTimeStamp)

        def __str__(self):
            timeStr = "" if self.isCloudFolder else " (%s)" %(self.getTimeStampStr())
            return "%s%s" %(self.cloudEntry, timeStr)
        def __repr__(self): return self.__str__()
        def toString(self): return self.__str__()

    def generateTempFileName(forFilename): return str(System.currentTimeMillis()) +  "-" + forFilename

    def makeTempDecryptedFileInDataset(_selectedFile, _subFolder=None):
        if _subFolder is None:
            _tmpDir = Paths.get(MD_REF.getCurrentAccountBook().getRootFolder().getCanonicalPath(), "tmp", "decrypted").toFile()
        else:
            _tmpDir = Paths.get(MD_REF.getCurrentAccountBook().getRootFolder().getCanonicalPath(), "tmp", "decrypted", _subFolder).toFile()
        _tmpDir.mkdirs()
        _copyFileName = File(_selectedFile).getName()
        _tmpFile = File.createTempFile(str(System.currentTimeMillis()), "-" + _copyFileName, _tmpDir)
        _tmpFile.deleteOnExit()
        myPrint("DB", "Created tmp directory/file:", _tmpFile.getCanonicalPath())
        return _tmpFile

    def getSafeFolderAsFileRef(): return File(MD_REF.getCurrentAccountBook().getRootFolder(), AccountBookWrapper.SAFE_SUBFOLDER_NAME)

    def isBadPaddingError(_error):
        errorStr = unicode(_error)
        if "badpadding" in errorStr.lower():
            myPrint("B", "@@ Caught: '%s'" %(errorStr))
            return True
        return False

    def getShowFileOption(_frame, _methodName, _fileName):
        """Gets file open/display options after decrypt. Returns Continue(True), Peek(bool), AttemptOpen(bool)"""

        _options = ["Decrypt(show folder)", "Decrypt(attempt to open)"]

        fileExtension = os.path.splitext(_fileName)[1].lower()
        if fileExtension in ["", ".", ".txt", ".dct", ".mdtxn", ".txn", ".csv", ".text", ".ascii", ".err", ".log"]:
            _options.append("Decrypt/Peek at file(on screen)")

        _selectedOption = JOptionPane.showInputDialog(_frame,
                                                      "Select decrypt option:",
                                                      _methodName,
                                                      JOptionPane.INFORMATION_MESSAGE,
                                                      getMDIcon(lAlwaysGetIcon=True),
                                                      _options,
                                                      None)
        if not _selectedOption:
            txt = "User aborted - aborting!"
            setDisplayStatus(txt, "R")
            myPopupInformationBox(toolbox_frame_, txt, _methodName, theMessageType=JOptionPane.QUESTION_MESSAGE)
            return False, False, False

        _lPeek = "peek" in _selectedOption.lower()
        _lAttemptOpen = "attempt" in _selectedOption.lower()
        return True, _lPeek, _lAttemptOpen


    def advanced_options_encrypt_file_into_dataset():
        _THIS_METHOD_NAME = "ADVANCED: IMPORT/ENCRYPT INTO DATASET"

        theTitle = "Select file to import/encrypt into Dataset/safe/tmp/encrypted dir"
        myPopupInformationBox(toolbox_frame_, theTitle, theTitle=_THIS_METHOD_NAME)

        LS = MD_REF.getCurrentAccountBook().getLocalStorage()

        selectedFile = getFileFromFileChooser(toolbox_frame_,               # Parent frame or None
                                              get_home_dir(),               # Starting path
                                              None,                         # Default Filename
                                              theTitle,                     # Title
                                              False,                        # Multi-file selection mode
                                              True,                         # True for Open/Load, False for Save
                                              True,                         # True = Files, else Dirs
                                              "IMPORT/ENCRYPT",             # Load/Save button text, None for defaults
                                              None,                         # File filter (non Mac only). Example: "txt" or "qif"
                                              lAllowTraversePackages=True,
                                              lForceJFC=False,
                                              lForceFD=True,
                                              lAllowNewFolderButton=True,
                                              lAllowOptionsButton=True)

        if selectedFile is None or selectedFile == "":
            txt = "ALERT: No file selected to import/encrypt..!"
            setDisplayStatus(txt, "R")
            myPopupInformationBox(toolbox_frame_, txt, theTitle=_THIS_METHOD_NAME, theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        if not os.path.exists(selectedFile) or not os.path.isfile(selectedFile):
            txt = "ALERT: File selected to import/encrypt either does not exist or is not a file"
            setDisplayStatus(txt, "R")
            myPopupInformationBox(toolbox_frame_,txt, theTitle=_THIS_METHOD_NAME, theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        try:
            copyFileName = File(selectedFile).getName()
            tmpFile = "tmp" + "/" + "encrypted" + "/" + generateTempFileName(copyFileName)                              # Assume always need "/" not os.path.sep here...
            LS.writeFile(tmpFile, FileInputStream(File(selectedFile)))      # auto closes in/out streams
        except:
            dump_sys_error_to_md_console_and_errorlog()
            txt = "FAILED to import/encrypt file '%s' (review help/console (errorlog.txt))" %(selectedFile)
            setDisplayStatus(txt, "R"); myPrint("B", txt)
            myPopupInformationBox(toolbox_frame_, txt, theTitle=_THIS_METHOD_NAME, theMessageType=JOptionPane.ERROR_MESSAGE)
            return

        myPrint("B", "%s: SUCCESS importing/encrypting file: '%s' into Dataset/tmp/encrypted dir (as: '%s')...!" %(_THIS_METHOD_NAME, selectedFile, tmpFile))

        txt = "File '%s' imported/encrypted into Dataset/tmp/encrypted dir" %(selectedFile)
        setDisplayStatus(txt, "B")
        myPopupInformationBox(toolbox_frame_, txt, theTitle=_THIS_METHOD_NAME, theMessageType=JOptionPane.INFORMATION_MESSAGE)
        try: MD_REF.getPlatformHelper().openDirectory(File(os.path.join(MD_REF.getCurrentAccountBook().getRootFolder().getCanonicalPath(), AccountBookWrapper.SAFE_SUBFOLDER_NAME, tmpFile.replace("/", os.path.sep))))
        except: myPrint("B", "@@ ERROR: - Failed to open file/folder?")

    def advanced_options_encrypt_file_into_sync_folder():
        _THIS_METHOD_NAME = "ADVANCED: IMPORT/ENCRYPT INTO SYNC FOLDER"

        try: syncFolder = MD_REF.getUI().getCurrentAccounts().getSyncFolder()
        except: syncFolder = None
        if syncFolder is None:
            txt = "Syncing not enabled, operation not possible!"
            setDisplayStatus(txt, "R")
            myPopupInformationBox(toolbox_frame_, txt, theTitle=_THIS_METHOD_NAME, theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        theTitle = "Select file to import/encrypt into '%s' Sync/tmp/encrypted folder" %(syncFolder.toString())
        myPopupInformationBox(toolbox_frame_, theTitle, theTitle=_THIS_METHOD_NAME)

        selectedFile = getFileFromFileChooser(toolbox_frame_,     # Parent frame or None
                                              get_home_dir(),     # Starting path
                                              None,               # Default Filename
                                              theTitle,           # Title
                                              False,              # Multi-file selection mode
                                              True,               # True for Open/Load, False for Save
                                              True,               # True = Files, else Dirs
                                              "IMPORT/ENCRYPT",   # Load/Save button text, None for defaults
                                              None,               # File filter (non Mac only). Example: "txt" or "qif"
                                              lAllowTraversePackages=True,
                                              lForceJFC=False,
                                              lForceFD=True,
                                              lAllowNewFolderButton=True,
                                              lAllowOptionsButton=True)

        if selectedFile is None or selectedFile == "":
            txt = "ALERT: No file selected to import/encrypt..!"
            setDisplayStatus(txt, "R")
            myPopupInformationBox(toolbox_frame_, txt, theTitle=_THIS_METHOD_NAME, theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        if not os.path.exists(selectedFile) or not os.path.isfile(selectedFile):
            txt = "ALERT: File selected to import/encrypt either does not exist or is not a file"
            setDisplayStatus(txt, "R")
            myPopupInformationBox(toolbox_frame_, txt, theTitle=_THIS_METHOD_NAME, theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        copyFileName = File(selectedFile).getName()
        tmpFile = generateTempFileName(copyFileName)
        tmpPath = "tmp" + "/" + "encrypted"                                                                             # Assume always need "/" not os.path.sep here...
        tmpFilePath = tmpPath + "/" + tmpFile                                                                           # Assume always need "/" not os.path.sep here...
        try:
            syncFolder.writeFile(tmpFilePath, File(selectedFile))       # No streams to close...
            myPrint("B", "File '%s' encrypted and uploaded to Sync/tmp/encrypted folder (location: '%s') (as: %s)"
                    %(selectedFile, syncFolder.toString(), tmpFilePath))
        except:
            dump_sys_error_to_md_console_and_errorlog()
            txt = "FAILED to import/encrypt file into Sync (review help/console (errorlog.txt))"
            setDisplayStatus(txt, "R"); myPrint("B", txt)
            myPopupInformationBox(toolbox_frame_, txt, theTitle=_THIS_METHOD_NAME, theMessageType=JOptionPane.ERROR_MESSAGE)
            return

        txt = "File encrypted / saved into Sync/tmp/encrypted folder (review help/console (errorlog.txt))"
        setDisplayStatus(txt, "B")
        myPopupInformationBox(toolbox_frame_, txt, theTitle=_THIS_METHOD_NAME)

        lUsingCloudAPI = syncFolder.getSyncTypeID().lower() in ["dropbox_api"]  # ["dropbox_api", "icloud"]

        if lUsingCloudAPI:
            syncFolderOnDiskOrURL = get_sync_folder() + "/" + tmpPath
            myPrint("B", "%s: SUCCESS importing/encrypting file: '%s' into Sync/tmp/encrypted folder ('%s')!" %(_THIS_METHOD_NAME, selectedFile, syncFolderOnDiskOrURL))
            myPopupInformationBox(toolbox_frame_, "Attempting to launch Cloud Sync Folder in Browser (you may have to login)", "OPEN CLOUD SYNC FOLDER")
            MD_REF.showURL(syncFolderOnDiskOrURL)
        else:
            try: syncFolderOnDiskOrURL = os.path.join(get_sync_folder(), tmpFilePath.replace("/", os.path.sep))
            except: syncFolderOnDiskOrURL = "<ERROR DERIVING SYNC FOLDER LOCATION>"

            myPrint("B", "%s: SUCCESS importing/encrypting file: '%s' into Sync/tmp/encrypted folder ('%s')!" %(_THIS_METHOD_NAME, selectedFile, syncFolderOnDiskOrURL))
            try: MD_REF.getPlatformHelper().openDirectory(File(syncFolderOnDiskOrURL))
            except: myPrint("B", "@@ ERROR: - Failed to open file/folder?")

    def advanced_options_decrypt_file_from_dataset():
        _THIS_METHOD_NAME = "ADVANCED: EXTRACT/DECRYPT FROM DATASET"

        myPopupInformationBox(toolbox_frame_,
                              theMessage="Select file from within Dataset's encrypted 'safe'",
                              theTitle=_THIS_METHOD_NAME)

        LS = MD_REF.getCurrentAccountBook().getLocalStorage()
        internalSafeFullPath = os.path.join(MD_REF.getCurrentAccountBook().getRootFolder().getCanonicalPath(), AccountBookWrapper.SAFE_SUBFOLDER_NAME)

        selectedFile = file_chooser_wrapper(_THIS_METHOD_NAME,
                                            internalSafeFullPath,
                                            "Select internal file to extract/decrypt",
                                            "DECRYPT",
                                            True)
        if selectedFile is None: return

        pathStart = Common.ACCOUNT_BOOK_EXTENSION + os.path.sep + AccountBookWrapper.SAFE_SUBFOLDER_NAME + os.path.sep
        searchForSafe = selectedFile.lower().find(pathStart)
        internalDatasetPath = selectedFile[searchForSafe + len(pathStart):].replace(os.path.sep, "/")                   # Assume always need "/" not os.path.sep here...

        if searchForSafe <= 0:
            txt = "ERROR: Selected file must be within Dataset's encrypted 'safe'"
            setDisplayStatus(txt, "R")
            myPopupInformationBox(toolbox_frame_, txt, _THIS_METHOD_NAME, theMessageType=JOptionPane.ERROR_MESSAGE)
            return

        fileRefInSafe = File(getSafeFolderAsFileRef(), internalDatasetPath)
        fileRefSelected = File(selectedFile)
        if (not fileRefInSafe.exists() or not fileRefSelected.exists()
                or not LS.exists(internalDatasetPath)
                or not Files.isSameFile(fileRefInSafe.toPath(), fileRefSelected.toPath())):
            txt = "ERROR: Selected file must exist and be physically located within this Dataset!"
            setDisplayStatus(txt, "R")
            myPopupInformationBox(toolbox_frame_, txt, _THIS_METHOD_NAME, theMessageType=JOptionPane.ERROR_MESSAGE)
            return
        del fileRefInSafe, fileRefSelected

        carryOn, lPeek, lAttemptOpen = getShowFileOption(toolbox_frame_, _THIS_METHOD_NAME, os.path.basename(selectedFile))
        if not carryOn: return

        tmpFile = None
        if not lPeek:
            tmpFile = makeTempDecryptedFileInDataset(selectedFile)

        lCaughtError = False
        lCaughtBadPaddingError = False
        readLines = None

        try:
            if lPeek:
                readLines = MDIOUtils.readlines(LS.readFile(internalDatasetPath))     # This auto-closes in/out streams
            else:
                LS.readFile(internalDatasetPath, FileOutputStream(tmpFile))         # This auto-closes in/out streams
            myPrint("B", "Successfully read from encrypted dataset file....")

        except:
            e_type, exc_value, exc_traceback = sys.exc_info()                                                           # noqa
            if isBadPaddingError(exc_value):
                lCaughtBadPaddingError = True
            else:
                lCaughtError = True

        if lCaughtError:
            dump_sys_error_to_md_console_and_errorlog()
            txt = "FAILED to extract/decrypt file '%s' (review help/console (errorlog.txt))" %(internalDatasetPath)
            setDisplayStatus(txt, "R"); myPrint("B", txt)
            myPopupInformationBox(toolbox_frame_, txt, _THIS_METHOD_NAME, theMessageType=JOptionPane.ERROR_MESSAGE)
            return

        if lCaughtBadPaddingError:
            myPrint("B", "@@ WARNING: file '%s' may have been corrupted. it may be best to delete it >> ERROR(BadPaddingException)!" %(selectedFile))

        if lPeek:

            if lCaughtBadPaddingError:
                txt = "ERROR: BadPaddingException(corrupted) - Cannot peek. Try decrypt option to see good contents (CONSIDER DELETING FILE!)"
                setDisplayStatus(txt, "R")
                myPopupInformationBox(toolbox_frame_, txt, theTitle=_THIS_METHOD_NAME, theMessageType=JOptionPane.ERROR_MESSAGE)
                return

            if readLines is None or len(readLines) < 1:
                txt = "Selected Dataset file '%s' appears to be empty..? Exiting..." %(internalDatasetPath)
                setDisplayStatus(txt, "R")
                myPopupInformationBox(toolbox_frame_, txt, _THIS_METHOD_NAME, theMessageType=JOptionPane.WARNING_MESSAGE)
                return

            myPrint("B", "SUCCESS - Extracted/decrypted file: '%s' from Dataset/safe (ready for peeking)!" %(selectedFile))

            len_lines = sum(len(line) for line in readLines)
            buildString = "\n".join(readLines)

            if debug:
                if "settings" in internalDatasetPath.lower():
                    myPrint("DB", ".... splitting file/text to peek by '&' delimiter for peeking.... (to disable, turn off debug)...")
                    buildString = ("<TEXT HAS BEEN SPLIT BY '&' DELIMITER FOR THIS VIEWING (to disable, turn off debug mode)...>\n\n"
                                   + buildString.replace("&", "&\n"))

            jif = QuickJFrame(_THIS_METHOD_NAME + "(%s lines, %s chars)" %(len(readLines), len_lines), buildString, copyToClipboard=GlobalVars.lCopyAllToClipBoard_TB, lWrapText=False).show_the_frame()

            txt = "Dataset file '%s' extracted/decrypted and shown to user" %(internalDatasetPath)
            setDisplayStatus(txt, "B")
            myPopupInformationBox(jif, txt, theTitle=_THIS_METHOD_NAME)

        else:

            if lCaughtBadPaddingError:
                txt = "ERROR: BadPaddingException(corrupted) - Have extracted/decrypted as much as possible (CONSIDER DELETING FILE!)"
                setDisplayStatus(txt, "R")
                myPopupInformationBox(toolbox_frame_, txt, theTitle=_THIS_METHOD_NAME, theMessageType=JOptionPane.ERROR_MESSAGE)
            else:
                myPrint("B", "SUCCESS - Extracted/decrypted file: '%s' from Dataset/safe and copied to tmp/decrypted dir... !" %(selectedFile))

            txt = "Dataset file '%s' extracted/decrypted and copied to tmp/decrypted dir" %(internalDatasetPath)
            setDisplayStatus(txt, "B")
            myPopupInformationBox(toolbox_frame_, txt, theTitle=_THIS_METHOD_NAME, theMessageType=JOptionPane.INFORMATION_MESSAGE)

            try: MD_REF.getPlatformHelper().openDirectory(tmpFile)
            except: myPrint("B", "@@ ERROR: - Failed to open file/folder?")
            if lAttemptOpen:
                try: Desktop.getDesktop().open(tmpFile)
                except: myPrint("B", "@@ ERROR: - Failed to open file/folder?")

    def advanced_options_decrypt_file_from_sync():
        _THIS_METHOD_NAME = "ADVANCED: EXTRACT/DECRYPT FROM SYNC FOLDER"

        try: syncFolder = MD_REF.getUI().getCurrentAccounts().getSyncFolder()
        except: syncFolder = None
        if syncFolder is None:
            txt = "Syncing not enabled, operation not possible!"
            setDisplayStatus(txt, "R")
            myPopupInformationBox(toolbox_frame_, txt, theTitle=_THIS_METHOD_NAME, theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        syncFolderOnDiskOrURL = get_sync_folder()

        # Not including iCloud as we can (usually) access this directly from disk!
        if syncFolder.getSyncTypeID().lower() in ["dropbox_api"]:       # ["dropbox_api", "icloud"]
            lUsingCloudAPI = True

            class MyJListRenderer(DefaultListCellRenderer):

                def __init__(self):
                    super(DefaultListCellRenderer, self).__init__()                                                     # noqa

                def getListCellRendererComponent(self, thelist, value, index, isSelected, cellHasFocus):
                    lightLightGray = Color(0xDCDCDC)
                    c = super(MyJListRenderer, self).getListCellRendererComponent(thelist, value, index, isSelected, cellHasFocus) # noqa
                    # c.setBackground(self.getBackground() if index % 2 == 0 else lightLightGray)

                    # Create a line separator between accounts
                    c.setBorder(BorderFactory.createMatteBorder(0, 0, 1, 0, lightLightGray))
                    return c

            jlst = JList()
            jlst.setBackground(MD_REF.getUI().getColors().listBackground)
            jlst.setCellRenderer(MyJListRenderer())
            jlst.setFixedCellHeight(jlst.getFixedCellHeight() + 30)
            jlst.setSelectionMode(ListSelectionModel.SINGLE_SELECTION)
            jlst.setModel(DefaultListModel())

            mainPnl = JPanel(BorderLayout())

            topPnl = JPanel(GridBagLayout())
            statusLabel = JLabel("<<scanning cloud / updating directory list>>")
            statusLabel.setForeground(getColorRed())
            topPnl.add(statusLabel, GridC.getc(0, 0).west().insets(5,5,5,5).wx(1.0))

            jsp = MyJScrollPaneForJOptionPane(jlst, 750, 600)

            mainPnl.add(topPnl, BorderLayout.NORTH)
            mainPnl.add(jsp, BorderLayout.CENTER)

            class GetCloudDirectorySwingWorker(SwingWorker):
                def __init__(self, _jlist, _statusLabel):
                    self.jlist = _jlist
                    self.statusLabel = _statusLabel

                def process(self, chunks):              # This executes on the EDT
                    # type: ([CloudDirectoryEntry]) -> None
                    if self.isCancelled(): return
                    model = self.jlist.getModel()
                    for directoryElement in chunks:
                        if isinstance(directoryElement, bool):
                            self.statusLabel.setText("<<DIRECTORY SCAN COMPLETE>>")
                            self.statusLabel.setForeground(getColorBlue())
                        else:
                            self.statusLabel.setText("<<scanning cloud: %s>>" %(directoryElement.cloudPath))
                            model.addElement(directoryElement)

                def doInBackground(self):
                    try:
                        def walkCloudFiles(_syncFolder, sPath, _sw):
                            # type: (AbstractSyncFolder, basestring, SwingWorker) -> None
                            if _sw.isCancelled(): return
                            sPath = CloudDirectoryEntry.completePath(sPath)
                            cloudFiles = _syncFolder.listFiles(sPath)
                            if len(cloudFiles) > 0:
                                for cloudFile in cloudFiles:
                                    if _sw.isCancelled(): return
                                    completePath = CloudDirectoryEntry.completePath(sPath)
                                    completeFilePath = completePath + cloudFile
                                    timeStamp = _syncFolder.getFileTimestamp(completeFilePath)
                                    _sw.super__publish([CloudDirectoryEntry(completeFilePath,
                                                                           completePath,
                                                                           isFolder=False,
                                                                           isFile=True,
                                                                           size=0,
                                                                           _timeStamp=timeStamp)])


                            for cloudFolder in _syncFolder.listSubfolders(sPath):
                                if _sw.isCancelled(): return
                                fullPath = sPath + cloudFolder
                                walkCloudFiles(_syncFolder, fullPath, _sw)

                        MoneybotURLDebug.changeState(False)

                        walkCloudFiles(syncFolder, "", self)

                        MoneybotURLDebug.resetState()

                        self.super__publish([True])
                    except:
                        e_type, exc_value, exc_traceback = sys.exc_info()                                               # noqa
                        if isinstance(exc_value, (InterruptedException, CancellationException)):
                            myPrint("DB", "@@ GetCloudDirectorySwingWorker cancelled / interrupted.. Quitting")
                        else:
                            myPrint("B", "@@ ERROR '%s' Detected within GetCloudDirectorySwingWorker()" %(exc_value))
                            dump_sys_error_to_md_console_and_errorlog()
                        return False
                    myPrint("DB", "GetCloudDirectorySwingWorker.doInBackground() completed...")
                    return True

                def done(self):
                    if False: self.get()                                                                                # noqa

            options = ["EXIT", "DECRYPT"]
            pane = JOptionPane()
            pane.setIcon(getMDIcon(lAlwaysGetIcon=True))
            pane.setMessage(mainPnl)
            pane.setMessageType(JOptionPane.QUESTION_MESSAGE)
            pane.setOptionType(JOptionPane.OK_CANCEL_OPTION)
            pane.setOptions(options)
            dlg = pane.createDialog(toolbox_frame_, _THIS_METHOD_NAME)

            sw = GetCloudDirectorySwingWorker(jlst, statusLabel)
            sw.execute()

            dlg.setVisible(True)

            rtnValue = pane.getValue()
            userAction = -1
            for i in range(0, len(options)):
                if options[i] == rtnValue:
                    userAction = i
                    break

            sw.cancel(True)

            if userAction != 1 or jlst.getSelectedValue() is None:
                txt = "No cloud sync file selected - aborting!"
                setDisplayStatus(txt, "R")
                myPopupInformationBox(toolbox_frame_, txt, _THIS_METHOD_NAME, theMessageType=JOptionPane.WARNING_MESSAGE)
                return

            selectedCloudFileEntry = jlst.getSelectedValue()
            del jsp, userAction, jlst
            myPrint("DB", "USER SELECTED >> CloudFile: %s (timeStamp: %s)" %(selectedCloudFileEntry.cloudEntry, selectedCloudFileEntry.getTimeStampStr()))

            syncSystemPath = selectedCloudFileEntry.cloudEntry
            actualFileName = os.path.basename(syncSystemPath)

        else:
            # todo - NOTE: sometimes the AppleScript file chooser doesn't actually open the iCloud Drive folder? (user has to try again)
            lUsingCloudAPI = False

            if not syncFolderOnDiskOrURL:
                txt = "ALERT: Cannot locate your Sync folder? - Aborting!"
                setDisplayStatus(txt, "R")
                myPopupInformationBox(toolbox_frame_, txt, _THIS_METHOD_NAME, theMessageType=JOptionPane.ERROR_MESSAGE)
                return

            myPrint("DB", "Sync folder location:", syncFolderOnDiskOrURL)

            if syncFolder.getSyncTypeID().lower() in ["icloud"]:
                myPopupInformationBox(toolbox_frame_, "Select file from (%s) Sync folder to extract/decrypt to Dataset/tmp/decrypted/fromSync dir. "
                                                      "<<IF FOLDER DOES NOT APPEAR ABORT & TRY AGAIN>>..." %(syncFolder.getSubpath()))
            else:
                myPopupInformationBox(toolbox_frame_, "Select file from Sync folder to extract/decrypt to Dataset/tmp/decrypted/fromSync dir", theTitle=_THIS_METHOD_NAME)

            selectedFile = file_chooser_wrapper(_THIS_METHOD_NAME,
                                                syncFolderOnDiskOrURL,
                                                "Select Sync file to extract/decrypt",
                                                "EXTRACT",
                                                True)
            if selectedFile is None: return

            if not selectedFile.startswith(syncFolderOnDiskOrURL):
                txt = "ERROR: File to extract/decrypt must be within your Sync folder"
                setDisplayStatus(txt, "R")
                myPopupInformationBox(toolbox_frame_,txt,_THIS_METHOD_NAME, theMessageType=JOptionPane.WARNING_MESSAGE)
                return

            syncSystemPath = selectedFile[len(syncFolderOnDiskOrURL):]
            actualFileName = os.path.basename(syncSystemPath)

            fileRefInSync = File(syncFolderOnDiskOrURL, syncSystemPath)
            fileRefSelected = File(selectedFile)
            if (not fileRefInSync.exists() or not fileRefSelected.exists()
                    or not syncFolder.exists(syncSystemPath)
                    or not Files.isSameFile(fileRefInSync.toPath(), fileRefSelected.toPath())):
                txt = "ERROR: Selected file must exist and be physically located within the Sync system!"
                setDisplayStatus(txt, "R")
                myPopupInformationBox(toolbox_frame_, txt, _THIS_METHOD_NAME, theMessageType=JOptionPane.ERROR_MESSAGE)
                return
            del fileRefInSync, fileRefSelected


        myPrint("DB", "%s: Sync system path: '%s' File: '%s'" %("CloudAPI" if lUsingCloudAPI else "SyncOnDisk", syncSystemPath, actualFileName))

        carryOn, lPeek, lAttemptOpen = getShowFileOption(toolbox_frame_, _THIS_METHOD_NAME, actualFileName)
        if not carryOn: return

        tmpCopyFile = makeTempDecryptedFileInDataset(actualFileName, "fromSync")

        fis = None
        try:
            readLines = None
            try:
                fis = syncFolder.readFile(syncSystemPath)
                if lPeek:
                    readLines = MDIOUtils.readlines(fis)                  # This will close the stream
                else:
                    # syncFolder.writeUnencryptedFile(tmpFilePath, fis)
                    Files.copy(convertBufferedSourceToInputStream(fis), tmpCopyFile.toPath(), [StandardCopyOption.REPLACE_EXISTING])
                myPrint("B", "Successfully read from encrypted sync file....")
            except:
                if fis is not None: fis.close(); fis = None
                fis = syncFolder.readUnencrypted(syncSystemPath)
                if lPeek:
                    readLines = MDIOUtils.readlines(fis)                  # This will close the stream
                else:
                    # syncFolder.writeUnencryptedFile(tmpFilePath, fis)
                    Files.copy(convertBufferedSourceToInputStream(fis), tmpCopyFile.toPath(), [StandardCopyOption.REPLACE_EXISTING])
                myPrint("B", "Successfully read from unencrypted sync file '%s'...." %(syncSystemPath))
        except:
            dump_sys_error_to_md_console_and_errorlog()
            txt = "Failed to extract/decrypt sync file (review help/console (errorlog.txt))... Exiting..."
            setDisplayStatus(txt, "R")
            myPopupInformationBox(toolbox_frame_, txt, _THIS_METHOD_NAME, theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        finally:
            if fis is not None: fis.close()
            tmpCopyFile.deleteOnExit()

        if lPeek:
            if readLines is None or len(readLines) < 1:
                txt = "Selected Sync file appears to be empty..? Exiting..."
                setDisplayStatus(txt, "R")
                myPopupInformationBox(toolbox_frame_, txt, _THIS_METHOD_NAME, theMessageType=JOptionPane.WARNING_MESSAGE)
                return

            len_lines = sum(len(line) for line in readLines)
            buildString = "\n".join(readLines)

            jif = QuickJFrame(_THIS_METHOD_NAME+"(%s lines, %s chars)" %(len(readLines),len_lines), buildString, copyToClipboard=GlobalVars.lCopyAllToClipBoard_TB, lWrapText=False).show_the_frame()
            del buildString

            txt = "Sync file '%s' extracted/decrypted and shown to user" %(syncSystemPath)
            setDisplayStatus(txt, "B")
            myPopupInformationBox(jif, txt)

        else:

            txt = "Sync file '%s' extracted/decrypted to Dataset/tmp/decrypted/fromSync (to: '%s')(review help/console (errorlog.txt))" %(syncSystemPath, tmpCopyFile.getCanonicalPath())
            setDisplayStatus(txt, "B"); myPrint("B", txt)
            myPopupInformationBox(toolbox_frame_, txt, theTitle=_THIS_METHOD_NAME)

            try: MD_REF.getPlatformHelper().openDirectory(tmpCopyFile)
            except: myPrint("B", "@@ ERROR: - Failed to open file/folder?")
            if lAttemptOpen:
                try: Desktop.getDesktop().open(tmpCopyFile)
                except: myPrint("B", "@@ ERROR: - Failed to open file/folder?")

    def advanced_options_decrypt_dataset():
        _THIS_METHOD_NAME = "ADVANCED: EXTRACT/DECRYPT ENTIRE DATASET"

        if not doesUserAcceptDisclaimer(toolbox_frame_, _THIS_METHOD_NAME, "Extract/decrypt entire dataset?"):
            txt = "User declined to continue - aborted"
            setDisplayStatus(txt, "B")
            myPopupInformationBox(toolbox_frame_, txt, _THIS_METHOD_NAME, theMessageType=JOptionPane.ERROR_MESSAGE)
            return

        _theTitle = "Select location to store Extracted/Decrypted dataset... (CANCEL=ABORT)"
        theDir = getFileFromFileChooser(toolbox_frame_,         # Parent frame or None
                                        get_home_dir(),         # Starting path
                                        None,                   # Default Filename
                                        _theTitle,              # Title
                                        False,                  # Multi-file selection mode
                                        True,                   # True for Open/Load, False for Save
                                        False,                  # True = Files, else Dirs
                                        "DECRYPT DATASET",      # Load/Save button text, None for defaults
                                        None,                   # File filter (non Mac only). Example: "txt" or "qif"
                                        lAllowTraversePackages=False,
                                        lForceJFC=False,
                                        lForceFD=False,
                                        lAllowNewFolderButton=True,
                                        lAllowOptionsButton=True)

        if theDir is None or theDir == "":
            txt = "User did not select extraction/decryption folder... Aborting"
            setDisplayStatus(txt, "B")
            myPopupInformationBox(toolbox_frame_, txt, _THIS_METHOD_NAME, JOptionPane.WARNING_MESSAGE)
            return

        if not os.path.exists(theDir):
            txt = "ERROR - the extraction/decryption folder does not exist?"
            myPopupInformationBox(toolbox_frame_, txt, _THIS_METHOD_NAME, JOptionPane.WARNING_MESSAGE)
            return

        decryptionFolder = File(theDir, "decrypted")
        if decryptionFolder.exists():
            txt = "Decrypted sub folder must NOT pre-exist - select another location..... Aborting"
            setDisplayStatus(txt, "R")
            myPopupInformationBox(toolbox_frame_, txt, _THIS_METHOD_NAME, JOptionPane.WARNING_MESSAGE)
            return

        myPrint("B", "Calling save routines before decryption...")
        MD_REF.saveCurrentAccount()
        MD_REF.getCurrentAccountBook().getLocalStorage().save()

        if myPopupAskQuestion(toolbox_frame_, theQuestion="Flush memory to disk(trunk) before starting extraction/decryption?", theTitle=_THIS_METHOD_NAME):
            myPrint("B", "Saving Trunk before extraction/decryption...")
            MD_REF.getCurrentAccountBook().saveTrunkFile()

        decryptionFolder.mkdirs()

        _msgPad = 100
        _msg = pad("Please wait: DECRYPTING", _msgPad, padChar=".")
        diag = MyPopUpDialogBox(toolbox_frame_, theStatus=_msg, theTitle=_msg, lModal=False, OKButtonText="WAIT")
        diag.go()

        myPrint("B", "DECRYPTING ENTIRE DATASET to: '%s'" %(decryptionFolder.getCanonicalPath()))

        wrapper = MD_REF.getUI().getCurrentAccounts()

        invokeMethodByReflection(wrapper, "copyFolderToDecryptedStore", [String, File], ["", decryptionFolder])

        myPrint("B", "FINISHED DECRYPTING ENTIRE DATASET to: '%s'" %(decryptionFolder.getCanonicalPath()))
        diag.kill()

        txt = "ENTIRE DATASET EXTRACTED/DECRYPTED TO %s" %(decryptionFolder.getCanonicalPath())
        setDisplayStatus(txt, "B")
        logToolboxUpdates("advanced_options_decrypt_dataset", txt)
        myPopupInformationBox(toolbox_frame_, txt, _THIS_METHOD_NAME)

        try: MD_REF.getPlatformHelper().openDirectory(decryptionFolder)
        except: pass

    def advanced_show_encryption_keys(justReturnKeys=False):
        _THIS_METHOD_NAME = "ADVANCED: SHOW ENCRYPTION KEYS"

        methodology =\
"""
#################################################################################################################################################################
#################################################################################################################################################################
    
    METHODOLOGY:
    
    The core encryption specification used, along with the Salt, IV, Iteration Count and Key length are the same for dataset('Local Storage') and Sync.
    - AES (aes-128-cbc) >> Advanced Encryption Standard - 128 bit - Cipher Block Chaining (symmetric algorithm)
                        for more details: https://en.wikipedia.org/wiki/Advanced_Encryption_Standard
                                          https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation#Cipher-block_chaining_(CBC)
                                          https://en.wikipedia.org/wiki/Symmetric-key_algorithm
       - Salt - fixed 14-byte value (stored within the Moneydance source code):                 https://en.wikipedia.org/wiki/Salt_(cryptography)
       - Initialization vector (IV) - fixed 16-byte value (within the Moneydance source code):  https://en.wikipedia.org/wiki/Initialization_vector
       - PBE Iteration count: 1024, PBE Key length: 128
       - When deriving the password-based key, dataset uses SHA512 whereas Sync uses SHA1.
    ##################
    INITIALISATION OF NEW DATASET (and therefore a new encryption key):
    Simplistically:  *password >derive> ^password-key >encrypt ~dataset-key> %encrypted-dataset-key >encode hex> @hex-encrypted-dataset-key >store> key file
                     ~dataset-key >encrypt> dataset file(s)
    1. Generate new secure random number (cryptographically strong, non-deterministic, self-seeding, random number generator)
       >> This is the dataset's core cryptographic ~dataset-key used for encryption. This key NEVER changes <<
    2. Obtain the default (internal) 51-character *password (fixed/stored within the Moneydance source code)
    3. Derive the *password based cryptographic ^password-key, using Password-Based Encryption (PBE), with algorithm: "PBKDF2WithHmacSHA512"  (DIFFERENT to B below).
              PBKDF2: Password-Based Key Derivation Function 2:                   https://en.wikipedia.org/wiki/PBKDF2
              HMAC:   keyed-hash message authentication code:                     https://en.wikipedia.org/wiki/HMAC
              SHA-2   (Secure Hash Algorithm 2 - 512 bit digest (hash values):    https://en.wikipedia.org/wiki/SHA-2
              PBE:    with salt, iteration: 1024, key length: 128
    4. Using the default *password derived ^password-key...:
              - encrypt the dataset's core encryption ~dataset-key using algorithm "AES/CBC/PKCS5Padding" with the fixed IV
                  Cipher Block Chaining (symmetric algorithm)
                  PKCS#5 Padding: https://en.wikipedia.org/wiki/Padding_(cryptography)#PKCS#5_and_PKCS#7
                  >> This is the %encrypted-dataset-key <<
       - Encode the %encrypted-dataset-key into @hex-encrypted-dataset-key
       - Store the @hex-encrypted-dataset-key with the "key" field in the plain text 'dataset/key' file and write to disk.
    
    >> The *password can be changed by the user at any time. Once changed, then steps 3 & 4 above are repeated.
       NOTE: The actual ~dataset-key never changes...
    
    >> To decrypt dataset files:
                  - perform step 3 using current *password to derive ^password-key.
                  - then reverse step 4 to obtain the ~dataset-key
                  - then decrypt file(s)
    
    ##################
    SYNC Encryption:
    Simplistically: Uses a simpler approach of +*sync-password >derive> +~sync-key using the same AES, Salt, IV, Iteration count, key length settings
    A. The user always creates the Sync +*sync-password when sync is first setup. NOTE: This is also stored within the dataset.
    B. Derive the +*sync-password based cryptographic +~sync-key, using Password-Based Encryption (PBE), with algorithm: "PBKDF2WithHmacSHA1" (DIFFERENT to 3 above).
              PBKDF2: Password-Based Key Derivation Function 2:
              HMAC:   keyed-hash message authentication code:
              SHA-1   (Secure Hash Algorithm 1 - 160-bit / 20-byte digest (hash values):    https://en.wikipedia.org/wiki/SHA-1
              PBE:    with salt, iteration: 1024, key length: 128
    C. Using the +*sync-password derived +~sync-key...:
              - encrypt sync file using algorithm "AES/CBC/PKCS5Padding" with the fixed IV
                  Cipher Block Chaining (symmetric algorithm)
                  PKCS#5 Padding:
#################################################################################################################################################################
#################################################################################################################################################################
"""

        localKeyHex = syncKeyHex = opensslCmdText = None
        try:
            wrapper = MD_REF.getCurrentAccounts()
            if wrapper is None:
                raise Exception("ERROR: Wrapper is none")

            localKeyHex = StringUtils.encodeHex(getFieldByReflection(getFieldByReflection(wrapper, "cipher"), "secretKey").getEncoded(), False)

            local_pbe_salt_hex = StringUtils.encodeHex(getFieldByReflection(LocalStorageCipher, "pbe_salt"), False)
            local_aes_iv_hex = StringUtils.encodeHex(getFieldByReflection(LocalStorageCipher, "aes_iv"), False)

            sync_pbe_salt_hex = StringUtils.encodeHex(getFieldByReflection(MDSyncCipher, "pbe_salt"), False)
            sync_aes_iv_hex = StringUtils.encodeHex(getFieldByReflection(MDSyncCipher, "aes_iv"), False)

            syncFolder = wrapper.getSyncFolder()
            if syncFolder is not None:
                syncKeyHex = StringUtils.encodeHex(getFieldByReflection(MDSyncCipher.getSyncCipher(wrapper.getSyncEncryptionPassword()), "secretKey").getEncoded(), False)
            del syncFolder, wrapper

            output = "%s:\n" \
                     "%s\n\n" %(_THIS_METHOD_NAME, "-" * len(_THIS_METHOD_NAME))

            output += "CONFIDENTIAL - DO NOT SHARE THIS INFORMATION UNLESS NECESSARY - STORE IN A SECURE LOCATION!\n\n"
            output += "Your dataset's local storage encryption key (hex): '%s'\n" %(localKeyHex)
            output += "- Local storage fixed/internal Salt value (hex):   '%s' IV value (hex): '%s'\n\n" %(local_pbe_salt_hex, local_aes_iv_hex)
            output += "Your sync encryption key (hex):                    '%s'\n" %("SYNC NOT ENABLED" if syncKeyHex is None else syncKeyHex)
            output += "- Sync fixed/internal          Salt value (hex):   '%s' IV value (hex): '%s'\n" %(sync_pbe_salt_hex, sync_aes_iv_hex)
            output += "\n\n"

            opensslCmdText = ""
            opensslCmdText += "Refer: '%s' ... to decrypt files from the command line (example):\n" %("https://wiki.openssl.org/index.php/Enc")
            opensslCmdText += "Dataset files:     openssl enc -aes-128-cbc -d -K %s -iv %s -in encryptedfile.txt -out decryptedfile.txt\n" %(localKeyHex, local_aes_iv_hex)
            opensslCmdText += "Sync folder files: openssl enc -aes-128-cbc -d -K %s -iv %s -in encryptedfile.txt -out decryptedfile.txt\n" %(syncKeyHex, sync_aes_iv_hex)
            output += opensslCmdText

            del local_pbe_salt_hex, local_aes_iv_hex, sync_pbe_salt_hex, sync_aes_iv_hex

            output += "\n\n"

            output += methodology
            output += "\n<END>"
            del methodology


            if not justReturnKeys:
                QuickJFrame(_THIS_METHOD_NAME, output, lAlertLevel=1, copyToClipboard=GlobalVars.lCopyAllToClipBoard_TB, lJumpToEnd=False, lWrapText=False).show_the_frame()
            del output

        except:
            txt = "ERROR getting encryption details !? (review console)"
            setDisplayStatus(txt, "R"); myPrint("B", txt)
            dump_sys_error_to_md_console_and_errorlog()
            if not justReturnKeys:
                myPopupInformationBox(toolbox_frame_, txt, _THIS_METHOD_NAME, JOptionPane.ERROR_MESSAGE)

        return localKeyHex, syncKeyHex, opensslCmdText

    def getDropboxSyncFolderForBasePath(basePath):
        try: from com.moneydance.apps.md.controller.sync import DropboxAPISyncFolder
        except:
            e_type, exc_value, exc_traceback = sys.exc_info()                                                           # noqa
            myPrint("B", "getDropboxSyncFolderForBasePath(): failed to import DropboxAPISyncFolder - INFORM DEVELOPER.... (error: '%s')" %(exc_value))
            return None
        try: syncFolder = MD_REF.getCurrentAccounts().getSyncFolder()
        except: syncFolder = None
        if syncFolder is None:
            myPrint("DB", "getDropboxSyncFolderForBasePath(): syncFolder is None....")
            return None
        # if not isinstance(syncFolder, DropboxAPISyncFolder):
        #     myPrint("DB", "getDropboxSyncFolderForBasePath(): syncFolder is not DropboxAPISyncFolder (found: '%s' / '%s')...." %(type(syncFolder), syncFolder))
        #     return newSyncFolder
        if "DropboxAPI:" not in syncFolder.toString():
            myPrint("DB", "getDropboxSyncFolderForBasePath(): syncFolder doe not appear to be 'DropboxAPI:' (found: '%s' / '%s')...." %(type(syncFolder), syncFolder))
            return None

        syncMethod = get_sync_folder(lReturnSyncMethod=True)
        if not isinstance(syncMethod, DropboxSyncConfigurer):
            myPrint("DB", "getDropboxSyncFolderForBasePath(): syncMethod is not 'DropboxSyncConfigurer' (found: '%s')...." %(type(syncMethod)))
            return None

        if not invokeMethodByReflection(syncMethod, "linkAccount", [Boolean.TYPE], [False]) or not syncMethod.isConnected():
            myPrint("DB", "getDropboxSyncFolderForBasePath(): failed to call .linkAccount() (connected: %s)" %(syncMethod.isConnected()))
            return None

        try:
            dbClient = getFieldByReflection(syncMethod, "dropbox")
            if dbClient is None:
                myPrint("B", "getDropboxSyncFolderForBasePath(): Logic error: dbClient is None....")
                return None
            newSyncFolder = DropboxAPISyncFolder(dbClient, basePath)
        except:
            e_type, exc_value, exc_traceback = sys.exc_info()                                                           # noqa
            myPrint("B", "getDropboxSyncFolderForBasePath(): Error calling DropboxAPISyncFolder() - INFORM DEVELOPER.... (error: '%s')" %(exc_value))
            return None

        myPrint("DB", "getDropboxSyncFolderForBasePath(): Obtained new DropboxAPISyncFolder(): %s" %(newSyncFolder))
        return newSyncFolder

    def advanced_options_force_reset_sync_settings():
        # Resets all Sync settings, generates a new Sync ID, Turns Sync Off. You can turn it back on later....

        _THIS_METHOD_NAME = "ADVANCED: FORCE RESET SYNC SETTINGS"

        storage = MD_REF.getCurrentAccountBook().getLocalStorage()

        if not confirm_backup_confirm_disclaimer(toolbox_frame_, _THIS_METHOD_NAME, "Force reset all Sync settings, generate new SyncID & disable Sync?"):
            return

        if not backup_local_storage_settings():
            txt = "%s: ERROR making backup of LocalStorage() ./safe/settings - no changes made!" %(_THIS_METHOD_NAME)
            setDisplayStatus(txt, "R")
            myPopupInformationBox(toolbox_frame_, txt, theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        SYNC_KEYS = getNetSyncKeys()

        for skey in SYNC_KEYS: storage.remove(skey)

        # Copied from: com.moneydance.apps.md.controller.AccountBookWrapper.resetSyncInfoIfNecessary()
        storage.put("netsync.dropbox.fileid", UUID.randomUUID())

        # NOTE: as of 2022.3(4063) - this is also performed: .setIsMasterSyncNode(True)
        MD_REF.getUI().getCurrentAccounts().setIsMasterSyncNode(True)
        storage.save()

        root = MD_REF.getCurrentAccountBook().getRootAccount()
        if root is not None:
            root.setEditingMode()
            for skey in SYNC_KEYS: root.removeParameter(skey)
            root.syncItem()

        txt = "ALL SYNC SETTINGS HAVE BEEN RESET - MONEYDANCE WILL NOW RESTART"
        setDisplayStatus(txt, "R"); myPrint("B", txt)
        logToolboxUpdates("advanced_options_force_reset_sync_settings", txt)
        play_the_money_sound()
        myPopupInformationBox(toolbox_frame_, txt, theMessageType=JOptionPane.WARNING_MESSAGE)

        ManuallyCloseAndReloadDataset.moneydanceExitOrRestart(lRestart=True)

    def advanced_clone_dataset():
        """This feature clones the open dataset. It takes a backup, restores the backup, wipes sync, removes transactional data.
        It deletes txns, price history, attachments from the clone (rather than recreating a new structure. The next evolution
        of this function will allow recreation of balances and cutoff dates"""

        _THIS_METHOD_NAME = "Clone Dataset".upper()
        PARAMETER_KEY = "toolbox_clone_dataset"

        output = "%s:\n" \
                 "%s\n\n" %(_THIS_METHOD_NAME, ("-" * (len(_THIS_METHOD_NAME)+1)))

        # Refer:
        # com.moneydance.apps.md.view.gui.MoneydanceGUI.saveToBackup(SecondaryFrame) : void
        # com.moneydance.apps.md.view.gui.MoneydanceGUI.openBackup(Frame) : boolean

        currentBook = MD_REF.getCurrentAccountBook()                                                                    # type: AccountBook
        if currentBook is None:
            myPopupInformationBox(toolbox_frame_, "ERROR: AccountBook is missing?",theTitle="ERROR",theMessageType=JOptionPane.ERROR_MESSAGE)
            return

        if not perform_qer_quote_loader_check(toolbox_frame_, _THIS_METHOD_NAME): return

        MD_decimal = MD_REF.getPreferences().getDecimalChar()

        currentName = currentBook.getName().strip()

        fCurrentFilePath = MD_REF.getCurrentAccountBook().getRootFolder()
        currentFilePath = fCurrentFilePath.getCanonicalPath()

        # newName = AccountBook.stripNonFilenameSafeCharacters(currentName+"_CLONE_%s" %(System.currentTimeMillis()))
        newName = AccountBook.stripNonFilenameSafeCharacters(currentName+"_CLONE")

        lbl_cloneName = JLabel("Enter the name for the cloned dataset:")
        user_cloneName = JTextField(newName)

        user_zeroAcctOpeningBalances = JCheckBox("Zero all account opening balances?", True)
        user_zeroAcctOpeningBalances.setToolTipText("When enabled, will reset account initial/opening balances to zero")

        user_purgeAllTransactions = JCheckBox("Purge all transactions?", True)
        user_purgeAllTransactions.setToolTipText("When enabled, purges all transactions from the clone")

        user_purgeSnapHistory = JCheckBox("Purge all security price & currency rate history (keep current and most recent one)?", True)
        user_purgeSnapHistory.setToolTipText("When enabled, purges security price & currency rate history (leaving current price/rate and most recent price/rate)")

        filterPanel = JPanel(GridLayout(0, 1))
        filterPanel.add(lbl_cloneName)
        filterPanel.add(user_cloneName)
        filterPanel.add(JLabel(""))
        filterPanel.add(user_zeroAcctOpeningBalances)
        filterPanel.add(user_purgeAllTransactions)
        filterPanel.add(user_purgeSnapHistory)

        _options = ["Cancel", "CLONE"]

        while True:
            jsp_acd = MyJScrollPaneForJOptionPane(filterPanel,850, 175)

            userAction = JOptionPane.showOptionDialog(toolbox_frame_,
                                                      jsp_acd,
                                                      "%s: Select CLONE Options:" %(_THIS_METHOD_NAME.upper()),
                                                      JOptionPane.OK_CANCEL_OPTION,
                                                      JOptionPane.QUESTION_MESSAGE,
                                                      getMDIcon(None),
                                                      _options,
                                                      _options[0])

            if userAction < 1:
                txt = "%s: User did not select clone options - no changes made" %(_THIS_METHOD_NAME)
                setDisplayStatus(txt, "R")
                myPopupInformationBox(toolbox_frame_,txt)
                return

            # userRequestedNewName = myPopupAskForInput(toolbox_frame_,
            #                                           theTitle=_THIS_METHOD_NAME,
            #                                           theFieldLabel="CLONED DATASET NAME:",
            #                                           theFieldDescription="Enter a new name for the cloned dataset",
            #                                           defaultValue=newName)
            #
            # if userRequestedNewName is None or userRequestedNewName == "":
            #     txt = "No name entered for cloned dataset - no changes made"
            #     myPopupInformationBox(toolbox_frame_,txt)
            #     setDisplayStatus(txt, "R")
            #     return

            newName = AccountBook.stripNonFilenameSafeCharacters(user_cloneName.getText())
            newNamePath = os.path.join(os.path.dirname(currentFilePath),newName + Common.ACCOUNT_BOOK_EXTENSION)
            fNewNamePath = File(newNamePath)

            if newName is None or newName == "" or fNewNamePath.exists():
                myPopupInformationBox(toolbox_frame_, "ERROR: new cloned file name: '%s' invalid or already exists?" %(newName),theTitle="ERROR",theMessageType=JOptionPane.ERROR_MESSAGE)
                continue

            if not user_zeroAcctOpeningBalances.isSelected() and not user_purgeAllTransactions.isSelected() and not user_purgeSnapHistory.isSelected():
                myPopupInformationBox(toolbox_frame_, "ERROR: Nothing selected to remove whilst cloning (pointless!)?",theTitle="ERROR",theMessageType=JOptionPane.ERROR_MESSAGE)
                continue

            break

        if not doesUserAcceptDisclaimer(toolbox_frame_, _THIS_METHOD_NAME, "Are you really sure you want to create a clone of current dataset?"):
            txt = "%s: User declined the disclaimer - no changes made...." %(_THIS_METHOD_NAME)
            setDisplayStatus(txt, "R")
            myPopupInformationBox(toolbox_frame_,txt,theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        # lKeepBalances = True
        # keepTxnsAfterDate = None
        lZeroOpeningBalances = user_zeroAcctOpeningBalances.isSelected()
        lRemoveAllTxns = user_purgeAllTransactions.isSelected()
        lRemoveAllSnapHistory = user_purgeSnapHistory.isSelected()

        output += "CLONE PROCESSING OPTIONS:\n" \
                  " ------------------------\n"
        output += "Purge all transactions:                           %s\n" %(lRemoveAllTxns)
        output += "Zero all accounts' opening balances:              %s\n" %(lZeroOpeningBalances)
        output += "Purge all security price & currency rate history: %s\n" %(lRemoveAllSnapHistory)
        output += "\n"

        _msgPad = 100
        _msg = pad("Please wait:",_msgPad,padChar=".")
        diag = MyPopUpDialogBox(toolbox_frame_, theStatus=_msg, theTitle=_msg, lModal=False, OKButtonText="WAIT")
        diag.go()

        try:
            output += "Current dataset file path:    %s\n" %(fCurrentFilePath.getCanonicalPath())
            output += "New cloned dataset file path: %s\n" %(fNewNamePath.getCanonicalPath())

            tmpFile = File.createTempFile("toolbox_%s" %(System.currentTimeMillis()), ".moneydancearchive")
            tmpFile.deleteOnExit()

            MD_REF.saveCurrentAccount()           # Flush any current txns in memory and start a new sync record..

            output += "Saving current dataset back to disk (trunk)\n"
            currentBook.saveTrunkFile()    # Save dataset too before backup


            class MyFilenameFilter(FilenameFilter):
                def accept(self, thedirname, thefilename):

                    keepDirs = ["attach"]
                    ignoreFiles = ["processed.dct"]
                    ignoreExtns = [".txn", ".txn-tmp", ".mdtxn", ".mdtxnarchive"]

                    for keepDir in keepDirs:
                        if thedirname.getPath().endswith(keepDir):
                            return True

                    for ignoreExt in ignoreExtns:
                        if thefilename.endswith(ignoreExt): return False

                    for ignoreFile in ignoreFiles:
                        if thefilename == ignoreFile: return False
                    return True

            _msg = pad("Please wait: Creating a temporary backup",_msgPad,padChar=".")
            diag.updateMessages(newTitle=_msg, newStatus=_msg)
            try:
                zipOut = ZipOutputStream(BufferedOutputStream(FileOutputStream(tmpFile), 65536))   # type: ZipOutputStream
                MDIOUtils.zipRecursively(zipOut, currentBook.getRootFolder(), MyFilenameFilter())
                zipOut.close()
                output += "Current dataset backed up to: %s (stripping out txn and archive files)\n" %(tmpFile)
            except:
                myPopupInformationBox(toolbox_frame_, "ERROR: could not create temporary backup (review console)",theTitle="ERROR",theMessageType=JOptionPane.ERROR_MESSAGE)
                output += dump_sys_error_to_md_console_and_errorlog(True)
                raise

            passphrase = MD_REF.getUI().getCurrentAccounts().getEncryptionKey()
            if passphrase and passphrase != "":
                output += "Your encryption passphrase: '%s' will be reused in the cloned dataset\n" %(passphrase)
            else:
                output += "No user encryption passphrase will be set in the clone\n"

            class MySecretKeyCallback(SecretKeyCallback):
                def __init__(self, passPhrase):
                    self.passPhrase = passPhrase

                def setVerifier(self, paramSecretKeyVerifier): pass

                def getPassphrase(self, hint):                                                                          # noqa
                    return self.passPhrase

                def getPassphrase(self, dataName, hint):                                                                # noqa
                    return self.passPhrase

            passwordCallback = MySecretKeyCallback(passphrase)

            # try:
            class MyFilenameFilter(FilenameFilter):
                def accept(self, dirname, filename):                                                                    # noqa
                    if filename.endswith(Common.ACCOUNT_BOOK_EXTENSION):
                        return True
                    return False

            _msg = pad("Please wait: Restoring temporary backup to clone new dataset",_msgPad,padChar=".")
            diag.updateMessages(newTitle=_msg, newStatus=_msg)

            tmpFolder = MDIOUtils.createTempFolder()
            output += "Created temporary folder (for restore): %s\n" %(tmpFolder)
            MDIOUtils.openZip(tmpFile, tmpFolder.getAbsolutePath())
            output += "Unzipped temporary backup into: %s\n" %(tmpFolder)
            zipContents = tmpFolder.list(MyFilenameFilter())
            if zipContents is None or len(zipContents) < 1: raise Exception("ERROR: Zip file seems incorrect")
            tmpMDFile = File(tmpFolder, zipContents[0])

            newBookFile = fNewNamePath
            if not tmpMDFile.renameTo(newBookFile):
                MDIOUtils.copyFolder(tmpMDFile, newBookFile)
                output += "Renamed restored dataset to: %s\n" %(newBookFile)

            newWrapper = AccountBookWrapper.wrapperForFolder(newBookFile)   # type: AccountBookWrapper
            if newWrapper is None: raise Exception("ERROR: 'AccountBookWrapper.wrapperForFolder' returned None")
            output += "Successfully obtained 'wrapper' for: %s\n" %(newBookFile)

            newWrapper.setUUIDResetFlag(True)

            _msg = pad("Please wait: Opening cloned dataset",_msgPad,padChar=".")
            diag.updateMessages(newTitle=_msg, newStatus=_msg)

            try:
                if not newWrapper.loadLocalStorage(passwordCallback): raise Exception("ERROR: calling 'newWrapper.loadLocalStorage()'")
                output += "Successfully loaded Clone's local storage \n"

                if not newWrapper.loadDataModel(passwordCallback): raise Exception("ERROR: calling 'newWrapper.loadDataModel()'")
                output += "Successfully loaded Clone's data model \n"

                newBook = newWrapper.getBook()
                if newBook is None: raise Exception("ERROR: 'AccountBook' is None")
                output += "Successfully obtained Clone's AccountBook reference\n"

                if MD_REF.getBuild() > 5153:  # MD2024.2 - the dataset loading methods were tweaked..!
                    newBook.setFinishedInitialLoad(True)
                    newBook.performPostLoadVerification()

                    newRoot = newBook.getRootAccountNullable()
                    if newRoot is None: raise Exception("ERROR: 'root' is None")
                    output += "Successfully obtained Clone's (nullable) 'root' reference\n"

                newBookSyncer = newBook.getSyncer()
                if newBookSyncer is None: raise Exception("ERROR: cloned dataset's 'Syncer' is None")
                output += "Clone's 'Syncer' is running (%s)\n" %(newBookSyncer)

            except MDException as mde:
                if mde.getCode() == 1004:
                    MD_REF.getUI().showErrorMessage("ERROR: The dataset's password is incorrect!?  Failed to open clone?")
                    raise
                else:
                    dump_sys_error_to_md_console_and_errorlog()
                    raise

            cloneTime = System.currentTimeMillis()
            newRoot = newBook.getRootAccount()

            newRoot.setParameter(PARAMETER_KEY, safeStr(cloneTime))
            newRoot.setComment("This dataset was cloned by the Toolbox extension on: %s (%s)"
                               %(convertStrippedIntDateFormattedText(DateUtil.getStrippedDateInt()), cloneTime))
            if newRoot.getAccountName().strip() != newBook.getName():
                output += "Updating new root's account name to: '%s'\n" %(newBook.getName())
                newRoot.setAccountName(newBook.getName())
            newBook.logModifiedItem(newRoot)

            if not AccountBookUtil.isWithinInternalStorage(newBook):
                AccountBookUtil.registerExternalAccountBook(newBook)
                output += "Registered cloned dataset with the File/Open menu list\n"

            _msg = pad("Please wait: Resetting Sync in cloned dataset..",_msgPad,padChar=".")
            diag.updateMessages(newTitle=_msg, newStatus=_msg)

            SYNC_KEYS = getNetSyncKeys()

            newStorage = newBook.getLocalStorage()
            for skey in SYNC_KEYS: newStorage.remove(skey)                                                              # noqa
            newStorage.put("netsync.dropbox.fileid", UUID.randomUUID())
            newStorage.put("_is_master_node", True)
            newStorage.put(PARAMETER_KEY, safeStr(cloneTime))
            newStorage.save()
            if newRoot is not None:
                newRoot.setEditingMode()
                for skey in SYNC_KEYS: newRoot.removeParameter(skey)
                newBook.logModifiedItem(newRoot)

            output += "Clone's Sync settings have been reset and the internal UUID set to: '%s'\n" %(newStorage.getStr("netsync.dropbox.fileid","<ERROR>"))

            output += "Imported and created clone book: %s\n" %(newBookFile.getCanonicalPath())
            # newBook.notifyAccountModified(newBook.getRootAccount())
            MD_REF.getUI().updateOpenFilesMenus()
            output += "Updated 'open files' menu...\n"

            if lZeroOpeningBalances:
                _msg = pad("Please wait: Zeroing account opening/initial balances..",_msgPad,padChar=".")
                diag.updateMessages(newTitle=_msg, newStatus=_msg)

                allAccounts = AccountUtil.allMatchesForSearch(newBook, AcctFilter.ALL_ACCOUNTS_FILTER)
                for acct in allAccounts:

                    lChangedBal = False
                    if not isKotlinCompiledBuild():     # Pre MD2023 there was only start balance (no adjustment balance)
                        xbal = acct.getStartBalance()
                        if xbal != 0:
                            rCurr = acct.getCurrencyType()
                            output += "Setting account's initial / opening balance to zero (was: %s): %s\n" %(rCurr.formatFancy(xbal, MD_decimal), acct)
                            acct.setStartBalance(0)
                            lChangedBal = True
                    else:
                        xbal = acct.getUnadjustedStartBalance()
                        if xbal != 0:
                            rCurr = acct.getCurrencyType()
                            output += "Setting account's unadjusted initial / opening balance to zero (was: %s): %s\n" %(rCurr.formatFancy(xbal, MD_decimal), acct)
                            acct.setStartBalance(0)
                            lChangedBal = True
                        xbal = acct.getBalanceAdjustment()
                        if xbal != 0:
                            rCurr = acct.getCurrencyType()
                            output += "Setting account's balance adjustment to zero (was: %s): %s\n" %(rCurr.formatFancy(xbal, MD_decimal), acct)
                            acct.setBalanceAdjustment(0)
                            lChangedBal = True

                    if lChangedBal:
                        SyncerDebug.changeState(debug)
                        newBook.logModifiedItem(acct)
                        SyncerDebug.resetState()
                        # acct.syncItem()

            # noinspection PyArgumentList
            class MyCloneTxnSearchFilter(TxnSearch):

                # def __init__(self,dateStart,dateEnd):
                #     self.dateStart = dateStart
                #     self.dateEnd = dateEnd

                def matchesAll(self):                                                                                           # noqa
                    return False

                def matches(self, _txn):
                    if not isinstance(_txn, ParentTxn): return False
                    return True
                    #
                    # if txn.getDateInt() >= self.dateStart and txn.getDateInt() <= self.dateEnd:                                 # noqa
                    #     return True
                    # return False


            if lRemoveAllTxns:
                newBook.setRecalcBalances(False)

                _msg = pad("Please wait: Deleting txns/attachments (as necessary)..",_msgPad,padChar=".")
                diag.updateMessages(newTitle=_msg, newStatus=_msg)

                startTimeMs = System.currentTimeMillis()
                attachmentsToDelete = []
                ts = newBook.getTransactionSet().getTransactions(MyCloneTxnSearchFilter())
                output += "Removing all (%s) transactions from clone...\n" %(ts.getSize())
                for txn in ts:
                    if not isinstance(txn, ParentTxn):
                        myPrint("B",txn.getSyncInfo().toMultilineHumanReadableString())
                        raise Exception("ERROR: Should not delete splits!")
                    if txn.hasAttachments():
                        for attachKey in txn.getAttachmentKeys():
                            attachTag = txn.getAttachmentTag(attachKey)
                            attachmentsToDelete.append(attachTag)
                tsList = ArrayList()
                ts.copyInto(tsList)

                SyncerDebug.changeState(debug)
                if not newBook.logRemovedItems(tsList): raise Exception("ERROR: newBook.logRemovedItems(tsList) returned false?")
                SyncerDebug.resetState()

                if len(attachmentsToDelete):
                    output += "Deleting %s attachments from clone...\n" %(len(attachmentsToDelete))
                    for attachment in attachmentsToDelete:
                        fAttachFile = File(attachment)
                        if fAttachFile.exists():
                            fAttachFile.delete()

                    if removeEmptyDirs(os.path.join(newBook.getRootFolder().getCanonicalPath(), AccountBookWrapper.SAFE_SUBFOLDER_NAME)):
                        output += "Successfully removed empty attachment folders...\n"
                    else:
                        output += "Error whilst removing empty attachment folders... (ignoring and continuing)\n"

                output += "Mass delete of %s txns and %s attachments took: %s seconds\n" %(ts.getSize(), len(attachmentsToDelete), (System.currentTimeMillis() - startTimeMs) / 1000.0)

            if lRemoveAllSnapHistory:
                startTimeMs = System.currentTimeMillis()

                _msg = pad("Please wait: Purging security price / currency rate history..",_msgPad,padChar=".")
                diag.updateMessages(newTitle=_msg, newStatus=_msg)

                keepSnaps = []

                allCurrencies = newBook.getCurrencies().getAllCurrencies()
                allSnaps = newBook.getItemsWithType(CurrencySnapshot.SYNCABLE_TYPE_VALUE)

                iCountSecurities = iCountCurrencies = 0

                for curSec in allCurrencies:
                    if curSec.getCurrencyType() == CurrencyType.Type.SECURITY: iCountSecurities += 1                    # noqa
                    if curSec.getCurrencyType() == CurrencyType.Type.CURRENCY: iCountCurrencies += 1                    # noqa
                    secSnapshots = curSec.getSnapshots()
                    if len(secSnapshots) > 0: keepSnaps.append(secSnapshots[-1])

                output += "Currency rate / Security price history ('csnaps') before purge: %s (%s currencies, %s securities)\n"\
                          %(allSnaps.size(), iCountCurrencies, iCountSecurities)

                for snap in keepSnaps: allSnaps.remove(snap)

                output += "Price history - keeping: %s 'csnaps', deleting: %s 'csnaps'\n" %(len(keepSnaps), allSnaps.size())

                SyncerDebug.changeState(debug)
                if not newBook.logRemovedItems(allSnaps): raise Exception("ERROR: newBook.logRemovedItems(allSnaps) returned false?")
                SyncerDebug.resetState()

                output += "Mass delete of %s currency rate / security price history 'csnaps' took: %s seconds\n"\
                          %(allSnaps.size(), (System.currentTimeMillis() - startTimeMs) / 1000.0)

            newBook.setRecalcBalances(True)

            if not newBook.save(): raise Exception("ERROR: cloned AccountBook .save() returned false")

            # myPrint("B", "Syncer: %s, isSyncing: %s, isRunningInBackground: %s" %(newBookSyncer, newBookSyncer.isSyncing(), newBookSyncer.isRunningInBackground()))
            newBookSyncer.stopSyncing()
            output += "Cloned dataset's 'Syncer' has been shut down (flushing remaining in-memory changes)\n"

            # register attachment for deletion etc
            # delete all txn files afterwards

            # newBook.saveTrunkFile()
            newBookSyncer.saveNewTrunkFile(True)
            output += "Cloned dataset has been re-saved to disk (as a new trunk file)\n"

            # Copied from com.infinitekind.tiksync.Syncer
            OUTGOING_PATH = "tiksync/out"
            INCOMING_PATH = "tiksync/in"
            TXN_FILE_EXTENSION = ".txn"
            TXN_FILE_EXTENSION_TMP = ".txn-tmp"
            OUTGOING_TXN_FILE_EXTENSION = ".mdtxn"
            PROCESSED_FILES = "tiksync/processed.dct"
            newStorage.delete(PROCESSED_FILES)
            for mdDir in [OUTGOING_PATH, INCOMING_PATH]:
                for filename in newStorage.listFiles(mdDir):
                    if (filename.endswith(TXN_FILE_EXTENSION_TMP)
                            or filename.endswith(OUTGOING_TXN_FILE_EXTENSION)
                            or filename.endswith(TXN_FILE_EXTENSION)):
                        newStorage.delete(mdDir + "/" + filename)
            output += "Deleted clone's 'processed.dct' and all .txn type files.....\n"

            output += "\n\n" \
                      " ------------------------------------------------------------------------------------------------\n"
            output += "Original dataset's object analysis:\n"
            output += count_database_objects()
            fileSize, fileCount = calculateMoneydanceDatasetSize(True)
            output += "...dataset size: %sMB (%s files)\n" %(rpad(fileSize,12),fileCount)
            output += "\n"

            output += "Analysis of objects in cloned dataset:\n"
            output += count_database_objects(newBook)
            fileSize, fileCount = calculateMoneydanceDatasetSize(True, whichBook=newBook)
            output += "...dataset size: %sMB (%s files)\n" %(rpad(fileSize,12),fileCount)
            output += " ------------------------------------------------------------------------------------------------\n"
            output += "\n"

            txt = "DATASET '%s' WAS CREATED FROM A CLONE OF '%s'" %(newBook.getName(), currentFilePath)
            myPrint("B", txt)
            logToolboxUpdates("advanced_clone_dataset", txt, book=newBook)

        except:
            txt = "Clone function has failed. Review log and console (CLONE INCOMPLETE)"
            myPrint("B", txt)
            output += "%s\n" %(txt)
            output += dump_sys_error_to_md_console_and_errorlog(True)
            jif = QuickJFrame(title=_THIS_METHOD_NAME, output=output, lAlertLevel=2, copyToClipboard=True, lWrapText=False).show_the_frame()
            myPopupInformationBox(jif,theMessage=txt, theTitle="ERROR",theMessageType=JOptionPane.ERROR_MESSAGE)
            return
        finally:
            diag.kill()

        output += "\n\nCLONE %s SUCCESSFULLY CREATED - USE MENU>FILE>OPEN\n\n" %(newBook.getName())
        output += "<END>"
        jif = QuickJFrame(title=_THIS_METHOD_NAME,output=output,copyToClipboard=True,lWrapText=False).show_the_frame()
        myPopupInformationBox(jif,"Clone dataset: %s created (review output)" %(newBook.getName()))

    def advanced_options_DEBUG(lForceON=False, lForceOFF=False):
        md_debug = MD_REF.DEBUG if (not isAppDebugEnabledBuild()) else AppDebug.DEBUG.isEnabled()                       # noqa
        moneydance_debug_props_key = "moneydance.debug"
        props_debug = Boolean.getBoolean(moneydance_debug_props_key)

        if lForceON:
            toggleText = "ON"
        elif lForceOFF:
            toggleText = "OFF"
        else:
            toggleText = "OFF" if (md_debug or props_debug) else "ON"

            # noinspection PyUnresolvedReferences
            if not isAppDebugEnabledBuild():
                askStr = ("main.DEBUG                             currently set to: %s\n"
                          "System.getProperty('%s') currently set to: %s\n"
                          "Syncer.DEBUG                           currently set to: %s\n"
                          "CustomURLStreamHandlerFactory.DEBUG    currently set to: %s\n"
                          "MoneybotURLStreamHandlerFactory.DEBUG  currently set to: %s\n"
                          "OFXConnection.DEBUG(_MESSAGES)         currently set to: %s\n"
                          "OnlineTxnMerger.DEBUG                  currently set to: %s\n"
                          "PlaidConnection.DEBUG                  currently set to: %s\n"
                          %(md_debug,
                            moneydance_debug_props_key, props_debug,
                            Syncer.DEBUG,                                                                               # noqa
                            CustomURLStreamHandlerFactory.DEBUG,                                                        # noqa
                            MoneybotURLStreamHandlerFactory.DEBUG,                                                      # noqa
                            OFXConnection.DEBUG_MESSAGES,                                                               # noqa
                            OnlineTxnMerger.DEBUG,                                                                      # noqa
                            "n/a" if (not isMDPlusGetPlaidClientEnabledBuild()) else PlaidConnection.DEBUG))            # noqa
            else:
                askStr = ("main.DEBUG                             currently set to: %s\n" 
                          "System.getProperty('%s') currently set to: %s\n"
                          %(md_debug, moneydance_debug_props_key, props_debug))
                for logger in AppDebug.getAllLoggers():                                                                 # noqa
                    askStr += "AppDebug.AppLogger: %s isEnabled: %s  includeInEnableAll: %s\n" %(pad(logger.getId(), 18), pad(str(logger.isEnabled()), 5), pad(str(logger.getIncludeInEnableAll()), 5))

            ask = MyPopUpDialogBox(toolbox_frame_,
                                   "MONEYDANCE DEBUG(s) STATUS:",
                                   askStr,
                                   theTitle="TOGGLE MONEYDANCE INTERNAL DEBUG(s)",
                                   lCancelButton=True,OKButtonText="SET ALL to %s" %toggleText)
            if not ask.go():
                txt = "NO CHANGES MADE TO MONEYDANCE's DEBUG(s)!"
                setDisplayStatus(txt,"B")
                return

            myPrint("B","User requested to change all Moneydance's internal DEBUG mode(s) to %s - flipping these now...!" %(toggleText))

        if toggleText == "OFF":
            newDebugSetting = False
            System.clearProperty(moneydance_debug_props_key)
        else:
            newDebugSetting = True
            System.setProperty(moneydance_debug_props_key, Boolean.toString(newDebugSetting))

        if isAppDebugEnabledBuild():
            # These won't run on all debug loggers! AppDebug.enableAllFlags() / AppDebug.disableAllFlags()
            for logger in AppDebug.getAllLoggers():                                                                     # noqa
                logger.setEnabled(newDebugSetting, True)
        else:
            MD_REF.DEBUG = newDebugSetting
            Syncer.DEBUG = newDebugSetting
            CustomURLStreamHandlerFactory.DEBUG = newDebugSetting
            MoneybotURLStreamHandlerFactory.DEBUG = newDebugSetting
            OFXConnection.DEBUG_MESSAGES = newDebugSetting
            OnlineTxnMerger.DEBUG = newDebugSetting
            if isMDPlusGetPlaidClientEnabledBuild(): PlaidConnection.DEBUG = newDebugSetting

        txt = "All Moneydance internal debug modes turned %s" %(toggleText)

        if lForceON:
            myPrint("DB", txt)
            return

        setDisplayStatus(txt,"B")
        myPopupInformationBox(toolbox_frame_, txt, "TOGGLE MONEYDANCE INTERNAL DEBUG(s)", JOptionPane.WARNING_MESSAGE)

    def advanced_options_other_DEBUG():
        # Also: System.getProperty("ofx.debug.console") - Throws up connection issues in a new file/console...

        debugKeys = ["com.moneydance.apps.md.view.gui.txnreg.DownloadedTxnsView.DEBUG",
                     "com.moneydance.apps.md.view.gui.OnlineUpdateTxnsWindow.DEBUG",
                     "com.infinitekind.util.StreamTable.DEBUG"]

        if isKotlinCompiledBuildAll() and MD_REF.getBuild() < 5100:
            # Before this build, the field is hidden as the class is not public even tho' field is public....
            # After 5100, then AppDebug logger is used for this...
            debugKeys.append("com.infinitekind.moneydance.model.CostCalculation.DEBUG_COST")

        selectedKey = JOptionPane.showInputDialog(toolbox_frame_,
                                                  "Select the DEBUG Setting you want to view/toggle",
                                                  "OTHER DEBUG",
                                                  JOptionPane.INFORMATION_MESSAGE,
                                                  getMDIcon(lAlwaysGetIcon=True),
                                                  debugKeys,
                                                  None)

        if not selectedKey or debugKeys.index(selectedKey) > len(debugKeys):
            txt = "No Debug key was selected to view/toggle.."
            setDisplayStatus(txt, "R")
            return

        if debugKeys.index(selectedKey) == 0:
            currentSetting = DownloadedTxnsView.DEBUG
        elif debugKeys.index(selectedKey) == 1:
            currentSetting = OnlineUpdateTxnsWindow.DEBUG
        elif debugKeys.index(selectedKey) == 2:
            currentSetting = getFieldByReflection(StreamTable, "DEBUG")
        elif debugKeys.index(selectedKey) == 3:
            currentSetting = getFieldByReflection(CostCalculation, "DEBUG_COST")
        else:
            raise Exception("LOGIC ERROR: Unknown selectedKey:", selectedKey)

        ask = MyPopUpDialogBox(toolbox_frame_, "OTHER DEBUG STATUS:",
                               "%s currently set to: %s" %(selectedKey, currentSetting),
                               theTitle="TOGGLE THIS MONEYDANCE INTERNAL OTHER DEBUG",
                               lCancelButton=True,OKButtonText="SET to %s" %(not currentSetting))
        if not ask.go():
            txt = "NO CHANGES MADE TO OTHER DEBUG!"
            setDisplayStatus(txt, "B")
            return

        myPrint("B","User requested to change DEBUG %s to %s - setting now...!" %(selectedKey,not currentSetting))

        if debugKeys.index(selectedKey) == 0:
            DownloadedTxnsView.DEBUG = not currentSetting
        elif debugKeys.index(selectedKey) == 1:
            OnlineUpdateTxnsWindow.DEBUG = not currentSetting
        elif debugKeys.index(selectedKey) == 2:
            setFieldByReflection(StreamTable, "DEBUG", not currentSetting)
        elif debugKeys.index(selectedKey) == 3:
            setFieldByReflection(CostCalculation, "DEBUG_COST", not currentSetting)

        txt = "Moneydance internal debug settings %s turned %s" %(selectedKey, not currentSetting)
        setDisplayStatus(txt, "B")
        myPopupInformationBox(toolbox_frame_, txt, "TOGGLE MONEYDANCE INTERNAL OTHER DEBUG", JOptionPane.WARNING_MESSAGE)


    def advanced_options_edit_parameter_keys():
        if MD_REF.getCurrentAccountBook() is None: return

        if not myPopupAskQuestion(toolbox_frame_,"EDIT OBJs MODE","DANGER - ARE YOU SURE YOU WANT TO VISIT THIS FUNCTION?", theMessageType=JOptionPane.ERROR_MESSAGE):
            txt = "Edit Obj Mode - User declined to proceed - aborting.."
            setDisplayStatus(txt, "R")
            return

        objSelecter = CuriousViewInternalSettingsButtonAction(lOFX=False, EDIT_MODE=True)
        theObject = objSelecter.actionPerformed("")  # type: list
        del objSelecter

        if theObject is None or len(theObject)!= 1:
            # txt = "ADVANCED Edit Obj Mode - No Object selected/found - aborting.."
            # setDisplayStatus(txt, "R")
            return

        theObject = theObject[0]            # type: MoneydanceSyncableItem

        _ADVANCED_KEYADD          = 0
        _ADVANCED_KEYCHG          = 1
        _ADVANCED_KEYDEL          = 2
        _ADVANCED_RECORDDELETE    = 3

        what = [
            "Object ADD    Parameter Key (and data)",
            "Object CHANGE Parameter Key's Data",
            "Object DELETE Parameter Key (and it's data)",
            "DELETE OBJECT - NOT RECOMMENDED!"
        ]

        while True:

            lAdd = lChg = lDel = lDeleteRecord = False

            selectedWhat = JOptionPane.showInputDialog(toolbox_frame_,
                                                       "Select the option for the modification (on %s)?" %(theObject),
                                                       "ADVANCED",
                                                       JOptionPane.WARNING_MESSAGE,
                                                       getMDIcon(None),
                                                       what,
                                                       None)

            if not selectedWhat:
                txt = "ADVANCED - Exiting"
                setDisplayStatus(txt, "B")
                return

            if selectedWhat == what[_ADVANCED_KEYADD]:          lAdd = True
            if selectedWhat == what[_ADVANCED_KEYCHG]:          lChg = True
            if selectedWhat == what[_ADVANCED_KEYDEL]:          lDel = True
            if selectedWhat == what[_ADVANCED_RECORDDELETE]:    lDeleteRecord = True

            text = ""
            if lChg:            text = "ADD"
            if lChg:            text = "CHANGE"
            if lDel:            text = "DELETE"
            if lDeleteRecord:   text = "DELETE OBJECT"

            if lAdd:
                addKey = myPopupAskForInput(toolbox_frame_,
                                            "ADD PARAMETER TO %s" % (theObject),
                                            "PARAMETER:",
                                            "Carefully enter the name of the Parameter you want to add (cAseMaTTers!) - STRINGS ONLY:",
                                            "",
                                            False,
                                            JOptionPane.WARNING_MESSAGE)

                if not addKey or len(addKey.strip()) < 1: continue
                addKey = addKey.strip()

                if not check_if_key_string_valid(addKey):
                    myPopupInformationBox(toolbox_frame_, "ERROR: Parameter %s is NOT valid!" % addKey, "ADD TO %s" %(theObject), JOptionPane.ERROR_MESSAGE)
                    continue    # back to ADVANCED Options menu

                testKeyExists = theObject.getParameter(addKey,None)                                                     # noqa

                if testKeyExists:
                    myPopupInformationBox(toolbox_frame_, "ERROR: Parameter %s already exists - cannot add - aborting..!" %(addKey), "ADD TO %s" %(theObject), JOptionPane.ERROR_MESSAGE)
                    continue    # back to ADVANCED Options menu

                addValue = myPopupAskForInput(toolbox_frame_,
                                              "ADD PARAMETER VALUE TO %s" %(theObject),
                                              "VALUE:",
                                              "Carefully enter the value you want to add (STRINGS ONLY! CaSE MattERS):",
                                              "",
                                              False,
                                              JOptionPane.WARNING_MESSAGE)

                if not addValue or len(addValue.strip()) <1: continue
                addValue = addValue.strip()

                if not check_if_key_data_string_valid(addValue):
                    myPopupInformationBox(toolbox_frame_, "ERROR: Parameter value %s is NOT valid!" %(addValue), "ADD TO %s" %(theObject), JOptionPane.ERROR_MESSAGE)
                    continue    # back to ADVANCED Options menu

                if confirm_backup_confirm_disclaimer(toolbox_frame_, "ADVANCED OPTIONS", "ADD PARAMETER VALUE TO %s" %(theObject)):

                    theObject.setParameter(addKey,addValue)                                                             # noqa
                    if isinstance(theObject, SplitTxn):                                                                 # noqa
                        theObject.getParentTxn().syncItem()                                                             # noqa
                    else:
                        theObject.syncItem()                                                                            # noqa
                    txt = "Parameter: %s Value: %s added to %s @@" %(addKey,addValue,theObject)
                    setDisplayStatus(txt, "R"); myPrint("B", txt)
                    logToolboxUpdates("advanced_options_edit_parameter_keys", txt)
                    play_the_money_sound()
                    myPopupInformationBox(toolbox_frame_,
                                          "SUCCESS: Key %s added to %s!" % (addKey,theObject),
                                          "ADD TO %s" %(theObject),
                                          JOptionPane.WARNING_MESSAGE)
                    continue

                continue

            # DELETE OBJECT  :-<
            if lDeleteRecord:

                output =  "%s PLEASE REVIEW PARAMETER & VALUE BEFORE DELETING OBJECT\n" %(theObject)
                output += " --------------------------------------------------------\n\n"

                if isinstance(theObject, SplitTxn):
                    txt = theObject.getParentTxn().getSyncInfo().toMultilineHumanReadableString()                       # noqa
                else:
                    txt = theObject.getSyncInfo().toMultilineHumanReadableString()                                      # noqa

                output += "\n%s\n" %(txt)

                output += "\n<END>"
                if isinstance(theObject, SplitTxn):
                    jif = QuickJFrame("REVIEW THE SPLIT TXN's DATA BEFORE DELETION (OF THE SPLIT)", output, copyToClipboard=GlobalVars.lCopyAllToClipBoard_TB).show_the_frame()
                elif isinstance(theObject, ParentTxn):
                    jif = QuickJFrame("REVIEW THE PARENT'S TXN DATA BEFORE DELETION (OF THE WHOLE PARENT TXN)", output, copyToClipboard=GlobalVars.lCopyAllToClipBoard_TB).show_the_frame()
                else:
                    jif = QuickJFrame("REVIEW THE OBJECT's DATA BEFORE DELETION", output, copyToClipboard=GlobalVars.lCopyAllToClipBoard_TB).show_the_frame()

                if confirm_backup_confirm_disclaimer(jif, "DELETE OBJECT", "DELETE OBJECT %s" %(theObject)):

                    if isinstance(theObject, SplitTxn):                                                                 # noqa
                        # This will delete the split only; thus we also must sync the parent
                        theObject.deleteItem()                                                                          # noqa
                        theObject.getParentTxn().syncItem()                                                             # noqa
                    else:
                        theObject.deleteItem()                                                                          # noqa

                    txt = "ADVANCED OPTIONS: OBJECT %s DELETED @@" %(theObject)
                    setDisplayStatus(txt, "R"); myPrint("B", txt)
                    logToolboxUpdates("advanced_options_edit_parameter_keys", txt)

                    play_the_money_sound()
                    myPopupInformationBox(jif,
                                          "SUCCESS: OBJECT %s DELETED" %(theObject),
                                          "DELETE OBJECT",
                                          JOptionPane.ERROR_MESSAGE)
                    return

                continue

            # OK, so we are changing or deleting
            if lChg or lDel:

                paramKeys = sorted(theObject.getParameterKeys())                                                        # noqa
                selectedKey = JOptionPane.showInputDialog(toolbox_frame_,
                                                          "Select the %s Parameter you want to %s" % (theObject,text),
                                                          "ADVANCED OPTIONS",
                                                          JOptionPane.WARNING_MESSAGE,
                                                          getMDIcon(None),
                                                          paramKeys,
                                                          None)
                if not selectedKey: continue

                value = theObject.getParameter(selectedKey, None)                                                       # noqa

                output =  "%s PLEASE REVIEW PARAMETER & VALUE BEFORE MAKING CHANGES\n" %(theObject)
                output += " -----------------------------------------------\n\n"

                output += "\n@@ This '%s' key can be changed/deleted by this script @@\n" %(selectedKey)

                output += "\n%s %s\n" %(pad("%s PARAMETER:"%(theObject), 25), selectedKey)
                output += "\n%s %s\n" %(pad("Type:",25), type(value))
                output += "\n%s %s\n" %(pad("Value:",25), value)

                output += "\n<END>"
                jif = QuickJFrame("REVIEW THE KEY BEFORE CHANGES to %s" %(theObject), output, lAutoSize=True, lWrapText=False, copyToClipboard=GlobalVars.lCopyAllToClipBoard_TB).show_the_frame()

                chgValue = None

                if lChg:
                    chgValue = myPopupAskForInput(jif,
                                                  "CHANGE PARAMETER VALUE IN %s" %(theObject),
                                                  "VALUE:",
                                                  "Carefully enter the new value (STRINGS ONLY! CaSE MattERS):",
                                                  value,
                                                  False,
                                                  JOptionPane.WARNING_MESSAGE)

                    if not chgValue or len(chgValue.strip()) <1 or chgValue == value: continue
                    chgValue = chgValue.strip()

                    if not check_if_key_data_string_valid(chgValue):
                        myPopupInformationBox(jif,"ERROR: value %s is NOT valid!" %chgValue,"CHANGE IN %s" %(theObject),JOptionPane.ERROR_MESSAGE)
                        continue    # back to ADVANCED Options menu

                confAction = ""
                if lDel:
                    if isinstance(value, basestring) and value.count('\n') > 10:
                        confAction = "%s key: %s (old value to long to display)" %(text, selectedKey)
                    else:
                        confAction = "%s key: %s (with old value: %s)" %(text, selectedKey, value)
                if lChg:
                    confAction = "%s key: %s to new value: %s" %(text, selectedKey, chgValue)

                if confirm_backup_confirm_disclaimer(jif, "%s VALUE IN %s" %(text, theObject), confAction):

                    if lDel:
                        theObject.setParameter(selectedKey,None)                                                        # noqa

                    if lChg:
                        theObject.setParameter(selectedKey,chgValue)                                                    # noqa

                    if isinstance(theObject, SplitTxn):                                                                 # noqa
                        theObject.getParentTxn().syncItem()                                                             # noqa
                    else:
                        theObject.syncItem()                                                                            # noqa

                    MD_REF.savePreferences()            # Flush all in memory settings to config.dict file on disk
                    play_the_money_sound()

                    if lDel:
                        if isinstance(value, basestring) and value.count('\n') > 10:
                            txt = "Parameter: %s DELETED from %s (old value to long to display) @@" %(selectedKey, theObject)
                            _msgTxt = "SUCCESS: Parameter: %s DELETED from %s (old value to long to display)" %(selectedKey, theObject)
                        else:
                            txt = "Parameter: %s DELETED from %s (old value: %s) @@" %(selectedKey, theObject, value)
                            _msgTxt = "SUCCESS: Parameter: %s DELETED from %s (old value: %s)" %(selectedKey, theObject, value)
                        myPrint("B", txt)
                        logToolboxUpdates("advanced_options_edit_parameter_keys", txt)

                        myPopupInformationBox(jif, _msgTxt, "DELETE IN %s" %(theObject), JOptionPane.WARNING_MESSAGE)

                    if lChg:
                        txt = "Parameter: %s CHANGED to %s in %s @@" %(selectedKey, chgValue, theObject)
                        myPrint("B", txt)
                        logToolboxUpdates("advanced_options_edit_parameter_keys", txt)
                        myPopupInformationBox(jif,
                                              "SUCCESS: Parameter: %s CHANGED to %s in %s" %(selectedKey, chgValue, theObject),
                                              "CHANGE IN %s" %(theObject),
                                              JOptionPane.WARNING_MESSAGE)
                    jif.dispose()       # already within the EDT
                    continue

                jif.dispose()       # already within the EDT
                continue

    def fix_account_start_dates(): return validate_account_start_dates(fix=True)

    def validate_account_start_dates(fix=False):
        if MD_REF.getCurrentAccountBook() is None: return

        if fix:
            _THIS_METHOD_NAME = "FIX: Fix Account 'start dates'..."
        else:
            _THIS_METHOD_NAME = "DIAG: Validate Account 'Start Dates'..."

        if fix:
            if not confirm_backup_confirm_disclaimer(toolbox_frame_, _THIS_METHOD_NAME.upper(), "Fix/repair all invalid account start dates?"):
                return False

        output = "\n" \
                 "%s:\n" \
                 " ======================================================\n\n" %(_THIS_METHOD_NAME.upper())
        if fix:
            output += "Fixes accounts where there is an invalid 'Start Date' (that is not newer than the earliest transactional date)...\n\n\n"
        else:
            output += "Validates that accounts have a valid 'Start Date' that is not newer than the earliest transactional date...\n\n\n"

        output += "%s %s %s %s\n" %(pad("Account Name",50),
                                    pad("Account Type",20),
                                    pad("Start Date",17),
                                    pad("Earliest txn date",17))

        output += "%s %s %s %s\n" %("-"*50,
                                    "-"*20,
                                    "-"*17,
                                    "-"*17)
        output += "\n"

        book = MD_REF.getCurrentAccountBook()
        dateFormatter = MD_REF.getPreferences().getShortDateFormatter()
        creationMap = LinkedHashMap()
        allAccts = AccountUtil.allMatchesForSearch(book, AcctFilter.ALL_ACCOUNTS_FILTER)
        Collections.sort(allAccts, AccountUtil.ACCOUNT_TYPE_NAME_CASE_INSENSITIVE_COMPARATOR)
        for acct in allAccts:
            if acct.getAccountType() == Account.AccountType.ROOT: continue
            creationDate = acct.getCreationDateInt()
            startBal = acct.getStartBalance()
            creationMap.put(acct, [creationDate, startBal, 0L])

        allTxns = book.getTransactionSet().getAllTxns()
        for txn in allTxns:
            txnDate = txn.getDateInt()
            values = creationMap.get(txn.getAccount())
            earliestTxnDate = values[2]                                                                                 # noqa
            if earliestTxnDate == 0 or txnDate <= earliestTxnDate:
                values[2] = txnDate                                                                                     # noqa

        todayInt = DateUtil.getStrippedDateInt()

        countInvalid = 0
        countRepaired = 0
        countNotRepaired = 0
        for acct in creationMap:
            if acct.getAccountType().isCategory(): continue
            if acct.getAccountType() == Account.AccountType.SECURITY: continue
            values = creationMap.get(acct)
            creationDate = values[0]                                                                                    # noqa
            earliestTxnDate = values[2]                                                                                 # noqa

            lFutureDate = (creationDate > todayInt)
            lZeroDate = (creationDate == 0)
            if lFutureDate and earliestTxnDate > 0 and earliestTxnDate <= todayInt: pass    # make future dated invalid
            if lFutureDate: pass                                                            # make future dated invalid
            elif not lZeroDate and earliestTxnDate == 0: continue                           # assume OK
            elif lZeroDate: pass                                                            # zero date is invalid/illogical
            elif earliestTxnDate == 0: continue                                             # assume OK
            elif earliestTxnDate >= creationDate: continue                                  # assume OK
            else: pass                                                                      # anything else is invalid

            if earliestTxnDate != 0: lZeroDate = False
            if earliestTxnDate > 0 and earliestTxnDate <= todayInt: lFutureDate = False

            countInvalid += 1
            status = "<%s NOT FIXED - ATTENTION NEEDED>" %("*FUTURE-DATE*" if (lFutureDate) else "*ZERO-DATE*  ") if (lFutureDate or lZeroDate) else "<FIXED>" if fix else "<INVALID>"
            output += "%s %s %s %s %s\n" % (pad(acct.getFullAccountName(), 50),
                                            pad(str(acct.getAccountType()), 20),
                                            pad(dateFormatter.format(creationDate), 17),
                                            pad(dateFormatter.format(earliestTxnDate), 17),
                                            status)
            if fix:
                if lZeroDate or lFutureDate:
                    countNotRepaired += 1                           # we cannot fix these... manual attention needed
                else:
                    countRepaired += 1
                    acct.setCreationDateInt(earliestTxnDate)
                    acct.syncItem()

        if countInvalid < 1: output += "<NO INVALID ACCOUNT 'START DATES' FOUND>\n"

        output += "\n<END>"

        if fix: txt = "%s: - Displaying Account 'Start Date' fix report..." %(_THIS_METHOD_NAME)
        else: txt = "%s: - Displaying Account 'Start Date' validation report..." %(_THIS_METHOD_NAME)

        setDisplayStatus(txt, "B")
        jif = QuickJFrame(_THIS_METHOD_NAME.upper(), output,copyToClipboard=GlobalVars.lCopyAllToClipBoard_TB, lWrapText=False, lAutoSize=True).show_the_frame()
        if fix:
            logToolboxUpdates("validate_account_start_dates", txt)
            myPopupInformationBox(jif, "%s accounts with invalid 'start dates' %s repaired (%s NOT repaired)" %(countInvalid, countRepaired, countNotRepaired), theMessageType=JOptionPane.WARNING_MESSAGE)

    def reset_all_inbuilt_report_params_defaults():
        if MD_REF.getCurrentAccountBook() is None: return

        _THIS_METHOD_NAME = "FIX: RESET all inbuilt report/graph parameters to defaults"

        if not myPopupAskQuestion(toolbox_frame_, theQuestion="Do you want to RESET all inbuilt report/graph parameters to defaults?", theTitle=_THIS_METHOD_NAME):
            txt = "%s: User decided not to erase all inbuilt report/graph parameters - no changes made.." %(_THIS_METHOD_NAME)
            setDisplayStatus(txt, "B")
            return

        if not confirm_backup_confirm_disclaimer(toolbox_frame_, _THIS_METHOD_NAME.upper(), "RESET all inbuilt report/graph parameters?"):
            return False

        ls = MD_REF.getCurrentAccountBook().getLocalStorage()
        erasedKeys = {}
        for key in sorted(ls.keys()):
            value = ls.getStr(key, None)
            if (value is not None and key.startswith("report_params.")):
                erasedKeys[key] = value
                ls.put(key, None)
                myPrint("B", "ERASED inbuilt report/graph key: '%s' value: '%s'" %(key, value))

        txt = "%s: %s inbuilt report/graph parameter settings erased (review console for details)" %(_THIS_METHOD_NAME, len(erasedKeys))
        setDisplayStatus(txt, "B")
        logToolboxUpdates("reset_all_inbuilt_report_params_defaults", txt)
        myPopupInformationBox(toolbox_frame_, txt, theMessageType=JOptionPane.WARNING_MESSAGE)

    def delete_all_memorized_reports():
        if MD_REF.getCurrentAccountBook() is None: return

        _THIS_METHOD_NAME = "FIX: DELETE all memorized reports/graphs"

        allMemGraphsReports = getMemorizedReports(True, False, None, True)                                              # type: [ReportSpec]
        allMemGraphs = getMemorizedReports(True, False, ReportSpec.Type.GRAPH, True)                                    # type: [ReportSpec]
        allMemReports = getMemorizedReports(True, False, ReportSpec.Type.TEXT, True)                                    # type: [ReportSpec]

        if (len(allMemReports) + len(allMemGraphs)) != len(allMemGraphsReports):
            raise Exception("LOGIC ERROR: delete_all_memorized_reports() - memorized reports(%s) + graphs(%s) != all(%s)!?" %(len(allMemReports), len(allMemGraphs), len(allMemGraphsReports)))

        if not myPopupAskQuestion(toolbox_frame_, theQuestion="Do you want to DELETE all %s memorized reports(%s) and graphs(%s)?" %(len(allMemGraphsReports), len(allMemReports), len(allMemGraphs)), theTitle=_THIS_METHOD_NAME):
            txt = "%s: User decided not to delete all %s memorized reports/graphs - no changes made.." %(_THIS_METHOD_NAME, len(allMemGraphsReports))
            setDisplayStatus(txt, "B")
            return

        if not confirm_backup_confirm_disclaimer(toolbox_frame_, _THIS_METHOD_NAME.upper(), "DELETE all %s memorized reports/graphs?" %(len(allMemGraphsReports))):
            return False

        for reportSpec in allMemGraphsReports:
            if not reportSpec.isMemorized(): raise Exception("LOGIC ERROR: ReportSpec: '%s' is NOT memorized!?" %(reportSpec))
            reportSpec.deleteItem()
            myPrint("B", "DELETED Memorized Graph/Report: '%s'" %(reportSpec))

        txt = "%s: %s memorized reports(%s) and graphs(%s) deleted (review console for details)" %(_THIS_METHOD_NAME, len(allMemGraphsReports), len(allMemReports), len(allMemGraphs))
        setDisplayStatus(txt, "B")
        logToolboxUpdates("delete_all_memorized_reports", txt)
        myPopupInformationBox(toolbox_frame_, txt, theMessageType=JOptionPane.WARNING_MESSAGE)

    def view_inactiveAcctsIncludedNW():
        return fix_inactiveAcctsIncludedNW(lFix=False)

    def fix_inactiveAcctsIncludedNW(lFix=False):
        if MD_REF.getCurrentAccountBook() is None: return
        if not isNetWorthUpgradedBuild(): return

        if lFix:
            from com.infinitekind.moneydance.model import UndoableChange    # should be OK as we have confirmed we are in MD2024.x onwards
            undo = MD_REF.getUI().getUndoManager()
            if undo is None: raise Exception("LOGIC ERROR: could not get Undo Manager?!")
            _THIS_METHOD_NAME = "FIX: Exclude all inactive accounts from Net Worth calculations"
        else:
            undo = None
            _THIS_METHOD_NAME = "DIAG: Show inactive accounts included in Net Worth calculations"

        output = "\n" \
                 "%s:\n" \
                 " ======================================================\n\n" %(_THIS_METHOD_NAME.upper())

        book = MD_REF.getCurrentAccountBook()
        base = MD_REF.getCurrentAccountBook().getCurrencies().getBaseType()
        dec = MD_REF.getPreferences().getDecimalChar()
        today = DateUtil.getStrippedDateInt()

        output += "Listing inactive accounts included in Net Worth calculations (Base currency: %s %s)\n\n" %(base.getIDString(), base.getName())

        allAccts = sorted(AccountUtil.allMatchesForSearch(book, AcctFilter.ALL_ACCOUNTS_FILTER),
                          key=lambda sort_x: (sort_x.getAccountType(), sort_x.getFullAccountName().upper()))

        totalBalance = 0L
        totalCurrentBalance = 0L
        accountsToFix = []
        for acct in allAccts:
            if not acct.isAccountNetWorthEligible(): continue       # only select NW eligible accounts
            if not acct.getAccountOrParentIsInactive(): continue    # only select INACTIVE accounts
            if not acct.getIncludeInNetWorth(): continue            # only select accounts still included in NW
            balance = CurrencyUtil.convertValue(acct.getBalance(), acct.getCurrencyType(), base)
            currentBalance = CurrencyUtil.convertValue(acct.getCurrentBalance(), acct.getCurrencyType(), base, today)
            totalBalance += balance
            totalCurrentBalance += currentBalance
            output += ("Type: %s Account: '%s' Current Balance: %s Balance: %s\n"
                       %(pad(acct.getAccountType(), 12), padTruncateWithDots(acct.getFullAccountName(), 80),
                         rpad(base.formatFancy(currentBalance, dec), 14), rpad(base.formatFancy(balance, dec), 14)))
            accountsToFix.append(acct)

        output += "\n%s Totals: Current Balance: %s Balance: %s\n" %((" "*102), rpad(base.formatFancy(totalCurrentBalance, dec), 14), rpad(base.formatFancy(totalBalance, dec), 14))
        output += "\n<END>"

        txt = "%s: - Displaying inactive accounts included in Net Worth calculations" %(_THIS_METHOD_NAME)
        setDisplayStatus(txt, "B")
        jif = QuickJFrame(_THIS_METHOD_NAME.upper(), output,copyToClipboard=GlobalVars.lCopyAllToClipBoard_TB, lWrapText=False, lAutoSize=True).show_the_frame()
        if not lFix: return

        if len(accountsToFix) < 1:
            txt = "%s: No accounts found to fix/exclude - no changes made" %(_THIS_METHOD_NAME)
            setDisplayStatus(txt, "R")
            myPopupInformationBox(jif, txt, theMessageType=JOptionPane.WARNING_MESSAGE)
            return

        if not confirm_backup_confirm_disclaimer(jif, _THIS_METHOD_NAME, "Exclude %s accounts from Net Worth calculations?" %(len(accountsToFix))):
            txt = "%s: User did not agree to proceed with changes - no changes made!" %(_THIS_METHOD_NAME)
            setDisplayStatus(txt, "R"); myPrint("B", txt)
            myPopupInformationBox(jif, txt, _THIS_METHOD_NAME, JOptionPane.WARNING_MESSAGE)
            return

        myPrint("B", "BEGIN: Excluding accounts from Net Worth calculations...:")
        change = UndoableChange()                                                                                       # noqa
        for acct in accountsToFix:
            change.beginModification(acct)
            acct.setIncludeInNetWorth(False)
            change.finishModification(acct)
            myPrint("B", "excluded account '%s' from Net Worth" %(acct))
        undo.recordChange(change)
        myPrint("B", "FINISHED: Excluded %s accounts from Net Worth calculations - UNDO HAS BEEN ENABLED" %(len(accountsToFix)))

        txt = "%s: Excluded %s accounts from Net Worth calculations ** UNDO ENABLED **" %(_THIS_METHOD_NAME, len(accountsToFix))
        setDisplayStatus(txt, "B")
        logToolboxUpdates("fix_inactiveAcctsIncludedNW", txt)
        myPopupInformationBox(jif, txt, theMessageType=JOptionPane.WARNING_MESSAGE)


    def view_networthCalculations():
        if MD_REF.getCurrentAccountBook() is None: return
        if not isNetWorthUpgradedBuild(): return

        if SwingUtilities.isEventDispatchThread():
            myPrint("DB", "Pushing view_networthCalculations() off the EDT for NetWorthCalculator....")
            genericThreadRunner(True, view_networthCalculations)
            return

        from com.infinitekind.moneydance.model import NetWorthCalculator

        _THIS_METHOD_NAME = "View all possible system generated NetWorth calculations"

        output = "\n" \
                 "%s:\n" \
                 " ======================================================\n\n" %(_THIS_METHOD_NAME.upper())

        book = MD_REF.getCurrentAccountBook()
        base = MD_REF.getCurrentAccountBook().getCurrencies().getBaseType()
        dec = MD_REF.getPreferences().getDecimalChar()

        output += "Base currency: %s %s\n\n" %(base.getIDString(), base.getName())

        for balType in [Account.BalanceType.CURRENT, Account.BalanceType.NORMAL]:
            for ignoreFlag in [True, False]:
                nwCalculator = NetWorthCalculator(book, base)
                nwCalculator.setBalanceType(balType)
                nwCalculator.setIgnoreAccountSpecificNetWorthFlags(ignoreFlag)                                          # noqa
                netWorth = nwCalculator.calculateTotal()
                output += ("BalanceType: %s ignoreAccountSpecificNetWorthFlags: %s NW Calculation: %s  \n"
                           %(pad("Current" if balType == Account.BalanceType.CURRENT else "Balance/Future", 15),
                             pad(str(ignoreFlag), 6),
                             rpad(base.formatFancy(netWorth.getAmount(), dec),20)))


        output += "\n\n"

        countExcluded = 0
        output += "Accounts with specific Net Worth exclusion flag set:\n"
        output += "----------------------------------------------------\n"
        for acct in AccountUtil.allMatchesForSearch(book, AcctFilter.ALL_ACCOUNTS_FILTER):
            if acct.isAccountNetWorthEligible() and not acct.getIncludeInNetWorth():
                countExcluded += 1
                output += "AcctType: %s Account: '%s'\n" %(pad(str(acct.getAccountType()), 20), acct.getFullAccountName())
        if (countExcluded < 1): output += "<none>\n"
        output += "----------------------------------------------------\n"

        output += "\n<END>"

        txt = "%s: Displaying NetWorth Settings" %(_THIS_METHOD_NAME)
        setDisplayStatus(txt, "B")
        QuickJFrame(_THIS_METHOD_NAME.upper(), output, copyToClipboard=GlobalVars.lCopyAllToClipBoard_TB, lWrapText=False, lAutoSize=True).show_the_frame()

    def view_shouldBeIncludedInNetWorth_settings():
        if MD_REF.getCurrentAccountBook() is None: return

        _THIS_METHOD_NAME = "View Accounts' shouldBeIncludedInNetWorth() settings"

        output = "\n" \
                 "%s:\n" \
                 " ======================================================\n\n" %(_THIS_METHOD_NAME.upper())

        if not isNetWorthUpgradedBuild():
            output += "Prior to MD2024.3(5204) Moneydance predefined rules to include/exclude Accounts in both the Summary Page NetWorthView widget, & also the Titlebar's dashboard NW graph\n" \
                      "- exclude when the account or its Parent is Inactive\n" \
                      "- exclude the ROOT account and Income/Expense Categories\n" \
                      "- Then it checks for a hidden account setting (you can set this in Toolbox Update Mode)\n" \
                      "- You cannot force include an account into the rules, you can only force exclude accounts....\n" \
                      "\n" \
                      "Other NetWorth rules for information:\n" \
                      "- NW Reports / Graphs are based on transactions up to the date you specify; uses Price history data for balance valuations\n" \
                      "- The Top title bar / dashboard NW Graph's cutoff date can be changed: 'All Dates' includes future Balances; uses Price history data for balance valuations\n" \
                      "- The Summary Screen's NW widget total ALWAYS uses Current Balance(s) - so future balances are excluded; uses Current Price\n" \
                      "NOTE: In MD2024.3(5204) all the calculations were aligned, and you have more user-control over the settings...\n\n"
        else:
            output += "From MD2024.3(5204) onwards all the Networth calculations and rules were aligned. You also have more inbuilt control over the settings...\n" \
                      "- ROOT and Income/Expense Categories are always excluded\n" \
                      "- You can exclude certain accounts from the calculations using Tools/Accounts and change the 'include in NW' setting'\n" \
                      "\n" \
                      "Other NetWorth rules for information:\n" \
                      "- right-click the dashboard and summary page widgets for settings" \
                      "- in the NW Graph and Reports you can toggle the 'include all accounts' flag to override and ignore the 'include in NW' setting\n" \
                      "- any end date that is today or future will always value using the current price field\n" \
                      "\n\n"

        output += "%s %s %s %s\n" %(pad("Account Name",50),
                                    pad("Account Type",20),
                                    pad("shouldBeIncludedInNetWorth()",30),
                                    pad("Override Setting",20))

        output += "%s %s %s %s\n" %("-"*50,
                                    "-"*20,
                                    "-"*30,
                                    "-"*20)

        output += "\n"

        allAccounts = AccountUtil.allMatchesForSearch(MD_REF.getCurrentAccountBook(), MyAcctFilter(25))
        allAccounts = sorted(allAccounts, key=lambda x: (x.getAccountType(), x.getFullAccountName().upper()))

        # the method shouldBeIncludedInNetWorth() was removed in MD2024.3(5204) and subsumed into the (getter/setter) property includeInNetWorth...
        for acct in allAccounts:
            if isNetWorthUpgradedBuild():
                if not acct.isAccountNetWorthEligible(): continue
            else:
                if acct.getAccountType() == Account.AccountType.INCOME or acct.getAccountType() == Account.AccountType.EXPENSE or acct.getAccountType() == Account.AccountType.ROOT:
                    continue

            output += "%s %s %s %s\n" %(pad(acct.getFullAccountName(),50),
                                        pad(str(acct.getAccountType()),20),
                                        pad(str(acct.shouldBeIncludedInNetWorth() if (not isNetWorthUpgradedBuild()) else acct.getIncludeInNetWorth()),30),
                                        ("-" if (not acct.getParameter(GlobalVars.Strings.MD_KEY_PARAM_APPLIES_TO_NW, None)) else (str(acct.getBooleanParameter(GlobalVars.Strings.MD_KEY_PARAM_APPLIES_TO_NW, True)))))
        output += "\n<END>"

        txt = "%s: Displaying NetWorth Settings" %(_THIS_METHOD_NAME)
        setDisplayStatus(txt, "B")
        QuickJFrame(_THIS_METHOD_NAME.upper(), output, copyToClipboard=GlobalVars.lCopyAllToClipBoard_TB, lWrapText=False, lAutoSize=True).show_the_frame()

    def edit_shouldBeIncludedInNetWorth_settings():
        if MD_REF.getCurrentAccountBook() is None: return
        if isNetWorthUpgradedBuild(): return

        _THIS_METHOD_NAME = "EDIT an Account's shouldBeIncludedInNetWorth() setting"

        allAccounts = AccountUtil.allMatchesForSearch(MD_REF.getCurrentAccountBook(), MyAcctFilter(25))
        allAccounts = sorted(allAccounts, key=lambda x: (x.getAccountType(), x.getFullAccountName().upper()))

        newAccounts = []
        for acct in allAccounts:
            if acct.getAccountType() == Account.AccountType.INCOME or acct.getAccountType() == Account.AccountType.EXPENSE or acct.getAccountType() == Account.AccountType.ROOT:
                continue
            newAccounts.append(StoreAccountList(acct))
        del allAccounts

        lPresentedBackupDisclaimer = False
        iCountChanges = 0

        while True:

            selectedAcct = JOptionPane.showInputDialog(toolbox_frame_,
                                                       "Select the Acct edit the shouldBeIncludedInNetWorth() setting",
                                                       _THIS_METHOD_NAME.upper(),
                                                       JOptionPane.INFORMATION_MESSAGE,
                                                       getMDIcon(lAlwaysGetIcon=True),
                                                       newAccounts,
                                                       None)
            if not selectedAcct: break

            selectedAcct = selectedAcct.obj       # type: Account                                                       # noqa

            currentNWsettingBool = selectedAcct.getBooleanParameter(GlobalVars.Strings.MD_KEY_PARAM_APPLIES_TO_NW, True)

            options = ["YES - Include", "NO - Exclude"]
            if currentNWsettingBool:
                current = options[0]
            else:
                current = options[1]

            selectedIncludeInNW = JOptionPane.showInputDialog(toolbox_frame_,
                                                       "Select whether to include/exclude this account in the default NW Home Screen Widget & Titlebar Graph",
                                                       _THIS_METHOD_NAME.upper()+" for: %s" %(selectedAcct.getAccountName()),
                                                       JOptionPane.WARNING_MESSAGE,
                                                       getMDIcon(None),
                                                       options,
                                                       current)
            if not selectedIncludeInNW: continue

            if not lPresentedBackupDisclaimer:
                if not confirm_backup_confirm_disclaimer(toolbox_frame_, _THIS_METHOD_NAME.upper(), "Change 'include in NW' to '%s'?" %(selectedIncludeInNW)):
                    return
                lPresentedBackupDisclaimer = True

            if options.index(selectedIncludeInNW) == 0:
                # Include selected
                selectedAcct.setParameter(GlobalVars.Strings.MD_KEY_PARAM_APPLIES_TO_NW, None)
            else:
                # Exclude selected
                selectedAcct.setParameter(GlobalVars.Strings.MD_KEY_PARAM_APPLIES_TO_NW, False)

            selectedAcct.syncItem()
            iCountChanges += 1

            txt = "%s: Account: '%s' Parameter: '%s' set to %s" %(_THIS_METHOD_NAME, selectedAcct, GlobalVars.Strings.MD_KEY_PARAM_APPLIES_TO_NW, selectedIncludeInNW)
            setDisplayStatus(txt, "B"); myPrint("B", txt)
            logToolboxUpdates("edit_shouldBeIncludedInNetWorth_settings", txt)
            myPopupInformationBox(toolbox_frame_,txt)

            continue

        if iCountChanges:
            txt = "%s: Updated the NW setting in %s Account(s)!" %(_THIS_METHOD_NAME, iCountChanges)
        else:
            txt = "%s: No Accounts changed" %(_THIS_METHOD_NAME)
        setDisplayStatus(txt, "R"); myPrint("B", txt)
        myPopupInformationBox(toolbox_frame_,txt,theMessageType=JOptionPane.WARNING_MESSAGE)


    #### Security stock splits - before/after split date price checks....

    # ---- tuning ----
    EPSILON = 1e-8
    TOL_ON = 0.05       # 5% tolerance for split-date price vs expected
    TOL_AFTER = 0.10    # 10% tolerance for first-after price vs expected

    # ---- helpers ----
    def _rel_close(a, b, tol):
        # pure relative tolerance in SAME orientation as output (no floor)
        if a is None or b is None:
            return False
        denom = abs(b)
        if denom < EPSILON:
            return False
        return abs(a - b) <= tol * denom

    def _pct_diff(actual, expected):
        if actual is None or expected is None or abs(expected) < EPSILON: return None
        return (actual - expected) / expected

    def _fmt_val(v, missingTxt, dec, curr):
        if isPriceDisplayDecimalsBuild(): return missingTxt if v is None else StringUtils.formatRate(v, dec, curr.getPriceDisplayDecimalPlaces())
        return missingTxt if v is None else (u"%.6f" %(v))

    def _fmt_pct(delta, missingTxt): return missingTxt if delta is None else (u"%+.2f%%" % (delta * 100.0))

    def format_split_ratio_both(ratio_double, dec, max_den=1000):
        if ratio_double <= 0.0 or unicode(ratio_double) == u"NaN": return u"?:?", unicode(ratio_double)
        frac = Fraction(ratio_double).limit_denominator(max_den)
        if isPriceDisplayDecimalsBuild(): return u"%d for %d" % (frac.numerator, frac.denominator), u"*" + StringUtils.formatRate(ratio_double, dec, 6)
        return u"%d for %d" % (frac.numerator, frac.denominator), u"*%.6f" % ratio_double

    def _find_on_prev_next(snaps, dates, target):
        n = len(dates)
        if n == 0: return None, None, None
        i = bisect_left(dates, target)
        on = snaps[i] if i < n and dates[i] == target else None
        prev = snaps[i-1] if i > 0 else None
        nxt = snaps[i+1] if (on is not None and i+1 < n) else (snaps[i] if (on is None and i < n) else None)
        return on, prev, nxt

    def _classify_issue(prev_rate, on_rate, later_exists, disp_on, disp_after, disp_expected):
        # Returns (warning, action) for failing rows only (OK rows are skipped before calling this)
        if prev_rate is None:
            return (u"No before split price found", u"Add a price record before the split date")
        if on_rate is None:
            if later_exists and disp_expected is not None and disp_after is not None:
                if _rel_close(disp_after, disp_expected, TOL_AFTER):
                    return (u"No split date price found (later price consistent with expected)",
                            u"Add a price record on the split date")
                return (u"No split date price found (later price inconsistent with expected)",
                        u"Add a price record on the split date")
            return (u"No split date price found", "Add a price record on the split date")
        if disp_expected is not None and disp_on is not None and not _rel_close(disp_on, disp_expected, TOL_ON):
            return (u"Split date price found, but expecting different price",
                    u"Review and correct the split date price record")
        if (disp_after is not None) and (disp_expected is not None) and (not _rel_close(disp_after, disp_expected, TOL_AFTER)):
            return (u"After split price inconsistent with expected post split price",
                    u"Review and correct post-split price records")
        return (u"", u"")

    # Signed deltas using Moneydance DateUtil (ints YYYYMMDD)
    def _delta_prev(prevDateInt, splitDateInt):
        if prevDateInt is None: return u""
        days = DateUtil.calculateDaysBetween(prevDateInt, splitDateInt)
        return u"%+d" % (-abs(days))

    def _delta_next(nextDateInt, splitDateInt):
        if nextDateInt is None: return u""
        days = DateUtil.calculateDaysBetween(splitDateInt, nextDateInt)
        return u"%+d" % abs(days)

    # ---- main ----
    def diag_security_splits_no_price(lAll=False):
        if MD_REF.getCurrentAccountBook() is None: return

        if lAll:
            _THIS_METHOD_NAME = u"DIAG: List all security split data (also performs validation)"
        else:
            _THIS_METHOD_NAME = u"DIAG: Validate dated price record exists on security split date(s)"

        output = u""
        output += u"\n%s:\n" % _THIS_METHOD_NAME.upper()
        output += u" ================================================================\n\n"

        # ---------- two-row headers ----------
        output += u"%s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s\n" % (
            pad(u"Security", 60),               # Security
            pad(u"Split", 10),                  # Split date
            pad(u"Qty Split", 12),              # Qty Split ratio (text: "X for Y")
            rpad(u"", 1),                       # ratio arrow
            rpad(u"Qty Split", 12),             # Qty Split decimal ratio
            pad(u"Before", 10),                 # Before split - date found
            pad(u"Before", 6),                  # Before split - days
            rpad(u"Before", 12),                # Before split - price
            pad(u"**Split**", 10),              # On split date - date found
            rpad(u"**Split**", 12),             # On split date - price
            rpad(u"Est. Price", 12),            # Est. price after split
            rpad(u"", 1),                       # Est. price arrow
            rpad(u"calc", 10),                  # Est price delta (post-split price to estimated price)
            pad(u"Next", 10),                   # Next after - split date
            pad(u"", 6),                        # Next after - days
            rpad(u"Next", 12),                  # Next after - price found
            rpad(u"Next", 10),                  # Next after price % delta
            pad(u"Warnings", 20)
        )

        output += u"%s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s\n" % (
            pad(u"", 60),                  # Security
            pad(u"Date", 10),              # Split date
            pad(u"New for Old", 12),       # Qty Split ratio (text: "X for Y")
            rpad(u"", 1),                  # ratio arrow
            rpad(u"(dec) Ratio", 12),      # Qty Split decimal ratio
            pad(u"Split Date", 10),        # Before split - date found
            pad(u"Days", 6),               # Before split - days
            rpad(u"Split Price", 12),      # Before split - price
            pad(u"Date Found", 10),        # On split date - date found
            rpad(u"Price Found", 12),      # On split date - price
            rpad(u"Post Split", 12),       # Est. price after split
            rpad(u"", 1),                  # Est. price arrow
            rpad(u"Price %\u0394", 10),    # Est price delta (post-split price to estimated price)
            pad(u"After Date", 10),        # Next after - split date
            pad(u"Days", 6),               # Next after - days
            rpad(u"Price Found", 12),      # Next after - price found
            rpad(u"Price %\u0394", 10),
            pad(u"Action", 20)
        )

        # underlines
        output += u"%s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s\n\n" % (
            u"-"*60, u"-"*10, u"-"*12, " "*1, u"-"*12, u"-"*10, u"-"*6, u"-"*12, u"-"*10, u"-"*12, u"-"*12, " "*1, u"-"*10, u"-"*10, u"-"*6, u"-"*12, u"-"*10, u"-"*20
        )

        # gather securities (securities only) and sort by name
        allSecurities = [s for s in MD_REF.getCurrentAccountBook().getCurrencies().getAllCurrencies()
                         if s.getCurrencyType() is CurrencyType.Type.SECURITY]
        allSecurities = sorted(allSecurities, key=lambda x: x.getName().upper())

        sdf = MD_REF.getPreferences().getShortDateFormatter()
        dec = MD_REF.getPreferences().getDecimalChar()

        countIssues = 0
        last_sec = None
        missingTxt = u"<missing>"

        for sec in allSecurities:
            splits = sec.getSplits()
            if not splits: continue

            snaps = list(sec.getSnapshots())
            if not snaps: continue

            dates = [s.getDateInt() for s in snaps]

            emitted_for_this_sec = False

            for split in splits:
                ratio = split.getSplitRatio()
                if abs(ratio - 1.0) < EPSILON: continue

                splitDate = split.getDateInt()
                on_snap, prev_snap, next_snap = _find_on_prev_next(snaps, dates, splitDate)

                beforeSplitDateRate = None if prev_snap is None else prev_snap.getRate()
                onSplitDateRate = None if on_snap is None else on_snap.getRate()
                afterSplitDateRate = None if next_snap is None else next_snap.getRate()

                # expected in RAW orientation (unchanged)
                estSplitDateRate = None if (beforeSplitDateRate is None or ratio <= 0.0) else (beforeSplitDateRate * ratio)

                # ---- compute DISPLAY orientation values once ----
                disp_before   = None if beforeSplitDateRate is None else safeInvertRate(beforeSplitDateRate)
                disp_on       = None if onSplitDateRate     is None else safeInvertRate(onSplitDateRate)
                disp_after    = None if afterSplitDateRate  is None else safeInvertRate(afterSplitDateRate)
                disp_expected = None if estSplitDateRate    is None else safeInvertRate(estSplitDateRate)

                # strict pass/fail using DISPLAY orientation for consistency with shown %Δ
                ok = True
                if beforeSplitDateRate is None: ok = False
                elif onSplitDateRate is None: ok = False
                elif disp_expected is None or not _rel_close(disp_on, disp_expected, TOL_ON): ok = False
                elif (disp_after is not None) and (not _rel_close(disp_after, disp_expected, TOL_AFTER)): ok = False

                if ok and (not lAll): continue

                if ok:
                    warning, action = u"OK", u""
                else:
                    later_exists = next_snap is not None
                    warning, action = _classify_issue(
                        beforeSplitDateRate, onSplitDateRate, afterSplitDateRate, estSplitDateRate,
                        later_exists, disp_on)

                beforeDisp   = _fmt_val(disp_before,   missingTxt, dec, sec)
                onDisp       = _fmt_val(disp_on,       missingTxt, dec, sec)
                afterDisp    = _fmt_val(disp_after,    missingTxt, dec, sec)
                expectedDisp = _fmt_val(disp_expected, missingTxt, dec, sec)

                # %Δ in DISPLAY orientation
                pct_on    = _pct_diff(disp_on,    disp_expected)
                pct_after = _pct_diff(disp_after, disp_expected)

                prevDateInt = None if prev_snap is None else prev_snap.getDateInt()
                onDateInt   = None if on_snap   is None else on_snap.getDateInt()
                nextDateInt = None if next_snap is None else next_snap.getDateInt()

                prevDateStr = missingTxt if prevDateInt is None else sdf.format(prevDateInt)
                onDateStr   = missingTxt if onDateInt   is None else sdf.format(onDateInt)
                nextDateStr = missingTxt if nextDateInt is None else sdf.format(nextDateInt)

                dPrev = _delta_prev(prevDateInt, splitDate)
                dNext = _delta_next(nextDateInt, splitDate)

                ratio_str, ratio_dec = format_split_ratio_both(ratio, dec)

                if not emitted_for_this_sec:
                    if last_sec is not None: output += u"\n"
                    last_sec = sec
                    emitted_for_this_sec = True

                secNameCol = sec.getName()

                output += u"%s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s\n" % (
                    padTruncateWithDots(secNameCol, 60),            # Security
                    pad(sdf.format(splitDate), 10),                 # Qty Split date
                    pad(ratio_str, 12),                             # Qty Split ratio (text: "X for Y")
                    pad(u"↓" if (ratio < 1.0) else u"↑", 1),        # ratio arrow
                    rpad(ratio_dec, 12),                            # Qty Split decimal ratio
                    pad(prevDateStr, 10),                           # Before split - date found
                    pad(dPrev, 6),                                  # Before split - days
                    rpad(beforeDisp, 12),                           # Before split - price
                    pad(onDateStr, 10),                             # On split date - date found
                    rpad(onDisp, 12),                               # On split date - price
                    rpad(expectedDisp, 12),                         # Est. price after split
                    pad(u"↑" if (ratio < 1.0) else u"↓", 1),        # Est. price arrow
                    rpad(_fmt_pct(pct_on,   missingTxt), 10),       # Est price delta
                    pad(nextDateStr, 10),                           # Next after - date
                    pad(dNext, 6),                                  # Next after - days
                    rpad(afterDisp, 12),                            # Next after - price
                    rpad(_fmt_pct(pct_after, missingTxt), 10),      # Next after price % delta
                    warning + (u" | " + action if action else "")   # warning / action
                )

                if not ok: countIssues += 1

        output += u"\n<END>"

        # Show frame if issues exist OR lAll=True. Suppress info popup when lAll=True.
        if lAll or countIssues > 0:
            if countIssues > 0:
                txt = "%s: Displaying %s split-date pricing validation issue(s)" % (_THIS_METHOD_NAME, countIssues)
                setDisplayStatus(txt, "R")
            else:
                txt = "%s: Displaying all split data (and validation results)" %(_THIS_METHOD_NAME)
                setDisplayStatus(txt, "B")
            jif = QuickJFrame(_THIS_METHOD_NAME.upper(), output, copyToClipboard=GlobalVars.lCopyAllToClipBoard_TB, lWrapText=False, lAutoSize=True).show_the_frame()
            myPopupInformationBox(jif, txt, theMessageType=JOptionPane.WARNING_MESSAGE)

        else:
            txt = "%s: - No split-date pricing validation issues detected!" %(_THIS_METHOD_NAME)
            setDisplayStatus(txt, "B")
            myPopupInformationBox(toolbox_frame_, txt, theMessageType=JOptionPane.INFORMATION_MESSAGE)

    #### Security stock splits - before/after split date price checks....

    def view_reports_record_keys():
        _THIS_METHOD_NAME = u"DIAG - View Reports' Data Export Record Keys"
        if MD_REF.getBuild() < 5500: return
        from com.moneydance.apps.md.view.gui import GraphReportGenerator
        rpts = getMemorizedReports(False, True, ReportSpec.Type.TEXT, False)                                            # noqa
        exportRpts = []
        for rs in rpts:
            try:
                repgen = GraphReportGenerator.getGenerator(rs, MD_REF.getUI())
                if repgen is not None and repgen.canGenerateExportData(): exportRpts.append(repgen)
            except: pass
        if len(exportRpts) < 1:
            txt = "%s: - No data export enabled reports detected!" %(_THIS_METHOD_NAME)
            setDisplayStatus(txt, "B")
            myPopupInformationBox(toolbox_frame_, txt, theMessageType=JOptionPane.INFORMATION_MESSAGE)

        output = u""
        output += u"\n%s:\n" % _THIS_METHOD_NAME.upper()
        output += u" ================================================================\n\n"

        for rpt in exportRpts:
            output += "\nReport: %s\n" %(rpt.getName())
            rKeys = rpt.getExportKeyDescriptions()
            if len(rKeys) < 1:
                output += "           <NONE>\n"
                continue
            for entry in rKeys.entrySet():
                key = entry.getKey()
                value = entry.getValue()
                output += "           %s = %s\n" %(pad(key, 5), value)

        output += "\n\n<END>\n"

        txt = "%s: Displaying data export record keys" %(_THIS_METHOD_NAME)
        setDisplayStatus(txt, "B")
        jif = QuickJFrame(_THIS_METHOD_NAME.upper(), output, copyToClipboard=GlobalVars.lCopyAllToClipBoard_TB, lWrapText=False, lAutoSize=True).show_the_frame()
        myPopupInformationBox(jif, txt, theMessageType=JOptionPane.WARNING_MESSAGE)

    def list_potentially_duplicate_securities():
        _THIS_METHOD_NAME = "LIST POTENTIALLY DUPLICATE SECURITIES".upper()
        _countDuplicateSecurities, _duplicateSecurities, output = detect_duplicate_securities()
        if _countDuplicateSecurities > 0:
            txt = "%s: Potentially %s duplicate securities found (Tools>Securities)!" %(_THIS_METHOD_NAME, _countDuplicateSecurities)
            setDisplayStatus(txt, "R"); myPrint("B", txt)
            QuickJFrame(_THIS_METHOD_NAME, output, copyToClipboard=GlobalVars.lCopyAllToClipBoard_TB, lWrapText=False, lAutoSize=True).show_the_frame()
        else:
            txt = "%s: No (potentially) duplicated securities detected" %(_THIS_METHOD_NAME)
            setDisplayStatus(txt, "B"); myPrint("B", txt)
            myPopupInformationBox(toolbox_frame_, txt, _THIS_METHOD_NAME, JOptionPane.INFORMATION_MESSAGE)
        del _countDuplicateSecurities, _duplicateSecurities, output

    def showMDLaunchParameters():
        _THIS_METHOD_NAME = "ADVANCED: SHOW MD LAUNCH PARAMETERS"

        displayTxt = """
------------------------------------------------------------------------------------------------------------------------
ADVANCED MONEYDANCE LAUNCH SETTINGS / PARAMETERS:
-------------------------------------------------

Moneydance(MD) is built on Java. Hence the application runs on a Java Virtual Machine (JVM).
- The MD installer typically creates an app package and launch icon for easy execution of the app

- NOTE: You can also execute the moneydance.jar using Java as long as you set up your environment properly.
        .. this is out of scope of this document, but refer to: https://yogi1967.github.io/MoneydancePythonScripts/
        .. and the example launch scripts contained on my site.
        .. MD2022.1(4058) Java 17, MD2022.3(4077) Java 18, MD2023.2(5008) Java 20, MD2023.2(5047) Java 21

- Windows and Linux: The launch package is built using install4j. The JVM can be modified by editing the vmoptions file.
                     See separate Toolbox > Advanced Options menu > 'View Java VM Options File' for details
                     You can edit this 'vmoptions' file and pass settings through to the JVM at launch:
                         e.g. -XX:MaxRAMPercentage=80 (which is now the default anyway)                     
                     You can in theory pass any valid JVM options in this file:
                         e.g. -Dtoolbox=great (would set the System property key 'toolbox' with a value of 'great' 
                     
                     You can also pass options on the command line that will be captured by install4j and passed through
                     to the JVM (so similar to the vmoptions file above, but via command line)
                        e.g. -J-Dtoolbox=great
                        refer: https://www.ej-technologies.com/resources/install4j/help/doc/installers/options.html

- Windows: You can simply execute the Moneydance.exe file (with [optional] parameters - see below)
           - NOTE: Even when launched this way, the vmoptions file will be processed.

                   - using the exe does not write to stderr / stdout, so you cannot easily see results from -v
                     .. you can use: "\\Program Files\\Moneydance\\Moneydance" -v > [pathto]outputfile.txt 2>&1
                     .. as an alternative you can try:
                     .. "\\Program Files\\Moneydance\\jre\\bin\\java" -jar "\\Program Files\\Moneydance\\lib\\moneydance.jar" -v

- Linux: The app package is normally located in /opt/Moneydance. This is actually an .sh script file.
         ... the [optional] parameters below will work with this app package using Terminal.
         
- Apple macOS: The installer creates an apple mac 'package' file called /Applications/Moneydance.app
               .. (this is really a special folder. In Finder, right-click and 'Show Package Contents'
               .. There is no vmoptions file option with macOS
               .. But you can simply execute Moneydance from Terminal using the following command:
               .. /Applications/Moneydance.app/Contents/MacOS/Moneydance (with [optional] parameters - see below)

Moneydance parameters:
----------------------
-d                  Enables Moneydance DEBUG mode (extra messages in help/console)
-v                  prints the current version (and then quits)
--version           same as -v
-nobackup'          disables backups for this MD session (from build 5047 onwards)
datasetname         will open the specified dataset >> specify the full path wrapped in (plain text) "quotes" 
pythonscriptname.py adds script to a list of scripts to execute (but this seems to then be ignored)
importfilename      executes file import (mutually exclusive to datasetname option)
-invoke_and_quit=x  will pass a string cmd that will invoke an 'fmodule' (extension) and quit (not showing UI)
                    .. executes Main.showURL(invokeAndQuitURI)
                    .. e.g. 'moneydance:fmodule:test:test:customevent:magic'
                    .. (e.g. my extension(s) with an id of test defines it's own command called 'test:customevent:magic'
                    .. (there are other variations of this parameter and with ? instead of ':' for parameters.....
-invoke=x           Same as -invoke_and_quit but does launch the UI first and doesn't quit...!

Extensions:
-----------
Two (known) extensions have been updated to leverage the -invoke command. These are: Quote Loader & Extract Data.
The commands to execuite these are:
                                    -invoke=moneydance:fmodule:securityquoteload:runstandalone:quit
                                    -invoke=moneydance:fmodule:extract_data:autoextract:quit
                                    (use :quit or :noquit) to quit the session or leave open after execution

Dataset Master Password:
------------------------
MD2021.2(3088): Adds capability to set the encryption passphrase into an environment variable to bypass the logon.
                Either: md_passphrase=   or  md_passphrase_[filename in lowercase format]=
                E.g. md_passphrase=test would pass the password of 'test'
                The variable must be set into the parent environment (using 'set' / 'export' command as appropriate)
                NOTE: If you have not set a master password, then you do not need to worry about this!

------------------------------------------------------------------------------------------------------------------------
"""

        jif = QuickJFrame(_THIS_METHOD_NAME, displayTxt, copyToClipboard=GlobalVars.lCopyAllToClipBoard_TB, lWrapText=False).show_the_frame()
        jif.toFront()

        txt = "Advanced Moneydance launch settings/parameters displayed"
        setDisplayStatus(txt, "B")


    class CollectTheGarbage(AbstractAction):

        def __init__(self): pass

        # noinspection PyUnusedLocal
        def actionPerformed(self, event):
            System.gc()
            txt = "@@@ Toolbox has requested System.gc() (Garbage Collection).... @@"
            setDisplayStatus(txt, "B"); myPrint("B", txt)
            MD_REF.getUI().setStatus(txt, 0)

    _extra_code_initialiser()
    myPrint("DB", "Extra Code Initialiser finished....")

except QuickAbortThisScriptException: pass

#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# toolbox_extra_code.py build: 1001 - Sept 2023 onwards - Stuart Beesley StuWareSoftSystems

# To avoid the dreaded issue below, moving some code here....:
# java.lang.RuntimeException: java.lang.RuntimeException: For unknown reason, too large method code couldn't be resolved

# build: 1000 - NEW SCRIPT
#               Rebuilt all the encrypt/decrypt file to/from Dataset/Sync... Now can access Dropbox Cloud Sync files online too...
# build: 1001 - Show encryption details report added - advanced_show_encryption_keys() ...
###############################################################################
# MIT License
#
# Copyright (c) 2021-2023 Stuart Beesley - StuWareSoftSystems & Infinite Kind (Moneydance)
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
global AccountBookWrapper, Common, GridC, MDIOUtils, StringUtils

# Java definitions
global File, FileInputStream, FileOutputStream, IOException, JOptionPane, System, String
global JList, ListSelectionModel, DefaultListCellRenderer, DefaultListSelectionModel, Color, Desktop
global BorderFactory, JSeparator, DefaultComboBoxModel, SwingWorker, JPanel, GridLayout, JLabel, GridBagLayout, BorderLayout
global Paths, Files, StandardCopyOption, Charset

# My definitions
global toolbox_frame_
global MD_REF, GlobalVars, debug, myPrint, QuickAbortThisScriptException
global myPopupInformationBox, getFileFromFileChooser, get_home_dir, myPopupAskQuestion
global invokeMethodByReflection, getFieldByReflection, setFieldByReflection
global MyPopUpDialogBox, logToolboxUpdates, file_chooser_wrapper, dump_sys_error_to_md_console_and_errorlog
global get_sync_folder, pad, setDisplayStatus, doesUserAcceptDisclaimer, get_time_stamp_as_nice_text
global MyJScrollPaneForJOptionPane, getMDIcon, QuickJFrame
global genericSwingEDTRunner, genericThreadRunner
global getColorBlue, getColorRed, getColorDarkGreen, MoneybotURLDebug
global isKotlinCompiledBuild, convertBufferedSourceToInputStream

# New definitions
from com.moneydance.apps.md.controller.sync import AbstractSyncFolder, MDSyncCipher
from com.moneydance.apps.md.controller import LocalStorageCipher
from javax.swing import DefaultListModel
from java.lang import InterruptedException
from java.util.concurrent import CancellationException

try:
    if GlobalVars.EXTRA_CODE_INITIALISED: raise QuickAbortThisScriptException

    myPrint("DB", "Extra Code Initialiser loading....")

    def _extra_code_initialiser():
        GlobalVars.EXTRA_CODE_INITIALISED = True
        myPrint("B", ">> extra_code script initialised <<")

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

        localKeyHex = syncKeyHex = None
        try:
            wrapper = MD_REF.getCurrentAccounts()
            if wrapper is None:
                raise Exception("ERROR: Wrapper is none")

            localKeyHex = StringUtils.encodeHex(getFieldByReflection(getFieldByReflection(wrapper, "cipher"), "secretKey").getEncoded(), False)
            local_aes_iv_hex = StringUtils.encodeHex(getFieldByReflection(LocalStorageCipher, "aes_iv"), False)
            sync_aes_iv_hex = StringUtils.encodeHex(getFieldByReflection(MDSyncCipher, "aes_iv"), False)

            syncFolder = wrapper.getSyncFolder()
            if syncFolder is not None:
                syncKeyHex = StringUtils.encodeHex(getFieldByReflection(MDSyncCipher.getSyncCipher(wrapper.getSyncEncryptionPassword()), "secretKey").getEncoded(), False)
            del syncFolder, wrapper

            output = "%s:\n" \
                     "%s\n\n" %(_THIS_METHOD_NAME, "-" * len(_THIS_METHOD_NAME))

            output += "CONFIDENTIAL - DO NOT SHARE THIS INFORMATION UNLESS NECESSARY - STORE IN A SECURE LOCATION!\n\n"
            output += "Your dataset's local storage encryption key (hex): '%s'\n" %(localKeyHex)
            output += "Your sync encryption key (hex):                    '%s'\n" %("SYNC NOT ENABLED" if syncKeyHex is None else syncKeyHex)
            output += "\n\n"

            output += "Refer: '%s' ... to decrypt files from the command line (example):\n" %("https://wiki.openssl.org/index.php/Enc\n")
            output += "Dataset files:     openssl enc -aes-128-cbc -d -K %s -iv %s -in encryptedfile.txt -out decryptedfile.txt\n" %(localKeyHex, local_aes_iv_hex)
            output += "Sync folder files: openssl enc -aes-128-cbc -d -K %s -iv %s -in encryptedfile.txt -out decryptedfile.txt\n" %(syncKeyHex, sync_aes_iv_hex)
            del local_aes_iv_hex, sync_aes_iv_hex

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

        return localKeyHex, syncKeyHex


    _extra_code_initialiser()
    myPrint("DB", "Extra Code Initialiser finished....")

except QuickAbortThisScriptException: pass

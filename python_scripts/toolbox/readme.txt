Author: Stuart Beesley - StuWareSoftSystems (November 2020 thru January 2021 - a lockdown project ~500 programming hours)
Credit: Derek Kent(23) for his extensive texting and many hours on this project!
        Also thanks to Kevin(N), Dan T Davis, and dwg for their testing, input and OFX Bank help/input.....

Get more Scripts/Extensions from: https://yogi1967.github.io/MoneydancePythonScripts/

NOTE: I AM JUST A USER - I HAVE NO AFFILIATION WITH MONEYDANCE!

Minimum Moneydance version for use as an Extension: 2021 (build: 2012) - (Minimum version 2020 if run as a script)
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
# reset_relative_currencies.py                  (from Moneydance support)
# remove_ofx_account_bindings.py                (from Moneydance support)
# convert_secondary_to_primary_data_set.py      (from Moneydance support)
# remove_one_service.py                         (from Moneydance support)
# delete_invalid_txns.py                        (from Moneydance support)
# price_history_thinner.py                      (from Moneydance support)
# fix_dropbox_one_way_syncing.py                (from Moneydance support)
# force_change_account_currency.py              (from Moneydance support)
# fix_restored_accounts.py (check only)         (from Moneydance support)
# extract_all_attachments.py                    (from Moneydance support)
# fix_account_parent.py                         (from Moneydance support)
# fix_non-hierarchical_security_account_txns.py (from Moneydance support)
# show_open_tax_lots.py                         (author unknown)
# MakeFifoCost.py                               (author unknown)
# change-security-cusip.py                      (from Finite Mobius, LLC / Jason R. Miller)

Features:
- Main window shows various diagnostic data and MD Preferences

** Toolbox turns on all Moneydance's internal DEBUG messages at startup. This puts extra messages into the Console window
   This is a useful tip - i.e. have the console window open and you will get more information when running tasks (e.g. OFX)

NOTE: Where CMD is specified, this may be CTRL (or ALT) in Windows / Linux

CMD-I - This  Help Instruction Information

CMD-O - Copy all outputs to Clipboard

ALT-B - Basic Mode
- Basic mode: Buttons
    - EXPORT BACKUP (This calls the Moneydance function to backup your dataset)
    - Copy (Diagnostics) to Clipboard
    - Display MD Passwords (encryption and Sync)
    - Analyse Dataset Objects Size & Files
    - View MD Config.dict file
    - View MD Custom Theme file  (only appears if it exists)
    - View Console.log
    - Copy Console.log file to wherever you want
    - View your Java .vmoptions file (only appears if it exists) - INCLUDES VARIOUS INSTRUCTIONS TOO
    - Open MD Folder
      (Preferences, Themes, Console log, Dataset, Extensions, Auto-backup folder, last backup folder[, Install Dir])
    - Find my Dataset (Search for *.moneydance & *.moneydancearchive Datasets)
    - View memorised reports (parameters and default settings)
    - View Register Txn Sort Orders
    - View Check number settings
    - View Extensions details
    - Extract your Attachments (this decrypts and extracts your attachments to a directory of your choice) (extract_all_attachments.py)
    - Online (OFX) Banking Tools:
        - Search for stored OFX related data
        - View your installed Service / Bank logon profiles
        - View full list of all MD's Bank dynamic setup profiles (and then select one to view specific details)
        - View your Online saved Txns, Payees, Payments
        - Toggle Moneydance DEBUG (turns ON all MD internal Debug messages - same as view console)
    - DIAGnostics - Analise your  attachments (and Detect Orphans)
    - DIAGnostics - Can I delete a Security (tells you whether a security/stock is being used - and where)
    - DIAGnostics - List decimal places (currency and security). Shows you hidden settings etc.
    - DIAGnostics - Diagnose relative currencies (currency & security's key settings). If errors, then go to FIX below
    - DIAGnostics - View Categories with zero balance. You can also inactivate these below.
    - DIAGnostics - Show your open LOTs on stocks/shares (when using LOT control) (show_open_tax_lots.py)
    - Find my Sync Encryption password(s) in iOS Backup(s)

ALT-M - Advanced Mode
    - FIX - Make me a Primary Dataset (convert from secondary dataset to enable Sync)) (convert_secondary_to_primary_data_set.py)
    - FIX - Create Dropbox Sync Folder (creates the missing .moneydancesync folder if missing from Dropbox)
    - FIX - Change Moneydance Fonts
    - FIX - Delete Custom Theme file
    - FIX - Fix relative currencies (fixes your currency and security's key settings) (reset_relative_currencies.py)
    - FIX - FORCE change an Account's Currency (use with care. Does not update any transactions) (force_change_account_currency.py)
    - FIX - Inactivate all Categories with Zero Balance
    - Online (OFX) Banking Tools:
        - All basic mode settings plus:
        - Forget OFX Banking Import Link (so that it asks you which account when importing ofx files) (remove_ofx_account_bindings.py)
        - Delete OFX Banking Logon Profile / Service (these are logon profiles that allow you to connect to your bank) (remove_one_service.py)
        - Reset/Fix/Edit/Add CUSIP Banking Link. This is the link for downloaded securities....
        - Update OFXLastTxnUpdate Last Download Date for Online Txns
        - OFX Cookie Management (some options also required Hacker mode)
        - OFX Authentication Management (some options also required Hacker mode)
        - Delete Saved OnlineTxnList record/Txns (Advanced + Hacker mode only)
    - FIX - Thin/Purge Price History (allows you to thin/prune your price history based on parameters you input; also fix 'orphans') (price_history_thinner.py
    - FIX - Correct the Name of Root to match Dataset
    - FIX - Delete One-Sided Txns (delete_invalid_txns.py)
    - FIX - Account's Invalid Parent Account (script fix_account_parent.py)
    - FIX - Convert Stock to LOT Controlled and Allocate LOTs using FiFo method (MakeFifoCost.py)
    - FIX - Convert Stock to Average Cost Control (and wipe any LOT control records)
    - FIX - Non Hierarchical Security Account Txns (fix_non-hierarchical_security_account_txns.py)
    - FIX - Delete Orphaned/Outdated Extensions (from config.dict and .mxt files)
    - FIX - RESET Window Display Settings
            This allows you to tell Moneydance to forget remembered Display settings:
            1. RESET>> Just Window locations (i.e. it leaves the other settings intact).
            2. RESET>> Just Register Transaction Filters.
            3. RESET>> Just Register Transaction Initial Views (e.g. In investments, start on Portfolio or Security View
            4. RESET>> Window locations, Size, Sort Orders, One-line, Split Reg, Offset, Column Widths; Dividers, isOpen,
            isExpanded, isMaximised settings (this does not reset Filters or Initial views)
    - FIX - Check / fix MacOS Tabbing Mode on Big Sur (when set to always). It will allow you to change it to fullscreen or manual/never.
            More information here: https://support.apple.com/en-gb/guide/mac-help/mchla4695cce/mac
    - FIX - Fix Dropbox One Way Syncing (runs the fix_dropbox_one_way_syncing.py script / fix). Removes key "migrated.netsync.dropbox.fileid"

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
    - Allows User to Add/Change/Delete Settings/Prefs >> key/value in config.dict or LocalStorage() (./safe/settings)
    - Toggle all internal Moneydance DEBUG settings ON/OFF (same as viewing console)
    - Toggle other known DEBUG settings on (extra messages in Console)
    - Extract (a single) File from within LocalStorage. Extracts a LocalStorage file to TMP dir for viewing (file self destructs after MD restart)
    - Call Save Trunk File option....
    - Suppress the "Your file seems to be in a shared folder (Dropbox)" warning... (optional when condition exists)
    - Edit/Change/Delete an Object's Parameter keys
    - Remove Int/Ext Files from Filelist.
        >> External locations > Edits config.dict to remove references to external files for File/open - AND ALLOWS YOU TO DELETE THE FILES TOO
        >> Default / Internal locations > ALLOWS YOU TO DELETE THE Dataset from disk (this then removes it from the File/Open menu)

CMD-P - View parameters file (StuWareSoftSystems). Also allows user to Delete all, and/or change/delete single saved parameters

Menu - DEBUG MODE
    >> Turns on this Extension's own internal debug messages...

Menu - Auto Prune of Internal Backup files
    >> Toolbox makes extra backups of config.dict, ./safe/settings and custom_theme.properties. This setting auto-prunes
       keeping at least 5 copies of each and / or 5 days
<END>
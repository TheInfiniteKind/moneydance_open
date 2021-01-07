Author: Stuart Beesley - StuWareSoftSystems (written November/December 2020 - a lockdown project)
Credit: Derek Kent(23) for his extensive texting

Get more Scripts/Extensions from: https://yogi1967.github.io/MoneydancePythonScripts/

NOTE: I AM JUST A USER - I HAVE NO AFFILIATION WITH MONEYDANCE!

Minimum Moneydance version for use as an Extension: 2021 (build: 2012) - (Minimum version 2020 if run as a script)

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
# reset_relative_currencies.py              (from Moneydance support)
# remove_ofx_account_bindings.py            (from Moneydance support)
# convert_secondary_to_primary_data_set.py  (from Moneydance support)
# remove_one_service.py                     (from Moneydance support)
# delete_invalid_txns.py                    (from Moneydance support)

Features:
- Main window shows various diagnostic data and MD Preferences

NOTE: Where CMD is specified, this may be CTRL (or ALT) in Windows / Linux

CMD-I - This  Help Instruction Information

CMD-O - Copy all outputs to Clipboard

ALT-B - Basic Mode
- Basic mode: Buttons
    - EXPORT BACKUP (This calls the Moneydance function to backup your dataset)
    - Copy (Diagnostics) to Clipboard
    - Display MD Passwords (encryption and Sync)
    - View MD Config.dict file
    - View MD Custom Theme file  (only appears if it exists)
    - View Console.log
    - Copy Console.log file to wherever you want
    - View your Java .vmoptions file (only appears if it exists)
    - Open MD Folder
      (Preferences, Themes, Console log, Dataset, Extensions, Auto-backup folder, last backup folder[, Install Dir])
    - Find my Dataset (Search for *.moneydance & *.moneydancearchive Datasets)
    - View memorised reports (parameters and default settings)
    - View Register Txn Sort Orders
    - View Check number settings
    - View Extensions details
    - DIAGnostics - Can I delete a Security (tells you whether a security/stock is being used - and where)
    - DIAGnostics - List decimal places (currency and security). Shows you hidden settings etc.
    - DIAGnostics - Diagnose relative currencies. If errors, then go to FIX below
    - DIAGnostics - View Categories with zero balance. You can also inactivate these below.
    - DIAGnostics - Analise your  attachments (and Detect Orphans)
    - VIEW - OFX Related Data
    - Find my Sync Encryption password(s) in iOS Backup(s)

ALT-M - Advanced Mode
    - FIX - Make me a Primary Dataset (convert from secondary dataset to enable Sync))
    - FIX - Create Dropbox Sync Folder (creates the missing .moneydancesync folder if missing from Dropbox)
    - FIX - Change Moneydance Fonts
    - FIX - Delete Custom Theme file
    - FIX - Fix relative currencies
    - FIX - Inactivate all Categories with Zero Balance
    - FIX - Forget OFX Banking Import Link (so that it asks you which account when importing ofx files)
    - FIX - Delete OFX Banking Logon Profile / Service (these are logon profiles that allow you to connect to your bank)
    - FIX - Correct the Name of Root to match Dataset
    - FIX - Delete One-Sided Txns
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

ALT-G - GEEK OUT MODE
    >> Allows you to view raw settings
    - Search for keys or keydata containing filter characters (you specify)
    - ROOT Parameter keys
    - Local Storage - Settings
    - User Preferences
    - All Accounts’ preference keys
    - View single Object's Keys/Data (Account, Category, Currency, Security, Report / Graph, Reminder, Address, OFX Service, by UUID, TXNs)
    - All Sync Settings
    - All Online Banking Settings
    - All Settings related to window sizes/positions/locations etc
    - All Environment Variables
    - All Java Properties

Menu - HACKER MODE
    >> VERY TECHNICAL - DO NOT USE UNLESS YOU KNOW WHAT YOU ARE DOING
    >> Allows User to Add/Change/Delete a key/value in config.dict or LocalStorage() (./safe/settings)
    >> Toggle internal Moneydance DEBUG ON/OFF (use with care)
    >> Toggle internal Moneydance OFX DEBUG CONSOLE WINDOW ON/OFF (use with care)
    >> Change the internal Next Check Number look-back threshold (in days) from the default of 180 (temporary change only)

CMD-P - View parameters file (StuWareSoftSystems). Also allows user to Delete all, and/or change/delete single saved parameters

Menu - DEBUG MODE
    >> Turns on script debug messages...

<END>
The Infinite Kind (Moneydance) - Co-authored by Stuart Beesley in collaboration with Moneydance as a support tool

Original Author: Stuart Beesley - StuWareSoftSystems (Nov 2020 thru April 2022 - a lockdown project ~1000 coding hours)
Credit: Derek Kent(23) for his extensive testing and many hours on this project!
        Also thanks to Kevin(N), Dan T Davis, and dwg for their testing, input and OFX Bank help/input.....

Get more Scripts/Extensions from: https://yogi1967.github.io/MoneydancePythonScripts/

Minimum Moneydance version for use as an Extension: 2021.1 (build: 3056, ideally 3069+) - (Minimum version 2020 if run as a script)
(If you have installed the extension, but nothing happens, then check your Moneydance version)

This is a Python(Jython 2.7) script that runs inside of Moneydance via the Moneybot Python Interpreter
As such it has full access to Moneydance's internals.
However, where possible this script uses the published APIs. In certain circumstances, it calls internal functions.
The script will never change anything without your permission - and it will always ask you for such (several times).

DISCLAIMER: YOU USE THIS SCRIPT AT YOUR OWN RISK AND YOU ACCEPT ANY CONSEQUENCES OF CHANGING YOUR DATA!

PLEASE ALWAYS BACKUP YOUR DATA FIRST! You  can use the Create Backup (green) button top-left in Toolbox to do this.

PURPOSE

To enable the User to self-diagnose problems, or access key diagnostics to enable support to help
- Basic mode:                       The default mode. Very safe and contains useful / view options only
- Update Mode:                      Allows running of fixes/updates. CAN CHANGE DATA (you will always be asked to confirm first)
- Advanced Mode:                    Enables 'advanced' features. USE WITH CARE!
- Curious? View Internal Settings:  View technical information/settings in various places (this is readonly)

- The Toolbox offers the option to Backup first  - ALWAYS BACKUP (But this is your choice!)
- The Toolbox will *ALWAYS* make a copy of config.dict, custom theme file, LocalStorage() ./safe/settings before any changes
>> These backup files will have a unique (timestamp-like) number and _$SAVED$ appended to the end of the filename

>> Your dataset backups will be located wherever you choose to save them (USE THE 'CREATE BACKUP' button (top left in green)
>> Note the normal Moneydance Backup is a complete dataset, but does not include config.dict, custom theme file, extensions etc

- All updates (and other key messages) get written to the Moneydance console error log

NOTE: Toolbox will connect to the internet to gather some data. IT WILL NOT SEND ANY OF YOUR DATA OUT FROM YOUR SYSTEM. This is why:
1. At launch it connects to the Author's code site to get information about the latest version of Toolbox and version requirements
2. At various times it may connect to the Infinite Kind server to gather information about extensions and versions
3. Within the OFX banking menu, it can connect to the Infinite Kind server to get the latest bank connection profiles for viewing

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

Toolbox uses the the internal MD 'code' font for display and outputs. Typically a Monospaced font so text columns align.
>> If your language's double-byte characters do not display properly, then change in update mode; General Tools>Set MD Fonts
>> Change 'code' font. Please only use a fixed-width Monospaced so that column alignments are maintained (but your choice).

Features:
- Main window shows various diagnostic data and MD Preferences

** Toolbox turns on all Moneydance's internal DEBUG messages at startup. This puts extra messages into the Console window
   This is a useful tip - i.e. have the console window open and you will get more information when running tasks (e.g. OFX)

NOTE: Where CMD is specified, this may be CTRL (or ALT) in Windows / Linux

CMD-I           This  Help Instruction Information
CMD-F           Search for text in display windows
CMD-O           Copy all outputs to Clipboard
CMD-SHIFT-U     Examine an object's raw data - enter the Object's UUID
CMD-SHIFT-+     Unlock Toolbox (Contact Author for password and usage) - (Might be CMD-SHIFT-= on some keyboards)

Toolbox also installs two new Extensions Menu options (which allow the user to select register transactions before running):
    - Toolbox: Move Investment Transactions
    - Toolbox: Total Selected Transactions

TOOLBAR / MENU BAR Contains the following:
    - Toolbox Options menu
    - Help/About menu
    - Button: Launch Console Window (opens the Moneydance Help>Show Console Window)
    - Button: Save Console Log (to a file of your choosing)
    - Button: Open MD Folder (Preferences, Themes, Console log, Dataset, Extensions, Auto-backup folder, last backup folder[, Sync Dir][, Install Dir])
    - Button: Copy/Save/Print Diagnostics below (to Clipboard (copies the main screen output to clipboard), or save to file, or print)

POPUP Output/Report Window(s):
    - Top, Bottom: Jump to beginning or end of display
    - Wrap Contents: Turns on line wrap. Also enables print 'fit-to-width'
    - Print, Save to file: Prints the contents or saves to file.

Basic Mode (Default at launch) - Use ALT-M to toggle between Basic and Update modes
- Basic mode: Buttons
    - CREATE BACKUP (This calls the Moneydance 'Export Backup' function to backup your dataset)
    - Analyse Dataset Objects Size & Files
    - Find my Dataset (Search for *.moneydance & *.moneydancearchive Datasets)
    - MENU: General Tools (contains a variety of general Diagnostics, Fixes and Tools...)
        - Display Dataset Password/Hint and Sync Passphrase
        - View MD Console (the whole file - searchable)
        - View MD Config.dict file
        - View MD Custom Theme file  (only appears if it exists)
        - View your Java .vmoptions file (only appears if it exists) - INCLUDES VARIOUS INSTRUCTIONS TOO
        - View Extensions details
        - View memorised reports (parameters and default settings)
        - Find my Sync Encryption password(s) in iOS Backup(s)
        - Execute the 'older' Import QIF file and set parameters for import (useful if you want to import Account Structure Only)
        - Convert a TimeStamp number into a readable date/time (display only)
    - MENU: Online (OFX) Banking Tools:
        - Search for stored OFX related data
        - View your installed Service / Bank logon profiles
        - View full list of all MD's Bank dynamic setup profiles (and then select one to view specific details)
        - View your Security's hidden CUSIP settings (These link your downloads on Investment Securities to MD Securities)
        - View your Online saved Txns, Payees, Payments
        - View your active accounts' calculated reconcile window auto 'as of' dates (Bank/Credit Cards/Investment)
        - View your accounts' calculated reconcile window auto 'as of' date (active accounts only)
        - Toggle Moneydance DEBUG (turns ON all MD internal Debug messages - same as view console)
    - MENU: Accounts & Categories tools
        - View Check number settings
        - DIAGnostics - View Categories with zero balance. You can also inactivate using Update mode.
        - DIAGnostics - View Accounts' shouldBeIncludedInNetWorth() settings...
    - MENU: Currency & Security tools:
        - DIAGnostics - Diagnose currencies / securities (including relative currencies) If errors, then go to FIX below
        - DIAGnostics - Can I delete a Security (tells you whether a security/stock is being used - and where)
        - DIAGnostics - Can I delete a Currency (tells you whether a currency is being used - and where)
        - DIAGnostics - List decimal places (currency & security). Shows you the hidden setting and related data.
        - DIAGnostics - Show your open LOTs on stocks/shares (when using LOT control) (show_open_tax_lots.py)
        - DIAGnostics - Diagnose currency / security's current price hidden 'price_date' field. If warnings, then go to FIX below
    - MENU: Transactions tools
        - View Register Txn Sort Orders
        - Extract your Attachments (this decrypts and extracts your attachments to a directory of your choice) (export_all_attachments.py)
        - DIAGnostics - Analise your  attachments (and Detect Orphans)

Menu - CURIOUS? VIEW INTERNAL SETTINGS (Read-Only - very safe)
    >> Allows you to view internal / raw settings / data
    - Search for a key/data (in most places  - but not txns)
    - Show ROOT Account's Parameter Keys and data
    - Show Dataset's Local Storage Keys and data (from ./safe/settings)
    - Show All User Preferences loaded into Memory (from config.dict)
    - Show Accounts' Parameter's Keys and Data
    - Show an Obj's settings/data (Acct, Cat, Curr, Security, Reports, Reminders, Addrs, OFX, by UUID, TXNs)
    - Show All Sync Settings
    - Show All Online Banking (Searches for OFX) Settings
    - Show all Settings relating to Window Locations/Sizes/Widths/Sort Order/Filters/Initial Reg View etc..
    - Show all Java JVM System Properties
    - Show all Operating System Environment Variables

ALT-M - Update Mode (** NOTE: Some menu items will disable if currency / security data issues detected. Some only available from 2021.2 onwards)
    All basic mode settings plus (note the text of buttons turn red when update mode enabled):
    - These four buttons will only appear if they are necessary / possible in your system, on the last button row
        - FIX - Make me a Primary Dataset (convert from Secondary dataset to enable Sync) (convert_secondary_to_primary_data_set.py)
        - FIX - Zap Invalid Window Locations (Appears if any of your saved windows are 'off screen')
        - FIX - Create Dropbox Sync Folder (creates the missing .moneydancesync folder if missing from Dropbox)
        - FIX - Check / fix MacOS Tabbing Mode on Big Sur (when set to always). It will allow you to change it to fullscreen or manual/never.
                More information here: https://support.apple.com/en-gb/guide/mac-help/mchla4695cce/mac
        - FIX - Fix Remove legacy Dropbox Migrated Sync Key (runs the fix_dropbox_one_way_syncing.py / reset_sync_and_dropbox_settings.py script / fix).
        - FIX - FIX: REGISTER MONEYDANCE. Allows you to enter your Moneydance license key
    - MENU: General Tools (contains a variety of general Diagnostics, Fixes and Tools...)
        - FIX - RESET Window Display Settings
                This allows you to tell Moneydance to forget remembered Display settings:
                1. RESET>> Just Window locations (i.e. it leaves the other settings intact).
                2. RESET>> Just Register Transaction Filters.
                3. RESET>> Just Register Transaction Initial Views (e.g. In investments, start on Portfolio or Security View
                4. RESET>> Window locations, Size, Sort Orders, One-line, Split Reg, Offset, Column Widths; Dividers, isOpen,
                isExpanded, isMaximised settings (this does not reset Filters or Initial views)
        - FIX - Rename this dataset Rename this dataset (within the same location)
        - FIX - Relocate this dataset back to the default 'internal' location
        - FIX - Relocate this dataset to another location [Note: IK do not recommend this]
        - FIX - Cleanup MD's File/Open list of 'external' files (does not touch actual files)
        - DELETE Files from Menu>File>Open list and also from DISK (Removes files from 'Internal' and 'External' locations).
            >> External locations > Edits config.dict to remove references to external files for File/open - AND ALLOWS YOU TO DELETE THE FILES TOO
            >> Default / Internal locations > ALLOWS YOU TO DELETE THE Dataset from disk (this then removes it from the File/Open menu)
        - FIX - Set/Change Default Moneydance FONTS
        - FIX - Delete Custom Theme file
        - FIX - Delete Orphaned/Outdated Extensions (from config.dict and .mxt files)
    - MENU: Online (OFX) Banking Tools:
        - Forget OFX Banking Import Link (so it asks which account when importing ofx files) (remove_ofx_account_bindings.py) (MD versions < 2022)
        - Delete OFX Banking Logon Profile / Service (these are logon profiles that allow you to connect to your bank) (remove_one_service.py)
        - Cleanup missing Online Banking Links (NOTE: This is always called when running 'Delete OFX Banking Logon Profile / Service' above
        - Reset/Fix/Edit/Add CUSIP Banking Link. This is the link for downloaded securities.... (remove_ofx_security_bindings.py and change-security-cusip.py)
        - Reset ALL OFX Last Txn Update Dates (default, OFX and MD+) (MD build 4074 onwards)
        - Update OFX Last Txn Update Date (Downloaded) field for an account (MD versions >= 2022 can now use Online menu, Setup Online Banking, Reset Sync Date)
        - Delete Single cached OnlineTxnList Record/Txns
        - Delete ALL cached OnlineTxnList record/Txns (delete_intermediate_downloaded_transaction_caches.py)
        - OFX Authentication Management (various functions to manage authentication, UserIDs, ClientUIDs)
            - SUBMENU: OFX Authentication Management
                - Clear the Authentication Cache (Passwords) for One Service / Bank Profile
                - Clear ALL Authentication Cache (Passwords)
                - Edit/Setup (multiple) UserIDs / Passwords (executes a special script) (ofx_populate_multiple_userids.py)
                - Edit stored authentication passwords linked to a working OFX Profile
                - Manual Edit of stored Root UserIDs/ClientUIDs
        - OFX Cookie Management (requires Advanced mode)
        - Force MD+ name cache & access tokens rebuild - Names and Access Tokens should rebuild themselves - MD Version 2022 onwards. USE WITH CARE. (requires Advanced mode)
        - Export your Moneydance+ (Plaid) license (keys) to a file (for 'transplant') - MD Version 2022 onwards. READONLY (requires Advanced mode)
        - Import ('transplant') your Moneydance+ (Plaid) license (keys) from a file (exported by Toolbox) - MD Version 2022 onwards. USE WITH CARE. (requires Advanced mode)
        - ZAP Dataset's Moneydance+ (Plaid) settings (requires Advanced mode) - MD Version 2022 onwards. USE WITH CARE. WILL REQUIRE RE-REGISTRATION!
        - USAA ONLY: Manually 'prime' / overwrite stored Root UserIDs/ClientUIDs
        - USAA Only: Executes the special script to create a working USAA OFX Profile (ofx_create_new_usaa_bank_custom_profile.py)

    - MENU: Accounts & Categories tools
        - FIX - Inactivate all Categories with Zero Balance
        - FIX - Edit an Account's shouldBeIncludedInNetWorth() setting
        - FIX - FORCE change an Account's Type (use with care. Does not update any transactions) (set_account_type.py)
        - FIX - FORCE change an Account's / Category's Currency (use with care. Does not update any transactions) (force_change_account_currency.py)
        - FIX - FORCE change ALL Accounts' / Categories' currencies (use with care. Does not update any transactions) (force_change_all_currencies.py)
        - FIX - FORCE Change Accounts / Categories [& Securities] FROM Currency TO Currency
        - FIX - Account's Invalid Parent Account (script fix_account_parent.py)
        - FIX - Correct the Name of Root to match Dataset
    - MENU: Currency & Security tools:
        - FIX - Fix currencies / securities (including relative currencies) (fixes your currency & security's key settings) (reset_relative_currencies.py)
        - FIX - Edit a Security's (hidden) Decimal Place setting (adjusts related Investment txns & Security balances accordingly).  >> 2021.2 onwards
        - FIX - Merge 'duplicate' securities (and related Investment txns) into one master security record (by TickerSymbol).        >> 2021.2 onwards
        - FIX - Detect and merge/fix duplicate Securities within same Investment Account(s)
        - FIX - Fix currency / security's current price hidden 'price_date' field. Also corrects current price whilst fixing too..   >> 2021.2 onwards
        - FIX - Manually edit a Security/Currency's current price hidden 'price_date' field
        - FIX - Detect and fix (wipe) LOT records where matched Buy/Sell records are invalid
        - FIX - Convert Stock to LOT Controlled and Allocate LOTs using FiFo method (MakeFifoCost.py)
        - FIX - Convert Stock to Average Cost Control (and wipe any LOT control records)
        - FIX - Detect and fix Investment Security records not properly linked to Security Master records
        - FIX - Thin/Purge Price History (allows you to thin/prune your price history based on parameters you input; also fix 'orphans') (price_history_thinner.py)
        - FIX - Fix invalid relative currency (& security) rates >> fixes relative rates where <= (1.0/9999999999) or >= 9999999999) (fix_invalid_currency_rates.py)
        - FIX - Delete invalid price history records where rate <= (1.0/9999999999) or >= 9999999999.
        - FIX - FORCE change an Account's / Category's Currency (use with care). (Does not update any transactions) (force_change_account_currency.py)
        - FIX - FORCE change ALL Accounts' / Categories' currencies (use with care). (Does not update any transactions) (force_change_all_currencies.py)
        - FIX - FORCE Change Accounts / Categories [& Securities] FROM Currency TO Currency
    - MENU: Transactions tools
        - Move/Merge Investment transactions from one account into another. DISABLED >> NOW RUN FROM EXTENSIONS MENU (you can pre-select register txns first)
        - FIX - Diagnose Attachments - DELETE Orphan attachments (allows you to delete Orphan attachments from Disk ** Syncing must be disabled **)
        - FIX - Non-Hierarchical Security Acct Txns (& detect Orphans) (fix_non-hierarchical_security_account_txns.py & fix_investment_txns_to_wrong_security.py)
        - FIX - Delete One-Sided Txns (delete_invalid_txns.py)
        - FIX - Reverse Transaction Amounts between dates (reverse_txn_amounts.py)
        - FIX - Reverse Transaction Exchange rates between dates (reverse_txn_amounts.py)
        - FIX - Detect and fix transactions assigned to 'root' account (Offers options to display / fix these transactions)

ALT-SHIFT-M - Menu - ADVANCED MODE (button turns red when enabled)
    >> SPECIAL ADVANCED FEATURES - USE WITH CARE!
    - Toggle other known DEBUG settings on (extra messages in Console)
    - Toggle all internal Moneydance DEBUG settings ON/OFF (same as viewing console)
    - Extract a (single) file from within LocalStorage. Decrypts a LocalStorage file to TMP dir for viewing (file self destructs after MD restart)
    - Peek at an encrypted file located in your Sync Folder.... Decrypts a Sync (e.g. Dropbox) file and shows it to you...
    - Shrink Dataset. This function deletes MD's log files of all prior changes (not needed).. Typically these are .txn, .mdtxn files...
    - Import (a single) File back into LocalStorage. Encrypts a file of your choosing and puts it into LocalStorage/safe/TMP...
    - Allows User to Add/Change/Delete Settings/Prefs >> key/value in config.dict or LocalStorage() (./safe/settings)
    - Edit/Change/Delete an Object's Parameter keys (this can change data in your dataset/database directly)
    - Clone Dataset's structure (purge transactional data) - Copy dataset keeping structures, purging all transactional data.
    - Call Save Trunk File option.... Immediately flushes all in memory changes to disk, including your dataset (rather than wait for restart)
    - Force a refresh/PUSH of your local dataset to Sync. Push new Sync data (and rebuild remote copies). Use carefully!
    - Force disable/turn Sync OFF (This just sets your Sync method to None - all other settings are preserved. You can turn it back on again)
    - Toggle Sync Downloading of Attachments (Normally this defaults to ON; Change to OFF to prevent attachments downloading via Sync)
    - Force reset Sync settings (This resets all Sync settings, changes your Sync ID, and turns Sync off. You can then re-enable it for a fresh Sync)
    - DEMOTE your Primary Sync dataset/node back to a Secondary Node
    - Suppress the "Your file seems to be in a shared folder (Dropbox)" warning... (optional when condition exists)

CMD-P - View parameters file (StuWareSoftSystems). Also allows user to Delete all, and/or change/delete single saved parameters

Menu - DEBUG MODE
    >> Turns on this Extension's own internal debug messages...

Menu - Auto Prune of Internal Backup files
    >> Toolbox makes extra backups of config.dict, ./safe/settings and custom_theme.properties. This setting auto-prunes
       keeping at least 5 copies of each and / or 5 days

Thanks for reading.....

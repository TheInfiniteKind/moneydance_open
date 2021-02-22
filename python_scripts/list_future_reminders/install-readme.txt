Author: Stuart Beesley - StuWareSoftSystems 2020-2021
Visit: https://yogi1967.github.io/MoneydancePythonScripts/ for more downloads and information

THESE ARE EXTENSIONS / SCRIPTS FOR MONEYDANCE WRITTEN IN PYTHON (JYTHON 2.7)
The scripts and extensions are identical. The extensions are simply a packaged script version.

The Extensions will only run on Moneydance version 2021 build 2012 onwards... The scripts don't have this requirement
NOTE: You may need to download the MD preview version from: https://infinitekind.com/preview
(If you have installed the extension, but nothing happens, then check your Moneydance version)

Extensions have a file extension of *.mxt
Scripts have a file extension of *.py
If you downloaded a zip file (extension *.zip) then unzip first in a directory of your choice to get at the file(s)

Toolbox is an Extension format only - i.e. just the Toolbox.mxt file
All the others have both Extension (*.mxt) and Script (*.py) formats

HOW DO YOU CHOOSE?
- If you just want to run once and then never again, or very infrequently, choose the Script version.
- If you want the functionality always available from the Moneydance extension menu, choose Extension

To run Extensions:
1) Install the Extension. Load Moneydance, Menu>Extensions>add from file>choose <extension_name>.mxt file
2) Accept the warning that the extension is unsigned / missing (this simply means that Moneydance have not signed / verified my extension). Click Install Extension.
3) Once its installed, restart Moneydance.
4) From now on, just click Menu>Extensions and the name of the Extension

To run Scripts:
1) Load Moneydance. Menu>Window>Show Moneybot Console
2) Open Script>choose <script_name>.py file
3) Click RUN (and not run snippet)
4) That's it.... Repeat these steps each time.

All Extensions/Scripts available:
toolbox:                                View Moneydance settings, diagnostics, fix issues, change settings and much more...
extract_data:                           Extract various data to screen and/or csv.. Consolidation of:
- stockglance2020                       View summary of Securities/Stocks on screen, total by Security, export to csv
- extract_reminders_csv                 View reminders on screen, edit if required, extract all to csv
- extract_currency_history_csv          Extract currency history to csv
- extract_investment_transactions_csv   Extract investment transactions to csv
- extract_account_registers_csv         Extract Account Register(s) to csv along with any attachments

list_future_reminders:                  View future reminders on screen. Allows you to set the days to look forward

useful_scripts: A zip collection of ad-hoc scripts for specific tasks. Just unzip and select the script you want. Includes:
- calculate_moneydance_objs_and_datasetsize.py: Analyse your dataset, object counts, file sizes, and find other known datasets
- extract_all_attachments.py: extract all your attachments out of Moneydance to a folder of your choice
- orphan_attachments.py: scans your attachments and detects if any are orphaned (and other related errors)
- demo_account_currency_rates.py: demo script for beginner coders with some simple Moneydance API calls etc...
- demo_calling_import_functions.py: demo script to show how to call deep API importFile() method and bypass UI popups
- ofx_create_new_usaa_bank_profile.py: script to create a new bank logon / service profile to connect to USAA Bank within Moneydance
- ofx_fix_existing_usaa_bank_profile.py: script that edits/updates your existing USAA bank profile so that it can connect within Moneydance
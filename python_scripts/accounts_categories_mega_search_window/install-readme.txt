!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!! From June 2021 on, most extensions available via the Moneydance menu >> Manage Extensions - Check there first !!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

Author: Stuart Beesley - StuWareSoftSystems 2020-2023
Visit: https://yogi1967.github.io/MoneydancePythonScripts/ for more downloads and information

THESE ARE EXTENSIONS / SCRIPTS FOR MONEYDANCE WRITTEN IN PYTHON (JYTHON 2.7)
The scripts and extensions are identical. The extensions are simply a packaged script version.

The Extensions will only run on Moneydance version 2021.1 (build 3056 onwards - ideally 3069+)...
The standalone script versions require a minimum of 2019.4 (build 1904 onwards)...
(If you have installed the extension, but nothing happens, then check your Moneydance version)

Extensions have a file extension of *.mxt
Scripts have a file extension of *.py
If you downloaded a zip file (extension *.zip) then unzip first in a directory of your choice to get at the file(s)

########################################################################################################################
NOTE: *.pyc files are CPython byte code files generated from the .py script. These are "helpers" to the Jython
interpreter. Within the .mxt file you may also find a *$py.class file. This is a compiled version of the script
for faster launch times. Some of my scripts are large and these "helpers" prevent a "method too large" RuntimeException.
You don't normally need to worry about all this, but if you want to run the .py script manually (e.g. in Moneybot),
then please ensure the .pyc file is placed in the same location as the .py script you are running.

As of Feb 2023 the precompiled versions (*$py.class files) are included with a bootstrap.py loader for faster
load times (avoids initial compile on launch). If the bootstrap fails to load this, then it will just run the script...
########################################################################################################################

Toolbox and net_account_balances are Extension format only - i.e. just the Toolbox.mxt file
All the others have both Extension (*.mxt) and Script (*.py) formats available within the zip.

HOW DO YOU CHOOSE?
- If you just want to run once and then never again, or very infrequently, choose the Script version.
- If you want the functionality always available from the Moneydance extensions menu, choose Extension

To install/run Extensions:
1) Launch the Moneydance application
2) Double-click the .mxt file (this may not work if you do not have .mxt extensions associated with Moneydance)
   .. or drag and drop the .mxt file onto the Moneydance left side bar
   .. or Menu>Extensions>add from file>choose <extension_name>.mxt file, then click open/install
3) Accept the warning that the extension is unsigned / missing (this simply means that Moneydance have not signed / verified my extension). Click Install Extension.
4) Once its installed, restart Moneydance.
5) From now on, just click Menu>Extensions and the name of the Extension

To run Scripts:
1) Load Moneydance. Menu>Window>Show Moneybot Console
2) Open Script>choose <script_name>.py file
3) Click RUN (and not run snippet)
4) That's it.... Repeat these steps each time.

All Extensions/Scripts available:
Toolbox:                                View Moneydance settings, diagnostics, fix issues, change settings and much more
                                        + Extension Menus: Total selected transactions & Move Investment Transactions
Custom Balances (net_account_balances): Summary Page (HomePage) widget. Display the total of selected Account Balances

Extract Data:                           Extract various data to screen and/or csv.. Consolidation of:
- stockglance2020                       View summary of Securities/Stocks on screen, total by Security, export to csv
- extract_reminders_csv                 View reminders on screen, edit if required, extract all to csv
- extract_currency_history_csv          Extract currency history to csv
- extract_investment_transactions_csv   Extract investment transactions to csv
- extract_account_registers_csv         Extract Account Register(s) to csv along with any attachments

List Future Reminders:                  View future reminders on screen. Allows you to set the days to look forward
Accounts Categories Mega Search Window: Combines MD Menu> Tools>Accounts/Categories and adds Quick Search box/capability
Security Performance Graph:             Graphs selected securities, calculating relative price performance as percentage

extension_tester:                       Demo extension/scripts for coders wanting to build Moneydance Python extensions

useful_scripts: A zip collection of ad-hoc scripts for specific tasks. Just unzip and select the script you want. Includes:
- calculate_moneydance_objs_and_datasetsize.py: Analyse your dataset, object counts, file sizes, and find other known datasets
- extract_all_attachments.py: extract all your attachments out of Moneydance to a folder of your choice
- orphan_attachments.py: scans your attachments and detects if any are orphaned (and other related errors)
- demo_account_currency_rates.py: demo script for beginner coders with some simple Moneydance API calls etc...
- demo_calling_import_functions.py: demo script to show how to call deep API importFile() method and bypass UI popups
- ofx_create_new_usaa_bank_custom_profile.py: script that creates a new custom USAA bank logon profile so that it can connect within Moneydance
- ofx_populate_multiple_userids.py: script that allows you to modify a working OFX profile and populate with multiple UserIDs
- import_categories.py: script that allows you to import from a CSV file to create new Categories

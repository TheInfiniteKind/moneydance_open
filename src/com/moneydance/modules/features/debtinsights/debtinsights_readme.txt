Help / Guide for extension: Debt Insights.
------------------------------------------------------------------------------------------------------------------------
Original author:            Robert Schmid (2001)
Significantly updated by:   Stuart Beesley - StuWareSoftSystems 2023

>> Runs on MD2015.8(1372) onwards....
------------------------------------------------------------------------------------------------------------------------

WARNING: This is a tool to help you understand your debt position.
         YOU CANNOT RELY ON THESE FIGURES FOR ACTUAL DEBT / INTEREST PAYMENTS >> ALWAYS REFER TO YOUR ACTUAL STATEMENTS!
------------------------------------------------------------------------------------------------------------------------

This extension is intended to show additional details regarding your debts (Credit Cards and Loans, excl. Liabilities)
It comprises two parts, described below:

Installation
------------
The extension is installed using the Extensions → Manage Extension menu.

Summary screen widget: Debt Insights: CCards
--------------------------------------------
A summary screen widget that lists your credit cards, balance(s) and a selectable middle column that can show:
- Credit limit (based on the account's Credit Limit setting)
- Available credit (calculated as credit limit less the applicable balance)
- Available credit graph
- Credit used graph
- APR (Annual Percentage Rate) i.e. Interest Rate (based on the account's APR setting)
- Next Interest Payment information (based on the account's APR setting)
- Next payment information (based on the account's Payment Plan setting)
The last column provides the usual selections of Balance, Cleared Balance or Current Balance.

** NOTEs:   Available Credit and Interest Payment will show zero when avail credit < 0 or interest > 0
            Applicable balance for calculations will depend on the config screen where you can select:
                - Dynamic - based on the widget selected balance, or...
                - Fixed - according to the balances selected on the setup screen...
                - and you can override MD's Payment Plan choice to force usage of Balance (not Cleared/Current Balance)
            Next Payment will never exceed the credit card balance, or zero.

The widget will be displayed on the summary screen.
- Use the down/right arrow icon left of the the header / title to collapse/expand the whole widget.
- Use the +/- (if showing) to expand/collapse accounts/sub account row(s)...

- Some of the information that is displayed depends on values that have been set within the Account's setup page.
    - Use MD Menu / Tools / Accounts / <select account> / Edit to edit the Account's settings
    - This Account Edit Window includes the following fields which impact how Debt Insights works:
    - APR, Credit Limit & Payment Plan...

See next section for information on how you can change the name from the default name of 'Debt Insights: CCards'
to anything you like along with other options that can be configured.

Debt Insights (Debt Overview) Window
------------------------------------
On the Extensions menu, the selection Debt Insights (Debt Overview) will display a popup window which groups credit
cards and loans together, displaying sortable columns with balance, payment information, interest, credit limit and APR.
The calculations mirror the widget, but are always in your base currency. NOTE: Each account row is a total of that row
plus all its sub accounts.

The bottom row totals each column with the exception of the APR columns which displays an effective APR across all
accounts.

An Asterisk (*) alongside a header indicates tool tips are available.

On this display, accounts can be flagged as follows:
- If payment is less than accrued interest - RED flag
- If credit card balance is more than 50% of the credit limit - YELLOW flag
- If APR is going to change within 90 days - YELLOW flag

The following options are available from this screen:
- Set Widget Name – This changes the name displayed on the summary page

- Toggle Enhance Colors - This changes the color of some values to green when positive.

- Override MD's Payment Plan to always use Balance - This allows you to override the Account's setting in Tools/Accounts
  Payment Plan from any of the options that specify Cleared or Current Balance to use Balance instead (where set).

- Credit Calculations Balance Type:
    - Use Widget's Dynamic Settings – This uses whatever you have set the summary page to display / calculate.
    - or Always use – This forces a particular balance type to be used in this popup window and on all the widget's
      credit calculations.

- Convert all Widget's values to Base Currency - This changes the widget's display on the account rows to show the value
  in your base currency, rather than local currency. NOTE: The totals and popup window always convert to base currency.

Key points:
-----------
- Inactive accounts are always ignored, everywhere...
- As mentioned, the Extensions Menu Popup window allows you to configure key components of the widget and calculations..
- The MD Account Settings for an account affect the calculations...
- Liability accounts are excluded. Only Credit Cards and Loan accounts are included.
- This tool does NOT account for capital calculations / repayments... It calculates interest, or Payment Plan settings

Config.dict entries
-------------------
Some settings beyond the normal “Extension” settings can be present in config.dict when using this extension.
For completeness here are listed the additions that Debt Insights makes to the file.

The standard entry for the extension is:
"debtinsights" = {
 "id" = "debtinsights"
 "verify" = "N"
}

All extensions have an entry similar to this in the file.

Debt Insights will also save some of your selections, these selections are similar to:
"debtinsights_balancetypechoice" = "0"
"debtinsights_enhancedcolors" = "n"
"debtinsights_widgetname" = "Debt Insights: : CCards"
"debtinsights_debug" = "n"
"debtinsights_forcebasecurrency" = "n"
"debtinsights_overridepaymentplanbalance" = "n"

>> ** ALL ** these settings can be maintained by the user in the popup window GUI...

You will see a number of other settings in the file
"gui.debtinsights_location" = "196x352"
"gui.debtinsights_size" = "1236x350"
These specify the location and the size of the Debt Insights: Overview popup window. These are automatically saved by
using/closing the Popup window

You should NOT have cause to manually edit any of these settings. However, if required, with Moneydance closed, you can
use a text editor to carefully edit the file and remove these entries, save, and restart Moneydance.
------------------------------------------------------------------------------------------------------------------------
Thanks for reading...

Get more Scripts/Extensions from: https://yogi1967.github.io/MoneydancePythonScripts/

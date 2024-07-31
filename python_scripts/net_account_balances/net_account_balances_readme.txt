Author: Stuart Beesley - StuWareSoftSystems (March 2021 - a lockdown project) - Last updated January 2024
Credit: (slack: @dtd) aka Dan T Davis for his input, testing and suggestions to make a (MUCH) better product......

Custom Balances works with 2021.1(3056) and newer.
DISCLAIMER: THIS EXTENSION IS READONLY (IT DOES NOT CHANGE DATA) >> BUT YOU USE AT YOUR OWN RISK!

DEFINITIONS:
- CB means this extension / Custom Balances
- Dates are typically mentioned in this guide in the format yyyymmdd (e.g. 15th January 2025 = 20250115)

INSTALLATION:
- Double-click the .mxt file (this may not work if you do not have .mxt extensions associated with Moneydance)
  ... or Drag & drop .mxt onto left side bar, or Extensions, Manage Extensions, add from file to install.
- Once installed, visit Preferences > Summary Page, and then move the new widget to the desired Summary Page location

PURPOSE:
This extension creates a 'widget' that calculates / displays totals on the Moneydance Summary Page (Home Page)

- This widget allows you to select multiple accounts / categories / Securities and filter Active/Inactive items
- The balances are totalled and displayed on the Summary Page widget, converted to the Currency you select to display

- You could create a Net Worth Balance for example; or total particular securities, or total certain accounts...
- Or total expenses by date - e.g. 'how much did I spend on fuel last month?'

- You can use it for anything really. Warning >> you can create 'nonsense' totals if you like too....

- To configure the widget, select an existing row on the Summary Page, or use the Extensions Menu

- You can add/delete/move as many rows as you require, and then configure the selected items per row
- You can select to total together Accounts / Categories (by date range) / Securities....

- You can change the name of each row, the balance type, and the currency to display. Also Active/Inactive items.

------------------------------------------------------------------------------------------------------------------------
UPGRADE NOTES:
If you have been using recent PREVIEW builds (since 1038 / November 2023) then you may have configured
'Final Maths Calculation' (FMC), and also come across 'absorbed into other UORs' and also 'not absorbed'. These settings
have gone, and have been migrated into:
a) 'Post UOR maths calculation' (PUM) (replacing FMC absorbed), or...
b) 'Format Display Adjust' (FDA)      (replacing FMC non-absorbed).

DEFINITION: 'absorbed' in this context means that the math takes place before being rolled upwards into other
UORs that refer to this row... I.e. 'non-absorbed' means the impact of the maths stays on this row alone.

There is a new exciting Formula (FOR) capability with this build. This in effect can replace RMC, UOR, PUM. You can
continue to use these, or use the new superior formula capability. You can actually combine all these, but this is
NOT RECOMMENDED as it's duplicative and confusing to understand. RECOMMENDATION: if you want to use formulas, then
manually update your settings to only use formula. Average by is not affected by this change. FDA and *100 can remain,
or be replaced by formula - your choice.

Formula gives you the ability to add multiple rows together, or perhaps subtract one row from another (for example).
These types of calculations are quite tricky to perform using the 'old' UOR maths.
------------------------------------------------------------------------------------------------------------------------

LET'S GET STARTED:

The GUI config screen utilises a split screen to show you the main settings (top) and the accounts picklist (bottom).
There is a draggable divider that you can drag/move up down if required. When the screen resolution is not large enough,
the divider move auto-move upwards so that bottom section can be seen. If this occurs, then the top section becomes
scrollable (like the bottom section). The screen size and divider locations do not save and will reset every MD session.

FIRST: If the configuration area is too large on your screen, and you cannot see enough of the 'Account Selection List'
then click 'Hide Controls' (top right). This will shrink the top section further (still scrollable). You can un-click
'hide controls' at any time. If you don't like the divider location, just drag/move it manually.

Let's start with a row that is <NOT CONFIGURED>. Give it a name - like Credit Card Debt.
Now select all your credit cards from the account selection list. Click each one. Hit Save All Settings.
See the result on the summary page.You did note the installation bit, right? Putting the widget in place?
You should now have a row which says "Credit Card Debt.    £(not too much hopefully)"
That's the basics of CB (to create custom calculations)... "Custom Balances"... But you can do so many things now!

How about an account which has a minimum balance? New row - "Checking Account I keep too low" (minimum balance 100)
Click that account to pick it, select "Hide Row" if >=X and set X to 100
If it goes below 100, it will appear, and you can even make it blink.

You can also monitor your spending. E.g. Groceries spend this month? So, create a row, and find your groceries category.
Select "Month to date" in Inc/Exp Date Range. If you have multiple groceries categories, you can select them all.
Save and look.

Now that you have an inkling of the custom balance power potential here, go explore.

------------------------------------------------------------------------------------------------------------------------
CREATING ROWS AND SAVING:

Select Row:     Allows you to pick the row you want to work on. (Details below)
Search Box:     Allows you to set up what rows you see in the widget via GroupID (Details below)
Warnings Box:   Provides warnings based on 'illogical' selections (Details below)
Insert Row Before/Insert Row After/Delete Row/Move Row/Duplicate Row: Allows you to create rows in any order.
Reload Settings/Backup Config/Restore Config: Allows you to restore or save your configuration.
------------------------------------------------------------------------------------------------------------------------

CHOICES/CONFIGURATION FOR A ROW:

- Row Name: Name for the row. (Details below)
            NOTE: To the right of the row name field there is a little "<" icon.
                  .. click this icon to view/insert special tags - refer 'ROW NAME FORMATTING' section

- Balance option: Choose from 'Balance', 'Current Balance', 'Cleared Balance'
    - These are the same definitions used by Moneydance:
        - Balance:             Includes all transactions - even future
        - Current Balance:     The same as Balance but excluding future transactions
        - Cleared Balance:     Includes all 'cleared' (i.e. reconciled) transactions - even future

- AutoSum:
  - You can turn AutoSum ON/OFF: When on,  AutoSum recursively totals the selected account and all its sub-accounts
                                           it auto summarises the whole account(s) including Investments/Cash/Securities
                                           ('recursively' means iterate through all an account's children accounts...)
                                 When off, it just adds the value held at that account level (ignoring its children)
                                           you can manually select individual accounts/cats/securities/cash (by row)

  - AutoSum ON  will always auto-include all a selected account's child/sub accounts at runtime.
            OFF will only include the accounts you have selected. You will have to select/add any new accounts created

  - Investment accounts hold Cash at the investment account level. AutoSum affects your ability to select just cash
                        - When AutoSum is on, all securities get totalled into the Investment account (including cash)

  - You set the AutoSum setting by row. Thus some rows can be on, and others can be off.

- Override Balance asof Date:  Allows you to obtain the balance asof a specified date.
        - Includes all transactions / balances up to, and including, the selected balance asof date
          When selected, the balance asof date options are enabled. Here you select the automatic asof end date,
          or specify a fixed custom asof date. Auto-dates will auto-adjust every time the calculations are executed.

        - the 'offset' field can be used here to adjust the balance asof date - refer 'Date offset' section.

        - Calculation methodology for Balance/Current/Cleared Balance when using asof date:
            - Balance always uses the calculated asof-dated Balance
            - Past asof-dated Current Balance uses the calculated asof-dated Balance
            - Today/future asof-dated Current Balance uses the real account's Current Balance
            - Past asof-dated Cleared Balance is ILLOGICAL, so uses the calculated asof-dated Balance      ** WARNING **
            - Today/future asof-dated Cleared Balance uses the real account's Cleared Balance

        The following points should be noted:
            - Income / Expense categories:   Not affected by this option - refer separate 'I/E Date Range' section
            - Include Reminders:             Not affected by this option - refer separate 'Include Reminders' section
            - Security accounts when the 'Securities: Cost Basis' options are selected:
                - refer separate 'Securities: Cost Basis / Unrealised Gains / Capital Gains options' section...

        - WARNING: tax dates when using 'asof' cannot be derived. The 'normal' txn date will be applied.
                   .. this exclusion also applies to all cost basis option(s)...

        - WARNING: When using asof dates, consider that inactive accounts might have had balances in the past!
                   I.E. It might be best to Include Inactive and select all accounts (including currently inactive).

        - WARNING: REFER 'PARALLEL BALANCES' BELOW CONCERNING CALCULATION SPEED

- Include Reminders: (non-committed) Reminders (up to the specified reminder asof date) can be included in the balances.

        >> This only includes reminder occurrence(s) that have not already been committed/recorded into the register
           ... ie. once they are recorded/committed then they are already within the actual balance for that date

        - The 'balance asof date' setting has no bearing on (non-recorded) Reminders to include.
        - Only uncommitted (ie. non-recorded) Reminders will be selected. Then...
        - Reminder date(s) will be forward calculated up to the Reminder's asof date setting. Then...
        - The normal rules will apply when calculating Balance, Current Balance, Cleared Balance balances

        - the 'offset' field can be used here to adjust the include reminders asof date - refer 'Date offset' section.

        - NOTE: It would be unusual to find any (non-recorded) reminders with a Cleared Status - so expect ZERO.
        - NOTE: Ignored when returning cost basis / unrealised / capital gains

        - WARNING: tax dates on (non-recorded) reminders cannot be calculated. The 'normal' date will be applied.
        - WARNING: REFER 'PARALLEL BALANCES' BELOW CONCERNING CALCULATION SPEED

- Securities: Return: Value / Cost Basis / Unrealised Gains / Capital Gains option(s):
    - Value:            [DEFAULT] Returns the normal balance (i.e. this does not enable cost basis options)

    - Cost Basis:       When selected, the cost basis (**as of the balance / asof date) for selected Security
                        accounts will be returned (instead of the normal shareholding value).

    - (CB incl. cash):  The same as 'Cost Basis' but includes Investment account's cash balances...
                        When selected then cash balances on (selected) investment accounts will be included too.
                        .. both this option AND the investment account(s) need to be selected for cash
                        .. if this option is not selected, then any selected investment accounts will generate zero

                        > REMEMBER: Cash is NOT specific to any security, it's just cash in the investment account!

                        > WARNING: Many would consider that cash should NEVER be included, as this is not specific
                                   to any security. But MD often includes cash for any accounts where there are
                                   securities with a share balance. NOTE: MD does not seem to include cash where an
                                   investment account has no securities with a share balance.

    - Unrealised Gains: When selected, the calculated unrealised gains (**asof the balance / asof date) for the
                        selected Security accounts will be returned. This is calculated as value less cost basis.

    - Capital Gains:    When selected, the calculated capital gains for the selected Security accounts will be
                        returned. This gains calculation is 'simple' and will not identify short/long term gains
                        (for example). NOTE: when this option is selected then an extra row will appear, that
                        allows you to select the date range for the capital gains reporting.

                        > WARNING: The date range cannot exceed the 'balance asof date'. Any transactions (gains)
                                   after the asof date will be excluded from the calculation!

    - (C/Gains Short):  As above, but returns the 'short' capital gains value
    - (C/Gains Long):   As above, but returns the 'long' capital gains value

    >> NOTES:
        - Calculated cost basis / unrealised / capital gains values will overwrite normal calculated balances
          ... this is a MUTUALLY EXCLUSIVE option. When enabled, no other calculation type(s) will be included!
          ...... (no reminders, no other non-security/investment(cb incl. cash), no income / expense transactions)
        - There can in theory be future-dated cost basis / ur / capital gains. Let me know how this works out for you?!
        - Current Balance will derive the cost basis asof today.
        - asof-date Cleared Balance is ILLOGICAL, so uses the calculated asof-date Balance                 ** WARNING **

        - WARNING: REFER 'PARALLEL BALANCES' BELOW CONCERNING CALCULATION SPEED

        - WARNING: 'Use Tax Dates' will be ignored when returning any of the cost basis options!

- Securities Capital Gains: This option only appears when 'capital gains' is selected.


- INC/EXP Date Range: Income/Expense Categories need a date range to provide a balance.
                      Otherwise they have entries for all dates. (Details below)

        - the 'offset' field can be used here to adjust the inc/exp date range date - refer 'Date offset' section.


- Display Currency: Allows you to display the balance in a chosen currency, or security value, or other format.
                    Disable Currency Formatting: drops any symbol/prefix/suffix associated with the currency.

------------------------------------------------------------------------------------------------------------------------

MATH ON CALCULATED BALANCES:

- Average by options:
    - You can change the calculated balance into an average. Specify the number to divide by (DEFAULT 1.0)
      ...or...
    - Use the predefined: 'Inc/Exp Date Range' - calculate calendar units between XXX option:
      ... Only enabled/allowed when Income/Expense categories are selected AND when NOT using 'All dates'
      ... XXX: select one of: NOTSET, DAYS, WEEKS, MONTHS, YEARS (prefixed with "-" will reverse the sign of avg/result)
      ... Tick/un-tick 'Fractional' as required - see below:
          - ticked will return the exact result (including decimals) - (E.g. 1.45 months in the date range)
          - un-ticked will chop off the decimals with no rounding to return an integer / whole number
      ... WARNING - this can return zero which will mean your calculated result will also be zero or 'n/a'
      ... When allowed/enabled and used, then this overrides the first avg/by field.

      *** NOTE: DO NOT select to use a date range if no Inc/Exp categories are selected. It will automatically revert
                back to All dates at a later point when it validates the settings.

- Row maths calculation (RMC): You can apply maths to this row's calculation. This will be applied BEFORE
                               it's used elsewhere (i.e. used in other rows). RMC occurs after Average by...
                               - E.g. take this row, divide it by operand(x),  and treat the result as a percentage.
                                 For example, calculate the estimated tax payable as a percentage of dividend income YTD
                                 ... by multiplying the calculated row * 0.2 (20%), and returning the taxable amount.

                           NOTE: You can enter an RMC with no accounts selected in the picklist. The calculation will
                                 start from 0.0. This is a way to create a reusable row constant for use in other
                                 rows - e.g. RMC: + 0.22 for a 22% tax rate. NOTE: As soon as you enable this, then the
                                 following UOR, PUM, Format as %, Multiply by 100 options will trigger for this row...

                           WARNING: You can use both average by, and RMC. This could cause strange results!

                           >> RECOMMENDATION: Use formula instead of RMC/UOR/PUM where possible

- Maths using another row (UOR): You can retrieve the result from another row(x) and then apply maths to the result of
                                 the current row.. E.g. take this row and divide it by the result from row(x).
                                 E.g. this could calculate the value of investments as a percentage of total networth.
                                 UORs can be chained together. E.G. row 3 can use row 2 and row 2 can use row 1

                                 WARNING: There is no currency conversion between chained UORs

                                 >> RECOMMENDATION: Use formula instead of RMC/UOR/PUM where possible

- Post UOR maths calculation (PUM):
                                 You can apply maths to the row's calculation as the last step BEFORE formulas
                                 This PUM will be calculated and always provided 'upwards' into any other UORs consuming
                                 this row (directly or indirectly). Hence, per row, you can 'roll' PUMs upwards.
                                 This setting is per row...

                                 PUM EXAMPLE:                                   DISPLAYED
                                 - Row1: UOR: 2+   accounts: 1.0   PUM +2.0        11,003
                                 - Row2: UOR: 3+   accounts: 1.0   PUM *1000.0     11,000
                                 - Row3: UOR: -    accounts: 10.0  no PUM            10.0

                                 >> RECOMMENDATION: Use formula instead of RMC/UOR/PUM where possible

- Formula (FOR): You can write a formula expression to be applied (AFTER any RMC, UOR, PUM options).

                 - You probably (always) should start with the default tag '@this'. @this will pull in this row's
                   calculated balance without having to set a 'tag'... Or you can just set a tag on this row and refer
                   to it... If you don't refer to this row, then the result of any formula will ignore any selected
                   pre-formula accounts / RMC, UOR, PUM calculations etc....

                   Example formulas: '((@this - applestock) / networth) * 100.0'
                                     '@this * 0.2' or '(rowtagname / otherrowtagname)' or '@danspecialnumber'
                                     'NetWorth / @pi' or 'random()' or '@mdbuild * @mdversion'

                 - You can also enter currencyIDs / security ticker symbols if you wish
                   (if setup in tools>Currencies / tools>Securities) >> E.g. '@this * @GBP' or '@this * @APPL'

                 - Formula can refer to the calculated result from any row with a 'tag' name (including it's own row)

                 - For example '((investments / networth) * 100)' to obtain your investments as a percentage of networth
                   ... assuming that you set the tags 'investments' and 'networth' on the appropriate row(s)

                 - Formulas NEVER absorb / roll up into other UORs

                 - Formulas NEVER include the results of formulas... Only everything before a formula.. I.e. the result
                   ... from a Formula is only visible to itself / its own row. I.e. if you refer to a row (tag)
                   ... in a formula, then you will refer to that row's calculated result BEFORE that row's formula

                 - Formulas are optional. You can use them with or without RMC, UOR, PUM, FDA, *100 etc. For ease of
                   management, you should probably only use (RMC, UOR, PUM) -OR- formulas,
                   ... not both (but it's up to you)!

                 NOTE: Currently, the only functions allowed are: sum(), abs(), min(), max(), round(), float(), random()
                       ** if these do not work properly for you, please contact the author

                 WARNING: You can enter an FORMULA with no accounts selected in the picklist. The formula will
                          try to resolve. BUT if you refer to @this or this row's tag, then you will probably get an
                          invalid result!

                 WARNING: NEVER use currency signs or commas in numbers, only use '.' as the decimal place!

                 LIMITATIONS: Do not try to use any of the following characters within magic tags: "._-". They will be
                              ignored and assumed to be word separators.. E.g. Canadian Security @shop.to won't work as
                              it becomes @shop in the formula.

                              For security tickers with a dot you may have conflicts with the Quote Loader extension.
                              A workaround is to save the stock ticker as "SHOP" in the properties for the security
                              (instead of SHOP.TO), and put "SHOP.TO" in the "Alt Ticker" column in Quote Loader. Then
                              just use @shop in Custom Balances.

                 >> RECOMMENDATION: Do not mix formula and RMC/UOR/PUM. Ideally, just use formula where possible

- Format display adjustment (FDA): You can apply maths to change the displayed value after all other calculations.
                                   As you would expect, this result is NEVER used elsewhere.
                                   - You could optionally perform this step manually in the formula too...

- Format as %: When ticked then normal currency formatting is disabled and the '%' symbol is appended.
               When 'Multiply by 100' is ticked, then the displayed result after everything else is multiplied by 100.
                    - You could optionally perform this step manually in the formula too...
                    - 'Multiply by 100' can be important if you haven't already done "math" to make it a true percentage

------------------------------------------------------------------------------------------------------------------------

FORMATTING FOR ROW DISPLAY:

- Hide row when options:
    Never, Always(Disable), balance = X, balance >= X, balance <= X. DEFAULT FOR X is ZERO
    >> 'Always(Disable)' normally causes the row NEVER to be calculated, unless consumed by another row (UOR)
       or formula (FOR)

    You can set X to any value (positive or negative)
    NOTE: If you select row option 'Hide Decimal Places', AND 'auto-hide row when balance=X',
          ... AND set X to a whole number (no decimals), then the calculated balance will be rounded when comparing to X
          Rounding mode is 'half-up' (e.g. auto-hide when X=0 would include calculated results -0.499 to +0.499)
          >> If you specify an X with decimals then no rounding will take place (for auto-hide check)
          >> If the calculated balance is already a whole number, then no rounding will take place (for auto-hide check)

- Hide Decimal places: Will hide decimal places on the selected row's calculated balance. The result will ALWAYS be
                       rounded for display purposes. Rounding mode 'half-up' will be used:
                       (e.g. 1.0 to 1.499 would become 1.0, and 1.5 to 1.999 would become 2.0)
                       (e.g. -1.0 to -1.499 would become -1.0, and -1.5 to -1.999 would become -2.0)
                       This option impacts auto-hide logic in some situations - refer: 'Hide row when options'....

- Row separator: You can put horizontal lines above / below rows to separate sections

- Blink: Enables the blinking of the selected rows (when displayed / visible)

- Show Warnings: This enables / disables the alerts flagging whether warnings have been detected in your parameters
                 These are primarily where you have created 'illogical' calculations - e.g. Expense: Gas plus a Security
                 You can enable/disable warnings per row. The widget doesn't care. It will total up anything...!

                 NOTE: For 'Multi-Warnings Detected' review Help>Console Window for details
                       .. The search for warnings stops after the first occurrence of each type of error it finds....

------------------------------------------------------------------------------------------------------------------------

ACCOUNT SELECTION LIST (PICKLIST)':

    - You select accounts one-by-one to include in the row calculation.
    - You can use the dropdown select box to quickly view certain accounts - e.g. "All Investment AND Security accts"
      ... using the dropdown does not actually select any accounts. You have to click each one.
      ... or use the following buttons
    - 'Select All Visible'      selects all accounts in the current view filtered list, and adds the selection to the
                                existing selection. E.g. If you view INVESTMENT, select all visible, then view SECURITY,
                                then select all, then you will end up with all investment and all security.
    - 'Clear Visible Selection' deselects all accounts in the currently viewable list (but does not deselect any
                                selected accounts in non-viewable filtered list). E.g. view SECURITY,
                                clear visible selection, then view INVESTMENT, and you will see your investment
                                selections are still there.
    - 'Clear Entire Selection'  deselects all accounts - whether they are in the viewable/filtered list or not.
    - 'Undo List Changes'       undo any selection changes since your last 'Store List Changes'
    - 'Store List Changes'      stores the current account list selection into memory (this does NOT save selections)

    >> You must click 'STORE LIST CHANGES' before you click simulate or exit the config screen. If you do not do this
       then your selection changes could be lost! However, you will be asked if you want to store the changes first.

>> DON'T FORGET TO 'SAVE ALL SETTINGS'! (for convenience, this also stores your current account selection list too) <<

<<Simulate Row>> - As you make changes, the value calculation is not recalculated. Once you have your list created,
you can click Simulate Row to provide the value you will see. Anytime you change a setting and want to see the simulated
result, then click the simulate button.


FILTERS FOR LIST CHOICES:

- Active / Inactive Accounts:
  - MD ALWAYS includes the total balance(s) of all child accounts in an account's total. Irrespective of Active/Inactive
  - Thus if you select Active only and select an account containing inactive children, it will include inactive balances
  - When using AutoSum in this situation you will get a warning on screen
  - You will also see a small (3 vertical bars) icon to the right of account totals in the list window when this occurs.
  - Inactive Securities: You can flag a security as inactive by un-ticking the 'Show on summary page' box on a security
                       in the MD/Tools/Securities menu. This will then treat this security in ALL investment accounts
                       as INACTIVE.

- List Choices - you can filter the pick list by multiple criteria.
	       - other filters include filtering out zero values, and by what has been selected.

------------------------------------------------------------------------------------------------------------------------

OPTIONS MENU:

  - Debug: Generates program debug messages in Help>Console Window. DO NOT LEAVE THIS PERMANENTLY ON (setting not saved)
                     NOTE: Enabling this will show [row number] against each widget row on the home screen
  - Show Print Icon: Enables/shows the print icon on the Home / Summary screen widget.. Will print the current view
                     NOTE: Even when icon not visible, clicking the white-space before the title will activate print...
  - Page Setup: Allows you to predefine certain page attributes for printing - e.g. Landscape etc...
  - Reset Defaults: Basically allows an entire reset to initial settings (i.e. gets rid of all your data)
  - Backup Config: Creates a backup of your current config file (then opens a window showing location of backup)
  - Restore Config: Allows you to restore (or import) config file from previous back up
  - You can change the default setting AutoSum for new rows that you insert/create. It does not affect existing rows
  - You can disable the Widget's Display Name Title. This prevents the title appearing on the Summary Page widget
  - Show Dashes instead of Zeros: Changes the display so that you get '-' instead of '£ 0.0'
  - Treat Securities with Zero Balance as Inactive: If a Security holds zero units, it will be treated as Inactive
  - Use Indian numbering format: On numbers greater than 10,000 group in powers of 100 (e.g. 10,00,000 not 1,000,000)
  - Use Tax Dates: When selected then all calculations based on Income/Expense categories will use the Tax Date.
                   WARNING: tax dates are not considered when including:
                            - reminders,  cost basis / ur-gains / capital gains, or when using 'balance asof dates'.
                            ... as such, the 'normal' transaction date will be used.
  - Display underline dots: Display 'underline' dots that fill the blank space between row names and values
  - Disable Warning Icon: Removes Warning Icon from the Widget


BACKUP/RESTORE:

- When in the config GUI, the keystroke combination:
          CMD-I       will display this readme/help guide...
          CMD-SHIFT-B will create a backup of your config...
          CMD-SHIFT-R will restore the last backup of your config...
          CMD-SHIFT-I will display some debugging information about the rows...
          CMD-SHIFT-L will display debugging information about the internal lastResultsTable (not for 'normal' users)...
          CMD-SHIFT-W will display current warnings (same as clicking the warnings icon)...
          CMD-SHIFT-G allows you to edit the pre-defined/used GroupID Filter(s)... Click +/- cell (on right) to add/del


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> DETAILS SECTION <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

SELECT ROW INFORMATION:

** NOTE: When rows can be hidden, they may not display on the Summary screen widget. Click on the widget to config:

- Click the little up/down arrow icon to the right of 'Select Row' for a popup display / row selector that shows:
  row number, name, groupid, tag name..

- The main selector box, shows the row number, groupid, tag name and filtering information - see below:
       ... rows coloured red are currently filtered out / hidden by a groupid filter or an auto-hide option
       ... row numbers are suffixed with codes:
           <always hide>    Always hide row option is set (red = NOT active and hidden)
           <auto hide>      An auto hide row rule is active (red = ACTIVE, but hidden)
           <groupid: xxx>   A groupid value has been set on this row
           <tag: xxx>       A tag name (variable name) has been set on this row (for use in UOR / formula)
           <FILTERED OUT>   This row is currently NOT showing on the Summary Screen widget due to the active filter.
                            NOTE: Filtered rows (red) are NOT active and hidden.

HIDE CONTROLS: If your monitor cannot display all the information, this click box on the top right will provide you
               with a better view to pick items on the pick list.

SEARCH BOX AND GROUPID:

Once you have a lot of rows, you may only wish to display some of them within the widget.
GroupID allows you create groups of rows that you can separately display.

- You can enter a 'GroupID' per row. This is free format text (digits 0-9, Aa-Zz, '_', '-', '.', ':', '%', ';')
   NOTE: You can also enter the ';' character to separate groups. But you cannot filter for ';' as
         this is the separator between filter search elements...

   When you enter 'Group ID' filter text (next to the row selector), then this will filter rows from
   appearing on the Summary / Home page widget.. For example, set a row with "123" and then filter "2", then
   only the row(s) containing "2" will appear on the widget (this would include groups with id "123")
   NOTE: You can filter multiple 'Group IDs' by separating with ';'
         Enter '!' (not) to make the filter include rows that do NOT have the requested filters
         Enter '&' (and) to make the filter include rows where all the requested filters match
                        NOTE: |(or) is default - will be the default anyway unless '!' or '&' used
         Group ID Filters are cAsE InSeNsItIve...
         Each filter you use will be remembered and stored for later quick selection.. The most recent will always be
              top of the list. Click the little up/down selector on the widget title bar, or in the GUI to select one
              Use CMD-SHIFT-G to edit the list and provide names to the filters
              Only the most recent 20 will be saved...

   WARNING: Only enter one of '!|&' characters as only one search type can be used within a single filter.
         NOTE:    !(not) is always implicitly also &(and) - i.e. !1;2 (means not '1' and not '2')

   EXAMPLES:
          - Filter: '1'      - only include rows where the groupid includes a '1'
          - Filter: '1;2;3'  - only include rows where the groupid includes a '1' or '2' or '3'
          - Filter: '!1;2;3' - only include rows where the groupid does NOT include a '1' or '2' or '3'
          - Filter: '&1;2;3' - only include rows where the groupid includes one '1' and '2' and '3'

NOTE: This is free text, so the numbers are examples. A groupid of "Debt;CCList;Whatever" totally works.


TAG FIELD:
The tag field allows you to assign a tag/variable name to the selected row. This can be used in formula expressions.
This can be blank (i.e. no tag / variable name has been set). First character can only be alpha(A-Z), followed only by
alpha-numeric characters. You can enter MiXeD case, but internally it will always use the lowercase version...

       NOTES:
        - you do NOT need to set a tag for use only in this row - you can simply refer to the magic tag @this.
        - if no tag is set then the row cannot be referred to by another row's formula.
        - please do NOT use tags such as 'row1' as these will go wrong if/when you reorder your rows..
        - ideally use short tags such as 'taxrate'.


WARNINGS BOX:

  - You can create (very) 'illogical' totals (e.g. by adding Securities to Income). CB tries to detect these issues.
  - It will alert you if any are found. Help>Console Window will show you the details of any warnings
  - A red warning icon will appear on the title bar of the widget, and in the GUI, if you have warnings.
        - Click the warning icon to see a popup window displaying the detail(s) of the warnings.
        - NOTE: The symbol will not be triggered for warnings on rows where Show Warnings has been un-ticked
                ... unless debug mode is enabled, in which case the icon will always appear.

DATE OFFSET:

- Negative (e.g. -1) means offset back into the past. Positive (e.g. +1) means offset forward into the future.
- This allows you to adjust the dates you want used for balances, reminders, or income/expense categories. By creating
  an offset, you can do comparison of balances over time between date periods. For example, you could create a balance
  for "Gas spent this year to date" and then offset it by -1 (year) to create another balance for
  "Gas spent last year to date". You could then use the UOR (use another row) to create a comparison % change,
  or absolute change.

- You could compare your stock balances between time periods to see how much you've gained (or lost) over a period.

    - The 'offset' field (default blank/zero) allows you to enter the number of 'periods' to add/subtract from the asof
      date or date range you are selecting (i.e. for balance offset, include reminders asof, income/expense date range).
      The offset field only applies to the date selector (on the left) that it's 'attached' to.
      E.g. if you select 'Last year' (i.e. 'period' range is year) and offset -1, then you will get a range date
      calculated that includes 'last year' minus 1 (period) year (=end two years ago). Offset works either -backwards,
      or +forwards .
      >> Offset does not apply to 'Custom', 'asof end future (all dates)', 'All dates',
         and 'Last 1 day (yesterday & today)' selection(s)...


ROW NAME FORMATTING:

NOTE: Click the little "<" icon to the right of the row name field to view/insert the tags below...

- ROW NAME Configuration Options:
  - You can embed the following text (lowercase) in the Row Name field to configure the row / total (value) as follows:
    <#brn>   = Forces row name to be blank/empty
    <#jr>    = Row name justify: right
    <#jc>    = Row name justify: center
    <#cre>   = Row name colour:  red
    <#cbl>   = Row name colour:  blue
    <#cgr>   = Row name colour:  light grey
    <#fbo>   = Row name font:    bold
    <#fit>   = Row name font:    italics
    <#fun>   = Row name font:    underline
    <#nud>   = No special underline dots...
    <#fud>   = Force special underline dots...
    <#bzv>   = Forces any total (value) to appear blank when zero
    <#cvre>  = Value colour:  red
    <#cvbl>  = Value colour:  blue
    <#cvgr>  = Value colour:  light grey
    <#fvbo>  = Value font:    bold
    <#fvit>  = Value font:    italics
    <#fvun>  = Value font:    underline

  - You can embed the following to insert variable text into the Row Name field:
    <##rn>    = insert the row number
    <##rt>    = insert the row tag
    <##bopt>  = insert the balance option selected
    <##bad>   = insert the balance asof date
    <##badn>  = insert the balance asof date name
    <##rad>   = insert the include reminders asof date
    <##radn>  = insert the include reminders asof date name
    <##cgdr>  = insert the capital gains date range
    <##cgdrn> = insert the capital gains date range name
    <##iedr>  = insert the income/expense date range
    <##iedrn> = insert the income/expense date range name

    NOTE: Underline dots will always be turned off if you justify center the text...

    <#html> = EXPERIMENTAL - USE WITH CARE: Takes your row name as html encoded text (do NOT wrap with <html> </html>)..
              Common html tags are: for bold: <b>text</b>   italics: <i>text</i>   small text: <small>small text</small>
                                        colors(hex) red: <font color=#bb0000>red text</font>
                                                    blue: #0000ff
                                                    default MD foreground color(black-ish): #4a4a4a
                                        Refer: https://www.rapidtables.com/web/color/RGB_Color.html

   HTML EXAMPLE:
   <#html><b><font color=#0000ff>Expenses </font></b>Last month <small><u><font color=#bb0000>OVERDUE</font></u></small>


USING CATEGORIES (DATE RANGE)

- Income / Expense Categories:
  - WARNING: REFER 'PARALLEL BALANCES' BELOW CONCERNING CALCULATION SPEED

  - You can change the date range selection from the default of "All Dates" to any of the options in the list

  - NOTE: You can select to use a date range at any time. BUT if you have not selected any Inc/Exp categories, then
          the date range will later revert back automatically to 'All dates'.

  - NOTE: The 'Balance asof Date' has no bearing on this setting which is used exclusively for Income / Expense txns
  - NOTE: The 'Include Reminders Date' has no bearing on this setting.
  - NOTE: The 'Securities Capital Gains' has a similar, but separate date range from the Income / Expense date range

  - NOTE: The date range will interact with your Balance/Current Balance/Cleared setting for that row:
          E.G.  Current Balance will always cutoff to today's date
                Balance will just include everything it finds within the above date ranges
                Cleared Balance will just include all cleared items within the above date ranges

  >> If you choose 'Custom Date' you can manually edit the date range. Once you have selected 'Custom Date',
       .. if you then select one of the preconfigured date options, it simply pre-populates the start/end dates for you
       .. this pre-selection name is irrelevant and is not saved. All that is saved is the date range you enter.

  - NOTE: All the date options are dynamic and will auto adjust, except 'Custom' dates which remain as you set them


KEY TO ROW FORMATTING ON SUMMARY SCREEN:

Against each row you may see (in small grey characters) the following (text) with these meanings (when option enabled):
(curr)          Will display the selected currency's ID when the base currency is not selected - e.g. 'GBP' or 'USD'
(avg/by: x)     Average by operand
(balasof)       Balance asof date
(rems)          Reminders included
(cb)            Cost Basis (no cash is being included)
(cb-c)          Cost Basis, including cash from selected investment accounts
(urg)           Unrealised Gains
(cg)            Capital Gains
(cg-s)          Capital Gains - Short Term value
(cg-l)          Capital Gains - Long Term value
(rmc)           Row maths calculation is being applied
(pum)           Post UOR maths is being applied (will absorb into other UORs that consume this row)
(for)           Formula is being applied
(fda)           Format display adjustment is being applied
(txd)           Tax dates are being used
(uor: x)        Maths using another row(x) is being applied

NOTE: If you enable debug mode, then these may be expanded into fuller definitions where appropriate.
(uuid: x)       When debugging, the row's UUID(x) will be shown. Useful when using CMD-SHIFT-I and CMD-SHIFT-L


DETAILS ON HOW CALCULATIONS OF BALANCES OCCURS:

>> CALCULATION ORDER: The calculations are performed is this sequence (for all rows, or just the simulation row):
    - Derive all rows required, and/or required within other rows (irrespective of always hide / GroupID filter)
      (this includes hunting for 'free' variables referred to in other formulas, or UOR chains that require this row)
    - (unless used within other rows / formulas) skip any 'always hide' rows
    - (unless used within other rows / formulas) skip any rows filtered out by GroupID
    - Calculate raw balances for derived rows/accounts, including recursive sub accounts for autosum rows
    - Convert calculated balances to target currency
    - Iterate over each row/calculation, apply any average/by calculations
    - Iterate over each row/calculation, apply any row maths calculations (rmc) specified
    - Iterate over each row/calculation, apply any Use Other Row (UOR) calculations.. Iterate the whole UOR chain
                                         Calculate pum into UOR result during processing...
    - >> results before this point will be stored within the 'tag' variables for formulas - see next step <<
    - Iterate over each row/calculation, apply any formula (for)
    - Iterate over each row/calculation, apply any format display adjustments (fda)
    - If *100 is selected, then multiply displayed result by 100

    NOTE: Format as %, Disable Currency Formatting, Hide Decimal Places only affect the display, not calculations
          ... although 'Hide Decimal Places' can cause rounding to be triggered when 'auto-hide row when balance=X'
          is specified... but this only affects the hide logic and format display. The calculated result is not impacted.

    WARNING: Rows that are used within other rows / formulas are ALWAYS calculated, irrespective of hide/GroupID filter
             >> be mindful of the CPU / speed impact of non-displayed rows especially when using parallel calculations!

    WARNING: Formulas only reference the results from above. They never include the results from other formulas
             To make a 'this-row' only adjustment, only use a formula, and do not use PUM.

>> DECIMAL PRECISION: Whilst only 2 decimal places will/can be displayed (according to your currency's decimal setting),
                      full decimal precision will be stored internally, and this internal value will be used for maths
                      functions that operate on the row's calculated result (e.g. average by, RMC, UOR, PUM, FOR, FDA)..


>> ROUNDING:
Rounding is only performed on the displayed result when 'Hide Decimal Places' is selected. The internal number
is never rounded, and full decimal precision is always preserved internally for onward UOR consumption.
- Rounding of Java Double / Python float numbers can be problematic. Custom Balances calls Jython's round() method. This
  internally uses Java's BigDecimal class with the RoundingMode.HALF_UP mode (e.g. 0.5 should become 1.0).
  NOTE: you won't always get what you expect. If you are interested - refer:
        https://docs.python.org/2.7/library/functions.html#round
        https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/math/RoundingMode.html#HALF_UP


>> PARALLEL BALANCES:
    - Selecting any of the following options will trigger 'parallel balance operations' for that row, for all accounts
      ... used by that row: Balance asof date; Income/Expense date range; Cost Basis / Unrealised Gains / Capital Gains;
      ...  including Reminders...

    - The sequence of harvesting data / calculating balances for rows using parallel balances is as follows:
        # 1. per row, gather all selected accounts along with all child/sub accounts...
        # 2. if Income/Expense dates requested, then harvest related I/E txns...
        # 3. convert the harvested I/E txn table into account balances...
        # 4. for all accounts / balances not derived by steps 2 & 3, calculate balance asof dates (where requested)...
        # 5. for all accounts / balances not derived by steps 2, 3 & 4, harvest remaining accounts' real balance(s)...
        # 6. replace balance(s) with cost basis / unrealised / capital gains on security accounts (where requested)...
        # 7. for all accounts selected, add reminder txn/balances up to the reminder's asof date (where requested).

    - NOTE: When cost basis / unrealised / capital gains is enabled, all other steps are skipped >> MUTUALLY EXCLUSIVE!
            (i.e. no reminders, income / expense transactions, no non-security/investment(cb incl. cash) accounts

    - NOTE: For the Summary Screen (Home Page), only selected accounts use parallel balances...
            But when using the configuration GUI, then all Accounts for the viewed row will use parallel balances...

    - WARNING: Parallel operations calculate by sweeping through transactions and calculating balances from scratch
               Balance asof dates & I/E date ranges harvest transactions...
               Future reminders are forward calculated...
               Cost Basis / Unrealised / Capital Gains sweep Buy/Sell txns... (possibly twice for Bal vs Current Bal)
               Remaining real balances, sweep accounts and uses the Account's real stored balance(s)
               ALL THIS CAN POTENTIALLY BE CPU CONSUMING. Do not use the widget for heavy reporting purposes!
               No harm will be caused, but these rows may take a few seconds to calculate / appear....


NOTES ON COST BASIS / CAPITAL GAINS:

** DISCLAIMER ** The author of Custom Balances accepts no responsibility for the accuracy of the cost basis or
                 capital gains calculations. Do not rely on these calculations for tax returns or other important
                 documents. Please verify and use your own calculations for important / official government reporting.

Cost basis can appear in Moneydance in multiple places:
-------------------------------------------------------
FROM MD2024(5100) Moneydance's internal Cost Basis / Capital Gains engine was rewritten (using Custom Balances' code).
.. The calculations were unified and all screens/reports use one calculation. Since this build, Custom Balances reuses
.. Moneydance's internal engine.. NOTE: There were a couple of further fixes made in MD2024.2(5119)

>> In simple terms, if you are using MD2024 onwards, then Custom Balances uses Moneydance's calculation. As far as we
know, the calculations should be correct everywhere... If you are using an older build of MD, then read on >>>>

PRIOR TO MD2024... it is not calculated consistently within Moneydance...:
... for example:
    - Investment account: Portfolio View tab (PVT)              (Avg Cost - newer method)
    - Cost Basis report (CBR)                                   (Avg Cost - old method)
    - Portfolio report (PR)                                     (Avg Cost - newer method)
    - Investment Performance report (IPR)                       (Avg Cost - newer method)
    - Capital Gains report (CGR)                                (Avg Cost - newer engmethodine)

Particularly for 'Average Cost' controlled securities, PVT & PR use MD's newer CostCalculation engine and this tends to
give a more accurate result. However, for securities with stock 'splits', this newer engine has flaws and the CBR can
sometimes give a 'better' result. In particular:

- for average cost...:
  .. if all shares are sold down to zero, and then later more shares are purchase, then CBR goes wrong
  from this point forward. MD's new engine deals properly with this situation.

  .. with securities with stock splits, MD's new engine fails to calculate properly. In this situation
  the old CBR report is better. Note: In this scenario, the capital gains report will also be wrong.

  .. Buy/Sell txns zero shares sells with a fee, and also MiscInc/Exp with a fee can be used to 'adjust'
  MD's calculation of the cost basis. MD's new engine accounts for this.

  .. Sell shares at zero price/amount causes CBR to ignore the txn and hence MD's cost basis goes wrong
  from this point. MD's new engine accounts for this.

  .. Sell all shares with a zero cost basis... causes the capital gains NOT to report the full txn value as the gain

- for 'Lot Control' securities, the original calculation method is used consistently for all screens/reports. But again,
  there can be issues in some places.

Under U.S. IRS, 'short-term' (ST) is considered to be when securities are held for one year or less. Hence, 'long-term'
(LT) are where held for greater than one year.

With long / short-term capital gains, MD will allocate the whole sale fee to LT or ST if the matched buys were all
of one term type. If the sale consists of both long and short term buys, then the whole sale fee is allocated into short
term. Custom Balances mirrors this calculation (instead of allocating the fee proportionally between long/short term.

Custom Balances uses its own cost calculation engine that has been recoded/fixed to account for known issues with MD's
cost basis calculations. Hence, the calculated cost basis won't consistently match with all MD screens/reports. However,
you should find that it will normally match with one of the items mentioned above for reconciliation purposes. If you do
find an issue with CB's calculation, please let the author know (along with details on how to reproduce the problem).

MD & Custom Balances follows the U.S. IRS 'single-category' average cost method definition. Gains are split short /
long-term using FIFO. From U.S. IRS Publication 564 for 2009, under Average Basis, for the 'single-category' method:
          "Even though you include all unsold shares of a fund in a single category to compute average
          basis, you may have both short-term and long-term gains or losses when you sell these shares.
          To determine your holding period, the shares disposed of are considered to be those acquired first."
          https://www.irs.gov/pub/irs-prior/p564--2009.pdf
>> to be clear, with average cost, gains are always calculated using the average cost, and that total gain will be split
   proportionally (based on the qty of ST/LT shares allocated to the sale) between ST/LT gains buckets.

There was a 'double-category' method which allowed you to separate short-term and long-term average cost pools,
but the IRS eliminated that method on April 1, 2011. NOTE: Custom Balances can compute the available shares
in both short-term and long-term pools (however this data is only shown in console when COST_DEBUG is enabled).
>> MD can report this same data in the Capital Gains report when the 'Show double-category average cost data' option is
   enabled. However, this does not affect the cost basis or gains calculation, and is incorrect when the security has
   stock splits....
------------------------------------------------------------------------------------------------------------------------



TECHNICAL/HISTORICAL NOTES:
- My original concept was to add balances to target zero. Thus a positive number is 'good', a negative is 'bad'
- The idea was that you net cash and debt to get back to zero every month (but you can do so much more than this now)!

>> Display Name changed to 'Custom Balances' (from 'Net Account Balances') Dec 2021.

Extension format only >> Minimum Moneydance version 2021.1 (build: 3056, ideally 3069 onwards)
(If you have installed the extension, but nothing happens, then check your Moneydance version)

This is a Python(Jython 2.7) Extension that runs inside of Moneydance via the Python Interpreter
It demonstrates the capabilities of Python(Jython). Yes - if you can do it in Java, you can do it in Jython too!

DEVELOPERS: >> You can actually grab the results of the calculations from other extensions.. Contact me for details...

Thanks for reading..... ;->
Get more Scripts/Extensions from: https://yogi1967.github.io/MoneydancePythonScripts/

<END>
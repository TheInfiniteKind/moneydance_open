Author: Stuart Beesley - StuWareSoftSystems (March 2021 - a lockdown project) - Last updated December 2022
Credit: Dan T Davis for his input, testing and suggestions to make a better product......

>> Display Name changed to 'Custom Balances' (from 'Net Account Balances') Dec 2021.

Extension format only >> Minimum Moneydance version 2021.1 (build: 3056, ideally 3069 onwards)
(If you have installed the extension, but nothing happens, then check your Moneydance version)

This is a Python(Jython 2.7) Extension that runs inside of Moneydance via the Moneybot Python Interpreter
It's a prototype to demonstrate the capabilities of Python. Yes - if you can do it in Java, you can do it in Python too!

DISCLAIMER: THIS EXTENSION IS READONLY (IT DOES NOT CHANGE DATA) >> BUT YOU USE AT YOUR OWN RISK!

PURPOSE:
This extension creates a 'widget' that displays Totals for items you select on the Moneydance Summary Page (Home Page)

- Double-click the .mxt file (this may not work if you do not have .mxt extensions associated with Moneydance)
  ... or Drag & drop .mxt onto left side bar, or Extensions, Manage Extensions, add from file to install.
- Once installed, visit Preferences > Summary Page, and then move the new widget to the desired Summary Page location

- This widget allows you to select multiple accounts / categories / Securities and filter Active/Inactive items
- The balances are totalled and displayed on the Summary Page widget, converted to the Currency you select to display

- My original concept was to add balances to target zero. Thus a positive number is 'good', a negative is 'bad'
- The idea was that you net cash and debt to get back to zero every month (but you can do so much more with this now)

- You could create a Net Worth Balance for example; or total particular securities, or total certain accounts...
- Or total expenses by date - e.g. 'how much did I spend on fuel last month?'
- You can use it for anything really. Warning >> you can create 'nonsense' totals if you like too....

- To configure the widget, select an existing row on the Summary Page, or use the Extensions Menu

- You can add/delete/move as many rows as you require, and then configure the selected items per row
- You can select to total together Accounts / Categories (by date range) / Securities....

- You can change the name of each row, the balance type, and the currency to display. Also Active/Inactive items.

- Hide row when options: Never, Always(Disable), balance=X, balance >= X, balance <= X. DEFAULT FOR X is ZERO
... You can set X to any value (positive or negative)
    NOTE: If you select Menu Option 'Hide Decimal Places', AND auto-hide row when balance=X,
          AND set X to a value with no decimals, then the calculated balance will be rounded when comparing to X.
          Rounding will be towards X... This means that X=0 would include -0.99 to +0.99 (example)

- Row separator: optionally put horizontal lines above / below rows to separate sections
- Blink: Enables the blinking of the selected rows (when displayed / visible)
- Avg/by: Changes the final displayed calculated balance into an average by dividing by the value set (DEFAULT 1.0)

** NOTE: When rows can be hidden, they may not display on the Summary screen widget. Click on the widget to config:
         - In the row selector:
           ... rows prefixed with a '*' / colored red are always hidden (disabled)
           ... rows prefixed with a '~' / colored red might be hidden depending on the calculated balance

- AutoSum:
  - You can turn AutoSum ON/OFF: When on,  AutoSum recursively totals the selected account and all its sub-accounts
                                           it auto summarises the whole account(s) including Investments/Cash/Securities
                                           ('recursively' means iterate through all an account's children accounts...)
                                 When off, it just adds the value held at that account level (ignoring its children)
                                           you can manually select individual accounts/cats/securities/cash (by row)

  - AutoSum ON  will always auto-include all a selected account's child/sub accounts at runtime.
            OFF will only include the accounts you have selected. You will have to select/add any new accounts created

  - Investment accounts hold Cash at the investment account level. AutoSum affects your ability to select just cash
                        - When AutoSum is on, all securities get totalled into the Investment account

  - You set the AutoSum setting by row. Thus some rows can be on, and others can be off.

- Show Warnings: This enables / disables the alerts flagging whether warnings have been detected in your parameters
                 These are primarily where you have created 'illogical' calculations - e.g. Expense: Gas plus a Security
                 You can enable/disable warnings per row. The widget doesn't care. It will total up anything...!

                 NOTE: For 'Multi-Warnings Detected' review Help>Console Window for details
                       .. The search for warnings stops after the first occurrence of each type of error it finds....

- Active / Inactive Accounts:
  - MD ALWAYS includes the total balance(s) of all child accounts in an account's total.. Irrespective of Active/Inactive
  - Thus if you select Active only and select an account which contains inactive children, it will include inactive balances
  - When using AutoSum in this situation you will get a warning on screen
  - You will also see a small (3 vertical bars) icon to the right of account totals in the list window when this occurs.

- Income / Expense Categories:
  - You can change the date range selection from the default of "All Dates" to any of the options in the list
  - WARNING: This switches the widget to build and maintain a 'parallel table' of balances.
             Calculated by sweeping through all transactions and calculating balances
             THIS CAN POTENTIALLY BE CPU CONSUMING. Do not use the widget for heavy reporting purposes!
             Any row that uses NON "All Dates" will trigger this parallel balances sweep

  - I/E Date Range options:
    Example: Given a today's date of 11th December 2021, the I/E Date Range filters will return the following:
    DR_YEAR_TO_DATE                20210101 - 20211211
    DR_FISCAL_YEAR_TO_DATE         20210406 - 20211211
    DR_LAST_FISCAL_QUARTER         20210706 - 20211005
    DR_QUARTER_TO_DATE             20211001 - 20211211
    DR_MONTH_TO_DATE               20211201 - 20211211
    DR_THIS_YEAR                   20210101 - 20211231 **future**
    DR_THIS_FISCAL_YEAR            20210406 - 20220405 **future**
    DR_THIS_QUARTER                20211001 - 20211231 **future**
    DR_THIS_MONTH                  20211201 - 20211231 **future**
    DR_THIS_WEEK                   20211205 - 20211211
    DR_LAST_YEAR                   20200101 - 20201231
    DR_LAST_FISCAL_YEAR            20200406 - 20210405
    DR_LAST_QUARTER                20210701 - 20210930
    DR_LAST_MONTH                  20211101 - 20211130
    DR_LAST_WEEK                   20211128 - 20211204
    DR_LAST_12_MONTHS              20201201 - 20211130
    DR_LAST_365_DAYS               20201211 - 20211211
    DR_LAST_30_DAYS                20211111 - 20211211
    DR_LAST_1_DAY                  20211210 - 20211211
    DR_ALL_DATES                   (returns all dates)

    NOTE: The above will interact with your Balance/Current Balance/Cleared setting for that row:
          E.G.  Current Balance will always cutoff to today's date
                Balance will just include everything it finds within the above date ranges
                Cleared Balance will just include all cleared items within the above date ranges

    >> If you choose 'Custom Date' you can manually edit the date range. Once you have selected 'Custom Date',
       .. if you then select one of the preconfigured date options, it simply pre-populates the start/end dates for you
       .. this pre-selection name is irrelevant and is not saved. All that is saved is the date range you enter.

    NOTE: All the date options are dynamic and will auto adjust, except 'Custom' dates which remain as you set them

- Warnings:
  - You can create illogical totals (e.g. by adding Securities to Income). NAB tries to detect these issues.
  - It will alert you if any are found. Help>Console Window will show you the details of any warnings

- ROW NAME Configuration Options:
  - You can embed the following text (lowercase) in the Row Name field to configure the row as follows:
    <#bz>   = This presents the total that is zero as blank/empty
    <#brn>  = Forces row name to be blank/empty
    <#jr>   = Right justifies the row name
    <#jc>   = Center justifies the row name
    <#cre>  = Changes the row name to appear in red colour
    <#cbl>  = Changes the row name to appear in blue colour
    <#cgr>  = Changes the row name to appear in light grey colour
    <#bo>   = Changes the row name to appear in bold
    <#it>   = Changes the row name to appear in italics
    <#html> = EXPERIMENTAL - USE WITH CARE: Takes your row name as html encoded text (do NOT wrap with <html> </html>)..

- Options Menu:
  - You can disable the Widget's Display Name Title. This prevents the title appearing on the Summary Page widget
  - You can change the default setting AutoSum for new rows that you insert/create. It does not affect existing rows
  - Show Dashes instead of Zeros: Changes the display so that you get '-' instead of '£ 0.0'
  - Treat Securities with Zero Balance as Inactive: If a Security holds zero units, it will be treated as Inactive
  - Use Indian numbering format: On numbers greater than 10,000 group in powers of 100 (e.g. 10,00,000 not 1,000,000)
  - Hide Decimal places: Will hide all decimal places on calculated balances (e.g. 1.99 will show as 1)
                         This option impacts auto-hide logic in some situations - refer: Hide row when options....
                         NOTE: Rounding towards X will be triggered for display formatting when this option selected:
                         ... This means if X=1 for example, then 0.1 thru 1.9 would show as 1 (not zero)

  - Display underline dots: Display 'underline' dots that fill the blank space between row names and values

  - Debug: Generates program debug messages in Help>Console Window. DO NOT LEAVE THIS PERMANENTLY ON

>> DON'T FORGET TO SAVE CHANGES <<

Thanks for reading..... ;->
Get more Scripts/Extensions from: https://yogi1967.github.io/MoneydancePythonScripts/
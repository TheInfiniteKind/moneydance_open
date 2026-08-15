Author: Stuart Beesley - StuWareSoftSystems (created August 2026 - last updated: August 2026)

Context Menu Tools - User Guide
================================

This extension adds extra right-click (context menu) options to Moneydance. It detects
right-click actions in Moneydance, and different menu items appear depending on what you have
selected and which features are enabled. Options are configured on the "Context Menu Tools"
configuration screen, where each feature can be enabled, disabled, and further customised. How
many objects you have selected can also affect which menu items appear.

Several options work with transactions in the register, but others can appear on accounts,
reminders, currencies, securities, reports, budgets, and more.

If an expected menu item isn't appearing, there may be a rule preventing it - see the relevant
section below, or "Why isn't an option showing?" near the end of this guide.


MENU OPTIONS (in the order they appear)
------------------------------------------
  - Show Raw Details
  - Copy Raw Details to Clipboard
  - Show Value of Selected Transactions
  - Duplicate Transactions...
      - With the same date(s)
      - Enter new date
      - Adjust duplicated date(s)
      - Adjust duplicated date(s) by one month
  - Copy Splits
  - Paste Splits
  - Apply Splits Template (from Reminders)
  - Rebalance Splits
  - Jump to Date in Register


CONFIGURATION SCREEN
---------------------
Use Moneydance's Extension Menu, and select "Context Menu Tools" to open the settings screen.
Every feature above can be turned on or off individually, and a few have extra options of their
own (shown indented underneath the relevant checkbox). Click OK to save, Cancel to discard
changes.


SHOW RAW DETAILS
-------------------
Copies the underlying raw data for whatever is selected - transactions, accounts, reminders,
budgets, currencies, reports, more or less anything - and shows it in a read-only window. Useful
if you just want to look, without disturbing whatever you currently have on the clipboard. Has
its own "Copy to Clipboard" button if you decide you want it after all. Asks for confirmation if
you select more than 10 items, purely to avoid opening an enormous window by accident.


COPY RAW DETAILS TO CLIPBOARD
--------------------------------
Same raw data as above, but copied straight to your clipboard instead of shown in a window -
mostly useful for troubleshooting or sending details to support. Works on any selection size; if
you select more than 10 items you'll be asked to confirm first, since it's about to overwrite
your clipboard.


SHOW VALUE OF SELECTED TRANSACTIONS
--------------------------------------
Select one or more transactions and choose this option to see their combined total, converted
into a currency of your choice (set in the config screen). This feature knows how to correctly
summarise complex investment transactions or different types.


DUPLICATE TRANSACTIONS...
----------------------------
Right-click a transaction and choose one of the Duplicate options to create a copy of it:

  - With the same date(s) - the duplicate keeps the original transaction's date(s), no prompt

  - Enter new date - prompts for one specific new date, used for a single transaction
    ** may also let you enter a new value - see below

  - Adjust duplicated date(s) - prompts for a relative shift (days/months/years), applied to
    every duplicated transaction - suits duplicating several transactions at once
    ** may also let you enter a new value - see below

  - Adjust duplicated date(s) by one month - shortcut that duplicates one month forward
    automatically, no prompt

** When duplicating 2 or more single-split transactions, where every selected transaction
   currently shares the same absolute value and the same currency, where none of the accounts
   involved are Root or Security type, and where any Investment account involved is a simple
   bank-transfer-type transaction, a "New value" field will also appear, letting you set one new
   amount applied to every duplicate (each duplicate's original debit/credit direction is kept).


COPY SPLITS / PASTE SPLITS
----------------------------
Copy the split lines from one transaction, then paste them onto another. Handy when a new
downloaded transaction should have the same category breakdown as one you've already entered.

Every option below requires that you have exactly one Parent transaction selected (not a split row,
not multiple transactions) before any of Copy Splits, Paste Splits, Apply Splits Template, or
Rebalance Splits can appear at all.

Copy is allowed when:
  - the transaction's account is a Bank or Credit Card account
  - it has at least one split
  - every split's category is in the same currency as the account
  - (the transaction's own reconciled status doesn't matter for Copy - any status is fine)

Paste is allowed when (in addition to a copy already existing):
  - you're not pasting back onto the exact transaction you copied from
  - none of the target's existing splits hold protected downloaded/online-bank data
  - the target account is a Bank or Credit Card account
  - the target transaction AND all of its existing splits are Unreconciled
  - every split's category on the target is in the same currency as the target account
  - the target account's currency matches what was copied

If the target's total doesn't match what you copied, you'll be asked how to handle the
difference (keep amounts exact and add the extra to a new split, or scale everything
proportionally). There's also a config option to always ask this, even when totals match.


APPLY SPLITS TEMPLATE (FROM REMINDERS)
------------------------------------------
Same idea as Copy/Paste, but the source is one of your saved Reminders instead of a live
transaction. Useful for a split pattern you use repeatedly - set it up once as a Reminder, then
apply it whenever you need it. The Reminder itself never needs to actually fire.

The target must pass the exact same rules as a Paste target above (protected data, account type,
unreconciled, currency-consistent splits) - the only difference is what currency it needs to
match: a Reminder's own transaction currency, rather than a previously copied one.

At least one Reminder must also qualify as a valid source (same rules as Copy above applies to
the Reminder's own transaction) before this option appears at all. Which Reminders show up in
the picker can be narrowed further in the config screen:
  - require the Reminder's own account to exactly match the target account
  - include or exclude Reminders that only have a single split
  - exclude Reminders that are expired/inactive
  - filter the displayed list by using a text string that will be filtered against the
    Reminder's name


REBALANCE SPLITS
-------------------
Unlike the other three, this doesn't bring in anything from elsewhere - it changes a
transaction's own total (or just the ratio between its existing splits) while keeping the same
split lines. Useful when you've duplicated an old transaction and the total has changed, but the
categories are still right.

Allowed when:
  - none of its splits hold protected downloaded/online-bank data
  - the account is a Bank or Credit Card account
  - the transaction and all its splits are Unreconciled
  - every split's category is in the same currency as the account
  - it has more than one split

You'll be asked for a new total (or leave it as-is to just change the ratio) and whether to keep
each split's existing proportion or divide the new total equally across all splits.


JUMP TO DATE IN REGISTER
----------------------------
Quickly jump the register to a specific date, instead of scrolling.


DEBUG MESSAGES
----------------
The config screen has an "Enable debug messages" checkbox. Turning it on makes the extension
write extra diagnostic information to Moneydance's console/log (accessed via Help / Console
Window) - mainly useful if something isn't behaving as expected and you want to see what the
extension is actually doing. In particular, this will show messages when the Copy Splits, Paste
Splits, Apply Splits Template, or Rebalance Splits menu items have been blocked, explaining
exactly why the option was not allowed.


WHY ISN'T AN OPTION SHOWING? (reading the console)
-----------------------------------------------------
If a menu option you expect isn't appearing, turn on "Enable debug messages" in the config
screen (see above), then try right-clicking the transaction again. Nothing will look different
in the menu itself, but a line will be written to Moneydance's console/log explaining exactly
which rule blocked it - for example:

  Rebalance Splits blocked for 'Venmo' (20260806, $2,170.00, 1 splits): Reconciled/Reconciling
  (target must be unreconciled)

That tells you the transaction was reconciled, which is why Rebalance Splits didn't appear. The
message always names the specific rule that failed, matching the "allowed when" lists above.


<END>

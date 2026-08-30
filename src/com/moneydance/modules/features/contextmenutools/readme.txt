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
  - Show Value of Selected Transactions
  - Duplicate Transactions...
      - With the same date(s)
      - Enter new date
      - Adjust duplicated date(s)
      - Adjust duplicated date(s) by one month
  - Copy Splits
  - Paste Splits
  - Apply Splits Template (from Reminders)
  - Apply Splits Template to Selected Transactions
  - Rebalance Splits
  - Update Reminder...
      - and transaction's value
      - from selected transaction
  - Edit Originating Reminder
  - Zap/Clean Memo
  - Show Other Side: Select Split
  - Jump to date in register
  - Show Raw Details
  - Copy Raw Details to Clipboard


CONFIGURATION SCREEN
---------------------
Use Moneydance's Extension Menu, and select "Context Menu Tools" to open the settings screen.
Every feature above can be turned on or off individually, and a few have extra options of their
own (shown indented underneath the relevant checkbox). Click OK to save, Cancel to discard
changes.


SHOW VALUE OF SELECTED TRANSACTIONS
--------------------------------------
Select two or more transactions and choose this option to see their combined total, converted
into a currency of your choice (set in the config screen). This feature knows how to correctly
summarise complex investment transactions or different types.


DUPLICATE TRANSACTIONS...
----------------------------
Right-click a transaction and choose one of the Duplicate options to create a copy of it. With a
single transaction selected, only "Adjust duplicated date(s) by one month" is available - the
other three options below only appear when 2 or more transactions are selected:

  - With the same date(s) - the duplicate keeps the original transaction's date(s), no prompt
    (2 or more transactions only)

  - Enter new date - prompts for one specific new date, applied to every duplicated transaction
    (2 or more transactions only)
    ** may also let you enter a new value - see below

  - Adjust duplicated date(s) - prompts for a relative shift (days/months/years), applied to
    every duplicated transaction - suits duplicating several transactions at once
    (2 or more transactions only)
    ** may also let you enter a new value - see below

  - Adjust duplicated date(s) by one month - shortcut that duplicates one month forward
    automatically, no prompt - available whether you've selected one transaction or several

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
proportionally). There's also a config option to always ask this, even when totals match, and a
separate config option to make "Allocate by %" the default-selected choice on that prompt
instead of "Overwrite target total" (this also applies to Apply Splits Template below, since
both share the same prompt).

Four further config options let you optionally carry the source's Description and/or Memo across
onto the target too - Description and Memo are controlled entirely separately, and each has two
independent settings:
  - Fill blank target Description/Memo from source - only fills the target field when it's
    currently empty, never overwrites something already there
  - Always overwrite target Description/Memo from source - overwrites the target field
    regardless of what it currently holds
A blank source field (including one containing only whitespace) is never copied across either
way. If both settings for a field are somehow on at once, "Always overwrite" takes priority. All
four default off, and all apply to Paste Splits and both Apply Splits Template options alike.


APPLY SPLITS TEMPLATE (FROM REMINDERS)
------------------------------------------
Same idea as Copy/Paste, but the source is one of your saved Reminders instead of a live
transaction. Useful for a split pattern you use repeatedly - set it up once as a Reminder, then
apply it whenever you need it. The Reminder itself never needs to actually fire.

The target must pass the exact same rules as a Paste target above (protected data, account type,
unreconciled, currency-consistent splits) - the only difference is what currency it needs to
match: a Reminder's own transaction currency, rather than a previously copied one.

Only Reminders set up as transaction-type reminders are ever considered as a source - plain
note-style reminders are always excluded, with no config option to include them.

At least one Reminder must also qualify as a valid source (same rules as Copy above applies to
the Reminder's own transaction) before this option appears at all. Double-click a Reminder in
the picker (instead of selecting it and clicking OK) to apply it straight away. Which Reminders
show up in the picker can be narrowed further in the config screen:
  - require the Reminder's own account to exactly match the target account
  - include or exclude Reminders that only have a single split
  - exclude Reminders that are expired/inactive
  - filter the displayed list by using a text string that will be filtered against the
    Reminder's name

APPLY SPLITS TEMPLATE TO SELECTED TRANSACTIONS
---------------------------------------------------
Select 2 to 9 transactions at once (instead of just one) and choose this option to apply the
same template to all of them in a single step - useful if you have several individual
transactions that all need the same split pattern, rather than doing them one at a time.

This is strict, all-or-nothing: the option only appears if every single selected transaction
passes every rule - each one must be a Parent transaction (not a split row), have only one
split, be in the same account as every other selected transaction, and otherwise meet the same
target rules as Paste above (protected data, account type, unreconciled, currency-consistent).
If even one selected transaction fails any rule, the option doesn't appear at all - turn on
"Enable debug messages" to see which transaction and rule caused it to be withheld (checking
stops at the first problem found, so there could be others further down the selection too).

After picking a template, you'll be asked once - not once per transaction - whether to use
Exact amounts (remainder on a new split) or Allocate by % for any selected transaction whose
total doesn't match the template's total; whichever you choose applies to every transaction that
needs it. This dialog always appears and always asks, regardless of the "Default Allocation
Method" config option below - that option only affects which choice is pre-selected here. This
also warns that each selected transaction's existing split will be replaced.

Every transaction gets applied in one single undo step. A summary afterward tells you how many
of the selected transactions were actually updated; if any were skipped (most likely because
something changed between right-clicking and confirming), check the debug log for details.


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


UPDATE REMINDER VALUE
-------------------------
Right-click a single transaction in a Bank or Credit Card account and, depending on what's
found, one of two options appears - only ever one of the two, never both. Only Reminders set up
as transaction-type reminders are ever considered - plain note-style reminders are always
excluded.

  - Update Reminder and transaction's value - shown when the transaction has a single split, and
    exactly one active Reminder in the same account has a single split with the exact same
    value. Opens a dialog showing the reminder's current ("From") value and lets you enter a new
    one, with Reset (back to the transaction's value) and Rewind (back to the reminder's current
    value) buttons alongside the field. A checkbox lets you also update the selected
    transaction's own value to match, in the same undo step - only available when the
    transaction and all its splits are Unreconciled and hold no protected downloaded/online-bank
    data; it's ticked by default whenever it's available.

    If more than one reminder shares that same value, or none of them share the transaction's
    exact description, you'll first see a short list to choose from before the value dialog
    appears - this is just a confirmation step, not a strict block. The list is ordered by how
    closely each reminder matches the transaction (value, then number of splits, then shared
    categories), most likely match first, rather than alphabetically.

  - Update Reminder from selected transaction - shown instead whenever no reminder's value
    exactly matches (or the transaction has more than one split). Opens a list of every eligible
    reminder in the same account, again ordered by closeness to the selected transaction rather
    than alphabetically; whichever one you pick has its stored transaction completely replaced
    with a copy of the one you selected - description, splits, categories, and all, not just the
    value. Useful for keeping a reminder in step with a downloaded transaction whose description
    or categorisation doesn't resemble anything the reminder was originally set up with.

This feature only ever changes the Reminder itself (and, if you tick the checkbox in the first
option, the transaction you right-clicked) - it never touches any other transaction in your
register, and a downloaded/matched transaction is never modified by this feature regardless of
which option you use.


EDIT ORIGINATING REMINDER
-----------------------------
Right-click a transaction and choose this option to open, ready for editing, the Reminder that
created it - useful when a scheduled bill's amount or other details have changed and you want to
bring the Reminder in line, starting from the transaction it already produced.

This only appears when a link back to a specific Reminder can be found, checked two ways:
  - Moneydance's own internal identifier, which it creates itself whenever a Reminder
    auto-commits a transaction
  - failing that, this extension's own record of having applied a Splits Template (single or to
    multiple selected transactions) from that Reminder to this transaction

Neither is a guess based on matching description or value - both are exact identity links. If
the transaction wasn't auto-committed from a Reminder, and never had a Splits Template applied
to it by this extension either, this option simply doesn't appear.


ZAP/CLEAN MEMO
------------------
Select one or more downloaded/imported transactions and choose this option to clean up junk or
redundant Memo fields - either blanking them out, or moving the memo into the Description first
if the Description is currently blank. This is a scaled-down, selection-based version of the
separate "Toolbox: Zap md+/ofx/qif (default) memo fields" extension, which sweeps a whole account
by date range instead - use that one for a big one-off cleanup, use this one for a quick tidy-up
of whatever you're already looking at.

This changes data, but every run goes through a single named Undo step - Menu > Edit > Undo
reverses it immediately if you change your mind, same as any other change in Moneydance.

All selected transactions must be in the same account, and that account must be Bank, Credit
Card, or Investment. Non-downloaded, non-imported transactions and split rows in the selection
are simply ignored, not blocked. Whether the menu item appears at all is a purely structural
check - selection size, same account, account type and Active status - it never looks at any
transaction's content or any of the settings below, so the option won't mysteriously vanish just
because you haven't configured anything yet, and it won't promise candidates that turn out not to
match once you're in the settings dialog either.

If you've selected more than 30 transactions, you'll be asked to confirm before continuing, since
a large batch can't easily be reviewed item-by-item first.

Clicking the option opens a small settings dialog (remembered per account, so different accounts
can be configured differently), starting with a line telling you how many of the selected
transactions currently look like candidates under your saved settings. Below that:
  - Which download types to include: MD+ downloads (Moneydance, via Plaid), OFX Direct Connect
    downloads (OFX+), manually imported .ofx/.qfx files (OFX-), downloaded .qif files (QIF+), and
    manually imported non-downloaded .qif files (QIF-). Each shows how many of that type are in
    your current selection, and greys out (though stays visible) for any type with none present -
    ticking a greyed-out option would have no effect anyway.
  - Only reconciled transactions (on by default)
  - Only confirmed transactions (on by default; bypassed for QIF-, which has no such concept)
  - Zap unchanged memo when it's already contained in a longer description
  - Swap memo into description when description is the same text, just shorter than the memo -
    not just any shorter description, it has to match exactly within the memo
  - Two more aggressive options, both off by default:
    - Don't check the original downloaded memo first (a memo that's been edited since it was
      downloaded is normally left alone - this bypasses that protection). Note that QIF-
      transactions are never protected this way regardless of this setting, since there's no
      original download to compare against
    - Don't compare memo to description at all - just zap (reconciled-only, confirmed-only, and
      the edit-protection check above still apply on top of this)

The "original downloaded memo first" check compares against Moneydance's own hidden record of
what was actually downloaded, separate from whatever the Memo field shows now - you can view it
yourself on any transaction via right-click > Show Transaction Details.

QIF- (manually imported, non-downloaded .qif files) behaves differently from the other four types
throughout this whole tool, for one consistent reason: it never went through Moneydance's online
banking pipeline at all - no download, no Confirm/Merge step, none of the usual metadata the
other four types have. That's why:
  - "Only confirmed transactions" has no effect on QIF- - there's no online-match status to check
  - The edit-protection check ("don't check the original memo first") never applies to QIF-
    either way, ticked or not - there's no originally-downloaded memo to compare against
  - Even identifying a transaction as QIF- in the first place relies on a weaker signal than the
    other four types (a single stored marker, rather than a genuine download-source record)
None of this is leniency - QIF- simply doesn't carry the data these checks need.

A memo exactly matching the description is always zapped, and a blank description always gets
the memo swapped into it, regardless of the settings above - those two cases have nothing worth
protecting either way. MD+ transactions are always zapped once found eligible (matching the
original tool's own behaviour, since their memos are typically unhelpful boilerplate) -
unconditionally, ignoring every other setting on this list once it's ticked.

Memos shown in [square brackets] belong to the other side of a transfer and can't be changed from
this account - right-click the transaction and choose "Show other side" to zap it from there
instead.

This only ever touches the Memo and Description fields - nothing else about the transaction is
changed. Afterward you'll see a plain message saying how many of the selected transactions were
actually changed - there's no separate report to review, unlike the full Toolbox extension. Turn
on "Enable debug messages" in the config screen beforehand if you want to see exactly why any
particular transaction was skipped.


SHOW OTHER SIDE: SELECT SPLIT
---------------------------------
Right-click a transaction with 2 or more splits and pick this option to jump straight to any
other part of it - the parent, or any sibling split - instead of clicking through the register
manually. By default this only appears for transactions with 2 or more splits; a config option
(see below) can turn it on for single-split transactions too. The menu text shows how many
splits the transaction has.

At the top of the window you'll see a summary of the transaction you right-clicked: whether it's
the Parent or a Split, its account, description, date, and value.

Below that, the list shows every option labelled by position: "Parent" if you started from a
split row, plus every OTHER split numbered by its position in the transaction - skipping
whichever one you're currently on, without renumbering the rest (e.g. right-click split 3 of 5
and the list reads Parent, 1, 2, 4, 5). Each entry shows its account, account type, and amount.
Double-click an entry (instead of selecting it and clicking OK) to jump straight there.

Security and Root type accounts are shown in the list but greyed out and can't be selected -
there's nothing useful to jump to for those.

For investment transactions, each entry's first line shows what role that split actually plays
(Buy, Sell, Dividend, Fee, and so on) instead of just repeating the transaction's description on
every row - the account/amount details stay on the second line as usual.

If the split you're about to jump to is a Category (an Income or Expense account), you'll be
asked to confirm first by default - editing transactions from inside a Category register can be
confusing, so this is a chance to back out. This can be turned off in the config screen.

Three related options in the config screen, all under this feature's own checkbox:
  - Warn before showing a Category split - the confirmation above (default on)
  - Show full account names (not just account name) - switches every account name shown in this
    feature between the full account path and just the short name; defaults to whatever your
    Moneydance "show full account path" preference is set to the first time you use it, then
    stays as you've set it here regardless of that preference changing later
  - Include single-split transactions - turns this feature on even for transactions with only
    one split, where the only "other side" to jump to is the parent (or vice versa) (default off)


JUMP TO DATE IN REGISTER
----------------------------
Quickly jump the register to a specific date, instead of scrolling.


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


DEBUG MESSAGES
----------------
The config screen has an "Enable debug messages" checkbox. Turning it on makes the extension
write extra diagnostic information to Moneydance's console/log (accessed via Help / Console
Window) - mainly useful if something isn't behaving as expected and you want to see what the
extension is actually doing. In particular, this will show messages when the Copy Splits, Paste
Splits, Apply Splits Template, Rebalance Splits, Duplicate Transactions, or Update Reminder
Value menu items have been blocked, explaining exactly why the option was not allowed. Show
Other Side: Select Split does not currently have this diagnostic logging.


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
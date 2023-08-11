Help / Guide for 'Toolbox: Zap md+/ofx/qif (default) memo fields' Extension Menu
------------------------------------------------------------------------------------------------------------------------
Note: The extension will quit so you can read this guide. When ready, (re)launch the extension again.

THIS EXTENSION CHANGES DATA. Recommended action is to first perform a BACKUP OF YOUR DATA.
Also, this extension enables the Edit/Undo system for your changes should you wish to undo them.
DISCLAIMER: YOU USE THIS EXTENSION AT YOUR OWN RISK AND YOU ACCEPT ANY CONSEQUENCES OF CHANGING YOUR DATA!
------------------------------------------------------------------------------------------------------------------------
PURPOSE:

This extension's main function is to remove ('zap') unwanted memos from transactions (particularly when downloaded)
Some downloaded memos are not helpful and clutter your transaction list. Depending on the settings it can also swap the
description and memo fields.
------------------------------------------------------------------------------------------------------------------------
WHAT HAPPENS:

A popup settings screen allows you to choose the criteria used in selecting which memos to zap or swap.

- Only Active Bank, Credit Card and Investment accounts are listed / searched.
- When All accounts is selected, the following settings are NOT saved as they zap more extensively.
    - Include NON downloaded / file imported QIF memo fields 'QIF-'
    - Don't compare memo to description (just zap)
    - Don't check / compare the original downloaded memo first
------------------------------------------------------------------------------------------------------------------------
DEFINITIONS:

The types of files are:
MD+  : Moneydance downloads (via Plaid)
OFX+ : OFX 'Direct Connect' downloads
OFX- : manual .ofx / .qfx file downloads/imports
QIF+ : manual .qif file downloads/imports
QIF- : import of manual non-downloaded .qif files (from Quicken or other programs)
       (the Moneydance Confirm/Merge options do not appear with QIF- txns...)

 - olmemo:        the hidden original memo that was downloaded (right-click, then 'Show Transaction Details' to view)
 - changed memo:  when olmemo is blank or txn memo is different to olmemo (i.e. memo created / edited by user)
------------------------------------------------------------------------------------------------------------------------
CRITERIA:

Select Account: One or all accounts can be selected. You can set criteria by account.
Months to look back: Default is 300 months, used as an initial zap for an entire account (valid range between 1-600).
Ideally shorten to perhaps 1 month after first use for better performance...

Only reconciled/confirmed transactions are chosen by default, but you can change this.
    - QIF- is an exception as the 'confirmed' check will be bypassed

You can then choose one or more of the download types types to zap.
You can also choose to zap/swap memos based on whether the memo is contained within the description or vice-versa.

The next two criteria are a bit more extensive (and potentially more 'risky' to run)':
- Don't check/compare the original downloaded memo first: This zaps memos (irrespective of whether you manually edited
  / created them).

- Don't compare memo to description (just zap) - Similar to how the MD+ selection works.
  Just zap the memo based on the criteria set.
------------------------------------------------------------------------------------------------------------------------
INITIATION/PROCESSING:

Set up your criteria. Click the ANALYSE button. Examine what is offered to zap.
If not to your liking, click CANCEL, start again and change the criteria.
If you want to zap these, click ZAP/SWAP MEMOS?
If you click ZAP/SWAP, it automatically happens. You can immediately Menu Edit/UNDO if you change your mind.
------------------------------------------------------------------------------------------------------------------------
FINALISATION:

You can undo a set of zaps, but if instead you do another set, the first undo goes away.
If you really don't like what happened, but you've done a lot, you can restore your backup.
Otherwise, congratulations - a lot of pesky memos are now gone, and your transaction list is cleaner.
------------------------------------------------------------------------------------------------------------------------
KNOWLEDGE:

Rules used to zap:
MD+    : always zap all original (unchanged) downloaded memos (based on settings chosen).

OFX/QIF:
    Stage 1 - 'changed memo check'
        if 'QIF-' then bypass this check
        if setting 'Don't check / compare the original downloaded memo first' ticked then bypass this check
        if 'changed memo check' then skip record
        if pass stage 1, then onto stage 2 below....

    Stage 2 - Zap/Swap check:
        Definition: setting = 'Zap unchanged memo when memo already within (longer) description'

        if setting 'Don't compare memo to description (just zap)' ticked then
               flag memo for ZAP (and continue with the checks below)

        if description is not blank and description matches memo then
               flag memo for ZAP
        elseif description blank and memo not blank then...
               flag for SWAP with description and flag memo for ZAP
               NOTE: There will be a '##' marker if the 'swap' setting was not ticked
        elseif memo found in description and if memo shorter than txnDesc then if setting ticked then
               flag memo for ZAP
        elseif description found in txnMemo and if description shorter than memo then if 'swap' setting ticked then
               flag for SWAP with description and memo ZAP

        if nothing flagged, then skip record....

NOTE: Memo fields that existed before being merged with downloaded transactions are treated as changed/edited memos.
      This might include auto filled, from Reminders, or manually entered memos. This extension will assume that these
      are wanted and should remain. For md+, these will never get zapped. For the other types you must tick the setting
      'Don't check / compare the original downloaded memo first' to allow the zap to take place.

NOTE: Memos contained within [brackets] originate from the 'other side' of this txn (i.e. the linked account) and cannot
      be zapped. You can only zap memos using this extension from the account where the txn / memo originated.
      To view the other side, highlight the txn, select right-click then 'Show other side'.
------------------------------------------------------------------------------------------------------------------------
Author: Stuart Beesley - StuWareSoftSystems 2023
Credit: Dan T Davis & DerekKent23 for their extensive testing and many hours on this project!
------------------------------------------------------------------------------------------------------------------------

Thanks for reading...

Get more Scripts/Extensions from: https://yogi1967.github.io/MoneydancePythonScripts/

<END>
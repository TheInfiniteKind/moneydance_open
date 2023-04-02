Help / Guide for Move Investment Transactions extension.
------------------------------------------------------------------------------------------------------------------------
Note: The extension will quit so you can read this guide. When ready, (re)launch the extension again.

PLEASE BACKUP YOUR DATA WHEN MAKING CHANGES! The extension will offer you the choice to backup before making changes.
DISCLAIMER: YOU USE THIS EXTENSION AT YOUR OWN RISK AND YOU ACCEPT ANY CONSEQUENCES OF CHANGING YOUR DATA!

------------------------------------------------------------------------------------------------------------------------
PURPOSE:
This extension allows you to move transactions from one investment account to another. The Moneydance 'Batch Change'
right-click context menu does not allow you to do this as it's complicated. This extension knows how to move these txns.

------------------------------------------------------------------------------------------------------------------------
WHAT HAPPENS:
At launch you may see 'Quote Loader / Q&ER running. Please verify it's not updating before running'. When performing a
large move, you should ideally ensure that these extensions are not updating at the same time. It doesn't matter too
much, other than before / after valuations may change if something is updating security price records at the same time.

At launch, this extension checks for data consistency before allowing you to proceed. If you see the following message:
'ERROR - Cross-linked (or Orphaned) security txns detected..', then you have a data issue that needs fixing before
proceeding. Toolbox 'MENU: Transaction tools' > 'FIX: Non-Hierarchical Security Acct Txns (& detect Orphans)' can do
this for you. Rarely if you have force deleted a security from an account (or if you have one-sided, old, QIF imported
txns) then Toolbox may not be able to correct the situation. If this occurs, reach out for guidance, but you will have
to manually correct your data first.

This extension performs extensive validation before doing anything. It will not proceed if anything fails validation
(see below for details). Irrespective, after you click PROCEED, after validation, the extension pauses, shows you the
log and asks if you want to proceed. It also offers you the opportunity to perform a backup. Once the move has occurred,
an updated log will appear for your perusal.

All that has to (pre)exist for a move, is the target investment account. It can be completely new/empty. Equally, it does
not matter if the target account already holds many securities and transactions. This extension will take care of
assigning new securities into the target account if necessary.

------------------------------------------------------------------------------------------------------------------------
KNOWLEDGE (a small lesson):
If you know everything there is to know about investment transactions, including average cost vs LOT control, skip this.

In Moneydance, investment transactions are both special and complex. They are different from other transaction types.
This is because they can hold many (invisible) splits, including: cash txfr, income, expense, commission and security.

Securities are configured with a 'Cost Basis' as either Average Cost controlled, or LOT controlled using the
Investment Account's 'Securities Detail' page > 'Edit Security' button. The default is Average Cost control and often
this setting is never actually set by the user as it can easily be overlooked. The cost basis setting can be configured
by investment account, and can be different across accounts.

The purpose of the cost basis setting is to determine how Moneydance calculates the cost basis of your shares. This is
critical for calculating capital gains and tax reports. Simplistically speaking, when using average cost, the average
purchase price of your Buys are used to calculate the cost basis, and then your Sells use the calculated average.

However, when using LOT control, you match Sells to Buys (matched 'sets') using the 'Edit Lots' button. In this
scenario, your cost basis is calculated per matched set. Sells can be matched to many different buys. Buys can be
partially sold by many different Sell transactions. The Edit Lots window helps you manage and track this. This
information is held against the security split and is hidden.

When using Average Cost control, there is normally no LOT matching information held against the security. HOWEVER, if
you enable LOT control and perform some LOT matching, and then later switch to Average Cost control, the hidden LOT
matching data that you created will still exist on the security records. If you switch back to LOT control, then this
pre-existing matching data will again be visible in the Edit Lots window.

The cost basis setting is important and very relevant to this extension. This is because if you move transactions from
investment account A to B, and A uses LOT control and B uses average cost (for example), then the extn needs to know how
to handle the underlying (hidden) LOT matching data. In this scenario, you need to determine if you should keep the LOT
matching data and copy it across, or dump the matching data as average cost control in the target account does not
actually require it? The processing options allow you to decide on the approach you want to take.

Similarly, if you are moving a subset of transactions containing LOT matching data, you need to ensure that you move
matched sets and that you do not separate Sells from the matched Buy transactions. This extension will detect and warn
you if you attempt to do this. The processing options allow you to force this move to occur and to dump or keep the
hidden LOT matching data.
------------------------------------------------------------------------------------------------------------------------

TIPS:
- Moving all txns in an account, or all txns for a selected security, is one of the simplest options.
- Using a date range filter or (pre)selecting from the register runs the risk of separating Buys from Sell txns.
- Moving txns where both the source and target security use average cost control is a simple scenario.
- Moving from/to different cost basis types causes complexity.
- Moving from/to LOT controlled securities can be simple, as long as you don't separate Buys from Sells.
- You can only move all/part of an investment account's initial [cash] balance from Source to Target as part of a
  transaction move. I.e. You cannot move the initial [cash] balance with no transactions. You should do this manually.
  Use Moneydance > highlight the investment account in the side bar > ACCOUNT > EDIT ACCOUNT to adjust initial balance.
- MD2023 introduces Balance Adjustment (by adding to the opening / start balance). Any move will be blocked by this
  utility until you manually remove the account's balance adjustment (Tools>Accounts>Select>Edit...)
------------------------------------------------------------------------------------------------------------------------
INITIATION:
You start the extension by selecting the Moneydance Extensions Menu and selecting: Toolbox: Move investment transactions

There are two modes of operation:
1. Move all transactions, or filter by Security, and/or date range. Ensure no transactions are selected before executing
2. Select any number of transactions within an investment account register that you want to move BEFORE running the extn
>> The options presented will change depending on the mode of operation you have selected.

Mode-1: Move all transactions / filter by security and/or filter by date range:
- Select the source investment account. This is where your transactions are now.
- Select the target investment account. This is where your transactions will be moved to.
- Tick Enable filter by security: to select and move all transactions for ONLY one security (and leave the rest alone)
- Tick Enable date range filters: to select transactions that fall between the date range that you specify....
  NOTE: If filter by security is also selected, then you will filter by security AND date range.
        If filter by security is not selected, then the date filter applies to all transactions on the source account.

Mode-2: Move only the transactions selected in the register:
- The source account will be pre-selected and locked in.
- Select the target investment account. This is where your transactions will be moved to.

------------------------------------------------------------------------------------------------------------------------
PROCESSING OPTIONS: (These dictate how the extension operates under certain conditions).
- The default settings are very 'safe' and you should leave these settings unchanged for the first attempt of the move.

- When you click PROCEED, the extension will VALIDATE the move, and it will present you with any problems found.
  > The extension will always show you the log/validation and ask you to confirm to proceed with the move, or to cancel.
  > By default, all validation checks will take place and a move will always be blocked if any errors are detected.

- Only when you have reviewed the validation, and after you understand any issues, should you change the default options
  > These options below allow you to ignore detected errors and force the move to occur.

** NOTE: When making another move attempt, ensure any option you were previously advised to select are reselected...
         I.E. as mentioned below, to correct some validation errors you may need multiple processing options selected.

- Auto MERGE Source Account's initial [cash] balance to Target's?
    > [Specify the amount of the existing initial [cash] balance to move]
- Auto ALLOW Source Account's Cash balance to go negative?
- Auto IGNORE where the share balance (by security) of selected txns to move is negative?
- Auto IGNORE any differences between Avg Cst & LOT Control flags and Merge anyway?
- Auto DELETE any related LOT records on txns moved that separate matched Buy/Sell LOTs?
- Select option when target uses 'average cost control' and txns being moved contain matched LOT data:
    > CHECK/WARN:        Validate for where Txns contain matched LOT records when the target uses Average Cost Control
    > IGNORE PROBLEM(s): Copy any existing matched LOT records unchanged when target uses Average Cost Control
    > WIPE:              Delete any matched LOT records from txns being moved when target uses Average Cost Control
- Auto IGNORE any account 'Loops' and Merge anyway?
- Auto DELETE Empty Source Account (only actions if empty after processing)?
- Auto SAVE-TRUNK - Immediately flush all changes back to disk (Use when making large changes)?

[Auto MERGE Source Account's initial [cash] balance to Target's?]
If the source account contains an 'Initial Balance' (can be seen on Tools>Accounts>Edit), then it will be displayed here
.. By default, it will pre-populate with the total initial [cash] balance. You edit this number and this amount will be
moved to the target account, and deducted from the source account.

[Auto ALLOW Source Account's Cash balance to go negative?]
Validation ensures that the total cash balance of transactions being moved is not negative. It also ensures that the
move would not leave the source account with a negative cash balance. This option allows you to force the move to occur.

[Auto IGNORE where the share balance (by security) of selected txns to move is negative?]
Validation ensures that the total share balance (per security) of transactions being moved is not negative. It also
ensures that the move would not leave the source account with a negative share balance (per security). This option
allows you to force the move to occur. Note: When highlighting one or more transactions in a Source account, for a given
security, the total number of shares of all selected Buy plus all selected Sell transactions must not be negative or the
move will be blocked by ‘a negative share balances FAILED VALIDATION’. The move will blocked even if after the move the
resultant number of shares would have been positive in both Source and Target accounts. Select this option to allow the
move.

[Auto IGNORE any differences between Avg Cst & LOT Control flags and Merge anyway?]                                (^^1)
Validation ensures that the source and target securities have the same cost basis setting. This option allows you to
force the move to occur. If forced, then any (pre)existing hidden LOT matching data will get transferred irrespective
of whether the target is average cost or LOT controlled. THIS SETTING INTERACTS WITH THE OTHER COST BASIS OPTIONS.

[Auto DELETE any related LOT records on txns moved that separate matched Buy/Sell LOTs?]                           (^^2)
Validation ensures that where (hidden) LOT matching data exists, that matched Buy & Sell transactions are not separated.
This is irrespective of the cost basis setting. This option allows you to ignore the separation of matched Buys/Sells.
If forced, then where matched LOTs would be separated, the relevant (hidden) LOT matching data will be removed from the
Sell transaction. This deletion of LOT data could take place in the source or target account depending on what is being
moved where. THIS SETTING INTERACTS WITH THE OTHER COST BASIS OPTIONS.

    NOTE: It's technically possible that you may have (pre)exiting data errors in relation to your (hidden) lot matching
    data. Potentially where matched Buy/Sell txns no longer exist, or have somehow been separated. If detected, you will
    see ''*** Buy/Sell matched LOTs ERRORS EXIST. Cannot proceed. PLEASE FIX & TRY AGAIN ***'. You can use Toolbox to
    correct this situation. Use the 'FIX: Detect and fix (wipe) LOT records where matched Buy/Sell records are invalid'
    feature in MENU: Currency & Security tools.

[Select option when target uses 'average cost control' and txns being moved contain matched LOT data]              (^^3)
  > CHECK/WARN [Default] Validates for where Txns contain matched LOT records when the target uses Average Cost Control
    Validation ensures that when txns are being moved from source using LOT control, to target using average cost,
    that the source txn (per security) does not contain (hidden) LOT matching data. If it does, then the move will be
    blocked by default. You are able to force the move to occur, but you must decide on how this is handled by using one
    of the other two options in this drop down.

  > IGNORE PROBLEM(s): Copy any existing matched LOT records unchanged when target uses Average Cost Control
    If this option is selected, then any (pre)existing (hidden) LOT data will simply be copied across to the target.
    The data will not be visible and is ignore by Moneydance, unless you re-enable lot control on the target security.

  > WIPE: Delete any matched LOT records from txns being moved when target uses Average Cost Control]
    If this option is selected, then any (pre)existing (hidden) LOT data will be dumped and not copied across to the
    target security. As the target security is using average cost control, this would be perfectly acceptable.
  THIS SETTING INTERACTS WITH THE OTHER COST BASIS OPTIONS.

>> NOTE: You may need to combine multiple cost basis processing options to force your move to occur! EXAMPLES:
   - If matched lot separation is detected, and also source is lot controlled, but target is average cost, then you will
     need to select options (^^1) AND (^^2) AND (^^3 - IGNORE or WIPE).
   - If target is average cost controlled and the source data contains (hidden) lot matching data (irrespective of
     whether the source is average cost or lot controlled), then options (^^1) AND (^^3 - IGNORE or WIPE)  would need to
     be selected.

[Auto IGNORE any account 'Loops' and Merge anyway?]
Investment accounts can transfer cash to/from another investment account. This can be via Xfr, SellXfr, BuyXfr txns. If
for example, you have Xfrs occurring to/from investment account A to/from B and you move txns from A to B, then you will
end up with transactions in B that are Xfrs to/from itself (i.e. B to/from B). This is referred to as a 'loop' and is
completely illogical. If you select this option, then you will force the move to occur and you will create txn 'loops'.
You can do this, and then manually edit the txns afterwards to correct the situation. Or you can edit the txn before the
move to ensure that no 'loops' are created.

[Auto DELETE Empty Source Account (only actions if empty after processing)?]
After the move, it's possible that the source account will be empty and contain no transactions. If you select this
option, then the source account will be deleted after the move. The deletion will only take place if the source account
is actually empty and also does not hold any remaining 'initial [cash] balance'. This option will be ignored if these
conditions are not met, so you can safely tick this option (if you now longer want the source account).

[Auto SAVE-TRUNK - Immediately flush all changes back to disk (Use when making large changes)?]
Moneydance does NOT normally update the dataset on disk (known as 'trunk' until you restart MD. The first procedure MD
undertakes when launching is to re-read all recent change txns, then update and save the dataset. When making small
updates you do not need to concern yourself with this. But when making a massive change then it can be a good idea to
immediately update/save your dataset on disk, to prevent MD having to redo all the save changes at next (re)launch. So,
if you are simply moving a handful of investment txns, leave this setting off. However, if you are moving 100s or 1000s
of txns then it would be a good idea to select this option.

------------------------------------------------------------------------------------------------------------------------
Author: Stuart Beesley - StuWareSoftSystems 2022
Credit: Derek Kent(23) for his extensive testing and many hours on this project!
------------------------------------------------------------------------------------------------------------------------
Thanks for reading...

Get more Scripts/Extensions from: https://yogi1967.github.io/MoneydancePythonScripts/

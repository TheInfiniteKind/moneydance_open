/*************************************************************************\
* Copyright (C) 2009-2011 Mennē Software Solutions, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.findandreplace;

/**
 * <p>Localizable string keys to look up in resources. Keeping all of these keys in one place
 * helps simplify tracking localized resources. It also helps when it comes time to audit for
 * unused strings.</p>
 *
 * @author Kevin Menningen
 * @version 1.60
 * @since 1.0
 */
class L10NFindAndReplace
{
    public static final String LABEL_COLON = "labelColon";
    public static final String TITLE = "title.text"; // Find and Replace
    public static final String VERSION_FMT = "version.format"; //Version V (Build B)

    public static final String FIND_LABEL = "findLabel.text"; // Find
    public static final String FIND_BOOL_LABEL = "combine_criteria"; // = Combine Criteria:
    public static final String FIND_BOOL_AND_MNC = "findBooleanAnd.mnemonic"; // N
    public static final String FIND_BOOL_OR_MNC = "findBooleanOr.mnemonic"; // R
    public static final String FIND_ACCOUNTS_LABEL = "accounts"; // = Accounts:
    public static final String FIND_ACCOUNTS_MNC = "findAccountsLabel.mnemonic"; // A
    public static final String FIND_ACCOUNTS_SELECT_TEXT = "findAccountsSelect.text"; // = Select
    public static final String FIND_ACCOUNTS_SELECT_MNC = "findAccountsSelect.mnemonic"; // = S
    public static final String FIND_CATEGORIES_LABEL = "category"; // = Categories:
    public static final String FIND_CATEGORIES_MNC = "findCategoriesLabel.mnemonic"; // A
    public static final String FIND_CATEGORIES_SELECT_TEXT = "findCategoriesSelect.text"; // = Select
    public static final String FIND_CATEGORIES_SELECT_MNC = "findCategoriesSelect.mnemonic"; // = S
    public static final String FIND_AMOUNT_LABEL = "amount"; // = Amount:
    public static final String FIND_AMOUNT_MNC = "findAmountLabel.mnemonic"; // = O
    public static final String FIND_DATE_LABEL = "srch_by_date"; // = Date:
    public static final String FIND_DATE_MNC = "findDateLabel.mnemonic"; // = E
    public static final String FIND_FREETEXT_LABEL = "findFreeTextLabel.text"; // = Free Text:
    public static final String FIND_FREETEXT_MNC = "findFreeTextLabel.mnemonic"; // = F
    public static final String FIND_FREETEXT_DESCRIPTION = "desc"; // = Search Description
    public static final String FIND_FREETEXT_DESC_TIP = "findDescription.toolTip";
    public static final String FIND_FREETEXT_MEMO = "memo"; // = Search Memo
    public static final String FIND_FREETEXT_MEMO_TIP = "findMemo.toolTip";
    public static final String FIND_FREETEXT_CHECK = "table_column_checknum"; // = Search Check #
    public static final String FIND_FREETEXT_CHECK_TIP = "findCheck.toolTip";
    public static final String FIND_FREETEXT_SPLITS = "findSplits.text"; // = Include Splits
    public static final String FIND_FREETEXT_SPLITS_TIP = "findSplits.toolTip";

    public static final String FIND_TAGS_LABEL = "findTagsLabel.text"; // = Tags:
    public static final String FIND_TAGS_MNC = "findTagsLabel.mnemonic"; // = T
    public static final String FIND_NOT = "findNot.text"; // = but not
    public static final String FIND_TAG_AND = "findAnd.text"; // And
    public static final String FIND_TAG_OR = "findOr.text"; // Or
    public static final String FIND_TAG_EXACT = "findExact.text"; // Exact

    public static final String FIND_CLEARED_LABEL = "cleared"; // = Cleared
    public static final String FIND_CLEARED_MNC = "findClearedLabel.mnemonic"; // = L
    public static final String FIND_USE_TIP = "findUse.toolTip";
    public static final String FIND_RECONCILING_LABEL = "reconciling"; // = Reconciling
    public static final String FIND_UNCLEARED_LABEL = "uncleared"; // = Uncleared
    public static final String FIND_CLEARED_TIP = "findCleared.toolTip"; // = Include cleared transactions
    public static final String FIND_RECONCILING_TIP = "findReconciling.toolTip"; // = Include reconciling transactions
    public static final String FIND_UNCLEARED_TIP = "findUncleared.toolTip"; // = Include uncleared transactions
    public static final String USE_TAX_DATE_MNC = "findUseTaxDate.mnemonic"; // X

    public static final String REPLACE_LABEL = "replaceLabel.text"; // = Replace
    public static final String REPLACE_CAT_LABEL = "category"; //  = Category:
    public static final String REPLACE_CAT_MNC = "replaceCategoryLabel.mnemonic"; //  = G
    public static final String REPLACE_AMOUNT_LABEL = "amount"; //  = Amount:
    public static final String REPLACE_AMOUNT_MNC = "replaceAmountLabel.mnemonic"; //  = U
    public static final String REPLACE_DESCRIPTION_LABEL = "desc"; //  = Description:
    public static final String REPLACE_DESCRIPTION_MNC = "replaceDescriptionLabel.mnemonic"; //  = C
    public static final String REPLACE_TAGS_LABEL = "replaceTags.text"; //  = Modify tags:
    public static final String REPLACE_TAGS_MNC = "replaceTags.mnemonic"; //  = F
    public static final String REPLACE_TAGSADD_LABEL = "replaceTagsAdd.text"; //  = Add tags:
    public static final String REPLACE_TAGSREMOVE_LABEL = "replaceTagsRemove.text"; //  = Remove tags:
    public static final String REPLACE_TAGSREPLACE_LABEL = "replaceTagsReplace.text"; //  = Replace with:
    public static final String REPLACE_TAGSADD_MNC = "replaceTagsAdd.mnemonic"; //  = A
    public static final String REPLACE_TAGSREMOVE_MNC = "replaceTagsRemove.mnemonic"; // = V
    public static final String REPLACE_TAGSREPLACE_MNC = "replaceTagsReplace.mnemonic"; //  = W
    public static final String REPLACE_MEMO_LABEL = "memo"; //  = Memo:
    public static final String REPLACE_MEMO_MNC = "replaceMemoLabel.mnemonic"; //  = M
    public static final String REPLACE_CHECK_LABEL = "txn_checknum"; //  = Check#:
    public static final String REPLACE_CHECK_MNC = "replaceCheckLabel.mnemonic"; //  = K
    public static final String REPLACING_PROGRESS = "replaceProgress.text"; // Replacing ...
    public static final String REPLACE_FOUND_TEXT_ONLY = "replaceOnlyFound"; // Found text only
    public static final String CONSOLIDATE_SPLITS = "showParents.text"; // Consolidate splits
    public static final String CONSOLIDATE_SPLITS_TIP = "showParents.toolTip";
    public static final String CONSOLIDATE_SPLITS_MNC = "showParents.mnemonic";
    public static final String RESULTS_LABEL = "resultsLabel.text"; //  Find Results
    public static final String RESULTS_COLUMN_DATE = "table_column_date"; // Date
    public static final String RESULTS_COLUMN_ACCOUNT = "table_column_account"; // Account
    public static final String RESULTS_COLUMN_DESCRIPTION = "table_column_description"; // Description
    public static final String RESULTS_COLUMN_TAG = "table_column_tags"; // Tag(s)
    public static final String RESULTS_COLUMN_CATEGORY = "category"; // Category
    public static final String RESULTS_COLUMN_CLEARED = "table_column_clearedchar"; //C
    public static final String RESULTS_COLUMN_AMOUNT = "table_column_amount"; // Amount
    public static final String RESULTS_SUMMARY_FMT = "resultsSummary.format";

    public static final String INCXFER_LABEL = "includeTransfers.text"; // Include Transfers
    public static final String INCXFER_TIP = "includeTransfers.toolTip"; // Allow all accounts to be included as categories
    public static final String INCXFER_MNC = "includeTransfers.mnemonic"; //D

    public static final String RESULTS_CHECKNO_LABEL = "table_column_checknum"; //  = Check#

    public static final String FIND_BUTTON_TEXT = "findBtn.text";
    public static final String FIND_BUTTON_MNC = "findBtn.mnemonic";
    public static final String REPLACE_BUTTON_TEXT = "replaceBtn.text";
    public static final String REPLACE_BUTTON_MNC = "replaceBtn.mnemonic";
    public static final String REPLACEALL_BUTTON_TEXT = "replaceAllBtn.text";
    public static final String REPLACEALL_BUTTON_MNC = "replaceAllBtn.mnemonic";
    public static final String GOTO_BUTTON_TEXT = "show_txn";
    public static final String GOTO_BUTTON_MNC = "gotoBtn.mnemonic";
    public static final String COPY_BUTTON_TEXT = "copyBtn.text";
    public static final String COPY_BUTTON_MNC = "copyBtn.mnemonic";
    public static final String RESET_BUTTON_TEXT = "resetBtn.text"; // = Reset

    public static final String CURRENCY_SHARES = "shares"; // = Shares

    public static final String ACCOUNTSELECT_TITLE = "select_acct_title";
    public static final String ACCOUNTSELECT_EXCLUDE = "accountselect.exclude.text"; // Excluded 
    public static final String ACCOUNTSELECT_INCLUDE = "accountselect.include.text"; // Included
    public static final String ACCOUNTSELECT_ADD = "accountselect.add.text"; // Add >
    public static final String ACCOUNTSELECT_ADDEXCEPT = "accountselect.addexcept.text"; // Add Except >>
    public static final String ACCOUNTSELECT_ADDALL = "accountselect.addall.text"; // Add All >>
    public static final String ACCOUNTSELECT_REMOVE = "accountselect.remove.text"; // < Remove
    public static final String ACCOUNTSELECT_REMOVEEXCEPT = "accountselect.removeexcept.text"; // << Remove Except
    public static final String ACCOUNTSELECT_REMOVEALL = "accountselect.removeall.text"; // << Remove All

    public static final String ACCOUNTFILTER_ALL = "accountfilter.all"; // All
    public static final String ACCOUNTFILTER_ALL_CATEGORIES = "all_categories"; // All Categories

    public static final String MARK_ALL_BUTTON_TEXT = "markAllBtn.text"; // Mark All
    public static final String MARK_ALL_BUTTON_MNC = "markAllBtn.mnemonic"; // M
    public static final String MARK_NONE_BUTTON_TEXT = "markNoneBtn.text"; // Mark None
    public static final String MARK_NONE_BUTTON_MNC = "markNoneBtn.mnemonic"; // N

    public static final String ERROR_TITLE = "error.title";
    public static final String ERROR_ACCOUNTNOTFOUND = "accountselect.accountnotfound";
    public static final String NOTICE_TITLE = "notice.title";

    /**
     * 0 = user-entered text  1 = error message
     */
    public static final String ERROR_REGEX_FMT = "error.regex";

    /** 0 = internal error message text. */
    public static final String ERROR_LOAD_FMT = "error.load";
    public static final String ERROR_NO_DATA = "error.nodata";


    // Stuff copied from the Moneydance resources
    public static final String OK = "ok";
    public static final String CANCEL = "cancel";
    public static final String NONE = "none"; // None
    public static final String DONE = "done"; // Done
    public static final String SPLIT_1 = "split_label1"; // -
    public static final String SPLIT_2 = "split_label2"; // splits -
    public static final String RECORD_BUTTON_TEXT = "record_txn";
    public static final String FIND_BOOL_AND = "srch_op_intersect"; // = And (Intersection)
    public static final String FIND_BOOL_OR = "srch_op_union"; // = Or (Union)
    public static final String FIND_BETWEEN = "srch_range0"; // = Between
    public static final String FIND_AND = "srch_range1"; // = and
    public static final String USE_TAX_DATE = "srch_use_tax_date"; // Use Tax Date

    // Account types copied from the Moneydance resources, would rather just get them from MD
    public static final String ACCOUNTTYPE_ASSET = "acct_type4300s"; //  = Asset
    public static final String ACCOUNTTYPE_BANK = "acct_type1000s"; //  = Bank
    public static final String ACCOUNTTYPE_CCARD = "acct_type2000s"; //  = Credit Card
    public static final String ACCOUNTTYPE_INCOME = "acct_type7000s"; //  = Income
    public static final String ACCOUNTTYPE_INVEST = "acct_type3000s"; //  = Investment
    public static final String ACCOUNTTYPE_LIABILITY = "acct_type4600s"; //  = Liability
    public static final String ACCOUNTTYPE_LOAN = "acct_type5000s"; //  = Loan
    public static final String ACCOUNTTYPE_EXPENSE = "acct_type6000s"; //  = Expense
    public static final String ACCOUNTTYPE_SECURITY = "acct_type4000s"; // = Security
    public static final String ACCOUNTFILTER_ALL_ACCOUNTS = "all_accounts"; // = All Accounts

    // Images
    public static final String FAR_IMAGE = "findAndReplace.image";
}

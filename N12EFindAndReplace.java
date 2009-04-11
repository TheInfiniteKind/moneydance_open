/*
 * N12EFindAndReplace.java
 *
 * File creation information:
 *
 * Author: Kevin Menningen
 * Date: Jan 26, 2008
 * Time: 1:45:32 PM
 */


package com.moneydance.modules.features.findandreplace;

/**
 * <p>Non-localizable (N12E) string statics. Keeping all strings out of the Java code makes it
 * much easier to know that everything is localized. Additionally, it forces the developer to
 * decide when they write a string constant: 'Will this be displayed to the user, or will it not?
 * Can this string be localized, or would localizing it break the software?'</p>
 *
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />

 * @author Kevin Menningen
 * @version 1.0
 * @since 1.0
 */
public class N12EFindAndReplace
{
    /** The name of the resource bundle file. */
    public static final String RESOURCES = FindAndReplace.class.getName();
    /** The command that is expected to be passed in to show the find/replace dialog. */
    public static final String INVOKE_COMMAND = "showdialog";
    /** Empty string. */
    public static final String EMPTY = "";
    /** Separate strings, as in a list of tags. */
    public static final String COMMA_SEPARATOR = ", ";
    /** Separate strings. */
    public static final String SPACE = " ";
    /** Indentation in a list. */
    public static final String INDENT = "     ";

    /** The title of the extension, if unavailable from resources. */
    public static final String TITLE = "Find and Replace";

    public static final String TABLE_ODD_BACKGROUND = "window";
    public static final String TABLE_EVEN_BACKGROUND = "control";

    /** Hard coded data format, would like to get these from user preferences. */
    public static final String DATE_FORMAT = "MM/dd/yyyy";
    /**
     * Regular expression prefix to find free text entered by the user. (?ui) switches to case
     * insensitive using the Unicode standard, \Q quotes the user's entry.
     */
    public static final String REGEX_PREFIX = "(?ui)\\Q";
    /**
     * Regular expression suffix to find free text entered by the user. \E ends the quote of the
     * user's entry.
     */
    public static final String REGEX_SUFFIX = "\\E";


    ///////////////////////////////////////////////////////////////////////////////////////////////
    // Properties Defined By Moneydance
    ///////////////////////////////////////////////////////////////////////////////////////////////
    /** Apparently hard-coded key used in tag set key,value pairs for the user-defined tags. */
    public static final String USER_TAG_KEY = "md.txntags";
    public static final String MD_OPEN_EVENT_ID = "md:file:opened";

    //////////////////////////////////////////////////////////////////////////////////////////////
    //  Properties for Property Change Notifications
    //////////////////////////////////////////////////////////////////////////////////////////////
    public static final String HOME_PAGE_ID = "MennesoftFindAndReplace";
    
    public static final String ALL_PROPERTIES = "UpdateAll";
    public static final String FIND_COMBINATION = "findCombination";
    public static final String ACCOUNT_SELECT = "accountSelect";
    public static final String ACCOUNT_USE = "accountUse";
    public static final String ACCOUNT_REQUIRED = "accountRequired";
    public static final String CATEGORY_SELECT = "categorySelect";
    public static final String CATEGORY_USE = "categoryUse";
    public static final String CATEGORY_REQUIRED = "categoryRequired";
    public static final String AMOUNT_USE = "amountUse";
    public static final String AMOUNT_REQUIRED = "amountRequired";
    public static final String DATE_USE = "dateUse";
    public static final String DATE_REQUIRED = "dateRequired";
    public static final String FREETEXT_USE = "freeTextUse";
    public static final String FREETEXT_REQUIRED = "freeTextRequired";
    public static final String FREETEXT_DESCRIPTION = "freeTextDescription";
    public static final String FREETEXT_MEMO = "freeTextMemo";
    public static final String FREETEXT_CHECK = "freeTextCheck#";
    public static final String FREETEXT_SPLITS = "freeTextIncludeSplits";
    public static final String TAGS_USE = "tagsUse";
    public static final String TAGS_REQUIRED = "tagsRequired";
    public static final String FIND_RESULTS_UPDATE = "findResultsUpdated";

    public static final String SELECT_TAG = "selectTag";

    public static final String REPLACE_CATEGORY = "replaceCategory";
    public static final String REPLACE_AMOUNT = "replaceAmount";
    public static final String REPLACE_DESCRIPTION = "replaceDescription";
    public static final String REPLACE_MEMO = "replaceMemo";
    public static final String REPLACE_TAGS = "replaceTags";


    ///////////////////////////////////////////////////////////////////////////////////////////////
    // HTML
    ///////////////////////////////////////////////////////////////////////////////////////////////
    public static final String HTML_BEGIN = "<html>";
    public static final String HTML_END = "</html>";
    public static final String PARA_BEGIN = "<p>";
    public static final String PARA_END = "</p>";
    public static final String LINE_END = "<br/>";
    public static final String BOLD_BEGIN = "<b>";
    public static final String BOLD_END = "</b>";
    public static final String COLOR_BEGIN_FMT = "<font style=\"color: #{0};\">";
    public static final String COLOR_END = "</font>";
    public static final String TABLE_BEGIN = "<table style=\"border-spacing: 0px\">";
    public static final String TABLE_END = "</table>";
    public static final String ROW_BEGIN = "<tr>";
    public static final String ROW_END = "</tr>";
    public static final String COL_BEGIN = "<td style=\"padding: 0px\">";
    public static final String COL_BEGIN_RIGHT = "<td style=\"text-align: right; padding: 0px\">";
    public static final String COL_END = "</td>";
    public static final String NBSPACE = "&nbsp;";


    ///////////////////////////////////////////////////////////////////////////////////////////////
    // XML Resource Files 
    ///////////////////////////////////////////////////////////////////////////////////////////////
    static final String FORMAT_XML_SUFFIX = "properties.xml";
    static final String FORMAT_XML = "java." + FORMAT_XML_SUFFIX;

    ///////////////////////////////////////////////////////////////////////////////////////////////
    // Logging and Errors
    ///////////////////////////////////////////////////////////////////////////////////////////////
    public static final String UNKNOWN_TRANSACTION = "Unknown transaction type";
    static final String ERROR_LOADING = "Error loading Find and Replace Plugin";
    static final String ERROR_TITLE = "Find and Replace";
    static final String ESCAPE_KEY = "ESCAPE";
    static final String COLON = ":";
    static final String XML_RESOURCE_LOAD_FAIL = "Unable to load an XML resource bundle: ";


    /**
     * Do not instantiate, static properties only
     */
    private N12EFindAndReplace()
    {
    }
}

/*************************************************************************\
* Copyright (C) 2009-2011 Mennē Software Solutions, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.model.AbstractTxn;
import com.moneydance.apps.md.model.ParentTxn;
import com.moneydance.apps.md.model.SplitTxn;
import com.moneydance.apps.md.model.Account;
import com.moneydance.apps.md.model.TxnTag;
import com.moneydance.apps.md.model.TxnTagSet;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;

import javax.swing.JComponent;
import javax.swing.JPanel;
import javax.swing.KeyStroke;
import javax.swing.UIManager;
import java.awt.Color;
import java.awt.Component;
import java.awt.Container;
import java.awt.Point;
import java.awt.Toolkit;
import java.awt.event.FocusListener;
import java.awt.event.InputEvent;
import java.awt.event.KeyEvent;
import java.text.MessageFormat;
import java.util.regex.Pattern;

/**
 * <p>Utility methods for extracting information from transactions. Many of these could be useful
 * in other plugins.</p>
 *
 * @author Kevin Menningen
 * @version 1.60
 * @since 1.0
 */
final class FarUtil
{
    private static Account getTransactionAccount(final AbstractTxn txn)
    {
        final Account result;
        if (txn instanceof SplitTxn)
        {
            result = txn.getParentTxn().getAccount();
        }
        else
        {
            result = txn.getAccount();
        }
        return result;
    }

    static String getTransactionAccountName(final AbstractTxn txn)
    {
        return getTransactionAccount(txn).getAccountName();
    }

    static int getTransactionDate(final AbstractTxn txn)
    {
        final ParentTxn dateTxn;
        if (txn instanceof ParentTxn)
        {
            dateTxn = (ParentTxn)txn;
        }
        else if (txn instanceof SplitTxn)
        {
            dateTxn = txn.getParentTxn();
        }
        else
        {
            return -1;
        }

        return dateTxn.getDateInt(); // YYYYMMDD
    }

    static Account getTransactionCategory(final AbstractTxn txn)
    {
        if (txn instanceof SplitTxn)
        {
            return txn.getAccount();
        }
        else if (txn instanceof ParentTxn)
        {
            // for the parent, check if we have only 1 split. If we do, use that. If we have more,
            // show the words '- N splits -'
            final ParentTxn parent = (ParentTxn)txn;
            int numSplits = parent.getSplitCount();
            if (numSplits == 1)
            {
                return parent.getSplit(0).getAccount();
            }
        }

        // multiple splits or some other type of transaction
        return null;
    }

    static String getTransactionMemo(final AbstractTxn txn)
    {
        final String memo;
        if (txn instanceof ParentTxn)
        {
            memo = ((ParentTxn)txn).getMemo();
        }
        else if (txn instanceof SplitTxn)
        {
            memo = txn.getParentTxn().getMemo();
        }
        else
        {
            memo = null;
        }
        return memo;
    }

    static String getTransactionCheckNo(final AbstractTxn txn)
    {
        final String memo;
        if (txn instanceof ParentTxn)
        {
            memo = txn.getCheckNumber();
        }
        else if (txn instanceof SplitTxn)
        {
            memo = txn.getParentTxn().getCheckNumber();
        }
        else
        {
            memo = null;
        }
        return memo;
    }

    static TxnTag[] getTransactionTags(final AbstractTxn txn, final TxnTagSet tagSet)
    {
        // user tags are associated with splits only
        final SplitTxn split;
        if (txn instanceof SplitTxn)
        {
            split = (SplitTxn)txn;
        }
        else if ((txn instanceof ParentTxn) && (((ParentTxn)txn).getSplitCount() == 1))
        {
            // get the first split only
            split = ((ParentTxn)txn).getSplit(0);
        }
        else
        {
            // no tags associated with parent transactions with more than one split
            return new TxnTag[0];
        }

        if (tagSet == null)
        {
            // enforce the use of the API method
            return new TxnTag[0];
        }

        return tagSet.getTagsForTxn(split);
    }

    static boolean hasRegularExpression(final String freeTextSearch)
    {
        return ((freeTextSearch != null) && (freeTextSearch.length() > 1)
                && freeTextSearch.startsWith("=")
                && !freeTextSearch.startsWith("=="));
    }

    /**
     * Return the portion of the regular expression after the leading '='.
     * @param freeTextSearch Text entered by the user.
     * @return A regular expression string ready for Pattern and Matcher.
     */
    static String createRegularExpression(final String freeTextSearch)
    {
        if (!hasRegularExpression(freeTextSearch))
        {
            return N12EFindAndReplace.EMPTY;
        }
        return freeTextSearch.substring(1, freeTextSearch.length());
    }

    /**
     * Get a label from resources, and if it does not have a colon, add it.
     * @param resources Resource provider.
     * @param key String key to look up in the resources
     * @return A string with a colon at the end.
     */
    static String getLabelText(final IResourceProvider resources, final String key)
    {
        StringBuilder label = new StringBuilder(resources.getString(key));
        if ((label.length() > 0) &&
                (label.charAt(label.length() - 1)) != N12EFindAndReplace.COLON.charAt(0))
        {
            label.append(resources.getString(L10NFindAndReplace.LABEL_COLON));
        }
        return label.toString();
    }

    public static Point pointFromSettingsString(final String settings)
    {
        if (settings == null)
        {
            return null;
        }
        String[] values = settings.split(N12EFindAndReplace.SETTINGS_PT_DELIMITER);
        if (values.length == 2)
        {
            return new Point(Integer.parseInt(values[0]), Integer.parseInt(values[1]));
        }
        return null;
    }

    public static String settingsStringFromPoint(final Point point)
    {
        final StringBuilder result = new StringBuilder(Integer.toString(point.x));
        result.append(N12EFindAndReplace.SETTINGS_PT_DELIMITER);
        result.append(Integer.toString(point.y));
        return result.toString();
    }

    static void recurseAddFocusListener(final Container root, final FocusListener listener)
    {
        for (Component child : root.getComponents())
        {
            if (child instanceof JPanel)
            {
                recurseAddFocusListener((Container)child, listener);
            }
            if (child.isFocusable())
            {
                // setup a focus traversal policy
                child.addFocusListener(listener);
            }
        }
    }

    static String stripHtmlPrefixSuffix(final String source)
    {
        String stripped = source;
        int startIndex = source.indexOf(N12EFindAndReplace.HTML_BEGIN);
        if (startIndex >= 0)
        {
            startIndex += N12EFindAndReplace.HTML_BEGIN.length();
        }
        else
        {
            startIndex = 0;
        }
        int endIndex = source.lastIndexOf(N12EFindAndReplace.HTML_END);
        if (endIndex < 0)
        {
            endIndex = source.length();
        }
        if (startIndex < endIndex)
        {
            stripped = source.substring(startIndex, endIndex);
        }
        return stripped;
    }

    static String getKeyHtmlDisplayText(final KeyStroke key, boolean makeSmaller)
    {
        if (key == null)
        {
            return "";
        }
        final String format;
        if (makeSmaller)
        {
            format = N12EFindAndReplace.KEY_DISPLAY_SMALLER_FMT;
        }
        else
        {
            format = N12EFindAndReplace.KEY_DISPLAY_FMT;
        }
        String color = getAcceleratorColorText();
        String display = getAcceleratorText(key);
        return MessageFormat.format(format, color, display);
    }

    static String getAcceleratorColorText()
    {
        Color color = UIManager.getColor("MenuItem.acceleratorForeground");
        if (color == null)
        {
            color = Color.GRAY;
        }
        return Integer.toHexString( color.getRGB() & 0x00ffffff );
    }

    public static String getAcceleratorText(KeyStroke accelerator)
    {
        String acceleratorDelimiter = UIManager.getString("MenuItem.acceleratorDelimiter");
        if (acceleratorDelimiter == null)
        {
            if (MoneydanceGUI.isMac)
            {
                acceleratorDelimiter = "";
            }
            else
            {
                acceleratorDelimiter = "+";
            }
        }

        StringBuilder result = new StringBuilder();
        if (accelerator != null)
        {
            int modifiers = accelerator.getModifiers();
            if (modifiers > 0)
            {
                if (MoneydanceGUI.isMac)
                {
                    result.append(getMacKeyModifiersText(modifiers));
                }
                else
                {
                    result.append(KeyEvent.getKeyModifiersText(modifiers));
                }
                result.append( acceleratorDelimiter );
            }

            int keyCode = accelerator.getKeyCode();
            if (keyCode != 0)
            {
                result.append(KeyEvent.getKeyText(keyCode));
            }
            else
            {
                result.append(String.valueOf(accelerator.getKeyChar()));
            }
        }
        return result.toString();
    }

    /**
     * Based on {@link java.awt.event.KeyEvent#getKeyModifiersText(int)}, this returns the key
     * modifier text in a format more consistent with the Mac look-and-feel.
     *
     * @param modifiers Any key modifiers that need to be converted to a string.
     * @return string a text description of the combination of modifier
     *                keys that were held down during the event
     * @see InputEvent#getModifiersExText(int)
     */
    static String getMacKeyModifiersText(int modifiers) {
        StringBuilder buf = new StringBuilder();
        if ((modifiers & InputEvent.ALT_GRAPH_MASK) != 0) {
            buf.append(Toolkit.getProperty("AWT.altGraph", "Alt Graph"));
        }
        // Control key
        if ((modifiers & InputEvent.CTRL_MASK) != 0) {
            buf.append(Toolkit.getProperty("AWT.control", "Ctrl"));
        }
        // Option key
        if ((modifiers & InputEvent.ALT_MASK) != 0) {
            buf.append(Toolkit.getProperty("AWT.alt", "Alt"));
        }
        // Shift key
        if ((modifiers & InputEvent.SHIFT_MASK) != 0) {
            buf.append(Toolkit.getProperty("AWT.shift", "Shift"));
        }
        // Command key
        if ((modifiers & InputEvent.META_MASK) != 0) {
            buf.append(Toolkit.getProperty("AWT.meta", "Meta"));
        }
        if ((modifiers & InputEvent.BUTTON1_MASK) != 0) {
            buf.append(Toolkit.getProperty("AWT.button1", "Button1"));
        }
        return buf.toString();
    }


    static String getKeystrokeTextFromMnemonic(String mnemonic, boolean addShift)
    {
        StringBuilder keyCode = new StringBuilder();
        if ((mnemonic != null) && (mnemonic.length() > 0))
        {
            if (addShift) keyCode.append("shift ");
            if (MoneydanceGUI.ACCELERATOR_MASK == InputEvent.CTRL_MASK)
            {
                keyCode.append("control ");
            }
            else
            {
                // Mac
                keyCode.append("meta ");
            }
            keyCode.append(mnemonic.charAt(0));
        }
        return keyCode.toString();
    }

    static void addKeyToToolTip(JComponent button, KeyStroke key)
    {
        String toolTip = button.getToolTipText();
        if ((toolTip != null) && (toolTip.length() > 0))
        {
            StringBuilder sb = new StringBuilder(N12EFindAndReplace.HTML_BEGIN);
            sb.append( stripHtmlPrefixSuffix(toolTip) );
            sb.append( getKeyHtmlDisplayText(key, true) );
            sb.append(N12EFindAndReplace.HTML_END);
            button.setToolTipText(sb.toString());
        }
        else if (key != null)
        {
            StringBuilder sb = new StringBuilder(N12EFindAndReplace.HTML_BEGIN);
            sb.append( getKeyHtmlDisplayText(key, false) );
            sb.append(N12EFindAndReplace.HTML_END);
            button.setToolTipText(sb.toString());
        }
    }

    static Pattern buildFindPattern(String textMatch)
    {
        // build the regular expression pattern to search with
        if (hasRegularExpression(textMatch))
        {
            String regex = createRegularExpression(textMatch);
            return Pattern.compile(regex);
        }
        else
        {
            final StringBuilder buffer = new StringBuilder(N12EFindAndReplace.REGEX_PREFIX);
            buffer.append(textMatch);
            buffer.append(N12EFindAndReplace.REGEX_SUFFIX);
            return Pattern.compile(buffer.toString());
        }
    }


    /**
     * Static utilities, do not instantiate.
     */
    private FarUtil()
    {
    }
}

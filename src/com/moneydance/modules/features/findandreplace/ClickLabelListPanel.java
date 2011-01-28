/*************************************************************************\
* Copyright (C) 2009-2011 Mennē Software Solutions, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.findandreplace;

import info.clearthought.layout.TableLayout;
import info.clearthought.layout.TableLayoutConstraints;

import javax.swing.BorderFactory;
import javax.swing.JLabel;
import javax.swing.JPanel;
import java.awt.Dimension;
import java.util.ArrayList;
import java.util.List;

/**
 * A control that contains a list of clickable labels, with the caller providing the runnable that
 * fires when the label is clicked.
 *
 * @author Kevin Menningen
 * @version 1.50
 * @since 1.3
 */
class ClickLabelListPanel extends JPanel
{
    /** The list of labels displayed. */
    private final List<LabelListItem> _labels;

    /**
     * Constructor to allow all fields to be final.
     */
    public ClickLabelListPanel()
    {
        // preserve the order in which items were added
        _labels = new ArrayList<LabelListItem>();
        // give a border left and right for margin
        setBorder(BorderFactory.createEmptyBorder(0, UiUtil.HGAP*2, 0, UiUtil.HGAP*2));
    }

    /**
     * Add a new label to the list.
     * @param text   The text to show, can include HTML.
     * @param action The action to run when the label is clicked.
     * @return The individual label control for this item.
     */
    public JLabel addLabel(final String text, final Runnable action)
    {
        final LabelListItem listItem = new LabelListItem(text, action);
        _labels.add(listItem);
        return listItem.control;
    }

    /**
     * Setup the spacing and attributes of the controls.
     */
    public void layoutUI()
    {
        // in case this is run multiple times, rebuild the child component list.
        removeAll();
        if (_labels.isEmpty())
        {
            return;
        }

        // We're going to build a special table layout size list that contains the minimum
        // component size, accounting for boldface fonts so that the line doesn't 'wiggle' when
        // you mouse over it. In between each label is a gap for a more pleasant horizontal spacing.
        final int columnCount = _labels.size() * 2 - 1;
        double[][] sizes = new double[2][];

        // columns first
        sizes[0] = new double[columnCount];
        for (int index = 0; index < columnCount; index += 2)
        {
            sizes[0][index] = TableLayout.PREFERRED;
            if (index < (columnCount - 1))
            {
                sizes[0][index + 1] = UiUtil.HGAP*2;
            }
        }

        // then rows - there is only one row of labels allowed
        sizes[1] = new double[] { TableLayout.PREFERRED };

        // calculate sizes and setup the labels
        final JLabel[] labels = new JLabel[_labels.size()];
        int index = 0;
        for (LabelListItem item : _labels)
        {
            final JLabel label = item.control;
            labels[index] = label;

            label.setHorizontalAlignment(JLabel.CENTER);

            // Here we override the preferred size, which does not account for boldface fonts, so
            // that the line doesn't 'wiggle' when you mouse over it. Because TableLayout allows
            // for fixed length cells, we simply replace the 'preferred' flag with a large enough
            // cell width to accomodate the bold font.
            Dimension textSize = labels[index].getPreferredSize();
            // add one pixel per displayed character due to bold text thickness
            sizes[0][index*2] = textSize.width + getCharCount(item.text);

            index++;
        }

        // lay them out in fixed size bins so the line doesn't wiggle horizontally
        setLayout(new TableLayout(sizes));
        for (index = 0; index < labels.length; index++ )
        {
            add(labels[index], new TableLayoutConstraints(index*2, 0, index*2, 0,
                                                  TableLayoutConstraints.LEFT,
                                                  TableLayoutConstraints.TOP));
        }

        validate();
    }

    @Override
    public void setEnabled(boolean enabled)
    {
        super.setEnabled(enabled);
        for (final LabelListItem label : _labels)
        {
            label.control.setEnabled(enabled);
        }
    }

    ///////////////////////////////////////////////////////////////////////////////////////////////
    // Private Methods
    ///////////////////////////////////////////////////////////////////////////////////////////////

    /**
     * Determine the number of non-HTML characters in a string. To count HTML, the string has to
     * begin with '&lt;html&gt;', in lower case. This method skips all characters inside tags and
     * shows only the text that will be displayed.
     *
     * @param text The string to count.
     * @return The number of
     */
    private int getCharCount(final String text)
    {
        if ((text == null) || (text.length() == 0))
        {
            return 0;
        }
        if (!text.startsWith(N12EFindAndReplace.HTML_BEGIN))
        {
            return text.length();
        }
        int count = 0;
        int tagLevel = 0;
        for (int index = 0; index < text.length(); index++)
        {
            char current = text.charAt(index);
            if (current == '<')
            {
                ++tagLevel;
            }
            else if (current == '>')
            {
                --tagLevel;
            }
            else
            {
                if (tagLevel == 0)
                {
                    ++count;
                }
            }
        }
        return count;
    }


    //////////////////////////////////////////////////////////////////////////////////////////////
    //  Inner Classes
    //////////////////////////////////////////////////////////////////////////////////////////////

    private class LabelListItem
    {
        private final String text;
        private final JLabel control;

        LabelListItem(final String labelText, final Runnable labelAction)
        {
            text = labelText;
            control = new ClickLabelWithDisabledHtml(labelText, labelAction);
        }
    }

}

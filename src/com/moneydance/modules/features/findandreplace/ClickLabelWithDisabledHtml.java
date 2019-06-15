/*************************************************************************\
* Copyright (C) 2009-2011 Mennē Software Solutions, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.view.gui.MDColors;

import javax.swing.JLabel;
import javax.swing.SwingUtilities;
import javax.swing.UIManager;
import java.awt.Color;
import java.awt.Cursor;
import java.awt.Font;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;

/**
 * This class represents a label that can be clicked on. It is colored blue when enabled and will
 * show a hand cursor as well as a boldface font when hovered over.
 * <p/>
 * By default an HTML label will not render as disabled correctly. Since HTML uses the
 * foreground color, we just put in the correct foreground color when disabled.
 *
 * @author Kevin Menningen
 * @version 1.50
 * @since 1.3
 */
class ClickLabelWithDisabledHtml extends JLabel
{
    /** True if it has an action, false if just a normal label. */
    private final boolean _hasAction;

    public ClickLabelWithDisabledHtml(final String htmlText, final Runnable action)
    {
        super(htmlText);
        _hasAction = (action != null);
        setupAction(action);
    }

    @Override
    public void setEnabled(boolean enabled) {
        super.setEnabled(enabled);
        if (enabled) {
            if (_hasAction) {
                setForeground(MDColors.getSingleton().defaultTextForeground);
            } else {
                setForeground(UIManager.getColor("Label.foreground"));
            }
        } else {
            setForeground(UIManager.getColor("Label.disabledForeground"));
        }
    }


    ///////////////////////////////////////////////////////////////////////////////////////////////
    // Private Methods
    ///////////////////////////////////////////////////////////////////////////////////////////////

    private void setupAction(final Runnable action)
    {
        if (action == null)
        {
            // this is not a clickable label, just act as a normal label
            return;
        }

        // by default it is enabled
        setForeground(MDColors.getSingleton().defaultTextForeground);

        final Font normFont = getFont();
        final Font boldFont = normFont.deriveFont(Font.BOLD);
        addMouseListener(new MouseAdapter()
        {
            @Override
            public void mouseClicked(MouseEvent event)
            {
                if (SwingUtilities.isLeftMouseButton(event) && isEnabled())
                {
                    action.run();
                }
            }

            @Override
            public void mouseEntered(MouseEvent event)
            {
                if (isEnabled())
                {
                    setFont(boldFont);
                    setCursor(new Cursor(Cursor.HAND_CURSOR));
                }
            }

            @Override
            public void mouseExited(MouseEvent event)
            {
                if (isEnabled())
                {
                    setFont(normFont);
                    setCursor(new Cursor(Cursor.DEFAULT_CURSOR));
                }
            }
        });
    } // setupAction()
}

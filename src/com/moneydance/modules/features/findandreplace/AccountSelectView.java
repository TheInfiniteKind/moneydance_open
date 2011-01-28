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

import javax.swing.JPanel;
import javax.swing.JList;
import javax.swing.JButton;
import javax.swing.JLabel;
import javax.swing.JScrollPane;
import javax.swing.SwingUtilities;
import javax.swing.JOptionPane;
import java.beans.PropertyChangeListener;
import java.beans.PropertyChangeEvent;
import java.awt.Font;
import java.awt.event.ActionListener;
import java.awt.event.ActionEvent;

/**
 * <p>The view for the account/category selection dialog.</p>
 *  
 * @author Kevin Menningen
 * @version 1.50
 * @since 1.0
 */
class AccountSelectView extends JPanel implements PropertyChangeListener
{
    private final AccountSelectModel _model;
    private AccountSelectController _controller;
    private IResourceProvider _resources;

    private JList _excludedList;
    private JScrollPane _candidateHost;
    private JList _includedList;
    private JScrollPane _includedHost;

    public AccountSelectView(final AccountSelectModel model)
    {
        _model = model;
    }


    /**
     * This method gets called when a bound property is changed.
     *
     * @param event A PropertyChangeEvent object describing the event source
     *            and the property that has changed.
     */

    public void propertyChange(final PropertyChangeEvent event)
    {
        refresh();
    }

    private void refresh()
    {
        final Runnable repaintRunner = new Runnable()
        {
            /**
             * Run on a specific thread, possibly not the current one.
             * @see Thread#run()
             */
            public void run()
            {
                _candidateHost.repaint();
                _includedHost.repaint();
                repaint();
            }
        };
        if (!SwingUtilities.isEventDispatchThread())
        {
            SwingUtilities.invokeLater(repaintRunner);
        }
        else
        {
            repaintRunner.run();
        }
    }

    void layoutUI()
    {
        final double[][] sizes = new double[][]
        {
            // columns
            {
                UiUtil.HGAP, // gap
                TableLayout.FILL, // accounts to include
                UiUtil.HGAP, // gap
                TableLayout.PREFERRED, // buttons
                UiUtil.HGAP, // gap
                TableLayout.FILL, // accounts already included
                UiUtil.HGAP // gap
            },

            // rows
            { UiUtil.VGAP, TableLayout.PREFERRED, UiUtil.VGAP / 2, TableLayout.FILL, UiUtil.VGAP  }
        };
        setLayout(new TableLayout(sizes));

        JLabel label = new JLabel(_resources.getString(L10NFindAndReplace.ACCOUNTSELECT_EXCLUDE));
        final Font boldFont = label.getFont().deriveFont(Font.BOLD);
        label.setFont(boldFont);
        add(label, new TableLayoutConstraints(1, 1));

        label = new JLabel(_resources.getString(L10NFindAndReplace.ACCOUNTSELECT_INCLUDE));
        label.setFont(boldFont);
        add(label, new TableLayoutConstraints(5, 1));

        _excludedList = new JList(_model.getCandidateList());

        // setting the preferred size will limit the list display - don't do it
//        _candidateList.setPreferredSize(new Dimension(200, 400));
        _excludedList.setVisibleRowCount(20);
        _candidateHost = new JScrollPane(_excludedList, JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED,
                JScrollPane.HORIZONTAL_SCROLLBAR_NEVER);
        add(_candidateHost, new TableLayoutConstraints(1,3));

        _includedList = new JList(_model.getIncludedList());
//        _includedList.setPreferredSize(new Dimension(200, 400));
        _includedList.setVisibleRowCount(20);
        _includedHost = new JScrollPane(_includedList, JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED,
                JScrollPane.HORIZONTAL_SCROLLBAR_NEVER);
        add(_includedHost, new TableLayoutConstraints(5,3));

        add(buildButtonPanel(), new TableLayoutConstraints(3, 3));
    }


    ///////////////////////////////////////////////////////////////////////////////////////////////
    // Private Methods
    ///////////////////////////////////////////////////////////////////////////////////////////////

    private JPanel buildButtonPanel()
    {
        final double[][] sizes = new double[][]
        {
            // columns
            { TableLayout.PREFERRED },

            // rows
            {
                TableLayout.FILL, UiUtil.VGAP,
                TableLayout.PREFERRED, UiUtil.VGAP,     // add
                TableLayout.PREFERRED, UiUtil.VGAP,     // add except
                TableLayout.PREFERRED, UiUtil.VGAP * 3, // add all
                TableLayout.PREFERRED, UiUtil.VGAP,     // remove
                TableLayout.PREFERRED, UiUtil.VGAP,     // remove except
                TableLayout.PREFERRED, UiUtil.VGAP,     // remove all
                TableLayout.FILL
            }
        };
        final JPanel panel = new JPanel(new TableLayout(sizes));

        final JButton addButton = new JButton(_resources.getString(L10NFindAndReplace.ACCOUNTSELECT_ADD));
        addButton.addActionListener(new ActionListener()
        {
            public void actionPerformed(final ActionEvent event)
            {
                final int[] indices = _excludedList.getSelectedIndices();
                try
                {
                    _controller.moveToIncluded(indices);
                }
                catch (Exception error)
                {
                    handleException(error);
                }
                clearSelections();
            }
        });
        panel.add(addButton, new TableLayoutConstraints(0, 2));

        final JButton addExceptButton = new JButton(_resources.getString(L10NFindAndReplace.ACCOUNTSELECT_ADDEXCEPT));
        addExceptButton.addActionListener(new ActionListener()
        {
            public void actionPerformed(final ActionEvent event)
            {
                final int[] indices = _excludedList.getSelectedIndices();
                try
                {
                    _controller.includeExcept(indices);
                }
                catch (Exception error)
                {
                    handleException(error);
                }
                clearSelections();
            }
        });
        panel.add(addExceptButton, new TableLayoutConstraints(0, 4));

        final JButton addAllButton = new JButton(_resources.getString(L10NFindAndReplace.ACCOUNTSELECT_ADDALL));
        addAllButton.addActionListener(new ActionListener()
        {
            public void actionPerformed(final ActionEvent event)
            {
                try
                {
                    _controller.includeAll();
                }
                catch (Exception error)
                {
                    handleException(error);
                }
                clearSelections();
            }
        });
        panel.add(addAllButton, new TableLayoutConstraints(0, 6));

        final JButton removeButton = new JButton(_resources.getString(L10NFindAndReplace.ACCOUNTSELECT_REMOVE));
        removeButton.addActionListener(new ActionListener()
        {
            public void actionPerformed(final ActionEvent event)
            {
                final int[] indices = _includedList.getSelectedIndices();
                try
                {
                    _controller.moveToExcluded(indices);
                }
                catch (Exception error)
                {
                    handleException(error);
                }

                clearSelections();
            }
        });
        panel.add(removeButton, new TableLayoutConstraints(0, 8));

        final JButton removeExceptButton = new JButton(_resources.getString(L10NFindAndReplace.ACCOUNTSELECT_REMOVEEXCEPT));
        removeExceptButton.addActionListener(new ActionListener()
        {
            public void actionPerformed(final ActionEvent event)
            {
                final int[] indices = _includedList.getSelectedIndices();
                try
                {
                    _controller.excludeExcept(indices);
                }
                catch (Exception error)
                {
                    handleException(error);
                }

                clearSelections();
            }
        });
        panel.add(removeExceptButton, new TableLayoutConstraints(0, 10));

        final JButton removeAllButton = new JButton(_resources.getString(L10NFindAndReplace.ACCOUNTSELECT_REMOVEALL));
        removeAllButton.addActionListener(new ActionListener()
        {
            public void actionPerformed(final ActionEvent event)
            {
                try
                {
                    _controller.excludeAll();
                }
                catch (Exception error)
                {
                    handleException(error);
                }

                clearSelections();
            }
        });
        panel.add(removeAllButton, new TableLayoutConstraints(0, 12));

        return panel;
    } // buildButtonPanel()

    private void clearSelections()
    {
        _excludedList.clearSelection();
        _includedList.clearSelection();
    }

    public void handleException(Exception error)
    {
        final String title = _resources.getString(L10NFindAndReplace.ERROR_TITLE);
        final String message = error.getLocalizedMessage();
        JOptionPane.showMessageDialog(this, message, title, JOptionPane.ERROR_MESSAGE);
    }

    void setController(final AccountSelectController controller)
    {
        _controller = controller;
        _resources = controller;
    }
}

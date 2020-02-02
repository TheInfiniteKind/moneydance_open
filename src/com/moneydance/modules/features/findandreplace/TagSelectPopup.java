/*************************************************************************\
* Copyright (C) 2015 Mennē Software Solutions, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.view.gui.MoneydanceGUI;

import javax.swing.AbstractAction;
import javax.swing.Box;
import javax.swing.DefaultListCellRenderer;
import javax.swing.JComponent;
import javax.swing.JDialog;
import javax.swing.JLabel;
import javax.swing.JList;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.KeyStroke;
import javax.swing.ListSelectionModel;
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.ListSelectionListener;
import java.awt.BorderLayout;
import java.awt.Component;
import java.awt.Dialog;
import java.awt.Window;
import java.awt.event.ActionEvent;
import java.awt.event.KeyEvent;

/**
 * This undecorated dialog shows all the possible tags in a scrolling list, and colors the currently
 * selected tags a different background color. Clicking on an uncolored tag will select it, clicking
 * on a colored tag will deselect it.
 */
public class TagSelectPopup extends JDialog {
  
  private MoneydanceGUI mdGUI;
  
    public TagSelectPopup(Window owner, final TxnTagsPicker picker, MoneydanceGUI mdGUI) {
        super(owner, Dialog.ModalityType.APPLICATION_MODAL);
        this.mdGUI = mdGUI;
        setUndecorated(true);
        
        JPanel mainPanel = new JPanel(new BorderLayout());
        final JList<String> tagsList = createList(picker);
        JScrollPane scrollPane = new JScrollPane(tagsList,
                                                 JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED,
                                                 JScrollPane.HORIZONTAL_SCROLLBAR_NEVER);
        mainPanel.add(scrollPane, BorderLayout.CENTER);

        int height = Math.max(200, (int) Math.round(owner.getHeight() * .4));
        mainPanel.add(Box.createVerticalStrut(height), BorderLayout.WEST);

        setContentPane(mainPanel);
        pack();
        setLocationRelativeTo(picker.getView());
        setupKeyboard();
    }

    private JList<String> createList(TxnTagsPicker picker)
    {
        JList<String> tagsList = new JList<>(picker.getFullTagsList());

        // make sure a click will pick the tag and add it to the list in the picker (if not there)
        tagsList.getSelectionModel().setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
        tagsList.addListSelectionListener(new TagsListSelectionListener(tagsList, picker));
        tagsList.setCellRenderer(new TagListCellRenderer(picker));
        return tagsList;
    }

    private void setupKeyboard()
    {
        // make sure Escape key will dismiss the dialog
        final AbstractAction closeAction = new AbstractAction("Close")
        {
            public void actionPerformed(ActionEvent evt)
            {
                setVisible(false);
            }
        };
        getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).
                put(KeyStroke.getKeyStroke(KeyEvent.VK_W, MoneydanceGUI.ACCELERATOR_MASK),
                    "close_window");
        getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).
                put(KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0),
                    "close_window");
        getRootPane().getActionMap().put("close_window", closeAction);
    }

    private class TagListCellRenderer extends DefaultListCellRenderer
    {
        final TxnTagsPicker _picker;

        private TagListCellRenderer(final TxnTagsPicker picker)
        {
            _picker = picker;
        }

        @Override
        public Component getListCellRendererComponent(JList<?> list, Object value, int index, boolean isSelected, boolean cellHasFocus)
        {
            JLabel result = (JLabel) super.getListCellRendererComponent(list, value, index, isSelected, cellHasFocus);
            String tag = (String) value;
            if (_picker.isTagSelected(tag)) {
              result.setBackground(mdGUI.getColors().listSelectionBG);
            } else {
              result.setBackground(mdGUI.getColors().listBackground);
            }
            return result;
        }

    }

    private class TagsListSelectionListener implements ListSelectionListener
    {
        private final JList<String> tagsList;
        private final TxnTagsPicker picker;

        public TagsListSelectionListener(JList<String> tagsList, TxnTagsPicker picker)
        {
            this.tagsList = tagsList;
            this.picker = picker;
        }

        public void valueChanged(ListSelectionEvent event)
        {
            if (event.getValueIsAdjusting()) return;
            int index = event.getFirstIndex();
            if (index < 0) return;
            String selected = tagsList.getModel().getElementAt(index);

            // either add or remove the tag
            picker.toggle(selected);
            TagSelectPopup.this.setVisible(false);
        }
    }
}

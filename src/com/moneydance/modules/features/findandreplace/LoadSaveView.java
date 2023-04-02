/*************************************************************************\
 * Copyright (C) 2012-2013 Mennē Software Solutions, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
 \*************************************************************************/
package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.view.gui.MDAction;
import com.moneydance.apps.md.view.gui.MDImages;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.moneydance.awt.GridC;

import javax.swing.BorderFactory;
import javax.swing.Box;
import javax.swing.ImageIcon;
import javax.swing.JComponent;
import javax.swing.JLabel;
import javax.swing.JList;
import javax.swing.JMenu;
import javax.swing.JMenuItem;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JPopupMenu;
import javax.swing.JScrollPane;
import javax.swing.JTextField;
import javax.swing.ListSelectionModel;
import javax.swing.SwingUtilities;
import javax.swing.UIManager;
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.ListSelectionListener;
import java.awt.BorderLayout;
import java.awt.Component;
import java.awt.GridBagLayout;
import java.awt.Image;
import java.awt.Rectangle;
import java.awt.Window;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.HierarchyEvent;
import java.awt.event.HierarchyListener;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.util.Collection;
import java.util.Vector;

/**
 * <p>View (menu and a dialog) for loading and saving find and replace parameters.</p>
 *
 * @author Kevin Menningen
 * @version Build 94
 * @since Build 83
 */
public class LoadSaveView extends JPanel
{
    private final LoadSaveModel _model;
    private JLabel _loadSaveLabel;

    LoadSaveView(final MoneydanceGUI mdGui, final FarController controller)
    {
        _model = new LoadSaveModel(mdGui.getCurrentBook(), controller);
        createControls(mdGui, controller);
    }
    
    private void createControls(final MoneydanceGUI mdGui, final IResourceProvider resources) 
    {
        setLayout(new BorderLayout());
        setOpaque(false);
        String prompt = getCurrentSearchName(mdGui);
        _loadSaveLabel = new JLabel(prompt);
        _loadSaveLabel.setOpaque(false);

        Image image = mdGui.getImage(MDImages.SELECTOR_SMALL);
        ImageIcon icon = new ImageIcon(image);
        _loadSaveLabel.setIcon(icon);
        final JComponent loadParent = _loadSaveLabel;
        _loadSaveLabel.addMouseListener(new MouseAdapter()
        {
            @Override
            public void mouseReleased(MouseEvent e)
            {
                showSavedSearchMenu(loadParent, mdGui, resources);
            }
        });
        add(_loadSaveLabel, BorderLayout.CENTER);
    }

    private String getCurrentSearchName(final MoneydanceGUI mdGui)
    {
        String currentSave = _model.getCurrentSearchName();
        if (FarUtil.isBlank(currentSave))
        {
            return mdGui.getStr("Memorized") + "...";
        }
        return currentSave;
    }

    private void showSavedSearchMenu(final JComponent menuParent, final MoneydanceGUI mdGui, final IResourceProvider resources)
    {
        final JPopupMenu popupMenu = new JPopupMenu();

        // build the indices in exactly the same order as in the model
        final Collection<String> savedSearches = _model.getSavedSearchNames();
        for (final String searchName : savedSearches)
        {
            final JMenu item = new JMenu(searchName);
            item.addMouseListener(new MouseAdapter()
            {
                @Override
                public void mouseClicked(MouseEvent e)
                {
                    popupMenu.setVisible(false);
                    loadSavedSearch(searchName, mdGui);
                }
            });
            MDAction loadAction = new MDAction(null, resources.getString(L10NFindAndReplace.LOAD), new ActionListener()
            {
                public void actionPerformed(ActionEvent e)
                {
                    loadSavedSearch(searchName, mdGui);
                }
            });
            item.add(loadAction);
            MDAction updateAction = new MDAction(mdGui, "update", new ActionListener()
            {
                public void actionPerformed(ActionEvent e)
                {
                    saveSearchSettings(searchName, mdGui);
                }
            });
            item.add(updateAction);
            item.addSeparator();
            MDAction deleteAction = new MDAction(mdGui, "delete", new ActionListener()
            {
                public void actionPerformed(ActionEvent e)
                {
                    deleteSavedSearch(searchName, mdGui);
                }
            });
            item.add(deleteAction);
            popupMenu.add(item);
        }
        // tack on the save current
        if (popupMenu.getComponentCount() > 0)
        {
            popupMenu.addSeparator();
        }
        MDAction saveAction = new MDAction(mdGui, "save_as...", new ActionListener()
        {
            public void actionPerformed(ActionEvent e)
            {
                saveCurrentSearch(mdGui, resources);
            }
        });
        popupMenu.add(new JMenuItem(saveAction));
        Rectangle bounds = menuParent.getBounds();
        popupMenu.show(menuParent, 0, (int) bounds.getHeight());
    }

    private void saveCurrentSearch(final MoneydanceGUI mdGUI, final IResourceProvider resources)
    {
        final JTextField nameField = new JTextField();
        JPanel p = buildSaveAsPanel(resources, nameField);
        // Requests focus on the field component.
        nameField.addHierarchyListener(new HierarchyListener()
        {
            public void hierarchyChanged(HierarchyEvent e)
            {
                final Component c = e.getComponent();
                if (c.isShowing() && (e.getChangeFlags() & HierarchyEvent.SHOWING_CHANGED) != 0)
                {
                    Window toplevel = SwingUtilities.getWindowAncestor(c);
                    toplevel.addWindowFocusListener(new WindowAdapter()
                    {
                        public void windowGainedFocus(WindowEvent e)
                        {
                            c.requestFocusInWindow();
                        }
                    });
                }
            }
        });
        int result = JOptionPane.showConfirmDialog(this, p, resources.getString(L10NFindAndReplace.SAVE_SEARCH_TITLE),
                                                   JOptionPane.OK_CANCEL_OPTION,
                                                   JOptionPane.QUESTION_MESSAGE);
        if (result == JOptionPane.OK_OPTION)
        {
            final String name = nameField.getText();
            if (_model.isValidName(name))
            {
                LoadSaveView.this.saveSearchSettings(name, mdGUI);
            }
            else
            {
                String title = mdGUI.getStr("error");
                String message = FarUtil.getLabelText(resources, L10NFindAndReplace.MEMORIZE_ERROR)
                        + ' ' + name;
                JOptionPane.showMessageDialog(LoadSaveView.this, message, title, JOptionPane.ERROR_MESSAGE);
            }
        }
    }

    private JPanel buildSaveAsPanel(IResourceProvider resources, final JTextField nameField)
    {
        JPanel p = new JPanel(new GridBagLayout());
        p.setBorder(BorderFactory.createEmptyBorder(0, 0, 0, UiUtil.HGAP * 4));
        final JLabel prompt = new JLabel(FarUtil.getLabelText(resources, L10NFindAndReplace.MEMORIZE_PROMPT));
        prompt.setBorder(BorderFactory.createEmptyBorder(0, 0, UiUtil.VGAP, UiUtil.HGAP * 2));
        p.add(prompt, GridC.getc(0, 0).wx(1).fillx());
        p.add(nameField, GridC.getc(0, 1).wx(1).fillx());
        p.add(Box.createHorizontalStrut(150), GridC.getc(0, 2));   // minimum width 150 pixels
        final Vector<String> existingNames = new Vector<String>(_model.getSavedSearchNames());
        final JList existingList = new JList(existingNames);
        existingList.setBorder(null);
        existingList.setOpaque(true);
        existingList.setFocusable(false);
        existingList.setBackground(UIManager.getColor("control"));
        existingList.setForeground(UIManager.getColor("controlText"));
        existingList.setVisibleRowCount(Math.min(10, existingNames.size()));
        existingList.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
        existingList.addListSelectionListener(new ListSelectionListener()
        {
            public void valueChanged(ListSelectionEvent e)
            {
                final String selectedName = (String)existingList.getSelectedValue();
                if (selectedName != null) {
                    nameField.setText(selectedName);
                    nameField.setCaretPosition(selectedName.length());
                }
                nameField.requestFocusInWindow();
            }
        });
        final JScrollPane listPane = new JScrollPane(existingList, JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED, JScrollPane.HORIZONTAL_SCROLLBAR_NEVER);
        listPane.setBorder(null);
        p.add(listPane, GridC.getc(0,3).wxy(1, 1).fillboth());
        return p;
    }

    private void saveSearchSettings(String searchName, MoneydanceGUI mdGUI)
    {
        _model.saveCurrentSearch(searchName);
        _loadSaveLabel.setText(getCurrentSearchName(mdGUI));
    }

    private void loadSavedSearch(final String searchName, MoneydanceGUI mdGui)
    {
        _model.loadSearchSettings(searchName);
        _loadSaveLabel.setText(getCurrentSearchName(mdGui));
    }

    private void deleteSavedSearch(final String searchName, MoneydanceGUI mdGui)
    {
        _model.deleteSavedSearch(searchName);
        _loadSaveLabel.setText(getCurrentSearchName(mdGui));
    }

 }

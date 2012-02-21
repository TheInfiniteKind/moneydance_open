package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.view.gui.MDAction;
import com.moneydance.apps.md.view.gui.MDImages;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.moneydance.apps.md.view.gui.OKButtonListener;
import com.moneydance.apps.md.view.gui.OKButtonPanel;
import com.moneydance.apps.md.view.gui.OKButtonWindow;
import com.moneydance.util.StringUtils;

import javax.swing.BorderFactory;
import javax.swing.ImageIcon;
import javax.swing.JComponent;
import javax.swing.JLabel;
import javax.swing.JMenu;
import javax.swing.JMenuItem;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JPopupMenu;
import javax.swing.JTextField;
import java.awt.BorderLayout;
import java.awt.Image;
import java.awt.Rectangle;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.util.Collection;

public class LoadSaveView extends JPanel
{
    private final LoadSaveModel _model;
    private JLabel _loadSaveLabel;

    LoadSaveView(final MoneydanceGUI mdGui, final FarController controller)
    {
        _model = new LoadSaveModel(mdGui.getCurrentAccount(), controller);
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
            public void mouseClicked(MouseEvent e)
            {
                showSavedSearchMenu(loadParent, mdGui, resources);
            }
        });
        add(_loadSaveLabel, BorderLayout.CENTER);
    }

    private String getCurrentSearchName(final MoneydanceGUI mdGui)
    {
        String currentSave = _model.getCurrentSearchName();
        if (StringUtils.isBlank(currentSave))
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
        JPanel panel = new JPanel(new BorderLayout());
        panel.setOpaque(false);
        final JLabel prompt = new JLabel(FarUtil.getLabelText(resources, L10NFindAndReplace.MEMORIZE_PROMPT));
        prompt.setBorder(BorderFactory.createEmptyBorder(0, 0, UiUtil.VGAP, 0));
        panel.add(prompt, BorderLayout.NORTH);
        final JTextField nameField = new JTextField();
        panel.add(nameField, BorderLayout.CENTER);
        OKButtonListener listener = new OKButtonListener()
        {
            public void buttonPressed(int nButton)
            {
                final String name = nameField.getText();
                if ((nButton == OKButtonPanel.ANSWER_OK))
                {
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
        };
        OKButtonWindow dialog = new OKButtonWindow(mdGUI, this,
                                                   resources.getString(L10NFindAndReplace.SAVE_SEARCH_TITLE),
                                                   listener, OKButtonPanel.QUESTION_OK_CANCEL) {
            @Override
            public void isNowVisible()
            {
                nameField.requestFocusInWindow();
            }
        };
        dialog.showDialog(panel);
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

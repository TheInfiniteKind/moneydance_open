package com.moneydance.modules.features.findandreplace;

import com.moneydance.awt.AwtUtil;
import com.moneydance.awt.JCurrencyField;
import com.moneydance.util.CustomDateFormat;
import com.moneydance.apps.md.view.gui.AccountChoice;
import com.moneydance.apps.md.model.Account;

import javax.swing.table.JTableHeader;
import javax.swing.table.TableColumn;
import javax.swing.border.EmptyBorder;
import javax.swing.*;
import javax.swing.event.DocumentListener;
import javax.swing.event.DocumentEvent;
import java.beans.PropertyChangeListener;
import java.beans.PropertyChangeEvent;
import java.awt.event.ActionListener;
import java.awt.event.ActionEvent;
import java.awt.event.WindowEvent;
import java.awt.event.ItemListener;
import java.awt.event.ItemEvent;
import java.awt.event.KeyEvent;
import java.awt.BorderLayout;
import java.awt.Dimension;
import java.awt.Toolkit;
import java.awt.Font;
import java.awt.Cursor;
import java.util.regex.Pattern;
import java.util.regex.PatternSyntaxException;
import java.text.MessageFormat;

import info.clearthought.layout.TableLayout;
import info.clearthought.layout.TableLayoutConstraints;
import info.clearthought.layout.TableLayoutConstants;

/**
 * <p>The main view for the Find and Replace plugin. Has all the find and replace controls and
 * hosts the results table as well.</p>
 *
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />

 * @author Kevin Menningen
 * @version 1.0
 * @since 1.0
 */
class FarView extends JFrame implements PropertyChangeListener
{
    private final FarModel _model;
    private FarController _controller;

    // find panel
    private JRadioButton _findAndRadio;
    private JRadioButton _findOrRadio;
    private ButtonGroup _findBooleanGroup;

    private JCheckBox _findAccountsUseCheck;
    private JCheckBox _findAccountsRequireCheck;
    private JLabel _findAccountsList;
    private JButton _findAccountsSelect;

    private JCheckBox _findCategoryUseCheck;
    private JCheckBox _findCategoryRequireCheck;
    private JLabel _findCategoryList;
    private JButton _findCategorySelect;

    private JCheckBox _findAmountUseCheck;
    private JCheckBox _findAmountRequireCheck;
    private AmountPickerGroup _findAmountPickers;

    private JCheckBox _findDateUseCheck;
    private JCheckBox _findDateRequireCheck;
    private DatePickerGroup _findDatePickers;

    private JCheckBox _findFreeTextUseCheck;
    private JCheckBox _findFreeTextRequireCheck;
    private JCheckBox _findFreeTextUseDescriptionCheck;
    private JCheckBox _findFreeTextUseMemoCheck;
    private JCheckBox _findFreeTextUseCheckCheck;
    private JCheckBox _findFreeTextIncludeSplitsCheck;
    private JTextField _findFreeText;

    private JCheckBox _findTagsUseCheck;
    private JCheckBox _findTagsRequireCheck;
    private TxnTagsPickerGroup _findTagPickers;

    // replace panel
    private JCheckBox _replaceCategoryCheck;
    private JComboBox _replaceCategory;
    private JCheckBox _replaceAmountCheck;
    private JCurrencyField _replaceAmount;
    private JCheckBox _replaceDescriptionCheck;
    private JTextField _replaceDescription;
    private JCheckBox _replaceTagsCheck;
    private TxnTagsPicker _replaceAddTags;
    private JRadioButton _replaceAddRadio;
    private TxnTagsPicker _replaceRemoveTags;
    private JRadioButton _replaceRemoveRadio;
    private TxnTagsPicker _replaceReplaceTags;
    private JRadioButton _replaceReplaceRadio;
    private ButtonGroup _replaceTagsGroup;
    private JCheckBox _replaceMemoCheck;
    private JTextField _replaceMemo;

    // transaction list
    private JTable _findResults;
    private JLabel _summary;

    // buttons
    private JButton _findButton;
    private JButton _replaceButton;
    private JButton _replaceAllButton;
    private JButton _recordButton;
    private JButton _closeButton;
    private JButton _markAllButton;
    private JButton _markNoneButton;

    FarView(final FarModel model)
    {
        _model = model;
    }

    ///////////////////////////////////////////////////////////////////////////////////////////////
    // Package Private Methods
    ///////////////////////////////////////////////////////////////////////////////////////////////

    void layoutUI()
    {
        setupButtons();

        final double[][] sizes = new double[][]
        {
            // columns
            {
                TableLayout.FILL, // find
                UiUtil.HGAP * 3, // gap
                TableLayout.FILL, // replace
            },

            // rows
            {
                TableLayout.PREFERRED, // find and replace
                UiUtil.VGAP,
                TableLayout.FILL,      // results
                UiUtil.VGAP,
                TableLayout.PREFERRED  // buttons
            }
        };

        final JPanel main = new JPanel(new TableLayout( sizes ));
        main.setBorder(new EmptyBorder(10, 10, 10, 10));

        main.add(createFindPanel(), new TableLayoutConstraints( 0, 0 ) );
        main.add(createReplacePanel(), new TableLayoutConstraints( 2, 0 ) );

        main.add(createResultsPanel(), new TableLayoutConstraints(0, 2, 2, 2));

        JPanel buttonPanel = createLowerLeftButtonPanel();
        main.add( buttonPanel, new TableLayoutConstraints( 0, 4, 0, 4,
                TableLayoutConstants.LEFT, TableLayoutConstants.FULL ) );
        buttonPanel = createLowerRightButtonPanel();
        main.add( buttonPanel, new TableLayoutConstraints( 0, 4, 2, 4,
                TableLayoutConstants.RIGHT, TableLayoutConstants.FULL ) );

        getContentPane().add( main );

        setDefaultCloseOperation(JFrame.DO_NOTHING_ON_CLOSE);
        enableEvents(WindowEvent.WINDOW_CLOSING);

        // set the title of the dialog/frame
        setTitle(_controller.getString(L10NFindAndReplace.TITLE));

        final Dimension parentSize = Toolkit.getDefaultToolkit().getScreenSize();
        final Dimension mySize = new Dimension(
                (int)(parentSize.getWidth() * 0.8),
                (int)(parentSize.getHeight() * 0.8) );
        setSize(mySize);
        AwtUtil.centerWindow(this);

        _model.getFindResults().addBlankTransaction();

        setupKeyListener();

        // default button
        getRootPane().setDefaultButton(_findButton);
    }

    void setController(final FarController controller)
    {
        _controller = controller;
    }

    JTable getFindResultsTable()
    {
        return _findResults;
    }

    ///////////////////////////////////////////////////////////////////////////////////////////////
    // Overrides
    ///////////////////////////////////////////////////////////////////////////////////////////////

    /**
     * Processes window events occurring on this component.
     * Hides the window or disposes of it, as specified by the setting
     * of the <code>defaultCloseOperation</code> property.
     *
     * @param event the window event
     * @see #setDefaultCloseOperation
     * @see java.awt.Window#processWindowEvent
     */
    @Override
    protected void processWindowEvent(WindowEvent event)
    {
        if (event.getID() == WindowEvent.WINDOW_CLOSING)
        {
            _controller.hide();
            return;
        }
        super.processWindowEvent(event);
    }


    ///////////////////////////////////////////////////////////////////////////////////////////////
    //  PropertyChangeListener
    ///////////////////////////////////////////////////////////////////////////////////////////////
    /**
     * This method gets called when a bound property is changed. Property changes will come from
     * the model mostly.
     *
     * @param event A PropertyChangeEvent object describing the event source
     *            and the property that has changed.
     */

    public void propertyChange(final PropertyChangeEvent event)
    {
        final String eventID = event.getPropertyName();
        final boolean all = N12EFindAndReplace.ALL_PROPERTIES.equals(eventID);

        if (all || N12EFindAndReplace.FIND_COMBINATION.equals(eventID))
        {
            if (_model.getFilterCombineOr())
            {
                _findBooleanGroup.setSelected(_findOrRadio.getModel(), true);
            }
            else
            {
                _findBooleanGroup.setSelected(_findAndRadio.getModel(), true);
            }
        }
        if (all || N12EFindAndReplace.ACCOUNT_SELECT.equals(eventID))
        {
            _findAccountsList.setText(_controller.getAccountListDisplay());
        }
        if (all || N12EFindAndReplace.ACCOUNT_USE.equals(eventID))
        {
            _findAccountsUseCheck.setSelected(_controller.getUseAccountFilter());
        }
        if (all || N12EFindAndReplace.ACCOUNT_REQUIRED.equals(eventID))
        {
            _findAccountsRequireCheck.setSelected(_controller.getRequireAccountFilter());
        }
        if (all || N12EFindAndReplace.CATEGORY_SELECT.equals(eventID))
        {
            _findCategoryList.setText(_controller.getCategoryListDisplay());
        }
        if (all || N12EFindAndReplace.CATEGORY_USE.equals(eventID))
        {
            _findCategoryUseCheck.setSelected(_controller.getUseCategoryFilter());
        }
        if (all || N12EFindAndReplace.CATEGORY_REQUIRED.equals(eventID))
        {
            _findCategoryRequireCheck.setSelected(_controller.getRequireCategoryFilter());
        }
        if (all || N12EFindAndReplace.AMOUNT_USE.equals(eventID))
        {
            _findAmountUseCheck.setSelected(_controller.getUseAmountFilter());
        }
        if (all || N12EFindAndReplace.AMOUNT_REQUIRED.equals(eventID))
        {
            _findAmountRequireCheck.setSelected(_controller.getRequireAmountFilter());
        }
        if (all || N12EFindAndReplace.DATE_USE.equals(eventID))
        {
            _findDateUseCheck.setSelected(_controller.getUseDateFilter());
        }
        if (all || N12EFindAndReplace.DATE_REQUIRED.equals(eventID))
        {
            _findDateRequireCheck.setSelected(_controller.getRequireDateFilter());
        }
        if (all || N12EFindAndReplace.FREETEXT_USE.equals(eventID))
        {
            final boolean use = _controller.getUseFreeTextFilter();
            _findFreeTextUseCheck.setSelected(use);

            _findFreeTextUseDescriptionCheck.setEnabled(use);
            _findFreeTextUseMemoCheck.setEnabled(use);
            _findFreeTextUseCheckCheck.setEnabled(use);
            _findFreeTextIncludeSplitsCheck.setEnabled(use);
        }
        if (all || N12EFindAndReplace.FREETEXT_REQUIRED.equals(eventID))
        {
            _findFreeTextRequireCheck.setSelected(_controller.getRequireFreeTextFilter());
        }
        if (all || N12EFindAndReplace.TAGS_USE.equals(eventID))
        {
            _findTagsUseCheck.setSelected(_controller.getUseTagsFilter());
        }
        if (all || N12EFindAndReplace.TAGS_REQUIRED.equals(eventID))
        {
            _findTagsRequireCheck.setSelected(_controller.getRequireTagsFilter());
        }
        if (all || N12EFindAndReplace.FREETEXT_DESCRIPTION.equals(eventID))
        {
            _findFreeTextUseDescriptionCheck.setSelected(_controller.getFreeTextUseDescription());
        }
        if (all || N12EFindAndReplace.FREETEXT_MEMO.equals(eventID))
        {
            _findFreeTextUseMemoCheck.setSelected(_controller.getFreeTextUseMemo());
        }
        if (all || N12EFindAndReplace.FREETEXT_CHECK.equals(eventID))
        {
            _findFreeTextUseCheckCheck.setSelected(_controller.getFreeTextUseCheck());
        }
        if (all || N12EFindAndReplace.FREETEXT_SPLITS.equals(eventID))
        {
            _findFreeTextIncludeSplitsCheck.setSelected(_controller.getFreeTextIncludeSplits());
        }

        // replacement
        if (all || N12EFindAndReplace.REPLACE_CATEGORY.equals(eventID))
        {
            _replaceCategoryCheck.setSelected(_controller.getReplaceCategory());
        }
        if (all || N12EFindAndReplace.REPLACE_AMOUNT.equals(eventID))
        {
            _replaceAmountCheck.setSelected(_controller.getReplaceAmount());
        }
        if (all || N12EFindAndReplace.REPLACE_DESCRIPTION.equals(eventID))
        {
            _replaceDescriptionCheck.setSelected(_controller.getReplaceDescription());
        }
        if (all || N12EFindAndReplace.REPLACE_MEMO.equals(eventID))
        {
            _replaceMemoCheck.setSelected(_controller.getReplaceMemo());
        }
        if (all || N12EFindAndReplace.REPLACE_TAGS.equals(eventID))
        {
            _replaceTagsCheck.setSelected(_controller.getReplaceTags());
        }

        if (all || N12EFindAndReplace.FIND_RESULTS_UPDATE.equals(eventID))
        {
            updateSummary();
            _findResults.repaint();
        }

        if (all)
        {
            TagPickerModel tagModel = _controller.getIncludedTagsModel();
            _findTagPickers.getIncludePicker().setModel(tagModel);

            tagModel = _controller.getExcludedTagsModel();
            _findTagPickers.getExcludePicker().setModel(tagModel);

            tagModel = _controller.getReplaceAddTagsModel();
            _replaceAddTags.setModel(tagModel);

            tagModel = _controller.getReplaceRemoveTagsModel();
            _replaceRemoveTags.setModel(tagModel);

            tagModel = _controller.getReplaceReplaceTagsModel();
            _replaceReplaceTags.setModel(tagModel);
        }

        // update state
        if (_controller.isDirty())
        {
            _recordButton.setEnabled(true);
        }
        else
        {
            _recordButton.setEnabled(false);
        }

    } // propertyChange()


    void setFreeText(String freeText)
    {
        _findFreeText.setText(freeText);
        if ((freeText != null) && (freeText.length() > 0))
        {
            _findFreeTextUseCheck.setSelected(true);
        }
    }

    void fireFind()
    {
        SwingUtilities.invokeLater(new Runnable()
        {
            public void run()
            {
                _findButton.doClick();
            }
        });
    }

    ///////////////////////////////////////////////////////////////////////////////////////////////
    // Private Methods
    ///////////////////////////////////////////////////////////////////////////////////////////////

    private void setupKeyListener()
    {
        KeyStroke escapeKeyStroke = KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0, false);
        Action escapeAction = new AbstractAction()
        {
            // close the frame when the user presses escape
            public void actionPerformed(ActionEvent e)
            {
                _controller.hide();
            }
        };
        getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(escapeKeyStroke,
                N12EFindAndReplace.ESCAPE_KEY);
        getRootPane().getActionMap().put(N12EFindAndReplace.ESCAPE_KEY, escapeAction);
    }

    private JPanel createResultsPanel()
    {
        final JPanel panel = new JPanel(new BorderLayout());
        final JLabel panelLabel = new JLabel(_controller.getString(L10NFindAndReplace.RESULTS_LABEL));
        final JPanel headerPanel = new JPanel(new BorderLayout());
        final Font bold = panelLabel.getFont().deriveFont(Font.BOLD);
        panelLabel.setFont( bold );
        headerPanel.add(panelLabel, BorderLayout.WEST);
        _summary = new JLabel();
        headerPanel.add(_summary, BorderLayout.EAST);
        panel.add(headerPanel, BorderLayout.NORTH);

        final FindResultsTableColumnModel columnModel = new FindResultsTableColumnModel(_controller);

        _findResults = new FindResultsTable(_model.getFindResults());
        _findResults.setColumnModel(columnModel);
        _findResults.setFillsViewportHeight(true);
        _findResults.setShowGrid(false);
        _findResults.setTableHeader(new JTableHeader(columnModel));
        _findResults.setDefaultRenderer(TableColumn.class, new FindResultsTableCellRenderer());
        _findResults.getSelectedRows();
        columnModel.setTableSelectionModel(_findResults.getSelectionModel());

        // experimentally-derived values
        columnModel.getColumn(FindResultsTableModel.SEL_INDEX).setPreferredWidth(28);
        columnModel.getColumn(FindResultsTableModel.USE_INDEX).setPreferredWidth(22);
        columnModel.getColumn(FindResultsTableModel.ACCOUNT_INDEX).setPreferredWidth(144);
        columnModel.getColumn(FindResultsTableModel.DATE_INDEX).setPreferredWidth(86);
        columnModel.getColumn(FindResultsTableModel.DESCRIPTION_INDEX).setPreferredWidth(206);
        columnModel.getColumn(FindResultsTableModel.TAG_INDEX).setPreferredWidth(144);
        columnModel.getColumn(FindResultsTableModel.CATEGORY_INDEX).setPreferredWidth(116);
        columnModel.getColumn(FindResultsTableModel.CLEARED_INDEX).setPreferredWidth(24);
        columnModel.getColumn(FindResultsTableModel.AMOUNT_INDEX).setPreferredWidth(72);

        panel.add(new JScrollPane(_findResults), BorderLayout.CENTER);

        return panel;
    }

    private void setupButtons()
    {
        _findButton = createButton(L10NFindAndReplace.FIND_BUTTON_TEXT,
                L10NFindAndReplace.FIND_BUTTON_MNC);
        _findButton.addActionListener(new ActionListener()
        {
            public void actionPerformed(final ActionEvent event)
            {
                final Cursor current = getCursor();
                setCursor(Cursor.getPredefinedCursor(Cursor.WAIT_CURSOR));
                if (saveFindEdits())
                {
                    _controller.find();
                }
                setCursor(current);
            }
        });

        _replaceButton = createButton(L10NFindAndReplace.REPLACE_BUTTON_TEXT,
                L10NFindAndReplace.REPLACE_BUTTON_MNC);
        _replaceButton.addActionListener(new ActionListener()
        {
            public void actionPerformed(final ActionEvent event)
            {
                final Cursor current = getCursor();
                setCursor(Cursor.getPredefinedCursor(Cursor.WAIT_CURSOR));
                saveReplaceEdits();
                _controller.replace();
                setCursor(current);
            }
        });

        _replaceAllButton = createButton(L10NFindAndReplace.REPLACEALL_BUTTON_TEXT,
                L10NFindAndReplace.REPLACEALL_BUTTON_MNC);
        _replaceAllButton.addActionListener(new ActionListener()
        {
            public void actionPerformed(final ActionEvent event)
            {
                final Cursor current = getCursor();
                setCursor(Cursor.getPredefinedCursor(Cursor.WAIT_CURSOR));
                saveReplaceEdits();
                _controller.replaceAll();
                setCursor(current);
            }
        });

        _closeButton = createButton(L10NFindAndReplace.CANCEL_BUTTON_TEXT, null);
        _closeButton.addActionListener(new ActionListener()
        {
            public void actionPerformed(final ActionEvent event)
            {
                _controller.hide();   
            }
        });

        _recordButton = createButton(L10NFindAndReplace.RECORD_BUTTON_TEXT, null);
        _recordButton.addActionListener(new ActionListener()
        {
            public void actionPerformed(final ActionEvent event)
            {
                _controller.commit();
                _controller.hide();
            }
        });

        _markAllButton = createButton(L10NFindAndReplace.MARK_ALL_BUTTON_TEXT, null);
        _markAllButton.addActionListener(new ActionListener()
        {
            public void actionPerformed(final ActionEvent event)
            {
                _controller.markAll();
            }
        });

        _markNoneButton = createButton(L10NFindAndReplace.MARK_NONE_BUTTON_TEXT, null);
        _markNoneButton.addActionListener(new ActionListener()
        {
            public void actionPerformed(final ActionEvent event)
            {
                _controller.markNone();
            }
        });


    }

    private JButton createButton(final String buttonTextKey, final String buttonMnemonicKey)
    {
        final JButton button = new JButton( _controller.getString(buttonTextKey) );
        if (buttonMnemonicKey != null)
        {
            setButtonMnemonic( button, buttonMnemonicKey );
        }
        return button;
    }

    private void setButtonMnemonic( AbstractButton button, final String buttonMnemonicKey )
    {
        String mnemonic = _controller.getString( buttonMnemonicKey );
        if ( (mnemonic != null) && (mnemonic.length() > 0) )
        {
            button.setMnemonic( mnemonic.charAt( 0 ) );
        }
    }

    private JPanel createFindPanel()
    {
        final double[][] sizes = new double[][]
        {
            // columns
            {
                TableLayout.PREFERRED, // label
                24, // checkbox with gaps
                2, // another checkbox with gaps - removed for now
                TableLayout.PREFERRED, // another label
                TableLayout.FILL, // field
                TableLayout.PREFERRED,  // label
                TableLayout.PREFERRED // second field
            },

            // rows -- all preferred with gaps in between
            {
                TableLayout.PREFERRED, UiUtil.VGAP, TableLayout.PREFERRED, UiUtil.VGAP,
                TableLayout.PREFERRED, UiUtil.VGAP, TableLayout.PREFERRED, UiUtil.VGAP,
                TableLayout.PREFERRED, UiUtil.VGAP, TableLayout.PREFERRED, UiUtil.VGAP,
                TableLayout.PREFERRED, UiUtil.VGAP, TableLayout.PREFERRED, UiUtil.VGAP,
                TableLayout.PREFERRED
            }
        };
        final JPanel findPanel = new JPanel( new TableLayout(sizes) );
        int row = 0;
        final JLabel panelLabel = new JLabel( _controller.getString( L10NFindAndReplace.FIND_LABEL ));
        final Font bold = panelLabel.getFont().deriveFont(Font.BOLD);
        panelLabel.setFont( bold );
        findPanel.add( panelLabel, new TableLayoutConstraints(0, row) );
        row += 2; // skip the gap

        // the combine criteria row is a little special -- the only 2 component field set and no
        // check box
        JLabel label = new JLabel(
                FarUtil.getLabelText(_controller, L10NFindAndReplace.FIND_BOOL_LABEL) );
        findPanel.add( label, new TableLayoutConstraints(0, row) );
        _findAndRadio = new JRadioButton( _controller.getString( L10NFindAndReplace.FIND_BOOL_AND ) );
        setButtonMnemonic( _findAndRadio, L10NFindAndReplace.FIND_BOOL_AND_MNC );
        findPanel.add( _findAndRadio, new TableLayoutConstraints( 3, row, 4, row,
                TableLayoutConstants.CENTER, TableLayoutConstants.FULL));
        _findOrRadio = new JRadioButton( _controller.getString( L10NFindAndReplace.FIND_BOOL_OR ) );
        setButtonMnemonic( _findOrRadio, L10NFindAndReplace.FIND_BOOL_OR_MNC );
        findPanel.add( _findOrRadio, new TableLayoutConstraints( 5, row, 6, row,
                TableLayoutConstants.CENTER, TableLayoutConstants.FULL));

        _findBooleanGroup = new ButtonGroup();
        _findBooleanGroup.add( _findAndRadio );
        _findBooleanGroup.add( _findOrRadio );

        row += 2;

        final String findCheckTip = _controller.getString(L10NFindAndReplace.FIND_USE_TIP);

        // accounts row
        _findAccountsUseCheck = new JCheckBox();
        _findAccountsUseCheck.setToolTipText(findCheckTip);
        _findAccountsRequireCheck = new JCheckBox();
        row = addRowLabel( findPanel, row, L10NFindAndReplace.FIND_ACCOUNTS_LABEL,
                L10NFindAndReplace.FIND_ACCOUNTS_MNC, _findAccountsUseCheck);
        _findAccountsList = new JLabel();
        findPanel.add( _findAccountsList, new TableLayoutConstraints( 3, row, 5, row) );
        _findAccountsSelect = createButton( L10NFindAndReplace.FIND_ACCOUNTS_SELECT_TEXT,
                L10NFindAndReplace.FIND_ACCOUNTS_SELECT_MNC );
        findPanel.add( _findAccountsSelect, new TableLayoutConstraints( 6, row ) );
        row += 2;

        // category row
        _findCategoryUseCheck = new JCheckBox();
        _findCategoryUseCheck.setToolTipText(findCheckTip);
        _findCategoryRequireCheck = new JCheckBox();
        row = addRowLabel( findPanel, row, L10NFindAndReplace.FIND_CATEGORIES_LABEL,
                L10NFindAndReplace.FIND_CATEGORIES_MNC, _findCategoryUseCheck);
        _findCategoryList = new JLabel();
        findPanel.add( _findCategoryList, new TableLayoutConstraints( 3, row, 5, row) );
        _findCategorySelect = createButton( L10NFindAndReplace.FIND_CATEGORIES_SELECT_TEXT,
                L10NFindAndReplace.FIND_CATEGORIES_SELECT_MNC );
        findPanel.add( _findCategorySelect, new TableLayoutConstraints( 6, row ) );
        row += 2;

        // label plus 2 checkboxes
        final int startCol = 3;

        // amount row
        _findAmountUseCheck = new JCheckBox();
        _findAmountUseCheck.setToolTipText(findCheckTip);
        _findAmountRequireCheck = new JCheckBox();
        row = addRowLabel( findPanel, row, L10NFindAndReplace.FIND_AMOUNT_LABEL,
                L10NFindAndReplace.FIND_AMOUNT_MNC, _findAmountUseCheck);

        _findAmountPickers = new AmountPickerGroup(_controller);
        row = addRowField1( findPanel, row, startCol, _findAmountPickers );

        // date row
        _findDateUseCheck = new JCheckBox();
        _findDateUseCheck.setToolTipText(findCheckTip);
        _findDateRequireCheck = new JCheckBox();
        row = addRowLabel( findPanel, row, L10NFindAndReplace.FIND_DATE_LABEL,
                L10NFindAndReplace.FIND_DATE_MNC, _findDateUseCheck);

        CustomDateFormat formatter;
        if (_controller.getMDMain() != null)
        {
            formatter = _controller.getMDMain().getPreferences().getShortDateFormatter();
        }
        else
        {
            formatter = new CustomDateFormat(N12EFindAndReplace.DATE_FORMAT);
        }
        _findDatePickers = new DatePickerGroup(formatter, _controller);
        row = addRowField1( findPanel, row, startCol, _findDatePickers);

        // free text
        _findFreeTextUseCheck = new JCheckBox();
        _findFreeTextUseCheck.setToolTipText(findCheckTip);
        _findFreeTextRequireCheck = new JCheckBox();
        row = addRowLabel( findPanel, row, L10NFindAndReplace.FIND_FREETEXT_LABEL,
                L10NFindAndReplace.FIND_FREETEXT_MNC, _findFreeTextUseCheck);
        _findFreeText = new JTextField();
        row = addRowField1( findPanel, row, startCol, _findFreeText);
        
        _findFreeTextUseDescriptionCheck = new JCheckBox(
                _controller.getString( L10NFindAndReplace.FIND_FREETEXT_DESCRIPTION ));
        _findFreeTextUseDescriptionCheck.setToolTipText(
                _controller.getString(L10NFindAndReplace.FIND_FREETEXT_DESC_TIP));
        _findFreeTextUseDescriptionCheck.setEnabled(false);

        _findFreeTextUseMemoCheck = new JCheckBox(
                _controller.getString( L10NFindAndReplace.FIND_FREETEXT_MEMO ));
        _findFreeTextUseMemoCheck.setToolTipText(
                _controller.getString(L10NFindAndReplace.FIND_FREETEXT_MEMO_TIP));
        _findFreeTextUseMemoCheck.setEnabled(false);

        _findFreeTextUseCheckCheck = new JCheckBox(
                _controller.getString( L10NFindAndReplace.FIND_FREETEXT_CHECK ));
        _findFreeTextUseCheckCheck.setToolTipText(
                _controller.getString(L10NFindAndReplace.FIND_FREETEXT_CHECK_TIP));
        _findFreeTextUseCheckCheck.setEnabled(false);

        _findFreeTextIncludeSplitsCheck = new JCheckBox(
                _controller.getString( L10NFindAndReplace.FIND_FREETEXT_SPLITS ));
        _findFreeTextIncludeSplitsCheck.setToolTipText(
                _controller.getString(L10NFindAndReplace.FIND_FREETEXT_SPLITS_TIP));
        _findFreeTextIncludeSplitsCheck.setEnabled(false);

        final double[][] checkSizes = new double[][]
        {
            // columns
            {
                TableLayout.PREFERRED, UiUtil.HGAP, TableLayout.PREFERRED, UiUtil.HGAP,
                TableLayout.PREFERRED, UiUtil.HGAP, TableLayout.PREFERRED
            },
            { TableLayout.PREFERRED }
        };
        final JPanel optionsPanel = new JPanel(new TableLayout(checkSizes));
        optionsPanel.add(_findFreeTextUseDescriptionCheck, new TableLayoutConstraints(0, 0));
        optionsPanel.add(_findFreeTextUseMemoCheck, new TableLayoutConstraints(2, 0));
        optionsPanel.add(_findFreeTextUseCheckCheck, new TableLayoutConstraints(4, 0));
        optionsPanel.add(_findFreeTextIncludeSplitsCheck, new TableLayoutConstraints(6, 0));
        row = addRowField1( findPanel, row, startCol, optionsPanel );

        // tags
        _findTagsUseCheck = new JCheckBox();
        _findTagsUseCheck.setToolTipText(findCheckTip);
        _findTagsRequireCheck = new JCheckBox();
        row = addRowLabel( findPanel, row, L10NFindAndReplace.FIND_TAGS_LABEL,
                L10NFindAndReplace.FIND_TAGS_MNC, _findTagsUseCheck);
        _findTagPickers = new TxnTagsPickerGroup(_controller.getMDGUI(), _model.getData(), _controller);
        addRowField1( findPanel, row, startCol, _findTagPickers);

        buildFindPanelActions();

        return findPanel;
    } // createFindPanel()

    private void buildFindPanelActions()
    {
        _findAndRadio.addItemListener(new ItemListener()
        {
            public void itemStateChanged(final ItemEvent event)
            {
                if (event.getStateChange() == ItemEvent.SELECTED)
                {
                    _controller.setFilterCombineOr(false);
                }
            }
        });
        _findOrRadio.addItemListener(new ItemListener()
        {
            public void itemStateChanged(final ItemEvent event)
            {
                if (event.getStateChange() == ItemEvent.SELECTED)
                {
                    _controller.setFilterCombineOr(true);
                }
            }
        });

        _findAccountsSelect.addActionListener(new ActionListener()
        {
            public void actionPerformed(final ActionEvent action)
            {
                _controller.selectAccounts();
            }
        });
        _findAccountsUseCheck.addItemListener(new ItemListener()
        {
            public void itemStateChanged(final ItemEvent event)
            {
                _controller.setUseAccountFilter(event.getStateChange() == ItemEvent.SELECTED);
            }
        });
        _findAccountsRequireCheck.addItemListener(new ItemListener()
        {
            public void itemStateChanged(final ItemEvent event)
            {
                _controller.setRequireAccountFilter(event.getStateChange() == ItemEvent.SELECTED);
            }
        });

        _findCategoryUseCheck.addItemListener(new ItemListener()
        {
            public void itemStateChanged(final ItemEvent event)
            {
                _controller.setUseCategoryFilter(event.getStateChange() == ItemEvent.SELECTED);
            }
        });
        _findCategoryRequireCheck.addItemListener(new ItemListener()
        {
            public void itemStateChanged(final ItemEvent event)
            {
                _controller.setRequireCategoryFilter(event.getStateChange() == ItemEvent.SELECTED);
            }
        });
        _findCategorySelect.addActionListener(new ActionListener()
        {
            public void actionPerformed(final ActionEvent action)
            {
                _controller.selectCategories();
            }
        });

        _findAmountPickers.addChangeListener(new DocumentListener()
        {
            public void insertUpdate(DocumentEvent e)
            {
                _controller.setUseAmountFilter(true);
                _controller.setRequireAmountFilter(!_controller.getFilterCombineOr());
            }
            public void removeUpdate(DocumentEvent e)
            {
                _controller.setUseAmountFilter(true);
                _controller.setRequireAmountFilter(!_controller.getFilterCombineOr());
            }

            public void changedUpdate(DocumentEvent e) { }
        });
        _findAmountUseCheck.addItemListener(new ItemListener()
        {
            public void itemStateChanged(final ItemEvent event)
            {
                _controller.setUseAmountFilter(event.getStateChange() == ItemEvent.SELECTED);
            }
        });
        _findAmountRequireCheck.addItemListener(new ItemListener()
        {
            public void itemStateChanged(final ItemEvent event)
            {
                _controller.setRequireAmountFilter(event.getStateChange() == ItemEvent.SELECTED);
            }
        });

        _findDatePickers.addChangeListener(new DocumentListener()
        {
            public void insertUpdate(DocumentEvent e)
            {
                _controller.setUseDateFilter(true);
                _controller.setRequireDateFilter(!_controller.getFilterCombineOr());
            }
            public void removeUpdate(DocumentEvent e)
            {
                _controller.setUseDateFilter(true);
                _controller.setRequireDateFilter(!_controller.getFilterCombineOr());
            }

            public void changedUpdate(DocumentEvent e) { }
        });
        _findDateUseCheck.addItemListener(new ItemListener()
        {
            public void itemStateChanged(final ItemEvent event)
            {
                _controller.setUseDateFilter(event.getStateChange() == ItemEvent.SELECTED);
            }
        });
        _findDateRequireCheck.addItemListener(new ItemListener()
        {
            public void itemStateChanged(final ItemEvent event)
            {
                _controller.setRequireDateFilter(event.getStateChange() == ItemEvent.SELECTED);
            }
        });

        _findFreeText.getDocument().addDocumentListener(new DocumentListener()
        {
            public void insertUpdate(DocumentEvent e)
            {
                _controller.setUseFreeTextFilter(true);
                _controller.setRequireFreeTextFilter(!_controller.getFilterCombineOr());
            }
            public void removeUpdate(DocumentEvent e)
            {
                _controller.setUseFreeTextFilter(true);
                _controller.setRequireFreeTextFilter(!_controller.getFilterCombineOr());
            }

            public void changedUpdate(DocumentEvent e) { }
        });
        _findFreeTextUseCheck.addItemListener(new ItemListener()
        {
            public void itemStateChanged(final ItemEvent event)
            {
                _controller.setUseFreeTextFilter(event.getStateChange() == ItemEvent.SELECTED);
            }
        });
        _findFreeTextRequireCheck.addItemListener(new ItemListener()
        {
            public void itemStateChanged(final ItemEvent event)
            {
                _controller.setRequireFreeTextFilter(event.getStateChange() == ItemEvent.SELECTED);
            }
        });
        _findFreeTextUseDescriptionCheck.addItemListener(new ItemListener()
        {
            public void itemStateChanged(final ItemEvent event)
            {
                _controller.setFreeTextUseDescription(event.getStateChange() == ItemEvent.SELECTED);
            }
        });
        _findFreeTextUseMemoCheck.addItemListener(new ItemListener()
        {
            public void itemStateChanged(final ItemEvent event)
            {
                _controller.setFreeTextUseMemo(event.getStateChange() == ItemEvent.SELECTED);
            }
        });
        _findFreeTextUseCheckCheck.addItemListener(new ItemListener()
        {
            public void itemStateChanged(final ItemEvent event)
            {
                _controller.setFreeTextUseCheck(event.getStateChange() == ItemEvent.SELECTED);
            }
        });
        _findFreeTextIncludeSplitsCheck.addItemListener(new ItemListener()
        {
            public void itemStateChanged(final ItemEvent event)
            {
                _controller.setFreeTextIncludeSplits(event.getStateChange() == ItemEvent.SELECTED);
            }
        });

        _findTagPickers.addSelectionListener(new ActionListener()
        {
            public void actionPerformed(final ActionEvent event)
            {
                // notify that tags will be used
                _controller.setUseTagsFilter(true);
                _controller.setRequireTagsFilter(!_controller.getFilterCombineOr());
            }
        });
        _findTagsUseCheck.addItemListener(new ItemListener()
        {
            public void itemStateChanged(final ItemEvent event)
            {
                _controller.setUseTagsFilter(event.getStateChange() == ItemEvent.SELECTED);
            }
        });
        _findTagsRequireCheck.addItemListener(new ItemListener()
        {
            public void itemStateChanged(final ItemEvent event)
            {
                _controller.setRequireTagsFilter(event.getStateChange() == ItemEvent.SELECTED);
            }
        });

    }

    private boolean saveFindEdits()
    {
        // account and category have already been saved
        _controller.setAmountRange(_findAmountPickers.getFromAmountPicker().getValue(),
                _findAmountPickers.getToAmountPicker().getValue());
        _controller.setDateRange(_findDatePickers.getFromDatePicker().getDateInt(),
                _findDatePickers.getToDatePicker().getDateInt());

        if (_controller.getUseFreeTextFilter())
        {
            final String textMatch = _findFreeText.getText();
            if (FarUtil.hasRegularExpression(textMatch))
            {
                String regex = FarUtil.createRegularExpression(textMatch);
                try
                {
                    Pattern.compile(regex);
                }
                catch (PatternSyntaxException error)
                {
                    final String title = _controller.getString(L10NFindAndReplace.NOTICE_TITLE);
                    final String message = error.getMessage();
                    final String format = _controller.getString(L10NFindAndReplace.ERROR_REGEX_FMT);
                    final String text = MessageFormat.format(format, textMatch, message);
                    JOptionPane.showMessageDialog(this, text, title, JOptionPane.ERROR_MESSAGE);
                    return false;
                }
            }

            _controller.setFreeTextMatch(_findFreeText.getText());
        }
        _findTagPickers.updateFromView();
        return true;
    }

    private JPanel createReplacePanel()
    {
        final double[][] sizes = new double[][]
        {
            // columns
            {
                TableLayout.PREFERRED, // label
                24, // checkbox with gaps
                TableLayout.PREFERRED, // label
                TableLayout.PREFERRED, // field
                TableLayout.PREFERRED,  // label
                TableLayout.FILL // second field
            },

            // rows -- all preferred with gaps in between
            {
                TableLayout.PREFERRED, UiUtil.VGAP, TableLayout.PREFERRED, UiUtil.VGAP,
                TableLayout.PREFERRED, UiUtil.VGAP, TableLayout.PREFERRED, UiUtil.VGAP,
                TableLayout.PREFERRED, UiUtil.VGAP, TableLayout.PREFERRED, UiUtil.VGAP,
                TableLayout.PREFERRED, UiUtil.VGAP, TableLayout.PREFERRED,
                UiUtil.VGAP * 2, TableLayout.FILL  // buttons
            }
        };
        final JPanel replacePanel = new JPanel( new TableLayout(sizes) );
        int row = 0;
        final JLabel panelLabel = new JLabel( _controller.getString( L10NFindAndReplace.REPLACE_LABEL ));
        final Font bold = panelLabel.getFont().deriveFont(Font.BOLD);
        panelLabel.setFont( bold );
        replacePanel.add( panelLabel, new TableLayoutConstraints(0, row) );
        row += 2; // skip the gap

        // only one checkbox
        final int startCol = 2;

        // categories row
        _replaceCategoryCheck = new JCheckBox();
        row = addRowLabel( replacePanel, row, L10NFindAndReplace.REPLACE_CAT_LABEL,
                L10NFindAndReplace.REPLACE_CAT_MNC, _replaceCategoryCheck );
        if (_controller.getMDGUI() != null)
        {
            AccountChoice chooser = new AccountChoice(_model.getData(), _controller.getMDGUI());
            chooser.setContainerAccount(_model.getData());
            chooser.setShowAssetAccounts(false);
            chooser.setShowBankAccounts(false);
            chooser.setShowCreditCardAccounts(false);
            chooser.setShowInvestAccounts(false);
            chooser.setShowLiabilityAccounts(false);
            chooser.setShowLoanAccounts(false);
            chooser.setShowSecurityAccounts(false);
            chooser.setShowOtherAccounts(false);

            // show only categories
            chooser.setShowIncomeAccounts(true);
            chooser.setShowExpenseAccounts(true);

            chooser.setSelectedAccountIndex(0);
            _replaceCategory = chooser;
        }
        else
        {
            _replaceCategory = new JComboBox();
        }
        row = addRowField1( replacePanel, row, startCol, _replaceCategory );

        // amount row
        _replaceAmountCheck = new JCheckBox();
        row = addRowLabel( replacePanel, row, L10NFindAndReplace.REPLACE_AMOUNT_LABEL,
                L10NFindAndReplace.REPLACE_AMOUNT_MNC, _replaceAmountCheck );
        _replaceAmount = new JCurrencyField(_controller.getCurrencyType(),
                _controller.getCurrencyTable(), _controller.getDecimalChar(),
                _controller.getCommaChar());
        row = addRowField1( replacePanel, row, startCol, _replaceAmount );

        // description
        _replaceDescriptionCheck = new JCheckBox();
        row = addRowLabel( replacePanel, row, L10NFindAndReplace.REPLACE_DESCRIPTION_LABEL,
                L10NFindAndReplace.REPLACE_DESCRIPTION_MNC, _replaceDescriptionCheck );
        _replaceDescription = new JTextField();
        row = addRowField1( replacePanel, row, startCol, _replaceDescription );

        // tags - 3 rows
        _replaceTagsCheck = new JCheckBox();
        row = addRowLabel( replacePanel, row, L10NFindAndReplace.REPLACE_TAGS_LABEL,
                L10NFindAndReplace.REPLACE_TAGS_MNC, _replaceTagsCheck );
        _replaceAddTags = new TxnTagsPicker(_controller.getMDGUI(), _model.getData());
        _replaceAddRadio = new JRadioButton();
        row = addRowField3( replacePanel, row, startCol, _replaceAddRadio, L10NFindAndReplace.REPLACE_TAGSADD_LABEL, _replaceAddTags.getView() );
        _replaceRemoveTags = new TxnTagsPicker(_controller.getMDGUI(), _model.getData());
        _replaceRemoveRadio = new JRadioButton();
        row = addRowField3( replacePanel, row, startCol, _replaceRemoveRadio, L10NFindAndReplace.REPLACE_TAGSREMOVE_LABEL, _replaceRemoveTags.getView() );
        _replaceReplaceTags = new TxnTagsPicker(_controller.getMDGUI(), _model.getData());
        _replaceReplaceRadio = new JRadioButton();
        row = addRowField3( replacePanel, row, startCol, _replaceReplaceRadio, L10NFindAndReplace.REPLACE_TAGSREPLACE_LABEL, _replaceReplaceTags.getView() );

        _replaceTagsGroup = new ButtonGroup();
        _replaceTagsGroup.add(_replaceAddRadio);
        _replaceTagsGroup.add(_replaceRemoveRadio);
        _replaceTagsGroup.add(_replaceReplaceRadio);

       // memo
        _replaceMemoCheck = new JCheckBox();
        row = addRowLabel( replacePanel, row, L10NFindAndReplace.REPLACE_MEMO_LABEL,
                L10NFindAndReplace.REPLACE_MEMO_MNC, _replaceMemoCheck );
        _replaceMemo = new JTextField();
        row = addRowField1( replacePanel, row, startCol, _replaceMemo );

        final JPanel buttonPanel = createUpperButtonPanel();
        replacePanel.add( buttonPanel, new TableLayoutConstraints( 0, row, 5, row,
                TableLayoutConstants.RIGHT, TableLayoutConstants.FULL ) );

        buildReplacePanelActions();
        return replacePanel;
    } // createReplacePanel()

    private void buildReplacePanelActions()
    {
        _replaceCategory.addItemListener(new ItemListener()
        {
            public void itemStateChanged(ItemEvent e)
            {
                _controller.setReplaceCategory(true);
            }
        });
        _replaceCategoryCheck.addItemListener(new ItemListener()
        {
            public void itemStateChanged(final ItemEvent event)
            {
                _controller.setReplaceCategory(event.getStateChange() == ItemEvent.SELECTED);
            }
        });

        _replaceAmount.getDocument().addDocumentListener(new DocumentListener()
        {
            public void insertUpdate(DocumentEvent e)
            {
                _controller.setReplaceAmount(true);
            }
            public void removeUpdate(DocumentEvent e)
            {
                _controller.setReplaceAmount(true);
            }

            public void changedUpdate(DocumentEvent e) { }
        });
        _replaceAmountCheck.addItemListener(new ItemListener()
        {
            public void itemStateChanged(final ItemEvent event)
            {
                _controller.setReplaceAmount(event.getStateChange() == ItemEvent.SELECTED);
            }
        });

        _replaceDescription.getDocument().addDocumentListener(new DocumentListener()
        {
            public void insertUpdate(DocumentEvent e)
            {
                _controller.setReplaceDescription(true);
            }
            public void removeUpdate(DocumentEvent e)
            {
                _controller.setReplaceDescription(true);
            }

            public void changedUpdate(DocumentEvent e) { }
        });
        _replaceDescriptionCheck.addItemListener(new ItemListener()
        {
            public void itemStateChanged(final ItemEvent event)
            {
                _controller.setReplaceDescription(event.getStateChange() == ItemEvent.SELECTED);
            }
        });

        _replaceMemo.getDocument().addDocumentListener(new DocumentListener()
        {
            public void insertUpdate(DocumentEvent e)
            {
                _controller.setReplaceMemo(true);
            }
            public void removeUpdate(DocumentEvent e)
            {
                _controller.setReplaceMemo(true);
            }

            public void changedUpdate(DocumentEvent e) { }
        });
        _replaceMemoCheck.addItemListener(new ItemListener()
        {
            public void itemStateChanged(final ItemEvent event)
            {
                _controller.setReplaceMemo(event.getStateChange() == ItemEvent.SELECTED);
            }
        });

        _replaceTagsCheck.addItemListener(new ItemListener()
        {
            public void itemStateChanged(final ItemEvent event)
            {
                _controller.setReplaceTags(event.getStateChange() == ItemEvent.SELECTED);
            }
        });

        _replaceAddTags.getView().addSelectionListener(new ActionListener()
        {
            public void actionPerformed(final ActionEvent event)
            {
                // notify that tags will be used
                _controller.setReplaceTags(true);
                _replaceAddRadio.setSelected(true);
            }
        });
        _replaceRemoveTags.getView().addSelectionListener(new ActionListener()
        {
            public void actionPerformed(final ActionEvent event)
            {
                // notify that tags will be used
                _controller.setReplaceTags(true);
                _replaceRemoveRadio.setSelected(true);
            }
        });
        _replaceReplaceTags.getView().addSelectionListener(new ActionListener()
        {
            public void actionPerformed(final ActionEvent event)
            {
                // notify that tags will be used
                _controller.setReplaceTags(true);
                _replaceReplaceRadio.setSelected(true);
            }
        });

    }

    private void saveReplaceEdits()
    {
        Account selectedAccount = null;
        if (_replaceCategory instanceof AccountChoice)
        {
            selectedAccount = ((AccountChoice)_replaceCategory).getSelectedAccount();
        }
        _controller.setReplacementCategory(selectedAccount);

        _controller.setReplacementAmount(_replaceAmount.getValue());
        _controller.setReplacementDescription(_replaceDescription.getText());
        _controller.setReplacementMemo(_replaceMemo.getText());

        final ButtonModel selectedTagAction = _replaceTagsGroup.getSelection();
        if (selectedTagAction != null)
        {
            ReplaceTagCommandType commandType;
            if (selectedTagAction.equals(_replaceAddRadio.getModel()))
            {
                commandType = ReplaceTagCommandType.ADD;
            }
            else if (selectedTagAction.equals(_replaceRemoveRadio.getModel()))
            {
                commandType = ReplaceTagCommandType.REMOVE;
            }
            else
            {
                commandType = ReplaceTagCommandType.REPLACE;
            }
            _controller.setReplaceTagType(commandType);
        }

        // update tags
        _replaceAddTags.updateFromView();
        _replaceRemoveTags.updateFromView();
        _replaceReplaceTags.updateFromView();
    }

    private void updateSummary()
    {
        String format = _controller.getString(L10NFindAndReplace.RESULTS_SUMMARY_FMT);
        FindResultsTableModel results = _model.getFindResults();
        final int count = results.getRowCount();
        long minuses = 0;
        long plusses = 0;
        for (int modelIndex = 0; modelIndex < count; modelIndex++)
        {
            // if the user unchecks the box, remove that from the results value
            if (results.getEntry(modelIndex).isUseInReplace())
            {
                long value = results.getAmount(modelIndex);
                if (value >= 0)
                {
                    plusses += value;
                }
                else
                {
                    minuses += value;
                }
            }
        }

        long total = plusses + minuses;

        int displayCount = count;
        if ((count == 1) && (results.isBlankEntry(results.getEntry(0))))
        {
            displayCount = 0;
        }
        String countDisplay = Integer.toString(displayCount);
        String adds = results.getAmountText(null, plusses);
        String subtracts = results.getAmountText(null, minuses);
        String totalDisplay = results.getAmountText(null, total);
        String result = String.format(format, countDisplay, adds, subtracts, totalDisplay);
        _summary.setText(result);
    }


    private int addRowLabel(JPanel panel, int rowNum, String labelKey, String labelMnemonicKey,
                            JCheckBox check)
    {
        TableLayoutConstraints constraints = new TableLayoutConstraints(0, rowNum);
        JLabel label = new JLabel( FarUtil.getLabelText(_controller, labelKey ) );
        label.setHorizontalAlignment( SwingConstants.RIGHT );
        String mnemonic = _controller.getString( labelMnemonicKey );
        if ( (mnemonic != null) && (mnemonic.length() > 0) )
        {
            label.setDisplayedMnemonic( mnemonic.charAt( 0 ) );
            check.setMnemonic( mnemonic.charAt( 0 ) );
        }
        panel.add( label, constraints );
        constraints = new TableLayoutConstraints(1, rowNum);
        panel.add( check, constraints );
        return rowNum;
    }

    private int addRowField1( JPanel panel, int rowNum, int startCol, JComponent field )
    {
        TableLayoutConstraints constraints = new TableLayoutConstraints(startCol, rowNum, startCol+3, rowNum);
        panel.add( field, constraints );
        return rowNum + 2;
    }

    private int addRowField3(JPanel panel, int rowNum, int startCol, JComponent field1,
                            String labelKey, JComponent field2)
    {
        TableLayoutConstraints constraints = new TableLayoutConstraints(startCol, rowNum, startCol+1, rowNum);
        panel.add( field1, constraints );
        constraints = new TableLayoutConstraints(startCol+2, rowNum);
        JLabel label = new JLabel( _controller.getString( labelKey ) );
        label.setHorizontalAlignment( SwingConstants.RIGHT );
        label.setBorder( new EmptyBorder( 0, UiUtil.HGAP, 0, UiUtil.HGAP) );
        panel.add( label, constraints );
        constraints = new TableLayoutConstraints(startCol+3, rowNum);
        panel.add( field2, constraints );
        return rowNum + 2;
    }

    private JPanel createUpperButtonPanel()
    {
        final double[][] sizes = new double[][]
        {
            // columns
            {
                TableLayout.FILL, TableLayout.PREFERRED,
                UiUtil.HGAP, TableLayout.PREFERRED,
                UiUtil.HGAP, TableLayout.PREFERRED
            },
            // rows
            { TableLayout.PREFERRED }
        };
        final JPanel buttons = new JPanel( new TableLayout( sizes ) );

        buttons.add( _findButton, UiUtil.createTableConstraintBtnR(1, 0) );
        buttons.add( _replaceButton, UiUtil.createTableConstraintBtnR(3, 0) );
        buttons.add( _replaceAllButton, UiUtil.createTableConstraintBtnR(5, 0) );

        return buttons;
    }

    private JPanel createLowerRightButtonPanel()
    {
        final double[][] sizes = new double[][]
        {
            // columns
            {
                TableLayout.PREFERRED, UiUtil.HGAP, TableLayout.PREFERRED
            },
            // rows
            { TableLayout.PREFERRED }
        };
        final JPanel buttons = new JPanel( new TableLayout( sizes ) );

        buttons.add( _recordButton, UiUtil.createTableConstraintBtnR(0, 0) );
        buttons.add( _closeButton, UiUtil.createTableConstraintBtnR(2, 0) );

        return buttons;
    }

    private JPanel createLowerLeftButtonPanel()
    {
        final double[][] sizes = new double[][]
        {
            // columns
            {
                TableLayout.PREFERRED, UiUtil.HGAP, TableLayout.PREFERRED
            },
            // rows
            { TableLayout.PREFERRED }
        };
        final JPanel buttons = new JPanel( new TableLayout( sizes ) );

        buttons.add(_markAllButton, UiUtil.createTableConstraintBtnL(0, 0) );
        buttons.add(_markNoneButton, UiUtil.createTableConstraintBtnL(2, 0) );

        return buttons;
    }

}

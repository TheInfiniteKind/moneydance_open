/*************************************************************************\
* Copyright (C) 2009-2013 Mennē Software Solutions, LLC
*
* This code is released as open source under the Apache 2.0 License:<br/>
* <a href="http://www.apache.org/licenses/LICENSE-2.0">
* http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/

package com.moneydance.modules.features.findandreplace;

import com.moneydance.apps.md.model.CurrencyType;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.moneydance.apps.md.view.gui.MoneydanceLAF;
import com.moneydance.apps.md.view.gui.SecondaryFrame;
import com.moneydance.apps.md.view.gui.TagLogic;
import com.moneydance.awt.AwtUtil;
import com.moneydance.apps.md.view.gui.AccountChoice;
import com.moneydance.apps.md.model.Account;

import javax.swing.event.ListSelectionEvent;
import javax.swing.event.ListSelectionListener;
import javax.swing.table.JTableHeader;
import javax.swing.table.TableColumn;
import javax.swing.border.EmptyBorder;
import javax.swing.*;
import javax.swing.event.DocumentListener;
import javax.swing.event.DocumentEvent;
import java.awt.Container;
import java.awt.FlowLayout;
import java.awt.FontMetrics;
import java.awt.event.FocusListener;
import java.beans.PropertyChangeListener;
import java.beans.PropertyChangeEvent;
import java.awt.event.ActionListener;
import java.awt.event.ActionEvent;
import java.awt.event.WindowEvent;
import java.awt.event.ItemListener;
import java.awt.event.ItemEvent;
import java.awt.event.KeyEvent;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.awt.event.FocusAdapter;
import java.awt.event.FocusEvent;
import java.awt.BorderLayout;
import java.awt.Dimension;
import java.awt.Toolkit;
import java.awt.Font;
import java.awt.Cursor;
import java.awt.GridLayout;
import java.awt.Color;
import java.awt.Component;
import java.util.regex.Pattern;
import java.util.regex.PatternSyntaxException;
import java.text.MessageFormat;

import com.moneydance.util.StringUtils;
import info.clearthought.layout.TableLayout;
import info.clearthought.layout.TableLayoutConstraints;
import info.clearthought.layout.TableLayoutConstants;

/**
 * <p>The main view for the Find and Replace plugin. Has all the find and replace controls and
 * hosts the results table as well.</p>
 *
 * @author Kevin Menningen
 * @version Build 94
 * @since 1.0
 */
class FarView extends SecondaryFrame implements PropertyChangeListener
{
    private final FarModel _model;
    private FarController _controller;

    private JRadioButton _findAndRadio;
    private JRadioButton _findOrRadio;
    private ButtonGroup _findBooleanGroup;

    private JCheckBox _findAccountsUseCheck;
    private JLabel _findAccountsList;
    private JButton _findAccountsSelect;

    private JCheckBox _findCategoryUseCheck;
    private JLabel _findCategoryList;
    private JButton _findCategorySelect;

    private JCheckBox _findAmountUseCheck;
    private AmountPickerGroup _findAmountPickers;

    private JCheckBox _findDateUseCheck;
    private DatePickerGroup _findDatePickers;
    private JCheckBox _useTaxDate;

    private JCheckBox _findFreeTextUseCheck;
    private JCheckBox _findFreeTextUseDescriptionCheck;
    private JCheckBox _findFreeTextUseMemoCheck;
    private JCheckBox _findFreeTextUseCheckCheck;
    private JCheckBox _findFreeTextIncludeSplitsCheck;
    private JTextField _findFreeText;

    private JCheckBox _findTagsUseCheck;
    private TxnTagsPicker _findTagPicker;
    private JRadioButton _tagsAnd;
    private JRadioButton _tagsOr;
    private JRadioButton _tagsExact;

    private JCheckBox _findClearedUseCheck;
    private JCheckBox _findClearedClearedCheck;
    private JCheckBox _findClearedReconcilingCheck;
    private JCheckBox _findClearedUnclearedCheck;

    // replace panel
    // we replace the category chooser on-the-fly so we need to track its parent and constraints
    private JPanel _replacePanel;
    private JCheckBox _replaceCategoryCheck;
    private JComboBox _replaceCategory;
    private TableLayoutConstraints _replaceCategoryConstraints;

    private JCheckBox _replaceAmountCheck;
    private AmountPickerGroup _replaceAmount;
    private JCheckBox _replaceDescriptionCheck;
    private JTextField _replaceDescription;
    private JCheckBox _replaceFoundDescriptionOnly;
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
    private JCheckBox _replaceFoundMemoOnly;
    private JCheckBox _replaceCheckCheck;
    private JTextField _replaceCheck;
    private JCheckBox _replaceFoundCheckOnly;

    private JCheckBox _includeTransfersCheck;
    private JCheckBox _showParentsCheck;
    private JCheckBox _splitsAsMemosCheck;
    private JTable _findResults;
    private JLabel _summary;

    // buttons
    private JButton _findButton;
    private JButton _replaceButton;
    private JButton _replaceAllButton;
    private JButton _recordButton;
    private JButton _closeButton;
    private JButton _resetButton;
    private JButton _markAllButton;
    private JButton _markNoneButton;
    private JButton _gotoButton;
    private JButton _copyButton;

    private Color _focusColor;

    // don't automatically check the 'use' boxes when updating programmatically
    private boolean _suppressAutoCheckUse = false;
    private JLabel _statusLabel;
    private Font _smallFont;

    FarView(final FarModel model, MoneydanceGUI mdGui, String title)
    {
        super(mdGui, title);
        _model = model;
    }

    @Override
    public void setVisible(boolean vis)
    {
        if (vis)
        {
            // default focus first time the window is displayed
            _findFreeText.requestFocusInWindow();
        }
        super.setVisible(vis);
    }

    public void goneAway()
    {
        super.goneAway();
        _findAmountPickers.cleanUp();
        _replaceAmount.cleanUp();
    }



    ///////////////////////////////////////////////////////////////////////////////////////////////
    // Package Private Methods
    ///////////////////////////////////////////////////////////////////////////////////////////////

    void layoutUI()
    {
        // initial focus is on the free text field, as it is the most commonly used
        setFocusTraversalPolicy(new FarFocusTraversalPolicy());
        // The frame itself should not receive focus. However, making this call prevents the Tab key
        // from working on very recent JRE editions. Therefore the call is removed and the user must
        // press Tab once to get focus.
//        setFocusable(false);

        _focusColor = new Color(255, 255, 180); // light yellow
        this.setIconImage(_controller.getImage(L10NFindAndReplace.FAR_IMAGE));
        
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

        JPanel bottomPanel = new JPanel(new BorderLayout());
        bottomPanel.add(createLowerLeftButtonPanel(), BorderLayout.WEST);
        bottomPanel.add(createLowerRightButtonPanel(), BorderLayout.EAST);

        JPanel centerPanel = new JPanel(new FlowLayout(FlowLayout.CENTER, UiUtil.HGAP, 0));
        JButton userGuide = new JButton(_controller.getString(L10NFindAndReplace.USER_GUIDE));
        userGuide.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent event) {
                FarUtil.launchUserGuide();
            }
        });
        mdGUI.applyFilterBarProperties(userGuide);
        centerPanel.add(userGuide);
        
        _statusLabel = new JLabel(getVersionText());
        setupControl(_statusLabel);
        _statusLabel.setHorizontalAlignment(JLabel.CENTER);
        _statusLabel.setVerticalAlignment(JLabel.BOTTOM);
        _smallFont = _statusLabel.getFont().deriveFont(_statusLabel.getFont().getSize() - 2f);
        _statusLabel.setFont(_smallFont);
        _statusLabel.setEnabled(false);
        centerPanel.add(_statusLabel);
        bottomPanel.add(centerPanel, BorderLayout.CENTER);

        main.add(bottomPanel, new TableLayoutConstraints(0, 4, 2, 4));
        getContentPane().add( main );
        updateFoundOnlyControls();

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
        if (event.getID() == WindowEvent.WINDOW_OPENED)
        {
            // make sure the row size has enough room for the font
            final float currentSize = _summary.getFont().getSize2D();
            final Font bold = _summary.getFont().deriveFont(Font.BOLD, currentSize + 2f);
            final FontMetrics fm = getGraphics().getFontMetrics(bold);
            _findResults.setRowHeight(fm.getHeight());
            // disable menu options that don't apply
            disableMenus();
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

        // when we set values programmatically we don't automatically set the 'use' checkboxes
        // and we have to check for recursion in case properties get set from within a suppressed
        // update
        final boolean enterSuppressed = !_suppressAutoCheckUse && all;
        if (enterSuppressed)
        {
            _suppressAutoCheckUse = true;
        }

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
            _findAccountsList.setText(_controller.getAccountListDisplay(mdGUI));
        }
        if (all || N12EFindAndReplace.ACCOUNT_USE.equals(eventID))
        {
            _findAccountsUseCheck.setSelected(_controller.getUseAccountFilter());
        }
        if (all || N12EFindAndReplace.CATEGORY_SELECT.equals(eventID))
        {
            _findCategoryList.setText(_controller.getCategoryListDisplay(mdGUI));
        }
        if (all || N12EFindAndReplace.CATEGORY_USE.equals(eventID))
        {
            _findCategoryUseCheck.setSelected(_controller.getUseCategoryFilter());
        }
        if (all || N12EFindAndReplace.AMOUNT_USE.equals(eventID))
        {
            _findAmountUseCheck.setSelected(_controller.getUseAmountFilter());
        }
        if (all || N12EFindAndReplace.FIND_AMOUNT_CURRENCY.equals(eventID))
        {
            final CurrencyType currencyType = all ? _controller.getAmountCurrency() :
                    (CurrencyType)event.getNewValue();
            if (currencyType != null)
            {
                _findAmountPickers.setCurrencyType(currencyType);
            }
        }
        if (all || N12EFindAndReplace.DATE_USE.equals(eventID))
        {
            _findDateUseCheck.setSelected(_controller.getUseDateFilter());
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

        if (all || N12EFindAndReplace.TAGS_USE.equals(eventID))
        {
            _findTagsUseCheck.setSelected(_controller.getUseTagsFilter());
        }
        if (all || N12EFindAndReplace.TAGS_LOGIC.equals(eventID))
        {
            final TagLogic combineLogic = _controller.getRequireTagsFilter();
            if (TagLogic.EXACT.equals(combineLogic))
            {
                _tagsExact.setSelected(true);
            }
            else if (TagLogic.AND.equals(combineLogic))
            {
                _tagsAnd.setSelected(true);
            }
            else
            {
                _tagsOr.setSelected(true);
            }
        }
        
        if (all || N12EFindAndReplace.CLEARED_USE.equals(eventID))
        {
            _findClearedUseCheck.setSelected(_controller.getUseClearedFilter());
        }
        if (all || N12EFindAndReplace.CLEARED_CLEARED.equals(eventID))
        {
            _findClearedClearedCheck.setSelected(_controller.getAllowCleared());
        }
        if (all || N12EFindAndReplace.CLEARED_RECONCILING.equals(eventID))
        {
            _findClearedReconcilingCheck.setSelected(_controller.getAllowReconciling());
        }
        if (all || N12EFindAndReplace.CLEARED_UNCLEARED.equals(eventID))
        {
            _findClearedUnclearedCheck.setSelected(_controller.getAllowUncleared());
        }
 
        // replacement
        if (all || N12EFindAndReplace.REPLACE_CATEGORY.equals(eventID))
        {
            final boolean replaceCategory = _controller.getReplaceCategory();
            _replaceCategoryCheck.setSelected(replaceCategory);
        }
        if (all || N12EFindAndReplace.REPLACE_AMOUNT.equals(eventID))
        {
            _replaceAmountCheck.setSelected(_controller.getReplaceAmount());
        }
        if (all || N12EFindAndReplace.REPL_AMOUNT_CURRENCY.equals(eventID))
        {
            final CurrencyType currencyType = all ? _controller.getReplaceAmountCurrency() :
                    (CurrencyType)event.getNewValue();
            if (currencyType != null)
            {
                _replaceAmount.setCurrencyType(currencyType);
            }
        }
        if (all || N12EFindAndReplace.REPLACE_DESCRIPTION.equals(eventID))
        {
            _replaceDescriptionCheck.setSelected(_controller.getReplaceDescription());
        }
        if (all || N12EFindAndReplace.REPLACE_FOUND_DESCRIPTION_ONLY.equals(eventID))
        {
            _replaceFoundDescriptionOnly.setSelected(_controller.getReplaceFoundDescriptionOnly());
        }
        if (all || N12EFindAndReplace.REPLACE_MEMO.equals(eventID))
        {
            _replaceMemoCheck.setSelected(_controller.getReplaceMemo());
        }
        if (all || N12EFindAndReplace.REPLACE_FOUND_MEMO_ONLY.equals(eventID))
        {
            _replaceFoundMemoOnly.setSelected(_controller.getReplaceFoundMemoOnly());
        }
        if (all || N12EFindAndReplace.REPLACE_CHECK.equals(eventID))
        {
            _replaceCheckCheck.setSelected(_controller.getReplaceCheck());
        }
        if (all || N12EFindAndReplace.REPLACE_FOUND_CHECK_ONLY.equals(eventID))
        {
            _replaceFoundCheckOnly.setSelected(_controller.getReplaceFoundCheckOnly());
        }
        if (all || N12EFindAndReplace.REPLACE_TAGS.equals(eventID))
        {
            final boolean replaceTags = _controller.getReplaceTags();
            _replaceTagsCheck.setSelected(replaceTags);
            if (replaceTags)
            {
                switch (_controller.getReplaceTagType())
                {
                    case ADD:
                    {
                        _replaceAddRadio.setSelected(true);
                        break;
                    }
                    case REMOVE:
                    {
                        _replaceRemoveRadio.setSelected(true);
                        break;
                    }
                    case REPLACE:
                    {
                        _replaceReplaceRadio.setSelected(true);
                        break;
                    }
                }
            }
            else
            {
                _replaceTagsGroup.clearSelection();
            }
        }

        if (all || N12EFindAndReplace.FIND_RESULTS_UPDATE.equals(eventID))
        {
            updateSummary();
            _findResults.repaint();
        }
        if (all || N12EFindAndReplace.INCLUDE_TRANSFERS.equals(eventID))
        {
            _includeTransfersCheck.setSelected(_controller.getIncludeTransfers());
            buildReplaceCategoryChooser();
        }
        if (all || N12EFindAndReplace.SHOW_PARENTS.equals(eventID))
        {
            _showParentsCheck.setSelected(_controller.getShowParents());
            updateSummary();
            _findResults.repaint();
        }
        if (all || N12EFindAndReplace.SPLITS_AS_MEMOS.equals(eventID))
        {
            _splitsAsMemosCheck.setSelected(_controller.getSplitsAsMemos());
            _findResults.repaint();
        }

        if (all)
        {
            TagPickerModel tagModel = _controller.getIncludedTagsModel();
            _findTagPicker.setModel(tagModel);

            tagModel = _controller.getReplaceAddTagsModel();
            _replaceAddTags.setModel(tagModel);

            tagModel = _controller.getReplaceRemoveTagsModel();
            _replaceRemoveTags.setModel(tagModel);

            tagModel = _controller.getReplaceReplaceTagsModel();
            _replaceReplaceTags.setModel(tagModel);

            _findFreeText.setText(_controller.getFreeTextMatch());
            _findAmountPickers.getFromAmountPicker().setValue(_controller.getAmountMinimum());
            _findAmountPickers.getToAmountPicker().setValue(_controller.getAmountMaximum());
            String dateRangeKey = _controller.getDateRangeKey();
            if (StringUtils.isBlank(dateRangeKey) ||
                    DateRangeOption.DR_CUSTOM_DATE.getResourceKey().equals(dateRangeKey))
            {
                // custom date, use saved dates
                _findDatePickers.setDateRangeKey(DateRangeOption.DR_CUSTOM_DATE.getResourceKey());
                _findDatePickers.getFromDatePicker().setDateInt(_controller.getDateMinimum());
                _findDatePickers.getToDatePicker().setDateInt(_controller.getDateMaximum());
            }
            else
            {
                // pre-defined date, set the pre-defined date and let the control calculate the
                // appropriate min and max dates
                _findDatePickers.setDateRangeKey(dateRangeKey);
            }
            _useTaxDate.setSelected(_controller.getUseTaxDate());

            _replaceDescription.setText(_controller.getReplacementDescription());
            _replaceMemo.setText(_controller.getReplacementMemo());
            _replaceCheck.setText(_controller.getReplacementCheck());
            _replaceAmount.getToAmountPicker().setValue(_controller.getReplacementAmount());
        }

        // clear the update suppression
        if (enterSuppressed)
        {
            _suppressAutoCheckUse = false;
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
        if ((freeText != null) && (freeText.length() > 0))
        {
            if (validateFreeText(freeText))
            {
                _controller.setFreeTextMatch(freeText);
                // this will fire an update
                _findFreeText.setText(freeText);
                _findFreeTextUseCheck.setSelected(true);
            }
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
        final JPanel resultsPanel = new JPanel(new BorderLayout());
        final JLabel panelLabel = setupControl( new JLabel(_controller.getString(L10NFindAndReplace.RESULTS_LABEL)) );
        final JPanel headerPanel = setupControl( new JPanel(new BorderLayout()) );
        final float currentSize = panelLabel.getFont().getSize2D();
        final Font bold = panelLabel.getFont().deriveFont(Font.BOLD, currentSize + 1.5f);
        panelLabel.setFont( bold );
        headerPanel.add(panelLabel, BorderLayout.WEST);
        JPanel modePanel = new JPanel(new FlowLayout(FlowLayout.CENTER, UiUtil.HGAP*2, 0));
        _showParentsCheck = setupControl( new JCheckBox(_controller.getString(L10NFindAndReplace.CONSOLIDATE_SPLITS)) );
        _showParentsCheck.setToolTipText(_controller.getString(L10NFindAndReplace.CONSOLIDATE_SPLITS_TIP));
        _showParentsCheck.setHorizontalAlignment(JCheckBox.CENTER);
        addKeystrokeToButton(_showParentsCheck, L10NFindAndReplace.CONSOLIDATE_SPLITS_MNC, false);
        modePanel.add(_showParentsCheck);
        _showParentsCheck.addItemListener(new ItemListener()
        {
            public void itemStateChanged(final ItemEvent event)
            {
                final boolean showParents = event.getStateChange() == ItemEvent.SELECTED;
                _controller.setShowParents(showParents);
                if (showParents)
                {
                    _controller.setSplitsAsMemos(false);
                }
                _splitsAsMemosCheck.setEnabled(!showParents);
            }
        });
        _splitsAsMemosCheck = setupControl( new JCheckBox(_controller.getString(L10NFindAndReplace.SPLITS_AS_MEMOS)) );
        _splitsAsMemosCheck.setToolTipText(_controller.getString(L10NFindAndReplace.SPLITS_AS_MEMOS_TIP));
        _splitsAsMemosCheck.setHorizontalAlignment(JCheckBox.CENTER);
        addKeystrokeToButton(_splitsAsMemosCheck, L10NFindAndReplace.SPLITS_AS_MEMOS_MNC, true);
        modePanel.add(_splitsAsMemosCheck, BorderLayout.CENTER);
        _splitsAsMemosCheck.addItemListener(new ItemListener()
        {
            public void itemStateChanged(final ItemEvent event)
            {
                final boolean useSplitDescriptionAsMemo = event.getStateChange() == ItemEvent.SELECTED;
                _controller.setSplitsAsMemos(useSplitDescriptionAsMemo);
                if (useSplitDescriptionAsMemo)
                {
                    _controller.setShowParents(false);
                }
                _showParentsCheck.setEnabled(!useSplitDescriptionAsMemo);
            }
        });
        headerPanel.add(modePanel, BorderLayout.CENTER);

        _summary = setupControl( new JLabel() );
        headerPanel.add(_summary, BorderLayout.EAST);
        resultsPanel.add(headerPanel, BorderLayout.NORTH);

        final FindResultsTableColumnModel columnModel = new FindResultsTableColumnModel(_controller);

        _findResults = new FindResultsTable(_model.getFindResults());
        _findResults.setColumnModel(columnModel);
        _findResults.setFillsViewportHeight(true);
        _findResults.setShowGrid(false);
        _findResults.setTableHeader(new JTableHeader(columnModel));
        _findResults.setDefaultRenderer(TableColumn.class, new FindResultsTableCellRenderer());
        columnModel.setTableSelectionModel(_findResults.getSelectionModel());
        _findResults.addMouseListener(new MouseAdapter()
        {
            @Override
            public void mouseClicked(MouseEvent e)
            {
                if (SwingUtilities.isLeftMouseButton(e) && (e.getClickCount() > 1))
                {
                    goToSelectedTransaction();
                }
            }
        });
        _findResults.getSelectionModel().addListSelectionListener(new ListSelectionListener()
        {
            public void valueChanged(ListSelectionEvent event)
            {
                // If the user single selects a row, consider that the starting point for replace
                // operations. Replace All will ignore this, but Replace will use it.
                final int min = _findResults.getSelectionModel().getMinSelectionIndex();
                final int max = _findResults.getSelectionModel().getMaxSelectionIndex();
                if (!event.getValueIsAdjusting() && (min == max) && (min != -1))
                {
                    // this is where the user wants to start replacing
                    _controller.setReplaceViewIndex(min);
                }
            }
        });

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

        resultsPanel.add(new JScrollPane(_findResults), BorderLayout.CENTER);
        return resultsPanel;
    }

    private void goToSelectedTransaction()
    {
        final int selectedRow = _findResults.getSelectedRow();
        if ((selectedRow >= 0) && (selectedRow < _findResults.getRowCount()))
        {
            final int modelIndex = _findResults.convertRowIndexToModel(selectedRow);
            _controller.gotoTransaction(modelIndex);
        }
    }

    private void setupButtons()
    {
        _findButton = createButton(L10NFindAndReplace.FIND_BUTTON_TEXT,
                L10NFindAndReplace.FIND_BUTTON_MNC, false);
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
                L10NFindAndReplace.REPLACE_BUTTON_MNC, true);
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
                L10NFindAndReplace.REPLACEALL_BUTTON_MNC, true);
        _replaceAllButton.addActionListener(new ActionListener()
        {
            public void actionPerformed(final ActionEvent event)
            {
                setProgressText();
                saveReplaceEdits();
                _controller.replaceAll();
                clearProgressText();
            }
        });

        _closeButton = createButton(L10NFindAndReplace.DONE, null, false);
        _closeButton.addActionListener(new ActionListener()
        {
            public void actionPerformed(final ActionEvent event)
            {
                _controller.hide();
            }
        });

        _recordButton = createButton(L10NFindAndReplace.RECORD_BUTTON_TEXT, null, false);
        _recordButton.addActionListener(new ActionListener()
        {
            public void actionPerformed(final ActionEvent event)
            {
                setProgressText();
                _controller.commit();
                // clear the results and run find again to revert colors
                _controller.find();
                clearProgressText();
            }
        });

        _resetButton = createButton(L10NFindAndReplace.RESET_BUTTON_TEXT, null, false);
        _resetButton.addActionListener(new ActionListener()
        {
            public void actionPerformed(final ActionEvent event)
            {
                _controller.reset();
            }
        });

        _markAllButton = createButton(L10NFindAndReplace.MARK_ALL_BUTTON_TEXT,
                                      L10NFindAndReplace.MARK_ALL_BUTTON_MNC, false);
        _markAllButton.addActionListener(new ActionListener()
        {
            public void actionPerformed(final ActionEvent event)
            {
                _controller.markAll();
            }
        });

        _markNoneButton = createButton(L10NFindAndReplace.MARK_NONE_BUTTON_TEXT,
                                       L10NFindAndReplace.MARK_NONE_BUTTON_MNC, false);
        _markNoneButton.addActionListener(new ActionListener()
        {
            public void actionPerformed(final ActionEvent event)
            {
                _controller.markNone();
            }
        });

        _gotoButton = createButton(L10NFindAndReplace.GOTO_BUTTON_TEXT,
                L10NFindAndReplace.GOTO_BUTTON_MNC, false);
        _gotoButton.addActionListener(new ActionListener()
        {
            public void actionPerformed(final ActionEvent event)
            {
                goToSelectedTransaction();
            }
        });

        _copyButton = createButton(L10NFindAndReplace.COPY_BUTTON_TEXT,
                L10NFindAndReplace.COPY_BUTTON_MNC, false);
        _copyButton.addActionListener(new ActionListener()
        {
            public void actionPerformed(final ActionEvent event)
            {
                _controller.copyToClipboard();
            }
        });

    }

    private JButton createButton(final String buttonTextKey, final String buttonMnemonicKey,
                                 final boolean addShift)
    {
        final JButton button = new JButton( _controller.getString(buttonTextKey) );
        if (buttonMnemonicKey != null)
        {
            addKeystrokeToButton(button, buttonMnemonicKey, addShift);
        }
        return button;
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
                // Panel label, combine criteria
                TableLayout.PREFERRED, UiUtil.VGAP, TableLayout.PREFERRED, UiUtil.VGAP,
                // account select, category select
                TableLayout.PREFERRED, UiUtil.VGAP, TableLayout.PREFERRED, UiUtil.VGAP,
                //  amount, date
                TableLayout.PREFERRED, UiUtil.VGAP, TableLayout.PREFERRED, UiUtil.VGAP,
                // free text, free text options
                TableLayout.PREFERRED, 0, TableLayout.PREFERRED, UiUtil.VGAP,
                // tags, tag options
                TableLayout.PREFERRED, 0, TableLayout.PREFERRED, UiUtil.VGAP,
                // cleared
                TableLayout.PREFERRED
            }
        };
        final JPanel findPanel = new JPanel(new TableLayout(sizes));
        int row = 0;
        final JLabel panelLabel = setupControl( new JLabel( _controller.getString( L10NFindAndReplace.FIND_LABEL )) );
        final float currentSize = panelLabel.getFont().getSize2D();
        final Font bold = panelLabel.getFont().deriveFont(Font.BOLD, currentSize + 1.5f);
        panelLabel.setFont( bold );
        findPanel.add(panelLabel, new TableLayoutConstraints(0, row));
        
        LoadSaveView loadSaveView = new LoadSaveView(mdGUI, _controller);
        findPanel.add(loadSaveView, new TableLayoutConstraints(6, row));
        row += 2; // skip the gap

        // the combine criteria row is a little special -- the only 2 component field set and no
        // check box
        JLabel label = setupControl( new JLabel(
                FarUtil.getLabelText(_controller, L10NFindAndReplace.FIND_BOOL_LABEL) ) );
        findPanel.add(label, new TableLayoutConstraints(0, row));
        _findAndRadio = setupControl(
                new JRadioButton( _controller.getString( L10NFindAndReplace.FIND_BOOL_AND ) ) );
        addKeystrokeToButton( _findAndRadio, L10NFindAndReplace.FIND_BOOL_AND_MNC, true);
        findPanel.add(_findAndRadio, new TableLayoutConstraints(3, row, 4, row,
                                                                TableLayoutConstants.CENTER, TableLayoutConstants.FULL));
        _findOrRadio = setupControl( new JRadioButton( _controller.getString( L10NFindAndReplace.FIND_BOOL_OR ) ) );
        addKeystrokeToButton( _findOrRadio, L10NFindAndReplace.FIND_BOOL_OR_MNC, true );
        findPanel.add(_findOrRadio, new TableLayoutConstraints(5, row, 6, row,
                                                               TableLayoutConstants.CENTER, TableLayoutConstants.FULL));

        _findBooleanGroup = new ButtonGroup();
        _findBooleanGroup.add( _findAndRadio );
        _findBooleanGroup.add( _findOrRadio );

        row += 2;

        final String findCheckTip = _controller.getString(L10NFindAndReplace.FIND_USE_TIP);

        // accounts row
        _findAccountsUseCheck = setupControl( new JCheckBox() );
        _findAccountsUseCheck.setToolTipText(findCheckTip);
        row = addRowLabel(findPanel, row, L10NFindAndReplace.FIND_ACCOUNTS_LABEL,
                L10NFindAndReplace.FIND_ACCOUNTS_MNC, _findAccountsUseCheck, false);
        _findAccountsList = setupControl( new JLabel() );
        findPanel.add(_findAccountsList, new TableLayoutConstraints(3, row, 5, row));
        _findAccountsSelect = createButton( L10NFindAndReplace.FIND_ACCOUNTS_SELECT_TEXT,
                L10NFindAndReplace.FIND_ACCOUNTS_SELECT_MNC, true );
        findPanel.add(_findAccountsSelect, new TableLayoutConstraints(6, row));
        row += 2;

        // category row
        _findCategoryUseCheck = setupControl( new JCheckBox() );
        _findCategoryUseCheck.setToolTipText(findCheckTip);
        row = addRowLabel(findPanel, row, L10NFindAndReplace.FIND_CATEGORIES_LABEL,
                L10NFindAndReplace.FIND_CATEGORIES_MNC, _findCategoryUseCheck, false);
        _findCategoryList = setupControl( new JLabel() );
        findPanel.add(_findCategoryList, new TableLayoutConstraints(3, row, 5, row));
        _findCategorySelect = createButton( L10NFindAndReplace.FIND_CATEGORIES_SELECT_TEXT,
                L10NFindAndReplace.FIND_CATEGORIES_SELECT_MNC, true );
        findPanel.add(_findCategorySelect, new TableLayoutConstraints(6, row));
        row += 2;

        // label plus 2 checkboxes
        final int startCol = 3;

        // amount row
        _findAmountUseCheck = setupControl( new JCheckBox() );
        _findAmountUseCheck.setToolTipText(findCheckTip);
        row = addRowLabel(findPanel, row, L10NFindAndReplace.FIND_AMOUNT_LABEL,
                L10NFindAndReplace.FIND_AMOUNT_MNC, _findAmountUseCheck, false);

        _findAmountPickers = new AmountPickerGroup(_controller, true, true);
        _findAmountPickers.addFocusListener(new ColoredFocusAdapter(
                _findAmountPickers.getFromAmountPicker(), _focusColor) );
        row = addRowField1(findPanel, row, startCol, _findAmountPickers );

        // date row
        _findDateUseCheck = setupControl( new JCheckBox() );
        _findDateUseCheck.setToolTipText(findCheckTip);
        row = addRowLabel(findPanel, row, L10NFindAndReplace.FIND_DATE_LABEL,
                L10NFindAndReplace.FIND_DATE_MNC, _findDateUseCheck, false);

        _findDatePickers = new DatePickerGroup(_controller.getMDGUI());
        _findDatePickers.addFocusListener(new ColoredFocusAdapter(
                _findDatePickers.getFromDatePicker(), _focusColor) );
        _useTaxDate = setupControl( new JCheckBox(_controller.getString(L10NFindAndReplace.USE_TAX_DATE)) );
        addKeystrokeToButton(_useTaxDate, L10NFindAndReplace.USE_TAX_DATE_MNC, false);
        row = addRowField2(findPanel, row, startCol, _findDatePickers, _useTaxDate);

        // free text
        _findFreeTextUseCheck = setupControl( new JCheckBox() );
        _findFreeTextUseCheck.setToolTipText(findCheckTip);
        row = addRowLabel(findPanel, row, L10NFindAndReplace.FIND_FREETEXT_LABEL,
                L10NFindAndReplace.FIND_FREETEXT_MNC, _findFreeTextUseCheck, false);
        _findFreeText = new JTextField();
        _findFreeText.addFocusListener(new ColoredFocusAdapter( _findFreeText, _focusColor) );
        row = addRowField1(findPanel, row, startCol, _findFreeText);

        _findFreeTextUseDescriptionCheck = setupControl( new JCheckBox(
                _controller.getString( L10NFindAndReplace.FIND_FREETEXT_DESCRIPTION )) );
        _findFreeTextUseDescriptionCheck.setToolTipText(
                _controller.getString(L10NFindAndReplace.FIND_FREETEXT_DESC_TIP));
        _findFreeTextUseDescriptionCheck.setEnabled(false);

        _findFreeTextUseMemoCheck = setupControl( new JCheckBox(
                _controller.getString( L10NFindAndReplace.FIND_FREETEXT_MEMO )) );
        _findFreeTextUseMemoCheck.setToolTipText(
                _controller.getString(L10NFindAndReplace.FIND_FREETEXT_MEMO_TIP));
        _findFreeTextUseMemoCheck.setEnabled(false);

        _findFreeTextUseCheckCheck = setupControl( new JCheckBox(
                _controller.getString( L10NFindAndReplace.FIND_FREETEXT_CHECK )) );
        _findFreeTextUseCheckCheck.setToolTipText(
                _controller.getString(L10NFindAndReplace.FIND_FREETEXT_CHECK_TIP));
        _findFreeTextUseCheckCheck.setEnabled(false);

        _findFreeTextIncludeSplitsCheck = setupControl( new JCheckBox(
                _controller.getString( L10NFindAndReplace.FIND_FREETEXT_SPLITS )) );
        _findFreeTextIncludeSplitsCheck.setToolTipText(
                _controller.getString(L10NFindAndReplace.FIND_FREETEXT_SPLITS_TIP));
        _findFreeTextIncludeSplitsCheck.setEnabled(false);

        // we use TableLayout here instead of GridLayout because TableLayout will size each column
        // according to the checkbox, whereas GridLayout will make the cells an equal size,
        // cutting off the text for the longer ones
        final double[][] checkSizes = new double[][]
        {
            // columns
            {
                TableLayout.PREFERRED, UiUtil.HGAP, TableLayout.PREFERRED, UiUtil.HGAP,
                TableLayout.PREFERRED, UiUtil.HGAP, TableLayout.PREFERRED
            },
            { TableLayout.PREFERRED }
        };
        final JPanel optionsPanel = setupControl( new JPanel(new TableLayout(checkSizes)) );
        optionsPanel.add(_findFreeTextUseDescriptionCheck, new TableLayoutConstraints(0, 0));
        optionsPanel.add(_findFreeTextUseMemoCheck, new TableLayoutConstraints(2, 0));
        optionsPanel.add(_findFreeTextUseCheckCheck, new TableLayoutConstraints(4, 0));
        optionsPanel.add(_findFreeTextIncludeSplitsCheck, new TableLayoutConstraints(6, 0));
        row = addRowField1(findPanel, row, startCol, optionsPanel );

        // tags
        _findTagsUseCheck = setupControl( new JCheckBox() );
        _findTagsUseCheck.setToolTipText(findCheckTip);
        row = addRowLabel(findPanel, row, L10NFindAndReplace.FIND_TAGS_LABEL,
                L10NFindAndReplace.FIND_TAGS_MNC, _findTagsUseCheck, false);
        _findTagPicker = new TxnTagsPicker(_controller.getMDGUI(), _model.getData());
        row = addRowField1(findPanel, row, startCol, _findTagPicker.getView());
        row = addRowField1(findPanel, row, startCol, createTagSupportPanel());
        
        // cleared
        _findClearedUseCheck = setupControl( new JCheckBox() );
        _findClearedUseCheck.setToolTipText(findCheckTip);
        row = addRowLabel(findPanel, row, L10NFindAndReplace.FIND_CLEARED_LABEL,
                L10NFindAndReplace.FIND_CLEARED_MNC, _findClearedUseCheck, false);
        
        _findClearedClearedCheck = setupControl( new JCheckBox(
                _controller.getString( L10NFindAndReplace.FIND_CLEARED_LABEL )) );
        _findClearedClearedCheck.setToolTipText(
                _controller.getString(L10NFindAndReplace.FIND_CLEARED_TIP));
        _findClearedReconcilingCheck = setupControl( new JCheckBox(
                _controller.getString( L10NFindAndReplace.FIND_RECONCILING_LABEL )) );
        _findClearedReconcilingCheck.setToolTipText(
                _controller.getString(L10NFindAndReplace.FIND_RECONCILING_TIP));
        _findClearedUnclearedCheck = setupControl( new JCheckBox(
                _controller.getString( L10NFindAndReplace.FIND_UNCLEARED_LABEL )) );
        _findClearedUnclearedCheck.setToolTipText(
                _controller.getString(L10NFindAndReplace.FIND_UNCLEARED_TIP));

        // The text in these should be short enough to work with GridLayout
        final JPanel clearedPanel = setupControl( new JPanel(new GridLayout(1, 3, UiUtil.HGAP, 0)) );
        clearedPanel.add(_findClearedClearedCheck);
        clearedPanel.add(_findClearedReconcilingCheck);
        clearedPanel.add(_findClearedUnclearedCheck);
        // keep the Find button on the Find side of the dialog
        final JPanel findBtnPanel = setupControl( new JPanel(new BorderLayout(UiUtil.HGAP * 2, 0)) );
        findBtnPanel.add(clearedPanel, BorderLayout.CENTER);
        findBtnPanel.add(_findButton, BorderLayout.EAST);
        addRowField1(findPanel, row, startCol, findBtnPanel);

        findPanel.setBorder(MoneydanceLAF.homePageBorder);
        buildFindPanelActions();
        addPanelFocusListeners(findPanel);
        return findPanel;
    } // createFindPanel()

    private <C extends JComponent> C setupControl(final C component)
    {
        component.setOpaque(false);
        return component;
    }

    private void addPanelFocusListeners(final JPanel parent)
    {
        final FocusListener listener = new ColoredParentFocusAdapter(parent);
        FarUtil.recurseAddFocusListener(parent, listener);
    }

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
                _controller.selectAccounts(mdGUI);
            }
        });
        _findAccountsUseCheck.addItemListener(new ItemListener()
        {
            public void itemStateChanged(final ItemEvent event)
            {
                _controller.setUseAccountFilter(event.getStateChange() == ItemEvent.SELECTED);
            }
        });

        _findCategoryUseCheck.addItemListener(new ItemListener()
        {
            public void itemStateChanged(final ItemEvent event)
            {
                _controller.setUseCategoryFilter(event.getStateChange() == ItemEvent.SELECTED);
            }
        });
        _findCategorySelect.addActionListener(new ActionListener()
        {
            public void actionPerformed(final ActionEvent action)
            {
                _controller.selectCategories(mdGUI);
            }
        });

        _findAmountPickers.addChangeListener(new DocumentListener()
        {
            public void insertUpdate(DocumentEvent e)
            {
                if (!_suppressAutoCheckUse && isAmountsDifferent())
                {
                    _controller.setUseAmountFilter(true);
                }
            }

            public void removeUpdate(DocumentEvent e)
            {
                if (!_suppressAutoCheckUse && isAmountsDifferent())
                {
                    _controller.setUseAmountFilter(true);
                }
            }

            public void changedUpdate(DocumentEvent e)
            {
            }
        });
        _findAmountUseCheck.addItemListener(new ItemListener()
        {
            public void itemStateChanged(final ItemEvent event)
            {
                _controller.setUseAmountFilter(event.getStateChange() == ItemEvent.SELECTED);
            }
        });

        _findDatePickers.addChangeListener(new DocumentListener()
        {
            public void insertUpdate(DocumentEvent e)
            {
                if (!_suppressAutoCheckUse)
                {
                    _controller.setUseDateFilter(true);
                }
            }

            public void removeUpdate(DocumentEvent e)
            {
                if (!_suppressAutoCheckUse)
                {
                    _controller.setUseDateFilter(true);
                }
            }

            public void changedUpdate(DocumentEvent e)
            {
            }
        });
        _findDateUseCheck.addItemListener(new ItemListener()
        {
            public void itemStateChanged(final ItemEvent event)
            {
                _controller.setUseDateFilter(event.getStateChange() == ItemEvent.SELECTED);
            }
        });

        _findFreeText.getDocument().addDocumentListener(new DocumentListener()
        {
            public void insertUpdate(DocumentEvent e)
            {
                if (!_suppressAutoCheckUse)
                {
                    _controller.setUseFreeTextFilter(true);
                }
                updateFoundOnlyControls();
            }

            public void removeUpdate(DocumentEvent e)
            {
                if (!_suppressAutoCheckUse)
                {
                    _controller.setUseFreeTextFilter(true);
                }
                updateFoundOnlyControls();
            }

            public void changedUpdate(DocumentEvent e)
            {
                updateFoundOnlyControls();
            }
        });
        _findFreeTextUseCheck.addItemListener(new ItemListener()
        {
            public void itemStateChanged(final ItemEvent event)
            {
                _controller.setUseFreeTextFilter(event.getStateChange() == ItemEvent.SELECTED);
                updateFoundOnlyControls();
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

        _findTagPicker.getView().addSelectionListener(new ActionListener()
        {
            public void actionPerformed(final ActionEvent event)
            {
                // notify that tags will be used
                if (!_suppressAutoCheckUse)
                {
                    _controller.setUseTagsFilter(true);
                }
            }
        });
        _findTagsUseCheck.addItemListener(new ItemListener()
        {
            public void itemStateChanged(final ItemEvent event)
            {
                _controller.setUseTagsFilter(event.getStateChange() == ItemEvent.SELECTED);
            }
        });

        _findClearedUseCheck.addItemListener(new ItemListener()
        {
            public void itemStateChanged(final ItemEvent event)
            {
                _controller.setUseClearedFilter(event.getStateChange() == ItemEvent.SELECTED);
            }
        });
        _findClearedClearedCheck.addItemListener(new ItemListener()
        {
            public void itemStateChanged(final ItemEvent event)
            {
                final boolean allow = event.getStateChange() == ItemEvent.SELECTED;
                if (allow != _controller.getAllowCleared() && !_suppressAutoCheckUse)
                {
                    _controller.setUseClearedFilter(true);
                    _controller.setAllowCleared(allow);
                }
            }
        });
        _findClearedReconcilingCheck.addItemListener(new ItemListener()
        {
            public void itemStateChanged(final ItemEvent event)
            {
                final boolean allow = event.getStateChange() == ItemEvent.SELECTED;
                if (allow != _controller.getAllowReconciling() && !_suppressAutoCheckUse)
                {
                    _controller.setUseClearedFilter(true);
                    _controller.setAllowReconciling(allow);
                }
            }
        });
        _findClearedUnclearedCheck.addItemListener(new ItemListener()
        {
            public void itemStateChanged(final ItemEvent event)
            {
                final boolean allow = event.getStateChange() == ItemEvent.SELECTED;
                if (allow != _controller.getAllowUncleared() && !_suppressAutoCheckUse)
                {
                    _controller.setUseClearedFilter(true);
                    _controller.setAllowUncleared(allow);
                }
            }
        });
    }

    private JPanel createTagSupportPanel()
    {
        final JPanel result = setupControl( new JPanel(new FlowLayout(FlowLayout.LEFT, UiUtil.HGAP*2, 0)) );

        final ClickLabelListPanel clickPanel = setupControl( new ClickLabelListPanel() );

        Runnable action = new Runnable()
        {
            public void run()
            {
                // select all tags in the list
                _findTagPicker.selectAll();
            }
        };
        clickPanel.addLabel(_controller.getString(L10NFindAndReplace.ACCOUNTFILTER_ALL), action);

        action = new Runnable()
        {
            public void run()
            {
                // select all tags in the list
                _findTagPicker.selectNone();
            }
        };
        clickPanel.addLabel(_controller.getString(L10NFindAndReplace.NONE), action);
        clickPanel.layoutUI();
        result.add(clickPanel);
        
        _tagsAnd = setupControl( new JRadioButton(_controller.getString(L10NFindAndReplace.FIND_TAG_AND)) );
        _tagsOr = setupControl( new JRadioButton(_controller.getString(L10NFindAndReplace.FIND_TAG_OR)) );
        _tagsExact = setupControl( new JRadioButton(_controller.getString(L10NFindAndReplace.FIND_TAG_EXACT)) );
        result.add(_tagsAnd);
        result.add(_tagsOr);
        result.add(_tagsExact);
        
        ButtonGroup tagBoolean = new ButtonGroup();
        tagBoolean.add(_tagsAnd);
        tagBoolean.add(_tagsOr);
        tagBoolean.add(_tagsExact);
        tagBoolean.setSelected(_tagsOr.getModel(), true);

        return result;
    }

    boolean saveFindEdits()
    {
        // account and category have already been saved
        _controller.setAmountRange(_findAmountPickers.getFromAmountPicker().getValue(),
                _findAmountPickers.getToAmountPicker().getValue());
        CurrencyType findCurrency = _findAmountPickers.getCurrencyType();
        _controller.setAmountCurrency(findCurrency, _findAmountPickers.isSharesCurrency(findCurrency));

        _controller.setDateRangeKey(_findDatePickers.getDateRangeKey());
        _controller.setDateRange(_findDatePickers.getFromDatePicker().getDateInt(),
                _findDatePickers.getToDatePicker().getDateInt(),
                _useTaxDate.isSelected());

        if (_controller.getUseFreeTextFilter())
        {
            final String textMatch = _findFreeText.getText();
            if (!validateFreeText(textMatch))
            {
                return false;
            }

            _controller.setFreeTextMatch(textMatch);
        }
        _findTagPicker.updateFromView();

        if (_tagsExact.isSelected())
        {
            _controller.setTagsFilterLogic(TagLogic.EXACT);
        }
        else if (_tagsAnd.isSelected())
        {
            _controller.setTagsFilterLogic(TagLogic.AND);
        }
        else
        {
            _controller.setTagsFilterLogic(TagLogic.OR);
        }

        return true;
    }

    private boolean validateFreeText(String textMatch)
    {
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
                                TableLayout.PREFERRED, UiUtil.VGAP, TableLayout.PREFERRED, UiUtil.VGAP,
                                TableLayout.PREFERRED, UiUtil.VGAP * 2, TableLayout.FILL  // buttons
                        }
                };
        _replacePanel = new JPanel(new TableLayout(sizes));
        int row = 0;
        final JLabel panelLabel = setupControl(new JLabel(_controller.getString(L10NFindAndReplace.REPLACE_LABEL)));
        final float currentSize = panelLabel.getFont().getSize2D();
        final Font bold = panelLabel.getFont().deriveFont(Font.BOLD, currentSize + 1.5f);
        panelLabel.setFont(bold);
        _replacePanel.add(panelLabel, new TableLayoutConstraints(0, row));
        row += 2; // skip the gap

        // only one checkbox
        final int startCol = 2;

        // categories row
        _replaceCategoryCheck = setupControl(new JCheckBox());
        row = addRowLabel(_replacePanel, row, L10NFindAndReplace.REPLACE_CAT_LABEL,
                          L10NFindAndReplace.REPLACE_CAT_MNC, _replaceCategoryCheck, true);

        // here we copy the functionality of addRowField1 so we can store the constraints
        _replaceCategoryConstraints = new TableLayoutConstraints(startCol, row, startCol + 3, row);
        if (_controller.getMDGUI() != null)
        {
            buildReplaceCategoryChooser();
        }
        else
        {
            // should never happen, defensive programming (or for testbeds)
            _replaceCategory = setupControl(new JComboBox());
            _replacePanel.add(_replaceCategory, _replaceCategoryConstraints);
        }
        row = row + 2;

        // amount row
        _replaceAmountCheck = setupControl(new JCheckBox());
        row = addRowLabel(_replacePanel, row, L10NFindAndReplace.REPLACE_AMOUNT_LABEL,
                          L10NFindAndReplace.REPLACE_AMOUNT_MNC, _replaceAmountCheck, true);

        _replaceAmount = new AmountPickerGroup(_controller, false, false);
        _replaceAmount.addFocusListener(new ColoredFocusAdapter( _replaceAmount.getToAmountPicker(), _focusColor) );
        row = addRowField1(_replacePanel, row, startCol, _replaceAmount);

        // description
        _replaceDescriptionCheck = setupControl(new JCheckBox());
        row = addRowLabel(_replacePanel, row, L10NFindAndReplace.REPLACE_DESCRIPTION_LABEL,
                          L10NFindAndReplace.REPLACE_DESCRIPTION_MNC, _replaceDescriptionCheck, true);
        _replaceDescription = new JTextField();
        _replaceDescription.addFocusListener(new ColoredFocusAdapter(_replaceDescription,
                                                                     _focusColor));
        _replaceFoundDescriptionOnly = new JCheckBox(
                _controller.getString(L10NFindAndReplace.REPLACE_FOUND_TEXT_ONLY));
        setupControl(_replaceFoundDescriptionOnly);
        row = addRowField2Right(_replacePanel, row, startCol, _replaceDescription,
                           _replaceFoundDescriptionOnly);

        // tags - 3 rows
        _replaceTagsCheck = setupControl(new JCheckBox());
        row = addRowLabel(_replacePanel, row, L10NFindAndReplace.REPLACE_TAGS_LABEL,
                          L10NFindAndReplace.REPLACE_TAGS_MNC, _replaceTagsCheck, true);
        _replaceAddTags = new TxnTagsPicker(_controller.getMDGUI(), _model.getData());
        _replaceAddRadio = setupControl(new JRadioButton());
        row = addRowField3(_replacePanel, row, startCol, _replaceAddRadio,
                           L10NFindAndReplace.REPLACE_TAGSADD_LABEL, _replaceAddTags.getView(),
                           L10NFindAndReplace.REPLACE_TAGSADD_MNC, true);
        _replaceRemoveTags = new TxnTagsPicker(_controller.getMDGUI(), _model.getData());
        _replaceRemoveRadio = setupControl(new JRadioButton());
        row = addRowField3(_replacePanel, row, startCol, _replaceRemoveRadio,
                           L10NFindAndReplace.REPLACE_TAGSREMOVE_LABEL, _replaceRemoveTags.getView(),
                           L10NFindAndReplace.REPLACE_TAGSREMOVE_MNC, true);
        _replaceReplaceTags = new TxnTagsPicker(_controller.getMDGUI(), _model.getData());
        _replaceReplaceRadio = setupControl(new JRadioButton());
        row = addRowField3(_replacePanel, row, startCol, _replaceReplaceRadio,
                           L10NFindAndReplace.REPLACE_TAGSREPLACE_LABEL, _replaceReplaceTags.getView(),
                           L10NFindAndReplace.REPLACE_TAGSREPLACE_MNC, true);

        _replaceTagsGroup = new ButtonGroup();
        _replaceTagsGroup.add(_replaceAddRadio);
        _replaceTagsGroup.add(_replaceRemoveRadio);
        _replaceTagsGroup.add(_replaceReplaceRadio);

        // memo
        _replaceMemoCheck = setupControl(new JCheckBox());
        row = addRowLabel(_replacePanel, row, L10NFindAndReplace.REPLACE_MEMO_LABEL,
                          L10NFindAndReplace.REPLACE_MEMO_MNC, _replaceMemoCheck, true);
        _replaceMemo = new JTextField();
        _replaceMemo.addFocusListener(new ColoredFocusAdapter(_replaceMemo, _focusColor));
        _replaceFoundMemoOnly = new JCheckBox(
                _controller.getString(L10NFindAndReplace.REPLACE_FOUND_TEXT_ONLY));
        setupControl(_replaceFoundMemoOnly);
        row = addRowField2Right(_replacePanel, row, startCol, _replaceMemo, _replaceFoundMemoOnly);

        // check number
        _replaceCheckCheck = setupControl(new JCheckBox());
        row = addRowLabel(_replacePanel, row, L10NFindAndReplace.REPLACE_CHECK_LABEL,
                          L10NFindAndReplace.REPLACE_CHECK_MNC, _replaceCheckCheck, true);
        _replaceCheck = new JTextField();
        _replaceCheck.addFocusListener(new ColoredFocusAdapter(_replaceCheck, _focusColor));
        _replaceFoundCheckOnly = new JCheckBox(
                _controller.getString(L10NFindAndReplace.REPLACE_FOUND_TEXT_ONLY));
        setupControl(_replaceFoundCheckOnly);
        row = addRowField2Right(_replacePanel, row, startCol, _replaceCheck, _replaceFoundCheckOnly);

        _includeTransfersCheck = setupControl(new JCheckBox(
                _controller.getString(L10NFindAndReplace.INCXFER_LABEL)));
        _includeTransfersCheck.setToolTipText(
                _controller.getString(L10NFindAndReplace.INCXFER_TIP));
        addKeystrokeToButton(_includeTransfersCheck, L10NFindAndReplace.INCXFER_MNC, true);
        _replacePanel.add(_includeTransfersCheck,
                          new TableLayoutConstraints(0, row, 1, row, TableLayoutConstants.LEFT,
                                                     TableLayoutConstants.BOTTOM));

        final JPanel buttonPanel = createUpperButtonPanel();
        _replacePanel.add(buttonPanel,
                          new TableLayoutConstraints(2, row, 5, row, TableLayoutConstants.FULL,
                                                     TableLayoutConstants.BOTTOM));

        _replacePanel.setBorder(MoneydanceLAF.homePageBorder);
        buildReplacePanelActions();
        addPanelFocusListeners(_replacePanel);
        return _replacePanel;
    } // createReplacePanel()

    private void addKeystrokeToButton(final AbstractButton button, final String mnemonicKey,
                                      boolean addShift)
    {
        final String mnemonic = _controller.getString(mnemonicKey);
        String keyCode = FarUtil.getKeystrokeTextFromMnemonic(mnemonic, addShift);
        KeyStroke key = null;
        if (keyCode.length() > 0)
        {
            key = KeyStroke.getKeyStroke(keyCode);
            getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(key, keyCode);
            final AbstractAction action = new AbstractAction()
            {
                public void actionPerformed(ActionEvent e)
                {
                    button.doClick();
                    button.requestFocusInWindow();
                }
            };
            getRootPane().getActionMap().put(keyCode, action);
            // for those look-and-feels that support mnemonics, add it
            button.setMnemonic(mnemonic.charAt(0));
        }
        FarUtil.addKeyToToolTip(button, key);
    }

    private void addKeystrokeToLabel(final JLabel label, final String mnemonicKey,
                                     boolean addShift)
    {
        String keyCode = FarUtil.getKeystrokeTextFromMnemonic(_controller.getString(mnemonicKey), addShift);
        if (keyCode.length() > 0)
        {
            // labels we just add a tooltip for, no action is needed
            FarUtil.addKeyToToolTip(label, KeyStroke.getKeyStroke(keyCode));
        }
    }

    private void buildReplacePanelActions()
    {
        _replaceCategory.addItemListener(new ItemListener()
        {
            public void itemStateChanged(ItemEvent e)
            {
                if (_replaceCategory instanceof AccountChoice)
                {
                    _controller.setReplaceCategory(true);
                }
                else
                {
                    _controller.setReplaceCategory(true);
                }
            }
        });
        _replaceCategoryCheck.addItemListener(new ItemListener()
        {
            public void itemStateChanged(final ItemEvent event)
            {
                _controller.setReplaceCategory(event.getStateChange() == ItemEvent.SELECTED);
            }
        });

        _replaceAmount.addChangeListener(new DocumentListener()
        {
            public void insertUpdate(DocumentEvent e)
            {
                boolean different = _replaceAmount.getToAmountPicker().getValue() != _controller.getReplacementAmount();
                if (!_suppressAutoCheckUse && different)
                {
                    _controller.setReplaceAmount(true);
                }
            }
            public void removeUpdate(DocumentEvent e)
            {
                boolean different = _replaceAmount.getToAmountPicker().getValue() != _controller.getReplacementAmount();
                if (!_suppressAutoCheckUse && different)
                {
                    _controller.setReplaceAmount(true);
                }
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
                if (!_suppressAutoCheckUse)
                {
                    _controller.setReplaceDescription(true);
                }
            }
            public void removeUpdate(DocumentEvent e)
            {
                if (!_suppressAutoCheckUse)
                {
                    _controller.setReplaceDescription(true);
                }
            }

            public void changedUpdate(DocumentEvent e) { }
        });
        _replaceDescriptionCheck.addItemListener(new ItemListener()
        {
            public void itemStateChanged(final ItemEvent event)
            {
                _controller.setReplaceDescription(event.getStateChange() == ItemEvent.SELECTED);
                updateFoundOnlyControls();
            }
        });
        _replaceFoundDescriptionOnly.addItemListener(new ItemListener()
        {
            public void itemStateChanged(final ItemEvent event)
            {
                _controller.setReplaceFoundDescriptionOnly(
                        event.getStateChange() == ItemEvent.SELECTED);
            }
        });

        _replaceMemo.getDocument().addDocumentListener(new DocumentListener()
        {
            public void insertUpdate(DocumentEvent e)
            {
                if (!_suppressAutoCheckUse)
                {
                    _controller.setReplaceMemo(true);
                }
            }
            public void removeUpdate(DocumentEvent e)
            {
                if (!_suppressAutoCheckUse)
                {
                    _controller.setReplaceMemo(true);
                }
            }

            public void changedUpdate(DocumentEvent e) { }
        });
        _replaceMemoCheck.addItemListener(new ItemListener()
        {
            public void itemStateChanged(final ItemEvent event)
            {
                _controller.setReplaceMemo(event.getStateChange() == ItemEvent.SELECTED);
                updateFoundOnlyControls();
            }
        });
        _replaceFoundMemoOnly.addItemListener(new ItemListener()
        {
            public void itemStateChanged(final ItemEvent event)
            {
                _controller.setReplaceFoundMemoOnly(
                        event.getStateChange() == ItemEvent.SELECTED);
            }
        });

        _replaceCheck.getDocument().addDocumentListener(new DocumentListener()
        {
            public void insertUpdate(DocumentEvent e)
            {
                if (!_suppressAutoCheckUse)
                {
                    _controller.setReplaceCheck(true);
                }
            }
            public void removeUpdate(DocumentEvent e)
            {
                if (!_suppressAutoCheckUse)
                {
                    _controller.setReplaceCheck(true);
                }
            }

            public void changedUpdate(DocumentEvent e) { }
        });
        _replaceCheckCheck.addItemListener(new ItemListener()
        {
            public void itemStateChanged(final ItemEvent event)
            {
                _controller.setReplaceCheck(event.getStateChange() == ItemEvent.SELECTED);
                updateFoundOnlyControls();
            }
        });
        _replaceFoundCheckOnly.addItemListener(new ItemListener()
        {
            public void itemStateChanged(final ItemEvent event)
            {
                _controller.setReplaceFoundCheckOnly(
                        event.getStateChange() == ItemEvent.SELECTED);
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
                if (!_suppressAutoCheckUse)
                {
                    _controller.setReplaceTags(true);
                }
                _replaceAddRadio.setSelected(true);
            }
        });
        _replaceRemoveTags.getView().addSelectionListener(new ActionListener()
        {
            public void actionPerformed(final ActionEvent event)
            {
                // notify that tags will be used
                if (!_suppressAutoCheckUse)
                {
                    _controller.setReplaceTags(true);
                }
                _replaceRemoveRadio.setSelected(true);
            }
        });
        _replaceReplaceTags.getView().addSelectionListener(new ActionListener()
        {
            public void actionPerformed(final ActionEvent event)
            {
                // notify that tags will be used
                if (!_suppressAutoCheckUse)
                {
                    _controller.setReplaceTags(true);
                }
                _replaceReplaceRadio.setSelected(true);
            }
        });

        _includeTransfersCheck.addItemListener(new ItemListener()
        {
            public void itemStateChanged(final ItemEvent event)
            {
                _controller.setIncludeTransfers(event.getStateChange() == ItemEvent.SELECTED);
            }
        });

    }

    void saveReplaceEdits()
    {
        Account selectedAccount = null;
        if (_replaceCategory instanceof AccountChoice)
        {
            selectedAccount = ((AccountChoice)_replaceCategory).getSelectedAccount();
        }
        _controller.setReplacementCategory(selectedAccount);

        _controller.setReplacementAmount(_replaceAmount.getToAmountPicker().getValue(), _replaceAmount.getCurrencyType());
        _controller.setReplacementDescription(_replaceDescription.getText());
        _controller.setReplaceFoundDescriptionOnly(_replaceFoundDescriptionOnly.isSelected());
        _controller.setReplacementMemo(_replaceMemo.getText());
        _controller.setReplaceFoundMemoOnly(_replaceFoundMemoOnly.isSelected());
        _controller.setReplacementCheck(_replaceCheck.getText());
        _controller.setReplaceFoundCheckOnly(_replaceFoundCheckOnly.isSelected());

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
        _summary.setText(_model.getSummaryText(_controller));
    }

    private void updateFoundOnlyControls()
    {
        final String findText = _findFreeText.getText();
        final boolean allowFoundOnly = _findFreeTextUseCheck.isSelected() &&
                (findText != null) && !"".equals(findText);
        _replaceFoundDescriptionOnly.setEnabled(allowFoundOnly);
        _replaceFoundMemoOnly.setEnabled(allowFoundOnly);
        _replaceFoundCheckOnly.setEnabled(allowFoundOnly);
    }

    private int addRowLabel(JPanel panel, int rowNum, String labelKey, String labelMnemonicKey,
                            JCheckBox check, boolean addShift)
    {
        TableLayoutConstraints constraints = new TableLayoutConstraints(0, rowNum);
        JLabel label = new JLabel( FarUtil.getLabelText(_controller, labelKey ) );
        label.setHorizontalAlignment(SwingConstants.RIGHT);
        String mnemonic = _controller.getString( labelMnemonicKey );
        if ( (mnemonic != null) && (mnemonic.length() > 0) )
        {
            label.setDisplayedMnemonic( mnemonic.charAt( 0 ) );
            addKeystrokeToLabel(label, labelMnemonicKey, addShift);
            // the checkbox has no text, so pointless to set the mnemonic
            addKeystrokeToButton(check, labelMnemonicKey, addShift);
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

    private int addRowField2( JPanel panel, int rowNum, int startCol, JComponent field1, JComponent field2 )
    {
        TableLayoutConstraints constraints = new TableLayoutConstraints(startCol, rowNum, startCol+2, rowNum);
        panel.add( field1, constraints );
        constraints = new TableLayoutConstraints(startCol+3, rowNum, startCol+3, rowNum);
        panel.add( field2, constraints );
        return rowNum + 2;
    }

    private int addRowField2Right( JPanel panel, int rowNum, int startCol, JComponent field1, JComponent field2 )
    {
        JPanel subPanel = new JPanel(new BorderLayout());
        setupControl(subPanel);
        subPanel.add(field1, BorderLayout.CENTER);
        subPanel.add(field2, BorderLayout.EAST);
        TableLayoutConstraints constraints = new TableLayoutConstraints(startCol, rowNum, startCol+3, rowNum);
        panel.add( subPanel, constraints );
        return rowNum + 2;
    }

    private int addRowField3(JPanel panel, int rowNum, int startCol, JRadioButton button, String labelKey,
                             JComponent field2, String labelMnemonicKey, boolean addShift)
    {
        TableLayoutConstraints constraints = new TableLayoutConstraints(startCol, rowNum, startCol+1, rowNum);
        panel.add( button, constraints );
        constraints = new TableLayoutConstraints(startCol+2, rowNum);
        JLabel label = new JLabel( _controller.getString( labelKey ) );
        label.setHorizontalAlignment( SwingConstants.RIGHT );
        label.setBorder( new EmptyBorder( 0, UiUtil.HGAP, 0, UiUtil.HGAP) );
        String mnemonic = _controller.getString( labelMnemonicKey );
        if ( (mnemonic != null) && (mnemonic.length() > 0) )
        {
            label.setDisplayedMnemonic( mnemonic.charAt( 0 ) );
            addKeystrokeToLabel(label, labelMnemonicKey, addShift);
            addKeystrokeToButton(button, labelMnemonicKey, addShift);
        }
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
                TableLayout.FILL,
                UiUtil.HGAP, TableLayout.PREFERRED,
                UiUtil.HGAP, TableLayout.PREFERRED
            },
            // rows
            { TableLayout.PREFERRED }
        };
        final JPanel buttons = setupControl( new JPanel( new TableLayout( sizes ) ) );

        buttons.add( _replaceButton, UiUtil.createTableConstraintBtnR(2, 0) );
        buttons.add( _replaceAllButton, UiUtil.createTableConstraintBtnR(4, 0) );

        return buttons;
    }

    private JPanel createLowerRightButtonPanel()
    {
        final JPanel buttons = new JPanel( new GridLayout( 1, 3, UiUtil.HGAP, 0 ) );

        buttons.add( _resetButton );
        buttons.add( _recordButton );
        buttons.add( _closeButton );

        return buttons;
    }

    private JPanel createLowerLeftButtonPanel()
    {
        // use table layout to get different sized buttons
        final double[][] sizes = new double[][]
        {
            // columns
            {
                TableLayout.PREFERRED, UiUtil.HGAP, TableLayout.PREFERRED, UiUtil.HGAP,
                TableLayout.PREFERRED, UiUtil.HGAP, TableLayout.PREFERRED
            },
            // rows
            { TableLayout.PREFERRED }
        };
        final JPanel buttons = new JPanel( new TableLayout( sizes ) );

        buttons.add(_markAllButton, UiUtil.createTableConstraintBtnL(0, 0) );
        buttons.add(_markNoneButton, UiUtil.createTableConstraintBtnL(2, 0) );
        buttons.add(_gotoButton, UiUtil.createTableConstraintBtnL(4, 0) );
        buttons.add(_copyButton, UiUtil.createTableConstraintBtnL(6, 0) );

        return buttons;
    }

    private void setProgressText()
    {
        _statusLabel.setText(_controller.getString(L10NFindAndReplace.REPLACING_PROGRESS));
        _statusLabel.setFont(_resetButton.getFont());
        _statusLabel.setEnabled(true);
        // since we're on the EDT we want to force an immediate repaint
        _statusLabel.getParent().validate();
        _statusLabel.paintImmediately(_statusLabel.getBounds());
    }

    private void clearProgressText()
    {
        _statusLabel.setText(getVersionText());
        _statusLabel.setFont(_smallFont);
        _statusLabel.setEnabled(false);
        // since we're on the EDT we want to force an immediate repaint
        _statusLabel.getParent().validate();
        _statusLabel.paintImmediately(_statusLabel.getBounds());
    }

    private String getVersionText()
    {
        final String format = _controller.getString(L10NFindAndReplace.VERSION_FMT);
        return MessageFormat.format(format, _controller.getBuildString());
    }

    private boolean isAmountsDifferent()
    {
        final long newFrom = _findAmountPickers.getFromAmountPicker().getValue();
        final long newTo = _findAmountPickers.getToAmountPicker().getValue();
        return (newFrom != _controller.getAmountMinimum()) ||
                (newTo != _controller.getAmountMaximum());
    }
    
    private void buildReplaceCategoryChooser()
    {
        if ((_replacePanel != null) && (_replaceCategory != null))
        {
            _replacePanel.remove(_replaceCategory);
        }
        if (_controller.getMDGUI() != null)
        {
            AccountChoice chooser = setupControl( new AccountChoice(_model.getData(), _controller.getMDGUI()) );
            chooser.setContainerAccount(_model.getData());
            
            final boolean normalAccounts = _controller.getIncludeTransfers();
            chooser.setShowAssetAccounts(normalAccounts);
            chooser.setShowBankAccounts(normalAccounts);
            chooser.setShowCreditCardAccounts(normalAccounts);
            chooser.setShowInvestAccounts(normalAccounts);
            chooser.setShowLiabilityAccounts(normalAccounts);
            chooser.setShowLoanAccounts(normalAccounts);
            chooser.setShowSecurityAccounts(normalAccounts);

            // never show other accounts
            chooser.setShowOtherAccounts(false);

            // always show categories
            chooser.setShowIncomeAccounts(true);
            chooser.setShowExpenseAccounts(true);

            final Account account = _controller.getReplacementCategory();
            if (_controller.getReplaceCategory() && (account != null))
            {
                chooser.setShowAccount(account, true);
                chooser.setSelectedAccount(account);
            }
            else
            {
                chooser.setSelectedAccountIndex(0);
            }
            _replaceCategory = chooser;
        }
        if ((_replacePanel != null) && (_replaceCategory != null))
        {
            _replacePanel.add(_replaceCategory, _replaceCategoryConstraints);
            _replacePanel.validate();
        }
    }


    private void disableMenus()
    {
        // File
        mainMenu.fileNewAction.setEnabled(true);
        //mainMenu.fileOpenAction.setEnabled(true);
        mainMenu.fileExportAction.setEnabled(true);
        mainMenu.fileEncryptionAction.setEnabled(false);
        mainMenu.fileArchiveAction.setEnabled(false);
        //mainMenu.fileSaveAsAction.setEnabled(true);
        mainMenu.fileSaveAction.setEnabled(true);
        mainMenu.printChecksAction.setEnabled(false);
        mainMenu.printTxnsAction.setEnabled(false);
        mainMenu.newTxnAction.setEnabled(false);
        // Edit
        mainMenu.editFindAction.setEnabled(false);
        mainMenu.editAdvancedFindAction.setEnabled(false);
        // View
        mainMenu.viewDBBudget.setEnabled(false);
        mainMenu.viewDBNothing.setEnabled(false);
        mainMenu.viewDBNetWorth.setEnabled(false);
        mainMenu.viewHomeAction.setEnabled(false);
        //mainMenu.viewShowSourceListAction.setEnabled(false);
        // Account
        mainMenu.acctNewAction.setEnabled(false);
        mainMenu.acctEditAction.setEnabled(false);
        mainMenu.acctDeleteAction.setEnabled(false);
        mainMenu.reconcileAction.setEnabled(false);
        // Online
        mainMenu.downloadAllAction.setEnabled(false);
        mainMenu.setupOnlineAction.setEnabled(false);
        mainMenu.setupOnlineBPAction.setEnabled(false);
        mainMenu.showOnlineBPAction.setEnabled(false);
        mainMenu.sendOnlineBPAction.setEnabled(false);
        mainMenu.confirmSelectedTxnsAction.setEnabled(false);
        mainMenu.forgetPasswdsAction.setEnabled(false);
        mainMenu.downloadTxnsAction.setEnabled(false);
        // Tools
        mainMenu.toolsLoanCalcAction.setEnabled(true);
        mainMenu.toolsNormalCalcAction.setEnabled(true);
        mainMenu.toolsRemindersAction.setEnabled(true);
        mainMenu.toolsBudgetAction.setEnabled(true);
        mainMenu.toolsTranslateCurrencyAction.setEnabled(true);
        mainMenu.toolsCurrencyAction.setEnabled(true);
        mainMenu.toolsSecuritiesAction.setEnabled(true);
        mainMenu.toolsCOAAction.setEnabled(true);
        mainMenu.toolsCategoriesAction.setEnabled(true);
        mainMenu.toolsAddressBookAction.setEnabled(true);
        mainMenu.toolsReportsAction.setEnabled(true);
        mainMenu.toolsTxnTagsAction.setEnabled(true);
        // Extensions, Windows and Help all stay enabled
    }

    private class ColoredFocusAdapter extends FocusAdapter
    {
        private final Color _normalBackground;
        private final Color _focusedBackground;

        ColoredFocusAdapter(final Component source, final Color focused)
        {
            _normalBackground = source.getBackground();
            _focusedBackground = focused;
        }

        @Override
        public void focusGained(FocusEvent event)
        {
            event.getComponent().setBackground(_focusedBackground);
        }

        @Override
        public void focusLost(FocusEvent event)
        {
            event.getComponent().setBackground(_normalBackground);
        }
    }

    private class FarFocusTraversalPolicy extends LayoutFocusTraversalPolicy
    {
        @Override
        public Component getDefaultComponent(Container aContainer)
        {
            Component defaultComponent = super.getDefaultComponent(aContainer);
            if ((defaultComponent == null) || (aContainer == FarView.this))
            {
                defaultComponent = _findFreeText;
            }
            return defaultComponent;
        }
    }
}

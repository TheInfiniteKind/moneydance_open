/*
 * PriceEntryScreen.java
 *
 *  Created: 2008-06-27
 *
 * Modified: 2011-11-11

 * This class is part of Security Price Entry, which is an extension
 * to the Moneydance personal finance program.
 *
 * Original Copyright (C) 2011 by Thomas Edelson of Songline Software
 * (www.songline-software.com).
 *
 * Now Copyright (c) 2015 The Infinite Kind Limited (infinitekind.com)
 *
 */

package com.moneydance.modules.features.priceui.priceEntry;


import com.infinitekind.moneydance.model.CurrencyType;
import com.infinitekind.util.CustomDateFormat;
import com.infinitekind.util.DateUtil;
import com.moneydance.apps.md.controller.UserPreferences;
import com.moneydance.awt.*;
import com.moneydance.modules.features.priceui.swing.RightAlignedCellRenderer;

import javax.swing.*;
import javax.swing.table.DefaultTableCellRenderer;
import java.awt.*;
import java.awt.event.KeyAdapter;
import java.awt.event.KeyEvent;


/**
 * Defines the GUI used for displaying, and entering, prices for securities
 * owned by -- or otherwise of interest to -- the user.
 *
 * @author Tom Edelson
 */
public class PriceEntryScreen extends javax.swing.JFrame {

    /*
     * This is partly generated code, courtesy of NetBeans.
     *
     * This code is intended to be portable between different
     * personal finance software packages.
     *
     */

    private final int PRICE_COLUMN = 2;

    private PriceEntryExec responder;

    private PriceTableModel tableModel;
    private static char decimalChar = '.';

    /*
     * Additional declarations of instance variables are in generated code
     * which appears at the bottom of this source file.
     *
     */


    /**
     * Creates (but does not display) new PriceEntryScreen window object.
     *
     * @param model           the "table model" from which the table in this form
     *                        will get its data.
     * @param responderObject the object to which this form object will call back to
     *                        execute user-requested actions.
     */
    public PriceEntryScreen(PriceTableModel model, PriceEntryExec responderObject) {

        tableModel = model;
        responder = responderObject;

        CustomDateFormat dateFormat = UserPreferences.getInstance().getShortDateFormatter();
        jLabel2 = new javax.swing.JLabel();
        makeCurrentFlagChbox = new javax.swing.JCheckBox();
        asOfDate = new JDateField(dateFormat);
        asOfDate.setDateInt(calcAsOfDate());
        jScrollPane1 = new javax.swing.JScrollPane();
        priceTable = new JTable();
        applyButton = new javax.swing.JButton();

        setDefaultCloseOperation(javax.swing.WindowConstants.EXIT_ON_CLOSE);

        setTitle("Security Prices");

        jLabel2.setText("As-of Date:");

        priceTable.setShowVerticalLines(false);

        makeCurrentFlagChbox.setSelected(true);
        makeCurrentFlagChbox.setText("Also set these prices as \"current\"");

        priceTable.setModel(tableModel);
        jScrollPane1.setViewportView(priceTable);

        applyButton.setText("Apply");
        applyButton.addActionListener(this::applyButtonActionPerformed);

        JRateField priceField = makeRateEditorField();
        EditingCellEditor rateEditor = new EditingCellEditor(priceField);
        rateEditor.setClickCountToStart(1);
        priceField.addKeyListener(new KeyAdapter() {
            @Override
            public void keyPressed(KeyEvent e) {
                if (e.getKeyCode() == KeyEvent.VK_ENTER) {
                    int nextRowIdx = priceTable.getSelectedRow() + 1;
                    if (nextRowIdx < priceTable.getRowCount()) {
                        rateEditor.stopCellEditing();
                        SwingUtilities.invokeLater(() -> {
                            priceTable.getSelectionModel().setSelectionInterval(nextRowIdx, nextRowIdx);
                            priceTable.editCellAt(nextRowIdx, PRICE_COLUMN);
                            priceTable.scrollRectToVisible(priceTable.getCellRect(nextRowIdx, 0, true));
                        });
                    }
                }
            }
        });

        RightAlignedCellRenderer amountRenderer = new RightAlignedCellRenderer();
        //priceTable.setDefaultRenderer(CurrencyType.class, new SecurityNameCellRenderer());
        priceTable.setDefaultRenderer(String.class, amountRenderer);
        priceTable.setDefaultEditor(Double.class, rateEditor);
        //System.err.println("editor column class: "+model.getColumnClass(PRICE_COLUMN));
        priceTable.getColumnModel().getColumn(PRICE_COLUMN).setCellEditor(rateEditor);

        Font rowFont = amountRenderer.getFont();
        FontMetrics fm = amountRenderer.getFontMetrics(rowFont);
        priceTable.setRowHeight((int) Math.round(fm.getHeight() * 1.2));
        priceTable.setAutoResizeMode(JTable.AUTO_RESIZE_SUBSEQUENT_COLUMNS);

        JPanel p = new JPanel(new GridBagLayout());
        JPanel asOfPanel = new JPanel(new GridBagLayout());
        asOfPanel.add(jLabel2, GridC.getc(0, 0).label());
        asOfPanel.add(asOfDate, GridC.getc(1, 0).field());
        asOfPanel.add(makeCurrentFlagChbox, GridC.getc(0, 1).colspan(2).insets(18, 0, 0, 0));
        p.add(asOfPanel, GridC.getc(0, 1).center().insets(18, 18, 18, 18));
        p.add(jScrollPane1, GridC.getc(0, 2).wxy(1, 1).fillboth());
        p.add(applyButton, GridC.getc(0, 3).east().insets(10, 50, 10, 10));
        setContentPane(p);
        pack();
        setDefaultCloseOperation(javax.swing.WindowConstants.DISPOSE_ON_CLOSE);

        // The following is a workaround for a bug in JTable
        //  (See "http://bugs.sun.com/bugdatabase/view_bug.do?bug_id=4709394"):
        priceTable.putClientProperty("terminateEditOnFocusLost", Boolean.TRUE);

        AwtUtil.setupWindow(this, 450, 450, null);
    } // end constructor


    private void applyButtonActionPerformed(java.awt.event.ActionEvent evt) {
        responder.applyPrices();
    }

    /**
     * Returns the "as-of date", or effective date, of the prices in the window.
     *
     * @return the effective date of the prices entered.
     * This may be the calculated, default value which was initially presented
     * to the user (to wit, the last day of the previous month),
     * or it may be a value entered by the user to replace the default.
     */

    public int getAsOfDate() {
        return asOfDate.getDateInt();
    }


    /**
     * Returns an indication as to whether the prices entered in the window
     * should be considered to be the "current prices" for those securities.
     *
     * @return the "make-current flag", which is true if these are the "current"
     * prices, and false if they are not.  This value is true by default, but
     * the user can change it to false (for example, if the prices entered
     * are from a broker's statement other than the most recent one).
     */

    public boolean getMakeCurrentFlag() {
        return makeCurrentFlagChbox.isSelected();
    }


    /*
     * Returns a Date which represents the last day of the previous month,
     * at noon.
     *
     * Ideally, I'd break out a separate utility function which took a Date
     * argument, so I could test the algorithm by feeding it lots of test cases.
     *
     * Called by: initComponents()
     *
     */
    private int calcAsOfDate() {
        int today = DateUtil.getStrippedDateInt();
        return DateUtil.incrementDate(today, 0, 0, (today % 100) * -1); // the last day of the previous month
    } // end method calcAsOfDate


    private javax.swing.JButton applyButton;
    private JDateField asOfDate;
    private javax.swing.JLabel jLabel2;
    private javax.swing.JScrollPane jScrollPane1;
    private javax.swing.JCheckBox makeCurrentFlagChbox;
    private javax.swing.JTable priceTable;


    private static JRateField makeRateEditorField() {
        JRateField field = new JRateField(decimalChar);
        field.setAllowBlank(true);
        field.setHorizontalAlignment(SwingConstants.RIGHT);
        field.setDefaultValue(0.0);
        return field;
    }


} // end class PriceEntryScreen

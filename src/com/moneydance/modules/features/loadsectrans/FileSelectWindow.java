/*
 *  Copyright (c) 2014, Michael Bray. All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 *   - Redistributions of source code must retain the above copyright
 *     notice, this list of conditions and the following disclaimer.
 *
 *   - Redistributions in binary form must reproduce the above copyright
 *     notice, this list of conditions and the following disclaimer in the
 *     documentation and/or other materials provided with the distribution.
 *
 *   - The name of the author may not used to endorse or promote products derived
 *     from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
 * IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 * THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 * PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 * LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */
package com.moneydance.modules.features.loadsectrans;


import java.awt.*;
import java.awt.event.ActionEvent;
import java.io.BufferedReader;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.*;
import java.util.List;

import javax.swing.*;
import javax.swing.event.TreeSelectionEvent;
import javax.swing.event.TreeSelectionListener;
import javax.swing.filechooser.FileNameExtensionFilter;
import javax.swing.tree.*;

import com.infinitekind.moneydance.model.Account;
import com.infinitekind.moneydance.model.CurrencyType;
import com.moneydance.apps.md.view.MoneydanceUI;
import com.moneydance.awt.GridC;
import com.moneydance.modules.features.mrbutil.MRBPreferences2;


public class FileSelectWindow extends JPanel implements TreeSelectionListener {
    private static final long serialVersionUID = 1L;
    private static final int MINSCROLLPANE = 300;
    private static final int SCROLLPANEDEPTH = 400;
    private JTextField fileName;
    private JButton loadBtn;
    private JButton chooseBtn;
    private JButton addBtn;
    private JComboBox<String> accountsCB;
    private JComboBox<String> tickerField;
    private JComboBox<String> dateField;
    private JComboBox<String> valueField;
    private JComboBox<String> txnTypeField;
    private JComboBox<String> descField;
    private JComboBox<String> unitField;
    private boolean unitsPresent=false;
    private JCheckBox stripExch;
    private JScrollPane fieldsScroll;
    private JPanel fieldsPan;
    private Parameters2 params;
    private JFileChooser fileChooser = null;
    private File securities;
    private loadPricesWindow loadWindow;
    private Map<String, Account> investAccts = new HashMap<>();
    private String[] arrNames;
    private MRBPreferences2 preferences;
    private Account rootAccount;
    private Account selectedCategory;
    public static Image openIcon;
    private static Image closeIcon;
    private static Image leafIcon;
    private ImageIcon openImage;
    private ImageIcon closeImage;
    private ImageIcon leafImage;

    private String[] columnData;
    private List<FieldLine> listLines;
    private Map<Object, String> linesButtons;
    private JTree categoryTree;
    private DefaultMutableTreeNode rootNode;
    private JScrollPane treeView;
    private Map<String, Account> accounts;
    private Map<String, TreeNode[]> acctPaths;
    private boolean dirty=false;
    private String strName = "";
    private MoneydanceUI mdGUI;
    private com.moneydance.apps.md.controller.Main mdMain;
    private JButton helpBtn;

    public FileSelectWindow() throws HeadlessException {
        mdMain = com.moneydance.apps.md.controller.Main.mainObj;
        mdGUI = mdMain.getUI();
        MRBPreferences2.loadPreferences(Main.context);
        preferences = MRBPreferences2.getInstance();
        accounts = new TreeMap<>();
        acctPaths = new TreeMap<>();
        investAccts.put("Please Select an Account", null);
        rootAccount =Main.context.getRootAccount();
        rootNode = new DefaultMutableTreeNode(rootAccount);
        loadAccounts(rootAccount, strName,rootNode);
        categoryTree = new JTree(rootNode);
        categoryTree.getSelectionModel().setSelectionMode(
                TreeSelectionModel.SINGLE_TREE_SELECTION);
        categoryTree.addTreeSelectionListener(this);

        // Create a tree that allows one selection at a time.
        categoryTree.getSelectionModel().setSelectionMode(
                TreeSelectionModel.SINGLE_TREE_SELECTION);
        openIcon = getIcon("icons8-opened-folder-16.png");
        closeIcon = getIcon("icons8-folder-16.png");
        leafIcon = getIcon("icons8-square-8.png");
        if (openIcon != null) openImage =new ImageIcon(openIcon);
        if (closeIcon != null)closeImage =new ImageIcon(closeIcon);
        if (leafIcon != null)leafImage =new ImageIcon(leafIcon);
        categoryTree.setCellRenderer(new DefaultTreeCellRenderer(){
            public Component getTreeCellRendererComponent(JTree tree, Object value, boolean selected, boolean expanded,
                                                          boolean leaf, int row, boolean hasFocus){
                NodeEntry entry;
                if (value != null && value instanceof DefaultMutableTreeNode) {
                    if (((DefaultMutableTreeNode) value).getUserObject() instanceof NodeEntry) {
                        entry = (NodeEntry) (((DefaultMutableTreeNode) value).getUserObject());
                        setText(entry.getAccount().getAccountName());
                    }
                }
                if (expanded && !leaf&& openImage != null)
                    setIcon(openImage);
                if (!expanded && ! leaf && closeImage !=null)
                    setIcon(closeImage);
                if (leaf&& leafImage != null)
                    setIcon(leafImage);
                if (selected) {
                    super.setBackground(Color.blue);
                    setForeground(Color.WHITE);
                    setOpaque(true);
                } else {
                    super.setBackground(getBackgroundNonSelectionColor());
                    setForeground(getTextNonSelectionColor());
                    setOpaque(false);
                }
                return this;
            }
        });

        // Listen for when the selection changes.
        categoryTree.addTreeSelectionListener(this);
        categoryTree.setRootVisible(false);

        // Create the scroll pane and add the tree to it.
        treeView = new JScrollPane();
        treeView.getViewport().add(categoryTree);
        treeView.getViewport().setPreferredSize(new Dimension(MINSCROLLPANE, SCROLLPANEDEPTH));
        categoryTree.setMinimumSize(new Dimension(MINSCROLLPANE, SCROLLPANEDEPTH));
        fileChooser = new JFileChooser();
        arrNames = investAccts.keySet().toArray(new String[0]);
        GridBagLayout gbl_panel = new GridBagLayout();
        this.setLayout(gbl_panel);
        int x = 0;
        int y = 0;
        JLabel lblFileName = new JLabel("File : ");
        this.add(lblFileName, GridC.getc(x, y).insets(20, 20, 0, 0));

        fileName = new JTextField();
        fileName.setText("");
        fileName.setColumns(50);
        x++;
        this.add(fileName, GridC.getc(x, y).colspan(3).insets(20, 5, 0, 0));

        chooseBtn = new JButton();
        Image img = getIcon("Search-Folder-icon.jpg");
        if (img == null)
            chooseBtn.setText("Find");
        else
            chooseBtn.setIcon(new ImageIcon(img));
        x = 4;
        this.add(chooseBtn, GridC.getc(x, y).insets(10, 5, 0, 0));
        chooseBtn.setBorder(javax.swing.BorderFactory.createLineBorder(this.getBackground()));
        chooseBtn.addActionListener(e -> chooseFile());
        JLabel lblAccounts = new JLabel("Which Investment Account : ");
        x = 1;
        y++;
        this.add(lblAccounts, GridC.getc(x, y).insets(10, 0, 0, 0));

        accountsCB = new JComboBox<>(arrNames);
        x++;
        this.add(accountsCB, GridC.getc(x, y).insets(5, 0, 0, 0));
        accountsCB.addActionListener(e->{
            JComboBox<?> accountsT;
            if (e.getSource() instanceof JComboBox)
                accountsT= (JComboBox<?>)e.getSource();
        });
        JLabel txnTypeLbl = new JLabel("Select Transaction Type Field");
        x = 1;
        y++;
        this.add(txnTypeLbl, GridC.getc(x, y).insets(5, 5, 5, 5));
        txnTypeField = new JComboBox<>();
        x++;
        txnTypeField.addItem("Please Select a Field");
        txnTypeField.addActionListener(e -> {
            JComboBox<?> referenceT;
            if (e.getSource() instanceof JComboBox) {
                referenceT = (JComboBox<?>) (e.getSource());
                dirty = true;
                params.setReference((String) referenceT.getSelectedItem());
            }
        });
        this.add(txnTypeField, GridC.getc(x, y).insets(5, 5, 5, 5).west());
        JLabel lblLTicker = new JLabel("Select Ticker Field");
        x = 1;
        y++;
        this.add(lblLTicker, GridC.getc(x, y).insets(5, 5, 5, 5));
        tickerField = new JComboBox<>();
        x++;
        tickerField.addItem("Please Select a Field");
        tickerField.addActionListener(e -> {
            JComboBox<?> tickT;
            if (e.getSource() instanceof JComboBox) {
                tickT = (JComboBox<?>) (e.getSource());
                dirty = true;
                params.setTicker((String) tickT.getSelectedItem());
            }
        });
        this.add(tickerField, GridC.getc(x, y).insets(5, 5, 5, 5).west());
        JLabel lblLExch = new JLabel("Remove Exchange from Ticker?");
        x++;
        this.add(lblLExch, GridC.getc(x, y).insets(5, 5, 5, 5).east());
        stripExch = new JCheckBox();
        x++;
        stripExch.addActionListener(e -> {
            JCheckBox chbExchT = (JCheckBox) e.getSource();
            dirty=true;
            params.setExch(chbExchT.isSelected());
        });
        this.add(stripExch, GridC.getc(x, y).insets(5, 5, 5, 5).west());
        JLabel lblLDate = new JLabel("Select Date Field");
        x = 1;
        y++;
        this.add(lblLDate, GridC.getc(x, y).insets(5, 5, 5, 5));
        x++;
        dateField = new JComboBox<>();
        dateField.addItem("Please Select a Field");
        dateField.addActionListener(e -> {
            JComboBox<?> cbDateT = (JComboBox<?>) (e.getSource());
            dirty=true;
            params.setDate((String) cbDateT.getSelectedItem());
        });
        this.add(dateField, GridC.getc(x, y).insets(5, 5, 5, 5).west());
        JLabel lblLValue = new JLabel("Select Value Field");
        x = 1;
        y++;
        this.add(lblLValue, GridC.getc(x, y).insets(5, 5, 5, 5));
        x++;
        valueField = new JComboBox<>();
        valueField.addItem("Please Select a Field");
        valueField.addActionListener(e -> {
            JComboBox<?> valueT;
            if (e.getSource() instanceof JComboBox) {
                valueT = (JComboBox<?>) (e.getSource());
                dirty = true;
                params.setValue((String) valueT.getSelectedItem());
            }
        });
        this.add(valueField, GridC.getc(x, y).insets(5, 5, 5, 5).west());
        x = 1;
        y++;
        JLabel lblLDesc = new JLabel("Select Description Field");
        this.add(lblLDesc, GridC.getc(x, y).insets(5, 5, 5, 5));
        x++;
        descField = new JComboBox<>();
        descField.addItem("Please Select a Field");
        descField.addActionListener(e -> {
            JComboBox<?> descT;
            if (e.getSource() instanceof JComboBox) {
                descT = (JComboBox<?>) (e.getSource());
                dirty = true;
                params.setDesc((String) descT.getSelectedItem());
            }
        });
        this.add(descField, GridC.getc(x, y).insets(5, 5, 5, 5).west());
        x = 1;
        y++;
        JLabel lblLUnit = new JLabel("Select Units Field");
        this.add(lblLUnit, GridC.getc(x, y).insets(5, 5, 5, 5));
        x++;
        unitField = new JComboBox<>();
        unitField.addItem("Please Select a Field");
        unitField.addActionListener(e -> {
            JComboBox<?> unitT;
            if (e.getSource() instanceof JComboBox) {
                unitT = (JComboBox<?>) (e.getSource());
                dirty = true;
                params.setUnitsField((String) unitT.getSelectedItem());
                unitsPresent = unitT.getSelectedIndex() > 0;
            }

        });
        this.add(unitField, GridC.getc(x, y).insets(5, 5, 5, 5).west());    x = 1;
        y++;
        JLabel lblTransType = new JLabel("Transaction Types");
        this.add(lblTransType, GridC.getc(x, y).insets(5, 5, 5, 5));
        JLabel lblTrantxt = new JLabel("Add one entry for each type of transaction to generate");
        x++;
        this.add(lblTrantxt, GridC.getc(x, y).insets(5, 5, 5, 5));
        fieldsPan = new JPanel(new GridBagLayout());
        fieldsPan.setPreferredSize(new Dimension(800, 100));
        fieldsPan.setAutoscrolls(true);
        fieldsScroll = new JScrollPane(fieldsPan);
        fieldsScroll.setPreferredSize(new Dimension(800, 100));
        x = 1;
        y++;
        this.add(fieldsScroll, GridC.getc(x, y).colspan(5).insets(5, 5, 5, 5));
        dirty=false;
        loadBtn = new JButton("Load");
        y++;
        this.add(loadBtn, GridC.getc(x, y).insets(5, 5, 5, 5));
        loadBtn.addActionListener(e -> loadSecurities());
        x++;
        JButton btnSave = new JButton("Save Parameters");
        this.add(btnSave, GridC.getc(x, y).insets(5, 5, 5, 5));
        btnSave.addActionListener(e -> {
            params.save();
            dirty=false;
        });


        x++;
        JButton btnClose = new JButton("Close");
        this.add(btnClose, GridC.getc(x++, y).insets(5, 5, 5, 5));
        helpBtn = new JButton("Help");
        helpBtn.setToolTipText("Display help information");
        helpBtn.addActionListener(e -> {
            String url = "https://github.com/mrbray99/moneydanceproduction/wiki/Security-Transaction-Load";
            mdGUI.showInternetURL(url);
        });
        this.add(helpBtn, GridC.getc(x, y).west().insets(10, 10, 10, 10));
        btnClose.addActionListener(e -> close());
    }

    private void chooseFile() {
        String lastDir = preferences.getString(Constants.PROGRAMNAME + Constants.PREFLASTDIRECTORY, "");
        fileChooser.setFileFilter(new FileNameExtensionFilter("csv", "CSV"));
        if (!lastDir.isEmpty()) {
            File lastDirFile = new File(lastDir);
            fileChooser.setCurrentDirectory(lastDirFile);
        }
        int iReturn = fileChooser.showDialog(this, "Select File");
        if (iReturn == JFileChooser.APPROVE_OPTION) {
            securities = fileChooser.getSelectedFile();
            fileName.setText(securities.getAbsolutePath());
        }
        lastDir = fileChooser.getCurrentDirectory().getAbsolutePath();
        preferences.put(Constants.PROGRAMNAME + Constants.PREFLASTDIRECTORY, lastDir);
        preferences.isDirty();
        params = new Parameters2();
        for (FieldLine objLine : params.getLines()) {
            objLine.setAccountObject();
        }
        loadFields();
    }

    private void loadFields() {
        FileReader headerReader;
        BufferedReader headerBufferReader;
        if (fileName.getText().isEmpty()) {
            JFrame fTemp = new JFrame();
            JOptionPane.showMessageDialog(fTemp, "Please Select a file first");
            return;
        }
        try {
            headerReader = new FileReader(fileName.getText());
            headerBufferReader = new BufferedReader(headerReader);
            /*
             * Get the headers
             */
            String inputLine = headerBufferReader.readLine();
            columnData = inputLine.split(",");
            headerBufferReader.close();
        } catch (FileNotFoundException e) {
            JFrame fTemp = new JFrame();
            JOptionPane.showMessageDialog(fTemp, "File " + fileName + " not Found");
            return;
        } catch (IOException e) {
            JFrame fTemp = new JFrame();
            JOptionPane.showMessageDialog(fTemp, "I//O Error whilst reading " + fileName);
            return;
        }
        int iTickerItem = -1;
        int iDateItem = -1;
        int iReferenceItem = -1;
        int iDescItem = -1;
        int iValueItem = -1;
        int iUnitItem = -1;
        for (int i = 0; i < columnData.length; i++) {
            if (columnData[i].equals(params.getTicker()))
                iTickerItem = i;
            tickerField.addItem(columnData[i]);
            if (columnData[i].equals(params.getValue()))
                iValueItem = i;
            valueField.addItem(columnData[i]);
            if (columnData[i].equals(params.getDate()))
                iDateItem = i;
            dateField.addItem(columnData[i]);
            if (columnData[i].equals(params.getReference()))
                iReferenceItem = i;
            txnTypeField.addItem(columnData[i]);
            if (columnData[i].equals(params.getDesc()))
                iDescItem = i;
            descField.addItem(columnData[i]);
            if (columnData[i].equals(params.getUnitsField()))
                iUnitItem = i;
            unitField.addItem(columnData[i]);
        }
        tickerField.setSelectedIndex(iTickerItem == -1 ? 0 : iTickerItem + 1);
        valueField.setSelectedIndex(iValueItem == -1 ? 0 : iValueItem + 1);
        dateField.setSelectedIndex(iDateItem == -1 ? 0 : iDateItem + 1);
        txnTypeField.setSelectedIndex(iReferenceItem == -1 ? 0 : iReferenceItem + 1);
        descField.setSelectedIndex(iDescItem == -1 ? 0 : iDescItem + 1);
        stripExch.setSelected(params.getExch());
        unitField.setSelectedIndex(iUnitItem == -1?0:iUnitItem+1);
        listLines = params.getLines();
        linesButtons = new HashMap<>();
        buildLines();
        stripExch.revalidate();
        tickerField.revalidate();
        valueField.revalidate();
        dateField.revalidate();
        txnTypeField.revalidate();
        descField.revalidate();
        unitField.revalidate();
        fieldsPan.revalidate();
        fieldsScroll.revalidate();
        dirty=false;
        JFrame topFrame = (JFrame) SwingUtilities.getWindowAncestor(this);
        topFrame.pack();
    }

    private void buildLines() {
        int iRow = 1;
        int x = 0;
        linesButtons.clear();
        JLabel lblRTypeH = new JLabel("Transaction Type");
        fieldsPan.add(lblRTypeH, GridC.getc(x, iRow).colspan(2).insets(5, 5, 5, 5));
        x = 2;
        JLabel lblTTypeH = new JLabel("Investment Type");
        fieldsPan.add(lblTTypeH, GridC.getc(x, iRow).insets(5, 5, 5, 5));
        x++;
        JLabel lblAcctH = new JLabel("Category");
        fieldsPan.add(lblAcctH, GridC.getc(x, iRow).insets(5, 5, 5, 5));
        iRow++;
        int iHeight = 100;
        for (FieldLine objLine : listLines) {
            iHeight += 50;
            x = 0;
            JLabel lblType = new JLabel(objLine.getType());
            fieldsPan.add(lblType, GridC.getc(x, iRow).insets(10, 10, 10, 10));
            x++;
            JButton btnChange = new JButton("Chg");
            linesButtons.put(btnChange, objLine.getType());
            fieldsPan.add(btnChange, GridC.getc(x, iRow).insets(10, 10, 10, 10));
            btnChange.addActionListener(e -> {
                JButton btnTemp = (JButton) e.getSource();
                changeTransType(linesButtons.get(btnTemp));  // identifies line
            });
            x++;
            JLabel typeLbl = new JLabel(objLine.getType());
            fieldsPan.add(typeLbl, GridC.getc(x, iRow).insets(10, 10, 10, 10));
            x++;
            JLabel categoryLbl = new JLabel(objLine.getAccountName());
             fieldsPan.add(categoryLbl, GridC.getc(x, iRow).insets(10, 10, 10, 10));
            x++;
            JButton btnDelete = new JButton("Delete");
            btnDelete.addActionListener(this::deleteTransType);
            fieldsPan.add(btnDelete, GridC.getc(x, iRow).insets(10, 10, 10, 10));
            linesButtons.put(btnDelete, objLine.getType());
            iRow++;
        }
        x = 0;
        addBtn = new JButton("Add Transaction Type");
        addBtn.addActionListener(e -> addTran());
        fieldsPan.add(addBtn, GridC.getc(x, iRow).insets(10, 10, 10, 10));
        fieldsPan.revalidate();
        fieldsPan.setPreferredSize(new Dimension(800, iHeight));
        if (iHeight > 400)
            iHeight = 300;
        fieldsScroll.setPreferredSize(new Dimension(800, iHeight));

    }

    private void deleteTransType(ActionEvent e) {
        String strType = linesButtons.get(e.getSource());
        params.deleteField(strType);
        fieldsPan.removeAll();
        buildLines();
        fieldsPan.revalidate();
        fieldsScroll.revalidate();
        JFrame topFrame = (JFrame) SwingUtilities.getWindowAncestor(this);
        topFrame.pack();
        dirty=true;

    }

    private void changeTransType(String strType) {
        displayTran(strType);
    }

    private void addTran() {
        displayTran(Constants.NEWTRAN);
    }

    private void displayTran(String strTran) {
        int x = 0;
        int y = 0;
        FieldLine currentLine = null;
        JPanel panInput = new JPanel(new GridBagLayout());
        JLabel lblType = new JLabel("Enter Transaction Type");
        panInput.add(lblType, GridC.getc(x, y).insets(10, 10, 10, 10));
        JTextField txtType = new JTextField();
        txtType.setColumns(20);
        x++;
        panInput.add(txtType, GridC.getc(x, y).insets(10, 10, 10, 10));
        x++;
        JLabel lblMult = new JLabel("Type");
        panInput.add(lblMult, GridC.getc(x, y).insets(10, 10, 10, 10));
        x++;
        JComboBox<String> transTypes = new JComboBox<>(Constants.TRANSTYPES);
        if (!unitsPresent){
            transTypes.removeItem(Constants.INVESTMENT_BUY);
            transTypes.removeItem(Constants.INVESTMENT_SELL);
        }
        panInput.add(transTypes, GridC.getc(x, y).insets(10, 10, 10, 10));
        x++;

        panInput.add(treeView, GridC.getc(x, y).insets(10, 10, 10, 10));
        if (!strTran.equals(Constants.NEWTRAN)) {
            currentLine = params.matchType(strTran);
            if (currentLine != null) {
                txtType.setText(currentLine.getType());
                transTypes.setSelectedIndex(currentLine.getTranType());
                TreeNode[] path = acctPaths.get(currentLine.getAccountName());
                TreePath treePath = new TreePath(path);
                categoryTree.expandPath(treePath);
                categoryTree.setSelectionPath(treePath);
                categoryTree.scrollPathToVisible(treePath);
            }
        }
        while (true) {
            int iResult = JOptionPane.showConfirmDialog(null, panInput,
                    "Enter Transaction Type Details", JOptionPane.OK_CANCEL_OPTION);
            if (iResult == JOptionPane.OK_OPTION) {
                String strType = txtType.getText();
                if (strType.isEmpty()) {
                    JOptionPane.showMessageDialog(null, "Transaction Type can not be blank");
                    continue;
                }
                FieldLine objTempLine = params.matchType(strType);
                if (objTempLine != null) {
                    if (currentLine != null && currentLine != objTempLine)
                        JOptionPane.showMessageDialog(null, "Transaction Type already defined");
                    continue;
                }
                if (currentLine != null) {
                    String strOldType = currentLine.getType();
                    currentLine.setType(strType);
                    currentLine.setTranType(transTypes.getSelectedIndex());
                    String acctName = getFullPath(selectedCategory);
                    currentLine.setAccount(acctName, accounts.get(acctName));
                    for (Map.Entry<Object, String> entry : linesButtons.entrySet()) {
                        String strValue = entry.getValue();
                        if (strValue.equals(strOldType))
                            entry.setValue(strType);
                    }
                } else {
                    dirty=true;
                    String name =getFullPath(selectedCategory);
                    params.addField(strType,
                            name,
                            accounts.get(name),
                            transTypes.getSelectedIndex());
                }
                break;
            }
            if (iResult == JOptionPane.CANCEL_OPTION)
                break;
        }
        fieldsPan.removeAll();
        buildLines();
        fieldsPan.revalidate();
        fieldsScroll.revalidate();
        JFrame topFrame = (JFrame) SwingUtilities.getWindowAncestor(this);
        topFrame.pack();

    }

    private void loadSecurities() {
        if (fileName.getText().isEmpty()) {
            JFrame fTemp = new JFrame();
            JOptionPane.showMessageDialog(fTemp, "Please Select a file first");
            return;
        }

        if (txnTypeField.getSelectedIndex() == 0 ||
                tickerField.getSelectedIndex() == 0 ||
                dateField.getSelectedIndex() == 0 ||
                valueField.getSelectedIndex() == 0 ||
                descField.getSelectedIndex() == 0) {
            JFrame fTemp = new JFrame();
            JOptionPane.showMessageDialog(fTemp, "All fields must be selected");
            return;
        }
        int[] iSelected = new int[columnData.length + 1];
        iSelected[txnTypeField.getSelectedIndex()] = 1;
        if (iSelected[tickerField.getSelectedIndex()] != 0) {
            JFrame fTemp = new JFrame();
            JOptionPane.showMessageDialog(fTemp, "No field can be selected twice");
            return;
        } else
            iSelected[tickerField.getSelectedIndex()] = 1;
        if (iSelected[dateField.getSelectedIndex()] != 0) {
            JFrame fTemp = new JFrame();
            JOptionPane.showMessageDialog(fTemp, "No field can be selected twice");
            return;
        } else
            iSelected[dateField.getSelectedIndex()] = 1;
        if (iSelected[descField.getSelectedIndex()] != 0) {
            JFrame fTemp = new JFrame();
            JOptionPane.showMessageDialog(fTemp, "No field can be selected twice");
            return;
        } else
            iSelected[descField.getSelectedIndex()] = 1;
        if (iSelected[valueField.getSelectedIndex()] != 0) {
            JFrame fTemp = new JFrame();
            JOptionPane.showMessageDialog(fTemp, "No field can be selected twice");
            return;
        } else
            iSelected[valueField.getSelectedIndex()] = 1;
        //Create and set up the window.
        if (accountsCB.getSelectedIndex() == 0) {
            JFrame fTemp = new JFrame();
            JOptionPane.showMessageDialog(fTemp, "Please select an account");
            return;
        }
        JFrame frame = new JFrame("Load Security Prices");
        frame.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
        Account acct = investAccts.get(accountsCB.getSelectedItem());
        loadTickers(acct);
        loadWindow = new loadPricesWindow(fileName, acct, params);
        frame.getContentPane().add(loadWindow);

        //Display the window.
        frame.pack();
        frame.setLocationRelativeTo(null);
        frame.setVisible(true);

    }

    private void close() {
        if (dirty) {
            int iResult = JOptionPane.showInternalConfirmDialog(null,"Parameters have been changed, do you wish to abandon the changes?", "Load Security Transactions",JOptionPane.YES_NO_OPTION);
            if (iResult != JOptionPane.YES_OPTION) {
                return;
            }
        }
        this.setVisible(false);
        if (loadWindow != null)
            loadWindow.close();
        JFrame topFrame = (JFrame) SwingUtilities.getWindowAncestor(this);
        topFrame.dispose();
    }

    /*
     * Create an array of Investment Accounts for combo box
     */
    private void loadAccounts(Account parentAcct, String strName, DefaultMutableTreeNode node) {
        DefaultMutableTreeNode newNode  = node;
        int sz = parentAcct.getSubAccountCount();
        String ticker;
        for (int i = 0; i < sz; i++) {
            Account acct = parentAcct.getSubAccount(i);
            if (acct == null)
                continue;
            if (acct.getAccountType() == Account.AccountType.INVESTMENT) {
                investAccts.put(acct.getAccountName(), acct);
            }
            String strEntry = strName.isEmpty() ? acct.getAccountName() : strName + ":" + acct.getAccountName();
            if (acct.getAccountType() == Account.AccountType.EXPENSE ||
                    acct.getAccountType() == Account.AccountType.INCOME) {
                newNode= new DefaultMutableTreeNode();
                node.add(newNode);
                NodeEntry nodeEntry = new NodeEntry(acct,strEntry);
                newNode.setUserObject(nodeEntry);
                acctPaths.put(strEntry,newNode.getPath());
                accounts.put(strEntry, acct);
            }
            loadAccounts(acct, strEntry, newNode);
        }
    }

    private Image getIcon(String icon) {
        try {
            ClassLoader cl = getClass().getClassLoader();
            java.io.InputStream in =
                    cl.getResourceAsStream("/com/moneydance/modules/features/loadsectrans/" + icon);
            if (in != null) {
                ByteArrayOutputStream bout = new ByteArrayOutputStream(1000);
                byte[] buf = new byte[256];
                int n;
                while ((n = in.read(buf, 0, buf.length)) >= 0)
                    bout.write(buf, 0, n);
                return Toolkit.getDefaultToolkit().createImage(bout.toByteArray());
            }
        } catch (Throwable e) {
        }
        return null;
    }

    /*
     * Create table of Securities keyed by Ticker
     */
    private void loadTickers(Account parentAcct) {
        int sz = parentAcct.getSubAccountCount();
        String ticker;
        for (int i = 0; i < sz; i++) {
            Account acct = parentAcct.getSubAccount(i);
            if (acct==null)
                continue;
            if (acct.getAccountType() == Account.AccountType.SECURITY) {
                CurrencyType ctTicker = acct.getCurrencyType();
                if (ctTicker != null) {
                    if (!ctTicker.getTickerSymbol().isEmpty()) {
                        CurrencyType tickerCurrency = acct.getCurrencyType();
                        ticker = tickerCurrency.getTickerSymbol();
                        if (params.getExch()){
                            int iPeriod = ticker.indexOf('.');
                            if (iPeriod > -1) {
                                ticker = ticker.substring(0,iPeriod);
                            }
                            else {
                                iPeriod = ticker.indexOf(':');
                                if (iPeriod > -1) {
                                    ticker= ticker.substring(0,iPeriod);
                                }
                            }
                        }
                        Main.mapAccounts.put(ticker, acct);
                    }
                }
            }
            loadTickers(acct);
        }
    }
    private String getFullPath(Account account){
        String fullPath = account.getAccountName();
        Account parent = account.getParentAccount();
        while (parent != null && parent != rootAccount){
            fullPath = parent.getAccountName()+":"+fullPath;
            parent = parent.getParentAccount();
        }
        return fullPath;
    }
    @Override
    public void valueChanged(TreeSelectionEvent e) {
        Object component = categoryTree.getLastSelectedPathComponent();
        DefaultMutableTreeNode node;
        NodeEntry entry;
        if (component == null)
            //Nothing is selected.
            return;
        if (component instanceof DefaultMutableTreeNode){
            node = (DefaultMutableTreeNode) component;
            entry= (NodeEntry)node.getUserObject();
            selectedCategory = entry.getAccount();
        }
    }

}
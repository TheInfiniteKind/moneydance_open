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
package com.moneydance.modules.features.qifloader;


import java.awt.Dimension;
import java.awt.GridBagLayout;
import java.awt.HeadlessException;
import java.awt.Image;
import java.awt.Toolkit;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.BufferedReader;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.*;

import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JComboBox;
import javax.swing.JFileChooser;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTextField;
import javax.swing.LookAndFeel;
import javax.swing.SwingUtilities;
import javax.swing.filechooser.FileNameExtensionFilter;

import com.infinitekind.moneydance.model.*;
import com.infinitekind.util.DateUtil;
import com.moneydance.awt.GridC;
import com.moneydance.awt.JDateField;
import com.moneydance.modules.features.mrbutil.MRBPreferences2;


public class FileSelectWindow extends JPanel {
    private static final long serialVersionUID = 1L;
    private JTextField fileName;
    private JButton loadBtn;
    private JButton chooseBtn;
    private JComboBox<String> accountsCB;

    JScrollPane fieldsScroll;
    private JFileChooser fileChooser = null;
    private File securities;
    private Map<String, Account> mapNames = new HashMap<String, Account>();
    private String[] names;
    private LookAndFeel previousLF;

    private List<Account> listCategories;
    private Map<String, Account> mapAccts;
    private SortedMap<String, Account> categories= new TreeMap<>();
    private String name = "";
    private Account acct;
    private List<QIFEntry> transactions = new ArrayList<>();
    private List<GenerateTransaction> listTrans= new ArrayList<>();
    private MRBPreferences2 preferences;

    public FileSelectWindow() throws HeadlessException {
        listCategories = new ArrayList<Account>();
        mapAccts = new HashMap<String, Account>();
        mapNames.put("Please Select an Account", null);
        loadAccounts(Main.context.getRootAccount(), name);
        fileChooser = new JFileChooser();
        names = mapNames.keySet().toArray(new String[0]);
        preferences = MRBPreferences2.getInstance();
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
        x = +4;
        this.add(chooseBtn, GridC.getc(x, y).insets(10, 5, 0, 0));
        chooseBtn.setBorder(javax.swing.BorderFactory.createLineBorder(this.getBackground()));
        chooseBtn.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                chooseFile();
            }
        });


        JLabel lblAccounts = new JLabel("Which Account : ");
        x = 1;
        y++;
        this.add(lblAccounts, GridC.getc(x, y).insets(10, 0, 0, 0));

        accountsCB = new JComboBox<String>(names);
        x++;
        this.add(accountsCB, GridC.getc(x, y).insets(5, 0, 0, 0));


        loadBtn = new JButton("Load");
        y++;
        this.add(loadBtn, GridC.getc(x, y).insets(5, 5, 5, 5));
        loadBtn.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                loadSecurities();
            }
        });
        x++;
        JButton btnClose = new JButton("Close");
        this.add(btnClose, GridC.getc(x, y).insets(5, 5, 5, 5));
        btnClose.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                close();
            }
        });
    }

    private void chooseFile() {
        fileChooser.setFileFilter(new FileNameExtensionFilter("qif", "QIF"));
        String lastDirectory = preferences.getString(Constants.PROGRAMNAME+"."+Constants.LASTDIR,"");
        if (!lastDirectory.isEmpty()) {
            File currentDirectory = new File(lastDirectory);
            if (currentDirectory!=null && currentDirectory.exists()&&currentDirectory.isDirectory())
                fileChooser.setCurrentDirectory(currentDirectory);
        }
        int iReturn = fileChooser.showDialog(this, "Select File");
        if (iReturn == JFileChooser.APPROVE_OPTION) {
            securities = fileChooser.getSelectedFile();
            fileName.setText(securities.getAbsolutePath());
            preferences.put(Constants.PROGRAMNAME+"."+Constants.LASTDIR,fileChooser.getCurrentDirectory().getAbsolutePath());
        }
    }


    private void loadSecurities() {
        if (fileName.getText().equals("")) {
            JFrame fTemp = new JFrame();
            JOptionPane.showMessageDialog(fTemp, "Please Select a file first");
            return;
        }
        //Create and set up the window.
        if (accountsCB.getSelectedIndex() == 0) {
            JFrame fTemp = new JFrame();
            JOptionPane.showMessageDialog(fTemp, "Please select an account");
            return;
        }
        acct = mapNames.get(accountsCB.getSelectedItem());
        if (loadFile(fileName)) {
            listTrans.clear();
            for (QIFEntry entry : transactions) {
                entry.setAmount(entry.getAmount() * -1.0);
                Long amount = Math.round(entry.getAmount() * 100);
                listTrans.add(new GenerateTransaction(Constants.PARENT, acct, entry.getDate(),
                        amount, entry.getDescription(), entry.getCheque(), entry.getCleared(), ""));
                Account category = null;
                if (entry.getCategory().isEmpty())
                    category = acct.getDefaultCategory();
                else {
                    String cat = entry.getCategory().toUpperCase();
                    if (categories.containsKey(cat))
                        category = categories.get(cat);
                    else
                        category = acct.getDefaultCategory();
                }
                listTrans.add(new GenerateTransaction(Constants.SPLIT, category,
                        entry.getDate(), -amount, entry.getDescription(), entry.getCheque(), entry.getCleared(), ""));
            }
			int i = 0;
			while (i<listTrans.size()) {
				if (listTrans.get(i).getType() == Constants.PARENT) {
					GenerateTransaction transLine = listTrans.get(i);
					GenerateTransaction transLine2 = listTrans.get(i+1);
					ParentTxn ptTran = ParentTxn.makeParentTxn(Main.acctBook, transLine.getDate(), transLine.getDate(), transLine.getDate(), transLine.getCheque(), acct, transLine.getDesc(),"" ,(long)-1,transLine.getStatus());

					/*
					 * Amount needs to be negative as SplitTxn will negate parent amount						  *
					 */
					SplitTxn stTran1 = SplitTxn.makeSplitTxn(ptTran,-transLine.getAmount(),-transLine.getAmount(),1.0,transLine2.getAccount(),transLine.getDesc(),(long) -1,transLine.getStatus());
					ptTran.addSplit(stTran1);
					ptTran.setIsNew(true);
					transLine.setIndex(i);
					transLine2.setIndex(i+1);
					i+=2;
					ptTran.syncItem();
				}
				else
					i++;
			}
            JOptionPane.showMessageDialog(null,transactions.size()+" transactions loaded into account "+acct.getAccountName());
        }


    }

    private void close() {
        this.setVisible(false);
        JFrame topFrame = (JFrame) SwingUtilities.getWindowAncestor(this);
        topFrame.dispose();
    }

    /*
     * Create an array of Investment Accounts for combo box
     */
    private void loadAccounts(Account parentAcct, String strName) {
        int sz = parentAcct.getSubAccountCount();
        for (int i = 0; i < sz; i++) {
            Account acct = parentAcct.getSubAccount(i);
            if (acct.getAccountType() == Account.AccountType.BANK ||
                    acct.getAccountType() == Account.AccountType.CREDIT_CARD) {
                mapNames.put(acct.getAccountName(), acct);
            }
            String strEntry = strName.equals("") ? acct.getAccountName() : strName + ":" + acct.getAccountName();
            if (acct.getAccountType() == Account.AccountType.EXPENSE ||
                    acct.getAccountType() == Account.AccountType.INCOME) {
                listCategories.add(acct);
                categories.put(acct.getAccountName().toUpperCase(), acct);
                mapAccts.put(strEntry, acct);
            }
            loadAccounts(acct, strEntry);
        }
    }

    private Image getIcon(String icon) {
        try {
            ClassLoader cl = getClass().getClassLoader();
            java.io.InputStream in =
                    cl.getResourceAsStream("/com/moneydance/modules/features/qifloader/" + icon);
            if (in != null) {
                ByteArrayOutputStream bout = new ByteArrayOutputStream(1000);
                byte buf[] = new byte[256];
                int n = 0;
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
        for (int i = 0; i < sz; i++) {
            Account acct = parentAcct.getSubAccount(i);
            if (acct.getAccountType() == Account.AccountType.SECURITY) {
                CurrencyType ctTicker = acct.getCurrencyType();
                if (ctTicker != null) {
                    if (!ctTicker.getTickerSymbol().equals("")) {
                        Main.mapAccounts.put(ctTicker.getTickerSymbol(), acct);
                    }
                }
            }
            loadTickers(acct);
        }
    }

    /*
     * try to load selected file
     */
    private boolean loadFile(JTextField txtFileName) {
        try {
            FileReader frPrices = new FileReader(txtFileName.getText());
            BufferedReader brPrices = new BufferedReader(frPrices);
            /*
             * Get the file type
             */
            String strLine = brPrices.readLine();
            if (strLine.charAt(0) != '!') {
                JFrame fTemp = new JFrame();
                JOptionPane.showMessageDialog(fTemp, "File Type missing");
                return false;
            }
            QIFEntry entry = new QIFEntry();
            transactions.clear();
            while ((strLine = brPrices.readLine()) != null) {
                switch (strLine.charAt(0)) {
                    case 'D':
                        String datestr = strLine.substring(1);
                        JDateField dateFld = new JDateField(Main.cdate);
                        int date = DateUtil.convertDateToInt(dateFld.getDateFromString(datestr));
                        entry.setDate(date);
                        break;
                    case 'P':
                        entry.setDescription(strLine.substring(1));
                        break;
                    case 'T':
                        Double value;
                        try {
                            value = Double.valueOf(strLine.substring(1));
                            entry.setAmount(value);
                        } catch (Exception e) {
                            value = 0.0;
                        }
                        entry.setAmount(value);
                        break;
                    case 'N':
                        entry.setCheque(strLine.substring(1));
                        break;
                    case 'C':
                        switch (strLine.charAt(1)) {
                            case ' ':
                                entry.setCleared(AbstractTxn.STATUS_UNRECONCILED);
                                break;
                            case '*':
                            case 'c':
                                entry.setCleared(AbstractTxn.STATUS_CLEARED);
                                break;
                            case 'X':
                            case 'R':
                                entry.setCleared(AbstractTxn.STATUS_RECONCILING);
                                break;
                            default:
                                entry.setCleared(AbstractTxn.STATUS_UNRECONCILED);
                                break;
                        }
                        break;
                    case 'L':
                        entry.setCategory(strLine.substring(1).trim());
                        break;
                    case '^':
                        transactions.add(entry);
                        entry = new QIFEntry();
                }
            }
            brPrices.close();
        } catch (FileNotFoundException e) {
            JFrame fTemp = new JFrame();
            JOptionPane.showMessageDialog(fTemp, "File " + txtFileName + " not Found");
            close();
            return false;
        } catch (IOException e) {
            JFrame fTemp = new JFrame();
            JOptionPane.showMessageDialog(fTemp, "I//O Error whilst reading " + txtFileName);
            close();
            return false;
        }
        return true;
    }
}
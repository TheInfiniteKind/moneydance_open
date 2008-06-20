
package com.moneydance.modules.features.txtimport;

import com.moneydance.apps.md.model.Account;
import com.moneydance.awt.*;
import javax.swing.*;
import javax.swing.border.*;
import java.awt.*;
import java.awt.event.*;

public class SelectOptionsPane
  extends JPanel
  implements WizardPane
{
  private Wizard wizard;
  private Resources rr;
  private ImportState importState;

  private JComboBox delimiterChoice;
  private JComboBox dateFormatChoice;
  private JComboBox accountChoice;
  private JComboBox decimalPointChoice;
  
  public SelectOptionsPane(Resources rr, ImportState importState) {
    this.rr = rr;
    this.importState = importState;
    
    accountChoice = new JComboBox(importState.getAccountList());
    delimiterChoice = new JComboBox(ImportState.DELIMITER_NAMES);
    dateFormatChoice = new JComboBox(ImportState.DATE_FORMATS);
    decimalPointChoice = new JComboBox(ImportState.DECIMAL_POINT_NAMES);

    Account defaultAcct = importState.getAccount();
    if(defaultAcct!=null) accountChoice.setSelectedItem(defaultAcct);
    delimiterChoice.setSelectedIndex(importState.getDelimiterIdx());
    dateFormatChoice.setSelectedIndex(importState.getDateFormatIdx());
    decimalPointChoice.setSelectedIndex(importState.getDecimalPointIdx());

    setLayout(new GridBagLayout());

    int y = 0;
    add(Box.createVerticalStrut(10),
        AwtUtil.getConstraints(0,y++,0,1,1,1,false,false));

    add(new JLabel(rr.getString("account_cb"), JLabel.RIGHT),
        AwtUtil.getConstraints(0,y,0,0,1,1,true,true));
    add(accountChoice,
        AwtUtil.getConstraints(1,y++,1,0,1,1,true,true));

    add(new JLabel(rr.getString("fields_delimiter"), JLabel.RIGHT),
        AwtUtil.getConstraints(0,y,0,0,1,1,true,true));
    add(delimiterChoice,
        AwtUtil.getConstraints(1,y++,1,0,1,1,true,true));

    add(new JLabel(rr.getString("date_fmt"), JLabel.RIGHT),
        AwtUtil.getConstraints(0,y,0,0,1,1,true,true));
    add(dateFormatChoice,
        AwtUtil.getConstraints(1,y++,1,0,1,1,true,true));

    add(new JLabel(rr.getString("decimal_point"), JLabel.RIGHT),
        AwtUtil.getConstraints(0,y,0,0,1,1,true,true));
    add(decimalPointChoice,
        AwtUtil.getConstraints(1,y++,1,0,1,1,true,true));

    add(Box.createVerticalStrut(10),
        AwtUtil.getConstraints(0,y++,0,1,1,1,false,false));
  }


  /** is called when this pane is made visible.   The wiz argument
      provides a reference to the Wizard object that this pane is
      a part of. */
  public void activated(Wizard wiz) {
    this.wizard = wiz;
    this.wizard.setNextButtonEnabled(accountChoice.getItemCount()>0);
  }

  /** Is called when the 'next' button is clicked to store
      the values entered in this pane.  Returns the next pane
      that the wizard should go to.  Returns null if the user
      should not be sent to the next pane. */
  public WizardPane storeValues() {
    importState.setAccount((Account)accountChoice.getSelectedItem());
    importState.setDateFormat(ImportState.DATE_FORMAT_IDS[dateFormatChoice.getSelectedIndex()]);
    importState.setDelimiter(ImportState.DELIMITERS[delimiterChoice.getSelectedIndex()]);
    importState.setDecimalPoint(ImportState.DECIMAL_POINTS[decimalPointChoice.getSelectedIndex()]);

    return new SelectFieldsPane(rr, importState);
  }

  /** Is called when no longer in use so that things can be
      cleaned up. */
  public void goneAway() {}
  
  /** Get the component that contains the GUI for this pane. */
  public JComponent getPanel() {
    return this;
  }
  
  /** Get whether or not this pane is the last one. */
  public boolean isLastPane() {
    return false;
  }


}







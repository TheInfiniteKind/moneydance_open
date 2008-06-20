
package com.moneydance.modules.features.txtimport;

import com.moneydance.awt.*;
import javax.swing.*;
import javax.swing.border.*;
import java.awt.*;
import java.awt.event.*;
import java.util.*;

public class SelectFieldsPane
  extends JPanel
  implements WizardPane,
             ActionListener
{
  private Wizard wizard;
  private Resources rr;
  private ImportState importState;

  private JButton moreFieldsButton;
  private JButton lessFieldsButton;

  private JPanel fieldPanel;
  private JComboBox[] fieldChoices;
  private JLabel[] fieldLabels;
  private String fieldNames[];
  private int numFields = 0;
  
  public SelectFieldsPane(Resources rr, ImportState importState) {
    this.rr = rr;
    this.importState = importState;

    fieldNames = new String[ImportState.FIELD_KEYS.length];
    for(int i=0; i<fieldNames.length; i++) {
      fieldNames[i] = rr.getString(ImportState.FIELD_KEYS[i]);
    }

    fieldPanel = new JPanel(new GridBagLayout());
    moreFieldsButton = new JButton(rr.getString("more_fields"));
    lessFieldsButton = new JButton(rr.getString("less_fields"));
    fieldChoices = new JComboBox[15];
    fieldLabels = new JLabel[15];
    numFields = 0;
    
    setLayout(new GridBagLayout());

    int y = 0;
    add(Box.createVerticalStrut(6),
        AwtUtil.getConstraints(0,y++,0,0,1,1,false,false));

    add(new JTextPanel(rr.getString("field_exp")),
        AwtUtil.getConstraints(0,y++,1,0,3,1,true,true));

    add(Box.createVerticalStrut(10),
        AwtUtil.getConstraints(0,y++,0,0,1,1,false,false));

    add(fieldPanel,
        AwtUtil.getConstraints(0,y,1,1,1,2,true,true));

    add(Box.createHorizontalStrut(10),
        AwtUtil.getConstraints(1,y,0,0,1,1,false,false));
    add(lessFieldsButton,
        AwtUtil.getConstraints(2,y++,0,1,1,1,false,false));
    add(moreFieldsButton,
        AwtUtil.getConstraints(2,y++,0,1,1,1,false,false));
    
    add(Box.createVerticalStrut(8),
        AwtUtil.getConstraints(0,y++,1,0,1,1,false,false));

    byte initialFields[] = importState.getFields();
    for(int i=0; i<initialFields.length; i++) {
      addField(initialFields[i]);
    }
    
    lessFieldsButton.addActionListener(this);
    moreFieldsButton.addActionListener(this);
  }

  private synchronized void addField(byte fieldID) {
    if(numFields>=fieldChoices.length)
      return;
    
    int defaultFieldIndex = 0;
    for(int i=0; i<ImportState.FIELD_IDS.length; i++) {
      if(ImportState.FIELD_IDS[i]==fieldID) {
        defaultFieldIndex = i;
        break;
      }
    }
    int fieldIdx = numFields++;
    fieldChoices[fieldIdx] = new JComboBox(fieldNames);
    fieldChoices[fieldIdx].setSelectedIndex(defaultFieldIndex);
    fieldLabels[fieldIdx] = new JLabel(rr.getString("field")+' '+(fieldIdx+1)+": ",
                                       JLabel.RIGHT);
    fieldPanel.add(fieldLabels[fieldIdx],
                   AwtUtil.getConstraints(0,fieldIdx,0,0,1,1,true,false));
    fieldPanel.add(fieldChoices[fieldIdx],
                   AwtUtil.getConstraints(1,fieldIdx,0,0,1,1,true,false));
  }

  private synchronized void removeField() {
    if(numFields<=0)
      return;

    int fieldIdx = --numFields;
    fieldPanel.remove(fieldChoices[fieldIdx]);
    fieldPanel.remove(fieldLabels[fieldIdx]);
    fieldChoices[fieldIdx] = null;
    fieldLabels[fieldIdx] = null;
  }

  /** is called when this pane is made visible.   The wiz argument
      provides a reference to the Wizard object that this pane is
      a part of. */
  public void activated(Wizard wiz) {
    this.wizard = wiz;
    this.wizard.setNextButtonEnabled(true);
  }

  /** Is called when the 'next' button is clicked to store
      the values entered in this pane.  Returns the next pane
      that the wizard should go to.  Returns null if the user
      should not be sent to the next pane. */
  public WizardPane storeValues() {
    byte fieldsToImport[] = null;
    synchronized(this) {
      fieldsToImport = new byte[numFields];
      for(int i=0; i<fieldsToImport.length; i++) {
        fieldsToImport[i] = ImportState.FIELD_IDS[fieldChoices[i].getSelectedIndex()];
      }
    }
    importState.setFields(fieldsToImport);

    try {
      importState.doImport();
    } catch (Throwable t) {
      t.printStackTrace(System.err);
      JOptionPane.
        showMessageDialog(this, 
                          rr.getString("error")+": "+t,
                          rr.getString("error"),
                          JOptionPane.ERROR_MESSAGE);
      return null;
    }
    
    return this;
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
    return true;
  }

  public void actionPerformed(ActionEvent evt) {
    Object src = evt.getSource();
    if(src==lessFieldsButton) {
      removeField();
      validate();
      repaint();
    } else if(src==moreFieldsButton) {
      addField(ImportState.NOTHING);
      validate();
      repaint();
    }
  }

}







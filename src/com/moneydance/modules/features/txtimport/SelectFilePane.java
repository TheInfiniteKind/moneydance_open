package com.moneydance.modules.features.txtimport;


import com.moneydance.awt.*;
import javax.swing.*;
import javax.swing.border.*;
import java.awt.*;
import java.awt.event.*;
import java.io.File;

public class SelectFilePane
  extends JPanel
  implements WizardPane,
             ActionListener
{
  private Wizard wizard;
  private Resources rr;
  private ImportState importState;

  private JTextField fileField;
  private JComboBox encodingChoice;
  private JButton browseButton;
  
  public SelectFilePane(Resources rr, ImportState importState) {
    this.rr = rr;
    this.importState = importState;

    fileField = new JTextField("", 25);
    fileField.setText(importState.getFile().getAbsolutePath());
    browseButton = new JButton(rr.getString("browse"));
    encodingChoice = new JComboBox(ImportState.FILE_ENCODINGS);
    encodingChoice.setSelectedItem(importState.getFileEncoding());
    
    setLayout(new GridBagLayout());

    add(new JLabel(rr.getString("choose_file"), JLabel.CENTER),
        AwtUtil.getConstraints(0,0,1,1,2,1,true,true));
    add(fileField,
        AwtUtil.getConstraints(0,1,1,0,1,1,true,true));
    add(browseButton,
        AwtUtil.getConstraints(1,1,0,0,1,1,true,true));
    add(Box.createVerticalStrut(8),
        AwtUtil.getConstraints(0,2,0,0,1,1,false,false));
    JPanel tmp = new JPanel(new GridBagLayout());
    tmp.add(new JLabel(rr.getString("file_encoding"), JLabel.RIGHT),
            AwtUtil.getConstraints(0,0,0,0,1,1,true,true));
    tmp.add(encodingChoice,
            AwtUtil.getConstraints(1,0,1,0,1,1,true,false));
    add(tmp,
        AwtUtil.getConstraints(0,3,1,0,2,1,true,true));
    add(Box.createVerticalStrut(10),
        AwtUtil.getConstraints(0,4,0,1,1,1,false,false));
    browseButton.addActionListener(this);
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
    String fileName = fileField.getText();
    try {
      File f = new File(fileName);
      if(!f.exists() || !f.canRead()) {
        JOptionPane.
          showMessageDialog(this, 
                            rr.getString("error")+": "+rr.getString("cant_read_file"),
                            rr.getString("error"),
                            JOptionPane.ERROR_MESSAGE);
        return null;
      }
      importState.setFile(f);
      importState.setFileEncoding(String.valueOf(encodingChoice.getSelectedItem()));
      
      return new SelectOptionsPane(rr, importState);
    } catch (Exception e) {
      JOptionPane.
        showMessageDialog(this, 
                          rr.getString("error")+": "+String.valueOf(e),
                          rr.getString("error"),
                          JOptionPane.ERROR_MESSAGE);
    }
    return null;
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


  private void browseForFile() {
    FileDialog fch = new FileDialog(AwtUtil.getFrame(this), rr.getString("choose_file"));
    fch.setVisible(true);
    String file = fch.getFile();
    String dir = fch.getDirectory();
    if(file==null || dir==null)
      return;
    if(!dir.endsWith(File.separator))
      dir = dir+File.separator;
    fileField.setText(dir + file);
  }

  public void actionPerformed(ActionEvent evt) {
    if(evt.getSource()==browseButton) {
      browseForFile();
    }
  }
  
}







/************************************************************\
 *      Copyright (C) 2008 Reilly Technologies, L.L.C.      *
\************************************************************/

package com.moneydance.modules.features.balpred;

import com.moneydance.awt.*;
import javax.swing.*;
import javax.swing.border.*;
import java.awt.*;
import java.awt.event.*;
import java.util.*;

public class Wizard
  extends JDialog
  implements ActionListener
{
  private JButton nextButton;
  private JButton cancelButton;

  private Resources resources;
  private JPanel contentPanel;
  private CardLayout cardLayout;
  private Stack paneStack = new Stack();
  private Vector allPanes = new Vector();
  private WizardPane currentPane;

  public Wizard(Frame parentFrame, Resources resources,
                String title, WizardPane firstPane, boolean modal) {
    super(parentFrame, title, modal);
    this.resources = resources;
    this.currentPane = firstPane;

    JPanel mainPanel = new JPanel(new GridBagLayout());
    cardLayout = new CardLayout(10, 10);
    contentPanel = new JPanel(cardLayout);
    mainPanel.setBorder(new EmptyBorder(10,10,10,10));

    nextButton = new JButton(resources.getString("next")+" >>");
    cancelButton = new JButton(resources.getString("cancel"));
    nextButton.setEnabled(false);

    getContentPane().add(mainPanel);

    mainPanel.add(contentPanel,
                  AwtUtil.getConstraints(0,1,1,1,4,1,true,true));
    
    mainPanel.add(cancelButton,
                  AwtUtil.getConstraints(0,2,0,0,1,1,true,true));
    mainPanel.add(new JLabel(" "),
                  AwtUtil.getConstraints(1,2,1,0,1,1,true,true));
    mainPanel.add(nextButton,
                  AwtUtil.getConstraints(3,2,0,0,1,1,true,true));

    nextButton.addActionListener(this);
    cancelButton.addActionListener(this);
    

    // setup the first pane in the wizard...
    contentPanel.add(currentPane.getPanel(), String.valueOf(paneStack.size()));
    cardLayout.show(contentPanel, String.valueOf(paneStack.size()));
    if(currentPane.isLastPane()) {
      nextButton.setLabel(resources.getString("finish"));
    }
    currentPane.activated(this);

    setDefaultCloseOperation(JFrame.DO_NOTHING_ON_CLOSE);
    enableEvents(WindowEvent.WINDOW_CLOSING);
    enableEvents(WindowEvent.WINDOW_OPENED);

    pack();
    setSize(360, 300);
    
    //AwtUtil.setWindowPosition(this, parentFrame);
    AwtUtil.centerWindow(this);
  }
  
  public final void processEvent(AWTEvent evt) {
    int id = evt.getID();
    if(id==WindowEvent.WINDOW_CLOSING) {
      goAwayNow();
      return;
    } else if(id==WindowEvent.WINDOW_OPENED) {
      requestFocus();
    }
    super.processEvent(evt);
  }
  
  public void actionPerformed(ActionEvent evt) {
    Object src = evt.getSource();
    if(src==nextButton) {
      nextButtonPressed();
    } else if(src==cancelButton) {
      goAwayNow();
    }
  }

  public void goneAway() {
    for(Enumeration en=allPanes.elements(); en.hasMoreElements(); ) {
      ((WizardPane)en.nextElement()).goneAway();
    }
  }

  /** Gets rid of the window without calling goingAway() */
  protected final void goAwayNow() {
    if(isVisible())
      super.setVisible(false);

    try {
      goneAway();
    } catch (Throwable e) {
      e.printStackTrace(System.err);
    }
  }

  private void nextButtonPressed() {
    try {
      if(currentPane.isLastPane()) {
        if(currentPane.storeValues()!=null) {
          goAwayNow();
          return;
        } else {
          return;
        }
      }

      // do any necessary processing before continuing to the next pane
      WizardPane nextPane = currentPane.storeValues();
      if(nextPane==null)
        return;
      if(!allPanes.contains(nextPane))
        allPanes.addElement(nextPane);

      // store the current pane, in case we need to go back to it
      paneStack.push(currentPane);

      // go to the next pane
      nextButton.setEnabled(false);
      contentPanel.add(nextPane.getPanel(), String.valueOf(paneStack.size()));
      cardLayout.show(contentPanel, String.valueOf(paneStack.size()));

      currentPane = nextPane;
      currentPane.activated(this);

      // if we're on the last pane, change the 'next' label to 'finish'
      if(currentPane.isLastPane()) {
        nextButton.setLabel(resources.getString("finish"));
      }
      
    } catch (Exception e) {
      JOptionPane.
        showMessageDialog(this, 
                          resources.getString("error")+": "+String.valueOf(e),
                          resources.getString("error"),
                          JOptionPane.ERROR_MESSAGE);
    }
  }

  public void setNextButtonEnabled(boolean val) {
    nextButton.setEnabled(val);
  }

}

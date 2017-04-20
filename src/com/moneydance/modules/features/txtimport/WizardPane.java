/************************************************************\
 *        Copyright 2017 The Infinite Kind, Limited         *
\************************************************************/

package com.moneydance.modules.features.txtimport;

import javax.swing.*;

public interface WizardPane {

  /** is called when this pane is made visible.   The wiz argument
      provides a reference to the Wizard object that this pane is
      a part of. */
  public void activated(Wizard wiz);

  /** Is called when the 'next' button is clicked to store
      the values entered in this pane.  Returns the next pane
      that the wizard should go to.  Returns null if the user
      should not be sent to the next pane. */
  public WizardPane storeValues();

  /** Is called when no longer in use so that things can be
      cleaned up. */
  public void goneAway();
  
  /** Get the component that contains the GUI for this pane. */
  public JComponent getPanel();
  
  /** Get whether or not this pane is the last one. */
  public boolean isLastPane();

}

package com.moneydance.modules.features.moneyPie;

import java.util.Observable;
import java.util.Observer;

import javax.swing.JComponent;
import javax.swing.JViewport;

import com.moneydance.apps.md.view.HomePageView;
import com.infinitekind.moneydance.model.*;
import com.moneydance.apps.md.view.gui.MoneydanceLAF;

public class BudgetHomePageViewController implements HomePageView, Observer {
  private  Main                extension;
  private  JViewport           viewport;
  private  boolean             initialized;

  public BudgetHomePageViewController(Main extension) {
    this.extension = extension;
  }

  private void init() {
    this.viewport = new JViewport();
    this.viewport.setOpaque(false);
    this.viewport.setBackground(this.extension.getPreferences().getBackground());
  }

  public synchronized void refresh() {
    if (this.viewport == null || !this.viewport.isVisible()) {
      return;
    }

    this.viewport.setView(new BudgetHomePageView(extension));

  }

  public void update(final Observable observable, final Object object) {
    this.refresh();
  }

  public JComponent getGUIView(AccountBook book) {
    if (!this.initialized) {
      this.initialized = true;
      this.init();
    }
    return this.viewport;
  }

  public void reset() {

  }

  public void setActive(final boolean active) {
    if (this.viewport == null) {
      return;
    }
    this.viewport.setVisible(active);
    this.refresh();
  }

  public String getID() {
    return "com.moneydance.modules.features.moneyPie.BudgetHomePageView";
  }


  public String toString() {
    return this.extension.getName();
  }

  public void cleanup() {
    if (!this.initialized) {
      return;
    }
    this.viewport.setEnabled(false);
    this.viewport.removeAll();
  }
}

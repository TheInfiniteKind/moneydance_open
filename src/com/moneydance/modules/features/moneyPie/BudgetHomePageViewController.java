package com.moneydance.modules.features.moneyPie;

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;

import javax.swing.JComponent;
import javax.swing.JViewport;

import com.moneydance.apps.md.view.HomePageView;
import com.infinitekind.moneydance.model.AccountBook;

public class BudgetHomePageViewController implements HomePageView, PropertyChangeListener {
  private  Main                extension;
  private  JViewport           viewport;
  private  boolean             initialized;

  public String getID() {
    return "com.moneydance.modules.features.moneyPie.BudgetHomePageView";
  }

  public String toString() {
    return this.extension.getName();
  }

  public void setActive(final boolean active) {
    if (this.viewport == null) {
      return;
    }
    this.viewport.setVisible(active);
    this.refresh();
  }

  public BudgetHomePageViewController(Main extension) {
    this.extension = extension;
    this.extension.addChangeListener(this);
  }

  private void init() {
    this.viewport = new JViewport();
    this.viewport.setOpaque(false);
    this.viewport.setBackground(this.extension.getPreferences().getBackground());
  }

  @Override
  public void propertyChange(PropertyChangeEvent event) {
    this.refresh();
  }

  public JComponent getGUIView(AccountBook book) {
    if (!this.initialized) {
      this.initialized = true;
      this.init();
    }
    return this.viewport;
  }

  public synchronized void refresh() {
    if (this.viewport == null || !this.viewport.isVisible()) {
      return;
    }

    this.viewport.setView(new BudgetHomePageView(extension));
  }

  public void reset() {
    this.refresh();
  }

  public void cleanup() {
    if (!this.initialized) {
      return;
    }
    this.viewport.setEnabled(false);
    this.viewport.removeAll();
  }
}

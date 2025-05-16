package com.moneydance.modules.features.mrbutil;

import java.awt.Graphics;
/**
 * Generic Print Interface
 * @author Mike Bray
 *
 */
public abstract interface MRBPrintable
{
  public abstract boolean usesWholePage();

  public abstract String getTitle();
  /**
   * Prints one page of the current report
   * 
   * @param paramGraphics - the graphics object for the printer
   * @param paramInt1 - current page number
   * @param paramDouble1 - width of the page
   * @param paramDouble2 - height of the page
   * @param paramInt2 - resolution of the page
   * @return true if more pages to print, false if finished
   */
  public abstract boolean printPage(Graphics paramGraphics, int paramInt1, double paramDouble1, double paramDouble2, int paramInt2);

}


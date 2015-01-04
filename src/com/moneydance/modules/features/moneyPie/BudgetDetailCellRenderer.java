/************************************************************\
 *       Copyright (C) 2010 Raging Coders                   *
\************************************************************/
package com.moneydance.modules.features.moneyPie;

import javax.swing.*;
import javax.swing.table.*;
import java.awt.*;

public class BudgetDetailCellRenderer extends DefaultTableCellRenderer {
  private static final long serialVersionUID = 1L;
  private Font boldFont, plainFont;

  BudgetDetailCellRenderer() {
    plainFont = getFont().deriveFont(Font.PLAIN);
    boldFont = plainFont.deriveFont(Font.BOLD);
    setHorizontalAlignment(LEFT);
  }

  public Component getTableCellRendererComponent(JTable table, Object value,
      boolean isSelected, boolean hasFocus, int row, int column) {
    if (value instanceof String){
      if (((String) value).indexOf("-")>=0 && column >= 3)
        setForeground(Color.RED);
      else
        setForeground(Color.BLACK);
    }
    if (isSelected){
      setFont(boldFont);
      setBackground(Color.YELLOW);
    } else {
      setFont(plainFont);
      setBackground(Color.WHITE);
    }
    if (column >= 3) setHorizontalAlignment(RIGHT);
    else             setHorizontalAlignment(LEFT);

    setText((String) value);
    return this;
  }

}

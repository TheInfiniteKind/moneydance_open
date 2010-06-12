package com.moneydance.modules.features.mikebalpred;

import javax.swing.*; 
import javax.swing.table.*; 
import java.awt.*; 
//import java.util.*;

public class DetailCellRenderer extends DefaultTableCellRenderer { 
//  private JTable table; 
  private Font boldFont, plainFont;
  
  DetailCellRenderer() { 
    plainFont = getFont().deriveFont(Font.PLAIN);
    boldFont = plainFont.deriveFont(Font.BOLD); 
    setHorizontalAlignment(LEFT); 
  } 
  
  public Component getTableCellRendererComponent(JTable table, Object value,
      boolean isSelected, boolean hasFocus, int row, int column) {
    if (value instanceof String)
    {
      if (((String) value).indexOf("-")>=0 && column >= 3)
        setForeground(Color.RED);
      else
        setForeground(Color.BLACK);
    }
    if (isSelected) 
    {
      setFont(boldFont);
      setBackground(Color.YELLOW);
    } else {
      setFont(plainFont);  
      setBackground(Color.WHITE);
//      if ((row & 1) == 0)   setBackground(MikeUtil.color1);
//      else                 setBackground(MikeUtil.color2);
    }
    if (column >= 3) setHorizontalAlignment(RIGHT); 
    else             setHorizontalAlignment(LEFT);

    setText((String) value);
    return this;
  }

}

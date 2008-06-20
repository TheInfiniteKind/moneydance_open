package com.moneydance.modules.features.balpred;

import com.moneydance.awt.graph.*;
import java.text.DateFormat;
import java.util.Date;

public class DateLabeler
  implements ValueLabeler
{
  private DateFormat dateFormat;
  
  public DateLabeler(DateFormat dateFormat) {
    this.dateFormat = dateFormat;
  }
  
  public String getLabelForValue(double value, int type) {
    return dateFormat.format(new Date(Math.round(value)));
  }
  
}

package com.moneydance.modules.features.mrbutil;

 /**
  * Model for classes wishing to create a report
  * @author Mike Bray
  *
  */
 public abstract class MRBReportGenerator 
 {
   private int[] arrColumnWidth = null;
   
   private boolean bIsLandscape = false;
 
   protected MRBReport objReport = null;

    protected boolean isDefaultLandscape()
   {
     return false;
   }
    /**
     * Get landscape flag
     * @return true if to be printed in landscape
     */
   public boolean isLandscape()
   {
     return this.bIsLandscape;
   }
   /**
    * Set the landscape flag
    * @param bIsLandscape - true if to be printed in landscape
    */
   public void setLandscape(boolean bIsLandscape)
   {
     this.bIsLandscape = bIsLandscape;
   }
 
   /**
    * Set the column widths
    * @param widths - array of widths in pixels
    */
   public void setColumnWidths(int[] widths)
   {
     this.arrColumnWidth = new int[widths.length];
     for (int index = 0; index < widths.length; index++) {
       this.arrColumnWidth[index] = ((int)Math.ceil(widths[index]));
     }
   }
   /**
    * Get the column widths
    * @return array of column widths
    */
   public int[] getColumnWidths()
   {
     return this.arrColumnWidth;
   }
 
   protected void setTitle (String strTitle) {
	   objReport.setTitle(strTitle);
   }
   protected void setSubTitle (String strSubTitle) {
	   objReport.setSubTitle(strSubTitle);
   }
  }


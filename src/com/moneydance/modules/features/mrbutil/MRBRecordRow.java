package com.moneydance.modules.features.mrbutil;

import java.awt.Color;
/**
 * Defines a single Row of a report
 * @author Mike Bray
 *
 */
 
 public class MRBRecordRow
 {
	 /**
	  * A blank row that can be used as a template for a new row
	  */
   public static final MRBRecordRow BLANK_ROW = new MRBRecordRow(null, null, null, null, null, null);
   private String[] strLabels = null;
   private byte[] byAlign = null;
   private Color[] clrBackground = null;
   private Color[] clrForeground = null;
   private byte[] byStyle = null;
   private byte[] byBorder = null;
   private static MRBRecordRow blank;
/**
 * Creates a new row. Parameters are arrays of data.  Each cell of the array aligns with a column in the report
 * @param strLabelsp - the actual data to be displayed (string values)
 * @param byAlignp the alignment of each cell
 * @param clrBackgroundp the Background colour of each cell
 * @param clrForegroundp the Text colour of each cell
 * @param byStylep the style for each cell
 * @param byBorderp the borders for each cell
 * @see MRBReportViewer MRBReportViewer for details of the alignment, style and border parameters
 */
   public MRBRecordRow(String[] strLabelsp, byte[] byAlignp, Color[] clrBackgroundp, Color clrForegroundp[], byte[] byStylep, byte[] byBorderp)
   {
     strLabels = strLabelsp;
     byAlign = byAlignp;
     clrBackground = clrBackgroundp;
     clrForeground = clrForegroundp;
     byStyle = byStylep;
     byBorder = byBorderp;
   }
 
   public MRBRecordRow() {
   }
 /**
  * Get the data for specified column
  * @param col column
  * @return string of data
  */
   public String getLabel(int col) {
     if ((col >= 0) && (strLabels != null) && (col < strLabels.length) && (strLabels[col] != null))
       return strLabels[col];
     return "";
   }
/**
 * Get the Alignment for specified column 
 * @param col column
 * @return Alignment
 * @see MRBReportViewer - MRBReportViewer for possible values 
 */
   public byte getAlignment(int col) {
     if ((col >= 0) && (byAlign != null) && (col < byAlign.length))
       return byAlign[col];
     return 1;
   }
 /**
  * Get the Color for the background for the specified column
  * @param col column
  * @return Color
  */
   public Color getColor(int col) {
     if ((col >= 0) && (clrBackground != null) && (col < clrBackground.length))
       return clrBackground[col];
     return Color.WHITE;
   }
   /**
    * Get the Color for the foreground(Text) for the specified column
    * @param col column
    * @return Color
    */
   public Color getColorFG(int col) {
	     if ((col >= 0) && (clrForeground != null) && (col < clrForeground.length))
	       return clrForeground[col];
	     return Color.BLACK;
	   } 
   /**
    * Get the Border for specified column 
    * @param col column
    * @return Border
    * @see MRBReportViewer - MRBReportViewer for possible values 
    */
   public byte getBorder(int col) {
     if ((col >= 0) && (byBorder != null) && (col < byBorder.length))
       return byBorder[col];
     return 0;
   }
   /**
    * Get the Style for specified column 
    * @param col column
    * @return Style
    * @see MRBReportViewer - MRBReportViewer for possible values 
    */

   public byte getStyle(int col)
   {
     if ((col >= 0) && (byStyle != null) && (col < byStyle.length))
       return byStyle[col];
     return 1;
   }
 

   public static final MRBRecordRow blankRow()
   {
     if (blank == null) blank = new MRBRecordRow(null, null, null,null, null, null);
     return blank;
   }
 }


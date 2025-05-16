package com.moneydance.modules.features.mrbutil;
 
 import java.awt.Font;

import javax.swing.UIManager;

import com.moneydance.apps.md.controller.UserPreferences;
/**
 * Manages the fonts to be used in the viewer and printing 
 * @author Mike Bray
 *
 */
 public class MRBReportFonts
 {
   private Font fnTitle;
   private Font fnSubTitle;
   private Font fnBold;
   private Font fnNormal;
   private Font fnItalic;
   private Font fnHeader;
 
   MRBReportFonts(Font baseFont)
   {
     float baseSize = baseFont.getSize2D();
     /*
      * get report title font as defined by MD - size 42, name "Helvetica".  Default "SansSerif"
      */
     this.fnTitle = UIManager.getFont("ReportTitle.font");
     /*
      * create other fonts
      *  if Title hasn't been defined use basefont, bold + 4 
      *  Subtitle is basefont, bold + 2
      *  Bold is basefont + bold
      *  Italic is base font + italic
      *  Header font is Bold font 
      */
     
     if (this.fnTitle == null) this.fnTitle = baseFont.deriveFont(Font.BOLD, (baseSize + 4.0F));
 
     this.fnSubTitle = baseFont.deriveFont(Font.BOLD, (baseSize + 2.0F));
     this.fnBold = baseFont.deriveFont(1, baseSize);
     this.fnNormal = baseFont.deriveFont(Font.PLAIN);
     this.fnItalic = baseFont.deriveFont(Font.ITALIC);
     this.fnHeader = this.fnBold;
   }
 
   public static MRBReportFonts getPrintingFonts(UserPreferences prefs) {
     Font f = UIManager.getFont("Label.font");
     String fontName = prefs.getSetting("print.font_name", f.getName());
     int fontSize = prefs.getIntSetting("print.font_size", 12);
     return new MRBReportFonts(new Font(fontName, 0, fontSize));
   }
 
   public static MRBReportFonts getScreenFonts() {
     return new MRBReportFonts(UIManager.getFont("Label.font"));
   }
 
   public Font getTitleFont() {
     return this.fnTitle;
   }
 
   public Font getSubtitleFont() {
     return this.fnSubTitle;
   }
 
   public Font getHeaderFont() {
     return this.fnHeader;
   }
 
   public Font getBoldFont() {
     return this.fnBold;
   }
 
   public Font getNormalFont() {
     return this.fnNormal;
   }
 
   public Font getItalicFont() {
     return this.fnItalic;
   }
 
   public void updateHeaderFontSize(float headerFontSize) {
     this.fnHeader = this.fnHeader.deriveFont(headerFontSize);
   }
 }

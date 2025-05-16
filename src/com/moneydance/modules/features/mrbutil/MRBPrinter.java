package com.moneydance.modules.features.mrbutil;
 
 import java.awt.Color;
import java.awt.Graphics;
import java.awt.print.PageFormat;
import java.awt.print.Paper;
import java.awt.print.Printable;
import java.awt.print.PrinterException;
import java.awt.print.PrinterJob;

import javax.print.PrintService;

import com.moneydance.apps.md.view.gui.MoneydanceGUI;
 /**
  * Defines the printer to be used for printing.  Uses standard dialogs to ask for printer.
  * <p>
  * Obtains the orientation and page sizes from the printer. Calls the printPage method in the 
  * Report Printer to construct the page 
  * @author Mike Bray
  *
  */
 public class MRBPrinter 
   implements Printable
 {
   private PrinterJob printJob = null;
   private MRBPrintable mrbPrintable =null;
   private int iLastPage = -1;
   private double dWidth;
   private double dHeight;
   
 
   /**
    * Creates the Printer object.  
    * @param objPrinterp The Report Printer object to be used
    * @return true if successful, false if not
    */
   public boolean print(MRBPrintable printable)
   {
     printJob = PrinterJob.getPrinterJob();
     if (printJob == null) {
       return false;
     }
 
     PrintService ps = printJob.getPrintService();
     if (ps == null) {
        return false;
     }
 
     mrbPrintable = printable;
     try
     {
       PageFormat pageFormat = printJob.defaultPage();
       pageFormat.setOrientation(PageFormat.LANDSCAPE);
       pageFormat = printJob.validatePage(pageFormat);
       Paper paper = pageFormat.getPaper();
       dHeight = paper.getHeight();
       dWidth = paper.getWidth();
       paper.setImageableArea(0.0D, 0.0D, dWidth, dHeight);
       pageFormat.setPaper(paper);
 
       printJob.setPrintable(this, pageFormat);
     } catch (Exception e) {
       e.printStackTrace(System.err);
       return false;
     }
 
     if (!printJob.printDialog()) {
       return false;
     }
     try
     {
       printJob.print();
     } catch (Exception e) {
       e.printStackTrace(System.err);
       return false;
     }
 
     return true;
   }
 
   @Override
   public int print(Graphics g, PageFormat pageFormat, int pageIndex)
     throws PrinterException
   {
 
     if ((iLastPage >= 0) && (pageIndex > iLastPage)) return 1;
     double dHeight;
     double dWidth;
     if (mrbPrintable.usesWholePage())
     {
       dWidth = pageFormat.getWidth();
       dHeight = pageFormat.getHeight();
     } else {
       dWidth = pageFormat.getWidth() - 72.0D;
       dHeight = pageFormat.getHeight() - 72.0D;
       int iImageableX = 36;
       int iImageableY = 36;
 
       if (MoneydanceGUI.isMac)
       		g = g.create(iImageableX, iImageableY, (int)dWidth, (int)dHeight);
     }
 
     g.setColor(Color.black);
 
     if (!mrbPrintable.printPage(g, pageIndex, dWidth, dHeight, 72))
     {
       iLastPage = pageIndex;
     }
 
     return 0;
   }
}

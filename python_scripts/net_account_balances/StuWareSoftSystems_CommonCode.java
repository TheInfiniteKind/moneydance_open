// Copyright (c) 2021 Stuart Beesley - StuWareSoftSystems - MIT License
// Purpose: Java code for use in Moneydance Jython scripts where simply not possible in pure Python/Jython
//          Bundled into the mxt(jar) file and use moneydance_extension_loader.loadClass() or java.net.URLClassLoader
//          No package name used as I want this in the root of the mxt(jar) so the MD signing routines keep it in the correct place.

//          Thus far the main need has been to use .print() type methods which Jython cannot 'handle' properly...

//package stuwaresoftsystems.code;

import javax.print.attribute.PrintRequestAttributeSet;
import javax.swing.*;
import java.awt.*;
import java.awt.geom.AffineTransform;
import java.awt.print.PageFormat;
import java.awt.print.Printable;
import java.awt.print.PrinterException;
import java.awt.print.PrinterJob;

@SuppressWarnings("unused")
public class StuWareSoftSystems_CommonCode {

    public static boolean DEBUG = false;

    public static final String codeVersion = "0.5";

    public static boolean test() {
        return test("");
    }

    public static boolean test(String name) {
        if (name == null) name = "";
        System.err.println("StuWareSoftSystems_CommonCode: test method... >> Hello " + name + " from your very own Java code");
        return (true);
    }

    public static void sudoPrinterJobPrint(PrinterJob printerJob) throws PrinterException {
        sudoPrinterJobPrint(printerJob, null);
    }

    public static void sudoPrinterJobPrint(PrinterJob printerJob, PrintRequestAttributeSet pras) throws PrinterException {
        if (pras == null) {
            printerJob.print();
        } else {
            printerJob.print(pras);
        }
    }

    public static class PrintWidgetPrinter implements Printable {

        JComponent compToPrint;

        public PrintWidgetPrinter(JComponent comp) {
            this.compToPrint = comp;
        }

        @Override
        public int print(Graphics graphics, PageFormat pageFormat, int pageIndex) throws PrinterException {

            if (pageIndex > 0) {
                return NO_SUCH_PAGE;
            }

            Graphics2D g2d = (Graphics2D) graphics;

            AffineTransform originalTransform = g2d.getTransform();

            double scaleX = pageFormat.getImageableWidth() / this.compToPrint.getWidth();
            double scaleY = pageFormat.getImageableHeight() / this.compToPrint.getHeight();
            double scale = Math.min(scaleX, scaleY);            // Maintain aspect ratio
            g2d.translate(pageFormat.getImageableX(), pageFormat.getImageableY());

            if (DEBUG) {
                System.err.println("PrintWidgetPrinter: Printer scale factor calculated at: " + (1.0 / scale));
            }

            if (scale < 1.0) {
                if (DEBUG) System.err.println("... will reduce size to fit paper");
                g2d.scale(scale, scale);
            } else {
                if (DEBUG) System.err.println("... no action taken to increase size (fill page)");
            }
            this.compToPrint.printAll(g2d);

            g2d.setTransform(originalTransform);

            /* tell the caller that this page is part of the printed document */
            return PAGE_EXISTS;
        }

    }
}

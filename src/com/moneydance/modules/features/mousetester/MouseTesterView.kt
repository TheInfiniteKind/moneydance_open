/************************************************************\
 *        Copyright (C) 2009 The Infinite Kind, LLC         *
\************************************************************/

package com.moneydance.modules.features.mousetester;

import com.infinitekind.moneydance.model.*;
import com.infinitekind.util.StringUtils;
import com.moneydance.apps.md.view.gui.*;
import com.moneydance.apps.md.view.*;
import com.moneydance.awt.*;
import java.awt.datatransfer.StringSelection;

import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.MouseEvent;
import java.awt.event.MouseListener;
import java.io.PrintWriter;
import java.io.Writer;

import static com.moneydance.modules.features.mousetester.Util.logConsole;

public class MouseTesterView implements HomePageView {
  public final static String ID = Main.EXTN_ID;
  protected MoneydanceGUI mdGUI = null;
  private ViewPanel view = null;
  private boolean active = false;
  private JTextArea mouseConsoleOutputArea = null;
  private PrintWriter consoleWriter = null;
  private Icon iconBlue = null;
  private Icon iconRed = null;
  private Icon iconNormal = null;

  public MouseTesterView() {
  }

  public void initializeObjects() {
    if (Main.getMDMain().getCurrentAccountBook() != null && mdGUI != null) {
      logConsole(true, Main.EXTN_ID + ": initializeObjects - already initialized... ignoring...");
      return;
    }

    if (Main.getMDMain().getCurrentAccountBook() == null && mdGUI == null) {
      logConsole(Main.EXTN_ID + ": initializeObjects - dataset & gui are not available yet... ignoring...");
      return;
    }

    // Use this to initialize stuff (only when dataset is open - assume the gui is open too)
    if (Main.getMDMain().getCurrentAccountBook() != null && mdGUI == null) {
      logConsole(Main.EXTN_ID + ": initializeObjects - dataset available - grabbing the GUI & initializing objects....");
      mdGUI = Main.getMDGUI();

      String ICON_PATH = "/com/moneydance/apps/md/view/gui/glyphs/moneybot.png";
      iconBlue = mdGUI.getImages().getIconWithColor(ICON_PATH, Util.getBlue());
      iconRed = mdGUI.getImages().getIconWithColor(ICON_PATH, Util.getRed());
      iconNormal = mdGUI.getImages().getIconWithColor(ICON_PATH, Util.getDefaultFGColor());

      mouseConsoleOutputArea = new JTextArea();
      mouseConsoleOutputArea.setEditable(false);
      mouseConsoleOutputArea.setFont(mdGUI.getFonts().mono);

      consoleWriter = new PrintWriter(new ConsoleWriter(mouseConsoleOutputArea));
      consoleWriter.println(Main.EXTN_NAME + " (results)...:");
      logConsole(Main.EXTN_ID + ": initializeObjects - finished initializing objects....");
      return;
    }

    logConsole(Main.EXTN_ID + ": initializeObjects - LOGIC ERROR - book: " + Main.getMDMain().getCurrentAccountBook() + " GUI: " + mdGUI);
  }

  /** Returns a unique identifier for this view.  This identifier must be unique across all identifiers for all extensions. */
  public String getID() { return ID; }
  
  /** Returns a short descriptive name of this view. */
  public String toString() { return Main.EXTN_NAME; }

  /** Returns a GUI component that provides a view of the info panel for the given data file. */
  public JComponent getGUIView(AccountBook book) {
    logConsole(Main.EXTN_ID + ": getGUIView - book: '" + book + "' isEDT: " + SwingUtilities.isEventDispatchThread());
    if (view != null) return view;
    synchronized (this) {
      initializeObjects();
      if (view == null) {
        view = new ViewPanel(book);
      }
      return view;
    }
  }

  /** 
   * Sets the view as active or inactive.  When not active, a view
   * should not have any registered listeners with other parts of
   * the program.  This will be called when a view is added to the
   * home page, or the home page is refreshed after not being visible
   * for a while.
   */
  public void setActive(boolean active) {
    logConsole(Main.EXTN_ID + ": setActive - active: " + active);
    this.active = active;
    if (view != null) {
      if (active) {
        view.activate();
      } else {
        view.deactivate();
      }
    }
  }

  public void refresh() {
    logConsole(Main.EXTN_ID + ": refresh");
    if (view != null) {
      view.refresh();
    }
  }

  /** Called when the view should clean up everything.  For example, this is called when a file is closed and the GUI is reset */
  public synchronized void reset() {
    logConsole(Main.EXTN_ID + ": reset");
    setActive(false);
    view = null;
  }

  private static class ConsoleWriter extends Writer implements Runnable {
    private JTextArea textArea;
    private final StringBuilder sb = new StringBuilder();

    public ConsoleWriter(JTextArea textArea) {
      this.textArea = textArea;
    }

    @Override
    public void write(char[] cbuf, int off, int len) {
      if (textArea == null) return;
      synchronized (sb) {
        sb.append(cbuf, off, len);
      }
      SwingUtilities.invokeLater(this);
    }

    @Override
    public void flush() { SwingUtilities.invokeLater(this); }

    @Override
    public void close() {
      textArea = null;
    }

    @Override
    public void run() {
      synchronized (sb) {
        if (StringUtils.isEmpty(String.valueOf(sb))) return;
        textArea.append(sb.toString());
        textArea.setCaretPosition(textArea.getDocument().getLength());
        sb.setLength(0);
      }
    }
  }

  private class ViewPanel extends JPanel implements MouseListener, ActionListener, AccountListener, CurrencyListener {
    private boolean clickFlip = false;
    private final AccountBook book;
    private final JLabel mouseTesterRow;

    ViewPanel(AccountBook book) {
      super(new GridBagLayout());
      logConsole(Main.EXTN_ID + ": ViewPanel()");
      this.book = book;

      setBorder(MoneydanceLAF.homePageBorder);
      setOpaque(false);
      mouseTesterRow = new JLabel("<<MouseTester: CLICK TEST>>");
      mouseTesterRow.setIcon(iconNormal);
      mouseTesterRow.addMouseListener(this);

      add(mouseTesterRow, GridC.getc(0,0).wx(1).fillboth().insets(0,14,6,14));

      JButton btn = new JButton(MDAction.makeNonKeyedAction(mdGUI, mdGUI.strings().copy_to_clipboard, "copy_clipboard", this));
      add(btn, GridC.getc(1,0).wx(1).fillboth().insets(0,14,6,14));

      JScrollPane scrollPane = new JScrollPane(mouseConsoleOutputArea) {
        @Override
        public Dimension getPreferredSize() {
          Dimension psz = super.getPreferredSize();
          psz.width = Math.min(200, psz.width);
          psz.height = 200;
          return psz;
        }
      };
      add(scrollPane, GridC.getc(0, 1).colspan(2).fillboth().insets(0,14,6,14));
      add(Box.createVerticalStrut(100), GridC.getc(0, 1));
      if(active) {
        activate();
      }
    }
    
    void activate() {
      book.addAccountListener(this);
      book.getCurrencies().addCurrencyListener(this);
      refresh();
    }

    void deactivate() {
      book.removeAccountListener(this);
      book.getCurrencies().removeCurrencyListener(this);
    }

    private final CollapsibleRefresher refresher = new CollapsibleRefresher(this::reallyRefresh);

    void refresh() {
        if (mdGUI.getSuspendRefreshes()) return;
        refresher.enqueueRefresh();
    }

    void reallyRefresh() {
      if (mdGUI.getSuspendRefreshes()) return;

      // Perform intensive data processing here and update the widget...
      repaint();
    }
    
    public void accountModified(Account acct) {
      //refresh();
    }

    public void currencyTableModified(CurrencyTable ctable) {
      //refresh();
    }
    
    public void accountBalanceChanged(Account acct) {
      //refresh();
    }


    public void accountDeleted(Account pacct, Account cacct) {
      //refresh();
    }

    public void accountAdded(Account pacct, Account nacct) {
      //refresh();
    }

    public void logMouseEvent(MouseEvent mouseEvent) {
      boolean javaPopupTrig = mouseEvent.isPopupTrigger();
      boolean moneydancePopupTrig = AwtUtil.isPopupTrigger(mouseEvent);
      consoleWriter.println(mouseEvent.paramString()
              + " isPopupTrigger(java): " + javaPopupTrig
              + " isPopupTrigger(MD): " + moneydancePopupTrig);
      if (javaPopupTrig || moneydancePopupTrig) {
        consoleWriter.println("... isPopup(java): " + javaPopupTrig + " isPopup(MD): " + moneydancePopupTrig);
      }
      repaint();
    }

    @Override
    public void mouseClicked(MouseEvent e) {
      clickFlip = !clickFlip;
      mouseTesterRow.setForeground(clickFlip ? Util.getRed() : Util.getBlue());
      logMouseEvent(e);
    }

    @Override
    public void mousePressed(MouseEvent e) {
      mouseTesterRow.setIcon(iconRed);
      logMouseEvent(e);
    }

    @Override
    public void mouseReleased(MouseEvent e) {
      mouseTesterRow.setIcon(iconBlue);
      logMouseEvent(e);
    }

    @Override
    public void mouseEntered(MouseEvent e) {
      mouseTesterRow.setBorder(BorderFactory.createLineBorder(Util.getRed()));
      logMouseEvent(e);
    }

    @Override
    public void mouseExited(MouseEvent e) {
      mouseTesterRow.setBorder(null);
      logMouseEvent(e);
    }

    @Override
    public void actionPerformed(ActionEvent evt) {
      if (evt.getActionCommand().equalsIgnoreCase("copy_clipboard")) {
        try {
          Toolkit.getDefaultToolkit().getSystemClipboard().setContents(new StringSelection(mouseConsoleOutputArea.getText()), null);
          consoleWriter.println("[results copied to clipboard]");
        } catch (Exception error) {
          logConsole(Main.EXTN_ID + " - Error copy contents of JTextArea to clipboard! " + error);
          consoleWriter.println("[ERROR copying to clipboard!" + error + "]");
          mdGUI.showErrorMessage(Main.EXTN_NAME + " - ERROR copying to clipboard!?", error);
        }
      }
    }
  }

}










/*
 *  Copyright (c) 2018, Michael Bray.  All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 *   - Redistributions of source code must retain the above copyright
 *     notice, this list of conditions and the following disclaimer.
 *
 *   - Redistributions in binary form must reproduce the above copyright
 *     notice, this list of conditions and the following disclaimer in the
 *     documentation and/or other materials provided with the distribution.
 *
 *   - The name of the author may not used to endorse or promote products derived
 *     from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
 * IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 * THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 * PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 * LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 */
package com.moneydance.modules.features.securityquoteload;

import java.awt.Color;
import java.awt.Image;
import java.awt.Toolkit;
import java.io.ByteArrayOutputStream;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.util.List;
import java.util.Locale;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;

import javax.swing.*;

import com.infinitekind.util.CustomDateFormat;
import com.infinitekind.util.DateUtil;
import com.moneydance.apps.md.controller.FeatureModule;
import com.moneydance.apps.md.controller.FeatureModuleContext;
import com.moneydance.apps.md.controller.UserPreferences;
import com.moneydance.apps.md.view.MoneydanceUI;
import com.moneydance.modules.features.mrbutil.MRBDebug;
import com.moneydance.modules.features.mrbutil.MRBPreferences2;
import com.moneydance.modules.features.mrbutil.MRBPlatform;
import com.moneydance.modules.features.mrbutil.MRBEDTInvoke;
import com.moneydance.modules.features.securityquoteload.quotes.QuoteException;
import com.moneydance.modules.features.securityquoteload.quotes.QuoteManager;
import com.moneydance.modules.features.securityquoteload.view.CalculateRunDate;

/**
 * Moneydance extension to load security prices obtained from Yahoo.com and
 * ft.com
 * <p>
 * Main class to create main window
 *
 * @author Mike Bray
 */

public class Main extends FeatureModule {
    public static boolean THROTTLE_YAHOO = true;
    public static CustomDateFormat cdate;
    public static Integer today;
    public static char decimalChar;
    public static FeatureModuleContext context;
    public static UserPreferences up;
    public static MRBDebug debugInst;
    public static Main extension;
    public static QuoteManager manager = null;
    public static Parameters params = null;
    public static String buildNo;
    public static Boolean autoSettingsChanged = false;
    public static boolean standAloneRequested = false;
    public static LinkedBlockingQueue<ProcessCommandArgument> processQueue;
    public static boolean alphaVantageLimitReached = false;

    private Image selectedBlack = null;
    private Image selectedLight;
    private Image unselectedBlack;
    private Image unselectedLight;
    public ImageIcon selectedIcon;
    public ImageIcon unselectedIcon;
    private String mdVersion;
    public MainPriceWindow frame;
    private Thread overallTimeout;
    private AtomicBoolean quotesCompleted = new AtomicBoolean(false);
    private int timeoutCount = 0;
    private String uri;
    private String command;
    private String cmdParam = "quit";
    public static MRBPreferences2 preferences;
    private String secMode;
    private String curMode;
    public String serverName = Constants.PROGRAMNAME;
    public int runtype = Constants.NORUN;
    public List<String> errorTickers;
    private TaskExecutor autoRun = null;
    public static ClassLoader loader;
    public boolean startUp = true;
    private Boolean closingRequested = false;
    public static boolean autoRunning = false;
    public static boolean secondRunRequired = false;
    public static boolean isUpdating = false;
    public static boolean isGUIOpen = false;
    public static boolean isQuotesRunning = false;
    private int timeoutMax = Constants.TIMEOUTCOUNT;
    private Timer autoDelay;
    private MoneydanceUI mdGUI;
    private com.moneydance.apps.md.controller.Main mdMain;
    private Thread processor = null;
    private boolean autoRunNeeded = false;


    /*
     * Called when extension is loaded<p> Need to register the feature and the URI
     * command to be called when the user selects the extension.
     *
     * normally "showconsole"
     */
    @Override
    public void init() {
        // the first thing we will do is register this module to be invoked
        // via the application toolbar
        extension = this;
        context = getContext();
        int iBuild = getBuild();
        buildNo = String.valueOf(iBuild);
        up = UserPreferences.getInstance();
        debugInst = new MRBDebug();
        debugInst.setExtension("Quote Load");
        String dateFormatStr;
        dateFormatStr = up.getSetting(UserPreferences.DATE_FORMAT);
        cdate = new CustomDateFormat(dateFormatStr);
        today = DateUtil.getStrippedDateInt();
        decimalChar = up.getDecimalChar();
        mdVersion = up.getSetting("current_version");
        int mdVersionNo = Integer.parseInt(mdVersion.substring(0, 4));
        if (mdVersionNo < Constants.MINIMUMVERSIONNO) {
            JOptionPane.showMessageDialog(null,
                    "This version of Quote Loader is designed to be run on Moneydance version "
                            + Constants.MINIMUMVERSIONNO + ". You are running version "
                            + mdVersion,
                    "Quote Loader", JOptionPane.ERROR_MESSAGE);
            return;
        }
        try {
            context.registerFeature(this, "showconsole", getIcon(Constants.QUOTELOADIMAGE), getName());
            debugInst.setDebugLevel(MRBDebug.DETAILED);
            debugInst.debug("Quote Load", "Init", MRBDebug.INFO, "Started Build " + buildNo);
            debugInst.debug("Quote Load", "Init", MRBDebug.INFO, "Locale " + Locale.getDefault());
            debugInst.debug("Quote Load", "Init", MRBDebug.INFO, "Decimal Character " + decimalChar);
        } catch (Exception e) {
            e.printStackTrace(System.err);
        }

    }

    /**
     * retrieves an image from within the .mxt file. Must be included when the
     * extension is compiled
     *
     * @param action the name of the image to load
     * @return the image
     */
    public Image getIcon(String action) {
        try {
            loader = getClass().getClassLoader();
            java.io.InputStream in = loader.getResourceAsStream(Constants.RESOURCEPATH + "/" + action);
            if (in != null) {
                ByteArrayOutputStream bout = new ByteArrayOutputStream(1000);
                byte[] buf = new byte[256];
                int n;
                while ((n = in.read(buf, 0, buf.length)) >= 0)
                    bout.write(buf, 0, n);
                return Toolkit.getDefaultToolkit().createImage(bout.toByteArray());
            }
        } catch (Throwable e) {
            return null;
        }
        return null;
    }

    @Override
    public void cleanup() {
        debugInst.debug("Quote Load", "cleanup", MRBDebug.SUMMARY, "cleanup  ");
        closeConsole();
    }

    @Override
    public void unload() {
        debugInst.debug("Quote Load", "unload", MRBDebug.SUMMARY, "unload  ");
        super.unload();
        if (autoRun != null) {
            autoRun.stop();
            autoRun = null;
        }
        closeConsole();

    }

    @Override
    public void handleEvent(String appEvent) {
        super.handleEvent(appEvent);
        debugInst.debug("Quote Load", "HandleEvent", MRBDebug.SUMMARY, "Event " + appEvent);
        if (appEvent.compareToIgnoreCase("md:file:opening") == 0) {
            handleEventFileOpening();
        } else if (appEvent.compareToIgnoreCase("md:file:opened") == 0) {
            handleEventFileOpened();
        } else if (appEvent.compareToIgnoreCase("md:file:closing") == 0) {
            handleEventFileClosing();
        } else if (appEvent.compareToIgnoreCase("md:file:closed") == 0) {
            handleEventFileClosed();
        }

    }

    protected void handleEventFileOpening() {
        debugInst.debug("Main", "HandleEventFileOpening", MRBDebug.DETAILED, "Opening ");
        closingRequested = false;
    }

    protected void handleEventFileOpened() {
        closingRequested = false;
        if (preferences != null)
            MRBPreferences2.forgetInstance();
        MRBPreferences2.loadPreferences(context);
        preferences = MRBPreferences2.getInstance();
        params = Parameters.getParameters();
        debugInst.setDebugLevel(
                preferences.getInt(Constants.PROGRAMNAME + "." + Constants.DEBUGLEVEL, MRBDebug.INFO));
        String debug;
        if (debugInst.getDebugLevel() == MRBDebug.INFO)
            debug = "INFO";
        else if (debugInst.getDebugLevel() == MRBDebug.SUMMARY)
            debug = "SUMM";
        else if (debugInst.getDebugLevel() == MRBDebug.DETAILED)
            debug = "DET";
        else
            debug = "OFF";
        debugInst.debug("Quote Load", "HandleEventFileOpened", MRBDebug.INFO, "Debug level set to " + debug);
        context = getContext();
        serverName = Constants.PROGRAMNAME;
        Timer autoDelayStart = new Timer(1, ((ae) -> javax.swing.SwingUtilities.invokeLater(() -> {
                sendAuto();
            })));
        autoDelayStart.setInitialDelay(20000);
        autoDelayStart.setRepeats(false);
        autoDelayStart.start();
        debugInst.debug("Quote Load", "handleEventFileOpened", MRBDebug.INFO,
                "Autorun delayed for 20 seconds ");
    }

    public void sendAuto() {
        if (standAloneRequested) {
            MRBEDTInvoke.showURL(context, "moneydance:fmodule:" + Constants.PROGRAMNAME + ":"
                    + Constants.STANDALONEREQUESTED);
        } else {
            debugInst.debug("Quote Load", "sendAuto", MRBDebug.INFO, "Check Auto");
            javax.swing.SwingUtilities.invokeLater(()-> {
               MRBEDTInvoke.showURL(context, "moneydance:fmodule:" + Constants.PROGRAMNAME + ":" + Constants.CHECKAUTOCMD);
            });
        }
    }

    private void resetAutoRun() {
        if (autoRun != null)
            autoRun.stop();
        autoRun = new TaskExecutor(this);
        LocalTime now = LocalTime.now();
        LocalTime next;
        if (now.isBefore(LocalTime.of(2, 0)))
            next = LocalTime.of(2, 0);
        else if (now.isBefore(LocalTime.of(4, 0)))
            next = LocalTime.of(4, 0);
        else if (now.isBefore(LocalTime.of(6, 0)))
            next = LocalTime.of(6, 0);
        else if (now.isBefore(LocalTime.of(8, 0)))
            next = LocalTime.of(8, 0);
        else if (now.isBefore(LocalTime.of(9, 0)))
            next = LocalTime.of(9, 0);
        else if (now.isBefore(LocalTime.of(11, 0)))
            next = LocalTime.of(11, 0);
        else if (now.isBefore(LocalTime.of(13, 0)))
            next = LocalTime.of(13, 0);
        else if (now.isBefore(LocalTime.of(15, 0)))
            next = LocalTime.of(15, 0);
        else if (now.isBefore(LocalTime.of(17, 0)))
            next = LocalTime.of(17, 0);
        else if (now.isBefore(LocalTime.of(19, 0)))
            next = LocalTime.of(19, 0);
        else if (now.isBefore(LocalTime.of(21, 0)))
            next = LocalTime.of(21, 0);
        else if (now.isBefore(LocalTime.of(22, 0)))
            next = LocalTime.of(22, 0);
        else if (now.isBefore(LocalTime.of(23, 0)))
            next = LocalTime.of(23, 0);
        else
            next = LocalTime.of(23, 59);
        LocalDateTime dateTime = LocalDateTime.of(LocalDate.now(), next);
        if (dateTime.isBefore(LocalDateTime.now()))
            dateTime.plusDays(1L);
        debugInst.debug("Quote Load", "resetAutoRun", MRBDebug.INFO,
                "now " + now + " next " + dateTime);
        autoRun.startExecutionAt(dateTime);
    }

    protected void handleEventFileClosing() {
        debugInst.debug("Quote Load", "HandleEventFileClosing", MRBDebug.DETAILED, "Closing ");
        if (frame != null && (frame.isSecDirty() || frame.isCurDirty() || frame.isParamDirty()))
            frame.close();
        closingRequested = true;
        if (autoRun != null) {
            autoRun.stop();
            autoRun = null;
        }
        if (manager != null)
            manager.shutdown();
        if (processor != null) {
            try {
                processQueue.put(new ProcessCommandArgument(Constants.CLOSEDOWNCMD, ""));
            } catch (InterruptedException e) {

            }
            processor = null;
        }
        closeConsole();
    }

    protected void handleEventFileClosed() {
        closingRequested = true;
        debugInst.debug("Quote Load", "HandleEventFileClosed", MRBDebug.DETAILED, "Closing ");
        if (autoRun != null) {
            autoRun.stop();
            autoRun = null;
        }
        if (processor != null) {
            try {
                processQueue.put(new ProcessCommandArgument(Constants.CLOSEDOWNCMD, ""));
            } catch (InterruptedException e) {

            }
            processor = null;
        }
        closeConsole();
    }

    /**
     * Processes the uri from Moneydance. Called by Moneydance
     * <p>
     * Commands:
     * <ul>
     * <li>showconsole - called when the user selects the extension
     * <li>timeout - the timeout started when the check for the backend request has
     * expired
     * <li>loadPrice - Backend has returned a price
     * <li>errorQuote - Backend has found an error
     * <li>doneQuote - Backend has completed all symbols on a particular getQuote
     * <li>checkprogram - Overall timer has expired, check to see if any outstanding
     * quotes
     * </ul>
     *
     * @param uri the uri from Moneydance
     */
    @Override
    public void invoke(String uri) {
        debugInst.debug("Quote Load", "invoke", MRBDebug.DETAILED, "Command uri " + uri);
        if (closingRequested)
            return;
        /*
         * load JCheckBox icons for Unix due to customised UIManager Look and feel
         */
        if (MRBPlatform.isUnix() || MRBPlatform.isFreeBSD()) {
            if (selectedBlack == null) {
                selectedBlack = getIcon(Constants.SELECTEDBLACKIMAGE);
                selectedLight = getIcon(Constants.SELECTEDLIGHTIMAGE);
                unselectedBlack = getIcon(Constants.UNSELECTEDBLACKIMAGE);
                unselectedLight = getIcon(Constants.UNSELECTEDLIGHTIMAGE);
                UIDefaults uiDefaults = UIManager.getDefaults();
                Color theme = uiDefaults.getColor("Panel.foreground");
                double darkness = 0;
                if (theme != null) {
                    darkness = 1 - (0.299 * theme.getRed() + 0.587 * theme.getGreen()
                            + 0.114 * theme.getBlue()) / 255;
                    debugInst.debug("Quote Load", "Init", MRBDebug.DETAILED,
                            "Panel.foreground Color " + theme + " Red " + theme.getRed()
                                    + " Green " + theme.getGreen() + " Blue " + theme.getBlue()
                                    + " Darkness " + darkness);
                }
                if (darkness > 0.5) {
                    if (selectedBlack != null) {
                        debugInst.debug("Quote Load", "Init", MRBDebug.DETAILED, "selected black loaded");
                        selectedIcon = new ImageIcon(
                                selectedBlack.getScaledInstance(16, 16, Image.SCALE_SMOOTH));
                    }
                    if (unselectedBlack != null) {
                        debugInst.debug("Quote Load", "Init", MRBDebug.DETAILED, "unselected black loaded");
                        unselectedIcon = new ImageIcon(
                                unselectedBlack.getScaledInstance(16, 16, Image.SCALE_SMOOTH));
                    }
                } else {
                    if (selectedLight != null) {
                        debugInst.debug("Quote Load", "Init", MRBDebug.DETAILED, "selected light loaded");
                        selectedIcon = new ImageIcon(
                                selectedLight.getScaledInstance(16, 16, Image.SCALE_SMOOTH));
                    }
                    if (unselectedLight != null) {
                        debugInst.debug("Quote Load", "Init", MRBDebug.DETAILED, "unselected light loaded");
                        unselectedIcon = new ImageIcon(
                                unselectedLight.getScaledInstance(16, 16, Image.SCALE_SMOOTH));
                    }
                }
            }
        }
        if (preferences == null) {
            MRBPreferences2.loadPreferences(context);
            preferences = MRBPreferences2.getInstance();
        }
        if (params == null)
            params = Parameters.getParameters();
        this.uri = uri;
        command = this.uri;
        int theIdx = uri.indexOf('?');
        if (theIdx >= 0) {
            command = uri.substring(0, theIdx);
        } else {
            theIdx = uri.indexOf(':');
            if (theIdx >= 0) {
                command = uri.substring(0, theIdx);
                cmdParam = uri.substring(theIdx + 1);
            }
        }

        if (command.equals("showconsole")) {
            if (frame != null && runtype > Constants.MANUALRUN) {
                JOptionPane.showMessageDialog(null, "Quote Loader is running an automatic update,please wait",
                        "Quote Loader", JOptionPane.INFORMATION_MESSAGE);
                return;
            }
            debugInst.debug("Quote Load", "invoke", MRBDebug.DETAILED, "runtype set to manual");
            runtype = Constants.MANUALRUN;
            showConsole();
        } else
            processCommand(command, uri);
    }

    private synchronized void processCommand(String command, String uri) {
        if (processor == null) {
            debugInst.debug("Quote Load", "processCommand", MRBDebug.DETAILED, "starting ProcessWorker");
            processQueue = new LinkedBlockingQueue();
            processor = new Thread(new ProcessWorker());
            processor.start();
        }
        try {
            processQueue.put(new ProcessCommandArgument(command, uri));
        } catch (InterruptedException e) {

        }
    }

    /**
     * Return the name of this extension
     */
    @Override
    public String getName() {
        return "Quote Loader";
    }

    /**
     * Create the GUI and show it. For thread safety, this method should be invoked
     * from the event dispatch thread.
     */
    private void createAndShowGUI() {
        if (context.getCurrentAccountBook().getCurrencies().getBaseType() == null) {
            JOptionPane.showMessageDialog(null,
                    "The Quote Loader extension depends on the base currency having been set. Please set the base currency before restarting",
                    "Quote Loader", JOptionPane.ERROR_MESSAGE);
            return;
        }
        // Create and set up the window.
        if (frame != null) {
            frame.requestFocus();
            return;
        }
        frame = new MainPriceWindow(this, runtype);
        if (errorTickers != null)
            frame.setErrorTickers(errorTickers);
        frame.setTitle("Quote Loader " + buildNo);
        frame.setIconImage(getIcon(Constants.QUOTELOADIMAGE));
        frame.setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE);
        // Display the window.
        frame.pack();
        frame.setLocationRelativeTo(null);
        frame.addWindowListener(new java.awt.event.WindowAdapter() {
            @Override
            public void windowClosing(java.awt.event.WindowEvent windowEvent) {
                closeConsole();
                // }
            }
        });
        frame.setVisible(true);


    }

    /**
     * Starts the user interface for the extension
     * <p>
     * First it checks if is present by sending a hello message to
     *
     * @see #invoke(String)
     */
    private synchronized void showConsole() {

        if (runtype != Constants.MANUALRUN) {
            String runmsg = switch (runtype) {
                case 2 -> "Auto Run - Securities Only";
                case 3 -> "Auto Run - Currencies Only";
                case 4 -> "Auto Run - Securities and Currencies";
                case 5 -> "Standalone  Run";
                default -> "";
            };
            debugInst.debug("Quote Load", "showConsole", MRBDebug.INFO, runmsg);
            processCommand(command, uri);
        } else {
            debugInst.debug("Quote Load", "showConsole", MRBDebug.INFO, "Manual Run");
            javax.swing.SwingUtilities.invokeLater(() -> {
                isGUIOpen = true;
                createAndShowGUI();
            });
        }
//		}

    }

    /**
     * closes the extension
     */
    synchronized void closeConsole() {
        debugInst.debug("Quote Load", "closeConsole", MRBDebug.DETAILED, "closing Console ");
        isGUIOpen = false;
        if (frame != null)
            frame.checkUnsaved();
        quotesCompleted.set(true);
        if (overallTimeout != null && overallTimeout.isAlive())
            overallTimeout.interrupt();
        errorTickers = null;
        if (frame != null) {
            frame.setVisible(false);
            frame.dispose();
            frame = null;
        }
        runtype = Constants.NORUN;
        if (params != null)
            Parameters.closeParameters();
        params = null;
        if (autoRunNeeded && !closingRequested){
            sendAuto();
            autoRunNeeded = false;
        }
    }
    public void setThrottleMessage(){
        if (frame != null)
            frame.setThrottleMessage();
    }
    public void unsetThrottleMessage(){
        if (frame != null)
            frame.unsetThrottleMessage();
    }

    /**
     * Process Command Argument
     */
    class ProcessCommandArgument {
        String command;
        String uri;

        public String getCommand() {
            return command;
        }

        public String getUri() {
            return uri;
        }

        public ProcessCommandArgument(String command, String uri) {
            this.command = command;
            this.uri = uri;

        }
    }

    /**
     * Process Command thread
     */
    class ProcessWorker implements Runnable {
        @Override
        public void run() {
            debugInst.debug("Quote Load", "ProcessWorker", MRBDebug.DETAILED, "ProcessWorker started");
            boolean done = false;
            while (!done) {
                try {
                    ProcessCommandArgument args = processQueue.take();
                    debugInst.debug("Quote Load", "ProcessWorker", MRBDebug.DETAILED, "Command " + args.getCommand() + " received");
                    if (args.getCommand().equals(Constants.CLOSEDOWNCMD)) {
                        done = true;
                        break;
                    }
                    processCommand(args.getCommand(), args.uri);
                } catch (InterruptedException e) {
                    debugInst.debug("Quote Load", "ProcessWorker", MRBDebug.DETAILED, "Process Worker interrupted");
                    done = true;
                }
            }
        }

        public synchronized void processCommand(String command, String uri) {
              debugInst.debug("Quote Load", "processCommand", MRBDebug.DETAILED, "process command invoked " + command);
			Integer totalQuotes;
            switch (command) {

              case Constants.SAVECMD -> {
                if (frame != null) {
                  frame.save();  // This should be executed off the EDT and on the process command thread...
                }
              }

				case Constants.RUNSTANDALONECMD -> {
					if (!cmdParam.equalsIgnoreCase("quit") && !cmdParam.equalsIgnoreCase("noquit")) {
						JOptionPane.showMessageDialog(null, "Invalid Quote Loader runauto parameter: " + cmdParam,
								"Quote Loader", JOptionPane.INFORMATION_MESSAGE);
						return;
					}
					standAloneRequested = true;
                    Timer autoDelayStart = new Timer(1, ((ae) -> javax.swing.SwingUtilities.invokeLater(() -> {
                        sendAuto();
                    })));
                    autoDelayStart.setInitialDelay(20000);
                    autoDelayStart.setRepeats(false);
                    autoDelayStart.start();
					return;
				}
				case Constants.STANDALONEREQUESTED -> {
					runtype = Constants.STANDALONERUN;
					debugInst.debug("Quote Load", "processCommand", MRBDebug.DETAILED, "running standalone");
					frame = new AutomaticRun(Main.this, runtype);
					return;
				}
				case Constants.RUNAUTOCMD -> {
					frame = new AutomaticRun(Main.this, runtype);
					return;
				}
				case Constants.CHECKAUTOCMD -> {
					/*
					 *  Check if an Auto run is due
					 */
					if (params == null)
						Parameters.getParameters();
					debugInst.debug("Quote Load", "processCommand", MRBDebug.DETAILED, "Running Checkautocmd");
					autoSettingsChanged = false;
					secMode = preferences.getString(Constants.PROGRAMNAME + "." + Constants.SECRUNMODE,
							Constants.MANUALMODE);
					curMode = preferences.getString(Constants.PROGRAMNAME + "." + Constants.CURRUNMODE,
							Constants.MANUALMODE);
					boolean secRunAuto = false;
					boolean curRunAuto = false;
					int secNextrun = 0;
					int curNextrun = 0;

					/*
					 * check for securities
					 */
					if (secMode.equals(Constants.AUTOMODE)) {
						debugInst.debug("Quote Load", "Process Command", MRBDebug.DETAILED,
								"Security Auto mode detected");
						secNextrun = preferences.getInt(Constants.PROGRAMNAME + "." + Constants.SECNEXTRUN, today);
						if (secNextrun <= today)
							secRunAuto = true;
					}
					/*
					 * check for currencies
					 */
					if (params.getCurrency() && curMode.equals(Constants.AUTOMODE)) {
						debugInst.debug("Quote Load", "Process Command", MRBDebug.DETAILED,
								"Currency Auto mode detected");
						curNextrun = preferences.getInt(Constants.PROGRAMNAME + "." + Constants.CURNEXTRUN, today);
						if (curNextrun <= today)
							curRunAuto = true;
					}
					debugInst.debug("Quote Load", "processCommand", MRBDebug.DETAILED,
							"Date check " + secRunAuto + " " + curRunAuto);
					int startTime = preferences.getInt(Constants.PROGRAMNAME + "." + Constants.STARTTIME,
							Constants.RUNSTARTUP);
					if (secRunAuto || curRunAuto) {
						if (startTime != Constants.RUNSTARTUP) {
                            /*
                             * Not a run at startup - check if time has been reached
                             */
                            LocalTime now = LocalTime.now();
                            LocalTime runTime = LocalTime.of(23, 59);
                            for (int i = 0; i < Constants.TIMEVALUES.length; i++) {
                                if (Constants.TIMEVALUES[i] == startTime) {
                                    if (Constants.TIMESTART[i] != 24)
                                        runTime = LocalTime.of(Constants.TIMESTART[i], 0);
                                }
                            }

                            LocalDateTime dateTime = LocalDateTime.of(LocalDate.now(), runTime);
                            if (dateTime.isBefore(LocalDateTime.now()))
                                dateTime.plusDays(1L);
                            debugInst.debug("Quote Load", "processCommand", MRBDebug.DETAILED,
                                    "Time check - Sec " + secRunAuto + " " + secNextrun + " " + startUp);
                            debugInst.debug("Quote Load", "processCommand", MRBDebug.DETAILED,
                                    "Time check - Cur " + curRunAuto + " " + curNextrun + " " + startUp);
                            debugInst.debug("Quote Load", "processCommand", MRBDebug.DETAILED,
                                    "Time check - run time " + runTime + " " + now);
                            if (!((secRunAuto && secNextrun < today && startUp)
                                    || (curRunAuto && curNextrun < today && startUp))) {
                                if (runTime.isAfter(now)) {
                                    /*
                                     * start time not reached - reset auto run
                                     */
                                    resetAutoRun();
                                    return;
                                }
                                startUp = false;
                            }
                            debugInst.debug("Quote Load", "processCommand", MRBDebug.DETAILED,
                                    "frame " + String.valueOf(frame == null) + " runtype " + runtype);
                        }

                        if (secRunAuto || curRunAuto) {
                            if (frame != null && runtype == Constants.MANUALRUN) {
                                /*
                                 * check to see if Quote Loader is open
                                 */
                                debugInst.debug("Quote Load", "processCommand", MRBDebug.DETAILED,
                                        "Quote Loader is open, autorun cannot run");
                                autoRunNeeded=true;
                                frame.setStatusMessage();
                                return;
                            }
                        }


                        /*
						 * determine what type of run
						 */
						if (secRunAuto && !curRunAuto)
							runtype = Constants.SECAUTORUN;
						if (!secRunAuto && curRunAuto)
							runtype = Constants.CURAUTORUN;
						if (secRunAuto && curRunAuto)
							runtype = Constants.BOTHAUTORUN;
						debugInst.debug("Quote Load", "Process Command", MRBDebug.DETAILED, "Submitting Auto Run");
						/*
						 * send Run Auto Cmd
						 */
						MRBEDTInvoke.showURL(context, "moneydance:fmodule:" + Constants.PROGRAMNAME + ":"
								+ Constants.RUNAUTOCMD);
						MRBEDTInvoke.showURL(context, "moneydance:setprogress?meter=0&label="
								+ "Quote Loader Updating Prices");

						if (secRunAuto) {
							/*
							 * reset security next run date
							 */
							preferences.put(Constants.PROGRAMNAME + "." + Constants.SECLASTRUN, today);
							CalculateRunDate secRun = new CalculateRunDate(Constants.SECRUNTYPE,
									Constants.SECRUNPARAM, Constants.SECLASTRUN);
							preferences.put(Constants.PROGRAMNAME + "." + Constants.SECNEXTRUN, secRun.getDate());
							preferences.isDirty();
						}
						/*
						 * reset currency next run date
						 */
						if (curRunAuto) {
							preferences.put(Constants.PROGRAMNAME + "." + Constants.CURLASTRUN, today);
							CalculateRunDate curRun = new CalculateRunDate(Constants.CURRUNTYPE,
									Constants.CURRUNPARAM, Constants.CURLASTRUN);
							preferences.put(Constants.PROGRAMNAME + "." + Constants.CURNEXTRUN, curRun.getDate());
							preferences.isDirty();
						}
						resetAutoRun();
					} else {
						debugInst.debug("Quote Load", "Process Command", MRBDebug.DETAILED, "Nothing to run");
						resetAutoRun();
					}
					return;
				}
				case Constants.GETQUOTECMD -> {
					Runnable task = () -> {
						manager = new QuoteManager();
						manager.getQuotes(uri);
					};
					new Thread(task).start();
					return;
				}
				case Constants.TIMEOUTCMD -> {
					debugInst.debug("Quote Load", "invoke", MRBDebug.SUMMARY, "time out received");
					return;
				}


				case Constants.STARTQUOTECMD -> {
					try {
						totalQuotes = Integer.valueOf(uri.substring(uri.indexOf("?numquotes=") + 11));
					} catch (NumberFormatException e) {
						totalQuotes = 0;
					}
					timeoutMax = totalQuotes < 100 ? 30 : totalQuotes < 200 ? 50 : 100;
					debugInst.debug("Quote Load", "processCommand", MRBDebug.DETAILED,
							"total quotes=" + totalQuotes + " maximum timeout set to " + timeoutMax);
					overallTimeout = new Thread(new QuoteTimer());
					overallTimeout.start();
					isQuotesRunning = true;
					return;
				}
				case Constants.TESTTICKERCMD -> {
					javax.swing.SwingUtilities.invokeLater(() -> frame.testTicker(uri));
					return;
				}
				case Constants.GETINDIVIDUALCMD -> {
					javax.swing.SwingUtilities.invokeLater(() -> frame.getIndividualTicker(uri));
					return;
				}
				case Constants.LOADPRICECMD -> {
					if (frame != null) {
						timeoutCount = 0;
						debugInst.debug("Quote Load", "processCommand", MRBDebug.DETAILED, "updating price " + uri);
						try {
							frame.updatePrices(uri);
						}
						catch (QuoteException e){

						}
					}
					return;
				}
				case Constants.LOADHISTORYCMD -> {
					if (frame != null) {
						timeoutCount = 0;
						debugInst.debug("Quote Load", "processCommand", MRBDebug.DETAILED, "updating history " + uri);
						try {
							frame.updateHistory(uri);
						}
						catch (QuoteException e){

						}
					}
					return;
				}
				case Constants.ERRORQUOTECMD -> {
					if (frame != null) {
						timeoutCount = 0;
						debugInst.debug("Quote Load", "processCommand", MRBDebug.DETAILED, "error returned " + uri);
						frame.failedQuote(uri);
					}
					return;
				}
				case Constants.DONEQUOTECMD -> {
					if (frame != null) {
						timeoutCount = 0;
						debugInst.debug("Quote Load", "processCommand", MRBDebug.DETAILED, "Done " + uri);
						javax.swing.SwingUtilities.invokeLater(() -> {
							frame.doneQuote(uri);
						});

					}
					return;
				}
				case Constants.CHECKPROGRESSCMD -> {
					if (frame != null) {
						if (frame.checkProgress()) {
							quotesCompleted.set(true);
						} else {
							debugInst.debug("Quote Load", "ProcessCommand", MRBDebug.SUMMARY,
									"Still Waiting for Backend");
							if (timeoutCount > timeoutMax) {
								javax.swing.SwingUtilities.invokeLater(() -> {
									JOptionPane.showMessageDialog(null, "Backend has failed to respond", "Quote Loader",
											JOptionPane.ERROR_MESSAGE);
								});
								frame.closeQuotes();
							} else
								timeoutCount++;
						}
					} else
						quotesCompleted.set(true);
					return;
				}
				/*
				 * check for end of automatic run completed
				 */
				case Constants.AUTODONECMD -> {
					runtype = 0;
					if (frame != null) {
						frame.dispose();
						frame = null;
						autoRunning = false;
						isQuotesRunning = false;
					}
					MRBEDTInvoke.showURL(context, "moneydance:setprogress?meter=0&label=" + "Quote Loader Update Completed");
					debugInst.debug("Quote Load", "ProcessCommand", MRBDebug.DETAILED, "Auto run done");
					if (standAloneRequested && cmdParam.equalsIgnoreCase("quit")) {
						MRBEDTInvoke.showURL(context, "moneydance:fmodule:" + Constants.PROGRAMNAME + ":"
								+ Constants.STANDALONEDONE);
					}
					return;
				}
				/*
				 * check for standalone run completed
				 */
				case Constants.STANDALONEDONE -> {
					debugInst.debug("Quote Load", "ProcessCommand", MRBDebug.INFO, "Standalone  run done");
					javax.swing.SwingUtilities.invokeLater(() -> {

						mdMain = com.moneydance.apps.md.controller.Main.mainObj;
						mdGUI = mdMain.getUI();
						mdMain.saveCurrentAccount();
						mdGUI.shutdownApp(false);
					});
				}
				/*
				 * check for manual run done
				 */
				case Constants.MANUALDONECMD -> {
					runtype = 0;
					isQuotesRunning = false;
				}
				/*
				 * second run required one autorun to allow currencies to be done first
				 */
				case Constants.RUNSECONDRUNCMD -> {
					if (frame != null && frame instanceof AutomaticRun)
						((AutomaticRun) frame).secondRun();
				}
			}
        }

    }

    /**
     * @author Mike Bray Sets up and runs a timer to check if backend has responded.
     * If it expires it sends a 'timeout' message to the invoke(uri) method
     */
    class QuoteTimer implements Runnable {
        @Override
        public void run() {
            debugInst.debug("Quote Load", "QuoteTimer", MRBDebug.SUMMARY, "Timer started");
            while (!quotesCompleted.get()) {
                try {
                    TimeUnit.SECONDS.sleep(Constants.OVERALLTIMEOUT);
                } catch (InterruptedException e) {
                    if (!quotesCompleted.get())
                        e.printStackTrace();
                }
                debugInst.debug("Quote Load", "QuoteTimer", MRBDebug.SUMMARY, "Timer expired");
                if (quotesCompleted.get())
                    debugInst.debug("Quote Load", "QuoteTimer", MRBDebug.INFO, "Quotes Completed");
                else {
                    MRBEDTInvoke.showURL(context, "moneydance:fmodule:" + Constants.PROGRAMNAME + ":"
                            + Constants.CHECKPROGRESSCMD);
                }
            }
        }

    }
}

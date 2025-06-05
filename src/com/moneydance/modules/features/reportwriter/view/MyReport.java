/*
 * Copyright (c) 2020, Michael Bray.  All rights reserved.
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
package com.moneydance.modules.features.reportwriter.view;

import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ComponentEvent;
import java.awt.event.ComponentListener;
import java.awt.event.InputEvent;
import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;


import com.moneydance.awt.GridC;
import com.moneydance.modules.features.mrbutil.MRBDebug;
import com.moneydance.modules.features.mrbutil.MRBDirectoryUtils;
import com.moneydance.modules.features.mrbutil.MRBPlatform;
import com.moneydance.modules.features.reportwriter.Constants;
import com.moneydance.modules.features.reportwriter.Main;
import com.moneydance.modules.features.reportwriter.Parameters;
import com.moneydance.modules.features.reportwriter.RWException;
import com.moneydance.modules.features.reportwriter.samples.DownloadException;

import com.moneydance.modules.features.reportwriter.OptionMessage;


import javax.swing.*;

public class MyReport extends JFrame {
    private Parameters params;
    /*
     * Screen variables
     */
    private JPanel mainScreen;
    private ReportPane reportPan;
    private SelectionPane selectionPan;
    private DataPane dataPan;
    private MyReport thisObj;
    private JButton closeBtn;
    private JButton settingsBtn;
    private JButton helpBtn;
    private JPanel buttons;
    public int iFRAMEWIDTH;
    public int iFRAMEDEPTH;
    public int SCREENWIDTH = 0;
    public int SCREENHEIGHT = 0;

    public MyReport() {
        thisObj = this;
        mainScreen = new JPanel(new GridBagLayout());
        this.add(mainScreen);
        this.getRootPane().getActionMap().put("close-window", new AbstractAction(){
            @Override
            public void actionPerformed(ActionEvent e) {
                Main.extension.closeConsole();
            }
        });
        this.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT)
                .put(KeyStroke.getKeyStroke("control W"), "close-window");
        if (MRBPlatform.isWindows()){
            this.getRootPane().getInputMap(JComponent.WHEN_ANCESTOR_OF_FOCUSED_COMPONENT)
                    .put(KeyStroke.getKeyStroke(java.awt.event.KeyEvent.VK_F4, InputEvent.CTRL_DOWN_MASK), "close-window");
        }

        mainScreen.addComponentListener(new ComponentListener() {
            @Override
            public void componentResized(ComponentEvent e) {
                int width = mainScreen.getWidth();
                int height = mainScreen.getHeight();
                Main.rwDebugInst.debug("MyReport", "MyReport", MRBDebug.SUMMARY,
                        "Component New size " + width + "/" + height);
                Main.preferences.put(Constants.PROGRAMNAME + "." + Constants.CRNTFRAMEWIDTH, width);
                Main.preferences.put(Constants.PROGRAMNAME + "." + Constants.CRNTFRAMEHEIGHT, height);
                Main.preferences.isDirty();
                updatePreferences(width, height);
            }

            @Override
            public void componentMoved(ComponentEvent e) {

            }

            @Override
            public void componentShown(ComponentEvent e) {

            }

            @Override
            public void componentHidden(ComponentEvent e) {

            }
        });
        params = new Parameters();
        if (params.getIntroScreen()) {
            new IntroScreen(params);
        }
        if (params.getDataDirectory() == null || params.getDataDirectory().equals(Constants.NODIRECTORY)
                || params.getOutputDirectory() == null || params.getOutputDirectory().equals(Constants.NODIRECTORY)) {
            new FirstRun(this, params);
            if (params.getDataDirectory().equals(Constants.NODIRECTORY)
                    || params.getOutputDirectory().equals(Constants.NODIRECTORY)) {
                OptionMessage.displayErrorMessage("Extension can not continue without setting the directories");
            } else
                params.save();
            resetData();
        } else
            checkDefaultDb();

        closeBtn = new JButton();
        if (Main.loadedIcons.closeImg == null)
            closeBtn.setText("Exit");
        else
            closeBtn.setIcon(new ImageIcon(Main.loadedIcons.closeImg));
        closeBtn.addActionListener(e -> Main.extension.closeConsole());
        settingsBtn = new JButton();
        if (Main.loadedIcons.settingsImg == null)
            settingsBtn.setText("Settings");
        else
            settingsBtn.setIcon(new ImageIcon(Main.loadedIcons.settingsImg));
        settingsBtn.addActionListener(e -> {
            new FirstRun(this, params);
            if (params.getDataDirectory().equals(Constants.NODIRECTORY)) {
                OptionMessage.displayErrorMessage(
                        "Extension can not continue without setting the directories");
            } else
                params.save();
            resetData();
        });
        helpBtn = new JButton();
        if (Main.loadedIcons.helpImg == null)
            helpBtn.setText("Help");
        else
            helpBtn.setIcon(new ImageIcon(Main.loadedIcons.helpImg));
        helpBtn.addActionListener(e -> new HelpScreen(params));
        dataPan = new DataPane(params);
        reportPan = new ReportPane(params);
        selectionPan = new SelectionPane(params);
        mainScreen.add(selectionPan, GridC.getc(0, 0).insets(0, 10, 5, 10));
        mainScreen.add(dataPan, GridC.getc(1, 0).insets(0, 5, 5, 5));
        mainScreen.add(reportPan, GridC.getc(2, 0).insets(0, 5, 5, 10));
        buttons = new JPanel();
        buttons.setLayout(new BoxLayout(buttons, BoxLayout.X_AXIS));
        buttons.add(closeBtn);
        buttons.add(Box.createRigidArea(new Dimension(10, 0)));
        buttons.add(settingsBtn);
        buttons.add(Box.createRigidArea(new Dimension(10, 0)));
        buttons.add(helpBtn);
        mainScreen.add(buttons, GridC.getc(0, 1).west().colspan(5).insets(10,10,10,10));
        setPreferences();
        mainScreen.setPreferredSize(new Dimension(iFRAMEWIDTH,iFRAMEDEPTH));
        pack();
     }

    /*
     * check to see if default database has changed
     */
    private void checkDefaultDb() {
        String defaultDBLoaded = Main.preferences.getString(Constants.PARMLASTDB, "00000000");
        if (defaultDBLoaded.compareTo(Main.databaseChanged) < 0) {
            try {
                createAdapter(params.getOutputDirectory());
            } catch (DownloadException | RWException e) {
                OptionMessage.displayErrorMessage("Issues setting up default database");
            }
        }

    }


    public void createAdapter(String directory) throws RWException {
        Main.rwDebugInst.debug("MyReport", "createAdapter", MRBDebug.DETAILED, "Creating database adapter");
        String outFile = directory + "/Moneydance.xml";
        File extensionData = MRBDirectoryUtils.getExtensionDataDirectory(Constants.PROGRAMNAME);
        String dirName = extensionData.getAbsolutePath();

        try {
            java.io.InputStream in = getClass().getResourceAsStream(Constants.RESOURCES + Constants.DATABASEADAPTER);
            byte[] buffer;
            if (in != null) {
                buffer = new byte[in.available()];
                in.read(buffer);
                File outputFile = new File(outFile);
                OutputStream outStream = new FileOutputStream(outputFile);
                String tempStr = new String(buffer, StandardCharsets.UTF_8);
                tempStr = tempStr.replace("##database##", directory + "/Moneydance");
                tempStr = tempStr.replace("##jar##", dirName + "/" + Constants.DATABASEJAR);
                tempStr = tempStr.replace(".jarsav", ".jar");
                buffer = tempStr.getBytes();
                outStream.write(buffer);
                outStream.close();
            }
        } catch (Throwable e) {
            e.printStackTrace();
            throw new RWException("Error creating Database Adapter");
        }
    }


    private ScreenPanel getFocus() {
        Component node = Main.frame.getFocusOwner();
        while (node != null) {
            if (node == selectionPan)
                return selectionPan;
            if (node == dataPan)
                return dataPan;
            if (node == reportPan)
                return reportPan;
            node = node.getParent();
        }
        return null;
    }


    /*
     * preferences
     */
    private void setPreferences() {
        iFRAMEWIDTH = Main.preferences.getInt(Constants.PROGRAMNAME + "." + Constants.CRNTFRAMEWIDTH,
                Constants.MAINSCREENWIDTH);
        iFRAMEDEPTH = Main.preferences.getInt(Constants.PROGRAMNAME + "." + Constants.CRNTFRAMEHEIGHT,
                Constants.MAINSCREENHEIGHT);
    }

    private void updatePreferences(int width, int height) {
        SCREENHEIGHT = height;
        SCREENWIDTH = width;
        int dataWidth = (width - 100) / 3;
        int dataHeight = (height - 150);
        Main.preferences.put(Constants.PROGRAMNAME + "." + Constants.DATAPANEWIDTH, dataWidth);
        Main.preferences.put(Constants.PROGRAMNAME + "." + Constants.DATAPANEHEIGHT, dataHeight);
        Main.preferences.isDirty();
        if (selectionPan != null)
            selectionPan.resize();
        if (reportPan != null)
            reportPan.resize();
        if (dataPan != null)
            dataPan.resize();
        Main.rwDebugInst.debug("MyReport", "updatePreferences", MRBDebug.DETAILED,
                "New size " + width + "/" + height + "/" + dataWidth + "/" + dataHeight);
    }

    public void resetData() {
        if (dataPan != null)
            dataPan.resetData();
        if (selectionPan != null)
            selectionPan.resetData();
        if (reportPan != null)
            reportPan.resetData();
    }

    public void closeDown() {
    }
}

package com.moneydance.modules.features.debtinsights.ui;

import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.moneydance.apps.md.view.gui.SecondaryDialog;
import com.moneydance.apps.md.view.gui.SecondaryWindow;
import com.moneydance.awt.GridC;
import com.moneydance.modules.features.debtinsights.Main;
import com.moneydance.modules.features.debtinsights.Util;

import javax.swing.*;
import java.awt.*;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;

@SuppressWarnings("CatchMayIgnoreException")
public class DisplayHelp extends SecondaryDialog {
    public DisplayHelp(MoneydanceGUI mdGUI, Frame parent, String title, boolean modal) {
        super(mdGUI, parent, title, modal);

        StringBuilder fileContents = new StringBuilder();
        String helpFile = String.format("/com/moneydance/modules/features/%s/%s_readme.txt", Main.EXTN_ID, Main.EXTN_ID);
        InputStream istream = getClass().getResourceAsStream(helpFile);
        if (istream == null) {
            Util.logConsole("Warning: Failed to get help file: " + helpFile);
            return;
        }
        Util.logConsole(true, "Obtained help file: " + helpFile);
        InputStreamReader istr = new InputStreamReader(istream, StandardCharsets.UTF_8);
        BufferedReader bufr = new BufferedReader(istr);
        while (true) {
            String line = null;
            try {
                line = bufr.readLine();
            } catch (Exception e) {}
            if (line != null) {
                line += "\n";
                fileContents.append(line);
                continue;
            }
            break;
        }
        fileContents.append("\n<END>");

        try {bufr.close();
        } catch (Exception e) {}

        try {istr.close();
        } catch (Exception e) {}

        try {istream.close();
        } catch (IOException e) {}

        if (fileContents.length() <= 0) {
            Util.logConsole("Warning: Help file contents appear to be empty: " + helpFile);
            return;
        }

        Util.logConsole(true, "Help file contains:\n" + String.valueOf(fileContents));

        JPanel pnl = new JPanel(new GridBagLayout());
        pnl.setBorder(BorderFactory.createEmptyBorder(8, 10, 8, 10));
        JTextArea jText = new JTextArea(String.valueOf(fileContents));
        jText.setEditable(false);
        jText.setLineWrap(false);
        jText.setWrapStyleWord(false);
//        jText.setFont(getMonoFont());
        JScrollPane jsp = new JScrollPane(jText, JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED, JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED);
        pnl.add(jsp, GridC.getc(0, 0).wxy(1.0F, 1.0F).colspan(5).fillboth());
        add(pnl);
        try {
            setEscapeKeyCancels(true);
        } catch (Exception e) {
        }
        setLocationRelativeTo(parent);
        pack();
//        setRememberSizeLocationKeys();
        setVisible(true);
    }
}

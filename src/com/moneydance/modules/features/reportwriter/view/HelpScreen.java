package com.moneydance.modules.features.reportwriter.view;

import com.moneydance.apps.md.view.MoneydanceUI;
import com.moneydance.awt.GridC;
import com.moneydance.modules.features.mrbutil.MRBDebug;
import com.moneydance.modules.features.reportwriter.Constants;
import com.moneydance.modules.features.reportwriter.Main;
import com.moneydance.modules.features.reportwriter.Parameters;
import com.moneydance.modules.features.reportwriter.OptionMessage;

import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

public class HelpScreen {
    private JDialog stage;
    private JPanel pane;
	private JButton helpBtn;
    private JButton introScreen;
	private ButtonGroup group;
 	private JRadioButton debugOff;
	private JRadioButton debugInfo;
	private JRadioButton debugSummary;
	private JRadioButton debugDetailed;
	private Parameters thisParams;
	private MoneydanceUI mdGUI;
	private com.moneydance.apps.md.controller.Main mdMain;

    public HelpScreen(Parameters params) {
    	thisParams= params;
		mdMain = com.moneydance.apps.md.controller.Main.mainObj;
		mdGUI = mdMain.getUI();
		stage = new JDialog();
		stage.setModalityType(Dialog.ModalityType.APPLICATION_MODAL);
		pane = new JPanel((new GridBagLayout()));
		stage.add(pane);
//TODO		Main.accels.setSceneClose(scene, new Runnable () {
/*			@Override
			public void run() {
				stage.close();
			}
		});*/
		stage.setTitle("Help");
		helpBtn = new JButton("Show Help");
		helpBtn.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				String url = "http://github.com/mrbray99/moneydanceproduction/wiki/Report-Writer";
				mdGUI.showInternetURL(url);
			}
		});

		pane.add(helpBtn, GridC.getc(0,0).insets(10,10,10,10));
		introScreen = new JButton("Display Intro Screen");
		introScreen.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				thisParams.setIntroScreen(true);
				params.save();
				OptionMessage.displayMessage("The intro screen will be shown the next time you start the extension");
			}
		});
		pane.add(introScreen, GridC.getc(0, 1).insets(10,10,10,10));
		debugOff = new JRadioButton ("Debug Off");
		debugInfo = new JRadioButton ("Debug Info Messages Only");
		debugSummary = new JRadioButton ("Debug Summary Message");
		debugDetailed = new JRadioButton ("All Debug Messages");
		group = new ButtonGroup();
		group.add(debugOff);
		group.add(debugInfo);
		group.add(debugSummary);
		group.add(debugDetailed);
		switch (Main.rwDebugInst.getDebugLevel()) {
		case MRBDebug.OFF:
			debugOff.setSelected(true);
			break;
		case MRBDebug.INFO:
			debugInfo.setSelected(true);
			break;
		case MRBDebug.SUMMARY:
			debugSummary.setSelected(true);
			break;
		default :
			debugDetailed.setSelected(true);
		}
		class GroupListener implements ActionListener {
			public void actionPerformed(ActionEvent e) {
				if (e.getSource() == debugOff) {
					Main.rwDebugInst.debug("HelpScreen","HelpScreen",MRBDebug.INFO,"Debug turned Off");
					Main.rwDebugInst.setDebugLevel(MRBDebug.OFF);;
				}
				else {
					if (e.getSource() == debugInfo) {
						Main.rwDebugInst.setDebugLevel(MRBDebug.INFO);
						Main.rwDebugInst.debug("HelpScreen","HelpScreen",MRBDebug.INFO,"Debug turned To Info");
					}
					else if (e.getSource()==debugSummary) {
						Main.rwDebugInst.setDebugLevel(MRBDebug.SUMMARY);
						Main.rwDebugInst.debug("HelpScreen","HelpScreen",MRBDebug.INFO,"Debug turned To Summary");
					}
					else {
						Main.rwDebugInst.setDebugLevel(MRBDebug.DETAILED);
						Main.rwDebugInst.debug("HelpScreen","HelpScreen",MRBDebug.INFO,"Debug turned To Detailed");
					}
				}
				Main.preferences.put(Constants.PROGRAMNAME+"."+Constants.DEBUGLEVEL, Main.rwDebugInst.getDebugLevel());
				Main.preferences.isDirty();
			}
		}

		GroupListener listener = new GroupListener();
		debugOff.addActionListener(listener);
		debugInfo.addActionListener(listener);
		debugSummary.addActionListener(listener);
		debugDetailed.addActionListener(listener);
		pane.add(debugOff, GridC.getc(0, 2).insets(10,10,10,10).west());
		pane.add(debugInfo, GridC.getc(0, 3).insets(10,10,10,10).west());
		pane.add(debugSummary, GridC.getc(0, 4).insets(10,10,10,10).west());
		pane.add(debugDetailed,GridC.getc( 0, 5).insets(10,10,10,10).west());
		String about = "<html>"+Constants.ABOUT1+Constants.ABOUT2+Constants.ABOUT3+Main.buildNo+"."+Main.minorBuildNo+"<br><br>"+Constants.ABOUT4+"</html>";
		JLabel aboutLbl = new JLabel(about);
		pane.add(aboutLbl,GridC.getc(1,0).insets(20,20,20,20).rowspan(5));
		stage.pack();
		stage.setLocationRelativeTo(null);
		stage.setVisible(true);
    }

}

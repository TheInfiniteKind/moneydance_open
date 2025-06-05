package com.moneydance.modules.features.reportwriter.view;



import com.moneydance.modules.features.mrbutil.MRBDebug;
import com.moneydance.modules.features.reportwriter.Constants;
import com.moneydance.modules.features.reportwriter.Main;
import com.moneydance.modules.features.reportwriter.Parameters;

import javax.swing.*;
import javax.swing.text.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

public class IntroScreen {
	private JDialog stage;
	private JPanel display;
	private JCheckBox donotDisplay;
	private JButton okBtn;
	private char [] bout = new char[102400];
	private Font normFont = new Font("Helvetica", Font.PLAIN, 10);
	public IntroScreen(Parameters params) {
		normFont = new Font(Main.labelFont.getFamily(), Font.PLAIN, Main.labelFont.getSize());
		display = new JPanel();
		display.setLayout(new BoxLayout(display,BoxLayout.Y_AXIS));
		boolean boldStarted = false;
		boolean firstBold = false;
		boolean firstEnd = false;
		JTextPane text=new JTextPane();
		text.setContentType("text/html");
		StringBuilder stringData = new StringBuilder("<html>");
		SimpleAttributeSet attributeSet = new SimpleAttributeSet();
//		try {
			Document doc = text.getStyledDocument();
			for (int j = 0; j < Constants.INTROTEXT.length; j++) {
				bout = Constants.INTROTEXT[j].toCharArray();
				for (int i = 0; i < bout.length; i++) {
					if (bout[i] == '*' && i < bout.length - 1 && bout[i + 1] == '*' && !boldStarted) {
						firstBold = true;
						boldStarted = true;
						stringData.append ("<b>");
//						StyleConstants.setBold(attributeSet,true);
//						text.setCharacterAttributes(attributeSet, true);
						continue;
					}
					if (bout[i] == '*' && firstBold) {
						firstBold = false;
						continue;
					}
					if (bout[i] == '*' && i < bout.length - 1 && bout[i + 1] == '*' && boldStarted) {
//						StyleConstants.setBold(attributeSet, false);
						stringData.append("</b>)");
						firstBold = true;
						continue;
					}
					if (bout[i] == ':' && i < bout.length - 1 && bout[i + 1] == ':') {
//						doc.insertString(doc.getLength(),"\n",attributeSet);
						stringData.append("<br>");
						firstEnd = true;
						continue;
					}
					if (bout[i] == ':' && firstEnd)
						continue;
					if (bout[i] != ':') {
//						doc.insertString(doc.getLength(), String.valueOf(bout[i]), attributeSet);
						stringData.append(bout[i]);
					}
				}
			}
/*		}
		catch (BadLocationException e){
			text.setText("Error in setting text");
		}*/
		stringData.append ("</html>");
		text.setText(stringData.toString());
		display.add(text);
		donotDisplay = new JCheckBox("Do not display again");
		donotDisplay.setSelected(false); 
		okBtn = new JButton();
		if (Main.loadedIcons.okImg == null)
			okBtn.setText("OK");
		else
			okBtn.setIcon(new ImageIcon(Main.loadedIcons.okImg));
		okBtn.addActionListener(e -> {
            params.setIntroScreen(!donotDisplay.isSelected());
            params.save();
            stage.dispose();
        });

		display.add(donotDisplay);
		display.add(okBtn);
		stage = new JDialog();
		stage.setModalityType(Dialog.ModalityType.APPLICATION_MODAL);
		stage.add(display);
		stage.pack();
		int SCREENWIDTH =Main.preferences.getInt(Constants.PROGRAMNAME+"."+Constants.CRNTFRAMEWIDTH,Constants.MAINSCREENWIDTH);
		int SCREENHEIGHT =Main.preferences.getInt(Constants.PROGRAMNAME+"."+Constants.CRNTFRAMEHEIGHT,Constants.MAINSCREENHEIGHT);
		int crntWidth = stage.getWidth();
		stage.setLocation((SCREENWIDTH-crntWidth)/2,SCREENHEIGHT/2);
		stage.setVisible(true);

	}
}

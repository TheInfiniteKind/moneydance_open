package com.moneydance.modules.features.reportwriter.view;

import com.moneydance.modules.features.reportwriter.Constants;
import com.moneydance.modules.features.reportwriter.Main;

import javax.swing.*;
import java.awt.*;
import java.awt.event.ComponentEvent;
import java.awt.event.ComponentListener;

public class MyGridPane extends JPanel {
	private String windowName;
	private Double winWidth;
	private Double winHeight;
	private MyGridPane thisObj;
	public MyGridPane(String windowName) {
		super();
		this.setLayout(new GridBagLayout());
		thisObj = this;
		this.windowName = windowName;
		this.addComponentListener(new ComponentListener(){
			@Override
			public void componentResized(ComponentEvent arg0) {
				JPanel panScreen = (JPanel) arg0.getSource();
				Dimension dimension = panScreen.getSize();
				winHeight = dimension.getHeight();
				Main.preferences.put(Constants.PROGRAMNAME+".WS"+windowName+"HEIGHT", winHeight);
				Main.preferences.isDirty();
				winWidth = dimension.getWidth();
				Main.preferences.put(Constants.PROGRAMNAME+".WS"+windowName+"WIDTH", winWidth);
				Main.preferences.isDirty();
				thisObj.setPreferredSize(dimension);
			}
			@Override
			public void componentShown(ComponentEvent arg0) {
				// not needed
			}

			@Override
			public void componentHidden(ComponentEvent e) {
				// not needed
			}

			@Override
			public void componentMoved(ComponentEvent e) {
				// not needed
			}
		});
	}
	public Double getWinWidth() {
		return winWidth;
	}
	public Double getWinHeight() {
		return winHeight;
	}
	
}

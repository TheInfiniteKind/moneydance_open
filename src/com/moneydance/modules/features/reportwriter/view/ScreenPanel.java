package com.moneydance.modules.features.reportwriter.view;

import com.moneydance.modules.features.reportwriter.Constants;
import com.moneydance.modules.features.reportwriter.Main;

import javax.swing.*;
import java.awt.*;

public abstract class ScreenPanel extends JPanel {
    protected int SCREENWIDTH; 
    protected int SCREENHEIGHT; 

	public ScreenPanel () {
		super();
	}
	public void fireDataChanged() {
		
	}
	public void resize() {
		SCREENWIDTH =Main.preferences.getInt(Constants.PROGRAMNAME+"."+Constants.DATAPANEWIDTH,Constants.DATASCREENWIDTH);
		SCREENHEIGHT =Main.preferences.getInt(Constants.PROGRAMNAME+"."+Constants.DATAPANEHEIGHT,Constants.DATASCREENHEIGHT);
//		setPreferredSize(new Dimension(SCREENWIDTH,SCREENHEIGHT));
//		setMinimumSize(new Dimension(SCREENWIDTH,SCREENHEIGHT));
//		setMaximumSize(new Dimension(SCREENWIDTH,SCREENHEIGHT));

	}
	protected void openMsg() {
		
	}
	protected void saveMsg () {
		
	}
	protected void deleteMsg() {
		
	}
	protected void newMsg() {
		
	}
	private void setPrefSize(int width, int height){
		setPreferredSize(new Dimension(width,height));
	}
}

package com.moneydance.modules.features.reportwriter.view;

import com.moneydance.modules.features.mrbutil.MRBDebug;
import com.moneydance.modules.features.reportwriter.Constants;
import com.moneydance.modules.features.reportwriter.Main;

import javax.swing.*;
import java.awt.*;
import java.awt.event.ComponentAdapter;
import java.awt.event.ComponentEvent;

public class ScreenDataPane {
	   protected int SCREENWIDTH; 
	   protected int SCREENHEIGHT;
	   protected int DEFAULTSCREENWIDTH; 
	   protected int DEFAULTSCREENHEIGHT;
	   protected String screenName;
	   protected JDialog stage = null;
	   protected String screenTitle;
	   private int mainWidth;
	   private int mainHeight;
	   private int locationX;
	   private int locationY;
//TODO	   protected WritableImage image;
	public ScreenDataPane () {
	}
	public void resize() {
		SCREENWIDTH =Main.preferences.getInt(Constants.PROGRAMNAME+"."+screenName+Constants.DATAPANEWIDTH,DEFAULTSCREENWIDTH);
		SCREENHEIGHT =Main.preferences.getInt(Constants.PROGRAMNAME+"."+screenName+Constants.DATAPANEHEIGHT,DEFAULTSCREENHEIGHT);

		if (stage !=null) {
			stage.setSize(new Dimension(SCREENWIDTH,SCREENHEIGHT));
		}
		Main.rwDebugInst.debug("ScreenDataPane", "resize", MRBDebug.DETAILED, "Size set to "+SCREENWIDTH+"/"+SCREENHEIGHT);

	}
	public void setLocation(){
		mainWidth = Main.frame.getWidth();
		mainHeight = Main.frame.getHeight();
		locationX = (mainWidth-SCREENWIDTH)/2;
		locationY = (mainHeight-SCREENHEIGHT)/2;
		stage.setLocation(locationX,locationY);
	}
	public void setStage(JDialog stage) {
		mainWidth = Main.frame.getWidth();
		mainHeight = Main.frame.getHeight();
		this.stage = stage;
		this.stage.setTitle(screenTitle);
		this.stage.setIconImage(Main.loadedIcons.mainImg);
		stage.addComponentListener(new ComponentAdapter(){
			public void componentHidden(ComponentEvent e){
				closePane();
			}
			public void componentResized(ComponentEvent evt){
				JDialog tmp = (JDialog)evt.getSource();
				SCREENWIDTH = tmp.getWidth();
				SCREENHEIGHT=tmp.getHeight();
				Main.preferences.put(Constants.PROGRAMNAME+"."+screenName+Constants.DATAPANEWIDTH, SCREENWIDTH);
				Main.rwDebugInst.debug("ScreenDataPane", "setStage", MRBDebug.DETAILED, "Size set to "+SCREENWIDTH+"-"+SCREENHEIGHT);
				Main.preferences.put(Constants.PROGRAMNAME+"."+screenName+Constants.DATAPANEWIDTH, SCREENWIDTH);
				sizeChanged();
			}
		});
		resize();
	}
	public void sizeChanged() {}

	public String getScreenTitle() {
		return screenTitle;
	}
	public void setScreenTitle(String screenTitle) {
		this.screenTitle = screenTitle;
	}
	public void closePane(){stage.setVisible(false);}
	
}

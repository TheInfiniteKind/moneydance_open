package com.moneydance.modules.features.loadsectrans;

import javax.swing.JCheckBox;

import com.moneydance.modules.features.mrbutil.MRBDebug;
import com.moneydance.modules.features.mrbutil.MRBPlatform;


public class MyCheckBox extends JCheckBox{
	private MRBDebug debugInst;
	int size=16;
	public MyCheckBox() {
		super();
		debugInst = new MRBDebug();
		debugInst.setExtension("SecurityLoadTrans");
		this.setHorizontalAlignment(CENTER);
		if (MRBPlatform.isFreeBSD() || MRBPlatform.isUnix()) {
			if (Main.extension.selectedIcon != null) {
				debugInst.debug("MyCheckBox", "construct no label", MRBDebug.DETAILED,"Using check box sel icons");
				setSelectedIcon(Main.extension.selectedIcon);
				setDisabledSelectedIcon(Main.extension.selectedIcon);
				setRolloverSelectedIcon(Main.extension.selectedIcon);
			}
			if (Main.extension.unselectedIcon != null) {
				debugInst.debug("MyCheckBox", "construct  no label", MRBDebug.DETAILED,"Using check box unsel icons");
				setIcon(Main.extension.unselectedIcon);
				setDisabledIcon(Main.extension.unselectedIcon);
				setRolloverIcon(Main.extension.unselectedIcon);
			}
		}
	}
	public MyCheckBox(String labelp) {
		super (labelp);
		this.setHorizontalAlignment(CENTER);
		if (MRBPlatform.isFreeBSD() || MRBPlatform.isUnix()) {
			if (Main.extension.selectedIcon != null) {
				debugInst.debug("MyCheckBox", "construct label", MRBDebug.DETAILED,"Using check box sel icons");
				setSelectedIcon(Main.extension.selectedIcon);
				setDisabledSelectedIcon(Main.extension.selectedIcon);
				setRolloverSelectedIcon(Main.extension.selectedIcon);
			}
			if (Main.extension.unselectedIcon != null) {
				debugInst.debug("MyCheckBox", "construct label", MRBDebug.DETAILED,"Using check box unsel icons");
				setIcon(Main.extension.unselectedIcon);
				setDisabledIcon(Main.extension.unselectedIcon);
				setRolloverIcon(Main.extension.unselectedIcon);
			} 
		}
	}
}

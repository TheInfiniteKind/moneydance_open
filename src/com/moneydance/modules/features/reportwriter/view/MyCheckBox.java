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


import com.moneydance.modules.features.mrbutil.MRBDebug;
import com.moneydance.modules.features.mrbutil.MRBPlatform;
import com.moneydance.modules.features.reportwriter.Main;

import javax.swing.*;


public class MyCheckBox extends JCheckBox{
	int size=16;
	public MyCheckBox() {
		super();
		this.setHorizontalAlignment(CENTER);
		if (MRBPlatform.isFreeBSD() || MRBPlatform.isUnix()) {
			if (Main.extension.selectedIcon != null) {
				Main.rwDebugInst.debug("MyCheckBox", "construct no label", MRBDebug.DETAILED,"Using check box sel icons");
				setSelectedIcon(Main.extension.selectedIcon);
				setDisabledSelectedIcon(Main.extension.selectedIcon);
				setRolloverSelectedIcon(Main.extension.selectedIcon);
			}
			if (Main.extension.unselectedIcon != null) {
				Main.rwDebugInst.debug("MyCheckBox", "construct  no label", MRBDebug.DETAILED,"Using check box unsel icons");
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
				Main.rwDebugInst.debug("MyCheckBox", "construct label", MRBDebug.DETAILED,"Using check box sel icons");
				setSelectedIcon(Main.extension.selectedIcon);
				setDisabledSelectedIcon(Main.extension.selectedIcon);
				setRolloverSelectedIcon(Main.extension.selectedIcon);
			}
			if (Main.extension.unselectedIcon != null) {
				Main.rwDebugInst.debug("MyCheckBox", "construct label", MRBDebug.DETAILED,"Using check box unsel icons");
				setIcon(Main.extension.unselectedIcon);
				setDisabledIcon(Main.extension.unselectedIcon);
				setRolloverIcon(Main.extension.unselectedIcon);
			} 
		}
	}
}

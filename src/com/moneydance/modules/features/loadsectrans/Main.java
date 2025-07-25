/*
 *  Copyright (c) 2014, Michael Bray. All rights reserved.
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
 */ 
package com.moneydance.modules.features.loadsectrans;

import java.awt.Color;
import java.awt.Image;
import java.awt.Toolkit;
import java.io.ByteArrayOutputStream;
import java.util.SortedMap;
import java.util.TreeMap;

import javax.swing.ImageIcon;
import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.UIDefaults;
import javax.swing.UIManager;

import com.infinitekind.moneydance.model.Account;
import com.infinitekind.moneydance.model.AccountBook;
import com.infinitekind.moneydance.model.TransactionSet;
import com.infinitekind.util.CustomDateFormat;
import com.moneydance.apps.md.controller.FeatureModule;
import com.moneydance.apps.md.controller.FeatureModuleContext;
import com.moneydance.apps.md.controller.UserPreferences;
import com.moneydance.modules.features.mrbutil.MRBPlatform;


/** Moneydance extension to load security transactions from a file and generates 
 * appropriate transactions
 * 
 * Main class to create main window
 */

public class Main
extends FeatureModule
{
	public static final CustomDateFormat cdate = new CustomDateFormat(UserPreferences.getInstance().getSetting(UserPreferences.DATE_FORMAT));
	public static FeatureModuleContext context;
	public static Account root;
	public static AccountBook acctBook;
	public static Main extension;
	private Image selectedBlack=null;
	private Image selectedLight;
	private Image unselectedBlack;
	private Image unselectedLight;
	public ImageIcon selectedIcon;
	public ImageIcon unselectedIcon;
	public static TransactionSet tranSet;
	public static MyTransactionSet generatedTranSet;
	public static SortedMap<String,Account> mapAccounts;
	private static int buildNum;
	public static String buildStr = "2019";
	private JPanel panScreen;

	@Override
	public void init() {
		// the first thing we will do is register this module to be invoked
		// via the application toolbar
		extension = this;
		context = getContext();
		try {
			context.registerFeature(this, "showconsole",
					getIcon("mrb icon2.png"),
					getName());
		}
		catch (Exception e) {
			e.printStackTrace(System.err);
		}
		buildNum = getBuild();
		buildStr = String.valueOf(buildNum);
	}
	/*
	 * Get Icon is not really needed as Icons are not used.  Included as the 
	 * register feature method requires it
	 */

	private Image getIcon(String action) {
		try {
			ClassLoader cl = getClass().getClassLoader();
			java.io.InputStream in = 
					cl.getResourceAsStream("/com/moneydance/modules/features/loadsectrans/"+action);
			if (in != null) {
				ByteArrayOutputStream bout = new ByteArrayOutputStream(1000);
				byte[] buf = new byte[256];
				int n ;
				while((n=in.read(buf, 0, buf.length))>=0)
					bout.write(buf, 0, n);
				return Toolkit.getDefaultToolkit().createImage(bout.toByteArray());
			}
		} catch (Throwable e) { }
		return null;
	}
	@Override
	public void cleanup() {
		closeConsole();
	}
  @Override
  public void unload() { cleanup(); }


	/** Process an invocation of this module with the given URI */
	@Override
	public void invoke(String uri) {
		String command = uri;
		int theIdx = uri.indexOf('?');
		if (MRBPlatform.isUnix() || MRBPlatform.isFreeBSD()) {
			if(selectedBlack == null) {
				selectedBlack = getIcon(Constants.SELECTEDBLACKIMAGE);
				selectedLight = getIcon(Constants.SELECTEDLIGHTIMAGE);
				unselectedBlack = getIcon(Constants.UNSELECTEDBLACKIMAGE);
				unselectedLight = getIcon(Constants.UNSELECTEDLIGHTIMAGE);
				UIDefaults uiDefaults = UIManager.getDefaults();
				Color theme = uiDefaults.getColor("Panel.foreground");
				double darkness = 0;
				if (theme !=null) {
					darkness = 1-(0.299*theme.getRed() + 0.587*theme.getGreen() + 0.114*theme.getBlue())/255;
				}
				if (darkness > 0.5) {
					if (selectedBlack != null) {
						selectedIcon = new ImageIcon(selectedBlack.getScaledInstance(16, 16, Image.SCALE_SMOOTH));
					}
					if (unselectedBlack != null) {
						unselectedIcon = new ImageIcon(unselectedBlack.getScaledInstance(16, 16, Image.SCALE_SMOOTH));
					}
				}
				else {
					if (selectedLight != null) {
						selectedIcon = new ImageIcon(selectedLight.getScaledInstance(16, 16, Image.SCALE_SMOOTH));
					}
					if (unselectedLight != null) {
						unselectedIcon = new ImageIcon(unselectedLight.getScaledInstance(16, 16, Image.SCALE_SMOOTH));
					}
				}
			}
		}		if(theIdx>=0) {
			command = uri.substring(0, theIdx);
		}
		else {
			theIdx = uri.indexOf(':');
			if(theIdx>=0) {
				command = uri.substring(0, theIdx);
			}
		}

		if(command.equals("showconsole")) {
			showConsole();
		}    
	}

	@Override
	public String getName() {
		return "Security Transaction Loader";
	}

	private synchronized void showConsole() {
		root = context.getRootAccount();
		acctBook = context.getCurrentAccountBook();
		mapAccounts = new TreeMap<>();
		tranSet = acctBook.getTransactionSet();
		JFrame frame = new JFrame("Load Security Transactions - Build "+buildStr);
		frame.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
		panScreen = new FileSelectWindow();
		frame.getContentPane().add(panScreen);
		//Display the window.
		frame.pack();
		frame.setLocationRelativeTo(null);
		frame.setVisible(true);
	}

	synchronized void closeConsole() {
		if(panScreen!=null) {
			panScreen = null;
		}
	}

}

/*
 * Copyright (c) 2014, Michael Bray. All rights reserved.
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
package com.moneydance.modules.features.budgetreport;

import java.awt.Image;
import java.awt.Toolkit;
import java.io.ByteArrayOutputStream;

import com.infinitekind.util.CustomDateFormat;
import com.moneydance.apps.md.controller.FeatureModule;
import com.moneydance.apps.md.controller.FeatureModuleContext;
import com.moneydance.apps.md.controller.UserPreferences;

/**
 * Moneydance extension to generate budget items for the 'new' type of budgets
 * 
 * Main class to create main window
 */

public class Main extends FeatureModule {
	public static CustomDateFormat cdate;
	private BudgetValuesWindow objBudgetmainWindow = null;
	public static FeatureModuleContext context;
	public UserPreferences up = null;
	public static Image imgIcon;
	public static String strBuild;

	@Override
	public void init() {
		// the first thing we will do is register this module to be invoked
		// via the application toolbar
		context = getContext();
		try {
			imgIcon = getIcon("/com/moneydance/modules/features/budgetreport/mrb icon2.png");
			context.registerFeature(this, "showconsole",
					imgIcon, getName());
		} catch (Exception e) {
			e.printStackTrace(System.err);
		}
	    int iBuild = getBuild();
	    strBuild = String.valueOf(iBuild);  
	}

	/*
	 * Get Icon is not really needed as Icons are not used. Included as the
	 * register feature method requires it
	 */

	private Image getIcon(String action) {
		try {
			ClassLoader cl = getClass().getClassLoader();
			java.io.InputStream in = cl
					.getResourceAsStream(action);
			if (in != null) {
				ByteArrayOutputStream bout = new ByteArrayOutputStream(1000);
				byte buf[] = new byte[256];
				int n = 0;
				while ((n = in.read(buf, 0, buf.length)) >= 0)
					bout.write(buf, 0, n);
				return Toolkit.getDefaultToolkit().createImage(
						bout.toByteArray());
			}
		} catch (Throwable e) {
		}
		return null;
	}
	/*
	 * This does not seem to be called, make sure handleEvent("md:file:closing") is present
	 */
	@Override
	public void cleanup() {
		closeConsole();
	}
  @Override
  public void unload() { cleanup(); }


	/*
	 * determine if file is being closed and close down extension
	 */
	@Override
	public void handleEvent(String appEvent) {

		if ("md:file:closing".equals(appEvent)) {
			closeConsole();
		}
	}

	/** Process an invocation of this module with the given URI */
	@Override
	public void invoke(String uri) {
		String command = uri;
		String strDateFormat;
		up = UserPreferences.getInstance();
		strDateFormat = up.getSetting(UserPreferences.DATE_FORMAT);
		cdate = new CustomDateFormat(strDateFormat);
		int theIdx = uri.indexOf('?');
		if (theIdx >= 0) {
			command = uri.substring(0, theIdx);
		} else {
			theIdx = uri.indexOf(':');
			if (theIdx >= 0) {
				command = uri.substring(0, theIdx);
			}
		}

		if (command.equals("showconsole")) {
			showConsole();
		}
	}

	@Override
	public String getName() {
		return "Budget Reporter";
	}

	private synchronized void showConsole() {
		objBudgetmainWindow = new BudgetValuesWindow(this);
		if (objBudgetmainWindow.bError)
			return;
		objBudgetmainWindow.setTitle("Budget Report - Build "+strBuild);
		if (imgIcon != null)
			objBudgetmainWindow.setIconImage(imgIcon);
		objBudgetmainWindow.setVisible(true);
	}

	FeatureModuleContext getUnprotectedContext() {
		return getContext();
	}

	synchronized void closeConsole() {
		if (objBudgetmainWindow != null) {
			if (!objBudgetmainWindow.bError)
				objBudgetmainWindow.goAway();
			objBudgetmainWindow = null;
			System.gc();
		}
	}
}

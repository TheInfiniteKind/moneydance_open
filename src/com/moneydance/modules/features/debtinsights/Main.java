/************************************************************\
 *       Copyright (C) 2001 Appgen Personal Software        *
\************************************************************/

package com.moneydance.modules.features.debtinsights;

import java.awt.Image;
import java.awt.Toolkit;
import java.io.ByteArrayOutputStream;

import com.moneydance.apps.md.controller.FeatureModule;
import com.moneydance.apps.md.controller.FeatureModuleContext;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.moneydance.awt.AwtUtil;
import com.moneydance.modules.features.debtinsights.debtmanager.DebtManagerWindow;
import com.moneydance.modules.features.debtinsights.ui.acctview.CreditCardAccountView;

/**
 * Pluggable module used to give users access to a Account List interface to
 * Moneydance.
 */

public class Main extends FeatureModule
{
	//private static Log log = LogFactory.getLog(Main.class);
	private DebtAccountListWindow	accountListWindow	= null;
	private DebtManagerWindow	debtManagerWindow	= null;

	@Override
	public void init()
	{
		// the first thing we will do is register this module to be invoked
		// via the application toolbar
		FeatureModuleContext context = getContext();
		try
		{
			context.registerFeature(this, "debtmanager",
			        getIcon(), "Debt Insights");
			context.registerHomePageView(this,
			        new CreditCardAccountView(this)); //.getAccountBook()));			
		}
		catch (Exception e)
		{
			e.printStackTrace(System.err);
		}
	}

	@Override
	public void cleanup()
	{
		closeConsole();
	}

	private Image getIcon()
	{
		try
		{
			ClassLoader cl = getClass().getClassLoader();
			java.io.InputStream in = cl
			        .getResourceAsStream("/com/moneydance/modules/features/debtinsights/icon.gif");
			if (in != null)
			{
				ByteArrayOutputStream bout = new ByteArrayOutputStream(1000);
				byte buf[] = new byte[256];
				int n = 0;
				while ((n = in.read(buf, 0, buf.length)) >= 0)
					bout.write(buf, 0, n);
				return Toolkit.getDefaultToolkit().createImage(
				        bout.toByteArray());
			}
		}
		catch (Throwable e)
		{
		}
		return null;
	}

	/** Process an invokation of this module with the given URI */
	@Override
	public void invoke(String uri)
	{
		String command = uri;
		int theIdx = uri.indexOf('?');
		if (theIdx >= 0)
		{
			command = uri.substring(0, theIdx);
		}
		else
		{
			theIdx = uri.indexOf(':');
			if (theIdx >= 0)
			{
				command = uri.substring(0, theIdx);
			}
		}

		if (command.equals("debtmanager"))
		{
			creditCardReport();
		}
	}

	@Override
	public String getName()
	{
		return "Debt Insights";
	}

	private synchronized void creditCardReport()
	{
		if (debtManagerWindow == null)
		{
			debtManagerWindow = new DebtManagerWindow(getMDGUI());
		}
		if (this.debtManagerWindow.refresh())
		{
			this.debtManagerWindow.pack();
			this.debtManagerWindow.toFront();
			this.debtManagerWindow.requestFocus();
			AwtUtil.centerWindow(debtManagerWindow);
			debtManagerWindow.setVisible(true);
		}
		else
		{
			this.debtManagerWindow.dispose();
			this.debtManagerWindow = null;
		}
	}
	
	FeatureModuleContext getUnprotectedContext()
	{
		return getContext();
	}

	synchronized void closeConsole()
	{
		if (accountListWindow != null)
		{
			accountListWindow.goAway();
			accountListWindow = null;
			System.gc();
		}
	}
	

    public com.moneydance.apps.md.controller.Main getMDMain()
    {
        return (com.moneydance.apps.md.controller.Main) getUnprotectedContext();
    }

    public MoneydanceGUI getMDGUI() {
			return (MoneydanceGUI)getMDMain().getUI();
    }
	

//	/* (non-Javadoc)
//	 * @see com.moneydance.apps.md.controller.FeatureModule#handleEvent(java.lang.String)
//	 */
	@Override
	public void handleEvent(String appEvent)
	{
		super.handleEvent(appEvent);
	}

}

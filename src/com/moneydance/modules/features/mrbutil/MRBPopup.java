package com.moneydance.modules.features.mrbutil;

/**
 * Interface for using pop menus on data columns in a report.  If defined for a report the 
 * Report Viewer will call getMenuItems to obtain the string values for a pop up menu on
 * the specified cell in the port
 * <p>
 * When the user clicks on an entry on the pop up menu actionPopup is called
 * @author Mike
 *
 */
public abstract interface MRBPopup {
	/**
	 * method called when user clicks on a Pop up menu option
	 * @param strActionp - the menu item chosen
	 * @param iRowp the row of the cell
	 * @param iColp the column of the cell
	 */
	public abstract void actionPopup (String strActionp, int iRowp, int iColp);
	/**
	 * called when the user right clicks on a cell
	 * @param iRowp the row of the cell
	 * @param iColp the column of the cell
	 * @return an array of menu choices that will be displayed
	 */
	public abstract String[] getMenuItems(int iRowp, int iColp);

}

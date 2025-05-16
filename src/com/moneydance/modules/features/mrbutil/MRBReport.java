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
package com.moneydance.modules.features.mrbutil;

import java.util.Vector;

/**
 *
 * Defines a standard report. The report consists of a defined set of rows and
 * columns organised in a table.
 * <p>
 * The report has a standard structure which contains:
 * 
 * <ul>
 * <li>A name - displayed in the top left of the screen
 * <li>A main title - displayed centrally using the Moneydance defined title font
 * <li>A subtitle - displayed centrally below the title using the Moneydance defined subtitle font
 * <li>A footer - printed (not displayed) at the bottom left of the report using the Moneydance defined printer font
 * </ul>
 * <p>
 * Rows of data are stored in a vector of MRBRecordRows
 * <p>
 * Columns are split into Row Header Columns, i.e. those columns that contain a description for a row and Data Columns.
 *  The number of columns used for the row headers is
 * defined and counts from the left.
 * <p>
 * A report can have a popup menu. This is used to add popup menus to Data
 * Columns
 * 
 * @author Mike Bray
 * @version 1.0
 * @since 2015-05-06
 * @see MRBRecordRow MRBRecordRow
 */
public class MRBReport {
	private String strName = "";
	private String strTitle = "";
	private String strSubTitle = "";
	private String strFooter = "";
	private int[] arrColumnWidths;
	private String[] arrColumnNames;
	private int iRowHeaders = 0;
	private MRBPopup objPopup = null;
	private Vector<MRBRecordRow> vRows = new Vector<MRBRecordRow>();

	/**
	 * Create a new Report
	 * 
	 * @param strNamep The name of the report
	 * @param arrColumnNamesp an array of column headings. These can contain HTML
	 */
	public MRBReport(String strNamep, String[] arrColumnNamesp) {
		this.strName = strNamep;
		this.arrColumnNames = arrColumnNamesp;
	}

	/**
	 * Get the name of the report
	 * 
	 * @return Report Name
	 */
	public String getName() {
		return this.strName;
	}

	/**
	 * Set the Report Title
	 * 
	 * @param title string title
	 */
	public void setTitle(String title) {
		this.strTitle = title;
	}

	/**
	 * Get the Report Title
	 * 
	 * @return Report Title
	 */
	public String getTitle() {
		return this.strTitle;
	}

	/**
	 * Get the number of columns that make up the row headers
	 * 
	 * @return Row Headers
	 */
	public int getRowHeaders() {
		return iRowHeaders;
	}

	/**
	 * Set the number of columns that make up the row headers
	 * 
	 * @param iRowHeadersp number of columns
	 */
	public void setRowHeaders(int iRowHeadersp) {
		iRowHeaders = iRowHeadersp;
	}

	/**
	 * Set the Report Subtitle
	 * 
	 * @param subTitle report subtitle
	 */
	public void setSubTitle(String subTitle) {
		this.strSubTitle = subTitle;
	}

	/**
	 * Get the Report Subtitle
	 * 
	 * @return - subtitle
	 */
	public String getSubTitle() {
		return this.strSubTitle;
	}

	/**
	 * Set the Report Footer
	 * 
	 * @param subFooterp report footer
	 */
	public void setFooter(String subFooterp) {
		strFooter = subFooterp;
	}

	/**
	 * Get the Report Footer
	 * 
	 * @return Report Footeer
	 */
	public String getFooter() {
		return this.strFooter;
	}

	/**
	 * Get the Report Column Count
	 * 
	 * @return number of columns
	 */
	public int getColumnCount() {
		return this.arrColumnNames.length;
	}

	/**
	 * Get the column header for the specific column (starts at 0)
	 * 
	 * @param col column number
	 * @return  the header for the specified column
	 */
	public String getColumnName(int col) {
		return this.arrColumnNames[col];
	}

	/**
	 * Get the column header for the specific column (starts at 0) stripped of
	 * HTML
	 * <p>
	 * breaks (&#60;br&#62;) are changed to new lines, &#60;html&#62; and &#60;&#47;html&#62; tags are removed
	 * 
	 * @param col column number
	 * @return the header for the specified column
	 */

	public String getColumnNameNoHTML(int col) {
		String strName;
		strName = arrColumnNames[col].replaceFirst("<html>", "");
		strName = strName.replaceFirst("<br>", "\n");
		strName = strName.replaceFirst("</html>", "");
		return strName;
	}

	/**
	 * Get an array of Column Widths
	 * 
	 * @return - array of widths
	 */
	public int[] getColumnWidths() {
		return this.arrColumnWidths;
	}

	/**
	 * Set the column widths
	 * 
	 * @param arrColumnWidthsp array of column widths in pixels
	 */
	public void setColumnWidth(int[] arrColumnWidthsp) {
		this.arrColumnWidths = arrColumnWidthsp;
	}

	/**
	 * Get the defined popup class for this report 
	 * 
	 * @return popup class
	 * @see MRBPopup
	 */
	public MRBPopup getPopUp() {
		return objPopup;
	}

	/**
	 * Set the Popup class for this report
	 * 
	 * @param objPopupp Popup
	 */
	public void setPopup(MRBPopup objPopupp) {
		objPopup = objPopupp;
	}

	/**
	 * Get the number of rows in the report
	 * 
	 * @return number of rows
	 */
	public int getRowCount() {
		return this.vRows.size();
	}

	/**
	 * Get the row at index
	 * 
	 * @param i index of required row
	 * @return MRBRecordRow
	 */
	public MRBRecordRow getRow(int i) {
		return this.vRows.elementAt(i);
	}

	/**
	 * Add a row to the Report
	 * 
	 * @param row row to be added to the end of the report
	 */
	public void addRow(MRBRecordRow row) {
		this.vRows.addElement(row);
	}

	/**
	 * Remove the row at the specified index
	 * 
	 * @param rowIndex index of row to delete
	 */
	public void removeRow(int rowIndex) {
		this.vRows.remove(rowIndex);
	}

	/**
	 * Insert a row after the specified index
	 * 
	 * @param row MRBRecordRow to be inserted
	 * @param where index of where to be inserted
	 */
	public void insertRow(MRBRecordRow row, int where) {
		this.vRows.insertElementAt(row, where);
	}

}

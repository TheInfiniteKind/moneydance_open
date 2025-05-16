package com.moneydance.modules.features.mrbutil;

import java.awt.Color;
import java.awt.Font;
import java.awt.FontMetrics;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.font.FontRenderContext;
import java.awt.font.LineMetrics;
import java.awt.geom.AffineTransform;

import javax.swing.JFrame;
import javax.swing.JOptionPane;

import com.moneydance.apps.md.controller.UserPreferences;
/**
 * Prints a report.
 * <p>
 * The number of pages required is calculated. The user is asked to select the required number
 *  of pages wide is required.  The report is scaled accordingly
 *  
 * @author Mike Bray
 *
 */
public class MRBReportPrinter implements MRBPrintable {
	private UserPreferences prefs;
	private MRBReport report;
	private MRBReportFonts fonts = null;
	private MRBReportViewer viewer;
	private double normalHeaderHeight = 0.0D;
	private FontRenderContext frc;
	private int numLinesTitlePage = 5;
	private int numLinesNormalPage = 5;
	private int numPages = 1;
	private int lineHeight = 10;
	private int[] columnWidths = null; // calculated widths
	private int[] pageColumns = null; // start column for each page
	private double[] columnRelativeWidths = null; // original widths from
														// Viewer
	private int COLUMN_SPACING = 1;
	private Color color1 = new Color(255, 255, 255);
	private Color color2 = new Color(245, 245, 245);

	private boolean infoCalculated = false;
	private boolean pagesCalculated = false;
	private int numHeaderRows = 1;
	private int numPagesWide; // number of horizontal pages
	private String defaultString = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!$%^&*()-+= {}[]";
	private double scale = 1.0D;
	private double totalColumnWidth;
	/**
	 * Creates a report printer
	 * 
	 * @param viewer - the MRBReportViewer that is displaying the report to be printed
	 * @param arrdColWidths - the column widths
	 */
	public MRBReportPrinter(MRBReportViewer viewer, double[] arrdColWidths) {
		prefs = UserPreferences.getInstance();
		this.viewer = viewer;
		report = this.viewer.getReport();
		columnRelativeWidths = arrdColWidths;
		fonts = MRBReportFonts.getPrintingFonts(prefs);
	}
	@Override
	public String getTitle() {
		return report.getTitle();
	}

	@Override
	public boolean usesWholePage() {
		return false;
	}


	@Override
	public boolean printPage(Graphics graphics, int crntPage,
			double width, double height, int resolution) {
		calculatePages(width, height);
		int realPage;
		int horizontalPage;
		if ((width <= 0.0D) || (height <= 0.0D))
			return false;

		int leftX = 0;
		if (numPagesWide > 1) {
			/*
			 * report will be more than one page wide determine actual page for
			 * printing purposes
			 */
			realPage = crntPage / (numPagesWide);
		} else
			realPage = crntPage;
		horizontalPage = crntPage - (realPage * numPagesWide)+1;
		/*
		 * set up 2 Dimension Graphics
		 */
		Graphics2D graphics2D = (Graphics2D) graphics;

		calculateInfo(graphics2D, height, width);

		int imageWidth = (int) Math.floor(width / scale);
		int imageHeight = (int) Math.floor(height / scale);

		int crntY = 0;
		graphics2D.setColor(Color.black);

		int crntLine = 0;

		int reportRowCount = report.getRowCount();
		int numCols = report.getColumnCount();
		int lineCrntPage;
		if (realPage <= 0) {
			lineCrntPage = numLinesTitlePage;
		} else {
			crntLine += numLinesTitlePage;
			int pageCount = realPage;
			while (pageCount > 1) {
				crntLine += numLinesNormalPage;
				pageCount--;
			}
			if (crntLine >= reportRowCount) 
				lineCrntPage = numLinesNormalPage - crntLine+reportRowCount;
			else
				lineCrntPage = numLinesNormalPage;
		}

		setOutputScale(graphics2D, (int) Math.ceil(width));
		if (realPage <= 0) {
			crntY = drawTitleAndSubtitle(graphics2D, leftX, crntY,
					imageWidth);
		}

		crntY = drawReportColumnHeaders(graphics2D, leftX, crntY,
				imageWidth, crntPage - realPage * (numPagesWide));

		crntLine = drawReportRows(graphics2D, leftX, crntY, imageWidth,
				crntLine, lineCrntPage, reportRowCount, numCols, crntPage - realPage
						* (numPagesWide));

		drawPageFooterText(graphics2D, leftX, imageWidth, imageHeight,
				realPage, crntPage - realPage * (numPagesWide));

		/*
		 * if all rows have been dealt with and the last horizontal page has been printed
		 * return false to indicate end of report.
		 */
		if (crntLine >= report.getRowCount()
				&& (horizontalPage >= numPagesWide))
			return false;
		return true;
	}

	private void setOutputScale(Graphics2D graphics2D, int pageWidth) {
		if (scale != 1.0D) {
			graphics2D.scale(scale, scale);
		} else {
			/*
			 * Move origin so text is in centre of page
			 */
			int iDiff = (int) Math
					.floor((pageWidth - totalColumnWidth) / 2.0D);
			graphics2D.translate(iDiff, 0);
		}
	}

	private int drawTitleAndSubtitle(Graphics2D g, int leftX, int currentY,
			double width) {
		g.setFont(fonts.getTitleFont());
		frc= g.getFontRenderContext();
		LineMetrics lm = fonts.getTitleFont().getLineMetrics(defaultString, frc);
		FontMetrics fm = g.getFontMetrics();
		currentY += Math.round(lm.getHeight());
		String title = report.getTitle();
		if ((title != null) && (title.length() > 0)) {
			g.drawString(title,
					leftX + (int) (width / 2.0D - fm.stringWidth(title) / 2),
					currentY - lm.getDescent() - 1);
		}
		String date = report.getSubTitle();
		if ((date != null) && (date.length() > 0)) {
			g.setFont(fonts.getSubtitleFont());
			frc= g.getFontRenderContext();
			lm = fonts.getSubtitleFont().getLineMetrics(defaultString, frc);
			fm = g.getFontMetrics();
			currentY += Math.round(lm.getHeight());
			g.drawString(date,
					leftX + (int) (width / 2.0D - fm.stringWidth(date) / 2),
					currentY - lm.getDescent() - 1);
		}
		return currentY;
	}

	private int drawReportColumnHeaders(Graphics2D g, int leftX, int currentY,
			double width, int page) {
		g.setFont(fonts.getHeaderFont());
		frc= g.getFontRenderContext();
		LineMetrics lm = fonts.getHeaderFont().getLineMetrics(defaultString, frc);
		FontMetrics fm = g.getFontMetrics();
		int rowHeight = Math.round(lm.getHeight());
		currentY = (int) (currentY + normalHeaderHeight);
		int headerHeight = (int) normalHeaderHeight;
		g.setClip(leftX, currentY - headerHeight, (int) width, headerHeight);
		g.setColor(Color.lightGray);
		g.drawLine(leftX, currentY - 2, leftX + (int) width, currentY - 2);

		int headerY = currentY;
		for (int row = numHeaderRows - 1; row >= 0; row--) {
			int currentX = leftX;
			int lastColumn;
			int firstColumn = pageColumns[page];
			if (page < numPagesWide-1)
				lastColumn = pageColumns[page + 1];
			else
				lastColumn = report.getColumnCount();
			/*
			 * if not first horizontal page draw row headers
			 */
			if (firstColumn > 0) {
				for (int ii = 0; ii < report.getRowHeaders(); ii++) {
					String columnName = report.getColumnNameNoHTML(ii);
					String[] lines = columnName.split("\n");

					g.setClip(currentX, headerY - rowHeight,
							columnWidths[ii], rowHeight);
					if (ii > 0) {
						g.setColor(Color.lightGray);
						g.drawLine(currentX + 1, currentY - headerHeight,
								currentX + 1, currentY);
					}

					if (row < lines.length) {
						if (!lines[row].isBlank()) {
							g.setColor(Color.black);
							g.drawString(
									lines[row],
									currentX + columnWidths[ii] / 2
											- fm.stringWidth(lines[row]) / 2,
									headerY - lm.getDescent() - 1);
						}
					}
					currentX += columnWidths[ii] + COLUMN_SPACING;
				}
			}
			/*
			 * Draw columns for this page
			 */
			for (int ii = firstColumn; ii < lastColumn; ii++) {
				String columnName = report.getColumnNameNoHTML(ii);
				String[] lines = columnName.split("\n");

				g.setClip(currentX, headerY - rowHeight, columnWidths[ii],
						rowHeight);
				if (ii > 0) {
					g.setColor(Color.lightGray);
					g.drawLine(currentX + 1, currentY - headerHeight,
							currentX + 1, currentY);
				}

				if (row < lines.length) {
					if (!lines[row].isBlank()) {
						g.setColor(Color.black);
						g.drawString(
								lines[row],
								currentX + columnWidths[ii] / 2
										- fm.stringWidth(lines[row]) / 2,
								headerY - lm.getDescent() - 1);
					}
				}
				currentX += columnWidths[ii] + COLUMN_SPACING;
			}
			headerY -= rowHeight;
		}
		return currentY;
	}

	private int drawReportRows(Graphics2D g, int leftX, int startY,
			double pageWidth, int startLineNum, int totalLinesPage, int totalRowsReport,
			int numCols, int page) {
		int currentY = startY;
		int lineOnPage = 0;
		g.setFont(fonts.getNormalFont());
		frc= g.getFontRenderContext();
		LineMetrics lm = fonts.getNormalFont().getLineMetrics(defaultString, frc);
		FontMetrics fm = g.getFontMetrics();
		int descent = Math.round(lm.getDescent()) + 1;
		/*
		 * determine first and last columns on page
		 */
		int lastColumn;
		int firstColumn = pageColumns[page];
		if (page < numPagesWide-1)
			lastColumn = pageColumns[page + 1];
		else
			lastColumn = numCols;
		/*
		 * loop through and draw each line
		 */
		while ((lineOnPage < totalLinesPage) && (startLineNum < totalRowsReport)) {
			currentY += lineHeight;
			int currentX = leftX;
			MRBRecordRow row = report.getRow(startLineNum);
			/*
			 * 
			 */
			if (row != null) {
				g.setClip(currentX, currentY - lineHeight, (int) pageWidth,
						lineHeight);
				g.setColor(lineOnPage % 2 == 0 ? color1 : color2);
				g.fillRect(currentX, currentY - lineHeight, (int) pageWidth,
						lineHeight);
				/*
				 * if not first horizontal page draw row headers
				 */
				if (firstColumn > 0) {
					for (int c = 0; c < report.getRowHeaders(); c++) {
						int cField = c;
						String value = row.getLabel(cField);
						g.setClip(currentX, currentY - lineHeight,
								columnWidths[c], lineHeight);
						if ((value != null) && (value.length() > 0)) {
							if (row.getBorder(cField) == MRBReportViewer.BORDER_TOP) {
								g.setColor(Color.gray);
								g.drawLine(currentX,
										currentY - lineHeight + 1, currentX
												+ columnWidths[c], currentY
												- lineHeight + 1);
							} else if (row.getBorder(cField) == MRBReportViewer.BORDER_BOTTOM) {
								g.setColor(Color.black);
								g.drawLine(currentX,
										currentY - lineHeight + 1, currentX
												+ columnWidths[c], currentY
												- lineHeight + 1);
							}

							switch (row.getStyle(cField)) {
							case MRBReportViewer.STYLE_BOLD:
								g.setFont(fonts.getBoldFont());
								break;
							case MRBReportViewer.STYLE_ITALIC:
								g.setFont(fonts.getItalicFont());
								break;
							case 1:
							case 3:
							default:
								g.setFont(fonts.getNormalFont());
							}

							g.setColor(row.getColorFG(cField));
							fm = g.getFontMetrics();
							switch (row.getAlignment(cField)) {
							case MRBReportViewer.ALIGN_RIGHT:
								g.drawString(
										value,
										currentX + columnWidths[c]
												- fm.stringWidth(value) - 4,
										currentY - descent);
								break;
							case MRBReportViewer.ALIGN_CENTER:
								g.drawString(
										value,
										currentX
												+ (columnWidths[c] - fm
														.stringWidth(value))
												/ 2, currentY - descent);
								break;
							default:
								g.drawString(value, currentX, currentY
										- descent);
							}
						}

						g.setColor(Color.black);
						currentX += columnWidths[c] + COLUMN_SPACING;
					}
				}
				/*
				 * Draw columns for this page
				 */
				for (int c = firstColumn; c < lastColumn; c++) {
					int cField = c;
					String value = row.getLabel(cField);
					g.setClip(currentX, currentY - lineHeight,
							columnWidths[c], lineHeight);
					if ((value != null) && (value.length() > 0)) {
						if (row.getBorder(cField) == MRBReportViewer.BORDER_TOP) {
							g.setColor(Color.gray);
							g.drawLine(currentX, currentY - lineHeight + 1,
									currentX + columnWidths[c], currentY
											- lineHeight + 1);
						} else if (row.getBorder(cField) == MRBReportViewer.BORDER_BOTTOM) {
							g.setColor(Color.black);
							g.drawLine(currentX, currentY - lineHeight + 1,
									currentX + columnWidths[c], currentY
											- lineHeight + 1);
						}

						switch (row.getStyle(cField)) {
						case MRBReportViewer.STYLE_BOLD:
							g.setFont(fonts.getBoldFont());
							break;
						case MRBReportViewer.STYLE_ITALIC:
							g.setFont(fonts.getItalicFont());
							break;
						case 1:
						case 3:
						default:
							g.setFont(fonts.getNormalFont());
						}

						g.setColor(row.getColorFG(cField));
						fm = g.getFontMetrics();
						switch (row.getAlignment(cField)) {
						case MRBReportViewer.ALIGN_RIGHT:
							g.drawString(value, currentX + columnWidths[c]
									- fm.stringWidth(value) - 4, currentY
									- descent);
							break;
						case MRBReportViewer.ALIGN_CENTER:
							g.drawString(
									value,
									currentX
											+ (columnWidths[c] - fm
													.stringWidth(value)) / 2,
									currentY - descent);
							break;
						default:
							g.drawString(value, currentX, currentY - descent);
						}
					}

					g.setColor(Color.black);
					currentX += columnWidths[c] + COLUMN_SPACING;
				}
				startLineNum++;
				lineOnPage++;
			}
		}
		return startLineNum;
	}

	private void drawPageFooterText(Graphics2D g, int leftX, double width,
			double height, int pageIndex, int iHorPage) {
		String pageStr = report.getFooter();
		pageStr = pageStr.replaceAll("\\{pagenum\\}",
				String.valueOf(pageIndex + 1) + " - "
						+ String.valueOf(iHorPage + 1));
		pageStr = pageStr.replaceAll("\\{numpages\\}",
				String.valueOf(numPages) + " - "
						+ String.valueOf(numPagesWide));
		g.setFont(fonts.getNormalFont());
		g.setColor(Color.black);
		frc= g.getFontRenderContext();
		LineMetrics lm = fonts.getNormalFont().getLineMetrics(defaultString, frc);
		FontMetrics fm = g.getFontMetrics();
		g.setClip(leftX, (int) (height - fm.getHeight()), (int) width,
				Math.round(lm.getHeight()));
		g.drawString(pageStr, leftX, (int) (height - lm.getDescent()));
	}


	/**
	 * Determine the number of horizontal pages required and then scale
	 * depending on user choice
	 * @param width - width of the page
	 * @param height - height of the page
	 */
	public synchronized void calculatePages(double width, double height) {
		if (pagesCalculated)
			return;
		double columnWidth = 0.0D;
		double pageWidth = 0.0D;
		double headerWidth = 0.0D;
		pageColumns = new int[report.getColumnCount()];
		columnWidths = new int[report.getColumnCount()];
		int currentPage = 0;
		numPagesWide = 0;
		pageColumns[0] = 0;
		/*
		 * determine width of row headers to be used on each page
		 */
		for (int j = 0; j < report.getRowHeaders(); j++) {
			headerWidth += ((int) Math.ceil(columnRelativeWidths[j]));
		}
		/*
		 * Determine number of horizontal pages using no scaling
		 */
		totalColumnWidth = 0.0D;
		for (int i = 0; i < columnWidths.length; i++) {
			columnWidths[i] = ((int) Math.ceil(columnRelativeWidths[i]));
			if ((pageWidth + columnRelativeWidths[i]) > width) {
				pageColumns[++currentPage] = i;
				pageWidth = headerWidth;
			}
			columnWidth += columnRelativeWidths[i];
			pageWidth += columnRelativeWidths[i];
		}
		totalColumnWidth = columnWidth;
		numPagesWide = currentPage + 1;
		;

		if (numPagesWide > 1) {
			/*
			 * more than one page required, ask user to select number to print
			 */
			boolean done = false;
			while (!done) {

				JFrame frmChoice = new JFrame();
				String[] strNumPages = new String[numPagesWide];
				for (int i = 0; i < numPagesWide; i++)
					strNumPages[i] = String.valueOf(i + 1);
				String strChoice = (String) JOptionPane.showInputDialog(
						frmChoice,
						"Your report will be "
								+ String.valueOf(currentPage + 1)
								+ " pages wide \n\n"
								+ "Select the number of pages required",
						"Report Size", JOptionPane.PLAIN_MESSAGE, null,
						strNumPages, strNumPages[currentPage]);

				// If a string was returned, set new pages wide
				if ((strChoice != null) && (strChoice.length() > 0)) {
					numPagesWide = Integer.parseInt(strChoice);
					done = true;
				}
			}
			double newWidth = ((numPagesWide) * headerWidth + totalColumnWidth)
					/ (numPagesWide);
			totalColumnWidth = 0.0D; // will be set to max page width
			pageColumns[0] = 0;
			currentPage = 0;
			pageWidth = 0.0D;
			for (int i = 0; i < columnWidths.length; i++) {
				if ((pageWidth + columnRelativeWidths[i]) > newWidth) {
					pageColumns[++currentPage] = i;
					totalColumnWidth = Math.max(totalColumnWidth,
							pageWidth);
					pageWidth = headerWidth;
				}
				columnWidth += columnRelativeWidths[i];
				pageWidth += columnRelativeWidths[i];
			}
			totalColumnWidth = Math.max(totalColumnWidth, pageWidth);
			numPagesWide = currentPage + 1;
				
		}
		pagesCalculated = true;
	}

	private synchronized void calculateInfo(Graphics2D graphics2D,
			double height, double width) {
		if (infoCalculated)
			return;
		scale = 1.0D;
		/*
		 * TotalColumnWidth set to maximum page width. All pages scaled to this
		 */
		if (totalColumnWidth > width) {
			scale = (width / totalColumnWidth);
		}

		fonts = MRBReportFonts.getPrintingFonts(prefs);

		AffineTransform oldTrans = graphics2D.getTransform(); // save for restore
																	

		setOutputScale(graphics2D, (int) Math.ceil(width));
		int iScaledHeight = (int) Math.floor(height / scale);

		scaleHeaderFont(graphics2D);


		frc= graphics2D.getFontRenderContext();
		LineMetrics lm = fonts.getNormalFont().getLineMetrics(defaultString, frc);
		/*
		 * calculate line height with 4 units of spacing
		 */
		lineHeight = (Math.round(lm.getHeight()) + 4);

		/*
		 * get Title font height
		 */
		double titleHeaderHeight = graphics2D.getFontMetrics(
				fonts.getTitleFont()).getHeight();
		/*
		 * add subtitle height if present
		 */
		String subtitle = report.getSubTitle();
		lm = fonts.getSubtitleFont().getLineMetrics(defaultString, frc);
		if (!subtitle.isBlank()) {
			titleHeaderHeight += lm.getHeight();
		}
		/*
		 * calculate column header height, add 10 units for spacing
		 */
		lm = fonts.getHeaderFont().getLineMetrics(defaultString, frc);
		int headerRowHeight = Math.round(lm.getHeight())+5;
		titleHeaderHeight += headerRowHeight+5;
		/*
		 * calculate footer height with 4 units for spacing 
		 */
		
		lm = fonts.getNormalFont().getLineMetrics(defaultString, frc);
		double footerHeight = lm.getHeight() + 4;

		normalHeaderHeight = (numHeaderRows * headerRowHeight + 2);

		/*
		 * calculate number of lines for title page and normal pages
		 */
		numLinesTitlePage = Math.max(5, (int) Math.floor((iScaledHeight
				- titleHeaderHeight - footerHeight)
				/ lineHeight));

		numLinesNormalPage = Math.max(5, (int) Math.floor((iScaledHeight
				- normalHeaderHeight - footerHeight)
				/ lineHeight));

		/*
		 * calculate number of pages deep
		 */
		int iRows = report.getRowCount();
		iRows -= numLinesTitlePage;
		while (iRows > 0) {
			numPages += 1;
			iRows -= numLinesNormalPage;
		}
		/*
		 * restore graphics
		 */
		graphics2D.setTransform(oldTrans);
		infoCalculated = true;
	}

	/*
	 * reduces header font size until column header text fits into column width
	 */

	private void scaleHeaderFont(Graphics2D obj2DGraphics) {
		Font fntHeader = fonts.getHeaderFont();
		float fHeaderFontSize = fntHeader.getSize();
		boolean bUpdate = false;
		FontMetrics fm = obj2DGraphics.getFontMetrics(fntHeader);
		for (int ii = 0; ii < columnWidths.length; ii++) {
			String strColumnName = report.getColumnNameNoHTML(ii);
			if (!strColumnName.isBlank()) {
				String[] arrstrLines = strColumnName.split("\n");
				numHeaderRows = Math.max(numHeaderRows, arrstrLines.length);
				for (String strLine : arrstrLines)
					if (!strLine.isBlank())
						while ((fm.stringWidth(strLine) > columnWidths[ii])
								&& (fHeaderFontSize > 5.0F)) {
							fHeaderFontSize -= 0.5F;
							fntHeader = fntHeader.deriveFont(fHeaderFontSize);
							fm = obj2DGraphics.getFontMetrics(fntHeader);
							bUpdate = true;
						}
			}
		}
		if (bUpdate)
			fonts.updateHeaderFontSize(fHeaderFontSize);
	}

}

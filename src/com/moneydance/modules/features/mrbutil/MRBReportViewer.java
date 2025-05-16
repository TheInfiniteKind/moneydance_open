package com.moneydance.modules.features.mrbutil;

import java.awt.Color;
import java.awt.Component;
import java.awt.Dimension;
import java.awt.FontMetrics;
import java.awt.GridBagLayout;
import java.awt.Point;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.ComponentEvent;
import java.awt.event.ComponentListener;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;

import javax.swing.BorderFactory;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JMenuItem;
import javax.swing.JPanel;
import javax.swing.JPopupMenu;
import javax.swing.JScrollPane;
import javax.swing.JTable;
import javax.swing.JTextField;
import javax.swing.SwingUtilities;
import javax.swing.border.EmptyBorder;
import javax.swing.table.AbstractTableModel;
import javax.swing.table.TableCellRenderer;
import javax.swing.table.TableColumn;
import javax.swing.table.TableColumnModel;

import com.moneydance.apps.md.controller.PreferencesListener;
import com.moneydance.awt.AwtUtil;
import com.moneydance.awt.GridC;
/**
 * Displays a standard report in a scrollable window
 * @author Mike Bray
 *
 */
public class MRBReportViewer extends JPanel implements PreferencesListener {
	/*
	 * Constants
	 */
	/**
	 * Sets the font to Bold
	 */
	public static final byte STYLE_BOLD = 2;
	/**
	 * Sets the font to italic
	 */
	public static final byte STYLE_ITALIC = 4;
	/**
	 * Aligns the data to the left of the cell
	 */
	public static final byte ALIGN_LEFT = 0;
	/**
	 * Aligns the data in the centre of the cell
	 */
	public static final byte ALIGN_CENTER = 1;
	/**
	 * Aligns the data to the right of the cell
	 */
	public static final byte ALIGN_RIGHT = 2;
	/**
	 * Places a 2 pixel border at the top of the cell
	 */
	public static final byte BORDER_TOP = 1;
	/**
	 * Places a 2 pixel border at the bottom of the cell
	 */
	public static final byte BORDER_BOTTOM = 2;
	/**
	 * Places a 2 pixel border at the top and bottom of the cell
	 */
	public static final byte BORDER_BOTH = 3;
	/**
	 * Places a 1 pixel border at the top of the cell
	 */
	public static final byte BORDER_TOP_HALF = 4;
	/**
	 * Places a 1 pixel border at the bottom of the cell
	 */
	public static final byte BORDER_BOTTOM_HALF = 5;
	/**
	 * Places a 1 pixel border at the top and bottom of the cell
	 */
	public static final byte BORDER_BOTH_HALF = 6;
	private String strData = "12345678901234567890123456789012345678901234567890";
	private JPanel panButtons;
	private JPanel panHeader;
	private JPanel panViewer;
	private JTextField title;
	private JTextField subTitle;
	private ReportTable reportTab;
	private ReportTableModel reportMod;
	private MRBReport report;
	private final JButton butPrint;
	private final JButton butClose;
	/*
	 * pop up menu items
	 */
	private JPopupMenu menPopup;
	private ActionListener menAction;
	private String [] strMenuItems;
	
	private JLabel lblName;
	private MRBPreferences2 preferences;
	private MRBReportFonts fonts;
	private int iSCREENWIDTH = 800;
	private int iSCREENDEPTH = 500;
	private int[] arrColumnWidths = null;
/**
 * Creates the panel for the report.  It is up to the caller to add this to a frame and display it.
 * <p> 
 * Note: the MRBPreferences must have been loaded prior to calling this constructor
 * </p>
 * @param reportp - The report to be displayed
 */
	public MRBReportViewer(MRBReport reportp) {
		report = reportp;
		preferences = MRBPreferences2.getInstance();
		setBackground(Color.white);
		title = new JTextField("");
		title.setBorder(null);
		title.setOpaque(false);
		title.setHorizontalAlignment(JTextField.CENTER);
		subTitle = new JTextField("");
		subTitle.setBorder(null);
		subTitle.setOpaque(false);
		subTitle.setHorizontalAlignment(JTextField.CENTER);
		preferencesUpdated();
		/*
		 * create the report table
		 */
		reportMod = new ReportTableModel();
		reportTab = new ReportTable(reportMod);
		reportTab.setAutoCreateColumnsFromModel(true);
		reportTab.setAutoResizeMode(0);
		reportTab.setRowSelectionAllowed(false);
		reportTab.setShowGrid(false);
		lblName = new JLabel(report.getName());
		lblName.setFont(fonts.getSubtitleFont());
		butPrint = new JButton("Print");
		butPrint.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				print();
			}
		});

		butClose = new JButton("Close");
		butClose.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				close();
			}
		});
		/*
		 * Set up screen
		 */
		addComponentListener(new ComponentListener() {

			@Override
			public void componentResized(ComponentEvent arg0) {
				JPanel panScreen = (JPanel) arg0.getSource();
				Dimension objDimension = panScreen.getSize();
				updatePreferences(objDimension);
			}

			@Override
			public void componentShown(ComponentEvent arg0) {
				// not needed
			}

			@Override
			public void componentHidden(ComponentEvent e) {
				// not needed
			}

			@Override
			public void componentMoved(ComponentEvent e) {
				// not needed
			}

		});
		setPreferences(); // set the screen sizes
		GridBagLayout gbcmain = new GridBagLayout();
		setLayout(gbcmain);
		/*
		 * Buttons Panel
		 */
		panButtons = new JPanel(new GridBagLayout());
		Dimension dimName = lblName.getPreferredSize();
		Dimension dimClose = butClose.getPreferredSize();
		Dimension dimPrint = butPrint.getPreferredSize();
		panButtons.add(
				lblName,
				GridC.getc(0, 0)
						.west()
						.padx(iSCREENWIDTH - dimName.width - dimClose.width
								- dimPrint.width - 50));
		panButtons.add(butPrint, GridC.getc(1, 0).east());
		panButtons.add(butClose, GridC.getc(2, 0).east());
		panButtons.setBorder(new EmptyBorder(8, 10, 8, 10));
		panButtons.setPreferredSize(new Dimension(iSCREENWIDTH, 50));
		panButtons.setBackground(new Color(211, 236, 248));
		panButtons.setForeground(Color.WHITE);
		/*
		 * Header Panel
		 */
		panHeader = new JPanel(gbcmain);
		panHeader.setBackground(Color.white);
		panHeader.setPreferredSize(new Dimension(iSCREENWIDTH,
				iSCREENDEPTH / 10));

		/*
		 * Viewer Panel
		 */
		panViewer = new JPanel(gbcmain);
		panViewer.setBackground(Color.white);
		panViewer.setPreferredSize(new Dimension(iSCREENWIDTH, (int) Math
				.round(iSCREENDEPTH * .9)));
		add(panButtons, GridC.getc(0, 0).fillx());
		add(panHeader,
				AwtUtil.getConstraints(0, 1, 1.0F, 0.0F, 1, 1, true, true));
		add(panViewer,
				AwtUtil.getConstraints(0, 2, 1.0F, 1.0F, 2, 1, true, true));

		setPreferredSize(new Dimension(iSCREENWIDTH, iSCREENDEPTH));

		reportTab.getTableHeader().setFont(
				MRBReportViewer.this.fonts.getBoldFont());
		panHeader.add(title, GridC.getc(0, 0).wx(1.0F).fillx());
		panHeader.add(subTitle,
				GridC.getc(0, 1).wx(1.0F).fillx().insets(4, 10, 10, 10));
		JScrollPane spViewer = new JScrollPane(reportTab);

		spViewer.setBorder(BorderFactory.createEmptyBorder());
		panViewer.add(spViewer, GridC.getc(0, 0).wxy(1.0F, 1.0F).fillboth());
		revalidate();
	}
	/**
	 * Adds the titles etc of the report to the report viewer. Called after the report has been created
	 * @param report - the standard report
	 */
	public void setReport(MRBReport reportp) {
		this.report = reportp;
		this.title.setText(report.getTitle());
		this.subTitle.setText(report.getSubTitle());
		this.reportMod.fireTableStructureChanged();
		this.reportMod.fireTableDataChanged();

		setColumnWidths(report.getColumnWidths());
	}
	/**
	 * Get the standard report for the viewer
	 * @return - the standard report
	 */
	public MRBReport getReport() {
		return this.report;
	}
	/**
	 * set the column widths for the viewer.  Allows the displayed width to be different than report column widths
	 * <p>
	 * Internal column widths are set using the FontMetrics of the chosen report font
	 * @param arrColumnWidthsp - an array of column widths
	 */
	private void setColumnWidths(int[] arrColumnWidthsp) {
		arrColumnWidths = arrColumnWidthsp;
		FontMetrics fm = this.reportTab
				.getFontMetrics(this.reportTab.getFont());

		TableColumnModel colModel = this.reportTab.getColumnModel();
		for (int i = 0; i < arrColumnWidths.length; i++) {
			String strCol = strData.substring(0, arrColumnWidths[i]);
			int maxColW = fm.stringWidth(String.valueOf(strCol) + 6);
			TableColumn col = colModel.getColumn(i);
			col.setPreferredWidth(maxColW);
		}
		this.reportTab.setAutoResizeMode(JTable.AUTO_RESIZE_OFF);
	}
	/**
	 * get the defined column widths
	 * @return - an array of widths
	 */
	private double[] getColumnWidths() {
		double[] dWidths = new double[arrColumnWidths.length];
		TableColumnModel colModel = this.reportTab.getColumnModel();
		for (int i = 0; i < arrColumnWidths.length; i++) {
			dWidths[i] = colModel.getColumn(i).getWidth();
		}
		return dWidths;
	}

	@Override
	public void preferencesUpdated() {
		updateFonts();
		validate();
	}
	/**
	 * Prints the current report using the MRBReportPrinter
	 */
	public void print() {
		MRBPrinter printer = new MRBPrinter();
		printer.print(new MRBReportPrinter(this, getColumnWidths()));

	}
	/**
	 * Closes the current viewer
	 */
	public void close() {
		setVisible(false);
		JFrame topFrame = (JFrame) SwingUtilities.getWindowAncestor(this);
		topFrame.dispose();
	}
	/**
	 * Resets the fonts to be used
	 */
	private void updateFonts() {
		fonts = MRBReportFonts.getScreenFonts();
		subTitle.setFont(fonts.getSubtitleFont());
		title.setFont(fonts.getTitleFont());
	}
	/**
	 * Internal class for the table used to display the report
	 * @author Mike Bray
	 *
	 */
	public class ReportTable extends JTable {

		ReportTableModel model;

		public ReportTable(ReportTableModel modelp) {
			super(modelp);
			model = modelp;
			setAutoResizeMode(JTable.AUTO_RESIZE_OFF);
			setCellSelectionEnabled(true);
			getTableHeader().setDefaultRenderer(new HeaderRender());
			if (report.getPopUp() != null) {
				menAction = new ActionListener() {
					@Override
					public void actionPerformed(ActionEvent aeEvent) {
						String strAction = aeEvent.getActionCommand();
						int iRow = ReportTable.this.getSelectedRow();
						int iCol = ReportTable.this.getSelectedColumn();
						report.getPopUp().actionPopup(strAction, iRow, iCol);
					}
				};
				menPopup = new JPopupMenu();
				addMouseListener(new MouseAdapter() {
					@Override
					public void mousePressed(MouseEvent me) {
						showPopup(me);
					}

					@Override
					public void mouseReleased(MouseEvent me) {
						showPopup(me);
					}
				});
			}
		}

		/*
		 * popup menu
		 */
		private void showPopup(MouseEvent me) {
			// is this event a popup trigger?
			if (me.isPopupTrigger()) {
				JTable tabSource = (JTable)me.getSource();
				Point p = me.getPoint();
				int iRow = tabSource.rowAtPoint(p);
				int iCol = tabSource.columnAtPoint(p);
				tabSource.changeSelection(iRow,  iCol,  false, false);
				if (iCol >= report.getRowHeaders()) {
					strMenuItems = report.getPopUp().getMenuItems(iRow, iCol);
					if (strMenuItems == null)
						return;
					for (Component objComp : menPopup.getComponents()) {
						if (objComp instanceof JMenuItem)
							menPopup.remove(objComp);
					}
					for (int i=0;i< strMenuItems.length;i++){
						JMenuItem miItem = new JMenuItem();
						miItem.setText(strMenuItems[i]);
						miItem.addActionListener(menAction);
						menPopup.add(miItem);
					}
					menPopup.show(me.getComponent(), me.getX(), me.getY());
				}
			}
		}
		@Override
		public Component prepareRenderer(TableCellRenderer renderer, int row,
				int column) {
			JTextField txtField = new JTextField();
			txtField.setText((String) getValueAt(row, column));
			MRBRecordRow rec = MRBReportViewer.this.report.getRow(row);
			switch (rec.getStyle(column)) {
			case STYLE_ITALIC:
				txtField.setFont(MRBReportViewer.this.fonts.getItalicFont());
				break;
			case STYLE_BOLD:
				txtField.setFont(MRBReportViewer.this.fonts.getBoldFont());
				break;
			default:
				txtField.setFont(MRBReportViewer.this.fonts.getNormalFont());
			}
			switch (rec.getAlignment(column)) {
			case ALIGN_LEFT:
				txtField.setHorizontalAlignment(JTextField.LEFT);
				break;
			case ALIGN_CENTER:
				txtField.setHorizontalAlignment(JTextField.CENTER);
				break;
			case ALIGN_RIGHT:
				txtField.setHorizontalAlignment(JTextField.RIGHT);
				break;
			default:
				txtField.setHorizontalAlignment(JTextField.LEFT);
			}
			switch (rec.getBorder(column)) {
			case BORDER_TOP:
				txtField.setBorder(BorderFactory.createMatteBorder(2, 0, 0, 0,
						Color.BLACK));
				break;
			case BORDER_BOTTOM:
				txtField.setBorder(BorderFactory.createMatteBorder(0, 0, 2, 0,
						Color.BLACK));
				break;
			case BORDER_BOTH:
				txtField.setBorder(BorderFactory.createMatteBorder(2, 0, 2, 0,
						Color.BLACK));
				break;
			case BORDER_TOP_HALF:
				txtField.setBorder(BorderFactory.createMatteBorder(1, 0, 0, 0,
						Color.BLACK));
				break;
			case BORDER_BOTTOM_HALF:
				txtField.setBorder(BorderFactory.createMatteBorder(0, 0, 1, 0,
						Color.BLACK));
				break;
			case BORDER_BOTH_HALF:
				txtField.setBorder(BorderFactory.createMatteBorder(1, 0, 1, 0,
						Color.BLACK));
				break;			default:
				txtField.setBorder(BorderFactory.createEmptyBorder());

			}
			txtField.setBackground(rec.getColor(column));
			txtField.setForeground(rec.getColorFG(column));
			return txtField;
		}

		private class HeaderRender extends JLabel implements TableCellRenderer {
			public HeaderRender() {
				setFont(MRBReportViewer.this.fonts.getHeaderFont());
				setBorder(BorderFactory.createMatteBorder(0, 0, 2, 0,
						Color.BLACK));
				setBackground(Color.WHITE);
			}

			@Override
			public Component getTableCellRendererComponent(JTable arg0,
					Object arg1, boolean arg2, boolean arg3, int arg4, int arg5) {
				setText(arg1.toString());
				Dimension dimHeader = getPreferredSize();
				dimHeader.height = 30;
				setPreferredSize(dimHeader);
				return this;
			}

		}
	}

	private class ReportTableModel extends AbstractTableModel {
		private ReportTableModel() {
		}

		@Override
		public int getRowCount() {
			return MRBReportViewer.this.report.getRowCount();
		}

		@Override
		public String getColumnName(int col) {
			return MRBReportViewer.this.report.getColumnName(col);
		}

		@Override
		public int getColumnCount() {
			return MRBReportViewer.this.report.getColumnCount();
		}

		@Override
		public Object getValueAt(int row, int col) {
			MRBRecordRow rec = MRBReportViewer.this.report.getRow(row);
			if (rec == null)
				return "???";
			return rec.getLabel(col);
		}
	}

	/*
	 * preferences
	 */
	private void setPreferences() {
		iSCREENWIDTH = preferences.getInt(MRBConstants.PROGRAMNAME+"."+MRBConstants.REPORTWIDTH,-1);
		iSCREENDEPTH = preferences.getInt(MRBConstants.PROGRAMNAME+"."+MRBConstants.REPORTDEPTH,-1);
		if (iSCREENWIDTH < 0 || iSCREENDEPTH < 0){
			iSCREENWIDTH = 800;
			iSCREENDEPTH = 500;
		}
	}

	private void updatePreferences(Dimension objDim) {
		preferences.put(MRBConstants.PROGRAMNAME+"."+MRBConstants.REPORTWIDTH, objDim.width);
		preferences.put(MRBConstants.PROGRAMNAME+"."+MRBConstants.REPORTDEPTH, objDim.height);
		setPreferences();
		preferences.isDirty();
		setPreferredSize(new Dimension(iSCREENWIDTH, iSCREENDEPTH));
		panButtons.setPreferredSize(new Dimension(iSCREENWIDTH, 50));
		panButtons.remove(lblName);
		Dimension dimName = this.lblName.getPreferredSize();
		Dimension dimClose = this.butClose.getPreferredSize();
		Dimension dimPrint = this.butPrint.getPreferredSize();
		panButtons.add(
				this.lblName,
				GridC.getc(0, 0)
						.west()
						.padx(iSCREENWIDTH - dimName.width - dimClose.width
								- dimPrint.width - 50));

		panHeader.setPreferredSize(new Dimension(iSCREENWIDTH,
				iSCREENDEPTH / 10));
		panViewer.setPreferredSize(new Dimension(iSCREENWIDTH, (int) Math
				.round(iSCREENDEPTH * .9)));
		this.revalidate();
	}

}

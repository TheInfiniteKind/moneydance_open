package com.moneydance.modules.features.budgetgen;

import java.awt.Dimension;
import java.awt.GridBagLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.ComponentEvent;
import java.awt.event.ComponentListener;
import java.util.List;
import java.util.prefs.Preferences;

import javax.swing.DefaultComboBoxModel;
import javax.swing.JButton;
import javax.swing.JCheckBox;
import javax.swing.JComboBox;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JViewport;
import javax.swing.SwingConstants;
import javax.swing.SwingUtilities;

import com.infinitekind.moneydance.model.DateRange;
import com.moneydance.awt.GridC;
import com.moneydance.modules.features.mrbutil.MRBPreferences2;
/*
 * Create Generate Window, contains BudgetLines that have an Amount
 */
public class GenerateWindow extends JPanel {
	private BudgetParameters objParams;
	private GenerateTable tabGen;
	private GenerateTableModel modGen;
	private GenerateTableHeader tabGenHead;
	private GenerateTableHeaderModel modGenHead;
	private List<BudgetLine> listBudgetLines;
	private int iType;
	private int iDisplayType;

	/*
	 * screen fields
	 */
	private JButton btnSave;
	private JButton btnCreate;
	private JButton btnClose;
	private JCheckBox cbDelete;
	private JComboBox<String> boxYears;
	private JPanel panTop;
	private JPanel panMid;
	private JPanel panBot;
	private JScrollPane spMid;

	private Preferences javaPref;
	private Preferences javaRoot;
	private MRBPreferences2 preferences;
	public int iGENSCREENWIDTH = Constants.GENSCREENWIDTH;
	public int iGENSCREENHEIGHT = Constants.GENSCREENHEIGHT;
	private int iGENTOPWIDTH;
	private int iGENMIDWIDTH;
	private int iGENBOTWIDTH;
	private int iGENTOPDEPTH;
	private int iGENMIDDEPTH;
	private int iGENBOTDEPTH;
	
	public GenerateWindow(int iYears, int iTypep, BudgetParameters objParamsp, int iDisplayTypep) {
		super();
		objParams = objParamsp;
		iType = iTypep;
		iDisplayType = iDisplayTypep;
		preferences = MRBPreferences2.getInstance();
		if (preferences == null) {
			System.err.println("MRB Generate Window failed to open - missing preferences");
			return;
		}
		/*
		 * first set up table model so it contains data
		 */
		modGen = new GenerateTableModel(objParams, iType);
		modGenHead = new GenerateTableHeaderModel();
		modGen.setYear(1);
		if (iDisplayType == Constants.GENERATE)
			objParams.generate(modGen.getPeriods());
		listBudgetLines = objParams.getLines();
		for ( BudgetLine objLine :listBudgetLines){
			long [] arrlTemp = objLine.getYear1Array();
			if (arrlTemp == null) {
				objLine.setNumPeriods(modGen.getPeriods().length);
			}
			modGen.AddLine(objLine);
			modGenHead.AddLine(objLine);
		}
		/*
		 * now create table
		 */
		tabGen = new GenerateTable(modGen, objParams);
		tabGenHead = new GenerateTableHeader(modGenHead);
		/*
		 * start of screen
		 */
		/*
		 * Top panel
		 */
		addComponentListener(new ComponentListener() {

			@Override
			public void componentResized(ComponentEvent arg0) {
				JPanel panScreen = (JPanel)arg0.getSource();
				Dimension objDimension = panScreen.getSize();
				updatePreferences (objDimension);
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
		setPreferences();  // set the screen sizes
		panTop = new JPanel(new GridBagLayout());
		panTop.setPreferredSize(new Dimension(iGENTOPWIDTH,iGENTOPDEPTH));
		/*
		 * year to display
		 */
		int x=0;
		int y=0;
		JLabel lblYearsl = new JLabel("Year to Display:");
		lblYearsl.setHorizontalAlignment(SwingConstants.RIGHT);
		panTop.add(lblYearsl, GridC.getc(x,y).west().insets(10,10,10,10));
		
		boxYears = new JComboBox<String>();
		boxYears.setModel(new DefaultComboBoxModel<String>(new String[] {"1", "2", "3"}));
		boxYears.setSelectedIndex(0);
		boxYears.setToolTipText("Select which year you want displayed");
		x++;
		panTop.add(boxYears,GridC.getc(x,y).west().insets(10,10,10,10));
		boxYears.addActionListener(new ActionListener () {
			@Override
			public void actionPerformed(ActionEvent e) {
				changeYears();
			}
	    });

		this.add(panTop);

		/*
		 * Middle panel - table
		 */

		panMid = new JPanel();
		spMid = new JScrollPane();
		spMid.getViewport().add(tabGen);
		int iHeaderWidth = Constants.GENCATPREFWIDTH+Constants.GENSELECTPREFWIDTH;
		int iDataWidth = iGENMIDWIDTH-iHeaderWidth-50;
		spMid.getViewport().setPreferredSize(new Dimension(iDataWidth,iGENMIDDEPTH-100));
		JViewport vpHeader = new JViewport();
		vpHeader.add(tabGenHead);
		vpHeader.setPreferredSize(new Dimension(iHeaderWidth,iGENMIDDEPTH-100));
		spMid.setRowHeader(vpHeader);
		spMid.setCorner(JScrollPane.UPPER_LEFT_CORNER, tabGenHead.getTableHeader());
		panMid.add(spMid);
		spMid.setPreferredSize(new Dimension(iGENMIDWIDTH,iGENMIDDEPTH));
		panMid.setPreferredSize(new Dimension(iGENMIDWIDTH,iGENMIDDEPTH));
		this.add(panMid);
		/*
		 * Bottom Panel - buttons
		 */
		panBot = new JPanel(new GridBagLayout());
		panBot.setPreferredSize(new Dimension(iGENBOTWIDTH,iGENBOTDEPTH));

		/*
		 * Button 1
		 */
		x=0;
		btnSave = new JButton("Save Parameters");
		btnSave.setToolTipText("Save the parameters.  You will be asked for a file name");
		btnSave.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				save();
			}
		});
		panBot.add(btnSave,GridC.getc(x,y).west().insets(15,15,15,15).fillx());

		/*
		 * Button 2
		 */
		x++;
		btnCreate = new JButton("Create Budget Items");
		btnCreate.setToolTipText("Create/Update the budget items within Moneydance");
		btnCreate.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				createItems();
			}
		});
		panBot.add(btnCreate,GridC.getc(x,y).west().insets(15,15,15,15).fillx());
		/*
		 * Check Box
		 */
		x++;
		cbDelete = new JCheckBox("Delete Current Values");
		cbDelete.setSelected(false);
		cbDelete.setToolTipText("If set and the new value is zero any existing Budget Item amount will be deleted");
		panBot.add(cbDelete,GridC.getc(x,y).west().insets(15,15,15,15).fillx());
		/*
		 * Button 3
		 */
		x++;
		btnClose = new JButton("Close");
		btnClose.setToolTipText("<html>Closes the window.  If the parameters have been changed<br> you will be asked if you wish to save them.<br> You will be asked for a file name</html>");
		btnClose.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				close();
			}
		});
		panBot.add(btnClose,GridC.getc(x,y).west().insets(15,15,15,15).fillx());
		
		this.add(panBot);
		panBot.setPreferredSize(new Dimension(iGENBOTWIDTH,iGENBOTDEPTH));
		this.setPreferredSize(new Dimension(iGENSCREENWIDTH,iGENSCREENHEIGHT));
	}
	public void close () {
		if (objParams.isDirty()) {
			JFrame fTemp = new JFrame();
			int iResult = JOptionPane
					.showConfirmDialog(fTemp,
							"The parameters have been changed.  Do you wish to save them?");
			if (iResult == JOptionPane.YES_OPTION) {
				objParams.saveParams();
			}
		}
		this.setVisible(false);
		JFrame topFrame = (JFrame) SwingUtilities.getWindowAncestor(this);
		topFrame.dispose();
	}
	/*
	 * Save selected lines
	 */
	private void createItems() {
		DateRange[] drPeriods = modGen.getPeriods();
		DateRange[] drYear = new DateRange[drPeriods.length];
		/*
		 * set date ranges based on year
		 */
		for (int i = 0;i<drYear.length;i++) {
			drYear[i] = new DateRange(drPeriods[i].getStartDateInt()+(boxYears.getSelectedIndex())*10000,
					drPeriods[i].getEndDateInt()+(boxYears.getSelectedIndex())*10000);
		}			
		/*
		 * Cycle through displayed lines - if Selected is true process Generated amount
		 * 
		 * Gen amt  Cur amt  Add  Update  Delete
		 *  != 0      = 0	  X
		 *  != 0 	 != 0           X
		 *  = 0      != 0                   X(a)
		 *  
		 *  
		 *  (a) only delete if flag set to delete
		 */
		for (int i = 0;i < modGen.getRowCount()/2;i++) {
			if ((boolean) modGenHead.getValueAt(i*2, 0)) {
				long[] arrGen = modGen.getGeneratedValues(i);
				long[] arrCur = modGen.getCurrentValues(i);
				for (int j=0;j<drYear.length;j++) {
					if (arrCur[j] == 0) {
						if (arrGen[j] != 0) {
								BudgetValuesWindow.budget.createItem(modGenHead.getCategoryObj(i),
										drYear[j],arrGen[j]);
								
						}
					}
					else
						if (arrGen[j] == 0) {
							if (cbDelete.isSelected())
								BudgetValuesWindow.budget.deleteItem(modGenHead.getCategoryObj(i),drYear[j]);
						}
						else {
								BudgetValuesWindow.budget.updateItem(modGenHead.getCategoryObj(i),
										drYear[j],arrGen[j]);
						}
				}
			}
		}
		BudgetValuesWindow.budget.reloadItems();
		modGen.reloadCurrent();
		modGen.fireTableDataChanged();

		
	}
	private void save() {
		objParams.saveParams();
	}
	private void changeYears() {
		modGen.setYear(boxYears.getSelectedIndex()+1);
		for (int i = 0; i < modGen.getColumnCount(); i++) {
			  String name = modGen.getColumnName(i);
			  int viewIdx = tabGen.convertColumnIndexToView(i);
			  tabGen.getColumnModel().getColumn(viewIdx).setHeaderValue(name);
			}
		modGen.fireTableDataChanged();
		panMid.revalidate();
	}
	/*
	 * preferences
	 */
	private void setPreferences() {
		String strType = iType==1? "exp" : "inc";
		iGENSCREENWIDTH = preferences.getInt(Constants.PROGRAMNAME+"."+Constants.GENWIDTHKEY+strType,-1);
		iGENSCREENHEIGHT = preferences.getInt(Constants.PROGRAMNAME+"."+Constants.GENDEPTHKEY+strType,-1);
		if (iGENSCREENWIDTH < 0 || iGENSCREENHEIGHT < 0) {
			javaRoot = Preferences.userRoot();
			javaPref = javaRoot.node("com.moneydance.modules.features.budgetgen.budgetvalueswindow");
			iGENSCREENWIDTH = javaPref.getInt(Constants.GENWIDTHKEY+strType, Constants.GENSCREENWIDTH);
			iGENSCREENHEIGHT = javaPref.getInt(Constants.GENDEPTHKEY+strType, Constants.GENSCREENHEIGHT);
		}
		iGENBOTDEPTH = 100;
		iGENTOPDEPTH = 50;
		iGENTOPWIDTH = iGENSCREENWIDTH-50;
		iGENBOTWIDTH = iGENSCREENWIDTH-50;
		iGENMIDWIDTH = iGENSCREENWIDTH-50;
		iGENMIDDEPTH = iGENSCREENHEIGHT - iGENBOTDEPTH- 50- iGENTOPDEPTH;
	}
	private void updatePreferences(Dimension objDim){
		String strType = iType==1? "exp" : "inc";
		preferences.put(Constants.PROGRAMNAME+"."+Constants.GENWIDTHKEY+strType,objDim.width);
		preferences.put(Constants.PROGRAMNAME+"."+Constants.GENDEPTHKEY+strType,objDim.height);
		setPreferences();
		preferences.isDirty();
		panTop.setPreferredSize(new Dimension(iGENTOPWIDTH,iGENTOPDEPTH));
		spMid.setPreferredSize(new Dimension(iGENMIDWIDTH,iGENMIDDEPTH));
		panMid.setPreferredSize(new Dimension(iGENMIDWIDTH,iGENMIDDEPTH));
		panBot.setPreferredSize(new Dimension(iGENBOTWIDTH,iGENBOTDEPTH));
		this.revalidate();
	}
}

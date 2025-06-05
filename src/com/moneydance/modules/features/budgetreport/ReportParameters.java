package com.moneydance.modules.features.budgetreport;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;

import com.infinitekind.moneydance.model.AccountBook;
import com.moneydance.apps.md.controller.FeatureModuleContext;



public class ReportParameters implements java.io.Serializable {

	/*
	 * Static and transient fields are not stored 
	 */
	private static final long serialVersionUID = 1L;
	private transient AccountBook abCurAcctBook;
	private transient File fiCurFolder;
	private transient FileInputStream fiCurInFile;
	private transient FileOutputStream fiCurOutFile;
	private transient String strFileName;
   /*
     * The following fields are stored
     */

	private String strParameterFile;
	private String strBudget;
	/*
	 * Constructor
	 */
	public ReportParameters(FeatureModuleContext context)  {

		/*
		 * determine if file already exists
		 */
		abCurAcctBook = context.getCurrentAccountBook();
		fiCurFolder = abCurAcctBook.getRootFolder();
		strFileName = fiCurFolder.getAbsolutePath()+"\\BudgetReport.parms";

		try {
			fiCurInFile = new FileInputStream(strFileName);
			ObjectInputStream ois = new ObjectInputStream(fiCurInFile);
			/*
			 * file exists, copy temporary object to this object
			 */
			ReportParameters objTemp = (ReportParameters) ois.readObject();
			this.strParameterFile = objTemp.strParameterFile;
			this.strBudget = objTemp.strBudget;
			fiCurInFile.close();
		}
		catch (IOException | ClassNotFoundException ioException) {
			/*
			 * create the file
			 */
			strParameterFile = "";
			strBudget = "";
			try {
				fiCurOutFile = new FileOutputStream(strFileName);
				ObjectOutputStream oos = new ObjectOutputStream(fiCurOutFile);
				oos.writeObject(this);
				fiCurOutFile.close();
			}
			catch(IOException i)
			{
				i.printStackTrace();
			}
		}
	}

	/*
	 * gets
	 * 
	 * Parameter File
	 */
	public String getFile() {
		return strParameterFile;
	}
	/*
	 * Budget Name
	 */
	public String getBudget() {
		return strBudget;
	}

	/*
	 * sets
	 * 
	 * Parameter File
	 */
	public void setFile(String strParameterFilep) {
		strParameterFile = strParameterFilep;
		return;
	}
	/*
	 * Budget
	 */
	public void setBudget (String strBudgetp){
		strBudget = strBudgetp;
	}

	/*
	 * Save the parameters into the specified file
	 */
	public void saveParams() {
		try {
			fiCurOutFile = new FileOutputStream(strFileName);
			ObjectOutputStream oos = new ObjectOutputStream(fiCurOutFile);
			oos.writeObject(this);
			oos.close();
			fiCurOutFile.close();
		}
		catch(IOException i)
		{
			i.printStackTrace();
		}
	
	}
}

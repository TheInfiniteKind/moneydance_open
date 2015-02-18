package com.moneydance.modules.features.moneyPie;

import com.moneydance.admin.KeyAdmin;
import java.io.FileInputStream;
import java.io.File;
import java.io.FileNotFoundException;

public class SignMxt {

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		// TODO Auto-generated method stub
		try
		{
			FileInputStream fis = new FileInputStream(new File("sign_pw.txt"));
			System.setIn(fis);
			KeyAdmin.main(args);
		}
		catch (FileNotFoundException fnfe)
		{
			System.out.println(fnfe.getMessage());
		}
		catch (Exception ex)
		{
			System.out.println(ex.getMessage());
		}
	}

}

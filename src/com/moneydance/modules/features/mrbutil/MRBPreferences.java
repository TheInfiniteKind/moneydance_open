package com.moneydance.modules.features.mrbutil;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.infinitekind.moneydance.model.AccountBook;
import com.moneydance.apps.md.controller.FeatureModuleContext;

/**
 * 
 * @author Mike Bray
 * @version 1.0
 * 
 *          Stores and retrieves key/value pairs used to manage user preferences
 */

public class MRBPreferences implements java.io.Serializable {
	private transient static MRBPreferences objPref = null;
	private transient FeatureModuleContext conCurrentCon;
	private transient AccountBook abCurAcctBook;
	private transient String strFileName = MRBConstants.PARAMETERFILE;
	private transient File fiCurFolder;
	private transient FileInputStream fiCurInFile;
	private transient FileOutputStream fiCurOutFile;
	private transient String strFullFileName;
	private boolean bDirty = false;
	/*
	 * These fields are saved
	 */
	public Map<String, String> mapData;

	/**
	 * Creates the object that is used for all references. This should only be
	 * called internally. Use loadPreferences.
	 * 
	 * @param contextp
	 */

	public MRBPreferences(FeatureModuleContext contextp) {
		conCurrentCon = contextp;
		abCurAcctBook = conCurrentCon.getCurrentAccountBook();
		fiCurFolder = abCurAcctBook.getRootFolder();
		strFullFileName = fiCurFolder.getAbsolutePath() + "/" + strFileName;

		try {
			fiCurInFile = new FileInputStream(strFullFileName);
			ObjectInputStream ois = new ObjectInputStream(fiCurInFile);
			/*
			 * file exists, copy temporary object to this object
			 */
			MRBPreferences objTemp = (MRBPreferences) ois.readObject();
			this.mapData = objTemp.mapData;
			fiCurInFile.close();
		} catch (IOException | ClassNotFoundException ioException) {
			/*
			 * file does not exist
			 * if MacOS or Unix try to use '\' in file name
			 */
			Boolean fileLoaded = false;
			if (MRBPlatform.isOSX() || MRBPlatform.isUnix() || MRBPlatform.isFreeBSD()) {
				if (loadOldFile())
					fileLoaded = true;
			}
			if (!fileLoaded) {
				mapData = new HashMap<>();
				/*
				 * create the file
				 */
				try {
					fiCurOutFile = new FileOutputStream(strFullFileName);
					ObjectOutputStream oos = new ObjectOutputStream(fiCurOutFile);
					oos.writeObject(this);
					fiCurOutFile.close();
				} catch (IOException i) {
					i.printStackTrace();
				}
			}
		}
		bDirty= true;
		isDirty();
	}
	private boolean loadOldFile() {
		strFullFileName = fiCurFolder.getAbsolutePath() + "\\" + strFileName;

		try {
			fiCurInFile = new FileInputStream(strFullFileName);
			ObjectInputStream ois = new ObjectInputStream(fiCurInFile);
			/*
			 * file exists, copy temporary object to this object
			 */
			MRBPreferences objTemp = (MRBPreferences) ois.readObject();
			this.mapData = objTemp.mapData;
			fiCurInFile.close();
		} catch (IOException | ClassNotFoundException ioException) {
			return false;
		}
		return true;
	}
	/**
	 * loads the preferences by calling the constructor. The object reference is
	 * stored to be returned by getInstance().
	 * 
	 * @param objContext
	 */
	public static void loadPreferences(FeatureModuleContext objContext) {
		if (objPref == null)
			objPref = new MRBPreferences(objContext);
	}

	/**
	 * Get an instance of the preferences
	 */
	public static MRBPreferences getInstance() {
		return objPref;
	}
	
	/**
	 * destroy current environment
	 */
	public static void forgetInstance() {
		objPref = null;
	}

	/**
	 * Stores a string pair in the preferences store. If the value is null, the
	 * existing pair is removed
	 * 
	 * This method is used by all other put methods. Other methods translate the
	 * value to a string
	 * 
	 * @param strKey
	 *            - the key for the pair
	 * @param value
	 *            - the value for the pair. If null, item is removed
	 * @return - the value added/removed
	 */
	public String put(String strKey, String value) {
		bDirty = true;
		if (value == null) {
			return mapData.remove(strKey);
		}
		String V=mapData.put(strKey, value);
		return V;
	}

	public void put(String strKey, Object value) {
		put(strKey, String.valueOf(value));
	}

	public void put(String strKey, long value) {
		put(strKey, String.valueOf(value));
	}

	public void put(String strKey, double value) {
		put(strKey, String.valueOf(value));
	}

	public void put(String strKey, int value) {
		put(strKey, String.valueOf(value));
	}

	public void put(String strKey, int[] value) {
		if (value == null) {
			bDirty = true;
			mapData.remove(strKey);
		} else {
			StringBuilder sb = new StringBuilder();
			for (int i : value) {
				if (sb.length() != 0)
					sb.append(',');
				sb.append(i);
			}
			put(strKey, sb.toString());
		}
	}

	public void put(String strKey, boolean value) {
		put(strKey, value ? "1" : "0");
	}

	/**
	 * Return the value for the given string
	 * 
	 * @param strKey
	 *            - the key
	 * @return - value object
	 */
	public String get(String strKey) {
		return mapData.get(strKey);
	}

	/**
	 * Returns the string value for the given key. If the key does not exist the
	 * default value is returned
	 * 
	 * @param strKey
	 *            - the key
	 * @param strDefault
	 *            - the default value if not present
	 * @return - the value
	 */
	public String getString(String strKey, String strDefault) {
		if (get(strKey) == null)
			return strDefault;
		return get(strKey);
	}

	/**
	 * Returns the Lists of string values for the given key.
	 * 
	 * @param strKey
	 *            - the key
	 * @return - the List of values
	 */

	public List<String> getStringList(String strKey) {
		int i = 0;
		ArrayList<String> arrStrings = new ArrayList<>();
		strKey = new StringBuilder().append(strKey).append(".").toString();
		while (true) {
			String val = getString(new StringBuilder().append(strKey).append(i)
					.toString(), null);
			if (val == null)
				break;
			arrStrings.add(val);
			i++;
		}
		return arrStrings;
	}

	/**
	 * Returns the integer value for the given key. If the key does not exist
	 * the default value is returned
	 * 
	 * @param strKey
	 *            - the key
	 * @param int iDefault - the default value if not present
	 * @return - the value
	 */

	public int getInt(String strKey, int iDefault) {
		String result = get(strKey);
		if (result == null)
			return iDefault;
		try {
			return Integer.parseInt(result);
		} catch (Throwable t) {
		}
		return iDefault;
	}

	/**
	 * Returns the Array of integer values for the given key.
	 * 
	 * @param strKey
	 *            - the key
	 * @return - the Array of values
	 */

	public int[] getIntArray(String strKey) {
		String result = get(strKey);
		if (result == null)
			return new int[0];
		int[] fields = new int[MRBUtils.countFields(result, ',')];
		for (int i = 0; i < fields.length; i++) {
			try {
				fields[i] = Integer.parseInt(MRBUtils
						.fieldIndex(result, ',', i));
			} catch (Throwable t) {
				fields[i] = 0;
			}
		}
		return fields;
	}

	/**
	 * Returns the long value for the given key. If the key does not exist the
	 * default value is returned
	 * 
	 * @param strKey
	 *            - the key
	 * @param long lDefault - the default value if not present
	 * @return - the value
	 */

	public long getLong(String strKey, long lDefault) {
		String result = get(strKey);
		if (result == null)
			return lDefault;
		try {
			return Long.parseLong(result);
		} catch (Throwable t) {
		}
		return lDefault;
	}

	/**
	 * Returns the double value for the given key. If the key does not exist the
	 * default value is returned
	 * 
	 * @param strKey
	 *            - the key
	 * @param double dDefault - the default value if not present
	 * @return - the value
	 */
	public double getDouble(String strKey, double dDefault) {
		String result = get(strKey);
		if (result == null)
			return dDefault;
		try {
			return Double.parseDouble(result);
		} catch (Throwable t) {
		}
		return dDefault;
	}

	/**
	 * Returns the boolean value for the given key. If the key does not exist
	 * the default value is returned
	 * 
	 * @param strKey
	 *            - the key
	 * @param boolean bDefault - the default value if not present
	 * @return - the value
	 */

	public boolean getBoolean(String strKey, boolean bDefault) {
		String result = get(strKey);
		if (result == null)
			return bDefault;
		result = result.trim();
		if (result.length() <= 0)
			return bDefault;
		switch (result.charAt(0)) {
		case '1':
		case 't':
		case 'y':
			return true;
		case '0':
		case 'f':
		case 'n':
			return false;
		}
		return bDefault;
	}

	/**
	 * Check to see if parameters have been changed. If so save. It is up to the
	 * extension to control when preferences are saved. It is not ideal to do it
	 * every time an individual value is updated.
	 */
	public void isDirty() {
		if (!bDirty)
			return;
		try {
			strFullFileName = fiCurFolder.getAbsolutePath() + "/" + strFileName;
			fiCurOutFile = new FileOutputStream(strFullFileName);
			ObjectOutputStream oos = new ObjectOutputStream(fiCurOutFile);
			oos.writeObject(this);
			oos.close();
			fiCurOutFile.close();
		} catch (IOException i) {
			i.printStackTrace();
		}
		/*
		 * clear dirty flags
		 */
		bDirty = false;

	}

}

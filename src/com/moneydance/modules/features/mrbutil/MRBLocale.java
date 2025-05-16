package com.moneydance.modules.features.mrbutil;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.UnsupportedEncodingException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

import com.moneydance.apps.md.controller.UserPreferences;

/**
 * 
 * @author Mike Bray
 * @version 1.0
 * 
 *          Stores and retrieves key/value pairs used to manage user preferences
 */

public class MRBLocale{
	private  String fullFileName;
	private  UserPreferences userPref;
	private  Locale locale;
	private InputStream inputStream;
	private InputStreamReader reader;
	private Map<String, String> mapData;

	/**
	 * Creates the object that is used for all locale dependent strings. This should only be
	 * called internally.
	 * 
	 * @param contextp
	 */

	public MRBLocale(Object obj,String strFileName) {
		userPref = UserPreferences.getInstance();
		locale = userPref.getLocale();	
		mapData = new HashMap<String,String>();
		fullFileName = strFileName;
		if (locale != null && locale.getLanguage()!= "en")
			fullFileName = fullFileName.replace("_en.", "_"+locale.getLanguage()+".");
		try {
			reader = getFile(obj,fullFileName, MRBConstants.LOCALEFILE);
		}
			catch (MRBLocaleException e) {
			
		}
		if (reader !=null)
			try {

				readCoding();
			}
		catch (MRBLocaleException e) {
			
		}
	}
	public InputStreamReader getFile(Object obj,String strFileName,String strDefaultFileName) {
		inputStream = obj.getClass().getResourceAsStream(strFileName);
		InputStreamReader objRdr = null;
		if (inputStream == null) {
			inputStream = obj.getClass().getResourceAsStream(strDefaultFileName);
			if (inputStream == null) {
				return null;
			}
		}
		try {
			objRdr = new InputStreamReader(inputStream, "UTF8");
			}
		catch (UnsupportedEncodingException e) {
			
		}
		return objRdr;
	}
	private void readCoding () throws MRBLocaleException {
		BufferedReader buffer = new BufferedReader(reader);
		String line;
		try {
			line = buffer.readLine();
			if (!line.substring(0, 1).equals("{"))
				throw new MRBLocaleException(new Throwable("Missing Open Bracket"));
		}
		catch (IOException e) {
			throw new MRBLocaleException(new Throwable("File I/O Error"));			
		}
		try {
			line = buffer.readLine();
		}
		catch (IOException e) {
			throw new MRBLocaleException(new Throwable("File I/O Error"));			
		}	
		String key;
		String valueStr;
		while(line != null){
			int iChar =line.indexOf('}');
			if ( iChar >= 0)
				break;
			iChar =line.indexOf('"');
			key=line.substring(iChar+1);
			iChar =key.indexOf('"');
			if (iChar >= 0) {
				valueStr = key.substring(iChar+1);
				key = key.substring(0,iChar);
				iChar = valueStr.indexOf('=');
				if (iChar >= 0) {
					valueStr = valueStr.substring(iChar+1);
					// valueStr contains rest of line, find first "
					iChar = valueStr.indexOf('"');
					if (iChar >= 0){ 
						valueStr = valueStr.substring(iChar+1);
						// first " found, valueStr contains rest of line
						// now search for \
						int i =0;
						String tempStr = "";
						char currentChar;
						while (i<valueStr.length()) {
							currentChar = valueStr.charAt(i);
							if (currentChar == '"') {
								mapData.put(key, tempStr);
								break;
							}
							if (currentChar == '\\') {
								i++;
								currentChar = valueStr.charAt(i);
							}
							tempStr += currentChar;
							i++;
						}
					}
				}
			}
			try {
				line = buffer.readLine();
			}
			catch (IOException e) {
				throw new MRBLocaleException(new Throwable("File I/O Error"));			
			}	
		}
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
			return "ERROR"+strDefault;
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
		ArrayList<String> arrStrings = new ArrayList<String>();
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


}

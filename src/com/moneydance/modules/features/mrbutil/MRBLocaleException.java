package com.moneydance.modules.features.mrbutil;
/**
 * Raised when an inconsistency in the Moneydance file is discovered.  Data needed does not exist
 * @author Mike Bray
 *
 */
public class MRBLocaleException extends RuntimeException {
	/**
	 * Constructor - 
	 * @param objCause - contains a string describing the error
	 */
	public MRBLocaleException (Throwable objCause) {
		super (objCause);
	}

}

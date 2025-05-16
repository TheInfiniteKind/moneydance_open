package com.moneydance.modules.features.mrbutil;

public class MRBUtils {
	public static final int countFields(String strTarget, char chDelimiter) {
		if (strTarget == null)
			return 0;
		int iCount = 0;
		int iIndex = -1;
		do {
			iCount++;
			iIndex = strTarget.indexOf(chDelimiter, iIndex + 1);
		} while (iIndex >= 0);
		return iCount;
	}

	public static final String fieldIndex(String strTarget, char chDelimiter,int iIndex) {
		int iCrntField = 0;
		int iLastIx = 0;
		int iTargetLen = strTarget.length();
		do {
			if (iCrntField == iIndex) {
				int iThisTemp = strTarget.indexOf(chDelimiter, iLastIx);
				if (iThisTemp >= 0) {
					return strTarget.substring(iLastIx, iThisTemp);
				}
				return strTarget.substring(iLastIx, iTargetLen);
			}
			int iThisIndex = strTarget.indexOf(chDelimiter, iLastIx);
			if (iThisIndex < 0) {
				return "";
			}
			iCrntField++;
			iLastIx = iThisIndex + 1;
		}
		while (iLastIx < iTargetLen);
		return "";
	}
}

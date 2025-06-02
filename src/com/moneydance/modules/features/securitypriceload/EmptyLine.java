package com.moneydance.modules.features.securitypriceload;

public class EmptyLine extends Exception {
	String str1;
	   /* Constructor of custom exception class
	    * here I am copying the message that we are passing while
	    * throwing the exception to a string and then displaying 
	    * that string along with the message.
	    */
	   EmptyLine(String str2) {
		str1=str2;
	   }
	   @Override
	public String toString(){ 
		return ("EmptyLine Found "+str1) ;
	   }
}

package com.moneydance.modules.features.reportwriter;


import java.util.Optional;

import javax.swing.JOptionPane;

public abstract class OptionMessage {
	
	public static void displayMessage(String message) {
		displayMessageSwing(message);
	}
	private static void displayMessageSwing(String message) {
		JOptionPane.showMessageDialog(null, message);
	}
	public static void displayErrorMessage(String message) {
		displayErrorMessageSwing(message);
	}
	private static void displayErrorMessageSwing(String message) {
		JOptionPane.showMessageDialog(null, message,"Report Writer",JOptionPane.ERROR_MESSAGE);
	}
	public static boolean yesnoMessage(String message) {
		return yesnoMessageSwing(message);

	}

	private static boolean yesnoMessageSwing(String message) {
        if (JOptionPane.showConfirmDialog(null,message,"Confirm", 
	            JOptionPane.YES_NO_OPTION,
	            JOptionPane.QUESTION_MESSAGE) == JOptionPane.YES_OPTION){
        	return true;
        }
        return false;
	}
	public static boolean okMessage(String message) {
		return okMessageSwing(message);
	}
	private static boolean okMessageSwing(String message) {
        if (JOptionPane.showConfirmDialog(null,message,"Confirm", 
	            JOptionPane.OK_OPTION,
	            JOptionPane.QUESTION_MESSAGE) == JOptionPane.OK_OPTION){
        	return true;
        }
        return false;
	}
	public static String inputMessage(String message) {
		return inputMessageSwing(message);

	}
	private static String inputMessageSwing(String message) {
        return JOptionPane.showInputDialog(null,message);
	}
	public static void customBtnMessageSwing(String message,String buttonMsg, BtnCallBack btnAction) {
		Object[] options = {"OK",buttonMsg};
		int n = JOptionPane.showOptionDialog(null, message,null, JOptionPane.YES_NO_OPTION,JOptionPane.ERROR_MESSAGE,null,options,options[0]);
		if (n==1)
			btnAction.callbackAction();
	}
}
abstract interface BtnCallBack {
	void callbackAction();
}

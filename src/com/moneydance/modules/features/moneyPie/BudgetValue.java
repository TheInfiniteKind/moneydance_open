package com.moneydance.modules.features.moneyPie;

import java.lang.NumberFormatException;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.text.DecimalFormat;
import java.text.DecimalFormatSymbols;
import com.infinitekind.moneydance.model.*;

public class BudgetValue extends Object {
	private double  value;
	private Account associatedAccount;
	private BudgetData data;
	private boolean isNoEntry = false;
	
	BudgetValue(BudgetData data, BudgetValue bValue){
		this.data = data;
		this.setValue(bValue.doubleValue());
	}
	
	BudgetValue(BudgetData data, double value){
		this.data = data;
		this.setValue(value);
	}
	
	BudgetValue(BudgetData data, int iValue){
		this.data = data;
		this.setValue(iValue);
	}
	
	BudgetValue(BudgetData data, long lValue){
		this.data = data;
		this.setValue(lValue);
	}
	
	BudgetValue(BudgetData data, Double dValue){
		this.data = data;
		this.setValue(dValue);
	}
	
	BudgetValue(BudgetData data, String sValue){
		this.data = data;
		this.setValue(sValue);
	}
	
	public void setIsNoEntry(boolean nEntry){
		this.isNoEntry = nEntry;
	}
	
	public boolean isNoEntry(){
		return this.isNoEntry;
	}
	
	public boolean isNegative(){
		if(this.value < 0){
			return true;
		} else {
			return false;
		}
	}
	
	public boolean isEqual(double cValue){
		if(this.value == cValue){
			return true;
		} else {
			return false;
		}
	}
	
	public boolean isEqual(BudgetValue cValue){
		if(this.value == cValue.doubleValue()){
			return true;
		} else {
			return false;
		}
	}
	
	public double diff(BudgetValue bValue){
		return this.value - bValue.doubleValue();
	}
	
	public void setAccount(Account account){
		this.associatedAccount = account;
	}
	
	public void setValue(BudgetValue bValue){
		this.value = bValue.doubleValue();
	}
	
    public void setValue(double value){
		this.value = value;
	}

	public void setValue(int iValue){
		this.setValue((double) iValue);
	}
	
	public void setValue(Double dValue){
		if(dValue == null){
			dValue = new Double(0);
			this.isNoEntry = true;
		}
		this.value = dValue.doubleValue();
	}
	
	public boolean isDoubleValue( String input )  
	{  
	   try  
	   {   
	      Double.parseDouble(input);
	      return true;  
	   }  
	   catch( NumberFormatException e )  
	   {  
	      return false;  
	   }  
	}  
	
	public void setValue(String sValue){
		this.setValue(sValue, false);
		
	}
	
	public void setValue(String sValue, boolean verbose){
		if(sValue == null) {
			sValue = "0";
			this.isNoEntry = true;
		}

		UnsafeAccessor ua = new UnsafeAccessor(this.data.extension.getUnprotectedContext());
		char dec = ua.getDecimalChar();
		
		if(verbose) System.err.println("DEBUG 1: " + sValue);
		if(dec == '.'){
			//American
			sValue = sValue.replace( "," , "");
		} else {
			//UK
			sValue = sValue.replace( "." , "");
			sValue = sValue.replace( "," , ".");
		}
		if(verbose) System.err.println("DEBUG 2: " + sValue);
		
		
		sValue = sValue.replace( " " , "");
		if(data != null){
			sValue = sValue.replace( data.getRoot().getCurrencyType().getPrefix() , "");
		}
		
		if(sValue.length() == 0){
			this.setValue(0);
			this.isNoEntry = true;
		} else {
			if(isDoubleValue(sValue)){
				Double dValue = new Double(sValue);
				this.value = dValue.doubleValue();
			} else {
				this.value = 0;
			}
			
		}
		
	}
	
	private double getValue(){
		if(associatedAccount != null){
		  BigDecimal B_Value = BigDecimal.valueOf(this.value);
		  BigDecimal B_Rate  = BigDecimal.valueOf(associatedAccount.getCurrencyType().getRawRate());
		  BigDecimal B_Amount = B_Value.divide(B_Rate, 2, RoundingMode.HALF_UP);
		  return B_Amount.doubleValue();
		} else {
			return this.value;
		}
		
	}
	
	public Double DoubleValue(){
		return new Double(this.doubleValue());
	}
	
	public double doubleValue(){
		return this.getValue();
	}
	
	public long longValue(){
		return this.DoubleValue().longValue();
	}
	
	public void negate(){
		this.setValue(- this.value);
	}
	
	public BudgetValue negateValue(){
		this.negate();
		return this;
	}
	
	public BudgetValue sign(boolean negative){
		  if(this.value == 0) return this;

		  if(negative){
			  return this.negateValue();
		  } else {
			  return this;
		  }
	}
	
	public String rawString(){		
		DecimalFormat nf = (DecimalFormat) DecimalFormat.getInstance();
		DecimalFormatSymbols custom = new DecimalFormatSymbols();
		
		UnsafeAccessor ua = new UnsafeAccessor(this.data.extension.getUnprotectedContext());
		char dec = ua.getDecimalChar();
		
		if(dec == '.'){
			//American
			custom.setDecimalSeparator('.');
			custom.setGroupingSeparator(','); 
		} else {
			//UK
			custom.setDecimalSeparator(',');
			custom.setGroupingSeparator('.'); 
		}

		nf.setDecimalFormatSymbols(custom);

        nf.setGroupingUsed(true);
        nf.setMinimumFractionDigits(2);
        nf.setMaximumFractionDigits(2);
        
        return nf.format(this.getValue());
	}
	
	public String toString(){
        String prefix = "";
        if(data != null){
        	prefix = data.getRoot().getCurrencyType().getPrefix();
        }
        return prefix + " " + this.rawString();
	}
	
	public String dString(){
		
		DecimalFormat nf = (DecimalFormat) DecimalFormat.getInstance();
		DecimalFormatSymbols custom = new DecimalFormatSymbols();
		
		UnsafeAccessor ua = new UnsafeAccessor(this.data.extension.getUnprotectedContext());
		char dec = ua.getDecimalChar();
		
		if(dec == '.'){
			//American
			custom.setDecimalSeparator('.');
		} else {
			//UK
			custom.setDecimalSeparator(',');
		}

		nf.setDecimalFormatSymbols(custom);

        nf.setGroupingUsed(false);
        nf.setMinimumFractionDigits(2);
        nf.setMaximumFractionDigits(2);
        
        return nf.format(this.getValue());
	}
	
	public BudgetValue dFormat(){
		this.setValue(this.dString());
		return this;
	}
	
	public Double toDouble(){
		Double dValue = new Double(this.getValue());
		return dValue;
	}
	
	public void add(double aValue){
		this.setValue(this.value + aValue);
	}
	
	public void minus(double mValue){
		this.setValue(this.value - mValue);
	}
	
	public void multiply(double mValue){
		BigDecimal B_value  = BigDecimal.valueOf(this.value);
  	    BigDecimal B_mValue = BigDecimal.valueOf(mValue);
  	    BigDecimal B_Amount = B_value.multiply(B_mValue);
  	  
		this.setValue(B_Amount.doubleValue());
	}
	
	public void divide(double dValue){
		this.setValue(this.value / dValue);
	}
	
	public void add(BudgetValue bValue){
		this.add(bValue.doubleValue());
	}
	
	public void minus(BudgetValue bValue){
		this.minus(bValue.doubleValue());
	}
	
	public void multiply(BudgetValue bValue){
		this.multiply(bValue.doubleValue());
	}
	
	public void divide(BudgetValue bValue){
		this.divide(bValue.doubleValue());
	}
	
}

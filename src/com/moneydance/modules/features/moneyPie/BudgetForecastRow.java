package com.moneydance.modules.features.moneyPie;

public class BudgetForecastRow implements Comparable<BudgetForecastRow> {
	public String      type;
	public String      date;
	public String      description;
	public String      amount;
	
	public int compareTo(BudgetForecastRow d){
	    return (this.date).compareTo(d.date);
	}
	
	public int compare(BudgetForecastRow d, BudgetForecastRow d1){
		return 1;
	  //return d.date - d1.date;
	}
}

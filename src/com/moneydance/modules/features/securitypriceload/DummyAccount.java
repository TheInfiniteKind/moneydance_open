package  com.moneydance.modules.features.securitypriceload;

import com.infinitekind.moneydance.model.Account;
import com.infinitekind.moneydance.model.CurrencyType;

public class DummyAccount {
	private String accountName;
	private Account acct;
	private CurrencyType currencyType;
	private CurrencyType relativeCurrency;
	private Boolean differentCur;
	public  DummyAccount (){
		
	}
	public String getAccountName (){
		return accountName;
	}
	public CurrencyType getCurrencyType() {
		return currencyType;
	}
	public CurrencyType getRelativeCurrencyType() {
		return relativeCurrency;
	}
	public Boolean getDifferentCur(){
		return differentCur;
	}
	public Account getAccount(){
		return acct;
	}
	public void setAccountName (String accountName){
		this.accountName = accountName;
	}
	public void setCurrencyType (CurrencyType currencyType){
		this.currencyType = currencyType;
		relativeCurrency = getRelativeCurrency(currencyType);
		if (relativeCurrency == null || Main.context.getCurrentAccountBook().getCurrencies().getBaseType()== relativeCurrency)
			differentCur = false;
		else
			differentCur = true;
	}
	public void setAccount (Account acct){
		this.acct = acct;
	}
	static CurrencyType getRelativeCurrency(CurrencyType curr) {
	  String relCurrID = curr.getParameter(CurrencyType.TAG_RELATIVE_TO_CURR);
	  return relCurrID == null ? null : curr.getBook().getCurrencies().getCurrencyByIDString(relCurrID);
    }
}

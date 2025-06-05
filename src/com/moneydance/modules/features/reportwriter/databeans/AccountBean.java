/*
 * Copyright (c) 2021, Michael Bray.  All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 *   - Redistributions of source code must retain the above copyright
 *     notice, this list of conditions and the following disclaimer.
 *
 *   - Redistributions in binary form must reproduce the above copyright
 *     notice, this list of conditions and the following disclaimer in the
 *     documentation and/or other materials provided with the distribution.
 *
 *   - The name of the author may not used to endorse or promote products derived
 *     from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
 * IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 * THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 * PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 * LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 * 
 */
package com.moneydance.modules.features.reportwriter.databeans;

import com.infinitekind.moneydance.model.Account;
import com.infinitekind.moneydance.model.Account.AccountType;
import com.moneydance.modules.features.reportwriter.Constants;
import com.moneydance.modules.features.reportwriter.Utilities;
import com.moneydance.modules.features.reportwriter.databeans.BeanAnnotations.BEANFIELDTYPE;
import com.moneydance.modules.features.reportwriter.databeans.BeanAnnotations.ColumnName;
import com.moneydance.modules.features.reportwriter.databeans.BeanAnnotations.ColumnTitle;
import com.moneydance.modules.features.reportwriter.databeans.BeanAnnotations.FieldType;

public class AccountBean extends DataBean {
	@ColumnName("AccountID")
	@ColumnTitle("Account ID")
	@FieldType(BEANFIELDTYPE.STRING)
	public String accountId; // ok
	@ColumnName("AccountName")
	@ColumnTitle("Account Name")
	@FieldType(BEANFIELDTYPE.STRING)
	public String accountName; // ok
	@ColumnName("AccountType")
	@ColumnTitle("Account Type")
	@FieldType(BEANFIELDTYPE.STRING)
	public String accountType; // ok
	@ColumnName("Inactive")
	@ColumnTitle("Inactive")
	@FieldType(BEANFIELDTYPE.BOOLEAN)
	public boolean inactive; // ok

	@ColumnName("AnnualFee")
	@ColumnTitle("Annual Fee")
	@FieldType(BEANFIELDTYPE.MONEY)
	public long annualFee; // ok
	@ColumnName("AprPercent")
	@ColumnTitle("APR Percent")
	@FieldType(BEANFIELDTYPE.PERCENT)
	public double aprPercent; // ok
	@ColumnName("BankAccountNumber")
	@ColumnTitle("Account Number")
	@FieldType(BEANFIELDTYPE.STRING)
	public String bankAccountNumber; // ok
	@ColumnName("BankName")
	@ColumnTitle("Name of Bank")
	@FieldType(BEANFIELDTYPE.STRING)
	public String bankName; // ok
	@ColumnName("Broker")
	@ColumnTitle("Name of Broker")
	@FieldType(BEANFIELDTYPE.STRING)
	public String broker; // ok
	@ColumnName("BrokerPhone")
	@ColumnTitle("Broker Phone Num")
	@FieldType(BEANFIELDTYPE.STRING)
	public String brokerPhone; // ok
	@ColumnName("SecurityType")
	@ColumnTitle("Security Type")
	@FieldType(BEANFIELDTYPE.STRING)
	public String securityType; // ok
	@ColumnName("SecuritySubType")
	@ColumnTitle("Security SubType")
	@FieldType(BEANFIELDTYPE.STRING)
	public String securitySubType; // ok
	@ColumnName("LotBased")
	@ColumnTitle("Lot Based")
	@FieldType(BEANFIELDTYPE.BOOLEAN)
	public boolean lotFlag;
	@ColumnName("CardExpirationMonth")
	@ColumnTitle("Card Expire Month")
	@FieldType(BEANFIELDTYPE.INTEGER)
	public int cardExpirationMonth; // ok
	@ColumnName("CardExpirationYear")
	@ColumnTitle("Card Expire Year")
	@FieldType(BEANFIELDTYPE.INTEGER)
	public int cardExpirationYear;// ok
	@ColumnName("CardNumber")
	@ColumnTitle("Card Long Number")
	@FieldType(BEANFIELDTYPE.STRING)
	public String cardNumber; // ok
	@ColumnName("CreditLimit")
	@ColumnTitle("Credit Limit")
	@FieldType(BEANFIELDTYPE.MONEY)
	public long creditLimit; // ok
	@ColumnName("CurrencyTypeID")
	@ColumnTitle("Currency ID")
	@FieldType(BEANFIELDTYPE.STRING)
	public String currencyTypeID; // ok
	@ColumnName("CurrencyTypeName")
	@ColumnTitle("Currency Name")
	@FieldType(BEANFIELDTYPE.STRING)
	public String currencyTypeName; // ok
	@ColumnName("DefaultCategory")
	@ColumnTitle("Default Category")
	@FieldType(BEANFIELDTYPE.STRING)
	public String defaultCategory; // ok
	@ColumnName("FullAccountName")
	@ColumnTitle("Long Account Name")
	@FieldType(BEANFIELDTYPE.STRING)
	public String fullAccountName; // ok
	@ColumnName("InitialBalance")
	@ColumnTitle("Initial Balance")
	@FieldType(BEANFIELDTYPE.MONEY)
	public long initialBalance; // ok startbalance
	@ColumnName("Comments")
	@ColumnTitle("Comments")
	@FieldType(BEANFIELDTYPE.STRING)
	public String comments; // ok
	@ColumnName("RoutingNumber")
	@ColumnTitle("Bank Routing/Sort Code")
	@FieldType(BEANFIELDTYPE.STRING)
	public String routingNumber; // ok OFXBankID
	@ColumnName("InitialDebt")
	@ColumnTitle("Initial Debt")
	@FieldType(BEANFIELDTYPE.MONEY)
	public long initialDebt; // same as start balance
	@ColumnName("PaymentPlan")
	@ColumnTitle("Payment Plan")
	@FieldType(BEANFIELDTYPE.STRING)
	public String paymentPlan; // tag pmt_spec
	@ColumnName("AprUntil")
	@ColumnTitle("Date APR changes")
	@FieldType(BEANFIELDTYPE.DATEINT)
	public java.sql.Date aprUntil; // tag apr_changes_dt
	@ColumnName("AprNewAmount")
	@ColumnTitle("New APR Percent")
	@FieldType(BEANFIELDTYPE.PERCENT)
	public double aprNewAmount; // tag apr_Perm_rt
	@ColumnName("principal")
	@ColumnTitle("Principal Amount")
	@FieldType(BEANFIELDTYPE.MONEY)
	public long principal;// tag init_principal
	@ColumnName("LoanPoints")
	@ColumnTitle("Loan Points")
	@FieldType(BEANFIELDTYPE.DOUBLE)
	public double loanPoints; // tag points
	@ColumnName("PaymentsPerYear")
	@ColumnTitle("Payments Per Year")
	@FieldType(BEANFIELDTYPE.INTEGER)
	public int paymentsPerYear; // tag pmts_per_year
	@ColumnName("NumPayments")
	@ColumnTitle("Total Num Payments")
	@FieldType(BEANFIELDTYPE.INTEGER)
	public int numPayments; // tag numPayments
	@ColumnName("InterestCategory")
	@ColumnTitle("Category for Interest")
	@FieldType(BEANFIELDTYPE.STRING)
	public String interestCategory; // tag interest_account
	@ColumnName("EscrowPayment")
	@ColumnTitle("Escrow Payment Amt")
	@FieldType(BEANFIELDTYPE.MONEY)
	public long escrowPayment; // ok
	@ColumnName("EscrowAccount")
	@ColumnTitle("Escrow Account Name")
	@FieldType(BEANFIELDTYPE.STRING)
	public String escrowAcct;// ok
	@ColumnName("SpecificPayment")
	@ColumnTitle("Specific Payment")
	@FieldType(BEANFIELDTYPE.MONEY)
	public long specificPayment;
	@ColumnName("PerPayment")
	@ColumnTitle("Percent Payment")
	@FieldType(BEANFIELDTYPE.DOUBLE)
	public double percentPayment;
	@ColumnName("CalcPayment")
	@ColumnTitle("Calculate or Specify Payment")
	@FieldType(BEANFIELDTYPE.BOOLEAN)
	public boolean calcPayment; // tag calc_pmt
	@ColumnName("StartDate")
	@ColumnTitle("Start Date")
	@FieldType(BEANFIELDTYPE.DATEINT)
	public java.sql.Date startDate;// ok creation date
	@ColumnName("ClearedBalance")
	@ColumnTitle("Cleared Balance")
	@FieldType(BEANFIELDTYPE.MONEY)
	public long clearedBalance; // ok
	@ColumnName("ConfirmedBalance")
	@ColumnTitle("Confirmed Balance")
	@FieldType(BEANFIELDTYPE.MONEY)
	public long confirmedBalance; // ok
	@ColumnName("CurrentBalance")
	@ColumnTitle("Current Balance")
	@FieldType(BEANFIELDTYPE.MONEY)
	public long currentBalance; // ok
	@ColumnName("SecClearedBalance")
	@ColumnTitle("Sec Cleared Balance")
	@FieldType(BEANFIELDTYPE.DOUBLE)
	public double secClearedBalance; // ok
	@ColumnName("SecConfirmedBalance")
	@ColumnTitle("Sec Confirmed Balance")
	@FieldType(BEANFIELDTYPE.DOUBLE)
	public double secConfirmedBalance; // ok
	@ColumnName("SecCurrentBalance")
	@ColumnTitle("Sec Current Balance")
	@FieldType(BEANFIELDTYPE.DOUBLE)
	public double secCurrentBalance;
	/*
	 * Transient fields
	 */
	private Account account;
	private Account subAccount;

	public AccountBean() {
		super();
		tableName = "Account";
		screenTitle = "Account";
		shortName = "acct";
		parmsName = Constants.PARMFLDACCT;
	}

	public Account getAccount() {
		return account;
	}

	public void setAccount(Account account) {
		this.account = account;
		this.subAccount = null;
	}

	public void setSubAccount(Account account, Account subAccount) {
		this.account = account;
		this.subAccount = subAccount;
	}

	@Override
	public void populateData() {
		accountId = setString(account.getUUID());
		accountName = setString(account.getAccountName());
		Account tempAcct;
		if (subAccount == null)
			tempAcct = account;
		else
			tempAcct = subAccount;
		accountType = setString(tempAcct.getAccountType().name());
		inactive = setBoolean(tempAcct.getAccountIsInactive());
		switch (tempAcct.getAccountType()) {
		case CREDIT_CARD:
			aprUntil = setDate(Utilities.getSQLDate(tempAcct.getRateChangeDate()));
			cardExpirationMonth = setInt(tempAcct.getCardExpirationMonth());
			cardExpirationYear = setInt(tempAcct.getCardExpirationYear());
			cardNumber = setString(tempAcct.getCardNumber());
			initialDebt = setMoney(tempAcct.getInitialPrincipal());
			creditLimit = setMoney(tempAcct.getCreditLimit());
			paymentPlan = setString(tempAcct.getDebtPaymentSpec().toString());
			aprNewAmount = setDouble(tempAcct.getPermanentAPR());
			calcPayment = setBoolean(tempAcct.getCalcPmt());
			interestCategory = setString(Constants.MISSINGSTRING);
			loanPoints = setDouble(Constants.MISSINGDOUBLE);
			paymentsPerYear = setInt(Constants.MISSINGINT);
			numPayments = setInt(Constants.MISSINGINT);
			specificPayment = setMoney(Constants.MISSINGLONG);
			percentPayment = setDouble(Constants.MISSINGDOUBLE);
			escrowAcct = setString(Constants.MISSINGSTRING);
			escrowPayment = setMoney(Constants.MISSINGLONG);
			break;
		case LOAN:
			aprUntil = setDate(Constants.MISSINGDATE);
			interestCategory = setString(
					tempAcct.getInterestAccount() == null ? "" : tempAcct.getInterestAccount().getAccountName());
			loanPoints = setDouble(tempAcct.getPoints());
			paymentsPerYear = setInt(tempAcct.getPaymentsPerYear());
			numPayments = setInt(tempAcct.getNumPayments());
			specificPayment = setMoney(tempAcct.getDebtPaymentAmount());
			percentPayment = setDouble(tempAcct.getDebtPaymentProportion());
			escrowAcct = setString(
					tempAcct.getEscrowAccount() == null ? "" : tempAcct.getEscrowAccount().getAccountName());
			escrowPayment = setMoney(tempAcct.getEscrowPayment());
			cardExpirationMonth = setInt(Constants.MISSINGINT);
			cardExpirationYear = setInt(Constants.MISSINGINT);
			cardNumber = setString(Constants.MISSINGSTRING);
			initialDebt = setMoney(Constants.MISSINGLONG);
			creditLimit = setMoney(Constants.MISSINGLONG);
			paymentPlan = setString(Constants.MISSINGSTRING);
			aprNewAmount = setDouble(Constants.MISSINGDOUBLE);
			calcPayment = setBoolean(tempAcct.getCalcPmt());
			break;
		case SECURITY:
			lotFlag = account == null ? false : tempAcct.getUsesAverageCost();
			securityType = account == null ? Constants.MISSINGSTRING : tempAcct.getSecurityType().name();
			securitySubType = account == null ? Constants.MISSINGSTRING : tempAcct.getSecuritySubType();
			broker = account == null ? Constants.MISSINGSTRING : tempAcct.getBroker();
			brokerPhone = account == null ? Constants.MISSINGSTRING : tempAcct.getBrokerPhone();
			aprUntil = setDate(Constants.MISSINGDATE);
			interestCategory = setString(Constants.MISSINGSTRING);
			loanPoints = setDouble(Constants.MISSINGDOUBLE);
			paymentsPerYear = setInt(Constants.MISSINGINT);
			numPayments = setInt(Constants.MISSINGINT);
			specificPayment = setMoney(Constants.MISSINGLONG);
			percentPayment = setDouble(Constants.MISSINGDOUBLE);
			escrowAcct = setString(Constants.MISSINGSTRING);
			escrowPayment = setMoney(Constants.MISSINGLONG);
			cardExpirationMonth = setInt(Constants.MISSINGINT);
			cardExpirationYear = setInt(Constants.MISSINGINT);
			cardNumber = setString(Constants.MISSINGSTRING);
			initialDebt = setMoney(Constants.MISSINGLONG);
			creditLimit = setMoney(Constants.MISSINGLONG);
			paymentPlan = setString(Constants.MISSINGSTRING);
			aprNewAmount = setDouble(Constants.MISSINGDOUBLE);
			calcPayment = setBoolean(tempAcct.getCalcPmt());
			break;
		default:
			aprUntil = setDate(Constants.MISSINGDATE);
			interestCategory = setString(Constants.MISSINGSTRING);
			loanPoints = setDouble(Constants.MISSINGDOUBLE);
			paymentsPerYear = setInt(Constants.MISSINGINT);
			numPayments = setInt(Constants.MISSINGINT);
			specificPayment = setMoney(Constants.MISSINGLONG);
			percentPayment = setDouble(Constants.MISSINGDOUBLE);
			escrowAcct = setString(Constants.MISSINGSTRING);
			escrowPayment = setMoney(Constants.MISSINGLONG);
			cardExpirationMonth = setInt(Constants.MISSINGINT);
			cardExpirationYear = setInt(Constants.MISSINGINT);
			cardNumber = setString(Constants.MISSINGSTRING);
			initialDebt = setMoney(Constants.MISSINGLONG);
			creditLimit = setMoney(Constants.MISSINGLONG);
			paymentPlan = setString(Constants.MISSINGSTRING);
			aprNewAmount = setDouble(Constants.MISSINGDOUBLE);
			calcPayment = setBoolean(tempAcct.getCalcPmt());
			break;
		}
		annualFee = setMoney(tempAcct.getAnnualFee());
		aprPercent = setDouble(tempAcct.getAPRPercent());
		bankAccountNumber = setString(tempAcct.getBankAccountNumber());
		bankName = setString(tempAcct.getBankName());
		routingNumber = setString(tempAcct.getOFXBankID());
		broker = setString(tempAcct.getBroker());
		brokerPhone = setString(tempAcct.getBrokerPhone());
		currencyTypeID = setString(tempAcct.getCurrencyType().getIDString());
		currencyTypeName = setString(tempAcct.getCurrencyType() == null ? "" : tempAcct.getCurrencyType().getName());
		defaultCategory = setString(
				tempAcct.getDefaultCategory() == null ? "" : tempAcct.getDefaultCategory().getAccountName());
		fullAccountName = setString(tempAcct.getFullAccountName());
		clearedBalance = setMoney(tempAcct.getClearedBalance());
		comments = setString(tempAcct.getComment());
		if (tempAcct.getAccountType() == AccountType.SECURITY) {
			secClearedBalance = setDouble(tempAcct.getCurrencyType().getDoubleValue(tempAcct.getClearedBalance()));
			secConfirmedBalance = setDouble(tempAcct.getCurrencyType().getDoubleValue(tempAcct.getConfirmedBalance()));
			secCurrentBalance = setDouble(tempAcct.getCurrencyType().getDoubleValue(tempAcct.getCurrentBalance()));
			confirmedBalance = setMoney(0L);
			currentBalance = setMoney(0L);
			clearedBalance = setMoney(0L);
		} else {
			clearedBalance = setMoney(tempAcct.getClearedBalance());
			confirmedBalance = setMoney(tempAcct.getConfirmedBalance());
			currentBalance = setMoney(tempAcct.getCurrentBalance());
			secConfirmedBalance = setDouble(0.0);
			secCurrentBalance = setDouble(0.0);
			secClearedBalance = setDouble(0.0);
		}
		initialBalance = setMoney(tempAcct.getStartBalance());
		startDate = setDate(Utilities.getSQLDate(tempAcct.getCreationDateInt()));
	}

	public Account retrieveAccount() {
		return account;
	}

}

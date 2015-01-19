/************************************************************\
 *      Copyright (C) 2008 Reilly Technologies, L.L.C.      *
\************************************************************/

package com.moneydance.modules.features.txtimport;

import com.infinitekind.moneydance.model.*;
import com.infinitekind.util.DateUtil;
import com.moneydance.apps.md.controller.UserPreferences;
import com.infinitekind.util.*;
import java.io.*;
import java.util.*;

public class ImportState {

  public static final byte ACCOUNT = 1;
  public static final byte AMOUNT = 2;
  public static final byte CHECKNUM = 3;
  public static final byte DATE = 4;
  public static final byte DESCRIPTION = 5;
  public static final byte STATUS = 6;
  public static final byte MEMO = 7;
  public static final byte NOTHING = 8;

  private static final int MDY = 0;
  private static final int DMY = 1;
  private static final int YMD = 2;
  private static final int YDM = 3;

  private static final byte Y = (byte)0;
  private static final byte M = (byte)1;
  private static final byte D = (byte)2;
  
  public static final String[] ENC_NAMES = { "DEFAULT", "ASCII", "UTF8" };
  public static final String[] ENC_IDS = { null, "ASCII", "UTF8" };
  
  public static final byte[] FIELD_IDS = { DATE, CHECKNUM, DESCRIPTION, ACCOUNT, 
                                           STATUS, AMOUNT, MEMO, NOTHING };
  public static final String[] FIELD_KEYS = { "date", "chknum", "description", "account_ls",
                                              "status", "amount", "memo", "ignore" };
  
  public static final String[] FILE_ENCODINGS = {"UTF-8", "UTF-16BE", "UTF-16LE",
                                                 "UTF-16", "US-ASCII", "ISO-8859-1" };
  public static final String[] DATE_FORMATS = {"MDY","DMY","YMD","YDM"};
  public static final int[] DATE_FORMAT_IDS = {MDY,DMY,YMD,YDM};
  public static final String[] DELIMITER_NAMES = { "[tab]", "[space]", "[ , ]",
                                                   "[ . ]", "[ | ]", "[ / ]",
                                                   "[ \\ ]", "[ - ]", "[ _ ]",
                                                   "[ * ]", "[ ~ ]", "[ ; ]" };
  public static final char[] DELIMITERS = {'\t', ' ', ',',
                                           '.', '|', '/',
                                           '\\', '-', '_',
                                           '*', '~', ';' };
  public static final String[] DECIMAL_POINT_NAMES = {".", ","};
  public static final char[] DECIMAL_POINTS = {'.', ','};

  private Main main = null;
  private File importFile = null;
  private String fileEncoding = FILE_ENCODINGS[0];
  private byte fieldsToImport[] = null;
  private char delimiter = '\t';
  private char decimalPoint = '.';
  private int dateFormat = MDY;
  private Account account = null;

  private int recordCount = 0;

  private AccountBook book;
  private Resources rr;
  
  public ImportState(
        Main m,
        Account root,
        Resources rr,
        String filename,
        Integer argAcctNum) {
    this.main = m;
    this.book = root.getBook();
    this.rr = rr;
    setFields(FIELD_IDS);

    try {
      String tmp;
      UserPreferences prefs = main.getMainController().getPreferences();
      if (filename != null && !"".equals(filename)) this.importFile = new File(filename);
      int numFields = prefs.getIntSetting("txtimport.numfields", FIELD_IDS.length);
      fieldsToImport = new byte[numFields];
      for(int i=0; i<fieldsToImport.length; i++) {
        fieldsToImport[i] = (byte)prefs.getIntSetting("txtimport.field"+i, FIELD_IDS[i]);
      }
      tmp = prefs.getSetting("txtimport.delimiter", String.valueOf(delimiter));
      if(tmp.length()>0) delimiter = tmp.charAt(0);
      fileEncoding = prefs.getSetting("txtimport.enc", fileEncoding);
      dateFormat = prefs.getIntSetting("txtimport.datefmt", MDY);
      tmp = prefs.getSetting("txtimport.decimal", ""+decimalPoint);
      if(tmp.length()>0) decimalPoint = tmp.charAt(0);
      int acctNum = prefs.getIntSetting("txtimport.acct", -1);
      if (argAcctNum != null) acctNum = argAcctNum.intValue();
      if(acctNum>=0) account = book.getAccountByNum(acctNum);
    } catch (Throwable t) {
      System.err.println("Error restoring preferences: "+t);
    }
    
  }

  void setDateFormat(int dateFormat) {
    this.dateFormat = dateFormat;
  }
  int getDateFormatIdx() {
    for(int i=0; i<DATE_FORMAT_IDS.length; i++) {
      if(dateFormat==DATE_FORMAT_IDS[i])
        return i;
    }
    dateFormat = DATE_FORMAT_IDS[0];
    return 0;
  }

  void setDelimiter(char delimiter) {
    this.delimiter = delimiter;
  }
  int getDelimiterIdx() {
    for(int i=0; i<DELIMITERS.length; i++) {
      if(DELIMITERS[i]==delimiter)
        return i;
    }
    delimiter = DELIMITERS[0];
    return 0;
  }

  void setDecimalPoint(char decimalPoint) {
    this.decimalPoint = decimalPoint;
  }
  int getDecimalPointIdx() {
    for(int i=0; i<DECIMAL_POINTS.length; i++) {
      if(DECIMAL_POINTS[i]==decimalPoint)
        return i;
    }
    decimalPoint = DECIMAL_POINTS[0];
    return 0;
  }
  
  void setFile(File fileToImport) {
    this.importFile = fileToImport;
  }

  File getFile() {
     return this.importFile;
  }

  void setFileEncoding(String encoding) {
    this.fileEncoding = encoding;
  }

  String getFileEncoding() {
    String encoding = this.fileEncoding;
    if(encoding==null) {
      encoding = FILE_ENCODINGS[0];
      fileEncoding = encoding;
    }
    return encoding;
  }

  void setAccount(Account account) {
    this.account = account;
  }

  Account getAccount() {
    return this.account;
  }
  
  void setFields(byte fields[]) {
    this.fieldsToImport = new byte[fields.length];
    System.arraycopy(fields, 0, fieldsToImport, 0, fields.length);
  }

  byte[] getFields() {
    byte fields[] = new byte[fieldsToImport.length];
    System.arraycopy(fieldsToImport, 0, fields, 0, fields.length);
    return fields;
  }

  String getNameForField(byte fieldID) {
    for(int i=0; i<FIELD_IDS.length; i++) {
      if(FIELD_IDS[i]==fieldID)
        return rr.getString(FIELD_KEYS[i]);
    }
    return "??";
  }

  /** Get a list of the accounts that can be selected for importing. */
  Account[] getAccountList() {
    Vector accounts = new Vector();
    getAccounts(book.getRootAccount(), accounts);
    Account accountArray[] = new Account[accounts.size()];
    for(int i=accountArray.length-1; i>=0; i--) {
      accountArray[i] = (Account)accounts.elementAt(i);
    }
    return accountArray;
  }

  /**
   * Do the import, with the current set of parameters.
   */
  public void doImport()
    throws Exception
  {
    recordCount = 0;
    if(fieldsToImport==null || fieldsToImport.length<=0) {
      throw new Exception(rr.getString("no_fields_err"));
    }

    Reader rdr = null;
    BufferedReader brdr = null;
    TransactionSet txnSet = null;
    try {
      String encoding = fileEncoding;
      if(encoding==null)
        encoding = FILE_ENCODINGS[0];
      rdr = new InputStreamReader(new FileInputStream(importFile), encoding);
      
      brdr = new BufferedReader(rdr);
      txnSet = book.getTransactionSet();
      
      String line;
      String[] fields = null;

      long amount = 0;
      Account category = null;
      int date = 0;
      String checkNum = null;
      String description = null;
      String memo = null;
      byte status = AbstractTxn.STATUS_UNRECONCILED;
      int today = DateUtil.getStrippedDateInt();
      CurrencyType currency = account.getCurrencyType();
      
      while(true) {
        line = brdr.readLine();
        if(line==null) break;
        line = line.trim();

        if(line.length()<=0) continue; // skip blank lines
        
        if (!line.matches("^(.*" + this.delimiter + "){" + (this.fieldsToImport.length - 1) + "}.*$")) {
          // skip lines with too much or too few fields
          continue;
        }

        // replace double quotes surrounding each field
        line = line.replaceAll("^\"", "");
        line = line.replaceAll("\"$", "");

        char[] charDelimiter = { this.delimiter };
        String strDelimiter = new String(charDelimiter);
        line = line.replaceAll("\"" + this.delimiter + "\"", strDelimiter);        

        // read each line into a Moneydance transaction...
        fields = StringUtils.split(line, delimiter);
        date = getDate(fields, today);
        amount = getAmount(fields, 0, currency);
        checkNum = getField(fields, CHECKNUM, "");
        description = getField(fields, DESCRIPTION, "");
        memo = getField(fields, MEMO, "");
        status = getStatus(fields, AbstractTxn.STATUS_UNRECONCILED);
        
        if (amount==0 && checkNum.length()==0 && description.length()==0) {
          continue;
        }

        category = getAccount(fields, rr.getString("default_category"),
                              amount<=0 ? Account.AccountType.EXPENSE : Account.AccountType.INCOME);
        
        ParentTxn ptxn = ParentTxn.makeParentTxn(book, date, date, System.currentTimeMillis(), 
                                                 checkNum, account, description, memo, -1, status);
        ptxn.addSplit(SplitTxn.makeSplitTxn(ptxn, amount, 1.0, category, ptxn.getDescription(), -1, status));
        ptxn.syncItem();
      }

      // safe the settings in the preferences
      try {
        UserPreferences prefs = main.getMainController().getPreferences();
        prefs.setSetting("txtimport.numfields", fieldsToImport.length);
        for(int i=0; i<fieldsToImport.length; i++) {
          prefs.setSetting("txtimport.field"+i, String.valueOf((int)fieldsToImport[i]));
        }
        prefs.setSetting("txtimport.delimiter", String.valueOf(delimiter));
        prefs.setSetting("txtimport.enc", fileEncoding);
        prefs.setSetting("txtimport.datefmt", dateFormat);
        prefs.setSetting("txtimport.decimal", ""+decimalPoint);
        prefs.setSetting("txtimport.acct", account.getAccountNum());
      } catch (Throwable t) {
        System.err.println("Error saving preferences: "+t);
      }
    } finally {
      if(brdr!=null) try { brdr.close(); } catch (Throwable t) {}
      if(rdr!=null) try { rdr.close(); } catch (Throwable t) {}
    }
  }

  /** Find and return the STATUS field in the appropriate format. */
  private final byte getStatus(String[] fieldValues, byte defaultStatus) {
    String statusStr = getField(fieldValues, STATUS, null);
    if(statusStr==null) return defaultStatus;
    statusStr = statusStr.trim();
    if(statusStr.length()<=0) return AbstractTxn.STATUS_UNRECONCILED;
    if(statusStr.startsWith("x") || statusStr.startsWith("X"))
      return AbstractTxn.STATUS_CLEARED;
    else if(statusStr.startsWith("*"))
      return AbstractTxn.STATUS_RECONCILING;
    return AbstractTxn.STATUS_UNRECONCILED;
  }
  
  /** Find and return the AMOUNT field in the appropriate format. */
  private final long getAmount(String[] fieldValues, long defaultAmount, CurrencyType currency) {
    String amountStr = getField(fieldValues, AMOUNT, null);
    if(amountStr==null) return defaultAmount;
    return currency.parse(amountStr, decimalPoint);
  }
  
  /** Find and return the DATE field in the appropriate format. */
  private final int getDate(String[] fieldValues, int defaultDate) {
    String dateStr = getField(fieldValues, DATE, null);
    if(dateStr==null) return defaultDate;
    dateStr = dateStr.trim();
    if(dateStr.length()<=0) return defaultDate;
    return parseDate(dateStr);
  }
  
  /** Find and return the ACCOUNT field in the appropriate format. */
  private final Account getAccount(String[] fieldValues, String defaultAccount, Account.AccountType defaultAcctType)
    throws Exception
  {
    String acctStr = getField(fieldValues, ACCOUNT, null);
    if(acctStr==null) return addNewAccount(defaultAccount, account.getCurrencyType(),
                                           book.getRootAccount(), "", defaultAcctType, true, -1);
    acctStr = acctStr.trim();
    return addNewAccount(acctStr, account.getCurrencyType(), book.getRootAccount(), "",
                         defaultAcctType, true, -1);
  }
  
  private final String getField(String[] fieldValues, byte code, String defStr) {
    if(fieldsToImport==null) return defStr;
    for(int i = Math.min(fieldValues.length-1, fieldsToImport.length-1); i>=0; i--) {
      if(fieldsToImport[i]==code) return fieldValues[i];
    }
    return defStr;
  }

  private void getAccounts(Account acct, Vector acctList) {
    for(int i=0; i<acct.getSubAccountCount(); i++) {
      Account subAcct = acct.getSubAccount(i);
      if(isChoosable(subAcct))
        acctList.addElement(subAcct);
      getAccounts(subAcct, acctList);
    }
  }
  
  private final boolean isChoosable(Account acct) {
    switch(acct.getAccountType()) {
      case BANK:
      case CREDIT_CARD:
      case ASSET:
      case LIABILITY:
      case LOAN:
        return true;
      default:
        return false;
    }
  }

  private final Calendar cal = Calendar.getInstance();

  private final int parseDate(String dateStr) {
    if(dateStr==null) return DateUtil.getStrippedDateInt();
    dateStr = dateStr.trim();
    int len = dateStr.length();
    char thisChar;
    int fieldIdx = 0;
    int fieldValues[] = { -1, -1, -1};
    for(int i=0; fieldIdx<3 && i<len; i++) {
      thisChar = dateStr.charAt(i);
      if(thisChar>='0' && thisChar<='9') { // is a digit...
        if(fieldValues[fieldIdx]==-1)
          fieldValues[fieldIdx] = 0;
        fieldValues[fieldIdx] *= 10;
        fieldValues[fieldIdx] += thisChar-'0';
      } else if(thisChar=='"' || thisChar=='\'') {
        // skip quotes
      } else {
        fieldIdx++;
      }
    }

    byte dateFields[] = { M, D, Y };
    switch(dateFormat) {
      case DMY:
        System.err.print("DMY ");
        dateFields = new byte[] {D, M, Y};
        break;
      case YMD:
        System.err.print("YMD ");
        dateFields = new byte[] {Y, M, D};
        break;
      case YDM:
        System.err.print("YDM ");
        dateFields = new byte[] {Y, D, M};
        break;
      case MDY:
      default:
        System.err.print("MDY ");
        dateFields = new byte[] {M, D, Y};
        break;
    }
    
    System.err.print("\n"+dateStr+"-->"+fieldValues[0]+", "+fieldValues[1]+", "+fieldValues[2]);
    int day = -1;
    int month = -1;
    int year = -1;
    if(fieldIdx==0 || (fieldIdx==1 && fieldValues[1]==0)) { // the values were not delimited!
      if(fieldValues[0]==0) { // no values!  return the current date
        cal.setTime(new Date()); 
      } else if(fieldValues[0]>9999) { // full date with or without century
        boolean includesCentury = fieldValues[0]>999999;
        cal.setTime(new Date());
        for(int i=2; i>=0; i--) {
          int blah = i;
          switch(dateFields[i]) {
            case Y:
              year = fieldValues[0]%(includesCentury?10000:100);
              fieldValues[0] = fieldValues[0]/(includesCentury?10000:100);
              break;
            case M:
              month = fieldValues[0]%100;
              fieldValues[0] = fieldValues[0]/100;
              break;
            case D:
              day = fieldValues[0]%100;
              fieldValues[0] = fieldValues[0]/100;
              break;
            default:
          }
        }
        if(year>=0) cal.set(Calendar.YEAR, year);
        if(month>=1) cal.set(Calendar.MONTH, month-1);
        if(day>=1) cal.set(Calendar.DAY_OF_MONTH, day);
      } else if(fieldValues[0]>99) { // mmdd or ddmm
        cal.setTime(new Date());
        year = cal.get(Calendar.YEAR);
        boolean monthFirst = true;
        for(int fi=0; fi<3; fi++) {
          if(dateFields[fi]==M) {
            monthFirst = true;
            break;
          } else if(dateFields[fi]==D) {
            monthFirst = false;
            break;
          }
        }
        if(monthFirst) {
          month = fieldValues[0]/100;
          day = fieldValues[0]%100;
        } else {
          day = fieldValues[0]/100;
          month = fieldValues[0]%100;
        }
        cal.set(Calendar.YEAR, year);
        cal.set(Calendar.MONTH, month-1);
        cal.set(Calendar.DAY_OF_MONTH, day);
      } else { // just the day of month (dd)
        cal.setTime(new Date());
        cal.set(Calendar.DAY_OF_MONTH, fieldValues[0]);
      }
    } else { // the fields were delimited...
      cal.setTime(new Date());
      for(int i=2; i>=0; i--) {
        if(fieldValues[i]==-1) continue;
        switch(dateFields[i]) {
          case Y:
            year = guessCenturyForYear(fieldValues[i]);
            break;
          case M:
            month = fieldValues[i];
            break;
          case D:
            day = fieldValues[i];
            break;
          default:
        }
      }
      if(year>=0) cal.set(Calendar.YEAR, year);
      if(month>=1) cal.set(Calendar.MONTH, month-1);
      if(day>=1) cal.set(Calendar.DAY_OF_MONTH, day);
    }

    cal.set(Calendar.HOUR_OF_DAY,12);
    cal.set(Calendar.MINUTE,0);
    cal.set(Calendar.SECOND,0);
    cal.set(Calendar.MILLISECOND,0);
    return DateUtil.convertCalToInt(cal);
  }

  private static final int guessCenturyForYear(int year) {
    if(year>199) {
      return year;
    } else if(year>72) {
      return year + 1900;
    } else {
      return year + 2000;
    }
  }

  private Account addNewAccount(String accountName, CurrencyType currencyType,
                                Account parentAccount, String description,
                                Account.AccountType accountType, boolean lenientMatch,
                                int currAccountId)
    throws Exception
  {
    if(accountName.indexOf(':')==0 && parentAccount.getAccountType()== Account.AccountType.ROOT) {
      accountName = accountName.substring(1);
    }

    int colIndex = accountName.indexOf(':');
    String restOfAcctName;
    String thisAcctName;
    if(colIndex>=0) {
      restOfAcctName = accountName.substring(colIndex+1);
      thisAcctName = accountName.substring(0,colIndex);
    } else {
      restOfAcctName = null;
      thisAcctName = accountName;
    }

    Account newAccount = null;
    for(int i=0; i<parentAccount.getSubAccountCount(); i++) {
      Account subAcct = parentAccount.getSubAccount(i);
      if((lenientMatch && subAcct.getAccountName().equalsIgnoreCase(thisAcctName)) ||
         (subAcct.getAccountType()==accountType &&
          subAcct.getAccountName().equalsIgnoreCase(thisAcctName))) {
        newAccount = subAcct;
        break;
      }
    }

    if(newAccount==null) {
      newAccount = Legacy.makeAccount(book, accountType, thisAcctName, currencyType, parentAccount);
      newAccount.setBankName(description);
      newAccount.setAccountDescription(description);
      newAccount.syncItem();
    }
    
    if(restOfAcctName!=null) {
      return addNewAccount(restOfAcctName, currencyType, newAccount,
                           description, accountType,lenientMatch,
                           currAccountId);
    } else {
      if(newAccount.getAccountNum()==currAccountId) {
        // if the found account is the same as the container account
        // create another account with the same name and return it
        if(accountType==Account.AccountType.BANK && parentAccount==book.getRootAccount()) {
          newAccount = Legacy.makeAccount(book, Account.AccountType.INCOME, 
                                          thisAcctName+"X", currencyType, 
                                          parentAccount);
        } else {
          newAccount = Legacy.makeAccount(book, accountType, thisAcctName+"X", 
                                          currencyType, parentAccount);
        }
        newAccount.setBankName(description);
        newAccount.syncItem();
      }
      return newAccount;
    }
  }
  


}









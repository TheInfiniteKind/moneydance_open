/************************************************************\
*      Copyright (C) 2007 Reilly Technologies, L.L.C.      *
\************************************************************/

package com.moneydance.modules.features.palmsync;

import java.io.*;
import java.util.*;
import com.infinitekind.moneydance.model.*;
import com.moneydance.apps.md.controller.*;
import com.moneydance.apps.md.view.resources.Resources;
import com.moneydance.apps.md.view.MoneydanceUI;
import com.infinitekind.util.*;

/** Object that converts a QIF file to PalmTxns.*/
public class QIFDataReader {
  private RootAccount rootAccount;
  private File qifFile;
  private PalmAccount account;
  
  public QIFDataReader(RootAccount rootAccount, File qifFile, PalmAccount account) {
    this.qifFile = qifFile;
    this.rootAccount = rootAccount;
    this.account = account;
  }

  public PalmTxn[] readTransactions()
    throws Exception
  {
    int fileSize = (int)qifFile.length();
    BufferedReader in =
      new BufferedReader(new InputStreamReader(new FileInputStream(qifFile)), 1000);
    String line = in.readLine();
    try {
      while(true) {
        if(line==null)
          return null;
    
        line = line.trim();
        if(line.length()<=0) {
          line = in.readLine();
          continue;
        }
        if(line.toUpperCase().startsWith("!TYPE:") ||
           line.toUpperCase().startsWith("TYPE:")) {
          // read the transactions
          return readTxnRegister(in, null);
        } else if(line.toUpperCase().startsWith("D") ||
                  line.toUpperCase().startsWith("C")) {
          return readTxnRegister(in, line);
        } else {
          line = readUpToSectionStart(in);  // ignore this section
        }
      }
    } finally {
      try { in.close(); } catch (Throwable t) {}
    }
  }
  
  public String readAccountName() throws Exception {
    int fileSize = (int)qifFile.length();
    BufferedReader in = new BufferedReader(new InputStreamReader(new FileInputStream(qifFile)), 				1000);
    String line = in.readLine();
    try {
      while(true) {
        if(line==null)
          return null;
        
        line = line.trim();
        if(line.length()<=0) {
          line = in.readLine();
          continue;
        }
        if(line.toUpperCase().startsWith("!ACCOUNT")) {
          return readAccountName(in);
         }
        else {
          line = readUpToSectionStart(in);  // ignore this section
         }
      }
    } 
      catch(Exception e) {
        System.out.println("Exception in read account name : " + e);
      }
      try { in.close(); } catch (Throwable t) {}
    return null;
  }


  /** Read in a definition of an account. */
  private String readAccountName(BufferedReader in) throws Exception {
    TxnEntry qifEntry = null;
    String line = in.readLine();
    while((qifEntry = readBasicTxn(in,line))!=null) {
      /* D Description
         N Account Name
         T Type         */
      String nameStr = qifEntry.getAccount("N");
    }
    return null;
  }


// *********************************************************************

  /** Read a bank register, returning the line after the register ends. */
  private PalmTxn[] readTxnRegister(BufferedReader in, String firstLine)
    throws Exception
  {
    Vector vec = new Vector();
    
    BankTxnEntry qifTxn=null;
    String line = firstLine==null ? in.readLine() : firstLine;
    boolean firstTxn = true;
    int counter = 0;
    while( (qifTxn = readBankTxn(in, line))!=null) {
      
      if(counter++%200 == 0) {
        System.gc();
        System.runFinalization();
      }

      line = null;
      
      String amount = qifTxn.getAmount("T");
      long date = qifTxn.getDate("D");
      byte status = qifTxn.getStatus("C");
      String category = qifTxn.getAccount("L");
      String checknum = qifTxn.getRecord("N");
      String description = qifTxn.getRecord("P");

      if(qifTxn.getNumSplits()<=0) { // find/create the category/transfer account
        boolean isTransfer = false;
        if(category.startsWith("[") && category.endsWith("]")) {
          category = category.substring(1,category.length()-1).trim();
        }
      } 
      
      CurrencyType currency = account.getSyncAccount().getCurrencyType();
      PalmTxn txn = new PalmTxn(account);
      txn.setDate(new Date(date));
      txn.setAmount(currency.parse(amount, '.'));
      txn.setDescription(description);
      txn.setCategory(category);
      txn.setCheckNum(checknum);
      txn.setCleared(status==AbstractTxn.STATUS_CLEARED);
      if(qifTxn.getNumSplits()>1) {
        for(int i=0; i<qifTxn.getNumSplits(); i++) {
          TxnEntry split = qifTxn.getSplit(i);
          String splitDesc = split.getRecord("E");
          String splitCat = split.getAccount("S");
          long splitAmt = currency.parse(split.getAmount("$"),'.');
          
          if(splitDesc==null || splitDesc.trim().length()<=0)
            splitDesc = description;
          if(splitCat==null)
            splitCat = category;
          txn.addSplit(splitDesc, splitCat, splitAmt);
        }
      }
      
      vec.addElement(txn);
      line = in.readLine();
    }

    PalmTxn[] txns = new PalmTxn[vec.size()];
    vec.copyInto(txns);
    return txns;
  }

  private String readUpToSectionStart(BufferedReader in) throws Exception {
    String line="";
    while(line!=null) {
      line=in.readLine();
      if(line==null) {
        return null;
      }
      if(line.startsWith("!") ||
         line.toUpperCase().startsWith("TYPE:") ||
         line.toUpperCase().startsWith("ACCOUNT") ||
         line.toUpperCase().startsWith("OPTION:") ||
         line.toUpperCase().startsWith("AUTOSWITCH") ||
         line.toUpperCase().startsWith("CLEAR:"))
        return line;
    }
    return line;
  }


  /** Read the transaction, including the specified first line */
  BankTxnEntry readBankTxn(BufferedReader in, String line) throws Exception {
    if(line!=null && (line.startsWith("^") || line.startsWith("!")))
      return null;
    BankTxnEntry txn = null;
    while(true) {
      if(line==null || line.startsWith("^"))
        return txn;

      if(txn==null) txn = new BankTxnEntry();
      txn.takeLine(line);
      line = in.readLine();
    }
  }

  TxnEntry readBasicTxn(BufferedReader in, String line) throws Exception {
    if(line!=null && (line.startsWith("^") || line.startsWith("!")))
      return null;
    TxnEntry txn = null;
    while(true) {
      if(line==null || line.startsWith("^"))
        return txn;
      if(txn==null) txn = new TxnEntry();
      txn.takeLine(line);
      line = in.readLine();
    }
  }

  class TxnEntry {
    private Hashtable records;

    TxnEntry() {
      records = new Hashtable();
    }

    void setRecord(String recordKey, String val) {
      if(!records.contains(recordKey))
        records.put(recordKey,val);
    }

    String getRecord(String recordKey) {
      String val = (String)records.get(recordKey);
      return (val==null)?"":val;
    }

    String getAccount(String recordKey) {
      // get a record representing an account, and strip off the
      // quicken "class" (the part after the /)
      String val = getRecord(recordKey);
      int slashIdx = val.indexOf('/');
      if(slashIdx>=0) {
        val = val.substring(0, slashIdx);
      }
      return val;
    }
    
    String getAmount(String recordKey) {
      // figure out whether this currency uses commas or periods as
      // a decimal point.  ****EXPERIMENTAL****
      String val = getRecord(recordKey);
      char decimalPoint = StringUtils.guessDecimalType(val);
      return val;
    }

    double getRate(String recordKey) {
      // figure out whether this currency uses commas or periods as
      // a decimal point.  ****EXPERIMENTAL****
      String val = getRecord(recordKey);
      char decimalPoint = StringUtils.guessDecimalType(val);
      return StringUtils.parseRate(val, decimalPoint);
    }

    byte getStatus(String recordKey) {
      String val = getRecord(recordKey).trim();
      if(val.startsWith("x") || val.startsWith("X"))
        return AbstractTxn.STATUS_CLEARED;
      else if(val.startsWith("*"))
        return AbstractTxn.STATUS_RECONCILING;
      return AbstractTxn.STATUS_UNRECONCILED;
    }

    long getDate(String recordKey) {
      return parseQuickenDate(getRecord(recordKey), Common.QIF_FORMAT_MMDDYY);
    }

    void takeLine(String line) {
      if(line==null) return;
      line = line.trim();
      if(line.length()<=0) return;
      setRecord(line.toUpperCase().substring(0,1),
                line.substring(1));
    }
    
    public String toString() {
      StringBuffer sb = new StringBuffer();
      for(Enumeration keys=records.keys(); keys.hasMoreElements();) {
        Object key = keys.nextElement();
        sb.append(key).append(" = ").append(records.get(key)).append("; ");
      }
      return sb.toString();
    }
  }


  private static Calendar cal = Calendar.getInstance();
  public static long parseQuickenDate(String origDate, byte dateFormat) {
    String date = origDate.trim();
    //Calendar cal = Calendar.getInstance();
    cal.set(Calendar.HOUR_OF_DAY, 12);
    cal.set(Calendar.MINUTE, 0);
    cal.set(Calendar.SECOND, 0);

    String fields[] = new String[]{ "", "", ""};
    int intFields[] = new int[3];
    char delim[] = new char[2];
    int fieldIdx = 0;

    int MONTH_INDEX = 0;
    int DAY_INDEX = 1;
    int YEAR_INDEX = 2;
        
    // read all of the characters until we get a number...
    while(true) {
      if(date.length()<=0)
        break;
      char ch = date.charAt(0);
      if(ch<'0' || ch>'9') {
        // not a numeric digit...
        date = date.substring(1);
      } else {
        break;
      }
    }

    // extract the fields and the delimiters...
    for(int i=0; fieldIdx < fields.length && i < date.length(); i++) {
      char ch = date.charAt(i);
      if(ch==' ' || (ch>='0' && ch<='9')) {
        fields[fieldIdx] += String.valueOf(ch);
      } else { // got a delimiter...
        if(fieldIdx<delim.length)
          delim[fieldIdx] = ch;
        fieldIdx++;
      }
    }

    switch(dateFormat) {
      case Common.QIF_FORMAT_MMDDYY:
        MONTH_INDEX = 0;
        DAY_INDEX = 1;
        YEAR_INDEX = 2;
        break;
      case Common.QIF_FORMAT_YYMMDD:
        YEAR_INDEX = 0;
        MONTH_INDEX = 1;
        DAY_INDEX = 2;
        break;
      case Common.QIF_FORMAT_DDMMYY:
        DAY_INDEX = 0;
        MONTH_INDEX = 1;
        YEAR_INDEX = 2;
        break;
      case Common.QIF_FORMAT_AUTO:
      default:
        if(delim[0]=='.') {
          DAY_INDEX = 0;
          MONTH_INDEX = 1;
          YEAR_INDEX = 2;
        } else { // if(delim[0]=='-') or any other delimiter
          MONTH_INDEX = 0;
          DAY_INDEX = 1;
          YEAR_INDEX = 2;
        }
        break;
    }

    // if there were no delimiters, parse fields[0] according to character position
    if(fieldIdx<2) {
      date = fields[0].trim();
      if(date.length()<8) { // 2 digit year
        try {
          fields[0] = date.substring(0,2);
          fields[1] = date.substring(2,4);
          fields[2] = date.substring(4);
        } catch (Exception e) {
            System.err.println("Invalid QIF date: "+date);
            e.printStackTrace(System.err);
          
        }
      } else { // 4 digit year
        try {
          if(YEAR_INDEX==0) {
            fields[0] = date.substring(0,4);
            fields[1] = date.substring(4,6);
            fields[2] = date.substring(6);
          } else if(YEAR_INDEX==1) {
            fields[0] = date.substring(0,2);
            fields[1] = date.substring(2,6);
            fields[2] = date.substring(6);
          } else { // YEAR_INDEX==2
            fields[0] = date.substring(0,2);
            fields[1] = date.substring(2,4);
            fields[2] = date.substring(4);
          }
        } catch (Exception e) {
            System.err.println("Error parsing QIF date: "+date);
            e.printStackTrace(System.err);
        }
        
      }
    }

    // convert each of the fields to an integer
    for(int i=0; i<fields.length; i++) {
      try {
        intFields[i] = Integer.parseInt(fields[i].trim());
      } catch (Exception e) {
            System.err.println("Warning: had trouble parsing field "+i+
                              " ("+fields[i]+") in QIF date: "+origDate);
            e.printStackTrace(System.err);
          
      }
    }
    
    int day = intFields[DAY_INDEX];
    int mo = intFields[MONTH_INDEX];
    int year = intFields[YEAR_INDEX];
      
    cal.set(Calendar.MONTH, mo-1);
    cal.set(Calendar.DAY_OF_MONTH, day);
    if(year>1800) {
      // year stays the same...
    } else if(year<70) {
      // 2 digit, 20XX year
      year = year + 2000;
    } else { // 2 digit, 19XX year or 3 digit 2XXX year
      year = year + 1900;
    }
    cal.set(Calendar.YEAR, year);
    return cal.getTime().getTime();
  }



  /*
    ---- Split transaction fields ----
    S Split category
    E Split description
    $ Split amount
   */

  /*
    ---- Bank transaction fields ----
    D Date
    N Action
    Y Security
    I Price
    Q Quantity
    C Status
    P Memo
    M Description
    O Commission
    L Category
    $ or T Amount
    */

  /*
    D Date
    T Amount
    C Status
    N CheckNum
    P Description
    M Memo
    L Category
  */
  class BankTxnEntry extends TxnEntry {
    private Vector splits = null;

    BankTxnEntry() {
    }

    int getNumSplits() {
      return splits==null ? 0 : splits.size();
    }

    TxnEntry getSplit(int i) {
      return splits==null ? null : (TxnEntry)splits.elementAt(i);
    }

    void takeLine(String line) {
      char key = '?';
      line = line.trim();
      if(line.length()>0)
        key = line.toUpperCase().charAt(0);
      else
        return; // blank lines are not very useful to us
      switch(key) {
      case 'S':
        TxnEntry split = new TxnEntry();
        if(splits==null) splits = new Vector();
        splits.addElement(split);
        split.setRecord("S",line.substring(1).trim());
        break;
      case 'E':
        if(splits!=null && splits.size()>0)
          ((TxnEntry)splits.elementAt(splits.size()-1)).
            setRecord("E",line.substring(1).trim());
        else
          System.err.println("QIF Import Error: record out of context: \""+line+"\"");
        break;
      case '$':
        if(splits!=null && splits.size()>0)
          ((TxnEntry)splits.elementAt(splits.size()-1)).
            setRecord("$",line.substring(1).trim());
        else
          System.err.println("QIF Import Error: record out of context: \""+line+"\"");
        break;
      default:
        setRecord(String.valueOf(key),line.substring(1));
        break;
      }
    }   
     }

}

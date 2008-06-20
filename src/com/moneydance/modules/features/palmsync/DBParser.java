/************************************************************\
*      Copyright (C) 2007 Reilly Technologies, L.L.C.      *
\************************************************************/

package com.moneydance.modules.features.palmsync;

import java.io.*;
import java.util.*;

import com.syncbuilder.storage.pocketmoney.*;
import com.syncbuilder.sync.*;
import com.syncbuilder.extstorage.*;
import com.syncbuilder.storage.*;
import com.syncbuilder.util.Util;
import com.moneydance.util.*;

public class DBParser {
  
  // This code based on ExpenseSucker.java, modified from that by Tilo Christ
  
  private FileInputStream istream;
  private MemoryDatabase db;
  private ExternalizationManager extman;
  private boolean areRecords = true;
  
  public DBParser(File fileName) throws Exception {
    istream = new FileInputStream(fileName);
  }
      
  public boolean areNewRecords() {
    return areRecords;
  }
    
  public Vector getExpenseRecords()
    throws com.syncbuilder.storage.DatabaseException,
           java.io.IOException
  {
    
    com.syncbuilder.storage.expense.DatabaseImpl dataimpl =
      new com.syncbuilder.storage.expense.DatabaseImpl();
    com.syncbuilder.storage.DatabaseImplFactory.registerDatabaseImpl(dataimpl);      
      
    db = new MemoryDatabase(null, "ExpenseDB", Database.OPEN_DEFAULT);
    try {
      extman = new PRCPDBExtManager();      
      Vector theRecords = new Vector();
      extman.readDatabase(istream, db);
      istream.close();
      int rec_count = db.getRecordCount();
      if(rec_count < 1) {
        areRecords = false;
        return null;
      }
      
      com.syncbuilder.storage.expense.Record record;
      for (int j = 0; j < rec_count; j++) {
        record = (com.syncbuilder.storage.expense.Record)db.getRecord(j);
        if(record.amount == null || record.amount.length() == 0) {
          continue;
        }
        theRecords.addElement(record);
      }
      
      return theRecords;
    } finally {
      try { db.close(); } catch (Throwable t) {
        System.err.println("Error closing database: "+t);
        t.printStackTrace(System.err);
      }
    }
  }
   
  // get pocketmoney transaction records
  
  public Vector getPocketmoneyTransactionRecords()
    throws com.syncbuilder.storage.DatabaseException,
           java.io.IOException
  {
    try {
      db = new MemoryDatabase(null, "PocketmoneyTransactionsDB", Database.OPEN_DEFAULT);
      extman = new PRCPDBExtManager();
      Vector theRecords = new Vector();
      extman.readDatabase(istream, db);
      istream.close();
      int rec_count = db.getRecordCount();
      if(rec_count < 1) {
        areRecords = false;
        return null;
      }
      com.syncbuilder.storage.Record record;
      com.syncbuilder.storage.pocketmoney.TransactionRecord pmoneyrec;
      for (int j = 0; j < rec_count; j++) {
        record = (com.syncbuilder.storage.Record)db.getRecord(j);
        pmoneyrec = new com.syncbuilder.storage.pocketmoney.TransactionRecord(record.pack(),
                                                                              record.getID(),
                                                                              record.getIndex(),
                                                                              record.getFlags(),
                                                                              record.getCategory());
        theRecords.addElement(pmoneyrec);
      }
      return theRecords;
    } finally {
      try { db.close(); } catch (Throwable t) {
        System.err.println("Error closing database: "+t);
        t.printStackTrace(System.err);
      }
    }
  }
         
  // get pocketmoney account records
      
  public Vector getPocketmoneyAccountRecords()
    throws com.syncbuilder.storage.DatabaseException,
           java.io.IOException
  {
    db = new MemoryDatabase(null, "PocketMoneyAccountDB", Database.OPEN_DEFAULT);
    extman = new PRCPDBExtManager();      
    Vector theRecords = new Vector();
    extman.readDatabase(istream, db);
    istream.close();
    int rec_count = db.getRecordCount();
    if(rec_count < 1) {
      areRecords = false;
      return null;
    }
      
    for (int j = 0; j < rec_count; j++) {
      com.syncbuilder.storage.Record record =
        (com.syncbuilder.storage.Record)(db.getRecord(j));
        
      // convert record to pocketmoney record
        
      byte[] thebytes = record.pack();
      com.syncbuilder.storage.pocketmoney.AccountRecord pmoneyrec = 
        new com.syncbuilder.storage.pocketmoney.AccountRecord(
          record.pack(), record.getID(), record.getIndex(), record.getFlags(),
          record.getCategory());
      theRecords.addElement(pmoneyrec);
    }
    db.close();
    return theRecords;
  }
}

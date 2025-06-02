package com.moneydance.modules.features.securityhistoryload;

import com.google.gson.Gson;
import com.google.gson.JsonParseException;
import com.google.gson.stream.JsonReader;
import com.infinitekind.moneydance.model.AccountBook;
import com.moneydance.modules.features.mrbutil.MRBDebug;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

public class NewParameters {
    private transient String fileName;
    public transient static Integer[] multipliersList = {-4, -3, -2, -1, 0, 1, 2, 3, 4};
    public transient static Integer[] decimalList = {4, 5, 6, 7, 8};
    public transient static String[] maximums = {"No Limit", "5", "6", "7", "8", "9"};
    public transient static String doNotLoad = "Do not load";
    private transient NewParameters newParams;

    enum FileType {OLD, NEW}

    ;
    private String tickerFld;
    private String priceFld;
    private String highFld;
    private String lowFld;
    private String volumeFld;
    private String dateFld;
    private int maxChar;
    private int defaultMultiplier;
    private int decimal;
    private boolean removeExch;
    private boolean includeZero;
    private boolean processCurrencies;
    private boolean ignoreCase;
    private String directoryName;
    private String lastFile;
    private int delimiter;
    private List<ExchangeLine> listExchangeLines;
    private List<String> listPrefixes;
    private transient File curFolder;
    private transient AccountBook acctBook;

    public NewParameters() {
        acctBook = Main.context.getCurrentAccountBook();
        curFolder = acctBook.getRootFolder();
        FileType result = findParameterFile();
        switch (result) {
            case NEW -> loadNewFile();
            case OLD -> loadOldFile()
                ;
        }
    }

    private FileType findParameterFile() {
        String fileName = curFolder.getAbsolutePath() + "/"+Constants.PARAMETERFILE2;
        try {
            FileInputStream curInFile = new FileInputStream(fileName);
            return FileType.NEW;
        } catch (FileNotFoundException e) {

        }
        fileName = curFolder.getAbsolutePath() + "/"+Constants.PARAMETERFILE;
        try {
            FileInputStream curInFile = new FileInputStream(fileName);
            return FileType.OLD;
        } catch (FileNotFoundException e) {

        }
            return FileType.NEW;
    }

    private void loadNewFile() {
        String fileName = curFolder.getAbsolutePath() + "/"+Constants.PARAMETERFILE2;
        boolean createNew = false;
        try {
            JsonReader reader = new JsonReader(new FileReader(fileName, StandardCharsets.UTF_8));
            Main.debugInst.debug("NewParameters", "NewParameters", MRBDebug.DETAILED, "NewParameters found "+fileName);
            newParams = new Gson().fromJson(reader, com.moneydance.modules.features.securityquoteload.NewParameters.class);
            reader.close();
        }
        catch (JsonParseException e) {
            Main.debugInst.debug("NewParameters", "NewParameters", MRBDebug.DETAILED, "Parse Exception "+e.getMessage());
            createNew = true;
        }
        catch (IOException e){
            createNew = true;
        }
        if (createNew){
            /*
             * file does not exist, initialize fields
             */
            fileName = curFolder.getAbsolutePath()+"/"+Constants.PARAMETERFILE2;
            initializeFields();
            /*
             * create the file
             */
            try {
                FileWriter writer = new FileWriter(fileName,StandardCharsets.UTF_8);
                String jsonString = new Gson().toJson(this);
                writer.write(jsonString);
                writer.close();
            } catch (IOException i) {
                i.printStackTrace();

            }
        }
    }

    private void loadOldFile() {
        String fileName = curFolder.getAbsolutePath() +"/"+Constants.PARAMETERFILE;
        try {
            FileInputStream curInFile = new FileInputStream(fileName);
            ObjectInputStream inputStream = new ObjectInputStream(curInFile);
            /*
             * file exists, copy temporary object to this object
             */
            Parameters tempParms = (Parameters) inputStream.readObject();
            this.tickerFld = tempParms.getTicker();
            this.priceFld = tempParms.getPrice();
            this.removeExch = tempParms.getExch();
            this.includeZero = tempParms.getZero();
            this.processCurrencies = tempParms.getCurrency();
            this.ignoreCase = tempParms.getCase();
            this.defaultMultiplier = tempParms.getDefaultMult();
            this.decimal = tempParms.getDecimal();
            this.highFld = tempParms.getHigh();
            this.lowFld = tempParms.getLow();
            this.volumeFld = tempParms.getVolume();
            this.dateFld = tempParms.getDate();
            this.maxChar = tempParms.getMaxChar();
            this.directoryName = tempParms.getDirectory();
            this.lastFile = tempParms.getLastFile();
            this.delimiter = tempParms.getDelimiter();
            this.listExchangeLines = tempParms.getLines();
            if (this.listExchangeLines == null)
                this.listExchangeLines = new ArrayList<ExchangeLine>();
            this.listPrefixes = tempParms.getPrefixes();
            if (this.listPrefixes == null)
                this.listPrefixes = new ArrayList<String>();
            curInFile.close();
        } catch (IOException | ClassNotFoundException ioException) {
            /*
             * file does not exist, initialize fields
             */
            initializeFields();
        }
     }
     private void initializeFields() {
         listExchangeLines = new ArrayList<ExchangeLine>();
         listPrefixes = new ArrayList<String>();
         tickerFld = "";
         priceFld = "";
         highFld = doNotLoad;
         lowFld = doNotLoad;
         volumeFld = doNotLoad;
         dateFld = "";
         maxChar = 0;
         removeExch = false;
         includeZero = false;
         processCurrencies = false;
         ignoreCase = false;
         defaultMultiplier = 4;
         decimal = 0;
         directoryName = "";
         lastFile = "";
         delimiter = 0;
     }
    public void save(){
        /*
         * create the file
         */
        fileName = curFolder.getAbsolutePath()+"/"+ Constants.PARAMETERFILE2;
        try {
            FileWriter writer2 = new FileWriter(fileName,StandardCharsets.UTF_8);
            String jsonString = new Gson().toJson(this);
            writer2.write(jsonString);
            writer2.close();
        } catch (IOException i) {
            i.printStackTrace();

        }
    }
    public List<String> getListPrefixes() {
        return listPrefixes;
    }

    public void setListPrefixes(List<String> listPrefixes) {
        this.listPrefixes = listPrefixes;
    }

    public List<ExchangeLine> getListExchangeLines() {
        return listExchangeLines;
    }

    public void setListExchangeLines(List<ExchangeLine> listExchangeLines) {
        this.listExchangeLines = listExchangeLines;
    }

    public int getDelimiter() {
        return delimiter;
    }

    public void setDelimiter(int delimiter) {
        this.delimiter = delimiter;
    }

    public String getLastFile() {
        return lastFile;
    }

    public void setLastFile(String lastFile) {
        this.lastFile = lastFile;
    }

    public String getDirectoryName() {
        return directoryName;
    }

    public void setDirectoryName(String directoryName) {
        this.directoryName = directoryName;
    }

    public boolean getIgnoreCase() {
        return ignoreCase;
    }

    public void setIgnoreCase(boolean ignoreCase) {
        this.ignoreCase = ignoreCase;
    }

    public boolean getProcessCurrencies() {
        return processCurrencies;
    }

    public void setProcessCurrencies(boolean processCurrencies) {
        this.processCurrencies = processCurrencies;
    }

    public boolean getIncludeZero() {
        return includeZero;
    }

    public void setIncludeZero(boolean includeZero) {
        this.includeZero = includeZero;
    }

    public boolean getRemoveExch() {
        return removeExch;
    }

    public void setRemoveExch(boolean removeExch) {
        this.removeExch = removeExch;
    }

    public int getDecimal() {
        return decimal;
    }

    public void setDecimal(int decimal) {
        this.decimal = decimal;
    }

    public int getDefaultMultiplier() {
        return defaultMultiplier;
    }

    public void setDefaultMultiplier(int defaultMultiplier) {
        this.defaultMultiplier = defaultMultiplier;
    }

    public int getMaxChar() {
        return maxChar;
    }

    public void setMaxChar(int maxChar) {
        this.maxChar = maxChar;
    }

    public String getDateFld() {
        return dateFld;
    }

    public void setDateFld(String dateFld) {
        this.dateFld = dateFld;
    }

    public String getVolumeFld() {
        return volumeFld;
    }

    public void setVolumeFld(String volumeFld) {
        this.volumeFld = volumeFld;
    }

    public String getLowFld() {
        return lowFld;
    }

    public void setLowFld(String lowFld) {
        this.lowFld = lowFld;
    }

    public String getHighFld() {
        return highFld;
    }

    public void setHighFld(String highFld) {
        this.highFld = highFld;
    }

    public String getPriceFld() {
        return priceFld;
    }

    public void setPriceFld(String priceFld) {
        this.priceFld = priceFld;
    }

    public String getTickerFld() {
        return tickerFld;
    }

    public void setTickerFld(String tickerFld) {
        this.tickerFld = tickerFld;
    }
    public void addExchange(String exch, int multiplier) {
        ExchangeLine objLine = new ExchangeLine(exch, multiplier);
        if (listExchangeLines == null)
            listExchangeLines = new ArrayList<ExchangeLine>();
        listExchangeLines.add(objLine);
    }
    public void addPrefix(String prefix) {
        if (listPrefixes == null)
            listPrefixes = new ArrayList<String>();
        listPrefixes.add(prefix);
    }
    public int getMultiplier(String exchange) {
        int result = defaultMultiplier;
        for (ExchangeLine line :listExchangeLines) {
            if (line.getExchange().equals(exchange)){
                result = line.getMultiplier();
                break;
            }
        }
        return multipliersList[result];
    }
    public void updateLine(String exchange, int multiplier){
        for (ExchangeLine line :listExchangeLines) {
            if (line.getExchange().equals(exchange))
                line.setMultiplier(multiplier);
        }

    }
    public void deleteExchange(String exchange){
        for (ExchangeLine line :listExchangeLines) {
            if (line.getExchange().equals(exchange)) {
                listExchangeLines.remove(line);
                break;
            }
        }

    }
    public void deletePrefix(String prefix){
        for (String prefixItem :listPrefixes) {
            if (prefixItem.equals(prefix)) {
                listPrefixes.remove(prefix);
                break;
            }
        }

    }
}

/*************************************************************************\
 * Copyright (C) 2010 The Infinite Kind, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/
package com.moneydance.modules.features.yahooqt

import com.infinitekind.moneydance.model.Account
import com.infinitekind.moneydance.model.Account.Companion.makeAccount
import com.infinitekind.moneydance.model.AccountBook.Companion.fakeAccountBook
import com.infinitekind.moneydance.model.CurrencyType
import com.infinitekind.moneydance.model.CurrencyUtil.createDefaultTable
import java.text.MessageFormat

/**
 * Base class for importing stock and currency prices. Derived classes provide specific
 * exchange rate and/or security price implementations.
 */
abstract class BaseConnection(val connectionID: String, model: StockQuotesModel, private val _capabilities: Int) {
  open val model: DownloadModel = DownloadModel(model, this)
  
  /**
   * Given a raw ticker symbol, convert it to a full symbol by adding prefix or suffix appropriate
   * for the stock exchange.
   *
   * @param parsedSymbol    The raw ticker symbol, parsed into its various parts.
   * @param exchange        The selected stock exchange to use.
   * @return The full ticker symbol appropriate for the selected stock exchange.
   */
  abstract fun getFullTickerSymbol(parsedSymbol: SymbolData, exchange: StockExchange?): String?
  
  /**
   * Given a ticker symbol, which could have an embedded currency (typically after the '-' symbol),
   * and return the currency code for the currency that should be used to interpret prices.
   * @param rawTickerSymbol The ticker symbol, potentially with an embedded currency.
   * @param exchange        The selected stock exchange to use.
   * @return the currency code from the ticker symbol, or if no embedded currency, the currency code
   * as specified by the given stock exchange.
   */
  open fun getCurrencyCodeForQuote(rawTickerSymbol: String, exchange: StockExchange?): String? {
    return null
  }
  
  
  /**
   * Retrieve the current exchange rate for the given currency and base
   * @param downloadInfo   The wrapper for the currency to be downloaded and the download results
   */
  abstract fun updateExchangeRate(downloadInfo: DownloadInfo)
  
  
  /** Update the currencies in the given list  */
  open fun updateExchangeRates(currenciesToUpdate: List<DownloadInfo>): Boolean {
    val res = model.resources
    var progressPercent = 0.0f
    val progressIncrement = if (currenciesToUpdate.isEmpty()) 1.0f else 1.0f / currenciesToUpdate.size.toFloat()
    for (downloadInfo in currenciesToUpdate) {
      System.err.println("updating currency: " + downloadInfo.security + " (" + downloadInfo.fullTickerSymbol + ")")
      updateExchangeRate(downloadInfo)
      val rate = downloadInfo.rate
      progressPercent += progressIncrement
      val message: String
      val logMessage: String
      if (rate <= 0.0) {
        message = MessageFormat.format(
          res.getString(L10NStockQuotes.ERROR_EXCHANGE_RATE_FMT),
          downloadInfo.security.idString,
          downloadInfo.relativeCurrency.idString
        )
        logMessage = MessageFormat.format(
          "Unable to get rate from {0} to {1}",
          downloadInfo.security.idString,
          downloadInfo.relativeCurrency.idString
        )
      } else {
        message = downloadInfo.buildRateDisplayText(model.quotesModel)
        logMessage = downloadInfo.buildRateLogText(model.quotesModel)
      }
      model.quotesModel.showProgress(progressPercent, message)
      QER_DLOG.log(logMessage)
      didUpdateItem(downloadInfo)
    }
    
    return true
  }
  
  open fun updateSecurities(securitiesToUpdate: List<DownloadInfo>): Boolean {
    val model = model.quotesModel ?: return false
    val res = model.resources
    var progressPercent = 0.0f
    val progressIncrement = if (securitiesToUpdate.isEmpty()) 1.0f else 1.0f / securitiesToUpdate.size.toFloat()
    for (downloadInfo in securitiesToUpdate) {
      QER_LOG.log("updating security: ${downloadInfo.security} (${downloadInfo.fullTickerSymbol}) from ${connectionID}")
      updateSecurity(downloadInfo)
      progressPercent += progressIncrement
      val message: String
      val logMessage: String
      if (!downloadInfo.wasSuccess()) {
        message = res.getString(L10NStockQuotes.ERROR_EXCHANGE_RATE_FMT)
          .replace("{0}", downloadInfo.security.idString)
          .replace("{1}", downloadInfo.relativeCurrency.idString)
        logMessage = message
      } else {
        message = downloadInfo.buildPriceDisplayText(model)
        logMessage = downloadInfo.buildPriceLogText(model)
      }
      model.showProgress(progressPercent, message)
      QER_DLOG.log(logMessage)
      
      didUpdateItem(downloadInfo)
    }
    return true
  }
  
  
  protected abstract fun updateSecurity(downloadInfo: DownloadInfo)
  
  
  /**
   * Define the default currency, which is the price currency that is to be used for the downloaded
   * quotes when the Default stock exchange is assigned to a security. The default implementation
   * specifies the U.S. Dollar as the default currency. If the default currency is not defined in
   * the current data file, the method does nothing.
   */
  open fun setDefaultCurrency() {
    val book = model.quotesModel?.book ?: return
    val currency = book.currencies.getCurrencyByIDString("USD") ?: return
    StockExchange.DEFAULT.setCurrency(currency)
  }
  
  fun canGetHistory(): Boolean {
    return ((_capabilities and HISTORY_SUPPORT) != 0)
  }
  
  fun canGetRates(): Boolean {
    return ((_capabilities and EXCHANGE_RATES_SUPPORT) != 0)
  }
  
  open val perConnectionThrottleTime: Long
    /**
     * Return the number of milliseconds by which the connection should be throttled.
     * The default is zero.
     */
    get() = 0
  
  
  /**
   * This is called after an item is updated.  If the error parameter is non-null then it
   * means there was a problem performing the update.  The default implementation checks
   * for a per-connection/item throttling time and if it is a positive number will
   * sleep/wait for the appropriate number of milliseconds.
   */
  fun didUpdateItem(downloadInfo: DownloadInfo?) {
    val delay = perConnectionThrottleTime
    if (delay > 0) {
      try {
        Thread.sleep(delay)
      } catch (e: InterruptedException) {
        System.err.println(
          "Unexpected error while sleeping throttled connection: $e"
        )
      }
    }
  }
  
  protected val timeZoneID: String
    get() =// the default time zone is EDT in the U.S.
      "America/New_York" // could possibly also use 'US/Eastern'
  
  protected val cookie: String?
    get() = null
  
  
  protected fun buildDownloadException(securityCurrency: DownloadInfo, result: Int): DownloadException {
    val resources = model.quotesModel!!.resources
    val message = when (result) {
      SnapshotImporter.ERROR_NO_INPUT_STREAM -> resources.getString(L10NStockQuotes.IMPORT_ERROR_NO_INPUT_STREAM)
      SnapshotImporter.ERROR_READ_INPUT -> resources.getString(L10NStockQuotes.IMPORT_ERROR_READ_INPUT)
      SnapshotImporter.ERROR_NO_DATA -> resources.getString(L10NStockQuotes.IMPORT_ERROR_NO_DATA)
      SnapshotImporter.ERROR_READING_DATA -> resources.getString(L10NStockQuotes.IMPORT_ERROR_READING_DATA)
      SnapshotImporter.ERROR_NO_VALID_DATA -> resources.getString(L10NStockQuotes.IMPORT_ERROR_NO_VALID_DATA)
      SnapshotImporter.ERROR_NOT_TEXT_DATA -> resources.getString(L10NStockQuotes.IMPORT_ERROR_NOT_TEXT_DATA)
      SnapshotImporter.ERROR_NO_COLUMNS -> resources.getString(L10NStockQuotes.IMPORT_ERROR_NO_COLUMNS)
      SnapshotImporter.ERROR_MALFORMED_TEXT -> resources.getString(L10NStockQuotes.IMPORT_ERROR_MALFORMED_TEXT)
      SnapshotImporter.ERROR_NO_HEADER -> resources.getString(L10NStockQuotes.IMPORT_ERROR_NO_HEADER)
      SnapshotImporter.ERROR_OTHER -> resources.getString(L10NStockQuotes.IMPORT_ERROR_OTHER)
      else -> resources.getString(L10NStockQuotes.IMPORT_ERROR_OTHER)
    }
    
    return DownloadException(securityCurrency, message)
  }
  
  
  @Throws(DownloadException::class)
  protected fun buildMessageAndThrow(securityCurrency: DownloadInfo, result: Int) {
    val exception = buildDownloadException(securityCurrency, result)
    if (exception != null) {
      throw exception
    }
  }
  
  
  companion object {
    const val HISTORY_SUPPORT: Int = 1
    const val EXCHANGE_RATES_SUPPORT: Int = 4
    const val ALL_SUPPORT: Int = HISTORY_SUPPORT or EXCHANGE_RATES_SUPPORT
    const val FOREX_HISTORY_INTERVAL: Int = 7 // snapshot minimum frequency, in days
    
    fun createEmptyTestModel(): StockQuotesModel {
      val book = fakeAccountBook()
      val model = StockQuotesModel()
      createDefaultTable(book, "USD")
      for (curr in book.currencies) {
        curr.setCurrencyType(CurrencyType.Type.CURRENCY)
        curr.setDecimalPlaces(2)
        curr.setTickerSymbol("")
      }
      book.performPostLoadVerification()
      // setup a basic account structure
      val rootAcct = book.getRootAccount()
      makeAccount(book, Account.AccountType.BANK, rootAcct).apply {
        setAccountName("Banking")
        syncItem()
      }
      makeAccount(book, Account.AccountType.INCOME, rootAcct).apply { 
        setAccountName("Misc Income")
        syncItem()
      }
      makeAccount(book, Account.AccountType.EXPENSE, rootAcct).apply {
        setAccountName("Misc Expense")
        syncItem()
      }
      model.setData(book)
      return model
    }
    
    fun runTests(currencyConnection: BaseConnection?,
                 securityConnection: BaseConnection?,
                 args: Array<String>) {
      val currencySymbols: MutableList<String> = ArrayList()
      val securitySymbols: MutableList<String> = ArrayList()
      
      var exchangeRatesMode = false
      for (arg in args) {
        if (arg == "-x") {
          exchangeRatesMode = true
        } else {
          if (exchangeRatesMode) {
            currencySymbols.add(arg)
          } else {
            securitySymbols.add(arg)
          }
        }
      }
      
      if (currencySymbols.size <= 0 && securitySymbols.size <= 0) {
        currencySymbols.addAll(
          mutableListOf(
            "ADP", "AED", "AFA", "ALL", "ANG", "AOK", "ARA", "ATS", "AUD", "AWG", "BBD", "BDT",
            "BEF", "BGL", "BHD", "BIF", "BMD", "BND", "BOB", "BRC", "BSD", "BTN", "BUK", "BWP",
            "BZD", "CAD", "CHF", "CLF", "CLP", "CNY", "COP", "CRC", "CSK", "CUP", "CVE", "CYP",
            "DDM", "DEM", "DJF", "DKK", "DOP", "DZD", "ECS", "EGP", "ESP", "ETB", "FIM", "FJD",
            "FKP", "FRF", "GBP", "GHC", "GIP", "GMD", "GNF", "GRD", "GTQ", "GWP", "GYD", "HKD",
            "HNL", "HTG", "HUF", "IDR", "IEP", "ILS", "INR", "IQD", "IRR", "ISK", "ITL", "JMD",
            "JOD", "JPY", "KES", "KHR", "KMF", "KPW", "KRW", "KWD", "KYD", "LAK", "LBP", "LKR",
            "LRD", "LSL", "LUF", "LYD", "MAD", "MGF", "MNT", "MOP", "MRO", "MTL", "MUR", "MVR",
            "MWK", "MXP", "MYR", "MZM", "NGN", "NIC", "NLG", "NOK", "NPR", "NZD", "OMR", "PAB",
            "PEI", "PGK", "PHP", "PKR", "PLZ", "PTE", "PYG", "QAR", "ROL", "RWF", "SAR", "SBD",
            "SCR", "SDP", "SEK", "SGD", "SHP", "SLL", "SOS", "SRG", "STD", "SUR", "SVC", "SYP",
            "SZL", "THB", "TND", "TOP", "TPE", "TRL", "TTD", "TWD", "TZS", "UGS", "USD", "UYP",
            "VEB", "VND", "VUV", "WST", "YDD", "YER", "YUD", "ZAR", "ZMK", "ZRZ", "ZWD"
          )
        )
        
        securitySymbols.addAll(
          mutableListOf(
            "DPL", "DTE", "DAI", "DCX", "DAN", "DHR", "DAC", "DRI", "DAR", "DVA", "DPM", "DCT",
            "DF", "DE", "DLM", "DK", "DFY", "DFG", "DFP", "DAL", "DEL", "DLX", "DNR", "DFS", "HXM",
            "DB", "DTK", "DT", "WMW", "DDR", "DVN", "DV", "DEX", "DEO", "DL", "DO", "DRH", "DSX",
            "DHX", "DKS", "DBD", "DLR", "DDS", "DIN", "DYS", "DBX", "DLB", "DTG", "DM", "D", "DCP",
            "DOM", "DPZ", "UFS", "DCI", "DRL", "DHT", "DEI", "DOV", "DDE", "DVD", "DPO", "DOW",
            "DHI", "DPS", "RDY", "DWA", "DRC", "DW", "DRQ", "DST", "DSW", "DD", "DMH", "DCO",
            "DUF", "DUK", "DRE", "DEP", "DFT", "DHG", "DRP", "DY", "DYN", "DX", "EME", "EJ", "UBC",
            "UBG", "FUD", "UBM", "USV", "UBN", "PTD", "EXP", "NGT", "EGP", "EMN", "EK", "EV",
            "ETJ", "ECL", "EIX", "EDR", "EW", "EFD", "EP", "EE", "EPB", "ELN", "ELU", "EQ", "AKO.A",
            "AKO.B", "ERJ", "EMC", "EMS", "EBS", "ESC", "EMR", "EDE", "EIG", "EOC", "EDN", "ICA",
            "ERI", "ELX", "ENB", "EEQ", "EEP", "ECA", "EAC", "ENP", "ENH", "EGN", "ENR", "EPL",
            "ETP", "ETE", "ES", "ENI", "ENS", "EC", "E", "EBF", "NPO", "ESV", "ETM", "ETR", "EHB",
            "EHA", "EHL", "EMQ", "EMO", "EPE", "EPD", "EPR", "EVC", "ENZ", "EOG", "EPC", "ENT",
            "EFX", "EQT", "ELS", "EQY", "EQR", "RET", "ESE", "ESS", "EL", "ESL", "DEG", "ETH",
            "EVR", "RE", "EBI", "EEE", "XCO", "EXM", "EXC", "XJT", "EXH", "EXR", "XOM", "FMC",
            "FNB", "FPL", "HCE", "FDS", "FIC", "FA", "FCS", "FFH", "FRP", "FDO", "FNM", "FFG",
            "AGM.A", "AGM", "FNA", "FRT", "FSS", "FII", "FDX", "FCH", "FMX", "FGP", "FOE", "FNF",
            "FSC", "FIF", "FSF", "FSE", "FAC", "FAF", "FBP", "FCF", "FHN", "FR", "FMD", "FMR",
            "FPO", "FEO", "FE", "FED", "FBC", "FSR", "FLE", "FTK", "FLO", "FLS", "FLR", "FTI",
            "FL", "F", "FCJ", "FCZ", "FCE.B", "FCE.A", "FCY", "FRX", "FST", "FOR", "FIG", "FO",
            "FCL", "FGC", "FTE", "BEN", "FC", "FT", "FRE", "FCX", "FMS", "FDP", "FBR", "FTR",
            "FTO", "FRO", "FCN", "FUL", "FRM", "FBN", "GMT", "GFA", "AJG", "GBL", "GME", "GRS",
            "GCI", "GPS", "GDI", "IT", "GET", "GEP", "BGC", "GD", "GE", "GIS", "GOM", "GNK", "GY",
            "DNA", "GEC", "GEJ", "GGP", "GMR", "XGM", "RGM", "HGM", "GMS", "GRM", "GXM", "GBM",
            "GPM", "GMA", "GSI", "GCO", "GWR", "GLS", "GED", "GEA", "GKM", "BGM", "G", "GPC", "GNW",
            "GEO", "GGC", "GAR", "GAT", "GPW", "GPU", "GAH", "GPD", "GPJ", "GRB", "GGB", "GNA",
            "GTY", "GA", "GIL", "GLG", "GLT", "GSK", "GLG.U", "GLG.UN", "GRT", "GCA", "GLP", "GPN",
            "GEG", "GSL.UN", "GSL.U", "GSL", "GM", "GMW", "GJM", "GFI", "GG", "GOL", "GR", "GDP",
            "GT", "IRE", "GPX", "GGG", "GTI", "GKK", "GVA", "GPK", "GTN.A", "GTN", "GAJ", "GAP",
            "GNI", "GXP", "GB", "GBX", "GHL", "GEF.B", "GEF", "GFF", "GPI", "GBE", "GMK", "ASR",
            "SAB", "CEL", "RC", "TMM", "GS", "GSC", "GNV", "GSH", "GFG", "GES", "GUQ", "GUL", "GUI",
            "GLF", "GU"
          )
        )
      }
      
      val currencies: MutableList<DownloadInfo> = ArrayList()
      val securities: MutableList<DownloadInfo> = ArrayList()
      
      if (securityConnection != null) {
        val ctable = securityConnection.model.book!!.currencies
        for (symbol in securitySymbols) {
          var security = ctable.getCurrencyByTickerSymbol(symbol)
          if (security == null) {
            security = CurrencyType(ctable).also { security ->
              security.setCurrencyType(CurrencyType.Type.SECURITY)
              security.setTickerSymbol(symbol)
              security.setName(symbol)
              security.setIDString("^$symbol")
              security.setDecimalPlaces(4)
              ctable.addCurrencyType(security)
            }
          }
          securities.add(DownloadInfo(security, securityConnection.model))
        }
      }
      
      if (currencyConnection != null) {
        val ctable = currencyConnection.model.book!!.currencies
        for (symbol in currencySymbols) {
          val currency = ctable.getCurrencyByIDString(symbol) ?: CurrencyType(ctable).also { newCurr ->
            newCurr.setCurrencyType(CurrencyType.Type.CURRENCY)
            newCurr.setName(symbol)
            newCurr.idString = symbol
            newCurr.setDecimalPlaces(2)
            ctable.addCurrencyType(newCurr)
          }
          currencies.add(DownloadInfo(currency, currencyConnection.model))
        }
      }
      
      currencyConnection?.updateExchangeRates(currencies)
      securityConnection?.updateSecurities(securities)
    }
  }
}

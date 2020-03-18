package com.moneydance.modules.features.yahooqt;

import com.infinitekind.util.StringUtils;

public abstract class APIKeyConnection extends BaseConnection
{
	public APIKeyConnection(String connectionID, StockQuotesModel model, int capabilities)
	{
		super(connectionID, model, capabilities);
	}
	
	public abstract String getAPIKey(final StockQuotesModel model, final boolean evenIfAlreadySet);
	
	@Override
	public String getFullTickerSymbol(SymbolData parsedSymbol, StockExchange exchange)
	{
		if ((parsedSymbol == null) || SQUtil.isBlank(parsedSymbol.symbol)) return null;
		// check if the exchange was already added on, which will override the selected exchange
		if (!SQUtil.isBlank(parsedSymbol.suffix))
		{
			return parsedSymbol.symbol + parsedSymbol.suffix;
		}
		// Check if the selected exchange has a Yahoo suffix or not. If it does, add it.
		String suffix = exchange.getSymbolYahoo();
		if (SQUtil.isBlank(suffix)) return parsedSymbol.symbol;
		return parsedSymbol.symbol + suffix;
	}
	
	@Override
	public String getCurrencyCodeForQuote(String rawTickerSymbol, StockExchange exchange)
	{
		if (SQUtil.isBlank(rawTickerSymbol)) return null;
		// check if this symbol overrides the exchange and the currency code
		int periodIdx = rawTickerSymbol.lastIndexOf('.');
		if (periodIdx > 0)
		{
			String marketID = rawTickerSymbol.substring(periodIdx + 1);
			if (marketID.contains("-"))
			{
				// the currency ID was encoded along with the market ID
				return StringUtils.fieldIndex(marketID, '-', 1);
			}
		}
		return exchange.getCurrencyCode();
	}
}

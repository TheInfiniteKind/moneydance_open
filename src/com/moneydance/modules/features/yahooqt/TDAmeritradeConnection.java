package com.moneydance.modules.features.yahooqt;

import com.google.gson.Gson;
import com.infinitekind.moneydance.model.Account;
import com.infinitekind.moneydance.model.AccountBook;
import com.infinitekind.util.StringUtils;
import com.moneydance.awt.GridC;
import com.moneydance.awt.JLinkLabel;
import com.moneydance.awt.JTextPanel;
import com.moneydance.modules.features.yahooqt.tdameritrade.History;
import static java.lang.Thread.sleep;

import javax.swing.AbstractAction;
import javax.swing.Action;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.SwingUtilities;
import java.awt.GridBagLayout;
import java.awt.event.ActionEvent;
import java.net.URI;
import java.net.URISyntaxException;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.text.MessageFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutionException;
import java.util.stream.Collectors;

/**
 * Download quotes and exchange rates from tdameritrade.com
 * This requires an API key which customers can register for at runtime and enter in the
 * prompt shown by this connection.
 * <p>
 * Note: connections are throttled to avoid TDAmeritrade's low threshold for
 * rejecting frequent connections.
 */
public class TDAmeritradeConnection extends APIKeyConnection
{
	private static final SimpleDateFormat SNAPSHOT_DATE_FORMAT = new SimpleDateFormat("yyyy-MM-dd");
	
	public static final String PREFS_KEY = "tdameritrade";
	private SimpleDateFormat refreshDateFmt;
	
	//TDAmeritrade limits all non-order related requests to 120 per minute.
	private int BURST_RATE_PER_MINUTE = 120;
	
	private static String apiKey = "";
	private static String HISTORY_URL = "https://api.tdameritrade.com/v1/marketdata/%s/pricehistory?apikey=%s&periodType=month&period=1&frequencyType=daily";
	
	public TDAmeritradeConnection(StockQuotesModel model)
	{
		super(PREFS_KEY, model, BaseConnection.HISTORY_SUPPORT);
		refreshDateFmt = new SimpleDateFormat("yyyy-MM-dd hh:mm:ss"); // 2017-11-07 11:46:52
		refreshDateFmt.setLenient(true);
	}
	
	private static String cachedAPIKey = null;
	private static long suppressAPIKeyRequestUntilTime = 0;
	
	private List<DownloadInfo> remainingToUpdate;
	
	public String getAPIKey(final StockQuotesModel model, final boolean evenIfAlreadySet)
	{
		if (!evenIfAlreadySet && cachedAPIKey != null) return cachedAPIKey;
		
		if (model == null) return null;
		
		AccountBook book = model.getBook();
		if (book == null) return null;
		
		final Account root = book.getRootAccount();
		String apiKey = root.getParameter("tdameritrade.apikey",
										  model.getPreferences().getSetting("tdameritrade_apikey", null));
		if (!evenIfAlreadySet && !StringUtils.isBlank(apiKey))
		{
			return apiKey;
		}
		
		if (!evenIfAlreadySet && suppressAPIKeyRequestUntilTime > System.currentTimeMillis())
		{ // further requests for the key have been suppressed
			return null;
		}
		
		final String existingAPIKey = apiKey;
		Runnable uiActions = new Runnable()
		{
			@Override
			public void run()
			{
				JPanel p = new JPanel(new GridBagLayout());
				AbstractAction signupAction = new AbstractAction()
				{
					@Override
					public void actionPerformed(ActionEvent e)
					{
						model.showURL("https://developer.tdameritrade.com/content/getting-started");
					}
				};
				String defaultAPIKey = existingAPIKey != null ? existingAPIKey : "";
				signupAction.putValue(Action.NAME, model.getResources().getString("tdameritrade.apikey_action"));
				JLinkLabel linkButton = new JLinkLabel(signupAction);
				p.add(new JTextPanel(model.getResources().getString("tdameritrade.apikey_msg")),
					  GridC.getc(0, 0).wxy(1, 1));
				p.add(linkButton,
					  GridC.getc(0, 1).center().insets(12, 16, 0, 16));
				while (true)
				{
					String inputString = JOptionPane.showInputDialog(null, p, defaultAPIKey);
					if (inputString == null)
					{ // the user canceled the prompt, so let's not ask again for 5 minutes unless this prompt was forced
						if (!evenIfAlreadySet)
						{
							suppressAPIKeyRequestUntilTime = System.currentTimeMillis() + 1000 * 60 * 5;
						}
						return;
					}
					
					if (!SQUtil.isEmpty(inputString) && !inputString.equals(JOptionPane.UNINITIALIZED_VALUE))
					{
						root.setParameter("tdameritrade.apikey", inputString);
						model.getPreferences().setSetting("tdameritrade_apikey", inputString);
						root.syncItem();
						cachedAPIKey = inputString;
						return;
					}
					else
					{
						// the user left the field blank or entered an invalid key
						model.getGUI().beep();
					}
				}
			}
		};
		
		if (SwingUtilities.isEventDispatchThread())
		{
			uiActions.run();
		}
		else
		{
			try
			{
				SwingUtilities.invokeAndWait(uiActions);
			}
			catch (Exception e)
			{
				e.printStackTrace();
			}
		}
		return cachedAPIKey;
	}
	
	
	public String toString()
	{
		StockQuotesModel model = getModel();
		return model == null ? "" : model.getResources().getString("tdameritrade");
	}
	
	/**
	 * Retrieve the current exchange rate for the given currency relative to the base
	 *
	 * @param downloadInfo The wrapper for the currency to be downloaded and the download results
	 */
	@Override
	public void updateExchangeRate(DownloadInfo downloadInfo)
	{
	}
	
	private URI getHistoryURI(String fullTickerSymbol) throws URISyntaxException
	{
		String apiKey = getAPIKey(getModel(), false);
		String uriStr = String.format(HISTORY_URL, SQUtil.urlEncode(fullTickerSymbol), SQUtil.urlEncode(apiKey));

		System.out.println(uriStr);
		return new URI(uriStr);
	}
	
//	int processors = Runtime.getRuntime().availableProcessors();
//	ExecutorService executorService = Executors.newFixedThreadPool(processors);
	
	HttpClient client = HttpClient.newBuilder()
//			.executor(executorService)
			.version(HttpClient.Version.HTTP_2)
			.build();
	
	@Override
	public boolean updateSecurities(List<DownloadInfo> securitiesToUpdate)
	{
		ResourceProvider res = model.getResources();
		float progressPercent = 0.0f;
		final float progressIncrement = securitiesToUpdate.isEmpty() ? 1.0f :
				100.0f / (float)securitiesToUpdate.size();
		boolean success = true;
		
		this.remainingToUpdate = new ArrayList<>(securitiesToUpdate);
		List<DownloadInfo> retry = new ArrayList<>();
		int remaining;
		int completedCount = 0;
		do
		{
			List<DownloadInfo> completed = updateSecurities();
			int requests = completed.size();
			int original = securitiesToUpdate.size();
			for (DownloadInfo downloadInfo: completed)
			{
				if (downloadInfo.getHistoryCount() == 0)
				{
					retry.add(downloadInfo);
				}
				else
				{
					progressPercent += progressIncrement;
					final String message, logMessage;
					if (!downloadInfo.wasSuccess())
					{
						message = MessageFormat.format(res.getString(L10NStockQuotes.ERROR_EXCHANGE_RATE_FMT),
													   downloadInfo.security.getIDString(),
													   downloadInfo.relativeCurrency.getIDString());
						logMessage = MessageFormat.format("Unable to get rate from {0} to {1}",
														  downloadInfo.security.getIDString(),
														  downloadInfo.relativeCurrency.getIDString());
					}
					else
					{
						message = downloadInfo.buildPriceDisplayText(model);
						logMessage = downloadInfo.buildPriceLogText(model);
					}
					model.showProgress(progressPercent, message);
					didUpdateItem(downloadInfo);
				}
			}
			this.remainingToUpdate.removeAll(completed);

			remaining = this.remainingToUpdate.size();
			completedCount = original - remaining;
			System.out.println(String.format("Updated %d quotes out of %d", completedCount, original));
			
			if (remaining > 0 && requests > 119)
			{
				try
				{
					System.out.println("WAIT: 1 minute");
					sleep(60000);
				}
				catch (InterruptedException e)
				{
					e.printStackTrace();
				}
			}
		}
		while (remaining > 0 && completedCount > 0);
		return true;
	}
	
	private List<DownloadInfo> updateSecurities()
	{
		int count = Math.min(BURST_RATE_PER_MINUTE, remainingToUpdate.size());
		System.out.println(String.format("Updates %d quotes out of %d", count, remainingToUpdate.size()));
		
		return this.remainingToUpdate.stream()
										.map(this::updateOneSecurity)
										.limit(BURST_RATE_PER_MINUTE)
										.collect(Collectors.toList());
	}
	
	@Override
	protected void updateSecurity(DownloadInfo downloadInfo)
	{
		//don't use this one
	}
	
	protected DownloadInfo updateOneSecurity(DownloadInfo stock)
	{
		if (stock.getHistoryCount() > 0)
			return stock;
		
		CompletableFuture<DownloadInfo> di = null;
		try
		{
			URI uri = getHistoryURI(stock.fullTickerSymbol);

			 di = client.sendAsync(HttpRequest.newBuilder(uri).GET().build(),
								   HttpResponse.BodyHandlers.ofString())
					.thenApply(response -> {
						System.out.println(stock.fullTickerSymbol + ":\n" + response.body());
						Gson gson = new Gson();
						
						// 1. JSON file to Java object
						History history = gson.fromJson(response.body(), History.class);
						stock.addHistory(history);
						return stock;
					});
		}
		catch (URISyntaxException uri)
		{
			uri.printStackTrace();
		}
		
		DownloadInfo stockReturn = null;
		try
		{
			stockReturn = di.get();
		}
		catch (InterruptedException e)
		{
			e.printStackTrace();
		}
		catch (ExecutionException e)
		{
			e.printStackTrace();
		}
		
		return stockReturn;
	}
	
	public static void main(String[] args)
	{
		if (args.length < 1)
		{
			System.err.println("usage: <thiscommand> <tdameritrade-apikey> <symbols>...");
			System.err.println(
					" -x: parameters after -x in the parameter list are symbols are three digit currency codes instead of security/ticker symbols");
			System.exit(-1);
		}
		
		cachedAPIKey = args[0].trim();
		
		TDAmeritradeConnection conn = new TDAmeritradeConnection(createEmptyTestModel());
		runTests(null, conn, Arrays.copyOfRange(args, 1, args.length));
	}
}
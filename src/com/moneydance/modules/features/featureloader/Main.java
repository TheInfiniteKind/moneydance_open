/**
 * Main.java
 * Copyright 2010, Sven Zethelius
 * 
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
 */
package com.moneydance.modules.features.featureloader;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.lang.reflect.Field;
import java.net.URL;
import java.net.URLClassLoader;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Arrays;
import java.util.Collection;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Properties;
import java.util.ResourceBundle;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.ScheduledThreadPoolExecutor;
import java.util.concurrent.TimeUnit;

import com.moneydance.apps.md.controller.FeatureModule;
import com.moneydance.apps.md.controller.FeatureModuleContext;

/**
 * FeatureLoader acts as a proxy to one or more FeatureModule dynamically. This
 * allow the delegated FeatureModule to be reloaded without stopping the
 * MoneyDance instance.
 * 
 * Note one sideeffect of the featureloader is that if the featuremodule is
 * uninstalled, the features it is adding won't be removed until the application
 * is restarted.
 * 
 * @author Sven Zethelius
 * 
 */
public class Main extends FeatureModule
{
	private static final String INVOKE = "reload-featureloader";

	private DateFormat DATE_FORMAT = new SimpleDateFormat("yyyy-MM-dd hh:mm:ss");

	private final ResourceBundle m_resources;

	private final List<Loader> m_loaders = new CopyOnWriteArrayList<Loader>();
	private final ScheduledThreadPoolExecutor m_executor = new ScheduledThreadPoolExecutor(1);
	private final PropertiesRefreshRunnable m_propertiesRunnable;

	public Main() throws FileNotFoundException
	{
		m_resources = ResourceBundle.getBundle("com.moneydance.modules.features.featureloader.Resources", Locale
				.getDefault());

		m_executor.setExecuteExistingDelayedTasksAfterShutdownPolicy(false);
		m_executor.setContinueExistingPeriodicTasksAfterShutdownPolicy(false);

		URL urlProperties = this.getClass().getClassLoader().getResource("FeatureLoader.properties");

		m_propertiesRunnable = new PropertiesRefreshRunnable(urlProperties, 1000);
	}

	@Override
	public void cleanup()
	{
		for (Loader loader : m_loaders)
		{
			loader.getModule().cleanup();
		}
	}

	@Override
	public String getName()
	{
		return m_resources.getString("Name");
	}

	@Override
	public void handleEvent(String appEvent)
	{
		for (Loader loader : m_loaders)
		{
			loader.getModule().handleEvent(appEvent);
		}
	}

	@Override
	public void init()
	{
		m_propertiesRunnable.start();
	}

	@Override
	public void invoke(String paramString)
	{
		if (paramString.startsWith(INVOKE))
		{
			for (Loader loader : m_loaders)
			{
				if (Integer.parseInt(paramString.split(":")[1]) == loader.hashCode())
				{
					loader.stop();
					loader.start();
				}
			}
		}
		else
		{
			for (Loader loader : m_loaders)
			{
				loader.getModule().invoke(paramString);
			}
		}
	}

	@Override
	public void unload()
	{
		m_propertiesRunnable.stop();
	}

	private Properties readProperties(URL url) throws FileNotFoundException, IOException
	{
		InputStream is = null;
		try
		{
			Properties props = new Properties();
			is = url.openStream();
			props.load(is);
			is.close();
			is = null;
			return props;
		}
		finally
		{
			if (is != null)
			{
				try
				{
					is.close();
				}
				catch (IOException e)
				{
					e.printStackTrace();
				}
			}
		}
	}

	/**
	 * Since the FeatureModule has a final setup method, need to copy necessary
	 * properties from the featureloader.Main into the created FeatureModule
	 * before it can be used, using reflection to copy the private members.
	 * 
	 * @param fm
	 * @return the updated FeatureModule
	 */
	private FeatureModule setup(FeatureModule fm)
	{
		Field[] fields = FeatureModule.class.getDeclaredFields();
		try
		{
			for (Field field : fields)
			{
				field.setAccessible(true);
				Object o = field.get(this);
				field.set(fm, o);
			}
		}
		catch (Exception e)
		{
			e.printStackTrace();
		}
		return fm;
	}

	/**
	 * Container to manage individual FeatureModules
	 * 
	 * @author Sven Zethelius
	 * 
	 */
	private class Loader extends ScheduledRefreshRunnable
	{
		private final String m_name;
		private final String m_clazzName;

		private FeatureModule m_module;

		public Loader(String name, URL[] urls, String clazzName, long interval)
		{
			super(urls, interval);
			m_name = name;
			m_clazzName = clazzName;
		}

		public FeatureModule getModule()
		{
			return m_module;
		}

		public boolean matches(URL[] urls)
		{
			return Arrays.deepEquals(m_urls, urls);
		}

		@SuppressWarnings("unchecked")
		@Override
		public synchronized void run()
		{
			try
			{
				ClassLoader cl = new URLClassLoader(m_urls, getClass().getClassLoader());
				Class<? extends FeatureModule> clazz = (Class<? extends FeatureModule>) Class.forName(m_clazzName,
						true, cl);

				if (getModule() != null)
				{
					System.out.println(DATE_FORMAT.format(new Date()) + " - Refreshing " + m_module.getName());
					getModule().cleanup();
					getModule().unload();
				}
				m_module = setup(clazz.newInstance());
				getModule().init();
			}
			catch (Exception e)
			{
				e.printStackTrace();
			}
		}

		@Override
		public synchronized void stop()
		{
			super.stop();

			if (getModule() != null)
			{
				getModule().cleanup();
				getModule().unload();
			}
		}
	}

	/**
	 * Listen for reloads of the property file.
	 * 
	 * @author Sven Zethelius
	 * 
	 */
	private class PropertiesRefreshRunnable extends ScheduledRefreshRunnable
	{
		public PropertiesRefreshRunnable(URL url, long interval)
		{
			super(url != null ? new URL[] { url } : new URL[0], interval);
		}

		@Override
		public synchronized void run()
		{
			Map<String, Loader> loaders = new HashMap<String, Loader>(m_loaders.size());
			for (Loader loader : m_loaders)
			{
				loaders.put(loader.m_name, loader);
			}

			try
			{
				if (m_urls.length == 0)
				{
					System.err.println("FeatureLoader.properties not found.  Not features to load.");
					return;
				}

				Properties props = readProperties(m_urls[0]);
				String[] features = props.getProperty("features", "").split(",");

				if (features.length == 0)
				{
					System.err.println("FeatureLoader found no features to load");
				}

				FeatureModuleContext context = getContext();
				String reloadFormat = m_resources.getString("Reload");

				for (String feature : features)
				{
					feature = feature.trim();
					Loader loader = loaders.remove(feature);

					String[] paths = props.getProperty(feature + "/path", "").split(";");
					String clazzName = "com.moneydance.modules.features." + feature.toLowerCase() + ".Main";
					long reloadInterval = Long.parseLong(props.getProperty(feature + "/reloadMS", "0").trim());

					URL[] urls = new URL[paths.length];
					for (int i = 0; i < paths.length; i++)
					{
						urls[i] = new URL(paths[i].trim());
						if (!new File(urls[i].getFile()).exists())
							throw new FileNotFoundException("File not found: " + paths[i]);
					}

					if (loader == null)
					{ // we don't have this one loaded already / initial load
						loader = new Loader(feature, urls, clazzName, reloadInterval);
						loader.start();
						m_loaders.add(loader);

						FeatureModule fm = loader.getModule();
						context.registerFeature(Main.this, INVOKE + ":" + loader.hashCode(), null, String.format(
								reloadFormat, fm.getName()));
					}
					else if (!loader.matches(urls))
					{ // we need to load a new classloader
						loader.stop();
						m_loaders.remove(loader);
						loader = new Loader(feature, urls, clazzName, reloadInterval);
						m_loaders.add(loader);
					}
					else
					{
						loader.setInterval(reloadInterval);
					}
				}
				Collection<Loader> toDelete = loaders.values();
				m_loaders.removeAll(toDelete);
				for (Loader loader : toDelete)
				{
					loader.stop();
				}
			}
			catch (Exception e)
			{
				e.printStackTrace();
			}
		}

		@Override
		public synchronized void stop()
		{
			super.stop();
			for (Loader loader : m_loaders)
			{
				loader.stop();
			}
		}

	}

	/**
	 * Base class for the refreshable files listeners. Keeps track of the files
	 * being listened to, and manages adding and removing it from the executor.
	 * 
	 * @author Sven Zethelius
	 * 
	 */
	private abstract class ScheduledRefreshRunnable implements Runnable
	{
		protected final URL[] m_urls;
		private long m_interval;
		private Runnable m_scheduled;

		public ScheduledRefreshRunnable(URL[] urls, long interval)
		{
			m_urls = urls;
			m_interval = interval;
		}

		public synchronized void setInterval(long interval)
		{
			if (m_interval == interval)
				return;

			m_interval = interval;
			if (m_scheduled != null)
			{
				m_executor.remove(m_scheduled);
			}
			if (m_interval > 0)
			{
				schedule();
			}
		}

		public synchronized void start()
		{
			run();
			schedule();
		}

		public synchronized void stop()
		{
			if (m_scheduled != null)
			{
				m_executor.remove(m_scheduled);
			}
		}

		private void schedule()
		{
			if (m_interval <= 0)
				return;

			File[] files = new File[m_urls.length];
			for (int i = 0; i < m_urls.length; i++)
			{
				files[i] = new File(m_urls[i].getFile());
			}
			FileWatchRunnable fwr = new FileWatchRunnable(files, this);
			m_scheduled = (Runnable) m_executor.scheduleWithFixedDelay(fwr, m_interval, m_interval,
					TimeUnit.MILLISECONDS);
		}
	}

}

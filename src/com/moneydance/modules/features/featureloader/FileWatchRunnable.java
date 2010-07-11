/**
 * FileWatchRunnable.java
 * Copyright (C) 2010, Sven Zethelius
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
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Allows a custom runnable to be invoked if files have changed since the last
 * time this instance was run.
 * 
 * @author Sven Zethelius
 * 
 */
public class FileWatchRunnable implements Runnable
{
	private final File[] m_files;
	private Map<File, Long> m_lastUpdated = new HashMap<File, Long>();
	private final Runnable m_runnable;

	public FileWatchRunnable(File[] files, Runnable runnable)
	{
		m_files = files;
		m_runnable = runnable;
		update();
	}

	@Override
	public void run()
	{
		try
		{
			if (update())
			{
				m_runnable.run();
			}
		}
		catch (Exception e)
		{
			e.printStackTrace();
		}
	}

	/**
	 * Recurse the list of directories, looking for any files that have updated.
	 * 
	 * @return true if any file updated
	 */
	boolean update()
	{
		Map<File, Long> lastUpdated = new HashMap<File, Long>((int) (m_lastUpdated.size() * 1.5));
		List<File> toVisit = new ArrayList<File>(m_lastUpdated.size());
		toVisit.addAll(Arrays.asList(m_files));

		boolean updated = false;
		while (!toVisit.isEmpty())
		{
			File file = toVisit.remove(toVisit.size() - 1);
			if (file.isDirectory())
			{
				toVisit.addAll(Arrays.asList(file.listFiles()));
			}
			else if (file.isFile())
			{
				long lastModified = file.lastModified();
				Long oldLastModified = m_lastUpdated.get(file);
				if (oldLastModified == null || lastModified > oldLastModified)
				{
					updated = true;
				}
				lastUpdated.put(file, lastModified);
			}
		}
		if (!lastUpdated.keySet().equals(m_lastUpdated.keySet()))
		{ // files have been deleted
			updated = true;
		}
		m_lastUpdated = lastUpdated;
		return updated;
	}
}
